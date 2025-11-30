"""
Furniture - Fixtures
====================

Fixed furniture elements: poles, hooks, rings, bars, etc.
"""

from .base import (
    Furniture, FurnitureType, SlotType, RestraintPoint, FurnitureSlot
)
from evennia import AttributeProperty


# =============================================================================
# POLES
# =============================================================================

class DancingPole(Furniture):
    """
    A pole for dancing and performing.
    """
    
    def at_object_creation(self):
        self.furniture_type = FurnitureType.FIXTURE
        self.size = "small"
        self.is_anchored = True
        
        self.add_slot(FurnitureSlot(
            key="dancing",
            slot_type=SlotType.STAND,
            max_occupants=1,
            default_pose="dancing on the pole",
            allowed_poses=["dancing", "spinning", "climbing", "grinding"],
            exposes=["all"],
            accessible_from=["watching"],
            occupied_desc="{name} works the pole.",
        ))
        
        self.add_slot(FurnitureSlot(
            key="watching",
            slot_type=SlotType.SIT,
            max_occupants=5,
            default_pose="watching the performance",
            accessible_from=["dancing"],
            occupied_desc="{names} watch appreciatively.",
        ))


class TiePost(Furniture):
    """
    A sturdy post for tying people to.
    """
    
    def at_object_creation(self):
        self.furniture_type = FurnitureType.FIXTURE
        self.size = "small"
        self.is_anchored = True
        
        self.add_slot(FurnitureSlot(
            key="tied",
            slot_type=SlotType.STAND,
            max_occupants=1,
            default_pose="tied to the post",
            allowed_poses=["tied", "bound", "struggling"],
            can_restrain=True,
            restraint_points=[RestraintPoint.WRISTS, RestraintPoint.ARMS],
            exposes=["front", "back"],
            accessible_from=["standing"],
            occupied_desc="{name} is tied to the post.",
        ))
        
        self.add_slot(FurnitureSlot(
            key="standing",
            slot_type=SlotType.STAND,
            max_occupants=2,
            default_pose="standing near the post",
            accessible_from=["tied"],
            occupied_desc="{names} attend the bound figure.",
        ))


class HitchingPost(Furniture):
    """
    A post for tying animals or pets.
    """
    
    def at_object_creation(self):
        self.furniture_type = FurnitureType.FIXTURE
        self.size = "small"
        self.is_anchored = True
        
        self.add_slot(FurnitureSlot(
            key="tied",
            slot_type=SlotType.STAND,
            max_occupants=2,
            default_pose="tied to the hitching post",
            allowed_poses=["tied", "waiting", "leashed"],
            can_restrain=True,
            restraint_points=[RestraintPoint.NECK],
            occupied_desc="{names} wait at the hitching post.",
            empty_desc="A sturdy hitching post.",
        ))


# =============================================================================
# HOOKS AND RINGS
# =============================================================================

class CeilingHook(Furniture):
    """
    A hook in the ceiling for suspension.
    """
    
    def at_object_creation(self):
        self.furniture_type = FurnitureType.FIXTURE
        self.size = "tiny"
        self.is_anchored = True
        
        self.add_slot(FurnitureSlot(
            key="hanging",
            slot_type=SlotType.RESTRAIN,
            max_occupants=1,
            default_pose="hanging from the ceiling hook",
            allowed_poses=["hanging", "suspended", "dangling"],
            can_restrain=True,
            restraint_points=[RestraintPoint.WRISTS, RestraintPoint.ARMS],
            exposes=["all"],
            accessible_from=["standing"],
            occupied_desc="{name} hangs from the hook.",
        ))
        
        self.add_slot(FurnitureSlot(
            key="standing",
            slot_type=SlotType.STAND,
            max_occupants=2,
            default_pose="standing beneath the hook",
            accessible_from=["hanging"],
            occupied_desc="{names} attend the hanging figure.",
        ))


