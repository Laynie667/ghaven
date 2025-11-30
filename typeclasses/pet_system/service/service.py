"""
Service Roles System
====================

Service and performance roles:
- Service roles (maid, butler, etc.)
- Task assignment and tracking
- Exhibition and performance
"""

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any, Tuple
from enum import Enum
from datetime import datetime, timedelta
import random


# =============================================================================
# ENUMS
# =============================================================================

class ServiceRole(Enum):
    """Types of service roles."""
    MAID = "maid"
    BUTLER = "butler"
    SERVANT = "servant"
    ATTENDANT = "attendant"
    PERFORMER = "performer"
    DISPLAY = "display"          # Living decoration
    FURNITURE = "furniture"      # Human furniture
    TOY = "toy"                  # Sexual service


class TaskType(Enum):
    """Types of tasks."""
    CLEANING = "cleaning"
    SERVING = "serving"
    COOKING = "cooking"
    ATTENDING = "attending"      # Personal attendance
    ERRANDS = "errands"
    PERFORMANCE = "performance"
    DISPLAY = "display"
    SEXUAL = "sexual"


class TaskStatus(Enum):
    """Status of a task."""
    ASSIGNED = "assigned"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"
    ABANDONED = "abandoned"


class PerformanceType(Enum):
    """Types of performances."""
    DANCE = "dance"
    STRIP = "strip"
    POSE = "pose"
    SERVE = "serve"
    DISPLAY = "display"
    ENTERTAIN = "entertain"
    PLEASURE = "pleasure"


# =============================================================================
# SERVICE UNIFORM
# =============================================================================

@dataclass
class ServiceUniform:
    """A service uniform."""
    name: str
    role: ServiceRole
    
    # Appearance
    description: str = ""
    modesty_level: int = 50     # 0 = fully exposed, 100 = fully covered
    
    # Components
    includes_headpiece: bool = False
    includes_collar: bool = False
    includes_apron: bool = False
    includes_stockings: bool = False
    includes_heels: bool = False
    
    # Effects
    movement_penalty: int = 0   # From restrictive clothing/heels
    arousal_modifier: int = 0   # How arousing to wear
    
    def to_dict(self) -> dict:
        return {
            "name": self.name,
            "role": self.role.value,
            "description": self.description,
            "modesty_level": self.modesty_level,
            "includes_headpiece": self.includes_headpiece,
            "includes_collar": self.includes_collar,
            "includes_apron": self.includes_apron,
            "includes_stockings": self.includes_stockings,
            "includes_heels": self.includes_heels,
            "movement_penalty": self.movement_penalty,
            "arousal_modifier": self.arousal_modifier,
        }


# Predefined uniforms
UNIFORM_CLASSIC_MAID = ServiceUniform(
    name="Classic Maid Uniform",
    role=ServiceRole.MAID,
    description="A black dress with white apron and lace trim.",
    modesty_level=70,
    includes_headpiece=True,
    includes_apron=True,
    includes_stockings=True,
    includes_heels=True,
    movement_penalty=5,
)

UNIFORM_FRENCH_MAID = ServiceUniform(
    name="French Maid Uniform",
    role=ServiceRole.MAID,
    description="A short, frilly black and white dress that barely covers.",
    modesty_level=30,
    includes_headpiece=True,
    includes_apron=True,
    includes_stockings=True,
    includes_heels=True,
    movement_penalty=10,
    arousal_modifier=15,
)

UNIFORM_NAKED_MAID = ServiceUniform(
    name="Naked Maid 'Uniform'",
    role=ServiceRole.MAID,
    description="Just an apron, collar, and heels.",
    modesty_level=10,
    includes_collar=True,
    includes_apron=True,
    includes_heels=True,
    movement_penalty=5,
    arousal_modifier=30,
)

UNIFORM_BUTLER = ServiceUniform(
    name="Butler's Livery",
    role=ServiceRole.BUTLER,
    description="Formal black suit with white gloves.",
    modesty_level=100,
    movement_penalty=0,
)

UNIFORM_DISPLAY = ServiceUniform(
    name="Display Harness",
    role=ServiceRole.DISPLAY,
    description="Leather straps that frame rather than cover.",
    modesty_level=5,
    includes_collar=True,
    includes_heels=True,
    movement_penalty=15,
    arousal_modifier=40,
)

UNIFORM_FURNITURE = ServiceUniform(
    name="Furniture Straps",
    role=ServiceRole.FURNITURE,
    description="Minimal straps to secure the body in position.",
    modesty_level=0,
    includes_collar=True,
    movement_penalty=50,  # Very restricted
    arousal_modifier=25,
)


