"""
NPC Package
===========

Complete NPC system with:
- Base NPC class with body integration
- Specialized NPC types (Ambient, Service, Companion, Feral, Guard, Unique)
- Behavior mixins (Conversation, Flirtation, Sexual, Pack, Territory, etc.)
- Feral mechanics (Knotting, Heat cycles, Leashing)
- Feral commands (pet, feed, tame, train, present, breed, etc.)
"""

from .base import (
    NPC,
    NPCType,
    BehaviorState,
    Disposition,
    Relationship,
    NPCPreferences,
)

from .npc_types import (
    AmbientNPC,
    ServiceNPC,
    CompanionNPC,
    FeralNPC,
    GuardNPC,
    UniqueNPC,
)

from .behaviors import (
    # Original mixins
    ConversationMixin,
    FlirtationMixin,
    SexualBehaviorMixin,
    PathfindingMixin,
    BehavioralNPC,
    # Feral behavior mixins
    FeralBehaviorMixin,
    PackBehaviorMixin,
    TerritoryBehaviorMixin,
    HuntingBehaviorMixin,
    MatingBehaviorMixin,
    FullFeralBehavior,
)

from .feral import (
    # Knot system
    KnotState,
    KnotConfig,
    TieData,
    KNOT_CONFIGS,
    # Heat system
    HeatPhase,
    HeatConfig,
    HEAT_CONFIGS,
    # Leash
    LeashState,
    LeashData,
    # Mixins
    KnottingMixin,
    HeatCycleMixin,
    FeralMechanicsMixin,
)

from .feral_commands import (
    FeralCmdSet,
    CmdPet,
    CmdFeed,
    CmdTame,
    CmdTrain,
    CmdPresent,
    CmdBreed,
    CmdFeralStatus,
    CmdKnotStatus,
    CmdStruggle,
)


__all__ = [
    # Base
    "NPC",
    "NPCType",
    "BehaviorState",
    "Disposition",
    "Relationship",
    "NPCPreferences",
    # Types
    "AmbientNPC",
    "ServiceNPC",
    "CompanionNPC",
    "FeralNPC",
    "GuardNPC",
    "UniqueNPC",
    # Behavior mixins
    "ConversationMixin",
    "FlirtationMixin",
    "SexualBehaviorMixin",
    "PathfindingMixin",
    "BehavioralNPC",
    # Feral behavior mixins
    "FeralBehaviorMixin",
    "PackBehaviorMixin",
    "TerritoryBehaviorMixin",
    "HuntingBehaviorMixin",
    "MatingBehaviorMixin",
    "FullFeralBehavior",
    # Knot system
    "KnotState",
    "KnotConfig",
    "TieData",
    "KNOT_CONFIGS",
    # Heat system
    "HeatPhase",
    "HeatConfig",
    "HEAT_CONFIGS",
    # Leash system
    "LeashState",
    "LeashData",
    # Mechanic mixins
    "KnottingMixin",
    "HeatCycleMixin",
    "FeralMechanicsMixin",
    # Commands
    "FeralCmdSet",
    "CmdPet",
    "CmdFeed",
    "CmdTame",
    "CmdTrain",
    "CmdPresent",
    "CmdBreed",
    "CmdFeralStatus",
    "CmdKnotStatus",
    "CmdStruggle",
]
