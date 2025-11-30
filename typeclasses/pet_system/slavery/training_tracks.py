"""
Training Tracks System
======================

Specialized training programs:
- Hucow
- Pleasure Slave
- Pony
- Breeding Stock
- House Slave
- Display/Trophy
- And more...
"""

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any, Tuple
from enum import Enum
from datetime import datetime, timedelta
import random


# =============================================================================
# ENUMS
# =============================================================================

class TrackStage(Enum):
    """Stages within a training track."""
    ORIENTATION = "orientation"
    BASIC = "basic"
    INTERMEDIATE = "intermediate"
    ADVANCED = "advanced"
    SPECIALIZATION = "specialization"
    MASTERY = "mastery"
    COMPLETE = "complete"


class TrackType(Enum):
    """Types of training tracks."""
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


# =============================================================================
# TRAINING MILESTONE
# =============================================================================

@dataclass
class TrainingMilestone:
    """A milestone in training."""
    milestone_id: str
    name: str
    description: str = ""
    
    # Requirements
    required_skills: Dict[str, int] = field(default_factory=dict)
    required_stats: Dict[str, int] = field(default_factory=dict)
    required_demonstrations: List[str] = field(default_factory=list)
    
    # Rewards
    unlocks_skills: List[str] = field(default_factory=list)
    stat_bonuses: Dict[str, int] = field(default_factory=dict)
    
    # Completion
    is_completed: bool = False
    completed_date: Optional[datetime] = None
    evaluator_name: str = ""
    
    def check_requirements(self, skills: Dict[str, int], stats: Dict[str, int]) -> Tuple[bool, List[str]]:
        """
        Check if requirements are met.
        Returns (met, missing_requirements).
        """
        missing = []
        
        for skill, required in self.required_skills.items():
            if skills.get(skill, 0) < required:
                missing.append(f"{skill}: {skills.get(skill, 0)}/{required}")
        
        for stat, required in self.required_stats.items():
            if stats.get(stat, 0) < required:
                missing.append(f"{stat}: {stats.get(stat, 0)}/{required}")
        
        return len(missing) == 0, missing
    
    def to_dict(self) -> dict:
        return {
            "milestone_id": self.milestone_id,
            "name": self.name,
            "description": self.description,
            "required_skills": self.required_skills,
            "required_stats": self.required_stats,
            "required_demonstrations": self.required_demonstrations,
            "unlocks_skills": self.unlocks_skills,
            "stat_bonuses": self.stat_bonuses,
            "is_completed": self.is_completed,
            "completed_date": self.completed_date.isoformat() if self.completed_date else None,
            "evaluator_name": self.evaluator_name,
        }


# =============================================================================
# TRACK DEFINITION
# =============================================================================

@dataclass
class TrackDefinition:
    """Definition of a training track."""
    track_type: TrackType
    name: str
    description: str = ""
    
    # Duration estimates
    minimum_days: int = 30
    average_days: int = 90
    
    # Entry requirements
    required_aptitudes: Dict[str, int] = field(default_factory=dict)
    preferred_traits: List[str] = field(default_factory=list)
    disqualifying_traits: List[str] = field(default_factory=list)
    
    # Training focus
    primary_skills: List[str] = field(default_factory=list)
    secondary_skills: List[str] = field(default_factory=list)
    
    # Equipment/modifications
    required_equipment: List[str] = field(default_factory=list)
    optional_modifications: List[str] = field(default_factory=list)
    required_modifications: List[str] = field(default_factory=list)
    
    # Milestones
    milestones: List[TrainingMilestone] = field(default_factory=list)
    
    # Outcome
    final_designation: str = ""
    value_multiplier: float = 1.0
    
    def to_dict(self) -> dict:
        return {
            "track_type": self.track_type.value,
            "name": self.name,
            "description": self.description,
            "minimum_days": self.minimum_days,
            "average_days": self.average_days,
            "required_aptitudes": self.required_aptitudes,
            "preferred_traits": self.preferred_traits,
            "disqualifying_traits": self.disqualifying_traits,
            "primary_skills": self.primary_skills,
            "secondary_skills": self.secondary_skills,
            "required_equipment": self.required_equipment,
            "optional_modifications": self.optional_modifications,
            "required_modifications": self.required_modifications,
            "milestones": [m.to_dict() for m in self.milestones],
            "final_designation": self.final_designation,
            "value_multiplier": self.value_multiplier,
        }


