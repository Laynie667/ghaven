"""
Pony Play System
================

Complete pony play mechanics including:
- Pony training and stats
- Cart pulling with stamina/endurance
- Pony shows and competitions
- Breeding programs
- Harness and tack equipment
"""

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any, Tuple
from enum import Enum
from datetime import datetime, timedelta
import random


# =============================================================================
# ENUMS
# =============================================================================

class PonyType(Enum):
    """Types of ponies."""
    DRAFT = "draft"               # Heavy hauling
    RIDING = "riding"             # Personal mount
    SHOW = "show"                 # Display and competition
    RACING = "racing"             # Speed
    BREEDING = "breeding"         # Stud/broodmare
    PLEASURE = "pleasure"         # Sexual use


class PonyGait(Enum):
    """Pony gaits."""
    STAND = "stand"
    WALK = "walk"
    TROT = "trot"
    CANTER = "canter"
    GALLOP = "gallop"
    PRANCE = "prance"             # High-stepping show gait


class TackType(Enum):
    """Types of tack and equipment."""
    BRIDLE = "bridle"
    BIT = "bit"
    HARNESS = "harness"
    SADDLE = "saddle"
    BLINDERS = "blinders"
    HOOVES = "hooves"             # Hoof boots
    TAIL = "tail"                 # Tail plug
    MANE = "mane"                 # Head plume
    BELLS = "bells"               # Decorative bells
    CART_HARNESS = "cart_harness"


class ShowCategory(Enum):
    """Pony show categories."""
    DRESSAGE = "dressage"         # Precise movements
    CART_PULL = "cart_pull"       # Pulling weight
    RACING = "racing"             # Speed events
    BEAUTY = "beauty"             # Appearance
    OBEDIENCE = "obedience"       # Following commands
    ENDURANCE = "endurance"       # Long distance
    BREEDING_DISPLAY = "breeding_display"  # Sexual display


# =============================================================================
# PONY TACK
# =============================================================================

@dataclass
class PonyTack:
    """A piece of pony equipment."""
    
    tack_id: str = ""
    tack_type: TackType = TackType.BRIDLE
    name: str = ""
    description: str = ""
    
    # Quality
    quality: str = "standard"     # "training", "standard", "show", "luxury"
    material: str = "leather"
    
    # Stats
    comfort: int = 50             # 0-100
    control: int = 50             # How much control it gives
    appearance: int = 50          # For shows
    
    # Special effects
    has_spikes: bool = False      # Painful
    has_stimulation: bool = False # Sexual
    is_locked: bool = False       # Can't be removed
    
    # Bit specifics
    bit_severity: int = 0         # 0-100, how harsh


@dataclass
class PonyTackSet:
    """Complete set of pony tack."""
    
    set_id: str = ""
    name: str = ""
    
    # Components
    bridle: Optional[PonyTack] = None
    bit: Optional[PonyTack] = None
    harness: Optional[PonyTack] = None
    saddle: Optional[PonyTack] = None
    blinders: Optional[PonyTack] = None
    hooves: Optional[PonyTack] = None
    tail_plug: Optional[PonyTack] = None
    mane_plume: Optional[PonyTack] = None
    bells: Optional[PonyTack] = None
    
    @property
    def total_comfort(self) -> int:
        """Get total comfort from all tack."""
        total = 0
        count = 0
        for item in [self.bridle, self.bit, self.harness, self.saddle, 
                    self.hooves, self.tail_plug]:
            if item:
                total += item.comfort
                count += 1
        return total // max(1, count)
    
    @property
    def total_control(self) -> int:
        """Get total control."""
        total = 0
        for item in [self.bridle, self.bit, self.harness, self.blinders]:
            if item:
                total += item.control
        return min(100, total)
    
    @property
    def total_appearance(self) -> int:
        """Get total appearance score."""
        total = 0
        count = 0
        for item in [self.bridle, self.harness, self.hooves, 
                    self.tail_plug, self.mane_plume, self.bells]:
            if item:
                total += item.appearance
                count += 1
        return total // max(1, count)


