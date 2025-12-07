"""
Exit Typeclasses - Movement Between Spaces

This module provides exits that make movement feel meaningful:
- Passage descriptions (what it feels like to traverse)
- Arrival descriptions (what it feels like to arrive)
- Sensory transmission (sound, scent, sight bleeding through)
- Physical restrictions (size, climbing, swimming)
- Door mechanics with linked pairs
- Hidden exits requiring discovery
- Realm gates with magical effects and possible misfires

Movement should never feel like just "you go north." Every transition
between spaces is an experience.

Exit Types:
    Exit        - Base exit with all features
    Door        - Can be opened, closed, locked
    HiddenExit  - Must be discovered before use
    RealmGate   - Magical portal with special effects
    OneWayExit  - Can only be traversed in one direction
    
Sensory Transmission:
    Exits control what sensory information passes between rooms:
    - transmits_sound: Can you hear through this exit?
    - transmits_smell: Do scents pass through?
    - transmits_sight: Can you see into the next room?
    - sound_reduction: How much sound is dampened (0-1)
    - scent_reduction: How much scent is dampened (0-1)
"""

from typing import Optional, List, Dict, Any
from evennia.objects.objects import DefaultExit
from evennia.utils.utils import lazy_property

# Handle early import during Django migration loading
try:
    from evennia.typeclasses.attributes import AttributeProperty
except (ImportError, TypeError, AttributeError):
    def AttributeProperty(default=None, **kwargs):
        return default
import random


# =============================================================================
# SIZE HIERARCHY
# =============================================================================

SIZE_HIERARCHY = {
    "tiny": 1,      # Mouse, insect
    "small": 2,     # Cat, small dog
    "medium": 3,    # Human, wolf
    "large": 4,     # Horse, bear
    "huge": 5,      # Elephant, giant
    "massive": 6,   # Dragon, building-sized
}


# =============================================================================
# PASSAGE TYPE DATA
# =============================================================================

PASSAGE_TYPES = {
    "walk": {
        "verb": "walk",
        "gerund": "walking",
        "default_desc": "You walk through.",
        "requires": None,
    },
    "climb": {
        "verb": "climb",
        "gerund": "climbing",
        "default_desc": "You climb carefully.",
        "requires": "can_climb",
    },
    "crawl": {
        "verb": "crawl",
        "gerund": "crawling",
        "default_desc": "You get down and crawl through.",
        "requires": "can_crawl",
    },
    "swim": {
        "verb": "swim",
        "gerund": "swimming",
        "default_desc": "You swim across.",
        "requires": "can_swim",
    },
    "jump": {
        "verb": "jump",
        "gerund": "jumping",
        "default_desc": "You leap across the gap.",
        "requires": "can_jump",
    },
    "squeeze": {
        "verb": "squeeze",
        "gerund": "squeezing",
        "default_desc": "You squeeze through the tight space.",
        "requires": None,
        "size_mod": -1,  # Reduces effective size for passage
    },
    "slide": {
        "verb": "slide",
        "gerund": "sliding",
        "default_desc": "You slide down.",
        "requires": None,
    },
    "portal": {
        "verb": "step through",
        "gerund": "stepping through",
        "default_desc": "Reality bends as you step through the portal.",
        "requires": None,
    },
}


# =============================================================================
# BASE EXIT
# =============================================================================

