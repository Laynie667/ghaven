"""
Room Typeclasses - Foundation for Immersive Spaces

This module provides the core room system with:
- Dynamic shortcode processing
- Time-of-day awareness
- Weather integration  
- Crowd dynamics
- Ambient activity (random events that make spaces feel alive)
- Sound bleeding between adjacent rooms
- Seasonal variations
- Atmosphere presets
- Partition system for internal room divisions

The goal: Text that breathes. Rooms that feel alive without requiring
game systems to be running.

Shortcode Reference:
    Room Identity:
        <room.name>         - Room's display name
        <room.region>       - Region (e.g., "The Grove")
        <room.zone>         - Zone within region
        <room.subzone>      - Specific area within zone
        
    Time & Season:
        <time.period>       - Current period name (dawn, morning, etc.)
        <time.desc>         - Time-appropriate description chunk
        <season>            - Current season name
        <season.desc>       - Season-appropriate description chunk
        
    Weather:
        <weather>           - Current weather condition name
        <weather.desc>      - Weather-appropriate description chunk
        
    Crowd & Activity:
        <crowd.level>       - Crowd level name (empty, sparse, busy, etc.)
        <crowd.desc>        - Crowd-appropriate description chunk
        <ambient.activity>  - Random event from activity pool
        <ambient.sound>     - Ambient sounds for this room
        <ambient.scent>     - Ambient scents for this room
        
    Sensory Bleeding:
        <sound.nearby>      - Sounds bleeding from adjacent rooms
        <scent.nearby>      - Scents bleeding from adjacent rooms
        <light.source>      - Light description (for indoor rooms)
        
    Dynamic Content:
        <exits>             - Formatted exit list
        <contents>          - Visible objects/characters
        <atmosphere>        - Full atmosphere description
        
    Indoor Surfaces:
        <surface:ceiling>   - Ceiling description
        <surface:floor>     - Floor description  
        <surface:wall>      - Wall description
        <surface:walls>     - Alias for wall
        
    Outdoor Features:
        <terrain>           - Terrain type description
        <ground>            - Ground surface description
        <sky>               - Sky description (weather/time aware)
"""

from typing import Optional, Dict, Any, List, Tuple
from evennia.objects.objects import DefaultRoom
from evennia.utils.utils import lazy_property

# Handle early import during Django migration loading
try:
    from evennia.typeclasses.attributes import AttributeProperty
except (ImportError, TypeError, AttributeError):
    def AttributeProperty(default=None, **kwargs):
        return default
import random


# =============================================================================
# TIME SYSTEM
# =============================================================================

class TimeOfDay:
    """
    Simple time period tracker.
    
    In a full implementation, this would sync with a global time script.
    For now, it provides the structure and can return a default or be
    set per-room for testing.
    """
    
    PERIODS = ["dawn", "morning", "midday", "afternoon", "evening", "night", "midnight"]
    
    PERIOD_DATA = {
        "dawn": {
            "hours": (5, 7),
            "light_level": "dim",
            "default_desc": "The first light of dawn creeps across the sky.",
            "sky_desc": "The eastern sky blushes pink and gold as the sun rises.",
        },
        "morning": {
            "hours": (7, 11),
            "light_level": "bright",
            "default_desc": "Morning light fills the space with warmth.",
            "sky_desc": "The morning sun climbs steadily, promising a full day ahead.",
        },
        "midday": {
            "hours": (11, 14),
            "light_level": "bright",
            "default_desc": "The sun stands high overhead.",
            "sky_desc": "The sun blazes at its zenith, shadows pooling directly beneath.",
        },
        "afternoon": {
            "hours": (14, 17),
            "light_level": "bright",
            "default_desc": "Afternoon light slants golden through the air.",
            "sky_desc": "The afternoon sun begins its slow descent westward.",
        },
        "evening": {
            "hours": (17, 20),
            "light_level": "dim",
            "default_desc": "Evening settles in, shadows lengthening.",
            "sky_desc": "The western sky blazes with sunset colors.",
        },
        "night": {
            "hours": (20, 24),
            "light_level": "dark",
            "default_desc": "Night has fallen, darkness embracing all.",
            "sky_desc": "Stars wheel overhead in the vast darkness.",
        },
        "midnight": {
            "hours": (0, 5),
            "light_level": "dark",
            "default_desc": "The deep hours of night, when the world sleeps.",
            "sky_desc": "The moon traces its silver path through the darkness.",
        },
    }
    
    @classmethod
    def get_current_period(cls) -> str:
        """Get current time period. Override this to sync with game time."""
        # Default: return a period based on real time for testing
        # In production, this would query a global time script
        from datetime import datetime
        hour = datetime.now().hour
        
        for period, data in cls.PERIOD_DATA.items():
            start, end = data["hours"]
            if start <= hour < end:
                return period
            # Handle midnight wrap
            if period == "midnight" and (hour >= 0 and hour < 5):
                return period
        
        return "midday"  # Fallback
    
    @classmethod
    def get_period_data(cls, period: str) -> dict:
        """Get data for a specific period."""
        return cls.PERIOD_DATA.get(period, cls.PERIOD_DATA["midday"])


# =============================================================================
# WEATHER SYSTEM
# =============================================================================

