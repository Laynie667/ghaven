"""
Scale System
============

Handles extreme size variations from microscopic to building-sized.

Scale is a multiplier where 1.0 = normal human size.
- 0.001 = ant-sized (micro)
- 0.01 = mouse-sized
- 0.1 = cat-sized
- 1.0 = human-sized (baseline)
- 10.0 = elephant-sized
- 100.0 = whale-sized
- 1000.0 = building-sized (hyper)
- 10000.0 = skyscraper-sized (extreme hyper)

Parts can have their own scale multiplier relative to body.
A hyper cock on a normal body = body_scale * part_scale
"""

from dataclasses import dataclass, field
from typing import Dict, Optional, Tuple, List
from enum import Enum


# =============================================================================
# SCALE CATEGORIES
# =============================================================================

class ScaleCategory(Enum):
    """Named categories for scale ranges."""
    MICROSCOPIC = "microscopic"   # < 0.001 - invisible to naked eye
    TINY = "tiny"                 # 0.001 - 0.01 - insect-sized
    MINUSCULE = "minuscule"       # 0.01 - 0.05 - mouse-sized
    SMALL = "small"               # 0.05 - 0.5 - cat to child sized
    NORMAL = "normal"             # 0.5 - 2.0 - human range
    LARGE = "large"               # 2.0 - 5.0 - horse-sized
    HUGE = "huge"                 # 5.0 - 20.0 - elephant-sized
    MASSIVE = "massive"           # 20.0 - 100.0 - whale-sized
    COLOSSAL = "colossal"         # 100.0 - 500.0 - building-sized
    TITANIC = "titanic"           # 500.0 - 2000.0 - skyscraper-sized
    GODLIKE = "godlike"           # > 2000.0 - mountain-sized


def get_scale_category(scale: float) -> ScaleCategory:
    """Get the category for a scale value."""
    if scale < 0.001:
        return ScaleCategory.MICROSCOPIC
    elif scale < 0.01:
        return ScaleCategory.TINY
    elif scale < 0.05:
        return ScaleCategory.MINUSCULE
    elif scale < 0.5:
        return ScaleCategory.SMALL
    elif scale < 2.0:
        return ScaleCategory.NORMAL
    elif scale < 5.0:
        return ScaleCategory.LARGE
    elif scale < 20.0:
        return ScaleCategory.HUGE
    elif scale < 100.0:
        return ScaleCategory.MASSIVE
    elif scale < 500.0:
        return ScaleCategory.COLOSSAL
    elif scale < 2000.0:
        return ScaleCategory.TITANIC
    else:
        return ScaleCategory.GODLIKE


# =============================================================================
# SIZE DESCRIPTORS
# =============================================================================

# Length descriptors by scale
LENGTH_DESCRIPTORS = {
    ScaleCategory.MICROSCOPIC: ["microscopic", "invisible", "cell-sized"],
    ScaleCategory.TINY: ["ant-sized", "grain-of-rice-sized", "tiny"],
    ScaleCategory.MINUSCULE: ["mouse-sized", "finger-sized", "minuscule"],
    ScaleCategory.SMALL: ["cat-sized", "small", "compact"],
    ScaleCategory.NORMAL: ["average", "normal", "typical"],
    ScaleCategory.LARGE: ["large", "impressive", "horse-sized"],
    ScaleCategory.HUGE: ["huge", "enormous", "elephant-sized"],
    ScaleCategory.MASSIVE: ["massive", "whale-sized", "tremendous"],
    ScaleCategory.COLOSSAL: ["colossal", "building-sized", "towering"],
    ScaleCategory.TITANIC: ["titanic", "skyscraper-sized", "mountainous"],
    ScaleCategory.GODLIKE: ["godlike", "world-sized", "incomprehensible"],
}


def describe_scale(scale: float) -> str:
    """Get a descriptor for a scale value."""
    category = get_scale_category(scale)
    descriptors = LENGTH_DESCRIPTORS.get(category, [""])
    return descriptors[0]


def describe_relative_scale(scale1: float, scale2: float) -> str:
    """Describe how scale1 compares to scale2."""
    ratio = scale1 / scale2 if scale2 > 0 else float('inf')
    
    if ratio < 0.001:
        return "utterly dwarfed by"
    elif ratio < 0.01:
        return "microscopic compared to"
    elif ratio < 0.1:
        return "tiny compared to"
    elif ratio < 0.5:
        return "much smaller than"
    elif ratio < 0.8:
        return "smaller than"
    elif ratio < 1.2:
        return "about the same size as"
    elif ratio < 2.0:
        return "larger than"
    elif ratio < 10.0:
        return "much larger than"
    elif ratio < 100.0:
        return "enormous compared to"
    elif ratio < 1000.0:
        return "colossal compared to"
    else:
        return "incomprehensibly larger than"


