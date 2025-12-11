"""
Helena's Room Builder - Helena's Cabin

Creates Helena's Room with:
- HelenaRoom typeclass with time-variant descriptions
- HelenaBed with dynamic state and decay
- HelenaKennel enterable furniture with interior/exterior views
- HelenaDesk with 4 drawers and mechanism
- TapestryExit toggleable hidden exits
- HiddenTrapdoor mechanism-activated exit
- WallRestraints and PurplePetBed furniture
- All kennel contents (drawings, Eevee plushie, etc.)

Run from Evennia:
    @py from world.build_helenas_room import build; build()

Test functions included at bottom.
"""

import random
from datetime import datetime
from typing import Optional, List

from evennia import create_object, search_object, DefaultScript
from evennia.typeclasses.attributes import AttributeProperty
from evennia.objects.objects import DefaultExit

from typeclasses.objects import Object, Furniture, Container
from typeclasses.rooms import IndoorRoom


# =============================================================================
# TIME VARIANT DATA
# =============================================================================

TIME_DESCRIPTIONS = {
    "morning": (
        "Light filters through gaps in the tapestries. The red silk gleams. "
        "The room smells of Helena's perfume and something earthier—Shadow was here."
    ),
    "afternoon": (
        "Quiet dominion. The desk's toys catch the light. Someone might be "
        "in the kennel below, waiting."
    ),
    "evening": (
        "Candles flicker in their sconces. The tapestries seem to breathe. "
        "The room becomes intimate, dangerous."
    ),
    "night": (
        "Helena's domain fully realized. The bed awaits. The kennel waits. "
        "The shackles wait. Everything waits for her."
    ),
}

# Map world time periods to our time keys
TIME_PERIOD_MAP = {
    "dawn": "morning",
    "morning": "morning",
    "midday": "afternoon",
    "afternoon": "afternoon",
    "evening": "evening",
    "night": "night",
}


# =============================================================================
# BED STATE DATA
# =============================================================================

BED_STATES = ["fresh", "rumpled", "messy", "soaked", "ripped"]

BED_STATE_DESCS = {
    "fresh": (
        "It is currently made with fresh sheets of velvety red silk with a "
        "fluffy blanket atop them—neatly tucked in at the edges."
    ),
    "rumpled": (
        "The red silk sheets are rumpled, the blanket pushed aside—someone "
        "slept here recently."
    ),
    "messy": (
        "The sheets are twisted and damp, wet spots darkening the silk. "
        "The blanket has been kicked half onto the floor."
    ),
    "soaked": (
        "The silk sheets are soaked through, clinging to the mattress. "
        "The scent of sex hangs heavy in the air around it."
    ),
    "ripped": (
        "The sheets are torn, claw marks shredding the red silk. The blanket "
        "lies in tatters. Someone—or something—got very rough."
    ),
}


# =============================================================================
# BED DECAY SCRIPT
# =============================================================================

class BedDecayScript(DefaultScript):
    """
    Ticks bed state toward 'fresh' over time.
    Each tick moves one step: ripped→soaked→messy→rumpled→fresh
    Interval: 30 minutes (1800 seconds)
    """
    
    def at_script_creation(self):
        self.key = "bed_decay"
        self.desc = "Decays bed state toward fresh"
        self.interval = 1800  # 30 minutes
        self.persistent = True
        self.start_delay = True
    
    def at_repeat(self):
        """Called every interval."""
        bed = self.obj
        if not bed:
            self.stop()
            return
        
        current_state = bed.bed_state
        if current_state == "fresh":
            return  # Already clean
        
        # Move one step toward fresh
        current_idx = BED_STATES.index(current_state)
        if current_idx > 0:
            new_state = BED_STATES[current_idx - 1]
            bed.bed_state = new_state
            
            # Notify room
            if bed.location:
                bed.location.msg_contents(
                    f"|xThe bed's state settles somewhat... now {new_state}.|n",
                    exclude=[]
                )


# =============================================================================
# HELENA'S ROOM TYPECLASS
# =============================================================================

