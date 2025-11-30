"""
Room Grid Types

Room types with coordinate/shape support for mapped areas.
"""

from .indoor import GridMixin, IndoorGridRoom
from .outdoor import OutdoorGridRoom

__all__ = [
    "GridMixin",
    "IndoorGridRoom",
    "OutdoorGridRoom",
]
