"""
Facilities System
=================

Physical locations for slave processing and training:
- Intake offices
- Holding kennels
- Examination rooms
- Breaking cells
- Training areas
- Auction blocks
"""

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any, Tuple
from enum import Enum
from datetime import datetime
import random


# =============================================================================
# ENUMS
# =============================================================================

class FacilityType(Enum):
    """Types of facilities."""
    INTAKE_OFFICE = "intake_office"
    HOLDING_KENNEL = "holding_kennel"
    EXAM_ROOM = "exam_room"
    TESTING_CHAMBER = "testing_chamber"
    MARKING_STATION = "marking_station"
    BREAKING_CELL = "breaking_cell"
    TRAINING_ROOM = "training_room"
    AUCTION_BLOCK = "auction_block"
    STORAGE = "storage"
    BREEDING_STALL = "breeding_stall"
    MILKING_PARLOR = "milking_parlor"
    STABLE = "stable"


class CellType(Enum):
    """Types of holding cells."""
    STANDARD = "standard"
    ISOLATION = "isolation"
    PUNISHMENT = "punishment"
    LUXURY = "luxury"
    KENNEL = "kennel"
    CAGE = "cage"
    PIT = "pit"


class RoomStatus(Enum):
    """Status of a room/cell."""
    AVAILABLE = "available"
    OCCUPIED = "occupied"
    RESERVED = "reserved"
    MAINTENANCE = "maintenance"
    LOCKED = "locked"


# =============================================================================
# CELL/ROOM
# =============================================================================

@dataclass
class HoldingCell:
    """A cell for holding slaves."""
    cell_id: str
    name: str
    cell_type: CellType = CellType.STANDARD
    
    # Capacity
    capacity: int = 1
    current_occupants: List[str] = field(default_factory=list)
    
    # Features
    has_bed: bool = True
    has_toilet: bool = True
    has_window: bool = False
    has_chains: bool = False
    has_stocks: bool = False
    
    # Conditions
    comfort_level: int = 50       # 0-100
    privacy_level: int = 50       # 0-100
    temperature: str = "normal"
    lighting: str = "dim"
    
    # Security
    lock_difficulty: int = 50     # DC to pick
    escape_difficulty: int = 60   # DC to escape
    
    # Status
    status: RoomStatus = RoomStatus.AVAILABLE
    
    # Location
    facility_id: str = ""
    
    @property
    def is_available(self) -> bool:
        """Check if cell has space."""
        return len(self.current_occupants) < self.capacity
    
    def add_occupant(self, dbref: str) -> Tuple[bool, str]:
        """Add an occupant to the cell."""
        if not self.is_available:
            return False, "Cell is full."
        
        self.current_occupants.append(dbref)
        if len(self.current_occupants) >= self.capacity:
            self.status = RoomStatus.OCCUPIED
        
        return True, f"Added to {self.name}."
    
    def remove_occupant(self, dbref: str) -> Tuple[bool, str]:
        """Remove an occupant."""
        if dbref not in self.current_occupants:
            return False, "Not in this cell."
        
        self.current_occupants.remove(dbref)
        if len(self.current_occupants) < self.capacity:
            self.status = RoomStatus.AVAILABLE
        
        return True, f"Removed from {self.name}."
    
    def get_description(self) -> str:
        """Get cell description."""
        features = []
        if self.has_bed:
            features.append("a small bed")
        else:
            features.append("a bare floor")
        if self.has_chains:
            features.append("chains on the wall")
        if self.has_stocks:
            features.append("wooden stocks")
        
        desc = f"A {self.cell_type.value} cell with {', '.join(features)}. "
        desc += f"The lighting is {self.lighting} and the temperature is {self.temperature}."
        
        return desc
    
    def to_dict(self) -> dict:
        return {
            "cell_id": self.cell_id,
            "name": self.name,
            "cell_type": self.cell_type.value,
            "capacity": self.capacity,
            "current_occupants": self.current_occupants,
            "has_bed": self.has_bed,
            "has_toilet": self.has_toilet,
            "has_window": self.has_window,
            "has_chains": self.has_chains,
            "has_stocks": self.has_stocks,
            "comfort_level": self.comfort_level,
            "privacy_level": self.privacy_level,
            "temperature": self.temperature,
            "lighting": self.lighting,
            "lock_difficulty": self.lock_difficulty,
            "escape_difficulty": self.escape_difficulty,
            "status": self.status.value,
            "facility_id": self.facility_id,
        }
    
    @classmethod
    def from_dict(cls, data: dict) -> "HoldingCell":
        cell = cls(
            cell_id=data["cell_id"],
            name=data["name"],
        )
        cell.cell_type = CellType(data.get("cell_type", "standard"))
        cell.capacity = data.get("capacity", 1)
        cell.current_occupants = data.get("current_occupants", [])
        cell.has_bed = data.get("has_bed", True)
        cell.has_toilet = data.get("has_toilet", True)
        cell.has_window = data.get("has_window", False)
        cell.has_chains = data.get("has_chains", False)
        cell.has_stocks = data.get("has_stocks", False)
        cell.comfort_level = data.get("comfort_level", 50)
        cell.privacy_level = data.get("privacy_level", 50)
        cell.temperature = data.get("temperature", "normal")
        cell.lighting = data.get("lighting", "dim")
        cell.lock_difficulty = data.get("lock_difficulty", 50)
        cell.escape_difficulty = data.get("escape_difficulty", 60)
        cell.status = RoomStatus(data.get("status", "available"))
        cell.facility_id = data.get("facility_id", "")
        return cell


