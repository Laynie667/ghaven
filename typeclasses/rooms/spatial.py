# SPATIAL AWARENESS SYSTEM
# typeclasses/rooms/spatial.py
"""
Spatial Awareness System - Inter-Room Perception

Creates the illusion of interconnected spaces without XYZGrid complexity.
Handles what you can see, hear, and smell from connected spaces.

THREE CORE CONCEPTS:

1. ADJACENCY - Nearby rooms you can perceive but must walk to reach
   Use for: Market stalls, adjacent shops, nearby paths
   
2. OVERLOOKS - Vertical views (balconies, windows, cliffs)
   Use for: Balconies viewing halls, towers viewing plazas, cliffs viewing beaches
   
3. PARTITIONS - Barriers between spaces with sensory properties
   Use for: Iron bars, glass walls, curtains, windows

This system works BETWEEN rooms. For positions WITHIN a room,
use the GridRoom system (typeclasses/rooms/grid.py).

Usage:
    from typeclasses.rooms.spatial import (
        SpatialMixin, SpatialRoom,
        Adjacency, Overlook, PartitionLink,
        Distance, PartitionType
    )
"""

from typing import Optional, Dict, List, Any, TYPE_CHECKING
from enum import Enum
from dataclasses import dataclass, field

# Handle early import during Django migration loading
try:
    from evennia.typeclasses.attributes import AttributeProperty
except (ImportError, TypeError, AttributeError):
    def AttributeProperty(default=None, **kwargs):
        return default

try:
    from evennia import search_object
except ImportError:
    search_object = None

if TYPE_CHECKING:
    from evennia.objects.objects import DefaultRoom


# =============================================================================
# ENUMS
# =============================================================================

class Distance(Enum):
    """
    How far away something is - affects perception detail.
    
    CLOSE:   Names, actions, hear full conversation
    MEDIUM:  Names, general activity ("talking", "fighting")  
    FAR:     Count and vague description ("several figures")
    DISTANT: Presence only ("movement", "empty")
    """
    CLOSE = "close"
    MEDIUM = "medium"
    FAR = "far"
    DISTANT = "distant"


class Direction(Enum):
    """Spatial relationship direction for overlooks."""
    ABOVE = "above"
    BELOW = "below"
    ACROSS = "across"     # Across a gap, courtyard


class PartitionType(Enum):
    """
    Types of barriers between spaces.
    
    Format: (see_through, hear_through, smell_through, pass_through)
    
    Note: 'muffled' for hearing means you hear sound but not words.
    """
    # Full passage
    OPEN = "open"
    
    # See-through barriers
    IRON_BARS = "iron_bars"         # Jail cells, cages
    WINDOW_CLOSED = "window_closed" # Glass window, closed
    WINDOW_OPEN = "window_open"     # Glass window, open
    GLASS_WALL = "glass_wall"       # Display cases, museum
    GRATE = "grate"                 # Floor/ceiling grates
    
    # Opaque barriers
    CURTAIN = "curtain"             # Fabric barrier
    THIN_WALL = "thin_wall"         # Hear through, can't see
    THICK_WALL = "thick_wall"       # Mostly blocks everything
    DOOR_CLOSED = "door_closed"     # Closed door
    DOOR_OPEN = "door_open"         # Open doorway
    
    # Special
    WATER_SURFACE = "water_surface" # Looking through water


# Partition properties: (see, hear, smell, pass)
# Values: True, False, "muffled", "distorted"
PARTITION_PROPERTIES = {
    PartitionType.OPEN:          (True, True, True, True),
    PartitionType.IRON_BARS:     (True, True, True, False),
    PartitionType.WINDOW_CLOSED: (True, "muffled", False, False),
    PartitionType.WINDOW_OPEN:   (True, True, True, False),
    PartitionType.GLASS_WALL:    (True, "muffled", False, False),
    PartitionType.GRATE:         (True, True, True, False),
    PartitionType.CURTAIN:       (False, True, True, True),
    PartitionType.THIN_WALL:     (False, "muffled", False, False),
    PartitionType.THICK_WALL:    (False, False, False, False),
    PartitionType.DOOR_CLOSED:   (False, "muffled", False, False),
    PartitionType.DOOR_OPEN:     (True, True, True, True),
    PartitionType.WATER_SURFACE: ("distorted", "muffled", False, True),
}


