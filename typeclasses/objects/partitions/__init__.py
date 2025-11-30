"""
Partitions Package

Partitions connect rooms without being traversable.
They allow sensory transmission and interaction between spaces.

Structure:
    base.py      - Core Partition class
    mixins.py    - OpeningMixin (body interaction), OperableMixin (open/close)
    types.py     - Preset partition types

Usage:
    from typeclasses.objects.partitions import Partition, GloryWall, WindowPartition
    from typeclasses.objects.partitions.mixins import OpeningMixin

Creating custom partitions:
    from typeclasses.objects.partitions import Partition
    from typeclasses.objects.partitions.mixins import OpeningMixin, OperableMixin
    
    class MySpecialPartition(OpeningMixin, OperableMixin, Partition):
        '''A custom partition with openings that can open/close.'''
        pass

Linking partitions:
    Two partitions must be linked to work together.
    
    # Create both partitions
    partition_a = create_object(GloryWall, key="wall", location=room_a)
    partition_b = create_object(GloryWall, key="wall", location=room_b)
    
    # Link them
    partition_a.db.partner_dbref = partition_b.dbref
    partition_b.db.partner_dbref = partition_a.dbref
"""

# Base
from .base import Partition

# Mixins
from .mixins import OpeningMixin, OperableMixin

# Preset types
from .types import (
    # Visual (see-through)
    WindowPartition,
    BarsPartition,
    FencePartition,
    
    # Opaque (block sight)
    WallPartition,
    CurtainPartition,
    ScreenPartition,
    
    # Opening (physical interaction)
    GloryWall,
    FeedingSlot,
    ServiceWindow,
    ConfessionalScreen,
    
    # Special
    MirrorPartition,
    MagicalBarrier,
)

__all__ = [
    # Base
    "Partition",
    
    # Mixins
    "OpeningMixin",
    "OperableMixin",
    
    # Types
    "WindowPartition",
    "BarsPartition",
    "FencePartition",
    "WallPartition",
    "CurtainPartition",
    "ScreenPartition",
    "GloryWall",
    "FeedingSlot",
    "ServiceWindow",
    "ConfessionalScreen",
    "MirrorPartition",
    "MagicalBarrier",
]
