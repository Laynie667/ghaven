"""
Body Anatomy Package

Defines sex configurations. Genital TYPE comes from species.

Order of composition:
    STRUCTURE → SPECIES → SEX → PRESENTATION
    
Species determines genital_category (canine, equine, human, etc.)
Sex config determines what organs (male, female, herm, futa, etc.)

Available sex configs:
    male, female, herm, futa, maleherm, cuntboy, femboy, 
    dickgirl, neuter, neuter_smooth, doll, female_multi, herm_multi

Usage:
    from typeclasses.body.anatomy import get_sex_config, FEMALE, get_genital_parts
    
    sex = get_sex_config("futa")
    parts = get_genital_parts("canine", sex)  # Gets canine-type futa parts
"""

from .base import (
    SexConfig,
    
    # Sex configurations
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
    
    # Part mappings
    GENITAL_PARTS,
    BREAST_PARTS,
    get_genital_parts,
    get_parts_to_remove,
    
    # Registry
    SEX_REGISTRY,
    get_sex_config,
    list_sex_configs,
    get_configs_by_presentation,
    get_configs_by_role,
    
    # Legacy support
    LEGACY_ANATOMY_MAP,
    resolve_legacy_anatomy,
)

__all__ = [
    "SexConfig",
    
    "MALE", "FEMALE", "HERM", "FUTA", "MALEHERM",
    "CUNTBOY", "FEMBOY", "DICKGIRL",
    "NEUTER", "NEUTER_SMOOTH", "DOLL",
    "FEMALE_MULTI", "HERM_MULTI",
    
    "GENITAL_PARTS", "BREAST_PARTS",
    "get_genital_parts", "get_parts_to_remove",
    
    "SEX_REGISTRY",
    "get_sex_config",
    "list_sex_configs",
    "get_configs_by_presentation",
    "get_configs_by_role",
    
    "LEGACY_ANATOMY_MAP",
    "resolve_legacy_anatomy",
]
