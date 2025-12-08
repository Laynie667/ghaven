"""
Time and Weather Commands for Gilderhaven
==========================================

Commands for checking time and weather.

Commands:
- time: View current game time
- weather: View current weather
- calendar: View calendar info
"""

from evennia import Command, CmdSet
from world.time_weather import (
    get_time, get_period, get_formatted_time, get_time_string,
    get_season, get_season_description, get_period_description,
    get_weather, get_weather_description, get_global_weather,
    is_daytime, is_night,
    WEATHER_CONDITIONS, SEASONS, MONTHS, DAYS_OF_WEEK,
)


class CmdTime(Command):
    """
    Check the current time.
    
    Usage:
        time        - Show current time and period
        time full   - Show detailed time info
    
    The Grove exists outside normal time, but the game
    still tracks day/night cycles for the outer realms.
    """
    
    key = "time"
    aliases = ["clock"]
    locks = "cmd:all()"
    help_category = "World"
    
    def func(self):
        caller = self.caller
        
        if self.args and "full" in self.args.lower():
            # Detailed view
            game_time = get_time()
            period = get_period()
            season = get_season()
            
            lines = ["|wCurrent Time|n"]
            lines.append("-" * 40)
            lines.append(get_formatted_time())
            lines.append("")
            lines.append(f"Hour: {get_time_string()}")
            lines.append(f"Period: {period.title()}")
            lines.append(get_period_description())
            lines.append("")
            lines.append(f"Season: {season.title()}")
            lines.append(get_season_description())
            
            if is_daytime():
                lines.append("")
                lines.append("|yThe sun is up.|n")
            else:
                lines.append("")
                lines.append("|xNight has fallen.|n")
            
            caller.msg("\n".join(lines))
        else:
            # Simple view
            period = get_period()
            game_time = get_time()
            
            time_str = f"|w{period.title()}|n, {game_time['day_of_week']}"
            
            if is_daytime():
                caller.msg(f"{time_str} |y(daytime)|n")
            else:
                caller.msg(f"{time_str} |x(nighttime)|n")


class CmdWeather(Command):
    """
    Check the current weather.
    
    Usage:
        weather         - Show weather where you are
        weather global  - Show global weather
    
    Weather affects outdoor areas. Indoor locations are
    sheltered from weather effects.
    """
    
    key = "weather"
    locks = "cmd:all()"
    help_category = "World"
    
    def func(self):
        caller = self.caller
        location = caller.location
        
        if self.args and "global" in self.args.lower():
            # Show global weather
            weather = get_global_weather()
            weather_data = WEATHER_CONDITIONS.get(weather, {})
            
            lines = ["|wGlobal Weather|n"]
            lines.append("-" * 40)
            lines.append(f"Condition: {weather_data.get('name', weather)}")
            
            if is_night():
                lines.append(weather_data.get("night_desc", ""))
            else:
                lines.append(weather_data.get("desc", ""))
            
            effects = weather_data.get("effects", [])
            if effects:
                lines.append(f"Effects: {', '.join(effects)}")
            
            caller.msg("\n".join(lines))
            return
        
        # Show local weather
        weather = get_weather(location)
        
        if weather is None:
            # Indoors
            global_weather = get_global_weather()
            weather_data = WEATHER_CONDITIONS.get(global_weather, {})
            indoor_notice = weather_data.get("indoor_notice", "")
            
            if indoor_notice:
                caller.msg(f"You are indoors. {indoor_notice}")
            else:
                caller.msg("You are indoors, sheltered from the weather.")
            return
        
        # Outdoors
        desc = get_weather_description(location)
        weather_data = WEATHER_CONDITIONS.get(weather, {})
        
        lines = []
        lines.append(f"|wWeather: {weather_data.get('name', weather)}|n")
        lines.append(desc)
        
        effects = weather_data.get("effects", [])
        if effects:
            lines.append(f"|xEffects: {', '.join(effects)}|n")
        
        caller.msg("\n".join(lines))


