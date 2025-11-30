"""
Partition - Preset Types

Ready-to-use partition types.
"""

from evennia import AttributeProperty
from .base import Partition
from .mixins import OpeningMixin, OperableMixin


# =============================================================================
# VISUAL PARTITIONS (See-through)
# =============================================================================

class WindowPartition(OperableMixin, Partition):
    """
    A window between spaces.
    
    Use for: Room windows, interior windows, observation windows.
    Not for climbing through - use WindowExit for that.
    """
    
    partition_material = AttributeProperty(default="glass")
    
    # Windows are see-through even when closed
    closed_transmits_sight = AttributeProperty(default=True)
    closed_transmits_sound = AttributeProperty(default=False)  # Glass blocks sound
    
    has_curtain = AttributeProperty(default=False)
    curtain_closed = AttributeProperty(default=False)
    
    @property
    def transmits_sight(self):
        if self.curtain_closed:
            return False
        return super().transmits_sight
    
    open_sound = AttributeProperty(default="The window slides open.")
    close_sound = AttributeProperty(default="The window clicks shut.")


class BarsPartition(Partition):
    """
    Bars or a grate between spaces.
    
    Use for: Prison bars, sewer grates, cage walls.
    """
    
    partition_material = AttributeProperty(default="iron")
    
    # Always see and hear through bars
    transmits_sight = AttributeProperty(default=True)
    transmits_sound = AttributeProperty(default=True)
    transmits_smell = AttributeProperty(default=True)
    
    sound_quality = AttributeProperty(default="clear")
    
    # Items can pass through if small enough
    allows_items = AttributeProperty(default=True)
    item_size_limit = AttributeProperty(default="small")
    
    bar_spacing = AttributeProperty(default="narrow")  # narrow, medium, wide


class FencePartition(Partition):
    """
    A fence or railing between areas.
    
    Use for: Garden fences, balcony railings, corral fences.
    """
    
    partition_material = AttributeProperty(default="wood")
    partition_height = AttributeProperty(default="partial")  # Not full height
    
    transmits_sight = AttributeProperty(default=True)
    transmits_sound = AttributeProperty(default=True)
    transmits_smell = AttributeProperty(default=True)
    
    sound_quality = AttributeProperty(default="clear")


# =============================================================================
# OPAQUE PARTITIONS (Block sight)
# =============================================================================

class WallPartition(Partition):
    """
    A solid wall partition.
    
    Use for: Room dividers, interior walls with pass-throughs.
    """
    
    partition_material = AttributeProperty(default="wood")
    partition_thickness = AttributeProperty(default="normal")
    
    transmits_sight = AttributeProperty(default=False)
    transmits_sound = AttributeProperty(default=True)
    transmits_smell = AttributeProperty(default=False)
    
    sound_quality = AttributeProperty(default="muffled")


class CurtainPartition(OperableMixin, Partition):
    """
    A hanging curtain or drape.
    
    Use for: Room dividers, alcove curtains, shower curtains.
    """
    
    partition_material = AttributeProperty(default="fabric")
    partition_thickness = AttributeProperty(default="thin")
    
    # Curtain states: open = pulled aside, closed = hanging
    open_transmits_sight = AttributeProperty(default=True)
    open_transmits_sound = AttributeProperty(default=True)
    open_transmits_smell = AttributeProperty(default=True)
    
    closed_transmits_sight = AttributeProperty(default=False)  # Can't see through
    closed_transmits_sound = AttributeProperty(default=True)  # Clear sound
    closed_transmits_smell = AttributeProperty(default=True)
    
    open_sound = AttributeProperty(default="The curtain rustles aside.")
    close_sound = AttributeProperty(default="The curtain falls back.")
    
    sound_quality = AttributeProperty(default="clear")  # Fabric doesn't block sound


class ScreenPartition(Partition):
    """
    A decorative screen or room divider.
    
    Use for: Japanese screens, folding dividers, privacy screens.
    """
    
    partition_material = AttributeProperty(default="paper")
    partition_height = AttributeProperty(default="full")
    
    transmits_sight = AttributeProperty(default=False)
    transmits_sound = AttributeProperty(default=True)
    transmits_smell = AttributeProperty(default=True)
    
    sound_quality = AttributeProperty(default="clear")
    
    # Screens can show silhouettes if backlit
    shows_silhouette = AttributeProperty(default=True)
    
    # -------------------------------------------------------------------------
    # FUTURE: Silhouette system
    # -------------------------------------------------------------------------
    
    # TODO: Show silhouettes when backlit
    # def get_silhouette_description(self, looker):
    #     """
    #     Describe silhouettes visible through screen.
    #     
    #     System: LIGHTING_SYSTEM
    #     """
    #     pass


# =============================================================================
# OPENING PARTITIONS (For physical interaction)
# =============================================================================

class GloryWall(OpeningMixin, Partition):
    """
    A partition with an opening for anonymous interaction.
    
    Use for: Adult content, anonymous interactions.
    """
    
    partition_material = AttributeProperty(default="wood")
    
    transmits_sight = AttributeProperty(default=False)  # Can't see through wall
    transmits_sound = AttributeProperty(default=True)
    transmits_smell = AttributeProperty(default=False)
    
    sound_quality = AttributeProperty(default="muffled")
    
    # Opening properties
    has_opening = AttributeProperty(default=True)
    opening_size = AttributeProperty(default="medium")
    opening_shape = AttributeProperty(default="round")
    opening_height = AttributeProperty(default="waist")
    
    opening_description = AttributeProperty(default="A round opening at waist height.")
    
    opening_allows = AttributeProperty(default=[
        "fingers", "hand", "arm", "tongue"
    ])
    
    # Anonymous by default
    is_anonymous = AttributeProperty(default=True)
    reveals_identity = AttributeProperty(default=["face", "head"])
    
    # Can sense presence but not identity
    can_sense_presence = AttributeProperty(default=True)
    can_sense_gender = AttributeProperty(default=False)
    
    # Interaction
    allows_touch = AttributeProperty(default=True)
    allows_grab = AttributeProperty(default=True)
    allows_restrain = AttributeProperty(default=True)  # Can hold parts in place


