from flask import Blueprint, jsonify, request, current_app, Response, stream_with_context
from app.models import db, Pokemon
from app.services.data_processor import DataProcessor
from app.services.exporter import DataExporter
from app import limiter, cache
import click
import re
import json

bp = Blueprint('main', __name__)


def validate_pokemon_name(name: str) -> bool:
    if not name or not isinstance(name, str):
        return False
    if len(name) > 50:
        return False
    if not re.match(r'^[a-z0-9\-]+$', name.lower()):
        return False
    return True


@bp.route('/')
def index():
    return jsonify({
        'message': 'Pokemon Scouting API',
        'endpoints': {
            '/health': 'GET - Health check endpoint',
            '/pokemon': 'GET - List all pokemon (supports ?include_deleted=true)',
            '/pokemon/<name>': 'GET - Get specific pokemon / DELETE - Soft delete pokemon',
            '/pokemon/<name>/restore': 'POST - Restore soft-deleted pokemon',
            '/pokemon/fetch/<name>': 'POST - Fetch and store pokemon from API',
            '/pokemon/fetch-multiple': 'POST - Fetch multiple pokemon (JSON body with "names" array)',
            '/pokemon/<name>/export': 'GET - Export pokemon data as JSON',
            '/pokemon/export/stream/json': 'GET - Stream export all pokemon as JSON',
            '/pokemon/export/stream/csv': 'GET - Stream export all pokemon as CSV'
        }
    })


@bp.route('/health')
def health_check():
    try:
        pokemon_count = Pokemon.query.count()
        return jsonify({
            'status': 'healthy',
            'database': 'connected',
            'pokemon_count': pokemon_count
        }), 200
    except Exception as e:
        return jsonify({
            'status': 'unhealthy',
            'database': 'disconnected',
            'error': str(e)
        }), 503


@bp.route('/pokemon', methods=['GET'])
@cache.cached(timeout=300, query_string=True)
def list_pokemon():
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 20, type=int)
    include_deleted = request.args.get('include_deleted', 'false').lower() == 'true'
    per_page = min(per_page, 100)
    
    query = Pokemon.query
    if not include_deleted:
        query = query.filter_by(deleted_at=None)
    
    pagination = query.paginate(
        page=page, per_page=per_page, error_out=False
    )
    
    return jsonify({
        'count': pagination.total,
        'page': page,
        'per_page': per_page,
        'total_pages': pagination.pages,
        'pokemon': [{'id': p.id, 'name': p.name, 'pokedex_id': p.pokedex_id} for p in pagination.items]
    })


@bp.route('/pokemon/<string:name>', methods=['GET'])
@cache.cached(timeout=300, query_string=True)
def get_pokemon(name):
    if not validate_pokemon_name(name):
        return jsonify({'error': 'Invalid pokemon name format'}), 400
    
    pokemon = Pokemon.query.options(
        db.joinedload(Pokemon.types),
        db.joinedload(Pokemon.abilities),
        db.joinedload(Pokemon.stats),
        db.joinedload(Pokemon.moves)
    ).filter_by(name=name.lower(), deleted_at=None).first()
    
    if not pokemon:
        return jsonify({'error': f'Pokemon {name} not found in database'}), 404
    
    return jsonify(pokemon.to_dict())


@bp.route('/pokemon/fetch/<string:name>', methods=['POST'])
@limiter.limit("10 per minute")
def fetch_pokemon(name):
    if not validate_pokemon_name(name):
        return jsonify({'error': 'Invalid pokemon name format'}), 400
    
    try:
        processor = DataProcessor()
        pokemon = processor.fetch_and_store_pokemon(name.lower())
        
        return jsonify({
            'message': f'Successfully fetched and stored {pokemon.name}',
            'data': pokemon.to_dict()
        }), 201
    except ValueError as e:
        return jsonify({'error': str(e)}), 404
    except Exception as e:
        return jsonify({'error': f'Failed to fetch pokemon: {str(e)}'}), 500


