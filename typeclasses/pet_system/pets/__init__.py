"""
Pets Package
============

Complete pet systems including:
- Feral pet stats, training, packs, offspring
- Pet play for humanoids
- Pet gear
"""

from .feral_stats import (
    PetMood,
    BondLevel,
    TrainingLevel,
    PetStats,
    PetStatsMixin,
)

from .feral_training import (
    TrickCategory,
    Trick,
    TRICKS,
    TrainingSession,
    TrainingSystem,
    get_trick,
    list_tricks_by_category,
    get_trick_by_command,
)

from .feral_packs import (
    PackRank,
    PackRole,
    PackBehavior,
    PackMember,
    Pack,
    PackManager,
    PackMixin,
    calculate_pack_compatibility,
    get_rank_display,
)

from .feral_offspring import (
    GestationStage,
    OffspringStage,
    SPECIES_BREEDING_DATA,
    get_species_breeding_data,
    InheritableTraits,
    Pregnancy,
    Offspring,
    BreedingSystem,
    PregnancyMixin,
)

from .pet_play import (
    PetPlayType,
    PetTypeDefinition,
    PET_TYPE_DEFINITIONS,
    get_pet_type_def,
    HeadspaceDepth,
    PetHeadspace,
    PetPlayMixin,
    PetPlayTraining,
    list_pet_types,
    get_pet_type_description,
    get_matching_pet_type,
)

from .pet_gear import (
    PetGearSlot,
    GearEffect,
    PetGear,
    ALL_PET_GEAR,
    get_gear,
    get_gear_for_pet_type,
    get_gear_by_slot,
    PetGearMixin,
    GEAR_SETS,
    get_gear_set,
)


__all__ = [
    # Feral Stats
    "PetMood",
    "BondLevel",
    "TrainingLevel",
    "PetStats",
    "PetStatsMixin",
    
    # Feral Training
    "TrickCategory",
    "Trick",
    "TRICKS",
    "TrainingSession",
    "TrainingSystem",
    "get_trick",
    "list_tricks_by_category",
    "get_trick_by_command",
    
    # Feral Packs
    "PackRank",
    "PackRole",
    "PackBehavior",
    "PackMember",
    "Pack",
    "PackManager",
    "PackMixin",
    "calculate_pack_compatibility",
    "get_rank_display",
    
    # Feral Offspring
    "GestationStage",
    "OffspringStage",
    "SPECIES_BREEDING_DATA",
    "get_species_breeding_data",
    "InheritableTraits",
    "Pregnancy",
    "Offspring",
    "BreedingSystem",
    "PregnancyMixin",
    
    # Pet Play
    "PetPlayType",
    "PetTypeDefinition",
    "PET_TYPE_DEFINITIONS",
    "get_pet_type_def",
    "HeadspaceDepth",
    "PetHeadspace",
    "PetPlayMixin",
    "PetPlayTraining",
    "list_pet_types",
    "get_pet_type_description",
    "get_matching_pet_type",
    
    # Pet Gear
    "PetGearSlot",
    "GearEffect",
    "PetGear",
    "ALL_PET_GEAR",
    "get_gear",
    "get_gear_for_pet_type",
    "get_gear_by_slot",
    "PetGearMixin",
    "GEAR_SETS",
    "get_gear_set",
]
