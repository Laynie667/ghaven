"""
Body System for Gilderhaven
============================

Lightweight body customization system.

Architecture:
- Body parts: Custom descriptions with state variants
- Species templates: Pre-made part collections with mechanics
- Body modifiers: Temporary/permanent changes (marks, inflation, etc.)
- Shortcodes: <body.X>, <worn.X> resolve in descriptions

No complex inheritance. Player controls visibility via shortcodes.

Usage:
    from world.body import (
        add_part, edit_part, apply_species,
        add_modifier, remove_modifier,
        process_shortcodes, get_body_display
    )
    
    # Apply species template
    apply_species(character, "canine")
    
    # Customize a part
    edit_part(character, "cock", "aroused", "thick red canine cock, knot swelling")
    
    # Add a modifier
    add_modifier(character, "neck", "marked", desc="covered in hickeys", duration=3600)
    
    # Process shortcodes in text
    output = process_shortcodes(character, "She has <body.eyes> and <body.cock>.")
"""

import time
from evennia.utils import logger


# =============================================================================
# GENITAL MECHANICS
# =============================================================================

# Mechanics are just tags - scenes check for these
GENITAL_MECHANICS = {
    "human": [],
    "canine": ["knot", "sheath", "tapered"],
    "equine": ["flare", "sheath", "medial_ring"],
    "feline": ["barbs", "sheath", "tapered"],
    "reptile": ["hemipenes", "cloaca"],
    "aquatic": ["prehensile", "retractable"],
    "tentacle": ["prehensile", "multiple", "slime"],
    "avian": ["cloaca"],
    "insect": ["ovipositor"],
}


# =============================================================================
# SPECIES TEMPLATES
# =============================================================================

