"""
Crafting System for Gilderhaven
================================

Comprehensive crafting with recipes, workstations, skills, and quality output.

Features:
- 7 crafting categories (alchemy, smithing, cooking, etc.)
- Workstation requirements
- Skill progression (0-100 per category)
- Quality system based on skill + materials
- Tool requirements
- Recipe discovery
- Quest integration

Usage:
    from world.crafting import (
        craft_item, can_craft, get_recipe,
        get_skill_level, add_skill_exp,
        get_available_recipes, discover_recipe
    )
    
    # Check if player can craft
    if can_craft(character, "health_potion"):
        result = craft_item(character, "health_potion")
    
    # Get recipes for a category
    recipes = get_available_recipes(character, category="alchemy")
"""

import random
from evennia.utils import logger


# =============================================================================
# Configuration
# =============================================================================

# Skill level ranges
MAX_SKILL = 100
SKILL_THRESHOLDS = {
    "novice": 0,
    "apprentice": 20,
    "journeyman": 40,
    "expert": 60,
    "master": 80,
    "grandmaster": 100,
}

# Quality tiers and their multipliers
QUALITY_TIERS = {
    "poor": {"multiplier": 0.5, "color": "|x", "min_roll": 0},
    "common": {"multiplier": 1.0, "color": "|w", "min_roll": 20},
    "fine": {"multiplier": 1.25, "color": "|g", "min_roll": 50},
    "excellent": {"multiplier": 1.5, "color": "|c", "min_roll": 75},
    "masterwork": {"multiplier": 2.0, "color": "|y", "min_roll": 95},
}

# Difficulty modifiers (subtracted from quality roll)
DIFFICULTY_MODIFIERS = {
    "trivial": 20,      # Bonus to roll
    "easy": 10,
    "normal": 0,
    "hard": -15,
    "expert": -30,
    "master": -50,
}

# Base exp per craft (modified by difficulty)
BASE_CRAFT_EXP = 10
EXP_PER_LEVEL = 100  # Exp needed per skill level


# =============================================================================
# Crafting Categories
# =============================================================================

CRAFTING_CATEGORIES = {
    "alchemy": {
        "name": "Alchemy",
        "desc": "Brew potions, elixirs, and magical concoctions.",
        "workstation": "alchemy_table",
        "primary_stat": "intelligence",
        "icon": "⚗️",
    },
    "smithing": {
        "name": "Smithing",
        "desc": "Forge metal tools, weapons, and armor.",
        "workstation": "forge",
        "primary_stat": "strength",
        "icon": "⚒️",
    },
    "cooking": {
        "name": "Cooking",
        "desc": "Prepare food and drinks with various effects.",
        "workstation": "cooking_fire",
        "primary_stat": "wisdom",
        "icon": "🍳",
    },
    "tailoring": {
        "name": "Tailoring",
        "desc": "Craft clothing and fabric items.",
        "workstation": "loom",
        "primary_stat": "dexterity",
        "icon": "🧵",
    },
    "woodworking": {
        "name": "Woodworking",
        "desc": "Carve wooden items and basic furniture.",
        "workstation": "workbench",
        "primary_stat": "dexterity",
        "icon": "🪵",
    },
    "jewelcrafting": {
        "name": "Jewelcrafting",
        "desc": "Create jewelry and cut gemstones.",
        "workstation": "jeweler_bench",
        "primary_stat": "dexterity",
        "icon": "💎",
    },
    "leatherworking": {
        "name": "Leatherworking",
        "desc": "Tan hides and craft leather goods.",
        "workstation": "tanning_rack",
        "primary_stat": "constitution",
        "icon": "🦴",
    },
}


# =============================================================================
# Workstation Templates
# =============================================================================

WORKSTATION_TEMPLATES = {
    "alchemy_table": {
        "key": "Alchemy Table",
        "desc": "A sturdy wooden table covered with vials, tubes, and a small burner. "
                "Various stains and scorch marks tell of countless experiments.",
        "category": "alchemy",
        "furniture_template": "alchemy_table",
    },
    "forge": {
        "key": "Blacksmith's Forge",
        "desc": "A roaring forge with bellows and an anvil nearby. The heat is intense, "
                "and the air smells of hot metal and coal.",
        "category": "smithing",
        "furniture_template": "forge",
    },
    "cooking_fire": {
        "key": "Cooking Fire",
        "desc": "A well-maintained fire pit with a grill and hanging pot. Perfect for "
                "preparing meals of all kinds.",
        "category": "cooking",
        "furniture_template": "cooking_fire",
    },
    "stove": {
        "key": "Kitchen Stove",
        "desc": "A proper kitchen stove with multiple burners and an oven. Much more "
                "sophisticated than a simple fire.",
        "category": "cooking",
        "furniture_template": "stove",
        "quality_bonus": 10,
    },
    "loom": {
        "key": "Weaving Loom",
        "desc": "A large wooden loom strung with threads. Foot pedals control the "
                "heddles while hands guide the shuttle.",
        "category": "tailoring",
        "furniture_template": "loom",
    },
    "sewing_table": {
        "key": "Sewing Table",
        "desc": "A well-lit table with drawers full of needles, thread, and fabric "
                "scraps. A pincushion sits within easy reach.",
        "category": "tailoring",
        "furniture_template": "sewing_table",
    },
    "workbench": {
        "key": "Workbench",
        "desc": "A heavy wooden workbench with vises, clamps, and tool racks. "
                "Wood shavings litter the floor beneath.",
        "category": "woodworking",
        "furniture_template": "workbench",
    },
    "jeweler_bench": {
        "key": "Jeweler's Bench",
        "desc": "A specialized bench with magnifying lenses, tiny tools, and a small "
                "torch for delicate metalwork.",
        "category": "jewelcrafting",
        "furniture_template": "jeweler_bench",
    },
    "tanning_rack": {
        "key": "Tanning Rack",
        "desc": "A wooden frame for stretching and treating hides. The smell of "
                "tanning chemicals is strong but not unpleasant.",
        "category": "leatherworking",
        "furniture_template": "tanning_rack",
    },
}


# =============================================================================
# Recipe Templates
# =============================================================================

# =============================================================================
# Recipe Discovery Sources
# =============================================================================
# "discovered_by_default": True  - Everyone knows this
# "discovery_source": "npc:Name" - Learned from talking to NPC
# "discovery_source": "skill:30" - Auto-learned at skill level 30
# "discovery_source": "scene:scene_key" - Learned from completing scene
# "discovery_source": "item:recipe_scroll" - Learned from using item
# No discovery = must be taught or found

