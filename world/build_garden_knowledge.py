"""
Garden of Knowledge Builder - Helena's Cabin

Creates the Garden of Knowledge (Oreo's library grove) with:
- GardenRoom typeclass with eternal sunset phases
- RootDesk with dynamic state and note-writing system
- LivingBookshelves with browsable sections
- LivingFlora responsive to presence
- Beanbag chair, atmospheric objects

Uses existing systems:
- AuriasJournal pattern for desk notes
- Furniture base for desk/beanbag
- AuriaBookcase pattern for bookshelves

Run from Evennia:
    @py from world.build_garden_knowledge import build; build()

Test functions:
    @py from world.build_garden_knowledge import test_sunset; test_sunset()
    @py from world.build_garden_knowledge import test_desk; test_desk()
    @py from world.build_garden_knowledge import test_notes; test_notes()
"""

import random
from datetime import datetime
from typing import Dict, List, Optional

from evennia import create_object, search_object
from evennia.typeclasses.attributes import AttributeProperty
from evennia.utils import logger

from typeclasses.objects import Object, Furniture, Container
from typeclasses.rooms import IndoorRoom


# =============================================================================
# SUNSET PHASE DATA
# =============================================================================

SUNSET_PHASES = {
    "dawn": (
        "The sunset glows with early warmth—pinks and soft oranges, as if the "
        "sun is just beginning its descent. Fresh dew glistens on leaves and flowers."
    ),
    "morning": (
        "Golden hour light, the sunset frozen at its most brilliant. The living "
        "shelves seem to stretch toward the warm glow. Peaceful reading light."
    ),
    "afternoon": (
        "Deep amber and rose, the sunset at its richest. Shadows are soft and "
        "warm. The earth smells fertile. Perfect for napping in the beanbag."
    ),
    "evening": (
        "Purples deepen, the sunset shifting toward twilight. The flowers close "
        "slightly. Intimate, cozy, magical."
    ),
    "night": (
        "The sunset holds at its final moment—deep violets and magentas, stars "
        "beginning to appear in the \"sky.\" Bioluminescent hints in the flowers. "
        "Enchanted."
    ),
}

# Map real time periods to sunset phases
TIME_TO_SUNSET = {
    "dawn": "dawn",
    "morning": "morning",
    "midday": "afternoon",
    "afternoon": "afternoon",
    "evening": "evening",
    "night": "night",
}


# =============================================================================
# DESK STATE DATA
# =============================================================================

DESK_STATES = {
    "clean": (
        "the surface is clear and polished, notes and quills arranged with care. "
        "Ready for work or... other activities"
    ),
    "cluttered": (
        "though the clutter atop suggest an obscene activity, and recently so, "
        "may have taken place by evidence left in the form of wet spots on "
        "carefully written notes"
    ),
    "messy": (
        "the surface is a mess of scattered papers, some stuck together, wet "
        "spots still glistening on the polished roots. Someone was busy here "
        "not long ago"
    ),
    "soaked": (
        "the surface is practically dripping, papers ruined, ink running. "
        "Whatever happened here was intense, enthusiastic, and very recent. "
        "The wood will need to be wiped down"
    ),
}

# Decay order: soaked -> messy -> cluttered -> clean
DESK_STATE_ORDER = ["clean", "cluttered", "messy", "soaked"]


# =============================================================================
# GARDEN ROOM TYPECLASS
# =============================================================================

