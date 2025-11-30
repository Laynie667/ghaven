"""
Acquisition System
==================

How individuals enter slavery:
- Capture (force)
- Debt (contract default)
- Voluntary submission
- Criminal sentencing
- Sale/trade
- Inheritance/birth
"""

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any, Tuple
from enum import Enum
from datetime import datetime, timedelta
import random


# =============================================================================
# ENUMS
# =============================================================================

class AcquisitionMethod(Enum):
    """How someone became a slave."""
    CAPTURE = "capture"             # Taken by force
    DEBT = "debt"                   # Contract/loan default
    VOLUNTARY = "voluntary"         # Willing submission
    SENTENCING = "sentencing"       # Criminal punishment
    SALE = "sale"                   # Purchased from previous owner
    TRADE = "trade"                 # Traded for goods/other slaves
    INHERITANCE = "inheritance"     # Born into or inherited
    WAGER = "wager"                 # Lost a bet
    TRIBUTE = "tribute"             # Given as tribute/gift
    CONQUEST = "conquest"           # Spoils of war


class CaptureMethod(Enum):
    """Specific capture methods."""
    AMBUSH = "ambush"
    TRAP = "trap"
    NET = "net"
    COMBAT_DEFEAT = "combat_defeat"
    DRUGGED = "drugged"
    SUBDUED = "subdued"
    LURED = "lured"
    RAIDED = "raided"


class DebtType(Enum):
    """Types of debt leading to slavery."""
    LOAN = "loan"                   # Borrowed money
    GAMBLING = "gambling"           # Gambling debts
    CRIMINAL_FINE = "criminal_fine" # Unpaid fines
    FAMILY_DEBT = "family_debt"     # Inherited debt
    CONTRACT_BREACH = "contract_breach"
    MEDICAL = "medical"             # Medical bills
    TAXES = "taxes"                 # Unpaid taxes


class VoluntaryReason(Enum):
    """Why someone would volunteer for slavery."""
    DEVOTION = "devotion"           # Love/devotion to master
    POVERTY = "poverty"             # Can't survive otherwise
    DESIRE = "desire"               # Wants to be owned
    PROTECTION = "protection"       # Seeking safety
    ATONEMENT = "atonement"         # Making up for something
    ADVENTURE = "adventure"         # Curious/thrill-seeking
    TRAINING = "training"           # Wants the training
    ESCAPE = "escape"               # Running from something worse


class SentenceType(Enum):
    """Criminal sentences resulting in slavery."""
    THEFT = "theft"
    ASSAULT = "assault"
    MURDER = "murder"
    TREASON = "treason"
    HERESY = "heresy"
    SMUGGLING = "smuggling"
    DEBT_CRIME = "debt_crime"
    ADULTERY = "adultery"
    ESCAPE_ATTEMPT = "escape_attempt"  # Recaptured runaway


class AcquisitionStatus(Enum):
    """Status of acquisition."""
    PENDING = "pending"             # Not yet processed
    PROCESSING = "processing"       # In intake
    CONTESTED = "contested"         # Ownership disputed
    CONFIRMED = "confirmed"         # Legally confirmed
    TEMPORARY = "temporary"         # Time-limited
    PERMANENT = "permanent"         # Forever


# =============================================================================
# CAPTURE EVENT
# =============================================================================

