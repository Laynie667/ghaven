"""
Hucow Farm System
=================

Comprehensive hucow management including:
- Hucow tracking and stats
- Lactation management
- Milking systems
- Herd organization
- Production quotas
"""

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any, Tuple
from enum import Enum
from datetime import datetime, timedelta
import random


# =============================================================================
# ENUMS
# =============================================================================

class HucowGrade(Enum):
    """Quality grades for hucows."""
    UNTRAINED = "untrained"       # Fresh capture, no training
    HEIFER = "heifer"             # In training, not yet producing
    STANDARD = "standard"         # Basic production
    QUALITY = "quality"           # Above average
    PREMIUM = "premium"           # High production
    PRIZE = "prize"               # Show-quality, exceptional
    BREEDER = "breeder"           # Proven breeding stock


class LactationStage(Enum):
    """Stages of lactation."""
    DRY = "dry"                   # Not producing
    INDUCING = "inducing"         # Lactation being induced
    COLOSTRUM = "colostrum"       # First milk, thick and rich
    TRANSITIONAL = "transitional" # Building to full production
    MATURE = "mature"             # Full production
    DECLINING = "declining"       # Reducing output
    WEANING = "weaning"           # Being dried off


class MilkType(Enum):
    """Types of milk produced."""
    STANDARD = "standard"
    CREAM_RICH = "cream_rich"     # High fat content
    PROTEIN_RICH = "protein_rich" # High protein
    SWEET = "sweet"               # Naturally sweeter
    COLOSTRUM = "colostrum"       # Antibody-rich first milk
    DRUGGED = "drugged"           # Infused with substances
    APHRODISIAC = "aphrodisiac"   # Has arousing properties
    MAGICAL = "magical"           # Magic-infused


class HucowBehavior(Enum):
    """Behavioral states."""
    DOCILE = "docile"             # Calm, compliant
    CONTENT = "content"           # Happy, well-adjusted
    RESTLESS = "restless"         # Needs attention
    NEEDY = "needy"               # Wants milking/breeding
    RESISTANT = "resistant"       # Fighting training
    HEAT = "heat"                 # In breeding cycle
    NURSING = "nursing"           # Feeding offspring
    EXHAUSTED = "exhausted"       # Overworked


class StallType(Enum):
    """Types of stalls."""
    STANDARD = "standard"         # Basic stall
    MILKING = "milking"           # Equipped for milking
    BREEDING = "breeding"         # For breeding sessions
    ISOLATION = "isolation"       # Problem hucows
    LUXURY = "luxury"             # Prize hucows
    MEDICAL = "medical"           # Treatment/recovery
    PUNISHMENT = "punishment"     # Discipline


# =============================================================================
# HUCOW STATS
# =============================================================================

