"""
Time and Weather System for Gilderhaven
=========================================

Game time tracking with:
- Configurable time scale (default: 1 real hour = 1 game day)
- Time periods (dawn, morning, afternoon, evening, night, midnight)
- Days, weeks, months, seasons, years
- Weather conditions per-area
- NPC schedule integration
- Time-gated content hooks

Architecture:
- Single TimeManager script tracks global time
- Rooms can have area-specific weather
- NPCs check schedules via hooks
- Events can be time-triggered

Usage:
    from world.time_weather import (
        get_time, get_period, get_weather, get_season,
        is_daytime, is_night, advance_time
    )
    
    # Check current time
    period = get_period()  # "morning", "night", etc.
    
    # Check weather in a room
    weather = get_weather(room)  # "clear", "rain", etc.
    
    # Time-gated content
    if is_night():
        spawn_dangerous_encounter()
"""

import time
import random
from evennia import DefaultScript, search_object
from evennia.utils import logger


# =============================================================================
# TIME CONFIGURATION
# =============================================================================

# How many real seconds = 1 game hour
# Default: 150 seconds (2.5 min) = 1 hour, so 1 hour real = 1 day game
SECONDS_PER_GAME_HOUR = 150

# Time periods
TIME_PERIODS = {
    "midnight": (0, 3),      # 00:00 - 02:59
    "late_night": (3, 5),    # 03:00 - 04:59
    "dawn": (5, 7),          # 05:00 - 06:59
    "morning": (7, 12),      # 07:00 - 11:59
    "afternoon": (12, 17),   # 12:00 - 16:59
    "evening": (17, 20),     # 17:00 - 19:59
    "night": (20, 24),       # 20:00 - 23:59
}

# Period descriptions
PERIOD_DESCRIPTIONS = {
    "midnight": "The deep of night, when shadows hold sway.",
    "late_night": "The darkest hours before dawn.",
    "dawn": "The sky lightens as a new day begins.",
    "morning": "The sun climbs higher, bringing warmth and light.",
    "afternoon": "The sun hangs high overhead.",
    "evening": "Golden light paints the world as the sun descends.",
    "night": "Stars emerge as darkness settles over the land.",
}

# Days of the week
DAYS_OF_WEEK = [
    "Moonday",
    "Treeday",
    "Waterday",
    "Stoneday",
    "Fireday",
    "Starday",
    "Sunday",
]

# Months (13 months of 28 days = 364 days + 1 festival day)
MONTHS = [
    ("Deepwinter", "winter"),
    ("Thawmoon", "winter"),
    ("Springseed", "spring"),
    ("Rainmoon", "spring"),
    ("Blossomtide", "spring"),
    ("Summerpeak", "summer"),
    ("Sunhigh", "summer"),
    ("Goldenharvest", "summer"),
    ("Harvestend", "autumn"),
    ("Leaffall", "autumn"),
    ("Mistmoon", "autumn"),
    ("Frostmoon", "winter"),
    ("Yearsend", "winter"),
]

# Seasons
SEASONS = {
    "spring": {
        "desc": "New growth emerges as the world awakens.",
        "weather_weights": {"clear": 30, "cloudy": 25, "rain": 30, "storm": 10, "fog": 5},
    },
    "summer": {
        "desc": "Warmth and long days mark the height of the year.",
        "weather_weights": {"clear": 50, "cloudy": 20, "rain": 15, "storm": 10, "hot": 5},
    },
    "autumn": {
        "desc": "Leaves turn gold and red as the year winds down.",
        "weather_weights": {"clear": 25, "cloudy": 30, "rain": 25, "fog": 15, "wind": 5},
    },
    "winter": {
        "desc": "Cold grips the land under gray skies.",
        "weather_weights": {"clear": 20, "cloudy": 30, "snow": 25, "blizzard": 5, "fog": 10, "cold": 10},
    },
}


# =============================================================================
# WEATHER CONFIGURATION  
# =============================================================================

