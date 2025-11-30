"""
Feral Pet Stats
===============

Tracking system for feral pet attributes:
- Loyalty, obedience, bond strength
- Mood states and energy
- Training progress
"""

from dataclasses import dataclass, field
from typing import Optional, Dict, List, Any
from enum import Enum
from datetime import datetime


# =============================================================================
# ENUMS
# =============================================================================

class PetMood(Enum):
    """Mood states for pets."""
    ECSTATIC = "ecstatic"      # Very happy, extra obedient
    HAPPY = "happy"            # Content, normal behavior
    CONTENT = "content"        # Neutral, baseline
    ANXIOUS = "anxious"        # Nervous, may disobey
    FEARFUL = "fearful"        # Scared, flight response
    AGGRESSIVE = "aggressive"  # Hostile, may attack
    DEPRESSED = "depressed"    # Withdrawn, low energy
    AROUSED = "aroused"        # In heat or stimulated
    EXHAUSTED = "exhausted"    # Too tired to do much


class BondLevel(Enum):
    """Bond strength between pet and owner."""
    NONE = "none"              # No bond (wild/untamed)
    WARY = "wary"              # Suspicious, newly tamed
    TOLERANT = "tolerant"      # Accepts handler
    FRIENDLY = "friendly"      # Likes handler
    BONDED = "bonded"          # Strong connection
    DEVOTED = "devoted"        # Deeply loyal
    SOULBOUND = "soulbound"    # Unbreakable bond


class TrainingLevel(Enum):
    """Overall training tier."""
    UNTRAINED = "untrained"
    BASIC = "basic"            # Knows sit, stay, come
    INTERMEDIATE = "intermediate"  # Knows complex tricks
    ADVANCED = "advanced"      # Highly trained
    EXPERT = "expert"          # Elite training
    MASTERFUL = "masterful"    # Perfectly trained


# =============================================================================
# PET STATS
# =============================================================================

