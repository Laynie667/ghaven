"""
Futanari Bull System
====================

Bull breeding stock including:
- Bull stats and tracking
- Breeding capabilities
- Stud services
- Bull NPCs
"""

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any, Tuple
from enum import Enum
from datetime import datetime, timedelta
import random


# =============================================================================
# ENUMS
# =============================================================================

class BullGrade(Enum):
    """Quality grades for bulls."""
    UNTESTED = "untested"         # New, unproven
    STANDARD = "standard"         # Basic breeding stock
    PROVEN = "proven"             # Successful breedings
    QUALITY = "quality"           # Above average results
    PREMIUM = "premium"           # High success rate
    CHAMPION = "champion"         # Show-quality, exceptional
    LEGENDARY = "legendary"       # Famous bloodline


class BullType(Enum):
    """Types of bulls."""
    NATURAL = "natural"           # Standard male anatomy
    FUTANARI = "futanari"         # Has both sets
    HYPER = "hyper"               # Oversized equipment
    MAGICAL = "magical"           # Magic-enhanced
    FERAL = "feral"               # Animal-type
    DEMON = "demon"               # Demonic traits
    DIVINE = "divine"             # Blessed/angelic


class RutState(Enum):
    """Rut (breeding drive) states."""
    CALM = "calm"                 # Normal state
    INTERESTED = "interested"     # Noticing heat
    AROUSED = "aroused"           # Ready to breed
    RUTTING = "rutting"           # Peak drive
    FRENZY = "frenzy"             # Uncontrollable
    EXHAUSTED = "exhausted"       # Post-breeding
    RECOVERING = "recovering"     # Building back


class BreedingStyle(Enum):
    """How the bull breeds."""
    GENTLE = "gentle"             # Careful, slow
    STANDARD = "standard"         # Normal pace
    ROUGH = "rough"               # Aggressive
    DOMINANT = "dominant"         # Controlling
    BRUTAL = "brutal"             # No mercy
    MARATHON = "marathon"         # Multiple rounds
    KNOTTING = "knotting"         # Ties with partner


# =============================================================================
# BULL STATS
# =============================================================================

@dataclass
class BullPhysical:
    """Physical attributes for bulls."""
    
    # Size
    height_cm: int = 180
    weight_kg: int = 90
    build: str = "muscular"       # lean, average, muscular, massive
    
    # Equipment - primary (cock)
    cock_length_cm: int = 18
    cock_girth_cm: int = 14
    cock_type: str = "human"      # human, equine, canine, demon, tentacle
    has_knot: bool = False
    knot_size_cm: int = 0
    
    # Equipment - secondary (for futanari)
    has_pussy: bool = False
    has_breasts: bool = False
    breast_size: str = "flat"
    can_lactate: bool = False
    can_get_pregnant: bool = False
    
    # Balls
    ball_size: str = "average"    # small, average, large, massive, hyper
    cum_volume_ml: int = 15       # Per ejaculation
    
    # Stamina
    refractory_minutes: int = 30
    max_rounds_per_day: int = 3
    current_rounds_today: int = 0
    
    @property
    def is_futanari(self) -> bool:
        """Check if futanari."""
        return self.has_pussy or self.has_breasts
    
    @property
    def equipment_description(self) -> str:
        """Get equipment description."""
        parts = []
        
        # Cock
        size_desc = "average"
        if self.cock_length_cm > 25:
            size_desc = "massive"
        elif self.cock_length_cm > 20:
            size_desc = "large"
        elif self.cock_length_cm < 12:
            size_desc = "modest"
        
        cock_desc = f"a {size_desc} {self.cock_type} cock ({self.cock_length_cm}cm)"
        if self.has_knot:
            cock_desc += f" with a {self.knot_size_cm}cm knot"
        parts.append(cock_desc)
        
        # Balls
        parts.append(f"{self.ball_size} balls")
        
        # Futanari parts
        if self.has_pussy:
            parts.append("a pussy")
        if self.has_breasts and self.breast_size != "flat":
            parts.append(f"{self.breast_size} breasts")
            if self.can_lactate:
                parts.append("(lactating)")
        
        return ", ".join(parts)
    
    def to_dict(self) -> dict:
        return {
            "height_cm": self.height_cm,
            "weight_kg": self.weight_kg,
            "build": self.build,
            "cock_length_cm": self.cock_length_cm,
            "cock_girth_cm": self.cock_girth_cm,
            "cock_type": self.cock_type,
            "has_knot": self.has_knot,
            "knot_size_cm": self.knot_size_cm,
            "has_pussy": self.has_pussy,
            "has_breasts": self.has_breasts,
            "breast_size": self.breast_size,
            "can_lactate": self.can_lactate,
            "can_get_pregnant": self.can_get_pregnant,
            "ball_size": self.ball_size,
            "cum_volume_ml": self.cum_volume_ml,
            "refractory_minutes": self.refractory_minutes,
            "max_rounds_per_day": self.max_rounds_per_day,
            "current_rounds_today": self.current_rounds_today,
        }
    
    @classmethod
    def from_dict(cls, data: dict) -> "BullPhysical":
        phys = cls()
        for key, value in data.items():
            if hasattr(phys, key):
                setattr(phys, key, value)
        return phys


