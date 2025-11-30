"""
Inflation System
================

Body inflation mechanics including:
- Cum inflation
- Belly expansion
- Breast inflation
- Capacity limits
- Discomfort and pleasure tracking
- Drainage
"""

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any, Tuple
from enum import Enum
from datetime import datetime, timedelta
import random


# =============================================================================
# ENUMS
# =============================================================================

class InflationType(Enum):
    """Types of inflation."""
    CUM = "cum"
    WATER = "water"
    AIR = "air"
    EGGS = "eggs"
    SLIME = "slime"
    MILK = "milk"
    MAGICAL = "magical"


class InflationLocation(Enum):
    """Where inflation occurs."""
    BELLY = "belly"               # Stomach/womb
    WOMB = "womb"                 # Specifically womb
    STOMACH = "stomach"           # Swallowed
    ANAL = "anal"                 # Anal inflation
    BREASTS = "breasts"
    BALLS = "balls"               # For futa/males
    FULL_BODY = "full_body"       # All over


class DistensionLevel(Enum):
    """Levels of body distension."""
    NONE = "none"
    SLIGHT = "slight"             # Barely noticeable
    VISIBLE = "visible"           # Obviously swollen
    HEAVY = "heavy"               # Very distended
    EXTREME = "extreme"           # Massively bloated
    IMMOBILIZING = "immobilizing" # Can barely move


# =============================================================================
# INFLATION STATE
# =============================================================================

