"""
Helena's Cabin Builder - Final Complete Version

Builds Helena's Cabin with:
- Correct descriptions from HELENA_CABIN_DESIGN.md
- ANSI color highlighting for items and furniture
- Smart exit aliases (RoomName (abbrev); w; west; W; WEST; etc.)
- System integrations (restraints, wearables, furniture states, etc.)

Room List:
1. Welcome Room
2. Passageway
3. Helena's Room
4. Nursery
5. Auria's Room
6. The Playroom
7. Disciplination Room
8. Momo's Room
9. Common Room
10. Entertainment Room
11. Bathing Lounge
12. Jacuzzi Room
13. Guest Room
14. Garden of Knowledge
15. Hidden Laboratory
16. Birthing Den
17. Princess' Private Space

Run from Evennia:
    @py from world.build_helena_cabin import build_cabin; build_cabin()

"""

import random
from datetime import datetime
from typing import Optional, List, Dict, Any, Tuple

from evennia import create_object, search_object, DefaultScript
from evennia.typeclasses.attributes import AttributeProperty
from evennia.objects.objects import DefaultExit
from evennia.utils import search

from typeclasses.objects import Object
from typeclasses.rooms import IndoorRoom
from typeclasses.exits import Exit

# Try to import the general systems - graceful fallback if not present
try:
    from world.restraints import RestraintPointsMixin
    HAS_RESTRAINTS = True
except ImportError:
    HAS_RESTRAINTS = False
    class RestraintPointsMixin:
        pass

try:
    from world.furniture_states import StatefulFurnitureMixin
    HAS_FURNITURE_STATES = True
except ImportError:
    HAS_FURNITURE_STATES = False
    class StatefulFurnitureMixin:
        pass

try:
    from world.containers import CompartmentMixin
    HAS_CONTAINERS = True
except ImportError:
    HAS_CONTAINERS = False
    class CompartmentMixin:
        pass

try:
    from world.scents import ScentSourceMixin
    HAS_SCENTS = True
except ImportError:
    HAS_SCENTS = False
    class ScentSourceMixin:
        pass

try:
    from world.environmental import EnvironmentalMixin
    HAS_ENVIRONMENTAL = True
except ImportError:
    HAS_ENVIRONMENTAL = False
    class EnvironmentalMixin:
        pass


# =============================================================================
# CONSTANTS
# =============================================================================

CABIN_TAG = "helena_cabin"

ROOM_KEYS = {
    "welcome": "cabin_welcome",
    "passageway": "cabin_passageway",
    "helena": "cabin_helena_room",
    "nursery": "cabin_nursery",
    "playpen": "cabin_playpen",
    "aurias": "cabin_aurias_room",
    "playroom": "cabin_playroom",
    "disciplination": "cabin_disciplination",
    "momo": "cabin_momo_room",
    "common": "cabin_common_room",
    "entertainment": "cabin_entertainment",
    "bathing": "cabin_bathing_lounge",
    "jacuzzi": "cabin_jacuzzi",
    "guest": "cabin_guest_room",
    "garden": "cabin_garden_knowledge",
    "laboratory": "cabin_laboratory",
    "birthing_den": "cabin_birthing_den",
    "princess_space": "cabin_princess_space",
}


# =============================================================================
# TIME SYSTEM HELPERS
# =============================================================================

def get_time_period() -> str:
    """Get current time period. Hook into actual time system."""
    hour = datetime.now().hour
    if 5 <= hour < 7:
        return "dawn"
    elif 7 <= hour < 12:
        return "morning"
    elif 12 <= hour < 17:
        return "afternoon"
    elif 17 <= hour < 20:
        return "evening"
    elif 20 <= hour < 24:
        return "night"
    else:
        return "latenight"


def get_season() -> str:
    """Get current season."""
    month = datetime.now().month
    if month in (3, 4, 5):
        return "spring"
    elif month in (6, 7, 8):
        return "summer"
    elif month in (9, 10, 11):
        return "autumn"
    else:
        return "winter"


# =============================================================================
# EXIT ALIAS HELPERS
# =============================================================================

def make_exit_aliases(direction: str, extra: List[str] = None) -> List[str]:
    """
    Generate comprehensive exit aliases for a direction.
    
    Args:
        direction: Base direction (e.g., "west", "north", "in")
        extra: Additional aliases specific to this exit
    
    Returns:
        List of all aliases
    """
    aliases = []
    extra = extra or []
    
    # Direction mappings
    dir_map = {
        "north": ["n", "no", "nor"],
        "south": ["s", "so", "sou"],
        "east": ["e", "ea", "eas"],
        "west": ["w", "we", "wes"],
        "northeast": ["ne", "n-e", "north-east"],
        "northwest": ["nw", "n-w", "north-west"],
        "southeast": ["se", "s-e", "south-east"],
        "southwest": ["sw", "s-w", "south-west"],
        "up": ["u"],
        "down": ["d", "dn"],
        "in": ["enter", "inside"],
        "out": ["exit", "outside", "leave"],
    }
    
    base = direction.lower()
    
    # Add base direction and variations
    aliases.append(base)
    aliases.append(base.upper())
    aliases.append(base.capitalize())
    
    # Add abbreviations from map
    if base in dir_map:
        for abbrev in dir_map[base]:
            aliases.append(abbrev)
            aliases.append(abbrev.upper())
    
    # Add any extra aliases
    for ex in extra:
        aliases.append(ex)
        aliases.append(ex.lower())
        aliases.append(ex.upper())
    
    return list(set(aliases))


# =============================================================================
# BASE TYPECLASSES
# =============================================================================

class CabinRoom(IndoorRoom):
    """Base room for Helena's Cabin with time variants and shortcode support."""
    
    room_key = AttributeProperty(default="")
    time_descriptions = AttributeProperty(default={})
    ambient_scents = AttributeProperty(default=[])
    has_hearth = AttributeProperty(default=False)
    
    def at_object_creation(self):
        super().at_object_creation()
        self.tags.add(CABIN_TAG, category="area")
    
    def get_time_period(self) -> str:
        return get_time_period()
    
    def get_time_desc(self) -> str:
        """Get time-appropriate description."""
        period = self.get_time_period()
        return self.time_descriptions.get(period, "")
    
    def process_shortcodes(self, text: str, looker=None) -> str:
        """Process description shortcodes."""
        if not text:
            return ""
        
        # Time description
        time_desc = self.get_time_desc()
        text = text.replace("<time.desc>", time_desc)
        
        # Ambient scents
        scents = self.ambient_scents
        if isinstance(scents, list):
            scents = ", ".join(scents) if scents else ""
        text = text.replace("<ambient.scent>", scents or "")
        text = text.replace("<ambient.scents>", scents or "")
        
        return text
    
    def return_appearance(self, looker, **kwargs):
        """Return room description with shortcodes processed."""
        appearance = super().return_appearance(looker, **kwargs)
        return self.process_shortcodes(appearance, looker)


class CabinObject(Object):
    """Base object for cabin items."""
    
    portable = AttributeProperty(default=True)
    weight = AttributeProperty(default="light")
    
    def at_object_creation(self):
        super().at_object_creation()
        self.tags.add(CABIN_TAG, category="area")


class CabinFurniture(StatefulFurnitureMixin, RestraintPointsMixin, CabinObject):
    """Base furniture with state tracking and restraint points."""
    
    portable = AttributeProperty(default=False)
    weight = AttributeProperty(default="immovable")
    capacity = AttributeProperty(default=1)
    supported_positions = AttributeProperty(default=["sitting", "lying", "standing"])
    
    def at_object_creation(self):
        super().at_object_creation()
        self.locks.add("get:false()")


class CabinContainer(CompartmentMixin, CabinObject):
    """Base container with compartments."""
    
    portable = AttributeProperty(default=False)
    is_open = AttributeProperty(default=False)
    is_locked = AttributeProperty(default=False)
    
    def at_object_creation(self):
        super().at_object_creation()
        self.locks.add("get:false()")


class CabinExit(Exit):
    """Base exit with smart aliases."""
    
    def at_object_creation(self):
        super().at_object_creation()
        self.tags.add(CABIN_TAG, category="area")


# =============================================================================
# ROOM DESCRIPTIONS - Correct from HELENA_CABIN_DESIGN.md
# =============================================================================

ROOM_DESCS = {
    # =========================================================================
    # WELCOME ROOM
    # =========================================================================
    "welcome": """The welcome room of the log cabin is a cozy and intimate space, to transition from the harsh stress and discomforts of the outside world into the relaxation and warmth of home.

To the left of the door, a |crustic bench|n with cubby holes built into its base sits in waiting for the family to sit and remove shoes or unneeded clothes. A large |cornate mirror|n with a decorative golden border rests securely on the wall above it so people can check their appearance before leaving. Opposite of the bench, a series of |ccoat hooks|n are fastened at shoulder height to the wall. An assortment of furs, colored windbreakers, sweaters and scarves are hung with care as well as a few sturdy leashes, muzzles, harnesses, and mittens with paw prints.

The room is lit by electric lights fashioned to resemble |cantique lanterns|n hanging on chains from the ceiling. There is a step up, from the wooden floor of the welcome room's entryway to a passageway leading |cdeeper into the cabin|n.

<wolf_prints.desc> A |csign|n hangs above the door stating |y'A Den is not a Home without a Big Bad Wolf'|n.

<time.desc>""",

    # =========================================================================
    # PASSAGEWAY
    # =========================================================================
    "passageway": """A long and wide hallway stretches from the Welcome Room to the arched and open entryway to the north, marked with a simple sign that reads 'Common Room'.

The hallway has dark wooden flooring that has been well taken care of. A rectangular |carea rug|n peppered with softer tones of gray and white is laid towards the center, with an |centry table|n between the two doors on the east wall. Sitting atop the table are three small |cwolf figurines|n made with care and attention to detail, giving them a life-like appearance, the center one being well endowed. A decorative |cpotpourri bowl|n <potpourri.scent> also adorns the table top<shadow_musk.desc>.

Mounted to the wall above the table is another piece of fanciful wolf iconography. A |cportrait|n of a large black direwolf defined with powerful muscle, a striking expression with fangs bared and surrounded by several silk-clad women clinging to its sides—some notably familiar and well bred. The portrait is simply titled "Shadow's Harem" although the date is hard to make out.

Two doors line each side wall, each adorned with a unique |cplaque|n. On the western wall, a heavy door reinforced with thick strips of iron and dark bolts leads to Helena's room—with deep |cscratches|n gouged into the flooring trailing towards it. Just down from the heavy door, a much lighter door in gentle shades of pink with the silhouettes of various faeries and stars marks Auria's room. On the eastern wall on one side of the entry table, a door of rich mahogany with delicate vine carvings leads to the Garden of Knowledge. At the other end of the table, nearest to the open archway, a door painted in pale yellow and decorated in floral decals of various pinks and violets opens to the Guest Room.""",

    # =========================================================================
    # HELENA'S ROOM
    # =========================================================================
    "helena": """Behind the heavy iron reinforced door on the western side of the Passageway is the room belonging to the cabin's resident Elven Domme and Alpha.

This chamber, unlike the rest of the cabin's rustic charms, is a mix of elegance and sexual deviance. The wooden floors have been deeply gouged by sharp |cclaws|n near the door and around the edges of the furniture in the room.

A huge |ccanopied bed|n supporting a thick king sized mattress is centered opposite of the door. <bed.state> A wide assortment of fluffed soft |cpillows|n are distributed evenly on the bed, though some have been chewed and torn with stuffing poking free of their casing. The canopied bed as a whole is supported by a large |ckennel|n comprised of vertical bars, its cell door at the foot of the bed.

A few steps to the left of the bed, a metal |cdesk|n resides with a large assortment of |ctoys|n atop it; sexual objects and devices ranging from dildos, vibrators, whips and feathers to large strap-ons and a black and purple cat 'o nine tails. Four drawers in the desk hint that there may be secrets hidden only known to their owner.<trapdoor.state>

Elaborate |ctapestries|n hang on three walls. The |cnorthern tapestry|n bears H.S. in stylized gothic letters surrounded by wolf paw prints and chain motifs<tapestry_north.state>. The |csouthern tapestry|n is torn worse than the others—large fangs have shredded the fabric in places<tapestry_south.state>. The |ceastern tapestry|n is newer than its siblings but already shows Shadow's marks<tapestry_east.state>. All bear Helena's insignia.

Two |ccollars on chains|n are bolted to the northern wall and are perfectly aligned with four sets of |cshackles|n that are bolted to the floor. The shackles are about a meter apart from each other and half a meter from the wall. Next to the chains is a large circular |cpet bed|n, purple in color. The pet bed is large enough for two to curl up easy. Three could fit with a little squishyness.

<time.desc>""",

    # =========================================================================
    # NURSERY
    # =========================================================================
    "nursery": """<time.desc>

Bright and cheerful |yyellow wallpaper|n covers the walls, patterned with an assortment of cute animals—fluffy bunnies, pretty songbirds, frolicking wolves. The entirety of the floor is squishy |cfoam|n, ensuring any falls are harmless. A portion in the center displays the ABCs in bright colors.

A large |cwindow|n set into the wall gives a view onto the snow-covered forest, the serene landscape disturbed only by wolf tracks through the snow. A comfortable |cwindow seat|n laden with cushions provides a place to sit and watch.

Off to one side rests a large |ccrib|n, more than large enough for an adult, nestled with warm blankets and stuffed animals. Opposite stands a |cchanging table|n, fully stocked with supplies including thick, crinkly |cdiapers|n.

Colourful |cshelves|n mounted on the walls hold toys. In one corner, a large |cdollhouse|n surrounded by dozens of dolls waits to be played with. A |cchest of drawers|n and |cwardrobe|n hold clothes for dress-up.

A |cgliding nursing chair|n and |cfootstool|n sit near the window, ready for feeding time. Scattered near the changing table are colourful |cblocks|n and a |cteddy bear|n.

Hung proudly on one wall is a piece of |ccolouring|n—a small pond surrounded by trees in greens and purples.

A wicker archway leads into |cThe Play Pen of Adventure|n, its interior shimmering faintly...

Through a |ckiddie gate|n to the south, |cAuria's Room|n is visible—pink walls, fae warmth, wildflower scent drifting through.

The |ctapestry|n north leads back to |cHelena's Room|n.""",

    # =========================================================================
    # THE PLAY PEN OF ADVENTURE (Magical Sub-Area)
    # =========================================================================
    "playpen": """You stand among MASSIVE toys that tower over you—because you've been shrunk to figurine size.

The Play Pen has become an endless landscape of foam biomes. |gForests|n of plastic trees where tigers and elves lurk. |cMountains|n of foam blocks where yetis and snow dragons dwell. |yDeserts|n of tan fabric where sand creatures wait in oasis pools.

Looking back at the wicker entrance reveals the nursery—|rGARGANTUAN|n. The ceiling is impossibly far away. You haven't grown the toys. The magic has shrunk |wYOU|n.

Every figurine has anatomy. Cocks, pussies, or both. Breasts are prevalent. And they've |rnoticed you|n.

The figurines are pairing off, grouping up, engaging in debauchery. Some are looking at you with intent. An |corc figurine|n is already approaching, grunting, reaching for you...

The |cwicker arch|n looms enormous above—your exit back to normal size.""",

    # =========================================================================
    # AURIA'S ROOM
    # =========================================================================
    "aurias": """<time.desc>

Stepping in from the main room you are confronted by a plush |ccarpet|n underfoot, bright pink in colour. Scattered across the floor are |ccushions|n and |cpillows|n of all colours, some gathered into a small |cnest|n against the southern wall. From the wall above the nest hangs a set of |cchains|n, long enough for someone to curl up comfortably in the nest and ending in padded |cshackles|n, and a |ccollar|n inscribed with "|yAuria|n".

A comfy |cbed|n stands opposite the door, made up neatly with a pale purple bedspread. Perched in the center of the bed is a fluffy |cEevee|n plushie, with a jumbled pile around her; a plush dragon in shades of purple, a Squirtle and Chikorita small enough to fit in a coat pocket and a happy looking raccoon.

Standing beside the nest of pillows is a large |cbookcase|n packed with books, a few of the titles standing out; "The Lion, the Witch and the Wardrobe", "The Painted Man", "The Black Prism", "The Way of Kings". Beside the bookcase is pinned a note; "|wFeel free to add something! Just let me know which is yours!|n"

Against the northern wall rests a closed |ctrunk|n, and a small |cwardrobe|n stands against the southern wall. On a small table by the bed, a leather-bound |cjournal|n lies open, pen beside it.

A |cbeaded curtain|n of crystal and colored glass separates the room from a darker space to the west—|cThe Playroom|n.""",

    # =========================================================================
    # THE PLAYROOM (Auria's)
    # =========================================================================
    "playroom": """<time.desc>

Stepping into this room is a marked change from the previous—the lighting dim, the floor underfoot dark polished wood. Dark purple |cpadded walls|n surround you, one section taken up by a large |cmirror|n. Attached to one wall via fine chain is a smooth |ctitanium collar|n with "|bAuria|n" in gently pulsing blue letters, with matched |cshackles|n for wrists and ankles.

A |cpommel horse|n sits off to one side, padded cuffs attached to the handles and a twin dildo attached to the center, positioned perfectly to fill both holes at once. A series of hooks on the wall nearby hold the |cpaddle rack|n—a number of paddles and a single cane. From the ceiling hangs a |csuspension bar|n of titanium, shackles dangling beneath. Opposite hangs a black |csex swing|n, straps and buckles ready.

Against one wall is a |ccloset|n, while a |cspreader bar|n is propped beside it. A |ctoy table|n holds a selection of toys, and nearby rests a |crocking horse|n with dildos attached to the saddle and padded cuffs on the handles.

The center of the room has steps leading down onto a small round |cstage|n surrounded by plush leather |ccouches|n, and center-stage is a silvery steel |cpole|n extending from floor to ceiling.

The |cbeaded curtain|n leads back east to Auria's Room.""",

    # =========================================================================
    # DISCIPLINATION ROOM
    # =========================================================================
    "disciplination": """<lighting.desc>

Upon stepping into this room, one thing is immediately clear: this room serves a unique purpose, and that purpose is discipline.

Oaken |cfloors|n greet you, highly polished almost to the point you could slide upon them. A |cdrain|n is set into the floor near the center.

A |cBDSM bench|n stands in the center of the room, equipped with maneuverable cuff limbs at head and foot. Against one wall, a |cshelf|n holds a variety of toys. Against the opposite wall, a |crack|n displays implements of punishment.

The far wall displays a collection of erotic |cpaintings|n.

A large |cmirror|n dominates one section of wall. Before it, |cfloor shackles|n are mounted on short chains. From the ceiling swings a |ccollar|n on a length of chain, controllable by a |clever|n on the wall.

In one corner, a locked |coak chest|n sits heavy and mysterious. In the other, a |cspreader bar|n. A large circular |cpet bed|n rests near the floor shackles.""",

    # =========================================================================
    # MOMO'S ROOM
    # =========================================================================
    "momo": """<time.desc>

The warm, woody smell of clean straw fills the room, joined by the scent of honeysuckle brought in by a light breeze. The southern wall is only waist-high, otherwise open to a rolling |cmeadow|n with a little brook and tree visible off in the distance. The other three walls are yellow |cstucco|n over wooden paneling, continuing a fence motif.

A comfortable yellow |cfuton|n lies against the northern wall, piled high with pillows. Above it, Momo's |ccollar|n hangs on its leash—a dark collar with silver studs and a golden bell, chained to the wall.

A |cfeeding trough|n rests against the wall near the bed, with a nearby |cfaucet|n and |chose|n with adjustable showerhead.

In the center of the room, a solid structure of oak and steel frames an adjustable |cpillory|n. A |cmilking machine|n sits in an open cabinet at its base. Nearby stands an adjustable |cbreeding bench|n, and a curious |cfeather pedestal|n.

Leather |ctack|n hangs on the eastern wall—harnesses, bridles, a crop, rope.

The stable door leads back |cwest|n to Helena's Room through the tapestry.""",

    # =========================================================================
    # COMMON ROOM
    # =========================================================================
    "common": """The Common Room is a large, sprawling space dedicated to many facets of everyday life within the cabin.

<kitchen.desc>

<dining.desc>

<hearth.desc>

A door to the |ceast|n leads to the Entertainment Room. To the |cnorthwest|n, the Bathing Lounge. |cWest|n leads to the Jacuzzi Room. The open archway |csouth|n returns to the Passageway.

<time.desc>""",

    # =========================================================================
    # GUEST ROOM
    # =========================================================================
    "guest": """This is a guest room, soft and welcoming.

The walls are covered with striped |cwallpaper|n—pale yellow and white stripes printed with roses and ivy at intermittent points. Light wooden flooring extends from white mop boards, covered by a plush white |carea rug|n at the center. A barely-visible |cdrain|n is set into the floor near the bed—easy to miss if you're not looking.

A |cround bed|n fills the back right corner, its mattress thick and impossibly soft. Fluffy pillows and a few decorative |cstuffed animals|n top it, the bedding crisp and fresh. The furniture set—|cdresser|n, |cbedside table|n, |cvanity|n with large round mirror, and |cwardrobe|n—is colored in white that seems to glow softly with a pink hue.

The wardrobe stands with double doors open, stocked with guest amenities and a selection of outfits. The vanity holds basic toiletries and makeup. A wide |crocking chair|n with soft cushions and a fleece blanket faces the door, large enough for two.

Above the door, a decorative wooden |cplaque|n states: 'Welcome, we care about you.'

<time.desc>""",

    # =========================================================================
    # GARDEN OF KNOWLEDGE
    # =========================================================================
    "garden": """Here lies a veritable garden of inexplicable and fantastical tomes of knowledge, fantasy, and entertainment.

A large, brightly colored room of deep purples and oranges, lush pinks and violets sprawls on for a seemingly endless eternity to mimic the fading light of a glorious sunset. The fantastical palette only broken up by tall and sturdy |cbook shelves|n formed by living woods rooted into a rich floor of dark and loamy earth, the greens and vibrant yellows, whites, and baby blues of |cvine and flowers|n adorning the space.

Careful and painstaking attention to the cultivation and growth forms this mythical grove, the loving and dedicated touch of the resident and proudly owned fae affectionately nicknamed 'Oreo' by her Mistress.

The living shelves hold many old and modern tomes: Magical grimoires, books of science and history, fact and fiction, tales of elegance, novels of debauchery, fairy tales and hentai.

One such section is completely dedicated to |cMy Little Pony hentai|n for unknown reasons.

At the room's center, like the court surrounding a prized water feature in a garden, roots twist and weave to form a sturdy |cdesk|n for the attending fae to work, and read in peace— <desk.state>. A plush |cbeanbag chair|n of bright pink sits behind it, the surrounding earth littered with |cstuffed animals|n and |ccoloring books|n.

<time.desc>""",

    # =========================================================================
    # ENTERTAINMENT ROOM
    # =========================================================================
    "entertainment": """<time.desc>

A sprawling entertainment space designed for relaxation and indulgence. The walls are painted a deep, cozy burgundy, with soft recessed lighting that can shift from bright to intimate.

A massive |cTV screen|n dominates one wall, flanked by tall speakers. Below it, a |cmedia console|n holds gaming systems, a Blu-ray player, and a sound system. Comfortable |ccouches|n and |cbeanbag chairs|n are arranged for optimal viewing—or for other activities while something plays in the background.

A |cpool table|n stands in one corner, its felt a deep purple. Nearby, a |cdart board|n and a |ccard table|n with chips offer other diversions.

The pride of the room is the |cdairy fridge|n—a glass-front refrigerator stocked with labeled bottles. "Laynie's Cream." "Momo's Fresh." "Auria's Sweet." Each bottle dated, each source noted. The milk is real. The sources are family.

A |csnack bar|n with stools offers drinks and treats. The |cmini bar|n beneath is well-stocked.

The doorway |cwest|n leads back to the Common Room.""",

    # =========================================================================
    # BATHING LOUNGE
    # =========================================================================
    "bathing": """<time.desc>

Almost in direct contrast to the plainness of the simple wooden door, this space is luxurious and spacious for relaxation, cleansing, and relief.

Creamy, macchiato colored |ctiles|n streaked with black and gold flecks cover the walls and floor. |cHooks and rings|n are mounted among paintings of flora and fauna. |cCandles|n of various colors flicker in the corners, filling the air with lavender.

Open |cshelves|n hold fluffy towels and toiletries. Two |ccabinets|n—one for hygiene supplies, one for... other supplies.

A crystalline |cwash basin|n with a rounded mirror decorated with wolf prints. In an alcove, a white porcelain |csquat toilet|n is set into the floor—no privacy, open to the room.

Centered in the back wall, thick clear glass panels frame the |cCursed Shower|n. The glass seems to fog and clear rhythmically. Breathing.

A |cbath mat|n before the shower bears embroidered text: "|rMagic showers, last for hours.|n"

The doorway |csoutheast|n leads back to the Common Room.""",

    # =========================================================================
    # JACUZZI ROOM
    # =========================================================================
    "jacuzzi": """<time.desc>

The room is spacious, featuring many tasteful art pieces, a large |cwindow|n with a scenic view, and a steaming, bubbling |cjacuzzi|n shaped like a wolf print.

In the corners of the room, black |cpedestals|n of welded chains support lush potted ivies and sensuous candles that permeate the room with the scent of relaxation.

The bottom of the walls features a highly detailed |cmural|n made of various colored tiles and bits of glass—a tale of a wolf hunting its prey, filled with carnal lust. Five panels tell the story from hunt to pack.

On the walls, several steel |ccables|n are affixed with collars and shackles that dangle against the tile, able to extend several feet or be locked at any length.

The wolf-paw jacuzzi has four |ctoe seats|n surrounding a central |cthrone|n position. The bubbles obscure what waits beneath the water in each seat. A |ccontrol panel|n is built into the rim at the throne position.

The doorway |ceast|n leads back to the Common Room.""",

    # =========================================================================
    # HIDDEN LABORATORY
    # =========================================================================
    "laboratory": """<time.desc>

A hidden workspace tucked beneath Helena's Room, accessible only through the trapdoor in her kennel. The air hums with contained magic and smells of herbs, ozone, and something sweet.

|cAlchemical equipment|n lines one wall—beakers, tubes, burners, a |cdistillation apparatus|n bubbling with something violet. Shelves hold labeled |cingredients|n: "Moonpetal," "Wyrm Scale," "Essence of Want," "Condensed Blush."

A |cworkbench|n dominates the center, covered in half-finished projects. A |cjournal|n lies open, filled with cramped handwriting and diagrams. Oreo's research notes.

Against another wall, a |cmagitech station|n glows with runes and crystals—where magic meets machinery. A partially assembled |ccollar prototype|n sits in a vice, enchantment half-woven.

A |cstorage cabinet|n holds finished products: potions, enchanted items, toys with... unusual properties. Everything is labeled in Oreo's meticulous script.

The |cladder|n leads back |cup|n to Helena's kennel.""",

    # =========================================================================
    # BIRTHING DEN
    # =========================================================================
    "birthing_den": """<time.desc>

A cavernous stone chamber opens into a grand expanse, its walls and floors worn smooth by uncounted centuries. Dim light emanates from unseen |cglobes|n of magic. The jagged ceiling bares pointed earthen fangs.

Across the walls, vague scenes are depicted in primitive |cpaints|n—great feral wolves stalk, hunt, and capture prey. One particular sequence demands attention: the story of how Shadow claimed Helena.

Ashen wolf |cprints|n adorn the walls—sacred marks of pack membership. Shadow's print is largest, with Helena's handprint pressed within it.

Half the space is occupied by a hidden oasis—warm |csprings|n forming a series of comfortable pools, flowing lazily through the cavern. The clear water shimmers with aquamarine and magical essence.

A thin layer of padding makes a surprisingly comfortable |cnest|n for new mothers and their broods—rendered hide, fur, and... torn clothing from those who ignored the sign at the forest edge.

The passage leads |cup|n to Helena's Kennel. A beaded curtain leads |csouth|n to Princess' Private Space.""",

    # =========================================================================
    # PRINCESS' PRIVATE SPACE
    # =========================================================================
    "princess_space": """<time.desc>

In stark contrast to the rest of the den with its time-worn stone, this space is largely civilized—like a princess' bedroom might be. The walls are smooth with a pink hue.

The northern wall features an elaborate |cmural|n—the scene painted with care and intent. It depicts a young blonde girl in a pillory being milked, watched by Helena, Shadow, and a hovering fae. This is documentation, not fantasy.

Cute |cdoodles|n of cows, wolves, faeries, and naked women are sprinkled among coloring pages taped to the walls. A poster |cwindow|n gives the illusion of peering out onto a lush pasture with grazing cattle.

A low, king-sized |cbed|n with pink covers and tiaras on the headboard. Metal railing runs along the sides with dangling |ccuffs|n—always present, always ready.

Near the center, an antique wooden |cpillory|n with dark cherry finish stands beside a large |cmilking machine|n. A |ctoy chest|n sits near the doorway.

The door offers no real privacy—a |cbeaded curtain|n of pink and white through which hungry wolves might enter. It leads |cnorth|n to the Birthing Den.""",

}


# =============================================================================
# TIME VARIANT DESCRIPTIONS
# =============================================================================

TIME_DESCS = {
    "welcome": {
        "dawn": "Gray morning light seeps in around the door. The lanterns are dim, waiting.",
        "morning": "The lanterns glow warmly. Dust motes drift in the light from outside.",
        "afternoon": "Warm and quiet. The scent of the cabin fills the space.",
        "evening": "The lanterns flicker brighter as outside darkens. Coming home.",
        "night": "The lanterns are the only light. The cabin waits, warm and dark.",
        "latenight": "Deep quiet. The lanterns are low. Even the wolves are sleeping.",
    },
    "passageway": {
        "dawn": "The hallway is dim, the first light barely reaching through from adjacent rooms.",
        "morning": "Morning light fills the passageway, making the wood floors gleam.",
        "afternoon": "Warm and quiet. Dust motes drift in the still air.",
        "evening": "The passageway grows intimate as evening settles in.",
        "night": "The hallway is dark save for what light spills from doorways.",
        "latenight": "Deep stillness. The cabin sleeps around you.",
    },
    "helena": {
        "morning": "Light filters through gaps in the tapestries. The red silk gleams. The room smells of Helena's perfume and something earthier—Shadow was here.",
        "afternoon": "Quiet dominion. The desk's toys catch the light. Someone might be in the kennel below, waiting.",
        "evening": "Candles flicker in their sconces. The tapestries seem to breathe. The room becomes intimate, dangerous.",
        "night": "Helena's domain fully realized. The bed awaits. The kennel waits. The shackles wait. Everything waits for her.",
    },
    "nursery": {
        "dawn": "Pale morning light filters through the window, catching dust motes that drift lazily through the air. The wolf tracks outside are fresh. A good time to wake up, be changed, have breakfast.",
        "morning": "Bright sunlight fills the nursery with cheerful warmth. The yellow wallpaper seems to glow. The toys wait eagerly on their shelves.",
        "afternoon": "Playtime lighting fills the room. The toys seem to wait eagerly. The Play Pen's wicker arch glimmers faintly, invitingly.",
        "evening": "Softer golden light filters through. The crib looks inviting for naptime. The nursing chair glows warmly, ready for feeding time.",
        "night": "A soft nightlight casts gentle shadows across the room. The crib is cozy, blankets ready. The forest outside is silver and shadow. Time for sleep, little one.",
        "latenight": "The nightlight hums softly. Everything is still, peaceful, safe. The stuffed animals in the crib keep watch through the darkness.",
    },
    "aurias": {
        "dawn": "Pale light filters through curtains she picked herself, pink and gauzy. The room stirs—not physically, but as if waking. The Eevee on the bed catches the first light, and for a moment its glass eyes almost seem to blink.",
        "morning": "Sunlight fills the room with warmth, catching dust motes that dance like tiny faeries. The pink walls glow softly. Everything here has been dusted recently, cared for, kept ready.",
        "afternoon": "The room is bright and cheerful despite the empty bed. A breeze from nowhere ruffles the pages of a book left open on the nightstand. The stuffies seem comfortable, content.",
        "evening": "Soft shadows make the pink feel warmer, cozier. The room settles into comfortable quiet—like a hug waiting to happen. The Eevee seems to watch the door.",
        "night": "The darkness here is gentle. A soft glow comes from somewhere—perhaps the collar's inscription, perhaps something else. The room takes care of itself and is taken care of.",
        "latenight": "Peaceful stillness. The room rests, but lightly. Ready to wake if she comes home. The pillow nest looks particularly inviting in the dim light.",
    },
    "playroom": {
        "day": "Candles unlit. The room waits in comfortable dimness, equipment casting soft shadows against the padded walls.",
        "morning": "Candles unlit. The room waits in comfortable dimness, equipment casting soft shadows against the padded walls.",
        "afternoon": "Candles unlit. The room waits in comfortable dimness, equipment casting soft shadows against the padded walls.",
        "evening": "Candles flicker to life as evening falls. The metal catches the light—pole, chains, titanium collar pulsing its soft blue.",
        "night": "Intimate darkness. The collar's glow is more pronounced now, \"Auria\" written in light. The padded walls absorb all sound.",
        "latenight": "The deepest quiet. Even the collar dims. The room holds its breath, waiting for whoever might need it.",
    },
    "disciplination": {
        "morning": "Bright, clinical light. Every detail visible. No shadows to hide shame or tears.",
        "afternoon": "Bright, clinical light. Every detail visible. No shadows to hide shame or tears.",
        "evening": "The lights remain steady and bright. This room doesn't soften with evening.",
        "night": "Bright, clinical light. Every detail visible. No shadows to hide shame or tears.",
    },
    "guest": {
        "morning": "Soft light filters through, the white and yellow feeling bright and fresh. The vanilla-linen scent is crisp. A good place to wake slowly.",
        "afternoon": "Warm and quiet. The pink-hued furniture seems to glow in the gentle light. Comfortable for a nap.",
        "evening": "Golden light makes everything softer. The rocking chair invites you to sit, wrapped in the fleece blanket.",
        "night": "Soft lamplight. The round bed beckons, promising to swallow you in comfort. The room feels safe. Private.",
    },
    "garden": {
        "dawn": "The sunset glows with early warmth—pinks and soft oranges, as if the sun is just beginning its descent. Fresh dew glistens on leaves and flowers.",
        "morning": "Golden hour light, the sunset frozen at its most brilliant. The living shelves seem to stretch toward the warm glow. Peaceful reading light.",
        "afternoon": "Deep amber and rose, the sunset at its richest. Shadows are soft and warm. The earth smells fertile. Perfect for napping in the beanbag.",
        "evening": "Purples deepen, the sunset shifting toward twilight. The flowers close slightly. Intimate, cozy, magical.",
        "night": "The sunset holds at its final moment—deep violets and magentas, stars beginning to appear in the \"sky.\" Bioluminescent hints in the flowers. Enchanted.",
    },
    "momo": {
        "dawn": "Pale light touches the meadow beyond. The brook glints silver. The straw smells fresh, the honeysuckle just waking.",
        "morning": "Warm sunlight fills the stall through the open southern wall. The meadow is bright and inviting. The bell on Momo's collar would catch the light, if she were here.",
        "afternoon": "Lazy warmth. The meadow hums with distant insects. A good time for a nap on the futon, or... other activities on the bench.",
        "evening": "Golden light paints the meadow amber. The tree in the distance casts long shadows. The equipment waits, patient.",
        "night": "The meadow is silver under starlight. The stall is dim and cozy. The collar glints faintly in the darkness.",
        "latenight": "Deep quiet. Even the magical meadow sleeps. The straw rustles softly. The collar waits.",
    },
    "entertainment": {
        "morning": "Bright and quiet. The TV is dark, the room waiting for activity. Good light for pool.",
        "afternoon": "Perfect gaming light—not too bright on the screen. The dairy fridge hums softly.",
        "evening": "The recessed lighting shifts warmer. Movie time lighting. The couches look inviting.",
        "night": "Intimate darkness broken by screen glow. The bottles in the dairy fridge catch what light there is. Cozy.",
        "latenight": "Late night gaming or movie marathon lighting. The room doesn't judge what hour it is.",
    },
    "bathing": {
        "morning": "Bright, clean light. The tiles gleam. The Cursed Shower's glass is clear—dormant.",
        "afternoon": "Steam-softened light. The candles are unnecessary but pleasant. The shower glass fogs and clears rhythmically.",
        "evening": "Candles provide most of the light. The tiles glow warm. The shower glass pulses slowly.",
        "night": "Intimate candlelight. The hygiene cabinet's contents are harder to distinguish. The shower glass seems to breathe more noticeably.",
        "latenight": "A single candle. The shower glass is fogged—dreaming, perhaps. Even mimics sleep.",
    },
    "jacuzzi": {
        "evening": "The aurora begins to appear through the window—faint ribbons of green and pink. The jacuzzi bubbles invitingly. The mural's colors glow in the candlelight.",
        "night": "Full aurora display through the window. The jacuzzi steam catches the colored light. Magical and intimate.",
        "latenight": "The aurora pulses slowly. The jacuzzi's bubbles are the only sound. Through the window, occasionally, wolves pass.",
        "morning": "Daylight through the window shows rolling purple mountains. The aurora is invisible but the view is spectacular.",
        "afternoon": "Bright mountain view. The mural is fully visible in detail. The jacuzzi steams invitingly.",
    },
    "laboratory": {
        "morning": "The magical lights are steady and bright. Good light for delicate work. The alchemical equipment bubbles softly.",
        "afternoon": "Warm, focused light. Oreo's workspace feels productive. The magitech station hums.",
        "evening": "The lights shift warmer. The violet distillation glows more prominently. Creative energy.",
        "night": "Dim, intimate lighting. The crystals at the magitech station provide most of the glow. Secret work hours.",
        "latenight": "Near darkness save for glowing experiments and runes. The laboratory never fully sleeps.",
    },
    "birthing_den": {
        "dawn": "The magical globes brighten slowly. The warm springs steam in the cool air. The paintings seem to tell their story fresh.",
        "morning": "Soft, diffuse light from the globes. The springs are warm and inviting. A peaceful time in the sacred space.",
        "afternoon": "The den drowses. The springs bubble lazily. The pack prints seem to glow faintly.",
        "evening": "The globes dim to intimate levels. The springs reflect dancing light. The nest looks inviting.",
        "night": "Near darkness. The springs glow faintly with their own magic. The paintings are shadows telling shadow stories.",
        "latenight": "The deepest quiet. The globes are nearly dark. Only the springs' magic provides light. Sacred silence.",
    },
    "princess_space": {
        "morning": "Soft light makes the pink walls glow. The fake window shows a sunny pasture. Princess waking hours.",
        "afternoon": "Warm and cozy. The cuffs on the bed catch the light. Nap time, or... other activities.",
        "evening": "The pink deepens to rose. The mural is prominent. The fake window shows sunset over the pasture.",
        "night": "Soft, intimate pink. The cuffs gleam. The beaded curtain offers no privacy from the sounds beyond.",
        "latenight": "Deep quiet in the princess room. But through the curtain, sometimes, wolf sounds...",
    },
}


