"""
Grove Hub Builder
=================

Builds the central Grove hub areas:
- Gate Plaza (realm gates, gatekeepers)
- Town Square (central gathering, fountain)
- Tavern Row (inn, pub, bath house)  
- Residential Quarter (housing access)
- Services Row (crafting, trainers)
- Waterfront (docks, fishing)
- Orchards (foraging within Grove)
- Guild Hall (guilds, job board)

Total: ~35 rooms

Run with: @py from content.grove_hub import build_grove_hub; build_grove_hub()
"""

from evennia import create_object, search_object
from evennia.utils import logger


def get_or_create_room(key, name, typeclass="typeclasses.rooms.Room"):
    """Get existing room or create new one."""
    existing = search_object(key, typeclass="typeclasses.rooms.Room")
    if existing:
        room = existing[0]
        room.key = name
        return room, False
    
    room = create_object(typeclass, key=name)
    room.db.room_key = key
    return room, True


def link_rooms(room1, direction, room2, reverse=None):
    """Create exits between rooms."""
    # Map direction to reverse
    reverse_map = {
        "north": "south", "south": "north",
        "east": "west", "west": "east",
        "up": "down", "down": "up",
        "in": "out", "out": "in",
        "northeast": "southwest", "southwest": "northeast",
        "northwest": "southeast", "southeast": "northwest",
    }
    
    if reverse is None:
        reverse = reverse_map.get(direction, "back")
    
    # Check if exit already exists
    for exit in room1.exits:
        if exit.destination == room2:
            return
    
    # Create exits
    exit1 = create_object(
        "typeclasses.exits.Exit",
        key=direction,
        location=room1,
        destination=room2
    )
    
    exit2 = create_object(
        "typeclasses.exits.Exit",
        key=reverse,
        location=room2,
        destination=room1
    )


def build_gate_plaza():
    """Build the Gate Plaza - realm travel hub."""
    rooms = {}
    
    # Main plaza
    room, created = get_or_create_room(
        "grove_gate_plaza",
        "Gate Plaza"
    )
    room.db.desc = """
|yThe Gate Plaza|n

Nine massive gates stand in a great circle, each a portal to one of the realms of 
Yggdrasil. <weather.desc> <time.desc>

The gates pulse with quiet energy—Midgard's gate of weathered stone, Asgard's gleaming 
gold arch, Helheim's shadowed obsidian portal, and six others, each reflecting their 
realm's nature. Travelers come and go, some purposeful, others clearly arriving by 
accident—gate "malfunctions" are common.

At the center stands the |wGatekeepers' Pavilion|n, where robed figures process 
arrivals and departures. A large |wRealm Board|n displays current conditions in each world.

The plaza bustles with activity—merchants hawking realm-specific goods, travelers 
comparing notes, and the occasional bounty hunter scanning the crowd.
    """.strip()
    room.db.area = "the_grove"
    room.db.room_type = "plaza"
    room.tags.add("safe", category="room_flag")
    room.tags.add("no_combat", category="room_flag")
    rooms["gate_plaza"] = room
    
    # Gatekeepers' Office
    room, created = get_or_create_room(
        "grove_gatekeepers_office",
        "Gatekeepers' Office"
    )
    room.db.desc = """
|yGatekeepers' Office|n

The administrative heart of realm travel. Tall counters divide the space, behind which 
robed Gatekeepers process an endless stream of paperwork. The walls are lined with 
cubbyholes containing scrolls, permits, and documentation.

A |wWaiting Area|n with worn benches sits to one side—some travelers have been here 
a while, their paperwork caught in bureaucratic tangles. The air smells of old paper 
and sealing wax.

Signs list fees, restrictions, and warnings for each realm. One prominent notice reads:
"|rThe Gatekeepers are not responsible for accidental destinations.|n"
    """.strip()
    room.db.area = "the_grove"
    room.tags.add("indoor", category="room_flag")
    rooms["gatekeepers_office"] = room
    
    # Arrivals Hall
    room, created = get_or_create_room(
        "grove_arrivals_hall",
        "Arrivals Hall"
    )
    room.db.desc = """
|yArrivals Hall|n

New arrivals from other realms appear here—sometimes gracefully, sometimes tumbling 
out in confusion. The floor is marked with arrival circles for each gate, glowing 
faintly with residual magic.

Helpful volunteers stand ready with directions, basic supplies, and sympathetic words 
for those who didn't intend to arrive. A |wNotice Board|n lists current events, 
warnings, and opportunities.

The hall connects to the main plaza through a grand archway.
    """.strip()
    room.db.area = "the_grove"
    room.tags.add("indoor", category="room_flag")
    rooms["arrivals_hall"] = room
    
    # Link rooms
    link_rooms(rooms["gate_plaza"], "north", rooms["gatekeepers_office"], "south")
    link_rooms(rooms["gate_plaza"], "east", rooms["arrivals_hall"], "west")
    
    return rooms