@dataclass
class InflationState:
    """Tracks inflation in a specific body area."""
    
    location: InflationLocation = InflationLocation.BELLY
    
    # Contents
    contents: Dict[str, int] = field(default_factory=dict)  # Type -> ml
    total_volume_ml: int = 0
    
    # Capacity
    base_capacity_ml: int = 1000
    current_capacity_ml: int = 1000
    stretch_bonus_ml: int = 0     # Permanent stretch
    
    # State
    distension_level: DistensionLevel = DistensionLevel.NONE
    distension_percent: float = 0.0
    
    # Sensation
    discomfort: int = 0           # 0-100
    pleasure: int = 0             # 0-100
    pressure: int = 0             # 0-100
    
    # Leakage
    is_leaking: bool = False
    leak_rate_ml_per_hour: int = 0
    
    @property
    def capacity(self) -> int:
        """Get total capacity including stretch."""
        return self.base_capacity_ml + self.stretch_bonus_ml
    
    @property
    def fill_percent(self) -> float:
        """Get fill percentage."""
        return (self.total_volume_ml / self.capacity) * 100 if self.capacity > 0 else 0
    
    @property
    def is_full(self) -> bool:
        """Check if at capacity."""
        return self.total_volume_ml >= self.capacity
    
    @property
    def is_overfilled(self) -> bool:
        """Check if over capacity."""
        return self.total_volume_ml > self.capacity
    
    def add_inflation(self, inflation_type: str, amount_ml: int) -> Tuple[int, str]:
        """
        Add inflation.
        Returns (amount_actually_added, message).
        """
        # Can slightly exceed capacity with discomfort
        max_fill = int(self.capacity * 1.5)
        can_add = max_fill - self.total_volume_ml
        
        actual_add = min(amount_ml, can_add)
        
        if actual_add <= 0:
            self.is_leaking = True
            return 0, "Too full! Excess leaks out immediately."
        
        # Add to contents
        if inflation_type in self.contents:
            self.contents[inflation_type] += actual_add
        else:
            self.contents[inflation_type] = actual_add
        
        self.total_volume_ml += actual_add
        
        # Update distension
        self._update_distension()
        
        # Stretch if overfilled
        if self.total_volume_ml > self.capacity:
            stretch = (self.total_volume_ml - self.capacity) // 10
            self.stretch_bonus_ml += stretch
        
        # Check for leakage
        if self.total_volume_ml > self.capacity:
            self.is_leaking = True
            self.leak_rate_ml_per_hour = (self.total_volume_ml - self.capacity) // 2
        
        # Generate message
        msg = self._get_inflation_message(actual_add, amount_ml - actual_add)
        
        return actual_add, msg
    
    def drain(self, amount_ml: int = 0, drain_type: str = "") -> Tuple[int, str]:
        """
        Drain inflation.
        Returns (amount_drained, message).
        """
        if amount_ml == 0:
            amount_ml = self.total_volume_ml
        
        if drain_type and drain_type in self.contents:
            # Drain specific type
            available = self.contents[drain_type]
            drained = min(amount_ml, available)
            self.contents[drain_type] -= drained
            if self.contents[drain_type] <= 0:
                del self.contents[drain_type]
        else:
            # Drain proportionally from all
            drained = min(amount_ml, self.total_volume_ml)
            ratio = drained / self.total_volume_ml if self.total_volume_ml > 0 else 0
            
            for t in list(self.contents.keys()):
                reduction = int(self.contents[t] * ratio)
                self.contents[t] -= reduction
                if self.contents[t] <= 0:
                    del self.contents[t]
        
        self.total_volume_ml = sum(self.contents.values())
        
        self._update_distension()
        
        if self.total_volume_ml <= self.capacity:
            self.is_leaking = False
            self.leak_rate_ml_per_hour = 0
        
        return drained, f"Expelled {drained}ml. Now at {self.fill_percent:.0f}% capacity."
    
    def process_time(self, hours: float) -> Tuple[int, str]:
        """
        Process time passing (leakage, absorption).
        Returns (amount_lost, message).
        """
        messages = []
        total_lost = 0
        
        # Natural leakage if overfilled
        if self.is_leaking and self.leak_rate_ml_per_hour > 0:
            leak = int(self.leak_rate_ml_per_hour * hours)
            drained, _ = self.drain(leak)
            total_lost += drained
            messages.append(f"Leaked {drained}ml")
        
        # Natural absorption (cum/slime absorb over time)
        absorb_types = ["cum", "slime"]
        for t in absorb_types:
            if t in self.contents:
                absorb = int(self.contents[t] * 0.1 * hours)  # 10% per hour
                if absorb > 0:
                    self.contents[t] -= absorb
                    self.total_volume_ml -= absorb
                    if self.contents[t] <= 0:
                        del self.contents[t]
                    messages.append(f"Absorbed {absorb}ml {t}")
        
        self._update_distension()
        
        return total_lost, " | ".join(messages) if messages else "No change."
    
    def _update_distension(self) -> None:
        """Update distension level and sensations."""
        self.distension_percent = self.fill_percent
        
        if self.distension_percent >= 150:
            self.distension_level = DistensionLevel.IMMOBILIZING
            self.discomfort = 100
            self.pressure = 100
            self.pleasure = 20
        elif self.distension_percent >= 120:
            self.distension_level = DistensionLevel.EXTREME
            self.discomfort = 80
            self.pressure = 90
            self.pleasure = 40
        elif self.distension_percent >= 90:
            self.distension_level = DistensionLevel.HEAVY
            self.discomfort = 50
            self.pressure = 70
            self.pleasure = 60
        elif self.distension_percent >= 60:
            self.distension_level = DistensionLevel.VISIBLE
            self.discomfort = 20
            self.pressure = 40
            self.pleasure = 70
        elif self.distension_percent >= 30:
            self.distension_level = DistensionLevel.SLIGHT
            self.discomfort = 5
            self.pressure = 20
            self.pleasure = 50
        else:
            self.distension_level = DistensionLevel.NONE
            self.discomfort = 0
            self.pressure = 0
            self.pleasure = 0
    
    def _get_inflation_message(self, added: int, overflow: int) -> str:
        """Get message for inflation event."""
        msgs = []
        
        if self.distension_level == DistensionLevel.IMMOBILIZING:
            msgs.append("Massively bloated, can barely move!")
        elif self.distension_level == DistensionLevel.EXTREME:
            msgs.append("Belly stretched to the limit, skin tight!")
        elif self.distension_level == DistensionLevel.HEAVY:
            msgs.append("Heavily distended, sloshing with every movement.")
        elif self.distension_level == DistensionLevel.VISIBLE:
            msgs.append("Noticeably swollen, belly rounding out.")
        elif self.distension_level == DistensionLevel.SLIGHT:
            msgs.append("Slight fullness, a gentle pressure.")
        
        if overflow > 0:
            msgs.append(f"{overflow}ml couldn't fit and leaked out.")
        
        if self.is_leaking:
            msgs.append("Leaking steadily.")
        
        return " ".join(msgs)
    
    def get_description(self) -> str:
        """Get descriptive text."""
        if self.total_volume_ml == 0:
            return "flat and empty"
        
        descs = {
            DistensionLevel.NONE: "normal",
            DistensionLevel.SLIGHT: "slightly swollen",
            DistensionLevel.VISIBLE: "noticeably distended",
            DistensionLevel.HEAVY: "heavily bloated, looking several months pregnant",
            DistensionLevel.EXTREME: "massively swollen, skin stretched taut",
            DistensionLevel.IMMOBILIZING: "grotesquely bloated, immobilized by sheer size",
        }
        
        desc = descs.get(self.distension_level, "swollen")
        
        # Add content description
        if self.contents:
            content_str = ", ".join(f"{v}ml {k}" for k, v in self.contents.items())
            desc += f" with {content_str}"
        
        return desc


