"""
Lactation System
================

Handles milk production, breast fullness, milking, and engorgement.
Supports hyper lactation with extreme volumes.
"""

from dataclasses import dataclass, field
from typing import Optional, Dict, List, Tuple
from enum import Enum
from datetime import datetime

from ..scale import format_measurement, ScalableCapacity
from . import InflationState, HyperInternalFluid


# =============================================================================
# LACTATION STATE
# =============================================================================

class LactationState(Enum):
    """Current lactation state."""
    DRY = "dry"                    # Not producing
    MINIMAL = "minimal"            # Producing very little
    LIGHT = "light"                # Light production
    MODERATE = "moderate"          # Normal lactating
    HEAVY = "heavy"                # Heavy production
    HYPER = "hyper"                # Extreme production
    OVERPRODUCING = "overproducing"  # Dangerous levels


class BreastFullness(Enum):
    """How full the breasts are."""
    EMPTY = "empty"
    SOFT = "soft"
    COMFORTABLE = "comfortable"
    FULL = "full"
    HEAVY = "heavy"
    ENGORGED = "engorged"
    PAINFULLY_FULL = "painfully_full"
    LEAKING = "leaking"
    SPRAYING = "spraying"
    OVERFLOWING = "overflowing"


# =============================================================================
# BREAST STORAGE
# =============================================================================

@dataclass
class BreastMilkStorage(HyperInternalFluid):
    """
    Milk storage in breasts.
    Extends HyperInternalFluid with breast-specific features.
    """
    cavity: str = "breasts"
    fluid_type: str = "milk"
    
    # Which breast (or "both" for combined)
    breast: str = "both"  # "left", "right", "both"
    
    # Engorgement
    is_engorged: bool = False
    engorgement_pain: float = 0.0  # 0-10 scale
    
    # Leaking/spraying state
    is_spraying: bool = False
    spray_triggers: List[str] = field(default_factory=list)  # What triggers spraying
    
    # Nipple state
    nipple_sensitivity: float = 1.0
    
    def __post_init__(self):
        super().__post_init__()
        
        # Default spray triggers
        if not self.spray_triggers:
            self.spray_triggers = ["arousal", "nursing", "stimulation", "full"]
    
    @property
    def fullness_state(self) -> BreastFullness:
        """Get current fullness state."""
        pct = self.capacity.fill_percent
        
        if pct < 5:
            return BreastFullness.EMPTY
        elif pct < 20:
            return BreastFullness.SOFT
        elif pct < 40:
            return BreastFullness.COMFORTABLE
        elif pct < 60:
            return BreastFullness.FULL
        elif pct < 80:
            return BreastFullness.HEAVY
        elif pct < 95:
            self.is_engorged = True
            return BreastFullness.ENGORGED
        elif pct < 110:
            self.is_engorged = True
            return BreastFullness.PAINFULLY_FULL
        elif pct < 150:
            self.is_leaking = True
            return BreastFullness.LEAKING
        elif pct < 200:
            self.is_spraying = True
            return BreastFullness.SPRAYING
        else:
            self.is_spraying = True
            return BreastFullness.OVERFLOWING
    
    def update_engorgement(self):
        """Update engorgement state based on fullness."""
        pct = self.capacity.fill_percent
        
        if pct < 80:
            self.is_engorged = False
            self.engorgement_pain = 0.0
        elif pct < 100:
            self.is_engorged = True
            self.engorgement_pain = (pct - 80) / 20 * 3  # 0-3 pain
        elif pct < 150:
            self.is_engorged = True
            self.engorgement_pain = 3 + ((pct - 100) / 50 * 4)  # 3-7 pain
        else:
            self.is_engorged = True
            self.engorgement_pain = min(10, 7 + ((pct - 150) / 50 * 3))  # 7-10 pain
    
    def describe(self) -> str:
        """Get description of breast state."""
        fullness = self.fullness_state
        stored = self.amount_ml
        
        breast_word = f"{self.breast} breast" if self.breast != "both" else "breasts"
        
        descriptions = {
            BreastFullness.EMPTY: f"soft, empty {breast_word}",
            BreastFullness.SOFT: f"soft {breast_word} with a little milk",
            BreastFullness.COMFORTABLE: f"comfortably full {breast_word}",
            BreastFullness.FULL: f"full, heavy {breast_word}",
            BreastFullness.HEAVY: f"heavy, swollen {breast_word} full of milk",
            BreastFullness.ENGORGED: f"engorged {breast_word}, tight with {format_measurement(stored, 'ml')} of milk",
            BreastFullness.PAINFULLY_FULL: f"painfully engorged {breast_word}, desperate for relief",
            BreastFullness.LEAKING: f"overfull {breast_word}, milk leaking from nipples",
            BreastFullness.SPRAYING: f"massively overfull {breast_word}, spraying milk",
            BreastFullness.OVERFLOWING: f"impossibly full {breast_word} with {format_measurement(stored, 'ml')}, constantly spraying",
        }
        
        return descriptions.get(fullness, f"full {breast_word}")