@dataclass
class LactationStats:
    """Lactation-specific statistics."""
    
    # Current state
    stage: LactationStage = LactationStage.DRY
    milk_type: MilkType = MilkType.STANDARD
    
    # Production capacity
    max_capacity_ml: int = 500        # Max udder capacity
    current_fill_ml: int = 0          # Current milk stored
    production_rate_ml_hour: int = 20 # ML produced per hour
    
    # Quality metrics
    fat_content: float = 3.5          # Percentage
    protein_content: float = 3.2      # Percentage
    sweetness: int = 50               # 0-100
    
    # History
    days_lactating: int = 0
    total_produced_liters: float = 0.0
    times_milked: int = 0
    
    # Timing
    last_milked: Optional[datetime] = None
    hours_since_milking: float = 0.0
    
    # Modifiers
    production_bonus: float = 1.0     # Multiplier
    quality_bonus: float = 1.0        # Multiplier
    
    @property
    def is_full(self) -> bool:
        """Check if udders are full."""
        return self.current_fill_ml >= self.max_capacity_ml * 0.9
    
    @property
    def is_engorged(self) -> bool:
        """Check if painfully overfull."""
        return self.current_fill_ml >= self.max_capacity_ml
    
    @property
    def fill_percentage(self) -> float:
        """Get fill percentage."""
        if self.max_capacity_ml == 0:
            return 0.0
        return (self.current_fill_ml / self.max_capacity_ml) * 100
    
    @property
    def needs_milking(self) -> bool:
        """Check if needs milking."""
        return self.fill_percentage >= 70 or self.hours_since_milking >= 8
    
    def produce_milk(self, hours: float = 1.0) -> int:
        """
        Produce milk over time.
        Returns amount produced.
        """
        if self.stage == LactationStage.DRY:
            return 0
        
        # Calculate production
        rate = self.production_rate_ml_hour * self.production_bonus
        
        # Stage modifiers
        stage_mods = {
            LactationStage.INDUCING: 0.1,
            LactationStage.COLOSTRUM: 0.3,
            LactationStage.TRANSITIONAL: 0.6,
            LactationStage.MATURE: 1.0,
            LactationStage.DECLINING: 0.7,
            LactationStage.WEANING: 0.3,
        }
        rate *= stage_mods.get(self.stage, 1.0)
        
        produced = int(rate * hours)
        
        # Add to storage, cap at max
        old_fill = self.current_fill_ml
        self.current_fill_ml = min(
            self.max_capacity_ml,
            self.current_fill_ml + produced
        )
        
        actual_produced = self.current_fill_ml - old_fill
        self.hours_since_milking += hours
        
        return actual_produced
    
    def milk(self) -> Tuple[int, str]:
        """
        Milk the hucow.
        Returns (amount_ml, message).
        """
        if self.stage == LactationStage.DRY:
            return 0, "No milk to extract - udders are dry."
        
        amount = self.current_fill_ml
        self.current_fill_ml = 0
        self.last_milked = datetime.now()
        self.hours_since_milking = 0.0
        self.times_milked += 1
        self.total_produced_liters += amount / 1000
        
        if amount > 400:
            msg = f"Heavy milking yields {amount}ml of {self.milk_type.value} milk!"
        elif amount > 200:
            msg = f"Good milking yields {amount}ml of milk."
        else:
            msg = f"Light milking produces {amount}ml."
        
        return amount, msg
    
    def induce_lactation(self) -> str:
        """Begin lactation induction."""
        if self.stage != LactationStage.DRY:
            return "Already lactating."
        
        self.stage = LactationStage.INDUCING
        self.days_lactating = 0
        return "Lactation induction begun. Regular stimulation required."
    
    def advance_stage(self) -> str:
        """Advance to next lactation stage."""
        progressions = {
            LactationStage.INDUCING: LactationStage.COLOSTRUM,
            LactationStage.COLOSTRUM: LactationStage.TRANSITIONAL,
            LactationStage.TRANSITIONAL: LactationStage.MATURE,
            LactationStage.MATURE: LactationStage.MATURE,  # Stays
            LactationStage.DECLINING: LactationStage.WEANING,
            LactationStage.WEANING: LactationStage.DRY,
        }
        
        old_stage = self.stage
        self.stage = progressions.get(self.stage, self.stage)
        
        if old_stage != self.stage:
            return f"Lactation advanced from {old_stage.value} to {self.stage.value}."
        return "Lactation stage unchanged."
    
    def to_dict(self) -> dict:
        return {
            "stage": self.stage.value,
            "milk_type": self.milk_type.value,
            "max_capacity_ml": self.max_capacity_ml,
            "current_fill_ml": self.current_fill_ml,
            "production_rate_ml_hour": self.production_rate_ml_hour,
            "fat_content": self.fat_content,
            "protein_content": self.protein_content,
            "sweetness": self.sweetness,
            "days_lactating": self.days_lactating,
            "total_produced_liters": self.total_produced_liters,
            "times_milked": self.times_milked,
            "last_milked": self.last_milked.isoformat() if self.last_milked else None,
            "hours_since_milking": self.hours_since_milking,
            "production_bonus": self.production_bonus,
            "quality_bonus": self.quality_bonus,
        }
    
    @classmethod
    def from_dict(cls, data: dict) -> "LactationStats":
        stats = cls()
        for key, value in data.items():
            if key == "stage":
                stats.stage = LactationStage(value)
            elif key == "milk_type":
                stats.milk_type = MilkType(value)
            elif key == "last_milked" and value:
                stats.last_milked = datetime.fromisoformat(value)
            elif hasattr(stats, key):
                setattr(stats, key, value)
        return stats


