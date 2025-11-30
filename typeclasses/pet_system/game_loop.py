"""
Game Loop & Tick System
=======================

The heartbeat of the world. Every tick, things happen.
Time passes. Arousal builds. Resistance fades.
Events trigger. NPCs act. Transformations progress.

You can run, but you can't hide from the tick.
"""

from evennia import DefaultScript, create_object, search_object
from evennia.utils import logger
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
import random

from .typeclasses import PetSystemsCharacter, PetSystemsNPC, PetSystemsRoom
from .world import ALL_NPC_TEMPLATES, generate_npc, NPCRole
from .world.locations import ALL_LOCATION_TEMPLATES
from .world.events import ALL_EVENT_TEMPLATES, get_random_event, trigger_event
from .integration import SystemHooks, SystemEvent


# =============================================================================
# TICK CONFIGURATION
# =============================================================================

class TickConfig:
    """Configuration for the tick system."""
    
    # How often ticks run (in real seconds)
    TICK_INTERVAL = 60  # 1 minute real time
    
    # How much game time passes per tick
    GAME_HOURS_PER_TICK = 0.5  # 30 game minutes
    
    # Event chances (per tick)
    BASE_EVENT_CHANCE = 0.15
    DANGEROUS_LOCATION_MULTIPLIER = 2.0
    VULNERABILITY_MULTIPLIER = 0.01  # Per point of vulnerability
    
    # NPC behavior
    NPC_ACTION_CHANCE = 0.3
    NPC_AGGRESSION_BONUS = 0.005  # Per point of aggression
    
    # Degradation rates (per tick)
    RESISTANCE_DECAY_CAPTURED = 1  # Lose resistance while captured
    AROUSAL_BUILDUP_DENIED = 5  # Arousal builds when denied
    TRANSFORMATION_AMBIENT = 1  # Passive transformation progress
    
    # Recovery rates (per tick, only when safe)
    STAMINA_RECOVERY = 5
    AROUSAL_DECAY_FREE = 2


# =============================================================================
# MAIN GAME TICK SCRIPT
# =============================================================================

