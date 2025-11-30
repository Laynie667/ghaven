"""
Slavery NPC Types
=================

NPCs for the slavery system:
- Slavers (capture)
- Handlers (transport, management)
- Examiners (physical, sexual, mental)
- Trainers (track-specific)
- Breakers (breaking resistance)
- Auctioneers (sales)
"""

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any, Tuple
from enum import Enum
from datetime import datetime
import random


# =============================================================================
# ENUMS
# =============================================================================

class SlaveryNPCRole(Enum):
    """Roles for slavery NPCs."""
    SLAVER = "slaver"
    HANDLER = "handler"
    EXAMINER = "examiner"
    TRAINER = "trainer"
    BREAKER = "breaker"
    AUCTIONEER = "auctioneer"
    GUARD = "guard"
    VETERINARIAN = "veterinarian"


class TrainerSpecialty(Enum):
    """Trainer specializations."""
    GENERAL = "general"
    OBEDIENCE = "obedience"
    SEXUAL = "sexual"
    PONY = "pony"
    HUCOW = "hucow"
    PET = "pet"
    DOMESTIC = "domestic"
    COMBAT = "combat"


class ExaminerSpecialty(Enum):
    """Examiner specializations."""
    PHYSICAL = "physical"
    SEXUAL = "sexual"
    MENTAL = "mental"
    MEDICAL = "medical"
    APTITUDE = "aptitude"


# =============================================================================
# BASE NPC
# =============================================================================

@dataclass
class SlaveryNPCBase:
    """Base class for slavery NPCs."""
    npc_id: str
    name: str
    role: SlaveryNPCRole
    
    # Stats
    skill_level: int = 50         # 0-100
    reputation: int = 50          # 0-100
    cruelty: int = 50             # 0-100, affects methods
    efficiency: int = 50          # 0-100, affects speed
    
    # Employment
    employer: str = ""            # Faction or owner
    facility_id: str = ""         # Assigned facility
    
    # Tracking
    subjects_handled: int = 0
    
    def get_effectiveness(self) -> int:
        """Calculate overall effectiveness."""
        return (self.skill_level + self.efficiency) // 2


# =============================================================================
# SLAVER
# =============================================================================

@dataclass
class SlaverNPC(SlaveryNPCBase):
    """NPC that captures slaves."""
    
    # Capture stats
    captures_made: int = 0
    capture_success_rate: float = 0.7
    
    # Methods
    preferred_methods: List[str] = field(default_factory=list)
    # e.g., ["ambush", "trap", "drugging", "combat"]
    
    # Territory
    hunting_grounds: List[str] = field(default_factory=list)
    
    # Equipment
    equipment: List[str] = field(default_factory=list)
    # e.g., ["nets", "ropes", "tranquilizers", "cage_wagon"]
    
    def __post_init__(self):
        self.role = SlaveryNPCRole.SLAVER
        if not self.preferred_methods:
            self.preferred_methods = ["subdued", "ambush"]
        if not self.equipment:
            self.equipment = ["ropes", "collar"]
    
    def attempt_capture(self, target_strength: int = 50) -> Tuple[bool, str]:
        """
        Attempt to capture a target.
        Returns (success, message).
        """
        # Base chance from success rate
        chance = self.capture_success_rate
        
        # Modify by skill vs target strength
        skill_mod = (self.skill_level - target_strength) / 100
        chance += skill_mod * 0.3
        
        # Modify by efficiency
        chance += (self.efficiency - 50) / 200
        
        # Roll
        roll = random.random()
        
        if roll < chance:
            self.captures_made += 1
            self.subjects_handled += 1
            return True, f"{self.name} successfully captures the target!"
        else:
            return False, f"{self.name} fails to capture the target."
    
    def get_capture_message(self, method: str, target_name: str) -> str:
        """Get flavor text for capture."""
        messages = {
            "ambush": f"{self.name} springs from hiding, grabbing {target_name} before they can react!",
            "trap": f"{target_name} triggers {self.name}'s trap and is caught!",
            "net": f"{self.name} throws a net over {target_name}, tangling them hopelessly!",
            "combat": f"{self.name} defeats {target_name} and binds them!",
            "drugged": f"{target_name} collapses as {self.name}'s drugs take effect!",
            "subdued": f"{self.name} overpowers {target_name} and restrains them!",
            "lured": f"{target_name} follows {self.name}'s lure right into captivity!",
        }
        return messages.get(method, f"{self.name} captures {target_name}!")


# =============================================================================
# HANDLER
# =============================================================================