class Weather:
    """
    Weather condition tracker.
    
    Like TimeOfDay, this would sync with a global weather script in
    full implementation.
    """
    
    CONDITIONS = ["clear", "cloudy", "overcast", "foggy", "drizzle", "rain", "storm", "snow"]
    
    CONDITION_DATA = {
        "clear": {
            "outdoor_desc": "The sky stretches clear and blue above.",
            "sound_mod": "",
            "visibility": "full",
            "mood": "pleasant",
        },
        "cloudy": {
            "outdoor_desc": "Scattered clouds drift lazily overhead.",
            "sound_mod": "",
            "visibility": "full",
            "mood": "neutral",
        },
        "overcast": {
            "outdoor_desc": "A grey blanket of clouds covers the sky.",
            "sound_mod": "",
            "visibility": "good",
            "mood": "somber",
        },
        "foggy": {
            "outdoor_desc": "Thick fog hangs in the air, limiting vision.",
            "sound_mod": "Sound seems muffled, absorbed by the fog.",
            "visibility": "poor",
            "mood": "mysterious",
        },
        "drizzle": {
            "outdoor_desc": "A light drizzle mists down from grey skies.",
            "sound_mod": "The soft patter of drizzle provides a gentle backdrop.",
            "visibility": "good",
            "mood": "melancholy",
        },
        "rain": {
            "outdoor_desc": "Rain falls steadily, darkening the world.",
            "sound_mod": "Rain drums against every surface.",
            "visibility": "moderate",
            "mood": "contemplative",
        },
        "storm": {
            "outdoor_desc": "A storm rages, wind and rain lashing the land.",
            "sound_mod": "Thunder rumbles and wind howls.",
            "visibility": "poor",
            "mood": "dramatic",
        },
        "snow": {
            "outdoor_desc": "Snow falls softly, blanketing the world in white.",
            "sound_mod": "The snow muffles all sound into hushed silence.",
            "visibility": "moderate",
            "mood": "peaceful",
        },
    }
    
    @classmethod
    def get_current_condition(cls) -> str:
        """Get current weather. Override to sync with game weather."""
        # Default: clear. In production, query weather script.
        return "clear"
    
    @classmethod
    def get_condition_data(cls, condition: str) -> dict:
        """Get data for a specific condition."""
        return cls.CONDITION_DATA.get(condition, cls.CONDITION_DATA["clear"])


# =============================================================================
# SEASON SYSTEM
# =============================================================================

class Season:
    """Season tracker."""
    
    SEASONS = ["spring", "summer", "autumn", "winter"]
    
    SEASON_DATA = {
        "spring": {
            "desc": "Spring's renewal touches everything with fresh growth.",
            "colors": "fresh greens and colorful blooms",
            "mood": "hopeful",
            "temperature": "mild",
        },
        "summer": {
            "desc": "Summer's warmth fills the air with lazy contentment.",
            "colors": "lush deep greens and bright flowers",
            "mood": "vibrant",
            "temperature": "warm",
        },
        "autumn": {
            "desc": "Autumn's palette paints the world in warm decay.",
            "colors": "reds, oranges, golds, and browns",
            "mood": "nostalgic",
            "temperature": "cool",
        },
        "winter": {
            "desc": "Winter's quiet grip holds the land in stillness.",
            "colors": "whites, greys, and bare branches",
            "mood": "contemplative",
            "temperature": "cold",
        },
    }
    
    @classmethod
    def get_current_season(cls) -> str:
        """Get current season. Override to sync with game calendar."""
        return "summer"  # Default
    
    @classmethod
    def get_season_data(cls, season: str) -> dict:
        """Get data for a specific season."""
        return cls.SEASON_DATA.get(season, cls.SEASON_DATA["summer"])


# =============================================================================
# CROWD SYSTEM
# =============================================================================

class CrowdLevel:
    """
    Tracks how populated a room feels.
    
    Based on actual player count + NPCs + time of day modifiers.
    """
    
    LEVELS = ["deserted", "empty", "sparse", "moderate", "busy", "crowded", "packed"]
    
    LEVEL_DATA = {
        "deserted": {
            "threshold": 0,
            "desc": "The space is utterly deserted, almost eerily so.",
            "sound_mod": "Your footsteps echo in the emptiness.",
            "mood": "lonely",
        },
        "empty": {
            "threshold": 0,
            "desc": "The area stands empty, quiet and still.",
            "sound_mod": "Silence hangs in the air.",
            "mood": "peaceful",
        },
        "sparse": {
            "threshold": 2,
            "desc": "A few scattered figures move through the space.",
            "sound_mod": "Occasional sounds break the quiet.",
            "mood": "calm",
        },
        "moderate": {
            "threshold": 5,
            "desc": "A moderate number of people go about their business.",
            "sound_mod": "The murmur of activity fills the air.",
            "mood": "comfortable",
        },
        "busy": {
            "threshold": 10,
            "desc": "The area buzzes with activity and movement.",
            "sound_mod": "Conversations overlap, creating a constant hum.",
            "mood": "energetic",
        },
        "crowded": {
            "threshold": 15,
            "desc": "Crowds press together, movement becoming difficult.",
            "sound_mod": "The noise of the crowd is almost overwhelming.",
            "mood": "intense",
        },
        "packed": {
            "threshold": 25,
            "desc": "Bodies pack the space, barely room to breathe.",
            "sound_mod": "A roar of noise surrounds you.",
            "mood": "chaotic",
        },
    }
    
    @classmethod
    def get_level_for_count(cls, count: int, time_mod: float = 1.0) -> str:
        """
        Determine crowd level based on occupant count.
        
        Args:
            count: Number of players + NPCs
            time_mod: Multiplier based on time (markets busier at midday)
        """
        effective = int(count * time_mod)
        
        # Work backwards through thresholds
        for level in reversed(cls.LEVELS):
            if effective >= cls.LEVEL_DATA[level]["threshold"]:
                return level
        
        return "empty"
    
    @classmethod
    def get_level_data(cls, level: str) -> dict:
        """Get data for a specific level."""
        return cls.LEVEL_DATA.get(level, cls.LEVEL_DATA["empty"])


