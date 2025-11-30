"""
Body Species - Feature Sets

Species defines cosmetic features that layer onto structure and anatomy.
This is the third layer of body composition.

Species features include:
    - Ear type
    - Tail type  
    - Muzzle/face type
    - Fur/scale/skin covering
    - Coloration hints
    - Special features (horns, wings, etc.)
"""

from dataclasses import dataclass, field
from typing import List, Dict, Optional


@dataclass
class SpeciesFeatures:
    """
    Defines species-specific cosmetic features.
    """
    
    key: str                          # Feature set identifier
    name: str                         # Display name
    description: str = ""
    
    # Parts this species adds
    adds_parts: List[str] = field(default_factory=list)
    
    # Parts this species removes
    removes_parts: List[str] = field(default_factory=list)
    
    # Parts this species REPLACES
    # Example: {"left_ear": "left_ear_canine"} 
    replaces_parts: Dict[str, str] = field(default_factory=dict)
    
    # Default descriptions for parts
    part_descriptions: Dict[str, str] = field(default_factory=dict)
    
    # Covering type
    covering_type: str = "skin"
    # Types: skin, fur, scales, feathers, chitin, slime, none
    
    covering_description: str = ""
    
    # GENITAL CATEGORY
    # Determines which genital type is used when applying sex config
    # Types: human, canine, equine, feline, reptile, aquatic, avian, insect, none
    genital_category: str = "human"
    
    # Innate abilities from species
    innate_abilities: List[str] = field(default_factory=list)
    # Examples: enhanced_smell, darkvision, water_breathing, flight, venom
    
    # Compatible with these structures
    compatible_structures: List[str] = field(default_factory=list)
    # Empty = compatible with all


# =============================================================================
# HUMANOID SPECIES
# =============================================================================

HUMAN = SpeciesFeatures(
    key="human",
    name="Human",
    description="Standard human features.",
    adds_parts=["hair"],
    covering_type="skin",
    covering_description="Smooth skin in various tones.",
    genital_category="human",
)

ELF = SpeciesFeatures(
    key="elf",
    name="Elf",
    description="Graceful humanoid with pointed ears.",
    adds_parts=["hair"],
    replaces_parts={
        "left_ear": "left_ear_pointed",
        "right_ear": "right_ear_pointed",
    },
    part_descriptions={
        "left_ear_pointed": "A long, elegantly pointed ear.",
        "right_ear_pointed": "A long, elegantly pointed ear.",
    },
    covering_type="skin",
    genital_category="human",
    innate_abilities=["darkvision", "trance"],
    compatible_structures=["bipedal_plantigrade"],
)

DWARF = SpeciesFeatures(
    key="dwarf",
    name="Dwarf",
    description="Stocky humanoid, often bearded.",
    adds_parts=["hair"],
    part_descriptions={
        "hair": "Thick, often braided hair.",
        "torso": "A broad, barrel-chested torso.",
    },
    covering_type="skin",
    genital_category="human",
    innate_abilities=["darkvision", "poison_resistance"],
    compatible_structures=["bipedal_plantigrade"],
)

ORC = SpeciesFeatures(
    key="orc",
    name="Orc",
    description="Muscular humanoid with tusks.",
    adds_parts=["hair", "tusks"],
    part_descriptions={
        "tusks": "Prominent tusks jutting from the lower jaw.",
        "torso": "A heavily muscled torso.",
    },
    covering_type="skin",
    covering_description="Thick, often greenish skin.",
    genital_category="human",
    compatible_structures=["bipedal_plantigrade"],
)

GOBLIN = SpeciesFeatures(
    key="goblin",
    name="Goblin",
    description="Small, wiry humanoid with pointed ears.",
    replaces_parts={
        "left_ear": "left_ear_pointed",
        "right_ear": "right_ear_pointed",
    },
    part_descriptions={
        "left_ear_pointed": "A large, pointed ear.",
        "right_ear_pointed": "A large, pointed ear.",
    },
    covering_type="skin",
    covering_description="Rough, often greenish skin.",
    genital_category="human",
    innate_abilities=["darkvision"],
    compatible_structures=["bipedal_plantigrade"],
)

