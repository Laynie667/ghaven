"""
Passageway Builder - Complete

Creates Helena's Cabin Passageway with all custom functionality:
- SeasonalPotpourri with seasonal scent shortcode
- ShadowMusk with state decay (present → recent → fading → absent)
- ViewerAwarePortrait that shows different text based on looker
- PassagewayRoom with <potpourri.scent> and <shadow_musk.desc> shortcodes
- Shadow detection triggers musk refresh
- All plaques as inspectable furniture

Run from Evennia:
    @py from world.build_passageway import build; build()

Test functions:
    @py from world.build_passageway import test_musk; test_musk()
    @py from world.build_passageway import test_portrait; test_portrait()
    @py from world.build_passageway import test_seasons; test_seasons()
"""

from evennia import create_object, search_object
from evennia.typeclasses.attributes import AttributeProperty
from typeclasses.objects import Object, Furniture, AtmosphericObject
from typeclasses.base_rooms import IndoorRoom


# =============================================================================
# NEW TYPECLASSES
# =============================================================================

class SeasonalPotpourri(Object):
    """
    Potpourri bowl with scent that changes by season.
    """
    
    portable = AttributeProperty(default=False)
    weight = AttributeProperty(default="light")
    
    seasonal_scents = AttributeProperty(default={
        "spring": "smelling of fresh green herbs and early wildflowers",
        "summer": "smelling of wild flowers and mint",
        "autumn": "smelling of dried apples and warm spices",
        "winter": "smelling of pine and cedar",
    })
    
    seasonal_examine = AttributeProperty(default={
        "spring": (
            "A decorative bowl filled with dried flowers and herbs. "
            "Fresh green herbs and early wildflowers dominate the mix. "
            "A hint of rain-washed earth lingers underneath."
        ),
        "summer": (
            "A decorative bowl filled with dried flowers and herbs. "
            "Wild flowers and fresh mint dominate, bright and clean. "
            "A touch of lavender rests underneath."
        ),
        "autumn": (
            "A decorative bowl filled with dried flowers and herbs. "
            "Dried apples and cinnamon, warm spices against the coming cold. "
            "A whisper of woodsmoke clings to everything."
        ),
        "winter": (
            "A decorative bowl filled with dried flowers and herbs. "
            "Pine and cedar, sharp and clean. Dried cranberries add a hint "
            "of tartness. The scent of shelter."
        ),
    })
    
    def get_season(self) -> str:
        """Get current season. Override with actual game season system."""
        # TODO: Hook into actual season system
        # For now, check room or return default
        if self.location and hasattr(self.location, 'current_season'):
            return self.location.current_season
        return "summer"
    
    def get_scent(self) -> str:
        """Get current scent string for shortcode."""
        season = self.get_season()
        return self.seasonal_scents.get(season, self.seasonal_scents["summer"])
    
    def return_appearance(self, looker, **kwargs):
        season = self.get_season()
        desc = self.seasonal_examine.get(season, self.seasonal_examine["summer"])
        return f"|w{self.key}|n\n\n{desc}"


class ShadowMusk(Object):
    """
    Invisible atmospheric that tracks Shadow's presence via scent.
    Decays: present → recent → fading → absent
    """
    
    portable = AttributeProperty(default=False)
    weight = AttributeProperty(default="immovable")
    current_state = AttributeProperty(default="absent")
    decay_ticks = AttributeProperty(default=0)
    
    # Invisible - doesn't show in room contents
    visible = AttributeProperty(default=False)
    
    decay_rates = AttributeProperty(default={
        "present": 5,
        "recent": 8,
        "fading": 12,
    })
    
    # For shortcode - inline in room desc
    state_inline = AttributeProperty(default={
        "present": ", though a heavy, unmistakable musk hangs in the air",
        "recent": ", though a slightly musky undertone wafts from somewhere nearby",
        "fading": ", though a faint musky undertone lingers",
        "absent": "",
    })
    
    def at_object_creation(self):
        super().at_object_creation()
        self.locks.add("get:false()")
        self.locks.add("view:false()")
    
    def get_inline_desc(self) -> str:
        """Get inline description for shortcode."""
        return self.state_inline.get(self.current_state, "")
    
    def on_shadow_pass(self):
        """Called when Shadow moves through the room."""
        self.current_state = "present"
        self.decay_ticks = 0
    
    def tick_decay(self) -> bool:
        """Process one decay tick. Returns True if state changed."""
        if self.current_state == "absent":
            return False
        
        self.decay_ticks += 1
        threshold = self.decay_rates.get(self.current_state, 10)
        
        if self.decay_ticks >= threshold:
            order = ["present", "recent", "fading", "absent"]
            try:
                idx = order.index(self.current_state)
                if idx < len(order) - 1:
                    self.current_state = order[idx + 1]
                    self.decay_ticks = 0
                    return True
            except ValueError:
                self.current_state = "absent"
        return False
    
    def force_state(self, state: str) -> bool:
        """Force to specific state (for testing)."""
        if state in self.state_inline:
            self.current_state = state
            self.decay_ticks = 0
            return True
        return False


