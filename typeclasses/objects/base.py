"""
Object - Base

The Object is the class for general items in the game world.

Use the ObjectParent class to implement common features for *all* entities
with a location in the game world (like Characters, Rooms, Exits).
"""

from evennia.objects.objects import DefaultObject
from evennia import AttributeProperty


class ObjectParent:
    """
    Mixin for ALL entities (Objects, Exits, Characters, Rooms).
    
    Anything defined here is available on every typeclass that inherits from it.
    This is the place for truly universal properties and methods.
    """
    
    # -------------------------------------------------------------------------
    # SHORTCODE SYSTEM
    # For injecting descriptions into room text via <obj:key>, <npc:key>, etc.
    # -------------------------------------------------------------------------
    
    short_desc = AttributeProperty(default="")
    shortcode_key = AttributeProperty(default="")
    
    # -------------------------------------------------------------------------
    # BUILDER METADATA
    # -------------------------------------------------------------------------
    
    builder_notes = AttributeProperty(default="")
    last_edited_by = AttributeProperty(default="")
    is_complete = AttributeProperty(default=False)
    review_status = AttributeProperty(default="draft")  # draft, review, approved
    
    # -------------------------------------------------------------------------
    # PHYSICAL PROPERTIES
    # Used by various systems for realistic interactions
    # -------------------------------------------------------------------------
    
    material = AttributeProperty(default="")  # wood, stone, metal, fabric, etc.
    weight = AttributeProperty(default=0)  # For carrying, breaking, etc.
    size = AttributeProperty(default="medium")  # tiny, small, medium, large, huge
    fragility = AttributeProperty(default="normal")  # fragile, normal, sturdy, unbreakable
    
    # -------------------------------------------------------------------------
    # SENSORY PROPERTIES
    # What can be perceived about this thing
    # -------------------------------------------------------------------------
    
    # Visual
    visible = AttributeProperty(default=True)
    look_desc = AttributeProperty(default="")  # Detailed examination description
    
    # Sound
    ambient_sound = AttributeProperty(default="")  # Sound it makes passively
    sound_on_interact = AttributeProperty(default="")  # Sound when used/touched
    
    # Smell
    smell_desc = AttributeProperty(default="")  # What it smells like
    smell_range = AttributeProperty(default=0)  # How far smell carries (0 = touch only)
    
    # Touch
    texture_desc = AttributeProperty(default="")  # What it feels like
    temperature = AttributeProperty(default="normal")  # cold, cool, normal, warm, hot
    
    # -------------------------------------------------------------------------
    # GRID POSITION
    # For objects in grid rooms
    # -------------------------------------------------------------------------
    
    grid_position = AttributeProperty(default=None)  # (x, y) within grid room
    
    # -------------------------------------------------------------------------
    # FUTURE: BODY/CLOTHING SYSTEM
    # -------------------------------------------------------------------------
    
    # TODO: Wearable Properties
    # is_wearable = AttributeProperty(default=False)
    # wear_slot = AttributeProperty(default="")  # "torso", "head", "wrists", etc.
    # covers_parts = AttributeProperty(default=[])  # Body parts this conceals
    # wear_layer = AttributeProperty(default=0)  # Layering order (0 = skin, higher = outer)
    #
    # System: CLOTHING_SYSTEM
    
    # -------------------------------------------------------------------------
    # FUTURE: CONSENT SYSTEM HOOKS
    # -------------------------------------------------------------------------
    
    # TODO: Consent Integration
    # requires_consent = AttributeProperty(default=False)
    # consent_type = AttributeProperty(default="ask")
    # interaction_rating = AttributeProperty(default="sfw")
    #
    # def check_consent(self, actor, target, action):
    #     """Verify consent before interaction."""
    #     pass
    #
    # System: CONSENT_SYSTEM
    
    # -------------------------------------------------------------------------
    # FUTURE: CONTENT FILTERING
    # -------------------------------------------------------------------------
    
    # TODO: Content Flags
    # content_flags = AttributeProperty(default=[])  # ["violence", "sexual", etc.]
    #
    # def is_visible_to(self, looker):
    #     """Check content preferences."""
    #     pass
    #
    # System: CONTENT_FILTER_SYSTEM


class Object(ObjectParent, DefaultObject):
    """
    Base object typeclass. Items, furniture, props, etc.
    """
    
    # -------------------------------------------------------------------------
    # INTERACTION
    # -------------------------------------------------------------------------
    
    is_gettable = AttributeProperty(default=True)  # Can be picked up
    is_droppable = AttributeProperty(default=True)  # Can be dropped
    is_giveable = AttributeProperty(default=True)  # Can be given to others
    
    # -------------------------------------------------------------------------
    # CONTAINER PROPERTIES
    # -------------------------------------------------------------------------
    
    is_container = AttributeProperty(default=False)
    container_capacity = AttributeProperty(default=0)  # 0 = not a container
    is_open = AttributeProperty(default=True)  # For containers
    is_locked = AttributeProperty(default=False)
    key_item = AttributeProperty(default="")  # shortcode_key of key
    
    # -------------------------------------------------------------------------
    # FUTURE: FURNITURE SYSTEM
    # Moved to objects/furniture/ but base hooks here
    # -------------------------------------------------------------------------
    
    # TODO: Furniture Properties
    # is_furniture = AttributeProperty(default=False)
    # furniture_positions = AttributeProperty(default=[])
    # furniture_capacity = AttributeProperty(default=1)
    # occupied_by = AttributeProperty(default=[])
    #
    # System: FURNITURE_SYSTEM
    
    # -------------------------------------------------------------------------
    # FUTURE: RESTRAINT SYSTEM
    # -------------------------------------------------------------------------
    
    # TODO: Restraint Properties  
    # is_restraint = AttributeProperty(default=False)
    # forced_position = AttributeProperty(default="")
    # escape_difficulty = AttributeProperty(default=10)
    # requires_help_to_escape = AttributeProperty(default=True)
    # restraint_type = AttributeProperty(default="")
    #
    # System: RESTRAINT_SYSTEM
    
    # -------------------------------------------------------------------------
    # FUTURE: EMITTER SYSTEM
    # -------------------------------------------------------------------------
    
    # TODO: Emitter Properties
    # is_emitter = AttributeProperty(default=False)
    # emit_type = AttributeProperty(default="")  # ambient, light, sound, smell
    # emit_messages = AttributeProperty(default=[])
    # emit_interval = AttributeProperty(default=60)
    # emit_chance = AttributeProperty(default=0.3)
    #
    # System: EMITTER_SYSTEM
    
    # -------------------------------------------------------------------------
    # FUTURE: LIGHT SOURCE
    # -------------------------------------------------------------------------
    
    # TODO: Light Properties
    # is_light_source = AttributeProperty(default=False)
    # light_level = AttributeProperty(default=0)  # How much light it provides
    # light_radius = AttributeProperty(default=0)  # How far light reaches
    # fuel_remaining = AttributeProperty(default=-1)  # -1 = infinite
    # is_lit = AttributeProperty(default=False)
    #
    # System: LIGHTING_SYSTEM
    
    pass
