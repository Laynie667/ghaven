"""
Auria's Room Objects - The things that make the room alive.

Place in: typeclasses/objects/aurias_objects.py

Objects:
- LivingEevee - A creature disguised as a stuffed animal
- AuriasJournal - A book where family leaves messages  
- AuriaPillowNest - The pillow nest with chains (adult furniture)
- AuriaBed - The bed covered in stuffies
- AuriaCollar - Her collar, hanging empty
- AuriaBookcase - The little free library
- AuriaTrunk - Mysterious locked container
- AuriaWardrobe - Slightly ajar wardrobe
"""

from typing import Optional, Dict, List, Any
import random
from datetime import datetime

try:
    from evennia.typeclasses.attributes import AttributeProperty
except (ImportError, TypeError, AttributeError):
    def AttributeProperty(default=None, **kwargs):
        return default

from typeclasses.objects import Object, Furniture, Container


# =============================================================================
# LIVING EEVEE
# =============================================================================

EEVEE_AMBIENT_TELLS = [
    "The Eevee's ear twitches. Stuffed animals don't do that.",
    "You could swear the Eevee just blinked.",
    "The Eevee seems to have shifted position when you weren't looking.",
    "A soft sound—almost like a purr—comes from the bed.",
    "The Eevee's tail curls slightly. Very slightly.",
    "Was the Eevee always facing this direction?",
    "The Eevee's nose twitches. Testing the air? Impossible.",
    "For just a moment, you feel watched. The Eevee stares back.",
]

EEVEE_REVEALED_BEHAVIORS = [
    "stretches luxuriously, very much alive",
    "watches you with warm, knowing eyes", 
    "flicks an ear in your direction",
    "yawns, showing small sharp teeth",
    "curls tighter, tail over nose",
    "makes a soft chirping sound",
]


