"""
Slave Status Mixin
==================

Character mixin for tracking slave status, documents, and training.
"""

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any, TYPE_CHECKING
from datetime import datetime

from .acquisition import (
    AcquisitionRecord, AcquisitionMethod, AcquisitionStatus,
    CaptureEvent, DebtRecord, VoluntarySubmission, CriminalSentence,
)
from .documentation import (
    SlaveRegistration, OwnershipCertificate, ServiceContract,
    BillOfSale, BrandRegistry, BreedingCertificate, ManumissionPapers,
    DocumentStatus,
)
from .processing import (
    ProcessingRecord, ProcessingStage, Classification,
    PhysicalExam, SexualExam, MentalExam, AptitudeTest,
)
from .training_tracks import TrackProgress, TrackType, TrackStage


# =============================================================================
# SLAVE STATUS
# =============================================================================

@dataclass
class SlaveStatus:
    """Complete slave status for a character."""
    
    # Basic status
    is_slave: bool = False
    is_free: bool = True
    
    # Acquisition
    acquisition_record: Optional[AcquisitionRecord] = None
    
    # Documents
    registration: Optional[SlaveRegistration] = None
    ownership_certificate: Optional[OwnershipCertificate] = None
    active_contracts: List[ServiceContract] = field(default_factory=list)
    brand_registry: Optional[BrandRegistry] = None
    breeding_certificates: List[BreedingCertificate] = field(default_factory=list)
    
    # Processing
    processing_record: Optional[ProcessingRecord] = None
    classification: Optional[Classification] = None
    
    # Training
    training_progress: Optional[TrackProgress] = None
    completed_tracks: List[str] = field(default_factory=list)
    
    # Ownership
    owner_dbref: str = ""
    owner_name: str = ""
    
    # History
    previous_owners: List[Dict[str, Any]] = field(default_factory=list)
    sale_history: List[BillOfSale] = field(default_factory=list)
    
    # Value
    current_value: int = 0
    
    # Freedom papers (if freed)
    manumission: Optional[ManumissionPapers] = None
    
    def to_dict(self) -> dict:
        """Serialize to dict."""
        return {
            "is_slave": self.is_slave,
            "is_free": self.is_free,
            "acquisition_record": self.acquisition_record.to_dict() if self.acquisition_record else None,
            "registration": self.registration.to_dict() if self.registration else None,
            "ownership_certificate": self.ownership_certificate.to_dict() if self.ownership_certificate else None,
            "active_contracts": [c.to_dict() for c in self.active_contracts],
            "brand_registry": self.brand_registry.to_dict() if self.brand_registry else None,
            "breeding_certificates": [b.to_dict() for b in self.breeding_certificates],
            "processing_record": self.processing_record.to_dict() if self.processing_record else None,
            "classification": self.classification.to_dict() if self.classification else None,
            "training_progress": self.training_progress.to_dict() if self.training_progress else None,
            "completed_tracks": self.completed_tracks,
            "owner_dbref": self.owner_dbref,
            "owner_name": self.owner_name,
            "previous_owners": self.previous_owners,
            "sale_history": [s.to_dict() for s in self.sale_history],
            "current_value": self.current_value,
            "manumission": self.manumission.to_dict() if self.manumission else None,
        }
    
    @classmethod
    def from_dict(cls, data: dict) -> "SlaveStatus":
        """Deserialize from dict."""
        status = cls()
        status.is_slave = data.get("is_slave", False)
        status.is_free = data.get("is_free", True)
        
        if data.get("acquisition_record"):
            status.acquisition_record = AcquisitionRecord.from_dict(data["acquisition_record"])
        if data.get("registration"):
            status.registration = SlaveRegistration.from_dict(data["registration"])
        if data.get("ownership_certificate"):
            status.ownership_certificate = OwnershipCertificate.from_dict(data["ownership_certificate"])
        if data.get("classification"):
            status.classification = Classification.from_dict(data["classification"])
        if data.get("training_progress"):
            status.training_progress = TrackProgress.from_dict(data["training_progress"])
        if data.get("manumission"):
            status.manumission = ManumissionPapers.from_dict(data["manumission"])
        
        status.active_contracts = [
            ServiceContract.from_dict(c) for c in data.get("active_contracts", [])
        ]
        status.breeding_certificates = [
            BreedingCertificate.from_dict(b) for b in data.get("breeding_certificates", [])
        ]
        status.sale_history = [
            BillOfSale.from_dict(s) for s in data.get("sale_history", [])
        ]
        
        status.completed_tracks = data.get("completed_tracks", [])
        status.owner_dbref = data.get("owner_dbref", "")
        status.owner_name = data.get("owner_name", "")
        status.previous_owners = data.get("previous_owners", [])
        status.current_value = data.get("current_value", 0)
        
        return status