WEATHER_CONDITIONS = {
    "clear": {
        "name": "Clear",
        "desc": "The sky is clear and bright.",
        "night_desc": "Stars twinkle in the clear night sky.",
        "effects": [],
    },
    "cloudy": {
        "name": "Cloudy",
        "desc": "Clouds drift across the sky.",
        "night_desc": "Clouds obscure the stars.",
        "effects": [],
    },
    "rain": {
        "name": "Rain",
        "desc": "Rain falls steadily from gray skies.",
        "night_desc": "Rain patters through the darkness.",
        "effects": ["wet", "reduced_visibility"],
        "indoor_notice": "You can hear rain pattering outside.",
    },
    "storm": {
        "name": "Storm",
        "desc": "Thunder rumbles and lightning flashes as rain pours down.",
        "night_desc": "Lightning illuminates the stormy night.",
        "effects": ["wet", "reduced_visibility", "loud"],
        "indoor_notice": "Thunder rumbles outside. Rain lashes the windows.",
    },
    "snow": {
        "name": "Snow",
        "desc": "Snowflakes drift down from the gray sky.",
        "night_desc": "Snow falls silently through the darkness.",
        "effects": ["cold", "reduced_visibility"],
        "indoor_notice": "Snow is falling outside.",
    },
    "blizzard": {
        "name": "Blizzard",
        "desc": "Howling winds drive blinding snow.",
        "night_desc": "The blizzard rages through the night.",
        "effects": ["cold", "reduced_visibility", "slow_movement"],
        "indoor_notice": "A blizzard howls outside.",
    },
    "fog": {
        "name": "Fog",
        "desc": "Thick fog shrouds the area.",
        "night_desc": "Impenetrable fog fills the night.",
        "effects": ["reduced_visibility"],
    },
    "wind": {
        "name": "Windy",
        "desc": "Strong winds gust through the area.",
        "night_desc": "Wind howls through the darkness.",
        "effects": [],
    },
    "hot": {
        "name": "Hot",
        "desc": "The air shimmers with oppressive heat.",
        "night_desc": "The night offers little relief from the heat.",
        "effects": ["hot"],
    },
    "cold": {
        "name": "Cold",
        "desc": "A bitter chill hangs in the air.",
        "night_desc": "The cold deepens as night falls.",
        "effects": ["cold"],
    },
}

# Area-specific weather overrides
AREA_WEATHER = {
    "indoor": None,  # No weather indoors
    "underground": None,  # No weather underground
    "grove": "mild",  # Grove is always mild (OOC safe zone)
    "museum": None,  # Indoors
}


# =============================================================================
# GLOBAL TIME STATE
# =============================================================================

# These get set by the TimeManager script
_game_time = {
    "hour": 8,
    "day": 1,
    "month": 0,
    "year": 1,
    "last_update": time.time(),
}

_global_weather = "clear"
_weather_duration = 0  # Hours until weather change


# =============================================================================
# TIME FUNCTIONS
# =============================================================================

def get_time_manager():
    """Get or create the TimeManager script."""
    scripts = search_object("TimeManager", typeclass="world.time_weather.TimeManager")
    if scripts:
        return scripts[0]
    
    # Create if doesn't exist
    from evennia import create_script
    try:
        script = create_script(
            "world.time_weather.TimeManager",
            key="TimeManager",
            persistent=True,
        )
        return script
    except Exception as e:
        logger.log_err(f"Failed to create TimeManager: {e}")
        return None


def get_time():
    """
    Get current game time.
    
    Returns:
        dict: {hour, day, month, year, day_of_week, month_name, season}
    """
    manager = get_time_manager()
    if manager:
        return manager.get_time()
    
    # Fallback to static time
    return {
        "hour": 12,
        "day": 1,
        "month": 0,
        "year": 1,
        "day_of_week": "Moonday",
        "month_name": "Deepwinter",
        "season": "winter",
    }


def get_hour():
    """Get current hour (0-23)."""
    return get_time()["hour"]


def get_period():
    """
    Get current time period.
    
    Returns:
        str: "dawn", "morning", "afternoon", "evening", "night", "midnight", "late_night"
    """
    hour = get_hour()
    
    for period, (start, end) in TIME_PERIODS.items():
        if start <= hour < end:
            return period
    
    return "night"


def get_period_description():
    """Get description of current time period."""
    return PERIOD_DESCRIPTIONS.get(get_period(), "")


def is_daytime():
    """Check if it's daytime (7:00 - 19:59)."""
    hour = get_hour()
    return 7 <= hour < 20


def is_night():
    """Check if it's nighttime (20:00 - 6:59)."""
    return not is_daytime()


def is_dawn():
    """Check if it's dawn (5:00 - 6:59)."""
    return get_period() == "dawn"


def is_dusk():
    """Check if it's evening/dusk (17:00 - 19:59)."""
    return get_period() == "evening"


def get_day_of_week():
    """Get current day of the week."""
    return get_time()["day_of_week"]


