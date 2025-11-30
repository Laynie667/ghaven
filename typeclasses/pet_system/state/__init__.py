"""
Character State Tracking
========================

Comprehensive state tracking that integrates all systems:
- Physical state
- Mental state
- Sexual state
- Role assignments
- History tracking
"""

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any, Tuple
from enum import Enum
from datetime import datetime, timedelta
import random


# =============================================================================
# ENUMS
# =============================================================================

class CharacterRole(Enum):
    """Assigned roles."""
    FREE = "free"
    SLAVE = "slave"
    HUCOW = "hucow"
    BREEDING_STOCK = "breeding_stock"
    PUBLIC_USE = "public_use"
    PET = "pet"
    SERVANT = "servant"
    BULL = "bull"
    HANDLER = "handler"
    TRAINER = "trainer"
    OWNER = "owner"


class PhysicalCondition(Enum):
    """Physical condition states."""
    HEALTHY = "healthy"
    TIRED = "tired"
    EXHAUSTED = "exhausted"
    INJURED = "injured"
    SICK = "sick"
    RECOVERING = "recovering"
    PREGNANT = "pregnant"
    LACTATING = "lactating"
    IN_HEAT = "in_heat"


class SexualState(Enum):
    """Sexual arousal states."""
    DORMANT = "dormant"
    CALM = "calm"
    INTERESTED = "interested"
    AROUSED = "aroused"
    NEEDY = "needy"
    DESPERATE = "desperate"
    EDGE = "edge"
    ORGASMING = "orgasming"
    AFTERGLOW = "afterglow"
    OVERSTIMULATED = "overstimulated"


class RestraintState(Enum):
    """Restraint states."""
    FREE = "free"
    LEASHED = "leashed"
    BOUND_LIGHT = "bound_light"
    BOUND_HEAVY = "bound_heavy"
    CAGED = "caged"
    FURNITURE = "furniture"        # Attached to furniture
    STOCKS = "stocks"
    SUSPENDED = "suspended"


# =============================================================================
# PHYSICAL STATE
# =============================================================================