# =============================================================================
# LACTATION TRACKER
# =============================================================================

@dataclass
class LactationTracker:
    """
    Tracks lactation state for a character.
    """
    # Current state
    state: LactationState = LactationState.DRY
    
    # Production rate (ml per tick at scale 1.0)
    base_production_rate: float = 0.0  # 0 = not lactating
    
    # Production multipliers
    production_multiplier: float = 1.0
    arousal_multiplier: float = 1.0
    stimulation_multiplier: float = 1.0
    
    # Body/breast scale
    breast_scale: float = 1.0
    
    # Storage
    left_breast: Optional[BreastMilkStorage] = None
    right_breast: Optional[BreastMilkStorage] = None
    
    # Production state
    last_milked: Optional[datetime] = None
    time_since_milking: int = 0  # ticks
    
    # Milk properties
    milk_richness: float = 1.0  # Quality/richness of milk
    milk_flavor: str = "sweet"  # sweet, rich, creamy, etc.
    
    # Special properties
    is_magical: bool = False  # Magical milk with special properties
    magical_effects: List[str] = field(default_factory=list)
    
    def __post_init__(self):
        if self.left_breast is None:
            self.left_breast = BreastMilkStorage(breast="left")
        if self.right_breast is None:
            self.right_breast = BreastMilkStorage(breast="right")
        
        # Scale capacity with breast size
        self.left_breast.capacity.scale = self.breast_scale
        self.right_breast.capacity.scale = self.breast_scale
    
    @property
    def current_production_rate(self) -> float:
        """Current milk production rate per tick."""
        if self.base_production_rate <= 0:
            return 0.0
        
        # Base rate scaled by breast volume
        rate = self.base_production_rate * (self.breast_scale ** 3)
        
        # Apply multipliers
        rate *= self.production_multiplier
        rate *= self.arousal_multiplier
        rate *= self.stimulation_multiplier
        
        # Engorgement reduces production
        if self.left_breast.is_engorged or self.right_breast.is_engorged:
            rate *= 0.5
        
        return rate
    
    @property
    def total_stored(self) -> float:
        """Total milk stored in both breasts."""
        return self.left_breast.amount_ml + self.right_breast.amount_ml
    
    @property
    def total_capacity(self) -> float:
        """Total storage capacity."""
        return self.left_breast.capacity.capacity + self.right_breast.capacity.capacity
    
    @property
    def average_fullness(self) -> float:
        """Average fullness percentage."""
        return (self.left_breast.capacity.fill_percent + 
                self.right_breast.capacity.fill_percent) / 2
    
    def start_lactation(self, production_rate: float = 0.5):
        """Start milk production."""
        self.base_production_rate = production_rate
        self.state = self._calculate_state()
    
    def stop_lactation(self):
        """Stop milk production (will gradually dry up)."""
        self.base_production_rate = 0.0
        self.state = LactationState.DRY
    
    def _calculate_state(self) -> LactationState:
        """Calculate current lactation state from production rate."""
        # Calculate rate without checking current state (to avoid circular dependency)
        if self.base_production_rate <= 0:
            return LactationState.DRY
        
        rate = self.base_production_rate * (self.breast_scale ** 3)
        rate *= self.production_multiplier
        rate *= self.arousal_multiplier
        rate *= self.stimulation_multiplier
        
        if rate <= 0:
            return LactationState.DRY
        elif rate < 0.1:
            return LactationState.MINIMAL
        elif rate < 0.5:
            return LactationState.LIGHT
        elif rate < 2.0:
            return LactationState.MODERATE
        elif rate < 10.0:
            return LactationState.HEAVY
        elif rate < 100.0:
            return LactationState.HYPER
        else:
            return LactationState.OVERPRODUCING
    
    def tick(self) -> Dict[str, float]:
        """
        Process one tick of lactation.
        Returns dict of produced/leaked amounts.
        """
        result = {
            "produced": 0.0,
            "leaked_left": 0.0,
            "leaked_right": 0.0,
        }
        
        if self.state == LactationState.DRY:
            return result
        
        self.time_since_milking += 1
        
        # Produce milk
        rate = self.current_production_rate
        per_breast = rate / 2
        
        # Add to each breast
        added_left, _ = self.left_breast.add(per_breast)
        added_right, _ = self.right_breast.add(per_breast)
        result["produced"] = added_left + added_right
        
        # Check for leaking
        if self.left_breast.is_leaking:
            result["leaked_left"] = self.left_breast.tick()
        if self.right_breast.is_leaking:
            result["leaked_right"] = self.right_breast.tick()
        
        # Update engorgement
        self.left_breast.update_engorgement()
        self.right_breast.update_engorgement()
        
        # Update state
        self.state = self._calculate_state()
        
        return result
    
    def milk(self, breast: str = "both", 
             amount: Optional[float] = None,
             method: str = "manual") -> Dict[str, float]:
        """
        Milk the breasts.
        
        Args:
            breast: "left", "right", or "both"
            amount: Specific amount to extract, or None for all available
            method: "manual", "pump", "nursing", "magic"
        
        Returns dict with amounts extracted.
        """
        result = {
            "left": 0.0,
            "right": 0.0,
            "total": 0.0,
            "method": method,
        }
        
        # Efficiency by method
        efficiency = {
            "manual": 0.7,
            "pump": 0.9,
            "nursing": 0.95,
            "magic": 1.0,
        }.get(method, 0.7)
        
        if breast in ("left", "both"):
            available = self.left_breast.amount_ml * efficiency
            to_extract = amount / 2 if amount else available
            extracted = self.left_breast.remove(min(to_extract, available))
            result["left"] = extracted
        
        if breast in ("right", "both"):
            available = self.right_breast.amount_ml * efficiency
            to_extract = amount / 2 if amount else available
            extracted = self.right_breast.remove(min(to_extract, available))
            result["right"] = extracted
        
        result["total"] = result["left"] + result["right"]
        
        # Update last milked time
        self.last_milked = datetime.now()
        self.time_since_milking = 0
        
        # Reduce engorgement
        self.left_breast.update_engorgement()
        self.right_breast.update_engorgement()
        
        return result
    
    def stimulate(self, intensity: float = 1.0):
        """
        Stimulate breasts (increases production temporarily).
        """
        self.stimulation_multiplier = 1.0 + (intensity * 0.5)
        
        # May trigger spraying if full enough
        if self.average_fullness > 80:
            if intensity > 0.5:
                self.left_breast.is_spraying = True
                self.right_breast.is_spraying = True
    
    def describe(self) -> str:
        """Get overall lactation description."""
        if self.state == LactationState.DRY:
            return "not lactating"
        
        stored = self.total_stored
        rate = self.current_production_rate
        
        state_desc = {
            LactationState.MINIMAL: "producing a little milk",
            LactationState.LIGHT: "lightly lactating",
            LactationState.MODERATE: "lactating steadily",
            LactationState.HEAVY: "heavily lactating",
            LactationState.HYPER: "hyper-lactating",
            LactationState.OVERPRODUCING: "overproducing milk at an alarming rate",
        }.get(self.state, "lactating")
        
        fullness_desc = ""
        if self.average_fullness > 80:
            fullness_desc = f", breasts engorged with {format_measurement(stored, 'ml')}"
        elif self.average_fullness > 50:
            fullness_desc = f", breasts heavy with {format_measurement(stored, 'ml')}"
        
        return f"{state_desc}{fullness_desc}"
    
    def describe_breasts(self) -> str:
        """Get description of breast state."""
        left_desc = self.left_breast.describe()
        right_desc = self.right_breast.describe()
        
        if left_desc == right_desc:
            return left_desc.replace("left breast", "breasts")
        else:
            return f"Left: {left_desc}. Right: {right_desc}"
    
    def get_stats(self) -> Dict:
        """Get technical stats."""
        return {
            "state": self.state.value,
            "production_rate_per_tick": self.current_production_rate,
            "total_stored_ml": self.total_stored,
            "total_capacity_ml": self.total_capacity,
            "average_fullness_pct": self.average_fullness,
            "left_breast": {
                "stored_ml": self.left_breast.amount_ml,
                "fullness": self.left_breast.fullness_state.value,
                "engorged": self.left_breast.is_engorged,
                "leaking": self.left_breast.is_leaking,
                "spraying": self.left_breast.is_spraying,
            },
            "right_breast": {
                "stored_ml": self.right_breast.amount_ml,
                "fullness": self.right_breast.fullness_state.value,
                "engorged": self.right_breast.is_engorged,
                "leaking": self.right_breast.is_leaking,
                "spraying": self.right_breast.is_spraying,
            },
            "time_since_milking": self.time_since_milking,
        }


