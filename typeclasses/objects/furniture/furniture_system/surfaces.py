"""
Furniture - Surfaces

Surface furniture: beds, tables, altars, counters, desks.
These provide horizontal surfaces for lying, bending over, etc.

Inheritance:
    Furniture
    └── Surface
        ├── Bed
        │   ├── SingleBed
        │   ├── DoubleBed
        │   ├── KingBed
        │   ├── Futon
        │   └── Hammock
        ├── Table
        │   ├── DiningTable
        │   ├── CoffeeTable
        │   └── PoolTable
        ├── Altar
        │   ├── StoneAltar
        │   └── SacrificialAltar
        ├── Counter
        │   ├── KitchenCounter
        │   └── BarCounter
        └── Desk
            ├── WritingDesk
            └── ExecutiveDesk
"""

from typing import Dict, Set
from .base import (
    Furniture,
    FurnitureType,
    FurnitureSlot,
    OccupantPosition,
)


# =============================================================================
# SURFACE BASE
# =============================================================================

class Surface(Furniture):
    """
    Base class for surface furniture.
    
    Surfaces support:
    - Lying positions
    - Bent over positions (edge)
    - Sexual positions requiring horizontal surface
    """
    
    def at_object_creation(self):
        super().at_object_creation()
        self.db.furniture_type = FurnitureType.TABLE
        self.db.position_tags = {"lying", "bent_over", "surface"}
        self.db.height = "waist"  # waist, low, high
    
    def get_slots(self) -> Dict[str, FurnitureSlot]:
        return {
            "surface": FurnitureSlot(
                key="surface",
                name="on the surface",
                max_occupants=1,
                positions={
                    OccupantPosition.LYING_BACK,
                    OccupantPosition.LYING_FRONT,
                    OccupantPosition.SITTING,
                },
                exposed_zones={"chest", "belly", "groin", "thighs", "back", "ass"},
                description="{name} is {position} on the surface",
            ),
        }


# =============================================================================
# BEDS
# =============================================================================

class Bed(Surface):
    """
    A bed. The primary furniture for lying positions.
    
    Position support:
    - All lying positions
    - Missionary, doggy, cowgirl, etc.
    - Cuddling, spooning
    """
    
    def at_object_creation(self):
        super().at_object_creation()
        self.db.furniture_type = FurnitureType.BED
        self.db.position_tags = {
            "lying", "bed", "missionary", "doggy", "cowgirl",
            "reverse_cowgirl", "spooning", "cuddling", "69",
            "prone_bone", "mating_press",
        }
        self.db.quality = "comfortable"
        self.db.material = "wood and fabric"
        self.db.max_total_occupants = 2
        self.db.height = "low"
        self.db.desc = "A comfortable bed with soft sheets."
    
    def get_slots(self) -> Dict[str, FurnitureSlot]:
        return {
            "mattress": FurnitureSlot(
                key="mattress",
                name="on the bed",
                max_occupants=2,
                positions={
                    OccupantPosition.LYING_BACK,
                    OccupantPosition.LYING_FRONT,
                    OccupantPosition.LYING_SIDE,
                    OccupantPosition.SITTING,
                    OccupantPosition.KNEELING,
                },
                exposed_zones={
                    "chest", "belly", "groin", "thighs",
                    "back", "ass", "face",
                },
                description="{name} is {position} on the bed",
            ),
            "edge": FurnitureSlot(
                key="edge",
                name="at the edge",
                max_occupants=1,
                positions={
                    OccupantPosition.LYING_BACK,
                    OccupantPosition.BENT_OVER,
                    OccupantPosition.KNEELING,
                },
                exposed_zones={"groin", "ass", "thighs"},
                description="{name} is positioned at the edge of the bed",
            ),
        }


class SingleBed(Bed):
    """A single/twin bed. Fits one comfortably, two tightly."""
    
    def at_object_creation(self):
        super().at_object_creation()
        self.db.max_total_occupants = 2
        self.db.desc = "A narrow single bed."
    
    def get_slots(self) -> Dict[str, FurnitureSlot]:
        slots = super().get_slots()
        slots["mattress"].max_occupants = 2
        return slots


