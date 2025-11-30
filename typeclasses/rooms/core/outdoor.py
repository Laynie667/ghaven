"""
Room - Outdoor

Outdoor room type with terrain, weather, sky, and time-of-day properties.
"""

from evennia import AttributeProperty
from .base import Room


class OutdoorRoom(Room):
    """
    Outdoor room - open spaces affected by weather and time.
    
    Adds:
        - Terrain properties (type, difficulty, movement cost)
        - Weather awareness (affected by global weather system)
        - Time-of-day awareness (sky, lighting changes)
        - Elevation (affects weather, temperature, visibility)
        - Natural hazards
    
    Shortcodes added:
        <sys:weather>  - current weather description
        <sys:sky>      - sky description based on time/weather
        <sys:time>     - time of day description
        <sys:terrain>  - terrain description
    """
    
    # -------------------------------------------------------------------------
    # TERRAIN SYSTEM
    # -------------------------------------------------------------------------
    
    terrain = AttributeProperty(default="grass")  # "grass", "sand", "rock", "snow", "mud", "water"
    terrain_desc = AttributeProperty(default="")  # Detailed terrain description
    
    # -------------------------------------------------------------------------
    # FUTURE: Terrain Effects
    # -------------------------------------------------------------------------
    
    # TODO: Movement & Difficulty
    # terrain_difficulty = AttributeProperty(default="normal")  # "easy", "normal", "rough", "climbing", "swimming"
    # movement_cost = AttributeProperty(default=1)  # Stamina/effort multiplier
    # requires_skill = AttributeProperty(default="")  # "climb", "swim", etc.
    # skill_difficulty = AttributeProperty(default=0)  # DC for skill check
    #
    # def check_terrain_traversal(self, character):
    #     """
    #     Check if character can traverse this terrain.
    #     
    #     Returns:
    #         tuple: (can_traverse: bool, message: str)
    #     
    #     System: MOVEMENT_SYSTEM, SKILL_SYSTEM
    #     """
    #     pass
    #
    # def get_movement_cost(self, character):
    #     """Calculate movement cost for this character."""
    #     pass
    
    # -------------------------------------------------------------------------
    # WEATHER SYSTEM
    # -------------------------------------------------------------------------
    
    weather_affected = AttributeProperty(default=True)  # Does weather apply here?
    
    # -------------------------------------------------------------------------
    # FUTURE: Weather Integration
    # -------------------------------------------------------------------------
    
    # TODO: Weather System Hooks
    # current_weather = None  # Pulled from global weather system, not stored
    # weather_shelter = AttributeProperty(default=0.0)  # 0 = fully exposed, 1 = fully sheltered
    # weather_modifiers = AttributeProperty(default={})  # Local weather tweaks
    #
    # def get_current_weather(self):
    #     """
    #     Get weather for this room.
    #     
    #     Checks:
    #     - Global weather system for region
    #     - Local modifiers (shelter, elevation, etc.)
    #     
    #     Returns:
    #         dict: Weather data including type, intensity, description
    #     
    #     System: WEATHER_SYSTEM
    #     """
    #     pass
    #
    # def get_weather_effects(self, character):
    #     """
    #     Get weather effects on a character.
    #     
    #     Effects might include:
    #     - Visibility reduction
    #     - Movement speed changes
    #     - Damage (extreme weather)
    #     - Skill modifiers
    #     
    #     System: WEATHER_SYSTEM
    #     """
    #     pass
    
    # -------------------------------------------------------------------------
    # TIME OF DAY SYSTEM
    # -------------------------------------------------------------------------
    
    time_affected = AttributeProperty(default=True)  # Does time of day matter?
    sky_visible = AttributeProperty(default=True)  # Can see the sky? (False in dense forest)
    
    # -------------------------------------------------------------------------
    # FUTURE: Time System Integration
    # -------------------------------------------------------------------------
    
    # TODO: Time-Based Changes
    # def get_time_period(self):
    #     """
    #     Get current time period.
    #     
    #     Returns:
    #         str: "dawn", "morning", "noon", "afternoon", "dusk", "evening", "night", "midnight"
    #     
    #     System: TIME_SYSTEM
    #     """
    #     pass
    #
    # def get_sky_desc(self):
    #     """
    #     Get sky description based on time and weather.
    #     
    #     System: TIME_SYSTEM, WEATHER_SYSTEM
    #     """
    #     pass
    #
    # def get_natural_light(self):
    #     """
    #     Calculate natural light level.
    #     
    #     Factors:
    #     - Time of day
    #     - Weather (clouds reduce light)
    #     - sky_visible (canopy blocks light)
    #     
    #     Returns:
    #         str: "dark", "dim", "normal", "bright"
    #     
    #     System: TIME_SYSTEM, LIGHTING_SYSTEM
    #     """
    #     pass
    
    # -------------------------------------------------------------------------
    # ELEVATION
    # -------------------------------------------------------------------------
    
    elevation = AttributeProperty(default=0)  # Height level (sea level = 0)
    
    # -------------------------------------------------------------------------
    # FUTURE: Elevation Effects
    # -------------------------------------------------------------------------
    
    # TODO: Altitude Effects
    # def get_elevation_effects(self):
    #     """
    #     Effects based on elevation.
    #     
    #     High elevation:
    #     - Colder temperature
    #     - Thinner air (stamina effects)
    #     - Different weather patterns
    #     - Greater visibility range
    #     
    #     System: ELEVATION_SYSTEM, TEMPERATURE_SYSTEM
    #     """
    #     pass
    
    # -------------------------------------------------------------------------
    # TEMPERATURE
    # -------------------------------------------------------------------------
    
    base_temperature = AttributeProperty(default="moderate")  # Baseline before weather/time
    
    # -------------------------------------------------------------------------
    # FUTURE: Outdoor Temperature
    # -------------------------------------------------------------------------
    
    # TODO: Dynamic Temperature
    # def calculate_temperature(self):
    #     """
    #     Calculate current outdoor temperature.
    #     
    #     Factors:
    #     - base_temperature
    #     - Time of day (cooler at night)
    #     - Weather (rain cools, sun heats)
    #     - Elevation (higher = colder)
    #     - Season
    #     
    #     System: TEMPERATURE_SYSTEM
    #     """
    #     pass
    
    # -------------------------------------------------------------------------
    # NATURAL HAZARDS
    # -------------------------------------------------------------------------
    
    # -------------------------------------------------------------------------
    # FUTURE: Environmental Hazards
    # -------------------------------------------------------------------------
    
    # TODO: Natural Hazards
    # natural_hazards = AttributeProperty(default=[])
    #
    # Example hazards:
    # - "quicksand" - chance to get stuck
    # - "thorns" - damage when moving
    # - "cliffs" - fall danger
    # - "wildlife" - random encounter chance
    # - "poisonous_plants" - damage on contact
    #
    # def check_hazards(self, character, action):
    #     """
    #     Check if any hazards trigger.
    #     
    #     Args:
    #         character: Who's at risk
    #         action: What they're doing ("enter", "move", "rest", etc.)
    #     
    #     System: HAZARD_SYSTEM
    #     """
    #     pass
    
    # -------------------------------------------------------------------------
    # WILDLIFE/ENCOUNTERS
    # -------------------------------------------------------------------------
    
    # TODO: Random Encounter System
    # encounter_table = AttributeProperty(default=[])
    # encounter_chance = AttributeProperty(default=0.0)  # Chance per interval
    #
    # Example:
    # encounter_table = [
    #     {"type": "wolf", "weight": 10, "time": ["night", "dusk"]},
    #     {"type": "deer", "weight": 30, "time": ["dawn", "morning"]},
    #     {"type": "bandit", "weight": 5, "conditions": ["road"]}
    # ]
    #
    # def roll_encounter(self):
    #     """
    #     Check for random encounter.
    #     
    #     System: ENCOUNTER_SYSTEM
    #     """
    #     pass
    
    # -------------------------------------------------------------------------
    # TRACKS/SIGNS
    # -------------------------------------------------------------------------
    
    # TODO: Tracking System
    # tracks = AttributeProperty(default=[])
    #
    # Tracks left by creatures/characters passing through
    # tracks = [
    #     {"type": "boot", "direction": "north", "age": 3600, "character": "#123"},
    #     {"type": "wolf", "direction": "east", "age": 7200}
    # ]
    #
    # def add_tracks(self, character, direction):
    #     """Add tracks when someone passes through."""
    #     pass
    #
    # def read_tracks(self, character):
    #     """Character attempts to read tracks (skill check)."""
    #     pass
    #
    # def age_tracks(self):
    #     """Called periodically to age/remove old tracks."""
    #     pass
    #
    # System: TRACKING_SYSTEM
    
    # -------------------------------------------------------------------------
    # FORAGING/RESOURCES
    # -------------------------------------------------------------------------
    
    # TODO: Resource System
    # resources = AttributeProperty(default={})
    #
    # Example:
    # resources = {
    #     "herbs": {"available": 5, "respawn_time": 3600, "skill": "herbalism"},
    #     "water": {"available": -1, "skill": None},  # -1 = unlimited
    #     "wood": {"available": 10, "respawn_time": 86400}
    # }
    #
    # def gather_resource(self, character, resource_type):
    #     """Character attempts to gather a resource."""
    #     pass
    #
    # def respawn_resources(self):
    #     """Called periodically to respawn gathered resources."""
    #     pass
    #
    # System: RESOURCE_SYSTEM
    
    # =========================================================================
    # WORKING CODE - OUTDOOR SHORTCODES
    # =========================================================================
    
    def _get_sys_desc(self, key, looker):
        """
        Extend parent's system shortcodes with outdoor-specific ones.
        """
        
        # Terrain shortcode
        if key == "terrain":
            return self.terrain_desc or self.terrain or ""
        
        # -------------------------------------------------------------------------
        # FUTURE: Weather shortcode
        # -------------------------------------------------------------------------
        
        # TODO: Weather Integration
        # if key == "weather":
        #     if not self.weather_affected:
        #         return ""
        #     weather_data = self.get_current_weather()
        #     return weather_data.get("description", "")
        #
        # System: WEATHER_SYSTEM
        
        # -------------------------------------------------------------------------
        # FUTURE: Sky shortcode
        # -------------------------------------------------------------------------
        
        # TODO: Sky/Time Integration
        # if key == "sky":
        #     if not self.sky_visible:
        #         return ""
        #     return self.get_sky_desc()
        #
        # System: TIME_SYSTEM
        
        # -------------------------------------------------------------------------
        # FUTURE: Time shortcode
        # -------------------------------------------------------------------------
        
        # TODO: Time Period
        # if key == "time":
        #     if not self.time_affected:
        #         return ""
        #     return self.get_time_period()
        #
        # System: TIME_SYSTEM
        
        # Fall back to parent
        return super()._get_sys_desc(key, looker)
    
    # -------------------------------------------------------------------------
    # FUTURE: Time/Weather Aware Appearance
    # -------------------------------------------------------------------------
    
    # TODO: Override return_appearance
    # def return_appearance(self, looker, **kwargs):
    #     """
    #     Modify appearance based on time and weather.
    #     
    #     - Dark nights with no moon = limited visibility
    #     - Fog = reduced detail
    #     - Storms = different mood
    #     
    #     System: TIME_SYSTEM, WEATHER_SYSTEM
    #     """
    #     pass
