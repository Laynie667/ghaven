"""
Body Templates - Static Definitions

Contains the data definitions for body composition:
- Structures: Body skeletal types (bipedal, quadruped, tauroid, etc.)
- Species: Creature types with cosmetic features
- Anatomy: Sex configurations (male, female, herm, etc.)
- Sexual Parts: Orifice and penetrator definitions
"""

from .structures import (
    BodyStructure,
    STRUCTURE_REGISTRY,
    get_structure,
    list_structures,
    get_structures_by_locomotion,
)

from .species import (
    SpeciesFeatures,
    SPECIES_REGISTRY,
    get_species,
    list_species,
    get_species_by_covering,
)

from .anatomy import (
    SexConfig,
    SEX_REGISTRY,
    get_sex_config,
    list_sex_configs,
    get_configs_by_presentation,
    get_configs_by_role,
    GENITAL_PARTS,
    get_genital_parts,
    get_parts_to_remove,
    # Sex config instances
    MALE,
    FEMALE,
    HERM,
    FUTA,
    MALEHERM,
    CUNTBOY,
    FEMBOY,
    DICKGIRL,
    NEUTER,
    NEUTER_SMOOTH,
    DOLL,
    FEMALE_MULTI,
    HERM_MULTI,
)

from .parts_sexual import (
    # Enums
    ArousalState,
    OrificeState,
    KnotState,
    
    # Mechanics dataclasses
    OrificeMechanics,
    PenetratorMechanics,
    
    # Sexual part definitions
    SexualPartDefinition,
    SEXUAL_PART_REGISTRY,
    get_sexual_part,
    get_orifices,
    get_penetrators,
    get_cock_by_category,
    get_male_parts,
    get_female_parts,
    get_breast_parts,
)

__all__ = [
    # Structures
    "BodyStructure",
    "STRUCTURE_REGISTRY",
    "get_structure",
    "list_structures",
    "get_structures_by_locomotion",
    
    # Species
    "SpeciesFeatures",
    "SPECIES_REGISTRY",
    "get_species",
    "list_species",
    "get_species_by_covering",
    
    # Anatomy
    "SexConfig",
    "SEX_REGISTRY",
    "get_sex_config",
    "list_sex_configs",
    "get_configs_by_presentation",
    "get_configs_by_role",
    "GENITAL_PARTS",
    "get_genital_parts",
    "get_parts_to_remove",
    "MALE",
    "FEMALE",
    "HERM",
    "FUTA",
    "MALEHERM",
    "CUNTBOY",
    "FEMBOY",
    "DICKGIRL",
    "NEUTER",
    "NEUTER_SMOOTH",
    "DOLL",
    "FEMALE_MULTI",
    "HERM_MULTI",
    
    # Sexual parts
    "ArousalState",
    "OrificeState",
    "KnotState",
    "OrificeMechanics",
    "PenetratorMechanics",
    "SexualPartDefinition",
    "SEXUAL_PART_REGISTRY",
    "get_sexual_part",
    "get_orifices",
    "get_penetrators",
    "get_cock_by_category",
    "get_male_parts",
    "get_female_parts",
    "get_breast_parts",
]