class Exit(DefaultExit):
    """
    Enhanced exit with immersive features.
    
    Features:
    - Passage descriptions (traverser sees this)
    - Arrival descriptions (destination room sees this)
    - Departure descriptions (origin room sees this)
    - Sensory transmission (sound/scent/sight)
    - Physical requirements (size, movement type)
    - Traffic descriptions (how busy this passage is)
    - Peek functionality (see into next room)
    """
    
    # -------------------------------------------------------------------------
    # Descriptions
    # -------------------------------------------------------------------------
    
    # What the mover experiences
    passage_desc = AttributeProperty(default="")
    
    # What the destination room sees when someone arrives
    arrival_desc = AttributeProperty(default="")
    
    # What the origin room sees when someone leaves
    departure_desc = AttributeProperty(default="")
    
    # Short description shown in exit list
    short_desc = AttributeProperty(default="")
    
    # -------------------------------------------------------------------------
    # Physical Properties
    # -------------------------------------------------------------------------
    
    # Size restriction (max size that can pass)
    max_size = AttributeProperty(default="massive")
    
    # How you traverse this exit
    passage_type = AttributeProperty(default="walk")
    
    # Is this a one-way exit?
    one_way = AttributeProperty(default=False)
    
    # -------------------------------------------------------------------------
    # Sensory Transmission
    # -------------------------------------------------------------------------
    
    transmits_sound = AttributeProperty(default=True)
    transmits_smell = AttributeProperty(default=True)
    transmits_sight = AttributeProperty(default=True)
    
    # Reduction factors (0 = full transmission, 1 = full block)
    sound_reduction = AttributeProperty(default=0.3)
    scent_reduction = AttributeProperty(default=0.5)
    
    # -------------------------------------------------------------------------
    # Traffic / Visibility
    # -------------------------------------------------------------------------
    
    # How this exit looks/feels
    traffic_level = AttributeProperty(default="normal")  # quiet, normal, busy
    
    # Can you see what's on the other side?
    can_peek = AttributeProperty(default=True)
    peek_distance = AttributeProperty(default="near")  # near, far, none
    
    # -------------------------------------------------------------------------
    # Hooks
    # -------------------------------------------------------------------------
    
    def at_object_creation(self):
        """Called when exit is first created."""
        super().at_object_creation()
    
    # -------------------------------------------------------------------------
    # Traversal Checks
    # -------------------------------------------------------------------------
    
    def can_traverse(self, traverser) -> tuple[bool, str]:
        """
        Check if traverser can use this exit.
        
        Returns:
            Tuple of (can_pass, failure_message)
        """
        # Check size
        if hasattr(traverser, 'size'):
            traverser_size = SIZE_HIERARCHY.get(traverser.size, 3)
            max_size = SIZE_HIERARCHY.get(self.max_size, 6)
            
            # Apply passage type size modifier
            passage_data = PASSAGE_TYPES.get(self.passage_type, {})
            size_mod = passage_data.get("size_mod", 0)
            
            if traverser_size > (max_size + size_mod):
                return (False, f"You are too large to fit through {self.key}.")
        
        # Check passage type requirements
        passage_data = PASSAGE_TYPES.get(self.passage_type, {})
        requires = passage_data.get("requires")
        
        if requires:
            if not hasattr(traverser, requires) or not getattr(traverser, requires):
                verb = passage_data.get("verb", "pass")
                return (False, f"You cannot {verb} through {self.key}.")
        
        return (True, "")
    
    def at_traverse(self, traversing_object, target_location, **kwargs):
        """
        Called when someone tries to traverse this exit.
        """
        # Check if traversal is allowed
        can_pass, fail_msg = self.can_traverse(traversing_object)
        if not can_pass:
            traversing_object.msg(fail_msg)
            return False
        
        # Get passage description
        passage_msg = self.get_passage_message(traversing_object)
        
        # Show passage message to traverser
        if passage_msg:
            traversing_object.msg(passage_msg)
        
        # Show departure message to origin room
        departure_msg = self.get_departure_message(traversing_object)
        if departure_msg and self.location:
            self.location.msg_contents(
                departure_msg,
                exclude=[traversing_object]
            )
        
        # Perform the actual move
        success = traversing_object.move_to(
            target_location,
            quiet=True,  # We handle messages ourselves
            move_type="traverse",
            **kwargs
        )
        
        if success:
            # Show arrival message to destination room
            arrival_msg = self.get_arrival_message(traversing_object)
            if arrival_msg and target_location:
                target_location.msg_contents(
                    arrival_msg,
                    exclude=[traversing_object]
                )
        
        return success
    
    # -------------------------------------------------------------------------
    # Message Generation
    # -------------------------------------------------------------------------
    
    def get_passage_message(self, traverser) -> str:
        """Get the message shown to the traverser."""
        if self.passage_desc:
            return self.passage_desc
        
        passage_data = PASSAGE_TYPES.get(self.passage_type, {})
        return passage_data.get("default_desc", "You pass through.")
    
    def get_departure_message(self, traverser) -> str:
        """Get the message shown to the origin room."""
        if self.departure_desc:
            return self.departure_desc.format(name=traverser.key)
        
        passage_data = PASSAGE_TYPES.get(self.passage_type, {})
        verb = passage_data.get("verb", "goes")
        
        return f"{traverser.key} {verb}s {self.key}."
    
    def get_arrival_message(self, traverser) -> str:
        """Get the message shown to the destination room."""
        if self.arrival_desc:
            return self.arrival_desc.format(name=traverser.key)
        
        # Find the reverse exit name if it exists
        reverse_name = "somewhere"
        if self.destination:
            for exit in self.destination.exits:
                if exit.destination == self.location:
                    reverse_name = exit.key
                    break
        
        return f"{traverser.key} arrives from {reverse_name}."
    
    # -------------------------------------------------------------------------
    # Peek Functionality
    # -------------------------------------------------------------------------
    
    def peek_through(self, looker) -> str:
        """
        Look through this exit to see the other side.
        
        Returns description of what can be seen.
        """
        if not self.can_peek or not self.transmits_sight:
            return "You can't see what's on the other side."
        
        if not self.destination:
            return "This exit leads nowhere you can see."
        
        dest = self.destination
        
        # Basic peek - just the room name
        if self.peek_distance == "far":
            return f"Through {self.key}, you can make out: {dest.key}"
        
        # Near peek - room name + brief description
        parts = [f"Through {self.key}, you see:"]
        parts.append(f"|c{dest.key}|n")
        
        # Add a glimpse of the room description
        if hasattr(dest, 'db') and dest.db.desc:
            # First sentence only
            desc = dest.db.desc.split('.')[0]
            if len(desc) > 100:
                desc = desc[:100] + "..."
            parts.append(desc)
        
        # Show who's visible there
        visible_chars = []
        for obj in dest.contents:
            if hasattr(obj, 'account') and obj.account:
                visible_chars.append(obj.key)
            elif hasattr(obj, 'is_npc') and obj.is_npc:
                visible_chars.append(obj.key)
        
        if visible_chars:
            parts.append(f"You can see: {', '.join(visible_chars)}")
        
        return "\n".join(parts)
    
    # -------------------------------------------------------------------------
    # Display
    # -------------------------------------------------------------------------
    
    def get_display_name(self, looker=None, **kwargs):
        """Return the display name, possibly with traffic indicator."""
        name = self.key
        
        # Add traffic indicator if notable
        if self.traffic_level == "busy":
            name = f"{name} |x(busy)|n"
        elif self.traffic_level == "quiet":
            name = f"{name} |x(quiet)|n"
        
        return name
    
    def return_appearance(self, looker=None, **kwargs):
        """What you see when you look at the exit."""
        parts = []
        
        # Exit name
        parts.append(f"|w{self.key}|n")
        
        # Short description if any
        if self.short_desc:
            parts.append(self.short_desc)
        
        # Passage type hint if not walk
        if self.passage_type != "walk":
            passage_data = PASSAGE_TYPES.get(self.passage_type, {})
            gerund = passage_data.get("gerund", "passing")
            parts.append(f"|x(requires {gerund})|n")
        
        # Size restriction if notable
        if self.max_size not in ("massive", "huge"):
            parts.append(f"|x(max size: {self.max_size})|n")
        
        # What you can see through
        if self.can_peek and self.transmits_sight and self.destination:
            parts.append("")
            parts.append(self.peek_through(looker))
        
        return "\n".join(parts)


