"""
Documentation System
====================

All the paperwork for slavery:
- Slave registration papers
- Ownership certificates
- Contracts (debt, voluntary, lease, breeding)
- Training records
- Bills of sale
- Breeding certificates
- Medical records
"""

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any, Tuple
from enum import Enum
from datetime import datetime, timedelta
import random


# =============================================================================
# ENUMS
# =============================================================================

class DocumentType(Enum):
    """Types of slave documents."""
    REGISTRATION = "registration"       # Slave registration
    OWNERSHIP = "ownership"             # Proof of ownership
    CONTRACT = "contract"               # Service contract
    BILL_OF_SALE = "bill_of_sale"       # Purchase record
    TRAINING_RECORD = "training_record" # Training documentation
    MEDICAL_RECORD = "medical_record"   # Health records
    BREEDING_CERT = "breeding_cert"     # Breeding certificate
    APPRAISAL = "appraisal"            # Value assessment
    BRAND_REGISTRY = "brand_registry"   # Brand/mark registration
    LEASE = "lease"                     # Rental agreement
    MANUMISSION = "manumission"         # Freedom papers


class ContractType(Enum):
    """Types of contracts."""
    DEBT_SERVICE = "debt_service"       # Working off debt
    VOLUNTARY = "voluntary"             # Voluntary submission
    LEASE = "lease"                     # Rental/loan
    BREEDING = "breeding"               # Breeding contract
    TRAINING = "training"               # Training agreement
    SALE = "sale"                       # Bill of sale
    TRADE = "trade"                     # Trade agreement


class DocumentStatus(Enum):
    """Status of a document."""
    DRAFT = "draft"
    PENDING = "pending"
    ACTIVE = "active"
    EXPIRED = "expired"
    VOIDED = "voided"
    COMPLETED = "completed"


class BrandLocation(Enum):
    """Where brands/marks are placed."""
    LEFT_SHOULDER = "left_shoulder"
    RIGHT_SHOULDER = "right_shoulder"
    LEFT_HIP = "left_hip"
    RIGHT_HIP = "right_hip"
    LOWER_BACK = "lower_back"
    INNER_THIGH = "inner_thigh"
    PUBIC = "pubic"
    BREAST = "breast"
    BUTTOCK = "buttock"
    NECK = "neck"


class BrandType(Enum):
    """Types of marks/brands."""
    BRAND = "brand"                     # Burned into skin
    TATTOO = "tattoo"                   # Inked
    MAGICAL = "magical"                 # Magical mark
    SCARIFICATION = "scarification"     # Cut/scarred
    PIERCING = "piercing"               # Marked jewelry


# =============================================================================
# SLAVE REGISTRATION
# =============================================================================

