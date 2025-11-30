"""
Feral Mechanics
===============

Mechanics for feral creature interactions:
- Knotting (tie, lock, release)
- Heat/rut cycles
- Leashing and dragging
"""

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple
from enum import Enum
from datetime import datetime
from random import random, randint

from evennia import AttributeProperty

try:
    from evennia.utils import delay
    HAS_DELAY = True
except ImportError:
    HAS_DELAY = False
    def delay(*args, **kwargs): pass


# =============================================================================
# KNOT SYSTEM
# =============================================================================

class KnotState(Enum):
    DEFLATED = "deflated"
    SWELLING = "swelling"
    LOCKED = "locked"
    DEFLATING = "deflating"


@dataclass
class KnotConfig:
    """Knotting configuration per species."""
    can_knot: bool = True
    swell_time: int = 30
    lock_time: int = 300
    lock_time_variance: int = 120
    deflate_time: int = 60
    knot_size: float = 1.0
    
    def get_actual_lock_time(self) -> int:
        variance = randint(-self.lock_time_variance, self.lock_time_variance)
        return max(60, self.lock_time + variance)


KNOT_CONFIGS = {
    "canine": KnotConfig(swell_time=30, lock_time=300, deflate_time=60),
    "wolf": KnotConfig(swell_time=45, lock_time=600, lock_time_variance=180, knot_size=1.2),
    "dog": KnotConfig(swell_time=30, lock_time=300, deflate_time=60),
    "fox": KnotConfig(swell_time=20, lock_time=180, lock_time_variance=60, knot_size=0.8),
    "hyena": KnotConfig(swell_time=25, lock_time=240, knot_size=0.9),
    "feline": KnotConfig(can_knot=False),
    "equine": KnotConfig(can_knot=False),
    "human": KnotConfig(can_knot=False),
    "default": KnotConfig(can_knot=False),
}


@dataclass
class TieData:
    """Data about an active tie."""
    penetrator_dbref: str
    penetrator_name: str
    receiver_dbref: str
    receiver_name: str
    knot_state: KnotState = KnotState.DEFLATED
    started_at: datetime = field(default_factory=datetime.now)
    lock_started_at: Optional[datetime] = None
    lock_duration: int = 300
    
    def time_remaining(self) -> int:
        if not self.lock_started_at or self.knot_state != KnotState.LOCKED:
            return 0
        elapsed = (datetime.now() - self.lock_started_at).total_seconds()
        return max(0, int(self.lock_duration - elapsed))


# =============================================================================
# HEAT SYSTEM
# =============================================================================

class HeatPhase(Enum):
    NORMAL = "normal"
    PRE_HEAT = "pre_heat"
    HEAT = "heat"
    POST_HEAT = "post_heat"


@dataclass
class HeatConfig:
    """Heat cycle configuration."""
    has_cycles: bool = True
    normal_duration: int = 168  # Hours
    pre_heat_duration: int = 24
    heat_duration: int = 72
    post_heat_duration: int = 24
    heat_arousal_mod: float = 3.0
    mate_seeking_chance: float = 0.3


HEAT_CONFIGS = {
    "canine": HeatConfig(normal_duration=336, heat_duration=72),
    "wolf": HeatConfig(normal_duration=720, heat_duration=96, heat_arousal_mod=4.0),
    "feline": HeatConfig(normal_duration=168, heat_duration=48, heat_arousal_mod=3.5, mate_seeking_chance=0.4),
    "equine": HeatConfig(normal_duration=504, heat_duration=120),
    "human": HeatConfig(has_cycles=False),
    "default": HeatConfig(has_cycles=False),
}


# =============================================================================
# LEASH SYSTEM
# =============================================================================

class LeashState(Enum):
    ATTACHED = "attached"
    TAUT = "taut"
    SLACK = "slack"


@dataclass
class LeashData:
    """Leash connection data."""
    holder_dbref: str
    holder_name: str
    leashed_dbref: str
    leashed_name: str
    state: LeashState = LeashState.ATTACHED
    length: int = 3
    strength: int = 50
    is_locked: bool = False


# =============================================================================
# KNOTTING MIXIN
# =============================================================================