# Preset tack
PRESET_TACK = {
    "training_bridle": PonyTack(
        tack_id="train_bridle",
        tack_type=TackType.BRIDLE,
        name="Training Bridle",
        quality="training",
        comfort=60,
        control=40,
        appearance=30,
    ),
    "show_bridle": PonyTack(
        tack_id="show_bridle",
        tack_type=TackType.BRIDLE,
        name="Show Bridle",
        quality="show",
        material="patent leather",
        comfort=70,
        control=50,
        appearance=80,
    ),
    "harsh_bit": PonyTack(
        tack_id="harsh_bit",
        tack_type=TackType.BIT,
        name="Harsh Correction Bit",
        quality="standard",
        material="steel",
        comfort=20,
        control=80,
        appearance=40,
        bit_severity=80,
    ),
    "plug_tail": PonyTack(
        tack_id="plug_tail",
        tack_type=TackType.TAIL,
        name="Plug Tail",
        description="Long horsehair tail attached to anal plug",
        comfort=40,
        control=0,
        appearance=70,
        has_stimulation=True,
    ),
    "hoof_boots": PonyTack(
        tack_id="hoof_boots",
        tack_type=TackType.HOOVES,
        name="Hoof Boots",
        description="Forces walking on tiptoe",
        comfort=30,
        control=20,
        appearance=60,
    ),
}


# =============================================================================
# PONY STATS
# =============================================================================

