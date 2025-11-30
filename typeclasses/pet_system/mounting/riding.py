"""
Riding System
=============

System for riding tauroid/quadruped characters:
- Saddle management
- Mounting and dismounting
- Gait control and movement
- Riding positions
"""

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any, Tuple
from enum import Enum


# =============================================================================
# ENUMS
# =============================================================================

class SaddleType(Enum):
    """Types of saddles."""
    BASIC = "basic"
    ENGLISH = "english"
    WESTERN = "western"
    BAREBACK = "bareback"      # No saddle, just pad/blanket
    BREEDING = "breeding"      # Has cutouts for access
    WAR = "war"               # Combat saddle
    CART = "cart"             # For pulling


class RidingPosition(Enum):
    """How the rider is seated."""
    ASTRIDE = "astride"           # Normal riding
    SIDESADDLE = "sidesaddle"     # Legs to one side
    BACKWARD = "backward"          # Facing rear
    LYING_FORWARD = "lying_forward"    # Lying on mount's back
    LYING_BACKWARD = "lying_backward"  # Lying facing up
    BOUND = "bound"               # Tied to saddle


class RiderState(Enum):
    """State of the rider."""
    MOUNTED = "mounted"
    SECURE = "secure"           # Strapped in
    PRECARIOUS = "precarious"   # About to fall
    BOUND_TO_SADDLE = "bound"   # Restrained


# =============================================================================
# SADDLE
# =============================================================================

@dataclass
class Saddle:
    """A saddle for riding."""
    key: str
    name: str
    saddle_type: SaddleType = SaddleType.BASIC
    
    # Properties
    material: str = "leather"
    color: str = "brown"
    
    # Capacity
    max_riders: int = 1
    
    # Features
    has_stirrups: bool = True
    has_pommel: bool = True
    has_cantle: bool = True       # Back of saddle
    has_horn: bool = False        # Western saddles
    has_d_rings: bool = True      # For attaching things
    has_breeding_cutout: bool = False
    
    # Restraint
    can_bind_rider: bool = False
    is_binding: bool = False
    
    # Comfort/Stability
    comfort: int = 50             # 0-100
    stability: int = 50           # 0-100, affects fall chance
    
    # Description
    short_desc: str = ""
    
    def get_description(self) -> str:
        """Get full saddle description."""
        parts = [f"A {self.color} {self.material} {self.saddle_type.value} saddle."]
        
        if self.short_desc:
            parts.append(self.short_desc)
        
        features = []
        if self.has_stirrups:
            features.append("stirrups")
        if self.has_horn:
            features.append("a horn")
        if self.has_d_rings:
            features.append("D-rings for attachments")
        if self.has_breeding_cutout:
            features.append("strategic cutouts for breeding access")
        
        if features:
            parts.append(f"It has {', '.join(features)}.")
        
        return " ".join(parts)
    
    def to_dict(self) -> dict:
        return {
            "key": self.key,
            "name": self.name,
            "saddle_type": self.saddle_type.value,
            "material": self.material,
            "color": self.color,
            "max_riders": self.max_riders,
            "has_stirrups": self.has_stirrups,
            "has_pommel": self.has_pommel,
            "has_cantle": self.has_cantle,
            "has_horn": self.has_horn,
            "has_d_rings": self.has_d_rings,
            "has_breeding_cutout": self.has_breeding_cutout,
            "can_bind_rider": self.can_bind_rider,
            "is_binding": self.is_binding,
            "comfort": self.comfort,
            "stability": self.stability,
            "short_desc": self.short_desc,
        }
    
    @classmethod
    def from_dict(cls, data: dict) -> "Saddle":
        saddle = cls(
            key=data["key"],
            name=data["name"],
        )
        saddle.saddle_type = SaddleType(data.get("saddle_type", "basic"))
        saddle.material = data.get("material", "leather")
        saddle.color = data.get("color", "brown")
        saddle.max_riders = data.get("max_riders", 1)
        saddle.has_stirrups = data.get("has_stirrups", True)
        saddle.has_pommel = data.get("has_pommel", True)
        saddle.has_cantle = data.get("has_cantle", True)
        saddle.has_horn = data.get("has_horn", False)
        saddle.has_d_rings = data.get("has_d_rings", True)
        saddle.has_breeding_cutout = data.get("has_breeding_cutout", False)
        saddle.can_bind_rider = data.get("can_bind_rider", False)
        saddle.is_binding = data.get("is_binding", False)
        saddle.comfort = data.get("comfort", 50)
        saddle.stability = data.get("stability", 50)
        saddle.short_desc = data.get("short_desc", "")
        return saddle


