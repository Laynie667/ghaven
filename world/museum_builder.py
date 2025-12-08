"""
Museum Builder

Detailed construction of The Curator's Museum.

The museum is organized into:
- PUBLIC WINGS: Accessible to all visitors
- SEMI-PRIVATE: By appointment or invitation
- BASEMENT: Invitation only. What happens below, stays below.

Run standalone:
    py from world.museum_builder import build_museum; m = build_museum()
    
Or as part of Grove:
    Automatically called by grove_builder.build_grove()
"""

from world.builder_utils import create_room, create_exit_pair, create_door
from evennia.utils.create import create_object


def build_museum_public() -> dict:
    """Build the public museum wings."""
    rooms = {}
    
    # =========================================================================
    # ENTRANCE AND RECEPTION
    # =========================================================================
    
    rooms["entrance"] = create_room(
        "Museum of the Nine Realms",
        "typeclasses.rooms.museum.MuseumEntrance",
    )
    
    rooms["reception"] = create_room(
        "Reception Hall",
        "typeclasses.rooms.museum.MuseumReception",
    )
    
    # Connect entrance to reception
    create_exit_pair(
        rooms["entrance"], rooms["reception"],
        "in", "entrance",
        ["inside", "reception"], ["out", "exit", "leave"]
    )
    
    # =========================================================================
    # COLLECTION WINGS
    # =========================================================================
    
    rooms["fossil_wing"] = create_room(
        "Fossil Wing",
        "typeclasses.rooms.museum.FossilWing",
    )
    
    rooms["fauna_wing"] = create_room(
        "Fauna Wing",
        "typeclasses.rooms.museum.FaunaWing",
    )
    
    rooms["flora_wing"] = create_room(
        "Flora Wing",
        "typeclasses.rooms.museum.FloraWing",
    )
    
    rooms["aquarium"] = create_room(
        "Aquarium Wing",
        "typeclasses.rooms.museum.AquariumWing",
    )
    
    rooms["insectarium"] = create_room(
        "Insectarium",
        "typeclasses.rooms.museum.Insectarium",
    )
    
    rooms["art_gallery"] = create_room(
        "Art Gallery",
        "typeclasses.rooms.museum.ArtGallery",
    )
    
    rooms["library"] = create_room(
        "Library",
        "typeclasses.rooms.museum.Library",
    )
    
    rooms["relics_hall"] = create_room(
        "Relics Hall",
        "typeclasses.rooms.museum.RelicsHall",
    )
    
    # =========================================================================
    # WING CONNECTIONS FROM RECEPTION
    # =========================================================================
    
    # Natural history cluster (west side)
    create_exit_pair(
        rooms["reception"], rooms["fossil_wing"],
        "fossils", "reception",
        ["fossil", "fossil wing", "west"], ["back", "reception"]
    )
    
    create_exit_pair(
        rooms["fossil_wing"], rooms["fauna_wing"],
        "fauna", "fossils",
        ["fauna wing", "creatures"], ["fossil wing", "back"]
    )
    
    create_exit_pair(
        rooms["fauna_wing"], rooms["flora_wing"],
        "flora", "fauna",
        ["flora wing", "plants"], ["fauna wing", "back"]
    )
    
    # Living specimens cluster (north side)
    create_exit_pair(
        rooms["reception"], rooms["aquarium"],
        "aquarium", "reception",
        ["fish", "aquarium wing", "north"], ["back", "reception"]
    )
    
    create_exit_pair(
        rooms["aquarium"], rooms["insectarium"],
        "insects", "aquarium",
        ["insectarium", "bugs"], ["fish", "aquarium"]
    )
    
    # Cultural cluster (east side)
    create_exit_pair(
        rooms["reception"], rooms["art_gallery"],
        "gallery", "reception",
        ["art", "art gallery", "east"], ["back", "reception"]
    )
    
    create_exit_pair(
        rooms["art_gallery"], rooms["library"],
        "library", "gallery",
        ["books", "reading room"], ["art", "gallery"]
    )
    
    # Relics (special - south side, more secure)
    create_exit_pair(
        rooms["reception"], rooms["relics_hall"],
        "relics", "reception",
        ["relics hall", "artifacts", "south"], ["back", "reception"]
    )
    
    # =========================================================================
    # CROSS-CONNECTIONS BETWEEN WINGS
    # =========================================================================
    
    # Flora connects to Aquarium (aquatic plants)
    create_exit_pair(
        rooms["flora_wing"], rooms["aquarium"],
        "aquatic plants", "botanical specimens",
        ["aquarium"], ["flora"]
    )
    
    # Insectarium connects to Flora (pollinators)
    create_exit_pair(
        rooms["insectarium"], rooms["flora_wing"],
        "pollinator garden", "insect specimens",
        ["flora", "garden"], ["insects", "bugs"]
    )
    
    return rooms


