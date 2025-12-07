"""
Object Typeclasses - Things That Exist in the World

This module provides objects that make spaces feel alive and interactive:
- Base objects with descriptions and physical properties
- Landmarks that define spaces (fountains, statues, trees)
- Atmospheric objects that add to ambiance
- Furniture for positions and interactions
- Containers with open/close/lock mechanics
- Special objects like the Iron Fae statue

Objects should feel tangible. They have weight, size, texture. They can
be examined, touched, sometimes used. They respond to the world around
them - a fountain sounds different in rain, a fire crackles louder at night.

Mixins:
    DescribableMixin - Short/long descriptions with shortcode support
    PhysicalMixin - Size, weight, physical properties
    SensoryMixin - Visual, sound, scent properties

Object Types:
    Object - Base object with all mixins
    Landmark - Major features that define spaces
    AtmosphericObject - Objects that add to room ambiance
    Furniture - Sittable, usable objects with positions
    Container - Objects that hold other objects
    LightSource - Objects that provide illumination
    IronFaeStatue - Special portal object (Auria's memorial)
"""

from typing import Optional, List, Dict, Any
from evennia.objects.objects import DefaultObject
import random

# Handle early import during Django migration loading
try:
    from evennia.typeclasses.attributes import AttributeProperty
except (ImportError, TypeError, AttributeError):
    # Fallback for migration time
    def AttributeProperty(default=None, **kwargs):
        return default


# =============================================================================
# EVENNIA COMPATIBILITY - ObjectParent
# =============================================================================

class ObjectParent:
    """
    Mixin inherited by both Object and Character.
    
    Evennia's default characters.py imports this.
    Put any methods here that should exist on BOTH objects and characters.
    """
    pass


# =============================================================================
# SIZE AND WEIGHT CONSTANTS
# =============================================================================

SIZE_HIERARCHY = {
    "tiny": 1,      # Ring, coin, insect
    "small": 2,     # Book, dagger, apple
    "medium": 3,    # Sword, chair, dog
    "large": 4,     # Table, horse, person
    "huge": 5,      # Cart, elephant, small building
    "massive": 6,   # Ship, dragon, building
}

WEIGHT_CATEGORIES = {
    "negligible": 0,    # Feather, paper
    "light": 1,         # Book, small tool
    "moderate": 2,      # Sword, chair
    "heavy": 3,         # Armor, large chest
    "very_heavy": 4,    # Anvil, statue
    "immovable": 5,     # Building, mountain
}


# =============================================================================
# DESCRIBABLE MIXIN
# =============================================================================

class DescribableMixin:
    """
    Provides rich description support with shortcodes.
    
    Shortcodes in descriptions are processed dynamically:
    - <self.name> - Object's name
    - <self.state> - Current state (if applicable)
    - <time.period> - Current time of day
    - <weather> - Current weather
    - <season> - Current season
    """
    
    # Short description (shown in room contents)
    short_desc = AttributeProperty(default="")
    
    # Examined description (shown when looked at directly)
    examined = AttributeProperty(default="")
    
    # State-based descriptions
    state_descriptions = AttributeProperty(default=dict)  # {state: desc}
    
    # Current state
    current_state = AttributeProperty(default="default")
    
    def get_short_desc(self, looker=None) -> str:
        """Get the short description."""
        if self.short_desc:
            return self.process_shortcodes(self.short_desc, looker)
        return self.key
    
    def get_examined_desc(self, looker=None) -> str:
        """Get the full examined description."""
        # Check for state-specific description
        if self.current_state in self.state_descriptions:
            desc = self.state_descriptions[self.current_state]
        elif self.examined:
            desc = self.examined
        elif self.db.desc:
            desc = self.db.desc
        else:
            desc = f"You see nothing special about {self.key}."
        
        return self.process_shortcodes(desc, looker)
    
    def process_shortcodes(self, text: str, looker=None) -> str:
        """Process shortcodes in text."""
        if not text:
            return ""
        
        # Self references
        text = text.replace("<self.name>", self.key)
        text = text.replace("<self.state>", self.current_state)
        
        # Get room for context
        room = self.location
        
        # Time
        if room and hasattr(room, 'get_time_period'):
            text = text.replace("<time.period>", room.get_time_period())
        else:
            text = text.replace("<time.period>", "day")
        
        # Weather
        if room and hasattr(room, 'get_weather'):
            text = text.replace("<weather>", room.get_weather())
        else:
            text = text.replace("<weather>", "clear")
        
        # Season
        if room and hasattr(room, 'get_season'):
            text = text.replace("<season>", room.get_season())
        else:
            text = text.replace("<season>", "summer")
        
        return text
    
    def set_state(self, state: str) -> bool:
        """Change the object's state."""
        self.current_state = state
        return True


