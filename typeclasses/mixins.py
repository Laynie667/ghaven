"""
Gilderhaven Typeclasses - Mixins
================================

Mixins that add functionality to Evennia typeclasses without
modifying base Character.py or Room.py directly.

Mixins:
- DynamicDescMixin: Process shortcodes in descriptions

Usage:
    # In your typeclasses/rooms.py
    from evennia import DefaultRoom
    from typeclasses.mixins import DynamicDescMixin
    
    class Room(DynamicDescMixin, DefaultRoom):
        pass
    
    # In your typeclasses/characters.py  
    from evennia import DefaultCharacter
    from typeclasses.mixins import DynamicDescMixin
    
    class Character(DynamicDescMixin, DefaultCharacter):
        pass
"""

from evennia.utils.utils import lazy_property


class DynamicDescMixin:
    """
    Mixin that processes shortcodes in object descriptions.
    
    Supports time, weather, body parts, pronouns, etc.
    Works for both Rooms and Characters.
    
    Shortcodes processed:
        Time:
            <time>              - Period name (morning, night)
            <time.period>       - Same as <time>
            <time.hour>         - Hour like "14:00"
            <time.desc>         - Period description text
            <time.full>         - Full formatted time
            <time.day>          - Day of week name
            <time.date>         - Full date
        
        Weather:
            <weather>           - Weather condition name
            <weather.desc>      - Weather description
            <weather.effects>   - Active weather effects
        
        Season:
            <season>            - Season name
            <season.desc>       - Season description
        
        Body (for characters):
            <body.X>            - Body part description
            <body.X.state>      - Body part in specific state
            <worn.slot>         - Equipment in slot
            <name>              - Character name
            <pronoun.subject>   - she/he/they
            <pronoun.object>    - her/him/them
            <pronoun.possessive>- her/his/their
            <position>          - Position description
            <pose>              - Current pose
    
    Usage in descriptions:
        @desc here = The village square. <weather.desc> <time.desc>
        @desc me = A wolf with <body.tail> and <body.ears>.
    """
    
    def get_display_desc(self, looker, **kwargs):
        """
        Get the description with shortcodes processed.
        
        Override this method in your typeclass to customize
        how descriptions are retrieved before processing.
        """
        return self.db.desc or ""
    
    def return_appearance(self, looker, **kwargs):
        """
        Process shortcodes in the appearance output.
        
        This hooks into Evennia's standard appearance system.
        """
        # Get base appearance from parent
        appearance = super().return_appearance(looker, **kwargs)
        
        if not appearance:
            return appearance
        
        # Process shortcodes
        try:
            from world.body import process_shortcodes
            
            # Determine context based on what kind of object this is
            if self.is_typeclass("typeclasses.rooms.Room", exact=False) or \
               hasattr(self, 'exits'):
                # This is a room - use looker as character, self as location
                appearance = process_shortcodes(looker, appearance, location=self)
            else:
                # This is a character/object - use self as character
                location = getattr(self, 'location', None)
                appearance = process_shortcodes(self, appearance, location=location)
        
        except ImportError:
            # world.body not available, return unprocessed
            pass
        except Exception as e:
            # Log error but don't break appearance
            from evennia.utils import logger
            logger.log_err(f"Error processing shortcodes: {e}")
        
        return appearance
    
    def get_dynamic_desc(self, looker=None):
        """
        Get description with shortcodes processed.
        
        Convenience method for getting just the processed desc.
        
        Args:
            looker: Who's looking (affects weather location, etc.)
        
        Returns:
            str: Processed description
        """
        desc = self.get_display_desc(looker)
        
        if not desc:
            return ""
        
        try:
            from world.body import process_shortcodes
            
            if self.is_typeclass("typeclasses.rooms.Room", exact=False) or \
               hasattr(self, 'exits'):
                return process_shortcodes(looker, desc, location=self)
            else:
                location = getattr(self, 'location', None)
                return process_shortcodes(self, desc, location=location)
        
        except ImportError:
            return desc
        except Exception:
            return desc


class TimeAwareMixin:
    """
    Mixin for objects that change behavior based on time.
    
    Provides convenience methods for time-based logic.
    
    Usage:
        class MyRoom(TimeAwareMixin, DefaultRoom):
            def at_object_receive(self, obj, source_location):
                if self.is_night():
                    obj.msg("The area seems more dangerous at night...")
    """
    
    def get_current_period(self):
        """Get current time period."""
        try:
            from world.time_weather import get_period
            return get_period()
        except ImportError:
            return "afternoon"
    
    def is_daytime(self):
        """Check if it's daytime."""
        try:
            from world.time_weather import is_daytime
            return is_daytime()
        except ImportError:
            return True
    
    def is_night(self):
        """Check if it's nighttime."""
        try:
            from world.time_weather import is_night
            return is_night()
        except ImportError:
            return False
    
    def is_dawn(self):
        """Check if it's dawn."""
        try:
            from world.time_weather import is_dawn
            return is_dawn()
        except ImportError:
            return False
    
    def is_dusk(self):
        """Check if it's dusk/evening."""
        try:
            from world.time_weather import is_dusk
            return is_dusk()
        except ImportError:
            return False
    
    def get_season(self):
        """Get current season."""
        try:
            from world.time_weather import get_season
            return get_season()
        except ImportError:
            return "summer"


