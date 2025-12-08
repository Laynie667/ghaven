"""
Builder Utilities for Gilderhaven
==================================

Helper functions for batch-creating rooms, exits, and objects.

Usage:
    from world.builder_utils import create_room, create_exit_pair, create_door
    
    room = create_room("Market Square", desc="...", typeclass="GroveRoom")
    create_exit_pair(room_a, room_b, "north", "south")
"""

from typing import Any, Dict, List, Optional, Tuple
from evennia import create_object, search_object
from evennia.utils import logger


# =============================================================================
# ROOM CREATION
# =============================================================================

def create_room(
    name: str,
    desc: str = "",
    typeclass: str = "typeclasses.rooms.Room",
    **kwargs
) -> Any:
    """
    Create a room with description and optional attributes.
    
    Args:
        name: Room name/key
        desc: Room description (supports shortcodes)
        typeclass: Full path to typeclass
        **kwargs: Additional attributes to set
        
    Returns:
        Created room object
        
    Example:
        room = create_room(
            "Market Square",
            desc="Bustling market with vendors...",
            typeclass="typeclasses.rooms.grove.GroveRoom",
            room_type="market",
            is_outdoor=True
        )
    """
    # Handle typeclass shorthand
    if not typeclass.startswith("typeclasses.") and not typeclass.startswith("evennia."):
        typeclass = f"typeclasses.rooms.{typeclass}"
    
    room = create_object(typeclass, key=name)
    
    if desc:
        room.db.desc = desc
    
    # Set additional attributes
    for key, value in kwargs.items():
        if hasattr(room, key):
            setattr(room, key, value)
        else:
            setattr(room.db, key, value)
    
    return room


def create_rooms_batch(room_data: List[Dict]) -> Dict[str, Any]:
    """
    Create multiple rooms from a list of configurations.
    
    Args:
        room_data: List of dicts with room parameters
        
    Returns:
        Dict mapping room names to room objects
        
    Example:
        rooms = create_rooms_batch([
            {"name": "Plaza", "typeclass": "GroveRoom", "desc": "..."},
            {"name": "Market", "typeclass": "MarketRoom", "desc": "..."},
        ])
    """
    created = {}
    for data in room_data:
        name = data.pop("name")
        room = create_room(name, **data)
        created[name] = room
    return created


# =============================================================================
# EXIT CREATION
# =============================================================================

def create_exit(
    source: Any,
    destination: Any,
    exit_name: str,
    aliases: List[str] = None,
    typeclass: str = "typeclasses.exits.Exit",
    **kwargs
) -> Any:
    """
    Create a one-way exit.
    
    Args:
        source: Room the exit is in
        destination: Room the exit leads to
        exit_name: Name of the exit (e.g., "north", "door", "gate")
        aliases: List of aliases (e.g., ["n"] for "north")
        typeclass: Exit typeclass
        **kwargs: Additional attributes
        
    Returns:
        Created exit object
    """
    exit_obj = create_object(
        typeclass,
        key=exit_name,
        aliases=aliases or [],
        location=source,
        destination=destination,
    )
    
    # Set additional attributes - FIXED: use setattr instead of __setattr__
    for key, value in kwargs.items():
        if hasattr(exit_obj, key):
            setattr(exit_obj, key, value)
        else:
            setattr(exit_obj.db, key, value)
    
    return exit_obj


def create_exit_pair(
    room_a: Any,
    room_b: Any,
    exit_a_to_b: str,
    exit_b_to_a: str,
    aliases_a: List[str] = None,
    aliases_b: List[str] = None,
    typeclass: str = "typeclasses.exits.Exit",
    **kwargs
) -> Tuple[Any, Any]:
    """
    Create bidirectional exits between two rooms.
    
    Args:
        room_a: First room
        room_b: Second room
        exit_a_to_b: Exit name from A to B (e.g., "north")
        exit_b_to_a: Exit name from B to A (e.g., "south")
        aliases_a: Aliases for A->B exit
        aliases_b: Aliases for B->A exit
        typeclass: Exit typeclass for both
        **kwargs: Additional attributes for both exits
        
    Returns:
        Tuple of (exit_a_to_b, exit_b_to_a)
        
    Example:
        create_exit_pair(plaza, market, "east", "west", ["e"], ["w"])
    """
    exit_1 = create_exit(room_a, room_b, exit_a_to_b, aliases_a, typeclass, **kwargs)
    exit_2 = create_exit(room_b, room_a, exit_b_to_a, aliases_b, typeclass, **kwargs)
    return exit_1, exit_2