TIEFLING = SpeciesFeatures(
    key="tiefling",
    name="Tiefling",
    description="Humanoid with demonic heritage - horns and tail.",
    adds_parts=["hair", "horns_demon", "tail_demon"],
    part_descriptions={
        "horns_demon": "Curved horns rising from the forehead.",
        "tail_demon": "A long, pointed tail with a spade tip.",
    },
    covering_type="skin",
    covering_description="Skin in various colors, often with an unusual hue.",
    genital_category="human",
    innate_abilities=["darkvision", "fire_resistance"],
    compatible_structures=["bipedal_plantigrade"],
)


# =============================================================================
# CANINE SPECIES
# =============================================================================

CANINE_GENERIC = SpeciesFeatures(
    key="canine_generic",
    name="Canine",
    description="Generic canine features.",
    adds_parts=["scruff"],
    replaces_parts={
        "face": "muzzle_canine",
        "nose": "muzzle_canine",  # Muzzle provides smell
        "left_ear": "left_ear_canine",
        "right_ear": "right_ear_canine",
    },
    part_descriptions={
        "muzzle_canine": "A canine muzzle with a wet nose.",
        "left_ear_canine": "A pointed, furred ear that swivels attentively.",
        "right_ear_canine": "A pointed, furred ear that swivels attentively.",
    },
    covering_type="fur",
    covering_description="Soft fur covering the body.",
    genital_category="canine",
    innate_abilities=["enhanced_smell", "enhanced_hearing"],
)

WOLF = SpeciesFeatures(
    key="wolf",
    name="Wolf",
    description="Lupine features - powerful and wild.",
    adds_parts=["tail_canine", "scruff", "fangs"],
    replaces_parts={
        "face": "muzzle_canine",
        "nose": "muzzle_canine",
        "left_ear": "left_ear_canine",
        "right_ear": "right_ear_canine",
    },
    part_descriptions={
        "muzzle_canine": "A long, powerful wolf muzzle.",
        "tail_canine": "A thick, bushy wolf tail.",
        "scruff": "A thick scruff of fur around the neck.",
        "fangs": "Sharp canine fangs.",
    },
    covering_type="fur",
    covering_description="Thick, luxurious wolf fur.",
    genital_category="canine",
    innate_abilities=["enhanced_smell", "enhanced_hearing", "pack_tactics"],
)

DOG = SpeciesFeatures(
    key="dog",
    name="Dog",
    description="Domestic canine features.",
    adds_parts=["tail_canine", "scruff"],
    replaces_parts={
        "face": "muzzle_canine",
        "nose": "muzzle_canine",
        "left_ear": "left_ear_canine",
        "right_ear": "right_ear_canine",
    },
    part_descriptions={
        "muzzle_canine": "A friendly canine muzzle.",
        "tail_canine": "A wagging dog tail.",
    },
    covering_type="fur",
    genital_category="canine",
    innate_abilities=["enhanced_smell", "enhanced_hearing"],
)

FOX = SpeciesFeatures(
    key="fox",
    name="Fox",
    description="Vulpine features - cunning and agile.",
    adds_parts=["tail_vulpine", "scruff"],
    replaces_parts={
        "face": "muzzle_canine",
        "nose": "muzzle_canine",
        "left_ear": "left_ear_canine",
        "right_ear": "right_ear_canine",
    },
    part_descriptions={
        "muzzle_canine": "A slender, pointed fox muzzle.",
        "tail_vulpine": "A large, fluffy fox tail.",
    },
    covering_type="fur",
    covering_description="Soft, thick fox fur.",
    genital_category="canine",
    innate_abilities=["enhanced_smell", "enhanced_hearing", "agility"],
)