def build_town_square():
    """Build Town Square - central gathering area."""
    rooms = {}
    
    # Main Square
    room, created = get_or_create_room(
        "grove_town_square",
        "Town Square"
    )
    room.db.desc = """
|yTown Square|n

The heart of the Grove. A great fountain dominates the center, water cascading from 
a statue of Yggdrasil itself—the World Tree rendered in bronze and crystal. 
<weather.desc>

Cobblestone paths radiate outward to the various districts. Benches ring the fountain, 
occupied by residents chatting, people-watching, or simply enjoying the eternal 
pleasant weather of the Grove.

A large |wNotice Board|n displays community announcements, event schedules, and the 
occasional "missing person" poster. Street performers sometimes gather here, their 
music drifting across the square.

<time.desc>
    """.strip()
    room.db.area = "the_grove"
    room.db.room_type = "plaza"
    room.tags.add("safe", category="room_flag")
    rooms["town_square"] = room
    
    # The Wishing Well
    room, created = get_or_create_room(
        "grove_wishing_well",
        "The Wishing Well"
    )
    room.db.desc = """
|yThe Wishing Well|n

A quaint stone well sits in a small garden off the main square. Its waters shimmer 
with an otherworldly light, coins glinting at the bottom from countless wishes.

Legend says that tossing a coin and making a wish might grant a small boon—though 
the well is fickle and sometimes grants wishes in unexpected ways.

A weathered sign reads: "|wOne wish per day. Results not guaranteed. Management 
not responsible for ironic fulfillment.|n"
    """.strip()
    room.db.area = "the_grove"
    rooms["wishing_well"] = room
    
    # Notice Board Square
    room, created = get_or_create_room(
        "grove_notice_board",
        "Notice Board Square"
    )
    room.db.desc = """
|yNotice Board Square|n

A small plaza dominated by a massive wooden |wNotice Board|n, its surface covered 
in layers of postings. Quest notices, job offerings, lost and found, personal ads, 
and cryptic messages compete for space.

Several smaller boards organize content by type:
- |gQuests & Adventures|n - Opportunities for the bold
- |yEmployment|n - Jobs and services needed
- |cCommunity|n - Events, meetings, lost items
- |rWarnings|n - Bounties, dangers, wanted posters

A few people linger, reading listings or adding new ones.
    """.strip()
    room.db.area = "the_grove"
    rooms["notice_board"] = room
    
    link_rooms(rooms["town_square"], "east", rooms["wishing_well"], "west")
    link_rooms(rooms["town_square"], "south", rooms["notice_board"], "north")
    
    return rooms