# =============================================================================
# DATA CLASSES
# =============================================================================

@dataclass
class Adjacency:
    """
    Defines a room that's perceivable from the current room.
    
    Use for market stalls, adjacent shops, nearby areas in same space.
    Players see who's there but must move to interact.
    
    Attributes:
        room_key: The key/dbref of the adjacent room
        direction: Cardinal direction or descriptive ("north", "across")
        distance: How far - affects detail level
        view_desc: What you see when looking that direction
        hear_desc: What sounds drift from there (optional)
        blocked_by: Conditions that block view (weather, time, etc.)
    """
    room_key: str
    direction: str = "nearby"
    distance: Distance = Distance.MEDIUM
    view_desc: str = ""
    hear_desc: str = ""
    blocked_by: List[str] = field(default_factory=list)
    
    def to_dict(self) -> dict:
        """Serialize for AttributeProperty storage."""
        return {
            "room_key": self.room_key,
            "direction": self.direction,
            "distance": self.distance.value,
            "view_desc": self.view_desc,
            "hear_desc": self.hear_desc,
            "blocked_by": self.blocked_by,
        }
    
    @classmethod
    def from_dict(cls, data: dict) -> "Adjacency":
        """Deserialize from storage."""
        data = dict(data)  # Copy to avoid mutation
        data["distance"] = Distance(data.get("distance", "medium"))
        return cls(**data)


@dataclass
class Overlook:
    """
    Defines a vertical view - balcony to hall, cliff to beach.
    
    Overlooks are one-way: you see DOWN (or up) into another space.
    The target room can optionally know it's being overlooked.
    
    Attributes:
        room_key: The room being overlooked
        direction: "below", "above", or "across"
        distance: How far - affects detail level
        view_desc: Description of what you see
        perceive_watcher: Can people below see someone's watching?
        watcher_desc: What they see ("A figure watches from above")
    """
    room_key: str
    direction: Direction = Direction.BELOW
    distance: Distance = Distance.FAR
    view_desc: str = ""
    perceive_watcher: bool = True
    watcher_desc: str = "A figure watches from above."
    
    def to_dict(self) -> dict:
        """Serialize for storage."""
        return {
            "room_key": self.room_key,
            "direction": self.direction.value,
            "distance": self.distance.value,
            "view_desc": self.view_desc,
            "perceive_watcher": self.perceive_watcher,
            "watcher_desc": self.watcher_desc,
        }
    
    @classmethod
    def from_dict(cls, data: dict) -> "Overlook":
        """Deserialize from storage."""
        data = dict(data)
        data["direction"] = Direction(data.get("direction", "below"))
        data["distance"] = Distance(data.get("distance", "far"))
        return cls(**data)


@dataclass
class PartitionLink:
    """
    A barrier between this room and another with sensory properties.
    
    Use for: jail cell bars, glass displays, curtained alcoves.
    Partitions are TWO-WAY - both rooms perceive through the barrier.
    
    Attributes:
        room_key: The room on the other side
        partition_type: What kind of barrier
        desc: Description of the barrier ("iron bars", "thick glass")
        can_toggle: Can the barrier state change?
        toggle_key: What changes it (item key, command, etc.)
    """
    room_key: str
    partition_type: PartitionType = PartitionType.GLASS_WALL
    desc: str = ""
    can_toggle: bool = False
    toggle_to: Optional[PartitionType] = None  # What it becomes when toggled
    toggle_key: str = ""
    
    def to_dict(self) -> dict:
        """Serialize for storage."""
        return {
            "room_key": self.room_key,
            "partition_type": self.partition_type.value,
            "desc": self.desc,
            "can_toggle": self.can_toggle,
            "toggle_to": self.toggle_to.value if self.toggle_to else None,
            "toggle_key": self.toggle_key,
        }
    
    @classmethod
    def from_dict(cls, data: dict) -> "PartitionLink":
        """Deserialize from storage."""
        data = dict(data)
        data["partition_type"] = PartitionType(data.get("partition_type", "glass_wall"))
        if data.get("toggle_to"):
            data["toggle_to"] = PartitionType(data["toggle_to"])
        return cls(**data)
    
    @property
    def properties(self) -> tuple:
        """Get (see, hear, smell, pass) for this partition type."""
        return PARTITION_PROPERTIES.get(
            self.partition_type, 
            (False, False, False, False)
        )
    
    @property
    def can_see(self) -> bool:
        """Can you see through this partition?"""
        return self.properties[0] is True
    
    @property
    def can_hear(self) -> bool:
        """Can you hear clearly through? (True or 'muffled')"""
        return self.properties[1] is not False
    
    @property
    def hearing_quality(self) -> str:
        """'clear', 'muffled', or 'blocked'"""
        h = self.properties[1]
        if h is True:
            return "clear"
        elif h == "muffled":
            return "muffled"
        return "blocked"
    
    @property
    def can_smell(self) -> bool:
        """Can smells pass through?"""
        return self.properties[2] is True
    
    @property
    def can_pass(self) -> bool:
        """Can you physically pass through?"""
        return self.properties[3] is True


