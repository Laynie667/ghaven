"""
Harness System
==============

Harnesses for breeding, riding, and restraint:
- Breeding harnesses (position lock, escape prevention)
- Mounting harnesses (assist smaller mounting larger)
- Riding harnesses (saddles, stirrups)
- Restraint harnesses
"""

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any, Set
from enum import Enum


# =============================================================================
# ENUMS
# =============================================================================

class HarnessType(Enum):
    """Types of harnesses."""
    BREEDING = "breeding"
    MOUNTING = "mounting"
    RIDING = "riding"
    RESTRAINT = "restraint"
    BELLY_SLING = "belly_sling"
    MILKING = "milking"
    CART = "cart"


class HarnessSlot(Enum):
    """Where harness is worn."""
    TORSO = "torso"
    HIPS = "hips"
    FULL_BODY = "full_body"
    BELLY = "belly"  # For belly slings on taurs


# =============================================================================
# HARNESS BASE
# =============================================================================

@dataclass
class Harness:
    """Base harness class."""
    key: str
    name: str
    harness_type: HarnessType
    slot: HarnessSlot = HarnessSlot.TORSO
    
    # Physical properties
    material: str = "leather"
    color: str = "black"
    
    # Lockability
    is_lockable: bool = True
    is_locked: bool = False
    
    # Who can use
    requires_structure: List[str] = field(default_factory=list)  # e.g., ["tauroid", "quadruped"]
    wearer_sex: str = "any"  # "male", "female", "any"
    
    # Features
    has_handles: bool = False
    has_d_rings: bool = True
    has_tail_lift: bool = False
    has_spread_straps: bool = False
    connects_to_furniture: bool = False
    connects_to_partner: bool = False  # For double harnesses
    
    # Mechanical effects
    breeding_bonus: float = 0.0       # Conception bonus
    escape_dc_mod: int = 0            # Modifier to escape DC
    position_lock: bool = False       # Locks wearer in position
    knot_security: bool = False       # Prevents breaking knot lock
    mount_assist: bool = False        # Helps smaller mount larger
    
    # Capacity (for slings)
    max_occupants: int = 0            # How many can be held
    
    # Descriptions
    short_desc: str = ""
    worn_desc: str = ""
    in_use_desc: str = ""
    
    def get_full_description(self) -> str:
        """Get full item description."""
        parts = [f"A {self.color} {self.material} {self.name.lower()}."]
        
        if self.short_desc:
            parts.append(self.short_desc)
        
        features = []
        if self.has_handles:
            features.append("handle grips")
        if self.has_d_rings:
            features.append("D-rings")
        if self.has_tail_lift:
            features.append("a tail lift strap")
        if self.has_spread_straps:
            features.append("spread straps")
        
        if features:
            parts.append(f"It features {', '.join(features)}.")
        
        if self.is_lockable:
            parts.append("It can be locked in place.")
        
        return " ".join(parts)
    
    def lock(self) -> bool:
        """Lock the harness."""
        if self.is_lockable:
            self.is_locked = True
            return True
        return False
    
    def unlock(self) -> bool:
        """Unlock the harness."""
        self.is_locked = False
        return True
    
    def to_dict(self) -> dict:
        return {
            "key": self.key,
            "name": self.name,
            "harness_type": self.harness_type.value,
            "slot": self.slot.value,
            "material": self.material,
            "color": self.color,
            "is_lockable": self.is_lockable,
            "is_locked": self.is_locked,
            "requires_structure": self.requires_structure,
            "wearer_sex": self.wearer_sex,
            "has_handles": self.has_handles,
            "has_d_rings": self.has_d_rings,
            "has_tail_lift": self.has_tail_lift,
            "has_spread_straps": self.has_spread_straps,
            "connects_to_furniture": self.connects_to_furniture,
            "connects_to_partner": self.connects_to_partner,
            "breeding_bonus": self.breeding_bonus,
            "escape_dc_mod": self.escape_dc_mod,
            "position_lock": self.position_lock,
            "knot_security": self.knot_security,
            "mount_assist": self.mount_assist,
            "max_occupants": self.max_occupants,
            "short_desc": self.short_desc,
            "worn_desc": self.worn_desc,
            "in_use_desc": self.in_use_desc,
        }
    
    @classmethod
    def from_dict(cls, data: dict) -> "Harness":
        harness = cls(
            key=data["key"],
            name=data["name"],
            harness_type=HarnessType(data["harness_type"]),
        )
        harness.slot = HarnessSlot(data.get("slot", "torso"))
        harness.material = data.get("material", "leather")
        harness.color = data.get("color", "black")
        harness.is_lockable = data.get("is_lockable", True)
        harness.is_locked = data.get("is_locked", False)
        harness.requires_structure = data.get("requires_structure", [])
        harness.wearer_sex = data.get("wearer_sex", "any")
        harness.has_handles = data.get("has_handles", False)
        harness.has_d_rings = data.get("has_d_rings", True)
        harness.has_tail_lift = data.get("has_tail_lift", False)
        harness.has_spread_straps = data.get("has_spread_straps", False)
        harness.connects_to_furniture = data.get("connects_to_furniture", False)
        harness.connects_to_partner = data.get("connects_to_partner", False)
        harness.breeding_bonus = data.get("breeding_bonus", 0.0)
        harness.escape_dc_mod = data.get("escape_dc_mod", 0)
        harness.position_lock = data.get("position_lock", False)
        harness.knot_security = data.get("knot_security", False)
        harness.mount_assist = data.get("mount_assist", False)
        harness.max_occupants = data.get("max_occupants", 0)
        harness.short_desc = data.get("short_desc", "")
        harness.worn_desc = data.get("worn_desc", "")
        harness.in_use_desc = data.get("in_use_desc", "")
        return harness


