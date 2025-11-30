"""
Substances Package
==================

Potions, drugs, and transformation systems:
- Consumable substances with effects
- Active effect tracking
- Species/body transformations
"""

from .potions import (
    SubstanceType,
    EffectCategory,
    EffectIntensity,
    AddictionLevel,
    SubstanceEffect,
    ActiveEffect,
    Substance,
    ALL_SUBSTANCES,
    get_substance,
    get_substances_by_category,
    SubstanceSystem,
    SubstanceAffectedMixin,
)

from .transformation import (
    TransformationType,
    TransformationDuration,
    TransformationStage,
    BodyChange,
    Transformation,
    ActiveTransformation,
    ALL_TRANSFORMATIONS,
    POTION_TRANSFORMATION_MAP,
    get_transformation,
    TransformationSystem,
    TransformableMixin,
)

from .substance_commands import SubstanceCmdSet


__all__ = [
    # Potions
    "SubstanceType",
    "EffectCategory",
    "EffectIntensity",
    "AddictionLevel",
    "SubstanceEffect",
    "ActiveEffect",
    "Substance",
    "ALL_SUBSTANCES",
    "get_substance",
    "get_substances_by_category",
    "SubstanceSystem",
    "SubstanceAffectedMixin",
    
    # Transformation
    "TransformationType",
    "TransformationDuration",
    "TransformationStage",
    "BodyChange",
    "Transformation",
    "ActiveTransformation",
    "ALL_TRANSFORMATIONS",
    "POTION_TRANSFORMATION_MAP",
    "get_transformation",
    "TransformationSystem",
    "TransformableMixin",
    
    # Commands
    "SubstanceCmdSet",
]
