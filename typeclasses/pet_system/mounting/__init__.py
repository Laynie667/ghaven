"""
Mounting Package
================

Systems for harnesses, belly mounting, and riding:
- Breeding and restraint harnesses
- Belly sling system for tauroids
- Saddles and riding
"""

from .harnesses import (
    HarnessType,
    HarnessSlot,
    Harness,
    ALL_HARNESSES,
    get_harness,
    get_harnesses_by_type,
    get_belly_slings,
    get_breeding_harnesses,
    HarnessMixin,
)

from .belly_mount import (
    BellyMountPosition,
    CarrierGait,
    ConcealmentLevel,
    GAIT_EFFECTS,
    BellyPositionDef,
    BELLY_POSITIONS,
    get_belly_position,
    SaddleBlanket,
    BellyMountState,
    BellyMountSystem,
    BellyMountCarrierMixin,
    BellyMountPassengerMixin,
)

from .riding import (
    SaddleType,
    RidingPosition,
    RiderState,
    Saddle,
    ALL_SADDLES,
    get_saddle,
    RidingState,
    RidingSystem,
    MountMixin,
    RiderMixin,
)


__all__ = [
    # Harnesses
    "HarnessType",
    "HarnessSlot",
    "Harness",
    "ALL_HARNESSES",
    "get_harness",
    "get_harnesses_by_type",
    "get_belly_slings",
    "get_breeding_harnesses",
    "HarnessMixin",
    
    # Belly Mount
    "BellyMountPosition",
    "CarrierGait",
    "ConcealmentLevel",
    "GAIT_EFFECTS",
    "BellyPositionDef",
    "BELLY_POSITIONS",
    "get_belly_position",
    "SaddleBlanket",
    "BellyMountState",
    "BellyMountSystem",
    "BellyMountCarrierMixin",
    "BellyMountPassengerMixin",
    
    # Riding
    "SaddleType",
    "RidingPosition",
    "RiderState",
    "Saddle",
    "ALL_SADDLES",
    "get_saddle",
    "RidingState",
    "RidingSystem",
    "MountMixin",
    "RiderMixin",
]
