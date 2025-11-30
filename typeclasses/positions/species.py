"""
Species Compatibility for Positions
====================================

Handles how different body structures interact with positions:
- Bipedal (humans, most anthros)
- Digitigrade bipedal (some anthros)
- Quadruped (feral animals)
- Taur (centaur, etc. - humanoid upper, quadruped lower)
- Serpentine (nagas, lamias - humanoid upper, snake lower)
- Avian (wings affect arm positions)
- Aquatic (merfolk - humanoid upper, fish lower)
- Multi-limbed (extra arms)

Each body structure modifies:
- Which positions are available
- How zones map between participants
- Height/size compatibility
- What's naturally accessible
"""

from dataclasses import dataclass, field
from typing import Dict, Set, Optional, List, Tuple, Any
from enum import Enum, auto

from .core import BodyZone, Posture, Mobility, ZONE_TO_PARTS


class BodyStructureType(Enum):
    """
    Core body structure types that affect positioning.
    """
    BIPEDAL = "bipedal"              # Standard two-legged upright
    DIGITIGRADE = "digitigrade"      # Bipedal but with bent legs (anthro wolves, etc.)
    QUADRUPED = "quadruped"          # Four-legged, horizontal body
    TAUR = "taur"                    # Humanoid upper body, quadruped lower
    SERPENTINE = "serpentine"        # Humanoid upper, snake/tail lower (no legs)
    AVIAN = "avian"                  # Bipedal with wings instead of/in addition to arms
    AQUATIC = "aquatic"              # Humanoid upper, fish tail lower
    MULTI_LIMBED = "multi_limbed"    # Extra arms (spider taur, etc.)
    AMORPHOUS = "amorphous"          # Slimes, shapeshifters


class SizeCategory(Enum):
    """
    Size categories for compatibility.
    """
    TINY = 1        # Pixie, small fey
    SMALL = 2       # Goblin, halfling
    MEDIUM = 3      # Human, most anthros
    LARGE = 4       # Centaur, large anthros
    HUGE = 5        # Giants, dragons
    MASSIVE = 6     # Kaiju-scale


@dataclass
class StructureTraits:
    """
    Traits for a specific body structure type.
    """
    structure_type: BodyStructureType
    
    # What zones exist on this body type
    zones_present: Set[BodyZone] = field(default_factory=set)
    
    # Zones that don't exist on this body type
    zones_absent: Set[BodyZone] = field(default_factory=set)
    
    # Additional zones unique to this body type
    zones_special: Set[str] = field(default_factory=set)
    
    # Natural postures this structure can achieve
    natural_postures: Set[Posture] = field(default_factory=set)
    
    # Postures this structure CANNOT do
    impossible_postures: Set[Posture] = field(default_factory=set)
    
    # Does this structure have usable hands?
    has_hands: bool = True
    
    # Does this structure have separate legs?
    has_legs: bool = True
    
    # Can this structure lie flat on back?
    can_lie_back: bool = True
    
    # Can this structure kneel?
    can_kneel: bool = True
    
    # Height modifier (affects position compatibility)
    height_modifier: float = 1.0
    
    # Position key overrides - maps standard position to variant
    # e.g., {"missionary": "quadruped_mounting"}
    position_variants: Dict[str, str] = field(default_factory=dict)
    
    # Tags for positions that work well with this structure
    compatible_tags: Set[str] = field(default_factory=set)
    
    # Tags for positions that don't work with this structure
    incompatible_tags: Set[str] = field(default_factory=set)


# ============================================================================
# Structure Definitions
# ============================================================================

