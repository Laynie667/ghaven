"""
Processing System
=================

The intake pipeline:
- Initial intake
- Physical examination
- Aptitude testing
- Classification
- Marking/branding
"""

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any, Tuple
from enum import Enum
from datetime import datetime
import random


# =============================================================================
# ENUMS
# =============================================================================

class ProcessingStage(Enum):
    """Stages of processing."""
    INTAKE = "intake"
    HOLDING = "holding"
    EXAMINATION = "examination"
    TESTING = "testing"
    CLASSIFICATION = "classification"
    MARKING = "marking"
    BREAKING = "breaking"
    TRAINING = "training"
    PLACEMENT = "placement"
    COMPLETE = "complete"


class ExaminationType(Enum):
    """Types of examinations."""
    PHYSICAL = "physical"
    SEXUAL = "sexual"
    MEDICAL = "medical"
    MENTAL = "mental"
    OBEDIENCE = "obedience"


class AptitudeCategory(Enum):
    """Categories of aptitude."""
    SEXUAL = "sexual"
    DOMESTIC = "domestic"
    LABOR = "labor"
    BREEDING = "breeding"
    ENTERTAINMENT = "entertainment"
    COMBAT = "combat"
    INTELLIGENCE = "intelligence"
    OBEDIENCE = "obedience"


class TrainingTrack(Enum):
    """Training specializations."""
    HUCOW = "hucow"
    PLEASURE = "pleasure"
    PONY = "pony"
    BREEDING = "breeding"
    HOUSE = "house"
    FIELD = "field"
    DISPLAY = "display"
    FIGHTER = "fighter"
    ENTERTAINMENT = "entertainment"
    PET = "pet"
    TOY = "toy"
    CONCUBINE = "concubine"
    GENERAL = "general"


class ValueGrade(Enum):
    """Quality grades."""
    COMMON = "common"
    QUALITY = "quality"
    PREMIUM = "premium"
    EXCEPTIONAL = "exceptional"
    PRICELESS = "priceless"


# =============================================================================
# EXAMINATION RESULTS
# =============================================================================

@dataclass
class PhysicalExam:
    """Results of physical examination."""
    exam_id: str
    subject_dbref: str = ""
    subject_name: str = ""
    
    # Basic measurements
    height_cm: int = 0
    weight_kg: int = 0
    
    # Physical attributes (0-100)
    strength: int = 50
    endurance: int = 50
    flexibility: int = 50
    health: int = 50
    
    # Appearance (0-100)
    facial_beauty: int = 50
    body_beauty: int = 50
    skin_quality: int = 50
    
    # Physical features
    hair_color: str = ""
    eye_color: str = ""
    skin_tone: str = ""
    body_type: str = ""           # "slim", "athletic", "curvy", "muscular", etc.
    
    # Notable features
    scars: List[str] = field(default_factory=list)
    birthmarks: List[str] = field(default_factory=list)
    tattoos: List[str] = field(default_factory=list)
    piercings: List[str] = field(default_factory=list)
    
    # Defects
    defects: List[str] = field(default_factory=list)
    
    # Examiner notes
    examiner_name: str = ""
    exam_date: Optional[datetime] = None
    notes: str = ""
    
    def get_appearance_score(self) -> int:
        """Calculate overall appearance score."""
        return (self.facial_beauty + self.body_beauty + self.skin_quality) // 3
    
    def get_fitness_score(self) -> int:
        """Calculate overall fitness score."""
        return (self.strength + self.endurance + self.flexibility + self.health) // 4
    
    def to_dict(self) -> dict:
        return {
            "exam_id": self.exam_id,
            "subject_dbref": self.subject_dbref,
            "subject_name": self.subject_name,
            "height_cm": self.height_cm,
            "weight_kg": self.weight_kg,
            "strength": self.strength,
            "endurance": self.endurance,
            "flexibility": self.flexibility,
            "health": self.health,
            "facial_beauty": self.facial_beauty,
            "body_beauty": self.body_beauty,
            "skin_quality": self.skin_quality,
            "hair_color": self.hair_color,
            "eye_color": self.eye_color,
            "skin_tone": self.skin_tone,
            "body_type": self.body_type,
            "scars": self.scars,
            "birthmarks": self.birthmarks,
            "tattoos": self.tattoos,
            "piercings": self.piercings,
            "defects": self.defects,
            "examiner_name": self.examiner_name,
            "exam_date": self.exam_date.isoformat() if self.exam_date else None,
            "notes": self.notes,
        }


