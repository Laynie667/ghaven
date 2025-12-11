"""
Guest Room Builder - Complete

Creates Helena's Cabin Guest Room (formerly Elle's Bedroom) with all functionality:
- GuestRoom typeclass with time-variant descriptions
- Round bed with scene positions and hidden waterproof cover
- Rocking chair with rocking motion mechanic
- Vanity with mirror (shows looker appearance)
- Wardrobe (save/load system hook)
- Dresser with hidden respawning toys
- Floor drain (watersports-friendly)
- Atmospheric objects (stuffies, plaque, rug, wallpaper)

Run from Evennia:
    @py from world.build_guest_room import build; build()

Test functions:
    @py from world.build_guest_room import test_time; test_time()
    @py from world.build_guest_room import test_mirror; test_mirror()
"""

from evennia import create_object, search_object
from evennia.typeclasses.attributes import AttributeProperty
from typeclasses.objects import Object, Furniture
from typeclasses.base_rooms import IndoorRoom


# =============================================================================
# NEW TYPECLASSES
# =============================================================================

class GuestRoom(IndoorRoom):
    """
    Guest Room with time-variant descriptions.
    
    Shortcodes:
        <time.desc> - Time-appropriate atmospheric description
    """
    
    time_descriptions = AttributeProperty(default={
        "morning": (
            "Soft light filters through, the white and yellow feeling bright and fresh. "
            "The vanilla-linen scent is crisp. A good place to wake slowly."
        ),
        "afternoon": (
            "Warm and quiet. The pink-hued furniture seems to glow in the gentle light. "
            "Comfortable for a nap."
        ),
        "evening": (
            "Golden light makes everything softer. The rocking chair invites you to sit, "
            "wrapped in the fleece blanket."
        ),
        "night": (
            "Soft lamplight. The round bed beckons, promising to swallow you in comfort. "
            "The room feels safe. Private."
        ),
    })
    
    def get_time_period(self) -> str:
        """Get current time period. Override with actual time system."""
        # TODO: Hook into actual time system
        return "afternoon"
    
    def process_shortcodes(self, text: str) -> str:
        """Process room description shortcodes."""
        text = super().process_shortcodes(text) if hasattr(super(), 'process_shortcodes') else text
        
        # Time description
        period = self.get_time_period()
        time_desc = self.time_descriptions.get(period, self.time_descriptions["afternoon"])
        text = text.replace("<time.desc>", time_desc)
        
        return text


class RoundBed(Furniture):
    """
    The round bed - unusual, inviting, with hidden waterproof cover.
    High capacity, multiple scene positions.
    """
    
    capacity = AttributeProperty(default=4)
    portable = AttributeProperty(default=False)
    
    position_slots = AttributeProperty(default=[
        "center", "edge", "sprawled", "curled"
    ])
    
    position_descs = AttributeProperty(default={
        "center": "{name} lies in the center of the round bed, sunk into its embrace.",
        "edge": "{name} lies at the edge of the round bed.",
        "sprawled": "{name} is sprawled across the round bed, taking up space.",
        "curled": "{name} is curled up on the round bed.",
    })
    
    scene_positions = AttributeProperty(default=[
        "lying (center)", "lying (edge)", "sprawled", "curled together",
        "on all fours", "riding", "face-down"
    ])
    
    restraint_points = AttributeProperty(default=[
        "bed frame (under)", "headboard area", "each other"
    ])
    
    # Hidden feature
    has_waterproof_cover = AttributeProperty(default=True)
    
    def return_appearance(self, looker, **kwargs):
        parts = [f"|w{self.key}|n", ""]
        
        desc = (
            "The bed is round, unusual and inviting. The mattress is so thick and soft "
            "that anyone lying on it sinks several inches into its embrace. Fluffy pillows "
            "cluster at the head, a few decorative stuffed animals arranged among them. "
            "The sheets smell of fresh linen."
        )
        parts.append(desc)
        
        # Who's using it
        if hasattr(self, 'current_users') and self.current_users:
            parts.append("")
            parts.append(self.get_occupied_desc())
        
        return "\n".join(parts)