@dataclass
class CaptureEvent:
    """Record of a capture."""
    capture_id: str
    
    # Who was captured
    captive_dbref: str = ""
    captive_name: str = ""
    
    # Who captured them
    captor_dbref: str = ""
    captor_name: str = ""
    captor_faction: str = ""      # Slaver guild, kingdom, etc.
    
    # How
    method: CaptureMethod = CaptureMethod.SUBDUED
    location: str = ""
    
    # Resistance
    resisted: bool = False
    resistance_level: int = 0     # 0-100
    injuries_sustained: List[str] = field(default_factory=list)
    
    # Witnesses
    witnesses: List[str] = field(default_factory=list)
    
    # Timestamp
    captured_at: Optional[datetime] = None
    
    def get_description(self) -> str:
        """Get description of capture."""
        method_descs = {
            CaptureMethod.AMBUSH: "ambushed and subdued",
            CaptureMethod.TRAP: "caught in a trap",
            CaptureMethod.NET: "netted and restrained",
            CaptureMethod.COMBAT_DEFEAT: "defeated in combat",
            CaptureMethod.DRUGGED: "drugged and taken",
            CaptureMethod.SUBDUED: "physically subdued",
            CaptureMethod.LURED: "lured and captured",
            CaptureMethod.RAIDED: "taken in a raid",
        }
        
        desc = method_descs.get(self.method, "captured")
        resist_desc = " despite fierce resistance" if self.resisted else ""
        
        return f"{self.captive_name} was {desc}{resist_desc} by {self.captor_name}"
    
    def to_dict(self) -> dict:
        return {
            "capture_id": self.capture_id,
            "captive_dbref": self.captive_dbref,
            "captive_name": self.captive_name,
            "captor_dbref": self.captor_dbref,
            "captor_name": self.captor_name,
            "captor_faction": self.captor_faction,
            "method": self.method.value,
            "location": self.location,
            "resisted": self.resisted,
            "resistance_level": self.resistance_level,
            "injuries_sustained": self.injuries_sustained,
            "witnesses": self.witnesses,
            "captured_at": self.captured_at.isoformat() if self.captured_at else None,
        }
    
    @classmethod
    def from_dict(cls, data: dict) -> "CaptureEvent":
        event = cls(capture_id=data["capture_id"])
        event.captive_dbref = data.get("captive_dbref", "")
        event.captive_name = data.get("captive_name", "")
        event.captor_dbref = data.get("captor_dbref", "")
        event.captor_name = data.get("captor_name", "")
        event.captor_faction = data.get("captor_faction", "")
        event.method = CaptureMethod(data.get("method", "subdued"))
        event.location = data.get("location", "")
        event.resisted = data.get("resisted", False)
        event.resistance_level = data.get("resistance_level", 0)
        event.injuries_sustained = data.get("injuries_sustained", [])
        event.witnesses = data.get("witnesses", [])
        
        if data.get("captured_at"):
            event.captured_at = datetime.fromisoformat(data["captured_at"])
        
        return event


# =============================================================================
# DEBT RECORD
# =============================================================================

