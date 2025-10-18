import os
from pathlib import Path


class Config:
    BASE_DIR = Path(__file__).resolve().parent.parent
    SQLALCHEMY_DATABASE_URI = os.getenv(
        'DATABASE_URL',
        f'sqlite:///{BASE_DIR / "pokemon_scouting.db"}'
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    POKEAPI_BASE_URL = os.getenv('POKEAPI_BASE_URL', 'https://pokeapi.co/api/v2')
    DEFAULT_POKEMON = [
        'pikachu',
        'dhelmise',
        'charizard',
        'parasect',
        'aerodactyl',
        'kingler'
    ]