class HelenaRoom(IndoorRoom):
    """
    Helena's bedroom - the Alpha's chamber.
    
    Features:
    - Time-variant descriptions
    - Shortcode processing for dynamic elements
    - Kennel interior view when looker is inside
    - Breeze from Birthing Den
    """
    
    def at_object_creation(self):
        super().at_object_creation()
        
        self.db.atmosphere = {
            "preset": "alpha_chamber",
            "sounds": "creaking bed frame, chains clinking, muffled sounds, breathing",
            "scents": "Helena's perfume, Shadow's musk, leather, silk",
            "mood": "dominion",
        }
        self.db.temperature = "warm"
        self.db.lighting = "candlelight and filtered natural"
    
    def get_time_key(self) -> str:
        """Get current time key for descriptions."""
        try:
            from world.world_state import get_world_state
            world = get_world_state()
            if world:
                period = world.get_time_period()
                return TIME_PERIOD_MAP.get(period, "afternoon")
        except (ImportError, AttributeError):
            pass
        
        # Fallback to real time
        hour = datetime.now().hour
        if 5 <= hour < 12:
            return "morning"
        elif 12 <= hour < 17:
            return "afternoon"
        elif 17 <= hour < 21:
            return "evening"
        else:
            return "night"
    
    def get_bed(self):
        """Find the bed in this room."""
        for obj in self.contents:
            if isinstance(obj, HelenaBed):
                return obj
        return None
    
    def get_kennel(self):
        """Find the kennel in this room."""
        for obj in self.contents:
            if isinstance(obj, HelenaKennel):
                return obj
        return None
    
    def get_trapdoor(self):
        """Find the trapdoor exit."""
        for obj in self.contents:
            if isinstance(obj, HiddenTrapdoor):
                return obj
        return None
    
    def get_tapestries(self):
        """Find all tapestry exits."""
        return [obj for obj in self.contents if isinstance(obj, TapestryExit)]
    
    def process_shortcodes(self, text: str, looker=None) -> str:
        """Process room description shortcodes."""
        if hasattr(super(), 'process_shortcodes'):
            text = super().process_shortcodes(text, looker)
        
        # <time.desc>
        time_key = self.get_time_key()
        time_desc = TIME_DESCRIPTIONS.get(time_key, TIME_DESCRIPTIONS["afternoon"])
        text = text.replace("<time.desc>", time_desc)
        
        # <bed.state>
        bed = self.get_bed()
        if bed:
            bed_desc = BED_STATE_DESCS.get(bed.bed_state, BED_STATE_DESCS["fresh"])
        else:
            bed_desc = BED_STATE_DESCS["fresh"]
        text = text.replace("<bed.state>", bed_desc)
        
        # <tapestry_north.state>, <tapestry_south.state>, <tapestry_east.state>
        for tap in self.get_tapestries():
            direction = tap.db.direction or "north"
            shortcode = f"<tapestry_{direction}.state>"
            if tap.is_open:
                state_text = tap.db.open_inline or ""
            else:
                state_text = ""
            text = text.replace(shortcode, state_text)
        
        # <trapdoor.state>
        trapdoor = self.get_trapdoor()
        if trapdoor and trapdoor.is_revealed:
            trap_text = (
                "\n\nNear the desk, a trapdoor in the floor stands open—a dark "
                "square revealing stone steps that descend into the Hidden "
                "Laboratory below. Cold air rises from the darkness."
            )
        else:
            trap_text = ""
        text = text.replace("<trapdoor.state>", trap_text)
        
        return text
    
    def return_appearance(self, looker, **kwargs):
        """Return room description, checking if looker is inside kennel."""
        kennel = self.get_kennel()
        
        # Check if looker is inside the kennel
        if kennel and kennel.is_character_inside(looker):
            return kennel.get_interior_view(looker)
        
        # Normal room view
        appearance = super().return_appearance(looker, **kwargs)
        appearance = self.process_shortcodes(appearance, looker)
        
        return appearance


# =============================================================================
# HELENA'S BED
# =============================================================================

class HelenaBed(Furniture):
    """
    The huge canopied bed with dynamic state.
    
    States: fresh, rumpled, messy, soaked, ripped
    Decay: Automatic via BedDecayScript (30 min per step toward fresh)
    """
    
    portable = AttributeProperty(default=False)
    weight = AttributeProperty(default="immovable")
    
    capacity = AttributeProperty(default=4)
    position_slots = AttributeProperty(default=[
        "lying", "lying at edge", "on all fours", "spread-eagle",
        "riding", "face-down", "pinned"
    ])
    
    bed_state = AttributeProperty(default="fresh")
    
    # Restraint points
    restraint_points = AttributeProperty(default=[
        "bedpost (corner)",
        "headboard",
        "canopy frame",
        "kennel bars (below)",
    ])
    
    def at_object_creation(self):
        super().at_object_creation()
        
        self.db.desc = (
            "A huge canopied bed supporting a thick king sized mattress, "
            "centered opposite the door. A wide assortment of fluffed soft "
            "pillows are distributed evenly—though some have been chewed and "
            "torn, stuffing poking free. The canopy bed is supported by a "
            "large kennel comprised of vertical bars, its cell door at the "
            "foot of the bed."
        )
        
        self.aliases.add("bed")
        self.aliases.add("canopy bed")
        self.aliases.add("canopied bed")
        
        # Start decay script
        self.scripts.add(BedDecayScript, key="bed_decay")
    
    def get_state_desc(self) -> str:
        """Get current state description."""
        return BED_STATE_DESCS.get(self.bed_state, BED_STATE_DESCS["fresh"])
    
    def soil(self) -> str:
        """Make the bed messier (called after activity)."""
        current_idx = BED_STATES.index(self.bed_state)
        if current_idx < len(BED_STATES) - 1:
            self.bed_state = BED_STATES[current_idx + 1]
            return f"The bed becomes {self.bed_state}."
        return "The bed can't get any messier."
    
    def clean(self) -> str:
        """Clean the bed one step."""
        current_idx = BED_STATES.index(self.bed_state)
        if current_idx > 0:
            self.bed_state = BED_STATES[current_idx - 1]
            return f"You tidy up the bed. It's now {self.bed_state}."
        return "The bed is already fresh."
    
    def clean_fully(self) -> str:
        """Clean the bed completely."""
        self.bed_state = "fresh"
        return "You change the sheets and make the bed properly. Fresh and ready."
    
    def rip(self) -> str:
        """Rip the sheets (rough activity)."""
        self.bed_state = "ripped"
        return "The sheets tear under the force. Claw marks shred the silk."
    
    def return_appearance(self, looker, **kwargs):
        parts = [f"|w{self.key}|n", ""]
        parts.append(self.db.desc)
        parts.append("")
        parts.append(f"|xCurrent state:|n {self.get_state_desc()}")
        
        if hasattr(self, 'current_users') and self.current_users:
            parts.append("")
            parts.append(self.get_occupied_desc())
        
        return "\n".join(parts)