@dataclass
class HandlerNPC(SlaveryNPCBase):
    """NPC that manages and transports slaves."""
    
    # Current charges
    current_charges: List[str] = field(default_factory=list)
    max_charges: int = 5
    
    # Transport
    has_transport: bool = False
    transport_type: str = ""      # "wagon", "ship", "on_foot"
    
    # Management style
    strictness: int = 50          # 0-100
    
    def __post_init__(self):
        self.role = SlaveryNPCRole.HANDLER
    
    def add_charge(self, slave_dbref: str) -> Tuple[bool, str]:
        """Add a slave to handler's charges."""
        if len(self.current_charges) >= self.max_charges:
            return False, f"{self.name} has too many charges already."
        
        self.current_charges.append(slave_dbref)
        self.subjects_handled += 1
        return True, f"{self.name} takes charge of the slave."
    
    def remove_charge(self, slave_dbref: str) -> Tuple[bool, str]:
        """Remove a slave from charges."""
        if slave_dbref not in self.current_charges:
            return False, "Not one of this handler's charges."
        
        self.current_charges.remove(slave_dbref)
        return True, f"{self.name} releases the slave to another's care."
    
    def discipline_charge(self, slave_dbref: str) -> str:
        """Discipline a charge."""
        if slave_dbref not in self.current_charges:
            return "Not one of this handler's charges."
        
        if self.cruelty > 70:
            return f"{self.name} delivers a harsh punishment."
        elif self.cruelty > 40:
            return f"{self.name} issues a firm correction."
        else:
            return f"{self.name} gives a stern warning."


# =============================================================================
# EXAMINER
# =============================================================================

@dataclass
class ExaminerNPC(SlaveryNPCBase):
    """NPC that examines slaves."""
    
    # Specialty
    specialty: ExaminerSpecialty = ExaminerSpecialty.PHYSICAL
    additional_specialties: List[str] = field(default_factory=list)
    
    # Exam stats
    exams_performed: int = 0
    thoroughness: int = 50        # 0-100, affects detail
    
    # Style
    clinical: bool = True         # Clinical vs hands-on
    
    def __post_init__(self):
        self.role = SlaveryNPCRole.EXAMINER
    
    def can_perform_exam(self, exam_type: str) -> bool:
        """Check if examiner can perform this exam type."""
        if self.specialty.value == exam_type:
            return True
        return exam_type in self.additional_specialties
    
    def perform_exam(self, exam_type: str) -> Tuple[bool, str, int]:
        """
        Perform an examination.
        Returns (success, message, quality_score).
        """
        if not self.can_perform_exam(exam_type):
            return False, f"{self.name} is not qualified for {exam_type} exams.", 0
        
        # Calculate quality
        quality = self.skill_level
        quality += (self.thoroughness - 50) // 2
        quality = min(100, max(0, quality + random.randint(-10, 10)))
        
        self.exams_performed += 1
        self.subjects_handled += 1
        
        return True, f"{self.name} completes the {exam_type} examination.", quality
    
    def get_exam_description(self, exam_type: str, target_name: str) -> str:
        """Get exam flavor text."""
        if self.clinical:
            style = "clinically and efficiently"
        else:
            style = "thoroughly and intimately"
        
        descs = {
            "physical": f"{self.name} examines {target_name}'s body {style}, measuring and recording every detail.",
            "sexual": f"{self.name} conducts a sexual evaluation of {target_name}, testing responses and capabilities.",
            "mental": f"{self.name} probes {target_name}'s mind, assessing intelligence, will, and personality.",
            "medical": f"{self.name} performs a medical examination of {target_name}, checking health and fertility.",
            "aptitude": f"{self.name} puts {target_name} through a series of tests to determine their aptitudes.",
        }
        return descs.get(exam_type, f"{self.name} examines {target_name}.")


# =============================================================================
# TRAINER
# =============================================================================

