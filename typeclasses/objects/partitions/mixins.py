"""
Partition - Mixins

Mixins for partition behavior.

OpeningMixin - For partitions with holes/openings that allow body interaction
OperableMixin - For partitions that can open/close (windows, shutters)
"""

from evennia import AttributeProperty


class OpeningMixin:
    """
    Mixin for partitions with openings that allow physical interaction.
    
    Handles:
        - Opening properties (size, shape, height)
        - Body part exposure through opening
        - Interaction with exposed parts from other side
        - Anonymous interaction (can't see who's on other side)
    
    For adult content: glory holes, feeding slots, interaction windows.
    """
    
    # -------------------------------------------------------------------------
    # OPENING PROPERTIES
    # -------------------------------------------------------------------------
    
    has_opening = AttributeProperty(default=True)
    
    opening_size = AttributeProperty(default="small")  # tiny, small, medium, large
    opening_shape = AttributeProperty(default="round")  # round, square, slot, irregular
    opening_height = AttributeProperty(default="waist")  # floor, low, waist, chest, head
    
    opening_description = AttributeProperty(default="A small opening in the partition.")
    
    # What fits through
    opening_allows = AttributeProperty(default=[
        "hand", "fingers", "arm"
    ])
    # Possible parts: fingers, hand, arm, tongue, head, leg, foot, torso, etc.
    # Full list should match your body system
    
    # -------------------------------------------------------------------------
    # EXPOSURE TRACKING
    # -------------------------------------------------------------------------
    
    # Parts exposed FROM this side (visible/touchable from other side)
    exposed_parts = AttributeProperty(default={})
    # Format: {character_dbref: ["right_hand", "right_arm"], ...}
    
    # -------------------------------------------------------------------------
    # ANONYMITY
    # -------------------------------------------------------------------------
    
    is_anonymous = AttributeProperty(default=True)  # Can't tell who's on other side
    reveals_identity = AttributeProperty(default=[])  # Parts that reveal identity: ["face", "head"]
    
    # What you can tell about the other side
    can_sense_presence = AttributeProperty(default=True)  # Know someone's there?
    can_sense_gender = AttributeProperty(default=False)  # Can tell gender?
    
    # -------------------------------------------------------------------------
    # INTERACTION PROPERTIES
    # -------------------------------------------------------------------------
    
    allows_touch = AttributeProperty(default=True)
    allows_grab = AttributeProperty(default=True)  # Can grab exposed parts
    allows_restrain = AttributeProperty(default=False)  # Can hold parts in place
    
    # -------------------------------------------------------------------------
    # POSITION REQUIREMENTS
    # -------------------------------------------------------------------------
    
    requires_position = AttributeProperty(default="")  # Position needed to use: "standing", "kneeling"
    
    # -------------------------------------------------------------------------
    # EXPOSE BODY PART
    # -------------------------------------------------------------------------
    
    def can_expose_part(self, character, part_name):
        """
        Check if character can expose this body part.
        
        Args:
            character: Who wants to expose
            part_name: What body part
            
        Returns:
            tuple: (can_expose: bool, message: str)
        """
        # Check if part is allowed through this opening
        if part_name not in self.opening_allows:
            return (False, f"The opening is too small for that.")
        
        # Check position requirement
        if self.requires_position:
            char_pos = character.db.position or "standing"
            if char_pos != self.requires_position:
                return (False, f"You need to be {self.requires_position} to do that.")
        
        # Check if character is at the partition (grid rooms)
        if character.db.grid_position and self.db.grid_position:
            cx, cy = character.db.grid_position
            px, py = self.db.grid_position
            if abs(cx - px) + abs(cy - py) > 1:
                return (False, "You need to move closer.")
        
        # -------------------------------------------------------------------------
        # FUTURE: Body system checks
        # -------------------------------------------------------------------------
        
        # TODO: Check if part exists on character
        # if not character.has_body_part(part_name):
        #     return (False, "You don't have that body part.")
        #
        # System: BODY_SYSTEM
        
        # TODO: Check if part is free (not restrained, not already exposed elsewhere)
        # if character.is_part_restrained(part_name):
        #     return (False, f"Your {part_name} is restrained.")
        #
        # System: RESTRAINT_SYSTEM
        
        # TODO: Check clothing
        # if character.is_part_covered(part_name):
        #     return (False, f"Your {part_name} is covered by clothing.")
        #
        # System: CLOTHING_SYSTEM
        
        return (True, "")
    
    def expose_part(self, character, part_name):
        """
        Expose a body part through the opening.
        
        Args:
            character: Who's exposing
            part_name: What body part
            
        Returns:
            tuple: (success: bool, message: str)
        """
        can_do, msg = self.can_expose_part(character, part_name)
        if not can_do:
            return (False, msg)
        
        # Track exposure
        char_id = character.dbref
        exposed = dict(self.exposed_parts)
        
        if char_id not in exposed:
            exposed[char_id] = []
        
        if part_name not in exposed[char_id]:
            exposed[char_id].append(part_name)
        
        self.exposed_parts = exposed
        
        # Messages
        character.msg(f"You extend your {part_name} through the {self.key}.")
        
        # Notify other side
        other_room = self.get_other_room()
        partner = self.get_partner()
        if other_room and partner:
            part_desc = self._get_exposed_part_description(character, part_name)
            other_room.msg_contents(f"{part_desc} extends through the {partner.key}.")
        
        # -------------------------------------------------------------------------
        # FUTURE: Set character state
        # -------------------------------------------------------------------------
        
        # TODO: Track on character that part is exposed
        # character.set_part_state(part_name, "exposed", at=self)
        #
        # System: BODY_SYSTEM
        
        return (True, "")
    
    def withdraw_part(self, character, part_name):
        """
        Withdraw an exposed body part.
        
        Args:
            character: Who's withdrawing
            part_name: What body part
            
        Returns:
            tuple: (success: bool, message: str)
        """
        char_id = character.dbref
        exposed = dict(self.exposed_parts)
        
        if char_id not in exposed or part_name not in exposed[char_id]:
            return (False, "You don't have that exposed.")
        
        # Check if held/restrained from other side
        # -------------------------------------------------------------------------
        # FUTURE: Check if part is held
        # -------------------------------------------------------------------------
        
        # TODO: Check if someone has grabbed this part
        # if self.is_part_held(char_id, part_name):
        #     return (False, "You can't pull back - someone has hold of you!")
        #
        # System: RESTRAINT_SYSTEM
        
        # Remove from tracking
        exposed[char_id].remove(part_name)
        if not exposed[char_id]:
            del exposed[char_id]
        self.exposed_parts = exposed
        
        # Messages
        character.msg(f"You withdraw your {part_name}.")
        
        other_room = self.get_other_room()
        partner = self.get_partner()
        if other_room and partner:
            other_room.msg_contents(f"A {part_name} withdraws from the {partner.key}.")
        
        return (True, "")
    
    def withdraw_all(self, character):
        """
        Withdraw all exposed parts.
        """
        char_id = character.dbref
        exposed = dict(self.exposed_parts)
        
        if char_id not in exposed:
            return (False, "You don't have anything exposed.")
        
        # TODO: Check each part isn't held
        
        del exposed[char_id]
        self.exposed_parts = exposed
        
        character.msg("You withdraw completely.")
        
        return (True, "")
    
    # -------------------------------------------------------------------------
    # GET EXPOSED PARTS
    # -------------------------------------------------------------------------
    
    def get_exposed_from_this_side(self):
        """
        Get parts exposed from this side (visible from OTHER side).
        
        Returns:
            dict: {character_dbref: [parts], ...}
        """
        return dict(self.exposed_parts)
    
    def get_exposed_from_other_side(self):
        """
        Get parts coming through from other side (visible HERE).
        
        Returns:
            dict: {character_dbref: [parts], ...}
        """
        partner = self.get_partner()
        if partner and hasattr(partner, 'exposed_parts'):
            return dict(partner.exposed_parts)
        return {}
    
    # -------------------------------------------------------------------------
    # DESCRIBE EXPOSED PARTS
    # -------------------------------------------------------------------------
    
    def _get_exposed_part_description(self, character, part_name):
        """
        Get anonymous or identified description of exposed part.
        """
        if not self.is_anonymous:
            return f"{character.key}'s {part_name}"
        
        if part_name in self.reveals_identity:
            return f"{character.key}'s {part_name}"
        
        # Anonymous description based on what can be sensed
        # -------------------------------------------------------------------------
        # FUTURE: Better anonymous descriptions
        # -------------------------------------------------------------------------
        
        # TODO: Base description on visible characteristics
        # skin_tone = character.get_skin_tone()
        # size = character.get_part_size(part_name)
        # return f"A {size} {skin_tone} {part_name}"
        #
        # System: BODY_SYSTEM
        
        return f"A {part_name}"
    
    def get_visible_parts_description(self, looker):
        """
        Describe what's coming through from the other side.
        
        Args:
            looker: Who's looking
            
        Returns:
            str: Description of visible exposed parts
        """
        exposed = self.get_exposed_from_other_side()
        if not exposed:
            return ""
        
        descriptions = []
        for char_id, parts in exposed.items():
            char = search_object(char_id)
            char = char[0] if char else None
            
            for part in parts:
                if char:
                    desc = self._get_exposed_part_description(char, part)
                else:
                    desc = f"A {part}"
                descriptions.append(desc)
        
        if not descriptions:
            return ""
        
        if len(descriptions) == 1:
            return f"{descriptions[0]} extends through the opening."
        else:
            return f"Through the opening: {', '.join(descriptions)}."
    
    # -------------------------------------------------------------------------
    # INTERACT WITH EXPOSED PARTS
    # -------------------------------------------------------------------------
    
    def interact_with_part(self, character, part_owner_id, part_name, action):
        """
        Interact with an exposed body part from the other side.
        
        Args:
            character: Who's interacting
            part_owner_id: dbref of who owns the part
            part_name: Which body part
            action: "touch", "grab", "stroke", "hold", "release", etc.
            
        Returns:
            tuple: (success: bool, message: str)
        """
        # Check part is actually exposed here
        exposed = self.get_exposed_from_other_side()
        if part_owner_id not in exposed or part_name not in exposed[part_owner_id]:
            return (False, "That's not there.")
        
        # Get the part owner
        owner = search_object(part_owner_id)
        owner = owner[0] if owner else None
        if not owner:
            return (False, "They seem to have left.")
        
        # -------------------------------------------------------------------------
        # FUTURE: Consent check
        # -------------------------------------------------------------------------
        
        # TODO: Check consent
        # if not self.check_consent(character, owner, action, part_name):
        #     return (False, "You don't have consent for that.")
        #
        # System: CONSENT_SYSTEM
        
        # Handle action
        if action == "touch":
            if not self.allows_touch:
                return (False, "You can't reach through.")
            
            character.msg(f"You touch the {part_name}.")
            owner.msg(f"Someone touches your {part_name} from the other side of the {self.key}.")
            return (True, "")
        
        elif action == "grab":
            if not self.allows_grab:
                return (False, "You can't grab through there.")
            
            # TODO: Track grab state
            character.msg(f"You grab the {part_name}.")
            owner.msg(f"Someone grabs your {part_name}! You can't pull back.")
            return (True, "")
        
        elif action == "release":
            # TODO: Release grabbed part
            character.msg(f"You release the {part_name}.")
            owner.msg(f"The grip on your {part_name} releases.")
            return (True, "")
        
        # -------------------------------------------------------------------------
        # FUTURE: More interaction types
        # -------------------------------------------------------------------------
        
        # TODO: Full range of interactions
        # - stroke, caress, pinch, squeeze, lick, kiss, etc.
        # - Each should trigger appropriate messages
        # - Some may require consent
        # - Some may affect body state
        #
        # System: INTERACTION_SYSTEM, CONSENT_SYSTEM
        
        return (False, "You're not sure how to do that.")
    
    # -------------------------------------------------------------------------
    # SENSING PRESENCE
    # -------------------------------------------------------------------------
    
    def sense_other_side(self, character):
        """
        Try to sense who/what is on the other side.
        
        Returns:
            str: Description of what can be sensed
        """
        other_room = self.get_other_room()
        partner = self.get_partner()
        
        if not other_room or not partner:
            return "You sense nothing."
        
        parts = []
        
        # Is anyone there?
        if self.can_sense_presence:
            occupants = [obj for obj in other_room.contents if obj.has_account]
            if occupants:
                parts.append(f"Someone is on the other side.")
            else:
                parts.append("No one seems to be there.")
        
        # Exposed parts visible
        exposed_desc = self.get_visible_parts_description(character)
        if exposed_desc:
            parts.append(exposed_desc)
        
        return " ".join(parts)
    
    # -------------------------------------------------------------------------
    # APPEARANCE
    # -------------------------------------------------------------------------
    
    def return_appearance(self, looker, **kwargs):
        """
        Show partition with opening details and exposed parts.
        """
        base = super().return_appearance(looker, **kwargs)
        
        parts = [base]
        
        # Opening description
        if self.has_opening:
            parts.append(self.opening_description)
        
        # What's exposed from other side
        exposed_desc = self.get_visible_parts_description(looker)
        if exposed_desc:
            parts.append(exposed_desc)
        
        return "\n".join(parts)


