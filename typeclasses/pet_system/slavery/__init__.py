"""
Slavery System Package
======================

Comprehensive slavery mechanics including:
- Acquisition (capture, debt, voluntary, sentencing)
- Documentation (registration, contracts, certificates)
- Processing (intake, examination, testing, classification)
- Training tracks (hucow, pleasure, pony, breeding, etc.)
- Facilities (cells, exam rooms, breaking cells, auction blocks)
- NPC types (slavers, trainers, handlers, breakers)
- Commands
"""

from .acquisition import (
    AcquisitionMethod,
    CaptureMethod,
    DebtType,
    VoluntaryReason,
    SentenceType,
    AcquisitionStatus,
    CaptureEvent,
    DebtRecord,
    VoluntarySubmission,
    CriminalSentence,
    AcquisitionRecord,
    AcquisitionSystem,
)

from .documentation import (
    DocumentType,
    ContractType,
    DocumentStatus,
    BrandLocation,
    BrandType,
    SlaveRegistration,
    OwnershipCertificate,
    ServiceContract,
    BillOfSale,
    BrandRegistry,
    BreedingCertificate,
    ManumissionPapers,
    DocumentManager,
)

from .processing import (
    ProcessingStage,
    ExaminationType,
    AptitudeCategory,
    TrainingTrack,
    ValueGrade,
    PhysicalExam,
    SexualExam,
    MentalExam,
    AptitudeTest,
    Classification,
    ProcessingRecord,
    ProcessingSystem,
)

from .training_tracks import (
    TrackStage,
    TrackType,
    TrainingMilestone,
    TrackDefinition,
    ALL_TRACKS,
    get_track,
    TrackProgress,
    TrackSystem,
)

from .facilities import (
    FacilityType,
    CellType,
    RoomStatus,
    HoldingCell,
    ExaminationRoom,
    TrainingRoom,
    BreakingCell,
    AuctionBlock,
    ProcessingFacility,
    create_standard_cell,
    create_kennel,
    create_isolation_cell,
    create_punishment_cell,
    create_luxury_cell,
    create_group_cage,
    create_standard_facility,
)

from .slave_mixin import (
    SlaveStatus,
    SlaveMixin,
    OwnerMixin,
)

from .npcs import (
    SlaveryNPCRole,
    TrainerSpecialty,
    ExaminerSpecialty,
    SlaveryNPCBase,
    SlaverNPC,
    HandlerNPC,
    ExaminerNPC,
    TrainerNPC,
    BreakerNPC,
    AuctioneerNPC,
    GuardNPC,
    VeterinarianNPC,
    SlaveryNPCFactory,
)

from .commands import SlaveryCmdSet


__version__ = "1.0.0"

__all__ = [
    # Acquisition
    "AcquisitionMethod",
    "CaptureMethod",
    "DebtType",
    "VoluntaryReason",
    "SentenceType",
    "AcquisitionStatus",
    "CaptureEvent",
    "DebtRecord",
    "VoluntarySubmission",
    "CriminalSentence",
    "AcquisitionRecord",
    "AcquisitionSystem",
    
    # Documentation
    "DocumentType",
    "ContractType",
    "DocumentStatus",
    "BrandLocation",
    "BrandType",
    "SlaveRegistration",
    "OwnershipCertificate",
    "ServiceContract",
    "BillOfSale",
    "BrandRegistry",
    "BreedingCertificate",
    "ManumissionPapers",
    "DocumentManager",
    
    # Processing
    "ProcessingStage",
    "ExaminationType",
    "AptitudeCategory",
    "TrainingTrack",
    "ValueGrade",
    "PhysicalExam",
    "SexualExam",
    "MentalExam",
    "AptitudeTest",
    "Classification",
    "ProcessingRecord",
    "ProcessingSystem",
    
    # Training Tracks
    "TrackStage",
    "TrackType",
    "TrainingMilestone",
    "TrackDefinition",
    "ALL_TRACKS",
    "get_track",
    "TrackProgress",
    "TrackSystem",
    
    # Facilities
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
    
    # Mixins
    "SlaveStatus",
    "SlaveMixin",
    "OwnerMixin",
    
    # NPCs
    "SlaveryNPCRole",
    "TrainerSpecialty",
    "ExaminerSpecialty",
    "SlaveryNPCBase",
    "SlaverNPC",
    "HandlerNPC",
    "ExaminerNPC",
    "TrainerNPC",
    "BreakerNPC",
    "AuctioneerNPC",
    "GuardNPC",
    "VeterinarianNPC",
    "SlaveryNPCFactory",
    
    # Commands
    "SlaveryCmdSet",
]
