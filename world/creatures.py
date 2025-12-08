"""
Creature Templates for Gilderhaven

Defines creature types, their stats, behaviors, attack patterns,
loot tables, and defeat outcomes.

All creatures focus on CAPTURE, not kill.
"""

from random import randint, random, choice

# =============================================================================
# CREATURE CATEGORIES
# =============================================================================

CREATURE_CATEGORIES = {
    "beast": {
        "name": "Beast",
        "desc": "Natural animals, often pack hunters.",
    },
    "monster": {
        "name": "Monster",
        "desc": "Magical or unnatural creatures.",
    },
    "plant": {
        "name": "Plant",
        "desc": "Carnivorous or animated plants.",
    },
    "humanoid": {
        "name": "Humanoid",
        "desc": "Intelligent humanoid creatures.",
    },
    "slime": {
        "name": "Slime",
        "desc": "Amorphous creatures.",
    },
    "spirit": {
        "name": "Spirit",
        "desc": "Ethereal or magical entities.",
    },
}


# =============================================================================
# AI BEHAVIOR TYPES
# =============================================================================

AI_BEHAVIORS = {
    "aggressive": {
        "name": "Aggressive",
        "desc": "Attacks on sight, focuses damage.",
        "attack_priority": ["attack", "power_attack"],
        "flee_threshold": 0.1,  # Flees at 10% HP
        "preferred_target": "lowest_hp",
    },
    "predatory": {
        "name": "Predatory",
        "desc": "Tries to capture, not kill. Grapples and exhausts.",
        "attack_priority": ["grapple", "attack"],
        "flee_threshold": 0.2,
        "preferred_target": "lowest_stamina",
        "goal": "capture",
    },
    "lustful": {
        "name": "Lustful",
        "desc": "Focuses on composure damage.",
        "attack_priority": ["tease", "grapple", "seduce"],
        "flee_threshold": 0.15,
        "preferred_target": "lowest_composure",
        "goal": "overwhelm",
    },
    "territorial": {
        "name": "Territorial",
        "desc": "Defends area, stops attacking if target flees.",
        "attack_priority": ["attack", "intimidate"],
        "flee_threshold": 0.3,
        "preferred_target": "closest",
        "stops_if_fleeing": True,
    },
    "pack": {
        "name": "Pack Hunter",
        "desc": "Coordinates with allies, focuses single target.",
        "attack_priority": ["grapple", "attack"],
        "flee_threshold": 0.25,
        "preferred_target": "same_as_ally",
        "pack_bonus": True,
    },
    "ambusher": {
        "name": "Ambusher",
        "desc": "High first-strike damage, then normal.",
        "attack_priority": ["power_attack", "attack"],
        "flee_threshold": 0.2,
        "ambush_bonus": 1.5,  # 50% more damage on first hit
    },
    "defensive": {
        "name": "Defensive",
        "desc": "Alternates attacking and defending.",
        "attack_priority": ["attack", "defend"],
        "flee_threshold": 0.3,
        "alternates_defense": True,
    },
    "swarm": {
        "name": "Swarm",
        "desc": "Weak individually, dangerous in numbers.",
        "attack_priority": ["attack"],
        "flee_threshold": 0.0,  # Never flees
        "swarm_bonus": True,
    },
}


# =============================================================================
# CREATURE TEMPLATES
# =============================================================================

