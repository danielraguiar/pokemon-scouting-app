import pytest
import requests
from unittest.mock import Mock, patch
from app.services.pokeapi_client import PokeAPIClient


def test_get_pokemon_success(app):
    with app.app_context():
        mock_response = Mock()
        mock_response.json.return_value = {'id': 25, 'name': 'pikachu'}
        mock_response.raise_for_status = Mock()
        
        with patch('requests.Session.get', return_value=mock_response):
            client = PokeAPIClient()
            result = client.get_pokemon('pikachu')
            
            assert result['name'] == 'pikachu'
            assert result['id'] == 25


def test_get_pokemon_not_found(app):
    with app.app_context():
        mock_response = Mock()
        mock_response.status_code = 404
        http_error = requests.exceptions.HTTPError()
        http_error.response = mock_response
        mock_response.raise_for_status.side_effect = http_error
        
        with patch('requests.Session.get', return_value=mock_response):
            client = PokeAPIClient()
            
            with pytest.raises(ValueError, match="not found"):
                client.get_pokemon('missingno')


def test_get_pokemon_connection_error(app):
    with app.app_context():
        with patch('requests.Session.get', side_effect=requests.exceptions.ConnectionError('Network error')):
            client = PokeAPIClient()
            
            with pytest.raises(ConnectionError, match="Failed to fetch"):
                client.get_pokemon('pikachu')


def test_get_pokemon_http_error(app):
    with app.app_context():
        mock_response = Mock()
        mock_response.status_code = 500
        http_error = requests.exceptions.HTTPError()
        http_error.response = mock_response
        mock_response.raise_for_status.side_effect = http_error
        
        with patch('requests.Session.get', return_value=mock_response):
            client = PokeAPIClient()
            
            with pytest.raises(requests.exceptions.HTTPError):
                client.get_pokemon('pikachu')


def test_get_pokemon_species_success(app):
    with app.app_context():
        mock_response = Mock()
        mock_response.json.return_value = {'name': 'pikachu', 'generation': {'name': 'generation-i'}}
        mock_response.raise_for_status = Mock()
        
        with patch('requests.Session.get', return_value=mock_response):
            client = PokeAPIClient()
            result = client.get_pokemon_species('pikachu')
            
            assert result['name'] == 'pikachu'


def test_get_pokemon_species_error(app):
    with app.app_context():
        with patch('requests.Session.get', side_effect=requests.exceptions.RequestException()):
            client = PokeAPIClient()
            result = client.get_pokemon_species('pikachu')
            
            assert result is None


def test_get_ability_success(app):
    with app.app_context():
        mock_response = Mock()
        mock_response.json.return_value = {'name': 'static'}
        mock_response.raise_for_status = Mock()
        
        with patch('requests.Session.get', return_value=mock_response):
            client = PokeAPIClient()
            result = client.get_ability('static')
            
            assert result['name'] == 'static'


def test_get_ability_error(app):
    with app.app_context():
        with patch('requests.Session.get', side_effect=requests.exceptions.RequestException()):
            client = PokeAPIClient()
            result = client.get_ability('static')
            
            assert result is None


def test_get_move_success(app):
    with app.app_context():
        mock_response = Mock()
        mock_response.json.return_value = {'name': 'thunder-shock', 'power': 40}
        mock_response.raise_for_status = Mock()
        
        with patch('requests.Session.get', return_value=mock_response):
            client = PokeAPIClient()
            result = client.get_move('thunder-shock')
            
            assert result['name'] == 'thunder-shock'


def test_get_move_error(app):
    with app.app_context():
        with patch('requests.Session.get', side_effect=requests.exceptions.RequestException()):
            client = PokeAPIClient()
            result = client.get_move('thunder-shock')
            
            assert result is None


def test_client_close(app):
    with app.app_context():
        client = PokeAPIClient()
        client.close()


def test_custom_base_url():
    client = PokeAPIClient(base_url='https://custom-api.com')
    assert client.base_url == 'https://custom-api.com'

