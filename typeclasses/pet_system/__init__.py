"""
Pet Systems Package
===================

Comprehensive adult systems for MUD games built on Evennia.

Core Subpackages:
- pets: Feral pet stats, training, tricks, packs, offspring
- mounting: Harnesses, belly mounts, riding, saddles  
- clothing: Clothing system with slots and states
- breeding: Pregnancy and offspring systems
- economy: Currency, shops, ownership, slave market
- training: Breaking, conditioning, hypnosis
- substances: Potions, drugs, transformations
- social: Relationships, reputation, harems
- mechanics: Grappling, rope bondage
- service: Maid/butler roles, tasks, performances
- production: Lactation, milking stations

Extended Systems:
- slavery: Full slavery system with acquisition, training, documentation
- hucow: Dairy farm system with lactation, bulls, breeding
- brothel: Client generation, services, reputation, scheduling
- corruption: Transformation paths (bimbo, demon, slut, hucow, etc.)
- pony: Cart pulling, shows, competitions, breeding
- monsters: Tentacles, oviposition, parasites, corruption
- inflation: Cum inflation, belly expansion, capacity limits
- arena: Sexual combat, defeat consequences, tournaments

World Content:
- world: NPCs, locations, random events, encounters

Integration:
- integration: Unified character mixins, cross-system hooks

Total: 80+ files, 50,000+ lines
"""

__version__ = "2.0.0"
__author__ = "Laynie"

# Convenience imports for common items
from .economy import (
    CurrencyType,
    Wallet,
    WalletMixin,
    Shop,
    ShopManager,
    OwnershipType,
    OwnershipRecord,
    OwnerMixin,
    PropertyMixin,
)
from .economy.economy_commands import EconomyCmdSet

from .substances import (
    Substance,
    SubstanceSystem,
    SubstanceAffectedMixin,
    Transformation,
    TransformationSystem,
    TransformableMixin,
    SubstanceCmdSet,
)

from .social import (
    Relationship,
    RelationshipMixin,
    Harem,
    SocialCmdSet,
)

from .mechanics import (
    GrappleInstance,
    GrappleSystem,
    GrappleMixin,
    ActiveBondage,
    BondageSystem,
    BondageMixin,
    MechanicsCmdSet,
)

from .service import (
    ServiceTask,
    ServantMixin,
    ServiceCmdSet,
)

from .production import (
    ProductionStats,
    ProducerMixin,
    ProductionCmdSet,
)

# New system imports
from .brothel import (
    ServiceType,
    ClientType,
    WhoreSpecialization,
    WhoreStats,
    Brothel,
    WhoreMixin,
    BrothelCmdSet,
)

from .corruption import (
    TransformationType,
    TransformationStage,
    CorruptionSource,
    TransformationManager,
    TransformationMixin,
    CorruptionCmdSet,
)

from .pony import (
    PonyType,
    PonyGait,
    TackType,
    PonyStats,
    PonyMixin,
    PonyCmdSet,
)

from .monsters import (
    MonsterType,
    BreedingMethod,
    EggType,
    OvipositionRecord,
    MonsterBreedingMixin,
    MonsterCmdSet,
)

from .inflation import (
    InflationType,
    InflationLocation,
    DistensionLevel,
    InflationTracker,
    InflationMixin,
    InflationCmdSet,
)

from .arena import (
    CombatStyle,
    CombatMove,
    CombatStats,
    Fight,
    Tournament,
    CombatMixin,
    ArenaCmdSet,
)

# World content
from .world import (
    NPCRole,
    Disposition,
    NPCTemplate,
    ALL_NPC_TEMPLATES,
    generate_npc,
)

from .world.locations import (
    LocationType,
    LocationTemplate,
    ALL_LOCATION_TEMPLATES,
)

from .world.events import (
    EventType,
    EventTemplate,
    ALL_EVENT_TEMPLATES,
    get_random_event,
    trigger_event,
)


__all__ = [
    # Version
    "__version__",
    "__author__",
    
    # Economy
    "CurrencyType",
    "Wallet",
    "WalletMixin",
    "Shop",
    "ShopManager",
    "OwnershipType",
    "OwnershipRecord",
    "OwnerMixin",
    "PropertyMixin",
    "EconomyCmdSet",
    
    # Substances
    "Substance",
    "SubstanceSystem",
    "SubstanceAffectedMixin",
    "Transformation",
    "TransformationSystem",
    "TransformableMixin",
    "SubstanceCmdSet",
    
    # Social
    "Relationship",
    "RelationshipMixin",
    "Harem",
    "SocialCmdSet",
    
    # Mechanics
    "GrappleInstance",
    "GrappleSystem",
    "GrappleMixin",
    "ActiveBondage",
    "BondageSystem",
    "BondageMixin",
    "MechanicsCmdSet",
    
    # Service
    "ServiceTask",
    "ServantMixin",
    "ServiceCmdSet",
    
    # Production
    "ProductionStats",
    "ProducerMixin",
    "ProductionCmdSet",
    
    # Brothel
    "ServiceType",
    "ClientType",
    "WhoreSpecialization",
    "WhoreStats",
    "Brothel",
    "WhoreMixin",
    "BrothelCmdSet",
    
    # Corruption
    "TransformationType",
    "TransformationStage",
    "CorruptionSource",
    "TransformationManager",
    "TransformationMixin",
    "CorruptionCmdSet",
    
    # Pony
    "PonyType",
    "PonyGait",
    "TackType",
    "PonyStats",
    "PonyMixin",
    "PonyCmdSet",
    
    # Monsters
    "MonsterType",
    "BreedingMethod",
    "EggType",
    "OvipositionRecord",
    "MonsterBreedingMixin",
    "MonsterCmdSet",
    
    # Inflation
    "InflationType",
    "InflationLocation",
    "DistensionLevel",
    "InflationTracker",
    "InflationMixin",
    "InflationCmdSet",
    
    # Arena
    "CombatStyle",
    "CombatMove",
    "CombatStats",
    "Fight",
    "Tournament",
    "CombatMixin",
    "ArenaCmdSet",
    
    # World - NPCs
    "NPCRole",
    "Disposition",
    "NPCTemplate",
    "ALL_NPC_TEMPLATES",
    "generate_npc",
    
    # World - Locations
    "LocationType",
    "LocationTemplate",
    "ALL_LOCATION_TEMPLATES",
    
    # World - Events
    "EventType",
    "EventTemplate",
    "ALL_EVENT_TEMPLATES",
    "get_random_event",
    "trigger_event",
]