# =============================================================================
# MEASUREMENTS
# =============================================================================

@dataclass
class ScaledMeasurement:
    """
    A measurement that scales with body/part size.
    
    base_value is the measurement at scale 1.0
    """
    base_value: float  # Value at scale 1.0
    unit: str = "inches"
    
    def at_scale(self, scale: float) -> float:
        """Get the actual value at a given scale."""
        return self.base_value * scale
    
    def describe(self, scale: float = 1.0) -> str:
        """Get human-readable description at scale."""
        value = self.at_scale(scale)
        return format_measurement(value, self.unit)


def format_measurement(value: float, unit: str = "inches") -> str:
    """
    Format a measurement value intelligently.
    Converts to appropriate units based on size.
    """
    if unit == "inches":
        if value < 0.01:
            return f"{value * 25400:.1f} microns"
        elif value < 1:
            return f"{value:.2f} inches"
        elif value < 12:
            return f"{value:.1f} inches"
        elif value < 36:
            feet = int(value // 12)
            inches = value % 12
            if inches > 0.5:
                return f"{feet}'{inches:.0f}\""
            return f"{feet} feet"
        elif value < 5280 * 12:  # Less than a mile
            feet = value / 12
            if feet < 100:
                return f"{feet:.1f} feet"
            else:
                return f"{feet:.0f} feet"
        else:
            miles = value / (5280 * 12)
            return f"{miles:.1f} miles"
    
    elif unit == "ml":
        if value < 1:
            return f"{value * 1000:.1f} microliters"
        elif value < 1000:
            return f"{value:.1f} ml"
        elif value < 1000000:
            return f"{value / 1000:.1f} liters"
        elif value < 1000000000:
            return f"{value / 1000000:.1f} cubic meters"
        else:
            return f"{value / 1000000000:.1f} thousand cubic meters"
    
    elif unit == "lbs":
        if value < 0.01:
            return f"{value * 453592:.1f} mg"
        elif value < 1:
            return f"{value * 16:.1f} oz"
        elif value < 2000:
            return f"{value:.1f} lbs"
        else:
            return f"{value / 2000:.1f} tons"
    
    return f"{value:.1f} {unit}"


# =============================================================================
# BODY PART SCALING
# =============================================================================

@dataclass
class ScalablePartSize:
    """
    Size data for a body part that can scale.
    """
    # Base measurements at scale 1.0 (normal human)
    base_length: float = 6.0  # inches
    base_girth: float = 5.0   # inches circumference
    base_diameter: float = 1.6  # inches
    base_volume: float = 0.0  # cubic inches (calculated if 0)
    
    # Current scale multiplier (1.0 = normal for this body)
    scale: float = 1.0
    
    # Min/max scale this part can reach
    min_scale: float = 0.001
    max_scale: float = 10000.0
    
    def __post_init__(self):
        if self.base_volume == 0:
            # Approximate as cylinder
            import math
            radius = self.base_diameter / 2
            self.base_volume = math.pi * radius * radius * self.base_length
    
    @property
    def length(self) -> float:
        """Current length."""
        return self.base_length * self.scale
    
    @property
    def girth(self) -> float:
        """Current girth (circumference)."""
        return self.base_girth * self.scale
    
    @property
    def diameter(self) -> float:
        """Current diameter."""
        return self.base_diameter * self.scale
    
    @property
    def volume(self) -> float:
        """Current volume (scales with cube of linear scale)."""
        return self.base_volume * (self.scale ** 3)
    
    def describe_length(self) -> str:
        """Get length description."""
        return format_measurement(self.length, "inches")
    
    def describe_girth(self) -> str:
        """Get girth description."""
        return format_measurement(self.girth, "inches")
    
    def grow(self, factor: float) -> float:
        """Grow by a factor. Returns new scale."""
        self.scale = min(self.max_scale, self.scale * factor)
        return self.scale
    
    def shrink(self, factor: float) -> float:
        """Shrink by a factor. Returns new scale."""
        self.scale = max(self.min_scale, self.scale / factor)
        return self.scale
    
    def set_scale(self, new_scale: float) -> float:
        """Set scale directly. Returns clamped scale."""
        self.scale = max(self.min_scale, min(self.max_scale, new_scale))
        return self.scale


# =============================================================================
# CAPACITY SCALING
# =============================================================================

@dataclass
class ScalableCapacity:
    """
    Capacity of an orifice/container that scales.
    
    Used for vaginas, asses, mouths, wombs, balls, etc.
    """
    # Base capacity at scale 1.0 (in cubic inches or ml)
    base_capacity: float = 100.0  # ml
    
    # How much is currently inside
    current_fill: float = 0.0
    
    # Stretch state (1.0 = unstretched, higher = stretched)
    stretch: float = 1.0
    max_stretch: float = 100.0  # Can stretch to 100x capacity
    
    # Scale of the body/part this belongs to
    scale: float = 1.0
    
    # Elasticity - how easily it stretches (higher = stretchier)
    elasticity: float = 1.0
    
    @property
    def capacity(self) -> float:
        """Current maximum capacity including stretch."""
        # Capacity scales with cube of body scale
        # Then multiplied by stretch
        return self.base_capacity * (self.scale ** 3) * self.stretch
    
    @property
    def fill_percent(self) -> float:
        """How full as a percentage."""
        if self.capacity <= 0:
            return 0.0
        return (self.current_fill / self.capacity) * 100
    
    @property
    def overfull(self) -> bool:
        """Is it over capacity?"""
        return self.current_fill > self.capacity
    
    def add(self, amount: float) -> Tuple[float, float]:
        """
        Add content. Returns (amount_added, overflow).
        With high elasticity, can exceed capacity by stretching.
        """
        space = self.capacity - self.current_fill
        
        if amount <= space:
            self.current_fill += amount
            return (amount, 0.0)
        
        # Need to stretch
        self.current_fill += amount
        needed_stretch = self.current_fill / (self.base_capacity * (self.scale ** 3))
        
        if needed_stretch <= self.max_stretch:
            # Can stretch to accommodate
            self.stretch = max(self.stretch, needed_stretch)
            return (amount, 0.0)
        else:
            # Over max stretch - overflow
            max_fill = self.base_capacity * (self.scale ** 3) * self.max_stretch
            overflow = self.current_fill - max_fill
            self.current_fill = max_fill
            self.stretch = self.max_stretch
            return (amount - overflow, overflow)
    
    def remove(self, amount: float) -> float:
        """Remove content. Returns amount actually removed."""
        removed = min(amount, self.current_fill)
        self.current_fill -= removed
        return removed
    
    def describe_fullness(self) -> str:
        """Get description of how full."""
        pct = self.fill_percent
        
        if pct < 1:
            return "empty"
        elif pct < 10:
            return "nearly empty"
        elif pct < 25:
            return "has some"
        elif pct < 50:
            return "half full"
        elif pct < 75:
            return "quite full"
        elif pct < 100:
            return "nearly full"
        elif pct < 150:
            return "full and bulging"
        elif pct < 300:
            return "stretched taut"
        elif pct < 500:
            return "grotesquely distended"
        elif pct < 1000:
            return "impossibly bloated"
        else:
            return "stretched beyond comprehension"
    
    def describe_capacity(self) -> str:
        """Get description of capacity."""
        cap = self.capacity
        return format_measurement(cap, "ml")


# =============================================================================
# HYPER DESCRIPTORS
# =============================================================================

def describe_hyper_cock(length_inches: float, girth_inches: float) -> str:
    """Generate vivid description of a hyper cock."""
    length_ft = length_inches / 12
    
    if length_inches < 12:
        size_word = "impressive"
    elif length_inches < 24:
        size_word = "massive"
    elif length_inches < 48:
        size_word = "enormous"
        comparison = "as long as an arm"
    elif length_inches < 96:
        size_word = "colossal"
        comparison = "as long as a person is tall"
    elif length_inches < 240:
        size_word = "titanic"
        comparison = f"stretching {length_ft:.0f} feet"
    elif length_inches < 600:
        size_word = "monstrous"
        comparison = f"a towering {length_ft:.0f} feet of cock"
    else:
        size_word = "godlike"
        comparison = f"an incomprehensible {length_ft:.0f} feet"
    
    if length_inches < 48:
        return f"{size_word} {format_measurement(length_inches, 'inches')} cock"
    else:
        return f"{size_word} cock, {comparison}"


def describe_hyper_breasts(volume_cc: float) -> str:
    """Generate description of hyper breasts."""
    # Cup size rough equivalents in cc
    # A = 150, B = 300, C = 450, D = 600, DD = 750...
    
    if volume_cc < 300:
        return "modest breasts"
    elif volume_cc < 600:
        return "full breasts"
    elif volume_cc < 1200:
        return "large breasts"
    elif volume_cc < 2500:
        return "huge breasts"
    elif volume_cc < 5000:
        return "massive breasts"
    elif volume_cc < 10000:
        return "enormous breasts, each bigger than a head"
    elif volume_cc < 50000:
        return "colossal breasts, each the size of a beach ball"
    elif volume_cc < 200000:
        return "titanic breasts, each bigger than a person"
    elif volume_cc < 1000000:
        return "impossible breasts, each the size of a car"
    else:
        liters = volume_cc / 1000
        return f"godlike breasts, each containing {liters:.0f} liters"


def describe_hyper_balls(volume_cc: float) -> str:
    """Generate description of hyper balls."""
    if volume_cc < 50:
        return "normal balls"
    elif volume_cc < 200:
        return "heavy balls"
    elif volume_cc < 500:
        return "large, churning balls"
    elif volume_cc < 2000:
        return "huge balls, each the size of a fist"
    elif volume_cc < 10000:
        return "massive balls, each the size of a melon"
    elif volume_cc < 50000:
        return "enormous balls, each bigger than a head"
    elif volume_cc < 200000:
        return "colossal balls, each the size of a beach ball"
    elif volume_cc < 1000000:
        return "titanic balls, each bigger than a person"
    else:
        liters = volume_cc / 1000
        return f"godlike balls containing {liters:.0f} liters of cum"


def describe_stretched_orifice(normal_diameter: float, 
                               current_diameter: float,
                               orifice_name: str = "pussy") -> str:
    """Describe how stretched an orifice is."""
    ratio = current_diameter / normal_diameter if normal_diameter > 0 else 1.0
    
    if ratio < 1.5:
        return f"snug {orifice_name}"
    elif ratio < 2.0:
        return f"stretched {orifice_name}"
    elif ratio < 3.0:
        return f"widely stretched {orifice_name}"
    elif ratio < 5.0:
        return f"gaping {orifice_name}"
    elif ratio < 10.0:
        return f"impossibly stretched {orifice_name}, gaping wide"
    elif ratio < 50.0:
        return f"grotesquely distended {orifice_name}"
    else:
        return f"{orifice_name} stretched beyond recognition"


# =============================================================================
# SIZE COMPARISON UTILITIES
# =============================================================================

def can_fit(inserter_diameter: float, 
            receiver_capacity: ScalableCapacity,
            force: bool = False) -> Tuple[bool, str]:
    """
    Check if something can fit inside something else.
    
    Returns (can_fit, description).
    """
    import math
    
    # Calculate volume of inserter (approximate as cylinder)
    # This is simplified - just checking diameter vs stretched capacity
    receiver_max_diameter = math.sqrt(receiver_capacity.capacity / math.pi) * 2
    
    ratio = inserter_diameter / receiver_max_diameter if receiver_max_diameter > 0 else float('inf')
    
    if ratio < 0.3:
        return (True, "fits easily")
    elif ratio < 0.6:
        return (True, "fits snugly")
    elif ratio < 0.9:
        return (True, "fits tightly")
    elif ratio < 1.0:
        return (True, "barely fits, stretching tight")
    elif ratio < 1.5 and receiver_capacity.elasticity > 1.0:
        return (True, "forces in with considerable stretching")
    elif ratio < 2.0 and receiver_capacity.elasticity > 2.0:
        return (True, "impossibly stretches to accommodate")
    elif force and receiver_capacity.elasticity > 3.0:
        return (True, "violently stretches beyond normal limits")
    else:
        return (False, "too large to fit")


__all__ = [
    "ScaleCategory",
    "get_scale_category",
    "describe_scale",
    "describe_relative_scale",
    "LENGTH_DESCRIPTORS",
    "ScaledMeasurement",
    "format_measurement",
    "ScalablePartSize",
    "ScalableCapacity",
    "describe_hyper_cock",
    "describe_hyper_breasts",
    "describe_hyper_balls",
    "describe_stretched_orifice",
    "can_fit",
]