@dataclass
class SlaveRegistration:
    """Official slave registration papers."""
    registration_id: str
    
    # Subject
    slave_dbref: str = ""
    slave_name: str = ""
    slave_given_name: str = ""    # Name assigned by owner
    
    # Basic info
    species: str = ""
    sex: str = ""
    age: int = 0
    height: str = ""
    weight: str = ""
    hair_color: str = ""
    eye_color: str = ""
    skin_color: str = ""
    distinguishing_marks: List[str] = field(default_factory=list)
    
    # Classification
    training_track: str = ""
    skill_level: str = ""         # "untrained", "basic", "trained", "expert"
    value_grade: str = ""         # "common", "quality", "premium", "exceptional"
    
    # Legal
    registration_date: Optional[datetime] = None
    registration_location: str = ""
    registrar_name: str = ""
    registration_number: str = ""  # Official number
    
    # Owner at registration
    owner_dbref: str = ""
    owner_name: str = ""
    
    # Status
    status: DocumentStatus = DocumentStatus.ACTIVE
    
    def generate_registration_number(self) -> str:
        """Generate official registration number."""
        year = datetime.now().strftime("%Y")
        rand = random.randint(10000, 99999)
        return f"SLV-{year}-{rand}"
    
    def get_papers_display(self) -> str:
        """Get formatted registration papers."""
        lines = [
            "╔════════════════════════════════════════╗",
            "║     OFFICIAL SLAVE REGISTRATION        ║",
            "╠════════════════════════════════════════╣",
            f"║ Reg. No: {self.registration_number:<29}║",
            f"║ Name: {self.slave_given_name or self.slave_name:<32}║",
            f"║ Species: {self.species:<29}║",
            f"║ Sex: {self.sex:<33}║",
            f"║ Age: {self.age:<33}║",
            "╠════════════════════════════════════════╣",
            f"║ Training: {self.training_track:<28}║",
            f"║ Grade: {self.value_grade:<31}║",
            "╠════════════════════════════════════════╣",
            f"║ Owner: {self.owner_name:<31}║",
            f"║ Registered: {str(self.registration_date.date()) if self.registration_date else 'N/A':<26}║",
            "╚════════════════════════════════════════╝",
        ]
        return "\n".join(lines)
    
    def to_dict(self) -> dict:
        return {
            "registration_id": self.registration_id,
            "slave_dbref": self.slave_dbref,
            "slave_name": self.slave_name,
            "slave_given_name": self.slave_given_name,
            "species": self.species,
            "sex": self.sex,
            "age": self.age,
            "height": self.height,
            "weight": self.weight,
            "hair_color": self.hair_color,
            "eye_color": self.eye_color,
            "skin_color": self.skin_color,
            "distinguishing_marks": self.distinguishing_marks,
            "training_track": self.training_track,
            "skill_level": self.skill_level,
            "value_grade": self.value_grade,
            "registration_date": self.registration_date.isoformat() if self.registration_date else None,
            "registration_location": self.registration_location,
            "registrar_name": self.registrar_name,
            "registration_number": self.registration_number,
            "owner_dbref": self.owner_dbref,
            "owner_name": self.owner_name,
            "status": self.status.value,
        }
    
    @classmethod
    def from_dict(cls, data: dict) -> "SlaveRegistration":
        reg = cls(registration_id=data["registration_id"])
        for key, value in data.items():
            if key == "status":
                reg.status = DocumentStatus(value)
            elif key == "registration_date" and value:
                reg.registration_date = datetime.fromisoformat(value)
            elif hasattr(reg, key):
                setattr(reg, key, value)
        return reg


# =============================================================================
# OWNERSHIP CERTIFICATE
# =============================================================================

@dataclass
class OwnershipCertificate:
    """Certificate of ownership."""
    certificate_id: str
    
    # Property
    slave_dbref: str = ""
    slave_name: str = ""
    registration_number: str = ""
    
    # Owner
    owner_dbref: str = ""
    owner_name: str = ""
    owner_address: str = ""
    
    # Ownership details
    ownership_type: str = ""      # "full", "partial", "leased", "temporary"
    acquisition_method: str = ""   # How acquired
    acquisition_date: Optional[datetime] = None
    
    # Value
    declared_value: int = 0
    currency: str = "gold"
    
    # Restrictions
    restrictions: List[str] = field(default_factory=list)
    # e.g., ["no resale without approval", "breeding rights reserved"]
    
    # Legal
    issued_date: Optional[datetime] = None
    issued_by: str = ""
    witness_names: List[str] = field(default_factory=list)
    
    # Chain of ownership
    previous_owners: List[Dict[str, Any]] = field(default_factory=list)
    
    status: DocumentStatus = DocumentStatus.ACTIVE
    
    def add_to_chain(self, owner_name: str, owner_dbref: str, date: datetime) -> None:
        """Add previous owner to chain."""
        self.previous_owners.append({
            "name": owner_name,
            "dbref": owner_dbref,
            "date": date.isoformat(),
        })
    
    def get_certificate_display(self) -> str:
        """Get formatted certificate."""
        lines = [
            "╔══════════════════════════════════════════╗",
            "║    CERTIFICATE OF OWNERSHIP              ║",
            "╠══════════════════════════════════════════╣",
            f"║ This certifies that                      ║",
            f"║ {self.owner_name:<40} ║",
            f"║ is the lawful owner of                   ║",
            f"║ {self.slave_name:<40} ║",
            f"║ Reg. No: {self.registration_number:<31} ║",
            "╠══════════════════════════════════════════╣",
            f"║ Ownership Type: {self.ownership_type:<24} ║",
            f"║ Declared Value: {self.declared_value} {self.currency:<17} ║",
            f"║ Acquired: {str(self.acquisition_date.date()) if self.acquisition_date else 'N/A':<30} ║",
            "╠══════════════════════════════════════════╣",
            f"║ Issued: {str(self.issued_date.date()) if self.issued_date else 'N/A':<32} ║",
            f"║ By: {self.issued_by:<36} ║",
            "╚══════════════════════════════════════════╝",
        ]
        return "\n".join(lines)
    
    def to_dict(self) -> dict:
        return {
            "certificate_id": self.certificate_id,
            "slave_dbref": self.slave_dbref,
            "slave_name": self.slave_name,
            "registration_number": self.registration_number,
            "owner_dbref": self.owner_dbref,
            "owner_name": self.owner_name,
            "owner_address": self.owner_address,
            "ownership_type": self.ownership_type,
            "acquisition_method": self.acquisition_method,
            "acquisition_date": self.acquisition_date.isoformat() if self.acquisition_date else None,
            "declared_value": self.declared_value,
            "currency": self.currency,
            "restrictions": self.restrictions,
            "issued_date": self.issued_date.isoformat() if self.issued_date else None,
            "issued_by": self.issued_by,
            "witness_names": self.witness_names,
            "previous_owners": self.previous_owners,
            "status": self.status.value,
        }
    
    @classmethod
    def from_dict(cls, data: dict) -> "OwnershipCertificate":
        cert = cls(certificate_id=data["certificate_id"])
        for key, value in data.items():
            if key == "status":
                cert.status = DocumentStatus(value)
            elif key in ["acquisition_date", "issued_date"] and value:
                setattr(cert, key, datetime.fromisoformat(value))
            elif hasattr(cert, key):
                setattr(cert, key, value)
        return cert


