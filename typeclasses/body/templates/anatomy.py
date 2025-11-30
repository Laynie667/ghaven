"""
Body Anatomy - Sex Configurations

ORDER OF COMPOSITION:
    STRUCTURE → SPECIES → ANATOMY → PRESENTATION
    
Anatomy defines SEX CONFIGURATION (which holes/bits you have).
The STYLE of those bits comes from the species' genital_category.

Sex configurations:
    - male: Cock + balls
    - female: Pussy + womb + breasts (3 orifices: mouth, pussy, ass)
    - herm: Both full sets (3 orifices + cock)
    - futa: Female body + cock, no balls (3 orifices + cock)
    - maleherm: Male body + pussy added
    - cuntboy: Male presentation, pussy instead of cock
    - femboy: Male genitals, feminine presentation
    - dickgirl: Female body + cock + balls, no pussy
    - neuter: No sexual organs
    - doll: Breasts only, no genitals

ORIFICES:
    All bodies have: mouth, asshole
    Female/herm/futa/cuntboy add: pussy
    Reptile/avian replace asshole with: cloaca

The compose() function looks up which PARTS to use based on:
    species.genital_category + sex_config
    
Example:
    Wolf + Female = canine-style pussy (same mechanics, species flavor text)
    Horse + Male = equine cock (flare, massive, sheath)
"""

from dataclasses import dataclass, field
from typing import List, Dict, Optional

# Import from the sexual parts module for the actual part definitions
# The parts_sexual module has all the mechanical details
from .parts_sexual import (
    get_male_parts, 
    get_female_parts, 
    get_breast_parts,
    OrificeMechanics,
    PenetratorMechanics,
)


@dataclass 
class SexConfig:
    """
    Defines sex configuration (what organs/characteristics).
    
    Does NOT specify which genital type - that comes from species.
    Species determines if you have a human cock, dog cock, horse cock, etc.
    This just determines IF you have a cock at all.
    """
    
    key: str                          # Config identifier
    name: str                         # Display name
    description: str = ""
    
    # === WHAT THIS SEX HAS ===
    has_cock: bool = False            # Any type of penetrator
    has_balls: bool = False           # Testicles
    has_pussy: bool = False           # Vaginal orifice
    has_womb: bool = False            # Internal reproductive
    has_breasts: bool = False         # Chest
    has_prostate: bool = False        # For anal pleasure (male bodies)
    
    # === ORIFICE COUNT ===
    # All bodies have mouth + ass = 2
    # Female adds pussy = 3
    # Cloaca replaces ass (still counts as 1)
    orifice_count: int = 2            # Calculated based on has_pussy
    
    # === BREAST CONFIG ===
    breast_count: int = 2
    breast_size_default: str = "average"
    can_lactate: bool = False
    
    # === PRESENTATION ===
    # How the body reads socially/visually
    presentation: str = "neutral"     # male, female, androgynous, neutral
    
    # === REPRODUCTION ===
    reproduction_role: str = "none"   # male, female, both, none
    can_impregnate: bool = False
    can_be_impregnated: bool = False
    
    def __post_init__(self):
        """Calculate orifice count."""
        self.orifice_count = 2  # mouth + ass always
        if self.has_pussy:
            self.orifice_count = 3


# =============================================================================
# GENITAL PART MAPPINGS
# Maps genital_category -> which part KEYS to use
# These map to the parts defined in parts_sexual.py
# =============================================================================

