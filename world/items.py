"""
Item System for Gilderhaven
============================

Comprehensive item management with:
- Item templates (data-driven definitions)
- Item creation and management
- Tool requirements for gathering
- Consumables with effects
- Equipment slots
- Item quality/durability
- Stacking for materials

Architecture:
- Items are Objects with item_data attribute
- Templates define base properties
- Instances can have unique qualities
- Integration with gathering, shops, effects

Usage:
    from world.items import (
        create_item, get_item_template, is_item,
        use_item, get_item_value, has_tool
    )
    
    # Create from template
    item = create_item("iron_ore", location=player)
    
    # Check if player has required tool
    if has_tool(player, "pickaxe"):
        # Can mine
    
    # Use a consumable
    use_item(player, health_potion)
"""

import random
from evennia import create_object, search_object
from evennia.utils import logger


# =============================================================================
# Item Categories
# =============================================================================

ITEM_CATEGORIES = {
    "material": "Raw materials from gathering",
    "tool": "Tools for gathering and crafting",
    "consumable": "Food, potions, and other usables",
    "equipment": "Wearable gear",
    "furniture_item": "Portable furniture (see furniture system)",
    "currency": "Money and valuables",
    "quest": "Quest-related items",
    "key": "Keys and access items",
    "container": "Bags and storage",
    "junk": "Low-value miscellaneous items",
    "treasure": "Valuable collectibles",
    "adult": "Adult-themed items",
}


# =============================================================================
# Item Quality
# =============================================================================

ITEM_QUALITIES = {
    "poor": {"name": "Poor", "color": "|x", "value_mult": 0.5, "durability_mult": 0.5},
    "common": {"name": "Common", "color": "|w", "value_mult": 1.0, "durability_mult": 1.0},
    "uncommon": {"name": "Uncommon", "color": "|g", "value_mult": 1.5, "durability_mult": 1.25},
    "rare": {"name": "Rare", "color": "|b", "value_mult": 2.5, "durability_mult": 1.5},
    "epic": {"name": "Epic", "color": "|m", "value_mult": 5.0, "durability_mult": 2.0},
    "legendary": {"name": "Legendary", "color": "|y", "value_mult": 10.0, "durability_mult": 3.0},
}


# =============================================================================
# Equipment Slots
# =============================================================================

EQUIPMENT_SLOTS = {
    "head": "Head",
    "neck": "Neck",
    "chest": "Chest",
    "back": "Back",
    "hands": "Hands",
    "waist": "Waist",
    "legs": "Legs",
    "feet": "Feet",
    "finger_l": "Left Finger",
    "finger_r": "Right Finger",
    "main_hand": "Main Hand",
    "off_hand": "Off Hand",
    "two_hand": "Two Hands",
}


# =============================================================================
# Item Templates - Materials
# =============================================================================