# =============================================================================
# CHARACTER MIXIN
# =============================================================================

class SlaveMixin:
    """
    Mixin for characters to track slave status.
    
    Add to your Character typeclass:
        class Character(SlaveMixin, DefaultCharacter):
            pass
    """
    
    @property
    def slave_status(self) -> SlaveStatus:
        """Get slave status."""
        data = self.db.slave_status
        if data:
            return SlaveStatus.from_dict(data)
        return SlaveStatus()
    
    @slave_status.setter
    def slave_status(self, status: SlaveStatus) -> None:
        """Set slave status."""
        self.db.slave_status = status.to_dict()
    
    def _save_slave_status(self, status: SlaveStatus) -> None:
        """Save slave status to db."""
        self.db.slave_status = status.to_dict()
    
    # -------------------------------------------------------------------------
    # Status checks
    # -------------------------------------------------------------------------
    
    @property
    def is_slave(self) -> bool:
        """Check if character is a slave."""
        return self.slave_status.is_slave
    
    @property
    def is_free(self) -> bool:
        """Check if character is free."""
        return self.slave_status.is_free
    
    @property
    def owner(self):
        """Get owner object."""
        status = self.slave_status
        if status.owner_dbref:
            from evennia import search_object
            results = search_object(status.owner_dbref)
            if results:
                return results[0]
        return None
    
    @property
    def registration_number(self) -> str:
        """Get registration number if registered."""
        status = self.slave_status
        if status.registration:
            return status.registration.registration_number
        return ""
    
    @property
    def training_track(self) -> str:
        """Get current training track."""
        status = self.slave_status
        if status.training_progress:
            return status.training_progress.track_type.value
        if status.classification:
            return status.classification.training_track.value
        return ""
    
    @property
    def slave_value(self) -> int:
        """Get current slave value."""
        status = self.slave_status
        if status.current_value:
            return status.current_value
        if status.classification:
            return status.classification.estimated_value
        return 0
    
    # -------------------------------------------------------------------------
    # Enslavement
    # -------------------------------------------------------------------------
    
    def enslave(
        self,
        owner,
        acquisition: AcquisitionRecord,
    ) -> str:
        """Enslave this character."""
        status = self.slave_status
        
        status.is_slave = True
        status.is_free = False
        status.acquisition_record = acquisition
        status.owner_dbref = owner.dbref if owner else ""
        status.owner_name = owner.key if owner else ""
        
        self._save_slave_status(status)
        
        return f"{self.key} has been enslaved."
    
    def register_slave(self, registration: SlaveRegistration) -> str:
        """Register as a slave."""
        status = self.slave_status
        status.registration = registration
        self._save_slave_status(status)
        
        return f"{self.key} registered as {registration.registration_number}."
    
    def transfer_ownership(self, new_owner, sale: BillOfSale = None) -> str:
        """Transfer to new owner."""
        status = self.slave_status
        
        # Record previous owner
        if status.owner_dbref:
            status.previous_owners.append({
                "dbref": status.owner_dbref,
                "name": status.owner_name,
                "transferred": datetime.now().isoformat(),
            })
        
        # Record sale
        if sale:
            status.sale_history.append(sale)
        
        # Update owner
        status.owner_dbref = new_owner.dbref
        status.owner_name = new_owner.key
        
        # Update ownership certificate
        if status.ownership_certificate:
            status.ownership_certificate.add_to_chain(
                status.owner_name, status.owner_dbref, datetime.now()
            )
            status.ownership_certificate.owner_dbref = new_owner.dbref
            status.ownership_certificate.owner_name = new_owner.key
        
        self._save_slave_status(status)
        
        return f"{self.key} transferred to {new_owner.key}."
    
    def free_slave(self, manumission: ManumissionPapers) -> str:
        """Free this slave."""
        status = self.slave_status
        
        status.is_slave = False
        status.is_free = True
        status.manumission = manumission
        status.owner_dbref = ""
        status.owner_name = ""
        
        self._save_slave_status(status)
        
        return f"{self.key} has been freed."
    
    # -------------------------------------------------------------------------
    # Processing
    # -------------------------------------------------------------------------
    
    def set_processing_record(self, record: ProcessingRecord) -> None:
        """Set processing record."""
        status = self.slave_status
        status.processing_record = record
        self._save_slave_status(status)
    
    def set_classification(self, classification: Classification) -> None:
        """Set classification."""
        status = self.slave_status
        status.classification = classification
        status.current_value = classification.estimated_value
        self._save_slave_status(status)
    
    # -------------------------------------------------------------------------
    # Training
    # -------------------------------------------------------------------------
    
    def start_training_track(self, progress: TrackProgress) -> str:
        """Start a training track."""
        status = self.slave_status
        status.training_progress = progress
        self._save_slave_status(status)
        
        return f"{self.key} has begun {progress.track_type.value} training."
    
    def update_training_progress(self, progress: TrackProgress) -> None:
        """Update training progress."""
        status = self.slave_status
        status.training_progress = progress
        self._save_slave_status(status)
    
    def complete_training_track(self) -> str:
        """Complete current training track."""
        status = self.slave_status
        
        if not status.training_progress:
            return "No training in progress."
        
        track_name = status.training_progress.track_type.value
        status.completed_tracks.append(track_name)
        status.training_progress = None
        
        self._save_slave_status(status)
        
        return f"{self.key} has completed {track_name} training."
    
    # -------------------------------------------------------------------------
    # Contracts
    # -------------------------------------------------------------------------
    
    def add_contract(self, contract: ServiceContract) -> str:
        """Add a service contract."""
        status = self.slave_status
        status.active_contracts.append(contract)
        self._save_slave_status(status)
        
        return f"Contract added for {self.key}."
    
    def get_active_contract(self) -> Optional[ServiceContract]:
        """Get active contract if any."""
        status = self.slave_status
        for contract in status.active_contracts:
            if contract.status == DocumentStatus.ACTIVE:
                return contract
        return None
    
    # -------------------------------------------------------------------------
    # Branding
    # -------------------------------------------------------------------------
    
    def set_brand(self, brand: BrandRegistry) -> str:
        """Set brand registry."""
        status = self.slave_status
        status.brand_registry = brand
        self._save_slave_status(status)
        
        return f"{self.key} has been branded."
    
    # -------------------------------------------------------------------------
    # Display
    # -------------------------------------------------------------------------
    
    def get_slave_status_display(self) -> str:
        """Get formatted slave status."""
        status = self.slave_status
        
        if status.is_free and not status.is_slave:
            if status.manumission:
                return f"{self.key} - FREED (formerly enslaved)"
            return f"{self.key} - FREE"
        
        lines = [f"=== Slave Status: {self.key} ==="]
        
        if status.registration:
            lines.append(f"Registration: {status.registration.registration_number}")
        
        if status.owner_name:
            lines.append(f"Owner: {status.owner_name}")
        
        if status.classification:
            lines.append(f"Classification: {status.classification.training_track.value}")
            lines.append(f"Grade: {status.classification.value_grade.value}")
            lines.append(f"Value: {status.classification.estimated_value} gold")
        
        if status.training_progress:
            lines.append(f"\nTraining: {status.training_progress.track_type.value}")
            lines.append(f"Stage: {status.training_progress.current_stage.value}")
            lines.append(f"Progress: {status.training_progress.overall_progress}%")
        
        if status.completed_tracks:
            lines.append(f"\nCompleted: {', '.join(status.completed_tracks)}")
        
        if status.brand_registry:
            lines.append(f"\nBrand: {status.brand_registry.brand_design}")
            lines.append(f"Location: {status.brand_registry.brand_location.value}")
        
        return "\n".join(lines)
    
    def get_papers_display(self) -> str:
        """Get all slave papers."""
        status = self.slave_status
        
        lines = [f"=== Papers for {self.key} ==="]
        
        if status.registration:
            lines.append("\n--- REGISTRATION ---")
            lines.append(status.registration.get_papers_display())
        
        if status.ownership_certificate:
            lines.append("\n--- OWNERSHIP CERTIFICATE ---")
            lines.append(status.ownership_certificate.get_certificate_display())
        
        if status.classification:
            lines.append("\n--- CLASSIFICATION ---")
            lines.append(status.classification.get_classification_display())
        
        if status.manumission:
            lines.append("\n--- FREEDOM PAPERS ---")
            lines.append(status.manumission.get_papers_display())
        
        if len(lines) == 1:
            lines.append("No papers on file.")
        
        return "\n".join(lines)