class KnottingMixin:
    """Mixin for knotting capabilities."""
    
    def get_knot_config(self) -> KnotConfig:
        if hasattr(self, 'db') and getattr(self.db, 'knot_config_data', None):
            return KnotConfig(**self.db.knot_config_data)
        body = self.get_body() if hasattr(self, 'get_body') else None
        if body:
            species = getattr(body, 'species_key', 'default')
            return KNOT_CONFIGS.get(species, KNOT_CONFIGS["default"])
        return KNOT_CONFIGS["default"]
    
    def set_knot_config(self, config: KnotConfig):
        if hasattr(self, 'db'):
            self.db.knot_config_data = {
                'can_knot': config.can_knot,
                'swell_time': config.swell_time,
                'lock_time': config.lock_time,
                'lock_time_variance': config.lock_time_variance,
                'deflate_time': config.deflate_time,
                'knot_size': config.knot_size,
            }
    
    def can_knot(self) -> bool:
        return self.get_knot_config().can_knot
    
    def get_current_tie(self) -> Optional[TieData]:
        if hasattr(self, 'db') and self.db.current_tie_data:
            data = self.db.current_tie_data.copy()
            data['knot_state'] = KnotState(data['knot_state']) if isinstance(data['knot_state'], str) else data['knot_state']
            if data.get('started_at') and isinstance(data['started_at'], str):
                data['started_at'] = datetime.fromisoformat(data['started_at'])
            if data.get('lock_started_at') and isinstance(data['lock_started_at'], str):
                data['lock_started_at'] = datetime.fromisoformat(data['lock_started_at'])
            return TieData(**data)
        return None
    
    def set_current_tie(self, tie: Optional[TieData]):
        if hasattr(self, 'db'):
            if tie:
                self.db.current_tie_data = {
                    'penetrator_dbref': tie.penetrator_dbref,
                    'penetrator_name': tie.penetrator_name,
                    'receiver_dbref': tie.receiver_dbref,
                    'receiver_name': tie.receiver_name,
                    'knot_state': tie.knot_state.value,
                    'started_at': tie.started_at.isoformat(),
                    'lock_started_at': tie.lock_started_at.isoformat() if tie.lock_started_at else None,
                    'lock_duration': tie.lock_duration,
                }
            else:
                self.db.current_tie_data = None
    
    def is_tied(self) -> bool:
        tie = self.get_current_tie()
        return tie is not None and tie.knot_state in (KnotState.LOCKED, KnotState.SWELLING)
    
    def get_tied_partner(self):
        tie = self.get_current_tie()
        if not tie:
            return None
        my_dbref = self.dbref if hasattr(self, 'dbref') else str(id(self))
        partner_dbref = tie.receiver_dbref if tie.penetrator_dbref == my_dbref else tie.penetrator_dbref
        try:
            from evennia.utils.search import search_object
            results = search_object(partner_dbref)
            return results[0] if results else None
        except Exception:
            return None
    
    def initiate_knot(self, receiver, voluntary: bool = True) -> Tuple[bool, str]:
        if not self.can_knot():
            return False, "Cannot knot."
        if self.is_tied():
            return False, "Already tied."
        if hasattr(receiver, 'is_tied') and receiver.is_tied():
            return False, f"{receiver.key} is already tied."
        
        config = self.get_knot_config()
        tie = TieData(
            penetrator_dbref=self.dbref,
            penetrator_name=self.key,
            receiver_dbref=receiver.dbref,
            receiver_name=receiver.key,
            knot_state=KnotState.SWELLING,
            lock_duration=config.get_actual_lock_time(),
        )
        
        self.set_current_tie(tie)
        if hasattr(receiver, 'set_current_tie'):
            receiver.set_current_tie(tie)
        
        if HAS_DELAY:
            delay(config.swell_time, self._knot_lock, receiver)
        
        return True, f"{self.key}'s knot begins to swell inside {receiver.key}..."
    
    def _knot_lock(self, receiver):
        tie = self.get_current_tie()
        if not tie or tie.knot_state != KnotState.SWELLING:
            return
        
        tie.knot_state = KnotState.LOCKED
        tie.lock_started_at = datetime.now()
        self.set_current_tie(tie)
        if hasattr(receiver, 'set_current_tie'):
            receiver.set_current_tie(tie)
        
        if self.location:
            self.location.msg_contents(f"{self.key}'s knot swells fully, locking them inside {receiver.key}!")
        
        if HAS_DELAY:
            delay(tie.lock_duration, self._knot_deflate_check, receiver)
    
    def _knot_deflate_check(self, receiver):
        tie = self.get_current_tie()
        if not tie or tie.knot_state != KnotState.LOCKED:
            return
        if tie.time_remaining() <= 0:
            self._knot_start_deflate(receiver)
        elif HAS_DELAY:
            delay(min(tie.time_remaining(), 60), self._knot_deflate_check, receiver)
    
    def _knot_start_deflate(self, receiver):
        tie = self.get_current_tie()
        if not tie:
            return
        tie.knot_state = KnotState.DEFLATING
        self.set_current_tie(tie)
        if hasattr(receiver, 'set_current_tie'):
            receiver.set_current_tie(tie)
        if self.location:
            self.location.msg_contents(f"{self.key}'s knot begins to soften...")
        config = self.get_knot_config()
        if HAS_DELAY:
            delay(config.deflate_time, self._knot_release, receiver)
    
    def _knot_release(self, receiver):
        self.set_current_tie(None)
        if hasattr(receiver, 'set_current_tie'):
            receiver.set_current_tie(None)
        if self.location:
            self.location.msg_contents(f"{self.key}'s knot deflates, releasing {receiver.key}.")


