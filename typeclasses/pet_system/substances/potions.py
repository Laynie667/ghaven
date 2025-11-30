"""
Potions & Substances System
===========================

Potions, drugs, and consumable substances:
- Effect types and durations
- Aphrodisiacs and stimulants
- Fertility and breeding enhancers
- Transformation potions
"""

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any, Tuple, Callable
from enum import Enum
from datetime import datetime, timedelta
import random


# =============================================================================
# ENUMS
# =============================================================================

class SubstanceType(Enum):
    """Types of substances."""
    POTION = "potion"           # Drinkable
    PILL = "pill"               # Swallowable
    INJECTION = "injection"     # Injected
    APPLIED = "applied"         # Applied to skin
    INHALED = "inhaled"         # Breathed in
    SUPPOSITORY = "suppository" # Inserted


class EffectCategory(Enum):
    """Categories of effects."""
    AROUSAL = "arousal"         # Sexual arousal
    FERTILITY = "fertility"     # Breeding effects
    PHYSICAL = "physical"       # Strength, stamina
    MENTAL = "mental"           # Willpower, obedience
    TRANSFORMATION = "transformation"  # Body changes
    LACTATION = "lactation"     # Milk production
    HEAT = "heat"               # Heat/rut induction
    SENSITIVITY = "sensitivity" # Heightened senses
    STAMINA = "stamina"         # Sexual stamina
    HEALING = "healing"         # Recovery


class EffectIntensity(Enum):
    """Intensity of effects."""
    MILD = "mild"
    MODERATE = "moderate"
    STRONG = "strong"
    EXTREME = "extreme"
    OVERWHELMING = "overwhelming"


class AddictionLevel(Enum):
    """Levels of addiction."""
    NONE = "none"
    LOW = "low"
    MODERATE = "moderate"
    HIGH = "high"
    SEVERE = "severe"


# =============================================================================
# EFFECT
# =============================================================================

@dataclass
class SubstanceEffect:
    """An effect from a substance."""
    effect_id: str
    name: str
    category: EffectCategory
    
    # Intensity and duration
    intensity: EffectIntensity = EffectIntensity.MODERATE
    base_duration_minutes: int = 60
    
    # Stat modifications
    stat_changes: Dict[str, int] = field(default_factory=dict)
    # e.g., {"arousal": 50, "fertility": 20}
    
    # Special flags
    prevents_orgasm: bool = False
    forces_heat: bool = False
    forces_lactation: bool = False
    increases_sensitivity: int = 0
    transformation_target: str = ""  # Species for transformation
    
    # Description
    onset_message: str = ""
    ongoing_message: str = ""
    fade_message: str = ""
    
    def get_duration_multiplier(self) -> float:
        """Get duration multiplier from intensity."""
        multipliers = {
            EffectIntensity.MILD: 0.5,
            EffectIntensity.MODERATE: 1.0,
            EffectIntensity.STRONG: 1.5,
            EffectIntensity.EXTREME: 2.0,
            EffectIntensity.OVERWHELMING: 3.0,
        }
        return multipliers.get(self.intensity, 1.0)
    
    def get_actual_duration(self) -> int:
        """Get actual duration in minutes."""
        return int(self.base_duration_minutes * self.get_duration_multiplier())
    
    def to_dict(self) -> dict:
        return {
            "effect_id": self.effect_id,
            "name": self.name,
            "category": self.category.value,
            "intensity": self.intensity.value,
            "base_duration_minutes": self.base_duration_minutes,
            "stat_changes": self.stat_changes,
            "prevents_orgasm": self.prevents_orgasm,
            "forces_heat": self.forces_heat,
            "forces_lactation": self.forces_lactation,
            "increases_sensitivity": self.increases_sensitivity,
            "transformation_target": self.transformation_target,
            "onset_message": self.onset_message,
            "ongoing_message": self.ongoing_message,
            "fade_message": self.fade_message,
        }
    
    @classmethod
    def from_dict(cls, data: dict) -> "SubstanceEffect":
        effect = cls(
            effect_id=data["effect_id"],
            name=data["name"],
            category=EffectCategory(data["category"]),
        )
        effect.intensity = EffectIntensity(data.get("intensity", "moderate"))
        effect.base_duration_minutes = data.get("base_duration_minutes", 60)
        effect.stat_changes = data.get("stat_changes", {})
        effect.prevents_orgasm = data.get("prevents_orgasm", False)
        effect.forces_heat = data.get("forces_heat", False)
        effect.forces_lactation = data.get("forces_lactation", False)
        effect.increases_sensitivity = data.get("increases_sensitivity", 0)
        effect.transformation_target = data.get("transformation_target", "")
        effect.onset_message = data.get("onset_message", "")
        effect.ongoing_message = data.get("ongoing_message", "")
        effect.fade_message = data.get("fade_message", "")
        return effect