# =============================================================================
# ATMOSPHERE PRESETS
# =============================================================================

ATMOSPHERE_PRESETS = {
    # Grove Areas
    "grove_default": {
        "ambient_sounds": "birdsong, rustling leaves, distant laughter",
        "ambient_scents": "flowers, fresh grass, a hint of cooking from nearby",
        "mood": "peaceful",
    },
    "grove_plaza": {
        "ambient_sounds": "fountain splashing, footsteps on stone, cheerful chatter",
        "ambient_scents": "fountain mist, food stalls, blooming flowers",
        "mood": "welcoming",
    },
    "grove_market": {
        "ambient_sounds": "merchants calling wares, coins changing hands, haggling voices",
        "ambient_scents": "spices, leather, fresh bread, exotic goods",
        "mood": "bustling",
    },
    "grove_forest": {
        "ambient_sounds": "wind through branches, birdsong, small creatures in underbrush",
        "ambient_scents": "pine, moss, wild mushrooms, leaf mold",
        "mood": "serene",
    },
    "grove_waterfront": {
        "ambient_sounds": "lapping water, creaking docks, gulls crying",
        "ambient_scents": "fresh water, fish, wet wood, water plants",
        "mood": "tranquil",
    },
    
    # Interior Types
    "tavern": {
        "ambient_sounds": "clinking glasses, laughter, crackling fire, a distant tune",
        "ambient_scents": "ale, roasting meat, pipe smoke, wood polish",
        "mood": "convivial",
    },
    "shop": {
        "ambient_sounds": "quiet browsing, the shopkeeper's movements, a bell when the door opens",
        "ambient_scents": "varies by shop type - dust and old things, or fresh goods",
        "mood": "commercial",
    },
    "library": {
        "ambient_sounds": "pages turning, quills scratching, hushed whispers",
        "ambient_scents": "old paper, leather bindings, candle wax, dust",
        "mood": "scholarly",
    },
    "temple": {
        "ambient_sounds": "soft chanting, bells, echoing footsteps",
        "ambient_scents": "incense, candle smoke, old stone",
        "mood": "reverent",
    },
    "workshop": {
        "ambient_sounds": "hammering, grinding, muttered curses, triumphant exclamations",
        "ambient_scents": "metal, oil, sawdust, sweat",
        "mood": "industrious",
    },
    
    # Underground
    "mine": {
        "ambient_sounds": "dripping water, distant pickaxes, settling stone",
        "ambient_scents": "earth, stone dust, lamp oil, stale air",
        "mood": "oppressive",
    },
    "cavern": {
        "ambient_sounds": "echoing drips, your own breathing, mysterious distant sounds",
        "ambient_scents": "wet stone, minerals, ancient air",
        "mood": "mysterious",
    },
    "crystal_cave": {
        "ambient_sounds": "crystalline chimes, harmonic resonance, pure silence between",
        "ambient_scents": "clean mineral air, a hint of ozone",
        "mood": "wondrous",
    },
    
    # Natural
    "meadow": {
        "ambient_sounds": "buzzing insects, swishing grass, distant birdsong",
        "ambient_scents": "wildflowers, warm grass, summer air",
        "mood": "idyllic",
    },
    "pond": {
        "ambient_sounds": "frogs croaking, fish splashing, dragonfly wings",
        "ambient_scents": "water lilies, mud, clean water, algae",
        "mood": "peaceful",
    },
    "beach": {
        "ambient_sounds": "waves on shore, gulls crying, wind in dune grass",
        "ambient_scents": "salt, seaweed, sun-warmed sand",
        "mood": "expansive",
    },
    "quarry": {
        "ambient_sounds": "wind across stone, occasional rockfall, tools on rock",
        "ambient_scents": "stone dust, sun-baked rock, earth",
        "mood": "exposed",
    },
    
    # Special
    "museum": {
        "ambient_sounds": "echoing footsteps, hushed conversations, preservation magic humming",
        "ambient_scents": "old wood, polish, formaldehyde, something older",
        "mood": "reverential",
    },
    "museum_basement": {
        "ambient_sounds": "dripping water, settling walls, something breathing",
        "ambient_scents": "antiseptic, old stone, anticipation",
        "mood": "clinical",
    },
    "sacred": {
        "ambient_sounds": "profound silence, your own heartbeat, whispers of the divine",
        "ambient_scents": "incense, starlight (somehow), ancient power",
        "mood": "holy",
    },
    "haunted": {
        "ambient_sounds": "creaking, whispers that might be wind, footsteps with no source",
        "ambient_scents": "dust, decay, cold despite the temperature",
        "mood": "unsettling",
    },
}


