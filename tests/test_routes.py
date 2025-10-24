import json
from app.models import db, Pokemon, PokemonType


def test_index_route(client):
    response = client.get('/')
    assert response.status_code == 200
    data = json.loads(response.data)
    assert 'message' in data
    assert 'endpoints' in data


def test_list_pokemon_empty(client):
    response = client.get('/pokemon')
    assert response.status_code == 200
    data = json.loads(response.data)
    assert data['count'] == 0
    assert data['page'] == 1
    assert data['per_page'] == 20
    assert data['total_pages'] == 0
    assert data['pokemon'] == []


def test_list_pokemon_with_data(app, client):
    with app.app_context():
        pokemon = Pokemon(name='pikachu', pokedex_id=25, height=4, weight=60)
        db.session.add(pokemon)
        db.session.commit()
    
    response = client.get('/pokemon')
    assert response.status_code == 200
    data = json.loads(response.data)
    assert data['count'] == 1
    assert data['page'] == 1
    assert data['total_pages'] == 1
    assert len(data['pokemon']) == 1


def test_get_pokemon_found(app, client):
    with app.app_context():
        pokemon = Pokemon(name='pikachu', pokedex_id=25, height=4, weight=60)
        ptype = PokemonType(type_name='electric', slot=1)
        pokemon.types.append(ptype)
        db.session.add(pokemon)
        db.session.commit()
    
    response = client.get('/pokemon/pikachu')
    assert response.status_code == 200
    data = json.loads(response.data)
    assert data['name'] == 'pikachu'
    assert data['pokedex_id'] == 25


def test_get_pokemon_not_found(client):
    response = client.get('/pokemon/missingno')
    assert response.status_code == 404
    data = json.loads(response.data)
    assert 'error' in data


def test_export_pokemon(app, client):
    with app.app_context():
        pokemon = Pokemon(name='charizard', pokedex_id=6, height=17, weight=905)
        db.session.add(pokemon)
        db.session.commit()
    
    response = client.get('/pokemon/charizard/export')
    assert response.status_code == 200
    data = json.loads(response.data)
    assert data['name'] == 'charizard'

