"""
Daily Routine System
====================

Scheduling and routine management including:
- Daily schedules
- Production quotas
- Task assignments
- Punishment for failures
- Reward tracking
"""

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any, Tuple, Callable
from enum import Enum
from datetime import datetime, time, timedelta
import random


# =============================================================================
# ENUMS
# =============================================================================

class TaskType(Enum):
    """Types of daily tasks."""
    MILKING = "milking"
    BREEDING = "breeding"
    FEEDING = "feeding"
    GROOMING = "grooming"
    EXERCISE = "exercise"
    TRAINING = "training"
    SERVICE = "service"
    CLEANING = "cleaning"
    DISPLAY = "display"
    REST = "rest"
    PUNISHMENT = "punishment"
    INSPECTION = "inspection"
    MEDICAL = "medical"


class QuotaType(Enum):
    """Types of quotas."""
    MILK_PRODUCTION = "milk_production"
    BREEDING_SESSIONS = "breeding_sessions"
    TRAINING_HOURS = "training_hours"
    SERVICE_ACTS = "service_acts"
    ORGASMS_GIVEN = "orgasms_given"
    LOADS_RECEIVED = "loads_received"
    OBEDIENCE_SCORE = "obedience_score"


class PunishmentType(Enum):
    """Types of punishments for failures."""
    SPANKING = "spanking"
    CANING = "caning"
    WHIPPING = "whipping"
    DENIAL = "denial"             # Orgasm denial
    ISOLATION = "isolation"
    BONDAGE = "bondage"
    PUBLIC_PUNISHMENT = "public_punishment"
    REDUCED_RATIONS = "reduced_rations"
    EXTRA_MILKING = "extra_milking"
    BREEDING_PUNISHMENT = "breeding_punishment"
    HUMILIATION = "humiliation"


class RewardType(Enum):
    """Types of rewards for success."""
    TREAT = "treat"
    REST = "rest"
    ORGASM = "orgasm"
    COMFORT = "comfort"
    PRAISE = "praise"
    PRIVILEGE = "privilege"
    GENTLE_HANDLING = "gentle_handling"


# =============================================================================
# SCHEDULED TASK
# =============================================================================

@dataclass
class ScheduledTask:
    """A single scheduled task."""
    
    task_id: str = ""
    task_type: TaskType = TaskType.REST
    name: str = ""
    description: str = ""
    
    # Timing
    scheduled_time: time = field(default_factory=lambda: time(8, 0))
    duration_minutes: int = 30
    
    # Location
    location: str = ""
    
    # Requirements
    requires_handler: bool = False
    handler_assigned: str = ""
    
    # Completion
    is_completed: bool = False
    completed_at: Optional[datetime] = None
    completion_notes: str = ""
    
    # Results
    performance_rating: int = 0   # 0-100
    
    def complete(self, rating: int = 70, notes: str = "") -> str:
        """Mark task as complete."""
        self.is_completed = True
        self.completed_at = datetime.now()
        self.performance_rating = rating
        self.completion_notes = notes
        
        if rating >= 90:
            return f"{self.name} completed excellently!"
        elif rating >= 70:
            return f"{self.name} completed satisfactorily."
        elif rating >= 50:
            return f"{self.name} completed poorly."
        else:
            return f"{self.name} failed."


# =============================================================================
# DAILY QUOTA
# =============================================================================

@dataclass
class DailyQuota:
    """A daily quota to meet."""
    
    quota_id: str = ""
    quota_type: QuotaType = QuotaType.MILK_PRODUCTION
    name: str = ""
    
    # Target
    target_amount: int = 0
    current_amount: int = 0
    
    # Unit
    unit: str = ""                # "ml", "sessions", "hours", etc.
    
    # Results
    is_met: bool = False
    exceeded_by: int = 0
    failed_by: int = 0
    
    @property
    def progress_percent(self) -> float:
        """Get progress percentage."""
        if self.target_amount == 0:
            return 100.0
        return (self.current_amount / self.target_amount) * 100
    
    def add_progress(self, amount: int) -> str:
        """Add progress toward quota."""
        self.current_amount += amount
        
        if self.current_amount >= self.target_amount:
            self.is_met = True
            self.exceeded_by = self.current_amount - self.target_amount
            return f"Quota met! ({self.current_amount}/{self.target_amount} {self.unit})"
        
        return f"Progress: {self.current_amount}/{self.target_amount} {self.unit} ({self.progress_percent:.0f}%)"
    
    def finalize(self) -> Tuple[bool, int]:
        """
        Finalize quota at end of day.
        Returns (was_met, difference).
        """
        if self.current_amount >= self.target_amount:
            self.is_met = True
            self.exceeded_by = self.current_amount - self.target_amount
            return True, self.exceeded_by
        else:
            self.is_met = False
            self.failed_by = self.target_amount - self.current_amount
            return False, -self.failed_by