# =============================================================================
# PARTITION SYSTEM (Internal Room Divisions)
# =============================================================================

class Partition:
    """
    Represents an internal division within a room.
    
    Partitions can:
    - Block movement (walls, locked doors)
    - Block sight (curtains, walls)
    - Block sound (soundproofed areas)
    - Have their own descriptions
    - Contain doors that can be opened/closed
    """
    
    def __init__(
        self,
        name: str,
        desc: str = "",
        blocks_movement: bool = True,
        blocks_sight: bool = True,
        blocks_sound: bool = False,
        has_door: bool = False,
        door_open: bool = True,
        door_locked: bool = False,
        door_key: str = "",
    ):
        self.name = name
        self.desc = desc
        self.blocks_movement = blocks_movement
        self.blocks_sight = blocks_sight
        self.blocks_sound = blocks_sound
        self.has_door = has_door
        self.door_open = door_open
        self.door_locked = door_locked
        self.door_key = door_key
    
    def can_pass(self) -> bool:
        """Check if movement through partition is possible."""
        if not self.blocks_movement:
            return True
        if self.has_door and self.door_open:
            return True
        return False
    
    def can_see_through(self) -> bool:
        """Check if you can see through the partition."""
        if not self.blocks_sight:
            return True
        if self.has_door and self.door_open:
            return True
        return False
    
    def can_hear_through(self) -> bool:
        """Check if sound passes through."""
        if not self.blocks_sound:
            return True
        if self.has_door and self.door_open:
            return True
        return False
    
    def to_dict(self) -> dict:
        """Serialize to dict for storage."""
        return {
            "name": self.name,
            "desc": self.desc,
            "blocks_movement": self.blocks_movement,
            "blocks_sight": self.blocks_sight,
            "blocks_sound": self.blocks_sound,
            "has_door": self.has_door,
            "door_open": self.door_open,
            "door_locked": self.door_locked,
            "door_key": self.door_key,
        }
    
    @classmethod
    def from_dict(cls, data: dict) -> "Partition":
        """Deserialize from dict."""
        return cls(**data)


# =============================================================================
# BASE ROOM
# =============================================================================