# =============================================================================
# BREEDING HARNESSES
# =============================================================================

BASIC_BREEDING_HARNESS = Harness(
    key="basic_breeding_harness",
    name="Basic Breeding Harness",
    harness_type=HarnessType.BREEDING,
    slot=HarnessSlot.HIPS,
    has_handles=True,
    has_d_rings=True,
    breeding_bonus=0.15,
    escape_dc_mod=30,
    position_lock=True,
    short_desc="A simple harness with hip straps and handles for grip during breeding.",
    worn_desc="{wearer} wears a breeding harness, handles ready for gripping",
    in_use_desc="{wearer} is held in place by a breeding harness while being bred",
)

LOCKING_BREEDING_HARNESS = Harness(
    key="locking_breeding_harness",
    name="Locking Breeding Harness",
    harness_type=HarnessType.BREEDING,
    slot=HarnessSlot.HIPS,
    has_handles=True,
    has_d_rings=True,
    has_tail_lift=True,
    breeding_bonus=0.20,
    escape_dc_mod=50,
    position_lock=True,
    knot_security=True,
    short_desc="A heavy-duty harness with locking straps that prevent escape during knotting.",
    worn_desc="{wearer} is locked into a breeding harness, unable to pull away",
    in_use_desc="{wearer} is locked in the breeding harness, completely unable to escape the knot",
)

TRAINING_BREEDING_HARNESS = Harness(
    key="training_breeding_harness",
    name="Training Breeding Harness",
    harness_type=HarnessType.BREEDING,
    slot=HarnessSlot.FULL_BODY,
    has_handles=True,
    has_d_rings=True,
    has_tail_lift=True,
    has_spread_straps=True,
    breeding_bonus=0.25,
    escape_dc_mod=70,
    position_lock=True,
    knot_security=True,
    connects_to_furniture=True,
    short_desc="A comprehensive harness designed to break in reluctant breeders.",
    worn_desc="{wearer} is strapped into a training harness, spread and unable to resist",
    in_use_desc="{wearer} is held completely immobile in the training harness while being bred",
)

PONY_BREEDING_HARNESS = Harness(
    key="pony_breeding_harness",
    name="Pony Breeding Harness",
    harness_type=HarnessType.BREEDING,
    slot=HarnessSlot.FULL_BODY,
    requires_structure=["tauroid", "quadruped"],
    has_handles=True,
    has_d_rings=True,
    has_tail_lift=True,
    breeding_bonus=0.20,
    escape_dc_mod=40,
    position_lock=True,
    short_desc="A harness designed for equine breeding, with blinders and tail lift.",
    worn_desc="{wearer} is fitted with a pony breeding harness, tail lifted for access",
)

