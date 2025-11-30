"""
Scene System
============

Tracks roleplay scenes with:
- Scene start/end times
- Participants
- Position history
- Action log
- Optional privacy settings
- Scene summaries

Commands:
    scene start [title] [= description]
    scene end [= summary]
    scene join
    scene leave
    scene info
    scene log [page]
    scene title <new title>
    scene private/public
"""

from datetime import datetime
from typing import Dict, List, Set, Optional, Any
from dataclasses import dataclass, field

# Evennia imports - only used when commands are loaded
try:
    from evennia import Command, CmdSet
    # Check if actually usable (evennia might be installed but not configured)
    if Command is None:
        raise ImportError("Evennia Command is None - not configured")
    HAS_EVENNIA = True
except (ImportError, Exception):
    HAS_EVENNIA = False
    # Stubs for testing without Evennia
    class Command:
        key = ""
        aliases = []
        locks = ""
        help_category = ""
        
        def parse(self):
            pass
        
        def func(self):
            pass
    
    class CmdSet:
        key = ""
        
        def at_cmdset_creation(self):
            pass
        
        def add(self, cmd):
            pass


@dataclass
class SceneAction:
    """A single action within a scene."""
    timestamp: datetime
    actor: Any  # Character reference
    action_type: str  # "thrust", "lick", "position_start", etc.
    target: Any = None  # Target character if applicable
    details: Dict = field(default_factory=dict)
    
    def describe(self) -> str:
        """Get human-readable description of the action."""
        actor_name = getattr(self.actor, "key", "Someone")
        
        if self.action_type == "position_start":
            pos_name = self.details.get("position_name", "a position")
            participants = self.details.get("participants", [])
            return f"{actor_name} initiated {pos_name} with {', '.join(participants)}"
        
        elif self.action_type == "position_end":
            pos_name = self.details.get("position_name", "the position")
            return f"{pos_name} ended"
        
        elif self.action_type == "position_join":
            pos_name = self.details.get("position_name", "the position")
            return f"{actor_name} joined {pos_name}"
        
        elif self.target:
            target_name = getattr(self.target, "key", "someone")
            if self.action_type == "thrust":
                intensity = self.details.get("intensity", 0.5)
                word = "hard" if intensity > 0.7 else "gently" if intensity < 0.3 else ""
                return f"{actor_name} thrust {word} into {target_name}".strip()
            elif self.action_type == "cum":
                loc = self.details.get("location", "")
                if loc == "in":
                    return f"{actor_name} came inside {target_name}"
                elif loc == "on":
                    part = self.details.get("part", "")
                    return f"{actor_name} came on {target_name}'s {part}" if part else f"{actor_name} came on {target_name}"
                return f"{actor_name} climaxed"
            else:
                part = self.details.get("part", "")
                if part:
                    return f"{actor_name} {self.action_type}ed {target_name}'s {part}"
                return f"{actor_name} {self.action_type}ed {target_name}"
        
        return f"{actor_name} performed {self.action_type}"


