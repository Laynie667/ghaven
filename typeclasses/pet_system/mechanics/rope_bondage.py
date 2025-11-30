"""
Rope Bondage System
===================

Rope and tie-based restraint:
- Tie patterns and positions
- Rope types
- Escape mechanics
- Suspension
"""

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any, Tuple
from enum import Enum
from datetime import datetime
import random


# =============================================================================
# ENUMS
# =============================================================================

class RopeType(Enum):
    """Types of rope materials."""
    HEMP = "hemp"               # Natural, rough
    JUTE = "jute"               # Natural, softer
    COTTON = "cotton"           # Soft, less secure
    SILK = "silk"               # Luxury, low friction
    NYLON = "nylon"             # Synthetic, strong
    CHAIN = "chain"             # Metal, very secure
    LEATHER = "leather"         # Straps


class TiePattern(Enum):
    """Bondage tie patterns."""
    WRISTS_FRONT = "wrists_front"
    WRISTS_BACK = "wrists_back"
    ANKLES = "ankles"
    HOGTIE = "hogtie"
    BOX_TIE = "box_tie"         # Takate-kote style
    SPREAD_EAGLE = "spread_eagle"
    CROTCH_ROPE = "crotch_rope"
    BREAST_HARNESS = "breast_harness"
    FULL_BODY = "full_body"
    SUSPENSION = "suspension"
    FROGTIE = "frogtie"
    ARMBINDER = "armbinder"


class BondagePosition(Enum):
    """Positions for the bound person."""
    STANDING = "standing"
    KNEELING = "kneeling"
    SITTING = "sitting"
    LYING_FACE_UP = "lying_face_up"
    LYING_FACE_DOWN = "lying_face_down"
    BENT_OVER = "bent_over"
    SUSPENDED = "suspended"
    DISPLAYED = "displayed"


# =============================================================================
# ROPE
# =============================================================================

@dataclass
class Rope:
    """A piece of rope."""
    rope_type: RopeType = RopeType.JUTE
    length_meters: float = 8.0
    color: str = "natural"
    
    # Properties
    strength: int = 50          # 0-100
    comfort: int = 50           # 0-100
    escape_modifier: int = 0    # Added to escape DC
    
    def get_properties(self) -> Dict[str, Any]:
        """Get rope properties based on type."""
        properties = {
            RopeType.HEMP: {"strength": 60, "comfort": 30, "escape_mod": 10},
            RopeType.JUTE: {"strength": 55, "comfort": 50, "escape_mod": 5},
            RopeType.COTTON: {"strength": 40, "comfort": 70, "escape_mod": -10},
            RopeType.SILK: {"strength": 35, "comfort": 80, "escape_mod": -15},
            RopeType.NYLON: {"strength": 70, "comfort": 40, "escape_mod": 15},
            RopeType.CHAIN: {"strength": 100, "comfort": 10, "escape_mod": 40},
            RopeType.LEATHER: {"strength": 65, "comfort": 55, "escape_mod": 10},
        }
        return properties.get(self.rope_type, {"strength": 50, "comfort": 50, "escape_mod": 0})
    
    def to_dict(self) -> dict:
        return {
            "rope_type": self.rope_type.value,
            "length_meters": self.length_meters,
            "color": self.color,
        }
    
    @classmethod
    def from_dict(cls, data: dict) -> "Rope":
        return cls(
            rope_type=RopeType(data.get("rope_type", "jute")),
            length_meters=data.get("length_meters", 8.0),
            color=data.get("color", "natural"),
        )


# =============================================================================
# TIE DEFINITION
# =============================================================================

