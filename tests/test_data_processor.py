import pytest
from unittest.mock import Mock, patch
from app.models import db, Pokemon
from app.services.data_processor import DataProcessor


def test_fetch_and_store_pokemon(app):
    with app.app_context():
        mock_response = {
            'id': 25,
            'name': 'pikachu',
            'height': 4,
            'weight': 60,
            'base_experience': 112,
            'types': [{'type': {'name': 'electric'}, 'slot': 1}],
            'abilities': [
                {'ability': {'name': 'static'}, 'is_hidden': False, 'slot': 1},
                {'ability': {'name': 'lightning-rod'}, 'is_hidden': True, 'slot': 3}
            ],
            'stats': [
                {'stat': {'name': 'hp'}, 'base_stat': 35, 'effort': 0},
                {'stat': {'name': 'attack'}, 'base_stat': 55, 'effort': 0}
            ],
            'moves': [
                {
                    'move': {'name': 'thunder-shock'},
                    'version_group_details': [
                        {
                            'move_learn_method': {'name': 'level-up'},
                            'level_learned_at': 1
                        }
                    ]
                }
            ]
        }
        
        with patch('app.services.pokeapi_client.PokeAPIClient.get_pokemon', return_value=mock_response):
            processor = DataProcessor()
            pokemon = processor.fetch_and_store_pokemon('pikachu')
            
            assert pokemon.name == 'pikachu'
            assert pokemon.pokedex_id == 25
            assert pokemon.height == 4
            assert pokemon.weight == 60
            assert len(pokemon.types) == 1
            assert len(pokemon.abilities) == 2
            assert len(pokemon.stats) == 2
            assert len(pokemon.moves) == 1


def test_fetch_and_store_pokemon_update_existing(app):
    with app.app_context():
        existing = Pokemon(name='pikachu', pokedex_id=25, height=4, weight=60)
        db.session.add(existing)
        db.session.commit()
        
        mock_response = {
            'id': 25,
            'name': 'pikachu',
            'height': 5,
            'weight': 70,
            'base_experience': 120,
            'types': [{'type': {'name': 'electric'}, 'slot': 1}],
            'abilities': [{'ability': {'name': 'static'}, 'is_hidden': False, 'slot': 1}],
            'stats': [{'stat': {'name': 'hp'}, 'base_stat': 35, 'effort': 0}],
            'moves': []
        }
        
        with patch('app.services.pokeapi_client.PokeAPIClient.get_pokemon', return_value=mock_response):
            processor = DataProcessor()
            pokemon = processor.fetch_and_store_pokemon('pikachu')
            
            assert pokemon.height == 5
            assert pokemon.weight == 70


def test_fetch_multiple_pokemon(app):
    with app.app_context():
        mock_response = {
            'id': 1,
            'name': 'bulbasaur',
            'height': 7,
            'weight': 69,
            'base_experience': 64,
            'types': [{'type': {'name': 'grass'}, 'slot': 1}],
            'abilities': [{'ability': {'name': 'overgrow'}, 'is_hidden': False, 'slot': 1}],
            'stats': [{'stat': {'name': 'hp'}, 'base_stat': 45, 'effort': 0}],
            'moves': []
        }
        
        with patch('app.services.pokeapi_client.PokeAPIClient.get_pokemon', return_value=mock_response):
            processor = DataProcessor()
            results, errors = processor.fetch_multiple_pokemon(['bulbasaur', 'charmander'])
            
            assert len(results) == 2
            assert len(errors) == 0


def test_fetch_multiple_pokemon_with_errors(app):
    with app.app_context():
        def mock_get_pokemon(name):
            if name == 'invalid':
                raise ValueError('Pokemon not found')
            return {
                'id': 1,
                'name': name,
                'height': 7,
                'weight': 69,
                'base_experience': 64,
                'types': [{'type': {'name': 'grass'}, 'slot': 1}],
                'abilities': [{'ability': {'name': 'overgrow'}, 'is_hidden': False, 'slot': 1}],
                'stats': [{'stat': {'name': 'hp'}, 'base_stat': 45, 'effort': 0}],
                'moves': []
            }
        
        with patch('app.services.pokeapi_client.PokeAPIClient.get_pokemon', side_effect=mock_get_pokemon):
            processor = DataProcessor()
            results, errors = processor.fetch_multiple_pokemon(['bulbasaur', 'invalid'])
            
            assert len(results) == 1
            assert len(errors) == 1
            assert errors[0]['pokemon'] == 'invalid'


def test_extract_moves_no_version_details(app):
    with app.app_context():
        processor = DataProcessor()
        
        moves_data = [
            {'move': {'name': 'tackle'}, 'version_group_details': []}
        ]
        
        result = processor._extract_moves(moves_data)
        assert len(result) == 0


def test_sanitize_pokemon_data_minimal(app):
    with app.app_context():
        processor = DataProcessor()
        
        raw_data = {
            'name': 'test',
            'id': 1,
            'types': [],
            'abilities': [],
            'stats': [],
            'moves': []
        }
        
        result = processor._sanitize_pokemon_data(raw_data)
        
        assert result['name'] == 'test'
        assert result['pokedex_id'] == 1
        assert result['height'] == 0
        assert result['weight'] == 0
        assert result['base_experience'] == 0