class ViewerAwarePortrait(Object):
    """
    Portrait that shows different text based on who's looking.
    """
    
    portable = AttributeProperty(default=False)
    weight = AttributeProperty(default="heavy")
    
    base_examine = AttributeProperty(default=(
        "A large oil painting in an ornate frame. The painting depicts a massive "
        "black direwolf, muscles rippling beneath dark fur, fangs bared in what "
        "might be a snarl or a grin. Her impressive endowment is rendered without shame.\n\n"
        "Arrayed around her are beautiful women in flowing silk, clinging to her sides "
        "in various states of devotion. Some kneel. Some recline against her flank. "
        "Each face is rendered with remarkable detail—real people, not imagined.\n\n"
        "The portrait is titled \"Shadow's Harem\" in elegant script. A date is partially "
        "visible but hard to make out."
    ))
    
    # Characters who see themselves in the painting
    recognized_keys = AttributeProperty(default=["laynie", "princess", "auria", "oreo"])
    recognized_tags = AttributeProperty(default=["claimed", "harem"])
    
    stranger_addition = AttributeProperty(default=(
        "\n\nThe women are beautiful, devoted. You don't recognize any of them "
        "specifically, but something about the painting makes you feel... considered."
    ))
    
    self_additions = AttributeProperty(default={
        "laynie": (
            "\n\nThere you are, nestled against Shadow's flank. The silk barely covers you. "
            "Your expression is... accurate. Whoever painted this has seen you like this."
        ),
        "princess": (
            "\n\nThere you are, nestled against Shadow's flank. The silk barely covers you. "
            "Your expression is... accurate. Whoever painted this has seen you like this."
        ),
        "auria": (
            "\n\nYou recognize yourself among the women, painted with care and obvious "
            "affection. The artist captured your essence—the way you look at Her."
        ),
        "oreo": (
            "\n\nYou recognize yourself among the women, painted with care and obvious "
            "affection. The artist captured your essence—the way you look at Her."
        ),
    })
    
    claimed_addition = AttributeProperty(default=(
        "\n\nOne of the women looks remarkably like you. The resemblance is uncanny—"
        "the artist must have known you would stand here someday."
    ))
    
    def get_viewer_addition(self, looker) -> str:
        """Get additional text based on who's looking."""
        if not looker:
            return self.stranger_addition
        
        # Check by key
        looker_key = looker.key.lower() if looker.key else ""
        if looker_key in self.recognized_keys:
            return self.self_additions.get(looker_key, self.claimed_addition)
        
        # Check by tags
        if hasattr(looker, 'tags'):
            for tag in self.recognized_tags:
                if looker.tags.has(tag, category="identity") or looker.tags.has(tag):
                    return self.claimed_addition
        
        return self.stranger_addition
    
    def return_appearance(self, looker, **kwargs):
        parts = [f"|w{self.key}|n", ""]
        parts.append(self.base_examine)
        parts.append(self.get_viewer_addition(looker))
        return "\n".join(parts)


