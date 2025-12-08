"""
Traps & Hazards System for Gilderhaven
=======================================

Trap objects, cursed items, and hazardous environmental features.
Based on museum_events_consequences.md trap systems.

Trap Categories:
- Cursed Items: Artifacts that curse on pickup
- Defensive Flora: Plants that affect harvesters
- Defensive Fauna: Creatures that defend themselves
- Environmental Hazards: Room-based dangers
- Locked/Trapped Containers: Chests with traps

Usage:
    from world.traps import create_cursed_item, create_hazardous_plant
    
    # Create a cursed artifact
    create_cursed_item(location, "ancient idol", curse_effect="transformation",
                       curse_data={"species": "frog"})
    
    # Create hazardous plant
    create_hazardous_plant(location, "passion bloom", hazard_type="pollen")
"""

import random
from evennia import create_object
from evennia.utils import logger

# =============================================================================
# Trap Type Definitions
# =============================================================================

# Curse effects from museum doc
CURSE_EFFECTS = {
    "transformation_gradual": {
        "name": "Gradual Transformation",
        "description": "Slowly transforms the victim",
        "effect_key": "curse_transform_gradual",
        "category": "curse",
        "message": "|rYou feel your body beginning to change...|n",
        "stages": 5,
        "stage_interval": 300,  # 5 minutes between stages
    },
    "transformation_instant": {
        "name": "Instant Transformation",
        "description": "Immediately transforms the victim",
        "effect_key": "curse_transform_instant",
        "category": "curse",
        "message": "|rYour body twists and reshapes in an instant!|n",
    },
    "compulsion": {
        "name": "Compulsion",
        "description": "Forces the victim to perform actions",
        "effect_key": "curse_compulsion",
        "category": "curse",
        "message": "|rAn irresistible urge overtakes you...|n",
    },
    "attraction": {
        "name": "Creature Attraction",
        "description": "Draws creatures to the victim",
        "effect_key": "curse_attraction",
        "category": "curse",
        "message": "|rYou suddenly feel very... noticeable to nearby creatures.|n",
    },
    "heat_permanent": {
        "name": "Permanent Heat",
        "description": "Induces permanent heat until cured",
        "effect_key": "curse_heat",
        "category": "curse",
        "message": "|mA burning heat spreads through your body...|n",
    },
    "size_change": {
        "name": "Size Alteration",
        "description": "Changes the victim's size",
        "effect_key": "curse_size",
        "category": "curse",
        "message": "|rThe world around you seems to shift in scale...|n",
    },
    "gender_change": {
        "name": "Gender Swap",
        "description": "Swaps the victim's gender",
        "effect_key": "curse_gender",
        "category": "curse",
        "message": "|rA strange sensation washes through your body...|n",
    },
    "species_drift": {
        "name": "Species Drift",
        "description": "Slowly shifts species over time",
        "effect_key": "curse_species_drift",
        "category": "curse",
        "message": "|rYou feel... less like yourself.|n",
    },
}