DOUBLE_HARNESS = Harness(
    key="double_harness",
    name="Double Breeding Harness",
    harness_type=HarnessType.BREEDING,
    slot=HarnessSlot.HIPS,
    has_handles=True,
    has_d_rings=True,
    breeding_bonus=0.15,
    escape_dc_mod=40,
    position_lock=True,
    connects_to_partner=True,
    max_occupants=2,
    short_desc="A harness that connects two receivers together for simultaneous breeding.",
    worn_desc="{wearer} is connected to another by a double breeding harness",
    in_use_desc="Two bodies are connected by the double harness, bred side by side",
)

MILKING_BREEDING_HARNESS = Harness(
    key="milking_breeding_harness",
    name="Milking Breeding Harness",
    harness_type=HarnessType.MILKING,
    slot=HarnessSlot.FULL_BODY,
    has_handles=True,
    has_d_rings=True,
    has_tail_lift=True,
    breeding_bonus=0.20,
    escape_dc_mod=45,
    position_lock=True,
    short_desc="A harness that provides access to both ends for breeding and milking.",
    worn_desc="{wearer} wears a milking-breeding harness, accessible from both ends",
)

# =============================================================================
# MOUNTING HARNESSES
# =============================================================================

MOUNTING_ASSIST_HARNESS = Harness(
    key="mounting_assist_harness",
    name="Mounting Assist Harness",
    harness_type=HarnessType.MOUNTING,
    slot=HarnessSlot.TORSO,
    has_handles=True,
    has_d_rings=True,
    mount_assist=True,
    short_desc="A harness with straps and handles that helps smaller partners mount larger ones.",
    worn_desc="{wearer} wears a mounting assist harness with convenient grips",
)

STABILITY_HARNESS = Harness(
    key="stability_harness",
    name="Stability Harness",
    harness_type=HarnessType.MOUNTING,
    slot=HarnessSlot.TORSO,
    has_handles=True,
    has_d_rings=True,
    connects_to_partner=True,
    mount_assist=True,
    escape_dc_mod=20,
    short_desc="A harness that connects mounter to receiver, preventing slipping off.",
    worn_desc="{wearer} is secured by a stability harness, locked to their partner",
)

# =============================================================================
# BELLY SLING HARNESSES
# =============================================================================

BASIC_BELLY_SLING = Harness(
    key="basic_belly_sling",
    name="Basic Belly Sling",
    harness_type=HarnessType.BELLY_SLING,
    slot=HarnessSlot.BELLY,
    requires_structure=["tauroid", "quadruped"],
    has_d_rings=True,
    escape_dc_mod=60,
    position_lock=True,
    max_occupants=1,
    short_desc="A sling that hangs beneath a tauroid's belly to carry a passenger.",
    worn_desc="{carrier} has a belly sling hanging beneath them",
    in_use_desc="{passenger} hangs suspended in the belly sling beneath {carrier}",
)

CONCEALED_BELLY_SLING = Harness(
    key="concealed_belly_sling",
    name="Concealed Belly Sling",
    harness_type=HarnessType.BELLY_SLING,
    slot=HarnessSlot.BELLY,
    requires_structure=["tauroid", "quadruped"],
    has_d_rings=True,
    escape_dc_mod=80,
    position_lock=True,
    max_occupants=1,
    short_desc="A low-profile sling designed to be hidden beneath a saddle blanket.",
    worn_desc="{carrier} has a subtle belly sling that's hard to notice",
    in_use_desc="{passenger} is secretly suspended beneath {carrier}, concealed from view",
)

BREEDING_BELLY_SLING = Harness(
    key="breeding_belly_sling",
    name="Breeding Belly Sling",
    harness_type=HarnessType.BELLY_SLING,
    slot=HarnessSlot.BELLY,
    requires_structure=["tauroid", "quadruped"],
    has_d_rings=True,
    has_spread_straps=True,
    breeding_bonus=0.15,
    escape_dc_mod=80,
    position_lock=True,
    knot_security=True,
    max_occupants=1,
    short_desc="A belly sling designed to position the occupant for breeding by the carrier.",
    worn_desc="{carrier} has a breeding sling beneath them",
    in_use_desc="{passenger} hangs in the breeding sling, impaled on {carrier}'s shaft",
)

