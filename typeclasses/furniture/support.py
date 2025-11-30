"""
Furniture - Support
===================

Beds, mattresses, cots, and other lying surfaces.
"""

from .base import (
    Furniture, FurnitureType, SlotType, RestraintPoint, FurnitureSlot
)
from evennia import AttributeProperty


# =============================================================================
# BASIC BEDS
# =============================================================================

class Bed(Furniture):
    """
    A standard bed for sleeping... or not sleeping.
    """
    
    size_name = AttributeProperty(default="double")  # single, double, queen, king
    
    def at_object_creation(self):
        self.furniture_type = FurnitureType.SUPPORT
        self.size = "large"
        
        capacity = {"single": 1, "double": 2, "queen": 2, "king": 3}.get(
            self.size_name, 2
        )
        
        # Main lying position
        self.add_slot(FurnitureSlot(
            key="lying",
            slot_type=SlotType.LIE,
            max_occupants=capacity,
            default_pose="lying on the bed",
            allowed_poses=[
                "lying", "sleeping", "sprawled", "curled up",
                "on back", "on stomach", "on side"
            ],
            exposes=["front", "back"],
            accessible_from=["sitting", "kneeling", "standing"],
            occupied_desc="{names} on the bed.",
        ))
        
        # Sitting on edge
        self.add_slot(FurnitureSlot(
            key="sitting",
            slot_type=SlotType.SIT,
            max_occupants=2,
            default_pose="sitting on the edge of the bed",
            allowed_poses=["sitting", "perched"],
            accessible_from=["lying"],
            occupied_desc="{names} sitting on the bed.",
        ))
        
        # Kneeling on bed
        self.add_slot(FurnitureSlot(
            key="kneeling",
            slot_type=SlotType.KNEEL,
            max_occupants=2,
            default_pose="kneeling on the bed",
            allowed_poses=["kneeling", "crouching", "on all fours"],
            accessible_from=["lying"],
            exposes=["rear", "front"],
            occupied_desc="{names} kneeling on the bed.",
        ))


class FourPosterBed(Furniture):
    """
    A four-poster bed with attachment points for restraints.
    """
    
    def at_object_creation(self):
        self.furniture_type = FurnitureType.SUPPORT
        self.size = "large"
        
        # Lying - can be restrained
        self.add_slot(FurnitureSlot(
            key="lying",
            slot_type=SlotType.LIE,
            max_occupants=2,
            default_pose="lying on the four-poster bed",
            allowed_poses=[
                "lying", "spread-eagled", "bound", 
                "on back", "on stomach"
            ],
            can_restrain=True,
            restraint_points=[
                RestraintPoint.WRISTS, RestraintPoint.ANKLES
            ],
            exposes=["front", "back", "genitals"],
            accessible_from=["kneeling", "standing"],
            occupied_desc="{names} on the bed.",
        ))
        
        # Kneeling
        self.add_slot(FurnitureSlot(
            key="kneeling",
            slot_type=SlotType.KNEEL,
            max_occupants=2,
            default_pose="kneeling on the bed",
            accessible_from=["lying"],
            occupied_desc="{names} kneeling.",
        ))
        
        # Standing at edge
        self.add_slot(FurnitureSlot(
            key="standing",
            slot_type=SlotType.STAND,
            max_occupants=2,
            default_pose="standing at the bed's edge",
            accessible_from=["lying"],
            occupied_desc="{names} at the bedside.",
        ))


class Cot(Furniture):
    """
    A simple cot for one.
    """
    
    def at_object_creation(self):
        self.furniture_type = FurnitureType.SUPPORT
        self.size = "small"
        self.is_anchored = False
        
        self.add_slot(FurnitureSlot(
            key="lying",
            slot_type=SlotType.LIE,
            max_occupants=1,
            default_pose="lying on the cot",
            allowed_poses=["lying", "sleeping", "curled up"],
            occupied_desc="{name} on the cot.",
        ))


class Mattress(Furniture):
    """
    Just a mattress on the floor.
    """
    
    def at_object_creation(self):
        self.furniture_type = FurnitureType.SUPPORT
        self.size = "medium"
        self.is_anchored = False
        
        self.add_slot(FurnitureSlot(
            key="lying",
            slot_type=SlotType.LIE,
            max_occupants=3,
            default_pose="on the mattress",
            allowed_poses=[
                "lying", "sprawled", "tangled together",
                "on top", "beneath"
            ],
            exposes=["all"],
            accessible_from=["kneeling"],
            occupied_desc="{names} on the mattress.",
        ))
        
        self.add_slot(FurnitureSlot(
            key="kneeling",
            slot_type=SlotType.KNEEL,
            max_occupants=2,
            default_pose="kneeling on the mattress",
            accessible_from=["lying"],
            occupied_desc="{names} kneeling.",
        ))