# =============================================================================
# ACTIVE EFFECT
# =============================================================================

@dataclass
class ActiveEffect:
    """A currently active effect on a character."""
    effect: SubstanceEffect
    started_at: datetime
    expires_at: datetime
    source_name: str = ""       # What substance caused it
    stacks: int = 1             # Number of stacks
    
    @property
    def remaining_minutes(self) -> int:
        """Get remaining duration."""
        delta = self.expires_at - datetime.now()
        return max(0, int(delta.total_seconds() / 60))
    
    @property
    def is_expired(self) -> bool:
        """Check if effect has expired."""
        return datetime.now() >= self.expires_at
    
    def extend(self, minutes: int) -> None:
        """Extend the effect duration."""
        self.expires_at += timedelta(minutes=minutes)
    
    def add_stack(self) -> None:
        """Add a stack (intensify effect)."""
        self.stacks += 1
        # Extend duration slightly with each stack
        self.extend(15)
    
    def get_stat_change(self, stat: str) -> int:
        """Get stat change with stacks applied."""
        base = self.effect.stat_changes.get(stat, 0)
        return int(base * (1 + (self.stacks - 1) * 0.5))
    
    def to_dict(self) -> dict:
        return {
            "effect": self.effect.to_dict(),
            "started_at": self.started_at.isoformat(),
            "expires_at": self.expires_at.isoformat(),
            "source_name": self.source_name,
            "stacks": self.stacks,
        }
    
    @classmethod
    def from_dict(cls, data: dict) -> "ActiveEffect":
        return cls(
            effect=SubstanceEffect.from_dict(data["effect"]),
            started_at=datetime.fromisoformat(data["started_at"]),
            expires_at=datetime.fromisoformat(data["expires_at"]),
            source_name=data.get("source_name", ""),
            stacks=data.get("stacks", 1),
        )


# =============================================================================
# SUBSTANCE
# =============================================================================

@dataclass
class Substance:
    """A potion or drug."""
    key: str
    name: str
    substance_type: SubstanceType = SubstanceType.POTION
    
    # Effects
    effects: List[SubstanceEffect] = field(default_factory=list)
    
    # Properties
    addiction_risk: AddictionLevel = AddictionLevel.NONE
    overdose_threshold: int = 3  # How many before overdose
    
    # Appearance
    color: str = "clear"
    taste: str = "bitter"
    smell: str = "pungent"
    
    # Value
    base_value: int = 50
    rarity: str = "common"
    
    # Description
    description: str = ""
    consume_message: str = "You consume the {name}."
    
    def get_consume_message(self) -> str:
        """Get consumption message."""
        return self.consume_message.format(name=self.name)
    
    def to_dict(self) -> dict:
        return {
            "key": self.key,
            "name": self.name,
            "substance_type": self.substance_type.value,
            "effects": [e.to_dict() for e in self.effects],
            "addiction_risk": self.addiction_risk.value,
            "overdose_threshold": self.overdose_threshold,
            "color": self.color,
            "taste": self.taste,
            "smell": self.smell,
            "base_value": self.base_value,
            "rarity": self.rarity,
            "description": self.description,
            "consume_message": self.consume_message,
        }
    
    @classmethod
    def from_dict(cls, data: dict) -> "Substance":
        substance = cls(
            key=data["key"],
            name=data["name"],
        )
        substance.substance_type = SubstanceType(data.get("substance_type", "potion"))
        substance.effects = [SubstanceEffect.from_dict(e) for e in data.get("effects", [])]
        substance.addiction_risk = AddictionLevel(data.get("addiction_risk", "none"))
        substance.overdose_threshold = data.get("overdose_threshold", 3)
        substance.color = data.get("color", "clear")
        substance.taste = data.get("taste", "bitter")
        substance.smell = data.get("smell", "pungent")
        substance.base_value = data.get("base_value", 50)
        substance.rarity = data.get("rarity", "common")
        substance.description = data.get("description", "")
        substance.consume_message = data.get("consume_message", "You consume the {name}.")
        return substance


