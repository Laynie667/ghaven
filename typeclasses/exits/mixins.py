"""
Exit - Mixins

Mixins that add specific behaviors to exits.
Combine these to create complex exit types.

Example:
    class SecretTrapdoor(DoorMixin, SecretMixin, TrapMixin, Exit):
        pass
"""

from evennia import AttributeProperty


class DoorMixin:
    """
    Mixin for exits that can be opened, closed, and locked.
    
    Adds:
        - Door states (open, closed, locked, jammed, broken, barricaded)
        - Key/lock system
        - Physical properties affecting interaction
        - State-dependent sensory transmission
    """
    
    # -------------------------------------------------------------------------
    # DOOR STATE
    # -------------------------------------------------------------------------
    
    door_state = AttributeProperty(default="open")
    # States:
    # - open: Can traverse, senses pass through
    # - closed: Cannot traverse, senses partially blocked
    # - locked: Cannot traverse, requires key/pick
    # - jammed: Cannot traverse, requires force
    # - broken: Always open, cannot close
    # - barricaded: Cannot traverse, requires removal
    
    # -------------------------------------------------------------------------
    # PHYSICAL PROPERTIES
    # -------------------------------------------------------------------------
    
    door_material = AttributeProperty(default="wood")  # wood, iron, stone, bars, fabric
    door_thickness = AttributeProperty(default="normal")  # thin, normal, thick, reinforced
    door_weight = AttributeProperty(default="normal")  # light, normal, heavy, massive
    
    # How these affect interactions:
    # - Material affects: sound transmission, break difficulty, lock type
    # - Thickness affects: sound dampening, strength
    # - Weight affects: open/close speed, slam damage, noise
    
    is_double_door = AttributeProperty(default=False)  # Two doors that open together
    opens_direction = AttributeProperty(default="push")  # push, pull, slide, swing
    
    # -------------------------------------------------------------------------
    # LOCK SYSTEM
    # -------------------------------------------------------------------------
    
    is_lockable = AttributeProperty(default=True)
    key_item = AttributeProperty(default="")  # shortcode_key of key
    lock_difficulty = AttributeProperty(default=5)  # DC for lockpicking
    lock_type = AttributeProperty(default="key")  # key, combination, magical, puzzle
    
    # -------------------------------------------------------------------------
    # DURABILITY
    # -------------------------------------------------------------------------
    
    door_hp = AttributeProperty(default=20)  # For bashing
    door_max_hp = AttributeProperty(default=20)
    bash_difficulty = AttributeProperty(default=10)  # DC for bashing
    
    # -------------------------------------------------------------------------
    # AUTO BEHAVIOR
    # -------------------------------------------------------------------------
    
    auto_close = AttributeProperty(default=False)  # Closes after use
    auto_close_delay = AttributeProperty(default=30)  # Seconds before auto-close
    auto_lock = AttributeProperty(default=False)  # Locks when closed
    
    # -------------------------------------------------------------------------
    # SOUNDS
    # -------------------------------------------------------------------------
    
    open_sound = AttributeProperty(default="The door opens.")
    close_sound = AttributeProperty(default="The door closes.")
    lock_sound = AttributeProperty(default="Click.")
    unlock_sound = AttributeProperty(default="Click.")
    knock_sound = AttributeProperty(default="Knock knock.")
    rattle_sound = AttributeProperty(default="The door rattles but doesn't open.")
    bash_sound = AttributeProperty(default="THUD!")
    break_sound = AttributeProperty(default="CRASH! The door splinters!")
    creak_sound = AttributeProperty(default="")  # Creeeeak (if set, plays on open)
    slam_sound = AttributeProperty(default="SLAM!")  # If closed forcefully
    
    # -------------------------------------------------------------------------
    # STATE-DEPENDENT DESCRIPTIONS
    # -------------------------------------------------------------------------
    
    desc_open = AttributeProperty(default="")  # "An open doorway."
    desc_closed = AttributeProperty(default="")  # "A closed wooden door."
    desc_locked = AttributeProperty(default="")  # "A locked door."
    desc_broken = AttributeProperty(default="")  # "A splintered doorframe."
    desc_barricaded = AttributeProperty(default="")  # "Furniture blocks the door."
    
    # -------------------------------------------------------------------------
    # STATE-DEPENDENT SENSORY TRANSMISSION
    # -------------------------------------------------------------------------
    
    def get_sound_dampening(self):
        """Calculate how much sound is blocked based on state and material."""
        if self.door_state in ("open", "broken"):
            return 0.0  # Full sound
        
        base_dampening = {
            "fabric": 0.1,
            "wood": 0.4,
            "iron": 0.7,
            "stone": 0.9,
            "bars": 0.1,
        }.get(self.door_material, 0.4)
        
        thickness_mod = {
            "thin": -0.1,
            "normal": 0.0,
            "thick": 0.2,
            "reinforced": 0.3,
        }.get(self.door_thickness, 0.0)
        
        return min(1.0, base_dampening + thickness_mod)
    
    def blocks_sight(self):
        """Whether you can see through."""
        if self.door_state in ("open", "broken"):
            return False
        if self.door_material == "bars":
            return False  # Can see through bars
        return True
    
    def blocks_smell(self):
        """Whether smells pass through."""
        if self.door_state in ("open", "broken"):
            return False
        return self.door_material not in ("bars", "fabric")
    
    # -------------------------------------------------------------------------
    # DOOR ACTIONS
    # -------------------------------------------------------------------------
    
    def do_open(self, character, force=False):
        """
        Attempt to open the door.
        
        Args:
            character: Who's opening
            force: Whether to force (slam) open
            
        Returns:
            tuple: (success: bool, message: str)
        """
        if self.door_state == "open":
            return (False, "It's already open.")
        
        if self.door_state == "locked":
            return (False, self.rattle_sound or "It's locked.")
        
        if self.door_state == "jammed":
            if force:
                # TODO: Strength check
                pass
            return (False, "It's stuck.")
        
        if self.door_state == "barricaded":
            return (False, "Something is blocking it from the other side.")
        
        if self.door_state == "broken":
            return (True, "It's already broken open.")
        
        # Open it
        self.door_state = "open"
        
        sound = self.open_sound
        if self.creak_sound:
            sound = f"{self.creak_sound} {sound}"
        if force and self.slam_sound:
            sound = self.slam_sound
        
        # Notify both rooms
        if self.location:
            self.location.msg_contents(sound)
        if self.destination:
            self.destination.msg_contents(sound)
        
        # -------------------------------------------------------------------------
        # FUTURE: Auto-close timer
        # -------------------------------------------------------------------------
        
        # TODO: Start auto-close timer
        # if self.auto_close:
        #     # Schedule close
        #     pass
        #
        # System: TIMER_SYSTEM
        
        return (True, "")
    
    def do_close(self, character, force=False):
        """
        Attempt to close the door.
        """
        if self.door_state == "closed" or self.door_state == "locked":
            return (False, "It's already closed.")
        
        if self.door_state == "broken":
            return (False, "It's too damaged to close.")
        
        if self.door_state != "open":
            return (False, "You can't close it.")
        
        self.door_state = "closed"
        
        sound = self.slam_sound if force else self.close_sound
        
        if self.location:
            self.location.msg_contents(sound)
        if self.destination:
            self.destination.msg_contents(sound)
        
        # -------------------------------------------------------------------------
        # FUTURE: Auto-lock
        # -------------------------------------------------------------------------
        
        # TODO: Auto-lock
        # if self.auto_lock:
        #     self.door_state = "locked"
        #     # Play lock sound
        #
        # System: DOOR_SYSTEM
        
        return (True, "")
    
    def do_lock(self, character):
        """
        Attempt to lock the door.
        """
        if not self.is_lockable:
            return (False, "It can't be locked.")
        
        if self.door_state == "locked":
            return (False, "It's already locked.")
        
        if self.door_state != "closed":
            return (False, "You need to close it first.")
        
        # Check for key
        if self.key_item:
            has_key = False
            for obj in character.contents:
                if obj.db.shortcode_key == self.key_item:
                    has_key = True
                    break
            if not has_key:
                return (False, "You don't have the key.")
        
        self.door_state = "locked"
        
        if self.lock_sound:
            character.msg(self.lock_sound)
        
        return (True, "You lock it.")
    
    def do_unlock(self, character):
        """
        Attempt to unlock the door.
        """
        if self.door_state != "locked":
            return (False, "It's not locked.")
        
        # Check for key
        if self.key_item:
            has_key = False
            for obj in character.contents:
                if obj.db.shortcode_key == self.key_item:
                    has_key = True
                    break
            if not has_key:
                return (False, "You don't have the key.")
        
        self.door_state = "closed"
        
        if self.unlock_sound:
            character.msg(self.unlock_sound)
        
        return (True, "You unlock it.")
    
    def do_knock(self, character):
        """
        Knock on the door.
        """
        if self.door_state == "open":
            return (False, "It's open.")
        
        sound = self.knock_sound or "Knock knock."
        
        # Both sides hear
        if self.location:
            self.location.msg_contents(f"{character.key} knocks on the {self.key}.")
        if self.destination:
            self.destination.msg_contents(sound)
        
        return (True, "You knock.")
    
    # -------------------------------------------------------------------------
    # FUTURE: BASH / LOCKPICK
    # -------------------------------------------------------------------------
    
    # TODO: Bash Door
    # def do_bash(self, character):
    #     """
    #     Attempt to break down the door.
    #     
    #     System: STRENGTH_SYSTEM, COMBAT_SYSTEM
    #     """
    #     pass
    
    # TODO: Lockpick
    # def do_lockpick(self, character):
    #     """
    #     Attempt to pick the lock.
    #     
    #     System: SKILL_SYSTEM
    #     """
    #     pass
    
    # -------------------------------------------------------------------------
    # OVERRIDE TRAVERSAL
    # -------------------------------------------------------------------------
    
    def at_traverse(self, traversing_object, target_location, **kwargs):
        """
        Check door state before allowing traversal.
        """
        if self.door_state == "closed":
            traversing_object.msg("The door is closed.")
            return
        
        if self.door_state == "locked":
            traversing_object.msg("The door is locked.")
            return
        
        if self.door_state == "jammed":
            traversing_object.msg("The door is stuck.")
            return
        
        if self.door_state == "barricaded":
            traversing_object.msg("The door is barricaded.")
            return
        
        # Door is open or broken - allow traversal
        super().at_traverse(traversing_object, target_location, **kwargs)
    
    def return_appearance(self, looker, **kwargs):
        """
        Show state-appropriate description.
        """
        base = super().return_appearance(looker, **kwargs)
        
        state_desc = {
            "open": self.desc_open,
            "closed": self.desc_closed,
            "locked": self.desc_locked or self.desc_closed,
            "jammed": self.desc_closed,
            "broken": self.desc_broken,
            "barricaded": self.desc_barricaded or self.desc_closed,
        }.get(self.door_state, "")
        
        if state_desc:
            return f"{base}\n{state_desc}"
        return base


