"""
The Grove - Central Hub Builder

Builds the main Grove hub areas:
- Gate Plaza (realm travel)
- Town Square (central gathering)
- Market Row (expanded shopping)
- Tavern Row (social spaces)
- Residential Quarter (housing access)
- Services Row (crafting stations)
- Waterfront (docks, fishing)
- Orchards (Grove-specific gathering)

Usage:
    from content.grove import build_grove_hub
    build_grove_hub()
"""

from evennia import create_object, search_object
from evennia.utils import logger


# =============================================================================
# GROVE HUB ROOMS
# =============================================================================

GROVE_HUB_ROOMS = {
    # === GATE PLAZA ===
    "gate_plaza": {
        "key": "Gate Plaza",
        "desc": (
            "Nine massive gates arranged in a circle dominate this plaza, each "
            "wrought from materials native to their destination realm. The gates "
            "shimmer with barely-contained energy, their surfaces occasionally "
            "rippling like disturbed water. At the center stands the Gatekeepers' "
            "post, where robed figures monitor all who come and go.\n\n"
            "<weather.desc>\n\n"
            "Travelers from across the realms pass through here - some arriving, "
            "some departing, all watched. A large notice warns: |rREALM GATES LEAD "
            "TO IC AREAS. PROCEED AT YOUR OWN RISK.|n"
        ),
        "area": "the_grove",
        "room_key": "grove_gate_plaza",
        "tags": ["safe", "no_combat", "hub"],
    },
    
    "gatekeepers_office": {
        "key": "Gatekeepers' Office",
        "desc": (
            "A circular room beneath the Gate Plaza, walls lined with ledgers and "
            "glowing crystals that track realm connections. Several desks are "
            "staffed by robed Gatekeepers, their faces hidden in shadow. Maps of "
            "the nine realms cover every surface, marked with travel routes and "
            "warnings.\n\n"
            "A sign reads: |wBounty verification, ownership documents, and debt "
            "warrants processed here. All claims must be documented.|n"
        ),
        "area": "the_grove",
        "room_key": "grove_gatekeepers_office",
        "tags": ["indoor", "safe"],
    },
    
    # === TOWN SQUARE ===
    "town_square": {
        "key": "Town Square",
        "desc": (
            "The heart of the Grove. A great fountain of Yggdrasil water burbles "
            "at the center, its basin filled with coins tossed by wishful travelers. "
            "Cobblestone paths radiate outward to every district. Benches circle "
            "the fountain, always occupied by chatting residents and weary arrivals.\n\n"
            "<weather.desc>\n\n"
            "This is where the Grove comes together. Merchants hawk wares, children "
            "play, and news spreads faster than wildfire. A large notice board stands "
            "near the fountain, covered in postings."
        ),
        "area": "the_grove",
        "room_key": "grove_town_square",
        "tags": ["safe", "no_combat", "hub", "central"],
    },
    
    "the_wishing_well": {
        "key": "The Wishing Well",
        "desc": (
            "A small alcove off the Town Square houses an ancient well, its stones "
            "worn smooth by countless hands. The water within glows faintly with "
            "an inner light. Legend says Yggdrasil's roots touch this water.\n\n"
            "A small sign reads: |wToss a coin and make a wish. Results may vary.|n"
        ),
        "area": "the_grove",
        "room_key": "grove_wishing_well",
        "tags": ["indoor", "safe"],
    },
    
    # === TAVERN ROW ===
    "tavern_row": {
        "key": "Tavern Row",
        "desc": (
            "The social heart of the Grove, where several establishments compete "
            "for attention. Warm light spills from doorways, laughter and music "
            "drift on the air, and the smell of good food mingles with ale and "
            "pipe smoke. The street is lively well into the night.\n\n"
            "<weather.desc>\n\n"
            "Signs advertise: |wThe Tipsy Sprite|n (tavern), |wThe Drowsy Fox|n "
            "(inn), |wFinger's Den|n (gambling), and |wThe Steam & Soak|n (bath house)."
        ),
        "area": "the_grove",
        "room_key": "grove_tavern_row",
        "tags": ["safe", "no_combat"],
    },
    
    "tipsy_sprite_common": {
        "key": "The Tipsy Sprite - Common Room",
        "desc": (
            "Big Tom's domain. The common room is warm and welcoming, a massive "
            "fireplace crackling against one wall. Long tables fill the space, "
            "occupied by travelers sharing meals and stories. The bar runs the "
            "length of the back wall, bottles of every description behind it.\n\n"
            "The smell of roasting meat and fresh bread fills the air. Big Tom "
            "himself tends bar, his booming laugh carrying over the crowd."
        ),
        "area": "the_grove",
        "room_key": "grove_tipsy_sprite_common",
        "tags": ["indoor", "safe", "shop"],
    },
    
    "drowsy_fox_lobby": {
        "key": "The Drowsy Fox - Lobby",
        "desc": (
            "A cozy inn lobby with plush armchairs and a crackling fireplace. "
            "The innkeeper, a matronly woman named Mira, keeps the place spotless "
            "and welcoming. Keys hang on hooks behind the desk, and a chalkboard "
            "lists available rooms.\n\n"
            "A sign notes: |wRooms available by the night or the week. Safe storage "
            "included. No questions asked about your business.|n"
        ),
        "area": "the_grove",
        "room_key": "grove_drowsy_fox_lobby",
        "tags": ["indoor", "safe"],
    },
    
    "fingers_den": {
        "key": "Finger's Den",
        "desc": (
            "A gambling hall that never closes. The interior is dim, lit by "
            "enchanted candles that cast no smoke. Card tables, dice pits, and "
            "spinning wheels of fortune fill the space. The establishment is run "
            "by Fingers - a slender figure whose hands move faster than eyes can "
            "follow.\n\n"
            "A sign warns: |yThe house always wins. Eventually.|n\n\n"
            "Despite the warning, fortunes are won and lost here nightly."
        ),
        "area": "the_grove",
        "room_key": "grove_fingers_den",
        "tags": ["indoor", "safe"],
    },
    
    "steam_and_soak": {
        "key": "The Steam & Soak - Entry",
        "desc": (
            "Warm, humid air and the scent of exotic oils greet you. The bath "
            "house is a place of relaxation and... whatever else consenting adults "
            "get up to in warm water. Attendants in light robes offer towels and "
            "direct visitors to various pools.\n\n"
            "A menu lists: |wPublic Baths|n (free), |wPrivate Pools|n (5g/hour), "
            "|wMassage Services|n (10g), |wPrivate Suites|n (25g/hour)."
        ),
        "area": "the_grove",
        "room_key": "grove_steam_soak_entry",
        "tags": ["indoor", "safe"],
    },
    
    "steam_public_baths": {
        "key": "Public Baths",
        "desc": (
            "A large, steaming pool fills most of the room, surrounded by marble "
            "benches and small alcoves for privacy. The water is kept at a perfect "
            "temperature by enchantment, and subtle magic keeps it eternally clean.\n\n"
            "Various patrons soak and chat, the atmosphere relaxed and informal. "
            "Towels are provided, clothing is optional, and judgment is forbidden."
        ),
        "area": "the_grove",
        "room_key": "grove_public_baths",
        "tags": ["indoor", "safe", "bath"],
    },
    
    # === RESIDENTIAL QUARTER ===
    "residential_entrance": {
        "key": "Residential Quarter Entrance",
        "desc": (
            "The path into the Residential Quarter, where Grove residents make "
            "their homes. A wrought-iron archway marks the entrance, decorated "
            "with flowering vines. The Housing Office sits just inside, its door "
            "always open for those seeking a place to stay.\n\n"
            "Beyond the arch, streets branch off toward Starter Row, Maple Lane, "
            "and Hilltop Estates. Each neighborhood has its own character."
        ),
        "area": "the_grove",
        "room_key": "grove_residential_entrance",
        "tags": ["safe", "no_combat"],
    },
    
    "housing_office": {
        "key": "Housing Office",
        "desc": (
            "A tidy office with maps of available properties covering the walls. "
            "A clerk sits behind a desk piled with deeds, keys, and contracts. "
            "Catalogs of furniture and home upgrades sit on a side table for "
            "browsing.\n\n"
            "Services offered: |wHome Purchase|n, |wUpgrades|n, |wPermit Changes|n, "
            "|wKey Replacement|n."
        ),
        "area": "the_grove",
        "room_key": "grove_housing_office",
        "tags": ["indoor", "safe"],
    },
    
    # === SERVICES ROW ===
    "services_row": {
        "key": "Services Row",
        "desc": (
            "A street dedicated to craftspeople and trainers. Workshops line both "
            "sides, their sounds blending together - the ring of hammers, the "
            "bubble of alchemical mixtures, the whir of spinning wheels. Artisans "
            "offer their services and teach their trades.\n\n"
            "<weather.desc>\n\n"
            "Signs point to: |wThe Forge|n (smithing), |wThe Loom|n (tailoring), "
            "|wThe Flask|n (alchemy), |wThe Bench|n (woodworking)."
        ),
        "area": "the_grove",
        "room_key": "grove_services_row",
        "tags": ["safe", "no_combat"],
    },
    
    "the_forge": {
        "key": "The Forge",
        "desc": (
            "Heat hits you like a wall. The Forge is dominated by a massive "
            "furnace, anvils arranged around it like supplicants. Hammers hang "
            "on every surface, and the smell of hot metal fills the air. The "
            "smith, a burly figure covered in soot, looks up as you enter.\n\n"
            "Workstations are available for those with materials and skill."
        ),
        "area": "the_grove",
        "room_key": "grove_forge",
        "tags": ["indoor", "safe", "workstation_smithing"],
    },
    
    "the_loom": {
        "key": "The Loom",
        "desc": (
            "Bolts of fabric in every color line the walls, and several looms "
            "click and clatter with work in progress. The scent of lanolin and "
            "dye mingles pleasantly. A seamstress works at a table covered in "
            "patterns and thread.\n\n"
            "Workstations available for tailoring and leatherwork."
        ),
        "area": "the_grove",
        "room_key": "grove_loom",
        "tags": ["indoor", "safe", "workstation_tailoring", "workstation_leatherworking"],
    },
    
    "the_flask": {
        "key": "The Flask",
        "desc": (
            "Glass vessels bubble and steam on every surface. Shelves hold "
            "ingredients in labeled jars - herbs, powders, liquids of suspicious "
            "color. The alchemist, Whisper's colleague Petal, tends a complex "
            "distillation setup with practiced hands.\n\n"
            "Alchemy workstations available. Handle ingredients with care."
        ),
        "area": "the_grove",
        "room_key": "grove_flask",
        "tags": ["indoor", "safe", "workstation_alchemy"],
    },
    
    "the_bench": {
        "key": "The Bench",
        "desc": (
            "Sawdust covers the floor and the smell of fresh-cut wood fills "
            "the air. Workbenches hold projects in various stages - furniture, "
            "tools, decorative carvings. A carpenter planes a board smooth, "
            "whistling tunelessly.\n\n"
            "Woodworking stations and basic jewelcraft tools available."
        ),
        "area": "the_grove",
        "room_key": "grove_bench",
        "tags": ["indoor", "safe", "workstation_woodworking", "workstation_jewelcrafting"],
    },
    
    # === WATERFRONT ===
    "waterfront": {
        "key": "The Waterfront",
        "desc": (
            "The Grove's waterfront stretches along a calm, clear lake fed by "
            "Yggdrasil's roots. Docks extend into the water, some for fishing, "
            "others for small boats. The water laps gently against the shore.\n\n"
            "<weather.desc>\n\n"
            "Fishers line the docks, and children play in the shallows. A few "
            "small boats are available for rent. The water here is clean enough "
            "to swim in - many do."
        ),
        "area": "the_grove",
        "room_key": "grove_waterfront",
        "tags": ["safe", "no_combat", "fishing"],
    },
    
    "fishing_dock": {
        "key": "Fishing Dock",
        "desc": (
            "A long wooden dock extends into the lake, several fishing spots "
            "marked along its length. Buckets sit ready for catches, and a bait "
            "vendor sells worms and lures from a small stand. The experienced "
            "fishers have their favorite spots.\n\n"
            "The lake holds: |wGrove Trout|n (common), |wGolden Carp|n (uncommon), "
            "|wRoot Bass|n (rare), |wYggdrasil Eel|n (very rare)."
        ),
        "area": "the_grove",
        "room_key": "grove_fishing_dock",
        "tags": ["safe", "fishing"],
    },
    
    "boat_rental": {
        "key": "Boat Rental",
        "desc": (
            "A small shack where boats can be rented by the hour. Rowboats, "
            "canoes, and small sailboats bob at the dock. The rental keeper, "
            "an old sailor named Barnacle Bill, offers lessons for beginners.\n\n"
            "Prices: |wRowboat|n (5g/hour), |wCanoe|n (8g/hour), |wSailboat|n "
            "(15g/hour, requires skill or lesson)."
        ),
        "area": "the_grove",
        "room_key": "grove_boat_rental",
        "tags": ["safe"],
    },
    
    # === ORCHARDS ===
    "orchards_entrance": {
        "key": "The Orchards",
        "desc": (
            "A peaceful grove within the Grove - rows of fruit trees stretching "
            "into the distance. The trees here bear fruit year-round thanks to "
            "Yggdrasil's blessing. Butterflies and bees drift between blossoms.\n\n"
            "<weather.desc>\n\n"
            "Residents are welcome to forage here freely. Trees bear: |wApples|n, "
            "|wPears|n, |wCherries|n, and the rare |wGolden Fruit|n."
        ),
        "area": "the_grove",
        "room_key": "grove_orchards",
        "tags": ["safe", "foraging"],
    },
    
    "deep_orchards": {
        "key": "Deep Orchards",
        "desc": (
            "Deeper among the fruit trees, where the most prized specimens grow. "
            "Here the trees seem older, their bark silvered with age. Some say "
            "these trees were the first planted when the Grove was founded.\n\n"
            "Rare herbs grow among the roots, and unusual insects can be found "
            "on the bark."
        ),
        "area": "the_grove",
        "room_key": "grove_deep_orchards",
        "tags": ["safe", "foraging", "bugs"],
    },
}