CREATURE_TEMPLATES = {
    # =========================================================================
    # SLIMES
    # =========================================================================
    "green_slime": {
        "name": "Green Slime",
        "desc": "A quivering mass of green gel. It pulses hungrily.",
        "category": "slime",
        "behavior": "lustful",
        "level": 1,
        "attributes": {
            "strength": 6,
            "agility": 4,
            "endurance": 12,
            "willpower": 3,
            "charisma": 8,
        },
        "base_hp": 30,
        "base_stamina": 40,
        "base_composure": 100,  # High - hard to seduce a slime
        "skills": {
            "grappling": 20,
            "seduction": 30,  # Natural aphrodisiac
        },
        "attacks": [
            {
                "name": "Engulf",
                "chance": 0.6,
                "damage_type": "composure",
                "damage": (5, 12),
                "message": "The slime engulfs {target}, tingling sensations spreading!",
            },
            {
                "name": "Slime Tendril",
                "chance": 0.4,
                "damage_type": "stamina",
                "damage": (3, 8),
                "message": "A tendril wraps around {target}, draining energy!",
            },
        ],
        "defeat_type": "slime",
        "befriendable": False,
        "loot": [
            {"item": "slime_gel", "chance": 0.8, "amount": (1, 3)},
            {"item": "beast_essence", "chance": 0.2, "amount": (1, 1)},
        ],
        "exp_reward": 15,
        "spawn_areas": ["whisperwood", "moonshallow"],
    },
    
    "pink_slime": {
        "name": "Pink Slime",
        "desc": "A rosy blob that smells faintly of flowers. Very... affectionate.",
        "category": "slime",
        "behavior": "lustful",
        "level": 3,
        "attributes": {
            "strength": 5,
            "agility": 5,
            "endurance": 10,
            "willpower": 2,
            "charisma": 15,
        },
        "base_hp": 25,
        "base_stamina": 35,
        "base_composure": 100,
        "skills": {
            "grappling": 25,
            "seduction": 50,
        },
        "attacks": [
            {
                "name": "Aphrodisiac Embrace",
                "chance": 0.7,
                "damage_type": "aphrodisiac",
                "damage": (8, 15),
                "message": "The pink slime envelops {target} in a warm, tingling embrace!",
            },
            {
                "name": "Slime Kiss",
                "chance": 0.3,
                "damage_type": "composure",
                "damage": (10, 18),
                "message": "The slime forms a mouth-like shape and plants a 'kiss' on {target}!",
            },
        ],
        "defeat_type": "slime",
        "befriendable": False,
        "loot": [
            {"item": "slime_gel", "chance": 0.7, "amount": (1, 2)},
            {"item": "passion_poppy", "chance": 0.3, "amount": (1, 2)},
            {"item": "beast_essence", "chance": 0.3, "amount": (1, 1)},
        ],
        "exp_reward": 25,
        "spawn_areas": ["whisperwood", "sunny_meadow"],
    },
    
    # =========================================================================
    # BEASTS
    # =========================================================================
    "wolf": {
        "name": "Wolf",
        "desc": "A grey wolf with hungry eyes. It circles you warily.",
        "category": "beast",
        "behavior": "pack",
        "level": 3,
        "attributes": {
            "strength": 12,
            "agility": 14,
            "endurance": 10,
            "willpower": 8,
            "charisma": 5,
        },
        "base_hp": 40,
        "base_stamina": 50,
        "base_composure": 60,
        "skills": {
            "melee": 25,
            "grappling": 30,
            "evasion": 20,
        },
        "attacks": [
            {
                "name": "Bite",
                "chance": 0.5,
                "damage_type": "physical",
                "damage": (6, 12),
                "message": "The wolf lunges and bites {target}!",
            },
            {
                "name": "Pounce",
                "chance": 0.3,
                "damage_type": "stamina",
                "damage": (8, 14),
                "applies": "grappled",
                "message": "The wolf pounces on {target}, pinning them!",
            },
            {
                "name": "Pack Howl",
                "chance": 0.2,
                "effect": "call_reinforcement",
                "message": "The wolf howls, calling for its pack!",
            },
        ],
        "defeat_type": "wolf",
        "befriendable": True,
        "befriend_difficulty": 18,
        "loot": [
            {"item": "wolf_pelt", "chance": 0.5, "amount": (1, 1)},
            {"item": "beast_essence", "chance": 0.3, "amount": (1, 1)},
            {"item": "fangs", "chance": 0.4, "amount": (1, 2)},
        ],
        "exp_reward": 30,
        "spawn_areas": ["whisperwood"],
        "pack_size": (2, 4),  # Spawns in groups
    },
    
    "alpha_wolf": {
        "name": "Alpha Wolf",
        "desc": "A massive wolf with scars marking many battles. Leader of the pack.",
        "category": "beast",
        "behavior": "pack",
        "level": 6,
        "attributes": {
            "strength": 16,
            "agility": 14,
            "endurance": 14,
            "willpower": 12,
            "charisma": 10,
        },
        "base_hp": 70,
        "base_stamina": 60,
        "base_composure": 80,
        "skills": {
            "melee": 40,
            "grappling": 45,
            "evasion": 25,
            "intimidation": 35,
        },
        "attacks": [
            {
                "name": "Savage Bite",
                "chance": 0.4,
                "damage_type": "physical",
                "damage": (10, 18),
                "message": "The alpha's jaws clamp down on {target}!",
            },
            {
                "name": "Dominating Pounce",
                "chance": 0.3,
                "damage_type": "stamina",
                "damage": (12, 20),
                "secondary_damage": {"type": "composure", "amount": (5, 10)},
                "applies": "grappled",
                "message": "The alpha pins {target} beneath its massive form!",
            },
            {
                "name": "Intimidating Growl",
                "chance": 0.3,
                "damage_type": "composure",
                "damage": (8, 15),
                "message": "The alpha growls menacingly, asserting dominance!",
            },
        ],
        "defeat_type": "wolf",
        "befriendable": True,
        "befriend_difficulty": 25,
        "loot": [
            {"item": "alpha_pelt", "chance": 0.6, "amount": (1, 1)},
            {"item": "beast_essence", "chance": 0.5, "amount": (1, 2)},
            {"item": "alpha_fang", "chance": 0.3, "amount": (1, 1)},
        ],
        "exp_reward": 60,
        "spawn_areas": ["whisperwood_deep"],
        "is_boss": True,
    },
    
    # =========================================================================
    # PLANTS
    # =========================================================================
    "grabbing_vine": {
        "name": "Grabbing Vine",
        "desc": "Thick vines that seem to move with purpose, reaching toward you.",
        "category": "plant",
        "behavior": "ambusher",
        "level": 2,
        "attributes": {
            "strength": 14,
            "agility": 6,
            "endurance": 15,
            "willpower": 5,
            "charisma": 3,
        },
        "base_hp": 35,
        "base_stamina": 100,  # Plants don't tire
        "base_composure": 100,  # Can't be seduced
        "skills": {
            "grappling": 40,
        },
        "attacks": [
            {
                "name": "Constrict",
                "chance": 0.6,
                "damage_type": "stamina",
                "damage": (6, 12),
                "applies": "grappled",
                "message": "Vines wrap tightly around {target}!",
            },
            {
                "name": "Squeeze",
                "chance": 0.4,
                "damage_type": "physical",
                "damage": (4, 10),
                "requires": "grappled",  # Only when grappling
                "message": "The vines squeeze {target} painfully!",
            },
        ],
        "defeat_type": "default",
        "befriendable": False,
        "loot": [
            {"item": "fiber", "chance": 0.9, "amount": (2, 5)},
            {"item": "wood", "chance": 0.5, "amount": (1, 2)},
        ],
        "exp_reward": 20,
        "spawn_areas": ["whisperwood", "moonshallow"],
    },
    
    "tentacle_blossom": {
        "name": "Tentacle Blossom",
        "desc": "A beautiful flower with writhing tentacle-like stamens. It exudes a sweet scent.",
        "category": "plant",
        "behavior": "lustful",
        "level": 5,
        "attributes": {
            "strength": 12,
            "agility": 8,
            "endurance": 12,
            "willpower": 5,
            "charisma": 14,
        },
        "base_hp": 45,
        "base_stamina": 100,
        "base_composure": 100,
        "skills": {
            "grappling": 50,
            "seduction": 45,
        },
        "attacks": [
            {
                "name": "Aphrodisiac Pollen",
                "chance": 0.4,
                "damage_type": "aphrodisiac",
                "damage": (10, 18),
                "message": "The flower releases a cloud of sweet pollen around {target}!",
            },
            {
                "name": "Tentacle Wrap",
                "chance": 0.35,
                "damage_type": "stamina",
                "damage": (5, 10),
                "applies": "grappled",
                "message": "Tentacles wind around {target}'s limbs!",
            },
            {
                "name": "Probing Tendrils",
                "chance": 0.25,
                "damage_type": "composure",
                "damage": (12, 22),
                "requires": "grappled",
                "message": "Tendrils explore {target}'s body intimately!",
            },
        ],
        "defeat_type": "tentacle_plant",
        "befriendable": False,
        "loot": [
            {"item": "passion_poppy", "chance": 0.6, "amount": (1, 3)},
            {"item": "beast_essence", "chance": 0.4, "amount": (1, 2)},
            {"item": "moon_lily", "chance": 0.2, "amount": (1, 1)},
        ],
        "exp_reward": 45,
        "spawn_areas": ["whisperwood_deep", "sunny_meadow"],
    },
    
    # =========================================================================
    # HUMANOIDS
    # =========================================================================
    "goblin": {
        "name": "Goblin",
        "desc": "A small green creature with pointed ears and a wicked grin.",
        "category": "humanoid",
        "behavior": "aggressive",
        "level": 2,
        "attributes": {
            "strength": 8,
            "agility": 12,
            "endurance": 8,
            "willpower": 6,
            "charisma": 5,
        },
        "base_hp": 25,
        "base_stamina": 35,
        "base_composure": 40,
        "skills": {
            "melee": 20,
            "evasion": 25,
        },
        "attacks": [
            {
                "name": "Club Swing",
                "chance": 0.7,
                "damage_type": "physical",
                "damage": (4, 10),
                "message": "The goblin swings its club at {target}!",
            },
            {
                "name": "Dirty Trick",
                "chance": 0.3,
                "damage_type": "stamina",
                "damage": (5, 8),
                "message": "The goblin throws dirt in {target}'s eyes!",
            },
        ],
        "defeat_type": "goblin",
        "befriendable": False,
        "loot": [
            {"item": "copper_coins", "chance": 0.8, "amount": (5, 20)},
            {"item": "junk", "chance": 0.5, "amount": (1, 2)},
        ],
        "exp_reward": 20,
        "spawn_areas": ["copper_hill"],
        "pack_size": (1, 3),
    },
    
    "goblin_shaman": {
        "name": "Goblin Shaman",
        "desc": "A goblin adorned with bones and feathers, clutching a gnarled staff.",
        "category": "humanoid",
        "behavior": "defensive",
        "level": 4,
        "attributes": {
            "strength": 6,
            "agility": 10,
            "endurance": 8,
            "willpower": 14,
            "charisma": 10,
        },
        "base_hp": 30,
        "base_stamina": 40,
        "base_composure": 60,
        "skills": {
            "melee": 10,
            "resistance": 35,
            "seduction": 20,  # Knows curses
        },
        "attacks": [
            {
                "name": "Hex",
                "chance": 0.5,
                "damage_type": "composure",
                "damage": (8, 14),
                "message": "The shaman casts a hex on {target}!",
            },
            {
                "name": "Lust Curse",
                "chance": 0.3,
                "damage_type": "aphrodisiac",
                "damage": (10, 18),
                "applies": "aroused",
                "message": "The shaman mutters a curse - heat floods through {target}!",
            },
            {
                "name": "Staff Strike",
                "chance": 0.2,
                "damage_type": "physical",
                "damage": (3, 8),
                "message": "The shaman whacks {target} with its staff!",
            },
        ],
        "defeat_type": "goblin",
        "befriendable": False,
        "loot": [
            {"item": "copper_coins", "chance": 0.9, "amount": (15, 40)},
            {"item": "bitter_root", "chance": 0.4, "amount": (1, 2)},
            {"item": "beast_essence", "chance": 0.3, "amount": (1, 1)},
        ],
        "exp_reward": 40,
        "spawn_areas": ["copper_hill"],
    },
    
    # =========================================================================
    # SPIRITS
    # =========================================================================
    "wisp": {
        "name": "Lustful Wisp",
        "desc": "A glowing ball of pink light that drifts toward you enticingly.",
        "category": "spirit",
        "behavior": "lustful",
        "level": 4,
        "attributes": {
            "strength": 2,
            "agility": 18,
            "endurance": 5,
            "willpower": 15,
            "charisma": 16,
        },
        "base_hp": 15,
        "base_stamina": 60,
        "base_composure": 80,
        "skills": {
            "evasion": 50,
            "seduction": 55,
        },
        "attacks": [
            {
                "name": "Euphoric Touch",
                "chance": 0.6,
                "damage_type": "composure",
                "damage": (10, 20),
                "message": "The wisp passes through {target}, leaving trails of pleasure!",
            },
            {
                "name": "Dream Whisper",
                "chance": 0.4,
                "damage_type": "aphrodisiac",
                "damage": (12, 22),
                "message": "The wisp whispers fantasies directly into {target}'s mind!",
            },
        ],
        "defeat_type": "default",
        "befriendable": True,
        "befriend_difficulty": 16,
        "loot": [
            {"item": "wisp_essence", "chance": 0.5, "amount": (1, 1)},
            {"item": "glowing_mushroom", "chance": 0.3, "amount": (1, 2)},
        ],
        "exp_reward": 35,
        "spawn_areas": ["moonshallow", "whisperwood"],
        "resistances": {"physical": 0.5},  # Takes half physical damage
    },
    
    # =========================================================================
    # MONSTERS
    # =========================================================================
    "harpy": {
        "name": "Harpy",
        "desc": "A creature with a woman's torso and bird-like wings and talons.",
        "category": "monster",
        "behavior": "predatory",
        "level": 5,
        "attributes": {
            "strength": 10,
            "agility": 16,
            "endurance": 10,
            "willpower": 10,
            "charisma": 14,
        },
        "base_hp": 40,
        "base_stamina": 55,
        "base_composure": 50,
        "skills": {
            "melee": 30,
            "grappling": 35,
            "seduction": 25,
            "evasion": 40,
        },
        "attacks": [
            {
                "name": "Talon Strike",
                "chance": 0.4,
                "damage_type": "physical",
                "damage": (8, 14),
                "message": "The harpy rakes {target} with sharp talons!",
            },
            {
                "name": "Snatch",
                "chance": 0.35,
                "damage_type": "stamina",
                "damage": (6, 12),
                "applies": "grappled",
                "message": "The harpy grabs {target} in her talons!",
            },
            {
                "name": "Alluring Song",
                "chance": 0.25,
                "damage_type": "composure",
                "damage": (10, 16),
                "message": "The harpy sings an enchanting melody that clouds {target}'s mind!",
            },
        ],
        "defeat_type": "harpy",
        "befriendable": True,
        "befriend_difficulty": 20,
        "loot": [
            {"item": "harpy_feather", "chance": 0.6, "amount": (2, 4)},
            {"item": "beast_essence", "chance": 0.3, "amount": (1, 1)},
        ],
        "exp_reward": 50,
        "spawn_areas": ["copper_hill_heights"],
        "can_fly": True,
    },
    
    "mimic": {
        "name": "Mimic",
        "desc": "What appeared to be a treasure chest reveals rows of teeth and a long tongue!",
        "category": "monster",
        "behavior": "ambusher",
        "level": 4,
        "attributes": {
            "strength": 14,
            "agility": 8,
            "endurance": 14,
            "willpower": 8,
            "charisma": 6,
        },
        "base_hp": 50,
        "base_stamina": 45,
        "base_composure": 70,
        "skills": {
            "grappling": 45,
            "melee": 25,
        },
        "attacks": [
            {
                "name": "Adhesive Tongue",
                "chance": 0.5,
                "damage_type": "stamina",
                "damage": (8, 14),
                "applies": "grappled",
                "message": "The mimic's tongue lashes out and sticks to {target}!",
            },
            {
                "name": "Crushing Bite",
                "chance": 0.35,
                "damage_type": "physical",
                "damage": (10, 18),
                "message": "The mimic chomps down on {target}!",
            },
            {
                "name": "Digest",
                "chance": 0.15,
                "damage_type": "composure",
                "damage": (5, 10),
                "requires": "grappled",
                "message": "Digestive fluids from the mimic tingle against {target}'s skin!",
            },
        ],
        "defeat_type": "default",
        "befriendable": False,
        "loot": [
            {"item": "copper_coins", "chance": 0.9, "amount": (30, 80)},
            {"item": "random_gem", "chance": 0.3, "amount": (1, 1)},
            {"item": "mimic_tongue", "chance": 0.2, "amount": (1, 1)},
        ],
        "exp_reward": 45,
        "spawn_areas": ["copper_hill", "dungeons"],
        "disguised_as": "treasure_chest",
    },
    
    "lamia": {
        "name": "Lamia",
        "desc": "A beautiful woman from the waist up, with the powerful body of a serpent below.",
        "category": "monster",
        "behavior": "predatory",
        "level": 7,
        "attributes": {
            "strength": 14,
            "agility": 12,
            "endurance": 14,
            "willpower": 14,
            "charisma": 18,
        },
        "base_hp": 65,
        "base_stamina": 60,
        "base_composure": 70,
        "skills": {
            "grappling": 55,
            "seduction": 50,
            "resistance": 35,
            "melee": 30,
        },
        "attacks": [
            {
                "name": "Constrict",
                "chance": 0.35,
                "damage_type": "stamina",
                "damage": (10, 18),
                "secondary_damage": {"type": "physical", "amount": (4, 8)},
                "applies": "grappled",
                "message": "The lamia coils her serpentine body around {target}!",
            },
            {
                "name": "Mesmerizing Gaze",
                "chance": 0.3,
                "damage_type": "composure",
                "damage": (12, 20),
                "message": "The lamia's eyes swirl hypnotically, clouding {target}'s thoughts!",
            },
            {
                "name": "Venomous Kiss",
                "chance": 0.2,
                "damage_type": "aphrodisiac",
                "damage": (15, 25),
                "requires": "grappled",
                "message": "The lamia presses her lips to {target}, venom inducing heat!",
            },
            {
                "name": "Tail Lash",
                "chance": 0.15,
                "damage_type": "physical",
                "damage": (8, 14),
                "message": "The lamia's tail whips across {target}!",
            },
        ],
        "defeat_type": "lamia",
        "befriendable": True,
        "befriend_difficulty": 24,
        "loot": [
            {"item": "lamia_scale", "chance": 0.5, "amount": (2, 5)},
            {"item": "beast_essence", "chance": 0.4, "amount": (1, 2)},
            {"item": "passion_poppy", "chance": 0.3, "amount": (1, 2)},
        ],
        "exp_reward": 75,
        "spawn_areas": ["whisperwood_deep", "ruins"],
        "is_boss": True,
    },
}


