"""
Fluid Tracking System
=====================

Tracks fluids on surfaces and inside cavities.
Supports amount tracking, drying/fading, and accumulation.

Fluids can be:
- External: On surfaces, visible
- Internal: Inside cavities (womb, stomach, etc.)
"""

from dataclasses import dataclass, field
from typing import Optional, Dict, List
from enum import Enum
from datetime import datetime

from .base import Mark, MarkPersistence, SurfaceType


# =============================================================================
# FLUID TYPES
# =============================================================================

class FluidType(Enum):
    """Types of fluids that can be tracked."""
    # Sexual fluids
    CUM = "cum"
    PRECUM = "precum"
    FEMCUM = "femcum"
    SLICK = "slick"  # Vaginal wetness
    
    # Other bodily fluids
    URINE = "urine"
    SALIVA = "saliva"
    SWEAT = "sweat"
    TEARS = "tears"
    BLOOD = "blood"
    MILK = "milk"
    
    # External substances
    WATER = "water"
    OIL = "oil"
    LUBE = "lube"
    WAX = "wax"
    MUD = "mud"
    SOAP = "soap"


class FluidState(Enum):
    """Current state of the fluid."""
    FRESH = "fresh"  # Just deposited
    WET = "wet"  # Still wet
    DRYING = "drying"  # Starting to dry
    DRIED = "dried"  # Dried but visible
    CRUSTED = "crusted"  # Old, crusty
    ABSORBED = "absorbed"  # Soaked into surface


# =============================================================================
# AMOUNT SYSTEM
# =============================================================================

# Amount thresholds in ml
AMOUNT_THRESHOLDS = {
    "trace": 1,       # < 1ml - barely noticeable
    "drops": 5,       # 1-5ml - a few drops
    "small": 15,      # 5-15ml - small amount
    "moderate": 30,   # 15-30ml - noticeable amount
    "large": 60,      # 30-60ml - significant amount
    "heavy": 100,     # 60-100ml - heavy coating
    "soaked": 200,    # 100-200ml - thoroughly soaked
    "dripping": 300,  # 200-300ml - actively dripping
    "flooded": 500,   # 300-500ml - excessive
    "overflowing": 1000,  # 500ml+ - way too much
}


def amount_to_word(ml: float) -> str:
    """Convert ml amount to descriptive word."""
    for word, threshold in AMOUNT_THRESHOLDS.items():
        if ml <= threshold:
            return word
    return "overflowing"


def word_to_amount(word: str) -> float:
    """Convert word to approximate ml (midpoint of range)."""
    thresholds = list(AMOUNT_THRESHOLDS.items())
    for i, (w, threshold) in enumerate(thresholds):
        if w == word:
            if i == 0:
                return threshold / 2
            prev_threshold = thresholds[i-1][1]
            return (prev_threshold + threshold) / 2
    return 1000  # Default to large amount


# =============================================================================
# FLUID MARK
# =============================================================================