@dataclass
class BreedingStats:
    """Breeding-related statistics."""
    
    # Fertility
    fertility_rating: int = 50        # 0-100
    is_fertile: bool = True
    
    # Heat cycle
    in_heat: bool = False
    heat_intensity: int = 0           # 0-100
    days_until_heat: int = 28
    heat_duration_days: int = 3
    days_in_heat: int = 0
    
    # Pregnancy
    is_pregnant: bool = False
    pregnancy_day: int = 0
    pregnancy_duration: int = 270     # Days (roughly 9 months)
    litter_size: int = 1
    sire_dbref: str = ""
    sire_name: str = ""
    
    # History
    times_bred: int = 0
    successful_pregnancies: int = 0
    total_offspring: int = 0
    
    # Last breeding
    last_bred: Optional[datetime] = None
    last_sire: str = ""
    
    @property
    def is_breedable(self) -> bool:
        """Check if can be bred."""
        return self.is_fertile and not self.is_pregnant and self.in_heat
    
    @property
    def pregnancy_progress(self) -> float:
        """Get pregnancy percentage."""
        if not self.is_pregnant:
            return 0.0
        return (self.pregnancy_day / self.pregnancy_duration) * 100
    
    @property
    def trimester(self) -> int:
        """Get current trimester (1-3)."""
        if not self.is_pregnant:
            return 0
        progress = self.pregnancy_progress
        if progress < 33:
            return 1
        elif progress < 66:
            return 2
        return 3
    
    def trigger_heat(self) -> str:
        """Trigger heat cycle."""
        self.in_heat = True
        self.heat_intensity = random.randint(60, 100)
        self.days_in_heat = 0
        return f"Heat cycle begins! Intensity: {self.heat_intensity}/100"
    
    def advance_heat(self) -> str:
        """Advance heat cycle by one day."""
        if not self.in_heat:
            self.days_until_heat -= 1
            if self.days_until_heat <= 0:
                return self.trigger_heat()
            return ""
        
        self.days_in_heat += 1
        if self.days_in_heat >= self.heat_duration_days:
            self.in_heat = False
            self.heat_intensity = 0
            self.days_until_heat = 28
            return "Heat cycle ends."
        
        return f"Heat continues. Day {self.days_in_heat}/{self.heat_duration_days}"
    
    def breed(self, sire_dbref: str, sire_name: str) -> Tuple[bool, str]:
        """
        Attempt breeding.
        Returns (success, message).
        """
        if not self.is_breedable:
            if self.is_pregnant:
                return False, "Already pregnant."
            if not self.in_heat:
                return False, "Not in heat."
            if not self.is_fertile:
                return False, "Not fertile."
            return False, "Cannot breed."
        
        self.times_bred += 1
        self.last_bred = datetime.now()
        self.last_sire = sire_name
        
        # Calculate conception chance
        chance = self.fertility_rating / 100
        chance *= (self.heat_intensity / 100)
        chance = min(0.95, chance + 0.2)  # Base 20% + modifiers, max 95%
        
        if random.random() < chance:
            self.is_pregnant = True
            self.pregnancy_day = 0
            self.sire_dbref = sire_dbref
            self.sire_name = sire_name
            self.in_heat = False
            self.heat_intensity = 0
            
            # Determine litter size
            self.litter_size = 1
            if random.random() < 0.15:
                self.litter_size = 2
            if random.random() < 0.03:
                self.litter_size = 3
            
            return True, f"Breeding successful! Conception confirmed."
        
        return False, "Breeding complete, but no conception this time."
    
    def advance_pregnancy(self) -> Tuple[bool, str]:
        """
        Advance pregnancy by one day.
        Returns (gave_birth, message).
        """
        if not self.is_pregnant:
            return False, ""
        
        self.pregnancy_day += 1
        
        if self.pregnancy_day >= self.pregnancy_duration:
            # Birth!
            offspring = self.litter_size
            self.successful_pregnancies += 1
            self.total_offspring += offspring
            
            # Reset
            self.is_pregnant = False
            self.pregnancy_day = 0
            self.sire_dbref = ""
            self.sire_name = ""
            self.litter_size = 1
            
            return True, f"Birth! {offspring} offspring delivered."
        
        return False, f"Pregnancy day {self.pregnancy_day}/{self.pregnancy_duration}"
    
    def to_dict(self) -> dict:
        return {
            "fertility_rating": self.fertility_rating,
            "is_fertile": self.is_fertile,
            "in_heat": self.in_heat,
            "heat_intensity": self.heat_intensity,
            "days_until_heat": self.days_until_heat,
            "heat_duration_days": self.heat_duration_days,
            "days_in_heat": self.days_in_heat,
            "is_pregnant": self.is_pregnant,
            "pregnancy_day": self.pregnancy_day,
            "pregnancy_duration": self.pregnancy_duration,
            "litter_size": self.litter_size,
            "sire_dbref": self.sire_dbref,
            "sire_name": self.sire_name,
            "times_bred": self.times_bred,
            "successful_pregnancies": self.successful_pregnancies,
            "total_offspring": self.total_offspring,
            "last_bred": self.last_bred.isoformat() if self.last_bred else None,
            "last_sire": self.last_sire,
        }
    
    @classmethod
    def from_dict(cls, data: dict) -> "BreedingStats":
        stats = cls()
        for key, value in data.items():
            if key == "last_bred" and value:
                stats.last_bred = datetime.fromisoformat(value)
            elif hasattr(stats, key):
                setattr(stats, key, value)
        return stats


