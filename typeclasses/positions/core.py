"""
Core enums and mappings for the position system.
"""

from enum import Enum, auto
from typing import Set, Dict


class BodyZone(Enum):
    """
    Spatial zones of the body for access mapping.
    
    Positions define access in terms of zones, which then
    map to specific body parts for mechanical resolution.
    """
    # Head/Face
    FACE = "face"
    MOUTH = "mouth"
    NECK = "neck"
    EARS = "ears"
    HAIR = "hair"
    
    # Upper body
    SHOULDERS = "shoulders"
    CHEST = "chest"
    BREASTS = "breasts"  # Specifically the breasts if present
    BACK_UPPER = "back_upper"
    ARMS = "arms"
    HANDS = "hands"
    
    # Core
    BELLY = "belly"
    SIDES = "sides"
    BACK_LOWER = "back_lower"
    
    # Lower body
    HIPS = "hips"
    GROIN = "groin"  # Front genital area
    ASS = "ass"      # Rear, includes the orifice
    THIGHS = "thighs"
    LEGS = "legs"
    FEET = "feet"
    TAIL = "tail"    # If present
    
    # Special
    WHOLE_BODY = "whole_body"  # For full-body access (hugging, etc.)


class Posture(Enum):
    """
    Physical posture of a participant in a position.
    
    Affects what zones are naturally accessible and
    what movements are possible.
    """
    # Upright
    STANDING = "standing"
    KNEELING = "kneeling"
    SITTING = "sitting"
    SQUATTING = "squatting"
    
    # Bent
    BENT_FORWARD = "bent_forward"      # Standing, bent at waist
    BENT_OVER = "bent_over"            # Over furniture/person
    HANDS_AND_KNEES = "hands_and_knees"  # On all fours
    
    # Lying
    LYING_BACK = "lying_back"          # On back, face up
    LYING_FRONT = "lying_front"        # On stomach, face down
    LYING_SIDE = "lying_side"          # On side
    
    # Supported
    LEANING = "leaning"                # Against wall/furniture
    MOUNTED = "mounted"                # On top of someone
    STRADDLING = "straddling"          # Legs around someone/something
    
    # Suspended
    SUSPENDED = "suspended"            # Hanging
    INVERTED = "inverted"              # Upside down
    SPREAD = "spread"                  # Spread-eagle (standing or lying)
    
    # Special
    CARRIED = "carried"                # Being held/carried
    PINNED = "pinned_down"             # Pressed against surface
    HELD = "held"                      # Being held in place by another


class Mobility(Enum):
    """
    How much the participant can move in their slot.
    """
    FREE = "free"              # Full movement control
    ACTIVE = "active"          # Moving but engaged (fucking, riding)
    LIMITED = "limited"        # Can move but restricted
    PASSIVE = "passive"        # Receiving, minimal movement
    HELD = "held"              # Being held in place by another
    RESTRAINED = "restrained"  # Bound by restraints
    IMMOBILE = "immobile"      # Cannot move at all


class FurnitureType(Enum):
    """
    Types of furniture/objects that enable positions.
    
    Objects and furniture in-game should have a `position_tags` 
    attribute containing relevant FurnitureType values.
    """
    # Surfaces
    FLOOR = "floor"            # Any floor (always available)
    BED = "bed"                # Soft horizontal surface
    TABLE = "table"            # Hard horizontal surface, waist height
    DESK = "desk"              # Similar to table
    COUCH = "couch"            # Soft seating, can lie on
    CHAIR = "chair"            # Seating
    BENCH = "bench"            # Long seating, can lie on
    THRONE = "throne"          # Large ornate chair
    
    # Vertical
    WALL = "wall"              # Vertical surface (always available)
    DOOR = "door"              # Vertical surface that opens
    PILLAR = "pillar"          # Vertical post
    TREE = "tree"              # Outdoor vertical
    
    # Special furniture
    STOCKS = "stocks"          # Restraint furniture
    PILLORY = "pillory"        # Head and hands locked
    CROSS = "cross"            # X-frame
    SYBIAN = "sybian"          # Mounted toy
    CAGE = "cage"              # Enclosure
    BREEDING_BENCH = "breeding_bench"  # Purpose-built
    
    # Suspension
    SUSPENSION_POINT = "suspension"  # Ceiling hook, beam
    SWING = "swing"            # Sex swing
    SLING = "sling"            # Leather sling
    
    # Water
    BATH = "bath"              # Bathtub
    POOL = "pool"              # Pool/hot tub
    SHOWER = "shower"          # Standing water
    
    # Outdoor
    GROUND = "ground"          # Natural ground
    GRASS = "grass"            # Soft natural surface
    HAY = "hay"                # Barn setting
    
    # Misc
    STAIRS = "stairs"          # Steps
    WINDOWSILL = "windowsill"  # For exhibitionism
    MIRROR = "mirror"          # For visual positions


# ============================================================================
# Zone to Part Mappings
# ============================================================================