HYENA = SpeciesFeatures(
    key="hyena",
    name="Hyena",
    description="Hyena features - powerful jaws and sloped back.",
    adds_parts=["tail_canine", "mane", "scruff"],
    replaces_parts={
        "face": "muzzle_canine",
        "nose": "muzzle_canine",
        "left_ear": "left_ear_canine",
        "right_ear": "right_ear_canine",
    },
    part_descriptions={
        "muzzle_canine": "A broad, powerful hyena muzzle with strong jaws.",
        "mane": "A coarse mane running down the neck and back.",
    },
    covering_type="fur",
    covering_description="Coarse, spotted fur.",
    genital_category="canine",
    innate_abilities=["enhanced_smell", "powerful_jaws"],
)


# =============================================================================
# FELINE SPECIES
# =============================================================================

FELINE_GENERIC = SpeciesFeatures(
    key="feline_generic",
    name="Feline",
    description="Generic feline features.",
    replaces_parts={
        "face": "muzzle_feline",
        "nose": "muzzle_feline",
        "left_ear": "left_ear_feline",
        "right_ear": "right_ear_feline",
    },
    part_descriptions={
        "muzzle_feline": "A short feline muzzle with whiskers.",
        "left_ear_feline": "A triangular, tufted ear.",
        "right_ear_feline": "A triangular, tufted ear.",
    },
    covering_type="fur",
    covering_description="Soft, sleek fur.",
    genital_category="feline",
    innate_abilities=["darkvision", "enhanced_hearing", "retractable_claws"],
)

CAT = SpeciesFeatures(
    key="cat",
    name="Cat",
    description="Domestic feline features.",
    adds_parts=["tail_feline"],
    replaces_parts={
        "face": "muzzle_feline",
        "nose": "muzzle_feline",
        "left_ear": "left_ear_feline",
        "right_ear": "right_ear_feline",
    },
    part_descriptions={
        "muzzle_feline": "A small feline muzzle with delicate whiskers.",
        "tail_feline": "A long, expressive feline tail.",
    },
    covering_type="fur",
    genital_category="feline",
    innate_abilities=["darkvision", "enhanced_hearing", "retractable_claws", "agility"],
)

LION = SpeciesFeatures(
    key="lion",
    name="Lion",
    description="Leonine features - majestic with optional mane.",
    adds_parts=["tail_feline"],  # Mane added separately for males
    replaces_parts={
        "face": "muzzle_feline",
        "nose": "muzzle_feline",
        "left_ear": "left_ear_feline",
        "right_ear": "right_ear_feline",
    },
    part_descriptions={
        "muzzle_feline": "A broad, powerful lion muzzle.",
        "tail_feline": "A tufted lion tail.",
    },
    covering_type="fur",
    covering_description="Short, tawny fur.",
    genital_category="feline",
    innate_abilities=["darkvision", "enhanced_hearing", "powerful_roar"],
)

TIGER = SpeciesFeatures(
    key="tiger",
    name="Tiger",
    description="Striped feline predator.",
    adds_parts=["tail_feline"],
    replaces_parts={
        "face": "muzzle_feline",
        "nose": "muzzle_feline",
        "left_ear": "left_ear_feline",
        "right_ear": "right_ear_feline",
    },
    part_descriptions={
        "muzzle_feline": "A powerful tiger muzzle with distinctive markings.",
        "tail_feline": "A thick, striped tail.",
    },
    covering_type="fur",
    covering_description="Orange fur with distinctive black stripes.",
    genital_category="feline",
    innate_abilities=["darkvision", "enhanced_hearing", "stealth"],
)