# =============================================================================
# PHYSICAL MIXIN
# =============================================================================

class PhysicalMixin:
    """
    Provides physical properties - size, weight, material.
    """
    
    size = AttributeProperty(default="medium")
    weight = AttributeProperty(default="moderate")
    material = AttributeProperty(default="")
    
    # Can this object be picked up?
    portable = AttributeProperty(default=True)
    
    # Does this block movement/sight?
    blocks_movement = AttributeProperty(default=False)
    blocks_sight = AttributeProperty(default=False)
    
    def get_size_value(self) -> int:
        """Get numeric size value."""
        return SIZE_HIERARCHY.get(self.size, 3)
    
    def get_weight_value(self) -> int:
        """Get numeric weight value."""
        return WEIGHT_CATEGORIES.get(self.weight, 2)
    
    def fits_through(self, max_size: str) -> bool:
        """Check if this object fits through an opening."""
        max_val = SIZE_HIERARCHY.get(max_size, 6)
        return self.get_size_value() <= max_val
    
    def can_contain(self, other) -> bool:
        """Check if this object can contain another."""
        if not hasattr(other, 'get_size_value'):
            return True
        return other.get_size_value() < self.get_size_value()
    
    def can_be_carried(self) -> bool:
        """Check if object can be picked up."""
        if not self.portable:
            return False
        if self.weight == "immovable":
            return False
        return True


# =============================================================================
# SENSORY MIXIN
# =============================================================================

class SensoryMixin:
    """
    Provides sensory properties - what you see, hear, smell.
    
    These properties can contribute to room atmosphere and
    be perceived from adjacent rooms through exits.
    """
    
    # Visibility
    visible = AttributeProperty(default=True)
    glow = AttributeProperty(default=False)
    glow_color = AttributeProperty(default="")
    
    # Sound
    makes_sound = AttributeProperty(default=False)
    sound_desc = AttributeProperty(default="")
    sound_volume = AttributeProperty(default="quiet")  # quiet, moderate, loud
    
    # State-based sounds
    sound_states = AttributeProperty(default=dict)  # {state: sound_desc}
    
    # Scent
    has_scent = AttributeProperty(default=False)
    scent_desc = AttributeProperty(default="")
    scent_strength = AttributeProperty(default="faint")  # faint, moderate, strong
    
    # Touch/texture
    texture = AttributeProperty(default="")
    temperature = AttributeProperty(default="normal")  # cold, cool, normal, warm, hot
    
    def get_current_sound(self) -> str:
        """Get the current sound this object makes."""
        if not self.makes_sound:
            return ""
        
        # Check for state-specific sound
        state = getattr(self, 'current_state', 'default')
        if state in self.sound_states:
            return self.sound_states[state]
        
        return self.sound_desc
    
    def get_sensory_desc(self) -> str:
        """Get full sensory description."""
        parts = []
        
        if self.glow:
            parts.append(f"It glows with a {self.glow_color or 'soft'} light.")
        
        if self.makes_sound and self.sound_desc:
            parts.append(self.sound_desc)
        
        if self.has_scent and self.scent_desc:
            parts.append(f"It smells of {self.scent_desc}.")
        
        if self.texture:
            parts.append(f"It feels {self.texture} to the touch.")
        
        return " ".join(parts)


