"""
Rooms Package

All room types for the game.

Usage:
    from typeclasses.rooms import Room, IndoorRoom, OutdoorRoom
    from typeclasses.rooms.grid import IndoorGridRoom, OutdoorGridRoom
    from typeclasses.rooms.presets import TavernRoom  # When available

Hierarchy:
    Room (base)
    ├── IndoorRoom
    │   └── IndoorGridRoom
    │       └── presets (DungeonRoom, TavernRoom, etc.)
    └── OutdoorRoom
        └── OutdoorGridRoom
            └── presets (WildernessRoom, RoadRoom, etc.)
"""

# Core room types
from .core import Room, IndoorRoom, OutdoorRoom

# Grid room types
from .grid import GridMixin, IndoorGridRoom, OutdoorGridRoom

# Presets - uncomment as they're created
# from .presets import TavernRoom, DungeonRoom, etc.

__all__ = [
    # Core
    "Room",
    "IndoorRoom",
    "OutdoorRoom",
    
    # Grid
    "GridMixin",
    "IndoorGridRoom",
    "OutdoorGridRoom",
    
    # Presets - add as created
]