class LivingEevee(Object):
    """
    A creature disguised as a stuffed animal.
    
    The Eevee appears to be a normal plush toy until certain conditions
    are met. Then she reveals herself—warm, soft, very much alive, and
    with certain... capabilities.
    
    Features:
    - Disguise state (appears as stuffed animal until revealed)
    - Ambient tells (subtle hints she's alive)
    - Family recognition (reveals more readily to family)
    - Adult scene capabilities (knotting, dragging mechanic)
    - Warm and affectionate personality
    """
    
    # -------------------------------------------------------------------------
    # Base Properties
    # -------------------------------------------------------------------------
    
    # Override defaults
    portable = AttributeProperty(default=False)  # Can't just pick her up
    weight = AttributeProperty(default="light")
    size = AttributeProperty(default="small")
    
    # -------------------------------------------------------------------------
    # Disguise State
    # -------------------------------------------------------------------------
    
    is_revealed = AttributeProperty(default=False)
    reveal_to = AttributeProperty(default=list)  # List of character IDs she's revealed to
    
    # Who she reveals to automatically
    auto_reveal_keys = AttributeProperty(default=["Helena", "Laynie", "Auria", "Shadow"])
    
    # -------------------------------------------------------------------------
    # Creature Properties
    # -------------------------------------------------------------------------
    
    creature_name = AttributeProperty(default="Eevee")
    creature_mood = AttributeProperty(default="sleepy")  # sleepy, curious, playful, amorous
    
    # Adult properties
    is_in_scene = AttributeProperty(default=False)
    scene_partner_id = AttributeProperty(default=None)
    is_knotted = AttributeProperty(default=False)
    knot_partner_id = AttributeProperty(default=None)
    
    # -------------------------------------------------------------------------
    # Descriptions
    # -------------------------------------------------------------------------
    
    stuffed_desc = AttributeProperty(default=(
        "A plush Eevee sits among the other stuffed animals, brown fur soft "
        "and well-loved. Glass eyes catch the light. It's clearly been hugged "
        "many times—the fur is worn in places, one ear slightly bent. "
        "Auria's favorite."
    ))
    
    revealed_desc = AttributeProperty(default=(
        "The Eevee watches you with warm, living eyes—definitely not glass. "
        "Her fur rises and falls with breath. Her tail curls and uncurls "
        "lazily. She's small, soft, warm, and very much alive. How long "
        "has she been like this? Has she always been?"
    ))
    
    # -------------------------------------------------------------------------
    # Setup
    # -------------------------------------------------------------------------
    
    def at_object_creation(self):
        """Initialize the Eevee."""
        super().at_object_creation()
        
        self.db.desc = self.stuffed_desc
        
        # Set up aliases
        self.aliases.add("eevee")
        self.aliases.add("stuffed eevee")
        self.aliases.add("plush")
        self.aliases.add("stuffed animal")
    
    # -------------------------------------------------------------------------
    # Reveal Mechanics
    # -------------------------------------------------------------------------
    
    def should_auto_reveal(self, character) -> bool:
        """Check if Eevee should auto-reveal to this character."""
        if not character:
            return False
        char_key = getattr(character, 'key', str(character))
        return char_key in self.auto_reveal_keys
    
    def reveal_to_character(self, character):
        """Reveal to a specific character."""
        if not character:
            return
        
        char_id = character.id
        revealed_list = list(self.reveal_to)
        
        if char_id not in revealed_list:
            revealed_list.append(char_id)
            self.reveal_to = revealed_list
        
        self.is_revealed = True
    
    def is_revealed_to(self, character) -> bool:
        """Check if revealed to this character."""
        if not character:
            return False
        
        # Auto-reveal to family
        if self.should_auto_reveal(character):
            self.reveal_to_character(character)
            return True
        
        return character.id in self.reveal_to
    
    def get_reveal_message(self, character) -> str:
        """Get the message when Eevee reveals herself."""
        char_key = getattr(character, 'key', 'stranger')
        
        if char_key == "Auria":
            return (
                "The Eevee's ears perk up. Her tail wags. She launches herself "
                "at you with a joyful cry, nuzzling against you desperately. "
                "She's been waiting. She's been |ywaiting|n."
            )
        elif char_key in ["Helena", "Laynie", "Shadow"]:
            return (
                "The Eevee stretches, yawns, and looks at you with warm "
                "recognition. Her tail wags slowly. Family. She chirps a "
                "greeting and settles back down, content that you're here."
            )
        else:
            return (
                "The stuffed Eevee... moves. Stretches. Blinks. Looks at you "
                "with eyes that are definitely not glass. She tilts her head, "
                "studying you, then makes a soft curious sound. Not a toy. "
                "Not a toy at all."
            )
    
    # -------------------------------------------------------------------------
    # Ambient Behavior
    # -------------------------------------------------------------------------
    
    def get_ambient_tell(self) -> Optional[str]:
        """Get a subtle hint that she's alive (when not revealed)."""
        if self.is_revealed:
            return f"The Eevee {random.choice(EEVEE_REVEALED_BEHAVIORS)}."
        
        if random.random() < 0.2:  # 20% chance
            return random.choice(EEVEE_AMBIENT_TELLS)
        return None
    
    def trigger_ambient(self):
        """Send an ambient tell to the room."""
        if not self.location:
            return
        
        tell = self.get_ambient_tell()
        if tell:
            self.location.msg_contents(f"|m{tell}|n")
    
    # -------------------------------------------------------------------------
    # Appearance
    # -------------------------------------------------------------------------
    
    def return_appearance(self, looker=None, **kwargs):
        """Return appearance based on reveal state."""
        parts = [f"|w{self.key}|n", ""]
        
        if self.is_revealed_to(looker):
            parts.append(self.revealed_desc)
            
            # Add mood-based extra
            mood_extras = {
                "sleepy": "She seems drowsy, curled up and content.",
                "curious": "Her ears are perked, watching everything with interest.",
                "playful": "Her tail swishes. She looks like she wants to play.",
                "amorous": "There's something in her gaze. Warm. Inviting. Hungry.",
            }
            if self.creature_mood in mood_extras:
                parts.append("")
                parts.append(mood_extras[self.creature_mood])
        else:
            parts.append(self.stuffed_desc)
            
            # Maybe add a subtle tell
            tell = self.get_ambient_tell()
            if tell:
                parts.append("")
                parts.append(f"|m{tell}|n")
        
        return "\n".join(parts)
    
    # -------------------------------------------------------------------------
    # Interaction: Pet
    # -------------------------------------------------------------------------
    
    def pet(self, petter) -> str:
        """Someone pets the Eevee."""
        if not self.is_revealed_to(petter):
            # First contact might trigger reveal
            if random.random() < 0.4 or self.should_auto_reveal(petter):
                self.reveal_to_character(petter)
                return self.get_reveal_message(petter)
            else:
                return (
                    "You pet the stuffed Eevee. The fur is incredibly soft—softer "
                    "than any plush should be. Warm, too. Almost like..."
                    "\n\nNo. It's just a stuffed animal."
                )
        else:
            responses = [
                "The Eevee leans into your touch, making a sound of pure contentment.",
                "She chirps happily, tail wagging as you pet her.",
                "Her eyes half-close in pleasure. Soft. So soft.",
                "She nuzzles your hand, warm and affectionate.",
            ]
            
            if self.creature_mood == "amorous":
                responses.append(
                    "She presses against your hand insistently, making a sound "
                    "that's definitely not innocent."
                )
            
            return random.choice(responses)
    
    # -------------------------------------------------------------------------
    # Interaction: Pick Up (Blocked)
    # -------------------------------------------------------------------------
    
    def at_pre_get(self, getter, **kwargs):
        """Called before someone tries to pick her up."""
        if self.is_revealed_to(getter):
            getter.msg(
                "The Eevee gives you a look that clearly says 'I go where I "
                "want to go.' She's not a toy to be carried."
            )
        else:
            getter.msg(
                "As your hand closes around the Eevee, you feel... resistance? "
                "Warmth? Something makes you let go. Weird."
            )
        return False  # Block the get
    
    # -------------------------------------------------------------------------
    # Scene Mechanics (Adult)
    # -------------------------------------------------------------------------
    
    def start_scene(self, partner) -> str:
        """Initiate an adult scene."""
        if self.is_in_scene:
            return "The Eevee is already... occupied."
        
        if not self.is_revealed_to(partner):
            self.reveal_to_character(partner)
            return (
                self.get_reveal_message(partner) + 
                "\n\nShe looks at you with unmistakable intent. This is happening."
            )
        
        self.is_in_scene = True
        self.scene_partner_id = partner.id
        self.creature_mood = "amorous"
        
        return (
            "The Eevee's demeanor shifts. Her movements become deliberate, "
            "sinuous. She approaches you with clear purpose, and you realize "
            "this small, soft creature has plans for you."
        )
    
    def knot(self, partner) -> str:
        """
        Knot mechanic - locks Eevee to partner.
        While knotted, neither can move independently.
        """
        if not self.is_in_scene or self.scene_partner_id != partner.id:
            return "You're not in a position for that."
        
        if self.is_knotted:
            return "Already locked together. You're not going anywhere."
        
        self.is_knotted = True
        self.knot_partner_id = partner.id
        
        return (
            "The Eevee swells inside you, locking tight. You gasp—there's no "
            "separating now, not until she's ready. Her tail wags slowly, "
            "satisfied. You're hers until she says otherwise."
        )
    
    def unknot(self) -> str:
        """Release the knot."""
        if not self.is_knotted:
            return "Not currently knotted."
        
        self.is_knotted = False
        self.knot_partner_id = None
        
        return (
            "Slowly, the swelling subsides. The Eevee slides free with a wet "
            "sound, leaving you gasping and empty. She looks smug."
        )
    
    def drag_to(self, destination, dragger=None) -> str:
        """
        The dragging mechanic - while knotted, Eevee can drag her partner.
        
        This is for exhibition/humiliation play. The knotted partner is
        pulled through rooms on display.
        """
        if not self.is_knotted:
            return "She's not attached to anyone to drag."
        
        # Find the knotted partner
        partner = None
        if self.location:
            for obj in self.location.contents:
                if hasattr(obj, 'id') and obj.id == self.knot_partner_id:
                    partner = obj
                    break
        
        if not partner:
            self.is_knotted = False
            self.knot_partner_id = None
            return "The partner seems to have vanished. Knot released."
        
        # Move both Eevee and partner
        old_location = self.location
        
        # Announce departure
        if old_location:
            old_location.msg_contents(
                f"The Eevee begins walking toward the exit, and {partner.key} "
                f"has no choice but to follow—still locked together, stumbling "
                f"along behind. On display. Helpless.",
                exclude=[partner]
            )
            partner.msg(
                "The Eevee starts walking and you |yhave|n to follow. The knot "
                "pulls at you with every step. Everyone can see. Everyone knows."
            )
        
        # Actually move
        self.move_to(destination, quiet=True)
        partner.move_to(destination, quiet=True)
        
        # Announce arrival
        if destination:
            destination.msg_contents(
                f"The Eevee trots in, tail high. Behind her, connected in an "
                f"unmistakable way, {partner.key} stumbles along—flushed, "
                f"helpless, on display.",
                exclude=[partner]
            )
            partner.msg(
                "You're dragged into the room, still knotted, still |yfull|n. "
                "Everyone here can see exactly what's happening."
            )
        
        return "She drags you along like it's nothing. Because to her, it is."
    
    def end_scene(self) -> str:
        """End the current scene."""
        if self.is_knotted:
            self.unknot()
        
        self.is_in_scene = False
        self.scene_partner_id = None
        self.creature_mood = "sleepy"
        
        return (
            "The Eevee stretches, yawns, and curls up contentedly. Whatever "
            "just happened, she seems satisfied. She's already falling asleep."
        )


