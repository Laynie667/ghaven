"""
Sexual State Tick Script
========================

Handles time-based changes to sexual state:
- Arousal decay when not stimulated
- Automatic rhythm thrusting
- Stamina recovery
- Post-orgasm refractory period
- Position fatigue

Runs periodically (configurable, default 5 seconds game time).
"""

from datetime import datetime, timedelta
from random import choice, random

# Evennia imports - only used when script is loaded in runtime
try:
    from evennia import DefaultScript, search_object
    from evennia.utils import logger
    # Check if actually usable
    if DefaultScript is None:
        raise ImportError("Evennia not configured")
    HAS_EVENNIA = True
except (ImportError, Exception):
    HAS_EVENNIA = False
    # Stubs for testing without Evennia
    class DefaultScript:
        def at_script_creation(self):
            pass
        def at_repeat(self):
            pass
    def search_object(*args, **kwargs):
        return []
    class logger:
        @staticmethod
        def log_err(*args):
            pass


# Configuration
TICK_INTERVAL = 5  # seconds between ticks (faster for rhythm)
AROUSAL_DECAY_RATE = 0.01  # per tick when not active
AROUSAL_DECAY_ACTIVE = 0.002  # per tick when in position
REFRACTORY_DURATION = 30  # seconds of refractory period