MATERIAL_TEMPLATES = {
    # Foraged Materials
    "wild_herbs": {
        "key": "bundle of wild herbs",
        "aliases": ["herbs", "wild herbs"],
        "desc": "A bundle of assorted wild herbs, fragrant and fresh.",
        "category": "material",
        "subcategory": "herb",
        "base_value": 5,
        "weight": 0.1,
        "stackable": True,
        "max_stack": 50,
    },
    "medicinal_roots": {
        "key": "medicinal roots",
        "aliases": ["roots"],
        "desc": "Gnarled roots with known healing properties.",
        "category": "material",
        "subcategory": "herb",
        "base_value": 12,
        "weight": 0.2,
        "stackable": True,
        "max_stack": 50,
    },
    "wild_berries": {
        "key": "handful of wild berries",
        "aliases": ["berries", "wild berries"],
        "desc": "Small, ripe berries. Safe to eat, mildly sweet.",
        "category": "material",
        "subcategory": "food_raw",
        "base_value": 3,
        "weight": 0.1,
        "stackable": True,
        "max_stack": 50,
        "edible": True,
        "hunger_restore": 5,
    },
    "edible_mushrooms": {
        "key": "edible mushrooms",
        "aliases": ["mushrooms"],
        "desc": "Common forest mushrooms, good for cooking.",
        "category": "material",
        "subcategory": "food_raw",
        "base_value": 4,
        "weight": 0.1,
        "stackable": True,
        "max_stack": 50,
        "edible": True,
        "hunger_restore": 8,
    },
    "glowing_mushroom": {
        "key": "glowing mushroom",
        "aliases": ["glowing mushrooms", "glow mushroom"],
        "desc": "A mushroom that emits a soft, ethereal glow. Alchemically valuable.",
        "category": "material",
        "subcategory": "herb",
        "base_value": 25,
        "weight": 0.1,
        "stackable": True,
        "max_stack": 20,
        "flags": ["magical"],
    },
    "wild_flowers": {
        "key": "wild flowers",
        "aliases": ["flowers"],
        "desc": "A small bouquet of colorful wildflowers.",
        "category": "material",
        "subcategory": "misc",
        "base_value": 2,
        "weight": 0.1,
        "stackable": True,
        "max_stack": 50,
    },
    "forest_nuts": {
        "key": "forest nuts",
        "aliases": ["nuts"],
        "desc": "Assorted nuts gathered from the forest floor.",
        "category": "material",
        "subcategory": "food_raw",
        "base_value": 4,
        "weight": 0.2,
        "stackable": True,
        "max_stack": 50,
        "edible": True,
        "hunger_restore": 10,
    },
    "bird_egg": {
        "key": "bird egg",
        "aliases": ["egg"],
        "desc": "A small speckled egg from a wild bird's nest.",
        "category": "material",
        "subcategory": "food_raw",
        "base_value": 6,
        "weight": 0.1,
        "stackable": True,
        "max_stack": 20,
        "edible": True,
        "hunger_restore": 12,
    },
    "honey": {
        "key": "jar of wild honey",
        "aliases": ["honey", "wild honey"],
        "desc": "Sweet golden honey harvested from a wild hive.",
        "category": "material",
        "subcategory": "food_raw",
        "base_value": 15,
        "weight": 0.3,
        "stackable": True,
        "max_stack": 20,
        "edible": True,
        "hunger_restore": 15,
    },
    
    # Fishing Materials
    "common_fish": {
        "key": "common fish",
        "aliases": ["fish"],
        "desc": "An ordinary freshwater fish. Good eating.",
        "category": "material",
        "subcategory": "fish",
        "base_value": 8,
        "weight": 0.5,
        "stackable": True,
        "max_stack": 20,
        "edible": True,
        "hunger_restore": 20,
    },
    "silver_fish": {
        "key": "silver fish",
        "aliases": ["silverfish"],
        "desc": "A fish with distinctive silver scales. Prized by cooks.",
        "category": "material",
        "subcategory": "fish",
        "base_value": 15,
        "weight": 0.6,
        "stackable": True,
        "max_stack": 20,
    },
    "golden_carp": {
        "key": "golden carp",
        "aliases": ["carp", "golden fish"],
        "desc": "A beautiful fish with golden scales. Very valuable.",
        "category": "material",
        "subcategory": "fish",
        "base_value": 50,
        "weight": 0.8,
        "stackable": True,
        "max_stack": 10,
        "flags": ["rare"],
    },
    "old_boot": {
        "key": "old boot",
        "aliases": ["boot"],
        "desc": "A waterlogged boot. Not much use to anyone.",
        "category": "junk",
        "base_value": 1,
        "weight": 0.5,
        "stackable": False,
    },
    "freshwater_clam": {
        "key": "freshwater clam",
        "aliases": ["clam"],
        "desc": "A small clam from the riverbed. Might contain a pearl.",
        "category": "material",
        "subcategory": "shellfish",
        "base_value": 5,
        "weight": 0.2,
        "stackable": True,
        "max_stack": 30,
    },
    "river_pearl": {
        "key": "river pearl",
        "aliases": ["pearl"],
        "desc": "A lustrous pearl from a freshwater clam.",
        "category": "treasure",
        "base_value": 100,
        "weight": 0.05,
        "stackable": True,
        "max_stack": 20,
        "flags": ["valuable"],
    },
    
    # Mining Materials
    "copper_ore": {
        "key": "copper ore",
        "aliases": ["copper"],
        "desc": "Raw copper ore, ready for smelting.",
        "category": "material",
        "subcategory": "ore",
        "base_value": 10,
        "weight": 1.0,
        "stackable": True,
        "max_stack": 50,
    },
    "iron_ore": {
        "key": "iron ore",
        "aliases": ["iron"],
        "desc": "Raw iron ore streaked with rust-red coloring.",
        "category": "material",
        "subcategory": "ore",
        "base_value": 15,
        "weight": 1.2,
        "stackable": True,
        "max_stack": 50,
    },
    "tin_ore": {
        "key": "tin ore",
        "aliases": ["tin"],
        "desc": "Silvery tin ore, useful for making bronze.",
        "category": "material",
        "subcategory": "ore",
        "base_value": 8,
        "weight": 0.9,
        "stackable": True,
        "max_stack": 50,
    },
    "silver_ore": {
        "key": "silver ore",
        "aliases": ["silver"],
        "desc": "Ore with veins of precious silver running through it.",
        "category": "material",
        "subcategory": "ore",
        "base_value": 40,
        "weight": 1.0,
        "stackable": True,
        "max_stack": 50,
        "flags": ["valuable"],
    },
    "gold_ore": {
        "key": "gold ore",
        "aliases": ["gold"],
        "desc": "Heavy ore glittering with gold deposits.",
        "category": "material",
        "subcategory": "ore",
        "base_value": 80,
        "weight": 1.5,
        "stackable": True,
        "max_stack": 30,
        "flags": ["valuable"],
    },
    "raw_gemstone": {
        "key": "raw gemstone",
        "aliases": ["gemstone", "gem"],
        "desc": "An uncut gemstone, cloudy but promising.",
        "category": "material",
        "subcategory": "gem",
        "base_value": 30,
        "weight": 0.2,
        "stackable": True,
        "max_stack": 30,
    },
    "coal": {
        "key": "lump of coal",
        "aliases": ["coal"],
        "desc": "Black coal, useful as fuel.",
        "category": "material",
        "subcategory": "fuel",
        "base_value": 3,
        "weight": 0.5,
        "stackable": True,
        "max_stack": 100,
    },
    "stone": {
        "key": "chunk of stone",
        "aliases": ["stone", "rock"],
        "desc": "A chunk of common stone.",
        "category": "material",
        "subcategory": "stone",
        "base_value": 1,
        "weight": 1.0,
        "stackable": True,
        "max_stack": 50,
    },
    "flint": {
        "key": "piece of flint",
        "aliases": ["flint"],
        "desc": "Sharp flint, good for starting fires or knapping.",
        "category": "material",
        "subcategory": "stone",
        "base_value": 5,
        "weight": 0.3,
        "stackable": True,
        "max_stack": 30,
    },
    
    # Bug Catching Materials
    "common_butterfly": {
        "key": "common butterfly",
        "aliases": ["butterfly"],
        "desc": "A delicate butterfly with patterned wings.",
        "category": "material",
        "subcategory": "bug",
        "base_value": 5,
        "weight": 0.01,
        "stackable": True,
        "max_stack": 20,
    },
    "dragonfly": {
        "key": "dragonfly",
        "aliases": [],
        "desc": "An iridescent dragonfly, wings shimmering.",
        "category": "material",
        "subcategory": "bug",
        "base_value": 12,
        "weight": 0.01,
        "stackable": True,
        "max_stack": 20,
    },
    "firefly": {
        "key": "firefly",
        "aliases": ["lightning bug"],
        "desc": "A firefly that glows softly even when captured.",
        "category": "material",
        "subcategory": "bug",
        "base_value": 8,
        "weight": 0.01,
        "stackable": True,
        "max_stack": 30,
        "flags": ["glowing"],
    },
    "beetle": {
        "key": "beetle",
        "aliases": [],
        "desc": "A shiny beetle with a hard carapace.",
        "category": "material",
        "subcategory": "bug",
        "base_value": 4,
        "weight": 0.02,
        "stackable": True,
        "max_stack": 30,
    },
    "rare_moth": {
        "key": "rare moon moth",
        "aliases": ["moon moth", "moth"],
        "desc": "A large moth with wings that seem to glow in moonlight.",
        "category": "material",
        "subcategory": "bug",
        "base_value": 35,
        "weight": 0.02,
        "stackable": True,
        "max_stack": 10,
        "flags": ["rare", "magical"],
    },
    "spider_silk": {
        "key": "spider silk",
        "aliases": ["silk"],
        "desc": "Fine silk harvested from spider webs.",
        "category": "material",
        "subcategory": "textile",
        "base_value": 15,
        "weight": 0.05,
        "stackable": True,
        "max_stack": 50,
    },
    
    # Beach/Tidepool Materials
    "seashell": {
        "key": "seashell",
        "aliases": ["shell"],
        "desc": "A pretty seashell from the beach.",
        "category": "material",
        "subcategory": "shell",
        "base_value": 2,
        "weight": 0.1,
        "stackable": True,
        "max_stack": 50,
    },
    "conch_shell": {
        "key": "conch shell",
        "aliases": ["conch"],
        "desc": "A large spiral shell. You can hear the ocean in it.",
        "category": "material",
        "subcategory": "shell",
        "base_value": 10,
        "weight": 0.4,
        "stackable": True,
        "max_stack": 20,
    },
    "sea_glass": {
        "key": "piece of sea glass",
        "aliases": ["sea glass", "beach glass"],
        "desc": "Glass worn smooth by the sea, frosted and beautiful.",
        "category": "material",
        "subcategory": "misc",
        "base_value": 5,
        "weight": 0.1,
        "stackable": True,
        "max_stack": 50,
    },
    "driftwood": {
        "key": "piece of driftwood",
        "aliases": ["driftwood"],
        "desc": "Weathered wood from the sea, smooth and pale.",
        "category": "material",
        "subcategory": "wood",
        "base_value": 3,
        "weight": 0.3,
        "stackable": True,
        "max_stack": 30,
    },
    "crab": {
        "key": "small crab",
        "aliases": ["crab"],
        "desc": "A small crab that keeps trying to pinch you.",
        "category": "material",
        "subcategory": "shellfish",
        "base_value": 8,
        "weight": 0.3,
        "stackable": True,
        "max_stack": 20,
    },
    "starfish": {
        "key": "starfish",
        "aliases": ["sea star"],
        "desc": "A colorful five-armed starfish.",
        "category": "material",
        "subcategory": "misc",
        "base_value": 6,
        "weight": 0.1,
        "stackable": True,
        "max_stack": 20,
    },
    "sea_urchin": {
        "key": "sea urchin",
        "aliases": ["urchin"],
        "desc": "A spiny sea urchin. Handle with care.",
        "category": "material",
        "subcategory": "misc",
        "base_value": 10,
        "weight": 0.2,
        "stackable": True,
        "max_stack": 20,
    },
    "seaweed": {
        "key": "strand of seaweed",
        "aliases": ["seaweed", "kelp"],
        "desc": "Fresh seaweed from the tide pools.",
        "category": "material",
        "subcategory": "plant",
        "base_value": 2,
        "weight": 0.1,
        "stackable": True,
        "max_stack": 50,
        "edible": True,
        "hunger_restore": 3,
    },
    
    # Additional Crafting Materials
    "red_herb": {
        "key": "red herb",
        "aliases": ["healing herb"],
        "desc": "A herb with distinctive red leaves, known for healing properties.",
        "category": "material",
        "subcategory": "herb",
        "base_value": 8,
        "weight": 0.1,
        "stackable": True,
        "max_stack": 50,
    },
    "green_herb": {
        "key": "green herb",
        "aliases": ["vigor herb"],
        "desc": "A vibrant green herb that restores energy.",
        "category": "material",
        "subcategory": "herb",
        "base_value": 6,
        "weight": 0.1,
        "stackable": True,
        "max_stack": 50,
    },
    "bitter_root": {
        "key": "bitter root",
        "aliases": ["antidote root"],
        "desc": "A bitter tasting root with detoxifying properties.",
        "category": "material",
        "subcategory": "herb",
        "base_value": 15,
        "weight": 0.2,
        "stackable": True,
        "max_stack": 30,
    },
    "passion_poppy": {
        "key": "passion poppy",
        "aliases": ["passion flower", "red poppy"],
        "desc": "A red flower with intoxicating properties. Handle with care.",
        "category": "material",
        "subcategory": "herb",
        "base_value": 20,
        "weight": 0.1,
        "stackable": True,
        "max_stack": 30,
        "flags": ["adult"],
    },
    "moon_lily": {
        "key": "moon lily",
        "aliases": ["moonflower"],
        "desc": "A pale flower that blooms only at night. Magically potent.",
        "category": "material",
        "subcategory": "herb",
        "base_value": 40,
        "weight": 0.1,
        "stackable": True,
        "max_stack": 20,
        "flags": ["magical", "rare"],
    },
    "beast_essence": {
        "key": "beast essence",
        "aliases": ["beast extract"],
        "desc": "A shimmering liquid extracted from magical beasts.",
        "category": "material",
        "subcategory": "magical",
        "base_value": 75,
        "weight": 0.2,
        "stackable": True,
        "max_stack": 10,
        "flags": ["magical", "rare"],
    },
    "glowing_algae": {
        "key": "glowing algae",
        "aliases": ["luminous algae"],
        "desc": "Algae that glows with bioluminescent light.",
        "category": "material",
        "subcategory": "plant",
        "base_value": 18,
        "weight": 0.1,
        "stackable": True,
        "max_stack": 30,
        "flags": ["glowing"],
    },
    "empty_vial": {
        "key": "empty vial",
        "aliases": ["vial", "glass vial"],
        "desc": "A small glass vial, perfect for potions.",
        "category": "material",
        "subcategory": "container",
        "base_value": 5,
        "weight": 0.1,
        "stackable": True,
        "max_stack": 50,
    },
    "fiber": {
        "key": "plant fiber",
        "aliases": ["fiber", "plant fibers"],
        "desc": "Strong plant fibers useful for rope and cloth.",
        "category": "material",
        "subcategory": "textile",
        "base_value": 2,
        "weight": 0.1,
        "stackable": True,
        "max_stack": 100,
    },
    "cloth": {
        "key": "bolt of cloth",
        "aliases": ["cloth", "fabric"],
        "desc": "A bolt of woven fabric.",
        "category": "material",
        "subcategory": "textile",
        "base_value": 15,
        "weight": 0.3,
        "stackable": True,
        "max_stack": 50,
    },
    "silk": {
        "key": "silk fabric",
        "aliases": ["silk"],
        "desc": "Fine silk fabric, smooth and luxurious.",
        "category": "material",
        "subcategory": "textile",
        "base_value": 50,
        "weight": 0.2,
        "stackable": True,
        "max_stack": 30,
        "flags": ["valuable"],
    },
    "lace": {
        "key": "delicate lace",
        "aliases": ["lace"],
        "desc": "Intricate lace fabric for fine clothing.",
        "category": "material",
        "subcategory": "textile",
        "base_value": 35,
        "weight": 0.1,
        "stackable": True,
        "max_stack": 30,
    },
    "hide": {
        "key": "animal hide",
        "aliases": ["hide", "raw hide", "pelt"],
        "desc": "An untreated animal hide, needs tanning.",
        "category": "material",
        "subcategory": "leather",
        "base_value": 10,
        "weight": 1.0,
        "stackable": True,
        "max_stack": 20,
    },
    "leather": {
        "key": "piece of leather",
        "aliases": ["leather", "tanned leather"],
        "desc": "Properly tanned and treated leather.",
        "category": "material",
        "subcategory": "leather",
        "base_value": 25,
        "weight": 0.5,
        "stackable": True,
        "max_stack": 30,
    },
    "wood": {
        "key": "piece of wood",
        "aliases": ["wood", "timber", "log"],
        "desc": "A piece of raw wood, suitable for crafting.",
        "category": "material",
        "subcategory": "wood",
        "base_value": 5,
        "weight": 1.0,
        "stackable": True,
        "max_stack": 50,
    },
    "plank": {
        "key": "wooden plank",
        "aliases": ["plank", "board"],
        "desc": "A cut and smoothed wooden plank.",
        "category": "material",
        "subcategory": "wood",
        "base_value": 8,
        "weight": 0.8,
        "stackable": True,
        "max_stack": 50,
    },
    "flour": {
        "key": "bag of flour",
        "aliases": ["flour"],
        "desc": "Finely ground flour for baking.",
        "category": "material",
        "subcategory": "cooking",
        "base_value": 4,
        "weight": 0.5,
        "stackable": True,
        "max_stack": 30,
    },
    "water": {
        "key": "bottle of water",
        "aliases": ["water"],
        "desc": "Clean, fresh water.",
        "category": "material",
        "subcategory": "cooking",
        "base_value": 1,
        "weight": 0.5,
        "stackable": True,
        "max_stack": 30,
    },
    "salt": {
        "key": "pinch of salt",
        "aliases": ["salt"],
        "desc": "Fine salt for cooking and preserving.",
        "category": "material",
        "subcategory": "cooking",
        "base_value": 2,
        "weight": 0.1,
        "stackable": True,
        "max_stack": 50,
    },
    "egg": {
        "key": "fresh egg",
        "aliases": ["egg", "chicken egg"],
        "desc": "A fresh egg from a chicken.",
        "category": "material",
        "subcategory": "cooking",
        "base_value": 3,
        "weight": 0.1,
        "stackable": True,
        "max_stack": 30,
    },
    "chocolate": {
        "key": "piece of chocolate",
        "aliases": ["chocolate"],
        "desc": "Rich, dark chocolate. A luxury ingredient.",
        "category": "material",
        "subcategory": "cooking",
        "base_value": 20,
        "weight": 0.2,
        "stackable": True,
        "max_stack": 20,
    },
    "mussel": {
        "key": "fresh mussel",
        "aliases": ["mussel"],
        "desc": "A fresh mussel from the shore.",
        "category": "material",
        "subcategory": "shellfish",
        "base_value": 4,
        "weight": 0.1,
        "stackable": True,
        "max_stack": 50,
    },
    "raw_fish": {
        "key": "raw fish",
        "aliases": ["uncooked fish"],
        "desc": "A fresh, uncooked fish.",
        "category": "material",
        "subcategory": "fish",
        "base_value": 6,
        "weight": 0.4,
        "stackable": True,
        "max_stack": 20,
    },
    "copper_ingot": {
        "key": "copper ingot",
        "aliases": ["copper bar"],
        "desc": "A bar of refined copper.",
        "category": "material",
        "subcategory": "metal",
        "base_value": 25,
        "weight": 1.0,
        "stackable": True,
        "max_stack": 50,
    },
    "iron_ingot": {
        "key": "iron ingot",
        "aliases": ["iron bar"],
        "desc": "A bar of refined iron.",
        "category": "material",
        "subcategory": "metal",
        "base_value": 40,
        "weight": 1.2,
        "stackable": True,
        "max_stack": 50,
    },
    "silver_ingot": {
        "key": "silver ingot",
        "aliases": ["silver bar"],
        "desc": "A bar of refined silver.",
        "category": "material",
        "subcategory": "metal",
        "base_value": 100,
        "weight": 1.0,
        "stackable": True,
        "max_stack": 30,
        "flags": ["valuable"],
    },
    "rough_gem": {
        "key": "rough gemstone",
        "aliases": ["rough gem", "uncut gem"],
        "desc": "An uncut gemstone, cloudy but with potential.",
        "category": "material",
        "subcategory": "gem",
        "base_value": 30,
        "weight": 0.2,
        "stackable": True,
        "max_stack": 30,
    },
    "cut_gem": {
        "key": "cut gemstone",
        "aliases": ["cut gem", "polished gem"],
        "desc": "A properly cut and polished gemstone.",
        "category": "material",
        "subcategory": "gem",
        "base_value": 75,
        "weight": 0.1,
        "stackable": True,
        "max_stack": 20,
        "flags": ["valuable"],
    },
    "fishing_hook": {
        "key": "fishing hook",
        "aliases": ["hook", "fish hook"],
        "desc": "A small metal hook for fishing.",
        "category": "material",
        "subcategory": "misc",
        "base_value": 2,
        "weight": 0.01,
        "stackable": True,
        "max_stack": 50,
    },
    "rope": {
        "key": "length of rope",
        "aliases": ["rope"],
        "desc": "A sturdy rope woven from plant fibers.",
        "category": "material",
        "subcategory": "misc",
        "base_value": 12,
        "weight": 0.5,
        "stackable": True,
        "max_stack": 20,
    },
    "chains": {
        "key": "metal chains",
        "aliases": ["chains", "chain"],
        "desc": "Sturdy metal chains with many uses.",
        "category": "material",
        "subcategory": "metal",
        "base_value": 35,
        "weight": 1.5,
        "stackable": True,
        "max_stack": 10,
        "flags": ["adult"],
    },
    "nails": {
        "key": "iron nails",
        "aliases": ["nails"],
        "desc": "A handful of sturdy iron nails.",
        "category": "material",
        "subcategory": "metal",
        "base_value": 1,
        "weight": 0.1,
        "stackable": True,
        "max_stack": 100,
    },
    "metal_ring": {
        "key": "metal ring",
        "aliases": ["ring", "iron ring"],
        "desc": "A simple metal ring. Useful for crafting.",
        "category": "material",
        "subcategory": "metal",
        "base_value": 3,
        "weight": 0.1,
        "stackable": True,
        "max_stack": 50,
    },
    "gold_ingot": {
        "key": "gold ingot",
        "aliases": ["gold bar"],
        "desc": "A bar of refined gold.",
        "category": "material",
        "subcategory": "metal",
        "base_value": 200,
        "weight": 1.5,
        "stackable": True,
        "max_stack": 20,
        "flags": ["valuable"],
    },
    "herb_paste": {
        "key": "herb paste",
        "aliases": ["paste"],
        "desc": "A ground herbal paste, foundation for many remedies.",
        "category": "material",
        "subcategory": "alchemy",
        "base_value": 8,
        "weight": 0.2,
        "stackable": True,
        "max_stack": 30,
    },
    "handle": {
        "key": "wooden handle",
        "aliases": ["handle"],
        "desc": "A shaped wooden handle for tools.",
        "category": "material",
        "subcategory": "wood",
        "base_value": 3,
        "weight": 0.2,
        "stackable": True,
        "max_stack": 30,
    },
    "leather_strips": {
        "key": "leather strips",
        "aliases": ["strips"],
        "desc": "Thin strips of leather for crafting.",
        "category": "material",
        "subcategory": "leather",
        "base_value": 5,
        "weight": 0.1,
        "stackable": True,
        "max_stack": 50,
    },
    "rubber_ball": {
        "key": "rubber ball",
        "aliases": ["ball"],
        "desc": "A small rubber ball. Has various uses.",
        "category": "material",
        "subcategory": "misc",
        "base_value": 10,
        "weight": 0.1,
        "stackable": True,
        "max_stack": 20,
    },
    "bandages": {
        "key": "bandages",
        "aliases": ["bandage"],
        "desc": "Clean cloth bandages for treating wounds.",
        "category": "consumable",
        "subcategory": "medicine",
        "base_value": 8,
        "weight": 0.1,
        "stackable": True,
        "max_stack": 30,
        "use_effect": {"type": "heal", "amount": 10},
        "use_message": "You wrap the bandages around your wounds.",
    },
}