RECIPE_TEMPLATES = {
    # =========================================================================
    # ALCHEMY - Whisper teaches advanced, basics are shop-bought
    # =========================================================================
    
    # --- Skill 0-15: Basic Brewing ---
    "herb_paste": {
        "name": "Herb Paste",
        "desc": "A basic herbal preparation. Foundation for many remedies.",
        "category": "alchemy",
        "skill_required": 0,
        "workstation": "alchemy_table",
        "ingredients": [
            {"item": "wild_herbs", "amount": 3},
        ],
        "tools": ["mortar_pestle"],
        "output": {"item": "herb_paste", "amount": 2},
        "difficulty": "trivial",
        "exp": 5,
        "discovered_by_default": True,
    },
    "healing_salve": {
        "name": "Healing Salve",
        "desc": "A topical ointment that speeds healing.",
        "category": "alchemy",
        "skill_required": 5,
        "workstation": "alchemy_table",
        "ingredients": [
            {"item": "herb_paste", "amount": 1},
            {"item": "honey", "amount": 1},
        ],
        "tools": [],
        "output": {"item": "healing_salve", "amount": 1},
        "difficulty": "easy",
        "exp": 8,
        "discovered_by_default": True,
    },
    "health_potion": {
        "name": "Health Potion",
        "desc": "A red potion that restores health.",
        "category": "alchemy",
        "skill_required": 10,
        "workstation": "alchemy_table",
        "ingredients": [
            {"item": "red_herb", "amount": 2},
            {"item": "herb_paste", "amount": 1},
            {"item": "empty_vial", "amount": 1},
        ],
        "tools": [],
        "output": {"item": "health_potion", "amount": 1},
        "difficulty": "easy",
        "exp": 12,
        "discovery_source": "npc:Whisper",  # Must learn from Whisper
    },
    "stamina_potion": {
        "name": "Stamina Potion",
        "desc": "A green potion that restores energy.",
        "category": "alchemy",
        "skill_required": 10,
        "workstation": "alchemy_table",
        "ingredients": [
            {"item": "green_herb", "amount": 2},
            {"item": "herb_paste", "amount": 1},
            {"item": "empty_vial", "amount": 1},
        ],
        "tools": [],
        "output": {"item": "stamina_potion", "amount": 1},
        "difficulty": "easy",
        "exp": 12,
        "discovery_source": "npc:Whisper",
    },
    
    # --- Skill 15-30: Intermediate ---
    "antidote": {
        "name": "Antidote",
        "desc": "Cures poison effects.",
        "category": "alchemy",
        "skill_required": 15,
        "workstation": "alchemy_table",
        "ingredients": [
            {"item": "bitter_root", "amount": 1},
            {"item": "green_herb", "amount": 1},
            {"item": "empty_vial", "amount": 1},
        ],
        "tools": ["mortar_pestle"],
        "output": {"item": "antidote", "amount": 1},
        "difficulty": "normal",
        "exp": 15,
        "discovery_source": "npc:Whisper",
    },
    "soothing_oil": {
        "name": "Soothing Oil",
        "desc": "A fragrant oil that relaxes muscles and calms nerves.",
        "category": "alchemy",
        "skill_required": 15,
        "workstation": "alchemy_table",
        "ingredients": [
            {"item": "wild_flowers", "amount": 3},
            {"item": "honey", "amount": 1},
        ],
        "tools": [],
        "output": {"item": "soothing_oil", "amount": 1},
        "difficulty": "normal",
        "exp": 15,
        "discovered_by_default": True,
    },
    "glowing_oil": {
        "name": "Glowing Oil",
        "desc": "An oil that makes skin glow faintly. Decorative.",
        "category": "alchemy",
        "skill_required": 20,
        "workstation": "alchemy_table",
        "ingredients": [
            {"item": "glowing_mushroom", "amount": 2},
            {"item": "soothing_oil", "amount": 1},
        ],
        "tools": [],
        "output": {"item": "glowing_oil", "amount": 1},
        "difficulty": "normal",
        "exp": 20,
        "discovery_source": "skill:20",  # Auto-learn at skill 20
    },
    "arousal_elixir": {
        "name": "Arousal Elixir",
        "desc": "A pink potion that heightens... sensitivity.",
        "category": "alchemy",
        "skill_required": 25,
        "workstation": "alchemy_table",
        "ingredients": [
            {"item": "passion_poppy", "amount": 3},
            {"item": "honey", "amount": 1},
            {"item": "empty_vial", "amount": 1},
        ],
        "tools": ["mortar_pestle"],
        "output": {"item": "arousal_elixir", "amount": 1},
        "difficulty": "normal",
        "exp": 25,
        "discovery_source": "scene:sunny_meadow_poppies_01",  # Found in poppy field
    },
    "numbing_cream": {
        "name": "Numbing Cream",
        "desc": "Reduces sensitivity temporarily. Has uses.",
        "category": "alchemy",
        "skill_required": 25,
        "workstation": "alchemy_table",
        "ingredients": [
            {"item": "bitter_root", "amount": 2},
            {"item": "herb_paste", "amount": 1},
        ],
        "tools": ["mortar_pestle"],
        "output": {"item": "numbing_cream", "amount": 1},
        "difficulty": "normal",
        "exp": 25,
        "discovery_source": "npc:Whisper",
    },
    
    # --- Skill 30-50: Advanced ---
    "glowing_potion": {
        "name": "Glowing Potion",
        "desc": "Makes the drinker glow faintly for a time.",
        "category": "alchemy",
        "skill_required": 30,
        "workstation": "alchemy_table",
        "ingredients": [
            {"item": "glowing_mushroom", "amount": 2},
            {"item": "glowing_algae", "amount": 1},
            {"item": "empty_vial", "amount": 1},
        ],
        "tools": [],
        "output": {"item": "glowing_potion", "amount": 1},
        "difficulty": "normal",
        "exp": 30,
        "discovery_source": "skill:30",
    },
    "heat_potion": {
        "name": "Heat Potion",
        "desc": "Induces artificial heat. Very potent.",
        "category": "alchemy",
        "skill_required": 35,
        "workstation": "alchemy_table",
        "ingredients": [
            {"item": "passion_poppy", "amount": 2},
            {"item": "beast_essence", "amount": 1},
            {"item": "arousal_elixir", "amount": 1},
        ],
        "tools": ["mortar_pestle"],
        "output": {"item": "heat_potion", "amount": 1},
        "difficulty": "hard",
        "exp": 40,
        "discovery_source": "npc:Curator",  # The Curator knows things
    },
    "obedience_draught": {
        "name": "Obedience Draught",
        "desc": "Increases suggestibility temporarily. Consent required.",
        "category": "alchemy",
        "skill_required": 40,
        "workstation": "alchemy_table",
        "ingredients": [
            {"item": "moon_lily", "amount": 1},
            {"item": "passion_poppy", "amount": 2},
            {"item": "honey", "amount": 2},
            {"item": "empty_vial", "amount": 1},
        ],
        "tools": ["mortar_pestle"],
        "output": {"item": "obedience_draught", "amount": 1},
        "difficulty": "hard",
        "exp": 45,
        "discovery_source": "npc:Curator",
    },
    "sensitivity_oil": {
        "name": "Sensitivity Oil",
        "desc": "Greatly heightens tactile sensitivity when applied.",
        "category": "alchemy",
        "skill_required": 40,
        "workstation": "alchemy_table",
        "ingredients": [
            {"item": "arousal_elixir", "amount": 1},
            {"item": "soothing_oil", "amount": 1},
            {"item": "passion_poppy", "amount": 1},
        ],
        "tools": [],
        "output": {"item": "sensitivity_oil", "amount": 1},
        "difficulty": "hard",
        "exp": 40,
        "discovery_source": "skill:40",
    },
    
    # --- Skill 50+: Expert ---
    "transformation_draught": {
        "name": "Transformation Draught",
        "desc": "Temporarily grants animal features.",
        "category": "alchemy",
        "skill_required": 50,
        "workstation": "alchemy_table",
        "ingredients": [
            {"item": "moon_lily", "amount": 2},
            {"item": "beast_essence", "amount": 1},
            {"item": "empty_vial", "amount": 1},
        ],
        "tools": ["mortar_pestle"],
        "output": {"item": "transformation_draught", "amount": 1},
        "difficulty": "hard",
        "exp": 50,
        "discovery_source": "npc:Curator",
    },
    "permanent_dye": {
        "name": "Permanent Dye",
        "desc": "Changes hair/fur color permanently until washed with solvent.",
        "category": "alchemy",
        "skill_required": 50,
        "workstation": "alchemy_table",
        "ingredients": [
            {"item": "wild_flowers", "amount": 5},
            {"item": "glowing_mushroom", "amount": 1},
            {"item": "empty_vial", "amount": 1},
        ],
        "tools": ["mortar_pestle"],
        "output": {"item": "permanent_dye", "amount": 1},
        "difficulty": "hard",
        "exp": 50,
        "discovery_source": "skill:50",
    },
    "lactation_elixir": {
        "name": "Lactation Elixir",
        "desc": "Induces or enhances milk production.",
        "category": "alchemy",
        "skill_required": 55,
        "workstation": "alchemy_table",
        "ingredients": [
            {"item": "moon_lily", "amount": 2},
            {"item": "honey", "amount": 3},
            {"item": "beast_essence", "amount": 1},
            {"item": "empty_vial", "amount": 1},
        ],
        "tools": ["mortar_pestle"],
        "output": {"item": "lactation_elixir", "amount": 1},
        "difficulty": "expert",
        "exp": 60,
        "discovery_source": "npc:Curator",
    },
    "virility_tonic": {
        "name": "Virility Tonic",
        "desc": "Greatly enhances... production and stamina.",
        "category": "alchemy",
        "skill_required": 55,
        "workstation": "alchemy_table",
        "ingredients": [
            {"item": "beast_essence", "amount": 2},
            {"item": "red_herb", "amount": 3},
            {"item": "passion_poppy", "amount": 2},
            {"item": "empty_vial", "amount": 1},
        ],
        "tools": ["mortar_pestle"],
        "output": {"item": "virility_tonic", "amount": 1},
        "difficulty": "expert",
        "exp": 60,
        "discovery_source": "npc:Curator",
    },
    "growth_formula": {
        "name": "Growth Formula",
        "desc": "Temporarily enhances specific body part size.",
        "category": "alchemy",
        "skill_required": 60,
        "workstation": "alchemy_table",
        "ingredients": [
            {"item": "beast_essence", "amount": 2},
            {"item": "moon_lily", "amount": 2},
            {"item": "glowing_mushroom", "amount": 2},
            {"item": "empty_vial", "amount": 1},
        ],
        "tools": ["mortar_pestle"],
        "output": {"item": "growth_formula", "amount": 1},
        "difficulty": "expert",
        "exp": 70,
        "discovery_source": "npc:Curator",
    },
    
    # =========================================================================
    # SMITHING - Greta sells basic tools, you craft upgrades and specialty
    # =========================================================================
    
    # --- Skill 0-15: Basic Metalwork ---
    "copper_ingot": {
        "name": "Copper Ingot",
        "desc": "A bar of refined copper.",
        "category": "smithing",
        "skill_required": 0,
        "workstation": "forge",
        "ingredients": [
            {"item": "copper_ore", "amount": 3},
            {"item": "coal", "amount": 1},
        ],
        "tools": [],
        "output": {"item": "copper_ingot", "amount": 1},
        "difficulty": "easy",
        "exp": 5,
        "discovered_by_default": True,
    },
    "fishing_hooks": {
        "name": "Fishing Hooks",
        "desc": "Bent metal hooks for fishing.",
        "category": "smithing",
        "skill_required": 5,
        "workstation": "forge",
        "ingredients": [
            {"item": "copper_ore", "amount": 1},
        ],
        "tools": [],
        "output": {"item": "fishing_hook", "amount": 5},
        "difficulty": "trivial",
        "exp": 3,
        "discovered_by_default": True,
    },
    "nails": {
        "name": "Iron Nails",
        "desc": "Basic iron nails for construction.",
        "category": "smithing",
        "skill_required": 10,
        "workstation": "forge",
        "ingredients": [
            {"item": "iron_ore", "amount": 1},
        ],
        "tools": ["smithing_hammer"],
        "output": {"item": "nails", "amount": 10},
        "difficulty": "trivial",
        "exp": 5,
        "discovered_by_default": True,
    },
    
    # --- Skill 15-30: Ingots and Repairs ---
    "iron_ingot": {
        "name": "Iron Ingot",
        "desc": "A bar of refined iron.",
        "category": "smithing",
        "skill_required": 15,
        "workstation": "forge",
        "ingredients": [
            {"item": "iron_ore", "amount": 3},
            {"item": "coal", "amount": 2},
        ],
        "tools": [],
        "output": {"item": "iron_ingot", "amount": 1},
        "difficulty": "normal",
        "exp": 10,
        "discovered_by_default": True,
    },
    "silver_ingot": {
        "name": "Silver Ingot",
        "desc": "A bar of refined silver.",
        "category": "smithing",
        "skill_required": 25,
        "workstation": "forge",
        "ingredients": [
            {"item": "silver_ore", "amount": 3},
            {"item": "coal", "amount": 2},
        ],
        "tools": [],
        "output": {"item": "silver_ingot", "amount": 1},
        "difficulty": "normal",
        "exp": 15,
        "discovery_source": "npc:Greta",  # Greta teaches smelting
    },
    "gold_ingot": {
        "name": "Gold Ingot",
        "desc": "A bar of refined gold.",
        "category": "smithing",
        "skill_required": 35,
        "workstation": "forge",
        "ingredients": [
            {"item": "gold_ore", "amount": 3},
            {"item": "coal", "amount": 3},
        ],
        "tools": [],
        "output": {"item": "gold_ingot", "amount": 1},
        "difficulty": "hard",
        "exp": 25,
        "discovery_source": "npc:Greta",
    },
    
    # --- Skill 25-40: Tool Upgrades (NOT basic tools - buy those from Greta) ---
    "reinforced_pickaxe": {
        "name": "Reinforced Pickaxe",
        "desc": "An upgraded pickaxe with better durability.",
        "category": "smithing",
        "skill_required": 25,
        "workstation": "forge",
        "ingredients": [
            {"item": "basic_pickaxe", "amount": 1},  # Upgrade existing
            {"item": "iron_ingot", "amount": 2},
        ],
        "tools": ["smithing_hammer"],
        "output": {"item": "quality_pickaxe", "amount": 1},
        "difficulty": "normal",
        "exp": 25,
        "discovery_source": "npc:Greta",
    },
    "reinforced_fishing_rod": {
        "name": "Reinforced Fishing Rod",
        "desc": "An upgraded rod with better line.",
        "category": "smithing",
        "skill_required": 25,
        "workstation": "forge",
        "ingredients": [
            {"item": "basic_fishing_rod", "amount": 1},
            {"item": "iron_ingot", "amount": 1},
            {"item": "silk", "amount": 2},
        ],
        "tools": ["smithing_hammer"],
        "output": {"item": "quality_fishing_rod", "amount": 1},
        "difficulty": "normal",
        "exp": 25,
        "discovery_source": "npc:Greta",
    },
    
    # --- Skill 30-50: Specialty Metal Items ---
    "chains": {
        "name": "Metal Chains",
        "desc": "Sturdy metal chains. Many uses.",
        "category": "smithing",
        "skill_required": 30,
        "workstation": "forge",
        "ingredients": [
            {"item": "iron_ingot", "amount": 2},
        ],
        "tools": ["smithing_hammer"],
        "output": {"item": "chains", "amount": 1},
        "difficulty": "normal",
        "exp": 25,
        "discovery_source": "skill:30",
    },
    "metal_ring": {
        "name": "Metal Ring",
        "desc": "A simple iron ring. Component for other items.",
        "category": "smithing",
        "skill_required": 30,
        "workstation": "forge",
        "ingredients": [
            {"item": "iron_ingot", "amount": 1},
        ],
        "tools": ["smithing_hammer"],
        "output": {"item": "metal_ring", "amount": 3},
        "difficulty": "normal",
        "exp": 20,
        "discovered_by_default": True,
    },
    "shackles": {
        "name": "Shackles",
        "desc": "Restraints for wrists or ankles.",
        "category": "smithing",
        "skill_required": 35,
        "workstation": "forge",
        "ingredients": [
            {"item": "iron_ingot", "amount": 2},
            {"item": "chains", "amount": 1},
        ],
        "tools": ["smithing_hammer"],
        "output": {"item": "shackles", "amount": 1},
        "difficulty": "hard",
        "exp": 35,
        "discovery_source": "npc:Curator",
    },
    "spreader_bar": {
        "name": "Spreader Bar",
        "desc": "A rigid bar with cuffs at each end.",
        "category": "smithing",
        "skill_required": 40,
        "workstation": "forge",
        "ingredients": [
            {"item": "iron_ingot", "amount": 3},
            {"item": "leather", "amount": 2},
        ],
        "tools": ["smithing_hammer"],
        "output": {"item": "spreader_bar", "amount": 1},
        "difficulty": "hard",
        "exp": 40,
        "discovery_source": "npc:Curator",
    },
    "cage_frame": {
        "name": "Cage Frame",
        "desc": "Metal framework for a small cage.",
        "category": "smithing",
        "skill_required": 45,
        "workstation": "forge",
        "ingredients": [
            {"item": "iron_ingot", "amount": 6},
            {"item": "chains", "amount": 2},
        ],
        "tools": ["smithing_hammer"],
        "output": {"item": "cage_frame", "amount": 1},
        "difficulty": "hard",
        "exp": 50,
        "discovery_source": "npc:Curator",
    },
    "bell_collar": {
        "name": "Bell Collar",
        "desc": "A metal collar with a small bell attached.",
        "category": "smithing",
        "skill_required": 35,
        "workstation": "forge",
        "ingredients": [
            {"item": "silver_ingot", "amount": 1},
            {"item": "iron_ingot", "amount": 1},
        ],
        "tools": ["smithing_hammer"],
        "output": {"item": "bell_collar", "amount": 1},
        "difficulty": "normal",
        "exp": 35,
        "discovery_source": "skill:35",
    },
    
    # --- Skill 50+: Master Smithing ---
    "master_pickaxe": {
        "name": "Master Pickaxe",
        "desc": "A masterwork pickaxe that makes mining effortless.",
        "category": "smithing",
        "skill_required": 50,
        "workstation": "forge",
        "ingredients": [
            {"item": "quality_pickaxe", "amount": 1},
            {"item": "silver_ingot", "amount": 2},
            {"item": "iron_ingot", "amount": 3},
        ],
        "tools": ["smithing_hammer"],
        "output": {"item": "master_pickaxe", "amount": 1},
        "difficulty": "expert",
        "exp": 60,
        "discovery_source": "npc:Greta",
    },
    "chastity_cage": {
        "name": "Chastity Cage",
        "desc": "A locking device for denial play.",
        "category": "smithing",
        "skill_required": 55,
        "workstation": "forge",
        "ingredients": [
            {"item": "silver_ingot", "amount": 2},
            {"item": "iron_ingot", "amount": 1},
        ],
        "tools": ["smithing_hammer"],
        "output": {"item": "chastity_cage", "amount": 1},
        "difficulty": "expert",
        "exp": 60,
        "discovery_source": "npc:Curator",
    },
    "branding_iron": {
        "name": "Branding Iron",
        "desc": "A custom branding iron. Handle with extreme care.",
        "category": "smithing",
        "skill_required": 60,
        "workstation": "forge",
        "ingredients": [
            {"item": "iron_ingot", "amount": 3},
            {"item": "wood", "amount": 1},
        ],
        "tools": ["smithing_hammer"],
        "output": {"item": "branding_iron", "amount": 1},
        "difficulty": "master",
        "exp": 75,
        "discovery_source": "npc:Curator",
    },
    
    # =========================================================================
    # COOKING - Tom sells basic food, you craft specialty/buff food
    # =========================================================================
    
    # --- Skill 0-15: Basic Cooking ---
    "cooked_fish": {
        "name": "Cooked Fish",
        "desc": "A simply prepared fish.",
        "category": "cooking",
        "skill_required": 0,
        "workstation": "cooking_fire",
        "ingredients": [
            {"item": "raw_fish", "amount": 1},
        ],
        "tools": [],
        "output": {"item": "cooked_fish", "amount": 1},
        "difficulty": "trivial",
        "exp": 3,
        "discovered_by_default": True,
    },
    "roasted_mushrooms": {
        "name": "Roasted Mushrooms",
        "desc": "Simple roasted mushrooms.",
        "category": "cooking",
        "skill_required": 0,
        "workstation": "cooking_fire",
        "ingredients": [
            {"item": "edible_mushrooms", "amount": 3},
        ],
        "tools": [],
        "output": {"item": "roasted_mushrooms", "amount": 1},
        "difficulty": "trivial",
        "exp": 3,
        "discovered_by_default": True,
    },
    "trail_rations": {
        "name": "Trail Rations",
        "desc": "Simple preserved food for travel.",
        "category": "cooking",
        "skill_required": 5,
        "workstation": "cooking_fire",
        "ingredients": [
            {"item": "wild_berries", "amount": 2},
            {"item": "forest_nuts", "amount": 2},
            {"item": "honey", "amount": 1},
        ],
        "tools": [],
        "output": {"item": "trail_rations", "amount": 3},
        "difficulty": "easy",
        "exp": 8,
        "discovered_by_default": True,
    },
    
    # --- Skill 15-30: Intermediate Cooking ---
    "herb_bread": {
        "name": "Herb Bread",
        "desc": "Fresh bread with herbs baked in. Slight healing effect.",
        "category": "cooking",
        "skill_required": 15,
        "workstation": "cooking_fire",
        "ingredients": [
            {"item": "flour", "amount": 2},
            {"item": "green_herb", "amount": 1},
            {"item": "water", "amount": 1},
        ],
        "tools": [],
        "output": {"item": "herb_bread", "amount": 2},
        "difficulty": "easy",
        "exp": 12,
        "discovery_source": "npc:Big Tom",
    },
    "honey_cake": {
        "name": "Honey Cake",
        "desc": "A sweet cake drizzled with honey. Restores energy.",
        "category": "cooking",
        "skill_required": 20,
        "workstation": "cooking_fire",
        "ingredients": [
            {"item": "flour", "amount": 2},
            {"item": "honey", "amount": 2},
            {"item": "egg", "amount": 1},
        ],
        "tools": [],
        "output": {"item": "honey_cake", "amount": 1},
        "difficulty": "normal",
        "exp": 20,
        "discovery_source": "npc:Big Tom",
    },
    "fish_soup": {
        "name": "Fish Soup",
        "desc": "A warming fish soup. Good for cold weather.",
        "category": "cooking",
        "skill_required": 20,
        "workstation": "cooking_fire",
        "ingredients": [
            {"item": "raw_fish", "amount": 2},
            {"item": "wild_herbs", "amount": 1},
            {"item": "water", "amount": 1},
        ],
        "tools": ["cooking_pot"],
        "output": {"item": "fish_soup", "amount": 1},
        "difficulty": "normal",
        "exp": 18,
        "discovered_by_default": True,
    },
    
    # --- Skill 25-40: Specialty Foods ---
    "seafood_stew": {
        "name": "Seafood Stew",
        "desc": "A hearty stew of ocean bounty. Stamina boost.",
        "category": "cooking",
        "skill_required": 25,
        "workstation": "cooking_fire",
        "ingredients": [
            {"item": "raw_fish", "amount": 2},
            {"item": "mussel", "amount": 3},
            {"item": "seaweed", "amount": 1},
            {"item": "water", "amount": 1},
        ],
        "tools": ["cooking_pot"],
        "output": {"item": "seafood_stew", "amount": 1},
        "difficulty": "normal",
        "exp": 28,
        "discovery_source": "skill:25",
    },
    "energy_bar": {
        "name": "Energy Bar",
        "desc": "A dense, portable food that restores stamina quickly.",
        "category": "cooking",
        "skill_required": 25,
        "workstation": None,  # Hand-craftable
        "ingredients": [
            {"item": "forest_nuts", "amount": 3},
            {"item": "honey", "amount": 2},
            {"item": "wild_berries", "amount": 2},
        ],
        "tools": [],
        "output": {"item": "energy_bar", "amount": 2},
        "difficulty": "normal",
        "exp": 22,
        "discovered_by_default": True,
    },
    "chocolate_truffle": {
        "name": "Chocolate Truffle",
        "desc": "Rich chocolate confection. Mood enhancer.",
        "category": "cooking",
        "skill_required": 30,
        "workstation": "cooking_fire",
        "ingredients": [
            {"item": "chocolate", "amount": 2},
            {"item": "honey", "amount": 1},
        ],
        "tools": [],
        "output": {"item": "chocolate_truffle", "amount": 3},
        "difficulty": "normal",
        "exp": 25,
        "discovery_source": "npc:Big Tom",
    },
    
    # --- Skill 35-50: Aphrodisiac and Special Foods ---
    "aphrodisiac_treat": {
        "name": "Aphrodisiac Treat",
        "desc": "A confection with... interesting effects.",
        "category": "cooking",
        "skill_required": 35,
        "workstation": "cooking_fire",
        "ingredients": [
            {"item": "honey", "amount": 2},
            {"item": "passion_poppy", "amount": 2},
            {"item": "chocolate", "amount": 1},
        ],
        "tools": [],
        "output": {"item": "aphrodisiac_treat", "amount": 2},
        "difficulty": "hard",
        "exp": 35,
        "discovery_source": "scene:sunny_meadow_poppies_01",
    },
    "stamina_feast": {
        "name": "Stamina Feast",
        "desc": "A full meal that greatly extends endurance.",
        "category": "cooking",
        "skill_required": 40,
        "workstation": "stove",  # Requires better equipment
        "ingredients": [
            {"item": "raw_fish", "amount": 2},
            {"item": "egg", "amount": 2},
            {"item": "green_herb", "amount": 2},
            {"item": "honey", "amount": 1},
        ],
        "tools": ["cooking_pot"],
        "output": {"item": "stamina_feast", "amount": 1},
        "difficulty": "hard",
        "exp": 45,
        "discovery_source": "npc:Big Tom",
    },
    "lovers_chocolate": {
        "name": "Lover's Chocolate",
        "desc": "Exquisite chocolate infused with... special ingredients.",
        "category": "cooking",
        "skill_required": 45,
        "workstation": "stove",
        "ingredients": [
            {"item": "chocolate", "amount": 3},
            {"item": "passion_poppy", "amount": 2},
            {"item": "honey", "amount": 2},
            {"item": "moon_lily", "amount": 1},
        ],
        "tools": [],
        "output": {"item": "lovers_chocolate", "amount": 2},
        "difficulty": "hard",
        "exp": 50,
        "discovery_source": "npc:Curator",
    },
    "beast_treat": {
        "name": "Beast Treat",
        "desc": "A treat that temporarily enhances animal instincts.",
        "category": "cooking",
        "skill_required": 50,
        "workstation": "stove",
        "ingredients": [
            {"item": "beast_essence", "amount": 1},
            {"item": "raw_fish", "amount": 2},
            {"item": "honey", "amount": 2},
        ],
        "tools": ["cooking_pot"],
        "output": {"item": "beast_treat", "amount": 1},
        "difficulty": "expert",
        "exp": 55,
        "discovery_source": "npc:Curator",
    },
    
    # =========================================================================
    # TAILORING - Fiber from gathering, cloth and specialty from crafting
    # =========================================================================
    
    # --- Skill 0-15: Basic Fiber Work ---
    "rope": {
        "name": "Rope",
        "desc": "Strong rope woven from fibers.",
        "category": "tailoring",
        "skill_required": 0,
        "workstation": None,  # Hand-craftable
        "ingredients": [
            {"item": "fiber", "amount": 5},
        ],
        "tools": [],
        "output": {"item": "rope", "amount": 1},
        "difficulty": "trivial",
        "exp": 3,
        "discovered_by_default": True,
    },
    "cloth": {
        "name": "Cloth",
        "desc": "A bolt of basic fabric.",
        "category": "tailoring",
        "skill_required": 5,
        "workstation": "loom",
        "ingredients": [
            {"item": "fiber", "amount": 5},
        ],
        "tools": [],
        "output": {"item": "cloth", "amount": 1},
        "difficulty": "easy",
        "exp": 5,
        "discovered_by_default": True,
    },
    "bandages": {
        "name": "Bandages",
        "desc": "Clean cloth bandages for wounds.",
        "category": "tailoring",
        "skill_required": 5,
        "workstation": None,
        "ingredients": [
            {"item": "cloth", "amount": 1},
        ],
        "tools": [],
        "output": {"item": "bandages", "amount": 3},
        "difficulty": "trivial",
        "exp": 3,
        "discovered_by_default": True,
    },
    
    # --- Skill 15-30: Clothing ---
    "simple_clothing": {
        "name": "Simple Clothing",
        "desc": "Basic but functional garments.",
        "category": "tailoring",
        "skill_required": 15,
        "workstation": "loom",
        "ingredients": [
            {"item": "cloth", "amount": 3},
        ],
        "tools": ["sewing_kit"],
        "output": {"item": "simple_clothing", "amount": 1},
        "difficulty": "easy",
        "exp": 15,
        "discovered_by_default": True,
    },
    "blindfold": {
        "name": "Blindfold",
        "desc": "A soft blindfold that blocks vision completely.",
        "category": "tailoring",
        "skill_required": 15,
        "workstation": None,
        "ingredients": [
            {"item": "cloth", "amount": 1},
            {"item": "silk", "amount": 1},
        ],
        "tools": ["sewing_kit"],
        "output": {"item": "blindfold", "amount": 1},
        "difficulty": "easy",
        "exp": 15,
        "discovery_source": "skill:15",
    },
    "gag": {
        "name": "Cloth Gag",
        "desc": "A simple cloth gag. Muffles speech.",
        "category": "tailoring",
        "skill_required": 15,
        "workstation": None,
        "ingredients": [
            {"item": "cloth", "amount": 1},
            {"item": "rope", "amount": 1},
        ],
        "tools": [],
        "output": {"item": "gag", "amount": 1},
        "difficulty": "easy",
        "exp": 12,
        "discovery_source": "npc:Curator",
    },
    
    # --- Skill 25-40: Silk and Specialty ---
    "silk_cloth": {
        "name": "Silk Fabric",
        "desc": "Fine woven silk. Luxurious.",
        "category": "tailoring",
        "skill_required": 25,
        "workstation": "loom",
        "ingredients": [
            {"item": "spider_silk", "amount": 5},
        ],
        "tools": [],
        "output": {"item": "silk", "amount": 1},
        "difficulty": "normal",
        "exp": 20,
        "discovered_by_default": True,
    },
    "silk_rope": {
        "name": "Silk Rope",
        "desc": "Soft but strong rope. Doesn't leave marks.",
        "category": "tailoring",
        "skill_required": 30,
        "workstation": "loom",
        "ingredients": [
            {"item": "silk", "amount": 3},
        ],
        "tools": [],
        "output": {"item": "silk_rope", "amount": 1},
        "difficulty": "normal",
        "exp": 25,
        "discovery_source": "skill:30",
    },
    "lace": {
        "name": "Lace",
        "desc": "Delicate lace fabric for fine clothing.",
        "category": "tailoring",
        "skill_required": 35,
        "workstation": "loom",
        "ingredients": [
            {"item": "silk", "amount": 2},
            {"item": "fiber", "amount": 3},
        ],
        "tools": ["sewing_kit"],
        "output": {"item": "lace", "amount": 1},
        "difficulty": "hard",
        "exp": 30,
        "discovery_source": "skill:35",
    },
    "elegant_dress": {
        "name": "Elegant Dress",
        "desc": "A beautiful formal dress.",
        "category": "tailoring",
        "skill_required": 40,
        "workstation": "loom",
        "ingredients": [
            {"item": "silk", "amount": 3},
            {"item": "lace", "amount": 1},
        ],
        "tools": ["sewing_kit"],
        "output": {"item": "elegant_dress", "amount": 1},
        "difficulty": "hard",
        "exp": 40,
        "discovery_source": "skill:40",
    },
    
    # --- Skill 40+: Adult Items ---
    "lingerie": {
        "name": "Lingerie",
        "desc": "Delicate, revealing undergarments.",
        "category": "tailoring",
        "skill_required": 40,
        "workstation": "loom",
        "ingredients": [
            {"item": "silk", "amount": 2},
            {"item": "lace", "amount": 1},
        ],
        "tools": ["sewing_kit"],
        "output": {"item": "lingerie", "amount": 1},
        "difficulty": "hard",
        "exp": 40,
        "discovery_source": "npc:Curator",
    },
    "corset": {
        "name": "Corset",
        "desc": "A structured corset that shapes the figure.",
        "category": "tailoring",
        "skill_required": 45,
        "workstation": "loom",
        "ingredients": [
            {"item": "cloth", "amount": 3},
            {"item": "silk", "amount": 1},
            {"item": "metal_ring", "amount": 6},
        ],
        "tools": ["sewing_kit"],
        "output": {"item": "corset", "amount": 1},
        "difficulty": "hard",
        "exp": 50,
        "discovery_source": "npc:Curator",
    },
    "maid_outfit": {
        "name": "Maid Outfit",
        "desc": "A classic maid uniform. Short skirt optional.",
        "category": "tailoring",
        "skill_required": 45,
        "workstation": "loom",
        "ingredients": [
            {"item": "cloth", "amount": 4},
            {"item": "lace", "amount": 2},
        ],
        "tools": ["sewing_kit"],
        "output": {"item": "maid_outfit", "amount": 1},
        "difficulty": "hard",
        "exp": 50,
        "discovery_source": "npc:Curator",
    },
    "pet_costume": {
        "name": "Pet Costume",
        "desc": "A costume with ears, tail, and paw mittens.",
        "category": "tailoring",
        "skill_required": 50,
        "workstation": "loom",
        "ingredients": [
            {"item": "cloth", "amount": 2},
            {"item": "silk", "amount": 1},
            {"item": "leather", "amount": 2},
        ],
        "tools": ["sewing_kit"],
        "output": {"item": "pet_costume", "amount": 1},
        "difficulty": "expert",
        "exp": 55,
        "discovery_source": "npc:Curator",
    },
    
    # =========================================================================
    # WOODWORKING - Wood from gathering, items and furniture crafted
    # =========================================================================
    
    # --- Skill 0-15: Basic Wood ---
    "plank": {
        "name": "Wooden Plank",
        "desc": "A cut and smoothed plank of wood.",
        "category": "woodworking",
        "skill_required": 0,
        "workstation": "workbench",
        "ingredients": [
            {"item": "wood", "amount": 1},
        ],
        "tools": [],
        "output": {"item": "plank", "amount": 2},
        "difficulty": "trivial",
        "exp": 2,
        "discovered_by_default": True,
    },
    "handle": {
        "name": "Wooden Handle",
        "desc": "A shaped wooden handle for tools.",
        "category": "woodworking",
        "skill_required": 5,
        "workstation": "workbench",
        "ingredients": [
            {"item": "wood", "amount": 1},
        ],
        "tools": [],
        "output": {"item": "handle", "amount": 2},
        "difficulty": "trivial",
        "exp": 3,
        "discovered_by_default": True,
    },
    "bug_net": {
        "name": "Bug Net",
        "desc": "A net for catching insects.",
        "category": "woodworking",
        "skill_required": 10,
        "workstation": None,
        "ingredients": [
            {"item": "wood", "amount": 1},
            {"item": "fiber", "amount": 3},
        ],
        "tools": [],
        "output": {"item": "bug_net", "amount": 1},
        "difficulty": "easy",
        "exp": 10,
        "discovered_by_default": True,
    },
    "fishing_rod": {
        "name": "Basic Fishing Rod",
        "desc": "A basic fishing rod. Functional but simple.",
        "category": "woodworking",
        "skill_required": 15,
        "workstation": "workbench",
        "ingredients": [
            {"item": "wood", "amount": 2},
            {"item": "fiber", "amount": 3},
            {"item": "fishing_hook", "amount": 1},
        ],
        "tools": [],
        "output": {"item": "basic_fishing_rod", "amount": 1},
        "difficulty": "easy",
        "exp": 15,
        "discovered_by_default": True,
    },
    
    # --- Skill 20-35: Furniture Basics ---
    "wooden_box": {
        "name": "Wooden Box",
        "desc": "A simple storage box.",
        "category": "woodworking",
        "skill_required": 15,
        "workstation": "workbench",
        "ingredients": [
            {"item": "plank", "amount": 4},
            {"item": "nails", "amount": 8},
        ],
        "tools": ["carpentry_tools"],
        "output": {"item": "wooden_box", "amount": 1},
        "difficulty": "easy",
        "exp": 15,
        "discovered_by_default": True,
    },
    "wooden_chair": {
        "name": "Wooden Chair",
        "desc": "A simple but sturdy chair.",
        "category": "woodworking",
        "skill_required": 25,
        "workstation": "workbench",
        "ingredients": [
            {"item": "plank", "amount": 4},
            {"item": "nails", "amount": 10},
        ],
        "tools": ["carpentry_tools"],
        "output": {"item": "wooden_chair", "amount": 1},
        "output_type": "furniture",
        "difficulty": "normal",
        "exp": 25,
        "discovered_by_default": True,
    },
    "wooden_table": {
        "name": "Wooden Table",
        "desc": "A functional wooden table.",
        "category": "woodworking",
        "skill_required": 30,
        "workstation": "workbench",
        "ingredients": [
            {"item": "plank", "amount": 6},
            {"item": "nails", "amount": 12},
        ],
        "tools": ["carpentry_tools"],
        "output": {"item": "wooden_table", "amount": 1},
        "output_type": "furniture",
        "difficulty": "normal",
        "exp": 30,
        "discovered_by_default": True,
    },
    "bed_frame": {
        "name": "Simple Bed Frame",
        "desc": "A basic bed frame. Add bedding separately.",
        "category": "woodworking",
        "skill_required": 35,
        "workstation": "workbench",
        "ingredients": [
            {"item": "plank", "amount": 8},
            {"item": "nails", "amount": 16},
            {"item": "rope", "amount": 2},
        ],
        "tools": ["carpentry_tools"],
        "output": {"item": "simple_bed", "amount": 1},
        "output_type": "furniture",
        "difficulty": "normal",
        "exp": 35,
        "discovery_source": "skill:35",
    },
    
    # --- Skill 35-50: Specialty Items ---
    "paddle": {
        "name": "Paddle",
        "desc": "A wooden paddle. For... rowing.",
        "category": "woodworking",
        "skill_required": 20,
        "workstation": "workbench",
        "ingredients": [
            {"item": "plank", "amount": 2},
        ],
        "tools": ["carpentry_tools"],
        "output": {"item": "paddle", "amount": 1},
        "difficulty": "easy",
        "exp": 15,
        "discovery_source": "npc:Curator",
    },
    "spanking_bench": {
        "name": "Spanking Bench",
        "desc": "A padded bench designed for... discipline.",
        "category": "woodworking",
        "skill_required": 45,
        "workstation": "workbench",
        "ingredients": [
            {"item": "plank", "amount": 10},
            {"item": "leather", "amount": 3},
            {"item": "nails", "amount": 20},
        ],
        "tools": ["carpentry_tools"],
        "output": {"item": "spanking_bench", "amount": 1},
        "output_type": "furniture",
        "difficulty": "hard",
        "exp": 50,
        "discovery_source": "npc:Curator",
    },
    "stocks": {
        "name": "Stocks",
        "desc": "Wooden restraints for public display.",
        "category": "woodworking",
        "skill_required": 45,
        "workstation": "workbench",
        "ingredients": [
            {"item": "plank", "amount": 8},
            {"item": "iron_ingot", "amount": 2},
            {"item": "nails", "amount": 16},
        ],
        "tools": ["carpentry_tools"],
        "output": {"item": "stocks", "amount": 1},
        "output_type": "furniture",
        "difficulty": "hard",
        "exp": 50,
        "discovery_source": "npc:Curator",
    },
    "st_andrews_cross": {
        "name": "St. Andrew's Cross",
        "desc": "An X-shaped frame with restraint points.",
        "category": "woodworking",
        "skill_required": 55,
        "workstation": "workbench",
        "ingredients": [
            {"item": "plank", "amount": 12},
            {"item": "leather", "amount": 4},
            {"item": "metal_ring", "amount": 8},
            {"item": "nails", "amount": 24},
        ],
        "tools": ["carpentry_tools"],
        "output": {"item": "st_andrews_cross", "amount": 1},
        "output_type": "furniture",
        "difficulty": "expert",
        "exp": 65,
        "discovery_source": "npc:Curator",
    },
    
    # =========================================================================
    # JEWELCRAFTING - Gems from mining, jewelry crafted
    # =========================================================================
    
    # --- Skill 0-15: Basic Gemwork ---
    "cut_gem": {
        "name": "Cut Gemstone",
        "desc": "A properly cut and polished gem.",
        "category": "jewelcrafting",
        "skill_required": 10,
        "workstation": "jeweler_bench",
        "ingredients": [
            {"item": "rough_gem", "amount": 1},
        ],
        "tools": ["jeweler_tools"],
        "output": {"item": "cut_gem", "amount": 1},
        "difficulty": "normal",
        "exp": 12,
        "discovered_by_default": True,
    },
    "simple_pendant": {
        "name": "Simple Pendant",
        "desc": "A basic metal pendant on a chain.",
        "category": "jewelcrafting",
        "skill_required": 15,
        "workstation": "jeweler_bench",
        "ingredients": [
            {"item": "copper_ingot", "amount": 1},
            {"item": "chains", "amount": 1},
        ],
        "tools": ["jeweler_tools"],
        "output": {"item": "simple_pendant", "amount": 1},
        "difficulty": "easy",
        "exp": 15,
        "discovered_by_default": True,
    },
    
    # --- Skill 20-35: Silver Work ---
    "silver_ring": {
        "name": "Silver Ring",
        "desc": "A simple silver band.",
        "category": "jewelcrafting",
        "skill_required": 20,
        "workstation": "jeweler_bench",
        "ingredients": [
            {"item": "silver_ingot", "amount": 1},
        ],
        "tools": ["jeweler_tools"],
        "output": {"item": "silver_ring", "amount": 1},
        "difficulty": "normal",
        "exp": 20,
        "discovered_by_default": True,
    },
    "silver_bracelet": {
        "name": "Silver Bracelet",
        "desc": "An elegant silver bracelet.",
        "category": "jewelcrafting",
        "skill_required": 25,
        "workstation": "jeweler_bench",
        "ingredients": [
            {"item": "silver_ingot", "amount": 2},
        ],
        "tools": ["jeweler_tools"],
        "output": {"item": "silver_bracelet", "amount": 1},
        "difficulty": "normal",
        "exp": 25,
        "discovery_source": "skill:25",
    },
    "gem_ring": {
        "name": "Gemmed Ring",
        "desc": "A ring set with a beautiful gemstone.",
        "category": "jewelcrafting",
        "skill_required": 35,
        "workstation": "jeweler_bench",
        "ingredients": [
            {"item": "silver_ingot", "amount": 1},
            {"item": "cut_gem", "amount": 1},
        ],
        "tools": ["jeweler_tools"],
        "output": {"item": "gem_ring", "amount": 1},
        "difficulty": "hard",
        "exp": 40,
        "discovery_source": "skill:35",
    },
    
    # --- Skill 30-50: Collars and Adult Jewelry ---
    "collar": {
        "name": "Leather Collar",
        "desc": "A decorative collar with a ring for attachments.",
        "category": "jewelcrafting",
        "skill_required": 30,
        "workstation": "jeweler_bench",
        "ingredients": [
            {"item": "silver_ingot", "amount": 1},
            {"item": "leather", "amount": 2},
            {"item": "metal_ring", "amount": 1},
        ],
        "tools": ["jeweler_tools"],
        "output": {"item": "collar", "amount": 1},
        "difficulty": "normal",
        "exp": 30,
        "discovery_source": "npc:Curator",
    },
    "ornate_collar": {
        "name": "Ornate Collar",
        "desc": "A beautiful collar with gem inlays.",
        "category": "jewelcrafting",
        "skill_required": 45,
        "workstation": "jeweler_bench",
        "ingredients": [
            {"item": "silver_ingot", "amount": 2},
            {"item": "leather", "amount": 2},
            {"item": "cut_gem", "amount": 2},
            {"item": "metal_ring", "amount": 1},
        ],
        "tools": ["jeweler_tools"],
        "output": {"item": "ornate_collar", "amount": 1},
        "difficulty": "hard",
        "exp": 50,
        "discovery_source": "npc:Curator",
    },
    "nipple_jewelry": {
        "name": "Nipple Jewelry",
        "desc": "Decorative piercings or clamps.",
        "category": "jewelcrafting",
        "skill_required": 30,
        "workstation": "jeweler_bench",
        "ingredients": [
            {"item": "silver_ingot", "amount": 1},
        ],
        "tools": ["jeweler_tools"],
        "output": {"item": "nipple_jewelry", "amount": 1},
        "difficulty": "normal",
        "exp": 30,
        "discovery_source": "npc:Curator",
    },
    "clit_jewelry": {
        "name": "Intimate Jewelry",
        "desc": "Delicate jewelry for intimate piercings.",
        "category": "jewelcrafting",
        "skill_required": 40,
        "workstation": "jeweler_bench",
        "ingredients": [
            {"item": "silver_ingot", "amount": 1},
            {"item": "cut_gem", "amount": 1},
        ],
        "tools": ["jeweler_tools"],
        "output": {"item": "intimate_jewelry", "amount": 1},
        "difficulty": "hard",
        "exp": 45,
        "discovery_source": "npc:Curator",
    },
    "ankle_bells": {
        "name": "Ankle Bells",
        "desc": "Decorative bells that chime with movement.",
        "category": "jewelcrafting",
        "skill_required": 25,
        "workstation": "jeweler_bench",
        "ingredients": [
            {"item": "silver_ingot", "amount": 1},
            {"item": "chains", "amount": 1},
        ],
        "tools": ["jeweler_tools"],
        "output": {"item": "ankle_bells", "amount": 1},
        "difficulty": "normal",
        "exp": 25,
        "discovery_source": "skill:25",
    },
    "ownership_tag": {
        "name": "Ownership Tag",
        "desc": "A metal tag that can be engraved with a name.",
        "category": "jewelcrafting",
        "skill_required": 35,
        "workstation": "jeweler_bench",
        "ingredients": [
            {"item": "silver_ingot", "amount": 1},
        ],
        "tools": ["jeweler_tools"],
        "output": {"item": "ownership_tag", "amount": 1},
        "difficulty": "normal",
        "exp": 35,
        "discovery_source": "npc:Curator",
    },
    
    # =========================================================================
    # LEATHERWORKING - Hides from future hunting, leather goods crafted
    # =========================================================================
    
    # --- Skill 0-15: Basic Leather ---
    "leather": {
        "name": "Leather",
        "desc": "Tanned and treated hide.",
        "category": "leatherworking",
        "skill_required": 0,
        "workstation": "tanning_rack",
        "ingredients": [
            {"item": "hide", "amount": 1},
            {"item": "salt", "amount": 1},
        ],
        "tools": [],
        "output": {"item": "leather", "amount": 1},
        "difficulty": "easy",
        "exp": 8,
        "discovered_by_default": True,
    },
    "leather_strips": {
        "name": "Leather Strips",
        "desc": "Thin strips of leather for crafting.",
        "category": "leatherworking",
        "skill_required": 5,
        "workstation": None,
        "ingredients": [
            {"item": "leather", "amount": 1},
        ],
        "tools": ["leatherworking_tools"],
        "output": {"item": "leather_strips", "amount": 4},
        "difficulty": "trivial",
        "exp": 3,
        "discovered_by_default": True,
    },
    "leather_belt": {
        "name": "Leather Belt",
        "desc": "A sturdy leather belt.",
        "category": "leatherworking",
        "skill_required": 10,
        "workstation": None,
        "ingredients": [
            {"item": "leather", "amount": 1},
            {"item": "metal_ring", "amount": 1},
        ],
        "tools": ["leatherworking_tools"],
        "output": {"item": "leather_belt", "amount": 1},
        "difficulty": "easy",
        "exp": 10,
        "discovered_by_default": True,
    },
    
    # --- Skill 15-30: Gear and Accessories ---
    "leather_gloves": {
        "name": "Leather Gloves",
        "desc": "Sturdy leather work gloves.",
        "category": "leatherworking",
        "skill_required": 15,
        "workstation": None,
        "ingredients": [
            {"item": "leather", "amount": 2},
        ],
        "tools": ["leatherworking_tools"],
        "output": {"item": "leather_gloves", "amount": 1},
        "difficulty": "easy",
        "exp": 15,
        "discovered_by_default": True,
    },
    "leather_armor": {
        "name": "Leather Armor",
        "desc": "Basic protective leather gear.",
        "category": "leatherworking",
        "skill_required": 25,
        "workstation": "tanning_rack",
        "ingredients": [
            {"item": "leather", "amount": 4},
            {"item": "fiber", "amount": 2},
        ],
        "tools": ["leatherworking_tools"],
        "output": {"item": "leather_armor", "amount": 1},
        "difficulty": "normal",
        "exp": 30,
        "discovered_by_default": True,
    },
    "satchel": {
        "name": "Leather Satchel",
        "desc": "A sturdy bag for carrying items.",
        "category": "leatherworking",
        "skill_required": 20,
        "workstation": None,
        "ingredients": [
            {"item": "leather", "amount": 3},
            {"item": "metal_ring", "amount": 2},
        ],
        "tools": ["leatherworking_tools"],
        "output": {"item": "satchel", "amount": 1},
        "difficulty": "normal",
        "exp": 22,
        "discovery_source": "skill:20",
    },
    
    # --- Skill 25-40: Restraints ---
    "leash": {
        "name": "Leash",
        "desc": "A leather lead with a sturdy clasp.",
        "category": "leatherworking",
        "skill_required": 20,
        "workstation": None,
        "ingredients": [
            {"item": "leather", "amount": 1},
            {"item": "metal_ring", "amount": 2},
        ],
        "tools": ["leatherworking_tools"],
        "output": {"item": "leash", "amount": 1},
        "difficulty": "easy",
        "exp": 18,
        "discovery_source": "npc:Curator",
    },
    "leather_cuffs": {
        "name": "Leather Cuffs",
        "desc": "Padded leather restraints for wrists.",
        "category": "leatherworking",
        "skill_required": 25,
        "workstation": None,
        "ingredients": [
            {"item": "leather", "amount": 2},
            {"item": "metal_ring", "amount": 2},
        ],
        "tools": ["leatherworking_tools"],
        "output": {"item": "leather_cuffs", "amount": 1},
        "difficulty": "normal",
        "exp": 25,
        "discovery_source": "npc:Curator",
    },
    "ankle_cuffs": {
        "name": "Ankle Cuffs",
        "desc": "Padded leather restraints for ankles.",
        "category": "leatherworking",
        "skill_required": 25,
        "workstation": None,
        "ingredients": [
            {"item": "leather", "amount": 2},
            {"item": "metal_ring", "amount": 2},
        ],
        "tools": ["leatherworking_tools"],
        "output": {"item": "ankle_cuffs", "amount": 1},
        "difficulty": "normal",
        "exp": 25,
        "discovery_source": "npc:Curator",
    },
    "blindfold_leather": {
        "name": "Leather Blindfold",
        "desc": "A padded leather blindfold. Complete darkness.",
        "category": "leatherworking",
        "skill_required": 25,
        "workstation": None,
        "ingredients": [
            {"item": "leather", "amount": 1},
            {"item": "cloth", "amount": 1},
        ],
        "tools": ["leatherworking_tools"],
        "output": {"item": "leather_blindfold", "amount": 1},
        "difficulty": "normal",
        "exp": 22,
        "discovery_source": "skill:25",
    },
    "ball_gag": {
        "name": "Ball Gag",
        "desc": "A leather strap with a ball for the mouth.",
        "category": "leatherworking",
        "skill_required": 30,
        "workstation": None,
        "ingredients": [
            {"item": "leather", "amount": 1},
            {"item": "rubber_ball", "amount": 1},
        ],
        "tools": ["leatherworking_tools"],
        "output": {"item": "ball_gag", "amount": 1},
        "difficulty": "normal",
        "exp": 28,
        "discovery_source": "npc:Curator",
    },
    
    # --- Skill 40+: Advanced Restraints ---
    "harness": {
        "name": "Body Harness",
        "desc": "A leather harness with multiple attachment points.",
        "category": "leatherworking",
        "skill_required": 40,
        "workstation": "tanning_rack",
        "ingredients": [
            {"item": "leather", "amount": 4},
            {"item": "metal_ring", "amount": 6},
        ],
        "tools": ["leatherworking_tools"],
        "output": {"item": "harness", "amount": 1},
        "difficulty": "hard",
        "exp": 45,
        "discovery_source": "npc:Curator",
    },
    "posture_collar": {
        "name": "Posture Collar",
        "desc": "A tall collar that restricts head movement.",
        "category": "leatherworking",
        "skill_required": 45,
        "workstation": "tanning_rack",
        "ingredients": [
            {"item": "leather", "amount": 3},
            {"item": "metal_ring", "amount": 2},
            {"item": "iron_ingot", "amount": 1},
        ],
        "tools": ["leatherworking_tools"],
        "output": {"item": "posture_collar", "amount": 1},
        "difficulty": "hard",
        "exp": 50,
        "discovery_source": "npc:Curator",
    },
    "pony_harness": {
        "name": "Pony Harness",
        "desc": "A full harness set for pony play.",
        "category": "leatherworking",
        "skill_required": 55,
        "workstation": "tanning_rack",
        "ingredients": [
            {"item": "leather", "amount": 6},
            {"item": "metal_ring", "amount": 8},
            {"item": "chains", "amount": 1},
        ],
        "tools": ["leatherworking_tools"],
        "output": {"item": "pony_harness", "amount": 1},
        "difficulty": "expert",
        "exp": 65,
        "discovery_source": "npc:Curator",
    },
    "bondage_hood": {
        "name": "Bondage Hood",
        "desc": "A full head covering with optional blindfold and gag attachments.",
        "category": "leatherworking",
        "skill_required": 60,
        "workstation": "tanning_rack",
        "ingredients": [
            {"item": "leather", "amount": 4},
            {"item": "cloth", "amount": 2},
            {"item": "metal_ring", "amount": 4},
        ],
        "tools": ["leatherworking_tools"],
        "output": {"item": "bondage_hood", "amount": 1},
        "difficulty": "expert",
        "exp": 70,
        "discovery_source": "npc:Curator",
    },
}