class SexualStateTickScript(DefaultScript):
    """
    Global script that ticks sexual state for all characters.
    
    Handles:
    - Arousal decay
    - Automatic rhythm thrusting
    - Refractory period countdown
    """
    
    def at_script_creation(self):
        """Set up the tick script."""
        self.key = "sexual_state_ticker"
        self.desc = "Manages arousal and rhythm"
        self.interval = TICK_INTERVAL
        self.persistent = True
        
        # Track state
        self.db.active_chars = set()  # chars with arousal or rhythm
        self.db.refractory_until = {}  # char id -> datetime when refractory ends
        self.db.rhythm_counters = {}  # char id -> seconds until next auto-thrust
    
    def at_repeat(self):
        """Called every tick interval."""
        self.tick_rhythms()
        self.tick_arousal()
        self.tick_refractory()
    
    def tick_rhythms(self):
        """Handle automatic rhythm thrusting."""
        if not self.db.rhythm_counters:
            self.db.rhythm_counters = {}
        
        to_remove = []
        
        for char_id, counter in list(self.db.rhythm_counters.items()):
            char = self.get_character(char_id)
            if not char:
                to_remove.append(char_id)
                continue
            
            # Get rhythm settings
            rhythm = None
            if hasattr(char, "db"):
                rhythm = getattr(char.db, "rhythm", None)
            else:
                rhythm = getattr(char, "rhythm", None)
            
            if not rhythm:
                to_remove.append(char_id)
                continue
            
            # Decrement counter
            new_counter = counter - TICK_INTERVAL
            
            if new_counter <= 0:
                # Time for an auto-thrust!
                self.execute_auto_thrust(char, rhythm)
                # Reset counter
                self.db.rhythm_counters[char_id] = rhythm.get("interval", 5)
            else:
                self.db.rhythm_counters[char_id] = new_counter
        
        for char_id in to_remove:
            del self.db.rhythm_counters[char_id]
    
    def execute_auto_thrust(self, char, rhythm):
        """Execute an automatic thrust for a character with active rhythm."""
        location = getattr(char, "location", None)
        if not location:
            return
        
        # Get position manager
        manager = getattr(location, "_position_manager", None)
        if not manager:
            return
        
        active = manager.get_position_for(char)
        if not active:
            # No longer in position, clear rhythm
            if hasattr(char, "db"):
                char.db.rhythm = None
            else:
                char.rhythm = None
            return
        
        if not active.can_participant_thrust(char):
            return
        
        # Find partner
        partner = None
        for slot_key, occupant in active.occupants.items():
            if occupant.character != char:
                partner = occupant.character
                break
        
        if not partner:
            return
        
        # Calculate arousal changes
        intensity = rhythm.get("intensity", 0.5)
        actor_gain = 0.06 + (intensity * 0.1)
        target_gain = 0.05 + (intensity * 0.08)
        
        # Randomize
        actor_gain *= (0.8 + random() * 0.4)
        target_gain *= (0.8 + random() * 0.4)
        
        # Apply arousal
        new_actor = self.modify_arousal(char, actor_gain)
        new_target = self.modify_arousal(partner, target_gain)
        
        # Build message (occasionally, not every thrust)
        if random() < 0.3:  # 30% chance of message
            self.send_rhythm_message(char, partner, intensity, location)
        
        # Check for orgasm
        self.check_orgasm(char, partner, location)
        self.check_orgasm(partner, char, location)
    
    def send_rhythm_message(self, actor, target, intensity, location):
        """Send an occasional rhythm message."""
        actor_name = getattr(actor, "key", "Someone")
        target_name = getattr(target, "key", "someone")
        
        if intensity < 0.4:
            messages = [
                f"{actor_name} continues the slow, steady rhythm.",
                f"{actor_name} maintains the gentle pace with {target_name}.",
            ]
        elif intensity < 0.7:
            messages = [
                f"{actor_name} keeps up the steady pace.",
                f"{actor_name} thrusts rhythmically into {target_name}.",
            ]
        else:
            messages = [
                f"{actor_name} pounds relentlessly into {target_name}.",
                f"{actor_name} keeps up the brutal pace.",
                f"{actor_name} shows no signs of slowing.",
            ]
        
        # Add arousal reactions sometimes
        target_arousal = self.get_arousal(target)
        if target_arousal > 0.7 and random() < 0.5:
            reactions = [
                f"{target_name} moans loudly.",
                f"{target_name} trembles with pleasure.",
                f"{target_name} gasps, getting close.",
            ]
            msg = f"{choice(messages)} {choice(reactions)}"
        else:
            msg = choice(messages)
        
        location.msg_contents(msg)
    
    def check_orgasm(self, char, partner, location):
        """Check if character should orgasm."""
        arousal = self.get_arousal(char)
        if arousal < 1.0:
            return
        
        # Check refractory
        char_id = self.char_id(char)
        if char_id in (self.db.refractory_until or {}):
            if datetime.now() < self.db.refractory_until[char_id]:
                return
        
        # ORGASM!
        char_name = getattr(char, "key", "Someone")
        partner_name = getattr(partner, "key", "someone")
        
        # Check for mutual
        partner_arousal = self.get_arousal(partner)
        if partner_arousal >= 0.95 and random() < 0.4:
            messages = [
                f"{char_name} and {partner_name} cum together!",
                f"They peak at the same moment, crying out in unison.",
            ]
            msg = choice(messages)
            self.set_arousal(char, 0.1)
            self.set_arousal(partner, 0.1)
            self.start_refractory(char)
            self.start_refractory(partner)
            
            # Clear both rhythms
            self.clear_rhythm(char)
            self.clear_rhythm(partner)
        else:
            messages = [
                f"{char_name} cums hard inside {partner_name}!",
                f"{char_name} groans as orgasm crashes through, filling {partner_name}.",
                f"{char_name} buries deep, pulsing release into {partner_name}.",
            ]
            msg = choice(messages)
            self.set_arousal(char, 0.1)
            self.start_refractory(char)
            self.clear_rhythm(char)
        
        location.msg_contents(msg)
    
    def clear_rhythm(self, char):
        """Clear a character's rhythm."""
        if hasattr(char, "db"):
            char.db.rhythm = None
        else:
            char.rhythm = None
        
        char_id = self.char_id(char)
        if char_id in (self.db.rhythm_counters or {}):
            del self.db.rhythm_counters[char_id]
    
    def tick_arousal(self):
        """Decay arousal for characters not being actively stimulated."""
        if not self.db.active_chars:
            return
        
        to_remove = set()
        
        for char_id in list(self.db.active_chars):
            char = self.get_character(char_id)
            if not char:
                to_remove.add(char_id)
                continue
            
            # Skip if in refractory
            if char_id in (self.db.refractory_until or {}):
                if datetime.now() < self.db.refractory_until[char_id]:
                    continue
            
            # Check if has active rhythm (no decay during rhythm)
            rhythm = None
            if hasattr(char, "db"):
                rhythm = getattr(char.db, "rhythm", None)
            else:
                rhythm = getattr(char, "rhythm", None)
            
            if rhythm:
                continue  # No decay while rhythm active
            
            # Check if in position
            location = getattr(char, "location", None)
            in_position = False
            if location:
                manager = getattr(location, "_position_manager", None)
                if manager:
                    in_position = manager.is_in_position(char)
            
            # Apply decay
            decay = AROUSAL_DECAY_ACTIVE if in_position else AROUSAL_DECAY_RATE
            current = self.get_arousal(char)
            new_val = max(0.0, current - decay)
            self.set_arousal(char, new_val)
            
            if new_val <= 0:
                to_remove.add(char_id)
        
        self.db.active_chars -= to_remove
    
    def tick_refractory(self):
        """Clean up expired refractory periods."""
        if not self.db.refractory_until:
            return
        
        now = datetime.now()
        expired = [cid for cid, until in self.db.refractory_until.items() 
                   if now >= until]
        
        for char_id in expired:
            del self.db.refractory_until[char_id]
            char = self.get_character(char_id)
            if char:
                char.msg("|gYou feel ready to go again.|n")
    
    # ========================================================================
    # Helper Methods
    # ========================================================================
    
    def get_character(self, char_id):
        """Get character from ID."""
        try:
            results = search_object(f"#{char_id}")
            return results[0] if results else None
        except:
            return None
    
    def char_id(self, char):
        """Get ID for a character."""
        return char.id if hasattr(char, "id") else id(char)
    
    def get_arousal(self, char):
        """Get arousal for character."""
        if hasattr(char, "db"):
            return getattr(char.db, "arousal", 0.0) or 0.0
        return getattr(char, "arousal", 0.0)
    
    def set_arousal(self, char, value):
        """Set arousal for character."""
        value = max(0.0, min(1.0, value))
        if hasattr(char, "db"):
            char.db.arousal = value
        else:
            char.arousal = value
    
    def modify_arousal(self, char, delta):
        """Modify arousal, return new value."""
        new_val = max(0.0, min(1.0, self.get_arousal(char) + delta))
        self.set_arousal(char, new_val)
        
        # Register for tracking
        if not self.db.active_chars:
            self.db.active_chars = set()
        self.db.active_chars.add(self.char_id(char))
        
        return new_val
    
    def start_refractory(self, char):
        """Start refractory period."""
        if not self.db.refractory_until:
            self.db.refractory_until = {}
        
        char_id = self.char_id(char)
        self.db.refractory_until[char_id] = datetime.now() + timedelta(seconds=REFRACTORY_DURATION)
    
    # ========================================================================
    # Public Interface
    # ========================================================================
    
    def register_rhythm(self, char):
        """Register a character's rhythm for auto-thrusting."""
        if not self.db.rhythm_counters:
            self.db.rhythm_counters = {}
        
        rhythm = None
        if hasattr(char, "db"):
            rhythm = getattr(char.db, "rhythm", None)
        else:
            rhythm = getattr(char, "rhythm", None)
        
        if rhythm:
            char_id = self.char_id(char)
            self.db.rhythm_counters[char_id] = rhythm.get("interval", 5)
    
    def register_arousal(self, char):
        """Register character for arousal tracking."""
        if not self.db.active_chars:
            self.db.active_chars = set()
        self.db.active_chars.add(self.char_id(char))


