"""
Welcome Room Builder - Complete

Creates Helena's Cabin Welcome Room with all custom functionality:
- WolfPrints with decay states (fresh → recent → fading → absent)
- Mirror that shows looker's appearance
- WelcomeRoom with <wolf_prints.desc> shortcode
- Shadow detection triggers wolf prints

Run from Evennia:
    @py from world.build_welcome_room import build; build()

Test wolf prints:
    @py from world.build_welcome_room import test_prints; test_prints()
    @py from world.build_welcome_room import shadow_pass; shadow_pass()
"""

from evennia import create_object, search_object
from evennia.typeclasses.attributes import AttributeProperty
from typeclasses.objects import Object, Furniture, AtmosphericObject
from typeclasses.base_rooms import IndoorRoom


# =============================================================================
# NEW TYPECLASSES
# =============================================================================

class WolfPrints(Object):
    """
    Dynamic wolf prints that track Shadow's passage.
    Decays: fresh → recent → fading → absent
    """
    
    portable = AttributeProperty(default=False)
    weight = AttributeProperty(default="immovable")
    current_state = AttributeProperty(default="absent")
    decay_ticks = AttributeProperty(default=0)
    
    decay_rates = AttributeProperty(default={
        "fresh": 3,
        "recent": 6,
        "fading": 10,
    })
    
    state_descriptions = AttributeProperty(default={
        "fresh": (
            "Fresh muddy wolf prints track from the door, still wet, still sharp. "
            "Shadow has just passed through. The scratches at the threshold are "
            "deeper than usual—pressed hard by something large moving with purpose."
        ),
        "recent": (
            "Muddy wolf prints cross the floor, drying but distinct. Shadow came "
            "through not long ago. The scratches at the threshold catch the light."
        ),
        "fading": (
            "Faint wolf prints mark the floor, mud mostly dried and crumbling. "
            "The scratches at the threshold remain sharp, worn into the wood over time."
        ),
        "absent": (
            "Scratches mark the threshold where the wooden floor changes—claw marks "
            "from something large, worn into the wood over time. No prints today, "
            "but the marks remember."
        ),
    })
    
    short_descriptions = AttributeProperty(default={
        "fresh": "Fresh wolf prints track across the floor, still wet.",
        "recent": "Drying wolf prints mark the floor.",
        "fading": "Faint wolf prints and deep scratches mark the threshold.",
        "absent": "Deep scratches mark the threshold.",
    })
    
    def at_object_creation(self):
        super().at_object_creation()
        self.locks.add("get:false()")
    
    def get_display_name(self, looker=None, **kwargs):
        return self.short_descriptions.get(self.current_state, "Scratches mark the floor.")
    
    def get_examined_desc(self, looker=None) -> str:
        return self.state_descriptions.get(self.current_state, self.state_descriptions["absent"])
    
    def return_appearance(self, looker, **kwargs):
        return f"|w{self.key}|n\n\n{self.get_examined_desc(looker)}"
    
    def on_shadow_pass(self):
        """Called when Shadow moves through the room."""
        old_state = self.current_state
        self.current_state = "fresh"
        self.decay_ticks = 0
        
        if self.location and old_state == "absent":
            self.location.msg_contents(
                "|wFresh muddy prints appear on the floor. Something large just passed through.|n"
            )
    
    def tick_decay(self) -> bool:
        """Process one decay tick. Returns True if state changed."""
        if self.current_state == "absent":
            return False
        
        self.decay_ticks += 1
        threshold = self.decay_rates.get(self.current_state, 10)
        
        if self.decay_ticks >= threshold:
            order = ["fresh", "recent", "fading", "absent"]
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
        if state in self.state_descriptions:
            self.current_state = state
            self.decay_ticks = 0
            return True
        return False


class Mirror(Object):
    """Mirror that shows looker's own appearance."""
    
    portable = AttributeProperty(default=False)
    weight = AttributeProperty(default="heavy")
    mirror_desc = AttributeProperty(default="A mirror hangs on the wall.")
    frame_desc = AttributeProperty(default="")
    
    def return_appearance(self, looker, **kwargs):
        parts = [f"|w{self.key}|n", ""]
        
        # Mirror description
        if self.examined:
            parts.append(self.examined)
        elif self.db.desc:
            parts.append(self.db.desc)
        else:
            parts.append(self.mirror_desc)
        
        if self.frame_desc:
            parts.append("")
            parts.append(self.frame_desc)
        
        # Reflection
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