# =============================================================================
# DAILY SCHEDULE
# =============================================================================

@dataclass
class DailySchedule:
    """Complete daily schedule for a subject."""
    
    schedule_id: str = ""
    subject_dbref: str = ""
    subject_name: str = ""
    
    # Date
    date: Optional[datetime] = None
    
    # Tasks
    tasks: List[ScheduledTask] = field(default_factory=list)
    
    # Quotas
    quotas: Dict[str, DailyQuota] = field(default_factory=dict)
    
    # Results
    tasks_completed: int = 0
    tasks_failed: int = 0
    quotas_met: int = 0
    quotas_failed: int = 0
    
    # Punishments earned
    punishments_earned: List[PunishmentType] = field(default_factory=list)
    punishments_administered: List[str] = field(default_factory=list)
    
    # Rewards earned
    rewards_earned: List[RewardType] = field(default_factory=list)
    rewards_given: List[str] = field(default_factory=list)
    
    # Overall
    overall_performance: int = 0  # 0-100
    
    def add_task(self, task: ScheduledTask) -> str:
        """Add a task to the schedule."""
        self.tasks.append(task)
        return f"Added: {task.name} at {task.scheduled_time}"
    
    def add_quota(self, quota: DailyQuota) -> str:
        """Add a quota."""
        self.quotas[quota.quota_type.value] = quota
        return f"Quota set: {quota.target_amount} {quota.unit} {quota.name}"
    
    def complete_task(self, task_id: str, rating: int = 70) -> str:
        """Complete a task."""
        for task in self.tasks:
            if task.task_id == task_id:
                msg = task.complete(rating)
                
                if rating >= 50:
                    self.tasks_completed += 1
                else:
                    self.tasks_failed += 1
                    self.punishments_earned.append(PunishmentType.SPANKING)
                
                return msg
        
        return "Task not found."
    
    def update_quota(self, quota_type: QuotaType, amount: int) -> str:
        """Update progress on a quota."""
        key = quota_type.value
        if key in self.quotas:
            return self.quotas[key].add_progress(amount)
        return "Quota not found."
    
    def finalize_day(self) -> str:
        """Finalize the day's performance."""
        lines = []
        
        # Check all quotas
        for quota in self.quotas.values():
            met, diff = quota.finalize()
            if met:
                self.quotas_met += 1
                if diff > 0:
                    self.rewards_earned.append(RewardType.PRAISE)
                    lines.append(f"✓ {quota.name}: Exceeded by {diff} {quota.unit}")
            else:
                self.quotas_failed += 1
                self.punishments_earned.append(PunishmentType.DENIAL)
                lines.append(f"✗ {quota.name}: Failed by {-diff} {quota.unit}")
        
        # Calculate overall performance
        total_tasks = len(self.tasks)
        total_quotas = len(self.quotas)
        
        if total_tasks + total_quotas > 0:
            score = 0
            if total_tasks > 0:
                score += (self.tasks_completed / total_tasks) * 50
            if total_quotas > 0:
                score += (self.quotas_met / total_quotas) * 50
            self.overall_performance = int(score)
        
        lines.append(f"\nOverall Performance: {self.overall_performance}/100")
        lines.append(f"Tasks: {self.tasks_completed} completed, {self.tasks_failed} failed")
        lines.append(f"Quotas: {self.quotas_met} met, {self.quotas_failed} failed")
        
        if self.punishments_earned:
            lines.append(f"Punishments earned: {len(self.punishments_earned)}")
        if self.rewards_earned:
            lines.append(f"Rewards earned: {len(self.rewards_earned)}")
        
        return "\n".join(lines)
    
    def get_current_task(self) -> Optional[ScheduledTask]:
        """Get the current scheduled task based on time."""
        now = datetime.now().time()
        
        for task in sorted(self.tasks, key=lambda t: t.scheduled_time):
            if not task.is_completed:
                # Check if it's time for this task
                task_end = datetime.combine(
                    datetime.today(),
                    task.scheduled_time
                ) + timedelta(minutes=task.duration_minutes)
                
                if task.scheduled_time <= now <= task_end.time():
                    return task
        
        return None
    
    def get_schedule_display(self) -> str:
        """Get formatted schedule display."""
        lines = [f"=== Daily Schedule: {self.subject_name} ==="]
        lines.append(f"Date: {self.date.strftime('%Y-%m-%d') if self.date else 'Today'}")
        
        lines.append("\n--- Tasks ---")
        for task in sorted(self.tasks, key=lambda t: t.scheduled_time):
            status = "✓" if task.is_completed else "○"
            lines.append(f"  {status} {task.scheduled_time.strftime('%H:%M')} - {task.name} ({task.duration_minutes}min)")
        
        lines.append("\n--- Quotas ---")
        for quota in self.quotas.values():
            status = "✓" if quota.is_met else f"{quota.progress_percent:.0f}%"
            lines.append(f"  [{status}] {quota.name}: {quota.current_amount}/{quota.target_amount} {quota.unit}")
        
        return "\n".join(lines)