# Maps body zones to the part keys that exist in that zone.
# Used to resolve what specific parts can be accessed when
# a position grants access to a zone.
ZONE_TO_PARTS: Dict[BodyZone, Set[str]] = {
    BodyZone.FACE: {"head", "face", "eyes", "nose"},
    BodyZone.MOUTH: {"mouth", "tongue", "lips", "throat"},
    BodyZone.NECK: {"neck"},
    BodyZone.EARS: {"ears", "ear_left", "ear_right"},
    BodyZone.HAIR: {"hair", "mane"},
    
    BodyZone.SHOULDERS: {"shoulders", "shoulder_left", "shoulder_right"},
    BodyZone.CHEST: {"chest", "torso_upper"},
    BodyZone.BREASTS: {"breasts", "breast_left", "breast_right", "nipples"},
    BodyZone.BACK_UPPER: {"back", "back_upper", "spine_upper"},
    BodyZone.ARMS: {"arms", "arm_left", "arm_right", "forearms"},
    BodyZone.HANDS: {"hands", "hand_left", "hand_right", "fingers"},
    
    BodyZone.BELLY: {"belly", "stomach", "abdomen", "torso_lower"},
    BodyZone.SIDES: {"sides", "flanks", "ribs"},
    BodyZone.BACK_LOWER: {"back_lower", "spine_lower", "small_of_back"},
    
    BodyZone.HIPS: {"hips", "hip_left", "hip_right", "pelvis"},
    BodyZone.GROIN: {"groin", "pussy", "cock", "balls", "clit", "sheath", "genital_slit"},
    BodyZone.ASS: {"ass", "buttocks", "anus", "tailhole", "cheeks"},
    BodyZone.THIGHS: {"thighs", "thigh_left", "thigh_right", "inner_thighs"},
    BodyZone.LEGS: {"legs", "leg_left", "leg_right", "calves", "knees"},
    BodyZone.FEET: {"feet", "foot_left", "foot_right", "toes", "paws_rear"},
    BodyZone.TAIL: {"tail", "tail_base"},
    
    BodyZone.WHOLE_BODY: set(),  # Special case - means all zones
}


def _build_part_to_zone() -> Dict[str, BodyZone]:
    """Build reverse mapping of part -> zone."""
    result = {}
    for zone, parts in ZONE_TO_PARTS.items():
        for part in parts:
            result[part] = zone
    return result


PART_TO_ZONE: Dict[str, BodyZone] = _build_part_to_zone()


# ============================================================================
# Posture Natural Access
# ============================================================================

# What zones are naturally MORE accessible based on posture
POSTURE_ENHANCED_ACCESS: Dict[Posture, Set[BodyZone]] = {
    Posture.STANDING: {BodyZone.FACE, BodyZone.CHEST, BodyZone.GROIN},
    Posture.KNEELING: {BodyZone.FACE, BodyZone.GROIN},  # Face at groin height
    Posture.SITTING: {BodyZone.FACE, BodyZone.CHEST, BodyZone.GROIN},
    Posture.BENT_FORWARD: {BodyZone.ASS, BodyZone.BACK_LOWER, BodyZone.GROIN},
    Posture.BENT_OVER: {BodyZone.ASS, BodyZone.BACK_LOWER, BodyZone.MOUTH},
    Posture.HANDS_AND_KNEES: {BodyZone.ASS, BodyZone.GROIN, BodyZone.MOUTH, BodyZone.BREASTS},
    Posture.LYING_BACK: {BodyZone.FACE, BodyZone.CHEST, BodyZone.BREASTS, BodyZone.BELLY, BodyZone.GROIN},
    Posture.LYING_FRONT: {BodyZone.ASS, BodyZone.BACK_UPPER, BodyZone.BACK_LOWER},
    Posture.LYING_SIDE: {BodyZone.FACE, BodyZone.SIDES, BodyZone.HIPS},
    Posture.STRADDLING: {BodyZone.GROIN, BodyZone.ASS, BodyZone.FACE},
    Posture.MOUNTED: {BodyZone.BACK_UPPER, BodyZone.HIPS, BodyZone.ASS},
    Posture.SUSPENDED: {BodyZone.WHOLE_BODY},  # Everything exposed
    Posture.INVERTED: {BodyZone.GROIN, BodyZone.LEGS, BodyZone.FEET},
    Posture.SPREAD: {BodyZone.GROIN, BodyZone.ASS, BodyZone.THIGHS},
    Posture.PINNED: {BodyZone.FACE, BodyZone.NECK, BodyZone.CHEST},
    Posture.HELD: {BodyZone.WHOLE_BODY},  # Being held - all zones potentially accessible
}

# What zones are naturally BLOCKED based on posture
POSTURE_BLOCKED_ACCESS: Dict[Posture, Set[BodyZone]] = {
    Posture.LYING_BACK: {BodyZone.BACK_UPPER, BodyZone.BACK_LOWER, BodyZone.ASS},
    Posture.LYING_FRONT: {BodyZone.CHEST, BodyZone.BREASTS, BodyZone.BELLY, BodyZone.GROIN},
    Posture.SITTING: {BodyZone.ASS, BodyZone.BACK_LOWER},
    Posture.LEANING: {BodyZone.BACK_UPPER, BodyZone.BACK_LOWER},
    Posture.PINNED: {BodyZone.BACK_UPPER, BodyZone.BACK_LOWER},
}


# ============================================================================
# Utility Functions
# ============================================================================

def zones_for_part(part_key: str) -> BodyZone:
    """Get the body zone a part belongs to."""
    return PART_TO_ZONE.get(part_key, BodyZone.WHOLE_BODY)


def parts_in_zone(zone: BodyZone) -> Set[str]:
    """Get all part keys in a body zone."""
    if zone == BodyZone.WHOLE_BODY:
        # Return all parts
        all_parts = set()
        for parts in ZONE_TO_PARTS.values():
            all_parts.update(parts)
        return all_parts
    return ZONE_TO_PARTS.get(zone, set())


def get_posture_access_modifiers(posture: Posture) -> tuple:
    """
    Get the enhanced and blocked zones for a posture.
    
    Returns:
        (enhanced_zones, blocked_zones)
    """
    enhanced = POSTURE_ENHANCED_ACCESS.get(posture, set())
    blocked = POSTURE_BLOCKED_ACCESS.get(posture, set())
    return enhanced, blocked