# =============================================================================
# SPAWN TABLES
# =============================================================================
# Defines what can spawn in each area

SPAWN_TABLES = {
    "whisperwood": {
        "common": ["green_slime", "grabbing_vine"],
        "uncommon": ["wolf", "wisp"],
        "rare": ["pink_slime", "tentacle_blossom"],
        "weights": {"common": 0.6, "uncommon": 0.3, "rare": 0.1},
    },
    "whisperwood_deep": {
        "common": ["wolf", "grabbing_vine"],
        "uncommon": ["tentacle_blossom", "pink_slime"],
        "rare": ["alpha_wolf", "lamia"],
        "weights": {"common": 0.5, "uncommon": 0.35, "rare": 0.15},
    },
    "moonshallow": {
        "common": ["green_slime", "wisp"],
        "uncommon": ["pink_slime"],
        "rare": [],
        "weights": {"common": 0.7, "uncommon": 0.3, "rare": 0.0},
    },
    "sunny_meadow": {
        "common": [],
        "uncommon": ["pink_slime"],
        "rare": ["tentacle_blossom"],
        "weights": {"common": 0.0, "uncommon": 0.8, "rare": 0.2},
    },
    "copper_hill": {
        "common": ["goblin"],
        "uncommon": ["goblin_shaman", "mimic"],
        "rare": [],
        "weights": {"common": 0.6, "uncommon": 0.4, "rare": 0.0},
    },
    "tidepools": {
        "common": [],
        "uncommon": [],
        "rare": [],  # Peaceful area
        "weights": {"common": 0.0, "uncommon": 0.0, "rare": 0.0},
    },
}