@dataclass
class PositionRecord:
    """Record of a position used during a scene."""
    position_key: str
    position_name: str
    started_at: datetime
    ended_at: Optional[datetime] = None
    participants: List[str] = field(default_factory=list)
    slot_assignments: Dict[str, str] = field(default_factory=dict)  # slot -> char name
    
    def duration_seconds(self) -> float:
        """Get duration in seconds."""
        end = self.ended_at or datetime.now()
        return (end - self.started_at).total_seconds()
    
    def describe(self) -> str:
        """Get human-readable description."""
        duration = self.duration_seconds()
        mins = int(duration // 60)
        if mins > 0:
            dur_str = f"{mins} min"
        else:
            dur_str = f"{int(duration)} sec"
        
        return f"{self.position_name} ({', '.join(self.participants)}) - {dur_str}"


class Scene:
    """
    Represents an active or completed RP scene.
    """
    
    def __init__(self, room, creator, title="Untitled Scene"):
        self.room = room
        self.creator = creator
        self.title = title
        self.description = ""
        
        self.started_at = datetime.now()
        self.ended_at = None
        
        self.participants: Set[Any] = {creator}  # Characters in scene
        self.positions: List[PositionRecord] = []  # Position history
        self.actions: List[SceneAction] = []  # Action log
        
        self.is_private = False  # If True, only participants see
        self.summary = ""  # End-of-scene summary
        
        # Track current position for quick reference
        self.current_position: Optional[PositionRecord] = None
    
    @property
    def is_active(self) -> bool:
        return self.ended_at is None
    
    @property
    def duration_seconds(self) -> float:
        end = self.ended_at or datetime.now()
        return (end - self.started_at).total_seconds()
    
    def add_participant(self, char):
        """Add a participant to the scene."""
        self.participants.add(char)
        self.record_action(char, "scene_join")
    
    def remove_participant(self, char):
        """Remove a participant from the scene."""
        self.participants.discard(char)
        self.record_action(char, "scene_leave")
    
    def record_action(self, actor, action_type, target=None, details=None):
        """Record an action in the scene."""
        action = SceneAction(
            timestamp=datetime.now(),
            actor=actor,
            action_type=action_type,
            target=target,
            details=details or {}
        )
        self.actions.append(action)
        
        # Auto-add participants
        if actor and actor not in self.participants:
            self.participants.add(actor)
        if target and target not in self.participants:
            self.participants.add(target)
    
    def start_position(self, position_key, position_name, participants, slots):
        """Record a position starting."""
        # End previous position if any
        if self.current_position:
            self.current_position.ended_at = datetime.now()
        
        record = PositionRecord(
            position_key=position_key,
            position_name=position_name,
            started_at=datetime.now(),
            participants=[getattr(p, "key", str(p)) for p in participants],
            slot_assignments=slots
        )
        
        self.positions.append(record)
        self.current_position = record
        
        self.record_action(
            participants[0] if participants else None,
            "position_start",
            details={
                "position_name": position_name,
                "participants": record.participants
            }
        )
    
    def end_position(self, position_key=None):
        """Record a position ending."""
        if self.current_position:
            self.current_position.ended_at = datetime.now()
            
            self.record_action(
                None,
                "position_end",
                details={"position_name": self.current_position.position_name}
            )
            
            self.current_position = None
    
    def end_scene(self, summary=""):
        """End the scene."""
        self.ended_at = datetime.now()
        self.summary = summary
        
        # End any active position
        if self.current_position:
            self.end_position()
    
    def get_log(self, page=1, per_page=20) -> List[SceneAction]:
        """Get paginated action log."""
        start = (page - 1) * per_page
        end = start + per_page
        return self.actions[start:end]
    
    def get_stats(self) -> Dict:
        """Get scene statistics."""
        action_counts = {}
        for action in self.actions:
            action_counts[action.action_type] = action_counts.get(action.action_type, 0) + 1
        
        return {
            "duration_minutes": self.duration_seconds / 60,
            "participants": len(self.participants),
            "positions_used": len(self.positions),
            "total_actions": len(self.actions),
            "action_breakdown": action_counts,
        }
    
    def describe(self) -> str:
        """Get scene description/summary."""
        lines = []
        lines.append(f"|w{self.title}|n")
        
        if self.description:
            lines.append(self.description)
        
        status = "Active" if self.is_active else "Ended"
        lines.append(f"|yStatus:|n {status}")
        
        duration = self.duration_seconds
        if duration > 3600:
            dur_str = f"{duration/3600:.1f} hours"
        elif duration > 60:
            dur_str = f"{int(duration/60)} minutes"
        else:
            dur_str = f"{int(duration)} seconds"
        lines.append(f"|yDuration:|n {dur_str}")
        
        participant_names = [getattr(p, "key", str(p)) for p in self.participants]
        lines.append(f"|yParticipants:|n {', '.join(participant_names)}")
        
        if self.positions:
            lines.append(f"|yPositions used:|n {len(self.positions)}")
            for pos in self.positions[-3:]:  # Last 3 positions
                lines.append(f"  - {pos.describe()}")
        
        if self.summary:
            lines.append(f"|ySummary:|n {self.summary}")
        
        return "\n".join(lines)


class SceneManager:
    """
    Manages scenes for a room.
    """
    
    def __init__(self):
        self.active_scene: Optional[Scene] = None
        self.past_scenes: List[Scene] = []
    
    def start_scene(self, room, creator, title="Untitled Scene") -> Scene:
        """Start a new scene."""
        if self.active_scene:
            # End current scene first
            self.end_scene()
        
        scene = Scene(room, creator, title)
        self.active_scene = scene
        return scene
    
    def end_scene(self, summary="") -> Optional[Scene]:
        """End the active scene."""
        if not self.active_scene:
            return None
        
        scene = self.active_scene
        scene.end_scene(summary)
        self.past_scenes.append(scene)
        self.active_scene = None
        return scene
    
    def get_scene(self) -> Optional[Scene]:
        """Get the active scene."""
        return self.active_scene
    
    def record_action(self, actor, action_type, target=None, details=None):
        """Record an action to the active scene if any."""
        if self.active_scene:
            self.active_scene.record_action(actor, action_type, target, details)
    
    def record_position(self, position_key, position_name, participants, slots):
        """Record a position starting."""
        if self.active_scene:
            self.active_scene.start_position(position_key, position_name, participants, slots)


def get_scene_manager(location) -> Optional[SceneManager]:
    """Get or create scene manager for a location."""
    if not location:
        return None
    
    manager = getattr(location, "_scene_manager", None)
    if manager is None:
        manager = SceneManager()
        location._scene_manager = manager
    return manager


# ============================================================================
# Commands
# ============================================================================

class CmdScene(Command):
    """
    Manage roleplay scenes.
    
    Usage:
        scene start [title] [= description]
        scene end [= summary]
        scene join
        scene leave
        scene info
        scene log [page]
        scene title <new title>
        scene private
        scene public
        scene history
        
    Scenes track participants, positions used, and action history.
    Great for remembering what happened in a session!
    """
    
    key = "scene"
    locks = "cmd:all()"
    help_category = "Social"
    
    def parse(self):
        self.subcommand = ""
        self.args_after = ""
        self.description = ""
        
        args = self.args.strip()
        
        if "=" in args:
            args, self.description = args.split("=", 1)
            self.description = self.description.strip()
            args = args.strip()
        
        parts = args.split(None, 1)
        if len(parts) >= 1:
            self.subcommand = parts[0].lower()
        if len(parts) >= 2:
            self.args_after = parts[1].strip()
    
    def func(self):
        caller = self.caller
        location = caller.location
        
        if not location:
            caller.msg("You need to be somewhere to manage scenes.")
            return
        
        manager = get_scene_manager(location)
        
        subcmd = self.subcommand
        
        if subcmd == "start":
            self.do_start(manager)
        elif subcmd == "end":
            self.do_end(manager)
        elif subcmd == "join":
            self.do_join(manager)
        elif subcmd == "leave":
            self.do_leave(manager)
        elif subcmd == "info":
            self.do_info(manager)
        elif subcmd == "log":
            self.do_log(manager)
        elif subcmd == "title":
            self.do_title(manager)
        elif subcmd == "private":
            self.do_privacy(manager, True)
        elif subcmd == "public":
            self.do_privacy(manager, False)
        elif subcmd == "history":
            self.do_history(manager)
        else:
            # Default - show current scene or help
            if manager.active_scene:
                self.do_info(manager)
            else:
                caller.msg("No active scene. Use |wscene start [title]|n to begin one.")
    
    def do_start(self, manager):
        """Start a new scene."""
        caller = self.caller
        
        if manager.active_scene:
            caller.msg("A scene is already active. Use |wscene end|n first.")
            return
        
        title = self.args_after or "Untitled Scene"
        scene = manager.start_scene(caller.location, caller, title)
        
        if self.description:
            scene.description = self.description
        
        msg = f"|g{caller.key} starts a scene: |w{title}|n"
        if self.description:
            msg += f"\n{self.description}"
        
        caller.location.msg_contents(msg)
    
    def do_end(self, manager):
        """End the active scene."""
        caller = self.caller
        
        if not manager.active_scene:
            caller.msg("No active scene to end.")
            return
        
        summary = self.description
        scene = manager.end_scene(summary)
        
        stats = scene.get_stats()
        
        msg = f"|y{caller.key} ends the scene: |w{scene.title}|n"
        msg += f"\nDuration: {stats['duration_minutes']:.1f} minutes"
        msg += f"\nPositions: {stats['positions_used']}"
        msg += f"\nActions: {stats['total_actions']}"
        
        if summary:
            msg += f"\n|ySummary:|n {summary}"
        
        caller.location.msg_contents(msg)
    
    def do_join(self, manager):
        """Join the active scene."""
        caller = self.caller
        
        if not manager.active_scene:
            caller.msg("No active scene to join.")
            return
        
        scene = manager.active_scene
        
        if caller in scene.participants:
            caller.msg("You're already in this scene.")
            return
        
        scene.add_participant(caller)
        caller.location.msg_contents(f"{caller.key} joins the scene.")
    
    def do_leave(self, manager):
        """Leave the active scene."""
        caller = self.caller
        
        if not manager.active_scene:
            caller.msg("No active scene.")
            return
        
        scene = manager.active_scene
        
        if caller not in scene.participants:
            caller.msg("You're not in this scene.")
            return
        
        scene.remove_participant(caller)
        caller.location.msg_contents(f"{caller.key} leaves the scene.")
    
    def do_info(self, manager):
        """Show scene information."""
        caller = self.caller
        
        if not manager.active_scene:
            caller.msg("No active scene. Use |wscene start|n to begin one.")
            return
        
        caller.msg(manager.active_scene.describe())
    
    def do_log(self, manager):
        """Show action log."""
        caller = self.caller
        
        if not manager.active_scene:
            caller.msg("No active scene.")
            return
        
        scene = manager.active_scene
        
        try:
            page = int(self.args_after) if self.args_after else 1
        except ValueError:
            page = 1
        
        actions = scene.get_log(page)
        
        if not actions:
            caller.msg("No actions recorded yet." if page == 1 else "No more actions.")
            return
        
        caller.msg(f"|wScene Log - Page {page}|n")
        
        for action in actions:
            time_str = action.timestamp.strftime("%H:%M")
            caller.msg(f"  [{time_str}] {action.describe()}")
        
        total_pages = (len(scene.actions) + 19) // 20
        if total_pages > 1:
            caller.msg(f"\nPage {page}/{total_pages}. Use |wscene log <page>|n")
    
    def do_title(self, manager):
        """Change scene title."""
        caller = self.caller
        
        if not manager.active_scene:
            caller.msg("No active scene.")
            return
        
        if not self.args_after:
            caller.msg("What should the new title be?")
            return
        
        old_title = manager.active_scene.title
        manager.active_scene.title = self.args_after
        
        caller.location.msg_contents(
            f"Scene renamed from '{old_title}' to '|w{self.args_after}|n'"
        )
    
    def do_privacy(self, manager, private):
        """Set scene privacy."""
        caller = self.caller
        
        if not manager.active_scene:
            caller.msg("No active scene.")
            return
        
        manager.active_scene.is_private = private
        
        if private:
            caller.location.msg_contents("Scene is now |rprivate|n.")
        else:
            caller.location.msg_contents("Scene is now |gpublic|n.")
    
    def do_history(self, manager):
        """Show past scenes."""
        caller = self.caller
        
        if not manager.past_scenes:
            caller.msg("No past scenes recorded.")
            return
        
        caller.msg("|wPast Scenes:|n")
        
        for i, scene in enumerate(manager.past_scenes[-10:], 1):
            date_str = scene.started_at.strftime("%m/%d %H:%M")
            duration = scene.duration_seconds / 60
            caller.msg(f"  {i}. {scene.title} ({date_str}, {duration:.0f}m)")


class SceneCmdSet(CmdSet):
    """Scene management commands."""
    
    key = "scene_cmdset"
    
    def at_cmdset_creation(self):
        self.add(CmdScene())


# ============================================================================
# Integration Hooks
# ============================================================================

def record_scene_action(actor, action_type, target=None, details=None):
    """
    Hook for other systems to record actions to the active scene.
    
    Call this from sexual commands, position changes, etc.
    """
    location = getattr(actor, "location", None)
    manager = get_scene_manager(location)
    if manager:
        manager.record_action(actor, action_type, target, details)


def record_scene_position(location, position_key, position_name, participants, slots):
    """
    Hook for position system to record position changes.
    
    Call this when a position starts.
    """
    manager = get_scene_manager(location)
    if manager:
        manager.record_position(position_key, position_name, participants, slots)
