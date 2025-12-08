"""
The Grove - Central Hub Builder
===============================

Builds the main Grove hub areas:
- Gate Plaza (realm travel)
- Town Square (central gathering)
- Tavern Row (social, inn, bath house)
- Residential Quarter (housing access)
- Waterfront (docks, fishing)
- Orchards (foraging within Grove)
- Services Row (crafting stations)
- Guild Hall (player organizations)

Run with: @py from content.the_grove import build_grove; build_grove()
"""

from evennia import create_object, search_object
from evennia.utils import logger


# =============================================================================
# GROVE ROOM DATA
# =============================================================================

GROVE_ROOMS = {
    # =========================================================================
    # GATE PLAZA - Realm Travel Hub
    # =========================================================================
    "gate_plaza": {
        "key": "Gate Plaza",
        "desc": (
            "Nine towering archways stand in a circle around a central platform, "
            "each gate crafted from materials native to its destination realm. "
            "Travelers arrive and depart in flashes of light, their forms "
            "materializing on the arrival stones. |wGatekeepers|n in hooded robes "
            "monitor the traffic, checking documents and occasionally redirecting "
            "those who arrived... unexpectedly.\n\n"
            "The gates pulse with quiet energy: |yMidgard's|n iron arch, "
            "|bAsgard's|n golden frame, |rMuspelheim's|n obsidian doorway, "
            "and six others representing the remaining realms. A large "
            "|wNotice Board|n lists travel advisories and realm conditions."
        ),
        "area": "the_grove",
        "room_type": "plaza",
        "tags": ["safe", "indoor", "no_combat"],
        "details": {
            "gates": "Nine archways, each distinct. Most shimmer with dormant energy, awaiting activation.",
            "gatekeepers": "Hooded figures who speak little but see everything. They ensure orderly travel.",
            "notice board": "Current realm conditions, travel warnings, and gate maintenance schedules.",
            "arrival stones": "Circular platforms where travelers materialize. Slightly warm to the touch.",
        },
    },
    
    "gatekeepers_office": {
        "key": "Gatekeepers' Office",
        "desc": (
            "A circular chamber behind the Gate Plaza, lined with shelves of "
            "ledgers, travel permits, and realm documentation. Maps of all nine "
            "realms cover the walls, pins marking known dangers and points of "
            "interest. Several |wGatekeepers|n work at desks, processing paperwork "
            "and handling inquiries.\n\n"
            "A counter separates visitors from the work area. Signs indicate "
            "services: |cTravel Permits|n, |cRealm Information|n, |cLost & Found|n, "
            "and ominously, |rBounty Verification|n."
        ),
        "area": "the_grove",
        "room_type": "office",
        "tags": ["safe", "indoor", "no_combat"],
    },
    
    # =========================================================================
    # TOWN SQUARE - Central Hub
    # =========================================================================
    "town_square": {
        "key": "Town Square",
        "desc": (
            "The heart of the Grove opens before you - a broad cobblestone plaza "
            "centered around an ancient fountain. Water flows eternally from a "
            "sculpture of Yggdrasil's roots, the sound a constant gentle music. "
            "Benches ring the fountain where residents and travelers rest.\n\n"
            "Paths lead in every direction: north to the |wGate Plaza|n, east to "
            "the |wMarket|n, west toward |wTavern Row|n, and south to the "
            "|wMuseum|n. The |wResidential Quarter|n lies to the northwest, while "
            "the |wWaterfront|n can be reached to the southeast. A grand "
            "|wNotice Board|n displays quests, events, and community announcements."
        ),
        "area": "the_grove",
        "room_type": "plaza",
        "tags": ["safe", "outdoor", "no_combat", "central"],
        "details": {
            "fountain": "Water flows from carved roots, collecting in a basin. Coins glitter at the bottom - wishes made by hopeful travelers.",
            "benches": "Worn wooden benches where folk gather to chat, rest, or people-watch.",
            "notice board": "Covered in papers: quest postings, missing person notices, event announcements, and the occasional 'WANTED' poster.",
            "cobblestones": "Smooth from centuries of foot traffic. Some have names carved into them - old residents, perhaps.",
        },
    },
    
    "wishing_well": {
        "key": "The Wishing Well",
        "desc": (
            "Tucked into a quiet corner of the square, an ancient stone well "
            "sits beneath a small gazebo. Unlike a normal well, this one glows "
            "faintly from within - coins tossed in catch the light as they fall "
            "into seemingly infinite depths.\n\n"
            "A weathered sign reads: |c'One wish per day. Results may vary. "
            "The Grove takes no responsibility for wishes granted in unexpected ways.'|n\n\n"
            "Locals swear the well has a sense of humor."
        ),
        "area": "the_grove",
        "room_type": "landmark",
        "tags": ["safe", "outdoor", "no_combat"],
        "details": {
            "well": "Deep. Very deep. The glow comes from somewhere far below. Coins spiral down slowly, as if falling through honey.",
            "sign": "The disclaimer is longer on the back, filled with tiny text about liability and 'ironic fulfillment clauses.'",
        },
    },
    
    # =========================================================================
    # TAVERN ROW - Social District
    # =========================================================================
    "tavern_row": {
        "key": "Tavern Row",
        "desc": (
            "The social heart of the Grove stretches before you - a street lined "
            "with establishments promising food, drink, entertainment, and rest. "
            "Warm light spills from windows, laughter and music drifting out.\n\n"
            "The |wTipsy Sprite|n tavern dominates the north side, Big Tom's "
            "domain. Across the way, the |wWanderer's Rest|n inn offers rooms "
            "for travelers. Further down, the steamy windows of the |wBath House|n "
            "promise relaxation, while the |wLucky Coin|n gambling den's doors "
            "never seem to close."
        ),
        "area": "the_grove",
        "room_type": "street",
        "tags": ["safe", "outdoor", "no_combat"],
    },
    
    "tipsy_sprite_tavern": {
        "key": "The Tipsy Sprite",
        "desc": (
            "Big Tom's tavern is exactly what a tavern should be - warm, loud, "
            "and smelling of good food and better ale. A massive hearth dominates "
            "one wall, its fire crackling cheerfully. Rough wooden tables fill "
            "the common room, scarred by years of use.\n\n"
            "|wBig Tom|n himself tends bar, a mountain of a man with a ready smile "
            "and an iron grip on troublemakers. A chalkboard lists today's menu "
            "and drink specials. A door leads to the |wkitchen|n, and stairs "
            "climb to |wprivate rooms|n above."
        ),
        "area": "the_grove",
        "room_type": "tavern",
        "tags": ["safe", "indoor", "no_combat", "shop"],
        "details": {
            "hearth": "Large enough to roast a whole boar. And has, on occasion.",
            "bar": "Polished wood worn smooth by elbows. Tap handles for a dozen different brews.",
            "chalkboard": "Today's Special: Mystery Meat Stew (Don't Ask). Drink Special: Whatever Tom Feels Like.",
            "tables": "Each one has stories carved into it. Names, dates, crude drawings, declarations of love.",
        },
    },
    
    "tipsy_sprite_kitchen": {
        "key": "Tipsy Sprite Kitchen",
        "desc": (
            "The heart of Tom's operation - a cramped but efficient kitchen where "
            "pots bubble and pans sizzle. Herbs hang from the ceiling, meats cure "
            "in the corner, and a perpetually stressed cook manages multiple dishes "
            "at once.\n\n"
            "A |wcooking station|n is available for those with permission to use "
            "the facilities. Tom charges a small fee but provides ingredients at cost."
        ),
        "area": "the_grove",
        "room_type": "workshop",
        "tags": ["safe", "indoor", "no_combat"],
        "has_workstation": "cooking",
    },
    
    "wanderers_rest": {
        "key": "The Wanderer's Rest",
        "desc": (
            "A proper inn for proper travelers. The common room is quieter than "
            "the Tipsy Sprite - plush chairs by the fireplace, private booths "
            "for conversation, and a small bar serving wine and spirits.\n\n"
            "|wMartha|n runs the establishment with gentle efficiency, her silver "
            "hair pinned beneath a lace cap. Room keys hang on hooks behind the "
            "desk, each tagged with a room number. A staircase leads to the "
            "|wguest rooms|n above."
        ),
        "area": "the_grove",
        "room_type": "inn",
        "tags": ["safe", "indoor", "no_combat"],
        "details": {
            "fireplace": "Smaller than Tom's hearth but no less welcoming. A cat usually sleeps nearby.",
            "booths": "High-backed for privacy. Popular for quiet conversations and clandestine meetings.",
            "room keys": "Brass keys on leather tags. Some rooms are marked as occupied.",
        },
    },
    
    "inn_hallway": {
        "key": "Inn Hallway",
        "desc": (
            "A carpeted hallway lined with numbered doors. Wall sconces provide "
            "soft lighting. The sounds from downstairs are muffled here - this "
            "floor is for rest.\n\n"
            "Doors lead to individual |wguest rooms|n. A small sitting area at "
            "the end of the hall has a window overlooking Tavern Row."
        ),
        "area": "the_grove",
        "room_type": "hallway",
        "tags": ["safe", "indoor", "no_combat"],
    },
    
    "inn_guest_room": {
        "key": "Guest Room",
        "desc": (
            "A modest but comfortable room. A bed with clean linens, a washstand "
            "with basin and pitcher, a small wardrobe, and a writing desk by the "
            "window. Everything a traveler needs for a good night's rest.\n\n"
            "A |wbell pull|n summons service. A |wdo not disturb|n sign hangs "
            "on the inside of the door."
        ),
        "area": "the_grove",
        "room_type": "bedroom",
        "tags": ["safe", "indoor", "no_combat", "private"],
    },
    
    "bath_house_entrance": {
        "key": "Grove Bath House",
        "desc": (
            "Steam wafts through the entrance of the Grove's public bath house. "
            "The reception area is tiled in pale blue, with benches for removing "
            "shoes and hooks for outer garments. A counter separates the entrance "
            "from the facilities beyond.\n\n"
            "|wAttendant Lin|n manages the front desk, offering towels, robes, "
            "and information about services. Signs point to the |wmain baths|n, "
            "|wprivate rooms|n, and |wmassage services|n.\n\n"
            "A posted sign: |c'The Grove Bath House is a place of relaxation. "
            "What happens in private rooms stays in private rooms.'|n"
        ),
        "area": "the_grove",
        "room_type": "bathhouse",
        "tags": ["safe", "indoor", "no_combat"],
    },
    
    "bath_house_main": {
        "key": "Main Baths",
        "desc": (
            "A large chamber dominated by a central pool of heated water, steam "
            "rising lazily toward the vaulted ceiling. Smaller pools line the "
            "edges - some hot, some cold, one bubbling with mineral salts.\n\n"
            "Benches and lounging areas surround the pools. Bathers of all sorts "
            "relax in the water or rest on heated stones. Conversation is quiet, "
            "punctuated by splashing and contented sighs.\n\n"
            "The atmosphere is... relaxed. Very relaxed."
        ),
        "area": "the_grove",
        "room_type": "bathhouse",
        "tags": ["safe", "indoor", "no_combat", "adult"],
        "details": {
            "central pool": "Large enough for a dozen bathers. Warm without being too hot.",
            "cold pool": "Bracingly cold. Good for waking up or closing pores.",
            "hot pool": "Almost too hot. Loosens muscles and inhibitions.",
            "mineral pool": "Bubbles and fizzes. Said to be good for the skin.",
        },
    },
    
    "bath_house_private": {
        "key": "Private Bath Room",
        "desc": (
            "A smaller, more intimate bathing chamber. A single deep pool, sized "
            "for two to four bathers, steams invitingly. Soft lighting, plush "
            "towels, and a selection of oils and soaps sit ready on a side table.\n\n"
            "A padded bench runs along one wall. A |wdo not disturb|n crystal "
            "glows by the door - when activated, the room becomes completely "
            "private.\n\n"
            "Whatever happens here is between you and whoever you're with."
        ),
        "area": "the_grove",
        "room_type": "private",
        "tags": ["safe", "indoor", "no_combat", "adult", "private"],
    },
    
    "lucky_coin": {
        "key": "The Lucky Coin",
        "desc": (
            "The Grove's gambling den operates around the clock, filled with the "
            "sounds of dice, cards, and the occasional cheer or groan. Smoke "
            "hangs in the air despite ventilation efforts. Tables host games "
            "of every variety.\n\n"
            "|wFingers|n, a slight figure of indeterminate age and gender, runs "
            "the establishment. They see everything and forget nothing - useful "
            "for both business and information brokering.\n\n"
            "House rules posted on the wall. The biggest one: |r'Debts are paid. "
            "One way or another.'|n"
        ),
        "area": "the_grove",
        "room_type": "gambling",
        "tags": ["safe", "indoor", "no_combat"],
        "details": {
            "dice tables": "Craps and similar games. The dice are tested regularly - the house doesn't need to cheat.",
            "card tables": "Poker, blackjack, and games from distant realms. Some tables have higher stakes than others.",
            "roulette wheel": "A spinning wheel of fortune. Or misfortune, depending on your luck.",
            "finger's corner": "Where Fingers holds court. Information has a price, but it's always accurate.",
        },
    },
    
    # =========================================================================
    # RESIDENTIAL QUARTER - Housing Access
    # =========================================================================
    "residential_entrance": {
        "key": "Residential Quarter",
        "desc": (
            "The path opens into a peaceful neighborhood of homes and gardens. "
            "Tree-lined streets wind between properties of various sizes - from "
            "cozy starter cottages to impressive estates on the distant hills.\n\n"
            "The |wHousing Office|n sits at the entrance, handling property sales, "
            "rentals, and permits. A |wFurniture Emporium|n displays samples of "
            "home furnishings in its windows. Signs point to different "
            "neighborhoods: |cStarter Row|n, |cMaple Lane|n, |cHilltop Estates|n."
        ),
        "area": "the_grove",
        "room_type": "street",
        "tags": ["safe", "outdoor", "no_combat"],
    },
    
    "housing_office": {
        "key": "Housing Office",
        "desc": (
            "A small but efficient office handling all residential matters. "
            "Property listings cover the walls - available homes, lots for sale, "
            "and rental opportunities. A scale model of the Residential Quarter "
            "sits under glass, tiny flags marking available properties.\n\n"
            "|wClerk Pembrook|n manages the office with bureaucratic precision. "
            "Forms for everything. Signatures required. But fair, always fair.\n\n"
            "Services offered: |cHome Purchase|n, |cRentals|n, |cUpgrades|n, "
            "|cPermit Applications|n."
        ),
        "area": "the_grove",
        "room_type": "office",
        "tags": ["safe", "indoor", "no_combat"],
    },
    
    "furniture_emporium": {
        "key": "Furniture Emporium",
        "desc": (
            "A showroom of domestic possibility. Sample rooms display furniture "
            "arrangements - cozy bedrooms, functional kitchens, elegant sitting "
            "rooms. Catalogs on stands show the full inventory.\n\n"
            "|wMadame Velvet|n oversees sales, her impeccable taste matched only "
            "by her sales ability. She can furnish a hovel or a mansion with "
            "equal enthusiasm.\n\n"
            "'|cA house is walls and roof,|n' she's fond of saying. '|cA home is "
            "what you put inside it.|n'"
        ),
        "area": "the_grove",
        "room_type": "shop",
        "tags": ["safe", "indoor", "no_combat", "shop"],
    },
    
    # =========================================================================
    # WATERFRONT - Docks & Fishing
    # =========================================================================
    "waterfront": {
        "key": "The Waterfront",
        "desc": (
            "The Grove's lakefront stretches peacefully, wooden docks extending "
            "over crystal-clear water. Small boats bob at their moorings. The "
            "air smells of water and wood, with hints of fish from the nearby "
            "|wFishmonger's Stall|n.\n\n"
            "Locals fish from the docks, lines trailing into the deep. A "
            "|wBoat Rental|n shack offers vessels for those wanting to explore "
            "the lake. Benches face the water, perfect for watching the sunset."
        ),
        "area": "the_grove",
        "room_type": "waterfront",
        "tags": ["safe", "outdoor", "no_combat"],
        "resources": ["fishing"],
    },
    
    "fishing_dock": {
        "key": "Fishing Dock",
        "desc": (
            "A long wooden dock extends over the water, worn smooth by years of "
            "use. Fishing poles lean against posts, some attended, some waiting "
            "for their owners to return. A bait bucket sits at the end.\n\n"
            "The water here is deep and clear. Fish shadows move below - some "
            "small, some surprisingly large. Local anglers swear the Grove's "
            "waters hold species found nowhere else."
        ),
        "area": "the_grove",
        "room_type": "dock",
        "tags": ["safe", "outdoor", "no_combat"],
        "resources": ["fishing"],
        "has_resource_node": {
            "type": "fishing",
            "skill": "fishing",
            "resources": [
                ("grove_bass", 0.3),
                ("silverscale", 0.25),
                ("mudcrawler", 0.2),
                ("golden_koi", 0.1),
                ("old_boot", 0.1),
                ("treasure_chest", 0.05),
            ],
        },
    },
    
    "boat_rental": {
        "key": "Boat Rental",
        "desc": (
            "A weathered shack at the water's edge, surrounded by small rowboats "
            "and canoes pulled up on the shore. Oars lean against the walls. A "
            "price list is posted by the window.\n\n"
            "|wOld Barnaby|n runs the rental, a grizzled figure who's spent more "
            "of his life on water than land. He'll rent you a boat, offer fishing "
            "advice, and tell stories of what lives in the deeper waters."
        ),
        "area": "the_grove",
        "room_type": "shop",
        "tags": ["safe", "outdoor", "no_combat"],
    },
    
    # =========================================================================
    # ORCHARDS - Grove Foraging
    # =========================================================================
    "orchards_entrance": {
        "key": "The Orchards",
        "desc": (
            "Rows of fruit trees stretch into the distance, their branches heavy "
            "with seasonal bounty. The air is sweet with ripening fruit and the "
            "buzz of bees. Baskets sit at the ends of rows for gatherers.\n\n"
            "Unlike the wilder foraging areas outside the Grove, the Orchards are "
            "cultivated and safe. What they lack in rare finds, they make up for "
            "in reliable, quality produce."
        ),
        "area": "the_grove",
        "room_type": "orchard",
        "tags": ["safe", "outdoor", "no_combat"],
    },
    
    "apple_grove": {
        "key": "Apple Grove",
        "desc": (
            "Apple trees of several varieties grow here - red, green, golden. "
            "Some trees are easily reachable, others require climbing or tools. "
            "Windfall apples dot the ground.\n\n"
            "A few |wbeehives|n sit between the rows, their occupants busy with "
            "the blossoms. Honey can sometimes be harvested, with care."
        ),
        "area": "the_grove",
        "room_type": "orchard",
        "tags": ["safe", "outdoor", "no_combat"],
        "has_resource_node": {
            "type": "foraging",
            "skill": "foraging",
            "resources": [
                ("apple", 0.35),
                ("golden_apple", 0.15),
                ("honey", 0.15),
                ("bee_wax", 0.1),
                ("apple_blossom", 0.15),
                ("worm", 0.1),
            ],
        },
    },
    
    "berry_bushes": {
        "key": "Berry Bushes",
        "desc": (
            "Bushes laden with berries of various kinds - strawberries, "
            "blueberries, blackberries, and a few exotic varieties. Thorns "
            "protect some of the best clusters.\n\n"
            "Birds compete with gatherers for the ripest berries. Early morning "
            "is the best time, before the birds wake."
        ),
        "area": "the_grove",
        "room_type": "garden",
        "tags": ["safe", "outdoor", "no_combat"],
        "has_resource_node": {
            "type": "foraging",
            "skill": "foraging",
            "resources": [
                ("strawberry", 0.25),
                ("blueberry", 0.25),
                ("blackberry", 0.2),
                ("raspberry", 0.15),
                ("grove_berry", 0.1),
                ("thorns", 0.05),
            ],
        },
    },
    
    # =========================================================================
    # SERVICES ROW - Crafting & Training
    # =========================================================================
    "services_row": {
        "key": "Services Row",
        "desc": (
            "A practical street lined with workshops and training facilities. "
            "The ring of hammers, the hiss of forges, and the bubbling of "
            "alchemical mixtures fill the air. This is where things get made.\n\n"
            "The |wSmithery|n glows with forge-light. |wWhisper's Alchemy|n "
            "releases occasional colored smoke. The |wCrafter's Hall|n offers "
            "workstations for rent. A |wTraining Yard|n echoes with practice."
        ),
        "area": "the_grove",
        "room_type": "street",
        "tags": ["safe", "outdoor", "no_combat"],
    },
    
    "smithery": {
        "key": "The Smithery",
        "desc": (
            "Heat radiates from the open forge where metal meets fire. Anvils "
            "ring, sparks fly, and finished goods hang from hooks - tools, "
            "weapons, hardware of all kinds.\n\n"
            "|wGreta Ironhand|n oversees the operation, her own goods mixing with "
            "commissioned work. Public |wforges|n are available for those with "
            "the skill to use them."
        ),
        "area": "the_grove",
        "room_type": "workshop",
        "tags": ["safe", "indoor", "no_combat", "shop"],
        "has_workstation": "smithing",
    },
    
    "crafters_hall": {
        "key": "Crafter's Hall",
        "desc": (
            "A large workshop space with stations for various crafts. "
            "Woodworking benches, tailoring tables, jewelcrafting stations, "
            "and leatherworking setups fill the room. Tools hang on pegboards, "
            "available for use.\n\n"
            "For a small fee, anyone can use the facilities. Masters sometimes "
            "offer lessons to promising students.\n\n"
            "Stations available: |wWoodworking|n, |wTailoring|n, |wJewelcrafting|n, "
            "|wLeatherworking|n."
        ),
        "area": "the_grove",
        "room_type": "workshop",
        "tags": ["safe", "indoor", "no_combat"],
        "has_workstation": "multi",  # Multiple workstations
    },
    
    "training_yard": {
        "key": "Training Yard",
        "desc": (
            "An open courtyard with practice dummies, sparring circles, and "
            "weapon racks. Those seeking to improve their combat skills come "
            "here to train without real danger.\n\n"
            "Sparring is allowed - and encouraged - but no true harm can come "
            "within the Grove's protection. A good place to learn before "
            "venturing through the gates."
        ),
        "area": "the_grove",
        "room_type": "training",
        "tags": ["safe", "outdoor", "no_combat", "training"],
        "details": {
            "dummies": "Straw-stuffed targets bearing years of abuse. They don't fight back.",
            "sparring circles": "Marked areas for practice fights. Non-lethal damage only within the Grove.",
            "weapon racks": "Practice weapons - dulled blades, padded clubs. Enough to learn, not enough to maim.",
        },
    },
    
    # =========================================================================
    # GUILD HALL - Player Organizations
    # =========================================================================
    "guild_hall": {
        "key": "Guild Hall",
        "desc": (
            "A grand building serving as headquarters for the Grove's various "
            "guilds and organizations. Banners representing different groups "
            "hang from the rafters. A central |wJob Board|n displays work "
            "opportunities posted by guilds and individuals alike.\n\n"
            "|wGuildmaster Vera|n manages the hall itself, handling registrations "
            "and disputes between organizations. Private meeting rooms line the "
            "upper floor."
        ),
        "area": "the_grove",
        "room_type": "hall",
        "tags": ["safe", "indoor", "no_combat"],
        "details": {
            "job board": "Work postings from guilds, businesses, and individuals. Some pay well. Some pay... differently.",
            "banners": "Each guild has its colors and sigil displayed. The more prominent, the higher their banner hangs.",
            "registry": "Official records of all registered guilds, their members, and their specialties.",
        },
    },
    
    "guild_meeting_room": {
        "key": "Guild Meeting Room",
        "desc": (
            "A private chamber for guild business. A large table dominates the "
            "center, surrounded by comfortable chairs. Maps and charts can be "
            "pinned to the walls. A lockable door ensures privacy.\n\n"
            "These rooms can be reserved by registered guilds or rented by "
            "anyone needing a private space for negotiations."
        ),
        "area": "the_grove",
        "room_type": "meeting",
        "tags": ["safe", "indoor", "no_combat", "private"],
    },
}