LEOPARD = SpeciesFeatures(
    key="leopard",
    name="Leopard",
    description="Spotted feline - agile and stealthy.",
    adds_parts=["tail_feline"],
    replaces_parts={
        "face": "muzzle_feline",
        "nose": "muzzle_feline",
        "left_ear": "left_ear_feline",
        "right_ear": "right_ear_feline",
    },
    covering_type="fur",
    covering_description="Golden fur with dark rosette spots.",
    genital_category="feline",
    innate_abilities=["darkvision", "enhanced_hearing", "stealth", "climbing"],
)


# =============================================================================
# EQUINE SPECIES
# =============================================================================

EQUINE_GENERIC = SpeciesFeatures(
    key="equine_generic",
    name="Equine",
    description="Generic equine features.",
    adds_parts=["mane"],
    replaces_parts={
        "face": "muzzle_equine",
        "nose": "muzzle_equine",
        "left_ear": "left_ear_equine",
        "right_ear": "right_ear_equine",
    },
    part_descriptions={
        "muzzle_equine": "A long equine muzzle with soft lips.",
        "left_ear_equine": "A long, mobile ear.",
        "right_ear_equine": "A long, mobile ear.",
        "mane": "A thick, flowing mane.",
    },
    covering_type="fur",
    covering_description="Short, sleek coat.",
    genital_category="equine",
)

HORSE = SpeciesFeatures(
    key="horse",
    name="Horse",
    description="Equine features - powerful and graceful.",
    adds_parts=["tail_equine", "mane"],
    replaces_parts={
        "face": "muzzle_equine",
        "nose": "muzzle_equine",
        "left_ear": "left_ear_equine",
        "right_ear": "right_ear_equine",
    },
    part_descriptions={
        "tail_equine": "A long, flowing tail.",
        "mane": "A thick, luxurious mane.",
    },
    covering_type="fur",
    covering_description="Sleek, short coat.",
    genital_category="equine",
    innate_abilities=["enhanced_speed", "endurance"],
)

UNICORN = SpeciesFeatures(
    key="unicorn",
    name="Unicorn",
    description="Magical equine with a single horn.",
    adds_parts=["tail_equine", "mane", "horns"],
    replaces_parts={
        "face": "muzzle_equine",
        "nose": "muzzle_equine",
        "left_ear": "left_ear_equine",
        "right_ear": "right_ear_equine",
    },
    part_descriptions={
        "horns": "A single, spiraling horn of pure magic.",
    },
    covering_type="fur",
    covering_description="Pristine, often white coat.",
    genital_category="equine",
    innate_abilities=["magic", "healing", "purity"],
)

ZEBRA = SpeciesFeatures(
    key="zebra",
    name="Zebra",
    description="Striped equine.",
    adds_parts=["tail_equine", "mane"],
    replaces_parts={
        "face": "muzzle_equine",
        "nose": "muzzle_equine",
        "left_ear": "left_ear_equine",
        "right_ear": "right_ear_equine",
    },
    covering_type="fur",
    covering_description="White fur with distinctive black stripes.",
    genital_category="equine",
)


# =============================================================================
# LAPINE SPECIES
# =============================================================================

RABBIT = SpeciesFeatures(
    key="rabbit",
    name="Rabbit",
    description="Lapine features - long ears and cotton tail.",
    adds_parts=["tail_lapine"],
    replaces_parts={
        "left_ear": "left_ear_lapine",
        "right_ear": "right_ear_lapine",
    },
    part_descriptions={
        "left_ear_lapine": "A very long, floppy ear.",
        "right_ear_lapine": "A very long, floppy ear.",
        "tail_lapine": "A small, fluffy cotton tail.",
    },
    covering_type="fur",
    covering_description="Soft, plush fur.",
    genital_category="human",  # Lapines typically use humanoid genitals in furry contexts
    innate_abilities=["enhanced_hearing", "enhanced_speed", "agility"],
)

