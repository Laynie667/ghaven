"""
Room - Indoor

Indoor room type with lighting, surfaces, and enclosed space properties.
"""

from evennia import AttributeProperty
from .base import Room


class IndoorRoom(Room):
    """
    Indoor room - enclosed spaces with ceilings, walls, lighting control.
    
    Adds:
        - Lighting system (affects visibility, mood)
        - Surface system (ceiling, floor, walls with shortcodes)
        - Window awareness (for time-of-day light changes)
        - Acoustics (for stealth/eavesdropping systems)
        - Temperature (baseline, modified by systems)
    
    Shortcodes added:
        <surface:ceiling>  - ceiling description
        <surface:floor>    - floor description
        <surface:wall>     - generic wall description
        <surface:north_wall>, etc. - specific wall
    """
    
    # -------------------------------------------------------------------------
    # LIGHTING SYSTEM
    # -------------------------------------------------------------------------
    
    lighting = AttributeProperty(default="normal")  # "dark", "dim", "normal", "bright"
    light_source = AttributeProperty(default="")  # "torches", "windows", "magical", "none"
    has_windows = AttributeProperty(default=False)  # If True, time of day can affect lighting
    
    # -------------------------------------------------------------------------
    # FUTURE: Dynamic Lighting
    # -------------------------------------------------------------------------
    
    # TODO: Light Level Calculation
    # Instead of static lighting, calculate from light sources in room
    #
    # base_light_level = AttributeProperty(default=0)  # Inherent room light
    # 
    # def calculate_lighting(self):
    #     """
    #     Calculate current light level from all sources.
    #     
    #     Checks:
    #     - base_light_level
    #     - Light-emitting objects in room
    #     - Character-carried light sources
    #     - Window + time of day
    #     
    #     Returns:
    #         str: "dark", "dim", "normal", or "bright"
    #     
    #     System: LIGHTING_SYSTEM
    #     """
    #     pass
    #
    # def get_light_sources(self):
    #     """Return all objects currently providing light."""
    #     pass
    
    # -------------------------------------------------------------------------
    # ENCLOSURE PROPERTIES
    # -------------------------------------------------------------------------
    
    enclosed = AttributeProperty(default=True)  # Fully enclosed (no weather)
    
    # -------------------------------------------------------------------------
    # SURFACE SYSTEM
    # Each surface can have its own description with shortcodes
    # -------------------------------------------------------------------------
    
    ceiling_desc = AttributeProperty(default="")
    floor_desc = AttributeProperty(default="")
    wall_desc = AttributeProperty(default="")  # Generic walls
    
    # -------------------------------------------------------------------------
    # FUTURE: Detailed Surface System
    # -------------------------------------------------------------------------
    
    # TODO: Per-Wall Descriptions
    # For rooms where specific walls matter
    #
    # surfaces = AttributeProperty(default={})
    #
    # Example:
    # surfaces = {
    #     "ceiling": "Vaulted stone arches. <obj:chandelier>",
    #     "floor": "Cold flagstones.",
    #     "north_wall": "Bare stone. <sys:graffiti:north>",
    #     "south_wall": "A faded tapestry. <obj:tapestry>",
    #     "east_wall": "A barred window.",
    #     "west_wall": "The door you entered through."
    # }
    #
    # def get_surface_desc(self, surface_name):
    #     """Get description for a specific surface, processed through shortcodes."""
    #     pass
    #
    # System: SURFACE_SYSTEM
    
    # -------------------------------------------------------------------------
    # FUTURE: GRAFFITI/WRITING SYSTEM
    # Persistent writing on surfaces
    # -------------------------------------------------------------------------
    
    # TODO: Graffiti System
    # wall_writings = AttributeProperty(default={})
    #
    # Example:
    # wall_writings = {
    #     "north": [
    #         {"text": "John was here", "author": "#123", "date": timestamp},
    #         {"text": "The treasure is beneath the old oak", "author": None}
    #     ]
    # }
    #
    # def add_writing(self, surface, text, author=None):
    #     """Add writing to a surface."""
    #     pass
    #
    # def remove_writing(self, surface, index):
    #     """Remove writing from a surface."""
    #     pass
    #
    # def get_writings(self, surface):
    #     """Get all writings on a surface."""
    #     pass
    #
    # System: GRAFFITI_SYSTEM
    
    # -------------------------------------------------------------------------
    # FUTURE: ATTACHMENT POINTS
    # Where things can be hoisted/hung from
    # -------------------------------------------------------------------------
    
    # TODO: Ceiling Attachment Points
    # ceiling_attachments = AttributeProperty(default=[])
    #
    # Example:
    # ceiling_attachments = [
    #     {"name": "beam", "capacity": 200, "occupied_by": None},
    #     {"name": "hook", "capacity": 50, "occupied_by": "#456"}
    # ]
    #
    # def get_attachment_points(self):
    #     """Return available attachment points."""
    #     pass
    #
    # def attach_to_ceiling(self, obj, attachment_name):
    #     """Attach an object to a ceiling point."""
    #     pass
    #
    # System: HOIST_SYSTEM
    
    # -------------------------------------------------------------------------
    # ACOUSTICS & ATMOSPHERE
    # -------------------------------------------------------------------------
    
    acoustics = AttributeProperty(default="normal")  # "echo", "muffled", "normal", "dead"
    
    # -------------------------------------------------------------------------
    # FUTURE: Sound System Integration
    # -------------------------------------------------------------------------
    
    # TODO: Sound Properties
    # sound_carries_to = AttributeProperty(default=[])  # Rooms that can hear this room
    # sound_dampening = AttributeProperty(default=0)  # Reduces sound transmission
    #
    # def transmit_sound(self, message, volume="normal"):
    #     """
    #     Send a sound to adjacent/connected rooms.
    #     
    #     Args:
    #         message: The sound/message
    #         volume: "whisper", "normal", "loud", "shout"
    #     
    #     System: SOUND_SYSTEM, STEALTH_SYSTEM
    #     """
    #     pass
    
    # -------------------------------------------------------------------------
    # TEMPERATURE
    # -------------------------------------------------------------------------
    
    base_temperature = AttributeProperty(default="moderate")  # "freezing", "cold", "moderate", "warm", "hot"
    
    # -------------------------------------------------------------------------
    # FUTURE: Temperature System
    # -------------------------------------------------------------------------
    
    # TODO: Dynamic Temperature
    # def calculate_temperature(self):
    #     """
    #     Calculate current temperature.
    #     
    #     Factors:
    #     - base_temperature
    #     - Heat sources in room (fireplace, etc.)
    #     - Windows + outside weather
    #     - Number of occupants
    #     
    #     System: TEMPERATURE_SYSTEM
    #     """
    #     pass
    #
    # def get_temperature_effects(self, character):
    #     """Return any effects temperature has on character."""
    #     pass
    
    # -------------------------------------------------------------------------
    # SMELL
    # -------------------------------------------------------------------------
    
    base_smell = AttributeProperty(default="")  # Ambient room smell
    
    # -------------------------------------------------------------------------
    # FUTURE: Smell System
    # -------------------------------------------------------------------------
    
    # TODO: Dynamic Smells
    # def calculate_smells(self):
    #     """
    #     Aggregate smells from room and contents.
    #     
    #     Checks:
    #     - base_smell
    #     - Smell-emitting objects
    #     - Character states (sweaty, perfumed, etc.)
    #     
    #     System: SMELL_SYSTEM
    #     """
    #     pass
    
    # =========================================================================
    # WORKING CODE - SURFACE SHORTCODE
    # =========================================================================
    
    def _get_sys_desc(self, key, looker):
        """
        Extend parent's system shortcodes with indoor-specific ones.
        """
        # Handle surface shortcodes
        if key.startswith("surface:"):
            surface_name = key.split(":")[1]
            return self._get_surface_desc(surface_name)
        
        # -------------------------------------------------------------------------
        # FUTURE: Lighting-conditional text
        # -------------------------------------------------------------------------
        
        # TODO: lit/dark conditionals
        # These might be better as separate shortcode patterns
        # if key == "lighting":
        #     return self.lighting
        #
        # System: LIGHTING_SYSTEM
        
        # Fall back to parent
        return super()._get_sys_desc(key, looker)
    
    def _get_surface_desc(self, surface_name):
        """
        Get description for a named surface.
        
        Args:
            surface_name: "ceiling", "floor", "wall", or specific like "north_wall"
            
        Returns:
            str: The surface description or empty string
        """
        if surface_name == "ceiling":
            return self.ceiling_desc or ""
        elif surface_name == "floor":
            return self.floor_desc or ""
        elif surface_name == "wall" or surface_name.endswith("_wall"):
            # Check for specific wall first in future surfaces dict
            # For now, return generic wall_desc
            return self.wall_desc or ""
        
        return ""
    
    # -------------------------------------------------------------------------
    # FUTURE: Lighting-Aware Appearance
    # -------------------------------------------------------------------------
    
    # TODO: Override return_appearance for lighting
    # def return_appearance(self, looker, **kwargs):
    #     """
    #     Modify appearance based on lighting.
    #     
    #     If dark:
    #     - Hide most details
    #     - Check if looker has light source
    #     - Show limited info
    #     
    #     System: LIGHTING_SYSTEM
    #     """
    #     # Check lighting
    #     current_light = self.calculate_lighting()
    #     looker_has_light = self._looker_has_light(looker)
    #     
    #     if current_light == "dark" and not looker_has_light:
    #         return "It's too dark to see anything."
    #     
    #     return super().return_appearance(looker, **kwargs)