# =============================================================================
# DOOR
# =============================================================================

class Door(Exit):
    """
    An exit that can be opened, closed, and locked.
    
    Doors can be linked to sync state (opening one opens both).
    """
    
    # -------------------------------------------------------------------------
    # Door State
    # -------------------------------------------------------------------------
    
    is_open = AttributeProperty(default=True)
    is_locked = AttributeProperty(default=False)
    
    # -------------------------------------------------------------------------
    # Lock Properties
    # -------------------------------------------------------------------------
    
    key_id = AttributeProperty(default="")  # What key opens this
    lock_difficulty = AttributeProperty(default=0)  # For lockpicking
    
    # -------------------------------------------------------------------------
    # Linked Door
    # -------------------------------------------------------------------------
    
    # Reference to the door on the other side (for syncing state)
    linked_exit_id = AttributeProperty(default=None)
    
    # -------------------------------------------------------------------------
    # Auto-close
    # -------------------------------------------------------------------------
    
    auto_close = AttributeProperty(default=False)
    auto_close_delay = AttributeProperty(default=60)  # Seconds
    
    # -------------------------------------------------------------------------
    # Sound Properties (change based on state)
    # -------------------------------------------------------------------------
    
    open_sound = AttributeProperty(default="The door creaks open.")
    close_sound = AttributeProperty(default="The door clicks shut.")
    lock_sound = AttributeProperty(default="The lock clicks into place.")
    unlock_sound = AttributeProperty(default="The lock clicks open.")
    
    # -------------------------------------------------------------------------
    # Traversal Override
    # -------------------------------------------------------------------------
    
    def can_traverse(self, traverser) -> tuple[bool, str]:
        """Check if door can be traversed."""
        # First check parent requirements
        can_pass, msg = super().can_traverse(traverser)
        if not can_pass:
            return (can_pass, msg)
        
        # Check if door is open
        if not self.is_open:
            return (False, f"The {self.key} is closed.")
        
        return (True, "")
    
    # -------------------------------------------------------------------------
    # Sensory Transmission Override
    # -------------------------------------------------------------------------
    
    @property
    def effective_transmits_sound(self) -> bool:
        """Sound transmission depends on door state."""
        if self.is_open:
            return True
        return self.transmits_sound  # Closed door's base transmission
    
    @property
    def effective_transmits_sight(self) -> bool:
        """Sight transmission depends on door state."""
        return self.is_open
    
    @property
    def effective_sound_reduction(self) -> float:
        """Closed doors reduce more sound."""
        if self.is_open:
            return 0.1
        return self.sound_reduction
    
    # -------------------------------------------------------------------------
    # Door Operations
    # -------------------------------------------------------------------------
    
    def _get_linked_exit(self):
        """Get the linked door object."""
        if self.linked_exit_id:
            from evennia import search_object
            results = search_object(
                searchdata=f"#{self.linked_exit_id}",
                typeclass=Door
            )
            if results:
                return results[0]
        return None
    
    def open_door(self, opener=None, sync=True) -> tuple[bool, str]:
        """
        Open the door.
        
        Args:
            opener: Who is opening the door
            sync: Whether to sync with linked door
            
        Returns:
            Tuple of (success, message)
        """
        if self.is_open:
            return (False, f"The {self.key} is already open.")
        
        if self.is_locked:
            return (False, f"The {self.key} is locked.")
        
        self.is_open = True
        
        # Update sensory transmission
        self.transmits_sight = True
        
        # Sync linked door
        if sync:
            linked = self._get_linked_exit()
            if linked:
                linked.open_door(opener, sync=False)
        
        # Announce
        msg = self.open_sound or f"The {self.key} opens."
        if self.location:
            self.location.msg_contents(msg)
        if self.destination:
            linked = self._get_linked_exit()
            if linked:
                self.destination.msg_contents(f"The {linked.key} opens from the other side.")
        
        return (True, msg)
    
    def close_door(self, closer=None, sync=True) -> tuple[bool, str]:
        """Close the door."""
        if not self.is_open:
            return (False, f"The {self.key} is already closed.")
        
        self.is_open = False
        
        # Update sensory transmission
        self.transmits_sight = False
        
        # Sync linked door
        if sync:
            linked = self._get_linked_exit()
            if linked:
                linked.close_door(closer, sync=False)
        
        # Announce
        msg = self.close_sound or f"The {self.key} closes."
        if self.location:
            self.location.msg_contents(msg)
        if self.destination:
            linked = self._get_linked_exit()
            if linked:
                self.destination.msg_contents(f"The {linked.key} closes from the other side.")
        
        return (True, msg)
    
    def lock_door(self, locker=None, sync=True) -> tuple[bool, str]:
        """Lock the door."""
        if self.is_locked:
            return (False, f"The {self.key} is already locked.")
        
        if self.is_open:
            return (False, f"You need to close the {self.key} first.")
        
        self.is_locked = True
        
        # Sync linked door
        if sync:
            linked = self._get_linked_exit()
            if linked:
                linked.lock_door(locker, sync=False)
        
        msg = self.lock_sound or f"You lock the {self.key}."
        return (True, msg)
    
    def unlock_door(self, unlocker=None, key=None, sync=True) -> tuple[bool, str]:
        """Unlock the door."""
        if not self.is_locked:
            return (False, f"The {self.key} is not locked.")
        
        # Check for correct key
        if self.key_id:
            if not key:
                return (False, f"The {self.key} requires a key.")
            
            key_match = False
            if hasattr(key, 'key_id') and key.key_id == self.key_id:
                key_match = True
            elif hasattr(key, 'db') and key.db.key_id == self.key_id:
                key_match = True
            
            if not key_match:
                return (False, "That key doesn't fit this lock.")
        
        self.is_locked = False
        
        # Sync linked door
        if sync:
            linked = self._get_linked_exit()
            if linked:
                linked.unlock_door(unlocker, key, sync=False)
        
        msg = self.unlock_sound or f"You unlock the {self.key}."
        return (True, msg)
    
    # -------------------------------------------------------------------------
    # Display Override
    # -------------------------------------------------------------------------
    
    def return_appearance(self, looker=None, **kwargs):
        """Show door state in appearance."""
        parts = []
        
        # Door name with state
        state = "open" if self.is_open else "closed"
        if self.is_locked:
            state = "locked"
        parts.append(f"|w{self.key}|n ({state})")
        
        # Short description
        if self.short_desc:
            parts.append(self.short_desc)
        
        # What you can see through (if open)
        if self.is_open and self.can_peek and self.destination:
            parts.append("")
            parts.append(self.peek_through(looker))
        
        return "\n".join(parts)
    
    def get_display_name(self, looker=None, **kwargs):
        """Show state in exit list."""
        state_indicator = ""
        if not self.is_open:
            state_indicator = " |x(closed)|n"
        if self.is_locked:
            state_indicator = " |r(locked)|n"
        
        return f"{self.key}{state_indicator}"