# =============================================================================
# PREDEFINED EFFECTS
# =============================================================================

# Arousal effects
EFFECT_AROUSAL_MILD = SubstanceEffect(
    effect_id="arousal_mild",
    name="Mild Arousal",
    category=EffectCategory.AROUSAL,
    intensity=EffectIntensity.MILD,
    base_duration_minutes=30,
    stat_changes={"arousal": 20},
    onset_message="A warm flush spreads through your body.",
    ongoing_message="You feel pleasantly aroused.",
    fade_message="The arousal fades to normal levels.",
)

EFFECT_AROUSAL_STRONG = SubstanceEffect(
    effect_id="arousal_strong",
    name="Intense Arousal",
    category=EffectCategory.AROUSAL,
    intensity=EffectIntensity.STRONG,
    base_duration_minutes=60,
    stat_changes={"arousal": 60},
    increases_sensitivity=30,
    onset_message="Intense heat floods through you, your body aching with need.",
    ongoing_message="Every sensation is magnified, your arousal almost unbearable.",
    fade_message="The overwhelming arousal slowly subsides.",
)

EFFECT_AROUSAL_OVERWHELMING = SubstanceEffect(
    effect_id="arousal_overwhelming",
    name="Overwhelming Lust",
    category=EffectCategory.AROUSAL,
    intensity=EffectIntensity.OVERWHELMING,
    base_duration_minutes=120,
    stat_changes={"arousal": 100, "willpower": -30},
    increases_sensitivity=50,
    onset_message="Your mind goes blank with pure, overwhelming NEED.",
    ongoing_message="You can think of nothing but release.",
    fade_message="Rational thought slowly returns as the lust fades.",
)

# Fertility effects
EFFECT_FERTILITY_BOOST = SubstanceEffect(
    effect_id="fertility_boost",
    name="Fertility Enhancement",
    category=EffectCategory.FERTILITY,
    intensity=EffectIntensity.MODERATE,
    base_duration_minutes=360,  # 6 hours
    stat_changes={"fertility": 50},
    onset_message="Your body tingles with fertile energy.",
    ongoing_message="You feel exceptionally fertile.",
    fade_message="Your fertility returns to normal.",
)

EFFECT_GUARANTEED_CONCEPTION = SubstanceEffect(
    effect_id="guaranteed_conception",
    name="Guaranteed Conception",
    category=EffectCategory.FERTILITY,
    intensity=EffectIntensity.EXTREME,
    base_duration_minutes=60,
    stat_changes={"fertility": 200},  # Over 100 = guaranteed
    onset_message="Powerful breeding magic courses through you.",
    ongoing_message="Your body is primed for conception.",
    fade_message="The conception magic fades.",
)

# Heat effects
EFFECT_INDUCED_HEAT = SubstanceEffect(
    effect_id="induced_heat",
    name="Induced Heat",
    category=EffectCategory.HEAT,
    intensity=EffectIntensity.STRONG,
    base_duration_minutes=480,  # 8 hours
    stat_changes={"arousal": 50, "fertility": 30},
    forces_heat=True,
    onset_message="Your body burns as artificial heat takes hold.",
    ongoing_message="You're in heat, desperate for breeding.",
    fade_message="The induced heat finally passes.",
)