class PassagewayRoom(IndoorRoom):
    """
    Passageway room with custom shortcodes and Shadow detection.
    
    Shortcodes:
        <potpourri.scent> - Current seasonal scent
        <shadow_musk.desc> - Musk description based on state
    """
    
    shadow_present = AttributeProperty(default=False)
    current_season = AttributeProperty(default="summer")
    
    def process_shortcodes(self, text: str) -> str:
        """Process room description shortcodes."""
        text = super().process_shortcodes(text) if hasattr(super(), 'process_shortcodes') else text
        
        # Potpourri scent
        potpourri = self._get_potpourri()
        if potpourri:
            scent = potpourri.get_scent()
        else:
            scent = "smelling of wild flowers and mint"
        text = text.replace("<potpourri.scent>", scent)
        
        # Shadow musk
        musk = self._get_shadow_musk()
        if musk:
            musk_desc = musk.get_inline_desc()
        else:
            musk_desc = ""
        text = text.replace("<shadow_musk.desc>", musk_desc)
        
        return text
    
    def _get_potpourri(self):
        """Find potpourri object."""
        for obj in self.contents:
            if isinstance(obj, SeasonalPotpourri):
                return obj
        return None
    
    def _get_shadow_musk(self):
        """Find shadow musk object."""
        for obj in self.contents:
            if isinstance(obj, ShadowMusk):
                return obj
        return None
    
    def _is_shadow(self, obj) -> bool:
        """Check if object is Shadow."""
        if not obj:
            return False
        key = obj.key.lower() if obj.key else ""
        return (
            key in ("shadow", "shadowkaven") or
            getattr(obj, 'is_shadow', False) or
            obj.tags.has("shadow", category="identity")
        )
    
    def at_object_receive(self, moved_obj, source_location, move_type=None, **kwargs):
        """Trigger musk refresh when Shadow enters."""
        super().at_object_receive(moved_obj, source_location, move_type, **kwargs)
        
        if self._is_shadow(moved_obj):
            self.shadow_present = True
            musk = self._get_shadow_musk()
            if musk:
                musk.on_shadow_pass()
    
    def at_object_leave(self, moved_obj, target_location, move_type=None, **kwargs):
        """Track Shadow leaving."""
        super().at_object_leave(moved_obj, target_location, move_type, **kwargs)
        
        if self._is_shadow(moved_obj):
            self.shadow_present = False
    
    def tick_musk(self) -> bool:
        """Tick musk decay."""
        musk = self._get_shadow_musk()
        if musk:
            return musk.tick_decay()
        return False


# =============================================================================
# BUILD FUNCTION
# =============================================================================