class WallRing(Furniture):
    """
    A ring mounted to the wall.
    """
    
    height = AttributeProperty(default="waist")  # floor, low, waist, high, overhead
    
    def at_object_creation(self):
        self.furniture_type = FurnitureType.FIXTURE
        self.size = "tiny"
        self.is_anchored = True
        
        # Position depends on height
        if self.height in ["floor", "low"]:
            slot_type = SlotType.KNEEL
            pose = "chained to the low ring"
            points = [RestraintPoint.NECK, RestraintPoint.WRISTS]
        elif self.height == "waist":
            slot_type = SlotType.STAND
            pose = "chained to the ring"
            points = [RestraintPoint.WRISTS, RestraintPoint.WAIST]
        else:
            slot_type = SlotType.STAND
            pose = "stretched up to the high ring"
            points = [RestraintPoint.WRISTS]
        
        self.add_slot(FurnitureSlot(
            key="chained",
            slot_type=slot_type,
            max_occupants=1,
            default_pose=pose,
            allowed_poses=["chained", "bound", "helpless"],
            can_restrain=True,
            restraint_points=points,
            exposes=["front", "back"] if self.height != "overhead" else ["all"],
            occupied_desc=f"{{name}} is chained to the {self.height}-height ring.",
        ))


class FloorRing(Furniture):
    """
    A ring embedded in the floor.
    """
    
    def at_object_creation(self):
        self.furniture_type = FurnitureType.FIXTURE
        self.size = "tiny"
        self.is_anchored = True
        
        self.add_slot(FurnitureSlot(
            key="chained",
            slot_type=SlotType.KNEEL,
            max_occupants=1,
            default_pose="chained to the floor",
            allowed_poses=["kneeling", "prostrate", "on all fours"],
            can_restrain=True,
            restraint_points=[RestraintPoint.NECK, RestraintPoint.WRISTS, RestraintPoint.ANKLES],
            exposes=["back", "rear"],
            occupied_desc="{name} is chained to the floor.",
        ))


# =============================================================================
# BARS AND FRAMES
# =============================================================================

class SpreaderBar(Furniture):
    """
    A bar to keep legs or arms spread.
    """
    
    bar_type = AttributeProperty(default="ankle")  # ankle, wrist, double
    
    def at_object_creation(self):
        self.furniture_type = FurnitureType.FIXTURE
        self.size = "small"
        self.is_anchored = False
        
        if self.bar_type == "ankle":
            points = [RestraintPoint.ANKLES]
            pose = "legs held spread by the bar"
            exposes = ["genitals", "inner thighs"]
        elif self.bar_type == "wrist":
            points = [RestraintPoint.WRISTS]
            pose = "arms held apart by the bar"
            exposes = ["chest", "sides"]
        else:
            points = [RestraintPoint.WRISTS, RestraintPoint.ANKLES]
            pose = "spread-eagled in the bars"
            exposes = ["all"]
        
        self.add_slot(FurnitureSlot(
            key="spread",
            slot_type=SlotType.RESTRAIN,
            max_occupants=1,
            default_pose=pose,
            allowed_poses=["spread", "held", "exposed"],
            can_restrain=True,
            restraint_points=points,
            exposes=exposes,
            occupied_desc=f"{{name}}'s {self.bar_type}s are held apart by the bar.",
        ))


class BalletBar(Furniture):
    """
    A ballet/exercise bar mounted to the wall.
    """
    
    def at_object_creation(self):
        self.furniture_type = FurnitureType.FIXTURE
        self.size = "medium"
        self.is_anchored = True
        
        self.add_slot(FurnitureSlot(
            key="stretching",
            slot_type=SlotType.STAND,
            max_occupants=2,
            default_pose="stretching at the bar",
            allowed_poses=["stretching", "bending", "leg raised"],
            exposes=["legs", "rear"],
            occupied_desc="{names} stretch at the bar.",
        ))
        
        self.add_slot(FurnitureSlot(
            key="bent_over",
            slot_type=SlotType.BEND,
            max_occupants=1,
            default_pose="bent over the bar",
            allowed_poses=["bent", "presenting"],
            can_restrain=True,
            restraint_points=[RestraintPoint.WRISTS],
            exposes=["rear", "genitals"],
            accessible_from=["standing"],
            occupied_desc="{name} is bent over the bar.",
        ))
        
        self.add_slot(FurnitureSlot(
            key="standing",
            slot_type=SlotType.STAND,
            max_occupants=1,
            default_pose="standing behind",
            accessible_from=["bent_over"],
            occupied_desc="{name} stands ready.",
        ))


