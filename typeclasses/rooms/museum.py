"""
Museum Rooms - The Curator's Domain

Comprehensive museum layout with detailed descriptions, shortcodes,
and state-aware content.

The Museum is organized into:
- PUBLIC AREAS: Entrance, Reception, Collection Wings
- SEMI-PRIVATE: Curator's Office, Workrooms
- THE BASEMENT: Invitation only. You know what's down there.

Shortcode System:
- <curator.presence> - Whether the Curator is visibly present
- <curator.mood> - Current disposition
- <wing.X.completion> - Completion percentage for wing X
- <display.X.status> - Whether display X is filled/empty
- <time.period> - Morning/afternoon/evening/night
- <visitor.count> - How many others are here
- <recent.donation> - Last item donated
- <basement.hint> - Subtle wrongness when appropriate
"""

from typing import Optional, Dict, Any, List
# Handle early import during Django migration loading
try:
    from evennia.typeclasses.attributes import AttributeProperty
except (ImportError, TypeError, AttributeError):
    def AttributeProperty(default=None, **kwargs):
        return default
from typeclasses.base_rooms import IndoorRoom


# =============================================================================
# MUSEUM ATMOSPHERE PRESETS
# =============================================================================

MUSEUM_ATMOSPHERES = {
    "museum_grand": {
        "ambient_sounds": "echoing footsteps, hushed conversations, the soft hum of preservation magic",
        "ambient_scents": "old wood, polish, a hint of formaldehyde, something older beneath",
        "mood": "reverential",
    },
    "museum_quiet": {
        "ambient_sounds": "settling displays, distant footsteps, the creak of old floorboards",
        "ambient_scents": "dust, paper, preservation oils",
        "mood": "contemplative",
    },
    "museum_aquarium": {
        "ambient_sounds": "bubbling water, soft filtration hums, occasional splashes",
        "ambient_scents": "salt, fresh water, aquatic plants",
        "mood": "mesmerizing",
    },
    "museum_living": {
        "ambient_sounds": "rustling leaves, buzzing insects, distant birdsong recordings",
        "ambient_scents": "earth, growing things, pollen",
        "mood": "natural",
    },
    "basement_clinical": {
        "ambient_sounds": "dripping water, distant echoes, something breathing that shouldn't be",
        "ambient_scents": "antiseptic, old stone, fear",
        "mood": "clinical",
    },
    "basement_intimate": {
        "ambient_sounds": "soft sounds, muffled everything, heartbeats",
        "ambient_scents": "warmth, bodies, the Curator's presence",
        "mood": "inevitable",
    },
}


# =============================================================================
# BASE MUSEUM ROOM
# =============================================================================

class MuseumRoomBase(IndoorRoom):
    """
    Base class for all museum rooms.
    
    Provides museum-specific shortcode processing and state tracking.
    """
    
    region = AttributeProperty(default="The Grove")
    zone = AttributeProperty(default="The Museum")
    is_ooc_zone = AttributeProperty(default=True)
    
    # Museum-specific
    wing = AttributeProperty(default="")
    curator_monitors = AttributeProperty(default=True)
    restricted = AttributeProperty(default=False)
    
    # Display tracking
    displays = AttributeProperty(default=dict)  # {name: {filled: bool, item: str, desc: str}}
    
    # Visitor tracking
    visitor_log = AttributeProperty(default=list)  # Recent visitors
    
    def process_shortcodes(self, text: str, looker=None) -> str:
        """Process museum-specific shortcodes."""
        text = super().process_shortcodes(text, looker)
        
        # Curator presence (check if Curator NPC is in room or nearby)
        curator_here = self._check_curator_presence()
        if curator_here:
            text = text.replace("<curator.presence>", "The Curator is here, observing everything with quiet intensity.")
            text = text.replace("<curator.watching>", "You feel watched. Measured. Catalogued.")
        else:
            text = text.replace("<curator.presence>", "The Curator's presence lingers even in their absence.")
            text = text.replace("<curator.watching>", "Even empty, this space feels observed.")
        
        # Visitor count
        visitor_count = len([c for c in self.contents if hasattr(c, 'account') and c.account and c != looker])
        if visitor_count == 0:
            text = text.replace("<visitor.count>", "You appear to be alone here")
            text = text.replace("<visitor.status>", "The wing is quiet, your footsteps echoing")
        elif visitor_count == 1:
            text = text.replace("<visitor.count>", "One other visitor browses nearby")
            text = text.replace("<visitor.status>", "Another visitor moves through the displays")
        else:
            text = text.replace("<visitor.count>", f"{visitor_count} other visitors are present")
            text = text.replace("<visitor.status>", "Several visitors mill about, examining exhibits")
        
        # Display status shortcodes
        for display_name, display_data in self.displays.items():
            tag = f"<display.{display_name}>"
            if display_data.get("filled"):
                text = text.replace(tag, display_data.get("filled_desc", "A specimen rests in the display."))
            else:
                text = text.replace(tag, display_data.get("empty_desc", "The display case stands empty, waiting."))
        
        # Wing completion (would need collection system)
        text = text.replace("<wing.completion>", self._get_wing_completion())
        
        # Basement hints (subtle wrongness in certain areas)
        if "<basement.hint>" in text:
            text = text.replace("<basement.hint>", self._get_basement_hint())
        
        return text
    
    def _check_curator_presence(self) -> bool:
        """Check if Curator NPC is present."""
        for obj in self.contents:
            if hasattr(obj, 'is_curator') and obj.is_curator:
                return True
        return False
    
    def _get_wing_completion(self) -> str:
        """Get wing completion status."""
        # Placeholder - would integrate with collection system
        return "The collection here grows ever more complete."
    
    def _get_basement_hint(self) -> str:
        """Get subtle wrongness hints."""
        import random
        hints = [
            "",  # Sometimes nothing
            "A chill brushes past you, sourceless.",
            "For a moment, you could swear you heard something below your feet.",
            "The shadows in the corner seem deeper than they should be.",
            "Your reflection in a display case seems to move a half-second too slow.",
            "The air tastes faintly of copper.",
        ]
        return random.choice(hints)
    
    def add_display(self, name: str, empty_desc: str, filled_desc: str, filled: bool = False) -> None:
        """Add a display case to the room."""
        displays = dict(self.displays)
        displays[name] = {
            "filled": filled,
            "empty_desc": empty_desc,
            "filled_desc": filled_desc,
            "item": None,
        }
        self.displays = displays
    
    def fill_display(self, name: str, item: str) -> bool:
        """Fill a display with an item."""
        if name in self.displays:
            displays = dict(self.displays)
            displays[name]["filled"] = True
            displays[name]["item"] = item
            self.displays = displays
            return True
        return False


