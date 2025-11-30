"""
Furniture Package
=================

Complete furniture system with:
- Base classes and slot management
- Seating (chairs, benches, thrones)
- Surfaces (tables, desks, altars)
- Support (beds, mattresses)
- Restraints (stocks, crosses, cages)
- Machines (fucking machines, sybian, milking)
- Fixtures (poles, hooks, rings)
- Commands for interaction

Total: 86 furniture types across 6 categories
"""

# Base
from .base import (
    FurnitureType,
    SlotType,
    RestraintPoint,
    FurnitureSlot,
    Furniture,
)

# Seating
from .seating import (
    Chair,
    Stool,
    Bench,
    Couch,
    Loveseat,
    Throne,
    Cushion,
    PetBed,
    SpankingBench,
    BreedingBench,
    Queening,
    ServingStool,
    SubmissiveBench,
)

# Surfaces
from .surfaces import (
    Table,
    Desk,
    Counter,
    Bar,
    Altar,
    SacrificialSlab,
    BreedingAltar,
    ExaminationTable,
    PilloryTable,
)

# Support
from .support import (
    Bed,
    FourPosterBed,
    Cot,
    Mattress,
    Futon,
    BondageBed,
    BreedingPit,
    KennelCage,
    HayPile,
    NestingArea,
)

# Restraints
from .restraints import (
    StandingStocks,
    Pillory,
    StAndrewsCross,
    WhippingPost,
    SuspensionFrame,
    KneelingStocks,
    DoggyStocks,
    Cage,
    HangingCage,
    StretchingRack,
    WoodenHorse,
)

# Machines
from .machines import (
    Machine,
    FuckingMachine,
    Sybian,
    BreedingMount,
    MilkingMachine,
    BreastPump,
    MilkingStanchion,
    SpankingMachine,
    TickleMachine,
)

# Fixtures
from .fixtures import (
    DancingPole,
    TiePost,
    HitchingPost,
    CeilingHook,
    WallRing,
    FloorRing,
    SpreaderBar,
    BalletBar,
    TowelBar,
    GloryHole,
    MilkingStall,
    BreedingStand,
)

# Commands
from .commands import (
    FurnitureCmdSet,
    CmdSit,
    CmdLie,
    CmdKneel,
    CmdBendOver,
    CmdGetUp,
    CmdUseFurniture,
    CmdRestrainOn,
    CmdReleaseFrom,
    CmdLockFurniture,
    CmdUnlockFurniture,
    CmdStartMachine,
    CmdStopMachine,
    CmdSetSpeed,
    CmdInflateKnot,
    CmdDeflateKnot,
    CmdExamineFurniture,
)


__all__ = [
    # Enums
    "FurnitureType",
    "SlotType", 
    "RestraintPoint",
    # Base
    "FurnitureSlot",
    "Furniture",
    # Seating (13)
    "Chair", "Stool", "Bench", "Couch", "Loveseat", "Throne", "Cushion", "PetBed",
    "SpankingBench", "BreedingBench", "Queening", "ServingStool", "SubmissiveBench",
    # Surfaces (9)
    "Table", "Desk", "Counter", "Bar",
    "Altar", "SacrificialSlab", "BreedingAltar",
    "ExaminationTable", "PilloryTable",
    # Support (10)
    "Bed", "FourPosterBed", "Cot", "Mattress", "Futon",
    "BondageBed", "BreedingPit", "KennelCage",
    "HayPile", "NestingArea",
    # Restraints (11)
    "StandingStocks", "Pillory", "StAndrewsCross", "WhippingPost", "SuspensionFrame",
    "KneelingStocks", "DoggyStocks",
    "Cage", "HangingCage",
    "StretchingRack", "WoodenHorse",
    # Machines (9)
    "Machine",
    "FuckingMachine", "Sybian", "BreedingMount",
    "MilkingMachine", "BreastPump", "MilkingStanchion",
    "SpankingMachine", "TickleMachine",
    # Fixtures (12)
    "DancingPole", "TiePost", "HitchingPost",
    "CeilingHook", "WallRing", "FloorRing",
    "SpreaderBar", "BalletBar", "TowelBar",
    "GloryHole", "MilkingStall", "BreedingStand",
    # Commands
    "FurnitureCmdSet",
]


# Convenience lookup
FURNITURE_TYPES = {
    # Seating
    "chair": Chair,
    "stool": Stool,
    "bench": Bench,
    "couch": Couch,
    "loveseat": Loveseat,
    "throne": Throne,
    "cushion": Cushion,
    "pet_bed": PetBed,
    "spanking_bench": SpankingBench,
    "breeding_bench": BreedingBench,
    "queening_stool": Queening,
    "serving_stool": ServingStool,
    "submissive_bench": SubmissiveBench,
    # Surfaces
    "table": Table,
    "desk": Desk,
    "counter": Counter,
    "bar": Bar,
    "altar": Altar,
    "sacrificial_slab": SacrificialSlab,
    "breeding_altar": BreedingAltar,
    "examination_table": ExaminationTable,
    "pillory_table": PilloryTable,
    # Support
    "bed": Bed,
    "four_poster": FourPosterBed,
    "cot": Cot,
    "mattress": Mattress,
    "futon": Futon,
    "bondage_bed": BondageBed,
    "breeding_pit": BreedingPit,
    "kennel": KennelCage,
    "hay_pile": HayPile,
    "nest": NestingArea,
    # Restraints
    "stocks": StandingStocks,
    "pillory": Pillory,
    "st_andrews_cross": StAndrewsCross,
    "whipping_post": WhippingPost,
    "suspension_frame": SuspensionFrame,
    "kneeling_stocks": KneelingStocks,
    "doggy_stocks": DoggyStocks,
    "cage": Cage,
    "hanging_cage": HangingCage,
    "rack": StretchingRack,
    "wooden_horse": WoodenHorse,
    # Machines
    "fucking_machine": FuckingMachine,
    "sybian": Sybian,
    "breeding_mount": BreedingMount,
    "milking_machine": MilkingMachine,
    "breast_pump": BreastPump,
    "milking_stanchion": MilkingStanchion,
    "spanking_machine": SpankingMachine,
    "tickle_machine": TickleMachine,
    # Fixtures
    "dancing_pole": DancingPole,
    "tie_post": TiePost,
    "hitching_post": HitchingPost,
    "ceiling_hook": CeilingHook,
    "wall_ring": WallRing,
    "floor_ring": FloorRing,
    "spreader_bar": SpreaderBar,
    "ballet_bar": BalletBar,
    "towel_bar": TowelBar,
    "glory_hole": GloryHole,
    "milking_stall": MilkingStall,
    "breeding_stand": BreedingStand,
}


def create_furniture(furniture_type: str, key: str = None, **kwargs):
    """
    Helper to create furniture by type string.
    
    Usage:
        chair = create_furniture("chair", key="wooden chair")
        bed = create_furniture("four_poster", key="canopy bed")
    """
    if furniture_type not in FURNITURE_TYPES:
        raise ValueError(f"Unknown furniture type: {furniture_type}")
    
    cls = FURNITURE_TYPES[furniture_type]
    
    # Evennia create_object would be used in actual game
    # This is a placeholder showing the pattern
    return cls
