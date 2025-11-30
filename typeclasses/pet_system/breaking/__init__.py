"""
Breaking and Conditioning System
================================

Psychological and physical breaking including:
- Resistance tracking
- Breaking methods
- Conditioning triggers
- Mental state management
- Obedience programming
"""

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any, Tuple
from enum import Enum
from datetime import datetime, timedelta
import random


# =============================================================================
# ENUMS
# =============================================================================

class ResistanceLevel(Enum):
    """Levels of resistance to breaking."""
    BROKEN = "broken"             # Completely broken, no resistance
    COMPLIANT = "compliant"       # Accepts role, minimal resistance  
    SUBMISSIVE = "submissive"     # Willingly submits
    RESIGNED = "resigned"         # Given up fighting
    WAVERING = "wavering"         # Resistance crumbling
    STUBBORN = "stubborn"         # Still fighting
    DEFIANT = "defiant"           # Active resistance
    REBELLIOUS = "rebellious"     # Dangerous, fights back


class BreakingMethod(Enum):
    """Methods of breaking resistance."""
    ISOLATION = "isolation"
    SENSORY_DEPRIVATION = "sensory_deprivation"
    SENSORY_OVERLOAD = "sensory_overload"
    SLEEP_DEPRIVATION = "sleep_deprivation"
    EXHAUSTION = "exhaustion"
    PAIN = "pain"
    PLEASURE = "pleasure"
    EDGING = "edging"
    FORCED_ORGASM = "forced_orgasm"
    DENIAL = "denial"
    HUMILIATION = "humiliation"
    DEGRADATION = "degradation"
    PRAISE = "praise"
    AFFECTION = "affection"
    FEAR = "fear"
    DRUGS = "drugs"
    HYPNOSIS = "hypnosis"
    CONDITIONING = "conditioning"
    MIND_BREAK = "mind_break"


class TriggerType(Enum):
    """Types of conditioned triggers."""
    WORD = "word"                 # Spoken command
    TOUCH = "touch"               # Physical touch
    SOUND = "sound"               # Bell, whistle, etc.
    VISUAL = "visual"             # Gesture, symbol
    TASTE = "taste"               # Specific taste
    SMELL = "smell"               # Specific scent
    POSITION = "position"         # Body position
    PAIN = "pain"                 # Pain stimulus
    PLEASURE = "pleasure"         # Pleasure stimulus


class ConditionedResponse(Enum):
    """Trained responses to triggers."""
    FREEZE = "freeze"             # Stop all movement
    KNEEL = "kneel"               # Drop to knees
    PRESENT = "present"           # Sexual presentation
    ORGASM = "orgasm"             # Forced orgasm
    AROUSAL = "arousal"           # Instant arousal
    OBEY = "obey"                 # Compulsive obedience
    SPEAK = "speak"               # Forced speech
    SILENCE = "silence"           # Cannot speak
    SLEEP = "sleep"               # Instant sleep
    WAKE = "wake"                 # Wake from sleep
    PAIN = "pain"                 # Feel pain
    PLEASURE = "pleasure"         # Feel pleasure
    FEAR = "fear"                 # Feel fear
    LOVE = "love"                 # Feel affection
    LACTATE = "lactate"           # Trigger milk letdown
    HEAT = "heat"                 # Trigger arousal/heat


class MentalState(Enum):
    """Current mental states."""
    NORMAL = "normal"
    DAZED = "dazed"
    CONFUSED = "confused"
    AROUSED = "aroused"
    TERRIFIED = "terrified"
    BLISSFUL = "blissful"
    EMPTY = "empty"               # Mind-broken emptiness
    DESPERATE = "desperate"
    NEEDY = "needy"
    SUBSPACE = "subspace"         # Deep submission
    MINDLESS = "mindless"         # No independent thought
    PROGRAMMED = "programmed"     # Acting on conditioning


# =============================================================================
# CONDITIONED TRIGGER
# =============================================================================

