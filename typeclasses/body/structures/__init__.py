"""
Body Structures Package

Defines fundamental body skeletons and locomotion types.

Available structures:
    - bipedal_plantigrade: Walks upright on flat feet (humans, elves)
    - bipedal_digitigrade: Walks upright on toes (anthros)
    - bipedal_digitigrade_paws: Digitigrade with paws instead of hands
    - quadruped: Four-legged, pawed (dogs, wolves)
    - quadruped_hooved: Four-legged, hooved (horses, deer)
    - tauroid: Humanoid upper, quadruped lower (centaurs)
    - serpentine: Humanoid upper, snake lower (lamia, nagas)
    - aquatic: Humanoid upper, fish tail (merfolk)
    - avian: Bird-like with wings for arms (harpies)
    - tentacled: Humanoid with tentacles

Usage:
    from typeclasses.body.structures import get_structure, BIPEDAL_PLANTIGRADE
    
    structure = get_structure("bipedal_digitigrade")
"""

from .base import (
    BodyStructure,
    
    # Structures
    BIPEDAL_PLANTIGRADE,
    BIPEDAL_DIGITIGRADE,
    BIPEDAL_DIGITIGRADE_PAWS,
    QUADRUPED,
    QUADRUPED_HOOVED,
    TAUROID,
    SERPENTINE,
    AQUATIC,
    AVIAN,
    TENTACLED,
    
    # Registry
    STRUCTURE_REGISTRY,
    get_structure,
    list_structures,
    get_structures_by_locomotion,
)

__all__ = [
    "BodyStructure",
    
    "BIPEDAL_PLANTIGRADE",
    "BIPEDAL_DIGITIGRADE",
    "BIPEDAL_DIGITIGRADE_PAWS",
    "QUADRUPED",
    "QUADRUPED_HOOVED",
    "TAUROID",
    "SERPENTINE",
    "AQUATIC",
    "AVIAN",
    "TENTACLED",
    
    "STRUCTURE_REGISTRY",
    "get_structure",
    "list_structures",
    "get_structures_by_locomotion",
]
