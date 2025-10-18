from app.models import db, Pokemon, PokemonType, PokemonAbility, PokemonStat


def test_pokemon_creation(app):
    with app.app_context():
        pokemon = Pokemon(
            name='pikachu',
            pokedex_id=25,
            height=4,
            weight=60,
            base_experience=112
        )
        db.session.add(pokemon)
        db.session.commit()
        
        assert pokemon.id is not None
        assert pokemon.name == 'pikachu'
        assert pokemon.pokedex_id == 25


def test_pokemon_relationships(app):
    with app.app_context():
        pokemon = Pokemon(name='charizard', pokedex_id=6, height=17, weight=905)
        db.session.add(pokemon)
        
        ptype = PokemonType(type_name='fire', slot=1)
        pokemon.types.append(ptype)
        
        ability = PokemonAbility(ability_name='blaze', is_hidden=False, slot=1)
        pokemon.abilities.append(ability)
        
        stat = PokemonStat(stat_name='hp', base_stat=78, effort=0)
        pokemon.stats.append(stat)
        
        db.session.commit()
        
        assert len(pokemon.types) == 1
        assert len(pokemon.abilities) == 1
        assert len(pokemon.stats) == 1
        assert pokemon.types[0].type_name == 'fire'


def test_pokemon_to_dict(app):
    with app.app_context():
        pokemon = Pokemon(name='pikachu', pokedex_id=25, height=4, weight=60)
        db.session.add(pokemon)
        db.session.commit()
        
        data = pokemon.to_dict()
        
        assert data['name'] == 'pikachu'
        assert data['pokedex_id'] == 25
        assert 'types' in data
        assert 'abilities' in data
        assert 'stats' in data