class SecretMixin:
    """
    Mixin for exits that are hidden until discovered.
    
    Adds:
        - Hidden state
        - Discovery mechanics
        - Disguise description
    """
    
    # -------------------------------------------------------------------------
    # HIDDEN STATE
    # -------------------------------------------------------------------------
    
    is_secret = AttributeProperty(default=True)
    discovered_by = AttributeProperty(default=[])  # List of character dbrefs who found it
    
    # -------------------------------------------------------------------------
    # DISCOVERY
    # -------------------------------------------------------------------------
    
    discovery_method = AttributeProperty(default="search")
    # Methods:
    # - search: Found by searching the room
    # - examine: Found by examining the disguise object
    # - interact: Found by interacting with something (pull lever, push brick)
    # - password: Found by saying a word/phrase
    # - item: Found by using/having specific item
    # - automatic: Found when entering room (perception check)
    
    discovery_difficulty = AttributeProperty(default=10)  # DC for search/perception
    discovery_item = AttributeProperty(default="")  # Item needed (if method = item)
    discovery_password = AttributeProperty(default="")  # Password (if method = password)
    discovery_trigger = AttributeProperty(default="")  # Object to interact with
    
    # -------------------------------------------------------------------------
    # DISGUISE
    # -------------------------------------------------------------------------
    
    disguised_as = AttributeProperty(default="")  # "bookshelf", "wall", "painting"
    disguise_description = AttributeProperty(default="")  # What it looks like when hidden
    revealed_description = AttributeProperty(default="")  # What it looks like once found
    
    # Hints (for those who look closely)
    has_hint = AttributeProperty(default=True)
    hint_description = AttributeProperty(default="")  # "The wall looks slightly uneven here."
    hint_difficulty = AttributeProperty(default=5)  # Easier than full discovery
    
    # -------------------------------------------------------------------------
    # DISCOVERY MESSAGES
    # -------------------------------------------------------------------------
    
    discover_message = AttributeProperty(default="You discover a hidden passage!")
    discover_message_others = AttributeProperty(default="")  # What room sees
    already_known_message = AttributeProperty(default="You already know about that.")
    
    # -------------------------------------------------------------------------
    # VISIBILITY CHECK
    # -------------------------------------------------------------------------
    
    def is_visible_to(self, looker):
        """
        Check if this exit is visible to a character.
        """
        if not self.is_secret:
            return True
        
        looker_id = looker.dbref
        return looker_id in self.discovered_by
    
    # -------------------------------------------------------------------------
    # DISCOVERY
    # -------------------------------------------------------------------------
    
    def discover(self, character):
        """
        Character discovers this secret exit.
        
        Returns:
            tuple: (success: bool, message: str)
        """
        char_id = character.dbref
        
        if char_id in self.discovered_by:
            return (False, self.already_known_message)
        
        # Add to discovered list
        discovered = list(self.discovered_by)
        discovered.append(char_id)
        self.discovered_by = discovered
        
        # Notify
        character.msg(self.discover_message)
        if self.discover_message_others:
            self.location.msg_contents(
                self.discover_message_others,
                exclude=[character]
            )
        
        return (True, "")
    
    # -------------------------------------------------------------------------
    # FUTURE: DISCOVERY CHECKS
    # -------------------------------------------------------------------------
    
    # TODO: Search Check
    # def try_discover(self, character, method, **kwargs):
    #     """
    #     Attempt to discover through specified method.
    #     
    #     System: SKILL_SYSTEM, PERCEPTION_SYSTEM
    #     """
    #     if method != self.discovery_method:
    #         return (False, "")
    #     
    #     # Roll perception/search vs difficulty
    #     # If success, call self.discover(character)
    #     pass
    
    # TODO: Passive Discovery
    # def at_object_receive(self, obj, source):
    #     """
    #     When someone enters room, check for automatic discovery.
    #     
    #     System: PERCEPTION_SYSTEM
    #     """
    #     if self.discovery_method == "automatic":
    #         # Roll perception check
    #         pass
    
    def return_appearance(self, looker, **kwargs):
        """
        Show disguise or real appearance based on discovery.
        """
        if self.is_visible_to(looker):
            if self.revealed_description:
                return self.revealed_description
            return super().return_appearance(looker, **kwargs)
        else:
            # Hidden - show nothing or disguise
            return self.disguise_description or ""