# =============================================================================
# EXIT CONNECTIONS
# =============================================================================

GROVE_EXITS = [
    # Gate Plaza connections
    ("gate_plaza", "south", "town_square", ["s", "square", "town"]),
    ("gate_plaza", "east", "gatekeepers_office", ["e", "office", "gatekeepers"]),
    ("gatekeepers_office", "west", "gate_plaza", ["w", "out", "plaza"]),
    
    # Town Square - Central Hub
    ("town_square", "north", "gate_plaza", ["n", "gates", "plaza"]),
    ("town_square", "east", "market_entrance", ["e", "market"]),  # To existing market
    ("town_square", "south", "museum_entrance", ["s", "museum"]),  # To existing museum
    ("town_square", "west", "tavern_row", ["w", "tavern", "taverns"]),
    ("town_square", "northwest", "residential_entrance", ["nw", "residential", "housing", "homes"]),
    ("town_square", "southeast", "waterfront", ["se", "waterfront", "docks", "lake"]),
    ("town_square", "northeast", "services_row", ["ne", "services", "crafting"]),
    ("town_square", "southwest", "wishing_well", ["sw", "well", "wish"]),
    ("wishing_well", "northeast", "town_square", ["ne", "out", "square"]),
    
    # Tavern Row
    ("tavern_row", "east", "town_square", ["e", "square"]),
    ("tavern_row", "north", "tipsy_sprite_tavern", ["n", "tavern", "sprite", "tom"]),
    ("tavern_row", "south", "wanderers_rest", ["s", "inn", "rest", "wanderer"]),
    ("tavern_row", "west", "bath_house_entrance", ["w", "bath", "baths"]),
    ("tavern_row", "northwest", "lucky_coin", ["nw", "gambling", "lucky", "coin"]),
    
    # Tipsy Sprite (Tavern)
    ("tipsy_sprite_tavern", "south", "tavern_row", ["s", "out", "row"]),
    ("tipsy_sprite_tavern", "west", "tipsy_sprite_kitchen", ["w", "kitchen", "back"]),
    ("tipsy_sprite_kitchen", "east", "tipsy_sprite_tavern", ["e", "out", "tavern"]),
    
    # Wanderer's Rest (Inn)
    ("wanderers_rest", "north", "tavern_row", ["n", "out", "row"]),
    ("wanderers_rest", "up", "inn_hallway", ["u", "upstairs", "rooms"]),
    ("inn_hallway", "down", "wanderers_rest", ["d", "downstairs", "lobby"]),
    ("inn_hallway", "east", "inn_guest_room", ["e", "room", "guest"]),
    ("inn_guest_room", "west", "inn_hallway", ["w", "out", "hall"]),
    
    # Bath House
    ("bath_house_entrance", "east", "tavern_row", ["e", "out", "row"]),
    ("bath_house_entrance", "west", "bath_house_main", ["w", "baths", "main"]),
    ("bath_house_entrance", "south", "bath_house_private", ["s", "private"]),
    ("bath_house_main", "east", "bath_house_entrance", ["e", "out", "entrance"]),
    ("bath_house_private", "north", "bath_house_entrance", ["n", "out", "entrance"]),
    
    # Lucky Coin
    ("lucky_coin", "southeast", "tavern_row", ["se", "out", "row"]),
    
    # Residential Quarter
    ("residential_entrance", "southeast", "town_square", ["se", "square", "town"]),
    ("residential_entrance", "north", "housing_office", ["n", "office", "housing"]),
    ("residential_entrance", "east", "furniture_emporium", ["e", "furniture", "emporium"]),
    ("housing_office", "south", "residential_entrance", ["s", "out"]),
    ("furniture_emporium", "west", "residential_entrance", ["w", "out"]),
    
    # Waterfront
    ("waterfront", "northwest", "town_square", ["nw", "square", "town"]),
    ("waterfront", "east", "fishing_dock", ["e", "dock", "fishing"]),
    ("waterfront", "west", "boat_rental", ["w", "boats", "rental"]),
    ("fishing_dock", "west", "waterfront", ["w", "back", "shore"]),
    ("boat_rental", "east", "waterfront", ["e", "out"]),
    
    # Orchards
    ("town_square", "west", "orchards_entrance", None),  # Already have west to tavern, need different
    # Let's put orchards accessible from waterfront
    ("waterfront", "south", "orchards_entrance", ["s", "orchards"]),
    ("orchards_entrance", "north", "waterfront", ["n", "back", "waterfront"]),
    ("orchards_entrance", "east", "apple_grove", ["e", "apples"]),
    ("orchards_entrance", "west", "berry_bushes", ["w", "berries"]),
    ("apple_grove", "west", "orchards_entrance", ["w", "back"]),
    ("berry_bushes", "east", "orchards_entrance", ["e", "back"]),
    
    # Services Row
    ("services_row", "southwest", "town_square", ["sw", "square", "town"]),
    ("services_row", "north", "smithery", ["n", "smith", "forge", "greta"]),
    ("services_row", "east", "crafters_hall", ["e", "crafters", "hall"]),
    ("services_row", "south", "training_yard", ["s", "training", "yard"]),
    ("services_row", "west", "guild_hall", ["w", "guild", "guilds"]),
    ("smithery", "south", "services_row", ["s", "out", "row"]),
    ("crafters_hall", "west", "services_row", ["w", "out", "row"]),
    ("training_yard", "north", "services_row", ["n", "out", "row"]),
    ("guild_hall", "east", "services_row", ["e", "out", "row"]),
    ("guild_hall", "up", "guild_meeting_room", ["u", "upstairs", "meeting"]),
    ("guild_meeting_room", "down", "guild_hall", ["d", "downstairs", "hall"]),
    
    # Connection to existing areas (Market)
    # Assuming market_entrance exists from market.py
]