# =============================================================================
# Helper Functions - Skills
# =============================================================================

def get_skill_level(character, category):
    """
    Get character's skill level in a crafting category.
    
    Args:
        character: The character
        category: Crafting category key
        
    Returns:
        int: Skill level (0-100)
    """
    skills = character.db.crafting_skills or {}
    return skills.get(category, 0)


def get_skill_exp(character, category):
    """Get current exp in a crafting category."""
    exp = character.db.crafting_exp or {}
    return exp.get(category, 0)


def get_skill_title(level):
    """Get skill title for a level."""
    for title, threshold in sorted(SKILL_THRESHOLDS.items(), key=lambda x: -x[1]):
        if level >= threshold:
            return title
    return "novice"


def add_skill_exp(character, category, amount):
    """
    Add experience to a crafting skill.
    
    Args:
        character: The character
        category: Crafting category key
        amount: Exp to add
        
    Returns:
        tuple: (new_level, leveled_up)
    """
    if category not in CRAFTING_CATEGORIES:
        return (0, False)
    
    # Initialize if needed
    if not character.db.crafting_skills:
        character.db.crafting_skills = {}
    if not character.db.crafting_exp:
        character.db.crafting_exp = {}
    
    current_level = character.db.crafting_skills.get(category, 0)
    current_exp = character.db.crafting_exp.get(category, 0)
    
    if current_level >= MAX_SKILL:
        return (current_level, False)
    
    new_exp = current_exp + amount
    leveled_up = False
    
    # Check for level up
    while new_exp >= EXP_PER_LEVEL and current_level < MAX_SKILL:
        new_exp -= EXP_PER_LEVEL
        current_level += 1
        leveled_up = True
    
    character.db.crafting_skills[category] = current_level
    character.db.crafting_exp[category] = new_exp
    
    return (current_level, leveled_up)


