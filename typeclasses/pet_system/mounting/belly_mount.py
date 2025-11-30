"""
Belly Mount System
==================

System for mounting passengers beneath tauroid/quadruped characters:
- Position someone in a belly sling beneath a carrier
- Different mounting positions (belly, sheath, udder)
- Movement effects (walking, trotting, galloping = stimulation)
- Concealment mechanics (saddle blankets)
"""

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any, Tuple
from enum import Enum
import random


# =============================================================================
# ENUMS
# =============================================================================

class BellyMountPosition(Enum):
    """Positions for belly-mounted passengers."""
    BELLY_SLUNG = "belly_slung"          # Generic, against belly
    SHEATH_MOUNT = "sheath_mount"        # Positioned at sheath, penetrated
    SHEATH_ORAL = "sheath_oral"          # Face at sheath, oral service
    UDDER_MOUNT = "udder_mount"          # Face at udders, nursing
    BREEDING_SLUNG = "breeding_slung"    # Rear exposed for third party
    INVERTED = "inverted"                # Upside down


class CarrierGait(Enum):
    """Movement gaits for carrier."""
    STANDING = "standing"
    WALKING = "walking"
    TROTTING = "trotting"
    CANTERING = "cantering"
    GALLOPING = "galloping"


class ConcealmentLevel(Enum):
    """How well the passenger is concealed."""
    EXPOSED = "exposed"          # Clearly visible
    PARTIAL = "partial"          # Partly hidden
    CONCEALED = "concealed"      # Hidden but detectable
    HIDDEN = "hidden"            # Very hard to notice


# =============================================================================
# MOVEMENT EFFECTS
# =============================================================================

GAIT_EFFECTS = {
    CarrierGait.STANDING: {
        "thrust_frequency": 0,      # Thrusts per tick
        "intensity": 0.0,           # 0-1
        "stamina_drain": 0,         # Per tick
        "description": "{carrier} stands still",
        "passenger_effect": "{passenger} hangs motionless",
    },
    CarrierGait.WALKING: {
        "thrust_frequency": 1,
        "intensity": 0.3,
        "stamina_drain": 1,
        "description": "{carrier} walks at a leisurely pace",
        "passenger_effect": "each step shifts {passenger} against {carrier}",
    },
    CarrierGait.TROTTING: {
        "thrust_frequency": 2,
        "intensity": 0.5,
        "stamina_drain": 2,
        "description": "{carrier} trots along briskly",
        "passenger_effect": "the trot bounces {passenger} rhythmically",
    },
    CarrierGait.CANTERING: {
        "thrust_frequency": 3,
        "intensity": 0.7,
        "stamina_drain": 4,
        "description": "{carrier} canters smoothly",
        "passenger_effect": "the canter drives {carrier}'s length deep into {passenger} with each stride",
    },
    CarrierGait.GALLOPING: {
        "thrust_frequency": 5,
        "intensity": 1.0,
        "stamina_drain": 8,
        "description": "{carrier} gallops at full speed",
        "passenger_effect": "{passenger} is pounded mercilessly by {carrier}'s gallop",
    },
}


# =============================================================================
# POSITION DEFINITIONS
# =============================================================================

@dataclass
class BellyPositionDef:
    """Definition of a belly mount position."""
    key: str
    name: str
    
    # Requirements
    carrier_sex: str = "any"      # "male", "female", "any"
    carrier_structure: List[str] = field(default_factory=lambda: ["tauroid", "quadruped"])
    
    # Passenger position
    passenger_orientation: str = "horizontal"  # horizontal, vertical, inverted
    passenger_facing: str = "up"               # up, down, forward, back
    
    # Access/exposure
    exposes: List[str] = field(default_factory=list)  # Body parts exposed
    accessible_to_carrier: List[str] = field(default_factory=list)  # What carrier can access
    
    # Penetration
    involves_penetration: bool = False
    penetration_source: str = ""    # "sheath", "external"
    
    # Oral
    involves_oral: bool = False
    oral_target: str = ""           # "sheath", "udders"
    
    # Movement effects
    movement_effect: str = ""       # "thrust_per_step", "sway", "bounce"
    
    # Concealment
    can_be_concealed: bool = True
    base_concealment: ConcealmentLevel = ConcealmentLevel.EXPOSED
    
    # Description templates
    entry_desc: str = ""
    ongoing_desc: str = ""
    movement_desc: str = ""


