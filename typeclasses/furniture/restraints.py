"""
Furniture - Restraints
======================

Stocks, crosses, cages, racks, and other bondage furniture.
"""

from .base import (
    Furniture, FurnitureType, SlotType, RestraintPoint, FurnitureSlot
)
from evennia import AttributeProperty


# =============================================================================
# STANDING RESTRAINTS
# =============================================================================

class StandingStocks(Furniture):
    """
    Standing stocks that lock neck and wrists.
    """
    
    def at_object_creation(self):
        self.furniture_type = FurnitureType.RESTRAINT
        self.size = "medium"
        self.is_anchored = True
        
        self.add_slot(FurnitureSlot(
            key="locked",
            slot_type=SlotType.STAND,
            max_occupants=1,
            default_pose="locked in the stocks",
            allowed_poses=["locked", "helpless", "displayed"],
            can_restrain=True,
            restraint_points=[RestraintPoint.NECK, RestraintPoint.WRISTS],
            exposes=["front", "back", "rear", "genitals"],
            accessible_from=["front", "rear"],
            occupied_desc="{name} stands locked in the stocks, bent forward.",
        ))
        
        self.add_slot(FurnitureSlot(
            key="front",
            slot_type=SlotType.STAND,
            max_occupants=1,
            default_pose="standing before the stocks",
            accessible_from=["locked"],
            occupied_desc="{name} stands at the captive's face.",
        ))
        
        self.add_slot(FurnitureSlot(
            key="rear",
            slot_type=SlotType.STAND,
            max_occupants=1,
            default_pose="standing behind the stocks",
            accessible_from=["locked"],
            occupied_desc="{name} stands behind the helpless captive.",
        ))


class Pillory(Furniture):
    """
    A pillory - stocks on a post.
    """
    
    def at_object_creation(self):
        self.furniture_type = FurnitureType.RESTRAINT
        self.size = "medium"
        self.is_anchored = True
        
        self.add_slot(FurnitureSlot(
            key="locked",
            slot_type=SlotType.STAND,
            max_occupants=1,
            default_pose="locked in the pillory",
            allowed_poses=["locked", "displayed", "humiliated"],
            can_restrain=True,
            restraint_points=[RestraintPoint.NECK, RestraintPoint.WRISTS],
            exposes=["face", "front", "back", "rear"],
            accessible_from=["standing"],
            occupied_desc="{name} stands on display in the pillory.",
        ))
        
        self.add_slot(FurnitureSlot(
            key="standing",
            slot_type=SlotType.STAND,
            max_occupants=3,
            default_pose="standing near the pillory",
            accessible_from=["locked"],
            occupied_desc="{names} observe the prisoner.",
        ))


class StAndrewsCross(Furniture):
    """
    An X-shaped cross for spread-eagle bondage.
    """
    
    def at_object_creation(self):
        self.furniture_type = FurnitureType.RESTRAINT
        self.size = "large"
        self.is_anchored = True
        
        # Facing cross (back exposed)
        self.add_slot(FurnitureSlot(
            key="facing",
            slot_type=SlotType.STAND,
            max_occupants=1,
            default_pose="spread-eagled on the cross, facing it",
            allowed_poses=["spread", "bound", "helpless"],
            can_restrain=True,
            restraint_points=[RestraintPoint.WRISTS, RestraintPoint.ANKLES],
            exposes=["back", "rear", "legs"],
            accessible_from=["behind"],
            occupied_desc="{name} is spread on the cross, back exposed.",
        ))
        
        # Facing out (front exposed)
        self.add_slot(FurnitureSlot(
            key="displayed",
            slot_type=SlotType.STAND,
            max_occupants=1,
            default_pose="spread-eagled on the cross, facing outward",
            allowed_poses=["spread", "displayed", "helpless"],
            can_restrain=True,
            restraint_points=[RestraintPoint.WRISTS, RestraintPoint.ANKLES],
            exposes=["front", "chest", "genitals", "face"],
            accessible_from=["standing"],
            occupied_desc="{name} is displayed spread-eagled on the cross.",
        ))
        
        # Access
        self.add_slot(FurnitureSlot(
            key="behind",
            slot_type=SlotType.STAND,
            max_occupants=2,
            default_pose="standing behind the cross",
            accessible_from=["facing"],
            occupied_desc="{names} behind the cross.",
        ))
        
        self.add_slot(FurnitureSlot(
            key="standing",
            slot_type=SlotType.STAND,
            max_occupants=2,
            default_pose="standing before the cross",
            accessible_from=["displayed"],
            occupied_desc="{names} before the displayed figure.",
        ))