# Defensive mechanisms for flora/fauna
DEFENSE_MECHANISMS = {
    "spray_pheromone": {
        "name": "Pheromone Spray",
        "description": "Marks with pheromones, attracting mates of the species",
        "effect_key": "pheromone_marked",
        "category": "debuff",
        "duration": 3600,  # 1 hour
        "message": "|yThe {source} sprays you with a musky substance!|n",
        "room_message": "|y{victim} gets sprayed by the {source}!|n",
    },
    "sting_venom": {
        "name": "Venomous Sting",
        "description": "Injects transformation catalyst venom",
        "effect_key": "transformation_venom",
        "category": "debuff",
        "duration": 1800,
        "message": "|rThe {source} stings you! Venom courses through your veins.|n",
        "room_message": "|r{victim} is stung by the {source}!|n",
    },
    "spores_parasitic": {
        "name": "Parasitic Spores",
        "description": "Infects with parasitic spores",
        "effect_key": "spore_infected",
        "category": "debuff",
        "duration": 7200,
        "message": "|rSpores from the {source} coat your skin, sinking in...|n",
    },
    "ink_blind": {
        "name": "Blinding Ink",
        "description": "Blinds and creates vulnerability",
        "effect_key": "blinded",
        "category": "debuff",
        "duration": 300,
        "message": "|xThe {source} sprays ink in your face! You can't see!|n",
    },
    "song_compel": {
        "name": "Compelling Song",
        "description": "Compels to follow and serve",
        "effect_key": "compelled",
        "category": "debuff",
        "duration": 600,
        "message": "|mA beautiful sound fills your mind... you must follow...|n",
    },
    "touch_bond": {
        "name": "Bonding Touch",
        "description": "Creates bond - can't be far from creature",
        "effect_key": "creature_bonded",
        "category": "curse",
        "duration": None,  # Until cured
        "message": "|mAs you touch the {source}, you feel an unbreakable connection form.|n",
    },
    "pollen_fertility": {
        "name": "Fertility Pollen",
        "description": "Causes fertility surge and heat",
        "effect_key": "pollen_heat",
        "category": "debuff",
        "duration": 3600,
        "message": "|mSweet pollen from the {source} fills your lungs... warmth spreads...|n",
    },
    "sap_adhesive": {
        "name": "Adhesive Sap",
        "description": "Stuck until freed",
        "effect_key": "stuck",
        "category": "debuff",
        "duration": 1800,
        "message": "|ySap from the {source} coats you! You're stuck!|n",
    },
    "thorns_aphrodisiac": {
        "name": "Aphrodisiac Thorns",
        "description": "Poison causes intense arousal",
        "effect_key": "aphrodisiac_poisoned",
        "category": "debuff",
        "duration": 1800,
        "message": "|mThe thorns prick you... a strange warmth floods your body.|n",
    },
    "scent_predator": {
        "name": "Predator-Attracting Scent",
        "description": "Draws predators to the victim",
        "effect_key": "predator_scent",
        "category": "debuff",
        "duration": 3600,
        "message": "|rA powerful scent clings to you... something is surely hunting you now.|n",
    },
    "nectar_addiction": {
        "name": "Addictive Nectar",
        "description": "Becomes addicted, compelled to return",
        "effect_key": "nectar_addicted",
        "category": "curse",
        "duration": None,
        "message": "|mThe nectar is... incredible. You |yneed|m more.|n",
    },
}


# Fishing hazards from museum doc
FISHING_HAZARDS = {
    "biting_fish": {
        "name": "Biting Fish",
        "chance": 0.05,
        "message": "|rSomething in the water bites you!|n",
        "effect_key": "wounded",
        "category": "debuff",
        "duration": 600,
    },
    "electric_eel": {
        "name": "Electric Eel",
        "chance": 0.03,
        "message": "|yYou catch an electric eel! It shocks you before escaping!|n",
        "effect_key": "shocked",
        "category": "debuff",
        "duration": 60,
    },
    "tentacle_grab": {
        "name": "Tentacle Grab",
        "chance": 0.02,
        "message": "|rA tentacle wraps around your arm and pulls you toward the water!|n",
        "effect_key": "grappled",
        "category": "debuff",
        "duration": 30,
    },
    "siren_song": {
        "name": "Siren Song",
        "chance": 0.01,
        "message": "|mYou hear beautiful singing from the water... you feel compelled to enter...|n",
        "effect_key": "charmed",
        "category": "debuff",
        "duration": 300,
    },
    "aphrodisiac_fish": {
        "name": "Aphrodisiac Fish",
        "chance": 0.05,
        "message": "|mYou catch a strange, glowing fish. Its touch sends warmth through you...|n",
        "effect_key": "aroused",
        "category": "debuff",
        "duration": 1800,
    },
}


# =============================================================================
# Trap Data Structures
# =============================================================================