class TraversalMixin:
    """
    Mixin for exits requiring special movement (climb, swim, crawl, etc.)
    
    Adds:
        - Traversal type requirements
        - Skill/ability checks
        - Failure consequences
    """
    
    # -------------------------------------------------------------------------
    # TRAVERSAL TYPE
    # -------------------------------------------------------------------------
    
    traversal_type = AttributeProperty(default="walk")
    # Types:
    # - walk: Normal movement
    # - step: Small obstacle (step over)
    # - climb: Requires climbing (ladder, rope, wall)
    # - crawl: Requires crawling (low space)
    # - squeeze: Tight space
    # - swim: Water crossing
    # - jump: Gap to cross
    # - fall: Downward drop
    # - fly: Requires flight
    
    traversal_difficulty = AttributeProperty(default=0)  # 0 = automatic, higher = harder
    traversal_skill = AttributeProperty(default="")  # Skill used for check
    
    # -------------------------------------------------------------------------
    # REQUIREMENTS
    # -------------------------------------------------------------------------
    
    requires_equipment = AttributeProperty(default="")  # "rope", "climbing_gear"
    requires_ability = AttributeProperty(default="")  # "flight", "water_breathing"
    requires_free_hands = AttributeProperty(default=False)
    
    # -------------------------------------------------------------------------
    # FAILURE
    # -------------------------------------------------------------------------
    
    failure_possible = AttributeProperty(default=True)  # Can you fail?
    failure_damage = AttributeProperty(default=0)  # Damage on failure
    failure_message = AttributeProperty(default="You fail to make it through.")
    failure_fall_room = AttributeProperty(default=None)  # Where you end up on failure
    
    # -------------------------------------------------------------------------
    # DESCRIPTIONS
    # -------------------------------------------------------------------------
    
    attempt_message = AttributeProperty(default="")  # "You begin to climb..."
    success_message = AttributeProperty(default="")  # "You make it across."
    
    # -------------------------------------------------------------------------
    # TRAVERSAL CHECK
    # -------------------------------------------------------------------------
    
    def check_traversal_ability(self, character):
        """
        Check if character can attempt this traversal.
        
        Returns:
            tuple: (can_attempt: bool, message: str)
        """
        # Check equipment
        if self.requires_equipment:
            has_equip = False
            for obj in character.contents:
                if obj.db.shortcode_key == self.requires_equipment:
                    has_equip = True
                    break
            if not has_equip:
                return (False, f"You need {self.requires_equipment} to do that.")
        
        # Check free hands
        if self.requires_free_hands:
            # TODO: Check if hands are free
            pass
        
        # -------------------------------------------------------------------------
        # FUTURE: Ability checks
        # -------------------------------------------------------------------------
        
        # TODO: Check abilities
        # if self.requires_ability:
        #     if not character.has_ability(self.requires_ability):
        #         return (False, f"You can't do that without {self.requires_ability}.")
        #
        # System: ABILITY_SYSTEM
        
        return (True, "")
    
    # -------------------------------------------------------------------------
    # FUTURE: SKILL CHECKS
    # -------------------------------------------------------------------------
    
    # TODO: Attempt traversal with skill check
    # def attempt_traversal(self, character):
    #     """
    #     Roll skill check for traversal.
    #     
    #     Returns:
    #         tuple: (success: bool, message: str)
    #     
    #     System: SKILL_SYSTEM
    #     """
    #     if self.traversal_difficulty == 0:
    #         return (True, self.success_message)
    #     
    #     # Roll vs difficulty
    #     # On fail, apply failure_damage, move to failure_fall_room
    #     pass


