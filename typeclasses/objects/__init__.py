"""
Objects Package

All object types for the game.

Structure:
    base.py              - ObjectParent mixin, base Object class
    partitions/          - Partition objects (windows, bars, glory walls)
    furniture/           - Usable furniture (beds, chairs, restraints)

Usage:
    from typeclasses.objects import ObjectParent, Object
    from typeclasses.objects.partitions import Partition, GloryWall
    from typeclasses.objects.furniture import Bed  # (when implemented)
"""

from .base import ObjectParent, Object

# Make partitions accessible
from . import partitions

__all__ = [
    "ObjectParent",
    "Object",
    "partitions",
]