# =============================================================================
# MILKING SESSION
# =============================================================================

@dataclass
class MilkingSession:
    """
    Tracks an active milking session.
    """
    # Who is being milked
    target_dbref: str = ""
    target_name: str = ""
    
    # Who is doing the milking (if any)
    milker_dbref: str = ""
    milker_name: str = ""
    
    # Method
    method: str = "manual"  # manual, pump, nursing, magic
    
    # Progress
    total_extracted: float = 0.0
    duration_ticks: int = 0
    
    # Pleasure/pain tracking
    pleasure_generated: float = 0.0
    pain_generated: float = 0.0
    
    # Started
    started_at: Optional[datetime] = None
    
    def __post_init__(self):
        if not self.started_at:
            self.started_at = datetime.now()
    
    def tick(self, lactation: LactationTracker) -> Dict:
        """Process one tick of milking."""
        self.duration_ticks += 1
        
        # Extract milk
        result = lactation.milk(
            breast="both",
            amount=None,  # Extract what's available
            method=self.method,
        )
        
        self.total_extracted += result["total"]
        
        # Generate pleasure (more if nursing)
        pleasure = 0.5
        if self.method == "nursing":
            pleasure = 1.5
        elif self.method == "magic":
            pleasure = 2.0
        
        # Engorged breasts are sensitive
        if lactation.left_breast.is_engorged or lactation.right_breast.is_engorged:
            pleasure *= 1.5
            # But also some pain
            self.pain_generated += 0.2
        
        self.pleasure_generated += pleasure
        
        return {
            "extracted": result["total"],
            "pleasure": pleasure,
            "total_extracted": self.total_extracted,
        }
    
    def describe_progress(self) -> str:
        """Get description of milking progress."""
        if self.total_extracted < 10:
            return "just started milking"
        elif self.total_extracted < 100:
            return f"milked {format_measurement(self.total_extracted, 'ml')} so far"
        elif self.total_extracted < 1000:
            return f"produced {format_measurement(self.total_extracted, 'ml')} of milk"
        else:
            return f"milked an impressive {format_measurement(self.total_extracted, 'ml')}"


__all__ = [
    "LactationState",
    "BreastFullness",
    "BreastMilkStorage",
    "LactationTracker",
    "MilkingSession",
]