# External connections to existing areas
EXTERNAL_CONNECTIONS = [
    # Town Square to existing Market
    ("town_square", "east", "Market Entrance", ["e", "market"]),
    # Town Square to existing Museum  
    ("town_square", "south", "Museum Entrance", ["s", "museum"]),
    # From Grove to newbie areas (may already exist via other builders)
    ("waterfront", "southeast", "Moonshallow Pond", ["se", "moonshallow", "pond"]),
]


# =============================================================================
# NPC TEMPLATES FOR GROVE
# =============================================================================

GROVE_NPCS = {
    "martha": {
        "key": "Martha",
        "desc": (
            "A kindly woman with silver hair pinned beneath a lace cap. Her eyes "
            "are warm but sharp - she misses nothing that happens in her inn. "
            "An apron covers her practical dress."
        ),
        "location": "wanderers_rest",
        "behavior": "stationary",
        "dialogue_tree": "martha_innkeeper",
    },
    
    "lin": {
        "key": "Attendant Lin",
        "desc": (
            "A graceful figure in flowing robes, their features deliberately "
            "androgynous. They speak softly and move like water. A faint scent "
            "of lavender follows them."
        ),
        "location": "bath_house_entrance",
        "behavior": "stationary",
        "dialogue_tree": "lin_attendant",
    },
    
    "fingers": {
        "key": "Fingers",
        "desc": (
            "Slight of build with quick, clever eyes that seem to evaluate "
            "everything's worth at a glance. Their gender is ambiguous, their "
            "age impossible to determine. Rings glitter on every finger - hence "
            "the name, or so they claim."
        ),
        "location": "lucky_coin",
        "behavior": "stationary",
        "dialogue_tree": "fingers_broker",
    },
    
    "pembrook": {
        "key": "Clerk Pembrook",
        "desc": (
            "A thin, precise man with spectacles perched on his nose and ink "
            "stains on his fingers. He speaks in forms and regulations but is "
            "scrupulously fair. A nameplate on his desk reads 'P. Pembrook, Esq.'"
        ),
        "location": "housing_office",
        "behavior": "stationary",
        "dialogue_tree": "pembrook_clerk",
    },
    
    "velvet": {
        "key": "Madame Velvet",
        "desc": (
            "An elegant woman of middle years with impeccable style. Her clothing "
            "serves as advertisement - perfectly coordinated, tastefully luxurious. "
            "She assesses your sense of aesthetics with a single glance."
        ),
        "location": "furniture_emporium",
        "behavior": "stationary",
        "dialogue_tree": "velvet_furniture",
    },
    
    "barnaby": {
        "key": "Old Barnaby",
        "desc": (
            "Weathered as driftwood and just as tough. His face is a map of "
            "wrinkles, his hands calloused from decades of rope and oar. He "
            "squints at you with eyes that have seen strange things in deep water."
        ),
        "location": "boat_rental",
        "behavior": "stationary",
        "dialogue_tree": "barnaby_boats",
    },
    
    "vera": {
        "key": "Guildmaster Vera",
        "desc": (
            "A striking woman in her prime, with iron-grey streaks in her dark "
            "hair. She carries herself with the authority of someone who has "
            "mediated a thousand disputes and won a hundred more arguments. "
            "The guild hall runs by her rules."
        ),
        "location": "guild_hall",
        "behavior": "stationary",
        "dialogue_tree": "vera_guildmaster",
    },
}


