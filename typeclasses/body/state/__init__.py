"""
Body State - Runtime State Tracking

Tracks the current state of body parts during gameplay:
- Sexual states: arousal, stretch, wetness, cum storage, etc.
- Presentation: marks, fluids, body conditions
"""

from .sexual import (
    SexualStateManager,
    OrificeStateData,
    PenetratorStateData,
    BreastStateData,
)

from .presentation import (
    BodyPresentation,
    Mark,
    MarkType,
    FluidPresence,
    FluidType,
    BodyState,
    BodyStateType,
)

__all__ = [
    # Sexual state
    "SexualStateManager",
    "OrificeStateData",
    "PenetratorStateData",
    "BreastStateData",
    
    # Presentation
    "BodyPresentation",
    "Mark",
    "MarkType",
    "FluidPresence",
    "FluidType",
    "BodyState",
    "BodyStateType",
]