class GardenRoom(IndoorRoom):
    """
    The Garden of Knowledge - a fae library grove in eternal sunset.
    
    Features:
    - Eternal sunset that shifts through phases based on time
    - <time.desc> shortcode for sunset phase description
    - <desk.state> shortcode pulls from RootDesk in room
    - Living environment hooks
    """
    
    # Override normal time behavior
    eternal_sunset = AttributeProperty(default=True)
    
    def at_object_creation(self):
        """Initialize the garden room."""
        super().at_object_creation()
        
        self.db.atmosphere = {
            "preset": "fae_library",
            "sounds": "rustling leaves, pages turning, soft humming, quill scratching",
            "scents": "flowers, rich earth, old books, ink, something sweet",
            "mood": "magical sanctuary",
        }
        self.db.temperature = "warm"
        self.db.lighting = "eternal sunset"
    
    def get_sunset_phase(self) -> str:
        """
        Get current sunset phase based on world time.
        Maps normal time periods to sunset equivalents.
        """
        # Try to get world time
        try:
            from world.world_state import get_world_state
            world = get_world_state()
            if world:
                time_period = world.get_time_period()
                return TIME_TO_SUNSET.get(time_period, "afternoon")
        except (ImportError, AttributeError):
            pass
        
        # Fallback: use real time roughly
        hour = datetime.now().hour
        if 5 <= hour < 8:
            return "dawn"
        elif 8 <= hour < 12:
            return "morning"
        elif 12 <= hour < 17:
            return "afternoon"
        elif 17 <= hour < 21:
            return "evening"
        else:
            return "night"
    
    def get_desk(self):
        """Find the RootDesk in this room."""
        for obj in self.contents:
            if isinstance(obj, RootDesk):
                return obj
        return None
    
    def process_shortcodes(self, text: str, looker=None) -> str:
        """Process room description shortcodes."""
        # Call parent if exists
        if hasattr(super(), 'process_shortcodes'):
            text = super().process_shortcodes(text, looker)
        
        # <time.desc> - Sunset phase description
        phase = self.get_sunset_phase()
        time_desc = SUNSET_PHASES.get(phase, SUNSET_PHASES["afternoon"])
        text = text.replace("<time.desc>", time_desc)
        
        # <desk.state> - Pull from desk object
        desk = self.get_desk()
        if desk:
            desk_desc = desk.get_state_desc()
        else:
            desk_desc = DESK_STATES["cluttered"]
        text = text.replace("<desk.state>", desk_desc)
        
        return text
    
    def return_appearance(self, looker, **kwargs):
        """Return room description with shortcodes processed."""
        # Get base appearance
        appearance = super().return_appearance(looker, **kwargs)
        
        # Process shortcodes
        appearance = self.process_shortcodes(appearance, looker)
        
        return appearance
    
    def at_object_receive(self, moved_obj, source_location, **kwargs):
        """Called when something enters the room."""
        super().at_object_receive(moved_obj, source_location, **kwargs)
        
        # Trigger flora response if a character enters
        if hasattr(moved_obj, 'account') or hasattr(moved_obj, 'is_npc'):
            self._flora_responds(moved_obj)
    
    def _flora_responds(self, character):
        """The living flora responds to someone entering."""
        flora = None
        for obj in self.contents:
            if isinstance(obj, LivingFlora):
                flora = obj
                break
        
        if flora and random.random() < 0.4:  # 40% chance
            flora.ambient_response(character)


# =============================================================================
# ROOT DESK TYPECLASS
# =============================================================================