# =============================================================================
# BASE OBJECT
# =============================================================================

class Object(ObjectParent, DescribableMixin, PhysicalMixin, SensoryMixin, DefaultObject):
    """
    Base object with full feature support.
    
    All objects in the game inherit from this, gaining:
    - Rich descriptions with shortcode processing
    - Physical properties (size, weight, material)
    - Sensory properties (sight, sound, scent)
    """
    
    def at_object_creation(self):
        """Called when object is first created."""
        super().at_object_creation()
    
    def return_appearance(self, looker=None, **kwargs):
        """
        Main appearance method.
        """
        parts = []
        
        # Name
        parts.append(f"|w{self.key}|n")
        
        # Main description
        parts.append(self.get_examined_desc(looker))
        
        # Sensory additions
        sensory = self.get_sensory_desc()
        if sensory:
            parts.append("")
            parts.append(sensory)
        
        return "\n".join(parts)
    
    def get_display_name(self, looker=None, **kwargs):
        """Return name for display in room contents."""
        if self.short_desc:
            return self.get_short_desc(looker)
        return self.key


# =============================================================================
# LANDMARK
# =============================================================================

class Landmark(Object):
    """
    A major feature that defines a space.
    
    Landmarks are:
    - Usually immovable
    - Often referenced in room descriptions
    - May have special interactions
    - Contribute significantly to atmosphere
    
    Examples: Fountains, statues, large trees, monuments
    """
    
    portable = AttributeProperty(default=False)
    weight = AttributeProperty(default="immovable")
    
    # Landmark type for categorization
    landmark_type = AttributeProperty(default="structure")
    
    # Does this landmark have special interactions?
    interactable = AttributeProperty(default=False)
    interaction_verb = AttributeProperty(default="use")
    interaction_desc = AttributeProperty(default="")
    
    # Time-variant appearance
    time_appearances = AttributeProperty(default=dict)  # {"night": "desc", etc}
    
    # Weather-variant appearance
    weather_appearances = AttributeProperty(default=dict)  # {"rain": "desc", etc}
    
    def get_examined_desc(self, looker=None) -> str:
        """Get description with time/weather variations."""
        room = self.location
        
        # Check time-specific description
        if room and hasattr(room, 'get_time_period'):
            time = room.get_time_period()
            if time in self.time_appearances:
                return self.process_shortcodes(self.time_appearances[time], looker)
        
        # Check weather-specific description
        if room and hasattr(room, 'get_weather'):
            weather = room.get_weather()
            if weather in self.weather_appearances:
                return self.process_shortcodes(self.weather_appearances[weather], looker)
        
        # Default
        return super().get_examined_desc(looker)
    
    def at_interact(self, interactor) -> str:
        """Called when someone interacts with this landmark."""
        if not self.interactable:
            return f"You can't {self.interaction_verb} {self.key}."
        
        if self.interaction_desc:
            return self.interaction_desc
        
        return f"You {self.interaction_verb} {self.key}."


# =============================================================================
# ATMOSPHERIC OBJECT
# =============================================================================

class AtmosphericObject(Object):
    """
    Objects that primarily add to room ambiance.
    
    These objects:
    - Contribute sounds/scents to room atmosphere
    - May not be directly interactable
    - Often have state-based variations (fire burning/dying)
    - React to time/weather
    
    Examples: Crackling fireplace, bubbling cauldron, wind chimes
    """
    
    # Pool of ambient descriptions
    ambient_pool = AttributeProperty(default=list)
    ambient_chance = AttributeProperty(default=0.3)
    
    # Activity (for animated objects)
    is_active = AttributeProperty(default=True)
    active_desc = AttributeProperty(default="")
    inactive_desc = AttributeProperty(default="")
    
    def get_ambient_contribution(self) -> str:
        """Get this object's contribution to room ambiance."""
        if not self.is_active:
            return ""
        
        if self.ambient_pool and random.random() < self.ambient_chance:
            return random.choice(self.ambient_pool)
        
        return ""
    
    def activate(self) -> str:
        """Activate this atmospheric object."""
        if self.is_active:
            return f"{self.key} is already active."
        
        self.is_active = True
        return self.active_desc or f"{self.key} comes to life."
    
    def deactivate(self) -> str:
        """Deactivate this atmospheric object."""
        if not self.is_active:
            return f"{self.key} is already inactive."
        
        self.is_active = False
        return self.inactive_desc or f"{self.key} goes quiet."