@bp.route('/pokemon/fetch-multiple', methods=['POST'])
@limiter.limit("5 per minute")
def fetch_multiple_pokemon():
    data = request.get_json()
    
    if not data or 'names' not in data:
        return jsonify({'error': 'Request body must contain "names" array'}), 400
    
    names = data['names']
    
    if not isinstance(names, list):
        return jsonify({'error': '"names" must be an array'}), 400
    
    if len(names) > 100:
        return jsonify({'error': 'Maximum 100 pokemon per request'}), 400
    
    invalid_names = [name for name in names if not validate_pokemon_name(name)]
    if invalid_names:
        return jsonify({
            'error': 'Invalid pokemon name format',
            'invalid_names': invalid_names
        }), 400
    
    processor = DataProcessor()
    results, errors = processor.fetch_multiple_pokemon(names)
    
    return jsonify({
        'message': f'Processed {len(results)} pokemon',
        'success_count': len(results),
        'error_count': len(errors),
        'results': [p.to_dict() for p in results],
        'errors': errors
    }), 201 if results else 500


@bp.route('/pokemon/<string:name>/export', methods=['GET'])
def export_pokemon(name):
    if not validate_pokemon_name(name):
        return jsonify({'error': 'Invalid pokemon name format'}), 400
    
    pokemon = Pokemon.query.options(
        db.joinedload(Pokemon.types),
        db.joinedload(Pokemon.abilities),
        db.joinedload(Pokemon.stats),
        db.joinedload(Pokemon.moves)
    ).filter_by(name=name.lower()).first()
    
    if not pokemon:
        return jsonify({'error': f'Pokemon {name} not found in database'}), 404
    
    return jsonify(pokemon.to_dict())


@bp.route('/pokemon/<string:name>', methods=['DELETE'])
def soft_delete_pokemon(name):
    if not validate_pokemon_name(name):
        return jsonify({'error': 'Invalid pokemon name format'}), 400
    
    pokemon = Pokemon.query.filter_by(name=name.lower(), deleted_at=None).first()
    
    if not pokemon:
        return jsonify({'error': f'Pokemon {name} not found in database'}), 404
    
    pokemon.soft_delete()
    cache.clear()
    
    return jsonify({
        'message': f'Successfully soft deleted {pokemon.name}',
        'deleted_at': pokemon.deleted_at.isoformat()
    }), 200


@bp.route('/pokemon/<string:name>/restore', methods=['POST'])
def restore_pokemon(name):
    if not validate_pokemon_name(name):
        return jsonify({'error': 'Invalid pokemon name format'}), 400
    
    pokemon = Pokemon.query.filter_by(name=name.lower()).filter(Pokemon.deleted_at.isnot(None)).first()
    
    if not pokemon:
        return jsonify({'error': f'Deleted pokemon {name} not found in database'}), 404
    
    pokemon.restore()
    cache.clear()
    
    return jsonify({
        'message': f'Successfully restored {pokemon.name}'
    }), 200


@bp.route('/pokemon/export/stream/json', methods=['GET'])
def stream_export_json():
    def generate():
        yield '{"count": '
        
        count = Pokemon.query.filter_by(deleted_at=None).count()
        yield str(count)
        yield ', "pokemon": ['
        
        first = True
        for pokemon in Pokemon.query.options(
            db.joinedload(Pokemon.types),
            db.joinedload(Pokemon.abilities),
            db.joinedload(Pokemon.stats),
            db.joinedload(Pokemon.moves)
        ).filter_by(deleted_at=None).yield_per(50):
            if not first:
                yield ', '
            first = False
            yield json.dumps(pokemon.to_dict())
        
        yield ']}'
    
    return Response(
        stream_with_context(generate()),
        mimetype='application/json',
        headers={'Content-Disposition': 'attachment; filename=pokemon_export.json'}
    )


