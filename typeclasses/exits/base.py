"""
Exit - Base

Exits connect rooms. This base class handles sensory properties,
grid positioning, and core traversal logic.

All exit types inherit from this.
"""

from evennia.objects.objects import DefaultExit
from evennia import AttributeProperty
from typeclasses.objects import ObjectParent


class Exit(ObjectParent, DefaultExit):
    """
    Base exit class.
    
    Handles:
        - Sensory properties (sight, sound, smell through exit)
        - Grid room positioning
        - Distance-based perception
        - Base traversal checks
    
    Inherit from this for all exit types.
    """
    
    # -------------------------------------------------------------------------
    # GRID LOCATION
    # -------------------------------------------------------------------------
    
    grid_location = AttributeProperty(default=None)  # (x, y) in grid rooms
    destination_grid_location = AttributeProperty(default=None)  # Where you arrive in destination
    
    # -------------------------------------------------------------------------
    # PHYSICAL PROPERTIES
    # -------------------------------------------------------------------------
    
    exit_size = AttributeProperty(default="large")  # tiny, small, medium, large, huge
    # Determines what can fit through without checks
    # tiny = mice, insects
    # small = cats, halflings crawling
    # medium = crouching human
    # large = standing human (default)
    # huge = carts, giants
    
    passage_type = AttributeProperty(default="walk")  # walk, step, climb, crawl, squeeze, swim, jump, fall
    passage_description = AttributeProperty(default="")  # "You push through the heavy door."
    arrival_description = AttributeProperty(default="")  # "The door creaks open and someone enters."
    
    # -------------------------------------------------------------------------
    # SENSORY - WHAT PASSES THROUGH THIS EXIT
    # -------------------------------------------------------------------------
    
    # From a distance (in grid rooms)
    visible_range = AttributeProperty(default=3)
    visible_description = AttributeProperty(default="")  # What it looks like from afar
    
    audible_range = AttributeProperty(default=0)  # 0 = silent
    sound_description = AttributeProperty(default="")
    
    smell_range = AttributeProperty(default=0)
    smell_description = AttributeProperty(default="")
    
    # Whether senses pass through to the other room
    transmits_sound = AttributeProperty(default=True)  # Can hear other room?
    transmits_smell = AttributeProperty(default=True)  # Can smell other room?
    transmits_light = AttributeProperty(default=True)  # Does light come through?
    sound_dampening = AttributeProperty(default=0.0)  # 0 = full, 1 = blocked
    
    # -------------------------------------------------------------------------
    # INTERACTION SOUNDS
    # What using this exit sounds like
    # -------------------------------------------------------------------------
    
    use_sound = AttributeProperty(default="")  # "Footsteps echo as you walk through."
    use_sound_others = AttributeProperty(default="")  # What room hears: "Footsteps approach."
    
    # -------------------------------------------------------------------------
    # DISTANCE PERCEPTION METHODS
    # -------------------------------------------------------------------------
    
    def get_distant_appearance(self, distance):
        """
        What this exit looks like from a distance.
        
        Args:
            distance: How many cells away the viewer is
            
        Returns:
            str: Description appropriate for distance
        """
        if distance > self.visible_range:
            return ""
        
        if distance == 0:
            return self.short_desc or self.key
        elif distance <= 2:
            return self.visible_description or self.short_desc or self.key
        else:
            return self.visible_description or f"something to the {self.key}"
    
    def get_sound_from_distance(self, distance):
        """What you hear from this exit at a distance."""
        if self.audible_range <= 0 or distance > self.audible_range:
            return ""
        return self.sound_description or ""
    
    def get_smell_from_distance(self, distance):
        """What you smell from this exit at a distance."""
        if self.smell_range <= 0 or distance > self.smell_range:
            return ""
        return self.smell_description or ""
    
    # -------------------------------------------------------------------------
    # TRAVERSAL CHECKS
    # -------------------------------------------------------------------------
    
    def can_traverse_from_position(self, character):
        """
        Check if character is at the right position to use this exit.
        """
        if self.grid_location is None:
            return (True, "")
        
        char_pos = character.db.grid_position
        if char_pos is None:
            return (True, "")
        
        ex, ey = self.grid_location
        cx, cy = char_pos
        distance = abs(ex - cx) + abs(ey - cy)
        
        if distance <= 1:
            return (True, "")
        else:
            return (False, f"You need to move closer to the {self.key} first.")
    
    def check_size(self, character):
        """
        Check if character can fit through this exit.
        
        Returns:
            tuple: (can_fit, requires_action, message)
        """
        char_size = character.db.size or "medium"
        
        size_order = ["tiny", "small", "medium", "large", "huge"]
        char_idx = size_order.index(char_size) if char_size in size_order else 2
        exit_idx = size_order.index(self.exit_size) if self.exit_size in size_order else 3
        
        if char_idx <= exit_idx:
            return (True, None, "")
        elif char_idx == exit_idx + 1:
            # One size larger - might squeeze through
            return (True, "squeeze", "You'll need to squeeze through.")
        else:
            return (False, None, "You're too large to fit through there.")
    
    def at_traverse(self, traversing_object, target_location, **kwargs):
        """
        Handle traversal with all checks.
        """
        # Check grid position
        can_go, msg = self.can_traverse_from_position(traversing_object)
        if not can_go:
            traversing_object.msg(msg)
            return
        
        # Check size
        can_fit, action_needed, fit_msg = self.check_size(traversing_object)
        if not can_fit:
            traversing_object.msg(fit_msg)
            return
        
        # -------------------------------------------------------------------------
        # FUTURE: Additional traversal checks
        # -------------------------------------------------------------------------
        
        # TODO: Check traversal type requirements
        # if self.passage_type != "walk":
        #     can_do, msg = self.check_traversal_ability(traversing_object)
        #     if not can_do:
        #         traversing_object.msg(msg)
        #         return
        #
        # System: TRAVERSAL_SYSTEM
        
        # Emit use sounds
        if self.use_sound:
            traversing_object.msg(self.use_sound)
        if self.use_sound_others:
            self.location.msg_contents(
                self.use_sound_others,
                exclude=[traversing_object]
            )
        
        # Do normal traversal
        super().at_traverse(traversing_object, target_location, **kwargs)
    
    def at_post_traverse(self, traversing_object, source_location, **kwargs):
        """
        After traversal - set position in destination.
        """
        super().at_post_traverse(traversing_object, source_location, **kwargs)
        
        # Set grid position in destination if applicable
        dest = traversing_object.location
        if dest and hasattr(dest, 'shape_type') and dest.shape_type:
            if self.destination_grid_location:
                traversing_object.db.grid_position = self.destination_grid_location
            else:
                # Default to room origin
                traversing_object.db.grid_position = (dest.x, dest.y)
        else:
            traversing_object.db.grid_position = None
        
        # Emit arrival sounds
        if self.arrival_description:
            dest.msg_contents(
                self.arrival_description,
                exclude=[traversing_object]
            )
    
    # -------------------------------------------------------------------------
    # FUTURE: PERCEIVE OTHER SIDE
    # -------------------------------------------------------------------------
    
    # TODO: Peek Through
    # def peek(self, character):
    #     """
    #     Character peeks through to see other side.
    #     
    #     Returns:
    #         str: Description of what they see
    #     
    #     System: PERCEPTION_SYSTEM
    #     """
    #     if not self.transmits_light:
    #         return "You can't see anything through there."
    #     # Get destination room's appearance, filtered
    #     pass
    
    # TODO: Listen Through
    # def listen(self, character):
    #     """
    #     Character listens at exit.
    #     
    #     System: PERCEPTION_SYSTEM, SOUND_SYSTEM
    #     """
    #     pass
    
    # TODO: Smell Through
    # def sniff(self, character):
    #     """
    #     Character smells at exit.
    #     
    #     System: PERCEPTION_SYSTEM, SMELL_SYSTEM
    #     """
    #     pass