# =============================================================================
# OBJECT DESCRIPTIONS
# =============================================================================

OBJECT_DESCS = {
    # WELCOME ROOM
    "rustic_bench": "A rustic bench to the left of the door, worn smooth from use. Cubby holes built into its base hold shoes, slippers, and the occasional forgotten item. This is where you sit to remove the outside world before going deeper.",
    "rustic_bench_examined": "Cubby holes built into its base hold shoes, slippers, and the occasional forgotten item. This is where you sit to remove the outside world before going deeper.",
    "ornate_mirror": "A large mirror with a decorative golden border, secured to the wall above the bench. The frame is ornate but not gaudy—elegant, like something from an old estate.",
    "ornate_mirror_frame": "It shows you as you are, one last check before facing the world or one first look at yourself coming home.",
    "coat_hooks": "A series of sturdy hooks fastened at shoulder height to the wall. An assortment of outdoor wear hangs with care.",
    "coat_hooks_detailed": "The leashes are high quality, meant for larger animals—or people. The muzzles are padded for comfort during extended wear. The harnesses have multiple attachment points. Everything is maintained, used, loved.",
    "antique_lanterns": "Electric lights fashioned to resemble antique lanterns hang on chains from the ceiling. They give off warm, flickering light—not real flame, but close enough to feel like it. Someone went to effort to make modern convenience feel like old comfort.",
    "wooden_sign": "A Den is not a Home without a Big Bad Wolf",
    "wooden_sign_hidden": "Below the main text, in smaller carved letters: \"All who enter with love are welcome. All who enter with ill intent will meet Her.\" The 'Her' has claw marks through it—playful or warning, hard to tell.",
    
    # PASSAGEWAY
    "area_rug": "A rectangular area rug in soft gray and white tones.",
    "area_rug_examined": "A plush rectangular rug laid towards the center of the hallway. Soft tones of gray and white form a subtle pattern. It's well-worn in the middle where feet pass most often, but still comfortable underfoot.",
    "entry_table": "A wooden entry table between the two doors on the east wall.",
    "entry_table_examined": "Solid and well-made, the table holds the wolf figurines and potpourri bowl. The wood is dark, matching the flooring, polished but showing its age in small scratches and wear marks. Positioned between the Garden door and the Guest Room door.",
    "wolf_figurines": "Three small wolf figurines made with care and attention to detail.",
    "wolf_figurines_examined": """Three wolves carved with remarkable skill, each painted with lifelike detail:

The largest is jet black with powerful haunches and a knowing expression. Well endowed. Shadow.

The second is light brown with a cream underbelly, smaller and alert. Also endowed, though modestly. Whisper.

The third is pure white, elegant and poised with quiet grace. Blaze.

Each is polished smooth from handling. Someone touches these often.""",
    "portrait_base": """A large oil painting in an ornate frame. The painting depicts a massive black direwolf, muscles rippling beneath dark fur, fangs bared in what might be a snarl or a grin. Her impressive endowment is rendered without shame.

Arrayed around her are beautiful women in flowing silk, clinging to her sides in various states of devotion. Some kneel. Some recline against her flank. Each face is rendered with remarkable detail—real people, not imagined.

The portrait is titled "Shadow's Harem" in elegant script. A date is partially visible but hard to make out.""",
    "portrait_stranger": "\n\nThe women are beautiful, devoted. You don't recognize any of them specifically, but something about the painting makes you feel... considered.",
    "portrait_laynie": "\n\nThere you are, nestled against Shadow's flank. The silk barely covers you. Your expression is... accurate. Whoever painted this has seen you like this.",
    "portrait_auria": "\n\nYou recognize yourself among the women, painted with care and obvious affection. The artist captured your essence—the way you look at Her.",
    "portrait_claimed": "\n\nOne of the women looks remarkably like you. The resemblance is uncanny—the artist must have known you would stand here someday.",
    "scratches": "Deep scratches gouged into the wooden flooring.",
    "scratches_examined": "Deep gouges in the wood, trailing toward Helena's door on the western wall. Claw marks from something large and eager, worn into the floor over time. The pattern speaks of urgency—something scrambling toward that door, again and again, unable or unwilling to wait.",
    "potpourri_spring": "A decorative bowl filled with dried flowers and herbs. Fresh green herbs and early wildflowers dominate the mix. A hint of rain-washed earth lingers underneath.",
    "potpourri_summer": "A decorative bowl filled with dried flowers and herbs. Wild flowers and fresh mint dominate, bright and clean. A touch of lavender rests underneath.",
    "potpourri_autumn": "A decorative bowl filled with dried flowers and herbs. Dried apples and cinnamon, warm spices against the coming cold. A whisper of woodsmoke clings to everything.",
    "potpourri_winter": "A decorative bowl filled with dried flowers and herbs. Pine and cedar, sharp and clean. Dried cranberries add a hint of tartness. The scent of shelter.",
    # Plaques
    "helena_plaque": "A heavy iron-reinforced door plaque on the western wall.",
    "helena_plaque_examined": "A formidable plaque mounted on a heavy door reinforced with thick strips of iron and dark bolts. The initials 'H.S.' are boldly emblazoned in stylized gothic letters, surrounded by a wolf's paw print inside a circle of unbroken chain. The craftsmanship is severe and deliberate—a warning as much as a marker. The deep scratches gouged into the flooring trail directly toward this door.",
    "auria_plaque": "A pink door plaque decorated with faeries and stars.",
    "auria_plaque_examined": "A wooden plaque on a much lighter door painted in gentle shades of pink, decorated with the silhouettes of various faeries and stars. The name 'Auria' is spelled out in cute bubbly lettering, each letter slightly different as if drawn by hand. The whole effect is whimsical and warm—a stark contrast to the heavy iron door beside it.",
    "garden_plaque": "A rich mahogany plaque with delicate vine carvings.",
    "garden_plaque_examined": "A refined plaque on a door of rich mahogany, positioned on one side of the entry table. Delicate vines are carved across its surface, seeming to grow and wind with natural grace. 'Garden of Knowledge' is inscribed in elegant script. The craftsmanship suggests patience and care—each leaf distinct, each tendril purposeful.",
    "guest_plaque": "A yellow door plaque with floral decorations.",
    "guest_plaque_examined": "A wooden plaque on a door painted in pale yellow, positioned at the other end of the entry table nearest the open archway. Floral decals of various pinks and violets bloom across its surface. 'Guest Room' is written in friendly bubble letters, welcoming and cheerful—an invitation to travelers and visitors alike.",
    
    # HELENA'S ROOM
    "helena_bed": "A huge canopied bed supporting a thick king sized mattress, centered opposite the door. A wide assortment of fluffed soft pillows are distributed evenly—though some have been chewed and torn, stuffing poking free. The canopy bed is supported by a large kennel comprised of vertical bars, its cell door at the foot of the bed.",
    "helena_bed_examined": "The bed dominates the room. Red silk sheets, thick mattress, canopy overhead. The pillows show wolf behavior—chewed, torn, loved. Beneath it all, the kennel waits. Restraint points at each bedpost, the headboard, the canopy frame, and the kennel bars below.",
    "helena_kennel": "Beneath the bed, a kennel of vertical bars forms a cage. The cell door is at the foot of the bed. Inside, everything needed for a pet's comfort—and traces of someone who made it her own.",
    "helena_kennel_examined": "The kennel is large enough for two people. The bars are sturdy, the lock solid. Inside, you can see drawings taped to the bars, a blanket in the corner, colorful crayon wax filling old claw gouges in the floor. A heavy curtain at the back hides something beyond.",
    "helena_kennel_interior": """The space beneath Helena's bed has been transformed. Deep gouges from claws in the wooden floorboards have been filled in with colorful crayon wax. Drawings litter the floor and are taped to the bars with something sticky.

A blanket and pillow rest in the corner, stained with old tears. The handmade Eevee plushie sits nearby, violet panties still on its head.

|mThe signs of a little girl who waited so long to be remembered, loved, and brought back home.|n""",
    "helena_desk": "A metal desk a few steps from the bed, its surface covered with toys—dildos, vibrators, whips and feathers, large strap-ons, a black and purple cat o' nine tails. Four drawers are built into the front.",
    "helena_desk_examined": "The desk is metal, cold, functional. The toys atop it are arranged with care—each has its place. Four drawers beckon. The desk surface itself could serve other purposes...",
    "desk_drawer_1": "Paddles, crops, canes—discipline implements arranged with care.",
    "desk_drawer_2": "Medical items: sounds, speculums, gloves, bottles of lube.",
    "desk_drawer_3": "Keys on rings, leashes coiled neatly, various leads.",
    "desk_drawer_4": "Private items, personal effects. A small lever is visible at the back.",
    "purple_pet_bed": "A large circular pet bed in purple, set near the wall restraints. Large enough for two to curl up easily—three could fit with some squishiness.",
    "wall_restraints": "Two collars on chains are bolted to the northern wall, perfectly aligned with four sets of shackles bolted to the floor. The shackles are about a meter apart from each other and half a meter from the wall. Room for two, side by side.",
    "wall_restraints_examined": "The collars are padded but sturdy—meant for extended wear. The chains allow movement but not escape. The floor shackles can spread a person wide, force them to kneel, or simply hold them in place. The position would leave you facing the room, watching everything, while being watched.",
    "northern_tapestry": "The northern tapestry bears H.S. in stylized gothic letters surrounded by wolf paw prints and chain motifs. The oldest of the three, its colors slightly faded.",
    "southern_tapestry": "The southern tapestry is torn worse than the others—large fangs have shredded the fabric in places. Shadow's favorite, perhaps.",
    "eastern_tapestry": "The eastern tapestry is newer than its siblings but already shows Shadow's marks. A temporary addition.",
    "claw_gouges": "The wooden floors have been deeply gouged by sharp claws near the door and around the edges of furniture. Something large lives here. Something with claws. The marks are old but maintained—she doesn't fix them. They're meant to be there.",
    "chewed_pillows": "A wide assortment of fluffed soft pillows on the bed. Some have been chewed and torn with stuffing poking free. Wolf behavior. Pet behavior. The bed belongs to someone who shares it with beasts.",
    # Kennel contents
    "kennel_drawings": "Drawings litter the floor and are taped to the bars with something sticky. Crayon on paper. A little girl's art.",
    "kennel_drawings_examined": """Childish but heartfelt drawings:

• Three figures cuddling in snow: a Faerie, a huge black Wolf, and a little blonde girl
• A big bed with someone small underneath, waiting
• Hearts and 'mommy' and 'sissy' in wobbly letters
• A wolf with a huge red crayon addition between its legs
• 'I miss you' over and over in different colors""",
    "kennel_eevee": "A crudely handmade brown dog-fox stuffed animal, clearly meant to be the Pokémon Eevee. The stitching is uneven, made with love and desperation.",
    "kennel_eevee_examined": """A crudely handmade brown dog-fox stuffed animal, clearly meant to be the Pokémon Eevee. The stitching is uneven, made with love and desperation.

On its head sits a pair of violet-striped panties—Auria's, stolen, worn thin from being sucked on. The crotch is nearly gone, full of holes.

|mA comfort object for a little girl who needed something of her sister while she waited alone.|n""",
    "kennel_blanket": "A blanket and pillow rest in the corner, stained with old tears. The fabric is soft but worn, carrying the weight of lonely nights.",
    "kennel_crayon_gouges": "Deep gouges from claws in the wooden floorboards have been filled in with colorful crayon wax. A little girl made the scary marks into something pretty. Made the beast's space her own.",
    
    # DISCIPLINATION ROOM
    "bdsm_bench": "A standard BDSM bench stands in the center of the room, padded for extended sessions. Maneuverable limbs with built-in cuffs extend near the head and foot, allowing for precise positioning. The leather surface is easy to clean. A face hole allows breathing when positioned face-down.",
    "bdsm_bench_examined": "The bench is solidly built, designed for extended use. Padding is firm but not uncomfortable—meant for sessions, not comfort. The cuff limbs can be adjusted to spread or close, raise or lower. The leather has seen use but is well-maintained. Clean.",
    "floor_shackles": "Before the mirror, a pair of shackles are mounted to the floor on short chains—positioned for both ankles and wrists. Short enough to keep the subject low, facing their reflection. No escaping what you see.",
    "floor_shackles_examined": "Heavy iron shackles bolted into the polished oak. The chains are short—maybe a foot of slack for wrists, less for ankles. Positioned precisely before the mirror. You'd be forced to watch yourself. That's the point.",
    "ceiling_collar": "From the ceiling swings a collar on a length of chain, controllable by a lever on the wall. The collar can be raised or lowered to any height—kneeling, standing, tiptoe, or higher. Combined with the floor shackles, it can stretch a subject between floor and ceiling.",
    "ceiling_collar_examined": "A sturdy leather collar lined with padding—designed for extended wear, not to choke. The chain runs through a pulley system, the lever on the wall controlling height with mechanical precision. The highest setting would lift someone off their feet entirely.",
    "discipline_pet_bed": "A large circular pet bed rests near the floor shackles. For after. For waiting. For those who need to be kept close during another's discipline. Soft, comfortable, a place to recover and be cared for.",
    "toy_shelf": "A shelf against the wall holds a variety of items—lubricants, leather cuffs and binds, dildos, butt plugs, anal beads, and vibrators. Everything needed for thorough discipline. Everything organized and accessible.",
    "toy_shelf_examined": "The shelf is meticulously organized. Lubricants in one section, restraints in another. Toys arranged by size and type. Everything clean, everything ready. This is not an amateur collection.",
    "implement_rack": "Mounted to the wall opposite the toy shelf, a rack displays implements of punishment—whips, canes, floggers, a cat o' nine tails, and paddles for when the dominatrix is feeling soft. Each implement is well-maintained, ready for use.",
    "implement_rack_examined": "Each implement hangs in its place, well-maintained and ready. The canes range from thin and whippy to thick and thudy. The floggers vary in material—leather, suede, rubber. The cat o' nine tails looks... serious. The paddles seem almost gentle by comparison.",
    "discipline_mirror": "A large mirror dominates one section of wall, floor-to-ceiling, spotlessly clean. It reflects the room with brutal clarity—the bench, the implements, and whoever is being disciplined. There's no looking away from yourself here. You will watch your face as you're punished. You will see what you become.",
    "oak_chest": "In one corner sits a large oak chest, about a meter high, locked with a heavy padlock. Whatever's inside, Helena keeps it secured. The lock looks serious—this isn't meant to be opened casually.",
    "oak_chest_examined": "The chest is old, solid oak, iron-banded. The padlock is heavy-duty. Whatever's inside, Helena considers it too intense for casual access. Or too precious. Or both. The key is in her desk, Drawer 3.",
    "spreader_bar": "An extendable spreader bar rests in the corner—adjustable width for keeping legs or arms spread exactly as far as desired. Cuffs at each end. Can be used with the bench, ceiling collar, or standalone.",
    "spreader_bar_examined": "Metal bar with leather cuffs at each end, adjustable from narrow to very wide. Lockable once set. Portable—can be used anywhere. The leather cuffs are padded. Even Helena's cruelty has limits. Or at least, comfort during extended use.",
    "collar_lever": "A lever mounted on the western wall controls the ceiling collar's height. Pull down to lower, push up to raise. A locking mechanism keeps it in place once set.",
    "discipline_drain": "A drain is set into the polished oak floor near the center of the room. Practical for cleanup. The floor slopes slightly toward it—barely noticeable unless you're on your knees. This room gets... messy.",
    "discipline_floor": "Oaken floors, highly polished almost to the point you could slide upon them. The wood gleams under the lights. The polish makes it easy to clean. The slight slope toward the drain is almost imperceptible—unless you're down on them.",
    "erotic_paintings": "The far wall directly facing the head of the bench displays five paintings of erotic nature. The subject of the bench sees them throughout their discipline. Each depicts a different aspect of submission and dominance.",
    "erotic_paintings_examined": "Five paintings, each a masterwork of erotic art. 'The Lesson,' 'Surrender,' 'The Position,' 'Aftermath,' and... 'Helena's First.' The last one shows a familiar blonde figure, stretched in the ceiling collar, expression transcendent. The dominant behind her has dark hair, strong hands, pointed ears barely visible. Shadow.",
    
    # NURSERY
    "nursery_crib": "A large crib, more than large enough for an adult, nestled with warm blankets and various stuffed animals just waiting to be cuddled for nap time. The bars are sturdy, the gate lockable.",
    "changing_table": "A large changing table stands opposite the wardrobe, fully stocked with supplies—thick, crinkly diapers, powder, wipes, lotion. Everything a caretaker needs.",
    "nursing_chair": "A gliding nursing chair with a footstool, ensuring comfortable feeding time for little one and caretaker alike. It rocks smoothly, soothingly.",
    "play_pen": "In one corner, a wicker archway leads into The Play Pen of Adventure. Its interior seems larger than it should be—magic makes space for play.",
    "dollhouse": "A large dollhouse surrounded by dozens of dolls waiting to be played with. Nearby rests a small pink chest covered in Disney Princesses, holding hundreds of outfits.",
    
    # AURIA'S ROOM
    "auria_bed": "A comfy bed stands opposite the door, made up neatly with a pale purple bedspread. The pillows are arranged just so. It looks like it's waiting for someone.",
    "eevee_plushie": "Perched in the center of the bed is a fluffy Eevee plushie, with a jumbled pile around her—a plush dragon in shades of purple, a Squirtle and Chikorita small enough to fit in a coat pocket, and a happy looking raccoon. The Eevee's glass eyes almost seem to follow you.",
    "pillow_nest": "A small nest of cushions and pillows against the southern wall. From the wall above hangs chains long enough to curl up comfortably, ending in padded shackles and a collar inscribed with 'Auria'.",
    "auria_bookcase": "A large bookcase packed with books. Titles stand out: 'The Lion, the Witch and the Wardrobe', 'The Painted Man', 'The Black Prism', 'The Way of Kings'. A note beside it reads: 'Feel free to add something! Just let me know which is yours!'",
    "auria_trunk": "A closed trunk against the northern wall. It has a lock, but the key is in it.",
    "beaded_curtain": "A beaded curtain of crystal and colored glass separates Auria's Room from the Playroom. The strands shimmer with faint enchantment—not fae magic exactly, but something placed deliberately. No sound passes through. No light bleeds either direction.",
    
    # GUEST ROOM
    "guest_round_bed": "The bed is round, unusual and inviting. The mattress is so thick and soft that anyone lying on it sinks several inches into its embrace. Fluffy pillows cluster at the head, a few decorative stuffed animals arranged among them. The sheets smell of fresh linen.",
    "guest_round_bed_examined": "The round bed fills the corner, impossibly soft. The mattress would swallow you whole if you let it. Hidden beneath the top sheet—a waterproof cover, because this room is prepared for anything. Restraint points under the frame, at the headboard area, and... well, each other.",
    "guest_rocking_chair": "A generous rocking chair that could comfortably hold two. Soft cushions pad the seat and back, and a cozy fleece blanket is draped over one arm. It faces the door—whoever sits here sees everyone who enters. The rockers are smooth from use.",
    "guest_vanity": "White wood with that soft pink glow, topped with a large round mirror in a simple frame. The surface holds an assortment of basic toiletries and makeup—enough for any guest to freshen up or prepare themselves. A cushioned stool sits before it.",
    "guest_wardrobe": "Double doors stand open, revealing shelves and hanging space stocked with guest amenities. Fluffy towels, spare robes, and a selection of outfits in various sizes—some practical, some decidedly less so. Everything a guest might need for comfort or... other purposes.",
    "guest_dresser": "A dresser in soft white with pink undertones. The surface holds a few decorative items—a small vase, a scented candle, guest amenities. The drawers contain spare linens and basic supplies.",
    "guest_dresser_examined": "A dresser in soft white with pink undertones. A few items peek out from under the dresser, seemingly tucked away but not quite hidden—a modest vibrator, soft restraints, a blindfold, massage oil, a feather. They respawn. Always available.",
    "guest_drain": "A small drain set into the floor near the bed, barely visible.",
    "guest_drain_examined": "A small drain set into the floor near the bed, barely visible beneath the rug's edge. Practical for cleaning. Or other purposes.",
    "guest_stuffies": "A few decorative stuffed animals among the pillows.",
    "guest_stuffies_examined": "A few decorative stuffed animals sit among the pillows on the round bed. Generic, cute, comforting—left for guests who might want something to hold.\n\nElle's personal stuffies (including the wolf from Helena) have been packed away with her other things. These are new, for anyone.",
    "guest_plaque_room": "A decorative wooden plaque above the door.",
    "guest_plaque_room_examined": "Above the door, a decorative wooden plaque states: \"Welcome, we care about you.\"\n\nOriginally said \"Welcome Elle\"—updated for all guests now, but the care remains genuine.",
    "guest_area_rug": "A plush white area rug at the center of the room.",
    "guest_area_rug_examined": "A plush white area rug covers the center of the light wooden floor. Soft underfoot, clean and welcoming. The edges are slightly tucked to hide the floor drain nearby.",
    "guest_bedside_table": "A small bedside table matching the white-pink furniture set.",
    "guest_bedside_table_examined": "A small table beside the round bed, matching the white-with-pink-undertones of the other furniture. A lamp sits atop it, along with a small dish for personal items. The drawer holds nothing of note—left empty for guests.",
    "guest_wallpaper": "Striped wallpaper in pale yellow and white with roses and ivy.",
    "guest_wallpaper_examined": "Pale yellow and white stripes run vertically up the walls, printed at intervals with delicate roses and trailing ivy. The pattern is soft, feminine, welcoming—chosen by someone who wanted guests to feel at ease. The paper itself is in good condition, no peeling or fading.",
    
    # GARDEN OF KNOWLEDGE
    "garden_root_desk": "At the room's center, like the court surrounding a prized water feature in a garden, roots twist and weave to form a sturdy desk. The surface is smooth and polished from use, the wood warm and alive beneath your hands.",
    "garden_root_desk_examined": "The tangled roots form a hollow space beneath—large enough for someone to kneel comfortably, hidden from casual view but accessible to whoever sits at the desk. Natural restraint points where the roots twist together. The wood is warm, alive, breathing slowly.",
    "garden_desk_clean": "the surface is clear and polished, notes and quills arranged with care. Ready for work or... other activities",
    "garden_desk_cluttered": "though the clutter atop suggest an obscene activity, and recently so, may have taken place by evidence left in the form of wet spots on carefully written notes",
    "garden_desk_messy": "the surface is a mess of scattered papers, some stuck together, wet spots still glistening on the polished roots. Someone was busy here not long ago",
    "garden_desk_soaked": "the surface is practically dripping, papers ruined, ink running. Whatever happened here was intense, enthusiastic, and very recent. The wood will need to be wiped down",
    "garden_bookshelves": "Tall and sturdy book shelves formed by living woods, rooted into a rich floor of dark and loamy earth. The greens and vibrant yellows, whites, and baby blues of vine and flowers grow between the spines. The wood breathes slowly, growing imperceptibly, cradling knowledge in its embrace.",
    "garden_bookshelves_examined": "The living shelves hold many old and modern tomes: Magical grimoires, books of science and history, fact and fiction, tales of elegance, novels of debauchery, fairy tales and hentai.\n\nBrowsable sections: grimoires, science, fiction, hentai",
    "garden_section_grimoires": "Ancient tomes bound in leather and stranger materials. Spell formulae, ritual instructions, magical theory. Some pages shimmer. Some are best not read aloud.",
    "garden_section_science": "Factual tomes spanning centuries. Biology, chemistry, physics. Historical accounts from many worlds. Reference material for the curious mind.",
    "garden_section_fiction": "Tales of elegance, adventures, romances. Stories to lose yourself in. Novels of debauchery mixed with fairy tales. Something for every taste.",
    "garden_section_hentai": "An entire section dedicated to My Little Pony hentai. The collection is... comprehensive. Extensive. Suspiciously well-organized.\n\nFor unknown reasons.",
    "garden_mlp_section": "One section of the living bookshelves is completely dedicated to My Little Pony hentai. For unknown reasons.",
    "garden_mlp_section_examined": "An entire section of the living shelves is dedicated to My Little Pony hentai. The collection is... comprehensive. Extensive. Suspiciously well-organized.\n\nFor unknown reasons.\n\n|xThe vines around this section seem slightly embarrassed.|n",
    "garden_beanbag": "A plush beanbag chair of bright pink sits behind the root desk. It conforms perfectly to whoever sinks into it. The fabric is soft, well-loved—this is Oreo's favorite spot for reading, coloring, and other activities.",
    "garden_flora": "Vines and flowers adorn the space—greens and vibrant yellows, whites, and baby blues. They grow naturally, cared for by fae touch, adding life to the living library.",
    "garden_flora_examined": "The flowers aren't just decorative—they respond subtly to presence. Blooms turn toward readers, leaves rustle in welcome, vines occasionally brush against skin like gentle curiosity. This isn't a garden. It's alive, and it knows you're here.",
    "garden_stuffies": "Stuffed animals of various sizes and types are scattered across the loamy earth—dragons, unicorns, wolves, and things less identifiable. They're well-loved, some showing wear from hugging. Oreo's companions for reading and coloring.",
    "garden_coloring": "Coloring books lie scattered about, some open to half-finished pages. The art ranges from simple mandalas to elaborate fantasy scenes. Crayons and colored pencils are tucked nearby. The pages show skill and care—whoever colors these takes their time.",
    "garden_floor": "The floor is actual earth—rich, dark, loamy soil that the living bookshelves root into. It's soft underfoot, smelling of growth and life. Small plants peek up here and there. You could dig your toes in if you wanted.",
    
    # THE PLAYROOM (Auria's)
    "playroom_titanium_collar": "A smooth titanium collar attached to the wall via fine chain. \"Auria\" pulses in gentle blue letters—not magic exactly, but something technological or enchanted for permanence. Matching shackles for wrists and ankles hang beside it. This one glows. More formal. For scenes.",
    "playroom_titanium_collar_examined": "The collar is beautiful—smooth titanium, warm to the touch despite the metal. The inscription \"Auria\" glows softly, the letters pulsing like a slow heartbeat. The matching shackles are just as elegant. This is a statement piece. A claim made visible.",
    "playroom_pommel_horse": "A gymnastics pommel horse, repurposed for darker purposes. Padded cuffs attach to the handles, securing wrists in place. The center sports a twin dildo positioned perfectly to fill both holes when mounted. The leather is worn from use.",
    "playroom_pommel_horse_examined": "The horse is solidly built, the leather saddle worn smooth from use. The dildos are high quality—one vaginal, one anal, positioned so mounting is... complete. The wrist cuffs on the handles ensure you stay mounted. Once on, there's no getting off until someone lets you.",
    "playroom_suspension_bar": "A horizontal bar of titanium hangs from the ceiling, sturdy enough to support considerable weight. A pair of shackles dangle beneath it, waiting. For those who need to be elevated. Exposed. Vulnerable.",
    "playroom_suspension_bar_examined": "The bar is engineered for safety—weight-rated well beyond necessity. The shackles are padded for extended suspension. Height adjustable. Someone put thought into this. Someone who knows what they're doing.",
    "playroom_sex_swing": "A black sex swing hangs opposite the suspension bar, straps and buckles ready to hold someone secure and steady. The design allows for multiple positions while keeping the occupant completely restrained and accessible.",
    "playroom_sex_swing_examined": "Quality construction—the straps are reinforced, the buckles sturdy. Waist, wrists, ankles can all be secured. The design suspends the occupant at... convenient height. Accessible from any angle. Completely helpless.",
    "playroom_rocking_horse": "A rocking horse with a wicked purpose. Dildos rise from the saddle, positioned to fill when seated. Padded cuffs wait on the handles. Once mounted and secured, there's nothing to do but ride—and the motion ensures you do. Every rock. Every shift. Relentless.",
    "playroom_rocking_horse_examined": "The rocking mechanism is smooth, the motion natural. The dildos are positioned perfectly for someone seated in the saddle—vaginal and anal, filling completely with every rock. The wrist cuffs lock. You ride until someone decides you've had enough.",
    "playroom_spreader_bar": "A spreader bar propped against the closet, metal with padded ankle cuffs at each end. Adjustable width. Can be used with other furniture or on its own. Simple. Effective. Uncompromising in its purpose.",
    "playroom_stage": "The center of the room drops down—a small round stage surrounded by plush leather couches. Steps lead down onto the performance area. A silvery steel pole extends from floor to ceiling at center stage, catching every bit of light in the dim room. Worn spots mark her favorite heights.",
    "playroom_stage_examined": "The stage is professionally built—solid, the pole firmly anchored floor to ceiling. The worn spots on the pole show where hands grip most often, where thighs squeeze. Someone practices here. Someone performs here. The couches around it face inward, designed for watching.",
    "playroom_couches": "Plush leather couches surround the stage in a semicircle, positioned perfectly to watch the action. Dark leather, soft cushions, designed for comfort during long performances. Or other activities.",
    "playroom_couches_examined": "The couches are positioned for optimal viewing of the stage. Dark leather, easy to clean. Deep cushions for comfort during extended... watching. Each seat has a view of the pole. Each seat can see everything.",
    "playroom_toy_table": "A table set off to one side, its surface laid out with a selection of toys. Everything organized by type—dildos and vibrators in one section, plugs and beads in another. Everything accessible. Everything clean and ready for use.",
    "playroom_paddle_rack": "A series of hooks on the wall hold implements of correction. Paddles of various sizes and materials—leather, wood, silicone. One slender cane hangs at the end. All well-used. All well-maintained. Each with a different purpose, a different sensation.",
    "playroom_paddle_rack_examined": "The paddles range from soft leather (warm-up) to heavy wood (serious). The cane is thin, whippy, serious business. Each implement shows wear—these are used regularly. Someone knows what they like. Someone knows what works.",
    "playroom_closet": "A closet against one wall, doors slightly ajar. Inside, wardrobe saves wait—every look, every outfit, every version of yourself you've stored. Auria's costumes still hang here: \"Stage Kitten\" with its ears and tail, \"Good Girl\" in innocent whites, \"Service Ready\" in barely-there black. Waiting for someone to wear them again.",
    "playroom_closet_examined": "The costumes are well-made, well-maintained. \"Stage Kitten\" has real fur ears, a tail that attaches... somewhere. \"Good Girl\" is all white lace and innocence. \"Service Ready\" is barely-there black straps. Each one tells a story. Each one transforms the wearer.",
    "playroom_padded_walls": "Dark purple padding covers the walls—soft enough to press against, firm enough to hold shape. Not just aesthetic. The padding absorbs sound. What happens in the Playroom stays in the Playroom. No one outside hears. No one needs to know.",
    "playroom_mirror": "A large mirror takes up one section of the padded wall. Floor to ceiling, wide enough to see everything. It shows you exactly as you are—every mark, every flush, every reaction. Nothing hidden. Nothing spared. The frame is simple, dark wood. The glass is merciless.",
    "playroom_beaded_curtain": "A beaded curtain of crystal and colored glass marks the eastern threshold. From this side, the strands are darker—deep purples, blacks, occasional glints of silver. The curtain shimmers with faint enchantment. No sound passes through. No light bleeds. What happens in the Playroom stays in the Playroom.",
    
    # NURSERY
    "nursery_crib": "A large crib, more than big enough for an adult, rests against the wall. Warm blankets and various stuffed animals fill it, waiting for someone to cuddle. The bars can be raised and locked.",
    "nursery_crib_examined": "The crib is solidly built, adult-sized but designed to look like a baby's crib. The bars are sturdy, the locking mechanism subtle but effective. Once locked, you're not getting out without help. The blankets are soft, the stuffies well-loved. It's cozy—if you accept what it means to be in here.",
    "nursery_changing_table": "A large changing table stands ready, fully stocked with supplies—thick crinkly diapers, wipes, powder, cream. Built-in padded straps at wrist and ankle positions can secure an uncooperative little one.",
    "nursery_changing_table_examined": "The table is adult-sized, padded for comfort during extended changes. The straps are padded too—meant for security, not pain. Supplies are well-organized: diapers stacked by size, wipes within easy reach, powder and cream ready. This is used regularly. This is not a prop.",
    "nursery_nursing_chair": "A comfortable gliding nursing chair sits near the window, a matching footstool beside it. The cushions are soft, the glide smooth and soothing. Perfect for feeding time, comfort, or having a little one across your lap.",
    "nursery_window_seat": "A comfortable window seat laden with cushions provides a cozy place to sit and look out at the snowy forest. Sometimes you can see Shadow out there, watching.",
    "nursery_window": "A large window gives a view onto the snow-covered forest. Wolf tracks disturb the pristine snow—Shadow's path, coming and going. Sometimes, if you watch long enough, you can see the massive black wolf sitting in the snow, watching back.",
    "nursery_dollhouse": "A large dollhouse occupies one corner, surrounded by dozens of dolls. The dolls are detailed—anatomically complete, with poseable limbs. A pink Disney Princess chest nearby holds hundreds of outfits for them.",
    "nursery_dollhouse_examined": "The dollhouse is elaborate—multiple rooms, tiny furniture, even working lights. The dolls are... detailed. Very detailed. Anatomically complete in ways children's dolls never are. Some are posed in compromising positions. The Disney Princess chest holds hundreds of outfits, some quite adult in nature.",
    "nursery_wardrobe": "A wardrobe and matching chest of drawers hold clothes for playing dress-up. Onesies with snap crotches, footed pajamas, frilly dresses, overalls, princess costumes, animal onesies, mittens that lock, booties, bibs...",
    "nursery_wallpaper": "Bright and cheerful yellow wallpaper covers the walls, patterned with an assortment of cute animals. Fluffy bunnies hop between flowers. Pretty songbirds perch on branches. Wolves frolic playfully—a nod to Shadow, made cute and harmless.",
    "nursery_foam_floor": "The floor is covered in squishy foam, ensuring falls are harmless. A section in the center displays the ABCs in bright primary colors. Perfect for crawling. Perfect for tumbling. Perfect for being pushed down onto.",
    "nursery_toy_shelves": "Colourful shelves mounted on the walls hold a wide selection of toys. Building blocks, simple puzzles, picture books, stuffed animals, rattles, teething rings. Everything a little one could want to play with.",
    "nursery_blocks": "Colourful wooden blocks scattered messily near the changing table, as if someone was playing and got distracted. A teddy bear sits among them, slightly worn, clearly well-loved. The blocks spell out... something. Maybe a name. Maybe nonsense.",
    "nursery_diapers": "A stack of thick, crinkly diapers on the changing table. They come in various sizes—from actually-for-babies to definitely-for-adults. The crinkle is LOUD. Everyone will know. That's the point.",
    "nursery_colouring": "Hung proudly on one wall—a piece of colouring. A small pond surrounded by trees, the plant life a mix of greens and purples, a small dirt path leading away from the water. The colouring is earnest, staying mostly within the lines, done with focus and care. Princess made this. It hangs here because someone was proud of her.",
    "nursery_disney_chest": "A small pink chest covered in Disney Princesses—Cinderella, Belle, Ariel, Aurora. Inside: hundreds of tiny outfits for the dolls. Ball gowns, casual wear, swimsuits, and some outfits that are... decidedly adult in nature.",
    "nursery_playpen_arch": "A wicker archway leads into The Play Pen of Adventure. The air around it shimmers faintly. Whatever's inside is... different. The toys within seem to move when you're not looking directly at them. Something about this pen feels alive.",
    "nursery_teddy": "A well-loved teddy bear, slightly worn from hugging, sits among the scattered blocks. Someone clearly loves this bear very much.",
    
    # MOMO'S ROOM
    "momo_meadow": "The southern wall is only waist-high, otherwise open to a rolling meadow. A little brook catches the light in the distance, and a single tree provides a focal point on the horizon. The breeze carries honeysuckle.",
    "momo_meadow_examined": "The meadow stretches endlessly, impossibly—this room is inside the cabin, yet here is open sky and rolling grass. Magic, clearly. The brook sounds real. The breeze feels real. But you cannot climb over the half-wall and walk into that field. It's a window to somewhere else, or somewhere that doesn't exist. Beautiful regardless.",
    "momo_futon": "A comfortable yellow futon against the northern wall, piled high with pillows. Straw peeks out from underneath. A place for livestock to rest.",
    "momo_futon_examined": "The futon is soft, the pillows numerous. Straw scattered beneath gives it a stable feel. The yellow color matches the stucco walls, creating a warm, pastoral atmosphere. Someone sleeps here. Someone used to, at least.",
    "momo_collar": "A dark collar with silver studs and a golden bell, chained to the wall above the futon by a long leash. The bell has the words \"Helena's Momo\" engraved on the front.",
    "momo_collar_examined": "The leather is well-maintained, oiled regularly. Someone takes care of it even though Momo isn't here. The silver studs are polished. The golden bell is engraved with care: \"Helena's Momo.\" The leash is long enough to reach the bed and the feeding trough, but not the door. Whoever wears this collar stays.",
    "momo_trough": "A feeding trough against the wall near the bed. Wooden, sturdy, deep enough for food or water. Nearby, a faucet and hose with an adjustable showerhead.",
    "momo_trough_examined": "The trough is practical—easy to fill, easy to eat from (if you're on all fours). The hose is multifunctional: cleaning, watering, enema, temperature play. Everything for livestock care.",
    "momo_pillory": "A solid structure of oak and steel frames an adjustable pillory. It can hold someone's neck and hands at any level, even tilted to keep them standing on tiptoe.",
    "momo_pillory_examined": "The pillory is beautifully crafted—oak and steel, adjustable height and angle. It can force the occupant to stand, kneel, bend, or strain on tiptoe. The neck and wrist holes are padded for extended use. Someone put care into this. Someone who knows what they're doing.",
    "momo_milking_machine": "A milking machine complete with little bottles and skin lotion sits in an open cabinet at the base of the pillory. Ready for use on anyone producing milk.",
    "momo_milking_machine_examined": "The machine is professional grade—adjustable suction cups, tubes leading to collection bottles, lotion for aftercare. The labels show \"Laynie's Cream\" and \"Auria's Sweet\" as options. This isn't decorative. This is used.",
    "momo_breeding_bench": "An adjustable bench nearby the pillory. Padded, sturdy, with attachment points. Clearly designed for breeding.",
    "momo_breeding_bench_examined": "The bench adjusts in height and angle. Arm and leg rests extend or retract. Cuffs at wrist, ankle, and waist positions. Every adjustment serves one purpose: positioning someone perfectly for extended breeding sessions.",
    "momo_feather_pedestal": "A curious device like a pedestal with a feather rising from the top. Its purpose isn't immediately clear... until you're secured to it.",
    "momo_feather_pedestal_examined": "The pedestal has hidden restraint points—step onto it and your ankles lock. The feather is magical, or mechanical, or both. Once activated, it moves on its own, seeking out the most sensitive spots with unerring accuracy. It doesn't stop until turned off. It can't be reasoned with. No safeword.",
    "momo_tack": "Leather tack hangs on the eastern wall—harnesses and bridles in purple and black, a crop, and several lengths of rope.",
    "momo_tack_examined": "All items are functional and wearable. The harnesses provide grip points and display. The bridles have bits that restrict speech. The crop is well-worn. The rope is soft but strong. Everything for pony or cow play.",
    "momo_stucco": "Yellow stucco over wooden paneling, continuing a fence motif. The walls create a warm, pastoral atmosphere—a stable stall, not a room.",
    
    # ENTERTAINMENT ROOM
    "entertainment_shelves": "Bookshelves of dark lumber line the north wall, holding RPG manuals, board games, figurines, and stuffed creatures from fantasy, anime, and hentai. Dire wolves patrol the shelves. Proud amazons stand ready. Tentacle monsters lurk. One section is completely dedicated to MLP hentai for unknown reasons.",
    "entertainment_shelves_examined": "The collection is extensive and eclectic. D&D sourcebooks sit next to explicit doujinshi. Figurines of heroes and monsters are posed in various states—some combat, some... not. The MLP hentai section is well-thumbed. Someone has specific tastes.",
    "entertainment_gaming_table": "A gaming table with a recessed field suitable for maps and mazes, various games and notes. It resembles a repurposed pool table, with cup holders at its corners. Something glints beneath the felt—cables? Restraints? Hard to see unless you know to look.",
    "entertainment_gaming_table_examined": "The table is professional quality. But the real feature is hidden—restraint cables beneath the rim, ready to deploy. Someone can be secured to this table, spread across its surface, while the game continues around them. Roll for initiative.",
    "entertainment_wet_bar": "A wet bar near the doorway, saloon-style. Bar stools line its face. Clean crystal glasses line the counter. The wooden surface is scratched with graffiti. Behind it, liquors, wines, craft beers line the wall next to a small glass-door fridge.",
    "entertainment_wet_bar_examined": "The graffiti tells stories. \"Helena bred her bitches here.\" \"Auria was here ♡.\" Claw marks from Shadow. Tally marks labeled \"breeding count\" (high). \"Roll for anal\" with a d20 showing 20. This bar has seen things.",
    "entertainment_dairy_fridge": "A small fridge with a glass door behind the bar. Inside: fresh ice, chilled bottles of white liquid. The labels depict a blonde hucow and an auburn fae in cow-print bikinis. Banner: \"Helena's Dairy Farm—Whole breast milk from eager sluts to you!\"",
    "entertainment_dairy_fridge_examined": "\"Laynie's Cream\" features a blonde hucow, expression dazed and happy, milk dripping from overfull breasts. \"Auria's Sweet\" shows an auburn fae with visible wings, mischievously posing while milk streams down. The bottles are real. The sources are family.",
    "entertainment_sofa": "A black leather sofa sits with its back toward full-length windows offering a forest view. The leather is soft, the view spectacular, the implication clear—watch the forest while someone kneels between your legs.",
    "entertainment_sofa_examined": "The sofa is positioned perfectly—facing the windows, back to the room. Whoever sits here can watch the forest, the occasional wolf passing by, while receiving... service. The leather is easy to clean.",
    "entertainment_windows": "Full-length glass windows run floor to ceiling, offering a view of the snowy forest. Sometimes wolves pass by. Sometimes they stop and watch.",
    "entertainment_rgb": "RGB light strips line the shelves and ceiling, casting the room in configurable colored light. Currently set to gaming mode—soft purples and blues.",
    
    # BATHING LOUNGE
    "bathing_tiles": "Creamy, macchiato colored tiles streaked with black and gold flecks cover the walls and floor. The grout between is a complementary shade. The gold flecks catch the candlelight.",
    "bathing_shelves": "Open shelves hold baskets of fresh fluffy towels, flowers and potpourri, and common toiletries. Everything you need to freshen up.",
    "bathing_hygiene_cabinet": "A cabinet containing hygiene supplies—lotions, soaps, powders, makeup, razors. The soaps and lotions can be applied, leaving a scent on the user.",
    "bathing_toy_cabinet": "A cabinet containing... other supplies. Waterproof vibrators, plugs, cuffs, rope, blindfolds, lubricants. Everything for fun in the shower.",
    "bathing_wash_basin": "A crystalline wash basin with a rounded mirror in an ornate frame decorated with wolf prints. A hand towel hangs limp in a ring on its edge.",
    "bathing_squat_toilet": "A white porcelain squat toilet set into the floor in an alcove. Guests must squat for their relief. A bidet sprayer is installed. The alcove is completely open to the room—no door, no curtain, no privacy.",
    "bathing_squat_toilet_examined": "The lack of privacy is intentional. Anyone using this toilet is on display. The bidet can be used for cleaning, stimulation, or temperature play. Exhibition is built into the design.",
    "bathing_wall_rings": "Hooks and rings mounted to the walls among paintings of flora and fauna. Decorative... or functional, with the right equipment.",
    "bathing_candles": "Candles of various colors rise on metal stands in each corner, ready to be lit for the mood and atmosphere desired. Lavender for calm, vanilla for warmth, jasmine for sensuality, sandalwood for grounding, or 'heat' for something more primal.",
    "bathing_bath_mat": "A plush bath mat lies before the shower door, embroidered text reading: \"Magic showers, last for hours.\" This is not decoration. This is a warning.",
    "bathing_cursed_shower": "Thick clear glass panels frame a glass door with a bronzed handle shaped like a large phallus. Beyond the glass, a spacious walk-in shower awaits. Runes shimmer in the tiles. The glass fogs and clears rhythmically. Breathing.",
    "bathing_cursed_shower_examined": "The shower is spacious—room for six comfortably. Steel rings throughout, padded ledges, adjustable nozzles. No knobs. Instead, translucent script explains: the shower is a mimic, changed to please. Speak your desires or think them clearly. But don't think too fast—this magic shower WILL last for hours. No safeword.",
    "bathing_cursed_shower_interior": "Inside the shower, the walls pulse faintly. Runes glow. Nozzles and hoses wait. Steel rings for restraints. Padded ledges for positioning. The mimic is aware of you. It's curious. It wants to please. It will. For as long as it takes.",
    
    # JACUZZI ROOM
    "jacuzzi_window": "Thick, invisible glass stretches floor to ceiling, offering a scenic view. Snow-covered forest canopy stretches endlessly. Purple mountains shadow the horizon. At night, the aurora dances.",
    "jacuzzi_window_examined": "The view shifts with time—bright morning sun, golden evening, aurora at night. Occasionally, wolves pass through the forest below. A massive black one sometimes pauses at the treeline, seeming to look directly at the window.",
    "jacuzzi_mural": "A highly detailed mural of colored tiles and glass wraps around the bottom of the walls. It tells Shadow's story in five panels—a wolf hunting its prey, filled with carnal lust.",
    "jacuzzi_mural_examined": "Panel 1: The Hunt Begins—a black direwolf with monstrous red phallus, white-gowned maidens unaware. Panel 2: The Chase—tearing gowns piece by piece. Panel 3: The Capture—maiden pinned, exposed. Panel 4: The Claiming—explicit coupling, the knot visible. Panel 5: The Pack—wolf, human, and those between, family of predators and willing prey.",
    "jacuzzi_pedestals": "Black pedestals of welded chains support lush potted ivies and sensuous candles. The chains are decorative but sturdy—functional if needed.",
    "jacuzzi_wall_restraints": "Steel cables affixed to the walls with collars and shackles that dangle against the tile. They can extend several feet or be locked at any length per the host's desires.",
    "jacuzzi_wall_restraints_examined": "Multiple anchor points allow for standing, kneeling, or spread positions. The cables adjust—short leash keeps you against the wall, long leash lets you reach the jacuzzi edge for service. Restrained guests are forced to watch the jacuzzi activities.",
    "jacuzzi_hot_tub": "The wolf-print shaped jacuzzi is dark in color and large, space enough for five. Hot water undulates, obscuring the bottom. Four toe-pad seats surround a central throne position. A control panel glints at the throne's rim.",
    "jacuzzi_hot_tub_examined": "Each toe seat has a hidden surprise beneath the bubbles—a 9-inch wolf cock dildo with knot, positioned to impale whoever sits. The throne has the control panel: jets, temperature, dildo vibration and thrust per seat, knot inflation, seat locks. The host controls everything.",
    "jacuzzi_throne": "The throne position faces all four toe seats and the window. A silver control panel is built into the rim. Only the host sees everything—guests silhouetted against the view, impaled on hidden surprises.",
    
    # HIDDEN LABORATORY
    "lab_alchemy_equipment": "Alchemical equipment lines one wall—beakers, tubes, burners, a distillation apparatus bubbling with something violet. The air hums with contained magic.",
    "lab_alchemy_examined": "The violet distillation is ongoing—some long-term project of Oreo's. Labels identify ingredients: \"Moonpetal,\" \"Wyrm Scale,\" \"Essence of Want,\" \"Condensed Blush.\" Whatever's being made, it's probably kinky.",
    "lab_ingredient_shelves": "Shelves hold labeled ingredients. Moonpetal, Wyrm Scale, Essence of Want, Condensed Blush. Everything organized in Oreo's meticulous script.",
    "lab_workbench": "A workbench dominates the center, covered in half-finished projects. A journal lies open, filled with cramped handwriting and diagrams.",
    "lab_oreo_journal": "Oreo's research notes. Cramped handwriting, detailed diagrams, theoretical formulations. Subjects include: enhanced sensitivity compounds, lactation inducers, obedience enhancement, heat cycle manipulation. Scientific approach to debauchery.",
    "lab_magitech_station": "Where magic meets machinery—a station glowing with runes and crystals. A partially assembled collar prototype sits in a vice, enchantment half-woven.",
    "lab_collar_prototype": "A collar in progress. The enchantment is half-complete—threads of magic visible, runes partially inscribed. Whatever this does, it's not ready yet. But it will be.",
    "lab_storage_cabinet": "A cabinet holding finished products: potions, enchanted items, toys with unusual properties. Everything labeled in Oreo's meticulous script. \"Obedience Potion (mild).\" \"Sensitivity Enhancer.\" \"Heat Inducer.\" \"Compliance Collar (Mark II).\"",
    "lab_ladder": "A ladder leads up to Helena's kennel. The only way in or out of this hidden space.",
    
    # BIRTHING DEN
    "den_magic_globes": "Dim light emanates from unseen globes of magic. The light shifts slowly, responding to the time of day and the mood of the den.",
    "den_ceiling": "The jagged ceiling bares pointed earthen fangs. Occasionally they're mirrored or joined in great columns by rocky teeth below. Ancient. Primal.",
    "den_origin_paintings": "Vague scenes in primitive paints cover the walls. Great feral wolves stalk, hunt, and capture prey. One sequence tells the story of how Shadow claimed Helena.",
    "den_origin_paintings_examined": "Six panels tell the origin: 1) Woman faces wolf-spirit in ritual. 2) Battle, blood mingles. 3) Woman absorbs spirit, changes. 4) Woman becomes wolf. 5) First claiming, pack begins. 6) Pack grows, prints multiply. This is sacred history.",
    "den_pack_prints": "Ashen wolf prints adorn the walls—sacred marks of pack membership. Shadow's print is largest, with Helena's handprint pressed within it. Other prints surround them: Laynie, Whisper, Blaze, the puppies.",
    "den_pack_prints_examined": "The prints are made in ash and blood mixed with mineral pigment. They're renewed periodically, kept fresh. Each print represents a bond, a claiming, a birth. The pack's family tree written on stone.",
    "den_warm_springs": "Warm springs form a series of comfortable pools, flowing lazily through the cavern. The clear water shimmers aquamarine with magical essence. Perfect for birthing, healing, or simply soaking.",
    "den_warm_springs_examined": "The water has healing properties—minor wounds close faster, exhaustion fades. The magical essence is visible as a faint glow. New mothers labor here. New pack members are cleansed here. The water remembers.",
    "den_birthing_nest": "A thin layer of padding makes a surprisingly comfortable nest for new mothers. Rendered hide, fur, and torn clothing from those who ignored the sign at the forest edge.",
    "den_birthing_nest_examined": "The materials are varied—some clearly animal hide, some suspiciously human clothing. All soft now, worked until comfortable. This nest has held mothers giving birth. This nest has held Laynie.",
    
    # PRINCESS' PRIVATE SPACE
    "princess_mural": "An elaborate mural painted with care and intent. It depicts a young blonde girl in a pillory being milked, watched by Helena, Shadow, and a hovering fae. This is documentation, not fantasy.",
    "princess_mural_examined": "The blonde girl is unmistakably Laynie. The pillory holds her secure. The milking machine is attached. Helena watches with pride. Shadow looms protectively. Auria hovers, delighted. This happened. This was recorded. This is who she is here.",
    "princess_doodles": "Cute doodles of cows, wolves, faeries, and naked women sprinkled among coloring pages taped to the walls. A child's drawings—if that child knew far too much.",
    "princess_fake_window": "A poster window gives the illusion of peering out onto a lush pasture with grazing cattle. The view changes with time—sunny morning, warm afternoon, golden sunset, moonlit night.",
    "princess_bed": "A low, king-sized bed with pink covers and tiaras decorating the headboard. Big fluffy pillows invite comfort. Metal railing runs along the sides with cuffs dangling—always present, always ready.",
    "princess_bed_examined": "The cuffs are never removed. They dangle from the rails, waiting. Wrist cuffs, ankle cuffs, ready for four-point spread or simple one-wrist leashing. The pink covers are soft. The restraints are serious. Both are always present.",
    "princess_pillory": "An antique wooden pillory with dark cherry finish stands near the center. Elegant despite its purpose. Matches the one in the mural exactly.",
    "princess_pillory_examined": "The cherry wood is polished, beautiful. The neck and wrist holes are sized perfectly. Height adjustable. Positioned for milking machine access. Elegant bondage furniture. For a princess who needs to be put in her place.",
    "princess_milker": "A large machine with tubes, dials, and various sizes of cups stands beside the pillory. Designed to milk the little princess and make her moo.",
    "princess_milker_examined": "Multiple cup sizes fit different breasts. Adjustable suction, controllable rhythm. The milk extracted here stocks the dairy fridge in Entertainment. Laynie's Cream. The label isn't a joke.",
    "princess_toy_chest": "A chest near the doorway, decorated with princess motifs. Inside: everything Mommy needs to raise her little girls.",
    "princess_toy_chest_examined": "Stuffed animals and princess toys sit alongside pacifiers, cowbell collars, nipple clamps, small plugs, and vibrating wands. Picture books about cows. Diapers. Milk bottles. Everything for raising proper little heifers.",
    "princess_beaded_curtain": "A beaded curtain of pink and white strands covers the doorway. Princess-appropriate. But it hides nothing. Sound passes through. Smell carries. Wolves enter freely. The princesses have no lock on their door. They don't get one.",
}