# Lactation effects
EFFECT_LACTATION_START = SubstanceEffect(
    effect_id="lactation_start",
    name="Induced Lactation",
    category=EffectCategory.LACTATION,
    intensity=EffectIntensity.MODERATE,
    base_duration_minutes=1440,  # 24 hours
    forces_lactation=True,
    onset_message="Your breasts swell and begin producing milk.",
    ongoing_message="Your breasts feel full and heavy with milk.",
    fade_message="Your milk production slows.",
)

# Mental effects
EFFECT_OBEDIENCE = SubstanceEffect(
    effect_id="obedience",
    name="Compliance",
    category=EffectCategory.MENTAL,
    intensity=EffectIntensity.MODERATE,
    base_duration_minutes=120,
    stat_changes={"obedience": 30, "willpower": -20},
    onset_message="Your mind feels... agreeable.",
    ongoing_message="It's so much easier to just obey.",
    fade_message="Your mind clears.",
)

EFFECT_SUBMISSION = SubstanceEffect(
    effect_id="submission",
    name="Submissive Haze",
    category=EffectCategory.MENTAL,
    intensity=EffectIntensity.STRONG,
    base_duration_minutes=180,
    stat_changes={"obedience": 50, "willpower": -40, "submission": 40},
    onset_message="All resistance drains from your mind.",
    ongoing_message="You feel utterly submissive and pliant.",
    fade_message="Your willpower slowly returns.",
)

# Stamina effects
EFFECT_STAMINA_BOOST = SubstanceEffect(
    effect_id="stamina_boost",
    name="Sexual Stamina",
    category=EffectCategory.STAMINA,
    intensity=EffectIntensity.MODERATE,
    base_duration_minutes=120,
    stat_changes={"stamina": 50},
    prevents_orgasm=True,
    onset_message="You feel like you could go all night.",
    ongoing_message="Your endurance seems limitless.",
    fade_message="Normal stamina returns.",
)

EFFECT_DENIAL = SubstanceEffect(
    effect_id="denial",
    name="Orgasm Denial",
    category=EffectCategory.STAMINA,
    intensity=EffectIntensity.STRONG,
    base_duration_minutes=240,
    prevents_orgasm=True,
    onset_message="Release becomes impossible.",
    ongoing_message="No matter how aroused, you cannot climax.",
    fade_message="The ability to orgasm returns.",
)

# Sensitivity effects
EFFECT_HEIGHTENED_SENSES = SubstanceEffect(
    effect_id="heightened_senses",
    name="Heightened Sensitivity",
    category=EffectCategory.SENSITIVITY,
    intensity=EffectIntensity.MODERATE,
    base_duration_minutes=60,
    increases_sensitivity=40,
    onset_message="Every nerve ending comes alive.",
    ongoing_message="The slightest touch sends shivers through you.",
    fade_message="Your senses return to normal.",
)


# =============================================================================
# PREDEFINED POTIONS
# =============================================================================

POTION_APHRODISIAC_MILD = Substance(
    key="aphrodisiac_mild",
    name="Mild Aphrodisiac",
    substance_type=SubstanceType.POTION,
    effects=[EFFECT_AROUSAL_MILD],
    color="pink",
    taste="sweet",
    smell="floral",
    base_value=25,
    rarity="common",
    description="A light potion that induces mild arousal.",
)

POTION_APHRODISIAC_STRONG = Substance(
    key="aphrodisiac_strong",
    name="Potent Aphrodisiac",
    substance_type=SubstanceType.POTION,
    effects=[EFFECT_AROUSAL_STRONG, EFFECT_HEIGHTENED_SENSES],
    addiction_risk=AddictionLevel.LOW,
    color="deep pink",
    taste="intensely sweet",
    smell="intoxicating",
    base_value=100,
    rarity="uncommon",
    description="A powerful aphrodisiac that creates intense arousal.",
)

POTION_LUST_BOMB = Substance(
    key="lust_bomb",
    name="Lust Bomb",
    substance_type=SubstanceType.POTION,
    effects=[EFFECT_AROUSAL_OVERWHELMING],
    addiction_risk=AddictionLevel.MODERATE,
    overdose_threshold=2,
    color="glowing pink",
    taste="overwhelmingly sweet",
    smell="maddening",
    base_value=500,
    rarity="rare",
    description="An extremely potent lust potion. Use with caution.",
)

