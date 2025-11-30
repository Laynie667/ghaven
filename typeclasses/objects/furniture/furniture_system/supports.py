"""
Furniture - Support

Support furniture: walls, pillars, posts.
These provide vertical surfaces to lean against, be pressed to, etc.

Inheritance:
    Furniture
    └── Support
        ├── Wall
        │   └── PaddedWall
        ├── Pillar
        │   └── OrnamentedPillar
        └── Post
            ├── WhippingPost
            └── TetheredPost
"""

from typing import Dict, Set
from .base import (
    Furniture,
    FurnitureType,
    FurnitureSlot,
    OccupantPosition,
)


# =============================================================================
# SUPPORT BASE
# =============================================================================

class Support(Furniture):
    """
    Base class for support furniture (vertical surfaces).
    
    Supports:
    - Standing against
    - Pressed against
    - Tied to (if has attachment points)
    """
    
    def at_object_creation(self):
        super().at_object_creation()
        self.db.furniture_type = FurnitureType.WALL
        self.db.position_tags = {"standing", "against", "pressed"}
    
    def get_slots(self) -> Dict[str, FurnitureSlot]:
        return {
            "against": FurnitureSlot(
                key="against",
                name="against the surface",
                max_occupants=1,
                positions={
                    OccupantPosition.STANDING,
                },
                exposed_zones={"front", "groin", "chest"},
                blocked_zones={"back"},
                description="{name} stands with their back against the surface",
            ),
        }


# =============================================================================
# WALLS
# =============================================================================

class Wall(Support):
    """
    A wall section. Can lean against, be pressed to, be pinned against.
    
    Position support:
    - Standing against (back to wall)
    - Facing wall (hands on wall)
    - Pinned (against wall)
    """
    
    def at_object_creation(self):
        super().at_object_creation()
        self.db.furniture_type = FurnitureType.WALL
        self.db.position_tags = {
            "standing", "against", "wall",
            "pinned", "pressed",
            "standing_doggy", "wall_fuck",
        }
        self.db.max_total_occupants = 2
        self.db.material = "stone"
        self.db.desc = "A solid wall."
    
    def get_slots(self) -> Dict[str, FurnitureSlot]:
        return {
            "against": FurnitureSlot(
                key="against",
                name="back to the wall",
                max_occupants=1,
                positions={
                    OccupantPosition.STANDING,
                    OccupantPosition.SITTING,  # Slid down
                },
                exposed_zones={"front", "groin", "chest", "face"},
                blocked_zones={"back"},
                description="{name} stands with their back to the wall",
            ),
            "facing": FurnitureSlot(
                key="facing",
                name="facing the wall",
                max_occupants=1,
                positions={
                    OccupantPosition.STANDING,
                    OccupantPosition.BENT_OVER,
                },
                exposed_zones={"back", "ass", "groin"},
                blocked_zones={"front", "face"},
                description="{name} faces the wall, hands braced against it",
            ),
        }


class PaddedWall(Wall):
    """A padded wall section, softer impact."""
    
    def at_object_creation(self):
        super().at_object_creation()
        self.db.material = "padded leather"
        self.db.quality = "comfortable"
        self.db.desc = "A wall section covered in padded leather."


class DungeonWall(Wall):
    """
    A dungeon wall with chains and attachment points.
    """
    
    def at_object_creation(self):
        super().at_object_creation()
        self.db.position_tags.add("bondage")
        self.db.position_tags.add("chained")
        self.db.material = "cold stone"
        self.db.desc = (
            "A cold stone wall with iron rings and chains "
            "set into it at various heights."
        )
    
    def get_slots(self) -> Dict[str, FurnitureSlot]:
        slots = super().get_slots()
        slots["chained"] = FurnitureSlot(
            key="chained",
            name="chained to the wall",
            max_occupants=1,
            positions={
                OccupantPosition.BOUND_STANDING,
                OccupantPosition.SUSPENDED,
            },
            is_restraint=True,
            requires_lock=True,
            exposed_zones={"front", "back", "groin", "chest", "ass"},
            description="{name} hangs from chains against the wall",
        )
        return slots


# =============================================================================
# PILLARS
# =============================================================================

class Pillar(Support):
    """
    A pillar or column. Can lean against all sides.
    """
    
    def at_object_creation(self):
        super().at_object_creation()
        self.db.furniture_type = FurnitureType.PILLAR
        self.db.position_tags = {"standing", "against", "pillar"}
        self.db.max_total_occupants = 2  # Both sides
        self.db.material = "stone"
        self.db.desc = "A stone pillar rising from floor to ceiling."
    
    def get_slots(self) -> Dict[str, FurnitureSlot]:
        return {
            "front": FurnitureSlot(
                key="front",
                name="against the pillar (front)",
                max_occupants=1,
                positions={
                    OccupantPosition.STANDING,
                    OccupantPosition.KNEELING,
                },
                exposed_zones={"back", "ass"},
                blocked_zones={"front", "chest"},
                description="{name} leans against the pillar",
            ),
            "back": FurnitureSlot(
                key="back",
                name="against the pillar (back)",
                max_occupants=1,
                positions={
                    OccupantPosition.STANDING,
                    OccupantPosition.KNEELING,
                },
                exposed_zones={"front", "chest", "groin"},
                blocked_zones={"back"},
                description="{name} leans against the other side of the pillar",
            ),
        }