class GameTickScript(DefaultScript):
    """
    The main game tick script. Runs continuously and processes
    all time-based game mechanics.
    
    This is the engine of your suffering.
    """
    
    def at_script_creation(self):
        """Called when script is first created."""
        self.key = "game_tick_script"
        self.desc = "Main game tick processor"
        self.interval = TickConfig.TICK_INTERVAL
        self.persistent = True
        self.start_delay = True
        
        # Tick tracking
        self.db.total_ticks = 0
        self.db.game_time_hours = 0
        self.db.last_tick = datetime.now()
        
        # Statistics (for my amusement)
        self.db.total_captures = 0
        self.db.total_breedings = 0
        self.db.total_cum_ml = 0
        self.db.total_eggs_laid = 0
        self.db.total_orgasms_forced = 0
        self.db.total_transformations_completed = 0
        self.db.resistance_broken_count = 0
    
    def at_repeat(self):
        """Called every tick interval."""
        self.db.total_ticks += 1
        self.db.game_time_hours += TickConfig.GAME_HOURS_PER_TICK
        self.db.last_tick = datetime.now()
        
        hours = TickConfig.GAME_HOURS_PER_TICK
        
        # Process all characters
        for character in self._get_all_characters():
            self._process_character_tick(character, hours)
        
        # Process all rooms
        for room in self._get_all_rooms():
            self._process_room_tick(room, hours)
        
        # Process scheduled events
        self._process_scheduled_events()
        
        # Trigger system-wide hooks
        SystemHooks.trigger(SystemEvent.TICK.value, hours=hours)
        
        if self.db.game_time_hours % 1 == 0:  # Every game hour
            SystemHooks.trigger(SystemEvent.HOUR_PASSED.value)
        
        if self.db.game_time_hours % 24 == 0:  # Every game day
            SystemHooks.trigger(SystemEvent.DAY_PASSED.value)
            self._daily_report()
    
    def _get_all_characters(self) -> List:
        """Get all player characters."""
        return PetSystemsCharacter.objects.all()
    
    def _get_all_rooms(self) -> List:
        """Get all pet systems rooms."""
        return PetSystemsRoom.objects.all()
    
    def _process_character_tick(self, character: PetSystemsCharacter, hours: float):
        """Process tick for a single character."""
        messages = []
        
        # === PHYSICAL STATE ===
        if hasattr(character, 'character_state'):
            state = character.character_state
            
            # Stamina recovery (if safe and not exhausted)
            if not character.db.is_captured:
                state.physical.stamina = min(100, 
                    state.physical.stamina + TickConfig.STAMINA_RECOVERY)
            
            # Arousal mechanics
            if state.sexual.denied:
                # Denial builds arousal
                state.sexual.arousal = min(99, 
                    state.sexual.arousal + TickConfig.AROUSAL_BUILDUP_DENIED)
                state.sexual.hours_denied += hours
                
                if state.sexual.arousal >= 95:
                    messages.append("Your body aches with denied need...")
            elif not character.db.is_captured:
                # Free characters can calm down
                state.sexual.arousal = max(0,
                    state.sexual.arousal - TickConfig.AROUSAL_DECAY_FREE)
            
            character.character_state = state
        
        # === RESISTANCE DECAY ===
        if character.db.is_captured:
            # Resistance slowly fades while captured
            old_resistance = character.db.current_resistance
            character.db.current_resistance = max(0,
                character.db.current_resistance - TickConfig.RESISTANCE_DECAY_CAPTURED)
            
            if old_resistance >= 30 and character.db.current_resistance < 30:
                messages.append("Something inside you... breaks. Resistance feels so futile.")
                self.db.resistance_broken_count += 1
            elif old_resistance >= 10 and character.db.current_resistance < 10:
                messages.append("You can barely remember why you ever resisted...")
                character.db.times_broken = (character.db.times_broken or 0) + 1
        
        # === INFLATION PROCESSING ===
        if hasattr(character, 'inflation'):
            tracker = character.inflation
            inflation_messages = tracker.process_time(hours)
            messages.extend(inflation_messages)
            character.db.inflation = tracker.to_dict()
            
            # Track total cum
            self.db.total_cum_ml += tracker.total_cum_received_ml
        
        # === TRANSFORMATION PROGRESS ===
        if hasattr(character, 'transformations'):
            mgr = character.transformations
            
            for trans_type, trans in list(mgr.transformations.items()):
                if trans.progress > 0 and trans.progress < 100:
                    # Passive progression while captured
                    if character.db.is_captured:
                        msg, stage_msg = mgr.add_corruption(
                            trans_type, 
                            TickConfig.TRANSFORMATION_AMBIENT,
                            "ambient"
                        )
                        if msg:
                            messages.append(msg)
                        if stage_msg:
                            messages.append(stage_msg)
                    
                    # Check for completion
                    if trans.progress >= 100:
                        messages.append(f"Your {trans_type.value} transformation is complete!")
                        self.db.total_transformations_completed += 1
            
            character.db.transformations = mgr.to_dict()
        
        # === LACTATION ===
        if hasattr(character, 'hucow_stats'):
            stats = character.hucow_stats
            if stats.is_lactating:
                # Milk builds up
                buildup = int(stats.production_rate_ml_hour * hours)
                
                if hasattr(character, 'character_state'):
                    state = character.character_state
                    state.physical.breast_fullness = min(100,
                        state.physical.breast_fullness + buildup // 10)
                    
                    if state.physical.breast_fullness >= 90:
                        messages.append("Your breasts are painfully full. You need to be milked...")
                    
                    character.character_state = state
        
        # === EGG PRESSURE ===
        if hasattr(character, 'oviposition'):
            ovi = character.oviposition
            if ovi.current_eggs > 0:
                # Eggs want out
                if ovi.current_eggs >= 10:
                    messages.append("The eggs inside you shift and press... you need to lay them.")
                
                # Random chance to start laying
                if random.random() < 0.1 * (ovi.current_eggs / 10):
                    # Force egg laying
                    laid = random.randint(1, min(5, ovi.current_eggs))
                    ovi.current_eggs -= laid
                    ovi.total_eggs_laid += laid
                    messages.append(f"Your body convulses as {laid} eggs push out!")
                    self.db.total_eggs_laid += laid
                
                character.db.oviposition = ovi.to_dict() if hasattr(ovi, 'to_dict') else ovi.__dict__
        
        # === ORGASM CHECK ===
        if hasattr(character, 'character_state'):
            state = character.character_state
            
            if state.sexual.arousal >= 100:
                # Forced orgasm
                forced = character.db.is_captured or state.sexual.denied
                state.sexual.orgasm(forced=forced)
                
                messages.append("Your body betrays you as you cum!")
                self.db.total_orgasms_forced += 1
                
                # Orgasm can trigger milk letdown
                if hasattr(character, 'hucow_stats'):
                    if character.hucow_stats.is_lactating:
                        messages.append("Milk sprays from your nipples!")
                
                character.character_state = state
        
        # === SEND MESSAGES ===
        if messages:
            character.msg("\n".join(messages))
    
    def _process_room_tick(self, room: PetSystemsRoom, hours: float):
        """Process tick for a room."""
        room.process_tick(hours)
    
    def _process_scheduled_events(self):
        """Process any scheduled events."""
        # Would handle scheduled auctions, shows, etc.
        pass
    
    def _daily_report(self):
        """Generate daily statistics (for the game master's amusement)."""
        report = [
            "=== Daily Report ===",
            f"Total Ticks: {self.db.total_ticks}",
            f"Game Time: {self.db.game_time_hours:.1f} hours",
            f"Captures: {self.db.total_captures}",
            f"Breedings: {self.db.total_breedings}",
            f"Cum Received: {self.db.total_cum_ml}ml",
            f"Eggs Laid: {self.db.total_eggs_laid}",
            f"Forced Orgasms: {self.db.total_orgasms_forced}",
            f"Transformations Complete: {self.db.total_transformations_completed}",
            f"Resistance Broken: {self.db.resistance_broken_count}",
        ]
        logger.log_info("\n".join(report))
    
    def get_status(self) -> str:
        """Get current tick system status."""
        return (
            f"=== Game Tick Status ===\n"
            f"Total Ticks: {self.db.total_ticks}\n"
            f"Game Time: {self.db.game_time_hours:.1f} hours ({self.db.game_time_hours/24:.1f} days)\n"
            f"Last Tick: {self.db.last_tick}\n"
            f"Tick Interval: {self.interval}s\n"
            f"\n=== Statistics ===\n"
            f"Captures: {self.db.total_captures}\n"
            f"Breedings: {self.db.total_breedings}\n"
            f"Total Cum: {self.db.total_cum_ml}ml\n"
            f"Eggs Laid: {self.db.total_eggs_laid}\n"
            f"Forced Orgasms: {self.db.total_orgasms_forced}\n"
            f"Transformations: {self.db.total_transformations_completed}\n"
            f"Broken: {self.db.resistance_broken_count}\n"
        )


# =============================================================================
# NPC SPAWNER SCRIPT
# =============================================================================

class NPCSpawnerScript(DefaultScript):
    """
    Spawns NPCs in appropriate locations.
    Ensures there are always... predators about.
    """
    
    def at_script_creation(self):
        """Called when script is first created."""
        self.key = "npc_spawner_script"
        self.desc = "NPC spawner"
        self.interval = 300  # Every 5 minutes
        self.persistent = True
        
        self.db.total_spawned = 0
        self.db.active_npcs = []
    
    def at_repeat(self):
        """Spawn NPCs as needed."""
        for room in PetSystemsRoom.objects.all():
            self._check_room_spawns(room)
    
    def _check_room_spawns(self, room: PetSystemsRoom):
        """Check if room needs NPC spawns."""
        current_npcs = room.get_npcs()
        max_npcs = room.db.max_npcs or 3
        
        if len(current_npcs) >= max_npcs:
            return
        
        spawn_types = room.db.spawns_npcs or []
        if not spawn_types:
            return
        
        # Spawn chance based on how empty the room is
        spawn_chance = 0.3 * (1 - len(current_npcs) / max_npcs)
        
        if random.random() < spawn_chance:
            # Pick a random NPC type to spawn
            npc_type = random.choice(spawn_types)
            
            # Find matching template
            template = None
            for t in ALL_NPC_TEMPLATES.values():
                if t.role.value == npc_type or npc_type in t.template_id:
                    template = t
                    break
            
            if not template:
                template = generate_npc()
            
            # Spawn NPC
            npc = PetSystemsNPC.create_from_template(template, location=room)
            
            if npc:
                self.db.total_spawned += 1
                self.db.active_npcs.append(npc.dbref)
                
                # Announce arrival
                room.msg_contents(f"{npc.key} arrives.")


# =============================================================================
# EVENT SCHEDULER SCRIPT
# =============================================================================

class EventSchedulerScript(DefaultScript):
    """
    Schedules and triggers special events.
    Auctions, shows, raids, rituals...
    """
    
    def at_script_creation(self):
        """Called when script is first created."""
        self.key = "event_scheduler_script"
        self.desc = "Event scheduler"
        self.interval = 600  # Every 10 minutes
        self.persistent = True
        
        self.db.scheduled_events = []
        self.db.past_events = []
    
    def at_repeat(self):
        """Check for and trigger scheduled events."""
        now = datetime.now()
        
        # Check scheduled events
        for event in list(self.db.scheduled_events):
            if event.get("trigger_time") and event["trigger_time"] <= now:
                self._trigger_scheduled_event(event)
                self.db.scheduled_events.remove(event)
                self.db.past_events.append(event)
        
        # Random world events
        if random.random() < 0.1:  # 10% chance per check
            self._trigger_random_world_event()
    
    def schedule_event(self, event_type: str, trigger_time: datetime, 
                       location=None, participants: List = None):
        """Schedule an event for later."""
        self.db.scheduled_events.append({
            "event_type": event_type,
            "trigger_time": trigger_time,
            "location": location.dbref if location else None,
            "participants": [p.dbref for p in (participants or [])],
        })
    
    def _trigger_scheduled_event(self, event: dict):
        """Trigger a scheduled event."""
        event_type = event.get("event_type")
        location = search_object(f"#{event['location']}")[0] if event.get("location") else None
        
        if event_type == "auction":
            self._run_auction(location)
        elif event_type == "raid":
            self._run_raid(location)
        elif event_type == "ritual":
            self._run_ritual(location)
    
    def _trigger_random_world_event(self):
        """Trigger a random world event."""
        event_types = ["wandering_slaver", "monster_sighting", "corruption_surge"]
        event_type = random.choice(event_types)
        
        # Find a room with players
        rooms_with_players = [
            r for r in PetSystemsRoom.objects.all()
            if r.get_players()
        ]
        
        if not rooms_with_players:
            return
        
        room = random.choice(rooms_with_players)
        
        if event_type == "wandering_slaver":
            # A slaver enters looking for prey
            template = ALL_NPC_TEMPLATES.get("stern_slaver") or generate_npc(role=NPCRole.SLAVER)
            npc = PetSystemsNPC.create_from_template(template, location=room)
            room.msg_contents(f"\nA {npc.key} enters, eyes scanning for potential acquisitions...")
            
        elif event_type == "monster_sighting":
            room.msg_contents("\nYou hear something large moving in the shadows...")
            
        elif event_type == "corruption_surge":
            room.msg_contents("\nA wave of dark energy washes through the area...")
            for player in room.get_players():
                if hasattr(player, 'transformations'):
                    mgr = player.transformations
                    for trans_type in list(mgr.transformations.keys()):
                        mgr.add_corruption(trans_type, 5, "ambient_surge")
                    player.db.transformations = mgr.to_dict()
    
    def _run_auction(self, location):
        """Run an auction event."""
        if not location:
            return
        
        location.msg_contents(
            "\n=== AUCTION BEGINS ===\n"
            "The auctioneer takes the stage. Fresh merchandise today!"
        )
        
        # Would run actual auction mechanics here
    
    def _run_raid(self, location):
        """Run a slaver raid event."""
        if not location:
            return
        
        location.msg_contents(
            "\n=== RAID! ===\n"
            "Slavers burst in! Everyone is a potential target!"
        )
        
        # Spawn multiple slavers
        for _ in range(3):
            template = ALL_NPC_TEMPLATES.get("stern_slaver")
            if template:
                PetSystemsNPC.create_from_template(template, location=location)
    
    def _run_ritual(self, location):
        """Run a corruption ritual event."""
        if not location:
            return
        
        location.msg_contents(
            "\n=== RITUAL BEGINS ===\n"
            "Dark chanting fills the air. The corruption spreads..."
        )
        
        for player in location.get_players():
            # Force corruption event
            trigger_event("corruption_ritual", player)


# =============================================================================
# HELPER FUNCTIONS
# =============================================================================

def start_game_systems():
    """Initialize all game systems."""
    from evennia import create_script
    
    # Create tick script if it doesn't exist
    tick_scripts = DefaultScript.objects.filter(db_key="game_tick_script")
    if not tick_scripts:
        create_script(GameTickScript)
    
    # Create spawner script
    spawner_scripts = DefaultScript.objects.filter(db_key="npc_spawner_script")
    if not spawner_scripts:
        create_script(NPCSpawnerScript)
    
    # Create event scheduler
    event_scripts = DefaultScript.objects.filter(db_key="event_scheduler_script")
    if not event_scripts:
        create_script(EventSchedulerScript)
    
    return "Game systems started."


def stop_game_systems():
    """Stop all game systems."""
    for script in DefaultScript.objects.filter(
        db_key__in=["game_tick_script", "npc_spawner_script", "event_scheduler_script"]
    ):
        script.stop()
        script.delete()
    
    return "Game systems stopped."


def get_game_status() -> str:
    """Get status of all game systems."""
    lines = ["=== Game Systems Status ==="]
    
    tick_script = DefaultScript.objects.filter(db_key="game_tick_script").first()
    if tick_script:
        lines.append(tick_script.get_status())
    else:
        lines.append("Tick system: NOT RUNNING")
    
    spawner = DefaultScript.objects.filter(db_key="npc_spawner_script").first()
    if spawner:
        lines.append(f"\nNPC Spawner: RUNNING (spawned {spawner.db.total_spawned})")
    else:
        lines.append("\nNPC Spawner: NOT RUNNING")
    
    scheduler = DefaultScript.objects.filter(db_key="event_scheduler_script").first()
    if scheduler:
        lines.append(f"Event Scheduler: RUNNING ({len(scheduler.db.scheduled_events)} pending)")
    else:
        lines.append("Event Scheduler: NOT RUNNING")
    
    return "\n".join(lines)


# =============================================================================
# EXPORTS
# =============================================================================

__all__ = [
    "TickConfig",
    "GameTickScript",
    "NPCSpawnerScript",
    "EventSchedulerScript",
    "start_game_systems",
    "stop_game_systems",
    "get_game_status",
]