def build_museum_private() -> dict:
    """Build semi-private museum areas."""
    rooms = {}
    
    # =========================================================================
    # CURATOR'S OFFICE
    # =========================================================================
    
    rooms["curator_office"] = create_room(
        "Curator's Office",
        "typeclasses.rooms.museum.CuratorOffice",
    )
    
    # =========================================================================
    # STAFF AREAS (simple rooms for now)
    # =========================================================================
    
    rooms["workroom"] = create_room(
        "Specimen Workroom",
        "typeclasses.rooms.museum.MuseumRoomBase",
        desc="""
|cSpecimen Workroom|n

Behind-the-scenes space where specimens are prepared for display. 
Workbenches hold tools of preservation, documentation, and preparation. 
The smell of chemicals is stronger here.

Staff access only. Visitors require escort.
""",
        wing="Staff",
        restricted=True,
    )
    
    rooms["storage"] = create_room(
        "Collection Storage",
        "typeclasses.rooms.museum.MuseumRoomBase",
        desc="""
|cCollection Storage|n

Climate-controlled storage for specimens not currently on display. 
Rows of shelving, carefully labeled boxes, and preservation containers 
extend into the darkness.

Everything has a place. Everything is documented.
""",
        wing="Staff",
        restricted=True,
    )
    
    return rooms


def build_museum_basement() -> dict:
    """Build the basement. Invitation only."""
    rooms = {}
    
    # =========================================================================
    # ACCESS POINTS
    # =========================================================================
    
    rooms["basement_entrance"] = create_room(
        "An Unmarked Door",
        "typeclasses.rooms.museum.BasementEntrance",
    )
    
    rooms["basement_stairs"] = create_room(
        "The Descent",
        "typeclasses.rooms.museum.BasementStairs",
    )
    
    # =========================================================================
    # MAIN BASEMENT
    # =========================================================================
    
    rooms["basement_main"] = create_room(
        "Basement - Main Hall",
        "typeclasses.rooms.museum.BasementMain",
    )
    
    # =========================================================================
    # BASEMENT CHAMBERS
    # =========================================================================
    
    rooms["breeding_chambers"] = create_room(
        "Breeding Chambers",
        "typeclasses.rooms.museum.BreedingChambers",
    )
    
    rooms["holding_cells"] = create_room(
        "Holding Cells",
        "typeclasses.rooms.museum.HoldingCells",
    )
    
    rooms["private_collection"] = create_room(
        "The Private Collection",
        "typeclasses.rooms.museum.PrivateCollection",
    )
    
    rooms["processing"] = create_room(
        "Processing Room",
        "typeclasses.rooms.museum.ProcessingRoom",
    )
    
    rooms["curator_quarters"] = create_room(
        "Curator's Quarters",
        "typeclasses.rooms.museum.CuratorQuarters",
    )
    
    # =========================================================================
    # BASEMENT CONNECTIONS
    # =========================================================================
    
    # Entrance to stairs (locked door)
    create_door(
        rooms["basement_entrance"], rooms["basement_stairs"],
        "basement door", "door",
        ["door", "down"], ["up", "back"],
        is_open=False,
        is_locked=True,
        key_id="basement_access",
    )
    
    # Stairs to main hall
    create_exit_pair(
        rooms["basement_stairs"], rooms["basement_main"],
        "down", "up",
        ["continue", "descend"], ["stairs", "ascend", "leave"]
    )
    
    # Main hall to chambers
    create_exit_pair(
        rooms["basement_main"], rooms["breeding_chambers"],
        "breeding chambers", "main hall",
        ["breeding", "chambers"], ["back", "hall"]
    )
    
    create_exit_pair(
        rooms["basement_main"], rooms["holding_cells"],
        "holding cells", "main hall",
        ["holding", "cells"], ["back", "hall"]
    )
    
    create_exit_pair(
        rooms["basement_main"], rooms["private_collection"],
        "private collection", "main hall",
        ["collection", "private"], ["back", "hall"]
    )
    
    create_exit_pair(
        rooms["basement_main"], rooms["processing"],
        "processing", "main hall",
        ["processing room"], ["back", "hall"]
    )
    
    # Curator's quarters (from main hall, special)
    create_door(
        rooms["basement_main"], rooms["curator_quarters"],
        "private quarters", "main hall",
        ["quarters", "curator"], ["out", "hall"],
        is_open=False,
        is_locked=True,
        key_id="curator_private",
    )
    
    # =========================================================================
    # INTERNAL BASEMENT CONNECTIONS
    # =========================================================================
    
    # Holding leads to processing (specimen flow)
    create_exit_pair(
        rooms["holding_cells"], rooms["processing"],
        "to processing", "from holding",
        ["processing"], ["holding", "cells"]
    )
    
    # Processing leads to breeding OR collection (outcomes)
    create_exit_pair(
        rooms["processing"], rooms["breeding_chambers"],
        "to breeding", "from processing",
        ["breeding"], ["processing"]
    )
    
    create_exit_pair(
        rooms["processing"], rooms["private_collection"],
        "to collection", "from processing",
        ["collection"], ["processing"]
    )
    
    # Curator's quarters connects to private collection (personal viewing)
    create_door(
        rooms["curator_quarters"], rooms["private_collection"],
        "viewing passage", "curator's passage",
        ["collection", "passage"], ["quarters", "private"],
        is_open=True,
        is_locked=False,
    )
    
    return rooms


