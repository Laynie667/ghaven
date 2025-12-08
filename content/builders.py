"""
Area Builders for Gilderhaven
==============================

Batch commands to deploy the content areas.
Each creates rooms, sets attributes, links exits, and populates resources.

Usage (in-game as admin):
    @py from content.builders import build_whisperwood; build_whisperwood(here)
    @py from content.builders import build_moonshallow; build_moonshallow(here)
    @py from content.builders import build_sunny_meadow; build_sunny_meadow(here)
    @py from content.builders import build_copper_hill; build_copper_hill(here)
    @py from content.builders import build_tidepools; build_tidepools(here)
    
Or build all from a central hub:
    @py from content.builders import build_all_newbie_areas; build_all_newbie_areas(here)

Connect Limbo to your hub:
    @py from content.builders import connect_limbo; connect_limbo(here)
"""

from evennia import create_object, search_object
from evennia.utils import logger


# =============================================================================
# Helper Functions
# =============================================================================

def create_room(key, desc, typeclass="typeclasses.rooms.Room", **kwargs):
    """Create a room with description."""
    room = create_object(typeclass, key=key)
    room.db.desc = desc
    
    for attr, value in kwargs.items():
        setattr(room.db, attr, value)
    
    return room


def create_exit_one_way(source, destination, key, aliases=None):
    """Create a one-way exit."""
    aliases = aliases or []
    
    exit_obj = create_object(
        "evennia.objects.objects.DefaultExit",
        key=key,
        location=source,
        destination=destination,
    )
    if aliases:
        exit_obj.aliases.add(aliases)
    
    return exit_obj


def link_rooms(room1, room2, exit1_name, exit2_name, aliases1=None, aliases2=None):
    """
    Create two-way exits between rooms.
    
    Args:
        room1: First room
        room2: Second room
        exit1_name: Name of exit from room1 to room2
        exit2_name: Name of exit from room2 to room1
        aliases1: Aliases for exit from room1
        aliases2: Aliases for exit from room2
    """
    aliases1 = aliases1 or []
    aliases2 = aliases2 or []
    
    # room1 -> room2
    create_exit_one_way(room1, room2, exit1_name, aliases1)
    
    # room2 -> room1
    create_exit_one_way(room2, room1, exit2_name, aliases2)


def connect_limbo(hub_room):
    """
    Connect Limbo (#2) to the hub room.
    
    Args:
        hub_room: The hub room to connect to
    """
    limbo = search_object("#2")
    if limbo:
        limbo = limbo[0]
        create_exit_one_way(limbo, hub_room, "grove", ["plaza", "hub", "gate"])
        create_exit_one_way(hub_room, limbo, "limbo", ["void"])
        logger.log_info(f"Connected Limbo to {hub_room.key}")
        return True
    return False


# =============================================================================
# Whisperwood Builder
# =============================================================================

