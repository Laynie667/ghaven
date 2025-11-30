"""
Body Presentation Package

Tracks surface state of a character's body - marks, fluids, physical state.

THIS IS ONLY APPLIED AT THE CHARACTER LEVEL.
Templates and base configurations do NOT include presentation.

Usage:
    from typeclasses.body.presentation import BodyPresentation, Mark, FluidPresence
    
    # On a character
    presentation = BodyPresentation()
    presentation.add_mark(Mark(MarkType.TATTOO, "left_arm", "A coiling dragon"))
    presentation.add_fluid(FluidPresence(FluidType.SWEAT, "chest", "light"))
"""

from .base import (
    # Enums
    MarkType,
    FluidType,
    BodyStateType,
    
    # Data classes
    Mark,
    FluidPresence,
    BodyState,
    
    # Main tracker
    BodyPresentation,
)

__all__ = [
    "MarkType",
    "FluidType", 
    "BodyStateType",
    "Mark",
    "FluidPresence",
    "BodyState",
    "BodyPresentation",
]