# =============================================================================
# FULL INFLATION TRACKING
# =============================================================================

@dataclass
class InflationTracker:
    """Tracks all inflation for a character."""
    
    subject_dbref: str = ""
    subject_name: str = ""
    
    # Body areas
    belly: InflationState = field(default_factory=lambda: InflationState(location=InflationLocation.BELLY, base_capacity_ml=2000))
    womb: InflationState = field(default_factory=lambda: InflationState(location=InflationLocation.WOMB, base_capacity_ml=1000))
    stomach: InflationState = field(default_factory=lambda: InflationState(location=InflationLocation.STOMACH, base_capacity_ml=1500))
    anal: InflationState = field(default_factory=lambda: InflationState(location=InflationLocation.ANAL, base_capacity_ml=500))
    breasts: InflationState = field(default_factory=lambda: InflationState(location=InflationLocation.BREASTS, base_capacity_ml=500))
    
    # Totals
    total_cum_received_ml: int = 0
    total_cum_absorbed_ml: int = 0
    
    # Records
    max_belly_distension: float = 0.0
    max_simultaneous_loads: int = 0
    
    def inflate(self, location: str, inflation_type: str, amount_ml: int) -> str:
        """Inflate a body area."""
        area = getattr(self, location, None)
        if not area:
            return f"Unknown location: {location}"
        
        actual, msg = area.add_inflation(inflation_type, amount_ml)
        
        # Track totals
        if inflation_type == "cum":
            self.total_cum_received_ml += actual
        
        # Update records
        if area.distension_percent > self.max_belly_distension:
            self.max_belly_distension = area.distension_percent
        
        return msg
    
    def drain_area(self, location: str, amount_ml: int = 0) -> str:
        """Drain a body area."""
        area = getattr(self, location, None)
        if not area:
            return f"Unknown location: {location}"
        
        drained, msg = area.drain(amount_ml)
        return msg
    
    def process_time(self, hours: float) -> List[str]:
        """Process time for all areas."""
        messages = []
        
        for location in ["belly", "womb", "stomach", "anal", "breasts"]:
            area = getattr(self, location)
            if area.total_volume_ml > 0:
                _, msg = area.process_time(hours)
                if "No change" not in msg:
                    messages.append(f"{location}: {msg}")
        
        return messages
    
    def get_total_volume(self) -> int:
        """Get total inflation volume across all areas."""
        return (
            self.belly.total_volume_ml +
            self.womb.total_volume_ml +
            self.stomach.total_volume_ml +
            self.anal.total_volume_ml +
            self.breasts.total_volume_ml
        )
    
    def get_appearance_description(self) -> str:
        """Get description of inflated appearance."""
        parts = []
        
        if self.belly.total_volume_ml > 0:
            parts.append(f"belly {self.belly.get_description()}")
        
        if self.womb.total_volume_ml > 0:
            parts.append(f"womb {self.womb.get_description()}")
        
        if self.stomach.total_volume_ml > 0:
            parts.append(f"stomach {self.stomach.get_description()}")
        
        if self.anal.total_volume_ml > 0:
            parts.append(f"ass {self.anal.get_description()}")
        
        if self.breasts.total_volume_ml > 0:
            parts.append(f"breasts {self.breasts.get_description()}")
        
        if not parts:
            return "Normal, uninflated body."
        
        return "Body showing: " + ", ".join(parts) + "."
    
    def get_status(self) -> str:
        """Get complete inflation status."""
        lines = [f"=== Inflation Status: {self.subject_name} ==="]
        
        total = self.get_total_volume()
        lines.append(f"Total Volume: {total}ml")
        
        for location in ["belly", "womb", "stomach", "anal", "breasts"]:
            area = getattr(self, location)
            if area.total_volume_ml > 0:
                lines.append(f"\n--- {location.upper()} ---")
                lines.append(f"Volume: {area.total_volume_ml}/{area.capacity}ml ({area.fill_percent:.0f}%)")
                lines.append(f"Distension: {area.distension_level.value}")
                lines.append(f"Contents: {area.contents}")
                lines.append(f"Discomfort: {area.discomfort}/100 | Pleasure: {area.pleasure}/100")
                if area.is_leaking:
                    lines.append(f"LEAKING: {area.leak_rate_ml_per_hour}ml/hour")
        
        lines.append(f"\n--- Records ---")
        lines.append(f"Total Cum Received: {self.total_cum_received_ml}ml")
        lines.append(f"Max Distension: {self.max_belly_distension:.0f}%")
        
        return "\n".join(lines)
    
    def to_dict(self) -> dict:
        return {
            "subject_dbref": self.subject_dbref,
            "subject_name": self.subject_name,
            "belly_volume": self.belly.total_volume_ml,
            "belly_capacity": self.belly.capacity,
            "womb_volume": self.womb.total_volume_ml,
            "stomach_volume": self.stomach.total_volume_ml,
            "anal_volume": self.anal.total_volume_ml,
            "breasts_volume": self.breasts.total_volume_ml,
            "total_cum_received_ml": self.total_cum_received_ml,
            "max_belly_distension": self.max_belly_distension,
        }
    
    @classmethod
    def from_dict(cls, data: dict) -> "InflationTracker":
        tracker = cls()
        tracker.subject_dbref = data.get("subject_dbref", "")
        tracker.subject_name = data.get("subject_name", "")
        tracker.belly.total_volume_ml = data.get("belly_volume", 0)
        tracker.womb.total_volume_ml = data.get("womb_volume", 0)
        tracker.stomach.total_volume_ml = data.get("stomach_volume", 0)
        tracker.anal.total_volume_ml = data.get("anal_volume", 0)
        tracker.breasts.total_volume_ml = data.get("breasts_volume", 0)
        tracker.total_cum_received_ml = data.get("total_cum_received_ml", 0)
        tracker.max_belly_distension = data.get("max_belly_distension", 0)
        return tracker