@dataclass
class ConditionedTrigger:
    """A single conditioned response."""
    
    trigger_id: str = ""
    name: str = ""
    
    # Trigger
    trigger_type: TriggerType = TriggerType.WORD
    trigger_stimulus: str = ""    # The word, touch location, sound, etc.
    
    # Response
    response: ConditionedResponse = ConditionedResponse.OBEY
    response_description: str = ""
    response_duration_seconds: int = 60
    
    # Strength
    conditioning_strength: int = 50  # 0-100
    resistance_difficulty: int = 50  # DC to resist
    
    # Owner
    installed_by: str = ""
    installed_date: Optional[datetime] = None
    
    # Usage
    times_triggered: int = 0
    last_triggered: Optional[datetime] = None
    
    def trigger(self, resistance: int = 0) -> Tuple[bool, str]:
        """
        Activate the trigger.
        Returns (success, message).
        """
        # Check if resisted
        if resistance > 0:
            resist_roll = random.randint(1, 100)
            if resist_roll + resistance > self.resistance_difficulty + self.conditioning_strength:
                return False, f"Struggles against the conditioning..."
        
        self.times_triggered += 1
        self.last_triggered = datetime.now()
        
        response_msgs = {
            ConditionedResponse.FREEZE: "freezes in place, unable to move",
            ConditionedResponse.KNEEL: "drops to their knees automatically",
            ConditionedResponse.PRESENT: "assumes a presenting position, body offered",
            ConditionedResponse.ORGASM: "convulses in an uncontrollable orgasm",
            ConditionedResponse.AROUSAL: "flushes with sudden, intense arousal",
            ConditionedResponse.OBEY: "feels compelled to obey",
            ConditionedResponse.SPEAK: "blurts out words uncontrollably",
            ConditionedResponse.SILENCE: "finds themselves unable to speak",
            ConditionedResponse.SLEEP: "collapses into instant sleep",
            ConditionedResponse.LACTATE: "feels milk letting down from their breasts",
            ConditionedResponse.HEAT: "burns with sudden breeding need",
            ConditionedResponse.SUBSPACE: "sinks into deep, mindless submission",
        }
        
        msg = response_msgs.get(self.response, "responds to the trigger")
        return True, msg
    
    def strengthen(self, amount: int = 10) -> str:
        """Strengthen the conditioning."""
        old = self.conditioning_strength
        self.conditioning_strength = min(100, self.conditioning_strength + amount)
        self.resistance_difficulty += amount // 2
        return f"Conditioning strengthened: {old} → {self.conditioning_strength}"
    
    def to_dict(self) -> dict:
        return {
            "trigger_id": self.trigger_id,
            "name": self.name,
            "trigger_type": self.trigger_type.value,
            "trigger_stimulus": self.trigger_stimulus,
            "response": self.response.value,
            "response_description": self.response_description,
            "response_duration_seconds": self.response_duration_seconds,
            "conditioning_strength": self.conditioning_strength,
            "resistance_difficulty": self.resistance_difficulty,
            "installed_by": self.installed_by,
            "installed_date": self.installed_date.isoformat() if self.installed_date else None,
            "times_triggered": self.times_triggered,
            "last_triggered": self.last_triggered.isoformat() if self.last_triggered else None,
        }
    
    @classmethod
    def from_dict(cls, data: dict) -> "ConditionedTrigger":
        trigger = cls()
        for key, value in data.items():
            if key == "trigger_type":
                trigger.trigger_type = TriggerType(value)
            elif key == "response":
                trigger.response = ConditionedResponse(value)
            elif key in ["installed_date", "last_triggered"] and value:
                setattr(trigger, key, datetime.fromisoformat(value))
            elif hasattr(trigger, key):
                setattr(trigger, key, value)
        return trigger


# =============================================================================
# BREAKING SESSION
# =============================================================================