# ============================================================================
# Script Management Functions
# ============================================================================

def get_ticker():
    """Get the global sexual state ticker, creating if needed."""
    if not HAS_EVENNIA:
        return None
    
    from evennia import search_script
    
    scripts = search_script("sexual_state_ticker")
    if scripts:
        return scripts[0]
    
    # Create it
    from evennia import create_script
    script = create_script(
        SexualStateTickScript,
        key="sexual_state_ticker",
        persistent=True,
        autostart=True
    )
    return script


def register_arousal(char):
    """Register a character for arousal tracking."""
    ticker = get_ticker()
    if ticker:
        ticker.register_arousal(char)


def register_rhythm(char):
    """Register a character's rhythm for auto-thrusting."""
    ticker = get_ticker()
    if ticker:
        ticker.register_rhythm(char)


def start_refractory(char):
    """Start refractory period for a character."""
    ticker = get_ticker()
    if ticker:
        ticker.start_refractory(char)


def is_refractory(char):
    """Check if character is in refractory period."""
    ticker = get_ticker()
    if not ticker:
        return False
    
    char_id = ticker.char_id(char)
    if not ticker.db.refractory_until:
        return False
    
    from datetime import datetime
    until = ticker.db.refractory_until.get(char_id)
    if until and datetime.now() < until:
        return True
    return False


# ============================================================================
# Room-Level Position Ticker (Optional)
# ============================================================================

class PositionTickScript(DefaultScript):
    """
    Per-room script for position-specific timing.
    This is optional - the global ticker handles most things.
    """
    
    def at_script_creation(self):
        self.key = "position_ticker"
        self.desc = "Tracks position timing"
        self.interval = 60
        self.persistent = True
    
    def at_repeat(self):
        """Check positions for long-duration effects."""
        location = self.obj
        if not location:
            return
        
        manager = getattr(location, "_position_manager", None)
        if not manager:
            return
        
        # Just check for very long positions
        for pos_id, active in list(manager._active_positions.items()):
            duration = active.get_duration()
            if duration > 1800:  # 30 minutes
                for slot_key, occupant in active.occupants.items():
                    occupant.character.msg(
                        "|yYou've been in this position for a while...|n"
                    )


def ensure_room_ticker(room):
    """Ensure a room has a position ticker script (optional)."""
    if not HAS_EVENNIA:
        return None
    
    for script in room.scripts.all():
        if script.key == "position_ticker":
            return script
    
    from evennia import create_script
    return create_script(
        PositionTickScript,
        key="position_ticker",
        obj=room,
        persistent=True,
        autostart=True
    )
