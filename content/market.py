"""
Market Square Content for Gilderhaven
======================================

The commercial hub of the Grove, located near Gate Plaza.

Rooms:
- Market Square (central hub)
- Tool Shop
- Apothecary
- Tavern
- Trading Post (material buyer)

Connects to Gate Plaza.
"""

from evennia.utils import logger


# =============================================================================
# Market Rooms
# =============================================================================

MARKET_ROOMS = {
    "market_square": {
        "key": "Market Square",
        "desc": """
The bustling heart of Grove commerce. Colorful stalls and permanent
shops line the cobblestone square, their wares displayed under
striped awnings. The smell of fresh bread mingles with exotic spices.

Shoppers haggle, merchants call out their goods, and the occasional
street performer draws a small crowd. A central fountain provides
a pleasant meeting spot.

Shops surround the square in every direction.
""",
        "area_type": "market",
        "ambient_sounds": [
            "A merchant calls out prices in a sing-song voice.",
            "Coins clink as a transaction completes.",
            "Someone haggles enthusiastically over the price of fish.",
            "The fountain burbles peacefully.",
            "A child runs past, laughing.",
        ],
        "flags": [],
    },
    
    "tool_shop": {
        "key": "Honest Work Tools",
        "desc": """
Racks of tools line the walls of this well-organized shop. Fishing
rods stand in barrels, pickaxes hang from hooks, and display cases
show off the finer implements.

The smell of oil and metal fills the air. Everything here is built
to last - no flimsy tourist goods.

A workbench in the back shows signs of recent repairs.
""",
        "area_type": "shop",
        "flags": ["shop"],
    },
    
    "apothecary_shop": {
        "key": "The Bubbling Flask",
        "desc": """
Shelves packed with bottles, vials, and jars stretch to the ceiling.
Dried herbs hang in bundles from the rafters. Something bubbles
quietly in the back room.

The air is thick with competing scents - mint, sulfur, something
floral, something decidedly not floral. Labels in cramped handwriting
mark mysterious concoctions.

A small sign reads: "You break it, you drink it."
""",
        "area_type": "shop",
        "flags": ["shop"],
    },
    
    "tavern": {
        "key": "The Tipsy Sprite",
        "desc": """
Warm light and the smell of cooking food welcome you into this
comfortable tavern. Worn wooden tables fill the common room, and
a long bar dominates one wall.

A fire crackles in the hearth. The sound of conversation and the
occasional burst of laughter create a cozy atmosphere.

Stairs in the back lead to rooms above.
""",
        "area_type": "tavern",
        "ambient_sounds": [
            "Someone laughs at a joke you didn't hear.",
            "Glasses clink together in a toast.",
            "The fire pops and crackles.",
            "A bard in the corner strums a soft melody.",
            "The tavern keeper wipes down the bar.",
        ],
        "flags": ["social"],
    },
    
    "trading_post": {
        "key": "Grove Trading Post",
        "desc": """
This no-nonsense establishment is all business. Scales, weights, and
measuring tools cover every surface. Crates and barrels hold sorted
materials awaiting transport.

A large chalkboard displays current buying prices for common goods.
The numbers change frequently.

This is where gatherers turn their hauls into coin.
""",
        "area_type": "shop",
        "flags": ["shop"],
    },
}


# =============================================================================
# Market NPCs
# =============================================================================

MARKET_NPCS = {
    "tool_vendor": {
        "key": "Greta the Toolsmith",
        "aliases": ["greta", "toolsmith", "tool vendor", "vendor"],
        "desc": """
A sturdy woman with arms like tree trunks and a no-nonsense demeanor.
Her hands are calloused from years of forge work, and her apron is
marked with old burn scars.

Despite her gruff appearance, her eyes crinkle with good humor when
she talks about her craft.
""",
        "location": "tool_shop",
        "shop_type": "tools",
        "dialogue_root": "tool_vendor_greeting",
    },
    
    "apothecary": {
        "key": "Whisper the Apothecary",
        "aliases": ["whisper", "apothecary", "potion seller"],
        "desc": """
An androgynous figure in flowing robes, with sharp eyes behind
thick spectacles. They move with precise, economical gestures,
and speak barely above a whisper.

Strange stains mark their fingers. You're not sure you want to
know what they've been working with.
""",
        "location": "apothecary_shop",
        "shop_type": "potions",
        "dialogue_root": "apothecary_greeting",
    },
    
    "tavern_keeper": {
        "key": "Big Tom",
        "aliases": ["tom", "barkeep", "innkeeper", "tavern keeper"],
        "desc": """
A massive man with a surprisingly gentle voice. His bald head
gleams in the firelight, and his impressive mustache is his
obvious pride.

He keeps a heavy cudgel behind the bar, but you've never seen
him need it. His disappointed look is weapon enough.
""",
        "location": "tavern",
        "shop_type": "food",
        "dialogue_root": "tavern_greeting",
    },
    
    "trader": {
        "key": "Sal the Buyer",
        "aliases": ["sal", "buyer", "trader"],
        "desc": """
A wiry figure with quick eyes and quicker fingers on the scales.
They dress practically in a leather vest covered with pockets,
each holding different tools of the trade.

Sal has a reputation for fair dealing - unusual in their line
of work.
""",
        "location": "trading_post",
        "shop_type": "materials",
        "dialogue_root": "buyer_greeting",
    },
}