def build_whisperwood(hub_room):
    """
    Build Whisperwood Forest area.
    
    Args:
        hub_room: The room to connect Whisperwood entrance to (e.g., Grove)
    
    Returns:
        dict: Created rooms keyed by name
    """
    from content.whisperwood import WHISPERWOOD_RESOURCES
    
    rooms = {}
    
    # Entrance
    rooms["entrance"] = create_room(
        "Whisperwood Entrance",
        "Ancient trees arch overhead, their branches intertwining to form a natural "
        "gateway into the forest. Dappled sunlight filters through the canopy, and the "
        "air is thick with the scent of moss and wildflowers. A well-worn path leads "
        "deeper into the woods.",
        area_name="Whisperwood",
        area_type="forest",
    )
    
    # Mushroom Grove
    rooms["mushroom_grove"] = create_room(
        "Mushroom Grove",
        "A clearing carpeted with mushrooms of every color imaginable. Some glow faintly "
        "with bioluminescence, while others release gentle puffs of spores when disturbed. "
        "Fallen logs provide homes for countless fungi, and the air smells earthy and rich.",
        area_name="Whisperwood",
        resource_nodes=[
            WHISPERWOOD_RESOURCES.get("mushroom_patch", {}),
            WHISPERWOOD_RESOURCES.get("glowing_fungi", {}),
        ],
        scene_triggers=["whisperwood_mushroom_01"],
    )
    
    # Flower Meadow
    rooms["flower_meadow"] = create_room(
        "Wildflower Meadow",
        "A sun-dappled clearing bursting with wildflowers. Butterflies dance between "
        "blooms while bees hum lazily from flower to flower. The grass is soft and "
        "inviting, perfect for lying back and watching clouds drift overhead.",
        area_name="Whisperwood",
        resource_nodes=[
            WHISPERWOOD_RESOURCES.get("wildflower_patch", {}),
            WHISPERWOOD_RESOURCES.get("butterfly_spot", {}),
        ],
        scene_triggers=["whisperwood_hornets_01"],
    )
    
    # Deep Woods
    rooms["deep_woods"] = create_room(
        "Deep Woods",
        "The forest grows darker and older here. Massive trees tower overhead, their "
        "trunks wider than houses. Strange sounds echo through the undergrowth, and "
        "the shadows seem to move with purpose. There's magic in this place - ancient "
        "and watchful.",
        area_name="Whisperwood",
        resource_nodes=[
            WHISPERWOOD_RESOURCES.get("ancient_herbs", {}),
            WHISPERWOOD_RESOURCES.get("rare_insects", {}),
        ],
        scene_triggers=["whisperwood_fae_01"],
        ambient_sounds=["rustling leaves", "distant owl", "creaking branches"],
    )
    
    # Slime Hollow
    rooms["slime_hollow"] = create_room(
        "Slime Hollow",
        "A damp depression in the forest floor where strange gelatinous creatures "
        "congregate. Slimes of various sizes and colors ooze between rocks and roots, "
        "leaving glistening trails. They seem harmless enough, though some are quite "
        "large.",
        area_name="Whisperwood",
        resource_nodes=[
            WHISPERWOOD_RESOURCES.get("slime_residue", {}),
        ],
        scene_triggers=["whisperwood_slime_01"],
    )
    
    # Link to hub
    link_rooms(hub_room, rooms["entrance"], "whisperwood", "gate plaza", 
               ["forest", "woods"], ["back", "hub", "plaza", "grove"])
    
    # Internal links
    link_rooms(rooms["entrance"], rooms["mushroom_grove"], "north", "south",
               ["n", "grove", "mushrooms"], ["s", "entrance", "back"])
    link_rooms(rooms["entrance"], rooms["flower_meadow"], "east", "west",
               ["e", "meadow", "flowers"], ["w", "entrance", "back"])
    link_rooms(rooms["mushroom_grove"], rooms["deep_woods"], "north", "south",
               ["n", "deeper", "deep"], ["s", "grove", "mushrooms"])
    link_rooms(rooms["flower_meadow"], rooms["slime_hollow"], "north", "south",
               ["n", "hollow", "slime"], ["s", "meadow", "flowers"])
    link_rooms(rooms["deep_woods"], rooms["slime_hollow"], "east", "west",
               ["e", "hollow"], ["w", "deep"])
    
    logger.log_info(f"Built Whisperwood: {len(rooms)} rooms")
    return rooms


# =============================================================================
# Moonshallow Pond Builder
# =============================================================================

