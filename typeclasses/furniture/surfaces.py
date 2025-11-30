"""
Furniture - Surfaces
====================

Tables, desks, counters, altars, and other surfaces.
"""

from .base import (
    Furniture, FurnitureType, SlotType, RestraintPoint, FurnitureSlot
)
from evennia import AttributeProperty


# =============================================================================
# BASIC SURFACES
# =============================================================================

class Table(Furniture):
    """
    A basic table. Can sit at or be bent over.
    """
    
    def at_object_creation(self):
        self.furniture_type = FurnitureType.SURFACE
        self.size = "medium"
        
        # Sitting at table
        self.add_slot(FurnitureSlot(
            key="seated",
            slot_type=SlotType.SIT,
            max_occupants=4,
            default_pose="seated at the table",
            allowed_poses=["seated", "leaning"],
            occupied_desc="{names} at the table.",
        ))
        
        # On the table
        self.add_slot(FurnitureSlot(
            key="surface",
            slot_type=SlotType.SURFACE,
            max_occupants=2,
            default_pose="on the table",
            allowed_poses=["lying", "bent over", "sprawled", "sitting"],
            exposes=["front", "back", "rear"],
            accessible_from=["seated", "standing"],
            occupied_desc="{names} on the table.",
        ))
        
        # Standing at table
        self.add_slot(FurnitureSlot(
            key="standing",
            slot_type=SlotType.STAND,
            max_occupants=2,
            default_pose="standing at the table",
            accessible_from=["surface"],
            occupied_desc="{names} standing at the table.",
        ))


class Desk(Furniture):
    """
    A desk for working... or playing.
    """
    
    def at_object_creation(self):
        self.furniture_type = FurnitureType.SURFACE
        self.size = "medium"
        
        # Behind desk
        self.add_slot(FurnitureSlot(
            key="seated",
            slot_type=SlotType.SIT,
            max_occupants=1,
            default_pose="seated behind the desk",
            allowed_poses=["seated", "working", "lounging"],
            occupied_desc="{name} behind the desk.",
        ))
        
        # Under desk
        self.add_slot(FurnitureSlot(
            key="under",
            slot_type=SlotType.KNEEL,
            max_occupants=1,
            default_pose="hidden under the desk",
            allowed_poses=["kneeling", "crouching"],
            accessible_from=["seated"],
            occupied_desc="{name} hidden beneath the desk.",
        ))
        
        # On desk
        self.add_slot(FurnitureSlot(
            key="surface",
            slot_type=SlotType.SURFACE,
            max_occupants=1,
            default_pose="on the desk",
            allowed_poses=["sitting", "bent over", "lying"],
            exposes=["front", "rear"],
            accessible_from=["seated", "standing"],
            occupied_desc="{name} on the desk.",
        ))
        
        # Standing in front
        self.add_slot(FurnitureSlot(
            key="standing",
            slot_type=SlotType.STAND,
            max_occupants=2,
            default_pose="standing before the desk",
            accessible_from=["surface"],
            occupied_desc="{names} standing before the desk.",
        ))


class Counter(Furniture):
    """
    A counter - higher than a table.
    """
    
    def at_object_creation(self):
        self.furniture_type = FurnitureType.SURFACE
        self.size = "large"
        
        # On counter
        self.add_slot(FurnitureSlot(
            key="surface",
            slot_type=SlotType.SURFACE,
            max_occupants=2,
            default_pose="on the counter",
            allowed_poses=["sitting", "lying", "bent over"],
            exposes=["front", "rear", "legs"],
            accessible_from=["standing"],
            occupied_desc="{names} on the counter.",
        ))
        
        # Behind counter
        self.add_slot(FurnitureSlot(
            key="behind",
            slot_type=SlotType.STAND,
            max_occupants=2,
            default_pose="behind the counter",
            accessible_from=["surface"],
            occupied_desc="{names} behind the counter.",
        ))
        
        # In front
        self.add_slot(FurnitureSlot(
            key="standing",
            slot_type=SlotType.STAND,
            max_occupants=3,
            default_pose="at the counter",
            accessible_from=["surface"],
            occupied_desc="{names} at the counter.",
        ))


