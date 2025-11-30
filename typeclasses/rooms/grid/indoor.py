"""
Room - Indoor Grid

Indoor room with coordinate/shape system and positional awareness.
"""

from evennia import AttributeProperty
from typeclasses.rooms.core.indoor import IndoorRoom


class GridMixin:
    """
    Mixin that adds coordinate, shape, and positional awareness to any room.
    
    Characters have positions within grid rooms.
    Exits/objects/NPCs exist at specific coordinates.
    Perception is based on distance and sensory ranges.
    """
    
    # -------------------------------------------------------------------------
    # COORDINATES
    # -------------------------------------------------------------------------
    
    x = AttributeProperty(default=0)  # X coordinate (origin point)
    y = AttributeProperty(default=0)  # Y coordinate
    z = AttributeProperty(default=0)  # Z coordinate (floor/elevation)
    
    # -------------------------------------------------------------------------
    # SHAPE SYSTEM
    # -------------------------------------------------------------------------
    
    shape_type = AttributeProperty(default="single")  # "single", "square", "rect", "L", "T", "custom"
    shape_data = AttributeProperty(default=None)  # Shape-specific data
    
    # -------------------------------------------------------------------------
    # Shape Types Documentation:
    # -------------------------------------------------------------------------
    #
    # "single" (default)
    #     shape_data = None
    #     Occupies just (x, y, z)
    #
    # "square"
    #     shape_data = {"size": 3}
    #     Occupies size x size grid centered on origin
    #
    # "rect"
    #     shape_data = {"width": 4, "height": 2}
    #     Occupies width x height from origin
    #
    # "L"
    #     shape_data = {"arm1": 3, "arm2": 2, "rotation": 0}
    #     L-shaped room, rotation 0/90/180/270
    #
    # "T"
    #     shape_data = {"stem": 2, "bar": 3, "rotation": 0}
    #     T-shaped room
    #
    # "custom"
    #     shape_data = {"cells": [(0,0), (1,0), (1,1), (2,1)]}
    #     Arbitrary shape defined by coordinate offsets
    
    # -------------------------------------------------------------------------
    # SENSORY RANGES (room-level defaults/overrides)
    # -------------------------------------------------------------------------
    
    default_sight_range = AttributeProperty(default=5)  # Default visibility in this room
    default_hearing_range = AttributeProperty(default=8)  # Default hearing range
    default_smell_range = AttributeProperty(default=4)  # Default smell range
    
    # Environmental modifiers
    visibility_modifier = AttributeProperty(default=0)  # +/- to sight range (fog, darkness)
    sound_modifier = AttributeProperty(default=0)  # +/- to hearing (loud, muffled)
    smell_modifier = AttributeProperty(default=0)  # +/- to smell (strong wind, stench)
    
    # -------------------------------------------------------------------------
    # SHAPE METHODS
    # -------------------------------------------------------------------------
    
    def get_occupied_cells(self):
        """
        Return all grid coordinates this room occupies.
        
        Returns:
            list: List of (x, y, z) tuples
        """
        origin = (self.x, self.y, self.z)
        
        if self.shape_type == "single" or not self.shape_data:
            return [origin]
        
        cells = []
        
        if self.shape_type == "square":
            size = self.shape_data.get("size", 1)
            offset = size // 2
            for dx in range(-offset, offset + 1):
                for dy in range(-offset, offset + 1):
                    cells.append((self.x + dx, self.y + dy, self.z))
        
        elif self.shape_type == "rect":
            width = self.shape_data.get("width", 1)
            height = self.shape_data.get("height", 1)
            for dx in range(width):
                for dy in range(height):
                    cells.append((self.x + dx, self.y + dy, self.z))
        
        elif self.shape_type == "custom":
            offsets = self.shape_data.get("cells", [(0, 0)])
            for offset in offsets:
                if len(offset) == 2:
                    dx, dy = offset
                    dz = 0
                else:
                    dx, dy, dz = offset
                cells.append((self.x + dx, self.y + dy, self.z + dz))
        
        # -------------------------------------------------------------------------
        # FUTURE: L and T shapes
        # -------------------------------------------------------------------------
        
        # TODO: Implement L-shape calculation
        # elif self.shape_type == "L":
        #     arm1 = self.shape_data.get("arm1", 2)
        #     arm2 = self.shape_data.get("arm2", 2)
        #     rotation = self.shape_data.get("rotation", 0)
        #     # Calculate cells based on rotation...
        #     pass
        #
        # System: GRID_SHAPE_SYSTEM
        
        # TODO: Implement T-shape calculation
        # elif self.shape_type == "T":
        #     pass
        
        return cells if cells else [origin]
    
    def contains_coordinate(self, x, y, z=None):
        """
        Check if this room contains a specific coordinate.
        """
        if z is None:
            z = self.z
        return (x, y, z) in self.get_occupied_cells()
    
    def is_valid_position(self, x, y):
        """
        Check if (x, y) is a valid position within this room.
        
        Args:
            x, y: Position to check (relative to room's coordinate space)
            
        Returns:
            bool: Whether position is within room shape
        """
        return (x, y, self.z) in self.get_occupied_cells()
    
    # -------------------------------------------------------------------------
    # DISTANCE CALCULATIONS
    # -------------------------------------------------------------------------
    
    def get_distance(self, pos1, pos2):
        """
        Calculate Manhattan distance between two positions.
        
        Args:
            pos1: (x, y) tuple
            pos2: (x, y) tuple
            
        Returns:
            int: Distance in cells
        """
        if pos1 is None or pos2 is None:
            return 0
        x1, y1 = pos1[:2]
        x2, y2 = pos2[:2]
        return abs(x2 - x1) + abs(y2 - y1)
    
    # -------------------------------------------------------------------------
    # POSITIONAL CONTENT QUERIES
    # -------------------------------------------------------------------------
    
    def get_things_at_position(self, x, y):
        """
        Get all objects/npcs at a specific grid position.
        
        Args:
            x, y: Grid coordinates
            
        Returns:
            list: Objects at that position
        """
        things = []
        for obj in self.contents:
            obj_pos = obj.db.grid_position
            if obj_pos and obj_pos[0] == x and obj_pos[1] == y:
                things.append(obj)
        return things
    
    def get_exits_at_position(self, x, y):
        """
        Get all exits at a specific grid position.
        
        Args:
            x, y: Grid coordinates
            
        Returns:
            list: Exits at that position
        """
        exits = []
        for ex in self.exits:
            ex_pos = ex.db.grid_location
            if ex_pos and ex_pos[0] == x and ex_pos[1] == y:
                exits.append(ex)
        return exits
    
    # -------------------------------------------------------------------------
    # SENSORY PERCEPTION
    # -------------------------------------------------------------------------
    
    def get_effective_sight_range(self, character):
        """
        Get effective sight range for a character in this room.
        
        Combines character's base sight with room modifiers.
        """
        base = character.db.sight_range or self.default_sight_range
        return max(0, base + self.visibility_modifier)
    
    def get_effective_hearing_range(self, character):
        """
        Get effective hearing range for a character in this room.
        """
        base = character.db.hearing_range or self.default_hearing_range
        return max(0, base + self.sound_modifier)
    
    def get_effective_smell_range(self, character):
        """
        Get effective smell range for a character in this room.
        """
        base = character.db.smell_range or self.default_smell_range
        return max(0, base + self.smell_modifier)
    
    def get_visible_exits(self, looker):
        """
        Get exits visible to a character based on position and sight range.
        
        Args:
            looker: Character looking
            
        Returns:
            list: List of (exit, distance, appearance) tuples
        """
        looker_pos = looker.db.grid_position
        if looker_pos is None:
            looker_pos = (self.x, self.y)
        
        sight_range = self.get_effective_sight_range(looker)
        visible = []
        
        for ex in self.exits:
            ex_pos = ex.db.grid_location
            
            # No grid location = always visible (standard exit behavior)
            if ex_pos is None:
                visible.append((ex, 0, ex.key))
                continue
            
            distance = self.get_distance(looker_pos, ex_pos)
            
            # Check if exit itself is visible from this range
            exit_visible_range = ex.db.visible_range or 3
            
            if distance <= sight_range and distance <= exit_visible_range:
                if not ex.db.hidden:
                    appearance = ex.get_distant_appearance(distance)
                    if appearance:
                        visible.append((ex, distance, appearance))
        
        return visible
    
    def get_audible_things(self, looker):
        """
        Get things the character can hear from their position.
        
        Returns:
            list: List of (thing, distance, sound_description) tuples
        """
        looker_pos = looker.db.grid_position
        if looker_pos is None:
            looker_pos = (self.x, self.y)
        
        hearing_range = self.get_effective_hearing_range(looker)
        audible = []
        
        # Check exits for sounds
        for ex in self.exits:
            ex_pos = ex.db.grid_location
            if ex_pos is None:
                continue
            
            distance = self.get_distance(looker_pos, ex_pos)
            
            if distance <= hearing_range:
                sound = ex.get_sound_from_distance(distance)
                if sound:
                    audible.append((ex, distance, sound))
        
        # -------------------------------------------------------------------------
        # FUTURE: Sounds from objects, NPCs, other rooms
        # -------------------------------------------------------------------------
        
        # TODO: Object Sounds
        # for obj in self.contents:
        #     if hasattr(obj, 'get_sound_from_distance'):
        #         ...
        #
        # System: SOUND_SYSTEM
        
        # TODO: Sounds from adjacent rooms
        # Check linked rooms, sounds bleeding through exits
        #
        # System: SOUND_PROPAGATION_SYSTEM
        
        return audible
    
    def get_smellable_things(self, looker):
        """
        Get things the character can smell from their position.
        
        Returns:
            list: List of (thing, distance, smell_description) tuples
        """
        looker_pos = looker.db.grid_position
        if looker_pos is None:
            looker_pos = (self.x, self.y)
        
        smell_range = self.get_effective_smell_range(looker)
        smellable = []
        
        # Check exits for smells
        for ex in self.exits:
            ex_pos = ex.db.grid_location
            if ex_pos is None:
                continue
            
            distance = self.get_distance(looker_pos, ex_pos)
            
            if distance <= smell_range:
                smell = ex.get_smell_from_distance(distance)
                if smell:
                    smellable.append((ex, distance, smell))
        
        # -------------------------------------------------------------------------
        # FUTURE: Smells from objects, NPCs, other rooms
        # -------------------------------------------------------------------------
        
        # TODO: Object Smells
        # for obj in self.contents:
        #     if hasattr(obj, 'get_smell_from_distance'):
        #         ...
        #
        # System: SMELL_SYSTEM
        
        return smellable
    
    # -------------------------------------------------------------------------
    # MODIFIED APPEARANCE FOR GRID ROOMS
    # -------------------------------------------------------------------------
    
    def return_appearance(self, looker, **kwargs):
        """
        Modified appearance that shows position-based information.
        """
        # Get base appearance
        appearance = super().return_appearance(looker, **kwargs)
        
        looker_pos = looker.db.grid_position
        if looker_pos is None:
            return appearance
        
        # Build grid-specific information
        grid_info = []
        
        # Current position
        grid_info.append(f"\n|wYour position:|n [{looker_pos[0]}, {looker_pos[1]}]")
        
        # Visible exits by distance
        visible_exits = self.get_visible_exits(looker)
        if visible_exits:
            here_exits = []
            near_exits = []
            far_exits = []
            
            for ex, distance, desc in visible_exits:
                if distance == 0:
                    here_exits.append(f"  {desc}")
                elif distance <= 2:
                    direction = self._get_direction_to(looker_pos, ex.db.grid_location)
                    near_exits.append(f"  {desc} ({direction}, {distance} cells)")
                else:
                    direction = self._get_direction_to(looker_pos, ex.db.grid_location)
                    far_exits.append(f"  {desc} ({direction}, {distance} cells)")
            
            if here_exits:
                grid_info.append("\n|wExits here:|n")
                grid_info.extend(here_exits)
            if near_exits:
                grid_info.append("\n|wNearby:|n")
                grid_info.extend(near_exits)
            if far_exits:
                grid_info.append("\n|wIn the distance:|n")
                grid_info.extend(far_exits)
        
        # Audible things
        audible = self.get_audible_things(looker)
        if audible:
            grid_info.append("\n|wYou hear:|n")
            for thing, distance, sound in audible:
                direction = ""
                if hasattr(thing, 'db') and thing.db.grid_location:
                    direction = f" to the {self._get_direction_to(looker_pos, thing.db.grid_location)}"
                grid_info.append(f"  {sound}{direction}")
        
        # Smellable things
        smellable = self.get_smellable_things(looker)
        if smellable:
            grid_info.append("\n|wYou smell:|n")
            for thing, distance, smell in smellable:
                direction = ""
                if hasattr(thing, 'db') and thing.db.grid_location:
                    direction = f" from the {self._get_direction_to(looker_pos, thing.db.grid_location)}"
                grid_info.append(f"  {smell}{direction}")
        
        return appearance + "\n".join(grid_info)
    
    def _get_direction_to(self, from_pos, to_pos):
        """
        Get cardinal direction from one position to another.
        """
        if from_pos is None or to_pos is None:
            return "nearby"
        
        dx = to_pos[0] - from_pos[0]
        dy = to_pos[1] - from_pos[1]
        
        if dx == 0 and dy == 0:
            return "here"
        
        direction = ""
        if dy > 0:
            direction += "north"
        elif dy < 0:
            direction += "south"
        
        if dx > 0:
            direction += "east"
        elif dx < 0:
            direction += "west"
        
        return direction or "nearby"
    
    # -------------------------------------------------------------------------
    # FUTURE: PATHFINDING
    # -------------------------------------------------------------------------
    
    # TODO: Pathfinding Support
    # def get_path_to(self, from_pos, to_pos):
    #     """
    #     Calculate path from one cell to another.
    #     
    #     Returns:
    #         list: List of (x, y) positions forming path, or None if impossible
    #     
    #     System: PATHFINDING_SYSTEM
    #     """
    #     pass
    #
    # def get_adjacent_cells(self, x, y):
    #     """Get valid cells adjacent to position."""
    #     pass
    #
    # def is_cell_passable(self, x, y):
    #     """Check if a cell can be walked through."""
    #     pass
    
    # -------------------------------------------------------------------------
    # FUTURE: MAP RENDERING
    # -------------------------------------------------------------------------
    
    # TODO: ASCII Map
    # def get_ascii_map(self, looker):
    #     """
    #     Generate ASCII map of room showing:
    #     - Room shape
    #     - Character positions
    #     - Exit locations
    #     - Objects
    #     
    #     System: MAP_SYSTEM
    #     """
    #     pass
    #
    # def get_map_symbol(self):
    #     """Return symbol for this room on larger maps."""
    #     pass
    
    # -------------------------------------------------------------------------
    # FUTURE: LINE OF SIGHT
    # -------------------------------------------------------------------------
    
    # TODO: LoS System
    # def has_line_of_sight(self, from_pos, to_pos):
    #     """
    #     Check if there's clear line of sight between positions.
    #     
    #     Considers:
    #     - Obstacles
    #     - Interior walls
    #     - Large objects
    #     
    #     System: LINE_OF_SIGHT_SYSTEM
    #     """
    #     pass
    
    # -------------------------------------------------------------------------
    # FUTURE: GRID ROOM REGISTRATION
    # -------------------------------------------------------------------------
    
    # TODO: World Grid Registration
    # def at_object_creation(self):
    #     """Register with world grid on creation."""
    #     super().at_object_creation()
    #     # from systems.grid import GRID_MANAGER
    #     # GRID_MANAGER.register_room(self)
    #
    # def at_object_delete(self):
    #     """Unregister from grid on deletion."""
    #     # GRID_MANAGER.unregister_room(self)
    #     return super().at_object_delete()
    #
    # System: GRID_SYSTEM


