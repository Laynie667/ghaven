"""
NPC Base
========

Base class for Non-Player Characters with body system integration.
"""

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple
from enum import Enum
from datetime import datetime
from random import random

from evennia.objects.objects import DefaultCharacter
from evennia import AttributeProperty


# =============================================================================
# ENUMS
# =============================================================================

class NPCType(Enum):
    AMBIENT = "ambient"
    SERVICE = "service"
    COMPANION = "companion"
    FERAL = "feral"
    GUARD = "guard"
    UNIQUE = "unique"


class BehaviorState(Enum):
    IDLE = "idle"
    WANDERING = "wandering"
    WORKING = "working"
    CONVERSING = "conversing"
    FOLLOWING = "following"
    INTERESTED = "interested"
    FLIRTING = "flirting"
    AROUSED = "aroused"
    ENGAGED = "engaged"
    AFRAID = "afraid"
    AGGRESSIVE = "aggressive"


class Disposition(Enum):
    HOSTILE = -2
    UNFRIENDLY = -1
    NEUTRAL = 0
    FRIENDLY = 1
    INTIMATE = 2


# =============================================================================
# DATA CLASSES
# =============================================================================

@dataclass
class Relationship:
    """NPC's relationship with a character."""
    character_dbref: str
    disposition: Disposition = Disposition.NEUTRAL
    familiarity: int = 0
    trust: int = 50
    attraction: int = 0
    respect: int = 50
    fear: int = 0
    times_met: int = 0
    times_intimate: int = 0
    last_seen: Optional[datetime] = None


@dataclass
class NPCPreferences:
    """NPC's interaction preferences."""
    attracted_to: List[str] = field(default_factory=lambda: ["male", "female"])
    preferred_roles: List[str] = field(default_factory=lambda: ["top", "bottom", "switch"])
    likes: List[str] = field(default_factory=list)
    hard_limits: List[str] = field(default_factory=list)
    dom_sub_tendency: int = 50
    libido: int = 50
    forwardness: int = 50


# =============================================================================
# NPC BASE CLASS
# =============================================================================

class NPC(DefaultCharacter):
    """
    Base NPC with body system integration.
    """
    
    npc_type = AttributeProperty(default=NPCType.AMBIENT)
    behavior_state = AttributeProperty(default=BehaviorState.IDLE)
    
    # Relationships
    relationships_data = AttributeProperty(default=dict)
    preferences_data = AttributeProperty(default=None)
    
    # Body system
    body_data = AttributeProperty(default=None)
    
    def get_body(self):
        """Get NPC's Body object."""
        if hasattr(self, '_body_cache') and self._body_cache:
            return self._body_cache
        if self.body_data:
            try:
                from .body import Body
                self._body_cache = Body.from_dict(self.body_data)
                return self._body_cache
            except ImportError:
                pass
        return None
    
    def set_body(self, body):
        self._body_cache = body
        self.body_data = body.to_dict()
    
    def save_body(self):
        if hasattr(self, '_body_cache') and self._body_cache:
            self.body_data = self._body_cache.to_dict()
    
    def init_body(self, structure: str = "bipedal_plantigrade", 
                  species: str = "human", sex: str = "male", **kwargs):
        """Initialize body by composition."""
        try:
            from .body import Body
            body = Body.compose(
                structure_key=structure,
                species_key=species,
                sex_config_key=sex,
                **kwargs
            )
            self.set_body(body)
        except ImportError:
            pass
    
    # Relationships
    def get_relationship(self, character) -> Relationship:
        dbref = character.dbref if hasattr(character, 'dbref') else str(character)
        data = (self.relationships_data or {}).get(dbref)
        if data:
            return Relationship(**data)
        return Relationship(character_dbref=dbref)
    
    def save_relationship(self, rel: Relationship):
        if not self.relationships_data:
            self.relationships_data = {}
        self.relationships_data[rel.character_dbref] = {
            'character_dbref': rel.character_dbref,
            'disposition': rel.disposition.value if isinstance(rel.disposition, Disposition) else rel.disposition,
            'familiarity': rel.familiarity,
            'trust': rel.trust,
            'attraction': rel.attraction,
            'respect': rel.respect,
            'fear': rel.fear,
            'times_met': rel.times_met,
            'times_intimate': rel.times_intimate,
            'last_seen': rel.last_seen.isoformat() if rel.last_seen else None,
        }
    
    def update_relationship(self, character, trust_change: int = 0,
                           attraction_change: int = 0, fear_change: int = 0,
                           familiarity_change: int = 0, respect_change: int = 0):
        rel = self.get_relationship(character)
        rel.trust = max(0, min(100, rel.trust + trust_change))
        rel.attraction = max(0, min(100, rel.attraction + attraction_change))
        rel.fear = max(0, min(100, rel.fear + fear_change))
        rel.familiarity = max(0, min(100, rel.familiarity + familiarity_change))
        rel.respect = max(0, min(100, rel.respect + respect_change))
        self.save_relationship(rel)
    
    # Preferences
    def get_preferences(self) -> NPCPreferences:
        if self.preferences_data:
            return NPCPreferences(**self.preferences_data)
        return NPCPreferences()
    
    def set_preferences(self, prefs: NPCPreferences):
        self.preferences_data = {
            'attracted_to': prefs.attracted_to,
            'preferred_roles': prefs.preferred_roles,
            'likes': prefs.likes,
            'hard_limits': prefs.hard_limits,
            'dom_sub_tendency': prefs.dom_sub_tendency,
            'libido': prefs.libido,
            'forwardness': prefs.forwardness,
        }
    
    # Hooks
    def on_character_arrives(self, character):
        rel = self.get_relationship(character)
        rel.last_seen = datetime.now()
        rel.times_met += 1
        self.save_relationship(rel)
    
    def on_character_leaves(self, character, destination):
        pass
    
    def on_spoken_to(self, speaker, message):
        pass


__all__ = [
    "NPCType", "BehaviorState", "Disposition",
    "Relationship", "NPCPreferences", "NPC",
]