# =============================================================================
# Helper Functions
# =============================================================================

def get_creature_template(creature_key):
    """Get a creature template by key."""
    return CREATURE_TEMPLATES.get(creature_key)


def get_spawn_table(area_key):
    """Get spawn table for an area."""
    return SPAWN_TABLES.get(area_key, {})


def roll_encounter(area_key):
    """
    Roll for a random encounter in an area.
    
    Returns:
        str or None: Creature key or None if no encounter
    """
    spawn_table = get_spawn_table(area_key)
    if not spawn_table:
        return None
    
    weights = spawn_table.get("weights", {})
    
    # Roll for rarity tier
    roll = random()
    cumulative = 0
    selected_tier = None
    
    for tier in ["rare", "uncommon", "common"]:
        cumulative += weights.get(tier, 0)
        if roll < cumulative:
            selected_tier = tier
            break
    
    if not selected_tier:
        return None
    
    # Get creatures from that tier
    creatures = spawn_table.get(selected_tier, [])
    if not creatures:
        # Fall back to lower tier
        for tier in ["common", "uncommon", "rare"]:
            creatures = spawn_table.get(tier, [])
            if creatures:
                break
    
    if not creatures:
        return None
    
    return choice(creatures)


def get_creature_stats(creature_key):
    """
    Get calculated stats for a creature.
    
    Returns dict with hp, stamina, composure, and combat values.
    """
    template = get_creature_template(creature_key)
    if not template:
        return None
    
    attrs = template.get("attributes", {})
    
    # Calculate pools similar to player
    hp = template.get("base_hp", 30)
    hp += attrs.get("endurance", 10) * 3
    hp += attrs.get("strength", 10)
    
    stamina = template.get("base_stamina", 30)
    stamina += attrs.get("endurance", 10) * 2
    stamina += attrs.get("agility", 10)
    
    composure = template.get("base_composure", 50)
    composure += attrs.get("willpower", 10) * 3
    
    return {
        "hp": hp,
        "max_hp": hp,
        "stamina": stamina,
        "max_stamina": stamina,
        "composure": composure,
        "max_composure": composure,
        "attributes": attrs,
        "skills": template.get("skills", {}),
        "attacks": template.get("attacks", []),
    }


