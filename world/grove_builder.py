"""
Grove Builder - Immersive Edition

Batch build script for The Grove hub area with rich, dynamic descriptions
that respond to time, weather, and season.

Run from Evennia with:
    @py from world.grove_builder import build_grove; build_grove()
"""

from world.builder_utils import (
    create_room,
    create_exit_pair,
    create_door,
    create_realm_gate,
    connect_rooms,
)
from world.museum_builder import build_museum as build_museum_full


# =============================================================================
# ROOM DESCRIPTIONS - Rich, Immersive, Dynamic
# =============================================================================

DESCS = {
    # =========================================================================
    # GATE PLAZA
    # =========================================================================
    
    "gate_plaza_center": """
The heart of The Grove opens before you—a grand plaza of ancient stone, each 
flagstone worn smooth by countless travelers from realms beyond counting. <time.desc>

At the center rises a fountain of impossible beauty: water spirals upward in 
defiance of nature, catching light that seems to come from everywhere and nowhere. 
The spray carries the scent of distant places—pine forests, ocean salt, volcanic 
ash, winter frost—all mingled into something that smells like |ypossibility|n.

<weather.desc>

Three alcoves ring the plaza's edge, each sheltering gates to distant realms. 
You can feel the thrum of magic in the air, a subsonic vibration that makes your 
teeth ache pleasantly. Travelers of every description pass through: mortals with 
wide eyes, elves with knowing smiles, dwarves grumbling about the surface, and 
stranger things that slide past the corner of your vision.

<ambient.activity>

The roots of Yggdrasil are visible here—massive wooden tentacles breaking through 
the stone, alive and somehow aware. They pulse faintly with an inner light, 
connecting this place to all others.""",

    "north_gate_alcove": """
The northern alcove opens like a cathedral to light and hope. <time.desc> Three 
gates shimmer here, their surfaces rippling like vertical pools of captured 
starlight. Golden runes frame each archway, warm to the touch and humming with 
protective magic.

<weather.desc>

The leftmost gate glows with the unmistakable radiance of |yAsgard|n—through its 
surface you glimpse golden spires and rainbow bridges. The center gate breathes 
with the wild green energy of |yVanaheim|n, and you can smell growing things, 
rich soil, the musk of beasts. The rightmost gate shimmers silver-bright: 
|yAlfheim|n, where the light elves dance eternal.

<ambient.activity>

Travelers here tend toward the elegant—Aesir warriors in gleaming armor, Vanir 
druids trailing flower petals, light elves who leave afterimages when they move. 
The air tastes of honey wine and summer.""",

    "east_gate_alcove": """
The eastern alcove crackles with practical energy—these are the gates of makers 
and survivors. <time.desc> Three archways stand here, each radiating a different 
kind of power.

<weather.desc>

The first gate feels |yordinary|n in a way that's almost shocking—through it 
lies |yMidgard|n, the mortal realm, and you can smell exhaust fumes and rain on 
concrete mixed with forest air and ocean spray. The second gate radiates bitter 
cold: |yJotunheim|n, where giants walk and winter never ends. The third burns 
with forge-heat: |yNidavellir|n, where dwarven hammers ring eternal.

<ambient.activity>

The travelers here are working folk—merchants hauling goods between realms, 
dwarven smiths with soot-stained beards, mortals clutching visitor passes with 
white-knuckled hands. The air smells of iron and ice and the particular ozone 
of mortal technology.""",

    "south_gate_alcove": """
The southern alcove feels |rdifferent|n. Heavier. The light doesn't reach as 
far here, and shadows pool in corners that shouldn't have corners. <time.desc> 
Three gates shimmer darkly, their surfaces less like water and more like oil.

<weather.desc>

The leftmost gate radiates heat that makes your skin prickle: |rMuspelheim|n, 
realm of fire, where everything burns forever. The center gate breathes frost 
so cold it hurts to look at: |cNiflheim|n, the primordial ice, older than 
memory. The rightmost gate is simply |xdark|n—|xHelheim|n, where the dead go, 
and from which they rarely return.

<ambient.activity>

Few linger here. Those who pass through tend toward dark cloaks and darker 
purposes—fire giants on diplomatic missions, frost giant traders, and 
occasionally, the silent ones who serve Hela. The air tastes of ash and 
endings.""",

    "gatekeeper_office": """
The office is smaller than it has any right to be, crammed with the accumulated 
detritus of someone who has spent centuries tracking who goes where and why. 
Scrolls overflow from shelves. Ledgers stack precariously on every flat surface. 
Brass instruments of unknown purpose tick and whir in corners.

Maps of all nine realms paper the walls, each one stuck through with pins and 
connected by colored strings in patterns that seem to move when you're not 
looking directly at them. Some pins glow faintly. Some strings vibrate.

A high desk dominates the space, positioned so whoever sits behind it can look 
down on visitors—a deliberate choice. The chair behind it is worn to the shape 
of its occupant. Behind it hangs a sign in neat calligraphy:

    |y"All Gate Incidents Must Be Reported. Eventually."|n

The air smells of old paper, ink, and the particular mustiness of bureaucracy 
that transcends all realms.""",

    # =========================================================================
    # MARKET SQUARE
    # =========================================================================
    
    "market_square": """
Commerce incarnate sprawls before you in glorious chaos. <time.desc> The market 
square is a riot of color and sound, merchant stalls crowding together like 
old friends, their awnings a patchwork quilt stitched from fabrics of nine 
realms.

<weather.desc>

The noise is magnificent—vendors hawking wares in a dozen languages, customers 
haggling with theatrical outrage, coins of a hundred currencies clinking into 
purses. The smells layer impossibly: roasting meat, exotic spices, fresh bread, 
perfumes, leather, and underneath it all the living green scent of the Grove 
itself.

<ambient.activity>

<crowd.desc>

Pathways wind between the stalls like rivers through a canyon, and the flow 
of bodies never quite stops. Pickpockets work the edges (watch your purse). 
Street performers claim corners (watch your heart). And everywhere, |yeverywhere|n, 
the pulse of buying and selling that makes the worlds go round.""",

    "merchant_row_north": """
The northern stretch of merchant row trades chaos for permanence. <time.desc> 
Stone buildings line the street, their facades painted in colors that would 
clash anywhere else but somehow harmonize here. Each shop front is a small 
artwork: hand-carved signs, stained glass windows, displays arranged to 
catch the eye.

<weather.desc>

These are the established merchants—the ones who've been here long enough to 
afford walls and roofs. Their wares trend upscale: enchanted items, rare 
ingredients, custom crafts that take months to complete. The shopkeepers know 
their customers by name and their preferences by heart.

<ambient.activity>

The foot traffic here is different than the market square—less frantic, more 
purposeful. These are buyers who know what they want and where to find it.""",

    "merchant_row_south": """
The southern merchant row curves toward the entertainment district, and you 
can hear faint music from that direction. <time.desc> The shops here are 
practical rather than pretty: tool suppliers, general goods, the everyday 
necessities that every realm-traveler needs.

<weather.desc>

Hand-painted signs advertise their wares without pretense: "ROPE - STRONG" 
and "BAGS - MANY SIZES" and "LIGHTS THAT WORK IN DARK PLACES." The 
shopkeepers here have the weathered look of people who've seen everything 
and aren't impressed by any of it.

<ambient.activity>

This is where experienced travelers shop—the ones who know that a reliable 
rope is worth more than a pretty sword.""",

    "general_store": """
The general store is a marvel of vertical storage. Shelves climb to a ceiling 
lost in shadow, packed with an impossible variety of goods. Bins crowd the 
floor: nails sorted by size, rope coiled by length, candles arranged by burn 
time. Rolling ladders on brass tracks provide access to the upper reaches.

The shopkeeper's counter squats near the door like a guard post, positioned 
for maximum visibility of both customers and the back room. A hand-lettered 
sign hangs prominently:

    |y"You Break It, You Buy It. Or Work It Off."|n

The back wall holds the interesting stuff—items that require asking for, 
things that aren't exactly illegal but aren't exactly encouraged either. 
The shopkeeper's gaze follows browsers like a hawk watching mice.""",

    "tool_shop": """
Metal and wood and honest work. The tool shop smells of oil and sawdust and 
the particular satisfaction of things well-made. Tools hang from every surface: 
axes arranged by weight, hammers by purpose, saws by tooth count. Bins hold 
nails, screws, brackets, fasteners for every conceivable application.

A workbench runs along one wall, scarred by years of demonstrations and 
repairs. The shopkeeper here can tell you exactly which tool you need for 
any job, and probably has an opinion about how you should do it. Several 
opinions, actually.

Handwritten notes are tacked everywhere: "SHARPEN BEFORE RETURNING," "ASK 
ABOUT MAINTENANCE," and mysteriously, "NOT FOR USE ON THURSDAYS (you know 
who you are)."

<ambient.activity>""",

    "clothier": """
Fabric cascades everywhere in this shop like frozen waterfalls of color. 
Bolts of cloth line the walls—silks from Alfheim, wools from Vanaheim, 
mysterious textiles from places that don't advertise. Finished garments 
hang from racks, ranging from practical traveling clothes to gowns that 
seem to be made of captured starlight.

A raised platform with mirrors dominates one corner—the fitting area, 
where pins and measuring tapes hover in the air on their own, ready for 
use. The clothier here can outfit you for any realm, any climate, any 
social occasion, and will have opinions about all of them.

Mannequins model the latest styles from each realm. Some of the mannequins 
blink, but that's probably just the light.""",

    "imports_shop": """
The exotic imports shop is half museum, half merchant's den. Display cases 
hold items from every corner of the nine realms, each one tagged with 
origin, properties, and price. Some tags include warnings. Some warnings 
include sketches of what happened to the last person who ignored them.

The air is thick with competing scents: Muspelheim incense, Niflheim 
crystals (they smell like winter), Jotunheim furs, Alfheim perfumes. 
Glass cases protect the truly valuable items, their locks inscribed 
with runes that glow faintly.

The proprietor here trades in information as much as goods. Buy something 
interesting, and you might learn where it came from, who made it, and 
what it's really for.""",

    # =========================================================================
    # SERVICES DISTRICT
    # =========================================================================
    
    "services_hub": """
The services district offers something rarer than goods: expertise. <time.desc> 
Buildings here announce their purpose with carved signs and professional 
discretion. The foot traffic is purposeful—people with problems seeking 
solutions.

<weather.desc>

A small plaza anchors the district, its benches occupied by waiting clients 
and the occasional messenger running between offices. Notice boards cluster 
near the center, thick with advertisements, job postings, and warnings.

<ambient.activity>

The atmosphere is businesslike but not unfriendly. These are the people 
who keep the Grove running—the fixers, the advisors, the specialists in 
problems you didn't know could be solved.""",

    "bank": """
The Realms Exchange Bank radiates stability from every polished surface. 
Marble columns. Brass fixtures. The kind of quiet that only vast amounts 
of wealth can buy.

Teller windows line one wall, each staffed by professionals whose 
neutral expressions reveal nothing. Behind them, vault doors of dwarvish 
make stand as testament to security. Private consultation rooms branch 
off for those with complicated needs.

A sign lists exchange rates between realm currencies, updated in real 
time by mechanisms that tick and whir. Another sign, smaller but more 
prominently placed, reads: "All Transactions Final. All Debts Remembered.""",

    "post_office": """
The Realms Postal Service office is organized chaos. Bins and slots cover 
every wall, sorted by realm, urgency, and method of delivery. Packages 
pile in corners. A massive board tracks active deliveries with pins and 
strings in patterns only the postmaster understands.

The counter is fortified like a small castle—decades of learning that 
some deliveries upset their recipients. Speaking tubes connect to 
unknown destinations. A small door leads to the aviary where messenger 
birds wait.

Signs explain rates and restrictions: "No Live Explosives," "Corpses 
Require Special Handling," and "We Are Not Responsible For Temporal 
Displacement During Transit.""",

    "insurance_office": """
The insurance office has the careful neutrality of a place that's seen 
every possible disaster and priced them all. Desks sit in neat rows, 
each occupied by an assessor reviewing claims. The walls are lined 
with filing cabinets that seem to extend further back than the building 
should allow.

Customers wait in uncomfortable chairs, clutching forms and anxious 
expressions. The forms are comprehensive—they ask questions about 
events that haven't happened yet, in some cases.

A prominent display lists common claims and their typical payouts. 
Another display, smaller and off to the side, lists excluded events: 
"Acts of Gods," "Acts of Ragnarok," "Paradoxes," and simply, "Loki.""",

    "notice_board_area": """
The notice board plaza serves as the Grove's nervous system—information 
flows through here like blood through a heart. <time.desc> Boards of 
various sizes cluster together, each dedicated to a different purpose.

<weather.desc>

The job board is always crowded, postings layered so thick you have to 
peel them back to read. The housing board is nearly as busy. The "seeking" 
board handles everything from lost items to missing persons to stranger 
requests best not examined closely.

<ambient.activity>

Messengers dart between boards, pinning new notices and removing old ones. 
Job seekers study postings with desperate hope. And occasionally, someone 
finds exactly what they were looking for.""",

    # =========================================================================
    # RESIDENTIAL AREAS
    # =========================================================================
    
    "residential_main": """
The residential streets of the Grove unfold in comfortable domesticity. 
<time.desc> Homes line the pathways in architectural anarchy—every realm's 
building style represented, somehow coexisting peacefully.

<weather.desc>

Asgardian longhouses neighbor Vanir tree-homes neighbor dwarvish stone 
bunkers. Mortal-style cottages sit beside elvish spirals of living wood. 
Each home reflects its owner's origin, but all share the same address: 
the Grove.

<ambient.activity>

Gardens spill between buildings. Children play in small parks. Neighbors 
chat across fences. The air smells of cooking from nine different 
cuisines. It's not quite any realm, but it's home to all of them.""",

    "residential_north": """
The northern residential quarter trends upscale. <time.desc> Larger homes 
sit back from the street behind actual gardens, the kind of real estate 
that says the owner has been here a while and plans to stay.

<weather.desc>

The architecture here tends toward the classical—Asgardian influences 
are strong, all clean lines and noble proportions. But even here, 
Grove chaos asserts itself: a dwarvish bunker sits between two golden 
halls, stubbornly practical among the pretty.

<ambient.activity>

The residents here nod politely rather than wave. Their servants do the 
shopping. But on quiet evenings, you might catch them on their porches, 
watching the sky like everyone else.""",

    "residential_south": """
The southern residential quarter is where the newer arrivals land—cheaper 
rents, smaller spaces, more noise. <time.desc> Buildings here stack and 
crowd, creative uses of limited space.

<weather.desc>

The architecture is practical rather than pretty: converted warehouses, 
multi-family dwellings, rooms rented by the week. But the community is 
strong—neighbors watch out for neighbors, and everyone knows everyone's 
business.

<ambient.activity>

Street vendors work the corners. Kids play in the streets. The smells of 
a dozen different cuisines compete. It's crowded and loud and absolutely 
alive.""",

    # =========================================================================
    # ENTERTAINMENT DISTRICT
    # =========================================================================
    
    "entertainment_hub": """
The entertainment district never really sleeps. <time.desc> Music drifts 
from multiple venues, different styles competing and occasionally 
harmonizing. Light spills from windows and doorways. Laughter echoes.

<weather.desc>

Taverns and pleasure houses and gaming halls cluster together like old 
friends with bad habits. Street performers work the spaces between. The 
air smells of spilled ale, exotic smoke, perfume, and possibility.

<ambient.activity>

<crowd.desc>

This is where the Grove comes to forget—to drink away sorrows, to gamble 
away regrets, to find company of various kinds. By day it's sleepy; by 
night it's the beating heart of Grove social life.""",

    "tavern_main": """
The Wanderer's Rest has been serving drinks longer than most realms have 
had names. <time.desc> The main room sprawls comfortably, all worn wood 
and warm light. A fire crackles in a massive hearth. Tables fill every 
available space, each with its own character.

<weather.desc>

The bar itself is a work of art—dark wood polished by countless elbows, 
brass fixtures green with age, bottles arranged in patterns that might 
be decorative or might be ritual. The bartender has seen everything 
twice and is surprised by nothing.

<ambient.activity>

The crowd is the usual Grove mix: travelers unwinding, locals solving 
the world's problems, strangers becoming friends over shared drinks. 
A bard plays in the corner, taking requests.""",

    "tavern_private": """
The private rooms of the Wanderer's Rest offer something precious: 
discretion. Walls here are thick—spelled against eavesdropping, 
according to the management. Doors lock from the inside.

Each room is furnished for comfort and conversation: plush seating, 
low tables, indirect lighting. A bell pull summons service. A 
speaking tube allows orders without opening the door.

These rooms have seen conspiracies and contracts, confessions and 
proposals, and a few things best not mentioned. The staff sees 
nothing, hears nothing, remembers nothing. That's included in the 
rental price.""",

    "tavern_back": """
The back room of the Wanderer's Rest is where the serious drinking 
happens. The lighting is dimmer here, the music doesn't reach, and 
the customers prefer it that way.

Booths line the walls, each with high backs for privacy. The tables 
are scarred with knife marks and burn rings and what might be ancient 
runes. The drinks served here are stronger than the main room, and 
the prices are... negotiable, depending on what you're buying.

The bartender here is not the same as out front. This one has seen 
things. You can tell by the eyes.""",

    "gambling_hall": """
The House of Chance welcomes all who believe in luck. <time.desc> 
Gaming tables fill the main floor: cards, dice, wheels, and stranger 
games from realms where probability works differently.

<weather.desc>

The lighting is carefully designed—bright enough to see your cards, 
dim enough to hide your tells. Crystal chandeliers cast rainbow 
fragments. Somewhere, always, a jackpot sound rings out, drawing 
eyes and hopes.

<ambient.activity>

House dealers run the tables with professional neutrality. Servers 
circulate with drinks (the first one's always free). In the corners, 
money lenders wait with patient smiles. The house always wins, but 
everyone believes they'll be the exception.""",

    "bathhouse": """
The Grove Bathhouse offers the ultimate luxury: time to do nothing. 
<time.desc> Steam drifts through the air, carrying the scent of 
mineral-rich water and expensive oils. The architecture blends every 
realm's bathing tradition into something new.

<weather.desc>

Multiple pools at multiple temperatures occupy the main hall—from 
near-freezing plunges to waters that steam. Private bathing rooms 
branch off for those who prefer solitude. Massage tables line a 
gallery where trained hands wait.

The dress code is simple: none. The Grove Bathhouse considers all 
bodies acceptable and interesting. The only rule is relaxation.""",

    "inn_lobby": """
The Crossroads Inn caters to travelers seeking more than a tavern 
bench. The lobby is designed to impress without intimidating: 
comfortable seating, warm lighting, the discrete presence of staff 
who anticipate needs.

A reception desk of polished wood anchors the space, attended by 
professionals who've mastered the art of welcoming hospitality. 
A board lists room availability and rates—from modest singles to 
suites that rent by the week.

The inn's reputation rests on two pillars: clean sheets and no 
questions asked. Both are guaranteed.""",

    # =========================================================================
    # NATURAL AREAS
    # =========================================================================
    
    "orchard_main": """
The Grove's orchard is a miracle of impossible botany. <time.desc> 
Trees from every realm grow here side by side: golden apples of 
Asgard next to silver-leafed Alfheim specimens, frost-resistant 
Jotunheim pines beside fire-blooming Muspelheim flowers.

<weather.desc>

Paths wind between the trees, marked with signs identifying each 
species (and appropriate warnings). The air is thick with competing 
perfumes—fruit and flower and the underlying green of growth itself.

<ambient.activity>

Gardeners tend the trees with careful expertise, knowing that some 
require prayer and some require blood sacrifice and some just need 
good mulch. Visitors wander in quiet appreciation, or search for 
specific specimens, or simply escape the bustle of the Grove proper.""",

    "orchard_clearing": """
A clearing opens in the orchard's heart, a circle of grass somehow 
always perfect regardless of season. <time.desc> This is where the 
orchard's caretakers come to rest, where visitors come to think, 
where the trees lean in as if listening.

<weather.desc>

A single ancient stump occupies the center—the remains of something 
vast, its rings too numerous to count. Some say it's a piece of 
Yggdrasil itself, others that it's older still. Either way, it 
radiates peace.

<ambient.activity>

Sound seems muffled here. Time moves strangely. People sit on the 
stump to make wishes, and sometimes the wishes come true.""",

    "waterfront_main": """
The Grove's waterfront shouldn't exist—there's no ocean nearby, no 
river, nothing to explain the stretch of beach and dock and water 
that nonetheless spreads before you. <time.desc> The water comes 
from somewhere and goes to somewhere else, and wise residents don't 
ask too many questions.

<weather.desc>

A small beach of golden sand curves along the water's edge. Docks 
extend into water too deep to see bottom. Boats of various designs 
bob at anchor—some sailboats, some rowboats, some that seem to move 
without visible means.

<ambient.activity>

The waterfront draws those seeking peace: fishers working the 
mysterious waters, swimmers braving the unknown currents, and 
dreamers watching the horizon for ships that might come from 
anywhere at all.""",

    "waterfront_docks": """
The docks extend over water that's deeper than it has any right 
to be. <time.desc> Boats cluster here in maritime democracy: 
expensive yachts beside working vessels beside things that might 
not be boats at all.

<weather.desc>

Each dock is marked with symbols indicating what kind of vessel 
may moor there. Some symbols are familiar. Some are not. One 
dock is marked only with a black flag, and locals avoid it 
after dark.

<ambient.activity>

Dock workers load and unload cargo that doesn't bear close 
inspection. Fishers compare catches. Captains advertise passage 
to destinations that might not be on any map.""",

    # =========================================================================
    # OUTLOOK & OVERLOOK
    # =========================================================================
    
    "overlook_main": """
The overlook rises at the Grove's edge, offering views that shouldn't 
be possible from any single vantage point. <time.desc> From here you 
can see |yeverything|n—the whole Grove spread below like a living map, 
and beyond it, glimpses of all nine realms.

<weather.desc>

Asgard gleams golden in one direction. Niflheim mists another. The 
mortal realm flickers like a dying channel. All of it visible from 
this single spot, as if the Grove sits at the center of everything.

<ambient.activity>

Benches line the overlook for contemplation. Telescopes of dwarvish 
make allow closer views. And everyone who stands here asks the same 
question: how is this possible? No one has a good answer.""",

    "overlook_east": """
The eastern overlook frames the crafting realms with particular 
clarity. <time.desc> From here you can see Midgard's endless variety, 
Nidavellir's deep forges glowing like buried stars, Jotunheim's 
frozen majesty stretching to infinity.

<weather.desc>

The view changes constantly—mortal cities rise and fall in fast 
forward, dwarvish creations emerge from mountain depths, giants 
walk across frozen plains like moving mountains. Time flows 
differently when viewed from here.

<ambient.activity>

Artists come here to paint views that should be impossible. Writers 
come for inspiration. And homesick mortals come to watch their 
world spin on without them.""",

    "overlook_west": """
The western overlook gazes toward the realms of magic and mystery. 
<time.desc> Alfheim shimmers with light that has no source. Vanaheim 
pulses with green life so vibrant it's almost painful. Asgard rises 
in golden spires connected by bridges of rainbow.

<weather.desc>

The beauty here is almost too much—visitors sometimes weep without 
knowing why. The light does things to your eyes, showing colors 
that don't have names, shapes that don't quite fit in your mind.

<ambient.activity>

Elves come here to remember home. Aesir come to see their halls 
from a new angle. And mortals come to understand why the old 
stories called these places heaven.""",
}


