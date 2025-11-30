"""
Sexual State Manager

Tracks per-part sexual states on a body:
- Orifice states (stretch, wetness, virginity)
- Penetrator states (arousal, knot state, cum storage)
- Breast states (lactation, sensitivity)

This lives on the Body object and gets serialized with it.
"""

from dataclasses import dataclass, field
from typing import Dict, Optional, List, Tuple, Any
from enum import Enum
import time

from .parts_sexual import (
    ArousalState,
    OrificeState,
    KnotState,
    SexualPartState,
    OrificeMechanics,
    PenetratorMechanics,
    SEXUAL_PART_REGISTRY,
    get_sexual_part,
)


# =============================================================================
# STATE MANAGER
# =============================================================================

class SexualStateManager:
    """
    Manages sexual states for all relevant parts on a body.
    
    Each orifice, penetrator, and breast has its own state tracking.
    States update from actions and decay/recover over time.
    """
    
    def __init__(self):
        # Part states keyed by part_key
        self.orifice_states: Dict[str, OrificeStateData] = {}
        self.penetrator_states: Dict[str, PenetratorStateData] = {}
        self.breast_states: Dict[str, BreastStateData] = {}
        
        # Global arousal (overall horniness)
        self.overall_arousal: float = 0.0
        self.arousal_state: ArousalState = ArousalState.SOFT
        
        # Timing
        self.last_tick: float = 0.0
        self.ticks_since_orgasm: int = 0
        self.in_refractory: bool = False
        self.refractory_remaining: int = 0
    
    def initialize_from_body(self, body: "Body"):
        """
        Initialize states based on body's parts.
        
        Called when body is created or loaded.
        """
        for part_key in body.parts:
            sex_part = get_sexual_part(part_key)
            
            # Check for sexual part directly
            if sex_part:
                if sex_part.is_orifice:
                    if part_key not in self.orifice_states:
                        self.orifice_states[part_key] = OrificeStateData(part_key=part_key)
                
                if sex_part.is_penetrator:
                    if part_key not in self.penetrator_states:
                        self.penetrator_states[part_key] = PenetratorStateData(part_key=part_key)
            
            # Special handling for parts that exist in parts.py but map to sexual parts
            # anus -> asshole mapping
            if part_key == "anus":
                if "anus" not in self.orifice_states and "asshole" not in self.orifice_states:
                    self.orifice_states["anus"] = OrificeStateData(part_key="anus")
            
            # mouth is both a regular part and a sexual orifice
            if part_key == "mouth":
                if "mouth" not in self.orifice_states:
                    self.orifice_states["mouth"] = OrificeStateData(part_key="mouth")
            
            # Breasts
            if part_key.startswith("breast") or part_key.startswith("nipple"):
                if part_key not in self.breast_states:
                    self.breast_states[part_key] = BreastStateData(part_key=part_key)
    
    # =========================================================================
    # ORIFICE STATE ACCESS
    # =========================================================================
    
    def get_orifice_state(self, part_key: str) -> Optional["OrificeStateData"]:
        """Get state for an orifice."""
        return self.orifice_states.get(part_key)
    
    def set_orifice_wetness(self, part_key: str, wetness: float):
        """Set wetness level for an orifice."""
        if part_key in self.orifice_states:
            self.orifice_states[part_key].current_wetness = max(0.0, min(1.0, wetness))
    
    def add_orifice_stretch(self, part_key: str, amount: float):
        """Add stretch to an orifice (from penetration)."""
        if part_key in self.orifice_states:
            state = self.orifice_states[part_key]
            state.current_stretch += amount
            state.times_used += 1
            if amount > state.largest_taken:
                state.largest_taken = amount
    
    def take_virginity(self, part_key: str, taken_by: str = ""):
        """Mark an orifice as no longer virgin."""
        if part_key in self.orifice_states:
            state = self.orifice_states[part_key]
            if state.orifice_state == OrificeState.VIRGIN:
                state.orifice_state = OrificeState.TIGHT
                state.virgin_lost_to = taken_by
                state.virgin_lost_when = time.time()
                return True
        return False
    
    def is_virgin(self, part_key: str) -> bool:
        """Check if an orifice is virgin."""
        state = self.orifice_states.get(part_key)
        if state:
            return state.orifice_state == OrificeState.VIRGIN
        return True  # Default to virgin if no state
    
    # =========================================================================
    # PENETRATOR STATE ACCESS
    # =========================================================================
    
    def get_penetrator_state(self, part_key: str) -> Optional["PenetratorStateData"]:
        """Get state for a penetrator."""
        return self.penetrator_states.get(part_key)
    
    def set_penetrator_arousal(self, part_key: str, arousal: ArousalState):
        """Set arousal for a penetrator."""
        if part_key in self.penetrator_states:
            self.penetrator_states[part_key].arousal = arousal
    
    def get_penetrator_arousal(self, part_key: str) -> ArousalState:
        """Get arousal for a penetrator."""
        state = self.penetrator_states.get(part_key)
        if state:
            return state.arousal
        return ArousalState.SOFT
    
    def swell_knot(self, part_key: str) -> bool:
        """Start swelling a knot."""
        state = self.penetrator_states.get(part_key)
        if state and state.knot_state == KnotState.DEFLATED:
            state.knot_state = KnotState.SWELLING
            return True
        return False
    
    def lock_knot(self, part_key: str, locked_in: str):
        """Lock a knot inside an orifice."""
        state = self.penetrator_states.get(part_key)
        if state:
            state.knot_state = KnotState.LOCKED
            state.locked_in_orifice = locked_in
    
    def unlock_knot(self, part_key: str):
        """Unlock a knot."""
        state = self.penetrator_states.get(part_key)
        if state:
            state.knot_state = KnotState.DEFLATING
            state.locked_in_orifice = ""
    
    def add_cum(self, part_key: str, amount: float):
        """Add cum storage (from time/production)."""
        state = self.penetrator_states.get(part_key)
        if state:
            state.cum_stored = min(1.0, state.cum_stored + amount)
    
    def drain_cum(self, part_key: str) -> float:
        """Drain cum on orgasm, return amount released."""
        state = self.penetrator_states.get(part_key)
        if state:
            released = state.cum_stored
            state.cum_stored = 0.0
            state.times_orgasmed += 1
            return released
        return 0.0
    
    # =========================================================================
    # BREAST STATE ACCESS
    # =========================================================================
    
    def get_breast_state(self, part_key: str) -> Optional["BreastStateData"]:
        """Get state for a breast."""
        return self.breast_states.get(part_key)
    
    def set_lactating(self, part_key: str, lactating: bool):
        """Set lactation state."""
        if part_key in self.breast_states:
            self.breast_states[part_key].is_lactating = lactating
    
    def add_milk(self, part_key: str, amount: float):
        """Add milk to breast."""
        if part_key in self.breast_states:
            state = self.breast_states[part_key]
            state.milk_stored = min(1.0, state.milk_stored + amount)
    
    def drain_milk(self, part_key: str, amount: float) -> float:
        """Drain milk from breast."""
        if part_key in self.breast_states:
            state = self.breast_states[part_key]
            drained = min(amount, state.milk_stored)
            state.milk_stored -= drained
            return drained
        return 0.0
    
    # =========================================================================
    # OVERALL AROUSAL
    # =========================================================================
    
    def add_arousal(self, amount: float):
        """Add to overall arousal."""
        self.overall_arousal = min(1.0, self.overall_arousal + amount)
        self._update_arousal_state()
    
    def reduce_arousal(self, amount: float):
        """Reduce overall arousal."""
        self.overall_arousal = max(0.0, self.overall_arousal - amount)
        self._update_arousal_state()
    
    def _update_arousal_state(self):
        """Update arousal state enum based on level."""
        if self.overall_arousal >= 0.9:
            self.arousal_state = ArousalState.THROBBING
        elif self.overall_arousal >= 0.7:
            self.arousal_state = ArousalState.HARD
        elif self.overall_arousal >= 0.5:
            self.arousal_state = ArousalState.HALF
        elif self.overall_arousal >= 0.25:
            self.arousal_state = ArousalState.CHUBBED
        else:
            self.arousal_state = ArousalState.SOFT
    
    def trigger_orgasm(self) -> Dict[str, float]:
        """
        Trigger orgasm - drain all penetrators, reset arousal.
        
        Returns:
            Dict of part_key -> cum amount released
        """
        released = {}
        
        # Drain all penetrators
        for part_key, state in self.penetrator_states.items():
            if state.cum_stored > 0:
                released[part_key] = self.drain_cum(part_key)
        
        # Reset arousal
        self.overall_arousal = 0.0
        self.arousal_state = ArousalState.SOFT
        
        # Enter refractory
        self.in_refractory = True
        self.refractory_remaining = 50  # ~5 minutes at 6 sec/tick
        self.ticks_since_orgasm = 0
        
        return released
    
    # =========================================================================
    # TIME/TICK PROCESSING
    # =========================================================================
    
    def tick(self, ticks: int = 1):
        """
        Process time passing.
        
        Called periodically to update states.
        """
        self.ticks_since_orgasm += ticks
        
        # Process refractory period
        if self.in_refractory:
            self.refractory_remaining -= ticks
            if self.refractory_remaining <= 0:
                self.in_refractory = False
                self.refractory_remaining = 0
        
        # Orifice recovery
        for state in self.orifice_states.values():
            state.tick(ticks)
        
        # Penetrator changes
        for state in self.penetrator_states.values():
            state.tick(ticks)
        
        # Arousal decay (if not stimulated)
        if self.overall_arousal > 0:
            decay = ticks * 0.01  # 1% per tick
            self.reduce_arousal(decay)
        
        # Cum regeneration
        for state in self.penetrator_states.values():
            regen = ticks * 0.002  # Slow regeneration
            state.cum_stored = min(1.0, state.cum_stored + regen)
        
        # Milk production (if lactating)
        for state in self.breast_states.values():
            if state.is_lactating:
                production = ticks * 0.001
                state.milk_stored = min(1.0, state.milk_stored + production)
    
    # =========================================================================
    # SERIALIZATION
    # =========================================================================
    
    def to_dict(self) -> dict:
        """Serialize to dictionary."""
        return {
            "orifice_states": {k: v.to_dict() for k, v in self.orifice_states.items()},
            "penetrator_states": {k: v.to_dict() for k, v in self.penetrator_states.items()},
            "breast_states": {k: v.to_dict() for k, v in self.breast_states.items()},
            "overall_arousal": self.overall_arousal,
            "arousal_state": self.arousal_state.value,
            "ticks_since_orgasm": self.ticks_since_orgasm,
            "in_refractory": self.in_refractory,
            "refractory_remaining": self.refractory_remaining,
        }
    
    @classmethod
    def from_dict(cls, data: dict) -> "SexualStateManager":
        """Deserialize from dictionary."""
        manager = cls()
        
        for k, v in data.get("orifice_states", {}).items():
            manager.orifice_states[k] = OrificeStateData.from_dict(v)
        
        for k, v in data.get("penetrator_states", {}).items():
            manager.penetrator_states[k] = PenetratorStateData.from_dict(v)
        
        for k, v in data.get("breast_states", {}).items():
            manager.breast_states[k] = BreastStateData.from_dict(v)
        
        manager.overall_arousal = data.get("overall_arousal", 0.0)
        arousal_val = data.get("arousal_state", "soft")
        manager.arousal_state = ArousalState(arousal_val) if isinstance(arousal_val, str) else arousal_val
        manager.ticks_since_orgasm = data.get("ticks_since_orgasm", 0)
        manager.in_refractory = data.get("in_refractory", False)
        manager.refractory_remaining = data.get("refractory_remaining", 0)
        
        return manager