def build_museum() -> dict:
    """
    Build the complete museum.
    
    Returns:
        Dict of all museum rooms organized by area
    """
    all_rooms = {
        "public": build_museum_public(),
        "private": build_museum_private(),
        "basement": build_museum_basement(),
    }
    
    # =========================================================================
    # CONNECT AREAS
    # =========================================================================
    
    public = all_rooms["public"]
    private = all_rooms["private"]
    basement = all_rooms["basement"]
    
    # Office from reception (by appointment)
    create_door(
        public["reception"], private["curator_office"],
        "office door", "reception",
        ["office", "curator office", "curator"], ["out", "reception"],
        is_open=False,
        is_locked=True,
        key_id="office_appointment",
    )
    
    # Workroom from relics (staff access)
    create_door(
        public["relics_hall"], private["workroom"],
        "staff door", "relics hall",
        ["staff", "workroom"], ["out", "relics"],
        is_open=False,
        is_locked=True,
        key_id="staff_access",
    )
    
    # Storage from workroom
    create_exit_pair(
        private["workroom"], private["storage"],
        "storage", "workroom",
        ["collection storage"], ["back", "work"]
    )
    
    # Basement entrance (hidden in reception)
    # This exit is NOT obvious - players must discover it or be told
    create_door(
        public["reception"], basement["basement_entrance"],
        "unmarked door", "museum",
        ["unmarked", "plain door"], ["out", "back", "museum"],
        is_open=False,
        is_locked=False,  # Finding it is the challenge
    )
    
    # Also accessible from Curator's office (private access)
    create_door(
        private["curator_office"], basement["basement_stairs"],
        "private stair", "office",
        ["basement", "stairs", "down"], ["up", "office"],
        is_open=False,
        is_locked=True,
        key_id="curator_basement",
    )
    
    # =========================================================================
    # SUMMARY
    # =========================================================================
    
    total_rooms = (
        len(all_rooms["public"]) + 
        len(all_rooms["private"]) + 
        len(all_rooms["basement"])
    )
    
    print(f"Museum built successfully!")
    print(f"  Public wings: {len(all_rooms['public'])} rooms")
    print(f"  Private areas: {len(all_rooms['private'])} rooms")
    print(f"  Basement: {len(all_rooms['basement'])} rooms")
    print(f"  Total: {total_rooms} rooms")
    
    return all_rooms


# =============================================================================
# EXPORTS
# =============================================================================

__all__ = [
    "build_museum",
    "build_museum_public",
    "build_museum_private", 
    "build_museum_basement",
]