@dataclass
class FluidMark(Mark):
    """
    Fluid present on a surface.
    """
    mark_type: str = "fluid"
    
    # Fluid type
    fluid_type: FluidType = FluidType.CUM
    
    # Amount (in ml for precision)
    amount_ml: float = 10.0
    
    # State
    state: FluidState = FluidState.FRESH
    
    # Time tracking
    deposited_at: Optional[datetime] = None
    
    # Source tracking
    source_character: str = ""  # Dbref of who it came from
    source_name: str = ""  # Display name
    
    def __post_init__(self):
        super().__post_init__()
        
        self.persistence = MarkPersistence.TEMPORARY
        
        if not self.deposited_at:
            self.deposited_at = datetime.now()
        
        # Set fade time based on fluid type and amount
        # More fluid = longer to dry
        base_fade = {
            FluidType.CUM: 50,
            FluidType.PRECUM: 30,
            FluidType.FEMCUM: 30,
            FluidType.SLICK: 20,
            FluidType.URINE: 40,
            FluidType.SALIVA: 20,
            FluidType.SWEAT: 30,
            FluidType.BLOOD: 100,
            FluidType.MILK: 40,
            FluidType.WATER: 20,
            FluidType.OIL: 200,
            FluidType.LUBE: 100,
        }.get(self.fluid_type, 30)
        
        # More fluid = longer fade
        amount_multiplier = 1 + (self.amount_ml / 50)
        self.fade_ticks = int(base_fade * amount_multiplier)
    
    @property
    def amount_word(self) -> str:
        """Get descriptive word for amount."""
        return amount_to_word(self.amount_ml)
    
    def add_fluid(self, ml: float, source: str = "", source_name: str = ""):
        """Add more of the same fluid."""
        self.amount_ml += ml
        self.state = FluidState.FRESH
        self.deposited_at = datetime.now()
        self.current_fade = 0  # Reset fade
        
        if source:
            self.source_character = source
        if source_name:
            self.source_name = source_name
    
    def remove_fluid(self, ml: float) -> float:
        """
        Remove fluid (absorbed, cleaned, etc.)
        Returns amount actually removed.
        """
        removed = min(ml, self.amount_ml)
        self.amount_ml -= removed
        return removed
    
    def tick(self) -> bool:
        """Process time. Returns True if should be removed."""
        # Update state based on fade progress
        fade_pct = self.get_fade_percent()
        
        if fade_pct < 0.2:
            self.state = FluidState.FRESH
        elif fade_pct < 0.4:
            self.state = FluidState.WET
        elif fade_pct < 0.6:
            self.state = FluidState.DRYING
        elif fade_pct < 0.8:
            self.state = FluidState.DRIED
        else:
            self.state = FluidState.CRUSTED
        
        # Call parent tick
        if super().tick():
            return True
        
        # Remove if amount is negligible
        return self.amount_ml < 0.1
    
    def get_display(self, verbose: bool = False) -> str:
        """Get display text for this fluid."""
        state_words = {
            FluidState.FRESH: "fresh",
            FluidState.WET: "wet",
            FluidState.DRYING: "drying",
            FluidState.DRIED: "dried",
            FluidState.CRUSTED: "crusted",
        }
        
        state_word = state_words.get(self.state, "")
        amount = self.amount_word
        fluid = self.fluid_type.value
        
        # Build description
        if amount in ("trace", "drops"):
            desc = f"{state_word} {fluid}" if state_word else fluid
        else:
            desc = f"{amount} {state_word} {fluid}".strip()
        
        if verbose and self.source_name:
            desc = f"{desc} (from {self.source_name})"
        
        return desc
    
    def get_stats(self) -> Dict:
        """Get technical stats for the fluid."""
        return {
            "fluid_type": self.fluid_type.value,
            "amount_ml": round(self.amount_ml, 1),
            "amount_desc": self.amount_word,
            "state": self.state.value,
            "source": self.source_name or self.source_character or "unknown",
            "age_ticks": self.current_fade,
            "fade_percent": round(self.get_fade_percent() * 100, 1),
        }
    
    def to_dict(self):
        data = super().to_dict()
        data.update({
            "fluid_type": self.fluid_type.value,
            "amount_ml": self.amount_ml,
            "state": self.state.value,
            "deposited_at": self.deposited_at.isoformat() if self.deposited_at else None,
            "source_character": self.source_character,
            "source_name": self.source_name,
        })
        return data
    
    @classmethod
    def from_dict(cls, data):
        data = data.copy()
        data["fluid_type"] = FluidType(data.get("fluid_type", "cum"))
        data["state"] = FluidState(data.get("state", "fresh"))
        data["surface"] = SurfaceType(data.get("surface", "surface"))
        data["persistence"] = MarkPersistence(data.get("persistence", "temporary"))
        if data.get("deposited_at"):
            data["deposited_at"] = datetime.fromisoformat(data["deposited_at"])
        if data.get("created_at"):
            data["created_at"] = datetime.fromisoformat(data["created_at"])
        return cls(**{k: v for k, v in data.items() if k in cls.__dataclass_fields__})


# =============================================================================
# INTERNAL FLUID (in body cavities)
# =============================================================================

