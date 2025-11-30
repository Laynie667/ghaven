"""
Grappling System
================

Non-lethal combat and restraint:
- Grappling and holds
- Pins and positions
- Escape mechanics
- Struggle system
"""

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any, Tuple
from enum import Enum
from datetime import datetime
import random


# =============================================================================
# ENUMS
# =============================================================================

class GrappleState(Enum):
    """States of a grapple."""
    NONE = "none"
    CLINCH = "clinch"           # Standing grapple
    TAKEDOWN = "takedown"       # Taking to ground
    MOUNT = "mount"             # On top
    GUARD = "guard"             # On bottom but legs wrapped
    SIDE_CONTROL = "side_control"
    BACK_CONTROL = "back_control"
    PINNED = "pinned"           # Fully controlled
    SUBMISSION = "submission"    # In a submission hold


class HoldType(Enum):
    """Types of holds."""
    WRIST_GRAB = "wrist_grab"
    ARM_LOCK = "arm_lock"
    HEADLOCK = "headlock"
    CHOKE = "choke"
    LEG_LOCK = "leg_lock"
    FULL_NELSON = "full_nelson"
    BEAR_HUG = "bear_hug"
    PIN = "pin"
    MOUNT = "mount"
    SPREAD_EAGLE = "spread_eagle"


class StruggleResult(Enum):
    """Results of a struggle attempt."""
    ESCAPE = "escape"
    PARTIAL = "partial"         # Improved position
    FAILED = "failed"
    EXHAUSTED = "exhausted"     # Failed and lost stamina


# =============================================================================
# HOLD
# =============================================================================

@dataclass
class Hold:
    """A restraining hold."""
    hold_type: HoldType
    name: str
    
    # Difficulty
    escape_dc: int = 50         # Base DC to escape
    maintain_dc: int = 30       # DC to maintain
    
    # Effects
    restricts_arms: bool = False
    restricts_legs: bool = False
    restricts_speech: bool = False
    causes_pain: bool = False
    causes_arousal: bool = False
    
    # Requirements
    requires_strength: int = 0
    requires_position: Optional[GrappleState] = None
    
    # Description
    apply_message: str = ""
    maintain_message: str = ""
    escape_message: str = ""
    
    def to_dict(self) -> dict:
        return {
            "hold_type": self.hold_type.value,
            "name": self.name,
            "escape_dc": self.escape_dc,
            "maintain_dc": self.maintain_dc,
            "restricts_arms": self.restricts_arms,
            "restricts_legs": self.restricts_legs,
            "restricts_speech": self.restricts_speech,
            "causes_pain": self.causes_pain,
            "causes_arousal": self.causes_arousal,
            "requires_strength": self.requires_strength,
            "requires_position": self.requires_position.value if self.requires_position else None,
            "apply_message": self.apply_message,
            "maintain_message": self.maintain_message,
            "escape_message": self.escape_message,
        }


# Predefined holds
HOLD_WRIST_GRAB = Hold(
    hold_type=HoldType.WRIST_GRAB,
    name="Wrist Grab",
    escape_dc=30,
    maintain_dc=20,
    restricts_arms=True,
    apply_message="{attacker} grabs {defender}'s wrists firmly.",
    maintain_message="{attacker} keeps a grip on {defender}'s wrists.",
    escape_message="{defender} wrenches free of the grip!",
)

HOLD_ARM_LOCK = Hold(
    hold_type=HoldType.ARM_LOCK,
    name="Arm Lock",
    escape_dc=50,
    maintain_dc=35,
    restricts_arms=True,
    causes_pain=True,
    apply_message="{attacker} twists {defender}'s arm behind their back!",
    maintain_message="{attacker} keeps {defender}'s arm painfully twisted.",
    escape_message="{defender} slips out of the arm lock!",
)

HOLD_HEADLOCK = Hold(
    hold_type=HoldType.HEADLOCK,
    name="Headlock",
    escape_dc=45,
    maintain_dc=30,
    restricts_speech=True,
    apply_message="{attacker} wraps an arm around {defender}'s neck in a headlock!",
    maintain_message="{attacker} keeps {defender} locked in the headlock.",
    escape_message="{defender} ducks out of the headlock!",
)

HOLD_BEAR_HUG = Hold(
    hold_type=HoldType.BEAR_HUG,
    name="Bear Hug",
    escape_dc=55,
    maintain_dc=40,
    restricts_arms=True,
    requires_strength=30,
    apply_message="{attacker} wraps powerful arms around {defender} in a crushing bear hug!",
    maintain_message="{attacker} squeezes {defender} tightly.",
    escape_message="{defender} wiggles free of the bear hug!",
)