def select_creature_attack(creature_key, target_state=None):
    """
    Select an attack for a creature based on AI and situation.
    
    Args:
        creature_key: The creature template key
        target_state: Optional state of target (grappled, etc.)
        
    Returns:
        dict: Selected attack data
    """
    template = get_creature_template(creature_key)
    if not template:
        return None
    
    attacks = template.get("attacks", [])
    if not attacks:
        return None
    
    # Filter by requirements
    available = []
    for attack in attacks:
        requires = attack.get("requires")
        if requires and target_state != requires:
            continue
        available.append(attack)
    
    if not available:
        available = attacks  # Fall back to all attacks
    
    # Weight by chance
    roll = random()
    cumulative = 0
    
    for attack in available:
        cumulative += attack.get("chance", 0.5)
        if roll < cumulative:
            return attack
    
    # Default to first available
    return available[0] if available else None


def calculate_creature_damage(creature_key, attack):
    """
    Calculate damage for a creature attack.
    
    Returns:
        tuple: (damage, damage_type)
    """
    template = get_creature_template(creature_key)
    if not template or not attack:
        return 0, "physical"
    
    damage_range = attack.get("damage", (5, 10))
    damage = randint(damage_range[0], damage_range[1])
    
    # Add attribute bonus
    attrs = template.get("attributes", {})
    damage_type = attack.get("damage_type", "physical")
    
    if damage_type == "physical":
        damage += (attrs.get("strength", 10) - 10) // 2
    elif damage_type in ["composure", "aphrodisiac"]:
        damage += (attrs.get("charisma", 10) - 10) // 2
    
    return damage, damage_type


