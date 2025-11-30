"""
Public Use System
=================

Systems for making slaves available for public use including:
- Public use status and tracking
- Use sessions and history
- Degradation tracking
- Public furniture integration
- Cum tracking
"""

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any, Tuple
from enum import Enum
from datetime import datetime, timedelta
import random


# =============================================================================
# ENUMS
# =============================================================================

class PublicUseStatus(Enum):
    """Public use availability status."""
    PRIVATE = "private"           # Not available for public use
    RESTRICTED = "restricted"     # Owner permission required
    AVAILABLE = "available"       # Open for use
    FREE_USE = "free_use"         # Anyone, anytime, any hole
    BREEDING_STOCK = "breeding_stock"  # Available for breeding only
    ORAL_ONLY = "oral_only"       # Mouth only
    DISPLAY_ONLY = "display_only" # Look but don't touch


class UseType(Enum):
    """Types of use."""
    ORAL = "oral"
    VAGINAL = "vaginal"
    ANAL = "anal"
    MANUAL = "manual"             # Handjob/fingering
    BREAST = "breast"             # Titfuck/nursing
    FEET = "feet"
    FULL = "full"                 # All holes
    BREEDING = "breeding"         # Specifically for impregnation
    MILKING = "milking"
    DISPLAY = "display"           # Being looked at/shown off


class UsePosition(Enum):
    """Positions for use."""
    STANDING = "standing"
    KNEELING = "kneeling"
    BENT_OVER = "bent_over"
    ON_BACK = "on_back"
    ON_HANDS_AND_KNEES = "on_hands_and_knees"
    SPREADEAGLE = "spreadeagle"
    SUSPENDED = "suspended"
    STOCKS = "stocks"
    BREEDING_BENCH = "breeding_bench"
    GLORY_HOLE = "glory_hole"
    WALL_MOUNTED = "wall_mounted"
    TOILET = "toilet"             # Human toilet


class DegradationType(Enum):
    """Types of degradation."""
    VERBAL = "verbal"             # Insults, name-calling
    PHYSICAL = "physical"         # Slapping, spitting
    SEXUAL = "sexual"             # Rough use
    HUMILIATION = "humiliation"   # Public embarrassment
    OBJECTIFICATION = "objectification"  # Treated as furniture
    DEHUMANIZATION = "dehumanization"   # Treated as animal
    WASTE = "waste"               # Used as toilet


# =============================================================================
# CUM TRACKING
# =============================================================================

@dataclass
class CumLoad:
    """A single load of cum."""
    
    load_id: str = ""
    source_dbref: str = ""
    source_name: str = ""
    
    # Location
    location: str = ""            # Where: "mouth", "pussy", "ass", "face", "body", etc.
    
    # Amount
    volume_ml: int = 15
    
    # Timing
    deposited_at: Optional[datetime] = None
    
    # Properties
    is_swallowed: bool = False
    is_absorbed: bool = False     # Absorbed into body
    is_cleaned: bool = False
    
    # Potency (for breeding)
    potency: int = 50             # 0-100