class Bar(Furniture):
    """
    A bar for drinks and company.
    """
    
    def at_object_creation(self):
        self.furniture_type = FurnitureType.SURFACE
        self.size = "large"
        self.is_anchored = True
        
        # Bar stools
        self.add_slot(FurnitureSlot(
            key="stool",
            slot_type=SlotType.SIT,
            max_occupants=5,
            default_pose="sitting at the bar",
            allowed_poses=["sitting", "leaning", "slumped"],
            occupied_desc="{names} at the bar.",
        ))
        
        # Behind bar
        self.add_slot(FurnitureSlot(
            key="behind",
            slot_type=SlotType.STAND,
            max_occupants=2,
            default_pose="behind the bar",
            occupied_desc="{names} working behind the bar.",
        ))
        
        # On bar (for the adventurous)
        self.add_slot(FurnitureSlot(
            key="surface",
            slot_type=SlotType.SURFACE,
            max_occupants=1,
            default_pose="on the bar",
            allowed_poses=["dancing", "lying", "crawling"],
            exposes=["all"],
            accessible_from=["stool", "behind"],
            occupied_desc="{name} is making a spectacle on the bar.",
        ))


# =============================================================================
# RITUAL/ALTAR SURFACES
# =============================================================================

class Altar(Furniture):
    """
    A ritual altar for ceremonies... or sacrifices.
    """
    
    def at_object_creation(self):
        self.furniture_type = FurnitureType.SURFACE
        self.size = "large"
        self.is_anchored = True
        
        # On altar
        self.add_slot(FurnitureSlot(
            key="surface",
            slot_type=SlotType.LIE,
            max_occupants=1,
            default_pose="lying on the altar",
            allowed_poses=["lying", "bound", "displayed"],
            can_restrain=True,
            restraint_points=[
                RestraintPoint.WRISTS, RestraintPoint.ANKLES,
                RestraintPoint.WAIST
            ],
            exposes=["front", "genitals", "chest"],
            accessible_from=["standing", "kneeling"],
            occupied_desc="{name} lies upon the altar.",
            empty_desc="The altar awaits an offering.",
        ))
        
        # Kneeling before
        self.add_slot(FurnitureSlot(
            key="kneeling",
            slot_type=SlotType.KNEEL,
            max_occupants=2,
            default_pose="kneeling before the altar",
            accessible_from=["surface"],
            occupied_desc="{names} kneel in supplication.",
        ))
        
        # Standing (officiating)
        self.add_slot(FurnitureSlot(
            key="standing",
            slot_type=SlotType.STAND,
            max_occupants=2,
            default_pose="standing over the altar",
            accessible_from=["surface"],
            occupied_desc="{names} stand ready to perform the ritual.",
        ))


class SacrificialSlab(Furniture):
    """
    A stone slab for dark rituals.
    """
    
    def at_object_creation(self):
        self.furniture_type = FurnitureType.SURFACE
        self.size = "large"
        self.is_anchored = True
        
        self.add_slot(FurnitureSlot(
            key="slab",
            slot_type=SlotType.LIE,
            max_occupants=1,
            default_pose="spread on the slab",
            allowed_poses=["spread", "chained", "helpless"],
            can_restrain=True,
            restraint_points=[
                RestraintPoint.WRISTS, RestraintPoint.ANKLES,
                RestraintPoint.NECK, RestraintPoint.WAIST
            ],
            exposes=["all"],
            occupied_desc="{name} lies helpless on the cold stone.",
            empty_desc="Dark stains mark the ancient stone.",
        ))
        
        self.add_slot(FurnitureSlot(
            key="standing",
            slot_type=SlotType.STAND,
            max_occupants=4,
            default_pose="standing around the slab",
            accessible_from=["slab"],
            occupied_desc="{names} circle the slab.",
        ))


