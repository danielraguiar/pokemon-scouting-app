from flask_restx import Api, Resource, fields, Namespace

api = Api(
    version='1.0',
    title='Pokemon Scouting API',
    description='A comprehensive API for managing Pokemon data from PokeAPI',
    doc='/api/docs'
)

pokemon_ns = api.namespace('pokemon', description='Pokemon operations', path='/')
health_ns = api.namespace('health', description='Health check', path='/')

type_model = api.model('Type', {
    'type': fields.String(description='Type name', example='electric'),
    'slot': fields.Integer(description='Type slot', example=1)
})

ability_model = api.model('Ability', {
    'name': fields.String(description='Ability name', example='static'),
    'is_hidden': fields.Boolean(description='Is hidden ability', example=False),
    'slot': fields.Integer(description='Ability slot', example=1)
})

stat_model = api.model('Stat', {
    'name': fields.String(description='Stat name', example='hp'),
    'base_stat': fields.Integer(description='Base stat value', example=35),
    'effort': fields.Integer(description='Effort value', example=0)
})

move_model = api.model('Move', {
    'name': fields.String(description='Move name', example='thunder-shock'),
    'learn_method': fields.String(description='Learn method', example='level-up'),
    'level_learned_at': fields.Integer(description='Level learned', example=1)
})

pokemon_summary_model = api.model('PokemonSummary', {
    'id': fields.Integer(description='Database ID', example=1),
    'name': fields.String(description='Pokemon name', example='pikachu'),
    'pokedex_id': fields.Integer(description='Pokedex number', example=25)
})

pokemon_detail_model = api.model('PokemonDetail', {
    'id': fields.Integer(description='Database ID'),
    'name': fields.String(description='Pokemon name'),
    'pokedex_id': fields.Integer(description='Pokedex number'),
    'height': fields.Integer(description='Height in decimeters'),
    'weight': fields.Integer(description='Weight in hectograms'),
    'base_experience': fields.Integer(description='Base experience'),
    'generation': fields.Integer(description='Generation number'),
    'sprite_url': fields.String(description='Sprite image URL'),
    'is_legendary': fields.Boolean(description='Is legendary'),
    'is_mythical': fields.Boolean(description='Is mythical'),
    'types': fields.List(fields.Nested(type_model)),
    'abilities': fields.List(fields.Nested(ability_model)),
    'stats': fields.List(fields.Nested(stat_model)),
    'moves': fields.List(fields.Nested(move_model)),
    'created_at': fields.String(description='Creation timestamp'),
    'updated_at': fields.String(description='Last update timestamp')
})

pokemon_list_response = api.model('PokemonListResponse', {
    'count': fields.Integer(description='Total count', example=9),
    'page': fields.Integer(description='Current page', example=1),
    'per_page': fields.Integer(description='Items per page', example=20),
    'total_pages': fields.Integer(description='Total pages', example=1),
    'pokemon': fields.List(fields.Nested(pokemon_summary_model))
})

health_response = api.model('HealthResponse', {
    'status': fields.String(description='Health status', example='healthy'),
    'database': fields.String(description='Database status', example='connected'),
    'pokemon_count': fields.Integer(description='Number of Pokemon in database', example=9)
})

error_response = api.model('ErrorResponse', {
    'error': fields.String(description='Error message', example='Pokemon not found')
})

fetch_multiple_request = api.model('FetchMultipleRequest', {
    'names': fields.List(
        fields.String,
        required=True,
        description='List of Pokemon names to fetch',
        example=['pikachu', 'charizard', 'mewtwo']
    )
})

fetch_multiple_response = api.model('FetchMultipleResponse', {
    'message': fields.String(description='Result message'),
    'success_count': fields.Integer(description='Number of successful fetches'),
    'error_count': fields.Integer(description='Number of errors'),
    'results': fields.List(fields.Nested(pokemon_detail_model)),
    'errors': fields.List(fields.Raw(description='Error details'))
})

delete_response = api.model('DeleteResponse', {
    'message': fields.String(description='Success message', example='Successfully soft deleted pikachu'),
    'deleted_at': fields.String(description='Deletion timestamp')
})

restore_response = api.model('RestoreResponse', {
    'message': fields.String(description='Success message', example='Successfully restored pikachu')
})