# =============================================================================
# DIALOGUE TREES FOR GROVE NPCS
# =============================================================================

GROVE_DIALOGUE = {
    "martha_innkeeper": {
        "start": {
            "text": (
                "Martha looks up with a warm smile. 'Welcome to the Wanderer's Rest, "
                "dear. Looking for a room, or just escaping the noise from Tom's place?'"
            ),
            "choices": [
                {"text": "I'd like a room for the night.", "goto": "room_inquiry"},
                {"text": "What can you tell me about the Grove?", "goto": "grove_info"},
                {"text": "Any interesting guests lately?", "goto": "gossip"},
                {"text": "Just looking around, thanks.", "goto": "farewell"},
            ],
        },
        "room_inquiry": {
            "text": (
                "'Rooms are 50 marks a night, breakfast included. Clean sheets, "
                "quiet neighbors, and I don't ask questions about your business. "
                "Shall I get you a key?'"
            ),
            "choices": [
                {"text": "Yes please.", "goto": "room_yes"},
                {"text": "Maybe later.", "goto": "farewell"},
            ],
        },
        "room_yes": {
            "text": (
                "She retrieves a brass key from the rack. 'Room 3, up the stairs "
                "and to the right. Rest well, dear. And remember - what happens "
                "in the Grove stays in the Grove.'"
            ),
            "end": True,
        },
        "grove_info": {
            "text": (
                "'The Grove's been here longer than anyone remembers. Safe haven "
                "at the roots of Yggdrasil. Folk from all nine realms pass through.' "
                "She leans closer. 'But safe doesn't mean without consequence. "
                "Mind what deals you make and who you make them with.'"
            ),
            "choices": [
                {"text": "What do you mean?", "goto": "warning"},
                {"text": "Thanks for the advice.", "goto": "farewell"},
            ],
        },
        "warning": {
            "text": (
                "'Bounty hunters and slave catchers can't grab you in the street here. "
                "But if they've got paperwork - legitimate claims, debts, ownership "
                "documents - even your home won't protect you.' She shrugs. "
                "'The Grove Accord protects against violence. Not consequences.'"
            ),
            "end": True,
        },
        "gossip": {
            "text": (
                "'Oh, there's always someone interesting passing through. Just yesterday, "
                "a merchant from Svartalfheim was asking about rare specimens for someone "
                "called the Curator. And I've seen more hunters around lately - watching, "
                "not hunting. Yet.' She winks. 'Walls have ears, dear. Mine more than most.'"
            ),
            "end": True,
        },
        "farewell": {
            "text": "'Take care, dear. My door's always open.'",
            "end": True,
        },
    },
    
    "fingers_broker": {
        "start": {
            "text": (
                "Fingers doesn't look up from shuffling a deck of cards. 'Information, "
                "games, or debts? Pick your poison.' The cards ripple through their "
                "hands like water."
            ),
            "choices": [
                {"text": "I need information.", "goto": "information"},
                {"text": "I want to gamble.", "goto": "gambling"},
                {"text": "I have a debt to settle.", "goto": "debts"},
                {"text": "Just browsing.", "goto": "farewell"},
            ],
        },
        "information": {
            "text": (
                "'Information has a price. Always.' They finally look at you, eyes "
                "sharp as knives. 'What do you want to know? Who's looking for whom, "
                "where the good hunting is, what's moving through the gates?' "
                "A card appears between their fingers. 'Prices vary by danger.'"
            ),
            "choices": [
                {"text": "Who's been asking about me?", "goto": "asking"},
                {"text": "Where's the best hunting?", "goto": "hunting"},
                {"text": "Never mind.", "goto": "farewell"},
            ],
        },
        "asking": {
            "text": (
                "They study you for a long moment. 'That one's free - first taste. "
                "Nobody. Yet. But that can change fast. Come back when you've made "
                "enemies worth tracking. That's when my services get valuable.'"
            ),
            "end": True,
        },
        "hunting": {
            "text": (
                "'Depends what you're hunting for.' They spread cards on the table. "
                "'Coin? Try the mines. Creatures? The deep woods. Something more... "
                "exotic?' A knowing smile. 'That information costs 100 marks.'"
            ),
            "end": True,
        },
        "gambling": {
            "text": (
                "'Cards, dice, or wheel?' They gesture to the room. 'House takes ten "
                "percent of pots over 100 marks. No credit, no IOUs. What you bet, "
                "you better have.' A pause. 'Unless you want to bet something else.'"
            ),
            "end": True,
        },
        "debts": {
            "text": (
                "'Paying or collecting?' Either way seems to please them. 'The Lucky "
                "Coin can facilitate both. We're very... creative... about payment "
                "arrangements.' The smile doesn't reach their eyes."
            ),
            "end": True,
        },
        "farewell": {
            "text": "'You know where to find me. Everyone does, eventually.'",
            "end": True,
        },
    },
    
    "lin_attendant": {
        "start": {
            "text": (
                "Lin bows gracefully. 'Welcome to the Grove Bath House. Here we wash "
                "away the dust of the road and the weight of the world. How may I "
                "serve you today?'"
            ),
            "choices": [
                {"text": "What services do you offer?", "goto": "services"},
                {"text": "I'd like to use the main baths.", "goto": "main_baths"},
                {"text": "I need a private room.", "goto": "private"},
                {"text": "Just looking.", "goto": "farewell"},
            ],
        },
        "services": {
            "text": (
                "'The main baths are open to all - hot pools, cold pools, mineral "
                "soaks. Private rooms can be reserved for... personal relaxation.' "
                "A knowing look. 'We also offer massage and specialty treatments. "
                "Discretion is absolute.'"
            ),
            "choices": [
                {"text": "Tell me about the private rooms.", "goto": "private"},
                {"text": "What specialty treatments?", "goto": "specialty"},
                {"text": "Thanks.", "goto": "farewell"},
            ],
        },
        "main_baths": {
            "text": (
                "'Through that door. Towels and robes are provided. The water "
                "is always perfect.' Lin hands you a fluffy towel. 'Relax and "
                "enjoy. The baths are a place of peace.'"
            ),
            "end": True,
        },
        "private": {
            "text": (
                "'Private rooms are 30 marks per hour. The door locks, the walls "
                "are thick, and we neither see nor hear what happens within.' "
                "Lin's expression remains serene. 'Many find them... restorative.'"
            ),
            "end": True,
        },
        "specialty": {
            "text": (
                "Lin produces a small menu. 'Massage, aromatherapy, skin treatments. "
                "We also offer... tension relief... for those with specific needs.' "
                "Their voice drops. 'Consenting adults only, of course. The Grove "
                "has rules about such things.'"
            ),
            "end": True,
        },
        "farewell": {
            "text": "'May your waters run clear.'",
            "end": True,
        },
    },
    
    "pembrook_clerk": {
        "start": {
            "text": (
                "Pembrook adjusts his spectacles and consults a ledger. 'Yes, yes, "
                "one moment. Ah.' He looks up. 'Welcome to the Housing Office. "
                "Purchase, rental, or inquiry?'"
            ),
            "choices": [
                {"text": "I want to buy a home.", "goto": "purchase"},
                {"text": "What properties are available?", "goto": "listings"},
                {"text": "I have questions about my existing property.", "goto": "existing"},
                {"text": "Just looking.", "goto": "farewell"},
            ],
        },
        "purchase": {
            "text": (
                "'Very good. First-time buyers receive a starter cottage at no cost - "
                "policy of the Grove. Upgrades and larger properties require payment.' "
                "He produces a form. 'Fill this out in triplicate. Initial here, here, "
                "and here. Sign at the bottom. Return by end of business.'"
            ),
            "end": True,
            "action": "show_housing_info",
        },
        "listings": {
            "text": (
                "'Current availability...' He runs a finger down a list. 'Starter "
                "cottages in Row A. Medium homes on Maple Lane - 25,000 marks. "
                "Estate plots on Hilltop - price on application.' He peers at you. "
                "'Budget determines options. Be realistic.'"
            ),
            "end": True,
        },
        "existing": {
            "text": (
                "'Property number?' He waits, quill ready. 'Upgrades require permits. "
                "Renovations require permits. Guest registration is recommended but "
                "not mandatory. Complaints about neighbors go to the Guildmaster.' "
                "A sniff. 'Follow procedures, everything works.'"
            ),
            "end": True,
        },
        "farewell": {
            "text": "'Office hours are dawn to dusk. Forms available at the front desk.'",
            "end": True,
        },
    },
    
    "velvet_furniture": {
        "start": {
            "text": (
                "Madame Velvet glides over, appraising you with an expert eye. "
                "'Ah, a new face. Welcome to the Emporium. Are you furnishing "
                "a new home, or updating existing... inadequacies?'"
            ),
            "choices": [
                {"text": "I need furniture for a new home.", "goto": "new_home"},
                {"text": "I want to upgrade my current furniture.", "goto": "upgrade"},
                {"text": "Just browsing.", "goto": "browse"},
                {"text": "What do you recommend?", "goto": "recommend"},
            ],
        },
        "new_home": {
            "text": (
                "'Exciting! A blank canvas.' She gestures to the showroom. 'I offer "
                "complete packages or individual pieces. The Starter Set covers "
                "basics - bed, storage, seating. 500 marks. Or...' her eyes gleam, "
                "'we could discuss something more... bespoke.'"
            ),
            "end": True,
        },
        "upgrade": {
            "text": (
                "'Wise. One's home should evolve.' She produces a catalog. 'What are "
                "you looking to improve? Sleeping arrangements? Storage? Perhaps "
                "something for... entertainment?' A raised eyebrow. 'I stock items "
                "for all tastes. Discretion assured.'"
            ),
            "end": True,
        },
        "browse": {
            "text": (
                "'By all means. Touch nothing without asking.' She returns to her "
                "perch but watches you. 'Quality reveals itself through examination. "
                "Take your time. I'll be here when you're ready to make a decision.'"
            ),
            "end": True,
        },
        "recommend": {
            "text": (
                "She studies you critically. 'For you... something practical but "
                "not without charm. A sturdy bed, versatile seating, adequate storage.' "
                "A slight smile. 'And perhaps one piece of indulgence. Everyone needs "
                "at least one thing in their home that brings joy.'"
            ),
            "end": True,
        },
    },
    
    "barnaby_boats": {
        "start": {
            "text": (
                "Barnaby squints at you from beneath a battered hat. 'Need a boat? "
                "Got rowboats, canoes, even a small sailboat if you know what you're "
                "doing.' He spits to the side. 'Don't know what you're doing, take "
                "a rowboat.'"
            ),
            "choices": [
                {"text": "I'd like to rent a boat.", "goto": "rental"},
                {"text": "What's out on the lake?", "goto": "lake_info"},
                {"text": "Got any fishing tips?", "goto": "fishing"},
                {"text": "Never mind.", "goto": "farewell"},
            ],
        },
        "rental": {
            "text": (
                "'Rowboat's 20 marks for the day. Canoe's 30. Sailboat's 50 but I "
                "need to see you can handle it first.' He jerks a thumb at the boats. "
                "'Bring 'em back in one piece. Damage comes out of your hide, one "
                "way or another.'"
            ),
            "end": True,
        },
        "lake_info": {
            "text": (
                "'Lake's deeper than it looks. Much deeper.' His eyes go distant. "
                "'Good fishing in the shallows. Middle's where the big ones are. "
                "The deep center...' He shakes his head. 'Stay out of the deep "
                "center. Things down there that shouldn't be disturbed.'"
            ),
            "choices": [
                {"text": "What things?", "goto": "deep_things"},
                {"text": "Thanks for the warning.", "goto": "farewell"},
            ],
        },
        "deep_things": {
            "text": (
                "He leans close, voice dropping. 'Saw something once. Long time ago. "
                "Went too far out on a night with no moon. Shapes in the water, big "
                "as my boat. Bigger. Eyes that glowed.' He pulls back. 'Never went "
                "back. Neither should you.'"
            ),
            "end": True,
        },
        "fishing": {
            "text": (
                "'Grove bass like worms, dawn and dusk. Silverscale go for bugs "
                "mid-afternoon. Golden koi...' He chuckles. 'Golden koi are smart. "
                "Need patience and better bait than most have.' A wink. 'Or you "
                "could just buy some from me. 5 marks a bucket.'"
            ),
            "end": True,
        },
        "farewell": {
            "text": "'Mind the water. It minds you back.'",
            "end": True,
        },
    },
    
    "vera_guildmaster": {
        "start": {
            "text": (
                "Guildmaster Vera sets down her quill and gives you her full attention. "
                "'Welcome to the Guild Hall. Are you here to register an organization, "
                "join an existing one, or file a complaint?'"
            ),
            "choices": [
                {"text": "How do I start a guild?", "goto": "start_guild"},
                {"text": "What guilds exist?", "goto": "guild_list"},
                {"text": "I'm looking for work.", "goto": "work"},
                {"text": "Just looking around.", "goto": "farewell"},
            ],
        },
        "start_guild": {
            "text": (
                "'Registration requires five founding members, a stated purpose, "
                "and 1,000 marks filing fee. The fee is non-refundable.' She slides "
                "a form across. 'Fill this out completely. Incomplete applications "
                "go to the bottom of the pile, and the pile is very tall.'"
            ),
            "end": True,
        },
        "guild_list": {
            "text": (
                "'Active guilds are listed on the registry board.' She gestures. "
                "'Merchant's Compact, Hunter's Lodge, Crafter's Circle, Adventurer's "
                "Guild... and several others of more specialized interest.' A knowing "
                "look. 'Some don't advertise. You have to know who to ask.'"
            ),
            "end": True,
        },
        "work": {
            "text": (
                "'Job board's by the entrance. Guilds post work, individuals post work. "
                "Some pay coin, some pay other things.' She leans back. 'Read the fine "
                "print. Some jobs have... requirements... that aren't immediately "
                "obvious. The Guild Hall doesn't arbitrate regrets.'"
            ),
            "end": True,
        },
        "farewell": {
            "text": "'The Hall is open dawn to dusk. Try not to start any wars.'",
            "end": True,
        },
    },
}


