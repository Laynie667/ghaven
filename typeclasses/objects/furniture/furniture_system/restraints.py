"""
Furniture - Restraints

Restraint furniture: stocks, pillories, crosses, frames, cages, breeding benches.
These are specifically designed to hold characters in vulnerable positions.

Inheritance:
    Furniture
    └── Restraint
        ├── Stocks
        │   ├── WoodenStocks
        │   └── IronStocks
        ├── Pillory
        ├── Cross
        │   ├── StAndrewsCross
        │   └── LatinCross
        ├── Frame
        │   ├── SpreadFrame
        │   └── SuspensionFrame
        ├── Cage
        │   ├── StandingCage
        │   ├── KneelingCage
        │   └── DogCage
        ├── BreedingBench
        │   ├── StandardBench
        │   └── AdjustableBench
        └── SpankingHorse
            ├── Sawhorse
            └── PaddedHorse
"""

from typing import Dict, Set, Tuple, TYPE_CHECKING
from .base import (
    Furniture,
    FurnitureType,
    FurnitureState,
    FurnitureSlot,
    OccupantPosition,
    Occupant,
)

if TYPE_CHECKING:
    from evennia.objects.objects import DefaultCharacter


# =============================================================================
# RESTRAINT BASE
# =============================================================================

class Restraint(Furniture):
    """
    Base class for restraint furniture.
    
    All restraint furniture:
    - Has at least one slot that restrains
    - Can be locked/unlocked
    - Exposes specific body zones
    - May have positions for others to interact
    """
    
    def at_object_creation(self):
        super().at_object_creation()
        self.db.furniture_type = FurnitureType.STOCKS  # Default
        self.db.position_tags = {"bondage", "restraint"}
        self.db.requires_key = False  # Some need keys
        self.db.escape_difficulty = 50  # 0-100 difficulty to escape
    
    def get_slots(self) -> Dict[str, FurnitureSlot]:
        return {
            "restrained": FurnitureSlot(
                key="restrained",
                name="restrained",
                max_occupants=1,
                positions={OccupantPosition.BOUND_STANDING},
                is_restraint=True,
                requires_lock=True,
                exposed_zones={"all"},
                description="{name} is restrained here",
            ),
        }
    
    def attempt_escape(
        self,
        character: "DefaultCharacter",
        strength_bonus: int = 0
    ) -> Tuple[bool, str]:
        """
        Attempt to escape from restraints.
        
        Returns:
            (success, message)
        """
        occupant = self.get_occupant_by_dbref(character.dbref)
        if not occupant:
            return False, "You're not restrained here."
        
        if not occupant.is_locked:
            # Just need to get out
            return self.release(character)
        
        # Roll against difficulty
        import random
        roll = random.randint(1, 100) + strength_bonus
        
        if roll > self.db.escape_difficulty:
            # Escape!
            occupant.is_locked = False
            return self.release(character, force=True)
        
        return False, f"You struggle against the {self.key} but can't break free."


# =============================================================================
# STOCKS
# =============================================================================

class Stocks(Restraint):
    """
    Medieval stocks - locks head and hands in a wooden frame.
    
    Position support:
    - Bent over (locked)
    - Standing in front (to use the locked person)
    - Kneeling in front (oral access)
    """
    
    def at_object_creation(self):
        super().at_object_creation()
        self.db.furniture_type = FurnitureType.STOCKS
        self.db.position_tags = {
            "bondage", "stocks", "bent_over",
            "doggy", "oral", "humiliation",
        }
        self.db.max_total_occupants = 3
        self.db.material = "heavy wood"
        self.db.escape_difficulty = 70
        self.db.desc = (
            "A heavy wooden stocks with holes for head and wrists. "
            "The top half can be lifted and locked down."
        )
    
    def get_slots(self) -> Dict[str, FurnitureSlot]:
        return {
            "locked": FurnitureSlot(
                key="locked",
                name="locked in the stocks",
                max_occupants=1,
                positions={OccupantPosition.BOUND_BENT},
                is_restraint=True,
                requires_lock=True,
                exposed_zones={
                    "ass", "groin", "back", "thighs",  # Rear
                    "face", "mouth",  # Front through hole
                },
                blocked_zones={"hands", "arms", "neck"},  # Trapped
                description="{name} is locked in the stocks, bent over and helpless",
            ),
            "front": FurnitureSlot(
                key="front",
                name="in front of the stocks",
                max_occupants=1,
                positions={
                    OccupantPosition.STANDING,
                    OccupantPosition.KNEELING,
                },
                exposed_zones={"groin"},
                description="{name} stands in front of the locked victim",
            ),
            "rear": FurnitureSlot(
                key="rear",
                name="behind the stocks",
                max_occupants=1,
                positions={
                    OccupantPosition.STANDING,
                    OccupantPosition.KNEELING,
                },
                exposed_zones={"groin"},
                description="{name} stands behind the locked victim",
            ),
        }