# =============================================================================
# ROOM PRESETS
# =============================================================================

def create_standard_cell(cell_id: str, name: str) -> HoldingCell:
    """Create a standard holding cell."""
    return HoldingCell(
        cell_id=cell_id,
        name=name,
        cell_type=CellType.STANDARD,
        capacity=1,
        has_bed=True,
        has_toilet=True,
        comfort_level=40,
    )


def create_kennel(cell_id: str, name: str) -> HoldingCell:
    """Create a kennel cage."""
    return HoldingCell(
        cell_id=cell_id,
        name=name,
        cell_type=CellType.KENNEL,
        capacity=1,
        has_bed=False,
        has_toilet=False,
        comfort_level=20,
        privacy_level=10,
    )


def create_isolation_cell(cell_id: str, name: str) -> HoldingCell:
    """Create an isolation cell."""
    return HoldingCell(
        cell_id=cell_id,
        name=name,
        cell_type=CellType.ISOLATION,
        capacity=1,
        has_bed=True,
        has_toilet=True,
        has_window=False,
        comfort_level=30,
        privacy_level=100,
        lighting="dark",
        escape_difficulty=80,
    )


def create_punishment_cell(cell_id: str, name: str) -> HoldingCell:
    """Create a punishment cell."""
    return HoldingCell(
        cell_id=cell_id,
        name=name,
        cell_type=CellType.PUNISHMENT,
        capacity=1,
        has_bed=False,
        has_toilet=False,
        has_chains=True,
        has_stocks=True,
        comfort_level=5,
        privacy_level=0,
        temperature="cold",
        lighting="harsh",
        escape_difficulty=90,
    )


def create_luxury_cell(cell_id: str, name: str) -> HoldingCell:
    """Create a luxury holding room."""
    return HoldingCell(
        cell_id=cell_id,
        name=name,
        cell_type=CellType.LUXURY,
        capacity=1,
        has_bed=True,
        has_toilet=True,
        has_window=True,
        comfort_level=80,
        privacy_level=70,
        temperature="comfortable",
        lighting="soft",
        escape_difficulty=70,
    )


def create_group_cage(cell_id: str, name: str) -> HoldingCell:
    """Create a large group cage."""
    return HoldingCell(
        cell_id=cell_id,
        name=name,
        cell_type=CellType.CAGE,
        capacity=5,
        has_bed=False,
        has_toilet=True,
        comfort_level=25,
        privacy_level=5,
        escape_difficulty=65,
    )


# =============================================================================
# EXAMINATION ROOM
# =============================================================================

