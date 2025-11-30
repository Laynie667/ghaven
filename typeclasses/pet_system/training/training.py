"""
Training System
===============

Advanced training mechanics:
- Breaking resistance
- Conditioning behaviors
- Obedience tracking
- Reward/punishment effects
"""

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any, Tuple, Callable
from enum import Enum
from datetime import datetime, timedelta
import random


# =============================================================================
# ENUMS
# =============================================================================

class TrainingStage(Enum):
    """Stages of breaking/training."""
    WILD = "wild"                # Untrained, high resistance
    RESISTANT = "resistant"      # Fighting training
    LEARNING = "learning"        # Beginning to accept
    COMPLIANT = "compliant"      # Following orders
    EAGER = "eager"              # Actively pleasing
    BROKEN = "broken"            # Completely submissive
    DEVOTED = "devoted"          # Bonded and loyal


class ResistanceType(Enum):
    """Types of resistance."""
    PHYSICAL = "physical"        # Fighting, struggling
    MENTAL = "mental"            # Willpower, defiance
    EMOTIONAL = "emotional"      # Pride, dignity
    SEXUAL = "sexual"            # Sexual reluctance


class ConditioningType(Enum):
    """Types of conditioned behaviors."""
    POSTURE = "posture"          # How they stand/sit
    SPEECH = "speech"            # How they speak
    RESPONSE = "response"        # Automatic responses
    TRIGGER = "trigger"          # Triggered behaviors
    AROUSAL = "arousal"          # Sexual conditioning
    FEAR = "fear"                # Fear conditioning
    PLEASURE = "pleasure"        # Pleasure association
    SUBMISSION = "submission"    # Submissive behaviors


class ReinforcementType(Enum):
    """Types of reinforcement."""
    POSITIVE = "positive"        # Rewards
    NEGATIVE = "negative"        # Punishment
    PRAISE = "praise"            # Verbal praise
    CRITICISM = "criticism"      # Verbal criticism
    PHYSICAL_REWARD = "physical_reward"   # Pleasant touch
    PHYSICAL_PUNISHMENT = "physical_punishment"  # Pain


# =============================================================================
# RESISTANCE STATE
# =============================================================================

@dataclass
class ResistanceState:
    """Tracks resistance during training."""
    # Resistance levels (0-100, higher = more resistant)
    physical: int = 50
    mental: int = 50
    emotional: int = 50
    sexual: int = 50
    
    # Base values (natural resistance)
    base_physical: int = 50
    base_mental: int = 50
    base_emotional: int = 50
    base_sexual: int = 50
    
    # Recovery rate per hour
    recovery_rate: int = 5
    
    # Last update
    last_update: Optional[datetime] = None
    
    def get_total_resistance(self) -> int:
        """Get average resistance."""
        return (self.physical + self.mental + self.emotional + self.sexual) // 4
    
    def get_resistance(self, resistance_type: ResistanceType) -> int:
        """Get specific resistance."""
        return getattr(self, resistance_type.value, 50)
    
    def reduce_resistance(self, resistance_type: ResistanceType, amount: int) -> int:
        """Reduce resistance. Returns new value."""
        current = self.get_resistance(resistance_type)
        new_value = max(0, current - amount)
        setattr(self, resistance_type.value, new_value)
        return new_value
    
    def recover(self) -> None:
        """Recover resistance toward base values."""
        if not self.last_update:
            self.last_update = datetime.now()
            return
        
        hours = (datetime.now() - self.last_update).total_seconds() / 3600
        recovery = int(hours * self.recovery_rate)
        
        if recovery > 0:
            # Recover toward base
            for attr in ["physical", "mental", "emotional", "sexual"]:
                current = getattr(self, attr)
                base = getattr(self, f"base_{attr}")
                
                if current < base:
                    setattr(self, attr, min(base, current + recovery))
            
            self.last_update = datetime.now()
    
    def get_stage(self) -> TrainingStage:
        """Get current training stage based on resistance."""
        total = self.get_total_resistance()
        
        if total >= 80:
            return TrainingStage.WILD
        elif total >= 60:
            return TrainingStage.RESISTANT
        elif total >= 40:
            return TrainingStage.LEARNING
        elif total >= 25:
            return TrainingStage.COMPLIANT
        elif total >= 10:
            return TrainingStage.EAGER
        elif total >= 1:
            return TrainingStage.BROKEN
        else:
            return TrainingStage.DEVOTED
    
    def to_dict(self) -> dict:
        return {
            "physical": self.physical,
            "mental": self.mental,
            "emotional": self.emotional,
            "sexual": self.sexual,
            "base_physical": self.base_physical,
            "base_mental": self.base_mental,
            "base_emotional": self.base_emotional,
            "base_sexual": self.base_sexual,
            "recovery_rate": self.recovery_rate,
            "last_update": self.last_update.isoformat() if self.last_update else None,
        }
    
    @classmethod
    def from_dict(cls, data: dict) -> "ResistanceState":
        state = cls()
        state.physical = data.get("physical", 50)
        state.mental = data.get("mental", 50)
        state.emotional = data.get("emotional", 50)
        state.sexual = data.get("sexual", 50)
        state.base_physical = data.get("base_physical", 50)
        state.base_mental = data.get("base_mental", 50)
        state.base_emotional = data.get("base_emotional", 50)
        state.base_sexual = data.get("base_sexual", 50)
        state.recovery_rate = data.get("recovery_rate", 5)
        
        if data.get("last_update"):
            state.last_update = datetime.fromisoformat(data["last_update"])
        
        return state


