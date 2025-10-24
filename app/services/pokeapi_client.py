import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
from typing import Optional, Dict, Any
from flask import current_app


class PokeAPIClient:
    
    def __init__(self, base_url: Optional[str] = None):
        self.base_url = base_url or current_app.config['POKEAPI_BASE_URL']
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Pokemon-Scouting-App/1.0'
        })
        
        retry_strategy = Retry(
            total=3,
            backoff_factor=1,
            status_forcelist=[429, 500, 502, 503, 504],
            allowed_methods=["GET"]
        )
        adapter = HTTPAdapter(max_retries=retry_strategy)
        self.session.mount("http://", adapter)
        self.session.mount("https://", adapter)
    
    def get_pokemon(self, pokemon_identifier: str) -> Optional[Dict[str, Any]]:
        url = f"{self.base_url}/pokemon/{pokemon_identifier.lower()}"
        
        try:
            response = self.session.get(url, timeout=10)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.HTTPError as e:
            if e.response.status_code == 404:
                raise ValueError(f"Pokemon '{pokemon_identifier}' not found")
            raise
        except requests.exceptions.RequestException as e:
            raise ConnectionError(f"Failed to fetch Pokemon data: {str(e)}")
    
    def get_pokemon_species(self, pokemon_identifier: str) -> Optional[Dict[str, Any]]:
        url = f"{self.base_url}/pokemon-species/{pokemon_identifier.lower()}"
        
        try:
            response = self.session.get(url, timeout=10)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException:
            return None
    
    def get_ability(self, ability_name: str) -> Optional[Dict[str, Any]]:
        url = f"{self.base_url}/ability/{ability_name.lower()}"
        
        try:
            response = self.session.get(url, timeout=10)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException:
            return None
    
    def get_move(self, move_name: str) -> Optional[Dict[str, Any]]:
        url = f"{self.base_url}/move/{move_name.lower()}"
        
        try:
            response = self.session.get(url, timeout=10)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException:
            return None
    
    def close(self):
        self.session.close()