# =============================================================================
# PREDEFINED TRACKS
# =============================================================================

TRACK_HUCOW = TrackDefinition(
    track_type=TrackType.HUCOW,
    name="Hucow Training",
    description="Transform into a productive, docile milk-producing hucow.",
    minimum_days=60,
    average_days=120,
    required_aptitudes={"breeding": 40, "obedience": 50},
    preferred_traits=["large breasts", "high fertility", "submissive"],
    disqualifying_traits=["aggressive", "low fertility"],
    primary_skills=["lactation", "milking_compliance", "breeding_readiness"],
    secondary_skills=["docility", "grazing", "herd_behavior"],
    required_equipment=["cowbell", "nose_ring", "milking_harness", "hoof_boots"],
    optional_modifications=["breast_enhancement", "lactation_induction"],
    required_modifications=["ear_tag", "brand"],
    milestones=[
        TrainingMilestone(
            milestone_id="hucow_1",
            name="Lactation Initiation",
            description="Begin producing milk",
            required_stats={"lactation_potential": 30},
            unlocks_skills=["basic_milking"],
        ),
        TrainingMilestone(
            milestone_id="hucow_2",
            name="Milking Compliance",
            description="Accept milking without resistance",
            required_stats={"obedience": 60},
            required_skills={"basic_milking": 50},
            unlocks_skills=["scheduled_milking"],
        ),
        TrainingMilestone(
            milestone_id="hucow_3",
            name="Full Production",
            description="Reach full milk production capacity",
            required_stats={"lactation_potential": 70},
            required_skills={"scheduled_milking": 70},
            stat_bonuses={"milk_quality": 20},
        ),
        TrainingMilestone(
            milestone_id="hucow_4",
            name="Breeding Ready",
            description="Prepared for breeding program",
            required_stats={"fertility_rating": 60, "obedience": 80},
            unlocks_skills=["breeding_presentation"],
        ),
        TrainingMilestone(
            milestone_id="hucow_5",
            name="Herd Integration",
            description="Can function in a herd environment",
            required_skills={"herd_behavior": 60},
            stat_bonuses={"docility": 20},
        ),
    ],
    final_designation="Certified Hucow",
    value_multiplier=1.5,
)

TRACK_PLEASURE = TrackDefinition(
    track_type=TrackType.PLEASURE,
    name="Pleasure Slave Training",
    description="Comprehensive sexual service training.",
    minimum_days=45,
    average_days=90,
    required_aptitudes={"sexual": 50, "obedience": 40},
    preferred_traits=["attractive", "responsive", "eager"],
    disqualifying_traits=["frigid", "aggressive"],
    primary_skills=["oral_service", "vaginal_service", "anal_service", "massage"],
    secondary_skills=["seduction", "erotic_dance", "pain_reception"],
    required_equipment=["collar", "pleasure_outfit"],
    optional_modifications=["sensitivity_enhancement"],
    milestones=[
        TrainingMilestone(
            milestone_id="pleasure_1",
            name="Basic Service",
            description="Master basic sexual techniques",
            required_stats={"obedience": 50},
            unlocks_skills=["oral_basics", "presentation"],
        ),
        TrainingMilestone(
            milestone_id="pleasure_2",
            name="Advanced Oral",
            description="Expert oral skills",
            required_skills={"oral_basics": 70},
            unlocks_skills=["deep_throat", "oral_worship"],
        ),
        TrainingMilestone(
            milestone_id="pleasure_3",
            name="Full Service",
            description="Complete vaginal/anal training",
            required_stats={"stamina": 60},
            unlocks_skills=["multi_partner", "endurance_service"],
        ),
        TrainingMilestone(
            milestone_id="pleasure_4",
            name="Specialty Training",
            description="Master specialty techniques",
            required_skills={"oral_worship": 80},
            unlocks_skills=["exotic_techniques"],
        ),
        TrainingMilestone(
            milestone_id="pleasure_5",
            name="Mastery",
            description="Complete pleasure slave certification",
            required_stats={"obedience": 90},
            stat_bonuses={"sexual_value": 30},
        ),
    ],
    final_designation="Certified Pleasure Slave",
    value_multiplier=1.8,
)