HARE = SpeciesFeatures(
    key="hare",
    name="Hare",
    description="Similar to rabbit but larger and more athletic.",
    adds_parts=["tail_lapine"],
    replaces_parts={
        "left_ear": "left_ear_lapine",
        "right_ear": "right_ear_lapine",
    },
    part_descriptions={
        "left_ear_lapine": "Long, upright ears.",
        "right_ear_lapine": "Long, upright ears.",
    },
    covering_type="fur",
    genital_category="human",
    innate_abilities=["enhanced_hearing", "enhanced_speed", "leaping"],
)


# =============================================================================
# REPTILE SPECIES
# =============================================================================

LIZARD = SpeciesFeatures(
    key="lizard",
    name="Lizard",
    description="Generic lizard features.",
    adds_parts=["tail_reptile", "tongue_forked"],
    removes_parts=["tongue"],
    replaces_parts={
        "face": "snout",
        "nose": "snout",
    },
    part_descriptions={
        "snout": "A scaled snout with a forked tongue.",
        "tail_reptile": "A thick, scaled tail.",
    },
    covering_type="scales",
    covering_description="Smooth, iridescent scales.",
    genital_category="reptile",
    innate_abilities=["cold_blooded", "regeneration"],
)

DRAGON = SpeciesFeatures(
    key="dragon",
    name="Dragon",
    description="Draconic features - horns, wings, scales.",
    adds_parts=["horns", "tail_reptile", "wings_dragon", "fangs", "tongue_forked"],
    removes_parts=["tongue"],
    replaces_parts={
        "face": "snout",
        "nose": "snout",
    },
    part_descriptions={
        "horns": "Majestic draconic horns.",
        "wings_dragon": "Massive, scaled wings.",
        "tail_reptile": "A powerful, armored tail.",
    },
    covering_type="scales",
    covering_description="Thick, armored scales.",
    genital_category="reptile",
    innate_abilities=["flight", "breath_weapon", "darkvision", "fire_resistance"],
)

KOBOLD = SpeciesFeatures(
    key="kobold",
    name="Kobold",
    description="Small draconic humanoid.",
    adds_parts=["tail_reptile", "horns"],
    replaces_parts={
        "face": "snout",
        "nose": "snout",
    },
    covering_type="scales",
    covering_description="Small, fine scales.",
    genital_category="reptile",
    innate_abilities=["darkvision", "trap_sense"],
    compatible_structures=["bipedal_plantigrade"],
)

SNAKE = SpeciesFeatures(
    key="snake",
    name="Snake",
    description="Serpentine features for lamia/naga.",
    adds_parts=["fangs", "tongue_forked"],
    removes_parts=["tongue"],
    replaces_parts={
        "face": "snout",
        "nose": "snout",
    },
    part_descriptions={
        "fangs": "Venomous fangs.",
        "tongue_forked": "A long, forked tongue that tastes the air.",
    },
    covering_type="scales",
    covering_description="Smooth, iridescent scales.",
    genital_category="reptile",
    innate_abilities=["enhanced_smell", "heat_sense", "constrict"],
    compatible_structures=["serpentine"],
)


# =============================================================================
# AVIAN SPECIES
# =============================================================================

BIRD = SpeciesFeatures(
    key="bird",
    name="Bird",
    description="Generic avian features.",
    adds_parts=["crest"],
    replaces_parts={
        "mouth": "beak",
    },
    covering_type="feathers",
    covering_description="Colorful plumage.",
    genital_category="avian",
    innate_abilities=["flight"],
)

RAVEN = SpeciesFeatures(
    key="raven",
    name="Raven",
    description="Corvid features - intelligent and dark-feathered.",
    replaces_parts={
        "mouth": "beak",
    },
    part_descriptions={
        "beak": "A sharp, curved black beak.",
    },
    covering_type="feathers",
    covering_description="Glossy black feathers.",
    genital_category="avian",
    innate_abilities=["flight", "intelligence", "mimicry"],
)

