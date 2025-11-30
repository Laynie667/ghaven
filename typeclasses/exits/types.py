"""
Exit - Preset Types

Ready-to-use exit types combining base Exit with mixins.
Inherit from these or use directly.
"""

from evennia import AttributeProperty
from .base import Exit
from .mixins import DoorMixin, SecretMixin, TraversalMixin, BarrierMixin, TrapMixin


# =============================================================================
# DOOR TYPES
# =============================================================================

class DoorExit(DoorMixin, Exit):
    """
    A standard door that can be opened, closed, and locked.
    
    Use for: Regular doors, gates, hatches.
    """
    pass


class HeavyDoor(DoorMixin, Exit):
    """
    A heavy, slow-moving door.
    
    Use for: Castle doors, vault doors, iron gates.
    """
    
    door_material = AttributeProperty(default="iron")
    door_weight = AttributeProperty(default="heavy")
    door_thickness = AttributeProperty(default="thick")
    
    open_sound = AttributeProperty(default="The heavy door groans open slowly.")
    close_sound = AttributeProperty(default="The door thuds shut with a heavy clang.")
    creak_sound = AttributeProperty(default="GRRRRNNND...")
    
    bash_difficulty = AttributeProperty(default=20)
    door_hp = AttributeProperty(default=50)
    door_max_hp = AttributeProperty(default=50)


class PortcullisExit(DoorMixin, Exit):
    """
    A portcullis or similar gate.
    
    Use for: Castle gates, prison bars, dungeon entrances.
    """
    
    door_material = AttributeProperty(default="bars")
    door_weight = AttributeProperty(default="massive")
    opens_direction = AttributeProperty(default="up")  # Raises instead of swings
    
    # Can see/hear through bars
    transmits_sound = AttributeProperty(default=True)
    transmits_light = AttributeProperty(default=True)
    
    open_sound = AttributeProperty(default="Chains rattle as the portcullis rises.")
    close_sound = AttributeProperty(default="The portcullis crashes down.")
    
    # Usually needs mechanism to operate
    requires_mechanism = AttributeProperty(default=True)  # Can't just push open
    mechanism_location = AttributeProperty(default="")  # Where the winch is


class CurtainExit(DoorMixin, Exit):
    """
    A curtain, tapestry, or fabric barrier.
    
    Use for: Alcove curtains, tent flaps, hanging tapestries.
    """
    
    door_material = AttributeProperty(default="fabric")
    door_weight = AttributeProperty(default="light")
    door_thickness = AttributeProperty(default="thin")
    
    is_lockable = AttributeProperty(default=False)
    
    # Sound passes through fabric
    transmits_sound = AttributeProperty(default=True)
    
    open_sound = AttributeProperty(default="The curtain rustles aside.")
    close_sound = AttributeProperty(default="The curtain falls back into place.")
    
    auto_close = AttributeProperty(default=True)
    auto_close_delay = AttributeProperty(default=5)


# =============================================================================
# SECRET EXITS
# =============================================================================

class SecretExit(SecretMixin, Exit):
    """
    A hidden passage without door mechanics.
    
    Use for: Hidden tunnels, concealed passages, secret paths.
    """
    pass


class SecretDoor(DoorMixin, SecretMixin, Exit):
    """
    A hidden door that can be opened/closed/locked.
    
    Use for: Bookshelf doors, rotating walls, hidden panels.
    """
    
    disguised_as = AttributeProperty(default="wall")
    disguise_description = AttributeProperty(default="The wall looks solid.")
    reveal_trigger = AttributeProperty(default="")  # What reveals it


class BookshelfDoor(DoorMixin, SecretMixin, Exit):
    """
    Classic hidden door behind a bookshelf.
    """
    
    disguised_as = AttributeProperty(default="bookshelf")
    disguise_description = AttributeProperty(default="A tall bookshelf filled with dusty tomes.")
    revealed_description = AttributeProperty(default="A bookshelf that swings open to reveal a hidden passage.")
    
    discovery_method = AttributeProperty(default="interact")
    discovery_trigger = AttributeProperty(default="book")  # Pull the right book
    
    hint_description = AttributeProperty(default="One book looks slightly more worn than the others.")
    
    open_sound = AttributeProperty(default="The bookshelf swings open with a soft click.")
    close_sound = AttributeProperty(default="The bookshelf swings back into place.")