POTION_FERTILITY = Substance(
    key="fertility_potion",
    name="Fertility Potion",
    substance_type=SubstanceType.POTION,
    effects=[EFFECT_FERTILITY_BOOST],
    color="pale green",
    taste="earthy",
    smell="fresh",
    base_value=150,
    rarity="uncommon",
    description="Significantly increases fertility for several hours.",
)

POTION_BREEDING = Substance(
    key="breeding_potion",
    name="Breeding Draught",
    substance_type=SubstanceType.POTION,
    effects=[EFFECT_GUARANTEED_CONCEPTION, EFFECT_AROUSAL_STRONG],
    addiction_risk=AddictionLevel.LOW,
    color="deep green",
    taste="rich",
    smell="musky",
    base_value=500,
    rarity="rare",
    description="Guarantees conception if breeding occurs within the hour.",
)

POTION_HEAT = Substance(
    key="heat_inducer",
    name="Heat Inducer",
    substance_type=SubstanceType.POTION,
    effects=[EFFECT_INDUCED_HEAT],
    addiction_risk=AddictionLevel.MODERATE,
    color="red-orange",
    taste="spicy",
    smell="musky",
    base_value=200,
    rarity="uncommon",
    description="Forces the drinker into heat for 8 hours.",
)

POTION_LACTATION = Substance(
    key="lactation_potion",
    name="Milk Maiden's Draught",
    substance_type=SubstanceType.POTION,
    effects=[EFFECT_LACTATION_START],
    color="white",
    taste="creamy",
    smell="sweet milk",
    base_value=100,
    rarity="uncommon",
    description="Induces lactation for 24 hours.",
)

POTION_OBEDIENCE = Substance(
    key="obedience_potion",
    name="Compliance Elixir",
    substance_type=SubstanceType.POTION,
    effects=[EFFECT_OBEDIENCE],
    addiction_risk=AddictionLevel.MODERATE,
    color="pale purple",
    taste="numbing",
    smell="subtle",
    base_value=200,
    rarity="uncommon",
    description="Makes the drinker more compliant and obedient.",
)

POTION_SUBMISSION = Substance(
    key="submission_potion",
    name="Slave's Surrender",
    substance_type=SubstanceType.POTION,
    effects=[EFFECT_SUBMISSION],
    addiction_risk=AddictionLevel.HIGH,
    overdose_threshold=2,
    color="deep purple",
    taste="bitter",
    smell="oppressive",
    base_value=400,
    rarity="rare",
    description="Strips away willpower and induces deep submission.",
)

POTION_STAMINA = Substance(
    key="stamina_potion",
    name="Stallion's Vigor",
    substance_type=SubstanceType.POTION,
    effects=[EFFECT_STAMINA_BOOST, EFFECT_AROUSAL_MILD],
    color="amber",
    taste="energizing",
    smell="sharp",
    base_value=75,
    rarity="common",
    description="Greatly enhances sexual stamina.",
)

POTION_DENIAL = Substance(
    key="denial_potion",
    name="Edge Walker's Curse",
    substance_type=SubstanceType.POTION,
    effects=[EFFECT_DENIAL, EFFECT_AROUSAL_STRONG],
    color="blue-purple",
    taste="frustrating",
    smell="teasing",
    base_value=150,
    rarity="uncommon",
    description="Prevents orgasm while maintaining arousal.",
)

POTION_SENSITIVITY = Substance(
    key="sensitivity_potion",
    name="Nerve Awakener",
    substance_type=SubstanceType.POTION,
    effects=[EFFECT_HEIGHTENED_SENSES],
    color="electric blue",
    taste="tingling",
    smell="sharp",
    base_value=100,
    rarity="uncommon",
    description="Heightens all physical sensations.",
)


# =============================================================================
# SUBSTANCE REGISTRY
# =============================================================================