class Room(DefaultRoom):
    """
    Base room with full immersion support.
    
    Features:
    - Shortcode processing for dynamic descriptions
    - Time/weather/season awareness
    - Crowd dynamics
    - Ambient activity system
    - Sound/scent bleeding from adjacent rooms
    - Atmosphere presets
    - Partition support for internal divisions
    
    Rooms should feel alive even when empty, different at dawn than
    at midnight, changed by weather, affected by who else is present.
    """
    
    # -------------------------------------------------------------------------
    # Core Identity
    # -------------------------------------------------------------------------
    
    region = AttributeProperty(default="Unknown")
    zone = AttributeProperty(default="")
    subzone = AttributeProperty(default="")
    
    # -------------------------------------------------------------------------
    # Safety Flags (for OOC areas)
    # -------------------------------------------------------------------------
    
    is_ooc_zone = AttributeProperty(default=False)
    is_safe_zone = AttributeProperty(default=False)
    allows_combat = AttributeProperty(default=True)
    allows_capture = AttributeProperty(default=True)
    
    # -------------------------------------------------------------------------
    # Atmosphere
    # -------------------------------------------------------------------------
    
    atmosphere_preset = AttributeProperty(default="")
    ambient_sounds = AttributeProperty(default="")
    ambient_scents = AttributeProperty(default="")
    mood = AttributeProperty(default="")
    
    # -------------------------------------------------------------------------
    # Time-Variant Descriptions
    # -------------------------------------------------------------------------
    
    time_descriptions = AttributeProperty(default=dict)  # {"dawn": "...", etc.}
    weather_descriptions = AttributeProperty(default=dict)  # {"rain": "...", etc.}
    season_descriptions = AttributeProperty(default=dict)  # {"spring": "...", etc.}
    crowd_descriptions = AttributeProperty(default=dict)  # {"empty": "...", etc.}
    
    # -------------------------------------------------------------------------
    # Ambient Activity
    # -------------------------------------------------------------------------
    
    activity_pool = AttributeProperty(default=list)  # List of random events
    activity_chance = AttributeProperty(default=0.3)  # Chance to show activity
    
    # -------------------------------------------------------------------------
    # Sound Bleeding
    # -------------------------------------------------------------------------
    
    sound_profile = AttributeProperty(default="")  # What this room sounds like from outside
    sound_bleed_radius = AttributeProperty(default=1)  # How far sound carries (in exits)
    sound_volume = AttributeProperty(default="moderate")  # quiet, moderate, loud
    
    # -------------------------------------------------------------------------
    # Scent Bleeding
    # -------------------------------------------------------------------------
    
    scent_profile = AttributeProperty(default="")  # What this room smells like from outside
    scent_bleed_radius = AttributeProperty(default=1)  # How far scent carries
    scent_strength = AttributeProperty(default="moderate")  # faint, moderate, strong
    
    # -------------------------------------------------------------------------
    # Crowd Modifiers
    # -------------------------------------------------------------------------
    
    base_crowd_mod = AttributeProperty(default=1.0)  # Multiplier for crowd level
    time_crowd_mods = AttributeProperty(default=dict)  # {"midday": 2.0, "night": 0.3}
    
    # -------------------------------------------------------------------------
    # Partitions
    # -------------------------------------------------------------------------
    
    partitions = AttributeProperty(default=dict)  # {name: partition_dict}
    
    # -------------------------------------------------------------------------
    # Room Hooks
    # -------------------------------------------------------------------------
    
    def at_object_creation(self):
        """Called when room is first created."""
        super().at_object_creation()
        
        # Apply atmosphere preset if set
        if self.atmosphere_preset:
            self.apply_atmosphere(self.atmosphere_preset)
    
    def apply_atmosphere(self, preset_name: str) -> bool:
        """
        Apply an atmosphere preset to this room.
        
        Args:
            preset_name: Key from ATMOSPHERE_PRESETS
            
        Returns:
            True if preset was applied, False if not found
        """
        preset = ATMOSPHERE_PRESETS.get(preset_name)
        if not preset:
            return False
        
        self.atmosphere_preset = preset_name
        self.ambient_sounds = preset.get("ambient_sounds", "")
        self.ambient_scents = preset.get("ambient_scents", "")
        self.mood = preset.get("mood", "")
        
        return True
    
    # -------------------------------------------------------------------------
    # Time/Weather/Season Getters
    # -------------------------------------------------------------------------
    
    def get_time_period(self) -> str:
        """Get current time period for this room."""
        try:
            from world.world_state import get_world_state
            return get_world_state().get_time_period()
        except:
            return TimeOfDay.get_current_period()
    
    def get_weather(self) -> str:
        """Get current weather for this room."""
        try:
            from world.world_state import get_world_state
            return get_world_state().get_weather()
        except:
            return Weather.get_current_condition()
    
    def get_season(self) -> str:
        """Get current season for this room."""
        try:
            from world.world_state import get_world_state
            return get_world_state().get_season()
        except:
            return Season.get_current_season()
    
    # -------------------------------------------------------------------------
    # Crowd Calculation
    # -------------------------------------------------------------------------
    
    def get_occupant_count(self) -> int:
        """Count players and NPCs in room."""
        count = 0
        for obj in self.contents:
            # Count players
            if hasattr(obj, 'account') and obj.account:
                count += 1
            # Count NPCs (would check for NPC typeclass)
            elif hasattr(obj, 'is_npc') and obj.is_npc:
                count += 1
        return count
    
    def get_crowd_level(self) -> str:
        """Calculate current crowd level."""
        count = self.get_occupant_count()
        
        # Apply time modifier
        time_mod = self.base_crowd_mod
        current_time = self.get_time_period()
        if current_time in self.time_crowd_mods:
            time_mod *= self.time_crowd_mods[current_time]
        
        return CrowdLevel.get_level_for_count(count, time_mod)
    
    # -------------------------------------------------------------------------
    # Sound Bleeding
    # -------------------------------------------------------------------------
    
    def get_nearby_sounds(self) -> List[str]:
        """Collect sounds bleeding from adjacent rooms."""
        sounds = []
        
        for exit in self.exits:
            if hasattr(exit, 'destination') and exit.destination:
                dest = exit.destination
                
                # Check if sound bleeds through this exit
                if hasattr(exit, 'transmits_sound') and not exit.transmits_sound:
                    continue
                
                # Get the destination's sound profile
                if hasattr(dest, 'sound_profile') and dest.sound_profile:
                    volume = getattr(dest, 'sound_volume', 'moderate')
                    
                    # Reduce based on exit type
                    reduction = getattr(exit, 'sound_reduction', 0.5)
                    
                    if volume == "loud" or reduction > 0.3:
                        direction = exit.key
                        sounds.append(f"From {direction}: {dest.sound_profile}")
        
        return sounds
    
    def get_nearby_scents(self) -> List[str]:
        """Collect scents bleeding from adjacent rooms."""
        scents = []
        
        for exit in self.exits:
            if hasattr(exit, 'destination') and exit.destination:
                dest = exit.destination
                
                # Check if scent bleeds through this exit
                if hasattr(exit, 'transmits_smell') and not exit.transmits_smell:
                    continue
                
                if hasattr(dest, 'scent_profile') and dest.scent_profile:
                    strength = getattr(dest, 'scent_strength', 'moderate')
                    
                    if strength in ("moderate", "strong"):
                        direction = exit.key
                        scents.append(f"From {direction}: {dest.scent_profile}")
        
        return scents
    
    # -------------------------------------------------------------------------
    # Ambient Activity
    # -------------------------------------------------------------------------
    
    def get_random_activity(self) -> str:
        """Get a random ambient activity event."""
        if not self.activity_pool:
            return ""
        
        if random.random() > self.activity_chance:
            return ""
        
        return random.choice(self.activity_pool)
    
    # -------------------------------------------------------------------------
    # Shortcode Processing
    # -------------------------------------------------------------------------
    
    def process_shortcodes(self, text: str, looker=None) -> str:
        """
        Process all shortcodes in text.
        
        Args:
            text: Text containing shortcodes
            looker: The character viewing the room
            
        Returns:
            Processed text with shortcodes replaced
        """
        if not text:
            return ""
        
        # --- Room Identity ---
        text = text.replace("<room.name>", self.key)
        text = text.replace("<room.region>", self.region)
        text = text.replace("<room.zone>", self.zone or "")
        text = text.replace("<room.subzone>", self.subzone or "")
        
        # --- Time ---
        current_time = self.get_time_period()
        time_data = TimeOfDay.get_period_data(current_time)
        
        text = text.replace("<time.period>", current_time)
        
        # Time description: use room-specific if available, else default
        time_desc = self.time_descriptions.get(current_time, time_data["default_desc"])
        text = text.replace("<time.desc>", time_desc)
        
        # --- Season ---
        current_season = self.get_season()
        season_data = Season.get_season_data(current_season)
        
        text = text.replace("<season>", current_season)
        
        season_desc = self.season_descriptions.get(current_season, season_data["desc"])
        text = text.replace("<season.desc>", season_desc)
        
        # --- Weather ---
        current_weather = self.get_weather()
        weather_data = Weather.get_condition_data(current_weather)
        
        text = text.replace("<weather>", current_weather)
        
        weather_desc = self.weather_descriptions.get(current_weather, weather_data.get("outdoor_desc", ""))
        text = text.replace("<weather.desc>", weather_desc)
        
        # --- Crowd ---
        crowd_level = self.get_crowd_level()
        crowd_data = CrowdLevel.get_level_data(crowd_level)
        
        text = text.replace("<crowd.level>", crowd_level)
        
        crowd_desc = self.crowd_descriptions.get(crowd_level, crowd_data["desc"])
        text = text.replace("<crowd.desc>", crowd_desc)
        
        # --- Ambient ---
        text = text.replace("<ambient.sound>", self.ambient_sounds or "")
        text = text.replace("<ambient.scent>", self.ambient_scents or "")
        text = text.replace("<ambient.sounds>", self.ambient_sounds or "")
        text = text.replace("<ambient.scents>", self.ambient_scents or "")
        
        activity = self.get_random_activity()
        text = text.replace("<ambient.activity>", activity)
        
        # --- Sound/Scent Bleeding ---
        nearby_sounds = self.get_nearby_sounds()
        text = text.replace("<sound.nearby>", " ".join(nearby_sounds) if nearby_sounds else "")
        
        nearby_scents = self.get_nearby_scents()
        text = text.replace("<scent.nearby>", " ".join(nearby_scents) if nearby_scents else "")
        
        # --- Atmosphere (combined) ---
        atmosphere_parts = []
        if self.ambient_sounds:
            atmosphere_parts.append(f"You hear {self.ambient_sounds}.")
        if self.ambient_scents:
            atmosphere_parts.append(f"The air carries the scent of {self.ambient_scents}.")
        text = text.replace("<atmosphere>", " ".join(atmosphere_parts))
        
        # --- Dynamic Content ---
        text = text.replace("<exits>", self.get_display_exits(looker))
        text = text.replace("<contents>", self.get_display_contents(looker))
        
        # --- Sky (for outdoor rooms, combines time + weather) ---
        sky_desc = self._get_sky_description()
        text = text.replace("<sky>", sky_desc)
        
        # --- Clean up any remaining empty shortcodes ---
        import re
        text = re.sub(r'<[^>]+>', '', text)
        
        # --- Clean up extra whitespace ---
        text = re.sub(r'\n\s*\n\s*\n', '\n\n', text)
        text = text.strip()
        
        return text
    
    def _get_sky_description(self) -> str:
        """Generate sky description based on time and weather."""
        time_data = TimeOfDay.get_period_data(self.get_time_period())
        weather_data = Weather.get_condition_data(self.get_weather())
        
        # If weather affects visibility, use weather desc
        if weather_data.get("visibility") in ("poor", "moderate"):
            return weather_data.get("outdoor_desc", "")
        
        # Otherwise use time-based sky
        return time_data.get("sky_desc", "")
    
    # -------------------------------------------------------------------------
    # Display Methods
    # -------------------------------------------------------------------------
    
    def get_display_exits(self, looker=None) -> str:
        """Format exits for display."""
        exits = []
        for exit in self.exits:
            # Check if exit is hidden
            if hasattr(exit, 'is_hidden') and exit.is_hidden:
                if hasattr(exit, 'discovered_by'):
                    if looker and looker not in exit.discovered_by:
                        continue
                else:
                    continue
            
            exits.append(f"|w{exit.key}|n")
        
        if not exits:
            return "There are no obvious exits."
        
        return "Exits: " + ", ".join(exits)
    
    def get_display_contents(self, looker=None) -> str:
        """Format visible contents for display."""
        things = []
        chars = []
        
        for obj in self.contents:
            # Skip exits
            if obj.destination:
                continue
            
            # Skip invisible objects
            if hasattr(obj, 'visible') and not obj.visible:
                continue
            
            # Categorize
            if hasattr(obj, 'account') or (hasattr(obj, 'is_npc') and obj.is_npc):
                if obj != looker:
                    chars.append(obj.get_display_name(looker))
            else:
                things.append(obj.get_display_name(looker))
        
        parts = []
        if chars:
            parts.append("Present: " + ", ".join(chars))
        if things:
            parts.append("You see: " + ", ".join(things))
        
        return "\n".join(parts) if parts else ""
    
    def return_appearance(self, looker=None, **kwargs):
        """
        Main appearance method. Called when someone looks at the room.
        """
        # Start with base description
        desc = self.db.desc or "You see nothing special."
        
        # Process all shortcodes
        desc = self.process_shortcodes(desc, looker)
        
        # Build full appearance
        parts = [
            f"|c{self.key}|n",  # Room name
            "",
            desc,
        ]
        
        # Add contents if not already in desc via shortcode
        if "<contents>" not in (self.db.desc or ""):
            contents = self.get_display_contents(looker)
            if contents:
                parts.append("")
                parts.append(contents)
        
        # Add exits if not already in desc via shortcode
        if "<exits>" not in (self.db.desc or ""):
            parts.append("")
            parts.append(self.get_display_exits(looker))
        
        return "\n".join(parts)
    
    # -------------------------------------------------------------------------
    # Partition Management
    # -------------------------------------------------------------------------
    
    def add_partition(self, partition: Partition) -> None:
        """Add an internal partition to the room."""
        partitions = dict(self.partitions)
        partitions[partition.name] = partition.to_dict()
        self.partitions = partitions
    
    def get_partition(self, name: str) -> Optional[Partition]:
        """Get a partition by name."""
        if name in self.partitions:
            return Partition.from_dict(self.partitions[name])
        return None
    
    def remove_partition(self, name: str) -> bool:
        """Remove a partition."""
        if name in self.partitions:
            partitions = dict(self.partitions)
            del partitions[name]
            self.partitions = partitions
            return True
        return False