STRUCTURE_TRAITS: Dict[BodyStructureType, StructureTraits] = {
    
    BodyStructureType.BIPEDAL: StructureTraits(
        structure_type=BodyStructureType.BIPEDAL,
        zones_present=set(BodyZone),  # All standard zones
        zones_absent=set(),
        natural_postures={
            Posture.STANDING, Posture.KNEELING, Posture.SITTING,
            Posture.LYING_BACK, Posture.LYING_FRONT, Posture.LYING_SIDE,
            Posture.BENT_FORWARD, Posture.BENT_OVER, Posture.HANDS_AND_KNEES,
            Posture.SQUATTING, Posture.LEANING, Posture.STRADDLING,
            Posture.SUSPENDED, Posture.SPREAD, Posture.PINNED, Posture.CARRIED,
            Posture.HELD,
        },
        impossible_postures=set(),
        has_hands=True,
        has_legs=True,
        can_lie_back=True,
        can_kneel=True,
        height_modifier=1.0,
        compatible_tags=set(),  # Works with everything
        incompatible_tags=set(),
    ),
    
    BodyStructureType.DIGITIGRADE: StructureTraits(
        structure_type=BodyStructureType.DIGITIGRADE,
        zones_present=set(BodyZone),
        zones_absent=set(),
        zones_special={"paws", "dewclaws"},
        natural_postures={
            Posture.STANDING, Posture.KNEELING, Posture.SITTING,
            Posture.LYING_BACK, Posture.LYING_FRONT, Posture.LYING_SIDE,
            Posture.BENT_FORWARD, Posture.BENT_OVER, Posture.HANDS_AND_KNEES,
            Posture.SQUATTING, Posture.LEANING, Posture.STRADDLING,
            Posture.SUSPENDED, Posture.SPREAD, Posture.PINNED, Posture.CARRIED,
        },
        impossible_postures=set(),
        has_hands=True,
        has_legs=True,
        can_lie_back=True,
        can_kneel=True,  # Can kneel, just differently
        height_modifier=1.0,
        compatible_tags={"primal"},  # Works well with primal positions
    ),
    
    BodyStructureType.QUADRUPED: StructureTraits(
        structure_type=BodyStructureType.QUADRUPED,
        zones_present={
            BodyZone.FACE, BodyZone.MOUTH, BodyZone.NECK, BodyZone.EARS,
            BodyZone.SHOULDERS, BodyZone.BACK_UPPER, BodyZone.BACK_LOWER,
            BodyZone.SIDES, BodyZone.BELLY, BodyZone.HIPS,
            BodyZone.GROIN, BodyZone.ASS, BodyZone.TAIL,
            BodyZone.LEGS, BodyZone.FEET, BodyZone.THIGHS,
        },
        zones_absent={
            BodyZone.CHEST, BodyZone.BREASTS,  # No upright chest
            BodyZone.ARMS, BodyZone.HANDS,     # Front legs, not arms
        },
        zones_special={"withers", "flank", "rump", "sheath_area"},
        natural_postures={
            Posture.STANDING,  # On all fours is their "standing"
            Posture.LYING_FRONT, Posture.LYING_SIDE,
            Posture.MOUNTED,  # Being mounted
        },
        impossible_postures={
            Posture.SITTING, Posture.KNEELING, Posture.SQUATTING,
            Posture.LYING_BACK,  # Can't really lie on back comfortably
            Posture.STRADDLING, Posture.HANDS_AND_KNEES,  # Already on all fours
            Posture.BENT_FORWARD, Posture.BENT_OVER,  # Horizontal already
            Posture.CARRIED,  # Too awkward
        },
        has_hands=False,
        has_legs=True,  # Four of them
        can_lie_back=False,
        can_kneel=False,
        height_modifier=0.6,  # Shorter than bipedal
        position_variants={
            "missionary": "mounted",
            "doggy": "mounted",
            "cowgirl": "reverse_mounted",
        },
        compatible_tags={"mounting", "feral", "primal"},
        incompatible_tags={"face_to_face", "sitting", "kneeling"},
    ),
    
    BodyStructureType.TAUR: StructureTraits(
        structure_type=BodyStructureType.TAUR,
        zones_present=set(BodyZone) | {BodyZone.TAIL},
        zones_absent=set(),
        zones_special={"withers", "flank", "rump", "barrel", "dock"},
        natural_postures={
            Posture.STANDING,
            Posture.LYING_FRONT, Posture.LYING_SIDE,
            Posture.BENT_FORWARD,
            Posture.MOUNTED,  # Someone on their back
        },
        impossible_postures={
            Posture.SITTING,  # Can't sit normally
            Posture.KNEELING,  # Too many legs
            Posture.LYING_BACK,  # Horse body in the way
            Posture.HANDS_AND_KNEES,  # Already has four legs down
            Posture.SQUATTING,
            Posture.STRADDLING,  # Too big
            Posture.CARRIED,
        },
        has_hands=True,  # Humanoid upper body
        has_legs=True,  # Four of them
        can_lie_back=False,
        can_kneel=False,
        height_modifier=1.4,  # Taller due to horse body
        position_variants={
            "missionary": "taur_mounting",
            "cowgirl": "taur_reverse",
            "doggy": "taur_rear",
        },
        compatible_tags={"mounting", "standing"},
        incompatible_tags={"lying_back", "sitting", "face_to_face"},
    ),
    
    BodyStructureType.SERPENTINE: StructureTraits(
        structure_type=BodyStructureType.SERPENTINE,
        zones_present={
            BodyZone.FACE, BodyZone.MOUTH, BodyZone.NECK, BodyZone.EARS,
            BodyZone.SHOULDERS, BodyZone.CHEST, BodyZone.BREASTS,
            BodyZone.ARMS, BodyZone.HANDS,
            BodyZone.BACK_UPPER, BodyZone.BACK_LOWER,
            BodyZone.BELLY, BodyZone.SIDES,
            BodyZone.GROIN, BodyZone.TAIL,
            BodyZone.HIPS,  # Where humanoid meets snake
        },
        zones_absent={
            BodyZone.LEGS, BodyZone.FEET, BodyZone.THIGHS,  # Snake tail instead
            BodyZone.ASS,  # Different anatomy - cloaca/vent instead
        },
        zones_special={"coils", "vent", "tail_tip", "scales"},
        natural_postures={
            Posture.LYING_FRONT, Posture.LYING_SIDE,
            Posture.BENT_FORWARD,  # Upper body can lean
            Posture.SUSPENDED,  # Can be hung
            # Coiling around things is unique
        },
        impossible_postures={
            Posture.STANDING,  # No legs - can rear up but not stand
            Posture.KNEELING,
            Posture.SITTING,  # Can coil into sitting position though
            Posture.LYING_BACK,  # Tail makes this awkward
            Posture.HANDS_AND_KNEES,  # No knees
            Posture.SQUATTING,
            Posture.STRADDLING,  # No legs to straddle with
        },
        has_hands=True,
        has_legs=False,
        can_lie_back=False,  # Sort of, with coils
        can_kneel=False,
        height_modifier=1.2,  # When reared up
        position_variants={
            "missionary": "coiled_embrace",
            "cowgirl": "coiled_riding",
            "doggy": "serpent_rear",
        },
        compatible_tags={"coiling", "constriction", "ground"},
        incompatible_tags={"standing", "kneeling", "sitting"},
    ),
    
    BodyStructureType.AVIAN: StructureTraits(
        structure_type=BodyStructureType.AVIAN,
        zones_present=set(BodyZone),
        zones_absent=set(),
        zones_special={"wings", "wing_joints", "feathers", "cloaca"},
        natural_postures={
            Posture.STANDING, Posture.KNEELING, Posture.SITTING,
            Posture.LYING_FRONT, Posture.LYING_SIDE,
            Posture.BENT_FORWARD, Posture.SQUATTING,
        },
        impossible_postures={
            Posture.LYING_BACK,  # Wings in the way
            Posture.PINNED,  # Would damage wings
        },
        has_hands=True,  # Assuming anthro with wings AND hands
        has_legs=True,
        can_lie_back=False,  # Wings
        can_kneel=True,
        height_modifier=1.0,
        compatible_tags=set(),
        incompatible_tags={"lying_back", "pinned"},
    ),
    
    BodyStructureType.AQUATIC: StructureTraits(
        structure_type=BodyStructureType.AQUATIC,
        zones_present={
            BodyZone.FACE, BodyZone.MOUTH, BodyZone.NECK, BodyZone.EARS,
            BodyZone.SHOULDERS, BodyZone.CHEST, BodyZone.BREASTS,
            BodyZone.ARMS, BodyZone.HANDS,
            BodyZone.BACK_UPPER, BodyZone.BACK_LOWER,
            BodyZone.BELLY, BodyZone.SIDES,
            BodyZone.GROIN, BodyZone.HIPS,
            BodyZone.TAIL,  # Fish tail
        },
        zones_absent={
            BodyZone.LEGS, BodyZone.FEET, BodyZone.THIGHS,
            BodyZone.ASS,  # Different anatomy
        },
        zones_special={"fins", "tail_fin", "scales", "gills"},
        natural_postures={
            Posture.LYING_FRONT, Posture.LYING_SIDE, Posture.LYING_BACK,
            Posture.SUSPENDED,  # In water
        },
        impossible_postures={
            Posture.STANDING, Posture.KNEELING, Posture.SITTING,
            Posture.SQUATTING, Posture.HANDS_AND_KNEES, Posture.STRADDLING,
        },
        has_hands=True,
        has_legs=False,
        can_lie_back=True,
        can_kneel=False,
        height_modifier=1.0,
        compatible_tags={"water", "lying"},
        incompatible_tags={"standing", "kneeling", "sitting"},
    ),
    
    BodyStructureType.MULTI_LIMBED: StructureTraits(
        structure_type=BodyStructureType.MULTI_LIMBED,
        zones_present=set(BodyZone),
        zones_absent=set(),
        zones_special={"extra_arms", "additional_hands"},
        natural_postures=set(Posture),  # Can do most things
        impossible_postures=set(),
        has_hands=True,  # Multiple!
        has_legs=True,
        can_lie_back=True,
        can_kneel=True,
        height_modifier=1.0,
        compatible_tags={"multi_partner"},  # Extra hands useful for groups
    ),
    
    BodyStructureType.AMORPHOUS: StructureTraits(
        structure_type=BodyStructureType.AMORPHOUS,
        zones_present=set(BodyZone),  # Can form any zone
        zones_absent=set(),
        zones_special={"pseudopod", "core", "membrane"},
        natural_postures=set(Posture),  # Can assume any shape
        impossible_postures=set(),
        has_hands=True,  # Can form them
        has_legs=True,  # Can form them
        can_lie_back=True,
        can_kneel=True,
        height_modifier=1.0,  # Variable
        compatible_tags=set(),  # Works with everything
    ),
}