# =============================================================================
# HEAT MIXIN
# =============================================================================

class HeatCycleMixin:
    """Mixin for heat cycles."""
    
    def get_heat_config(self) -> HeatConfig:
        body = self.get_body() if hasattr(self, 'get_body') else None
        if body:
            species = getattr(body, 'species_key', 'default')
            return HEAT_CONFIGS.get(species, HEAT_CONFIGS["default"])
        return HEAT_CONFIGS["default"]
    
    def get_heat_phase(self) -> HeatPhase:
        if hasattr(self, 'db'):
            phase = getattr(self.db, 'heat_phase', None)
            if phase:
                return HeatPhase(phase) if isinstance(phase, str) else phase
        return HeatPhase.NORMAL
    
    def set_heat_phase(self, phase: HeatPhase):
        if hasattr(self, 'db'):
            self.db.heat_phase = phase.value
            self.db.heat_phase_started = datetime.now().isoformat()
    
    def is_in_heat(self) -> bool:
        return self.get_heat_phase() == HeatPhase.HEAT
    
    def get_arousal_modifier(self) -> float:
        config = self.get_heat_config()
        phase = self.get_heat_phase()
        mods = {
            HeatPhase.NORMAL: 1.0,
            HeatPhase.PRE_HEAT: 1.5,
            HeatPhase.HEAT: config.heat_arousal_mod,
            HeatPhase.POST_HEAT: 1.2,
        }
        return mods.get(phase, 1.0)
    
    def trigger_heat(self):
        self.set_heat_phase(HeatPhase.HEAT)
        if self.location:
            self.location.msg_contents(f"{self.key} is clearly in heat, driven by powerful urges.")
    
    def should_seek_mate(self) -> bool:
        if not self.is_in_heat():
            return False
        return random() < self.get_heat_config().mate_seeking_chance


# =============================================================================
# LEASHING MIXIN
# =============================================================================