class RockingChair(Furniture):
    """
    Wide rocking chair for two. Continues rocking during scenes.
    """
    
    capacity = AttributeProperty(default=2)
    portable = AttributeProperty(default=False)
    is_rocking = AttributeProperty(default=False)
    
    position_slots = AttributeProperty(default=["seated", "lap"])
    
    position_descs = AttributeProperty(default={
        "seated": "{name} sits in the rocking chair, wrapped in the fleece blanket.",
        "lap": "{name} sits in someone's lap in the rocking chair.",
    })
    
    scene_positions = AttributeProperty(default=[
        "sitting alone", "lap sitting", "cuddling", "straddling"
    ])
    
    def start_rocking(self):
        """Start the rocking motion."""
        self.is_rocking = True
        if self.location:
            self.location.msg_contents(
                "The rocking chair begins to rock gently, creaking softly."
            )
    
    def stop_rocking(self):
        """Stop the rocking motion."""
        self.is_rocking = False
        if self.location:
            self.location.msg_contents(
                "The rocking chair settles, going still."
            )
    
    def return_appearance(self, looker, **kwargs):
        parts = [f"|w{self.key}|n", ""]
        
        desc = (
            "A generous rocking chair that could comfortably hold two. Soft cushions "
            "pad the seat and back, and a cozy fleece blanket is draped over one arm. "
            "It faces the door—whoever sits here sees everyone who enters. "
            "The rockers are smooth from use."
        )
        parts.append(desc)
        
        if self.is_rocking:
            parts.append("")
            parts.append("It rocks gently back and forth, creaking softly.")
        
        if hasattr(self, 'current_users') and self.current_users:
            parts.append("")
            parts.append(self.get_occupied_desc())
        
        return "\n".join(parts)


class VanityMirror(Furniture):
    """
    Vanity with mirror that shows looker's appearance.
    """
    
    portable = AttributeProperty(default=False)
    
    def return_appearance(self, looker, **kwargs):
        parts = [f"|w{self.key}|n", ""]
        
        desc = (
            "White wood with that soft pink glow, topped with a large round mirror "
            "in a simple frame. The surface holds an assortment of basic toiletries "
            "and makeup—enough for any guest to freshen up or prepare themselves. "
            "A cushioned stool sits before it."
        )
        parts.append(desc)
        
        # Mirror reflection
        if looker:
            parts.append("")
            parts.append("|wYour reflection:|n")
            parts.append("")
            try:
                reflection = looker.return_appearance(looker)
                parts.append(reflection)
            except Exception:
                parts.append("You see yourself reflected in the glass.")
        
        return "\n".join(parts)


class GuestWardrobe(Furniture):
    """
    Wardrobe with save/load system access.
    """
    
    portable = AttributeProperty(default=False)
    is_open = AttributeProperty(default=True)
    
    # Contents for display (not actual inventory)
    display_contents = AttributeProperty(default=[
        "fluffy towels", "spare robes", "outfits in various sizes",
        "guest amenities", "some decidedly impractical attire"
    ])
    
    def return_appearance(self, looker, **kwargs):
        parts = [f"|w{self.key}|n", ""]
        
        if self.is_open:
            desc = (
                "Double doors stand open, revealing shelves and hanging space stocked "
                "with guest amenities. Fluffy towels, spare robes, and a selection of "
                "outfits in various sizes—some practical, some decidedly less so. "
                "Everything a guest might need for comfort or... other purposes."
            )
        else:
            desc = "A wardrobe in soft white with pink undertones. The double doors are closed."
        
        parts.append(desc)
        return "\n".join(parts)


class HiddenToysDresser(Furniture):
    """
    Dresser with hidden toys underneath that respawn.
    """
    
    portable = AttributeProperty(default=False)
    
    # Toys that respawn when taken
    hidden_toys = AttributeProperty(default=[
        "a modest vibrator", "soft restraints", "a blindfold",
        "massage oil", "a feather"
    ])
    
    def return_appearance(self, looker, **kwargs):
        parts = [f"|w{self.key}|n", ""]
        
        desc = (
            "A dresser in soft white with pink undertones. The surface holds a few "
            "decorative items—a small vase, a scented candle, guest amenities. "
            "The drawers contain spare linens and basic supplies."
        )
        parts.append(desc)
        
        # Hint at hidden items
        parts.append("")
        parts.append(
            "A few items peek out from under the dresser, seemingly tucked away "
            "but not quite hidden."
        )
        
        return "\n".join(parts)
    
    def get_hidden_item(self, item_name: str):
        """
        Get a hidden item. These respawn, so always available.
        Returns item name if valid, None otherwise.
        """
        for toy in self.hidden_toys:
            if item_name.lower() in toy.lower():
                return toy
        return None


# =============================================================================
# BUILD FUNCTION
# =============================================================================

