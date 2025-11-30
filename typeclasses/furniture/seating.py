"""
Furniture - Seating
===================

Chairs, benches, couches, stools, and other seating.
"""

from .base import (
    Furniture, FurnitureType, SlotType, RestraintPoint, FurnitureSlot
)
from evennia import AttributeProperty


# =============================================================================
# BASIC SEATING
# =============================================================================

class Chair(Furniture):
    """
    A simple chair for one person.
    """
    
    def at_object_creation(self):
        self.furniture_type = FurnitureType.SEATING
        self.size = "small"
        
        self.add_slot(FurnitureSlot(
            key="seat",
            slot_type=SlotType.SIT,
            max_occupants=1,
            default_pose="sitting",
            allowed_poses=["sitting", "lounging", "perched"],
            occupied_desc="{name} is sitting here.",
            empty_desc="",
        ))


class Stool(Furniture):
    """
    A backless stool.
    """
    
    def at_object_creation(self):
        self.furniture_type = FurnitureType.SEATING
        self.size = "small"
        
        self.add_slot(FurnitureSlot(
            key="seat",
            slot_type=SlotType.SIT,
            max_occupants=1,
            default_pose="perched",
            allowed_poses=["perched", "sitting", "straddling"],
            exposes=["back", "rear"],
            occupied_desc="{name} is perched on it.",
        ))


class Bench(Furniture):
    """
    A bench that seats multiple people.
    """
    
    seats = AttributeProperty(default=3)
    
    def at_object_creation(self):
        self.furniture_type = FurnitureType.SEATING
        self.size = "medium"
        
        self.add_slot(FurnitureSlot(
            key="seat",
            slot_type=SlotType.SIT,
            max_occupants=self.seats,
            default_pose="sitting",
            allowed_poses=["sitting", "lounging", "lying"],
            occupied_desc="{names} sitting on the bench.",
        ))


class Couch(Furniture):
    """
    A comfortable couch for sitting or lying.
    """
    
    def at_object_creation(self):
        self.furniture_type = FurnitureType.SEATING
        self.size = "large"
        
        # Main seating
        self.add_slot(FurnitureSlot(
            key="seat",
            slot_type=SlotType.SIT,
            max_occupants=3,
            default_pose="sitting",
            allowed_poses=["sitting", "lounging", "curled up"],
            accessible_from=["lying"],
            occupied_desc="{names} on the couch.",
        ))
        
        # Lying position
        self.add_slot(FurnitureSlot(
            key="lying",
            slot_type=SlotType.LIE,
            max_occupants=1,
            default_pose="lying on the couch",
            allowed_poses=["lying", "sprawled", "curled up"],
            exposes=["front", "back"],
            accessible_from=["seat"],
            occupied_desc="{name} is lying on the couch.",
        ))


class Loveseat(Furniture):
    """
    A small couch for two.
    """
    
    def at_object_creation(self):
        self.furniture_type = FurnitureType.SEATING
        self.size = "medium"
        
        self.add_slot(FurnitureSlot(
            key="seat",
            slot_type=SlotType.SIT,
            max_occupants=2,
            default_pose="sitting close",
            allowed_poses=["sitting", "cuddling", "entwined"],
            occupied_desc="{names} share the loveseat.",
        ))


class Throne(Furniture):
    """
    An imposing throne for one.
    """
    
    def at_object_creation(self):
        self.furniture_type = FurnitureType.SEATING
        self.size = "large"
        self.is_anchored = True
        
        self.add_slot(FurnitureSlot(
            key="seat",
            slot_type=SlotType.SIT,
            max_occupants=1,
            default_pose="seated imperiously",
            allowed_poses=["seated", "lounging", "sprawled"],
            occupied_desc="{name} sits upon the throne.",
            empty_desc="The throne awaits.",
        ))
        
        # Floor position at feet
        self.add_slot(FurnitureSlot(
            key="floor",
            slot_type=SlotType.KNEEL,
            max_occupants=2,
            default_pose="kneeling at the foot of the throne",
            allowed_poses=["kneeling", "prostrate", "sitting"],
            accessible_from=["seat"],
            occupied_desc="{names} at the foot of the throne.",
        ))


class Cushion(Furniture):
    """
    A floor cushion for sitting or kneeling.
    """
    
    def at_object_creation(self):
        self.furniture_type = FurnitureType.SEATING
        self.size = "small"
        self.is_anchored = False
        
        self.add_slot(FurnitureSlot(
            key="cushion",
            slot_type=SlotType.SIT,
            max_occupants=1,
            default_pose="sitting on the cushion",
            allowed_poses=["sitting", "kneeling", "curled up"],
            occupied_desc="{name} on the cushion.",
        ))


class PetBed(Furniture):
    """
    A pet bed - cushion with sides.
    """
    
    def at_object_creation(self):
        self.furniture_type = FurnitureType.SEATING
        self.size = "small"
        self.is_anchored = False
        
        self.add_slot(FurnitureSlot(
            key="bed",
            slot_type=SlotType.LIE,
            max_occupants=2,
            default_pose="curled up in their bed",
            allowed_poses=["curled up", "lying", "sleeping"],
            occupied_desc="{names} in the pet bed.",
            empty_desc="An empty pet bed.",
        ))