@dataclass
class PonyStats:
    """Complete pony statistics."""
    
    pony_id: str = ""
    pony_name: str = ""           # Pony name (not human name)
    registration: str = ""        # Registry number
    
    # Type
    pony_type: PonyType = PonyType.RIDING
    
    # Physical stats
    strength: int = 50            # Pulling power
    speed: int = 50               # Running speed
    endurance: int = 50           # How long can work
    agility: int = 50             # Precision movements
    
    # Current state
    current_stamina: int = 100
    max_stamina: int = 100
    current_gait: PonyGait = PonyGait.STAND
    
    # Training
    training_level: int = 0       # 0-100
    obedience: int = 30           # 0-100
    gait_training: Dict[str, int] = field(default_factory=dict)  # Gait -> skill
    
    # Appearance
    beauty: int = 50
    coat_condition: int = 50      # How well groomed
    mane_style: str = "natural"
    
    # Equipment
    current_tack: Optional[PonyTackSet] = None
    
    # Breeding (if applicable)
    is_stallion: bool = False     # Has cock
    is_mare: bool = True          # Has pussy
    fertility: int = 50
    times_bred: int = 0
    offspring: int = 0
    
    # Competition
    shows_entered: int = 0
    shows_won: int = 0
    ribbons: List[str] = field(default_factory=list)
    
    # Work
    total_distance_pulled: float = 0.0  # km
    total_hours_worked: float = 0.0
    
    # Owner
    owner_dbref: str = ""
    owner_name: str = ""
    stable: str = ""
    
    def use_stamina(self, amount: int) -> Tuple[bool, str]:
        """Use stamina for activity."""
        if self.current_stamina < amount:
            return False, "Too exhausted!"
        
        self.current_stamina -= amount
        
        if self.current_stamina < 20:
            return True, "Pony is getting exhausted!"
        return True, f"Stamina: {self.current_stamina}/{self.max_stamina}"
    
    def rest(self, hours: float = 1.0) -> str:
        """Rest to recover stamina."""
        recovery = int(hours * 20)
        self.current_stamina = min(self.max_stamina, self.current_stamina + recovery)
        return f"Rested. Stamina: {self.current_stamina}/{self.max_stamina}"
    
    def change_gait(self, gait: PonyGait) -> str:
        """Change current gait."""
        self.current_gait = gait
        
        skill = self.gait_training.get(gait.value, 0)
        
        if skill < 30:
            return f"Struggles to maintain {gait.value}."
        elif skill < 60:
            return f"Moves into a {gait.value}."
        else:
            return f"Executes a perfect {gait.value}."
    
    def train_gait(self, gait: PonyGait, hours: float = 1.0) -> str:
        """Train a specific gait."""
        current = self.gait_training.get(gait.value, 0)
        gain = int(hours * 5)
        
        self.gait_training[gait.value] = min(100, current + gain)
        self.training_level = sum(self.gait_training.values()) // max(1, len(self.gait_training))
        
        self.use_stamina(int(hours * 15))
        
        return f"{gait.value} training: {self.gait_training[gait.value]}/100"
    
    def calculate_pull_capacity(self) -> int:
        """Calculate how much weight can pull in kg."""
        base = self.strength * 2
        
        # Endurance affects sustained pulling
        endurance_mod = self.endurance / 100
        
        # Training bonus
        training_mod = 1 + (self.training_level / 200)
        
        # Tack affects control/efficiency
        tack_mod = 1.0
        if self.current_tack:
            tack_mod = 1 + (self.current_tack.total_control / 200)
        
        return int(base * endurance_mod * training_mod * tack_mod)
    
    def calculate_speed(self, gait: PonyGait) -> float:
        """Calculate speed in km/h for a gait."""
        base_speeds = {
            PonyGait.STAND: 0,
            PonyGait.WALK: 4,
            PonyGait.TROT: 10,
            PonyGait.CANTER: 20,
            PonyGait.GALLOP: 35,
            PonyGait.PRANCE: 3,
        }
        
        base = base_speeds.get(gait, 0)
        
        # Speed stat affects
        speed_mod = self.speed / 50
        
        # Training in this gait
        gait_skill = self.gait_training.get(gait.value, 30) / 100
        
        return base * speed_mod * gait_skill
    
    def get_status(self) -> str:
        """Get pony status display."""
        lines = [f"=== {self.pony_name} ({self.registration}) ==="]
        lines.append(f"Type: {self.pony_type.value.upper()}")
        
        lines.append(f"\n--- Physical Stats ---")
        lines.append(f"Strength: {self.strength} | Speed: {self.speed}")
        lines.append(f"Endurance: {self.endurance} | Agility: {self.agility}")
        lines.append(f"Stamina: {self.current_stamina}/{self.max_stamina}")
        
        lines.append(f"\n--- Training ---")
        lines.append(f"Level: {self.training_level}/100")
        lines.append(f"Obedience: {self.obedience}/100")
        for gait, skill in self.gait_training.items():
            lines.append(f"  {gait}: {skill}/100")
        
        lines.append(f"\n--- Appearance ---")
        lines.append(f"Beauty: {self.beauty}/100")
        lines.append(f"Coat: {self.coat_condition}/100")
        
        lines.append(f"\n--- Career ---")
        lines.append(f"Shows: {self.shows_won}/{self.shows_entered} won")
        lines.append(f"Distance Pulled: {self.total_distance_pulled:.1f}km")
        lines.append(f"Hours Worked: {self.total_hours_worked:.1f}")
        
        if self.ribbons:
            lines.append(f"Ribbons: {', '.join(self.ribbons[-5:])}")
        
        return "\n".join(lines)
    
    def to_dict(self) -> dict:
        return {
            "pony_id": self.pony_id,
            "pony_name": self.pony_name,
            "registration": self.registration,
            "pony_type": self.pony_type.value,
            "strength": self.strength,
            "speed": self.speed,
            "endurance": self.endurance,
            "agility": self.agility,
            "current_stamina": self.current_stamina,
            "max_stamina": self.max_stamina,
            "training_level": self.training_level,
            "obedience": self.obedience,
            "gait_training": self.gait_training,
            "beauty": self.beauty,
            "shows_entered": self.shows_entered,
            "shows_won": self.shows_won,
            "ribbons": self.ribbons,
        }
    
    @classmethod
    def from_dict(cls, data: dict) -> "PonyStats":
        stats = cls()
        for key, value in data.items():
            if key == "pony_type":
                stats.pony_type = PonyType(value)
            elif hasattr(stats, key):
                setattr(stats, key, value)
        return stats


# =============================================================================
# CART PULLING
# =============================================================================

@dataclass
class Cart:
    """A cart for ponies to pull."""
    
    cart_id: str = ""
    name: str = ""
    cart_type: str = "standard"   # "light", "standard", "heavy", "racing"
    
    # Weight
    empty_weight_kg: int = 50
    max_capacity_kg: int = 200
    current_load_kg: int = 0
    
    # Passengers
    max_passengers: int = 2
    current_passengers: List[str] = field(default_factory=list)
    
    # Features
    has_whip_holder: bool = True
    has_reins: bool = True
    has_bells: bool = False
    is_racing_cart: bool = False
    
    @property
    def total_weight(self) -> int:
        """Get total weight including passengers."""
        passenger_weight = len(self.current_passengers) * 70  # 70kg average
        return self.empty_weight_kg + self.current_load_kg + passenger_weight