@dataclass
class TrainerNPC(SlaveryNPCBase):
    """NPC that trains slaves."""
    
    # Specialty
    specialty: TrainerSpecialty = TrainerSpecialty.GENERAL
    additional_specialties: List[str] = field(default_factory=list)
    
    # Training stats
    slaves_trained: int = 0
    current_trainees: List[str] = field(default_factory=list)
    max_trainees: int = 3
    
    # Methods
    uses_rewards: bool = True
    uses_punishment: bool = True
    uses_pleasure: bool = False
    uses_pain: bool = False
    
    # Effectiveness modifiers
    patience: int = 50            # Affects difficult trainees
    creativity: int = 50          # Affects variety of methods
    
    def __post_init__(self):
        self.role = SlaveryNPCRole.TRAINER
    
    def can_train(self, track_type: str) -> bool:
        """Check if trainer can train this track."""
        # General trainers can do basic training for any track
        if self.specialty == TrainerSpecialty.GENERAL:
            return True
        if self.specialty.value == track_type:
            return True
        return track_type in self.additional_specialties
    
    def add_trainee(self, slave_dbref: str) -> Tuple[bool, str]:
        """Add a trainee."""
        if len(self.current_trainees) >= self.max_trainees:
            return False, f"{self.name} has too many trainees."
        
        self.current_trainees.append(slave_dbref)
        return True, f"{self.name} accepts a new trainee."
    
    def remove_trainee(self, slave_dbref: str) -> Tuple[bool, str]:
        """Remove a trainee."""
        if slave_dbref not in self.current_trainees:
            return False, "Not training this slave."
        
        self.current_trainees.remove(slave_dbref)
        self.slaves_trained += 1
        self.subjects_handled += 1
        return True, f"{self.name} concludes training."
    
    def conduct_session(self, hours: int = 1) -> Tuple[str, int]:
        """
        Conduct a training session.
        Returns (message, skill_gain).
        """
        base_gain = self.skill_level // 10
        
        # Modify by efficiency
        base_gain = int(base_gain * (0.5 + self.efficiency / 100))
        
        # Modify by hours
        base_gain *= hours
        
        # Add randomness
        base_gain += random.randint(-2, 5)
        base_gain = max(1, base_gain)
        
        method = self._get_training_method()
        
        return f"{self.name} conducts training using {method}.", base_gain
    
    def _get_training_method(self) -> str:
        """Get training method based on trainer style."""
        methods = []
        if self.uses_rewards:
            methods.append("positive reinforcement")
        if self.uses_punishment:
            methods.append("discipline")
        if self.uses_pleasure:
            methods.append("pleasure conditioning")
        if self.uses_pain:
            methods.append("pain training")
        
        if not methods:
            methods = ["repetition"]
        
        return random.choice(methods)
    
    def get_specialty_description(self) -> str:
        """Get description of specialty."""
        descs = {
            TrainerSpecialty.GENERAL: "basic obedience and behavior",
            TrainerSpecialty.OBEDIENCE: "strict obedience and command response",
            TrainerSpecialty.SEXUAL: "sexual service and pleasure techniques",
            TrainerSpecialty.PONY: "pony behavior, gaits, and tack",
            TrainerSpecialty.HUCOW: "lactation, milking compliance, and herd behavior",
            TrainerSpecialty.PET: "pet behavior and owner bonding",
            TrainerSpecialty.DOMESTIC: "domestic service and household duties",
            TrainerSpecialty.COMBAT: "fighting skills and combat obedience",
        }
        return descs.get(self.specialty, "specialized training")


# =============================================================================
# BREAKER
# =============================================================================

@dataclass
class BreakerNPC(SlaveryNPCBase):
    """NPC that breaks resistant slaves."""
    
    # Breaking stats
    slaves_broken: int = 0
    current_subject: str = ""
    
    # Methods
    methods: List[str] = field(default_factory=list)
    # e.g., ["isolation", "sleep_deprivation", "pleasure", "pain", "humiliation"]
    
    # Intensity
    intensity: int = 50           # 0-100
    
    # Tracking current breaking
    sessions_with_current: int = 0
    
    def __post_init__(self):
        self.role = SlaveryNPCRole.BREAKER
        if not self.methods:
            self.methods = ["discipline", "isolation", "conditioning"]
    
    def begin_breaking(self, slave_dbref: str) -> str:
        """Begin breaking a slave."""
        self.current_subject = slave_dbref
        self.sessions_with_current = 0
        return f"{self.name} begins the breaking process."
    
    def conduct_session(self, target_willpower: int = 50) -> Tuple[str, int, bool]:
        """
        Conduct a breaking session.
        Returns (message, willpower_reduction, is_broken).
        """
        self.sessions_with_current += 1
        
        # Calculate effectiveness
        effectiveness = self.skill_level + self.cruelty // 2
        effectiveness = int(effectiveness * (0.5 + self.intensity / 100))
        
        # Calculate willpower reduction
        reduction = effectiveness // 5
        reduction += random.randint(-3, 5)
        reduction = max(1, reduction)
        
        # Check if broken
        new_willpower = target_willpower - reduction
        is_broken = new_willpower <= 10
        
        if is_broken:
            self.slaves_broken += 1
            self.subjects_handled += 1
            self.current_subject = ""
            return f"{self.name} completes the breaking. The slave's will is shattered.", reduction, True
        
        method = random.choice(self.methods)
        return f"{self.name} applies {method}. The slave weakens...", reduction, False
    
    def end_breaking(self) -> str:
        """End current breaking."""
        self.current_subject = ""
        return f"{self.name} concludes the breaking process."