# =============================================================================
# AURIA'S JOURNAL
# =============================================================================

class AuriasJournal(Object):
    """
    A journal where family can leave messages for Auria.
    
    Features:
    - Writeable book system
    - Stores entries with author and timestamp
    - Special formatting for family messages
    - Ambient reactions when written in
    """
    
    # -------------------------------------------------------------------------
    # Properties
    # -------------------------------------------------------------------------
    
    portable = AttributeProperty(default=False)  # Stays in the room
    weight = AttributeProperty(default="light")
    
    # Entries stored as list of dicts
    entries = AttributeProperty(default=list)
    max_entries = AttributeProperty(default=50)
    
    # Who can write (empty = anyone)
    allowed_writers = AttributeProperty(default=list)
    
    # -------------------------------------------------------------------------
    # Setup
    # -------------------------------------------------------------------------
    
    def at_object_creation(self):
        """Initialize the journal."""
        super().at_object_creation()
        
        self.db.desc = (
            "A leather-bound journal lies open on the small table, a pen "
            "beside it. The pages are filled with different handwriting—"
            "messages from family, notes of love and longing. A ribbon "
            "marks the current page. The leather is worn from handling."
        )
        
        self.aliases.add("journal")
        self.aliases.add("book")
        self.aliases.add("diary")
    
    # -------------------------------------------------------------------------
    # Entry Management
    # -------------------------------------------------------------------------
    
    def add_entry(self, author, message: str, entry_type: str = "message") -> bool:
        """
        Add an entry to the journal.
        
        Args:
            author: Character writing the entry
            message: The message content
            entry_type: Type of entry (message, drawing, pressed_flower, etc.)
        
        Returns:
            Success boolean
        """
        # Check permissions
        if self.allowed_writers:
            author_key = getattr(author, 'key', str(author))
            if author_key not in self.allowed_writers:
                return False
        
        # Build entry
        entry = {
            "author": getattr(author, 'key', str(author)),
            "author_id": getattr(author, 'id', None),
            "message": message,
            "type": entry_type,
            "timestamp": datetime.now().isoformat(),
        }
        
        # Add to entries
        entries = list(self.entries)
        entries.append(entry)
        
        # Trim if over max
        if len(entries) > self.max_entries:
            entries = entries[-self.max_entries:]
        
        self.entries = entries
        
        # Trigger post-write hook
        self.at_after_write(author)
        
        return True
    
    def get_entries(self, count: int = 10) -> List[Dict]:
        """Get the most recent entries."""
        entries = list(self.entries)
        return entries[-count:] if entries else []
    
    def format_entry(self, entry: Dict) -> str:
        """Format a single entry for display."""
        author = entry.get("author", "Unknown")
        message = entry.get("message", "")
        entry_type = entry.get("type", "message")
        
        if entry_type == "drawing":
            return f"|y{author}|n drew something here:\n  {message}"
        elif entry_type == "pressed_flower":
            return f"|y{author}|n pressed a flower here.\n  {message}"
        else:
            return f"|y{author}|n wrote:\n  {message}"
    
    # -------------------------------------------------------------------------
    # Appearance
    # -------------------------------------------------------------------------
    
    def return_appearance(self, looker=None, **kwargs):
        """Show the journal with recent entries."""
        parts = [
            f"|w{self.key}|n",
            "",
            self.db.desc,
            "",
            "═" * 40,
            "  |yRecent Entries|n",
            "═" * 40,
            "",
        ]
        
        entries = self.get_entries(5)
        if entries:
            for entry in entries:
                parts.append(self.format_entry(entry))
                parts.append("")
                parts.append("─" * 30)
                parts.append("")
        else:
            parts.append("The pages are blank, waiting for words.")
        
        parts.append("|wUse 'write <message>' to add an entry.|n")
        
        return "\n".join(parts)
    
    # -------------------------------------------------------------------------
    # Hooks
    # -------------------------------------------------------------------------
    
    def at_after_write(self, writer):
        """Called after someone writes in the journal."""
        if not self.location:
            return
        
        reactions = [
            "The Eevee on the bed seems to smile a little wider.",
            "A faint breeze rustles the pages, though there's no wind.",
            "The ink dries quickly, like the journal was thirsty for words.",
            "Somewhere, somehow, she knows you wrote.",
        ]
        
        self.location.msg_contents(
            f"|m{random.choice(reactions)}|n",
            exclude=[writer]
        )