@dataclass
class TieDefinition:
    """Definition of a tie pattern."""
    pattern: TiePattern
    name: str
    
    # Requirements
    rope_length_needed: float = 8.0
    skill_required: int = 0     # 0-100
    time_to_apply: int = 2      # Minutes
    
    # Difficulty
    base_escape_dc: int = 50
    
    # Effects
    restricts_arms: bool = False
    restricts_legs: bool = False
    restricts_movement: bool = False
    exposes_front: bool = False
    exposes_rear: bool = False
    causes_arousal: bool = False
    allows_penetration: bool = False
    
    # Valid positions
    valid_positions: List[BondagePosition] = field(default_factory=list)
    
    # Can be suspended?
    allows_suspension: bool = False
    
    # Description
    description: str = ""
    apply_message: str = ""
    bound_message: str = ""
    
    def get_escape_dc(self, rope: Rope, tier_skill: int = 50) -> int:
        """Calculate escape DC with modifiers."""
        dc = self.base_escape_dc
        
        # Rope modifier
        props = rope.get_properties()
        dc += props.get("escape_mod", 0)
        
        # Tier skill makes it harder to escape
        skill_bonus = (tier_skill - 50) // 2
        dc += skill_bonus
        
        return dc
    
    def to_dict(self) -> dict:
        return {
            "pattern": self.pattern.value,
            "name": self.name,
            "rope_length_needed": self.rope_length_needed,
            "skill_required": self.skill_required,
            "time_to_apply": self.time_to_apply,
            "base_escape_dc": self.base_escape_dc,
            "restricts_arms": self.restricts_arms,
            "restricts_legs": self.restricts_legs,
            "restricts_movement": self.restricts_movement,
            "exposes_front": self.exposes_front,
            "exposes_rear": self.exposes_rear,
            "causes_arousal": self.causes_arousal,
            "allows_penetration": self.allows_penetration,
            "valid_positions": [p.value for p in self.valid_positions],
            "allows_suspension": self.allows_suspension,
            "description": self.description,
            "apply_message": self.apply_message,
            "bound_message": self.bound_message,
        }


# Predefined ties
TIE_WRISTS_FRONT = TieDefinition(
    pattern=TiePattern.WRISTS_FRONT,
    name="Wrists Bound (Front)",
    rope_length_needed=3.0,
    skill_required=10,
    time_to_apply=1,
    base_escape_dc=35,
    restricts_arms=True,
    valid_positions=[BondagePosition.STANDING, BondagePosition.KNEELING, 
                     BondagePosition.SITTING, BondagePosition.LYING_FACE_UP],
    description="Wrists bound together in front.",
    apply_message="{tier} binds {subject}'s wrists together in front of them.",
    bound_message="with wrists bound in front",
)

TIE_WRISTS_BACK = TieDefinition(
    pattern=TiePattern.WRISTS_BACK,
    name="Wrists Bound (Behind)",
    rope_length_needed=3.0,
    skill_required=15,
    time_to_apply=1,
    base_escape_dc=45,
    restricts_arms=True,
    valid_positions=[BondagePosition.STANDING, BondagePosition.KNEELING,
                     BondagePosition.BENT_OVER, BondagePosition.LYING_FACE_DOWN],
    description="Wrists bound behind the back.",
    apply_message="{tier} pulls {subject}'s wrists behind their back and binds them.",
    bound_message="with wrists bound behind",
)

TIE_ANKLES = TieDefinition(
    pattern=TiePattern.ANKLES,
    name="Ankles Bound",
    rope_length_needed=3.0,
    skill_required=10,
    time_to_apply=1,
    base_escape_dc=30,
    restricts_legs=True,
    restricts_movement=True,
    valid_positions=[BondagePosition.SITTING, BondagePosition.LYING_FACE_UP,
                     BondagePosition.LYING_FACE_DOWN],
    description="Ankles bound together.",
    apply_message="{tier} binds {subject}'s ankles together.",
    bound_message="with ankles bound",
)

TIE_HOGTIE = TieDefinition(
    pattern=TiePattern.HOGTIE,
    name="Hogtie",
    rope_length_needed=8.0,
    skill_required=30,
    time_to_apply=3,
    base_escape_dc=65,
    restricts_arms=True,
    restricts_legs=True,
    restricts_movement=True,
    exposes_rear=True,
    valid_positions=[BondagePosition.LYING_FACE_DOWN],
    description="Wrists and ankles bound together behind the back.",
    apply_message="{tier} pulls {subject} into a hogtie, connecting wrists to ankles!",
    bound_message="hogtied and helpless",
)