class DoubleBed(Bed):
    """A double/full bed. Comfortable for two."""
    
    def at_object_creation(self):
        super().at_object_creation()
        self.db.max_total_occupants = 3
        self.db.desc = "A comfortable double bed."
    
    def get_slots(self) -> Dict[str, FurnitureSlot]:
        slots = super().get_slots()
        slots["mattress"].max_occupants = 3
        return slots


class KingBed(Bed):
    """A king-size bed. Room for activities."""
    
    def at_object_creation(self):
        super().at_object_creation()
        self.db.max_total_occupants = 4
        self.db.quality = "luxurious"
        self.db.desc = "A luxurious king-size bed with silk sheets."
    
    def get_slots(self) -> Dict[str, FurnitureSlot]:
        slots = super().get_slots()
        slots["mattress"].max_occupants = 4
        return slots


class FourPosterBed(KingBed):
    """
    A four-poster bed with posts at each corner.
    Can be used for light bondage (tying to posts).
    """
    
    def at_object_creation(self):
        super().at_object_creation()
        self.db.position_tags.update({"bondage", "tied", "spread"})
        self.db.desc = "An elegant four-poster bed with carved wooden posts at each corner."
    
    def get_slots(self) -> Dict[str, FurnitureSlot]:
        slots = super().get_slots()
        slots["tied"] = FurnitureSlot(
            key="tied",
            name="tied to the posts",
            max_occupants=1,
            positions={
                OccupantPosition.LYING_BACK,
                OccupantPosition.LYING_FRONT,
            },
            is_restraint=True,
            requires_lock=False,  # Ropes, not locks
            exposed_zones={
                "chest", "belly", "groin", "thighs",
                "back", "ass", "arms", "legs",
            },
            description="{name} is tied spread-eagle to the bed posts",
        )
        return slots


class Futon(Bed):
    """A futon - converts between couch and bed."""
    
    def at_object_creation(self):
        super().at_object_creation()
        self.db.max_total_occupants = 2
        self.db.quality = "simple"
        self.db.desc = "A futon that can fold into a couch."
        self.db.is_folded = False
    
    def fold(self) -> str:
        """Convert between bed and couch mode."""
        self.db.is_folded = not self.db.is_folded
        if self.db.is_folded:
            self.db.furniture_type = FurnitureType.COUCH
            return "The futon folds up into a couch."
        else:
            self.db.furniture_type = FurnitureType.BED
            return "The futon unfolds into a bed."


class Hammock(Bed):
    """
    A hammock. Suspended, swaying, tricky to use.
    """
    
    def at_object_creation(self):
        super().at_object_creation()
        self.db.furniture_type = FurnitureType.SWING  # Similar mechanics
        self.db.position_tags = {"lying", "swinging", "cuddling"}
        self.db.max_total_occupants = 2
        self.db.quality = "relaxing"
        self.db.material = "woven rope"
        self.db.desc = "A woven rope hammock strung between two points."
    
    def get_slots(self) -> Dict[str, FurnitureSlot]:
        return {
            "hammock": FurnitureSlot(
                key="hammock",
                name="in the hammock",
                max_occupants=2,
                positions={
                    OccupantPosition.LYING_BACK,
                    OccupantPosition.LYING_SIDE,
                },
                exposed_zones={"chest", "belly", "groin", "back"},
                description="{name} sways gently in the hammock",
            ),
        }


# =============================================================================
# TABLES
# =============================================================================