@dataclass
class CumStatus:
    """Track cum on and in body."""
    
    # Internal cum
    mouth_loads: List[CumLoad] = field(default_factory=list)
    pussy_loads: List[CumLoad] = field(default_factory=list)
    ass_loads: List[CumLoad] = field(default_factory=list)
    stomach_loads: List[CumLoad] = field(default_factory=list)  # Swallowed
    womb_loads: List[CumLoad] = field(default_factory=list)     # Deep in womb
    
    # External cum
    face_loads: List[CumLoad] = field(default_factory=list)
    hair_loads: List[CumLoad] = field(default_factory=list)
    breast_loads: List[CumLoad] = field(default_factory=list)
    body_loads: List[CumLoad] = field(default_factory=list)
    
    # Totals
    total_loads_received: int = 0
    total_volume_ml: int = 0
    unique_sources: List[str] = field(default_factory=list)
    
    def add_load(
        self,
        location: str,
        source_dbref: str,
        source_name: str,
        volume: int = 15,
        potency: int = 50,
    ) -> str:
        """Add a cum load."""
        load = CumLoad(
            load_id=f"CUM-{datetime.now().strftime('%H%M%S')}-{random.randint(100, 999)}",
            source_dbref=source_dbref,
            source_name=source_name,
            location=location,
            volume_ml=volume,
            deposited_at=datetime.now(),
            potency=potency,
        )
        
        # Add to appropriate list
        location_map = {
            "mouth": self.mouth_loads,
            "pussy": self.pussy_loads,
            "vagina": self.pussy_loads,
            "ass": self.ass_loads,
            "anal": self.ass_loads,
            "womb": self.womb_loads,
            "face": self.face_loads,
            "hair": self.hair_loads,
            "breasts": self.breast_loads,
            "body": self.body_loads,
        }
        
        target_list = location_map.get(location.lower(), self.body_loads)
        target_list.append(load)
        
        self.total_loads_received += 1
        self.total_volume_ml += volume
        
        if source_dbref not in self.unique_sources:
            self.unique_sources.append(source_dbref)
        
        return f"Takes {source_name}'s load in/on {location}. ({volume}ml)"
    
    def swallow(self) -> Tuple[int, str]:
        """Swallow all cum in mouth."""
        if not self.mouth_loads:
            return 0, "Nothing to swallow."
        
        total = sum(l.volume_ml for l in self.mouth_loads)
        
        for load in self.mouth_loads:
            load.is_swallowed = True
            self.stomach_loads.append(load)
        
        self.mouth_loads.clear()
        
        return total, f"Swallows {total}ml of cum."
    
    def clean_external(self) -> Tuple[int, str]:
        """Clean all external cum."""
        total = 0
        
        for load_list in [self.face_loads, self.hair_loads, 
                          self.breast_loads, self.body_loads]:
            total += sum(l.volume_ml for l in load_list)
            for load in load_list:
                load.is_cleaned = True
            load_list.clear()
        
        if total == 0:
            return 0, "Already clean."
        
        return total, f"Cleaned {total}ml of cum."
    
    def get_internal_total(self) -> int:
        """Get total internal cum volume."""
        return (
            sum(l.volume_ml for l in self.pussy_loads) +
            sum(l.volume_ml for l in self.ass_loads) +
            sum(l.volume_ml for l in self.womb_loads) +
            sum(l.volume_ml for l in self.stomach_loads)
        )
    
    def get_external_total(self) -> int:
        """Get total external cum volume."""
        return (
            sum(l.volume_ml for l in self.face_loads) +
            sum(l.volume_ml for l in self.hair_loads) +
            sum(l.volume_ml for l in self.breast_loads) +
            sum(l.volume_ml for l in self.body_loads)
        )
    
    def get_description(self) -> str:
        """Get description of cum status."""
        parts = []
        
        # Internal
        if self.pussy_loads:
            vol = sum(l.volume_ml for l in self.pussy_loads)
            parts.append(f"pussy dripping with {vol}ml of cum ({len(self.pussy_loads)} loads)")
        
        if self.womb_loads:
            vol = sum(l.volume_ml for l in self.womb_loads)
            parts.append(f"womb full of {vol}ml")
        
        if self.ass_loads:
            vol = sum(l.volume_ml for l in self.ass_loads)
            parts.append(f"ass leaking {vol}ml ({len(self.ass_loads)} loads)")
        
        if self.mouth_loads:
            vol = sum(l.volume_ml for l in self.mouth_loads)
            parts.append(f"mouth holding {vol}ml")
        
        # External
        if self.face_loads:
            parts.append(f"face coated in cum")
        
        if self.hair_loads:
            parts.append(f"cum in hair")
        
        if self.breast_loads:
            parts.append(f"breasts glazed")
        
        if self.body_loads:
            parts.append(f"body splattered")
        
        if not parts:
            return "clean"
        
        return ", ".join(parts)
    
    def to_dict(self) -> dict:
        return {
            "total_loads_received": self.total_loads_received,
            "total_volume_ml": self.total_volume_ml,
            "unique_sources": self.unique_sources,
            "current_pussy": sum(l.volume_ml for l in self.pussy_loads),
            "current_ass": sum(l.volume_ml for l in self.ass_loads),
            "current_womb": sum(l.volume_ml for l in self.womb_loads),
        }