def get_loot_drops(creature_key):
    """
    Roll for loot drops from a creature.
    
    Returns:
        list: [(item_key, amount), ...]
    """
    template = get_creature_template(creature_key)
    if not template:
        return []
    
    drops = []
    loot_table = template.get("loot", [])
    
    for loot in loot_table:
        if random() < loot.get("chance", 0.5):
            amount_range = loot.get("amount", (1, 1))
            amount = randint(amount_range[0], amount_range[1])
            drops.append((loot["item"], amount))
    
    return drops


def get_creature_exp(creature_key):
    """Get experience reward for defeating a creature."""
    template = get_creature_template(creature_key)
    if not template:
        return 0
    return template.get("exp_reward", 10)


def is_befriendable(creature_key):
    """Check if a creature can be befriended."""
    template = get_creature_template(creature_key)
    if not template:
        return False
    return template.get("befriendable", False)


def get_befriend_difficulty(creature_key):
    """Get difficulty to befriend a creature."""
    template = get_creature_template(creature_key)
    if not template:
        return 99
    return template.get("befriend_difficulty", 20)


def get_pack_size(creature_key):
    """Get number of creatures that spawn together."""
    template = get_creature_template(creature_key)
    if not template:
        return (1, 1)
    return template.get("pack_size", (1, 1))


def get_defeat_type(creature_key):
    """Get the defeat outcome type for a creature."""
    template = get_creature_template(creature_key)
    if not template:
        return "default"
    return template.get("defeat_type", "default")