# =============================================================================
# AUCTIONEER
# =============================================================================

@dataclass
class AuctioneerNPC(SlaveryNPCBase):
    """NPC that conducts slave auctions."""
    
    # Auction stats
    auctions_conducted: int = 0
    total_sales_value: int = 0
    
    # Style
    showmanship: int = 50         # 0-100, affects audience engagement
    
    # Current auction
    current_lot: str = ""
    current_bid: int = 0
    bidders: List[str] = field(default_factory=list)
    
    def __post_init__(self):
        self.role = SlaveryNPCRole.AUCTIONEER
    
    def start_auction(self, slave_dbref: str, starting_bid: int) -> str:
        """Start an auction."""
        self.current_lot = slave_dbref
        self.current_bid = starting_bid
        self.bidders = []
        return f"{self.name} calls the auction to order!"
    
    def accept_bid(self, bidder: str, amount: int) -> Tuple[bool, str]:
        """Accept a bid."""
        if amount <= self.current_bid:
            return False, f"Bid must be higher than {self.current_bid}!"
        
        self.current_bid = amount
        if bidder not in self.bidders:
            self.bidders.append(bidder)
        
        return True, f"{self.name} announces: '{amount} gold! Do I hear more?'"
    
    def close_auction(self, winner: str) -> Tuple[int, str]:
        """
        Close the auction.
        Returns (final_price, message).
        """
        final_price = self.current_bid
        self.total_sales_value += final_price
        self.auctions_conducted += 1
        self.subjects_handled += 1
        
        self.current_lot = ""
        self.current_bid = 0
        self.bidders = []
        
        return final_price, f"{self.name} declares: 'SOLD to {winner} for {final_price} gold!'"
    
    def describe_lot(self, slave_name: str, details: Dict[str, Any]) -> str:
        """Get auctioneer's description of a lot."""
        lines = [f"{self.name} presents the merchandise:"]
        lines.append(f"'Ladies and gentlemen, I present {slave_name}!'")
        
        if details.get("training_track"):
            lines.append(f"'Trained as a {details['training_track']}!'")
        if details.get("value_grade"):
            lines.append(f"'Graded as {details['value_grade']} quality!'")
        if details.get("virgin"):
            lines.append(f"'Still pure and untouched!'")
        if details.get("special_features"):
            for feature in details['special_features']:
                lines.append(f"'{feature}!'")
        
        return "\n".join(lines)


# =============================================================================
# GUARD
# =============================================================================

@dataclass
class GuardNPC(SlaveryNPCBase):
    """NPC that guards facilities and slaves."""
    
    # Combat stats
    combat_skill: int = 50
    alertness: int = 50
    
    # Equipment
    armed: bool = True
    weapon_type: str = "club"
    has_restraints: bool = True
    
    # Patrol
    patrol_route: List[str] = field(default_factory=list)
    current_position: str = ""
    
    def __post_init__(self):
        self.role = SlaveryNPCRole.GUARD
    
    def attempt_stop_escape(self, escapee_skill: int = 50) -> Tuple[bool, str]:
        """
        Attempt to stop an escape.
        Returns (success, message).
        """
        # Guard's chance
        guard_roll = self.combat_skill + self.alertness + random.randint(-20, 20)
        escapee_roll = escapee_skill + random.randint(-20, 20)
        
        if guard_roll > escapee_roll:
            self.subjects_handled += 1
            return True, f"{self.name} intercepts the escapee!"
        else:
            return False, f"{self.name} fails to stop the escape!"
    
    def restrain_subject(self, subject_name: str) -> str:
        """Restrain a subject."""
        if self.has_restraints:
            return f"{self.name} quickly restrains {subject_name}."
        else:
            return f"{self.name} holds {subject_name} in place."


# =============================================================================
# VETERINARIAN
# =============================================================================