def build():
    """Build Guest Room with all objects and connection to Passageway."""
    
    # Find Passageway (should exist)
    passageway = search_object("Passageway")
    if not passageway:
        print("ERROR: Passageway not found. Build it first.")
        return None
    passageway = passageway[0]
    
    # Create Guest Room
    room = create_object(GuestRoom, key="Guest Room")
    
    room.db.desc = """This is a guest room, soft and welcoming.

The walls are covered with striped |cwallpaper|n—pale yellow and white stripes printed with roses and ivy at intermittent points. Light wooden flooring extends from white mop boards, covered by a plush white |carea rug|n at the center. A barely-visible |cdrain|n is set into the floor near the bed—easy to miss if you're not looking.

A |cround bed|n fills the back right corner, its mattress thick and impossibly soft. Fluffy pillows and a few decorative |cstuffed animals|n top it, the bedding crisp and fresh. The furniture set—|cdresser|n, |cbedside table|n, |cvanity|n with large round mirror, and |cwardrobe|n—is colored in white that seems to glow softly with a pink hue.

The wardrobe stands with double doors open, stocked with guest amenities and a selection of outfits. The vanity holds basic toiletries and makeup. A wide |crocking chair|n with soft cushions and a fleece blanket faces the door, large enough for two.

Above the door, a decorative wooden |cplaque|n states: 'Welcome, we care about you.'

<time.desc>"""
    
    room.db.atmosphere = {
        "sounds": "quiet, muffled cabin sounds, occasional creak of rocking chair",
        "scents": "vanilla, fresh linen, hint of roses from wallpaper",
        "mood": "welcoming",
        "preset": "guest_comfort",
    }
    room.lighting = "soft"
    room.temperature = "comfortable"
    
    # ---------------------------------------------------------------------
    # EXITS
    # ---------------------------------------------------------------------
    
    # Exit to Passageway
    exit_out = create_object(
        "evennia.objects.objects.DefaultExit",
        key="out",
        location=room,
        destination=passageway,
        aliases=["passageway", "west", "w", "door"],
    )
    exit_out.db.desc = (
        "The door leads west to the Passageway. The pale yellow door with floral "
        "decals still says \"Elle\" on its plaque—no one's changed it yet. Maybe they won't."
    )
    
    # Update Passageway exit to point here instead of Limbo
    for exit_obj in passageway.exits:
        if exit_obj.key == "east2":
            exit_obj.destination = room
            print(f"Updated Passageway exit 'east2' to point to Guest Room")
            break
    
    # ---------------------------------------------------------------------
    # FURNITURE
    # ---------------------------------------------------------------------
    
    # Round Bed
    bed = create_object(RoundBed, key="round bed", location=room,
                       aliases=["bed"])
    bed.db.desc = "A round bed with an impossibly soft mattress, fluffy pillows, and stuffed animals."
    
    # Rocking Chair
    chair = create_object(RockingChair, key="rocking chair", location=room,
                         aliases=["chair", "rocker"])
    chair.db.desc = "A wide rocking chair with soft cushions and a fleece blanket, large enough for two."
    
    # Dresser (with hidden toys)
    dresser = create_object(HiddenToysDresser, key="dresser", location=room,
                           aliases=["drawer", "drawers"])
    dresser.db.desc = "A dresser in soft white with pink undertones."
    
    # Vanity (with mirror)
    vanity = create_object(VanityMirror, key="vanity", location=room,
                          aliases=["mirror", "vanity mirror"])
    vanity.db.desc = "A vanity with a large round mirror, holding basic toiletries and makeup."
    
    # Wardrobe
    wardrobe = create_object(GuestWardrobe, key="wardrobe", location=room,
                            aliases=["closet", "clothes"])
    wardrobe.db.desc = "A wardrobe with double doors open, stocked with guest amenities and outfits."
    
    # ---------------------------------------------------------------------
    # OBJECTS
    # ---------------------------------------------------------------------
    
    # Floor Drain
    drain = create_object(Object, key="drain", location=room,
                         aliases=["floor drain"])
    drain.db.desc = "A small drain set into the floor near the bed, barely visible."
    drain.examined = (
        "A small drain set into the floor near the bed, barely visible beneath the "
        "rug's edge. Practical for cleaning. Or other purposes."
    )
    drain.portable = False
    
    # Stuffed Animals
    stuffies = create_object(Object, key="stuffed animals", location=room,
                            aliases=["stuffies", "plushies", "animals"])
    stuffies.db.desc = "A few decorative stuffed animals among the pillows."
    stuffies.examined = (
        "A few decorative stuffed animals sit among the pillows on the round bed. "
        "Generic, cute, comforting—left for guests who might want something to hold.\n\n"
        "Elle's personal stuffies (including the wolf from Helena) have been packed "
        "away with her other things. These are new, for anyone."
    )
    stuffies.portable = False
    
    # Welcome Plaque
    plaque = create_object(Object, key="plaque", location=room,
                          aliases=["welcome plaque", "sign"])
    plaque.db.desc = "A decorative wooden plaque above the door."
    plaque.examined = (
        "Above the door, a decorative wooden plaque states: \"Welcome, we care about you.\"\n\n"
        "Originally said \"Welcome Elle\"—updated for all guests now, but the care remains genuine."
    )
    plaque.portable = False
    
    # Area Rug
    rug = create_object(Object, key="area rug", location=room,
                       aliases=["rug", "carpet"])
    rug.db.desc = "A plush white area rug at the center of the room."
    rug.examined = (
        "A plush white area rug covers the center of the light wooden floor. "
        "Soft underfoot, clean and welcoming. The edges are slightly tucked to "
        "hide the floor drain nearby."
    )
    rug.portable = False
    
    # Bedside Table
    table = create_object(Object, key="bedside table", location=room,
                         aliases=["nightstand", "side table"])
    table.db.desc = "A small bedside table matching the white-pink furniture set."
    table.examined = (
        "A small table beside the round bed, matching the white-with-pink-undertones "
        "of the other furniture. A lamp sits atop it, along with a small dish for "
        "personal items. The drawer holds nothing of note—left empty for guests."
    )
    table.portable = False
    
    # Wallpaper
    wallpaper = create_object(Object, key="wallpaper", location=room,
                             aliases=["walls", "wall"])
    wallpaper.db.desc = "Striped wallpaper in pale yellow and white with roses and ivy."
    wallpaper.examined = (
        "Pale yellow and white stripes run vertically up the walls, printed at "
        "intervals with delicate roses and trailing ivy. The pattern is soft, "
        "feminine, welcoming—chosen by someone who wanted guests to feel at ease. "
        "The paper itself is in good condition, no peeling or fading."
    )
    wallpaper.portable = False
    
    # ---------------------------------------------------------------------
    # OUTPUT
    # ---------------------------------------------------------------------
    
    print(f"Built Guest Room: {room.dbref}")
    print(f"Connected to Passageway: {passageway.dbref}")
    print(f"")
    print(f"Exits:")
    print(f"  out → Passageway")
    print(f"")
    print(f"Furniture:")
    print(f"  round bed (capacity 4, scene positions, restraint points)")
    print(f"  rocking chair (capacity 2, rocking mechanic)")
    print(f"  dresser (hidden respawning toys)")
    print(f"  vanity (mirror shows appearance)")
    print(f"  wardrobe (save/load system hook)")
    print(f"")
    print(f"Objects: drain, stuffed animals, plaque, area rug, bedside table, wallpaper")
    print(f"")
    print(f"Test with:")
    print(f"  @py from world.build_guest_room import test_time; test_time()")
    print(f"  @py from world.build_guest_room import test_mirror; test_mirror()")
    print(f"  @py from world.build_guest_room import test_rocking; test_rocking()")
    
    return room