# =============================================================================
# DISTRICT BUILDERS
# =============================================================================

def build_gate_plaza() -> dict:
    """Build the Gate Plaza district."""
    rooms = {}
    
    rooms["plaza_center"] = create_room(
        "Gate Plaza",
        "typeclasses.rooms.grove.GatePlazaRoom",
        desc=DESCS["gate_plaza_center"],
    )
    
    rooms["north_alcove"] = create_room(
        "Northern Gate Alcove",
        "typeclasses.rooms.grove.GatePlazaRoom",
        desc=DESCS["north_gate_alcove"],
    )
    
    rooms["east_alcove"] = create_room(
        "Eastern Gate Alcove",
        "typeclasses.rooms.grove.GatePlazaRoom",
        desc=DESCS["east_gate_alcove"],
    )
    
    rooms["south_alcove"] = create_room(
        "Southern Gate Alcove",
        "typeclasses.rooms.grove.GatePlazaRoom",
        desc=DESCS["south_gate_alcove"],
    )
    
    rooms["gatekeeper_office"] = create_room(
        "Gatekeeper's Office",
        "typeclasses.rooms.grove.GroveIndoor",
        desc=DESCS["gatekeeper_office"],
    )
    
    # Connect rooms
    create_exit_pair(
        rooms["plaza_center"], rooms["north_alcove"],
        "north", "south", ["n"], ["s"]
    )
    create_exit_pair(
        rooms["plaza_center"], rooms["east_alcove"],
        "east", "west", ["e"], ["w"]
    )
    create_exit_pair(
        rooms["plaza_center"], rooms["south_alcove"],
        "southwest", "northeast", ["sw"], ["ne"]
    )
    
    create_door(
        rooms["plaza_center"], rooms["gatekeeper_office"],
        "office door", "door", ["office"], ["out"]
    )
    
    return rooms