def get_all_skills(character):
    """Get all crafting skills for a character."""
    skills = character.db.crafting_skills or {}
    result = {}
    for category in CRAFTING_CATEGORIES:
        result[category] = {
            "level": skills.get(category, 0),
            "exp": (character.db.crafting_exp or {}).get(category, 0),
            "title": get_skill_title(skills.get(category, 0)),
        }
    return result


# =============================================================================
# Helper Functions - Recipes
# =============================================================================

def get_recipe(recipe_key):
    """Get a recipe by key."""
    return RECIPE_TEMPLATES.get(recipe_key)


def get_recipes_by_category(category):
    """Get all recipes in a category."""
    return {
        k: v for k, v in RECIPE_TEMPLATES.items()
        if v.get("category") == category
    }


def has_discovered_recipe(character, recipe_key):
    """
    Check if character has discovered a recipe.
    
    Discovery sources:
    - "discovered_by_default": True = everyone knows
    - "discovery_source": "skill:30" = auto-learn at skill 30
    - "discovery_source": "npc:Name" = must talk to NPC
    - "discovery_source": "scene:key" = complete scene
    - "discovery_source": "item:key" = use recipe item
    - No source = must be explicitly taught
    """
    recipe = get_recipe(recipe_key)
    if not recipe:
        return False
    
    # Default discovered recipes
    if recipe.get("discovered_by_default", False):
        return True
    
    # Check explicitly discovered list
    discovered = character.db.discovered_recipes or []
    if recipe_key in discovered:
        return True
    
    # Check skill-based auto-discovery
    discovery_source = recipe.get("discovery_source", "")
    if discovery_source.startswith("skill:"):
        try:
            required_skill = int(discovery_source.split(":")[1])
            category = recipe.get("category")
            current_skill = get_skill_level(character, category)
            if current_skill >= required_skill:
                return True
        except (ValueError, IndexError):
            pass
    
    return False