# =============================================================================
# CARDINAL DIRECTION HELPERS
# =============================================================================

CARDINAL_OPPOSITES = {
    "north": "south",
    "south": "north",
    "east": "west",
    "west": "east",
    "northeast": "southwest",
    "northwest": "southeast",
    "southeast": "northwest",
    "southwest": "northeast",
    "up": "down",
    "down": "up",
    "in": "out",
    "out": "in",
}

CARDINAL_ALIASES = {
    "north": ["n"],
    "south": ["s"],
    "east": ["e"],
    "west": ["w"],
    "northeast": ["ne"],
    "northwest": ["nw"],
    "southeast": ["se"],
    "southwest": ["sw"],
    "up": ["u"],
    "down": ["d"],
}


def create_cardinal_exit_pair(
    room_a: Any,
    room_b: Any,
    direction: str,
    typeclass: str = "typeclasses.exits.Exit",
    **kwargs
) -> Tuple[Any, Any]:
    """
    Create bidirectional exits using cardinal directions.
    
    Automatically determines the opposite direction and aliases.
    
    Args:
        room_a: First room
        room_b: Second room  
        direction: Direction from A to B (e.g., "north")
        typeclass: Exit typeclass
        **kwargs: Additional attributes
        
    Returns:
        Tuple of (exit_a_to_b, exit_b_to_a)
        
    Example:
        create_cardinal_exit_pair(plaza, market, "east")
        # Creates "east" exit from plaza to market
        # Creates "west" exit from market to plaza
    """
    opposite = CARDINAL_OPPOSITES.get(direction, direction)
    aliases_a = CARDINAL_ALIASES.get(direction, [])
    aliases_b = CARDINAL_ALIASES.get(opposite, [])
    
    return create_exit_pair(
        room_a, room_b,
        direction, opposite,
        aliases_a, aliases_b,
        typeclass,
        **kwargs
    )


# =============================================================================
# DOOR CREATION
# =============================================================================

def create_door(
    room_a: Any,
    room_b: Any,
    door_name: str = "door",
    aliases: List[str] = None,
    typeclass: str = "typeclasses.exits.Door",
    locked: bool = False,
    key_id: str = None,
    **kwargs
) -> Tuple[Any, Any]:
    """
    Create a door between two rooms.
    
    Doors are two-way exits that can be opened/closed/locked.
    
    Args:
        room_a: First room
        room_b: Second room
        door_name: Name of the door
        aliases: Aliases for the door
        typeclass: Door typeclass
        locked: Whether door starts locked
        key_id: ID of key that unlocks this door
        **kwargs: Additional attributes
        
    Returns:
        Tuple of (door_a_side, door_b_side)
    """
    aliases = aliases or []
    
    # Create exits
    door_a = create_exit(room_a, room_b, door_name, aliases, typeclass, **kwargs)
    door_b = create_exit(room_b, room_a, door_name, aliases, typeclass, **kwargs)
    
    # Link them so state syncs
    door_a.db.paired_door = door_b.dbref
    door_b.db.paired_door = door_a.dbref
    
    # Set lock state
    if locked:
        door_a.db.is_locked = True
        door_b.db.is_locked = True
    
    if key_id:
        door_a.db.key_id = key_id
        door_b.db.key_id = key_id
    
    return door_a, door_b


# =============================================================================
# OBJECT CREATION
# =============================================================================

def create_item(
    name: str,
    location: Any = None,
    typeclass: str = "typeclasses.objects.Object",
    desc: str = "",
    **kwargs
) -> Any:
    """
    Create an item/object.
    
    Args:
        name: Object name
        location: Where to place it
        typeclass: Object typeclass
        desc: Object description
        **kwargs: Additional attributes
        
    Returns:
        Created object
    """
    obj = create_object(typeclass, key=name, location=location)
    
    if desc:
        obj.db.desc = desc
    
    for key, value in kwargs.items():
        if hasattr(obj, key):
            setattr(obj, key, value)
        else:
            setattr(obj.db, key, value)
    
    return obj