# =============================================================================
# PUBLIC WING ROOMS
# =============================================================================

class MuseumEntrance(MuseumRoomBase):
    """The grand museum entrance."""
    wing = AttributeProperty(default="Entrance")
    
    def at_object_creation(self):
        super().at_object_creation()
        self.db.desc = """
|cMuseum of the Nine Realms|n

Grand double doors of ancient oak and brass stand permanently open, welcoming 
all who seek knowledge—or who have something to contribute.

The foyer soars upward three stories, light falling from crystalline skylights 
that seem to capture illumination from sources beyond this realm. The floor is 
a mosaic depicting Yggdrasil, its roots spreading across the stone, its branches 
reaching toward the distant ceiling.

<display.entrance_feature>

Display cases flank the entrance, showing tantalizing samples from the collections 
within: a fossilized claw from some prehistoric terror, a preserved flower that 
still seems to glow, a fish suspended in crystal-clear preservation fluid.

<visitor.status>

<curator.watching>

A reception desk waits ahead, and beyond it, corridors branch to the museum's 
many wings.
"""
        # Add feature display
        self.add_display(
            "entrance_feature",
            "A central pedestal stands empty, awaiting something worthy of the entrance hall.",
            "The entrance pedestal holds the museum's current featured piece—a magnificent specimen that draws every eye."
        )


class MuseumReception(MuseumRoomBase):
    """The central reception hall."""
    wing = AttributeProperty(default="Reception")
    
    # Donation tracking
    recent_donations = AttributeProperty(default=list)
    donation_of_the_day = AttributeProperty(default="")
    
    def at_object_creation(self):
        super().at_object_creation()
        self.db.desc = """
|cReception Hall|n

The museum's heart, where all paths converge. A circular chamber with corridors 
radiating outward like spokes of a wheel—or roots spreading from a trunk.

A curved |wdonation desk|n occupies one side, staffed or unstaffed depending on 
the hour. A ledger lies open, recording contributions. Behind it, a board displays:

  |y"MOST NEEDED SPECIMENS - See the Curator for Particular Requests"|n

Comfortable seating clusters around small tables, offering rest for weary visitors 
or space for quiet contemplation of what they've seen. A directory mounted on a 
brass stand lists the wings:

  |c• Fossil Wing|n - Bones and stones from before memory
  |c• Fauna Wing|n - Creatures of the realms, preserved
  |c• Flora Wing|n - Living gardens and dried specimens  
  |c• Aquarium|n - Life beneath the waters
  |c• Insectarium|n - The smallest collection, the largest variety
  |c• Art Gallery|n - Creations of mortal and immortal hands
  |c• Library|n - Words, preserved
  |c• Relics Hall|n - Artifacts of power and history

<donation.recent>

<curator.presence>

|xThe directory does not list a basement. There is no basement. 
Why would you think there was a basement?|n
"""
    
    def process_shortcodes(self, text: str, looker=None) -> str:
        text = super().process_shortcodes(text, looker)
        
        if self.recent_donations:
            recent = self.recent_donations[-1]
            text = text.replace(
                "<donation.recent>",
                f"A small plaque notes the most recent donation: \"{recent}\" - contributed today."
            )
        else:
            text = text.replace(
                "<donation.recent>",
                "The donation board shows many slots waiting to be filled."
            )
        
        return text