class RootDesk(Furniture):
    """
    The root desk at the center of the garden.
    
    Features:
    - Dynamic state (clean -> cluttered -> messy -> soaked)
    - Note-writing system (like AuriasJournal)
    - Beneath position with partial visibility
    - Natural root restraint points
    """
    
    portable = AttributeProperty(default=False)
    weight = AttributeProperty(default="immovable")
    
    # Furniture settings
    capacity = AttributeProperty(default=2)  # Seated + beneath
    position_slots = AttributeProperty(default=[
        "seated", "bent over", "beneath", "atop", "kneeling beneath"
    ])
    position_descs = AttributeProperty(default={
        "seated": "{name} sits at the root desk, working.",
        "bent over": "{name} is bent over the desk surface.",
        "beneath": "{name} is hidden beneath the twisted roots.",
        "atop": "{name} is sprawled across the desk.",
        "kneeling beneath": "{name} kneels beneath the desk, between someone's legs.",
    })
    
    # Desk state
    desk_state = AttributeProperty(default="cluttered")
    
    # Notes system (like AuriasJournal)
    notes = AttributeProperty(default=list)
    max_notes = AttributeProperty(default=30)
    
    # Restraint points
    restraint_points = AttributeProperty(default=[
        "root formation (wrists)",
        "root formation (ankles)",
        "beneath desk roots",
    ])
    
    def at_object_creation(self):
        """Initialize the desk."""
        super().at_object_creation()
        
        self.db.desc = (
            "At the room's center, like the court surrounding a prized water "
            "feature in a garden, roots twist and weave to form a sturdy desk. "
            "The surface is smooth and polished from use, the wood warm and "
            "alive beneath your hands.\n\n"
            "The tangled roots form a hollow space beneath—large enough for "
            "someone to kneel comfortably, hidden from casual view but "
            "accessible to whoever sits at the desk."
        )
        
        self.aliases.add("desk")
        self.aliases.add("root desk")
    
    # -------------------------------------------------------------------------
    # State Management
    # -------------------------------------------------------------------------
    
    def get_state_desc(self) -> str:
        """Get current state description for shortcode."""
        return DESK_STATES.get(self.desk_state, DESK_STATES["cluttered"])
    
    def set_state(self, new_state: str) -> tuple[bool, str]:
        """Set desk state manually."""
        if new_state not in DESK_STATES:
            return (False, f"Invalid state. Options: {', '.join(DESK_STATES.keys())}")
        
        self.desk_state = new_state
        return (True, f"The desk is now {new_state}.")
    
    def soil(self) -> str:
        """Make the desk messier (called after activity)."""
        current_idx = DESK_STATE_ORDER.index(self.desk_state)
        
        if current_idx < len(DESK_STATE_ORDER) - 1:
            self.desk_state = DESK_STATE_ORDER[current_idx + 1]
            return f"The desk becomes {self.desk_state}."
        else:
            return "The desk can't get any messier."
    
    def clean(self) -> str:
        """Clean the desk one step."""
        current_idx = DESK_STATE_ORDER.index(self.desk_state)
        
        if current_idx > 0:
            self.desk_state = DESK_STATE_ORDER[current_idx - 1]
            return f"You clean up a bit. The desk is now {self.desk_state}."
        else:
            return "The desk is already clean."
    
    def clean_fully(self) -> str:
        """Clean the desk completely."""
        self.desk_state = "clean"
        return "You thoroughly clean the desk. It's spotless now."
    
    # -------------------------------------------------------------------------
    # Note System (AuriasJournal pattern)
    # -------------------------------------------------------------------------
    
    def add_note(self, author, message: str) -> bool:
        """
        Add a note to the desk.
        
        Args:
            author: Character writing the note
            message: The note content
        
        Returns:
            Success boolean
        """
        note = {
            "author": getattr(author, 'key', str(author)),
            "author_id": getattr(author, 'id', None),
            "message": message,
            "timestamp": datetime.now().isoformat(),
        }
        
        notes = list(self.notes)
        notes.append(note)
        
        # Trim if over max
        if len(notes) > self.max_notes:
            notes = notes[-self.max_notes:]
        
        self.notes = notes
        return True
    
    def get_notes(self, count: int = 5) -> List[Dict]:
        """Get the most recent notes."""
        notes = list(self.notes)
        return notes[-count:] if notes else []
    
    def format_note(self, note: Dict) -> str:
        """Format a single note for display."""
        author = note.get("author", "Unknown")
        message = note.get("message", "")
        return f"|y{author}|n wrote:\n  {message}"
    
    def read_notes(self) -> str:
        """Get formatted display of recent notes."""
        notes = self.get_notes(5)
        
        if not notes:
            return "No notes on the desk."
        
        parts = [
            "|wNotes scattered on the desk:|n",
            "─" * 30,
        ]
        
        for note in notes:
            parts.append(self.format_note(note))
            parts.append("")
        
        return "\n".join(parts)
    
    # -------------------------------------------------------------------------
    # Appearance
    # -------------------------------------------------------------------------
    
    def return_appearance(self, looker, **kwargs):
        """Show the desk with state and notes."""
        parts = [f"|w{self.key}|n", ""]
        parts.append(self.db.desc)
        
        # Current state
        parts.append("")
        parts.append(f"|xCurrent state: {self.get_state_desc()}|n")
        
        # Show who's using it
        if hasattr(self, 'current_users') and self.current_users:
            parts.append("")
            parts.append(self.get_occupied_desc())
        
        # Show recent notes if any
        if self.notes:
            parts.append("")
            parts.append(self.read_notes())
        
        parts.append("")
        parts.append("|wCommands: desk write <text>, desk read, desk clean, desk soil|n")
        
        return "\n".join(parts)


# =============================================================================
# LIVING BOOKSHELVES TYPECLASS
# =============================================================================