@dataclass
class CartPullSession:
    """A cart pulling session."""
    
    session_id: str = ""
    
    # Participants
    pony_dbref: str = ""
    pony_name: str = ""
    driver_dbref: str = ""
    driver_name: str = ""
    
    # Cart
    cart: Optional[Cart] = None
    
    # Journey
    distance_km: float = 0.0
    distance_completed: float = 0.0
    
    # Performance
    average_speed: float = 0.0
    stamina_used: int = 0
    
    # Status
    is_active: bool = False
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    
    # Events
    events: List[str] = field(default_factory=list)
    whip_uses: int = 0
    stumbles: int = 0
    
    def start(self, pony: PonyStats, distance: float) -> str:
        """Start a pulling session."""
        self.is_active = True
        self.start_time = datetime.now()
        self.distance_km = distance
        self.pony_name = pony.pony_name
        
        # Check if pony can pull the weight
        capacity = pony.calculate_pull_capacity()
        weight = self.cart.total_weight if self.cart else 0
        
        if weight > capacity * 1.5:
            return f"Cart too heavy! {pony.pony_name} cannot pull {weight}kg (max: {capacity}kg)"
        
        if weight > capacity:
            self.events.append("Straining under heavy load")
        
        return f"{pony.pony_name} begins pulling. Distance: {distance}km"
    
    def progress(self, pony: PonyStats, minutes: int = 30) -> Tuple[str, bool]:
        """
        Progress the journey.
        Returns (message, journey_complete).
        """
        if not self.is_active:
            return "No active journey.", False
        
        # Calculate speed based on current gait and stats
        speed = pony.calculate_speed(pony.current_gait)
        
        # Weight penalty
        if self.cart:
            weight_ratio = self.cart.total_weight / max(1, pony.calculate_pull_capacity())
            speed *= max(0.3, 1 - (weight_ratio - 1) * 0.5)
        
        # Distance covered
        hours = minutes / 60
        distance = speed * hours
        self.distance_completed += distance
        
        # Stamina cost
        stamina_cost = int(minutes * 0.5)
        if pony.current_gait in [PonyGait.CANTER, PonyGait.GALLOP]:
            stamina_cost *= 2
        if self.cart and self.cart.total_weight > pony.calculate_pull_capacity():
            stamina_cost = int(stamina_cost * 1.5)
        
        success, msg = pony.use_stamina(stamina_cost)
        self.stamina_used += stamina_cost
        
        if not success:
            self.events.append("Collapsed from exhaustion")
            return "Pony collapses from exhaustion!", False
        
        # Random events
        if random.random() < 0.1:
            if pony.training_level < 50 and random.random() < 0.3:
                self.stumbles += 1
                self.events.append("Stumbled")
        
        # Check completion
        if self.distance_completed >= self.distance_km:
            return self.complete(pony), True
        
        remaining = self.distance_km - self.distance_completed
        return f"Progress: {self.distance_completed:.1f}/{self.distance_km}km ({remaining:.1f}km remaining)", False
    
    def use_whip(self, pony: PonyStats) -> str:
        """Use the whip on the pony."""
        self.whip_uses += 1
        self.events.append("Whipped")
        
        # Temporary speed boost at stamina cost
        pony.current_stamina = max(0, pony.current_stamina - 5)
        
        if pony.obedience < 50:
            if random.random() < 0.2:
                return f"{pony.pony_name} bucks at the whip!"
        
        return f"{pony.pony_name} lurches forward under the whip!"
    
    def complete(self, pony: PonyStats) -> str:
        """Complete the journey."""
        self.is_active = False
        self.end_time = datetime.now()
        
        duration = (self.end_time - self.start_time).total_seconds() / 3600
        self.average_speed = self.distance_km / max(0.1, duration)
        
        # Update pony stats
        pony.total_distance_pulled += self.distance_km
        pony.total_hours_worked += duration
        
        # Training gain
        pony.endurance = min(100, pony.endurance + 1)
        pony.strength = min(100, pony.strength + 1)
        
        return f"Journey complete! {self.distance_km}km in {duration:.1f}h (avg {self.average_speed:.1f}km/h)"
    
    def get_summary(self) -> str:
        """Get session summary."""
        lines = [f"=== Cart Pull Session ==="]
        lines.append(f"Pony: {self.pony_name}")
        lines.append(f"Distance: {self.distance_completed:.1f}/{self.distance_km}km")
        lines.append(f"Avg Speed: {self.average_speed:.1f}km/h")
        lines.append(f"Stamina Used: {self.stamina_used}")
        lines.append(f"Whip Uses: {self.whip_uses}")
        lines.append(f"Stumbles: {self.stumbles}")
        
        return "\n".join(lines)