EAGLE = SpeciesFeatures(
    key="eagle",
    name="Eagle",
    description="Raptor features - keen eyes and powerful talons.",
    replaces_parts={
        "mouth": "beak",
    },
    part_descriptions={
        "beak": "A hooked, powerful beak.",
    },
    covering_type="feathers",
    genital_category="avian",
    innate_abilities=["flight", "keen_sight"],
)


# =============================================================================
# AQUATIC SPECIES
# =============================================================================

FISH = SpeciesFeatures(
    key="fish",
    name="Fish",
    description="Aquatic features for merfolk.",
    adds_parts=["dorsal_fin", "pectoral_fins", "gills"],
    covering_type="scales",
    covering_description="Iridescent fish scales.",
    genital_category="aquatic",
    innate_abilities=["water_breathing", "swim_speed"],
    compatible_structures=["aquatic"],
)

SHARK = SpeciesFeatures(
    key="shark",
    name="Shark",
    description="Predatory aquatic features.",
    adds_parts=["dorsal_fin", "gills", "fangs"],
    covering_type="scales",
    covering_description="Rough, sandpaper-like skin.",
    genital_category="aquatic",
    innate_abilities=["water_breathing", "swim_speed", "blood_sense"],
    compatible_structures=["aquatic"],
)

DOLPHIN = SpeciesFeatures(
    key="dolphin",
    name="Dolphin",
    description="Cetacean features - playful and intelligent.",
    adds_parts=["dorsal_fin"],
    replaces_parts={
        "face": "snout",
        "nose": "snout",
    },
    part_descriptions={
        "snout": "A long, bottle-like snout.",
    },
    covering_type="skin",
    covering_description="Smooth, rubbery skin.",
    genital_category="aquatic",
    innate_abilities=["water_breathing", "swim_speed", "echolocation"],
)


# =============================================================================
# DEMON/ANGEL SPECIES
# =============================================================================

ANGEL = SpeciesFeatures(
    key="angel",
    name="Angel",
    description="Divine features - feathered wings and radiance.",
    adds_parts=["hair", "wings_feathered"],
    part_descriptions={
        "wings_feathered": "Large, pristine white feathered wings.",
    },
    covering_type="skin",
    covering_description="Flawless, often luminous skin.",
    genital_category="human",
    innate_abilities=["flight", "divine_resistance", "radiance"],
    compatible_structures=["bipedal_plantigrade"],
)

DEMON = SpeciesFeatures(
    key="demon",
    name="Demon",
    description="Infernal features - horns, tail, bat wings.",
    adds_parts=["hair", "horns_demon", "tail_demon", "wings_bat"],
    part_descriptions={
        "horns_demon": "Curved demonic horns.",
        "tail_demon": "A long, pointed tail.",
        "wings_bat": "Leathery bat-like wings.",
    },
    covering_type="skin",
    covering_description="Skin in unusual colors - red, purple, or black.",
    genital_category="human",
    innate_abilities=["flight", "fire_resistance", "darkvision"],
    compatible_structures=["bipedal_plantigrade"],
)

SUCCUBUS = SpeciesFeatures(
    key="succubus",
    name="Succubus",
    description="Seductive demon - horns, tail, wings.",
    adds_parts=["hair", "horns_demon", "tail_demon", "wings_bat"],
    part_descriptions={
        "horns_demon": "Elegant, curved horns.",
        "tail_demon": "A sinuous, spade-tipped tail.",
        "wings_bat": "Sleek, dark wings.",
    },
    covering_type="skin",
    covering_description="Flawless, alluring skin in unusual hues.",
    genital_category="human",
    innate_abilities=["flight", "seduction", "darkvision", "charm"],
    compatible_structures=["bipedal_plantigrade"],
)


# =============================================================================
# INSECTOID SPECIES
# =============================================================================

BEE = SpeciesFeatures(
    key="bee",
    name="Bee",
    description="Bee features - antennae, wings, stinger.",
    adds_parts=["antennae", "wings_insect", "stinger"],
    covering_type="chitin",
    covering_description="Fuzzy yellow and black chitin.",
    genital_category="insect",
    innate_abilities=["flight", "enhanced_smell"],
)