# =============================================================================
# PUNISHMENT RECORD
# =============================================================================

@dataclass
class PunishmentRecord:
    """Record of a punishment."""
    
    punishment_id: str = ""
    subject_dbref: str = ""
    subject_name: str = ""
    
    # Type
    punishment_type: PunishmentType = PunishmentType.SPANKING
    
    # Reason
    reason: str = ""
    task_failed: str = ""
    quota_failed: str = ""
    
    # Details
    intensity: int = 50           # 0-100
    duration_minutes: int = 10
    
    # Administered
    administered_by: str = ""
    administered_at: Optional[datetime] = None
    
    # Effects
    pain_inflicted: int = 0       # 0-100
    humiliation_inflicted: int = 0
    obedience_gained: int = 0
    
    def administer(self, administrator: str) -> str:
        """Administer the punishment."""
        self.administered_by = administrator
        self.administered_at = datetime.now()
        
        # Calculate effects based on type and intensity
        pain_map = {
            PunishmentType.SPANKING: 30,
            PunishmentType.CANING: 60,
            PunishmentType.WHIPPING: 50,
            PunishmentType.DENIAL: 10,
            PunishmentType.ISOLATION: 5,
            PunishmentType.BONDAGE: 20,
            PunishmentType.PUBLIC_PUNISHMENT: 40,
            PunishmentType.REDUCED_RATIONS: 5,
            PunishmentType.EXTRA_MILKING: 25,
            PunishmentType.BREEDING_PUNISHMENT: 15,
            PunishmentType.HUMILIATION: 10,
        }
        
        humiliation_map = {
            PunishmentType.SPANKING: 20,
            PunishmentType.PUBLIC_PUNISHMENT: 70,
            PunishmentType.HUMILIATION: 80,
            PunishmentType.BREEDING_PUNISHMENT: 40,
        }
        
        self.pain_inflicted = int(pain_map.get(self.punishment_type, 20) * (self.intensity / 50))
        self.humiliation_inflicted = int(humiliation_map.get(self.punishment_type, 20) * (self.intensity / 50))
        self.obedience_gained = self.intensity // 5
        
        # Generate message
        msgs = {
            PunishmentType.SPANKING: f"receives {self.intensity // 10 * 5} hard spanks",
            PunishmentType.CANING: f"is caned severely",
            PunishmentType.WHIPPING: f"is whipped until crying",
            PunishmentType.DENIAL: f"is denied any release",
            PunishmentType.ISOLATION: f"is locked in isolation",
            PunishmentType.BONDAGE: f"is bound in uncomfortable bondage",
            PunishmentType.PUBLIC_PUNISHMENT: f"is punished publicly",
            PunishmentType.REDUCED_RATIONS: f"has rations reduced",
            PunishmentType.EXTRA_MILKING: f"is milked extra harshly",
            PunishmentType.BREEDING_PUNISHMENT: f"is bred as punishment",
            PunishmentType.HUMILIATION: f"is humiliated in front of everyone",
        }
        
        return f"{self.subject_name} {msgs.get(self.punishment_type, 'is punished')} by {administrator}."


# =============================================================================
# SCHEDULE TEMPLATES
# =============================================================================