class WoodenStocks(Stocks):
    """Standard wooden stocks."""
    pass


class IronStocks(Stocks):
    """Iron stocks - stronger, harder to escape."""
    
    def at_object_creation(self):
        super().at_object_creation()
        self.db.material = "cold iron"
        self.db.escape_difficulty = 90
        self.db.desc = (
            "Heavy iron stocks, cold to the touch. "
            "No amount of struggling will break these."
        )


# =============================================================================
# PILLORY
# =============================================================================

class Pillory(Restraint):
    """
    A pillory - standing stocks that lock head and hands.
    Victim stands upright, exposed to the crowd.
    """
    
    def at_object_creation(self):
        super().at_object_creation()
        self.db.furniture_type = FurnitureType.PILLORY
        self.db.position_tags = {
            "bondage", "pillory", "standing",
            "humiliation", "public",
        }
        self.db.max_total_occupants = 3
        self.db.escape_difficulty = 65
        self.db.desc = (
            "A wooden pillory on a raised platform. "
            "Holes for head and wrists keep the victim standing and exposed."
        )
    
    def get_slots(self) -> Dict[str, FurnitureSlot]:
        return {
            "locked": FurnitureSlot(
                key="locked",
                name="locked in the pillory",
                max_occupants=1,
                positions={OccupantPosition.BOUND_STANDING},
                is_restraint=True,
                requires_lock=True,
                exposed_zones={
                    "face", "mouth",  # Through hole
                    "chest", "belly", "groin", "thighs",  # Front
                    "back", "ass",  # Rear
                },
                blocked_zones={"hands", "arms", "neck"},
                description="{name} stands locked in the pillory, publicly displayed",
            ),
            "crowd": FurnitureSlot(
                key="crowd",
                name="in the crowd",
                max_occupants=5,
                positions={OccupantPosition.STANDING},
                description="{name} watches from the crowd",
            ),
        }


# =============================================================================
# CROSSES
# =============================================================================

class Cross(Restraint):
    """
    Base class for crosses - vertical restraint frames.
    """
    
    def at_object_creation(self):
        super().at_object_creation()
        self.db.furniture_type = FurnitureType.CROSS
        self.db.position_tags = {"bondage", "cross", "spread"}
        self.db.max_total_occupants = 2
        self.db.escape_difficulty = 80


class StAndrewsCross(Cross):
    """
    X-shaped cross - spreads limbs to the corners.
    The classic BDSM cross.
    """
    
    def at_object_creation(self):
        super().at_object_creation()
        self.db.position_tags = {
            "bondage", "cross", "spread", "x_cross",
            "standing", "display",
        }
        self.db.material = "padded wood"
        self.db.desc = (
            "An X-shaped St. Andrew's Cross, padded where the body rests. "
            "Cuffs at each corner secure wrists and ankles."
        )
    
    def get_slots(self) -> Dict[str, FurnitureSlot]:
        return {
            "bound": FurnitureSlot(
                key="bound",
                name="bound to the cross",
                max_occupants=1,
                positions={OccupantPosition.BOUND_STANDING},
                is_restraint=True,
                requires_lock=True,
                exposed_zones={
                    "chest", "belly", "groin", "thighs",
                    "inner_thighs", "armpits",
                },
                blocked_zones={"back"},  # Against the cross
                description="{name} is spread-eagled on the cross, fully exposed",
            ),
            "before": FurnitureSlot(
                key="before",
                name="before the cross",
                max_occupants=1,
                positions={
                    OccupantPosition.STANDING,
                    OccupantPosition.KNEELING,
                },
                description="{name} stands before the bound figure",
            ),
        }


class LatinCross(Cross):
    """
    T-shaped cross - traditional crucifixion position.
    Arms out to the sides, body hanging.
    """
    
    def at_object_creation(self):
        super().at_object_creation()
        self.db.position_tags = {
            "bondage", "cross", "crucifixion",
            "standing", "suspended",
        }
        self.db.material = "rough wood"
        self.db.desc = (
            "A T-shaped wooden cross. "
            "The victim hangs with arms outstretched."
        )
    
    def get_slots(self) -> Dict[str, FurnitureSlot]:
        return {
            "crucified": FurnitureSlot(
                key="crucified",
                name="crucified",
                max_occupants=1,
                positions={OccupantPosition.SUSPENDED},
                is_restraint=True,
                requires_lock=True,
                exposed_zones={
                    "chest", "belly", "groin", "thighs",
                    "armpits", "sides",
                },
                blocked_zones={"back"},
                description="{name} hangs from the cross, arms outstretched",
            ),
        }


