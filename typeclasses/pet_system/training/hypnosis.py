"""
Hypnosis System
===============

Mind control through hypnosis:
- Trance induction
- Suggestion implantation
- Trigger installation
- Memory manipulation
"""

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any, Tuple
from enum import Enum
from datetime import datetime, timedelta
import random


# =============================================================================
# ENUMS
# =============================================================================

class TranceDepth(Enum):
    """Depth of hypnotic trance."""
    AWAKE = "awake"              # Not in trance
    LIGHT = "light"              # Light relaxation
    MEDIUM = "medium"            # Responsive to suggestion
    DEEP = "deep"                # Highly suggestible
    SOMNAMBULISTIC = "somnambulistic"  # Complete control


class SuggestionType(Enum):
    """Types of hypnotic suggestions."""
    BEHAVIOR = "behavior"        # Do something
    BELIEF = "belief"            # Believe something
    SENSATION = "sensation"      # Feel something
    EMOTION = "emotion"          # Feel emotion
    MEMORY = "memory"            # Remember/forget
    IDENTITY = "identity"        # Who they are
    TRIGGER = "trigger"          # Install trigger


class SuggestionStrength(Enum):
    """How strong a suggestion is."""
    WEAK = "weak"               # Easy to break
    MODERATE = "moderate"       # Requires effort
    STRONG = "strong"           # Difficult to break
    PERMANENT = "permanent"     # Nearly unbreakable


# =============================================================================
# TRANCE STATE
# =============================================================================

@dataclass
class TranceState:
    """Current hypnotic trance state."""
    depth: TranceDepth = TranceDepth.AWAKE
    
    # Hypnotist
    hypnotist_dbref: str = ""
    hypnotist_name: str = ""
    
    # Stats
    susceptibility: int = 50     # Base susceptibility (0-100)
    current_depth_value: int = 0  # 0-100, determines TranceDepth
    
    # Trance history
    times_hypnotized: int = 0
    total_trance_time: int = 0   # In minutes
    
    # Session
    trance_start: Optional[datetime] = None
    
    def get_depth(self) -> TranceDepth:
        """Get trance depth based on value."""
        if self.current_depth_value <= 0:
            return TranceDepth.AWAKE
        elif self.current_depth_value <= 25:
            return TranceDepth.LIGHT
        elif self.current_depth_value <= 50:
            return TranceDepth.MEDIUM
        elif self.current_depth_value <= 75:
            return TranceDepth.DEEP
        else:
            return TranceDepth.SOMNAMBULISTIC
    
    def deepen(self, amount: int = 10) -> Tuple[TranceDepth, str]:
        """Deepen the trance."""
        old_depth = self.get_depth()
        self.current_depth_value = min(100, self.current_depth_value + amount)
        new_depth = self.get_depth()
        self.depth = new_depth
        
        if new_depth != old_depth:
            return new_depth, f"Trance deepens to {new_depth.value} level."
        return new_depth, "Trance deepens slightly."
    
    def lighten(self, amount: int = 10) -> Tuple[TranceDepth, str]:
        """Lighten the trance."""
        old_depth = self.get_depth()
        self.current_depth_value = max(0, self.current_depth_value - amount)
        new_depth = self.get_depth()
        self.depth = new_depth
        
        if new_depth == TranceDepth.AWAKE:
            return new_depth, "Emerges from trance completely."
        elif new_depth != old_depth:
            return new_depth, f"Trance lightens to {new_depth.value} level."
        return new_depth, "Trance lightens slightly."
    
    def wake(self) -> str:
        """Wake from trance."""
        if self.trance_start:
            duration = (datetime.now() - self.trance_start).total_seconds() / 60
            self.total_trance_time += int(duration)
        
        self.current_depth_value = 0
        self.depth = TranceDepth.AWAKE
        self.trance_start = None
        
        return "Eyes flutter open, slowly returning to awareness."
    
    def enter_trance(self, hypnotist_dbref: str, hypnotist_name: str) -> str:
        """Enter initial trance state."""
        self.hypnotist_dbref = hypnotist_dbref
        self.hypnotist_name = hypnotist_name
        self.current_depth_value = 20
        self.depth = TranceDepth.LIGHT
        self.trance_start = datetime.now()
        self.times_hypnotized += 1
        
        return "Eyes grow heavy, slipping into a light trance."
    
    def is_in_trance(self) -> bool:
        """Check if currently in trance."""
        return self.depth != TranceDepth.AWAKE
    
    def get_suggestion_resistance(self) -> int:
        """Get resistance to suggestions based on depth."""
        depth_modifier = {
            TranceDepth.AWAKE: 100,
            TranceDepth.LIGHT: 70,
            TranceDepth.MEDIUM: 40,
            TranceDepth.DEEP: 20,
            TranceDepth.SOMNAMBULISTIC: 5,
        }
        
        base_resist = 100 - self.susceptibility
        depth_mod = depth_modifier.get(self.depth, 100)
        
        return int(base_resist * depth_mod / 100)
    
    def to_dict(self) -> dict:
        return {
            "depth": self.depth.value,
            "hypnotist_dbref": self.hypnotist_dbref,
            "hypnotist_name": self.hypnotist_name,
            "susceptibility": self.susceptibility,
            "current_depth_value": self.current_depth_value,
            "times_hypnotized": self.times_hypnotized,
            "total_trance_time": self.total_trance_time,
            "trance_start": self.trance_start.isoformat() if self.trance_start else None,
        }
    
    @classmethod
    def from_dict(cls, data: dict) -> "TranceState":
        state = cls()
        state.depth = TranceDepth(data.get("depth", "awake"))
        state.hypnotist_dbref = data.get("hypnotist_dbref", "")
        state.hypnotist_name = data.get("hypnotist_name", "")
        state.susceptibility = data.get("susceptibility", 50)
        state.current_depth_value = data.get("current_depth_value", 0)
        state.times_hypnotized = data.get("times_hypnotized", 0)
        state.total_trance_time = data.get("total_trance_time", 0)
        
        if data.get("trance_start"):
            state.trance_start = datetime.fromisoformat(data["trance_start"])
        
        return state


