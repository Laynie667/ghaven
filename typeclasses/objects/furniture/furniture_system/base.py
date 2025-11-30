"""
Furniture System - Base Classes

Furniture objects that characters can interact with, sit on, lie on,
be restrained to, or use for various activities.

INHERITANCE HIERARCHY:
    Furniture (base)
    ├── Seating
    │   ├── Chair
    │   ├── Bench
    │   ├── Throne
    │   ├── Stool
    │   └── Couch
    ├── Surface
    │   ├── Bed
    │   ├── Table
    │   ├── Altar
    │   ├── Counter
    │   └── Desk
    ├── Support
    │   ├── Wall (lean against)
    │   ├── Pillar
    │   └── Post
    ├── Restraint
    │   ├── Stocks
    │   ├── Pillory
    │   ├── Cross
    │   ├── Frame
    │   ├── Cage
    │   └── BreedingBench
    └── Machine
        ├── SybiandMount
        ├── MilkingStation
        └── FuckingMachine

POSITION INTEGRATION:
    Positions can require furniture via FurnitureType enum.
    Furniture provides that type plus any additional position tags.
    
USAGE:
    from typeclasses.objects.furniture import Bed, Stocks
    
    bed = create_object(Bed, key="four-poster bed", location=room)
    bed.db.quality = "luxurious"
    
    # Character uses furniture
    bed.use(character)  # Places character on/in furniture
    bed.release(character)  # Removes character
    
    # Check if position works here
    if bed.supports_position("missionary"):
        ...
"""

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Set, Any, Tuple, TYPE_CHECKING
from enum import Enum, auto

# Evennia imports
try:
    from evennia.objects.objects import DefaultObject
    from evennia import AttributeProperty
    HAS_EVENNIA = True
except ImportError:
    HAS_EVENNIA = False
    class DefaultObject:
        pass
    def AttributeProperty(default=None):
        return default

if TYPE_CHECKING:
    from evennia.objects.objects import DefaultCharacter


# =============================================================================
# ENUMS
# =============================================================================

class FurnitureType(Enum):
    """
    Types of furniture for position requirements.
    Matches the FurnitureType in positions/core.py
    """
    NONE = "none"
    BED = "bed"
    CHAIR = "chair"
    BENCH = "bench"
    TABLE = "table"
    WALL = "wall"
    FLOOR = "floor"
    STOCKS = "stocks"
    PILLORY = "pillory"
    CROSS = "cross"
    FRAME = "frame"
    CAGE = "cage"
    BREEDING_BENCH = "breeding_bench"
    THRONE = "throne"
    ALTAR = "altar"
    COUCH = "couch"
    DESK = "desk"
    COUNTER = "counter"
    POST = "post"
    PILLAR = "pillar"
    SYBIAN = "sybian"
    MILKING_STATION = "milking_station"
    FUCKING_MACHINE = "fucking_machine"
    SWING = "swing"
    SLING = "sling"
    HORSE = "horse"  # Spanking horse / sawhorse


class FurnitureState(Enum):
    """Current state of the furniture."""
    AVAILABLE = "available"       # No one using it
    OCCUPIED = "occupied"         # Someone on/in it
    LOCKED = "locked"             # Restraint furniture - locked
    BROKEN = "broken"             # Damaged, can't be used
    RESERVED = "reserved"         # Reserved but not occupied


class OccupantPosition(Enum):
    """How an occupant is positioned on the furniture."""
    SITTING = "sitting"
    LYING_BACK = "lying_back"
    LYING_FRONT = "lying_front"
    LYING_SIDE = "lying_side"
    KNEELING = "kneeling"
    STANDING = "standing"
    BENT_OVER = "bent_over"
    BOUND_STANDING = "bound_standing"
    BOUND_KNEELING = "bound_kneeling"
    BOUND_BENT = "bound_bent"
    SUSPENDED = "suspended"
    STRADDLING = "straddling"
    MOUNTED = "mounted"           # On a machine/sybian


# =============================================================================
# SLOT DEFINITIONS
# =============================================================================

@dataclass
class FurnitureSlot:
    """
    A slot on furniture that a character can occupy.
    
    Some furniture has multiple slots:
    - Bed: multiple lying positions
    - Stocks: one locked position, one standing/kneeling in front
    - Cage: one inside, observers outside
    """
    key: str                                    # Slot identifier
    name: str                                   # Display name
    max_occupants: int = 1                      # How many can use this slot
    positions: Set[OccupantPosition] = field(default_factory=set)  # Valid positions
    is_restraint: bool = False                  # Does this slot restrain?
    requires_lock: bool = False                 # Needs to be locked?
    exposed_zones: Set[str] = field(default_factory=set)  # Body zones exposed
    blocked_zones: Set[str] = field(default_factory=set)  # Body zones blocked
    description: str = ""                       # How occupant appears