def build():
    """Build Passageway with all objects and exits."""
    
    # Find Welcome Room (should exist)
    welcome = search_object("Welcome Room")
    if not welcome:
        print("ERROR: Welcome Room not found. Build it first.")
        return None
    welcome = welcome[0]
    
    # Create Passageway
    room = create_object(PassagewayRoom, key="Passageway")
    
    room.db.desc = """A long and wide hallway stretches from the Welcome Room to the arched and open entryway to the north, marked with a simple sign that reads 'Common Room'.

The hallway has dark wooden flooring that has been well taken care of. A rectangular |carea rug|n peppered with softer tones of gray and white is laid towards the center, with an |centry table|n between the two doors on the east wall. Sitting atop the table are three small |cwolf figurines|n made with care and attention to detail, giving them a life-like appearance, the center one being well endowed. A decorative |cpotpourri bowl|n <potpourri.scent> also adorns the table top<shadow_musk.desc>.

Mounted to the wall above the table is another piece of fanciful wolf iconography. A |cportrait|n of a large black direwolf defined with powerful muscle, a striking expression with fangs bared and surrounded by several silk-clad women clinging to its sides—some notably familiar and well bred. The portrait is simply titled "Shadow's Harem" although the date is hard to make out.

Two doors line each side wall, each adorned with a unique |cplaque|n. On the western wall, a heavy door reinforced with thick strips of iron and dark bolts leads to Helena's room—with deep |cscratches|n gouged into the flooring trailing towards it. Just down from the heavy door, a much lighter door in gentle shades of pink with the silhouettes of various faeries and stars marks Auria's room. On the eastern wall on one side of the entry table, a door of rich mahogany with delicate vine carvings leads to the Garden of Knowledge. At the other end of the table, nearest to the open archway, a door painted in pale yellow and decorated in floral decals of various pinks and violets opens to the Guest Room."""
    
    room.db.atmosphere = {
        "sounds": "muffled voices from the Common Room, distant warmth, creaking wood",
        "scents": "potpourri, wood polish, faint musk",
        "mood": "homey",
    }
    room.lighting = "normal"
    room.temperature = "warm"
    
    # ---------------------------------------------------------------------
    # EXITS
    # ---------------------------------------------------------------------
    
    # Exit to Welcome Room
    create_object(
        "evennia.objects.objects.DefaultExit",
        key="out",
        location=room,
        destination=welcome,
        aliases=["welcome", "south", "s"],
    )
    
    # Exit from Welcome Room to Passageway
    create_object(
        "evennia.objects.objects.DefaultExit",
        key="in",
        location=welcome,
        destination=room,
        aliases=["passageway", "hallway", "north", "n"],
    )
    
    # Placeholder exits (to Limbo until rooms are built)
    limbo = search_object("#2")[0]
    
    create_object(
        "evennia.objects.objects.DefaultExit",
        key="west1",
        location=room,
        destination=limbo,
        aliases=["helena", "helena's room", "h.s."],
    )
    
    create_object(
        "evennia.objects.objects.DefaultExit",
        key="west2",
        location=room,
        destination=limbo,
        aliases=["auria", "auria's room"],
    )
    
    create_object(
        "evennia.objects.objects.DefaultExit",
        key="east1",
        location=room,
        destination=limbo,
        aliases=["garden", "garden of knowledge", "library"],
    )
    
    create_object(
        "evennia.objects.objects.DefaultExit",
        key="east2",
        location=room,
        destination=limbo,
        aliases=["guest", "guest room"],
    )
    
    create_object(
        "evennia.objects.objects.DefaultExit",
        key="north",
        location=room,
        destination=limbo,
        aliases=["common", "common room", "in", "n"],
    )
    
    # ---------------------------------------------------------------------
    # OBJECTS
    # ---------------------------------------------------------------------
    
    # Shadow Musk (invisible)
    musk = create_object(ShadowMusk, key="shadow musk", location=room)
    
    # Area Rug
    rug = create_object(Object, key="area rug", location=room,
                       aliases=["rug", "carpet"])
    rug.db.desc = "A rectangular area rug in soft gray and white tones."
    rug.examined = (
        "A plush rectangular rug laid towards the center of the hallway. "
        "Soft tones of gray and white form a subtle pattern. It's well-worn "
        "in the middle where feet pass most often, but still comfortable underfoot."
    )
    rug.portable = False
    
    # Entry Table
    table = create_object(Object, key="entry table", location=room,
                         aliases=["table"])
    table.db.desc = "A wooden entry table between the two doors on the east wall."
    table.examined = (
        "Solid and well-made, the table holds the wolf figurines and potpourri bowl. "
        "The wood is dark, matching the flooring, polished but showing its age in "
        "small scratches and wear marks. Positioned between the Garden door and the "
        "Guest Room door."
    )
    table.portable = False
    
    # Wolf Figurines
    figurines = create_object(Object, key="wolf figurines", location=room,
                             aliases=["figurines", "wolves", "statues"])
    figurines.db.desc = "Three small wolf figurines made with care and attention to detail."
    figurines.examined = (
        "Three wolves carved with remarkable skill, each painted with lifelike detail:\n\n"
        "The largest is jet black with powerful haunches and a knowing expression. "
        "Well endowed. Shadow.\n\n"
        "The second is light brown with a cream underbelly, smaller and alert. "
        "Also endowed, though modestly. Whisper.\n\n"
        "The third is pure white, elegant and poised with quiet grace. Blaze.\n\n"
        "Each is polished smooth from handling. Someone touches these often."
    )
    figurines.portable = False
    
    # Potpourri Bowl
    potpourri = create_object(SeasonalPotpourri, key="potpourri bowl", location=room,
                             aliases=["potpourri", "bowl"])
    potpourri.db.desc = "A decorative bowl of dried flowers and herbs."
    
    # Portrait
    portrait = create_object(ViewerAwarePortrait, key="portrait", location=room,
                            aliases=["painting", "shadow's harem", "harem"])
    portrait.db.desc = "A portrait titled \"Shadow's Harem\"."
    
    # Scratches
    scratches = create_object(Object, key="scratches", location=room,
                             aliases=["gouges", "claw marks", "marks"])
    scratches.db.desc = "Deep scratches gouged into the wooden flooring."
    scratches.examined = (
        "Deep gouges in the wood, trailing toward Helena's door on the western wall. "
        "Claw marks from something large and eager, worn into the floor over time. "
        "The pattern speaks of urgency—something scrambling toward that door, again "
        "and again, unable or unwilling to wait."
    )
    scratches.portable = False
    
    # ---------------------------------------------------------------------
    # PLAQUES (Furniture)
    # ---------------------------------------------------------------------
    
    # Helena's Plaque
    helena_plaque = create_object(Furniture, key="Helena's plaque", location=room,
                                 aliases=["h.s. plaque", "iron plaque", "gothic plaque"])
    helena_plaque.db.desc = "A heavy iron-reinforced door plaque on the western wall."
    helena_plaque.examined = (
        "A formidable plaque mounted on a heavy door reinforced with thick strips of "
        "iron and dark bolts. The initials 'H.S.' are boldly emblazoned in stylized "
        "gothic letters, surrounded by a wolf's paw print inside a circle of unbroken "
        "chain. The craftsmanship is severe and deliberate—a warning as much as a marker. "
        "The deep scratches gouged into the flooring trail directly toward this door."
    )
    helena_plaque.portable = False
    
    # Auria's Plaque
    auria_plaque = create_object(Furniture, key="Auria's plaque", location=room,
                                aliases=["pink plaque", "faerie plaque"])
    auria_plaque.db.desc = "A pink door plaque decorated with faeries and stars."
    auria_plaque.examined = (
        "A wooden plaque on a much lighter door painted in gentle shades of pink, "
        "decorated with the silhouettes of various faeries and stars. The name 'Auria' "
        "is spelled out in cute bubbly lettering, each letter slightly different as if "
        "drawn by hand. The whole effect is whimsical and warm—a stark contrast to the "
        "heavy iron door beside it."
    )
    auria_plaque.portable = False
    
    # Garden Plaque
    garden_plaque = create_object(Furniture, key="Garden plaque", location=room,
                                 aliases=["mahogany plaque", "vine plaque", "garden of knowledge plaque"])
    garden_plaque.db.desc = "A rich mahogany plaque with delicate vine carvings."
    garden_plaque.examined = (
        "A refined plaque on a door of rich mahogany, positioned on one side of the "
        "entry table. Delicate vines are carved across its surface, seeming to grow "
        "and wind with natural grace. 'Garden of Knowledge' is inscribed in elegant "
        "script. The craftsmanship suggests patience and care—each leaf distinct, "
        "each tendril purposeful."
    )
    garden_plaque.portable = False
    
    # Guest Room Plaque
    guest_plaque = create_object(Furniture, key="Guest Room plaque", location=room,
                                aliases=["yellow plaque", "floral plaque", "guest plaque"])
    guest_plaque.db.desc = "A yellow door plaque with floral decorations."
    guest_plaque.examined = (
        "A wooden plaque on a door painted in pale yellow, positioned at the other end "
        "of the entry table nearest the open archway. Floral decals of various pinks and "
        "violets bloom across its surface. 'Guest Room' is written in friendly bubble "
        "letters, welcoming and cheerful—an invitation to travelers and visitors alike."
    )
    guest_plaque.portable = False
    
    # ---------------------------------------------------------------------
    # OUTPUT
    # ---------------------------------------------------------------------
    
    print(f"Built Passageway: {room.dbref}")
    print(f"Connected to Welcome Room: {welcome.dbref}")
    print(f"")
    print(f"Exits:")
    print(f"  out → Welcome Room")
    print(f"  west1 → Helena's Room (placeholder → Limbo)")
    print(f"  west2 → Auria's Room (placeholder → Limbo)")
    print(f"  east1 → Garden of Knowledge (placeholder → Limbo)")
    print(f"  east2 → Guest Room (placeholder → Limbo)")
    print(f"  north → Common Room (placeholder → Limbo)")
    print(f"")
    print(f"Objects: area rug, entry table, wolf figurines, potpourri bowl,")
    print(f"         portrait, scratches, shadow musk (invisible)")
    print(f"")
    print(f"Plaques: Helena's, Auria's, Garden, Guest Room")
    print(f"")
    print(f"Test with:")
    print(f"  @py from world.build_passageway import test_musk; test_musk()")
    print(f"  @py from world.build_passageway import test_portrait; test_portrait()")
    print(f"  @py from world.build_passageway import test_seasons; test_seasons()")
    
    return room