# =============================================================================
# GROVE EXITS
# =============================================================================

GROVE_HUB_EXITS = {
    # Gate Plaza connections
    "gate_plaza": [
        ("south", "town_square", ["s"]),
        ("down", "gatekeepers_office", ["office", "gatekeepers"]),
        # Realm gates would connect here when built
    ],
    "gatekeepers_office": [
        ("up", "gate_plaza", ["out", "plaza"]),
    ],
    
    # Town Square - central hub
    "town_square": [
        ("north", "gate_plaza", ["n", "gates"]),
        ("east", "market_entrance", ["e", "market"]),  # Existing market
        ("west", "tavern_row", ["w", "taverns"]),
        ("south", "residential_entrance", ["s", "housing", "homes"]),
        ("northeast", "services_row", ["ne", "services", "crafting"]),
        ("southeast", "waterfront", ["se", "water", "docks"]),
        ("southwest", "orchards_entrance", ["sw", "orchards"]),
        ("alcove", "the_wishing_well", ["well", "wish"]),
    ],
    "the_wishing_well": [
        ("out", "town_square", ["square", "leave"]),
    ],
    
    # Tavern Row
    "tavern_row": [
        ("east", "town_square", ["e", "square"]),
        ("tipsy", "tipsy_sprite_common", ["tavern", "sprite", "tom"]),
        ("fox", "drowsy_fox_lobby", ["inn", "drowsy"]),
        ("fingers", "fingers_den", ["gambling", "den", "cards"]),
        ("steam", "steam_and_soak", ["bath", "soak", "baths"]),
    ],
    "tipsy_sprite_common": [
        ("out", "tavern_row", ["leave", "street"]),
    ],
    "drowsy_fox_lobby": [
        ("out", "tavern_row", ["leave", "street"]),
    ],
    "fingers_den": [
        ("out", "tavern_row", ["leave", "street"]),
    ],
    "steam_and_soak": [
        ("out", "tavern_row", ["leave", "street"]),
        ("baths", "steam_public_baths", ["public", "pool"]),
    ],
    "steam_public_baths": [
        ("out", "steam_and_soak", ["entry", "leave"]),
    ],
    
    # Residential Quarter
    "residential_entrance": [
        ("north", "town_square", ["n", "square"]),
        ("office", "housing_office", ["housing"]),
        # Player homes would connect from here via instancing
    ],
    "housing_office": [
        ("out", "residential_entrance", ["leave", "quarter"]),
    ],
    
    # Services Row
    "services_row": [
        ("southwest", "town_square", ["sw", "square"]),
        ("forge", "the_forge", ["smithing", "smith"]),
        ("loom", "the_loom", ["tailoring", "tailor"]),
        ("flask", "the_flask", ["alchemy", "alchemist"]),
        ("bench", "the_bench", ["woodworking", "carpenter"]),
    ],
    "the_forge": [
        ("out", "services_row", ["leave", "street"]),
    ],
    "the_loom": [
        ("out", "services_row", ["leave", "street"]),
    ],
    "the_flask": [
        ("out", "services_row", ["leave", "street"]),
    ],
    "the_bench": [
        ("out", "services_row", ["leave", "street"]),
    ],
    
    # Waterfront
    "waterfront": [
        ("northwest", "town_square", ["nw", "square"]),
        ("dock", "fishing_dock", ["fishing", "fish"]),
        ("rental", "boat_rental", ["boats", "boat"]),
    ],
    "fishing_dock": [
        ("shore", "waterfront", ["back", "leave"]),
    ],
    "boat_rental": [
        ("shore", "waterfront", ["back", "leave"]),
    ],
    
    # Orchards
    "orchards_entrance": [
        ("northeast", "town_square", ["ne", "square"]),
        ("deeper", "deep_orchards", ["deep", "in"]),
    ],
    "deep_orchards": [
        ("out", "orchards_entrance", ["back", "leave"]),
    ],
}