class BarrierMixin:
    """
    Mixin for exits that can be blocked/barricaded.
    
    Adds:
        - Barrier state
        - Blocking objects tracking
        - Removal mechanics
    """
    
    # -------------------------------------------------------------------------
    # BARRIER STATE
    # -------------------------------------------------------------------------
    
    is_barricaded = AttributeProperty(default=False)
    barrier_strength = AttributeProperty(default=10)  # How hard to break through
    
    # What's blocking it
    blocking_objects = AttributeProperty(default=[])  # dbrefs of furniture, etc.
    blocking_description = AttributeProperty(default="")  # "Heavy furniture blocks the way."
    
    # -------------------------------------------------------------------------
    # SIDES
    # -------------------------------------------------------------------------
    
    barricaded_from = AttributeProperty(default="")  # "here" or "other" - which side
    
    # -------------------------------------------------------------------------
    # FUTURE: BARRICADE ACTIONS
    # -------------------------------------------------------------------------
    
    # TODO: Create barricade
    # def do_barricade(self, character, with_objects=None):
    #     """
    #     Barricade the exit.
    #     
    #     System: FURNITURE_SYSTEM
    #     """
    #     pass
    
    # TODO: Remove barricade
    # def do_unbarricade(self, character):
    #     """
    #     Remove barricade.
    #     
    #     System: STRENGTH_SYSTEM
    #     """
    #     pass