# ============================================================================
# Compatibility Checking
# ============================================================================

@dataclass
class CompatibilityResult:
    """Result of checking position compatibility."""
    compatible: bool
    reason: str = ""
    warnings: List[str] = field(default_factory=list)
    suggested_variant: Optional[str] = None
    zone_adjustments: Dict[BodyZone, BodyZone] = field(default_factory=dict)


def get_structure_traits(structure_type: BodyStructureType) -> StructureTraits:
    """Get traits for a body structure type."""
    return STRUCTURE_TRAITS.get(structure_type, STRUCTURE_TRAITS[BodyStructureType.BIPEDAL])


def check_posture_compatibility(
    structure: BodyStructureType,
    required_posture: Posture
) -> Tuple[bool, str]:
    """
    Check if a body structure can achieve a posture.
    
    Returns:
        (can_do, reason)
    """
    traits = get_structure_traits(structure)
    
    if required_posture in traits.impossible_postures:
        return False, f"{structure.value} cannot achieve {required_posture.value} posture"
    
    if required_posture in traits.natural_postures:
        return True, ""
    
    # Not natural but not impossible - possible with effort
    return True, f"{structure.value} can awkwardly achieve {required_posture.value}"


def check_position_compatibility(
    position_key: str,
    structure_a: BodyStructureType,
    structure_b: BodyStructureType,
    size_a: SizeCategory = SizeCategory.MEDIUM,
    size_b: SizeCategory = SizeCategory.MEDIUM,
) -> CompatibilityResult:
    """
    Check if two body structures are compatible for a position.
    
    Args:
        position_key: The position to check
        structure_a: First participant's body structure
        structure_b: Second participant's body structure
        size_a: First participant's size
        size_b: Second participant's size
        
    Returns:
        CompatibilityResult with details
    """
    from .library import get_position
    
    position = get_position(position_key)
    if not position:
        return CompatibilityResult(
            compatible=False,
            reason=f"Unknown position: {position_key}"
        )
    
    traits_a = get_structure_traits(structure_a)
    traits_b = get_structure_traits(structure_b)
    
    warnings = []
    
    # Check for incompatible tags
    for tag in position.tags:
        if tag in traits_a.incompatible_tags:
            return CompatibilityResult(
                compatible=False,
                reason=f"{structure_a.value} is incompatible with {tag} positions",
                suggested_variant=traits_a.position_variants.get(position_key)
            )
        if tag in traits_b.incompatible_tags:
            return CompatibilityResult(
                compatible=False,
                reason=f"{structure_b.value} is incompatible with {tag} positions",
                suggested_variant=traits_b.position_variants.get(position_key)
            )
    
    # Check posture requirements for each slot
    slots = list(position.slots.values())
    if len(slots) >= 2:
        slot_a, slot_b = slots[0], slots[1]
        
        can_a, reason_a = check_posture_compatibility(structure_a, slot_a.posture)
        if not can_a:
            variant = traits_a.position_variants.get(position_key)
            return CompatibilityResult(
                compatible=False,
                reason=reason_a,
                suggested_variant=variant
            )
        elif reason_a:
            warnings.append(reason_a)
        
        can_b, reason_b = check_posture_compatibility(structure_b, slot_b.posture)
        if not can_b:
            variant = traits_b.position_variants.get(position_key)
            return CompatibilityResult(
                compatible=False,
                reason=reason_b,
                suggested_variant=variant
            )
        elif reason_b:
            warnings.append(reason_b)
    
    # Check size compatibility
    size_diff = abs(size_a.value - size_b.value)
    max_diff = position.requirements.max_size_difference
    
    if size_diff > max_diff:
        return CompatibilityResult(
            compatible=False,
            reason=f"Size difference too large ({size_a.name} vs {size_b.name})"
        )
    elif size_diff > max_diff - 1:
        warnings.append(f"Significant size difference may make this awkward")
    
    # Check zone availability
    zone_adjustments = {}
    
    # If one participant is missing zones the position needs, flag it
    for slot in position.slots.values():
        for target_slot, zones in slot.can_access.items():
            for zone in zones:
                # Check if the target has this zone
                if structure_b == structure_a:
                    target_traits = traits_a
                else:
                    target_traits = traits_b
                
                if zone in target_traits.zones_absent:
                    warnings.append(f"{zone.value} not present on {target_traits.structure_type.value}")
    
    # Check specific structure combinations
    if structure_a == BodyStructureType.QUADRUPED or structure_b == BodyStructureType.QUADRUPED:
        if "face_to_face" in position.tags:
            return CompatibilityResult(
                compatible=False,
                reason="Quadrupeds cannot do face-to-face positions with bipeds",
                suggested_variant="mounted" if "penetrative" in position.tags else None
            )
    
    if structure_a == BodyStructureType.TAUR or structure_b == BodyStructureType.TAUR:
        if "lying_back" in position.tags or position_key in ["missionary", "cowgirl"]:
            return CompatibilityResult(
                compatible=False,
                reason="Taurs cannot lie on their backs",
                suggested_variant=traits_a.position_variants.get(position_key) or 
                                 traits_b.position_variants.get(position_key)
            )
    
    if structure_a == BodyStructureType.SERPENTINE or structure_b == BodyStructureType.SERPENTINE:
        if "standing" in position.tags or "kneeling" in position.tags:
            return CompatibilityResult(
                compatible=False,
                reason="Serpentine bodies cannot stand or kneel",
                suggested_variant="coiled_embrace"
            )
    
    return CompatibilityResult(
        compatible=True,
        warnings=warnings,
        zone_adjustments=zone_adjustments
    )