LOCKING_BELLY_SLING = Harness(
    key="locking_belly_sling",
    name="Locking Belly Sling",
    harness_type=HarnessType.BELLY_SLING,
    slot=HarnessSlot.BELLY,
    requires_structure=["tauroid", "quadruped"],
    has_d_rings=True,
    has_spread_straps=True,
    escape_dc_mod=100,
    position_lock=True,
    knot_security=True,
    max_occupants=1,
    short_desc="A belly sling with locking restraints that make escape nearly impossible.",
    worn_desc="{carrier} has a locking belly sling beneath them",
    in_use_desc="{passenger} is locked into the belly sling, completely helpless",
)

DOUBLE_BELLY_SLING = Harness(
    key="double_belly_sling",
    name="Double Belly Sling",
    harness_type=HarnessType.BELLY_SLING,
    slot=HarnessSlot.BELLY,
    requires_structure=["tauroid", "quadruped"],
    has_d_rings=True,
    escape_dc_mod=70,
    position_lock=True,
    max_occupants=2,
    short_desc="A large belly sling capable of carrying two passengers.",
    worn_desc="{carrier} has a large double belly sling",
    in_use_desc="Two bodies hang suspended in the belly sling beneath {carrier}",
)

# =============================================================================
# RIDING HARNESSES
# =============================================================================

BASIC_SADDLE = Harness(
    key="basic_saddle",
    name="Basic Saddle",
    harness_type=HarnessType.RIDING,
    slot=HarnessSlot.TORSO,
    requires_structure=["tauroid", "quadruped"],
    has_d_rings=True,
    max_occupants=1,
    short_desc="A simple saddle for riding.",
    worn_desc="{wearer} is saddled",
)

BREEDING_SADDLE = Harness(
    key="breeding_saddle",
    name="Breeding Saddle",
    harness_type=HarnessType.RIDING,
    slot=HarnessSlot.TORSO,
    requires_structure=["tauroid", "quadruped"],
    has_d_rings=True,
    breeding_bonus=0.10,
    max_occupants=1,
    short_desc="A saddle with cutouts that provide access for breeding while riding.",
    worn_desc="{wearer} wears a breeding saddle with strategic openings",
)

CART_HARNESS = Harness(
    key="cart_harness",
    name="Cart Harness",
    harness_type=HarnessType.CART,
    slot=HarnessSlot.FULL_BODY,
    requires_structure=["tauroid", "quadruped"],
    has_d_rings=True,
    short_desc="A harness for pulling carts or sulkies.",
    worn_desc="{wearer} is harnessed for pulling",
)

# =============================================================================
# RESTRAINT HARNESSES
# =============================================================================

FULL_BODY_HARNESS = Harness(
    key="full_body_harness",
    name="Full Body Restraint Harness",
    harness_type=HarnessType.RESTRAINT,
    slot=HarnessSlot.FULL_BODY,
    has_handles=True,
    has_d_rings=True,
    escape_dc_mod=60,
    position_lock=True,
    connects_to_furniture=True,
    short_desc="A comprehensive harness with straps across the entire body.",
    worn_desc="{wearer} is wrapped in a full body harness",
)

SUSPENSION_HARNESS = Harness(
    key="suspension_harness",
    name="Suspension Harness",
    harness_type=HarnessType.RESTRAINT,
    slot=HarnessSlot.FULL_BODY,
    has_d_rings=True,
    escape_dc_mod=80,
    position_lock=True,
    connects_to_furniture=True,
    short_desc="A harness designed for safe suspension and bondage.",
    worn_desc="{wearer} is secured in a suspension harness",
)

CROTCH_HARNESS = Harness(
    key="crotch_harness",
    name="Crotch Harness",
    harness_type=HarnessType.RESTRAINT,
    slot=HarnessSlot.HIPS,
    has_d_rings=True,
    escape_dc_mod=40,
    short_desc="A harness that frames and exposes the crotch area.",
    worn_desc="{wearer} wears a crotch harness, genitals framed and exposed",
)


# =============================================================================
# HARNESS REGISTRY
# =============================================================================