@dataclass
class DebtRecord:
    """Record of debt leading to slavery."""
    debt_id: str
    
    # Debtor
    debtor_dbref: str = ""
    debtor_name: str = ""
    
    # Creditor
    creditor_dbref: str = ""
    creditor_name: str = ""
    creditor_faction: str = ""
    
    # Debt details
    debt_type: DebtType = DebtType.LOAN
    original_amount: int = 0
    current_amount: int = 0       # With interest
    currency: str = "gold"
    interest_rate: float = 0.1    # Per month
    
    # Terms
    incurred_date: Optional[datetime] = None
    due_date: Optional[datetime] = None
    default_date: Optional[datetime] = None
    
    # Conversion to slavery
    service_value_per_day: int = 10  # How much debt paid per day of slavery
    estimated_service_days: int = 0
    
    # Can be paid off?
    allows_buyout: bool = True
    buyout_amount: int = 0        # Amount to purchase freedom
    
    def calculate_payoff(self) -> int:
        """Calculate days of service to pay off debt."""
        if self.service_value_per_day <= 0:
            return 9999
        return self.current_amount // self.service_value_per_day
    
    def apply_interest(self, months: int = 1) -> int:
        """Apply interest to debt."""
        for _ in range(months):
            self.current_amount = int(self.current_amount * (1 + self.interest_rate))
        self.estimated_service_days = self.calculate_payoff()
        return self.current_amount
    
    def make_payment(self, amount: int) -> Tuple[int, bool]:
        """
        Make payment on debt.
        Returns (remaining_debt, is_paid_off).
        """
        self.current_amount = max(0, self.current_amount - amount)
        self.estimated_service_days = self.calculate_payoff()
        return self.current_amount, self.current_amount == 0
    
    def to_dict(self) -> dict:
        return {
            "debt_id": self.debt_id,
            "debtor_dbref": self.debtor_dbref,
            "debtor_name": self.debtor_name,
            "creditor_dbref": self.creditor_dbref,
            "creditor_name": self.creditor_name,
            "creditor_faction": self.creditor_faction,
            "debt_type": self.debt_type.value,
            "original_amount": self.original_amount,
            "current_amount": self.current_amount,
            "currency": self.currency,
            "interest_rate": self.interest_rate,
            "incurred_date": self.incurred_date.isoformat() if self.incurred_date else None,
            "due_date": self.due_date.isoformat() if self.due_date else None,
            "default_date": self.default_date.isoformat() if self.default_date else None,
            "service_value_per_day": self.service_value_per_day,
            "estimated_service_days": self.estimated_service_days,
            "allows_buyout": self.allows_buyout,
            "buyout_amount": self.buyout_amount,
        }
    
    @classmethod
    def from_dict(cls, data: dict) -> "DebtRecord":
        record = cls(debt_id=data["debt_id"])
        record.debtor_dbref = data.get("debtor_dbref", "")
        record.debtor_name = data.get("debtor_name", "")
        record.creditor_dbref = data.get("creditor_dbref", "")
        record.creditor_name = data.get("creditor_name", "")
        record.creditor_faction = data.get("creditor_faction", "")
        record.debt_type = DebtType(data.get("debt_type", "loan"))
        record.original_amount = data.get("original_amount", 0)
        record.current_amount = data.get("current_amount", 0)
        record.currency = data.get("currency", "gold")
        record.interest_rate = data.get("interest_rate", 0.1)
        record.service_value_per_day = data.get("service_value_per_day", 10)
        record.estimated_service_days = data.get("estimated_service_days", 0)
        record.allows_buyout = data.get("allows_buyout", True)
        record.buyout_amount = data.get("buyout_amount", 0)
        
        for field_name in ["incurred_date", "due_date", "default_date"]:
            if data.get(field_name):
                setattr(record, field_name, datetime.fromisoformat(data[field_name]))
        
        return record


# =============================================================================
# VOLUNTARY SUBMISSION
# =============================================================================