def build_moonshallow(hub_room):
    """
    Build Moonshallow Pond area.
    
    Args:
        hub_room: The room to connect entrance to
    
    Returns:
        dict: Created rooms
    """
    from content.moonshallow import MOONSHALLOW_RESOURCES
    
    rooms = {}
    
    # Pond Shore
    rooms["shore"] = create_room(
        "Moonshallow Shore",
        "The shore of a serene pond that glimmers with an otherworldly light. Reeds "
        "sway gently at the water's edge, and lily pads dot the surface. At night, "
        "the water is said to reflect not the sky above, but strange constellations "
        "from somewhere else entirely.",
        area_name="Moonshallow",
        area_type="water",
        resource_nodes=[
            MOONSHALLOW_RESOURCES.get("reed_bed", {}),
            MOONSHALLOW_RESOURCES.get("shore_fishing", {}),
        ],
    )
    
    # Lily Pad Garden
    rooms["lily_pads"] = create_room(
        "Lily Pad Garden",
        "A section of the pond thick with enormous lily pads, some large enough to "
        "stand on (briefly). Frogs of unusual colors perch on the pads, their songs "
        "creating an otherworldly chorus. Dragonflies with iridescent wings zip "
        "between the flowers.",
        area_name="Moonshallow",
        resource_nodes=[
            MOONSHALLOW_RESOURCES.get("lily_flowers", {}),
            MOONSHALLOW_RESOURCES.get("pond_frogs", {}),
        ],
        scene_triggers=["moonshallow_frogs_01"],
    )
    
    # Deep Pool
    rooms["deep_pool"] = create_room(
        "The Deep Pool",
        "The pond deepens here into a pool of impossible depth. The water is crystal "
        "clear yet seems to go down forever, fading into darkness that occasionally "
        "pulses with faint, mysterious light. Something ancient rests at the bottom.",
        area_name="Moonshallow",
        resource_nodes=[
            MOONSHALLOW_RESOURCES.get("deep_fishing", {}),
            MOONSHALLOW_RESOURCES.get("glowing_algae", {}),
        ],
        scene_triggers=["moonshallow_ancient_01"],
        ambient_sounds=["water lapping", "distant bubbling", "strange hum"],
    )
    
    # Turtle Rock
    rooms["turtle_rock"] = create_room(
        "Turtle Rock",
        "A large flat rock juts from the shallows, worn smooth by countless seasons. "
        "Turtles of all sizes bask here in the sunlight, their shells patterned with "
        "strange geometric designs. One massive turtle seems to have been here forever.",
        area_name="Moonshallow",
        resource_nodes=[
            MOONSHALLOW_RESOURCES.get("turtle_spot", {}),
        ],
        scene_triggers=["moonshallow_turtle_01"],
    )
    
    # Moon Altar
    rooms["altar"] = create_room(
        "Moon Altar",
        "A small island in the center of the pond holds an ancient stone altar covered "
        "in glowing runes. The water around it is perfectly still, and the air hums "
        "with latent magic. On full moons, the altar is said to grant visions to those "
        "who leave offerings.",
        area_name="Moonshallow",
        special_location=True,
        scene_triggers=["moonshallow_moonfish_01"],
    )
    
    # Link to hub
    link_rooms(hub_room, rooms["shore"], "moonshallow", "gate plaza",
               ["pond", "water", "moon"], ["back", "hub", "plaza", "grove"])
    
    # Internal links
    link_rooms(rooms["shore"], rooms["lily_pads"], "east", "west",
               ["e", "lilies", "lily"], ["w", "shore", "back"])
    link_rooms(rooms["shore"], rooms["turtle_rock"], "north", "south",
               ["n", "rock", "turtle"], ["s", "shore", "back"])
    link_rooms(rooms["lily_pads"], rooms["deep_pool"], "north", "south",
               ["n", "deep", "pool"], ["s", "lilies", "lily"])
    link_rooms(rooms["turtle_rock"], rooms["deep_pool"], "east", "west",
               ["e", "pool"], ["w", "rock", "turtle"])
    link_rooms(rooms["deep_pool"], rooms["altar"], "north", "south",
               ["n", "altar", "island"], ["s", "pool", "deep"])
    
    logger.log_info(f"Built Moonshallow: {len(rooms)} rooms")
    return rooms


# =============================================================================
# Sunny Meadow Builder
# =============================================================================