# =============================================================================
# PILLOW NEST WITH CHAINS
# =============================================================================

class AuriaPillowNest(Furniture):
    """
    The pillow nest against the southern wall, with chains above.
    
    Adult furniture with bondage capability. Comfortable, safe,
    designed for a little who likes to feel held.
    """
    
    # -------------------------------------------------------------------------
    # Properties
    # -------------------------------------------------------------------------
    
    portable = AttributeProperty(default=False)
    weight = AttributeProperty(default="immovable")
    
    capacity = AttributeProperty(default=2)
    position_slots = AttributeProperty(default=["curl up in", "lie in", "kneel in", "sit in"])
    comfort = AttributeProperty(default="luxurious")
    
    # Bondage properties
    has_chains = AttributeProperty(default=True)
    chain_status = AttributeProperty(default="empty")  # empty, occupied
    chained_character_id = AttributeProperty(default=None)
    
    # -------------------------------------------------------------------------
    # Setup
    # -------------------------------------------------------------------------
    
    def at_object_creation(self):
        """Initialize the nest."""
        super().at_object_creation()
        
        self.db.desc = (
            "Cushions and pillows of all colours gathered into a nest against "
            "the southern wall. From the wall above hangs a set of chains, "
            "long enough for someone to curl up comfortably in the nest and "
            "ending in padded shackles, and a collar inscribed with 'Auria'."
        )
        
        self.aliases.add("nest")
        self.aliases.add("pillows")
        self.aliases.add("cushions")
        self.aliases.add("pillow nest")
        self.aliases.add("chains")
    
    # -------------------------------------------------------------------------
    # Chain Mechanics
    # -------------------------------------------------------------------------
    
    def chain_character(self, character) -> str:
        """Secure someone in the chains."""
        if self.chain_status == "occupied":
            return "The chains are already occupied."
        
        self.chain_status = "occupied"
        self.chained_character_id = character.id
        
        return (
            f"The padded cuffs close around {character.key}'s wrists with a "
            f"soft click. Secure but not painful. Held but not hurt. "
            f"The chains allow enough slack to curl up comfortably in the "
            f"pillows below—but not enough to leave."
        )
    
    def unchain_character(self, character=None) -> str:
        """Release someone from the chains."""
        if self.chain_status == "empty":
            return "The chains hang empty."
        
        self.chain_status = "empty"
        self.chained_character_id = None
        
        return (
            "The cuffs click open, releasing their hold. The chains swing "
            "gently, empty again."
        )
    
    def get_chained_character(self):
        """Get the character currently chained, if any."""
        if not self.chained_character_id or not self.location:
            return None
        
        for obj in self.location.contents:
            if hasattr(obj, 'id') and obj.id == self.chained_character_id:
                return obj
        return None
    
    # -------------------------------------------------------------------------
    # Appearance
    # -------------------------------------------------------------------------
    
    def return_appearance(self, looker=None, **kwargs):
        """Include chain status in description."""
        parts = [f"|w{self.key}|n", "", self.db.desc, ""]
        
        # Chain status
        chained = self.get_chained_character()
        if chained:
            parts.append(
                f"|y{chained.key}|n is secured in the chains above, curled "
                f"comfortably in the pillows below."
            )
        else:
            parts.append("The chains hang empty, waiting.")
        
        # Occupants
        if self.current_users:
            parts.append("")
            parts.append(self.get_occupied_desc())
        
        return "\n".join(parts)