GENITAL_PARTS = {
    # Human-type genitals
    "human": {
        "cock": ["cock_human", "glans", "foreskin"],
        "balls": ["balls", "scrotum"],
        "pussy": ["pussy", "clit", "clit_hood", "labia"],
        "womb": ["cervix", "womb", "ovaries"],
        "prostate": ["prostate"],
    },
    
    # Canine-type (knot, sheath)
    "canine": {
        "cock": ["cock_canine", "knot", "sheath"],
        "balls": ["balls"],
        "pussy": ["pussy", "clit", "labia"],
        "womb": ["cervix", "womb", "ovaries"],
        "prostate": ["prostate"],
    },
    
    # Equine-type (large, flared)
    "equine": {
        "cock": ["cock_equine", "sheath"],
        "balls": ["balls"],
        "pussy": ["pussy", "clit", "labia"],
        "womb": ["cervix", "womb", "ovaries"],
        "prostate": ["prostate"],
    },
    
    # Feline-type (barbed)
    "feline": {
        "cock": ["cock_feline", "sheath"],
        "balls": ["balls"],
        "pussy": ["pussy", "clit", "labia"],
        "womb": ["cervix", "womb", "ovaries"],
        "prostate": ["prostate"],
    },
    
    # Reptile-type (hemipenes, cloaca)
    "reptile": {
        "cock": ["hemipenes"],         # Or cock_reptile for single
        "balls": [],                    # Internal, no visible balls
        "pussy": ["cloaca"],            # Cloaca serves as pussy
        "womb": ["womb", "ovaries"],
        "prostate": [],                 # Different anatomy
        "replaces_asshole": True,       # Cloaca replaces asshole
    },
    
    # Aquatic (dolphin-type, prehensile)
    "aquatic": {
        "cock": ["cock_dolphin"],
        "balls": ["balls"],             # Internal but present
        "pussy": ["pussy", "clit"],
        "womb": ["cervix", "womb", "ovaries"],
        "prostate": ["prostate"],
    },
    
    # Avian (cloaca for everything)
    "avian": {
        "cock": ["cloaca"],             # Cloacal kiss, no external penis
        "balls": [],                    # Internal
        "pussy": ["cloaca"],            # Same cloaca
        "womb": ["womb", "ovaries"],
        "prostate": [],
        "replaces_asshole": True,
    },
    
    # Insect (ovipositor)
    "insect": {
        "cock": ["ovipositor"],         # Ovipositor as penetrator
        "balls": [],                    # Different reproduction
        "pussy": ["cloaca"],            # Simplified
        "womb": ["womb", "ovaries"],
        "prostate": [],
    },
    
    # Tentacle
    "tentacle": {
        "cock": ["cock_tentacle"],
        "balls": ["balls"],             # Can have them
        "pussy": ["pussy", "clit"],
        "womb": ["womb"],
        "prostate": [],
    },
    
    # None - no genitals (slime, construct, etc.)
    "none": {
        "cock": [],
        "balls": [],
        "pussy": [],
        "womb": [],
        "prostate": [],
    },
}

# Breast parts (same for all species)
BREAST_PARTS = {
    2: ["breast_left", "breast_right", "nipple_left", "nipple_right"],
    4: ["breast_left", "breast_right", "breast_lower_left", "breast_lower_right",
        "nipple_left", "nipple_right", "nipple_lower_left", "nipple_lower_right"],
    6: ["breast_left", "breast_right", "breast_mid_left", "breast_mid_right",
        "breast_lower_left", "breast_lower_right",
        "nipple_left", "nipple_right", "nipple_mid_left", "nipple_mid_right",
        "nipple_lower_left", "nipple_lower_right"],
}


def get_genital_parts(genital_category: str, sex_config: "SexConfig") -> List[str]:
    """
    Get the genital parts to add based on category and sex config.
    
    Args:
        genital_category: From species (human, canine, equine, etc.)
        sex_config: The sex configuration
    
    Returns:
        List of part keys to add
    """
    parts = []
    mapping = GENITAL_PARTS.get(genital_category, GENITAL_PARTS["human"])
    
    if sex_config.has_cock:
        parts.extend(mapping.get("cock", []))
    
    if sex_config.has_balls:
        parts.extend(mapping.get("balls", []))
    
    if sex_config.has_pussy:
        parts.extend(mapping.get("pussy", []))
    
    if sex_config.has_womb:
        parts.extend(mapping.get("womb", []))
    
    if sex_config.has_prostate:
        parts.extend(mapping.get("prostate", []))
    
    if sex_config.has_breasts:
        breast_count = sex_config.breast_count
        if breast_count in BREAST_PARTS:
            parts.extend(BREAST_PARTS[breast_count])
        else:
            parts.extend(BREAST_PARTS[2])  # Default to 2
    
    return parts


def get_parts_to_remove(genital_category: str) -> List[str]:
    """Get parts that should be removed for this genital category."""
    mapping = GENITAL_PARTS.get(genital_category, {})
    if mapping.get("replaces_asshole"):
        return ["asshole"]
    return []


# =============================================================================
# SEX CONFIGURATIONS
# =============================================================================

MALE = SexConfig(
    key="male",
    name="Male",
    description="Standard male configuration. Cock, balls, no pussy.",
    has_cock=True,
    has_balls=True,
    has_pussy=False,
    has_womb=False,
    has_breasts=False,
    has_prostate=True,
    presentation="male",
    reproduction_role="male",
    can_impregnate=True,
    can_be_impregnated=False,
)