# =============================================================================
# TRAVERSAL EXITS
# =============================================================================

class ClimbableExit(TraversalMixin, Exit):
    """
    An exit requiring climbing.
    
    Use for: Ladders, ropes, walls, trees.
    """
    
    traversal_type = AttributeProperty(default="climb")
    passage_type = AttributeProperty(default="climb")
    requires_free_hands = AttributeProperty(default=True)
    
    attempt_message = AttributeProperty(default="You begin to climb...")
    success_message = AttributeProperty(default="You make it to the top.")
    failure_message = AttributeProperty(default="You lose your grip and fall!")


class SwimExit(TraversalMixin, Exit):
    """
    An exit requiring swimming.
    
    Use for: Underwater passages, river crossings.
    """
    
    traversal_type = AttributeProperty(default="swim")
    passage_type = AttributeProperty(default="swim")
    
    # Water properties
    water_depth = AttributeProperty(default="deep")  # shallow, deep, variable
    current_strength = AttributeProperty(default="none")  # none, mild, strong, dangerous
    
    attempt_message = AttributeProperty(default="You enter the water...")
    success_message = AttributeProperty(default="You swim across successfully.")
    failure_message = AttributeProperty(default="The current is too strong!")


class CrawlExit(TraversalMixin, Exit):
    """
    An exit requiring crawling.
    
    Use for: Tunnels, vents, small openings.
    """
    
    traversal_type = AttributeProperty(default="crawl")
    passage_type = AttributeProperty(default="crawl")
    exit_size = AttributeProperty(default="small")
    
    attempt_message = AttributeProperty(default="You get down and start crawling...")
    success_message = AttributeProperty(default="You squeeze through.")


class JumpExit(TraversalMixin, Exit):
    """
    An exit requiring jumping across a gap.
    
    Use for: Chasms, rooftop gaps, broken bridges.
    """
    
    traversal_type = AttributeProperty(default="jump")
    passage_type = AttributeProperty(default="jump")
    
    failure_possible = AttributeProperty(default=True)
    failure_damage = AttributeProperty(default=5)
    
    gap_width = AttributeProperty(default="medium")  # small, medium, large
    
    attempt_message = AttributeProperty(default="You take a running leap...")
    success_message = AttributeProperty(default="You land safely on the other side!")
    failure_message = AttributeProperty(default="You don't quite make it!")


# =============================================================================
# TRAP EXITS
# =============================================================================

class TrapDoor(DoorMixin, TrapMixin, Exit):
    """
    A trapdoor that may drop you into somewhere unpleasant.
    
    Use for: Pit traps, dungeon drops, secret basement access.
    """
    
    is_one_way = AttributeProperty(default=False)  # Can climb back up?
    traversal_type = AttributeProperty(default="fall")
    
    trap_trigger_message = AttributeProperty(default="The floor gives way beneath you!")
    trap_damage_message = AttributeProperty(default="You hit the ground hard.")


class OneWayExit(TrapMixin, Exit):
    """
    An exit you can't return through.
    
    Use for: Slides, chutes, one-way doors, cliffs.
    """
    
    is_one_way = AttributeProperty(default=True)
    one_way_message = AttributeProperty(default="There's no way back up.")


class FallExit(TraversalMixin, TrapMixin, Exit):
    """
    A drop or fall to another location.
    
    Use for: Cliffs, holes, balconies.
    """
    
    traversal_type = AttributeProperty(default="fall")
    is_one_way = AttributeProperty(default=True)
    
    fall_height = AttributeProperty(default=10)  # For damage calculation
    
    trap_damage = AttributeProperty(default=10)
    trap_damage_type = AttributeProperty(default="fall")


# =============================================================================
# COMBINATION EXITS
# =============================================================================