class CmdCalendar(Command):
    """
    View calendar information.
    
    Usage:
        calendar          - Show current date
        calendar months   - List all months
        calendar seasons  - List seasons
        calendar days     - List days of the week
    
    The Grove calendar has 13 months of 28 days each,
    organized into four seasons.
    """
    
    key = "calendar"
    aliases = ["date"]
    locks = "cmd:all()"
    help_category = "World"
    
    def func(self):
        caller = self.caller
        
        if self.args:
            arg = self.args.strip().lower()
            
            if arg == "months":
                lines = ["|wMonths of the Year|n"]
                lines.append("-" * 40)
                
                for idx, (name, season) in enumerate(MONTHS):
                    lines.append(f"  {idx+1}. {name} ({season})")
                
                caller.msg("\n".join(lines))
                return
            
            elif arg == "seasons":
                lines = ["|wSeasons|n"]
                lines.append("-" * 40)
                
                for season, data in SEASONS.items():
                    lines.append(f"|c{season.title()}|n")
                    lines.append(f"  {data['desc']}")
                    
                    # List months in this season
                    season_months = [m[0] for m in MONTHS if m[1] == season]
                    lines.append(f"  Months: {', '.join(season_months)}")
                    lines.append("")
                
                caller.msg("\n".join(lines))
                return
            
            elif arg == "days":
                lines = ["|wDays of the Week|n"]
                lines.append("-" * 40)
                
                for day in DAYS_OF_WEEK:
                    lines.append(f"  {day}")
                
                caller.msg("\n".join(lines))
                return
        
        # Show current date
        game_time = get_time()
        season = get_season()
        
        day = game_time["day"]
        suffix = "th"
        if day in (1, 21):
            suffix = "st"
        elif day in (2, 22):
            suffix = "nd"
        elif day in (3, 23):
            suffix = "rd"
        
        lines = ["|wCalendar|n"]
        lines.append("-" * 40)
        lines.append(f"Date: {game_time['day_of_week']}, {day}{suffix} of {game_time['month_name']}")
        lines.append(f"Year: {game_time['year']}")
        lines.append(f"Season: {season.title()}")
        lines.append("")
        lines.append(get_season_description())
        
        caller.msg("\n".join(lines))


class CmdTimeAdmin(Command):
    """
    Admin commands for time/weather control.
    
    Usage:
        timeadmin                 - Show debug info
        timeadmin set hour <n>    - Set hour (0-23)
        timeadmin set day <n>     - Set day (1-28)
        timeadmin set month <n>   - Set month (0-12)
        timeadmin set season <s>  - Set season
        timeadmin weather <cond>  - Set weather
        timeadmin advance <hours> - Advance time
    
    This is an admin-only command for testing.
    """
    
    key = "timeadmin"
    aliases = ["@time"]
    locks = "cmd:perm(Admin) or perm(Developer)"
    help_category = "Admin"
    
    def func(self):
        caller = self.caller
        
        if not self.args:
            # Debug info
            from world.time_weather import get_time_debug
            caller.msg(get_time_debug())
            return
        
        args = self.args.strip().lower().split()
        
        if args[0] == "set" and len(args) >= 3:
            from world.time_weather import get_time_manager, set_season
            manager = get_time_manager()
            
            if not manager:
                caller.msg("TimeManager not found.")
                return
            
            what = args[1]
            value = args[2]
            
            if what == "hour":
                try:
                    hour = int(value)
                    manager.set_time(hour=hour)
                    caller.msg(f"Set hour to {hour}.")
                except ValueError:
                    caller.msg("Hour must be a number 0-23.")
            
            elif what == "day":
                try:
                    day = int(value)
                    manager.set_time(day=day)
                    caller.msg(f"Set day to {day}.")
                except ValueError:
                    caller.msg("Day must be a number 1-28.")
            
            elif what == "month":
                try:
                    month = int(value)
                    manager.set_time(month=month)
                    caller.msg(f"Set month to {month}.")
                except ValueError:
                    caller.msg("Month must be a number 0-12.")
            
            elif what == "season":
                set_season(value)
                caller.msg(f"Set season to {value}.")
            
            else:
                caller.msg("Unknown time component. Use: hour, day, month, season")
        
        elif args[0] == "weather" and len(args) >= 2:
            from world.time_weather import set_weather
            condition = args[1]
            
            if condition not in WEATHER_CONDITIONS:
                caller.msg(f"Unknown weather: {condition}")
                caller.msg(f"Options: {', '.join(WEATHER_CONDITIONS.keys())}")
                return
            
            duration = int(args[2]) if len(args) > 2 else None
            set_weather(condition, duration)
            caller.msg(f"Set weather to {condition}.")
        
        elif args[0] == "advance" and len(args) >= 2:
            from world.time_weather import advance_time
            try:
                hours = int(args[1])
                advance_time(hours)
                caller.msg(f"Advanced time by {hours} hours.")
            except ValueError:
                caller.msg("Hours must be a number.")
        
        else:
            caller.msg("Usage: timeadmin [set hour/day/month/season <value>] [weather <cond>] [advance <hours>]")


# =============================================================================
# Command Set
# =============================================================================

class TimeCmdSet(CmdSet):
    """Time and weather commands."""
    
    key = "time"
    priority = 1
    
    def at_cmdset_creation(self):
        self.add(CmdTime())
        self.add(CmdWeather())
        self.add(CmdCalendar())
        self.add(CmdTimeAdmin())