def build_sunny_meadow(hub_room):
    """
    Build Sunny Meadow area.
    """
    from content.sunny_meadow import SUNNY_MEADOW_RESOURCES
    
    rooms = {}
    
    # Meadow Entrance
    rooms["entrance"] = create_room(
        "Sunny Meadow",
        "Rolling hills of tall grass stretch before you, dotted with wildflowers of "
        "every color. The sun seems to shine brighter here, and a warm breeze carries "
        "the scent of honey and fresh growth. Butterflies and bees fill the air with "
        "gentle motion.",
        area_name="Sunny Meadow",
        area_type="meadow",
        resource_nodes=[
            SUNNY_MEADOW_RESOURCES.get("wildflowers", {}),
            SUNNY_MEADOW_RESOURCES.get("butterfly_field", {}),
        ],
    )
    
    # Bee Garden
    rooms["bee_garden"] = create_room(
        "Bee Garden",
        "A section of meadow absolutely thick with flowering plants, tended by "
        "thousands of busy bees. Several large hives hang from an old oak tree at "
        "the center. The air is heavy with the scent of honey, and the constant "
        "buzzing is almost hypnotic.",
        area_name="Sunny Meadow",
        resource_nodes=[
            SUNNY_MEADOW_RESOURCES.get("bee_hives", {}),
            SUNNY_MEADOW_RESOURCES.get("honey_flowers", {}),
        ],
        scene_triggers=["sunny_meadow_bees_01"],
    )
    
    # Poppy Field
    rooms["poppy_field"] = create_room(
        "Passion Poppy Field",
        "A field of unusual red poppies that seem to glow faintly in the sunlight. "
        "Their scent is intoxicating and the pollen makes your head swim pleasantly. "
        "Some say these flowers have... interesting effects on those who linger too "
        "long among them.",
        area_name="Sunny Meadow",
        resource_nodes=[
            SUNNY_MEADOW_RESOURCES.get("passion_poppies", {}),
            SUNNY_MEADOW_RESOURCES.get("poppy_pollen", {}),
        ],
        scene_triggers=["sunny_meadow_poppies_01"],
        ambient_effects=["aroused", "dizzy"],
    )
    
    # Hilltop
    rooms["hilltop"] = create_room(
        "Meadow Hilltop",
        "The highest point in the meadow offers a stunning view of the surrounding "
        "lands. You can see the forest to the north, water glinting to the east, and "
        "distant mountains beyond. A perfect spot for picnics or watching the sunset.",
        area_name="Sunny Meadow",
        resource_nodes=[
            SUNNY_MEADOW_RESOURCES.get("hilltop_herbs", {}),
        ],
    )
    
    # Guardian's Circle
    rooms["guardian"] = create_room(
        "Guardian's Circle",
        "A ring of standing stones marks this sacred spot. The grass within the circle "
        "is impossibly green, and flowers bloom here regardless of season. The meadow's "
        "guardian spirit dwells here - a being of sunshine and growth who protects these "
        "lands.",
        area_name="Sunny Meadow",
        special_location=True,
        scene_triggers=["sunny_meadow_guardian_01"],
    )
    
    # Link to hub
    link_rooms(hub_room, rooms["entrance"], "meadow", "gate plaza",
               ["sunny", "sunny meadow"], ["back", "hub", "plaza", "grove"])
    
    # Internal links
    link_rooms(rooms["entrance"], rooms["bee_garden"], "east", "west",
               ["e", "bees", "garden"], ["w", "meadow", "back"])
    link_rooms(rooms["entrance"], rooms["poppy_field"], "south", "north",
               ["s", "poppies", "poppy"], ["n", "meadow", "back"])
    link_rooms(rooms["bee_garden"], rooms["hilltop"], "north", "south",
               ["n", "hill", "up", "hilltop"], ["s", "garden", "bees", "down"])
    link_rooms(rooms["poppy_field"], rooms["guardian"], "south", "north",
               ["s", "circle", "guardian", "stones"], ["n", "poppies", "poppy"])
    link_rooms(rooms["hilltop"], rooms["guardian"], "west", "east",
               ["w", "circle"], ["e", "hill", "hilltop"])
    
    logger.log_info(f"Built Sunny Meadow: {len(rooms)} rooms")
    return rooms


# =============================================================================
# Copper Hill Builder
# =============================================================================