# =============================================================================
# BUILD FUNCTION
# =============================================================================

def build_grove():
    """Build all Grove hub rooms and connections."""
    from evennia import search_object
    
    # Get or create Limbo as fallback
    limbo = search_object("Limbo", exact=True)
    limbo = limbo[0] if limbo else None
    
    created_rooms = {}
    
    print("Building Grove Hub Areas...")
    
    # Create all rooms
    for room_key, room_data in GROVE_ROOMS.items():
        # Check if room exists
        existing = search_object(room_data["key"], exact=True)
        if existing:
            print(f"  Room '{room_data['key']}' already exists, skipping.")
            created_rooms[room_key] = existing[0]
            continue
        
        # Create room
        room = create_object(
            "typeclasses.rooms.Room",
            key=room_data["key"],
        )
        
        # Set attributes
        room.db.desc = room_data["desc"]
        room.db.area = room_data.get("area", "the_grove")
        room.db.room_type = room_data.get("room_type", "room")
        room.db.room_key = room_key
        room.db.danger_level = "safe"  # Grove is safe
        
        # Set details
        if "details" in room_data:
            room.db.details = room_data["details"]
        
        # Add tags
        for tag in room_data.get("tags", []):
            room.tags.add(tag, category="room_flag")
        
        # Mark workstation if applicable
        if "has_workstation" in room_data:
            room.db.workstation = room_data["has_workstation"]
        
        created_rooms[room_key] = room
        print(f"  Created: {room_data['key']}")
    
    print("\nCreating exits...")
    
    # Create exits between Grove rooms
    for exit_data in GROVE_EXITS:
        from_key, direction, to_key, aliases = exit_data
        
        from_room = created_rooms.get(from_key)
        to_room = created_rooms.get(to_key)
        
        if not from_room or not to_room:
            print(f"  Skipping exit: {from_key} -> {to_key} (room not found)")
            continue
        
        # Check if exit exists
        existing_exit = None
        for ex in from_room.exits:
            if ex.key.lower() == direction.lower():
                existing_exit = ex
                break
        
        if existing_exit:
            print(f"  Exit '{direction}' from {from_room.key} already exists, skipping.")
            continue
        
        # Create exit
        exit_obj = create_object(
            "typeclasses.exits.Exit",
            key=direction,
            location=from_room,
            destination=to_room,
        )
        
        if aliases:
            exit_obj.aliases.add(aliases)
        
        print(f"  Created exit: {from_room.key} --{direction}--> {to_room.key}")
    
    print("\nConnecting to existing areas...")
    
    # Connect to existing areas (Market, Museum, etc.)
    town_square = created_rooms.get("town_square")
    if town_square:
        # Find Market Entrance
        market = search_object("Market Entrance", exact=True)
        if market:
            market = market[0]
            # Create two-way exits if they don't exist
            _create_exit_if_missing(town_square, "east", market, ["e", "market"])
            _create_exit_if_missing(market, "west", town_square, ["w", "square", "town"])
            print(f"  Connected Town Square <-> Market Entrance")
        
        # Find Museum Entrance
        museum = search_object("Museum Entrance", exact=True)
        if museum:
            museum = museum[0]
            _create_exit_if_missing(town_square, "south", museum, ["s", "museum"])
            _create_exit_if_missing(museum, "north", town_square, ["n", "square", "town"])
            print(f"  Connected Town Square <-> Museum Entrance")
    
    # Connect waterfront to Moonshallow
    waterfront = created_rooms.get("waterfront")
    if waterfront:
        moonshallow = search_object("Moonshallow Pond", exact=True)
        if moonshallow:
            moonshallow = moonshallow[0]
            _create_exit_if_missing(waterfront, "southeast", moonshallow, ["se", "moonshallow", "pond"])
            _create_exit_if_missing(moonshallow, "northwest", waterfront, ["nw", "waterfront", "grove"])
            print(f"  Connected Waterfront <-> Moonshallow Pond")
    
    # Connect Gate Plaza to Limbo (temporary, for testing)
    gate_plaza = created_rooms.get("gate_plaza")
    if gate_plaza and limbo:
        _create_exit_if_missing(limbo, "grove", gate_plaza, ["grove", "thegrove"])
        print(f"  Connected Limbo -> Gate Plaza")
    
    print("\nGrove Hub build complete!")
    print(f"Created {len(created_rooms)} rooms.")
    
    return created_rooms


