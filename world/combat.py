"""
Combat and Encounter System for Gilderhaven

A capture/defeat focused combat system with three resource pools,
stat-based resolution, equipment integration, and context-sensitive
defeat outcomes.

NO DEATH - only capture, defeat, exhaustion, or submission.
"""

from random import randint, random, choice
from evennia.utils import delay

# =============================================================================
# PRIMARY ATTRIBUTES
# =============================================================================
# These are the base stats that define a character's combat capabilities.
# Players allocate points at creation and can train them slowly over time.

PRIMARY_ATTRIBUTES = {
    "strength": {
        "name": "Strength",
        "abbrev": "STR",
        "desc": "Physical power. Affects melee damage and grapple strength.",
        "default": 10,
        "min": 1,
        "max": 30,
    },
    "agility": {
        "name": "Agility",
        "abbrev": "AGI",
        "desc": "Speed and reflexes. Affects dodge, flee chance, and initiative.",
        "default": 10,
        "min": 1,
        "max": 30,
    },
    "endurance": {
        "name": "Endurance",
        "abbrev": "END",
        "desc": "Physical resilience. Affects HP and stamina pools.",
        "default": 10,
        "min": 1,
        "max": 30,
    },
    "willpower": {
        "name": "Willpower",
        "abbrev": "WIL",
        "desc": "Mental fortitude. Affects composure and resist effects.",
        "default": 10,
        "min": 1,
        "max": 30,
    },
    "charisma": {
        "name": "Charisma",
        "abbrev": "CHA",
        "desc": "Force of personality. Affects intimidate, seduce, befriend.",
        "default": 10,
        "min": 1,
        "max": 30,
    },
}

# Starting attribute points to distribute (above defaults)
STARTING_ATTRIBUTE_POINTS = 15

# =============================================================================
# RESOURCE POOLS
# =============================================================================
# The three "health bars" that determine combat state

RESOURCE_POOLS = {
    "hp": {
        "name": "Health",
        "abbrev": "HP",
        "desc": "Physical health. At zero, you're knocked out.",
        "color": "|r",
        "base": 50,
        "per_endurance": 5,  # +5 HP per END point
        "per_strength": 2,   # +2 HP per STR point
        "regen_per_tick": 1,  # Out of combat
        "zero_state": "unconscious",
    },
    "stamina": {
        "name": "Stamina",
        "abbrev": "STA",
        "desc": "Energy reserve. At zero, you're exhausted and can't escape.",
        "color": "|y",
        "base": 30,
        "per_endurance": 3,
        "per_agility": 2,
        "regen_per_tick": 2,
        "zero_state": "exhausted",
    },
    "composure": {
        "name": "Composure",
        "abbrev": "CMP",
        "desc": "Mental/arousal resistance. At zero, you're overwhelmed.",
        "color": "|m",
        "base": 40,
        "per_willpower": 4,
        "per_charisma": 1,
        "regen_per_tick": 3,
        "zero_state": "overwhelmed",
    },
}


# =============================================================================
# COMBAT SKILLS
# =============================================================================
# Skills improve with use. Higher skill = better rolls.

COMBAT_SKILLS = {
    "melee": {
        "name": "Melee Combat",
        "desc": "Fighting with weapons or fists.",
        "governs": ["attack_accuracy", "melee_damage"],
        "trained_by": ["attacking", "sparring"],
    },
    "defense": {
        "name": "Defense",
        "desc": "Blocking and parrying attacks.",
        "governs": ["block_chance", "damage_reduction"],
        "trained_by": ["blocking", "being_attacked"],
    },
    "evasion": {
        "name": "Evasion",
        "desc": "Dodging attacks entirely.",
        "governs": ["dodge_chance", "flee_success"],
        "trained_by": ["dodging", "fleeing"],
    },
    "grappling": {
        "name": "Grappling",
        "desc": "Wrestling, pinning, and escaping holds.",
        "governs": ["grapple_attack", "escape_chance"],
        "trained_by": ["grappling", "escaping"],
    },
    "resistance": {
        "name": "Mental Resistance",
        "desc": "Resisting mental and arousal effects.",
        "governs": ["composure_defense", "effect_resist"],
        "trained_by": ["resisting_effects"],
    },
    "intimidation": {
        "name": "Intimidation",
        "desc": "Scaring off opponents.",
        "governs": ["intimidate_success"],
        "trained_by": ["intimidating"],
    },
    "seduction": {
        "name": "Seduction",
        "desc": "Turning the tables with charm.",
        "governs": ["seduce_success", "composure_damage"],
        "trained_by": ["seducing"],
    },
}

# Skill caps and progression
MAX_SKILL = 100
SKILL_EXP_PER_LEVEL = 100
SKILL_GAIN_CHANCE = 0.3  # 30% chance to gain skill exp per use


# =============================================================================
# COMBAT ACTIONS
# =============================================================================

COMBAT_ACTIONS = {
    # === Offensive ===
    "attack": {
        "name": "Attack",
        "desc": "Strike your opponent with your weapon or fists.",
        "type": "offensive",
        "stamina_cost": 5,
        "skill": "melee",
        "targets": "enemy",
        "damage_type": "physical",
    },
    "power_attack": {
        "name": "Power Attack",
        "desc": "A heavy strike. More damage, less accuracy.",
        "type": "offensive",
        "stamina_cost": 12,
        "skill": "melee",
        "targets": "enemy",
        "damage_type": "physical",
        "damage_mult": 1.5,
        "accuracy_mod": -15,
    },
    "grapple": {
        "name": "Grapple",
        "desc": "Attempt to grab and restrain your opponent.",
        "type": "offensive",
        "stamina_cost": 10,
        "skill": "grappling",
        "targets": "enemy",
        "damage_type": "stamina",
        "on_success": "grappled",
    },
    "tease": {
        "name": "Tease",
        "desc": "Attempt to fluster your opponent.",
        "type": "offensive",
        "stamina_cost": 3,
        "skill": "seduction",
        "targets": "enemy",
        "damage_type": "composure",
    },
    
    # === Defensive ===
    "defend": {
        "name": "Defend",
        "desc": "Focus on blocking incoming attacks.",
        "type": "defensive",
        "stamina_cost": 3,
        "skill": "defense",
        "effect": "defending",
        "defense_bonus": 30,
    },
    "dodge": {
        "name": "Dodge",
        "desc": "Focus on evading attacks entirely.",
        "type": "defensive",
        "stamina_cost": 5,
        "skill": "evasion",
        "effect": "dodging",
        "evasion_bonus": 25,
    },
    
    # === Utility ===
    "flee": {
        "name": "Flee",
        "desc": "Attempt to escape the encounter.",
        "type": "utility",
        "stamina_cost": 15,
        "skill": "evasion",
        "contested_by": "grappling",  # If grappled
    },
    "struggle": {
        "name": "Struggle",
        "desc": "Try to break free from a grapple.",
        "type": "utility",
        "stamina_cost": 8,
        "skill": "grappling",
        "removes": "grappled",
    },
    "intimidate": {
        "name": "Intimidate",
        "desc": "Try to scare off your opponent.",
        "type": "utility",
        "stamina_cost": 5,
        "skill": "intimidation",
        "contested_by": "resistance",
        "on_success": "fled",  # Enemy flees
    },
    "seduce": {
        "name": "Seduce",
        "desc": "Try to charm your way out... or in.",
        "type": "utility",
        "stamina_cost": 5,
        "skill": "seduction",
        "contested_by": "resistance",
        "damage_type": "composure",
    },
    "befriend": {
        "name": "Befriend",
        "desc": "Attempt to calm a creature and make peace.",
        "type": "utility",
        "stamina_cost": 0,
        "skill": "charisma",  # Uses raw charisma
        "requires": ["creature_befriendable"],
        "on_success": "peaceful",
    },
    "use": {
        "name": "Use Item",
        "desc": "Use an item from your inventory.",
        "type": "utility",
        "stamina_cost": 0,
        "requires_item": True,
    },
    "submit": {
        "name": "Submit",
        "desc": "Surrender to your opponent.",
        "type": "utility",
        "stamina_cost": 0,
        "ends_combat": True,
        "outcome": "defeat",
    },
}