def discover_recipe(character, recipe_key):
    """
    Mark a recipe as discovered for a character.
    
    Returns:
        bool: True if newly discovered, False if already known
    """
    # Check if already known
    recipe = get_recipe(recipe_key)
    if not recipe:
        return False
    
    if recipe.get("discovered_by_default", False):
        return False  # Already known by default
    
    discovered = character.db.discovered_recipes or []
    if recipe_key in discovered:
        return False  # Already discovered
    
    if not character.db.discovered_recipes:
        character.db.discovered_recipes = []
    
    character.db.discovered_recipes.append(recipe_key)
    return True


def get_discovery_hint(recipe_key):
    """
    Get a hint about how to discover a recipe.
    
    Returns:
        str: Hint text or empty string if unknown
    """
    recipe = get_recipe(recipe_key)
    if not recipe:
        return ""
    
    if recipe.get("discovered_by_default", False):
        return "Known by default."
    
    source = recipe.get("discovery_source", "")
    
    if source.startswith("npc:"):
        npc_name = source.split(":")[1]
        return f"Talk to {npc_name} to learn this recipe."
    
    if source.startswith("skill:"):
        skill_level = source.split(":")[1]
        category = recipe.get("category", "unknown")
        cat_name = CRAFTING_CATEGORIES.get(category, {}).get("name", category)
        return f"Learned automatically at {cat_name} skill {skill_level}."
    
    if source.startswith("scene:"):
        return "Discovered through exploration."
    
    if source.startswith("item:"):
        return "Learned from a recipe scroll or book."
    
    return "Must be discovered or taught."