TIE_BOX_TIE = TieDefinition(
    pattern=TiePattern.BOX_TIE,
    name="Box Tie (Takate-kote)",
    rope_length_needed=15.0,
    skill_required=50,
    time_to_apply=5,
    base_escape_dc=70,
    restricts_arms=True,
    exposes_front=True,
    causes_arousal=True,
    allows_suspension=True,
    valid_positions=[BondagePosition.STANDING, BondagePosition.KNEELING,
                     BondagePosition.SUSPENDED],
    description="Arms bound behind in a box pattern, framing the chest.",
    apply_message="{tier} creates an intricate box tie, binding {subject}'s arms behind their back in a beautiful pattern.",
    bound_message="bound in an elegant box tie",
)

TIE_SPREAD_EAGLE = TieDefinition(
    pattern=TiePattern.SPREAD_EAGLE,
    name="Spread Eagle",
    rope_length_needed=12.0,
    skill_required=20,
    time_to_apply=3,
    base_escape_dc=60,
    restricts_arms=True,
    restricts_legs=True,
    restricts_movement=True,
    exposes_front=True,
    exposes_rear=True,
    causes_arousal=True,
    allows_penetration=True,
    valid_positions=[BondagePosition.LYING_FACE_UP, BondagePosition.LYING_FACE_DOWN,
                     BondagePosition.STANDING],
    description="Arms and legs spread wide and bound to anchors.",
    apply_message="{tier} spreads {subject}'s limbs wide and secures them tightly!",
    bound_message="spread-eagled and exposed",
)

TIE_CROTCH_ROPE = TieDefinition(
    pattern=TiePattern.CROTCH_ROPE,
    name="Crotch Rope",
    rope_length_needed=5.0,
    skill_required=25,
    time_to_apply=2,
    base_escape_dc=45,
    restricts_movement=True,
    causes_arousal=True,
    valid_positions=[BondagePosition.STANDING, BondagePosition.KNEELING,
                     BondagePosition.SITTING],
    description="Rope running between the legs.",
    apply_message="{tier} threads rope between {subject}'s legs, pulling it taut.",
    bound_message="with rope running intimately between their legs",
)

TIE_BREAST_HARNESS = TieDefinition(
    pattern=TiePattern.BREAST_HARNESS,
    name="Breast Harness",
    rope_length_needed=8.0,
    skill_required=35,
    time_to_apply=4,
    base_escape_dc=50,
    exposes_front=True,
    causes_arousal=True,
    allows_suspension=True,
    valid_positions=[BondagePosition.STANDING, BondagePosition.KNEELING,
                     BondagePosition.SUSPENDED],
    description="Decorative rope harness framing the chest.",
    apply_message="{tier} weaves rope around {subject}'s chest in an intricate harness.",
    bound_message="wearing a rope breast harness",
)

TIE_FULL_BODY = TieDefinition(
    pattern=TiePattern.FULL_BODY,
    name="Full Body Tie",
    rope_length_needed=30.0,
    skill_required=60,
    time_to_apply=10,
    base_escape_dc=80,
    restricts_arms=True,
    restricts_legs=True,
    restricts_movement=True,
    exposes_front=True,
    exposes_rear=True,
    causes_arousal=True,
    allows_penetration=True,
    allows_suspension=True,
    valid_positions=[BondagePosition.STANDING, BondagePosition.LYING_FACE_UP,
                     BondagePosition.SUSPENDED],
    description="Complete rope bondage covering the entire body.",
    apply_message="{tier} wraps {subject} in rope from shoulders to ankles, creating an intricate full-body bind!",
    bound_message="completely wrapped in rope",
)

TIE_FROGTIE = TieDefinition(
    pattern=TiePattern.FROGTIE,
    name="Frogtie",
    rope_length_needed=10.0,
    skill_required=35,
    time_to_apply=4,
    base_escape_dc=60,
    restricts_legs=True,
    restricts_movement=True,
    exposes_front=True,
    exposes_rear=True,
    allows_penetration=True,
    valid_positions=[BondagePosition.KNEELING, BondagePosition.LYING_FACE_UP,
                     BondagePosition.LYING_FACE_DOWN],
    description="Legs folded and bound in a kneeling position.",
    apply_message="{tier} folds {subject}'s legs and binds ankle to thigh on each side.",
    bound_message="with legs bound in a frogtie",
)