def build_copper_hill(hub_room):
    """
    Build Copper Hill mining area.
    """
    from content.copper_hill import COPPER_HILL_RESOURCES
    
    rooms = {}
    
    # Mine Entrance
    rooms["entrance"] = create_room(
        "Copper Hill Entrance",
        "A rocky hillside rises before you, its exposed stone streaked with veins of "
        "green copper ore. A well-worn path leads to a mine entrance supported by "
        "weathered timber. The clang of distant pickaxes echoes from within.",
        area_name="Copper Hill",
        area_type="mining",
        resource_nodes=[
            COPPER_HILL_RESOURCES.get("surface_rocks", {}),
            COPPER_HILL_RESOURCES.get("clay_deposit", {}),
        ],
    )
    
    # Upper Tunnels
    rooms["upper_tunnels"] = create_room(
        "Upper Tunnels",
        "The main mining tunnels branch off in several directions. Support beams line "
        "the walls, and lanterns hang at intervals providing flickering light. Cart "
        "tracks run along the floor, and the air is thick with dust and the smell of "
        "earth.",
        area_name="Copper Hill",
        resource_nodes=[
            COPPER_HILL_RESOURCES.get("copper_vein", {}),
            COPPER_HILL_RESOURCES.get("coal_seam", {}),
        ],
        ambient_sounds=["dripping water", "distant clanging", "creaking timber"],
    )
    
    # Crystal Cavern
    rooms["crystal_cavern"] = create_room(
        "Crystal Cavern",
        "A natural cavern glitters with crystals of every color. Quartz formations "
        "catch the light and scatter rainbows across the walls. The air is cool and "
        "still, and there's a sense of timeless beauty to this hidden place.",
        area_name="Copper Hill",
        resource_nodes=[
            COPPER_HILL_RESOURCES.get("quartz_cluster", {}),
            COPPER_HILL_RESOURCES.get("gem_pocket", {}),
        ],
        scene_triggers=["copper_crystal_01"],
    )
    
    # Deep Shaft
    rooms["deep_shaft"] = create_room(
        "Deep Shaft",
        "A vertical shaft descends into darkness. A rickety elevator provides access "
        "to the lower levels, its cables groaning ominously. Strange sounds echo up "
        "from below - sounds that don't quite match what you'd expect from a mine.",
        area_name="Copper Hill",
        resource_nodes=[
            COPPER_HILL_RESOURCES.get("iron_vein", {}),
            COPPER_HILL_RESOURCES.get("glowing_mushrooms", {}),
        ],
        scene_triggers=["copper_creature_01", "copper_cavein_01"],
    )
    
    # Fossil Chamber
    rooms["fossil_chamber"] = create_room(
        "Fossil Chamber",
        "An ancient seabed preserved in stone, this chamber is filled with the remains "
        "of creatures from an impossible past. Spiral shells, strange bones, and the "
        "imprints of things that should never have existed are embedded in every surface.",
        area_name="Copper Hill",
        resource_nodes=[
            COPPER_HILL_RESOURCES.get("fossil_bed", {}),
            COPPER_HILL_RESOURCES.get("silver_vein", {}),
        ],
    )
    
    # Narrow Crevice
    rooms["crevice"] = create_room(
        "Narrow Crevice",
        "A tight squeeze between rock walls leads to a small chamber. The passage is "
        "barely wide enough for a person, and the walls seem to press in oppressively. "
        "But treasures are sometimes found in the places others can't reach.",
        area_name="Copper Hill",
        resource_nodes=[
            COPPER_HILL_RESOURCES.get("tunnel_bugs", {}),
        ],
        scene_triggers=["copper_stuck_01"],
    )
    
    # Link to hub
    link_rooms(hub_room, rooms["entrance"], "copper hill", "gate plaza",
               ["mine", "mining", "hill", "copper"], ["back", "hub", "plaza", "grove", "out"])
    
    # Internal links
    link_rooms(rooms["entrance"], rooms["upper_tunnels"], "enter", "exit",
               ["in", "mine", "tunnel", "tunnels"], ["out", "entrance", "leave", "back"])
    link_rooms(rooms["upper_tunnels"], rooms["crystal_cavern"], "east", "west",
               ["e", "crystals", "crystal", "cavern"], ["w", "tunnels", "back"])
    link_rooms(rooms["upper_tunnels"], rooms["deep_shaft"], "down", "up",
               ["d", "shaft", "deep"], ["u", "upper", "tunnels"])
    link_rooms(rooms["deep_shaft"], rooms["fossil_chamber"], "east", "west",
               ["e", "fossils", "fossil"], ["w", "shaft", "back"])
    link_rooms(rooms["crystal_cavern"], rooms["crevice"], "squeeze", "out",
               ["crevice", "narrow", "crack"], ["back", "cavern", "crystals"])
    
    logger.log_info(f"Built Copper Hill: {len(rooms)} rooms")
    return rooms