# =============================================================================
# PERCEPTION HELPERS
# =============================================================================

def describe_occupants_at_distance(
    characters: list, 
    distance: Distance,
    looker=None
) -> str:
    """
    Generate a description of characters based on distance.
    
    Args:
        characters: List of character objects
        distance: How far away they are
        looker: The one looking (to exclude from list)
        
    Returns:
        String description appropriate to distance
    """
    # Filter out the looker
    chars = [c for c in characters if c != looker]
    
    if not chars:
        return "Empty."
    
    count = len(chars)
    
    if distance == Distance.CLOSE:
        # Full detail: names and what they're doing
        names = [c.get_display_name(looker) if hasattr(c, 'get_display_name') else c.key for c in chars]
        if count == 1:
            return names[0]
        elif count == 2:
            return f"{names[0]} and {names[1]}"
        else:
            return f"{', '.join(names[:-1])}, and {names[-1]}"
    
    elif distance == Distance.MEDIUM:
        # Names but less detail
        names = [c.get_display_name(looker) if hasattr(c, 'get_display_name') else c.key for c in chars]
        if count == 1:
            return f"{names[0]} is there"
        else:
            return f"{', '.join(names)} are there"
    
    elif distance == Distance.FAR:
        # Counts and vague descriptions
        if count == 1:
            return "A figure"
        elif count <= 3:
            return f"{count} figures"
        else:
            return "Several figures"
    
    else:  # DISTANT
        # Presence only
        if count == 0:
            return "Empty"
        elif count == 1:
            return "Movement"
        else:
            return "Activity"


def get_room_by_key(room_key: str):
    """
    Find a room by key or dbref.
    
    Handles both "#123" style dbrefs and "market_stall_north" keys.
    """
    if not search_object:
        return None
        
    if room_key.startswith("#"):
        # It's a dbref
        results = search_object(room_key)
    else:
        # It's a key
        results = search_object(room_key, typeclass="typeclasses.rooms")
        if not results:
            # Try without typeclass restriction
            results = search_object(room_key)
    
    return results[0] if results else None


# =============================================================================
# SPATIAL MIXIN
# =============================================================================