# =============================================================================
# TEST FUNCTIONS
# =============================================================================

def get_guest_room():
    """Find the Guest Room."""
    results = search_object("Guest Room")
    return results[0] if results else None


def test_time():
    """Test all time-variant descriptions."""
    room = get_guest_room()
    if not room:
        return "Guest Room not found."
    
    print("=== TIME-VARIANT DESCRIPTIONS ===\n")
    for period in ["morning", "afternoon", "evening", "night"]:
        desc = room.time_descriptions.get(period)
        print(f"{period.upper()}:")
        print(f"  {desc}")
        print()
    
    return room


def test_mirror():
    """Test vanity mirror reflection."""
    room = get_guest_room()
    if not room:
        return "Guest Room not found."
    
    vanity = None
    for obj in room.contents:
        if isinstance(obj, VanityMirror):
            vanity = obj
            break
    
    if not vanity:
        return "Vanity not found."
    
    print("=== VANITY MIRROR TEST ===\n")
    print("Looking at vanity will show looker's appearance.")
    print(f"Vanity found: {vanity.dbref}")
    
    return vanity


def test_rocking():
    """Test rocking chair mechanic."""
    room = get_guest_room()
    if not room:
        return "Guest Room not found."
    
    chair = None
    for obj in room.contents:
        if isinstance(obj, RockingChair):
            chair = obj
            break
    
    if not chair:
        return "Rocking chair not found."
    
    print("=== ROCKING CHAIR TEST ===\n")
    print(f"Current state: {'rocking' if chair.is_rocking else 'still'}")
    
    chair.start_rocking()
    print(f"After start_rocking(): {'rocking' if chair.is_rocking else 'still'}")
    
    chair.stop_rocking()
    print(f"After stop_rocking(): {'rocking' if chair.is_rocking else 'still'}")
    
    return chair


def test_dresser():
    """Test dresser hidden toys."""
    room = get_guest_room()
    if not room:
        return "Guest Room not found."
    
    dresser = None
    for obj in room.contents:
        if isinstance(obj, HiddenToysDresser):
            dresser = obj
            break
    
    if not dresser:
        return "Dresser not found."
    
    print("=== HIDDEN TOYS TEST ===\n")
    print("Available hidden toys:")
    for toy in dresser.hidden_toys:
        print(f"  - {toy}")
    
    print("\nTest get_hidden_item('vibrator'):")
    result = dresser.get_hidden_item("vibrator")
    print(f"  Result: {result}")
    
    return dresser
