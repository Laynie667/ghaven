"""
Pet Play System
===============

Humanoid pet play mechanics:
- Pet types (puppy, kitten, pony, cow, bunny, piggy)
- Headspace and mental states
- Pet behaviors and sounds
- Integration with species for bonuses
"""

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any, Set
from enum import Enum
from datetime import datetime
import random


# =============================================================================
# PET TYPES
# =============================================================================

class PetPlayType(Enum):
    """Types of pet play."""
    PUPPY = "puppy"
    KITTEN = "kitten"
    PONY = "pony"
    COW = "cow"
    BUNNY = "bunny"
    PIGGY = "piggy"
    FOX = "fox"
    WOLF = "wolf"


# =============================================================================
# PET TYPE DEFINITIONS
# =============================================================================

@dataclass
class PetTypeDefinition:
    """Definition of a pet play type."""
    key: str
    name: str
    
    # Personality traits
    traits: List[str] = field(default_factory=list)
    
    # Sounds they make
    sounds: List[str] = field(default_factory=list)
    
    # Movement/actions
    movements: List[str] = field(default_factory=list)
    
    # Default position
    default_position: str = "on all fours"
    
    # Species that get bonuses
    matching_species: List[str] = field(default_factory=list)
    
    # Special mechanics
    special_mechanic: str = ""
    
    # Speech patterns when in headspace
    speech_sounds: Dict[str, str] = field(default_factory=dict)
    
    # Behavioral modifiers
    behavior_mods: Dict[str, float] = field(default_factory=dict)