# =============================================================================
# PONY SHOW
# =============================================================================

@dataclass
class ShowCompetitor:
    """A competitor in a pony show."""
    
    pony_dbref: str = ""
    pony_name: str = ""
    handler_name: str = ""
    
    # Scores
    scores: Dict[str, int] = field(default_factory=dict)
    total_score: int = 0
    
    # Placement
    placement: int = 0            # 1st, 2nd, etc.


@dataclass
class PonyShow:
    """A pony show competition."""
    
    show_id: str = ""
    name: str = ""
    category: ShowCategory = ShowCategory.DRESSAGE
    
    # Location
    location: str = ""
    
    # Competitors
    competitors: List[ShowCompetitor] = field(default_factory=list)
    max_competitors: int = 10
    
    # Judging
    judges: List[str] = field(default_factory=list)
    
    # Status
    is_active: bool = False
    is_complete: bool = False
    
    # Prizes
    first_prize: int = 500
    second_prize: int = 250
    third_prize: int = 100
    first_ribbon: str = "Blue Ribbon"
    
    def enter_competitor(self, pony: PonyStats, handler_name: str) -> Tuple[bool, str]:
        """Enter a pony in the show."""
        if len(self.competitors) >= self.max_competitors:
            return False, "Show is full."
        
        if any(c.pony_dbref == pony.pony_id for c in self.competitors):
            return False, "Already entered."
        
        competitor = ShowCompetitor(
            pony_dbref=pony.pony_id,
            pony_name=pony.pony_name,
            handler_name=handler_name,
        )
        
        self.competitors.append(competitor)
        
        return True, f"{pony.pony_name} entered in {self.name}."
    
    def judge_competitor(self, pony: PonyStats, competitor: ShowCompetitor) -> int:
        """Judge a competitor's performance."""
        score = 0
        
        if self.category == ShowCategory.DRESSAGE:
            # Judged on gait precision and obedience
            score += pony.agility * 3
            score += pony.obedience * 2
            score += sum(pony.gait_training.values()) // max(1, len(pony.gait_training))
            if pony.current_tack:
                score += pony.current_tack.total_appearance
            
        elif self.category == ShowCategory.CART_PULL:
            # Judged on strength and endurance
            score += pony.strength * 3
            score += pony.endurance * 2
            score += pony.training_level
            
        elif self.category == ShowCategory.RACING:
            # Judged on speed
            score += pony.speed * 4
            score += pony.endurance
            gallop_skill = pony.gait_training.get("gallop", 30)
            score += gallop_skill
            
        elif self.category == ShowCategory.BEAUTY:
            # Judged on appearance
            score += pony.beauty * 3
            score += pony.coat_condition * 2
            if pony.current_tack:
                score += pony.current_tack.total_appearance * 2
            
        elif self.category == ShowCategory.OBEDIENCE:
            # Judged on obedience and training
            score += pony.obedience * 4
            score += pony.training_level * 2
            
        elif self.category == ShowCategory.ENDURANCE:
            # Judged on endurance and stamina
            score += pony.endurance * 4
            score += pony.max_stamina // 2
            score += pony.strength
        
        # Random factor for competition
        score += random.randint(-20, 20)
        
        competitor.total_score = max(0, score)
        return competitor.total_score
    
    def run_show(self, ponies: Dict[str, PonyStats]) -> str:
        """Run the complete show."""
        if len(self.competitors) < 2:
            return "Not enough competitors."
        
        self.is_active = True
        
        # Judge all competitors
        for comp in self.competitors:
            pony = ponies.get(comp.pony_dbref)
            if pony:
                self.judge_competitor(pony, comp)
        
        # Rank by score
        sorted_comps = sorted(self.competitors, key=lambda c: c.total_score, reverse=True)
        
        for i, comp in enumerate(sorted_comps):
            comp.placement = i + 1
        
        self.is_active = False
        self.is_complete = True
        
        return self.get_results()
    
    def get_results(self) -> str:
        """Get show results."""
        lines = [f"=== {self.name} Results ==="]
        lines.append(f"Category: {self.category.value.upper()}")
        
        sorted_comps = sorted(self.competitors, key=lambda c: c.placement)
        
        for comp in sorted_comps:
            place_str = {1: "🥇", 2: "🥈", 3: "🥉"}.get(comp.placement, f"{comp.placement}.")
            prize = {1: self.first_prize, 2: self.second_prize, 3: self.third_prize}.get(comp.placement, 0)
            
            lines.append(f"{place_str} {comp.pony_name} ({comp.handler_name}) - {comp.total_score} pts")
            if prize:
                lines.append(f"   Prize: {prize}g")
        
        return "\n".join(lines)