# =============================================================================
# DAMAGE TYPES
# =============================================================================

DAMAGE_TYPES = {
    "physical": {
        "name": "Physical",
        "targets": "hp",
        "resisted_by": "armor",
        "blocked_by": "defense",
    },
    "stamina": {
        "name": "Exhausting",
        "targets": "stamina",
        "resisted_by": "endurance",
        "blocked_by": "grappling",
    },
    "composure": {
        "name": "Mental",
        "targets": "composure",
        "resisted_by": "willpower",
        "blocked_by": "resistance",
    },
    "aphrodisiac": {
        "name": "Aphrodisiac",
        "targets": "composure",
        "resisted_by": "willpower",
        "blocked_by": "resistance",
        "ignores_armor": True,
    },
    "poison": {
        "name": "Poison",
        "targets": "hp",
        "resisted_by": "endurance",
        "over_time": True,
    },
}


# =============================================================================
# COMBAT STATES
# =============================================================================

COMBAT_STATES = {
    "normal": {
        "name": "Normal",
        "desc": "No special conditions.",
    },
    "defending": {
        "name": "Defending",
        "desc": "Focused on blocking. +30 defense, -10 attack.",
        "defense_mod": 30,
        "attack_mod": -10,
        "duration": 1,  # Lasts until next action
    },
    "dodging": {
        "name": "Dodging",
        "desc": "Focused on evasion. +25 evasion, can't attack.",
        "evasion_mod": 25,
        "can_attack": False,
        "duration": 1,
    },
    "grappled": {
        "name": "Grappled",
        "desc": "Restrained by opponent. Can't flee, -20 to actions.",
        "can_flee": False,
        "action_mod": -20,
        "escape_action": "struggle",
    },
    "grappling": {
        "name": "Grappling",
        "desc": "Holding an opponent. Limited actions, +20 to grapple attacks.",
        "grapple_mod": 20,
        "limited_actions": ["grapple", "tease", "release"],
    },
    "stunned": {
        "name": "Stunned",
        "desc": "Dazed and unable to act.",
        "can_act": False,
        "duration": 1,
    },
    "aroused": {
        "name": "Aroused",
        "desc": "Distracted by arousal. -10 to resistance.",
        "resistance_mod": -10,
        "duration": 3,
        "stacks": True,  # Can stack for more penalty
    },
    "exhausted": {
        "name": "Exhausted",
        "desc": "Stamina depleted. Cannot flee or struggle effectively.",
        "flee_mod": -50,
        "struggle_mod": -30,
    },
    "unconscious": {
        "name": "Unconscious",
        "desc": "Knocked out. Combat ends in defeat.",
        "ends_combat": True,
        "outcome": "defeat_hp",
    },
    "overwhelmed": {
        "name": "Overwhelmed",
        "desc": "Composure broken. Combat ends in defeat.",
        "ends_combat": True,
        "outcome": "defeat_composure",
    },
}


# =============================================================================
# EQUIPMENT SLOTS
# =============================================================================

EQUIPMENT_SLOTS = {
    "main_hand": {
        "name": "Main Hand",
        "desc": "Primary weapon.",
        "affects": ["damage", "accuracy"],
    },
    "off_hand": {
        "name": "Off Hand",
        "desc": "Shield or secondary weapon.",
        "affects": ["defense", "damage"],
    },
    "body": {
        "name": "Body Armor",
        "desc": "Chest and torso protection.",
        "affects": ["armor", "evasion_penalty"],
    },
    "head": {
        "name": "Head",
        "desc": "Helmet or hat.",
        "affects": ["armor", "perception"],
    },
    "hands": {
        "name": "Hands",
        "desc": "Gloves or gauntlets.",
        "affects": ["armor", "grapple"],
    },
    "feet": {
        "name": "Feet",
        "desc": "Boots or shoes.",
        "affects": ["armor", "evasion"],
    },
    "accessory": {
        "name": "Accessory",
        "desc": "Ring, amulet, or charm.",
        "affects": ["special"],
    },
}


# =============================================================================
# WEAPON TYPES
# =============================================================================

WEAPON_TYPES = {
    "unarmed": {
        "name": "Unarmed",
        "damage_range": (2, 6),
        "damage_type": "physical",
        "speed": 1.2,  # Faster
        "accuracy_mod": 10,
        "skill": "melee",
    },
    "dagger": {
        "name": "Dagger",
        "damage_range": (4, 10),
        "damage_type": "physical",
        "speed": 1.1,
        "accuracy_mod": 5,
        "skill": "melee",
        "special": "can_flee_attack",  # Attack while fleeing
    },
    "sword": {
        "name": "Sword",
        "damage_range": (8, 16),
        "damage_type": "physical",
        "speed": 1.0,
        "accuracy_mod": 0,
        "skill": "melee",
    },
    "club": {
        "name": "Club",
        "damage_range": (6, 14),
        "damage_type": "physical",
        "speed": 0.9,
        "accuracy_mod": -5,
        "skill": "melee",
        "special": "stun_chance",  # Chance to stun
    },
    "whip": {
        "name": "Whip",
        "damage_range": (3, 8),
        "damage_type": "physical",
        "speed": 1.0,
        "accuracy_mod": 0,
        "skill": "melee",
        "special": "grapple_bonus",  # +10 to grapple
        "composure_damage": (2, 5),  # Also does composure damage
    },
    "paddle": {
        "name": "Paddle",
        "damage_range": (2, 6),
        "damage_type": "physical",
        "speed": 1.0,
        "accuracy_mod": 5,
        "skill": "melee",
        "composure_damage": (4, 8),  # Primarily composure
    },
    "staff": {
        "name": "Staff",
        "damage_range": (5, 12),
        "damage_type": "physical",
        "speed": 0.95,
        "accuracy_mod": 0,
        "skill": "melee",
        "defense_bonus": 10,
    },
}


