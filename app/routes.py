from flask import Blueprint, jsonify, request, current_app
from app.models import db, Pokemon
from app.services.data_processor import DataProcessor
from app.services.exporter import DataExporter
import click
import re

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
            '/pokemon': 'GET - List all pokemon',
            '/pokemon/<name>': 'GET - Get specific pokemon',
            '/pokemon/fetch/<name>': 'POST - Fetch and store pokemon from API',
            '/pokemon/fetch-multiple': 'POST - Fetch multiple pokemon (JSON body with "names" array)',
            '/pokemon/<name>/export': 'GET - Export pokemon data as JSON'
        }
    })


@bp.route('/pokemon', methods=['GET'])
def list_pokemon():
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 20, type=int)
    per_page = min(per_page, 100)
    
    pagination = Pokemon.query.paginate(
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
def get_pokemon(name):
    if not validate_pokemon_name(name):
        return jsonify({'error': 'Invalid pokemon name format'}), 400
    
    pokemon = Pokemon.query.filter_by(name=name.lower()).first()
    
    if not pokemon:
        return jsonify({'error': f'Pokemon {name} not found in database'}), 404
    
    return jsonify(pokemon.to_dict())


@bp.route('/pokemon/fetch/<string:name>', methods=['POST'])
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
    
    pokemon = Pokemon.query.filter_by(name=name.lower()).first()
    
    if not pokemon:
        return jsonify({'error': f'Pokemon {name} not found in database'}), 404
    
    return jsonify(pokemon.to_dict())


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
    pokemon_list = Pokemon.query.all()
    
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
    pokemon_list = Pokemon.query.all()
    
    if not pokemon_list:
        click.echo('No pokemon found in database')
        return
    
    exporter = DataExporter()
    exporter.export_multiple_to_json(pokemon_list, output_file)
    
    click.echo(f'[OK] Exported {len(pokemon_list)} pokemon to {output_file}')


@bp.cli.command('export-csv')
@click.argument('output_file')
def export_csv_cli(output_file):
    pokemon_list = Pokemon.query.all()
    
    if not pokemon_list:
        click.echo('No pokemon found in database')
        return
    
    exporter = DataExporter()
    exporter.export_to_csv(pokemon_list, output_file)
    
    click.echo(f'[OK] Exported {len(pokemon_list)} pokemon to {output_file}')