@health_ns.route('/health')
class HealthCheck(Resource):
    @health_ns.doc('health_check')
    @health_ns.response(200, 'Success', health_response)
    @health_ns.response(503, 'Service Unavailable', error_response)
    def get(self):
        """Health check endpoint - Check API and database status"""
        pass

@pokemon_ns.route('/pokemon')
class PokemonList(Resource):
    @pokemon_ns.doc('list_pokemon')
    @pokemon_ns.param('page', 'Page number', type=int, default=1)
    @pokemon_ns.param('per_page', 'Items per page (max 100)', type=int, default=20)
    @pokemon_ns.param('include_deleted', 'Include soft-deleted Pokemon', type=bool, default=False)
    @pokemon_ns.response(200, 'Success', pokemon_list_response)
    def get(self):
        """List all Pokemon with pagination"""
        pass

@pokemon_ns.route('/pokemon/<string:name>')
@pokemon_ns.param('name', 'Pokemon name (lowercase)')
class PokemonDetail(Resource):
    @pokemon_ns.doc('get_pokemon')
    @pokemon_ns.response(200, 'Success', pokemon_detail_model)
    @pokemon_ns.response(404, 'Not Found', error_response)
    @pokemon_ns.response(400, 'Bad Request', error_response)
    def get(self, name):
        """Get a specific Pokemon by name"""
        pass
    
    @pokemon_ns.doc('delete_pokemon')
    @pokemon_ns.response(200, 'Success', delete_response)
    @pokemon_ns.response(404, 'Not Found', error_response)
    def delete(self, name):
        """Soft delete a Pokemon (can be restored)"""
        pass

@pokemon_ns.route('/pokemon/<string:name>/restore')
@pokemon_ns.param('name', 'Pokemon name to restore')
class PokemonRestore(Resource):
    @pokemon_ns.doc('restore_pokemon')
    @pokemon_ns.response(200, 'Success', restore_response)
    @pokemon_ns.response(404, 'Not Found', error_response)
    def post(self, name):
        """Restore a soft-deleted Pokemon"""
        pass

@pokemon_ns.route('/pokemon/<string:name>/export')
@pokemon_ns.param('name', 'Pokemon name to export')
class PokemonExport(Resource):
    @pokemon_ns.doc('export_pokemon')
    @pokemon_ns.response(200, 'Success', pokemon_detail_model)
    @pokemon_ns.response(404, 'Not Found', error_response)
    def get(self, name):
        """Export a single Pokemon as JSON"""
        pass

@pokemon_ns.route('/pokemon/fetch/<string:name>')
@pokemon_ns.param('name', 'Pokemon name to fetch from PokeAPI')
class PokemonFetch(Resource):
    @pokemon_ns.doc('fetch_pokemon')
    @pokemon_ns.response(200, 'Success', pokemon_detail_model)
    @pokemon_ns.response(404, 'Not Found', error_response)
    @pokemon_ns.response(429, 'Too Many Requests', error_response)
    def post(self, name):
        """Fetch a Pokemon from PokeAPI and store in database (Rate limited: 10/min)"""
        pass

@pokemon_ns.route('/pokemon/fetch-multiple')
class PokemonFetchMultiple(Resource):
    @pokemon_ns.doc('fetch_multiple_pokemon')
    @pokemon_ns.expect(fetch_multiple_request, validate=True)
    @pokemon_ns.response(200, 'Success', fetch_multiple_response)
    @pokemon_ns.response(207, 'Partial Success', fetch_multiple_response)
    @pokemon_ns.response(400, 'Bad Request', error_response)
    @pokemon_ns.response(429, 'Too Many Requests', error_response)
    def post(self):
        """Fetch multiple Pokemon from PokeAPI (Rate limited: 5/min, max 100 Pokemon per request)"""
        pass

@pokemon_ns.route('/pokemon/export/stream/json')
class PokemonStreamJSON(Resource):
    @pokemon_ns.doc('stream_export_json')
    @pokemon_ns.response(200, 'Success - Streaming JSON')
    def get(self):
        """Stream all Pokemon as JSON (memory-efficient for large datasets)"""
        pass

@pokemon_ns.route('/pokemon/export/stream/csv')
class PokemonStreamCSV(Resource):
    @pokemon_ns.doc('stream_export_csv')
    @pokemon_ns.response(200, 'Success - Streaming CSV')
    @pokemon_ns.produces(['text/csv'])
    def get(self):
        """Stream all Pokemon as CSV (memory-efficient, opens in Excel)"""
        pass