# =============================================================================
# PONY BREEDING
# =============================================================================

@dataclass
class PonyBreedingRecord:
    """Record of pony breeding."""
    
    record_id: str = ""
    
    # Parents
    sire_id: str = ""
    sire_name: str = ""
    dam_id: str = ""
    dam_name: str = ""
    
    # Breeding
    breed_date: Optional[datetime] = None
    conception: bool = False
    
    # Offspring
    foal_id: str = ""
    foal_name: str = ""
    
    # Inherited stats (averages with variation)
    inherited_strength: int = 0
    inherited_speed: int = 0
    inherited_endurance: int = 0
    inherited_beauty: int = 0


def breed_ponies(sire: PonyStats, dam: PonyStats) -> Tuple[bool, str, Optional[PonyStats]]:
    """
    Breed two ponies.
    Returns (success, message, offspring_stats or None).
    """
    if not sire.is_stallion:
        return False, f"{sire.pony_name} is not a stallion.", None
    
    if not dam.is_mare:
        return False, f"{dam.pony_name} is not a mare.", None
    
    # Conception chance based on fertility
    chance = (sire.fertility + dam.fertility) / 200
    
    if random.random() > chance:
        sire.times_bred += 1
        dam.times_bred += 1
        return False, "Breeding unsuccessful. No conception.", None
    
    # Create offspring
    foal = PonyStats(
        pony_id=f"FOAL-{datetime.now().strftime('%Y%m%d%H%M%S')}-{random.randint(100, 999)}",
        pony_name=f"Foal of {sire.pony_name}",
        registration=f"F-{random.randint(10000, 99999)}",
    )
    
    # Inherit stats with variation
    def inherit_stat(s1: int, s2: int) -> int:
        avg = (s1 + s2) // 2
        variation = random.randint(-10, 10)
        return max(10, min(100, avg + variation))
    
    foal.strength = inherit_stat(sire.strength, dam.strength)
    foal.speed = inherit_stat(sire.speed, dam.speed)
    foal.endurance = inherit_stat(sire.endurance, dam.endurance)
    foal.agility = inherit_stat(sire.agility, dam.agility)
    foal.beauty = inherit_stat(sire.beauty, dam.beauty)
    foal.fertility = inherit_stat(sire.fertility, dam.fertility)
    
    # Random sex
    foal.is_stallion = random.random() < 0.5
    foal.is_mare = not foal.is_stallion
    
    # Update parents
    sire.times_bred += 1
    sire.offspring += 1
    dam.times_bred += 1
    dam.offspring += 1
    
    sex = "colt" if foal.is_stallion else "filly"
    
    return True, f"Successful breeding! A {sex} is born!", foal


# =============================================================================
# PONY MIXIN
# =============================================================================

class PonyMixin:
    """Mixin for pony play characters."""
    
    @property
    def pony_stats(self) -> PonyStats:
        """Get pony stats."""
        data = self.db.pony_stats
        if data:
            return PonyStats.from_dict(data)
        return PonyStats(pony_id=self.dbref, pony_name=self.key)
    
    @pony_stats.setter
    def pony_stats(self, stats: PonyStats) -> None:
        """Set pony stats."""
        self.db.pony_stats = stats.to_dict()
    
    @property
    def is_pony(self) -> bool:
        """Check if registered as pony."""
        return bool(self.db.pony_stats)


__all__ = [
    "PonyType",
    "PonyGait",
    "TackType",
    "ShowCategory",
    "PonyTack",
    "PonyTackSet",
    "PRESET_TACK",
    "PonyStats",
    "Cart",
    "CartPullSession",
    "ShowCompetitor",
    "PonyShow",
    "PonyBreedingRecord",
    "breed_ponies",
    "PonyMixin",
    "PonyCmdSet",
]

# Import commands
from .commands import PonyCmdSet