class Futon(Furniture):
    """
    A futon - can be set up as couch or bed.
    """
    
    mode = AttributeProperty(default="couch")  # "couch" or "bed"
    
    def at_object_creation(self):
        self.furniture_type = FurnitureType.SUPPORT
        self.size = "medium"
        self._setup_slots()
    
    def _setup_slots(self):
        """Set up slots based on mode."""
        if self.mode == "bed":
            self.add_slot(FurnitureSlot(
                key="lying",
                slot_type=SlotType.LIE,
                max_occupants=2,
                default_pose="lying on the futon",
                allowed_poses=["lying", "sprawled", "sleeping"],
                exposes=["front", "back"],
                occupied_desc="{names} on the futon.",
            ))
        else:
            self.add_slot(FurnitureSlot(
                key="sitting",
                slot_type=SlotType.SIT,
                max_occupants=3,
                default_pose="sitting on the futon",
                allowed_poses=["sitting", "lounging", "curled up"],
                occupied_desc="{names} on the futon.",
            ))
    
    def convert(self) -> str:
        """Convert between bed and couch mode."""
        # Clear occupants first
        for slot in self.get_slots():
            if slot.current_occupants:
                return "Clear the futon first."
        
        self.mode = "bed" if self.mode == "couch" else "couch"
        self._slots_data = []
        self._setup_slots()
        return f"Futon converted to {self.mode} mode."


# =============================================================================
# BDSM BEDS
# =============================================================================

class BondageBed(Furniture):
    """
    A bed specifically designed for bondage with multiple anchor points.
    """
    
    def at_object_creation(self):
        self.furniture_type = FurnitureType.RESTRAINT
        self.size = "large"
        
        # Main position - face up
        self.add_slot(FurnitureSlot(
            key="face_up",
            slot_type=SlotType.LIE,
            max_occupants=1,
            default_pose="lying face up, limbs spread",
            allowed_poses=["spread-eagled", "bound", "helpless"],
            can_restrain=True,
            restraint_points=[
                RestraintPoint.WRISTS, RestraintPoint.ANKLES,
                RestraintPoint.WAIST, RestraintPoint.THIGHS
            ],
            exposes=["front", "genitals", "chest"],
            accessible_from=["kneeling", "standing", "straddling"],
            occupied_desc="{name} lies bound and spread on the bed.",
        ))
        
        # Face down
        self.add_slot(FurnitureSlot(
            key="face_down",
            slot_type=SlotType.LIE,
            max_occupants=1,
            default_pose="lying face down, limbs spread",
            allowed_poses=["spread", "bound", "helpless"],
            can_restrain=True,
            restraint_points=[
                RestraintPoint.WRISTS, RestraintPoint.ANKLES,
                RestraintPoint.WAIST
            ],
            exposes=["back", "rear", "genitals"],
            accessible_from=["kneeling", "standing", "mounting"],
            occupied_desc="{name} lies face down and helpless.",
        ))
        
        # Straddling (on top)
        self.add_slot(FurnitureSlot(
            key="straddling",
            slot_type=SlotType.SIT,
            max_occupants=1,
            default_pose="straddling the bed's occupant",
            accessible_from=["face_up"],
            occupied_desc="{name} straddles the bound figure.",
        ))
        
        # Mounting from behind
        self.add_slot(FurnitureSlot(
            key="mounting",
            slot_type=SlotType.MOUNT,
            max_occupants=1,
            default_pose="mounting the helpless figure",
            accessible_from=["face_down"],
            occupied_desc="{name} mounts from behind.",
        ))
        
        # Kneeling beside
        self.add_slot(FurnitureSlot(
            key="kneeling",
            slot_type=SlotType.KNEEL,
            max_occupants=2,
            default_pose="kneeling beside the bed",
            accessible_from=["face_up", "face_down"],
            occupied_desc="{names} kneel at the bedside.",
        ))
        
        # Standing at edge
        self.add_slot(FurnitureSlot(
            key="standing",
            slot_type=SlotType.STAND,
            max_occupants=2,
            default_pose="standing at the bed's edge",
            accessible_from=["face_up", "face_down"],
            occupied_desc="{names} stand ready.",
        ))


