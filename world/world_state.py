"""
World State System - Time, Weather, Seasons

A global system that tracks the state of the world:
- Time of day (6 periods: dawn, morning, midday, afternoon, evening, night)
- Weather (various conditions that change organically)
- Season (spring, summer, autumn, winter)

Rooms query this system to get current conditions for their descriptions.

USAGE:
    # Get the world state (creates if doesn't exist)
    from world.world_state import get_world_state
    state = get_world_state()
    
    # Query current conditions
    time = state.get_time_period()        # "afternoon"
    weather = state.get_weather()          # "clear"
    season = state.get_season()            # "summer"
    
    # In rooms:
    def get_time_period(self):
        return get_world_state().get_time_period()

CONFIGURATION:
    The world state can run in two modes:
    - Static: Values set manually, don't change automatically
    - Dynamic: Values change on timers (for actual gameplay)
"""

import random
from typing import Optional, Dict, List, Tuple
from datetime import datetime, timedelta
from evennia.scripts.scripts import DefaultScript
from evennia.utils.create import create_script

# Handle early import during Django migration loading
try:
    from evennia.typeclasses.attributes import AttributeProperty
except (ImportError, TypeError, AttributeError):
    def AttributeProperty(default=None, **kwargs):
        return default


# =============================================================================
# CONSTANTS
# =============================================================================

TIME_PERIODS = ["dawn", "morning", "midday", "afternoon", "evening", "night"]

# How many real minutes per game time period (in dynamic mode)
# Default: 20 real minutes = 1 game time period
# Full day = 2 hours real time
MINUTES_PER_PERIOD = 20

WEATHER_CONDITIONS = ["clear", "cloudy", "overcast", "rain", "heavy_rain", "storm", "fog", "snow"]

# Weather transition weights (what weather tends to follow what)
WEATHER_TRANSITIONS = {
    "clear": {"clear": 60, "cloudy": 30, "fog": 10},
    "cloudy": {"clear": 30, "cloudy": 40, "overcast": 20, "rain": 10},
    "overcast": {"cloudy": 20, "overcast": 40, "rain": 30, "heavy_rain": 10},
    "rain": {"rain": 40, "overcast": 30, "heavy_rain": 20, "clear": 10},
    "heavy_rain": {"heavy_rain": 30, "rain": 40, "storm": 20, "overcast": 10},
    "storm": {"storm": 20, "heavy_rain": 50, "rain": 30},
    "fog": {"fog": 40, "clear": 40, "cloudy": 20},
    "snow": {"snow": 50, "overcast": 30, "clear": 20},
}

# Weather by season (what weather is possible in each season)
SEASONAL_WEATHER = {
    "spring": ["clear", "cloudy", "overcast", "rain", "fog"],
    "summer": ["clear", "cloudy", "rain", "heavy_rain", "storm"],
    "autumn": ["clear", "cloudy", "overcast", "rain", "fog"],
    "winter": ["clear", "cloudy", "overcast", "snow", "fog"],
}

SEASONS = ["spring", "summer", "autumn", "winter"]

# Real-world days per game season (in dynamic mode)
DAYS_PER_SEASON = 7


# =============================================================================
# WORLD STATE SCRIPT
# =============================================================================

