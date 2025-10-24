from flask_restx import Api

api = Api(
    version='1.0',
    title='Pokemon Scouting API',
    description='A comprehensive API for managing Pokemon data from PokeAPI',
    doc='/api/docs',
    prefix='/api'
)

pokemon_ns = api.namespace('pokemon', description='Pokemon operations')
health_ns = api.namespace('health', description='Health check operations')

