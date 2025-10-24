from typing import Dict, Any, List, Optional
from app.models import db, Pokemon, PokemonType, PokemonAbility, PokemonStat, PokemonMove
from app.services.pokeapi_client import PokeAPIClient


class DataProcessor:
    
    def __init__(self):
        self.api_client = PokeAPIClient()
    
    def fetch_and_store_pokemon(self, pokemon_name: str) -> Pokemon:
        raw_data = self.api_client.get_pokemon(pokemon_name)
        sanitized_data = self._sanitize_pokemon_data(raw_data)
        
        pokemon = self._get_or_create_pokemon(sanitized_data)
        self._update_pokemon_relations(pokemon, sanitized_data)
        
        db.session.commit()
        return pokemon
    
    def _sanitize_pokemon_data(self, raw_data: Dict[str, Any]) -> Dict[str, Any]:
        sprites = raw_data.get('sprites', {})
        sprite_url = sprites.get('front_default') or sprites.get('other', {}).get('official-artwork', {}).get('front_default')
        
        return {
            'name': raw_data.get('name', '').lower(),
            'pokedex_id': raw_data.get('id', 0),
            'height': raw_data.get('height', 0),
            'weight': raw_data.get('weight', 0),
            'base_experience': raw_data.get('base_experience', 0),
            'generation': self._extract_generation(raw_data.get('id', 0)),
            'sprite_url': sprite_url,
            'is_legendary': raw_data.get('is_legendary', False),
            'is_mythical': raw_data.get('is_mythical', False),
            'types': self._extract_types(raw_data.get('types', [])),
            'abilities': self._extract_abilities(raw_data.get('abilities', [])),
            'stats': self._extract_stats(raw_data.get('stats', [])),
            'moves': self._extract_moves(raw_data.get('moves', []))
        }
    
    def _extract_generation(self, pokedex_id: int) -> int:
        if pokedex_id <= 151:
            return 1
        elif pokedex_id <= 251:
            return 2
        elif pokedex_id <= 386:
            return 3
        elif pokedex_id <= 493:
            return 4
        elif pokedex_id <= 649:
            return 5
        elif pokedex_id <= 721:
            return 6
        elif pokedex_id <= 809:
            return 7
        elif pokedex_id <= 905:
            return 8
        else:
            return 9
    
    def _extract_types(self, types_data: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        return [
            {
                'name': type_entry['type']['name'],
                'slot': type_entry.get('slot', 0)
            }
            for type_entry in types_data
        ]
    
    def _extract_abilities(self, abilities_data: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        return [
            {
                'name': ability_entry['ability']['name'],
                'is_hidden': ability_entry.get('is_hidden', False),
                'slot': ability_entry.get('slot', 0)
            }
            for ability_entry in abilities_data
        ]
    
    def _extract_stats(self, stats_data: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        return [
            {
                'name': stat_entry['stat']['name'],
                'base_stat': stat_entry.get('base_stat', 0),
                'effort': stat_entry.get('effort', 0)
            }
            for stat_entry in stats_data
        ]
    
    def _extract_moves(self, moves_data: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        extracted_moves = []
        level_up_moves = []
        other_moves = []
        
        for move_entry in moves_data:
            move_name = move_entry['move']['name']
            version_group_details = move_entry.get('version_group_details', [])
            
            if version_group_details:
                latest_version = version_group_details[-1]
                learn_method = latest_version.get('move_learn_method', {}).get('name', 'unknown')
                move_data = {
                    'name': move_name,
                    'learn_method': learn_method,
                    'level_learned_at': latest_version.get('level_learned_at', 0)
                }
                
                if learn_method == 'level-up':
                    level_up_moves.append(move_data)
                elif learn_method in ['machine', 'tutor', 'egg']:
                    other_moves.append(move_data)
        
        level_up_moves.sort(key=lambda x: x['level_learned_at'])
        extracted_moves.extend(level_up_moves[:50])
        extracted_moves.extend(other_moves[:50])
        
        return extracted_moves[:100]
    
    def _get_or_create_pokemon(self, data: Dict[str, Any]) -> Pokemon:
        pokemon = Pokemon.query.filter_by(name=data['name']).first()
        
        if pokemon:
            pokemon.height = data['height']
            pokemon.weight = data['weight']
            pokemon.base_experience = data['base_experience']
            pokemon.pokedex_id = data['pokedex_id']
            pokemon.generation = data['generation']
            pokemon.sprite_url = data['sprite_url']
            pokemon.is_legendary = data['is_legendary']
            pokemon.is_mythical = data['is_mythical']
            
            for relation in ['types', 'abilities', 'stats', 'moves']:
                getattr(pokemon, relation).clear()
        else:
            pokemon = Pokemon(
                name=data['name'],
                pokedex_id=data['pokedex_id'],
                height=data['height'],
                weight=data['weight'],
                base_experience=data['base_experience'],
                generation=data['generation'],
                sprite_url=data['sprite_url'],
                is_legendary=data['is_legendary'],
                is_mythical=data['is_mythical']
            )
            db.session.add(pokemon)
        
        return pokemon
    
    def _update_pokemon_relations(self, pokemon: Pokemon, data: Dict[str, Any]):
        for type_data in data['types']:
            pokemon_type = PokemonType(
                type_name=type_data['name'],
                slot=type_data['slot']
            )
            pokemon.types.append(pokemon_type)
        
        for ability_data in data['abilities']:
            pokemon_ability = PokemonAbility(
                ability_name=ability_data['name'],
                is_hidden=ability_data['is_hidden'],
                slot=ability_data['slot']
            )
            pokemon.abilities.append(pokemon_ability)
        
        for stat_data in data['stats']:
            pokemon_stat = PokemonStat(
                stat_name=stat_data['name'],
                base_stat=stat_data['base_stat'],
                effort=stat_data['effort']
            )
            pokemon.stats.append(pokemon_stat)
        
        for move_data in data['moves']:
            pokemon_move = PokemonMove(
                move_name=move_data['name'],
                learn_method=move_data['learn_method'],
                level_learned_at=move_data['level_learned_at']
            )
            pokemon.moves.append(pokemon_move)
    
    def fetch_multiple_pokemon(self, pokemon_names: List[str]) -> List[Pokemon]:
        results = []
        errors = []
        
        for name in pokemon_names:
            try:
                pokemon = self.fetch_and_store_pokemon(name)
                results.append(pokemon)
            except Exception as e:
                errors.append({'pokemon': name, 'error': str(e)})
        
        return results, errors