ALL_SUBSTANCES: Dict[str, Substance] = {
    "aphrodisiac_mild": POTION_APHRODISIAC_MILD,
    "aphrodisiac_strong": POTION_APHRODISIAC_STRONG,
    "lust_bomb": POTION_LUST_BOMB,
    "fertility_potion": POTION_FERTILITY,
    "breeding_potion": POTION_BREEDING,
    "heat_inducer": POTION_HEAT,
    "lactation_potion": POTION_LACTATION,
    "obedience_potion": POTION_OBEDIENCE,
    "submission_potion": POTION_SUBMISSION,
    "stamina_potion": POTION_STAMINA,
    "denial_potion": POTION_DENIAL,
    "sensitivity_potion": POTION_SENSITIVITY,
}


def get_substance(key: str) -> Optional[Substance]:
    """Get a substance by key."""
    template = ALL_SUBSTANCES.get(key)
    if template:
        return Substance.from_dict(template.to_dict())
    return None


def get_substances_by_category(category: EffectCategory) -> List[Substance]:
    """Get all substances with effects in a category."""
    result = []
    for substance in ALL_SUBSTANCES.values():
        for effect in substance.effects:
            if effect.category == category:
                result.append(substance)
                break
    return result


# =============================================================================
# SUBSTANCE SYSTEM
# =============================================================================

class SubstanceSystem:
    """
    Manages substance consumption and effects.
    """
    
    @staticmethod
    def consume(
        character,
        substance: Substance,
    ) -> Tuple[bool, str, List[ActiveEffect]]:
        """
        Have a character consume a substance.
        Returns (success, message, active_effects).
        """
        if not hasattr(character, 'active_effects'):
            return False, f"{character.key} cannot be affected by substances.", []
        
        messages = [substance.get_consume_message()]
        new_effects = []
        
        # Check overdose
        recent_doses = getattr(character, 'recent_doses', {})
        substance_doses = recent_doses.get(substance.key, 0)
        
        if substance_doses >= substance.overdose_threshold:
            # Overdose!
            messages.append("The overdose has severe consequences!")
            # Apply negative effects
            return True, " ".join(messages), []
        
        # Track dose
        recent_doses[substance.key] = substance_doses + 1
        character.recent_doses = recent_doses
        
        # Apply effects
        current_effects = character.active_effects
        
        for effect in substance.effects:
            # Check for stacking
            existing = None
            for active in current_effects:
                if active.effect.effect_id == effect.effect_id:
                    existing = active
                    break
            
            if existing:
                # Stack the effect
                existing.add_stack()
                messages.append(f"The {effect.name} effect intensifies!")
            else:
                # Create new active effect
                duration = effect.get_actual_duration()
                active = ActiveEffect(
                    effect=effect,
                    started_at=datetime.now(),
                    expires_at=datetime.now() + timedelta(minutes=duration),
                    source_name=substance.name,
                )
                current_effects.append(active)
                new_effects.append(active)
                messages.append(effect.onset_message)
        
        character.active_effects = current_effects
        
        # Check addiction
        if substance.addiction_risk != AddictionLevel.NONE:
            if random.randint(1, 100) <= substance.addiction_risk.value == "high" and 30 or 10:
                messages.append("You feel a craving for more...")
        
        return True, " ".join(messages), new_effects
    
    @staticmethod
    def apply_force(
        target,
        substance: Substance,
        forcer = None,
    ) -> Tuple[bool, str]:
        """Force a substance on a target."""
        force_messages = {
            SubstanceType.POTION: "forces {target} to drink the {substance}",
            SubstanceType.PILL: "forces a {substance} down {target}'s throat",
            SubstanceType.INJECTION: "injects {target} with {substance}",
            SubstanceType.APPLIED: "rubs {substance} onto {target}",
            SubstanceType.INHALED: "forces {target} to breathe in the {substance}",
            SubstanceType.SUPPOSITORY: "inserts the {substance} into {target}",
        }
        
        forcer_name = forcer.key if forcer else "Someone"
        msg_template = force_messages.get(substance.substance_type, "administers {substance} to {target}")
        action_msg = f"{forcer_name} {msg_template.format(target=target.key, substance=substance.name)}."
        
        success, effect_msg, effects = SubstanceSystem.consume(target, substance)
        
        return success, f"{action_msg} {effect_msg}"
    
    @staticmethod
    def process_effects(character) -> List[str]:
        """
        Process active effects, removing expired ones.
        Returns messages about expiring effects.
        """
        if not hasattr(character, 'active_effects'):
            return []
        
        messages = []
        remaining = []
        
        for active in character.active_effects:
            if active.is_expired:
                messages.append(active.effect.fade_message)
            else:
                remaining.append(active)
        
        character.active_effects = remaining
        return messages
    
    @staticmethod
    def get_stat_modifier(character, stat: str) -> int:
        """Get total stat modifier from active effects."""
        if not hasattr(character, 'active_effects'):
            return 0
        
        total = 0
        for active in character.active_effects:
            total += active.get_stat_change(stat)
        
        return total
    
    @staticmethod
    def has_effect(character, effect_id: str) -> bool:
        """Check if character has an active effect."""
        if not hasattr(character, 'active_effects'):
            return False
        
        for active in character.active_effects:
            if active.effect.effect_id == effect_id:
                return True
        
        return False
    
    @staticmethod
    def can_orgasm(character) -> bool:
        """Check if orgasm is prevented by effects."""
        if not hasattr(character, 'active_effects'):
            return True
        
        for active in character.active_effects:
            if active.effect.prevents_orgasm:
                return False
        
        return True
    
    @staticmethod
    def is_in_heat(character) -> bool:
        """Check if in drug-induced heat."""
        if not hasattr(character, 'active_effects'):
            return False
        
        for active in character.active_effects:
            if active.effect.forces_heat:
                return True
        
        return False