@dataclass
class SexualExam:
    """Results of sexual examination."""
    exam_id: str
    subject_dbref: str = ""
    subject_name: str = ""
    
    # Basic
    sex: str = ""                 # "male", "female", "herm", etc.
    virginity: Dict[str, bool] = field(default_factory=dict)
    # {"vaginal": True, "anal": True, "oral": False}
    
    # Attributes (0-100)
    sensitivity: int = 50
    responsiveness: int = 50
    libido: int = 50
    stamina: int = 50
    
    # Female attributes
    breast_size: str = ""
    breast_sensitivity: int = 50
    lactation_potential: int = 0
    vaginal_tightness: int = 50
    
    # Male attributes
    penis_size: str = ""
    testicular_size: str = ""
    refractory_period: int = 50   # Lower = faster recovery
    
    # Fertility
    fertility_rating: int = 50
    fertility_tested: bool = False
    
    # Experience indicators
    experience_level: str = ""    # "virgin", "novice", "experienced", "expert"
    known_skills: List[str] = field(default_factory=list)
    
    # Response testing
    responds_to_pain: bool = False
    responds_to_pleasure: bool = True
    orgasm_ease: int = 50         # How easily they orgasm
    multi_orgasmic: bool = False
    
    # Notes
    examiner_name: str = ""
    exam_date: Optional[datetime] = None
    notes: str = ""
    
    def get_sexual_value_score(self) -> int:
        """Calculate sexual value score."""
        base = (self.sensitivity + self.responsiveness + self.libido + self.stamina) // 4
        
        # Virginity bonus
        if self.virginity.get("vaginal") or self.virginity.get("anal"):
            base += 20
        
        return min(100, base)
    
    def to_dict(self) -> dict:
        return {
            "exam_id": self.exam_id,
            "subject_dbref": self.subject_dbref,
            "subject_name": self.subject_name,
            "sex": self.sex,
            "virginity": self.virginity,
            "sensitivity": self.sensitivity,
            "responsiveness": self.responsiveness,
            "libido": self.libido,
            "stamina": self.stamina,
            "breast_size": self.breast_size,
            "breast_sensitivity": self.breast_sensitivity,
            "lactation_potential": self.lactation_potential,
            "vaginal_tightness": self.vaginal_tightness,
            "penis_size": self.penis_size,
            "testicular_size": self.testicular_size,
            "refractory_period": self.refractory_period,
            "fertility_rating": self.fertility_rating,
            "fertility_tested": self.fertility_tested,
            "experience_level": self.experience_level,
            "known_skills": self.known_skills,
            "responds_to_pain": self.responds_to_pain,
            "responds_to_pleasure": self.responds_to_pleasure,
            "orgasm_ease": self.orgasm_ease,
            "multi_orgasmic": self.multi_orgasmic,
            "examiner_name": self.examiner_name,
            "exam_date": self.exam_date.isoformat() if self.exam_date else None,
            "notes": self.notes,
        }