def create_furniture(
    name: str,
    room: Any,
    typeclass: str = "typeclasses.objects.Furniture",
    desc: str = "",
    capacity: int = 1,
    furniture_type: str = "seat",
    **kwargs
) -> Any:
    """
    Create furniture and register it with the room.
    
    Args:
        name: Furniture name
        room: Room to place it in
        typeclass: Furniture typeclass
        desc: Description
        capacity: How many can use it
        furniture_type: Type (seat, bed, surface, etc.)
        **kwargs: Additional attributes
        
    Returns:
        Created furniture object
    """
    furniture = create_item(
        name,
        location=room,
        typeclass=typeclass,
        desc=desc,
        capacity=capacity,
        furniture_type=furniture_type,
        **kwargs
    )
    
    # Register with room if it supports furniture tracking
    if hasattr(room, 'add_furniture'):
        room.add_furniture(furniture)
    
    return furniture


# =============================================================================
# NPC CREATION
# =============================================================================

def create_npc(
    name: str,
    location: Any,
    typeclass: str = "typeclasses.npcs.NPC",
    desc: str = "",
    npc_type: str = "ambient",
    **kwargs
) -> Any:
    """
    Create an NPC.
    
    Args:
        name: NPC name
        location: Where to place them
        typeclass: NPC typeclass
        desc: Description
        npc_type: Type (ambient, vendor, unique, etc.)
        **kwargs: Additional attributes
        
    Returns:
        Created NPC
    """
    npc = create_object(typeclass, key=name, location=location)
    
    if desc:
        npc.db.desc = desc
    
    npc.db.npc_type = npc_type
    
    for key, value in kwargs.items():
        if hasattr(npc, key):
            setattr(npc, key, value)
        else:
            setattr(npc.db, key, value)
    
    return npc


# =============================================================================
# CLEANUP UTILITIES
# =============================================================================

def delete_room_and_contents(room: Any, delete_exits: bool = True) -> int:
    """
    Delete a room and everything in it.
    
    Args:
        room: Room to delete
        delete_exits: Also delete exits leading to this room
        
    Returns:
        Number of objects deleted
    """
    count = 0
    
    # Delete contents
    for obj in list(room.contents):
        obj.delete()
        count += 1
    
    # Delete exits leading here
    if delete_exits:
        for exit_obj in search_object(room.dbref, typeclass="evennia.objects.objects.DefaultExit"):
            if hasattr(exit_obj, 'destination') and exit_obj.destination == room:
                exit_obj.delete()
                count += 1
    
    # Delete the room
    room.delete()
    count += 1
    
    return count


def find_or_create_room(name: str, **kwargs) -> Tuple[Any, bool]:
    """
    Find an existing room by name, or create it if it doesn't exist.
    
    Args:
        name: Room name to find/create
        **kwargs: Arguments for create_room if creating
        
    Returns:
        Tuple of (room, was_created)
    """
    results = search_object(name, typeclass="typeclasses.rooms.Room")
    if results:
        return results[0], False
    
    return create_room(name, **kwargs), True


# =============================================================================
# BATCH BUILDING
# =============================================================================

def build_area_from_spec(spec: Dict) -> Dict[str, Any]:
    """
    Build an entire area from a specification dict.
    
    Args:
        spec: Area specification with 'rooms' and 'exits' keys
        
    Returns:
        Dict of created objects
        
    Example:
        spec = {
            "rooms": [
                {"name": "Plaza", "desc": "...", "typeclass": "GroveRoom"},
                {"name": "Market", "desc": "...", "typeclass": "MarketRoom"},
            ],
            "exits": [
                {"from": "Plaza", "to": "Market", "direction": "east"},
            ]
        }
        objects = build_area_from_spec(spec)
    """
    created = {"rooms": {}, "exits": []}
    
    # Create rooms
    for room_spec in spec.get("rooms", []):
        name = room_spec.pop("name")
        room = create_room(name, **room_spec)
        created["rooms"][name] = room
    
    # Create exits
    for exit_spec in spec.get("exits", []):
        from_room = created["rooms"].get(exit_spec["from"])
        to_room = created["rooms"].get(exit_spec["to"])
        
        if from_room and to_room:
            direction = exit_spec.get("direction", "passage")
            
            if direction in CARDINAL_OPPOSITES:
                exits = create_cardinal_exit_pair(from_room, to_room, direction)
            else:
                reverse = exit_spec.get("reverse", direction)
                exits = create_exit_pair(from_room, to_room, direction, reverse)
            
            created["exits"].extend(exits)
    
    return created
