"""
Slave Status Mixin
==================

Character mixin for tracking slave status and records.
"""

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any, TYPE_CHECKING
from datetime import datetime

from .acquisition import (
    AcquisitionRecord, AcquisitionMethod, AcquisitionStatus,
    CaptureEvent, DebtRecord, VoluntarySubmission, CriminalSentence
)
from .documentation import (
    SlaveRegistration, OwnershipCertificate, ServiceContract,
    BrandRegistry, BillOfSale
)
from .processing import ProcessingRecord, Classification, TrainingTrack, ValueGrade
from .training_tracks import TrackProgress, TrackType


# =============================================================================
# SLAVE STATUS
# =============================================================================

@dataclass
class SlaveStatus:
    """Complete slave status record."""
    
    # Basic status
    is_slave: bool = False
    is_free: bool = True
    
    # Current owner
    owner_dbref: str = ""
    owner_name: str = ""
    
    # Classification
    training_track: str = ""
    value_grade: str = ""
    current_value: int = 0
    
    # Registration
    registration_number: str = ""
    
    # Acquisition
    acquisition_method: str = ""
    acquisition_date: Optional[datetime] = None
    
    # For debt slaves
    remaining_debt: int = 0
    days_served: int = 0
    
    # For sentenced slaves
    remaining_sentence_days: int = 0
    
    # For voluntary
    can_revoke: bool = False
    revocation_deadline: Optional[datetime] = None
    
    # Training status
    training_complete: bool = False
    training_days: int = 0
    
    # Current location
    assigned_facility: str = ""
    assigned_cell: str = ""
    
    # Marks
    is_branded: bool = False
    brand_location: str = ""
    brand_design: str = ""
    
    # Collaring
    is_collared: bool = False
    collar_type: str = ""
    
    # Behavior tracking
    obedience_score: int = 50
    infractions: int = 0
    punishments_received: int = 0
    rewards_received: int = 0
    
    def enslave(
        self,
        owner_dbref: str,
        owner_name: str,
        method: str,
    ) -> str:
        """Mark as enslaved."""
        self.is_slave = True
        self.is_free = False
        self.owner_dbref = owner_dbref
        self.owner_name = owner_name
        self.acquisition_method = method
        self.acquisition_date = datetime.now()
        
        return f"Now enslaved to {owner_name}."
    
    def free(self) -> str:
        """Mark as freed."""
        former_owner = self.owner_name
        
        self.is_slave = False
        self.is_free = True
        self.owner_dbref = ""
        self.owner_name = ""
        
        return f"Freed from {former_owner}."
    
    def transfer(self, new_owner_dbref: str, new_owner_name: str) -> str:
        """Transfer to new owner."""
        former_owner = self.owner_name
        self.owner_dbref = new_owner_dbref
        self.owner_name = new_owner_name
        
        return f"Transferred from {former_owner} to {new_owner_name}."
    
    def add_infraction(self, severity: int = 1) -> int:
        """Record an infraction."""
        self.infractions += severity
        self.obedience_score = max(0, self.obedience_score - severity * 2)
        return self.infractions
    
    def add_punishment(self, severity: int = 1) -> None:
        """Record a punishment."""
        self.punishments_received += 1
        # Punishment can increase obedience
        self.obedience_score = min(100, self.obedience_score + severity)
    
    def add_reward(self) -> None:
        """Record a reward."""
        self.rewards_received += 1
        self.obedience_score = min(100, self.obedience_score + 3)
    
    def serve_day(self) -> Tuple[int, bool]:
        """
        Serve one day.
        Returns (remaining, is_complete).
        """
        self.days_served += 1
        self.training_days += 1
        
        # For debt slaves
        if self.remaining_debt > 0:
            # Assume 10 gold per day
            self.remaining_debt = max(0, self.remaining_debt - 10)
            if self.remaining_debt == 0:
                return 0, True
            return self.remaining_debt, False
        
        # For sentenced slaves
        if self.remaining_sentence_days > 0:
            self.remaining_sentence_days -= 1
            if self.remaining_sentence_days == 0:
                return 0, True
            return self.remaining_sentence_days, False
        
        return 0, False
    
    def get_status_display(self, name: str = "Subject") -> str:
        """Get formatted status display."""
        if not self.is_slave:
            return f"{name} is free."
        
        lines = [f"=== Slave Status: {name} ==="]
        lines.append(f"Owner: {self.owner_name or 'Unowned'}")
        lines.append(f"Registration: {self.registration_number or 'Unregistered'}")
        
        if self.training_track:
            lines.append(f"Track: {self.training_track}")
        if self.value_grade:
            lines.append(f"Grade: {self.value_grade}")
        if self.current_value:
            lines.append(f"Value: {self.current_value} gold")
        
        lines.append(f"\nObedience: {self.obedience_score}/100")
        lines.append(f"Infractions: {self.infractions}")
        
        if self.remaining_debt > 0:
            lines.append(f"\nDebt Remaining: {self.remaining_debt} gold")
        if self.remaining_sentence_days > 0:
            lines.append(f"\nSentence Remaining: {self.remaining_sentence_days} days")
        
        if self.is_branded:
            lines.append(f"\nBranded: {self.brand_location}")
        if self.is_collared:
            lines.append(f"Collared: {self.collar_type}")
        
        return "\n".join(lines)
    
    def to_dict(self) -> dict:
        return {
            "is_slave": self.is_slave,
            "is_free": self.is_free,
            "owner_dbref": self.owner_dbref,
            "owner_name": self.owner_name,
            "training_track": self.training_track,
            "value_grade": self.value_grade,
            "current_value": self.current_value,
            "registration_number": self.registration_number,
            "acquisition_method": self.acquisition_method,
            "acquisition_date": self.acquisition_date.isoformat() if self.acquisition_date else None,
            "remaining_debt": self.remaining_debt,
            "days_served": self.days_served,
            "remaining_sentence_days": self.remaining_sentence_days,
            "can_revoke": self.can_revoke,
            "revocation_deadline": self.revocation_deadline.isoformat() if self.revocation_deadline else None,
            "training_complete": self.training_complete,
            "training_days": self.training_days,
            "assigned_facility": self.assigned_facility,
            "assigned_cell": self.assigned_cell,
            "is_branded": self.is_branded,
            "brand_location": self.brand_location,
            "brand_design": self.brand_design,
            "is_collared": self.is_collared,
            "collar_type": self.collar_type,
            "obedience_score": self.obedience_score,
            "infractions": self.infractions,
            "punishments_received": self.punishments_received,
            "rewards_received": self.rewards_received,
        }
    
    @classmethod
    def from_dict(cls, data: dict) -> "SlaveStatus":
        status = cls()
        for key, value in data.items():
            if key in ["acquisition_date", "revocation_deadline"] and value:
                setattr(status, key, datetime.fromisoformat(value))
            elif hasattr(status, key):
                setattr(status, key, value)
        return status