# =============================================================================
# USE SESSION
# =============================================================================

@dataclass
class UseSession:
    """Record of a single use session."""
    
    session_id: str = ""
    subject_dbref: str = ""
    subject_name: str = ""
    user_dbref: str = ""
    user_name: str = ""
    
    # Type
    use_type: UseType = UseType.FULL
    position: UsePosition = UsePosition.BENT_OVER
    
    # Location
    location_name: str = ""
    was_public: bool = True
    
    # Timing
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    duration_minutes: int = 0
    
    # Results
    orgasms_given: int = 0        # User's orgasms
    orgasms_received: int = 0     # Subject's orgasms (if allowed)
    cum_deposited_ml: int = 0
    cum_location: str = ""
    
    # Degradation
    degradation_applied: List[DegradationType] = field(default_factory=list)
    
    # Notes
    events: List[str] = field(default_factory=list)
    
    def add_event(self, event: str) -> None:
        """Add an event."""
        self.events.append(event)
    
    def get_summary(self) -> str:
        """Get session summary."""
        lines = [f"=== Use Session ==="]
        lines.append(f"Subject: {self.subject_name}")
        lines.append(f"User: {self.user_name}")
        lines.append(f"Type: {self.use_type.value}")
        lines.append(f"Position: {self.position.value}")
        lines.append(f"Duration: {self.duration_minutes} minutes")
        
        if self.cum_deposited_ml:
            lines.append(f"Cum: {self.cum_deposited_ml}ml in/on {self.cum_location}")
        
        return "\n".join(lines)


# =============================================================================
# PUBLIC USE RECORD
# =============================================================================