ALL_UNIFORMS: Dict[str, ServiceUniform] = {
    "classic_maid": UNIFORM_CLASSIC_MAID,
    "french_maid": UNIFORM_FRENCH_MAID,
    "naked_maid": UNIFORM_NAKED_MAID,
    "butler": UNIFORM_BUTLER,
    "display": UNIFORM_DISPLAY,
    "furniture": UNIFORM_FURNITURE,
}


# =============================================================================
# TASK
# =============================================================================

@dataclass
class ServiceTask:
    """A task assigned to a servant."""
    task_id: str
    
    # Assignment
    assigner_dbref: str = ""
    assigner_name: str = ""
    assignee_dbref: str = ""
    assignee_name: str = ""
    
    # Task details
    task_type: TaskType = TaskType.SERVING
    description: str = ""
    location_dbref: str = ""
    
    # Difficulty and timing
    difficulty: int = 50        # 0-100
    time_limit_minutes: int = 60
    
    # Status
    status: TaskStatus = TaskStatus.ASSIGNED
    progress: int = 0           # 0-100
    
    # Quality
    quality_score: int = 0      # Set on completion
    
    # Timing
    assigned_at: Optional[datetime] = None
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    
    @property
    def is_overdue(self) -> bool:
        """Check if task is overdue."""
        if not self.assigned_at or self.status in (TaskStatus.COMPLETED, TaskStatus.FAILED):
            return False
        deadline = self.assigned_at + timedelta(minutes=self.time_limit_minutes)
        return datetime.now() > deadline
    
    @property
    def time_remaining(self) -> int:
        """Get remaining time in minutes."""
        if not self.assigned_at:
            return self.time_limit_minutes
        deadline = self.assigned_at + timedelta(minutes=self.time_limit_minutes)
        remaining = (deadline - datetime.now()).total_seconds() / 60
        return max(0, int(remaining))
    
    def start(self) -> str:
        """Start working on task."""
        self.status = TaskStatus.IN_PROGRESS
        self.started_at = datetime.now()
        return f"{self.assignee_name} begins working on: {self.description}"
    
    def advance(self, amount: int = 10) -> Tuple[bool, str]:
        """
        Advance task progress.
        Returns (completed, message).
        """
        self.progress = min(100, self.progress + amount)
        
        if self.progress >= 100:
            return self.complete()
        
        return False, f"Task progress: {self.progress}%"
    
    def complete(self, quality: int = 0) -> Tuple[bool, str]:
        """Complete the task."""
        self.status = TaskStatus.COMPLETED
        self.completed_at = datetime.now()
        self.progress = 100
        
        # Calculate quality if not provided
        if quality == 0:
            # Base quality from difficulty
            quality = random.randint(50, 100)
            
            # Penalty for being late
            if self.is_overdue:
                quality -= 20
            
            # Bonus for being fast
            if self.started_at and self.completed_at:
                time_taken = (self.completed_at - self.started_at).total_seconds() / 60
                if time_taken < self.time_limit_minutes * 0.5:
                    quality += 10
        
        self.quality_score = max(0, min(100, quality))
        
        quality_desc = "poorly" if quality < 40 else "adequately" if quality < 70 else "well" if quality < 90 else "excellently"
        
        return True, f"{self.assignee_name} completes the task {quality_desc}! (Quality: {self.quality_score})"
    
    def fail(self, reason: str = "") -> str:
        """Mark task as failed."""
        self.status = TaskStatus.FAILED
        self.completed_at = datetime.now()
        return f"{self.assignee_name} fails the task! {reason}"
    
    def to_dict(self) -> dict:
        return {
            "task_id": self.task_id,
            "assigner_dbref": self.assigner_dbref,
            "assigner_name": self.assigner_name,
            "assignee_dbref": self.assignee_dbref,
            "assignee_name": self.assignee_name,
            "task_type": self.task_type.value,
            "description": self.description,
            "location_dbref": self.location_dbref,
            "difficulty": self.difficulty,
            "time_limit_minutes": self.time_limit_minutes,
            "status": self.status.value,
            "progress": self.progress,
            "quality_score": self.quality_score,
            "assigned_at": self.assigned_at.isoformat() if self.assigned_at else None,
            "started_at": self.started_at.isoformat() if self.started_at else None,
            "completed_at": self.completed_at.isoformat() if self.completed_at else None,
        }
    
    @classmethod
    def from_dict(cls, data: dict) -> "ServiceTask":
        task = cls(task_id=data["task_id"])
        task.assigner_dbref = data.get("assigner_dbref", "")
        task.assigner_name = data.get("assigner_name", "")
        task.assignee_dbref = data.get("assignee_dbref", "")
        task.assignee_name = data.get("assignee_name", "")
        task.task_type = TaskType(data.get("task_type", "serving"))
        task.description = data.get("description", "")
        task.location_dbref = data.get("location_dbref", "")
        task.difficulty = data.get("difficulty", 50)
        task.time_limit_minutes = data.get("time_limit_minutes", 60)
        task.status = TaskStatus(data.get("status", "assigned"))
        task.progress = data.get("progress", 0)
        task.quality_score = data.get("quality_score", 0)
        
        if data.get("assigned_at"):
            task.assigned_at = datetime.fromisoformat(data["assigned_at"])
        if data.get("started_at"):
            task.started_at = datetime.fromisoformat(data["started_at"])
        if data.get("completed_at"):
            task.completed_at = datetime.fromisoformat(data["completed_at"])
        
        return task


