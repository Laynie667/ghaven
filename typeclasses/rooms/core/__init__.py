"""
Room Core Types

Base room types that form the foundation of the room system.
"""

from .base import Room
from .indoor import IndoorRoom
from .outdoor import OutdoorRoom

__all__ = [
    "Room",
    "IndoorRoom", 
    "OutdoorRoom",
]