@dataclass
class PublicUseRecord:
    """Complete public use tracking for a subject."""
    
    subject_dbref: str = ""
    subject_name: str = ""
    
    # Status
    status: PublicUseStatus = PublicUseStatus.PRIVATE
    owner_dbref: str = ""
    owner_name: str = ""
    
    # Restrictions
    allowed_uses: List[UseType] = field(default_factory=list)
    forbidden_uses: List[UseType] = field(default_factory=list)
    requires_permission: bool = False
    
    # Current state
    is_currently_in_use: bool = False
    current_user: str = ""
    current_position: UsePosition = UsePosition.STANDING
    current_location: str = ""
    
    # Physical state
    cum_status: CumStatus = field(default_factory=CumStatus)
    
    # Stats
    times_used_today: int = 0
    times_used_total: int = 0
    unique_users: int = 0
    
    # Use history (recent)
    recent_sessions: List[UseSession] = field(default_factory=list)
    
    # Degradation tracking
    degradation_level: int = 0    # 0-100, how degraded they feel
    humiliation_level: int = 0    # 0-100
    
    # Records
    most_uses_single_day: int = 0
    longest_session_minutes: int = 0
    most_users_at_once: int = 0
    
    def set_status(self, status: PublicUseStatus) -> str:
        """Set public use status."""
        old = self.status
        self.status = status
        
        status_msgs = {
            PublicUseStatus.PRIVATE: f"{self.subject_name} is now private property.",
            PublicUseStatus.RESTRICTED: f"{self.subject_name} requires permission for use.",
            PublicUseStatus.AVAILABLE: f"{self.subject_name} is now available for public use.",
            PublicUseStatus.FREE_USE: f"{self.subject_name} is FREE USE - any hole, anyone, anytime.",
            PublicUseStatus.BREEDING_STOCK: f"{self.subject_name} is available for breeding.",
            PublicUseStatus.ORAL_ONLY: f"{self.subject_name}'s mouth is available.",
            PublicUseStatus.DISPLAY_ONLY: f"{self.subject_name} is on display - look but don't touch.",
        }
        
        return status_msgs.get(status, f"Status changed to {status.value}")
    
    def begin_use(
        self,
        user_dbref: str,
        user_name: str,
        use_type: UseType,
        position: UsePosition,
        location: str = "",
    ) -> Tuple[bool, str, Optional[UseSession]]:
        """Begin a use session."""
        
        # Check if available
        if self.status == PublicUseStatus.PRIVATE:
            return False, f"{self.subject_name} is private property.", None
        
        if self.is_currently_in_use:
            return False, f"{self.subject_name} is currently being used.", None
        
        # Check use type allowed
        if self.forbidden_uses and use_type in self.forbidden_uses:
            return False, f"{use_type.value} use is not allowed.", None
        
        if self.allowed_uses and use_type not in self.allowed_uses:
            return False, f"{use_type.value} use is not permitted.", None
        
        # Create session
        session = UseSession(
            session_id=f"USE-{datetime.now().strftime('%Y%m%d%H%M%S')}-{random.randint(100, 999)}",
            subject_dbref=self.subject_dbref,
            subject_name=self.subject_name,
            user_dbref=user_dbref,
            user_name=user_name,
            use_type=use_type,
            position=position,
            location_name=location,
            was_public=True,
            start_time=datetime.now(),
        )
        
        self.is_currently_in_use = True
        self.current_user = user_name
        self.current_position = position
        self.current_location = location
        
        # Generate start message
        position_msgs = {
            UsePosition.KNEELING: f"kneels before {user_name}",
            UsePosition.BENT_OVER: f"bends over for {user_name}",
            UsePosition.ON_HANDS_AND_KNEES: f"gets on all fours for {user_name}",
            UsePosition.SPREADEAGLE: f"spreads wide for {user_name}",
            UsePosition.STOCKS: f"is locked in the stocks for {user_name}",
            UsePosition.GLORY_HOLE: f"waits at the glory hole",
            UsePosition.BREEDING_BENCH: f"is strapped to the breeding bench for {user_name}",
        }
        
        msg = position_msgs.get(position, f"presents for {user_name}")
        
        return True, f"{self.subject_name} {msg}.", session
    
    def end_use(
        self,
        session: UseSession,
        cum_volume: int = 0,
        cum_location: str = "",
    ) -> str:
        """End a use session."""
        
        session.end_time = datetime.now()
        session.duration_minutes = int(
            (session.end_time - session.start_time).total_seconds() / 60
        )
        
        if cum_volume:
            session.cum_deposited_ml = cum_volume
            session.cum_location = cum_location
            self.cum_status.add_load(
                cum_location,
                session.user_dbref,
                session.user_name,
                cum_volume,
            )
        
        # Update stats
        self.times_used_today += 1
        self.times_used_total += 1
        
        if session.duration_minutes > self.longest_session_minutes:
            self.longest_session_minutes = session.duration_minutes
        
        # Add to history
        self.recent_sessions.append(session)
        if len(self.recent_sessions) > 20:
            self.recent_sessions.pop(0)
        
        # Clear current use
        self.is_currently_in_use = False
        self.current_user = ""
        
        return f"{session.user_name} finishes using {self.subject_name}."
    
    def apply_degradation(self, deg_type: DegradationType, intensity: int = 10) -> str:
        """Apply degradation."""
        self.degradation_level = min(100, self.degradation_level + intensity)
        
        if deg_type == DegradationType.HUMILIATION:
            self.humiliation_level = min(100, self.humiliation_level + intensity)
        
        deg_msgs = {
            DegradationType.VERBAL: "is called degrading names",
            DegradationType.PHYSICAL: "is slapped and spat on",
            DegradationType.SEXUAL: "is roughly used",
            DegradationType.HUMILIATION: "is publicly humiliated",
            DegradationType.OBJECTIFICATION: "is treated as furniture",
            DegradationType.DEHUMANIZATION: "is treated like an animal",
            DegradationType.WASTE: "is used as a toilet",
        }
        
        return f"{self.subject_name} {deg_msgs.get(deg_type, 'is degraded')}."
    
    def get_status_display(self) -> str:
        """Get status display."""
        lines = [f"=== Public Use Status: {self.subject_name} ==="]
        
        lines.append(f"Status: {self.status.value.upper()}")
        lines.append(f"Owner: {self.owner_name or 'None'}")
        
        if self.is_currently_in_use:
            lines.append(f"\nCURRENTLY IN USE by {self.current_user}")
            lines.append(f"Position: {self.current_position.value}")
        
        lines.append(f"\n--- Statistics ---")
        lines.append(f"Uses Today: {self.times_used_today}")
        lines.append(f"Total Uses: {self.times_used_total}")
        lines.append(f"Unique Users: {self.unique_users}")
        
        lines.append(f"\n--- Cum Status ---")
        lines.append(self.cum_status.get_description())
        lines.append(f"Total Received: {self.cum_status.total_loads_received} loads, {self.cum_status.total_volume_ml}ml")
        
        lines.append(f"\n--- Degradation ---")
        lines.append(f"Level: {self.degradation_level}/100")
        lines.append(f"Humiliation: {self.humiliation_level}/100")
        
        return "\n".join(lines)
    
    def to_dict(self) -> dict:
        return {
            "subject_dbref": self.subject_dbref,
            "subject_name": self.subject_name,
            "status": self.status.value,
            "owner_dbref": self.owner_dbref,
            "owner_name": self.owner_name,
            "is_currently_in_use": self.is_currently_in_use,
            "current_user": self.current_user,
            "times_used_today": self.times_used_today,
            "times_used_total": self.times_used_total,
            "unique_users": self.unique_users,
            "degradation_level": self.degradation_level,
            "humiliation_level": self.humiliation_level,
            "cum_status": self.cum_status.to_dict(),
        }
    
    @classmethod
    def from_dict(cls, data: dict) -> "PublicUseRecord":
        record = cls()
        for key, value in data.items():
            if key == "status":
                record.status = PublicUseStatus(value)
            elif key == "cum_status":
                record.cum_status = CumStatus()
                record.cum_status.total_loads_received = value.get("total_loads_received", 0)
                record.cum_status.total_volume_ml = value.get("total_volume_ml", 0)
            elif hasattr(record, key):
                setattr(record, key, value)
        return record


# =============================================================================
# PUBLIC USE MIXIN
# =============================================================================

class PublicUseMixin:
    """Mixin for characters that can be used publicly."""
    
    @property
    def public_use(self) -> PublicUseRecord:
        """Get public use record."""
        data = self.db.public_use_record
        if data:
            return PublicUseRecord.from_dict(data)
        return PublicUseRecord(subject_dbref=self.dbref, subject_name=self.key)
    
    @public_use.setter
    def public_use(self, record: PublicUseRecord) -> None:
        """Set public use record."""
        self.db.public_use_record = record.to_dict()
    
    def save_public_use(self, record: PublicUseRecord) -> None:
        """Save public use record."""
        self.db.public_use_record = record.to_dict()
    
    @property
    def is_free_use(self) -> bool:
        """Check if free use."""
        return self.public_use.status == PublicUseStatus.FREE_USE


__all__ = [
    "PublicUseStatus",
    "UseType",
    "UsePosition",
    "DegradationType",
    "CumLoad",
    "CumStatus",
    "UseSession",
    "PublicUseRecord",
    "PublicUseMixin",
]