# =============================================================================
# PERFORMANCE
# =============================================================================

@dataclass
class Performance:
    """A performance or exhibition."""
    performance_id: str
    
    # Performer
    performer_dbref: str = ""
    performer_name: str = ""
    
    # Type and venue
    performance_type: PerformanceType = PerformanceType.DANCE
    venue_dbref: str = ""
    venue_name: str = ""
    
    # Audience
    audience_dbrefs: List[str] = field(default_factory=list)
    
    # Status
    is_active: bool = False
    stage: int = 0              # Current stage of performance
    max_stages: int = 5
    
    # Ratings
    arousal_generated: int = 0  # Total arousal caused
    tips_earned: int = 0        # Tips received
    
    # Timing
    started_at: Optional[datetime] = None
    
    def start(self) -> str:
        """Start the performance."""
        self.is_active = True
        self.started_at = datetime.now()
        self.stage = 1
        
        start_messages = {
            PerformanceType.DANCE: f"{self.performer_name} begins to dance...",
            PerformanceType.STRIP: f"{self.performer_name} starts a teasing dance, fingers playing with clothing...",
            PerformanceType.POSE: f"{self.performer_name} strikes a provocative pose...",
            PerformanceType.DISPLAY: f"{self.performer_name} is put on display for viewing...",
            PerformanceType.ENTERTAIN: f"{self.performer_name} begins entertaining the audience...",
            PerformanceType.PLEASURE: f"{self.performer_name} begins their service...",
        }
        
        return start_messages.get(self.performance_type, f"{self.performer_name} begins performing.")
    
    def advance_stage(self) -> Tuple[bool, str]:
        """
        Advance to next stage.
        Returns (finished, message).
        """
        self.stage += 1
        
        if self.stage > self.max_stages:
            return self.finish()
        
        # Generate arousal for audience
        arousal = random.randint(5, 15) * self.stage
        self.arousal_generated += arousal
        
        stage_messages = {
            PerformanceType.STRIP: [
                "A piece of clothing comes off...",
                "More skin is revealed...",
                "Nearly bare now...",
                "Down to the last scraps...",
                "Fully exposed!",
            ],
            PerformanceType.DANCE: [
                "The dance grows more sensual...",
                "Movements become more provocative...",
                "Hips sway hypnotically...",
                "The dance reaches a fever pitch...",
                "A final flourish!",
            ],
        }
        
        messages = stage_messages.get(self.performance_type, [f"Stage {self.stage}..."])
        msg_idx = min(self.stage - 1, len(messages) - 1)
        
        return False, messages[msg_idx]
    
    def finish(self) -> Tuple[bool, str]:
        """Finish the performance."""
        self.is_active = False
        return True, f"{self.performer_name}'s performance concludes! (Arousal generated: {self.arousal_generated}, Tips: {self.tips_earned})"
    
    def add_tip(self, amount: int, tipper_name: str = "") -> str:
        """Add a tip."""
        self.tips_earned += amount
        if tipper_name:
            return f"{tipper_name} tips {amount} coins!"
        return f"A tip of {amount} coins!"
    
    def to_dict(self) -> dict:
        return {
            "performance_id": self.performance_id,
            "performer_dbref": self.performer_dbref,
            "performer_name": self.performer_name,
            "performance_type": self.performance_type.value,
            "venue_dbref": self.venue_dbref,
            "venue_name": self.venue_name,
            "audience_dbrefs": self.audience_dbrefs,
            "is_active": self.is_active,
            "stage": self.stage,
            "max_stages": self.max_stages,
            "arousal_generated": self.arousal_generated,
            "tips_earned": self.tips_earned,
            "started_at": self.started_at.isoformat() if self.started_at else None,
        }
    
    @classmethod
    def from_dict(cls, data: dict) -> "Performance":
        perf = cls(performance_id=data["performance_id"])
        perf.performer_dbref = data.get("performer_dbref", "")
        perf.performer_name = data.get("performer_name", "")
        perf.performance_type = PerformanceType(data.get("performance_type", "dance"))
        perf.venue_dbref = data.get("venue_dbref", "")
        perf.venue_name = data.get("venue_name", "")
        perf.audience_dbrefs = data.get("audience_dbrefs", [])
        perf.is_active = data.get("is_active", False)
        perf.stage = data.get("stage", 0)
        perf.max_stages = data.get("max_stages", 5)
        perf.arousal_generated = data.get("arousal_generated", 0)
        perf.tips_earned = data.get("tips_earned", 0)
        
        if data.get("started_at"):
            perf.started_at = datetime.fromisoformat(data["started_at"])
        
        return perf