@dataclass
class MentalExam:
    """Results of mental/psychological examination."""
    exam_id: str
    subject_dbref: str = ""
    subject_name: str = ""
    
    # Intelligence (0-100)
    intelligence: int = 50
    memory: int = 50
    learning_speed: int = 50
    
    # Personality
    willpower: int = 50
    submission_tendency: int = 50  # Natural inclination
    obedience: int = 50
    defiance: int = 50
    
    # Emotional
    emotional_stability: int = 50
    fear_response: int = 50
    pain_tolerance: int = 50
    pleasure_seeking: int = 50
    
    # Psychological traits
    traits: List[str] = field(default_factory=list)
    # e.g., ["submissive", "masochistic", "eager to please", "rebellious"]
    
    # Fears and triggers
    fears: List[str] = field(default_factory=list)
    triggers: List[str] = field(default_factory=list)
    
    # Breaking assessment
    estimated_break_difficulty: int = 50  # How hard to break
    recommended_methods: List[str] = field(default_factory=list)
    
    # Notes
    examiner_name: str = ""
    exam_date: Optional[datetime] = None
    notes: str = ""
    
    def get_trainability_score(self) -> int:
        """Calculate how trainable they are."""
        # High intelligence, high submission, low defiance = easy to train
        base = self.intelligence // 2 + self.submission_tendency // 2
        base -= self.defiance // 4
        base += self.learning_speed // 4
        return max(0, min(100, base))
    
    def to_dict(self) -> dict:
        return {
            "exam_id": self.exam_id,
            "subject_dbref": self.subject_dbref,
            "subject_name": self.subject_name,
            "intelligence": self.intelligence,
            "memory": self.memory,
            "learning_speed": self.learning_speed,
            "willpower": self.willpower,
            "submission_tendency": self.submission_tendency,
            "obedience": self.obedience,
            "defiance": self.defiance,
            "emotional_stability": self.emotional_stability,
            "fear_response": self.fear_response,
            "pain_tolerance": self.pain_tolerance,
            "pleasure_seeking": self.pleasure_seeking,
            "traits": self.traits,
            "fears": self.fears,
            "triggers": self.triggers,
            "estimated_break_difficulty": self.estimated_break_difficulty,
            "recommended_methods": self.recommended_methods,
            "examiner_name": self.examiner_name,
            "exam_date": self.exam_date.isoformat() if self.exam_date else None,
            "notes": self.notes,
        }


# =============================================================================
# APTITUDE TESTING
# =============================================================================

@dataclass
class AptitudeTest:
    """Results of aptitude testing."""
    test_id: str
    subject_dbref: str = ""
    subject_name: str = ""
    
    # Scores by category (0-100)
    aptitudes: Dict[str, int] = field(default_factory=dict)
    # {
    #   "sexual": 75,
    #   "domestic": 60,
    #   "labor": 40,
    #   "breeding": 80,
    #   "entertainment": 55,
    #   "combat": 30,
    #   "intelligence": 65,
    #   "obedience": 70,
    # }
    
    # Recommended tracks based on testing
    primary_recommendation: str = ""
    secondary_recommendations: List[str] = field(default_factory=list)
    
    # Specific skill indicators
    skill_indicators: Dict[str, int] = field(default_factory=dict)
    # More specific: {"oral_skill": 60, "massage": 45, "cooking": 30}
    
    # Testing notes
    tester_name: str = ""
    test_date: Optional[datetime] = None
    notes: str = ""
    
    def get_highest_aptitude(self) -> Tuple[str, int]:
        """Get highest aptitude."""
        if not self.aptitudes:
            return "", 0
        return max(self.aptitudes.items(), key=lambda x: x[1])
    
    def recommend_track(self) -> str:
        """Recommend a training track based on aptitudes."""
        if not self.aptitudes:
            return TrainingTrack.GENERAL.value
        
        # Track mapping
        track_aptitudes = {
            TrainingTrack.HUCOW.value: ["breeding", "domestic", "obedience"],
            TrainingTrack.PLEASURE.value: ["sexual", "obedience"],
            TrainingTrack.PONY.value: ["labor", "obedience", "entertainment"],
            TrainingTrack.BREEDING.value: ["breeding", "sexual"],
            TrainingTrack.HOUSE.value: ["domestic", "obedience", "intelligence"],
            TrainingTrack.FIELD.value: ["labor"],
            TrainingTrack.DISPLAY.value: ["entertainment", "sexual"],
            TrainingTrack.FIGHTER.value: ["combat"],
            TrainingTrack.ENTERTAINMENT.value: ["entertainment", "sexual"],
            TrainingTrack.PET.value: ["obedience", "domestic"],
            TrainingTrack.TOY.value: ["sexual", "obedience"],
            TrainingTrack.CONCUBINE.value: ["sexual", "intelligence", "entertainment"],
        }
        
        best_track = TrainingTrack.GENERAL.value
        best_score = 0
        
        for track, required_aptitudes in track_aptitudes.items():
            score = sum(self.aptitudes.get(apt, 0) for apt in required_aptitudes)
            avg_score = score // len(required_aptitudes) if required_aptitudes else 0
            
            if avg_score > best_score:
                best_score = avg_score
                best_track = track
        
        return best_track
    
    def to_dict(self) -> dict:
        return {
            "test_id": self.test_id,
            "subject_dbref": self.subject_dbref,
            "subject_name": self.subject_name,
            "aptitudes": self.aptitudes,
            "primary_recommendation": self.primary_recommendation,
            "secondary_recommendations": self.secondary_recommendations,
            "skill_indicators": self.skill_indicators,
            "tester_name": self.tester_name,
            "test_date": self.test_date.isoformat() if self.test_date else None,
            "notes": self.notes,
        }