class OrnamentedPillar(Pillar):
    """An ornate, decorated pillar."""
    
    def at_object_creation(self):
        super().at_object_creation()
        self.db.quality = "ornate"
        self.db.material = "carved marble"
        self.db.desc = "An ornate marble pillar with intricate carvings."


class BondagePillar(Pillar):
    """A pillar with attachment points for bondage."""
    
    def at_object_creation(self):
        super().at_object_creation()
        self.db.position_tags.add("bondage")
        self.db.desc = (
            "A stone pillar with iron rings embedded at various heights."
        )
    
    def get_slots(self) -> Dict[str, FurnitureSlot]:
        slots = super().get_slots()
        slots["bound"] = FurnitureSlot(
            key="bound",
            name="bound to the pillar",
            max_occupants=1,
            positions={
                OccupantPosition.BOUND_STANDING,
                OccupantPosition.BOUND_KNEELING,
            },
            is_restraint=True,
            requires_lock=True,
            exposed_zones={"front", "back", "groin", "chest", "ass"},
            description="{name} is bound around the pillar",
        )
        return slots


# =============================================================================
# POSTS
# =============================================================================

class Post(Support):
    """
    A standalone post. Smaller than pillar, often for restraint.
    """
    
    def at_object_creation(self):
        super().at_object_creation()
        self.db.furniture_type = FurnitureType.POST
        self.db.position_tags = {"standing", "post"}
        self.db.max_total_occupants = 1
        self.db.material = "wood"
        self.db.desc = "A sturdy wooden post."
    
    def get_slots(self) -> Dict[str, FurnitureSlot]:
        return {
            "at": FurnitureSlot(
                key="at",
                name="at the post",
                max_occupants=1,
                positions={
                    OccupantPosition.STANDING,
                    OccupantPosition.KNEELING,
                },
                exposed_zones={"back", "ass", "groin"},
                description="{name} stands at the post",
            ),
        }


class WhippingPost(Post):
    """
    A whipping post with wrist restraints at the top.
    """
    
    def at_object_creation(self):
        super().at_object_creation()
        self.db.position_tags = {"standing", "post", "bondage", "punishment"}
        self.db.desc = (
            "A tall wooden post with iron shackles near the top "
            "for binding raised wrists."
        )
    
    def get_slots(self) -> Dict[str, FurnitureSlot]:
        return {
            "bound": FurnitureSlot(
                key="bound",
                name="bound to the whipping post",
                max_occupants=1,
                positions={
                    OccupantPosition.BOUND_STANDING,
                },
                is_restraint=True,
                requires_lock=True,
                exposed_zones={"back", "ass", "sides"},
                blocked_zones={"front", "chest"},  # Against the post
                description="{name} is bound to the whipping post, back exposed",
            ),
        }


class TetherPost(Post):
    """
    A tether post with a ring for leashes/chains.
    """
    
    def at_object_creation(self):
        super().at_object_creation()
        self.db.position_tags = {"standing", "post", "tethered", "leash"}
        self.db.desc = (
            "A short post with an iron ring for tethering."
        )
    
    def get_slots(self) -> Dict[str, FurnitureSlot]:
        return {
            "tethered": FurnitureSlot(
                key="tethered",
                name="tethered to the post",
                max_occupants=1,
                positions={
                    OccupantPosition.STANDING,
                    OccupantPosition.KNEELING,
                    OccupantPosition.SITTING,
                    OccupantPosition.LYING_FRONT,
                },
                is_restraint=True,
                requires_lock=False,  # Leash, not lock
                exposed_zones={"all"},  # Can move around
                description="{name} is tethered to the post by a leash",
            ),
        }


class HitchingPost(Post):
    """A hitching post for tying up mounts (or people)."""
    
    def at_object_creation(self):
        super().at_object_creation()
        self.db.position_tags = {"standing", "post", "tethered", "mount"}
        self.db.desc = "A hitching post for securing mounts."


# =============================================================================
# EXPORTS
# =============================================================================

__all__ = [
    # Base
    "Support",
    
    # Walls
    "Wall",
    "PaddedWall",
    "DungeonWall",
    
    # Pillars
    "Pillar",
    "OrnamentedPillar",
    "BondagePillar",
    
    # Posts
    "Post",
    "WhippingPost",
    "TetherPost",
    "HitchingPost",
]