# =============================================================================
# STATE DATA CLASSES
# =============================================================================

@dataclass
class OrificeStateData:
    """State data for a single orifice."""
    
    part_key: str
    
    # Virginity
    orifice_state: OrificeState = OrificeState.VIRGIN
    virgin_lost_to: str = ""
    virgin_lost_when: float = 0.0
    
    # Stretch
    current_stretch: float = 0.0
    permanent_stretch: float = 0.0
    stretch_recovery_rate: float = 0.1  # Per tick
    
    # Wetness
    current_wetness: float = 0.0
    
    # Usage tracking
    times_used: int = 0
    largest_taken: float = 0.0
    
    # Gaping
    is_gaping: bool = False
    gape_remaining: int = 0  # Ticks until closes
    
    # What's currently inside
    currently_penetrated_by: str = ""  # Part key or item
    penetration_depth: float = 0.0
    is_knotted: bool = False
    
    # Cum inside
    cum_inside: float = 0.0
    cum_sources: List[str] = field(default_factory=list)  # Who came inside
    
    def tick(self, ticks: int = 1):
        """Process time passing."""
        # Stretch recovery
        if self.current_stretch > 0 and not self.currently_penetrated_by:
            recovery = ticks * self.stretch_recovery_rate
            self.current_stretch = max(0, self.current_stretch - recovery)
        
        # Gape recovery
        if self.is_gaping:
            self.gape_remaining -= ticks
            if self.gape_remaining <= 0:
                self.is_gaping = False
                self.gape_remaining = 0
        
        # Wetness decay (unless aroused - handled elsewhere)
        if self.current_wetness > 0:
            self.current_wetness = max(0, self.current_wetness - ticks * 0.02)
        
        # Cum leaking
        if self.cum_inside > 0 and not self.is_knotted:
            leak_rate = 0.05 if self.is_gaping else 0.01
            self.cum_inside = max(0, self.cum_inside - ticks * leak_rate)
    
    def to_dict(self) -> dict:
        return {
            "part_key": self.part_key,
            "orifice_state": self.orifice_state.value,
            "virgin_lost_to": self.virgin_lost_to,
            "virgin_lost_when": self.virgin_lost_when,
            "current_stretch": self.current_stretch,
            "permanent_stretch": self.permanent_stretch,
            "stretch_recovery_rate": self.stretch_recovery_rate,
            "current_wetness": self.current_wetness,
            "times_used": self.times_used,
            "largest_taken": self.largest_taken,
            "is_gaping": self.is_gaping,
            "gape_remaining": self.gape_remaining,
            "currently_penetrated_by": self.currently_penetrated_by,
            "penetration_depth": self.penetration_depth,
            "is_knotted": self.is_knotted,
            "cum_inside": self.cum_inside,
            "cum_sources": self.cum_sources,
        }
    
    @classmethod
    def from_dict(cls, data: dict) -> "OrificeStateData":
        state = cls(part_key=data.get("part_key", ""))
        state.orifice_state = OrificeState(data.get("orifice_state", "virgin"))
        state.virgin_lost_to = data.get("virgin_lost_to", "")
        state.virgin_lost_when = data.get("virgin_lost_when", 0.0)
        state.current_stretch = data.get("current_stretch", 0.0)
        state.permanent_stretch = data.get("permanent_stretch", 0.0)
        state.stretch_recovery_rate = data.get("stretch_recovery_rate", 0.1)
        state.current_wetness = data.get("current_wetness", 0.0)
        state.times_used = data.get("times_used", 0)
        state.largest_taken = data.get("largest_taken", 0.0)
        state.is_gaping = data.get("is_gaping", False)
        state.gape_remaining = data.get("gape_remaining", 0)
        state.currently_penetrated_by = data.get("currently_penetrated_by", "")
        state.penetration_depth = data.get("penetration_depth", 0.0)
        state.is_knotted = data.get("is_knotted", False)
        state.cum_inside = data.get("cum_inside", 0.0)
        state.cum_sources = data.get("cum_sources", [])
        return state