def get_compatible_positions(
    structure_a: BodyStructureType,
    structure_b: BodyStructureType,
    size_a: SizeCategory = SizeCategory.MEDIUM,
    size_b: SizeCategory = SizeCategory.MEDIUM,
) -> List[str]:
    """
    Get all positions compatible with two body structures.
    
    Returns:
        List of position keys that work
    """
    from .library import POSITIONS
    
    compatible = []
    
    for key in POSITIONS:
        result = check_position_compatibility(key, structure_a, structure_b, size_a, size_b)
        if result.compatible:
            compatible.append(key)
    
    return compatible


def get_suggested_positions(
    structure_a: BodyStructureType,
    structure_b: BodyStructureType,
) -> List[Tuple[str, str]]:
    """
    Get position suggestions with compatibility notes.
    
    Returns:
        List of (position_key, note) tuples
    """
    from .library import POSITIONS
    
    suggestions = []
    traits_a = get_structure_traits(structure_a)
    traits_b = get_structure_traits(structure_b)
    
    for key, position in POSITIONS.items():
        # Check if tags match preferences
        a_likes = traits_a.compatible_tags & position.tags
        b_likes = traits_b.compatible_tags & position.tags
        
        result = check_position_compatibility(key, structure_a, structure_b)
        
        if result.compatible:
            note = ""
            if a_likes or b_likes:
                note = "recommended"
            elif result.warnings:
                note = result.warnings[0]
            suggestions.append((key, note))
        elif result.suggested_variant:
            suggestions.append((result.suggested_variant, f"variant of {key}"))
    
    return suggestions