# =============================================================================
# HELENA'S KENNEL (ENTERABLE)
# =============================================================================

class HelenaKennel(Furniture):
    """
    The kennel beneath the bed - enterable furniture.
    
    Characters can 'enter kennel' to go inside.
    When inside, 'look' shows interior description.
    Contains Princess's hideaway objects.
    Curtain at back leads to Birthing Den.
    """
    
    portable = AttributeProperty(default=False)
    weight = AttributeProperty(default="immovable")
    
    capacity = AttributeProperty(default=2)
    position_slots = AttributeProperty(default=[
        "inside", "curled up inside", "kneeling inside", "lying inside",
        "face at bars", "displayed"
    ])
    
    # Kennel state
    is_locked = AttributeProperty(default=False)
    curtain_open = AttributeProperty(default=False)
    
    # Track who is inside (by character id)
    inside_characters = AttributeProperty(default=list)
    
    def at_object_creation(self):
        super().at_object_creation()
        
        self.db.desc = (
            "Beneath the bed, a kennel of vertical bars forms a cage. The "
            "cell door is at the foot of the bed. Inside, everything needed "
            "for a pet's comfort—and traces of someone who made it her own."
        )
        
        self.db.interior_desc = (
            "The space beneath Helena's bed has been transformed. Deep gouges "
            "from claws in the wooden floorboards have been filled in with "
            "colorful crayon wax. Drawings litter the floor and are taped to "
            "the bars with something sticky.\n\n"
            "A blanket and pillow rest in the corner, stained with old tears. "
            "The handmade Eevee plushie sits nearby, violet panties still on "
            "its head.\n\n"
            "|mThe signs of a little girl who waited so long to be remembered, "
            "loved, and brought back home.|n"
        )
        
        self.aliases.add("kennel")
        self.aliases.add("cage")
    
    def is_character_inside(self, character) -> bool:
        """Check if character is inside the kennel."""
        char_id = character.id if hasattr(character, 'id') else None
        if char_id:
            return char_id in self.inside_characters
        return False
    
    def enter_kennel(self, character) -> tuple[bool, str]:
        """Have a character enter the kennel."""
        if self.is_locked:
            return (False, "The kennel door is locked.")
        
        if self.is_character_inside(character):
            return (False, "You're already inside the kennel.")
        
        if len(self.inside_characters) >= self.capacity:
            return (False, "The kennel is too crowded.")
        
        char_id = character.id if hasattr(character, 'id') else None
        if char_id:
            chars = list(self.inside_characters)
            chars.append(char_id)
            self.inside_characters = chars
        
        return (True, 
            "You crawl through the kennel door and into the space beneath "
            "the bed. The bars close around you. Through them, you can see, "
            "hear, and smell everything in Helena's room above."
        )
    
    def leave_kennel(self, character) -> tuple[bool, str]:
        """Have a character leave the kennel."""
        if not self.is_character_inside(character):
            return (False, "You're not inside the kennel.")
        
        if self.is_locked:
            return (False, "The kennel door is locked. You're trapped inside.")
        
        char_id = character.id if hasattr(character, 'id') else None
        if char_id:
            chars = list(self.inside_characters)
            if char_id in chars:
                chars.remove(char_id)
            self.inside_characters = chars
        
        return (True, "You crawl out of the kennel, leaving the small space behind.")
    
    def lock(self) -> str:
        """Lock the kennel from outside."""
        if self.is_locked:
            return "The kennel is already locked."
        self.is_locked = True
        return "You lock the kennel door. Click."
    
    def unlock(self) -> str:
        """Unlock the kennel from outside."""
        if not self.is_locked:
            return "The kennel is already unlocked."
        self.is_locked = False
        return "You unlock the kennel door."
    
    def open_curtain(self) -> str:
        """Open the curtain at the back."""
        if self.curtain_open:
            return "The curtain is already open."
        self.curtain_open = True
        return (
            "You draw back the heavy curtain, revealing a dark tunnel "
            "descending into the earth. The breeze flows freely now, "
            "carrying the unmistakable scent of the den below."
        )
    
    def close_curtain(self) -> str:
        """Close the curtain."""
        if not self.curtain_open:
            return "The curtain is already closed."
        self.curtain_open = False
        return "You let the curtain fall back into place. It sways gently in the breeze."
    
    def get_interior_view(self, looker) -> str:
        """Get the view from inside the kennel."""
        parts = [
            "|wInside the Kennel|n",
            "",
            self.db.interior_desc,
            "",
        ]
        
        # Curtain state
        if self.curtain_open:
            parts.append(
                "The heavy curtain at the back is drawn aside, revealing a "
                "dark tunnel descending into the earth. The breeze flows "
                "freely, carrying scents of the Birthing Den below."
            )
        else:
            parts.append(
                "At the back, a heavy curtain sways gently in a cool breeze. "
                "Something lies beyond."
            )
        
        parts.append("")
        
        # View of room through bars
        parts.append("|xThrough the bars, you see:|n")
        parts.append(
            "Helena's room spreads before you—the desk with its toys, the "
            "tapestries on the walls, the wall restraints. You can see, hear, "
            "and smell everything. But you're in here. Caged. Waiting."
        )
        
        # Lock state
        parts.append("")
        if self.is_locked:
            parts.append("|rThe kennel door is locked.|n")
        else:
            parts.append("|gThe kennel door is unlocked.|n")
        
        # Others inside
        others_inside = []
        for char_id in self.inside_characters:
            if char_id != looker.id:
                char = search_object(f"#{char_id}")
                if char:
                    others_inside.append(char[0].key)
        
        if others_inside:
            parts.append(f"Also inside: {', '.join(others_inside)}")
        
        # Exits
        parts.append("")
        parts.append("|wExits:|n")
        if not self.is_locked:
            parts.append("  [out] - Crawl out of the kennel")
        if self.curtain_open:
            parts.append("  [curtain/down] - Birthing Den")
        
        return "\n".join(parts)
    
    def get_exterior_desc(self) -> str:
        """Get description when looking from outside."""
        parts = [self.db.desc]
        
        # Who's inside?
        if self.inside_characters:
            inside_names = []
            for char_id in self.inside_characters:
                char = search_object(f"#{char_id}")
                if char:
                    inside_names.append(char[0].key)
            if inside_names:
                parts.append(f"\n|xInside the kennel:|n {', '.join(inside_names)}")
        
        # Lock state
        if self.is_locked:
            parts.append("\n|rThe door is locked.|n")
        
        return "".join(parts)
    
    def return_appearance(self, looker, **kwargs):
        """Show kennel - interior if inside, exterior otherwise."""
        if self.is_character_inside(looker):
            return self.get_interior_view(looker)
        else:
            return f"|w{self.key}|n\n\n{self.get_exterior_desc()}"


