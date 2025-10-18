import json
from unittest.mock import Mock, patch
from click.testing import CliRunner
from app.models import db, Pokemon, PokemonType, PokemonAbility


def test_fetch_pokemon_cli_success(app, runner):
    with app.app_context():
        mock_response = {
            'id': 25,
            'name': 'pikachu',
            'height': 4,
            'weight': 60,
            'base_experience': 112,
            'types': [{'type': {'name': 'electric'}, 'slot': 1}],
            'abilities': [{'ability': {'name': 'static'}, 'is_hidden': False, 'slot': 1}],
            'stats': [{'stat': {'name': 'hp'}, 'base_stat': 35, 'effort': 0}],
            'moves': []
        }
        
        with patch('app.services.pokeapi_client.PokeAPIClient.get_pokemon', return_value=mock_response):
            result = runner.invoke(args=['main', 'fetch-pokemon', 'pikachu'])
            
            assert result.exit_code == 0
            assert '[OK]' in result.output
            assert 'pikachu' in result.output


def test_fetch_pokemon_cli_error(app, runner):
    with app.app_context():
        with patch('app.services.pokeapi_client.PokeAPIClient.get_pokemon', side_effect=ValueError('Not found')):
            result = runner.invoke(args=['main', 'fetch-pokemon', 'missingno'])
            
            assert result.exit_code == 0
            assert '[ERROR]' in result.output


def test_fetch_pokemon_cli_multiple(app, runner):
    with app.app_context():
        mock_response = {
            'id': 25,
            'name': 'pikachu',
            'height': 4,
            'weight': 60,
            'base_experience': 112,
            'types': [{'type': {'name': 'electric'}, 'slot': 1}],
            'abilities': [{'ability': {'name': 'static'}, 'is_hidden': False, 'slot': 1}],
            'stats': [{'stat': {'name': 'hp'}, 'base_stat': 35, 'effort': 0}],
            'moves': []
        }
        
        with patch('app.services.pokeapi_client.PokeAPIClient.get_pokemon', return_value=mock_response):
            result = runner.invoke(args=['main', 'fetch-pokemon', 'pikachu', 'charizard'])
            
            assert result.exit_code == 0


def test_fetch_default_cli(app, runner):
    with app.app_context():
        mock_response = {
            'id': 25,
            'name': 'pikachu',
            'height': 4,
            'weight': 60,
            'base_experience': 112,
            'types': [{'type': {'name': 'electric'}, 'slot': 1}],
            'abilities': [{'ability': {'name': 'static'}, 'is_hidden': False, 'slot': 1}],
            'stats': [{'stat': {'name': 'hp'}, 'base_stat': 35, 'effort': 0}],
            'moves': []
        }
        
        with patch('app.services.pokeapi_client.PokeAPIClient.get_pokemon', return_value=mock_response):
            result = runner.invoke(args=['main', 'fetch-default'])
            
            assert result.exit_code == 0
            assert '[OK]' in result.output


def test_fetch_default_cli_with_errors(app, runner):
    with app.app_context():
        def mock_get_pokemon(name):
            if name == 'dhelmise':
                raise ValueError('Not found')
            return {
                'id': 25,
                'name': name,
                'height': 4,
                'weight': 60,
                'base_experience': 112,
                'types': [{'type': {'name': 'electric'}, 'slot': 1}],
                'abilities': [{'ability': {'name': 'static'}, 'is_hidden': False, 'slot': 1}],
                'stats': [{'stat': {'name': 'hp'}, 'base_stat': 35, 'effort': 0}],
                'moves': []
            }
        
        with patch('app.services.pokeapi_client.PokeAPIClient.get_pokemon', side_effect=mock_get_pokemon):
            result = runner.invoke(args=['main', 'fetch-default'])
            
            assert result.exit_code == 0
            assert '[ERROR]' in result.output


def test_list_pokemon_cli_empty(app, runner):
    with app.app_context():
        result = runner.invoke(args=['main', 'list-pokemon'])
        
        assert result.exit_code == 0
        assert 'No pokemon found' in result.output


def test_list_pokemon_cli_with_data(app, runner):
    with app.app_context():
        pokemon = Pokemon(name='pikachu', pokedex_id=25, height=4, weight=60)
        ptype = PokemonType(type_name='electric', slot=1)
        ability = PokemonAbility(ability_name='static', is_hidden=False, slot=1)
        pokemon.types.append(ptype)
        pokemon.abilities.append(ability)
        db.session.add(pokemon)
        db.session.commit()
        
        result = runner.invoke(args=['main', 'list-pokemon'])
        
        assert result.exit_code == 0
        assert 'pikachu' in result.output.lower()
        assert '25' in result.output


def test_export_json_cli_empty(app, runner, tmp_path):
    with app.app_context():
        output_file = tmp_path / "test.json"
        result = runner.invoke(args=['main', 'export-json', str(output_file)])
        
        assert result.exit_code == 0
        assert 'No pokemon found' in result.output


def test_export_json_cli_with_data(app, runner, tmp_path):
    with app.app_context():
        pokemon = Pokemon(name='pikachu', pokedex_id=25, height=4, weight=60)
        db.session.add(pokemon)
        db.session.commit()
        
        output_file = tmp_path / "test.json"
        result = runner.invoke(args=['main', 'export-json', str(output_file)])
        
        assert result.exit_code == 0
        assert '[OK]' in result.output
        assert output_file.exists()


def test_export_csv_cli_empty(app, runner, tmp_path):
    with app.app_context():
        output_file = tmp_path / "test.csv"
        result = runner.invoke(args=['main', 'export-csv', str(output_file)])
        
        assert result.exit_code == 0
        assert 'No pokemon found' in result.output


def test_export_csv_cli_with_data(app, runner, tmp_path):
    with app.app_context():
        pokemon = Pokemon(name='pikachu', pokedex_id=25, height=4, weight=60)
        db.session.add(pokemon)
        db.session.commit()
        
        output_file = tmp_path / "test.csv"
        result = runner.invoke(args=['main', 'export-csv', str(output_file)])
        
        assert result.exit_code == 0
        assert '[OK]' in result.output
        assert output_file.exists()