BELLY_POSITIONS: Dict[str, BellyPositionDef] = {
    "belly_slung": BellyPositionDef(
        key="belly_slung",
        name="Belly Slung",
        passenger_orientation="horizontal",
        passenger_facing="up",
        exposes=["front", "face"],
        accessible_to_carrier=["chest", "face"],
        movement_effect="sway",
        entry_desc="{passenger} is secured in the sling beneath {carrier}'s belly",
        ongoing_desc="{passenger} hangs suspended, pressed against {carrier}'s warm belly",
        movement_desc="Each step sways {passenger} gently",
    ),
    "sheath_mount": BellyPositionDef(
        key="sheath_mount",
        name="Sheath Locked",
        carrier_sex="male",
        passenger_orientation="horizontal",
        passenger_facing="up",
        exposes=["back", "rear"],
        accessible_to_carrier=["genitals", "chest"],
        involves_penetration=True,
        penetration_source="sheath",
        movement_effect="thrust_per_step",
        can_be_concealed=True,
        entry_desc="{passenger} is impaled on {carrier}'s shaft as they're secured in the sling",
        ongoing_desc="{passenger} hangs suspended, stretched around {carrier}'s massive length",
        movement_desc="Every step drives {carrier} deeper into {passenger}",
    ),
    "sheath_oral": BellyPositionDef(
        key="sheath_oral",
        name="Sheath Service",
        carrier_sex="male",
        passenger_orientation="horizontal",
        passenger_facing="forward",
        exposes=["rear", "back"],
        accessible_to_carrier=["face", "mouth"],
        involves_oral=True,
        oral_target="sheath",
        movement_effect="thrust_per_step",
        entry_desc="{passenger}'s face is positioned at {carrier}'s sheath",
        ongoing_desc="{passenger} services {carrier} orally from the belly sling",
        movement_desc="Each step pushes {carrier}'s length into {passenger}'s mouth",
    ),
    "udder_mount": BellyPositionDef(
        key="udder_mount",
        name="Udder Mount",
        carrier_sex="female",
        passenger_orientation="horizontal",
        passenger_facing="up",
        exposes=["back", "rear"],
        accessible_to_carrier=["face", "mouth"],
        involves_oral=True,
        oral_target="udders",
        movement_effect="sway",
        entry_desc="{passenger}'s face is pressed into {carrier}'s udders",
        ongoing_desc="{passenger} nurses from {carrier}'s swaying udders",
        movement_desc="The motion presses udders against {passenger}'s face",
    ),
    "breeding_slung": BellyPositionDef(
        key="breeding_slung",
        name="Breeding Slung",
        passenger_orientation="horizontal",
        passenger_facing="down",
        exposes=["rear", "genitals"],
        accessible_to_carrier=[],
        movement_effect="bounce",
        entry_desc="{passenger} is suspended with rear exposed for breeding",
        ongoing_desc="{passenger} hangs helplessly, rear exposed and accessible to anyone behind {carrier}",
        movement_desc="{passenger} bounces in the sling, exposed rear an invitation",
    ),
    "inverted": BellyPositionDef(
        key="inverted",
        name="Inverted",
        passenger_orientation="inverted",
        passenger_facing="down",
        exposes=["face", "chest", "genitals"],
        accessible_to_carrier=["genitals", "rear"],
        movement_effect="swing",
        entry_desc="{passenger} is suspended upside-down beneath {carrier}",
        ongoing_desc="{passenger} hangs inverted, blood rushing to their head",
        movement_desc="{passenger} swings helplessly with each step",
    ),
}


def get_belly_position(key: str) -> Optional[BellyPositionDef]:
    """Get belly position by key."""
    return BELLY_POSITIONS.get(key)


# =============================================================================
# SADDLE BLANKET (CONCEALMENT)
# =============================================================================