# =============================================================================
# GROVE NPCS
# =============================================================================

GROVE_HUB_NPCS = {
    # Gatekeepers
    "gatekeeper": {
        "key": "A Gatekeeper",
        "desc": (
            "A robed figure whose face remains hidden in shadow regardless of "
            "the light. They speak in a calm, neutral tone and seem to see "
            "everything. Gatekeepers never sleep, never eat, and never forget."
        ),
        "location": "gate_plaza",
        "dialogue_tree": "gatekeeper_dialogue",
        "behaviors": ["stationary"],
    },
    
    # Mira the innkeeper
    "mira": {
        "key": "Mira",
        "desc": (
            "The innkeeper of the Drowsy Fox, a matronly woman with kind eyes "
            "and a no-nonsense attitude. Her silver-streaked hair is always "
            "pinned up practically, and she keeps her establishment spotless."
        ),
        "location": "drowsy_fox_lobby",
        "dialogue_tree": "mira_dialogue",
        "behaviors": ["friendly", "helpful"],
    },
    
    # Fingers the gambler
    "fingers": {
        "key": "Fingers",
        "desc": (
            "Thin as a reed and twice as flexible, Fingers runs the gambling "
            "den with a perpetual half-smile. Their hands are never still - "
            "always shuffling cards, spinning coins, or drumming on surfaces. "
            "No one knows their real name or origins."
        ),
        "location": "fingers_den",
        "dialogue_tree": "fingers_dialogue",
        "behaviors": ["mysterious", "gambler"],
    },
    
    # Petal the alchemist
    "petal": {
        "key": "Petal",
        "desc": (
            "Whisper's colleague at the Flask, though more focused on healing "
            "and utility potions than exotic concoctions. Petal is small and "
            "quiet, with green-stained fingers and a perpetual squint from "
            "examining tiny ingredients."
        ),
        "location": "the_flask",
        "dialogue_tree": "petal_dialogue",
        "behaviors": ["helpful", "crafting_trainer"],
        "teaches_recipes": True,
    },
    
    # Barnacle Bill
    "barnacle_bill": {
        "key": "Barnacle Bill",
        "desc": (
            "An old sailor who retired to the Grove after decades at sea. "
            "His weathered face is creased with laugh lines, and he's always "
            "happy to share tales of his adventures between boat rentals. "
            "His wooden leg thumps on the dock as he walks."
        ),
        "location": "boat_rental",
        "dialogue_tree": "barnacle_dialogue",
        "behaviors": ["friendly", "storyteller"],
    },
}