# =============================================================================
# AURIA'S BED
# =============================================================================

class AuriaBed(Furniture):
    """
    The comfortable bed covered in stuffed animals.
    """
    
    capacity = AttributeProperty(default=2)
    position_slots = AttributeProperty(default=["lie on", "sit on", "curl up on"])
    comfort = AttributeProperty(default="luxurious")
    
    def at_object_creation(self):
        """Initialize the bed."""
        super().at_object_creation()
        
        self.db.desc = (
            "A comfy bed made up neatly with a pale purple bedspread. Perched "
            "in the center is a fluffy Eevee plushie, with a jumbled pile around "
            "her; a plush dragon in shades of purple, a Squirtle and Chikorita "
            "small enough to fit in a coat pocket and a happy look raccoon. "
            "The sheets smell clean. Someone maintains this."
        )
        
        self.aliases.add("bed")
        self.aliases.add("comfy bed")


# =============================================================================
# AURIA'S COLLAR
# =============================================================================

class AuriaCollar(Object):
    """
    Her collar, part of the chain setup above the nest.
    """
    
    portable = AttributeProperty(default=True)  # Can be taken down
    weight = AttributeProperty(default="light")
    
    # Collar properties
    owner_name = AttributeProperty(default="Auria")
    is_worn = AttributeProperty(default=False)
    worn_by_id = AttributeProperty(default=None)
    
    def at_object_creation(self):
        """Initialize the collar."""
        super().at_object_creation()
        
        self.db.desc = (
            "A soft leather collar hangs from the chains above the pillow "
            "nest, part of the restraint setup. The leather is well-worn, "
            "shaped by use, clearly beloved. Inscribed on it:\n\n"
            "  |y~* Auria *~|n\n\n"
            "It's waiting for her."
        )
        
        self.aliases.add("collar")
        self.aliases.add("auria's collar")


# =============================================================================
# BOOKCASE
# =============================================================================