# =============================================================================
# INDOOR ROOM
# =============================================================================

class IndoorRoom(Room):
    """
    An indoor/enclosed space.
    
    Additional features:
    - Lighting levels (affects visibility)
    - Surface descriptions (ceiling, floor, walls)
    - Temperature
    - Acoustics
    - Not directly affected by weather (but can reference it)
    """
    
    # -------------------------------------------------------------------------
    # Indoor Properties
    # -------------------------------------------------------------------------
    
    lighting = AttributeProperty(default="normal")  # dark, dim, normal, bright
    
    # Surfaces
    ceiling_desc = AttributeProperty(default="")
    floor_desc = AttributeProperty(default="")
    wall_desc = AttributeProperty(default="")
    
    # Environment
    temperature = AttributeProperty(default="comfortable")  # cold, cool, comfortable, warm, hot
    acoustics = AttributeProperty(default="normal")  # echoing, normal, muffled, dead
    
    # Weather protection
    weather_protected = AttributeProperty(default=True)
    can_hear_weather = AttributeProperty(default=True)  # Can you hear rain on roof?
    
    # -------------------------------------------------------------------------
    # Lighting Effects
    # -------------------------------------------------------------------------
    
    LIGHTING_EFFECTS = {
        "dark": {
            "visibility": "none",
            "desc": "Darkness engulfs everything. You can barely see your hand in front of your face.",
            "detail_mod": 0.0,  # How much detail you can see
        },
        "dim": {
            "visibility": "poor",
            "desc": "Dim light struggles to illuminate the space, leaving shadows in every corner.",
            "detail_mod": 0.5,
        },
        "normal": {
            "visibility": "full",
            "desc": "",  # No special description for normal lighting
            "detail_mod": 1.0,
        },
        "bright": {
            "visibility": "full",
            "desc": "Bright light fills every corner, leaving no shadow unexplored.",
            "detail_mod": 1.0,
        },
    }
    
    def get_lighting_effect(self) -> dict:
        """Get current lighting effect data."""
        return self.LIGHTING_EFFECTS.get(self.lighting, self.LIGHTING_EFFECTS["normal"])
    
    # -------------------------------------------------------------------------
    # Shortcode Processing Override
    # -------------------------------------------------------------------------
    
    def process_shortcodes(self, text: str, looker=None) -> str:
        """Process indoor-specific shortcodes."""
        # Parent processing first
        text = super().process_shortcodes(text, looker)
        
        # --- Surfaces ---
        text = text.replace("<surface:ceiling>", self.ceiling_desc or "a plain ceiling")
        text = text.replace("<surface:floor>", self.floor_desc or "a plain floor")
        text = text.replace("<surface:wall>", self.wall_desc or "plain walls")
        text = text.replace("<surface:walls>", self.wall_desc or "plain walls")
        
        # --- Lighting ---
        lighting_effect = self.get_lighting_effect()
        text = text.replace("<light.level>", self.lighting)
        text = text.replace("<light.desc>", lighting_effect.get("desc", ""))
        
        # Light source (would be determined by objects in room)
        text = text.replace("<light.source>", self._get_light_source_desc())
        
        # --- Temperature ---
        text = text.replace("<temperature>", self.temperature)
        
        # --- Weather sounds (muffled if indoors) ---
        if self.can_hear_weather:
            weather = self.get_weather()
            weather_sound = self._get_indoor_weather_sound(weather)
            text = text.replace("<weather.sound>", weather_sound)
        else:
            text = text.replace("<weather.sound>", "")
        
        return text
    
    def _get_light_source_desc(self) -> str:
        """Determine what's providing light."""
        # Would check for light sources in room
        # For now, return based on lighting level
        sources = {
            "dark": "There is no light source here.",
            "dim": "Faint light filters in from somewhere.",
            "normal": "The space is adequately lit.",
            "bright": "Bright light illuminates every corner.",
        }
        return sources.get(self.lighting, "")
    
    def _get_indoor_weather_sound(self, weather: str) -> str:
        """Get muffled weather sounds heard from inside."""
        sounds = {
            "clear": "",
            "cloudy": "",
            "overcast": "",
            "foggy": "",
            "drizzle": "The soft patter of drizzle sounds against the roof.",
            "rain": "Rain drums steadily on the roof above.",
            "storm": "Thunder rumbles outside and rain hammers the walls.",
            "snow": "A soft hush from the snow falling outside.",
        }
        return sounds.get(weather, "")
    
    # -------------------------------------------------------------------------
    # Visibility in Dark Rooms
    # -------------------------------------------------------------------------
    
    def return_appearance(self, looker=None, **kwargs):
        """Handle dark room visibility."""
        lighting = self.get_lighting_effect()
        
        # If dark and looker can't see in dark
        if lighting["visibility"] == "none":
            can_see_dark = False
            if looker and hasattr(looker, 'can_see_in_dark'):
                can_see_dark = looker.can_see_in_dark
            
            if not can_see_dark:
                return f"|c{self.key}|n\n\n{lighting['desc']}\n\n{self.get_display_exits(looker)}"
        
        return super().return_appearance(looker, **kwargs)