@dataclass
class ExaminationRoom:
    """Room for slave examinations."""
    room_id: str
    name: str
    
    # Equipment
    has_exam_table: bool = True
    has_restraints: bool = True
    has_stirrups: bool = False
    has_measuring_tools: bool = True
    has_medical_equipment: bool = False
    
    # Specialized
    specialized_for: List[str] = field(default_factory=list)
    # e.g., ["physical", "sexual", "medical"]
    
    # Status
    status: RoomStatus = RoomStatus.AVAILABLE
    current_subject: str = ""
    current_examiner: str = ""
    
    # Location
    facility_id: str = ""
    
    def begin_exam(self, subject_dbref: str, examiner_name: str) -> str:
        """Begin an examination."""
        self.status = RoomStatus.OCCUPIED
        self.current_subject = subject_dbref
        self.current_examiner = examiner_name
        return f"Examination beginning in {self.name}."
    
    def end_exam(self) -> str:
        """End the examination."""
        self.status = RoomStatus.AVAILABLE
        self.current_subject = ""
        self.current_examiner = ""
        return f"Examination in {self.name} concluded."
    
    def get_description(self) -> str:
        """Get room description."""
        features = []
        if self.has_exam_table:
            features.append("an examination table")
        if self.has_restraints:
            features.append("leather restraints")
        if self.has_stirrups:
            features.append("stirrups for positioning")
        if self.has_medical_equipment:
            features.append("medical instruments")
        
        desc = f"An examination room equipped with {', '.join(features)}. "
        desc += "The room is clinical and sterile."
        
        return desc
    
    def to_dict(self) -> dict:
        return {
            "room_id": self.room_id,
            "name": self.name,
            "has_exam_table": self.has_exam_table,
            "has_restraints": self.has_restraints,
            "has_stirrups": self.has_stirrups,
            "has_measuring_tools": self.has_measuring_tools,
            "has_medical_equipment": self.has_medical_equipment,
            "specialized_for": self.specialized_for,
            "status": self.status.value,
            "current_subject": self.current_subject,
            "current_examiner": self.current_examiner,
            "facility_id": self.facility_id,
        }


# =============================================================================
# TRAINING ROOM
# =============================================================================

@dataclass
class TrainingRoom:
    """Room for slave training."""
    room_id: str
    name: str
    
    # Type
    training_types: List[str] = field(default_factory=list)
    # e.g., ["obedience", "sexual", "domestic", "pony"]
    
    # Equipment
    equipment: List[str] = field(default_factory=list)
    # e.g., ["training_post", "treadmill", "mirrors", "punishment_bench"]
    
    # Capacity
    capacity: int = 1
    current_trainees: List[str] = field(default_factory=list)
    
    # Assigned trainer
    assigned_trainer: str = ""
    
    # Status
    status: RoomStatus = RoomStatus.AVAILABLE
    
    # Location
    facility_id: str = ""
    
    def to_dict(self) -> dict:
        return {
            "room_id": self.room_id,
            "name": self.name,
            "training_types": self.training_types,
            "equipment": self.equipment,
            "capacity": self.capacity,
            "current_trainees": self.current_trainees,
            "assigned_trainer": self.assigned_trainer,
            "status": self.status.value,
            "facility_id": self.facility_id,
        }


# =============================================================================
# BREAKING CELL
# =============================================================================

