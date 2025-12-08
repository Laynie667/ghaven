"""
Room Typeclasses

Usage:
    from typeclasses.rooms import Room, IndoorRoom, OutdoorRoom
    from typeclasses.rooms import GroveRoom, PlayerHome
    from typeclasses.rooms import MuseumEntrance, FossilWing, BasementMain
    from typeclasses.rooms import GridRoom, GridOutdoorRoom
"""

# Import base classes first
from typeclasses.base_rooms import (
    Room,
    IndoorRoom,
    OutdoorRoom,
    ATMOSPHERE_PRESETS,
    TimeOfDay,
    Weather,
    Season,
    CrowdLevel,
    Partition,
)

from typeclasses.rooms.grid import (
    GridPosition,
    GridRoomMixin,
    GridRoom,
    GridIndoorRoom,
    GridOutdoorRoom,
    create_plaza_grid,
    create_linear_grid,
)

from typeclasses.rooms.grove import (
    GroveRoom,
    GroveIndoor,
    GatePlazaRoom,
    MarketRoom,
    ShopRoom,
    ServicesRoom,
    ResidentialStreet,
    PlayerHome,
    OrchardRoom,
    WaterfrontRoom,
    TavernRoom,
    GamblingRoom,
    BathhouseRoom,
    InnRoom,
    OverlookRoom,
)

from typeclasses.rooms.museum import (
    MuseumRoomBase,
    MuseumEntrance,
    MuseumReception,
    FossilWing,
    FaunaWing,
    FloraWing,
    AquariumWing,
    Insectarium,
    ArtGallery,
    Library,
    RelicsHall,
    CuratorOffice,
    BasementEntrance,
    BasementStairs,
    BasementMain,
    BreedingChambers,
    HoldingCells,
    PrivateCollection,
    ProcessingRoom,
    CuratorQuarters,
)

__all__ = [
    # Base
    "Room",
    "IndoorRoom", 
    "OutdoorRoom",
    "ATMOSPHERE_PRESETS",
    "TimeOfDay",
    "Weather",
    "Season",
    "CrowdLevel",
    "Partition",
    
    # Grid
    "GridPosition",
    "GridRoomMixin",
    "GridRoom",
    "GridIndoorRoom",
    "GridOutdoorRoom",
    "create_plaza_grid",
    "create_linear_grid",
    
    # Grove
    "GroveRoom",
    "GroveIndoor",
    "GatePlazaRoom",
    "MarketRoom",
    "ShopRoom",
    "ServicesRoom",
    "ResidentialStreet",
    "PlayerHome",
    "OrchardRoom",
    "WaterfrontRoom",
    "TavernRoom",
    "GamblingRoom",
    "BathhouseRoom",
    "InnRoom",
    "OverlookRoom",
    
    # Museum
    "MuseumRoomBase",
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
    "CuratorOffice",
    "BasementEntrance",
    "BasementStairs",
    "BasementMain",
    "BreedingChambers",
    "HoldingCells",
    "PrivateCollection",
    "ProcessingRoom",
    "CuratorQuarters",
]