PET_TYPE_DEFINITIONS: Dict[str, PetTypeDefinition] = {
    "puppy": PetTypeDefinition(
        key="puppy",
        name="Puppy",
        traits=["eager", "playful", "loyal", "excitable", "affectionate"],
        sounds=["bark", "yip", "whine", "whimper", "howl", "growl", "pant"],
        movements=["wag", "pant", "lick", "nuzzle", "roll over", "fetch", "beg"],
        default_position="on all fours",
        matching_species=["wolf", "dog", "fox", "jackal", "hyena", "werewolf"],
        special_mechanic="tail_wag",
        speech_sounds={
            "yes": "woof!",
            "no": "whine",
            "happy": "yip yip!",
            "sad": "whimper",
            "excited": "bark bark bark!",
            "want": "whine",
        },
        behavior_mods={
            "obedience": 1.2,
            "energy": 1.3,
            "affection": 1.2,
        },
    ),
    "kitten": PetTypeDefinition(
        key="kitten",
        name="Kitten",
        traits=["aloof", "curious", "graceful", "independent", "playful"],
        sounds=["meow", "mew", "purr", "hiss", "chirp", "trill", "yowl"],
        movements=["stretch", "knead", "rub", "pounce", "groom", "curl up", "swat"],
        default_position="on all fours",
        matching_species=["cat", "lion", "tiger", "leopard", "panther", "lynx", "neko"],
        special_mechanic="purr",
        speech_sounds={
            "yes": "mrrp",
            "no": "hiss",
            "happy": "purrrr",
            "sad": "mew",
            "excited": "chirp!",
            "want": "meow?",
        },
        behavior_mods={
            "obedience": 0.8,  # Cats are stubborn
            "independence": 1.4,
            "grace": 1.3,
        },
    ),
    "pony": PetTypeDefinition(
        key="pony",
        name="Pony",
        traits=["obedient", "strong", "proud", "elegant", "competitive"],
        sounds=["neigh", "whinny", "snort", "nicker", "blow"],
        movements=["trot", "prance", "stamp", "toss head", "rear", "kneel"],
        default_position="standing",
        matching_species=["horse", "pony", "donkey", "zebra", "unicorn", "centaur"],
        special_mechanic="gait_control",
        speech_sounds={
            "yes": "nicker",
            "no": "snort",
            "happy": "whinny",
            "sad": "blow",
            "excited": "neigh!",
            "want": "nicker nicker",
        },
        behavior_mods={
            "obedience": 1.3,
            "endurance": 1.4,
            "pride": 1.2,
        },
    ),
    "cow": PetTypeDefinition(
        key="cow",
        name="Cow",
        traits=["docile", "gentle", "patient", "productive", "calm"],
        sounds=["moo", "low", "bellow", "huff"],
        movements=["graze", "chew", "sway", "nuzzle", "lick"],
        default_position="standing or on all fours",
        matching_species=["cow", "minotaur", "bull"],
        special_mechanic="lactation_boost",
        speech_sounds={
            "yes": "moo",
            "no": "huff",
            "happy": "moooo",
            "sad": "low",
            "excited": "moo!",
            "want": "moo?",
        },
        behavior_mods={
            "obedience": 1.1,
            "lactation": 1.5,  # Cow play boosts milk production
            "patience": 1.3,
        },
    ),
    "bunny": PetTypeDefinition(
        key="bunny",
        name="Bunny",
        traits=["timid", "quick", "fertile", "soft", "nervous"],
        sounds=["squeak", "thump", "purr", "whimper"],
        movements=["hop", "wiggle nose", "freeze", "thump", "binky", "groom"],
        default_position="crouched",
        matching_species=["rabbit", "hare", "bunny"],
        special_mechanic="breeding_boost",
        speech_sounds={
            "yes": "squeak",
            "no": "thump",
            "happy": "purr",
            "sad": "whimper",
            "excited": "binky!",
            "want": "squeak squeak",
        },
        behavior_mods={
            "fertility": 1.5,  # Bunny play boosts fertility
            "timidity": 1.3,
            "speed": 1.2,
        },
    ),
    "piggy": PetTypeDefinition(
        key="piggy",
        name="Piggy",
        traits=["greedy", "messy", "eager", "shameless", "gluttonous"],
        sounds=["oink", "squeal", "grunt", "snort", "snuffle"],
        movements=["root", "wallow", "snuffle", "roll", "gobble"],
        default_position="on all fours",
        matching_species=["pig", "boar"],
        special_mechanic="degradation",
        speech_sounds={
            "yes": "oink!",
            "no": "snort",
            "happy": "oink oink",
            "sad": "squeal",
            "excited": "squeeee!",
            "want": "oink oink oink",
        },
        behavior_mods={
            "shame_resistance": 1.5,  # Piggies don't feel shame
            "messiness": 1.4,
            "eagerness": 1.3,
        },
    ),
    "fox": PetTypeDefinition(
        key="fox",
        name="Fox",
        traits=["clever", "mischievous", "playful", "cunning", "flirty"],
        sounds=["yip", "bark", "chitter", "scream", "purr"],
        movements=["pounce", "play", "stalk", "trot", "curl up"],
        default_position="on all fours",
        matching_species=["fox", "kitsune"],
        special_mechanic="mischief",
        speech_sounds={
            "yes": "yip!",
            "no": "chitter",
            "happy": "yip yip!",
            "sad": "whine",
            "excited": "yipyipyip!",
            "want": "chitter chitter",
        },
        behavior_mods={
            "mischief": 1.4,
            "cleverness": 1.3,
            "playfulness": 1.2,
        },
    ),
    "wolf": PetTypeDefinition(
        key="wolf",
        name="Wolf",
        traits=["proud", "pack-minded", "fierce", "loyal", "dominant"],
        sounds=["howl", "growl", "bark", "whine", "snarl"],
        movements=["prowl", "stalk", "nuzzle", "pin", "mount"],
        default_position="on all fours",
        matching_species=["wolf", "werewolf", "dire wolf"],
        special_mechanic="pack_dynamics",
        speech_sounds={
            "yes": "bark",
            "no": "snarl",
            "happy": "howl!",
            "sad": "whine",
            "excited": "howwwl!",
            "want": "growl",
        },
        behavior_mods={
            "pack_loyalty": 1.4,
            "dominance": 1.2,
            "ferocity": 1.3,
        },
    ),
}


def get_pet_type_def(pet_type: str) -> Optional[PetTypeDefinition]:
    """Get pet type definition by key."""
    return PET_TYPE_DEFINITIONS.get(pet_type.lower())


# =============================================================================
# HEADSPACE
# =============================================================================

class HeadspaceDepth(Enum):
    """How deep in pet headspace."""
    NONE = "none"            # Not in headspace
    LIGHT = "light"          # Aware they're playing
    MODERATE = "moderate"    # Getting into it
    DEEP = "deep"            # Fully immersed
    SUBSPACE = "subspace"    # Lost in pet mind