@dataclass
class BreakingCell:
    """Specialized cell for breaking resistant slaves."""
    cell_id: str
    name: str
    
    # Breaking equipment
    has_suspension_rig: bool = True
    has_restraint_frame: bool = True
    has_sensory_deprivation: bool = False
    has_punishment_tools: bool = True
    has_pleasure_devices: bool = False
    
    # Conditions (controllable)
    temperature_control: bool = True
    lighting_control: bool = True
    sound_control: bool = False
    
    # Current settings
    current_temperature: str = "cold"
    current_lighting: str = "harsh"
    current_sound: str = "silent"
    
    # Status
    status: RoomStatus = RoomStatus.AVAILABLE
    current_subject: str = ""
    current_breaker: str = ""
    
    # Breaking progress tracking
    hours_in_cell: int = 0
    sessions_completed: int = 0
    
    # Location
    facility_id: str = ""
    
    def begin_session(self, subject_dbref: str, breaker_name: str) -> str:
        """Begin a breaking session."""
        self.status = RoomStatus.OCCUPIED
        self.current_subject = subject_dbref
        self.current_breaker = breaker_name
        self.sessions_completed += 1
        return f"Breaking session {self.sessions_completed} beginning in {self.name}."
    
    def end_session(self, hours: int = 1) -> str:
        """End the breaking session."""
        self.hours_in_cell += hours
        self.current_breaker = ""
        return f"Session ended. Total time in cell: {self.hours_in_cell} hours."
    
    def release_subject(self) -> str:
        """Release subject from the cell."""
        name = self.current_subject
        self.status = RoomStatus.AVAILABLE
        self.current_subject = ""
        self.hours_in_cell = 0
        return f"Subject released from {self.name}."
    
    def set_conditions(
        self,
        temperature: str = None,
        lighting: str = None,
        sound: str = None,
    ) -> str:
        """Set cell conditions."""
        changes = []
        if temperature and self.temperature_control:
            self.current_temperature = temperature
            changes.append(f"temperature to {temperature}")
        if lighting and self.lighting_control:
            self.current_lighting = lighting
            changes.append(f"lighting to {lighting}")
        if sound and self.sound_control:
            self.current_sound = sound
            changes.append(f"sound to {sound}")
        
        if changes:
            return f"Cell conditions changed: {', '.join(changes)}."
        return "No changes made."
    
    def get_description(self) -> str:
        """Get cell description."""
        desc = f"A specialized breaking cell. "
        
        features = []
        if self.has_suspension_rig:
            features.append("suspension rig with chains")
        if self.has_restraint_frame:
            features.append("an X-frame for restraint")
        if self.has_punishment_tools:
            features.append("various implements of discipline")
        if self.has_pleasure_devices:
            features.append("devices for forced pleasure")
        
        if features:
            desc += f"It contains {', '.join(features)}. "
        
        desc += f"The room is {self.current_temperature} with {self.current_lighting} lighting."
        
        return desc
    
    def to_dict(self) -> dict:
        return {
            "cell_id": self.cell_id,
            "name": self.name,
            "has_suspension_rig": self.has_suspension_rig,
            "has_restraint_frame": self.has_restraint_frame,
            "has_sensory_deprivation": self.has_sensory_deprivation,
            "has_punishment_tools": self.has_punishment_tools,
            "has_pleasure_devices": self.has_pleasure_devices,
            "temperature_control": self.temperature_control,
            "lighting_control": self.lighting_control,
            "sound_control": self.sound_control,
            "current_temperature": self.current_temperature,
            "current_lighting": self.current_lighting,
            "current_sound": self.current_sound,
            "status": self.status.value,
            "current_subject": self.current_subject,
            "current_breaker": self.current_breaker,
            "hours_in_cell": self.hours_in_cell,
            "sessions_completed": self.sessions_completed,
            "facility_id": self.facility_id,
        }


# =============================================================================
# AUCTION BLOCK
# =============================================================================

@dataclass
class AuctionBlock:
    """Platform for slave auctions."""
    block_id: str
    name: str
    
    # Features
    has_display_platform: bool = True
    has_restraint_posts: bool = True
    has_rotating_platform: bool = False
    has_lighting: bool = True
    
    # Capacity
    audience_capacity: int = 50
    
    # Current state
    status: RoomStatus = RoomStatus.AVAILABLE
    current_lot: str = ""         # Current slave being auctioned
    current_auctioneer: str = ""
    
    # Location
    facility_id: str = ""
    
    def start_auction(self, lot_dbref: str, auctioneer: str) -> str:
        """Start an auction."""
        self.status = RoomStatus.OCCUPIED
        self.current_lot = lot_dbref
        self.current_auctioneer = auctioneer
        return f"Auction beginning on {self.name}."
    
    def end_auction(self) -> str:
        """End the auction."""
        self.status = RoomStatus.AVAILABLE
        self.current_lot = ""
        self.current_auctioneer = ""
        return f"Auction concluded."
    
    def get_description(self) -> str:
        """Get block description."""
        desc = "A raised platform for displaying and selling slaves. "
        
        if self.has_rotating_platform:
            desc += "The central platform can rotate for all-around viewing. "
        if self.has_restraint_posts:
            desc += "Sturdy posts with chains allow restraint during display. "
        
        desc += f"Seating for {self.audience_capacity} potential buyers surrounds the block."
        
        return desc
    
    def to_dict(self) -> dict:
        return {
            "block_id": self.block_id,
            "name": self.name,
            "has_display_platform": self.has_display_platform,
            "has_restraint_posts": self.has_restraint_posts,
            "has_rotating_platform": self.has_rotating_platform,
            "has_lighting": self.has_lighting,
            "audience_capacity": self.audience_capacity,
            "status": self.status.value,
            "current_lot": self.current_lot,
            "current_auctioneer": self.current_auctioneer,
            "facility_id": self.facility_id,
        }