@dataclass 
class VoluntarySubmission:
    """Record of voluntary enslavement."""
    submission_id: str
    
    # Who submitted
    submitter_dbref: str = ""
    submitter_name: str = ""
    
    # To whom
    master_dbref: str = ""
    master_name: str = ""
    receiving_faction: str = ""
    
    # Why
    reason: VoluntaryReason = VoluntaryReason.DESIRE
    stated_reason: str = ""       # Their own words
    
    # Terms
    is_permanent: bool = False
    duration_days: int = 0        # If not permanent
    can_revoke: bool = True       # Can they change their mind?
    revocation_period_days: int = 7  # Grace period to back out
    
    # Conditions
    limits: List[str] = field(default_factory=list)      # Hard limits
    preferences: List[str] = field(default_factory=list)  # Soft preferences
    requested_training: str = ""   # What track they want
    
    # Verification
    witnessed_by: List[str] = field(default_factory=list)
    verified: bool = False
    verification_method: str = ""  # "interview", "trial_period", etc.
    
    # Timestamps
    submitted_at: Optional[datetime] = None
    revocation_deadline: Optional[datetime] = None
    
    @property
    def can_still_revoke(self) -> bool:
        """Check if still within revocation period."""
        if not self.can_revoke:
            return False
        if not self.revocation_deadline:
            return True
        return datetime.now() < self.revocation_deadline
    
    def to_dict(self) -> dict:
        return {
            "submission_id": self.submission_id,
            "submitter_dbref": self.submitter_dbref,
            "submitter_name": self.submitter_name,
            "master_dbref": self.master_dbref,
            "master_name": self.master_name,
            "receiving_faction": self.receiving_faction,
            "reason": self.reason.value,
            "stated_reason": self.stated_reason,
            "is_permanent": self.is_permanent,
            "duration_days": self.duration_days,
            "can_revoke": self.can_revoke,
            "revocation_period_days": self.revocation_period_days,
            "limits": self.limits,
            "preferences": self.preferences,
            "requested_training": self.requested_training,
            "witnessed_by": self.witnessed_by,
            "verified": self.verified,
            "verification_method": self.verification_method,
            "submitted_at": self.submitted_at.isoformat() if self.submitted_at else None,
            "revocation_deadline": self.revocation_deadline.isoformat() if self.revocation_deadline else None,
        }
    
    @classmethod
    def from_dict(cls, data: dict) -> "VoluntarySubmission":
        sub = cls(submission_id=data["submission_id"])
        sub.submitter_dbref = data.get("submitter_dbref", "")
        sub.submitter_name = data.get("submitter_name", "")
        sub.master_dbref = data.get("master_dbref", "")
        sub.master_name = data.get("master_name", "")
        sub.receiving_faction = data.get("receiving_faction", "")
        sub.reason = VoluntaryReason(data.get("reason", "desire"))
        sub.stated_reason = data.get("stated_reason", "")
        sub.is_permanent = data.get("is_permanent", False)
        sub.duration_days = data.get("duration_days", 0)
        sub.can_revoke = data.get("can_revoke", True)
        sub.revocation_period_days = data.get("revocation_period_days", 7)
        sub.limits = data.get("limits", [])
        sub.preferences = data.get("preferences", [])
        sub.requested_training = data.get("requested_training", "")
        sub.witnessed_by = data.get("witnessed_by", [])
        sub.verified = data.get("verified", False)
        sub.verification_method = data.get("verification_method", "")
        
        if data.get("submitted_at"):
            sub.submitted_at = datetime.fromisoformat(data["submitted_at"])
        if data.get("revocation_deadline"):
            sub.revocation_deadline = datetime.fromisoformat(data["revocation_deadline"])
        
        return sub


# =============================================================================
# CRIMINAL SENTENCE
# =============================================================================