# =============================================================================
# SERVICE CONTRACT
# =============================================================================

@dataclass
class ServiceContract:
    """Contract for service/slavery."""
    contract_id: str
    
    # Parties
    slave_dbref: str = ""
    slave_name: str = ""
    owner_dbref: str = ""
    owner_name: str = ""
    
    # Contract type
    contract_type: ContractType = ContractType.VOLUNTARY
    
    # Terms
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    is_indefinite: bool = False
    
    # Service terms
    service_type: str = ""        # What kind of service
    duties: List[str] = field(default_factory=list)
    hours_per_day: int = 0
    rest_days_per_week: int = 0
    
    # Compensation (if any)
    provides_room: bool = True
    provides_board: bool = True
    provides_clothing: bool = True
    stipend_amount: int = 0
    stipend_frequency: str = ""   # "daily", "weekly", "monthly"
    
    # Limits and conditions
    hard_limits: List[str] = field(default_factory=list)
    soft_limits: List[str] = field(default_factory=list)
    special_conditions: List[str] = field(default_factory=list)
    
    # Termination
    can_terminate_early: bool = False
    termination_notice_days: int = 30
    termination_penalty: int = 0
    
    # For debt contracts
    debt_amount: int = 0
    debt_paid: int = 0
    daily_payoff_rate: int = 0
    
    # Signatures
    slave_signed: bool = False
    slave_signed_date: Optional[datetime] = None
    owner_signed: bool = False
    owner_signed_date: Optional[datetime] = None
    witness_signed: bool = False
    witness_name: str = ""
    
    status: DocumentStatus = DocumentStatus.DRAFT
    
    @property
    def is_fully_signed(self) -> bool:
        """Check if contract is fully executed."""
        return self.slave_signed and self.owner_signed
    
    @property
    def remaining_debt(self) -> int:
        """Get remaining debt."""
        return max(0, self.debt_amount - self.debt_paid)
    
    @property
    def days_remaining(self) -> int:
        """Get days remaining on contract."""
        if self.is_indefinite:
            return -1
        if not self.end_date:
            return 0
        delta = self.end_date - datetime.now()
        return max(0, delta.days)
    
    def sign_slave(self) -> str:
        """Slave signs the contract."""
        self.slave_signed = True
        self.slave_signed_date = datetime.now()
        
        if self.is_fully_signed:
            self.status = DocumentStatus.ACTIVE
            return f"{self.slave_name} signs the contract. Contract is now active."
        
        return f"{self.slave_name} signs the contract."
    
    def sign_owner(self) -> str:
        """Owner signs the contract."""
        self.owner_signed = True
        self.owner_signed_date = datetime.now()
        
        if self.is_fully_signed:
            self.status = DocumentStatus.ACTIVE
            return f"{self.owner_name} signs the contract. Contract is now active."
        
        return f"{self.owner_name} signs the contract."
    
    def make_debt_payment(self, days_served: int = 1) -> Tuple[int, bool]:
        """
        Apply days served to debt.
        Returns (remaining_debt, is_paid_off).
        """
        payment = days_served * self.daily_payoff_rate
        self.debt_paid += payment
        
        if self.remaining_debt <= 0:
            self.status = DocumentStatus.COMPLETED
            return 0, True
        
        return self.remaining_debt, False
    
    def get_contract_display(self) -> str:
        """Get formatted contract."""
        lines = [
            "╔═══════════════════════════════════════════════╗",
            "║           SERVICE CONTRACT                     ║",
            "╠═══════════════════════════════════════════════╣",
            f"║ Contract Type: {self.contract_type.value:<30}║",
            f"║ Status: {self.status.value:<37}║",
            "╠═══════════════════════════════════════════════╣",
            f"║ Service Provider: {self.slave_name:<27}║",
            f"║ Contract Holder: {self.owner_name:<28}║",
            "╠═══════════════════════════════════════════════╣",
        ]
        
        if self.is_indefinite:
            lines.append("║ Term: Indefinite                              ║")
        else:
            start = str(self.start_date.date()) if self.start_date else "N/A"
            end = str(self.end_date.date()) if self.end_date else "N/A"
            lines.append(f"║ Term: {start} to {end:<18}║")
        
        if self.debt_amount > 0:
            lines.append(f"║ Debt: {self.remaining_debt}/{self.debt_amount} gold remaining       ║")
        
        lines.append("╠═══════════════════════════════════════════════╣")
        lines.append(f"║ Service Provider Signed: {'Yes' if self.slave_signed else 'No':<20}║")
        lines.append(f"║ Contract Holder Signed: {'Yes' if self.owner_signed else 'No':<21}║")
        lines.append("╚═══════════════════════════════════════════════╝")
        
        return "\n".join(lines)
    
    def to_dict(self) -> dict:
        data = {
            "contract_id": self.contract_id,
            "slave_dbref": self.slave_dbref,
            "slave_name": self.slave_name,
            "owner_dbref": self.owner_dbref,
            "owner_name": self.owner_name,
            "contract_type": self.contract_type.value,
            "is_indefinite": self.is_indefinite,
            "service_type": self.service_type,
            "duties": self.duties,
            "hours_per_day": self.hours_per_day,
            "rest_days_per_week": self.rest_days_per_week,
            "provides_room": self.provides_room,
            "provides_board": self.provides_board,
            "provides_clothing": self.provides_clothing,
            "stipend_amount": self.stipend_amount,
            "stipend_frequency": self.stipend_frequency,
            "hard_limits": self.hard_limits,
            "soft_limits": self.soft_limits,
            "special_conditions": self.special_conditions,
            "can_terminate_early": self.can_terminate_early,
            "termination_notice_days": self.termination_notice_days,
            "termination_penalty": self.termination_penalty,
            "debt_amount": self.debt_amount,
            "debt_paid": self.debt_paid,
            "daily_payoff_rate": self.daily_payoff_rate,
            "slave_signed": self.slave_signed,
            "owner_signed": self.owner_signed,
            "witness_signed": self.witness_signed,
            "witness_name": self.witness_name,
            "status": self.status.value,
        }
        
        for date_field in ["start_date", "end_date", "slave_signed_date", "owner_signed_date"]:
            val = getattr(self, date_field)
            data[date_field] = val.isoformat() if val else None
        
        return data
    
    @classmethod
    def from_dict(cls, data: dict) -> "ServiceContract":
        contract = cls(contract_id=data["contract_id"])
        
        for key, value in data.items():
            if key == "contract_type":
                contract.contract_type = ContractType(value)
            elif key == "status":
                contract.status = DocumentStatus(value)
            elif key in ["start_date", "end_date", "slave_signed_date", "owner_signed_date"] and value:
                setattr(contract, key, datetime.fromisoformat(value))
            elif hasattr(contract, key):
                setattr(contract, key, value)
        
        return contract