@dataclass
class BullBreedingStats:
    """Breeding performance stats."""
    
    # Fertility
    virility: int = 70            # 0-100, chance to impregnate
    sperm_potency: int = 70       # 0-100, affects conception
    
    # Performance
    stamina: int = 70             # 0-100
    technique: int = 50           # 0-100, affects pleasure given
    aggression: int = 50          # 0-100, breeding intensity
    
    # Style
    preferred_style: BreedingStyle = BreedingStyle.STANDARD
    
    # Current state
    rut_state: RutState = RutState.CALM
    arousal: int = 0              # 0-100
    
    # History
    total_breedings: int = 0
    successful_impregnations: int = 0
    offspring_sired: int = 0
    
    # Records
    breedings_today: int = 0
    last_breeding: Optional[datetime] = None
    hours_since_breeding: float = 24.0
    
    @property
    def success_rate(self) -> float:
        """Calculate impregnation success rate."""
        if self.total_breedings == 0:
            return 0.0
        return (self.successful_impregnations / self.total_breedings) * 100
    
    @property
    def is_ready(self) -> bool:
        """Check if ready to breed."""
        return (
            self.rut_state not in [RutState.EXHAUSTED, RutState.RECOVERING] and
            self.hours_since_breeding >= 0.5  # 30 minutes minimum
        )
    
    def detect_heat(self, heat_intensity: int) -> str:
        """React to nearby heat."""
        if self.rut_state == RutState.EXHAUSTED:
            return "Too exhausted to respond."
        
        # Arousal increases based on heat intensity
        arousal_gain = heat_intensity // 2
        self.arousal = min(100, self.arousal + arousal_gain)
        
        # Update rut state
        if self.arousal >= 90:
            self.rut_state = RutState.FRENZY
            return "Enters a breeding frenzy!"
        elif self.arousal >= 70:
            self.rut_state = RutState.RUTTING
            return "Goes into full rut!"
        elif self.arousal >= 50:
            self.rut_state = RutState.AROUSED
            return "Becomes visibly aroused."
        elif self.arousal >= 30:
            self.rut_state = RutState.INTERESTED
            return "Perks up, nostrils flaring."
        
        return ""
    
    def calculate_conception_chance(self, target_fertility: int) -> float:
        """Calculate chance of conception."""
        # Base chance from virility and target fertility
        chance = (self.virility + target_fertility) / 200
        
        # Potency modifier
        chance *= (self.sperm_potency / 100)
        
        # Rut state bonus
        rut_bonus = {
            RutState.CALM: 0.8,
            RutState.INTERESTED: 0.9,
            RutState.AROUSED: 1.0,
            RutState.RUTTING: 1.2,
            RutState.FRENZY: 1.3,
        }
        chance *= rut_bonus.get(self.rut_state, 1.0)
        
        return min(0.95, chance)
    
    def perform_breeding(self, target_name: str) -> Tuple[str, int]:
        """
        Perform breeding act.
        Returns (description, pleasure_given).
        """
        self.total_breedings += 1
        self.breedings_today += 1
        self.last_breeding = datetime.now()
        self.hours_since_breeding = 0
        
        # Calculate pleasure based on technique and style
        pleasure = self.technique
        
        style_msgs = {
            BreedingStyle.GENTLE: f"carefully mounts {target_name}, taking it slow",
            BreedingStyle.STANDARD: f"mounts {target_name} with steady, rhythmic thrusts",
            BreedingStyle.ROUGH: f"roughly takes {target_name}, pounding hard",
            BreedingStyle.DOMINANT: f"pins {target_name} down and claims them completely",
            BreedingStyle.BRUTAL: f"savagely breeds {target_name} without mercy",
            BreedingStyle.MARATHON: f"breeds {target_name} through multiple rounds",
            BreedingStyle.KNOTTING: f"knots inside {target_name}, tying them together",
        }
        
        base_msg = style_msgs.get(self.preferred_style, f"breeds {target_name}")
        
        # Intensity from aggression
        if self.aggression > 80:
            pleasure += 20
            base_msg += " with brutal intensity"
        elif self.aggression > 60:
            pleasure += 10
            base_msg += " aggressively"
        
        # Rut bonus
        if self.rut_state == RutState.FRENZY:
            pleasure += 30
            base_msg += " in a mindless frenzy"
        elif self.rut_state == RutState.RUTTING:
            pleasure += 20
            base_msg += " driven by overwhelming need"
        
        # Exhaustion check
        if self.breedings_today >= 3:
            self.rut_state = RutState.EXHAUSTED
        elif self.breedings_today >= 2:
            self.arousal = max(0, self.arousal - 40)
        
        return base_msg, min(100, pleasure)
    
    def rest(self, hours: float) -> str:
        """Rest and recover."""
        self.hours_since_breeding += hours
        
        if self.rut_state == RutState.EXHAUSTED:
            if self.hours_since_breeding >= 8:
                self.rut_state = RutState.RECOVERING
                return "Beginning to recover."
        elif self.rut_state == RutState.RECOVERING:
            if self.hours_since_breeding >= 16:
                self.rut_state = RutState.CALM
                self.breedings_today = 0
                return "Fully recovered."
        
        # Arousal decay
        self.arousal = max(0, self.arousal - int(hours * 5))
        
        return ""
    
    def to_dict(self) -> dict:
        return {
            "virility": self.virility,
            "sperm_potency": self.sperm_potency,
            "stamina": self.stamina,
            "technique": self.technique,
            "aggression": self.aggression,
            "preferred_style": self.preferred_style.value,
            "rut_state": self.rut_state.value,
            "arousal": self.arousal,
            "total_breedings": self.total_breedings,
            "successful_impregnations": self.successful_impregnations,
            "offspring_sired": self.offspring_sired,
            "breedings_today": self.breedings_today,
            "last_breeding": self.last_breeding.isoformat() if self.last_breeding else None,
            "hours_since_breeding": self.hours_since_breeding,
        }
    
    @classmethod
    def from_dict(cls, data: dict) -> "BullBreedingStats":
        stats = cls()
        for key, value in data.items():
            if key == "preferred_style":
                stats.preferred_style = BreedingStyle(value)
            elif key == "rut_state":
                stats.rut_state = RutState(value)
            elif key == "last_breeding" and value:
                stats.last_breeding = datetime.fromisoformat(value)
            elif hasattr(stats, key):
                setattr(stats, key, value)
        return stats