def build_market_square() -> dict:
    """Build the Market Square district."""
    rooms = {}
    
    rooms["market_center"] = create_room(
        "Market Square",
        "typeclasses.rooms.grove.MarketRoom",
        desc=DESCS["market_square"],
    )
    
    rooms["north_row"] = create_room(
        "Merchant Row - North",
        "typeclasses.rooms.grove.MarketRoom",
        desc=DESCS["merchant_row_north"],
    )
    
    rooms["south_row"] = create_room(
        "Merchant Row - South",
        "typeclasses.rooms.grove.MarketRoom",
        desc=DESCS["merchant_row_south"],
    )
    
    rooms["general_store"] = create_room(
        "General Store",
        "typeclasses.rooms.grove.ShopRoom",
        desc=DESCS["general_store"],
    )
    
    rooms["tool_shop"] = create_room(
        "Tool Shop",
        "typeclasses.rooms.grove.ShopRoom",
        desc=DESCS["tool_shop"],
    )
    
    rooms["clothier"] = create_room(
        "Clothier",
        "typeclasses.rooms.grove.ShopRoom",
        desc=DESCS["clothier"],
    )
    
    rooms["imports"] = create_room(
        "Exotic Imports",
        "typeclasses.rooms.grove.ShopRoom",
        desc=DESCS["imports_shop"],
    )
    
    # Connect rooms
    create_exit_pair(
        rooms["market_center"], rooms["north_row"],
        "north", "south", ["n"], ["s"]
    )
    create_exit_pair(
        rooms["market_center"], rooms["south_row"],
        "south", "north", ["s"], ["n"]
    )
    
    create_door(
        rooms["north_row"], rooms["general_store"],
        "general store", "out", ["store", "general"], ["out"]
    )
    create_door(
        rooms["north_row"], rooms["tool_shop"],
        "tool shop", "out", ["tools", "tool"], ["out"]
    )
    create_door(
        rooms["south_row"], rooms["clothier"],
        "clothier", "out", ["clothes", "clothier"], ["out"]
    )
    create_door(
        rooms["south_row"], rooms["imports"],
        "imports shop", "out", ["imports", "exotic"], ["out"]
    )
    
    return rooms