@bp.route('/pokemon/export/stream/csv', methods=['GET'])
def stream_export_csv():
    def generate():
        yield 'name,pokedex_id,height,weight,base_experience,generation,is_legendary,is_mythical,types,abilities,hp,attack,defense,special_attack,special_defense,speed\n'
        
        for pokemon in Pokemon.query.options(
            db.joinedload(Pokemon.types),
            db.joinedload(Pokemon.abilities),
            db.joinedload(Pokemon.stats)
        ).filter_by(deleted_at=None).yield_per(50):
            stats_dict = {stat.stat_name: stat.base_stat for stat in pokemon.stats}
            
            row = [
                pokemon.name,
                str(pokemon.pokedex_id),
                str(pokemon.height or ''),
                str(pokemon.weight or ''),
                str(pokemon.base_experience or ''),
                str(pokemon.generation or ''),
                str(pokemon.is_legendary),
                str(pokemon.is_mythical),
                '; '.join([t.type_name for t in pokemon.types]),
                '; '.join([a.ability_name for a in pokemon.abilities]),
                str(stats_dict.get('hp', 0)),
                str(stats_dict.get('attack', 0)),
                str(stats_dict.get('defense', 0)),
                str(stats_dict.get('special-attack', 0)),
                str(stats_dict.get('special-defense', 0)),
                str(stats_dict.get('speed', 0))
            ]
            
            yield ','.join(row) + '\n'
    
    return Response(
        stream_with_context(generate()),
        mimetype='text/csv',
        headers={'Content-Disposition': 'attachment; filename=pokemon_export.csv'}
    )


@bp.cli.command('fetch-pokemon')
@click.argument('names', nargs=-1, required=True)
def fetch_pokemon_cli(names):
    processor = DataProcessor()
    
    with current_app.app_context():
        for name in names:
            try:
                pokemon = processor.fetch_and_store_pokemon(name.lower())
                click.echo(f'[OK] Successfully fetched and stored: {pokemon.name}')
            except ValueError as e:
                click.echo(f'[ERROR] Error fetching {name}: {str(e)}', err=True)
            except Exception as e:
                click.echo(f'[ERROR] Unexpected error fetching {name}: {str(e)}', err=True)


@bp.cli.command('fetch-default')
def fetch_default_pokemon():
    processor = DataProcessor()
    pokemon_names = current_app.config['DEFAULT_POKEMON']
    
    click.echo(f'Fetching {len(pokemon_names)} default pokemon...')
    
    with current_app.app_context():
        results, errors = processor.fetch_multiple_pokemon(pokemon_names)
        
        click.echo(f'\n[OK] Successfully fetched: {len(results)} pokemon')
        for pokemon in results:
            click.echo(f'  - {pokemon.name} (#{pokemon.pokedex_id})')
        
        if errors:
            click.echo(f'\n[ERROR] Errors: {len(errors)}')
            for error in errors:
                click.echo(f'  - {error["pokemon"]}: {error["error"]}')


@bp.cli.command('list-pokemon')
def list_pokemon_cli():
    pokemon_list = Pokemon.query.options(
        db.joinedload(Pokemon.types),
        db.joinedload(Pokemon.abilities)
    ).all()
    
    if not pokemon_list:
        click.echo('No pokemon found in database')
        return
    
    click.echo(f'Found {len(pokemon_list)} pokemon in database:\n')
    for p in pokemon_list:
        click.echo(f'#{p.pokedex_id:03d} - {p.name.capitalize()}')
        click.echo(f'  Types: {", ".join([t.type_name for t in p.types])}')
        click.echo(f'  Abilities: {", ".join([a.ability_name for a in p.abilities])}')
        click.echo()


@bp.cli.command('export-json')
@click.argument('output_file')
def export_json_cli(output_file):
    pokemon_list = Pokemon.query.options(
        db.joinedload(Pokemon.types),
        db.joinedload(Pokemon.abilities),
        db.joinedload(Pokemon.stats),
        db.joinedload(Pokemon.moves)
    ).all()
    
    if not pokemon_list:
        click.echo('No pokemon found in database')
        return
    
    exporter = DataExporter()
    exporter.export_multiple_to_json(pokemon_list, output_file)
    
    click.echo(f'[OK] Exported {len(pokemon_list)} pokemon to {output_file}')


@bp.cli.command('export-csv')
@click.argument('output_file')
def export_csv_cli(output_file):
    pokemon_list = Pokemon.query.options(
        db.joinedload(Pokemon.types),
        db.joinedload(Pokemon.abilities),
        db.joinedload(Pokemon.stats)
    ).all()
    
    if not pokemon_list:
        click.echo('No pokemon found in database')
        return
    
    exporter = DataExporter()
    exporter.export_to_csv(pokemon_list, output_file)
    
    click.echo(f'[OK] Exported {len(pokemon_list)} pokemon to {output_file}')