@dataclass
class HucowStats:
    """Complete hucow statistics."""
    
    # Identity
    hucow_id: str = ""
    name: str = ""
    given_name: str = ""              # Assigned cow name
    tag_number: str = ""              # Ear tag number
    
    # Grade
    grade: HucowGrade = HucowGrade.UNTRAINED
    
    # Physical
    breast_size: str = "average"      # small, average, large, huge, massive
    body_type: str = "average"        # slim, average, curvy, plump, fat
    udder_condition: str = "healthy"  # healthy, sore, damaged, enhanced
    
    # Stats
    docility: int = 50                # 0-100, how compliant
    contentment: int = 50             # 0-100, happiness
    training_progress: int = 0        # 0-100
    
    # Current state
    behavior: HucowBehavior = HucowBehavior.RESTLESS
    
    # Sub-stats
    lactation: LactationStats = field(default_factory=LactationStats)
    breeding: BreedingStats = field(default_factory=BreedingStats)
    
    # Location
    assigned_stall: str = ""
    assigned_herd: str = ""
    
    # Owner
    owner_dbref: str = ""
    owner_name: str = ""
    
    # Value
    purchase_price: int = 0
    current_value: int = 0
    
    # Records
    days_on_farm: int = 0
    punishments_received: int = 0
    rewards_received: int = 0
    escape_attempts: int = 0
    
    def update_behavior(self) -> str:
        """Update behavior based on stats."""
        old = self.behavior
        
        if self.breeding.in_heat:
            self.behavior = HucowBehavior.HEAT
        elif self.lactation.is_engorged:
            self.behavior = HucowBehavior.NEEDY
        elif self.contentment < 20:
            self.behavior = HucowBehavior.RESISTANT
        elif self.contentment < 40:
            self.behavior = HucowBehavior.RESTLESS
        elif self.docility > 70 and self.contentment > 60:
            self.behavior = HucowBehavior.CONTENT
        elif self.docility > 80:
            self.behavior = HucowBehavior.DOCILE
        else:
            self.behavior = HucowBehavior.RESTLESS
        
        if old != self.behavior:
            return f"Behavior changed: {old.value} → {self.behavior.value}"
        return ""
    
    def calculate_value(self) -> int:
        """Calculate current market value."""
        base = 500
        
        # Grade multiplier
        grade_mult = {
            HucowGrade.UNTRAINED: 0.5,
            HucowGrade.HEIFER: 0.8,
            HucowGrade.STANDARD: 1.0,
            HucowGrade.QUALITY: 1.5,
            HucowGrade.PREMIUM: 2.0,
            HucowGrade.PRIZE: 3.0,
            HucowGrade.BREEDER: 2.5,
        }
        base *= grade_mult.get(self.grade, 1.0)
        
        # Production bonus
        if self.lactation.stage == LactationStage.MATURE:
            base += self.lactation.production_rate_ml_hour * 10
        
        # Breeding bonus
        if self.breeding.is_fertile:
            base += 200
        if self.breeding.successful_pregnancies > 0:
            base += self.breeding.successful_pregnancies * 100
        
        # Docility bonus
        base += self.docility * 2
        
        # Breast size bonus
        size_bonus = {
            "small": 0,
            "average": 50,
            "large": 150,
            "huge": 300,
            "massive": 500,
        }
        base += size_bonus.get(self.breast_size, 0)
        
        self.current_value = int(base)
        return self.current_value
    
    def get_status_display(self) -> str:
        """Get formatted status display."""
        lines = [f"=== Hucow Status: {self.name} ==="]
        if self.given_name:
            lines.append(f"Cow Name: {self.given_name}")
        if self.tag_number:
            lines.append(f"Tag: #{self.tag_number}")
        
        lines.append(f"Grade: {self.grade.value}")
        lines.append(f"Behavior: {self.behavior.value}")
        lines.append(f"Docility: {self.docility}/100")
        lines.append(f"Contentment: {self.contentment}/100")
        
        lines.append(f"\n--- Lactation ---")
        lines.append(f"Stage: {self.lactation.stage.value}")
        lines.append(f"Fill: {self.lactation.current_fill_ml}/{self.lactation.max_capacity_ml}ml ({self.lactation.fill_percentage:.0f}%)")
        lines.append(f"Production: {self.lactation.production_rate_ml_hour}ml/hour")
        lines.append(f"Total Produced: {self.lactation.total_produced_liters:.1f}L")
        
        lines.append(f"\n--- Breeding ---")
        lines.append(f"Fertility: {self.breeding.fertility_rating}/100")
        if self.breeding.in_heat:
            lines.append(f"IN HEAT! Intensity: {self.breeding.heat_intensity}/100")
        elif self.breeding.is_pregnant:
            lines.append(f"PREGNANT: Day {self.breeding.pregnancy_day}/{self.breeding.pregnancy_duration}")
            lines.append(f"Sire: {self.breeding.sire_name}")
        else:
            lines.append(f"Days until heat: {self.breeding.days_until_heat}")
        
        lines.append(f"Times Bred: {self.breeding.times_bred}")
        lines.append(f"Offspring: {self.breeding.total_offspring}")
        
        self.calculate_value()
        lines.append(f"\nCurrent Value: {self.current_value} gold")
        
        return "\n".join(lines)
    
    def to_dict(self) -> dict:
        return {
            "hucow_id": self.hucow_id,
            "name": self.name,
            "given_name": self.given_name,
            "tag_number": self.tag_number,
            "grade": self.grade.value,
            "breast_size": self.breast_size,
            "body_type": self.body_type,
            "udder_condition": self.udder_condition,
            "docility": self.docility,
            "contentment": self.contentment,
            "training_progress": self.training_progress,
            "behavior": self.behavior.value,
            "lactation": self.lactation.to_dict(),
            "breeding": self.breeding.to_dict(),
            "assigned_stall": self.assigned_stall,
            "assigned_herd": self.assigned_herd,
            "owner_dbref": self.owner_dbref,
            "owner_name": self.owner_name,
            "purchase_price": self.purchase_price,
            "current_value": self.current_value,
            "days_on_farm": self.days_on_farm,
            "punishments_received": self.punishments_received,
            "rewards_received": self.rewards_received,
            "escape_attempts": self.escape_attempts,
        }
    
    @classmethod
    def from_dict(cls, data: dict) -> "HucowStats":
        stats = cls()
        for key, value in data.items():
            if key == "grade":
                stats.grade = HucowGrade(value)
            elif key == "behavior":
                stats.behavior = HucowBehavior(value)
            elif key == "lactation":
                stats.lactation = LactationStats.from_dict(value)
            elif key == "breeding":
                stats.breeding = BreedingStats.from_dict(value)
            elif hasattr(stats, key):
                setattr(stats, key, value)
        return stats