# =============================================================================
# CONDITIONED BEHAVIOR
# =============================================================================

@dataclass
class ConditionedBehavior:
    """A trained/conditioned behavior."""
    behavior_id: str
    name: str
    
    # Type
    conditioning_type: ConditioningType = ConditioningType.RESPONSE
    
    # Trigger (what activates it)
    trigger: str = ""            # Word, action, or situation
    trigger_type: str = "word"   # word, action, situation, arousal_level
    
    # Response
    response: str = ""           # What they do/say
    response_type: str = "say"   # say, emote, feel, do
    
    # Strength (0-100)
    strength: int = 0            # How ingrained
    
    # Resistance to fight it
    can_resist: bool = True
    resist_dc: int = 15          # DC to resist
    
    # Decay
    decays: bool = True
    decay_rate: int = 1          # Per day without reinforcement
    last_triggered: Optional[datetime] = None
    last_reinforced: Optional[datetime] = None
    
    def trigger_behavior(self, character_willpower: int = 10) -> Tuple[bool, str]:
        """
        Attempt to trigger the behavior.
        Returns (triggered, response).
        """
        self.last_triggered = datetime.now()
        
        # Check if they resist
        if self.can_resist:
            roll = random.randint(1, 20) + character_willpower
            if roll >= self.resist_dc + (self.strength // 10):
                return False, f"resists the urge to {self.response}"
        
        return True, self.response
    
    def reinforce(self, amount: int = 5) -> int:
        """Reinforce the conditioning. Returns new strength."""
        self.strength = min(100, self.strength + amount)
        self.last_reinforced = datetime.now()
        return self.strength
    
    def decay(self) -> int:
        """Apply decay. Returns new strength."""
        if not self.decays:
            return self.strength
        
        if not self.last_reinforced:
            return self.strength
        
        days = (datetime.now() - self.last_reinforced).days
        decay_amount = days * self.decay_rate
        
        self.strength = max(0, self.strength - decay_amount)
        return self.strength
    
    def is_active(self) -> bool:
        """Check if conditioning is still active."""
        return self.strength > 0
    
    def to_dict(self) -> dict:
        return {
            "behavior_id": self.behavior_id,
            "name": self.name,
            "conditioning_type": self.conditioning_type.value,
            "trigger": self.trigger,
            "trigger_type": self.trigger_type,
            "response": self.response,
            "response_type": self.response_type,
            "strength": self.strength,
            "can_resist": self.can_resist,
            "resist_dc": self.resist_dc,
            "decays": self.decays,
            "decay_rate": self.decay_rate,
            "last_triggered": self.last_triggered.isoformat() if self.last_triggered else None,
            "last_reinforced": self.last_reinforced.isoformat() if self.last_reinforced else None,
        }
    
    @classmethod
    def from_dict(cls, data: dict) -> "ConditionedBehavior":
        behavior = cls(
            behavior_id=data["behavior_id"],
            name=data["name"],
        )
        behavior.conditioning_type = ConditioningType(data.get("conditioning_type", "response"))
        behavior.trigger = data.get("trigger", "")
        behavior.trigger_type = data.get("trigger_type", "word")
        behavior.response = data.get("response", "")
        behavior.response_type = data.get("response_type", "say")
        behavior.strength = data.get("strength", 0)
        behavior.can_resist = data.get("can_resist", True)
        behavior.resist_dc = data.get("resist_dc", 15)
        behavior.decays = data.get("decays", True)
        behavior.decay_rate = data.get("decay_rate", 1)
        
        if data.get("last_triggered"):
            behavior.last_triggered = datetime.fromisoformat(data["last_triggered"])
        if data.get("last_reinforced"):
            behavior.last_reinforced = datetime.fromisoformat(data["last_reinforced"])
        
        return behavior


# =============================================================================
# PRESET CONDITIONED BEHAVIORS
# =============================================================================

PRESET_BEHAVIORS = {
    # Speech conditioning
    "address_master": ConditionedBehavior(
        behavior_id="address_master",
        name="Address as Master",
        conditioning_type=ConditioningType.SPEECH,
        trigger="speaking to owner",
        trigger_type="situation",
        response="addresses them as Master/Mistress",
        response_type="say",
        resist_dc=12,
    ),
    
    "speak_third_person": ConditionedBehavior(
        behavior_id="speak_third_person",
        name="Speak in Third Person",
        conditioning_type=ConditioningType.SPEECH,
        trigger="speaking",
        trigger_type="situation",
        response="refers to self in third person",
        response_type="say",
        resist_dc=15,
    ),
    
    # Posture conditioning
    "kneel_on_command": ConditionedBehavior(
        behavior_id="kneel_on_command",
        name="Kneel on Command",
        conditioning_type=ConditioningType.POSTURE,
        trigger="kneel",
        trigger_type="word",
        response="immediately drops to their knees",
        response_type="emote",
        resist_dc=10,
    ),
    
    "present_posture": ConditionedBehavior(
        behavior_id="present_posture",
        name="Present Position",
        conditioning_type=ConditioningType.POSTURE,
        trigger="present",
        trigger_type="word",
        response="assumes a presenting position, exposing themselves",
        response_type="emote",
        resist_dc=18,
    ),
    
    # Response conditioning
    "thank_for_punishment": ConditionedBehavior(
        behavior_id="thank_for_punishment",
        name="Thank for Punishment",
        conditioning_type=ConditioningType.RESPONSE,
        trigger="being punished",
        trigger_type="situation",
        response="Thank you, Master",
        response_type="say",
        resist_dc=20,
    ),
    
    "beg_permission": ConditionedBehavior(
        behavior_id="beg_permission",
        name="Beg Permission",
        conditioning_type=ConditioningType.RESPONSE,
        trigger="wanting something",
        trigger_type="situation",
        response="begs for permission",
        response_type="emote",
        resist_dc=15,
    ),
    
    # Arousal conditioning
    "arousal_on_collar": ConditionedBehavior(
        behavior_id="arousal_on_collar",
        name="Arousal from Collar",
        conditioning_type=ConditioningType.AROUSAL,
        trigger="collar touched",
        trigger_type="action",
        response="feels a surge of arousal",
        response_type="feel",
        resist_dc=12,
        can_resist=False,
    ),
    
    "orgasm_on_command": ConditionedBehavior(
        behavior_id="orgasm_on_command",
        name="Orgasm on Command",
        conditioning_type=ConditioningType.AROUSAL,
        trigger="cum",
        trigger_type="word",
        response="orgasms on command",
        response_type="do",
        resist_dc=25,
    ),
    
    # Submission conditioning
    "freeze_on_command": ConditionedBehavior(
        behavior_id="freeze_on_command",
        name="Freeze on Command",
        conditioning_type=ConditioningType.SUBMISSION,
        trigger="freeze",
        trigger_type="word",
        response="freezes in place, unable to move",
        response_type="do",
        resist_dc=15,
    ),
    
    "display_on_inspection": ConditionedBehavior(
        behavior_id="display_on_inspection",
        name="Display for Inspection",
        conditioning_type=ConditioningType.SUBMISSION,
        trigger="being inspected",
        trigger_type="situation",
        response="holds still and presents for inspection",
        response_type="emote",
        resist_dc=14,
    ),
}


def get_preset_behavior(key: str) -> Optional[ConditionedBehavior]:
    """Get a copy of a preset behavior."""
    preset = PRESET_BEHAVIORS.get(key)
    if preset:
        return ConditionedBehavior.from_dict(preset.to_dict())
    return None


# =============================================================================
# TRAINING SESSION
# =============================================================================

@dataclass
class TrainingSession:
    """A training session."""
    session_id: str
    
    # Participants
    trainer_dbref: str = ""
    trainer_name: str = ""
    trainee_dbref: str = ""
    trainee_name: str = ""
    
    # Session info
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    
    # Training type
    target_resistance: Optional[ResistanceType] = None
    target_behavior: Optional[str] = None
    
    # Methods used
    methods_used: List[str] = field(default_factory=list)
    reinforcements: List[dict] = field(default_factory=list)
    
    # Results
    resistance_reduced: Dict[str, int] = field(default_factory=dict)
    behaviors_conditioned: List[str] = field(default_factory=list)
    
    # Notes
    notes: str = ""
    
    def add_reinforcement(
        self,
        reinforcement_type: ReinforcementType,
        intensity: int = 5,
        description: str = "",
    ) -> None:
        """Record a reinforcement action."""
        self.reinforcements.append({
            "type": reinforcement_type.value,
            "intensity": intensity,
            "description": description,
            "timestamp": datetime.now().isoformat(),
        })
    
    def get_duration_minutes(self) -> int:
        """Get session duration in minutes."""
        if not self.start_time:
            return 0
        
        end = self.end_time or datetime.now()
        return int((end - self.start_time).total_seconds() / 60)
    
    def get_summary(self) -> str:
        """Get session summary."""
        lines = [
            f"=== Training Session ===",
            f"Trainer: {self.trainer_name}",
            f"Trainee: {self.trainee_name}",
            f"Duration: {self.get_duration_minutes()} minutes",
        ]
        
        if self.resistance_reduced:
            lines.append("Resistance Reduced:")
            for rtype, amount in self.resistance_reduced.items():
                lines.append(f"  {rtype}: -{amount}")
        
        if self.behaviors_conditioned:
            lines.append(f"Behaviors Conditioned: {', '.join(self.behaviors_conditioned)}")
        
        return "\n".join(lines)
    
    def to_dict(self) -> dict:
        return {
            "session_id": self.session_id,
            "trainer_dbref": self.trainer_dbref,
            "trainer_name": self.trainer_name,
            "trainee_dbref": self.trainee_dbref,
            "trainee_name": self.trainee_name,
            "start_time": self.start_time.isoformat() if self.start_time else None,
            "end_time": self.end_time.isoformat() if self.end_time else None,
            "target_resistance": self.target_resistance.value if self.target_resistance else None,
            "target_behavior": self.target_behavior,
            "methods_used": self.methods_used,
            "reinforcements": self.reinforcements,
            "resistance_reduced": self.resistance_reduced,
            "behaviors_conditioned": self.behaviors_conditioned,
            "notes": self.notes,
        }


# =============================================================================
# TRAINING METHODS
# =============================================================================

@dataclass
class TrainingMethod:
    """A method of training."""
    key: str
    name: str
    description: str
    
    # What it affects
    targets_resistance: List[ResistanceType] = field(default_factory=list)
    resistance_reduction: int = 5       # Base reduction per use
    
    # Conditioning
    can_condition: bool = False
    conditioning_strength: int = 5      # How much to strengthen behavior
    
    # Requirements
    requires_restraint: bool = False
    requires_arousal: int = 0           # Min arousal level
    requires_submission: int = 0        # Min submission level
    
    # Effects on trainee
    arousal_change: int = 0
    pain_level: int = 0
    humiliation_level: int = 0
    
    # Trainer requirements
    min_skill: int = 0


TRAINING_METHODS = {
    # Physical methods
    "spanking": TrainingMethod(
        key="spanking",
        name="Spanking",
        description="Discipline through spanking.",
        targets_resistance=[ResistanceType.PHYSICAL, ResistanceType.EMOTIONAL],
        resistance_reduction=3,
        pain_level=3,
        humiliation_level=4,
    ),
    
    "bondage": TrainingMethod(
        key="bondage",
        name="Bondage",
        description="Restraint to reinforce helplessness.",
        targets_resistance=[ResistanceType.PHYSICAL, ResistanceType.MENTAL],
        resistance_reduction=4,
        requires_restraint=True,
    ),
    
    "edging": TrainingMethod(
        key="edging",
        name="Edging",
        description="Denial and control of pleasure.",
        targets_resistance=[ResistanceType.SEXUAL, ResistanceType.MENTAL],
        resistance_reduction=5,
        can_condition=True,
        conditioning_strength=3,
        arousal_change=30,
    ),
    
    "forced_orgasm": TrainingMethod(
        key="forced_orgasm",
        name="Forced Orgasm",
        description="Overwhelming with pleasure.",
        targets_resistance=[ResistanceType.SEXUAL, ResistanceType.EMOTIONAL],
        resistance_reduction=6,
        can_condition=True,
        conditioning_strength=5,
        arousal_change=50,
        requires_arousal=50,
    ),
    
    # Mental methods
    "verbal_degradation": TrainingMethod(
        key="verbal_degradation",
        name="Verbal Degradation",
        description="Breaking down pride through words.",
        targets_resistance=[ResistanceType.EMOTIONAL, ResistanceType.MENTAL],
        resistance_reduction=4,
        humiliation_level=6,
    ),
    
    "praise_reward": TrainingMethod(
        key="praise_reward",
        name="Praise and Reward",
        description="Positive reinforcement for good behavior.",
        targets_resistance=[ResistanceType.EMOTIONAL],
        resistance_reduction=2,
        can_condition=True,
        conditioning_strength=4,
    ),
    
    "position_training": TrainingMethod(
        key="position_training",
        name="Position Training",
        description="Drilling proper postures and positions.",
        targets_resistance=[ResistanceType.PHYSICAL],
        resistance_reduction=3,
        can_condition=True,
        conditioning_strength=6,
    ),
    
    "speech_training": TrainingMethod(
        key="speech_training",
        name="Speech Training",
        description="Training proper forms of address.",
        targets_resistance=[ResistanceType.MENTAL, ResistanceType.EMOTIONAL],
        resistance_reduction=3,
        can_condition=True,
        conditioning_strength=5,
    ),
    
    # Advanced methods
    "sensory_deprivation": TrainingMethod(
        key="sensory_deprivation",
        name="Sensory Deprivation",
        description="Isolation to break mental resistance.",
        targets_resistance=[ResistanceType.MENTAL],
        resistance_reduction=8,
        requires_restraint=True,
        min_skill=3,
    ),
    
    "pleasure_conditioning": TrainingMethod(
        key="pleasure_conditioning",
        name="Pleasure Conditioning",
        description="Associating obedience with pleasure.",
        targets_resistance=[ResistanceType.SEXUAL, ResistanceType.MENTAL],
        resistance_reduction=5,
        can_condition=True,
        conditioning_strength=8,
        arousal_change=20,
        min_skill=2,
    ),
    
    "pain_conditioning": TrainingMethod(
        key="pain_conditioning",
        name="Pain Conditioning",
        description="Teaching through carefully applied pain.",
        targets_resistance=[ResistanceType.PHYSICAL, ResistanceType.MENTAL],
        resistance_reduction=6,
        can_condition=True,
        conditioning_strength=6,
        pain_level=5,
        min_skill=3,
    ),
    
    "humiliation_training": TrainingMethod(
        key="humiliation_training",
        name="Humiliation Training",
        description="Breaking ego through embarrassment.",
        targets_resistance=[ResistanceType.EMOTIONAL],
        resistance_reduction=7,
        humiliation_level=8,
        min_skill=2,
    ),
}


def get_training_method(key: str) -> Optional[TrainingMethod]:
    """Get a training method by key."""
    return TRAINING_METHODS.get(key)


# =============================================================================
# TRAINING SYSTEM
# =============================================================================

class TrainingSystem:
    """
    Manages training operations.
    """
    
    @staticmethod
    def generate_id() -> str:
        """Generate session ID."""
        timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
        rand = random.randint(1000, 9999)
        return f"TRN-{timestamp}-{rand}"
    
    @staticmethod
    def start_session(
        trainer,
        trainee,
    ) -> TrainingSession:
        """Start a training session."""
        return TrainingSession(
            session_id=TrainingSystem.generate_id(),
            trainer_dbref=trainer.dbref,
            trainer_name=trainer.key,
            trainee_dbref=trainee.dbref,
            trainee_name=trainee.key,
            start_time=datetime.now(),
        )
    
    @staticmethod
    def apply_method(
        session: TrainingSession,
        trainee_resistance: ResistanceState,
        method_key: str,
        intensity: int = 5,
    ) -> Tuple[bool, str, Dict[str, int]]:
        """
        Apply a training method.
        Returns (success, message, resistance_changes).
        """
        method = get_training_method(method_key)
        if not method:
            return False, f"Unknown training method: {method_key}", {}
        
        session.methods_used.append(method_key)
        
        # Calculate effectiveness
        base_reduction = method.resistance_reduction
        reduction = int(base_reduction * (intensity / 5))
        
        # Apply to resistances
        changes = {}
        for resistance_type in method.targets_resistance:
            old_value = trainee_resistance.get_resistance(resistance_type)
            new_value = trainee_resistance.reduce_resistance(resistance_type, reduction)
            changes[resistance_type.value] = old_value - new_value
            
            # Track in session
            if resistance_type.value not in session.resistance_reduced:
                session.resistance_reduced[resistance_type.value] = 0
            session.resistance_reduced[resistance_type.value] += (old_value - new_value)
        
        # Build message
        stage = trainee_resistance.get_stage()
        msg = f"Applied {method.name}. {trainee_resistance.get_total_resistance()}% resistance remaining. Stage: {stage.value}"
        
        return True, msg, changes
    
    @staticmethod
    def condition_behavior(
        trainee_behaviors: Dict[str, ConditionedBehavior],
        behavior_key: str,
        strength_gain: int = 5,
    ) -> Tuple[bool, str]:
        """
        Condition or reinforce a behavior.
        """
        if behavior_key in trainee_behaviors:
            # Reinforce existing
            behavior = trainee_behaviors[behavior_key]
            new_strength = behavior.reinforce(strength_gain)
            return True, f"Reinforced {behavior.name}. Strength: {new_strength}%"
        else:
            # Create new from preset
            behavior = get_preset_behavior(behavior_key)
            if not behavior:
                return False, f"Unknown behavior: {behavior_key}"
            
            behavior.strength = strength_gain
            behavior.last_reinforced = datetime.now()
            trainee_behaviors[behavior_key] = behavior
            
            return True, f"Began conditioning {behavior.name}. Strength: {strength_gain}%"
    
    @staticmethod
    def check_trigger(
        trainee_behaviors: Dict[str, ConditionedBehavior],
        trigger_word: str,
        trainee_willpower: int = 10,
    ) -> List[Tuple[str, str]]:
        """
        Check if any behaviors are triggered.
        Returns list of (behavior_name, response).
        """
        triggered = []
        
        for behavior in trainee_behaviors.values():
            if not behavior.is_active():
                continue
            
            if behavior.trigger_type == "word" and trigger_word.lower() == behavior.trigger.lower():
                success, response = behavior.trigger_behavior(trainee_willpower)
                if success:
                    triggered.append((behavior.name, response))
        
        return triggered


# =============================================================================
# TRAINING MIXIN
# =============================================================================

class TraineeMixin:
    """
    Mixin for characters that can be trained.
    """
    
    @property
    def resistance_state(self) -> ResistanceState:
        """Get resistance state."""
        data = self.attributes.get("resistance_state")
        if data:
            state = ResistanceState.from_dict(data)
            state.recover()  # Apply recovery
            return state
        return ResistanceState()
    
    @resistance_state.setter
    def resistance_state(self, state: ResistanceState):
        """Set resistance state."""
        self.attributes.add("resistance_state", state.to_dict())
    
    @property
    def conditioned_behaviors(self) -> Dict[str, ConditionedBehavior]:
        """Get conditioned behaviors."""
        data = self.attributes.get("conditioned_behaviors", {})
        return {k: ConditionedBehavior.from_dict(v) for k, v in data.items()}
    
    @conditioned_behaviors.setter
    def conditioned_behaviors(self, behaviors: Dict[str, ConditionedBehavior]):
        """Set conditioned behaviors."""
        data = {k: v.to_dict() for k, v in behaviors.items()}
        self.attributes.add("conditioned_behaviors", data)
    
    def get_training_stage(self) -> TrainingStage:
        """Get current training stage."""
        return self.resistance_state.get_stage()
    
    def check_conditioned_response(self, trigger: str) -> List[str]:
        """
        Check for conditioned responses to a trigger.
        Returns list of response messages.
        """
        behaviors = self.conditioned_behaviors
        willpower = getattr(self, 'willpower', 10)
        
        triggered = TrainingSystem.check_trigger(behaviors, trigger, willpower)
        
        responses = []
        for name, response in triggered:
            responses.append(f"{self.key} {response}")
        
        return responses


class TrainerMixin:
    """
    Mixin for characters that can train others.
    """
    
    @property
    def training_skill(self) -> int:
        """Get training skill level."""
        return self.attributes.get("training_skill", 1)
    
    @training_skill.setter
    def training_skill(self, value: int):
        """Set training skill."""
        self.attributes.add("training_skill", value)
    
    @property
    def active_session(self) -> Optional[TrainingSession]:
        """Get active training session."""
        data = self.attributes.get("active_training_session")
        if data:
            return TrainingSession(**data)
        return None
    
    @active_session.setter
    def active_session(self, session: Optional[TrainingSession]):
        """Set active session."""
        if session:
            self.attributes.add("active_training_session", session.to_dict())
        else:
            self.attributes.remove("active_training_session")


__all__ = [
    "TrainingStage",
    "ResistanceType",
    "ConditioningType",
    "ReinforcementType",
    "ResistanceState",
    "ConditionedBehavior",
    "PRESET_BEHAVIORS",
    "get_preset_behavior",
    "TrainingSession",
    "TrainingMethod",
    "TRAINING_METHODS",
    "get_training_method",
    "TrainingSystem",
    "TraineeMixin",
    "TrainerMixin",
]