class BreedingPit(Furniture):
    """
    A sunken, padded area for group activities.
    """
    
    def at_object_creation(self):
        self.furniture_type = FurnitureType.SUPPORT
        self.size = "huge"
        self.is_anchored = True
        
        # Main pit area
        self.add_slot(FurnitureSlot(
            key="pit",
            slot_type=SlotType.LIE,
            max_occupants=6,
            default_pose="in the breeding pit",
            allowed_poses=[
                "lying", "tangled", "writhing", "mounted",
                "on all fours", "spread"
            ],
            exposes=["all"],
            occupied_desc="{names} fill the breeding pit.",
        ))
        
        # Edge - watching or waiting
        self.add_slot(FurnitureSlot(
            key="edge",
            slot_type=SlotType.SIT,
            max_occupants=4,
            default_pose="sitting at the pit's edge",
            allowed_poses=["sitting", "watching", "waiting"],
            accessible_from=["pit"],
            occupied_desc="{names} watch from the edge.",
        ))


class KennelCage(Furniture):
    """
    A large cage/kennel for pets.
    """
    
    def at_object_creation(self):
        self.furniture_type = FurnitureType.RESTRAINT
        self.size = "medium"
        self.requires_unlock = True
        
        self.add_slot(FurnitureSlot(
            key="inside",
            slot_type=SlotType.LIE,
            max_occupants=2,
            default_pose="curled up in the kennel",
            allowed_poses=["curled up", "lying", "crouching", "waiting"],
            can_restrain=True,  # Cage can be locked
            restraint_points=[],  # No specific points, cage itself restrains
            exposes=["all"],  # Visible through bars
            occupied_desc="{names} in the kennel.",
            empty_desc="An empty kennel.",
        ))
    
    def lock(self) -> Tuple[bool, str]:
        """Lock the kennel door."""
        if self.is_locked:
            return False, "Already locked."
        self.is_locked = True
        
        # Mark all occupants as restrained
        slots = self.get_slots()
        for slot in slots:
            for dbref in slot.current_occupants:
                if dbref not in slot.restrained_occupants:
                    slot.restrained_occupants.append(dbref)
        self.save_slots(slots)
        
        return True, "You lock the kennel."
    
    def unlock(self) -> Tuple[bool, str]:
        """Unlock the kennel door."""
        if not self.is_locked:
            return False, "Not locked."
        self.is_locked = False
        
        # Unmark all as restrained
        slots = self.get_slots()
        for slot in slots:
            slot.restrained_occupants.clear()
        self.save_slots(slots)
        
        return True, "You unlock the kennel."


# =============================================================================
# SPECIALTY
# =============================================================================

class HayPile(Furniture):
    """
    A pile of hay in a barn or stable.
    """
    
    def at_object_creation(self):
        self.furniture_type = FurnitureType.SUPPORT
        self.size = "large"
        self.is_anchored = False
        
        self.add_slot(FurnitureSlot(
            key="hay",
            slot_type=SlotType.LIE,
            max_occupants=4,
            default_pose="in the hay",
            allowed_poses=[
                "lying", "rolling", "tumbling", "hidden",
                "mounting", "mounted"
            ],
            exposes=["all"],
            occupied_desc="{names} in the hay.",
            empty_desc="A soft pile of hay.",
        ))


class NestingArea(Furniture):
    """
    A soft nesting area for feral creatures.
    """
    
    def at_object_creation(self):
        self.furniture_type = FurnitureType.SUPPORT
        self.size = "medium"
        
        self.add_slot(FurnitureSlot(
            key="nest",
            slot_type=SlotType.LIE,
            max_occupants=3,
            default_pose="curled in the nest",
            allowed_poses=["curled", "sleeping", "nursing", "nesting"],
            occupied_desc="{names} in the nest.",
            empty_desc="A cozy nesting area.",
        ))


# =============================================================================
# EXPORTS
# =============================================================================

__all__ = [
    # Basic
    "Bed",
    "FourPosterBed",
    "Cot",
    "Mattress",
    "Futon",
    # BDSM
    "BondageBed",
    "BreedingPit",
    "KennelCage",
    # Specialty
    "HayPile",
    "NestingArea",
]