@dataclass
class PenetratorStateData:
    """State data for a single penetrator."""
    
    part_key: str
    
    # Arousal
    arousal: ArousalState = ArousalState.SOFT
    arousal_level: float = 0.0  # 0.0-1.0 for granular tracking
    
    # Knot (if applicable)
    knot_state: KnotState = KnotState.DEFLATED
    locked_in_orifice: str = ""  # Part key of orifice
    lock_remaining: int = 0  # Ticks until unlock
    
    # Cum
    cum_stored: float = 1.0  # 0.0-1.0, percentage full
    times_orgasmed: int = 0
    
    # Currently in use
    currently_inside: str = ""  # Orifice part key
    current_depth: float = 0.0
    
    # Size (can be customized from defaults)
    size_modifier: float = 1.0  # Multiplier on base size
    
    def tick(self, ticks: int = 1):
        """Process time passing."""
        # Arousal decay if not stimulated
        if self.arousal_level > 0 and not self.currently_inside:
            decay = ticks * 0.02
            self.arousal_level = max(0, self.arousal_level - decay)
            self._update_arousal_state()
        
        # Knot deflation
        if self.knot_state == KnotState.LOCKED:
            self.lock_remaining -= ticks
            if self.lock_remaining <= 0:
                self.knot_state = KnotState.DEFLATING
        elif self.knot_state == KnotState.DEFLATING:
            # Fully deflates after some time
            self.knot_state = KnotState.DEFLATED
            self.locked_in_orifice = ""
    
    def _update_arousal_state(self):
        """Update arousal enum from level."""
        if self.arousal_level >= 0.9:
            self.arousal = ArousalState.THROBBING
        elif self.arousal_level >= 0.7:
            self.arousal = ArousalState.HARD
        elif self.arousal_level >= 0.5:
            self.arousal = ArousalState.HALF
        elif self.arousal_level >= 0.25:
            self.arousal = ArousalState.CHUBBED
        else:
            self.arousal = ArousalState.SOFT
    
    def to_dict(self) -> dict:
        return {
            "part_key": self.part_key,
            "arousal": self.arousal.value,
            "arousal_level": self.arousal_level,
            "knot_state": self.knot_state.value,
            "locked_in_orifice": self.locked_in_orifice,
            "lock_remaining": self.lock_remaining,
            "cum_stored": self.cum_stored,
            "times_orgasmed": self.times_orgasmed,
            "currently_inside": self.currently_inside,
            "current_depth": self.current_depth,
            "size_modifier": self.size_modifier,
        }
    
    @classmethod
    def from_dict(cls, data: dict) -> "PenetratorStateData":
        state = cls(part_key=data.get("part_key", ""))
        state.arousal = ArousalState(data.get("arousal", "soft"))
        state.arousal_level = data.get("arousal_level", 0.0)
        state.knot_state = KnotState(data.get("knot_state", "deflated"))
        state.locked_in_orifice = data.get("locked_in_orifice", "")
        state.lock_remaining = data.get("lock_remaining", 0)
        state.cum_stored = data.get("cum_stored", 1.0)
        state.times_orgasmed = data.get("times_orgasmed", 0)
        state.currently_inside = data.get("currently_inside", "")
        state.current_depth = data.get("current_depth", 0.0)
        state.size_modifier = data.get("size_modifier", 1.0)
        return state