HOLD_FULL_NELSON = Hold(
    hold_type=HoldType.FULL_NELSON,
    name="Full Nelson",
    escape_dc=60,
    maintain_dc=45,
    restricts_arms=True,
    requires_position=GrappleState.BACK_CONTROL,
    apply_message="{attacker} locks {defender} in a full nelson, arms completely immobilized!",
    maintain_message="{attacker} keeps {defender} helplessly locked.",
    escape_message="{defender} manages to break the full nelson!",
)

HOLD_PIN = Hold(
    hold_type=HoldType.PIN,
    name="Pin",
    escape_dc=55,
    maintain_dc=40,
    restricts_arms=True,
    restricts_legs=True,
    requires_position=GrappleState.MOUNT,
    apply_message="{attacker} pins {defender} to the ground!",
    maintain_message="{attacker} keeps {defender} pinned beneath them.",
    escape_message="{defender} bucks {attacker} off!",
)

HOLD_MOUNT = Hold(
    hold_type=HoldType.MOUNT,
    name="Mounted Pin",
    escape_dc=60,
    maintain_dc=45,
    restricts_legs=True,
    causes_arousal=True,
    requires_position=GrappleState.MOUNT,
    apply_message="{attacker} straddles {defender}, pinning them beneath their weight!",
    maintain_message="{attacker} keeps {defender} pinned beneath them.",
    escape_message="{defender} rolls and escapes the mount!",
)

HOLD_SPREAD_EAGLE = Hold(
    hold_type=HoldType.SPREAD_EAGLE,
    name="Spread Eagle Pin",
    escape_dc=70,
    maintain_dc=55,
    restricts_arms=True,
    restricts_legs=True,
    causes_arousal=True,
    requires_position=GrappleState.MOUNT,
    apply_message="{attacker} forces {defender}'s arms above their head and spreads their legs wide!",
    maintain_message="{attacker} keeps {defender} helplessly spread.",
    escape_message="{defender} twists free despite their vulnerable position!",
)

ALL_HOLDS: Dict[str, Hold] = {
    "wrist_grab": HOLD_WRIST_GRAB,
    "arm_lock": HOLD_ARM_LOCK,
    "headlock": HOLD_HEADLOCK,
    "bear_hug": HOLD_BEAR_HUG,
    "full_nelson": HOLD_FULL_NELSON,
    "pin": HOLD_PIN,
    "mount": HOLD_MOUNT,
    "spread_eagle": HOLD_SPREAD_EAGLE,
}


# =============================================================================
# GRAPPLE STATE
# =============================================================================