SPECIES_TEMPLATES = {
    # -------------------------------------------------------------------------
    # Humanoid Species
    # -------------------------------------------------------------------------
    "human": {
        "name": "Human",
        "desc": "Standard human features.",
        "parts": {
            "eyes": {"default": "eyes"},
            "hair": {"default": "hair"},
            "skin": {"default": "skin"},
        },
        "genital_category": "human",
        "covering": "skin",
        "abilities": [],
    },
    
    "elf": {
        "name": "Elf",
        "desc": "Graceful humanoid with pointed ears.",
        "parts": {
            "eyes": {"default": "sharp, luminous eyes"},
            "ears": {"default": "long, elegantly pointed ears"},
            "hair": {"default": "fine, silken hair"},
            "skin": {"default": "flawless skin"},
        },
        "genital_category": "human",
        "covering": "skin",
        "abilities": ["darkvision", "trance"],
    },
    
    "dwarf": {
        "name": "Dwarf",
        "desc": "Stocky humanoid, often bearded.",
        "parts": {
            "eyes": {"default": "keen eyes"},
            "hair": {"default": "thick, often braided hair"},
            "beard": {"default": "impressive beard"},
            "skin": {"default": "weathered skin"},
        },
        "genital_category": "human",
        "covering": "skin",
        "abilities": ["darkvision", "stonecunning"],
    },
    
    "orc": {
        "name": "Orc",
        "desc": "Powerful, tusked humanoid.",
        "parts": {
            "eyes": {"default": "fierce eyes"},
            "tusks": {"default": "prominent tusks"},
            "skin": {"default": "green-gray skin"},
        },
        "genital_category": "human",
        "covering": "skin",
        "abilities": ["relentless"],
    },
    
    "goblin": {
        "name": "Goblin",
        "desc": "Small, clever creature with pointed ears.",
        "parts": {
            "eyes": {"default": "large, cunning eyes"},
            "ears": {"default": "long, pointed ears"},
            "skin": {"default": "mottled green skin"},
        },
        "genital_category": "human",
        "covering": "skin",
        "abilities": ["nimble_escape"],
    },
    
    # -------------------------------------------------------------------------
    # Canine Species
    # -------------------------------------------------------------------------
    "canine": {
        "name": "Canine",
        "desc": "Wolf or dog-like anthro.",
        "parts": {
            "eyes": {"default": "amber eyes"},
            "ears": {"default": "pointed canine ears", "alert": "perked ears"},
            "muzzle": {"default": "canine muzzle"},
            "tail": {"default": "bushy tail", "wagging": "wagging tail", "tucked": "tucked tail"},
            "fur": {"default": "soft fur"},
            "paws": {"default": "padded paws"},
            "cock": {
                "default": "canine cock hidden in its sheath",
                "aroused": "red tapered cock, knot visible at the base",
                "knotted": "swollen knot locked inside",
            },
        },
        "genital_category": "canine",
        "covering": "fur",
        "abilities": ["enhanced_smell", "pack_tactics"],
    },
    
    "wolf": {
        "name": "Wolf",
        "desc": "Larger, wilder canine.",
        "parts": {
            "eyes": {"default": "golden predator eyes"},
            "ears": {"default": "tall wolf ears"},
            "muzzle": {"default": "powerful wolf muzzle"},
            "tail": {"default": "thick wolf tail"},
            "fur": {"default": "dense gray fur"},
            "fangs": {"default": "sharp fangs"},
            "cock": {
                "default": "wolf cock sheathed",
                "aroused": "red wolf cock unsheathed, thick knot visible",
                "knotted": "massive knot swollen and locked",
            },
        },
        "genital_category": "canine",
        "covering": "fur",
        "abilities": ["enhanced_smell", "pack_tactics", "howl"],
    },
    
    "fox": {
        "name": "Fox",
        "desc": "Sleek, clever vulpine.",
        "parts": {
            "eyes": {"default": "sharp amber eyes"},
            "ears": {"default": "large triangular ears"},
            "muzzle": {"default": "slender fox muzzle"},
            "tail": {"default": "fluffy fox tail"},
            "fur": {"default": "russet fur with white markings"},
            "cock": {
                "default": "fox cock in sheath",
                "aroused": "slender red cock with modest knot",
            },
        },
        "genital_category": "canine",
        "covering": "fur",
        "abilities": ["enhanced_smell", "cunning"],
    },
    
    # -------------------------------------------------------------------------
    # Feline Species
    # -------------------------------------------------------------------------
    "feline": {
        "name": "Feline",
        "desc": "Cat-like anthro.",
        "parts": {
            "eyes": {"default": "slitted eyes"},
            "ears": {"default": "triangular cat ears", "alert": "swiveling ears"},
            "muzzle": {"default": "feline muzzle"},
            "tail": {"default": "long sinuous tail", "puffed": "puffed tail"},
            "fur": {"default": "sleek fur"},
            "claws": {"default": "retractable claws"},
            "tongue": {"default": "rough tongue"},
            "cock": {
                "default": "feline cock sheathed",
                "aroused": "barbed cock unsheathed",
            },
        },
        "genital_category": "feline",
        "covering": "fur",
        "abilities": ["darkvision", "claws", "always_land_on_feet"],
    },
    
    "lion": {
        "name": "Lion",
        "desc": "Proud, powerful feline.",
        "parts": {
            "eyes": {"default": "golden eyes"},
            "mane": {"default": "majestic mane"},
            "ears": {"default": "rounded ears"},
            "tail": {"default": "tufted tail"},
            "fur": {"default": "tawny fur"},
            "cock": {
                "default": "lion cock sheathed",
                "aroused": "thick barbed cock emerged",
            },
        },
        "genital_category": "feline",
        "covering": "fur",
        "abilities": ["roar", "pride_leader"],
    },
    
    "tiger": {
        "name": "Tiger",
        "desc": "Powerful striped predator.",
        "parts": {
            "eyes": {"default": "intense amber eyes"},
            "ears": {"default": "rounded ears with white spots"},
            "fur": {"default": "orange fur with black stripes"},
            "tail": {"default": "long striped tail"},
            "cock": {
                "default": "tiger cock sheathed",
                "aroused": "thick barbed cock unsheathed",
            },
        },
        "genital_category": "feline",
        "covering": "fur",
        "abilities": ["powerful_build", "ambush"],
    },
    
    # -------------------------------------------------------------------------
    # Equine Species
    # -------------------------------------------------------------------------
    "equine": {
        "name": "Equine",
        "desc": "Horse-like anthro.",
        "parts": {
            "eyes": {"default": "large dark eyes"},
            "ears": {"default": "long equine ears"},
            "muzzle": {"default": "equine muzzle"},
            "mane": {"default": "flowing mane"},
            "tail": {"default": "long horse tail"},
            "hooves": {"default": "solid hooves"},
            "cock": {
                "default": "equine cock in sheath",
                "aroused": "massive flared horse cock",
                "flaring": "cock flared wide, medial ring prominent",
            },
        },
        "genital_category": "equine",
        "covering": "short coat",
        "abilities": ["powerful_kick", "endurance"],
    },
    
    "unicorn": {
        "name": "Unicorn",
        "desc": "Magical horned equine.",
        "parts": {
            "eyes": {"default": "luminous eyes"},
            "horn": {"default": "spiraling horn"},
            "mane": {"default": "shimmering mane"},
            "tail": {"default": "silken tail"},
            "coat": {"default": "pure white coat"},
            "cock": {
                "default": "equine cock in sheath",
                "aroused": "glowing flared cock",
            },
        },
        "genital_category": "equine",
        "covering": "silken coat",
        "abilities": ["magic", "purity", "teleport"],
    },
    
    # -------------------------------------------------------------------------
    # Reptilian Species
    # -------------------------------------------------------------------------
    "reptile": {
        "name": "Reptile",
        "desc": "Scaled lizard-like anthro.",
        "parts": {
            "eyes": {"default": "slitted reptilian eyes"},
            "snout": {"default": "scaled snout"},
            "scales": {"default": "smooth scales"},
            "tail": {"default": "thick reptilian tail"},
            "claws": {"default": "sharp claws"},
            "cock": {
                "default": "hemipenes retracted",
                "aroused": "twin hemipenes emerged",
            },
        },
        "genital_category": "reptile",
        "covering": "scales",
        "abilities": ["cold_blooded", "regeneration"],
    },
    
    "dragon": {
        "name": "Dragon",
        "desc": "Powerful scaled creature with wings.",
        "parts": {
            "eyes": {"default": "ancient slitted eyes"},
            "horns": {"default": "curved horns"},
            "snout": {"default": "powerful dragon snout"},
            "scales": {"default": "thick armored scales"},
            "wings": {"default": "massive leathery wings"},
            "tail": {"default": "powerful spiked tail"},
            "cock": {
                "default": "dragon cock in slit",
                "aroused": "ridged dragon cock emerged",
            },
        },
        "genital_category": "reptile",
        "covering": "scales",
        "abilities": ["flight", "breath_weapon", "frightful_presence"],
    },
    
    "snake": {
        "name": "Snake / Naga",
        "desc": "Serpentine creature.",
        "parts": {
            "eyes": {"default": "hypnotic slitted eyes"},
            "fangs": {"default": "venomous fangs"},
            "tongue": {"default": "forked tongue"},
            "scales": {"default": "iridescent scales"},
            "coils": {"default": "powerful coils"},
            "cock": {
                "default": "hemipenes hidden",
                "aroused": "twin hemipenes emerged from slit",
            },
        },
        "genital_category": "reptile",
        "covering": "scales",
        "abilities": ["constrict", "venom", "heat_sense"],
    },
    
    # -------------------------------------------------------------------------
    # Aquatic Species
    # -------------------------------------------------------------------------
    "shark": {
        "name": "Shark",
        "desc": "Predatory aquatic anthro.",
        "parts": {
            "eyes": {"default": "black shark eyes"},
            "snout": {"default": "blunt shark snout"},
            "teeth": {"default": "rows of sharp teeth"},
            "fin": {"default": "dorsal fin"},
            "skin": {"default": "rough shark skin"},
            "gills": {"default": "gills"},
            "cock": {
                "default": "claspers retracted",
                "aroused": "claspers extended",
            },
        },
        "genital_category": "aquatic",
        "covering": "rough skin",
        "abilities": ["water_breathing", "blood_sense", "swim_speed"],
    },
    
    "dolphin": {
        "name": "Dolphin",
        "desc": "Playful aquatic mammal.",
        "parts": {
            "eyes": {"default": "intelligent eyes"},
            "beak": {"default": "dolphin beak"},
            "blowhole": {"default": "blowhole"},
            "fin": {"default": "dorsal fin"},
            "skin": {"default": "smooth gray skin"},
            "cock": {
                "default": "prehensile cock retracted",
                "aroused": "long prehensile cock extended",
            },
        },
        "genital_category": "aquatic",
        "covering": "smooth skin",
        "abilities": ["water_breathing", "echolocation", "swim_speed"],
    },
    
    # -------------------------------------------------------------------------
    # Avian Species
    # -------------------------------------------------------------------------
    "avian": {
        "name": "Avian",
        "desc": "Bird-like anthro.",
        "parts": {
            "eyes": {"default": "keen bird eyes"},
            "beak": {"default": "curved beak"},
            "feathers": {"default": "colorful plumage"},
            "wings": {"default": "feathered wings"},
            "talons": {"default": "sharp talons"},
            "tail_feathers": {"default": "tail feathers"},
        },
        "genital_category": "avian",
        "covering": "feathers",
        "abilities": ["flight", "keen_sight"],
    },
    
    "raven": {
        "name": "Raven",
        "desc": "Intelligent corvid anthro.",
        "parts": {
            "eyes": {"default": "cunning black eyes"},
            "beak": {"default": "sharp black beak"},
            "feathers": {"default": "glossy black feathers"},
            "wings": {"default": "dark wings"},
        },
        "genital_category": "avian",
        "covering": "feathers",
        "abilities": ["flight", "mimicry", "intelligence"],
    },
    
    # -------------------------------------------------------------------------
    # Monster Species (from Niflheim, Muspelheim, etc.)
    # -------------------------------------------------------------------------
    "slime": {
        "name": "Slime",
        "desc": "Amorphous creature.",
        "parts": {
            "body": {"default": "translucent gelatinous form"},
            "core": {"default": "glowing core"},
            "pseudopods": {"default": "shifting pseudopods"},
            "cock": {
                "default": "no visible genitals",
                "aroused": "phallic pseudopod formed",
            },
        },
        "genital_category": "tentacle",
        "covering": "slime",
        "abilities": ["amorphous", "absorb", "split"],
    },
    
    "demon": {
        "name": "Demon",
        "desc": "Infernal being from Muspelheim.",
        "parts": {
            "eyes": {"default": "burning eyes"},
            "horns": {"default": "curved horns"},
            "skin": {"default": "red skin"},
            "tail": {"default": "spaded tail"},
            "wings": {"default": "leathery bat wings"},
            "cock": {
                "default": "demonic cock",
                "aroused": "ridged infernal cock, dripping with heat",
            },
        },
        "genital_category": "human",  # Demons are human-like
        "covering": "skin",
        "abilities": ["fire_resistance", "flight", "corruption"],
    },
    
    "tentacle_beast": {
        "name": "Tentacle Beast",
        "desc": "Creature from Niflheim mists.",
        "parts": {
            "eyes": {"default": "many unblinking eyes"},
            "maw": {"default": "beaked maw"},
            "tentacles": {
                "default": "writhing tentacles",
                "aroused": "tentacles dripping with slime",
            },
        },
        "genital_category": "tentacle",
        "covering": "slime",
        "abilities": ["grapple", "multiple_attacks", "slime"],
    },
    
    # -------------------------------------------------------------------------
    # Hybrid / Special
    # -------------------------------------------------------------------------
    "futa_human": {
        "name": "Futanari (Human)",
        "desc": "Human with both sets of genitals.",
        "parts": {
            "eyes": {"default": "eyes"},
            "hair": {"default": "hair"},
            "skin": {"default": "skin"},
            "breasts": {"default": "breasts", "aroused": "flushed breasts"},
            "cock": {
                "default": "cock",
                "aroused": "hard cock",
            },
            "pussy": {
                "default": "pussy",
                "aroused": "wet pussy",
            },
        },
        "genital_category": "human",
        "covering": "skin",
        "abilities": [],
    },
    
    "futa_canine": {
        "name": "Futanari (Canine)",
        "desc": "Canine anthro with both sets.",
        "parts": {
            "eyes": {"default": "amber eyes"},
            "ears": {"default": "pointed canine ears"},
            "muzzle": {"default": "canine muzzle"},
            "tail": {"default": "bushy tail"},
            "fur": {"default": "soft fur"},
            "breasts": {"default": "fur-covered breasts"},
            "cock": {
                "default": "canine cock in sheath",
                "aroused": "red knotted cock unsheathed",
            },
            "pussy": {
                "default": "pussy hidden in fur",
                "aroused": "wet pussy, folds swollen",
            },
        },
        "genital_category": "canine",
        "covering": "fur",
        "abilities": ["enhanced_smell", "pack_tactics"],
    },
}