class WhippingPost(Furniture):
    """
    A post for tying victims for punishment.
    """
    
    def at_object_creation(self):
        self.furniture_type = FurnitureType.RESTRAINT
        self.size = "small"
        self.is_anchored = True
        
        self.add_slot(FurnitureSlot(
            key="bound",
            slot_type=SlotType.STAND,
            max_occupants=1,
            default_pose="tied to the post",
            allowed_poses=["tied", "hanging", "sagging"],
            can_restrain=True,
            restraint_points=[RestraintPoint.WRISTS, RestraintPoint.ARMS],
            exposes=["back", "rear", "sides"],
            accessible_from=["standing"],
            occupied_desc="{name} hangs bound from the post.",
        ))
        
        self.add_slot(FurnitureSlot(
            key="standing",
            slot_type=SlotType.STAND,
            max_occupants=2,
            default_pose="standing ready",
            accessible_from=["bound"],
            occupied_desc="{names} stand ready.",
        ))


class SuspensionFrame(Furniture):
    """
    A frame for suspension bondage.
    """
    
    def at_object_creation(self):
        self.furniture_type = FurnitureType.RESTRAINT
        self.size = "large"
        self.is_anchored = True
        
        # Full suspension
        self.add_slot(FurnitureSlot(
            key="suspended",
            slot_type=SlotType.RESTRAIN,
            max_occupants=1,
            default_pose="suspended in the frame",
            allowed_poses=["suspended", "hanging", "floating"],
            can_restrain=True,
            restraint_points=[
                RestraintPoint.WRISTS, RestraintPoint.ANKLES,
                RestraintPoint.WAIST, RestraintPoint.THIGHS
            ],
            exposes=["all"],
            accessible_from=["standing"],
            occupied_desc="{name} hangs suspended in the frame.",
        ))
        
        # Partial suspension (feet touching)
        self.add_slot(FurnitureSlot(
            key="partial",
            slot_type=SlotType.STAND,
            max_occupants=1,
            default_pose="partially suspended, toes touching ground",
            allowed_poses=["straining", "stretched", "helpless"],
            can_restrain=True,
            restraint_points=[RestraintPoint.WRISTS, RestraintPoint.ARMS],
            exposes=["all"],
            accessible_from=["standing"],
            occupied_desc="{name} strains on tiptoe.",
        ))
        
        self.add_slot(FurnitureSlot(
            key="standing",
            slot_type=SlotType.STAND,
            max_occupants=3,
            default_pose="standing in the frame area",
            accessible_from=["suspended", "partial"],
            occupied_desc="{names} approach the bound figure.",
        ))


# =============================================================================
# FLOOR/KNEELING RESTRAINTS
# =============================================================================