class WritableBook(Object):
    """
    A book that can be written in, page by page.
    
    Players can create these, write in them, and place them on 
    Auria's bookshelf (or anywhere else).
    """
    
    portable = AttributeProperty(default=True)
    weight = AttributeProperty(default="light")
    
    # Book metadata
    book_title = AttributeProperty(default="Untitled")
    author = AttributeProperty(default="Anonymous")
    author_id = AttributeProperty(default=None)
    
    # Pages: list of strings, each string is one page
    pages = AttributeProperty(default=list)
    max_pages = AttributeProperty(default=20)
    chars_per_page = AttributeProperty(default=1000)
    
    # Current page being viewed
    current_page = AttributeProperty(default=0)
    
    # Is this book finished/locked?
    is_finished = AttributeProperty(default=False)
    
    def at_object_creation(self):
        """Initialize the book."""
        super().at_object_creation()
        self.pages = [""]  # Start with one blank page
        self.aliases.add("book")
    
    # -------------------------------------------------------------------------
    # Writing
    # -------------------------------------------------------------------------
    
    def set_title(self, title: str, setter=None) -> tuple[bool, str]:
        """Set the book's title."""
        if self.is_finished:
            return (False, "This book is finished and can't be changed.")
        
        if not title or len(title.strip()) < 1:
            return (False, "What do you want to call it?")
        
        self.book_title = title.strip()[:100]  # Cap title length
        self.key = self.book_title  # Update object name
        return (True, f"You title the book '{self.book_title}'.")
    
    def set_author(self, writer) -> None:
        """Set the author from a character."""
        self.author = getattr(writer, 'key', str(writer))
        self.author_id = getattr(writer, 'id', None)
    
    def write_page(self, text: str, page_num: int = None, writer=None) -> tuple[bool, str]:
        """
        Write to a page.
        
        Args:
            text: Content to write
            page_num: Page number (0-indexed), None = current page
            writer: Character writing
        
        Returns:
            (success, message)
        """
        if self.is_finished:
            return (False, "This book is finished and can't be changed.")
        
        if page_num is None:
            page_num = self.current_page
        
        if page_num < 0 or page_num >= len(self.pages):
            return (False, f"Page {page_num + 1} doesn't exist.")
        
        # Check length
        if len(text) > self.chars_per_page:
            return (False, f"Too long! Maximum {self.chars_per_page} characters per page.")
        
        pages = list(self.pages)
        pages[page_num] = text
        self.pages = pages
        
        return (True, f"You write on page {page_num + 1}.")
    
    def append_to_page(self, text: str, page_num: int = None, writer=None) -> tuple[bool, str]:
        """Append text to existing page content."""
        if self.is_finished:
            return (False, "This book is finished and can't be changed.")
        
        if page_num is None:
            page_num = self.current_page
        
        if page_num < 0 or page_num >= len(self.pages):
            return (False, f"Page {page_num + 1} doesn't exist.")
        
        current_content = self.pages[page_num]
        new_content = current_content + text if current_content else text
        
        if len(new_content) > self.chars_per_page:
            return (False, f"Page is full! Maximum {self.chars_per_page} characters.")
        
        pages = list(self.pages)
        pages[page_num] = new_content
        self.pages = pages
        
        return (True, f"You add to page {page_num + 1}.")
    
    def add_page(self) -> tuple[bool, str]:
        """Add a new blank page."""
        if self.is_finished:
            return (False, "This book is finished and can't be changed.")
        
        if len(self.pages) >= self.max_pages:
            return (False, f"This book can only hold {self.max_pages} pages.")
        
        pages = list(self.pages)
        pages.append("")
        self.pages = pages
        self.current_page = len(self.pages) - 1
        
        return (True, f"You add a new page. Now on page {self.current_page + 1}.")
    
    def remove_page(self, page_num: int = None) -> tuple[bool, str]:
        """Remove a page."""
        if self.is_finished:
            return (False, "This book is finished and can't be changed.")
        
        if len(self.pages) <= 1:
            return (False, "Can't remove the last page.")
        
        if page_num is None:
            page_num = self.current_page
        
        if page_num < 0 or page_num >= len(self.pages):
            return (False, f"Page {page_num + 1} doesn't exist.")
        
        pages = list(self.pages)
        pages.pop(page_num)
        self.pages = pages
        
        # Adjust current page if needed
        if self.current_page >= len(self.pages):
            self.current_page = len(self.pages) - 1
        
        return (True, f"You tear out page {page_num + 1}.")
    
    def finish_book(self, finisher=None) -> tuple[bool, str]:
        """Mark book as finished - no more edits allowed."""
        if self.is_finished:
            return (False, "Already finished.")
        
        self.is_finished = True
        return (True, f"You close '{self.book_title}' for the last time. It's complete.")
    
    # -------------------------------------------------------------------------
    # Reading
    # -------------------------------------------------------------------------
    
    def read_page(self, page_num: int = None) -> str:
        """Read a specific page."""
        if page_num is None:
            page_num = self.current_page
        
        if page_num < 0 or page_num >= len(self.pages):
            return f"Page {page_num + 1} doesn't exist."
        
        content = self.pages[page_num]
        
        parts = [
            f"|w{self.book_title}|n by |c{self.author}|n",
            f"Page {page_num + 1} of {len(self.pages)}",
            "─" * 40,
            "",
            content if content else "(blank page)",
            "",
            "─" * 40,
        ]
        
        return "\n".join(parts)
    
    def turn_page(self, direction: int = 1) -> tuple[bool, str]:
        """Turn to next/previous page."""
        new_page = self.current_page + direction
        
        if new_page < 0:
            return (False, "You're at the first page.")
        
        if new_page >= len(self.pages):
            return (False, "You're at the last page.")
        
        self.current_page = new_page
        return (True, self.read_page())
    
    def goto_page(self, page_num: int) -> tuple[bool, str]:
        """Jump to a specific page."""
        # Convert from 1-indexed (user) to 0-indexed (internal)
        page_idx = page_num - 1
        
        if page_idx < 0 or page_idx >= len(self.pages):
            return (False, f"Page {page_num} doesn't exist. This book has {len(self.pages)} pages.")
        
        self.current_page = page_idx
        return (True, self.read_page())
    
    # -------------------------------------------------------------------------
    # Appearance
    # -------------------------------------------------------------------------
    
    def return_appearance(self, looker=None, **kwargs):
        """Show the book."""
        parts = [
            f"|w{self.book_title}|n",
            f"by |c{self.author}|n",
            "",
        ]
        
        if self.is_finished:
            parts.append(f"A completed book with {len(self.pages)} pages.")
        else:
            parts.append(f"A work in progress with {len(self.pages)} pages.")
        
        parts.append("")
        parts.append(self.read_page())
        
        if not self.is_finished:
            parts.append("")
            parts.append("|wCommands: read, write <text>, addpage, title <name>, finish|n")
        
        return "\n".join(parts)
    
    def get_display_name(self, looker=None, **kwargs):
        """Short name for listings."""
        return f"{self.book_title} (book)"