# =============================================================================
# FACILITY
# =============================================================================

@dataclass
class ProcessingFacility:
    """A complete processing facility."""
    facility_id: str
    name: str
    
    # Rooms and cells
    holding_cells: Dict[str, HoldingCell] = field(default_factory=dict)
    exam_rooms: Dict[str, ExaminationRoom] = field(default_factory=dict)
    training_rooms: Dict[str, TrainingRoom] = field(default_factory=dict)
    breaking_cells: Dict[str, BreakingCell] = field(default_factory=dict)
    auction_blocks: Dict[str, AuctionBlock] = field(default_factory=dict)
    
    # Staff
    staff: Dict[str, str] = field(default_factory=dict)
    # {dbref: role}
    
    # Statistics
    total_processed: int = 0
    current_population: int = 0
    
    # Location
    location_dbref: str = ""
    
    def add_cell(self, cell: HoldingCell) -> None:
        """Add a holding cell."""
        cell.facility_id = self.facility_id
        self.holding_cells[cell.cell_id] = cell
    
    def add_exam_room(self, room: ExaminationRoom) -> None:
        """Add an examination room."""
        room.facility_id = self.facility_id
        self.exam_rooms[room.room_id] = room
    
    def add_training_room(self, room: TrainingRoom) -> None:
        """Add a training room."""
        room.facility_id = self.facility_id
        self.training_rooms[room.room_id] = room
    
    def add_breaking_cell(self, cell: BreakingCell) -> None:
        """Add a breaking cell."""
        cell.facility_id = self.facility_id
        self.breaking_cells[cell.cell_id] = cell
    
    def add_auction_block(self, block: AuctionBlock) -> None:
        """Add an auction block."""
        block.facility_id = self.facility_id
        self.auction_blocks[block.block_id] = block
    
    def find_available_cell(self, cell_type: CellType = None) -> Optional[HoldingCell]:
        """Find an available cell."""
        for cell in self.holding_cells.values():
            if cell.is_available:
                if cell_type is None or cell.cell_type == cell_type:
                    return cell
        return None
    
    def find_available_exam_room(self, exam_type: str = None) -> Optional[ExaminationRoom]:
        """Find an available exam room."""
        for room in self.exam_rooms.values():
            if room.status == RoomStatus.AVAILABLE:
                if exam_type is None or exam_type in room.specialized_for:
                    return room
        return None
    
    def get_population_count(self) -> int:
        """Count current population."""
        count = 0
        for cell in self.holding_cells.values():
            count += len(cell.current_occupants)
        return count
    
    def get_facility_status(self) -> str:
        """Get facility status summary."""
        lines = [f"=== {self.name} Status ==="]
        
        # Cells
        total_cells = len(self.holding_cells)
        occupied_cells = sum(1 for c in self.holding_cells.values() if c.current_occupants)
        lines.append(f"Holding Cells: {occupied_cells}/{total_cells} occupied")
        
        # Exam rooms
        total_exam = len(self.exam_rooms)
        busy_exam = sum(1 for r in self.exam_rooms.values() if r.status == RoomStatus.OCCUPIED)
        lines.append(f"Exam Rooms: {busy_exam}/{total_exam} in use")
        
        # Training rooms
        total_train = len(self.training_rooms)
        lines.append(f"Training Rooms: {total_train}")
        
        # Breaking cells
        total_break = len(self.breaking_cells)
        busy_break = sum(1 for c in self.breaking_cells.values() if c.status == RoomStatus.OCCUPIED)
        lines.append(f"Breaking Cells: {busy_break}/{total_break} in use")
        
        # Population
        lines.append(f"\nCurrent Population: {self.get_population_count()}")
        lines.append(f"Total Processed: {self.total_processed}")
        
        return "\n".join(lines)
    
    def to_dict(self) -> dict:
        return {
            "facility_id": self.facility_id,
            "name": self.name,
            "holding_cells": {k: v.to_dict() for k, v in self.holding_cells.items()},
            "exam_rooms": {k: v.to_dict() for k, v in self.exam_rooms.items()},
            "training_rooms": {k: v.to_dict() for k, v in self.training_rooms.items()},
            "breaking_cells": {k: v.to_dict() for k, v in self.breaking_cells.items()},
            "auction_blocks": {k: v.to_dict() for k, v in self.auction_blocks.items()},
            "staff": self.staff,
            "total_processed": self.total_processed,
            "current_population": self.current_population,
            "location_dbref": self.location_dbref,
        }