# ============================================================================
# Zone Mapping for Different Structures
# ============================================================================

def map_zone_for_structure(
    zone: BodyZone,
    structure: BodyStructureType
) -> Optional[BodyZone]:
    """
    Map a standard zone to what exists on a specific body structure.
    
    Some structures don't have certain zones, or have equivalents.
    
    Returns:
        The equivalent zone, or None if no equivalent
    """
    traits = get_structure_traits(structure)
    
    # If the zone exists on this structure, return it
    if zone in traits.zones_present and zone not in traits.zones_absent:
        return zone
    
    # Handle mappings for missing zones
    if zone in traits.zones_absent:
        # Try to find equivalents
        if zone == BodyZone.ASS:
            if structure == BodyStructureType.SERPENTINE:
                return BodyZone.TAIL  # Vent area is on tail
            if structure == BodyStructureType.AQUATIC:
                return BodyZone.TAIL
        
        if zone == BodyZone.CHEST:
            if structure == BodyStructureType.QUADRUPED:
                return BodyZone.SHOULDERS  # Closest equivalent
        
        if zone == BodyZone.HANDS:
            if structure == BodyStructureType.QUADRUPED:
                return BodyZone.FEET  # Forepaws
        
        if zone in {BodyZone.LEGS, BodyZone.THIGHS, BodyZone.FEET}:
            if structure in {BodyStructureType.SERPENTINE, BodyStructureType.AQUATIC}:
                return BodyZone.TAIL
        
        return None
    
    return zone


