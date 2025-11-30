"""
Pet Systems Typeclasses
=======================

Actual Evennia typeclasses for characters, NPCs, and rooms.
These are the objects that exist in the game world.

The prey... and the predators.
"""

from evennia import DefaultCharacter, DefaultRoom, DefaultExit, DefaultScript
from evennia.utils import lazy_property
from dataclasses import dataclass
from typing import Dict, List, Optional, Any
import random

# Import all our mixins
from .integration import (
    PetSystemsFullMixin,
    PetSystemsSubmissiveMixin,
    PetSystemsDominantMixin,
    SystemHooks,
    SystemEvent,
    process_time_tick,
    get_character_summary,
    initialize_character,
)

from .world import NPCTemplate, ALL_NPC_TEMPLATES, generate_npc, Disposition
from .world.locations import LocationTemplate, ALL_LOCATION_TEMPLATES, LocationDanger
from .world.events import get_random_event, trigger_event, EventTemplate


# =============================================================================
# PLAYER CHARACTER
# =============================================================================

class PetSystemsCharacter(PetSystemsFullMixin, DefaultCharacter):
    """
    The player character. Has access to ALL systems.
    Can be owner or owned, predator or prey.
    
    ...but let's be honest about which you'll end up as.
    """
    
    def at_object_creation(self):
        """Called when character is first created."""
        super().at_object_creation()
        
        # Initialize all systems
        initialize_character(self, role="free")
        
        # Vulnerability tracking
        self.db.is_captured = False
        self.db.current_owner = None
        self.db.escape_attempts = 0
        self.db.times_captured = 0
        self.db.times_bred = 0
        self.db.times_broken = 0
        
        # Event tracking
        self.db.events_experienced = []
        self.db.last_event_time = None
        
        # Resistance (starts high... won't stay that way)
        self.db.base_resistance = 80
        self.db.current_resistance = 80
        
    @lazy_property
    def vulnerability(self) -> int:
        """
        How vulnerable is this character to capture/events?
        Higher = more likely to have... things happen.
        """
        base = 20
        
        # Low resistance = more vulnerable
        resistance = self.db.current_resistance or 80
        base += (100 - resistance) // 2
        
        # Previous captures make you easier to catch
        base += self.db.times_captured * 5
        
        # Being broken makes you very vulnerable
        if hasattr(self, 'mental_status'):
            mental = self.mental_status
            if mental.resistance < 30:
                base += 30
        
        # Transformations increase vulnerability
        if hasattr(self, 'transformations'):
            mgr = self.transformations
            for trans in mgr.get_all_active():
                base += trans.progress // 10
        
        # Inflation makes movement harder
        if hasattr(self, 'inflation'):
            tracker = self.inflation
            total = tracker.get_total_volume()
            if total > 500:
                base += 10
            if total > 1000:
                base += 20
        
        return min(95, base)
    
    def can_escape(self, difficulty: int = 50) -> tuple[bool, str]:
        """
        Attempt to escape current situation.
        Returns (success, message).
        """
        # Base chance
        escape_chance = 100 - self.vulnerability
        escape_chance -= difficulty
        
        # Exhaustion penalty
        if hasattr(self, 'character_state'):
            state = self.character_state
            if state.physical.stamina < 30:
                escape_chance -= 20
        
        # Bondage makes escape harder
        if hasattr(self, 'active_bondage'):
            bondage = self.active_bondage
            if bondage:
                escape_chance -= 30
        
        roll = random.randint(1, 100)
        
        if roll <= escape_chance:
            self.db.escape_attempts += 1
            return True, "You manage to break free!"
        else:
            self.db.escape_attempts += 1
            # Failed escapes have consequences
            self.db.current_resistance = max(0, self.db.current_resistance - 5)
            return False, "Your escape attempt fails. You feel your will weakening..."
    
    def get_captured(self, captor=None, reason: str = ""):
        """Handle being captured."""
        self.db.is_captured = True
        self.db.times_captured += 1
        self.db.current_owner = captor.dbref if captor else None
        
        # Resistance drops with each capture
        self.db.current_resistance = max(0, self.db.current_resistance - 10)
        
        msg = f"You have been captured"
        if captor:
            msg += f" by {captor.key}"
        if reason:
            msg += f" ({reason})"
        msg += "!"
        
        self.msg(msg)
        
        # Trigger capture event
        SystemHooks.trigger(SystemEvent.SOLD.value, character=self, new_owner=captor)
    
    def process_tick(self, hours: float = 1.0) -> List[str]:
        """Process a time tick for this character."""
        messages = process_time_tick(self, hours)
        
        # Check for random events based on location
        if self.location and hasattr(self.location, 'roll_for_event'):
            event = self.location.roll_for_event(self)
            if event:
                event_msg, _ = trigger_event(event.event_id, self)
                messages.append(event_msg)
                self.db.events_experienced.append(event.event_id)
        
        return messages