# =============================================================================
# MODIFIER TYPES
# =============================================================================

MODIFIER_TYPES = {
    # Size changes
    "enlarged": {
        "desc_format": "{level_adj} enlarged {part}",
        "levels": {1: "slightly", 2: "noticeably", 3: "significantly", 4: "massively", 5: "impossibly"},
        "can_be_permanent": True,
    },
    "shrunk": {
        "desc_format": "{level_adj} shrunk {part}",
        "levels": {1: "slightly", 2: "noticeably", 3: "significantly", 4: "drastically", 5: "nearly gone"},
        "can_be_permanent": True,
    },
    
    # Inflation
    "inflated": {
        "desc_format": "{part} {custom_desc}",
        "default_desc": "swollen and full",
        "levels": {1: "slightly swollen", 2: "noticeably full", 3: "heavily bloated", 4: "distended", 5: "ready to burst"},
        "can_be_permanent": False,
    },
    
    # Marks
    "marked": {
        "desc_format": "{part} {custom_desc}",
        "default_desc": "bearing marks",
        "subtypes": ["hickey", "bite", "bruise", "scratch", "handprint", "whip_mark", "rope_burn"],
        "can_be_permanent": False,
    },
    
    # Writing
    "written": {
        "desc_format": "{part} with '{text}' written on it",
        "can_be_permanent": False,
    },
    
    # Permanent body mods
    "pierced": {
        "desc_format": "{part} with {custom_desc}",
        "default_desc": "a piercing",
        "can_be_permanent": True,
    },
    "tattooed": {
        "desc_format": "{part} with {custom_desc}",
        "default_desc": "a tattoo",
        "can_be_permanent": True,
    },
    "branded": {
        "desc_format": "{part} branded with {custom_desc}",
        "default_desc": "an ownership mark",
        "can_be_permanent": True,
    },
    
    # Restraints
    "bound": {
        "desc_format": "{part} bound with {custom_desc}",
        "default_desc": "rope",
        "can_be_permanent": False,
    },
    "clamped": {
        "desc_format": "{part} with {custom_desc} attached",
        "default_desc": "clamps",
        "can_be_permanent": False,
    },
    "plugged": {
        "desc_format": "{part} filled with {custom_desc}",
        "default_desc": "a plug",
        "can_be_permanent": False,
    },
    "gagged": {
        "desc_format": "{part} filled with {custom_desc}",
        "default_desc": "a gag",
        "can_be_permanent": False,
    },
    
    # Fluids
    "dripping": {
        "desc_format": "{part} {custom_desc}",
        "default_desc": "dripping with fluids",
        "can_be_permanent": False,
    },
    "cum_covered": {
        "desc_format": "{part} {custom_desc}",
        "default_desc": "covered in cum",
        "can_be_permanent": False,
    },
    
    # Condition
    "gaped": {
        "desc_format": "{part} {level_adj} gaped",
        "levels": {1: "slightly", 2: "noticeably", 3: "widely", 4: "obscenely"},
        "can_be_permanent": False,
    },
    "stretched": {
        "desc_format": "{part} stretched {custom_desc}",
        "default_desc": "open",
        "can_be_permanent": False,
    },
    "raw": {
        "desc_format": "{part} raw and {custom_desc}",
        "default_desc": "sensitive",
        "can_be_permanent": False,
    },
}