# =============================================================================
# FRAMES
# =============================================================================

class Frame(Restraint):
    """
    Base class for restraint frames.
    """
    
    def at_object_creation(self):
        super().at_object_creation()
        self.db.furniture_type = FurnitureType.FRAME
        self.db.position_tags = {"bondage", "frame", "spread"}


class SpreadFrame(Frame):
    """
    A frame that spreads the victim's limbs.
    Can be horizontal or vertical.
    """
    
    def at_object_creation(self):
        super().at_object_creation()
        self.db.position_tags = {
            "bondage", "frame", "spread",
            "horizontal", "vertical",
        }
        self.db.orientation = "vertical"  # vertical or horizontal
        self.db.max_total_occupants = 2
        self.db.desc = (
            "A metal frame with adjustable cuffs at each corner. "
            "It can hold someone spread-eagled."
        )
    
    def get_slots(self) -> Dict[str, FurnitureSlot]:
        if self.db.orientation == "horizontal":
            position = OccupantPosition.LYING_BACK
            desc = "{name} lies spread-eagled in the frame"
            exposed = {"chest", "belly", "groin", "thighs", "inner_thighs"}
            blocked = {"back"}
        else:
            position = OccupantPosition.BOUND_STANDING
            desc = "{name} hangs spread in the frame"
            exposed = {"chest", "belly", "groin", "thighs", "inner_thighs", "back", "ass"}
            blocked = set()
        
        return {
            "spread": FurnitureSlot(
                key="spread",
                name="spread in the frame",
                max_occupants=1,
                positions={position},
                is_restraint=True,
                requires_lock=True,
                exposed_zones=exposed,
                blocked_zones=blocked,
                description=desc,
            ),
            "before": FurnitureSlot(
                key="before",
                name="before the frame",
                max_occupants=1,
                positions={OccupantPosition.STANDING, OccupantPosition.KNEELING},
                description="{name} stands before the bound figure",
            ),
        }
    
    def rotate(self) -> str:
        """Rotate the frame between vertical and horizontal."""
        if self.db.orientation == "vertical":
            self.db.orientation = "horizontal"
            return "The frame rotates to horizontal."
        else:
            self.db.orientation = "vertical"
            return "The frame rotates to vertical."


class SuspensionFrame(Frame):
    """
    A frame for suspension bondage.
    Victim hangs from above.
    """
    
    def at_object_creation(self):
        super().at_object_creation()
        self.db.position_tags = {
            "bondage", "frame", "suspension",
            "hanging", "aerial",
        }
        self.db.max_total_occupants = 2
        self.db.desc = (
            "A sturdy frame with attachment points above. "
            "Designed for suspension bondage."
        )
    
    def get_slots(self) -> Dict[str, FurnitureSlot]:
        return {
            "suspended": FurnitureSlot(
                key="suspended",
                name="suspended from the frame",
                max_occupants=1,
                positions={OccupantPosition.SUSPENDED},
                is_restraint=True,
                requires_lock=False,  # Ropes, not locks
                exposed_zones={
                    "all",  # Fully accessible when suspended
                },
                description="{name} hangs suspended from the frame",
            ),
            "floor": FurnitureSlot(
                key="floor",
                name="beneath the frame",
                max_occupants=1,
                positions={
                    OccupantPosition.STANDING,
                    OccupantPosition.KNEELING,
                    OccupantPosition.LYING_BACK,
                },
                description="{name} is beneath the suspended figure",
            ),
        }


# =============================================================================
# CAGES
# =============================================================================

class Cage(Restraint):
    """
    Base class for cages.
    """
    
    def at_object_creation(self):
        super().at_object_creation()
        self.db.furniture_type = FurnitureType.CAGE
        self.db.position_tags = {"bondage", "cage", "confined"}
        self.db.material = "iron bars"
        self.db.escape_difficulty = 95  # Very hard to escape