def teach_npc_recipes(character, npc_name):
    """
    Teach all recipes from a specific NPC.
    Call this when finishing dialogue with an NPC.
    
    Args:
        character: The character learning
        npc_name: The NPC name (from discovery_source)
        
    Returns:
        list: Names of newly learned recipes
    """
    learned = []
    
    for recipe_key, recipe in RECIPE_TEMPLATES.items():
        source = recipe.get("discovery_source", "")
        if source == f"npc:{npc_name}":
            # Check if they meet skill requirement
            category = recipe.get("category")
            required_skill = recipe.get("skill_required", 0)
            current_skill = get_skill_level(character, category)
            
            if current_skill >= required_skill:
                if discover_recipe(character, recipe_key):
                    learned.append(recipe.get("name", recipe_key))
    
    return learned


def teach_scene_recipes(character, scene_key):
    """
    Teach recipes discovered from a scene.
    Call this when completing a scene.
    
    Args:
        character: The character
        scene_key: The scene that was completed
        
    Returns:
        list: Names of newly learned recipes
    """
    learned = []
    
    for recipe_key, recipe in RECIPE_TEMPLATES.items():
        source = recipe.get("discovery_source", "")
        if source == f"scene:{scene_key}":
            if discover_recipe(character, recipe_key):
                learned.append(recipe.get("name", recipe_key))
    
    return learned


