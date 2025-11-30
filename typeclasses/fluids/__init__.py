"""
Enhanced Fluid System
=====================

Extends the base fluid system to support:
- Extreme amounts (liters, gallons, cubic meters)
- Cumflation (belly/body inflation from fluids)
- Visual inflation descriptions
- Production tracking (cum production rate)
"""

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple
from enum import Enum
from datetime import datetime

from ..scale import format_measurement, ScalableCapacity


# =============================================================================
# EXTREME AMOUNT THRESHOLDS
# =============================================================================

# Extended thresholds for hyper play (in ml)
EXTREME_AMOUNT_THRESHOLDS = {
    "trace": 1,
    "drops": 5,
    "small": 15,
    "moderate": 30,
    "large": 60,
    "heavy": 100,
    "soaked": 200,
    "dripping": 300,
    "flooded": 500,
    "drenched": 1000,       # 1 liter
    "pooling": 2000,        # 2 liters
    "torrential": 5000,     # 5 liters
    "flooding": 10000,      # 10 liters
    "deluge": 25000,        # 25 liters
    "ocean": 50000,         # 50 liters
    "tsunami": 100000,      # 100 liters
    "biblical": 500000,     # 500 liters
    "apocalyptic": 1000000, # 1000 liters / 1 cubic meter
}


def extreme_amount_to_word(ml: float) -> str:
    """Convert ml to descriptive word, supporting extreme amounts."""
    for word, threshold in EXTREME_AMOUNT_THRESHOLDS.items():
        if ml <= threshold:
            return word
    return "reality-breaking"


def describe_extreme_amount(ml: float, fluid_name: str = "cum") -> str:
    """Get natural description of extreme fluid amounts."""
    if ml < 1:
        return f"a trace of {fluid_name}"
    elif ml < 5:
        return f"a few drops of {fluid_name}"
    elif ml < 30:
        return f"some {fluid_name}"
    elif ml < 100:
        return f"a noticeable amount of {fluid_name}"
    elif ml < 500:
        return f"a lot of {fluid_name}"
    elif ml < 1000:
        return f"a huge amount of {fluid_name}"
    elif ml < 5000:
        liters = ml / 1000
        return f"{liters:.1f} liters of {fluid_name}"
    elif ml < 50000:
        liters = ml / 1000
        return f"an absurd {liters:.0f} liters of {fluid_name}"
    elif ml < 500000:
        liters = ml / 1000
        return f"an impossible {liters:.0f} liters of {fluid_name}"
    else:
        cubic_meters = ml / 1000000
        return f"a reality-defying {cubic_meters:.1f} cubic meters of {fluid_name}"


# =============================================================================
# INFLATION STATE
# =============================================================================

class InflationLevel(Enum):
    """Visual inflation levels."""
    NONE = "none"
    SLIGHT = "slight"
    NOTICEABLE = "noticeable"
    PRONOUNCED = "pronounced"
    HEAVY = "heavy"
    EXTREME = "extreme"
    MASSIVE = "massive"
    IMMOBILIZING = "immobilizing"
    ROOM_FILLING = "room_filling"
    BUILDING_SIZED = "building_sized"