# =============================================================================
# CLASSIFICATION
# =============================================================================

@dataclass
class Classification:
    """Final classification of a slave."""
    classification_id: str
    subject_dbref: str = ""
    subject_name: str = ""
    
    # Assigned track
    training_track: TrainingTrack = TrainingTrack.GENERAL
    
    # Grade
    value_grade: ValueGrade = ValueGrade.COMMON
    estimated_value: int = 0
    
    # Based on exams
    physical_exam_id: str = ""
    sexual_exam_id: str = ""
    mental_exam_id: str = ""
    aptitude_test_id: str = ""
    
    # Summary scores
    appearance_score: int = 0
    fitness_score: int = 0
    sexual_score: int = 0
    trainability_score: int = 0
    overall_score: int = 0
    
    # Special designations
    designations: List[str] = field(default_factory=list)
    # e.g., ["virgin", "breeder", "lactating", "exotic species"]
    
    # Restrictions/warnings
    restrictions: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)
    
    # Classification details
    classifier_name: str = ""
    classification_date: Optional[datetime] = None
    classification_location: str = ""
    notes: str = ""
    
    def calculate_value(self) -> int:
        """Calculate estimated value based on scores."""
        base_values = {
            ValueGrade.COMMON: 100,
            ValueGrade.QUALITY: 300,
            ValueGrade.PREMIUM: 750,
            ValueGrade.EXCEPTIONAL: 2000,
            ValueGrade.PRICELESS: 5000,
        }
        
        base = base_values.get(self.value_grade, 100)
        
        # Modify by overall score
        score_mult = 0.5 + (self.overall_score / 100)
        
        # Special designation bonuses
        if "virgin" in self.designations:
            score_mult += 0.3
        if "exotic species" in self.designations:
            score_mult += 0.5
        if "breeder" in self.designations:
            score_mult += 0.2
        
        return int(base * score_mult)
    
    def determine_grade(self) -> ValueGrade:
        """Determine grade based on overall score."""
        if self.overall_score >= 90:
            return ValueGrade.PRICELESS
        elif self.overall_score >= 75:
            return ValueGrade.EXCEPTIONAL
        elif self.overall_score >= 60:
            return ValueGrade.PREMIUM
        elif self.overall_score >= 40:
            return ValueGrade.QUALITY
        else:
            return ValueGrade.COMMON
    
    def get_classification_display(self) -> str:
        """Get formatted classification."""
        lines = [
            "╔═══════════════════════════════════════════════╗",
            "║         SLAVE CLASSIFICATION                   ║",
            "╠═══════════════════════════════════════════════╣",
            f"║ Subject: {self.subject_name:<36}║",
            "╠═══════════════════════════════════════════════╣",
            f"║ Track: {self.training_track.value.upper():<38}║",
            f"║ Grade: {self.value_grade.value.upper():<38}║",
            f"║ Estimated Value: {self.estimated_value} gold{' ' * (24 - len(str(self.estimated_value)))}║",
            "╠═══════════════════════════════════════════════╣",
            "║ SCORES:                                        ║",
            f"║   Appearance: {self.appearance_score}/100{' ' * 27}║",
            f"║   Fitness: {self.fitness_score}/100{' ' * 30}║",
            f"║   Sexual: {self.sexual_score}/100{' ' * 31}║",
            f"║   Trainability: {self.trainability_score}/100{' ' * 25}║",
            f"║   OVERALL: {self.overall_score}/100{' ' * 30}║",
        ]
        
        if self.designations:
            lines.append("╠═══════════════════════════════════════════════╣")
            lines.append(f"║ Designations: {', '.join(self.designations):<31}║")
        
        if self.warnings:
            lines.append("╠═══════════════════════════════════════════════╣")
            for warning in self.warnings[:3]:
                lines.append(f"║ ⚠ {warning:<42}║")
        
        lines.append("╚═══════════════════════════════════════════════╝")
        
        return "\n".join(lines)
    
    def to_dict(self) -> dict:
        return {
            "classification_id": self.classification_id,
            "subject_dbref": self.subject_dbref,
            "subject_name": self.subject_name,
            "training_track": self.training_track.value,
            "value_grade": self.value_grade.value,
            "estimated_value": self.estimated_value,
            "physical_exam_id": self.physical_exam_id,
            "sexual_exam_id": self.sexual_exam_id,
            "mental_exam_id": self.mental_exam_id,
            "aptitude_test_id": self.aptitude_test_id,
            "appearance_score": self.appearance_score,
            "fitness_score": self.fitness_score,
            "sexual_score": self.sexual_score,
            "trainability_score": self.trainability_score,
            "overall_score": self.overall_score,
            "designations": self.designations,
            "restrictions": self.restrictions,
            "warnings": self.warnings,
            "classifier_name": self.classifier_name,
            "classification_date": self.classification_date.isoformat() if self.classification_date else None,
            "classification_location": self.classification_location,
            "notes": self.notes,
        }
    
    @classmethod
    def from_dict(cls, data: dict) -> "Classification":
        classif = cls(classification_id=data["classification_id"])
        for key, value in data.items():
            if key == "training_track":
                classif.training_track = TrainingTrack(value)
            elif key == "value_grade":
                classif.value_grade = ValueGrade(value)
            elif key == "classification_date" and value:
                classif.classification_date = datetime.fromisoformat(value)
            elif hasattr(classif, key):
                setattr(classif, key, value)
        return classif


