"""
NPC Spawning
============

Factory functions and templates for creating NPCs.
"""

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Set
from random import choice, randint

from .base import NPC, NPCType, BehaviorState, ActivityLevel, NPCPreferences
from .npc_types import AmbientNPC, ServiceNPC, CompanionNPC, FeralNPC, GuardNPC, UniqueNPC

try:
    from evennia import create_object
    from evennia.utils.search import search_object
    HAS_EVENNIA = True
except ImportError:
    HAS_EVENNIA = False
    def create_object(*args, **kwargs): return None
    def search_object(*args, **kwargs): return []


# =============================================================================
# TEMPLATES
# =============================================================================

@dataclass
class NPCTemplate:
    """Template for spawning NPCs."""
    name_pool: List[str] = field(default_factory=list)
    short_desc: str = ""
    npc_class: type = NPC
    npc_type: NPCType = NPCType.AMBIENT
    body_preset: Optional[str] = None
    body_config: Optional[Dict] = None
    behavior_state: BehaviorState = BehaviorState.IDLE
    activity_level: ActivityLevel = ActivityLevel.REACTIVE
    dom_sub_range: tuple = (30, 70)
    libido_range: tuple = (30, 70)
    forwardness_range: tuple = (20, 60)
    attracted_to: Set[str] = field(default_factory=lambda: {"male", "female"})
    extra_attrs: Dict = field(default_factory=dict)


# Preset templates
TAVERN_PATRON = NPCTemplate(
    name_pool=["Weary Traveler", "Local Drunk", "Grizzled Veteran"],
    short_desc="a tavern patron",
    npc_class=AmbientNPC,
    npc_type=NPCType.AMBIENT,
    body_preset="human_male",
    extra_attrs={
        "ambient_actions": ["takes a drink.", "mutters to themselves.", "stares into their cup."],
        "ambient_frequency": 0.03,
    }
)

BARTENDER = NPCTemplate(
    name_pool=["Barkeep", "Innkeeper"],
    short_desc="the bartender",
    npc_class=ServiceNPC,
    npc_type=NPCType.SERVICE,
    body_preset="human_male",
    extra_attrs={
        "service_type": "bar",
        "work_greeting": "What'll it be?",
    }
)

GUARD = NPCTemplate(
    name_pool=["Town Guard", "Gate Guard"],
    short_desc="a guard",
    npc_class=GuardNPC,
    npc_type=NPCType.GUARD,
    body_preset="human_male",
    behavior_state=BehaviorState.WORKING,
    extra_attrs={"combat_skill": 60}
)

WOLF = NPCTemplate(
    name_pool=["Wolf", "Gray Wolf", "Timber Wolf"],
    short_desc="a wild wolf",
    npc_class=FeralNPC,
    npc_type=NPCType.FERAL,
    body_config={"structure": "quadruped", "species": "wolf", "sex": "male"},
    extra_attrs={
        "animal_type": "canine",
        "is_domesticated": False,
        "sounds": {
            "neutral": ["looks around.", "sniffs the air."],
            "happy": ["wags its tail.", "pants."],
            "aggressive": ["growls.", "bares fangs."],
            "afraid": ["whimpers.", "tucks its tail."],
        },
    }
)

WOLF_COMPANION = NPCTemplate(
    name_pool=["Shadow", "Luna", "Fang", "Storm"],
    short_desc="a large wolf",
    npc_class=CompanionNPC,
    npc_type=NPCType.COMPANION,
    body_config={"structure": "quadruped", "species": "wolf", "sex": "male"},
    activity_level=ActivityLevel.PROACTIVE,
    dom_sub_range=(40, 70),
    libido_range=(50, 80),
)


# =============================================================================
# FACTORY FUNCTIONS
# =============================================================================

def spawn_npc(template: NPCTemplate, location, name: str = None, **kwargs) -> Optional[NPC]:
    """Spawn an NPC from a template."""
    if not HAS_EVENNIA:
        return None
    
    npc_name = name or (choice(template.name_pool) if template.name_pool else "NPC")
    
    npc = create_object(template.npc_class, key=npc_name, location=location)
    if not npc:
        return None
    
    npc.db.npc_type = kwargs.get("npc_type", template.npc_type)
    npc.db.short_desc = kwargs.get("short_desc", template.short_desc)
    npc.db.behavior_state = kwargs.get("behavior_state", template.behavior_state)
    npc.db.activity_level = kwargs.get("activity_level", template.activity_level)
    
    # Body
    if template.body_preset:
        try:
            npc.init_body_preset(template.body_preset)
        except Exception:
            pass
    elif template.body_config:
        config = template.body_config.copy()
        config.update(kwargs.get("body_config", {}))
        try:
            npc.init_body(**config)
        except Exception:
            pass
    
    # Preferences
    prefs = NPCPreferences(
        attracted_to=set(template.attracted_to),
        dom_sub_tendency=randint(*template.dom_sub_range),
        libido=randint(*template.libido_range),
        forwardness=randint(*template.forwardness_range),
    )
    npc.set_preferences(prefs)
    
    # Extra attributes
    for key, value in template.extra_attrs.items():
        setattr(npc.db, key, value)
    
    return npc


# =============================================================================
# POPULATION
# =============================================================================

@dataclass
class PopulationConfig:
    """Room population settings."""
    min_npcs: int = 0
    max_npcs: int = 5
    allowed_types: List[NPCType] = field(default_factory=lambda: [NPCType.AMBIENT])
    templates: List[NPCTemplate] = field(default_factory=list)
    spawn_chance: float = 0.5


def populate_room(room, config: PopulationConfig) -> List[NPC]:
    """Ensure room has appropriate NPC population."""
    current = [obj for obj in room.contents if isinstance(obj, NPC)]
    total = len(current)
    
    while total < config.min_npcs:
        if config.templates:
            template = choice(config.templates)
            npc = spawn_npc(template, room)
            if npc:
                current.append(npc)
                total += 1
    
    return current


def find_npcs_in_room(room, npc_type: NPCType = None) -> List[NPC]:
    """Find NPCs in a room."""
    npcs = [obj for obj in room.contents if isinstance(obj, NPC)]
    if npc_type:
        npcs = [n for n in npcs if getattr(n.db, 'npc_type', None) == npc_type]
    return npcs


def find_npc_by_name(room, name: str) -> Optional[NPC]:
    """Find NPC by name."""
    for obj in room.contents:
        if isinstance(obj, NPC) and name.lower() in obj.key.lower():
            return obj
    return None


__all__ = [
    "NPCTemplate", "PopulationConfig",
    "TAVERN_PATRON", "BARTENDER", "GUARD", "WOLF", "WOLF_COMPANION",
    "spawn_npc", "populate_room", "find_npcs_in_room", "find_npc_by_name",
]