@dataclass
class VeterinarianNPC(SlaveryNPCBase):
    """NPC that handles medical/breeding aspects."""
    
    # Medical stats
    medical_skill: int = 50
    breeding_knowledge: int = 50
    
    # Specialties
    specialties: List[str] = field(default_factory=list)
    # e.g., ["fertility", "lactation", "general_health", "modifications"]
    
    def __post_init__(self):
        self.role = SlaveryNPCRole.VETERINARIAN
        if not self.specialties:
            self.specialties = ["general_health"]
    
    def health_check(self, subject_name: str) -> Tuple[str, int]:
        """
        Perform a health check.
        Returns (message, health_score).
        """
        health = random.randint(60, 100)  # Simplified
        health += (self.medical_skill - 50) // 5
        health = min(100, max(0, health))
        
        self.subjects_handled += 1
        
        return f"{self.name} completes health assessment of {subject_name}.", health
    
    def fertility_check(self, subject_name: str) -> Tuple[str, int]:
        """
        Check fertility.
        Returns (message, fertility_score).
        """
        if "fertility" not in self.specialties:
            return f"{self.name} is not a fertility specialist.", 0
        
        fertility = random.randint(40, 90)
        fertility += (self.breeding_knowledge - 50) // 5
        fertility = min(100, max(0, fertility))
        
        return f"{self.name} assesses {subject_name}'s fertility.", fertility
    
    def induce_lactation(self, subject_name: str) -> str:
        """Induce lactation in a subject."""
        if "lactation" not in self.specialties:
            return f"{self.name} is not a lactation specialist."
        
        self.subjects_handled += 1
        return f"{self.name} begins lactation induction treatment for {subject_name}."


# =============================================================================
# NPC FACTORY
# =============================================================================

class SlaveryNPCFactory:
    """Factory for creating slavery NPCs."""
    
    @staticmethod
    def generate_id(prefix: str = "NPC") -> str:
        """Generate unique ID."""
        timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
        rand = random.randint(1000, 9999)
        return f"{prefix}-{timestamp}-{rand}"
    
    @staticmethod
    def create_slaver(name: str, skill: int = 50) -> SlaverNPC:
        """Create a slaver NPC."""
        return SlaverNPC(
            npc_id=SlaveryNPCFactory.generate_id("SLV"),
            name=name,
            role=SlaveryNPCRole.SLAVER,
            skill_level=skill,
        )
    
    @staticmethod
    def create_handler(name: str, skill: int = 50) -> HandlerNPC:
        """Create a handler NPC."""
        return HandlerNPC(
            npc_id=SlaveryNPCFactory.generate_id("HND"),
            name=name,
            role=SlaveryNPCRole.HANDLER,
            skill_level=skill,
        )
    
    @staticmethod
    def create_examiner(
        name: str,
        specialty: ExaminerSpecialty,
        skill: int = 50,
    ) -> ExaminerNPC:
        """Create an examiner NPC."""
        return ExaminerNPC(
            npc_id=SlaveryNPCFactory.generate_id("EXM"),
            name=name,
            role=SlaveryNPCRole.EXAMINER,
            skill_level=skill,
            specialty=specialty,
        )
    
    @staticmethod
    def create_trainer(
        name: str,
        specialty: TrainerSpecialty,
        skill: int = 50,
    ) -> TrainerNPC:
        """Create a trainer NPC."""
        return TrainerNPC(
            npc_id=SlaveryNPCFactory.generate_id("TRN"),
            name=name,
            role=SlaveryNPCRole.TRAINER,
            skill_level=skill,
            specialty=specialty,
        )
    
    @staticmethod
    def create_breaker(name: str, skill: int = 50, cruelty: int = 60) -> BreakerNPC:
        """Create a breaker NPC."""
        return BreakerNPC(
            npc_id=SlaveryNPCFactory.generate_id("BRK"),
            name=name,
            role=SlaveryNPCRole.BREAKER,
            skill_level=skill,
            cruelty=cruelty,
        )
    
    @staticmethod
    def create_auctioneer(name: str, skill: int = 50) -> AuctioneerNPC:
        """Create an auctioneer NPC."""
        return AuctioneerNPC(
            npc_id=SlaveryNPCFactory.generate_id("AUC"),
            name=name,
            role=SlaveryNPCRole.AUCTIONEER,
            skill_level=skill,
        )
    
    @staticmethod
    def create_guard(name: str, combat: int = 50) -> GuardNPC:
        """Create a guard NPC."""
        return GuardNPC(
            npc_id=SlaveryNPCFactory.generate_id("GRD"),
            name=name,
            role=SlaveryNPCRole.GUARD,
            skill_level=combat,
            combat_skill=combat,
        )
    
    @staticmethod
    def create_veterinarian(name: str, skill: int = 50) -> VeterinarianNPC:
        """Create a veterinarian NPC."""
        return VeterinarianNPC(
            npc_id=SlaveryNPCFactory.generate_id("VET"),
            name=name,
            role=SlaveryNPCRole.VETERINARIAN,
            skill_level=skill,
            medical_skill=skill,
        )


__all__ = [
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
]
