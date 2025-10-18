import json
from unittest.mock import Mock, patch
from app.models import db, Pokemon


def test_fetch_pokemon_route_success(app, client):
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
            response = client.post('/pokemon/fetch/pikachu')
            
            assert response.status_code == 201
            data = json.loads(response.data)
            assert 'message' in data
            assert data['data']['name'] == 'pikachu'
            
            pokemon = Pokemon.query.filter_by(name='pikachu').first()
            assert pokemon is not None
            assert pokemon.pokedex_id == 25


def test_fetch_pokemon_route_not_found(app, client):
    with app.app_context():
        with patch('app.services.pokeapi_client.PokeAPIClient.get_pokemon', side_effect=ValueError('Pokemon not found')):
            response = client.post('/pokemon/fetch/missingno')
            
            assert response.status_code == 404
            data = json.loads(response.data)
            assert 'error' in data


def test_fetch_pokemon_route_api_error(app, client):
    with app.app_context():
        with patch('app.services.pokeapi_client.PokeAPIClient.get_pokemon', side_effect=Exception('API Error')):
            response = client.post('/pokemon/fetch/pikachu')
            
            assert response.status_code == 500
            data = json.loads(response.data)
            assert 'error' in data


def test_fetch_multiple_pokemon_success(app, client):
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
            response = client.post('/pokemon/fetch-multiple',
                                    data=json.dumps({'names': ['bulbasaur', 'charmander']}),
                                    content_type='application/json')
            
            assert response.status_code == 201
            data = json.loads(response.data)
            assert 'success_count' in data


def test_fetch_multiple_pokemon_missing_names(app, client):
    response = client.post('/pokemon/fetch-multiple',
                            data=json.dumps({}),
                            content_type='application/json')
    
    assert response.status_code == 400
    data = json.loads(response.data)
    assert 'error' in data


def test_fetch_multiple_pokemon_invalid_names(app, client):
    response = client.post('/pokemon/fetch-multiple',
                            data=json.dumps({'names': 'not-a-list'}),
                            content_type='application/json')
    
    assert response.status_code == 400
    data = json.loads(response.data)
    assert 'error' in data


def test_export_pokemon_not_found(client):
    response = client.get('/pokemon/nonexistent/export')
    assert response.status_code == 404