@dataclass
class InflationState:
    """
    Tracks inflation of a body part or whole body from fluids.
    """
    # Total fluid causing inflation (ml)
    total_fluid_ml: float = 0.0
    
    # Base body scale (affects how much fluid causes visible inflation)
    body_scale: float = 1.0
    
    # How easily this inflates (higher = inflates more visibly)
    inflation_sensitivity: float = 1.0
    
    # Max inflation before immobilization
    max_mobility_inflation: float = 10000.0  # ml at scale 1.0
    
    @property
    def adjusted_amount(self) -> float:
        """Fluid amount adjusted for body scale."""
        # Larger bodies need more fluid to show inflation
        return self.total_fluid_ml / (self.body_scale ** 3)
    
    @property
    def inflation_level(self) -> InflationLevel:
        """Get current inflation level."""
        amt = self.adjusted_amount * self.inflation_sensitivity
        
        if amt < 50:
            return InflationLevel.NONE
        elif amt < 200:
            return InflationLevel.SLIGHT
        elif amt < 500:
            return InflationLevel.NOTICEABLE
        elif amt < 1000:
            return InflationLevel.PRONOUNCED
        elif amt < 3000:
            return InflationLevel.HEAVY
        elif amt < 10000:
            return InflationLevel.EXTREME
        elif amt < 50000:
            return InflationLevel.MASSIVE
        elif amt < 200000:
            return InflationLevel.IMMOBILIZING
        elif amt < 1000000:
            return InflationLevel.ROOM_FILLING
        else:
            return InflationLevel.BUILDING_SIZED
    
    @property
    def is_immobilized(self) -> bool:
        """Check if inflation prevents movement."""
        return self.total_fluid_ml > self.max_mobility_inflation * (self.body_scale ** 3)
    
    def add_fluid(self, ml: float):
        """Add fluid causing inflation."""
        self.total_fluid_ml += ml
    
    def remove_fluid(self, ml: float) -> float:
        """Remove fluid. Returns amount removed."""
        removed = min(ml, self.total_fluid_ml)
        self.total_fluid_ml -= removed
        return removed
    
    def describe(self, body_part: str = "belly") -> str:
        """Get description of inflation state."""
        level = self.inflation_level
        
        descriptions = {
            InflationLevel.NONE: f"flat {body_part}",
            InflationLevel.SLIGHT: f"slightly swollen {body_part}",
            InflationLevel.NOTICEABLE: f"noticeably bloated {body_part}",
            InflationLevel.PRONOUNCED: f"heavily swollen {body_part}, looking pregnant",
            InflationLevel.HEAVY: f"hugely distended {body_part}, like late pregnancy",
            InflationLevel.EXTREME: f"massively inflated {body_part}, taut as a drum",
            InflationLevel.MASSIVE: f"grotesquely bloated {body_part}, bigger than the rest of the body",
            InflationLevel.IMMOBILIZING: f"impossibly inflated {body_part}, unable to move",
            InflationLevel.ROOM_FILLING: f"{body_part} inflated to fill the room",
            InflationLevel.BUILDING_SIZED: f"{body_part} inflated to building size",
        }
        
        return descriptions.get(level, f"inflated {body_part}")
    
    def describe_belly(self) -> str:
        """Specific description for belly inflation (cumflation)."""
        level = self.inflation_level
        amt = self.total_fluid_ml
        
        if level == InflationLevel.NONE:
            return ""
        elif level == InflationLevel.SLIGHT:
            return "belly slightly rounded with cum"
        elif level == InflationLevel.NOTICEABLE:
            return "belly visibly swollen with cum"
        elif level == InflationLevel.PRONOUNCED:
            return f"belly heavily distended with {format_measurement(amt, 'ml')} of cum, looking months pregnant"
        elif level == InflationLevel.HEAVY:
            return f"belly hugely bloated with cum, looking ready to burst with {format_measurement(amt, 'ml')}"
        elif level == InflationLevel.EXTREME:
            return f"belly grotesquely inflated, taut skin stretched around {format_measurement(amt, 'ml')} of cum"
        elif level == InflationLevel.MASSIVE:
            return f"belly inflated beyond reason, a massive cum-filled orb containing {format_measurement(amt, 'ml')}"
        elif level == InflationLevel.IMMOBILIZING:
            return f"completely immobilized by cum-bloated belly containing {format_measurement(amt, 'ml')}"
        elif level == InflationLevel.ROOM_FILLING:
            return f"belly inflated to monstrous proportions, filling the space with {format_measurement(amt, 'ml')} of cum"
        else:
            return f"belly expanded to godlike proportions with {format_measurement(amt, 'ml')} of cum"


# =============================================================================
# ENHANCED INTERNAL FLUID
# =============================================================================