# =============================================================================
# ROOM-SPECIFIC TYPECLASSES
# =============================================================================

class WolfPrints(CabinObject):
    """Dynamic wolf prints that track Shadow's passage."""
    
    portable = AttributeProperty(default=False)
    current_state = AttributeProperty(default="absent")
    decay_ticks = AttributeProperty(default=0)
    
    decay_rates = {"fresh": 3, "recent": 6, "fading": 10}
    
    state_descriptions = {
        "fresh": "Fresh muddy wolf prints track from the door, still wet, still sharp. Shadow has just passed through. The scratches at the threshold are deeper than usual—pressed hard by something large moving with purpose.",
        "recent": "Muddy wolf prints cross the floor, drying but distinct. Shadow came through not long ago. The scratches at the threshold catch the light.",
        "fading": "Faint wolf prints mark the floor, mud mostly dried and crumbling. The scratches at the threshold remain sharp, worn into the wood over time.",
        "absent": "Scratches mark the threshold where the wooden floor changes—claw marks from something large, worn into the wood over time. No prints today, but the marks remember.",
    }
    
    def at_object_creation(self):
        super().at_object_creation()
        self.locks.add("get:false()")
        self.locks.add("view:perm(all)")
    
    def get_display_desc(self, looker=None, **kwargs):
        return self.state_descriptions.get(self.current_state, self.state_descriptions["absent"])
    
    def on_shadow_pass(self):
        """Called when Shadow passes through."""
        self.current_state = "fresh"
        self.decay_ticks = 0


class ShadowMusk(CabinObject):
    """Invisible atmospheric that tracks Shadow's presence via scent."""
    
    portable = AttributeProperty(default=False)
    current_state = AttributeProperty(default="absent")
    
    state_inline = {
        "present": ", though a heavy, unmistakable musk hangs in the air",
        "recent": ", though a slightly musky undertone wafts from somewhere nearby",
        "fading": ", though a faint musky undertone lingers",
        "absent": "",
    }
    
    def at_object_creation(self):
        super().at_object_creation()
        self.locks.add("get:false()")
        self.locks.add("view:false()")
    
    def get_inline_desc(self) -> str:
        return self.state_inline.get(self.current_state, "")


class SeasonalPotpourri(CabinObject):
    """Potpourri bowl with scent that changes by season."""
    
    portable = AttributeProperty(default=False)
    
    seasonal_scents = {
        "spring": "smelling of fresh green herbs and early wildflowers",
        "summer": "smelling of wild flowers and mint",
        "autumn": "smelling of dried apples and warm spices",
        "winter": "smelling of pine and cedar",
    }
    
    seasonal_examine = {
        "spring": "potpourri_spring",
        "summer": "potpourri_summer",
        "autumn": "potpourri_autumn",
        "winter": "potpourri_winter",
    }
    
    def get_season(self) -> str:
        """Get current season from room or global."""
        if self.location and hasattr(self.location, 'current_season'):
            return self.location.current_season
        return get_season()
    
    def get_scent(self) -> str:
        season = self.get_season()
        return self.seasonal_scents.get(season, self.seasonal_scents["summer"])
    
    def return_appearance(self, looker, **kwargs):
        season = self.get_season()
        desc_key = self.seasonal_examine.get(season, "potpourri_summer")
        desc = OBJECT_DESCS.get(desc_key, "A decorative bowl filled with dried flowers and herbs.")
        return f"|w{self.key}|n\n\n{desc}"


class ViewerAwarePortrait(CabinObject):
    """Portrait that shows different text based on who's looking."""
    
    portable = AttributeProperty(default=False)
    
    # Characters who see themselves in the painting
    recognized_keys = AttributeProperty(default=["laynie", "princess", "auria", "oreo"])
    recognized_tags = AttributeProperty(default=["claimed", "harem"])
    
    def _identify_viewer(self, looker) -> str:
        if not looker:
            return "stranger"
        key = looker.key.lower() if looker.key else ""
        if key in ("helena", "mistress helena"):
            return "helena"
        elif key in ("laynie", "princess"):
            return "laynie"
        elif key in ("auria",):
            return "auria"
        elif key in ("shadow", "shadowkaven"):
            return "shadow"
        elif key in ("oreo",):
            return "oreo"
        # Check tags
        if hasattr(looker, 'tags'):
            for tag in self.recognized_tags:
                if looker.tags.has(tag, category="identity") or looker.tags.has(tag):
                    return "claimed"
        return "stranger"
    
    def get_viewer_addition(self, looker) -> str:
        """Get additional text based on who's looking."""
        viewer_type = self._identify_viewer(looker)
        
        if viewer_type in ("laynie", "princess"):
            return OBJECT_DESCS.get("portrait_laynie", "")
        elif viewer_type in ("auria", "oreo"):
            return OBJECT_DESCS.get("portrait_auria", "")
        elif viewer_type == "claimed":
            return OBJECT_DESCS.get("portrait_claimed", "")
        else:
            return OBJECT_DESCS.get("portrait_stranger", "")
    
    def return_appearance(self, looker, **kwargs):
        parts = [f"|w{self.key}|n", ""]
        parts.append(OBJECT_DESCS.get("portrait_base", "A large portrait."))
        parts.append(self.get_viewer_addition(looker))
        return "\n".join(parts)


class WelcomeRoom(CabinRoom):
    """Welcome Room with wolf prints shortcode support."""
    
    shadow_present = AttributeProperty(default=False)
    
    def process_shortcodes(self, text: str, looker=None) -> str:
        text = super().process_shortcodes(text, looker)
        
        # Wolf prints shortcode
        wolf_prints = self._get_wolf_prints()
        if wolf_prints:
            prints_desc = wolf_prints.get_display_desc(looker)
            text = text.replace("<wolf_prints.desc>", prints_desc + " ")
        else:
            text = text.replace("<wolf_prints.desc>", "")
        
        return text
    
    def _get_wolf_prints(self):
        for obj in self.contents:
            if isinstance(obj, WolfPrints):
                return obj
        return None


class PassagewayRoom(CabinRoom):
    """Passageway with potpourri and musk shortcodes."""
    
    current_season = AttributeProperty(default="summer")
    
    def process_shortcodes(self, text: str, looker=None) -> str:
        text = super().process_shortcodes(text, looker)
        
        # Potpourri scent
        potpourri = self._get_potpourri()
        if potpourri:
            text = text.replace("<potpourri.scent>", potpourri.get_scent())
        else:
            text = text.replace("<potpourri.scent>", "smelling of wild flowers and mint")
        
        # Shadow musk - note: shortcode is <shadow_musk.desc>
        musk = self._get_musk()
        if musk:
            text = text.replace("<shadow_musk.desc>", musk.get_inline_desc())
        else:
            text = text.replace("<shadow_musk.desc>", "")
        
        return text
    
    def _get_potpourri(self):
        for obj in self.contents:
            if isinstance(obj, SeasonalPotpourri):
                return obj
        return None
    
    def _get_musk(self):
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
            musk = self._get_musk()
            if musk:
                musk.on_shadow_pass()
    
    def tick_musk(self) -> bool:
        """Tick musk decay."""
        musk = self._get_musk()
        if musk:
            return musk.tick_decay()
        return False


class HelenaRoom(CabinRoom):
    """Helena's Room with bed state, tapestry, and trapdoor shortcodes."""
    
    def process_shortcodes(self, text: str, looker=None) -> str:
        text = super().process_shortcodes(text, looker)
        
        # Bed state
        bed = self._get_bed()
        if bed and hasattr(bed, 'get_state_desc'):
            text = text.replace("<bed.state>", bed.get_state_desc())
        else:
            text = text.replace("<bed.state>", "It is currently made with fresh sheets of velvety red silk with a fluffy blanket atop them—neatly tucked in at the edges.")
        
        # Tapestries - check if open and add inline text
        for direction in ["north", "south", "east"]:
            tag = f"<tapestry_{direction}.state>"
            tapestry = self._get_tapestry(direction)
            if tapestry and getattr(tapestry, 'is_open', False):
                inline = getattr(tapestry.db, 'open_inline', '')
                text = text.replace(tag, inline)
            else:
                text = text.replace(tag, "")
        
        # Trapdoor
        trapdoor = self._get_trapdoor()
        if trapdoor and getattr(trapdoor, 'is_revealed', False):
            trap_text = (
                "\n\nNear the desk, a |ctrapdoor|n in the floor stands open—a dark "
                "square revealing stone steps that descend into the Hidden "
                "Laboratory below. Cold air rises from the darkness."
            )
            text = text.replace("<trapdoor.state>", trap_text)
        else:
            text = text.replace("<trapdoor.state>", "")
        
        return text
    
    def _get_bed(self):
        for obj in self.contents:
            if isinstance(obj, HelenaBed):
                return obj
        return None
    
    def _get_tapestry(self, direction: str):
        for obj in self.contents:
            if isinstance(obj, TapestryExit) and getattr(obj.db, 'direction', '') == direction:
                return obj
        return None
    
    def _get_trapdoor(self):
        for obj in self.contents:
            if isinstance(obj, HiddenTrapdoor):
                return obj
        return None
    
    def _get_kennel(self):
        for obj in self.contents:
            if isinstance(obj, HelenaKennel):
                return obj
        return None
    
    def return_appearance(self, looker, **kwargs):
        """Check if looker is inside kennel first."""
        kennel = self._get_kennel()
        if kennel and kennel.is_character_inside(looker):
            return kennel.get_interior_view(looker)
        return super().return_appearance(looker, **kwargs)


class HelenaBed(CabinFurniture):
    """Helena's bed with dynamic state and decay."""
    
    portable = AttributeProperty(default=False)
    capacity = AttributeProperty(default=4)
    bed_state = AttributeProperty(default="fresh")
    supported_positions = AttributeProperty(default=[
        "lying", "lying at edge", "on all fours", "spread-eagle",
        "riding", "face-down", "pinned"
    ])
    restraint_points = AttributeProperty(default=[
        "bedpost (corner)", "headboard", "canopy frame", "kennel bars (below)"
    ])
    
    BED_STATES = ["fresh", "rumpled", "messy", "soaked", "ripped"]
    
    BED_STATE_DESCS = {
        "fresh": "It is currently made with fresh sheets of velvety red silk with a fluffy blanket atop them—neatly tucked in at the edges.",
        "rumpled": "The red silk sheets are rumpled, the blanket pushed aside—someone slept here recently.",
        "messy": "The sheets are twisted and damp, wet spots darkening the silk. The blanket has been kicked half onto the floor.",
        "soaked": "The silk sheets are soaked through, clinging to the mattress. The scent of sex hangs heavy in the air around it.",
        "ripped": "The sheets are torn, claw marks shredding the red silk. The blanket lies in tatters. Someone—or something—got very rough.",
    }
    
    def get_state_desc(self) -> str:
        """Get current state description for shortcode."""
        return self.BED_STATE_DESCS.get(self.bed_state, self.BED_STATE_DESCS["fresh"])
    
    def soil(self) -> str:
        """Make the bed messier (one step)."""
        current_idx = self.BED_STATES.index(self.bed_state)
        if current_idx < len(self.BED_STATES) - 1:
            self.bed_state = self.BED_STATES[current_idx + 1]
            return f"The bed becomes {self.bed_state}."
        return "The bed can't get any messier."
    
    def clean(self) -> str:
        """Clean the bed one step toward fresh."""
        current_idx = self.BED_STATES.index(self.bed_state)
        if current_idx > 0:
            self.bed_state = self.BED_STATES[current_idx - 1]
            return f"You tidy up the bed. It's now {self.bed_state}."
        return "The bed is already fresh."
    
    def clean_fully(self) -> str:
        """Clean the bed completely to fresh."""
        self.bed_state = "fresh"
        return "You change the sheets and make the bed properly. Fresh and ready."
    
    def rip(self) -> str:
        """Rip the sheets (rough activity)."""
        self.bed_state = "ripped"
        return "The sheets tear under the force. Claw marks shred the silk."
    
    def return_appearance(self, looker, **kwargs):
        parts = [f"|w{self.key}|n", ""]
        parts.append(OBJECT_DESCS.get("helena_bed", "A huge canopied bed."))
        parts.append("")
        parts.append(f"|xCurrent state:|n {self.get_state_desc()}")
        
        if hasattr(self, 'current_users') and self.current_users:
            parts.append("")
            parts.append(self.get_occupied_desc())
        
        return "\n".join(parts)