def build_tavern_row():
    """Build Tavern Row - social and entertainment district."""
    rooms = {}
    
    # Tavern Row Main
    room, created = get_or_create_room(
        "grove_tavern_row",
        "Tavern Row"
    )
    room.db.desc = """
|yTavern Row|n

The entertainment heart of the Grove. Music and laughter spill from doorways along 
this cobblestone street. Lanterns hang from iron posts, casting warm pools of light.

The |wTipsy Sprite|n tavern anchors one end—Big Tom's establishment, known for good 
food and cold drinks. Across the way, the |wGolden Rest Inn|n offers rooms for 
travelers. Further down, the more adventurous can find the |wSteam & Stone Bath House|n 
and whispers of a gambling den somewhere nearby.

The crowd here is lively—travelers swapping tales, locals unwinding, and the 
occasional trouble looking for company.
    """.strip()
    room.db.area = "the_grove"
    rooms["tavern_row"] = room
    
    # Tipsy Sprite Tavern (expanded from existing)
    room, created = get_or_create_room(
        "grove_tipsy_sprite",
        "The Tipsy Sprite Tavern"
    )
    room.db.desc = """
|yThe Tipsy Sprite Tavern|n

Big Tom's establishment—warm, welcoming, and always busy. The bar stretches along 
one wall, bottles of every description lined up behind it. Tables fill the common 
room, from intimate corners to the long communal table by the hearth.

The smell of roasting meat and fresh bread fills the air. A fireplace crackles in 
the corner. The walls are decorated with trophies, curios, and the occasional piece 
of "art" that's clearly a drunken purchase.

|wBig Tom|n himself tends bar, massive arms working the taps while keeping an eye 
on everything. He knows everyone's business and keeps most of it to himself.
    """.strip()
    room.db.area = "the_grove"
    room.tags.add("indoor", category="room_flag")
    room.db.shop_type = "tavern"
    rooms["tipsy_sprite"] = room
    
    # Tavern Back Room
    room, created = get_or_create_room(
        "grove_tavern_backroom",
        "Tipsy Sprite - Back Room"
    )
    room.db.desc = """
|yBack Room|n

A private room in the back of the Tipsy Sprite. Heavy curtains block the view from 
the main tavern. The lighting is dim, the furniture plush, and the atmosphere... 
discreet.

This room can be rented by the hour for private conversations, card games, or 
whatever else patrons need privacy for. Big Tom asks no questions, but his walls 
have ears.
    """.strip()
    room.db.area = "the_grove"
    room.tags.add("indoor", category="room_flag")
    room.tags.add("private", category="room_flag")
    rooms["tavern_backroom"] = room
    
    # Golden Rest Inn
    room, created = get_or_create_room(
        "grove_golden_rest",
        "The Golden Rest Inn"
    )
    room.db.desc = """
|yThe Golden Rest Inn|n

A comfortable inn for travelers who need a proper bed. The lobby features overstuffed 
chairs, a crackling fireplace, and the pleasant hum of quiet conversation.

The |wInnkeeper|n—a matronly woman named Mira—manages the desk, offering rooms at 
reasonable rates. A board displays available rooms and prices.

Stairs lead up to the guest rooms, while a small dining area serves breakfast to 
guests. The inn prides itself on being quiet, clean, and asking no questions about 
what guests do with their privacy.
    """.strip()
    room.db.area = "the_grove"
    room.tags.add("indoor", category="room_flag")
    rooms["golden_rest"] = room
    
    # Bath House
    room, created = get_or_create_room(
        "grove_bath_house",
        "Steam & Stone Bath House"
    )
    room.db.desc = """
|ySteam & Stone Bath House|n

The Grove's premier relaxation establishment. Warm, humid air greets visitors, 
scented with lavender and eucalyptus. The entrance hall offers changing rooms and 
lockers for belongings.

Beyond lie the baths themselves—hot pools, cold plunges, steam rooms, and private 
soaking chambers. Attendants offer massages, grooming services, and refreshments.

A discreet sign notes that the bath house offers both "social bathing" in the main 
pools and "private services" in the back rooms. What happens in the bath house, 
stays in the bath house.
    """.strip()
    room.db.area = "the_grove"
    room.tags.add("indoor", category="room_flag")
    rooms["bath_house"] = room
    
    # Bath House - Main Pool
    room, created = get_or_create_room(
        "grove_bath_main_pool",
        "Main Bathing Pool"
    )
    room.db.desc = """
|yMain Bathing Pool|n

A large, steaming pool dominates this chamber. The water is perfectly hot, maintained 
by subtle magic. Stone benches line the edges, and the ceiling is open to let steam 
escape while filtered sunlight streams in.

Bathers relax in the water, conversation echoing off the tiled walls. Attendants 
circulate with towels, drinks, and oils. The atmosphere is social and relaxed—though 
wandering hands beneath the water are not uncommon.

Steps lead to smaller private pools and steam rooms.
    """.strip()
    room.db.area = "the_grove"
    room.tags.add("indoor", category="room_flag")
    rooms["bath_main_pool"] = room
    
    # Bath House - Private Room
    room, created = get_or_create_room(
        "grove_bath_private",
        "Private Bath Chamber"
    )
    room.db.desc = """
|yPrivate Bath Chamber|n

A small, intimate bathing chamber available for rent. A private pool steams invitingly, 
large enough for two or three to share comfortably. Soft towels, oils, and other 
amenities are provided.

The door locks from the inside. What happens here is entirely the bathers' business.
    """.strip()
    room.db.area = "the_grove"
    room.tags.add("indoor", category="room_flag")
    room.tags.add("private", category="room_flag")
    rooms["bath_private"] = room
    
    # The Gambling Den (hidden-ish)
    room, created = get_or_create_room(
        "grove_gambling_den",
        "The Lucky Coin"
    )
    room.db.desc = """
|yThe Lucky Coin|n

A dimly lit establishment tucked away behind an unmarked door. The air is thick with 
pipe smoke and tension. Card tables fill the main room, dice games in the corners, 
and more exotic wagers in the back.

The house takes a cut of every pot. The rules are simple: play fair or get thrown 
out (or worse). Debts incurred here are real—and the house has ways of collecting.

A heavyset orc named |wFingers|n runs the tables. He got the name from what he takes 
from cheaters.
    """.strip()
    room.db.area = "the_grove"
    room.tags.add("indoor", category="room_flag")
    rooms["gambling_den"] = room
    
    # Link rooms
    link_rooms(rooms["tavern_row"], "north", rooms["tipsy_sprite"], "out")
    link_rooms(rooms["tipsy_sprite"], "back", rooms["tavern_backroom"], "out")
    link_rooms(rooms["tavern_row"], "east", rooms["golden_rest"], "out")
    link_rooms(rooms["tavern_row"], "south", rooms["bath_house"], "out")
    link_rooms(rooms["bath_house"], "in", rooms["bath_main_pool"], "out")
    link_rooms(rooms["bath_main_pool"], "private", rooms["bath_private"], "out")
    link_rooms(rooms["tavern_row"], "alley", rooms["gambling_den"], "out")
    
    return rooms