TRACK_PONY = TrackDefinition(
    track_type=TrackType.PONY,
    name="Pony Training",
    description="Transform into a graceful, obedient ponygirl/boy.",
    minimum_days=90,
    average_days=180,
    required_aptitudes={"labor": 50, "obedience": 60},
    preferred_traits=["athletic", "graceful", "high_endurance"],
    disqualifying_traits=["lazy", "clumsy"],
    primary_skills=["gait_work", "harness_acceptance", "cart_pulling", "commands"],
    secondary_skills=["prancing", "showing", "racing"],
    required_equipment=["bridle", "bit", "harness", "hoof_boots", "tail_plug"],
    required_modifications=["mane_styling"],
    optional_modifications=["hoof_modifications"],
    milestones=[
        TrainingMilestone(
            milestone_id="pony_1",
            name="Tack Acceptance",
            description="Accept all pony tack without resistance",
            required_stats={"obedience": 60},
            unlocks_skills=["basic_gait"],
        ),
        TrainingMilestone(
            milestone_id="pony_2",
            name="Basic Gaits",
            description="Master walk, trot, canter",
            required_skills={"basic_gait": 60},
            unlocks_skills=["advanced_gait"],
        ),
        TrainingMilestone(
            milestone_id="pony_3",
            name="Harness Trained",
            description="Can pull cart reliably",
            required_stats={"endurance": 70},
            required_skills={"advanced_gait": 70},
            unlocks_skills=["cart_pulling"],
        ),
        TrainingMilestone(
            milestone_id="pony_4",
            name="Show Ready",
            description="Prepared for show competition",
            required_skills={"prancing": 60, "showing": 60},
            stat_bonuses={"appearance": 10},
        ),
        TrainingMilestone(
            milestone_id="pony_5",
            name="Racing Qualified",
            description="Can compete in races",
            required_stats={"endurance": 80, "speed": 70},
            unlocks_skills=["racing"],
        ),
    ],
    final_designation="Trained Pony",
    value_multiplier=2.0,
)

TRACK_BREEDING = TrackDefinition(
    track_type=TrackType.BREEDING,
    name="Breeding Stock Training",
    description="Optimized for breeding and pregnancy.",
    minimum_days=30,
    average_days=60,
    required_aptitudes={"breeding": 60, "sexual": 40},
    preferred_traits=["high_fertility", "wide_hips", "healthy"],
    disqualifying_traits=["infertile", "health_issues"],
    primary_skills=["breeding_presentation", "pregnancy_care", "birthing"],
    secondary_skills=["heat_management", "nursing"],
    required_equipment=["breeding_harness", "fertility_monitor"],
    optional_modifications=["fertility_enhancement"],
    milestones=[
        TrainingMilestone(
            milestone_id="breed_1",
            name="Fertility Optimized",
            description="Fertility at peak levels",
            required_stats={"fertility_rating": 70},
            unlocks_skills=["heat_cycles"],
        ),
        TrainingMilestone(
            milestone_id="breed_2",
            name="Breeding Ready",
            description="Accepts mounting without resistance",
            required_stats={"obedience": 70},
            unlocks_skills=["breeding_presentation"],
        ),
        TrainingMilestone(
            milestone_id="breed_3",
            name="First Breeding",
            description="Successfully bred",
            required_demonstrations=["successful_breeding"],
        ),
        TrainingMilestone(
            milestone_id="breed_4",
            name="Successful Birth",
            description="First successful delivery",
            required_demonstrations=["successful_birth"],
            stat_bonuses={"breeding_value": 30},
        ),
    ],
    final_designation="Breeding Stock",
    value_multiplier=1.6,
)