# =============================================================================
# CORE FUNCTIONS - Body Parts
# =============================================================================

def get_body_parts(character):
    """Get character's body parts dict."""
    if not character.db.body_parts:
        character.db.body_parts = {}
    return character.db.body_parts


def get_body_states(character):
    """Get character's current body states dict."""
    if not character.db.body_states:
        character.db.body_states = {}
    return character.db.body_states


def has_part(character, part_name):
    """Check if character has a body part defined."""
    return part_name in get_body_parts(character)


def add_part(character, part_name, default_desc=None, states=None):
    """
    Add a body part to character.
    
    Args:
        character: The character
        part_name: Name of the part (e.g., "tail", "ears")
        default_desc: Default description (or just the part name)
        states: Dict of state -> description
    
    Returns:
        bool: Success
    """
    parts = get_body_parts(character)
    
    parts[part_name] = {
        "default": default_desc or part_name,
    }
    
    if states:
        parts[part_name].update(states)
    
    return True


def edit_part(character, part_name, state, description):
    """
    Edit a body part's description for a specific state.
    
    Args:
        character: The character
        part_name: Part to edit
        state: State name (e.g., "default", "aroused")
        description: New description
    
    Returns:
        bool: Success
    """
    parts = get_body_parts(character)
    
    if part_name not in parts:
        parts[part_name] = {"default": part_name}
    
    parts[part_name][state] = description
    return True