# =============================================================================
# SUGGESTION
# =============================================================================

@dataclass
class HypnoticSuggestion:
    """A hypnotic suggestion implanted in the mind."""
    suggestion_id: str
    
    # Type and content
    suggestion_type: SuggestionType = SuggestionType.BEHAVIOR
    content: str = ""            # The actual suggestion
    
    # Trigger (if applicable)
    trigger_word: str = ""       # Word that activates
    trigger_situation: str = ""  # Situation that activates
    
    # Strength
    strength: SuggestionStrength = SuggestionStrength.MODERATE
    strength_value: int = 50     # 0-100
    
    # Source
    hypnotist_dbref: str = ""
    hypnotist_name: str = ""
    
    # Timestamps
    implanted_at: Optional[datetime] = None
    last_activated: Optional[datetime] = None
    activation_count: int = 0
    
    # Decay
    decays: bool = True
    decay_rate: int = 5          # Per week
    
    # Active
    is_active: bool = True
    
    def activate(self) -> Tuple[bool, str]:
        """Activate the suggestion."""
        if not self.is_active:
            return False, ""
        
        self.last_activated = datetime.now()
        self.activation_count += 1
        
        return True, self.content
    
    def resist(self, willpower: int) -> bool:
        """
        Attempt to resist the suggestion.
        Returns True if resisted.
        """
        resist_dc = self.strength_value // 2
        roll = random.randint(1, 20) + willpower
        
        if roll >= resist_dc:
            # Resisted - weaken suggestion
            self.strength_value = max(0, self.strength_value - 10)
            if self.strength_value <= 0:
                self.is_active = False
            return True
        
        return False
    
    def reinforce(self, amount: int = 10) -> int:
        """Reinforce the suggestion."""
        self.strength_value = min(100, self.strength_value + amount)
        return self.strength_value
    
    def apply_decay(self) -> int:
        """Apply decay. Returns new strength."""
        if not self.decays:
            return self.strength_value
        
        if not self.implanted_at:
            return self.strength_value
        
        weeks = (datetime.now() - self.implanted_at).days // 7
        decay = weeks * self.decay_rate
        
        self.strength_value = max(0, self.strength_value - decay)
        if self.strength_value <= 0:
            self.is_active = False
        
        return self.strength_value
    
    def to_dict(self) -> dict:
        return {
            "suggestion_id": self.suggestion_id,
            "suggestion_type": self.suggestion_type.value,
            "content": self.content,
            "trigger_word": self.trigger_word,
            "trigger_situation": self.trigger_situation,
            "strength": self.strength.value,
            "strength_value": self.strength_value,
            "hypnotist_dbref": self.hypnotist_dbref,
            "hypnotist_name": self.hypnotist_name,
            "implanted_at": self.implanted_at.isoformat() if self.implanted_at else None,
            "last_activated": self.last_activated.isoformat() if self.last_activated else None,
            "activation_count": self.activation_count,
            "decays": self.decays,
            "decay_rate": self.decay_rate,
            "is_active": self.is_active,
        }
    
    @classmethod
    def from_dict(cls, data: dict) -> "HypnoticSuggestion":
        suggestion = cls(suggestion_id=data["suggestion_id"])
        suggestion.suggestion_type = SuggestionType(data.get("suggestion_type", "behavior"))
        suggestion.content = data.get("content", "")
        suggestion.trigger_word = data.get("trigger_word", "")
        suggestion.trigger_situation = data.get("trigger_situation", "")
        suggestion.strength = SuggestionStrength(data.get("strength", "moderate"))
        suggestion.strength_value = data.get("strength_value", 50)
        suggestion.hypnotist_dbref = data.get("hypnotist_dbref", "")
        suggestion.hypnotist_name = data.get("hypnotist_name", "")
        suggestion.decays = data.get("decays", True)
        suggestion.decay_rate = data.get("decay_rate", 5)
        suggestion.is_active = data.get("is_active", True)
        suggestion.activation_count = data.get("activation_count", 0)
        
        if data.get("implanted_at"):
            suggestion.implanted_at = datetime.fromisoformat(data["implanted_at"])
        if data.get("last_activated"):
            suggestion.last_activated = datetime.fromisoformat(data["last_activated"])
        
        return suggestion