@dataclass 
class BullStats:
    """Complete bull statistics."""
    
    # Identity
    bull_id: str = ""
    name: str = ""
    given_name: str = ""          # Stud name
    registration: str = ""         # Stud registry number
    
    # Type and grade
    bull_type: BullType = BullType.NATURAL
    grade: BullGrade = BullGrade.UNTESTED
    
    # Sub-stats
    physical: BullPhysical = field(default_factory=BullPhysical)
    breeding: BullBreedingStats = field(default_factory=BullBreedingStats)
    
    # Temperament
    temperament: str = "calm"      # calm, excitable, aggressive, gentle
    trainability: int = 50         # 0-100
    
    # Owner
    owner_dbref: str = ""
    owner_name: str = ""
    
    # Location
    assigned_stall: str = ""
    assigned_farm: str = ""
    
    # Value
    stud_fee: int = 100           # Cost per breeding
    current_value: int = 1000
    
    # Records
    days_active: int = 0
    
    def calculate_value(self) -> int:
        """Calculate current market value."""
        base = 1000
        
        # Grade multiplier
        grade_mult = {
            BullGrade.UNTESTED: 0.5,
            BullGrade.STANDARD: 1.0,
            BullGrade.PROVEN: 1.5,
            BullGrade.QUALITY: 2.0,
            BullGrade.PREMIUM: 3.0,
            BullGrade.CHAMPION: 5.0,
            BullGrade.LEGENDARY: 10.0,
        }
        base *= grade_mult.get(self.grade, 1.0)
        
        # Type bonus
        type_bonus = {
            BullType.NATURAL: 0,
            BullType.FUTANARI: 500,
            BullType.HYPER: 300,
            BullType.MAGICAL: 800,
            BullType.DEMON: 600,
            BullType.DIVINE: 1000,
        }
        base += type_bonus.get(self.bull_type, 0)
        
        # Performance bonus
        base += self.breeding.success_rate * 10
        base += self.breeding.offspring_sired * 50
        
        # Equipment bonus
        if self.physical.cock_length_cm > 20:
            base += (self.physical.cock_length_cm - 20) * 20
        
        # Futanari bonus
        if self.physical.is_futanari:
            base += 500
            if self.physical.can_lactate:
                base += 200
        
        self.current_value = int(base)
        return self.current_value
    
    def calculate_stud_fee(self) -> int:
        """Calculate appropriate stud fee."""
        base = 50
        
        # Grade multiplier
        grade_mult = {
            BullGrade.UNTESTED: 0.5,
            BullGrade.STANDARD: 1.0,
            BullGrade.PROVEN: 1.5,
            BullGrade.QUALITY: 2.0,
            BullGrade.PREMIUM: 3.0,
            BullGrade.CHAMPION: 5.0,
            BullGrade.LEGENDARY: 10.0,
        }
        base *= grade_mult.get(self.grade, 1.0)
        
        # Success rate bonus
        base += self.breeding.success_rate
        
        self.stud_fee = int(base)
        return self.stud_fee
    
    def update_grade(self) -> str:
        """Update grade based on performance."""
        old_grade = self.grade
        
        breedings = self.breeding.total_breedings
        success = self.breeding.success_rate
        offspring = self.breeding.offspring_sired
        
        if offspring >= 50 and success >= 80:
            self.grade = BullGrade.LEGENDARY
        elif offspring >= 25 and success >= 70:
            self.grade = BullGrade.CHAMPION
        elif offspring >= 15 and success >= 60:
            self.grade = BullGrade.PREMIUM
        elif offspring >= 8 and success >= 50:
            self.grade = BullGrade.QUALITY
        elif breedings >= 5:
            self.grade = BullGrade.PROVEN
        elif breedings >= 1:
            self.grade = BullGrade.STANDARD
        
        if old_grade != self.grade:
            return f"Grade improved: {old_grade.value} → {self.grade.value}!"
        return ""
    
    def get_status_display(self) -> str:
        """Get formatted status display."""
        lines = [f"=== Bull Status: {self.name} ==="]
        if self.given_name:
            lines.append(f"Stud Name: {self.given_name}")
        if self.registration:
            lines.append(f"Registry: {self.registration}")
        
        lines.append(f"Type: {self.bull_type.value}")
        lines.append(f"Grade: {self.grade.value}")
        
        lines.append(f"\n--- Physical ---")
        lines.append(f"Build: {self.physical.build}")
        lines.append(f"Equipment: {self.physical.equipment_description}")
        lines.append(f"Cum Volume: {self.physical.cum_volume_ml}ml")
        
        lines.append(f"\n--- Breeding ---")
        lines.append(f"Virility: {self.breeding.virility}/100")
        lines.append(f"Technique: {self.breeding.technique}/100")
        lines.append(f"Style: {self.breeding.preferred_style.value}")
        lines.append(f"State: {self.breeding.rut_state.value}")
        lines.append(f"Arousal: {self.breeding.arousal}/100")
        
        lines.append(f"\n--- Records ---")
        lines.append(f"Total Breedings: {self.breeding.total_breedings}")
        lines.append(f"Impregnations: {self.breeding.successful_impregnations}")
        lines.append(f"Offspring Sired: {self.breeding.offspring_sired}")
        lines.append(f"Success Rate: {self.breeding.success_rate:.1f}%")
        
        self.calculate_value()
        self.calculate_stud_fee()
        lines.append(f"\nStud Fee: {self.stud_fee} gold")
        lines.append(f"Value: {self.current_value} gold")
        
        return "\n".join(lines)
    
    def to_dict(self) -> dict:
        return {
            "bull_id": self.bull_id,
            "name": self.name,
            "given_name": self.given_name,
            "registration": self.registration,
            "bull_type": self.bull_type.value,
            "grade": self.grade.value,
            "physical": self.physical.to_dict(),
            "breeding": self.breeding.to_dict(),
            "temperament": self.temperament,
            "trainability": self.trainability,
            "owner_dbref": self.owner_dbref,
            "owner_name": self.owner_name,
            "assigned_stall": self.assigned_stall,
            "assigned_farm": self.assigned_farm,
            "stud_fee": self.stud_fee,
            "current_value": self.current_value,
            "days_active": self.days_active,
        }
    
    @classmethod
    def from_dict(cls, data: dict) -> "BullStats":
        stats = cls()
        for key, value in data.items():
            if key == "bull_type":
                stats.bull_type = BullType(value)
            elif key == "grade":
                stats.grade = BullGrade(value)
            elif key == "physical":
                stats.physical = BullPhysical.from_dict(value)
            elif key == "breeding":
                stats.breeding = BullBreedingStats.from_dict(value)
            elif hasattr(stats, key):
                setattr(stats, key, value)
        return stats