# =============================================================================
# SADDLE DEFINITIONS
# =============================================================================

BASIC_SADDLE = Saddle(
    key="basic_saddle",
    name="Basic Saddle",
    saddle_type=SaddleType.BASIC,
    comfort=50,
    stability=50,
    short_desc="A simple, functional saddle.",
)

ENGLISH_SADDLE = Saddle(
    key="english_saddle",
    name="English Saddle",
    saddle_type=SaddleType.ENGLISH,
    has_horn=False,
    comfort=60,
    stability=55,
    short_desc="A sleek saddle designed for close contact riding.",
)

WESTERN_SADDLE = Saddle(
    key="western_saddle",
    name="Western Saddle",
    saddle_type=SaddleType.WESTERN,
    has_horn=True,
    comfort=70,
    stability=70,
    short_desc="A sturdy saddle with a horn for roping.",
)

BAREBACK_PAD = Saddle(
    key="bareback_pad",
    name="Bareback Pad",
    saddle_type=SaddleType.BAREBACK,
    has_stirrups=False,
    has_pommel=False,
    has_cantle=False,
    has_horn=False,
    comfort=40,
    stability=30,
    short_desc="Just a padded cushion - minimal protection between rider and mount.",
)

BREEDING_SADDLE = Saddle(
    key="breeding_saddle",
    name="Breeding Saddle",
    saddle_type=SaddleType.BREEDING,
    has_breeding_cutout=True,
    can_bind_rider=True,
    comfort=45,
    stability=60,
    short_desc="A saddle with strategic cutouts allowing intimate contact while riding.",
)

BONDAGE_SADDLE = Saddle(
    key="bondage_saddle",
    name="Bondage Saddle",
    saddle_type=SaddleType.BREEDING,
    has_breeding_cutout=True,
    can_bind_rider=True,
    comfort=30,
    stability=80,
    short_desc="A saddle designed to restrain the rider in an exposed position.",
)

WAR_SADDLE = Saddle(
    key="war_saddle",
    name="War Saddle",
    saddle_type=SaddleType.WAR,
    has_horn=True,
    comfort=40,
    stability=85,
    max_riders=1,
    short_desc="A heavy combat saddle with high cantle and armor attachments.",
)

TANDEM_SADDLE = Saddle(
    key="tandem_saddle",
    name="Tandem Saddle",
    saddle_type=SaddleType.WESTERN,
    max_riders=2,
    has_horn=True,
    comfort=55,
    stability=60,
    short_desc="An extended saddle that can accommodate two riders.",
)

ALL_SADDLES: Dict[str, Saddle] = {
    "basic_saddle": BASIC_SADDLE,
    "english_saddle": ENGLISH_SADDLE,
    "western_saddle": WESTERN_SADDLE,
    "bareback_pad": BAREBACK_PAD,
    "breeding_saddle": BREEDING_SADDLE,
    "bondage_saddle": BONDAGE_SADDLE,
    "war_saddle": WAR_SADDLE,
    "tandem_saddle": TANDEM_SADDLE,
}


def get_saddle(key: str) -> Optional[Saddle]:
    """Get saddle by key."""
    return ALL_SADDLES.get(key)


# =============================================================================
# RIDING STATE
# =============================================================================