class KneelingStocks(Furniture):
    """
    Stocks designed for a kneeling position.
    """
    
    def at_object_creation(self):
        self.furniture_type = FurnitureType.RESTRAINT
        self.size = "medium"
        self.is_anchored = True
        
        self.add_slot(FurnitureSlot(
            key="locked",
            slot_type=SlotType.KNEEL,
            max_occupants=1,
            default_pose="locked in the kneeling stocks",
            allowed_poses=["kneeling", "bent", "helpless"],
            can_restrain=True,
            restraint_points=[
                RestraintPoint.NECK, RestraintPoint.WRISTS,
                RestraintPoint.ANKLES
            ],
            exposes=["face", "rear", "back"],
            accessible_from=["standing_front", "standing_rear"],
            occupied_desc="{name} kneels helpless in the stocks.",
        ))
        
        self.add_slot(FurnitureSlot(
            key="standing_front",
            slot_type=SlotType.STAND,
            max_occupants=1,
            default_pose="standing before the kneeling stocks",
            accessible_from=["locked"],
            occupied_desc="{name} stands at the captive's face.",
        ))
        
        self.add_slot(FurnitureSlot(
            key="standing_rear",
            slot_type=SlotType.STAND,
            max_occupants=1,
            default_pose="standing behind the kneeling stocks",
            accessible_from=["locked"],
            occupied_desc="{name} stands behind the helpless captive.",
        ))


class DoggyStocks(Furniture):
    """
    Stocks that force an all-fours position.
    """
    
    def at_object_creation(self):
        self.furniture_type = FurnitureType.RESTRAINT
        self.size = "medium"
        self.is_anchored = True
        
        self.add_slot(FurnitureSlot(
            key="locked",
            slot_type=SlotType.KNEEL,
            max_occupants=1,
            default_pose="locked on all fours",
            allowed_poses=["on all fours", "presenting", "helpless"],
            can_restrain=True,
            restraint_points=[
                RestraintPoint.NECK, RestraintPoint.WRISTS,
                RestraintPoint.ANKLES
            ],
            exposes=["rear", "genitals", "face"],
            accessible_from=["front", "rear", "mounting"],
            occupied_desc="{name} is locked on all fours, presenting.",
        ))
        
        self.add_slot(FurnitureSlot(
            key="mounting",
            slot_type=SlotType.MOUNT,
            max_occupants=1,
            default_pose="mounting the restrained figure",
            accessible_from=["locked"],
            occupied_desc="{name} mounts the helpless captive.",
        ))
        
        self.add_slot(FurnitureSlot(
            key="front",
            slot_type=SlotType.STAND,
            max_occupants=1,
            default_pose="standing at the captive's face",
            accessible_from=["locked"],
            occupied_desc="{name} stands before the helpless mouth.",
        ))
        
        self.add_slot(FurnitureSlot(
            key="rear",
            slot_type=SlotType.STAND,
            max_occupants=1,
            default_pose="standing behind",
            accessible_from=["locked"],
            occupied_desc="{name} observes from behind.",
        ))


# =============================================================================
# CAGES
# =============================================================================

class Cage(Furniture):
    """
    A standing cage for confinement.
    """
    
    def at_object_creation(self):
        self.furniture_type = FurnitureType.RESTRAINT
        self.size = "medium"
        self.is_anchored = True
        self.requires_unlock = True
        
        self.add_slot(FurnitureSlot(
            key="inside",
            slot_type=SlotType.STAND,
            max_occupants=1,
            default_pose="standing in the cage",
            allowed_poses=["standing", "crouching", "pressed against bars"],
            can_restrain=True,
            exposes=["all"],  # Visible through bars
            occupied_desc="{name} stands caged.",
            empty_desc="An empty cage.",
        ))
    
    def lock(self) -> tuple:
        if self.is_locked:
            return False, "Already locked."
        self.is_locked = True
        slots = self.get_slots()
        for slot in slots:
            for dbref in slot.current_occupants:
                if dbref not in slot.restrained_occupants:
                    slot.restrained_occupants.append(dbref)
        self.save_slots(slots)
        return True, "The cage locks shut."
    
    def unlock(self) -> tuple:
        if not self.is_locked:
            return False, "Not locked."
        self.is_locked = False
        slots = self.get_slots()
        for slot in slots:
            slot.restrained_occupants.clear()
        self.save_slots(slots)
        return True, "The cage unlocks."


