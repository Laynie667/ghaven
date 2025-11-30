"""
Furniture - Machines
====================

Mechanical furniture: fucking machines, sybians, milking machines, etc.
"""

from typing import Tuple
from .base import (
    Furniture, FurnitureType, SlotType, RestraintPoint, FurnitureSlot
)
from evennia import AttributeProperty


# =============================================================================
# BASE MACHINE
# =============================================================================

class Machine(Furniture):
    """
    Base class for mechanical furniture.
    
    Machines have:
    - Power state (on/off)
    - Speed/intensity settings
    - Optional automation
    """
    
    is_powered = AttributeProperty(default=False)
    speed = AttributeProperty(default=0)  # 0-10
    max_speed = AttributeProperty(default=10)
    
    def turn_on(self) -> Tuple[bool, str]:
        """Turn machine on."""
        if self.is_powered:
            return False, "Already running."
        self.is_powered = True
        self.speed = 1
        return True, f"The {self.key} hums to life."
    
    def turn_off(self) -> Tuple[bool, str]:
        """Turn machine off."""
        if not self.is_powered:
            return False, "Not running."
        self.is_powered = False
        self.speed = 0
        return True, f"The {self.key} powers down."
    
    def set_speed(self, level: int) -> Tuple[bool, str]:
        """Set machine speed."""
        if not self.is_powered:
            return False, "Turn it on first."
        
        level = max(0, min(self.max_speed, level))
        old_speed = self.speed
        self.speed = level
        
        if level == 0:
            return self.turn_off()
        
        if level > old_speed:
            return True, f"The {self.key} speeds up to level {level}."
        else:
            return True, f"The {self.key} slows to level {level}."
    
    def increase_speed(self) -> Tuple[bool, str]:
        """Increase speed by 1."""
        return self.set_speed(self.speed + 1)
    
    def decrease_speed(self) -> Tuple[bool, str]:
        """Decrease speed by 1."""
        return self.set_speed(self.speed - 1)
    
    def get_speed_desc(self) -> str:
        """Get description of current speed."""
        if not self.is_powered:
            return "off"
        
        if self.speed <= 2:
            return "gentle"
        elif self.speed <= 4:
            return "moderate"
        elif self.speed <= 6:
            return "vigorous"
        elif self.speed <= 8:
            return "intense"
        else:
            return "relentless"


# =============================================================================
# FUCKING MACHINES
# =============================================================================

class FuckingMachine(Machine):
    """
    A mechanical fucking machine with adjustable dildo.
    """
    
    attachment = AttributeProperty(default="standard")  # dildo type
    stroke_length = AttributeProperty(default="medium")  # short, medium, long
    
    def at_object_creation(self):
        self.furniture_type = FurnitureType.MACHINE
        self.size = "medium"
        
        # On all fours receiving
        self.add_slot(FurnitureSlot(
            key="receiving",
            slot_type=SlotType.KNEEL,
            max_occupants=1,
            default_pose="on all fours before the machine",
            allowed_poses=["on all fours", "presenting", "receiving"],
            can_restrain=True,
            restraint_points=[
                RestraintPoint.WRISTS, RestraintPoint.ANKLES,
                RestraintPoint.WAIST
            ],
            exposes=["rear", "genitals"],
            occupied_desc="{name} is positioned before the machine.",
        ))
        
        # Lying back receiving
        self.add_slot(FurnitureSlot(
            key="lying",
            slot_type=SlotType.LIE,
            max_occupants=1,
            default_pose="lying back, legs spread for the machine",
            allowed_poses=["spread", "receiving", "helpless"],
            can_restrain=True,
            restraint_points=[RestraintPoint.WRISTS, RestraintPoint.ANKLES],
            exposes=["front", "genitals"],
            occupied_desc="{name} lies spread before the machine.",
        ))
    
    def get_furniture_desc(self, looker=None) -> str:
        """Include machine status in description."""
        desc = super().get_furniture_desc(looker)
        
        if self.is_powered:
            speed_desc = self.get_speed_desc()
            desc += f"\nThe machine is running at a {speed_desc} pace."
            
            # Describe effect on occupant
            occupants = self.get_occupants()
            if occupants:
                if self.speed <= 3:
                    reaction = "shifts slightly"
                elif self.speed <= 6:
                    reaction = "gasps with each thrust"
                else:
                    reaction = "cries out helplessly"
                desc += f" {occupants[0].key} {reaction}."
        else:
            desc += "\nThe machine is idle."
        
        return desc


