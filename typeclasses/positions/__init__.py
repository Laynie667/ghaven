"""
Position System
===============

Tracks spatial relationships between characters during interactions.

Positions define:
- Who can access what on whom
- What's exposed to non-participants
- Physical requirements (furniture, mobility)
- Custom flavor text for player expression

Example Usage:
    from typeclasses.positions import PositionManager, POSITIONS
    
    # Get a position
    missionary = POSITIONS.get("missionary")
    
    # Check if characters can use it
    can_use, reason = missionary.can_use(char_a, char_b, furniture=bed)
    
    # Start the position
    manager = PositionManager()
    active = manager.start_position(
        "missionary",
        participants={"top": char_a, "bottom": char_b},
        anchor=bed,
        custom_flavor="pinning them down firmly"
    )
    
    # Check access
    zones = active.get_accessible_zones("top", "bottom")
    # {BodyZone.GROIN, BodyZone.CHEST, BodyZone.FACE, ...}
    
    # What can outsiders access on the bottom?
    exposed = active.get_exposed_zones("bottom")
    # {BodyZone.MOUTH, BodyZone.FACE}  # Mouth still accessible!
"""

from .core import (
    BodyZone,
    Posture,
    Mobility,
    FurnitureType,
    ZONE_TO_PARTS,
    PART_TO_ZONE,
    parts_in_zone,
    zones_for_part,
)

from .definitions import (
    SlotDefinition,
    PositionRequirement,
    PositionDefinition,
)

from .active import (
    ActivePosition,
    SlotOccupant,
)

from .library import (
    POSITIONS,
    get_position,
    get_positions_by_tag,
    get_positions_for_furniture,
    get_positions_for_participant_count,
    search_positions,
)

from .manager import PositionManager

from .species import (
    BodyStructureType,
    SizeCategory,
    StructureTraits,
    STRUCTURE_TRAITS,
    get_structure_traits,
    check_posture_compatibility,
    check_position_compatibility,
    get_compatible_positions,
    get_suggested_positions,
    map_zone_for_structure,
    get_accessible_zones_for_structure,
    CompatibilityResult,
)

# Import species-specific positions to register them
from . import species_positions

from .integration import (
    check_part_access,
    check_penetration_access,
    execute_penetration,
    execute_thrust,
    execute_oral,
    get_combined_state,
    do_fuck,
    do_thrust,
    do_lick,
    AccessResult,
    InteractionResult,
)

__all__ = [
    # Enums
    "BodyZone",
    "Posture",
    "Mobility",
    "FurnitureType",
    "BodyStructureType",
    "SizeCategory",
    # Mappings
    "ZONE_TO_PARTS",
    "PART_TO_ZONE",
    "STRUCTURE_TRAITS",
    "parts_in_zone",
    "zones_for_part",
    # Definitions
    "SlotDefinition",
    "PositionRequirement",
    "PositionDefinition",
    "StructureTraits",
    # Active tracking
    "ActivePosition",
    "SlotOccupant",
    # Library
    "POSITIONS",
    "get_position",
    "get_positions_by_tag",
    "get_positions_for_furniture",
    "get_positions_for_participant_count",
    "search_positions",
    # Manager
    "PositionManager",
    # Species compatibility
    "get_structure_traits",
    "check_posture_compatibility",
    "check_position_compatibility",
    "get_compatible_positions",
    "get_suggested_positions",
    "map_zone_for_structure",
    "get_accessible_zones_for_structure",
    "CompatibilityResult",
    # Integration
    "check_part_access",
    "check_penetration_access",
    "execute_penetration",
    "execute_thrust",
    "execute_oral",
    "get_combined_state",
    "do_fuck",
    "do_thrust",
    "do_lick",
    "AccessResult",
    "InteractionResult",
]