# =============================================================================
# FURNITURE
# =============================================================================

class Furniture(Object):
    """
    Objects that can be sat on, laid on, or otherwise used.
    
    Furniture provides:
    - Position slots (sit, lay, lean, etc.)
    - Capacity limits
    - User tracking
    - Position-specific descriptions
    """
    
    portable = AttributeProperty(default=False)
    weight = AttributeProperty(default="heavy")
    
    # Capacity
    capacity = AttributeProperty(default=1)
    current_users = AttributeProperty(default=list)
    
    # Available positions
    position_slots = AttributeProperty(default=list)  # ["sit", "lay", "lean"]
    
    # Position descriptions (what it looks like when occupied)
    position_descs = AttributeProperty(default=dict)  # {"sit": "{name} sits on..."}
    
    # Comfort level (affects rest/recovery)
    comfort = AttributeProperty(default="normal")  # uncomfortable, normal, comfortable, luxurious
    
    def at_object_creation(self):
        """Set default position slots."""
        super().at_object_creation()
        if not self.position_slots:
            self.position_slots = ["sit"]
    
    def get_available_slots(self) -> int:
        """Get number of available slots."""
        return self.capacity - len(self.current_users)
    
    def is_occupied(self) -> bool:
        """Check if furniture has any users."""
        return len(self.current_users) > 0
    
    def is_full(self) -> bool:
        """Check if furniture is at capacity."""
        return len(self.current_users) >= self.capacity
    
    def add_user(self, user, position: str = None) -> tuple[bool, str]:
        """
        Add a user to this furniture.
        
        Args:
            user: The character using the furniture
            position: The position type (sit, lay, etc.)
            
        Returns:
            (success, message)
        """
        if self.is_full():
            return (False, f"There's no room on {self.key}.")
        
        if position and position not in self.position_slots:
            available = ", ".join(self.position_slots)
            return (False, f"You can only {available} on {self.key}.")
        
        # Add user
        users = list(self.current_users)
        users.append({
            "user_id": user.id,
            "position": position or self.position_slots[0],
        })
        self.current_users = users
        
        pos = position or self.position_slots[0]
        return (True, f"You {pos} on {self.key}.")
    
    def remove_user(self, user) -> tuple[bool, str]:
        """Remove a user from this furniture."""
        users = list(self.current_users)
        for i, u in enumerate(users):
            if u["user_id"] == user.id:
                users.pop(i)
                self.current_users = users
                return (True, f"You get up from {self.key}.")
        
        return (False, f"You're not on {self.key}.")
    
    def get_user_position(self, user) -> Optional[str]:
        """Get a user's current position on this furniture."""
        for u in self.current_users:
            if u["user_id"] == user.id:
                return u["position"]
        return None
    
    def get_occupied_desc(self) -> str:
        """Get description of who's using this furniture."""
        if not self.current_users:
            return ""
        
        parts = []
        for u in self.current_users:
            # Find the user object
            for obj in self.location.contents if self.location else []:
                if hasattr(obj, 'id') and obj.id == u["user_id"]:
                    pos = u["position"]
                    if pos in self.position_descs:
                        parts.append(self.position_descs[pos].format(name=obj.key))
                    else:
                        parts.append(f"{obj.key} is {pos}ting on {self.key}.")
                    break
        
        return " ".join(parts)


# =============================================================================
# CONTAINER
# =============================================================================

