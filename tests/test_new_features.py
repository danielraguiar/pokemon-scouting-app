import json
from app.models import db, Pokemon, PokemonType, PokemonStat
from datetime import datetime, UTC


def test_health_check_endpoint(client):
    response = client.get('/health')
    assert response.status_code == 200
    data = json.loads(response.data)
    assert data['status'] == 'healthy'
    assert data['database'] == 'connected'
    assert 'pokemon_count' in data


def test_pagination_with_defaults(app, client):
    with app.app_context():
        for i in range(25):
            pokemon = Pokemon(name=f'pokemon_{i}', pokedex_id=i)
            db.session.add(pokemon)
        db.session.commit()
    
    response = client.get('/pokemon')
    assert response.status_code == 200
    data = json.loads(response.data)
    assert data['page'] == 1
    assert data['per_page'] == 20
    assert len(data['pokemon']) == 20
    assert data['total_pages'] == 2


def test_pagination_custom_per_page(app, client):
    with app.app_context():
        for i in range(15):
            pokemon = Pokemon(name=f'pokemon_{i}', pokedex_id=i)
            db.session.add(pokemon)
        db.session.commit()
    
    response = client.get('/pokemon?per_page=5&page=2')
    assert response.status_code == 200
    data = json.loads(response.data)
    assert data['page'] == 2
    assert data['per_page'] == 5
    assert len(data['pokemon']) == 5


def test_soft_delete_pokemon(app, client):
    with app.app_context():
        pokemon = Pokemon(name='pikachu', pokedex_id=25, height=4, weight=60)
        db.session.add(pokemon)
        db.session.commit()
    
    response = client.delete('/pokemon/pikachu')
    assert response.status_code == 200
    data = json.loads(response.data)
    assert 'deleted_at' in data
    
    response = client.get('/pokemon/pikachu')
    assert response.status_code == 404


def test_soft_delete_nonexistent_pokemon(client):
    response = client.delete('/pokemon/nonexistent')
    assert response.status_code == 404


def test_restore_pokemon(app, client):
    with app.app_context():
        pokemon = Pokemon(name='charizard', pokedex_id=6, height=17, weight=905)
        pokemon.deleted_at = datetime.now(UTC)
        db.session.add(pokemon)
        db.session.commit()
    
    response = client.post('/pokemon/charizard/restore')
    assert response.status_code == 200
    data = json.loads(response.data)
    assert 'restored' in data['message'].lower()
    
    response = client.get('/pokemon/charizard')
    assert response.status_code == 200


def test_restore_nondeleted_pokemon(app, client):
    with app.app_context():
        pokemon = Pokemon(name='bulbasaur', pokedex_id=1, height=7, weight=69)
        db.session.add(pokemon)
        db.session.commit()
    
    response = client.post('/pokemon/bulbasaur/restore')
    assert response.status_code == 404


def test_list_pokemon_exclude_deleted_by_default(app, client):
    with app.app_context():
        pokemon1 = Pokemon(name='pikachu', pokedex_id=25, height=4, weight=60)
        pokemon2 = Pokemon(name='charizard', pokedex_id=6, height=17, weight=905)
        pokemon2.deleted_at = datetime.now(UTC)
        db.session.add(pokemon1)
        db.session.add(pokemon2)
        db.session.commit()
    
    response = client.get('/pokemon')
    assert response.status_code == 200
    data = json.loads(response.data)
    assert data['count'] == 1
    assert len(data['pokemon']) == 1
    assert data['pokemon'][0]['name'] == 'pikachu'


def test_list_pokemon_include_deleted(app, client):
    with app.app_context():
        pokemon1 = Pokemon(name='pikachu', pokedex_id=25, height=4, weight=60)
        pokemon2 = Pokemon(name='charizard', pokedex_id=6, height=17, weight=905)
        pokemon2.deleted_at = datetime.now(UTC)
        db.session.add(pokemon1)
        db.session.add(pokemon2)
        db.session.commit()
    
    response = client.get('/pokemon?include_deleted=true')
    assert response.status_code == 200
    data = json.loads(response.data)
    assert data['count'] == 2
    assert len(data['pokemon']) == 2


def test_pokemon_model_new_fields(app):
    with app.app_context():
        pokemon = Pokemon(
            name='mewtwo',
            pokedex_id=150,
            height=20,
            weight=1220,
            generation=1,
            sprite_url='https://example.com/mewtwo.png',
            is_legendary=True,
            is_mythical=False
        )
        db.session.add(pokemon)
        db.session.commit()
        
        retrieved = Pokemon.query.filter_by(name='mewtwo').first()
        assert retrieved.generation == 1
        assert retrieved.sprite_url == 'https://example.com/mewtwo.png'
        assert retrieved.is_legendary is True
        assert retrieved.is_mythical is False


def test_pokemon_soft_delete_methods(app):
    with app.app_context():
        pokemon = Pokemon(name='squirtle', pokedex_id=7, height=5, weight=90)
        db.session.add(pokemon)
        db.session.commit()
        
        assert not pokemon.is_deleted
        
        pokemon.soft_delete()
        assert pokemon.is_deleted
        assert pokemon.deleted_at is not None
        
        pokemon.restore()
        assert not pokemon.is_deleted
        assert pokemon.deleted_at is None


def test_stream_export_json(app, client):
    with app.app_context():
        pokemon = Pokemon(name='pikachu', pokedex_id=25, height=4, weight=60)
        ptype = PokemonType(type_name='electric', slot=1)
        pokemon.types.append(ptype)
        db.session.add(pokemon)
        db.session.commit()
    
    response = client.get('/pokemon/export/stream/json')
    assert response.status_code == 200
    assert response.content_type == 'application/json'
    assert b'pikachu' in response.data


def test_stream_export_csv(app, client):
    with app.app_context():
        pokemon = Pokemon(name='charizard', pokedex_id=6, height=17, weight=905)
        stat = PokemonStat(stat_name='hp', base_stat=78, effort=0)
        pokemon.stats.append(stat)
        db.session.add(pokemon)
        db.session.commit()
    
    response = client.get('/pokemon/export/stream/csv')
    assert response.status_code == 200
    assert 'text/csv' in response.content_type
    assert b'charizard' in response.data
    assert b'name,pokedex_id' in response.data


def test_input_validation_invalid_name(client):
    response = client.get('/pokemon/invalid$name!')
    assert response.status_code == 400
    data = json.loads(response.data)
    assert 'Invalid pokemon name format' in data['error']


def test_input_validation_too_long_name(client):
    long_name = 'a' * 51
    response = client.get(f'/pokemon/{long_name}')
    assert response.status_code == 400


def test_caching_works(app, client):
    with app.app_context():
        pokemon = Pokemon(name='pikachu', pokedex_id=25, height=4, weight=60)
        db.session.add(pokemon)
        db.session.commit()
    
    response1 = client.get('/pokemon/pikachu')
    assert response1.status_code == 200
    
    response2 = client.get('/pokemon/pikachu')
    assert response2.status_code == 200
    assert response1.data == response2.data