# =============================================================================
# BILL OF SALE
# =============================================================================

@dataclass
class BillOfSale:
    """Record of slave sale."""
    sale_id: str
    
    # Property
    slave_dbref: str = ""
    slave_name: str = ""
    registration_number: str = ""
    
    # Seller
    seller_dbref: str = ""
    seller_name: str = ""
    
    # Buyer
    buyer_dbref: str = ""
    buyer_name: str = ""
    
    # Sale details
    sale_price: int = 0
    currency: str = "gold"
    payment_method: str = ""      # "cash", "credit", "trade", "auction"
    
    # Sale location
    sale_location: str = ""
    sale_date: Optional[datetime] = None
    
    # Auction details (if applicable)
    was_auction: bool = False
    starting_bid: int = 0
    final_bid: int = 0
    number_of_bidders: int = 0
    
    # Witnesses
    witness_names: List[str] = field(default_factory=list)
    auctioneer_name: str = ""
    
    # Warranties
    warranty_period_days: int = 0
    warranty_conditions: List[str] = field(default_factory=list)
    # e.g., ["healthy", "trained as stated", "no hidden defects"]
    
    # Return policy
    allows_return: bool = False
    return_period_days: int = 0
    return_conditions: str = ""
    
    status: DocumentStatus = DocumentStatus.COMPLETED
    
    def get_receipt_display(self) -> str:
        """Get formatted receipt."""
        lines = [
            "╔═══════════════════════════════════════════╗",
            "║            BILL OF SALE                   ║",
            "╠═══════════════════════════════════════════╣",
            f"║ Sale ID: {self.sale_id:<31}║",
            f"║ Date: {str(self.sale_date.date()) if self.sale_date else 'N/A':<34}║",
            "╠═══════════════════════════════════════════╣",
            f"║ Property: {self.slave_name:<30}║",
            f"║ Reg. No: {self.registration_number:<31}║",
            "╠═══════════════════════════════════════════╣",
            f"║ Seller: {self.seller_name:<32}║",
            f"║ Buyer: {self.buyer_name:<33}║",
            "╠═══════════════════════════════════════════╣",
            f"║ Sale Price: {self.sale_price} {self.currency:<24}║",
            f"║ Payment: {self.payment_method:<31}║",
        ]
        
        if self.was_auction:
            lines.append(f"║ (Auction - {self.number_of_bidders} bidders)               ║")
        
        lines.append("╚═══════════════════════════════════════════╝")
        
        return "\n".join(lines)
    
    def to_dict(self) -> dict:
        return {
            "sale_id": self.sale_id,
            "slave_dbref": self.slave_dbref,
            "slave_name": self.slave_name,
            "registration_number": self.registration_number,
            "seller_dbref": self.seller_dbref,
            "seller_name": self.seller_name,
            "buyer_dbref": self.buyer_dbref,
            "buyer_name": self.buyer_name,
            "sale_price": self.sale_price,
            "currency": self.currency,
            "payment_method": self.payment_method,
            "sale_location": self.sale_location,
            "sale_date": self.sale_date.isoformat() if self.sale_date else None,
            "was_auction": self.was_auction,
            "starting_bid": self.starting_bid,
            "final_bid": self.final_bid,
            "number_of_bidders": self.number_of_bidders,
            "witness_names": self.witness_names,
            "auctioneer_name": self.auctioneer_name,
            "warranty_period_days": self.warranty_period_days,
            "warranty_conditions": self.warranty_conditions,
            "allows_return": self.allows_return,
            "return_period_days": self.return_period_days,
            "return_conditions": self.return_conditions,
            "status": self.status.value,
        }
    
    @classmethod
    def from_dict(cls, data: dict) -> "BillOfSale":
        bill = cls(sale_id=data["sale_id"])
        for key, value in data.items():
            if key == "status":
                bill.status = DocumentStatus(value)
            elif key == "sale_date" and value:
                bill.sale_date = datetime.fromisoformat(value)
            elif hasattr(bill, key):
                setattr(bill, key, value)
        return bill