# =============================================================================
# RESOURCE NODES
# =============================================================================

GROVE_HUB_RESOURCES = {
    "fishing_dock": [
        {"type": "fish", "resource": "grove_trout", "rarity": "common"},
        {"type": "fish", "resource": "golden_carp", "rarity": "uncommon"},
        {"type": "fish", "resource": "root_bass", "rarity": "rare"},
    ],
    "waterfront": [
        {"type": "fish", "resource": "grove_trout", "rarity": "common"},
    ],
    "orchards_entrance": [
        {"type": "forage", "resource": "apple", "rarity": "common"},
        {"type": "forage", "resource": "pear", "rarity": "common"},
        {"type": "forage", "resource": "cherry", "rarity": "uncommon"},
    ],
    "deep_orchards": [
        {"type": "forage", "resource": "golden_fruit", "rarity": "rare"},
        {"type": "forage", "resource": "silverleaf", "rarity": "uncommon"},
        {"type": "bugs", "resource": "golden_beetle", "rarity": "rare"},
        {"type": "bugs", "resource": "grove_butterfly", "rarity": "uncommon"},
    ],
}


# =============================================================================
# FURNITURE / OBJECTS
# =============================================================================

GROVE_HUB_FURNITURE = {
    "town_square": [
        {"key": "notice_board", "name": "Notice Board", "type": "decoration"},
        {"key": "fountain_bench", "name": "Fountain Bench", "type": "seating"},
    ],
    "steam_public_baths": [
        {"key": "bathing_pool", "name": "Bathing Pool", "type": "bath"},
        {"key": "bath_bench", "name": "Bath Bench", "type": "seating"},
    ],
    "tipsy_sprite_common": [
        {"key": "bar_stool", "name": "Bar Stool", "type": "seating"},
        {"key": "common_table", "name": "Common Table", "type": "table"},
    ],
}