class FeedingSlot(OpeningMixin, OperableMixin, Partition):
    """
    A small slot that can open and close.
    
    Use for: Prison feeding slots, mail slots, small pass-throughs.
    """
    
    partition_material = AttributeProperty(default="iron")
    
    # Slot properties
    has_opening = AttributeProperty(default=True)
    opening_size = AttributeProperty(default="small")
    opening_shape = AttributeProperty(default="slot")
    opening_height = AttributeProperty(default="waist")
    
    opening_description = AttributeProperty(default="A small slot in the partition.")
    
    opening_allows = AttributeProperty(default=[
        "fingers", "hand"
    ])
    
    # Can be opened/closed
    is_operable = AttributeProperty(default=True)
    
    # When closed, nothing passes
    closed_transmits_sight = AttributeProperty(default=False)
    closed_transmits_sound = AttributeProperty(default=True)
    
    # When open, can see through slot
    open_transmits_sight = AttributeProperty(default=True)  # Limited view
    open_transmits_sound = AttributeProperty(default=True)
    
    # Items can pass when open
    allows_items = AttributeProperty(default=True)
    item_size_limit = AttributeProperty(default="small")
    
    # Anonymous unless looking directly through
    is_anonymous = AttributeProperty(default=True)
    
    open_sound = AttributeProperty(default="The slot slides open.")
    close_sound = AttributeProperty(default="The slot slides shut.")


class ServiceWindow(OpeningMixin, OperableMixin, Partition):
    """
    A service window / counter opening.
    
    Use for: Bank teller windows, ticket booths, confessionals.
    """
    
    partition_material = AttributeProperty(default="wood")
    
    has_opening = AttributeProperty(default=True)
    opening_size = AttributeProperty(default="large")
    opening_shape = AttributeProperty(default="square")
    opening_height = AttributeProperty(default="chest")
    
    opening_description = AttributeProperty(default="A large service window.")
    
    opening_allows = AttributeProperty(default=[
        "fingers", "hand", "arm", "head"
    ])
    
    # Can see and communicate clearly
    open_transmits_sight = AttributeProperty(default=True)
    open_transmits_sound = AttributeProperty(default=True)
    
    # Not anonymous - can see each other
    is_anonymous = AttributeProperty(default=False)
    
    # Items pass easily
    allows_items = AttributeProperty(default=True)
    item_size_limit = AttributeProperty(default="medium")
    
    # Has a counter/ledge
    has_counter = AttributeProperty(default=True)


class ConfessionalScreen(OpeningMixin, Partition):
    """
    A confessional screen or similar privacy barrier.
    
    Use for: Confessionals, interview screens, witness protection.
    """
    
    partition_material = AttributeProperty(default="wood")
    
    transmits_sight = AttributeProperty(default=False)
    transmits_sound = AttributeProperty(default=True)
    transmits_smell = AttributeProperty(default=False)
    
    sound_quality = AttributeProperty(default="clear")  # Designed for speaking
    
    # Small mesh/grate opening
    has_opening = AttributeProperty(default=True)
    opening_size = AttributeProperty(default="tiny")  # Just for sound
    opening_shape = AttributeProperty(default="mesh")
    opening_height = AttributeProperty(default="head")
    
    opening_allows = AttributeProperty(default=[])  # Nothing fits through
    
    # Anonymous design
    is_anonymous = AttributeProperty(default=True)
    can_sense_presence = AttributeProperty(default=True)


# =============================================================================
# SPECIAL PARTITIONS
# =============================================================================

class MirrorPartition(Partition):
    """
    A two-way mirror or magical viewing surface.
    
    Use for: Interrogation rooms, magical scrying, one-way observation.
    """
    
    partition_material = AttributeProperty(default="glass")
    
    # One side is mirrored, other side can see through
    is_two_way = AttributeProperty(default=True)
    observation_side = AttributeProperty(default="other")  # Which side can see through
    
    # This side sees mirror unless observation_side is "this"
    # Other side sees through unless observation_side is "other"
    
    sound_quality = AttributeProperty(default="faint")  # Minimal sound transmission
    
    def get_transmits_sight(self, from_side):
        """Check if you can see through from your side."""
        if from_side == self.observation_side:
            return True
        return False  # See reflection only


class MagicalBarrier(Partition):
    """
    A magical force barrier.
    
    Use for: Force fields, magical walls, containment.
    """
    
    partition_material = AttributeProperty(default="magical")
    
    # Usually can see through magical barriers
    transmits_sight = AttributeProperty(default=True)
    transmits_sound = AttributeProperty(default=False)  # Sound doesn't pass
    transmits_smell = AttributeProperty(default=False)
    
    # Visual appearance
    barrier_appearance = AttributeProperty(default="A shimmering barrier of force.")
    barrier_color = AttributeProperty(default="blue")
    
    # Can be dispelled?
    is_dispellable = AttributeProperty(default=True)
    dispel_difficulty = AttributeProperty(default=15)
    
    # -------------------------------------------------------------------------
    # FUTURE: Magic system integration
    # -------------------------------------------------------------------------
    
    # TODO: Dispel mechanics
    # def try_dispel(self, character, spell=None):
    #     """Attempt to dispel the barrier."""
    #     pass
    #
    # System: MAGIC_SYSTEM