def build_services() -> dict:
    """Build the Services district."""
    rooms = {}
    
    rooms["hub"] = create_room(
        "Services District",
        "typeclasses.rooms.grove.ServicesRoom",
        desc=DESCS["services_hub"],
    )
    
    rooms["bank"] = create_room(
        "Realms Exchange Bank",
        "typeclasses.rooms.grove.GroveIndoor",
        desc=DESCS["bank"],
    )
    
    rooms["post"] = create_room(
        "Realms Postal Service",
        "typeclasses.rooms.grove.GroveIndoor",
        desc=DESCS["post_office"],
    )
    
    rooms["insurance"] = create_room(
        "Realms Insurance",
        "typeclasses.rooms.grove.GroveIndoor",
        desc=DESCS["insurance_office"],
    )
    
    rooms["notices"] = create_room(
        "Notice Board Plaza",
        "typeclasses.rooms.grove.ServicesRoom",
        desc=DESCS["notice_board_area"],
    )
    
    # Connect rooms
    create_exit_pair(
        rooms["hub"], rooms["notices"],
        "east", "west", ["e"], ["w"]
    )
    
    create_door(
        rooms["hub"], rooms["bank"],
        "bank", "out", ["bank"], ["out"]
    )
    create_door(
        rooms["hub"], rooms["post"],
        "post office", "out", ["post", "postal"], ["out"]
    )
    create_door(
        rooms["notices"], rooms["insurance"],
        "insurance office", "out", ["insurance"], ["out"]
    )
    
    return rooms


