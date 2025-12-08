"""
Grid Room System - Positional Awareness in Large Spaces

For rooms where "where you are in the room" matters:
- Large plazas with distinct areas
- Markets with stall positions
- Open meadows with different patches
- Mine chambers with multiple tunnel entrances

Grid rooms track:
- Character positions within the space
- Distance between positions
- What's visible/accessible from each position
- Area-specific descriptions and features

Usage:
    A 5x5 plaza might have:
    - "center" (2,2) - the fountain
    - "north gate" (2,0) - entrance to north
    - "south market" (2,4) - where vendors gather
    
    Players can be "near the fountain" or "by the north gate" and
    see different things, interact with different objects, hear
    different sounds.
"""

from typing import Optional, Dict, Any, List, Tuple, Set
# Handle early import during Django migration loading
try:
    from evennia.typeclasses.attributes import AttributeProperty
except (ImportError, TypeError, AttributeError):
    def AttributeProperty(default=None, **kwargs):
        return default

# Import directly from base module to avoid circular import
from typeclasses.base_rooms import Room, OutdoorRoom, IndoorRoom
import math


# =============================================================================
# GRID POSITION
# =============================================================================

class GridPosition:
    """
    A named position within a grid room.
    
    Positions have:
    - Coordinates (x, y)
    - Name ("by the fountain", "near the north gate")
    - Description (what you see from here)
    - Features (what's interactable here)
    - Connections (can you move directly to other positions?)
    """
    
    def __init__(
        self,
        name: str,
        x: int,
        y: int,
        desc: str = "",
        short_desc: str = "",
        features: List[str] = None,
        blocks_movement: bool = False,
        blocks_sight: bool = False,
    ):
        self.name = name
        self.x = x
        self.y = y
        self.desc = desc
        self.short_desc = short_desc
        self.features = features or []
        self.blocks_movement = blocks_movement
        self.blocks_sight = blocks_sight
    
    @property
    def coords(self) -> Tuple[int, int]:
        """Return (x, y) tuple."""
        return (self.x, self.y)
    
    def distance_to(self, other: "GridPosition") -> float:
        """Calculate distance to another position."""
        return math.sqrt((self.x - other.x)**2 + (self.y - other.y)**2)
    
    def is_adjacent(self, other: "GridPosition") -> bool:
        """Check if positions are adjacent (including diagonal)."""
        return abs(self.x - other.x) <= 1 and abs(self.y - other.y) <= 1
    
    def to_dict(self) -> dict:
        """Serialize for storage."""
        return {
            "name": self.name,
            "x": self.x,
            "y": self.y,
            "desc": self.desc,
            "short_desc": self.short_desc,
            "features": self.features,
            "blocks_movement": self.blocks_movement,
            "blocks_sight": self.blocks_sight,
        }
    
    @classmethod
    def from_dict(cls, data: dict) -> "GridPosition":
        """Deserialize from storage."""
        return cls(**data)


# =============================================================================
# GRID ROOM MIXIN
# =============================================================================