@dataclass
class PetHeadspace:
    """
    Tracks a character's pet play headspace.
    """
    # Type of pet
    pet_type: str = ""
    
    # Pet name (if different from character name)
    pet_name: str = ""
    
    # Handler/owner
    handler_dbref: str = ""
    handler_name: str = ""
    
    # Depth of headspace
    depth: HeadspaceDepth = HeadspaceDepth.NONE
    depth_value: int = 0  # 0-100 for gradual changes
    
    # Duration tracking
    entered_at: Optional[datetime] = None
    total_time_minutes: int = 0
    
    # Modifiers
    speech_filter: bool = False   # Replace words with pet sounds
    movement_restrict: bool = False  # Must stay in position
    simplified_thought: bool = False  # Simpler responses
    
    # Conditioning (long-term)
    conditioning_level: int = 0  # 0-100, makes entering headspace easier
    times_entered: int = 0
    
    # Current state
    is_active: bool = False
    current_mood: str = "neutral"  # happy, excited, anxious, needy, etc.
    
    @property
    def pet_type_def(self) -> Optional[PetTypeDefinition]:
        """Get the pet type definition."""
        return get_pet_type_def(self.pet_type)
    
    def enter_headspace(self, pet_type: str, pet_name: str = "", handler=None):
        """Enter pet headspace."""
        self.pet_type = pet_type
        self.pet_name = pet_name
        self.is_active = True
        self.entered_at = datetime.now()
        self.depth = HeadspaceDepth.LIGHT
        self.depth_value = 20
        self.times_entered += 1
        
        if handler:
            self.handler_dbref = handler.dbref
            self.handler_name = handler.key
        
        # Apply modifiers based on depth
        self._update_modifiers()
    
    def exit_headspace(self):
        """Exit pet headspace."""
        if self.entered_at:
            duration = (datetime.now() - self.entered_at).total_seconds() / 60
            self.total_time_minutes += int(duration)
        
        self.is_active = False
        self.depth = HeadspaceDepth.NONE
        self.depth_value = 0
        self.speech_filter = False
        self.movement_restrict = False
        self.simplified_thought = False
        self.entered_at = None
    
    def deepen(self, amount: int = 10):
        """Deepen headspace."""
        if not self.is_active:
            return
        
        self.depth_value = min(100, self.depth_value + amount)
        self._update_depth_level()
        self._update_modifiers()
    
    def lighten(self, amount: int = 10):
        """Lighten headspace."""
        if not self.is_active:
            return
        
        self.depth_value = max(0, self.depth_value - amount)
        self._update_depth_level()
        self._update_modifiers()
        
        if self.depth_value <= 0:
            self.exit_headspace()
    
    def _update_depth_level(self):
        """Update depth enum based on value."""
        if self.depth_value >= 90:
            self.depth = HeadspaceDepth.SUBSPACE
        elif self.depth_value >= 70:
            self.depth = HeadspaceDepth.DEEP
        elif self.depth_value >= 40:
            self.depth = HeadspaceDepth.MODERATE
        elif self.depth_value > 0:
            self.depth = HeadspaceDepth.LIGHT
        else:
            self.depth = HeadspaceDepth.NONE
    
    def _update_modifiers(self):
        """Update behavior modifiers based on depth."""
        if self.depth == HeadspaceDepth.SUBSPACE:
            self.speech_filter = True
            self.movement_restrict = True
            self.simplified_thought = True
        elif self.depth == HeadspaceDepth.DEEP:
            self.speech_filter = True
            self.movement_restrict = True
            self.simplified_thought = False
        elif self.depth == HeadspaceDepth.MODERATE:
            self.speech_filter = True
            self.movement_restrict = False
            self.simplified_thought = False
        else:
            self.speech_filter = False
            self.movement_restrict = False
            self.simplified_thought = False
    
    def filter_speech(self, text: str) -> str:
        """Filter speech through pet sounds if in headspace."""
        if not self.speech_filter or not self.pet_type_def:
            return text
        
        # Deep headspace = mostly pet sounds
        if self.depth in (HeadspaceDepth.DEEP, HeadspaceDepth.SUBSPACE):
            sounds = self.pet_type_def.sounds
            if sounds:
                # Replace most words with sounds
                return random.choice(sounds).capitalize()
        
        # Moderate = occasional sounds
        sounds_map = self.pet_type_def.speech_sounds
        text_lower = text.lower()
        
        for word, sound in sounds_map.items():
            if word in text_lower:
                return sound.capitalize()
        
        return text
    
    def get_random_sound(self) -> str:
        """Get a random pet sound."""
        if self.pet_type_def and self.pet_type_def.sounds:
            return random.choice(self.pet_type_def.sounds)
        return ""
    
    def get_random_movement(self) -> str:
        """Get a random pet movement/action."""
        if self.pet_type_def and self.pet_type_def.movements:
            return random.choice(self.pet_type_def.movements)
        return ""
    
    def get_status_display(self) -> str:
        """Get formatted status display."""
        if not self.is_active:
            return "Not in pet headspace."
        
        lines = []
        
        type_def = self.pet_type_def
        type_name = type_def.name if type_def else self.pet_type.title()
        
        lines.append(f"=== Pet Mode: {type_name} ===")
        
        if self.pet_name:
            lines.append(f"Pet Name: {self.pet_name}")
        
        if self.handler_name:
            lines.append(f"Handler: {self.handler_name}")
        
        lines.append(f"Headspace: {self.depth.value} ({self.depth_value}%)")
        lines.append(f"Mood: {self.current_mood}")
        
        if self.speech_filter:
            lines.append("Speech: Filtered to pet sounds")
        if self.movement_restrict:
            lines.append("Movement: Restricted to pet positions")
        
        lines.append(f"Conditioning: {self.conditioning_level}%")
        
        return "\n".join(lines)
    
    def to_dict(self) -> dict:
        return {
            "pet_type": self.pet_type,
            "pet_name": self.pet_name,
            "handler_dbref": self.handler_dbref,
            "handler_name": self.handler_name,
            "depth": self.depth.value,
            "depth_value": self.depth_value,
            "entered_at": self.entered_at.isoformat() if self.entered_at else None,
            "total_time_minutes": self.total_time_minutes,
            "speech_filter": self.speech_filter,
            "movement_restrict": self.movement_restrict,
            "simplified_thought": self.simplified_thought,
            "conditioning_level": self.conditioning_level,
            "times_entered": self.times_entered,
            "is_active": self.is_active,
            "current_mood": self.current_mood,
        }
    
    @classmethod
    def from_dict(cls, data: dict) -> "PetHeadspace":
        hs = cls()
        
        hs.pet_type = data.get("pet_type", "")
        hs.pet_name = data.get("pet_name", "")
        hs.handler_dbref = data.get("handler_dbref", "")
        hs.handler_name = data.get("handler_name", "")
        hs.depth = HeadspaceDepth(data.get("depth", "none"))
        hs.depth_value = data.get("depth_value", 0)
        
        if data.get("entered_at"):
            hs.entered_at = datetime.fromisoformat(data["entered_at"])
        
        hs.total_time_minutes = data.get("total_time_minutes", 0)
        hs.speech_filter = data.get("speech_filter", False)
        hs.movement_restrict = data.get("movement_restrict", False)
        hs.simplified_thought = data.get("simplified_thought", False)
        hs.conditioning_level = data.get("conditioning_level", 0)
        hs.times_entered = data.get("times_entered", 0)
        hs.is_active = data.get("is_active", False)
        hs.current_mood = data.get("current_mood", "neutral")
        
        return hs