class LivingBookshelves(Container):
    """
    Bookshelves formed from living wood, rooted into the loamy earth.
    
    Features:
    - Browsable genre sections
    - Can hold WritableBook objects
    - Living wood aesthetic
    """
    
    portable = AttributeProperty(default=False)
    weight = AttributeProperty(default="immovable")
    is_open = AttributeProperty(default=True)
    
    # Genre sections (flavor text, not actual containers)
    sections = AttributeProperty(default={
        "grimoires": (
            "Ancient tomes bound in leather and stranger materials. Spell "
            "formulae, ritual instructions, magical theory. Some pages shimmer. "
            "Some are best not read aloud."
        ),
        "science": (
            "Factual tomes spanning centuries. Biology, chemistry, physics. "
            "Historical accounts from many worlds. Reference material for the "
            "curious mind."
        ),
        "fiction": (
            "Tales of elegance, adventures, romances. Stories to lose yourself "
            "in. Novels of debauchery mixed with fairy tales. Something for "
            "every taste."
        ),
        "hentai": (
            "An entire section dedicated to My Little Pony hentai. The collection "
            "is... comprehensive. Extensive. Suspiciously well-organized.\n\n"
            "For unknown reasons."
        ),
    })
    
    max_books = AttributeProperty(default=100)
    
    def at_object_creation(self):
        """Initialize the bookshelves."""
        super().at_object_creation()
        
        self.db.desc = (
            "Tall and sturdy book shelves formed by living woods, rooted into "
            "a rich floor of dark and loamy earth. The greens and vibrant "
            "yellows, whites, and baby blues of vine and flowers grow between "
            "the spines. The wood breathes slowly, growing imperceptibly, "
            "cradling knowledge in its embrace.\n\n"
            "The living shelves hold many old and modern tomes: Magical "
            "grimoires, books of science and history, fact and fiction, tales "
            "of elegance, novels of debauchery, fairy tales and hentai."
        )
        
        self.aliases.add("shelves")
        self.aliases.add("bookshelves")
        self.aliases.add("book shelves")
        self.aliases.add("bookcase")
    
    def get_section(self, section_name: str) -> Optional[str]:
        """Get description of a specific section."""
        section_name = section_name.lower()
        
        # Handle aliases
        aliases = {
            "magic": "grimoires",
            "magical": "grimoires",
            "spells": "grimoires",
            "history": "science",
            "reference": "science",
            "stories": "fiction",
            "novels": "fiction",
            "mlp": "hentai",
            "pony": "hentai",
            "ponies": "hentai",
        }
        
        section_name = aliases.get(section_name, section_name)
        return self.sections.get(section_name)
    
    def list_sections(self) -> str:
        """List available sections."""
        return ", ".join(self.sections.keys())
    
    def return_appearance(self, looker, **kwargs):
        """Show bookshelves with sections."""
        parts = [f"|w{self.key}|n", ""]
        parts.append(self.db.desc)
        
        parts.append("")
        parts.append("|wBrowsable sections:|n")
        for section_name in self.sections.keys():
            parts.append(f"  |c{section_name}|n")
        
        parts.append("")
        parts.append("|wUse 'browse <section>' to examine a section.|n")
        
        # Show any player books shelved here
        player_books = [obj for obj in self.contents if hasattr(obj, 'book_title')]
        if player_books:
            parts.append("")
            parts.append("|wPlayer contributions:|n")
            for book in player_books[:10]:
                parts.append(f"  '{book.book_title}' by {book.author}")
        
        return "\n".join(parts)


# =============================================================================
# MLP HENTAI SECTION (Separate viewable for emphasis)
# =============================================================================

class MLPHentaiSection(Object):
    """
    The MLP hentai section. For unknown reasons.
    """
    
    portable = AttributeProperty(default=False)
    
    def at_object_creation(self):
        """Initialize."""
        super().at_object_creation()
        
        self.db.desc = (
            "One section of the living bookshelves is completely dedicated to "
            "My Little Pony hentai. For unknown reasons."
        )
        
        self.aliases.add("mlp section")
        self.aliases.add("mlp hentai")
        self.aliases.add("pony section")
        self.aliases.add("hentai section")
    
    def return_appearance(self, looker, **kwargs):
        """Examine the section in detail."""
        return (
            "|wMy Little Pony Hentai Section|n\n\n"
            "An entire section of the living shelves is dedicated to My Little "
            "Pony hentai. The collection is... comprehensive. Extensive. "
            "Suspiciously well-organized.\n\n"
            "For unknown reasons.\n\n"
            "|xThe vines around this section seem slightly embarrassed.|n"
        )


# =============================================================================
# LIVING FLORA TYPECLASS
# =============================================================================

