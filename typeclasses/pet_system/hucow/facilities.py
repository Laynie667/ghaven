"""
Farm Facilities System
======================

Farm infrastructure including:
- Milking parlors
- Breeding barns
- Stalls and pens
- Herd management
- Production tracking
"""

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any, Tuple
from enum import Enum
from datetime import datetime, timedelta
import random


# =============================================================================
# ENUMS
# =============================================================================

class FacilityType(Enum):
    """Types of farm facilities."""
    MILKING_PARLOR = "milking_parlor"
    BREEDING_BARN = "breeding_barn"
    HOLDING_PEN = "holding_pen"
    STALL_BLOCK = "stall_block"
    MEDICAL_BAY = "medical_bay"
    AUCTION_RING = "auction_ring"
    TRAINING_AREA = "training_area"
    PUNISHMENT_SHED = "punishment_shed"
    BULL_PEN = "bull_pen"
    NURSERY = "nursery"


class MilkingMethod(Enum):
    """Methods of milking."""
    MANUAL = "manual"             # By hand
    SUCTION = "suction"           # Pump machine
    VACUUM = "vacuum"             # Industrial
    MASSAGE = "massage"           # Pleasure-based
    FORCED = "forced"             # Rough extraction
    BREEDING = "breeding"         # Milked during breeding


class StallFeature(Enum):
    """Features a stall can have."""
    BASIC = "basic"               # Just space
    PADDED = "padded"             # Comfortable
    MILKING_STATION = "milking_station"
    BREEDING_FRAME = "breeding_frame"
    RESTRAINTS = "restraints"
    FEEDING_TROUGH = "feeding_trough"
    WATER_SUPPLY = "water_supply"
    WASTE_DRAIN = "waste_drain"
    HEATING = "heating"
    DISPLAY_WINDOW = "display_window"


# =============================================================================
# MILKING STATION
# =============================================================================

@dataclass
class MilkingStation:
    """Individual milking station."""
    
    station_id: str = ""
    name: str = "Station"
    
    # Equipment
    method: MilkingMethod = MilkingMethod.SUCTION
    suction_power: int = 50       # 0-100
    has_massage: bool = False
    has_stimulation: bool = False  # Sexual stimulation
    has_restraints: bool = True
    
    # Capacity
    is_occupied: bool = False
    current_hucow: str = ""       # dbref
    current_hucow_name: str = ""
    
    # Performance
    extraction_efficiency: float = 1.0  # Multiplier
    comfort_level: int = 50       # 0-100
    
    # Session tracking
    session_start: Optional[datetime] = None
    milk_extracted_ml: int = 0
    
    def attach_hucow(self, hucow_dbref: str, hucow_name: str) -> str:
        """Attach a hucow to the station."""
        if self.is_occupied:
            return f"Station already occupied by {self.current_hucow_name}."
        
        self.is_occupied = True
        self.current_hucow = hucow_dbref
        self.current_hucow_name = hucow_name
        self.session_start = datetime.now()
        self.milk_extracted_ml = 0
        
        return f"{hucow_name} attached to {self.name}."
    
    def release_hucow(self) -> Tuple[str, int]:
        """
        Release hucow from station.
        Returns (message, total_milk_extracted).
        """
        if not self.is_occupied:
            return "Station is empty.", 0
        
        name = self.current_hucow_name
        milk = self.milk_extracted_ml
        
        self.is_occupied = False
        self.current_hucow = ""
        self.current_hucow_name = ""
        self.session_start = None
        self.milk_extracted_ml = 0
        
        return f"{name} released. Total extracted: {milk}ml", milk
    
    def perform_milking(self, available_milk: int) -> Tuple[int, str]:
        """
        Perform milking cycle.
        Returns (milk_extracted, message).
        """
        if not self.is_occupied:
            return 0, "No hucow attached."
        
        # Calculate extraction
        base_extraction = min(available_milk, 100)  # Max 100ml per cycle
        
        # Apply efficiency
        extracted = int(base_extraction * self.extraction_efficiency)
        
        # Method modifiers
        method_mods = {
            MilkingMethod.MANUAL: 0.7,
            MilkingMethod.SUCTION: 1.0,
            MilkingMethod.VACUUM: 1.2,
            MilkingMethod.MASSAGE: 0.9,
            MilkingMethod.FORCED: 1.3,
        }
        extracted = int(extracted * method_mods.get(self.method, 1.0))
        
        # Stimulation bonus
        if self.has_stimulation:
            extracted = int(extracted * 1.15)
        
        self.milk_extracted_ml += extracted
        
        # Generate message
        method_msgs = {
            MilkingMethod.MANUAL: f"Hands work {self.current_hucow_name}'s teats",
            MilkingMethod.SUCTION: f"Pumps rhythmically drain {self.current_hucow_name}",
            MilkingMethod.VACUUM: f"Industrial suction pulls milk from {self.current_hucow_name}",
            MilkingMethod.MASSAGE: f"Gentle massage coaxes milk from {self.current_hucow_name}",
            MilkingMethod.FORCED: f"Rough extraction forces milk from {self.current_hucow_name}",
        }
        
        msg = method_msgs.get(self.method, f"Milking {self.current_hucow_name}")
        msg += f" - {extracted}ml extracted."
        
        return extracted, msg
    
    def to_dict(self) -> dict:
        return {
            "station_id": self.station_id,
            "name": self.name,
            "method": self.method.value,
            "suction_power": self.suction_power,
            "has_massage": self.has_massage,
            "has_stimulation": self.has_stimulation,
            "has_restraints": self.has_restraints,
            "is_occupied": self.is_occupied,
            "current_hucow": self.current_hucow,
            "current_hucow_name": self.current_hucow_name,
            "extraction_efficiency": self.extraction_efficiency,
            "comfort_level": self.comfort_level,
            "session_start": self.session_start.isoformat() if self.session_start else None,
            "milk_extracted_ml": self.milk_extracted_ml,
        }
    
    @classmethod
    def from_dict(cls, data: dict) -> "MilkingStation":
        station = cls()
        for key, value in data.items():
            if key == "method":
                station.method = MilkingMethod(value)
            elif key == "session_start" and value:
                station.session_start = datetime.fromisoformat(value)
            elif hasattr(station, key):
                setattr(station, key, value)
        return station