@dataclass
class SaddleBlanket:
    """A blanket for concealing belly-mounted passengers."""
    key: str = "saddle_blanket"
    name: str = "Saddle Blanket"
    
    # Properties
    coverage: str = "full"          # full, partial, decorative
    material: str = "wool"
    color: str = "brown"
    
    # State
    is_lifted: bool = False
    
    # Concealment bonus
    concealment_bonus: int = 30     # Added to concealment checks
    
    def lift(self) -> str:
        """Lift the blanket to reveal what's beneath."""
        self.is_lifted = True
        return "The blanket is lifted, revealing what's hidden beneath..."
    
    def drop(self) -> str:
        """Let the blanket fall back into place."""
        self.is_lifted = False
        return "The blanket falls back into place, concealing everything."
    
    def get_concealment_modifier(self) -> int:
        """Get concealment modifier."""
        if self.is_lifted:
            return -100  # Everything visible
        return self.concealment_bonus
    
    def to_dict(self) -> dict:
        return {
            "key": self.key,
            "name": self.name,
            "coverage": self.coverage,
            "material": self.material,
            "color": self.color,
            "is_lifted": self.is_lifted,
            "concealment_bonus": self.concealment_bonus,
        }
    
    @classmethod
    def from_dict(cls, data: dict) -> "SaddleBlanket":
        blanket = cls()
        blanket.key = data.get("key", "saddle_blanket")
        blanket.name = data.get("name", "Saddle Blanket")
        blanket.coverage = data.get("coverage", "full")
        blanket.material = data.get("material", "wool")
        blanket.color = data.get("color", "brown")
        blanket.is_lifted = data.get("is_lifted", False)
        blanket.concealment_bonus = data.get("concealment_bonus", 30)
        return blanket


# =============================================================================
# BELLY MOUNT STATE
# =============================================================================