@dataclass
class PhysicalState:
    """Complete physical state tracking."""
    
    # Health
    health: int = 100             # 0-100
    stamina: int = 100            # 0-100
    condition: PhysicalCondition = PhysicalCondition.HEALTHY
    
    # Needs
    hunger: int = 0               # 0-100 (higher = more hungry)
    thirst: int = 0
    fatigue: int = 0              # 0-100 (higher = more tired)
    
    # Pain
    pain: int = 0                 # 0-100
    pain_sources: List[str] = field(default_factory=list)
    
    # Lactation (if applicable)
    is_lactating: bool = False
    breast_fullness: int = 0      # 0-100
    milk_pressure: int = 0        # 0-100 (discomfort from full breasts)
    
    # Pregnancy (if applicable)
    is_pregnant: bool = False
    pregnancy_day: int = 0
    pregnancy_symptoms: List[str] = field(default_factory=list)
    
    # Heat (if applicable)
    in_heat: bool = False
    heat_intensity: int = 0       # 0-100
    
    # Marks and injuries
    bruises: List[str] = field(default_factory=list)
    welts: List[str] = field(default_factory=list)
    brands: List[str] = field(default_factory=list)
    
    def update_needs(self, hours: float = 1.0) -> List[str]:
        """Update needs over time. Returns status messages."""
        messages = []
        
        self.hunger = min(100, self.hunger + int(hours * 4))
        self.thirst = min(100, self.thirst + int(hours * 6))
        self.fatigue = min(100, self.fatigue + int(hours * 3))
        
        if self.hunger >= 80:
            messages.append("Starving")
        elif self.hunger >= 50:
            messages.append("Hungry")
        
        if self.thirst >= 80:
            messages.append("Dehydrated")
        elif self.thirst >= 50:
            messages.append("Thirsty")
        
        if self.fatigue >= 80:
            messages.append("Exhausted")
            self.condition = PhysicalCondition.EXHAUSTED
        elif self.fatigue >= 50:
            messages.append("Tired")
            self.condition = PhysicalCondition.TIRED
        
        # Lactation pressure
        if self.is_lactating:
            self.breast_fullness = min(100, self.breast_fullness + int(hours * 10))
            if self.breast_fullness >= 80:
                self.milk_pressure = self.breast_fullness - 60
                messages.append("Breasts painfully full")
        
        # Heat intensifies
        if self.in_heat:
            self.heat_intensity = min(100, self.heat_intensity + int(hours * 5))
            if self.heat_intensity >= 80:
                messages.append("Heat overwhelming")
        
        return messages
    
    def feed(self, amount: int = 50) -> str:
        """Feed the character."""
        self.hunger = max(0, self.hunger - amount)
        return f"Hunger reduced to {self.hunger}/100"
    
    def water(self, amount: int = 50) -> str:
        """Give water."""
        self.thirst = max(0, self.thirst - amount)
        return f"Thirst reduced to {self.thirst}/100"
    
    def rest(self, hours: float = 8.0) -> str:
        """Rest and recover."""
        self.fatigue = max(0, self.fatigue - int(hours * 10))
        if self.condition == PhysicalCondition.EXHAUSTED and self.fatigue < 50:
            self.condition = PhysicalCondition.TIRED
        if self.condition == PhysicalCondition.TIRED and self.fatigue < 20:
            self.condition = PhysicalCondition.HEALTHY
        return f"Rested. Fatigue: {self.fatigue}/100"
    
    def add_pain(self, amount: int, source: str) -> str:
        """Add pain from a source."""
        self.pain = min(100, self.pain + amount)
        if source not in self.pain_sources:
            self.pain_sources.append(source)
        return f"Pain increased to {self.pain}/100 ({source})"
    
    def reduce_pain(self, amount: int = 20) -> str:
        """Reduce pain over time."""
        self.pain = max(0, self.pain - amount)
        if self.pain == 0:
            self.pain_sources.clear()
        return f"Pain reduced to {self.pain}/100"
    
    def get_summary(self) -> str:
        """Get physical state summary."""
        lines = []
        
        lines.append(f"Condition: {self.condition.value}")
        lines.append(f"Health: {self.health}/100 | Stamina: {self.stamina}/100")
        lines.append(f"Hunger: {self.hunger}/100 | Thirst: {self.thirst}/100 | Fatigue: {self.fatigue}/100")
        
        if self.pain > 0:
            lines.append(f"Pain: {self.pain}/100 ({', '.join(self.pain_sources)})")
        
        if self.is_lactating:
            lines.append(f"Breast Fullness: {self.breast_fullness}/100")
        
        if self.is_pregnant:
            lines.append(f"Pregnant: Day {self.pregnancy_day}")
        
        if self.in_heat:
            lines.append(f"IN HEAT: {self.heat_intensity}/100")
        
        return "\n".join(lines)


# =============================================================================
# SEXUAL STATE
# =============================================================================