# =============================================================================
# MILKING PARLOR
# =============================================================================

@dataclass
class MilkingParlor:
    """Complete milking facility."""
    
    parlor_id: str = ""
    name: str = "Milking Parlor"
    
    # Stations
    stations: Dict[str, MilkingStation] = field(default_factory=dict)
    max_stations: int = 10
    
    # Storage
    milk_storage_liters: float = 0.0
    max_storage_liters: float = 1000.0
    
    # Staff
    assigned_milkers: List[str] = field(default_factory=list)
    
    # Schedule
    milking_times: List[str] = field(default_factory=list)
    # e.g., ["06:00", "12:00", "18:00"]
    
    # Records
    total_milk_today_liters: float = 0.0
    total_milk_all_time_liters: float = 0.0
    hucows_milked_today: int = 0
    
    def add_station(self, station: MilkingStation) -> str:
        """Add a milking station."""
        if len(self.stations) >= self.max_stations:
            return "Parlor at maximum capacity."
        
        self.stations[station.station_id] = station
        return f"Station {station.name} added."
    
    def find_available_station(self) -> Optional[MilkingStation]:
        """Find an unoccupied station."""
        for station in self.stations.values():
            if not station.is_occupied:
                return station
        return None
    
    def get_occupied_count(self) -> int:
        """Get number of occupied stations."""
        return sum(1 for s in self.stations.values() if s.is_occupied)
    
    def store_milk(self, amount_ml: int) -> str:
        """Store extracted milk."""
        liters = amount_ml / 1000
        
        if self.milk_storage_liters + liters > self.max_storage_liters:
            overflow = (self.milk_storage_liters + liters) - self.max_storage_liters
            self.milk_storage_liters = self.max_storage_liters
            return f"Storage full! {overflow:.2f}L overflow lost."
        
        self.milk_storage_liters += liters
        self.total_milk_today_liters += liters
        self.total_milk_all_time_liters += liters
        
        return f"Stored {liters:.2f}L. Total: {self.milk_storage_liters:.2f}L"
    
    def sell_milk(self, liters: float, price_per_liter: float = 5.0) -> Tuple[float, str]:
        """
        Sell milk from storage.
        Returns (gold_earned, message).
        """
        if liters > self.milk_storage_liters:
            liters = self.milk_storage_liters
        
        self.milk_storage_liters -= liters
        gold = liters * price_per_liter
        
        return gold, f"Sold {liters:.2f}L for {gold:.0f} gold."
    
    def get_status_display(self) -> str:
        """Get parlor status display."""
        lines = [f"=== {self.name} ==="]
        
        occupied = self.get_occupied_count()
        lines.append(f"Stations: {occupied}/{len(self.stations)} occupied")
        
        lines.append(f"\nStorage: {self.milk_storage_liters:.1f}/{self.max_storage_liters:.0f}L")
        lines.append(f"Today: {self.total_milk_today_liters:.1f}L")
        lines.append(f"All Time: {self.total_milk_all_time_liters:.1f}L")
        
        if self.milking_times:
            lines.append(f"\nSchedule: {', '.join(self.milking_times)}")
        
        # List occupied stations
        occupied_list = [s for s in self.stations.values() if s.is_occupied]
        if occupied_list:
            lines.append("\nCurrently Milking:")
            for station in occupied_list:
                lines.append(f"  {station.name}: {station.current_hucow_name}")
        
        return "\n".join(lines)
    
    def to_dict(self) -> dict:
        return {
            "parlor_id": self.parlor_id,
            "name": self.name,
            "stations": {k: v.to_dict() for k, v in self.stations.items()},
            "max_stations": self.max_stations,
            "milk_storage_liters": self.milk_storage_liters,
            "max_storage_liters": self.max_storage_liters,
            "assigned_milkers": self.assigned_milkers,
            "milking_times": self.milking_times,
            "total_milk_today_liters": self.total_milk_today_liters,
            "total_milk_all_time_liters": self.total_milk_all_time_liters,
            "hucows_milked_today": self.hucows_milked_today,
        }
    
    @classmethod
    def from_dict(cls, data: dict) -> "MilkingParlor":
        parlor = cls()
        for key, value in data.items():
            if key == "stations":
                parlor.stations = {k: MilkingStation.from_dict(v) for k, v in value.items()}
            elif hasattr(parlor, key):
                setattr(parlor, key, value)
        return parlor