class BreedingAltar(Furniture):
    """
    An altar specifically designed for breeding rituals.
    """
    
    def at_object_creation(self):
        self.furniture_type = FurnitureType.SURFACE
        self.size = "large"
        self.is_anchored = True
        
        # Main position - bent over
        self.add_slot(FurnitureSlot(
            key="offering",
            slot_type=SlotType.BEND,
            max_occupants=1,
            default_pose="bent over the breeding altar",
            allowed_poses=["bent over", "presenting", "receiving"],
            can_restrain=True,
            restraint_points=[
                RestraintPoint.WRISTS, RestraintPoint.ANKLES,
                RestraintPoint.WAIST
            ],
            exposes=["rear", "genitals"],
            accessible_from=["mounting", "kneeling"],
            occupied_desc="{name} presents themselves on the altar.",
        ))
        
        # Mounting position
        self.add_slot(FurnitureSlot(
            key="mounting",
            slot_type=SlotType.MOUNT,
            max_occupants=1,
            default_pose="mounting the altar's occupant",
            accessible_from=["offering"],
            occupied_desc="{name} claims the offering.",
        ))
        
        # Kneeling (oral access)
        self.add_slot(FurnitureSlot(
            key="kneeling",
            slot_type=SlotType.KNEEL,
            max_occupants=1,
            default_pose="kneeling before the altar",
            accessible_from=["offering"],
            occupied_desc="{name} kneels in service.",
        ))


# =============================================================================
# BDSM SURFACES
# =============================================================================

class ExaminationTable(Furniture):
    """
    A medical examination table with stirrups.
    """
    
    def at_object_creation(self):
        self.furniture_type = FurnitureType.SURFACE
        self.size = "medium"
        
        # Main position
        self.add_slot(FurnitureSlot(
            key="patient",
            slot_type=SlotType.LIE,
            max_occupants=1,
            default_pose="lying on the examination table, legs in stirrups",
            allowed_poses=["lying", "spread", "exposed"],
            can_restrain=True,
            restraint_points=[
                RestraintPoint.WRISTS, RestraintPoint.ANKLES,
                RestraintPoint.THIGHS
            ],
            exposes=["genitals", "chest", "front"],
            accessible_from=["examiner"],
            occupied_desc="{name} lies exposed on the table.",
        ))
        
        # Doctor position
        self.add_slot(FurnitureSlot(
            key="examiner",
            slot_type=SlotType.STAND,
            max_occupants=2,
            default_pose="standing at the examination table",
            accessible_from=["patient"],
            occupied_desc="{names} ready to examine.",
        ))


class PilloryTable(Furniture):
    """
    A table with a built-in pillory.
    """
    
    def at_object_creation(self):
        self.furniture_type = FurnitureType.RESTRAINT
        self.size = "medium"
        
        # Bent over with neck/wrists locked
        self.add_slot(FurnitureSlot(
            key="locked",
            slot_type=SlotType.BEND,
            max_occupants=1,
            default_pose="bent over and locked in the pillory",
            allowed_poses=["locked", "helpless", "displayed"],
            can_restrain=True,
            restraint_points=[
                RestraintPoint.NECK, RestraintPoint.WRISTS,
                RestraintPoint.ANKLES
            ],
            exposes=["rear", "genitals", "back", "face"],
            accessible_from=["front", "rear"],
            occupied_desc="{name} is locked in the pillory, bent over and helpless.",
        ))
        
        # Access from front (face)
        self.add_slot(FurnitureSlot(
            key="front",
            slot_type=SlotType.STAND,
            max_occupants=1,
            default_pose="standing before the pillory",
            accessible_from=["locked"],
            occupied_desc="{name} stands at the captive's face.",
        ))
        
        # Access from rear
        self.add_slot(FurnitureSlot(
            key="rear",
            slot_type=SlotType.STAND,
            max_occupants=1,
            default_pose="standing behind the pillory",
            accessible_from=["locked"],
            occupied_desc="{name} stands behind the helpless captive.",
        ))


# =============================================================================
# EXPORTS
# =============================================================================

__all__ = [
    # Basic
    "Table",
    "Desk",
    "Counter",
    "Bar",
    # Ritual
    "Altar",
    "SacrificialSlab",
    "BreedingAltar",
    # BDSM
    "ExaminationTable",
    "PilloryTable",
]