def build_residential() -> dict:
    """Build the Residential district."""
    rooms = {}
    
    rooms["main"] = create_room(
        "Residential Quarter",
        "typeclasses.rooms.grove.ResidentialStreet",
        desc=DESCS["residential_main"],
    )
    
    rooms["north"] = create_room(
        "Residential Quarter - North",
        "typeclasses.rooms.grove.ResidentialStreet",
        desc=DESCS["residential_north"],
    )
    
    rooms["south"] = create_room(
        "Residential Quarter - South",
        "typeclasses.rooms.grove.ResidentialStreet",
        desc=DESCS["residential_south"],
    )
    
    # Connect rooms
    create_exit_pair(
        rooms["main"], rooms["north"],
        "north", "south", ["n"], ["s"]
    )
    create_exit_pair(
        rooms["main"], rooms["south"],
        "south", "north", ["s"], ["n"]
    )
    
    return rooms


def build_entertainment() -> dict:
    """Build the Entertainment district."""
    rooms = {}
    
    rooms["hub"] = create_room(
        "Entertainment District",
        "typeclasses.rooms.grove.TavernRoom",
        desc=DESCS["entertainment_hub"],
    )
    
    rooms["tavern_main"] = create_room(
        "The Wanderer's Rest",
        "typeclasses.rooms.grove.TavernRoom",
        desc=DESCS["tavern_main"],
    )
    
    rooms["tavern_private"] = create_room(
        "Private Rooms",
        "typeclasses.rooms.grove.TavernRoom",
        desc=DESCS["tavern_private"],
    )
    
    rooms["tavern_back"] = create_room(
        "Back Room",
        "typeclasses.rooms.grove.TavernRoom",
        desc=DESCS["tavern_back"],
    )
    
    rooms["gambling"] = create_room(
        "House of Chance",
        "typeclasses.rooms.grove.GamblingRoom",
        desc=DESCS["gambling_hall"],
    )
    
    rooms["bathhouse"] = create_room(
        "Grove Bathhouse",
        "typeclasses.rooms.grove.BathhouseRoom",
        desc=DESCS["bathhouse"],
    )
    
    rooms["inn"] = create_room(
        "Crossroads Inn - Lobby",
        "typeclasses.rooms.grove.InnRoom",
        desc=DESCS["inn_lobby"],
    )
    
    # Connect rooms
    create_door(
        rooms["hub"], rooms["tavern_main"],
        "tavern door", "out", ["tavern", "wanderer"], ["out"]
    )
    create_exit_pair(
        rooms["tavern_main"], rooms["tavern_private"],
        "private", "common", ["private"], ["common", "main"]
    )
    create_exit_pair(
        rooms["tavern_main"], rooms["tavern_back"],
        "back", "front", ["back"], ["front", "main"]
    )
    
    create_door(
        rooms["hub"], rooms["gambling"],
        "gaming hall", "out", ["gambling", "games", "house"], ["out"]
    )
    create_door(
        rooms["hub"], rooms["bathhouse"],
        "bathhouse", "out", ["bath", "bathhouse"], ["out"]
    )
    create_door(
        rooms["hub"], rooms["inn"],
        "inn", "out", ["inn", "crossroads"], ["out"]
    )
    
    return rooms