# =============================================================================
# PROCESSING RECORD
# =============================================================================

@dataclass
class ProcessingRecord:
    """Complete processing record."""
    record_id: str
    subject_dbref: str = ""
    subject_name: str = ""
    
    # Current stage
    current_stage: ProcessingStage = ProcessingStage.INTAKE
    
    # Timestamp tracking
    intake_date: Optional[datetime] = None
    examination_date: Optional[datetime] = None
    testing_date: Optional[datetime] = None
    classification_date: Optional[datetime] = None
    marking_date: Optional[datetime] = None
    completion_date: Optional[datetime] = None
    
    # Exam records
    physical_exam: Optional[PhysicalExam] = None
    sexual_exam: Optional[SexualExam] = None
    mental_exam: Optional[MentalExam] = None
    aptitude_test: Optional[AptitudeTest] = None
    classification: Optional[Classification] = None
    
    # Assignment
    assigned_handler: str = ""
    assigned_trainer: str = ""
    assigned_facility: str = ""
    
    # Notes
    processing_notes: List[str] = field(default_factory=list)
    
    def add_note(self, note: str) -> None:
        """Add a processing note."""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M")
        self.processing_notes.append(f"[{timestamp}] {note}")
    
    def advance_stage(self) -> Tuple[ProcessingStage, str]:
        """Advance to next processing stage."""
        stages = list(ProcessingStage)
        current_idx = stages.index(self.current_stage)
        
        if current_idx < len(stages) - 1:
            self.current_stage = stages[current_idx + 1]
            self.add_note(f"Advanced to {self.current_stage.value}")
            return self.current_stage, f"Advanced to {self.current_stage.value} stage."
        
        return self.current_stage, "Already at final stage."
    
    def get_status_display(self) -> str:
        """Get processing status display."""
        lines = [f"=== Processing: {self.subject_name} ==="]
        lines.append(f"Current Stage: {self.current_stage.value.upper()}")
        
        # Stage completion indicators
        stage_status = []
        stages_order = [
            (ProcessingStage.INTAKE, self.intake_date),
            (ProcessingStage.EXAMINATION, self.examination_date),
            (ProcessingStage.TESTING, self.testing_date),
            (ProcessingStage.CLASSIFICATION, self.classification_date),
            (ProcessingStage.MARKING, self.marking_date),
            (ProcessingStage.COMPLETE, self.completion_date),
        ]
        
        for stage, date in stages_order:
            status = "✓" if date else "○"
            stage_status.append(f"  {status} {stage.value}")
        
        lines.extend(stage_status)
        
        if self.classification:
            lines.append(f"\nClassified as: {self.classification.training_track.value}")
            lines.append(f"Grade: {self.classification.value_grade.value}")
        
        return "\n".join(lines)
    
    def to_dict(self) -> dict:
        return {
            "record_id": self.record_id,
            "subject_dbref": self.subject_dbref,
            "subject_name": self.subject_name,
            "current_stage": self.current_stage.value,
            "intake_date": self.intake_date.isoformat() if self.intake_date else None,
            "examination_date": self.examination_date.isoformat() if self.examination_date else None,
            "testing_date": self.testing_date.isoformat() if self.testing_date else None,
            "classification_date": self.classification_date.isoformat() if self.classification_date else None,
            "marking_date": self.marking_date.isoformat() if self.marking_date else None,
            "completion_date": self.completion_date.isoformat() if self.completion_date else None,
            "physical_exam": self.physical_exam.to_dict() if self.physical_exam else None,
            "sexual_exam": self.sexual_exam.to_dict() if self.sexual_exam else None,
            "mental_exam": self.mental_exam.to_dict() if self.mental_exam else None,
            "aptitude_test": self.aptitude_test.to_dict() if self.aptitude_test else None,
            "classification": self.classification.to_dict() if self.classification else None,
            "assigned_handler": self.assigned_handler,
            "assigned_trainer": self.assigned_trainer,
            "assigned_facility": self.assigned_facility,
            "processing_notes": self.processing_notes,
        }
    
    @classmethod
    def from_dict(cls, data: dict) -> "ProcessingRecord":
        record = cls(record_id=data["record_id"])
        record.subject_dbref = data.get("subject_dbref", "")
        record.subject_name = data.get("subject_name", "")
        record.current_stage = ProcessingStage(data.get("current_stage", "intake"))
        
        for date_field in ["intake_date", "examination_date", "testing_date",
                          "classification_date", "marking_date", "completion_date"]:
            if data.get(date_field):
                setattr(record, date_field, datetime.fromisoformat(data[date_field]))
        
        record.assigned_handler = data.get("assigned_handler", "")
        record.assigned_trainer = data.get("assigned_trainer", "")
        record.assigned_facility = data.get("assigned_facility", "")
        record.processing_notes = data.get("processing_notes", [])
        
        return record