# =============================================================================
# Builder Functions
# =============================================================================

def build_grove_hub(connect_to_existing=True):
    """
    Build all Grove hub rooms.
    
    Args:
        connect_to_existing: If True, connect to existing Market entrance
        
    Returns:
        dict: Created rooms by key
    """
    created_rooms = {}
    
    logger.log_info("Building Grove Hub areas...")
    
    # Create rooms
    for room_key, room_data in GROVE_HUB_ROOMS.items():
        # Check if already exists
        existing = search_object(room_data["key"], typeclass="typeclasses.rooms.Room")
        if existing:
            existing = [r for r in existing if r.db.room_key == room_data.get("room_key")]
            if existing:
                logger.log_info(f"  Room already exists: {room_data['key']}")
                created_rooms[room_key] = existing[0]
                continue
        
        # Create room
        room = create_object(
            "typeclasses.rooms.Room",
            key=room_data["key"],
        )
        
        room.db.desc = room_data["desc"]
        room.db.area = room_data.get("area", "the_grove")
        room.db.room_key = room_data.get("room_key", room_key)
        
        # Add tags
        for tag in room_data.get("tags", []):
            room.tags.add(tag, category="room_flag")
        
        created_rooms[room_key] = room
        logger.log_info(f"  Created: {room_data['key']}")
    
    # Create exits
    logger.log_info("Creating exits...")
    for source_key, exits in GROVE_HUB_EXITS.items():
        source = created_rooms.get(source_key)
        if not source:
            continue
        
        for exit_data in exits:
            direction, dest_key, aliases = exit_data
            dest = created_rooms.get(dest_key)
            
            if not dest:
                # Try to find existing room (like market_entrance)
                if dest_key == "market_entrance":
                    existing = search_object("Market Entrance", typeclass="typeclasses.rooms.Room")
                    if existing:
                        dest = existing[0]
                
                if not dest:
                    logger.log_warn(f"  Destination not found: {dest_key}")
                    continue
            
            # Check if exit exists
            existing_exits = [
                ex for ex in source.exits
                if ex.destination == dest
            ]
            if existing_exits:
                continue
            
            # Create exit
            exit_obj = create_object(
                "typeclasses.exits.Exit",
                key=direction,
                location=source,
                destination=dest,
            )
            exit_obj.aliases.add(aliases)
    
    # Connect to existing areas
    if connect_to_existing:
        connect_grove_to_existing(created_rooms)
    
    logger.log_info(f"Grove Hub complete. {len(created_rooms)} rooms.")
    return created_rooms