# Need this for type hints
from typing import Tuple


# =============================================================================
# SLAVE MIXIN
# =============================================================================

class SlaveMixin:
    """
    Mixin for characters that can be enslaved.
    Add to your Character typeclass.
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
    
    def save_slave_status(self, status: SlaveStatus) -> None:
        """Save slave status."""
        self.db.slave_status = status.to_dict()
    
    # Convenience properties
    @property
    def is_slave(self) -> bool:
        """Check if enslaved."""
        return self.slave_status.is_slave
    
    @property
    def is_free(self) -> bool:
        """Check if free."""
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
        """Get registration number."""
        return self.slave_status.registration_number
    
    # Document storage
    @property
    def acquisition_record(self) -> Optional[AcquisitionRecord]:
        """Get acquisition record."""
        data = self.db.acquisition_record
        if data:
            return AcquisitionRecord.from_dict(data)
        return None
    
    @acquisition_record.setter
    def acquisition_record(self, record: AcquisitionRecord) -> None:
        """Set acquisition record."""
        self.db.acquisition_record = record.to_dict()
    
    @property
    def slave_registration(self) -> Optional[SlaveRegistration]:
        """Get registration papers."""
        data = self.db.slave_registration
        if data:
            return SlaveRegistration.from_dict(data)
        return None
    
    @slave_registration.setter
    def slave_registration(self, reg: SlaveRegistration) -> None:
        """Set registration papers."""
        self.db.slave_registration = reg.to_dict()
    
    @property
    def ownership_certificate(self) -> Optional[OwnershipCertificate]:
        """Get ownership certificate."""
        data = self.db.ownership_certificate
        if data:
            return OwnershipCertificate.from_dict(data)
        return None
    
    @ownership_certificate.setter
    def ownership_certificate(self, cert: OwnershipCertificate) -> None:
        """Set ownership certificate."""
        self.db.ownership_certificate = cert.to_dict()
    
    @property
    def service_contract(self) -> Optional[ServiceContract]:
        """Get service contract."""
        data = self.db.service_contract
        if data:
            return ServiceContract.from_dict(data)
        return None
    
    @service_contract.setter
    def service_contract(self, contract: ServiceContract) -> None:
        """Set service contract."""
        self.db.service_contract = contract.to_dict()
    
    @property
    def processing_record(self) -> Optional[ProcessingRecord]:
        """Get processing record."""
        data = self.db.processing_record
        if data:
            return ProcessingRecord.from_dict(data)
        return None
    
    @processing_record.setter
    def processing_record(self, record: ProcessingRecord) -> None:
        """Set processing record."""
        self.db.processing_record = record.to_dict()
    
    @property
    def track_progress(self) -> Optional[TrackProgress]:
        """Get training track progress."""
        data = self.db.track_progress
        if data:
            return TrackProgress.from_dict(data)
        return None
    
    @track_progress.setter
    def track_progress(self, progress: TrackProgress) -> None:
        """Set training track progress."""
        self.db.track_progress = progress.to_dict()
    
    @property
    def brand_registry(self) -> Optional[BrandRegistry]:
        """Get brand registry."""
        data = self.db.brand_registry
        if data:
            return BrandRegistry.from_dict(data)
        return None
    
    @brand_registry.setter
    def brand_registry(self, registry: BrandRegistry) -> None:
        """Set brand registry."""
        self.db.brand_registry = registry.to_dict()
    
    # Sale history
    @property
    def sale_history(self) -> List[BillOfSale]:
        """Get sale history."""
        data_list = self.db.sale_history or []
        return [BillOfSale.from_dict(d) for d in data_list]
    
    def add_sale_record(self, sale: BillOfSale) -> None:
        """Add a sale record to history."""
        history = self.db.sale_history or []
        history.append(sale.to_dict())
        self.db.sale_history = history


# =============================================================================
# OWNER MIXIN
# =============================================================================

class OwnerMixin:
    """
    Mixin for characters that can own slaves.
    Add to your Character typeclass.
    """
    
    @property
    def owned_slaves(self) -> List[str]:
        """Get list of owned slave dbrefs."""
        return self.db.owned_slaves or []
    
    def add_slave(self, slave_dbref: str) -> None:
        """Add a slave to ownership."""
        slaves = self.db.owned_slaves or []
        if slave_dbref not in slaves:
            slaves.append(slave_dbref)
            self.db.owned_slaves = slaves
    
    def remove_slave(self, slave_dbref: str) -> None:
        """Remove a slave from ownership."""
        slaves = self.db.owned_slaves or []
        if slave_dbref in slaves:
            slaves.remove(slave_dbref)
            self.db.owned_slaves = slaves
    
    def get_slaves(self) -> List:
        """Get owned slave objects."""
        from evennia import search_object
        slaves = []
        for dbref in self.owned_slaves:
            results = search_object(dbref)
            if results:
                slaves.append(results[0])
        return slaves
    
    @property
    def slave_count(self) -> int:
        """Get number of owned slaves."""
        return len(self.owned_slaves)
    
    # Owner's brand/symbol
    @property
    def owner_brand(self) -> str:
        """Get owner's brand design."""
        return self.db.owner_brand or ""
    
    @owner_brand.setter
    def owner_brand(self, design: str) -> None:
        """Set owner's brand design."""
        self.db.owner_brand = design
    
    # Facilities
    @property
    def owned_facilities(self) -> List[str]:
        """Get owned facility IDs."""
        return self.db.owned_facilities or []
    
    def add_facility(self, facility_id: str) -> None:
        """Add a facility."""
        facilities = self.db.owned_facilities or []
        if facility_id not in facilities:
            facilities.append(facility_id)
            self.db.owned_facilities = facilities


__all__ = [
    "SlaveStatus",
    "SlaveMixin",
    "OwnerMixin",
]