# =============================================================================
# BDSM SEATING
# =============================================================================

class SpankingBench(Furniture):
    """
    A padded bench for spanking, with restraint points.
    """
    
    def at_object_creation(self):
        self.furniture_type = FurnitureType.RESTRAINT
        self.size = "medium"
        
        self.add_slot(FurnitureSlot(
            key="bent_over",
            slot_type=SlotType.BEND,
            max_occupants=1,
            default_pose="bent over the spanking bench",
            allowed_poses=["bent over", "draped over"],
            can_restrain=True,
            restraint_points=[RestraintPoint.WRISTS, RestraintPoint.ANKLES],
            exposes=["rear", "genitals", "back"],
            occupied_desc="{name} is bent over the bench.",
        ))
        
        self.add_slot(FurnitureSlot(
            key="standing",
            slot_type=SlotType.STAND,
            max_occupants=1,
            default_pose="standing behind the bench",
            accessible_from=["bent_over"],
            occupied_desc="{name} stands ready.",
        ))


class BreedingBench(Furniture):
    """
    A specialized bench that locks the occupant in breeding position.
    """
    
    def at_object_creation(self):
        self.furniture_type = FurnitureType.RESTRAINT
        self.size = "medium"
        
        self.add_slot(FurnitureSlot(
            key="mounted",
            slot_type=SlotType.BEND,
            max_occupants=1,
            default_pose="locked in the breeding bench",
            allowed_poses=["locked", "presenting", "helpless"],
            can_restrain=True,
            restraint_points=[
                RestraintPoint.WRISTS, RestraintPoint.ANKLES,
                RestraintPoint.WAIST, RestraintPoint.NECK
            ],
            exposes=["rear", "genitals", "chest"],
            occupied_desc="{name} is locked in the breeding bench, exposed and helpless.",
        ))
        
        self.add_slot(FurnitureSlot(
            key="mounting",
            slot_type=SlotType.MOUNT,
            max_occupants=1,
            default_pose="mounted on the bench's occupant",
            accessible_from=["mounted"],
            occupied_desc="{name} is mounting the bench's occupant.",
        ))


class Queening(Furniture):
    """
    A queening stool/throne for face-sitting.
    """
    
    def at_object_creation(self):
        self.furniture_type = FurnitureType.SEATING
        self.size = "medium"
        
        # Bottom position - under the seat
        self.add_slot(FurnitureSlot(
            key="beneath",
            slot_type=SlotType.LIE,
            max_occupants=1,
            default_pose="lying beneath the queening stool",
            allowed_poses=["lying", "restrained"],
            can_restrain=True,
            restraint_points=[RestraintPoint.WRISTS, RestraintPoint.ANKLES],
            accessible_from=["seat"],
            occupied_desc="{name} lies beneath, face upward.",
        ))
        
        # Top position - sitting
        self.add_slot(FurnitureSlot(
            key="seat",
            slot_type=SlotType.SIT,
            max_occupants=1,
            default_pose="seated on the queening stool",
            allowed_poses=["seated", "grinding"],
            accessible_from=["beneath"],
            exposes=["genitals", "rear"],
            occupied_desc="{name} sits enthroned above.",
        ))


class ServingStool(Furniture):
    """
    A low stool that puts the occupant at a convenient height.
    """
    
    def at_object_creation(self):
        self.furniture_type = FurnitureType.SEATING
        self.size = "small"
        
        self.add_slot(FurnitureSlot(
            key="kneeling",
            slot_type=SlotType.KNEEL,
            max_occupants=1,
            default_pose="kneeling on the serving stool",
            allowed_poses=["kneeling", "waiting"],
            exposes=["face", "chest", "genitals"],
            occupied_desc="{name} kneels at a convenient height.",
        ))


class SubmissiveBench(Furniture):
    """
    A bench designed for kneeling worship.
    """
    
    def at_object_creation(self):
        self.furniture_type = FurnitureType.SEATING
        self.size = "medium"
        
        # Kneeling position
        self.add_slot(FurnitureSlot(
            key="kneeling",
            slot_type=SlotType.KNEEL,
            max_occupants=1,
            default_pose="kneeling at the bench",
            allowed_poses=["kneeling", "bent forward", "prostrate"],
            can_restrain=True,
            restraint_points=[RestraintPoint.WRISTS],
            exposes=["face", "back", "rear"],
            occupied_desc="{name} kneels in submission.",
        ))
        
        # Standing position
        self.add_slot(FurnitureSlot(
            key="standing",
            slot_type=SlotType.STAND,
            max_occupants=1,
            default_pose="standing before the bench",
            accessible_from=["kneeling"],
            occupied_desc="{name} stands ready to be served.",
        ))


# =============================================================================
# EXPORTS
# =============================================================================

__all__ = [
    # Basic
    "Chair",
    "Stool",
    "Bench",
    "Couch",
    "Loveseat",
    "Throne",
    "Cushion",
    "PetBed",
    # BDSM
    "SpankingBench",
    "BreedingBench",
    "Queening",
    "ServingStool",
    "SubmissiveBench",
]