@dataclass
class RidingState:
    """Tracks the state of a mount being ridden."""
    # Mount
    mount_dbref: str = ""
    mount_name: str = ""
    
    # Riders (list for tandem saddles)
    riders: List[dict] = field(default_factory=list)
    # Each rider: {"dbref": str, "name": str, "position": str, "state": str}
    
    # Saddle
    saddle: Optional[Saddle] = None
    
    # Current gait
    gait: str = "standing"  # Uses CarrierGait from belly_mount
    
    # State
    is_active: bool = False
    
    def add_rider(self, rider_dbref: str, rider_name: str, 
                  position: RidingPosition = RidingPosition.ASTRIDE) -> bool:
        """Add a rider."""
        max_riders = self.saddle.max_riders if self.saddle else 1
        
        if len(self.riders) >= max_riders:
            return False
        
        self.riders.append({
            "dbref": rider_dbref,
            "name": rider_name,
            "position": position.value,
            "state": RiderState.MOUNTED.value,
        })
        self.is_active = True
        return True
    
    def remove_rider(self, rider_dbref: str) -> bool:
        """Remove a rider."""
        for i, rider in enumerate(self.riders):
            if rider["dbref"] == rider_dbref:
                del self.riders[i]
                if not self.riders:
                    self.is_active = False
                return True
        return False
    
    def get_rider(self, rider_dbref: str) -> Optional[dict]:
        """Get rider info."""
        for rider in self.riders:
            if rider["dbref"] == rider_dbref:
                return rider
        return None
    
    def bind_rider(self, rider_dbref: str) -> bool:
        """Bind a rider to the saddle."""
        if not self.saddle or not self.saddle.can_bind_rider:
            return False
        
        for rider in self.riders:
            if rider["dbref"] == rider_dbref:
                rider["state"] = RiderState.BOUND_TO_SADDLE.value
                return True
        return False
    
    def unbind_rider(self, rider_dbref: str) -> bool:
        """Unbind a rider."""
        for rider in self.riders:
            if rider["dbref"] == rider_dbref:
                if rider["state"] == RiderState.BOUND_TO_SADDLE.value:
                    rider["state"] = RiderState.MOUNTED.value
                    return True
        return False
    
    def to_dict(self) -> dict:
        return {
            "mount_dbref": self.mount_dbref,
            "mount_name": self.mount_name,
            "riders": self.riders,
            "saddle": self.saddle.to_dict() if self.saddle else None,
            "gait": self.gait,
            "is_active": self.is_active,
        }
    
    @classmethod
    def from_dict(cls, data: dict) -> "RidingState":
        state = cls()
        state.mount_dbref = data.get("mount_dbref", "")
        state.mount_name = data.get("mount_name", "")
        state.riders = data.get("riders", [])
        
        if data.get("saddle"):
            state.saddle = Saddle.from_dict(data["saddle"])
        
        state.gait = data.get("gait", "standing")
        state.is_active = data.get("is_active", False)
        
        return state


# =============================================================================
# RIDING SYSTEM
# =============================================================================