# =============================================================================
# VICTORY/DEFEAT CONDITIONS
# =============================================================================

VICTORY_CONDITIONS = {
    "hp_zero": {
        "name": "Knockout",
        "desc": "Opponent's HP reduced to zero.",
        "check": "hp",
        "winner_gets": "loot",
    },
    "stamina_zero": {
        "name": "Exhaustion",
        "desc": "Opponent's stamina depleted.",
        "check": "stamina",
        "winner_gets": "capture",
    },
    "composure_zero": {
        "name": "Overwhelm",
        "desc": "Opponent's composure broken.",
        "check": "composure",
        "winner_gets": "scene",  # Consent-gated
    },
    "fled": {
        "name": "Escape",
        "desc": "Opponent successfully fled.",
        "result": "draw",
    },
    "submit": {
        "name": "Submission",
        "desc": "Opponent surrendered.",
        "winner_gets": "choice",
    },
    "peaceful": {
        "name": "Peace",
        "desc": "Combat ended peacefully.",
        "result": "draw",
        "reputation_gain": True,
    },
    "intimidated": {
        "name": "Scared Off",
        "desc": "Opponent fled in fear.",
        "winner_gets": "none",
    },
}


# =============================================================================
# Helper Functions - Attributes & Resources
# =============================================================================

def get_attribute(character, attr_key):
    """Get a character's attribute value."""
    if not character.db.attributes:
        character.db.attributes = {}
    default = PRIMARY_ATTRIBUTES.get(attr_key, {}).get("default", 10)
    return character.db.attributes.get(attr_key, default)


def set_attribute(character, attr_key, value):
    """Set a character's attribute value."""
    if not character.db.attributes:
        character.db.attributes = {}
    attr_data = PRIMARY_ATTRIBUTES.get(attr_key)
    if attr_data:
        value = max(attr_data["min"], min(attr_data["max"], value))
    character.db.attributes[attr_key] = value


def get_max_resource(character, resource_key):
    """Calculate maximum value for a resource pool."""
    pool = RESOURCE_POOLS.get(resource_key)
    if not pool:
        return 100
    
    max_val = pool.get("base", 50)
    
    # Add attribute bonuses
    for attr, mult in pool.items():
        if attr.startswith("per_"):
            attr_key = attr[4:]  # Remove "per_"
            if attr_key in PRIMARY_ATTRIBUTES:
                attr_val = get_attribute(character, attr_key)
                max_val += attr_val * mult
    
    # Equipment bonuses could go here
    
    return max_val


def get_resource(character, resource_key):
    """Get current value of a resource."""
    if not character.db.resources:
        character.db.resources = {}
    
    max_val = get_max_resource(character, resource_key)
    current = character.db.resources.get(resource_key, max_val)
    return min(current, max_val)


def set_resource(character, resource_key, value):
    """Set current value of a resource."""
    if not character.db.resources:
        character.db.resources = {}
    
    max_val = get_max_resource(character, resource_key)
    value = max(0, min(max_val, value))
    character.db.resources[resource_key] = value
    return value


def modify_resource(character, resource_key, amount):
    """
    Modify a resource by amount (positive or negative).
    Returns the new value.
    """
    current = get_resource(character, resource_key)
    return set_resource(character, resource_key, current + amount)


def restore_all_resources(character):
    """Restore all resources to maximum."""
    for resource_key in RESOURCE_POOLS:
        max_val = get_max_resource(character, resource_key)
        set_resource(character, resource_key, max_val)


def get_resource_display(character, resource_key, bar_length=10):
    """Get a visual bar display for a resource."""
    pool = RESOURCE_POOLS.get(resource_key, {})
    current = get_resource(character, resource_key)
    max_val = get_max_resource(character, resource_key)
    
    filled = int((current / max_val) * bar_length) if max_val > 0 else 0
    empty = bar_length - filled
    
    color = pool.get("color", "|w")
    bar = f"{color}{'█' * filled}|n{'░' * empty}"
    
    name = pool.get("abbrev", resource_key.upper())
    return f"{name}: {bar} {current}/{max_val}"


def get_all_resources_display(character):
    """Get display for all three resource pools."""
    lines = []
    for resource_key in ["hp", "stamina", "composure"]:
        lines.append(get_resource_display(character, resource_key))
    return "\n".join(lines)


# =============================================================================
# Helper Functions - Combat Skills
# =============================================================================

def get_combat_skill(character, skill_key):
    """Get a combat skill level (0-100)."""
    if not character.db.combat_skills:
        character.db.combat_skills = {}
    return character.db.combat_skills.get(skill_key, 0)


def get_combat_skill_exp(character, skill_key):
    """Get current exp toward next skill level."""
    if not character.db.combat_skill_exp:
        character.db.combat_skill_exp = {}
    return character.db.combat_skill_exp.get(skill_key, 0)


def add_combat_skill_exp(character, skill_key, amount=1):
    """
    Add experience to a combat skill.
    Returns (new_level, leveled_up).
    """
    if not character.db.combat_skills:
        character.db.combat_skills = {}
    if not character.db.combat_skill_exp:
        character.db.combat_skill_exp = {}
    
    current_level = character.db.combat_skills.get(skill_key, 0)
    if current_level >= MAX_SKILL:
        return current_level, False
    
    current_exp = character.db.combat_skill_exp.get(skill_key, 0)
    new_exp = current_exp + amount
    
    leveled_up = False
    while new_exp >= SKILL_EXP_PER_LEVEL and current_level < MAX_SKILL:
        new_exp -= SKILL_EXP_PER_LEVEL
        current_level += 1
        leveled_up = True
    
    character.db.combat_skills[skill_key] = current_level
    character.db.combat_skill_exp[skill_key] = new_exp
    
    return current_level, leveled_up