class CabinBench(Furniture):
    """Bench with cubby storage."""
    
    capacity = AttributeProperty(default=2)
    position_slots = AttributeProperty(default=["sit"])
    position_descs = AttributeProperty(default={"sit": "{name} sits on the bench."})
    cubby_contents = AttributeProperty(default=list)
    
    def return_appearance(self, looker, **kwargs):
        parts = [f"|w{self.key}|n", ""]
        
        # Base description
        if self.examined:
            parts.append(self.examined)
        elif self.db.desc:
            parts.append(self.db.desc)
        
        # Cubbies
        if self.cubby_contents:
            parts.append("")
            parts.append(f"Inside the cubbies: {', '.join(self.cubby_contents)}.")
        
        # Who's sitting
        if self.current_users:
            parts.append("")
            parts.append(self.get_occupied_desc())
        
        return "\n".join(parts)


class PetGearHooks(AtmosphericObject):
    """Coat hooks with hidden pet gear."""
    
    portable = AttributeProperty(default=False)
    
    normal_items = AttributeProperty(default=[
        "furs for cold days", "colored windbreakers", "sweaters", "scarves"
    ])
    pet_gear = AttributeProperty(default=[
        "sturdy leashes", "well-made muzzles", "leather harnesses", 
        "mittens with paw prints on the palms"
    ])
    detailed_desc = AttributeProperty(default=(
        "The leashes are high quality, meant for larger animals—or people. "
        "The muzzles are padded for comfort during extended wear. "
        "The harnesses have multiple attachment points. "
        "Everything is maintained, used, loved."
    ))
    
    def return_appearance(self, looker, **kwargs):
        parts = [f"|w{self.key}|n", ""]
        
        if self.db.desc:
            parts.append(self.db.desc)
        
        parts.append("")
        all_items = self.normal_items + self.pet_gear
        parts.append(f"Hanging here: {', '.join(all_items)}.")
        parts.append("")
        parts.append(self.detailed_desc)
        
        return "\n".join(parts)


class ViewableSign(Object):
    """Sign with hidden detail on examination."""
    
    portable = AttributeProperty(default=False)
    main_inscription = AttributeProperty(default="A sign.")
    hidden_detail = AttributeProperty(default="")
    sign_material = AttributeProperty(default="wooden")
    
    def return_appearance(self, looker, **kwargs):
        parts = [f"|w{self.key}|n", ""]
        
        parts.append(f"A {self.sign_material} sign hangs here.")
        parts.append("")
        parts.append(f'It reads: "|y{self.main_inscription}|n"')
        
        if self.hidden_detail:
            parts.append("")
            parts.append("On closer inspection, you notice:")
            parts.append(f"|x{self.hidden_detail}|n")
        
        return "\n".join(parts)


class CabinLanterns(AtmosphericObject):
    """Atmospheric electric lanterns."""
    
    portable = AttributeProperty(default=False)
    is_active = AttributeProperty(default=True)
    
    ambient_pool = AttributeProperty(default=[
        "The lanterns flicker briefly, casting dancing shadows.",
        "Warm light pools beneath the lanterns.",
        "A lantern sways slightly on its chain.",
    ])