def create_hucow_schedule(subject_name: str, subject_dbref: str) -> DailySchedule:
    """Create a standard hucow daily schedule."""
    
    schedule = DailySchedule(
        schedule_id=f"SCH-{datetime.now().strftime('%Y%m%d')}-{random.randint(100, 999)}",
        subject_dbref=subject_dbref,
        subject_name=subject_name,
        date=datetime.now(),
    )
    
    # Morning milking
    schedule.add_task(ScheduledTask(
        task_id="MILK-AM",
        task_type=TaskType.MILKING,
        name="Morning Milking",
        scheduled_time=time(6, 0),
        duration_minutes=45,
        location="Milking Parlor",
        requires_handler=True,
    ))
    
    # Feeding
    schedule.add_task(ScheduledTask(
        task_id="FEED-AM",
        task_type=TaskType.FEEDING,
        name="Morning Feeding",
        scheduled_time=time(7, 0),
        duration_minutes=30,
        location="Feeding Trough",
    ))
    
    # Grooming
    schedule.add_task(ScheduledTask(
        task_id="GROOM",
        task_type=TaskType.GROOMING,
        name="Grooming & Inspection",
        scheduled_time=time(8, 0),
        duration_minutes=30,
        location="Grooming Station",
        requires_handler=True,
    ))
    
    # Exercise
    schedule.add_task(ScheduledTask(
        task_id="EXERCISE",
        task_type=TaskType.EXERCISE,
        name="Exercise Period",
        scheduled_time=time(9, 0),
        duration_minutes=60,
        location="Exercise Yard",
    ))
    
    # Training
    schedule.add_task(ScheduledTask(
        task_id="TRAIN",
        task_type=TaskType.TRAINING,
        name="Training Session",
        scheduled_time=time(10, 30),
        duration_minutes=90,
        location="Training Room",
        requires_handler=True,
    ))
    
    # Midday milking
    schedule.add_task(ScheduledTask(
        task_id="MILK-NOON",
        task_type=TaskType.MILKING,
        name="Midday Milking",
        scheduled_time=time(12, 0),
        duration_minutes=45,
        location="Milking Parlor",
        requires_handler=True,
    ))
    
    # Afternoon feeding
    schedule.add_task(ScheduledTask(
        task_id="FEED-PM",
        task_type=TaskType.FEEDING,
        name="Afternoon Feeding",
        scheduled_time=time(13, 0),
        duration_minutes=30,
        location="Feeding Trough",
    ))
    
    # Breeding (if scheduled)
    schedule.add_task(ScheduledTask(
        task_id="BREED",
        task_type=TaskType.BREEDING,
        name="Breeding Session",
        scheduled_time=time(14, 0),
        duration_minutes=60,
        location="Breeding Barn",
        requires_handler=True,
    ))
    
    # Rest
    schedule.add_task(ScheduledTask(
        task_id="REST",
        task_type=TaskType.REST,
        name="Rest Period",
        scheduled_time=time(15, 30),
        duration_minutes=90,
        location="Stall",
    ))
    
    # Evening milking
    schedule.add_task(ScheduledTask(
        task_id="MILK-PM",
        task_type=TaskType.MILKING,
        name="Evening Milking",
        scheduled_time=time(18, 0),
        duration_minutes=45,
        location="Milking Parlor",
        requires_handler=True,
    ))
    
    # Evening feeding
    schedule.add_task(ScheduledTask(
        task_id="FEED-EVE",
        task_type=TaskType.FEEDING,
        name="Evening Feeding",
        scheduled_time=time(19, 0),
        duration_minutes=30,
        location="Feeding Trough",
    ))
    
    # Night milking
    schedule.add_task(ScheduledTask(
        task_id="MILK-NIGHT",
        task_type=TaskType.MILKING,
        name="Night Milking",
        scheduled_time=time(22, 0),
        duration_minutes=30,
        location="Stall",
        requires_handler=True,
    ))
    
    # Add quotas
    schedule.add_quota(DailyQuota(
        quota_id="Q-MILK",
        quota_type=QuotaType.MILK_PRODUCTION,
        name="Milk Production",
        target_amount=2000,        # 2 liters
        unit="ml",
    ))
    
    schedule.add_quota(DailyQuota(
        quota_id="Q-OBEY",
        quota_type=QuotaType.OBEDIENCE_SCORE,
        name="Obedience",
        target_amount=70,
        unit="points",
    ))
    
    return schedule