class GridRoomMixin:
    """
    Mixin that adds grid functionality to any room type.
    
    Apply to Room, IndoorRoom, or OutdoorRoom to create
    positional awareness.
    """
    
    # -------------------------------------------------------------------------
    # Grid Configuration
    # -------------------------------------------------------------------------
    
    grid_width = AttributeProperty(default=5)
    grid_height = AttributeProperty(default=5)
    
    # Named positions: {name: GridPosition.to_dict()}
    grid_positions = AttributeProperty(default=dict)
    
    # Character positions: {character_id: position_name}
    character_positions = AttributeProperty(default=dict)
    
    # Default position for new arrivals
    default_position = AttributeProperty(default="center")
    
    # -------------------------------------------------------------------------
    # Position Management
    # -------------------------------------------------------------------------
    
    def add_position(self, position: GridPosition) -> None:
        """Add a named position to the grid."""
        positions = dict(self.grid_positions)
        positions[position.name] = position.to_dict()
        self.grid_positions = positions
    
    def get_position(self, name: str) -> Optional[GridPosition]:
        """Get a position by name."""
        if name in self.grid_positions:
            return GridPosition.from_dict(self.grid_positions[name])
        return None
    
    def get_position_at(self, x: int, y: int) -> Optional[GridPosition]:
        """Get position at specific coordinates."""
        for pos_data in self.grid_positions.values():
            if pos_data["x"] == x and pos_data["y"] == y:
                return GridPosition.from_dict(pos_data)
        return None
    
    def get_all_positions(self) -> List[GridPosition]:
        """Get all defined positions."""
        return [GridPosition.from_dict(p) for p in self.grid_positions.values()]
    
    def remove_position(self, name: str) -> bool:
        """Remove a position."""
        if name in self.grid_positions:
            positions = dict(self.grid_positions)
            del positions[name]
            self.grid_positions = positions
            return True
        return False
    
    # -------------------------------------------------------------------------
    # Character Position Tracking
    # -------------------------------------------------------------------------
    
    def get_character_position(self, character) -> Optional[GridPosition]:
        """Get a character's current position in the room."""
        char_id = character.id
        if char_id in self.character_positions:
            pos_name = self.character_positions[char_id]
            return self.get_position(pos_name)
        return self.get_position(self.default_position)
    
    def set_character_position(self, character, position_name: str) -> bool:
        """
        Set a character's position.
        
        Returns True if position exists and was set.
        """
        if position_name not in self.grid_positions:
            return False
        
        positions = dict(self.character_positions)
        positions[character.id] = position_name
        self.character_positions = positions
        return True
    
    def clear_character_position(self, character) -> None:
        """Remove a character's position tracking (when they leave)."""
        char_id = character.id
        if char_id in self.character_positions:
            positions = dict(self.character_positions)
            del positions[char_id]
            self.character_positions = positions
    
    def get_characters_at_position(self, position_name: str) -> List:
        """Get all characters at a specific position."""
        characters = []
        for obj in self.contents:
            if hasattr(obj, 'id') and obj.id in self.character_positions:
                if self.character_positions[obj.id] == position_name:
                    characters.append(obj)
        return characters
    
    # -------------------------------------------------------------------------
    # Movement Within Grid
    # -------------------------------------------------------------------------
    
    def can_move_to_position(
        self, 
        character, 
        target_position: str
    ) -> Tuple[bool, str]:
        """
        Check if character can move to target position.
        
        Returns (can_move, reason)
        """
        current = self.get_character_position(character)
        target = self.get_position(target_position)
        
        if not target:
            return (False, f"There is no position called '{target_position}'.")
        
        if target.blocks_movement:
            return (False, f"You cannot move to {target.name}.")
        
        # Check if adjacent or allow longer moves
        if current and not current.is_adjacent(target):
            # Check for blocking positions between
            if self._path_blocked(current, target):
                return (False, "Something blocks your path.")
        
        return (True, "")
    
    def _path_blocked(
        self, 
        start: GridPosition, 
        end: GridPosition
    ) -> bool:
        """Check if movement path is blocked."""
        # Simple line-of-sight check
        dx = end.x - start.x
        dy = end.y - start.y
        steps = max(abs(dx), abs(dy))
        
        if steps == 0:
            return False
        
        for i in range(1, steps):
            check_x = start.x + int(dx * i / steps)
            check_y = start.y + int(dy * i / steps)
            
            pos = self.get_position_at(check_x, check_y)
            if pos and pos.blocks_movement:
                return True
        
        return False
    
    def move_character_to_position(
        self, 
        character, 
        target_position: str,
        quiet: bool = False
    ) -> bool:
        """
        Move a character to a position within the room.
        
        Returns True if movement succeeded.
        """
        can_move, reason = self.can_move_to_position(character, target_position)
        
        if not can_move:
            if not quiet:
                character.msg(reason)
            return False
        
        old_pos = self.get_character_position(character)
        new_pos = self.get_position(target_position)
        
        # Update position
        self.set_character_position(character, target_position)
        
        if not quiet:
            # Notify character
            character.msg(f"You move to {new_pos.name}.")
            if new_pos.short_desc:
                character.msg(new_pos.short_desc)
            
            # Notify others at old position
            if old_pos:
                for other in self.get_characters_at_position(old_pos.name):
                    if other != character:
                        other.msg(f"{character.key} moves toward {new_pos.name}.")
            
            # Notify others at new position
            for other in self.get_characters_at_position(target_position):
                if other != character:
                    other.msg(f"{character.key} arrives at {new_pos.name}.")
        
        return True
    
    # -------------------------------------------------------------------------
    # Visibility
    # -------------------------------------------------------------------------
    
    def can_see_position(
        self, 
        from_pos: GridPosition, 
        to_pos: GridPosition
    ) -> bool:
        """Check if one position can see another."""
        if to_pos.blocks_sight:
            return False
        
        # Check for blocking positions between
        return not self._sight_blocked(from_pos, to_pos)
    
    def _sight_blocked(
        self, 
        start: GridPosition, 
        end: GridPosition
    ) -> bool:
        """Check if line of sight is blocked."""
        dx = end.x - start.x
        dy = end.y - start.y
        steps = max(abs(dx), abs(dy))
        
        if steps == 0:
            return False
        
        for i in range(1, steps):
            check_x = start.x + int(dx * i / steps)
            check_y = start.y + int(dy * i / steps)
            
            pos = self.get_position_at(check_x, check_y)
            if pos and pos.blocks_sight:
                return True
        
        return False
    
    def get_visible_positions(self, from_position: str) -> List[GridPosition]:
        """Get all positions visible from a given position."""
        from_pos = self.get_position(from_position)
        if not from_pos:
            return []
        
        visible = []
        for pos in self.get_all_positions():
            if pos.name != from_position and self.can_see_position(from_pos, pos):
                visible.append(pos)
        
        return visible
    
    def get_characters_visible_from(self, position_name: str) -> List:
        """Get all characters visible from a position."""
        visible_positions = self.get_visible_positions(position_name)
        visible_positions.append(self.get_position(position_name))  # Include current
        
        characters = []
        for pos in visible_positions:
            if pos:
                characters.extend(self.get_characters_at_position(pos.name))
        
        return characters
    
    # -------------------------------------------------------------------------
    # Distance and Proximity
    # -------------------------------------------------------------------------
    
    def get_distance(self, pos1: str, pos2: str) -> float:
        """Get distance between two positions."""
        p1 = self.get_position(pos1)
        p2 = self.get_position(pos2)
        
        if not p1 or not p2:
            return float('inf')
        
        return p1.distance_to(p2)
    
    def get_nearby_positions(
        self, 
        position_name: str, 
        max_distance: float = 2.0
    ) -> List[GridPosition]:
        """Get positions within a certain distance."""
        center = self.get_position(position_name)
        if not center:
            return []
        
        return [
            pos for pos in self.get_all_positions()
            if pos.name != position_name and center.distance_to(pos) <= max_distance
        ]
    
    # -------------------------------------------------------------------------
    # Room Hooks Override
    # -------------------------------------------------------------------------
    
    def at_object_receive(self, moved_obj, source_location, move_type=None, **kwargs):
        """Called when something enters the room."""
        super().at_object_receive(moved_obj, source_location, move_type, **kwargs)
        
        # Set new character to default position
        if hasattr(moved_obj, 'account') or (hasattr(moved_obj, 'is_npc') and moved_obj.is_npc):
            self.set_character_position(moved_obj, self.default_position)
    
    def at_object_leave(self, moved_obj, target_location, move_type=None, **kwargs):
        """Called when something leaves the room."""
        super().at_object_leave(moved_obj, target_location, move_type, **kwargs)
        
        # Clear position tracking
        self.clear_character_position(moved_obj)
    
    # -------------------------------------------------------------------------
    # Description Override
    # -------------------------------------------------------------------------
    
    def get_position_description(self, position_name: str) -> str:
        """Get description specific to a position."""
        pos = self.get_position(position_name)
        if not pos:
            return ""
        
        parts = []
        
        # Position description
        if pos.desc:
            parts.append(pos.desc)
        
        # What's visible from here
        visible = self.get_visible_positions(position_name)
        if visible:
            visible_names = [v.name for v in visible]
            parts.append(f"From here you can see: {', '.join(visible_names)}")
        
        # Who's here
        chars_here = self.get_characters_at_position(position_name)
        if chars_here:
            char_names = [c.key for c in chars_here]
            parts.append(f"Also here: {', '.join(char_names)}")
        
        # Features
        if pos.features:
            parts.append(f"You notice: {', '.join(pos.features)}")
        
        return "\n".join(parts)
    
    def process_shortcodes(self, text: str, looker=None) -> str:
        """Add grid-specific shortcodes."""
        text = super().process_shortcodes(text, looker)
        
        # Current position
        if looker:
            pos = self.get_character_position(looker)
            if pos:
                text = text.replace("<position>", pos.name)
                text = text.replace("<position.desc>", pos.desc or "")
                text = text.replace("<position.short>", pos.short_desc or "")
            else:
                text = text.replace("<position>", "somewhere")
                text = text.replace("<position.desc>", "")
                text = text.replace("<position.short>", "")
        
        # List all positions
        all_positions = [p.name for p in self.get_all_positions()]
        text = text.replace("<positions>", ", ".join(all_positions))
        
        return text