# =============================================================================
# BULL MIXIN
# =============================================================================

class BullMixin:
    """
    Mixin for characters that can be bulls.
    Add to your Character typeclass.
    """
    
    @property
    def bull_stats(self) -> BullStats:
        """Get bull stats."""
        data = self.db.bull_stats
        if data:
            return BullStats.from_dict(data)
        return BullStats(name=self.key)
    
    @bull_stats.setter
    def bull_stats(self, stats: BullStats) -> None:
        """Set bull stats."""
        self.db.bull_stats = stats.to_dict()
    
    def save_bull_stats(self, stats: BullStats) -> None:
        """Save bull stats."""
        self.db.bull_stats = stats.to_dict()
    
    @property
    def is_bull(self) -> bool:
        """Check if registered as bull."""
        return bool(self.db.bull_stats)
    
    @property
    def is_futanari_bull(self) -> bool:
        """Check if futanari."""
        if not self.is_bull:
            return False
        return self.bull_stats.physical.is_futanari
    
    def initialize_bull(
        self,
        owner,
        given_name: str = "",
        bull_type: BullType = BullType.NATURAL,
        is_futanari: bool = False,
    ) -> str:
        """Initialize as a bull."""
        import random
        
        physical = BullPhysical(
            cock_length_cm=random.randint(15, 25),
            cock_girth_cm=random.randint(12, 18),
            cum_volume_ml=random.randint(10, 30),
        )
        
        if is_futanari or bull_type == BullType.FUTANARI:
            physical.has_pussy = True
            physical.has_breasts = True
            physical.breast_size = random.choice(["small", "average", "large"])
            physical.can_lactate = random.random() < 0.3
            bull_type = BullType.FUTANARI
        
        stats = BullStats(
            bull_id=f"BUL-{datetime.now().strftime('%Y%m%d%H%M%S')}-{random.randint(1000, 9999)}",
            name=self.key,
            given_name=given_name or f"Stud-{random.randint(100, 999)}",
            registration=f"STD-{random.randint(10000, 99999)}",
            bull_type=bull_type,
            physical=physical,
            owner_dbref=owner.dbref if owner else "",
            owner_name=owner.key if owner else "",
        )
        
        self.save_bull_stats(stats)
        
        futa_str = " (futanari)" if physical.is_futanari else ""
        return f"Registered as {bull_type.value} bull{futa_str}: {stats.given_name}"


