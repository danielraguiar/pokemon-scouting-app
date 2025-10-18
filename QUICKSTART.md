# Pokémon Scouting App - Quick Start Guide

## Installation

1. Clone the repository
2. Install dependencies:
```bash
pip install -r requirements.txt
```

## Quick Usage Examples

### Fetch Default Pokémon
```bash
python -m flask --app run main fetch-default
```

This will fetch: Pikachu, Dhelmise, Charizard, Parasect, Aerodactyl, and Kingler

### Fetch Specific Pokémon
```bash
python -m flask --app run main fetch-pokemon mewtwo dragonite snorlax
```

### List All Pokémon in Database
```bash
python -m flask --app run main list-pokemon
```

### Export Data

**JSON Export:**
```bash
python -m flask --app run main export-json output.json
```

**CSV Export:**
```bash
python -m flask --app run main export-csv output.csv
```

## REST API Usage

### Start the Server
```bash
python run.py
```

Server runs on http://localhost:5000

### API Endpoints

**List all Pokémon:**
```bash
curl http://localhost:5000/pokemon
```

**Get specific Pokémon:**
```bash
curl http://localhost:5000/pokemon/pikachu
```

**Fetch and store a Pokémon:**
```bash
curl -X POST http://localhost:5000/pokemon/fetch/mewtwo
```

**Fetch multiple Pokémon:**
```bash
curl -X POST http://localhost:5000/pokemon/fetch-multiple \
  -H "Content-Type: application/json" \
  -d '{"names": ["bulbasaur", "charmander", "squirtle"]}'
```

## Running Tests

```bash
python -m pytest tests/ -v
```

## Project Structure

```
pokemon-scouting-app/
├── app/
│   ├── __init__.py          # Flask app factory
│   ├── config.py            # Configuration
│   ├── models.py            # Database models
│   ├── routes.py            # API routes and CLI commands
│   └── services/
│       ├── pokeapi_client.py    # API client
│       ├── data_processor.py    # Data processing
│       └── exporter.py          # Export functionality
├── tests/                   # Test suite
├── requirements.txt         # Dependencies
└── run.py                   # Entry point
```

## Key Features

- ✅ Fetch Pokémon data from PokeAPI
- ✅ Store data in SQLite database
- ✅ Export to JSON and CSV
- ✅ REST API and CLI interfaces
- ✅ Comprehensive test suite
- ✅ Easily configurable for any Pokémon

## Data Stored

For each Pokémon:
- Basic info (name, ID, height, weight, experience)
- Types (primary and secondary)
- Abilities (including hidden abilities)
- Stats (HP, Attack, Defense, Special Attack, Special Defense, Speed)
- Moves (with learn methods and levels)

## Extending the App

### Add More Default Pokémon

Edit `app/config.py`:
```python
DEFAULT_POKEMON = [
    'pikachu',
    'charizard',
    'mewtwo',     # Add here
    'dragonite'   # Add here
]
```

### Custom Database Queries

```python
from app import create_app
from app.models import Pokemon, PokemonType

app = create_app()
with app.app_context():
    electric_types = Pokemon.query.join(Pokemon.types).filter(
        PokemonType.type_name == 'electric'
    ).all()
```