# =============================================================================
# HIDDEN EXIT
# =============================================================================

class HiddenExit(Exit):
    """
    An exit that must be discovered before it can be used.
    
    Hidden exits don't appear in the exit list until discovered.
    Discovery can happen through:
    - Searching the room
    - Having specific knowledge/items
    - Being told by another player
    - Triggering an event
    """
    
    # -------------------------------------------------------------------------
    # Hidden State
    # -------------------------------------------------------------------------
    
    is_hidden = AttributeProperty(default=True)
    
    # Who has discovered this exit (list of character IDs)
    discovered_by = AttributeProperty(default=list)
    
    # -------------------------------------------------------------------------
    # Discovery Requirements
    # -------------------------------------------------------------------------
    
    discovery_dc = AttributeProperty(default=15)  # Difficulty to find
    discovery_skill = AttributeProperty(default="perception")  # What skill to use
    discovery_hint = AttributeProperty(default="")  # Hint text shown on search
    
    # Auto-reveal conditions
    reveal_on_key = AttributeProperty(default="")  # Reveal if player has this key_id
    reveal_on_knowledge = AttributeProperty(default="")  # Reveal if player knows this
    
    # -------------------------------------------------------------------------
    # Descriptions
    # -------------------------------------------------------------------------
    
    hidden_desc = AttributeProperty(default="")  # What you see when searching
    revealed_desc = AttributeProperty(default="")  # Description once found
    
    # -------------------------------------------------------------------------
    # Discovery Methods
    # -------------------------------------------------------------------------
    
    def is_discovered_by(self, character) -> bool:
        """Check if character has discovered this exit."""
        if not self.is_hidden:
            return True
        
        # Check discovered list
        if character.id in self.discovered_by:
            return True
        
        # Check auto-reveal conditions
        if self.reveal_on_key:
            if self._character_has_key(character, self.reveal_on_key):
                return True
        
        if self.reveal_on_knowledge:
            if self._character_has_knowledge(character, self.reveal_on_knowledge):
                return True
        
        return False
    
    def _character_has_key(self, character, key_id: str) -> bool:
        """Check if character has a key with given ID."""
        for obj in character.contents:
            if hasattr(obj, 'key_id') and obj.key_id == key_id:
                return True
            if hasattr(obj, 'db') and obj.db.key_id == key_id:
                return True
        return False
    
    def _character_has_knowledge(self, character, knowledge: str) -> bool:
        """Check if character has specific knowledge."""
        if hasattr(character, 'knowledge'):
            return knowledge in character.knowledge
        if hasattr(character, 'db') and character.db.knowledge:
            return knowledge in character.db.knowledge
        return False
    
    def reveal_to(self, character, announce=True) -> bool:
        """
        Reveal this exit to a character.
        
        Args:
            character: The character to reveal to
            announce: Whether to announce the discovery
            
        Returns:
            True if newly revealed, False if already known
        """
        if character.id in self.discovered_by:
            return False
        
        # Add to discovered list
        discovered = list(self.discovered_by)
        discovered.append(character.id)
        self.discovered_by = discovered
        
        if announce:
            msg = self.revealed_desc or f"You discover a hidden passage: {self.key}!"
            character.msg(msg)
        
        return True
    
    # -------------------------------------------------------------------------
    # Traversal Override
    # -------------------------------------------------------------------------
    
    def can_traverse(self, traverser) -> tuple[bool, str]:
        """Must be discovered to traverse."""
        if self.is_hidden and not self.is_discovered_by(traverser):
            # Don't even acknowledge the exit exists
            return (False, "You can't go that way.")
        
        return super().can_traverse(traverser)
    
    # -------------------------------------------------------------------------
    # Display Override
    # -------------------------------------------------------------------------
    
    def get_display_name(self, looker=None, **kwargs):
        """Only show if discovered."""
        if self.is_hidden and looker and not self.is_discovered_by(looker):
            return None  # Don't show at all
        
        return super().get_display_name(looker, **kwargs)