class SpatialMixin:
    """
    Mixin adding spatial awareness to any room type.
    
    Adds:
    - adjacent_rooms: Nearby rooms you can perceive
    - overlooks: Rooms you can see from above/below
    - partitions: Barrier-separated spaces
    
    Apply to your Room class:
        class MyRoom(SpatialMixin, Room):
            pass
    """
    
    # -------------------------------------------------------------------------
    # Attribute Storage
    # -------------------------------------------------------------------------
    
    # {key: Adjacency.to_dict()}
    adjacent_rooms = AttributeProperty(default=dict)
    
    # {key: Overlook.to_dict()}
    overlooks = AttributeProperty(default=dict)
    
    # {key: PartitionLink.to_dict()}
    partitions = AttributeProperty(default=dict)
    
    # Rooms that overlook THIS room (auto-populated or manual)
    overlooked_by = AttributeProperty(default=list)
    
    # -------------------------------------------------------------------------
    # Adjacency Management
    # -------------------------------------------------------------------------
    
    def add_adjacent(self, adjacency: Adjacency) -> None:
        """Add an adjacent room."""
        adj = dict(self.adjacent_rooms)
        adj[adjacency.room_key] = adjacency.to_dict()
        self.adjacent_rooms = adj
    
    def remove_adjacent(self, room_key: str) -> bool:
        """Remove an adjacent room."""
        if room_key in self.adjacent_rooms:
            adj = dict(self.adjacent_rooms)
            del adj[room_key]
            self.adjacent_rooms = adj
            return True
        return False
    
    def get_adjacent(self, room_key: str) -> Optional[Adjacency]:
        """Get adjacency data for a specific room."""
        if room_key in self.adjacent_rooms:
            return Adjacency.from_dict(self.adjacent_rooms[room_key])
        return None
    
    def get_all_adjacent(self) -> List[Adjacency]:
        """Get all adjacent rooms."""
        return [Adjacency.from_dict(a) for a in self.adjacent_rooms.values()]
    
    # -------------------------------------------------------------------------
    # Overlook Management
    # -------------------------------------------------------------------------
    
    def add_overlook(self, overlook: Overlook) -> None:
        """Add a room this one overlooks."""
        ovl = dict(self.overlooks)
        ovl[overlook.room_key] = overlook.to_dict()
        self.overlooks = ovl
        
        # Optionally register with the target room
        target = get_room_by_key(overlook.room_key)
        if target and hasattr(target, 'overlooked_by'):
            if self.key not in target.overlooked_by:
                target.overlooked_by = list(target.overlooked_by) + [self.key]
    
    def remove_overlook(self, room_key: str) -> bool:
        """Remove an overlook."""
        if room_key in self.overlooks:
            ovl = dict(self.overlooks)
            del ovl[room_key]
            self.overlooks = ovl
            return True
        return False
    
    def get_overlook(self, room_key: str) -> Optional[Overlook]:
        """Get overlook data for a specific room."""
        if room_key in self.overlooks:
            return Overlook.from_dict(self.overlooks[room_key])
        return None
    
    def get_all_overlooks(self) -> List[Overlook]:
        """Get all rooms this one overlooks."""
        return [Overlook.from_dict(o) for o in self.overlooks.values()]
    
    # -------------------------------------------------------------------------
    # Partition Management
    # -------------------------------------------------------------------------
    
    def add_partition(self, partition: PartitionLink) -> None:
        """Add a partition to another room."""
        parts = dict(self.partitions)
        parts[partition.room_key] = partition.to_dict()
        self.partitions = parts
    
    def remove_partition(self, room_key: str) -> bool:
        """Remove a partition."""
        if room_key in self.partitions:
            parts = dict(self.partitions)
            del parts[room_key]
            self.partitions = parts
            return True
        return False
    
    def get_partition(self, room_key: str) -> Optional[PartitionLink]:
        """Get partition data for a specific room."""
        if room_key in self.partitions:
            return PartitionLink.from_dict(self.partitions[room_key])
        return None
    
    def get_all_partitions(self) -> List[PartitionLink]:
        """Get all partitions from this room."""
        return [PartitionLink.from_dict(p) for p in self.partitions.values()]
    
    def toggle_partition(self, room_key: str) -> bool:
        """
        Toggle a partition's state (e.g., open/close window).
        
        Returns True if toggled, False if can't toggle.
        """
        partition = self.get_partition(room_key)
        if not partition or not partition.can_toggle or not partition.toggle_to:
            return False
        
        # Swap current and toggle_to
        new_type = partition.toggle_to
        partition.toggle_to = partition.partition_type
        partition.partition_type = new_type
        
        # Save
        parts = dict(self.partitions)
        parts[room_key] = partition.to_dict()
        self.partitions = parts
        
        return True
    
    # -------------------------------------------------------------------------
    # Perception Methods
    # -------------------------------------------------------------------------
    
    def get_visible_from_adjacent(self, looker=None) -> List[dict]:
        """
        Get what's visible in adjacent rooms.
        
        Returns list of dicts with:
            - direction: Where the room is
            - view_desc: Description of what you see
            - occupants: Description of who's there
            - room: The actual room object (if found)
        """
        results = []
        
        for adj in self.get_all_adjacent():
            room = get_room_by_key(adj.room_key)
            
            entry = {
                "direction": adj.direction,
                "distance": adj.distance,
                "view_desc": adj.view_desc,
                "room": room,
                "room_key": adj.room_key,
            }
            
            # Get occupants if room exists
            if room:
                chars = [c for c in room.contents if hasattr(c, 'account') or 
                        (hasattr(c, 'is_npc') and c.is_npc)]
                entry["occupants"] = describe_occupants_at_distance(
                    chars, adj.distance, looker
                )
                entry["room_name"] = room.key
            else:
                entry["occupants"] = ""
                entry["room_name"] = adj.room_key
            
            results.append(entry)
        
        return results
    
    def get_visible_from_overlooks(self, looker=None) -> List[dict]:
        """
        Get what's visible from overlook positions.
        
        Returns list of dicts with:
            - direction: "below", "above", "across"
            - view_desc: Description of what you see
            - occupants: Who's there (detail based on distance)
            - room: The actual room object
        """
        results = []
        
        for overlook in self.get_all_overlooks():
            room = get_room_by_key(overlook.room_key)
            
            entry = {
                "direction": overlook.direction.value,
                "distance": overlook.distance,
                "view_desc": overlook.view_desc,
                "room": room,
                "room_key": overlook.room_key,
            }
            
            if room:
                chars = [c for c in room.contents if hasattr(c, 'account') or
                        (hasattr(c, 'is_npc') and c.is_npc)]
                entry["occupants"] = describe_occupants_at_distance(
                    chars, overlook.distance, looker
                )
                entry["room_name"] = room.key
            else:
                entry["occupants"] = ""
                entry["room_name"] = overlook.room_key
            
            results.append(entry)
        
        return results
    
    def get_visible_through_partitions(self, looker=None) -> List[dict]:
        """
        Get what's visible through partitions (that allow sight).
        
        Returns list of dicts with:
            - partition_desc: Description of the barrier
            - partition_type: The type of barrier
            - can_see/can_hear/can_smell: What passes through
            - occupants: Who's there (if visible)
            - room: The room object
        """
        results = []
        
        for partition in self.get_all_partitions():
            room = get_room_by_key(partition.room_key)
            
            entry = {
                "partition_desc": partition.desc,
                "partition_type": partition.partition_type.value,
                "can_see": partition.can_see,
                "can_hear": partition.can_hear,
                "hearing_quality": partition.hearing_quality,
                "can_smell": partition.can_smell,
                "can_pass": partition.can_pass,
                "room": room,
                "room_key": partition.room_key,
            }
            
            if room and partition.can_see:
                chars = [c for c in room.contents if hasattr(c, 'account') or
                        (hasattr(c, 'is_npc') and c.is_npc)]
                # Partitions are usually close-ish
                entry["occupants"] = describe_occupants_at_distance(
                    chars, Distance.MEDIUM, looker
                )
                entry["room_name"] = room.key
            else:
                entry["occupants"] = ""
                entry["room_name"] = partition.room_key if not room else room.key
            
            results.append(entry)
        
        return results
    
    def get_watchers(self) -> List[dict]:
        """
        Get who's watching this room from overlook positions.
        
        For rooms that are overlooked - returns info about watchers.
        """
        watchers = []
        
        for room_key in self.overlooked_by:
            room = get_room_by_key(room_key)
            if not room:
                continue
            
            # Get the overlook data from that room
            overlook = room.get_overlook(self.key) if hasattr(room, 'get_overlook') else None
            if not overlook or not overlook.perceive_watcher:
                continue
            
            # Check if anyone's in the overlook room
            chars = [c for c in room.contents if hasattr(c, 'account') or
                    (hasattr(c, 'is_npc') and c.is_npc)]
            
            if chars:
                watchers.append({
                    "room_key": room_key,
                    "watcher_desc": overlook.watcher_desc,
                    "count": len(chars),
                })
        
        return watchers
    
    # -------------------------------------------------------------------------
    # Look Hook Extension
    # -------------------------------------------------------------------------
    
    def get_spatial_description(self, looker=None) -> str:
        """
        Build the spatial awareness portion of room description.
        
        Call this from your room's return_appearance or look hook.
        """
        parts = []
        
        # Adjacent rooms
        adjacent = self.get_visible_from_adjacent(looker)
        if adjacent:
            adj_lines = []
            for adj in adjacent:
                line = f"  {adj['direction'].title()}: "
                if adj['view_desc']:
                    line += adj['view_desc']
                if adj['occupants'] and adj['occupants'] not in ("Empty", "Empty."):
                    line += f" ({adj['occupants']})"
                elif not adj['view_desc']:
                    line += adj.get('room_name', 'somewhere')
                adj_lines.append(line)
            parts.append("Nearby you can see:\n" + "\n".join(adj_lines))
        
        # Overlooks
        overlooks = self.get_visible_from_overlooks(looker)
        if overlooks:
            ovl_lines = []
            for ovl in overlooks:
                direction = ovl['direction'].title()
                line = f"  {direction}: "
                if ovl['view_desc']:
                    line += ovl['view_desc']
                if ovl['occupants'] and ovl['occupants'] not in ("Empty", "Empty."):
                    line += f" {ovl['occupants']}."
                ovl_lines.append(line)
            parts.append("\n".join(ovl_lines))
        
        # Partitions (only those you can see through)
        partitions = self.get_visible_through_partitions(looker)
        visible_partitions = [p for p in partitions if p['can_see']]
        if visible_partitions:
            part_lines = []
            for part in visible_partitions:
                line = f"  Through {part['partition_desc']}: "
                if part['occupants']:
                    line += part['occupants']
                else:
                    line += "empty"
                part_lines.append(line)
            parts.append("\n".join(part_lines))
        
        # Being watched
        watchers = self.get_watchers()
        if watchers:
            for w in watchers:
                parts.append(w['watcher_desc'])
        
        return "\n\n".join(parts)
    
    # -------------------------------------------------------------------------
    # Sound Propagation
    # -------------------------------------------------------------------------
    
    def propagate_sound(
        self, 
        message: str, 
        source=None,
        volume: str = "normal"
    ) -> None:
        """
        Send a sound to adjacent/partitioned rooms that can hear.
        
        Args:
            message: The sound/speech to propagate
            source: Who/what made the sound
            volume: "whisper", "normal", "loud", "shout"
        """
        # Volume affects which rooms hear it
        volume_reach = {
            "whisper": [Distance.CLOSE],
            "normal": [Distance.CLOSE, Distance.MEDIUM],
            "loud": [Distance.CLOSE, Distance.MEDIUM, Distance.FAR],
            "shout": [Distance.CLOSE, Distance.MEDIUM, Distance.FAR, Distance.DISTANT],
        }
        allowed_distances = volume_reach.get(volume, [Distance.CLOSE, Distance.MEDIUM])
        
        # Adjacent rooms
        for adj in self.get_all_adjacent():
            if adj.distance not in allowed_distances:
                continue
            
            room = get_room_by_key(adj.room_key)
            if room:
                prefix = f"From {adj.direction}: " if adj.direction else "Nearby: "
                room.msg_contents(f"{prefix}{message}")
        
        # Partitioned rooms (if they can hear)
        for partition in self.get_all_partitions():
            if not partition.can_hear:
                continue
            
            room = get_room_by_key(partition.room_key)
            if room:
                if partition.hearing_quality == "muffled":
                    room.msg_contents(f"Muffled sounds from beyond the {partition.desc}...")
                else:
                    room.msg_contents(f"Through the {partition.desc}: {message}")
        
        # Rooms this one overlooks (sound carries up)
        for overlook in self.get_all_overlooks():
            if overlook.distance not in allowed_distances:
                continue
            
            room = get_room_by_key(overlook.room_key)
            if room:
                direction = "above" if overlook.direction == Direction.BELOW else "nearby"
                room.msg_contents(f"From {direction}: {message}")