@dataclass
class SexualState_:
    """Sexual state tracking."""
    
    # Arousal
    arousal: int = 0              # 0-100
    state: SexualState = SexualState.CALM
    
    # Denial
    denied: bool = False
    hours_denied: float = 0
    edges_without_release: int = 0
    
    # Orgasm tracking
    orgasms_today: int = 0
    orgasms_total: int = 0
    last_orgasm: Optional[datetime] = None
    forced_orgasms_today: int = 0
    
    # Sensitivity
    sensitivity: int = 50         # 0-100
    nipple_sensitivity: int = 50
    clit_sensitivity: int = 50
    
    # Fluids
    wetness: int = 0              # 0-100
    dripping: bool = False
    
    # Use tracking today
    oral_uses: int = 0
    vaginal_uses: int = 0
    anal_uses: int = 0
    cum_received_ml: int = 0
    
    def update_state(self) -> str:
        """Update state based on arousal."""
        old = self.state
        
        if self.arousal >= 95:
            self.state = SexualState.EDGE
        elif self.arousal >= 80:
            self.state = SexualState.DESPERATE
        elif self.arousal >= 60:
            self.state = SexualState.NEEDY
        elif self.arousal >= 40:
            self.state = SexualState.AROUSED
        elif self.arousal >= 20:
            self.state = SexualState.INTERESTED
        elif self.arousal >= 5:
            self.state = SexualState.CALM
        else:
            self.state = SexualState.DORMANT
        
        if old != self.state:
            return f"State: {old.value} → {self.state.value}"
        return ""
    
    def increase_arousal(self, amount: int) -> str:
        """Increase arousal."""
        mult = 1.0
        if self.denied:
            mult = 1.5
        if self.edges_without_release > 0:
            mult += self.edges_without_release * 0.2
        
        self.arousal = min(100, self.arousal + int(amount * mult))
        self.wetness = min(100, self.wetness + amount // 2)
        
        if self.wetness >= 80:
            self.dripping = True
        
        state_msg = self.update_state()
        return f"Arousal: {self.arousal}/100. {state_msg}"
    
    def edge(self) -> str:
        """Bring to edge without release."""
        self.arousal = 99
        self.state = SexualState.EDGE
        self.edges_without_release += 1
        
        return f"Brought to the edge! ({self.edges_without_release} edges without release)"
    
    def orgasm(self, forced: bool = False) -> str:
        """Experience orgasm."""
        self.state = SexualState.ORGASMING
        self.orgasms_today += 1
        self.orgasms_total += 1
        self.last_orgasm = datetime.now()
        
        if forced:
            self.forced_orgasms_today += 1
        
        # Post-orgasm
        self.arousal = max(0, self.arousal - 50)
        self.edges_without_release = 0
        
        if self.denied:
            self.denied = False
            self.hours_denied = 0
        
        return f"Orgasm #{self.orgasms_today} today! (Total: {self.orgasms_total})"
    
    def deny(self) -> str:
        """Deny orgasm."""
        self.denied = True
        self.arousal = min(100, self.arousal + 10)  # Frustration builds
        return "Denied release!"
    
    def record_use(self, use_type: str, cum_ml: int = 0) -> str:
        """Record being used."""
        if use_type == "oral":
            self.oral_uses += 1
        elif use_type == "vaginal":
            self.vaginal_uses += 1
        elif use_type == "anal":
            self.anal_uses += 1
        
        self.cum_received_ml += cum_ml
        
        total = self.oral_uses + self.vaginal_uses + self.anal_uses
        return f"Used {total} times today. Cum received: {self.cum_received_ml}ml"
    
    def daily_reset(self) -> None:
        """Reset daily counters."""
        self.orgasms_today = 0
        self.forced_orgasms_today = 0
        self.oral_uses = 0
        self.vaginal_uses = 0
        self.anal_uses = 0
        self.cum_received_ml = 0
    
    def get_summary(self) -> str:
        """Get sexual state summary."""
        lines = []
        
        lines.append(f"State: {self.state.value.upper()}")
        lines.append(f"Arousal: {self.arousal}/100 | Wetness: {self.wetness}/100")
        
        if self.denied:
            lines.append(f"DENIED - {self.hours_denied:.1f} hours")
        
        if self.edges_without_release > 0:
            lines.append(f"Edges: {self.edges_without_release}")
        
        lines.append(f"Orgasms Today: {self.orgasms_today} (Forced: {self.forced_orgasms_today})")
        
        uses = self.oral_uses + self.vaginal_uses + self.anal_uses
        if uses > 0:
            lines.append(f"Uses Today: {uses} (O:{self.oral_uses} V:{self.vaginal_uses} A:{self.anal_uses})")
            lines.append(f"Cum Received: {self.cum_received_ml}ml")
        
        return "\n".join(lines)


# =============================================================================
# COMPLETE CHARACTER STATE
# =============================================================================

@dataclass
class CharacterState:
    """Complete character state combining all systems."""
    
    # Identity
    character_dbref: str = ""
    character_name: str = ""
    
    # Role
    current_role: CharacterRole = CharacterRole.FREE
    owner_dbref: str = ""
    owner_name: str = ""
    
    # Restraints
    restraint_state: RestraintState = RestraintState.FREE
    restraint_details: str = ""
    
    # Sub-states
    physical: PhysicalState = field(default_factory=PhysicalState)
    sexual: SexualState_ = field(default_factory=SexualState_)
    
    # Location
    assigned_location: str = ""   # Stall, kennel, etc.
    current_location: str = ""
    
    # Clothing
    is_nude: bool = False
    clothing_items: List[str] = field(default_factory=list)
    
    # Equipment
    collar: str = ""
    leash: str = ""
    gag: str = ""
    blindfold: bool = False
    plugged: bool = False
    chastity: bool = False
    
    # Daily tracking
    date: Optional[datetime] = None
    tasks_completed: int = 0
    tasks_failed: int = 0
    punishments_received: int = 0
    rewards_received: int = 0
    
    # Value tracking
    current_value: int = 0
    earnings_today: int = 0
    
    def update_all(self, hours: float = 1.0) -> List[str]:
        """Update all states over time."""
        messages = []
        
        # Physical needs
        phys_msgs = self.physical.update_needs(hours)
        messages.extend(phys_msgs)
        
        # Pain fades slowly
        if self.physical.pain > 0:
            self.physical.reduce_pain(int(hours * 5))
        
        # Denial tracking
        if self.sexual.denied:
            self.sexual.hours_denied += hours
            self.sexual.increase_arousal(int(hours * 5))
        
        # Arousal decay (slow)
        if not self.sexual.denied and self.sexual.arousal > 0:
            self.sexual.arousal = max(0, self.sexual.arousal - int(hours * 2))
            self.sexual.update_state()
        
        return messages
    
    def assign_role(self, role: CharacterRole, owner_dbref: str = "", owner_name: str = "") -> str:
        """Assign a role."""
        old = self.current_role
        self.current_role = role
        self.owner_dbref = owner_dbref
        self.owner_name = owner_name
        
        return f"Role changed: {old.value} → {role.value}"
    
    def restrain(self, state: RestraintState, details: str = "") -> str:
        """Apply restraints."""
        self.restraint_state = state
        self.restraint_details = details
        return f"Restrained: {state.value}"
    
    def strip(self) -> str:
        """Remove all clothing."""
        items = len(self.clothing_items)
        self.clothing_items.clear()
        self.is_nude = True
        return f"Stripped of {items} items. Now nude."
    
    def equip(self, equipment_type: str, item: str = "") -> str:
        """Equip something."""
        if equipment_type == "collar":
            self.collar = item or "collar"
            return f"Collared with {self.collar}"
        elif equipment_type == "leash":
            self.leash = item or "leash"
            return f"Leashed with {self.leash}"
        elif equipment_type == "gag":
            self.gag = item or "ball gag"
            return f"Gagged with {self.gag}"
        elif equipment_type == "blindfold":
            self.blindfold = True
            return "Blindfolded"
        elif equipment_type == "plug":
            self.plugged = True
            return "Plugged"
        elif equipment_type == "chastity":
            self.chastity = True
            self.sexual.denied = True
            return "Locked in chastity"
        return "Unknown equipment"
    
    def daily_reset(self) -> str:
        """Reset daily counters."""
        self.date = datetime.now()
        self.tasks_completed = 0
        self.tasks_failed = 0
        self.punishments_received = 0
        self.rewards_received = 0
        self.earnings_today = 0
        self.sexual.daily_reset()
        return "Daily counters reset."
    
    def get_full_status(self) -> str:
        """Get complete status display."""
        lines = [f"=== Status: {self.character_name} ==="]
        
        # Role
        lines.append(f"\n--- Role ---")
        lines.append(f"Role: {self.current_role.value.upper()}")
        if self.owner_name:
            lines.append(f"Owner: {self.owner_name}")
        
        # Restraints/Equipment
        lines.append(f"\n--- Restraints & Equipment ---")
        lines.append(f"State: {self.restraint_state.value}")
        equip = []
        if self.collar:
            equip.append(f"Collar: {self.collar}")
        if self.leash:
            equip.append(f"Leash: {self.leash}")
        if self.gag:
            equip.append(f"Gag: {self.gag}")
        if self.blindfold:
            equip.append("Blindfolded")
        if self.plugged:
            equip.append("Plugged")
        if self.chastity:
            equip.append("CHASTITY")
        if equip:
            lines.append("  " + " | ".join(equip))
        lines.append(f"Nude: {'Yes' if self.is_nude else 'No'}")
        
        # Physical
        lines.append(f"\n--- Physical ---")
        lines.append(self.physical.get_summary())
        
        # Sexual
        lines.append(f"\n--- Sexual ---")
        lines.append(self.sexual.get_summary())
        
        # Daily
        lines.append(f"\n--- Today ---")
        lines.append(f"Tasks: {self.tasks_completed} completed, {self.tasks_failed} failed")
        lines.append(f"Punishments: {self.punishments_received} | Rewards: {self.rewards_received}")
        lines.append(f"Earnings: {self.earnings_today} gold")
        
        return "\n".join(lines)
    
    def to_dict(self) -> dict:
        return {
            "character_dbref": self.character_dbref,
            "character_name": self.character_name,
            "current_role": self.current_role.value,
            "owner_dbref": self.owner_dbref,
            "owner_name": self.owner_name,
            "restraint_state": self.restraint_state.value,
            "is_nude": self.is_nude,
            "collar": self.collar,
            "leash": self.leash,
            "gag": self.gag,
            "blindfold": self.blindfold,
            "plugged": self.plugged,
            "chastity": self.chastity,
            "physical": {
                "health": self.physical.health,
                "stamina": self.physical.stamina,
                "hunger": self.physical.hunger,
                "thirst": self.physical.thirst,
                "fatigue": self.physical.fatigue,
                "pain": self.physical.pain,
                "is_lactating": self.physical.is_lactating,
                "breast_fullness": self.physical.breast_fullness,
                "is_pregnant": self.physical.is_pregnant,
                "pregnancy_day": self.physical.pregnancy_day,
                "in_heat": self.physical.in_heat,
                "heat_intensity": self.physical.heat_intensity,
            },
            "sexual": {
                "arousal": self.sexual.arousal,
                "state": self.sexual.state.value,
                "denied": self.sexual.denied,
                "hours_denied": self.sexual.hours_denied,
                "orgasms_total": self.sexual.orgasms_total,
                "sensitivity": self.sexual.sensitivity,
            },
        }
    
    @classmethod
    def from_dict(cls, data: dict) -> "CharacterState":
        state = cls()
        state.character_dbref = data.get("character_dbref", "")
        state.character_name = data.get("character_name", "")
        state.current_role = CharacterRole(data.get("current_role", "free"))
        state.owner_dbref = data.get("owner_dbref", "")
        state.owner_name = data.get("owner_name", "")
        state.restraint_state = RestraintState(data.get("restraint_state", "free"))
        state.is_nude = data.get("is_nude", False)
        state.collar = data.get("collar", "")
        state.leash = data.get("leash", "")
        state.gag = data.get("gag", "")
        state.blindfold = data.get("blindfold", False)
        state.plugged = data.get("plugged", False)
        state.chastity = data.get("chastity", False)
        
        if "physical" in data:
            p = data["physical"]
            state.physical.health = p.get("health", 100)
            state.physical.stamina = p.get("stamina", 100)
            state.physical.hunger = p.get("hunger", 0)
            state.physical.thirst = p.get("thirst", 0)
            state.physical.fatigue = p.get("fatigue", 0)
            state.physical.pain = p.get("pain", 0)
            state.physical.is_lactating = p.get("is_lactating", False)
            state.physical.breast_fullness = p.get("breast_fullness", 0)
            state.physical.is_pregnant = p.get("is_pregnant", False)
            state.physical.pregnancy_day = p.get("pregnancy_day", 0)
            state.physical.in_heat = p.get("in_heat", False)
            state.physical.heat_intensity = p.get("heat_intensity", 0)
        
        if "sexual" in data:
            s = data["sexual"]
            state.sexual.arousal = s.get("arousal", 0)
            state.sexual.state = SexualState(s.get("state", "calm"))
            state.sexual.denied = s.get("denied", False)
            state.sexual.hours_denied = s.get("hours_denied", 0)
            state.sexual.orgasms_total = s.get("orgasms_total", 0)
            state.sexual.sensitivity = s.get("sensitivity", 50)
        
        return state


# =============================================================================
# STATE MIXIN
# =============================================================================

class CharacterStateMixin:
    """Mixin for full character state tracking."""
    
    @property
    def char_state(self) -> CharacterState:
        """Get character state."""
        data = self.db.character_state
        if data:
            return CharacterState.from_dict(data)
        return CharacterState(character_dbref=self.dbref, character_name=self.key)
    
    @char_state.setter
    def char_state(self, state: CharacterState) -> None:
        """Set character state."""
        self.db.character_state = state.to_dict()
    
    def save_char_state(self, state: CharacterState) -> None:
        """Save character state."""
        self.db.character_state = state.to_dict()


__all__ = [
    "CharacterRole",
    "PhysicalCondition",
    "SexualState",
    "RestraintState",
    "PhysicalState",
    "SexualState_",
    "CharacterState",
    "CharacterStateMixin",
]