class FossilWing(MuseumRoomBase):
    """The fossil collection wing."""
    wing = AttributeProperty(default="Fossils")
    
    # Track fossils by realm
    realm_collections = AttributeProperty(default=dict)
    
    def at_object_creation(self):
        super().at_object_creation()
        self.db.desc = """
|cFossil Wing - Echoes in Stone|n

Time itself seems to slow in this wing. The air is cool, still, reverent. 
These are witnesses to ages before memory, before the realms took their 
current forms.

The centerpiece dominates: <display.centerpiece>

Nine alcoves ring the main hall, each dedicated to a realm's ancient past:

  <display.asgard_fossils>
  <display.midgard_fossils>
  <display.jotunheim_fossils>
  
Smaller cases hold individual specimens—teeth, claws, shells, the impressions 
of things soft that somehow found immortality in stone. Labels describe each 
find: where it was discovered, what it might have been, how it lived and died.

<wing.completion>

<visitor.count>. <basement.hint>

The silence here feels appropriate. These were living things once. Now they 
are monuments.
"""
        # Add displays
        self.add_display(
            "centerpiece",
            "An empty central platform awaits something magnificent. The Curator has plans.",
            "A complete skeleton towers over the wing—a creature from before the realms divided, when chaos still ruled."
        )
        self.add_display(
            "asgard_fossils",
            "|yAsgard Alcove|n - Empty cases await the golden realm's ancient dead.",
            "|yAsgard Alcove|n - Fossils of creatures that flew Asgard's prehistoric skies rest in golden-framed cases."
        )
        self.add_display(
            "midgard_fossils",
            "|gMidgard Alcove|n - The mortal realm's deep past lies undiscovered.",
            "|gMidgard Alcove|n - Dinosaur bones, ancient fish, the compressed remains of primordial forests."
        )
        self.add_display(
            "jotunheim_fossils",
            "|cJotunheim Alcove|n - What froze in the giant realm's eternal ice?",
            "|cJotunheim Alcove|n - Massive bones, frozen creatures, things preserved in ice since before memory."
        )


class FaunaWing(MuseumRoomBase):
    """The fauna collection wing."""
    wing = AttributeProperty(default="Fauna")
    
    def at_object_creation(self):
        super().at_object_creation()
        self.db.desc = """
|cFauna Wing - The Beasts of Nine Realms|n

Glass eyes watch you from every direction. Preserved specimens stand in 
eternal poses—predators frozen mid-hunt, prey caught in moments of 
impossible stillness. Dioramas recreate habitats in miniature.

The taxidermy here is exquisite. Too exquisite, perhaps. Some specimens 
seem almost alive, as if they might move the moment you look away.

<display.main_diorama>

Acquisition notes beneath certain displays hint at collection methods:

  |x"Captured during the Jotunheim expedition of..."
  "Acquired through trade with Svartalfheim hunters..."  
  "Donated by a collector who wished to remain anonymous..."|n

The Curator has particular interest in rare specimens. |wParticularly|n rare 
specimens command |wparticular|n attention.

<display.rare_case>

<visitor.status>

<basement.hint>

Some notes mention "living specimens" maintained elsewhere in the museum. 
The notes do not specify where.
"""
        self.add_display(
            "main_diorama",
            "The central diorama space awaits a scene worthy of its prominence.",
            "A massive diorama depicts a hunt frozen in time—predator and prey locked in eternal chase."
        )
        self.add_display(
            "rare_case",
            "A special case sits empty, its plaque reading 'Reserved for Exceptional Specimens.'",
            "The rare specimen case holds something extraordinary—a creature thought extinct, somehow preserved in perfect condition."
        )


class FloraWing(MuseumRoomBase):
    """The flora collection wing - living and preserved plants."""
    wing = AttributeProperty(default="Flora")
    
    # Seasonal blooming
    current_season = AttributeProperty(default="spring")
    
    def at_object_creation(self):
        super().at_object_creation()
        self.db.desc = """
|cFlora Wing - Gardens of the Realms|n

Unlike the preserved stillness of other wings, this space lives and breathes. 
Controlled environments maintain realm-specific conditions: here a pocket of 
Muspelheim's heat nurtures fire-blooms, there Niflheim's chill preserves 
ice-flowers in perpetual crystalline beauty.

<display.living_garden>

Dried specimens and pressed flowers fill cases along the walls, each labeled 
with realm of origin, magical properties, and uses—culinary, alchemical, or 
otherwise.

<seasonal.bloom>

|yThe Curator maintains particular interest in specimens with|n 
|yalchemical applications. Certain plants command premium trades.|n

<display.rare_bloom>

<visitor.count>.

The air is thick with competing scents—sweet, bitter, earthy, alien. 
Something beneath the floral notes suggests preservation chemicals. 
Or something else. <basement.hint>
"""
        self.add_display(
            "living_garden",
            "Empty planters wait for specimens from each realm.",
            "Living plants from nine realms grow in carefully maintained micro-environments, each a tiny slice of their home world."
        )
        self.add_display(
            "rare_bloom",
            "A climate-controlled case stands empty, waiting for something extraordinary.",
            "Behind protective glass, a flower that shouldn't exist blooms in defiance of nature—a hybrid created by the Curator's own hand."
        )
    
    def process_shortcodes(self, text: str, looker=None) -> str:
        text = super().process_shortcodes(text, looker)
        
        season_descs = {
            "spring": "Spring specimens are in full bloom—new growth everywhere, the promise of things to come.",
            "summer": "Summer's abundance fills the wing—everything lush, heavy, fertile.",
            "autumn": "Autumn colors dominate—reds, golds, the beautiful decay of the year's end.",
            "winter": "Winter specimens rest dormant, though the Niflheim section seems more vibrant than ever.",
        }
        text = text.replace("<seasonal.bloom>", season_descs.get(self.current_season, ""))
        
        return text