class LivingFlora(Object):
    """
    The vines and flowers that respond to presence.
    Fae-touched, alive, aware.
    """
    
    portable = AttributeProperty(default=False)
    
    # Ambient responses
    responses = AttributeProperty(default=[
        "A vine brushes gently against your arm as you pass.",
        "Flowers turn slightly toward you, as if curious.",
        "Leaves rustle in welcome, though there's no wind.",
        "A bloom opens as you approach, then slowly closes.",
        "The vines seem to shift, making a path for you.",
    ])
    
    def at_object_creation(self):
        """Initialize the flora."""
        super().at_object_creation()
        
        self.db.desc = (
            "Vines and flowers adorn the space—greens and vibrant yellows, "
            "whites, and baby blues. They grow naturally, cared for by fae "
            "touch, adding life to the living library."
        )
        
        self.aliases.add("vines")
        self.aliases.add("flowers")
        self.aliases.add("flora")
        self.aliases.add("plants")
    
    def return_appearance(self, looker, **kwargs):
        """Detailed examination reveals they're alive."""
        return (
            "|wVines and Flowers|n\n\n"
            "Vines and flowers adorn the space—greens and vibrant yellows, "
            "whites, and baby blues. They grow naturally, cared for by fae "
            "touch, adding life to the living library.\n\n"
            "|mOn closer look:|n\n"
            "The flowers aren't just decorative—they respond subtly to "
            "presence. Blooms turn toward readers, leaves rustle in welcome, "
            "vines occasionally brush against skin like gentle curiosity. "
            "This isn't a garden. It's alive, and it knows you're here."
        )
    
    def ambient_response(self, character):
        """Send an ambient message about flora responding."""
        if not self.location:
            return
        
        response = random.choice(self.responses)
        character.msg(f"|m{response}|n")


# =============================================================================
# BEANBAG CHAIR
# =============================================================================

class GardenBeanbag(Furniture):
    """
    The bright pink beanbag chair behind the desk.
    Oreo's favorite reading spot.
    """
    
    portable = AttributeProperty(default=False)
    weight = AttributeProperty(default="heavy")
    
    capacity = AttributeProperty(default=2)
    position_slots = AttributeProperty(default=[
        "lounging", "curled up", "cuddling", "lap sitting"
    ])
    position_descs = AttributeProperty(default={
        "lounging": "{name} is sunk into the pink beanbag, comfortable.",
        "curled up": "{name} is curled up in the beanbag, reading.",
        "cuddling": "{name} is cuddled up with someone in the beanbag.",
        "lap sitting": "{name} sits in someone's lap in the beanbag.",
    })
    comfort = AttributeProperty(default="luxurious")
    
    def at_object_creation(self):
        """Initialize the beanbag."""
        super().at_object_creation()
        
        self.db.desc = (
            "A plush beanbag chair of bright pink sits behind the root desk. "
            "It conforms perfectly to whoever sinks into it. The fabric is "
            "soft, well-loved—this is Oreo's favorite spot for reading, "
            "coloring, and other activities."
        )
        
        self.aliases.add("beanbag")
        self.aliases.add("bean bag")
        self.aliases.add("chair")
        self.aliases.add("pink beanbag")


# =============================================================================
# BUILD FUNCTION
# =============================================================================