# =============================================================================
# SERVICE SYSTEM
# =============================================================================

class ServiceSystem:
    """
    Manages service roles and tasks.
    """
    
    @staticmethod
    def generate_id(prefix: str = "TSK") -> str:
        """Generate unique ID."""
        timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
        rand = random.randint(1000, 9999)
        return f"{prefix}-{timestamp}-{rand}"
    
    @staticmethod
    def assign_task(
        assigner,
        assignee,
        task_type: TaskType,
        description: str,
        difficulty: int = 50,
        time_limit: int = 60,
    ) -> ServiceTask:
        """Assign a task to a servant."""
        task = ServiceTask(
            task_id=ServiceSystem.generate_id("TSK"),
            assigner_dbref=assigner.dbref,
            assigner_name=assigner.key,
            assignee_dbref=assignee.dbref,
            assignee_name=assignee.key,
            task_type=task_type,
            description=description,
            difficulty=difficulty,
            time_limit_minutes=time_limit,
            assigned_at=datetime.now(),
        )
        
        return task
    
    @staticmethod
    def start_performance(
        performer,
        performance_type: PerformanceType,
        venue = None,
    ) -> Performance:
        """Start a performance."""
        perf = Performance(
            performance_id=ServiceSystem.generate_id("PRF"),
            performer_dbref=performer.dbref,
            performer_name=performer.key,
            performance_type=performance_type,
        )
        
        if venue:
            perf.venue_dbref = venue.dbref
            perf.venue_name = venue.key
        
        return perf


# =============================================================================
# SERVICE MIXIN
# =============================================================================

class ServantMixin:
    """
    Mixin for characters that can serve.
    """
    
    @property
    def service_role(self) -> Optional[ServiceRole]:
        """Get current service role."""
        role = self.attributes.get("service_role")
        if role:
            return ServiceRole(role)
        return None
    
    @service_role.setter
    def service_role(self, role: Optional[ServiceRole]):
        """Set service role."""
        if role:
            self.attributes.add("service_role", role.value)
        else:
            self.attributes.remove("service_role")
    
    @property
    def current_uniform(self) -> Optional[str]:
        """Get current uniform key."""
        return self.attributes.get("service_uniform")
    
    @current_uniform.setter
    def current_uniform(self, uniform_key: Optional[str]):
        """Set current uniform."""
        if uniform_key:
            self.attributes.add("service_uniform", uniform_key)
        else:
            self.attributes.remove("service_uniform")
    
    @property
    def current_tasks(self) -> List[ServiceTask]:
        """Get assigned tasks."""
        data = self.attributes.get("service_tasks", [])
        return [ServiceTask.from_dict(t) for t in data]
    
    def add_task(self, task: ServiceTask) -> None:
        """Add a task."""
        tasks = self.attributes.get("service_tasks", [])
        tasks.append(task.to_dict())
        self.attributes.add("service_tasks", tasks)
    
    def get_task(self, task_id: str) -> Optional[ServiceTask]:
        """Get a task by ID."""
        for task in self.current_tasks:
            if task.task_id == task_id:
                return task
        return None
    
    def update_task(self, task: ServiceTask) -> None:
        """Update a task."""
        tasks = self.attributes.get("service_tasks", [])
        for i, t in enumerate(tasks):
            if t.get("task_id") == task.task_id:
                tasks[i] = task.to_dict()
                break
        self.attributes.add("service_tasks", tasks)
    
    @property
    def current_performance(self) -> Optional[Performance]:
        """Get current performance."""
        data = self.attributes.get("current_performance")
        if data:
            return Performance.from_dict(data)
        return None
    
    @current_performance.setter
    def current_performance(self, perf: Optional[Performance]):
        """Set current performance."""
        if perf:
            self.attributes.add("current_performance", perf.to_dict())
        else:
            self.attributes.remove("current_performance")
    
    def is_serving(self) -> bool:
        """Check if in a service role."""
        return self.service_role is not None
    
    def is_performing(self) -> bool:
        """Check if currently performing."""
        perf = self.current_performance
        return perf is not None and perf.is_active


__all__ = [
    "ServiceRole",
    "TaskType",
    "TaskStatus",
    "PerformanceType",
    "ServiceUniform",
    "ALL_UNIFORMS",
    "ServiceTask",
    "Performance",
    "ServiceSystem",
    "ServantMixin",
]
