import pytest
from unittest.mock import Mock, patch
from app.services.pokeapi_client import PokeAPIClient
from app.services.data_processor import DataProcessor
from app.services.exporter import DataExporter
from app.models import db, Pokemon, PokemonType


def test_pokeapi_client_initialization(app):
    with app.app_context():
        client = PokeAPIClient()
        assert client.base_url == 'https://pokeapi.co/api/v2'


def test_data_processor_sanitize_types(app):
    with app.app_context():
        processor = DataProcessor()
        
        types_data = [
            {'type': {'name': 'electric'}, 'slot': 1}
        ]
        
        result = processor._extract_types(types_data)
        
        assert len(result) == 1
        assert result[0]['name'] == 'electric'
        assert result[0]['slot'] == 1


def test_data_processor_sanitize_abilities(app):
    with app.app_context():
        processor = DataProcessor()
        
        abilities_data = [
            {'ability': {'name': 'static'}, 'is_hidden': False, 'slot': 1},
            {'ability': {'name': 'lightning-rod'}, 'is_hidden': True, 'slot': 3}
        ]
        
        result = processor._extract_abilities(abilities_data)
        
        assert len(result) == 2
        assert result[0]['name'] == 'static'
        assert result[0]['is_hidden'] is False
        assert result[1]['is_hidden'] is True


def test_data_processor_sanitize_stats(app):
    with app.app_context():
        processor = DataProcessor()
        
        stats_data = [
            {'stat': {'name': 'hp'}, 'base_stat': 35, 'effort': 0}
        ]
        
        result = processor._extract_stats(stats_data)
        
        assert len(result) == 1
        assert result[0]['name'] == 'hp'
        assert result[0]['base_stat'] == 35


def test_exporter_json(app):
    with app.app_context():
        pokemon = Pokemon(name='pikachu', pokedex_id=25, height=4, weight=60)
        db.session.add(pokemon)
        db.session.commit()
        
        exporter = DataExporter()
        json_str = exporter.export_to_json(pokemon)
        
        assert 'pikachu' in json_str
        assert '25' in json_str