# =============================================================================
# BREEDING PEN
# =============================================================================

@dataclass
class BreedingPen:
    """Pen for breeding sessions."""
    
    pen_id: str = ""
    name: str = "Breeding Pen"
    
    # Configuration
    has_breeding_frame: bool = True
    has_padding: bool = True
    has_restraints: bool = True
    allows_observation: bool = True
    
    # Current session
    is_occupied: bool = False
    current_hucow: str = ""
    current_hucow_name: str = ""
    current_bull: str = ""
    current_bull_name: str = ""
    session_start: Optional[datetime] = None
    
    # Records
    breedings_performed: int = 0
    successful_conceptions: int = 0
    
    def begin_session(
        self,
        hucow_dbref: str,
        hucow_name: str,
        bull_dbref: str,
        bull_name: str,
    ) -> str:
        """Begin a breeding session."""
        if self.is_occupied:
            return f"Pen occupied by {self.current_hucow_name}."
        
        self.is_occupied = True
        self.current_hucow = hucow_dbref
        self.current_hucow_name = hucow_name
        self.current_bull = bull_dbref
        self.current_bull_name = bull_name
        self.session_start = datetime.now()
        
        return f"Breeding session begun: {bull_name} with {hucow_name}"
    
    def end_session(self, conception: bool = False) -> str:
        """End breeding session."""
        if not self.is_occupied:
            return "No session in progress."
        
        self.breedings_performed += 1
        if conception:
            self.successful_conceptions += 1
        
        bull = self.current_bull_name
        hucow = self.current_hucow_name
        
        self.is_occupied = False
        self.current_hucow = ""
        self.current_hucow_name = ""
        self.current_bull = ""
        self.current_bull_name = ""
        self.session_start = None
        
        if conception:
            return f"Session complete. {hucow} successfully bred by {bull}!"
        return f"Session complete. No conception this time."
    
    def to_dict(self) -> dict:
        return {
            "pen_id": self.pen_id,
            "name": self.name,
            "has_breeding_frame": self.has_breeding_frame,
            "has_padding": self.has_padding,
            "has_restraints": self.has_restraints,
            "allows_observation": self.allows_observation,
            "is_occupied": self.is_occupied,
            "current_hucow": self.current_hucow,
            "current_hucow_name": self.current_hucow_name,
            "current_bull": self.current_bull,
            "current_bull_name": self.current_bull_name,
            "session_start": self.session_start.isoformat() if self.session_start else None,
            "breedings_performed": self.breedings_performed,
            "successful_conceptions": self.successful_conceptions,
        }
    
    @classmethod
    def from_dict(cls, data: dict) -> "BreedingPen":
        pen = cls()
        for key, value in data.items():
            if key == "session_start" and value:
                pen.session_start = datetime.fromisoformat(value)
            elif hasattr(pen, key):
                setattr(pen, key, value)
        return pen


