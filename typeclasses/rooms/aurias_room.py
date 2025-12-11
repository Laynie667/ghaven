"""
Auria's Room - A fae girl's bedroom, waiting for her return.

Place in: typeclasses/rooms/aurias_room.py

Features:
- Time-variant descriptions that shift throughout the day
- Fae ambient effects (subtle wrongness, magic bleeding through)
- Family-aware responses (recognizes Helena, Laynie, Shadow)
- Integration points for special objects (Eevee, journal, nest)
"""

from typing import Optional, Dict, List
import random

try:
    from evennia.typeclasses.attributes import AttributeProperty
except (ImportError, TypeError, AttributeError):
    def AttributeProperty(default=None, **kwargs):
        return default

from typeclasses.base_rooms import IndoorRoom


# =============================================================================
# TIME-VARIANT DESCRIPTIONS
# =============================================================================

AURIA_TIME_DESCS = {
    "dawn": (
        "Pale light filters through curtains she picked herself, pink and gauzy. "
        "The room stirs—not physically, but as if waking. The Eevee on the bed "
        "catches the first light, and for a moment its glass eyes almost seem to blink."
    ),
    "morning": (
        "Sunlight fills the room with warmth, catching dust motes that dance like "
        "tiny faeries. The pink walls glow softly. On the bed, the stuffed animals "
        "are arranged in their usual pile, though you could swear the Eevee was "
        "facing the other way yesterday."
    ),
    "afternoon": (
        "The room drowses in afternoon light. Shadows gather in friendly corners. "
        "The pillow nest looks inviting, the chains above it catching occasional "
        "glints of sun. Everything waits, patient and pink and warm."
    ),
    "dusk": (
        "Golden light paints everything amber and rose. The room feels fuller "
        "somehow, as if preparing for something. The Eevee's shadow stretches "
        "long across the bedspread. There are no flowers in the room, yet "
        "you smell flowers."
    ),
    "evening": (
        "Firefly lights drift near the ceiling, fading in and out. They're not "
        "fireflies—there's no source for them, no explanation. The room is warm "
        "despite no fire. The stuffies watch the door."
    ),
    "night": (
        "The room glows faintly, softly, from no source you can find. Moonlight "
        "through the curtains, perhaps, but the glow comes from everywhere and "
        "nowhere. The Eevee's eyes catch light that isn't there."
    ),
    "midnight": (
        "Stars. There are stars on the ceiling. You don't remember them being "
        "there before. The room breathes—slow, patient, waiting. The chains "
        "above the nest sway gently in air that doesn't move."
    ),
}


# =============================================================================
# FAE AMBIENT EFFECTS
# =============================================================================

FAE_AMBIENT_POOL = [
    "A giggle echoes from nowhere. Or maybe you imagined it.",
    "The flowers on her drawings seem brighter than they were a moment ago.",
    "You catch movement in your peripheral vision. Nothing's there.",
    "For just a moment, the room smells like a forest after rain.",
    "The Eevee on the bed seems to be in a slightly different position.",
    "A warm breeze touches your cheek. The window is closed.",
    "One of the crayon suns on the wall flickers. Like actual sunlight.",
    "You hear humming—soft, wordless, gone before you can locate it.",
    "The shadows in the corner are deeper than the lighting explains.",
    "Something brushes past your ankle. Nothing visible.",
    "The air tastes faintly of honey and something you can't name.",
    "Dust motes swirl in a pattern too deliberate to be random.",
]

FAE_FAMILY_MESSAGES = {
    "Helena": [
        "The room seems to brighten when you enter. It knows its Mommy.",
        "Warmth wraps around you like a hug. She left that here for you.",
        "The Eevee's head turns—just slightly—toward you.",
    ],
    "Laynie": [
        "The room relaxes around you. Sister-energy, familiar and safe.",
        "You smell her perfume for just a moment. The one she let you borrow.",
        "The stuffies seem to lean toward you. They remember.",
    ],
    "Shadow": [
        "The room's magic pulses in recognition. Pack. Family. Home.",
        "Every fae-touched corner seems to hum a greeting.",
    ],
    "Auria": [
        "Home. The word fills every corner, every color, every mote of light.",
        "Everything here has been waiting. Everything here is yours.",
        "The room exhales. Finally. Finally you're back.",
    ],
}