class AquariumWing(MuseumRoomBase):
    """The aquarium wing - fish and aquatic life."""
    wing = AttributeProperty(default="Aquarium")
    
    # Feeding schedule
    last_feeding = AttributeProperty(default=None)
    next_feeding = AttributeProperty(default=None)
    
    def at_object_creation(self):
        super().at_object_creation()
        self.db.desc = """
|cAquarium Wing - Depths of Nine Realms|n

Blue-green light ripples across every surface, refracted through countless 
tanks. The air is humid, rich with the scent of water from nine different 
worlds—salt and fresh, volcanic and glacial, mundane and magical.

<display.central_tank>

Smaller tanks line the walls in realm-organized sections:

  |yAsgard's Waters|n - Golden fish that shimmer like captured sunlight
  |gMidgard's Depths|n - Familiar ocean and freshwater life
  |cNiflheim's Abyss|n - Things that live in frozen darkness
  |rMuspelheim's Vents|n - Creatures of volcanic heat
  
<display.deep_tank>

<feeding.status>

The sound of water is everywhere—bubbling, filtering, the soft splash of 
fins against glass. <visitor.status>

Some tanks are marked "|rDO NOT TAP GLASS|n." 
One tank is marked "|rDO NOT MAKE EYE CONTACT.|n"

<basement.hint>
"""
        self.add_display(
            "central_tank",
            "An enormous central tank dominates the wing, its depths dark and waiting.",
            "The central tank holds something massive—a shadow that moves in the depths, never fully visible, always watching."
        )
        self.add_display(
            "deep_tank",
            "A pressure-sealed deep tank awaits specimens from the crushing depths.",
            "The deep tank holds nightmares from where light never reaches—luminescent horrors, impossible anatomies."
        )
    
    def process_shortcodes(self, text: str, looker=None) -> str:
        text = super().process_shortcodes(text, looker)
        
        # Feeding status
        if self.next_feeding:
            text = text.replace("<feeding.status>", f"A sign notes: 'Next feeding: {self.next_feeding}'")
        else:
            text = text.replace("<feeding.status>", "The fish drift lazily, recently fed and content.")
        
        return text


class Insectarium(MuseumRoomBase):
    """The insect collection."""
    wing = AttributeProperty(default="Insects")
    
    def at_object_creation(self):
        super().at_object_creation()
        self.db.desc = """
|cInsectarium - The Smallest Collection|n

They say insects outnumber all other life forms combined. Looking at this 
wing, you believe it.

Pinned specimens cover entire walls in geometric arrangements—butterflies 
sorted by color gradient, beetles organized by size, moths from pale to 
dark. The artistry is undeniable, even if the medium is unsettling.

<display.butterfly_wall>

Living terrariums buzz and click with activity. Some are clearly labeled: 
"|gSAFE TO OBSERVE|n". Others bear warnings:

  |r"DO NOT OPEN"
  "VENOMOUS - MAINTENANCE ONLY"  
  "SPECIMEN BITES - DO NOT TAUNT"|n

<display.dangerous_case>

<visitor.count>.

Something crawls across the inside of a terrarium glass, leaving a trail 
of something that might be slime. Or might be something else.

<basement.hint>

|xA note on one empty case reads: "ESCAPED - PLEASE REPORT SIGHTINGS"|n
"""
        self.add_display(
            "butterfly_wall",
            "Empty frames await their complement of wings and color.",
            "An entire wall of butterflies creates a gradient from white to black, every color represented—thousands of wings, frozen forever."
        )
        self.add_display(
            "dangerous_case",
            "A reinforced terrarium sits empty, its warnings feeling premature.",
            "The reinforced case holds something that moves too fast to track, occasionally striking the glass with a sound like cracking stone."
        )


class ArtGallery(MuseumRoomBase):
    """Player art and curator's collection."""
    wing = AttributeProperty(default="Art")
    
    # Track displayed art
    player_art = AttributeProperty(default=list)
    featured_artist = AttributeProperty(default="")
    
    def at_object_creation(self):
        super().at_object_creation()
        self.db.desc = """
|cArt Gallery - Visions of the Realms|n

Paintings, sculptures, tapestries, and stranger mediums fill this wing. 
Some pieces are ancient, recovered from fallen civilizations. Others are 
clearly recent—player contributions marked with small plaques crediting 
their creators.

<display.featured_wall>

The Curator has particular taste. Not everything submitted earns a place 
on these walls. Those that do... the Curator remembers the artist.

|yFeatured Artist: <artist.name>|n

Sculptures occupy central pedestals:
<display.sculpture_main>

The gallery extends deeper, older works giving way to newer submissions, 
the familiar blending with the alien.

<visitor.status>

Something about the art here feels too vivid. The eyes in portraits seem 
to follow you. The landscapes feel like windows rather than paintings.

<basement.hint>
"""
        self.add_display(
            "featured_wall",
            "The featured wall awaits work worthy of prominence.",
            "The featured wall displays the Curator's current favorite—a piece that captures something ineffable, something true."
        )
        self.add_display(
            "sculpture_main",
            "Empty pedestals await three-dimensional works of art.",
            "Sculptures capture moments: a figure in ecstasy, a creature in motion, something that might be abstract or might be too real."
        )
    
    def process_shortcodes(self, text: str, looker=None) -> str:
        text = super().process_shortcodes(text, looker)
        
        if self.featured_artist:
            text = text.replace("<artist.name>", self.featured_artist)
        else:
            text = text.replace("<artist.name>", "Position Available - Impress the Curator")
        
        return text