@dataclass
class BreakingSession:
    """Record of a breaking session."""
    
    session_id: str = ""
    subject_dbref: str = ""
    subject_name: str = ""
    breaker_name: str = ""
    
    # Methods used
    methods_used: List[BreakingMethod] = field(default_factory=list)
    
    # Duration
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    duration_hours: float = 0.0
    
    # Results
    resistance_start: int = 0
    resistance_end: int = 0
    resistance_reduced: int = 0
    
    willpower_start: int = 0
    willpower_end: int = 0
    willpower_reduced: int = 0
    
    # Events during session
    events: List[str] = field(default_factory=list)
    
    # State changes
    mental_state_changes: List[str] = field(default_factory=list)
    
    def add_event(self, event: str) -> None:
        """Add an event to the session log."""
        timestamp = datetime.now().strftime("%H:%M")
        self.events.append(f"[{timestamp}] {event}")
    
    def get_summary(self) -> str:
        """Get session summary."""
        lines = [f"=== Breaking Session: {self.subject_name} ==="]
        lines.append(f"Breaker: {self.breaker_name}")
        lines.append(f"Duration: {self.duration_hours:.1f} hours")
        
        lines.append(f"\nMethods: {', '.join(m.value for m in self.methods_used)}")
        
        lines.append(f"\nResistance: {self.resistance_start} → {self.resistance_end} (-{self.resistance_reduced})")
        lines.append(f"Willpower: {self.willpower_start} → {self.willpower_end} (-{self.willpower_reduced})")
        
        if self.events:
            lines.append(f"\n--- Session Log ---")
            for event in self.events[-10:]:
                lines.append(event)
        
        return "\n".join(lines)


# =============================================================================
# MENTAL STATE TRACKING
# =============================================================================