# =============================================================================
# AURIA'S ROOM TYPECLASS
# =============================================================================

class AuriasRoom(IndoorRoom):
    """
    Auria's Room - warm, pink, fae-touched, waiting.
    
    A bedroom that belongs to a fae girl who stepped away but is never
    forgotten. The family maintains it. The magic lingers. The stuffies
    keep watch.
    
    Features:
    - Time-variant descriptions that shift with the day
    - Fae ambient effects (random magical moments)
    - Family-aware responses (special messages for family members)
    - Integration with special objects (Eevee, journal, nest)
    """
    
    # -------------------------------------------------------------------------
    # Room Identity
    # -------------------------------------------------------------------------
    
    region = AttributeProperty(default="Helena's Cabin")
    zone = AttributeProperty(default="Private Quarters")
    subzone = AttributeProperty(default="Auria's Wing")
    
    # -------------------------------------------------------------------------
    # Atmosphere
    # -------------------------------------------------------------------------
    
    temperature = AttributeProperty(default="warm")
    lighting = AttributeProperty(default="soft")
    
    # Ambient settings
    ambient_sounds = AttributeProperty(
        default="silence that isn't quite silent, something humming just out of hearing"
    )
    ambient_scents = AttributeProperty(
        default="wildflowers, morning dew, something sweet and strange"
    )
    mood = AttributeProperty(default="fae-touched")
    
    # -------------------------------------------------------------------------
    # State Tracking
    # -------------------------------------------------------------------------
    
    # Family members who belong here
    family_keys = AttributeProperty(default=["Helena", "Laynie", "Auria", "Shadow"])
    
    # Track if Eevee has revealed herself this session
    eevee_revealed = AttributeProperty(default=False)
    
    # Fae effects active
    fae_magic_visible = AttributeProperty(default=True)
    
    # -------------------------------------------------------------------------
    # Setup
    # -------------------------------------------------------------------------
    
    def at_object_creation(self):
        """Initialize the room."""
        super().at_object_creation()
        
        # Room surfaces
        self.ceiling_desc = "a ceiling painted pale pink, with tiny stars that might glow at night"
        self.floor_desc = "bright pink plush carpet, soft as clouds underfoot"
        self.wall_desc = "walls in soft pink, covered with crayon drawings and taped-up art"
        
        # Base description uses shortcodes for dynamic content
        self.db.desc = self._build_base_description()
    
    def _build_base_description(self) -> str:
        """Build the base room description with shortcodes."""
        return """<time.desc>

Stepping in from the main room you are confronted by a plush carpet underfoot, 
bright pink in colour. Scattered across the floor are cushions and pillows of 
all colours, some gathered into a small |wnest|n against the southern wall. 
From the wall above the nest hangs a set of |wchains|n, long enough for someone 
to curl up comfortably in the nest and ending in padded shackles, and a collar 
inscribed with "|yAuria|n".

A comfy |wbed|n stands opposite the door, made up neatly with a pale purple 
bedspread. Perched in the center of the bed is a fluffy |wEevee|n plushie, 
with a jumbled pile around her; a plush dragon in shades of purple, a Squirtle 
and Chikorita small enough to fit in a coat pocket and a happy look raccoon.

Standing beside the nest of pillows is a large |wbookcase|n packed with books, 
a few of the titles standing out; "The Lion, the Witch and the Wardrobe", 
"The Painted Man", "The Black Prism", "The Way of Kings". Beside the bookcase 
is pinned a note; "|wFeel free to add something! Just let me know which is yours!|n"

Against the northern wall rests a |wclosed trunk|n, and a small |wwardrobe|n 
stands against the southern wall. On a small table by the bed, a leather-bound 
|wjournal|n lies open, pen beside it.

<contents>
<exits>"""
    
    # -------------------------------------------------------------------------
    # Time-Based Description
    # -------------------------------------------------------------------------
    
    def get_time_description(self) -> str:
        """Get time-appropriate room description."""
        time_period = self.get_time_period()
        return AURIA_TIME_DESCS.get(time_period, AURIA_TIME_DESCS["morning"])
    
    def get_time_period(self) -> str:
        """
        Get current time period.
        Override this if you have a time system, otherwise defaults to morning.
        """
        # Check if room has time awareness from parent
        if hasattr(super(), 'get_time_period'):
            return super().get_time_period()
        
        # Default fallback - could hook into game time system
        return "morning"
    
    # -------------------------------------------------------------------------
    # Shortcode Processing
    # -------------------------------------------------------------------------
    
    def process_shortcodes(self, text: str, looker=None) -> str:
        """Process room-specific shortcodes."""
        # Parent processing first
        text = super().process_shortcodes(text, looker)
        
        # Time description
        text = text.replace("<time.desc>", self.get_time_description())
        
        # Eevee state
        if self.eevee_revealed:
            text = text.replace("<eevee.state>", "watching you with knowing eyes")
        else:
            text = text.replace("<eevee.state>", "sitting perfectly still among the other stuffies")
        
        return text
    
    # -------------------------------------------------------------------------
    # Family Recognition
    # -------------------------------------------------------------------------
    
    def is_family(self, character) -> bool:
        """Check if a character is family."""
        if not character:
            return False
        char_key = character.key if hasattr(character, 'key') else str(character)
        return char_key in self.family_keys
    
    def get_family_message(self, character) -> Optional[str]:
        """Get a special message for family members."""
        if not self.is_family(character):
            return None
        
        char_key = character.key if hasattr(character, 'key') else str(character)
        messages = FAE_FAMILY_MESSAGES.get(char_key, [])
        
        if messages:
            return random.choice(messages)
        return None
    
    # -------------------------------------------------------------------------
    # Fae Ambient Effects
    # -------------------------------------------------------------------------
    
    def get_fae_ambient(self) -> Optional[str]:
        """
        Get a random fae ambient effect.
        Call this periodically or on certain triggers.
        """
        if not self.fae_magic_visible:
            return None
        
        if random.random() < 0.3:  # 30% chance
            return random.choice(FAE_AMBIENT_POOL)
        return None
    
    def trigger_fae_moment(self, exclude=None):
        """
        Trigger a fae ambient moment for everyone in the room.
        
        Args:
            exclude: Character to exclude from message
        """
        ambient = self.get_fae_ambient()
        if ambient:
            self.msg_contents(f"|m{ambient}|n", exclude=exclude)
    
    # -------------------------------------------------------------------------
    # Entry/Exit Hooks
    # -------------------------------------------------------------------------
    
    def at_object_receive(self, moved_obj, source_location, move_type=None, **kwargs):
        """Called when something enters the room."""
        super().at_object_receive(moved_obj, source_location, move_type, **kwargs)
        
        # Check if it's a character (has account or is NPC)
        is_character = hasattr(moved_obj, 'account') or getattr(moved_obj, 'is_npc', False)
        
        if is_character:
            # Family gets a special message
            family_msg = self.get_family_message(moved_obj)
            if family_msg:
                moved_obj.msg(f"|m{family_msg}|n")
            
            # Small chance of fae ambient on entry
            if random.random() < 0.2:
                # Delayed slightly so it comes after the look
                from evennia.utils import delay
                delay(2, self.trigger_fae_moment, exclude=[moved_obj])
    
    # -------------------------------------------------------------------------
    # Appearance Override
    # -------------------------------------------------------------------------
    
    def return_appearance(self, looker=None, **kwargs):
        """Build the room's appearance."""
        # Get base appearance
        appearance = super().return_appearance(looker, **kwargs)
        
        # Add fae ambient if triggered
        ambient = self.get_fae_ambient()
        if ambient:
            appearance += f"\n\n|m{ambient}|n"
        
        return appearance


# =============================================================================
# BUILDER FUNCTION
# =============================================================================

def create_aurias_room(location=None):
    """
    Create Auria's Room with all its special properties.
    
    Usage:
        from typeclasses.rooms.aurias_room import create_aurias_room
        room = create_aurias_room()
    
    Args:
        location: Parent location if any (usually None for rooms)
    
    Returns:
        The created room object
    """
    from evennia import create_object
    
    room = create_object(
        AuriasRoom,
        key="Auria's Room",
        location=location,
    )
    
    return room


# =============================================================================
# EXPORTS
# =============================================================================

__all__ = [
    "AuriasRoom",
    "create_aurias_room",
    "AURIA_TIME_DESCS",
    "FAE_AMBIENT_POOL",
    "FAE_FAMILY_MESSAGES",
]