@dataclass
class BellyMountState:
    """Tracks the state of a belly mount."""
    # Participants
    carrier_dbref: str = ""
    carrier_name: str = ""
    passenger_dbref: str = ""
    passenger_name: str = ""
    
    # Position
    position: str = "belly_slung"
    
    # Carrier state
    gait: CarrierGait = CarrierGait.STANDING
    
    # Concealment
    blanket: Optional[SaddleBlanket] = None
    
    # State
    is_active: bool = False
    is_locked: bool = False
    
    # Stats
    ticks_mounted: int = 0
    arousal_buildup: int = 0
    
    @property
    def position_def(self) -> Optional[BellyPositionDef]:
        """Get position definition."""
        return get_belly_position(self.position)
    
    @property
    def gait_effects(self) -> dict:
        """Get current gait effects."""
        return GAIT_EFFECTS.get(self.gait, GAIT_EFFECTS[CarrierGait.STANDING])
    
    def set_gait(self, gait: CarrierGait) -> str:
        """Change carrier's gait."""
        old_gait = self.gait
        self.gait = gait
        
        effects = self.gait_effects
        desc = effects["description"].format(
            carrier=self.carrier_name,
            passenger=self.passenger_name,
        )
        
        if self.is_active and gait != CarrierGait.STANDING:
            passenger_effect = effects["passenger_effect"].format(
                carrier=self.carrier_name,
                passenger=self.passenger_name,
            )
            return f"{desc}. {passenger_effect}"
        
        return desc
    
    def get_concealment_level(self) -> ConcealmentLevel:
        """Calculate current concealment level."""
        pos_def = self.position_def
        if not pos_def:
            return ConcealmentLevel.EXPOSED
        
        if not pos_def.can_be_concealed:
            return ConcealmentLevel.EXPOSED
        
        # Start with base concealment
        base = pos_def.base_concealment
        
        # Blanket bonus
        if self.blanket and not self.blanket.is_lifted:
            # Blanket significantly helps
            if base == ConcealmentLevel.EXPOSED:
                return ConcealmentLevel.CONCEALED
            elif base == ConcealmentLevel.PARTIAL:
                return ConcealmentLevel.HIDDEN
        
        return base
    
    def check_noticed(self, observer_perception: int = 10, attention: str = "casual") -> Tuple[bool, str]:
        """
        Check if an observer notices the hidden passenger.
        
        Args:
            observer_perception: Observer's perception stat
            attention: Level of attention (casual, looking, searching, intimate)
            
        Returns:
            (noticed: bool, description: str)
        """
        # Blanket lifted = obvious
        if self.blanket and self.blanket.is_lifted:
            return True, "The lifted blanket reveals everything."
        
        # Base DC to notice
        base_dc = 15
        
        # Blanket coverage
        if self.blanket:
            base_dc += self.blanket.get_concealment_modifier()
        else:
            base_dc -= 20  # No concealment
        
        # Gait modifiers (movement makes it harder to hide)
        gait_mods = {
            CarrierGait.STANDING: 0,
            CarrierGait.WALKING: -5,
            CarrierGait.TROTTING: -10,
            CarrierGait.CANTERING: -15,
            CarrierGait.GALLOPING: -20,
        }
        base_dc += gait_mods.get(self.gait, 0)
        
        # Arousal makes noise
        if self.arousal_buildup > 70:
            base_dc -= 15  # Moaning
        elif self.arousal_buildup > 40:
            base_dc -= 5   # Breathing hard
        
        # Attention modifiers
        attention_mods = {
            "casual": 0,
            "looking": -10,
            "searching": -20,
            "intimate": -30,
        }
        base_dc += attention_mods.get(attention, 0)
        
        # Roll
        roll = random.randint(1, 20) + observer_perception
        
        if roll >= base_dc:
            if roll >= base_dc + 10:
                return True, f"clearly sees {self.passenger_name} suspended beneath"
            else:
                return True, "notices suspicious movement under the blanket"
        
        return False, "notices nothing unusual"
    
    def tick(self) -> List[str]:
        """Process a tick of being mounted. Returns messages."""
        if not self.is_active:
            return []
        
        messages = []
        self.ticks_mounted += 1
        
        effects = self.gait_effects
        
        # Arousal buildup from movement
        intensity = effects["intensity"]
        thrust_freq = effects["thrust_frequency"]
        
        if intensity > 0:
            arousal_gain = int(intensity * 10) + thrust_freq * 2
            self.arousal_buildup = min(100, self.arousal_buildup + arousal_gain)
            
            # Generate description at certain thresholds
            pos_def = self.position_def
            if pos_def and pos_def.movement_desc:
                if self.ticks_mounted % 5 == 0:  # Every 5 ticks
                    msg = pos_def.movement_desc.format(
                        carrier=self.carrier_name,
                        passenger=self.passenger_name,
                    )
                    messages.append(msg)
            
            # High arousal messages
            if self.arousal_buildup >= 90:
                messages.append(f"{self.passenger_name} is on the edge, barely containing their moans.")
            elif self.arousal_buildup >= 70:
                messages.append(f"{self.passenger_name} whimpers with each movement.")
        
        return messages
    
    def to_dict(self) -> dict:
        return {
            "carrier_dbref": self.carrier_dbref,
            "carrier_name": self.carrier_name,
            "passenger_dbref": self.passenger_dbref,
            "passenger_name": self.passenger_name,
            "position": self.position,
            "gait": self.gait.value,
            "blanket": self.blanket.to_dict() if self.blanket else None,
            "is_active": self.is_active,
            "is_locked": self.is_locked,
            "ticks_mounted": self.ticks_mounted,
            "arousal_buildup": self.arousal_buildup,
        }
    
    @classmethod
    def from_dict(cls, data: dict) -> "BellyMountState":
        state = cls()
        state.carrier_dbref = data.get("carrier_dbref", "")
        state.carrier_name = data.get("carrier_name", "")
        state.passenger_dbref = data.get("passenger_dbref", "")
        state.passenger_name = data.get("passenger_name", "")
        state.position = data.get("position", "belly_slung")
        state.gait = CarrierGait(data.get("gait", "standing"))
        
        if data.get("blanket"):
            state.blanket = SaddleBlanket.from_dict(data["blanket"])
        
        state.is_active = data.get("is_active", False)
        state.is_locked = data.get("is_locked", False)
        state.ticks_mounted = data.get("ticks_mounted", 0)
        state.arousal_buildup = data.get("arousal_buildup", 0)
        
        return state


# =============================================================================
# BELLY MOUNT SYSTEM
# =============================================================================

