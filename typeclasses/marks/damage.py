"""
Damage Marks System
===================

Tracks physical damage marks on bodies:
- Bruises (from impact)
- Welts (from striking)
- Cuts (from sharp edges)
- Abrasions (scrapes)
- Bite marks
- Rope burns
- Handprints
"""

from dataclasses import dataclass, field
from typing import Optional, List
from enum import Enum
from datetime import datetime

from .base import Mark, MarkPersistence, SurfaceType


# =============================================================================
# DAMAGE TYPES
# =============================================================================

class DamageType(Enum):
    """Types of damage marks."""
    BRUISE = "bruise"
    WELT = "welt"
    CUT = "cut"
    SCRATCH = "scratch"
    ABRASION = "abrasion"
    BITE = "bite"
    HICKEY = "hickey"
    ROPE_BURN = "rope_burn"
    HANDPRINT = "handprint"
    SLAP_MARK = "slap_mark"
    PINCH = "pinch"
    FRICTION_BURN = "friction_burn"
    WHIP_MARK = "whip_mark"
    CANE_MARK = "cane_mark"
    PADDLE_MARK = "paddle_mark"
    BELT_MARK = "belt_mark"


class DamageSeverity(Enum):
    """How severe the damage is."""
    FAINT = "faint"       # Barely visible
    LIGHT = "light"       # Noticeable but minor
    MODERATE = "moderate" # Clearly visible
    SEVERE = "severe"     # Significant damage
    EXTREME = "extreme"   # Very serious


class DamageState(Enum):
    """Current state of the damage as it heals."""
    FRESH = "fresh"           # Just happened - bright/red
    DEVELOPING = "developing"  # Still forming (bruises darken)
    PEAK = "peak"             # At worst appearance
    HEALING = "healing"       # Starting to fade
    FADING = "fading"         # Almost gone
    SCARRING = "scarring"     # Leaving a scar


# =============================================================================
# DAMAGE MARK
# =============================================================================