class Table(Surface):
    """
    A table. Horizontal surface at waist height.
    
    Position support:
    - Bent over (primary)
    - Lying on
    - Under table (oral, worship)
    """
    
    def at_object_creation(self):
        super().at_object_creation()
        self.db.furniture_type = FurnitureType.TABLE
        self.db.position_tags = {
            "bent_over", "lying", "table",
            "doggy", "prone_bone",
        }
        self.db.max_total_occupants = 2
        self.db.height = "waist"
        self.db.desc = "A sturdy wooden table."
    
    def get_slots(self) -> Dict[str, FurnitureSlot]:
        return {
            "surface": FurnitureSlot(
                key="surface",
                name="on the table",
                max_occupants=1,
                positions={
                    OccupantPosition.LYING_BACK,
                    OccupantPosition.LYING_FRONT,
                    OccupantPosition.BENT_OVER,
                    OccupantPosition.SITTING,
                },
                exposed_zones={
                    "chest", "belly", "groin", "thighs",
                    "back", "ass",
                },
                description="{name} is {position} on the table",
            ),
            "under": FurnitureSlot(
                key="under",
                name="under the table",
                max_occupants=1,
                positions={
                    OccupantPosition.KNEELING,
                    OccupantPosition.LYING_BACK,
                },
                exposed_zones={"face", "chest"},
                blocked_zones={"back"},  # Table above
                description="{name} is hidden under the table",
            ),
        }


class DiningTable(Table):
    """A dining table. Larger, multiple people around it."""
    
    def at_object_creation(self):
        super().at_object_creation()
        self.db.max_total_occupants = 3
        self.db.desc = "A large dining table with chairs around it."


class CoffeeTable(Table):
    """A low coffee table."""
    
    def at_object_creation(self):
        super().at_object_creation()
        self.db.height = "low"
        self.db.position_tags = {"bent_over", "kneeling", "low"}
        self.db.desc = "A low coffee table."


class PoolTable(Table):
    """A pool/billiard table. Sturdy, felt surface."""
    
    def at_object_creation(self):
        super().at_object_creation()
        self.db.quality = "sturdy"
        self.db.material = "slate and felt"
        self.db.position_tags.add("pool")
        self.db.desc = "A pool table with green felt surface."


# =============================================================================
# ALTARS
# =============================================================================

class Altar(Surface):
    """
    An altar. Ritual surface, often stone.
    
    Position support:
    - Lying (sacrifice/ritual positions)
    - Bound (ritual restraint)
    - Worship (kneeling before)
    """
    
    def at_object_creation(self):
        super().at_object_creation()
        self.db.furniture_type = FurnitureType.ALTAR
        self.db.position_tags = {
            "lying", "altar", "ritual", "sacrifice",
            "worship", "bondage",
        }
        self.db.quality = "sacred"
        self.db.material = "carved stone"
        self.db.max_total_occupants = 2
        self.db.height = "waist"
        self.db.desc = "A carved stone altar, cold and imposing."
    
    def get_slots(self) -> Dict[str, FurnitureSlot]:
        return {
            "surface": FurnitureSlot(
                key="surface",
                name="upon the altar",
                max_occupants=1,
                positions={
                    OccupantPosition.LYING_BACK,
                    OccupantPosition.LYING_FRONT,
                    OccupantPosition.BOUND_BENT,
                },
                is_restraint=True,  # Can be bound here
                exposed_zones={
                    "chest", "belly", "groin", "thighs",
                    "back", "ass", "face",
                },
                description="{name} lies upon the altar",
            ),
            "before": FurnitureSlot(
                key="before",
                name="before the altar",
                max_occupants=2,
                positions={
                    OccupantPosition.KNEELING,
                    OccupantPosition.STANDING,
                },
                exposed_zones={"face", "chest"},
                description="{name} kneels in worship before the altar",
            ),
        }


class SacrificialAltar(Altar):
    """
    A sacrificial altar with restraint points.
    """
    
    def at_object_creation(self):
        super().at_object_creation()
        self.db.position_tags.add("bound")
        self.db.desc = (
            "A dark stone altar with iron rings set into its surface "
            "for binding sacrifices."
        )
    
    def get_slots(self) -> Dict[str, FurnitureSlot]:
        slots = super().get_slots()
        slots["surface"].requires_lock = True
        slots["surface"].description = "{name} is bound upon the sacrificial altar"
        return slots


# =============================================================================
# COUNTERS
# =============================================================================