# =============================================================================
# FACILITY PRESETS
# =============================================================================

def create_standard_facility(facility_id: str, name: str) -> ProcessingFacility:
    """Create a standard processing facility."""
    facility = ProcessingFacility(
        facility_id=facility_id,
        name=name,
    )
    
    # Add holding cells
    for i in range(10):
        cell = create_standard_cell(f"{facility_id}_cell_{i}", f"Cell {i+1}")
        facility.add_cell(cell)
    
    # Add kennels
    for i in range(5):
        kennel = create_kennel(f"{facility_id}_kennel_{i}", f"Kennel {i+1}")
        facility.add_cell(kennel)
    
    # Add isolation cells
    for i in range(3):
        iso = create_isolation_cell(f"{facility_id}_iso_{i}", f"Isolation {i+1}")
        facility.add_cell(iso)
    
    # Add punishment cells
    for i in range(2):
        pun = create_punishment_cell(f"{facility_id}_pun_{i}", f"Punishment Cell {i+1}")
        facility.add_cell(pun)
    
    # Add exam rooms
    physical_exam = ExaminationRoom(
        room_id=f"{facility_id}_exam_phys",
        name="Physical Examination Room",
        has_exam_table=True,
        has_restraints=True,
        has_measuring_tools=True,
        specialized_for=["physical"],
    )
    facility.add_exam_room(physical_exam)
    
    sexual_exam = ExaminationRoom(
        room_id=f"{facility_id}_exam_sex",
        name="Sexual Examination Room",
        has_exam_table=True,
        has_restraints=True,
        has_stirrups=True,
        specialized_for=["sexual"],
    )
    facility.add_exam_room(sexual_exam)
    
    medical_exam = ExaminationRoom(
        room_id=f"{facility_id}_exam_med",
        name="Medical Examination Room",
        has_exam_table=True,
        has_medical_equipment=True,
        specialized_for=["medical"],
    )
    facility.add_exam_room(medical_exam)
    
    # Add breaking cells
    for i in range(3):
        breaking = BreakingCell(
            cell_id=f"{facility_id}_break_{i}",
            name=f"Breaking Cell {i+1}",
            has_suspension_rig=True,
            has_restraint_frame=True,
            has_punishment_tools=True,
        )
        facility.add_breaking_cell(breaking)
    
    # Add training rooms
    obedience_room = TrainingRoom(
        room_id=f"{facility_id}_train_obed",
        name="Obedience Training Room",
        training_types=["obedience", "basic"],
        equipment=["training_post", "leashes", "kneeling_pads"],
        capacity=5,
    )
    facility.add_training_room(obedience_room)
    
    sexual_room = TrainingRoom(
        room_id=f"{facility_id}_train_sex",
        name="Sexual Training Room",
        training_types=["sexual", "pleasure"],
        equipment=["training_horse", "mirrors", "practice_devices"],
        capacity=3,
    )
    facility.add_training_room(sexual_room)
    
    # Add auction block
    auction = AuctionBlock(
        block_id=f"{facility_id}_auction",
        name="Main Auction Block",
        has_display_platform=True,
        has_restraint_posts=True,
        has_rotating_platform=True,
        audience_capacity=100,
    )
    facility.add_auction_block(auction)
    
    return facility


__all__ = [
    "FacilityType",
    "CellType",
    "RoomStatus",
    "HoldingCell",
    "ExaminationRoom",
    "TrainingRoom",
    "BreakingCell",
    "AuctionBlock",
    "ProcessingFacility",
    "create_standard_cell",
    "create_kennel",
    "create_isolation_cell",
    "create_punishment_cell",
    "create_luxury_cell",
    "create_group_cage",
    "create_standard_facility",
]