# =============================================================================
# INDUCTION TECHNIQUES
# =============================================================================

@dataclass
class InductionTechnique:
    """A hypnotic induction technique."""
    key: str
    name: str
    description: str
    
    # Effectiveness
    base_depth: int = 20         # Initial depth achieved
    deepening_rate: int = 10     # Depth gain per application
    
    # Requirements
    requires_eye_contact: bool = True
    requires_relaxation: bool = True
    requires_focus_object: bool = False
    
    # Difficulty
    difficulty: int = 10         # DC to perform
    min_skill: int = 1


INDUCTION_TECHNIQUES = {
    "eye_fixation": InductionTechnique(
        key="eye_fixation",
        name="Eye Fixation",
        description="Have the subject focus on a point until their eyes tire.",
        base_depth=25,
        deepening_rate=10,
        requires_focus_object=True,
    ),
    
    "progressive_relaxation": InductionTechnique(
        key="progressive_relaxation",
        name="Progressive Relaxation",
        description="Guide the subject through relaxing each part of their body.",
        base_depth=30,
        deepening_rate=15,
        requires_eye_contact=False,
    ),
    
    "countdown": InductionTechnique(
        key="countdown",
        name="Countdown Induction",
        description="Count down while deepening the trance.",
        base_depth=20,
        deepening_rate=12,
        difficulty=8,
    ),
    
    "confusion": InductionTechnique(
        key="confusion",
        name="Confusion Technique",
        description="Overwhelm the conscious mind with complexity.",
        base_depth=35,
        deepening_rate=8,
        difficulty=15,
        min_skill=3,
    ),
    
    "instant": InductionTechnique(
        key="instant",
        name="Instant Induction",
        description="Rapid induction for already trained subjects.",
        base_depth=40,
        deepening_rate=20,
        difficulty=18,
        min_skill=4,
    ),
    
    "fractionation": InductionTechnique(
        key="fractionation",
        name="Fractionation",
        description="Repeatedly bringing in and out of trance to deepen.",
        base_depth=15,
        deepening_rate=25,
        difficulty=12,
        min_skill=2,
    ),
}