# =============================================================================
# TEST FUNCTIONS
# =============================================================================

def get_passageway():
    """Find the Passageway."""
    results = search_object("Passageway")
    return results[0] if results else None


def test_musk():
    """Test all shadow musk states."""
    room = get_passageway()
    if not room:
        return "Passageway not found."
    
    musk = room._get_shadow_musk()
    if not musk:
        return "Shadow musk not found."
    
    output = []
    for state in ["present", "recent", "fading", "absent"]:
        musk.force_state(state)
        inline = musk.get_inline_desc()
        output.append(f"\n=== {state.upper()} ===")
        output.append(f"Inline: '{inline}'")
    
    print("\n".join(output))
    return musk


def test_portrait():
    """Test portrait viewer-awareness."""
    room = get_passageway()
    if not room:
        return "Passageway not found."
    
    portrait = None
    for obj in room.contents:
        if isinstance(obj, ViewerAwarePortrait):
            portrait = obj
            break
    
    if not portrait:
        return "Portrait not found."
    
    # Create mock lookers
    class MockLooker:
        def __init__(self, key, tags=None):
            self.key = key
            self._tags = tags or []
        
        class MockTags:
            def __init__(self, tags):
                self._tags = tags
            def has(self, tag, category=None):
                return tag in self._tags
        
        @property
        def tags(self):
            return self.MockTags(self._tags)
    
    test_lookers = [
        MockLooker("Stranger"),
        MockLooker("Laynie"),
        MockLooker("Princess"),
        MockLooker("Auria"),
        MockLooker("RandomPerson", ["claimed"]),
    ]
    
    print("=== PORTRAIT VIEWER TEST ===\n")
    for looker in test_lookers:
        addition = portrait.get_viewer_addition(looker)
        print(f"{looker.key}: {addition[:60]}...")
        print()
    
    return portrait