TRACK_HOUSE = TrackDefinition(
    track_type=TrackType.HOUSE,
    name="House Slave Training",
    description="Domestic service training.",
    minimum_days=30,
    average_days=60,
    required_aptitudes={"domestic": 50, "obedience": 50, "intelligence": 40},
    preferred_traits=["diligent", "clean", "organized"],
    disqualifying_traits=["lazy", "clumsy", "rebellious"],
    primary_skills=["cleaning", "cooking", "serving", "attendance"],
    secondary_skills=["laundry", "organizing", "hosting"],
    required_equipment=["maid_uniform", "collar"],
    milestones=[
        TrainingMilestone(
            milestone_id="house_1",
            name="Basic Cleaning",
            description="Can clean to standard",
            required_skills={"cleaning": 50},
        ),
        TrainingMilestone(
            milestone_id="house_2",
            name="Service Protocol",
            description="Proper serving etiquette",
            required_stats={"obedience": 70},
            required_skills={"serving": 60},
        ),
        TrainingMilestone(
            milestone_id="house_3",
            name="Full Domestic",
            description="Complete domestic capability",
            required_skills={"cleaning": 70, "cooking": 60, "serving": 70},
        ),
        TrainingMilestone(
            milestone_id="house_4",
            name="Head Servant Ready",
            description="Can supervise other servants",
            required_stats={"intelligence": 60},
            stat_bonuses={"domestic_value": 20},
        ),
    ],
    final_designation="Trained House Slave",
    value_multiplier=1.3,
)

TRACK_DISPLAY = TrackDefinition(
    track_type=TrackType.DISPLAY,
    name="Display/Trophy Training",
    description="Living decoration and arm candy.",
    minimum_days=30,
    average_days=45,
    required_aptitudes={"entertainment": 60},
    preferred_traits=["beautiful", "graceful", "elegant"],
    disqualifying_traits=["plain", "clumsy"],
    primary_skills=["posing", "graceful_movement", "silent_attendance"],
    secondary_skills=["modeling", "decoration"],
    required_equipment=["display_outfit", "jewelry", "collar"],
    milestones=[
        TrainingMilestone(
            milestone_id="display_1",
            name="Static Posing",
            description="Can hold poses for extended periods",
            required_stats={"endurance": 50},
            unlocks_skills=["basic_posing"],
        ),
        TrainingMilestone(
            milestone_id="display_2",
            name="Grace Training",
            description="Movement is elegant and pleasing",
            required_skills={"graceful_movement": 60},
        ),
        TrainingMilestone(
            milestone_id="display_3",
            name="Display Ready",
            description="Ready for public display",
            required_stats={"appearance": 70, "obedience": 80},
            stat_bonuses={"display_value": 30},
        ),
    ],
    final_designation="Display Piece",
    value_multiplier=1.4,
)

TRACK_PET = TrackDefinition(
    track_type=TrackType.PET,
    name="Pet Training",
    description="Trained companion pet.",
    minimum_days=45,
    average_days=90,
    required_aptitudes={"obedience": 60, "domestic": 40},
    preferred_traits=["affectionate", "loyal", "playful"],
    disqualifying_traits=["aggressive", "independent"],
    primary_skills=["pet_behaviors", "commands", "affection_display"],
    secondary_skills=["tricks", "fetch", "heel"],
    required_equipment=["collar", "leash", "pet_bed"],
    optional_modifications=["tail_plug", "ears"],
    milestones=[
        TrainingMilestone(
            milestone_id="pet_1",
            name="Basic Commands",
            description="Responds to sit, stay, come",
            required_stats={"obedience": 60},
            unlocks_skills=["basic_commands"],
        ),
        TrainingMilestone(
            milestone_id="pet_2",
            name="Pet Behavior",
            description="Natural pet behaviors adopted",
            required_skills={"pet_behaviors": 60},
        ),
        TrainingMilestone(
            milestone_id="pet_3",
            name="Leash Trained",
            description="Walks properly on leash",
            required_skills={"heel": 70},
        ),
        TrainingMilestone(
            milestone_id="pet_4",
            name="Fully Trained Pet",
            description="Complete pet training",
            required_stats={"obedience": 90},
            stat_bonuses={"loyalty": 30},
        ),
    ],
    final_designation="Trained Pet",
    value_multiplier=1.5,
)