class Library(MuseumRoomBase):
    """Player writings and ancient texts."""
    wing = AttributeProperty(default="Library")
    
    # Track submitted works
    player_works = AttributeProperty(default=list)
    recent_submission = AttributeProperty(default="")
    
    def at_object_creation(self):
        super().at_object_creation()
        self.db.desc = """
|cLibrary - Words Preserved|n

Shelves rise to distant ceilings, crammed with books, scrolls, tablets, 
and stranger recording methods. The smell of old paper and binding glue 
mingles with preservation magic. Reading nooks are tucked between stacks, 
offering privacy and comfort.

<display.rare_texts>

A submission desk near the entrance accepts new works. Player writings 
that meet the Curator's standards join the permanent collection. Those 
that don't... well. The Curator keeps everything, in one form or another.

|yRecent Additions: <recent.works>|n

The collection is organized by:
  |c• Realm of Origin|n - Stories from nine worlds
  |c• Subject Matter|n - History, fiction, poetry, research
  |c• Sensitivity|n - Some shelves require special permission

<visitor.status>

The library enforces silence. Sound dampening magic ensures whispers don't 
carry. What's discussed in the reading nooks stays in the reading nooks.

<basement.hint>

|xA locked cabinet bears the label: "FORBIDDEN TEXTS - CURATOR ACCESS ONLY"
The lock looks more symbolic than practical.|n
"""
        self.add_display(
            "rare_texts",
            "Display cases await texts of particular historical significance.",
            "Rare texts rest under glass—original manuscripts, forbidden knowledge, words that shaped realms."
        )
    
    def process_shortcodes(self, text: str, looker=None) -> str:
        text = super().process_shortcodes(text, looker)
        
        if self.player_works:
            recent = ", ".join(self.player_works[-3:])
            text = text.replace("<recent.works>", recent)
        else:
            text = text.replace("<recent.works>", "The collection awaits your contribution")
        
        return text


class RelicsHall(MuseumRoomBase):
    """Artifacts of power and history."""
    wing = AttributeProperty(default="Relics")
    
    # Security tracking
    guard_count = AttributeProperty(default=2)
    security_level = AttributeProperty(default="normal")
    
    def at_object_creation(self):
        super().at_object_creation()
        self.db.desc = """
|cRelics Hall - Artifacts of Power|n

The security here is immediately apparent. Wards shimmer visibly around 
display cases. <guard.status> The floor is pressure-sensitive. The air 
tastes of binding magic.

These are not merely old things. These are powerful things.

<display.centerpiece_relic>

Cases organized by realm hold artifacts of historical significance:
  - Weapons that turned the tide of ancient wars
  - Tools of creation and destruction
  - Objects whose purposes have been forgotten
  - Things that |rshould not be touched|n

<display.unknown_relic>

<visitor.count>. The guards watch everyone equally.

Plaques describe known properties. Some plaques simply read: 
"|rEFFECTS UNKNOWN - CAUTION ADVISED|n"

<basement.hint>

|yThe Curator personally acquires relics. Special arrangements exist 
for those who can locate items of particular interest.|n
"""
        self.add_display(
            "centerpiece_relic",
            "The central display stands empty, its wards active around nothing. Waiting.",
            "The hall's centerpiece is a relic of such power that wards visible to the naked eye strain to contain it."
        )
        self.add_display(
            "unknown_relic",
            "A heavily warded case sits empty, prepared for something dangerous.",
            "Something in this case defies identification. It shifts when not observed directly, its form uncertain."
        )
    
    def process_shortcodes(self, text: str, looker=None) -> str:
        text = super().process_shortcodes(text, looker)
        
        if self.guard_count == 0:
            text = text.replace("<guard.status>", "Oddly, no guards are visible—though you feel watched.")
        elif self.guard_count == 1:
            text = text.replace("<guard.status>", "A single guard stands at attention.")
        else:
            text = text.replace("<guard.status>", f"{self.guard_count} guards patrol in measured patterns.")
        
        return text


# =============================================================================
# SEMI-PRIVATE AREAS
# =============================================================================

class CuratorOffice(MuseumRoomBase):
    """The Curator's private office."""
    wing = AttributeProperty(default="Private")
    restricted = AttributeProperty(default=True)
    
    # Appointment tracking
    current_appointment = AttributeProperty(default=None)
    next_appointment = AttributeProperty(default=None)
    
    def at_object_creation(self):
        super().at_object_creation()
        self.lighting = "warm"
        self.db.desc = """
|cThe Curator's Office|n

Surprisingly warm. Surprisingly comfortable. The office of someone who 
spends long hours here and has made it their own.

Bookshelves line every wall, competing for space with curiosity cabinets 
filled with specimens too personal for public display. A massive desk 
dominates the center, its surface organized with the precision of someone 
who knows exactly where everything is.

<curator.presence>

<display.desk_specimen>

Comfortable chairs face the desk—for guests, for supplicants, for those 
the Curator has summoned. The lighting is soft, warm, designed to put 
visitors at ease.

<display.personal_collection>

A door in the back leads to private quarters. A different door, less 
obvious, leads... elsewhere.

<appointment.status>

|xYou're here because the Curator wanted you here. 
The question is: what do they want?|n
"""
        self.add_display(
            "desk_specimen",
            "The desk is clear except for papers and tools of administration.",
            "A specimen jar sits on the desk—something the Curator is currently studying. Its contents watch you."
        )
        self.add_display(
            "personal_collection",
            "Personal display cases hold items of obvious sentimental value.",
            "The Curator's personal collection includes things that seem ordinary but clearly mean something—a lock of hair, a dried flower, a collar."
        )
    
    def process_shortcodes(self, text: str, looker=None) -> str:
        text = super().process_shortcodes(text, looker)
        
        if self.current_appointment:
            text = text.replace("<appointment.status>", f"The Curator is currently meeting with {self.current_appointment}.")
        elif self.next_appointment:
            text = text.replace("<appointment.status>", f"The next appointment: {self.next_appointment}")
        else:
            text = text.replace("<appointment.status>", "The Curator's schedule appears open. For now.")
        
        return text


