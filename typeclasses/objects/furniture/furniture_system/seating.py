"""
Furniture - Seating

Seating furniture: chairs, benches, thrones, stools, couches.
These primarily support sitting positions but may allow other uses.

Inheritance:
    Furniture
    └── Seating
        ├── Chair
        ├── Bench
        ├── Throne
        ├── Stool
        └── Couch
"""

from typing import Dict, Set
from .base import (
    Furniture,
    FurnitureType,
    FurnitureSlot,
    OccupantPosition,
)


# =============================================================================
# SEATING BASE
# =============================================================================

class Seating(Furniture):
    """
    Base class for seating furniture.
    
    Seating supports:
    - Sitting positions
    - Lap sitting (rider on seated person)
    - Some sexual positions (cowgirl, lap sex, etc.)
    """
    
    def at_object_creation(self):
        """Set up seating defaults."""
        super().at_object_creation()
        self.db.furniture_type = FurnitureType.CHAIR
        self.db.position_tags = {"sitting", "lap"}
    
    def get_slots(self) -> Dict[str, FurnitureSlot]:
        return {
            "seat": FurnitureSlot(
                key="seat",
                name="seated",
                max_occupants=1,
                positions={
                    OccupantPosition.SITTING,
                },
                exposed_zones={"lap", "groin", "thighs", "chest"},
                description="{name} is sitting here",
            ),
            "lap": FurnitureSlot(
                key="lap",
                name="on lap",
                max_occupants=1,
                positions={
                    OccupantPosition.SITTING,
                    OccupantPosition.STRADDLING,
                },
                exposed_zones={"back", "ass", "groin"},
                description="{name} is sitting on someone's lap",
            ),
        }


# =============================================================================
# CHAIR
# =============================================================================

class Chair(Seating):
    """
    A standard chair. One person sits, another can sit on their lap.
    
    Position support:
    - Sitting
    - Lap sitting
    - Cowgirl/reverse cowgirl (when straddling)
    """
    
    def at_object_creation(self):
        super().at_object_creation()
        self.db.furniture_type = FurnitureType.CHAIR
        self.db.position_tags = {"sitting", "lap", "cowgirl", "reverse_cowgirl"}
        self.db.max_total_occupants = 2
        self.db.desc = "A sturdy wooden chair."


class ArmChair(Chair):
    """
    An armchair with armrests. More comfortable, same functionality.
    """
    
    def at_object_creation(self):
        super().at_object_creation()
        self.db.quality = "comfortable"
        self.db.desc = "A plush armchair with padded armrests."


class DiningChair(Chair):
    """
    A dining chair - simpler, less comfortable.
    """
    
    def at_object_creation(self):
        super().at_object_creation()
        self.db.quality = "simple"
        self.db.position_tags = {"sitting", "lap"}  # Less versatile
        self.db.desc = "A simple wooden dining chair."


# =============================================================================
# BENCH
# =============================================================================

class Bench(Seating):
    """
    A bench. Multiple people can sit side by side.
    
    Position support:
    - Sitting (multiple)
    - Lying (if long enough)
    - Bent over (edge)
    """
    
    def at_object_creation(self):
        super().at_object_creation()
        self.db.furniture_type = FurnitureType.BENCH
        self.db.position_tags = {"sitting", "lying", "bent_over", "lap"}
        self.db.max_total_occupants = 4
        self.db.desc = "A long wooden bench."
    
    def get_slots(self) -> Dict[str, FurnitureSlot]:
        return {
            "seat": FurnitureSlot(
                key="seat",
                name="seated",
                max_occupants=3,
                positions={
                    OccupantPosition.SITTING,
                    OccupantPosition.LYING_BACK,
                    OccupantPosition.LYING_FRONT,
                },
                exposed_zones={"lap", "groin", "thighs", "chest", "back"},
                description="{name} is {position} on the bench",
            ),
            "edge": FurnitureSlot(
                key="edge",
                name="at the edge",
                max_occupants=1,
                positions={
                    OccupantPosition.BENT_OVER,
                    OccupantPosition.KNEELING,
                },
                exposed_zones={"ass", "groin", "back"},
                description="{name} is {position} over the edge of the bench",
            ),
        }


class ParkBench(Bench):
    """An outdoor park bench."""
    
    def at_object_creation(self):
        super().at_object_creation()
        self.db.desc = "A weathered wooden park bench."


class PaddedBench(Bench):
    """A padded bench, more comfortable."""
    
    def at_object_creation(self):
        super().at_object_creation()
        self.db.quality = "comfortable"
        self.db.material = "padded leather"
        self.db.desc = "A bench with plush leather padding."


# =============================================================================
# THRONE
# =============================================================================

