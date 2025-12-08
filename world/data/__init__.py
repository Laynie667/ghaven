"""
World Data

Static data for world building:
- Ambient activity pools
- Sound profiles and bleeding
- Time/weather descriptions
"""

from .activities import *
from .sounds import *

__all__ = [
    # Activities
    "PLAZA_ACTIVITIES",
    "MARKET_ACTIVITIES",
    "TAVERN_ACTIVITIES",
    "FOREST_ACTIVITIES",
    "WATERFRONT_ACTIVITIES",
    "MUSEUM_ACTIVITIES",
    "MINE_ACTIVITIES",
    "RESIDENTIAL_ACTIVITIES",
    "MEADOW_ACTIVITIES",
    "QUARRY_ACTIVITIES",
    "DAWN_ACTIVITIES",
    "MORNING_ACTIVITIES",
    "EVENING_ACTIVITIES",
    "NIGHT_ACTIVITIES",
    
    # Sounds
    "PLAZA_SOUNDS",
    "MARKET_SOUNDS",
    "TAVERN_SOUNDS",
    "FORGE_SOUNDS",
    "LIBRARY_SOUNDS",
    "WATERFRONT_SOUNDS",
    "FOREST_SOUNDS",
    "MINE_SOUNDS",
    "QUARRY_SOUNDS",
    "MUSEUM_SOUNDS",
    "RESIDENTIAL_SOUNDS",
    "VOLUME_MODIFIERS",
    "BARRIER_SOUND_REDUCTION",
    "WEATHER_SOUND_MODS",
    "get_sound_from_distance",
    "apply_barrier_reduction",
]