class BellyMountSystem:
    """
    Manages belly mounting operations.
    """
    
    @staticmethod
    def can_be_carrier(character) -> Tuple[bool, str]:
        """Check if character can carry someone in a belly sling."""
        structure = getattr(character, 'body_structure', None)
        
        valid_structures = ["tauroid", "quadruped"]
        
        if structure and structure.lower() in valid_structures:
            return True, ""
        
        return False, "Only tauroid or quadruped characters can carry belly passengers."
    
    @staticmethod
    def can_mount(carrier, passenger, position: str = "belly_slung") -> Tuple[bool, str]:
        """Check if passenger can be mounted to carrier."""
        # Check carrier eligibility
        can_carry, reason = BellyMountSystem.can_be_carrier(carrier)
        if not can_carry:
            return False, reason
        
        # Check if carrier already has passenger
        existing = getattr(carrier, 'belly_mount_state', None)
        if existing and existing.is_active:
            return False, f"{carrier.key} already has a belly passenger."
        
        # Check position requirements
        pos_def = get_belly_position(position)
        if not pos_def:
            return False, f"Unknown position: {position}"
        
        # Check sex requirements
        if pos_def.carrier_sex != "any":
            carrier_sex = getattr(carrier, 'sex', 'any')
            if carrier_sex != pos_def.carrier_sex:
                return False, f"Position {pos_def.name} requires a {pos_def.carrier_sex} carrier."
        
        # Check harness/sling
        harness = getattr(carrier, 'worn_harness', None)
        if not harness or harness.harness_type.value != "belly_sling":
            return False, f"{carrier.key} needs a belly sling equipped."
        
        return True, ""
    
    @staticmethod
    def mount_passenger(carrier, passenger, position: str = "belly_slung") -> Tuple[bool, str]:
        """Mount a passenger beneath the carrier."""
        can_mount, reason = BellyMountSystem.can_mount(carrier, passenger, position)
        if not can_mount:
            return False, reason
        
        pos_def = get_belly_position(position)
        
        # Create mount state
        state = BellyMountState(
            carrier_dbref=carrier.dbref,
            carrier_name=carrier.key,
            passenger_dbref=passenger.dbref,
            passenger_name=passenger.key,
            position=position,
            is_active=True,
        )
        
        # Store state on both characters
        carrier.attributes.add("belly_mount_state", state.to_dict())
        passenger.attributes.add("belly_mounted_to", carrier.dbref)
        
        # Entry description
        desc = pos_def.entry_desc.format(
            carrier=carrier.key,
            passenger=passenger.key,
        )
        
        return True, desc
    
    @staticmethod
    def unmount_passenger(carrier, force: bool = False) -> Tuple[bool, str]:
        """Remove passenger from belly sling."""
        state_data = carrier.attributes.get("belly_mount_state")
        if not state_data:
            return False, "No belly passenger."
        
        state = BellyMountState.from_dict(state_data)
        
        if not state.is_active:
            return False, "No active belly mount."
        
        if state.is_locked and not force:
            return False, "The sling is locked! Cannot remove passenger."
        
        # Clear state
        state.is_active = False
        carrier.attributes.add("belly_mount_state", state.to_dict())
        
        # Clear passenger reference
        # Would need to look up passenger by dbref in real implementation
        
        return True, f"{state.passenger_name} is released from the belly sling."
    
    @staticmethod
    def change_position(carrier, new_position: str) -> Tuple[bool, str]:
        """Change passenger's position in the sling."""
        state_data = carrier.attributes.get("belly_mount_state")
        if not state_data:
            return False, "No belly passenger."
        
        state = BellyMountState.from_dict(state_data)
        
        if not state.is_active:
            return False, "No active belly mount."
        
        pos_def = get_belly_position(new_position)
        if not pos_def:
            return False, f"Unknown position: {new_position}"
        
        # Check sex requirements for new position
        if pos_def.carrier_sex != "any":
            carrier_sex = getattr(carrier, 'sex', 'any')
            if carrier_sex != pos_def.carrier_sex:
                return False, f"Position {pos_def.name} requires a {pos_def.carrier_sex} carrier."
        
        old_pos = state.position
        state.position = new_position
        carrier.attributes.add("belly_mount_state", state.to_dict())
        
        desc = pos_def.entry_desc.format(
            carrier=state.carrier_name,
            passenger=state.passenger_name,
        )
        
        return True, f"Position changed from {old_pos} to {new_position}. {desc}"
    
    @staticmethod
    def change_gait(carrier, gait: CarrierGait) -> str:
        """Change carrier's gait."""
        state_data = carrier.attributes.get("belly_mount_state")
        
        if state_data:
            state = BellyMountState.from_dict(state_data)
            result = state.set_gait(gait)
            carrier.attributes.add("belly_mount_state", state.to_dict())
            return result
        
        # No passenger, just change gait description
        effects = GAIT_EFFECTS.get(gait, GAIT_EFFECTS[CarrierGait.STANDING])
        return effects["description"].format(carrier=carrier.key, passenger="")
    
    @staticmethod
    def apply_blanket(carrier, blanket: SaddleBlanket) -> str:
        """Apply a saddle blanket for concealment."""
        state_data = carrier.attributes.get("belly_mount_state")
        
        if state_data:
            state = BellyMountState.from_dict(state_data)
            state.blanket = blanket
            carrier.attributes.add("belly_mount_state", state.to_dict())
            
            if state.is_active:
                return f"The {blanket.name} drapes over {carrier.key}, concealing {state.passenger_name} from view."
        
        return f"The {blanket.name} is draped over {carrier.key}."
    
    @staticmethod
    def lift_blanket(carrier) -> str:
        """Lift the saddle blanket."""
        state_data = carrier.attributes.get("belly_mount_state")
        
        if not state_data:
            return "Nothing to reveal."
        
        state = BellyMountState.from_dict(state_data)
        
        if not state.blanket:
            return "No blanket to lift."
        
        result = state.blanket.lift()
        carrier.attributes.add("belly_mount_state", state.to_dict())
        
        if state.is_active:
            pos_def = state.position_def
            ongoing = pos_def.ongoing_desc.format(
                carrier=state.carrier_name,
                passenger=state.passenger_name,
            ) if pos_def else ""
            return f"{result} {ongoing}"
        
        return result
    
    @staticmethod
    def drop_blanket(carrier) -> str:
        """Drop the saddle blanket back down."""
        state_data = carrier.attributes.get("belly_mount_state")
        
        if not state_data:
            return "No blanket."
        
        state = BellyMountState.from_dict(state_data)
        
        if not state.blanket:
            return "No blanket."
        
        result = state.blanket.drop()
        carrier.attributes.add("belly_mount_state", state.to_dict())
        
        return result