@dataclass
class BreastStateData:
    """State data for a breast."""
    
    part_key: str
    
    # Lactation
    is_lactating: bool = False
    milk_stored: float = 0.0  # 0.0-1.0
    milk_production_rate: float = 0.001  # Per tick when lactating
    
    # Engorgement (when milk is full)
    is_engorged: bool = False
    
    # Sensitivity
    sensitivity_modifier: float = 1.0
    nipple_erect: bool = False
    
    # Size
    size_modifier: float = 1.0
    
    def tick(self, ticks: int = 1):
        """Process time passing."""
        # Milk production
        if self.is_lactating:
            self.milk_stored = min(1.0, self.milk_stored + ticks * self.milk_production_rate)
            self.is_engorged = self.milk_stored >= 0.9
        
        # Nipple erection fades
        # (stays erect from cold/arousal but fades otherwise)
    
    def to_dict(self) -> dict:
        return {
            "part_key": self.part_key,
            "is_lactating": self.is_lactating,
            "milk_stored": self.milk_stored,
            "milk_production_rate": self.milk_production_rate,
            "is_engorged": self.is_engorged,
            "sensitivity_modifier": self.sensitivity_modifier,
            "nipple_erect": self.nipple_erect,
            "size_modifier": self.size_modifier,
        }
    
    @classmethod
    def from_dict(cls, data: dict) -> "BreastStateData":
        state = cls(part_key=data.get("part_key", ""))
        state.is_lactating = data.get("is_lactating", False)
        state.milk_stored = data.get("milk_stored", 0.0)
        state.milk_production_rate = data.get("milk_production_rate", 0.001)
        state.is_engorged = data.get("is_engorged", False)
        state.sensitivity_modifier = data.get("sensitivity_modifier", 1.0)
        state.nipple_erect = data.get("nipple_erect", False)
        state.size_modifier = data.get("size_modifier", 1.0)
        return state