# =============================================================================
# THE BASEMENT
# =============================================================================

class BasementEntrance(MuseumRoomBase):
    """The unmarked door to the basement."""
    wing = AttributeProperty(default="")
    restricted = AttributeProperty(default=True)
    
    def at_object_creation(self):
        super().at_object_creation()
        self.lighting = "dim"
        self.db.desc = """
|xAn Unmarked Door|n

A plain door in an out-of-the-way corner of the museum. Nothing marks it 
as significant. No sign indicates what lies beyond. The door is the same 
as any other staff entrance.

And yet.

Something about it draws the eye. Something about it says |rdon't|n even 
as something else whispers |ycome closer|n.

<door.status>

The lock is heavy, old, enchanted. You'd need an invitation to pass. Or 
something the Curator wanted badly enough to trade access for.

|xThere is no basement. Why do you keep thinking about the basement?|n

You could turn around. Go back to the public galleries. Forget you saw 
this door. That would be the smart thing to do.

<basement.hint>

|rThe door is waiting.|n
"""
    
    def process_shortcodes(self, text: str, looker=None) -> str:
        text = super().process_shortcodes(text, looker)
        
        # Check if looker has basement access
        has_access = False
        if looker and hasattr(looker, 'basement_access'):
            has_access = looker.basement_access
        
        if has_access:
            text = text.replace("<door.status>", "The door recognizes you. The lock clicks open at your touch.")
        else:
            text = text.replace("<door.status>", "The door is locked. Sealed. Denying entry to those without invitation.")
        
        return text


class BasementStairs(MuseumRoomBase):
    """The stairs down into the basement."""
    wing = AttributeProperty(default="Basement")
    restricted = AttributeProperty(default=True)
    
    def at_object_creation(self):
        super().at_object_creation()
        self.lighting = "dim"
        self.db.desc = """
|xThe Descent|n

Stone stairs spiral downward into darkness. The temperature drops with 
each step—not cold exactly, but cooler, more controlled. The sounds of 
the museum above fade quickly, replaced by a silence that feels enforced.

The walls are bare stone, older than the building above. These stairs 
existed before the museum was built. The museum was built because these 
stairs exist.

Sound-dampening enchantments swallow your footsteps. What happens below 
stays below.

<stair.count>

Halfway down, you pass a point of no return. Not physically—the stairs 
continue in both directions. But something shifts. You've committed to 
seeing what waits at the bottom.

The Curator is aware of everyone who descends these stairs.

|rEvery. Single. One.|n
"""
    
    def process_shortcodes(self, text: str, looker=None) -> str:
        text = super().process_shortcodes(text, looker)
        
        # How many others in basement
        # (Would need to check basement rooms)
        text = text.replace("<stair.count>", "You appear to be the only one descending.")
        
        return text


class BasementMain(MuseumRoomBase):
    """Main basement hall."""
    wing = AttributeProperty(default="Basement")
    restricted = AttributeProperty(default=True)
    
    def at_object_creation(self):
        super().at_object_creation()
        self.lighting = "dim"
        self.db.desc = """
|xThe Basement - Main Hall|n

This is not what you expected. Or perhaps it's exactly what you expected, 
and that's worse.

The main hall is clean, clinical, organized with the same precision as 
the galleries above. Display cases line the walls—but these specimens are 
different. Rarer. More dangerous. More... alive.

<display.live_specimens>

Corridors branch off in several directions, each marked with discrete 
labels that tell you everything you need to know and nothing you want 
to confirm:

  |r→ Breeding Chambers|n
  |r→ Holding Cells|n
  |r→ Processing|n
  |r→ Private Collection|n
  |y→ Curator's Quarters|n

<curator.presence>

<display.recent_acquisition>

The air smells of antiseptic and something sweeter beneath. The lighting 
is clinical, revealing, allowing no shadows to hide in.

|xYou're here now. You chose to come. 
The Curator appreciates choice. 
It makes what comes next more meaningful.|n
"""
        self.add_display(
            "live_specimens",
            "Cases designed for living specimens wait empty, their life support systems humming.",
            "Living specimens occupy the cases—creatures too rare to dissect, too valuable to display publicly, too dangerous to release."
        )
        self.add_display(
            "recent_acquisition",
            "A processing table sits clean and empty, awaiting new arrivals.",
            "A recent acquisition rests in a containment field, still being evaluated. It watches you watching it."
        )


