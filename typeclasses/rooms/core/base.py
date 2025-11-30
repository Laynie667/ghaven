"""
Room - Base

The foundational room class with shortcode processing.
All room types inherit from this.
"""

from evennia.objects.objects import DefaultRoom
from evennia import AttributeProperty
from evennia import search_object
from typeclasses.objects import ObjectParent
import re


class Room(ObjectParent, DefaultRoom):
    """
    Base room with shortcode processing.
    
    Shortcodes (use in room descriptions):
        <obj:key>      - injects object's short_desc
        <npc:key>      - injects npc's short_desc  
        <room:#dbref>  - injects room's short_desc (for exits, peeking)
        <sys:key>      - injects system content (weather, time, etc.)
    
    If the referenced thing doesn't exist or isn't present, 
    the shortcode is replaced with nothing (empty string).
    
    Inherits short_desc and shortcode_key from ObjectParent.
    """
    
    # -------------------------------------------------------------------------
    # SHORTCODE SYSTEM
    # Pattern matches <type:key> format
    # -------------------------------------------------------------------------
    
    shortcode_pattern = re.compile(r'<(obj|npc|room|sys):([^>]+)>')
    
    # -------------------------------------------------------------------------
    # REGION/ZONE SYSTEM
    # For grouping rooms and applying area-wide effects
    # -------------------------------------------------------------------------
    
    region = AttributeProperty(default="")  # "Darkwood Forest", "Castle Vorn"
    zone = AttributeProperty(default="")  # Sub-area within region
    zone_level = AttributeProperty(default=0)  # Suggested difficulty
    
    # -------------------------------------------------------------------------
    # FUTURE: FACTION SYSTEM
    # -------------------------------------------------------------------------
    
    # TODO: Faction Territory
    # faction_territory = AttributeProperty(default="")  # Who controls this area
    # faction_standing_required = AttributeProperty(default=0)  # Min rep to enter
    #
    # System: FACTION_SYSTEM
    
    # -------------------------------------------------------------------------
    # FUTURE: AMBIENT PROFILE SYSTEM
    # Instead of per-room messages, rooms reference ambient profiles
    # -------------------------------------------------------------------------
    
    # TODO: Ambient Profiles
    # ambient_profile = AttributeProperty(default="")  # "tavern", "forest", "dungeon"
    # ambient_enabled = AttributeProperty(default=True)
    #
    # Profiles will be defined in a central location and contain:
    # - Messages with chances and intervals
    # - Conditions (time, weather, room state)
    # - Content ratings for filtering
    #
    # System: AMBIENT_SYSTEM
    
    # -------------------------------------------------------------------------
    # FUTURE: ROOM STATE SYSTEM
    # Rooms can shift between states, changing descriptions and properties
    # -------------------------------------------------------------------------
    
    # TODO: Room States
    # room_states = AttributeProperty(default={})
    # current_state = AttributeProperty(default="default")
    #
    # Example states:
    # {
    #     "default": {"desc": "The tavern is quiet.", "lighting": "dim"},
    #     "busy": {"desc": "The tavern bustles.", "lighting": "bright"},
    #     "brawl": {"desc": "A fight has broken out!", "lighting": "bright"}
    # }
    #
    # def set_state(self, state_name):
    #     """Change room state, updating properties accordingly."""
    #     pass
    #
    # System: ROOM_STATE_SYSTEM
    
    # -------------------------------------------------------------------------
    # FUTURE: ENTRY REQUIREMENTS
    # Beyond locks - requirements based on character state
    # -------------------------------------------------------------------------
    
    # TODO: Entry Requirements
    # entry_requirements = AttributeProperty(default={})
    #
    # Example requirements:
    # {
    #     "light_source": True,       # Must have torch/lantern
    #     "swim_skill": 2,            # Minimum skill level
    #     "size": "small",            # Only small characters fit
    #     "key_item": "silver_key",   # Must possess item
    #     "faction_rep": {"guild": 10}  # Reputation check
    # }
    #
    # entry_fail_messages = AttributeProperty(default={})  # Custom fail messages
    #
    # def check_entry(self, character):
    #     """Check if character meets entry requirements."""
    #     pass
    #
    # System: ENTRY_SYSTEM
    
    # -------------------------------------------------------------------------
    # FUTURE: LINKED ROOMS
    # For multi-room spaces that share properties
    # -------------------------------------------------------------------------
    
    # TODO: Linked Rooms
    # linked_rooms = AttributeProperty(default=[])  # List of dbrefs
    # linked_properties = AttributeProperty(default=[])  # What syncs: ["lighting", "state"]
    #
    # def sync_linked_rooms(self, property_name, value):
    #     """Update a property across all linked rooms."""
    #     pass
    #
    # System: LINKED_ROOM_SYSTEM
    
    # -------------------------------------------------------------------------
    # FUTURE: PRIVACY & CONSENT
    # For adult content and scene management
    # -------------------------------------------------------------------------
    
    # TODO: Privacy System
    # is_private = AttributeProperty(default=False)  # Hide occupants from outside
    # is_lockable = AttributeProperty(default=False)  # Can be locked from inside
    # is_locked = AttributeProperty(default=False)  # Currently locked
    # no_teleport = AttributeProperty(default=False)  # Block teleport/summon
    # no_scry = AttributeProperty(default=False)  # Block magical viewing
    #
    # System: PRIVACY_SYSTEM
    
    # TODO: Adult Content
    # adult_only = AttributeProperty(default=False)  # Requires age verification
    # consent_type = AttributeProperty(default="ask")  # "ask", "open", "closed"
    # content_flags = AttributeProperty(default=[])  # ["sexual", "violence", "bondage"]
    #
    # System: CONSENT_SYSTEM, CONTENT_FILTER_SYSTEM
    
    # -------------------------------------------------------------------------
    # FUTURE: SCENE SYSTEM
    # For tracking RP scenes in progress
    # -------------------------------------------------------------------------
    
    # TODO: Scene Tracking
    # active_scene = AttributeProperty(default=None)
    #
    # Scene structure:
    # {
    #     "participants": ["#123", "#456"],
    #     "type": "private",  # private, open, closed
    #     "rating": "adult",  # sfw, mature, adult
    #     "started_at": timestamp,
    #     "summary": ""
    # }
    #
    # def start_scene(self, initiator, scene_type, rating):
    #     """Begin a new scene in this room."""
    #     pass
    #
    # def end_scene(self):
    #     """End the current scene."""
    #     pass
    #
    # System: SCENE_SYSTEM
    
    # -------------------------------------------------------------------------
    # FUTURE: ROOM AWARENESS
    # Properties that affect gameplay systems
    # -------------------------------------------------------------------------
    
    # TODO: Capacity & Crowding
    # capacity = AttributeProperty(default=0)  # 0 = unlimited
    # is_cramped = AttributeProperty(default=False)  # Affects combat, movement
    #
    # System: COMBAT_SYSTEM, MOVEMENT_SYSTEM
    
    # TODO: Visibility & Acoustics
    # visibility_range = AttributeProperty(default=1)  # How far can see
    # acoustics = AttributeProperty(default="normal")  # "echo", "muffled", "normal"
    # privacy_level = AttributeProperty(default="public")  # Affects eavesdropping
    #
    # System: STEALTH_SYSTEM, PERCEPTION_SYSTEM
    
    # TODO: Movement Costs
    # movement_cost = AttributeProperty(default=1)  # Stamina/effort to traverse
    # terrain_difficulty = AttributeProperty(default="normal")  # "easy", "rough", "climbing"
    #
    # System: MOVEMENT_SYSTEM, STAMINA_SYSTEM
    
    # -------------------------------------------------------------------------
    # FUTURE: HAZARDS
    # Environmental dangers
    # -------------------------------------------------------------------------
    
    # TODO: Hazard System
    # hazards = AttributeProperty(default=[])  # ["underwater", "toxic", "burning", "freezing"]
    # hazard_damage = AttributeProperty(default=0)  # Damage per tick
    # hazard_interval = AttributeProperty(default=60)  # Seconds between damage
    # hazard_message = AttributeProperty(default="")  # What player sees
    #
    # System: HAZARD_SYSTEM
    
    # -------------------------------------------------------------------------
    # FUTURE: EVENT HOOKS
    # Rooms react to game events
    # -------------------------------------------------------------------------
    
    # TODO: Combat Hooks
    # def at_combat_start(self, combatants):
    #     """
    #     Room reacts to combat starting.
    #     
    #     Returns False to prevent combat (sacred ground, etc.)
    #     
    #     System: COMBAT_SYSTEM
    #     """
    #     pass
    #
    # def at_combat_end(self, combatants, outcome):
    #     """Room reacts to combat ending."""
    #     pass
    
    # TODO: Magic Hooks
    # def at_magic_cast(self, caster, spell):
    #     """
    #     Room reacts to magic being cast.
    #     
    #     Returns False to prevent/fizzle magic (dead zones, etc.)
    #     
    #     System: MAGIC_SYSTEM
    #     """
    #     pass
    
    # TODO: Rest Hooks
    # def at_rest(self, character):
    #     """
    #     Character attempts to rest here.
    #     
    #     Returns False if resting isn't possible.
    #     
    #     System: REST_SYSTEM
    #     """
    #     pass
    
    # TODO: Death Hooks
    # def at_character_death(self, character, killer):
    #     """Room reacts to a death occurring here."""
    #     pass
    
    # -------------------------------------------------------------------------
    # FUTURE: FURNITURE TRACKING
    # Room knows what usable furniture it contains
    # -------------------------------------------------------------------------
    
    # TODO: Furniture Awareness
    # def get_furniture(self):
    #     """Return list of furniture objects in this room."""
    #     pass
    #
    # def get_available_furniture(self):
    #     """Return furniture that isn't fully occupied."""
    #     pass
    #
    # def get_occupied_furniture(self):
    #     """Return furniture with someone using it."""
    #     pass
    #
    # System: FURNITURE_SYSTEM
    
    # -------------------------------------------------------------------------
    # FUTURE: POSITION DISPLAY
    # Show character positions when looking
    # -------------------------------------------------------------------------
    
    # TODO: Position-Aware Character Display
    # Override get_display_characters to show positions/furniture use
    #
    # def get_display_characters(self, looker, **kwargs):
    #     """
    #     Show characters with their current positions.
    #     
    #     Example output:
    #       John is here, leaning against the wall.
    #       Mary is here, bound in the stocks.
    #       Bob is here.
    #     
    #     System: POSITION_SYSTEM, FURNITURE_SYSTEM
    #     """
    #     pass
    
    # =========================================================================
    # WORKING CODE - SHORTCODE PROCESSING
    # =========================================================================
    
    def process_shortcodes(self, text, looker):
        """
        Find shortcodes in text, replace with actual content.
        Missing stuff just disappears.
        
        Args:
            text (str): The text containing shortcodes
            looker: The object looking (usually a character)
            
        Returns:
            str: Text with shortcodes replaced
        """
        
        def replace_shortcode(match):
            code_type = match.group(1)  # obj, npc, room, sys
            code_key = match.group(2)   # the key or dbref
            
            if code_type == "obj":
                return self._get_obj_desc(code_key)
            elif code_type == "npc":
                return self._get_npc_desc(code_key)
            elif code_type == "room":
                return self._get_room_desc(code_key)
            elif code_type == "sys":
                return self._get_sys_desc(code_key, looker)
            
            return ""  # unknown type, skip it
        
        return self.shortcode_pattern.sub(replace_shortcode, text)
    
    def _get_obj_desc(self, key):
        """
        Find object in this room by shortcode_key, return its short_desc.
        
        Args:
            key (str): The shortcode_key to search for
            
        Returns:
            str: The object's short_desc, or empty string if not found
        """
        for obj in self.contents:
            # Skip characters and NPCs - they're not "objects"
            if obj.has_account or getattr(obj, 'is_npc', False):
                continue
            if obj.db.shortcode_key == key:
                return obj.db.short_desc or ""
        return ""
    
    def _get_npc_desc(self, key):
        """
        Find NPC in this room by shortcode_key, return its short_desc.
        
        Args:
            key (str): The shortcode_key to search for
            
        Returns:
            str: The NPC's short_desc, or empty string if not found
        """
        for obj in self.contents:
            if getattr(obj, 'is_npc', False):
                if obj.db.shortcode_key == key:
                    return obj.db.short_desc or ""
        return ""
    
    def _get_room_desc(self, dbref):
        """
        Find room by dbref, return its short_desc.
        
        Args:
            dbref (str): The dbref like "#123" or "123"
            
        Returns:
            str: The room's short_desc, or empty string if not found
        """
        dbref = dbref.lstrip('#')
        results = search_object(f"#{dbref}")
        if results:
            return results[0].db.short_desc or ""
        return ""
    
    def _get_sys_desc(self, key, looker):
        """
        System shortcodes for dynamic content.
        
        Override this method in child classes to add custom systems.
        
        Args:
            key (str): The system key (e.g., "weather", "time")
            looker: The object looking
            
        Returns:
            str: The system output, or empty string
        """
        # -------------------------------------------------------------------------
        # FUTURE: System shortcode handlers
        # -------------------------------------------------------------------------
        
        # TODO: Weather System
        # if key == "weather":
        #     return self._get_weather_desc(looker)
        #
        # System: WEATHER_SYSTEM
        
        # TODO: Time System
        # if key == "time":
        #     return self._get_time_desc(looker)
        # if key == "sky":
        #     return self._get_sky_desc(looker)
        #
        # System: TIME_SYSTEM
        
        # TODO: Graffiti/Writing System
        # if key.startswith("graffiti:"):
        #     surface = key.split(":")[1]
        #     return self._get_graffiti(surface)
        #
        # System: GRAFFITI_SYSTEM
        
        # TODO: Quest System
        # if key.startswith("quest:"):
        #     quest_id = key.split(":")[1]
        #     return self._get_quest_status(looker, quest_id)
        #
        # System: QUEST_SYSTEM
        
        return ""
    
    # -------------------------------------------------------------------------
    # FUTURE: CONDITIONAL SHORTCODES
    # Shortcodes that show/hide based on conditions
    # -------------------------------------------------------------------------
    
    # TODO: Conditional Shortcodes
    # These will be processed before regular shortcodes
    #
    # <lit:text> - only shows if lighting isn't dark
    # <dark:text> - only shows if lighting IS dark
    # <day:text> - only shows during daytime
    # <night:text> - only shows at night
    # <weather:rain:text> - only shows during specific weather
    # <state:busy:text> - only shows in specific room state
    # <has:silver_key:text> - only shows if looker has item
    #
    # conditional_pattern = re.compile(r'<(lit|dark|day|night):([^>]+)>')
    # weather_pattern = re.compile(r'<weather:(\w+):([^>]+)>')
    # state_pattern = re.compile(r'<state:(\w+):([^>]+)>')
    # has_pattern = re.compile(r'<has:(\w+):([^>]+)>')
    #
    # def process_conditionals(self, text, looker):
    #     """Process conditional shortcodes before regular ones."""
    #     pass
    #
    # System: CONDITIONAL_SHORTCODE_SYSTEM
    
    def return_appearance(self, looker, **kwargs):
        """
        Main method called when someone looks at this room.
        Processes shortcodes before returning the description.
        
        Args:
            looker: The object looking at this room
            **kwargs: Additional arguments passed through
            
        Returns:
            str: The processed room appearance
        """
        # -------------------------------------------------------------------------
        # FUTURE: Pre-processing hooks
        # -------------------------------------------------------------------------
        
        # TODO: Content filtering
        # Check looker's content preferences, filter/modify what they see
        #
        # System: CONTENT_FILTER_SYSTEM
        
        # TODO: Visibility check
        # If room is dark and looker has no light, show limited info
        #
        # System: LIGHTING_SYSTEM
        
        # TODO: Process conditional shortcodes first
        # text = self.process_conditionals(text, looker)
        #
        # System: CONDITIONAL_SHORTCODE_SYSTEM
        
        # Get the normal appearance from Evennia
        appearance = super().return_appearance(looker, **kwargs)
        
        # Run it through shortcode processor
        return self.process_shortcodes(appearance, looker)