# =============================================================================
# FUTANARI BULL PRESETS
# =============================================================================

def create_futanari_bull(
    name: str = "Unnamed",
    breast_size: str = "large",
    cock_length: int = 22,
    has_knot: bool = False,
    can_lactate: bool = True,
    aggression: int = 60,
) -> BullStats:
    """Create a futanari bull with custom stats."""
    import random
    
    physical = BullPhysical(
        build="muscular",
        cock_length_cm=cock_length,
        cock_girth_cm=int(cock_length * 0.7),
        cock_type="human",
        has_knot=has_knot,
        knot_size_cm=int(cock_length * 0.4) if has_knot else 0,
        has_pussy=True,
        has_breasts=True,
        breast_size=breast_size,
        can_lactate=can_lactate,
        can_get_pregnant=True,
        ball_size="large",
        cum_volume_ml=random.randint(20, 50),
    )
    
    breeding = BullBreedingStats(
        virility=random.randint(60, 90),
        sperm_potency=random.randint(60, 90),
        stamina=random.randint(60, 90),
        technique=random.randint(50, 80),
        aggression=aggression,
    )
    
    return BullStats(
        bull_id=f"BUL-{datetime.now().strftime('%Y%m%d%H%M%S')}-{random.randint(1000, 9999)}",
        name=name,
        given_name=name,
        registration=f"FUTA-{random.randint(10000, 99999)}",
        bull_type=BullType.FUTANARI,
        physical=physical,
        breeding=breeding,
    )


# Preset futanari bulls
PRESET_BULLS = {
    "gentle_breeder": create_futanari_bull(
        name="Gentle Breeder",
        breast_size="average",
        cock_length=18,
        aggression=30,
    ),
    "dominant_stud": create_futanari_bull(
        name="Dominant Stud",
        breast_size="large",
        cock_length=24,
        aggression=80,
    ),
    "knotting_beast": create_futanari_bull(
        name="Knotting Beast",
        breast_size="huge",
        cock_length=26,
        has_knot=True,
        aggression=70,
    ),
    "milky_mother": create_futanari_bull(
        name="Milky Mother",
        breast_size="massive",
        cock_length=20,
        can_lactate=True,
        aggression=40,
    ),
}


__all__ = [
    "BullGrade",
    "BullType",
    "RutState",
    "BreedingStyle",
    "BullPhysical",
    "BullBreedingStats",
    "BullStats",
    "BullMixin",
    "create_futanari_bull",
    "PRESET_BULLS",
]