def connect_grove_to_existing(created_rooms):
    """Connect new Grove hub to existing areas."""
    town_square = created_rooms.get("town_square")
    if not town_square:
        return
    
    # Connect to Market
    market = search_object("Market Entrance", typeclass="typeclasses.rooms.Room")
    if market:
        market = market[0]
        # Create exit from market to town square if not exists
        existing = [ex for ex in market.exits if ex.destination == town_square]
        if not existing:
            exit_obj = create_object(
                "typeclasses.exits.Exit",
                key="west",
                location=market,
                destination=town_square,
            )
            exit_obj.aliases.add(["w", "square"])
            logger.log_info("  Connected Market to Town Square")
    
    # Connect to Museum
    museum = search_object("Museum Entrance", typeclass="typeclasses.rooms.Room")
    if museum:
        museum = museum[0]
        # Create bidirectional exits
        existing = [ex for ex in museum.exits if ex.destination == town_square]
        if not existing:
            exit_obj = create_object(
                "typeclasses.exits.Exit",
                key="out",
                location=museum,
                destination=town_square,
            )
            exit_obj.aliases.add(["square", "leave"])
            
            exit_obj2 = create_object(
                "typeclasses.exits.Exit",
                key="museum",
                location=town_square,
                destination=museum,
            )
            exit_obj2.aliases.add(["m", "curator"])
            logger.log_info("  Connected Museum to Town Square")
    
    # Connect to newbie areas (through existing paths or new ones)
    whisperwood = search_object("Forest Edge", typeclass="typeclasses.rooms.Room")
    if whisperwood:
        whisperwood = whisperwood[0]
        # Town square -> west path -> whisperwood
        # (Might already be connected via market)