# =============================================================================
# REALM GATE
# =============================================================================

class RealmGate(Exit):
    """
    Magical portal between realms.
    
    Realm gates have special properties:
    - Visual effects on traversal
    - Possible malfunctions (wrong destination)
    - May require payment or attunement
    - Can be redirected by others
    """
    
    # -------------------------------------------------------------------------
    # Gate Properties
    # -------------------------------------------------------------------------
    
    destination_realm = AttributeProperty(default="")
    gate_name = AttributeProperty(default="")
    
    # -------------------------------------------------------------------------
    # Visual Effects
    # -------------------------------------------------------------------------
    
    gate_color = AttributeProperty(default="shimmering blue")
    gate_effect = AttributeProperty(default="The portal ripples as you approach.")
    traversal_effect = AttributeProperty(default="Reality twists around you as you step through...")
    
    # -------------------------------------------------------------------------
    # Malfunction Properties
    # -------------------------------------------------------------------------
    
    malfunction_chance = AttributeProperty(default=0.0)  # 0-1
    accident_destinations = AttributeProperty(default=list)  # List of room IDs
    
    # -------------------------------------------------------------------------
    # Requirements
    # -------------------------------------------------------------------------
    
    requires_payment = AttributeProperty(default=False)
    payment_amount = AttributeProperty(default=0)
    requires_attunement = AttributeProperty(default=False)
    attuned_players = AttributeProperty(default=list)
    
    # -------------------------------------------------------------------------
    # Redirect System
    # -------------------------------------------------------------------------
    
    # Someone can redirect this gate temporarily
    redirect_target = AttributeProperty(default=None)  # Room ID
    redirect_by = AttributeProperty(default="")  # Who set the redirect
    redirect_remaining = AttributeProperty(default=0)  # Uses remaining
    
    # -------------------------------------------------------------------------
    # Gate Methods
    # -------------------------------------------------------------------------
    
    def get_actual_destination(self, traverser):
        """
        Determine where the gate actually sends you.
        
        Considers: malfunction, redirect, normal destination
        """
        # Check for redirect first
        if self.redirect_target and self.redirect_remaining > 0:
            self.redirect_remaining -= 1
            from evennia import search_object
            results = search_object(f"#{self.redirect_target}")
            if results:
                return results[0]
        
        # Check for malfunction
        if self.malfunction_chance > 0 and self.accident_destinations:
            if random.random() < self.malfunction_chance:
                dest_id = random.choice(self.accident_destinations)
                from evennia import search_object
                results = search_object(f"#{dest_id}")
                if results:
                    return results[0]
        
        # Normal destination
        return self.destination
    
    def set_redirect(self, target_room, setter, uses: int = 1) -> bool:
        """
        Set a temporary redirect for this gate.
        
        Args:
            target_room: Where to redirect to
            setter: Who is setting the redirect
            uses: How many times the redirect applies
            
        Returns:
            True if redirect was set
        """
        self.redirect_target = target_room.id if hasattr(target_room, 'id') else target_room
        self.redirect_by = setter.key if hasattr(setter, 'key') else str(setter)
        self.redirect_remaining = uses
        return True
    
    def clear_redirect(self) -> None:
        """Clear any active redirect."""
        self.redirect_target = None
        self.redirect_by = ""
        self.redirect_remaining = 0
    
    # -------------------------------------------------------------------------
    # Traversal Override
    # -------------------------------------------------------------------------
    
    def can_traverse(self, traverser) -> tuple[bool, str]:
        """Check gate-specific requirements."""
        can_pass, msg = super().can_traverse(traverser)
        if not can_pass:
            return (can_pass, msg)
        
        # Check attunement
        if self.requires_attunement:
            if traverser.id not in self.attuned_players:
                return (False, "This gate does not respond to you. You must be attuned first.")
        
        # Check payment (would integrate with economy system)
        if self.requires_payment:
            # Placeholder - would check if player has funds
            pass
        
        return (True, "")
    
    def at_traverse(self, traversing_object, target_location, **kwargs):
        """Handle gate traversal with effects."""
        # Check if traversal is allowed
        can_pass, fail_msg = self.can_traverse(traversing_object)
        if not can_pass:
            traversing_object.msg(fail_msg)
            return False
        
        # Get actual destination (may differ from target_location)
        actual_dest = self.get_actual_destination(traversing_object)
        
        # Show gate effect
        if self.gate_effect:
            traversing_object.msg(self.gate_effect)
        
        # Show traversal effect
        if self.traversal_effect:
            traversing_object.msg(self.traversal_effect)
        
        # Departure message
        if self.location:
            self.location.msg_contents(
                f"{traversing_object.key} steps into the {self.gate_name or 'portal'} and vanishes.",
                exclude=[traversing_object]
            )
        
        # Perform the move
        success = traversing_object.move_to(
            actual_dest,
            quiet=True,
            move_type="portal",
            **kwargs
        )
        
        if success:
            # Arrival message
            if actual_dest:
                actual_dest.msg_contents(
                    f"{traversing_object.key} materializes from a shimmer of light.",
                    exclude=[traversing_object]
                )
            
            # Notify if destination was different (malfunction)
            if actual_dest != target_location:
                traversing_object.msg("|rThe portal malfunctions! You arrive somewhere unexpected...|n")
        
        return success
    
    # -------------------------------------------------------------------------
    # Display Override
    # -------------------------------------------------------------------------
    
    def return_appearance(self, looker=None, **kwargs):
        """Show gate details."""
        parts = []
        
        # Gate name with color
        name = self.gate_name or self.key
        parts.append(f"|w{name}|n - A {self.gate_color} portal")
        
        # Destination realm
        if self.destination_realm:
            parts.append(f"Leads to: |c{self.destination_realm}|n")
        
        # Requirements
        if self.requires_attunement:
            if looker and looker.id in self.attuned_players:
                parts.append("|gYou are attuned to this gate.|n")
            else:
                parts.append("|yRequires attunement.|n")
        
        if self.requires_payment:
            parts.append(f"|yRequires payment: {self.payment_amount} marks|n")
        
        # Warning if known malfunction chance
        if self.malfunction_chance > 0.1:
            parts.append("|rThis gate is unstable. Travel at your own risk.|n")
        
        return "\n".join(parts)


# =============================================================================
# ONE WAY EXIT
# =============================================================================

class OneWayExit(Exit):
    """
    An exit that can only be traversed in one direction.
    
    Useful for:
    - Drops/falls
    - Slides
    - One-way doors
    - Portals without return
    """
    
    one_way = AttributeProperty(default=True)
    
    # Warning shown before traversal
    one_way_warning = AttributeProperty(default="")
    
    def at_traverse(self, traversing_object, target_location, **kwargs):
        """Warn about one-way nature."""
        # Show warning if set
        if self.one_way_warning:
            traversing_object.msg(self.one_way_warning)
        
        return super().at_traverse(traversing_object, target_location, **kwargs)


# =============================================================================
# EXPORTS
# =============================================================================

__all__ = [
    # Data
    "SIZE_HIERARCHY",
    "PASSAGE_TYPES",
    
    # Exit Types
    "Exit",
    "Door",
    "HiddenExit",
    "RealmGate",
    "OneWayExit",
]