ANT = SpeciesFeatures(
    key="ant",
    name="Ant",
    description="Ant features - antennae, mandibles, exoskeleton.",
    adds_parts=["antennae", "mandibles", "exoskeleton"],
    replaces_parts={
        "mouth": "mandibles",
    },
    covering_type="chitin",
    covering_description="Hard, segmented chitin.",
    genital_category="insect",
    innate_abilities=["enhanced_smell", "strength"],
)

SPIDER = SpeciesFeatures(
    key="spider",
    name="Spider",
    description="Arachnid features - multiple eyes, spinnerets.",
    adds_parts=["compound_eyes", "fangs"],
    covering_type="chitin",
    covering_description="Smooth, often hairy chitin.",
    genital_category="insect",
    innate_abilities=["web_spinning", "wall_climbing", "venom"],
)


# =============================================================================
# MISC SPECIES
# =============================================================================

SLIME_SPECIES = SpeciesFeatures(
    key="slime_species",
    name="Slime",
    description="Amorphous, gelatinous being.",
    covering_type="slime",
    covering_description="Translucent, gelatinous body.",
    genital_category="none",  # Can manifest any
    innate_abilities=["amorphous", "acid_resistance", "regeneration"],
)

ROBOT = SpeciesFeatures(
    key="robot",
    name="Robot",
    description="Mechanical/android features.",
    covering_type="none",
    covering_description="Metal plating and synthetic materials.",
    genital_category="none",  # Optional attachments
    innate_abilities=["mechanical", "no_breathing", "poison_immunity"],
)


# =============================================================================
# SPECIES REGISTRY
# =============================================================================

SPECIES_REGISTRY: Dict[str, SpeciesFeatures] = {
    # Humanoid
    "human": HUMAN,
    "elf": ELF,
    "dwarf": DWARF,
    "orc": ORC,
    "goblin": GOBLIN,
    "tiefling": TIEFLING,
    
    # Canine
    "canine_generic": CANINE_GENERIC,
    "wolf": WOLF,
    "dog": DOG,
    "fox": FOX,
    "hyena": HYENA,
    
    # Feline
    "feline_generic": FELINE_GENERIC,
    "cat": CAT,
    "lion": LION,
    "tiger": TIGER,
    "leopard": LEOPARD,
    
    # Equine
    "equine_generic": EQUINE_GENERIC,
    "horse": HORSE,
    "unicorn": UNICORN,
    "zebra": ZEBRA,
    
    # Lapine
    "rabbit": RABBIT,
    "hare": HARE,
    
    # Reptile
    "lizard": LIZARD,
    "dragon": DRAGON,
    "kobold": KOBOLD,
    "snake": SNAKE,
    
    # Avian
    "bird": BIRD,
    "raven": RAVEN,
    "eagle": EAGLE,
    
    # Aquatic
    "fish": FISH,
    "shark": SHARK,
    "dolphin": DOLPHIN,
    
    # Demon/Angel
    "angel": ANGEL,
    "demon": DEMON,
    "succubus": SUCCUBUS,
    
    # Insectoid
    "bee": BEE,
    "ant": ANT,
    "spider": SPIDER,
    
    # Misc
    "slime_species": SLIME_SPECIES,
    "robot": ROBOT,
}


def get_species(key: str) -> Optional[SpeciesFeatures]:
    """Get a species feature set by key."""
    return SPECIES_REGISTRY.get(key)


def list_species() -> List[str]:
    """List all species keys."""
    return list(SPECIES_REGISTRY.keys())


def get_species_by_covering(covering_type: str) -> List[SpeciesFeatures]:
    """Get all species with a specific covering type."""
    return [s for s in SPECIES_REGISTRY.values() if s.covering_type == covering_type]
