"""
Body System Package

A layered body composition system for characters.

ARCHITECTURE:
    1. STRUCTURE  → Skeleton, locomotion type (bipedal, quadruped, tauroid, etc.)
    2. SPECIES    → Creature type, cosmetic features, genital_category
    3. SEX        → male/female/herm/futa/etc (uses species genital type)
    4. PRESENTATION → Marks, fluids, state (CHARACTER LEVEL ONLY)

USAGE:
    from typeclasses.body import Body
    
    # Compose a body (structure, species, sex)
    body = Body.compose(
        structure="bipedal_digitigrade",
        species="wolf",
        sex="female"  # Uses canine genitals because wolf has genital_category="canine"
    )
    
    # Initialize sexual state tracking
    body.init_sexual_states()
    
    # Override genital type
    body = Body.compose(
        structure="bipedal_plantigrade",
        species="human",
        sex="futa",
        genital_override="equine"  # Human futa with horse cock
    )
    
    # Check capabilities
    can_speak, msg = body.can_speak()
    sight_penalty = body.get_sight_penalty()
    
    # Modify
    body.injure_part("left_arm", 2, "deep gash")
    body.obstruct_part("mouth", "#gag123", "ball_gag")
    
    # Save to character
    character.db.body_data = body.to_dict()

FOLDER STRUCTURE:
    body/
    ├── core/           - Body class, parts, presets
    ├── templates/      - Static definitions (structures, species, anatomy, sexual parts)
    ├── state/          - Runtime state tracking (sexual states, presentation)
    ├── mechanics/      - Calculations (fit, arousal, fluids)
    ├── description/    - Description shortcode system
    └── actions/        - Action framework
"""

# =============================================================================
# CORE - Body composition
# =============================================================================
from .core import (
    # Main classes
    Body,
    PartInstance,
    PartState,
    
    # Part definitions
    PartDefinition,
    PART_REGISTRY,
    get_part,
    get_parts_with_function,
    get_children_of,
    list_optional_parts,
    list_sexual_parts,
    
    # Presets
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

# =============================================================================
# TEMPLATES - Static definitions
# =============================================================================
from .templates import (
    # Structures
    BodyStructure,
    STRUCTURE_REGISTRY,
    get_structure,
    list_structures,
    get_structures_by_locomotion,
    
    # Species
    SpeciesFeatures,
    SPECIES_REGISTRY,
    get_species,
    list_species,
    get_species_by_covering,
    
    # Anatomy (sex configs)
    SexConfig,
    SEX_REGISTRY,
    get_sex_config,
    list_sex_configs,
    get_configs_by_presentation,
    get_configs_by_role,
    GENITAL_PARTS,
    get_genital_parts,
    get_parts_to_remove,
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
    
    # Sexual parts
    ArousalState,
    OrificeState,
    KnotState,
    OrificeMechanics,
    PenetratorMechanics,
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

# =============================================================================
# STATE - Runtime tracking
# =============================================================================
from .state import (
    # Sexual state
    SexualStateManager,
    OrificeStateData,
    PenetratorStateData,
    BreastStateData,
    
    # Presentation
    BodyPresentation,
    Mark,
    MarkType,
    FluidPresence,
    FluidType,
    BodyState,
    BodyStateType,
)

# =============================================================================
# MECHANICS - Calculations
# =============================================================================
from .mechanics import (
    # Result types
    FitResult,
    PenetrationResult,
    ArousalChange,
    
    # Calculations
    calculate_fit,
    calculate_knot_lock,
    calculate_knot_unlock_time,
    calculate_arousal_change,
    calculate_arousal_decay,
    calculate_cum_production,
    calculate_cum_volume,
    calculate_cum_capacity,
    calculate_natural_wetness,
    calculate_lube_depletion,
    calculate_stretch_recovery,
    calculate_permanent_stretch,
    check_virginity_loss,
    calculate_zone_stimulation,
    calculate_conception_chance,
    get_fit_description,
)

# =============================================================================
# DESCRIPTION - Shortcode system
# =============================================================================
from .description import (
    ClothingState,
    ArousalLevel,
    PartDescriptions,
    PartShortcodeProcessor,
    process_description,
    get_character_description,
    COCK_DESCS,
    SIZE_WORDS,
)

# =============================================================================
# ACTIONS - Interaction framework
# =============================================================================
from .actions import (
    ActionCategory,
    ActionResult,
    ActionRequirement,
    ActionEffect,
    ActionDefinition,
    ActionAttempt,
    ActionOutcome,
    ACTIONS,
    get_action,
    get_actions_by_category,
    get_available_actions,
    get_actions_for_part,
    execute_action,
    check_action_requirements,
)


__all__ = [
    # Core
    "Body",
    "PartInstance",
    "PartState",
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
    
    # State
    "SexualStateManager",
    "OrificeStateData",
    "PenetratorStateData",
    "BreastStateData",
    "BodyPresentation",
    "Mark",
    "MarkType",
    "FluidPresence",
    "FluidType",
    "BodyState",
    "BodyStateType",
    
    # Mechanics
    "FitResult",
    "PenetrationResult",
    "ArousalChange",
    "calculate_fit",
    "calculate_knot_lock",
    "calculate_knot_unlock_time",
    "calculate_arousal_change",
    "calculate_arousal_decay",
    "calculate_cum_production",
    "calculate_cum_volume",
    "calculate_cum_capacity",
    "calculate_natural_wetness",
    "calculate_lube_depletion",
    "calculate_stretch_recovery",
    "calculate_permanent_stretch",
    "check_virginity_loss",
    "calculate_zone_stimulation",
    "calculate_conception_chance",
    "get_fit_description",
    
    # Description
    "ClothingState",
    "ArousalLevel",
    "PartDescriptions",
    "PartShortcodeProcessor",
    "process_description",
    "get_character_description",
    "COCK_DESCS",
    "SIZE_WORDS",
    
    # Actions
    "ActionCategory",
    "ActionResult",
    "ActionRequirement",
    "ActionEffect",
    "ActionDefinition",
    "ActionAttempt",
    "ActionOutcome",
    "ACTIONS",
    "get_action",
    "get_actions_by_category",
    "get_available_actions",
    "get_actions_for_part",
    "execute_action",
    "check_action_requirements",
]