# =============================================================================
# Item Templates - Tools
# =============================================================================

TOOL_TEMPLATES = {
    # Gathering Tools
    "basic_fishing_rod": {
        "key": "basic fishing rod",
        "aliases": ["fishing rod", "rod", "pole"],
        "desc": "A simple wooden fishing rod with basic tackle.",
        "category": "tool",
        "subcategory": "fishing",
        "tool_type": "fishing_rod",
        "tool_tier": 1,
        "base_value": 50,
        "weight": 1.5,
        "durability": 100,
        "gathering_bonus": 0,
    },
    "quality_fishing_rod": {
        "key": "quality fishing rod",
        "aliases": ["good rod", "quality rod"],
        "desc": "A well-crafted fishing rod with quality line.",
        "category": "tool",
        "subcategory": "fishing",
        "tool_type": "fishing_rod",
        "tool_tier": 2,
        "base_value": 150,
        "weight": 1.3,
        "durability": 200,
        "gathering_bonus": 10,
    },
    "master_fishing_rod": {
        "key": "master fishing rod",
        "aliases": ["master rod"],
        "desc": "An expertly crafted fishing rod, perfectly balanced.",
        "category": "tool",
        "subcategory": "fishing",
        "tool_type": "fishing_rod",
        "tool_tier": 3,
        "base_value": 500,
        "weight": 1.0,
        "durability": 500,
        "gathering_bonus": 25,
    },
    
    "basic_pickaxe": {
        "key": "basic pickaxe",
        "aliases": ["pickaxe", "pick"],
        "desc": "A simple pickaxe with a wooden handle and iron head.",
        "category": "tool",
        "subcategory": "mining",
        "tool_type": "pickaxe",
        "tool_tier": 1,
        "base_value": 75,
        "weight": 3.0,
        "durability": 100,
        "gathering_bonus": 0,
    },
    "quality_pickaxe": {
        "key": "quality pickaxe",
        "aliases": ["good pickaxe", "good pick"],
        "desc": "A well-forged pickaxe that bites into stone easily.",
        "category": "tool",
        "subcategory": "mining",
        "tool_type": "pickaxe",
        "tool_tier": 2,
        "base_value": 200,
        "weight": 2.5,
        "durability": 200,
        "gathering_bonus": 10,
    },
    "master_pickaxe": {
        "key": "master pickaxe",
        "aliases": ["master pick"],
        "desc": "A masterwork pickaxe that makes mining feel effortless.",
        "category": "tool",
        "subcategory": "mining",
        "tool_type": "pickaxe",
        "tool_tier": 3,
        "base_value": 600,
        "weight": 2.0,
        "durability": 500,
        "gathering_bonus": 25,
    },
    
    "bug_net": {
        "key": "bug catching net",
        "aliases": ["bug net", "net", "butterfly net"],
        "desc": "A fine mesh net on a long handle for catching insects.",
        "category": "tool",
        "subcategory": "catching",
        "tool_type": "bug_net",
        "tool_tier": 1,
        "base_value": 40,
        "weight": 0.5,
        "durability": 50,
        "gathering_bonus": 0,
    },
    "quality_bug_net": {
        "key": "quality bug net",
        "aliases": ["good net", "good bug net"],
        "desc": "A well-made net with a wider mouth and sturdier handle.",
        "category": "tool",
        "subcategory": "catching",
        "tool_type": "bug_net",
        "tool_tier": 2,
        "base_value": 120,
        "weight": 0.4,
        "durability": 100,
        "gathering_bonus": 15,
    },
    
    "foraging_basket": {
        "key": "foraging basket",
        "aliases": ["basket"],
        "desc": "A woven basket for gathering herbs and plants.",
        "category": "tool",
        "subcategory": "foraging",
        "tool_type": "foraging_basket",
        "tool_tier": 1,
        "base_value": 25,
        "weight": 0.5,
        "durability": 75,
        "gathering_bonus": 5,
    },
    "herbalist_satchel": {
        "key": "herbalist's satchel",
        "aliases": ["satchel", "herb bag"],
        "desc": "A leather satchel designed for collecting and preserving herbs.",
        "category": "tool",
        "subcategory": "foraging",
        "tool_type": "foraging_basket",
        "tool_tier": 2,
        "base_value": 100,
        "weight": 0.3,
        "durability": 150,
        "gathering_bonus": 15,
    },
    
    "beach_bucket": {
        "key": "beach bucket",
        "aliases": ["bucket", "pail"],
        "desc": "A sturdy bucket for collecting shells and beach finds.",
        "category": "tool",
        "subcategory": "beach",
        "tool_type": "beach_bucket",
        "tool_tier": 1,
        "base_value": 20,
        "weight": 0.5,
        "durability": 100,
        "gathering_bonus": 5,
    },
    
    # Crafting Tools
    "mortar_pestle": {
        "key": "mortar and pestle",
        "aliases": ["mortar", "pestle"],
        "desc": "A stone bowl and grinding tool for preparing alchemical ingredients.",
        "category": "tool",
        "subcategory": "alchemy",
        "tool_type": "mortar_pestle",
        "tool_tier": 1,
        "base_value": 40,
        "weight": 1.5,
        "durability": 200,
    },
    "smithing_hammer": {
        "key": "smithing hammer",
        "aliases": ["smith hammer", "forging hammer"],
        "desc": "A heavy hammer designed for working hot metal on an anvil.",
        "category": "tool",
        "subcategory": "smithing",
        "tool_type": "smithing_hammer",
        "tool_tier": 1,
        "base_value": 60,
        "weight": 2.5,
        "durability": 300,
    },
    "carpentry_tools": {
        "key": "carpentry toolkit",
        "aliases": ["carpentry tools", "woodworking tools", "carpenter's tools"],
        "desc": "A set of saws, chisels, and planes for working wood.",
        "category": "tool",
        "subcategory": "woodworking",
        "tool_type": "carpentry_tools",
        "tool_tier": 1,
        "base_value": 80,
        "weight": 3.0,
        "durability": 250,
    },
    "sewing_kit": {
        "key": "sewing kit",
        "aliases": ["sewing tools", "needle and thread"],
        "desc": "A compact kit with needles, thread, scissors, and thimbles.",
        "category": "tool",
        "subcategory": "tailoring",
        "tool_type": "sewing_kit",
        "tool_tier": 1,
        "base_value": 30,
        "weight": 0.3,
        "durability": 100,
    },
    "jeweler_tools": {
        "key": "jeweler's toolkit",
        "aliases": ["jeweler tools", "jeweling tools"],
        "desc": "Delicate tools for working with precious metals and gems.",
        "category": "tool",
        "subcategory": "jewelcrafting",
        "tool_type": "jeweler_tools",
        "tool_tier": 1,
        "base_value": 100,
        "weight": 0.8,
        "durability": 150,
    },
    "leatherworking_tools": {
        "key": "leatherworking toolkit",
        "aliases": ["leather tools", "tanning tools"],
        "desc": "Tools for cutting, stitching, and treating leather.",
        "category": "tool",
        "subcategory": "leatherworking",
        "tool_type": "leatherworking_tools",
        "tool_tier": 1,
        "base_value": 55,
        "weight": 1.5,
        "durability": 200,
    },
    "cooking_pot": {
        "key": "cooking pot",
        "aliases": ["pot", "stew pot"],
        "desc": "A large iron pot for cooking stews and soups.",
        "category": "tool",
        "subcategory": "cooking",
        "tool_type": "cooking_pot",
        "tool_tier": 1,
        "base_value": 35,
        "weight": 3.0,
        "durability": 500,
    },
}