def build_residential():
    """Build Residential Quarter access."""
    rooms = {}
    
    # Residential Main
    room, created = get_or_create_room(
        "grove_residential",
        "Residential Quarter"
    )
    room.db.desc = """
|yResidential Quarter|n

The quiet streets of the Grove's housing district. Tree-lined paths wind between 
homes of various sizes—from cozy starter cottages to grand estates. Gardens bloom 
in every yard, and the pace here is slower than the bustling market or tavern row.

The |wHousing Office|n sits at the entrance, handling purchases, rentals, and 
complaints about neighbors. Beyond it, streets branch off to different neighborhoods:
|wStarter Row|n for new residents, |wMaple Lane|n for established homes, and 
|wHilltop Estates|n for the wealthy.

Notices remind residents: "|yLock your doors. The Grove Accord protects against 
violence, not theft—or legal claims.|n"
    """.strip()
    room.db.area = "the_grove"
    rooms["residential"] = room
    
    # Housing Office
    room, created = get_or_create_room(
        "grove_housing_office",
        "Housing Office"
    )
    room.db.desc = """
|yHousing Office|n

A tidy office where all housing matters are handled. A counter divides the space, 
behind which clerks process endless paperwork. Maps of available properties cover 
one wall, listings updated daily.

The |wHousing Administrator|n—a fussy gnome named Deeds—handles purchases, upgrades, 
and the occasional eviction. He knows every property in the Grove and takes his 
job very seriously.

Brochures advertise available homes, from modest starter plots to lavish estates. 
A price list hangs prominently.
    """.strip()
    room.db.area = "the_grove"
    room.tags.add("indoor", category="room_flag")
    rooms["housing_office"] = room
    
    # Starter Row
    room, created = get_or_create_room(
        "grove_starter_row",
        "Starter Row"
    )
    room.db.desc = """
|yStarter Row|n

A cheerful street of small, tidy cottages—starter homes for new Grove residents. 
The yards are modest, the houses simple but comfortable. It's where everyone begins.

Neighbors here tend to be friendly, often new to the Grove themselves. The community 
feeling is strong, even if the houses are small.

Paths lead to individual homes, each with a small garden plot and a number on the door.
    """.strip()
    room.db.area = "the_grove"
    rooms["starter_row"] = room
    
    # Maple Lane
    room, created = get_or_create_room(
        "grove_maple_lane",
        "Maple Lane"
    )
    room.db.desc = """
|yMaple Lane|n

A pleasant street of medium-sized homes, shaded by the maple trees that give it its 
name. The houses here are larger than Starter Row—two stories, proper gardens, room 
for guests.

Residents here have established themselves, saved their coin, and upgraded from 
starter cottages. The neighborhood is quieter, more settled.
    """.strip()
    room.db.area = "the_grove"
    rooms["maple_lane"] = room
    
    # Hilltop Estates
    room, created = get_or_create_room(
        "grove_hilltop_estates",
        "Hilltop Estates"
    )
    room.db.desc = """
|yHilltop Estates|n

The wealthy end of the Residential Quarter. Large estates sit on generous plots, 
each with manicured grounds, private gardens, and impressive architecture. The 
view from here overlooks much of the Grove.

Security is better here—private guards, warded gates, and suspicious neighbors who 
notice strangers. The wealthy protect what they have.
    """.strip()
    room.db.area = "the_grove"
    rooms["hilltop_estates"] = room
    
    # Link rooms
    link_rooms(rooms["residential"], "north", rooms["housing_office"], "out")
    link_rooms(rooms["residential"], "east", rooms["starter_row"], "west")
    link_rooms(rooms["residential"], "south", rooms["maple_lane"], "north")
    link_rooms(rooms["maple_lane"], "south", rooms["hilltop_estates"], "north")
    
    return rooms