# =============================================================================
# PET PLAY MIXIN
# =============================================================================

class PetPlayMixin:
    """
    Mixin for characters that can engage in pet play.
    """
    
    @property
    def pet_headspace(self) -> PetHeadspace:
        """Get pet headspace data."""
        data = self.attributes.get("pet_headspace", {})
        if data:
            return PetHeadspace.from_dict(data)
        return PetHeadspace()
    
    def save_pet_headspace(self, headspace: PetHeadspace):
        """Save pet headspace data."""
        self.attributes.add("pet_headspace", headspace.to_dict())
    
    def is_in_pet_mode(self) -> bool:
        """Check if currently in pet headspace."""
        return self.pet_headspace.is_active
    
    def get_pet_type(self) -> Optional[str]:
        """Get current pet type if in headspace."""
        hs = self.pet_headspace
        return hs.pet_type if hs.is_active else None
    
    def enter_pet_mode(self, pet_type: str, pet_name: str = "", handler=None) -> str:
        """Enter pet play headspace."""
        hs = self.pet_headspace
        
        if hs.is_active:
            return f"Already in {hs.pet_type} mode. Exit first."
        
        type_def = get_pet_type_def(pet_type)
        if not type_def:
            return f"Unknown pet type: {pet_type}"
        
        hs.enter_headspace(pet_type, pet_name, handler)
        self.save_pet_headspace(hs)
        
        type_name = type_def.name
        name_str = f" '{pet_name}'" if pet_name else ""
        
        return f"You slip into {type_name} headspace{name_str}. {random.choice(type_def.sounds).capitalize()}!"
    
    def exit_pet_mode(self) -> str:
        """Exit pet play headspace."""
        hs = self.pet_headspace
        
        if not hs.is_active:
            return "Not in pet headspace."
        
        type_def = hs.pet_type_def
        type_name = type_def.name if type_def else hs.pet_type.title()
        
        hs.exit_headspace()
        self.save_pet_headspace(hs)
        
        return f"You slowly come out of {type_name} headspace, returning to yourself."
    
    def deepen_pet_mode(self, amount: int = 10) -> str:
        """Deepen pet headspace."""
        hs = self.pet_headspace
        
        if not hs.is_active:
            return "Not in pet headspace."
        
        old_depth = hs.depth
        hs.deepen(amount)
        self.save_pet_headspace(hs)
        
        if hs.depth != old_depth:
            return f"You sink deeper into headspace... ({hs.depth.value})"
        return f"Headspace deepens slightly ({hs.depth_value}%)"
    
    def make_pet_sound(self) -> str:
        """Make an appropriate pet sound."""
        hs = self.pet_headspace
        
        if not hs.is_active:
            return ""
        
        sound = hs.get_random_sound()
        return sound.capitalize() if sound else ""
    
    def get_species_pet_bonus(self) -> float:
        """Get bonus multiplier if species matches pet type."""
        hs = self.pet_headspace
        if not hs.is_active:
            return 1.0
        
        type_def = hs.pet_type_def
        if not type_def:
            return 1.0
        
        char_species = getattr(self, 'species', None)
        if char_species and char_species.lower() in type_def.matching_species:
            return 1.25  # 25% bonus for matching species
        
        return 1.0
    
    def get_pet_display_name(self) -> str:
        """Get display name (pet name if in headspace)."""
        hs = self.pet_headspace
        
        if hs.is_active and hs.pet_name:
            return hs.pet_name
        
        return self.key