@dataclass
class DamageMark(Mark):
    """
    A mark of physical damage on a body.
    """
    mark_type: str = "damage"
    
    # Damage type
    damage_type: DamageType = DamageType.BRUISE
    
    # Severity
    severity: DamageSeverity = DamageSeverity.LIGHT
    
    # State
    damage_state: DamageState = DamageState.FRESH
    
    # Appearance
    shape: str = ""  # "oval", "rectangular", "finger-shaped", "teeth-shaped"
    
    # Cause
    cause: str = ""  # What caused it ("slap", "paddle", "teeth", "rope")
    caused_by: str = ""  # Dbref of who caused it
    caused_by_name: str = ""  # Display name
    
    # Pain tracking
    is_painful: bool = True
    pain_level: int = 1  # 1-10 scale
    
    # Healing
    will_scar: bool = False
    heal_rate: float = 1.0  # Multiplier for healing speed
    
    def __post_init__(self):
        super().__post_init__()
        
        self.surface = SurfaceType.SKIN
        self.persistence = MarkPersistence.TEMPORARY
        
        # Set healing time based on severity and type
        base_fade = {
            DamageSeverity.FAINT: 20,
            DamageSeverity.LIGHT: 50,
            DamageSeverity.MODERATE: 100,
            DamageSeverity.SEVERE: 200,
            DamageSeverity.EXTREME: 400,
        }.get(self.severity, 50)
        
        # Some damage types heal slower
        type_multiplier = {
            DamageType.BRUISE: 1.5,  # Bruises take time
            DamageType.HICKEY: 1.2,
            DamageType.BITE: 1.3,
            DamageType.CUT: 2.0,  # Cuts heal slow
            DamageType.WHIP_MARK: 1.5,
        }.get(self.damage_type, 1.0)
        
        self.fade_ticks = int(base_fade * type_multiplier / self.heal_rate)
        
        # Set color based on type
        if not self.color:
            self.color = self._get_initial_color()
        
        # Set pain based on severity
        if self.pain_level == 1:
            self.pain_level = {
                DamageSeverity.FAINT: 1,
                DamageSeverity.LIGHT: 2,
                DamageSeverity.MODERATE: 4,
                DamageSeverity.SEVERE: 7,
                DamageSeverity.EXTREME: 9,
            }.get(self.severity, 2)
        
        # Extreme damage might scar
        if self.severity == DamageSeverity.EXTREME:
            self.will_scar = True
    
    def _get_initial_color(self) -> str:
        """Get initial color based on damage type."""
        colors = {
            DamageType.BRUISE: "red",
            DamageType.WELT: "red",
            DamageType.CUT: "red",
            DamageType.SCRATCH: "red",
            DamageType.HICKEY: "red",
            DamageType.BITE: "red",
            DamageType.HANDPRINT: "pink",
            DamageType.SLAP_MARK: "pink",
            DamageType.ROPE_BURN: "pink",
        }
        return colors.get(self.damage_type, "red")
    
    def _get_bruise_color(self, fade_pct: float) -> str:
        """Get bruise color based on healing stage."""
        if fade_pct < 0.1:
            return "red"
        elif fade_pct < 0.3:
            return "dark purple"
        elif fade_pct < 0.5:
            return "purple-blue"
        elif fade_pct < 0.7:
            return "greenish-yellow"
        elif fade_pct < 0.9:
            return "yellowish"
        else:
            return "faint yellow"
    
    def tick(self) -> bool:
        """Process healing."""
        fade_pct = self.get_fade_percent()
        
        # Update state based on healing
        if fade_pct < 0.1:
            self.damage_state = DamageState.FRESH
        elif fade_pct < 0.3:
            self.damage_state = DamageState.DEVELOPING
        elif fade_pct < 0.5:
            self.damage_state = DamageState.PEAK
        elif fade_pct < 0.8:
            self.damage_state = DamageState.HEALING
        else:
            self.damage_state = DamageState.FADING
        
        # Update color for bruises
        if self.damage_type == DamageType.BRUISE:
            self.color = self._get_bruise_color(fade_pct)
        
        # Pain decreases as it heals
        if fade_pct > 0.5:
            self.pain_level = max(1, self.pain_level - 1)
        if fade_pct > 0.8:
            self.is_painful = False
        
        # Check if should scar
        if self.will_scar and fade_pct > 0.95:
            self.damage_state = DamageState.SCARRING
            # Don't remove - will become a scar
            return False
        
        return super().tick()
    
    def get_display(self, verbose: bool = False) -> str:
        """Get display text for this damage."""
        severity_word = ""
        if self.severity in (DamageSeverity.SEVERE, DamageSeverity.EXTREME):
            severity_word = f"{self.severity.value} "
        elif self.severity == DamageSeverity.FAINT:
            severity_word = "faint "
        
        state_word = ""
        if self.damage_state == DamageState.FRESH:
            state_word = "fresh "
        elif self.damage_state == DamageState.HEALING:
            state_word = "healing "
        elif self.damage_state == DamageState.FADING:
            state_word = "fading "
        
        # Color for bruises
        color_word = ""
        if self.damage_type == DamageType.BRUISE and self.color:
            color_word = f"{self.color} "
        
        # Shape
        shape_word = ""
        if self.shape:
            shape_word = f"{self.shape} "
        
        damage_name = self.damage_type.value.replace("_", " ")
        
        base = f"{state_word}{severity_word}{color_word}{shape_word}{damage_name}"
        
        if verbose and self.caused_by_name:
            base = f"{base} (from {self.caused_by_name})"
        
        return base
    
    def to_dict(self):
        data = super().to_dict()
        data.update({
            "damage_type": self.damage_type.value,
            "severity": self.severity.value,
            "damage_state": self.damage_state.value,
            "shape": self.shape,
            "cause": self.cause,
            "caused_by": self.caused_by,
            "caused_by_name": self.caused_by_name,
            "is_painful": self.is_painful,
            "pain_level": self.pain_level,
            "will_scar": self.will_scar,
            "heal_rate": self.heal_rate,
        })
        return data
    
    @classmethod
    def from_dict(cls, data):
        data = data.copy()
        # Handle enums - check if already converted
        if "damage_type" in data and isinstance(data["damage_type"], str):
            data["damage_type"] = DamageType(data["damage_type"])
        if "severity" in data and isinstance(data["severity"], str):
            data["severity"] = DamageSeverity(data["severity"])
        if "damage_state" in data and isinstance(data["damage_state"], str):
            data["damage_state"] = DamageState(data["damage_state"])
        if "surface" in data and isinstance(data["surface"], str):
            data["surface"] = SurfaceType(data["surface"])
        if "persistence" in data and isinstance(data["persistence"], str):
            data["persistence"] = MarkPersistence(data["persistence"])
        if data.get("created_at") and isinstance(data["created_at"], str):
            data["created_at"] = datetime.fromisoformat(data["created_at"])
        # Remove class marker
        data.pop("mark_class", None)
        # Filter to valid fields for this class
        valid = {k: v for k, v in data.items() if k in cls.__dataclass_fields__}
        return cls(**valid)


# =============================================================================
# SPECIALIZED DAMAGE MARKS
# =============================================================================