def get_available_recipes(character, category=None):
    """
    Get all recipes available to a character.
    
    Args:
        character: The character
        category: Optional category filter
        
    Returns:
        dict: Available recipes keyed by recipe_key
    """
    available = {}
    
    for recipe_key, recipe in RECIPE_TEMPLATES.items():
        # Category filter
        if category and recipe.get("category") != category:
            continue
        
        # Must be discovered
        if not has_discovered_recipe(character, recipe_key):
            continue
        
        available[recipe_key] = recipe
    
    return available


# =============================================================================
# Helper Functions - Workstations
# =============================================================================

def get_workstation(room, category):
    """
    Find a workstation of a given category in a room.
    
    Args:
        room: The room to search
        category: Crafting category
        
    Returns:
        Object or None: The workstation object
    """
    for obj in room.contents:
        ws_type = obj.db.workstation_type
        if ws_type:
            ws_data = WORKSTATION_TEMPLATES.get(ws_type, {})
            if ws_data.get("category") == category:
                return obj
    return None


def has_workstation(room, workstation_key):
    """Check if a specific workstation type exists in room."""
    for obj in room.contents:
        if obj.db.workstation_type == workstation_key:
            return True
    return False


def get_workstation_bonus(workstation):
    """Get quality bonus from a workstation."""
    if not workstation:
        return 0
    ws_type = workstation.db.workstation_type
    ws_data = WORKSTATION_TEMPLATES.get(ws_type, {})
    return ws_data.get("quality_bonus", 0)


# =============================================================================
# Helper Functions - Inventory Checks
# =============================================================================

def has_ingredients(character, recipe):
    """
    Check if character has all required ingredients.
    
    Returns:
        tuple: (has_all, missing_list)
    """
    ingredients = recipe.get("ingredients", [])
    missing = []
    
    inventory = character.db.inventory or []
    
    for req in ingredients:
        item_key = req["item"]
        amount_needed = req["amount"]
        
        # Count items in inventory
        count = 0
        for item in inventory:
            if item.db.item_key == item_key:
                count += item.db.stack_count or 1
        
        if count < amount_needed:
            missing.append({
                "item": item_key,
                "have": count,
                "need": amount_needed,
            })
    
    return (len(missing) == 0, missing)


def has_tools(character, recipe):
    """
    Check if character has required tools equipped or in inventory.
    
    Returns:
        tuple: (has_all, missing_list)
    """
    tools_needed = recipe.get("tools", [])
    if not tools_needed:
        return (True, [])
    
    missing = []
    inventory = character.db.inventory or []
    equipment = character.db.equipment or {}
    
    for tool_key in tools_needed:
        found = False
        
        # Check inventory
        for item in inventory:
            if item.db.item_key == tool_key or item.db.tool_type == tool_key:
                found = True
                break
        
        # Check equipment
        if not found:
            for slot, item in equipment.items():
                if item and (item.db.item_key == tool_key or item.db.tool_type == tool_key):
                    found = True
                    break
        
        if not found:
            missing.append(tool_key)
    
    return (len(missing) == 0, missing)


def consume_ingredients(character, recipe):
    """
    Remove ingredients from inventory.
    
    Args:
        character: The character
        recipe: Recipe dict
        
    Returns:
        bool: Success
    """
    ingredients = recipe.get("ingredients", [])
    inventory = character.db.inventory or []
    
    for req in ingredients:
        item_key = req["item"]
        amount_needed = req["amount"]
        
        remaining = amount_needed
        to_remove = []
        
        for item in inventory:
            if item.db.item_key == item_key and remaining > 0:
                stack = item.db.stack_count or 1
                if stack <= remaining:
                    to_remove.append(item)
                    remaining -= stack
                else:
                    item.db.stack_count = stack - remaining
                    remaining = 0
        
        # Remove items
        for item in to_remove:
            inventory.remove(item)
            item.delete()
    
    character.db.inventory = inventory
    return True


# =============================================================================
# Core Crafting Functions
# =============================================================================

def can_craft(character, recipe_key, room=None):
    """
    Check if a character can craft a recipe.
    
    Args:
        character: The character
        recipe_key: Recipe template key
        room: Optional room (uses character's location if not provided)
        
    Returns:
        tuple: (can_craft, reason_if_not)
    """
    recipe = get_recipe(recipe_key)
    if not recipe:
        return (False, "Unknown recipe.")
    
    room = room or character.location
    
    # Check if discovered
    if not has_discovered_recipe(character, recipe_key):
        return (False, "You haven't learned this recipe yet.")
    
    # Check skill level
    category = recipe.get("category")
    skill_required = recipe.get("skill_required", 0)
    current_skill = get_skill_level(character, category)
    
    if current_skill < skill_required:
        return (False, f"Requires {category} skill {skill_required} (you have {current_skill}).")
    
    # Check workstation
    workstation_key = recipe.get("workstation")
    if workstation_key:
        if not has_workstation(room, workstation_key):
            ws_name = WORKSTATION_TEMPLATES.get(workstation_key, {}).get("key", workstation_key)
            return (False, f"Requires a {ws_name}.")
    
    # Check ingredients
    has_ing, missing_ing = has_ingredients(character, recipe)
    if not has_ing:
        missing_str = ", ".join(f"{m['need']}x {m['item']}" for m in missing_ing)
        return (False, f"Missing ingredients: {missing_str}")
    
    # Check tools
    has_tool, missing_tools = has_tools(character, recipe)
    if not has_tool:
        return (False, f"Missing tools: {', '.join(missing_tools)}")
    
    return (True, "")