# =============================================================================
# PET PLAY TRAINING
# =============================================================================

@dataclass
class PetPlayTraining:
    """Tracks pet play training for a humanoid pet."""
    
    # Owner/trainer
    trainer_dbref: str = ""
    trainer_name: str = ""
    
    # Training stats
    obedience: int = 50      # 0-100
    presentation: int = 50   # 0-100, how well they present
    endurance: int = 50      # 0-100, how long they can maintain
    grace: int = 50          # 0-100, elegance of movement
    
    # Tricks learned (for humanoid pet tricks)
    tricks_learned: List[str] = field(default_factory=list)
    
    # Conditioning
    conditioned_responses: Dict[str, str] = field(default_factory=dict)
    # e.g., {"snap": "kneel", "whistle": "come", "good pet": "wag"}
    
    # Training history
    sessions_completed: int = 0
    rewards_received: int = 0
    punishments_received: int = 0
    
    def add_conditioned_response(self, trigger: str, response: str):
        """Add a conditioned response."""
        self.conditioned_responses[trigger.lower()] = response
    
    def check_trigger(self, text: str) -> Optional[str]:
        """Check if text contains a trained trigger."""
        text_lower = text.lower()
        for trigger, response in self.conditioned_responses.items():
            if trigger in text_lower:
                return response
        return None
    
    def to_dict(self) -> dict:
        return {
            "trainer_dbref": self.trainer_dbref,
            "trainer_name": self.trainer_name,
            "obedience": self.obedience,
            "presentation": self.presentation,
            "endurance": self.endurance,
            "grace": self.grace,
            "tricks_learned": self.tricks_learned,
            "conditioned_responses": self.conditioned_responses,
            "sessions_completed": self.sessions_completed,
            "rewards_received": self.rewards_received,
            "punishments_received": self.punishments_received,
        }
    
    @classmethod
    def from_dict(cls, data: dict) -> "PetPlayTraining":
        return cls(**{k: v for k, v in data.items() if k in cls.__dataclass_fields__})


# =============================================================================
# HELPER FUNCTIONS
# =============================================================================

def list_pet_types() -> List[str]:
    """Get list of all pet play types."""
    return list(PET_TYPE_DEFINITIONS.keys())


def get_pet_type_description(pet_type: str) -> str:
    """Get description of a pet type."""
    type_def = get_pet_type_def(pet_type)
    if not type_def:
        return f"Unknown pet type: {pet_type}"
    
    traits = ", ".join(type_def.traits[:3])
    sounds = ", ".join(type_def.sounds[:3])
    
    return f"{type_def.name}: {traits}. Sounds: {sounds}."


def get_matching_pet_type(species: str) -> Optional[str]:
    """Get the pet type that matches a species."""
    species_lower = species.lower()
    
    for type_key, type_def in PET_TYPE_DEFINITIONS.items():
        if species_lower in type_def.matching_species:
            return type_key
    
    return None


__all__ = [
    "PetPlayType",
    "PetTypeDefinition",
    "PET_TYPE_DEFINITIONS",
    "get_pet_type_def",
    "HeadspaceDepth",
    "PetHeadspace",
    "PetPlayMixin",
    "PetPlayTraining",
    "list_pet_types",
    "get_pet_type_description",
    "get_matching_pet_type",
]