# =============================================================================
# PROCESSING SYSTEM
# =============================================================================

class ProcessingSystem:
    """
    Manages the slave processing pipeline.
    """
    
    @staticmethod
    def generate_id(prefix: str = "PRC") -> str:
        """Generate unique ID."""
        timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
        rand = random.randint(1000, 9999)
        return f"{prefix}-{timestamp}-{rand}"
    
    @staticmethod
    def begin_intake(subject, facility: str = "") -> ProcessingRecord:
        """Begin intake processing."""
        record = ProcessingRecord(
            record_id=ProcessingSystem.generate_id("PRC"),
            subject_dbref=subject.dbref,
            subject_name=subject.key,
            current_stage=ProcessingStage.INTAKE,
            intake_date=datetime.now(),
            assigned_facility=facility,
        )
        record.add_note("Intake processing begun")
        
        return record
    
    @staticmethod
    def perform_physical_exam(
        record: ProcessingRecord,
        examiner_name: str = "",
    ) -> PhysicalExam:
        """Perform physical examination."""
        exam = PhysicalExam(
            exam_id=ProcessingSystem.generate_id("PHY"),
            subject_dbref=record.subject_dbref,
            subject_name=record.subject_name,
            examiner_name=examiner_name,
            exam_date=datetime.now(),
        )
        
        # Randomize for demo - in real use would read from character
        exam.strength = random.randint(30, 80)
        exam.endurance = random.randint(30, 80)
        exam.flexibility = random.randint(30, 80)
        exam.health = random.randint(50, 100)
        exam.facial_beauty = random.randint(40, 90)
        exam.body_beauty = random.randint(40, 90)
        exam.skin_quality = random.randint(50, 90)
        
        record.physical_exam = exam
        record.add_note("Physical examination completed")
        
        return exam
    
    @staticmethod
    def perform_sexual_exam(
        record: ProcessingRecord,
        examiner_name: str = "",
    ) -> SexualExam:
        """Perform sexual examination."""
        exam = SexualExam(
            exam_id=ProcessingSystem.generate_id("SEX"),
            subject_dbref=record.subject_dbref,
            subject_name=record.subject_name,
            examiner_name=examiner_name,
            exam_date=datetime.now(),
        )
        
        # Randomize for demo
        exam.sensitivity = random.randint(40, 90)
        exam.responsiveness = random.randint(40, 90)
        exam.libido = random.randint(30, 80)
        exam.stamina = random.randint(30, 80)
        exam.fertility_rating = random.randint(40, 90)
        exam.orgasm_ease = random.randint(30, 80)
        
        # Random virginity
        exam.virginity = {
            "vaginal": random.random() > 0.7,
            "anal": random.random() > 0.5,
            "oral": random.random() > 0.9,
        }
        
        record.sexual_exam = exam
        record.add_note("Sexual examination completed")
        
        return exam
    
    @staticmethod
    def perform_mental_exam(
        record: ProcessingRecord,
        examiner_name: str = "",
    ) -> MentalExam:
        """Perform mental/psychological examination."""
        exam = MentalExam(
            exam_id=ProcessingSystem.generate_id("MNT"),
            subject_dbref=record.subject_dbref,
            subject_name=record.subject_name,
            examiner_name=examiner_name,
            exam_date=datetime.now(),
        )
        
        # Randomize for demo
        exam.intelligence = random.randint(40, 90)
        exam.memory = random.randint(40, 80)
        exam.learning_speed = random.randint(40, 80)
        exam.willpower = random.randint(30, 80)
        exam.submission_tendency = random.randint(30, 80)
        exam.obedience = random.randint(20, 70)
        exam.defiance = random.randint(20, 60)
        exam.emotional_stability = random.randint(40, 80)
        exam.pain_tolerance = random.randint(30, 70)
        
        exam.estimated_break_difficulty = (exam.willpower + exam.defiance) // 2
        
        record.mental_exam = exam
        record.add_note("Mental examination completed")
        
        return exam
    
    @staticmethod
    def perform_aptitude_testing(
        record: ProcessingRecord,
        tester_name: str = "",
    ) -> AptitudeTest:
        """Perform aptitude testing."""
        test = AptitudeTest(
            test_id=ProcessingSystem.generate_id("APT"),
            subject_dbref=record.subject_dbref,
            subject_name=record.subject_name,
            tester_name=tester_name,
            test_date=datetime.now(),
        )
        
        # Calculate aptitudes from exam results
        phys = record.physical_exam
        sex = record.sexual_exam
        ment = record.mental_exam
        
        if phys and sex and ment:
            test.aptitudes = {
                "sexual": sex.get_sexual_value_score(),
                "domestic": (ment.intelligence + ment.obedience) // 2,
                "labor": (phys.strength + phys.endurance) // 2,
                "breeding": sex.fertility_rating,
                "entertainment": (phys.get_appearance_score() + sex.sensitivity) // 2,
                "combat": (phys.strength + phys.endurance + ment.pain_tolerance) // 3,
                "intelligence": ment.intelligence,
                "obedience": ment.obedience,
            }
        else:
            # Random if no exams
            for cat in AptitudeCategory:
                test.aptitudes[cat.value] = random.randint(30, 80)
        
        test.primary_recommendation = test.recommend_track()
        
        record.aptitude_test = test
        record.testing_date = datetime.now()
        record.add_note("Aptitude testing completed")
        
        return test
    
    @staticmethod
    def perform_classification(
        record: ProcessingRecord,
        classifier_name: str = "",
    ) -> Classification:
        """Perform final classification."""
        classif = Classification(
            classification_id=ProcessingSystem.generate_id("CLS"),
            subject_dbref=record.subject_dbref,
            subject_name=record.subject_name,
            classifier_name=classifier_name,
            classification_date=datetime.now(),
        )
        
        # Set scores from exams
        if record.physical_exam:
            classif.appearance_score = record.physical_exam.get_appearance_score()
            classif.fitness_score = record.physical_exam.get_fitness_score()
        
        if record.sexual_exam:
            classif.sexual_score = record.sexual_exam.get_sexual_value_score()
            
            # Check virginity for designation
            if record.sexual_exam.virginity.get("vaginal"):
                classif.designations.append("virgin")
        
        if record.mental_exam:
            classif.trainability_score = record.mental_exam.get_trainability_score()
            
            if record.mental_exam.defiance > 70:
                classif.warnings.append("High defiance - may require extensive breaking")
        
        # Calculate overall
        classif.overall_score = (
            classif.appearance_score +
            classif.fitness_score +
            classif.sexual_score +
            classif.trainability_score
        ) // 4
        
        # Set track from aptitude test
        if record.aptitude_test:
            track_str = record.aptitude_test.primary_recommendation
            try:
                classif.training_track = TrainingTrack(track_str)
            except ValueError:
                classif.training_track = TrainingTrack.GENERAL
        
        # Determine grade and value
        classif.value_grade = classif.determine_grade()
        classif.estimated_value = classif.calculate_value()
        
        record.classification = classif
        record.classification_date = datetime.now()
        record.add_note(f"Classified as {classif.training_track.value}, grade {classif.value_grade.value}")
        
        return classif
    
    @staticmethod
    def complete_processing(record: ProcessingRecord) -> str:
        """Mark processing as complete."""
        record.current_stage = ProcessingStage.COMPLETE
        record.completion_date = datetime.now()
        record.add_note("Processing complete - ready for training or sale")
        
        return f"{record.subject_name} processing complete."


__all__ = [
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
]