def create_breeding_stock_schedule(subject_name: str, subject_dbref: str) -> DailySchedule:
    """Create a schedule for breeding stock."""
    
    schedule = DailySchedule(
        schedule_id=f"SCH-{datetime.now().strftime('%Y%m%d')}-{random.randint(100, 999)}",
        subject_dbref=subject_dbref,
        subject_name=subject_name,
        date=datetime.now(),
    )
    
    # Morning breeding
    schedule.add_task(ScheduledTask(
        task_id="BREED-AM",
        task_type=TaskType.BREEDING,
        name="Morning Breeding",
        scheduled_time=time(6, 0),
        duration_minutes=60,
        location="Breeding Barn",
        requires_handler=True,
    ))
    
    # Feeding
    schedule.add_task(ScheduledTask(
        task_id="FEED-AM",
        task_type=TaskType.FEEDING,
        name="Morning Feeding",
        scheduled_time=time(7, 30),
        duration_minutes=30,
    ))
    
    # Fertility treatment
    schedule.add_task(ScheduledTask(
        task_id="MEDICAL",
        task_type=TaskType.MEDICAL,
        name="Fertility Treatment",
        scheduled_time=time(9, 0),
        duration_minutes=30,
        location="Medical Bay",
        requires_handler=True,
    ))
    
    # Midday breeding
    schedule.add_task(ScheduledTask(
        task_id="BREED-NOON",
        task_type=TaskType.BREEDING,
        name="Midday Breeding",
        scheduled_time=time(12, 0),
        duration_minutes=60,
        location="Breeding Barn",
        requires_handler=True,
    ))
    
    # Afternoon breeding
    schedule.add_task(ScheduledTask(
        task_id="BREED-PM",
        task_type=TaskType.BREEDING,
        name="Afternoon Breeding",
        scheduled_time=time(15, 0),
        duration_minutes=60,
        location="Breeding Barn",
        requires_handler=True,
    ))
    
    # Evening breeding
    schedule.add_task(ScheduledTask(
        task_id="BREED-EVE",
        task_type=TaskType.BREEDING,
        name="Evening Breeding",
        scheduled_time=time(18, 0),
        duration_minutes=60,
        location="Breeding Barn",
        requires_handler=True,
    ))
    
    # Night breeding
    schedule.add_task(ScheduledTask(
        task_id="BREED-NIGHT",
        task_type=TaskType.BREEDING,
        name="Night Breeding",
        scheduled_time=time(21, 0),
        duration_minutes=60,
        location="Stall",
        requires_handler=True,
    ))
    
    # Quotas
    schedule.add_quota(DailyQuota(
        quota_id="Q-BREED",
        quota_type=QuotaType.BREEDING_SESSIONS,
        name="Breeding Sessions",
        target_amount=5,
        unit="sessions",
    ))
    
    schedule.add_quota(DailyQuota(
        quota_id="Q-LOADS",
        quota_type=QuotaType.LOADS_RECEIVED,
        name="Loads Received",
        target_amount=5,
        unit="loads",
    ))
    
    return schedule


def create_free_use_schedule(subject_name: str, subject_dbref: str) -> DailySchedule:
    """Create a schedule for free-use property."""
    
    schedule = DailySchedule(
        schedule_id=f"SCH-{datetime.now().strftime('%Y%m%d')}-{random.randint(100, 999)}",
        subject_dbref=subject_dbref,
        subject_name=subject_name,
        date=datetime.now(),
    )
    
    # Morning display
    schedule.add_task(ScheduledTask(
        task_id="DISPLAY-AM",
        task_type=TaskType.DISPLAY,
        name="Morning Public Display",
        scheduled_time=time(8, 0),
        duration_minutes=180,
        location="Public Square",
    ))
    
    # Service period
    schedule.add_task(ScheduledTask(
        task_id="SERVICE-AM",
        task_type=TaskType.SERVICE,
        name="Morning Service Hours",
        scheduled_time=time(11, 0),
        duration_minutes=180,
        location="Service Station",
    ))
    
    # Afternoon display
    schedule.add_task(ScheduledTask(
        task_id="DISPLAY-PM",
        task_type=TaskType.DISPLAY,
        name="Afternoon Public Display",
        scheduled_time=time(14, 0),
        duration_minutes=180,
        location="Public Square",
    ))
    
    # Evening service
    schedule.add_task(ScheduledTask(
        task_id="SERVICE-PM",
        task_type=TaskType.SERVICE,
        name="Evening Service Hours",
        scheduled_time=time(17, 0),
        duration_minutes=240,
        location="Service Station",
    ))
    
    # Quotas
    schedule.add_quota(DailyQuota(
        quota_id="Q-SERVICE",
        quota_type=QuotaType.SERVICE_ACTS,
        name="Service Acts",
        target_amount=20,
        unit="acts",
    ))
    
    schedule.add_quota(DailyQuota(
        quota_id="Q-ORGASMS",
        quota_type=QuotaType.ORGASMS_GIVEN,
        name="Orgasms Given",
        target_amount=15,
        unit="orgasms",
    ))
    
    schedule.add_quota(DailyQuota(
        quota_id="Q-LOADS",
        quota_type=QuotaType.LOADS_RECEIVED,
        name="Loads Received",
        target_amount=10,
        unit="loads",
    ))
    
    return schedule


__all__ = [
    "TaskType",
    "QuotaType",
    "PunishmentType",
    "RewardType",
    "ScheduledTask",
    "DailyQuota",
    "DailySchedule",
    "PunishmentRecord",
    "create_hucow_schedule",
    "create_breeding_stock_schedule",
    "create_free_use_schedule",
]