def remove_part(character, part_name):
    """Remove a body part."""
    parts = get_body_parts(character)
    if part_name in parts:
        del parts[part_name]
        return True
    return False


def set_part_state(character, part_name, state):
    """
    Set the current state of a body part.
    
    Args:
        character: The character
        part_name: Part to set
        state: State name or None for default
    """
    states = get_body_states(character)
    
    if state:
        states[part_name] = state
    elif part_name in states:
        del states[part_name]


def get_part_state(character, part_name):
    """Get current state of a body part."""
    return get_body_states(character).get(part_name, "default")


# =============================================================================
# CORE FUNCTIONS - Species
# =============================================================================

def get_species_template(species_key):
    """Get a species template by key."""
    return SPECIES_TEMPLATES.get(species_key)


def list_species():
    """Get list of available species."""
    return list(SPECIES_TEMPLATES.keys())


def apply_species(character, species_key, replace=False):
    """
    Apply a species template to character.
    
    Args:
        character: The character
        species_key: Key from SPECIES_TEMPLATES
        replace: If True, clear existing parts first
    
    Returns:
        bool: Success
    """
    template = get_species_template(species_key)
    if not template:
        return False
    
    if replace:
        character.db.body_parts = {}
        character.db.body_states = {}
    
    parts = get_body_parts(character)
    
    # Apply template parts
    for part_name, part_data in template.get("parts", {}).items():
        if part_name not in parts or replace:
            parts[part_name] = dict(part_data)
    
    # Store species info
    if not character.db.body_species:
        character.db.body_species = []
    
    if species_key not in character.db.body_species:
        character.db.body_species.append(species_key)
    
    # Store genital category for mechanics
    character.db.genital_category = template.get("genital_category", "human")
    
    # Store covering type
    character.db.body_covering = template.get("covering", "skin")
    
    # Store abilities
    if not character.db.species_abilities:
        character.db.species_abilities = []
    for ability in template.get("abilities", []):
        if ability not in character.db.species_abilities:
            character.db.species_abilities.append(ability)
    
    return True


def add_species_part(character, species_key, part_name):
    """
    Add a single part from a species template.
    
    Args:
        character: The character
        species_key: Species to pull from
        part_name: Part to add
    
    Returns:
        bool: Success
    """
    template = get_species_template(species_key)
    if not template:
        return False
    
    part_data = template.get("parts", {}).get(part_name)
    if not part_data:
        return False
    
    parts = get_body_parts(character)
    parts[part_name] = dict(part_data)
    
    # If adding genitals, update category
    if part_name == "cock" and "genital_category" in template:
        character.db.genital_category = template["genital_category"]
    
    return True


def get_genital_category(character):
    """Get character's genital category for mechanics."""
    return character.db.genital_category or "human"


def get_genital_mechanics(character):
    """Get mechanics based on genital category."""
    category = get_genital_category(character)
    return GENITAL_MECHANICS.get(category, [])