# =============================================================================
# Builder Function
# =============================================================================

def build_market(hub_room):
    """
    Build the Market Square and all shops.
    
    Args:
        hub_room: Room to connect market to (usually Gate Plaza)
    
    Returns:
        dict: Created rooms keyed by room key
    """
    from evennia import create_object, search_object
    from typeclasses.rooms import Room
    from world.npcs import create_npc, NPC_TEMPLATES
    from world.shops import setup_shop
    
    rooms = {}
    
    # Create rooms
    for room_key, room_data in MARKET_ROOMS.items():
        room = create_object(
            Room,
            key=room_data["key"],
            attributes=[
                ("desc", room_data["desc"].strip()),
            ]
        )
        
        room.db.area_name = "Market Square"
        room.db.area_type = room_data.get("area_type", "market")
        room.db.ambient_sound_pool = room_data.get("ambient_sounds", [])
        
        for flag in room_data.get("flags", []):
            room.tags.add(flag, category="room_flag")
        
        rooms[room_key] = room
        logger.log_info(f"Created market room: {room_data['key']}")
    
    # Create exits from hub to market
    hub_room.db.desc = hub_room.db.desc or ""
    
    # Exit from hub to market square
    create_object(
        "typeclasses.exits.Exit",
        key="market",
        aliases=["market square", "shops"],
        location=hub_room,
        destination=rooms["market_square"],
        attributes=[("desc", "The bustling market square awaits.")]
    )
    
    # Exit back to hub
    create_object(
        "typeclasses.exits.Exit",
        key="plaza",
        aliases=["gate", "gate plaza", "south"],
        location=rooms["market_square"],
        destination=hub_room,
        attributes=[("desc", "Back to the central plaza.")]
    )
    
    # Connect shops to market square
    shop_exits = [
        ("market_square", "tool_shop", "tools", ["tool shop", "honest work", "east"], "west", ["market", "square", "out"]),
        ("market_square", "apothecary_shop", "apothecary", ["potions", "flask", "north"], "south", ["market", "square", "out"]),
        ("market_square", "tavern", "tavern", ["tipsy sprite", "inn", "bar", "west"], "east", ["market", "square", "out"]),
        ("market_square", "trading_post", "trading post", ["trader", "sell", "northwest"], "southeast", ["market", "square", "out"]),
    ]
    
    for from_key, to_key, exit_name, exit_aliases, return_name, return_aliases in shop_exits:
        # Exit to shop
        create_object(
            "typeclasses.exits.Exit",
            key=exit_name,
            aliases=exit_aliases,
            location=rooms[from_key],
            destination=rooms[to_key],
        )
        
        # Exit back
        create_object(
            "typeclasses.exits.Exit",
            key=return_name,
            aliases=return_aliases,
            location=rooms[to_key],
            destination=rooms[from_key],
        )
    
    # Create NPCs
    for npc_key, npc_data in MARKET_NPCS.items():
        location_key = npc_data.get("location")
        location = rooms.get(location_key)
        
        if not location:
            continue
        
        # Create NPC as Character
        npc = create_object(
            "typeclasses.characters.Character",
            key=npc_data["key"],
            location=location,
        )
        
        npc.db.desc = npc_data.get("desc", "").strip()
        
        # Add aliases
        if npc_data.get("aliases"):
            npc.aliases.add(npc_data["aliases"])
        
        # Set up as NPC
        npc.tags.add("npc", category="object_type")
        npc.db.npc_template = npc_key
        npc.db.npc_data = {
            "dialogue_root": npc_data.get("dialogue_root", "shopkeeper_greeting"),
            "flags": ["merchant"],
        }
        npc.db.npc_memory = {}
        npc.db.npc_state = {"current_activity": "shopkeeping"}
        
        # Set up shop
        shop_type = npc_data.get("shop_type")
        if shop_type:
            setup_shop(npc, shop_type)
            logger.log_info(f"Set up {shop_type} shop on {npc_data['key']}")
        
        logger.log_info(f"Created NPC: {npc_data['key']} in {location.key}")
    
    logger.log_info(f"Built Market with {len(rooms)} rooms and {len(MARKET_NPCS)} NPCs")
    
    return rooms


def cleanup_market():
    """Remove all market rooms and NPCs."""
    from evennia import search_object
    
    # Find and delete market rooms
    for room_data in MARKET_ROOMS.values():
        results = search_object(room_data["key"])
        for obj in results:
            if hasattr(obj, 'db') and obj.db.area_name == "Market Square":
                obj.delete()
    
    # Delete NPCs
    for npc_data in MARKET_NPCS.values():
        results = search_object(npc_data["key"])
        for obj in results:
            obj.delete()