@dataclass
class MentalStatus:
    """Complete mental state tracking."""
    
    subject_dbref: str = ""
    subject_name: str = ""
    
    # Core stats
    willpower: int = 50           # 0-100, resistance to breaking
    resistance: int = 50          # 0-100, current resistance level
    sanity: int = 100             # 0-100, mental stability
    
    # Derived level
    resistance_level: ResistanceLevel = ResistanceLevel.STUBBORN
    
    # Current state
    mental_state: MentalState = MentalState.NORMAL
    arousal: int = 0              # 0-100
    fear: int = 0                 # 0-100
    desperation: int = 0          # 0-100
    
    # Conditioning
    obedience: int = 0            # 0-100, trained obedience
    devotion: int = 0             # 0-100, emotional attachment
    dependency: int = 0           # 0-100, psychological dependency
    
    # Triggers
    triggers: List[ConditionedTrigger] = field(default_factory=list)
    
    # Breaking history
    sessions_endured: int = 0
    hours_in_breaking: float = 0.0
    times_broken: int = 0
    
    # Current session
    in_breaking_session: bool = False
    current_session_start: Optional[datetime] = None
    
    def update_resistance_level(self) -> str:
        """Update resistance level based on stats."""
        old_level = self.resistance_level
        
        if self.resistance <= 5 or self.willpower <= 5:
            self.resistance_level = ResistanceLevel.BROKEN
        elif self.resistance <= 15:
            self.resistance_level = ResistanceLevel.COMPLIANT
        elif self.resistance <= 25:
            self.resistance_level = ResistanceLevel.SUBMISSIVE
        elif self.resistance <= 40:
            self.resistance_level = ResistanceLevel.RESIGNED
        elif self.resistance <= 55:
            self.resistance_level = ResistanceLevel.WAVERING
        elif self.resistance <= 70:
            self.resistance_level = ResistanceLevel.STUBBORN
        elif self.resistance <= 85:
            self.resistance_level = ResistanceLevel.DEFIANT
        else:
            self.resistance_level = ResistanceLevel.REBELLIOUS
        
        if old_level != self.resistance_level:
            return f"Resistance changed: {old_level.value} → {self.resistance_level.value}"
        return ""
    
    def apply_breaking_method(self, method: BreakingMethod, intensity: int = 50) -> Tuple[str, int]:
        """
        Apply a breaking method.
        Returns (message, resistance_reduced).
        """
        reduction = 0
        willpower_loss = 0
        message = ""
        
        # Base effectiveness varies by method
        base_effect = {
            BreakingMethod.ISOLATION: 3,
            BreakingMethod.SENSORY_DEPRIVATION: 4,
            BreakingMethod.SENSORY_OVERLOAD: 5,
            BreakingMethod.SLEEP_DEPRIVATION: 4,
            BreakingMethod.EXHAUSTION: 3,
            BreakingMethod.PAIN: 4,
            BreakingMethod.PLEASURE: 5,
            BreakingMethod.EDGING: 6,
            BreakingMethod.FORCED_ORGASM: 7,
            BreakingMethod.DENIAL: 5,
            BreakingMethod.HUMILIATION: 4,
            BreakingMethod.DEGRADATION: 5,
            BreakingMethod.PRAISE: 3,
            BreakingMethod.AFFECTION: 3,
            BreakingMethod.FEAR: 4,
            BreakingMethod.DRUGS: 8,
            BreakingMethod.HYPNOSIS: 6,
            BreakingMethod.CONDITIONING: 5,
            BreakingMethod.MIND_BREAK: 10,
        }
        
        base = base_effect.get(method, 3)
        
        # Scale by intensity
        reduction = int(base * (intensity / 50))
        willpower_loss = reduction // 2
        
        # Add randomness
        reduction += random.randint(-2, 3)
        reduction = max(1, reduction)
        
        # Apply reduction
        old_resistance = self.resistance
        self.resistance = max(0, self.resistance - reduction)
        self.willpower = max(0, self.willpower - willpower_loss)
        
        # Update mental state based on method
        state_effects = {
            BreakingMethod.PLEASURE: MentalState.AROUSED,
            BreakingMethod.FORCED_ORGASM: MentalState.BLISSFUL,
            BreakingMethod.EDGING: MentalState.DESPERATE,
            BreakingMethod.FEAR: MentalState.TERRIFIED,
            BreakingMethod.SENSORY_DEPRIVATION: MentalState.CONFUSED,
            BreakingMethod.MIND_BREAK: MentalState.EMPTY,
            BreakingMethod.HYPNOSIS: MentalState.DAZED,
            BreakingMethod.EXHAUSTION: MentalState.DAZED,
        }
        
        if method in state_effects:
            self.mental_state = state_effects[method]
        
        # Generate message
        method_messages = {
            BreakingMethod.ISOLATION: "Left alone in the darkness, mind beginning to crack.",
            BreakingMethod.SENSORY_DEPRIVATION: "Floating in nothingness, sense of self dissolving.",
            BreakingMethod.SENSORY_OVERLOAD: "Overwhelmed by sensation, unable to think.",
            BreakingMethod.SLEEP_DEPRIVATION: "Exhaustion strips away the will to fight.",
            BreakingMethod.PAIN: "Pain breaks through defenses, wearing down resistance.",
            BreakingMethod.PLEASURE: "Pleasure rewires the brain, associating submission with bliss.",
            BreakingMethod.EDGING: "Kept on the edge, desperate for release, willing to do anything.",
            BreakingMethod.FORCED_ORGASM: "Forced to cum again and again until the mind goes blank.",
            BreakingMethod.DENIAL: "Denied release, need building until obedience seems worth it.",
            BreakingMethod.HUMILIATION: "Shame and degradation erode pride and self-worth.",
            BreakingMethod.DEGRADATION: "Treated as less than human, beginning to believe it.",
            BreakingMethod.PRAISE: "Kindness after cruelty creates desperate gratitude.",
            BreakingMethod.AFFECTION: "Gentle touches create confusing emotional bonds.",
            BreakingMethod.FEAR: "Terror overwhelms rational thought.",
            BreakingMethod.DRUGS: "Chemicals flood the system, mind becoming pliable.",
            BreakingMethod.HYPNOSIS: "Words sink deep, rewriting thoughts.",
            BreakingMethod.CONDITIONING: "Responses becoming automatic, trained like an animal.",
            BreakingMethod.MIND_BREAK: "Something fundamental shatters. What remains is compliant.",
        }
        
        message = method_messages.get(method, "Resistance weakens.")
        
        # Check for breaking
        level_msg = self.update_resistance_level()
        if level_msg:
            message += f"\n{level_msg}"
        
        if self.resistance_level == ResistanceLevel.BROKEN:
            self.times_broken += 1
            message += "\n*** BROKEN ***"
        
        return message, reduction
    
    def install_trigger(
        self,
        trigger_type: TriggerType,
        stimulus: str,
        response: ConditionedResponse,
        installer: str,
    ) -> ConditionedTrigger:
        """Install a new conditioned trigger."""
        trigger = ConditionedTrigger(
            trigger_id=f"TRG-{datetime.now().strftime('%Y%m%d%H%M%S')}-{random.randint(100, 999)}",
            name=f"{stimulus} → {response.value}",
            trigger_type=trigger_type,
            trigger_stimulus=stimulus,
            response=response,
            conditioning_strength=30 + self.obedience // 2,  # Easier to condition the obedient
            resistance_difficulty=50 - self.resistance // 3,  # Easier on broken subjects
            installed_by=installer,
            installed_date=datetime.now(),
        )
        
        self.triggers.append(trigger)
        return trigger
    
    def activate_trigger(self, stimulus: str) -> Tuple[bool, str, Optional[ConditionedTrigger]]:
        """
        Check if a stimulus activates any triggers.
        Returns (activated, message, trigger).
        """
        for trigger in self.triggers:
            if trigger.trigger_stimulus.lower() in stimulus.lower():
                success, msg = trigger.trigger(self.resistance)
                if success:
                    return True, msg, trigger
                return False, msg, trigger
        
        return False, "No trigger activated.", None
    
    def increase_obedience(self, amount: int) -> str:
        """Increase obedience level."""
        old = self.obedience
        self.obedience = min(100, self.obedience + amount)
        return f"Obedience: {old} → {self.obedience}"
    
    def increase_devotion(self, amount: int) -> str:
        """Increase devotion level."""
        old = self.devotion
        self.devotion = min(100, self.devotion + amount)
        return f"Devotion: {old} → {self.devotion}"
    
    def increase_dependency(self, amount: int) -> str:
        """Increase dependency level."""
        old = self.dependency
        self.dependency = min(100, self.dependency + amount)
        return f"Dependency: {old} → {self.dependency}"
    
    def get_status_display(self) -> str:
        """Get formatted status display."""
        lines = [f"=== Mental Status: {self.subject_name} ==="]
        
        lines.append(f"\n--- Core Stats ---")
        lines.append(f"Willpower: {self.willpower}/100")
        lines.append(f"Resistance: {self.resistance}/100")
        lines.append(f"Sanity: {self.sanity}/100")
        lines.append(f"Level: {self.resistance_level.value.upper()}")
        
        lines.append(f"\n--- Current State ---")
        lines.append(f"Mental State: {self.mental_state.value}")
        lines.append(f"Arousal: {self.arousal}/100")
        lines.append(f"Fear: {self.fear}/100")
        lines.append(f"Desperation: {self.desperation}/100")
        
        lines.append(f"\n--- Conditioning ---")
        lines.append(f"Obedience: {self.obedience}/100")
        lines.append(f"Devotion: {self.devotion}/100")
        lines.append(f"Dependency: {self.dependency}/100")
        
        if self.triggers:
            lines.append(f"\n--- Triggers ({len(self.triggers)}) ---")
            for t in self.triggers[:5]:
                lines.append(f"  '{t.trigger_stimulus}' → {t.response.value} ({t.conditioning_strength}%)")
        
        lines.append(f"\n--- History ---")
        lines.append(f"Sessions Endured: {self.sessions_endured}")
        lines.append(f"Hours in Breaking: {self.hours_in_breaking:.1f}")
        lines.append(f"Times Broken: {self.times_broken}")
        
        return "\n".join(lines)
    
    def to_dict(self) -> dict:
        return {
            "subject_dbref": self.subject_dbref,
            "subject_name": self.subject_name,
            "willpower": self.willpower,
            "resistance": self.resistance,
            "sanity": self.sanity,
            "resistance_level": self.resistance_level.value,
            "mental_state": self.mental_state.value,
            "arousal": self.arousal,
            "fear": self.fear,
            "desperation": self.desperation,
            "obedience": self.obedience,
            "devotion": self.devotion,
            "dependency": self.dependency,
            "triggers": [t.to_dict() for t in self.triggers],
            "sessions_endured": self.sessions_endured,
            "hours_in_breaking": self.hours_in_breaking,
            "times_broken": self.times_broken,
            "in_breaking_session": self.in_breaking_session,
            "current_session_start": self.current_session_start.isoformat() if self.current_session_start else None,
        }
    
    @classmethod
    def from_dict(cls, data: dict) -> "MentalStatus":
        status = cls()
        for key, value in data.items():
            if key == "resistance_level":
                status.resistance_level = ResistanceLevel(value)
            elif key == "mental_state":
                status.mental_state = MentalState(value)
            elif key == "triggers":
                status.triggers = [ConditionedTrigger.from_dict(t) for t in value]
            elif key == "current_session_start" and value:
                status.current_session_start = datetime.fromisoformat(value)
            elif hasattr(status, key):
                setattr(status, key, value)
        return status