class RidingSystem:
    """
    Manages riding operations.
    """
    
    @staticmethod
    def can_be_mounted(character) -> Tuple[bool, str]:
        """Check if character can be ridden."""
        structure = getattr(character, 'body_structure', None)
        
        valid_structures = ["tauroid", "quadruped"]
        
        if structure and structure.lower() in valid_structures:
            return True, ""
        
        return False, "Only tauroid or quadruped characters can be ridden."
    
    @staticmethod
    def can_mount(mount, rider) -> Tuple[bool, str]:
        """Check if rider can mount."""
        can_ride, reason = RidingSystem.can_be_mounted(mount)
        if not can_ride:
            return False, reason
        
        # Check mount's riding state
        state = RidingSystem.get_riding_state(mount)
        
        if state and state.is_active:
            saddle = state.saddle
            max_riders = saddle.max_riders if saddle else 1
            
            if len(state.riders) >= max_riders:
                return False, f"{mount.key} already has maximum riders."
        
        # Check if rider is already mounted
        if hasattr(rider, 'mounted_on') and rider.mounted_on:
            return False, f"{rider.key} is already mounted on something."
        
        return True, ""
    
    @staticmethod
    def get_riding_state(mount) -> Optional[RidingState]:
        """Get riding state for a mount."""
        data = mount.attributes.get("riding_state")
        if data:
            return RidingState.from_dict(data)
        return None
    
    @staticmethod
    def saddle_mount(mount, saddle: Saddle) -> str:
        """Put a saddle on a mount."""
        can_ride, reason = RidingSystem.can_be_mounted(mount)
        if not can_ride:
            return reason
        
        state = RidingSystem.get_riding_state(mount)
        
        if state and state.is_active and state.riders:
            return "Cannot change saddle while riders are mounted."
        
        if not state:
            state = RidingState(
                mount_dbref=mount.dbref,
                mount_name=mount.key,
            )
        
        state.saddle = saddle
        mount.attributes.add("riding_state", state.to_dict())
        
        return f"You saddle {mount.key} with a {saddle.name}."
    
    @staticmethod
    def unsaddle_mount(mount) -> str:
        """Remove saddle from mount."""
        state = RidingSystem.get_riding_state(mount)
        
        if not state or not state.saddle:
            return f"{mount.key} is not saddled."
        
        if state.is_active and state.riders:
            return "Cannot remove saddle while riders are mounted."
        
        saddle_name = state.saddle.name
        state.saddle = None
        mount.attributes.add("riding_state", state.to_dict())
        
        return f"You remove the {saddle_name} from {mount.key}."
    
    @staticmethod
    def mount_rider(mount, rider, position: RidingPosition = RidingPosition.ASTRIDE) -> Tuple[bool, str]:
        """Mount a rider onto a mount."""
        can_mount, reason = RidingSystem.can_mount(mount, rider)
        if not can_mount:
            return False, reason
        
        state = RidingSystem.get_riding_state(mount)
        
        if not state:
            state = RidingState(
                mount_dbref=mount.dbref,
                mount_name=mount.key,
            )
        
        success = state.add_rider(rider.dbref, rider.key, position)
        
        if not success:
            return False, f"{mount.key} cannot carry any more riders."
        
        mount.attributes.add("riding_state", state.to_dict())
        rider.attributes.add("mounted_on", mount.dbref)
        
        position_desc = {
            RidingPosition.ASTRIDE: "astride",
            RidingPosition.SIDESADDLE: "sidesaddle",
            RidingPosition.BACKWARD: "facing backward",
            RidingPosition.LYING_FORWARD: "lying forward",
            RidingPosition.LYING_BACKWARD: "lying back",
            RidingPosition.BOUND: "bound to the saddle",
        }
        
        pos_text = position_desc.get(position, "")
        
        return True, f"{rider.key} mounts {mount.key}{' ' + pos_text if pos_text else ''}."
    
    @staticmethod
    def dismount_rider(mount, rider, force: bool = False) -> Tuple[bool, str]:
        """Dismount a rider."""
        state = RidingSystem.get_riding_state(mount)
        
        if not state:
            return False, f"{rider.key} is not mounted on {mount.key}."
        
        rider_info = state.get_rider(rider.dbref)
        
        if not rider_info:
            return False, f"{rider.key} is not mounted on {mount.key}."
        
        # Check if bound
        if rider_info["state"] == RiderState.BOUND_TO_SADDLE.value and not force:
            return False, f"{rider.key} is bound to the saddle and cannot dismount!"
        
        state.remove_rider(rider.dbref)
        mount.attributes.add("riding_state", state.to_dict())
        rider.attributes.remove("mounted_on")
        
        return True, f"{rider.key} dismounts from {mount.key}."
    
    @staticmethod
    def bind_rider_to_saddle(mount, rider) -> Tuple[bool, str]:
        """Bind a rider to the saddle."""
        state = RidingSystem.get_riding_state(mount)
        
        if not state:
            return False, "No riding state."
        
        if not state.saddle or not state.saddle.can_bind_rider:
            return False, "This saddle cannot bind riders."
        
        if state.bind_rider(rider.dbref):
            mount.attributes.add("riding_state", state.to_dict())
            return True, f"{rider.key} is bound to the saddle on {mount.key}."
        
        return False, f"{rider.key} is not mounted on {mount.key}."
    
    @staticmethod
    def unbind_rider(mount, rider) -> Tuple[bool, str]:
        """Unbind a rider from the saddle."""
        state = RidingSystem.get_riding_state(mount)
        
        if not state:
            return False, "No riding state."
        
        if state.unbind_rider(rider.dbref):
            mount.attributes.add("riding_state", state.to_dict())
            return True, f"{rider.key} is released from the saddle bindings."
        
        return False, f"{rider.key} is not bound."
    
    @staticmethod
    def change_gait(mount, gait: str) -> str:
        """Change the mount's gait."""
        state = RidingSystem.get_riding_state(mount)
        
        if state:
            state.gait = gait
            mount.attributes.add("riding_state", state.to_dict())
        
        gait_descs = {
            "standing": f"{mount.key} stands still.",
            "walking": f"{mount.key} walks at an easy pace.",
            "trotting": f"{mount.key} breaks into a trot.",
            "cantering": f"{mount.key} canters smoothly.",
            "galloping": f"{mount.key} gallops at full speed!",
        }
        
        return gait_descs.get(gait, f"{mount.key} moves at a {gait}.")
    
    @staticmethod
    def get_riding_description(mount) -> str:
        """Get description of mount being ridden for room desc."""
        state = RidingSystem.get_riding_state(mount)
        
        if not state or not state.is_active or not state.riders:
            if state and state.saddle:
                return f"saddled with a {state.saddle.name}"
            return ""
        
        rider_names = [r["name"] for r in state.riders]
        
        if len(rider_names) == 1:
            rider_text = rider_names[0]
        else:
            rider_text = f"{', '.join(rider_names[:-1])} and {rider_names[-1]}"
        
        saddle_text = f"a {state.saddle.name}" if state.saddle else "bareback"
        
        return f"carrying {rider_text} on {saddle_text}"