def has_mechanic(character, mechanic):
    """Check if character has a genital mechanic."""
    return mechanic in get_genital_mechanics(character)


def has_ability(character, ability):
    """Check if character has a species ability."""
    abilities = character.db.species_abilities or []
    return ability in abilities


# =============================================================================
# CORE FUNCTIONS - Modifiers
# =============================================================================

def get_body_modifiers(character):
    """Get character's body modifiers dict."""
    if not character.db.body_modifiers:
        character.db.body_modifiers = {}
    return character.db.body_modifiers


def add_modifier(character, part_name, modifier_type, **kwargs):
    """
    Add a modifier to a body part.
    
    Args:
        character: The character
        part_name: Part to modify (e.g., "neck", "breasts")
        modifier_type: Type from MODIFIER_TYPES
        **kwargs:
            level: For level-based modifiers (1-5)
            desc: Custom description
            text: For 'written' type
            duration: Seconds until expiry (None = permanent)
            permanent: Override permanence
    
    Returns:
        bool: Success
    """
    modifiers = get_body_modifiers(character)
    
    if part_name not in modifiers:
        modifiers[part_name] = []
    
    modifier = {
        "type": modifier_type,
        "added": time.time(),
    }
    
    if "level" in kwargs:
        modifier["level"] = min(5, max(1, kwargs["level"]))
    
    if "desc" in kwargs:
        modifier["desc"] = kwargs["desc"]
    
    if "text" in kwargs:
        modifier["text"] = kwargs["text"]
    
    if "duration" in kwargs and kwargs["duration"]:
        modifier["expires"] = time.time() + kwargs["duration"]
    elif kwargs.get("permanent"):
        modifier["permanent"] = True
    
    if "subtype" in kwargs:
        modifier["subtype"] = kwargs["subtype"]
    
    modifiers[part_name].append(modifier)
    return True


def remove_modifier(character, part_name, modifier_type=None, all_mods=False):
    """
    Remove modifiers from a body part.
    
    Args:
        character: The character
        part_name: Part to clear
        modifier_type: Specific type to remove, or None for all
        all_mods: Remove all modifiers of this type
    
    Returns:
        int: Number removed
    """
    modifiers = get_body_modifiers(character)
    
    if part_name not in modifiers:
        return 0
    
    if modifier_type is None:
        count = len(modifiers[part_name])
        modifiers[part_name] = []
        return count
    
    original_count = len(modifiers[part_name])
    
    if all_mods:
        modifiers[part_name] = [m for m in modifiers[part_name] if m["type"] != modifier_type]
    else:
        # Remove first matching
        for i, m in enumerate(modifiers[part_name]):
            if m["type"] == modifier_type:
                modifiers[part_name].pop(i)
                break
    
    return original_count - len(modifiers[part_name])


def get_part_modifiers(character, part_name):
    """Get all modifiers on a body part."""
    modifiers = get_body_modifiers(character)
    return modifiers.get(part_name, [])


def clean_expired_modifiers(character):
    """Remove all expired modifiers."""
    modifiers = get_body_modifiers(character)
    now = time.time()
    
    for part_name in list(modifiers.keys()):
        modifiers[part_name] = [
            m for m in modifiers[part_name]
            if m.get("permanent") or not m.get("expires") or m["expires"] > now
        ]
        if not modifiers[part_name]:
            del modifiers[part_name]


# =============================================================================
# CONVENIENCE FUNCTIONS - Common Modifiers
# =============================================================================

def mark(character, part_name, mark_type="hickey", duration=7200, desc=None):
    """Add a mark (hickey, bruise, bite, etc.)."""
    add_modifier(
        character, part_name, "marked",
        subtype=mark_type,
        desc=desc or f"covered in {mark_type}s",
        duration=duration
    )


def write_on(character, part_name, text, duration=14400):
    """Write text on a body part."""
    add_modifier(
        character, part_name, "written",
        text=text,
        duration=duration
    )


def inflate(character, part_name, level=1, duration=3600, desc=None):
    """Inflate a body part."""
    add_modifier(
        character, part_name, "inflated",
        level=level,
        desc=desc,
        duration=duration
    )


def resize(character, part_name, change, permanent=True):
    """
    Resize a body part.
    
    Args:
        change: Positive for enlarge, negative for shrink
    """
    modifier_type = "enlarged" if change > 0 else "shrunk"
    level = abs(change)
    
    add_modifier(
        character, part_name, modifier_type,
        level=level,
        permanent=permanent
    )


def bind_part(character, part_name, with_what="rope", duration=None):
    """Bind a body part."""
    add_modifier(
        character, part_name, "bound",
        desc=with_what,
        duration=duration
    )


def pierce(character, part_name, desc="a silver ring"):
    """Add a piercing."""
    add_modifier(
        character, part_name, "pierced",
        desc=desc,
        permanent=True
    )


def tattoo(character, part_name, desc="an intricate design"):
    """Add a tattoo."""
    add_modifier(
        character, part_name, "tattooed",
        desc=desc,
        permanent=True
    )


