"""
Builder Utilities

Helper functions for batch world building.

Usage:
    from world.builder_utils import create_room, create_exit_pair, create_door
    
    plaza = create_room("Gate Plaza", GroveRoom, desc="The central plaza...")
    market = create_room("Market Square", MarketRoom, desc="Stalls and vendors...")
    
    create_exit_pair(plaza, market, "south", "north")
"""

from typing import Optional, List, Tuple, Any, Dict
from evennia.utils.create import create_object
from evennia import search_object


# =============================================================================
# ROOM CREATION
# =============================================================================

def create_room(
    name: str,
    typeclass: str = "typeclasses.rooms.Room",
    desc: str = "",
    zone: str = "",
    region: str = "",
    atmosphere: str = "",
    **kwargs
) -> Any:
    """
    Create a single room.
    
    Args:
        name: Room name/key
        typeclass: Typeclass path or class
        desc: Room description (can include shortcodes)
        zone: Zone name
        region: Region name
        atmosphere: Atmosphere preset to apply
        **kwargs: Additional attributes to set
        
    Returns:
        Created room object
        
    Example:
        room = create_room(
            "Market Square",
            typeclass="typeclasses.rooms.grove.MarketRoom",
            desc="A bustling marketplace fills the square...",
            zone="Market Square",
            stall_spots=6,
        )
    """
    room = create_object(
        typeclass,
        key=name,
    )
    
    # Set description
    if desc:
        room.db.desc = desc
    
    # Set organization
    if zone:
        room.zone = zone
    if region:
        room.region = region
    
    # Apply atmosphere
    if atmosphere and hasattr(room, 'apply_atmosphere'):
        room.apply_atmosphere(atmosphere)
    
    # Set additional attributes
    for key, value in kwargs.items():
        if hasattr(room, key):
            setattr(room, key, value)
        else:
            setattr(room.db, key, value)
    
    return room


def create_rooms_batch(room_data: List[Dict]) -> Dict[str, Any]:
    """
    Create multiple rooms from a list of definitions.
    
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
    
    # Set additional attributes
    for key, value in kwargs.items():
        if hasattr(exit_obj, key):
            setattr(exit_obj, key, value)
        else:
            exit_obj.db.__setattr__(key, value)
    
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
        exit_a_to_b: Name of exit from A to B (e.g., "north")
        exit_b_to_a: Name of exit from B to A (e.g., "south")
        aliases_a: Aliases for A->B exit
        aliases_b: Aliases for B->A exit
        typeclass: Exit typeclass for both
        **kwargs: Additional attributes for both exits
        
    Returns:
        Tuple of (exit_a_to_b, exit_b_to_a)
        
    Example:
        create_exit_pair(plaza, market, "south", "north", ["s"], ["n"])
    """
    exit_ab = create_exit(
        room_a, room_b, exit_a_to_b, 
        aliases=aliases_a,
        typeclass=typeclass,
        **kwargs
    )
    
    exit_ba = create_exit(
        room_b, room_a, exit_b_to_a,
        aliases=aliases_b,
        typeclass=typeclass,
        **kwargs
    )
    
    return (exit_ab, exit_ba)


# =============================================================================
# DOOR CREATION
# =============================================================================

def create_door(
    source: Any,
    destination: Any,
    door_name: str,
    return_name: str = None,
    aliases: List[str] = None,
    return_aliases: List[str] = None,
    is_open: bool = True,
    is_locked: bool = False,
    key_id: str = "",
    **kwargs
) -> Tuple[Any, Any]:
    """
    Create a door (bidirectional linked exit).
    
    Args:
        source: Room the door is in
        destination: Room the door leads to
        door_name: Name from source side
        return_name: Name from destination side (default: same as door_name)
        aliases: Aliases for source side
        return_aliases: Aliases for destination side
        is_open: Initial open state
        is_locked: Initial locked state
        key_id: ID of key that unlocks
        **kwargs: Additional attributes
        
    Returns:
        Tuple of (door_from_source, door_from_dest)
        
    Example:
        create_door(
            street, shop, 
            "shop door", "door",
            is_open=True
        )
    """
    if return_name is None:
        return_name = door_name
    
    door_in = create_object(
        "typeclasses.exits.Door",
        key=door_name,
        aliases=aliases or [],
        location=source,
        destination=destination,
    )
    
    door_out = create_object(
        "typeclasses.exits.Door",
        key=return_name,
        aliases=return_aliases or [],
        location=destination,
        destination=source,
    )
    
    # Link them
    door_in.linked_exit = door_out.dbref
    door_out.linked_exit = door_in.dbref
    
    # Set states
    door_in.is_open = is_open
    door_in.is_locked = is_locked
    door_in.key_id = key_id
    
    door_out.is_open = is_open
    door_out.is_locked = is_locked
    door_out.key_id = key_id
    
    # Additional attributes
    for key, value in kwargs.items():
        if hasattr(door_in, key):
            setattr(door_in, key, value)
            setattr(door_out, key, value)
    
    return (door_in, door_out)