# =============================================================================
# BREAKING MIXIN
# =============================================================================

class BreakingMixin:
    """Mixin for characters that can be broken."""
    
    @property
    def mental_status(self) -> MentalStatus:
        """Get mental status."""
        data = self.db.mental_status
        if data:
            return MentalStatus.from_dict(data)
        return MentalStatus(subject_dbref=self.dbref, subject_name=self.key)
    
    @mental_status.setter
    def mental_status(self, status: MentalStatus) -> None:
        """Set mental status."""
        self.db.mental_status = status.to_dict()
    
    def save_mental_status(self, status: MentalStatus) -> None:
        """Save mental status."""
        self.db.mental_status = status.to_dict()
    
    @property
    def is_broken(self) -> bool:
        """Check if broken."""
        return self.mental_status.resistance_level == ResistanceLevel.BROKEN
    
    @property
    def resistance_level(self) -> ResistanceLevel:
        """Get current resistance level."""
        return self.mental_status.resistance_level


# =============================================================================
# PRESET TRIGGERS
# =============================================================================

PRESET_TRIGGERS = {
    "kneel_command": {
        "trigger_type": TriggerType.WORD,
        "stimulus": "kneel",
        "response": ConditionedResponse.KNEEL,
    },
    "freeze_command": {
        "trigger_type": TriggerType.WORD,
        "stimulus": "freeze",
        "response": ConditionedResponse.FREEZE,
    },
    "present_command": {
        "trigger_type": TriggerType.WORD,
        "stimulus": "present",
        "response": ConditionedResponse.PRESENT,
    },
    "cum_command": {
        "trigger_type": TriggerType.WORD,
        "stimulus": "cum",
        "response": ConditionedResponse.ORGASM,
    },
    "sleep_command": {
        "trigger_type": TriggerType.WORD,
        "stimulus": "sleep",
        "response": ConditionedResponse.SLEEP,
    },
    "heat_trigger": {
        "trigger_type": TriggerType.TOUCH,
        "stimulus": "inner thigh",
        "response": ConditionedResponse.HEAT,
    },
    "letdown_trigger": {
        "trigger_type": TriggerType.TOUCH,
        "stimulus": "nipple",
        "response": ConditionedResponse.LACTATE,
    },
    "bell_response": {
        "trigger_type": TriggerType.SOUND,
        "stimulus": "bell",
        "response": ConditionedResponse.AROUSAL,
    },
}


__all__ = [
    "ResistanceLevel",
    "BreakingMethod",
    "TriggerType",
    "ConditionedResponse",
    "MentalState",
    "ConditionedTrigger",
    "BreakingSession",
    "MentalStatus",
    "BreakingMixin",
    "PRESET_TRIGGERS",
]