@dataclass
class GrappleInstance:
    """An active grapple between two characters."""
    grapple_id: str
    
    # Participants
    attacker_dbref: str = ""
    attacker_name: str = ""
    defender_dbref: str = ""
    defender_name: str = ""
    
    # State
    grapple_state: GrappleState = GrappleState.CLINCH
    active_hold: Optional[Hold] = None
    
    # Control (who's winning)
    # Positive = attacker advantage, Negative = defender advantage
    control: int = 0
    
    # Stamina
    attacker_stamina: int = 100
    defender_stamina: int = 100
    
    # Timing
    started_at: Optional[datetime] = None
    rounds: int = 0
    
    def apply_hold(self, hold: Hold) -> str:
        """Apply a hold."""
        self.active_hold = hold
        return hold.apply_message.format(
            attacker=self.attacker_name,
            defender=self.defender_name,
        )
    
    def release_hold(self) -> str:
        """Release the current hold."""
        if not self.active_hold:
            return ""
        
        hold_name = self.active_hold.name
        self.active_hold = None
        return f"{self.attacker_name} releases the {hold_name}."
    
    def attempt_escape(self, defender_strength: int = 50, defender_skill: int = 50) -> Tuple[StruggleResult, str]:
        """
        Defender attempts to escape.
        Returns (result, message).
        """
        if not self.active_hold:
            return StruggleResult.ESCAPE, f"{self.defender_name} is already free!"
        
        # Calculate escape chance
        escape_dc = self.active_hold.escape_dc
        
        # Modifiers
        escape_dc += self.control  # Higher control makes escape harder
        escape_dc -= (defender_strength - 50) // 2  # Strength helps
        escape_dc -= (defender_skill - 50) // 2  # Skill helps
        
        # Stamina affects chances
        stamina_penalty = (100 - self.defender_stamina) // 4
        escape_dc += stamina_penalty
        
        # Roll
        roll = random.randint(1, 100)
        
        # Cost stamina either way
        stamina_cost = random.randint(5, 15)
        self.defender_stamina = max(0, self.defender_stamina - stamina_cost)
        
        if self.defender_stamina <= 0:
            return StruggleResult.EXHAUSTED, f"{self.defender_name} is too exhausted to struggle!"
        
        if roll >= escape_dc:
            # Success!
            message = self.active_hold.escape_message.format(
                attacker=self.attacker_name,
                defender=self.defender_name,
            )
            self.active_hold = None
            self.control = max(-50, self.control - 20)
            
            # Check if fully escaped
            if self.control <= -30:
                self.grapple_state = GrappleState.NONE
                return StruggleResult.ESCAPE, f"{message} {self.defender_name} breaks free entirely!"
            
            return StruggleResult.PARTIAL, message
        
        elif roll >= escape_dc - 20:
            # Partial - improved position
            self.control = max(-50, self.control - 5)
            return StruggleResult.PARTIAL, f"{self.defender_name} struggles but can't escape!"
        
        else:
            # Failed
            self.control = min(50, self.control + 5)  # Attacker gains control
            return StruggleResult.FAILED, f"{self.defender_name}'s struggle is futile!"
    
    def maintain_hold(self, attacker_strength: int = 50) -> Tuple[bool, str]:
        """
        Attacker attempts to maintain hold.
        Returns (success, message).
        """
        if not self.active_hold:
            return True, ""
        
        maintain_dc = self.active_hold.maintain_dc
        maintain_dc -= (attacker_strength - 50) // 2
        maintain_dc -= self.control // 2
        
        # Stamina
        stamina_cost = random.randint(3, 8)
        self.attacker_stamina = max(0, self.attacker_stamina - stamina_cost)
        
        roll = random.randint(1, 100)
        
        if roll >= maintain_dc:
            return True, self.active_hold.maintain_message.format(
                attacker=self.attacker_name,
                defender=self.defender_name,
            )
        else:
            # Lost hold
            hold_name = self.active_hold.name
            self.active_hold = None
            self.control = max(-50, self.control - 15)
            return False, f"{self.attacker_name} loses their grip on the {hold_name}!"
    
    def advance_position(self, target_state: GrappleState) -> Tuple[bool, str]:
        """Attacker attempts to advance position."""
        # Transition costs
        transitions = {
            (GrappleState.CLINCH, GrappleState.TAKEDOWN): 40,
            (GrappleState.TAKEDOWN, GrappleState.MOUNT): 45,
            (GrappleState.TAKEDOWN, GrappleState.SIDE_CONTROL): 35,
            (GrappleState.SIDE_CONTROL, GrappleState.MOUNT): 40,
            (GrappleState.MOUNT, GrappleState.BACK_CONTROL): 50,
            (GrappleState.MOUNT, GrappleState.PINNED): 55,
        }
        
        transition = (self.grapple_state, target_state)
        if transition not in transitions:
            return False, "Can't transition to that position from here."
        
        dc = transitions[transition]
        dc -= self.control // 2
        
        roll = random.randint(1, 100)
        
        if roll >= dc:
            old_state = self.grapple_state
            self.grapple_state = target_state
            self.control = min(50, self.control + 10)
            return True, f"{self.attacker_name} advances from {old_state.value} to {target_state.value}!"
        
        return False, f"{self.attacker_name} fails to advance position."
    
    def get_status(self) -> str:
        """Get grapple status."""
        lines = [
            f"=== Grapple: {self.attacker_name} vs {self.defender_name} ===",
            f"Position: {self.grapple_state.value}",
            f"Control: {self.control:+d} ({'attacker' if self.control > 0 else 'defender'} advantage)",
        ]
        
        if self.active_hold:
            lines.append(f"Hold: {self.active_hold.name}")
        
        lines.append(f"Stamina: {self.attacker_name}: {self.attacker_stamina}%, {self.defender_name}: {self.defender_stamina}%")
        
        return "\n".join(lines)
    
    def to_dict(self) -> dict:
        return {
            "grapple_id": self.grapple_id,
            "attacker_dbref": self.attacker_dbref,
            "attacker_name": self.attacker_name,
            "defender_dbref": self.defender_dbref,
            "defender_name": self.defender_name,
            "grapple_state": self.grapple_state.value,
            "active_hold": self.active_hold.to_dict() if self.active_hold else None,
            "control": self.control,
            "attacker_stamina": self.attacker_stamina,
            "defender_stamina": self.defender_stamina,
            "started_at": self.started_at.isoformat() if self.started_at else None,
            "rounds": self.rounds,
        }
    
    @classmethod
    def from_dict(cls, data: dict) -> "GrappleInstance":
        grapple = cls(grapple_id=data["grapple_id"])
        grapple.attacker_dbref = data.get("attacker_dbref", "")
        grapple.attacker_name = data.get("attacker_name", "")
        grapple.defender_dbref = data.get("defender_dbref", "")
        grapple.defender_name = data.get("defender_name", "")
        grapple.grapple_state = GrappleState(data.get("grapple_state", "clinch"))
        grapple.control = data.get("control", 0)
        grapple.attacker_stamina = data.get("attacker_stamina", 100)
        grapple.defender_stamina = data.get("defender_stamina", 100)
        grapple.rounds = data.get("rounds", 0)
        
        if data.get("started_at"):
            grapple.started_at = datetime.fromisoformat(data["started_at"])
        
        # Rebuild hold from type
        if data.get("active_hold"):
            hold_type = data["active_hold"].get("hold_type")
            if hold_type in ALL_HOLDS:
                grapple.active_hold = ALL_HOLDS[hold_type]
        
        return grapple