@dataclass
class CriminalSentence:
    """Record of criminal sentencing to slavery."""
    sentence_id: str
    
    # Criminal
    criminal_dbref: str = ""
    criminal_name: str = ""
    
    # Crime
    crime_type: SentenceType = SentenceType.THEFT
    crime_description: str = ""
    severity: int = 50            # 0-100
    
    # Sentence
    sentence_days: int = 365      # Duration of slavery
    hard_labor: bool = False
    public_punishment: bool = False
    
    # Assigned to
    assigned_to_dbref: str = ""   # Owner or institution
    assigned_to_name: str = ""
    
    # Legal
    judge_name: str = ""
    court_location: str = ""
    sentenced_date: Optional[datetime] = None
    release_date: Optional[datetime] = None
    
    # Parole
    eligible_for_parole: bool = False
    parole_date: Optional[datetime] = None
    
    # Escape attempts
    escape_attempts: int = 0
    additional_time_added: int = 0  # Days added for escapes/violations
    
    def add_time(self, days: int, reason: str = "") -> None:
        """Add time to sentence."""
        self.additional_time_added += days
        self.sentence_days += days
        if self.release_date:
            self.release_date += timedelta(days=days)
    
    def to_dict(self) -> dict:
        return {
            "sentence_id": self.sentence_id,
            "criminal_dbref": self.criminal_dbref,
            "criminal_name": self.criminal_name,
            "crime_type": self.crime_type.value,
            "crime_description": self.crime_description,
            "severity": self.severity,
            "sentence_days": self.sentence_days,
            "hard_labor": self.hard_labor,
            "public_punishment": self.public_punishment,
            "assigned_to_dbref": self.assigned_to_dbref,
            "assigned_to_name": self.assigned_to_name,
            "judge_name": self.judge_name,
            "court_location": self.court_location,
            "sentenced_date": self.sentenced_date.isoformat() if self.sentenced_date else None,
            "release_date": self.release_date.isoformat() if self.release_date else None,
            "eligible_for_parole": self.eligible_for_parole,
            "parole_date": self.parole_date.isoformat() if self.parole_date else None,
            "escape_attempts": self.escape_attempts,
            "additional_time_added": self.additional_time_added,
        }
    
    @classmethod
    def from_dict(cls, data: dict) -> "CriminalSentence":
        sent = cls(sentence_id=data["sentence_id"])
        sent.criminal_dbref = data.get("criminal_dbref", "")
        sent.criminal_name = data.get("criminal_name", "")
        sent.crime_type = SentenceType(data.get("crime_type", "theft"))
        sent.crime_description = data.get("crime_description", "")
        sent.severity = data.get("severity", 50)
        sent.sentence_days = data.get("sentence_days", 365)
        sent.hard_labor = data.get("hard_labor", False)
        sent.public_punishment = data.get("public_punishment", False)
        sent.assigned_to_dbref = data.get("assigned_to_dbref", "")
        sent.assigned_to_name = data.get("assigned_to_name", "")
        sent.judge_name = data.get("judge_name", "")
        sent.court_location = data.get("court_location", "")
        sent.eligible_for_parole = data.get("eligible_for_parole", False)
        sent.escape_attempts = data.get("escape_attempts", 0)
        sent.additional_time_added = data.get("additional_time_added", 0)
        
        for field_name in ["sentenced_date", "release_date", "parole_date"]:
            if data.get(field_name):
                setattr(sent, field_name, datetime.fromisoformat(data[field_name]))
        
        return sent


# =============================================================================
# ACQUISITION RECORD
# =============================================================================