def build():
    """Build the Garden of Knowledge with all objects and connections."""
    
    # Find Passageway (should exist)
    passageway = search_object("Passageway")
    if passageway:
        passageway = passageway[0]
    else:
        print("WARNING: Passageway not found. Exit will point to Limbo.")
        passageway = None
    
    # Create the Garden Room
    room = create_object(GardenRoom, key="Garden of Knowledge")
    
    room.db.desc = """Here lies a veritable garden of inexplicable and fantastical tomes of knowledge, fantasy, and entertainment.

A large, brightly colored room of deep purples and oranges, lush pinks and violets sprawls on for a seemingly endless eternity to mimic the fading light of a glorious sunset. The fantastical palette only broken up and by tall and sturdy |cbook shelves|n formed by living woods rooted into a rich floor of dark and loamy earth, the greens and vibrant yellows, whites, and baby blues of |cvine and flowers|n adorning the space.

Careful and painstaking attention to the cultivation and growth forms this mythical grove, the loving and dedicated touch of the resident and proudly owned fae affectionately nicknamed 'Oreo' by her Mistress.

The living shelves hold many old and modern tomes: Magical grimoires, books of science and history, fact and fiction, tales of elegance, novels of debauchery, fairy tales and hentai.

One such section is completely dedicated to |cMy Little Pony hentai|n for unknown reasons.

At the room's center, like the court surrounding a prized water feature in a garden, roots twist and weave to form a sturdy |cdesk|n for the attending fae to work, and read in peace— <desk.state>. A plush |cbeanbag chair|n of bright pink sits behind it, the surrounding earth littered with |cstuffed animals|n and |ccoloring books|n.

<time.desc>"""
    
    # -------------------------------------------------------------------------
    # EXITS
    # -------------------------------------------------------------------------
    
    # Get Limbo as fallback
    limbo = search_object("#2")
    limbo = limbo[0] if limbo else None
    
    # Exit to Passageway
    exit_out = create_object(
        "evennia.objects.objects.DefaultExit",
        key="out",
        location=room,
        destination=passageway or limbo,
        aliases=["west", "w", "passageway", "door"],
    )
    exit_out.db.desc = (
        "A door on the western wall, its frame wrapped in vines that extend "
        "from the living bookshelves. Beyond lies the Passageway—the main "
        "hallway of the cabin. The transition from eternal sunset to mundane "
        "lighting is always a bit disorienting."
    )
    
    # Exit to Hidden Laboratory (placeholder for now)
    exit_lab = create_object(
        "evennia.objects.objects.DefaultExit",
        key="east",
        location=room,
        destination=limbo,
        aliases=["e", "laboratory", "lab"],
    )
    exit_lab.db.desc = (
        "The passage east returns to the cold, clinical laboratory. The "
        "contrast is jarring—from living sunset grove to sterile tiles and "
        "steel. Two sides of Helena's interests, side by side."
    )
    
    # Update Passageway exit to point here if it exists
    if passageway:
        for exit_obj in passageway.exits:
            if exit_obj.key == "east1":
                exit_obj.destination = room
                print(f"Updated Passageway exit 'east1' to point to Garden of Knowledge")
                break
    
    # -------------------------------------------------------------------------
    # FURNITURE
    # -------------------------------------------------------------------------
    
    # Root Desk
    desk = create_object(RootDesk, key="root desk", location=room)
    
    # Beanbag Chair
    beanbag = create_object(GardenBeanbag, key="beanbag chair", location=room)
    
    # -------------------------------------------------------------------------
    # CONTAINERS
    # -------------------------------------------------------------------------
    
    # Living Bookshelves
    shelves = create_object(LivingBookshelves, key="living book shelves", location=room)
    
    # -------------------------------------------------------------------------
    # OBJECTS
    # -------------------------------------------------------------------------
    
    # MLP Hentai Section (separate viewable)
    mlp = create_object(MLPHentaiSection, key="MLP hentai section", location=room)
    
    # Living Flora
    flora = create_object(LivingFlora, key="vine and flowers", location=room)
    
    # Stuffed Animals
    stuffies = create_object(Object, key="stuffed animals", location=room,
                            aliases=["stuffies", "plushies"])
    stuffies.db.desc = (
        "Stuffed animals of various sizes and types are scattered across the "
        "loamy earth—dragons, unicorns, wolves, and things less identifiable. "
        "They're well-loved, some showing wear from hugging. Oreo's companions "
        "for reading and coloring."
    )
    stuffies.portable = False
    
    # Coloring Books
    coloring = create_object(Object, key="coloring books", location=room,
                            aliases=["coloring", "books"])
    coloring.db.desc = (
        "Coloring books lie scattered about, some open to half-finished pages. "
        "The art ranges from simple mandalas to elaborate fantasy scenes. "
        "Crayons and colored pencils are tucked nearby. The pages show skill "
        "and care—whoever colors these takes their time."
    )
    coloring.portable = False
    
    # Loamy Earth Floor
    floor = create_object(Object, key="loamy earth", location=room,
                         aliases=["floor", "earth", "soil", "ground"])
    floor.db.desc = (
        "The floor is actual earth—rich, dark, loamy soil that the living "
        "bookshelves root into. It's soft underfoot, smelling of growth and "
        "life. Small plants peek up here and there. You could dig your toes "
        "in if you wanted."
    )
    floor.portable = False
    
    # -------------------------------------------------------------------------
    # SEED INITIAL NOTES
    # -------------------------------------------------------------------------
    
    _seed_desk_notes(desk)
    
    # -------------------------------------------------------------------------
    # OUTPUT
    # -------------------------------------------------------------------------
    
    print(f"Built Garden of Knowledge: {room.dbref}")
    if passageway:
        print(f"Connected to Passageway: {passageway.dbref}")
    print(f"")
    print(f"Exits:")
    print(f"  out/west → Passageway")
    print(f"  east → Hidden Laboratory (placeholder)")
    print(f"")
    print(f"Furniture:")
    print(f"  root desk (state system, notes, positions, restraints)")
    print(f"  beanbag chair (capacity 2)")
    print(f"")
    print(f"Containers:")
    print(f"  living book shelves (browsable sections)")
    print(f"")
    print(f"Objects:")
    print(f"  MLP hentai section, vine and flowers, stuffed animals,")
    print(f"  coloring books, loamy earth")
    print(f"")
    print(f"Test with:")
    print(f"  @py from world.build_garden_knowledge import test_sunset; test_sunset()")
    print(f"  @py from world.build_garden_knowledge import test_desk; test_desk()")
    print(f"  @py from world.build_garden_knowledge import test_notes; test_notes()")
    
    return room