TIE_SUSPENSION = TieDefinition(
    pattern=TiePattern.SUSPENSION,
    name="Suspension Rig",
    rope_length_needed=20.0,
    skill_required=70,
    time_to_apply=8,
    base_escape_dc=85,
    restricts_arms=True,
    restricts_legs=True,
    restricts_movement=True,
    exposes_front=True,
    exposes_rear=True,
    allows_penetration=True,
    allows_suspension=True,
    valid_positions=[BondagePosition.SUSPENDED],
    description="Full suspension bondage.",
    apply_message="{tier} carefully suspends {subject} in an intricate rope harness!",
    bound_message="suspended helplessly in rope",
)


ALL_TIES: Dict[str, TieDefinition] = {
    "wrists_front": TIE_WRISTS_FRONT,
    "wrists_back": TIE_WRISTS_BACK,
    "ankles": TIE_ANKLES,
    "hogtie": TIE_HOGTIE,
    "box_tie": TIE_BOX_TIE,
    "spread_eagle": TIE_SPREAD_EAGLE,
    "crotch_rope": TIE_CROTCH_ROPE,
    "breast_harness": TIE_BREAST_HARNESS,
    "full_body": TIE_FULL_BODY,
    "frogtie": TIE_FROGTIE,
    "suspension": TIE_SUSPENSION,
}


# =============================================================================
# ACTIVE BONDAGE
# =============================================================================

