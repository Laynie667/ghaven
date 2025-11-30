"""
Core body composition classes.

- Body: Main body class that combines structure + species + sex
- PartInstance: Runtime instance of a body part
- PartDefinition: Static definition of a part type
- Presets: Quick-compose functions for common body types
"""

from .parts import (
    PartDefinition,
    PART_REGISTRY,
    get_part,
    get_parts_with_function,
    get_children_of,
    list_optional_parts,
    list_sexual_parts,
)

from .body import (
    Body,
    PartInstance,
    PartState,
)

from .presets import (
    compose_human_male,
    compose_human_female,
    compose_elf_male,
    compose_elf_female,
    compose_wolf_anthro_male,
    compose_wolf_anthro_female,
    compose_wolf_feral,
    compose_cat_anthro_female,
    compose_horse_anthro_male,
    compose_centaur_male,
    compose_centaur_female,
    compose_lamia_female,
    compose_mermaid,
    compose_succubus,
    compose_herm_wolf,
    compose_futa_human,
    compose_femboy_fox,
    compose_futa_horse_human,
    compose_dickgirl_cat,
)

__all__ = [
    # Core classes
    "Body",
    "PartInstance",
    "PartState",
    
    # Part definitions
    "PartDefinition",
    "PART_REGISTRY",
    "get_part",
    "get_parts_with_function",
    "get_children_of",
    "list_optional_parts",
    "list_sexual_parts",
    
    # Presets
    "compose_human_male",
    "compose_human_female",
    "compose_elf_male",
    "compose_elf_female",
    "compose_wolf_anthro_male",
    "compose_wolf_anthro_female",
    "compose_wolf_feral",
    "compose_cat_anthro_female",
    "compose_horse_anthro_male",
    "compose_centaur_male",
    "compose_centaur_female",
    "compose_lamia_female",
    "compose_mermaid",
    "compose_succubus",
    "compose_herm_wolf",
    "compose_futa_human",
    "compose_femboy_fox",
    "compose_futa_horse_human",
    "compose_dickgirl_cat",
]
