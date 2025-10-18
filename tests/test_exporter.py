import json
import os
from pathlib import Path
from app.models import db, Pokemon, PokemonType, PokemonStat
from app.services.exporter import DataExporter


def test_export_to_json_with_file(app, tmp_path):
    with app.app_context():
        pokemon = Pokemon(name='pikachu', pokedex_id=25, height=4, weight=60)
        db.session.add(pokemon)
        db.session.commit()
        
        output_file = tmp_path / "test_export.json"
        exporter = DataExporter()
        exporter.export_to_json(pokemon, str(output_file))
        
        assert output_file.exists()
        
        with open(output_file, 'r') as f:
            data = json.load(f)
            assert data['name'] == 'pikachu'


def test_export_to_json_without_file(app):
    with app.app_context():
        pokemon = Pokemon(name='charizard', pokedex_id=6, height=17, weight=905)
        db.session.add(pokemon)
        db.session.commit()
        
        exporter = DataExporter()
        json_str = exporter.export_to_json(pokemon)
        
        data = json.loads(json_str)
        assert data['name'] == 'charizard'
        assert data['pokedex_id'] == 6


def test_export_multiple_to_json_with_file(app, tmp_path):
    with app.app_context():
        pokemon1 = Pokemon(name='pikachu', pokedex_id=25, height=4, weight=60)
        pokemon2 = Pokemon(name='charizard', pokedex_id=6, height=17, weight=905)
        db.session.add_all([pokemon1, pokemon2])
        db.session.commit()
        
        output_file = tmp_path / "test_multiple.json"
        exporter = DataExporter()
        exporter.export_multiple_to_json([pokemon1, pokemon2], str(output_file))
        
        assert output_file.exists()
        
        with open(output_file, 'r') as f:
            data = json.load(f)
            assert data['count'] == 2
            assert len(data['pokemon']) == 2


def test_export_multiple_to_json_without_file(app):
    with app.app_context():
        pokemon1 = Pokemon(name='pikachu', pokedex_id=25, height=4, weight=60)
        pokemon2 = Pokemon(name='charizard', pokedex_id=6, height=17, weight=905)
        db.session.add_all([pokemon1, pokemon2])
        db.session.commit()
        
        exporter = DataExporter()
        json_str = exporter.export_multiple_to_json([pokemon1, pokemon2])
        
        data = json.loads(json_str)
        assert data['count'] == 2
        assert len(data['pokemon']) == 2


def test_export_to_csv(app, tmp_path):
    with app.app_context():
        pokemon = Pokemon(name='pikachu', pokedex_id=25, height=4, weight=60, base_experience=112)
        ptype = PokemonType(type_name='electric', slot=1)
        pokemon.types.append(ptype)
        
        stat_hp = PokemonStat(stat_name='hp', base_stat=35, effort=0)
        stat_attack = PokemonStat(stat_name='attack', base_stat=55, effort=0)
        pokemon.stats.extend([stat_hp, stat_attack])
        
        db.session.add(pokemon)
        db.session.commit()
        
        output_file = tmp_path / "test_export.csv"
        exporter = DataExporter()
        exporter.export_to_csv([pokemon], str(output_file))
        
        assert output_file.exists()
        
        content = output_file.read_text()
        assert 'pikachu' in content
        assert '25' in content
        assert 'electric' in content


def test_export_to_csv_empty_list(app, tmp_path):
    with app.app_context():
        output_file = tmp_path / "empty_export.csv"
        exporter = DataExporter()
        exporter.export_to_csv([], str(output_file))
        
        assert output_file.exists()


def test_export_to_csv_multiple_pokemon(app, tmp_path):
    with app.app_context():
        pokemon1 = Pokemon(name='pikachu', pokedex_id=25, height=4, weight=60)
        pokemon2 = Pokemon(name='charizard', pokedex_id=6, height=17, weight=905)
        
        stat1 = PokemonStat(stat_name='hp', base_stat=35, effort=0)
        stat2 = PokemonStat(stat_name='hp', base_stat=78, effort=0)
        pokemon1.stats.append(stat1)
        pokemon2.stats.append(stat2)
        
        db.session.add_all([pokemon1, pokemon2])
        db.session.commit()
        
        output_file = tmp_path / "multiple.csv"
        exporter = DataExporter()
        exporter.export_to_csv([pokemon1, pokemon2], str(output_file))
        
        content = output_file.read_text()
        assert 'pikachu' in content
        assert 'charizard' in content