class WorldState(DefaultScript):
    """
    Global world state tracker.
    
    This script tracks time, weather, and season for the entire game world.
    It can run in static mode (manual updates) or dynamic mode (automatic
    progression based on real time).
    """
    
    # =========================================================================
    # MODE
    # =========================================================================
    
    # Static = manual updates only, Dynamic = auto progression
    mode = AttributeProperty(default="static")
    
    # =========================================================================
    # TIME
    # =========================================================================
    
    current_time_index = AttributeProperty(default=3)  # afternoon
    last_time_update = AttributeProperty(default=None)
    
    # =========================================================================
    # WEATHER
    # =========================================================================
    
    current_weather = AttributeProperty(default="clear")
    last_weather_change = AttributeProperty(default=None)
    weather_duration = AttributeProperty(default=3)  # How many time periods this weather lasts
    weather_remaining = AttributeProperty(default=3)
    
    # =========================================================================
    # SEASON
    # =========================================================================
    
    current_season_index = AttributeProperty(default=1)  # summer
    season_day = AttributeProperty(default=1)  # Day within the season
    last_season_update = AttributeProperty(default=None)
    
    # =========================================================================
    # INITIALIZATION
    # =========================================================================
    
    def at_script_creation(self):
        """Set up the world state."""
        self.key = "world_state"
        self.desc = "Global world state tracker"
        self.persistent = True
        
        # Set initial state
        self.current_time_index = 3  # Afternoon
        self.current_weather = "clear"
        self.current_season_index = 1  # Summer
        
        # Track when we last updated
        now = datetime.now()
        self.last_time_update = now.isoformat()
        self.last_weather_change = now.isoformat()
        self.last_season_update = now.isoformat()
    
    # =========================================================================
    # GETTERS
    # =========================================================================
    
    def get_time_period(self) -> str:
        """Get current time period name."""
        if self.mode == "dynamic":
            self._update_time()
        return TIME_PERIODS[self.current_time_index]
    
    def get_time_index(self) -> int:
        """Get current time period index."""
        if self.mode == "dynamic":
            self._update_time()
        return self.current_time_index
    
    def get_weather(self) -> str:
        """Get current weather condition."""
        if self.mode == "dynamic":
            self._update_weather()
        return self.current_weather
    
    def get_season(self) -> str:
        """Get current season name."""
        if self.mode == "dynamic":
            self._update_season()
        return SEASONS[self.current_season_index]
    
    def get_season_index(self) -> int:
        """Get current season index."""
        if self.mode == "dynamic":
            self._update_season()
        return self.current_season_index
    
    def get_season_day(self) -> int:
        """Get current day within the season."""
        return self.season_day
    
    def get_full_state(self) -> Dict:
        """Get complete world state."""
        return {
            "time": self.get_time_period(),
            "time_index": self.get_time_index(),
            "weather": self.get_weather(),
            "season": self.get_season(),
            "season_index": self.get_season_index(),
            "season_day": self.get_season_day(),
            "mode": self.mode,
        }
    
    # =========================================================================
    # SETTERS (for static mode or admin overrides)
    # =========================================================================
    
    def set_time_period(self, period: str) -> bool:
        """Manually set time period."""
        if period in TIME_PERIODS:
            self.current_time_index = TIME_PERIODS.index(period)
            self.last_time_update = datetime.now().isoformat()
            return True
        return False
    
    def set_weather(self, weather: str) -> bool:
        """Manually set weather."""
        if weather in WEATHER_CONDITIONS:
            self.current_weather = weather
            self.last_weather_change = datetime.now().isoformat()
            self.weather_remaining = self.weather_duration
            return True
        return False
    
    def set_season(self, season: str) -> bool:
        """Manually set season."""
        if season in SEASONS:
            self.current_season_index = SEASONS.index(season)
            self.season_day = 1
            self.last_season_update = datetime.now().isoformat()
            return True
        return False
    
    def set_mode(self, mode: str) -> bool:
        """Set operation mode."""
        if mode in ("static", "dynamic"):
            self.mode = mode
            return True
        return False
    
    # =========================================================================
    # ADVANCEMENT (for static mode - call these to progress time)
    # =========================================================================
    
    def advance_time(self) -> str:
        """Advance to next time period. Returns new period name."""
        self.current_time_index = (self.current_time_index + 1) % len(TIME_PERIODS)
        self.last_time_update = datetime.now().isoformat()
        
        # Check weather progression
        self.weather_remaining -= 1
        if self.weather_remaining <= 0:
            self._change_weather()
        
        # Check for new day (when it becomes dawn)
        if self.current_time_index == 0:
            self._new_day()
        
        return self.get_time_period()
    
    def _new_day(self):
        """Handle start of new day."""
        self.season_day += 1
        
        # Check for season change
        if self.season_day > DAYS_PER_SEASON:
            self.season_day = 1
            self.current_season_index = (self.current_season_index + 1) % len(SEASONS)
            self.last_season_update = datetime.now().isoformat()
    
    # =========================================================================
    # DYNAMIC UPDATES
    # =========================================================================
    
    def _update_time(self):
        """Update time based on real elapsed time (dynamic mode)."""
        if not self.last_time_update:
            return
        
        try:
            last_update = datetime.fromisoformat(self.last_time_update)
        except:
            last_update = datetime.now()
        
        now = datetime.now()
        elapsed = now - last_update
        minutes_elapsed = elapsed.total_seconds() / 60
        
        # How many time periods have passed?
        periods_elapsed = int(minutes_elapsed / MINUTES_PER_PERIOD)
        
        if periods_elapsed > 0:
            for _ in range(periods_elapsed):
                self.advance_time()
            self.last_time_update = now.isoformat()
    
    def _update_weather(self):
        """Update weather if needed (called from get_weather in dynamic mode)."""
        # Weather updates happen in advance_time
        pass
    
    def _update_season(self):
        """Update season if needed (called from get_season in dynamic mode)."""
        # Season updates happen in _new_day
        pass
    
    # =========================================================================
    # WEATHER SYSTEM
    # =========================================================================
    
    def _change_weather(self):
        """Change to new weather based on transitions and season."""
        current = self.current_weather
        season = SEASONS[self.current_season_index]
        
        # Get possible next weather states
        transitions = WEATHER_TRANSITIONS.get(current, {"clear": 100})
        
        # Filter by season
        seasonal = SEASONAL_WEATHER.get(season, WEATHER_CONDITIONS)
        valid_transitions = {k: v for k, v in transitions.items() if k in seasonal}
        
        if not valid_transitions:
            valid_transitions = {"clear": 100}
        
        # Weighted random choice
        total = sum(valid_transitions.values())
        roll = random.randint(1, total)
        
        cumulative = 0
        for weather, weight in valid_transitions.items():
            cumulative += weight
            if roll <= cumulative:
                self.current_weather = weather
                break
        
        # Set duration (random within range)
        self.weather_duration = random.randint(2, 5)
        self.weather_remaining = self.weather_duration
        self.last_weather_change = datetime.now().isoformat()
    
    # =========================================================================
    # UTILITY
    # =========================================================================
    
    def is_daytime(self) -> bool:
        """Check if it's currently daytime."""
        return self.current_time_index in [1, 2, 3]  # morning, midday, afternoon
    
    def is_nighttime(self) -> bool:
        """Check if it's currently nighttime."""
        return self.current_time_index in [5]  # night
    
    def is_transition(self) -> bool:
        """Check if it's dawn or evening."""
        return self.current_time_index in [0, 4]  # dawn, evening
    
    def weather_is_bad(self) -> bool:
        """Check if weather is poor."""
        return self.current_weather in ["rain", "heavy_rain", "storm", "snow"]
    
    def visibility_modifier(self) -> float:
        """Get visibility modifier (1.0 = full, lower = reduced)."""
        weather_mod = {
            "clear": 1.0,
            "cloudy": 1.0,
            "overcast": 0.9,
            "rain": 0.7,
            "heavy_rain": 0.5,
            "storm": 0.3,
            "fog": 0.2,
            "snow": 0.6,
        }.get(self.current_weather, 1.0)
        
        time_mod = {
            "dawn": 0.7,
            "morning": 1.0,
            "midday": 1.0,
            "afternoon": 1.0,
            "evening": 0.7,
            "night": 0.3,
        }.get(TIME_PERIODS[self.current_time_index], 1.0)
        
        return weather_mod * time_mod
    
    def get_ambient_modifier(self) -> Dict:
        """Get modifiers for ambient systems (sound, spawn rates, etc.)."""
        return {
            "visibility": self.visibility_modifier(),
            "sound_range": 1.0 if self.current_weather != "storm" else 0.5,
            "spawn_rate": 1.0 if not self.weather_is_bad() else 0.7,
            "npc_activity": 1.0 if self.is_daytime() else 0.3,
        }