TRACK_TOY = TrackDefinition(
    track_type=TrackType.TOY,
    name="Toy Training",
    description="Object for use - minimal agency.",
    minimum_days=60,
    average_days=120,
    required_aptitudes={"sexual": 50, "obedience": 70},
    preferred_traits=["passive", "responsive"],
    disqualifying_traits=["dominant", "willful"],
    primary_skills=["objectification", "passive_acceptance", "use_positions"],
    secondary_skills=["storage_positions", "silence"],
    required_equipment=["storage_container", "restraints"],
    milestones=[
        TrainingMilestone(
            milestone_id="toy_1",
            name="Passive Acceptance",
            description="Accepts use without reaction",
            required_stats={"obedience": 80},
        ),
        TrainingMilestone(
            milestone_id="toy_2",
            name="Objectification",
            description="Identity as object internalized",
            required_stats={"submission": 80},
            unlocks_skills=["object_mindset"],
        ),
        TrainingMilestone(
            milestone_id="toy_3",
            name="Full Toy Status",
            description="Complete toy training",
            required_stats={"obedience": 95, "submission": 90},
            stat_bonuses={"use_value": 30},
        ),
    ],
    final_designation="Trained Toy",
    value_multiplier=1.2,
)

TRACK_CONCUBINE = TrackDefinition(
    track_type=TrackType.CONCUBINE,
    name="Concubine Training",
    description="High-class companion and sexual partner.",
    minimum_days=90,
    average_days=180,
    required_aptitudes={"sexual": 60, "intelligence": 50, "entertainment": 50},
    preferred_traits=["beautiful", "intelligent", "charming", "cultured"],
    disqualifying_traits=["crude", "unintelligent"],
    primary_skills=["conversation", "seduction", "pleasure_arts", "etiquette"],
    secondary_skills=["music", "dance", "massage", "companionship"],
    required_equipment=["fine_clothing", "jewelry", "collar"],
    milestones=[
        TrainingMilestone(
            milestone_id="concubine_1",
            name="Social Graces",
            description="Proper etiquette and conversation",
            required_stats={"intelligence": 60},
            required_skills={"etiquette": 60, "conversation": 60},
        ),
        TrainingMilestone(
            milestone_id="concubine_2",
            name="Pleasure Arts",
            description="Expert in pleasure techniques",
            required_skills={"pleasure_arts": 70},
        ),
        TrainingMilestone(
            milestone_id="concubine_3",
            name="Cultural Education",
            description="Knowledge of arts and culture",
            required_skills={"music": 50, "dance": 50},
        ),
        TrainingMilestone(
            milestone_id="concubine_4",
            name="Full Concubine",
            description="Complete concubine training",
            required_stats={"obedience": 80},
            stat_bonuses={"companion_value": 40},
        ),
    ],
    final_designation="Trained Concubine",
    value_multiplier=2.5,
)

# Registry of all tracks
ALL_TRACKS: Dict[str, TrackDefinition] = {
    TrackType.HUCOW.value: TRACK_HUCOW,
    TrackType.PLEASURE.value: TRACK_PLEASURE,
    TrackType.PONY.value: TRACK_PONY,
    TrackType.BREEDING.value: TRACK_BREEDING,
    TrackType.HOUSE.value: TRACK_HOUSE,
    TrackType.DISPLAY.value: TRACK_DISPLAY,
    TrackType.PET.value: TRACK_PET,
    TrackType.TOY.value: TRACK_TOY,
    TrackType.CONCUBINE.value: TRACK_CONCUBINE,
}


def get_track(track_type: str) -> Optional[TrackDefinition]:
    """Get a track definition."""
    return ALL_TRACKS.get(track_type)