def spawn_grove_npcs(created_rooms):
    """Spawn NPCs in Grove hub areas."""
    from world.npcs import create_npc
    
    spawned = []
    
    for npc_key, npc_data in GROVE_HUB_NPCS.items():
        location_key = npc_data.get("location")
        location = created_rooms.get(location_key)
        
        if not location:
            continue
        
        # Check if NPC exists
        existing = [
            obj for obj in location.contents
            if obj.key == npc_data["key"]
        ]
        if existing:
            continue
        
        # Create NPC
        npc = create_npc(
            npc_data["key"],
            location=location,
            desc=npc_data.get("desc"),
        )
        
        if npc:
            npc.db.dialogue_tree = npc_data.get("dialogue_tree")
            spawned.append(npc)
            logger.log_info(f"  Spawned NPC: {npc_data['key']}")
    
    return spawned


def setup_grove_resources(created_rooms):
    """Set up resource nodes in Grove areas."""
    from world.resources import setup_resource_node
    
    for room_key, resources in GROVE_HUB_RESOURCES.items():
        room = created_rooms.get(room_key)
        if not room:
            continue
        
        for resource_data in resources:
            setup_resource_node(
                room,
                resource_data["type"],
                resource_data["resource"],
                rarity=resource_data.get("rarity", "common"),
            )


# =============================================================================
# Quick Build Function
# =============================================================================

def build_all_grove():
    """Build everything for the Grove hub."""
    rooms = build_grove_hub()
    spawn_grove_npcs(rooms)
    setup_grove_resources(rooms)
    return rooms
