"""
Body Description System

Handles dynamic description generation with shortcodes.
Players write descriptions with [part:X] tags that get replaced
based on current state (dressed/nude, aroused/normal).
"""

from .shortcodes import (
    # State enums
    ClothingState,
    ArousalLevel,
    
    # Template class
    PartDescriptions,
    
    # Processor
    PartShortcodeProcessor,
    
    # Convenience functions
    process_description,
    get_character_description,
    
    # Templates
    COCK_DESCS,
    SIZE_WORDS,
)

__all__ = [
    # State enums
    "ClothingState",
    "ArousalLevel",
    
    # Template class
    "PartDescriptions",
    
    # Processor
    "PartShortcodeProcessor",
    
    # Convenience functions
    "process_description",
    "get_character_description",
    
    # Templates
    "COCK_DESCS",
    "SIZE_WORDS",
]