def brand(character, part_name, desc="an ownership mark"):
    """Brand a body part."""
    add_modifier(
        character, part_name, "branded",
        desc=desc,
        permanent=True
    )


def drip(character, part_name, desc="dripping with cum", duration=1800):
    """Add dripping fluid."""
    add_modifier(
        character, part_name, "dripping",
        desc=desc,
        duration=duration
    )


def gape(character, part_name, level=2, duration=3600):
    """Gape an orifice."""
    add_modifier(
        character, part_name, "gaped",
        level=level,
        duration=duration
    )


def heal_part(character, part_name):
    """Remove temporary marks from a part."""
    modifiers = get_body_modifiers(character)
    if part_name not in modifiers:
        return
    
    modifiers[part_name] = [
        m for m in modifiers[part_name]
        if m.get("permanent")
    ]


def clean_part(character, part_name):
    """Remove writing and fluids from a part."""
    modifiers = get_body_modifiers(character)
    if part_name not in modifiers:
        return
    
    washable = ["written", "dripping", "cum_covered"]
    modifiers[part_name] = [
        m for m in modifiers[part_name]
        if m["type"] not in washable
    ]


def heal_all(character):
    """Remove all temporary marks."""
    modifiers = get_body_modifiers(character)
    for part_name in list(modifiers.keys()):
        heal_part(character, part_name)


def clean_all(character):
    """Clean all writing and fluids."""
    modifiers = get_body_modifiers(character)
    for part_name in list(modifiers.keys()):
        clean_part(character, part_name)


# =============================================================================
# SHORTCODE PROCESSOR
# =============================================================================

def get_part_description(character, part_name, force_state=None):
    """
    Get the full description of a body part including modifiers.
    
    Args:
        character: The character
        part_name: Part to describe
        force_state: Override current state
    
    Returns:
        str: Full description
    """
    clean_expired_modifiers(character)
    
    parts = get_body_parts(character)
    
    # Get base description
    if part_name in parts:
        part_data = parts[part_name]
        state = force_state or get_part_state(character, part_name)
        
        # Check for arousal from effects
        if not force_state and state == "default":
            from world.effects import has_effect
            if has_effect(character, "aroused") and "aroused" in part_data:
                state = "aroused"
        
        base_desc = part_data.get(state, part_data.get("default", part_name))
    else:
        # No custom part defined, use part name
        base_desc = part_name
    
    # Apply modifiers
    modifiers = get_part_modifiers(character, part_name)
    
    if not modifiers:
        return base_desc
    
    # Build modifier descriptions
    modifier_descs = []
    
    for mod in modifiers:
        mod_type = mod["type"]
        mod_info = MODIFIER_TYPES.get(mod_type, {})
        
        if mod_type == "written":
            modifier_descs.append(f"with '{mod.get('text', '???')}' written on it")
        
        elif mod_type in ("enlarged", "shrunk", "gaped"):
            level = mod.get("level", 1)
            level_adj = mod_info.get("levels", {}).get(level, "")
            modifier_descs.append(f"{level_adj} {mod_type}")
        
        elif mod_type == "inflated":
            level = mod.get("level", 1)
            desc = mod.get("desc") or mod_info.get("levels", {}).get(level, mod_info.get("default_desc", "swollen"))
            modifier_descs.append(desc)
        
        elif mod_type in ("marked", "bound", "pierced", "tattooed", "branded", "dripping", "cum_covered"):
            desc = mod.get("desc") or mod_info.get("default_desc", "")
            if desc:
                modifier_descs.append(desc)
        
        elif mod_type in ("clamped", "plugged", "gagged"):
            desc = mod.get("desc") or mod_info.get("default_desc", "")
            if desc:
                modifier_descs.append(f"with {desc}")
    
    # Combine base + modifiers
    if modifier_descs:
        return f"{base_desc}, {', '.join(modifier_descs)}"
    
    return base_desc


def get_worn_description(character, slot):
    """
    Get description of worn equipment in a slot.
    
    Args:
        character: The character
        slot: Equipment slot (e.g., "chest", "legs")
    
    Returns:
        str: Item description or empty string
    """
    try:
        from world.items import get_equipped
        
        item = get_equipped(character, slot)
        if item:
            return item.db.desc or item.key
    except ImportError:
        pass
    
    return ""