# =============================================================================
# INFLATION MIXIN
# =============================================================================

class InflationMixin:
    """Mixin for characters that can be inflated."""
    
    @property
    def inflation(self) -> InflationTracker:
        """Get inflation tracker."""
        data = self.db.inflation
        if data:
            return InflationTracker.from_dict(data)
        return InflationTracker(subject_dbref=self.dbref, subject_name=self.key)
    
    @inflation.setter
    def inflation(self, tracker: InflationTracker) -> None:
        """Set inflation tracker."""
        self.db.inflation = tracker.to_dict()
    
    def add_cum_inflation(self, location: str, amount_ml: int) -> str:
        """Convenience method to add cum inflation."""
        tracker = self.inflation
        result = tracker.inflate(location, "cum", amount_ml)
        self.inflation = tracker
        return result


# =============================================================================
# PRESET INFLATION EVENTS
# =============================================================================

def cum_dump(tracker: InflationTracker, amount_ml: int, location: str = "womb") -> str:
    """Large single cum deposit."""
    msg = tracker.inflate(location, "cum", amount_ml)
    return f"Massive load pumped in! {msg}"


def gangbang_inflation(tracker: InflationTracker, num_loads: int, avg_amount: int = 50) -> str:
    """Multiple loads from gangbang."""
    messages = []
    
    for i in range(num_loads):
        amount = random.randint(int(avg_amount * 0.7), int(avg_amount * 1.3))
        location = random.choice(["womb", "womb", "womb", "anal", "stomach"])
        msg = tracker.inflate(location, "cum", amount)
        messages.append(f"Load {i+1}: {amount}ml")
    
    total = sum(int(m.split(":")[1].replace("ml", "").strip()) for m in messages)
    
    return f"Gangbang complete! {num_loads} loads, {total}ml total.\n{tracker.get_appearance_description()}"


def slime_engulf(tracker: InflationTracker, amount_ml: int) -> str:
    """Slime flooding all holes."""
    womb_amount = amount_ml // 2
    anal_amount = amount_ml // 3
    stomach_amount = amount_ml // 6
    
    tracker.inflate("womb", "slime", womb_amount)
    tracker.inflate("anal", "slime", anal_amount)
    tracker.inflate("stomach", "slime", stomach_amount)
    
    return f"Slime floods every hole! {amount_ml}ml total.\n{tracker.get_appearance_description()}"


__all__ = [
    "InflationType",
    "InflationLocation",
    "DistensionLevel",
    "InflationState",
    "InflationTracker",
    "InflationMixin",
    "cum_dump",
    "gangbang_inflation",
    "slime_engulf",
    "InflationCmdSet",
]

# Import commands
from .commands import InflationCmdSet