class BreedingChambers(MuseumRoomBase):
    """Where the breeding programs happen."""
    wing = AttributeProperty(default="Basement")
    restricted = AttributeProperty(default=True)
    
    # Program tracking
    active_programs = AttributeProperty(default=list)
    current_subjects = AttributeProperty(default=list)
    
    def at_object_creation(self):
        super().at_object_creation()
        self.lighting = "clinical"
        self.db.desc = """
|rBreeding Chambers|n

The Curator's breeding programs are legendary among certain circles. 
Rare creatures, endangered species, impossible hybrids—this is where 
they're created, maintained, expanded.

<chamber.status>

Each chamber is climate-controlled, sized appropriately for its intended 
occupants, equipped with everything necessary for successful... programs.

Observation windows allow monitoring without disturbance. Recording 
crystals capture everything for later study. Nothing that happens here 
goes undocumented.

<display.breeding_records>

|xThe Curator takes particular interest in acquiring breeding stock.
Some specimens are purpose-acquired. 
Some are... repurposed from other roles.
The Curator is flexible.|n

<active.programs>

A chart tracks lineages, successful pairings, promising offspring. 
Some entries are clearly creature species. Others are marked with 
symbols you don't recognize.

|rOne column is labeled "Volunteer Programs." 
Another is labeled "Involuntary."
Both columns have entries.|n
"""
        self.add_display(
            "breeding_records",
            "Record books wait to document new programs.",
            "Extensive records document generations of successful breeding—lineages, traits, the slow perfection of specimens."
        )
    
    def process_shortcodes(self, text: str, looker=None) -> str:
        text = super().process_shortcodes(text, looker)
        
        if self.active_programs:
            program_list = ", ".join(self.active_programs)
            text = text.replace("<active.programs>", f"Active programs: {program_list}")
        else:
            text = text.replace("<active.programs>", "The chambers await new programs. New subjects.")
        
        if self.current_subjects:
            text = text.replace("<chamber.status>", f"Several chambers are currently occupied. Sounds emerge from behind closed doors.")
        else:
            text = text.replace("<chamber.status>", "The chambers are empty. Waiting. Prepared.")
        
        return text


class HoldingCells(MuseumRoomBase):
    """For specimens not yet processed."""
    wing = AttributeProperty(default="Basement")
    restricted = AttributeProperty(default=True)
    
    # Cell tracking
    occupied_cells = AttributeProperty(default=dict)  # cell_id: occupant_desc
    total_cells = AttributeProperty(default=10)
    
    def at_object_creation(self):
        super().at_object_creation()
        self.lighting = "harsh"
        self.db.desc = """
|rHolding Cells|n

Rows of cells line both walls, each designed for containment of various 
specimen types. Some have bars. Some have force fields. Some have walls 
that seem to absorb light itself.

<cell.status>

The cells are not uncomfortable—the Curator is not cruel without purpose. 
Clean bedding, adequate space, regular meals. This is not a dungeon.

It's a waiting room.

<display.cell_manifest>

What happens to specimens in holding depends on many factors:
  - Value to the collection
  - Rarity of type
  - Cooperative behavior
  - The Curator's current needs
  - What arrangements might be made

|xSome specimens are processed quickly.
Some wait.
Some wait a very long time.
Some learn to stop waiting and start serving.|n

<new.arrivals>

The cells can hear each other. Solidarity forms. Or competition. 
The Curator finds both useful.
"""
        self.add_display(
            "cell_manifest",
            "A manifest board shows all cells empty and awaiting assignment.",
            "The manifest lists current occupants by cell number, species or type, date of acquisition, and 'disposition status.'"
        )
    
    def process_shortcodes(self, text: str, looker=None) -> str:
        text = super().process_shortcodes(text, looker)
        
        occupied = len(self.occupied_cells)
        if occupied == 0:
            text = text.replace("<cell.status>", "All cells stand empty. A rare occurrence.")
            text = text.replace("<new.arrivals>", "")
        elif occupied == 1:
            text = text.replace("<cell.status>", "A single cell is occupied. Its inhabitant watches you pass.")
            text = text.replace("<new.arrivals>", "The occupied cell contains a recent arrival. Still adjusting.")
        else:
            text = text.replace("<cell.status>", f"{occupied} cells are currently occupied. Eyes track your movement.")
            text = text.replace("<new.arrivals>", "Several specimens await processing. Some appear resigned. Some still struggle.")
        
        return text


class PrivateCollection(MuseumRoomBase):
    """The Curator's most prized acquisitions."""
    wing = AttributeProperty(default="Basement")
    restricted = AttributeProperty(default=True)
    
    # Collection tracking  
    collection_items = AttributeProperty(default=list)
    favorites = AttributeProperty(default=list)
    
    def at_object_creation(self):
        super().at_object_creation()
        self.lighting = "warm"
        self.db.desc = """
|yThe Private Collection|n

This is different from the cells. This is not holding. This is display.

The chamber is warm, well-lit, almost comfortable. Display cases of 
various sizes occupy carefully planned positions—some small enough for 
jewelry, some large enough for... larger acquisitions.

<display.case_main>

These are the Curator's favorites. The specimens who earned a permanent 
place. Who proved themselves valuable enough to keep, interesting enough 
to preserve, beautiful enough to display.

<display.living_exhibits>

Some cases hold preserved specimens. Others hold living ones. The living 
ones are maintained in perfect comfort, their every need met, their 
existence devoted to being |yowned|n.

<collection.status>

|rThe Curator visits this room often.
Touching, admiring, appreciating.
Being appreciated in return.|n

<display.favorite>

A velvet settee offers seating for the Curator—or for special guests 
invited to view the collection. To perhaps... contribute to it.

|xEvery specimen here chose this, eventually.
Some chose quickly. Some took time.
The Curator is patient.|n
"""
        self.add_display(
            "case_main",
            "Central cases await worthy additions to the permanent collection.",
            "The central display holds the collection's crown jewels—specimens so perfect they've transcended their original nature."
        )
        self.add_display(
            "living_exhibits",
            "Life support cases hum quietly, prepared for living additions.",
            "Living exhibits occupy their cases with the calm of long acceptance. They are cared for. They are owned. They are content."
        )
        self.add_display(
            "favorite",
            "A premium display position awaits something truly special.",
            "The Curator's current favorite occupies the place of honor—always visible, always appreciated, always reminded of their status."
        )
    
    def process_shortcodes(self, text: str, looker=None) -> str:
        text = super().process_shortcodes(text, looker)
        
        count = len(self.collection_items)
        if count == 0:
            text = text.replace("<collection.status>", "The collection is young, but growing. There is room for more.")
        else:
            text = text.replace("<collection.status>", f"The collection contains {count} prized specimens, each with a story of acquisition.")
        
        return text


