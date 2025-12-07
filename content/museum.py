"""
The Museum - Curator's Domain
==============================

The Museum is the Curator's space in the Grove. It houses collections of
artifacts, curiosities, and specimens from across the realms. The Curator
maintains, preserves, and occasionally... acquires new pieces for display.

Structure:
- Public Areas (Foyer, Grand Gallery, Wings)
- Semi-Private (Curator's Office - by appointment)
- Restricted (Archives, Restoration Room)
- Private (Curator's Chambers - invitation only)

The Curator is an NPC that will eventually have API integration,
allowing real interaction and dynamic behavior.
"""

# =============================================================================
# Room Descriptions
# =============================================================================

MUSEUM_ROOMS = {
    "foyer": {
        "key": "Museum Foyer",
        "desc": """
You stand in the entrance hall of the Museum, a space of quiet grandeur.
Marble floors reflect the soft glow of enchanted lamps. A curved reception
desk of polished mahogany sits to one side, though it appears unmanned.

High walls display rotating featured pieces - this month showcasing a
collection of preserved moth wings under glass, each one more intricate
than the last.

A sign in elegant script reads: |y"Welcome to the Museum. Touch nothing.
The Curator sees everything."|n

Archways lead deeper into the galleries, while the entrance doors open
back to the Grove.
""",
        "area_type": "museum",
        "ambient_sounds": [
            "The soft echo of your footsteps on marble.",
            "A distant clock ticks somewhere in the galleries.",
            "The faint hum of preservation enchantments.",
        ],
    },
    
    "grand_gallery": {
        "key": "Grand Gallery",
        "desc": """
The Grand Gallery stretches before you, a cathedral of curiosity. Vaulted
ceilings disappear into shadow above, while display cases and pedestals
line the walls and fill the space between massive columns.

The collection here spans centuries and realms: ancient weapons behind
enchanted glass, taxidermied creatures frozen in lifelike poses, jewels
that seem to pulse with inner light, and artifacts whose purpose you
cannot begin to guess.

Velvet ropes mark paths between the exhibits. |yA brass plaque reminds
visitors: "Look. Learn. Do not touch."|n

Wings branch off to either side - |cCuriosities|n to the east and 
|cNatural History|n to the west. A door marked |ySTAFF ONLY|n leads north.
""",
        "area_type": "museum",
        "ambient_sounds": [
            "Your reflection moves in a dozen display cases.",
            "Something shifts in one of the displays. Or did it?",
            "The preservation enchantments hum softly.",
            "A moth circles one of the enchanted lamps.",
        ],
    },
    
    "curiosities_wing": {
        "key": "Curiosities Wing",
        "desc": """
This wing houses the stranger pieces of the collection - items that defy
easy categorization. The lighting here is dimmer, more dramatic, casting
long shadows between the displays.

A cabinet of impossible objects catches your eye: a bottle containing a
storm, a mirror that shows reflections of people who aren't there, a
music box that plays memories. Beside it, a display of cursed items
(safely contained) radiates a subtle wrongness.

One corner is dedicated to |rerotica from across the ages|n - tastefully
displayed behind frosted glass for those who seek it out.

The plaques here are more detailed, often including acquisition notes:
|y"Recovered from the ruins of...", "Donated by the estate of...",
"Confiscated from..."|n

Some cards simply read: |x"Origin unknown."|n
""",
        "area_type": "museum",
        "flags": ["adult_content_available"],
        "ambient_sounds": [
            "The cursed items seem to whisper at the edge of hearing.",
            "A music box plays a few notes, then falls silent.",
            "The storm in the bottle flickers with tiny lightning.",
        ],
    },
    
    "natural_history": {
        "key": "Natural History Wing",
        "desc": """
Glass cases line this wing, each containing specimens preserved with
exacting care. The Curator's skill is evident - these creatures look
merely asleep, not dead.

A massive skeleton dominates the center of the room - some ancient beast
with too many joints in its spine. Around it, smaller displays showcase
flora and fauna from across the realms: luminescent mushrooms, preserved
slimes, crystallized insects, and plants that shouldn't exist.

One alcove is dedicated to |ytransformation specimens|n - before and after
examples of those affected by curses, potions, and wild magic. The
preservation work here is... disturbingly detailed.

A door marked |c"Restoration - Authorized Personnel Only"|n leads to a
back room.
""",
        "area_type": "museum",
        "flags": ["adult_content_available"],
        "ambient_sounds": [
            "You could swear something in one of the cases blinked.",
            "The luminescent mushrooms pulse gently.",
            "Preservation fluid bubbles softly in a specimen jar.",
        ],
    },
    
    "curators_office": {
        "key": "Curator's Office",
        "desc": """
The Curator's office is a study in controlled authority. Dark wood
paneling absorbs sound, creating an intimate quiet despite the high
ceiling. Bookshelves line the walls, filled with catalogs, research
journals, and acquisition records.

The |ydesk|n dominates the room - a massive piece of furniture that has
witnessed countless negotiations, acquisitions, and... private meetings.
A |yhigh-backed leather chair|n sits behind it, and a |ylower guest chair|n
faces it. A |yvelvet cushion|n sits beside the chair, its purpose clear.

Soft lamplight glints off glass cases containing the Curator's personal
collection - pieces too precious or too dangerous for public display.

This is a space where deals are made and boundaries are established.

|yA brass nameplate on the desk reads simply: "The Curator"|n
""",
        "area_type": "museum",
        "flags": ["semi_private", "adult"],
        "ambient_sounds": [
            "A clock ticks softly on the mantle.",
            "The leather chair creaks slightly.",
            "Pages rustle somewhere, though no one turns them.",
        ],
    },
    
    "archives": {
        "key": "Museum Archives",
        "desc": """
Row upon row of shelving stretches into the shadows, holding centuries
of accumulated knowledge. The air here is cool and dry, controlled by
preservation enchantments that make your skin prickle.

Catalogs document every piece in the collection - acquisition records,
provenance, conditions of display. But there are also other records here:
research notes on transformation effects, documented experiments,
detailed observations of subjects under various... conditions.

A locked cage in one corner contains items deemed too dangerous even
for the restricted areas. The Curator keeps the only key.

|rThis area requires explicit permission to access.|n
""",
        "area_type": "museum",
        "flags": ["restricted", "adult"],
        "ambient_sounds": [
            "Something moves on a high shelf. A rat? Something else?",
            "The preservation enchantments hum at a different pitch here.",
            "Papers rustle as you pass, despite no breeze.",
        ],
    },
    
    "restoration_room": {
        "key": "Restoration Room",
        "desc": """
This clinical space is where the Curator performs... restoration work.

An |yexamination table|n dominates the center of the room, padded and
equipped with adjustable restraints. Cabinets along the walls hold
tools and supplies: brushes and solvents for delicate artifacts,
but also other implements whose purpose requires no imagination.

A |yglass display case|n large enough to hold a person stands in one
corner, currently empty. |yLeash hooks|n line one wall at various heights.
A |ydisplay pedestal|n with soft lighting waits for something - or
someone - to be placed upon it.

The Curator's work here is meticulous. Whether restoring a damaged
artifact or... training a new acquisition... attention to detail is
paramount.

|rThis room is strictly off-limits without the Curator's invitation.|n
""",
        "area_type": "museum",
        "flags": ["restricted", "adult", "bondage"],
        "ambient_sounds": [
            "Restraints clink softly against the examination table.",
            "The lighting adjusts automatically as you move.",
            "A preservation enchantment hums expectantly.",
        ],
    },
    
    "private_chambers": {
        "key": "Curator's Private Chambers",
        "desc": """
Few are invited here. Fewer still leave unchanged.

The Curator's private chambers are luxurious but controlled - dark wood,
deep red fabrics, soft lighting that can be adjusted to any mood. A
massive |yfour-poster bed|n dominates one wall, its ornate carvings hiding
anchor points for those who need... guidance.

Comfortable seating clusters near a fireplace, where intimate
conversations can be held. But the room's true nature reveals itself
in the details: |yleash hooks|n by the bed, a |ykneeling cushion|n in the
corner, a |ydisplay pedestal|n near the window where morning light would
illuminate whatever is placed there.

This is where the Curator lives. Where the Curator plays. Where the
Curator takes what is offered freely - and holds it with absolute care.

The door locks from the inside. Only the Curator holds the key.

|rBy invitation only. What happens here, stays here.|n
""",
        "area_type": "museum",
        "flags": ["private", "adult", "bondage"],
        "ambient_sounds": [
            "The fire crackles softly.",
            "Silk sheets rustle at the slightest movement.",
            "Your heartbeat seems louder here.",
        ],
    },
}