def build_services():
    """Build Services Row - crafting and trainers."""
    rooms = {}
    
    # Services Row Main
    room, created = get_or_create_room(
        "grove_services_row",
        "Services Row"
    )
    room.db.desc = """
|yServices Row|n

The working heart of the Grove. Workshops, forges, and studios line this busy street, 
the sounds of industry filling the air. Crafters of all types ply their trades here, 
from smiths to tailors to alchemists.

Apprentices run errands between shops. The smell of hot metal, tanning leather, and 
exotic potions mingles in the air. This is where things get made.

|wPublic Workstations|n are available for those who want to craft their own goods—
for a small fee to cover materials and wear.
    """.strip()
    room.db.area = "the_grove"
    rooms["services_row"] = room
    
    # Public Workshop
    room, created = get_or_create_room(
        "grove_workshop",
        "Public Workshop"
    )
    room.db.desc = """
|yPublic Workshop|n

A large, well-equipped workspace open to all Grove residents. Workbenches, tools, 
and basic materials are available for crafters to use.

Stations are organized by craft:
- |wForge|n for smithing and metalwork
- |wWorkbench|n for woodworking and general crafting
- |wAlchemy Table|n for potions and compounds
- |wLoom & Needle|n for tailoring and leatherwork
- |wJeweler's Bench|n for fine detail work

A |wWorkshop Attendant|n monitors the space, answers questions, and ensures nobody 
burns the place down.
    """.strip()
    room.db.area = "the_grove"
    room.tags.add("indoor", category="room_flag")
    room.db.workstation = True
    rooms["workshop"] = room
    
    # Training Hall
    room, created = get_or_create_room(
        "grove_training_hall",
        "Training Hall"
    )
    room.db.desc = """
|yTraining Hall|n

A large open space for combat training. Padded floors, practice weapons, and training 
dummies fill the room. The walls are lined with mirrors and racks of equipment.

|wTrainers|n offer lessons in various combat styles—for a fee. Sparring matches can 
be arranged, though the Grove's peace extends even here: all combat is non-lethal, 
all injuries heal quickly.

A board lists available trainers and their specialties.
    """.strip()
    room.db.area = "the_grove"
    room.tags.add("indoor", category="room_flag")
    rooms["training_hall"] = room
    
    link_rooms(rooms["services_row"], "north", rooms["workshop"], "out")
    link_rooms(rooms["services_row"], "east", rooms["training_hall"], "out")
    
    return rooms