@dataclass
class BruiseMark(DamageMark):
    """A bruise from blunt impact."""
    damage_type: DamageType = DamageType.BRUISE
    
    # Bruise-specific
    deep: bool = False  # Deep tissue bruise (longer healing)
    
    def __post_init__(self):
        super().__post_init__()
        if self.deep:
            self.fade_ticks = int(self.fade_ticks * 1.5)
            self.will_scar = False  # Bruises don't scar


@dataclass
class WeltMark(DamageMark):
    """A raised welt from striking."""
    damage_type: DamageType = DamageType.WELT
    
    # Welt-specific
    raised: bool = True
    
    def __post_init__(self):
        super().__post_init__()
        self.shape = self.shape or "linear"


@dataclass
class BiteMark(DamageMark):
    """A bite mark showing teeth impressions."""
    damage_type: DamageType = DamageType.BITE
    
    # Bite-specific
    broke_skin: bool = False
    teeth_visible: bool = True
    
    def __post_init__(self):
        super().__post_init__()
        self.shape = "teeth-shaped"
        if self.broke_skin:
            self.severity = DamageSeverity.MODERATE
            self.will_scar = True


@dataclass
class HandprintMark(DamageMark):
    """A handprint from slapping."""
    damage_type: DamageType = DamageType.HANDPRINT
    
    # Handprint-specific
    fingers_visible: bool = True
    hand_size: str = "medium"  # small, medium, large
    
    def __post_init__(self):
        super().__post_init__()
        self.shape = "hand-shaped"
        self.fade_ticks = 30  # Handprints fade quickly


@dataclass
class RopeMarkMark(DamageMark):
    """Marks from rope bondage."""
    damage_type: DamageType = DamageType.ROPE_BURN
    
    # Rope-specific
    pattern: str = ""  # "wrap", "crosshatch", "single line"
    rope_type: str = ""  # "hemp", "nylon", "silk"
    
    def __post_init__(self):
        super().__post_init__()
        self.shape = self.pattern or "rope pattern"


# =============================================================================
# HELPER FUNCTIONS
# =============================================================================

def create_slap_mark(location: str, 
                     severity: DamageSeverity = DamageSeverity.LIGHT,
                     caused_by: str = "",
                     caused_by_name: str = "") -> HandprintMark:
    """Create a slap mark."""
    return HandprintMark(
        location=location,
        severity=severity,
        cause="slap",
        caused_by=caused_by,
        caused_by_name=caused_by_name,
    )


def create_spanking_marks(location: str = "ass",
                          count: int = 1,
                          severity: DamageSeverity = DamageSeverity.LIGHT,
                          caused_by: str = "",
                          caused_by_name: str = "") -> List[DamageMark]:
    """Create marks from spanking."""
    marks = []
    positions = ["left cheek", "right cheek", "center"]
    
    for i in range(count):
        pos = positions[i % len(positions)]
        marks.append(HandprintMark(
            location=location,
            position=pos,
            severity=severity,
            cause="spanking",
            caused_by=caused_by,
            caused_by_name=caused_by_name,
        ))
    
    return marks


def create_whip_marks(location: str,
                      count: int = 1,
                      severity: DamageSeverity = DamageSeverity.MODERATE,
                      caused_by: str = "",
                      caused_by_name: str = "") -> List[WeltMark]:
    """Create marks from whipping."""
    marks = []
    
    for i in range(count):
        marks.append(WeltMark(
            location=location,
            severity=severity,
            cause="whip",
            damage_type=DamageType.WHIP_MARK,
            caused_by=caused_by,
            caused_by_name=caused_by_name,
        ))
    
    return marks


def describe_damage_state(marks: List[DamageMark], location: str) -> str:
    """Get a natural description of damage on a location."""
    if not marks:
        return ""
    
    # Count by type
    by_type = {}
    for mark in marks:
        t = mark.damage_type.value
        if t not in by_type:
            by_type[t] = []
        by_type[t].append(mark)
    
    parts = []
    for damage_type, type_marks in by_type.items():
        count = len(type_marks)
        
        # Get worst severity
        severities = [m.severity for m in type_marks]
        worst = max(severities, key=lambda s: list(DamageSeverity).index(s))
        
        if count == 1:
            parts.append(f"a {type_marks[0].get_display()}")
        elif count < 4:
            parts.append(f"several {damage_type.replace('_', ' ')}s")
        else:
            parts.append(f"many {damage_type.replace('_', ' ')}s")
    
    if len(parts) == 1:
        return parts[0]
    elif len(parts) == 2:
        return f"{parts[0]} and {parts[1]}"
    else:
        return ", ".join(parts[:-1]) + f", and {parts[-1]}"