class Sybian(Machine):
    """
    A saddle-style vibrating machine.
    """
    
    attachment = AttributeProperty(default="standard")
    vibration_pattern = AttributeProperty(default="steady")  # steady, pulse, wave, random
    
    def at_object_creation(self):
        self.furniture_type = FurnitureType.MACHINE
        self.size = "medium"
        
        self.add_slot(FurnitureSlot(
            key="riding",
            slot_type=SlotType.SIT,
            max_occupants=1,
            default_pose="straddling the sybian",
            allowed_poses=["riding", "grinding", "squirming"],
            can_restrain=True,
            restraint_points=[RestraintPoint.THIGHS, RestraintPoint.WRISTS],
            exposes=["chest", "face"],
            accessible_from=["standing"],
            occupied_desc="{name} straddles the sybian.",
        ))
        
        self.add_slot(FurnitureSlot(
            key="standing",
            slot_type=SlotType.STAND,
            max_occupants=2,
            default_pose="standing near the sybian",
            accessible_from=["riding"],
            occupied_desc="{names} watch.",
        ))
    
    def set_pattern(self, pattern: str) -> Tuple[bool, str]:
        """Set vibration pattern."""
        valid = ["steady", "pulse", "wave", "random", "escalate"]
        if pattern not in valid:
            return False, f"Invalid pattern. Choose: {', '.join(valid)}"
        
        self.vibration_pattern = pattern
        return True, f"Pattern set to {pattern}."
    
    def get_furniture_desc(self, looker=None) -> str:
        desc = super().get_furniture_desc(looker)
        
        if self.is_powered:
            speed_desc = self.get_speed_desc()
            desc += f"\nThe sybian vibrates with {speed_desc} intensity ({self.vibration_pattern} pattern)."
            
            occupants = self.get_occupants()
            if occupants:
                if self.speed <= 3:
                    reaction = "shifts on the saddle"
                elif self.speed <= 6:
                    reaction = "moans and grinds"
                else:
                    reaction = "writhes and cries out"
                desc += f" {occupants[0].key} {reaction}."
        
        return desc


class BreedingMount(Machine):
    """
    A machine designed to simulate being mounted by a large animal.
    """
    
    mount_type = AttributeProperty(default="canine")  # canine, equine, generic
    has_knot = AttributeProperty(default=True)
    knot_inflated = AttributeProperty(default=False)
    
    def at_object_creation(self):
        self.furniture_type = FurnitureType.MACHINE
        self.size = "large"
        
        self.add_slot(FurnitureSlot(
            key="mounted",
            slot_type=SlotType.KNEEL,
            max_occupants=1,
            default_pose="on all fours beneath the breeding mount",
            allowed_poses=["mounted", "bred", "knotted"],
            can_restrain=True,
            restraint_points=[
                RestraintPoint.WRISTS, RestraintPoint.ANKLES,
                RestraintPoint.WAIST
            ],
            exposes=["rear", "genitals", "back"],
            occupied_desc="{name} is positioned beneath the breeding mount.",
        ))
    
    def inflate_knot(self) -> Tuple[bool, str]:
        """Inflate the knot attachment."""
        if not self.has_knot:
            return False, "This mount doesn't have a knot attachment."
        if self.knot_inflated:
            return False, "Already inflated."
        
        self.knot_inflated = True
        occupants = self.get_occupants()
        if occupants:
            return True, f"The knot swells inside {occupants[0].key}, locking them in place!"
        return True, "The knot inflates."
    
    def deflate_knot(self) -> Tuple[bool, str]:
        """Deflate the knot."""
        if not self.knot_inflated:
            return False, "Not inflated."
        
        self.knot_inflated = False
        occupants = self.get_occupants()
        if occupants:
            return True, f"The knot deflates, releasing {occupants[0].key}."
        return True, "The knot deflates."


# =============================================================================
# MILKING MACHINES
# =============================================================================

class MilkingMachine(Machine):
    """
    A machine for extracting milk or other fluids.
    """
    
    suction_strength = AttributeProperty(default=5)  # 1-10
    target_area = AttributeProperty(default="breasts")  # breasts, genitals, both
    
    def at_object_creation(self):
        self.furniture_type = FurnitureType.MACHINE
        self.size = "medium"
        
        self.add_slot(FurnitureSlot(
            key="attached",
            slot_type=SlotType.SIT,
            max_occupants=1,
            default_pose="hooked up to the milking machine",
            allowed_poses=["attached", "milked", "drained"],
            can_restrain=True,
            restraint_points=[RestraintPoint.WRISTS, RestraintPoint.WAIST],
            exposes=["chest", "genitals"],
            accessible_from=["standing"],
            occupied_desc="{name} is attached to the milking machine.",
        ))
        
        self.add_slot(FurnitureSlot(
            key="standing",
            slot_type=SlotType.STAND,
            max_occupants=2,
            default_pose="standing at the controls",
            accessible_from=["attached"],
            occupied_desc="{names} monitor the machine.",
        ))
    
    def set_suction(self, level: int) -> Tuple[bool, str]:
        """Set suction strength."""
        level = max(1, min(10, level))
        self.suction_strength = level
        
        if level <= 3:
            desc = "gentle"
        elif level <= 6:
            desc = "firm"
        else:
            desc = "intense"
        
        return True, f"Suction set to {desc} ({level})."