def process_shortcodes(character, text):
    """
    Process shortcodes in text.
    
    Supported codes:
        <body.X> - Body part description
        <body.X.state> - Force specific state
        <worn.X> - Equipment in slot X
        <name> - Character name
        <pronoun.X> - Pronouns (he/she/they/his/her/their/him/her/them)
        <position> - Current position description
        <pose> - Current pose only
    
    Args:
        character: The character
        text: Text with shortcodes
    
    Returns:
        str: Processed text
    """
    import re
    
    def replace_code(match):
        code = match.group(1)
        parts = code.split(".")
        
        code_type = parts[0]
        
        if code_type == "body" and len(parts) >= 2:
            part_name = parts[1]
            force_state = parts[2] if len(parts) > 2 else None
            return get_part_description(character, part_name, force_state)
        
        elif code_type == "worn" and len(parts) >= 2:
            slot = parts[1]
            return get_worn_description(character, slot)
        
        elif code_type == "name":
            return character.key
        
        elif code_type == "pronoun" and len(parts) >= 2:
            return get_pronoun(character, parts[1])
        
        elif code_type == "position":
            return get_position_desc(character)
        
        elif code_type == "pose":
            pos = character.db.position or {}
            return pos.get("pose", "standing")
        
        # Unknown code, return as-is
        return match.group(0)
    
    return re.sub(r"<([^>]+)>", replace_code, text)


def get_pronoun(character, pronoun_type):
    """Get appropriate pronoun for character."""
    pronouns = character.db.pronouns or "they/them/their"
    
    # Parse stored pronouns
    parts = pronouns.split("/")
    
    mapping = {
        "subject": 0,      # he/she/they
        "object": 1,       # him/her/them
        "possessive": 2,   # his/her/their
        "he": 0, "she": 0, "they": 0,
        "him": 1, "her": 1, "them": 1,
        "his": 2, "hers": 2, "their": 2, "theirs": 2,
    }
    
    idx = mapping.get(pronoun_type.lower(), 0)
    if idx < len(parts):
        return parts[idx]
    
    return "they"


def get_position_desc(character):
    """Get position description."""
    pos = character.db.position
    if not pos:
        return "standing"
    
    pose = pos.get("pose", "standing")
    furniture_id = pos.get("furniture")
    
    if furniture_id:
        try:
            from evennia.objects.models import ObjectDB
            furniture = ObjectDB.objects.get(id=furniture_id)
            return f"{pose} on {furniture.key}"
        except:
            pass
    
    return pose


# =============================================================================
# DISPLAY FUNCTIONS
# =============================================================================

def get_body_display(character, show_modifiers=True):
    """
    Get formatted display of all body parts.
    
    Args:
        character: The character
        show_modifiers: Include modifier information
    
    Returns:
        str: Formatted display
    """
    clean_expired_modifiers(character)
    
    lines = []
    lines.append(f"|wBody - {character.key}|n")
    lines.append("-" * 40)
    
    # Species
    species = character.db.body_species or []
    if species:
        lines.append(f"Species: {', '.join(species)}")
    
    # Covering
    covering = character.db.body_covering
    if covering:
        lines.append(f"Covering: {covering}")
    
    # Genital mechanics
    mechanics = get_genital_mechanics(character)
    if mechanics:
        lines.append(f"Mechanics: {', '.join(mechanics)}")
    
    lines.append("")
    lines.append("|cBody Parts:|n")
    
    parts = get_body_parts(character)
    states = get_body_states(character)
    
    for part_name, part_data in parts.items():
        current_state = states.get(part_name, "default")
        desc = get_part_description(character, part_name)
        
        state_indicator = f" [{current_state}]" if current_state != "default" else ""
        lines.append(f"  {part_name}{state_indicator}: {desc}")
    
    if show_modifiers:
        modifiers = get_body_modifiers(character)
        if modifiers:
            lines.append("")
            lines.append("|cActive Modifiers:|n")
            for part_name, mods in modifiers.items():
                for mod in mods:
                    mod_type = mod["type"]
                    permanent = "permanent" if mod.get("permanent") else ""
                    expires = ""
                    if mod.get("expires"):
                        remaining = int(mod["expires"] - time.time())
                        if remaining > 0:
                            mins = remaining // 60
                            expires = f"({mins}m remaining)"
                    
                    lines.append(f"  {part_name}: {mod_type} {permanent} {expires}".strip())
    
    return "\n".join(lines)


def get_modifier_display(character):
    """Get just the modifiers display."""
    clean_expired_modifiers(character)
    
    lines = []
    lines.append("|wBody Modifiers|n")
    lines.append("-" * 40)
    
    modifiers = get_body_modifiers(character)
    
    if not modifiers:
        lines.append("No active modifiers.")
        return "\n".join(lines)
    
    for part_name, mods in modifiers.items():
        for mod in mods:
            mod_type = mod["type"]
            desc_parts = [f"|c{part_name}|n: {mod_type}"]
            
            if mod.get("level"):
                desc_parts.append(f"(level {mod['level']})")
            
            if mod.get("text"):
                desc_parts.append(f'"{mod["text"]}"')
            
            if mod.get("desc"):
                desc_parts.append(f"- {mod['desc']}")
            
            if mod.get("permanent"):
                desc_parts.append("|y[permanent]|n")
            elif mod.get("expires"):
                remaining = int(mod["expires"] - time.time())
                if remaining > 0:
                    mins = remaining // 60
                    desc_parts.append(f"|x({mins}m)|n")
            
            lines.append("  " + " ".join(desc_parts))
    
    return "\n".join(lines)
