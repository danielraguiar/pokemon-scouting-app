import os
from pathlib import Path


class Config:
    BASE_DIR = Path(__file__).resolve().parent.parent
    SECRET_KEY = os.getenv('SECRET_KEY', 'dev-secret-change-in-production')
    SQLALCHEMY_DATABASE_URI = os.getenv(
        'DATABASE_URL',
        f'sqlite:///{BASE_DIR / "pokemon_scouting.db"}'
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    POKEAPI_BASE_URL = os.getenv('POKEAPI_BASE_URL', 'https://pokeapi.co/api/v2')
    POKEAPI_REQUEST_TIMEOUT = int(os.getenv('POKEAPI_TIMEOUT', '10'))
    MAX_MOVES_PER_POKEMON = int(os.getenv('MAX_MOVES', '100'))
    DEFAULT_POKEMON = [
        'pikachu',
        'dhelmise',
        'charizard',
        'parasect',
        'aerodactyl',
        'kingler'
    ]


class DevelopmentConfig(Config):
    DEBUG = True
    ENV = 'development'


class ProductionConfig(Config):
    DEBUG = False
    ENV = 'production'


class TestingConfig(Config):
    TESTING = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'
    ENV = 'testing'