class StandingCage(Cage):
    """
    A cage large enough to stand in.
    Bars allow access from outside.
    """
    
    def at_object_creation(self):
        super().at_object_creation()
        self.db.position_tags = {
            "bondage", "cage", "confined",
            "standing", "display",
        }
        self.db.max_total_occupants = 2
        self.db.desc = (
            "A tall iron cage with bars on all sides. "
            "Just enough room to stand."
        )
    
    def get_slots(self) -> Dict[str, FurnitureSlot]:
        return {
            "inside": FurnitureSlot(
                key="inside",
                name="inside the cage",
                max_occupants=1,
                positions={
                    OccupantPosition.STANDING,
                    OccupantPosition.KNEELING,
                    OccupantPosition.SITTING,
                },
                is_restraint=True,
                requires_lock=True,
                exposed_zones={
                    # Bars allow access
                    "chest", "belly", "groin", "thighs",
                    "back", "ass",
                },
                description="{name} is caged, visible through the bars",
            ),
            "outside": FurnitureSlot(
                key="outside",
                name="outside the cage",
                max_occupants=1,
                positions={
                    OccupantPosition.STANDING,
                    OccupantPosition.KNEELING,
                },
                description="{name} stands outside the cage",
            ),
        }


class KneelingCage(Cage):
    """
    A smaller cage that forces kneeling.
    """
    
    def at_object_creation(self):
        super().at_object_creation()
        self.db.position_tags = {
            "bondage", "cage", "confined",
            "kneeling", "humiliation",
        }
        self.db.max_total_occupants = 2
        self.db.desc = (
            "A small iron cage, too short to stand in. "
            "The occupant must kneel or crouch."
        )
    
    def get_slots(self) -> Dict[str, FurnitureSlot]:
        return {
            "inside": FurnitureSlot(
                key="inside",
                name="inside the cage",
                max_occupants=1,
                positions={
                    OccupantPosition.KNEELING,
                    OccupantPosition.SITTING,
                },
                is_restraint=True,
                requires_lock=True,
                exposed_zones={"chest", "face", "back"},
                description="{name} kneels in the cramped cage",
            ),
            "outside": FurnitureSlot(
                key="outside",
                name="outside the cage",
                max_occupants=1,
                positions={OccupantPosition.STANDING, OccupantPosition.KNEELING},
                description="{name} watches from outside the cage",
            ),
        }


class DogCage(Cage):
    """
    A cage sized for pets - forces all fours position.
    """
    
    def at_object_creation(self):
        super().at_object_creation()
        self.db.position_tags = {
            "bondage", "cage", "confined",
            "pet", "all_fours", "humiliation",
        }
        self.db.max_total_occupants = 1
        self.db.material = "wire mesh"
        self.db.desc = (
            "A wire dog crate, far too small for a human to be comfortable. "
            "The occupant can only fit on all fours."
        )
    
    def get_slots(self) -> Dict[str, FurnitureSlot]:
        return {
            "inside": FurnitureSlot(
                key="inside",
                name="cramped inside the crate",
                max_occupants=1,
                positions={OccupantPosition.LYING_FRONT},  # All fours
                is_restraint=True,
                requires_lock=True,
                exposed_zones={"back", "ass"},  # Limited access
                description="{name} is cramped in the dog crate on all fours",
            ),
        }


# =============================================================================
# BREEDING BENCH
# =============================================================================

class BreedingBench(Restraint):
    """
    A bench specifically designed to present someone for breeding.
    Locks them in position with rear exposed.
    """
    
    def at_object_creation(self):
        super().at_object_creation()
        self.db.furniture_type = FurnitureType.BREEDING_BENCH
        self.db.position_tags = {
            "bondage", "breeding_bench", "bent_over",
            "doggy", "breeding", "prone",
        }
        self.db.max_total_occupants = 2
        self.db.material = "padded leather"
        self.db.escape_difficulty = 75
        self.db.desc = (
            "A padded breeding bench with restraints for wrists and ankles. "
            "The victim is held bent over, rear presented and accessible."
        )
    
    def get_slots(self) -> Dict[str, FurnitureSlot]:
        return {
            "mounted": FurnitureSlot(
                key="mounted",
                name="locked on the breeding bench",
                max_occupants=1,
                positions={OccupantPosition.BOUND_BENT},
                is_restraint=True,
                requires_lock=True,
                exposed_zones={
                    "ass", "groin", "thighs", "back",
                    "pussy", "tailhole",  # Specifically presented
                },
                blocked_zones={"front", "chest"},  # Against padding
                description="{name} is locked on the breeding bench, rear presented",
            ),
            "behind": FurnitureSlot(
                key="behind",
                name="behind the bench",
                max_occupants=1,
                positions={
                    OccupantPosition.STANDING,
                    OccupantPosition.KNEELING,
                },
                exposed_zones={"groin"},
                description="{name} stands behind the bench, ready to breed",
            ),
        }