# =============================================================================
# OUTDOOR ROOM
# =============================================================================

class OutdoorRoom(Room):
    """
    An outdoor/open-air space.
    
    Additional features:
    - Full weather effects
    - Terrain type
    - Ground and sky descriptions
    - Time directly affects appearance
    - Visibility affected by weather
    """
    
    # -------------------------------------------------------------------------
    # Outdoor Properties
    # -------------------------------------------------------------------------
    
    terrain = AttributeProperty(default="ground")  # grass, forest, water, mountain, etc.
    ground_desc = AttributeProperty(default="")
    sky_desc_override = AttributeProperty(default="")  # Override for specific sky description
    
    # Weather effects
    weather_shelter = AttributeProperty(default=0.0)  # 0-1, how much shelter from weather
    
    # Time effects
    time_affects_desc = AttributeProperty(default=True)  # Does time change description?
    
    # -------------------------------------------------------------------------
    # Terrain Data
    # -------------------------------------------------------------------------
    
    TERRAIN_DATA = {
        "grass": {
            "desc": "soft grass",
            "footstep": "Your feet sink slightly into the soft grass.",
            "wet_mod": "The grass squelches wetly underfoot.",
        },
        "forest": {
            "desc": "forest floor covered in leaves and needles",
            "footstep": "Leaves crunch beneath your feet.",
            "wet_mod": "Wet leaves stick to your boots.",
        },
        "dirt": {
            "desc": "packed dirt",
            "footstep": "Your feet raise small puffs of dust.",
            "wet_mod": "The dirt has turned to mud.",
        },
        "stone": {
            "desc": "solid stone",
            "footstep": "Your footsteps echo off the stone.",
            "wet_mod": "The wet stone is slick underfoot.",
        },
        "sand": {
            "desc": "loose sand",
            "footstep": "Sand shifts beneath your feet.",
            "wet_mod": "The wet sand is firmer underfoot.",
        },
        "water_shallow": {
            "desc": "shallow water",
            "footstep": "Water splashes around your ankles.",
            "wet_mod": "",  # Already wet
        },
        "snow": {
            "desc": "pristine snow",
            "footstep": "Snow crunches beneath each step.",
            "wet_mod": "The snow has turned to slush.",
        },
    }
    
    def get_terrain_data(self) -> dict:
        """Get data for current terrain."""
        return self.TERRAIN_DATA.get(self.terrain, self.TERRAIN_DATA["grass"])
    
    # -------------------------------------------------------------------------
    # Shortcode Processing Override
    # -------------------------------------------------------------------------
    
    def process_shortcodes(self, text: str, looker=None) -> str:
        """Process outdoor-specific shortcodes."""
        # Parent processing first
        text = super().process_shortcodes(text, looker)
        
        # --- Terrain ---
        terrain_data = self.get_terrain_data()
        text = text.replace("<terrain>", terrain_data.get("desc", self.terrain))
        
        # Ground description (terrain + weather mod)
        ground = self.ground_desc or terrain_data.get("desc", "the ground")
        weather = self.get_weather()
        if weather in ("rain", "storm", "drizzle"):
            wet_mod = terrain_data.get("wet_mod", "")
            if wet_mod:
                ground = f"{ground}. {wet_mod}"
        text = text.replace("<ground>", ground)
        
        # --- Sky override ---
        if self.sky_desc_override:
            text = text.replace("<sky>", self.sky_desc_override)
        # Parent handles <sky> with time/weather combo
        
        # --- Footstep flavor (could be used in movement messages) ---
        text = text.replace("<footstep>", terrain_data.get("footstep", ""))
        
        return text


# =============================================================================
# EXPORTS
# =============================================================================

__all__ = [
    # Systems
    "TimeOfDay",
    "Weather",
    "Season",
    "CrowdLevel",
    "Partition",
    "ATMOSPHERE_PRESETS",
    
    # Room Types
    "Room",
    "IndoorRoom",
    "OutdoorRoom",
]