class Container(Object):
    """
    Objects that can hold other objects.
    
    Containers have:
    - Open/close states
    - Optional locks
    - Capacity limits
    - Visibility of contents
    """
    
    # Container state
    is_open = AttributeProperty(default=True)
    is_locked = AttributeProperty(default=False)
    
    # Lock properties
    key_id = AttributeProperty(default="")
    lock_difficulty = AttributeProperty(default=0)
    
    # Capacity
    max_contents = AttributeProperty(default=10)
    max_weight = AttributeProperty(default="heavy")
    
    # Can you see inside when closed?
    transparent = AttributeProperty(default=False)
    
    # Descriptions for states
    open_desc = AttributeProperty(default="")
    closed_desc = AttributeProperty(default="")
    locked_desc = AttributeProperty(default="")
    
    def get_examined_desc(self, looker=None) -> str:
        """Include container state in description."""
        # Get base description
        base = super().get_examined_desc(looker)
        
        # Add state-specific description
        if self.is_locked:
            state_desc = self.locked_desc or "It is locked."
        elif not self.is_open:
            state_desc = self.closed_desc or "It is closed."
        else:
            state_desc = self.open_desc or "It is open."
        
        parts = [base, state_desc]
        
        # Show contents if visible
        if self.is_open or self.transparent:
            contents = self.get_visible_contents(looker)
            if contents:
                parts.append(f"Inside you see: {contents}")
            else:
                parts.append("It is empty.")
        
        return "\n".join(parts)
    
    def get_visible_contents(self, looker=None) -> str:
        """Get string listing visible contents."""
        items = []
        for obj in self.contents:
            if hasattr(obj, 'visible') and not obj.visible:
                continue
            items.append(obj.get_display_name(looker) if hasattr(obj, 'get_display_name') else obj.key)
        
        return ", ".join(items)
    
    def open(self, opener=None) -> tuple[bool, str]:
        """Open the container."""
        if self.is_open:
            return (False, f"{self.key} is already open.")
        
        if self.is_locked:
            return (False, f"{self.key} is locked.")
        
        self.is_open = True
        return (True, f"You open {self.key}.")
    
    def close(self, closer=None) -> tuple[bool, str]:
        """Close the container."""
        if not self.is_open:
            return (False, f"{self.key} is already closed.")
        
        self.is_open = False
        return (True, f"You close {self.key}.")
    
    def lock(self, locker=None, key=None) -> tuple[bool, str]:
        """Lock the container."""
        if self.is_locked:
            return (False, f"{self.key} is already locked.")
        
        if self.is_open:
            return (False, f"Close {self.key} first.")
        
        if self.key_id and key:
            key_match = getattr(key, 'key_id', None) == self.key_id
            if not key_match:
                return (False, "That key doesn't fit.")
        
        self.is_locked = True
        return (True, f"You lock {self.key}.")
    
    def unlock(self, unlocker=None, key=None) -> tuple[bool, str]:
        """Unlock the container."""
        if not self.is_locked:
            return (False, f"{self.key} is not locked.")
        
        if self.key_id:
            if not key:
                return (False, f"{self.key} requires a key.")
            key_match = getattr(key, 'key_id', None) == self.key_id
            if not key_match:
                return (False, "That key doesn't fit.")
        
        self.is_locked = False
        return (True, f"You unlock {self.key}.")
    
    def can_accept(self, obj) -> tuple[bool, str]:
        """Check if container can accept an object."""
        if not self.is_open:
            return (False, f"{self.key} is closed.")
        
        if len(self.contents) >= self.max_contents:
            return (False, f"{self.key} is full.")
        
        if hasattr(obj, 'get_size_value') and hasattr(self, 'get_size_value'):
            if obj.get_size_value() >= self.get_size_value():
                return (False, f"{obj.key} is too large for {self.key}.")
        
        return (True, "")


# =============================================================================
# LIGHT SOURCE
# =============================================================================