class HangingCage(Furniture):
    """
    A cage suspended from the ceiling.
    """
    
    def at_object_creation(self):
        self.furniture_type = FurnitureType.RESTRAINT
        self.size = "medium"
        self.is_anchored = True
        self.requires_unlock = True
        
        self.add_slot(FurnitureSlot(
            key="inside",
            slot_type=SlotType.SIT,
            max_occupants=1,
            default_pose="huddled in the hanging cage",
            allowed_poses=["huddled", "curled", "swinging"],
            can_restrain=True,
            exposes=["all"],
            occupied_desc="{name} hangs caged above.",
            empty_desc="An empty cage sways overhead.",
        ))
    
    def lock(self) -> tuple:
        if self.is_locked:
            return False, "Already locked."
        self.is_locked = True
        slots = self.get_slots()
        for slot in slots:
            for dbref in slot.current_occupants:
                if dbref not in slot.restrained_occupants:
                    slot.restrained_occupants.append(dbref)
        self.save_slots(slots)
        return True, "The cage locks."
    
    def unlock(self) -> tuple:
        if not self.is_locked:
            return False, "Not locked."
        self.is_locked = False
        slots = self.get_slots()
        for slot in slots:
            slot.restrained_occupants.clear()
        self.save_slots(slots)
        return True, "The cage unlocks."


# =============================================================================
# RACKS
# =============================================================================

class StretchingRack(Furniture):
    """
    A medieval stretching rack.
    """
    
    def at_object_creation(self):
        self.furniture_type = FurnitureType.RESTRAINT
        self.size = "large"
        self.is_anchored = True
        
        self.add_slot(FurnitureSlot(
            key="stretched",
            slot_type=SlotType.LIE,
            max_occupants=1,
            default_pose="stretched on the rack",
            allowed_poses=["stretched", "strained", "helpless"],
            can_restrain=True,
            restraint_points=[RestraintPoint.WRISTS, RestraintPoint.ANKLES],
            exposes=["all"],
            accessible_from=["standing"],
            occupied_desc="{name} lies stretched on the rack.",
        ))
        
        self.add_slot(FurnitureSlot(
            key="standing",
            slot_type=SlotType.STAND,
            max_occupants=2,
            default_pose="standing at the rack",
            accessible_from=["stretched"],
            occupied_desc="{names} attend the rack.",
        ))
    
    def tighten(self) -> str:
        """Tighten the rack."""
        occupants = self.get_occupants()
        if not occupants:
            return "The rack is empty."
        return f"You turn the wheel. {occupants[0].key} groans as the rack stretches tighter."
    
    def loosen(self) -> str:
        """Loosen the rack."""
        occupants = self.get_occupants()
        if not occupants:
            return "The rack is empty."
        return f"You release some tension. {occupants[0].key} gasps with relief."


class WoodenHorse(Furniture):
    """
    A wooden horse / Spanish donkey.
    """
    
    def at_object_creation(self):
        self.furniture_type = FurnitureType.RESTRAINT
        self.size = "medium"
        self.is_anchored = True
        
        self.add_slot(FurnitureSlot(
            key="riding",
            slot_type=SlotType.SIT,
            max_occupants=1,
            default_pose="straddling the wooden horse",
            allowed_poses=["straddling", "suffering", "bound"],
            can_restrain=True,
            restraint_points=[RestraintPoint.WRISTS, RestraintPoint.ANKLES],
            exposes=["genitals", "chest", "back"],
            accessible_from=["standing"],
            occupied_desc="{name} straddles the cruel wooden edge.",
        ))
        
        self.add_slot(FurnitureSlot(
            key="standing",
            slot_type=SlotType.STAND,
            max_occupants=2,
            default_pose="standing at the horse",
            accessible_from=["riding"],
            occupied_desc="{names} observe the suffering.",
        ))


# =============================================================================
# EXPORTS
# =============================================================================

__all__ = [
    # Standing
    "StandingStocks",
    "Pillory",
    "StAndrewsCross",
    "WhippingPost",
    "SuspensionFrame",
    # Kneeling
    "KneelingStocks",
    "DoggyStocks",
    # Cages
    "Cage",
    "HangingCage",
    # Racks
    "StretchingRack",
    "WoodenHorse",
]