# =============================================================================
# HUCOW MIXIN
# =============================================================================

class HucowMixin:
    """
    Mixin for characters that can be hucows.
    Add to your Character typeclass.
    """
    
    @property
    def hucow_stats(self) -> HucowStats:
        """Get hucow stats."""
        data = self.db.hucow_stats
        if data:
            return HucowStats.from_dict(data)
        return HucowStats(name=self.key)
    
    @hucow_stats.setter
    def hucow_stats(self, stats: HucowStats) -> None:
        """Set hucow stats."""
        self.db.hucow_stats = stats.to_dict()
    
    def save_hucow_stats(self, stats: HucowStats) -> None:
        """Save hucow stats."""
        self.db.hucow_stats = stats.to_dict()
    
    @property
    def is_hucow(self) -> bool:
        """Check if registered as hucow."""
        return bool(self.db.hucow_stats)
    
    @property
    def is_lactating(self) -> bool:
        """Check if currently lactating."""
        if not self.is_hucow:
            return False
        return self.hucow_stats.lactation.stage != LactationStage.DRY
    
    @property
    def needs_milking(self) -> bool:
        """Check if needs milking."""
        if not self.is_hucow:
            return False
        return self.hucow_stats.lactation.needs_milking
    
    @property
    def in_heat(self) -> bool:
        """Check if in heat."""
        if not self.is_hucow:
            return False
        return self.hucow_stats.breeding.in_heat
    
    def initialize_hucow(
        self,
        owner,
        given_name: str = "",
        tag_number: str = "",
    ) -> str:
        """Initialize as a hucow."""
        import random
        
        stats = HucowStats(
            hucow_id=f"HCW-{datetime.now().strftime('%Y%m%d%H%M%S')}-{random.randint(1000, 9999)}",
            name=self.key,
            given_name=given_name or f"Cow-{random.randint(100, 999)}",
            tag_number=tag_number or str(random.randint(10000, 99999)),
            owner_dbref=owner.dbref if owner else "",
            owner_name=owner.key if owner else "",
            grade=HucowGrade.UNTRAINED,
        )
        
        self.save_hucow_stats(stats)
        
        return f"Registered as hucow #{stats.tag_number}: {stats.given_name}"