# =============================================================================
# BELLY MOUNT MIXIN
# =============================================================================

class BellyMountCarrierMixin:
    """
    Mixin for characters that can carry belly passengers.
    """
    
    @property
    def belly_mount_state(self) -> Optional[BellyMountState]:
        """Get belly mount state."""
        data = self.attributes.get("belly_mount_state")
        if data:
            return BellyMountState.from_dict(data)
        return None
    
    def has_belly_passenger(self) -> bool:
        """Check if carrying a belly passenger."""
        state = self.belly_mount_state
        return state is not None and state.is_active
    
    def get_belly_passenger_desc(self) -> str:
        """Get description of belly passenger for room desc."""
        state = self.belly_mount_state
        if not state or not state.is_active:
            return ""
        
        concealment = state.get_concealment_level()
        
        if concealment == ConcealmentLevel.HIDDEN:
            return ""  # Don't mention at all
        elif concealment == ConcealmentLevel.CONCEALED:
            return "A saddle blanket drapes over their lower half."
        elif concealment == ConcealmentLevel.PARTIAL:
            return "Something seems to be suspended beneath them."
        else:
            pos_def = state.position_def
            if pos_def:
                return pos_def.ongoing_desc.format(
                    carrier=state.carrier_name,
                    passenger=state.passenger_name,
                )
            return f"{state.passenger_name} hangs in a sling beneath them."


class BellyMountPassengerMixin:
    """
    Mixin for characters that can be belly passengers.
    """
    
    @property
    def belly_mounted_to(self) -> str:
        """Get dbref of carrier if belly mounted."""
        return self.attributes.get("belly_mounted_to", "")
    
    def is_belly_mounted(self) -> bool:
        """Check if currently mounted to someone's belly."""
        return bool(self.belly_mounted_to)


__all__ = [
    "BellyMountPosition",
    "CarrierGait",
    "ConcealmentLevel",
    "GAIT_EFFECTS",
    "BellyPositionDef",
    "BELLY_POSITIONS",
    "get_belly_position",
    "SaddleBlanket",
    "BellyMountState",
    "BellyMountSystem",
    "BellyMountCarrierMixin",
    "BellyMountPassengerMixin",
]