def build_waterfront():
    """Build Waterfront - docks and fishing."""
    rooms = {}
    
    # Waterfront Main
    room, created = get_or_create_room(
        "grove_waterfront",
        "The Waterfront"
    )
    room.db.desc = """
|yThe Waterfront|n

The Grove's lakefront district. Wooden docks extend over calm waters that shimmer 
with an otherworldly light. Small boats bob at their moorings, and the air smells 
of water and fish.

<weather.desc>

Fishing is popular here—the Grove's waters hold unique species found nowhere else. 
Benches along the water's edge provide spots for relaxation, contemplation, or 
quiet conversation.

The |wBoathouse|n rents small craft for those who want to explore the lake. The 
|wFish Market|n buys and sells the day's catch.
    """.strip()
    room.db.area = "the_grove"
    rooms["waterfront"] = room
    
    # Fishing Pier
    room, created = get_or_create_room(
        "grove_fishing_pier",
        "Fishing Pier"
    )
    room.db.desc = """
|yFishing Pier|n

A long wooden pier extending over the water. Anglers line the railings, lines 
dangling into the depths. The waters here are deeper, home to larger and rarer fish.

A tackle shop at the pier's base sells bait, hooks, and rods. Old-timers share tips 
about what's biting and where. Competition can be fierce when rare fish are spotted.

<time.desc> The fishing is said to be best at dawn and dusk.
    """.strip()
    room.db.area = "the_grove"
    room.db.resource_type = "fish"
    rooms["fishing_pier"] = room
    
    # Boathouse
    room, created = get_or_create_room(
        "grove_boathouse",
        "The Boathouse"
    )
    room.db.desc = """
|yThe Boathouse|n

A sturdy wooden building at the water's edge, housing rental boats and water 
equipment. Small rowboats and canoes hang from racks, while larger vessels are 
moored at the attached dock.

The |wBoatmaster|n—a grizzled old sailor named Gill—handles rentals and offers 
advice about the lake's currents and hidden coves. He's seen everything the waters 
hold and shares stories for the price of a drink.
    """.strip()
    room.db.area = "the_grove"
    room.tags.add("indoor", category="room_flag")
    rooms["boathouse"] = room
    
    link_rooms(rooms["waterfront"], "east", rooms["fishing_pier"], "west")
    link_rooms(rooms["waterfront"], "north", rooms["boathouse"], "out")
    
    return rooms


def build_orchards():
    """Build the Orchards - foraging area."""
    rooms = {}
    
    # Orchards Main
    room, created = get_or_create_room(
        "grove_orchards",
        "The Orchards"
    )
    room.db.desc = """
|yThe Orchards|n

Rows of fruit trees stretch across gentle hills, their branches heavy with produce. 
Apple, pear, cherry, and more exotic fruits grow here year-round—the Grove's eternal 
pleasant weather ensures constant harvests.

<weather.desc>

Residents are welcome to pick fruit for personal use. Baskets sit at the orchard's 
edge for gathering. The air is sweet with the scent of ripe fruit and blossoms.

Paths wind between the trees, leading to different groves and quiet spots perfect 
for picnics—or privacy.
    """.strip()
    room.db.area = "the_grove"
    room.db.resource_type = "forage"
    rooms["orchards"] = room
    
    # Flower Gardens
    room, created = get_or_create_room(
        "grove_flower_gardens",
        "Flower Gardens"
    )
    room.db.desc = """
|yFlower Gardens|n

A beautiful garden of cultivated flowers—roses, lilies, exotic blooms from all 
realms. The colors are vibrant, the scents intoxicating.

Butterflies and bees drift between blossoms. The paths are well-maintained, with 
benches placed at scenic viewpoints. This is a popular spot for romantic walks 
and quiet reflection.

Some flowers can be picked; others are marked as "display only." The |wGardener|n 
watches with a careful eye.
    """.strip()
    room.db.area = "the_grove"
    room.db.resource_type = "flowers"
    rooms["flower_gardens"] = room
    
    # Bug Meadow
    room, created = get_or_create_room(
        "grove_bug_meadow",
        "Bug Meadow"
    )
    room.db.desc = """
|yBug Meadow|n

A wild meadow on the edge of the orchards where insects thrive. Butterflies dance 
over wildflowers, beetles trundle through the grass, and at night, fireflies light 
the darkness.

Bug catchers come here with nets and jars, seeking specimens for the Museum or 
personal collections. The variety is remarkable—species from all realms seem to 
find their way here.

<time.desc> Different bugs appear at different times of day.
    """.strip()
    room.db.area = "the_grove"
    room.db.resource_type = "bugs"
    rooms["bug_meadow"] = room
    
    link_rooms(rooms["orchards"], "east", rooms["flower_gardens"], "west")
    link_rooms(rooms["orchards"], "south", rooms["bug_meadow"], "north")
    
    return rooms