def maybe_train_skill(character, skill_key, difficulty=1):
    """
    Chance-based skill training from use.
    Higher difficulty = more exp.
    """
    if random() < SKILL_GAIN_CHANCE:
        exp_gain = max(1, difficulty)
        return add_combat_skill_exp(character, skill_key, exp_gain)
    return get_combat_skill(character, skill_key), False


# =============================================================================
# Helper Functions - Combat Calculations
# =============================================================================

def calculate_initiative(character):
    """Calculate initiative for turn order."""
    agility = get_attribute(character, "agility")
    # Base initiative from agility + random factor
    return agility + randint(1, 20)


def calculate_accuracy(attacker, action, weapon=None):
    """Calculate hit chance for an attack."""
    base_accuracy = 50
    
    # Skill bonus
    skill_key = action.get("skill", "melee")
    skill_level = get_combat_skill(attacker, skill_key)
    skill_bonus = skill_level // 2  # +1 accuracy per 2 skill
    
    # Agility bonus
    agility = get_attribute(attacker, "agility")
    agi_bonus = (agility - 10) * 2  # +2 per point above 10
    
    # Weapon modifier
    weapon_mod = 0
    if weapon:
        weapon_type = weapon.db.weapon_type or "unarmed"
        weapon_data = WEAPON_TYPES.get(weapon_type, {})
        weapon_mod = weapon_data.get("accuracy_mod", 0)
    
    # Action modifier
    action_mod = action.get("accuracy_mod", 0)
    
    return base_accuracy + skill_bonus + agi_bonus + weapon_mod + action_mod


def calculate_evasion(defender, state=None):
    """Calculate chance to dodge an attack."""
    base_evasion = 10
    
    # Skill bonus
    skill_level = get_combat_skill(defender, "evasion")
    skill_bonus = skill_level // 3
    
    # Agility bonus
    agility = get_attribute(defender, "agility")
    agi_bonus = (agility - 10) * 2
    
    # State bonus (dodging stance)
    state_bonus = 0
    if state:
        state_data = COMBAT_STATES.get(state, {})
        state_bonus = state_data.get("evasion_mod", 0)
    
    # Armor penalty would go here
    
    return base_evasion + skill_bonus + agi_bonus + state_bonus


def calculate_defense(defender, state=None):
    """Calculate damage reduction from blocking."""
    base_defense = 5
    
    # Skill bonus
    skill_level = get_combat_skill(defender, "defense")
    skill_bonus = skill_level // 4
    
    # Strength bonus (for blocking force)
    strength = get_attribute(defender, "strength")
    str_bonus = (strength - 10)
    
    # State bonus (defending stance)
    state_bonus = 0
    if state:
        state_data = COMBAT_STATES.get(state, {})
        state_bonus = state_data.get("defense_mod", 0)
    
    return base_defense + skill_bonus + str_bonus + state_bonus


def calculate_damage(attacker, action, weapon=None):
    """Calculate damage dealt by an attack."""
    # Base damage from weapon
    if weapon:
        weapon_type = weapon.db.weapon_type or "unarmed"
        weapon_data = WEAPON_TYPES.get(weapon_type, WEAPON_TYPES["unarmed"])
    else:
        weapon_data = WEAPON_TYPES["unarmed"]
    
    min_dmg, max_dmg = weapon_data.get("damage_range", (2, 6))
    base_damage = randint(min_dmg, max_dmg)
    
    # Strength bonus for physical
    damage_type = action.get("damage_type", "physical")
    if damage_type == "physical":
        strength = get_attribute(attacker, "strength")
        str_bonus = (strength - 10) // 2
        base_damage += str_bonus
    
    # Skill bonus
    skill_key = action.get("skill", "melee")
    skill_level = get_combat_skill(attacker, skill_key)
    skill_bonus = skill_level // 10  # +1 damage per 10 skill
    base_damage += skill_bonus
    
    # Action multiplier
    damage_mult = action.get("damage_mult", 1.0)
    base_damage = int(base_damage * damage_mult)
    
    return max(1, base_damage)


def calculate_composure_damage(attacker, action, weapon=None):
    """Calculate composure damage (for tease/seduce attacks)."""
    # Weapon composure damage
    weapon_composure = (0, 0)
    if weapon:
        weapon_type = weapon.db.weapon_type or "unarmed"
        weapon_data = WEAPON_TYPES.get(weapon_type, {})
        weapon_composure = weapon_data.get("composure_damage", (0, 0))
    
    if weapon_composure[1] > 0:
        base_damage = randint(weapon_composure[0], weapon_composure[1])
    else:
        base_damage = randint(3, 8)  # Default composure damage
    
    # Charisma bonus
    charisma = get_attribute(attacker, "charisma")
    cha_bonus = (charisma - 10)
    
    # Seduction skill bonus
    skill_level = get_combat_skill(attacker, "seduction")
    skill_bonus = skill_level // 5
    
    return max(1, base_damage + cha_bonus + skill_bonus)