def create_trap_data(trap_type, trigger="get", chance=1.0, effect_key=None,
                     duration=None, message=None, room_message=None,
                     one_time=True, data=None):
    """
    Create trap data to store on an object.
    
    Args:
        trap_type: Type of trap ("curse", "defense", "environmental")
        trigger: What triggers the trap ("get", "touch", "enter", "use")
        chance: Probability of triggering (0.0-1.0)
        effect_key: Effect to apply when triggered
        duration: How long the effect lasts
        message: Message to victim
        room_message: Message to room
        one_time: If True, trap can only trigger once
        data: Additional data for the effect
    
    Returns:
        dict: Trap data
    """
    return {
        "trap_type": trap_type,
        "trigger": trigger,
        "chance": chance,
        "effect_key": effect_key,
        "duration": duration,
        "message": message,
        "room_message": room_message,
        "one_time": one_time,
        "triggered": False,
        "data": data or {},
    }


# =============================================================================
# Trap Checking & Triggering
# =============================================================================

def check_trap(obj, character, trigger_type):
    """
    Check if an object's trap should trigger.
    
    Args:
        obj: Object with potential trap
        character: Character triggering
        trigger_type: Type of trigger ("get", "touch", etc.)
    
    Returns:
        bool: True if trap triggered
    """
    trap_data = obj.db.trap
    if not trap_data:
        return False
    
    # Check trigger type matches
    if trap_data.get("trigger") != trigger_type:
        return False
    
    # Check if already triggered (one-time)
    if trap_data.get("one_time") and trap_data.get("triggered"):
        return False
    
    # Check chance
    chance = trap_data.get("chance", 1.0)
    if random.random() > chance:
        return False
    
    # Trigger the trap!
    return trigger_trap(obj, character, trap_data)


def trigger_trap(obj, character, trap_data):
    """
    Trigger a trap on a character.
    
    Args:
        obj: Trap object
        character: Victim
        trap_data: Trap configuration
    
    Returns:
        bool: True if effect applied
    """
    from world.effects import apply_effect
    
    # Mark as triggered
    trap_data["triggered"] = True
    obj.db.trap = trap_data
    
    # Send messages
    message = trap_data.get("message")
    if message:
        formatted = message.format(source=obj.key, victim=character.key)
        character.msg(formatted)
    
    room_message = trap_data.get("room_message")
    if room_message and character.location:
        formatted = room_message.format(source=obj.key, victim=character.key)
        character.location.msg_contents(formatted, exclude=[character])
    
    # Apply effect
    effect_key = trap_data.get("effect_key")
    if effect_key:
        return apply_effect(
            character,
            effect_key,
            category=trap_data.get("category", "debuff"),
            duration=trap_data.get("duration"),
            data=trap_data.get("data")
        )
    
    return True


# =============================================================================
# Object Creation Helpers
# =============================================================================

def create_cursed_item(location, key, curse_type, description=None,
                      trigger="get", chance=1.0, **curse_data):
    """
    Create a cursed item that applies a curse when picked up.
    
    Args:
        location: Where to create the item
        key: Item name
        curse_type: Key from CURSE_EFFECTS
        description: Item description
        trigger: What triggers curse (usually "get")
        chance: Probability of curse triggering
        **curse_data: Additional data for the curse
    
    Returns:
        Object: The cursed item
    """
    curse = CURSE_EFFECTS.get(curse_type, CURSE_EFFECTS["transformation_gradual"])
    
    obj = create_object(
        "typeclasses.objects.Object",
        key=key,
        location=location
    )
    
    if description:
        obj.db.desc = description
    else:
        obj.db.desc = f"A seemingly ordinary {key}. Something feels... off about it."
    
    # Set up trap data
    obj.db.trap = create_trap_data(
        trap_type="curse",
        trigger=trigger,
        chance=chance,
        effect_key=curse["effect_key"],
        duration=curse.get("duration"),
        message=curse.get("message"),
        one_time=True,
        data=curse_data
    )
    
    # Tag it
    obj.tags.add("cursed", category="item_type")
    obj.tags.add("trap", category="item_type")
    
    return obj