# =============================================================================
# GRAPPLE SYSTEM
# =============================================================================

class GrappleSystem:
    """
    Manages grappling combat.
    """
    
    @staticmethod
    def generate_id() -> str:
        """Generate unique ID."""
        timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
        rand = random.randint(1000, 9999)
        return f"GRP-{timestamp}-{rand}"
    
    @staticmethod
    def initiate_grapple(
        attacker,
        defender,
        attacker_strength: int = 50,
        defender_strength: int = 50,
    ) -> Tuple[bool, str, Optional[GrappleInstance]]:
        """
        Initiate a grapple.
        Returns (success, message, grapple).
        """
        # Check if defender is already grappled
        if hasattr(defender, 'current_grapple') and defender.current_grapple:
            return False, f"{defender.key} is already in a grapple!", None
        
        # Opposed check
        attacker_roll = random.randint(1, 100) + (attacker_strength - 50) // 2
        defender_roll = random.randint(1, 100) + (defender_strength - 50) // 2
        
        if attacker_roll > defender_roll:
            # Success
            grapple = GrappleInstance(
                grapple_id=GrappleSystem.generate_id(),
                attacker_dbref=attacker.dbref,
                attacker_name=attacker.key,
                defender_dbref=defender.dbref,
                defender_name=defender.key,
                grapple_state=GrappleState.CLINCH,
                control=attacker_roll - defender_roll,
                started_at=datetime.now(),
            )
            
            return True, f"{attacker.key} grabs {defender.key} and pulls them into a clinch!", grapple
        
        else:
            return False, f"{defender.key} shrugs off {attacker.key}'s grapple attempt!", None
    
    @staticmethod
    def end_grapple(grapple: GrappleInstance) -> str:
        """End a grapple."""
        return f"The grapple between {grapple.attacker_name} and {grapple.defender_name} ends."


# =============================================================================
# GRAPPLE MIXIN
# =============================================================================

class GrappleMixin:
    """
    Mixin for characters that can grapple.
    """
    
    @property
    def current_grapple(self) -> Optional[GrappleInstance]:
        """Get current grapple."""
        data = self.attributes.get("current_grapple")
        if data:
            return GrappleInstance.from_dict(data)
        return None
    
    @current_grapple.setter
    def current_grapple(self, grapple: Optional[GrappleInstance]):
        """Set current grapple."""
        if grapple:
            self.attributes.add("current_grapple", grapple.to_dict())
        else:
            self.attributes.remove("current_grapple")
    
    def is_grappling(self) -> bool:
        """Check if in a grapple."""
        return self.current_grapple is not None
    
    def is_pinned(self) -> bool:
        """Check if pinned."""
        grapple = self.current_grapple
        if not grapple:
            return False
        return grapple.grapple_state == GrappleState.PINNED and grapple.defender_dbref == self.dbref
    
    @property
    def grapple_strength(self) -> int:
        """Get grappling strength."""
        return self.attributes.get("grapple_strength", 50)
    
    @property
    def grapple_skill(self) -> int:
        """Get grappling skill."""
        return self.attributes.get("grapple_skill", 50)


__all__ = [
    "GrappleState",
    "HoldType",
    "StruggleResult",
    "Hold",
    "ALL_HOLDS",
    "GrappleInstance",
    "GrappleSystem",
    "GrappleMixin",
]