# =============================================================================
# Item Templates - Consumables
# =============================================================================

CONSUMABLE_TEMPLATES = {
    "health_potion_minor": {
        "key": "minor health potion",
        "aliases": ["health potion", "healing potion", "red potion"],
        "desc": "A small vial of red liquid that restores health.",
        "category": "consumable",
        "subcategory": "potion",
        "base_value": 25,
        "weight": 0.2,
        "stackable": True,
        "max_stack": 20,
        "use_effect": {"type": "heal", "amount": 20},
        "use_message": "You drink the potion. Warmth spreads through your body.",
    },
    "health_potion_major": {
        "key": "major health potion",
        "aliases": ["big health potion", "large healing potion"],
        "desc": "A large vial of deep red liquid that greatly restores health.",
        "category": "consumable",
        "subcategory": "potion",
        "base_value": 75,
        "weight": 0.3,
        "stackable": True,
        "max_stack": 10,
        "use_effect": {"type": "heal", "amount": 50},
        "use_message": "You drink the potion. Injuries mend as energy surges through you.",
    },
    
    "stamina_potion": {
        "key": "stamina potion",
        "aliases": ["energy potion", "green potion"],
        "desc": "A green potion that restores energy.",
        "category": "consumable",
        "subcategory": "potion",
        "base_value": 20,
        "weight": 0.2,
        "stackable": True,
        "max_stack": 20,
        "use_effect": {"type": "restore_stamina", "amount": 30},
        "use_message": "You drink the potion. Your fatigue melts away.",
    },
    
    "antidote": {
        "key": "antidote",
        "aliases": ["cure poison", "anti-venom"],
        "desc": "A bitter medicine that cures poison.",
        "category": "consumable",
        "subcategory": "medicine",
        "base_value": 30,
        "weight": 0.2,
        "stackable": True,
        "max_stack": 10,
        "use_effect": {"type": "cure", "cures": ["poisoned"]},
        "use_message": "You drink the bitter antidote. The poison in your veins neutralizes.",
    },
    
    "bread": {
        "key": "loaf of bread",
        "aliases": ["bread"],
        "desc": "A fresh loaf of crusty bread.",
        "category": "consumable",
        "subcategory": "food",
        "base_value": 5,
        "weight": 0.3,
        "stackable": True,
        "max_stack": 20,
        "edible": True,
        "hunger_restore": 25,
        "use_message": "You eat the bread. It's simple but filling.",
    },
    
    "cooked_fish": {
        "key": "cooked fish",
        "aliases": ["grilled fish", "fish dinner"],
        "desc": "A nicely grilled fish, seasoned and ready to eat.",
        "category": "consumable",
        "subcategory": "food",
        "base_value": 15,
        "weight": 0.4,
        "stackable": True,
        "max_stack": 10,
        "edible": True,
        "hunger_restore": 40,
        "use_message": "You eat the fish. Delicious!",
    },
    
    "ale": {
        "key": "mug of ale",
        "aliases": ["ale", "beer"],
        "desc": "A frothy mug of ale.",
        "category": "consumable",
        "subcategory": "drink",
        "base_value": 3,
        "weight": 0.5,
        "stackable": False,
        "use_effect": {"type": "apply_effect", "effect": "tipsy", "duration": 300},
        "use_message": "You drink the ale. It's bitter but refreshing.",
    },
    
    "aphrodisiac_potion": {
        "key": "aphrodisiac potion",
        "aliases": ["pink potion", "love potion"],
        "desc": "A shimmering pink potion that heightens... sensitivity.",
        "category": "consumable",
        "subcategory": "potion",
        "base_value": 50,
        "weight": 0.2,
        "stackable": True,
        "max_stack": 5,
        "flags": ["adult"],
        "use_effect": {"type": "apply_effect", "effect": "aroused", "duration": 600},
        "use_message": "You drink the potion. Heat spreads through your body...",
    },
}