@dataclass
class InternalFluid(Mark):
    """
    Fluid inside a body cavity (womb, stomach, ass, etc.)
    """
    mark_type: str = "internal_fluid"
    
    # Fluid type
    fluid_type: FluidType = FluidType.CUM
    
    # Amount in ml
    amount_ml: float = 10.0
    
    # Cavity
    cavity: str = "vagina"  # womb, vagina, ass, stomach, mouth
    
    # Source
    source_character: str = ""
    source_name: str = ""
    
    # Mixed sources tracking
    sources: Dict[str, float] = field(default_factory=dict)  # source_id -> ml
    
    # Absorption/leaking
    is_leaking: bool = False
    leak_rate: float = 0.5  # ml per tick when leaking
    absorption_rate: float = 0.1  # ml per tick absorbed by body
    
    def __post_init__(self):
        super().__post_init__()
        
        self.surface = SurfaceType.INTERNAL
        self.visible = False  # Not visible from outside
        self.persistence = MarkPersistence.TEMPORARY
        
        # Track primary source
        if self.source_character and self.source_character not in self.sources:
            self.sources[self.source_character] = self.amount_ml
        
        # Set fade based on cavity
        # Cum in womb takes longer to come out than in vagina
        fade_times = {
            "womb": 500,
            "vagina": 100,
            "ass": 150,
            "stomach": 300,
            "mouth": 30,
        }
        self.fade_ticks = fade_times.get(self.cavity, 100)
    
    @property
    def amount_word(self) -> str:
        return amount_to_word(self.amount_ml)
    
    def add_fluid(self, ml: float, source: str = "", source_name: str = ""):
        """Add more fluid to this cavity."""
        self.amount_ml += ml
        self.current_fade = 0  # Reset fade
        
        if source:
            if source in self.sources:
                self.sources[source] += ml
            else:
                self.sources[source] = ml
            self.source_character = source
        if source_name:
            self.source_name = source_name
    
    def leak(self) -> float:
        """
        Process leaking. Returns amount leaked out.
        """
        if not self.is_leaking:
            return 0.0
        
        leaked = min(self.leak_rate, self.amount_ml)
        self.amount_ml -= leaked
        
        # Reduce from sources proportionally
        if leaked > 0 and self.sources:
            total = sum(self.sources.values())
            for src in self.sources:
                self.sources[src] -= (self.sources[src] / total) * leaked
        
        return leaked
    
    def absorb(self) -> float:
        """Process absorption. Returns amount absorbed."""
        absorbed = min(self.absorption_rate, self.amount_ml)
        self.amount_ml -= absorbed
        return absorbed
    
    def tick(self) -> bool:
        """Process time passing."""
        self.absorb()
        
        # Start leaking when full enough
        if self.amount_ml > 50:
            self.is_leaking = True
        elif self.amount_ml < 10:
            self.is_leaking = False
        
        if self.is_leaking:
            self.leak()
        
        # Remove if empty
        return self.amount_ml < 0.1
    
    def get_fullness(self) -> str:
        """Get description of how full the cavity is."""
        if self.amount_ml < 5:
            return "empty"
        elif self.amount_ml < 20:
            return "has a little"
        elif self.amount_ml < 50:
            return "partially filled"
        elif self.amount_ml < 100:
            return "quite full"
        elif self.amount_ml < 200:
            return "very full"
        elif self.amount_ml < 400:
            return "stuffed"
        else:
            return "overflowing"
    
    def get_display(self, verbose: bool = False) -> str:
        """Get IC description."""
        fullness = self.get_fullness()
        fluid = self.fluid_type.value
        
        if fullness == "empty":
            return ""
        
        if self.cavity == "womb":
            desc = f"womb is {fullness} of {fluid}"
        elif self.cavity == "stomach":
            desc = f"belly is {fullness} of {fluid}"
        else:
            desc = f"{self.cavity} is {fullness} of {fluid}"
        
        if self.is_leaking:
            desc = f"{desc}, leaking"
        
        return desc
    
    def get_stats(self) -> Dict:
        """Get technical stats."""
        return {
            "fluid_type": self.fluid_type.value,
            "cavity": self.cavity,
            "amount_ml": round(self.amount_ml, 1),
            "fullness": self.get_fullness(),
            "is_leaking": self.is_leaking,
            "sources": {k: round(v, 1) for k, v in self.sources.items()},
            "fade_percent": round(self.get_fade_percent() * 100, 1),
        }
    
    def to_dict(self):
        data = super().to_dict()
        data.update({
            "fluid_type": self.fluid_type.value,
            "amount_ml": self.amount_ml,
            "cavity": self.cavity,
            "source_character": self.source_character,
            "source_name": self.source_name,
            "sources": self.sources,
            "is_leaking": self.is_leaking,
            "leak_rate": self.leak_rate,
            "absorption_rate": self.absorption_rate,
        })
        return data
    
    @classmethod
    def from_dict(cls, data):
        data = data.copy()
        # Handle enums
        if "fluid_type" in data and isinstance(data["fluid_type"], str):
            data["fluid_type"] = FluidType(data["fluid_type"])
        if "surface" in data and isinstance(data["surface"], str):
            data["surface"] = SurfaceType(data["surface"])
        if "persistence" in data and isinstance(data["persistence"], str):
            data["persistence"] = MarkPersistence(data["persistence"])
        # Handle datetime
        if data.get("created_at") and isinstance(data["created_at"], str):
            from datetime import datetime
            data["created_at"] = datetime.fromisoformat(data["created_at"])
        # Remove class marker
        data.pop("mark_class", None)
        # Filter to valid fields
        valid = {k: v for k, v in data.items() if k in cls.__dataclass_fields__}
        return cls(**valid)


# =============================================================================
# HELPER FUNCTIONS
# =============================================================================

def describe_fluid_amount(ml: float, fluid_type: FluidType) -> str:
    """Get a natural description of a fluid amount."""
    word = amount_to_word(ml)
    
    fluid_name = fluid_type.value
    
    descriptions = {
        "trace": f"a trace of {fluid_name}",
        "drops": f"a few drops of {fluid_name}",
        "small": f"a small amount of {fluid_name}",
        "moderate": f"a noticeable amount of {fluid_name}",
        "large": f"a large amount of {fluid_name}",
        "heavy": f"a heavy coating of {fluid_name}",
        "soaked": f"thoroughly soaked in {fluid_name}",
        "dripping": f"dripping with {fluid_name}",
        "flooded": f"flooded with {fluid_name}",
        "overflowing": f"overflowing with {fluid_name}",
    }
    
    return descriptions.get(word, f"{word} {fluid_name}")


def describe_internal_amount(ml: float, cavity: str, fluid_type: FluidType) -> str:
    """Describe internal fluid amount."""
    fluid = fluid_type.value
    
    if ml < 5:
        return ""
    elif ml < 20:
        return f"a little {fluid} in {cavity}"
    elif ml < 50:
        return f"some {fluid} in {cavity}"
    elif ml < 100:
        return f"{cavity} noticeably full of {fluid}"
    elif ml < 200:
        return f"{cavity} very full of {fluid}"
    elif ml < 400:
        return f"{cavity} stuffed with {fluid}"
    else:
        return f"{cavity} overflowing with {fluid}"