# =============================================================================
# REALM GATE CREATION
# =============================================================================

def create_realm_gate(
    source: Any,
    destination: Any,
    gate_name: str,
    realm_name: str,
    aliases: List[str] = None,
    malfunction_chance: float = 0.0,
    requires_payment: int = 0,
    **kwargs
) -> Any:
    """
    Create a realm gate (one-way magical portal).
    
    Gates are one-way. Create two gates for bidirectional travel.
    
    Args:
        source: Room the gate is in
        destination: Room the gate leads to
        gate_name: Name of the gate
        realm_name: Name of destination realm
        aliases: Gate aliases
        malfunction_chance: Chance of "accident" (0.0-1.0)
        requires_payment: Cost to use
        **kwargs: Additional attributes
        
    Returns:
        Created gate object
        
    Example:
        create_realm_gate(
            plaza, asgard_entry,
            "Asgard Gate", "Asgard",
            aliases=["asgard"],
            malfunction_chance=0.05,
        )
    """
    gate = create_object(
        "typeclasses.exits.RealmGate",
        key=gate_name,
        aliases=aliases or [],
        location=source,
        destination=destination,
    )
    
    gate.destination_realm = realm_name
    gate.malfunction_chance = malfunction_chance
    gate.requires_payment = requires_payment
    
    # Additional attributes
    for key, value in kwargs.items():
        if hasattr(gate, key):
            setattr(gate, key, value)
    
    return gate


# =============================================================================
# CLEANUP / UTILITIES
# =============================================================================

def find_room(name: str) -> Optional[Any]:
    """
    Find a room by name.
    
    Args:
        name: Room name to search for
        
    Returns:
        Room object or None
    """
    results = search_object(name)
    for obj in results:
        if hasattr(obj, 'destination'):
            continue  # It's an exit
        if obj.location is None:
            # Rooms have no location
            return obj
    return None


def delete_room(room: Any, delete_exits: bool = True) -> bool:
    """
    Delete a room and optionally its exits.
    
    Args:
        room: Room to delete
        delete_exits: Also delete exits from this room
        
    Returns:
        True if deleted
    """
    if delete_exits:
        for exit_obj in room.exits:
            exit_obj.delete()
    
    room.delete()
    return True


def connect_rooms(connections: List[Tuple]) -> List:
    """
    Create multiple connections at once.
    
    Args:
        connections: List of tuples:
            (room_a, room_b, "exit_name", "return_name") for exits
            (room_a, room_b, "exit_name", "return_name", "door") for doors
            
    Returns:
        List of created exit objects
        
    Example:
        connect_rooms([
            (plaza, market, "south", "north"),
            (plaza, gate_office, "office door", "door", "door"),
        ])
    """
    created = []
    
    for conn in connections:
        if len(conn) == 4:
            # Regular exit pair
            room_a, room_b, exit_ab, exit_ba = conn
            exits = create_exit_pair(room_a, room_b, exit_ab, exit_ba)
            created.extend(exits)
        elif len(conn) == 5 and conn[4] == "door":
            # Door
            room_a, room_b, door_name, return_name, _ = conn
            doors = create_door(room_a, room_b, door_name, return_name)
            created.extend(doors)
    
    return created


# =============================================================================
# EXPORTS
# =============================================================================

__all__ = [
    "create_room",
    "create_rooms_batch",
    "create_exit",
    "create_exit_pair",
    "create_door",
    "create_realm_gate",
    "find_room",
    "delete_room",
    "connect_rooms",
]