def _seed_desk_notes(desk):
    """Add starter notes to the desk."""
    
    class FakeAuthor:
        key = "Oreo"
        id = None
    
    desk.add_note(
        FakeAuthor(),
        "Studying transmutation theory. The grimoire on page 47 is WRONG "
        "about elemental balance. I fixed it in the margins. You're welcome."
    )
    
    FakeAuthor.key = "Helena"
    desk.add_note(
        FakeAuthor(),
        "Little one. Stop drawing ponies in the grimoires. Use the coloring "
        "books.\n\n    ♥ Mistress"
    )
    
    FakeAuthor.key = "Oreo"
    desk.add_note(
        FakeAuthor(),
        "The ponies IMPROVE the grimoires. This is a scholarly contribution."
    )


# =============================================================================
# TEST FUNCTIONS
# =============================================================================

def get_garden():
    """Find the Garden of Knowledge."""
    results = search_object("Garden of Knowledge")
    return results[0] if results else None


def test_sunset():
    """Test all sunset phases."""
    room = get_garden()
    if not room:
        return "Garden of Knowledge not found."
    
    print("=== SUNSET PHASES ===\n")
    for phase, desc in SUNSET_PHASES.items():
        print(f"{phase.upper()}:")
        print(f"  {desc}")
        print()
    
    print(f"Current phase: {room.get_sunset_phase()}")
    return room


def test_desk():
    """Test desk state system."""
    room = get_garden()
    if not room:
        return "Garden of Knowledge not found."
    
    desk = room.get_desk()
    if not desk:
        return "Desk not found."
    
    print("=== DESK STATE TEST ===\n")
    print(f"Current state: {desk.desk_state}")
    print(f"Description: {desk.get_state_desc()}")
    print()
    
    print("Testing state changes:")
    print(f"  soil() -> {desk.soil()}")
    print(f"  State now: {desk.desk_state}")
    print(f"  clean() -> {desk.clean()}")
    print(f"  State now: {desk.desk_state}")
    
    return desk


def test_notes():
    """Test desk note system."""
    room = get_garden()
    if not room:
        return "Garden of Knowledge not found."
    
    desk = room.get_desk()
    if not desk:
        return "Desk not found."
    
    print("=== DESK NOTES TEST ===\n")
    print(desk.read_notes())
    
    return desk


def test_flora():
    """Test living flora responses."""
    room = get_garden()
    if not room:
        return "Garden of Knowledge not found."
    
    flora = None
    for obj in room.contents:
        if isinstance(obj, LivingFlora):
            flora = obj
            break
    
    if not flora:
        return "Flora not found."
    
    print("=== LIVING FLORA TEST ===\n")
    print("Possible ambient responses:")
    for response in flora.responses:
        print(f"  - {response}")
    
    return flora


def test_shelves():
    """Test bookshelf sections."""
    room = get_garden()
    if not room:
        return "Garden of Knowledge not found."
    
    shelves = None
    for obj in room.contents:
        if isinstance(obj, LivingBookshelves):
            shelves = obj
            break
    
    if not shelves:
        return "Bookshelves not found."
    
    print("=== BOOKSHELF SECTIONS ===\n")
    for section_name, desc in shelves.sections.items():
        print(f"{section_name.upper()}:")
        print(f"  {desc}")
        print()
    
    return shelves