# =============================================================================
# BRAND REGISTRY
# =============================================================================

@dataclass
class BrandRegistry:
    """Registry of slave markings/brands."""
    registry_id: str
    
    # Subject
    slave_dbref: str = ""
    slave_name: str = ""
    registration_number: str = ""
    
    # Brand details
    brand_type: BrandType = BrandType.BRAND
    brand_location: BrandLocation = BrandLocation.LEFT_HIP
    brand_design: str = ""        # Description of the design
    brand_meaning: str = ""       # What it signifies
    
    # Owner mark
    owner_dbref: str = ""
    owner_name: str = ""
    owner_symbol: str = ""        # Owner's registered symbol
    
    # Application
    applied_date: Optional[datetime] = None
    applied_by: str = ""          # Who did the branding
    applied_location: str = ""    # Where it was done
    
    # Additional marks
    additional_marks: List[Dict[str, Any]] = field(default_factory=list)
    # Each entry: {"type": "", "location": "", "design": "", "date": "", "meaning": ""}
    
    def add_mark(
        self,
        mark_type: BrandType,
        location: BrandLocation,
        design: str,
        meaning: str = "",
    ) -> None:
        """Add additional mark."""
        self.additional_marks.append({
            "type": mark_type.value,
            "location": location.value,
            "design": design,
            "meaning": meaning,
            "date": datetime.now().isoformat(),
        })
    
    def get_marks_display(self) -> str:
        """Get display of all marks."""
        lines = [f"=== Brand Registry: {self.slave_name} ==="]
        lines.append(f"Primary Mark:")
        lines.append(f"  Type: {self.brand_type.value}")
        lines.append(f"  Location: {self.brand_location.value}")
        lines.append(f"  Design: {self.brand_design}")
        lines.append(f"  Owner: {self.owner_name}")
        
        if self.additional_marks:
            lines.append(f"\nAdditional Marks:")
            for mark in self.additional_marks:
                lines.append(f"  - {mark['type']} on {mark['location']}: {mark['design']}")
        
        return "\n".join(lines)
    
    def to_dict(self) -> dict:
        return {
            "registry_id": self.registry_id,
            "slave_dbref": self.slave_dbref,
            "slave_name": self.slave_name,
            "registration_number": self.registration_number,
            "brand_type": self.brand_type.value,
            "brand_location": self.brand_location.value,
            "brand_design": self.brand_design,
            "brand_meaning": self.brand_meaning,
            "owner_dbref": self.owner_dbref,
            "owner_name": self.owner_name,
            "owner_symbol": self.owner_symbol,
            "applied_date": self.applied_date.isoformat() if self.applied_date else None,
            "applied_by": self.applied_by,
            "applied_location": self.applied_location,
            "additional_marks": self.additional_marks,
        }
    
    @classmethod
    def from_dict(cls, data: dict) -> "BrandRegistry":
        reg = cls(registry_id=data["registry_id"])
        for key, value in data.items():
            if key == "brand_type":
                reg.brand_type = BrandType(value)
            elif key == "brand_location":
                reg.brand_location = BrandLocation(value)
            elif key == "applied_date" and value:
                reg.applied_date = datetime.fromisoformat(value)
            elif hasattr(reg, key):
                setattr(reg, key, value)
        return reg