class TrapMixin:
    """
    Mixin for dangerous exits (trap doors, pit traps, etc.)
    
    Adds:
        - One-way behavior
        - Damage on traversal
        - Trigger conditions
    """
    
    # -------------------------------------------------------------------------
    # ONE-WAY
    # -------------------------------------------------------------------------
    
    is_one_way = AttributeProperty(default=False)  # Can't return
    one_way_message = AttributeProperty(default="You can't go back that way.")
    
    # -------------------------------------------------------------------------
    # DAMAGE
    # -------------------------------------------------------------------------
    
    trap_damage = AttributeProperty(default=0)  # Damage on use
    trap_damage_type = AttributeProperty(default="")  # "fall", "spike", "fire"
    trap_save_difficulty = AttributeProperty(default=0)  # DC to avoid damage
    
    # -------------------------------------------------------------------------
    # TRIGGER
    # -------------------------------------------------------------------------
    
    trap_triggered = AttributeProperty(default=False)  # Has it gone off?
    trap_resets = AttributeProperty(default=False)  # Does it reset?
    trap_reset_time = AttributeProperty(default=0)  # Seconds to reset
    
    # -------------------------------------------------------------------------
    # MESSAGES
    # -------------------------------------------------------------------------
    
    trap_trigger_message = AttributeProperty(default="")  # "The floor gives way!"
    trap_damage_message = AttributeProperty(default="")  # "You hit the ground hard."
    trap_avoid_message = AttributeProperty(default="")  # "You catch yourself just in time."
    
    # -------------------------------------------------------------------------
    # FUTURE: TRAP MECHANICS
    # -------------------------------------------------------------------------
    
    # TODO: Detect trap
    # def try_detect(self, character):
    #     """
    #     Attempt to notice the trap.
    #     
    #     System: PERCEPTION_SYSTEM
    #     """
    #     pass
    
    # TODO: Disarm trap
    # def try_disarm(self, character):
    #     """
    #     Attempt to disarm.
    #     
    #     System: SKILL_SYSTEM
    #     """
    #     pass
    
    def at_traverse(self, traversing_object, target_location, **kwargs):
        """
        Apply trap effects on traversal.
        """
        if self.trap_damage > 0:
            if self.trap_trigger_message:
                traversing_object.msg(self.trap_trigger_message)
            
            # TODO: Apply damage
            # traversing_object.take_damage(self.trap_damage, self.trap_damage_type)
            
            if self.trap_damage_message:
                traversing_object.msg(self.trap_damage_message)
        
        super().at_traverse(traversing_object, target_location, **kwargs)
