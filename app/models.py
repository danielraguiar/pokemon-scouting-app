from flask_sqlalchemy import SQLAlchemy
from datetime import datetime, UTC
import json

db = SQLAlchemy()


class Pokemon(db.Model):
    __tablename__ = 'pokemon'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), unique=True, nullable=False, index=True)
    pokedex_id = db.Column(db.Integer, nullable=False)
    height = db.Column(db.Integer)
    weight = db.Column(db.Integer)
    base_experience = db.Column(db.Integer)
    generation = db.Column(db.Integer)
    sprite_url = db.Column(db.String(500))
    is_legendary = db.Column(db.Boolean, default=False)
    is_mythical = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(UTC))
    updated_at = db.Column(db.DateTime, default=lambda: datetime.now(UTC), onupdate=lambda: datetime.now(UTC))
    
    types = db.relationship('PokemonType', back_populates='pokemon', cascade='all, delete-orphan')
    abilities = db.relationship('PokemonAbility', back_populates='pokemon', cascade='all, delete-orphan')
    stats = db.relationship('PokemonStat', back_populates='pokemon', cascade='all, delete-orphan')
    moves = db.relationship('PokemonMove', back_populates='pokemon', cascade='all, delete-orphan')
    
    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'pokedex_id': self.pokedex_id,
            'height': self.height,
            'weight': self.weight,
            'base_experience': self.base_experience,
            'generation': self.generation,
            'sprite_url': self.sprite_url,
            'is_legendary': self.is_legendary,
            'is_mythical': self.is_mythical,
            'types': [t.to_dict() for t in self.types],
            'abilities': [a.to_dict() for a in self.abilities],
            'stats': [s.to_dict() for s in self.stats],
            'moves': [m.to_dict() for m in self.moves],
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }


class PokemonType(db.Model):
    __tablename__ = 'pokemon_types'
    
    id = db.Column(db.Integer, primary_key=True)
    pokemon_id = db.Column(db.Integer, db.ForeignKey('pokemon.id'), nullable=False)
    type_name = db.Column(db.String(50), nullable=False)
    slot = db.Column(db.Integer, nullable=False)
    
    pokemon = db.relationship('Pokemon', back_populates='types')
    
    def to_dict(self):
        return {
            'type': self.type_name,
            'slot': self.slot
        }


class PokemonAbility(db.Model):
    __tablename__ = 'pokemon_abilities'
    
    id = db.Column(db.Integer, primary_key=True)
    pokemon_id = db.Column(db.Integer, db.ForeignKey('pokemon.id'), nullable=False)
    ability_name = db.Column(db.String(100), nullable=False)
    is_hidden = db.Column(db.Boolean, default=False)
    slot = db.Column(db.Integer, nullable=False)
    
    pokemon = db.relationship('Pokemon', back_populates='abilities')
    
    def to_dict(self):
        return {
            'name': self.ability_name,
            'is_hidden': self.is_hidden,
            'slot': self.slot
        }


class PokemonStat(db.Model):
    __tablename__ = 'pokemon_stats'
    
    id = db.Column(db.Integer, primary_key=True)
    pokemon_id = db.Column(db.Integer, db.ForeignKey('pokemon.id'), nullable=False)
    stat_name = db.Column(db.String(50), nullable=False)
    base_stat = db.Column(db.Integer, nullable=False)
    effort = db.Column(db.Integer, default=0)
    
    pokemon = db.relationship('Pokemon', back_populates='stats')
    
    def to_dict(self):
        return {
            'name': self.stat_name,
            'base_stat': self.base_stat,
            'effort': self.effort
        }


class PokemonMove(db.Model):
    __tablename__ = 'pokemon_moves'
    
    id = db.Column(db.Integer, primary_key=True)
    pokemon_id = db.Column(db.Integer, db.ForeignKey('pokemon.id'), nullable=False)
    move_name = db.Column(db.String(100), nullable=False)
    learn_method = db.Column(db.String(50))
    level_learned_at = db.Column(db.Integer)
    
    pokemon = db.relationship('Pokemon', back_populates='moves')
    
    def to_dict(self):
        return {
            'name': self.move_name,
            'learn_method': self.learn_method,
            'level_learned_at': self.level_learned_at
        }

