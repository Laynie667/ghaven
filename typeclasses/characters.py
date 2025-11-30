"""
Character

Characters are objects controlled by player accounts.
They have physical presence, can move, and interact with the world.
"""

from evennia.objects.objects import DefaultCharacter
from evennia import AttributeProperty
from .objects import ObjectParent


class Character(ObjectParent, DefaultCharacter):
    """
    Base character class for player-controlled entities.
    
    Inherits short_desc and shortcode_key from ObjectParent.
    
    Adds:
        - Grid position tracking (for grid rooms)
        - Sensory ranges (sight, hearing, smell)
        - Position/pose system hooks
    """
    
    # -------------------------------------------------------------------------
    # GRID POSITION
    # Where this character is within a grid room
    # -------------------------------------------------------------------------
    
    grid_position = AttributeProperty(default=None)  # (x, y) within current grid room, None otherwise
    
    def get_grid_position(self):
        """Get current grid position, or None if not in grid room."""
        return self.grid_position
    
    def set_grid_position(self, x, y):
        """Set grid position within current room."""
        self.grid_position = (x, y)
    
    def clear_grid_position(self):
        """Clear grid position (when leaving grid room)."""
        self.grid_position = None
    
    # -------------------------------------------------------------------------
    # SENSORY RANGES
    # How far this character can perceive things
    # -------------------------------------------------------------------------
    
    sight_range = AttributeProperty(default=5)  # Cells away can see
    hearing_range = AttributeProperty(default=8)  # Cells away can hear
    smell_range = AttributeProperty(default=4)  # Cells away can smell
    
    # -------------------------------------------------------------------------
    # FUTURE: Sensory Modifiers
    # -------------------------------------------------------------------------
    
    # TODO: Dynamic Sensory Calculation
    # Base ranges can be modified by:
    # - Equipment (glasses, ear plugs)
    # - Conditions (blind, deaf)
    # - Environment (dark, foggy, loud)
    # - Species/Race traits
    # - Skills
    #
    # def get_effective_sight_range(self):
    #     """Calculate actual sight range with modifiers."""
    #     base = self.sight_range
    #     # Check conditions, equipment, environment
    #     # Apply modifiers
    #     return modified_range
    #
    # def get_effective_hearing_range(self):
    #     """Calculate actual hearing range with modifiers."""
    #     pass
    #
    # def get_effective_smell_range(self):
    #     """Calculate actual smell range with modifiers."""
    #     pass
    #
    # System: SENSORY_SYSTEM
    
    # -------------------------------------------------------------------------
    # FUTURE: SENSORY CONDITIONS
    # -------------------------------------------------------------------------
    
    # TODO: Sensory Impairments
    # is_blind = AttributeProperty(default=False)
    # is_deaf = AttributeProperty(default=False)
    # is_anosmic = AttributeProperty(default=False)  # Can't smell
    #
    # temporary_blindness = AttributeProperty(default=0)  # Ticks remaining
    # temporary_deafness = AttributeProperty(default=0)
    #
    # System: CONDITION_SYSTEM
    
    # -------------------------------------------------------------------------
    # POSITION / POSE SYSTEM
    # -------------------------------------------------------------------------
    
    position = AttributeProperty(default="")  # "standing", "sitting", "kneeling", "lying", etc.
    pose = AttributeProperty(default="")  # Custom pose text for room display
    
    # -------------------------------------------------------------------------
    # FUTURE: Position Effects
    # -------------------------------------------------------------------------
    
    # TODO: Position System
    # def get_display_position(self):
    #     """
    #     Get position text for room display.
    #     
    #     Returns something like:
    #     - "standing" -> "" (default, not shown)
    #     - "sitting" -> "sitting"
    #     - "lying on the bed" -> "lying on the bed"
    #     
    #     System: POSITION_SYSTEM
    #     """
    #     pass
    #
    # def can_change_position(self, new_position):
    #     """Check if character can change to new position (not restrained, etc)."""
    #     pass
    #
    # def set_position(self, new_position, pose=None):
    #     """Change position with optional custom pose."""
    #     pass
    
    # -------------------------------------------------------------------------
    # FUTURE: FURNITURE ATTACHMENT
    # -------------------------------------------------------------------------
    
    # TODO: Furniture System
    # using_furniture = AttributeProperty(default=None)  # dbref of furniture being used
    # furniture_position = AttributeProperty(default="")  # Position on that furniture
    # can_move = AttributeProperty(default=True)  # Can leave current position
    #
    # def get_furniture(self):
    #     """Get furniture object if using one."""
    #     pass
    #
    # def attach_to_furniture(self, furniture, position=None):
    #     """Attach character to furniture."""
    #     pass
    #
    # def detach_from_furniture(self):
    #     """Remove from furniture."""
    #     pass
    #
    # System: FURNITURE_SYSTEM
    
    # -------------------------------------------------------------------------
    # BODY SYSTEM
    # -------------------------------------------------------------------------
    
    body_data = AttributeProperty(default=None)  # Serialized body dict
    
    def get_body(self):
        """
        Get the character's Body object.
        
        Deserializes from body_data on first call, caches result.
        
        Returns:
            Body: The character's body, or None if not initialized
        """
        # Check cache first
        if hasattr(self, '_body_cache') and self._body_cache is not None:
            return self._body_cache
        
        # Deserialize from storage
        if self.body_data:
            from typeclasses.body import Body
            self._body_cache = Body.from_dict(self.body_data)
            return self._body_cache
        
        return None
    
    def set_body(self, body):
        """
        Set the character's body.
        
        Args:
            body: Body object
        """
        self._body_cache = body
        self.body_data = body.to_dict()
    
    def save_body(self):
        """Save cached body changes to storage."""
        if hasattr(self, '_body_cache') and self._body_cache:
            self.body_data = self._body_cache.to_dict()
    
    def init_body(
        self,
        structure: str = "bipedal_plantigrade",
        species: str = "human",
        sex: str = "male",
        genital_override: str = None,
        custom_parts: dict = None,
        add_presentation: bool = True
    ):
        """
        Initialize body by composing structure + species + sex.
        
        Args:
            structure: Body structure key
                - bipedal_plantigrade (humans, elves)
                - bipedal_digitigrade (anthro canines, felines)
                - quadruped (feral dogs, wolves)
                - tauroid (centaurs)
                - serpentine (lamia, nagas)
                - aquatic (merfolk)
            species: Species key (determines genital type)
                - human, elf, dwarf, orc (human genitals)
                - wolf, fox, dog (canine genitals)
                - cat, lion, tiger (feline genitals)
                - horse (equine genitals)
                - snake, dragon (reptile genitals)
            sex: Sex config key
                - male, female
                - herm, futa, maleherm
                - femboy, cuntboy, dickgirl
                - neuter, doll
            genital_override: Override species genital type
                - e.g., "equine" for horse cock on human
            custom_parts: Optional dict of part customizations
            add_presentation: Add BodyPresentation layer (marks/fluids)
        
        Example:
            char.init_body("bipedal_digitigrade", "wolf", "female")  # Female wolf with canine genitals
            char.init_body("tauroid", "horse", "male")  # Male centaur with equine genitals
            char.init_body("bipedal_plantigrade", "human", "futa", genital_override="equine")  # Futa with horse cock
        """
        from typeclasses.body import Body, BodyPresentation
        
        body = Body.compose(structure, species, sex, genital_override, custom_parts)
        
        if add_presentation:
            body.presentation = BodyPresentation()
        
        self.set_body(body)
    
    def init_body_preset(self, preset: str):
        """
        Initialize body from a preset composition.
        
        Available presets:
            - human_male, human_female
            - elf_male, elf_female
            - wolf_anthro_male, wolf_anthro_female
            - wolf_feral
            - cat_anthro_female
            - horse_anthro_male
            - centaur_male, centaur_female
            - lamia_female
            - mermaid
            - succubus
            - herm_wolf
            - futa_human
            - femboy_fox
            - futa_horse_human (human futa with horse cock)
            - dickgirl_cat
        """
        from typeclasses.body import (
            BodyPresentation,
            compose_human_male, compose_human_female,
            compose_elf_male, compose_elf_female,
            compose_wolf_anthro_male, compose_wolf_anthro_female,
            compose_wolf_feral,
            compose_cat_anthro_female,
            compose_horse_anthro_male,
            compose_centaur_male, compose_centaur_female,
            compose_lamia_female,
            compose_mermaid,
            compose_succubus,
            compose_herm_wolf,
            compose_futa_human,
            compose_femboy_fox,
            compose_futa_horse_human,
            compose_dickgirl_cat,
        )
        
        presets = {
            "human_male": compose_human_male,
            "human_female": compose_human_female,
            "elf_male": compose_elf_male,
            "elf_female": compose_elf_female,
            "wolf_anthro_male": compose_wolf_anthro_male,
            "wolf_anthro_female": compose_wolf_anthro_female,
            "wolf_feral": compose_wolf_feral,
            "cat_anthro_female": compose_cat_anthro_female,
            "horse_anthro_male": compose_horse_anthro_male,
            "centaur_male": compose_centaur_male,
            "centaur_female": compose_centaur_female,
            "lamia_female": compose_lamia_female,
            "mermaid": compose_mermaid,
            "succubus": compose_succubus,
            "herm_wolf": compose_herm_wolf,
            "futa_human": compose_futa_human,
            "femboy_fox": compose_femboy_fox,
            "futa_horse_human": compose_futa_horse_human,
            "dickgirl_cat": compose_dickgirl_cat,
        }
        
        if preset not in presets:
            raise ValueError(f"Unknown preset: {preset}. Available: {list(presets.keys())}")
        
        body = presets[preset]()
        body.presentation = BodyPresentation()
        self.set_body(body)
    
    # -------------------------------------------------------------------------
    # BODY FUNCTION CHECKS
    # These check the body's capabilities
    # -------------------------------------------------------------------------
    
    def can_speak(self):
        """Check if character can speak based on body."""
        body = self.get_body()
        if not body:
            return (True, "")  # No body system = can speak
        return body.can_speak()
    
    def can_hear(self):
        """Check if character can hear based on body."""
        body = self.get_body()
        if not body:
            return (True, "")
        return body.can_hear()
    
    def can_smell(self):
        """Check if character can smell based on body."""
        body = self.get_body()
        if not body:
            return (True, "")
        return body.can_smell()
    
    def can_see(self):
        """Check if character can see based on body."""
        body = self.get_body()
        if not body:
            return (True, "")
        return body.can_see()
    
    def can_manipulate(self):
        """Check if character can use hands/manipulate objects."""
        body = self.get_body()
        if not body:
            return (True, "")
        return body.can_manipulate()
    
    def can_move_body(self):
        """Check if character can move based on body (legs, etc)."""
        body = self.get_body()
        if not body:
            return (True, "")
        return body.can_move()
    
    # -------------------------------------------------------------------------
    # BODY-BASED SENSORY MODIFIERS
    # -------------------------------------------------------------------------
    
    def get_effective_sight_range(self):
        """Calculate actual sight range with body modifiers."""
        base = self.sight_range
        body = self.get_body()
        
        if body:
            # get_sight_penalty returns capability multiplier (1.0 = full, 0.5 = half, 0 = blind)
            capability = body.get_sight_penalty()
            base = int(base * capability)
        
        return max(0, base)
    
    def get_effective_hearing_range(self):
        """Calculate actual hearing range with body modifiers."""
        base = self.hearing_range
        body = self.get_body()
        
        if body:
            # get_hearing_penalty returns capability multiplier
            capability = body.get_hearing_penalty()
            base = int(base * capability)
        
        return max(0, base)
    
    def get_effective_smell_range(self):
        """Calculate actual smell range with body modifiers."""
        base = self.smell_range
        body = self.get_body()
        
        if body:
            can_smell, _ = body.can_smell()
            if not can_smell:
                return 0
        
        return base
    
    # -------------------------------------------------------------------------
    # BODY PART ACCESS SHORTCUTS
    # -------------------------------------------------------------------------
    
    def has_body_part(self, part_key):
        """Check if character has a specific body part."""
        body = self.get_body()
        if not body:
            return True  # No body system = has all parts
        return body.has_part(part_key)
    
    def get_body_part(self, part_key):
        """Get state of a specific body part."""
        body = self.get_body()
        if not body:
            return None
        return body.get_part(part_key)
    
    def get_exposed_parts(self):
        """Get list of uncovered body parts."""
        body = self.get_body()
        if not body:
            return []
        return body.get_exposed_parts()
    
    def get_covered_parts(self):
        """Get list of covered body parts."""
        body = self.get_body()
        if not body:
            return []
        return body.get_covered_parts()
    
    def obstruct_body_part(self, part_key, obstruction, obstruction_type):
        """Obstruct a body part (gag mouth, blindfold eyes, etc)."""
        body = self.get_body()
        if not body:
            return False
        result = body.obstruct_part(part_key, obstruction, obstruction_type)
        if result:
            self.save_body()
        return result
    
    def clear_body_obstruction(self, part_key):
        """Remove obstruction from a body part."""
        body = self.get_body()
        if not body:
            return False
        result = body.clear_obstruction(part_key)
        if result:
            self.save_body()
        return result
    
    # -------------------------------------------------------------------------
    # PRESENTATION SHORTCUTS (marks, fluids, state)
    # These only work if body has presentation layer
    # -------------------------------------------------------------------------
    
    def get_presentation(self):
        """Get the presentation layer for this character's body."""
        body = self.get_body()
        if not body:
            return None
        return body.presentation
    
    def add_mark(self, mark_type, location, description, **kwargs):
        """
        Add a mark to the character's body.
        
        Args:
            mark_type: MarkType enum value
            location: Body part key
            description: Mark description
            **kwargs: Additional Mark parameters (position, size, etc.)
        """
        from typeclasses.body import Mark
        
        pres = self.get_presentation()
        if not pres:
            return False
        
        mark = Mark(
            mark_type=mark_type,
            location=location,
            description=description,
            **kwargs
        )
        pres.add_mark(mark)
        self.save_body()
        return True
    
    def add_fluid(self, fluid_type, location, amount="light", **kwargs):
        """
        Add fluid to a body part.
        
        Args:
            fluid_type: FluidType enum value
            location: Body part key
            amount: trace, light, moderate, heavy, dripping, covered
            **kwargs: Additional FluidPresence parameters
        """
        from typeclasses.body import FluidPresence
        
        pres = self.get_presentation()
        if not pres:
            return False
        
        fluid = FluidPresence(
            fluid_type=fluid_type,
            location=location,
            amount=amount,
            **kwargs
        )
        pres.add_fluid(fluid)
        self.save_body()
        return True
    
    def set_body_state(self, state_type, location=None, intensity="light"):
        """
        Set a body state (temperature, arousal, etc).
        
        Args:
            state_type: BodyStateType enum value
            location: Body part key or None for whole body
            intensity: light, moderate, strong
        """
        from typeclasses.body import BodyState
        
        pres = self.get_presentation()
        if not pres:
            return False
        
        state = BodyState(
            state_type=state_type,
            location=location,
            intensity=intensity
        )
        pres.set_state(state)
        self.save_body()
        return True
    
    def clean_body(self):
        """Remove all fluids from body (bathing)."""
        pres = self.get_presentation()
        if not pres:
            return False
        pres.clear_all_fluids()
        self.save_body()
        return True
    
    def get_arousal_level(self):
        """Get current arousal state."""
        pres = self.get_presentation()
        if not pres:
            return "calm"
        return pres.get_arousal_level()
    
    def tick_presentation(self):
        """
        Process time passing for presentation layer.
        Call periodically to fade marks, dry fluids, etc.
        """
        pres = self.get_presentation()
        if not pres:
            return
        pres.tick()
        self.save_body()
    
    # System: BODY_SYSTEM
    
    # -------------------------------------------------------------------------
    # FUTURE: CLOTHING SYSTEM
    # -------------------------------------------------------------------------
    
    # TODO: What's Worn
    # worn_items = AttributeProperty(default={})  # slot: item_dbref
    #
    # def wear(self, item, slot=None):
    #     """Put on an item."""
    #     pass
    #
    # def remove(self, item_or_slot):
    #     """Take off an item."""
    #     pass
    #
    # def get_worn_on(self, slot):
    #     """Get item worn on a slot."""
    #     pass
    #
    # System: CLOTHING_SYSTEM
    
    # -------------------------------------------------------------------------
    # FUTURE: CONSENT SYSTEM
    # -------------------------------------------------------------------------
    
    # TODO: Consent Preferences
    # consent_preferences = AttributeProperty(default={})
    #
    # Example:
    # {
    #     "default": "ask",  # Default consent mode
    #     "blanket": ["#123", "#456"],  # Characters with blanket consent
    #     "blocked": ["#789"],  # Characters who can't interact
    # }
    #
    # def check_consent(self, other_character, action_type):
    #     """Check if action is consented."""
    #     pass
    #
    # def grant_consent(self, other_character, consent_type):
    #     """Grant consent to another character."""
    #     pass
    #
    # def revoke_consent(self, other_character):
    #     """Revoke consent from another character."""
    #     pass
    #
    # System: CONSENT_SYSTEM
    
    # -------------------------------------------------------------------------
    # FUTURE: CONTENT PREFERENCES
    # -------------------------------------------------------------------------
    
    # TODO: Content Filtering
    # content_preferences = AttributeProperty(default={})
    #
    # Example:
    # {
    #     "can_view_adult": True,
    #     "show_violence": True,
    #     "show_sexual": True,
    #     "hard_limits": ["vore", "underage"],
    #     "favorites": ["romance", "bondage"],
    # }
    #
    # def can_view_content(self, content_flags):
    #     """Check if this character's preferences allow viewing content."""
    #     pass
    #
    # System: CONTENT_FILTER_SYSTEM
    
    # -------------------------------------------------------------------------
    # FUTURE: RELATIONSHIPS
    # -------------------------------------------------------------------------
    
    # TODO: Relationship Tracking
    # relationships = AttributeProperty(default={})
    #
    # Example:
    # {
    #     "#456": {
    #         "type": "romantic",
    #         "status": "partnered",
    #         "consent_level": "blanket",
    #         "notes": "Player notes here",
    #     }
    # }
    #
    # def get_relationship(self, other_character):
    #     """Get relationship with another character."""
    #     pass
    #
    # def set_relationship(self, other_character, rel_type, status):
    #     """Set/update relationship."""
    #     pass
    #
    # System: RELATIONSHIP_SYSTEM
    
    # -------------------------------------------------------------------------
    # MOVEMENT HOOKS
    # -------------------------------------------------------------------------
    
    def at_post_move(self, source_location, move_type="move", **kwargs):
        """
        Called after moving to a new location.
        
        Handles grid position updates when entering/leaving grid rooms.
        """
        super().at_post_move(source_location, move_type=move_type, **kwargs)
        
        # Check if new location is a grid room
        new_loc = self.location
        if new_loc and hasattr(new_loc, 'shape_type') and new_loc.shape_type:
            # Entering a grid room
            # TODO: Set position based on which exit we used
            # For now, set to room origin
            if self.grid_position is None:
                self.grid_position = (new_loc.x, new_loc.y)
        else:
            # Not a grid room, clear grid position
            self.grid_position = None
    
    # -------------------------------------------------------------------------
    # FUTURE: GRID MOVEMENT
    # -------------------------------------------------------------------------
    
    # TODO: Movement Within Grid Rooms
    # def move_to_cell(self, x, y):
    #     """
    #     Move to a specific cell within current grid room.
    #     
    #     Checks:
    #     - Is cell valid (within room shape)?
    #     - Is cell passable (no blocking objects)?
    #     - Movement cost/time
    #     
    #     Returns:
    #         bool: Whether movement succeeded
    #     
    #     System: GRID_MOVEMENT_SYSTEM
    #     """
    #     pass
    #
    # def get_distance_to_cell(self, x, y):
    #     """Calculate distance to a cell from current position."""
    #     if not self.grid_position:
    #         return 0
    #     cx, cy = self.grid_position
    #     return abs(x - cx) + abs(y - cy)  # Manhattan distance
    #
    # def get_adjacent_cells(self):
    #     """Get cells adjacent to current position."""
    #     pass
    #
    # def can_move_to_cell(self, x, y):
    #     """Check if movement to cell is possible."""
    #     pass
    
    # -------------------------------------------------------------------------
    # FUTURE: PERCEPTION IN GRID ROOMS
    # -------------------------------------------------------------------------
    
    # TODO: What Character Perceives
    # def get_visible_exits(self):
    #     """
    #     Get exits visible from current position.
    #     
    #     Considers:
    #     - Character's sight_range
    #     - Exit's visible_range
    #     - Obstacles
    #     - Lighting
    #     
    #     System: PERCEPTION_SYSTEM
    #     """
    #     pass
    #
    # def get_audible_things(self):
    #     """Get things character can hear from current position."""
    #     pass
    #
    # def get_smellable_things(self):
    #     """Get things character can smell from current position."""
    #     pass
    #
    # def get_things_at_position(self, x, y):
    #     """Get objects/npcs at a specific grid position."""
    #     pass