def calculate_quality(character, recipe, workstation=None):
    """
    Calculate output quality for a craft.
    
    Args:
        character: The character
        recipe: Recipe dict
        workstation: Optional workstation object
        
    Returns:
        str: Quality tier key
    """
    category = recipe.get("category")
    difficulty = recipe.get("difficulty", "normal")
    
    # Base roll
    skill_level = get_skill_level(character, category)
    base_roll = random.randint(1, 100)
    
    # Skill bonus (higher skill = more consistent)
    skill_bonus = skill_level // 2
    
    # Difficulty modifier
    diff_mod = DIFFICULTY_MODIFIERS.get(difficulty, 0)
    
    # Workstation bonus
    ws_bonus = get_workstation_bonus(workstation) if workstation else 0
    
    # Final roll
    final_roll = base_roll + skill_bonus + diff_mod + ws_bonus
    final_roll = max(0, min(100, final_roll))
    
    # Determine quality
    result_quality = "poor"
    for quality, data in sorted(QUALITY_TIERS.items(), key=lambda x: -x[1]["min_roll"]):
        if final_roll >= data["min_roll"]:
            result_quality = quality
            break
    
    return result_quality


def craft_item(character, recipe_key, room=None):
    """
    Attempt to craft an item.
    
    Args:
        character: The character
        recipe_key: Recipe template key
        room: Optional room
        
    Returns:
        dict: Result with keys: success, message, item, quality, exp_gained, leveled_up
    """
    # Validate
    can, reason = can_craft(character, recipe_key, room)
    if not can:
        return {
            "success": False,
            "message": reason,
            "item": None,
            "quality": None,
            "exp_gained": 0,
            "leveled_up": False,
        }
    
    recipe = get_recipe(recipe_key)
    room = room or character.location
    category = recipe.get("category")
    
    # Get workstation
    workstation = None
    workstation_key = recipe.get("workstation")
    if workstation_key:
        workstation = get_workstation(room, category)
    
    # Consume ingredients
    consume_ingredients(character, recipe)
    
    # Calculate quality
    quality = calculate_quality(character, recipe, workstation)
    quality_data = QUALITY_TIERS[quality]
    
    # Create output item(s)
    output = recipe.get("output", {})
    output_key = output.get("item")
    output_amount = output.get("amount", 1)
    output_type = recipe.get("output_type", "item")
    
    created_items = []
    
    if output_type == "furniture":
        # Create furniture
        try:
            from world.furniture import create_furniture
            for _ in range(output_amount):
                furn = create_furniture(output_key)
                if furn:
                    furn.db.quality = quality
                    furn.db.crafter = character.key
                    # Add to room
                    furn.location = room
                    created_items.append(furn)
        except ImportError:
            pass
    else:
        # Create items
        try:
            from world.items import create_item
            for _ in range(output_amount):
                item = create_item(output_key)
                if item:
                    item.db.quality = quality
                    item.db.crafter = character.key
                    # Add to inventory
                    if not character.db.inventory:
                        character.db.inventory = []
                    character.db.inventory.append(item)
                    created_items.append(item)
        except ImportError:
            # Fallback if items module not available
            pass
    
    # Grant exp
    base_exp = recipe.get("exp", BASE_CRAFT_EXP)
    exp_gained = base_exp
    new_level, leveled_up = add_skill_exp(character, category, exp_gained)
    
    # Build result message
    item_name = recipe.get("name", output_key)
    quality_color = quality_data["color"]
    
    if output_amount > 1:
        msg = f"You craft {output_amount}x {quality_color}{quality}|n {item_name}!"
    else:
        msg = f"You craft a {quality_color}{quality}|n {item_name}!"
    
    if leveled_up:
        cat_name = CRAFTING_CATEGORIES[category]["name"]
        msg += f"\n|y{cat_name} skill increased to {new_level}!|n"
    
    return {
        "success": True,
        "message": msg,
        "items": created_items,
        "quality": quality,
        "exp_gained": exp_gained,
        "leveled_up": leveled_up,
        "new_level": new_level if leveled_up else None,
    }


# =============================================================================
# Display Functions
# =============================================================================

def get_recipe_display(recipe_key, character=None):
    """
    Get formatted display for a recipe.
    
    Args:
        recipe_key: Recipe key
        character: Optional character (for skill comparison)
        
    Returns:
        str: Formatted recipe display
    """
    recipe = get_recipe(recipe_key)
    if not recipe:
        return "Unknown recipe."
    
    lines = []
    lines.append(f"|w{recipe['name']}|n")
    lines.append(f"|x{recipe.get('desc', '')}|n")
    lines.append("")
    
    # Category and difficulty
    cat_data = CRAFTING_CATEGORIES.get(recipe.get("category", ""), {})
    cat_name = cat_data.get("name", recipe.get("category", "Unknown"))
    difficulty = recipe.get("difficulty", "normal").title()
    lines.append(f"Category: |c{cat_name}|n  Difficulty: |y{difficulty}|n")
    
    # Skill requirement
    skill_req = recipe.get("skill_required", 0)
    if character:
        current = get_skill_level(character, recipe.get("category"))
        if current >= skill_req:
            lines.append(f"Skill Required: |g{skill_req}|n (you have {current})")
        else:
            lines.append(f"Skill Required: |r{skill_req}|n (you have {current})")
    else:
        lines.append(f"Skill Required: {skill_req}")
    
    # Workstation
    ws_key = recipe.get("workstation")
    if ws_key:
        ws_name = WORKSTATION_TEMPLATES.get(ws_key, {}).get("key", ws_key)
        lines.append(f"Workstation: |c{ws_name}|n")
    else:
        lines.append("Workstation: |gNone (hand-craft)|n")
    
    # Ingredients
    lines.append("")
    lines.append("|wIngredients:|n")
    for ing in recipe.get("ingredients", []):
        item_key = ing["item"]
        amount = ing["amount"]
        lines.append(f"  • {amount}x {item_key}")
    
    # Tools
    tools = recipe.get("tools", [])
    if tools:
        lines.append("")
        lines.append("|wTools Required:|n")
        for tool in tools:
            lines.append(f"  • {tool}")
    
    # Output
    output = recipe.get("output", {})
    output_amount = output.get("amount", 1)
    lines.append("")
    lines.append(f"|wProduces:|n {output_amount}x {output.get('item', 'unknown')}")
    
    return "\n".join(lines)


def get_skill_display(character, category=None):
    """
    Get formatted skill display.
    
    Args:
        character: The character
        category: Optional specific category
        
    Returns:
        str: Formatted display
    """
    lines = []
    lines.append("|w=== Crafting Skills ===|n")
    lines.append("")
    
    skills = get_all_skills(character)
    
    categories_to_show = [category] if category else CRAFTING_CATEGORIES.keys()
    
    for cat_key in categories_to_show:
        if cat_key not in CRAFTING_CATEGORIES:
            continue
        
        cat_data = CRAFTING_CATEGORIES[cat_key]
        skill_data = skills.get(cat_key, {"level": 0, "exp": 0, "title": "novice"})
        
        icon = cat_data.get("icon", "•")
        name = cat_data.get("name", cat_key)
        level = skill_data["level"]
        exp = skill_data["exp"]
        title = skill_data["title"].title()
        
        # Progress bar
        progress = int((exp / EXP_PER_LEVEL) * 10)
        bar = "|g" + "█" * progress + "|x" + "░" * (10 - progress) + "|n"
        
        lines.append(f"{icon} |c{name}|n: {level} ({title})")
        lines.append(f"   {bar} {exp}/{EXP_PER_LEVEL} exp")
    
    return "\n".join(lines)


def get_category_recipe_list(character, category):
    """
    Get list of recipes in a category for a character.
    
    Args:
        character: The character
        category: Category key
        
    Returns:
        str: Formatted list
    """
    recipes = get_available_recipes(character, category=category)
    
    if not recipes:
        return "No recipes discovered in this category."
    
    lines = []
    cat_data = CRAFTING_CATEGORIES.get(category, {})
    lines.append(f"|w=== {cat_data.get('name', category)} Recipes ===|n")
    lines.append("")
    
    skill_level = get_skill_level(character, category)
    
    # Sort by skill requirement
    sorted_recipes = sorted(recipes.items(), key=lambda x: x[1].get("skill_required", 0))
    
    for recipe_key, recipe in sorted_recipes:
        name = recipe.get("name", recipe_key)
        req = recipe.get("skill_required", 0)
        difficulty = recipe.get("difficulty", "normal")
        
        # Color based on skill
        if skill_level >= req:
            skill_color = "|g"
        else:
            skill_color = "|r"
        
        diff_colors = {
            "trivial": "|x",
            "easy": "|g",
            "normal": "|w",
            "hard": "|y",
            "expert": "|r",
            "master": "|m",
        }
        diff_color = diff_colors.get(difficulty, "|w")
        
        lines.append(f"  {recipe_key}: |w{name}|n")
        lines.append(f"      {skill_color}Skill {req}|n | {diff_color}{difficulty.title()}|n")
    
    return "\n".join(lines)


# =============================================================================
# Quest Integration
# =============================================================================

def check_craft_objective(character, recipe_key, amount=1):
    """
    Check quest objectives for crafting.
    Called after successful craft.
    
    Args:
        character: The character
        recipe_key: What was crafted
        amount: How many
    """
    try:
        from world.quests import check_objective
        check_objective(character, "craft", item=recipe_key, amount=amount)
    except ImportError:
        pass


# =============================================================================
# Initialization
# =============================================================================

def initialize_crafting(character):
    """
    Initialize crafting data for a new character.
    
    Args:
        character: The character
    """
    if not character.db.crafting_skills:
        character.db.crafting_skills = {}
    
    if not character.db.crafting_exp:
        character.db.crafting_exp = {}
    
    if not character.db.discovered_recipes:
        character.db.discovered_recipes = []