@dataclass
class AcquisitionRecord:
    """Complete record of how someone was acquired."""
    record_id: str
    
    # Subject
    subject_dbref: str = ""
    subject_name: str = ""
    
    # Method
    method: AcquisitionMethod = AcquisitionMethod.CAPTURE
    status: AcquisitionStatus = AcquisitionStatus.PENDING
    
    # Specific records (only one will be populated)
    capture_event: Optional[CaptureEvent] = None
    debt_record: Optional[DebtRecord] = None
    voluntary_submission: Optional[VoluntarySubmission] = None
    criminal_sentence: Optional[CriminalSentence] = None
    
    # For SALE/TRADE
    previous_owner_dbref: str = ""
    previous_owner_name: str = ""
    sale_price: int = 0
    
    # Current ownership
    current_owner_dbref: str = ""
    current_owner_name: str = ""
    current_owner_faction: str = ""
    
    # Timestamps
    acquired_date: Optional[datetime] = None
    processed_date: Optional[datetime] = None
    
    # Notes
    notes: str = ""
    
    def get_summary(self) -> str:
        """Get acquisition summary."""
        lines = [f"=== Acquisition Record: {self.subject_name} ==="]
        lines.append(f"Method: {self.method.value}")
        lines.append(f"Status: {self.status.value}")
        
        if self.capture_event:
            lines.append(f"Capture: {self.capture_event.get_description()}")
        elif self.debt_record:
            lines.append(f"Debt: {self.debt_record.current_amount} {self.debt_record.currency}")
            lines.append(f"Service required: {self.debt_record.estimated_service_days} days")
        elif self.voluntary_submission:
            lines.append(f"Voluntary: {self.voluntary_submission.reason.value}")
            if self.voluntary_submission.can_still_revoke:
                lines.append("  (Still within revocation period)")
        elif self.criminal_sentence:
            lines.append(f"Crime: {self.criminal_sentence.crime_type.value}")
            lines.append(f"Sentence: {self.criminal_sentence.sentence_days} days")
        
        if self.current_owner_name:
            lines.append(f"Current Owner: {self.current_owner_name}")
        
        return "\n".join(lines)
    
    def to_dict(self) -> dict:
        return {
            "record_id": self.record_id,
            "subject_dbref": self.subject_dbref,
            "subject_name": self.subject_name,
            "method": self.method.value,
            "status": self.status.value,
            "capture_event": self.capture_event.to_dict() if self.capture_event else None,
            "debt_record": self.debt_record.to_dict() if self.debt_record else None,
            "voluntary_submission": self.voluntary_submission.to_dict() if self.voluntary_submission else None,
            "criminal_sentence": self.criminal_sentence.to_dict() if self.criminal_sentence else None,
            "previous_owner_dbref": self.previous_owner_dbref,
            "previous_owner_name": self.previous_owner_name,
            "sale_price": self.sale_price,
            "current_owner_dbref": self.current_owner_dbref,
            "current_owner_name": self.current_owner_name,
            "current_owner_faction": self.current_owner_faction,
            "acquired_date": self.acquired_date.isoformat() if self.acquired_date else None,
            "processed_date": self.processed_date.isoformat() if self.processed_date else None,
            "notes": self.notes,
        }
    
    @classmethod
    def from_dict(cls, data: dict) -> "AcquisitionRecord":
        record = cls(record_id=data["record_id"])
        record.subject_dbref = data.get("subject_dbref", "")
        record.subject_name = data.get("subject_name", "")
        record.method = AcquisitionMethod(data.get("method", "capture"))
        record.status = AcquisitionStatus(data.get("status", "pending"))
        
        if data.get("capture_event"):
            record.capture_event = CaptureEvent.from_dict(data["capture_event"])
        if data.get("debt_record"):
            record.debt_record = DebtRecord.from_dict(data["debt_record"])
        if data.get("voluntary_submission"):
            record.voluntary_submission = VoluntarySubmission.from_dict(data["voluntary_submission"])
        if data.get("criminal_sentence"):
            record.criminal_sentence = CriminalSentence.from_dict(data["criminal_sentence"])
        
        record.previous_owner_dbref = data.get("previous_owner_dbref", "")
        record.previous_owner_name = data.get("previous_owner_name", "")
        record.sale_price = data.get("sale_price", 0)
        record.current_owner_dbref = data.get("current_owner_dbref", "")
        record.current_owner_name = data.get("current_owner_name", "")
        record.current_owner_faction = data.get("current_owner_faction", "")
        record.notes = data.get("notes", "")
        
        if data.get("acquired_date"):
            record.acquired_date = datetime.fromisoformat(data["acquired_date"])
        if data.get("processed_date"):
            record.processed_date = datetime.fromisoformat(data["processed_date"])
        
        return record


# =============================================================================
# ACQUISITION SYSTEM
# =============================================================================

