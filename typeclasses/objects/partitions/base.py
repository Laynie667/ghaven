"""
Partition - Base

Partitions are objects that connect two rooms WITHOUT being traversable exits.
They allow interaction between rooms: sight, sound, smell, passing items,
and potentially body parts through openings.

Each partition has a "partner" in the connected room. They stay in sync.
"""

from evennia import AttributeProperty
from evennia import search_object
from typeclasses.objects import Object


class Partition(Object):
    """
    Base partition class.
    
    A partition:
        - Exists in a room as an object
        - Has a partner partition in another room
        - Allows some senses to pass through (configurable)
        - May allow items to pass through
        - May have openings for interaction
    
    Not traversable - use Exit for that.
    """
    
    # -------------------------------------------------------------------------
    # PARTNER LINK
    # -------------------------------------------------------------------------
    
    partner_dbref = AttributeProperty(default=None)  # dbref of partner partition
    
    def get_partner(self):
        """Get the partner partition object."""
        if not self.partner_dbref:
            return None
        results = search_object(self.partner_dbref)
        return results[0] if results else None
    
    def get_other_room(self):
        """Get the room on the other side."""
        partner = self.get_partner()
        return partner.location if partner else None
    
    # -------------------------------------------------------------------------
    # PHYSICAL PROPERTIES
    # -------------------------------------------------------------------------
    
    partition_material = AttributeProperty(default="wood")
    partition_thickness = AttributeProperty(default="normal")  # thin, normal, thick
    partition_height = AttributeProperty(default="full")  # partial, full, low
    
    # Visual properties
    is_opaque = AttributeProperty(default=True)  # Can't see through
    has_gaps = AttributeProperty(default=False)  # Small gaps/cracks
    
    # -------------------------------------------------------------------------
    # SENSORY TRANSMISSION
    # What passes through this partition
    # -------------------------------------------------------------------------
    
    transmits_sight = AttributeProperty(default=False)  # Can see through?
    transmits_sound = AttributeProperty(default=True)  # Can hear through?
    transmits_smell = AttributeProperty(default=False)  # Can smell through?
    
    sound_quality = AttributeProperty(default="muffled")  # clear, muffled, faint
    
    # -------------------------------------------------------------------------
    # DESCRIPTIONS
    # -------------------------------------------------------------------------
    
    this_side_desc = AttributeProperty(default="")  # What it looks like from this side
    other_side_hint = AttributeProperty(default="")  # Hint about other side: "Sounds come from beyond."
    
    # -------------------------------------------------------------------------
    # PERCEIVE OTHER SIDE
    # -------------------------------------------------------------------------
    
    def get_other_side_description(self, looker):
        """
        What can be perceived of the other side.
        
        Returns:
            str: Description based on what transmits through
        """
        other_room = self.get_other_room()
        if not other_room:
            return ""
        
        parts = []
        
        if self.transmits_sight:
            # Can see the other room
            parts.append(f"Through the {self.key}, you see {other_room.key}.")
            # TODO: Get limited appearance of other room
        
        if self.transmits_sound:
            # Can hear sounds
            quality = {
                "clear": "You can hear clearly from the other side.",
                "muffled": "Muffled sounds come from the other side.",
                "faint": "Faint sounds drift from beyond.",
            }.get(self.sound_quality, "")
            if quality:
                parts.append(quality)
            
            # TODO: Get actual sounds from other room
            # System: SOUND_SYSTEM
        
        if self.transmits_smell:
            # Can smell other room
            # TODO: Get smells from other room
            # System: SMELL_SYSTEM
            pass
        
        return " ".join(parts)
    
    # -------------------------------------------------------------------------
    # COMMUNICATION THROUGH PARTITION
    # -------------------------------------------------------------------------
    
    def transmit_message(self, sender, message, msg_type="say"):
        """
        Send a message through to the other side.
        
        Args:
            sender: Who's speaking/acting
            message: The message content
            msg_type: "say", "whisper", "shout", "knock", etc.
        """
        other_room = self.get_other_room()
        partner = self.get_partner()
        
        if not other_room or not partner:
            return
        
        if not self.transmits_sound:
            return
        
        # Format based on quality and type
        if msg_type == "whisper":
            if self.sound_quality == "clear":
                output = f"A whisper comes through the {partner.key}: \"{message}\""
            elif self.sound_quality == "muffled":
                output = f"A faint whisper comes through the {partner.key}."
            else:
                return  # Too faint
        
        elif msg_type == "shout":
            if self.sound_quality in ("clear", "muffled"):
                output = f"A shout comes through the {partner.key}: \"{message}\""
            else:
                output = f"A muffled shout comes from beyond the {partner.key}."
        
        elif msg_type == "knock":
            output = f"Someone knocks on the {partner.key}."
        
        else:  # say
            if self.sound_quality == "clear":
                output = f"From beyond the {partner.key}, you hear: \"{message}\""
            elif self.sound_quality == "muffled":
                output = f"Muffled speech comes from beyond the {partner.key}."
            else:
                output = f"Faint sounds come from beyond the {partner.key}."
        
        other_room.msg_contents(output)
    
    def do_knock(self, character):
        """
        Knock on the partition.
        """
        # This side
        self.location.msg_contents(f"{character.key} knocks on the {self.key}.")
        
        # Other side
        self.transmit_message(character, "", msg_type="knock")
        
        return (True, "You knock.")
    
    # -------------------------------------------------------------------------
    # ITEM PASSING
    # -------------------------------------------------------------------------
    
    allows_items = AttributeProperty(default=False)  # Can pass items through?
    item_size_limit = AttributeProperty(default="small")  # Max size that fits
    
    def pass_item(self, character, item):
        """
        Pass an item through to the other side.
        
        Args:
            character: Who's passing the item
            item: The item object
            
        Returns:
            tuple: (success: bool, message: str)
        """
        if not self.allows_items:
            return (False, "You can't pass anything through there.")
        
        # Check size
        item_size = item.db.size or "medium"
        size_order = ["tiny", "small", "medium", "large", "huge"]
        
        item_idx = size_order.index(item_size) if item_size in size_order else 2
        limit_idx = size_order.index(self.item_size_limit) if self.item_size_limit in size_order else 1
        
        if item_idx > limit_idx:
            return (False, f"The {item.key} is too large to fit through.")
        
        # Get other room
        other_room = self.get_other_room()
        partner = self.get_partner()
        
        if not other_room:
            return (False, "There's nothing on the other side.")
        
        # Move item
        item.move_to(other_room, quiet=True)
        
        # Messages
        character.msg(f"You pass the {item.key} through the {self.key}.")
        self.location.msg_contents(
            f"{character.key} passes something through the {self.key}.",
            exclude=[character]
        )
        other_room.msg_contents(
            f"A {item.key} comes through from the {partner.key}."
        )
        
        return (True, "")
    
    # -------------------------------------------------------------------------
    # FUTURE: STATE SYNC WITH PARTNER
    # -------------------------------------------------------------------------
    
    # TODO: Keep partner in sync
    # def sync_with_partner(self, property_name, value):
    #     """
    #     Sync a property change with partner partition.
    #     
    #     System: PARTITION_SYSTEM
    #     """
    #     partner = self.get_partner()
    #     if partner:
    #         setattr(partner.db, property_name, value)
    
    # -------------------------------------------------------------------------
    # APPEARANCE
    # -------------------------------------------------------------------------
    
    def return_appearance(self, looker, **kwargs):
        """
        Show partition with info about other side.
        """
        base = super().return_appearance(looker, **kwargs)
        
        # Add other side info
        other_side = self.get_other_side_description(looker)
        if other_side:
            base = f"{base}\n{other_side}"
        
        return base