# =============================================================================
# TRACK PROGRESS
# =============================================================================

@dataclass
class TrackProgress:
    """Progress through a training track."""
    progress_id: str
    
    # Subject
    subject_dbref: str = ""
    subject_name: str = ""
    
    # Track
    track_type: TrackType = TrackType.GENERAL
    current_stage: TrackStage = TrackStage.ORIENTATION
    
    # Progress
    days_in_training: int = 0
    overall_progress: int = 0     # 0-100
    
    # Skills gained
    skills: Dict[str, int] = field(default_factory=dict)
    
    # Milestones
    completed_milestones: List[str] = field(default_factory=list)
    current_milestone: str = ""
    
    # Assigned trainer
    trainer_dbref: str = ""
    trainer_name: str = ""
    
    # Timing
    started_date: Optional[datetime] = None
    last_training_date: Optional[datetime] = None
    
    # Evaluations
    evaluations: List[Dict[str, Any]] = field(default_factory=list)
    
    def add_skill_progress(self, skill: str, amount: int) -> int:
        """Add progress to a skill."""
        current = self.skills.get(skill, 0)
        new_value = min(100, current + amount)
        self.skills[skill] = new_value
        return new_value
    
    def complete_milestone(self, milestone_id: str, evaluator: str = "") -> str:
        """Mark a milestone as complete."""
        if milestone_id not in self.completed_milestones:
            self.completed_milestones.append(milestone_id)
            return f"Milestone completed: {milestone_id}"
        return "Milestone already completed."
    
    def advance_stage(self) -> Tuple[bool, str]:
        """Advance to next training stage."""
        stages = list(TrackStage)
        current_idx = stages.index(self.current_stage)
        
        if current_idx < len(stages) - 1:
            self.current_stage = stages[current_idx + 1]
            return True, f"Advanced to {self.current_stage.value} stage."
        
        return False, "Already at final stage."
    
    def add_evaluation(self, evaluator: str, score: int, notes: str) -> None:
        """Add a training evaluation."""
        self.evaluations.append({
            "date": datetime.now().isoformat(),
            "evaluator": evaluator,
            "score": score,
            "notes": notes,
        })
    
    def calculate_overall_progress(self, track: TrackDefinition) -> int:
        """Calculate overall progress percentage."""
        if not track.milestones:
            return 0
        
        completed = len(self.completed_milestones)
        total = len(track.milestones)
        
        return int((completed / total) * 100)
    
    def get_progress_display(self) -> str:
        """Get progress display."""
        track = get_track(self.track_type.value)
        track_name = track.name if track else self.track_type.value
        
        lines = [f"=== Training Progress: {self.subject_name} ==="]
        lines.append(f"Track: {track_name}")
        lines.append(f"Stage: {self.current_stage.value}")
        lines.append(f"Days in training: {self.days_in_training}")
        lines.append(f"Overall progress: {self.overall_progress}%")
        
        if self.skills:
            lines.append("\nSkills:")
            for skill, level in sorted(self.skills.items()):
                bar = "█" * (level // 10) + "░" * (10 - level // 10)
                lines.append(f"  {skill}: [{bar}] {level}%")
        
        if self.completed_milestones:
            lines.append(f"\nMilestones: {len(self.completed_milestones)} completed")
        
        return "\n".join(lines)
    
    def to_dict(self) -> dict:
        return {
            "progress_id": self.progress_id,
            "subject_dbref": self.subject_dbref,
            "subject_name": self.subject_name,
            "track_type": self.track_type.value,
            "current_stage": self.current_stage.value,
            "days_in_training": self.days_in_training,
            "overall_progress": self.overall_progress,
            "skills": self.skills,
            "completed_milestones": self.completed_milestones,
            "current_milestone": self.current_milestone,
            "trainer_dbref": self.trainer_dbref,
            "trainer_name": self.trainer_name,
            "started_date": self.started_date.isoformat() if self.started_date else None,
            "last_training_date": self.last_training_date.isoformat() if self.last_training_date else None,
            "evaluations": self.evaluations,
        }
    
    @classmethod
    def from_dict(cls, data: dict) -> "TrackProgress":
        prog = cls(progress_id=data["progress_id"])
        prog.subject_dbref = data.get("subject_dbref", "")
        prog.subject_name = data.get("subject_name", "")
        prog.track_type = TrackType(data.get("track_type", "general"))
        prog.current_stage = TrackStage(data.get("current_stage", "orientation"))
        prog.days_in_training = data.get("days_in_training", 0)
        prog.overall_progress = data.get("overall_progress", 0)
        prog.skills = data.get("skills", {})
        prog.completed_milestones = data.get("completed_milestones", [])
        prog.current_milestone = data.get("current_milestone", "")
        prog.trainer_dbref = data.get("trainer_dbref", "")
        prog.trainer_name = data.get("trainer_name", "")
        prog.evaluations = data.get("evaluations", [])
        
        if data.get("started_date"):
            prog.started_date = datetime.fromisoformat(data["started_date"])
        if data.get("last_training_date"):
            prog.last_training_date = datetime.fromisoformat(data["last_training_date"])
        
        return prog


# =============================================================================
# TRACK SYSTEM
# =============================================================================

class TrackSystem:
    """
    Manages training track progression.
    """
    
    @staticmethod
    def generate_id() -> str:
        """Generate unique ID."""
        timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
        rand = random.randint(1000, 9999)
        return f"TRK-{timestamp}-{rand}"
    
    @staticmethod
    def start_track(
        subject,
        track_type: TrackType,
        trainer = None,
    ) -> TrackProgress:
        """Start a training track."""
        progress = TrackProgress(
            progress_id=TrackSystem.generate_id(),
            subject_dbref=subject.dbref,
            subject_name=subject.key,
            track_type=track_type,
            current_stage=TrackStage.ORIENTATION,
            started_date=datetime.now(),
        )
        
        if trainer:
            progress.trainer_dbref = trainer.dbref
            progress.trainer_name = trainer.key
        
        # Set first milestone
        track = get_track(track_type.value)
        if track and track.milestones:
            progress.current_milestone = track.milestones[0].milestone_id
        
        return progress
    
    @staticmethod
    def do_training(
        progress: TrackProgress,
        hours: int = 1,
    ) -> Tuple[str, Dict[str, int]]:
        """
        Perform training session.
        Returns (message, skill_gains).
        """
        track = get_track(progress.track_type.value)
        if not track:
            return "Unknown track.", {}
        
        skill_gains = {}
        messages = []
        
        # Train primary skills
        for skill in track.primary_skills:
            gain = random.randint(1, 5) * hours
            new_val = progress.add_skill_progress(skill, gain)
            skill_gains[skill] = gain
        
        # Chance for secondary skills
        for skill in track.secondary_skills:
            if random.random() < 0.3:
                gain = random.randint(1, 3) * hours
                new_val = progress.add_skill_progress(skill, gain)
                skill_gains[skill] = gain
        
        # Update tracking
        progress.last_training_date = datetime.now()
        
        # Check milestone progress
        if progress.current_milestone:
            for milestone in track.milestones:
                if milestone.milestone_id == progress.current_milestone:
                    met, missing = milestone.check_requirements(progress.skills, {})
                    if met:
                        progress.complete_milestone(milestone.milestone_id)
                        messages.append(f"Milestone completed: {milestone.name}")
                        
                        # Find next milestone
                        idx = track.milestones.index(milestone)
                        if idx < len(track.milestones) - 1:
                            progress.current_milestone = track.milestones[idx + 1].milestone_id
                        else:
                            progress.current_milestone = ""
        
        # Update overall progress
        progress.overall_progress = progress.calculate_overall_progress(track)
        
        main_msg = f"Training session completed ({hours} hours)."
        if messages:
            main_msg += " " + " ".join(messages)
        
        return main_msg, skill_gains


__all__ = [
    "TrackStage",
    "TrackType",
    "TrainingMilestone",
    "TrackDefinition",
    "ALL_TRACKS",
    "get_track",
    "TrackProgress",
    "TrackSystem",
]
