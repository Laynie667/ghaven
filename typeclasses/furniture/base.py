"""
Furniture System - Base Classes
===============================

Base furniture class and core types.

Furniture provides:
- Slots for characters to occupy
- Positions/poses for occupants
- Locking/restraint capabilities
- Integration with room display
"""

from enum import Enum
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass, field

from evennia.objects.objects import DefaultObject
from evennia import AttributeProperty


# =============================================================================
# ENUMS
# =============================================================================

class FurnitureType(Enum):
    """Types of furniture."""
    SEATING = "seating"       # Chairs, benches, couches
    SURFACE = "surface"       # Tables, desks, altars
    SUPPORT = "support"       # Beds, mattresses, cushions
    RESTRAINT = "restraint"   # Stocks, crosses, cages
    MACHINE = "machine"       # Fucking machines, sybian
    STORAGE = "storage"       # Chests, wardrobes
    FIXTURE = "fixture"       # Poles, hooks, rings


class SlotType(Enum):
    """Types of slots on furniture."""
    SIT = "sit"
    LIE = "lie"
    KNEEL = "kneel"
    STAND = "stand"
    BEND = "bend"
    RESTRAIN = "restrain"
    MOUNT = "mount"
    SURFACE = "surface"


class RestraintPoint(Enum):
    """Points where restraints can attach."""
    WRISTS = "wrists"
    ANKLES = "ankles"
    NECK = "neck"
    WAIST = "waist"
    THIGHS = "thighs"
    ARMS = "arms"
    LEGS = "legs"
    HEAD = "head"


# =============================================================================
# SLOT DEFINITION
# =============================================================================

@dataclass
class FurnitureSlot:
    """A slot on furniture that a character can occupy."""
    
    key: str                              # Unique identifier
    slot_type: SlotType                   # Type of slot
    max_occupants: int = 1                # How many can use this slot
    current_occupants: List[str] = field(default_factory=list)  # dbrefs
    
    # Position/pose
    default_pose: str = ""                # Default pose when using
    allowed_poses: List[str] = field(default_factory=list)
    
    # Restraint
    can_restrain: bool = False
    restraint_points: List[RestraintPoint] = field(default_factory=list)
    restrained_occupants: List[str] = field(default_factory=list)  # dbrefs
    
    # Access
    accessible_from: List[str] = field(default_factory=list)  # Other slot keys
    exposes: List[str] = field(default_factory=list)  # Body parts exposed
    
    # Description
    occupied_desc: str = ""               # "{name} is sitting here"
    empty_desc: str = ""                  # "An empty seat"
    
    def is_available(self) -> bool:
        """Check if slot has room."""
        return len(self.current_occupants) < self.max_occupants
    
    def add_occupant(self, dbref: str) -> bool:
        """Add occupant to slot."""
        if not self.is_available():
            return False
        if dbref not in self.current_occupants:
            self.current_occupants.append(dbref)
        return True
    
    def remove_occupant(self, dbref: str) -> bool:
        """Remove occupant from slot."""
        if dbref in self.current_occupants:
            self.current_occupants.remove(dbref)
            if dbref in self.restrained_occupants:
                self.restrained_occupants.remove(dbref)
            return True
        return False
    
    def restrain_occupant(self, dbref: str) -> bool:
        """Restrain an occupant in this slot."""
        if not self.can_restrain:
            return False
        if dbref not in self.current_occupants:
            return False
        if dbref not in self.restrained_occupants:
            self.restrained_occupants.append(dbref)
        return True
    
    def release_occupant(self, dbref: str) -> bool:
        """Release a restrained occupant."""
        if dbref in self.restrained_occupants:
            self.restrained_occupants.remove(dbref)
            return True
        return False
    
    def is_restrained(self, dbref: str) -> bool:
        """Check if occupant is restrained."""
        return dbref in self.restrained_occupants
    
    def to_dict(self) -> dict:
        """Convert to dictionary for storage."""
        return {
            "key": self.key,
            "slot_type": self.slot_type.value,
            "max_occupants": self.max_occupants,
            "current_occupants": self.current_occupants.copy(),
            "default_pose": self.default_pose,
            "allowed_poses": self.allowed_poses.copy(),
            "can_restrain": self.can_restrain,
            "restraint_points": [rp.value for rp in self.restraint_points],
            "restrained_occupants": self.restrained_occupants.copy(),
            "accessible_from": self.accessible_from.copy(),
            "exposes": self.exposes.copy(),
            "occupied_desc": self.occupied_desc,
            "empty_desc": self.empty_desc,
        }
    
    @classmethod
    def from_dict(cls, data: dict) -> "FurnitureSlot":
        """Create from dictionary."""
        return cls(
            key=data["key"],
            slot_type=SlotType(data["slot_type"]),
            max_occupants=data.get("max_occupants", 1),
            current_occupants=data.get("current_occupants", []),
            default_pose=data.get("default_pose", ""),
            allowed_poses=data.get("allowed_poses", []),
            can_restrain=data.get("can_restrain", False),
            restraint_points=[RestraintPoint(rp) for rp in data.get("restraint_points", [])],
            restrained_occupants=data.get("restrained_occupants", []),
            accessible_from=data.get("accessible_from", []),
            exposes=data.get("exposes", []),
            occupied_desc=data.get("occupied_desc", ""),
            empty_desc=data.get("empty_desc", ""),
        )