# Import from bulls module
from .bulls import (
    BullGrade,
    BullType,
    RutState,
    BreedingStyle,
    BullPhysical,
    BullBreedingStats,
    BullStats,
    BullMixin,
    create_futanari_bull,
    PRESET_BULLS,
)

# Import from facilities module
from .facilities import (
    FacilityType,
    MilkingMethod,
    StallFeature,
    MilkingStation,
    MilkingParlor,
    BreedingPen,
    BreedingBarn,
    Herd,
    Farm,
    create_standard_milking_parlor,
    create_standard_breeding_barn,
    create_standard_farm,
)

# Import from npcs module
from .npcs import (
    FarmhandRole,
    NPCPersonality,
    FarmhandNPC,
    generate_farmhand,
    generate_farm_staff,
    BreedingEvent,
    BreedingEventGenerator,
    PRESET_FARMHANDS,
)

# Import from commands module
from .commands import HucowCmdSet


__version__ = "1.0.0"

__all__ = [
    # Hucow stats
    "HucowGrade",
    "LactationStage",
    "MilkType",
    "HucowBehavior",
    "StallType",
    "LactationStats",
    "BreedingStats",
    "HucowStats",
    "HucowMixin",
    
    # Bulls
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
    
    # Facilities
    "FacilityType",
    "MilkingMethod",
    "StallFeature",
    "MilkingStation",
    "MilkingParlor",
    "BreedingPen",
    "BreedingBarn",
    "Herd",
    "Farm",
    "create_standard_milking_parlor",
    "create_standard_breeding_barn",
    "create_standard_farm",
    
    # NPCs
    "FarmhandRole",
    "NPCPersonality",
    "FarmhandNPC",
    "generate_farmhand",
    "generate_farm_staff",
    "BreedingEvent",
    "BreedingEventGenerator",
    "PRESET_FARMHANDS",
    
    # Commands
    "HucowCmdSet",
]