@dataclass
class HyperInternalFluid:
    """
    Fluid inside a body cavity with support for extreme amounts.
    """
    # Identity
    fluid_id: str = ""
    fluid_type: str = "cum"  # cum, urine, milk, etc.
    
    # Location
    cavity: str = "womb"  # womb, vagina, ass, stomach, balls, breasts
    
    # Amount
    amount_ml: float = 0.0
    
    # Capacity (can be very high for hyper)
    capacity: Optional[ScalableCapacity] = None
    
    # Sources
    sources: Dict[str, float] = field(default_factory=dict)
    primary_source_name: str = ""
    
    # State
    is_leaking: bool = False
    leak_rate: float = 1.0  # ml per tick
    absorption_rate: float = 0.1  # ml per tick
    
    # Inflation tracking
    inflation: Optional[InflationState] = None
    
    # Time
    created_at: Optional[datetime] = None
    
    def __post_init__(self):
        if not self.fluid_id:
            self.fluid_id = f"{self.cavity}_{self.fluid_type}_{id(self)}"
        if not self.created_at:
            self.created_at = datetime.now()
        if self.capacity is None:
            # Default capacities by cavity type
            base_caps = {
                "womb": 500,
                "vagina": 200,
                "ass": 300,
                "stomach": 2000,
                "mouth": 100,
                "balls": 100,
                "breasts": 500,
            }
            self.capacity = ScalableCapacity(
                base_capacity=base_caps.get(self.cavity, 200),
                elasticity=10.0,  # Very stretchy for hyper
                max_stretch=1000.0,  # Can stretch to 1000x
            )
        if self.inflation is None:
            self.inflation = InflationState()
    
    @property
    def amount_word(self) -> str:
        return extreme_amount_to_word(self.amount_ml)
    
    def add(self, ml: float, source: str = "", source_name: str = "") -> Tuple[float, float]:
        """
        Add fluid. Returns (added, overflow).
        """
        added, overflow = self.capacity.add(ml)
        self.amount_ml = self.capacity.current_fill
        
        if source:
            if source in self.sources:
                self.sources[source] += added
            else:
                self.sources[source] = added
        
        if source_name:
            self.primary_source_name = source_name
        
        # Update inflation
        if self.inflation:
            self.inflation.add_fluid(added)
        
        # Start leaking if very full
        if self.capacity.fill_percent > 80:
            self.is_leaking = True
            self.leak_rate = max(1.0, self.amount_ml * 0.001)  # Leak faster when fuller
        
        return (added, overflow)
    
    def remove(self, ml: float) -> float:
        """Remove fluid. Returns amount removed."""
        removed = self.capacity.remove(ml)
        self.amount_ml = self.capacity.current_fill
        
        if self.inflation:
            self.inflation.remove_fluid(removed)
        
        # Stop leaking if mostly empty
        if self.capacity.fill_percent < 20:
            self.is_leaking = False
        
        return removed
    
    def tick(self) -> float:
        """
        Process one tick. Returns amount leaked/absorbed.
        """
        total_lost = 0.0
        
        # Absorption
        absorbed = min(self.absorption_rate, self.amount_ml * 0.01)
        if absorbed > 0:
            self.remove(absorbed)
            total_lost += absorbed
        
        # Leaking
        if self.is_leaking:
            leaked = min(self.leak_rate, self.amount_ml * 0.05)
            if leaked > 0:
                self.remove(leaked)
                total_lost += leaked
        
        return total_lost
    
    def get_display(self) -> str:
        """Get IC description."""
        if self.amount_ml < 1:
            return ""
        
        fullness = self.capacity.describe_fullness()
        
        if self.cavity in ("womb", "stomach"):
            # These cause visible belly inflation
            if self.inflation:
                belly_desc = self.inflation.describe_belly()
                if belly_desc:
                    return belly_desc
        
        desc = f"{self.cavity} {fullness} of {self.fluid_type}"
        
        if self.is_leaking:
            desc = f"{desc}, leaking"
        
        return desc
    
    def get_stats(self) -> Dict:
        """Get technical stats."""
        return {
            "fluid_type": self.fluid_type,
            "cavity": self.cavity,
            "amount_ml": self.amount_ml,
            "amount_formatted": format_measurement(self.amount_ml, "ml"),
            "amount_word": self.amount_word,
            "capacity_ml": self.capacity.capacity,
            "fill_percent": self.capacity.fill_percent,
            "stretch": self.capacity.stretch,
            "is_leaking": self.is_leaking,
            "inflation_level": self.inflation.inflation_level.value if self.inflation else "none",
            "sources": {k: format_measurement(v, "ml") for k, v in self.sources.items()},
        }


# =============================================================================
# CUM PRODUCTION
# =============================================================================