def build_orchard() -> dict:
    """Build the Orchard area."""
    rooms = {}
    
    rooms["main"] = create_room(
        "The Orchard",
        "typeclasses.rooms.grove.OrchardRoom",
        desc=DESCS["orchard_main"],
    )
    
    rooms["clearing"] = create_room(
        "Orchard Clearing",
        "typeclasses.rooms.grove.OrchardRoom",
        desc=DESCS["orchard_clearing"],
    )
    
    # Connect rooms
    create_exit_pair(
        rooms["main"], rooms["clearing"],
        "clearing", "path", ["clearing", "center"], ["path", "out"]
    )
    
    return rooms


def build_waterfront() -> dict:
    """Build the Waterfront area."""
    rooms = {}
    
    rooms["main"] = create_room(
        "Waterfront",
        "typeclasses.rooms.grove.WaterfrontRoom",
        desc=DESCS["waterfront_main"],
    )
    
    rooms["docks"] = create_room(
        "The Docks",
        "typeclasses.rooms.grove.WaterfrontRoom",
        desc=DESCS["waterfront_docks"],
    )
    
    # Connect rooms
    create_exit_pair(
        rooms["main"], rooms["docks"],
        "docks", "beach", ["dock", "docks"], ["beach", "shore"]
    )
    
    return rooms