# =============================================================================
# RIDING MIXINS
# =============================================================================

class MountMixin:
    """
    Mixin for characters that can be ridden.
    """
    
    @property
    def riding_state(self) -> Optional[RidingState]:
        """Get riding state."""
        return RidingSystem.get_riding_state(self)
    
    def is_being_ridden(self) -> bool:
        """Check if being ridden."""
        state = self.riding_state
        return state is not None and state.is_active
    
    def get_riders(self) -> List[dict]:
        """Get list of current riders."""
        state = self.riding_state
        if state:
            return state.riders
        return []
    
    def is_saddled(self) -> bool:
        """Check if saddled."""
        state = self.riding_state
        return state is not None and state.saddle is not None


class RiderMixin:
    """
    Mixin for characters that can ride.
    """
    
    @property
    def mounted_on(self) -> str:
        """Get dbref of mount if mounted."""
        return self.attributes.get("mounted_on", "")
    
    def is_mounted(self) -> bool:
        """Check if currently mounted."""
        return bool(self.mounted_on)
    
    def is_bound_to_saddle(self) -> bool:
        """Check if bound to saddle."""
        mount_ref = self.mounted_on
        if not mount_ref:
            return False
        
        # Would need to look up mount and check state
        # In real implementation, would fetch mount object
        return False


__all__ = [
    "SaddleType",
    "RidingPosition",
    "RiderState",
    "Saddle",
    "ALL_SADDLES",
    "get_saddle",
    "RidingState",
    "RidingSystem",
    "MountMixin",
    "RiderMixin",
]