def get_induction(key: str) -> Optional[InductionTechnique]:
    """Get induction technique by key."""
    return INDUCTION_TECHNIQUES.get(key)


# =============================================================================
# HYPNOSIS SYSTEM
# =============================================================================

class HypnosisSystem:
    """
    Manages hypnosis operations.
    """
    
    @staticmethod
    def generate_id() -> str:
        """Generate suggestion ID."""
        timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
        rand = random.randint(1000, 9999)
        return f"SUG-{timestamp}-{rand}"
    
    @staticmethod
    def attempt_induction(
        hypnotist,
        subject,
        technique_key: str = "eye_fixation",
    ) -> Tuple[bool, str, Optional[TranceState]]:
        """
        Attempt to hypnotize a subject.
        """
        technique = get_induction(technique_key)
        if not technique:
            return False, f"Unknown technique: {technique_key}", None
        
        # Check skill requirement
        hypnotist_skill = getattr(hypnotist, 'hypnosis_skill', 1)
        if hypnotist_skill < technique.min_skill:
            return False, f"Requires hypnosis skill {technique.min_skill}.", None
        
        # Get or create trance state
        if hasattr(subject, 'trance_state'):
            trance = subject.trance_state
        else:
            trance = TranceState()
        
        # If already in trance with someone else, harder
        if trance.is_in_trance() and trance.hypnotist_dbref != hypnotist.dbref:
            return False, f"{subject.key} is already entranced by {trance.hypnotist_name}.", None
        
        # Roll for success
        roll = random.randint(1, 20) + hypnotist_skill
        resist = trance.get_suggestion_resistance()
        
        if roll < technique.difficulty + (resist // 10):
            return False, f"{subject.key} resists the induction.", None
        
        # Success
        if trance.is_in_trance():
            # Deepen existing trance
            new_depth, message = trance.deepen(technique.deepening_rate)
        else:
            # Enter new trance
            message = trance.enter_trance(hypnotist.dbref, hypnotist.key)
        
        return True, f"{subject.key} {message}", trance
    
    @staticmethod
    def deepen_trance(
        trance: TranceState,
        amount: int = 10,
    ) -> Tuple[TranceDepth, str]:
        """Deepen an existing trance."""
        if not trance.is_in_trance():
            return TranceDepth.AWAKE, "Not in trance."
        
        return trance.deepen(amount)
    
    @staticmethod
    def implant_suggestion(
        hypnotist,
        subject,
        trance: TranceState,
        suggestion_type: SuggestionType,
        content: str,
        trigger_word: str = "",
    ) -> Tuple[bool, str, Optional[HypnoticSuggestion]]:
        """
        Implant a suggestion in a hypnotized subject.
        """
        if not trance.is_in_trance():
            return False, "Subject must be in trance.", None
        
        # Calculate suggestion strength based on trance depth
        depth_strength = {
            TranceDepth.LIGHT: 20,
            TranceDepth.MEDIUM: 40,
            TranceDepth.DEEP: 70,
            TranceDepth.SOMNAMBULISTIC: 90,
        }
        
        base_strength = depth_strength.get(trance.depth, 0)
        
        # Check resistance
        resist = trance.get_suggestion_resistance()
        roll = random.randint(1, 100)
        
        if roll < resist:
            return False, "Subject resists the suggestion.", None
        
        # Create suggestion
        suggestion = HypnoticSuggestion(
            suggestion_id=HypnosisSystem.generate_id(),
            suggestion_type=suggestion_type,
            content=content,
            trigger_word=trigger_word,
            strength_value=base_strength,
            hypnotist_dbref=hypnotist.dbref,
            hypnotist_name=hypnotist.key,
            implanted_at=datetime.now(),
        )
        
        # Determine strength category
        if base_strength >= 80:
            suggestion.strength = SuggestionStrength.STRONG
        elif base_strength >= 50:
            suggestion.strength = SuggestionStrength.MODERATE
        else:
            suggestion.strength = SuggestionStrength.WEAK
        
        return True, f"Suggestion implanted: '{content}'", suggestion
    
    @staticmethod
    def check_triggers(
        suggestions: List[HypnoticSuggestion],
        trigger_word: str,
        subject_willpower: int = 10,
    ) -> List[Tuple[str, bool]]:
        """
        Check if any suggestions are triggered.
        Returns list of (content, resisted).
        """
        results = []
        
        for suggestion in suggestions:
            if not suggestion.is_active:
                continue
            
            if suggestion.trigger_word and trigger_word.lower() == suggestion.trigger_word.lower():
                # Check if resisted
                resisted = suggestion.resist(subject_willpower)
                
                if not resisted:
                    suggestion.activate()
                    results.append((suggestion.content, False))
                else:
                    results.append((suggestion.content, True))
        
        return results
    
    @staticmethod
    def wake_subject(trance: TranceState) -> str:
        """Wake a subject from trance."""
        return trance.wake()


# =============================================================================
# HYPNOSIS MIXINS
# =============================================================================

class HypnotizableMixin:
    """
    Mixin for characters that can be hypnotized.
    """
    
    @property
    def trance_state(self) -> TranceState:
        """Get trance state."""
        data = self.attributes.get("trance_state")
        if data:
            return TranceState.from_dict(data)
        return TranceState()
    
    @trance_state.setter
    def trance_state(self, state: TranceState):
        """Set trance state."""
        self.attributes.add("trance_state", state.to_dict())
    
    @property
    def hypnotic_suggestions(self) -> List[HypnoticSuggestion]:
        """Get active suggestions."""
        data = self.attributes.get("hypnotic_suggestions", [])
        return [HypnoticSuggestion.from_dict(s) for s in data]
    
    @hypnotic_suggestions.setter
    def hypnotic_suggestions(self, suggestions: List[HypnoticSuggestion]):
        """Set suggestions."""
        data = [s.to_dict() for s in suggestions]
        self.attributes.add("hypnotic_suggestions", data)
    
    def add_suggestion(self, suggestion: HypnoticSuggestion) -> None:
        """Add a hypnotic suggestion."""
        suggestions = self.hypnotic_suggestions
        suggestions.append(suggestion)
        self.hypnotic_suggestions = suggestions
    
    def is_in_trance(self) -> bool:
        """Check if in trance."""
        return self.trance_state.is_in_trance()
    
    def get_trance_depth(self) -> TranceDepth:
        """Get current trance depth."""
        return self.trance_state.depth
    
    def check_hypnotic_triggers(self, word: str) -> List[str]:
        """
        Check if a word triggers any suggestions.
        Returns list of triggered responses.
        """
        suggestions = self.hypnotic_suggestions
        willpower = getattr(self, 'willpower', 10)
        
        results = HypnosisSystem.check_triggers(suggestions, word, willpower)
        
        # Update suggestions
        self.hypnotic_suggestions = suggestions
        
        responses = []
        for content, resisted in results:
            if not resisted:
                responses.append(content)
        
        return responses


class HypnotistMixin:
    """
    Mixin for characters that can hypnotize others.
    """
    
    @property
    def hypnosis_skill(self) -> int:
        """Get hypnosis skill level."""
        return self.attributes.get("hypnosis_skill", 1)
    
    @hypnosis_skill.setter
    def hypnosis_skill(self, value: int):
        """Set hypnosis skill."""
        self.attributes.add("hypnosis_skill", max(1, min(10, value)))
    
    @property
    def subjects_entranced(self) -> List[str]:
        """Get list of currently entranced subjects."""
        return self.attributes.get("subjects_entranced", [])
    
    def add_subject(self, subject_dbref: str) -> None:
        """Add an entranced subject."""
        subjects = self.subjects_entranced
        if subject_dbref not in subjects:
            subjects.append(subject_dbref)
            self.attributes.add("subjects_entranced", subjects)
    
    def remove_subject(self, subject_dbref: str) -> None:
        """Remove a subject."""
        subjects = self.subjects_entranced
        if subject_dbref in subjects:
            subjects.remove(subject_dbref)
            self.attributes.add("subjects_entranced", subjects)


__all__ = [
    "TranceDepth",
    "SuggestionType",
    "SuggestionStrength",
    "TranceState",
    "HypnoticSuggestion",
    "InductionTechnique",
    "INDUCTION_TECHNIQUES",
    "get_induction",
    "HypnosisSystem",
    "HypnotizableMixin",
    "HypnotistMixin",
]