# =============================================================================
# BREEDING CERTIFICATE
# =============================================================================

@dataclass
class BreedingCertificate:
    """Certificate for authorized breeding."""
    certificate_id: str
    
    # Dam (mother)
    dam_dbref: str = ""
    dam_name: str = ""
    dam_registration: str = ""
    dam_owner_name: str = ""
    
    # Sire (father)
    sire_dbref: str = ""
    sire_name: str = ""
    sire_registration: str = ""
    sire_owner_name: str = ""
    
    # Breeding details
    breeding_date: Optional[datetime] = None
    breeding_location: str = ""
    breeding_witnessed: bool = False
    witness_name: str = ""
    
    # Pregnancy
    confirmed_pregnant: bool = False
    confirmation_date: Optional[datetime] = None
    expected_due_date: Optional[datetime] = None
    
    # Offspring
    offspring_count: int = 0
    offspring_dbrefs: List[str] = field(default_factory=list)
    birth_date: Optional[datetime] = None
    
    # Ownership of offspring
    offspring_ownership: str = ""  # "dam_owner", "sire_owner", "split", "contract"
    ownership_split: str = ""      # e.g., "60/40 dam/sire"
    
    # Value
    stud_fee: int = 0
    stud_fee_paid: bool = False
    
    status: DocumentStatus = DocumentStatus.PENDING
    
    def get_certificate_display(self) -> str:
        """Get formatted certificate."""
        lines = [
            "╔════════════════════════════════════════════╗",
            "║        BREEDING CERTIFICATE                ║",
            "╠════════════════════════════════════════════╣",
            f"║ Dam: {self.dam_name:<36}║",
            f"║ Sire: {self.sire_name:<35}║",
            "╠════════════════════════════════════════════╣",
        ]
        
        if self.breeding_date:
            lines.append(f"║ Bred: {str(self.breeding_date.date()):<35}║")
        
        if self.confirmed_pregnant:
            lines.append(f"║ Status: CONFIRMED PREGNANT                 ║")
            if self.expected_due_date:
                lines.append(f"║ Due: {str(self.expected_due_date.date()):<36}║")
        
        if self.offspring_count > 0:
            lines.append(f"║ Offspring: {self.offspring_count:<30}║")
        
        lines.append(f"║ Ownership: {self.offspring_ownership:<30}║")
        lines.append("╚════════════════════════════════════════════╝")
        
        return "\n".join(lines)
    
    def to_dict(self) -> dict:
        data = {
            "certificate_id": self.certificate_id,
            "dam_dbref": self.dam_dbref,
            "dam_name": self.dam_name,
            "dam_registration": self.dam_registration,
            "dam_owner_name": self.dam_owner_name,
            "sire_dbref": self.sire_dbref,
            "sire_name": self.sire_name,
            "sire_registration": self.sire_registration,
            "sire_owner_name": self.sire_owner_name,
            "breeding_location": self.breeding_location,
            "breeding_witnessed": self.breeding_witnessed,
            "witness_name": self.witness_name,
            "confirmed_pregnant": self.confirmed_pregnant,
            "offspring_count": self.offspring_count,
            "offspring_dbrefs": self.offspring_dbrefs,
            "offspring_ownership": self.offspring_ownership,
            "ownership_split": self.ownership_split,
            "stud_fee": self.stud_fee,
            "stud_fee_paid": self.stud_fee_paid,
            "status": self.status.value,
        }
        
        for date_field in ["breeding_date", "confirmation_date", "expected_due_date", "birth_date"]:
            val = getattr(self, date_field)
            data[date_field] = val.isoformat() if val else None
        
        return data
    
    @classmethod
    def from_dict(cls, data: dict) -> "BreedingCertificate":
        cert = cls(certificate_id=data["certificate_id"])
        for key, value in data.items():
            if key == "status":
                cert.status = DocumentStatus(value)
            elif key in ["breeding_date", "confirmation_date", "expected_due_date", "birth_date"] and value:
                setattr(cert, key, datetime.fromisoformat(value))
            elif hasattr(cert, key):
                setattr(cert, key, value)
        return cert