class BreastPump(Machine):
    """
    A simpler breast pumping station.
    """
    
    def at_object_creation(self):
        self.furniture_type = FurnitureType.MACHINE
        self.size = "small"
        
        self.add_slot(FurnitureSlot(
            key="pumping",
            slot_type=SlotType.SIT,
            max_occupants=1,
            default_pose="seated at the breast pump",
            allowed_poses=["pumping", "leaking"],
            exposes=["chest"],
            occupied_desc="{name} is being pumped.",
        ))


class MilkingStanchion(Machine):
    """
    A stanchion that holds the occupant in place for milking.
    Like for cows, but for... other purposes.
    """
    
    def at_object_creation(self):
        self.furniture_type = FurnitureType.MACHINE
        self.size = "large"
        
        self.add_slot(FurnitureSlot(
            key="locked",
            slot_type=SlotType.STAND,
            max_occupants=1,
            default_pose="locked in the milking stanchion",
            allowed_poses=["locked", "milked", "helpless"],
            can_restrain=True,
            restraint_points=[RestraintPoint.NECK, RestraintPoint.WAIST],
            exposes=["chest", "udders", "rear", "genitals"],
            accessible_from=["standing", "kneeling"],
            occupied_desc="{name} stands locked in the stanchion.",
        ))
        
        self.add_slot(FurnitureSlot(
            key="standing",
            slot_type=SlotType.STAND,
            max_occupants=2,
            default_pose="standing at the stanchion",
            accessible_from=["locked"],
            occupied_desc="{names} attend to the milking.",
        ))
        
        self.add_slot(FurnitureSlot(
            key="kneeling",
            slot_type=SlotType.KNEEL,
            max_occupants=1,
            default_pose="kneeling beneath the stanchion",
            accessible_from=["locked"],
            occupied_desc="{name} kneels beneath, ready to catch.",
        ))


# =============================================================================
# SPECIALTY MACHINES
# =============================================================================

class SpankingMachine(Machine):
    """
    An automated spanking machine.
    """
    
    implement = AttributeProperty(default="paddle")  # paddle, cane, strap, hand
    
    def at_object_creation(self):
        self.furniture_type = FurnitureType.MACHINE
        self.size = "medium"
        
        self.add_slot(FurnitureSlot(
            key="bent_over",
            slot_type=SlotType.BEND,
            max_occupants=1,
            default_pose="bent over before the spanking machine",
            allowed_poses=["bent over", "presented", "receiving"],
            can_restrain=True,
            restraint_points=[RestraintPoint.WRISTS, RestraintPoint.ANKLES],
            exposes=["rear", "back"],
            occupied_desc="{name} presents for the spanking machine.",
        ))
    
    def get_furniture_desc(self, looker=None) -> str:
        desc = super().get_furniture_desc(looker)
        
        if self.is_powered:
            speed_desc = self.get_speed_desc()
            desc += f"\nThe {self.implement} swings at a {speed_desc} tempo."
            
            occupants = self.get_occupants()
            if occupants:
                if self.speed <= 3:
                    reaction = "flinches with each stroke"
                elif self.speed <= 6:
                    reaction = "yelps and squirms"
                else:
                    reaction = "cries out with each relentless impact"
                desc += f" {occupants[0].key} {reaction}."
        
        return desc


class TickleMachine(Machine):
    """
    An automated tickling machine with multiple arms.
    """
    
    def at_object_creation(self):
        self.furniture_type = FurnitureType.MACHINE
        self.size = "large"
        
        self.add_slot(FurnitureSlot(
            key="strapped",
            slot_type=SlotType.LIE,
            max_occupants=1,
            default_pose="strapped into the tickle machine",
            allowed_poses=["strapped", "helpless", "thrashing"],
            can_restrain=True,
            restraint_points=[
                RestraintPoint.WRISTS, RestraintPoint.ANKLES,
                RestraintPoint.WAIST
            ],
            exposes=["all"],
            occupied_desc="{name} is at the mercy of the tickle machine.",
        ))


# =============================================================================
# EXPORTS
# =============================================================================

__all__ = [
    # Base
    "Machine",
    # Fucking machines
    "FuckingMachine",
    "Sybian",
    "BreedingMount",
    # Milking
    "MilkingMachine",
    "BreastPump",
    "MilkingStanchion",
    # Specialty
    "SpankingMachine",
    "TickleMachine",
]