@dataclass
class PetStats:
    """
    Core statistics for a feral pet.
    """
    # Ownership
    owner_dbref: str = ""
    owner_name: str = ""
    
    # Core stats (0-100 scale)
    loyalty: int = 50          # Overall loyalty to owner
    obedience: int = 50        # Likelihood to follow commands
    affection: int = 50        # How much they like their owner
    trust: int = 50            # Trust in owner (affects fear responses)
    
    # Bond
    bond_level: BondLevel = BondLevel.NONE
    bond_strength: int = 0     # 0-100, progress within bond level
    
    # Training
    training_level: TrainingLevel = TrainingLevel.UNTRAINED
    training_points: int = 0   # Progress to next level
    tricks_learned: List[str] = field(default_factory=list)
    tricks_mastered: List[str] = field(default_factory=list)
    
    # Current state
    mood: PetMood = PetMood.CONTENT
    energy: int = 100          # 0-100, depletes with activity
    hunger: int = 0            # 0-100, increases over time
    arousal: int = 0           # 0-100, sexual arousal
    
    # Needs satisfaction
    last_fed: Optional[datetime] = None
    last_petted: Optional[datetime] = None
    last_played: Optional[datetime] = None
    last_bred: Optional[datetime] = None
    
    # Discipline tracking
    times_rewarded: int = 0
    times_punished: int = 0
    reward_punishment_ratio: float = 1.0
    
    # Statistics
    commands_obeyed: int = 0
    commands_disobeyed: int = 0
    successful_breeds: int = 0
    offspring_count: int = 0
    
    def get_obedience_modifier(self) -> float:
        """Get modifier for obedience checks based on current state."""
        modifier = 1.0
        
        # Mood effects
        mood_mods = {
            PetMood.ECSTATIC: 1.3,
            PetMood.HAPPY: 1.15,
            PetMood.CONTENT: 1.0,
            PetMood.ANXIOUS: 0.8,
            PetMood.FEARFUL: 0.6,
            PetMood.AGGRESSIVE: 0.4,
            PetMood.DEPRESSED: 0.7,
            PetMood.AROUSED: 0.85,  # Distracted
            PetMood.EXHAUSTED: 0.5,
        }
        modifier *= mood_mods.get(self.mood, 1.0)
        
        # Energy effects
        if self.energy < 20:
            modifier *= 0.6
        elif self.energy < 50:
            modifier *= 0.85
        
        # Hunger effects
        if self.hunger > 80:
            modifier *= 0.7
        elif self.hunger > 50:
            modifier *= 0.9
        
        # Bond effects
        bond_mods = {
            BondLevel.NONE: 0.3,
            BondLevel.WARY: 0.5,
            BondLevel.TOLERANT: 0.7,
            BondLevel.FRIENDLY: 0.9,
            BondLevel.BONDED: 1.1,
            BondLevel.DEVOTED: 1.25,
            BondLevel.SOULBOUND: 1.5,
        }
        modifier *= bond_mods.get(self.bond_level, 1.0)
        
        return modifier
    
    def check_obedience(self, difficulty: int = 50, trick_name: str = "") -> bool:
        """
        Check if pet obeys a command.
        
        Args:
            difficulty: Base difficulty (0-100)
            trick_name: Name of trick being commanded
            
        Returns:
            True if pet obeys
        """
        import random
        
        # Base chance from obedience stat
        base_chance = self.obedience
        
        # Apply modifiers
        base_chance *= self.get_obedience_modifier()
        
        # Mastered tricks are easier
        if trick_name in self.tricks_mastered:
            base_chance += 30
        elif trick_name in self.tricks_learned:
            base_chance += 10
        
        # Roll
        roll = random.randint(1, 100)
        success = roll <= (base_chance - difficulty + 50)
        
        # Track stats
        if success:
            self.commands_obeyed += 1
        else:
            self.commands_disobeyed += 1
        
        return success
    
    def modify_stat(self, stat: str, amount: int, cap: bool = True):
        """Modify a stat by amount, optionally capping at 0-100."""
        current = getattr(self, stat, 0)
        new_value = current + amount
        
        if cap:
            new_value = max(0, min(100, new_value))
        
        setattr(self, stat, new_value)
    
    def apply_reward(self, strength: int = 10):
        """Apply positive reinforcement."""
        self.times_rewarded += 1
        self.modify_stat("loyalty", strength // 2)
        self.modify_stat("affection", strength)
        self.modify_stat("trust", strength // 2)
        self.modify_stat("obedience", strength // 3)
        
        # Mood improvement
        if self.mood in (PetMood.ANXIOUS, PetMood.FEARFUL, PetMood.DEPRESSED):
            self.mood = PetMood.CONTENT
        elif self.mood == PetMood.CONTENT:
            self.mood = PetMood.HAPPY
        elif self.mood == PetMood.HAPPY:
            self.mood = PetMood.ECSTATIC
        
        self._update_ratio()
    
    def apply_punishment(self, strength: int = 10):
        """Apply negative reinforcement."""
        self.times_punished += 1
        self.modify_stat("trust", -strength)
        self.modify_stat("affection", -strength // 2)
        
        # Can increase obedience through fear, but damages trust
        if self.trust > 30:
            self.modify_stat("obedience", strength // 4)
        else:
            self.modify_stat("obedience", -strength // 2)
        
        # Mood worsening
        if self.mood in (PetMood.ECSTATIC, PetMood.HAPPY):
            self.mood = PetMood.CONTENT
        elif self.mood == PetMood.CONTENT:
            self.mood = PetMood.ANXIOUS
        elif self.mood == PetMood.ANXIOUS:
            if self.trust < 30:
                self.mood = PetMood.AGGRESSIVE
            else:
                self.mood = PetMood.FEARFUL
        
        self._update_ratio()
    
    def _update_ratio(self):
        """Update reward/punishment ratio."""
        total = self.times_rewarded + self.times_punished
        if total > 0:
            self.reward_punishment_ratio = self.times_rewarded / total
    
    def feed(self):
        """Feed the pet."""
        self.hunger = max(0, self.hunger - 50)
        self.last_fed = datetime.now()
        self.modify_stat("affection", 5)
        
        if self.mood == PetMood.DEPRESSED:
            self.mood = PetMood.CONTENT
    
    def pet(self):
        """Pet/stroke the pet."""
        self.last_petted = datetime.now()
        self.modify_stat("affection", 10)
        self.modify_stat("trust", 5)
        
        if self.mood in (PetMood.ANXIOUS, PetMood.FEARFUL):
            self.mood = PetMood.CONTENT
    
    def play(self, duration: int = 10):
        """Play with the pet."""
        self.last_played = datetime.now()
        self.modify_stat("energy", -duration * 2)
        self.modify_stat("affection", duration)
        self.modify_stat("bond_strength", duration // 2)
        
        if self.mood != PetMood.EXHAUSTED:
            self.mood = PetMood.HAPPY
    
    def rest(self, duration: int = 10):
        """Let the pet rest."""
        self.modify_stat("energy", duration * 3)
        
        if self.energy > 50 and self.mood == PetMood.EXHAUSTED:
            self.mood = PetMood.CONTENT
    
    def update_bond_level(self):
        """Update bond level based on bond strength."""
        if self.bond_strength >= 100:
            # Advance bond level
            bond_order = list(BondLevel)
            current_index = bond_order.index(self.bond_level)
            
            if current_index < len(bond_order) - 1:
                self.bond_level = bond_order[current_index + 1]
                self.bond_strength = 0
        elif self.bond_strength < 0:
            # Regress bond level
            bond_order = list(BondLevel)
            current_index = bond_order.index(self.bond_level)
            
            if current_index > 0:
                self.bond_level = bond_order[current_index - 1]
                self.bond_strength = 50
    
    def update_training_level(self):
        """Update training level based on tricks learned."""
        trick_count = len(self.tricks_learned)
        mastery_count = len(self.tricks_mastered)
        
        if mastery_count >= 15:
            self.training_level = TrainingLevel.MASTERFUL
        elif mastery_count >= 10:
            self.training_level = TrainingLevel.EXPERT
        elif trick_count >= 10:
            self.training_level = TrainingLevel.ADVANCED
        elif trick_count >= 5:
            self.training_level = TrainingLevel.INTERMEDIATE
        elif trick_count >= 2:
            self.training_level = TrainingLevel.BASIC
        else:
            self.training_level = TrainingLevel.UNTRAINED
    
    def tick(self, minutes: int = 1):
        """Process time passing."""
        # Hunger increases
        self.modify_stat("hunger", minutes // 10)
        
        # Energy regenerates slowly when resting
        if self.mood not in (PetMood.AROUSED, PetMood.AGGRESSIVE):
            self.modify_stat("energy", minutes // 5)
        
        # Arousal decreases slowly
        if self.arousal > 0:
            self.modify_stat("arousal", -minutes // 2)
        
        # Mood normalization over time
        if self.mood == PetMood.ECSTATIC and minutes > 30:
            self.mood = PetMood.HAPPY
        elif self.mood == PetMood.HAPPY and minutes > 60:
            self.mood = PetMood.CONTENT
        
        # Bond decay if neglected
        if self.last_petted:
            hours_since = (datetime.now() - self.last_petted).total_seconds() / 3600
            if hours_since > 24:
                self.modify_stat("bond_strength", -1)
        
        self.update_bond_level()
    
    def get_status_display(self) -> str:
        """Get formatted status display."""
        lines = []
        
        # Header
        lines.append(f"=== Pet Stats ===")
        
        # Owner
        if self.owner_name:
            lines.append(f"Owner: {self.owner_name}")
        
        # Core stats
        lines.append(f"Loyalty: {self.loyalty}/100")
        lines.append(f"Obedience: {self.obedience}/100")
        lines.append(f"Affection: {self.affection}/100")
        lines.append(f"Trust: {self.trust}/100")
        
        # Bond
        lines.append(f"Bond: {self.bond_level.value} ({self.bond_strength}/100)")
        
        # Training
        lines.append(f"Training: {self.training_level.value}")
        lines.append(f"Tricks: {len(self.tricks_learned)} learned, {len(self.tricks_mastered)} mastered")
        
        # Current state
        lines.append(f"Mood: {self.mood.value}")
        lines.append(f"Energy: {self.energy}/100")
        lines.append(f"Hunger: {self.hunger}/100")
        
        if self.arousal > 0:
            lines.append(f"Arousal: {self.arousal}/100")
        
        return "\n".join(lines)
    
    def to_dict(self) -> dict:
        """Serialize to dictionary."""
        return {
            "owner_dbref": self.owner_dbref,
            "owner_name": self.owner_name,
            "loyalty": self.loyalty,
            "obedience": self.obedience,
            "affection": self.affection,
            "trust": self.trust,
            "bond_level": self.bond_level.value,
            "bond_strength": self.bond_strength,
            "training_level": self.training_level.value,
            "training_points": self.training_points,
            "tricks_learned": self.tricks_learned,
            "tricks_mastered": self.tricks_mastered,
            "mood": self.mood.value,
            "energy": self.energy,
            "hunger": self.hunger,
            "arousal": self.arousal,
            "last_fed": self.last_fed.isoformat() if self.last_fed else None,
            "last_petted": self.last_petted.isoformat() if self.last_petted else None,
            "last_played": self.last_played.isoformat() if self.last_played else None,
            "last_bred": self.last_bred.isoformat() if self.last_bred else None,
            "times_rewarded": self.times_rewarded,
            "times_punished": self.times_punished,
            "commands_obeyed": self.commands_obeyed,
            "commands_disobeyed": self.commands_disobeyed,
            "successful_breeds": self.successful_breeds,
            "offspring_count": self.offspring_count,
        }
    
    @classmethod
    def from_dict(cls, data: dict) -> "PetStats":
        """Deserialize from dictionary."""
        stats = cls()
        
        stats.owner_dbref = data.get("owner_dbref", "")
        stats.owner_name = data.get("owner_name", "")
        stats.loyalty = data.get("loyalty", 50)
        stats.obedience = data.get("obedience", 50)
        stats.affection = data.get("affection", 50)
        stats.trust = data.get("trust", 50)
        stats.bond_level = BondLevel(data.get("bond_level", "none"))
        stats.bond_strength = data.get("bond_strength", 0)
        stats.training_level = TrainingLevel(data.get("training_level", "untrained"))
        stats.training_points = data.get("training_points", 0)
        stats.tricks_learned = data.get("tricks_learned", [])
        stats.tricks_mastered = data.get("tricks_mastered", [])
        stats.mood = PetMood(data.get("mood", "content"))
        stats.energy = data.get("energy", 100)
        stats.hunger = data.get("hunger", 0)
        stats.arousal = data.get("arousal", 0)
        
        if data.get("last_fed"):
            stats.last_fed = datetime.fromisoformat(data["last_fed"])
        if data.get("last_petted"):
            stats.last_petted = datetime.fromisoformat(data["last_petted"])
        if data.get("last_played"):
            stats.last_played = datetime.fromisoformat(data["last_played"])
        if data.get("last_bred"):
            stats.last_bred = datetime.fromisoformat(data["last_bred"])
        
        stats.times_rewarded = data.get("times_rewarded", 0)
        stats.times_punished = data.get("times_punished", 0)
        stats.commands_obeyed = data.get("commands_obeyed", 0)
        stats.commands_disobeyed = data.get("commands_disobeyed", 0)
        stats.successful_breeds = data.get("successful_breeds", 0)
        stats.offspring_count = data.get("offspring_count", 0)
        
        stats._update_ratio()
        return stats


# =============================================================================
# PET STATS MIXIN
# =============================================================================

class PetStatsMixin:
    """
    Mixin for NPCs/characters to have pet stats.
    """
    
    @property
    def pet_stats(self) -> PetStats:
        """Get or create pet stats."""
        if not hasattr(self, '_pet_stats_cache'):
            data = self.attributes.get("pet_stats", {})
            if data:
                self._pet_stats_cache = PetStats.from_dict(data)
            else:
                self._pet_stats_cache = PetStats()
        return self._pet_stats_cache
    
    def save_pet_stats(self):
        """Save pet stats to attributes."""
        self.attributes.add("pet_stats", self.pet_stats.to_dict())
        if hasattr(self, '_pet_stats_cache'):
            del self._pet_stats_cache
    
    def set_owner(self, owner):
        """Set the pet's owner."""
        self.pet_stats.owner_dbref = owner.dbref
        self.pet_stats.owner_name = owner.key
        self.save_pet_stats()
    
    def clear_owner(self):
        """Remove owner."""
        self.pet_stats.owner_dbref = ""
        self.pet_stats.owner_name = ""
        self.pet_stats.bond_level = BondLevel.NONE
        self.pet_stats.bond_strength = 0
        self.save_pet_stats()
    
    def is_owned_by(self, character) -> bool:
        """Check if owned by specific character."""
        return self.pet_stats.owner_dbref == character.dbref
    
    def get_loyalty_desc(self) -> str:
        """Get description of loyalty level."""
        loyalty = self.pet_stats.loyalty
        
        if loyalty >= 90:
            return "fanatically loyal"
        elif loyalty >= 75:
            return "very loyal"
        elif loyalty >= 60:
            return "loyal"
        elif loyalty >= 40:
            return "somewhat loyal"
        elif loyalty >= 25:
            return "uncertain"
        elif loyalty >= 10:
            return "disloyal"
        else:
            return "hostile"
    
    def get_mood_desc(self) -> str:
        """Get description of current mood."""
        mood = self.pet_stats.mood
        
        descriptions = {
            PetMood.ECSTATIC: "tail wagging furiously, eyes bright with joy",
            PetMood.HAPPY: "relaxed and content, occasionally wagging",
            PetMood.CONTENT: "calm and attentive",
            PetMood.ANXIOUS: "ears back, pacing nervously",
            PetMood.FEARFUL: "cowering, tail tucked between legs",
            PetMood.AGGRESSIVE: "hackles raised, growling low",
            PetMood.DEPRESSED: "listless, head down",
            PetMood.AROUSED: "panting, clearly excited",
            PetMood.EXHAUSTED: "lying flat, barely moving",
        }
        
        return descriptions.get(mood, "")


__all__ = [
    "PetMood",
    "BondLevel",
    "TrainingLevel",
    "PetStats",
    "PetStatsMixin",
]