ALL_HARNESSES: Dict[str, Harness] = {
    # Breeding
    "basic_breeding_harness": BASIC_BREEDING_HARNESS,
    "locking_breeding_harness": LOCKING_BREEDING_HARNESS,
    "training_breeding_harness": TRAINING_BREEDING_HARNESS,
    "pony_breeding_harness": PONY_BREEDING_HARNESS,
    "double_harness": DOUBLE_HARNESS,
    "milking_breeding_harness": MILKING_BREEDING_HARNESS,
    # Mounting
    "mounting_assist_harness": MOUNTING_ASSIST_HARNESS,
    "stability_harness": STABILITY_HARNESS,
    # Belly slings
    "basic_belly_sling": BASIC_BELLY_SLING,
    "concealed_belly_sling": CONCEALED_BELLY_SLING,
    "breeding_belly_sling": BREEDING_BELLY_SLING,
    "locking_belly_sling": LOCKING_BELLY_SLING,
    "double_belly_sling": DOUBLE_BELLY_SLING,
    # Riding
    "basic_saddle": BASIC_SADDLE,
    "breeding_saddle": BREEDING_SADDLE,
    "cart_harness": CART_HARNESS,
    # Restraint
    "full_body_harness": FULL_BODY_HARNESS,
    "suspension_harness": SUSPENSION_HARNESS,
    "crotch_harness": CROTCH_HARNESS,
}


def get_harness(key: str) -> Optional[Harness]:
    """Get harness by key."""
    return ALL_HARNESSES.get(key)


def get_harnesses_by_type(harness_type: HarnessType) -> List[Harness]:
    """Get all harnesses of a type."""
    return [h for h in ALL_HARNESSES.values() if h.harness_type == harness_type]


def get_belly_slings() -> List[Harness]:
    """Get all belly sling harnesses."""
    return get_harnesses_by_type(HarnessType.BELLY_SLING)


def get_breeding_harnesses() -> List[Harness]:
    """Get all breeding harnesses."""
    return get_harnesses_by_type(HarnessType.BREEDING)


# =============================================================================
# HARNESS MIXIN
# =============================================================================

class HarnessMixin:
    """
    Mixin for characters that can wear harnesses.
    """
    
    @property
    def worn_harness(self) -> Optional[Harness]:
        """Get currently worn harness."""
        data = self.attributes.get("worn_harness")
        if data:
            return Harness.from_dict(data)
        return None
    
    @worn_harness.setter
    def worn_harness(self, harness: Optional[Harness]):
        """Set worn harness."""
        if harness:
            self.attributes.add("worn_harness", harness.to_dict())
        else:
            self.attributes.remove("worn_harness")
    
    def can_wear_harness(self, harness: Harness) -> tuple[bool, str]:
        """Check if character can wear a harness."""
        # Check existing harness
        if self.worn_harness:
            return False, "Already wearing a harness."
        
        # Check structure requirements
        if harness.requires_structure:
            char_structure = getattr(self, 'body_structure', None)
            if char_structure and char_structure not in harness.requires_structure:
                return False, f"This harness requires: {', '.join(harness.requires_structure)}"
        
        # Check sex requirements
        if harness.wearer_sex != "any":
            char_sex = getattr(self, 'sex', 'any')
            if char_sex != harness.wearer_sex:
                return False, f"This harness is for {harness.wearer_sex} only."
        
        return True, ""
    
    def put_on_harness(self, harness: Harness) -> str:
        """Put on a harness."""
        can_wear, reason = self.can_wear_harness(harness)
        if not can_wear:
            return reason
        
        self.worn_harness = harness
        return f"You strap on the {harness.name}."
    
    def remove_harness(self, force: bool = False) -> str:
        """Remove worn harness."""
        harness = self.worn_harness
        if not harness:
            return "Not wearing a harness."
        
        if harness.is_locked and not force:
            return f"The {harness.name} is locked on!"
        
        self.worn_harness = None
        return f"You remove the {harness.name}."
    
    def get_harness_breeding_bonus(self) -> float:
        """Get breeding bonus from harness."""
        harness = self.worn_harness
        if harness:
            return harness.breeding_bonus
        return 0.0
    
    def get_harness_escape_mod(self) -> int:
        """Get escape DC modifier from harness."""
        harness = self.worn_harness
        if harness:
            return harness.escape_dc_mod
        return 0
    
    def is_position_locked(self) -> bool:
        """Check if harness locks position."""
        harness = self.worn_harness
        return harness and harness.position_lock
    
    def is_knot_secured(self) -> bool:
        """Check if harness provides knot security."""
        harness = self.worn_harness
        return harness and harness.knot_security


__all__ = [
    "HarnessType",
    "HarnessSlot",
    "Harness",
    "ALL_HARNESSES",
    "get_harness",
    "get_harnesses_by_type",
    "get_belly_slings",
    "get_breeding_harnesses",
    "HarnessMixin",
]