# =============================================================================
# BREEDING BARN
# =============================================================================

@dataclass
class BreedingBarn:
    """Facility for organized breeding."""
    
    barn_id: str = ""
    name: str = "Breeding Barn"
    
    # Pens
    pens: Dict[str, BreedingPen] = field(default_factory=dict)
    max_pens: int = 5
    
    # Resident bulls
    resident_bulls: List[str] = field(default_factory=list)
    
    # Queue
    breeding_queue: List[Tuple[str, str]] = field(default_factory=list)
    # List of (hucow_dbref, preferred_bull_dbref)
    
    # Records
    total_breedings: int = 0
    total_conceptions: int = 0
    
    def add_pen(self, pen: BreedingPen) -> str:
        """Add a breeding pen."""
        if len(self.pens) >= self.max_pens:
            return "Barn at capacity."
        
        self.pens[pen.pen_id] = pen
        return f"Pen {pen.name} added."
    
    def add_to_queue(self, hucow_dbref: str, bull_dbref: str = "") -> str:
        """Add hucow to breeding queue."""
        self.breeding_queue.append((hucow_dbref, bull_dbref))
        return f"Added to breeding queue. Position: {len(self.breeding_queue)}"
    
    def find_available_pen(self) -> Optional[BreedingPen]:
        """Find an unoccupied pen."""
        for pen in self.pens.values():
            if not pen.is_occupied:
                return pen
        return None
    
    def record_breeding(self, conception: bool) -> None:
        """Record a breeding result."""
        self.total_breedings += 1
        if conception:
            self.total_conceptions += 1
    
    @property
    def conception_rate(self) -> float:
        """Get overall conception rate."""
        if self.total_breedings == 0:
            return 0.0
        return (self.total_conceptions / self.total_breedings) * 100
    
    def get_status_display(self) -> str:
        """Get barn status."""
        lines = [f"=== {self.name} ==="]
        
        occupied = sum(1 for p in self.pens.values() if p.is_occupied)
        lines.append(f"Pens: {occupied}/{len(self.pens)} in use")
        
        lines.append(f"\nTotal Breedings: {self.total_breedings}")
        lines.append(f"Conceptions: {self.total_conceptions}")
        lines.append(f"Success Rate: {self.conception_rate:.1f}%")
        
        lines.append(f"\nQueue: {len(self.breeding_queue)} waiting")
        
        if self.resident_bulls:
            lines.append(f"\nResident Bulls: {len(self.resident_bulls)}")
        
        # Active sessions
        active = [p for p in self.pens.values() if p.is_occupied]
        if active:
            lines.append("\nActive Sessions:")
            for pen in active:
                lines.append(f"  {pen.name}: {pen.current_bull_name} × {pen.current_hucow_name}")
        
        return "\n".join(lines)
    
    def to_dict(self) -> dict:
        return {
            "barn_id": self.barn_id,
            "name": self.name,
            "pens": {k: v.to_dict() for k, v in self.pens.items()},
            "max_pens": self.max_pens,
            "resident_bulls": self.resident_bulls,
            "breeding_queue": self.breeding_queue,
            "total_breedings": self.total_breedings,
            "total_conceptions": self.total_conceptions,
        }
    
    @classmethod
    def from_dict(cls, data: dict) -> "BreedingBarn":
        barn = cls()
        for key, value in data.items():
            if key == "pens":
                barn.pens = {k: BreedingPen.from_dict(v) for k, v in value.items()}
            elif hasattr(barn, key):
                setattr(barn, key, value)
        return barn