def build_guild_hall():
    """Build Guild Hall area."""
    rooms = {}
    
    # Guild Hall Main
    room, created = get_or_create_room(
        "grove_guild_hall",
        "Guild Hall"
    )
    room.db.desc = """
|yGuild Hall|n

The headquarters for Grove guilds and organizations. A grand building with banners 
representing various groups hanging from the rafters. The main hall serves as a 
gathering space and job board.

Guilds maintain offices here, recruiting new members and organizing activities. 
The |wJob Board|n lists work opportunities posted by guilds and individuals alike.

A |wGuild Registrar|n handles the paperwork for forming new guilds, joining existing 
ones, and mediating disputes. Guild politics can get... complicated.
    """.strip()
    room.db.area = "the_grove"
    room.tags.add("indoor", category="room_flag")
    rooms["guild_hall"] = room
    
    # Job Board Room
    room, created = get_or_create_room(
        "grove_job_board",
        "Job Board Chamber"
    )
    room.db.desc = """
|yJob Board Chamber|n

A room dedicated to employment opportunities. The walls are covered with postings—
jobs, contracts, requests for services. Everything from "need help moving furniture" 
to "seeking adventurers for dangerous expedition."

Categories organize the chaos:
- |gAdventuring|n - Quests and expeditions
- |yLabor|n - Physical work and odd jobs
- |cServices|n - Skilled work and crafting
- |mPersonal|n - Private arrangements

Take a posting that interests you. Complete the work. Get paid. Simple.
    """.strip()
    room.db.area = "the_grove"
    room.tags.add("indoor", category="room_flag")
    rooms["job_board"] = room
    
    link_rooms(rooms["guild_hall"], "east", rooms["job_board"], "west")
    
    return rooms


def build_grove_hub():
    """Build all Grove hub areas and connect them."""
    logger.log_info("Building Grove Hub areas...")
    
    all_rooms = {}
    
    # Build each section
    all_rooms.update(build_gate_plaza())
    all_rooms.update(build_town_square())
    all_rooms.update(build_tavern_row())
    all_rooms.update(build_residential())
    all_rooms.update(build_services())
    all_rooms.update(build_waterfront())
    all_rooms.update(build_orchards())
    all_rooms.update(build_guild_hall())
    
    # Connect sections together
    # Gate Plaza -> Town Square
    link_rooms(all_rooms["gate_plaza"], "south", all_rooms["town_square"], "north")
    
    # Town Square is the hub - connect everything
    link_rooms(all_rooms["town_square"], "west", all_rooms["tavern_row"], "east")
    link_rooms(all_rooms["town_square"], "east", all_rooms["residential"], "west")
    link_rooms(all_rooms["town_square"], "southwest", all_rooms["waterfront"], "northeast")
    link_rooms(all_rooms["town_square"], "southeast", all_rooms["services_row"], "northwest")
    link_rooms(all_rooms["town_square"], "northwest", all_rooms["orchards"], "southeast")
    link_rooms(all_rooms["town_square"], "northeast", all_rooms["guild_hall"], "southwest")
    
    # Connect to existing Museum if it exists
    museum = search_object("museum_entrance", typeclass="typeclasses.rooms.Room")
    if museum:
        link_rooms(all_rooms["services_row"], "south", museum[0], "north")
        logger.log_info("Connected to existing Museum.")
    
    # Connect to existing Market if it exists  
    market = search_object("market_main", typeclass="typeclasses.rooms.Room")
    if market:
        link_rooms(all_rooms["services_row"], "west", market[0], "east")
        logger.log_info("Connected to existing Market.")
    
    # Connect to existing newbie areas
    # Whisperwood
    whisperwood = search_object("whisperwood_entrance", typeclass="typeclasses.rooms.Room")
    if whisperwood:
        link_rooms(all_rooms["orchards"], "west", whisperwood[0], "east")
        logger.log_info("Connected to Whisperwood.")
    
    # Moonshallow
    moonshallow = search_object("moonshallow_shore", typeclass="typeclasses.rooms.Room")
    if moonshallow:
        link_rooms(all_rooms["waterfront"], "south", moonshallow[0], "north")
        logger.log_info("Connected to Moonshallow.")
    
    # Count rooms
    room_count = len(all_rooms)
    logger.log_info(f"Grove Hub complete: {room_count} rooms created/updated.")
    
    return all_rooms


# Quick access function
def rebuild_grove():
    """Rebuild entire Grove hub. Safe to run multiple times."""
    return build_grove_hub()