# =============================================================================
# HELENA'S DESK
# =============================================================================

class HelenaDesk(Furniture):
    """
    Metal desk with toys and 4 drawers.
    Drawer 4 contains mechanism to reveal trapdoor.
    """
    
    portable = AttributeProperty(default=False)
    weight = AttributeProperty(default="immovable")
    
    capacity = AttributeProperty(default=1)
    position_slots = AttributeProperty(default=[
        "seated", "bent over", "displayed atop"
    ])
    
    # Drawer states
    drawer_open = AttributeProperty(default=[False, False, False, False])
    
    def at_object_creation(self):
        super().at_object_creation()
        
        self.db.desc = (
            "A metal desk a few steps from the bed, its surface covered with "
            "toys—dildos, vibrators, whips and feathers, large strap-ons, a "
            "black and purple cat o' nine tails. Four drawers are built into "
            "the front."
        )
        
        self.db.drawer_contents = {
            1: "Paddles, crops, canes—discipline implements arranged with care.",
            2: "Medical items: sounds, speculums, gloves, bottles of lube.",
            3: "Keys on rings, leashes coiled neatly, various leads.",
            4: "Private items, personal effects. A small lever is visible at the back.",
        }
        
        self.aliases.add("desk")
        self.aliases.add("metal desk")
    
    def open_drawer(self, num: int) -> tuple[bool, str]:
        """Open a drawer."""
        if num < 1 or num > 4:
            return (False, "Drawers are numbered 1-4.")
        
        idx = num - 1
        states = list(self.drawer_open)
        
        if states[idx]:
            return (False, f"Drawer {num} is already open.")
        
        states[idx] = True
        self.drawer_open = states
        
        contents = self.db.drawer_contents.get(num, "Empty.")
        return (True, f"You open drawer {num}.\n\n|xContents:|n {contents}")
    
    def close_drawer(self, num: int) -> tuple[bool, str]:
        """Close a drawer."""
        if num < 1 or num > 4:
            return (False, "Drawers are numbered 1-4.")
        
        idx = num - 1
        states = list(self.drawer_open)
        
        if not states[idx]:
            return (False, f"Drawer {num} is already closed.")
        
        states[idx] = False
        self.drawer_open = states
        return (True, f"You close drawer {num}.")
    
    def use_mechanism(self, user) -> str:
        """Pull the lever in drawer 4 to toggle trapdoor."""
        # Check if drawer 4 is open
        if not self.drawer_open[3]:
            return "You need to open drawer 4 first."
        
        # Find trapdoor in room
        if not self.location:
            return "Something is wrong."
        
        trapdoor = None
        for obj in self.location.contents:
            if isinstance(obj, HiddenTrapdoor):
                trapdoor = obj
                break
        
        if not trapdoor:
            return "The lever clicks, but nothing happens."
        
        # Toggle trapdoor
        if trapdoor.is_revealed:
            trapdoor.is_revealed = False
            return (
                "You pull the lever. With a heavy thunk, the trapdoor swings "
                "closed, sealing the passage to the laboratory below."
            )
        else:
            trapdoor.is_revealed = True
            return (
                "You pull the lever. A click, then a grinding sound—a trapdoor "
                "in the floor swings open, revealing stone steps descending "
                "into darkness. Cold air rises from below."
            )
    
    def return_appearance(self, looker, **kwargs):
        parts = [f"|w{self.key}|n", ""]
        parts.append(self.db.desc)
        
        # Show drawer states
        parts.append("")
        parts.append("|xDrawers:|n")
        for i, is_open in enumerate(self.drawer_open):
            state = "open" if is_open else "closed"
            parts.append(f"  Drawer {i+1}: {state}")
            if is_open:
                contents = self.db.drawer_contents.get(i+1, "Empty.")
                parts.append(f"    → {contents}")
        
        return "\n".join(parts)


# =============================================================================
# TAPESTRY EXIT
# =============================================================================