# =============================================================================
# MANUMISSION PAPERS
# =============================================================================

@dataclass
class ManumissionPapers:
    """Freedom papers."""
    manumission_id: str
    
    # Freed slave
    slave_dbref: str = ""
    slave_name: str = ""
    registration_number: str = ""
    
    # Former owner
    former_owner_dbref: str = ""
    former_owner_name: str = ""
    
    # Freedom details
    freedom_type: str = ""        # "full", "conditional", "purchased"
    freedom_date: Optional[datetime] = None
    
    # Conditions (for conditional freedom)
    conditions: List[str] = field(default_factory=list)
    condition_period_days: int = 0
    
    # If purchased
    purchase_price: int = 0
    purchased_by: str = ""        # Self, benefactor, etc.
    
    # Legal
    issued_by: str = ""
    issued_location: str = ""
    witness_names: List[str] = field(default_factory=list)
    
    # New identity
    new_name: str = ""            # Name they take as free person
    citizenship_granted: bool = False
    
    status: DocumentStatus = DocumentStatus.ACTIVE
    
    def get_papers_display(self) -> str:
        """Get formatted freedom papers."""
        lines = [
            "╔═══════════════════════════════════════════════╗",
            "║           MANUMISSION PAPERS                   ║",
            "║           (Certificate of Freedom)             ║",
            "╠═══════════════════════════════════════════════╣",
            f"║ This certifies that                            ║",
            f"║ {self.slave_name:<45}║",
            f"║ formerly registered as {self.registration_number:<22}║",
            f"║ has been granted FREEDOM                       ║",
            "╠═══════════════════════════════════════════════╣",
            f"║ Freedom Type: {self.freedom_type:<31}║",
            f"║ Effective: {str(self.freedom_date.date()) if self.freedom_date else 'N/A':<34}║",
        ]
        
        if self.new_name:
            lines.append(f"║ Now known as: {self.new_name:<31}║")
        
        if self.citizenship_granted:
            lines.append("║ FULL CITIZENSHIP GRANTED                       ║")
        
        lines.append("╚═══════════════════════════════════════════════╝")
        
        return "\n".join(lines)
    
    def to_dict(self) -> dict:
        return {
            "manumission_id": self.manumission_id,
            "slave_dbref": self.slave_dbref,
            "slave_name": self.slave_name,
            "registration_number": self.registration_number,
            "former_owner_dbref": self.former_owner_dbref,
            "former_owner_name": self.former_owner_name,
            "freedom_type": self.freedom_type,
            "freedom_date": self.freedom_date.isoformat() if self.freedom_date else None,
            "conditions": self.conditions,
            "condition_period_days": self.condition_period_days,
            "purchase_price": self.purchase_price,
            "purchased_by": self.purchased_by,
            "issued_by": self.issued_by,
            "issued_location": self.issued_location,
            "witness_names": self.witness_names,
            "new_name": self.new_name,
            "citizenship_granted": self.citizenship_granted,
            "status": self.status.value,
        }
    
    @classmethod
    def from_dict(cls, data: dict) -> "ManumissionPapers":
        papers = cls(manumission_id=data["manumission_id"])
        for key, value in data.items():
            if key == "status":
                papers.status = DocumentStatus(value)
            elif key == "freedom_date" and value:
                papers.freedom_date = datetime.fromisoformat(value)
            elif hasattr(papers, key):
                setattr(papers, key, value)
        return papers