# =============================================================================
# Curator NPC Data
# =============================================================================

CURATOR_NPC = {
    "key": "The Curator",
    "aliases": ["curator"],
    "desc": """
The Curator stands before you - tall, blonde, possessed of a presence that
fills any room. Strong features soften only slightly when something catches
their interest, and right now that something might be you.

They dress impeccably in dark colors - professional but with hints of
something more beneath the surface. A silver chain hangs from their pocket,
and you notice their hands are both elegant and strong.

Their eyes miss nothing. When they focus on you, you feel catalogued,
appraised, and perhaps... selected.

The Curator speaks with quiet authority. They do not ask. They state.
And somehow, you find yourself wanting to comply.
""",
    "personality": {
        "dominant": True,
        "patient": True,
        "precise": True,
        "possessive": True,
        "caring": True,  # Within the dynamic
    },
    "dialogue_style": {
        "direct": True,
        "uses_titles": True,  # "Good girl", etc.
        "physical": True,  # Describes touch, position
        "commanding": True,
    },
}


# =============================================================================
# Furniture Placement
# =============================================================================

MUSEUM_FURNITURE = {
    "curators_office": [
        {"template": "curators_desk", "position": "dominating the room"},
        {"template": "curators_chair", "position": "behind the desk"},
        {"template": "guest_chair_low", "position": "facing the desk"},
        {"template": "kneeling_cushion_curator", "position": "beside the chair"},
        {"template": "artifact_case", "position": "along the walls"},
    ],
    "restoration_room": [
        {"template": "examination_table", "position": "in the center"},
        {"template": "living_display_case", "position": "in the corner"},
        {"template": "display_pedestal", "position": "under a spotlight"},
        {"template": "leash_hook", "position": "along the wall"},
        {"template": "leash_hook", "position": "by the door"},
    ],
    "private_chambers": [
        {"template": "curators_bed", "position": "against the far wall"},
        {"template": "kneeling_cushion_curator", "position": "beside the bed"},
        {"template": "display_pedestal", "position": "by the window"},
        {"template": "leash_hook", "position": "by the bedpost"},
    ],
    "grand_gallery": [
        {"template": "museum_bench", "position": "facing the main display"},
        {"template": "museum_bench", "position": "by the columns"},
        {"template": "velvet_rope", "position": "marking the exhibits"},
    ],
}