# =============================================================================
# NPC CHARACTER
# =============================================================================

class PetSystemsNPC(PetSystemsDominantMixin, DefaultCharacter):
    """
    An NPC in the world. Usually a predator.
    Has AI behavior and will act autonomously.
    """
    
    def at_object_creation(self):
        """Called when NPC is first created."""
        super().at_object_creation()
        
        # NPC template reference
        self.db.template_id = None
        self.db.npc_role = None
        self.db.disposition = "professional"
        
        # AI state
        self.db.current_target = None
        self.db.current_action = None
        self.db.action_cooldown = 0
        
        # Behavior weights
        self.db.aggression = 50
        self.db.lust = 50
        self.db.cruelty = 50
        
        # Owned characters
        self.db.owned_slaves = []
        self.db.current_breeding_target = None
        
    @classmethod
    def create_from_template(cls, template: NPCTemplate, location=None):
        """Create an NPC from a template."""
        npc = cls.create(template.name, location=location)
        
        npc.db.template_id = template.template_id
        npc.db.npc_role = template.role.value
        npc.db.disposition = template.disposition.value
        
        # Copy stats
        npc.db.aggression = template.stats.cruelty
        npc.db.lust = template.stats.libido
        npc.db.cruelty = template.stats.cruelty
        
        # Store template data
        npc.db.greets_with = template.greets_with
        npc.db.punishes_with = template.punishes_with
        npc.db.preferred_methods = template.preferred_methods
        
        # Set description
        npc.db.desc = template.description
        
        return npc
    
    def get_template(self) -> Optional[NPCTemplate]:
        """Get the template this NPC was created from."""
        if self.db.template_id:
            return ALL_NPC_TEMPLATES.get(self.db.template_id)
        return None
    
    def greet(self, target) -> str:
        """Generate a greeting for a target."""
        template = self.get_template()
        if template:
            return template.generate_greeting(target.key)
        return f"{self.key} looks at {target.key}."
    
    def decide_action(self, targets: List) -> Optional[tuple]:
        """
        AI decision making. What does this NPC want to do?
        Returns (action, target) or None.
        """
        if self.db.action_cooldown > 0:
            self.db.action_cooldown -= 1
            return None
        
        if not targets:
            return None
        
        # Filter for valid targets (not other NPCs, not already owned by us)
        valid_targets = [
            t for t in targets 
            if isinstance(t, PetSystemsCharacter) 
            and t.dbref not in (self.db.owned_slaves or [])
        ]
        
        if not valid_targets:
            return None
        
        # Pick most vulnerable target
        target = max(valid_targets, key=lambda t: t.vulnerability)
        
        # Decide action based on disposition and stats
        disposition = self.db.disposition
        roll = random.randint(1, 100)
        
        if disposition == "sadistic":
            if roll < self.db.cruelty:
                return ("punish", target)
            elif roll < self.db.cruelty + self.db.lust:
                return ("use", target)
            else:
                return ("intimidate", target)
                
        elif disposition == "perverted":
            if roll < self.db.lust:
                return ("breed", target)
            elif roll < self.db.lust + 20:
                return ("use", target)
            else:
                return ("capture", target)
                
        elif disposition == "strict":
            if roll < 40:
                return ("inspect", target)
            elif roll < 70:
                return ("discipline", target)
            else:
                return ("assign_task", target)
                
        elif disposition == "cruel":
            if roll < self.db.cruelty:
                return ("punish", target)
            else:
                return ("use", target)
                
        elif disposition == "caring":
            if roll < 60:
                return ("comfort", target)
            else:
                return ("gentle_use", target)
        
        # Default: capture or use
        if roll < 50:
            return ("capture", target)
        else:
            return ("use", target)
    
    def execute_action(self, action: str, target) -> str:
        """Execute an action on a target."""
        self.db.action_cooldown = random.randint(2, 5)
        
        messages = []
        
        if action == "capture":
            if not target.db.is_captured:
                # Roll against target vulnerability
                if random.randint(1, 100) <= target.vulnerability:
                    target.get_captured(self, "overpowered")
                    messages.append(f"{self.key} captures {target.key}!")
                    self.db.owned_slaves = self.db.owned_slaves or []
                    self.db.owned_slaves.append(target.dbref)
                else:
                    messages.append(f"{self.key} tries to capture {target.key} but fails.")
                    
        elif action == "use":
            # Sexual use
            cum_amount = random.randint(30, 100)
            if hasattr(target, 'inflation'):
                tracker = target.inflation
                location = random.choice(["womb", "anal", "stomach"])
                msg = tracker.inflate(location, "cum", cum_amount)
                target.db.inflation = tracker.to_dict()
                messages.append(f"{self.key} uses {target.key}. {msg}")
            
            # Arousal
            if hasattr(target, 'character_state'):
                state = target.character_state
                state.sexual.increase_arousal(random.randint(20, 40))
                target.character_state = state
                
        elif action == "breed":
            # Breeding use - larger deposits
            cum_amount = random.randint(100, 300)
            if hasattr(target, 'inflation'):
                tracker = target.inflation
                msg = tracker.inflate("womb", "cum", cum_amount)
                target.db.inflation = tracker.to_dict()
                messages.append(f"{self.key} breeds {target.key}! {msg}")
                target.db.times_bred = (target.db.times_bred or 0) + 1
                
        elif action == "punish":
            # Punishment
            method = random.choice(self.db.punishes_with or ["discipline"])
            messages.append(f"{self.key} punishes {target.key} with {method}.")
            
            # Reduce resistance
            target.db.current_resistance = max(0, target.db.current_resistance - 5)
            
            # Humiliation
            if hasattr(target, 'character_state'):
                state = target.character_state
                state.mental.humiliation = min(100, state.mental.humiliation + 20)
                target.character_state = state
                
        elif action == "intimidate":
            messages.append(f"{self.key} looms menacingly over {target.key}.")
            target.db.current_resistance = max(0, target.db.current_resistance - 3)
            
        elif action == "inspect":
            messages.append(f"{self.key} thoroughly inspects {target.key}.")
            # Humiliating inspection
            if hasattr(target, 'character_state'):
                state = target.character_state
                state.mental.humiliation = min(100, state.mental.humiliation + 15)
                target.character_state = state
                
        elif action == "discipline":
            messages.append(f"{self.key} disciplines {target.key} strictly.")
            target.db.current_resistance = max(0, target.db.current_resistance - 5)
            
        elif action == "comfort":
            messages.append(f"{self.key} offers {target.key} gentle comfort.")
            # Comfort is insidious - it builds dependency
            if hasattr(target, 'character_state'):
                state = target.character_state
                state.sexual.increase_arousal(10)
                target.character_state = state
                
        elif action == "gentle_use":
            cum_amount = random.randint(20, 50)
            if hasattr(target, 'inflation'):
                tracker = target.inflation
                msg = tracker.inflate("womb", "cum", cum_amount)
                target.db.inflation = tracker.to_dict()
                messages.append(f"{self.key} gently uses {target.key}. {msg}")
                
        return "\n".join(messages)
    
    def process_tick(self, hours: float = 1.0):
        """Process NPC AI tick."""
        # Find targets in location
        if self.location:
            targets = [
                obj for obj in self.location.contents 
                if obj != self and isinstance(obj, PetSystemsCharacter)
            ]
            
            decision = self.decide_action(targets)
            if decision:
                action, target = decision
                result = self.execute_action(action, target)
                
                # Announce to room
                if result:
                    self.location.msg_contents(result)