def get_accessible_zones_for_structure(
    from_structure: BodyStructureType,
    to_structure: BodyStructureType,
    base_zones: Set[BodyZone]
) -> Set[BodyZone]:
    """
    Filter accessible zones based on what actually exists on the target.
    
    Args:
        from_structure: The one doing the accessing
        to_structure: The one being accessed
        base_zones: The zones the position would normally grant access to
        
    Returns:
        Filtered set of zones that actually exist on the target
    """
    to_traits = get_structure_traits(to_structure)
    
    result = set()
    
    for zone in base_zones:
        mapped = map_zone_for_structure(zone, to_structure)
        if mapped:
            result.add(mapped)
    
    return result


# ============================================================================
# Special Position Variants for Non-Standard Bodies
# ============================================================================

# These would be registered as actual positions in the library
# Here we define the concepts

QUADRUPED_POSITIONS = {
    "mounted": "Standard quadruped mating - one mounts the other from behind",
    "reverse_mounted": "Mounted facing backward",
    "side_by_side": "Both lying on sides",
    "presenting": "One presents hindquarters to the other",
}

TAUR_POSITIONS = {
    "taur_mounting": "One taur mounts another, or a biped mounts the taur's back",
    "taur_rear": "Biped takes taur from behind while taur stands",
    "taur_oral": "Biped kneels before standing taur",
    "under_taur": "Biped lies under taur's barrel for access",
}

SERPENTINE_POSITIONS = {
    "coiled_embrace": "Serpent wraps coils around partner, face to face",
    "coiled_binding": "Serpent restrains partner in coils",
    "serpent_rear": "Partner takes serpent from behind the humanoid portion",
    "tail_wrapped": "Serpent's tail wraps partner's body during act",
}

MIXED_SPECIES_POSITIONS = {
    "size_difference_standing": "Large partner standing, small partner at convenient height",
    "size_difference_oral": "Small partner services large partner",
    "carried_fuck": "Large partner carries small partner during",
}