@dataclass
class ActiveBondage:
    """Active bondage on a character."""
    bondage_id: str
    
    # Participants
    tier_dbref: str = ""        # Who tied them
    tier_name: str = ""
    subject_dbref: str = ""
    subject_name: str = ""
    
    # Ties (can have multiple)
    active_ties: List[TiePattern] = field(default_factory=list)
    
    # Rope used
    rope: Optional[Rope] = None
    
    # Position
    position: BondagePosition = BondagePosition.KNEELING
    
    # Anchored to something?
    anchor_dbref: str = ""      # Furniture, pole, etc.
    anchor_name: str = ""
    
    # Tier skill at time of tying
    tier_skill: int = 50
    
    # State
    is_suspended: bool = False
    struggle_count: int = 0
    rope_loosened: int = 0      # 0-100, makes escape easier
    
    # Timing
    tied_at: Optional[datetime] = None
    
    def add_tie(self, pattern: TiePattern) -> str:
        """Add a tie."""
        if pattern not in self.active_ties:
            self.active_ties.append(pattern)
            tie_def = ALL_TIES.get(pattern.value)
            if tie_def:
                return tie_def.apply_message.format(
                    tier=self.tier_name,
                    subject=self.subject_name,
                )
        return ""
    
    def remove_tie(self, pattern: TiePattern) -> str:
        """Remove a tie."""
        if pattern in self.active_ties:
            self.active_ties.remove(pattern)
            tie_def = ALL_TIES.get(pattern.value)
            return f"{self.tier_name} unties the {tie_def.name if tie_def else pattern.value}."
        return ""
    
    def get_total_escape_dc(self) -> int:
        """Calculate total escape DC from all ties."""
        if not self.active_ties:
            return 0
        
        total_dc = 0
        rope = self.rope or Rope()
        
        for pattern in self.active_ties:
            tie_def = ALL_TIES.get(pattern.value)
            if tie_def:
                total_dc += tie_def.get_escape_dc(rope, self.tier_skill)
        
        # Average across ties, with bonus for multiple
        avg_dc = total_dc // len(self.active_ties)
        multi_bonus = (len(self.active_ties) - 1) * 10
        
        # Loosened ropes make escape easier
        final_dc = avg_dc + multi_bonus - self.rope_loosened
        
        return max(10, final_dc)
    
    def attempt_escape(self, subject_strength: int = 50, subject_skill: int = 50) -> Tuple[bool, str]:
        """
        Attempt to escape bondage.
        Returns (success, message).
        """
        if not self.active_ties:
            return True, f"{self.subject_name} is already free!"
        
        self.struggle_count += 1
        escape_dc = self.get_total_escape_dc()
        
        # Calculate escape chance
        roll = random.randint(1, 100)
        modifier = (subject_strength - 50) // 4 + (subject_skill - 50) // 4
        
        if roll + modifier >= escape_dc:
            # Success!
            self.active_ties.clear()
            return True, f"{self.subject_name} wriggles free of the ropes!"
        
        elif roll + modifier >= escape_dc - 20:
            # Partial - loosened ropes
            self.rope_loosened = min(50, self.rope_loosened + random.randint(5, 15))
            return False, f"{self.subject_name} struggles against the ropes, feeling them loosen slightly."
        
        else:
            return False, f"{self.subject_name} struggles uselessly against the ropes."
    
    def is_arms_bound(self) -> bool:
        """Check if arms are restricted."""
        for pattern in self.active_ties:
            tie_def = ALL_TIES.get(pattern.value)
            if tie_def and tie_def.restricts_arms:
                return True
        return False
    
    def is_legs_bound(self) -> bool:
        """Check if legs are restricted."""
        for pattern in self.active_ties:
            tie_def = ALL_TIES.get(pattern.value)
            if tie_def and tie_def.restricts_legs:
                return True
        return False
    
    def is_immobilized(self) -> bool:
        """Check if movement is restricted."""
        for pattern in self.active_ties:
            tie_def = ALL_TIES.get(pattern.value)
            if tie_def and tie_def.restricts_movement:
                return True
        return False
    
    def is_exposed(self) -> Tuple[bool, bool]:
        """Check exposure. Returns (front_exposed, rear_exposed)."""
        front = False
        rear = False
        for pattern in self.active_ties:
            tie_def = ALL_TIES.get(pattern.value)
            if tie_def:
                if tie_def.exposes_front:
                    front = True
                if tie_def.exposes_rear:
                    rear = True
        return front, rear
    
    def get_description(self) -> str:
        """Get description of bondage state."""
        if not self.active_ties:
            return ""
        
        tie_descs = []
        for pattern in self.active_ties:
            tie_def = ALL_TIES.get(pattern.value)
            if tie_def:
                tie_descs.append(tie_def.bound_message)
        
        position_desc = f"in a {self.position.value.replace('_', ' ')} position"
        
        if self.is_suspended:
            position_desc = "suspended in the air"
        
        return f"{' and '.join(tie_descs)}, {position_desc}"
    
    def to_dict(self) -> dict:
        return {
            "bondage_id": self.bondage_id,
            "tier_dbref": self.tier_dbref,
            "tier_name": self.tier_name,
            "subject_dbref": self.subject_dbref,
            "subject_name": self.subject_name,
            "active_ties": [t.value for t in self.active_ties],
            "rope": self.rope.to_dict() if self.rope else None,
            "position": self.position.value,
            "anchor_dbref": self.anchor_dbref,
            "anchor_name": self.anchor_name,
            "tier_skill": self.tier_skill,
            "is_suspended": self.is_suspended,
            "struggle_count": self.struggle_count,
            "rope_loosened": self.rope_loosened,
            "tied_at": self.tied_at.isoformat() if self.tied_at else None,
        }
    
    @classmethod
    def from_dict(cls, data: dict) -> "ActiveBondage":
        bondage = cls(bondage_id=data["bondage_id"])
        bondage.tier_dbref = data.get("tier_dbref", "")
        bondage.tier_name = data.get("tier_name", "")
        bondage.subject_dbref = data.get("subject_dbref", "")
        bondage.subject_name = data.get("subject_name", "")
        bondage.active_ties = [TiePattern(t) for t in data.get("active_ties", [])]
        
        if data.get("rope"):
            bondage.rope = Rope.from_dict(data["rope"])
        
        bondage.position = BondagePosition(data.get("position", "kneeling"))
        bondage.anchor_dbref = data.get("anchor_dbref", "")
        bondage.anchor_name = data.get("anchor_name", "")
        bondage.tier_skill = data.get("tier_skill", 50)
        bondage.is_suspended = data.get("is_suspended", False)
        bondage.struggle_count = data.get("struggle_count", 0)
        bondage.rope_loosened = data.get("rope_loosened", 0)
        
        if data.get("tied_at"):
            bondage.tied_at = datetime.fromisoformat(data["tied_at"])
        
        return bondage