class Counter(Surface):
    """
    A counter. Waist-height surface, typically in kitchen/bar.
    """
    
    def at_object_creation(self):
        super().at_object_creation()
        self.db.furniture_type = FurnitureType.COUNTER
        self.db.position_tags = {"bent_over", "sitting", "counter"}
        self.db.max_total_occupants = 2
        self.db.height = "waist"
        self.db.desc = "A sturdy counter."
    
    def get_slots(self) -> Dict[str, FurnitureSlot]:
        return {
            "surface": FurnitureSlot(
                key="surface",
                name="on the counter",
                max_occupants=1,
                positions={
                    OccupantPosition.SITTING,
                    OccupantPosition.BENT_OVER,
                    OccupantPosition.LYING_BACK,
                },
                exposed_zones={"groin", "thighs", "ass", "chest"},
                description="{name} is {position} on the counter",
            ),
            "behind": FurnitureSlot(
                key="behind",
                name="behind the counter",
                max_occupants=1,
                positions={
                    OccupantPosition.STANDING,
                    OccupantPosition.KNEELING,
                },
                exposed_zones={"face", "chest"},
                description="{name} stands behind the counter",
            ),
        }


class KitchenCounter(Counter):
    """A kitchen counter."""
    
    def at_object_creation(self):
        super().at_object_creation()
        self.db.material = "granite"
        self.db.desc = "A granite kitchen counter."


class BarCounter(Counter):
    """A bar counter with stools."""
    
    def at_object_creation(self):
        super().at_object_creation()
        self.db.material = "polished wood"
        self.db.desc = "A polished wooden bar counter."


# =============================================================================
# DESKS
# =============================================================================

class Desk(Surface):
    """
    A desk. Work surface, but also bent-over potential.
    """
    
    def at_object_creation(self):
        super().at_object_creation()
        self.db.furniture_type = FurnitureType.DESK
        self.db.position_tags = {"bent_over", "desk", "sitting"}
        self.db.max_total_occupants = 2
        self.db.height = "waist"
        self.db.desc = "A wooden desk."
    
    def get_slots(self) -> Dict[str, FurnitureSlot]:
        return {
            "surface": FurnitureSlot(
                key="surface",
                name="on the desk",
                max_occupants=1,
                positions={
                    OccupantPosition.BENT_OVER,
                    OccupantPosition.SITTING,
                    OccupantPosition.LYING_BACK,
                },
                exposed_zones={"ass", "groin", "back", "thighs"},
                description="{name} is {position} over the desk",
            ),
            "chair": FurnitureSlot(
                key="chair",
                name="at the desk",
                max_occupants=1,
                positions={
                    OccupantPosition.SITTING,
                },
                exposed_zones={"lap", "chest"},
                description="{name} sits at the desk",
            ),
            "under": FurnitureSlot(
                key="under",
                name="under the desk",
                max_occupants=1,
                positions={
                    OccupantPosition.KNEELING,
                },
                exposed_zones={"face"},
                blocked_zones={"back"},
                description="{name} is hidden under the desk",
            ),
        }


class WritingDesk(Desk):
    """A simple writing desk."""
    
    def at_object_creation(self):
        super().at_object_creation()
        self.db.quality = "simple"
        self.db.desc = "A simple writing desk with a leather top."


class ExecutiveDesk(Desk):
    """A large, imposing executive desk."""
    
    def at_object_creation(self):
        super().at_object_creation()
        self.db.quality = "imposing"
        self.db.material = "mahogany"
        self.db.desc = "A massive mahogany executive desk, polished to a shine."


# =============================================================================
# EXPORTS
# =============================================================================

__all__ = [
    # Base
    "Surface",
    
    # Beds
    "Bed",
    "SingleBed",
    "DoubleBed",
    "KingBed",
    "FourPosterBed",
    "Futon",
    "Hammock",
    
    # Tables
    "Table",
    "DiningTable",
    "CoffeeTable",
    "PoolTable",
    
    # Altars
    "Altar",
    "SacrificialAltar",
    
    # Counters
    "Counter",
    "KitchenCounter",
    "BarCounter",
    
    # Desks
    "Desk",
    "WritingDesk",
    "ExecutiveDesk",
]