class WelcomeRoom(IndoorRoom):
    """
    Welcome Room with wolf print tracking and Shadow detection.
    
    Shortcodes:
        <wolf_prints.desc> - Current wolf print state
        <wolf_prints.state> - State name
        <time.desc> - Time-appropriate description
    """
    
    region = AttributeProperty(default="Helena's Cabin")
    zone = AttributeProperty(default="Entry")
    shadow_present = AttributeProperty(default=False)
    
    time_descriptions = AttributeProperty(default={
        "dawn": "Early light seeps through. The cabin stirs awake.",
        "morning": "Bright light filters through, the lanterns unnecessary but charming.",
        "midday": "The cabin is bright and comfortable.",
        "afternoon": "Warm and quiet. The lanterns glow softly even in daylight.",
        "evening": "The lanterns come into their own, casting warm pools of light. Home.",
        "night": "Cozy darkness punctuated by lantern light. The world outside is cold; in here, warmth waits.",
    })
    
    def process_shortcodes(self, text: str, looker=None) -> str:
        """Process room shortcodes including wolf prints."""
        text = super().process_shortcodes(text, looker)
        
        # Wolf prints
        wolf_prints = self._get_wolf_prints()
        if wolf_prints:
            text = text.replace("<wolf_prints.desc>", wolf_prints.get_examined_desc(looker))
            text = text.replace("<wolf_prints.state>", wolf_prints.current_state)
        else:
            text = text.replace("<wolf_prints.desc>", "Scratches mark the threshold.")
            text = text.replace("<wolf_prints.state>", "absent")
        
        # Time
        period = self.get_time_period() if hasattr(self, 'get_time_period') else "afternoon"
        time_desc = self.time_descriptions.get(period, "")
        text = text.replace("<time.desc>", time_desc)
        
        return text
    
    def _get_wolf_prints(self):
        """Find wolf prints object."""
        for obj in self.contents:
            if hasattr(obj, 'on_shadow_pass'):
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
        """Trigger wolf prints when Shadow enters."""
        super().at_object_receive(moved_obj, source_location, move_type, **kwargs)
        
        if self._is_shadow(moved_obj):
            self.shadow_present = True
            wolf_prints = self._get_wolf_prints()
            if wolf_prints:
                wolf_prints.on_shadow_pass()
    
    def at_object_leave(self, moved_obj, target_location, move_type=None, **kwargs):
        """Track Shadow leaving."""
        super().at_object_leave(moved_obj, target_location, move_type, **kwargs)
        
        if self._is_shadow(moved_obj):
            self.shadow_present = False
    
    def tick_wolf_prints(self) -> bool:
        """Tick wolf print decay."""
        wolf_prints = self._get_wolf_prints()
        if wolf_prints:
            return wolf_prints.tick_decay()
        return False


# =============================================================================
# BUILD FUNCTION
# =============================================================================

