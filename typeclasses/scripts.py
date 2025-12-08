"""
Script Typeclasses for Gilderhaven
===================================

Background scripts that handle timed events, effect expiry,
and world simulation.

These scripts run persistently and handle:
- Effect/buff expiration
- Random ambient events
- World state updates
- Scheduled NPC activities
"""

from evennia.scripts.scripts import DefaultScript
from evennia.utils import logger


# =============================================================================
# EFFECT EXPIRY SCRIPT
# =============================================================================

class EffectExpiryScript(DefaultScript):
    """
    Script that removes an effect after its duration expires.
    
    Created automatically when a timed effect is applied.
    Stores the target and effect_id, then removes the effect
    when the timer fires.
    
    Usage (called by world/effects.py):
        script = EffectExpiryScript.create(
            obj=target,
            key=f"effect_expiry_{effect_id}",
            interval=duration,
            persistent=False,
            autostart=True,
        )
        script.db.effect_id = effect_id
    """
    
    def at_script_creation(self):
        """Called when script is first created."""
        self.key = "effect_expiry"
        self.desc = "Removes an effect when duration expires"
        self.persistent = False  # Don't survive server restart
        self.start_delay = True  # Wait for interval before first fire
        
        # Will be set by the creator
        self.db.effect_id = None
    
    def at_repeat(self):
        """
        Called when the timer fires.
        
        Removes the effect from the target and deletes this script.
        """
        target = self.obj
        effect_id = self.db.effect_id
        
        if not target or not effect_id:
            logger.log_warn(f"EffectExpiryScript fired without target or effect_id")
            self.stop()
            return
        
        try:
            from world.effects import remove_effect
            
            # Remove the effect
            success = remove_effect(target, effect_id, silent=False)
            
            if success:
                logger.log_info(f"Effect {effect_id} expired on {target.key}")
            else:
                logger.log_warn(f"Failed to remove expired effect {effect_id} from {target.key}")
        
        except ImportError:
            logger.log_err("world.effects not available for EffectExpiryScript")
        except Exception as e:
            logger.log_err(f"Error in EffectExpiryScript: {e}")
        
        # Script only fires once
        self.stop()
    
    def at_stop(self):
        """Called when script stops."""
        # Clean up
        pass


# =============================================================================
# RANDOM EVENT TICKER
# =============================================================================

class RandomEventTickScript(DefaultScript):
    """
    Global script that fires random ambient and world events periodically.
    
    Runs every 60 seconds by default. Checks all populated rooms
    and potentially triggers ambient events, NPC activities, 
    weather changes, etc.
    
    Usage (run once to start):
        @py from typeclasses.scripts import RandomEventTickScript; RandomEventTickScript.create()
        
    Or programmatically:
        from typeclasses.scripts import RandomEventTickScript
        RandomEventTickScript.create(key="random_event_ticker")
    """
    
    def at_script_creation(self):
        """Called when script is first created."""
        self.key = "random_event_ticker"
        self.desc = "Fires random ambient and world events"
        self.interval = 60  # Every 60 seconds
        self.persistent = True  # Survive server restart
        self.start_delay = True  # Don't fire immediately on creation
    
    def at_repeat(self):
        """
        Called every interval.
        
        Triggers the random event system to potentially fire
        ambient events in populated rooms.
        """
        try:
            from world.random_events import tick_random_events
            tick_random_events()
        except ImportError:
            # world.random_events not yet implemented, skip silently
            pass
        except Exception as e:
            logger.log_err(f"Error in RandomEventTickScript: {e}")
    
    def at_start(self):
        """Called when script starts."""
        logger.log_info("RandomEventTickScript started - ambient events active")
    
    def at_stop(self):
        """Called when script stops."""
        logger.log_info("RandomEventTickScript stopped")


# =============================================================================
# WORLD TIME SCRIPT
# =============================================================================

