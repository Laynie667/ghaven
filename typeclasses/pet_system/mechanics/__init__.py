"""
Mechanics Package
=================

Combat and restraint mechanics:
- Grappling and holds
- Rope bondage
"""

from .grappling import (
    GrappleState,
    HoldType,
    StruggleResult,
    Hold,
    ALL_HOLDS,
    GrappleInstance,
    GrappleSystem,
    GrappleMixin,
)

from .rope_bondage import (
    RopeType,
    TiePattern,
    BondagePosition,
    Rope,
    TieDefinition,
    ALL_TIES,
    ActiveBondage,
    BondageSystem,
    BondageMixin,
)

from .mechanics_commands import MechanicsCmdSet


__all__ = [
    # Grappling
    "GrappleState",
    "HoldType",
    "StruggleResult",
    "Hold",
    "ALL_HOLDS",
    "GrappleInstance",
    "GrappleSystem",
    "GrappleMixin",
    
    # Bondage
    "RopeType",
    "TiePattern",
    "BondagePosition",
    "Rope",
    "TieDefinition",
    "ALL_TIES",
    "ActiveBondage",
    "BondageSystem",
    "BondageMixin",
    
    # Commands
    "MechanicsCmdSet",
]
