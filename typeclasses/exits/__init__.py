"""
Exits Package

All exit types for the game.

Structure:
    base.py      - Core Exit class with sensory/grid features
    mixins.py    - Behavior mixins (Door, Secret, Traversal, etc.)
    types.py     - Preset exit types combining base + mixins

Usage:
    from typeclasses.exits import Exit, DoorExit, SecretDoor
    from typeclasses.exits.mixins import DoorMixin, SecretMixin

Creating custom exits:
    from typeclasses.exits import Exit
    from typeclasses.exits.mixins import DoorMixin, SecretMixin, TraversalMixin
    
    class MySpecialDoor(DoorMixin, SecretMixin, TraversalMixin, Exit):
        '''A hidden climbing door!'''
        pass
"""

# Base
from .base import Exit

# Mixins
from .mixins import (
    DoorMixin,
    SecretMixin,
    TraversalMixin,
    BarrierMixin,
    TrapMixin,
)

# Preset types
from .types import (
    # Doors
    DoorExit,
    HeavyDoor,
    PortcullisExit,
    CurtainExit,
    
    # Secret
    SecretExit,
    SecretDoor,
    BookshelfDoor,
    
    # Traversal
    ClimbableExit,
    SwimExit,
    CrawlExit,
    JumpExit,
    
    # Traps
    TrapDoor,
    OneWayExit,
    FallExit,
    
    # Combinations
    HatchExit,
    SecretTrapDoor,
    WindowExit,
    
    # Special
    MagicalPortal,
    ElevatorExit,
)

__all__ = [
    # Base
    "Exit",
    
    # Mixins
    "DoorMixin",
    "SecretMixin",
    "TraversalMixin",
    "BarrierMixin",
    "TrapMixin",
    
    # Preset types
    "DoorExit",
    "HeavyDoor",
    "PortcullisExit",
    "CurtainExit",
    "SecretExit",
    "SecretDoor",
    "BookshelfDoor",
    "ClimbableExit",
    "SwimExit",
    "CrawlExit",
    "JumpExit",
    "TrapDoor",
    "OneWayExit",
    "FallExit",
    "HatchExit",
    "SecretTrapDoor",
    "WindowExit",
    "MagicalPortal",
    "ElevatorExit",
]