class OperableMixin:
    """
    Mixin for partitions that can be opened/closed.
    
    For: Windows, shutters, hatches that aren't traversable.
    """
    
    # -------------------------------------------------------------------------
    # STATE
    # -------------------------------------------------------------------------
    
    is_operable = AttributeProperty(default=True)
    current_state = AttributeProperty(default="closed")  # open, closed, locked, broken
    
    is_lockable = AttributeProperty(default=False)
    key_item = AttributeProperty(default="")
    
    # -------------------------------------------------------------------------
    # STATE-DEPENDENT TRANSMISSION
    # -------------------------------------------------------------------------
    
    # What changes when opened
    open_transmits_sight = AttributeProperty(default=True)
    open_transmits_sound = AttributeProperty(default=True)
    open_transmits_smell = AttributeProperty(default=True)
    
    closed_transmits_sight = AttributeProperty(default=False)
    closed_transmits_sound = AttributeProperty(default=True)  # Muffled
    closed_transmits_smell = AttributeProperty(default=False)
    
    @property
    def transmits_sight(self):
        if self.current_state == "open":
            return self.open_transmits_sight
        return self.closed_transmits_sight
    
    @property
    def transmits_sound(self):
        if self.current_state == "open":
            return self.open_transmits_sound
        return self.closed_transmits_sound
    
    @property
    def transmits_smell(self):
        if self.current_state == "open":
            return self.open_transmits_smell
        return self.closed_transmits_smell
    
    # -------------------------------------------------------------------------
    # SOUNDS
    # -------------------------------------------------------------------------
    
    open_sound = AttributeProperty(default="It opens.")
    close_sound = AttributeProperty(default="It closes.")
    lock_sound = AttributeProperty(default="Click.")
    unlock_sound = AttributeProperty(default="Click.")
    
    # -------------------------------------------------------------------------
    # DESCRIPTIONS
    # -------------------------------------------------------------------------
    
    desc_open = AttributeProperty(default="")
    desc_closed = AttributeProperty(default="")
    desc_locked = AttributeProperty(default="")
    
    # -------------------------------------------------------------------------
    # ACTIONS
    # -------------------------------------------------------------------------
    
    def do_open(self, character):
        """Open the partition."""
        if self.current_state == "open":
            return (False, "It's already open.")
        if self.current_state == "locked":
            return (False, "It's locked.")
        if self.current_state == "broken":
            return (True, "It's broken open.")
        
        self.current_state = "open"
        
        # Notify both sides
        if self.open_sound:
            self.location.msg_contents(self.open_sound)
        other_room = self.get_other_room()
        if other_room:
            other_room.msg_contents(self.open_sound)
        
        # Sync with partner
        partner = self.get_partner()
        if partner and hasattr(partner, 'current_state'):
            partner.current_state = "open"
        
        return (True, "You open it.")
    
    def do_close(self, character):
        """Close the partition."""
        if self.current_state == "closed":
            return (False, "It's already closed.")
        if self.current_state == "locked":
            return (False, "It's already closed and locked.")
        if self.current_state == "broken":
            return (False, "It's too broken to close.")
        
        self.current_state = "closed"
        
        if self.close_sound:
            self.location.msg_contents(self.close_sound)
        other_room = self.get_other_room()
        if other_room:
            other_room.msg_contents(self.close_sound)
        
        partner = self.get_partner()
        if partner and hasattr(partner, 'current_state'):
            partner.current_state = "closed"
        
        return (True, "You close it.")
    
    def do_lock(self, character):
        """Lock the partition."""
        if not self.is_lockable:
            return (False, "It can't be locked.")
        if self.current_state == "locked":
            return (False, "It's already locked.")
        if self.current_state != "closed":
            return (False, "Close it first.")
        
        # Check key
        if self.key_item:
            has_key = any(
                obj.db.shortcode_key == self.key_item 
                for obj in character.contents
            )
            if not has_key:
                return (False, "You don't have the key.")
        
        self.current_state = "locked"
        
        if self.lock_sound:
            character.msg(self.lock_sound)
        
        partner = self.get_partner()
        if partner and hasattr(partner, 'current_state'):
            partner.current_state = "locked"
        
        return (True, "You lock it.")
    
    def do_unlock(self, character):
        """Unlock the partition."""
        if self.current_state != "locked":
            return (False, "It's not locked.")
        
        # Check key
        if self.key_item:
            has_key = any(
                obj.db.shortcode_key == self.key_item 
                for obj in character.contents
            )
            if not has_key:
                return (False, "You don't have the key.")
        
        self.current_state = "closed"
        
        if self.unlock_sound:
            character.msg(self.unlock_sound)
        
        partner = self.get_partner()
        if partner and hasattr(partner, 'current_state'):
            partner.current_state = "closed"
        
        return (True, "You unlock it.")
    
    def return_appearance(self, looker, **kwargs):
        """Show state-appropriate description."""
        base = super().return_appearance(looker, **kwargs)
        
        state_desc = {
            "open": self.desc_open,
            "closed": self.desc_closed,
            "locked": self.desc_locked or self.desc_closed,
        }.get(self.current_state, "")
        
        if state_desc:
            return f"{base}\n{state_desc}"
        return base