# =============================================================================
# ROOM
# =============================================================================

class PetSystemsRoom(DefaultRoom):
    """
    A room in the world. Can have ambient effects and trigger events.
    """
    
    def at_object_creation(self):
        """Called when room is first created."""
        super().at_object_creation()
        
        # Location template reference
        self.db.template_id = None
        self.db.location_type = None
        
        # Ambient effects
        self.db.ambient_arousal = 0
        self.db.ambient_humiliation = 0
        self.db.ambient_corruption = 0
        
        # Danger
        self.db.danger_level = "moderate"
        self.db.escape_difficulty = 50
        
        # Event settings
        self.db.event_chance = 0.2  # 20% chance per tick
        self.db.possible_events = []
        
        # NPCs that spawn here
        self.db.spawns_npcs = []
        self.db.max_npcs = 3
        self.db.current_npcs = []
        
        # Special features
        self.db.has_restraints = False
        self.db.has_milking_equipment = False
        self.db.has_breeding_equipment = False
        
    @classmethod
    def create_from_template(cls, template: LocationTemplate):
        """Create a room from a template."""
        room = cls.create(template.name)
        
        room.db.template_id = template.template_id
        room.db.location_type = template.location_type.value
        room.db.desc = template.get_entry_description()
        
        # Copy properties
        room.db.ambient_arousal = template.ambient_arousal
        room.db.ambient_humiliation = template.ambient_humiliation
        room.db.ambient_corruption = template.ambient_corruption
        room.db.danger_level = template.danger_level.value
        room.db.escape_difficulty = template.escape_difficulty
        room.db.has_restraints = template.has_restraints
        room.db.has_milking_equipment = template.has_milking_equipment
        room.db.has_breeding_equipment = template.has_breeding_equipment
        room.db.possible_events = template.possible_events
        room.db.spawns_npcs = template.typical_npcs
        
        # Set event chance based on danger
        danger_chances = {
            "safe": 0.05,
            "low": 0.1,
            "moderate": 0.2,
            "high": 0.35,
            "extreme": 0.5,
        }
        room.db.event_chance = danger_chances.get(template.danger_level.value, 0.2)
        
        return room
    
    def at_object_receive(self, moved_obj, source_location, **kwargs):
        """Called when an object enters this room."""
        super().at_object_receive(moved_obj, source_location, **kwargs)
        
        if isinstance(moved_obj, PetSystemsCharacter):
            # Apply ambient effects
            self._apply_ambient_effects(moved_obj)
            
            # Announce entry with flavor
            template_id = self.db.template_id
            if template_id:
                template = ALL_LOCATION_TEMPLATES.get(template_id)
                if template and template.atmosphere:
                    moved_obj.msg(template.atmosphere)
            
            # NPCs react
            for npc in self.get_npcs():
                greeting = npc.greet(moved_obj)
                self.msg_contents(greeting)
            
            # Check for immediate event
            if random.random() < self.db.event_chance:
                self.roll_for_event(moved_obj, immediate=True)
    
    def _apply_ambient_effects(self, character):
        """Apply ambient effects to a character."""
        if hasattr(character, 'character_state'):
            state = character.character_state
            
            if self.db.ambient_arousal:
                state.sexual.increase_arousal(self.db.ambient_arousal // 4)
                
            if self.db.ambient_humiliation:
                state.mental.humiliation = min(100, 
                    state.mental.humiliation + self.db.ambient_humiliation // 4)
                
            character.character_state = state
        
        if self.db.ambient_corruption and hasattr(character, 'transformations'):
            # Ambient corruption can progress any active transformation
            mgr = character.transformations
            for trans_type in list(mgr.transformations.keys()):
                mgr.add_corruption(trans_type, self.db.ambient_corruption // 4, "ambient")
            character.db.transformations = mgr.to_dict()
    
    def get_npcs(self) -> List:
        """Get all NPCs currently in this room."""
        return [obj for obj in self.contents if isinstance(obj, PetSystemsNPC)]
    
    def get_players(self) -> List:
        """Get all player characters in this room."""
        return [obj for obj in self.contents if isinstance(obj, PetSystemsCharacter)]
    
    def roll_for_event(self, character, immediate: bool = False) -> Optional[EventTemplate]:
        """Roll for a random event."""
        # Get character states
        states = []
        if character.db.is_captured:
            states.append("is_slave")
        if hasattr(character, 'hucow_stats') and character.hucow_stats.is_lactating:
            states.append("is_lactating")
        if hasattr(character, 'is_pony') and character.is_pony:
            states.append("is_pony")
        if hasattr(character, 'whore_stats'):
            states.append("is_whore")
        if hasattr(character, 'is_fighter') and character.is_fighter:
            states.append("is_fighter")
        
        # Get event
        event = get_random_event(
            location_type=self.db.location_type,
            character_states=states,
        )
        
        if event:
            # Higher vulnerability = more likely to trigger
            trigger_chance = 50 + character.vulnerability // 2
            
            if immediate or random.randint(1, 100) <= trigger_chance:
                return event
        
        return None
    
    def process_tick(self, hours: float = 1.0):
        """Process room tick - ambient effects and events."""
        players = self.get_players()
        
        for player in players:
            # Apply ambient effects
            self._apply_ambient_effects(player)
            
            # Roll for events
            if random.random() < self.db.event_chance:
                event = self.roll_for_event(player)
                if event:
                    msg, _ = trigger_event(event.event_id, player)
                    player.msg(f"\n{msg}\n")
        
        # NPC AI ticks
        for npc in self.get_npcs():
            npc.process_tick(hours)


# =============================================================================
# EXPORTS
# =============================================================================

__all__ = [
    "PetSystemsCharacter",
    "PetSystemsNPC", 
    "PetSystemsRoom",
]