@dataclass
class Occupant:
    """Tracks a character occupying furniture."""
    character_dbref: str
    character_name: str
    slot_key: str
    position: OccupantPosition
    is_locked: bool = False
    is_voluntary: bool = True                   # Chose to be here
    lock_dbref: Optional[str] = None            # What's locking them
    entered_at: float = 0.0                     # Timestamp


# =============================================================================
# BASE FURNITURE CLASS
# =============================================================================

class Furniture(DefaultObject):
    """
    Base class for all furniture objects.
    
    Furniture provides:
    - Slots for characters to occupy
    - Position support (which positions work here)
    - State tracking (available, occupied, locked, broken)
    - Description integration (how occupants appear)
    
    Subclasses define specific behavior for different furniture types.
    """
    
    # -------------------------------------------------------------------------
    # ATTRIBUTES
    # -------------------------------------------------------------------------
    
    # Core identity
    furniture_type = AttributeProperty(default=FurnitureType.NONE)
    quality = AttributeProperty(default="standard")  # shabby, standard, fine, luxurious
    material = AttributeProperty(default="wood")
    
    # State
    state = AttributeProperty(default=FurnitureState.AVAILABLE)
    condition = AttributeProperty(default=100)  # 0-100, breaks at 0
    
    # Occupants: {slot_key: [Occupant, ...]}
    occupants = AttributeProperty(default=dict)
    
    # Position support
    position_tags = AttributeProperty(default=set)  # Tags this furniture provides
    
    # Capacity
    max_total_occupants = AttributeProperty(default=1)
    
    # -------------------------------------------------------------------------
    # SLOT DEFINITIONS (Override in subclasses)
    # -------------------------------------------------------------------------
    
    def get_slots(self) -> Dict[str, FurnitureSlot]:
        """
        Get slot definitions for this furniture.
        Override in subclasses to define specific slots.
        """
        return {
            "default": FurnitureSlot(
                key="default",
                name="on the furniture",
                max_occupants=1,
                positions={OccupantPosition.SITTING},
            )
        }
    
    # -------------------------------------------------------------------------
    # TYPE AND POSITION SUPPORT
    # -------------------------------------------------------------------------
    
    def get_furniture_type(self) -> FurnitureType:
        """Get the furniture type for position compatibility."""
        return self.furniture_type
    
    def get_position_tags(self) -> Set[str]:
        """Get all position tags this furniture provides."""
        tags = set(self.position_tags) if self.position_tags else set()
        # Add type-based tags
        ftype = self.get_furniture_type()
        if ftype != FurnitureType.NONE:
            tags.add(ftype.value)
        return tags
    
    def supports_position(self, position_key: str) -> bool:
        """
        Check if this furniture supports a given position.
        
        This is a basic check - the position system does the full
        compatibility check including structure requirements.
        """
        # Would need to import positions to do full check
        # For now, just check if we have the right type
        return True  # Let position system handle it
    
    def supports_furniture_type(self, ftype: FurnitureType) -> bool:
        """Check if this furniture matches a required type."""
        return self.get_furniture_type() == ftype
    
    # -------------------------------------------------------------------------
    # OCCUPANCY
    # -------------------------------------------------------------------------
    
    def is_available(self) -> bool:
        """Check if furniture has any available slots."""
        if self.state in (FurnitureState.BROKEN,):
            return False
        total = sum(len(occs) for occs in self.occupants.values()) if self.occupants else 0
        return total < self.max_total_occupants
    
    def get_available_slots(self) -> List[str]:
        """Get list of slot keys with space available."""
        available = []
        slots = self.get_slots()
        current = self.occupants or {}
        
        for slot_key, slot_def in slots.items():
            current_count = len(current.get(slot_key, []))
            if current_count < slot_def.max_occupants:
                available.append(slot_key)
        
        return available
    
    def get_occupants(self, slot_key: str = None) -> List[Occupant]:
        """
        Get occupants, optionally filtered by slot.
        """
        if not self.occupants:
            return []
        
        if slot_key:
            return self.occupants.get(slot_key, [])
        
        # All occupants
        all_occs = []
        for occs in self.occupants.values():
            all_occs.extend(occs)
        return all_occs
    
    def get_occupant_by_dbref(self, dbref: str) -> Optional[Occupant]:
        """Find an occupant by their character dbref."""
        for occs in (self.occupants or {}).values():
            for occ in occs:
                if occ.character_dbref == dbref:
                    return occ
        return None
    
    def is_occupied_by(self, character: "DefaultCharacter") -> bool:
        """Check if a specific character is on this furniture."""
        return self.get_occupant_by_dbref(character.dbref) is not None
    
    # -------------------------------------------------------------------------
    # USE / RELEASE
    # -------------------------------------------------------------------------
    
    def use(
        self,
        character: "DefaultCharacter",
        slot_key: str = None,
        position: OccupantPosition = None,
        voluntary: bool = True
    ) -> Tuple[bool, str]:
        """
        Have a character use this furniture.
        
        Args:
            character: The character using the furniture
            slot_key: Which slot to occupy (default: first available)
            position: How to position them (default: slot's first position)
            voluntary: Whether they chose this (vs forced)
            
        Returns:
            (success, message)
        """
        # Check state
        if self.state == FurnitureState.BROKEN:
            return False, f"The {self.key} is broken."
        
        # Already on it?
        if self.is_occupied_by(character):
            return False, f"You're already on the {self.key}."
        
        # Get slots
        slots = self.get_slots()
        
        # Find slot
        if slot_key:
            if slot_key not in slots:
                return False, f"The {self.key} doesn't have a '{slot_key}' position."
            slot = slots[slot_key]
        else:
            # First available
            available = self.get_available_slots()
            if not available:
                return False, f"The {self.key} is fully occupied."
            slot_key = available[0]
            slot = slots[slot_key]
        
        # Check slot capacity
        current = self.occupants or {}
        if slot_key not in current:
            current[slot_key] = []
        
        if len(current[slot_key]) >= slot.max_occupants:
            return False, f"That position on the {self.key} is taken."
        
        # Determine position
        if position is None:
            position = list(slot.positions)[0] if slot.positions else OccupantPosition.SITTING
        elif position not in slot.positions:
            return False, f"You can't {position.value} in that position."
        
        # Create occupant
        import time
        occupant = Occupant(
            character_dbref=character.dbref,
            character_name=character.key,
            slot_key=slot_key,
            position=position,
            is_voluntary=voluntary,
            entered_at=time.time(),
        )
        
        current[slot_key].append(occupant)
        self.occupants = current
        
        # Update state
        if not self.is_available():
            self.state = FurnitureState.OCCUPIED
        
        # Link character to furniture
        character.db.on_furniture = self.dbref
        character.db.furniture_slot = slot_key
        
        return True, self._get_use_message(character, slot, position)
    
    def release(
        self,
        character: "DefaultCharacter",
        force: bool = False
    ) -> Tuple[bool, str]:
        """
        Remove a character from this furniture.
        
        Args:
            character: The character to release
            force: Override locks (for admin/breakout)
            
        Returns:
            (success, message)
        """
        occupant = self.get_occupant_by_dbref(character.dbref)
        if not occupant:
            return False, f"You're not on the {self.key}."
        
        # Check if locked
        if occupant.is_locked and not force:
            return False, f"You're locked in place on the {self.key}."
        
        # Remove from slot
        current = self.occupants or {}
        if occupant.slot_key in current:
            current[occupant.slot_key] = [
                o for o in current[occupant.slot_key]
                if o.character_dbref != character.dbref
            ]
            if not current[occupant.slot_key]:
                del current[occupant.slot_key]
        
        self.occupants = current
        
        # Update state
        if not self.get_occupants():
            self.state = FurnitureState.AVAILABLE
        
        # Unlink character
        character.db.on_furniture = None
        character.db.furniture_slot = None
        
        return True, self._get_release_message(character)
    
    # -------------------------------------------------------------------------
    # LOCKING (for restraint furniture)
    # -------------------------------------------------------------------------
    
    def lock_occupant(
        self,
        character: "DefaultCharacter",
        lock_dbref: str = None
    ) -> Tuple[bool, str]:
        """Lock an occupant in place."""
        occupant = self.get_occupant_by_dbref(character.dbref)
        if not occupant:
            return False, f"{character.key} is not on the {self.key}."
        
        slot = self.get_slots().get(occupant.slot_key)
        if not slot or not slot.is_restraint:
            return False, f"The {self.key} can't lock someone in that position."
        
        occupant.is_locked = True
        occupant.lock_dbref = lock_dbref
        
        # Update stored
        current = self.occupants or {}
        for i, occ in enumerate(current.get(occupant.slot_key, [])):
            if occ.character_dbref == character.dbref:
                current[occupant.slot_key][i] = occupant
                break
        self.occupants = current
        self.state = FurnitureState.LOCKED
        
        return True, f"You lock {character.key} in place on the {self.key}."
    
    def unlock_occupant(
        self,
        character: "DefaultCharacter",
        key_dbref: str = None
    ) -> Tuple[bool, str]:
        """Unlock an occupant."""
        occupant = self.get_occupant_by_dbref(character.dbref)
        if not occupant:
            return False, f"{character.key} is not on the {self.key}."
        
        if not occupant.is_locked:
            return False, f"{character.key} isn't locked."
        
        # TODO: Check if key_dbref matches lock_dbref requirements
        
        occupant.is_locked = False
        occupant.lock_dbref = None
        
        # Update stored
        current = self.occupants or {}
        for i, occ in enumerate(current.get(occupant.slot_key, [])):
            if occ.character_dbref == character.dbref:
                current[occupant.slot_key][i] = occupant
                break
        self.occupants = current
        
        # Update state if no one locked
        any_locked = any(
            occ.is_locked
            for occs in current.values()
            for occ in occs
        )
        if not any_locked:
            self.state = FurnitureState.OCCUPIED if current else FurnitureState.AVAILABLE
        
        return True, f"You unlock {character.key} from the {self.key}."
    
    # -------------------------------------------------------------------------
    # DESCRIPTION
    # -------------------------------------------------------------------------
    
    def get_display_name(self, looker: "DefaultCharacter" = None, **kwargs) -> str:
        """Get display name with state indicators."""
        name = self.key
        
        if self.state == FurnitureState.BROKEN:
            name = f"{name} (broken)"
        elif self.state == FurnitureState.LOCKED:
            name = f"{name} (locked)"
        elif self.state == FurnitureState.OCCUPIED:
            name = f"{name} (occupied)"
        
        return name
    
    def get_occupant_description(self) -> str:
        """Get description of who's on the furniture."""
        occupants = self.get_occupants()
        if not occupants:
            return ""
        
        lines = []
        slots = self.get_slots()
        
        for occ in occupants:
            slot = slots.get(occ.slot_key)
            if slot and slot.description:
                desc = slot.description.format(
                    name=occ.character_name,
                    position=occ.position.value
                )
            else:
                desc = f"{occ.character_name} is {occ.position.value} here"
            
            if occ.is_locked:
                desc += " (locked)"
            
            lines.append(desc)
        
        return "\n".join(lines)
    
    def return_appearance(self, looker: "DefaultCharacter" = None, **kwargs) -> str:
        """Full appearance including occupants."""
        desc = self.db.desc or f"A {self.quality} {self.material} {self.key}."
        
        occ_desc = self.get_occupant_description()
        if occ_desc:
            desc = f"{desc}\n\n{occ_desc}"
        
        return desc
    
    # -------------------------------------------------------------------------
    # MESSAGE HELPERS
    # -------------------------------------------------------------------------
    
    def _get_use_message(
        self,
        character: "DefaultCharacter",
        slot: FurnitureSlot,
        position: OccupantPosition
    ) -> str:
        """Get message for using furniture."""
        return f"You {position.value.replace('_', ' ')} on the {self.key}."
    
    def _get_release_message(self, character: "DefaultCharacter") -> str:
        """Get message for leaving furniture."""
        return f"You get off the {self.key}."
    
    # -------------------------------------------------------------------------
    # DAMAGE
    # -------------------------------------------------------------------------
    
    def damage(self, amount: int, reason: str = "") -> Tuple[bool, str]:
        """
        Damage the furniture.
        
        Returns:
            (broke, message)
        """
        self.condition = max(0, self.condition - amount)
        
        if self.condition <= 0:
            self.state = FurnitureState.BROKEN
            # Release all occupants
            for occ in self.get_occupants():
                # Would need to look up character by dbref
                pass
            return True, f"The {self.key} breaks!"
        
        return False, f"The {self.key} creaks ominously."
    
    def repair(self, amount: int) -> str:
        """Repair the furniture."""
        old_condition = self.condition
        self.condition = min(100, self.condition + amount)
        
        if old_condition <= 0 and self.condition > 0:
            self.state = FurnitureState.AVAILABLE
            return f"The {self.key} has been repaired."
        
        return f"The {self.key} is in better condition."


# =============================================================================
# EXPORTS
# =============================================================================

__all__ = [
    # Enums
    "FurnitureType",
    "FurnitureState",
    "OccupantPosition",
    
    # Data classes
    "FurnitureSlot",
    "Occupant",
    
    # Base class
    "Furniture",
]