class WorldTimeScript(DefaultScript):
    """
    Global script that advances in-game time.
    
    Tracks the current time of day and season.
    Updates room descriptions that use time-based shortcodes.
    
    Time periods: dawn, morning, midday, afternoon, evening, night
    Seasons: spring, summer, autumn, winter
    
    Usage:
        @py from typeclasses.scripts import WorldTimeScript; WorldTimeScript.create()
    """
    
    def at_script_creation(self):
        """Called when script is first created."""
        self.key = "world_time"
        self.desc = "Tracks and advances in-game time"
        self.interval = 300  # Every 5 minutes real time = 1 hour game time
        self.persistent = True
        self.start_delay = False
        
        # Initialize time state
        self.db.hour = 8  # Start at 8 AM
        self.db.day = 1
        self.db.season_day = 1
        self.db.season = "summer"
    
    def at_repeat(self):
        """Advance time by one hour."""
        self.db.hour = (self.db.hour + 1) % 24
        
        # New day
        if self.db.hour == 0:
            self.db.day += 1
            self.db.season_day += 1
            
            # Season change every 28 days
            if self.db.season_day > 28:
                self.db.season_day = 1
                seasons = ["spring", "summer", "autumn", "winter"]
                current_idx = seasons.index(self.db.season)
                self.db.season = seasons[(current_idx + 1) % 4]
                
                # Announce season change
                self._announce_season_change()
    
    def _announce_season_change(self):
        """Announce the season change to all players."""
        from evennia import SESSION_HANDLER
        
        messages = {
            "spring": "The world awakens as |gspring|n arrives. Flowers begin to bloom.",
            "summer": "The warmth of |ysummer|n spreads across the land.",
            "autumn": "Leaves turn golden as |rautumn|n settles in.",
            "winter": "A chill fills the air as |wwinter|n takes hold.",
        }
        
        msg = messages.get(self.db.season, "The seasons change.")
        
        for session in SESSION_HANDLER.get_sessions():
            if session.puppet:
                session.puppet.msg(f"\n|w[World]|n {msg}\n")
    
    def get_time_period(self) -> str:
        """Get current time period name."""
        hour = self.db.hour
        if 5 <= hour < 7:
            return "dawn"
        elif 7 <= hour < 12:
            return "morning"
        elif 12 <= hour < 14:
            return "midday"
        elif 14 <= hour < 18:
            return "afternoon"
        elif 18 <= hour < 21:
            return "evening"
        else:
            return "night"
    
    def get_season(self) -> str:
        """Get current season."""
        return self.db.season
    
    def get_hour(self) -> int:
        """Get current hour (0-23)."""
        return self.db.hour


# =============================================================================
# WEATHER SCRIPT
# =============================================================================