# =============================================================================
# BASE FURNITURE CLASS
# =============================================================================

class Furniture(DefaultObject):
    """
    Base furniture class.
    
    All furniture has:
    - One or more slots for occupants
    - A furniture type
    - Optional restraint capabilities
    """
    
    # -------------------------------------------------------------------------
    # ATTRIBUTES
    # -------------------------------------------------------------------------
    
    furniture_type = AttributeProperty(default=FurnitureType.SEATING)
    short_desc = AttributeProperty(default="")
    
    # Slots stored as list of dicts, converted to FurnitureSlot on access
    _slots_data = AttributeProperty(default=list)
    
    # Flags
    is_anchored = AttributeProperty(default=True)  # Can't be picked up
    requires_unlock = AttributeProperty(default=False)
    is_locked = AttributeProperty(default=False)
    
    # Size
    size = AttributeProperty(default="medium")  # tiny, small, medium, large, huge
    
    # -------------------------------------------------------------------------
    # SLOT MANAGEMENT
    # -------------------------------------------------------------------------
    
    def get_slots(self) -> List[FurnitureSlot]:
        """Get all slots as FurnitureSlot objects."""
        if not self._slots_data:
            return []
        return [FurnitureSlot.from_dict(d) for d in self._slots_data]
    
    def save_slots(self, slots: List[FurnitureSlot]):
        """Save slots back to storage."""
        self._slots_data = [s.to_dict() for s in slots]
    
    def get_slot(self, key: str) -> Optional[FurnitureSlot]:
        """Get a specific slot by key."""
        for slot in self.get_slots():
            if slot.key == key:
                return slot
        return None
    
    def add_slot(self, slot: FurnitureSlot):
        """Add a new slot."""
        slots = self.get_slots()
        # Remove existing with same key
        slots = [s for s in slots if s.key != slot.key]
        slots.append(slot)
        self.save_slots(slots)
    
    def has_available_slot(self, slot_type: SlotType = None) -> bool:
        """Check if any slot is available."""
        for slot in self.get_slots():
            if slot_type and slot.slot_type != slot_type:
                continue
            if slot.is_available():
                return True
        return False
    
    def get_available_slots(self, slot_type: SlotType = None) -> List[FurnitureSlot]:
        """Get all available slots."""
        available = []
        for slot in self.get_slots():
            if slot_type and slot.slot_type != slot_type:
                continue
            if slot.is_available():
                available.append(slot)
        return available
    
    # -------------------------------------------------------------------------
    # OCCUPANT MANAGEMENT
    # -------------------------------------------------------------------------
    
    def add_occupant(self, character, slot_key: str = None) -> Tuple[bool, str]:
        """
        Add a character to this furniture.
        
        Args:
            character: The character to add
            slot_key: Specific slot, or None for first available
            
        Returns:
            (success, message)
        """
        slots = self.get_slots()
        target_slot = None
        
        if slot_key:
            for slot in slots:
                if slot.key == slot_key:
                    target_slot = slot
                    break
            if not target_slot:
                return False, f"No slot named '{slot_key}' on this furniture."
        else:
            # Find first available
            for slot in slots:
                if slot.is_available():
                    target_slot = slot
                    break
        
        if not target_slot:
            return False, "No available slots."
        
        if not target_slot.is_available():
            return False, "That slot is occupied."
        
        # Add to slot
        dbref = character.dbref
        target_slot.add_occupant(dbref)
        self.save_slots(slots)
        
        # Update character
        if hasattr(character, 'using_furniture_dbref'):
            character.using_furniture_dbref = self.dbref
            character.furniture_slot = target_slot.key
        
        # Set pose if available
        if target_slot.default_pose and hasattr(character, 'pose'):
            character.pose = target_slot.default_pose
        
        return True, f"You use the {self.key}."
    
    def remove_occupant(self, character, force: bool = False) -> Tuple[bool, str]:
        """
        Remove a character from this furniture.
        
        Args:
            character: The character to remove
            force: If True, ignore restraints
            
        Returns:
            (success, message)
        """
        dbref = character.dbref
        slots = self.get_slots()
        
        for slot in slots:
            if dbref in slot.current_occupants:
                # Check restraints
                if slot.is_restrained(dbref) and not force:
                    return False, "You're restrained and can't get up!"
                
                slot.remove_occupant(dbref)
                self.save_slots(slots)
                
                # Update character
                if hasattr(character, 'using_furniture_dbref'):
                    character.using_furniture_dbref = None
                    character.furniture_slot = None
                    character.furniture_locked = False
                
                return True, f"You get off the {self.key}."
        
        return False, "You're not on this furniture."
    
    def get_occupants(self) -> List:
        """Get all occupants across all slots."""
        from evennia.utils.search import search_object
        
        occupants = []
        for slot in self.get_slots():
            for dbref in slot.current_occupants:
                try:
                    results = search_object(dbref)
                    if results:
                        occupants.append(results[0])
                except Exception:
                    pass
        return occupants
    
    def get_occupant_slot(self, character) -> Optional[FurnitureSlot]:
        """Get the slot a character is in."""
        dbref = character.dbref
        for slot in self.get_slots():
            if dbref in slot.current_occupants:
                return slot
        return None
    
    # -------------------------------------------------------------------------
    # RESTRAINT MANAGEMENT
    # -------------------------------------------------------------------------
    
    def can_restrain(self) -> bool:
        """Check if any slot can restrain."""
        return any(slot.can_restrain for slot in self.get_slots())
    
    def restrain_occupant(self, character, slot_key: str = None) -> Tuple[bool, str]:
        """
        Restrain an occupant.
        
        Args:
            character: The character to restrain
            slot_key: Specific slot, or None to find them
            
        Returns:
            (success, message)
        """
        dbref = character.dbref
        slots = self.get_slots()
        target_slot = None
        
        if slot_key:
            for slot in slots:
                if slot.key == slot_key:
                    target_slot = slot
                    break
        else:
            # Find slot they're in
            for slot in slots:
                if dbref in slot.current_occupants:
                    target_slot = slot
                    break
        
        if not target_slot:
            return False, "They're not on this furniture."
        
        if not target_slot.can_restrain:
            return False, "This position can't restrain anyone."
        
        if dbref not in target_slot.current_occupants:
            return False, "They're not in that position."
        
        if target_slot.is_restrained(dbref):
            return False, "They're already restrained."
        
        target_slot.restrain_occupant(dbref)
        self.save_slots(slots)
        
        # Update character
        if hasattr(character, 'furniture_locked'):
            character.furniture_locked = True
        
        return True, f"You restrain {character.key} on the {self.key}."
    
    def release_occupant(self, character) -> Tuple[bool, str]:
        """Release a restrained occupant."""
        dbref = character.dbref
        slots = self.get_slots()
        
        for slot in slots:
            if slot.is_restrained(dbref):
                slot.release_occupant(dbref)
                self.save_slots(slots)
                
                if hasattr(character, 'furniture_locked'):
                    character.furniture_locked = False
                
                return True, f"You release {character.key} from the {self.key}."
        
        return False, "They're not restrained."
    
    def is_occupant_restrained(self, character) -> bool:
        """Check if an occupant is restrained."""
        dbref = character.dbref
        for slot in self.get_slots():
            if slot.is_restrained(dbref):
                return True
        return False
    
    # -------------------------------------------------------------------------
    # DISPLAY
    # -------------------------------------------------------------------------
    
    def get_display_name(self, looker=None, **kwargs):
        """Get name for display."""
        return self.key
    
    def get_furniture_desc(self, looker=None) -> str:
        """Get description including occupants."""
        lines = [self.db.desc or f"A {self.key}."]
        
        for slot in self.get_slots():
            if slot.current_occupants:
                occupant_names = []
                for dbref in slot.current_occupants:
                    try:
                        from evennia.utils.search import search_object
                        results = search_object(dbref)
                        if results:
                            name = results[0].key
                            if slot.is_restrained(dbref):
                                name += " (restrained)"
                            occupant_names.append(name)
                    except Exception:
                        pass
                
                if occupant_names:
                    if slot.occupied_desc:
                        desc = slot.occupied_desc.format(
                            name=", ".join(occupant_names),
                            names=", ".join(occupant_names)
                        )
                        lines.append(desc)
                    else:
                        lines.append(f"Occupied by: {', '.join(occupant_names)}")
            elif slot.empty_desc:
                lines.append(slot.empty_desc)
        
        return "\n".join(lines)
    
    def return_appearance(self, looker, **kwargs):
        """Return the appearance of this furniture."""
        return self.get_furniture_desc(looker)
    
    # -------------------------------------------------------------------------
    # HOOKS
    # -------------------------------------------------------------------------
    
    def at_object_creation(self):
        """Called when furniture is first created."""
        # Override in subclasses to set up default slots
        pass
    
    def at_before_get(self, getter, **kwargs):
        """Called before being picked up."""
        if self.is_anchored:
            getter.msg(f"The {self.key} is anchored in place.")
            return False
        
        # Check for occupants
        if self.get_occupants():
            getter.msg(f"The {self.key} is occupied!")
            return False
        
        return True


# =============================================================================
# EXPORTS
# =============================================================================

__all__ = [
    "FurnitureType",
    "SlotType",
    "RestraintPoint",
    "FurnitureSlot",
    "Furniture",
]