def get_month():
    """Get current month info."""
    game_time = get_time()
    return {
        "name": game_time["month_name"],
        "number": game_time["month"],
        "season": game_time["season"],
    }


def get_season():
    """Get current season."""
    return get_time()["season"]


def get_season_description():
    """Get description of current season."""
    season = get_season()
    return SEASONS.get(season, {}).get("desc", "")


def get_year():
    """Get current year."""
    return get_time()["year"]


def get_formatted_time():
    """
    Get nicely formatted time string.
    
    Returns:
        str: "Morning, Moonday, 15th of Springseed, Year 1"
    """
    game_time = get_time()
    period = get_period().title()
    
    day = game_time["day"]
    suffix = "th"
    if day in (1, 21):
        suffix = "st"
    elif day in (2, 22):
        suffix = "nd"
    elif day in (3, 23):
        suffix = "rd"
    
    return (f"{period}, {game_time['day_of_week']}, "
            f"{day}{suffix} of {game_time['month_name']}, "
            f"Year {game_time['year']}")


def get_time_string():
    """Get simple time string like '14:30'."""
    hour = get_hour()
    # We don't track minutes, so just show the hour
    return f"{hour:02d}:00"


# =============================================================================
# WEATHER FUNCTIONS
# =============================================================================

def get_global_weather():
    """Get current global weather condition."""
    manager = get_time_manager()
    if manager:
        return manager.db.weather or "clear"
    return "clear"


def get_weather(location=None):
    """
    Get weather for a location.
    
    Args:
        location: Room to check, or None for global
    
    Returns:
        str: Weather condition key
    """
    if location is None:
        return get_global_weather()
    
    # Check for indoor/special areas
    area_type = getattr(location.db, 'area_type', None)
    if area_type in AREA_WEATHER:
        override = AREA_WEATHER[area_type]
        if override is None:
            return None  # No weather
        elif override == "mild":
            return "clear"  # Always nice
    
    # Check for indoor flag
    if location.tags.has("indoor", category="room_flag"):
        return None
    
    # Check for area-specific override
    if location.db.weather_override:
        return location.db.weather_override
    
    return get_global_weather()


def get_weather_description(location=None, include_indoor=True):
    """
    Get weather description for a location.
    
    Args:
        location: Room to check
        include_indoor: Include indoor notice for weather
    
    Returns:
        str: Weather description
    """
    weather = get_weather(location)
    
    if weather is None:
        # Indoor - check for notice
        if include_indoor:
            global_weather = get_global_weather()
            weather_data = WEATHER_CONDITIONS.get(global_weather, {})
            return weather_data.get("indoor_notice", "")
        return ""
    
    weather_data = WEATHER_CONDITIONS.get(weather, {})
    
    if is_night():
        return weather_data.get("night_desc", weather_data.get("desc", ""))
    
    return weather_data.get("desc", "")


def get_weather_effects(location=None):
    """
    Get active weather effects for a location.
    
    Returns:
        list: Effect keys like ["wet", "cold", "reduced_visibility"]
    """
    weather = get_weather(location)
    
    if weather is None:
        return []
    
    weather_data = WEATHER_CONDITIONS.get(weather, {})
    return weather_data.get("effects", [])


def has_weather_effect(location, effect):
    """Check if location has a specific weather effect."""
    return effect in get_weather_effects(location)


def set_weather(condition, duration=None):
    """
    Manually set weather condition.
    
    Args:
        condition: Weather key
        duration: Hours until auto-change (None = random)
    """
    manager = get_time_manager()
    if manager:
        manager.set_weather(condition, duration)


# =============================================================================
# TIME MANAGER SCRIPT
# =============================================================================