class TowelBar(Furniture):
    """
    A simple towel bar - can be used for quick restraint.
    """
    
    def at_object_creation(self):
        self.furniture_type = FurnitureType.FIXTURE
        self.size = "small"
        self.is_anchored = True
        
        self.add_slot(FurnitureSlot(
            key="bound",
            slot_type=SlotType.STAND,
            max_occupants=1,
            default_pose="hands tied to the towel bar",
            allowed_poses=["bound", "stretched"],
            can_restrain=True,
            restraint_points=[RestraintPoint.WRISTS],
            exposes=["front", "back"],
            occupied_desc="{name} is bound to the towel bar.",
        ))


# =============================================================================
# SPECIALTY FIXTURES
# =============================================================================

class GloryHole(Furniture):
    """
    A partition with a hole at a strategic height.
    """
    
    def at_object_creation(self):
        self.furniture_type = FurnitureType.FIXTURE
        self.size = "medium"
        self.is_anchored = True
        
        # One side
        self.add_slot(FurnitureSlot(
            key="presenting",
            slot_type=SlotType.STAND,
            max_occupants=1,
            default_pose="presenting through the hole",
            allowed_poses=["presenting", "inserted"],
            exposes=["genitals"],
            accessible_from=["servicing"],
            occupied_desc="Someone presents through the hole.",
        ))
        
        # Other side
        self.add_slot(FurnitureSlot(
            key="servicing",
            slot_type=SlotType.KNEEL,
            max_occupants=1,
            default_pose="kneeling at the glory hole",
            allowed_poses=["kneeling", "servicing"],
            accessible_from=["presenting"],
            occupied_desc="Someone waits on the other side.",
        ))


class MilkingStall(Furniture):
    """
    A stall designed to keep occupants in position for milking.
    """
    
    def at_object_creation(self):
        self.furniture_type = FurnitureType.FIXTURE
        self.size = "medium"
        self.is_anchored = True
        
        self.add_slot(FurnitureSlot(
            key="stall",
            slot_type=SlotType.STAND,
            max_occupants=1,
            default_pose="standing in the milking stall",
            allowed_poses=["standing", "leaning", "presenting udders"],
            can_restrain=True,
            restraint_points=[RestraintPoint.NECK, RestraintPoint.WAIST],
            exposes=["chest", "udders", "rear"],
            accessible_from=["milking"],
            occupied_desc="{name} stands ready in the stall.",
        ))
        
        self.add_slot(FurnitureSlot(
            key="milking",
            slot_type=SlotType.KNEEL,
            max_occupants=1,
            default_pose="kneeling at the stall",
            accessible_from=["stall"],
            occupied_desc="{name} tends to the milking.",
        ))


class BreedingStand(Furniture):
    """
    A stand to hold someone in position for breeding.
    """
    
    def at_object_creation(self):
        self.furniture_type = FurnitureType.FIXTURE
        self.size = "medium"
        self.is_anchored = True
        
        self.add_slot(FurnitureSlot(
            key="presenting",
            slot_type=SlotType.BEND,
            max_occupants=1,
            default_pose="bent over the breeding stand",
            allowed_poses=["presenting", "mounted", "bred"],
            can_restrain=True,
            restraint_points=[
                RestraintPoint.WRISTS, RestraintPoint.ANKLES,
                RestraintPoint.WAIST
            ],
            exposes=["rear", "genitals"],
            accessible_from=["mounting"],
            occupied_desc="{name} presents on the breeding stand.",
        ))
        
        self.add_slot(FurnitureSlot(
            key="mounting",
            slot_type=SlotType.MOUNT,
            max_occupants=1,
            default_pose="mounting",
            accessible_from=["presenting"],
            occupied_desc="{name} mounts eagerly.",
        ))


# =============================================================================
# EXPORTS
# =============================================================================

__all__ = [
    # Poles
    "DancingPole",
    "TiePost",
    "HitchingPost",
    # Hooks/Rings
    "CeilingHook",
    "WallRing",
    "FloorRing",
    # Bars
    "SpreaderBar",
    "BalletBar",
    "TowelBar",
    # Specialty
    "GloryHole",
    "MilkingStall",
    "BreedingStand",
]