# =============================================================================
# Tidepools Builder
# =============================================================================

def build_tidepools(hub_room):
    """
    Build Tidepools beach area.
    """
    from content.tidepools import TIDEPOOLS_RESOURCES
    
    rooms = {}
    
    # Beach
    rooms["beach"] = create_room(
        "Sandy Beach",
        "A stretch of golden sand meets the gentle waves of a calm sea. Shells and "
        "driftwood litter the tideline, and seabirds wheel overhead. The salt breeze "
        "is refreshing, and the sound of the waves is endlessly soothing.",
        area_name="Tidepools",
        area_type="beach",
        resource_nodes=[
            TIDEPOOLS_RESOURCES.get("shell_scatter", {}),
            TIDEPOOLS_RESOURCES.get("driftwood_pile", {}),
        ],
    )
    
    # Rocky Tidepools
    rooms["tidepools"] = create_room(
        "Rocky Tidepools",
        "Volcanic rocks form natural pools filled with seawater and marine life. "
        "Colorful anemones, scuttling crabs, and darting fish inhabit these miniature "
        "ecosystems. Each pool is a tiny world unto itself.",
        area_name="Tidepools",
        resource_nodes=[
            TIDEPOOLS_RESOURCES.get("tidepool", {}),
            TIDEPOOLS_RESOURCES.get("tidepool_fish", {}),
            TIDEPOOLS_RESOURCES.get("seaweed_rocks", {}),
        ],
        scene_triggers=["tidepools_crab_01", "tidepools_grab_01"],
    )
    
    # Mussel Beds
    rooms["mussel_beds"] = create_room(
        "Mussel Beds",
        "Rocks completely covered in dark mussels stretch along the shoreline. The "
        "shells click and clatter as waves wash over them. Careful harvesting can "
        "yield both food and occasional pearls.",
        area_name="Tidepools",
        resource_nodes=[
            TIDEPOOLS_RESOURCES.get("mussel_bed", {}),
            TIDEPOOLS_RESOURCES.get("sea_glass_spot", {}),
        ],
    )
    
    # Fishing Rocks
    rooms["fishing_rocks"] = create_room(
        "Fishing Rocks",
        "Large flat rocks extend into deeper water, providing perfect spots for "
        "casting a line. The water here is deep enough for larger fish, and patient "
        "anglers are sometimes rewarded with impressive catches.",
        area_name="Tidepools",
        resource_nodes=[
            TIDEPOOLS_RESOURCES.get("shore_fishing", {}),
            TIDEPOOLS_RESOURCES.get("rare_shells", {}),
        ],
        scene_triggers=["tidepools_tide_01"],
    )
    
    # Hidden Cove
    rooms["cove"] = create_room(
        "Hidden Cove",
        "A secluded cove sheltered by towering cliffs. The water here is impossibly "
        "clear, and strange lights sometimes dance beneath the surface at night. "
        "Local legends speak of mermaids and buried treasure.",
        area_name="Tidepools",
        resource_nodes=[
            TIDEPOOLS_RESOURCES.get("treasure_spot", {}),
        ],
        scene_triggers=["tidepools_treasure_01", "tidepools_mermaid_01"],
        special_location=True,
    )
    
    # Link to hub
    link_rooms(hub_room, rooms["beach"], "tidepools", "gate plaza",
               ["beach", "shore", "sea", "ocean"], ["back", "hub", "plaza", "grove"])
    
    # Internal links
    link_rooms(rooms["beach"], rooms["tidepools"], "east", "west",
               ["e", "pools", "rocks", "tidepool"], ["w", "beach", "sand", "back"])
    link_rooms(rooms["beach"], rooms["mussel_beds"], "south", "north",
               ["s", "mussels", "mussel"], ["n", "beach", "back"])
    link_rooms(rooms["tidepools"], rooms["fishing_rocks"], "east", "west",
               ["e", "fishing", "fish"], ["w", "pools", "tidepool"])
    link_rooms(rooms["mussel_beds"], rooms["cove"], "south", "north",
               ["s", "cove", "hidden"], ["n", "mussels", "back"])
    link_rooms(rooms["fishing_rocks"], rooms["cove"], "south", "north",
               ["s", "cove"], ["n", "rocks", "fishing"])
    
    logger.log_info(f"Built Tidepools: {len(rooms)} rooms")
    return rooms