# =============================================================================
# Item Templates - Equipment
# =============================================================================

EQUIPMENT_TEMPLATES = {
    "leather_gloves": {
        "key": "leather gloves",
        "aliases": ["gloves"],
        "desc": "Simple leather gloves that protect your hands.",
        "category": "equipment",
        "slot": "hands",
        "base_value": 20,
        "weight": 0.3,
        "armor": 1,
    },
    
    "work_boots": {
        "key": "sturdy work boots",
        "aliases": ["boots", "work boots"],
        "desc": "Heavy boots suitable for rough terrain.",
        "category": "equipment",
        "slot": "feet",
        "base_value": 35,
        "weight": 1.0,
        "armor": 2,
    },
    
    "simple_ring": {
        "key": "simple silver ring",
        "aliases": ["ring", "silver ring"],
        "desc": "A plain silver ring.",
        "category": "equipment",
        "slot": "finger_l",
        "base_value": 50,
        "weight": 0.05,
    },
    
    "collar_leather": {
        "key": "leather collar",
        "aliases": ["collar"],
        "desc": "A simple leather collar with a metal ring.",
        "category": "equipment",
        "slot": "neck",
        "base_value": 30,
        "weight": 0.2,
        "flags": ["adult", "collar"],
    },
    
    "collar_elegant": {
        "key": "elegant collar",
        "aliases": ["nice collar", "fancy collar"],
        "desc": "A beautifully crafted collar of soft leather with silver fittings.",
        "category": "equipment",
        "slot": "neck",
        "base_value": 150,
        "weight": 0.2,
        "flags": ["adult", "collar"],
    },
}