class WeatherScript(DefaultScript):
    """
    Global script that manages weather patterns.
    
    Weather can change randomly or be set manually.
    Affects outdoor room descriptions.
    
    Weather types: clear, cloudy, rain, storm, fog, snow
    
    Usage:
        @py from typeclasses.scripts import WeatherScript; WeatherScript.create()
    """
    
    def at_script_creation(self):
        """Called when script is first created."""
        self.key = "world_weather"
        self.desc = "Manages weather patterns"
        self.interval = 600  # Check every 10 minutes
        self.persistent = True
        self.start_delay = True
        
        # Initialize weather state
        self.db.current_weather = "clear"
        self.db.weather_duration = 0  # Hours until next change
    
    def at_repeat(self):
        """Potentially change the weather."""
        import random
        
        # Decrease duration
        self.db.weather_duration -= 1
        
        # Time for a change?
        if self.db.weather_duration <= 0:
            self._change_weather()
    
    def _change_weather(self):
        """Randomly select new weather."""
        import random
        
        # Get season for weather probabilities
        time_script = self._get_time_script()
        season = time_script.get_season() if time_script else "summer"
        
        # Weather probabilities by season
        weather_weights = {
            "spring": {"clear": 30, "cloudy": 30, "rain": 30, "storm": 5, "fog": 5},
            "summer": {"clear": 50, "cloudy": 25, "rain": 15, "storm": 10},
            "autumn": {"clear": 25, "cloudy": 35, "rain": 25, "fog": 15},
            "winter": {"clear": 30, "cloudy": 30, "snow": 30, "fog": 10},
        }
        
        weights = weather_weights.get(season, weather_weights["summer"])
        
        # Weighted random selection
        choices = list(weights.keys())
        probs = list(weights.values())
        
        new_weather = random.choices(choices, weights=probs, k=1)[0]
        
        if new_weather != self.db.current_weather:
            self.db.current_weather = new_weather
            self._announce_weather_change()
        
        # Set duration (2-8 hours)
        self.db.weather_duration = random.randint(2, 8)
    
    def _get_time_script(self):
        """Get the world time script if it exists."""
        from evennia import search_script
        results = search_script("world_time")
        return results[0] if results else None
    
    def _announce_weather_change(self):
        """Announce weather change to players in outdoor areas."""
        from evennia import SESSION_HANDLER
        
        messages = {
            "clear": "The sky clears, revealing bright sunshine.",
            "cloudy": "Clouds roll in, dimming the light.",
            "rain": "Rain begins to fall from the grey sky.",
            "storm": "Thunder rumbles as a storm moves in.",
            "fog": "A thick fog rolls across the land.",
            "snow": "Snowflakes begin drifting down from above.",
        }
        
        msg = messages.get(self.db.current_weather, "The weather shifts.")
        
        for session in SESSION_HANDLER.get_sessions():
            puppet = session.puppet
            if puppet and puppet.location:
                # Only announce to players in outdoor areas
                loc = puppet.location
                if getattr(loc.db, 'is_outdoor', False) or getattr(loc, 'is_outdoor', False):
                    puppet.msg(f"\n|w[Weather]|n {msg}\n")
    
    def get_weather(self) -> str:
        """Get current weather."""
        return self.db.current_weather
    
    def set_weather(self, weather: str, duration: int = 4):
        """Manually set weather."""
        valid = ["clear", "cloudy", "rain", "storm", "fog", "snow"]
        if weather in valid:
            self.db.current_weather = weather
            self.db.weather_duration = duration
            self._announce_weather_change()


# =============================================================================
# NPC SCHEDULE SCRIPT
# =============================================================================

class NPCScheduleScript(DefaultScript):
    """
    Script that handles NPC scheduling and movement.
    
    Checks if NPCs need to move to their scheduled locations
    based on the current time of day.
    
    Usage:
        @py from typeclasses.scripts import NPCScheduleScript; NPCScheduleScript.create()
    """
    
    def at_script_creation(self):
        """Called when script is first created."""
        self.key = "npc_scheduler"
        self.desc = "Handles NPC schedules and movement"
        self.interval = 300  # Every 5 minutes
        self.persistent = True
        self.start_delay = True
    
    def at_repeat(self):
        """Check and update NPC positions."""
        try:
            from world.npc_schedules import update_all_npc_schedules
            update_all_npc_schedules()
        except ImportError:
            # world.npc_schedules not yet implemented
            pass
        except Exception as e:
            logger.log_err(f"Error in NPCScheduleScript: {e}")


# =============================================================================
# RESOURCE RESPAWN SCRIPT
# =============================================================================

class ResourceRespawnScript(DefaultScript):
    """
    Script that handles resource node respawning.
    
    Checks all depleted resource nodes and respawns them
    if enough time has passed.
    
    Usage:
        @py from typeclasses.scripts import ResourceRespawnScript; ResourceRespawnScript.create()
    """
    
    def at_script_creation(self):
        """Called when script is first created."""
        self.key = "resource_respawn"
        self.desc = "Handles resource node respawning"
        self.interval = 120  # Every 2 minutes
        self.persistent = True
        self.start_delay = True
    
    def at_repeat(self):
        """Check and respawn depleted resources."""
        try:
            from world.resources import tick_resource_respawns
            tick_resource_respawns()
        except ImportError:
            # world.resources not yet implemented
            pass
        except Exception as e:
            logger.log_err(f"Error in ResourceRespawnScript: {e}")


# =============================================================================
# CONVENIENCE FUNCTIONS
# =============================================================================