# =============================================================================
# Build All
# =============================================================================

def build_all_newbie_areas(hub_room):
    """
    Build all newbie areas connected to a central hub.
    
    Args:
        hub_room: Central room (like the Grove) to connect all areas to
    
    Returns:
        dict: All rooms from all areas
    """
    all_rooms = {}
    
    all_rooms["whisperwood"] = build_whisperwood(hub_room)
    all_rooms["moonshallow"] = build_moonshallow(hub_room)
    all_rooms["sunny_meadow"] = build_sunny_meadow(hub_room)
    all_rooms["copper_hill"] = build_copper_hill(hub_room)
    all_rooms["tidepools"] = build_tidepools(hub_room)
    
    total = sum(len(area) for area in all_rooms.values())
    logger.log_info(f"Built all newbie areas: {total} total rooms")
    
    hub_room.msg_contents(f"|gBuilt {total} rooms across 5 areas.|n")
    
    return all_rooms


# =============================================================================
# Cleanup
# =============================================================================

def cleanup_area(area_name):
    """
    Remove all rooms with a given area_name.
    USE WITH CAUTION.
    
    Args:
        area_name: The area_name attribute to match
    
    Returns:
        int: Number of rooms deleted
    """
    from evennia.objects.models import ObjectDB
    from django.db.models import Q
    
    # Find rooms with this area_name
    all_objects = ObjectDB.objects.all()
    to_delete = []
    
    for obj in all_objects:
        if obj.db.area_name == area_name:
            to_delete.append(obj)
    
    count = len(to_delete)
    
    for obj in to_delete:
        obj.delete()
    
    logger.log_info(f"Cleaned up {count} rooms/objects from {area_name}")
    return count


def cleanup_all_newbie_areas():
    """
    Remove all newbie area rooms.
    USE WITH CAUTION.
    
    Returns:
        int: Total rooms deleted
    """
    total = 0
    total += cleanup_area("Whisperwood")
    total += cleanup_area("Moonshallow")
    total += cleanup_area("Sunny Meadow")
    total += cleanup_area("Copper Hill")
    total += cleanup_area("Tidepools")
    
    logger.log_info(f"Cleaned up all newbie areas: {total} total rooms")
    return total


# =============================================================================
# Museum Builder
# =============================================================================