# =============================================================================
# Item Templates - Keys and Special
# =============================================================================

KEY_TEMPLATES = {
    "curator_card": {
        "key": "Curator's access card",
        "aliases": ["access card", "card", "curator card"],
        "desc": "A cream-colored card with elegant script. It grants access to the Curator's private areas.",
        "category": "key",
        "base_value": 0,
        "weight": 0.01,
        "flags": ["quest", "no_sell", "no_drop"],
        "grants_access": ["curator_office", "curator_archives"],
    },
    
    "home_key": {
        "key": "house key",
        "aliases": ["key", "home key"],
        "desc": "A key to your home.",
        "category": "key",
        "base_value": 0,
        "weight": 0.05,
        "flags": ["no_sell"],
    },
}


# =============================================================================
# Combine All Templates
# =============================================================================

ITEM_TEMPLATES = {}
ITEM_TEMPLATES.update(MATERIAL_TEMPLATES)
ITEM_TEMPLATES.update(TOOL_TEMPLATES)
ITEM_TEMPLATES.update(CONSUMABLE_TEMPLATES)
ITEM_TEMPLATES.update(EQUIPMENT_TEMPLATES)
ITEM_TEMPLATES.update(KEY_TEMPLATES)


# =============================================================================
# Core Item Functions
# =============================================================================

def get_item_template(template_key):
    """Get an item template by key."""
    return ITEM_TEMPLATES.get(template_key)