# =============================================================================
# OWNER MIXIN
# =============================================================================

class SlaveOwnerMixin:
    """
    Mixin for characters who can own slaves.
    """
    
    @property
    def owned_slaves(self) -> List[str]:
        """Get list of owned slave dbrefs."""
        return self.db.owned_slaves or []
    
    @owned_slaves.setter
    def owned_slaves(self, slaves: List[str]) -> None:
        """Set owned slaves list."""
        self.db.owned_slaves = slaves
    
    def add_slave(self, slave) -> str:
        """Add a slave to ownership."""
        slaves = self.owned_slaves
        if slave.dbref not in slaves:
            slaves.append(slave.dbref)
            self.owned_slaves = slaves
        return f"{slave.key} added to {self.key}'s property."
    
    def remove_slave(self, slave) -> str:
        """Remove a slave from ownership."""
        slaves = self.owned_slaves
        if slave.dbref in slaves:
            slaves.remove(slave.dbref)
            self.owned_slaves = slaves
        return f"{slave.key} removed from {self.key}'s property."
    
    def get_slaves(self) -> list:
        """Get all owned slave objects."""
        from evennia import search_object
        slaves = []
        for dbref in self.owned_slaves:
            results = search_object(dbref)
            if results:
                slaves.append(results[0])
        return slaves
    
    def get_slave_count(self) -> int:
        """Get number of owned slaves."""
        return len(self.owned_slaves)
    
    def get_slaves_display(self) -> str:
        """Get display of owned slaves."""
        slaves = self.get_slaves()
        
        if not slaves:
            return f"{self.key} owns no slaves."
        
        lines = [f"=== {self.key}'s Property ({len(slaves)} slaves) ==="]
        
        for slave in slaves:
            if hasattr(slave, 'slave_status'):
                status = slave.slave_status
                reg = status.registration.registration_number if status.registration else "unregistered"
                track = status.training_progress.track_type.value if status.training_progress else "none"
                lines.append(f"  {slave.key} [{reg}] - {track}")
            else:
                lines.append(f"  {slave.key}")
        
        return "\n".join(lines)


__all__ = [
    "SlaveStatus",
    "SlaveMixin",
    "SlaveOwnerMixin",
]
