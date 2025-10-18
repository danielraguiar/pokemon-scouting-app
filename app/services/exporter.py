import json
import csv
from typing import List, Optional
from pathlib import Path
from app.models import Pokemon


class DataExporter:
    
    @staticmethod
    def export_to_json(pokemon: Pokemon, filepath: Optional[str] = None) -> str:
        data = pokemon.to_dict()
        json_str = json.dumps(data, indent=2)
        
        if filepath:
            output_path = Path(filepath)
            output_path.parent.mkdir(parents=True, exist_ok=True)
            
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(json_str)
        
        return json_str
    
    @staticmethod
    def export_multiple_to_json(pokemon_list: List[Pokemon], filepath: Optional[str] = None) -> str:
        data = {
            'count': len(pokemon_list),
            'pokemon': [p.to_dict() for p in pokemon_list]
        }
        json_str = json.dumps(data, indent=2)
        
        if filepath:
            output_path = Path(filepath)
            output_path.parent.mkdir(parents=True, exist_ok=True)
            
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(json_str)
        
        return json_str
    
    @staticmethod
    def export_to_csv(pokemon_list: List[Pokemon], filepath: str):
        output_path = Path(filepath)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(output_path, 'w', newline='', encoding='utf-8') as f:
            if not pokemon_list:
                return
            
            fieldnames = [
                'name', 'pokedex_id', 'height', 'weight', 'base_experience',
                'types', 'abilities', 'hp', 'attack', 'defense',
                'special_attack', 'special_defense', 'speed'
            ]
            
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            
            for pokemon in pokemon_list:
                stats_dict = {stat.stat_name: stat.base_stat for stat in pokemon.stats}
                
                row = {
                    'name': pokemon.name,
                    'pokedex_id': pokemon.pokedex_id,
                    'height': pokemon.height,
                    'weight': pokemon.weight,
                    'base_experience': pokemon.base_experience,
                    'types': ', '.join([t.type_name for t in pokemon.types]),
                    'abilities': ', '.join([a.ability_name for a in pokemon.abilities]),
                    'hp': stats_dict.get('hp', 0),
                    'attack': stats_dict.get('attack', 0),
                    'defense': stats_dict.get('defense', 0),
                    'special_attack': stats_dict.get('special-attack', 0),
                    'special_defense': stats_dict.get('special-defense', 0),
                    'speed': stats_dict.get('speed', 0)
                }
                
                writer.writerow(row)