def list_templates(category=None, subcategory=None):
    """
    List available item templates.
    
    Args:
        category: Filter by category
        subcategory: Filter by subcategory
    
    Returns:
        dict: Matching templates
    """
    results = {}
    for key, template in ITEM_TEMPLATES.items():
        if category and template.get("category") != category:
            continue
        if subcategory and template.get("subcategory") != subcategory:
            continue
        results[key] = template
    return results


def create_item(template_key, location=None, quality="common", quantity=1):
    """
    Create an item from a template.
    
    Args:
        template_key: Key in ITEM_TEMPLATES
        location: Where to place the item
        quality: Item quality tier
        quantity: Stack size for stackable items
    
    Returns:
        Object: The created item
    """
    template = get_item_template(template_key)
    if not template:
        logger.log_err(f"Unknown item template: {template_key}")
        return None
    
    # Create the object
    item = create_object(
        "typeclasses.objects.Object",
        key=template["key"],
        location=location,
    )
    
    if not item:
        return None
    
    # Set up item data
    item.db.desc = template.get("desc", "")
    item.db.item_template = template_key
    item.db.item_data = {
        "category": template.get("category", "junk"),
        "subcategory": template.get("subcategory"),
        "base_value": template.get("base_value", 0),
        "weight": template.get("weight", 0.1),
        "stackable": template.get("stackable", False),
        "max_stack": template.get("max_stack", 1),
        "quantity": min(quantity, template.get("max_stack", 1)) if template.get("stackable") else 1,
        "quality": quality,
        "flags": template.get("flags", []),
    }
    
    # Tool-specific data
    if template.get("tool_type"):
        item.db.tool_data = {
            "tool_type": template["tool_type"],
            "tool_tier": template.get("tool_tier", 1),
            "gathering_bonus": template.get("gathering_bonus", 0),
            "durability": template.get("durability", 100),
            "max_durability": template.get("durability", 100),
        }
    
    # Consumable-specific data
    if template.get("use_effect") or template.get("edible"):
        item.db.consumable_data = {
            "use_effect": template.get("use_effect"),
            "use_message": template.get("use_message"),
            "edible": template.get("edible", False),
            "hunger_restore": template.get("hunger_restore", 0),
        }
    
    # Equipment-specific data
    if template.get("slot"):
        item.db.equipment_data = {
            "slot": template["slot"],
            "armor": template.get("armor", 0),
            "stats": template.get("stats", {}),
        }
    
    # Key-specific data
    if template.get("grants_access"):
        item.db.key_data = {
            "grants_access": template["grants_access"],
        }
    
    # Add aliases
    if template.get("aliases"):
        item.aliases.add(template["aliases"])
    
    # Tag as item
    item.tags.add("item", category="object_type")
    item.tags.add(template.get("category", "junk"), category="item_category")
    
    # Add flag tags
    for flag in template.get("flags", []):
        item.tags.add(flag, category="item_flag")
    
    return item


def is_item(obj):
    """Check if an object is an item."""
    return obj.tags.has("item", category="object_type")


def get_item_data(item):
    """Get item's data dict."""
    return item.db.item_data or {}


def get_item_category(item):
    """Get item's category."""
    data = get_item_data(item)
    return data.get("category", "junk")


def get_item_quantity(item):
    """Get quantity for stackable items."""
    data = get_item_data(item)
    return data.get("quantity", 1)


def set_item_quantity(item, quantity):
    """Set quantity for stackable items."""
    if not item.db.item_data:
        return
    max_stack = item.db.item_data.get("max_stack", 1)
    item.db.item_data["quantity"] = max(0, min(quantity, max_stack))


def add_to_stack(item, amount):
    """
    Add to a stackable item's quantity.
    
    Returns:
        int: Amount that couldn't fit (overflow)
    """
    if not item.db.item_data or not item.db.item_data.get("stackable"):
        return amount
    
    current = get_item_quantity(item)
    max_stack = item.db.item_data.get("max_stack", 1)
    
    new_total = current + amount
    if new_total <= max_stack:
        set_item_quantity(item, new_total)
        return 0
    else:
        set_item_quantity(item, max_stack)
        return new_total - max_stack


def remove_from_stack(item, amount):
    """
    Remove from a stackable item's quantity.
    
    Returns:
        int: Amount actually removed
    """
    current = get_item_quantity(item)
    removed = min(current, amount)
    new_quantity = current - removed
    
    if new_quantity <= 0:
        item.delete()
    else:
        set_item_quantity(item, new_quantity)
    
    return removed


# =============================================================================
# Item Value
# =============================================================================

def get_item_value(item, for_sale=True):
    """
    Get the value of an item.
    
    Args:
        item: The item
        for_sale: If True, return sell value (usually less than buy)
    
    Returns:
        int: Value in coins
    """
    data = get_item_data(item)
    base_value = data.get("base_value", 0)
    quality = data.get("quality", "common")
    quantity = data.get("quantity", 1)
    
    # Quality multiplier
    quality_data = ITEM_QUALITIES.get(quality, ITEM_QUALITIES["common"])
    value = int(base_value * quality_data["value_mult"])
    
    # Stack multiplier
    value *= quantity
    
    # Sell penalty
    if for_sale:
        value = int(value * 0.5)  # Shops buy at 50%
    
    return max(1, value) if base_value > 0 else 0


def get_item_display_name(item, include_quantity=True):
    """
    Get formatted display name for an item.
    
    Args:
        item: The item
        include_quantity: Show stack count
    
    Returns:
        str: Formatted name
    """
    data = get_item_data(item)
    quality = data.get("quality", "common")
    quality_data = ITEM_QUALITIES.get(quality, ITEM_QUALITIES["common"])
    
    name = f"{quality_data['color']}{item.key}|n"
    
    if include_quantity and data.get("stackable"):
        quantity = data.get("quantity", 1)
        if quantity > 1:
            name = f"{name} (x{quantity})"
    
    return name


# =============================================================================
# Tool Functions
# =============================================================================

def is_tool(item):
    """Check if item is a tool."""
    return item.db.tool_data is not None


def get_tool_type(item):
    """Get the tool type (fishing_rod, pickaxe, etc)."""
    if not item.db.tool_data:
        return None
    return item.db.tool_data.get("tool_type")


def get_tool_tier(item):
    """Get the tool's tier (1-3)."""
    if not item.db.tool_data:
        return 0
    return item.db.tool_data.get("tool_tier", 1)


def get_tool_bonus(item):
    """Get the tool's gathering bonus."""
    if not item.db.tool_data:
        return 0
    return item.db.tool_data.get("gathering_bonus", 0)


def has_tool(character, tool_type, min_tier=1):
    """
    Check if character has a specific tool type.
    
    Args:
        character: The character
        tool_type: Type of tool needed
        min_tier: Minimum tier required
    
    Returns:
        Object or None: The tool if found
    """
    for item in character.contents:
        if is_tool(item):
            if get_tool_type(item) == tool_type:
                if get_tool_tier(item) >= min_tier:
                    return item
    return None