@dataclass
class CumProduction:
    """
    Tracks cum production for balls.
    """
    # Production rate (ml per tick at scale 1.0)
    base_rate: float = 0.1  # Normal: ~0.1ml per tick
    
    # Current production multiplier
    production_multiplier: float = 1.0
    
    # Ball scale (affects production and storage)
    ball_scale: float = 1.0
    
    # Storage
    storage: Optional[HyperInternalFluid] = None
    
    # Arousal affects production
    arousal_multiplier: float = 1.0
    
    def __post_init__(self):
        if self.storage is None:
            self.storage = HyperInternalFluid(
                cavity="balls",
                fluid_type="cum",
            )
            # Scale storage capacity with ball size
            self.storage.capacity.scale = self.ball_scale
    
    @property
    def current_rate(self) -> float:
        """Current production rate per tick."""
        # Production scales with ball volume (cube of scale)
        return self.base_rate * (self.ball_scale ** 3) * self.production_multiplier * self.arousal_multiplier
    
    @property
    def stored_ml(self) -> float:
        """Amount currently stored."""
        return self.storage.amount_ml
    
    @property
    def capacity_ml(self) -> float:
        """Total storage capacity."""
        return self.storage.capacity.capacity
    
    @property
    def fullness(self) -> float:
        """How full as percentage."""
        return self.storage.capacity.fill_percent
    
    def tick(self) -> float:
        """
        Process one tick of production.
        Returns amount produced.
        """
        produced = self.current_rate
        added, _ = self.storage.add(produced)
        return added
    
    def release(self, amount: Optional[float] = None) -> float:
        """
        Release cum (orgasm). Returns amount released.
        If amount is None, releases all stored cum.
        """
        if amount is None:
            amount = self.stored_ml
        
        return self.storage.remove(amount)
    
    def describe(self) -> str:
        """Get description of balls state."""
        fullness = self.fullness
        stored = self.stored_ml
        
        if stored < 10:
            return "balls hanging relaxed"
        elif fullness < 25:
            return "balls with some weight"
        elif fullness < 50:
            return "heavy balls, visibly full"
        elif fullness < 75:
            return f"swollen balls, churning with {format_measurement(stored, 'ml')}"
        elif fullness < 100:
            return f"taut, overfull balls containing {format_measurement(stored, 'ml')}"
        else:
            return f"massively bloated balls, straining with {format_measurement(stored, 'ml')} of cum"


# =============================================================================
# ORGASM WITH HYPER CUM
# =============================================================================

@dataclass
class HyperOrgasm:
    """
    Data for a hyper-scale orgasm event.
    """
    # Amount released
    amount_ml: float = 0.0
    
    # Duration (in ticks) - hyper orgasms last longer
    duration_ticks: int = 1
    
    # Intensity
    intensity: float = 1.0  # 0.0 - 10.0+
    
    # Source
    source_name: str = ""
    source_dbref: str = ""
    
    def describe_amount(self) -> str:
        """Describe the amount released."""
        return describe_extreme_amount(self.amount_ml, "cum")
    
    def describe(self) -> str:
        """Full orgasm description."""
        amt = self.amount_ml
        
        if amt < 10:
            release = "spurts"
        elif amt < 50:
            release = "shoots thick ropes of"
        elif amt < 200:
            release = "erupts with"
        elif amt < 1000:
            release = "explodes with a torrent of"
        elif amt < 5000:
            release = "unleashes a flood of"
        elif amt < 20000:
            release = "releases an impossible deluge of"
        elif amt < 100000:
            release = "erupts like a fire hose with"
        else:
            release = "releases a cataclysmic flood of"
        
        duration_desc = ""
        if self.duration_ticks > 5:
            seconds = self.duration_ticks * 5  # Assuming 5 sec ticks
            if seconds < 60:
                duration_desc = f" for {seconds} seconds"
            else:
                minutes = seconds / 60
                duration_desc = f" for {minutes:.1f} minutes"
        
        return f"{release} {format_measurement(amt, 'ml')} of cum{duration_desc}"


def calculate_orgasm_amount(production: CumProduction,
                           intensity: float = 1.0,
                           multiplier: float = 1.0) -> HyperOrgasm:
    """
    Calculate orgasm based on stored cum and intensity.
    """
    # Base: release all stored cum
    base_amount = production.stored_ml
    
    # Intensity affects how much is released (higher = more complete release)
    release_percent = min(1.0, 0.5 + (intensity * 0.1))
    
    # Apply multipliers
    amount = base_amount * release_percent * multiplier
    
    # Duration based on amount
    if amount < 100:
        duration = 1
    elif amount < 1000:
        duration = 2
    elif amount < 10000:
        duration = 5
    elif amount < 100000:
        duration = 10
    else:
        duration = 20
    
    return HyperOrgasm(
        amount_ml=amount,
        duration_ticks=duration,
        intensity=intensity,
    )


__all__ = [
    "EXTREME_AMOUNT_THRESHOLDS",
    "extreme_amount_to_word",
    "describe_extreme_amount",
    "InflationLevel",
    "InflationState",
    "HyperInternalFluid",
    "CumProduction",
    "HyperOrgasm",
    "calculate_orgasm_amount",
]

# Also export lactation submodule
from .lactation import (
    LactationState,
    BreastFullness,
    BreastMilkStorage,
    LactationTracker,
    MilkingSession,
)