# =============================================================================
# SUBSTANCE MIXIN
# =============================================================================

class SubstanceAffectedMixin:
    """
    Mixin for characters that can be affected by substances.
    """
    
    @property
    def active_effects(self) -> List[ActiveEffect]:
        """Get active substance effects."""
        data = self.attributes.get("active_effects", [])
        return [ActiveEffect.from_dict(d) for d in data]
    
    @active_effects.setter
    def active_effects(self, effects: List[ActiveEffect]):
        """Set active effects."""
        self.attributes.add("active_effects", [e.to_dict() for e in effects])
    
    @property
    def recent_doses(self) -> Dict[str, int]:
        """Track recent doses for overdose."""
        return self.attributes.get("recent_doses", {})
    
    @recent_doses.setter
    def recent_doses(self, doses: Dict[str, int]):
        """Set recent doses."""
        self.attributes.add("recent_doses", doses)
    
    def consume_substance(self, substance: Substance) -> Tuple[bool, str]:
        """Consume a substance."""
        success, message, effects = SubstanceSystem.consume(self, substance)
        return success, message
    
    def get_effect_modifier(self, stat: str) -> int:
        """Get modifier to a stat from active effects."""
        return SubstanceSystem.get_stat_modifier(self, stat)
    
    def has_active_effect(self, effect_id: str) -> bool:
        """Check for an active effect."""
        return SubstanceSystem.has_effect(self, effect_id)
    
    def can_orgasm(self) -> bool:
        """Check if orgasm is possible."""
        return SubstanceSystem.can_orgasm(self)
    
    def is_drugged(self) -> bool:
        """Check if any substance effects are active."""
        return len(self.active_effects) > 0
    
    def get_active_effects_display(self) -> str:
        """Get display of active effects."""
        effects = self.active_effects
        if not effects:
            return "No active substance effects."
        
        lines = ["Active Effects:"]
        for active in effects:
            remaining = active.remaining_minutes
            stacks = f" x{active.stacks}" if active.stacks > 1 else ""
            lines.append(f"  {active.effect.name}{stacks} ({remaining}m remaining)")
        
        return "\n".join(lines)


__all__ = [
    "SubstanceType",
    "EffectCategory",
    "EffectIntensity",
    "AddictionLevel",
    "SubstanceEffect",
    "ActiveEffect",
    "Substance",
    "ALL_SUBSTANCES",
    "get_substance",
    "get_substances_by_category",
    "SubstanceSystem",
    "SubstanceAffectedMixin",
]