class LightSource(AtmosphericObject):
    """
    Objects that provide illumination.
    
    Light sources:
    - Have fuel/duration (or are permanent)
    - Affect room lighting when active
    - Can be lit/extinguished
    """
    
    # Light properties
    is_lit = AttributeProperty(default=False)
    light_level = AttributeProperty(default="normal")  # dim, normal, bright
    light_radius = AttributeProperty(default=1)  # How many rooms it lights
    
    # Fuel
    uses_fuel = AttributeProperty(default=True)
    fuel_remaining = AttributeProperty(default=100)
    fuel_per_tick = AttributeProperty(default=1)
    
    # Permanent light (magic, etc.)
    is_permanent = AttributeProperty(default=False)
    
    # Descriptions
    lit_desc = AttributeProperty(default="")
    unlit_desc = AttributeProperty(default="")
    
    def light(self, lighter=None) -> tuple[bool, str]:
        """Light this light source."""
        if self.is_lit:
            return (False, f"{self.key} is already lit.")
        
        if self.uses_fuel and self.fuel_remaining <= 0:
            return (False, f"{self.key} has no fuel.")
        
        self.is_lit = True
        self.is_active = True
        
        return (True, self.lit_desc or f"You light {self.key}.")
    
    def extinguish(self, extinguisher=None) -> tuple[bool, str]:
        """Extinguish this light source."""
        if not self.is_lit:
            return (False, f"{self.key} is not lit.")
        
        if self.is_permanent:
            return (False, f"{self.key} cannot be extinguished.")
        
        self.is_lit = False
        self.is_active = False
        
        return (True, self.unlit_desc or f"You extinguish {self.key}.")
    
    def consume_fuel(self) -> bool:
        """
        Consume fuel for one tick.
        
        Returns False if fuel runs out.
        """
        if not self.uses_fuel or self.is_permanent:
            return True
        
        self.fuel_remaining -= self.fuel_per_tick
        
        if self.fuel_remaining <= 0:
            self.is_lit = False
            self.is_active = False
            return False
        
        return True
    
    def refuel(self, amount: int = 100) -> str:
        """Add fuel to this light source."""
        if not self.uses_fuel:
            return f"{self.key} doesn't use fuel."
        
        self.fuel_remaining = min(100, self.fuel_remaining + amount)
        return f"You refuel {self.key}."


# =============================================================================
# IRON FAE STATUE
# =============================================================================