# =============================================================================
# DOCUMENT MANAGER
# =============================================================================

class DocumentManager:
    """
    Manages slave documentation.
    """
    
    @staticmethod
    def generate_id(prefix: str = "DOC") -> str:
        """Generate unique ID."""
        timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
        rand = random.randint(1000, 9999)
        return f"{prefix}-{timestamp}-{rand}"
    
    @staticmethod
    def create_registration(
        slave,
        owner,
        training_track: str = "",
    ) -> SlaveRegistration:
        """Create registration papers."""
        reg = SlaveRegistration(
            registration_id=DocumentManager.generate_id("REG"),
            slave_dbref=slave.dbref,
            slave_name=slave.key,
            species=getattr(slave, 'species', 'human'),
            sex=getattr(slave, 'sex', 'unknown'),
            training_track=training_track,
            registration_date=datetime.now(),
            owner_dbref=owner.dbref if owner else "",
            owner_name=owner.key if owner else "",
        )
        reg.registration_number = reg.generate_registration_number()
        
        return reg
    
    @staticmethod
    def create_ownership_certificate(
        slave,
        owner,
        registration: SlaveRegistration,
        acquisition_method: str = "",
        value: int = 0,
    ) -> OwnershipCertificate:
        """Create ownership certificate."""
        cert = OwnershipCertificate(
            certificate_id=DocumentManager.generate_id("OWN"),
            slave_dbref=slave.dbref,
            slave_name=slave.key,
            registration_number=registration.registration_number,
            owner_dbref=owner.dbref,
            owner_name=owner.key,
            ownership_type="full",
            acquisition_method=acquisition_method,
            acquisition_date=datetime.now(),
            declared_value=value,
            issued_date=datetime.now(),
        )
        
        return cert
    
    @staticmethod
    def create_bill_of_sale(
        slave,
        seller,
        buyer,
        price: int,
        registration_number: str = "",
    ) -> BillOfSale:
        """Create bill of sale."""
        bill = BillOfSale(
            sale_id=DocumentManager.generate_id("SALE"),
            slave_dbref=slave.dbref,
            slave_name=slave.key,
            registration_number=registration_number,
            seller_dbref=seller.dbref,
            seller_name=seller.key,
            buyer_dbref=buyer.dbref,
            buyer_name=buyer.key,
            sale_price=price,
            sale_date=datetime.now(),
            payment_method="cash",
        )
        
        return bill
    
    @staticmethod
    def create_manumission(
        slave,
        former_owner,
        registration_number: str = "",
        freedom_type: str = "full",
    ) -> ManumissionPapers:
        """Create freedom papers."""
        papers = ManumissionPapers(
            manumission_id=DocumentManager.generate_id("FREE"),
            slave_dbref=slave.dbref,
            slave_name=slave.key,
            registration_number=registration_number,
            former_owner_dbref=former_owner.dbref,
            former_owner_name=former_owner.key,
            freedom_type=freedom_type,
            freedom_date=datetime.now(),
        )
        
        return papers


__all__ = [
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
]