# =============================================================================
# SINGLETON ACCESS
# =============================================================================

_world_state_cache = None


def get_world_state() -> WorldState:
    """
    Get the global world state script.
    
    Creates the script if it doesn't exist.
    Caches the reference for performance.
    """
    global _world_state_cache
    
    if _world_state_cache and _world_state_cache.pk:
        return _world_state_cache
    
    # Try to find existing
    from evennia import search_script
    scripts = search_script("world_state")
    
    if scripts:
        _world_state_cache = scripts[0]
        return _world_state_cache
    
    # Create new
    _world_state_cache = create_script(
        WorldState,
        key="world_state",
        persistent=True,
        autostart=True,
    )
    
    return _world_state_cache


def set_time(period: str) -> bool:
    """Convenience function to set time."""
    return get_world_state().set_time_period(period)


def set_weather(condition: str) -> bool:
    """Convenience function to set weather."""
    return get_world_state().set_weather(condition)


def set_season(season: str) -> bool:
    """Convenience function to set season."""
    return get_world_state().set_season(season)


def advance_time() -> str:
    """Convenience function to advance time."""
    return get_world_state().advance_time()


def get_state() -> Dict:
    """Convenience function to get full state."""
    return get_world_state().get_full_state()


# =============================================================================
# ROOM INTEGRATION
# =============================================================================

def connect_room_to_world_state(room):
    """
    Monkey-patch a room to use the world state.
    
    Call this on rooms to make their time/weather/season methods
    return actual world state values.
    
    Usage:
        from world.world_state import connect_room_to_world_state
        connect_room_to_world_state(my_room)
    """
    def get_time_period(self):
        return get_world_state().get_time_period()
    
    def get_weather(self):
        return get_world_state().get_weather()
    
    def get_season(self):
        return get_world_state().get_season()
    
    room.get_time_period = lambda: get_time_period(room)
    room.get_weather = lambda: get_weather(room)
    room.get_season = lambda: get_season(room)


# =============================================================================
# EXPORTS
# =============================================================================

__all__ = [
    "WorldState",
    "get_world_state",
    "set_time",
    "set_weather", 
    "set_season",
    "advance_time",
    "get_state",
    "connect_room_to_world_state",
    "TIME_PERIODS",
    "WEATHER_CONDITIONS",
    "SEASONS",
]