def create_hazardous_plant(location, key, hazard_type, description=None,
                          chance=0.3, **hazard_data):
    """
    Create a plant that can affect harvesters.
    
    Args:
        location: Where to create the plant
        key: Plant name
        hazard_type: Key from DEFENSE_MECHANISMS
        description: Plant description
        chance: Probability of hazard triggering on harvest
        **hazard_data: Additional data
    
    Returns:
        Object: The hazardous plant
    """
    hazard = DEFENSE_MECHANISMS.get(hazard_type)
    if not hazard:
        hazard = DEFENSE_MECHANISMS["pollen_fertility"]
    
    obj = create_object(
        "typeclasses.objects.Object",
        key=key,
        location=location
    )
    
    if description:
        obj.db.desc = description
    else:
        obj.db.desc = f"A {key}. Beautiful, but it might be dangerous to touch."
    
    obj.db.trap = create_trap_data(
        trap_type="flora_defense",
        trigger="get",
        chance=chance,
        effect_key=hazard["effect_key"],
        category=hazard.get("category", "debuff"),
        duration=hazard.get("duration"),
        message=hazard.get("message"),
        room_message=hazard.get("room_message"),
        one_time=False,  # Can trigger repeatedly
        data=hazard_data
    )
    
    obj.tags.add("hazardous_plant", category="item_type")
    obj.tags.add("trap", category="item_type")
    
    return obj


def create_defensive_creature(location, key, defense_type, description=None,
                             chance=0.5, **defense_data):
    """
    Create a creature that defends itself when caught/touched.
    
    Args:
        location: Where to create the creature
        key: Creature name
        defense_type: Key from DEFENSE_MECHANISMS
        description: Creature description
        chance: Probability of defense triggering
        **defense_data: Additional data
    
    Returns:
        Object: The defensive creature
    """
    defense = DEFENSE_MECHANISMS.get(defense_type)
    if not defense:
        defense = DEFENSE_MECHANISMS["spray_pheromone"]
    
    obj = create_object(
        "typeclasses.objects.Object",
        key=key,
        location=location
    )
    
    if description:
        obj.db.desc = description
    else:
        obj.db.desc = f"A {key}. It eyes you warily."
    
    obj.db.trap = create_trap_data(
        trap_type="fauna_defense",
        trigger="get",
        chance=chance,
        effect_key=defense["effect_key"],
        category=defense.get("category", "debuff"),
        duration=defense.get("duration"),
        message=defense.get("message"),
        room_message=defense.get("room_message"),
        one_time=True,  # Once caught, defense spent
        data=defense_data
    )
    
    obj.tags.add("creature", category="item_type")
    obj.tags.add("defensive", category="item_type")
    obj.tags.add("trap", category="item_type")
    
    return obj


def create_trapped_container(location, key, trap_effect, description=None,
                            loot=None, chance=1.0, **trap_data):
    """
    Create a container with a trap that triggers on opening.
    
    Args:
        location: Where to create the container
        key: Container name
        trap_effect: Effect to apply (from DEFENSE_MECHANISMS or custom)
        description: Container description
        loot: List of item keys to spawn inside when opened
        chance: Probability of trap triggering
        **trap_data: Additional trap configuration
    
    Returns:
        Object: The trapped container
    """
    obj = create_object(
        "typeclasses.objects.Container",  # STUB: Use Container typeclass
        key=key,
        location=location
    )
    
    if description:
        obj.db.desc = description
    else:
        obj.db.desc = f"A {key}. Might contain treasure... or danger."
    
    # Get effect data if it's a known type
    if trap_effect in DEFENSE_MECHANISMS:
        effect_data = DEFENSE_MECHANISMS[trap_effect]
        effect_key = effect_data["effect_key"]
        duration = effect_data.get("duration")
        message = effect_data.get("message", "|rThe trap triggers!|n")
    else:
        effect_key = trap_effect
        duration = trap_data.get("duration")
        message = trap_data.get("message", "|rA trap!|n")
    
    obj.db.trap = create_trap_data(
        trap_type="container_trap",
        trigger="open",
        chance=chance,
        effect_key=effect_key,
        duration=duration,
        message=message,
        one_time=True,
        data=trap_data
    )
    
    obj.db.loot = loot or []
    
    obj.tags.add("container", category="item_type")
    obj.tags.add("trapped", category="item_type")
    obj.tags.add("trap", category="item_type")
    
    return obj


# =============================================================================
# Environmental Hazard Rooms
# =============================================================================

