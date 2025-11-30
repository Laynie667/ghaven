"""
Pet Systems Initialization
==========================

Setup scripts for initializing the game world.
Creates locations, spawns NPCs, and prepares everything
for a player to... experience.

Run this to build a starting scenario.
"""

from typing import List, Optional
import random


def create_starting_world():
    """
    Create the initial game world with all locations and NPCs.
    Returns a summary of what was created.
    """
    from .typeclasses import PetSystemsRoom, PetSystemsNPC
    from .world.locations import ALL_LOCATION_TEMPLATES
    from .world import ALL_NPC_TEMPLATES
    
    created_rooms = []
    created_npcs = []
    
    # Create all location templates
    for template_id, template in ALL_LOCATION_TEMPLATES.items():
        room = PetSystemsRoom.create_from_template(template)
        created_rooms.append(room)
    
    # Spawn appropriate NPCs in each room
    npc_assignments = {
        "central_market": ["stern_slaver", "cruel_mistress"],
        "processing_center": ["efficient_handler"],
        "breaking_cells": ["cruel_mistress"],
        "rose_petal": ["stern_madam"],
        "the_pit": ["sleazy_pimp"],
        "public_stocks": [],  # Random passersby
        "green_pastures_dairy": ["hucow_trainer"],
        "milking_parlor": ["hucow_trainer"],
        "bull_pen": [],  # Bulls handled separately
        "silver_bridle_stables": ["pony_trainer"],
        "training_ring": ["pony_trainer"],
        "crimson_pit": ["arena_master"],
        "gladiator_barracks": [],
        "tentacle_pit": [],  # Monsters, not NPCs
        "slime_pool": [],
        "breeding_cave": ["monster_breeder"],
        "temple_of_lilith": ["corruption_cultist"],
        "bimbo_spa": [],  # Attendants would be bimbos
    }
    
    for room in created_rooms:
        template_id = room.db.template_id
        npc_ids = npc_assignments.get(template_id, [])
        
        for npc_id in npc_ids:
            template = ALL_NPC_TEMPLATES.get(npc_id)
            if template:
                npc = PetSystemsNPC.create_from_template(template, location=room)
                created_npcs.append(npc)
    
    # Link rooms together (basic connections)
    # In a real implementation, would create proper exits
    
    return {
        "rooms": len(created_rooms),
        "npcs": len(created_npcs),
        "room_list": [r.key for r in created_rooms],
        "npc_list": [n.key for n in created_npcs],
    }


def create_danger_zone():
    """
    Create a special danger zone - a gauntlet of perils.
    Perfect for testing... or punishment.
    """
    from .typeclasses import PetSystemsRoom
    from .world.dangers import ALL_DANGERS
    
    # Create a series of connected dangerous rooms
    rooms = []
    
    danger_sequence = [
        ("The Entrance", "You stand at the entrance to the danger zone. There's no turning back.", []),
        ("Slime Corridor", "The walls drip with suspicious slime...", ["slime_pit"]),
        ("Tentacle Hall", "Shadows writhe on the walls.", ["tentacle_snare"]),
        ("The Gas Chamber", "A faint pink mist fills this room.", ["aphrodisiac_gas"]),
        ("Goblin Den", "Crude drawings cover the walls.", ["goblin_pack"]),
        ("Orc Territory", "The smell of musk is overwhelming.", ["orc_raider"]),
        ("The Corruption Font", "Dark energy pulses from the center.", ["corruption_font"]),
        ("The Breeding Chamber", "Restraints line the walls.", ["breeding_trap"]),
        ("Tentacle Nest", "You shouldn't have come here.", ["tentacle_beast"]),
        ("The Final Chamber", "A succubus awaits.", ["succubus"]),
    ]
    
    for name, desc, dangers in danger_sequence:
        from evennia import create_object
        room = create_object(
            PetSystemsRoom,
            key=name,
        )
        room.db.desc = desc
        room.db.danger_level = "extreme"
        room.db.event_chance = 0.5
        room.db.escape_difficulty = 80
        room.db.possible_dangers = dangers
        rooms.append(room)
    
    # Would link rooms with exits here
    
    return rooms


def setup_player_scenario(character, scenario: str = "captured_slave"):
    """
    Set up a specific scenario for a player character.
    
    Scenarios:
    - free: Starting fresh
    - captured_slave: Already captured
    - brothel_worker: Working at the brothel
    - hucow: Registered as hucow
    - pony: Pony in training
    - corruption_victim: Undergoing transformation
    - arena_fighter: Fighting in the pits
    - breeding_stock: In the breeding pits
    """
    from .integration import initialize_character
    
    scenario_setups = {
        "free": _setup_free,
        "captured_slave": _setup_captured,
        "brothel_worker": _setup_brothel,
        "hucow": _setup_hucow,
        "pony": _setup_pony,
        "corruption_victim": _setup_corruption,
        "arena_fighter": _setup_fighter,
        "breeding_stock": _setup_breeding,
    }
    
    setup_func = scenario_setups.get(scenario, _setup_free)
    return setup_func(character)


def _setup_free(character) -> str:
    """Free character setup."""
    character.db.is_captured = False
    character.db.current_resistance = 80
    return "You are free... for now."


def _setup_captured(character) -> str:
    """Captured slave setup."""
    character.db.is_captured = True
    character.db.current_resistance = 50
    character.db.times_captured = 1
    
    # Some initial breaking
    if hasattr(character, 'character_state'):
        state = character.character_state
        state.sexual.arousal = 40
        state.mental.humiliation = 30
        character.character_state = state
    
    return "You are a captured slave. Your breaking has begun."