def build_museum(hub_room):
    """
    Build the Museum - The Curator's domain.
    
    Creates:
    - Museum Foyer (connects to hub)
    - Grand Gallery
    - Curiosities Wing
    - Natural History Wing
    - Curator's Office
    - Archives (restricted)
    - Restoration Room (restricted)
    - Private Chambers (private)
    
    Args:
        hub_room: The hub room to connect the museum entrance to
        
    Returns:
        dict: Created rooms by key
    """
    from content.museum import MUSEUM_ROOMS, MUSEUM_FURNITURE, MUSEUM_RESOURCES
    from world.furniture import create_furniture, place_furniture
    
    rooms = {}
    
    # -------------------------------------------------------------------------
    # Create all rooms
    # -------------------------------------------------------------------------
    
    for room_key, room_data in MUSEUM_ROOMS.items():
        room = create_room(
            key=room_data["key"],
            desc=room_data["desc"].strip(),
            area_name="Museum",
            area_type=room_data.get("area_type", "museum"),
        )
        
        # Set ambient sounds as a list for random selection (use different attr name)
        room.db.ambient_sound_pool = room_data.get("ambient_sounds", [])
        
        # Set flags
        for flag in room_data.get("flags", []):
            room.tags.add(flag, category="room_flag")
        
        # Set resources if any
        if room_key in MUSEUM_RESOURCES:
            room.db.resource_nodes = MUSEUM_RESOURCES[room_key]
        
        rooms[room_key] = room
    
    # -------------------------------------------------------------------------
    # Link rooms
    # -------------------------------------------------------------------------
    
    # Hub → Foyer
    create_exit_one_way(
        hub_room, rooms["foyer"], 
        "museum", ["the museum", "m"]
    )
    create_exit_one_way(
        rooms["foyer"], hub_room,
        "grove", ["out", "exit", "leave", "gate plaza"]
    )
    
    # Foyer → Grand Gallery
    link_rooms(
        rooms["foyer"], rooms["grand_gallery"],
        "gallery", "foyer",
        ["galleries", "in", "deeper"], ["entrance", "out"]
    )
    
    # Grand Gallery → Wings
    link_rooms(
        rooms["grand_gallery"], rooms["curiosities_wing"],
        "east", "west",
        ["curiosities", "e"], ["gallery", "w", "grand gallery"]
    )
    link_rooms(
        rooms["grand_gallery"], rooms["natural_history"],
        "west", "east",
        ["natural history", "w", "specimens"], ["gallery", "e", "grand gallery"]
    )
    
    # Grand Gallery → Curator's Office (staff door)
    link_rooms(
        rooms["grand_gallery"], rooms["curators_office"],
        "north", "south",
        ["office", "staff", "n", "curator"], ["gallery", "s", "out"]
    )
    
    # Curator's Office → Archives
    link_rooms(
        rooms["curators_office"], rooms["archives"],
        "archives", "office",
        ["records", "back"], ["out", "curator"]
    )
    
    # Natural History → Restoration Room
    link_rooms(
        rooms["natural_history"], rooms["restoration_room"],
        "restoration", "specimens",
        ["back", "authorized"], ["out", "natural history"]
    )
    
    # Curator's Office → Private Chambers
    link_rooms(
        rooms["curators_office"], rooms["private_chambers"],
        "private door", "office",
        ["chambers", "private", "bedroom"], ["out", "office"]
    )
    
    # -------------------------------------------------------------------------
    # Place furniture
    # -------------------------------------------------------------------------
    
    for room_key, furniture_list in MUSEUM_FURNITURE.items():
        if room_key not in rooms:
            continue
        
        room = rooms[room_key]
        
        for furn_data in furniture_list:
            template = furn_data["template"]
            furn = create_furniture(template)
            if furn:
                place_furniture(furn, room)
                if "position" in furn_data:
                    furn.db.position_desc = furn_data["position"]
    
    # -------------------------------------------------------------------------
    # Mark restricted areas
    # -------------------------------------------------------------------------
    
    # Set access requirements
    rooms["archives"].db.requires_permission = "curator_access"
    rooms["restoration_room"].db.requires_permission = "curator_access"
    rooms["private_chambers"].db.requires_permission = "curator_private"
    
    # -------------------------------------------------------------------------
    # Spawn the Curator
    # -------------------------------------------------------------------------
    
    from world.npcs import create_npc
    
    curator = create_npc("curator", location=rooms["foyer"])
    if curator:
        curator.db.home_room = rooms["foyer"].id
        curator.db.office_room = rooms["curators_office"].id
        curator.db.private_room = rooms["private_chambers"].id
        logger.log_info(f"Spawned The Curator in Museum Foyer")
    
    logger.log_info(f"Built Museum with {len(rooms)} rooms")
    
    return rooms


def cleanup_museum():
    """
    Remove all Museum rooms.
    
    Returns:
        int: Rooms deleted
    """
    return cleanup_area("Museum")


# =============================================================================
# Market - Re-export from market.py
# =============================================================================

def build_market(hub_room):
    """
    Build the Market Square area.
    
    Args:
        hub_room: Room to connect to (usually Gate Plaza)
    
    Returns:
        dict: Created rooms
    """
    from content.market import build_market as _build_market
    return _build_market(hub_room)


def cleanup_market():
    """Remove all Market rooms."""
    from content.market import cleanup_market as _cleanup_market
    return _cleanup_market()