# =============================================================================
# BONDAGE SYSTEM
# =============================================================================

class BondageSystem:
    """
    Manages rope bondage.
    """
    
    @staticmethod
    def generate_id() -> str:
        """Generate unique ID."""
        timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
        rand = random.randint(1000, 9999)
        return f"BND-{timestamp}-{rand}"
    
    @staticmethod
    def start_bondage(
        tier,
        subject,
        rope: Optional[Rope] = None,
    ) -> Tuple[bool, str, Optional[ActiveBondage]]:
        """Start bondage session."""
        if hasattr(subject, 'current_bondage') and subject.current_bondage:
            return False, f"{subject.key} is already bound!", None
        
        bondage = ActiveBondage(
            bondage_id=BondageSystem.generate_id(),
            tier_dbref=tier.dbref,
            tier_name=tier.key,
            subject_dbref=subject.dbref,
            subject_name=subject.key,
            rope=rope or Rope(),
            tier_skill=getattr(tier, 'bondage_skill', 50),
            tied_at=datetime.now(),
        )
        
        return True, f"{tier.key} prepares rope to bind {subject.key}...", bondage
    
    @staticmethod
    def apply_tie(
        bondage: ActiveBondage,
        pattern: TiePattern,
        position: Optional[BondagePosition] = None,
    ) -> Tuple[bool, str]:
        """Apply a tie pattern."""
        tie_def = ALL_TIES.get(pattern.value)
        if not tie_def:
            return False, "Unknown tie pattern."
        
        # Check skill
        if bondage.tier_skill < tie_def.skill_required:
            return False, f"Requires skill level {tie_def.skill_required} to perform {tie_def.name}."
        
        # Check position compatibility
        if position:
            if position not in tie_def.valid_positions:
                valid = [p.value for p in tie_def.valid_positions]
                return False, f"{tie_def.name} requires one of: {', '.join(valid)}"
            bondage.position = position
        
        # Apply
        message = bondage.add_tie(pattern)
        
        # Update suspension
        if tie_def.allows_suspension and bondage.position == BondagePosition.SUSPENDED:
            bondage.is_suspended = True
        
        return True, message
    
    @staticmethod
    def release(bondage: ActiveBondage) -> str:
        """Release someone from bondage."""
        bondage.active_ties.clear()
        bondage.is_suspended = False
        return f"{bondage.subject_name} is released from the ropes."


# =============================================================================
# BONDAGE MIXIN
# =============================================================================

class BondageMixin:
    """
    Mixin for characters that can be bound.
    """
    
    @property
    def current_bondage(self) -> Optional[ActiveBondage]:
        """Get current bondage state."""
        data = self.attributes.get("current_bondage")
        if data:
            return ActiveBondage.from_dict(data)
        return None
    
    @current_bondage.setter
    def current_bondage(self, bondage: Optional[ActiveBondage]):
        """Set current bondage."""
        if bondage:
            self.attributes.add("current_bondage", bondage.to_dict())
        else:
            self.attributes.remove("current_bondage")
    
    def is_bound(self) -> bool:
        """Check if currently bound."""
        bondage = self.current_bondage
        return bondage is not None and len(bondage.active_ties) > 0
    
    def can_move_arms(self) -> bool:
        """Check if arms are free."""
        bondage = self.current_bondage
        if not bondage:
            return True
        return not bondage.is_arms_bound()
    
    def can_move_legs(self) -> bool:
        """Check if legs are free."""
        bondage = self.current_bondage
        if not bondage:
            return True
        return not bondage.is_legs_bound()
    
    def can_move(self) -> bool:
        """Check if can move freely."""
        bondage = self.current_bondage
        if not bondage:
            return True
        return not bondage.is_immobilized()
    
    @property
    def bondage_skill(self) -> int:
        """Get bondage/rope skill."""
        return self.attributes.get("bondage_skill", 50)


__all__ = [
    "RopeType",
    "TiePattern",
    "BondagePosition",
    "Rope",
    "TieDefinition",
    "ALL_TIES",
    "ActiveBondage",
    "BondageSystem",
    "BondageMixin",
]