# =============================================================================
# SPATIAL ROOM CLASS
# =============================================================================

# Import base Room - adjust path as needed for your project
try:
    from typeclasses.base_rooms import Room as BaseRoom
except ImportError:
    try:
        from typeclasses.rooms import Room as BaseRoom
    except ImportError:
        from evennia import DefaultRoom as BaseRoom


class SpatialRoom(SpatialMixin, BaseRoom):
    """
    Room with full spatial awareness capabilities.
    
    Includes adjacency, overlooks, and partitions.
    """
    
    def return_appearance(self, looker, **kwargs):
        """Override to include spatial awareness."""
        # Get base appearance
        base = super().return_appearance(looker, **kwargs)
        
        # Add spatial information
        spatial = self.get_spatial_description(looker)
        
        if spatial:
            return f"{base}\n\n{spatial}"
        return base


# =============================================================================
# BUILDER HELPERS
# =============================================================================

def link_adjacent_rooms(
    room1,
    room2,
    direction1: str = "nearby",
    direction2: str = "nearby",
    distance: Distance = Distance.MEDIUM,
    view_desc1: str = "",
    view_desc2: str = "",
    bidirectional: bool = True
) -> None:
    """
    Helper to set up adjacency between two rooms.
    
    Args:
        room1, room2: The rooms to link
        direction1: Direction from room1 to room2
        direction2: Direction from room2 to room1
        distance: How far apart they appear
        view_desc1: What room1 sees looking at room2
        view_desc2: What room2 sees looking at room1
        bidirectional: Whether both rooms see each other
    """
    if not hasattr(room1, 'add_adjacent'):
        raise TypeError(f"{room1} doesn't have SpatialMixin")
    
    room1.add_adjacent(Adjacency(
        room_key=room2.key,
        direction=direction1,
        distance=distance,
        view_desc=view_desc1,
    ))
    
    if bidirectional and hasattr(room2, 'add_adjacent'):
        room2.add_adjacent(Adjacency(
            room_key=room1.key,
            direction=direction2,
            distance=distance,
            view_desc=view_desc2,
        ))