def roll_contest(attacker, defender, attack_skill, defend_skill):
    """
    Roll a contested check between two characters.
    Returns (winner, margin) where winner is 'attacker' or 'defender'.
    """
    # Attacker roll
    attack_skill_val = get_combat_skill(attacker, attack_skill)
    attack_attr = get_attribute(attacker, "strength")  # Default to strength
    if attack_skill in ["seduction", "intimidation"]:
        attack_attr = get_attribute(attacker, "charisma")
    attack_roll = randint(1, 20) + (attack_skill_val // 5) + (attack_attr // 2)
    
    # Defender roll
    defend_skill_val = get_combat_skill(defender, defend_skill)
    defend_attr = get_attribute(defender, "willpower")
    if defend_skill == "grappling":
        defend_attr = get_attribute(defender, "strength")
    elif defend_skill == "evasion":
        defend_attr = get_attribute(defender, "agility")
    defend_roll = randint(1, 20) + (defend_skill_val // 5) + (defend_attr // 2)
    
    if attack_roll > defend_roll:
        return "attacker", attack_roll - defend_roll
    else:
        return "defender", defend_roll - attack_roll


# =============================================================================
# Combat State Machine
# =============================================================================

class CombatInstance:
    """
    Manages a single combat encounter.
    
    Stored on characters as character.ndb.combat
    """
    
    def __init__(self, participants, location, encounter_type="hostile"):
        """
        Initialize combat.
        
        Args:
            participants: List of (character, side) tuples
                         side is 'player' or 'enemy'
            location: Room where combat occurs
            encounter_type: Type of encounter for AI behavior
        """
        self.participants = {}  # {character: CombatantState}
        self.location = location
        self.encounter_type = encounter_type
        self.round = 0
        self.turn_order = []
        self.current_turn = 0
        self.active = True
        self.outcome = None
        self.log = []
        
        # Initialize combatants
        for char, side in participants:
            self.add_combatant(char, side)
        
        # Calculate initial turn order
        self.roll_initiative()
    
    def add_combatant(self, character, side):
        """Add a combatant to the fight."""
        self.participants[character] = {
            "side": side,
            "state": "normal",
            "states": [],  # Active status effects
            "initiative": 0,
            "action_taken": False,
            "fled": False,
        }
        # Link combat to character
        character.ndb.combat = self
    
    def remove_combatant(self, character):
        """Remove a combatant from the fight."""
        if character in self.participants:
            del self.participants[character]
            character.ndb.combat = None
    
    def roll_initiative(self):
        """Determine turn order for the round."""
        initiatives = []
        for char in self.participants:
            init = calculate_initiative(char)
            self.participants[char]["initiative"] = init
            initiatives.append((init, char))
        
        # Sort by initiative (highest first)
        initiatives.sort(key=lambda x: x[0], reverse=True)
        self.turn_order = [char for _, char in initiatives]
        self.current_turn = 0
    
    def get_current_combatant(self):
        """Get the character whose turn it is."""
        if self.turn_order and self.current_turn < len(self.turn_order):
            return self.turn_order[self.current_turn]
        return None
    
    def advance_turn(self):
        """Move to the next combatant's turn."""
        self.current_turn += 1
        
        # Check if round is over
        if self.current_turn >= len(self.turn_order):
            self.end_round()
    
    def end_round(self):
        """Process end of round effects and start new round."""
        self.round += 1
        
        # Process duration-based states
        for char, data in self.participants.items():
            new_states = []
            for state_key in data.get("states", []):
                state_data = COMBAT_STATES.get(state_key, {})
                duration = state_data.get("duration", 0)
                if duration > 0:
                    # Decrement duration (stored separately)
                    pass  # Would track duration per state
                else:
                    new_states.append(state_key)
            data["states"] = new_states
            data["action_taken"] = False
        
        # Regeneration/DoT effects would go here
        
        # New initiative
        self.roll_initiative()
    
    def get_enemies(self, character):
        """Get all enemies of a character."""
        char_side = self.participants.get(character, {}).get("side")
        enemies = []
        for char, data in self.participants.items():
            if data["side"] != char_side and not data.get("fled"):
                enemies.append(char)
        return enemies
    
    def get_allies(self, character):
        """Get all allies of a character (including self)."""
        char_side = self.participants.get(character, {}).get("side")
        allies = []
        for char, data in self.participants.items():
            if data["side"] == char_side and not data.get("fled"):
                allies.append(char)
        return allies
    
    def check_victory(self):
        """
        Check if combat has ended.
        Returns (ended, winner_side, condition) or (False, None, None).
        """
        player_side = []
        enemy_side = []
        
        for char, data in self.participants.items():
            if data.get("fled"):
                continue
            
            # Check if defeated
            hp = get_resource(char, "hp")
            stamina = get_resource(char, "stamina")
            composure = get_resource(char, "composure")
            
            defeated = False
            if hp <= 0:
                data["state"] = "unconscious"
                defeated = True
            elif composure <= 0:
                data["state"] = "overwhelmed"
                defeated = True
            
            if not defeated:
                if data["side"] == "player":
                    player_side.append(char)
                else:
                    enemy_side.append(char)
        
        # Check victory conditions
        if not player_side and enemy_side:
            return True, "enemy", "player_defeated"
        elif not enemy_side and player_side:
            return True, "player", "enemy_defeated"
        elif not player_side and not enemy_side:
            return True, None, "mutual_defeat"
        
        return False, None, None
    
    def execute_action(self, actor, action_key, target=None, item=None):
        """
        Execute a combat action.
        
        Returns dict with results.
        """
        action = COMBAT_ACTIONS.get(action_key)
        if not action:
            return {"success": False, "message": "Invalid action."}
        
        actor_data = self.participants.get(actor)
        if not actor_data:
            return {"success": False, "message": "Not in combat."}
        
        # Check if can act
        if actor_data.get("state") == "stunned":
            return {"success": False, "message": "You are stunned!"}
        
        # Check stamina cost
        stamina_cost = action.get("stamina_cost", 0)
        current_stamina = get_resource(actor, "stamina")
        if current_stamina < stamina_cost:
            return {"success": False, "message": "Not enough stamina!"}
        
        # Pay stamina cost
        if stamina_cost > 0:
            modify_resource(actor, "stamina", -stamina_cost)
        
        result = {
            "success": True,
            "action": action_key,
            "actor": actor,
            "target": target,
            "messages": [],
            "damage_dealt": 0,
            "effects_applied": [],
        }
        
        # Handle different action types
        if action["type"] == "offensive":
            result = self._execute_attack(actor, target, action, result)
        elif action["type"] == "defensive":
            result = self._execute_defense(actor, action, result)
        elif action["type"] == "utility":
            result = self._execute_utility(actor, target, action, result, item)
        
        # Mark action taken
        actor_data["action_taken"] = True
        
        # Log the action
        self.log.append(result)
        
        # Check for combat end
        ended, winner, condition = self.check_victory()
        if ended:
            self.end_combat(winner, condition)
            result["combat_ended"] = True
            result["winner"] = winner
            result["condition"] = condition
        
        return result
    
    def _execute_attack(self, actor, target, action, result):
        """Handle offensive actions."""
        if not target:
            enemies = self.get_enemies(actor)
            if enemies:
                target = enemies[0]
            else:
                result["success"] = False
                result["messages"].append("No valid target.")
                return result
        
        target_data = self.participants.get(target)
        if not target_data:
            result["success"] = False
            result["messages"].append("Invalid target.")
            return result
        
        # Get weapon
        weapon = actor.db.equipment.get("main_hand") if actor.db.equipment else None
        
        # Calculate hit
        accuracy = calculate_accuracy(actor, action, weapon)
        evasion = calculate_evasion(target, target_data.get("state"))
        
        hit_roll = randint(1, 100)
        hit_needed = max(5, min(95, 100 - accuracy + evasion))
        
        if hit_roll < hit_needed:
            # Miss
            result["hit"] = False
            result["messages"].append(f"{actor.key} attacks {target.key} but misses!")
            maybe_train_skill(actor, action.get("skill", "melee"), 1)
            maybe_train_skill(target, "evasion", 1)
            return result
        
        # Hit - calculate damage
        result["hit"] = True
        damage_type = action.get("damage_type", "physical")
        
        if damage_type == "physical":
            damage = calculate_damage(actor, action, weapon)
            defense = calculate_defense(target, target_data.get("state"))
            final_damage = max(1, damage - defense)
            
            modify_resource(target, "hp", -final_damage)
            result["damage_dealt"] = final_damage
            result["damage_type"] = "hp"
            result["messages"].append(
                f"{actor.key} hits {target.key} for {final_damage} damage!"
            )
            
        elif damage_type == "stamina":
            damage = randint(5, 12) + get_attribute(actor, "strength") // 2
            modify_resource(target, "stamina", -damage)
            result["damage_dealt"] = damage
            result["damage_type"] = "stamina"
            result["messages"].append(
                f"{actor.key} grapples {target.key}, draining {damage} stamina!"
            )
            
            # Apply grappled state on success
            if action.get("on_success") == "grappled":
                target_data["states"].append("grappled")
                self.participants[actor]["states"].append("grappling")
                result["effects_applied"].append("grappled")
                result["messages"].append(f"{target.key} is now grappled!")
            
        elif damage_type in ["composure", "aphrodisiac"]:
            damage = calculate_composure_damage(actor, action, weapon)
            modify_resource(target, "composure", -damage)
            result["damage_dealt"] = damage
            result["damage_type"] = "composure"
            result["messages"].append(
                f"{actor.key} flusters {target.key}, dealing {damage} composure damage!"
            )
        
        # Train skills
        maybe_train_skill(actor, action.get("skill", "melee"), 2)
        maybe_train_skill(target, "defense", 1)
        
        # Weapon composure damage (for whips, paddles, etc.)
        if weapon and damage_type == "physical":
            weapon_type = weapon.db.weapon_type or "unarmed"
            weapon_data = WEAPON_TYPES.get(weapon_type, {})
            if "composure_damage" in weapon_data:
                comp_range = weapon_data["composure_damage"]
                comp_damage = randint(comp_range[0], comp_range[1])
                modify_resource(target, "composure", -comp_damage)
                result["messages"].append(
                    f"The {weapon_type} also deals {comp_damage} composure damage!"
                )
        
        return result
    
    def _execute_defense(self, actor, action, result):
        """Handle defensive actions."""
        effect = action.get("effect")
        if effect:
            actor_data = self.participants[actor]
            # Remove other stance states
            actor_data["states"] = [
                s for s in actor_data["states"]
                if s not in ["defending", "dodging"]
            ]
            actor_data["states"].append(effect)
            result["messages"].append(f"{actor.key} takes a {action['name']} stance.")
            
            maybe_train_skill(actor, action.get("skill", "defense"), 1)
        
        return result
    
    def _execute_utility(self, actor, target, action, result, item=None):
        """Handle utility actions."""
        action_key = result["action"]
        
        if action_key == "flee":
            return self._execute_flee(actor, result)
        elif action_key == "struggle":
            return self._execute_struggle(actor, result)
        elif action_key == "intimidate":
            return self._execute_intimidate(actor, target, result)
        elif action_key == "submit":
            return self._execute_submit(actor, result)
        elif action_key == "use":
            return self._execute_use_item(actor, item, result)
        elif action_key == "befriend":
            return self._execute_befriend(actor, target, result)
        elif action_key == "seduce":
            return self._execute_seduce(actor, target, result)
        
        return result
    
    def _execute_flee(self, actor, result):
        """Attempt to escape combat."""
        actor_data = self.participants[actor]
        
        # Check if grappled
        if "grappled" in actor_data.get("states", []):
            result["success"] = False
            result["messages"].append("You can't flee while grappled! Struggle first.")
            return result
        
        # Check stamina
        if get_resource(actor, "stamina") < 10:
            result["success"] = False
            result["messages"].append("Too exhausted to flee!")
            return result
        
        # Flee check - evasion vs enemy grappling
        enemies = self.get_enemies(actor)
        best_enemy_grapple = 0
        for enemy in enemies:
            grapple = get_combat_skill(enemy, "grappling")
            if grapple > best_enemy_grapple:
                best_enemy_grapple = grapple
        
        flee_skill = get_combat_skill(actor, "evasion")
        agility = get_attribute(actor, "agility")
        
        flee_roll = randint(1, 20) + (flee_skill // 5) + (agility // 3)
        catch_roll = randint(1, 20) + (best_enemy_grapple // 5)
        
        if flee_roll > catch_roll:
            # Escaped!
            actor_data["fled"] = True
            result["messages"].append(f"{actor.key} successfully escapes!")
            result["fled"] = True
            maybe_train_skill(actor, "evasion", 3)
        else:
            result["success"] = False
            result["messages"].append(f"{actor.key} tries to flee but is cut off!")
            maybe_train_skill(actor, "evasion", 1)
        
        return result
    
    def _execute_struggle(self, actor, result):
        """Attempt to break free from grapple."""
        actor_data = self.participants[actor]
        
        if "grappled" not in actor_data.get("states", []):
            result["messages"].append("You're not grappled.")
            return result
        
        # Find who's grappling us
        grappler = None
        for char, data in self.participants.items():
            if "grappling" in data.get("states", []) and char != actor:
                grappler = char
                break
        
        if not grappler:
            # No grappler found, free automatically
            actor_data["states"].remove("grappled")
            result["messages"].append("You break free!")
            return result
        
        # Contest: our grappling vs their grappling
        winner, margin = roll_contest(actor, grappler, "grappling", "grappling")
        
        if winner == "attacker":
            actor_data["states"].remove("grappled")
            self.participants[grappler]["states"].remove("grappling")
            result["messages"].append(f"{actor.key} breaks free from the grapple!")
            maybe_train_skill(actor, "grappling", 2)
        else:
            result["success"] = False
            result["messages"].append(f"{actor.key} struggles but can't break free!")
            maybe_train_skill(actor, "grappling", 1)
        
        return result
    
    def _execute_intimidate(self, actor, target, result):
        """Try to scare off opponent."""
        if not target:
            enemies = self.get_enemies(actor)
            if enemies:
                target = enemies[0]
            else:
                result["success"] = False
                result["messages"].append("No one to intimidate.")
                return result
        
        # Contest: intimidation vs resistance
        winner, margin = roll_contest(actor, target, "intimidation", "resistance")
        
        if winner == "attacker" and margin > 5:
            self.participants[target]["fled"] = True
            result["messages"].append(f"{target.key} is scared off by {actor.key}!")
            result["intimidated"] = True
            maybe_train_skill(actor, "intimidation", 3)
        else:
            result["success"] = False
            result["messages"].append(f"{target.key} is not impressed.")
            maybe_train_skill(actor, "intimidation", 1)
        
        return result
    
    def _execute_submit(self, actor, result):
        """Surrender to opponent."""
        actor_data = self.participants[actor]
        actor_data["state"] = "submitted"
        result["messages"].append(f"{actor.key} surrenders!")
        result["submitted"] = True
        
        # This will trigger defeat in check_victory
        self.end_combat("enemy", "submission")
        result["combat_ended"] = True
        
        return result
    
    def _execute_seduce(self, actor, target, result):
        """Try to overwhelm opponent with charm."""
        if not target:
            enemies = self.get_enemies(actor)
            if enemies:
                target = enemies[0]
            else:
                result["success"] = False
                result["messages"].append("No one to seduce.")
                return result
        
        # Contest: seduction vs resistance
        winner, margin = roll_contest(actor, target, "seduction", "resistance")
        
        damage = calculate_composure_damage(actor, COMBAT_ACTIONS["seduce"])
        
        if winner == "attacker":
            # Extra damage on win
            damage = int(damage * 1.5)
            result["messages"].append(
                f"{actor.key} successfully seduces {target.key}!"
            )
        else:
            damage = damage // 2
            result["messages"].append(
                f"{actor.key} tries to seduce {target.key} with limited success."
            )
        
        modify_resource(target, "composure", -damage)
        result["damage_dealt"] = damage
        result["damage_type"] = "composure"
        result["messages"].append(f"{target.key} loses {damage} composure!")
        
        maybe_train_skill(actor, "seduction", 2)
        maybe_train_skill(target, "resistance", 1)
        
        return result
    
    def _execute_befriend(self, actor, target, result):
        """Try to make peace with a creature."""
        if not target:
            result["success"] = False
            result["messages"].append("No one to befriend.")
            return result
        
        # Check if target is befriendable
        if hasattr(target, "db") and not target.db.befriendable:
            result["success"] = False
            result["messages"].append(f"{target.key} cannot be befriended.")
            return result
        
        # Charisma check
        charisma = get_attribute(actor, "charisma")
        difficulty = target.db.befriend_difficulty if hasattr(target, "db") else 15
        
        roll = randint(1, 20) + charisma // 2
        
        if roll >= difficulty:
            self.participants[target]["fled"] = True  # Creature leaves peacefully
            result["messages"].append(
                f"{actor.key} calms {target.key}. It leaves peacefully."
            )
            result["befriended"] = True
            
            # Could increase reputation with creature type here
        else:
            result["success"] = False
            result["messages"].append(
                f"{actor.key} tries to calm {target.key} but it's not interested."
            )
        
        return result
    
    def _execute_use_item(self, actor, item, result):
        """Use an item in combat."""
        if not item:
            result["success"] = False
            result["messages"].append("What item?")
            return result
        
        # Item use would integrate with items.py
        # For now, basic structure
        if hasattr(item, "db") and item.db.combat_use:
            use_data = item.db.combat_use
            
            if use_data.get("heal_hp"):
                amount = use_data["heal_hp"]
                modify_resource(actor, "hp", amount)
                result["messages"].append(f"{actor.key} uses {item.key}, restoring {amount} HP!")
            
            if use_data.get("heal_stamina"):
                amount = use_data["heal_stamina"]
                modify_resource(actor, "stamina", amount)
                result["messages"].append(f"{actor.key} uses {item.key}, restoring {amount} stamina!")
            
            if use_data.get("heal_composure"):
                amount = use_data["heal_composure"]
                modify_resource(actor, "composure", amount)
                result["messages"].append(f"{actor.key} uses {item.key}, restoring {amount} composure!")
            
            # Consume the item
            if use_data.get("consumed", True):
                item.delete()
        else:
            result["success"] = False
            result["messages"].append(f"Can't use {item.key} in combat.")
        
        return result
    
    def end_combat(self, winner_side, condition):
        """End the combat and process results."""
        self.active = False
        self.outcome = {
            "winner": winner_side,
            "condition": condition,
        }
        
        # Unlink combat from all participants
        for char in list(self.participants.keys()):
            char.ndb.combat = None
        
        return self.outcome
    
    def get_status_display(self, for_character):
        """Get a formatted combat status display."""
        lines = []
        lines.append("|w=== COMBAT ===|n")
        lines.append(f"Round {self.round}")
        lines.append("")
        
        # Show all combatants
        for char, data in self.participants.items():
            if data.get("fled"):
                continue
            
            side_marker = "|g[ALLY]|n" if data["side"] == self.participants.get(for_character, {}).get("side") else "|r[ENEMY]|n"
            turn_marker = " |y<--|n" if char == self.get_current_combatant() else ""
            
            lines.append(f"{side_marker} {char.key}{turn_marker}")
            lines.append(f"  {get_resource_display(char, 'hp')}")
            lines.append(f"  {get_resource_display(char, 'stamina')}")
            lines.append(f"  {get_resource_display(char, 'composure')}")
            
            # Show states
            states = data.get("states", [])
            if states:
                state_names = [COMBAT_STATES.get(s, {}).get("name", s) for s in states]
                lines.append(f"  Status: {', '.join(state_names)}")
            lines.append("")
        
        # Show available actions for current character
        current = self.get_current_combatant()
        if current == for_character:
            lines.append("|wYour turn! Actions:|n")
            available = self.get_available_actions(for_character)
            action_list = ", ".join(available)
            lines.append(f"  {action_list}")
        
        return "\n".join(lines)
    
    def get_available_actions(self, character):
        """Get list of actions available to a character."""
        char_data = self.participants.get(character, {})
        states = char_data.get("states", [])
        
        available = []
        
        for action_key, action in COMBAT_ACTIONS.items():
            # Check state restrictions
            if "grappled" in states:
                if action_key in ["flee", "attack", "power_attack"]:
                    continue
            if "grappling" in states:
                limited = COMBAT_STATES["grappling"].get("limited_actions", [])
                if action_key not in limited and action_key not in ["release", "use", "submit"]:
                    continue
            
            # Check stamina
            stamina_cost = action.get("stamina_cost", 0)
            if get_resource(character, "stamina") < stamina_cost:
                continue
            
            available.append(action_key)
        
        return available


# =============================================================================
# Encounter Initialization
# =============================================================================

def start_combat(player, enemies, location, encounter_type="hostile"):
    """
    Initialize a combat encounter.
    
    Args:
        player: The player character
        enemies: List of enemy characters/creatures
        location: Room where combat occurs
        encounter_type: Type affecting AI behavior
        
    Returns:
        CombatInstance
    """
    participants = [(player, "player")]
    for enemy in enemies:
        participants.append((enemy, "enemy"))
    
    combat = CombatInstance(participants, location, encounter_type)
    
    # Announce combat
    player.msg("|r=== COMBAT BEGINS ===|n")
    enemy_names = ", ".join([e.key for e in enemies])
    player.msg(f"You are attacked by: {enemy_names}!")
    player.msg(combat.get_status_display(player))
    
    # NPC enemies get their AI triggered
    for enemy in enemies:
        if hasattr(enemy, "db") and enemy.db.is_npc:
            # AI will act on their turn
            pass
    
    return combat


def start_pvp_combat(challenger, target, location):
    """
    Initialize PvP combat between two players.
    
    Requires target consent.
    """
    # Check if target has PvP enabled
    if hasattr(target, "db") and not target.db.pvp_enabled:
        return None, "Target has PvP disabled."
    
    participants = [
        (challenger, "player"),
        (target, "enemy"),  # "enemy" just means opposing side
    ]
    
    combat = CombatInstance(participants, location, "pvp")
    
    challenger.msg(f"|r=== PVP COMBAT ===|n\nYou challenge {target.key}!")
    target.msg(f"|r=== PVP COMBAT ===|n\n{challenger.key} attacks you!")
    
    challenger.msg(combat.get_status_display(challenger))
    target.msg(combat.get_status_display(target))
    
    return combat, "Combat started."


# =============================================================================
# Defeat Processing
# =============================================================================

DEFEAT_OUTCOMES = {
    # Creature type -> outcome settings
    "default": {
        "wake_location": "same",  # Wake where you fell
        "wake_delay": 30,  # Seconds
        "loot_lost": False,
        "scene_key": None,
    },
    "slime": {
        "wake_location": "same",
        "wake_delay": 60,
        "loot_lost": False,
        "scene_key": "slime_capture",
        "condition_check": "composure",  # Only scene if composure defeat
    },
    "goblin": {
        "wake_location": "goblin_camp",  # Wake in their camp
        "wake_delay": 120,
        "loot_lost": True,  # They rob you
        "escape_required": True,  # Must escape
        "scene_key": "goblin_capture",
    },
    "wolf": {
        "wake_location": "same",
        "wake_delay": 45,
        "loot_lost": False,
        "scene_key": "wolf_pack",
    },
    "tentacle_plant": {
        "wake_location": "same",
        "wake_delay": 90,
        "scene_key": "tentacle_capture",
        "condition_check": "composure",
    },
    "pvp": {
        "wake_location": "same",
        "wake_delay": 30,
        "loot_lost": False,  # Winner decides
        "winner_choice": True,
    },
}


def process_defeat(character, victor, condition, encounter_type="default"):
    """
    Process what happens when a character is defeated.
    
    Args:
        character: The defeated character
        victor: Who defeated them
        condition: How they were defeated (hp_zero, composure_zero, etc.)
        encounter_type: Type of encounter for outcome selection
    """
    outcome = DEFEAT_OUTCOMES.get(encounter_type, DEFEAT_OUTCOMES["default"])
    
    # Check if scene plays based on condition
    scene_key = outcome.get("scene_key")
    condition_check = outcome.get("condition_check")
    
    if condition_check and condition != f"{condition_check}_zero":
        scene_key = None  # No scene for wrong defeat type
    
    # Check character's defeat preferences
    prefs = character.db.defeat_preferences or "choice"
    
    if scene_key and prefs != "fade_to_black":
        # Would trigger scene system here
        character.msg(f"|mA scene would play here: {scene_key}|n")
    else:
        character.msg("|wEverything goes dark...|n")
    
    # Handle loot loss
    if outcome.get("loot_lost"):
        # Would remove coins/items here
        character.msg("|rYou've been robbed while unconscious!|n")
    
    # Determine wake location
    wake_loc = outcome.get("wake_location", "same")
    if wake_loc == "same":
        wake_room = character.location
    else:
        # Would look up room by key
        wake_room = character.location  # Fallback
    
    # Schedule waking up
    wake_delay = outcome.get("wake_delay", 30)
    
    def wake_up():
        character.msg("|wYou slowly regain consciousness...|n")
        restore_all_resources(character)
        
        if outcome.get("escape_required"):
            character.msg("|yYou need to find a way to escape!|n")
        else:
            # Move to wake location if different
            if wake_room != character.location:
                character.move_to(wake_room, quiet=True)
                character.msg(character.location.get_display_name(character))
    
    delay(wake_delay, wake_up)
    
    return outcome


# =============================================================================
# Utility Functions
# =============================================================================

def is_in_combat(character):
    """Check if character is currently in combat."""
    return character.ndb.combat is not None and character.ndb.combat.active


def get_combat(character):
    """Get the character's current combat instance."""
    return character.ndb.combat


def can_initiate_combat(character):
    """Check if character can start a fight."""
    if is_in_combat(character):
        return False, "Already in combat."
    
    if get_resource(character, "hp") <= 0:
        return False, "Too injured to fight."
    
    return True, "OK"


def initialize_combat_stats(character):
    """Set up combat stats for a new character."""
    if not character.db.attributes:
        character.db.attributes = {}
        for attr_key, attr_data in PRIMARY_ATTRIBUTES.items():
            character.db.attributes[attr_key] = attr_data["default"]
    
    if not character.db.combat_skills:
        character.db.combat_skills = {}
    
    if not character.db.combat_skill_exp:
        character.db.combat_skill_exp = {}
    
    if not character.db.resources:
        character.db.resources = {}
    
    # Initialize resources to max
    restore_all_resources(character)


def get_attribute_display(character):
    """Get formatted display of all attributes."""
    lines = ["|wAttributes:|n"]
    for attr_key, attr_data in PRIMARY_ATTRIBUTES.items():
        value = get_attribute(character, attr_key)
        abbrev = attr_data["abbrev"]
        name = attr_data["name"]
        lines.append(f"  {abbrev}: {value:2d} ({name})")
    return "\n".join(lines)


def get_combat_skills_display(character):
    """Get formatted display of combat skills."""
    lines = ["|wCombat Skills:|n"]
    for skill_key, skill_data in COMBAT_SKILLS.items():
        level = get_combat_skill(character, skill_key)
        exp = get_combat_skill_exp(character, skill_key)
        name = skill_data["name"]
        lines.append(f"  {name}: {level} ({exp}/{SKILL_EXP_PER_LEVEL} exp)")
    return "\n".join(lines)