def build_overlook() -> dict:
    """Build the Overlook area."""
    rooms = {}
    
    rooms["main"] = create_room(
        "The Overlook",
        "typeclasses.rooms.grove.OverlookRoom",
        desc=DESCS["overlook_main"],
    )
    
    rooms["east"] = create_room(
        "Eastern Overlook",
        "typeclasses.rooms.grove.OverlookRoom",
        desc=DESCS["overlook_east"],
    )
    
    rooms["west"] = create_room(
        "Western Overlook",
        "typeclasses.rooms.grove.OverlookRoom",
        desc=DESCS["overlook_west"],
    )
    
    # Connect rooms
    create_exit_pair(
        rooms["main"], rooms["east"],
        "east", "west", ["e"], ["w"]
    )
    create_exit_pair(
        rooms["main"], rooms["west"],
        "west", "east", ["w"], ["e"]
    )
    
    return rooms


# =============================================================================
# MAIN BUILD FUNCTION
# =============================================================================

def build_grove() -> dict:
    """
    Build the entire Grove hub area.
    
    Returns dict of all created rooms organized by district.
    """
    # Build museum first (since grove_builder imports it)
    build_museum_full()
    
    all_rooms = {}
    
    # Build each district
    all_rooms["gate_plaza"] = build_gate_plaza()
    all_rooms["market"] = build_market_square()
    all_rooms["services"] = build_services()
    all_rooms["residential"] = build_residential()
    all_rooms["entertainment"] = build_entertainment()
    all_rooms["orchard"] = build_orchard()
    all_rooms["waterfront"] = build_waterfront()
    all_rooms["overlook"] = build_overlook()
    
    # Connect districts
    # Plaza to Market
    create_exit_pair(
        all_rooms["gate_plaza"]["plaza_center"],
        all_rooms["market"]["market_center"],
        "market", "plaza",
        ["market"], ["plaza", "gates"]
    )
    
    # Market to Services
    create_exit_pair(
        all_rooms["market"]["south_row"],
        all_rooms["services"]["hub"],
        "services", "market",
        ["services"], ["market"]
    )
    
    # Services to Residential
    create_exit_pair(
        all_rooms["services"]["hub"],
        all_rooms["residential"]["main"],
        "residential", "services",
        ["residential", "homes"], ["services"]
    )
    
    # Market to Entertainment
    create_exit_pair(
        all_rooms["market"]["south_row"],
        all_rooms["entertainment"]["hub"],
        "entertainment", "market",
        ["entertainment", "tavern"], ["market"]
    )
    
    # Residential to Orchard
    create_exit_pair(
        all_rooms["residential"]["north"],
        all_rooms["orchard"]["main"],
        "orchard", "residential",
        ["orchard", "trees"], ["residential", "homes"]
    )
    
    # Residential to Waterfront
    create_exit_pair(
        all_rooms["residential"]["south"],
        all_rooms["waterfront"]["main"],
        "waterfront", "residential",
        ["water", "beach"], ["residential", "homes"]
    )
    
    # Orchard to Overlook
    create_exit_pair(
        all_rooms["orchard"]["clearing"],
        all_rooms["overlook"]["main"],
        "overlook", "orchard",
        ["overlook", "view"], ["orchard", "trees"]
    )
    
    # Calculate totals
    total_rooms = sum(len(district) for district in all_rooms.values())
    
    print(f"Grove built successfully!")
    print(f"Districts: {len(all_rooms)}")
    print(f"Total rooms: {total_rooms}")
    
    return all_rooms


# =============================================================================
# INDIVIDUAL EXPORTS
# =============================================================================

__all__ = [
    "build_grove",
    "build_gate_plaza",
    "build_market_square",
    "build_services",
    "build_residential",
    "build_entertainment",
    "build_orchard",
    "build_waterfront",
    "build_overlook",
]