class TapestryExit(DefaultExit):
    """
    A tapestry that hides an exit.
    When closed: appears as object, exit not usable
    When open: exit visible and usable
    Persists state.
    """
    
    is_open = AttributeProperty(default=False)
    
    def at_object_creation(self):
        super().at_object_creation()
        self.locks.add("traverse:tapestry_open()")
    
    def at_traverse(self, traversing_object, target_location, **kwargs):
        """Check if tapestry is open before allowing traverse."""
        if not self.is_open:
            traversing_object.msg(
                "The tapestry hangs in place, hiding whatever lies beyond. "
                "You'd need to move it aside first."
            )
            return False
        return super().at_traverse(traversing_object, target_location, **kwargs)
    
    def toggle(self) -> str:
        """Toggle tapestry open/closed."""
        if self.is_open:
            self.is_open = False
            return self.db.close_msg or "You let the tapestry fall back into place."
        else:
            self.is_open = True
            return self.db.open_msg or "You push the tapestry aside, revealing a doorway."
    
    def return_appearance(self, looker, **kwargs):
        parts = [f"|w{self.key}|n", ""]
        parts.append(self.db.desc or "An elaborate tapestry.")
        
        if self.is_open:
            parts.append("")
            parts.append(f"|xThe tapestry is pushed aside, revealing a doorway.|n")
            parts.append(f"Exit leads to: {self.destination.key if self.destination else 'Unknown'}")
        
        return "\n".join(parts)


# =============================================================================
# HIDDEN TRAPDOOR
# =============================================================================

class HiddenTrapdoor(DefaultExit):
    """
    A trapdoor hidden in the floor.
    Only visible/usable when revealed by mechanism.
    """
    
    is_revealed = AttributeProperty(default=False)
    
    def at_traverse(self, traversing_object, target_location, **kwargs):
        """Only allow traverse if revealed."""
        if not self.is_revealed:
            traversing_object.msg("There's no visible exit there.")
            return False
        return super().at_traverse(traversing_object, target_location, **kwargs)
    
    def return_appearance(self, looker, **kwargs):
        if not self.is_revealed:
            return "You don't see that here."
        
        return (
            "|wTrapdoor|n\n\n"
            "A trapdoor stands open in the floor near the desk. Stone steps "
            "descend into darkness below—the Hidden Laboratory awaits. Cold "
            "air rises from the depths."
        )
    
    def get_display_name(self, looker=None, **kwargs):
        if not self.is_revealed:
            return ""  # Hidden
        return "trapdoor"


# =============================================================================
# WALL RESTRAINTS
# =============================================================================

class WallRestraints(Furniture):
    """
    Two collars on chains + four floor shackles.
    Capacity 2 - two people side by side.
    """
    
    portable = AttributeProperty(default=False)
    weight = AttributeProperty(default="immovable")
    
    capacity = AttributeProperty(default=2)
    position_slots = AttributeProperty(default=[
        "standing chained", "kneeling chained", "spread on floor", "displayed"
    ])
    
    restraint_points = AttributeProperty(default=[
        "collar chain (left)",
        "collar chain (right)",
        "floor shackle (left wrist)",
        "floor shackle (right wrist)",
        "floor shackle (left ankle)",
        "floor shackle (right ankle)",
    ])
    
    def at_object_creation(self):
        super().at_object_creation()
        
        self.db.desc = (
            "Two collars on chains are bolted to the northern wall, perfectly "
            "aligned with four sets of shackles bolted to the floor. The "
            "shackles are about a meter apart from each other and half a "
            "meter from the wall. Room for two, side by side."
        )
        
        self.aliases.add("restraints")
        self.aliases.add("chains")
        self.aliases.add("shackles")
        self.aliases.add("wall chains")


# =============================================================================
# PURPLE PET BED
# =============================================================================

class PurplePetBed(Furniture):
    """
    Large circular pet bed near the wall restraints.
    """
    
    portable = AttributeProperty(default=False)
    weight = AttributeProperty(default="heavy")
    
    capacity = AttributeProperty(default=3)
    position_slots = AttributeProperty(default=[
        "curled up", "lying", "cuddling", "squeezed in"
    ])
    
    def at_object_creation(self):
        super().at_object_creation()
        
        self.db.desc = (
            "A large circular pet bed in purple, set near the wall restraints. "
            "Large enough for two to curl up easily—three could fit with some "
            "squishiness."
        )
        
        self.aliases.add("pet bed")
        self.aliases.add("purple bed")
        self.aliases.add("dog bed")


# =============================================================================
# KENNEL CONTENTS - VIEWABLE OBJECTS
# =============================================================================

class KennelDrawings(Object):
    """Princess's drawings taped to the kennel bars."""
    
    portable = AttributeProperty(default=False)
    
    def at_object_creation(self):
        super().at_object_creation()
        
        self.db.desc = (
            "Drawings litter the floor and are taped to the bars with something "
            "sticky. Crayon on paper. A little girl's art."
        )
        
        self.db.examine_desc = (
            "Childish but heartfelt drawings:\n\n"
            "• Three figures cuddling in snow: a Faerie, a huge black Wolf, "
            "and a little blonde girl\n"
            "• A big bed with someone small underneath, waiting\n"
            "• Hearts and 'mommy' and 'sissy' in wobbly letters\n"
            "• A wolf with a huge red crayon addition between its legs\n"
            "• 'I miss you' over and over in different colors"
        )
        
        self.aliases.add("drawings")
        self.aliases.add("pictures")
    
    def return_appearance(self, looker, **kwargs):
        return f"|wPrincess's Drawings|n\n\n{self.db.examine_desc}"