class AdjustableBreedingBench(BreedingBench):
    """
    A breeding bench with adjustable height and angle.
    """
    
    def at_object_creation(self):
        super().at_object_creation()
        self.db.height = "waist"  # low, waist, high
        self.db.angle = "horizontal"  # horizontal, angled_up, angled_down
        self.db.desc = (
            "An adjustable breeding bench with hydraulic controls. "
            "Height and angle can be changed for optimal positioning."
        )
    
    def adjust_height(self, height: str) -> str:
        """Adjust bench height."""
        if height in ("low", "waist", "high"):
            self.db.height = height
            return f"The bench adjusts to {height} height."
        return "Invalid height. Use: low, waist, or high."
    
    def adjust_angle(self, angle: str) -> str:
        """Adjust bench angle."""
        if angle in ("horizontal", "angled_up", "angled_down"):
            self.db.angle = angle
            return f"The bench tilts to {angle.replace('_', ' ')}."
        return "Invalid angle."


# =============================================================================
# SPANKING HORSE
# =============================================================================

class SpankingHorse(Restraint):
    """
    Base class for spanking horses / sawhorses.
    """
    
    def at_object_creation(self):
        super().at_object_creation()
        self.db.furniture_type = FurnitureType.HORSE
        self.db.position_tags = {
            "bondage", "horse", "bent_over",
            "spanking", "punishment",
        }
        self.db.max_total_occupants = 2


class Sawhorse(SpankingHorse):
    """
    A simple sawhorse - victim bends over the top.
    """
    
    def at_object_creation(self):
        super().at_object_creation()
        self.db.material = "rough wood"
        self.db.escape_difficulty = 40  # Easier to escape
        self.db.desc = (
            "A simple wooden sawhorse. "
            "Uncomfortable but effective for punishment."
        )
    
    def get_slots(self) -> Dict[str, FurnitureSlot]:
        return {
            "over": FurnitureSlot(
                key="over",
                name="bent over the horse",
                max_occupants=1,
                positions={
                    OccupantPosition.BENT_OVER,
                    OccupantPosition.BOUND_BENT,
                },
                is_restraint=True,
                requires_lock=False,  # Often just held/tied
                exposed_zones={"ass", "back", "thighs"},
                blocked_zones={"belly"},  # On the horse
                description="{name} is bent over the sawhorse, rear presented",
            ),
            "beside": FurnitureSlot(
                key="beside",
                name="beside the horse",
                max_occupants=1,
                positions={OccupantPosition.STANDING},
                description="{name} stands ready beside the horse",
            ),
        }


class PaddedHorse(SpankingHorse):
    """
    A padded spanking horse with restraint points.
    """
    
    def at_object_creation(self):
        super().at_object_creation()
        self.db.material = "padded leather"
        self.db.escape_difficulty = 70
        self.db.desc = (
            "A well-padded spanking horse with leather straps "
            "to secure wrists and ankles."
        )
    
    def get_slots(self) -> Dict[str, FurnitureSlot]:
        return {
            "strapped": FurnitureSlot(
                key="strapped",
                name="strapped to the horse",
                max_occupants=1,
                positions={OccupantPosition.BOUND_BENT},
                is_restraint=True,
                requires_lock=True,
                exposed_zones={"ass", "back", "thighs", "groin"},
                blocked_zones={"belly", "chest"},
                description="{name} is strapped securely over the padded horse",
            ),
            "beside": FurnitureSlot(
                key="beside",
                name="beside the horse",
                max_occupants=1,
                positions={OccupantPosition.STANDING},
                description="{name} stands ready with implement in hand",
            ),
        }


# =============================================================================
# EXPORTS
# =============================================================================

__all__ = [
    # Base
    "Restraint",
    
    # Stocks
    "Stocks",
    "WoodenStocks",
    "IronStocks",
    
    # Pillory
    "Pillory",
    
    # Crosses
    "Cross",
    "StAndrewsCross",
    "LatinCross",
    
    # Frames
    "Frame",
    "SpreadFrame",
    "SuspensionFrame",
    
    # Cages
    "Cage",
    "StandingCage",
    "KneelingCage",
    "DogCage",
    
    # Breeding Bench
    "BreedingBench",
    "AdjustableBreedingBench",
    
    # Spanking Horse
    "SpankingHorse",
    "Sawhorse",
    "PaddedHorse",
]
