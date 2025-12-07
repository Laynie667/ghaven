"""
Gilderhaven Area Content
========================

Pre-built content for Grove areas. Each module contains:
- Resource definitions (gatherable nodes)
- Hazardous flora/fauna definitions
- Room triggers (entry, ambient, time-based)
- Scenes (branching encounters and events)
- Setup helper functions

Areas:
- whisperwood: Forest, bugs, foraging, mushrooms
- moonshallow: Pond, fishing, frogs, water creatures  
- sunny_meadow: Flowers, herbs, bees, pollen effects
- copper_hill: Mining, caves, gems, fossils
- tidepools: Beach, shells, crabs, treasure
- museum: The Curator's domain, exhibits, collections
- market: Shops, trading, economy hub

Usage:
    from content.whisperwood import setup_whisperwood_room, WHISPERWOOD_RESOURCES
    from content.moonshallow import setup_moonshallow_room
    from content.sunny_meadow import setup_meadow_room
    from content.copper_hill import setup_copper_hill_room
    from content.tidepools import setup_tidepools_room
    
    # In room setup:
    setup_whisperwood_room(room, "edge")  # or "paths", "clearing", "stump"
    setup_moonshallow_room(room, "shore")  # or "shallows", "deep", "cove"
    setup_meadow_room(room, "gate")  # or "fields", "garden", "hilltop"
    setup_copper_hill_room(room, "base")  # or "tunnels", "cavern", "deep"
    setup_tidepools_room(room, "beach")  # or "pools", "shore", "cove"
"""

# Import scene registrations (auto-registers scenes)
from . import whisperwood
from . import moonshallow
from . import sunny_meadow
from . import copper_hill
from . import tidepools
from . import museum
from . import market

# Convenient imports
from .whisperwood import setup_whisperwood_room, WHISPERWOOD_RESOURCES, WHISPERWOOD_HAZARDS
from .moonshallow import setup_moonshallow_room, MOONSHALLOW_RESOURCES
from .sunny_meadow import setup_meadow_room, SUNNY_MEADOW_RESOURCES, SUNNY_MEADOW_HAZARDS
from .copper_hill import setup_copper_hill_room, COPPER_HILL_RESOURCES
from .tidepools import setup_tidepools_room, TIDEPOOLS_RESOURCES
from .museum import MUSEUM_ROOMS, CURATOR_NPC, MUSEUM_SCENES
from .market import MARKET_ROOMS, MARKET_NPCS

# Area builders
from .builders import (
    build_whisperwood,
    build_moonshallow,
    build_sunny_meadow,
    build_copper_hill,
    build_tidepools,
    build_all_newbie_areas,
    build_museum,
    build_market,
    cleanup_area,
    cleanup_museum,
    cleanup_market,
)