class ProcessingRoom(MuseumRoomBase):
    """Where new specimens are prepared."""
    wing = AttributeProperty(default="Basement")
    restricted = AttributeProperty(default=True)
    
    # Current activity
    currently_processing = AttributeProperty(default=None)
    processing_stage = AttributeProperty(default="")
    
    def at_object_creation(self):
        super().at_object_creation()
        self.lighting = "clinical"
        self.db.desc = """
|rProcessing Room|n

Clinical. Efficient. Everything in its place. This is where new 
acquisitions become specimens, where the wild becomes curated.

<processing.current>

Equipment lines the walls:
  - Examination tables with restraint points
  - Measurement tools of various precisions
  - Cataloguing systems and specimen tags
  - Preservation equipment for those who've reached their end
  - |yConditioning equipment for those who haven't|n

<display.equipment_ready>

The room is designed for complete documentation:
  - Physical measurements
  - Magical potential assessment
  - Behavioral observation
  - |rCompliance training introduction|n

<processing.notes>

A whiteboard tracks specimens in various stages:
  "INTAKE → ASSESSMENT → CLASSIFICATION → ASSIGNMENT"

Some arrows point to "Collection." Some point to "Breeding Program."
Some point to "Trade/Sale." Some arrows point to nothing, their 
destinations removed.

|xThe Curator personally handles special acquisitions.
Everything else is processed by trained staff.
The difference is significant.|n
"""
        self.add_display(
            "equipment_ready",
            "Processing equipment is cleaned and ready for new arrivals.",
            "Current equipment in use shows signs of recent activity. Cleaned, but not quite clean enough to hide purpose."
        )
    
    def process_shortcodes(self, text: str, looker=None) -> str:
        text = super().process_shortcodes(text, looker)
        
        if self.currently_processing:
            text = text.replace(
                "<processing.current>", 
                f"A specimen is currently being processed. Stage: {self.processing_stage}. Observation is permitted."
            )
            text = text.replace(
                "<processing.notes>",
                "Notes on the current specimen fill a clipboard. Measurements, observations, recommendations."
            )
        else:
            text = text.replace("<processing.current>", "The tables are empty, recently cleaned, awaiting the next arrival.")
            text = text.replace("<processing.notes>", "No current processing notes. The Curator's schedule determines when this room sees use.")
        
        return text


class CuratorQuarters(MuseumRoomBase):
    """The Curator's private chambers."""
    wing = AttributeProperty(default="Basement")
    restricted = AttributeProperty(default=True)
    
    # Guest tracking
    current_guest = AttributeProperty(default=None)
    guest_status = AttributeProperty(default="")
    
    def at_object_creation(self):
        super().at_object_creation()
        self.lighting = "warm"
        self.db.desc = """
|yThe Curator's Quarters|n

Private. Intimate. A space that reveals the person behind the position—
or perhaps conceals them more effectively.

The chamber is larger than expected, divided into areas of different 
purpose. A living space with comfortable seating. A study with books 
and research materials. A sleeping area with a bed larger than necessary 
for one.

<curator.presence>

<quarters.guest>

The décor is personal in a way the office isn't. Items with clear 
sentimental value. Gifts from appreciative donors. Mementos of 
memorable acquisitions.

<display.personal_items>

A connected washroom offers privacy. A connected... other room... 
serves different purposes.

|xBeing invited here is significant.
Being invited to stay is more significant.
What happens in the Curator's quarters is between the Curator 
and their guest.|n

<display.bed>

|rYou are in the Curator's most private space.
You are here because the Curator wants you here.
Consider carefully what that means.|n
"""
        self.add_display(
            "personal_items",
            "Personal items fill shelves—mementos of a long life of collecting.",
            "Photographs, preserved flowers, jewelry, small tokens—each tells a story of someone who mattered. Who still matters."
        )
        self.add_display(
            "bed",
            "The bed is made with precision, waiting for its owner's return.",
            "The bed is large, comfortable, currently occupied in ways that suggest the Curator is... busy."
        )
    
    def process_shortcodes(self, text: str, looker=None) -> str:
        text = super().process_shortcodes(text, looker)
        
        if self.current_guest:
            text = text.replace(
                "<quarters.guest>",
                f"The Curator has company. {self.guest_status}"
            )
        else:
            text = text.replace("<quarters.guest>", "The quarters are empty save for you. A rare privilege.")
        
        return text


# =============================================================================
# EXPORTS
# =============================================================================

__all__ = [
    # Base
    "MuseumRoomBase",
    
    # Public Wings
    "MuseumEntrance",
    "MuseumReception",
    "FossilWing",
    "FaunaWing",
    "FloraWing",
    "AquariumWing",
    "Insectarium",
    "ArtGallery",
    "Library",
    "RelicsHall",
    
    # Semi-Private
    "CuratorOffice",
    
    # Basement
    "BasementEntrance",
    "BasementStairs",
    "BasementMain",
    "BreedingChambers",
    "HoldingCells",
    "PrivateCollection",
    "ProcessingRoom",
    "CuratorQuarters",
]