def build():
    """Build Welcome Room with exit from Limbo."""
    
    # Get Limbo
    limbo = search_object("#2")[0]
    
    # Create Welcome Room
    room = create_object(WelcomeRoom, key="Welcome Room")
    
    room.db.desc = """The welcome room of the log cabin is a cozy and intimate space, to transition from the harsh stress and discomforts of the outside world into the relaxation and warmth of home.

To the left of the door, a rustic bench with cubby holes built into its base sits in waiting for the family to sit and remove shoes or unneeded clothes. A large mirror with a decorative golden border rests securely on the wall above it so people can check their appearance before leaving. Opposite of the bench, a series of coat hooks are fastened at shoulder height to the wall. An assortment of furs, colored windbreakers, sweaters and scarves are hung with care as well as a few sturdy leashes, muzzles, harnesses, and mittens with paw prints.

The room is lit by electric lights fashioned to resemble antique lanterns hanging on chains from the ceiling. There is a step up, from the wooden floor of the welcome room's entryway to a passageway leading further into the cabin.

<wolf_prints.desc> A sign hangs above the door stating |y'A Den is not a Home without a Big Bad Wolf'|n.

<time.desc>"""

    room.db.atmosphere = {
        "sounds": "muffled wind outside, crackling fire from deeper within, creaking wood",
        "scents": "wood, warmth, a faint musk of wolf, cold air lingering near the door",
        "mood": "welcoming",
    }
    room.lighting = "normal"
    room.temperature = "warm"
    
    # Exit from Limbo to Welcome Room
    create_object(
        "evennia.objects.objects.DefaultExit",
        key="in",
        location=limbo,
        destination=room,
        aliases=["cabin", "enter"],
    )
    
    # Exit from Welcome Room back to Limbo
    create_object(
        "evennia.objects.objects.DefaultExit",
        key="out",
        location=room,
        destination=limbo,
        aliases=["outside", "leave", "exit"],
    )
    
    # Wolf Prints
    prints = create_object(WolfPrints, key="wolf prints", location=room, 
                          aliases=["prints", "scratches", "tracks", "claw marks"])
    
    # Bench
    bench = create_object(CabinBench, key="rustic bench", location=room,
                         aliases=["bench", "seat"])
    bench.db.desc = "A rustic bench to the left of the door, worn smooth from use."
    bench.examined = "Cubby holes built into its base hold shoes, slippers, and the occasional forgotten item. This is where you sit to remove the outside world before going deeper."
    bench.cubby_contents = ["worn slippers", "a pair of boots", "a forgotten scarf"]
    
    # Mirror
    mirror = create_object(Mirror, key="ornate mirror", location=room,
                          aliases=["mirror", "looking glass"])
    mirror.db.desc = "A large mirror with a decorative golden border, secured to the wall above the bench."
    mirror.examined = "The frame is ornate but not gaudy—elegant, like something from an old estate."
    mirror.frame_desc = "It shows you as you are, one last check before facing the world or one first look at yourself coming home."
    
    # Hooks
    hooks = create_object(PetGearHooks, key="coat hooks", location=room,
                         aliases=["hooks", "coats", "gear", "leashes"])
    hooks.db.desc = "A series of sturdy hooks fastened at shoulder height to the wall. An assortment of outdoor wear hangs with care."
    
    # Lanterns
    lanterns = create_object(CabinLanterns, key="antique lanterns", location=room,
                            aliases=["lanterns", "lights", "lamps"])
    lanterns.db.desc = "Electric lights fashioned to resemble antique lanterns hang on chains from the ceiling."
    lanterns.examined = "They give off warm, flickering light—not real flame, but close enough to feel like it. Someone went to effort to make modern convenience feel like old comfort."
    
    # Sign
    sign = create_object(ViewableSign, key="wooden sign", location=room,
                        aliases=["sign"])
    sign.main_inscription = "A Den is not a Home without a Big Bad Wolf"
    sign.hidden_detail = (
        'Below the main text, in smaller carved letters: '
        '"All who enter with love are welcome. All who enter with ill intent '
        "will meet Her.\" The 'Her' has claw marks through it—playful or warning, hard to tell."
    )
    
    print(f"Built Welcome Room: {room.dbref}")
    print(f"Exits: 'in' from Limbo, 'out' back to Limbo")
    print(f"Objects: wolf prints, bench, mirror, hooks, lanterns, sign")
    print(f"")
    print(f"Test with:")
    print(f"  @py from world.build_welcome_room import test_prints; test_prints()")
    print(f"  @py from world.build_welcome_room import shadow_pass; shadow_pass()")
    
    return room


# =============================================================================
# TEST FUNCTIONS
# =============================================================================

def get_welcome_room():
    """Find the Welcome Room."""
    results = search_object("Welcome Room")
    return results[0] if results else None


def test_prints():
    """Test all wolf print states."""
    room = get_welcome_room()
    if not room:
        return "Welcome Room not found."
    
    prints = room._get_wolf_prints()
    if not prints:
        return "Wolf prints not found."
    
    output = []
    for state in ["fresh", "recent", "fading", "absent"]:
        prints.force_state(state)
        output.append(f"\n=== {state.upper()} ===")
        output.append(prints.get_examined_desc())
    
    print("\n".join(output))
    return prints


def shadow_pass():
    """Simulate Shadow passing through."""
    room = get_welcome_room()
    if not room:
        return "Welcome Room not found."
    
    prints = room._get_wolf_prints()
    if not prints:
        return "Wolf prints not found."
    
    old = prints.current_state
    prints.on_shadow_pass()
    print(f"Wolf prints: '{old}' → '{prints.current_state}'")
    return prints


def tick(n=1):
    """Tick wolf print decay n times."""
    room = get_welcome_room()
    if not room:
        return "Welcome Room not found."
    
    prints = room._get_wolf_prints()
    if not prints:
        return "Wolf prints not found."
    
    for i in range(n):
        changed = prints.tick_decay()
        if changed:
            print(f"Tick {i+1}: → '{prints.current_state}'")
    
    print(f"Current state: '{prints.current_state}' (ticks: {prints.decay_ticks})")
    return prints