FEMALE = SexConfig(
    key="female",
    name="Female",
    description="Standard female configuration. Pussy, womb, breasts. Three orifices.",
    has_cock=False,
    has_balls=False,
    has_pussy=True,
    has_womb=True,
    has_breasts=True,
    has_prostate=False,
    can_lactate=True,
    presentation="female",
    reproduction_role="female",
    can_impregnate=False,
    can_be_impregnated=True,
)

HERM = SexConfig(
    key="herm",
    name="Hermaphrodite",
    description="Full hermaphrodite - both complete sets. Cock, balls, pussy, womb, breasts.",
    has_cock=True,
    has_balls=True,
    has_pussy=True,
    has_womb=True,
    has_breasts=True,
    has_prostate=True,
    can_lactate=True,
    presentation="androgynous",
    reproduction_role="both",
    can_impregnate=True,
    can_be_impregnated=True,
)

FUTA = SexConfig(
    key="futa",
    name="Futanari",
    description="Female body with cock, no balls. Three orifices plus a cock.",
    has_cock=True,
    has_balls=False,
    has_pussy=True,
    has_womb=True,
    has_breasts=True,
    has_prostate=False,
    can_lactate=True,
    presentation="female",
    reproduction_role="both",
    can_impregnate=True,
    can_be_impregnated=True,
)

MALEHERM = SexConfig(
    key="maleherm",
    name="Male-Herm",
    description="Male body with pussy added. Cock, balls, pussy, no breasts.",
    has_cock=True,
    has_balls=True,
    has_pussy=True,
    has_womb=True,
    has_breasts=False,
    has_prostate=True,
    presentation="male",
    reproduction_role="both",
    can_impregnate=True,
    can_be_impregnated=True,
)

CUNTBOY = SexConfig(
    key="cuntboy",
    name="Cuntboy",
    description="Male presentation with pussy instead of cock. Flat chest.",
    has_cock=False,
    has_balls=False,
    has_pussy=True,
    has_womb=True,
    has_breasts=False,
    has_prostate=False,
    presentation="male",
    reproduction_role="female",
    can_impregnate=False,
    can_be_impregnated=True,
)

FEMBOY = SexConfig(
    key="femboy",
    name="Femboy",
    description="Male genitals with feminine presentation. Cock and balls, flat chest.",
    has_cock=True,
    has_balls=True,
    has_pussy=False,
    has_womb=False,
    has_breasts=False,
    has_prostate=True,
    presentation="female",  # Presents feminine
    reproduction_role="male",
    can_impregnate=True,
    can_be_impregnated=False,
)

DICKGIRL = SexConfig(
    key="dickgirl",
    name="Dickgirl",
    description="Female body with cock and balls, no pussy.",
    has_cock=True,
    has_balls=True,
    has_pussy=False,
    has_womb=False,
    has_breasts=True,
    has_prostate=True,
    can_lactate=True,
    presentation="female",
    reproduction_role="male",
    can_impregnate=True,
    can_be_impregnated=False,
)

NEUTER = SexConfig(
    key="neuter",
    name="Neuter",
    description="No sexual organs. Just mouth and ass.",
    has_cock=False,
    has_balls=False,
    has_pussy=False,
    has_womb=False,
    has_breasts=False,
    has_prostate=False,
    presentation="neutral",
    reproduction_role="none",
    can_impregnate=False,
    can_be_impregnated=False,
)

NEUTER_SMOOTH = SexConfig(
    key="neuter_smooth",
    name="Neuter (Smooth)",
    description="Completely smooth genital area. Ken doll.",
    has_cock=False,
    has_balls=False,
    has_pussy=False,
    has_womb=False,
    has_breasts=False,
    has_prostate=False,
    presentation="neutral",
    reproduction_role="none",
    can_impregnate=False,
    can_be_impregnated=False,
)

DOLL = SexConfig(
    key="doll",
    name="Doll",
    description="No genitals, decorative breasts. Aesthetic only.",
    has_cock=False,
    has_balls=False,
    has_pussy=False,
    has_womb=False,
    has_breasts=True,
    has_prostate=False,
    can_lactate=False,
    presentation="female",
    reproduction_role="none",
    can_impregnate=False,
    can_be_impregnated=False,
)