def setup_hazard_room(room, hazard_type, chance=0.2, **hazard_data):
    """
    Set up a room as environmentally hazardous.
    
    Args:
        room: Room to make hazardous
        hazard_type: Type of environmental hazard
        chance: Probability of triggering per entry
        **hazard_data: Additional hazard configuration
    """
    hazard = DEFENSE_MECHANISMS.get(hazard_type, {})
    
    room.db.environmental_hazard = {
        "type": hazard_type,
        "chance": chance,
        "effect_key": hazard.get("effect_key", hazard_type),
        "category": hazard.get("category", "environmental"),
        "duration": hazard.get("duration"),
        "message": hazard.get("message", "|rYou're affected by the environment!|n"),
        **hazard_data
    }
    
    room.tags.add("hazardous", category="room_type")


def check_room_hazard(room, character):
    """
    Check and apply room environmental hazard.
    Called from room's at_object_receive.
    
    Args:
        room: Hazardous room
        character: Character entering
    
    Returns:
        bool: True if hazard triggered
    """
    hazard = room.db.environmental_hazard
    if not hazard:
        return False
    
    # Check chance
    if random.random() > hazard.get("chance", 0.2):
        return False
    
    from world.effects import apply_effect
    
    # Apply effect
    message = hazard.get("message", "|rThe environment affects you!|n")
    character.msg(message.format(source="the environment", victim=character.key))
    
    return apply_effect(
        character,
        hazard.get("effect_key"),
        category=hazard.get("category", "environmental"),
        duration=hazard.get("duration"),
        data=hazard.get("data", {})
    )


# =============================================================================
# Curse Removal
# =============================================================================

def get_curse_cure(effect_key):
    """
    Get information about how to cure a curse.
    
    Args:
        effect_key: The curse effect key
    
    Returns:
        dict: Cure information
    """
    # STUB: This would be expanded with actual cure mechanics
    CURE_METHODS = {
        "curse_transform_gradual": {
            "method": "curator",
            "description": "The Curator can remove this... for a price.",
            "cost": 100,
            "alternative": "Wait for it to wear off (if it does).",
        },
        "curse_transform_instant": {
            "method": "wardrobe",
            "description": "The Wardrobe system can restore your original form.",
            "cost": 0,
        },
        "curse_heat": {
            "method": "satisfy",
            "description": "The curse can be... satisfied. Or the Curator might help.",
            "alternative": "Certain rare herbs can suppress it temporarily.",
        },
        "nectar_addicted": {
            "method": "willpower",
            "description": "Stay away from the source long enough and it fades.",
            "duration": 86400,  # 24 hours
        },
    }
    
    return CURE_METHODS.get(effect_key, {
        "method": "curator",
        "description": "The Curator might be able to help.",
    })


def attempt_curse_removal(character, effect_key, method=None):
    """
    Attempt to remove a curse.
    
    Args:
        character: Cursed character
        effect_key: Curse to remove
        method: Method being used
    
    Returns:
        tuple: (bool success, str message)
    """
    from world.effects import has_effect, remove_effect
    
    if not has_effect(character, effect_key):
        return False, "You don't have that curse."
    
    cure_info = get_curse_cure(effect_key)
    required_method = cure_info.get("method")
    
    # STUB: Implement actual cure mechanics
    # For now, just remove if method matches
    if method == required_method or method == "admin":
        remove_effect(character, effect_key)
        return True, "|gThe curse lifts!|n"
    
    return False, f"This curse requires: {cure_info.get('description', 'unknown cure')}"


# =============================================================================
# Hook Integration
# =============================================================================

"""
To integrate traps with objects, add to typeclasses/objects.py:

class Object(DefaultObject):
    def at_get(self, getter, **kwargs):
        super().at_get(getter, **kwargs)
        from world.traps import check_trap
        check_trap(self, getter, "get")
    
    def at_pre_get(self, getter, **kwargs):
        # Optional: prevent pickup entirely
        return True

And to rooms for environmental hazards:

class Room(DefaultRoom):
    def at_object_receive(self, obj, source_location, **kwargs):
        super().at_object_receive(obj, source_location, **kwargs)
        if obj.has_account:  # Is a player
            from world.traps import check_room_hazard
            check_room_hazard(self, obj)
"""