class IronFaeStatue(Landmark):
    """
    The Iron Fae - Memorial to Auria.
    
    A statue crafted primarily of iron, a metal anathema to the fae.
    It stands as testament to an unnatural absence.
    
    For those who know the secret, who approach with love rather than
    curiosity, the statue is not merely a monument. It is a door.
    
    A kiss opens the way.
    
    This special object:
    - Acts as a hidden portal to Vormir
    - Accepts offerings that appear in both locations
    - Responds to certain interactions (kiss)
    - Has deep emotional/lore significance
    """
    
    landmark_type = AttributeProperty(default="memorial")
    
    # Portal destination
    destination_id = AttributeProperty(default=None)  # Room ID on Vormir
    
    # Who has access (player IDs)
    has_access = AttributeProperty(default=list)
    
    # Access conditions
    requires_love = AttributeProperty(default=True)  # Must have relationship with pack
    
    # Offerings
    offerings = AttributeProperty(default=list)  # Items left at statue
    
    # Emotional states - different descriptions based on viewer
    stranger_desc = AttributeProperty(default="""
A statue of mixed metals stands here, primarily iron but threaded with 
silver and gold. It depicts a feminine figure of ethereal beauty—pointed 
ears, flowing hair, a smile that seems sad from one angle, hopeful from 
another.

The craftsmanship is exquisite. The iron seems wrong for such delicate 
features, and yet... there's something intentional about that wrongness. 
Something painful.

A small plaque at the base reads: |y"Auria. The door remains open."|n

Offerings are scattered at the statue's feet—flowers, small tokens, 
written notes. Some look fresh. Some have been here a very long time.
""")
    
    knowing_desc = AttributeProperty(default="""
She stands before you, frozen in iron—the one metal she could never touch 
without burning. The statue captures her perfectly: the tilt of her head, 
the curve of her smile, the way her eyes seemed to hold secrets and 
promises in equal measure.

This is not merely a memorial. This is a door. A promise.

|cThe way home remains open.|n

You know what to do.
""")
    
    def get_examined_desc(self, looker=None) -> str:
        """Return appropriate description based on viewer."""
        if looker and self._has_access(looker):
            return self.process_shortcodes(self.knowing_desc, looker)
        return self.process_shortcodes(self.stranger_desc, looker)
    
    def _has_access(self, character) -> bool:
        """Check if character has access to the portal."""
        if not character:
            return False
        
        # Check explicit access list
        if character.id in self.has_access:
            return True
        
        # Check for relationship markers
        if hasattr(character, 'db'):
            if character.db.pack_member:
                return True
            if character.db.knows_iron_fae:
                return True
        
        return False
    
    def grant_access(self, character) -> None:
        """Grant a character access to the portal."""
        if character.id not in self.has_access:
            access_list = list(self.has_access)
            access_list.append(character.id)
            self.has_access = access_list
    
    def revoke_access(self, character) -> None:
        """Revoke a character's access."""
        if character.id in self.has_access:
            access_list = list(self.has_access)
            access_list.remove(character.id)
            self.has_access = access_list
    
    def at_kiss(self, kisser) -> str:
        """
        Handle the kiss interaction.
        
        This is the secret that opens the way.
        """
        if not self._has_access(kisser):
            # Beautiful but sad response for strangers
            return """
You press your lips to the cold iron. It tastes of metal and old sorrow.

Nothing happens. The statue remains a statue. Whatever magic others 
speak of, it does not respond to you.

|xPerhaps you need to be known, first. Perhaps you need to love, 
and be loved in return.|n
"""
        
        # For those with access - the way opens
        if not self.destination_id:
            return """
You press your lips to the iron. It's warm, somehow. Welcoming.

The world shimmers—but the way is not yet ready. The destination 
awaits construction.

|y(The portal destination has not been set.)|n
"""
        
        # Teleport to Vormir
        from evennia import search_object
        results = search_object(f"#{self.destination_id}")
        
        if not results:
            return "The way flickers but does not open. Something is wrong."
        
        destination = results[0]
        
        # The transition
        kisser.msg("""
You press your lips to the iron, expecting cold—but it's warm. 
Alive. The statue seems to lean into the kiss.

The world dissolves around you. For a moment, you are nowhere—
suspended between here and there, between absence and presence.

Then you are |csomewhere else|n.
""")
        
        # Notify origin room
        if kisser.location:
            kisser.location.msg_contents(
                f"{kisser.key} kisses the statue—and vanishes.",
                exclude=[kisser]
            )
        
        # Move the player
        kisser.move_to(destination, quiet=True)
        
        # Notify destination
        destination.msg_contents(
            f"The air shimmers, and {kisser.key} materializes from nowhere.",
            exclude=[kisser]
        )
        
        return ""  # Message already sent
    
    def leave_offering(self, character, item) -> str:
        """Leave an offering at the statue."""
        # Move item to statue
        item.move_to(self, quiet=True)
        
        # Record offering
        offerings = list(self.offerings)
        offerings.append({
            "item": item.key,
            "from": character.key,
            "item_id": item.id,
        })
        self.offerings = offerings
        
        # Response based on access
        if self._has_access(character):
            return f"""
You place {item.key} at Auria's feet.

For a moment—just a moment—you could swear the statue's expression shifts. 
Something like gratitude. Something like longing.

|yThe offering will appear in both places.|n
"""
        else:
            return f"""
You place {item.key} among the other offerings at the statue's base.

You're not sure why, exactly. It just felt right.
"""


# =============================================================================
# EXPORTS
# =============================================================================

__all__ = [
    # Evennia Compatibility
    "ObjectParent",
    
    # Constants
    "SIZE_HIERARCHY",
    "WEIGHT_CATEGORIES",
    
    # Mixins
    "DescribableMixin",
    "PhysicalMixin",
    "SensoryMixin",
    
    # Object Types
    "Object",
    "Landmark",
    "AtmosphericObject",
    "Furniture",
    "Container",
    "LightSource",
    "IronFaeStatue",
]