class WeatherAwareMixin:
    """
    Mixin for objects that respond to weather.
    
    Provides convenience methods for weather-based logic.
    
    Usage:
        class OutdoorRoom(WeatherAwareMixin, DefaultRoom):
            def at_object_receive(self, obj, source_location):
                if self.is_raining():
                    obj.msg("Rain soaks you as you enter.")
    """
    
    def get_weather(self):
        """Get weather at this location."""
        try:
            from world.time_weather import get_weather
            return get_weather(self)
        except ImportError:
            return "clear"
    
    def get_weather_desc(self):
        """Get weather description for this location."""
        try:
            from world.time_weather import get_weather_description
            return get_weather_description(self)
        except ImportError:
            return ""
    
    def is_indoor(self):
        """Check if this location is indoors (no weather)."""
        if self.tags.has("indoor", category="room_flag"):
            return True
        try:
            from world.time_weather import get_weather
            return get_weather(self) is None
        except ImportError:
            return False
    
    def is_raining(self):
        """Check if it's raining here."""
        weather = self.get_weather()
        return weather in ("rain", "storm")
    
    def is_snowing(self):
        """Check if it's snowing here."""
        weather = self.get_weather()
        return weather in ("snow", "blizzard")
    
    def is_stormy(self):
        """Check if there's a storm."""
        weather = self.get_weather()
        return weather in ("storm", "blizzard")
    
    def has_weather_effect(self, effect):
        """Check for specific weather effect."""
        try:
            from world.time_weather import has_weather_effect
            return has_weather_effect(self, effect)
        except ImportError:
            return False
    
    def is_cold(self):
        """Check if it's cold here."""
        return self.has_weather_effect("cold")
    
    def is_wet(self):
        """Check if weather is making things wet."""
        return self.has_weather_effect("wet")
    
    def has_reduced_visibility(self):
        """Check if visibility is reduced."""
        return self.has_weather_effect("reduced_visibility")


class GilderhaveRoomMixin(DynamicDescMixin, TimeAwareMixin, WeatherAwareMixin):
    """
    Combined mixin for Gilderhaven rooms.
    
    Includes:
    - Dynamic descriptions with shortcodes
    - Time awareness
    - Weather awareness
    - Quest objective tracking
    - Random encounter triggering
    
    Usage:
        from evennia import DefaultRoom
        from typeclasses.mixins import GilderhaveRoomMixin
        
        class Room(GilderhaveRoomMixin, DefaultRoom):
            pass
    """
    
    def at_object_receive(self, obj, source_location, **kwargs):
        """Called when something enters this room."""
        super().at_object_receive(obj, source_location, **kwargs)
        
        # Only track player characters
        if not hasattr(obj, 'has_account') or not obj.has_account:
            return
        
        # Track room visits for quests
        try:
            from world.quests import check_visit_objective
            
            # Check if first visit
            visited = obj.db.visited_rooms or []
            room_key = self.db.room_key or self.key
            first_visit = room_key not in visited
            
            if first_visit:
                visited.append(room_key)
                obj.db.visited_rooms = visited
            
            check_visit_objective(obj, self.key, room_key=room_key, first_visit=first_visit)
        except ImportError:
            pass
        
        # Check for random encounters
        try:
            from world.encounters import on_room_enter
            from world.parties import is_party_leader, get_party
            
            # Only trigger for solo players or party leaders
            party = get_party(obj)
            if party and not is_party_leader(obj):
                # Non-leaders don't trigger encounters (they follow leader)
                return
            
            # Check for encounter (with small delay to let movement finish)
            from evennia.utils import delay
            delay(0.5, on_room_enter, obj, self)
        except ImportError:
            pass
    
    def get_danger_level(self):
        """Get danger level for this room."""
        try:
            from world.encounters import get_room_danger
            return get_room_danger(self)
        except ImportError:
            return {"name": "Unknown", "encounter_mult": 1.0}
    
    def is_safe_zone(self):
        """Check if this room is safe from encounters."""
        danger = self.get_danger_level()
        return danger.get("encounter_mult", 1.0) == 0


class GilderhaveCharacterMixin(DynamicDescMixin, TimeAwareMixin):
    """
    Combined mixin for Gilderhaven characters.
    
    Includes:
    - Dynamic descriptions with shortcodes
    - Time awareness
    - Party movement (followers auto-move with leader)
    
    Usage:
        from evennia import DefaultCharacter
        from typeclasses.mixins import GilderhaveCharacterMixin
        
        class Character(GilderhaveCharacterMixin, DefaultCharacter):
            pass
    """
    
    def at_after_move(self, source_location, **kwargs):
        """Called after a move has been performed."""
        super().at_after_move(source_location, **kwargs)
        
        # If party leader, move party members
        try:
            from world.parties import is_party_leader, party_move
            
            if is_party_leader(self):
                party_move(self, self.location)
        except ImportError:
            pass
    
    def is_in_party(self):
        """Check if character is in a party."""
        try:
            from world.parties import is_in_party
            return is_in_party(self)
        except ImportError:
            return False
    
    def is_party_leader(self):
        """Check if character is party leader."""
        try:
            from world.parties import is_party_leader
            return is_party_leader(self)
        except ImportError:
            return False
    
    def get_party(self):
        """Get character's party."""
        try:
            from world.parties import get_party
            return get_party(self)
        except ImportError:
            return None
    
    def is_in_combat(self):
        """Check if character is in combat."""
        try:
            from world.combat import is_in_combat
            return is_in_combat(self)
        except ImportError:
            return False
    
    def is_in_encounter(self):
        """Check if character is in an encounter."""
        try:
            from world.encounters import is_in_encounter
            return is_in_encounter(self)
        except ImportError:
            return False