def _setup_brothel(character) -> str:
    """Brothel worker setup."""
    from .brothel import WhoreStats, WhoreSpecialization
    
    character.db.is_captured = True
    character.db.current_resistance = 40
    
    stats = WhoreStats(
        worker_dbref=character.dbref,
        worker_name=character.key,
        specialization=WhoreSpecialization.NONE,
    )
    character.db.whore_stats = stats.to_dict()
    
    return "You are a brothel worker. Time to earn your keep."


def _setup_hucow(character) -> str:
    """Hucow setup."""
    from .hucow import HucowStats
    
    character.db.is_captured = True
    character.db.current_resistance = 30
    
    stats = HucowStats(
        cow_id=character.dbref,
        cow_name=character.key,
        is_registered=True,
        is_lactating=True,
        production_rate_ml_hour=100,
    )
    character.db.hucow_stats = stats.to_dict()
    
    # Start with full breasts
    if hasattr(character, 'character_state'):
        state = character.character_state
        state.physical.breast_fullness = 80
        character.character_state = state
    
    return "You are a registered hucow. Your udders are heavy with milk."


def _setup_pony(character) -> str:
    """Pony setup."""
    from .pony import PonyStats, PonyType
    
    character.db.is_captured = True
    character.db.current_resistance = 35
    
    stats = PonyStats(
        pony_id=character.dbref,
        pony_name=character.key,
        pony_type=PonyType.RIDING,
        equipped_tack=["bridle", "bit", "harness"],
    )
    character.db.pony_stats = stats.to_dict()
    
    return "You are a pony in training. Your trainer awaits."


def _setup_corruption(character) -> str:
    """Corruption victim setup."""
    from .corruption import TransformationType, TransformationManager
    
    character.db.is_captured = True
    character.db.current_resistance = 40
    
    # Start multiple transformations
    mgr = TransformationManager(
        subject_dbref=character.dbref,
        subject_name=character.key,
    )
    
    # Random transformation type
    trans_type = random.choice([
        TransformationType.BIMBO,
        TransformationType.DEMON,
        TransformationType.SLUT,
    ])
    
    mgr.start_transformation(trans_type)
    mgr.add_corruption(trans_type, 30, "initial")  # Start at 30%
    
    character.db.transformations = mgr.to_dict()
    
    return f"You are undergoing {trans_type.value} transformation. You can feel it changing you..."


def _setup_fighter(character) -> str:
    """Arena fighter setup."""
    from .arena import CombatStats, CombatStyle
    
    character.db.is_captured = True
    character.db.current_resistance = 50
    
    stats = CombatStats(
        fighter_id=character.dbref,
        fighter_name=character.key,
        style=CombatStyle.DEFENSIVE,
    )
    character.db.combat_stats = stats.to_dict()
    
    return "You are a gladiator slave. Fight or face the consequences of defeat."


def _setup_breeding(character) -> str:
    """Breeding stock setup."""
    from .monsters import OvipositionRecord
    
    character.db.is_captured = True
    character.db.current_resistance = 20
    character.db.times_bred = 5
    
    # Already carrying eggs
    ovi = OvipositionRecord(
        host_dbref=character.dbref,
        host_name=character.key,
    )
    ovi.current_eggs = 8
    ovi.total_eggs_received = 20
    ovi.total_eggs_laid = 12
    ovi.belly_distension = 40
    
    character.db.oviposition = ovi.__dict__
    
    # Already inflated
    if hasattr(character, 'inflation'):
        tracker = character.inflation
        tracker.inflate("womb", "cum", 500)
        tracker.inflate("belly", "eggs", 400)
        character.db.inflation = tracker.to_dict()
    
    return "You are breeding stock. Your belly swells with eggs. More monsters approach..."


# =============================================================================
# QUICK START FUNCTIONS
# =============================================================================

def quick_start_game():
    """
    Quick start everything needed for gameplay.
    """
    from .game_loop import start_game_systems
    
    # Start game systems
    start_game_systems()
    
    # Create world
    world_result = create_starting_world()
    
    return (
        f"Game started!\n"
        f"Created {world_result['rooms']} rooms and {world_result['npcs']} NPCs.\n"
        f"Game systems are running."
    )


def setup_test_character(character):
    """
    Set up a character for testing all systems.
    Gives them a taste of everything.
    """
    from .integration import initialize_character
    
    # Initialize all systems
    initialize_character(character, role="free")
    
    # Give some stats to play with
    character.db.current_resistance = 60
    character.db.times_captured = 2
    
    # Some arousal
    if hasattr(character, 'character_state'):
        state = character.character_state
        state.sexual.arousal = 50
        character.character_state = state
    
    # Some inflation
    if hasattr(character, 'inflation'):
        tracker = character.inflation
        tracker.inflate("womb", "cum", 200)
        character.db.inflation = tracker.to_dict()
    
    # Start a transformation
    if hasattr(character, 'transformations'):
        from .corruption import TransformationType, TransformationManager
        mgr = TransformationManager(
            subject_dbref=character.dbref,
            subject_name=character.key,
        )
        mgr.start_transformation(TransformationType.SLUT)
        mgr.add_corruption(TransformationType.SLUT, 20, "testing")
        character.db.transformations = mgr.to_dict()
    
    return "Test character configured. Ready for... testing."


__all__ = [
    "create_starting_world",
    "create_danger_zone",
    "setup_player_scenario",
    "quick_start_game",
    "setup_test_character",
]