class AcquisitionSystem:
    """
    Manages slave acquisition.
    """
    
    @staticmethod
    def generate_id(prefix: str = "ACQ") -> str:
        """Generate unique ID."""
        timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
        rand = random.randint(1000, 9999)
        return f"{prefix}-{timestamp}-{rand}"
    
    @staticmethod
    def create_capture(
        captive,
        captor,
        method: CaptureMethod = CaptureMethod.SUBDUED,
        location: str = "",
        resisted: bool = False,
    ) -> AcquisitionRecord:
        """Create acquisition record from capture."""
        capture = CaptureEvent(
            capture_id=AcquisitionSystem.generate_id("CAP"),
            captive_dbref=captive.dbref,
            captive_name=captive.key,
            captor_dbref=captor.dbref,
            captor_name=captor.key,
            method=method,
            location=location,
            resisted=resisted,
            captured_at=datetime.now(),
        )
        
        record = AcquisitionRecord(
            record_id=AcquisitionSystem.generate_id("ACQ"),
            subject_dbref=captive.dbref,
            subject_name=captive.key,
            method=AcquisitionMethod.CAPTURE,
            capture_event=capture,
            current_owner_dbref=captor.dbref,
            current_owner_name=captor.key,
            acquired_date=datetime.now(),
        )
        
        return record
    
    @staticmethod
    def create_debt_slavery(
        debtor,
        creditor,
        amount: int,
        debt_type: DebtType = DebtType.LOAN,
    ) -> AcquisitionRecord:
        """Create acquisition record from debt."""
        debt = DebtRecord(
            debt_id=AcquisitionSystem.generate_id("DBT"),
            debtor_dbref=debtor.dbref,
            debtor_name=debtor.key,
            creditor_dbref=creditor.dbref,
            creditor_name=creditor.key,
            debt_type=debt_type,
            original_amount=amount,
            current_amount=amount,
            incurred_date=datetime.now(),
            default_date=datetime.now(),
        )
        debt.estimated_service_days = debt.calculate_payoff()
        
        record = AcquisitionRecord(
            record_id=AcquisitionSystem.generate_id("ACQ"),
            subject_dbref=debtor.dbref,
            subject_name=debtor.key,
            method=AcquisitionMethod.DEBT,
            debt_record=debt,
            current_owner_dbref=creditor.dbref,
            current_owner_name=creditor.key,
            acquired_date=datetime.now(),
        )
        
        return record
    
    @staticmethod
    def create_voluntary(
        submitter,
        master,
        reason: VoluntaryReason = VoluntaryReason.DESIRE,
        is_permanent: bool = False,
        duration_days: int = 365,
        limits: List[str] = None,
    ) -> AcquisitionRecord:
        """Create acquisition record from voluntary submission."""
        submission = VoluntarySubmission(
            submission_id=AcquisitionSystem.generate_id("VOL"),
            submitter_dbref=submitter.dbref,
            submitter_name=submitter.key,
            master_dbref=master.dbref if master else "",
            master_name=master.key if master else "",
            reason=reason,
            is_permanent=is_permanent,
            duration_days=duration_days,
            limits=limits or [],
            submitted_at=datetime.now(),
        )
        
        if submission.can_revoke:
            submission.revocation_deadline = datetime.now() + timedelta(days=submission.revocation_period_days)
        
        record = AcquisitionRecord(
            record_id=AcquisitionSystem.generate_id("ACQ"),
            subject_dbref=submitter.dbref,
            subject_name=submitter.key,
            method=AcquisitionMethod.VOLUNTARY,
            voluntary_submission=submission,
            current_owner_dbref=master.dbref if master else "",
            current_owner_name=master.key if master else "",
            acquired_date=datetime.now(),
        )
        
        return record
    
    @staticmethod
    def create_sentence(
        criminal,
        crime: SentenceType,
        sentence_days: int,
        assigned_to = None,
    ) -> AcquisitionRecord:
        """Create acquisition record from criminal sentence."""
        sentence = CriminalSentence(
            sentence_id=AcquisitionSystem.generate_id("SNT"),
            criminal_dbref=criminal.dbref,
            criminal_name=criminal.key,
            crime_type=crime,
            sentence_days=sentence_days,
            sentenced_date=datetime.now(),
            release_date=datetime.now() + timedelta(days=sentence_days),
        )
        
        if assigned_to:
            sentence.assigned_to_dbref = assigned_to.dbref
            sentence.assigned_to_name = assigned_to.key
        
        record = AcquisitionRecord(
            record_id=AcquisitionSystem.generate_id("ACQ"),
            subject_dbref=criminal.dbref,
            subject_name=criminal.key,
            method=AcquisitionMethod.SENTENCING,
            criminal_sentence=sentence,
            current_owner_dbref=assigned_to.dbref if assigned_to else "",
            current_owner_name=assigned_to.key if assigned_to else "",
            acquired_date=datetime.now(),
        )
        
        return record


__all__ = [
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
]