class EeveePlushie(Object):
    """The handmade Eevee with Auria's worn panties."""
    
    portable = AttributeProperty(default=True)
    
    def at_object_creation(self):
        super().at_object_creation()
        
        self.db.desc = (
            "A crudely handmade brown dog-fox stuffed animal, clearly meant "
            "to be the Pokémon Eevee. The stitching is uneven, made with love "
            "and desperation."
        )
        
        self.db.examine_desc = (
            "A crudely handmade brown dog-fox stuffed animal, clearly meant "
            "to be the Pokémon Eevee. The stitching is uneven, made with love "
            "and desperation.\n\n"
            "On its head sits a pair of violet-striped panties—Auria's, stolen, "
            "worn thin from being sucked on. The crotch is nearly gone, full "
            "of holes.\n\n"
            "|mA comfort object for a little girl who needed something of her "
            "sister while she waited alone.|n"
        )
        
        self.aliases.add("eevee")
        self.aliases.add("plushie")
        self.aliases.add("stuffie")
        self.aliases.add("stuffed animal")
    
    def return_appearance(self, looker, **kwargs):
        return f"|wHandmade Eevee Plushie|n\n\n{self.db.examine_desc}"


class TearStainedBlanket(Object):
    """The blanket and pillow in the kennel."""
    
    portable = AttributeProperty(default=False)
    
    def at_object_creation(self):
        super().at_object_creation()
        
        self.db.desc = (
            "A blanket and pillow rest in the corner, stained with old tears. "
            "The fabric is soft but worn, carrying the weight of lonely nights."
        )
        
        self.aliases.add("blanket")
        self.aliases.add("pillow")
        self.aliases.add("bedding")


class CrayonGouges(Object):
    """The claw gouges filled with crayon wax."""
    
    portable = AttributeProperty(default=False)
    
    def at_object_creation(self):
        super().at_object_creation()
        
        self.db.desc = (
            "Deep gouges from claws in the wooden floorboards have been filled "
            "in with colorful crayon wax. A little girl made the scary marks "
            "into something pretty. Made the beast's space her own."
        )
        
        self.aliases.add("gouges")
        self.aliases.add("crayon")
        self.aliases.add("claw marks")


# =============================================================================
# ROOM OBJECTS - VIEWABLE
# =============================================================================

class ClawGouges(Object):
    """The claw gouges in the room floor."""
    
    portable = AttributeProperty(default=False)
    
    def at_object_creation(self):
        super().at_object_creation()
        
        self.db.desc = (
            "The wooden floors have been deeply gouged by sharp claws near "
            "the door and around the edges of furniture. Something large lives "
            "here. Something with claws. The marks are old but maintained—she "
            "doesn't fix them. They're meant to be there."
        )
        
        self.aliases.add("gouges")
        self.aliases.add("claw marks")
        self.aliases.add("scratches")


class ChewedPillows(Object):
    """The chewed pillows on the bed."""
    
    portable = AttributeProperty(default=False)
    
    def at_object_creation(self):
        super().at_object_creation()
        
        self.db.desc = (
            "A wide assortment of fluffed soft pillows on the bed. Some have "
            "been chewed and torn with stuffing poking free. Wolf behavior. "
            "Pet behavior. The bed belongs to someone who shares it with beasts."
        )
        
        self.aliases.add("pillows")


# =============================================================================
# KENNEL CURTAIN EXIT
# =============================================================================

class KennelCurtainExit(DefaultExit):
    """
    Exit from inside the kennel to Birthing Den.
    Only usable if:
    1. Character is inside the kennel
    2. Curtain is open
    """
    
    def at_traverse(self, traversing_object, target_location, **kwargs):
        """Check conditions before allowing traverse."""
        # Find the kennel
        kennel = None
        if self.location:
            for obj in self.location.contents:
                if isinstance(obj, HelenaKennel):
                    kennel = obj
                    break
        
        if not kennel:
            traversing_object.msg("You can't go that way.")
            return False
        
        if not kennel.is_character_inside(traversing_object):
            traversing_object.msg("You need to be inside the kennel to use that exit.")
            return False
        
        if not kennel.curtain_open:
            traversing_object.msg("The curtain is closed. You can't see what's beyond.")
            return False
        
        # Remove from kennel tracking
        kennel.leave_kennel(traversing_object)
        
        return super().at_traverse(traversing_object, target_location, **kwargs)


# =============================================================================
# BUILD FUNCTION
# =============================================================================