def start_world_scripts():
    """
    Start all world simulation scripts.
    
    Call this once after server setup to activate all systems.
    
    Usage:
        @py from typeclasses.scripts import start_world_scripts; start_world_scripts()
    """
    from evennia import search_script
    
    scripts_to_start = [
        ("random_event_ticker", RandomEventTickScript),
        ("world_time", WorldTimeScript),
        ("world_weather", WeatherScript),
        ("npc_scheduler", NPCScheduleScript),
        ("resource_respawn", ResourceRespawnScript),
    ]
    
    started = []
    
    for key, script_class in scripts_to_start:
        # Check if already running
        existing = search_script(key)
        if existing:
            logger.log_info(f"Script '{key}' already running")
            continue
        
        # Create and start
        script = script_class.create(key=key)
        started.append(key)
        logger.log_info(f"Started script: {key}")
    
    return started


def stop_world_scripts():
    """
    Stop all world simulation scripts.
    
    Usage:
        @py from typeclasses.scripts import stop_world_scripts; stop_world_scripts()
    """
    from evennia import search_script
    
    keys = [
        "random_event_ticker",
        "world_time", 
        "world_weather",
        "npc_scheduler",
        "resource_respawn",
    ]
    
    stopped = []
    
    for key in keys:
        results = search_script(key)
        for script in results:
            script.stop()
            stopped.append(key)
            logger.log_info(f"Stopped script: {key}")
    
    return stopped


def get_world_time():
    """
    Get the current in-game time info.
    
    Returns:
        dict with hour, period, day, season
    """
    from evennia import search_script
    
    results = search_script("world_time")
    if results:
        script = results[0]
        return {
            "hour": script.get_hour(),
            "period": script.get_time_period(),
            "day": script.db.day,
            "season": script.get_season(),
        }
    
    # Defaults if script not running
    return {
        "hour": 12,
        "period": "midday",
        "day": 1,
        "season": "summer",
    }


def get_world_weather():
    """
    Get the current weather.
    
    Returns:
        str: Current weather type
    """
    from evennia import search_script
    
    results = search_script("world_weather")
    if results:
        return results[0].get_weather()
    
    return "clear"


def set_time(period: str):
    """
    Manually set the time of day.
    
    Args:
        period: One of dawn, morning, midday, afternoon, evening, night
        
    Usage:
        @py from typeclasses.scripts import set_time; set_time("night")
    """
    from evennia import search_script
    
    period_hours = {
        "dawn": 6,
        "morning": 9,
        "midday": 12,
        "afternoon": 15,
        "evening": 19,
        "night": 22,
    }
    
    if period not in period_hours:
        return f"Invalid period. Choose from: {', '.join(period_hours.keys())}"
    
    results = search_script("world_time")
    if results:
        results[0].db.hour = period_hours[period]
        return f"Time set to {period} ({period_hours[period]}:00)"
    
    return "WorldTimeScript not running. Start it first."


def set_weather(weather: str):
    """
    Manually set the weather.
    
    Args:
        weather: One of clear, cloudy, rain, storm, fog, snow
        
    Usage:
        @py from typeclasses.scripts import set_weather; set_weather("storm")
    """
    from evennia import search_script
    
    valid = ["clear", "cloudy", "rain", "storm", "fog", "snow"]
    
    if weather not in valid:
        return f"Invalid weather. Choose from: {', '.join(valid)}"
    
    results = search_script("world_weather")
    if results:
        results[0].set_weather(weather)
        return f"Weather set to {weather}"
    
    return "WeatherScript not running. Start it first."


# =============================================================================
# MODULE EXPORTS
# =============================================================================

__all__ = [
    # Script classes
    "EffectExpiryScript",
    "RandomEventTickScript",
    "WorldTimeScript",
    "WeatherScript",
    "NPCScheduleScript",
    "ResourceRespawnScript",
    
    # Convenience functions
    "start_world_scripts",
    "stop_world_scripts",
    "get_world_time",
    "get_world_weather",
    "set_time",
    "set_weather",
]