class TimeManager(DefaultScript):
    """
    Global script that tracks game time and weather.
    
    Runs continuously, updating time based on real time elapsed.
    """
    
    def at_script_creation(self):
        """Set up the time manager."""
        self.key = "TimeManager"
        self.desc = "Tracks game time and weather"
        self.interval = 60  # Check every minute
        self.persistent = True
        
        # Initialize time
        self.db.hour = 8  # Start at 8 AM
        self.db.day = 1
        self.db.month = 2  # Springseed (spring)
        self.db.year = 1
        self.db.last_real_time = time.time()
        
        # Initialize weather
        self.db.weather = "clear"
        self.db.weather_hours_left = random.randint(4, 12)
        
        logger.log_info("TimeManager created")
    
    def at_repeat(self):
        """Called every interval - update time."""
        self.update_time()
    
    def update_time(self):
        """Update game time based on real time elapsed."""
        now = time.time()
        elapsed_real = now - (self.db.last_real_time or now)
        self.db.last_real_time = now
        
        # Calculate game hours elapsed
        hours_elapsed = elapsed_real / SECONDS_PER_GAME_HOUR
        
        if hours_elapsed < 1:
            return
        
        # Track period changes for announcements
        old_period = self._get_period(self.db.hour)
        
        # Advance time
        full_hours = int(hours_elapsed)
        self.db.hour += full_hours
        
        # Handle day rollover
        while self.db.hour >= 24:
            self.db.hour -= 24
            self.db.day += 1
            
            # Handle month rollover (28 days per month)
            if self.db.day > 28:
                self.db.day = 1
                self.db.month += 1
                
                # Handle year rollover (13 months)
                if self.db.month >= 13:
                    self.db.month = 0
                    self.db.year += 1
        
        # Update weather
        self.db.weather_hours_left = (self.db.weather_hours_left or 0) - full_hours
        if self.db.weather_hours_left <= 0:
            self.roll_weather()
        
        # Check for period change announcements
        new_period = self._get_period(self.db.hour)
        if old_period != new_period:
            self.announce_period_change(new_period)
        
        # Trigger NPC schedule updates
        self.update_npc_schedules()
    
    def _get_period(self, hour):
        """Get period for a given hour."""
        for period, (start, end) in TIME_PERIODS.items():
            if start <= hour < end:
                return period
        return "night"
    
    def announce_period_change(self, new_period):
        """Announce time period changes to outdoor rooms."""
        # Get all rooms (this could be optimized with tags)
        from evennia.objects.models import ObjectDB
        
        messages = {
            "dawn": "|yThe sun begins to rise, painting the sky with color.|n",
            "morning": "|yMorning light spreads across the land.|n",
            "afternoon": "|yThe sun reaches its peak overhead.|n",
            "evening": "|yThe sun begins its descent, casting long shadows.|n",
            "night": "|xDarkness falls as night arrives.|n",
            "midnight": "|xThe deepest part of night settles in.|n",
            "late_night": "|xThe night grows old, dawn still hours away.|n",
        }
        
        msg = messages.get(new_period)
        if not msg:
            return
        
        # Only announce to outdoor, occupied rooms
        try:
            from typeclasses.rooms import Room
            for room in ObjectDB.objects.filter(db_typeclass_path__contains="Room"):
                if room.tags.has("indoor", category="room_flag"):
                    continue
                if room.contents:
                    for obj in room.contents:
                        if hasattr(obj, 'msg') and hasattr(obj, 'has_account'):
                            if obj.has_account:
                                obj.msg(msg)
        except Exception as e:
            logger.log_err(f"Error announcing period change: {e}")
    
    def roll_weather(self):
        """Roll new random weather based on season."""
        season = self.get_season()
        weights = SEASONS.get(season, {}).get("weather_weights", {"clear": 100})
        
        # Weighted random selection
        total = sum(weights.values())
        roll = random.randint(1, total)
        
        cumulative = 0
        for condition, weight in weights.items():
            cumulative += weight
            if roll <= cumulative:
                self.set_weather(condition)
                return
        
        self.set_weather("clear")
    
    def set_weather(self, condition, duration=None):
        """Set weather condition."""
        old_weather = self.db.weather
        self.db.weather = condition
        self.db.weather_hours_left = duration or random.randint(4, 12)
        
        # Announce if weather changed significantly
        if old_weather != condition:
            self.announce_weather_change(old_weather, condition)
    
    def announce_weather_change(self, old_weather, new_weather):
        """Announce weather changes to outdoor rooms."""
        transitions = {
            ("clear", "rain"): "Clouds gather overhead and rain begins to fall.",
            ("clear", "storm"): "Dark clouds roll in as a storm approaches!",
            ("clear", "snow"): "Snowflakes begin to drift down from the sky.",
            ("rain", "clear"): "The rain stops and the clouds begin to part.",
            ("rain", "storm"): "The rain intensifies into a full storm!",
            ("storm", "clear"): "The storm passes, leaving clear skies.",
            ("storm", "rain"): "The storm weakens to a steady rain.",
            ("snow", "clear"): "The snow stops falling, leaving a white blanket.",
            ("snow", "blizzard"): "The wind picks up, turning the snow into a blizzard!",
            ("blizzard", "snow"): "The blizzard calms to gentle snowfall.",
        }
        
        msg = transitions.get((old_weather, new_weather))
        if not msg:
            new_data = WEATHER_CONDITIONS.get(new_weather, {})
            msg = f"The weather changes: {new_data.get('name', new_weather)}."
        
        msg = f"|c{msg}|n"
        
        # Announce to outdoor rooms
        try:
            from evennia.objects.models import ObjectDB
            for room in ObjectDB.objects.filter(db_typeclass_path__contains="Room"):
                if room.tags.has("indoor", category="room_flag"):
                    continue
                if room.contents:
                    for obj in room.contents:
                        if hasattr(obj, 'msg') and hasattr(obj, 'has_account'):
                            if obj.has_account:
                                obj.msg(msg)
        except Exception as e:
            logger.log_err(f"Error announcing weather change: {e}")
    
    def update_npc_schedules(self):
        """Update NPC positions based on schedules."""
        period = self._get_period(self.db.hour)
        
        try:
            from world.npcs import get_scheduled_location, move_npc_to_schedule
            from evennia import search_object
            
            # Find all NPCs
            npcs = search_object(None, attribute_name="npc_template")
            for npc in npcs:
                scheduled = get_scheduled_location(npc, period)
                if scheduled and npc.location and npc.location.key != scheduled:
                    move_npc_to_schedule(npc, period)
        except Exception as e:
            logger.log_err(f"Error updating NPC schedules: {e}")
    
    def get_time(self):
        """Get current game time dict."""
        day_of_week_idx = (self.db.day - 1) % 7
        month_data = MONTHS[self.db.month]
        
        return {
            "hour": self.db.hour,
            "day": self.db.day,
            "month": self.db.month,
            "year": self.db.year,
            "day_of_week": DAYS_OF_WEEK[day_of_week_idx],
            "month_name": month_data[0],
            "season": month_data[1],
        }
    
    def get_season(self):
        """Get current season."""
        month_data = MONTHS[self.db.month]
        return month_data[1]
    
    def set_time(self, hour=None, day=None, month=None, year=None):
        """Manually set time (admin function)."""
        if hour is not None:
            self.db.hour = max(0, min(23, hour))
        if day is not None:
            self.db.day = max(1, min(28, day))
        if month is not None:
            self.db.month = max(0, min(12, month))
        if year is not None:
            self.db.year = max(1, year)