def build():
    """Build Helena's Room with all objects and connections."""
    
    # Get or create Limbo for placeholder destinations
    limbo = search_object("#2")
    limbo = limbo[0] if limbo else None
    
    # Find Passageway
    passageway = search_object("Passageway")
    passageway = passageway[0] if passageway else limbo
    
    # -------------------------------------------------------------------------
    # CREATE ROOM
    # -------------------------------------------------------------------------
    
    room = create_object(HelenaRoom, key="Helena's Room")
    
    room.db.desc = """Behind the heavy iron reinforced door on the western side of the Passageway is the room belonging to the cabin's resident Elven Domme and Alpha.

This chamber, unlike the rest of the cabin's rustic charms, is a mix of elegance and sexual deviance. The wooden floors have been deeply gouged by sharp |cclaws|n near the door and around the edges of the furniture in the room.

A huge |ccanopied bed|n supporting a thick king sized mattress is centered opposite of the door. <bed.state> A wide assortment of fluffed soft |cpillows|n are distributed evenly on the bed, though some have been chewed and torn with stuffing poking free of their casing. The canopied bed as a whole is supported by a large |ckennel|n comprised of vertical bars, its cell door at the foot of the bed.

A few steps to the left of the bed, a metal |cdesk|n resides with a large assortment of toys atop it; sexual objects and devices ranging from dildos, vibrators, whips and feathers to large strap-ons and a black and purple cat 'o nine tails. Four drawers in the desk hint that there may be secrets hidden only known to their owner.<trapdoor.state>

Elaborate |ctapestries|n hang on three walls. The |cnorthern tapestry|n bears H.S. in stylized gothic letters surrounded by wolf paw prints and chain motifs<tapestry_north.state>. The |csouthern tapestry|n is torn worse than the others—large fangs have shredded the fabric in places<tapestry_south.state>. The |ceastern tapestry|n is newer than its siblings but already shows Shadow's marks<tapestry_east.state>. All bear Helena's insignia.

Two |ccollars on chains|n are bolted to the northern wall and are perfectly aligned with four sets of |cshackles|n that are bolted to the floor. The shackles are about a meter apart from each other and half a meter from the wall. Next to the chains is a large circular |cpet bed|n, purple in color. The pet bed is large enough for two to curl up easy. Three could fit with a little squishyness.

A cool breeze drifts through the room from somewhere below—the kennel, perhaps. It carries the scent of earth and something primal.

<time.desc>"""
    
    # -------------------------------------------------------------------------
    # MAIN EXIT - TO PASSAGEWAY
    # -------------------------------------------------------------------------
    
    exit_out = create_object(
        DefaultExit,
        key="out",
        location=room,
        destination=passageway,
        aliases=["east", "e", "door", "passageway"],
    )
    exit_out.db.desc = (
        "The heavy iron-reinforced door leads east back to the Passageway. "
        "H.S. in gothic letters watches you leave."
    )
    
    # Update Passageway exit to point here
    if passageway and passageway != limbo:
        for exit_obj in passageway.exits:
            if exit_obj.key in ["west1", "w1"]:
                exit_obj.destination = room
                print(f"Updated Passageway exit to point to Helena's Room")
                break
    
    # -------------------------------------------------------------------------
    # FURNITURE
    # -------------------------------------------------------------------------
    
    # Bed
    bed = create_object(HelenaBed, key="canopied bed", location=room)
    
    # Kennel
    kennel = create_object(HelenaKennel, key="kennel", location=room)
    
    # Desk
    desk = create_object(HelenaDesk, key="metal desk", location=room)
    
    # Pet Bed
    pet_bed = create_object(PurplePetBed, key="purple pet bed", location=room)
    
    # Wall Restraints
    restraints = create_object(WallRestraints, key="wall chains", location=room)
    
    # -------------------------------------------------------------------------
    # TAPESTRY EXITS
    # -------------------------------------------------------------------------
    
    # North - to Nursery
    tap_north = create_object(
        TapestryExit,
        key="northern tapestry",
        location=room,
        destination=limbo,
        aliases=["north tapestry", "north", "n", "nursery"],
    )
    tap_north.db.direction = "north"
    tap_north.db.desc = (
        "The northern tapestry bears H.S. in stylized gothic letters "
        "surrounded by wolf paw prints and chain motifs. The oldest of "
        "the three, its colors slightly faded."
    )
    tap_north.db.open_msg = (
        "You push the northern tapestry aside, revealing a doorway to the Nursery."
    )
    tap_north.db.close_msg = "You let the northern tapestry fall back into place."
    tap_north.db.open_inline = "—pushed aside, revealing a doorway to the Nursery"
    
    # South - to Disciplination Room
    tap_south = create_object(
        TapestryExit,
        key="southern tapestry",
        location=room,
        destination=limbo,
        aliases=["south tapestry", "south", "s", "disciplination"],
    )
    tap_south.db.direction = "south"
    tap_south.db.desc = (
        "The southern tapestry is torn worse than the others—large fangs "
        "have shredded the fabric in places. Shadow's favorite, perhaps."
    )
    tap_south.db.open_msg = (
        "You push the southern tapestry aside, exposing the entrance to "
        "the Disciplination Room."
    )
    tap_south.db.close_msg = "You let the southern tapestry fall back into place."
    tap_south.db.open_inline = "—pushed aside, exposing the entrance to the Disciplination Room"
    
    # East - to Momo's Room
    tap_east = create_object(
        TapestryExit,
        key="eastern tapestry",
        location=room,
        destination=limbo,
        aliases=["east tapestry", "momo", "momos room"],
    )
    tap_east.db.direction = "east"
    tap_east.db.desc = (
        "The eastern tapestry is newer than its siblings but already shows "
        "Shadow's marks. A temporary addition."
    )
    tap_east.db.open_msg = (
        "You pull back the eastern tapestry, revealing a door to Momo's Room."
    )
    tap_east.db.close_msg = "You let the eastern tapestry fall back into place."
    tap_east.db.open_inline = "—pulled back, revealing a door to Momo's Room"
    
    # -------------------------------------------------------------------------
    # HIDDEN TRAPDOOR
    # -------------------------------------------------------------------------
    
    trapdoor = create_object(
        HiddenTrapdoor,
        key="trapdoor",
        location=room,
        destination=limbo,
        aliases=["down", "d", "laboratory", "lab"],
    )
    trapdoor.db.desc = (
        "A trapdoor stands open in the floor, stone steps descending into "
        "darkness—the Hidden Laboratory."
    )
    
    # -------------------------------------------------------------------------
    # KENNEL CURTAIN EXIT
    # -------------------------------------------------------------------------
    
    curtain_exit = create_object(
        KennelCurtainExit,
        key="curtain",
        location=room,
        destination=limbo,
        aliases=["birthing den", "den", "tunnel"],
    )
    curtain_exit.db.desc = "The passage through the curtain to the Birthing Den."
    
    # -------------------------------------------------------------------------
    # KENNEL CONTENTS
    # -------------------------------------------------------------------------
    
    # Note: These are in the room but conceptually "in" the kennel
    # Access is controlled by commands checking if you're inside
    
    drawings = create_object(KennelDrawings, key="Princess's drawings", location=room)
    drawings.db.in_kennel = True
    
    eevee = create_object(EeveePlushie, key="handmade Eevee plushie", location=room)
    eevee.db.in_kennel = True
    
    blanket = create_object(TearStainedBlanket, key="tear-stained blanket", location=room)
    blanket.db.in_kennel = True
    
    kennel_gouges = create_object(CrayonGouges, key="crayon-filled gouges", location=room)
    kennel_gouges.db.in_kennel = True
    
    # -------------------------------------------------------------------------
    # ROOM OBJECTS
    # -------------------------------------------------------------------------
    
    claw_marks = create_object(ClawGouges, key="claw gouges", location=room)
    pillows = create_object(ChewedPillows, key="chewed pillows", location=room)
    
    # -------------------------------------------------------------------------
    # OUTPUT
    # -------------------------------------------------------------------------
    
    print(f"Built Helena's Room: {room.dbref}")
    print(f"")
    print(f"Furniture:")
    print(f"  canopied bed (state system, decay script)")
    print(f"  kennel (enterable, lockable, curtain)")
    print(f"  metal desk (4 drawers, mechanism)")
    print(f"  purple pet bed")
    print(f"  wall chains (restraints)")
    print(f"")
    print(f"Exits:")
    print(f"  out/east → Passageway")
    print(f"  northern tapestry → Nursery (Limbo)")
    print(f"  southern tapestry → Disciplination Room (Limbo)")
    print(f"  eastern tapestry → Momo's Room (Limbo)")
    print(f"  trapdoor → Laboratory (Limbo, hidden)")
    print(f"  curtain → Birthing Den (Limbo, from kennel)")
    print(f"")
    print(f"Kennel contents:")
    print(f"  drawings, Eevee plushie, blanket, crayon gouges")
    print(f"")
    print(f"Commands needed: helena_room_commands.py")
    
    return room