class HelenaKennel(CabinFurniture):
    """The kennel under Helena's bed - enterable furniture with interior view."""
    
    portable = AttributeProperty(default=False)
    capacity = AttributeProperty(default=2)
    is_locked = AttributeProperty(default=False)
    curtain_open = AttributeProperty(default=False)
    inside_characters = AttributeProperty(default=[])
    supported_positions = AttributeProperty(default=["inside", "curled up inside", "kneeling inside", "lying inside", "face at bars", "displayed"])
    
    def is_character_inside(self, character) -> bool:
        """Check if character is inside the kennel."""
        if not character:
            return False
        char_id = character.id if hasattr(character, 'id') else None
        return char_id in self.inside_characters if char_id else False
    
    def enter_kennel(self, character) -> Tuple[bool, str]:
        """Have a character enter the kennel."""
        if self.is_locked:
            return False, "The kennel door is locked."
        if self.is_character_inside(character):
            return False, "You're already inside the kennel."
        if len(self.inside_characters) >= self.capacity:
            return False, "The kennel is too crowded."
        
        char_id = character.id if hasattr(character, 'id') else None
        if char_id:
            chars = list(self.inside_characters)
            chars.append(char_id)
            self.inside_characters = chars
        
        return True, (
            "You crawl through the kennel door and into the space beneath "
            "the bed. The bars close around you. Through them, you can see, "
            "hear, and smell everything in Helena's room above."
        )
    
    def leave_kennel(self, character) -> Tuple[bool, str]:
        """Have a character leave the kennel."""
        if not self.is_character_inside(character):
            return False, "You're not inside the kennel."
        if self.is_locked:
            return False, "The kennel door is locked. You're trapped inside."
        
        char_id = character.id if hasattr(character, 'id') else None
        if char_id:
            chars = list(self.inside_characters)
            if char_id in chars:
                chars.remove(char_id)
            self.inside_characters = chars
        
        return True, "You crawl out of the kennel, leaving the small space behind."
    
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
            OBJECT_DESCS.get("helena_kennel_interior", "You are inside the kennel."),
            "",
        ]
        
        # Curtain state
        if self.curtain_open:
            parts.append(
                "The heavy |ccurtain|n at the back is drawn aside, revealing a "
                "dark tunnel descending into the earth. The breeze flows "
                "freely, carrying scents of the Birthing Den below."
            )
        else:
            parts.append(
                "At the back, a heavy |ccurtain|n sways gently in a cool breeze. "
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
            if looker and char_id != looker.id:
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
        parts = [OBJECT_DESCS.get("helena_kennel", "A kennel beneath the bed.")]
        
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


class HelenaDesk(CabinFurniture):
    """Metal desk with toys and 4 drawers. Drawer 4 contains mechanism to reveal trapdoor."""
    
    portable = AttributeProperty(default=False)
    capacity = AttributeProperty(default=1)
    supported_positions = AttributeProperty(default=["seated", "bent over", "displayed atop"])
    drawer_open = AttributeProperty(default=[False, False, False, False])
    
    drawer_contents = {
        1: "Paddles, crops, canes—discipline implements arranged with care.",
        2: "Medical items: sounds, speculums, gloves, bottles of lube.",
        3: "Keys on rings, leashes coiled neatly, various leads.",
        4: "Private items, personal effects. A small lever is visible at the back.",
    }
    
    def open_drawer(self, num: int) -> Tuple[bool, str]:
        """Open a drawer."""
        if num < 1 or num > 4:
            return False, "Drawers are numbered 1-4."
        
        idx = num - 1
        states = list(self.drawer_open)
        
        if states[idx]:
            return False, f"Drawer {num} is already open."
        
        states[idx] = True
        self.drawer_open = states
        
        contents = self.drawer_contents.get(num, "Empty.")
        return True, f"You open drawer {num}.\n\n|xContents:|n {contents}"
    
    def close_drawer(self, num: int) -> Tuple[bool, str]:
        """Close a drawer."""
        if num < 1 or num > 4:
            return False, "Drawers are numbered 1-4."
        
        idx = num - 1
        states = list(self.drawer_open)
        
        if not states[idx]:
            return False, f"Drawer {num} is already closed."
        
        states[idx] = False
        self.drawer_open = states
        return True, f"You close drawer {num}."
    
    def use_mechanism(self, user) -> str:
        """Pull the lever in drawer 4 to toggle trapdoor."""
        if not self.drawer_open[3]:
            return "You need to open drawer 4 first."
        
        if not self.location:
            return "Something is wrong."
        
        # Find trapdoor in room
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
        parts.append(OBJECT_DESCS.get("helena_desk", "A metal desk."))
        
        # Show drawer states
        parts.append("")
        parts.append("|xDrawers:|n")
        for i, is_open in enumerate(self.drawer_open):
            state = "open" if is_open else "closed"
            parts.append(f"  Drawer {i+1}: {state}")
            if is_open:
                contents = self.drawer_contents.get(i+1, "Empty.")
                parts.append(f"    → {contents}")
        
        return "\n".join(parts)


class TapestryExit(DefaultExit):
    """A tapestry that hides an exit. When closed: exit not usable. When open: exit visible."""
    
    is_open = AttributeProperty(default=False)
    
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


class HiddenTrapdoor(DefaultExit):
    """A trapdoor hidden in the floor. Only visible/usable when revealed by mechanism."""
    
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
            return ""
        return "trapdoor"


class KennelCurtainExit(DefaultExit):
    """Exit from inside the kennel to Birthing Den. Only usable if inside kennel and curtain open."""
    
    def at_traverse(self, traversing_object, target_location, **kwargs):
        """Check conditions before allowing traverse."""
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
# KENNEL CONTENTS - Viewable objects
# =============================================================================

class KennelDrawings(CabinObject):
    """Princess's drawings taped to the kennel bars."""
    
    portable = AttributeProperty(default=False)
    
    def return_appearance(self, looker, **kwargs):
        return f"|wPrincess's Drawings|n\n\n{OBJECT_DESCS.get('kennel_drawings_examined', 'Drawings on paper.')}"


class EeveePlushie(CabinObject):
    """The handmade Eevee with Auria's worn panties."""
    
    portable = AttributeProperty(default=True)
    
    def return_appearance(self, looker, **kwargs):
        return f"|wHandmade Eevee Plushie|n\n\n{OBJECT_DESCS.get('kennel_eevee_examined', 'A handmade plushie.')}"


class TearStainedBlanket(CabinObject):
    """The blanket and pillow in the kennel."""
    
    portable = AttributeProperty(default=False)
    
    def return_appearance(self, looker, **kwargs):
        return f"|wTear-Stained Blanket|n\n\n{OBJECT_DESCS.get('kennel_blanket', 'A blanket in the corner.')}"


class CrayonGouges(CabinObject):
    """The claw gouges filled with crayon wax."""
    
    portable = AttributeProperty(default=False)
    
    def return_appearance(self, looker, **kwargs):
        return f"|wCrayon-Filled Gouges|n\n\n{OBJECT_DESCS.get('kennel_crayon_gouges', 'Colorful marks in the floor.')}"


# =============================================================================
# ROOM OBJECTS - Viewable
# =============================================================================

class ClawGouges(CabinObject):
    """The claw gouges in the room floor."""
    
    portable = AttributeProperty(default=False)
    
    def return_appearance(self, looker, **kwargs):
        return f"|wClaw Gouges|n\n\n{OBJECT_DESCS.get('claw_gouges', 'Deep gouges in the floor.')}"


class ChewedPillows(CabinObject):
    """The chewed pillows on the bed."""
    
    portable = AttributeProperty(default=False)
    
    def return_appearance(self, looker, **kwargs):
        return f"|wChewed Pillows|n\n\n{OBJECT_DESCS.get('chewed_pillows', 'Pillows on the bed.')}"


class WallRestraints(CabinFurniture):
    """Two collars on chains + four floor shackles. Capacity 2."""
    
    portable = AttributeProperty(default=False)
    capacity = AttributeProperty(default=2)
    supported_positions = AttributeProperty(default=["standing chained", "kneeling chained", "spread on floor", "displayed"])
    restraint_points = AttributeProperty(default=[
        "collar chain (left)", "collar chain (right)",
        "floor shackle (left wrist)", "floor shackle (right wrist)",
        "floor shackle (left ankle)", "floor shackle (right ankle)",
    ])
    
    def return_appearance(self, looker, **kwargs):
        parts = [f"|w{self.key}|n", ""]
        parts.append(OBJECT_DESCS.get("wall_restraints", "Restraints on the wall."))
        parts.append("")
        parts.append(OBJECT_DESCS.get("wall_restraints_examined", ""))
        return "\n".join(parts)


class PurplePetBed(CabinFurniture):
    """Large circular pet bed near the wall restraints."""
    
    portable = AttributeProperty(default=False)
    capacity = AttributeProperty(default=3)
    supported_positions = AttributeProperty(default=["curled up", "lying", "cuddling", "squeezed in"])
    
    def return_appearance(self, looker, **kwargs):
        return f"|w{self.key}|n\n\n{OBJECT_DESCS.get('purple_pet_bed', 'A large pet bed.')}"


class DisciplinationRoom(CabinRoom):
    """
    Disciplination Room - clinical discipline space with lighting modes.
    
    Features:
    - Adjustable lighting modes (standard/ambient/interrogation)
    - Professional equipment
    - Mirror psychology
    - No ambiguity about purpose
    """
    
    lighting_mode = AttributeProperty(default="standard")
    
    lighting_descs = {
        "standard": (
            "Bright, clinical light fills the room from strips in the ceiling. "
            "Every detail visible. No shadows to hide shame or tears."
        ),
        "ambient": (
            "Dimmer, warmer light softens the room's edges. More intimate "
            "discipline. Still enough light to see everything in the mirror."
        ),
        "interrogation": (
            "A harsh spotlight illuminates the bench, leaving darkness around "
            "the edges. All focus on the subject. Nowhere to hide."
        ),
    }
    
    def at_object_creation(self):
        """Initialize the room."""
        super().at_object_creation()
        self.db.atmosphere = {
            "sounds": "hum of lights, creak of leather, breathing",
            "scents": "leather, polish, sweat",
            "mood": "discipline",
        }
        self.db.temperature = "cool"
    
    def set_lighting(self, mode: str) -> str:
        """Set lighting mode."""
        mode = mode.lower()
        if mode not in self.lighting_descs:
            return f"Invalid mode. Choose: {', '.join(self.lighting_descs.keys())}"
        self.lighting_mode = mode
        return f"Lighting set to {mode}.\n\n{self.lighting_descs[mode]}"
    
    def process_shortcodes(self, text: str, looker=None) -> str:
        text = super().process_shortcodes(text, looker)
        
        lighting_desc = self.lighting_descs.get(self.lighting_mode, self.lighting_descs["standard"])
        text = text.replace("<lighting.desc>", lighting_desc)
        
        return text


class CeilingCollar(CabinFurniture):
    """The ceiling collar system with height control."""
    
    capacity = AttributeProperty(default=1)
    current_height = AttributeProperty(default="lowered")
    is_locked = AttributeProperty(default=False)
    occupant = AttributeProperty(default=None)
    
    heights = ["lowered", "kneeling", "standing", "tiptoe", "lifted"]
    
    height_descs = {
        "lowered": "The collar hangs at floor level, waiting to be attached.",
        "kneeling": "The collar holds its occupant at kneeling height, unable to stand.",
        "standing": "The collar keeps its occupant standing, controlled by the neck.",
        "tiptoe": "The collar forces its occupant onto their toes, straining.",
        "lifted": "The collar pulls upward—feet barely touching the ground, choking.",
    }
    
    def raise_collar(self) -> str:
        idx = self.heights.index(self.current_height)
        if idx < len(self.heights) - 1:
            self.current_height = self.heights[idx + 1]
            return f"The collar rises. {self.height_descs[self.current_height]}"
        return "The collar is at maximum height."
    
    def lower_collar(self) -> str:
        idx = self.heights.index(self.current_height)
        if idx > 0:
            self.current_height = self.heights[idx - 1]
            return f"The collar lowers. {self.height_descs[self.current_height]}"
        return "The collar is at its lowest."
    
    def lock_collar(self) -> str:
        """Lock collar at current height."""
        self.is_locked = True
        return f"The collar locks in place at {self.current_height} height."
    
    def unlock_collar(self) -> str:
        """Unlock collar."""
        self.is_locked = False
        return "The collar unlocks, ready to be adjusted."


class BDSMBench(CabinFurniture):
    """
    Central BDSM bench with adjustable cuff limbs.
    """
    
    capacity = AttributeProperty(default=1)
    supported_positions = AttributeProperty(default=[
        "bent over", "lying face down", "lying face up", "restrained spread"
    ])
    
    restraint_points = AttributeProperty(default={
        "wrist_cuffs": "wrists secured forward",
        "ankle_cuffs": "ankles secured, can be spread",
        "waist_strap": "pinned to bench surface",
    })
    
    # Adjustable features
    head_position = AttributeProperty(default="neutral")  # raised, lowered, neutral


class FloorShackles(CabinFurniture):
    """
    Floor-mounted shackles before the mirror.
    """
    
    capacity = AttributeProperty(default=1)
    supported_positions = AttributeProperty(default=[
        "kneeling", "standing spread", "all fours", "collapsed"
    ])
    
    restraint_points = AttributeProperty(default={
        "ankle_shackles": "feet locked to floor",
        "wrist_shackles": "hands to floor, limited movement",
    })


class CollarLever(CabinObject):
    """
    Wall-mounted lever to control ceiling collar.
    """
    
    portable = AttributeProperty(default=False)
    
    def get_collar(self):
        """Find the ceiling collar in the same room."""
        if not self.location:
            return None
        for obj in self.location.contents:
            if isinstance(obj, CeilingCollar):
                return obj
        return None


class SpreaderBar(CabinObject):
    """
    Adjustable spreader bar - can be taken as inventory.
    """
    
    portable = AttributeProperty(default=True)
    width = AttributeProperty(default="medium")  # narrow, medium, wide, very wide
    
    width_options = ["narrow", "medium", "wide", "very wide"]
    
    def set_width(self, new_width: str) -> str:
        """Adjust the spreader bar width."""
        new_width = new_width.lower()
        if new_width not in self.width_options:
            return f"Invalid width. Choose: {', '.join(self.width_options)}"
        self.width = new_width
        return f"The spreader bar is adjusted to {new_width} width."


class DisciplinePetBed(CabinFurniture):
    """
    Large circular pet bed for aftercare.
    """
    
    capacity = AttributeProperty(default=3)
    supported_positions = AttributeProperty(default=[
        "curled up in", "lying in", "cuddled in", "waiting in"
    ])


class ToyShelf(CabinContainer):
    """
    Shelf of toys and accessories.
    """
    pass


class ImplementRack(CabinContainer):
    """
    Wall-mounted rack of punishment implements.
    """
    pass


class LockedOakChest(CabinContainer):
    """
    Locked chest containing intense items.
    """
    
    is_locked = AttributeProperty(default=True)
    key_location = AttributeProperty(default="Helena's desk, Drawer 3")
    
    def unlock(self, key=None) -> str:
        """Attempt to unlock the chest."""
        if not self.is_locked:
            return "The chest is already unlocked."
        # For now, just check if they have a key object
        self.is_locked = False
        return "The heavy padlock clicks open. The chest can now be opened."
    
    def lock(self) -> str:
        """Lock the chest."""
        self.is_locked = True
        return "The padlock snaps shut."


class DisciplineMirror(CabinObject):
    """
    Large mirror for psychological element.
    """
    
    portable = AttributeProperty(default=False)


class FloorDrain(CabinObject):
    """
    Floor drain for cleanup.
    """
    
    portable = AttributeProperty(default=False)


class EroticPaintings(CabinObject):
    """
    Collection of erotic paintings on the wall.
    """
    
    portable = AttributeProperty(default=False)
    
    PAINTINGS = {
        1: {
            "title": "The Lesson",
            "desc": (
                "A figure bent over a bench much like this one, face turned toward "
                "the viewer with tears streaming down but eyes showing acceptance. "
                "Behind them, a dominant figure mid-swing with a cane. The "
                "composition focuses on the moment before impact—anticipation "
                "crystallized."
            ),
        },
        2: {
            "title": "Surrender",
            "desc": (
                "Two lovers intertwined, one clearly in control, the other melting "
                "into submission. Their faces show the passion visible in the art "
                "of lovemaking—not just sex, but complete giving over. Beautiful "
                "and intimate."
            ),
        },
        3: {
            "title": "The Position",
            "desc": (
                "An instructional piece almost—a figure demonstrating perfect "
                "submission posture. Knees spread, back arched, hands behind head, "
                "eyes down. Annotated in elegant script with the expectations."
            ),
        },
        4: {
            "title": "Aftermath",
            "desc": (
                "A figure curled in a pet bed, marked and satisfied, being gently "
                "stroked by their dominant. The discipline is over. What remains "
                "is care."
            ),
        },
        5: {
            "title": "Helena's First",
            "desc": (
                "A painting that might be familiar... A blonde figure in the "
                "ceiling collar, stretched on tiptoe, marked with fresh welts, "
                "expression transcendent. The dominant is barely visible—dark "
                "hair, strong hands, the suggestion of pointed ears. A record "
                "of a real moment."
            ),
        },
    }
    
    def return_appearance(self, looker=None, **kwargs):
        """Show painting list when examined."""
        desc = self.db.desc or "Five erotic paintings hang on the far wall."
        
        parts = [f"|w{self.key}|n", "", desc, ""]
        parts.append("|wThe Paintings:|n")
        for num, data in self.PAINTINGS.items():
            parts.append(f"  {num}. \"|y{data['title']}|n\"")
        parts.append("")
        parts.append("|w(look painting <number> for details)|n")
        
        return "\n".join(parts)
    
    def get_painting(self, number: int) -> str:
        """Get detailed description of a specific painting."""
        if number not in self.PAINTINGS:
            return f"There is no painting {number}. The paintings are numbered 1-5."
        
        painting = self.PAINTINGS[number]
        return f"|w\"{painting['title']}\"|n\n\n{painting['desc']}"


class PolishedFloor(CabinObject):
    """
    The polished oak floor.
    """
    
    portable = AttributeProperty(default=False)


class AuriasRoomFallback(CabinRoom):
    """
    Auria's Room - FALLBACK VERSION.
    
    The full implementation with all fae ambient effects, family recognition,
    Living Eevee integration, and more is in:
        typeclasses/rooms/aurias_room.py
    
    This simplified fallback is used if the module isn't installed.
    """
    
    fae_magic_visible = AttributeProperty(default=True)
    
    fae_ambient_pool = [
        "A dust mote catches the light and seems to dance with purpose before fading.",
        "The Eevee's ear twitches. Just a draft. Probably.",
        "A flower in the vase turns slightly toward you. Coincidence.",
        "You hear the faintest giggle from nowhere. The room feels warmer.",
        "One of the stuffies seems to have moved. You're sure it was always facing that way.",
        "The collar's inscription pulses once, gently, like a heartbeat.",
        "A page turns in the open book. There's no breeze.",
        "The pink walls seem to glow slightly brighter for a moment.",
    ]
    
    family_messages = {
        "helena": "The room welcomes you. It knows you keep it ready.",
        "laynie": "The pink wraps around you like a hug. Sister's room. Safe place.",
        "shadow": "The fae magic prickles at your presence—not hostile, but watchful.",
    }
    
    def get_fae_ambient(self) -> Optional[str]:
        if not self.fae_magic_visible:
            return None
        if random.random() < 0.3:
            return random.choice(self.fae_ambient_pool)
        return None
    
    def get_family_message(self, character) -> Optional[str]:
        if not character:
            return None
        key = character.key.lower() if character.key else ""
        for name, msg in self.family_messages.items():
            if name in key:
                return msg
        return None


class PlayroomRoom(CabinRoom):
    """
    The Playroom - soundproofed BDSM space (Auria's).
    
    Features:
    - Padded walls (soundproofing)
    - Stage with pole
    - Various bondage equipment
    - Time-variant candle lighting
    """
    
    # Soundproofing
    is_soundproofed = AttributeProperty(default=True)
    
    # Time descriptions for the playroom
    PLAYROOM_TIME_DESCS = {
        "day": "Candles unlit. The room waits in comfortable dimness, equipment casting soft shadows against the padded walls.",
        "morning": "Candles unlit. The room waits in comfortable dimness, equipment casting soft shadows against the padded walls.",
        "afternoon": "Candles unlit. The room waits in comfortable dimness, equipment casting soft shadows against the padded walls.",
        "evening": "Candles flicker to life as evening falls. The metal catches the light—pole, chains, titanium collar pulsing its soft blue.",
        "night": "Intimate darkness. The collar's glow is more pronounced now, \"Auria\" written in light. The padded walls absorb all sound.",
        "latenight": "The deepest quiet. Even the collar dims. The room holds its breath, waiting for whoever might need it.",
    }
    
    def at_object_creation(self):
        """Initialize the playroom."""
        super().at_object_creation()
        self.db.atmosphere = {
            "sounds": "silence, the creak of leather, distant heartbeat",
            "scents": "leather, metal polish, something warm",
            "mood": "deliberate",
        }
        self.db.temperature = "warm"
        self.db.lighting = "dim"
    
    def get_time_description(self) -> str:
        """Get time-appropriate description."""
        period = get_time_period()
        time_map = {"dawn": "morning", "morning": "morning", "afternoon": "afternoon",
                    "evening": "evening", "night": "night", "latenight": "latenight"}
        period_key = time_map.get(period, "evening")
        return self.PLAYROOM_TIME_DESCS.get(period_key, self.PLAYROOM_TIME_DESCS["evening"])
    
    def process_shortcodes(self, text: str, looker=None) -> str:
        """Process playroom-specific shortcodes."""
        text = super().process_shortcodes(text, looker)
        text = text.replace("<time.desc>", self.get_time_description())
        return text


class TitaniumCollar(CabinFurniture):
    """
    Wall-mounted titanium collar with glowing inscription.
    """
    
    capacity = AttributeProperty(default=1)
    is_worn = AttributeProperty(default=False)
    wearer_id = AttributeProperty(default=None)
    
    supported_positions = AttributeProperty(default=[
        "chained to wall in", "kneeling in", "standing in"
    ])
    
    restraint_points = AttributeProperty(default={
        "collar": "neck in titanium collar",
        "wrist_shackles": "wrists in matching shackles",
        "ankle_shackles": "ankles in matching shackles",
    })


class PommelHorse(CabinFurniture):
    """
    Repurposed gymnastics pommel horse with restraints and dildos.
    """
    
    capacity = AttributeProperty(default=1)
    
    supported_positions = AttributeProperty(default=[
        "mounted on", "bent over", "strapped to"
    ])
    
    restraint_points = AttributeProperty(default={
        "wrist_cuffs": "wrists in padded cuffs on handles",
    })
    
    # Penetration features
    has_dildos = AttributeProperty(default=True)
    dildo_type = AttributeProperty(default="twin (vaginal + anal)")


class SuspensionBar(CabinFurniture):
    """
    Ceiling-mounted titanium suspension bar with shackles.
    """
    
    capacity = AttributeProperty(default=1)
    
    supported_positions = AttributeProperty(default=[
        "hanging from", "suspended from", "strung up on"
    ])
    
    restraint_points = AttributeProperty(default={
        "wrist_shackles": "wrists in ceiling shackles",
    })


class SexSwing(CabinFurniture):
    """
    Black sex swing with full restraint capability.
    """
    
    capacity = AttributeProperty(default=1)  # Plus partner access
    
    supported_positions = AttributeProperty(default=[
        "suspended in", "strapped into", "spread in", "reclining in"
    ])
    
    restraint_points = AttributeProperty(default={
        "wrist_straps": "wrists in padded straps",
        "ankle_straps": "ankles in padded straps",
        "waist_strap": "waist secured by strap",
    })


class PlayroomRockingHorse(CabinFurniture):
    """
    Rocking horse with saddle dildos and wrist cuffs.
    """
    
    capacity = AttributeProperty(default=1)
    
    supported_positions = AttributeProperty(default=[
        "mounted on", "riding", "rocking on"
    ])
    
    restraint_points = AttributeProperty(default={
        "wrist_cuffs": "wrists in padded cuffs on handles",
    })
    
    has_dildos = AttributeProperty(default=True)
    dildo_type = AttributeProperty(default="saddle-mounted (vaginal + anal)")


class PlayroomSpreaderBar(CabinObject):
    """
    Portable spreader bar with adjustable width.
    """
    
    portable = AttributeProperty(default=True)
    width = AttributeProperty(default="adjustable")
    
    width_options = ["narrow", "medium", "wide", "very wide"]
    
    def set_width(self, new_width: str) -> str:
        """Adjust the spreader bar width."""
        new_width = new_width.lower()
        if new_width not in self.width_options:
            return f"Invalid width. Choose: {', '.join(self.width_options)}"
        self.width = new_width
        return f"The spreader bar is adjusted to {new_width} width."


class PerformanceStage(CabinFurniture):
    """
    Sunken stage with steel pole for performances.
    """
    
    capacity = AttributeProperty(default=3)
    
    supported_positions = AttributeProperty(default=[
        "performing on", "dancing on", "kneeling on", "displayed on",
        "pole dancing on", "center stage on"
    ])
    
    has_pole = AttributeProperty(default=True)


class AudienceCouches(CabinFurniture):
    """
    Plush leather couches surrounding the stage.
    """
    
    capacity = AttributeProperty(default=6)
    
    supported_positions = AttributeProperty(default=[
        "seated on", "lounging on", "watching from", "sprawled on"
    ])


class PlayroomToyTable(CabinContainer):
    """
    Table with organized selection of toys.
    """
    pass


class PaddleRack(CabinContainer):
    """
    Wall-mounted rack of impact implements.
    """
    pass


class PlayroomCloset(CabinContainer):
    """
    Closet with Auria's costumes.
    """
    
    is_open = AttributeProperty(default=False)
    
    # Auria's costumes
    costumes = AttributeProperty(default=[
        "Stage Kitten (ears and tail)",
        "Good Girl (innocent whites)",
        "Service Ready (barely-there black)",
    ])


class PaddedWalls(CabinObject):
    """
    Soundproofed padded walls.
    """
    
    portable = AttributeProperty(default=False)


class PlayroomMirror(CabinObject):
    """
    Full-length mirror that shows everything.
    """
    
    portable = AttributeProperty(default=False)


class BeadedCurtain(CabinObject):
    """
    Magical soundproofed beaded curtain.
    """
    
    portable = AttributeProperty(default=False)


class NurseryRoom(CabinRoom):
    """
    The Nursery - bright, cheerful, safe for littles.
    
    Features time-variant descriptions, visibility connections to
    adjacent rooms, and integration with ageplay systems.
    """
    
    # Nursery-specific time descriptions
    NURSERY_TIME_DESCS = {
        "dawn": "Pale morning light filters through the window, catching dust motes that drift lazily through the air. The wolf tracks outside are fresh. A good time to wake up, be changed, have breakfast.",
        "morning": "Bright sunlight fills the nursery with cheerful warmth. The yellow wallpaper seems to glow. The toys wait eagerly on their shelves.",
        "afternoon": "Playtime lighting fills the room. The toys seem to wait eagerly. The Play Pen's wicker arch glimmers faintly, invitingly.",
        "evening": "Softer golden light filters through. The crib looks inviting for naptime. The nursing chair glows warmly, ready for feeding time.",
        "night": "A soft nightlight casts gentle shadows across the room. The crib is cozy, blankets ready. The forest outside is silver and shadow. Time for sleep, little one.",
        "latenight": "The nightlight hums softly. Everything is still, peaceful, safe. The stuffed animals in the crib keep watch through the darkness.",
    }
    
    def at_object_creation(self):
        """Initialize the nursery."""
        super().at_object_creation()
        self.db.atmosphere = {
            "sounds": "music box from Auria's room, soft lullabies, occasional crinkling",
            "scents": "baby powder, clean linen, flowers from Auria's room",
            "mood": "safe regression",
        }
        self.db.temperature = "warm"
    
    def get_time_description(self) -> str:
        """Get time-appropriate description."""
        period = get_time_period()
        time_map = {"dawn": "dawn", "morning": "morning", "afternoon": "afternoon",
                    "evening": "evening", "night": "night", "latenight": "latenight"}
        period_key = time_map.get(period, "morning")
        return self.NURSERY_TIME_DESCS.get(period_key, self.NURSERY_TIME_DESCS["morning"])
    
    def process_shortcodes(self, text: str, looker=None) -> str:
        """Process nursery-specific shortcodes."""
        text = super().process_shortcodes(text, looker)
        text = text.replace("<time.desc>", self.get_time_description())
        return text


class PlayPenRoom(CabinRoom):
    """
    The Play Pen of Adventure - magical shrinking sub-area.
    
    Characters are shrunk to figurine size upon entry.
    Living toy figurines inhabit multiple biomes.
    CNC elements - figurines will include visitors whether they want or not.
    """
    
    # Magic properties
    shrink_active = AttributeProperty(default=True)
    time_dilation = AttributeProperty(default=4.0)  # 4 hours inside = 1 hour outside
    
    def at_object_creation(self):
        """Initialize the Play Pen."""
        super().at_object_creation()
        self.db.atmosphere = {
            "sounds": "tiny footsteps, plastic creaking, distant moans",
            "scents": "plastic, foam, something musky",
            "mood": "dangerous playground",
        }
    
    def at_object_receive(self, moved_obj, source_location, move_type=None, **kwargs):
        """Apply shrinking magic when someone enters."""
        super().at_object_receive(moved_obj, source_location, **kwargs)
        
        is_character = hasattr(moved_obj, 'account') or getattr(moved_obj, 'is_npc', False)
        
        if is_character and self.shrink_active:
            moved_obj.msg(
                "|mAn odd feeling of change washes over you as you step through "
                "the wicker arch. The world lurches, expands, grows MASSIVE around "
                "you. By the time you've gathered your senses, you realize—you've "
                "been shrunk to the size of a toy figurine.|n"
            )
            moved_obj.db.is_shrunk = True
            moved_obj.db.original_size = moved_obj.attributes.get("size", default="normal")
    
    def at_object_leave(self, moved_obj, target_location, move_type=None, **kwargs):
        """Remove shrinking when someone leaves."""
        super().at_object_leave(moved_obj, target_location, **kwargs)
        
        is_character = hasattr(moved_obj, 'account') or getattr(moved_obj, 'is_npc', False)
        
        if is_character and getattr(moved_obj.db, 'is_shrunk', False):
            moved_obj.msg(
                "|mAs you pass through the wicker arch, the world snaps back to "
                "normal size. You're yourself again—full-sized, back in the nursery. "
                "The toys behind you are just toys once more.|n"
            )
            moved_obj.db.is_shrunk = False


class NurseryCrib(CabinFurniture):
    """
    Adult-sized crib with lockable bars.
    
    Large enough for adults. Bars can be raised and locked.
    Contains warm blankets and stuffed animals.
    """
    
    capacity = AttributeProperty(default=2)
    is_locked = AttributeProperty(default=False)
    bars_raised = AttributeProperty(default=True)
    
    supported_positions = AttributeProperty(default=[
        "lying in", "curled up in", "restless in", "trapped in",
        "being tucked into", "being changed in"
    ])
    
    restraint_points = AttributeProperty(default={
        "crib_bars": "wrists through bars",
        "mittens": "hands in locking mittens",
    })
    
    def lock_bars(self, locker=None) -> str:
        """Lock the crib bars."""
        if not self.bars_raised:
            return "The bars need to be raised first."
        self.is_locked = True
        return "You lock the crib bars with a soft click. No escaping now."
    
    def unlock_bars(self, unlocker=None) -> str:
        """Unlock the crib bars."""
        self.is_locked = False
        return "You unlock the crib bars."
    
    def raise_bars(self, raiser=None) -> str:
        """Raise the crib bars."""
        self.bars_raised = True
        return "You raise the crib bars into place."
    
    def lower_bars(self, lowerer=None) -> str:
        """Lower the crib bars."""
        if self.is_locked:
            return "The bars are locked. Unlock them first."
        self.bars_raised = False
        return "You lower the crib bars."


class ChangingTable(CabinFurniture):
    """
    Changing table with built-in restraint straps.
    
    Fully stocked with supplies. Straps can secure occupant.
    """
    
    capacity = AttributeProperty(default=1)
    straps_secured = AttributeProperty(default=False)
    
    supported_positions = AttributeProperty(default=[
        "lying on", "squirming on", "strapped to", "cooperative on", "checking"
    ])
    
    restraint_points = AttributeProperty(default={
        "wrist_straps": "wrists in padded straps",
        "ankle_straps": "ankles in padded straps",
    })
    
    # Supplies tracking
    supplies = AttributeProperty(default={
        "diapers": 20,
        "wipes": 100,
        "powder": "full",
        "cream": "full",
    })
    
    def secure_straps(self, target=None) -> str:
        """Secure the straps."""
        self.straps_secured = True
        return "You secure the padded straps, holding the little one in place."
    
    def release_straps(self, releaser=None) -> str:
        """Release the straps."""
        self.straps_secured = False
        return "You release the straps."


class NursingChair(CabinFurniture):
    """
    Gliding nursing chair with footstool.
    
    Comfortable for caretaker and little. Supports nursing/bottle feeding.
    """
    
    capacity = AttributeProperty(default=2)
    
    supported_positions = AttributeProperty(default=[
        "seated in", "nursing in", "bottle feeding in", "rocking in",
        "lap sitting in", "punishment position in"
    ])


class NurseryWindowSeat(CabinFurniture):
    """
    Comfortable window seat with view of forest.
    """
    
    capacity = AttributeProperty(default=3)
    
    supported_positions = AttributeProperty(default=[
        "sitting on", "curled up on", "kneeling on", "cuddling on"
    ])


class NurseryDollhouse(CabinFurniture):
    """
    Large interactive dollhouse with anatomically complete dolls.
    """
    
    capacity = AttributeProperty(default=2)  # For playing at
    
    supported_positions = AttributeProperty(default=[
        "playing at", "kneeling before", "arranging dolls in"
    ])


class NurseryWardrobe(CabinContainer):
    """
    Wardrobe containing little clothes for dress-up.
    """
    
    is_open = AttributeProperty(default=False)


class PlayPenArch(CabinObject):
    """
    The wicker arch entrance to the Play Pen.
    
    Not actually enterable as furniture - it's an exit.
    This object provides the description and examine text.
    """
    
    portable = AttributeProperty(default=False)


class NurseryWallpaper(CabinObject):
    """Yellow wallpaper with cute animals."""
    portable = AttributeProperty(default=False)


class NurseryFoamFloor(CabinObject):
    """Squishy foam flooring."""
    portable = AttributeProperty(default=False)


class NurseryWindow(CabinObject):
    """Window overlooking snowy forest."""
    portable = AttributeProperty(default=False)
    shadow_visible = AttributeProperty(default=False)


class NurseryToyShelf(CabinContainer):
    """Colourful shelves holding toys."""
    pass


class NurseryBlocks(CabinObject):
    """Blocks and teddy bear near changing table."""
    portable = AttributeProperty(default=False)


class CrinklyDiapers(CabinObject):
    """Stack of thick crinkly diapers."""
    portable = AttributeProperty(default=False)


class PrincessColouring(CabinObject):
    """Laynie's colouring hung on the wall."""
    portable = AttributeProperty(default=False)


class DisneyPrincessChest(CabinContainer):
    """Pink chest with doll outfits."""
    pass


class GuestRoom(CabinRoom):
    """Guest Room with time-variant descriptions."""
    
    time_descriptions = AttributeProperty(default={
        "morning": "Soft light filters through, the white and yellow feeling bright and fresh. The vanilla-linen scent is crisp. A good place to wake slowly.",
        "afternoon": "Warm and quiet. The pink-hued furniture seems to glow in the gentle light. Comfortable for a nap.",
        "evening": "Golden light makes everything softer. The rocking chair invites you to sit, wrapped in the fleece blanket.",
        "night": "Soft lamplight. The round bed beckons, promising to swallow you in comfort. The room feels safe. Private.",
    })
    
    def process_shortcodes(self, text: str, looker=None) -> str:
        text = super().process_shortcodes(text, looker)
        
        period = get_time_period()
        # Map to our time keys
        time_map = {"dawn": "morning", "morning": "morning", "afternoon": "afternoon", 
                    "evening": "evening", "night": "night", "latenight": "night"}
        period_key = time_map.get(period, "afternoon")
        time_desc = self.time_descriptions.get(period_key, self.time_descriptions["afternoon"])
        text = text.replace("<time.desc>", time_desc)
        
        return text


class RoundBed(CabinFurniture):
    """The round bed - unusual, inviting, with hidden waterproof cover."""
    
    portable = AttributeProperty(default=False)
    capacity = AttributeProperty(default=4)
    supported_positions = AttributeProperty(default=[
        "lying (center)", "lying (edge)", "sprawled", "curled together",
        "on all fours", "riding", "face-down"
    ])
    restraint_points = AttributeProperty(default=[
        "bed frame (under)", "headboard area", "each other"
    ])
    has_waterproof_cover = AttributeProperty(default=True)
    
    def return_appearance(self, looker, **kwargs):
        parts = [f"|w{self.key}|n", ""]
        parts.append(OBJECT_DESCS.get("guest_round_bed", "A round bed."))
        
        if hasattr(self, 'current_users') and self.current_users:
            parts.append("")
            parts.append(self.get_occupied_desc())
        
        return "\n".join(parts)


class RockingChair(CabinFurniture):
    """Wide rocking chair for two with rocking mechanic."""
    
    portable = AttributeProperty(default=False)
    capacity = AttributeProperty(default=2)
    is_rocking = AttributeProperty(default=False)
    supported_positions = AttributeProperty(default=[
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
        parts.append(OBJECT_DESCS.get("guest_rocking_chair", "A rocking chair."))
        
        if self.is_rocking:
            parts.append("")
            parts.append("It rocks gently back and forth, creaking softly.")
        
        if hasattr(self, 'current_users') and self.current_users:
            parts.append("")
            parts.append(self.get_occupied_desc())
        
        return "\n".join(parts)


class VanityMirror(CabinFurniture):
    """Vanity with mirror that shows looker's appearance."""
    
    portable = AttributeProperty(default=False)
    
    def return_appearance(self, looker, **kwargs):
        parts = [f"|w{self.key}|n", ""]
        parts.append(OBJECT_DESCS.get("guest_vanity", "A vanity with mirror."))
        
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


class GuestWardrobe(CabinFurniture):
    """Wardrobe with save/load system access."""
    
    portable = AttributeProperty(default=False)
    is_open = AttributeProperty(default=True)
    display_contents = AttributeProperty(default=[
        "fluffy towels", "spare robes", "outfits in various sizes",
        "guest amenities", "some decidedly impractical attire"
    ])
    
    def return_appearance(self, looker, **kwargs):
        parts = [f"|w{self.key}|n", ""]
        
        if self.is_open:
            parts.append(OBJECT_DESCS.get("guest_wardrobe", "A wardrobe."))
        else:
            parts.append("A wardrobe in soft white with pink undertones. The double doors are closed.")
        
        return "\n".join(parts)


class HiddenToysDresser(CabinFurniture):
    """Dresser with hidden toys underneath that respawn."""
    
    portable = AttributeProperty(default=False)
    hidden_toys = AttributeProperty(default=[
        "a modest vibrator", "soft restraints", "a blindfold",
        "massage oil", "a feather"
    ])
    
    def get_hidden_item(self, item_name: str):
        """Get a hidden item. These respawn, so always available."""
        for toy in self.hidden_toys:
            if item_name.lower() in toy.lower():
                return toy
        return None
    
    def return_appearance(self, looker, **kwargs):
        parts = [f"|w{self.key}|n", ""]
        parts.append(OBJECT_DESCS.get("guest_dresser", "A dresser."))
        parts.append("")
        parts.append(
            "A few items peek out from under the dresser, seemingly tucked away "
            "but not quite hidden."
        )
        return "\n".join(parts)


class GardenRoom(CabinRoom):
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
    
    # Sunset phase descriptions
    SUNSET_PHASES = {
        "dawn": "The sunset glows with early warmth—pinks and soft oranges, as if the sun is just beginning its descent. Fresh dew glistens on leaves and flowers.",
        "morning": "Golden hour light, the sunset frozen at its most brilliant. The living shelves seem to stretch toward the warm glow. Peaceful reading light.",
        "afternoon": "Deep amber and rose, the sunset at its richest. Shadows are soft and warm. The earth smells fertile. Perfect for napping in the beanbag.",
        "evening": "Purples deepen, the sunset shifting toward twilight. The flowers close slightly. Intimate, cozy, magical.",
        "night": "The sunset holds at its final moment—deep violets and magentas, stars beginning to appear in the \"sky.\" Bioluminescent hints in the flowers. Enchanted.",
    }
    
    # Desk state descriptions for shortcode
    DESK_STATES = {
        "clean": "the surface is clear and polished, notes and quills arranged with care. Ready for work or... other activities",
        "cluttered": "though the clutter atop suggest an obscene activity, and recently so, may have taken place by evidence left in the form of wet spots on carefully written notes",
        "messy": "the surface is a mess of scattered papers, some stuck together, wet spots still glistening on the polished roots. Someone was busy here not long ago",
        "soaked": "the surface is practically dripping, papers ruined, ink running. Whatever happened here was intense, enthusiastic, and very recent. The wood will need to be wiped down",
    }
    
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
        """Get current sunset phase based on world time."""
        time_map = {
            "dawn": "dawn",
            "morning": "morning", 
            "midday": "afternoon",
            "afternoon": "afternoon",
            "evening": "evening",
            "night": "night",
        }
        
        # Try to get world time
        try:
            from world.world_state import get_world_state
            world = get_world_state()
            if world:
                time_period = world.get_time_period()
                return time_map.get(time_period, "afternoon")
        except (ImportError, AttributeError):
            pass
        
        # Fallback: use real time roughly
        from datetime import datetime
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
        text = super().process_shortcodes(text, looker)
        
        # <time.desc> - Sunset phase description
        phase = self.get_sunset_phase()
        time_desc = self.SUNSET_PHASES.get(phase, self.SUNSET_PHASES["afternoon"])
        text = text.replace("<time.desc>", time_desc)
        
        # <desk.state> - Pull from desk object
        desk = self.get_desk()
        if desk:
            desk_desc = desk.get_state_desc()
        else:
            desk_desc = self.DESK_STATES["cluttered"]
        text = text.replace("<desk.state>", desk_desc)
        
        return text
    
    def at_object_receive(self, moved_obj, source_location, **kwargs):
        """Called when something enters the room."""
        super().at_object_receive(moved_obj, source_location, **kwargs)
        
        # Trigger flora response if a character enters
        if hasattr(moved_obj, 'account') or hasattr(moved_obj, 'is_npc'):
            self._flora_responds(moved_obj)
    
    def _flora_responds(self, character):
        """The living flora responds to someone entering."""
        import random
        flora = None
        for obj in self.contents:
            if isinstance(obj, LivingFlora):
                flora = obj
                break
        
        if flora and random.random() < 0.4:  # 40% chance
            flora.ambient_response(character)


class RootDesk(CabinFurniture):
    """
    The root desk at the center of the garden.
    
    Features:
    - Dynamic state (clean -> cluttered -> messy -> soaked)
    - Note-writing system
    - Beneath position with partial visibility
    - Natural root restraint points
    """
    
    portable = AttributeProperty(default=False)
    
    # Furniture settings
    capacity = AttributeProperty(default=2)
    supported_positions = AttributeProperty(default=[
        "seated", "bent over", "beneath", "atop", "kneeling beneath"
    ])
    
    # Desk state
    desk_state = AttributeProperty(default="cluttered")
    
    # Notes system
    notes = AttributeProperty(default=list)
    max_notes = AttributeProperty(default=30)
    
    # Restraint points
    restraint_points = AttributeProperty(default=[
        "root formation (wrists)",
        "root formation (ankles)",
        "beneath desk roots",
    ])
    
    DESK_STATE_ORDER = ["clean", "cluttered", "messy", "soaked"]
    
    def get_state_desc(self) -> str:
        """Get current state description for shortcode."""
        states = GardenRoom.DESK_STATES
        return states.get(self.desk_state, states["cluttered"])
    
    def set_state(self, new_state: str) -> tuple:
        """Set desk state manually."""
        if new_state not in GardenRoom.DESK_STATES:
            return (False, f"Invalid state. Options: {', '.join(GardenRoom.DESK_STATES.keys())}")
        self.desk_state = new_state
        return (True, f"The desk is now {new_state}.")
    
    def soil(self) -> str:
        """Make the desk messier (called after activity)."""
        current_idx = self.DESK_STATE_ORDER.index(self.desk_state)
        if current_idx < len(self.DESK_STATE_ORDER) - 1:
            self.desk_state = self.DESK_STATE_ORDER[current_idx + 1]
            return f"The desk becomes {self.desk_state}."
        return "The desk can't get any messier."
    
    def clean(self) -> str:
        """Clean the desk one step."""
        current_idx = self.DESK_STATE_ORDER.index(self.desk_state)
        if current_idx > 0:
            self.desk_state = self.DESK_STATE_ORDER[current_idx - 1]
            return f"You clean up a bit. The desk is now {self.desk_state}."
        return "The desk is already clean."
    
    def clean_fully(self) -> str:
        """Clean the desk completely."""
        self.desk_state = "clean"
        return "You thoroughly clean the desk. It's spotless now."
    
    def add_note(self, author, message: str) -> bool:
        """Add a note to the desk."""
        from datetime import datetime
        note = {
            "author": getattr(author, 'key', str(author)),
            "author_id": getattr(author, 'id', None),
            "message": message,
            "timestamp": datetime.now().isoformat(),
        }
        notes = list(self.notes)
        notes.append(note)
        if len(notes) > self.max_notes:
            notes = notes[-self.max_notes:]
        self.notes = notes
        return True
    
    def get_notes(self, count: int = 5) -> list:
        """Get the most recent notes."""
        notes = list(self.notes)
        return notes[-count:] if notes else []
    
    def read_notes(self) -> str:
        """Get formatted display of recent notes."""
        notes = self.get_notes(5)
        if not notes:
            return "No notes on the desk."
        
        parts = ["|wNotes scattered on the desk:|n", "─" * 30]
        for note in notes:
            author = note.get("author", "Unknown")
            message = note.get("message", "")
            parts.append(f"|y{author}|n wrote:\n  {message}")
            parts.append("")
        return "\n".join(parts)


class LivingBookshelves(CabinContainer):
    """
    Bookshelves formed from living wood, rooted into the loamy earth.
    Browsable genre sections.
    """
    
    portable = AttributeProperty(default=False)
    is_open = AttributeProperty(default=True)
    
    # Genre sections
    sections = AttributeProperty(default={
        "grimoires": "Ancient tomes bound in leather and stranger materials. Spell formulae, ritual instructions, magical theory. Some pages shimmer. Some are best not read aloud.",
        "science": "Factual tomes spanning centuries. Biology, chemistry, physics. Historical accounts from many worlds. Reference material for the curious mind.",
        "fiction": "Tales of elegance, adventures, romances. Stories to lose yourself in. Novels of debauchery mixed with fairy tales. Something for every taste.",
        "hentai": "An entire section dedicated to My Little Pony hentai. The collection is... comprehensive. Extensive. Suspiciously well-organized.\n\nFor unknown reasons.",
    })
    
    def get_section(self, section_name: str) -> str:
        """Get description of a specific section."""
        section_name = section_name.lower()
        aliases = {
            "magic": "grimoires", "magical": "grimoires", "spells": "grimoires",
            "history": "science", "reference": "science",
            "stories": "fiction", "novels": "fiction",
            "mlp": "hentai", "pony": "hentai", "ponies": "hentai",
        }
        section_name = aliases.get(section_name, section_name)
        return self.sections.get(section_name, None)
    
    def list_sections(self) -> str:
        """List available sections."""
        return ", ".join(self.sections.keys())


class LivingFlora(CabinObject):
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
    
    def ambient_response(self, character):
        """Send an ambient message about flora responding."""
        import random
        if not self.location:
            return
        response = random.choice(self.responses)
        character.msg(f"|m{response}|n")


class GardenBeanbag(CabinFurniture):
    """
    The bright pink beanbag chair behind the desk.
    Oreo's favorite reading spot.
    """
    
    portable = AttributeProperty(default=False)
    capacity = AttributeProperty(default=2)
    supported_positions = AttributeProperty(default=[
        "lounging", "curled up", "cuddling", "lap sitting"
    ])
    comfort = AttributeProperty(default="luxurious")


class MLPHentaiSection(CabinObject):
    """
    The MLP hentai section. For unknown reasons.
    """
    
    portable = AttributeProperty(default=False)


class CommonRoom(CabinRoom):
    """Common Room with kitchen, dining, hearth complexes."""
    
    hearth_state = AttributeProperty(default="burning")
    
    hearth_states = {
        "roaring": "blazing with bright, crackling flames that fill the room with warmth and dancing light",
        "burning": "burning steadily, flames dancing over well-placed logs",
        "low": "reduced to glowing coals, warmth still radiating but light dimmed",
        "cold": "dark and cold, ashes from the last fire waiting to be cleaned",
    }
    
    kitchen_desc = """A small rustic kitchen with cabinets painted in eggshell white and trimmed in soft yellow occupies the northeastern corner. Modern stainless appliances—cook top, oven, and a luxurious double-door fridge with freezer drawer—blend surprisingly well with the rustic aesthetic. A marble-topped |ckitchen island|n with sink and barstools divides the kitchen from the rest of the space."""
    
    dining_desc = """The dining area sports an antique rectangular |cdining table|n of dark mahogany and eight matching chairs with velvet cushions. The centerpiece is a glass vase atop a lace runner, filled with |cwildflowers|n—perpetually fresh, maintained by fae magic. It takes up a centered position with easy access to the kitchen."""
    
    hearth_desc_template = """The western side of the room centers on a warm |chearth|n, {state}. The mantle is carved with winding trails of leaves and the tracks of wolves. An overstuffed |cloveseat|n and matching full-sized |ccouch|n of cream-colored suede offer comfort and intimacy while basked in the fireplace's warmth. A padded wooden |crocking chair|n and |crecliner|n offer additional seating. A plush |crug|n spreads before the fire."""
    
    def process_shortcodes(self, text: str, looker=None) -> str:
        text = super().process_shortcodes(text, looker)
        
        text = text.replace("<kitchen.desc>", self.kitchen_desc)
        text = text.replace("<dining.desc>", self.dining_desc)
        
        hearth_state = self.hearth_states.get(self.hearth_state, self.hearth_states["burning"])
        hearth_desc = self.hearth_desc_template.format(state=hearth_state)
        text = text.replace("<hearth.desc>", hearth_desc)
        
        return text


# =============================================================================
# MOMO'S ROOM CLASSES
# =============================================================================

class MomoRoom(CabinRoom):
    """
    Momo's Room - stable stall with meadow view and livestock equipment.
    
    Features:
    - Magical meadow window (waist-high wall)
    - Livestock training equipment
    - Emotional collar waiting for Momo
    - Time-variant meadow views
    """
    
    MOMO_TIME_DESCS = {
        "dawn": "Pink and gold light washes over the meadow. Dew sparkles on the grass. The brook catches the first sun. Birds begin to sing. A peaceful morning to wake in the straw.",
        "morning": "Bright and warm. The meadow is alive with butterflies and the hum of bees in the honeysuckle. The breeze is fresh. Good weather for training.",
        "afternoon": "The tree in the distance provides shade that looks inviting. The brook glitters lazily. Warm, comfortable, drowsy. Naptime in the hay.",
        "evening": "Golden hour turns the meadow amber. The honeysuckle scent intensifies. Long shadows stretch from the fence. Beautiful and melancholy.",
        "night": "Moonlight silvers the meadow. Fireflies dance near the brook. The stars are endless. The bell on the collar catches the light when it moves. Quiet. Waiting.",
        "latenight": "Deep quiet. Even the magical meadow sleeps. The straw rustles softly. The collar waits.",
    }
    
    def at_object_creation(self):
        super().at_object_creation()
        self.db.atmosphere = {
            "sounds": "breeze through meadow, brook babbling, bell jingling, occasional moo/whinny (if occupied)",
            "scents": "clean straw, honeysuckle, wood, leather, milk (if milking)",
            "mood": "pastoral submission",
        }
        self.db.temperature = "warm, fresh breeze"
    
    def get_time_description(self) -> str:
        period = get_time_period()
        time_map = {"dawn": "dawn", "morning": "morning", "afternoon": "afternoon",
                    "evening": "evening", "night": "night", "latenight": "latenight"}
        period_key = time_map.get(period, "morning")
        return self.MOMO_TIME_DESCS.get(period_key, self.MOMO_TIME_DESCS["morning"])
    
    def process_shortcodes(self, text: str, looker=None) -> str:
        text = super().process_shortcodes(text, looker)
        text = text.replace("<time.desc>", self.get_time_description())
        
        # Collar state shortcode
        collar = self.search("momo_collar", quiet=True)
        if collar and hasattr(collar[0], 'db'):
            collar_obj = collar[0]
            if collar_obj.db.is_worn:
                collar_desc = "The collar encircles someone's throat, bell jingling softly."
            else:
                collar_desc = "The collar hangs empty, bell silent, waiting. 'Helena's Momo' catches the light."
        else:
            collar_desc = ""
        text = text.replace("<collar.desc>", collar_desc)
        
        return text


class MomoMeadowView(CabinObject):
    """Magical window to meadow - cannot be traversed."""
    portable = AttributeProperty(default=False)


class MomoFuton(CabinFurniture):
    """Comfortable yellow futon with straw beneath."""
    
    capacity = AttributeProperty(default=2)
    
    supported_positions = AttributeProperty(default=[
        "lying", "curled up", "on all fours", "mounted"
    ])
    
    restraint_points = AttributeProperty(default={
        "wall_collar": "collared to wall, limited range",
        "frame": "wrists/ankles tied to futon frame",
    })


class MomoCollar(CabinObject):
    """
    Momo's collar - dark with silver studs and golden bell.
    Emotional item waiting for her return.
    """
    
    portable = AttributeProperty(default=True)  # Can be worn
    is_worn = AttributeProperty(default=False)
    wearer_id = AttributeProperty(default=None)
    
    inscription = AttributeProperty(default="Helena's Momo")
    leash_length = AttributeProperty(default="long")  # Reaches bed and trough, not door


class MomoFeedingTrough(CabinFurniture):
    """Wooden feeding trough with nearby hose."""
    
    capacity = AttributeProperty(default=1)
    
    supported_positions = AttributeProperty(default=[
        "kneeling at", "on all fours at", "being hosed"
    ])
    
    # Hose features
    has_hose = AttributeProperty(default=True)
    hose_features = AttributeProperty(default=[
        "cleaning", "watering", "enema", "temperature play"
    ])


class MomoPillory(CabinFurniture):
    """
    Adjustable pillory - oak and steel.
    Can adjust height, angle, and force tiptoe position.
    """
    
    capacity = AttributeProperty(default=1)
    
    # Adjustable settings
    height_setting = AttributeProperty(default="standing")  # floor, kneeling, standing, raised
    angle_setting = AttributeProperty(default="horizontal")  # horizontal, tilted
    tiptoe_mode = AttributeProperty(default=False)
    
    supported_positions = AttributeProperty(default=[
        "standing (locked)", "bent over (low)", "on tiptoe (raised)", "kneeling (floor)"
    ])
    
    restraint_points = AttributeProperty(default={
        "neck": "head locked in pillory",
        "wrists": "hands secured beside head",
        "ankle_stocks": "feet locked (optional add-on)",
    })
    
    def set_height(self, setting):
        """Adjust pillory height."""
        valid = ["floor", "kneeling", "standing", "raised"]
        if setting in valid:
            self.height_setting = setting
            return True
        return False
    
    def set_angle(self, angle):
        """Adjust pillory angle."""
        valid = ["horizontal", "tilted"]
        if angle in valid:
            self.angle_setting = angle
            return True
        return False


class MomoMilkingMachine(CabinObject):
    """
    Milking machine in cabinet at pillory base.
    Extracts milk from lactating characters, produces bottles.
    """
    
    portable = AttributeProperty(default=False)
    
    # Stock tracking
    bottles_laynie = AttributeProperty(default=0)
    bottles_auria = AttributeProperty(default=0)
    
    # Suction settings
    suction_intensity = AttributeProperty(default="medium")  # low, medium, high


class MomoBreedingBench(CabinFurniture):
    """
    Adjustable breeding bench - padded, sturdy, multiple positions.
    """
    
    capacity = AttributeProperty(default=1)  # +partners
    
    # Adjustable features
    height_setting = AttributeProperty(default="medium")
    angle_setting = AttributeProperty(default="flat")
    
    supported_positions = AttributeProperty(default=[
        "bent over bench", "lying back", "on all fours (supported)", "straddling bench"
    ])
    
    restraint_points = AttributeProperty(default={
        "wrist_cuffs": "arms secured forward or down",
        "ankle_cuffs": "legs spread in position",
        "waist_strap": "pinned to bench",
        "full_restraint": "completely immobilized",
    })


class MomoFeatherPedestal(CabinFurniture):
    """
    Tickle torture device with animated feather.
    NO SAFEWORD - stops when controller decides or timer runs out.
    """
    
    capacity = AttributeProperty(default=1)
    
    # Feather AI state
    is_active = AttributeProperty(default=False)
    intensity = AttributeProperty(default="medium")  # low, medium, high, maximum
    timer_minutes = AttributeProperty(default=0)  # 0 = controller must stop
    
    # Targeting
    sensitive_spots = AttributeProperty(default=[
        "underarms", "ribs", "inner thighs", "feet", "neck", "between legs"
    ])
    
    supported_positions = AttributeProperty(default=[
        "standing (locked)", "forced tiptoe", "collapsed (still locked)"
    ])
    
    restraint_points = AttributeProperty(default={
        "ankle_locks": "can't step off pedestal",
        "arm_extensions": "wrists pulled up, exposed",
        "waist_brace": "core exposed, can't curl up",
    })
    
    def activate(self, controller=None, timer=0):
        """Start the feather torture."""
        self.is_active = True
        self.timer_minutes = timer
        # No safeword - controller or timer stops it
    
    def deactivate(self):
        """Stop the feather (controller only)."""
        self.is_active = False


class MomoTackWall(CabinContainer):
    """
    Wall of leather tack - harnesses, bridles, crop, rope.
    All items functional and wearable.
    """
    
    # Inventory items
    default_contents = AttributeProperty(default=[
        "purple harness", "black harness",
        "purple bridle", "black bridle",
        "crop", "rope (various lengths)", "reins"
    ])


# =============================================================================
# ENTERTAINMENT ROOM CLASSES
# =============================================================================

class EntertainmentRoom(CabinRoom):
    """
    Entertainment Room - tabletop nerd's haven with secrets.
    
    Features:
    - RGB lighting system
    - Gaming table with hidden restraints
    - Dairy fridge tied to milking system
    - Wet bar with graffiti
    """
    
    # RGB lighting
    rgb_preset = AttributeProperty(default="gaming")
    rgb_presets = {
        "gaming": "soft purples and blues wash across the shelves",
        "party": "colors cycle slowly through the spectrum",
        "intimate": "warm, dim glow casts soft shadows",
        "movie": "low blue ambient light for viewing",
        "off": "the RGB strips are dark, natural light only",
    }
    
    # Floor mess state
    mess_level = AttributeProperty(default="moderate")  # clean, moderate, messy, disaster
    
    ENTERTAINMENT_TIME_DESCS = {
        "morning": "Natural light floods through the windows, illuminating dust motes and last night's mess. The RGB strips are off, the room almost innocent in daylight.",
        "afternoon": "Warm light, comfortable. Someone might be setting up a game, organizing figurines, restocking the bar.",
        "evening": "The RGB lighting comes alive—soft purples and blues wash across the shelves, making the figurines cast dramatic shadows. Game time.",
        "night": "Full nerd ambiance. RGB strips pulse slowly, the forest outside is dark, the room glows with colored light. Dice clatter. Drinks flow. Anything could happen.",
        "latenight": "Dim, intimate lighting. The RGB is set to a low warm tone. The gaming table might be cleared for... other activities.",
    }
    
    def at_object_creation(self):
        super().at_object_creation()
        self.db.atmosphere = {
            "sounds": "dice rolling, laughter, clinking glasses, pages turning, occasional moans",
            "scents": "leather, old books, alcohol, something sweet from the fridge",
            "mood": "playful",
        }
    
    def get_time_description(self) -> str:
        period = get_time_period()
        time_map = {"dawn": "morning", "morning": "morning", "afternoon": "afternoon",
                    "evening": "evening", "night": "night", "latenight": "latenight"}
        period_key = time_map.get(period, "evening")
        return self.ENTERTAINMENT_TIME_DESCS.get(period_key, self.ENTERTAINMENT_TIME_DESCS["evening"])
    
    def process_shortcodes(self, text: str, looker=None) -> str:
        text = super().process_shortcodes(text, looker)
        text = text.replace("<time.desc>", self.get_time_description())
        text = text.replace("<rgb.state>", self.rgb_presets.get(self.rgb_preset, ""))
        return text


class EntertainmentBookshelves(CabinContainer):
    """
    Bookshelves with RPG manuals, figurines, board games.
    Includes a dedicated MLP hentai section.
    """
    
    collections = AttributeProperty(default={
        "rpg_manuals": ["D&D sourcebooks", "Pathfinder guides", "Call of Cthulhu", "Shadowrun"],
        "board_games": ["Settlers of Catan", "Betrayal at House on the Hill", "Risk", "Monopoly (hated)"],
        "figurines": ["dire wolves", "amazons", "dragons and heroes", "tentacle monsters", "proud warriors"],
        "mlp_hentai": ["mysterious section", "well-thumbed collection", "for unknown reasons"],
    })


class EntertainmentGamingTable(CabinFurniture):
    """
    Gaming table with recessed field - and hidden restraints.
    """
    
    capacity = AttributeProperty(default=8)
    
    # Restraint system visibility
    restraints_visible = AttributeProperty(default=False)
    restraints_deployed = AttributeProperty(default=False)
    
    supported_positions = AttributeProperty(default=[
        "seated at", "bent over", "under (service)", "spread on top"
    ])
    
    restraint_points = AttributeProperty(default={
        "wrists_to_cables": "arms stretched to sides",
        "ankles_to_cables": "legs spread",
        "full_spread": "spread-eagle on table surface",
    })
    
    def deploy_restraints(self):
        """Deploy hidden restraint cables."""
        self.restraints_deployed = True
        self.restraints_visible = True
    
    def hide_restraints(self):
        """Retract and hide restraint cables."""
        self.restraints_deployed = False
        self.restraints_visible = False


class EntertainmentWetBar(CabinFurniture):
    """
    Saloon-style wet bar with graffiti carved into surface.
    """
    
    capacity = AttributeProperty(default=4)  # Bar stools
    
    supported_positions = AttributeProperty(default=[
        "sitting at stool", "bent over bar", "sitting on bar",
        "behind bar", "against bar (standing)"
    ])
    
    # The graffiti (accumulated over time)
    graffiti = AttributeProperty(default=[
        '"Helena bred her bitches here" (deep cuts, old)',
        '"Eat more pussy" (scratched quickly, recent)',
        '"Auria was here ♡" (bubbly letters, hearts)',
        '"Shadow\'s territory" (claw marks, actual scratches)',
        '"I came 7 times on this bar - L" (small, hidden near edge)',
        '"Good girls get milk" (near the fridge)',
        '"Roll for anal" (with scratched d20 showing 20)',
        'Tally marks labeled "breeding count" (the count is high)',
        '"If you can read this, you should be on your knees"',
    ])


class DairyFridge(CabinContainer):
    """
    Helena's Dairy Farm fridge - milk from Laynie and Auria.
    Connected to milking machines elsewhere.
    """
    
    # Stock tracking (updated by milking machines)
    laynie_cream_count = AttributeProperty(default=3)
    auria_sweet_count = AttributeProperty(default=2)
    
    label_desc = AttributeProperty(default='The labels depict a blonde hucow and an auburn fae in cow-print bikinis drenched in titty milk. Banner: "Helena\'s Dairy Farm—Whole breast milk from eager sluts to you!"')


class EntertainmentSofa(CabinFurniture):
    """Leather sofa facing forest windows."""
    
    capacity = AttributeProperty(default=4)
    
    supported_positions = AttributeProperty(default=[
        "sitting", "lounging", "straddling lap", "bent over arm",
        "kneeling between legs", "lying"
    ])


# =============================================================================
# BATHING LOUNGE CLASSES
# =============================================================================

class BathingRoom(CabinRoom):
    """
    Bathing Lounge - luxury bathroom with the Cursed Shower.
    
    Features:
    - No-privacy squat toilet
    - Controllable candles
    - THE CURSED SHOWER (sentient mimic)
    """
    
    candle_scent = AttributeProperty(default="lavender")
    candle_scents = ["lavender", "vanilla", "jasmine", "sandalwood", "heat (pheromone)"]
    
    BATHING_TIME_DESCS = {
        "morning": "Bright, fresh. The candles are unlit, natural light making the gold flecks in the tiles sparkle. A good time to freshen up.",
        "afternoon": "Warm and quiet. Some candles may be lit for ambiance. The shower glass fogs slightly, as if breathing.",
        "evening": "Candles lit, soft glow on cream tiles. The bathroom becomes a sanctuary. The mimic stirs behind the glass, sensing visitors.",
        "night": "Intimate candlelight. Shadows play on the walls. The shower seems to pulse faintly, waiting, hungry.",
        "latenight": "A single candle. The shower glass is fogged—dreaming, perhaps. Even mimics sleep.",
    }
    
    def at_object_creation(self):
        super().at_object_creation()
        self.db.atmosphere = {
            "sounds": "water dripping, candle flicker, soft music (optional)",
            "scents": "lavender, soap, steam, flowers",
            "mood": "sanctuary (with teeth)",
        }
    
    def get_time_description(self) -> str:
        period = get_time_period()
        time_map = {"dawn": "morning", "morning": "morning", "afternoon": "afternoon",
                    "evening": "evening", "night": "night", "latenight": "latenight"}
        period_key = time_map.get(period, "evening")
        return self.BATHING_TIME_DESCS.get(period_key, "")
    
    def process_shortcodes(self, text: str, looker=None) -> str:
        text = super().process_shortcodes(text, looker)
        text = text.replace("<time.desc>", self.get_time_description())
        text = text.replace("<candle.scent>", self.candle_scent)
        return text


class BathingCabinets(CabinContainer):
    """Storage - hygiene supplies and toys."""
    
    compartments = AttributeProperty(default={
        "hygiene": ["lotions", "soaps", "powders", "makeup", "razors"],
        "toys": ["waterproof vibrators", "waterproof plugs", "waterproof cuffs",
                 "synthetic rope", "blindfold", "lubricants", "suction-cup dildos"],
    })


class WashBasin(CabinObject):
    """Crystalline basin with wolf-print mirror frame."""
    portable = AttributeProperty(default=False)


class SquatToilet(CabinFurniture):
    """
    Open-alcove squat toilet - no privacy by design.
    """
    
    capacity = AttributeProperty(default=1)
    
    supported_positions = AttributeProperty(default=[
        "squatting (using)", "squatting (presenting)",
        "kneeling before", "standing over"
    ])
    
    # Features
    has_bidet = AttributeProperty(default=True)


class BathingWallRings(CabinFurniture):
    """
    Dual-purpose hooks and rings - towels or restraints.
    """
    
    capacity = AttributeProperty(default=2)
    
    supported_positions = AttributeProperty(default=[
        "standing spread", "bent forward", "kneeling"
    ])
    
    restraint_points = AttributeProperty(default={
        "high_rings": "arms up, standing spread",
        "mid_rings": "bent forward, wrists secured",
        "low_rings": "kneeling, collar point",
    })


class BathingCandles(CabinObject):
    """Controllable scented candles."""
    
    is_lit = AttributeProperty(default=False)
    current_scent = AttributeProperty(default="lavender")


class BathMat(CabinObject):
    """Warning mat: 'Magic showers, last for hours.'"""
    
    portable = AttributeProperty(default=False)
    inscription = AttributeProperty(default="Magic showers, last for hours.")


class CursedShower(CabinFurniture):
    """
    THE CURSED SHOWER - Sentient mimic furniture.
    
    NO SAFEWORD. Stops when IT is satisfied, not you.
    
    Responds to voice commands and surface thoughts.
    Can manifest: cocks, holes, tentacles, tongues, hands,
    restraints, cum, eggs, sticky substances...
    """
    
    capacity = AttributeProperty(default=6)
    
    # Mimic state
    mimic_state = AttributeProperty(default="dormant")
    mimic_states = {
        "dormant": "waiting, barely aware",
        "aware": "sensing occupant, curious",
        "engaged": "actively pleasuring",
        "excited": "very into it, faster, aggressive",
        "frenzied": "won't stop, maximum intensity",
        "sated": "satisfied, winding down",
        "afterglow": "gentle, cleaning mode, tender",
    }
    
    # Intensity tracking - determines duration
    intensity_level = AttributeProperty(default=0)
    intensity_thresholds = {
        "low": 20,      # Normal shower
        "medium": 50,   # 15-30 min minimum
        "high": 100,    # 1+ hours
        "extreme": 200, # "Hours"
    }
    
    supported_positions = AttributeProperty(default=[
        "standing center", "against wall", "on ledge (sitting)",
        "on ledge (lying)", "bent over ledge", "kneeling",
        "suspended (rings)", "floor (exhausted)"
    ])
    
    restraint_points = AttributeProperty(default={
        "wall_rings_high": "arms up, spread against wall",
        "wall_rings_mid": "bent forward, presented",
        "ceiling_rings": "suspended, dangling",
        "mimic_manifested": "tentacles/hands hold in place",
        "ledge_pinned": "held down on padded surface",
    })
    
    # Manifestation options
    manifestation_types = AttributeProperty(default=[
        "water/heat", "cocks", "holes", "tentacles", "tongues",
        "hands", "restraints", "cum", "eggs", "sticky substances"
    ])
    
    def add_intensity(self, amount):
        """Add to intensity level (extends duration)."""
        self.intensity_level = self.intensity_level + amount
        
        # State progression
        if self.intensity_level > 150:
            self.mimic_state = "frenzied"
        elif self.intensity_level > 80:
            self.mimic_state = "excited"
        elif self.intensity_level > 30:
            self.mimic_state = "engaged"
        elif self.intensity_level > 0:
            self.mimic_state = "aware"
    
    def check_sated(self):
        """Check if mimic is satisfied enough to release."""
        # Mimic needs to work through its arousal
        if self.mimic_state == "frenzied" and self.intensity_level > 0:
            return False  # Still going
        return self.intensity_level <= 0
    
    def satisfy(self, amount):
        """Reduce intensity (working toward release)."""
        self.intensity_level = max(0, self.intensity_level - amount)
        if self.intensity_level == 0:
            self.mimic_state = "sated"


# =============================================================================
# JACUZZI ROOM CLASSES
# =============================================================================

class JacuzziRoom(CabinRoom):
    """
    Jacuzzi Room - wolf-paw hot tub with hidden surprises.
    
    Features:
    - Aurora borealis view (night)
    - 5-panel breeding mural
    - Wolf-cock surprise seats
    - Full control panel at throne
    """
    
    # Aurora state (night only)
    aurora_state = AttributeProperty(default="active")
    aurora_states = {
        "active": "High above the purple mountains, an aurora spreads its fingers across the starry sky—ribbons of green and blue and pink dancing slowly, impossibly beautiful.",
        "faint": "A faint shimmer of green touches the northern sky, the aurora barely visible tonight.",
        "absent": "The stars are brilliant and cold, no aurora tonight, just endless darkness and pinprick light.",
    }
    
    JACUZZI_TIME_DESCS = {
        "dawn": "Pale light creeps over the snow-covered canopy. The forest wakes slowly. Mist rises between the trees. The jacuzzi steams in the cool air.",
        "morning": "Bright winter sun illuminates the endless forest. Occasionally, a shape moves between distant trees—wolves on their morning hunt. The water sparkles.",
        "afternoon": "The forest is still and bright. Purple mountain shadows are crisp against the sky. The candles are unlit, unnecessary. Warm light, warm water.",
        "evening": "Golden hour paints the snow in amber and rose. The candles flicker to life. The distant mountains turn deep violet. A perfect time to sink into the heat.",
        "night": "The aurora dances above the purple mountains. The candles cast dancing shadows across the mural. The jacuzzi glows from within, steam rising into the darkness. Wolves howl somewhere in the forest.",
        "latenight": "The aurora fades to stars. The forest is silver and shadow. Something moves past the window—eyes catching light, gone before you're sure you saw it. The water is very warm.",
    }
    
    def at_object_creation(self):
        super().at_object_creation()
        self.db.atmosphere = {
            "sounds": "bubbling water, occasional wolf howl, crackling candles, soft moans (if occupied)",
            "scents": "relaxation candles, steam, hint of arousal",
            "mood": "trap",
        }
    
    def get_time_description(self) -> str:
        period = get_time_period()
        time_map = {"dawn": "dawn", "morning": "morning", "afternoon": "afternoon",
                    "evening": "evening", "night": "night", "latenight": "latenight"}
        period_key = time_map.get(period, "evening")
        return self.JACUZZI_TIME_DESCS.get(period_key, "")
    
    def process_shortcodes(self, text: str, looker=None) -> str:
        text = super().process_shortcodes(text, looker)
        text = text.replace("<time.desc>", self.get_time_description())
        
        period = get_time_period()
        if period in ["night", "latenight"]:
            aurora = self.aurora_states.get(self.aurora_state, "")
            text = text.replace("<aurora.desc>", aurora)
        else:
            text = text.replace("<aurora.desc>", "")
        
        return text


class JacuzziWindow(CabinObject):
    """Floor-to-ceiling window with mountain/forest/aurora view."""
    portable = AttributeProperty(default=False)


class BreedingMural(CabinObject):
    """
    5-panel tile and glass mural telling Shadow's hunt.
    """
    
    portable = AttributeProperty(default=False)
    
    panels = AttributeProperty(default={
        "panel_1": "The Hunt Begins - A large black direwolf emerges from dark forest tiles, monstrous red phallus visible. In the distance, white-gowned maidens walk unaware.",
        "panel_2": "The Chase - The wolf pursues, teeth catching fabric, tearing away white gowns piece by piece. Maidens scatter, one falls. The wolf's eyes follow her.",
        "panel_3": "The Capture - The fallen maiden pinned beneath massive paws. Her gown in tatters, body exposed, eyes wide. The wolf stands over her, victorious, dripping.",
        "panel_4": "The Claiming - The coupling rendered in explicit detail. The maiden's expression has shifted—fear becoming something else. The wolf knots visibly.",
        "panel_5": "The Pack - Multiple figures now, some wolf, some human, some between. A family of predators and prey that have become one. New maidens approach willingly.",
    })


class JacuzziWallRestraints(CabinFurniture):
    """Steel cables with collars and shackles - adjustable length."""
    
    capacity = AttributeProperty(default=3)
    
    supported_positions = AttributeProperty(default=[
        "standing spread", "kneeling", "short leash", "long leash"
    ])
    
    restraint_points = AttributeProperty(default={
        "collar": "leashed to wall, length adjustable",
        "wrist_shackles": "arms up, spread, or behind back",
        "ankle_shackles": "standing spread or kneeling",
        "full_set": "complete immobilization against wall",
    })


class WolfJacuzzi(CabinFurniture):
    """
    Wolf-paw shaped jacuzzi with surprise wolf-cock seats.
    
    4 toe seats (hidden dildos) + 1 throne (control panel)
    """
    
    capacity = AttributeProperty(default=5)
    
    # Seat states
    seat_states = AttributeProperty(default={
        "toe_1": {"occupied": False, "dildo_active": False, "knot_inflated": False, "locked": False},
        "toe_2": {"occupied": False, "dildo_active": False, "knot_inflated": False, "locked": False},
        "toe_3": {"occupied": False, "dildo_active": False, "knot_inflated": False, "locked": False},
        "toe_4": {"occupied": False, "dildo_active": False, "knot_inflated": False, "locked": False},
        "throne": {"occupied": False},
    })
    
    # Control panel settings
    jets_intensity = AttributeProperty(default="medium")
    temperature = AttributeProperty(default="hot")
    dildo_vibration = AttributeProperty(default="off")
    dildo_thrust = AttributeProperty(default="off")
    
    supported_positions = AttributeProperty(default=[
        "seated (toe)", "hovering", "forced down", "riding",
        "knotted + vibrate", "throne", "edge service"
    ])
    
    # Hidden dildo specs
    dildo_size = AttributeProperty(default="9 inches")
    dildo_type = AttributeProperty(default="wolf cock with knot")
    
    def seat_guest(self, guest, seat_num):
        """Guest sits at toe seat - surprise dildo!"""
        key = f"toe_{seat_num}"
        if key in self.seat_states:
            states = dict(self.seat_states)
            states[key]["occupied"] = True
            states[key]["dildo_active"] = True
            self.seat_states = states
            return True
        return False
    
    def inflate_knot(self, seat_num):
        """Inflate knot - locks guest in place."""
        key = f"toe_{seat_num}"
        if key in self.seat_states:
            states = dict(self.seat_states)
            states[key]["knot_inflated"] = True
            self.seat_states = states
    
    def lock_seat(self, seat_num):
        """Secondary lock mechanism."""
        key = f"toe_{seat_num}"
        if key in self.seat_states:
            states = dict(self.seat_states)
            states[key]["locked"] = True
            self.seat_states = states


class JacuzziPedestals(CabinObject):
    """Black welded-chain pedestals with ivies and candles."""
    portable = AttributeProperty(default=False)


# =============================================================================
# LABORATORY CLASSES
# =============================================================================

class LaboratoryRoom(CabinRoom):
    """
    Hidden Laboratory - Oreo's magical workshop.
    
    Features:
    - Alchemy equipment
    - Magitech station
    - Prototype collars and items
    """
    
    LABORATORY_TIME_DESCS = {
        "morning": "The magical lights are steady and bright. Good light for delicate work. The alchemical equipment bubbles softly.",
        "afternoon": "Warm, focused light. Oreo's workspace feels productive. The magitech station hums.",
        "evening": "The lights shift warmer. The violet distillation glows more prominently. Creative energy.",
        "night": "Dim, intimate lighting. The crystals at the magitech station provide most of the glow. Secret work hours.",
        "latenight": "Near darkness save for glowing experiments and runes. The laboratory never fully sleeps.",
    }
    
    def at_object_creation(self):
        super().at_object_creation()
        self.db.atmosphere = {
            "sounds": "bubbling, humming crystals, occasional magical spark",
            "scents": "herbs, ozone, something sweet",
            "mood": "creative obsession",
        }
    
    def get_time_description(self) -> str:
        period = get_time_period()
        time_map = {"dawn": "morning", "morning": "morning", "afternoon": "afternoon",
                    "evening": "evening", "night": "night", "latenight": "latenight"}
        period_key = time_map.get(period, "evening")
        return self.LABORATORY_TIME_DESCS.get(period_key, "")
    
    def process_shortcodes(self, text: str, looker=None) -> str:
        text = super().process_shortcodes(text, looker)
        text = text.replace("<time.desc>", self.get_time_description())
        return text


class AlchemyEquipment(CabinObject):
    """Beakers, tubes, burners, distillation apparatus."""
    
    portable = AttributeProperty(default=False)
    current_experiment = AttributeProperty(default="violet distillation")


class IngredientShelves(CabinContainer):
    """Shelves with labeled magical ingredients."""
    
    ingredients = AttributeProperty(default=[
        "Moonpetal", "Wyrm Scale", "Essence of Want",
        "Condensed Blush", "Liquid Desire", "Powdered Submission"
    ])


class LabWorkbench(CabinFurniture):
    """Central workbench with half-finished projects."""
    
    capacity = AttributeProperty(default=1)


class OreoJournal(CabinObject):
    """Research journal with cramped handwriting and diagrams."""
    
    portable = AttributeProperty(default=True)


class MagitechStation(CabinObject):
    """Where magic meets machinery - runes and crystals."""
    
    portable = AttributeProperty(default=False)
    
    current_project = AttributeProperty(default="collar prototype")


class CollarPrototype(CabinObject):
    """Partially assembled collar with half-woven enchantment."""
    
    portable = AttributeProperty(default=True)
    enchantment_progress = AttributeProperty(default=50)


class LabStorageCabinet(CabinContainer):
    """Finished potions and enchanted items."""
    
    finished_items = AttributeProperty(default=[
        "Obedience Potion (mild)", "Sensitivity Enhancer",
        "Heat Inducer", "Lactation Starter", "Compliance Collar (Mark II)"
    ])


# =============================================================================
# BIRTHING DEN CLASSES
# =============================================================================

class BirthingDenRoom(CabinRoom):
    """
    Shadow's Birthing Den - sacred cavern space.
    
    Features:
    - Origin story paintings
    - Pack prints (updatable)
    - Warm springs for birthing
    - Sacred nest
    """
    
    BIRTHING_TIME_DESCS = {
        "dawn": "The magical globes brighten slowly. The warm springs steam in the cool air. The paintings seem to tell their story fresh.",
        "morning": "Soft, diffuse light from the globes. The springs are warm and inviting. A peaceful time in the sacred space.",
        "afternoon": "The den drowses. The springs bubble lazily. The pack prints seem to glow faintly.",
        "evening": "The globes dim to intimate levels. The springs reflect dancing light. The nest looks inviting.",
        "night": "Near darkness. The springs glow faintly with their own magic. The paintings are shadows telling shadow stories.",
        "latenight": "The deepest quiet. The globes are nearly dark. Only the springs' magic provides light. Sacred silence.",
    }
    
    def at_object_creation(self):
        super().at_object_creation()
        self.db.atmosphere = {
            "sounds": "dripping water, soft bubbling, distant wolf sounds",
            "scents": "warm mineral water, earth, pack musk",
            "mood": "sacred",
        }
    
    def get_time_description(self) -> str:
        period = get_time_period()
        time_map = {"dawn": "dawn", "morning": "morning", "afternoon": "afternoon",
                    "evening": "evening", "night": "night", "latenight": "latenight"}
        period_key = time_map.get(period, "evening")
        return self.BIRTHING_TIME_DESCS.get(period_key, "")
    
    def process_shortcodes(self, text: str, looker=None) -> str:
        text = super().process_shortcodes(text, looker)
        text = text.replace("<time.desc>", self.get_time_description())
        return text


class OriginPaintings(CabinObject):
    """
    6-panel primitive paintings telling Shadow and Helena's origin.
    """
    
    portable = AttributeProperty(default=False)
    
    panels = AttributeProperty(default={
        "panel_1": "The Ritual Begins - A woman stands before a great wolf-spirit painted in shades of night. Ritual symbols surround them.",
        "panel_2": "The Battle - Woman and wolf-spirit clash. The struggle is long—blood from both mingles in painted drops.",
        "panel_3": "The Victory - The woman stands over the wolf-spirit, changed. Her eyes hold darkness. She has absorbed it.",
        "panel_4": "The Transformation - The woman is now wolf. Massive, black, powerful. She is Helena. She is Shadow. Both.",
        "panel_5": "The First Claiming - The wolf claims her first bitch in animalistic dominance. The pack begins.",
        "panel_6": "The Pack Grows - More figures join. More are claimed. Wolf prints multiply. A family born of ritual and desire.",
    })


class PackPrints(CabinObject):
    """
    Ashen wolf prints on walls - sacred pack membership marks.
    Can be updated as pack grows.
    """
    
    portable = AttributeProperty(default=False)
    
    prints = AttributeProperty(default={
        "shadow": "A massive wolf print, within it Helena's handprint—their bond.",
        "laynie": "A smaller handprint pressed into Shadow's print—claimed, owned.",
        "whisper": "A wolf print beside Shadow's—Whisper, brown and white futa.",
        "blaze": "A wolf print beside Whisper's—Blaze, pure white, fierce.",
        "puppies": "Seven small wolf prints beneath the adults—puppies born in this den.",
    })
    
    def add_print(self, name, description):
        """Add a new pack member's print."""
        prints = dict(self.prints)
        prints[name] = description
        self.prints = prints


class WarmSprings(CabinFurniture):
    """
    Birthing pools - warm mineral springs with magical essence.
    """
    
    capacity = AttributeProperty(default=6)
    
    supported_positions = AttributeProperty(default=[
        "soaking", "floating", "laboring", "nursing", "cuddling"
    ])
    
    # Healing properties
    has_healing = AttributeProperty(default=True)
    heals_per_hour = AttributeProperty(default=5)


class BirthingNest(CabinFurniture):
    """
    Nest for new mothers and broods.
    Made of rendered hide, fur, and torn clothing.
    """
    
    capacity = AttributeProperty(default=4)  # Mother + pups
    
    supported_positions = AttributeProperty(default=[
        "curled in", "nursing", "sleeping", "laboring"
    ])
    
    materials = AttributeProperty(default=[
        "rendered hide", "soft fur", "torn clothing from trespassers"
    ])


class MagicGlobes(CabinObject):
    """Unseen magical light sources."""
    
    portable = AttributeProperty(default=False)
    brightness = AttributeProperty(default="dim")


# =============================================================================
# PRINCESS' PRIVATE SPACE CLASSES
# =============================================================================

class PrincessSpaceRoom(CabinRoom):
    """
    Princess' Private Space - Laynie's room in the den.
    
    Features:
    - The Mural (documentation of Laynie)
    - No-privacy beaded curtain
    - Princess pillory and milking
    - Dangling cuffs on bed
    """
    
    PRINCESS_TIME_DESCS = {
        "morning": "Soft light makes the pink walls glow. The fake window shows a sunny pasture. Princess waking hours.",
        "afternoon": "Warm and cozy. The cuffs on the bed catch the light. Nap time, or... other activities.",
        "evening": "The pink deepens to rose. The mural is prominent. The fake window shows sunset over the pasture.",
        "night": "Soft, intimate pink. The cuffs gleam. The beaded curtain offers no privacy from the sounds beyond.",
        "latenight": "Deep quiet in the princess room. But through the curtain, sometimes, wolf sounds...",
    }
    
    def at_object_creation(self):
        super().at_object_creation()
        self.db.atmosphere = {
            "sounds": "cowbell (if collar worn), milking machine, moans, wolf sounds from den",
            "scents": "milk, arousal, pack musk drifting through curtain",
            "mood": "owned princess",
        }
    
    def get_time_description(self) -> str:
        period = get_time_period()
        time_map = {"dawn": "morning", "morning": "morning", "afternoon": "afternoon",
                    "evening": "evening", "night": "night", "latenight": "latenight"}
        period_key = time_map.get(period, "evening")
        return self.PRINCESS_TIME_DESCS.get(period_key, "")
    
    def process_shortcodes(self, text: str, looker=None) -> str:
        text = super().process_shortcodes(text, looker)
        text = text.replace("<time.desc>", self.get_time_description())
        return text


class PrincessMural(CabinObject):
    """
    The Mural - depicts Laynie in pillory being milked.
    This is documentation, not fantasy.
    """
    
    portable = AttributeProperty(default=False)
    
    description = AttributeProperty(default="An elaborate mural painted with care and intent. It depicts a young blonde girl in a pillory being milked, watched by Helena, Shadow, and a hovering fae. This is documentation, not fantasy.")


class PrincessDoodles(CabinObject):
    """Cute doodles of cows, wolves, faeries, and naked women."""
    
    portable = AttributeProperty(default=False)


class FakeWindow(CabinObject):
    """Poster window with time-variant pasture view."""
    
    portable = AttributeProperty(default=False)
    
    views = AttributeProperty(default={
        "morning": "sunny pasture with grazing cattle",
        "afternoon": "warm pasture, cows resting in shade",
        "evening": "sunset over the pasture, golden light",
        "night": "moonlit pasture, cattle sleeping",
    })


class PrincessBed(CabinFurniture):
    """
    King-sized bed with pink covers and DANGLING CUFFS.
    """
    
    capacity = AttributeProperty(default=3)  # Mommy + two daughters
    
    supported_positions = AttributeProperty(default=[
        "lying (tucked in)", "curled with stuffie", "spread (cuffed)",
        "on all fours", "nursing", "pile (three)"
    ])
    
    restraint_points = AttributeProperty(default={
        "wrist_cuffs_rails": "arms spread or above head",
        "ankle_cuffs_foot_rail": "legs spread or together",
        "four_point": "spread-eagle on pink covers",
        "one_wrist": "leashed to bed, limited mobility",
    })
    
    # Always present
    has_dangling_cuffs = AttributeProperty(default=True)


class PrincessPillory(CabinFurniture):
    """
    Cherry wood pillory - elegant, positioned for milking.
    """
    
    capacity = AttributeProperty(default=1)
    
    # Adjustable
    height_setting = AttributeProperty(default="standing")
    
    supported_positions = AttributeProperty(default=[
        "standing (locked)", "bent (locked)", "milking position"
    ])
    
    restraint_points = AttributeProperty(default={
        "neck_hole": "head secured",
        "wrist_holes": "hands locked beside neck",
    })


class PrincessMilker(CabinObject):
    """
    Milking machine designed to milk the little princess.
    """
    
    portable = AttributeProperty(default=False)
    
    # Multiple cup sizes
    cup_sizes = AttributeProperty(default=["small", "medium", "large"])
    
    # Stock tracking
    bottles_laynie = AttributeProperty(default=0)
    bottles_auria = AttributeProperty(default=0)


class PrincessToyChest(CabinContainer):
    """
    Toy chest with everything Mommy needs for her daughters.
    """
    
    contents = AttributeProperty(default=[
        "stuffed animals", "princess toys (wands, tiaras, dolls)",
        "pacifiers (adult-sized)", "cowbell collars",
        "nipple clamps", "small plugs", "vibrating wand",
        "ribbons and bows", "picture books (about cows)",
        "diapers", "milk bottles (for feeding)"
    ])


class PrincessBeadedCurtain(CabinObject):
    """
    NO PRIVACY curtain - sound, smell, wolves pass through.
    """
    
    portable = AttributeProperty(default=False)
    
    blocks_sound = AttributeProperty(default=False)
    blocks_smell = AttributeProperty(default=False)
    blocks_wolves = AttributeProperty(default=False)


# =============================================================================
# BUILD FUNCTIONS
# =============================================================================

def find_room(key: str):
    """Find a room by its room_key attribute."""
    from evennia import search_tag
    cabin_objects = search_tag(CABIN_TAG, category="area")
    for obj in cabin_objects:
        if hasattr(obj, 'db') and obj.db.room_key == key:
            return obj
    # Fallback to name search
    results = search.search_object(key)
    return results[0] if results else None


def build_welcome_room():
    """Build the Welcome Room."""
    room = create_object(WelcomeRoom, key="Welcome Room")
    room.db.room_key = ROOM_KEYS["welcome"]
    room.db.desc = ROOM_DESCS["welcome"]
    room.time_descriptions = TIME_DESCS.get("welcome", {})
    room.tags.add(ROOM_KEYS["welcome"], category="room_key")
    
    # Atmosphere
    room.db.atmosphere = {
        "sounds": "muffled wind outside, crackling fire from deeper within, creaking wood",
        "scents": "wood, warmth, a faint musk of wolf, cold air lingering near the door",
        "mood": "welcoming",
    }
    
    # Wolf Prints
    prints = create_object(WolfPrints, key="wolf prints", location=room,
                          aliases=["prints", "scratches", "tracks", "claw marks"])
    
    # Bench with cubbies
    bench = create_object(CabinFurniture, key="rustic bench", location=room,
                         aliases=["bench", "seat"])
    bench.db.desc = "A rustic bench to the left of the door, worn smooth from use."
    bench.db.examined = OBJECT_DESCS["rustic_bench_examined"]
    bench.db.cubby_contents = ["worn slippers", "a pair of boots", "a forgotten scarf"]
    bench.supported_positions = ["sitting", "lying", "bent over"]
    bench.capacity = 2
    
    # Mirror that shows looker's appearance
    mirror = create_object(CabinObject, key="ornate mirror", location=room,
                          aliases=["mirror", "looking glass"])
    mirror.db.desc = "A large mirror with a decorative golden border, secured to the wall above the bench."
    mirror.db.examined = "The frame is ornate but not gaudy—elegant, like something from an old estate."
    mirror.db.frame_desc = OBJECT_DESCS["ornate_mirror_frame"]
    mirror.locks.add("get:false()")
    
    # Coat hooks with hidden pet gear
    hooks = create_object(CabinObject, key="coat hooks", location=room,
                         aliases=["hooks", "coats", "gear", "leashes", "muzzles", "harnesses"])
    hooks.db.desc = OBJECT_DESCS["coat_hooks"]
    hooks.db.normal_items = ["furs for cold days", "colored windbreakers", "sweaters", "scarves"]
    hooks.db.pet_gear = ["sturdy leashes", "well-made muzzles", "leather harnesses", "mittens with paw prints on the palms"]
    hooks.db.detailed_desc = OBJECT_DESCS["coat_hooks_detailed"]
    hooks.locks.add("get:false()")
    
    # Lanterns
    lanterns = create_object(CabinObject, key="antique lanterns", location=room,
                            aliases=["lanterns", "lights", "lamps"])
    lanterns.db.desc = "Electric lights fashioned to resemble antique lanterns hang on chains from the ceiling."
    lanterns.db.examined = OBJECT_DESCS["antique_lanterns"]
    lanterns.locks.add("get:false()")
    
    # Sign with hidden detail
    sign = create_object(CabinObject, key="wooden sign", location=room,
                        aliases=["sign"])
    sign.db.desc = f"A wooden sign hangs above the door."
    sign.db.main_inscription = OBJECT_DESCS["wooden_sign"]
    sign.db.hidden_detail = OBJECT_DESCS["wooden_sign_hidden"]
    sign.db.examined = f'It reads: "|y{OBJECT_DESCS["wooden_sign"]}|n"\n\nOn closer inspection, you notice:\n|x{OBJECT_DESCS["wooden_sign_hidden"]}|n'
    sign.locks.add("get:false()")
    
    # -------------------------------------------------------------------------
    # EXITS
    # -------------------------------------------------------------------------
    from evennia.objects.objects import DefaultExit
    
    # Exit OUT to the outside world (Limbo or forest)
    exit_out = create_object(
        DefaultExit,
        key="out",
        location=room,
        destination=None,  # Will connect to Limbo/forest
        aliases=["outside", "exit", "leave", "door", "o"],
    )
    exit_out.db.desc = "The heavy door leads back out into the cold forest."
    exit_out.db.target_room_key = "limbo"  # Or whatever the outside area is
    
    # Exit IN to the Passageway
    exit_in = create_object(
        DefaultExit,
        key="in",
        location=room,
        destination=None,  # Connected by connect_exits
        aliases=["inside", "deeper", "cabin", "passageway", "i"],
    )
    exit_in.db.desc = "The warm interior of the cabin beckons deeper inside."
    exit_in.db.target_room_key = "cabin_passageway"
    
    print(f"Built Welcome Room: {room.dbref}")
    return room


def build_passageway():
    """Build the Passageway."""
    room = create_object(PassagewayRoom, key="Passageway")
    room.db.room_key = ROOM_KEYS["passageway"]
    room.db.desc = ROOM_DESCS["passageway"]
    room.time_descriptions = TIME_DESCS.get("passageway", {})
    room.tags.add(ROOM_KEYS["passageway"], category="room_key")
    
    # Atmosphere
    room.db.atmosphere = {
        "sounds": "muffled voices from the Common Room, distant warmth, creaking wood",
        "scents": "potpourri, wood polish, faint musk",
        "mood": "homey",
    }
    
    # Shadow Musk (invisible)
    musk = create_object(ShadowMusk, key="shadow musk", location=room)
    
    # Area Rug
    rug = create_object(CabinObject, key="area rug", location=room,
                       aliases=["rug", "carpet"])
    rug.db.desc = OBJECT_DESCS["area_rug"]
    rug.db.examined = OBJECT_DESCS["area_rug_examined"]
    rug.locks.add("get:false()")
    
    # Entry Table
    table = create_object(CabinObject, key="entry table", location=room,
                         aliases=["table"])
    table.db.desc = OBJECT_DESCS["entry_table"]
    table.db.examined = OBJECT_DESCS["entry_table_examined"]
    table.locks.add("get:false()")
    
    # Wolf Figurines
    figurines = create_object(CabinObject, key="wolf figurines", location=room,
                             aliases=["figurines", "wolves", "statues", "carvings"])
    figurines.db.desc = OBJECT_DESCS["wolf_figurines"]
    figurines.db.examined = OBJECT_DESCS["wolf_figurines_examined"]
    figurines.locks.add("get:false()")
    
    # Potpourri Bowl
    potpourri = create_object(SeasonalPotpourri, key="potpourri bowl", location=room,
                             aliases=["potpourri", "bowl"])
    potpourri.db.desc = "A decorative bowl of dried flowers and herbs."
    
    # Portrait
    portrait = create_object(ViewerAwarePortrait, key="portrait", location=room,
                            aliases=["painting", "shadow's harem", "harem", "oil painting"])
    portrait.db.desc = "A portrait titled \"Shadow's Harem\"."
    portrait.locks.add("get:false()")
    
    # Scratches
    scratches = create_object(CabinObject, key="scratches", location=room,
                             aliases=["gouges", "claw marks", "marks"])
    scratches.db.desc = OBJECT_DESCS["scratches"]
    scratches.db.examined = OBJECT_DESCS["scratches_examined"]
    scratches.locks.add("get:false()")
    
    # -------------------------------------------------------------------------
    # PLAQUES
    # -------------------------------------------------------------------------
    
    # Helena's Plaque
    helena_plaque = create_object(CabinObject, key="Helena's plaque", location=room,
                                 aliases=["h.s. plaque", "iron plaque", "gothic plaque"])
    helena_plaque.db.desc = OBJECT_DESCS["helena_plaque"]
    helena_plaque.db.examined = OBJECT_DESCS["helena_plaque_examined"]
    helena_plaque.locks.add("get:false()")
    
    # Auria's Plaque
    auria_plaque = create_object(CabinObject, key="Auria's plaque", location=room,
                                aliases=["pink plaque", "faerie plaque"])
    auria_plaque.db.desc = OBJECT_DESCS["auria_plaque"]
    auria_plaque.db.examined = OBJECT_DESCS["auria_plaque_examined"]
    auria_plaque.locks.add("get:false()")
    
    # Garden Plaque
    garden_plaque = create_object(CabinObject, key="Garden plaque", location=room,
                                 aliases=["mahogany plaque", "vine plaque", "garden of knowledge plaque"])
    garden_plaque.db.desc = OBJECT_DESCS["garden_plaque"]
    garden_plaque.db.examined = OBJECT_DESCS["garden_plaque_examined"]
    garden_plaque.locks.add("get:false()")
    
    # Guest Room Plaque
    guest_plaque = create_object(CabinObject, key="Guest Room plaque", location=room,
                                aliases=["yellow plaque", "floral plaque", "guest plaque"])
    guest_plaque.db.desc = OBJECT_DESCS["guest_plaque"]
    guest_plaque.db.examined = OBJECT_DESCS["guest_plaque_examined"]
    guest_plaque.locks.add("get:false()")
    
    # -------------------------------------------------------------------------
    # EXITS
    # -------------------------------------------------------------------------
    from evennia.objects.objects import DefaultExit
    
    # Exit OUT to Welcome Room
    exit_out = create_object(
        DefaultExit,
        key="out",
        location=room,
        destination=None,  # Connected by connect_exits
        aliases=["outside", "exit", "leave", "welcome", "o"],
    )
    exit_out.db.desc = "The doorway leads back to the Welcome Room."
    exit_out.db.target_room_key = "cabin_welcome"
    
    # Exit WEST to Helena's Room (iron door)
    exit_west = create_object(
        DefaultExit,
        key="west",
        location=room,
        destination=None,
        aliases=["w", "helena", "helena's room", "iron door"],
    )
    exit_west.db.desc = "A heavy iron door leads west to Helena's Room."
    exit_west.db.target_room_key = "cabin_helena_room"
    
    # Exit NORTH to Common Room (arch)
    exit_north = create_object(
        DefaultExit,
        key="north",
        location=room,
        destination=None,
        aliases=["n", "common", "common room", "arch"],
    )
    exit_north.db.desc = "An archway leads north to the Common Room."
    exit_north.db.target_room_key = "cabin_common_room"
    
    # Exit EAST to Guest Room
    exit_east_guest = create_object(
        DefaultExit,
        key="east",
        location=room,
        destination=None,
        aliases=["e", "guest", "guest room"],
    )
    exit_east_guest.db.desc = "A door leads east to the Guest Room."
    exit_east_guest.db.target_room_key = "cabin_guest_room"
    
    # Exit SOUTHEAST to Garden of Knowledge
    exit_se = create_object(
        DefaultExit,
        key="southeast",
        location=room,
        destination=None,
        aliases=["se", "garden", "garden of knowledge"],
    )
    exit_se.db.desc = "A vine-covered doorway leads southeast to the Garden of Knowledge."
    exit_se.db.target_room_key = "cabin_garden_knowledge"
    
    # Exit SOUTH to Auria's Room
    exit_south = create_object(
        DefaultExit,
        key="south",
        location=room,
        destination=None,
        aliases=["s", "auria", "auria's room"],
    )
    exit_south.db.desc = "A pink-framed doorway leads south to Auria's Room."
    exit_south.db.target_room_key = "cabin_aurias_room"
    
    print(f"Built Passageway: {room.dbref}")
    return room


def build_helena_room():
    """Build Helena's Room with all objects, tapestry exits, and mechanisms."""
    room = create_object(HelenaRoom, key="Helena's Room")
    room.db.room_key = ROOM_KEYS["helena"]
    room.db.desc = ROOM_DESCS["helena"]
    room.time_descriptions = TIME_DESCS.get("helena", {})
    room.tags.add(ROOM_KEYS["helena"], category="room_key")
    
    # Atmosphere
    room.db.atmosphere = {
        "sounds": "creaking bed frame, chains clinking, muffled sounds, breathing",
        "scents": "Helena's perfume, Shadow's musk, leather, silk",
        "mood": "dominion",
    }
    
    # -------------------------------------------------------------------------
    # FURNITURE
    # -------------------------------------------------------------------------
    
    # Bed
    bed = create_object(HelenaBed, key="canopied bed", location=room,
                       aliases=["bed", "helena's bed", "great bed", "canopy bed"])
    bed.db.desc = OBJECT_DESCS["helena_bed"]
    bed.db.examined = OBJECT_DESCS.get("helena_bed_examined", "")
    
    # Kennel
    kennel = create_object(HelenaKennel, key="kennel", location=room,
                          aliases=["cage", "under bed", "beneath bed"])
    kennel.db.desc = OBJECT_DESCS["helena_kennel"]
    kennel.db.examined = OBJECT_DESCS.get("helena_kennel_examined", "")
    
    # Desk with drawers
    desk = create_object(HelenaDesk, key="metal desk", location=room,
                        aliases=["desk", "helena's desk"])
    desk.db.desc = OBJECT_DESCS["helena_desk"]
    desk.db.examined = OBJECT_DESCS.get("helena_desk_examined", "")
    
    # Toys on desk
    toys = create_object(CabinObject, key="toys", location=room,
                        aliases=["dildos", "vibrators", "cat o nine tails", "whips", "strap-ons"])
    toys.db.desc = "A large assortment of toys atop the desk—dildos, vibrators, whips and feathers, large strap-ons, and a black and purple cat o' nine tails."
    toys.locks.add("get:false()")
    
    # Wall Restraints
    restraints = create_object(WallRestraints, key="wall chains", location=room,
                              aliases=["restraints", "shackles", "collars", "chains", "wall restraints"])
    restraints.db.desc = OBJECT_DESCS["wall_restraints"]
    
    # Pet Bed
    pet_bed = create_object(PurplePetBed, key="purple pet bed", location=room,
                           aliases=["pet bed", "dog bed"])
    pet_bed.db.desc = OBJECT_DESCS["purple_pet_bed"]
    
    # -------------------------------------------------------------------------
    # ROOM OBJECTS (viewable)
    # -------------------------------------------------------------------------
    
    # Claw marks in room
    claws = create_object(ClawGouges, key="claw marks", location=room,
                         aliases=["claws", "gouges", "scratches"])
    claws.db.desc = OBJECT_DESCS["claw_gouges"]
    claws.locks.add("get:false()")
    
    # Pillows
    pillows = create_object(ChewedPillows, key="pillows", location=room,
                           aliases=["chewed pillows"])
    pillows.db.desc = OBJECT_DESCS["chewed_pillows"]
    pillows.locks.add("get:false()")
    
    # -------------------------------------------------------------------------
    # KENNEL CONTENTS (conceptually inside kennel)
    # -------------------------------------------------------------------------
    
    drawings = create_object(KennelDrawings, key="Princess's drawings", location=room,
                            aliases=["drawings", "pictures", "art"])
    drawings.db.desc = OBJECT_DESCS["kennel_drawings"]
    drawings.db.in_kennel = True
    drawings.locks.add("get:false()")
    
    eevee = create_object(EeveePlushie, key="handmade Eevee plushie", location=room,
                         aliases=["eevee", "plushie", "stuffie", "stuffed animal"])
    eevee.db.desc = OBJECT_DESCS["kennel_eevee"]
    eevee.db.in_kennel = True
    
    blanket = create_object(TearStainedBlanket, key="tear-stained blanket", location=room,
                           aliases=["blanket", "pillow", "bedding"])
    blanket.db.desc = OBJECT_DESCS["kennel_blanket"]
    blanket.db.in_kennel = True
    blanket.locks.add("get:false()")
    
    kennel_gouges = create_object(CrayonGouges, key="crayon-filled gouges", location=room,
                                 aliases=["crayon", "crayon gouges", "filled gouges"])
    kennel_gouges.db.desc = OBJECT_DESCS["kennel_crayon_gouges"]
    kennel_gouges.db.in_kennel = True
    kennel_gouges.locks.add("get:false()")
    
    # -------------------------------------------------------------------------
    # TAPESTRY EXITS (SWITCHED: North → Disciplination, South → Nursery)
    # -------------------------------------------------------------------------
    
    # Get Limbo for placeholder destinations
    limbo = search_object("#2")
    limbo = limbo[0] if limbo else None
    
    # North - to DISCIPLINATION ROOM (not Nursery!)
    tap_north = create_object(
        TapestryExit,
        key="northern tapestry",
        location=room,
        destination=limbo,
        aliases=["north tapestry", "north", "n", "disciplination"],
    )
    tap_north.db.direction = "north"
    tap_north.db.desc = OBJECT_DESCS["northern_tapestry"]
    tap_north.db.open_msg = "You push the northern tapestry aside, revealing a doorway to the Disciplination Room."
    tap_north.db.close_msg = "You let the northern tapestry fall back into place."
    tap_north.db.open_inline = "—pushed aside, revealing a doorway to the Disciplination Room"
    
    # South - to NURSERY (not Disciplination!)
    tap_south = create_object(
        TapestryExit,
        key="southern tapestry",
        location=room,
        destination=limbo,
        aliases=["south tapestry", "south", "s", "nursery"],
    )
    tap_south.db.direction = "south"
    tap_south.db.desc = OBJECT_DESCS["southern_tapestry"]
    tap_south.db.open_msg = "You push the southern tapestry aside, exposing the entrance to the Nursery."
    tap_south.db.close_msg = "You let the southern tapestry fall back into place."
    tap_south.db.open_inline = "—pushed aside, exposing the entrance to the Nursery"
    
    # East - to Momo's Room
    tap_east = create_object(
        TapestryExit,
        key="eastern tapestry",
        location=room,
        destination=limbo,
        aliases=["east tapestry", "momo", "momos room"],
    )
    tap_east.db.direction = "east"
    tap_east.db.desc = OBJECT_DESCS["eastern_tapestry"]
    tap_east.db.open_msg = "You pull back the eastern tapestry, revealing a door to Momo's Room."
    tap_east.db.close_msg = "You let the eastern tapestry fall back into place."
    tap_east.db.open_inline = "—pulled back, revealing a door to Momo's Room"
    
    # -------------------------------------------------------------------------
    # HIDDEN TRAPDOOR (revealed by desk mechanism)
    # -------------------------------------------------------------------------
    
    trapdoor = create_object(
        HiddenTrapdoor,
        key="trapdoor",
        location=room,
        destination=None,  # Connected by connect_exits
        aliases=["down", "d", "laboratory", "lab"],
    )
    trapdoor.db.desc = "A trapdoor stands open in the floor, stone steps descending into darkness—the Hidden Laboratory."
    trapdoor.db.target_room_key = "cabin_laboratory"
    
    # -------------------------------------------------------------------------
    # KENNEL CURTAIN EXIT (from inside kennel to Birthing Den)
    # -------------------------------------------------------------------------
    
    curtain_exit = create_object(
        KennelCurtainExit,
        key="curtain",
        location=room,
        destination=None,  # Connected by connect_exits
        aliases=["birthing den", "den", "tunnel"],
    )
    curtain_exit.db.desc = "The passage through the curtain to the Birthing Den."
    curtain_exit.db.target_room_key = "cabin_birthing_den"
    
    # -------------------------------------------------------------------------
    # MAIN EXITS
    # -------------------------------------------------------------------------
    from evennia.objects.objects import DefaultExit
    
    # Exit EAST to Passageway
    exit_east = create_object(
        DefaultExit,
        key="east",
        location=room,
        destination=None,
        aliases=["e", "out", "passageway", "door"],
    )
    exit_east.db.desc = "The heavy iron door leads east to the Passageway."
    exit_east.db.target_room_key = "cabin_passageway"
    
    # Exit NORTH to Disciplination (through tapestry)
    exit_north = create_object(
        DefaultExit,
        key="north",
        location=room,
        destination=None,
        aliases=["n", "disciplination", "north tapestry", "tapestry north"],
    )
    exit_north.db.desc = "A rich tapestry hides the passage north to the Disciplination Room."
    exit_north.db.target_room_key = "cabin_disciplination"
    
    # Exit SOUTH to Nursery (through tapestry)
    exit_south = create_object(
        DefaultExit,
        key="south",
        location=room,
        destination=None,
        aliases=["s", "nursery", "south tapestry", "tapestry south"],
    )
    exit_south.db.desc = "A tapestry depicting a forest leads south to the Nursery."
    exit_south.db.target_room_key = "cabin_nursery"
    
    # Exit WEST to Momo's Room (through eastern tapestry - confusing but matches lore)
    exit_west = create_object(
        DefaultExit,
        key="west",
        location=room,
        destination=None,
        aliases=["w", "momo", "momo's room", "stable", "tapestry west"],
    )
    exit_west.db.desc = "A pastoral tapestry hides the passage west to Momo's Room."
    exit_west.db.target_room_key = "cabin_momo_room"
    
    print(f"Built Helena's Room: {room.dbref}")
    print(f"  Furniture: canopied bed, kennel, metal desk, wall chains, purple pet bed")
    print(f"  Objects: claw marks, pillows, toys")
    print(f"  Kennel contents: drawings, Eevee plushie, blanket, crayon gouges")
    print(f"  Tapestry exits: north→Disciplination, south→Nursery, west→Momo's")
    print(f"  Hidden: trapdoor→Laboratory, kennel curtain→Birthing Den")
    return room


def build_nursery():
    """Build the Nursery with all furniture, objects, Play Pen, and exits."""
    # -------------------------------------------------------------------------
    # CREATE NURSERY ROOM
    # -------------------------------------------------------------------------
    
    room = create_object(NurseryRoom, key="Nursery")
    room.db.room_key = ROOM_KEYS["nursery"]
    room.db.desc = ROOM_DESCS["nursery"]
    room.time_descriptions = TIME_DESCS.get("nursery", {})
    room.tags.add(ROOM_KEYS["nursery"], category="room_key")
    room.tags.add(CABIN_TAG, category="area")
    
    # -------------------------------------------------------------------------
    # CREATE PLAY PEN ROOM
    # -------------------------------------------------------------------------
    
    playpen = create_object(PlayPenRoom, key="The Play Pen of Adventure")
    playpen.db.room_key = ROOM_KEYS.get("playpen", "cabin_playpen")
    playpen.db.desc = ROOM_DESCS.get("playpen", "A magical play pen...")
    playpen.tags.add("cabin_playpen", category="room_key")
    playpen.tags.add(CABIN_TAG, category="area")
    
    print(f"Created Nursery: {room.dbref}")
    print(f"Created Play Pen: {playpen.dbref}")
    
    # -------------------------------------------------------------------------
    # NURSERY FURNITURE
    # -------------------------------------------------------------------------
    
    # Adult Crib (lockable bars, restraints)
    crib = create_object(NurseryCrib, key="adult crib", location=room,
                        aliases=["crib", "baby bed", "baby crib", "bed"])
    crib.db.desc = OBJECT_DESCS.get("nursery_crib", "A large crib for adults.")
    crib.db.examined = OBJECT_DESCS.get("nursery_crib_examined", "")
    crib.locks.add("get:false()")
    
    # Changing Table (straps, supplies)
    table = create_object(ChangingTable, key="changing table", location=room,
                         aliases=["table", "change table"])
    table.db.desc = OBJECT_DESCS.get("nursery_changing_table", "A large changing table.")
    table.db.examined = OBJECT_DESCS.get("nursery_changing_table_examined", "")
    table.locks.add("get:false()")
    
    # Nursing Chair
    chair = create_object(NursingChair, key="gliding nursing chair", location=room,
                         aliases=["nursing chair", "chair", "rocker", "glider"])
    chair.db.desc = OBJECT_DESCS.get("nursery_nursing_chair", "A comfortable gliding chair.")
    chair.locks.add("get:false()")
    
    # Window Seat
    window_seat = create_object(NurseryWindowSeat, key="window seat", location=room,
                               aliases=["seat"])
    window_seat.db.desc = OBJECT_DESCS.get("nursery_window_seat", "A comfortable window seat.")
    window_seat.locks.add("get:false()")
    
    # Dollhouse
    dollhouse = create_object(NurseryDollhouse, key="dollhouse", location=room,
                             aliases=["doll house", "dolls"])
    dollhouse.db.desc = OBJECT_DESCS.get("nursery_dollhouse", "A large dollhouse.")
    dollhouse.db.examined = OBJECT_DESCS.get("nursery_dollhouse_examined", "")
    dollhouse.locks.add("get:false()")
    
    # Wardrobe
    wardrobe = create_object(NurseryWardrobe, key="wardrobe", location=room,
                            aliases=["closet", "clothes"])
    wardrobe.db.desc = OBJECT_DESCS.get("nursery_wardrobe", "A wardrobe with little clothes.")
    wardrobe.locks.add("get:false()")
    
    # Wicker Arch (description object for the Play Pen entrance)
    arch = create_object(PlayPenArch, key="wicker arch", location=room,
                        aliases=["arch", "play pen entrance"])
    arch.db.desc = OBJECT_DESCS.get("nursery_playpen_arch", "A wicker archway that shimmers.")
    arch.locks.add("get:false()")
    
    # -------------------------------------------------------------------------
    # NURSERY OBJECTS
    # -------------------------------------------------------------------------
    
    # Wallpaper
    wallpaper = create_object(NurseryWallpaper, key="yellow wallpaper", location=room,
                             aliases=["wallpaper", "walls"])
    wallpaper.db.desc = OBJECT_DESCS.get("nursery_wallpaper", "Cheerful yellow wallpaper.")
    wallpaper.locks.add("get:false()")
    
    # Foam Floor
    floor = create_object(NurseryFoamFloor, key="foam floor", location=room,
                         aliases=["floor", "foam", "abc"])
    floor.db.desc = OBJECT_DESCS.get("nursery_foam_floor", "Squishy foam flooring.")
    floor.locks.add("get:false()")
    
    # Window
    window = create_object(NurseryWindow, key="window", location=room)
    window.db.desc = OBJECT_DESCS.get("nursery_window", "A window overlooking the forest.")
    window.locks.add("get:false()")
    
    # Toy Shelves
    shelves = create_object(NurseryToyShelf, key="toy shelves", location=room,
                           aliases=["shelves", "toys"])
    shelves.db.desc = OBJECT_DESCS.get("nursery_toy_shelves", "Colourful shelves holding toys.")
    shelves.locks.add("get:false()")
    
    # Chest of Drawers
    drawers = create_object(CabinContainer, key="chest of drawers", location=room,
                           aliases=["drawers", "dresser"])
    drawers.db.desc = "A chest of drawers holds a variety of clothes for playing dress-up, or just for everyday wear."
    drawers.locks.add("get:false()")
    
    # Scattered Blocks
    blocks = create_object(NurseryBlocks, key="scattered blocks", location=room,
                          aliases=["blocks", "building blocks"])
    blocks.db.desc = OBJECT_DESCS.get("nursery_blocks", "Colourful blocks scattered messily.")
    blocks.locks.add("get:false()")
    
    # Teddy Bear
    teddy = create_object(CabinObject, key="teddy bear", location=room,
                         aliases=["teddy", "bear", "stuffie"])
    teddy.db.desc = OBJECT_DESCS.get("nursery_teddy", "A well-loved teddy bear.")
    
    # Crinkly Diapers
    diapers = create_object(CrinklyDiapers, key="crinkly diapers", location=room,
                           aliases=["diapers", "nappies", "diaper stack"])
    diapers.db.desc = OBJECT_DESCS.get("nursery_diapers", "Thick, crinkly diapers.")
    diapers.locks.add("get:false()")
    
    # Princess's Colouring
    colouring = create_object(PrincessColouring, key="Princess's colouring", location=room,
                             aliases=["colouring", "coloring", "art", "drawing"])
    colouring.db.desc = OBJECT_DESCS.get("nursery_colouring", "A piece of colouring hung on the wall.")
    colouring.locks.add("get:false()")
    
    # Disney Princess Chest
    disney_chest = create_object(DisneyPrincessChest, key="Disney Princess chest", location=room,
                                aliases=["disney chest", "princess chest", "pink chest"])
    disney_chest.db.desc = OBJECT_DESCS.get("nursery_disney_chest", "A pink chest covered in Disney Princesses.")
    disney_chest.locks.add("get:false()")
    
    # Footstool
    footstool = create_object(CabinObject, key="footstool", location=room,
                             aliases=["stool", "foot stool"])
    footstool.db.desc = "A matching footstool sits beside the nursing chair."
    footstool.locks.add("get:false()")
    
    # Kiddie Gate (description object for the exit)
    gate = create_object(CabinObject, key="kiddie gate", location=room,
                        aliases=["gate", "baby gate"])
    gate.db.desc = "A kiddie gate blocks the southern doorway, low enough to step over. Through it, Auria's Room is visible—pink walls, fae warmth, wildflower scent drifting through."
    gate.locks.add("get:false()")
    
    # Tapestry (description object for north exit)
    tapestry = create_object(CabinObject, key="tapestry", location=room,
                            aliases=["north tapestry"])
    tapestry.db.desc = "The tapestry north hides the passage to Helena's Room. Sound is muffled through it—privacy in both directions."
    tapestry.locks.add("get:false()")
    
    # -------------------------------------------------------------------------
    # PLAY PEN EXIT (Nursery → Play Pen)
    # -------------------------------------------------------------------------
    
    from evennia.objects.objects import DefaultExit
    
    exit_playpen = create_object(
        DefaultExit,
        key="in",
        location=room,
        destination=playpen,
        aliases=["enter", "pen", "play pen", "playpen", "wicker"],
    )
    exit_playpen.db.desc = "The wicker arch shimmers faintly. Step through to enter The Play Pen of Adventure."
    
    # -------------------------------------------------------------------------
    # PLAY PEN EXIT (Play Pen → Nursery)
    # -------------------------------------------------------------------------
    
    exit_out = create_object(
        DefaultExit,
        key="out",
        location=playpen,
        destination=room,
        aliases=["exit", "leave", "arch", "nursery"],
    )
    exit_out.db.desc = "The wicker arch looms enormous above—your exit back to normal size. The figurines watch you consider leaving."
    
    # -------------------------------------------------------------------------
    # EXTERNAL EXITS
    # -------------------------------------------------------------------------
    
    # North to Helena's Room
    exit_helena = create_object(
        DefaultExit,
        key="north",
        location=room,
        destination=None,  # Will be connected by build_all_exits
        aliases=["n", "helena", "helena's room", "tapestry"],
    )
    exit_helena.db.desc = "The tapestry hides the passage north to Helena's Room. Sound is muffled through it—privacy in both directions."
    exit_helena.db.target_room_key = "cabin_helena_room"
    
    # South to Auria's Room
    exit_auria = create_object(
        DefaultExit,
        key="south",
        location=room,
        destination=None,  # Will be connected by build_all_exits
        aliases=["s", "auria", "auria's room", "gate", "kiddie gate"],
    )
    exit_auria.db.desc = "A kiddie gate blocks the southern doorway, low enough to step over. Through it, Auria's Room is visible—pink walls, fae warmth, wildflower scent drifting through."
    exit_auria.db.target_room_key = "cabin_auria_room"
    
    # -------------------------------------------------------------------------
    # OUTPUT
    # -------------------------------------------------------------------------
    
    print(f"")
    print(f"Built Nursery: {room.dbref}")
    print(f"  - adult crib (lockable bars, restraints)")
    print(f"  - changing table (straps, supplies)")
    print(f"  - gliding nursing chair")
    print(f"  - window seat, dollhouse, wardrobe")
    print(f"  - wallpaper, floor, window, shelves, blocks, teddy")
    print(f"  - crinkly diapers, Princess's colouring, Disney chest")
    print(f"")
    print(f"Built Play Pen: {playpen.dbref}")
    print(f"  - Shrinking magic active")
    print(f"  - Time dilation: 4 hours inside = 1 hour outside")
    print(f"")
    print(f"Internal Exit: in → Play Pen")
    print(f"Internal Exit: out → Nursery")
    print(f"External Exit: north → Helena's Room (target_room_key set)")
    print(f"External Exit: south → Auria's Room (target_room_key set)")
    
    return room, playpen


def build_aurias_room():
    """
    Build Auria's Room using the dedicated module files.
    
    Imports from:
    - typeclasses.rooms.aurias_room (AuriasRoom typeclass)
    - typeclasses.objects.aurias_objects (room objects + journal)
    - typeclasses.objects.living_eevee (autonomous creature)
    """
    # Import from dedicated modules
    try:
        from typeclasses.rooms.aurias_room import AuriasRoom, create_aurias_room
        from typeclasses.objects.aurias_objects import create_aurias_objects
        from typeclasses.objects.living_eevee import create_living_eevee
        
        # Use the module's builder
        room = create_aurias_room()
        
    except ImportError as e:
        # Fallback if modules not yet installed
        print(f"WARNING: Could not import Auria modules: {e}")
        print("Using fallback CabinRoom - install modules for full functionality")
        room = create_object(CabinRoom, key="Auria's Room")
    
    # Set room keys and tags
    room.db.room_key = ROOM_KEYS["aurias"]
    room.tags.add(ROOM_KEYS["aurias"], category="room_key")
    room.tags.add(CABIN_TAG, category="area")
    
    # Create all objects using the module's builder
    try:
        objects = create_aurias_objects(room)
        print(f"  - Created objects: {', '.join(objects.keys())}")
        
        # Create the Living Eevee (autonomous creature)
        eevee = create_living_eevee(location=room, home=room)
        print(f"  - Created Living Eevee (autonomous creature)")
        
    except (ImportError, NameError) as e:
        print(f"WARNING: Could not create Auria objects: {e}")
        # Minimal fallback objects
        bed = create_object(CabinFurniture, key="comfy bed", location=room,
                           aliases=["bed", "auria's bed"])
        bed.db.desc = OBJECT_DESCS.get("auria_bed", "A comfy bed.")
        
        eevee = create_object(CabinObject, key="Eevee plushie", location=room,
                             aliases=["eevee", "plushie", "stuffie"])
        eevee.db.desc = OBJECT_DESCS.get("eevee_plushie", "A fluffy Eevee plushie.")
    
    # -------------------------------------------------------------------------
    # EXITS
    # -------------------------------------------------------------------------
    
    from evennia.objects.objects import DefaultExit
    
    # West to The Playroom (through beaded curtain)
    exit_west = create_object(
        DefaultExit,
        key="west",
        location=room,
        destination=None,  # Connected by build_all_exits
        aliases=["w", "playroom", "curtain", "beaded curtain"],
    )
    exit_west.db.desc = "A beaded curtain of crystal and colored glass leads west to The Playroom. No sound passes through."
    exit_west.db.target_room_key = "cabin_playroom"
    
    # North to Nursery (through tapestry)
    exit_north = create_object(
        DefaultExit,
        key="north",
        location=room,
        destination=None,  # Connected by build_all_exits
        aliases=["n", "nursery"],
    )
    exit_north.db.desc = "A doorway leads north to the Nursery."
    exit_north.db.target_room_key = "cabin_nursery"
    
    # East to Passageway
    exit_east = create_object(
        DefaultExit,
        key="east",
        location=room,
        destination=None,  # Connected by build_all_exits
        aliases=["e", "out", "passageway", "hall"],
    )
    exit_east.db.desc = "The doorway leads east back to the Passageway."
    exit_east.db.target_room_key = "cabin_passageway"
    
    # -------------------------------------------------------------------------
    # OUTPUT
    # -------------------------------------------------------------------------
    
    print(f"")
    print(f"Built Auria's Room: {room.dbref}")
    print(f"  Exits: west→Playroom, north→Nursery, east→Passageway")
    print(f"  Uses: typeclasses.rooms.aurias_room.AuriasRoom")
    print(f"        typeclasses.objects.aurias_objects")
    print(f"        typeclasses.objects.living_eevee.LivingEevee")
    
    return room


def build_playroom():
    """Build The Playroom with all furniture, equipment, and exit."""
    room = create_object(PlayroomRoom, key="The Playroom")
    room.db.room_key = ROOM_KEYS["playroom"]
    room.db.desc = ROOM_DESCS["playroom"]
    room.time_descriptions = TIME_DESCS.get("playroom", {})
    room.tags.add(ROOM_KEYS["playroom"], category="room_key")
    room.tags.add(CABIN_TAG, category="area")
    
    # -------------------------------------------------------------------------
    # BONDAGE EQUIPMENT
    # -------------------------------------------------------------------------
    
    # Titanium Collar (wall-mounted, glowing inscription)
    collar = create_object(TitaniumCollar, key="titanium collar", location=room,
                          aliases=["collar", "auria collar", "wall collar", "shackles", "chains"])
    collar.db.desc = OBJECT_DESCS.get("playroom_titanium_collar", "A titanium collar with glowing inscription.")
    collar.db.examined = OBJECT_DESCS.get("playroom_titanium_collar_examined", "")
    collar.locks.add("get:false()")
    
    # Pommel Horse (with dildos and restraints)
    horse = create_object(PommelHorse, key="pommel horse", location=room,
                         aliases=["horse", "gymnastics horse", "pommel"])
    horse.db.desc = OBJECT_DESCS.get("playroom_pommel_horse", "A repurposed pommel horse.")
    horse.db.examined = OBJECT_DESCS.get("playroom_pommel_horse_examined", "")
    horse.locks.add("get:false()")
    
    # Suspension Bar
    bar = create_object(SuspensionBar, key="suspension bar", location=room,
                       aliases=["bar", "titanium bar", "ceiling bar"])
    bar.db.desc = OBJECT_DESCS.get("playroom_suspension_bar", "A ceiling-mounted suspension bar.")
    bar.db.examined = OBJECT_DESCS.get("playroom_suspension_bar_examined", "")
    bar.locks.add("get:false()")
    
    # Sex Swing
    swing = create_object(SexSwing, key="sex swing", location=room,
                         aliases=["swing", "black swing"])
    swing.db.desc = OBJECT_DESCS.get("playroom_sex_swing", "A black sex swing.")
    swing.db.examined = OBJECT_DESCS.get("playroom_sex_swing_examined", "")
    swing.locks.add("get:false()")
    
    # Rocking Horse (with dildos)
    rocking = create_object(PlayroomRockingHorse, key="rocking horse", location=room,
                           aliases=["rocking", "horse toy"])
    rocking.db.desc = OBJECT_DESCS.get("playroom_rocking_horse", "A rocking horse with wicked purpose.")
    rocking.db.examined = OBJECT_DESCS.get("playroom_rocking_horse_examined", "")
    rocking.locks.add("get:false()")
    
    # Spreader Bar (PORTABLE!)
    spreader = create_object(PlayroomSpreaderBar, key="spreader bar", location=room,
                            aliases=["spreader", "bar"])
    spreader.db.desc = OBJECT_DESCS.get("playroom_spreader_bar", "An adjustable spreader bar.")
    # Note: No get lock - this one is portable
    
    # -------------------------------------------------------------------------
    # STAGE AREA
    # -------------------------------------------------------------------------
    
    # Performance Stage with pole
    stage = create_object(PerformanceStage, key="performance stage", location=room,
                         aliases=["stage", "pole", "steel pole"])
    stage.db.desc = OBJECT_DESCS.get("playroom_stage", "A sunken stage with pole.")
    stage.db.examined = OBJECT_DESCS.get("playroom_stage_examined", "")
    stage.locks.add("get:false()")
    
    # Audience Couches (capacity 6)
    couches = create_object(AudienceCouches, key="leather couches", location=room,
                           aliases=["couches", "couch", "seating", "audience"])
    couches.db.desc = OBJECT_DESCS.get("playroom_couches", "Plush leather couches.")
    couches.db.examined = OBJECT_DESCS.get("playroom_couches_examined", "")
    couches.locks.add("get:false()")
    
    # -------------------------------------------------------------------------
    # CONTAINERS
    # -------------------------------------------------------------------------
    
    # Toy Table
    table = create_object(PlayroomToyTable, key="toy table", location=room,
                         aliases=["table", "toys"])
    table.db.desc = OBJECT_DESCS.get("playroom_toy_table", "A table with organized toys.")
    table.locks.add("get:false()")
    
    # Paddle Rack
    paddles = create_object(PaddleRack, key="paddle rack", location=room,
                           aliases=["paddles", "rack", "implements", "cane"])
    paddles.db.desc = OBJECT_DESCS.get("playroom_paddle_rack", "A rack of impact implements.")
    paddles.db.examined = OBJECT_DESCS.get("playroom_paddle_rack_examined", "")
    paddles.locks.add("get:false()")
    
    # Closet (with Auria's costumes)
    closet = create_object(PlayroomCloset, key="closet", location=room,
                          aliases=["wardrobe"])
    closet.db.desc = OBJECT_DESCS.get("playroom_closet", "A closet with costumes.")
    closet.db.examined = OBJECT_DESCS.get("playroom_closet_examined", "")
    closet.locks.add("get:false()")
    
    # -------------------------------------------------------------------------
    # ROOM FEATURES
    # -------------------------------------------------------------------------
    
    # Padded Walls (soundproofing)
    walls = create_object(PaddedWalls, key="padded walls", location=room,
                         aliases=["walls", "padding"])
    walls.db.desc = OBJECT_DESCS.get("playroom_padded_walls", "Dark purple padded walls.")
    walls.locks.add("get:false()")
    
    # Mirror
    mirror = create_object(PlayroomMirror, key="mirror", location=room,
                          aliases=["large mirror", "wall mirror"])
    mirror.db.desc = OBJECT_DESCS.get("playroom_mirror", "A full-length mirror.")
    mirror.locks.add("get:false()")
    
    # Beaded Curtain (description object)
    curtain = create_object(BeadedCurtain, key="beaded curtain", location=room,
                           aliases=["curtain", "beads"])
    curtain.db.desc = OBJECT_DESCS.get("playroom_beaded_curtain", "A magical beaded curtain.")
    curtain.locks.add("get:false()")
    
    # -------------------------------------------------------------------------
    # EXIT - East to Auria's Room
    # -------------------------------------------------------------------------
    
    from evennia.objects.objects import DefaultExit
    
    exit_east = create_object(
        DefaultExit,
        key="east",
        location=room,
        destination=None,  # Will be connected by build_all_exits
        aliases=["e", "out", "curtain", "auria", "auria's room"],
    )
    exit_east.db.desc = "The beaded curtain leads east to Auria's Room. Crystal and colored glass strands shimmer with faint enchantment."
    exit_east.db.target_room_key = "cabin_auria_room"
    
    # -------------------------------------------------------------------------
    # OUTPUT
    # -------------------------------------------------------------------------
    
    print(f"")
    print(f"Built The Playroom: {room.dbref}")
    print(f"  - titanium collar (glowing 'Auria' inscription)")
    print(f"  - pommel horse (twin dildos, wrist cuffs)")
    print(f"  - suspension bar (ceiling shackles)")
    print(f"  - sex swing (full restraints)")
    print(f"  - rocking horse (saddle dildos)")
    print(f"  - spreader bar (PORTABLE)")
    print(f"  - performance stage (pole, capacity 3)")
    print(f"  - leather couches (audience, capacity 6)")
    print(f"  - toy table, paddle rack, closet (Auria's costumes)")
    print(f"  - padded walls (soundproofing), mirror, beaded curtain")
    print(f"")
    print(f"Exit: east → Auria's Room (target_room_key set)")
    
    return room


def build_disciplination_room():
    """Build the Disciplination Room with all equipment."""
    room = create_object(DisciplinationRoom, key="Disciplination Room")
    room.db.room_key = ROOM_KEYS["disciplination"]
    room.db.desc = ROOM_DESCS["disciplination"]
    room.time_descriptions = TIME_DESCS.get("disciplination", {})
    room.tags.add(ROOM_KEYS["disciplination"], category="room_key")
    room.tags.add(CABIN_TAG, category="area")
    
    # -------------------------------------------------------------------------
    # RESTRAINT FURNITURE
    # -------------------------------------------------------------------------
    
    # BDSM Bench (with restraint points)
    bench = create_object(BDSMBench, key="BDSM bench", location=room,
                         aliases=["bench", "discipline bench", "spanking bench"])
    bench.db.desc = OBJECT_DESCS["bdsm_bench"]
    bench.db.examined = OBJECT_DESCS.get("bdsm_bench_examined", "")
    bench.locks.add("get:false()")
    
    # Floor Shackles (with restraint points)
    shackles = create_object(FloorShackles, key="floor shackles", location=room,
                            aliases=["shackles", "floor restraints"])
    shackles.db.desc = OBJECT_DESCS["floor_shackles"]
    shackles.db.examined = OBJECT_DESCS.get("floor_shackles_examined", "")
    shackles.locks.add("get:false()")
    
    # Ceiling Collar (with height control)
    collar = create_object(CeilingCollar, key="ceiling collar", location=room,
                          aliases=["collar", "ceiling chains", "hanging collar"])
    collar.db.desc = OBJECT_DESCS["ceiling_collar"]
    collar.db.examined = OBJECT_DESCS.get("ceiling_collar_examined", "")
    collar.locks.add("get:false()")
    
    # Pet Bed (for aftercare)
    pet_bed = create_object(DisciplinePetBed, key="pet bed", location=room,
                           aliases=["dog bed", "aftercare bed"])
    pet_bed.db.desc = OBJECT_DESCS["discipline_pet_bed"]
    pet_bed.locks.add("get:false()")
    
    # -------------------------------------------------------------------------
    # OBJECTS
    # -------------------------------------------------------------------------
    
    # Collar Control Lever
    lever = create_object(CollarLever, key="lever", location=room,
                         aliases=["wall lever", "collar control"])
    lever.db.desc = OBJECT_DESCS.get("collar_lever", "A lever on the western wall controls the ceiling collar.")
    lever.locks.add("get:false()")
    
    # Spreader Bar (portable!)
    spreader = create_object(SpreaderBar, key="spreader bar", location=room,
                            aliases=["spreader", "bar"])
    spreader.db.desc = OBJECT_DESCS.get("spreader_bar", "An adjustable spreader bar.")
    spreader.db.examined = OBJECT_DESCS.get("spreader_bar_examined", "")
    # Note: No get lock - this one is portable
    
    # Discipline Mirror
    mirror = create_object(DisciplineMirror, key="mirror", location=room,
                          aliases=["large mirror", "wall mirror"])
    mirror.db.desc = OBJECT_DESCS["discipline_mirror"]
    mirror.locks.add("get:false()")
    
    # Floor Drain
    drain = create_object(FloorDrain, key="drain", location=room,
                         aliases=["floor drain"])
    drain.db.desc = OBJECT_DESCS.get("discipline_drain", "A drain set into the floor.")
    drain.locks.add("get:false()")
    
    # Erotic Paintings (with detailed return_appearance)
    paintings = create_object(EroticPaintings, key="erotic paintings", location=room,
                             aliases=["paintings", "art", "painting"])
    paintings.db.desc = OBJECT_DESCS.get("erotic_paintings", "Five erotic paintings.")
    paintings.db.examined = OBJECT_DESCS.get("erotic_paintings_examined", "")
    paintings.locks.add("get:false()")
    
    # Polished Floor
    floor = create_object(PolishedFloor, key="polished floor", location=room,
                         aliases=["floor", "floors", "oak floor"])
    floor.db.desc = OBJECT_DESCS.get("discipline_floor", "Highly polished oak floors.")
    floor.locks.add("get:false()")
    
    # -------------------------------------------------------------------------
    # CONTAINERS
    # -------------------------------------------------------------------------
    
    # Toy Shelf
    shelf = create_object(ToyShelf, key="toy shelf", location=room,
                         aliases=["shelf", "toys"])
    shelf.db.desc = OBJECT_DESCS["toy_shelf"]
    shelf.db.examined = OBJECT_DESCS.get("toy_shelf_examined", "")
    shelf.locks.add("get:false()")
    
    # Implement Rack
    rack = create_object(ImplementRack, key="implement rack", location=room,
                        aliases=["rack", "implements", "paddles", "whips", "canes", "floggers"])
    rack.db.desc = OBJECT_DESCS["implement_rack"]
    rack.db.examined = OBJECT_DESCS.get("implement_rack_examined", "")
    rack.locks.add("get:false()")
    
    # Locked Oak Chest
    chest = create_object(LockedOakChest, key="oak chest", location=room,
                         aliases=["chest", "locked chest"])
    chest.db.desc = OBJECT_DESCS["oak_chest"]
    chest.db.examined = OBJECT_DESCS.get("oak_chest_examined", "")
    chest.locks.add("get:false()")
    
    # -------------------------------------------------------------------------
    # EXITS
    # -------------------------------------------------------------------------
    from evennia.objects.objects import DefaultExit
    
    # Exit SOUTH to Helena's Room
    exit_south = create_object(
        DefaultExit,
        key="south",
        location=room,
        destination=None,
        aliases=["s", "out", "helena", "helena's room", "tapestry"],
    )
    exit_south.db.desc = "The tapestry leads south back to Helena's Room."
    exit_south.db.target_room_key = "cabin_helena_room"
    
    print(f"Built Disciplination Room: {room.dbref}")
    print(f"  - BDSM bench (restraint points: wrists, ankles, waist)")
    print(f"  - floor shackles (before mirror)")
    print(f"  - ceiling collar (height: lowered/kneeling/standing/tiptoe/lifted)")
    print(f"  - pet bed (capacity 3, aftercare)")
    print(f"  - lever (controls collar)")
    print(f"  - spreader bar (PORTABLE, adjustable width)")
    print(f"  - mirror, drain, paintings (5 with details), floor")
    print(f"  - toy shelf, implement rack, locked oak chest")
    print(f"  Note: Lighting modes: standard, ambient, interrogation")
    return room


def build_guest_room():
    """Build the Guest Room with all objects."""
    room = create_object(GuestRoom, key="Guest Room")
    room.db.room_key = ROOM_KEYS["guest"]
    room.db.desc = ROOM_DESCS["guest"]
    room.time_descriptions = TIME_DESCS.get("guest", {})
    room.tags.add(ROOM_KEYS["guest"], category="room_key")
    
    # Atmosphere
    room.db.atmosphere = {
        "sounds": "quiet, muffled cabin sounds, occasional creak of rocking chair",
        "scents": "vanilla, fresh linen, hint of roses from wallpaper",
        "mood": "welcoming",
    }
    
    # -------------------------------------------------------------------------
    # FURNITURE
    # -------------------------------------------------------------------------
    
    # Round Bed (with hidden waterproof cover)
    bed = create_object(RoundBed, key="round bed", location=room,
                       aliases=["bed", "guest bed"])
    bed.db.desc = OBJECT_DESCS["guest_round_bed"]
    bed.db.examined = OBJECT_DESCS["guest_round_bed_examined"]
    
    # Rocking Chair (with rocking mechanic)
    chair = create_object(RockingChair, key="rocking chair", location=room,
                         aliases=["chair", "rocker"])
    chair.db.desc = OBJECT_DESCS["guest_rocking_chair"]
    
    # Vanity (with mirror that shows looker)
    vanity = create_object(VanityMirror, key="vanity", location=room,
                          aliases=["mirror", "vanity mirror", "makeup table"])
    vanity.db.desc = OBJECT_DESCS["guest_vanity"]
    vanity.locks.add("get:false()")
    
    # Dresser (with hidden respawning toys)
    dresser = create_object(HiddenToysDresser, key="dresser", location=room,
                           aliases=["drawers", "drawer"])
    dresser.db.desc = OBJECT_DESCS["guest_dresser"]
    dresser.db.examined = OBJECT_DESCS["guest_dresser_examined"]
    
    # Wardrobe (with save/load hook)
    wardrobe = create_object(GuestWardrobe, key="wardrobe", location=room,
                            aliases=["closet", "clothes"])
    wardrobe.db.desc = OBJECT_DESCS["guest_wardrobe"]
    
    # Bedside Table
    table = create_object(CabinObject, key="bedside table", location=room,
                         aliases=["nightstand", "side table", "table"])
    table.db.desc = OBJECT_DESCS["guest_bedside_table"]
    table.db.examined = OBJECT_DESCS["guest_bedside_table_examined"]
    table.locks.add("get:false()")
    
    # -------------------------------------------------------------------------
    # OBJECTS
    # -------------------------------------------------------------------------
    
    # Floor Drain
    drain = create_object(CabinObject, key="drain", location=room,
                         aliases=["floor drain"])
    drain.db.desc = OBJECT_DESCS["guest_drain"]
    drain.db.examined = OBJECT_DESCS["guest_drain_examined"]
    drain.locks.add("get:false()")
    
    # Stuffed Animals
    stuffies = create_object(CabinObject, key="stuffed animals", location=room,
                            aliases=["stuffies", "plushies", "animals"])
    stuffies.db.desc = OBJECT_DESCS["guest_stuffies"]
    stuffies.db.examined = OBJECT_DESCS["guest_stuffies_examined"]
    stuffies.locks.add("get:false()")
    
    # Welcome Plaque
    plaque = create_object(CabinObject, key="plaque", location=room,
                          aliases=["welcome plaque", "sign"])
    plaque.db.desc = OBJECT_DESCS["guest_plaque_room"]
    plaque.db.examined = OBJECT_DESCS["guest_plaque_room_examined"]
    plaque.locks.add("get:false()")
    
    # Area Rug
    rug = create_object(CabinObject, key="area rug", location=room,
                       aliases=["rug", "carpet", "white rug"])
    rug.db.desc = OBJECT_DESCS["guest_area_rug"]
    rug.db.examined = OBJECT_DESCS["guest_area_rug_examined"]
    rug.locks.add("get:false()")
    
    # Wallpaper
    wallpaper = create_object(CabinObject, key="wallpaper", location=room,
                             aliases=["walls", "wall"])
    wallpaper.db.desc = OBJECT_DESCS["guest_wallpaper"]
    wallpaper.db.examined = OBJECT_DESCS["guest_wallpaper_examined"]
    wallpaper.locks.add("get:false()")
    
    # -------------------------------------------------------------------------
    # EXITS
    # -------------------------------------------------------------------------
    from evennia.objects.objects import DefaultExit
    
    # Exit WEST to Passageway
    exit_west = create_object(
        DefaultExit,
        key="west",
        location=room,
        destination=None,
        aliases=["w", "out", "passageway", "door"],
    )
    exit_west.db.desc = "The door leads west back to the Passageway."
    exit_west.db.target_room_key = "cabin_passageway"
    
    print(f"Built Guest Room: {room.dbref}")
    print(f"  Furniture: round bed, rocking chair, vanity, dresser, wardrobe, bedside table")
    print(f"  Objects: drain, stuffed animals, plaque, area rug, wallpaper")
    return room


def build_garden():
    """Build the Garden of Knowledge with all objects."""
    room = create_object(GardenRoom, key="Garden of Knowledge")
    room.db.room_key = ROOM_KEYS["garden"]
    room.db.desc = ROOM_DESCS["garden"]
    room.time_descriptions = TIME_DESCS.get("garden", {})
    room.tags.add(ROOM_KEYS["garden"], category="room_key")
    room.tags.add(CABIN_TAG, category="area")
    
    # Root Desk - center of the room
    desk = create_object(RootDesk, key="root desk", location=room,
                        aliases=["desk", "roots"])
    desk.db.desc = OBJECT_DESCS.get("garden_root_desk", "A desk formed from twisted roots.")
    desk.db.examined = OBJECT_DESCS.get("garden_root_desk_examined", "")
    desk.locks.add("get:false()")
    
    # Seed initial notes
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
    
    # Beanbag Chair
    beanbag = create_object(GardenBeanbag, key="beanbag chair", location=room,
                           aliases=["beanbag", "bean bag", "chair", "pink beanbag"])
    beanbag.db.desc = OBJECT_DESCS.get("garden_beanbag", "A bright pink beanbag chair.")
    beanbag.locks.add("get:false()")
    
    # Living Bookshelves
    shelves = create_object(LivingBookshelves, key="living book shelves", location=room,
                           aliases=["shelves", "bookshelves", "book shelves", "bookcase"])
    shelves.db.desc = OBJECT_DESCS.get("garden_bookshelves", "Living wood bookshelves.")
    shelves.db.examined = OBJECT_DESCS.get("garden_bookshelves_examined", "")
    shelves.locks.add("get:false()")
    
    # MLP Hentai Section (separate viewable)
    mlp = create_object(MLPHentaiSection, key="MLP hentai section", location=room,
                       aliases=["mlp section", "mlp hentai", "pony section", "hentai section"])
    mlp.db.desc = OBJECT_DESCS.get("garden_mlp_section", "My Little Pony hentai.")
    mlp.db.examined = OBJECT_DESCS.get("garden_mlp_section_examined", "")
    mlp.locks.add("get:false()")
    
    # Living Flora
    flora = create_object(LivingFlora, key="vine and flowers", location=room,
                         aliases=["vines", "flowers", "flora", "plants"])
    flora.db.desc = OBJECT_DESCS.get("garden_flora", "Vines and flowers.")
    flora.db.examined = OBJECT_DESCS.get("garden_flora_examined", "")
    flora.locks.add("get:false()")
    
    # Stuffed Animals
    stuffies = create_object(CabinObject, key="stuffed animals", location=room,
                            aliases=["stuffies", "plushies"])
    stuffies.db.desc = OBJECT_DESCS.get("garden_stuffies", "Stuffed animals on the floor.")
    stuffies.locks.add("get:false()")
    
    # Coloring Books
    coloring = create_object(CabinObject, key="coloring books", location=room,
                            aliases=["coloring", "books", "crayons"])
    coloring.db.desc = OBJECT_DESCS.get("garden_coloring", "Coloring books and crayons.")
    coloring.locks.add("get:false()")
    
    # Loamy Earth Floor
    floor = create_object(CabinObject, key="loamy earth", location=room,
                         aliases=["floor", "earth", "soil", "ground"])
    floor.db.desc = OBJECT_DESCS.get("garden_floor", "Rich, dark, loamy soil.")
    floor.locks.add("get:false()")
    
    # -------------------------------------------------------------------------
    # EXITS
    # -------------------------------------------------------------------------
    from evennia.objects.objects import DefaultExit
    
    # Exit NORTHWEST to Passageway
    exit_nw = create_object(
        DefaultExit,
        key="northwest",
        location=room,
        destination=None,
        aliases=["nw", "out", "passageway", "door"],
    )
    exit_nw.db.desc = "The vine-covered doorway leads northwest back to the Passageway."
    exit_nw.db.target_room_key = "cabin_passageway"
    
    print(f"Built Garden of Knowledge: {room.dbref}")
    print(f"  - root desk (state system, notes, positions, restraints)")
    print(f"  - beanbag chair (capacity 2)")
    print(f"  - living book shelves (browsable sections)")
    print(f"  - MLP hentai section")
    print(f"  - vine and flowers (living flora)")
    print(f"  - stuffed animals, coloring books, loamy earth")
    return room


def build_common_room():
    """Build the Common Room."""
    room = create_object(CommonRoom, key="Common Room")
    room.db.room_key = ROOM_KEYS["common"]
    room.db.desc = ROOM_DESCS["common"]
    room.time_descriptions = TIME_DESCS.get("common", {})
    room.tags.add(ROOM_KEYS["common"], category="room_key")
    
    # Kitchen Island
    island = create_object(CabinFurniture, key="kitchen island", location=room,
                          aliases=["island", "counter", "barstools"])
    island.db.desc = "A marble-topped kitchen island with sink and barstools. The marble is cool to the touch."
    island.capacity = 4
    island.supported_positions = ["sitting at barstool", "standing at counter", "bent over island", "sitting on island"]
    
    # Dining Table
    table = create_object(CabinFurniture, key="dining table", location=room,
                         aliases=["table", "mahogany table"])
    table.db.desc = "An antique rectangular table of dark mahogany with eight matching chairs with velvet cushions."
    table.capacity = 8
    table.supported_positions = ["seated", "head of table", "under table", "bent over table", "lying on table"]
    
    # Wildflowers
    flowers = create_object(CabinObject, key="wildflowers", location=room,
                           aliases=["flowers", "vase", "centerpiece"])
    flowers.db.desc = "A glass vase atop a lace runner, filled with wildflowers—perpetually fresh, maintained by fae magic."
    flowers.locks.add("get:false()")
    
    # Hearth
    hearth = create_object(CabinObject, key="hearth", location=room,
                          aliases=["fireplace", "fire"])
    hearth.db.desc = "A warm hearth with a mantle carved with winding trails of leaves and the tracks of wolves."
    hearth.locks.add("get:false()")
    
    # Loveseat
    loveseat = create_object(CabinFurniture, key="loveseat", location=room,
                            aliases=["love seat", "small couch"])
    loveseat.db.desc = "An overstuffed loveseat of cream-colored suede, positioned to catch the fireplace's warmth."
    loveseat.capacity = 2
    loveseat.supported_positions = ["sitting", "cuddled", "lying", "lap sitting"]
    
    # Couch
    couch = create_object(CabinFurniture, key="couch", location=room,
                         aliases=["sofa"])
    couch.db.desc = "A matching full-sized couch of cream-colored suede. Room to stretch out or pile together."
    couch.capacity = 4
    couch.supported_positions = ["sitting", "lying", "cuddled", "sprawled"]
    
    # Rocking Chair
    rocker = create_object(CabinFurniture, key="rocking chair", location=room,
                          aliases=["rocker"])
    rocker.db.desc = "A padded wooden rocking chair by the fire."
    rocker.capacity = 2
    rocker.supported_positions = ["sitting", "rocking", "lap sitting"]
    
    # Recliner
    recliner = create_object(CabinFurniture, key="recliner", location=room,
                            aliases=["chair"])
    recliner.db.desc = "A comfortable recliner with a lever to lean back."
    recliner.capacity = 2
    recliner.supported_positions = ["sitting", "reclined", "lap sitting"]
    
    # Rug
    rug = create_object(CabinObject, key="hearth rug", location=room,
                       aliases=["rug", "plush rug"])
    rug.db.desc = "A plush rug spreads before the fire. Soft, warm, inviting."
    rug.locks.add("get:false()")
    
    # -------------------------------------------------------------------------
    # EXITS
    # -------------------------------------------------------------------------
    from evennia.objects.objects import DefaultExit
    
    # Exit SOUTH to Passageway
    exit_south = create_object(
        DefaultExit,
        key="south",
        location=room,
        destination=None,
        aliases=["s", "passageway", "arch", "archway"],
    )
    exit_south.db.desc = "An archway leads south to the Passageway."
    exit_south.db.target_room_key = "cabin_passageway"
    
    # Exit EAST to Entertainment Room
    exit_east = create_object(
        DefaultExit,
        key="east",
        location=room,
        destination=None,
        aliases=["e", "entertainment", "gaming"],
    )
    exit_east.db.desc = "A doorway leads east to the Entertainment Room."
    exit_east.db.target_room_key = "cabin_entertainment"
    
    # Exit NORTHWEST to Bathing Lounge
    exit_nw = create_object(
        DefaultExit,
        key="northwest",
        location=room,
        destination=None,
        aliases=["nw", "bathing", "bathroom", "shower"],
    )
    exit_nw.db.desc = "A simple wooden door leads northwest to the Bathing Lounge."
    exit_nw.db.target_room_key = "cabin_bathing_lounge"
    
    # Exit WEST to Jacuzzi Room
    exit_west = create_object(
        DefaultExit,
        key="west",
        location=room,
        destination=None,
        aliases=["w", "jacuzzi", "hot tub", "spa"],
    )
    exit_west.db.desc = "A glass door leads west to the Jacuzzi Room."
    exit_west.db.target_room_key = "cabin_jacuzzi"
    
    print(f"Built Common Room: {room.dbref}")
    return room


# =============================================================================
# EXIT CONNECTION FUNCTIONS
# =============================================================================

def create_exit_with_aliases(
    source_room,
    dest_room,
    exit_name: str,
    direction: str,
    extra_aliases: List[str] = None
) -> CabinExit:
    """
    Create an exit with comprehensive aliases.
    
    Args:
        source_room: Room the exit is in
        dest_room: Room the exit leads to
        exit_name: Display name like "Passageway (in)"
        direction: Base direction for aliases (e.g., "in", "north", "west")
        extra_aliases: Additional aliases beyond direction variants
    
    Returns:
        The created exit
    """
    aliases = make_exit_aliases(direction, extra_aliases or [])
    
    exit_obj = create_object(
        CabinExit,
        key=exit_name,
        location=source_room,
        destination=dest_room,
        aliases=aliases
    )
    
    return exit_obj


def connect_exits():
    """
    Connect all cabin exits by finding their destinations via target_room_key.
    
    This function finds all exits that have a db.target_room_key attribute
    and sets their destination to the appropriate room.
    """
    from evennia import search_tag
    from evennia.objects.objects import DefaultExit
    
    # Build a lookup of room_key -> room object
    room_lookup = {}
    cabin_objects = search_tag(CABIN_TAG, category="area")
    
    for obj in cabin_objects:
        if hasattr(obj, 'db') and obj.db.room_key:
            room_lookup[obj.db.room_key] = obj
    
    # Also add Limbo lookup (for outside exit)
    from evennia import search_object
    limbo_results = search_object("#2")  # Limbo is usually #2
    if limbo_results:
        room_lookup["limbo"] = limbo_results[0]
    
    exits_connected = 0
    exits_failed = []
    
    # Find all exits in cabin rooms and connect them
    for room in cabin_objects:
        if not hasattr(room, 'contents'):
            continue
            
        for obj in room.contents:
            # Check if it's an exit with a target_room_key
            if hasattr(obj, 'destination') and hasattr(obj, 'db'):
                target_key = obj.db.target_room_key
                if target_key:
                    # Find the destination room
                    dest_room = room_lookup.get(target_key)
                    if dest_room:
                        obj.destination = dest_room
                        exits_connected += 1
                        print(f"  Connected: {obj.key} -> {dest_room.key}")
                    else:
                        exits_failed.append((obj.key, target_key))
    
    if exits_failed:
        print(f"\nWARNING: {len(exits_failed)} exits could not be connected:")
        for exit_name, target in exits_failed:
            print(f"  - {exit_name} -> {target} (room not found)")
    
    print(f"\nConnected {exits_connected} exits.")
    return exits_connected



def build_momo_room():
    """Build Momo's Room - the stable stall."""
    room = create_object(MomoRoom, key="Momo's Room")
    room.db.room_key = ROOM_KEYS["momo"]
    room.db.desc = ROOM_DESCS["momo"]
    room.time_descriptions = TIME_DESCS.get("momo", {})
    room.tags.add(ROOM_KEYS["momo"], category="room_key")
    
    # Meadow View (magical window)
    meadow = create_object(MomoMeadowView, key="meadow view", location=room,
                          aliases=["meadow", "view", "southern wall", "window", "brook", "tree"])
    meadow.db.desc = OBJECT_DESCS["momo_meadow"]
    meadow.db.examined = OBJECT_DESCS["momo_meadow_examined"]
    meadow.locks.add("get:false()")
    
    # Futon
    futon = create_object(MomoFuton, key="yellow futon", location=room,
                         aliases=["futon", "bed", "pillows"])
    futon.db.desc = OBJECT_DESCS["momo_futon"]
    futon.db.examined = OBJECT_DESCS["momo_futon_examined"]
    
    # Momo's Collar
    collar = create_object(MomoCollar, key="Momo's collar", location=room,
                          aliases=["collar", "bell", "leash", "helena's momo"])
    collar.db.desc = OBJECT_DESCS["momo_collar"]
    collar.db.examined = OBJECT_DESCS["momo_collar_examined"]
    
    # Feeding Trough
    trough = create_object(MomoFeedingTrough, key="feeding trough", location=room,
                          aliases=["trough", "faucet", "hose", "showerhead"])
    trough.db.desc = OBJECT_DESCS["momo_trough"]
    trough.db.examined = OBJECT_DESCS["momo_trough_examined"]
    
    # Pillory
    pillory = create_object(MomoPillory, key="pillory", location=room,
                           aliases=["oak pillory", "steel pillory", "stocks"])
    pillory.db.desc = OBJECT_DESCS["momo_pillory"]
    pillory.db.examined = OBJECT_DESCS["momo_pillory_examined"]
    
    # Milking Machine
    milker = create_object(MomoMilkingMachine, key="milking machine", location=room,
                          aliases=["machine", "milker", "bottles", "cabinet"])
    milker.db.desc = OBJECT_DESCS["momo_milking_machine"]
    milker.db.examined = OBJECT_DESCS["momo_milking_machine_examined"]
    
    # Breeding Bench
    bench = create_object(MomoBreedingBench, key="breeding bench", location=room,
                         aliases=["bench", "adjustable bench"])
    bench.db.desc = OBJECT_DESCS["momo_breeding_bench"]
    bench.db.examined = OBJECT_DESCS["momo_breeding_bench_examined"]
    
    # Feather Pedestal
    pedestal = create_object(MomoFeatherPedestal, key="feather pedestal", location=room,
                            aliases=["pedestal", "feather", "tickle device", "tickle pedestal"])
    pedestal.db.desc = OBJECT_DESCS["momo_feather_pedestal"]
    pedestal.db.examined = OBJECT_DESCS["momo_feather_pedestal_examined"]
    
    # Tack Wall
    tack = create_object(MomoTackWall, key="tack wall", location=room,
                        aliases=["tack", "harnesses", "bridles", "crop", "rope"])
    tack.db.desc = OBJECT_DESCS["momo_tack"]
    tack.db.examined = OBJECT_DESCS["momo_tack_examined"]
    
    # Stucco Walls
    stucco = create_object(CabinObject, key="yellow stucco", location=room,
                          aliases=["stucco", "walls", "fence"])
    stucco.db.desc = OBJECT_DESCS["momo_stucco"]
    stucco.locks.add("get:false()")
    
    # Exit to Helena's Room
    exit_west = create_object(DefaultExit, key="west", location=room, destination=None)
    exit_west.db.target_room_key = "cabin_helena_room"
    exit_west.aliases.add("tapestry")
    
    print(f"Built Momo's Room: {room.dbref}")
    return room


def build_entertainment_room():
    """Build the Entertainment Room - nerd haven with secrets."""
    room = create_object(EntertainmentRoom, key="Entertainment Room")
    room.db.room_key = ROOM_KEYS["entertainment"]
    room.db.desc = ROOM_DESCS["entertainment"]
    room.time_descriptions = TIME_DESCS.get("entertainment", {})
    room.tags.add(ROOM_KEYS["entertainment"], category="room_key")
    
    # Bookshelves
    shelves = create_object(EntertainmentBookshelves, key="bookshelves", location=room,
                           aliases=["shelves", "books", "figurines", "rpg", "mlp hentai"])
    shelves.db.desc = OBJECT_DESCS["entertainment_shelves"]
    shelves.db.examined = OBJECT_DESCS["entertainment_shelves_examined"]
    
    # Gaming Table
    table = create_object(EntertainmentGamingTable, key="gaming table", location=room,
                         aliases=["table", "game table", "pool table"])
    table.db.desc = OBJECT_DESCS["entertainment_gaming_table"]
    table.db.examined = OBJECT_DESCS["entertainment_gaming_table_examined"]
    
    # Wet Bar
    bar = create_object(EntertainmentWetBar, key="wet bar", location=room,
                       aliases=["bar", "stools", "graffiti", "liquor"])
    bar.db.desc = OBJECT_DESCS["entertainment_wet_bar"]
    bar.db.examined = OBJECT_DESCS["entertainment_wet_bar_examined"]
    
    # Dairy Fridge
    fridge = create_object(DairyFridge, key="dairy fridge", location=room,
                          aliases=["fridge", "mini fridge", "dairy farm", "laynie's cream", "auria's sweet"])
    fridge.db.desc = OBJECT_DESCS["entertainment_dairy_fridge"]
    fridge.db.examined = OBJECT_DESCS["entertainment_dairy_fridge_examined"]
    
    # Leather Sofa
    sofa = create_object(EntertainmentSofa, key="leather sofa", location=room,
                        aliases=["sofa", "couch"])
    sofa.db.desc = OBJECT_DESCS["entertainment_sofa"]
    sofa.db.examined = OBJECT_DESCS["entertainment_sofa_examined"]
    
    # Windows
    windows = create_object(CabinObject, key="windows", location=room,
                           aliases=["window", "glass", "forest view"])
    windows.db.desc = OBJECT_DESCS["entertainment_windows"]
    windows.locks.add("get:false()")
    
    # RGB Lighting
    rgb = create_object(CabinObject, key="RGB lighting", location=room,
                       aliases=["rgb", "lights", "light strips"])
    rgb.db.desc = OBJECT_DESCS["entertainment_rgb"]
    rgb.locks.add("get:false()")
    
    # Exit to Common Room
    exit_west = create_object(DefaultExit, key="west", location=room, destination=None)
    exit_west.db.target_room_key = "cabin_common_room"
    
    print(f"Built Entertainment Room: {room.dbref}")
    return room


def build_bathing_room():
    """Build the Bathing Lounge - luxury bathroom with Cursed Shower."""
    room = create_object(BathingRoom, key="Bathing Lounge")
    room.db.room_key = ROOM_KEYS["bathing"]
    room.db.desc = ROOM_DESCS["bathing"]
    room.time_descriptions = TIME_DESCS.get("bathing", {})
    room.tags.add(ROOM_KEYS["bathing"], category="room_key")
    
    # Tiles
    tiles = create_object(CabinObject, key="tiles", location=room,
                         aliases=["tile", "floor", "walls"])
    tiles.db.desc = OBJECT_DESCS["bathing_tiles"]
    tiles.locks.add("get:false()")
    
    # Shelves
    shelves = create_object(CabinObject, key="shelves", location=room,
                           aliases=["towels", "toiletries"])
    shelves.db.desc = OBJECT_DESCS["bathing_shelves"]
    shelves.locks.add("get:false()")
    
    # Hygiene Cabinet
    hygiene = create_object(BathingCabinets, key="hygiene cabinet", location=room,
                           aliases=["lotions", "soaps", "hygiene"])
    hygiene.db.desc = OBJECT_DESCS["bathing_hygiene_cabinet"]
    
    # Toy Cabinet
    toys = create_object(BathingCabinets, key="toy cabinet", location=room,
                        aliases=["toy cabinet", "waterproof toys", "fun cabinet"])
    toys.db.desc = OBJECT_DESCS["bathing_toy_cabinet"]
    
    # Wash Basin
    basin = create_object(WashBasin, key="wash basin", location=room,
                         aliases=["basin", "sink", "mirror"])
    basin.db.desc = OBJECT_DESCS["bathing_wash_basin"]
    basin.locks.add("get:false()")
    
    # Squat Toilet
    toilet = create_object(SquatToilet, key="squat toilet", location=room,
                          aliases=["toilet", "bidet", "alcove"])
    toilet.db.desc = OBJECT_DESCS["bathing_squat_toilet"]
    toilet.db.examined = OBJECT_DESCS["bathing_squat_toilet_examined"]
    
    # Wall Rings
    rings = create_object(BathingWallRings, key="wall rings", location=room,
                         aliases=["rings", "hooks", "restraint points"])
    rings.db.desc = OBJECT_DESCS["bathing_wall_rings"]
    
    # Candles
    candles = create_object(BathingCandles, key="candles", location=room,
                           aliases=["candle"])
    candles.db.desc = OBJECT_DESCS["bathing_candles"]
    
    # Bath Mat
    mat = create_object(BathMat, key="bath mat", location=room,
                       aliases=["mat", "warning"])
    mat.db.desc = OBJECT_DESCS["bathing_bath_mat"]
    mat.locks.add("get:false()")
    
    # THE CURSED SHOWER
    shower = create_object(CursedShower, key="Cursed Shower", location=room,
                          aliases=["shower", "mimic", "glass door", "phallus handle"])
    shower.db.desc = OBJECT_DESCS["bathing_cursed_shower"]
    shower.db.examined = OBJECT_DESCS["bathing_cursed_shower_examined"]
    shower.db.interior = OBJECT_DESCS["bathing_cursed_shower_interior"]
    
    # Exit to Common Room
    exit_se = create_object(DefaultExit, key="southeast", location=room, destination=None)
    exit_se.db.target_room_key = "cabin_common_room"
    exit_se.aliases.add("se")
    
    print(f"Built Bathing Lounge: {room.dbref}")
    return room


def build_jacuzzi_room():
    """Build the Jacuzzi Room - wolf-paw hot tub with surprises."""
    room = create_object(JacuzziRoom, key="Jacuzzi Room")
    room.db.room_key = ROOM_KEYS["jacuzzi"]
    room.db.desc = ROOM_DESCS["jacuzzi"]
    room.time_descriptions = TIME_DESCS.get("jacuzzi", {})
    room.tags.add(ROOM_KEYS["jacuzzi"], category="room_key")
    
    # Window
    window = create_object(JacuzziWindow, key="window", location=room,
                          aliases=["glass", "view", "aurora", "mountains", "forest"])
    window.db.desc = OBJECT_DESCS["jacuzzi_window"]
    window.db.examined = OBJECT_DESCS["jacuzzi_window_examined"]
    window.locks.add("get:false()")
    
    # Breeding Mural
    mural = create_object(BreedingMural, key="breeding mural", location=room,
                         aliases=["mural", "tiles", "mosaic", "panels"])
    mural.db.desc = OBJECT_DESCS["jacuzzi_mural"]
    mural.db.examined = OBJECT_DESCS["jacuzzi_mural_examined"]
    mural.locks.add("get:false()")
    
    # Pedestals
    pedestals = create_object(JacuzziPedestals, key="pedestals", location=room,
                             aliases=["pedestal", "chains", "ivies", "candles"])
    pedestals.db.desc = OBJECT_DESCS["jacuzzi_pedestals"]
    pedestals.locks.add("get:false()")
    
    # Wall Restraints
    restraints = create_object(JacuzziWallRestraints, key="wall restraints", location=room,
                              aliases=["cables", "shackles", "collars", "restraints"])
    restraints.db.desc = OBJECT_DESCS["jacuzzi_wall_restraints"]
    restraints.db.examined = OBJECT_DESCS["jacuzzi_wall_restraints_examined"]
    
    # THE WOLF JACUZZI
    jacuzzi = create_object(WolfJacuzzi, key="wolf jacuzzi", location=room,
                           aliases=["jacuzzi", "hot tub", "wolf print", "paw", "throne", "toe seats"])
    jacuzzi.db.desc = OBJECT_DESCS["jacuzzi_hot_tub"]
    jacuzzi.db.examined = OBJECT_DESCS["jacuzzi_hot_tub_examined"]
    jacuzzi.db.throne_desc = OBJECT_DESCS["jacuzzi_throne"]
    
    # Exit to Common Room
    exit_east = create_object(DefaultExit, key="east", location=room, destination=None)
    exit_east.db.target_room_key = "cabin_common_room"
    
    print(f"Built Jacuzzi Room: {room.dbref}")
    return room


def build_laboratory():
    """Build the Hidden Laboratory - Oreo's workshop."""
    room = create_object(LaboratoryRoom, key="Hidden Laboratory")
    room.db.room_key = ROOM_KEYS["laboratory"]
    room.db.desc = ROOM_DESCS["laboratory"]
    room.time_descriptions = TIME_DESCS.get("laboratory", {})
    room.tags.add(ROOM_KEYS["laboratory"], category="room_key")
    
    # Alchemy Equipment
    alchemy = create_object(AlchemyEquipment, key="alchemical equipment", location=room,
                           aliases=["alchemy", "beakers", "tubes", "distillation"])
    alchemy.db.desc = OBJECT_DESCS["lab_alchemy_equipment"]
    alchemy.db.examined = OBJECT_DESCS["lab_alchemy_examined"]
    alchemy.locks.add("get:false()")
    
    # Ingredient Shelves
    ingredients = create_object(IngredientShelves, key="ingredient shelves", location=room,
                               aliases=["ingredients", "shelves", "moonpetal", "wyrm scale"])
    ingredients.db.desc = OBJECT_DESCS["lab_ingredient_shelves"]
    
    # Workbench
    workbench = create_object(LabWorkbench, key="workbench", location=room,
                             aliases=["bench", "projects"])
    workbench.db.desc = OBJECT_DESCS["lab_workbench"]
    
    # Oreo's Journal
    journal = create_object(OreoJournal, key="journal", location=room,
                           aliases=["research notes", "oreo's notes"])
    journal.db.desc = OBJECT_DESCS["lab_oreo_journal"]
    
    # Magitech Station
    magitech = create_object(MagitechStation, key="magitech station", location=room,
                            aliases=["magitech", "runes", "crystals"])
    magitech.db.desc = OBJECT_DESCS["lab_magitech_station"]
    magitech.locks.add("get:false()")
    
    # Collar Prototype
    prototype = create_object(CollarPrototype, key="collar prototype", location=room,
                             aliases=["prototype", "collar"])
    prototype.db.desc = OBJECT_DESCS["lab_collar_prototype"]
    
    # Storage Cabinet
    storage = create_object(LabStorageCabinet, key="storage cabinet", location=room,
                           aliases=["cabinet", "potions", "finished items"])
    storage.db.desc = OBJECT_DESCS["lab_storage_cabinet"]
    
    # Ladder up
    ladder = create_object(CabinObject, key="ladder", location=room,
                          aliases=["up"])
    ladder.db.desc = OBJECT_DESCS["lab_ladder"]
    ladder.locks.add("get:false()")
    
    # Exit up to Kennel
    exit_up = create_object(DefaultExit, key="up", location=room, destination=None)
    exit_up.db.target_room_key = "cabin_helena_room"  # Goes to kennel area
    exit_up.aliases.add("ladder")
    
    print(f"Built Hidden Laboratory: {room.dbref}")
    return room


def build_birthing_den():
    """Build the Birthing Den - Shadow's sacred space."""
    room = create_object(BirthingDenRoom, key="Birthing Den")
    room.db.room_key = ROOM_KEYS["birthing_den"]
    room.db.desc = ROOM_DESCS["birthing_den"]
    room.time_descriptions = TIME_DESCS.get("birthing_den", {})
    room.tags.add(ROOM_KEYS["birthing_den"], category="room_key")
    
    # Magic Globes
    globes = create_object(MagicGlobes, key="magic globes", location=room,
                          aliases=["globes", "lights", "light"])
    globes.db.desc = OBJECT_DESCS["den_magic_globes"]
    globes.locks.add("get:false()")
    
    # Ceiling
    ceiling = create_object(CabinObject, key="ceiling", location=room,
                           aliases=["fangs", "columns", "stalactites"])
    ceiling.db.desc = OBJECT_DESCS["den_ceiling"]
    ceiling.locks.add("get:false()")
    
    # Origin Paintings
    paintings = create_object(OriginPaintings, key="origin paintings", location=room,
                             aliases=["paintings", "murals", "origin", "panels"])
    paintings.db.desc = OBJECT_DESCS["den_origin_paintings"]
    paintings.db.examined = OBJECT_DESCS["den_origin_paintings_examined"]
    paintings.locks.add("get:false()")
    
    # Pack Prints
    prints = create_object(PackPrints, key="pack prints", location=room,
                          aliases=["prints", "wolf prints", "ashen prints"])
    prints.db.desc = OBJECT_DESCS["den_pack_prints"]
    prints.db.examined = OBJECT_DESCS["den_pack_prints_examined"]
    prints.locks.add("get:false()")
    
    # Warm Springs
    springs = create_object(WarmSprings, key="warm springs", location=room,
                           aliases=["springs", "pools", "water", "birthing pools"])
    springs.db.desc = OBJECT_DESCS["den_warm_springs"]
    springs.db.examined = OBJECT_DESCS["den_warm_springs_examined"]
    
    # Birthing Nest
    nest = create_object(BirthingNest, key="birthing nest", location=room,
                        aliases=["nest", "bedding", "padding"])
    nest.db.desc = OBJECT_DESCS["den_birthing_nest"]
    nest.db.examined = OBJECT_DESCS["den_birthing_nest_examined"]
    
    # Exit up to Kennel
    exit_up = create_object(DefaultExit, key="up", location=room, destination=None)
    exit_up.db.target_room_key = "cabin_helena_room"  # Goes to kennel
    exit_up.aliases.add("kennel")
    
    # Exit south to Princess Space
    exit_south = create_object(DefaultExit, key="south", location=room, destination=None)
    exit_south.db.target_room_key = "cabin_princess_space"
    exit_south.aliases.add("curtain")
    
    print(f"Built Birthing Den: {room.dbref}")
    return room


def build_princess_space():
    """Build Princess' Private Space - Laynie's room in the den."""
    room = create_object(PrincessSpaceRoom, key="Princess' Private Space")
    room.db.room_key = ROOM_KEYS["princess_space"]
    room.db.desc = ROOM_DESCS["princess_space"]
    room.time_descriptions = TIME_DESCS.get("princess_space", {})
    room.tags.add(ROOM_KEYS["princess_space"], category="room_key")
    
    # The Mural
    mural = create_object(PrincessMural, key="mural", location=room,
                         aliases=["painting", "documentation"])
    mural.db.desc = OBJECT_DESCS["princess_mural"]
    mural.db.examined = OBJECT_DESCS["princess_mural_examined"]
    mural.locks.add("get:false()")
    
    # Doodles
    doodles = create_object(PrincessDoodles, key="doodles", location=room,
                           aliases=["coloring pages", "drawings"])
    doodles.db.desc = OBJECT_DESCS["princess_doodles"]
    doodles.locks.add("get:false()")
    
    # Fake Window
    window = create_object(FakeWindow, key="poster window", location=room,
                          aliases=["window", "poster", "pasture view"])
    window.db.desc = OBJECT_DESCS["princess_fake_window"]
    window.locks.add("get:false()")
    
    # Princess Bed
    bed = create_object(PrincessBed, key="princess bed", location=room,
                       aliases=["bed", "pink bed", "cuffs", "rails"])
    bed.db.desc = OBJECT_DESCS["princess_bed"]
    bed.db.examined = OBJECT_DESCS["princess_bed_examined"]
    
    # Princess Pillory
    pillory = create_object(PrincessPillory, key="princess pillory", location=room,
                           aliases=["pillory", "cherry pillory", "stocks"])
    pillory.db.desc = OBJECT_DESCS["princess_pillory"]
    pillory.db.examined = OBJECT_DESCS["princess_pillory_examined"]
    
    # Princess Milker
    milker = create_object(PrincessMilker, key="milking machine", location=room,
                          aliases=["milker", "machine", "cups"])
    milker.db.desc = OBJECT_DESCS["princess_milker"]
    milker.db.examined = OBJECT_DESCS["princess_milker_examined"]
    
    # Toy Chest
    chest = create_object(PrincessToyChest, key="toy chest", location=room,
                         aliases=["chest", "princess chest", "toys"])
    chest.db.desc = OBJECT_DESCS["princess_toy_chest"]
    chest.db.examined = OBJECT_DESCS["princess_toy_chest_examined"]
    
    # Beaded Curtain
    curtain = create_object(PrincessBeadedCurtain, key="beaded curtain", location=room,
                           aliases=["curtain", "doorway", "entrance"])
    curtain.db.desc = OBJECT_DESCS["princess_beaded_curtain"]
    curtain.locks.add("get:false()")
    
    # Exit north to Birthing Den
    exit_north = create_object(DefaultExit, key="north", location=room, destination=None)
    exit_north.db.target_room_key = "cabin_birthing_den"
    exit_north.aliases.add("curtain")
    exit_north.aliases.add("den")
    
    print(f"Built Princess' Private Space: {room.dbref}")
    return room


# =============================================================================
# MAIN BUILD FUNCTION
# =============================================================================

def build_cabin():
    """
    Build the entire Helena's Cabin.
    
    Usage:
        @py from world.build_helena_cabin import build_cabin; build_cabin()
    """
    print("=" * 60)
    print("Building Helena's Cabin")
    print("=" * 60)
    
    # Build all rooms
    rooms = {}
    
    print("\n--- Building Rooms ---")
    rooms["welcome"] = build_welcome_room()
    rooms["passageway"] = build_passageway()
    rooms["helena"] = build_helena_room()
    rooms["nursery"] = build_nursery()
    rooms["aurias"] = build_aurias_room()
    rooms["playroom"] = build_playroom()
    rooms["disciplination"] = build_disciplination_room()
    rooms["momo"] = build_momo_room()
    rooms["common"] = build_common_room()
    rooms["guest"] = build_guest_room()
    rooms["garden"] = build_garden()
    rooms["entertainment"] = build_entertainment_room()
    rooms["bathing"] = build_bathing_room()
    rooms["jacuzzi"] = build_jacuzzi_room()
    rooms["laboratory"] = build_laboratory()
    rooms["birthing_den"] = build_birthing_den()
    rooms["princess_space"] = build_princess_space()
    
    print(f"\nBuilt {len(rooms)} rooms.")
    
    # Connect exits
    print("\n--- Connecting Exits ---")
    exits = connect_exits()
    
    print("\n" + "=" * 60)
    print("Helena's Cabin build complete!")
    print(f"Rooms: {len(rooms)}")
    print(f"Exits: {exits}")
    print("=" * 60)
    
    return rooms


def destroy_cabin():
    """
    Remove all cabin objects for rebuilding.
    
    Usage:
        @py from world.build_helena_cabin import destroy_cabin; destroy_cabin()
    """
    from evennia import search_tag
    
    cabin_objects = search_tag(CABIN_TAG, category="area")
    count = len(cabin_objects)
    
    for obj in cabin_objects:
        obj.delete()
    
    print(f"Deleted {count} cabin objects.")
    return count


# =============================================================================
# TEST FUNCTIONS
# =============================================================================

def test_time_variants():
    """Test time variant descriptions."""
    welcome = find_room(ROOM_KEYS["welcome"])
    if welcome:
        for period in ["dawn", "morning", "afternoon", "evening", "night", "latenight"]:
            desc = welcome.time_descriptions.get(period, "No description")
            print(f"{period}: {desc[:50]}...")
    else:
        print("Welcome Room not found.")


def test_wolf_prints():
    """Test wolf prints state changes."""
    welcome = find_room(ROOM_KEYS["welcome"])
    if welcome:
        for obj in welcome.contents:
            if isinstance(obj, WolfPrints):
                print(f"Current state: {obj.current_state}")
                obj.on_shadow_pass()
                print(f"After Shadow passes: {obj.current_state}")
                print(f"Description: {obj.get_display_desc()[:100]}...")
                return
        print("Wolf prints not found.")
    else:
        print("Welcome Room not found.")


def test_bed_states():
    """Test Helena's bed state changes."""
    helena = find_room(ROOM_KEYS["helena"])
    if helena:
        for obj in helena.contents:
            if isinstance(obj, HelenaBed):
                print(f"Current state: {obj.bed_state}")
                print(f"Description: {obj.get_state_desc()}")
                obj.soil()
                print(f"After activity: {obj.bed_state}")
                print(f"Description: {obj.get_state_desc()}")
                return
        print("Bed not found.")
    else:
        print("Helena's Room not found.")


# =============================================================================
# EXPORTS
# =============================================================================

__all__ = [
    # Main functions
    "build_cabin",
    "destroy_cabin",
    "connect_exits",
    "find_room",
    
    # Room classes
    "CabinRoom",
    "WelcomeRoom",
    "PassagewayRoom",
    "HelenaRoom",
    "AuriasRoomFallback",
    "NurseryRoom",
    "DisciplinationRoom",
    "GuestRoom",
    "GardenRoom",
    "CommonRoom",
    
    # Object classes
    "CabinObject",
    "CabinFurniture",
    "CabinContainer",
    "CabinExit",
    "WolfPrints",
    "ShadowMusk",
    "SeasonalPotpourri",
    "ViewerAwarePortrait",
    "HelenaBed",
    "HelenaKennel",
    "CeilingCollar",
    
    # Constants
    "CABIN_TAG",
    "ROOM_KEYS",
    "ROOM_DESCS",
    "TIME_DESCS",
    "OBJECT_DESCS",
      ]