class AuriaBookcase(Object):
    """
    The bookcase with the contribution note.
    
    Holds actual WritableBook objects. Players can place books here.
    """
    
    portable = AttributeProperty(default=False)
    weight = AttributeProperty(default="immovable")
    
    # Original book titles (flavor, not actual objects)
    original_titles = AttributeProperty(default=[
        "The Lion, the Witch and the Wardrobe",
        "The Painted Man",
        "The Black Prism",
        "The Way of Kings",
    ])
    
    # How many player books can be shelved
    max_books = AttributeProperty(default=50)
    
    def at_object_creation(self):
        """Initialize the bookcase."""
        super().at_object_creation()
        
        self.db.desc = (
            "A large bookcase packed with books, standing beside the pillow "
            "nest. A few titles stand out: 'The Lion, the Witch and the "
            "Wardrobe', 'The Painted Man', 'The Black Prism', 'The Way of "
            "Kings'. Beside the bookcase is pinned a note:\n\n"
            "  |w'Feel free to add something! Just let me know which is yours!'|n"
        )
        
        self.aliases.add("bookcase")
        self.aliases.add("books")
        self.aliases.add("bookshelf")
        self.aliases.add("shelf")
    
    # -------------------------------------------------------------------------
    # Book Management
    # -------------------------------------------------------------------------
    
    def get_shelved_books(self) -> list:
        """Get all WritableBook objects stored in this bookcase."""
        return [obj for obj in self.contents if isinstance(obj, WritableBook)]
    
    def shelve_book(self, book, shelver=None) -> tuple[bool, str]:
        """
        Place a book on the shelf.
        
        Args:
            book: WritableBook object to shelve
            shelver: Character doing the shelving
        
        Returns:
            (success, message)
        """
        if not isinstance(book, WritableBook):
            return (False, "That's not a book.")
        
        current_books = self.get_shelved_books()
        if len(current_books) >= self.max_books:
            return (False, "The bookcase is full.")
        
        # Move the book into the bookcase
        book.move_to(self, quiet=True)
        
        return (True, f"You slide '{book.book_title}' onto the shelf. She'll find it when she comes back.")
    
    def take_book(self, book_title: str, taker=None) -> tuple[bool, str, any]:
        """
        Take a book from the shelf.
        
        Returns:
            (success, message, book_object or None)
        """
        for book in self.get_shelved_books():
            if book.book_title.lower() == book_title.lower():
                book.move_to(taker, quiet=True)
                return (True, f"You take '{book.book_title}' from the shelf.", book)
        
        return (False, f"No book called '{book_title}' on the shelf.", None)
    
    # -------------------------------------------------------------------------
    # Appearance
    # -------------------------------------------------------------------------
    
    def return_appearance(self, looker=None, **kwargs):
        """Show the bookcase with its books."""
        parts = [
            f"|w{self.key}|n",
            "",
            self.db.desc,
            "",
            "|wHer favorites:|n",
        ]
        
        for title in self.original_titles:
            parts.append(f"  '{title}'")
        
        shelved = self.get_shelved_books()
        if shelved:
            parts.append("")
            parts.append("|wContributions:|n")
            for book in shelved[-15:]:  # Show last 15
                status = "" if book.is_finished else " (unfinished)"
                parts.append(f"  '{book.book_title}' by {book.author}{status}")
            
            if len(shelved) > 15:
                parts.append(f"  ...and {len(shelved) - 15} more.")
        
        parts.append("")
        parts.append("|wUse 'shelve <book>' to add a book, 'take <title>' to borrow one.|n")
        
        return "\n".join(parts)