def _create_exit_if_missing(from_room, direction, to_room, aliases=None):
    """Helper to create an exit only if it doesn't exist."""
    for ex in from_room.exits:
        if ex.key.lower() == direction.lower():
            return None  # Exit exists
    
    exit_obj = create_object(
        "typeclasses.exits.Exit",
        key=direction,
        location=from_room,
        destination=to_room,
    )
    
    if aliases:
        exit_obj.aliases.add(aliases)
    
    return exit_obj


def spawn_grove_npcs():
    """Spawn NPCs for the Grove hub areas."""
    from world.npcs import create_npc, NPC_TEMPLATES, DIALOGUE_TREES
    
    print("Spawning Grove NPCs...")
    
    # Add dialogue trees to the system
    DIALOGUE_TREES.update(GROVE_DIALOGUE)
    
    for npc_key, npc_data in GROVE_NPCS.items():
        # Find location
        location = search_object(npc_data.get("location", ""), exact=False)
        if not location:
            print(f"  Location not found for {npc_key}: {npc_data.get('location')}")
            continue
        location = location[0]
        
        # Check if NPC already exists
        existing = [obj for obj in location.contents if obj.key == npc_data["key"]]
        if existing:
            print(f"  {npc_data['key']} already exists in {location.key}, skipping.")
            continue
        
        # Create NPC
        npc = create_object(
            "typeclasses.characters.Character",
            key=npc_data["key"],
            location=location,
        )
        
        npc.db.desc = npc_data["desc"]
        npc.db.is_npc = True
        npc.db.npc_type = "grove_resident"
        npc.db.behavior = npc_data.get("behavior", "stationary")
        npc.db.dialogue_tree = npc_data.get("dialogue_tree")
        npc.db.home_location = location
        
        print(f"  Spawned: {npc_data['key']} in {location.key}")
    
    print("Grove NPC spawn complete!")


# =============================================================================
# QUICK BUILD COMMANDS
# =============================================================================

def build_all():
    """Build everything for the Grove."""
    build_grove()
    spawn_grove_npcs()
    print("\n=== GROVE BUILD COMPLETE ===")