# Multi-breast variants
FEMALE_MULTI = SexConfig(
    key="female_multi",
    name="Female (Multi-Breast)",
    description="Female with multiple rows of breasts. Like a mother dog.",
    has_cock=False,
    has_balls=False,
    has_pussy=True,
    has_womb=True,
    has_breasts=True,
    has_prostate=False,
    breast_count=6,
    can_lactate=True,
    presentation="female",
    reproduction_role="female",
    can_impregnate=False,
    can_be_impregnated=True,
)

HERM_MULTI = SexConfig(
    key="herm_multi",
    name="Herm (Multi-Breast)",
    description="Hermaphrodite with multiple rows of breasts.",
    has_cock=True,
    has_balls=True,
    has_pussy=True,
    has_womb=True,
    has_breasts=True,
    has_prostate=True,
    breast_count=6,
    can_lactate=True,
    presentation="androgynous",
    reproduction_role="both",
    can_impregnate=True,
    can_be_impregnated=True,
)


# =============================================================================
# SEX CONFIG REGISTRY
# =============================================================================

SEX_REGISTRY: Dict[str, SexConfig] = {
    "male": MALE,
    "female": FEMALE,
    "herm": HERM,
    "futa": FUTA,
    "maleherm": MALEHERM,
    "cuntboy": CUNTBOY,
    "femboy": FEMBOY,
    "dickgirl": DICKGIRL,
    "neuter": NEUTER,
    "neuter_smooth": NEUTER_SMOOTH,
    "doll": DOLL,
    "female_multi": FEMALE_MULTI,
    "herm_multi": HERM_MULTI,
}


def get_sex_config(key: str) -> Optional[SexConfig]:
    """Get a sex configuration by key."""
    return SEX_REGISTRY.get(key)


def list_sex_configs() -> List[str]:
    """List all sex configuration keys."""
    return list(SEX_REGISTRY.keys())


def get_configs_by_presentation(presentation: str) -> List[SexConfig]:
    """Get all configs with a specific presentation."""
    return [c for c in SEX_REGISTRY.values() if c.presentation == presentation]


def get_configs_by_role(role: str) -> List[SexConfig]:
    """Get all configs with a specific reproduction role."""
    return [c for c in SEX_REGISTRY.values() if c.reproduction_role == role]


# =============================================================================
# BACKWARD COMPATIBILITY / LEGACY SUPPORT
# =============================================================================

# For backward compatibility with old "male_canine" style keys
# Maps to (sex_config_key, genital_category_override)
LEGACY_ANATOMY_MAP = {
    "male_human": ("male", "human"),
    "male_canine": ("male", "canine"),
    "male_equine": ("male", "equine"),
    "male_feline": ("male", "feline"),
    "male_reptile": ("male", "reptile"),
    "male_dolphin": ("male", "aquatic"),
    "male_tentacle": ("male", "tentacle"),
    
    "female_human": ("female", "human"),
    "female_canine": ("female", "canine"),
    "female_equine": ("female", "equine"),
    "female_feline": ("female", "feline"),
    "female_reptile": ("female", "reptile"),
    "female_multi_breast": ("female_multi", None),
    
    "herm_human": ("herm", "human"),
    "herm_canine": ("herm", "canine"),
    "herm_equine": ("herm", "equine"),
    "futa_human": ("futa", "human"),
    "futa_canine": ("futa", "canine"),
    
    "femboy_human": ("femboy", "human"),
    "femboy_canine": ("femboy", "canine"),
    "cuntboy_human": ("cuntboy", "human"),
    "cuntboy_canine": ("cuntboy", "canine"),
    
    "neuter": ("neuter", None),
    "neuter_smooth": ("neuter_smooth", None),
    "doll": ("doll", None),
    "xenomorph": ("neuter", "insect"),
    "slime": ("neuter", "none"),
}


def resolve_legacy_anatomy(anatomy_key: str) -> tuple:
    """
    Convert old anatomy key to new (sex_config, genital_override) tuple.
    
    Returns:
        (sex_config_key, genital_category_override_or_None)
    """
    if anatomy_key in LEGACY_ANATOMY_MAP:
        return LEGACY_ANATOMY_MAP[anatomy_key]
    
    # Try to parse as "sex_species" pattern
    if "_" in anatomy_key:
        parts = anatomy_key.split("_", 1)
        sex = parts[0]
        if sex in SEX_REGISTRY:
            return (sex, parts[1] if len(parts) > 1 else None)
    
    # Default: treat as sex config key
    if anatomy_key in SEX_REGISTRY:
        return (anatomy_key, None)
    
    # Unknown - default to male human
    return ("male", "human")