# =============================================================================
# TEST FUNCTIONS
# =============================================================================

def get_room():
    """Find Helena's Room."""
    results = search_object("Helena's Room")
    return results[0] if results else None


def test_bed():
    """Test bed state system."""
    room = get_room()
    if not room:
        return "Room not found."
    
    bed = room.get_bed()
    if not bed:
        return "Bed not found."
    
    print("=== BED STATE TEST ===")
    print(f"Current: {bed.bed_state}")
    print(f"Soil: {bed.soil()}")
    print(f"Now: {bed.bed_state}")
    print(f"Clean: {bed.clean()}")
    print(f"Now: {bed.bed_state}")
    print(f"Rip: {bed.rip()}")
    print(f"Now: {bed.bed_state}")
    print(f"Clean fully: {bed.clean_fully()}")
    print(f"Now: {bed.bed_state}")
    
    return bed


def test_tapestry():
    """Test tapestry toggle."""
    room = get_room()
    if not room:
        return "Room not found."
    
    taps = room.get_tapestries()
    if not taps:
        return "No tapestries found."
    
    print("=== TAPESTRY TEST ===")
    for tap in taps:
        print(f"{tap.key}: is_open={tap.is_open}")
        print(f"  Toggle: {tap.toggle()}")
        print(f"  Now: is_open={tap.is_open}")
        tap.toggle()  # Reset
    
    return taps


def test_trapdoor():
    """Test trapdoor mechanism."""
    room = get_room()
    if not room:
        return "Room not found."
    
    trapdoor = room.get_trapdoor()
    desk = None
    for obj in room.contents:
        if isinstance(obj, HelenaDesk):
            desk = obj
            break
    
    if not trapdoor or not desk:
        return "Missing objects."
    
    print("=== TRAPDOOR TEST ===")
    print(f"Revealed: {trapdoor.is_revealed}")
    print(f"Open drawer 4: {desk.open_drawer(4)}")
    print(f"Use mechanism: {desk.use_mechanism(None)}")
    print(f"Now revealed: {trapdoor.is_revealed}")
    print(f"Use again: {desk.use_mechanism(None)}")
    print(f"Now revealed: {trapdoor.is_revealed}")
    
    return trapdoor


def test_kennel():
    """Test kennel entry."""
    room = get_room()
    if not room:
        return "Room not found."
    
    kennel = room.get_kennel()
    if not kennel:
        return "Kennel not found."
    
    print("=== KENNEL TEST ===")
    print(f"Locked: {kennel.is_locked}")
    print(f"Inside: {kennel.inside_characters}")
    print(f"Curtain: {kennel.curtain_open}")
    print(f"Lock: {kennel.lock()}")
    print(f"Unlock: {kennel.unlock()}")
    print(f"Open curtain: {kennel.open_curtain()}")
    print(f"Close curtain: {kennel.close_curtain()}")
    
    return kennel