class HatchExit(DoorMixin, TraversalMixin, Exit):
    """
    A hatch that requires climbing through.
    
    Use for: Ceiling hatches, floor hatches, ship hatches.
    """
    
    traversal_type = AttributeProperty(default="climb")
    requires_free_hands = AttributeProperty(default=True)
    
    hatch_direction = AttributeProperty(default="up")  # up or down
    
    open_sound = AttributeProperty(default="The hatch creaks open.")
    close_sound = AttributeProperty(default="The hatch thuds shut.")


class SecretTrapDoor(DoorMixin, SecretMixin, TrapMixin, Exit):
    """
    A hidden trapdoor - nasty surprise.
    
    Use for: Trap rooms, dungeon surprises.
    """
    
    is_secret = AttributeProperty(default=True)
    discovery_method = AttributeProperty(default="search")
    
    trap_damage = AttributeProperty(default=5)
    
    disguised_as = AttributeProperty(default="floor")
    disguise_description = AttributeProperty(default="The floor looks normal.")
    hint_description = AttributeProperty(default="Some of the flagstones look slightly loose.")


class WindowExit(DoorMixin, TraversalMixin, Exit):
    """
    A window that can be climbed through.
    
    Use for: Building windows, openings, skylights.
    """
    
    traversal_type = AttributeProperty(default="climb")
    exit_size = AttributeProperty(default="medium")
    
    # Windows are see-through when closed
    transmits_light = AttributeProperty(default=True)
    
    # Can see other room
    def blocks_sight(self):
        return False  # Always can see through
    
    door_material = AttributeProperty(default="wood")  # Frame material
    has_glass = AttributeProperty(default=True)
    is_barred = AttributeProperty(default=False)
    
    open_sound = AttributeProperty(default="The window creaks open.")
    close_sound = AttributeProperty(default="The window clicks shut.")
    
    # Breaking glass
    glass_broken = AttributeProperty(default=False)
    break_glass_message = AttributeProperty(default="CRASH! Glass shatters everywhere!")


# =============================================================================
# SPECIAL EXITS
# =============================================================================

class MagicalPortal(Exit):
    """
    A magical portal or teleportation point.
    
    Use for: Portals, teleport circles, magical doors.
    """
    
    # Visual effect
    portal_appearance = AttributeProperty(default="A shimmering portal hangs in the air.")
    
    # Activation
    always_active = AttributeProperty(default=True)
    activation_item = AttributeProperty(default="")  # Item needed to activate
    activation_word = AttributeProperty(default="")  # Word to activate
    
    # Stability
    is_stable = AttributeProperty(default=True)  # False = random destination
    portal_destinations = AttributeProperty(default=[])  # If unstable, list of possible dbrefs
    
    # Effects
    traverse_effect = AttributeProperty(default="")  # "dizzy", "nauseated", etc.
    
    use_sound = AttributeProperty(default="Reality warps around you.")
    
    # -------------------------------------------------------------------------
    # FUTURE: Portal mechanics
    # -------------------------------------------------------------------------
    
    # TODO: Activation check
    # def check_activation(self, character):
    #     """Check if portal is active for this character."""
    #     pass
    #
    # TODO: Random destination
    # def get_destination(self):
    #     """Get destination (may be random if unstable)."""
    #     pass
    #
    # System: MAGIC_SYSTEM


class ElevatorExit(DoorMixin, Exit):
    """
    An elevator or lift.
    
    Use for: Building elevators, mine lifts, magical platforms.
    """
    
    current_floor = AttributeProperty(default=0)
    floors = AttributeProperty(default={})  # {0: "#dbref", 1: "#dbref", ...}
    
    is_moving = AttributeProperty(default=False)
    move_time = AttributeProperty(default=5)  # Seconds between floors
    
    call_sound = AttributeProperty(default="Ding!")
    move_sound = AttributeProperty(default="The elevator rumbles to life.")
    arrive_sound = AttributeProperty(default="Ding!")
    
    # -------------------------------------------------------------------------
    # FUTURE: Elevator mechanics
    # -------------------------------------------------------------------------
    
    # TODO: Call elevator
    # def call_to_floor(self, floor_number):
    #     """Call elevator to specific floor."""
    #     pass
    #
    # TODO: Go to floor
    # def go_to_floor(self, character, floor_number):
    #     """Take character to floor."""
    #     pass
    #
    # System: ELEVATOR_SYSTEM
