"""
Room Base
=========

Base room class that IndoorRoom and OutdoorRoom inherit from.

Update imports in indoor.py and outdoor.py:
    from .rooms import Room
"""

from typing import Dict, List, Optional
from random import choice, random

from evennia.objects.objects import DefaultRoom
from evennia import AttributeProperty


class Room(DefaultRoom):
    """
    Base room class for all locations.
    
    Provides:
    - Furniture management
    - NPC population
    - Partition system
    - Atmosphere/ambient system
    - Shortcode processing
    """
    
    # -------------------------------------------------------------------------
    # BASIC PROPERTIES
    # -------------------------------------------------------------------------
    
    short_desc = AttributeProperty(default="")
    is_private = AttributeProperty(default=False)
    is_public = AttributeProperty(default=True)
    room_type = AttributeProperty(default="generic")
    
    # -------------------------------------------------------------------------
    # FURNITURE SYSTEM
    # -------------------------------------------------------------------------
    
    furniture_list = AttributeProperty(default=list)
    
    def get_furniture(self) -> List:
        """Get all furniture objects in room."""
        from evennia.utils.search import search_object
        furniture = []
        for dbref in (self.furniture_list or []):
            try:
                results = search_object(dbref)
                if results:
                    furniture.append(results[0])
            except Exception:
                pass
        return furniture
    
    def add_furniture(self, obj):
        """Add furniture to room."""
        if not self.furniture_list:
            self.furniture_list = []
        if obj.dbref not in self.furniture_list:
            self.furniture_list.append(obj.dbref)
            obj.location = self
    
    def remove_furniture(self, obj):
        """Remove furniture from room."""
        if self.furniture_list and obj.dbref in self.furniture_list:
            self.furniture_list.remove(obj.dbref)
    
    def get_furniture_by_type(self, furniture_type: str) -> List:
        """Get furniture of a specific type."""
        furniture = self.get_furniture()
        return [f for f in furniture 
                if hasattr(f, 'furniture_type') and 
                (f.furniture_type == furniture_type or 
                 getattr(f.furniture_type, 'value', None) == furniture_type)]
    
    def get_available_furniture(self) -> List:
        """Get furniture with available slots."""
        return [f for f in self.get_furniture()
                if hasattr(f, 'has_available_slot') and f.has_available_slot()]
    
    # -------------------------------------------------------------------------
    # NPC SYSTEM
    # -------------------------------------------------------------------------
    
    npc_population_config = AttributeProperty(default=None)
    
    def get_npcs(self) -> List:
        """Get all NPCs in room."""
        return [obj for obj in self.contents 
                if hasattr(obj, 'db') and getattr(obj.db, 'npc_type', None)]
    
    def get_npcs_by_type(self, npc_type: str) -> List:
        """Get NPCs of a specific type."""
        return [npc for npc in self.get_npcs()
                if getattr(npc.db, 'npc_type', None) == npc_type]
    
    def get_characters(self) -> List:
        """Get all player characters in room."""
        return [obj for obj in self.contents
                if hasattr(obj, 'account') and obj.account]
    
    def get_all_occupants(self) -> List:
        """Get all characters and NPCs."""
        return self.get_characters() + self.get_npcs()
    
    def populate_room(self, force: bool = False):
        """Spawn NPCs based on population config."""
        config = self.npc_population_config
        if not config:
            return
        
        current_npcs = len(self.get_npcs())
        min_npcs = config.get("min_npcs", 0)
        max_npcs = config.get("max_npcs", 5)
        
        if not force and current_npcs >= min_npcs:
            return
        
        # TODO: Implement spawning based on templates
    
    # -------------------------------------------------------------------------
    # PARTITION SYSTEM
    # -------------------------------------------------------------------------
    
    partitions = AttributeProperty(default=dict)
    
    def add_partition(self, key: str, connected_dbref: str, 
                      partition_type: str = "wall", 
                      openings: List[str] = None):
        """Add a partition to another room."""
        if not self.partitions:
            self.partitions = {}
        self.partitions[key] = {
            "connected_room": connected_dbref,
            "type": partition_type,
            "openings": openings or [],
        }
    
    def get_partition(self, key: str) -> Optional[Dict]:
        """Get partition data by key."""
        return (self.partitions or {}).get(key)
    
    def get_characters_through_partition(self, partition_key: str) -> List:
        """Get characters visible through a partition opening."""
        partition = self.get_partition(partition_key)
        if not partition or not partition.get("openings"):
            return []
        
        try:
            from evennia.utils.search import search_object
            room = search_object(partition["connected_room"])
            if room:
                return room[0].get_characters()
        except Exception:
            pass
        return []
    
    # -------------------------------------------------------------------------
    # ATMOSPHERE SYSTEM
    # -------------------------------------------------------------------------
    
    atmosphere_preset = AttributeProperty(default=None)
    ambient_messages = AttributeProperty(default=list)
    ambient_frequency = AttributeProperty(default=0.1)
    scent = AttributeProperty(default="")
    sounds = AttributeProperty(default="")
    
    def apply_atmosphere(self, preset_key: str):
        """Apply an atmosphere preset to this room."""
        try:
            from .room_atmosphere import apply_preset_to_room
            return apply_preset_to_room(self, preset_key)
        except ImportError:
            self.atmosphere_preset = preset_key
            return False
    
    def get_ambient_message(self) -> Optional[str]:
        """Get a random ambient message."""
        messages = list(self.ambient_messages or [])
        
        if self.atmosphere_preset:
            try:
                from .room_atmosphere import ATMOSPHERE_PRESETS
                preset = ATMOSPHERE_PRESETS.get(self.atmosphere_preset)
                if preset:
                    messages.extend(preset.get("ambient_messages", []))
            except ImportError:
                pass
        
        return choice(messages) if messages else None
    
    def do_ambient_tick(self):
        """Called periodically to emit ambient messages."""
        if random() < self.ambient_frequency:
            msg = self.get_ambient_message()
            if msg:
                self.msg_contents(f"|x{msg}|n")
    
    def get_scent_description(self) -> str:
        """Get room scent description."""
        if self.scent:
            return f"The air smells of {self.scent}."
        return ""
    
    def get_sound_description(self) -> str:
        """Get room sound description."""
        if self.sounds:
            return f"You hear {self.sounds}."
        return ""
    
    # -------------------------------------------------------------------------
    # DESCRIPTION SYSTEM
    # -------------------------------------------------------------------------
    
    def return_appearance(self, looker, **kwargs):
        """Return room appearance with processed shortcodes."""
        desc = self.db.desc or ""
        desc = self._process_shortcodes(desc, looker)
        
        string = f"|c{self.key}|n\n{desc}"
        
        # Add atmosphere
        if self.scent:
            string += f"\n\n|xThe air smells of {self.scent}.|n"
        if self.sounds:
            string += f"\n|xYou hear {self.sounds}.|n"
        
        # Contents
        contents = self._get_contents_display(looker)
        if contents:
            string += f"\n\n{contents}"
        
        # Furniture
        furniture_display = self._get_furniture_display(looker)
        if furniture_display:
            string += f"\n\n{furniture_display}"
        
        # Exits
        exits = ", ".join(e.key for e in self.exits) or "None"
        string += f"\n\n|wExits:|n {exits}"
        
        return string
    
    def _process_shortcodes(self, text: str, looker) -> str:
        """Process shortcodes in description text."""
        import re
        pattern = r'<(\w+):([^>]+)>'
        
        def replace(m):
            code_type, key = m.group(1), m.group(2)
            
            if code_type == "obj":
                return self._get_obj_desc(key, looker)
            elif code_type == "sys":
                return self._get_sys_desc(key, looker)
            elif code_type == "cond":
                return self._get_cond_desc(key, looker)
            
            return m.group(0)
        
        return re.sub(pattern, replace, text)
    
    def _get_obj_desc(self, key: str, looker) -> str:
        """Get description for object shortcode."""
        for obj in self.contents:
            if getattr(obj, 'shortcode_key', None) == key:
                return getattr(obj.db, 'short_desc', None) or obj.key
        return f"[obj:{key}]"
    
    def _get_sys_desc(self, key: str, looker) -> str:
        """Get description for system shortcode."""
        # Override in subclasses for specific shortcodes
        return f"[sys:{key}]"
    
    def _get_cond_desc(self, key: str, looker) -> str:
        """Get description for conditional shortcode."""
        # Format: <cond:condition|true_text|false_text>
        parts = key.split("|")
        if len(parts) != 3:
            return ""
        
        condition, true_text, false_text = parts
        
        # Evaluate condition
        # TODO: Implement condition evaluation
        return true_text
    
    def _get_contents_display(self, looker) -> str:
        """Get display string for room contents."""
        chars = []
        for obj in self.contents:
            if obj == looker:
                continue
            if obj.dbref in (self.furniture_list or []):
                continue
            
            if hasattr(obj, 'body_data') or (hasattr(obj, 'account') and obj.account):
                pose = getattr(obj.db, 'pose', '')
                if pose:
                    chars.append(f"{obj.key} {pose}")
                else:
                    chars.append(f"{obj.key} is here")
        
        return ". ".join(chars) + "." if chars else ""
    
    def _get_furniture_display(self, looker) -> str:
        """Get display string for furniture."""
        furniture = self.get_furniture()
        if not furniture:
            return ""
        
        lines = []
        for f in furniture:
            # Get furniture description with occupants
            if hasattr(f, 'get_display_string'):
                lines.append(f.get_display_string())
            else:
                lines.append(f.key)
        
        return "\n".join(lines)
    
    # -------------------------------------------------------------------------
    # HOOKS
    # -------------------------------------------------------------------------
    
    def at_object_creation(self):
        """Called when room is created."""
        super().at_object_creation()
        
        # Apply atmosphere if preset set
        if self.atmosphere_preset:
            self.apply_atmosphere(self.atmosphere_preset)
    
    def at_object_receive(self, obj, source, **kwargs):
        """Called when object arrives in room."""
        super().at_object_receive(obj, source, **kwargs)
        
        # Populate NPCs if needed
        if hasattr(obj, 'account') and obj.account:
            self.populate_room()
        
        # Notify NPCs
        for npc in self.get_npcs():
            if hasattr(npc, 'on_character_arrives'):
                npc.on_character_arrives(obj)
    
    def at_object_leave(self, obj, target, **kwargs):
        """Called when object leaves room."""
        super().at_object_leave(obj, target, **kwargs)
        
        # Notify NPCs
        for npc in self.get_npcs():
            if hasattr(npc, 'on_character_leaves'):
                npc.on_character_leaves(obj, target)


__all__ = ["Room"]