class IndoorGridRoom(GridMixin, IndoorRoom):
    """
    Indoor room with coordinate/shape support.
    
    Combines:
        - All base Room features (shortcodes, regions, etc.)
        - Indoor features (lighting, surfaces, acoustics)
        - Grid features (coordinates, shapes, positional perception)
    
    Use for:
        - Mapped dungeons
        - Building interiors with floor plans
        - Any indoor space that needs grid positioning
    """
    
    # -------------------------------------------------------------------------
    # FUTURE: INDOOR GRID SPECIFIC
    # -------------------------------------------------------------------------
    
    # TODO: Floor/Level System
    # floor_number = AttributeProperty(default=0)
    # building_id = AttributeProperty(default="")
    #
    # def get_floors_above(self):
    #     """Return rooms directly above this one."""
    #     pass
    #
    # def get_floors_below(self):
    #     """Return rooms directly below this one."""
    #     pass
    #
    # System: BUILDING_SYSTEM
    
    # TODO: Interior Walls
    # interior_walls = AttributeProperty(default=[])
    #
    # For rooms with internal divisions that block movement/sight
    # interior_walls = [
    #     {"from": (0, 0), "to": (0, 2), "type": "solid"},
    #     {"from": (1, 1), "to": (2, 1), "type": "partial"}
    # ]
    #
    # System: INTERIOR_WALL_SYSTEM
    
    pass