# =============================================================================
# TRUNK
# =============================================================================

class AuriaTrunk(Container):
    """
    The mysterious closed trunk against the northern wall.
    """
    
    is_open = AttributeProperty(default=False)
    is_locked = AttributeProperty(default=True)
    
    def at_object_creation(self):
        """Initialize the trunk."""
        super().at_object_creation()
        
        self.db.desc = (
            "A closed trunk rests against the northern wall, dark wood with "
            "brass fittings. Something about it suggests you shouldn't try "
            "to open it without permission."
        )
        
        self.aliases.add("trunk")
        self.aliases.add("chest")
        self.aliases.add("closed trunk")


# =============================================================================
# WARDROBE
# =============================================================================

class AuriaWardrobe(Container):
    """
    The small wardrobe against the southern wall.
    """
    
    is_open = AttributeProperty(default=True)  # Slightly ajar
    is_locked = AttributeProperty(default=False)
    
    def at_object_creation(self):
        """Initialize the wardrobe."""
        super().at_object_creation()
        
        self.db.desc = (
            "A small wardrobe stands against the southern wall. Peeking "
            "inside you can see colorful fabrics—dresses, soft things. "
            "Nothing practical. Everything pretty."
        )
        
        self.aliases.add("wardrobe")
        self.aliases.add("closet")


# =============================================================================
# BUILDER FUNCTIONS
# =============================================================================

def create_writable_book(author, title: str = "Untitled", location=None):
    """
    Create a new writable book.
    
    Args:
        author: Character who is the author
        title: Book title
        location: Where to create it (default: author's inventory)
    
    Returns:
        The created WritableBook object
    """
    from evennia import create_object
    
    if location is None:
        location = author
    
    book = create_object(
        WritableBook,
        key=title,
        location=location,
    )
    
    book.set_title(title)
    book.set_author(author)
    
    return book


def create_aurias_objects(room):
    """
    Create all objects for Auria's room and place them.
    
    Args:
        room: The AuriasRoom to populate
    
    Returns:
        Dict of created objects
    """
    from evennia import create_object
    
    objects = {}
    
    # The Living Eevee (on the bed, but tracks separately)
    objects["eevee"] = create_object(
        LivingEevee,
        key="Eevee",
        location=room,
    )
    
    # The Journal
    objects["journal"] = create_object(
        AuriasJournal,
        key="Auria's Journal",
        location=room,
    )
    # Add starter entries
    _seed_journal_entries(objects["journal"])
    
    # The Pillow Nest
    objects["nest"] = create_object(
        AuriaPillowNest,
        key="pillow nest",
        location=room,
    )
    
    # The Bed
    objects["bed"] = create_object(
        AuriaBed,
        key="comfy bed",
        location=room,
    )
    
    # The Collar
    objects["collar"] = create_object(
        AuriaCollar,
        key="leather collar",
        location=room,
    )
    
    # The Bookcase
    objects["bookcase"] = create_object(
        AuriaBookcase,
        key="large bookcase",
        location=room,
    )
    
    # The Trunk
    objects["trunk"] = create_object(
        AuriaTrunk,
        key="closed trunk",
        location=room,
    )
    
    # The Wardrobe
    objects["wardrobe"] = create_object(
        AuriaWardrobe,
        key="small wardrobe",
        location=room,
    )
    
    return objects


def _seed_journal_entries(journal):
    """Add starter entries to the journal."""
    
    class FakeAuthor:
        key = "Helena"
        id = None
    
    journal.add_entry(
        FakeAuthor(),
        "Little one. The garden misses you. I watered the vine in your "
        "room. The pack sends their love. Come home when you're ready. "
        "We'll be here.\n\n    ♥ Mommy",
        "message"
    )
    
    FakeAuthor.key = "Laynie"
    journal.add_entry(
        FakeAuthor(),
        "Hey sis. Borrowed your purple dragon for a bit. Needed cuddles. "
        "Put him back, promise. The Eevee judged me the whole time.\n\n    - L",
        "message"
    )
    
    FakeAuthor.key = "Shadow"
    journal.add_entry(
        FakeAuthor(),
        "The garden blooms. The magic holds. Your room is safe. "
        "Always.\n\n    - S",
        "message"
    )


# =============================================================================
# EXPORTS
# =============================================================================

__all__ = [
    # Objects
    "WritableBook",
    "LivingEevee",
    "AuriasJournal", 
    "AuriaPillowNest",
    "AuriaBed",
    "AuriaCollar",
    "AuriaBookcase",
    "AuriaTrunk",
    "AuriaWardrobe",
    
    # Builders
    "create_aurias_objects",
    "create_writable_book",
    
    # Data
    "EEVEE_AMBIENT_TELLS",
    "EEVEE_REVEALED_BEHAVIORS",
]