# =============================================================================
# HERD
# =============================================================================

@dataclass
class Herd:
    """Group of hucows managed together."""
    
    herd_id: str = ""
    name: str = "Unnamed Herd"
    
    # Members
    members: List[str] = field(default_factory=list)  # hucow dbrefs
    max_size: int = 20
    
    # Assigned bull
    assigned_bull: str = ""
    assigned_bull_name: str = ""
    
    # Production
    daily_quota_liters: float = 50.0
    current_production_liters: float = 0.0
    
    # Quality
    average_grade: str = "standard"
    
    def add_member(self, hucow_dbref: str) -> str:
        """Add a hucow to the herd."""
        if len(self.members) >= self.max_size:
            return "Herd at maximum size."
        
        if hucow_dbref in self.members:
            return "Already in this herd."
        
        self.members.append(hucow_dbref)
        return f"Added to herd {self.name}."
    
    def remove_member(self, hucow_dbref: str) -> str:
        """Remove a hucow from the herd."""
        if hucow_dbref not in self.members:
            return "Not in this herd."
        
        self.members.remove(hucow_dbref)
        return f"Removed from herd {self.name}."
    
    def assign_bull(self, bull_dbref: str, bull_name: str) -> str:
        """Assign a bull to this herd."""
        self.assigned_bull = bull_dbref
        self.assigned_bull_name = bull_name
        return f"Bull {bull_name} assigned to herd {self.name}."
    
    @property
    def quota_progress(self) -> float:
        """Get progress toward daily quota."""
        if self.daily_quota_liters == 0:
            return 100.0
        return (self.current_production_liters / self.daily_quota_liters) * 100
    
    def to_dict(self) -> dict:
        return {
            "herd_id": self.herd_id,
            "name": self.name,
            "members": self.members,
            "max_size": self.max_size,
            "assigned_bull": self.assigned_bull,
            "assigned_bull_name": self.assigned_bull_name,
            "daily_quota_liters": self.daily_quota_liters,
            "current_production_liters": self.current_production_liters,
            "average_grade": self.average_grade,
        }
    
    @classmethod
    def from_dict(cls, data: dict) -> "Herd":
        herd = cls()
        for key, value in data.items():
            if hasattr(herd, key):
                setattr(herd, key, value)
        return herd


# =============================================================================
# FARM
# =============================================================================