# =============================================================================
# NPC SCHEDULE INTEGRATION
# =============================================================================

def get_npc_schedule_period():
    """
    Get schedule period for NPCs.
    
    Maps time periods to simpler schedule slots.
    """
    period = get_period()
    
    mapping = {
        "midnight": "night",
        "late_night": "night",
        "dawn": "morning",
        "morning": "morning",
        "afternoon": "afternoon",
        "evening": "evening",
        "night": "night",
    }
    
    return mapping.get(period, "afternoon")


# =============================================================================
# ADMIN/DEBUG FUNCTIONS
# =============================================================================

def advance_time(hours=1):
    """
    Manually advance time (for testing).
    
    Args:
        hours: Hours to advance
    """
    manager = get_time_manager()
    if manager:
        manager.db.hour += hours
        # Let normal update handle rollovers
        manager.update_time()


def set_time_of_day(hour):
    """Set time to specific hour (0-23)."""
    manager = get_time_manager()
    if manager:
        manager.set_time(hour=hour)


def set_season(season):
    """Set to a specific season."""
    manager = get_time_manager()
    if not manager:
        return
    
    # Find a month in that season
    for idx, (name, s) in enumerate(MONTHS):
        if s == season:
            manager.set_time(month=idx)
            return


def force_weather(condition, duration=None):
    """Force specific weather condition."""
    set_weather(condition, duration)


def get_time_debug():
    """Get debug string with all time info."""
    game_time = get_time()
    weather = get_global_weather()
    
    manager = get_time_manager()
    weather_left = manager.db.weather_hours_left if manager else 0
    
    return (
        f"Time: {get_formatted_time()}\n"
        f"Hour: {game_time['hour']}, Period: {get_period()}\n"
        f"Day: {game_time['day']}/{game_time['month_name']}/Year {game_time['year']}\n"
        f"Season: {game_time['season']}\n"
        f"Weather: {weather} ({weather_left}h remaining)\n"
        f"Daytime: {is_daytime()}, Night: {is_night()}"
    )
