"""
Training Package
================

Training, conditioning, and hypnosis systems:
- Breaking resistance
- Conditioning behaviors
- Hypnosis and suggestions
"""

from .training import (
    TrainingStage,
    ResistanceType,
    ConditioningType,
    ReinforcementType,
    ResistanceState,
    ConditionedBehavior,
    PRESET_BEHAVIORS,
    get_preset_behavior,
    TrainingSession,
    TrainingMethod,
    TRAINING_METHODS,
    get_training_method,
    TrainingSystem,
    TraineeMixin,
    TrainerMixin,
)

from .hypnosis import (
    TranceDepth,
    SuggestionType,
    SuggestionStrength,
    TranceState,
    HypnoticSuggestion,
    InductionTechnique,
    INDUCTION_TECHNIQUES,
    get_induction,
    HypnosisSystem,
    HypnotizableMixin,
    HypnotistMixin,
)

from .training_commands import (
    CmdBreak,
    CmdCondition,
    CmdTrigger,
    CmdHypnotize,
    CmdDeepen,
    CmdSuggest,
    CmdWake,
    CmdTranceStatus,
    TrainingCmdSet,
)


__all__ = [
    # Training
    "TrainingStage",
    "ResistanceType",
    "ConditioningType",
    "ReinforcementType",
    "ResistanceState",
    "ConditionedBehavior",
    "PRESET_BEHAVIORS",
    "get_preset_behavior",
    "TrainingSession",
    "TrainingMethod",
    "TRAINING_METHODS",
    "get_training_method",
    "TrainingSystem",
    "TraineeMixin",
    "TrainerMixin",
    
    # Hypnosis
    "TranceDepth",
    "SuggestionType",
    "SuggestionStrength",
    "TranceState",
    "HypnoticSuggestion",
    "InductionTechnique",
    "INDUCTION_TECHNIQUES",
    "get_induction",
    "HypnosisSystem",
    "HypnotizableMixin",
    "HypnotistMixin",
    
    # Commands
    "CmdBreak",
    "CmdCondition",
    "CmdTrigger",
    "CmdHypnotize",
    "CmdDeepen",
    "CmdSuggest",
    "CmdWake",
    "CmdTranceStatus",
    "TrainingCmdSet",
]