@dataclass
class Farm:
    """Complete farm facility."""
    
    farm_id: str = ""
    name: str = "Unnamed Farm"
    
    # Owner
    owner_dbref: str = ""
    owner_name: str = ""
    
    # Facilities
    milking_parlor: Optional[MilkingParlor] = None
    breeding_barn: Optional[BreedingBarn] = None
    
    # Herds
    herds: Dict[str, Herd] = field(default_factory=dict)
    
    # Bulls
    bulls: List[str] = field(default_factory=list)
    
    # Staff
    staff: Dict[str, str] = field(default_factory=dict)
    # dbref: role
    
    # Finance
    gold_balance: int = 0
    daily_expenses: int = 0
    daily_income: int = 0
    
    # Records
    total_hucows: int = 0
    total_bulls: int = 0
    
    def get_all_hucows(self) -> List[str]:
        """Get all hucow dbrefs."""
        hucows = []
        for herd in self.herds.values():
            hucows.extend(herd.members)
        return hucows
    
    def get_status_display(self) -> str:
        """Get farm status display."""
        lines = [f"=== {self.name} ==="]
        lines.append(f"Owner: {self.owner_name}")
        
        lines.append(f"\n--- Population ---")
        lines.append(f"Hucows: {len(self.get_all_hucows())}")
        lines.append(f"Bulls: {len(self.bulls)}")
        lines.append(f"Herds: {len(self.herds)}")
        
        if self.milking_parlor:
            lines.append(f"\n--- Milking ---")
            lines.append(f"Storage: {self.milking_parlor.milk_storage_liters:.1f}L")
            lines.append(f"Today: {self.milking_parlor.total_milk_today_liters:.1f}L")
        
        if self.breeding_barn:
            lines.append(f"\n--- Breeding ---")
            lines.append(f"Conception Rate: {self.breeding_barn.conception_rate:.1f}%")
        
        lines.append(f"\n--- Finance ---")
        lines.append(f"Balance: {self.gold_balance} gold")
        
        return "\n".join(lines)
    
    def to_dict(self) -> dict:
        return {
            "farm_id": self.farm_id,
            "name": self.name,
            "owner_dbref": self.owner_dbref,
            "owner_name": self.owner_name,
            "milking_parlor": self.milking_parlor.to_dict() if self.milking_parlor else None,
            "breeding_barn": self.breeding_barn.to_dict() if self.breeding_barn else None,
            "herds": {k: v.to_dict() for k, v in self.herds.items()},
            "bulls": self.bulls,
            "staff": self.staff,
            "gold_balance": self.gold_balance,
            "daily_expenses": self.daily_expenses,
            "daily_income": self.daily_income,
            "total_hucows": self.total_hucows,
            "total_bulls": self.total_bulls,
        }
    
    @classmethod
    def from_dict(cls, data: dict) -> "Farm":
        farm = cls()
        for key, value in data.items():
            if key == "milking_parlor" and value:
                farm.milking_parlor = MilkingParlor.from_dict(value)
            elif key == "breeding_barn" and value:
                farm.breeding_barn = BreedingBarn.from_dict(value)
            elif key == "herds":
                farm.herds = {k: Herd.from_dict(v) for k, v in value.items()}
            elif hasattr(farm, key):
                setattr(farm, key, value)
        return farm


# =============================================================================
# FACTORY FUNCTIONS
# =============================================================================

def create_standard_milking_parlor(name: str = "Main Parlor") -> MilkingParlor:
    """Create a standard milking parlor with stations."""
    parlor = MilkingParlor(
        parlor_id=f"MP-{datetime.now().strftime('%Y%m%d%H%M%S')}-{random.randint(100, 999)}",
        name=name,
        milking_times=["06:00", "12:00", "18:00"],
    )
    
    # Add stations
    for i in range(6):
        station = MilkingStation(
            station_id=f"MS-{i+1}",
            name=f"Station {i+1}",
            method=MilkingMethod.SUCTION,
            suction_power=60,
            has_restraints=True,
        )
        parlor.add_station(station)
    
    return parlor


def create_standard_breeding_barn(name: str = "Breeding Barn") -> BreedingBarn:
    """Create a standard breeding barn with pens."""
    barn = BreedingBarn(
        barn_id=f"BB-{datetime.now().strftime('%Y%m%d%H%M%S')}-{random.randint(100, 999)}",
        name=name,
    )
    
    # Add pens
    for i in range(3):
        pen = BreedingPen(
            pen_id=f"BP-{i+1}",
            name=f"Pen {i+1}",
            has_breeding_frame=True,
            has_padding=True,
            has_restraints=True,
        )
        barn.add_pen(pen)
    
    return barn


def create_standard_farm(name: str, owner_dbref: str, owner_name: str) -> Farm:
    """Create a complete farm with all facilities."""
    farm = Farm(
        farm_id=f"FARM-{datetime.now().strftime('%Y%m%d%H%M%S')}-{random.randint(100, 999)}",
        name=name,
        owner_dbref=owner_dbref,
        owner_name=owner_name,
        milking_parlor=create_standard_milking_parlor(),
        breeding_barn=create_standard_breeding_barn(),
    )
    
    # Create default herd
    default_herd = Herd(
        herd_id=f"HERD-001",
        name="Main Herd",
    )
    farm.herds[default_herd.herd_id] = default_herd
    
    return farm


__all__ = [
    "FacilityType",
    "MilkingMethod",
    "StallFeature",
    "MilkingStation",
    "MilkingParlor",
    "BreedingPen",
    "BreedingBarn",
    "Herd",
    "Farm",
    "create_standard_milking_parlor",
    "create_standard_breeding_barn",
    "create_standard_farm",
]
