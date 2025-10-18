# Pokémon Scouting Application

A Python Flask application for retrieving, processing, storing, and exporting Pokémon data from the PokeAPI. This application provides both REST API endpoints and CLI commands for comprehensive Pokémon data management.

## Features

- **Data Retrieval**: Fetch Pokémon data from PokeAPI
- **Data Processing**: Sanitize and format raw API data
- **Database Storage**: SQLite database with SQLAlchemy ORM
- **Data Export**: Export to JSON and CSV formats
- **REST API**: RESTful endpoints for web integration
- **CLI Commands**: Command-line interface for batch operations
- **Comprehensive Testing**: Full pytest test suite
- **Reusable Design**: Easily configurable for any Pokémon

## Architecture

```
pokemon-scouting-app/
├── app/
│   ├── __init__.py           # Flask application factory
│   ├── config.py             # Configuration settings
│   ├── models.py             # SQLAlchemy database models
│   ├── routes.py             # Flask routes and CLI commands
│   └── services/
│       ├── pokeapi_client.py # PokeAPI HTTP client
│       ├── data_processor.py # Data processing and sanitization
│       └── exporter.py       # Data export functionality
├── tests/                    # Pytest test suite
├── requirements.txt          # Python dependencies
└── run.py                    # Application entry point
```

## Installation

### Prerequisites

- Python 3.8 or higher
- pip (Python package manager)
- Git

### Setup Instructions

1. **Clone the repository**
```bash
git clone https://github.com/yourusername/pokemon-scouting-app.git
cd pokemon-scouting-app
```

2. **Create a virtual environment**
```bash
python -m venv venv

# On Windows
venv\Scripts\activate

# On macOS/Linux
source venv/bin/activate
```

3. **Install dependencies**
```bash
pip install -r requirements.txt
```

4. **Initialize the database**
```bash
flask --app run main fetch-default
```

## Usage

### CLI Commands

The application provides several CLI commands for data management:

#### Fetch Default Pokémon
Fetch the default set of Pokémon (Pikachu, Dhelmise, Charizard, Parasect, Aerodactyl, Kingler):
```bash
flask --app run main fetch-default
```

#### Fetch Specific Pokémon
Fetch one or more specific Pokémon:
```bash
flask --app run main fetch-pokemon pikachu charizard mewtwo
```

#### List Pokémon
Display all Pokémon stored in the database:
```bash
flask --app run main list-pokemon
```

#### Export Data to JSON
Export all Pokémon data to a JSON file:
```bash
flask --app run main export-json pokemon_data.json
```

#### Export Data to CSV
Export all Pokémon data to a CSV file:
```bash
flask --app run main export-csv pokemon_data.csv
```

### REST API

Start the Flask development server:
```bash
flask --app run run
# or
python run.py
```

The server will start on `http://localhost:5000`

#### API Endpoints

**GET /** - API information
```bash
curl http://localhost:5000/
```

**GET /pokemon** - List all stored Pokémon
```bash
curl http://localhost:5000/pokemon
```

**GET /pokemon/<name>** - Get specific Pokémon details
```bash
curl http://localhost:5000/pokemon/pikachu
```

**POST /pokemon/fetch/<name>** - Fetch and store a Pokémon
```bash
curl -X POST http://localhost:5000/pokemon/fetch/pikachu
```

**POST /pokemon/fetch-multiple** - Fetch multiple Pokémon
```bash
curl -X POST http://localhost:5000/pokemon/fetch-multiple \
  -H "Content-Type: application/json" \
  -d '{"names": ["pikachu", "charizard", "mewtwo"]}'
```

**GET /pokemon/<name>/export** - Export specific Pokémon as JSON
```bash
curl http://localhost:5000/pokemon/pikachu/export
```

## Configuration

### Adding New Pokémon to Default List

Edit the `DEFAULT_POKEMON` list in `app/config.py`:

```python
DEFAULT_POKEMON = [
    'pikachu',
    'dhelmise',
    'charizard',
    'parasect',
    'aerodactyl',
    'kingler',
    'mewtwo',        # Add new Pokémon here
    'dragonite'      # Add more as needed
]
```

### Database Configuration

By default, the application uses SQLite. To change the database location or type, modify `SQLALCHEMY_DATABASE_URI` in `app/config.py`:

```python
SQLALCHEMY_DATABASE_URI = 'sqlite:///pokemon_scouting.db'
```

### PokeAPI Configuration

The base URL for PokeAPI is configurable in `app/config.py`:

```python
POKEAPI_BASE_URL = 'https://pokeapi.co/api/v2'
```

## Data Model

The application stores comprehensive Pokémon data:

### Pokemon Table
- Name, Pokédex ID, Height, Weight, Base Experience
- Timestamps (created_at, updated_at)

### Related Data
- **Types**: Primary and secondary types with slot positions
- **Abilities**: Regular and hidden abilities
- **Stats**: HP, Attack, Defense, Special Attack, Special Defense, Speed
- **Moves**: Move names, learn methods, and levels

## Testing

Run the complete test suite:

```bash
pytest
```

Run tests with coverage:

```bash
pytest --cov=app tests/
```

Run specific test files:

```bash
pytest tests/test_models.py
pytest tests/test_routes.py
pytest tests/test_services.py
```

## Data Sanitization

The application sanitizes and processes raw API data:

1. **Type Extraction**: Captures all Pokémon types with slot ordering
2. **Ability Processing**: Identifies regular and hidden abilities
3. **Stats Normalization**: Extracts base stats and effort values
4. **Move Filtering**: Processes moves with learn methods and levels
5. **Data Validation**: Ensures data integrity and consistency

## Extending the Application

### Adding New Pokémon

**Via CLI:**
```bash
flask --app run main fetch-pokemon snorlax gyarados
```

**Via API:**
```bash
curl -X POST http://localhost:5000/pokemon/fetch/snorlax
```

### Database Issues

If you encounter database errors, reset the database:

```bash
# Delete the database file
rm pokemon_scouting.db

# Reinitialize with default Pokémon
flask --app run main fetch-default
```

### API Connection Issues

If PokeAPI is unreachable:
- Check your internet connection
- Verify the API URL in `app/config.py`
- The PokeAPI may be temporarily down

### Module Not Found Errors

Ensure your virtual environment is activated and dependencies are installed:

```bash
pip install -r requirements.txt
```

## Project Structure Details

### Models (`app/models.py`)
- `Pokemon`: Main Pokémon entity
- `PokemonType`: Type relationships
- `PokemonAbility`: Ability relationships
- `PokemonStat`: Stat values
- `PokemonMove`: Move relationships

### Services
- `PokeAPIClient`: HTTP client for API requests
- `DataProcessor`: Data retrieval and sanitization
- `DataExporter`: Export functionality

### Routes (`app/routes.py`)
- REST API endpoints
- CLI commands via Flask-Click integration

## Technologies Used

- **Flask**: Web framework
- **SQLAlchemy**: ORM for database operations
- **Requests**: HTTP client for API calls
- **Pytest**: Testing framework
- **Click**: CLI command framework
- **SQLite**: Lightweight database

## Best Practices Implemented

1. **Application Factory Pattern**: Flexible app initialization
2. **Separation of Concerns**: Clear service layer architecture
3. **Error Handling**: Comprehensive exception management
4. **Data Validation**: Input sanitization and validation
5. **RESTful Design**: Standard HTTP methods and status codes
6. **Testing**: Unit and integration tests
7. **Configuration Management**: Environment-based settings
8. **Documentation**: Comprehensive inline and README docs