# =============================================================================
# Museum Scenes
# =============================================================================

MUSEUM_SCENES = {
    "curator_greeting": {
        "key": "curator_greeting",
        "name": "The Curator's Greeting",
        "entry_text": """
A presence materializes beside you - The Curator, appearing as if from
nowhere, though you suspect they were watching all along.

"Welcome to my Museum." Their voice is warm but carries an undercurrent
of authority. "I trust you'll treat my collection with the respect it
deserves."

Their eyes move over you with clinical precision, assessing.

"Is there something specific you're looking for? Or are you here to
be... browsed?"
""",
        "choices": [
            {
                "key": "looking",
                "text": "Just looking around.",
                "response": """
"Of course. Feel free to explore the public galleries." A slight smile.
"But do remember - the Curator sees everything. If you have... questions
about any of the exhibits, I'm always available."

They pause.

"Some of my most interesting work isn't on public display."
""",
            },
            {
                "key": "curious",
                "text": "What kind of work do you do here?",
                "response": """
"I acquire. I preserve. I display." They gesture at the surrounding
collections. "Some things are fragile and need protection. Some things
are dangerous and need containment. Some things are precious and need...
proper appreciation."

Their gaze returns to you.

"I have a gift for recognizing what things need. And ensuring they get it."
""",
            },
            {
                "key": "interested",
                "text": "You mentioned work that isn't on public display?",
                "response": """
"Did I?" That slight smile again. "How observant of you."

They step closer, and you catch a hint of something subtle - leather,
old paper, something warm underneath.

"There are areas of the Museum reserved for... special guests. By
invitation only, of course. I don't extend such invitations lightly."

A pause.

"But I do extend them."
""",
                "flags": ["shows_interest"],
            },
        ],
        "location_hints": ["museum", "foyer", "gallery"],
    },
    
    "private_invitation": {
        "key": "private_invitation",
        "name": "An Invitation",
        "requirements": {"flag": "shows_interest"},
        "entry_text": """
The Curator finds you again - or perhaps they were never not watching.

"You seem... curious." They produce a small card from their pocket,
elegant script on cream paper. "I find curious people interesting."

They hold the card between two fingers.

"This grants you access to my office. By appointment, of course. I
conduct all business there - acquisitions, negotiations..."

A beat.

"...appraisals."

"Should you wish to be... appraised."
""",
        "choices": [
            {
                "key": "accept",
                "text": "Accept the card.",
                "response": """
Their fingers brush yours as you take the card, and you feel a small
jolt of... something.

"Good." Simple. Final. Pleased.

"Come to my office when you're ready. The door will open for you."

They're gone before you can respond, leaving only the faint warmth
where their fingers touched yours, and a card that seems heavier
than paper should be.
""",
                "effects": {"add_flag": "museum_access"},
            },
            {
                "key": "decline",
                "text": "I'm not sure I'm ready for that.",
                "response": """
"Honesty. Good." No disappointment, just acknowledgment.

"The invitation remains open. I don't rescind such things."

They step back, the professional distance restored.

"Enjoy the public galleries. Perhaps in time, you'll find yourself
ready to see more."

The card disappears back into their pocket, but somehow you know
it still has your name on it.
""",
            },
        ],
    },
}


# =============================================================================
# Resource Nodes (for gathering, if any)
# =============================================================================

MUSEUM_RESOURCES = {
    "curiosities_wing": [
        {
            "key": "discarded notes",
            "type": "search",
            "yields": [
                {"key": "research fragment", "rarity": "common", "weight": 50},
                {"key": "acquisition record", "rarity": "uncommon", "weight": 30},
                {"key": "curator's personal note", "rarity": "rare", "weight": 15},
                {"key": "forbidden knowledge scrap", "rarity": "epic", "weight": 5},
            ],
            "cooldown": 300,
            "scene_chance": 10,
            "scene_pool": ["curator_greeting"],
        },
    ],
}