# =============================================================================
# GRID ROOM TYPES
# =============================================================================

class GridRoom(GridRoomMixin, Room):
    """Standard room with grid positions."""
    pass


class GridIndoorRoom(GridRoomMixin, IndoorRoom):
    """Indoor room with grid positions."""
    pass


class GridOutdoorRoom(GridRoomMixin, OutdoorRoom):
    """Outdoor room with grid positions."""
    pass


# =============================================================================
# HELPER: CREATE STANDARD GRID LAYOUTS
# =============================================================================

def create_plaza_grid(room, size: int = 5) -> None:
    """
    Set up a standard plaza grid with center and edges.
    
    Creates positions:
    - center
    - north, south, east, west (edges)
    - northeast, northwest, southeast, southwest (corners)
    """
    room.grid_width = size
    room.grid_height = size
    mid = size // 2
    
    # Center
    room.add_position(GridPosition(
        name="center",
        x=mid, y=mid,
        short_desc="You stand in the center of the plaza.",
    ))
    
    # Cardinal edges
    room.add_position(GridPosition(
        name="north edge",
        x=mid, y=0,
        short_desc="You stand at the northern edge of the plaza.",
    ))
    room.add_position(GridPosition(
        name="south edge",
        x=mid, y=size-1,
        short_desc="You stand at the southern edge of the plaza.",
    ))
    room.add_position(GridPosition(
        name="east edge",
        x=size-1, y=mid,
        short_desc="You stand at the eastern edge of the plaza.",
    ))
    room.add_position(GridPosition(
        name="west edge",
        x=0, y=mid,
        short_desc="You stand at the western edge of the plaza.",
    ))
    
    # Corners
    room.add_position(GridPosition(
        name="northeast corner",
        x=size-1, y=0,
        short_desc="You stand in the northeastern corner of the plaza.",
    ))
    room.add_position(GridPosition(
        name="northwest corner",
        x=0, y=0,
        short_desc="You stand in the northwestern corner of the plaza.",
    ))
    room.add_position(GridPosition(
        name="southeast corner",
        x=size-1, y=size-1,
        short_desc="You stand in the southeastern corner of the plaza.",
    ))
    room.add_position(GridPosition(
        name="southwest corner",
        x=0, y=size-1,
        short_desc="You stand in the southwestern corner of the plaza.",
    ))
    
    room.default_position = "center"


def create_linear_grid(room, length: int = 5, direction: str = "north-south") -> None:
    """
    Set up a linear path grid.
    
    Creates positions along a line (for tunnels, paths, etc.)
    """
    if direction == "north-south":
        room.grid_width = 1
        room.grid_height = length
        
        for i in range(length):
            if i == 0:
                name = "north end"
            elif i == length - 1:
                name = "south end"
            else:
                name = f"middle ({i})"
            
            room.add_position(GridPosition(
                name=name,
                x=0, y=i,
            ))
    else:  # east-west
        room.grid_width = length
        room.grid_height = 1
        
        for i in range(length):
            if i == 0:
                name = "west end"
            elif i == length - 1:
                name = "east end"
            else:
                name = f"middle ({i})"
            
            room.add_position(GridPosition(
                name=name,
                x=i, y=0,
            ))
    
    room.default_position = "middle (1)" if length > 2 else "north end"


# =============================================================================
# EXPORTS
# =============================================================================

__all__ = [
    "GridPosition",
    "GridRoomMixin",
    "GridRoom",
    "GridIndoorRoom",
    "GridOutdoorRoom",
    "create_plaza_grid",
    "create_linear_grid",
]