def setup_overlook(
    high_room,
    low_room,
    view_desc: str = "",
    distance: Distance = Distance.FAR,
    perceive_watcher: bool = True,
    watcher_desc: str = "Someone watches from above."
) -> None:
    """
    Helper to set up an overlook (balcony -> hall, cliff -> beach).
    
    Args:
        high_room: The room doing the overlooking
        low_room: The room being overlooked
        view_desc: What you see from above
        distance: How far down (affects detail)
        perceive_watcher: Can people below see the watcher?
        watcher_desc: What people below see
    """
    if not hasattr(high_room, 'add_overlook'):
        raise TypeError(f"{high_room} doesn't have SpatialMixin")
    
    high_room.add_overlook(Overlook(
        room_key=low_room.key,
        direction=Direction.BELOW,
        distance=distance,
        view_desc=view_desc,
        perceive_watcher=perceive_watcher,
        watcher_desc=watcher_desc,
    ))


def setup_partition(
    room1,
    room2,
    partition_type: PartitionType,
    desc: str = "",
    bidirectional: bool = True,
    can_toggle: bool = False,
    toggle_to: PartitionType = None
) -> None:
    """
    Helper to set up a partition between two rooms.
    
    Args:
        room1, room2: The rooms separated by the partition
        partition_type: What kind of barrier
        desc: Description ("iron bars", "thick glass")
        bidirectional: Both rooms perceive through it
        can_toggle: Can it be opened/closed
        toggle_to: What it toggles to
    """
    if not hasattr(room1, 'add_partition'):
        raise TypeError(f"{room1} doesn't have SpatialMixin")
    
    room1.add_partition(PartitionLink(
        room_key=room2.key,
        partition_type=partition_type,
        desc=desc,
        can_toggle=can_toggle,
        toggle_to=toggle_to,
    ))
    
    if bidirectional and hasattr(room2, 'add_partition'):
        room2.add_partition(PartitionLink(
            room_key=room1.key,
            partition_type=partition_type,
            desc=desc,
            can_toggle=can_toggle,
            toggle_to=toggle_to,
        ))


# =============================================================================
# EXPORTS
# =============================================================================

__all__ = [
    # Enums
    "Distance",
    "Direction",
    "PartitionType",
    "PARTITION_PROPERTIES",
    
    # Data classes
    "Adjacency",
    "Overlook",
    "PartitionLink",
    
    # Helper functions
    "describe_occupants_at_distance",
    "get_room_by_key",
    
    # Mixin and Room
    "SpatialMixin",
    "SpatialRoom",
    
    # Builder helpers
    "link_adjacent_rooms",
    "setup_overlook",
    "setup_partition",
]