class Throne(Seating):
    """
    A throne. Imposing, meant for one person of authority.
    
    Position support:
    - Sitting (elevated)
    - Lap sitting (subservient position)
    - Kneeling before (floor slot)
    """
    
    def at_object_creation(self):
        super().at_object_creation()
        self.db.furniture_type = FurnitureType.THRONE
        self.db.position_tags = {"sitting", "lap", "throne", "worship"}
        self.db.quality = "imposing"
        self.db.material = "carved stone"
        self.db.max_total_occupants = 3
        self.db.desc = "An imposing throne of carved stone, elevated above the floor."
    
    def get_slots(self) -> Dict[str, FurnitureSlot]:
        return {
            "throne": FurnitureSlot(
                key="throne",
                name="enthroned",
                max_occupants=1,
                positions={OccupantPosition.SITTING},
                exposed_zones={"lap", "groin", "thighs", "chest"},
                description="{name} sits upon the throne",
            ),
            "lap": FurnitureSlot(
                key="lap",
                name="on lap",
                max_occupants=1,
                positions={
                    OccupantPosition.SITTING,
                    OccupantPosition.STRADDLING,
                },
                exposed_zones={"back", "ass", "groin"},
                description="{name} sits on the enthroned one's lap",
            ),
            "floor": FurnitureSlot(
                key="floor",
                name="before the throne",
                max_occupants=2,
                positions={
                    OccupantPosition.KNEELING,
                    OccupantPosition.LYING_FRONT,
                },
                exposed_zones={"back", "ass", "head"},
                description="{name} kneels before the throne",
            ),
        }


# =============================================================================
# STOOL
# =============================================================================

class Stool(Seating):
    """
    A simple stool. No back, basic seating.
    """
    
    def at_object_creation(self):
        super().at_object_creation()
        self.db.furniture_type = FurnitureType.CHAIR  # Counts as chair
        self.db.position_tags = {"sitting", "straddling"}
        self.db.max_total_occupants = 1
        self.db.desc = "A simple wooden stool."
    
    def get_slots(self) -> Dict[str, FurnitureSlot]:
        return {
            "seat": FurnitureSlot(
                key="seat",
                name="seated",
                max_occupants=1,
                positions={
                    OccupantPosition.SITTING,
                    OccupantPosition.STRADDLING,
                },
                exposed_zones={"lap", "groin", "thighs", "chest", "back"},
                description="{name} sits on the stool",
            ),
        }


class BarStool(Stool):
    """A tall bar stool."""
    
    def at_object_creation(self):
        super().at_object_creation()
        self.db.desc = "A tall bar stool with a circular seat."


# =============================================================================
# COUCH
# =============================================================================

class Couch(Seating):
    """
    A couch or sofa. Multiple people, lying down possible.
    
    Position support:
    - Sitting (multiple)
    - Lying
    - Cuddling
    - Various sexual positions
    """
    
    def at_object_creation(self):
        super().at_object_creation()
        self.db.furniture_type = FurnitureType.COUCH
        self.db.position_tags = {
            "sitting", "lying", "lap", "cuddling",
            "missionary", "spooning", "cowgirl",
        }
        self.db.quality = "comfortable"
        self.db.material = "upholstered"
        self.db.max_total_occupants = 4
        self.db.desc = "A comfortable upholstered couch."
    
    def get_slots(self) -> Dict[str, FurnitureSlot]:
        return {
            "cushion": FurnitureSlot(
                key="cushion",
                name="on the cushions",
                max_occupants=3,
                positions={
                    OccupantPosition.SITTING,
                    OccupantPosition.LYING_BACK,
                    OccupantPosition.LYING_SIDE,
                },
                exposed_zones={"lap", "groin", "thighs", "chest", "belly"},
                description="{name} is {position} on the couch",
            ),
            "lap": FurnitureSlot(
                key="lap",
                name="on someone's lap",
                max_occupants=1,
                positions={
                    OccupantPosition.SITTING,
                    OccupantPosition.STRADDLING,
                    OccupantPosition.LYING_SIDE,
                },
                exposed_zones={"back", "ass", "groin"},
                description="{name} is cuddled up on someone's lap",
            ),
        }


class Loveseat(Couch):
    """A smaller couch for two."""
    
    def at_object_creation(self):
        super().at_object_creation()
        self.db.max_total_occupants = 2
        self.db.desc = "A cozy loveseat built for two."
    
    def get_slots(self) -> Dict[str, FurnitureSlot]:
        slots = super().get_slots()
        slots["cushion"].max_occupants = 2
        return slots


class Chaise(Couch):
    """A chaise lounge - designed for lying down."""
    
    def at_object_creation(self):
        super().at_object_creation()
        self.db.position_tags = {
            "lying", "reclining", "cuddling",
            "missionary", "spooning",
        }
        self.db.max_total_occupants = 2
        self.db.desc = "An elegant chaise lounge, designed for reclining."
    
    def get_slots(self) -> Dict[str, FurnitureSlot]:
        return {
            "recline": FurnitureSlot(
                key="recline",
                name="reclining",
                max_occupants=1,
                positions={
                    OccupantPosition.LYING_BACK,
                    OccupantPosition.LYING_SIDE,
                    OccupantPosition.SITTING,
                },
                exposed_zones={"chest", "belly", "groin", "thighs"},
                description="{name} reclines on the chaise",
            ),
            "alongside": FurnitureSlot(
                key="alongside",
                name="alongside",
                max_occupants=1,
                positions={
                    OccupantPosition.LYING_SIDE,
                    OccupantPosition.KNEELING,
                },
                exposed_zones={"back", "ass", "groin"},
                description="{name} lies alongside the reclining occupant",
            ),
        }


# =============================================================================
# EXPORTS
# =============================================================================

__all__ = [
    # Base
    "Seating",
    
    # Chairs
    "Chair",
    "ArmChair",
    "DiningChair",
    
    # Benches
    "Bench",
    "ParkBench",
    "PaddedBench",
    
    # Throne
    "Throne",
    
    # Stools
    "Stool",
    "BarStool",
    
    # Couches
    "Couch",
    "Loveseat",
    "Chaise",
]