def test_seasons():
    """Test potpourri seasonal scents."""
    room = get_passageway()
    if not room:
        return "Passageway not found."
    
    potpourri = room._get_potpourri()
    if not potpourri:
        return "Potpourri not found."
    
    print("=== SEASONAL SCENTS ===\n")
    for season in ["spring", "summer", "autumn", "winter"]:
        room.current_season = season
        scent = potpourri.get_scent()
        print(f"{season.upper()}: {scent}")
    
    room.current_season = "summer"  # Reset
    return potpourri


def shadow_pass():
    """Simulate Shadow passing through."""
    room = get_passageway()
    if not room:
        return "Passageway not found."
    
    musk = room._get_shadow_musk()
    if not musk:
        return "Shadow musk not found."
    
    old = musk.current_state
    musk.on_shadow_pass()
    print(f"Shadow musk: '{old}' → '{musk.current_state}'")
    return musk


def tick(n=1):
    """Tick musk decay n times."""
    room = get_passageway()
    if not room:
        return "Passageway not found."
    
    musk = room._get_shadow_musk()
    if not musk:
        return "Shadow musk not found."
    
    for i in range(n):
        changed = musk.tick_decay()
        if changed:
            print(f"Tick {i+1}: → '{musk.current_state}'")
    
    print(f"Current state: '{musk.current_state}' (ticks: {musk.decay_ticks})")
    return musk