def get_best_tool(character, tool_type):
    """
    Get the best tool of a type the character has.
    
    Args:
        character: The character
        tool_type: Type of tool
    
    Returns:
        Object or None: Best tool or None
    """
    best = None
    best_tier = 0
    
    for item in character.contents:
        if is_tool(item) and get_tool_type(item) == tool_type:
            tier = get_tool_tier(item)
            if tier > best_tier:
                best = item
                best_tier = tier
    
    return best


def damage_tool(tool, amount=1):
    """
    Damage a tool, reducing durability.
    
    Args:
        tool: The tool
        amount: Durability to remove
    
    Returns:
        bool: True if tool broke
    """
    if not tool.db.tool_data:
        return False
    
    current = tool.db.tool_data.get("durability", 100)
    new_durability = current - amount
    
    if new_durability <= 0:
        # Tool broke
        return True
    
    tool.db.tool_data["durability"] = new_durability
    return False


def repair_tool(tool, amount=None):
    """
    Repair a tool.
    
    Args:
        tool: The tool
        amount: Durability to restore (None = full)
    """
    if not tool.db.tool_data:
        return
    
    max_dur = tool.db.tool_data.get("max_durability", 100)
    current = tool.db.tool_data.get("durability", 0)
    
    if amount is None:
        tool.db.tool_data["durability"] = max_dur
    else:
        tool.db.tool_data["durability"] = min(max_dur, current + amount)


# =============================================================================
# Consumable Functions
# =============================================================================

def is_consumable(item):
    """Check if item is consumable."""
    return item.db.consumable_data is not None


def use_item(character, item):
    """
    Use a consumable item.
    
    Args:
        character: Who's using it
        item: The item to use
    
    Returns:
        bool: Success
    """
    if not is_consumable(item):
        character.msg(f"You can't use {item.key}.")
        return False
    
    data = item.db.consumable_data
    
    # Show use message
    if data.get("use_message"):
        character.msg(data["use_message"])
    
    # Apply effects
    effect = data.get("use_effect")
    if effect:
        apply_use_effect(character, effect)
    
    # Handle food
    if data.get("edible"):
        hunger_restore = data.get("hunger_restore", 0)
        # STUB: Would integrate with hunger system
        if hunger_restore:
            character.msg(f"You feel less hungry. (+{hunger_restore} fullness)")
    
    # Remove one from stack
    remove_from_stack(item, 1)
    
    return True


def apply_use_effect(character, effect):
    """
    Apply an item's use effect.
    
    Args:
        character: Target
        effect: Effect dict
    """
    effect_type = effect.get("type")
    
    if effect_type == "heal":
        amount = effect.get("amount", 10)
        # STUB: Would heal character
        character.msg(f"|gYou recover {amount} health.|n")
    
    elif effect_type == "restore_stamina":
        amount = effect.get("amount", 10)
        character.msg(f"|gYou recover {amount} stamina.|n")
    
    elif effect_type == "cure":
        cures = effect.get("cures", [])
        from world.effects import remove_effect
        for effect_name in cures:
            if remove_effect(character, effect_name):
                character.msg(f"|gYou are cured of {effect_name}.|n")
    
    elif effect_type == "apply_effect":
        from world.effects import apply_effect
        effect_name = effect.get("effect")
        duration = effect.get("duration", 60)
        apply_effect(character, effect_name, duration=duration)


# =============================================================================
# Equipment Functions
# =============================================================================

def is_equipment(item):
    """Check if item is equipment."""
    return item.db.equipment_data is not None


def get_equipment_slot(item):
    """Get what slot equipment uses."""
    if not item.db.equipment_data:
        return None
    return item.db.equipment_data.get("slot")


def get_equipped(character, slot):
    """Get item equipped in a slot."""
    equipped = character.db.equipped or {}
    item_id = equipped.get(slot)
    if not item_id:
        return None
    
    try:
        from evennia.objects.models import ObjectDB
        return ObjectDB.objects.get(id=item_id)
    except:
        return None


def equip_item(character, item):
    """
    Equip an item.
    
    Args:
        character: Who's equipping
        item: The item
    
    Returns:
        bool: Success
    """
    if not is_equipment(item):
        character.msg(f"You can't equip {item.key}.")
        return False
    
    slot = get_equipment_slot(item)
    if not slot:
        return False
    
    # Initialize equipped dict
    if not character.db.equipped:
        character.db.equipped = {}
    
    # Unequip current item in slot
    current = get_equipped(character, slot)
    if current:
        unequip_item(character, current)
    
    # Equip new item
    character.db.equipped[slot] = item.id
    character.msg(f"You equip {item.key}.")
    
    return True


def unequip_item(character, item):
    """
    Unequip an item.
    
    Args:
        character: Who's unequipping
        item: The item
    
    Returns:
        bool: Success
    """
    if not character.db.equipped:
        return False
    
    slot = get_equipment_slot(item)
    if not slot:
        return False
    
    if character.db.equipped.get(slot) != item.id:
        return False
    
    del character.db.equipped[slot]
    character.msg(f"You unequip {item.key}.")
    
    return True


def get_all_equipped(character):
    """
    Get all equipped items.
    
    Returns:
        dict: slot -> item
    """
    if not character.db.equipped:
        return {}
    
    result = {}
    for slot, item_id in character.db.equipped.items():
        try:
            from evennia.objects.models import ObjectDB
            item = ObjectDB.objects.get(id=item_id)
            result[slot] = item
        except:
            pass
    
    return result


# =============================================================================
# Inventory Helpers
# =============================================================================

def find_item_in_inventory(character, template_key):
    """
    Find an item by template in character's inventory.
    
    Returns:
        Object or None
    """
    for item in character.contents:
        if is_item(item) and item.db.item_template == template_key:
            return item
    return None


def count_items(character, template_key):
    """
    Count total quantity of an item type.
    
    Returns:
        int: Total count
    """
    total = 0
    for item in character.contents:
        if is_item(item) and item.db.item_template == template_key:
            total += get_item_quantity(item)
    return total


def give_item(character, template_key, quantity=1, quality="common"):
    """
    Give an item to a character, handling stacking.
    
    Args:
        character: Recipient
        template_key: Item template
        quantity: How many
        quality: Item quality
    
    Returns:
        Object: The item (or existing stack)
    """
    template = get_item_template(template_key)
    if not template:
        return None
    
    # Check if stackable and character has existing stack
    if template.get("stackable"):
        existing = find_item_in_inventory(character, template_key)
        if existing:
            overflow = add_to_stack(existing, quantity)
            if overflow > 0:
                # Create additional stack for overflow
                create_item(template_key, location=character, quality=quality, quantity=overflow)
            return existing
    
    # Create new item
    return create_item(template_key, location=character, quality=quality, quantity=quantity)


def take_item(character, template_key, quantity=1):
    """
    Remove items from character's inventory.
    
    Args:
        character: Who to take from
        template_key: Item template
        quantity: How many to remove
    
    Returns:
        int: Amount actually removed
    """
    removed = 0
    remaining = quantity
    
    # Find all matching items
    items = [i for i in character.contents if is_item(i) and i.db.item_template == template_key]
    
    for item in items:
        if remaining <= 0:
            break
        
        took = remove_from_stack(item, remaining)
        removed += took
        remaining -= took
    
    return removed