class LeashingMixin:
    """Mixin for leashing."""
    
    def get_leash_data(self) -> Optional[LeashData]:
        if hasattr(self, 'db') and self.db.leash_data:
            data = self.db.leash_data.copy()
            data['state'] = LeashState(data['state']) if isinstance(data['state'], str) else data['state']
            return LeashData(**data)
        return None
    
    def set_leash_data(self, data: Optional[LeashData]):
        if hasattr(self, 'db'):
            if data:
                self.db.leash_data = {
                    'holder_dbref': data.holder_dbref,
                    'holder_name': data.holder_name,
                    'leashed_dbref': data.leashed_dbref,
                    'leashed_name': data.leashed_name,
                    'state': data.state.value,
                    'length': data.length,
                    'strength': data.strength,
                    'is_locked': data.is_locked,
                }
            else:
                self.db.leash_data = None
    
    def get_holding_leash(self) -> Optional[LeashData]:
        if hasattr(self, 'db') and self.db.holding_leash_data:
            data = self.db.holding_leash_data.copy()
            data['state'] = LeashState(data['state']) if isinstance(data['state'], str) else data['state']
            return LeashData(**data)
        return None
    
    def set_holding_leash(self, data: Optional[LeashData]):
        if hasattr(self, 'db'):
            if data:
                self.db.holding_leash_data = {
                    'holder_dbref': data.holder_dbref,
                    'holder_name': data.holder_name,
                    'leashed_dbref': data.leashed_dbref,
                    'leashed_name': data.leashed_name,
                    'state': data.state.value,
                    'length': data.length,
                    'strength': data.strength,
                    'is_locked': data.is_locked,
                }
            else:
                self.db.holding_leash_data = None
    
    def is_leashed(self) -> bool:
        return self.get_leash_data() is not None
    
    def is_holding_leash(self) -> bool:
        return self.get_holding_leash() is not None
    
    def get_leash_holder(self):
        data = self.get_leash_data()
        if not data:
            return None
        try:
            from evennia.utils.search import search_object
            results = search_object(data.holder_dbref)
            return results[0] if results else None
        except Exception:
            return None
    
    def get_leashed_creature(self):
        data = self.get_holding_leash()
        if not data:
            return None
        try:
            from evennia.utils.search import search_object
            results = search_object(data.leashed_dbref)
            return results[0] if results else None
        except Exception:
            return None
    
    def leash(self, target, length: int = 3, strength: int = 50, locked: bool = False) -> Tuple[bool, str]:
        if self.is_holding_leash():
            return False, "Already holding a leash."
        if hasattr(target, 'is_leashed') and target.is_leashed():
            return False, f"{target.key} is already leashed."
        
        data = LeashData(
            holder_dbref=self.dbref,
            holder_name=self.key,
            leashed_dbref=target.dbref,
            leashed_name=target.key,
            length=length,
            strength=strength,
            is_locked=locked,
        )
        
        self.set_holding_leash(data)
        if hasattr(target, 'set_leash_data'):
            target.set_leash_data(data)
        
        return True, f"You attach a leash to {target.key}."
    
    def unleash(self, force: bool = False) -> Tuple[bool, str]:
        data = self.get_holding_leash()
        if not data:
            return False, "Not holding a leash."
        if data.is_locked and not force:
            return False, "The leash is locked."
        
        target = self.get_leashed_creature()
        self.set_holding_leash(None)
        if target and hasattr(target, 'set_leash_data'):
            target.set_leash_data(None)
        
        return True, "You release the leash."
    
    def break_free_from_leash(self, bonus: int = 0) -> Tuple[bool, str]:
        data = self.get_leash_data()
        if not data:
            return False, "Not leashed."
        if data.is_locked:
            return False, "The leash is locked."
        
        roll = randint(1, 100) + bonus
        if roll > data.strength:
            holder = self.get_leash_holder()
            self.set_leash_data(None)
            if holder and hasattr(holder, 'set_holding_leash'):
                holder.set_holding_leash(None)
            return True, "You wrench free!"
        return False, "Can't break free."


# =============================================================================
# COMBINED MIXIN
# =============================================================================

class FeralMechanicsMixin(KnottingMixin, HeatCycleMixin, LeashingMixin):
    """All feral mechanics combined."""
    
    def at_pre_move(self, destination, **kwargs):
        if hasattr(self, 'is_leashed') and self.is_leashed():
            holder = self.get_leash_holder()
            if holder and holder.location == self.location:
                self.msg(f"Your leash is held by {holder.key}.")
                return False
        if hasattr(super(), 'at_pre_move'):
            return super().at_pre_move(destination, **kwargs)
        return True
    
    def at_post_move(self, source_location, **kwargs):
        if hasattr(super(), 'at_post_move'):
            super().at_post_move(source_location, **kwargs)
        
        # Drag leashed creature
        if hasattr(self, 'is_holding_leash') and self.is_holding_leash():
            target = self.get_leashed_creature()
            if target and target.location != self.location:
                if target.location:
                    target.location.msg_contents(f"{self.key} tugs {target.key}'s leash.")
                target.move_to(self.location, quiet=True)
                self.location.msg_contents(f"{target.key} is dragged in by {self.key}.")
        
        # Drag knotted partner
        if hasattr(self, 'is_tied') and self.is_tied():
            partner = self.get_tied_partner()
            if partner and partner.location != self.location:
                if partner.location:
                    partner.location.msg_contents(f"{partner.key} is pulled along, locked to {self.key}.")
                partner.move_to(self.location, quiet=True)
                self.location.msg_contents(f"{partner.key} is dragged in, knotted to {self.key}.")


__all__ = [
    "KnotState", "KnotConfig", "TieData", "KNOT_CONFIGS",
    "HeatPhase", "HeatConfig", "HEAT_CONFIGS",
    "LeashState", "LeashData",
    "KnottingMixin", "HeatCycleMixin", "LeashingMixin",
    "FeralMechanicsMixin",
]
