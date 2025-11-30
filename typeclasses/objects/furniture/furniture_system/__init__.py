"""
Furniture System
================

A comprehensive furniture system for the MUD.

INHERITANCE HIERARCHY:
    Furniture (base.py)
    ├── Seating (seating.py)
    │   ├── Chair, ArmChair, DiningChair
    │   ├── Bench, ParkBench, PaddedBench
    │   ├── Throne
    │   ├── Stool, BarStool
    │   └── Couch, Loveseat, Chaise
    │
    ├── Surface (surfaces.py)
    │   ├── Bed, SingleBed, DoubleBed, KingBed, FourPosterBed, Futon, Hammock
    │   ├── Table, DiningTable, CoffeeTable, PoolTable
    │   ├── Altar, SacrificialAltar
    │   ├── Counter, KitchenCounter, BarCounter
    │   └── Desk, WritingDesk, ExecutiveDesk
    │
    ├── Support (supports.py)
    │   ├── Wall, PaddedWall, DungeonWall
    │   ├── Pillar, OrnamentedPillar, BondagePillar
    │   └── Post, WhippingPost, TetherPost, HitchingPost
    │
    ├── Restraint (restraints.py)
    │   ├── Stocks, WoodenStocks, IronStocks
    │   ├── Pillory
    │   ├── Cross, StAndrewsCross, LatinCross
    │   ├── Frame, SpreadFrame, SuspensionFrame
    │   ├── Cage, StandingCage, KneelingCage, DogCage
    │   ├── BreedingBench, AdjustableBreedingBench
    │   └── SpankingHorse, Sawhorse, PaddedHorse
    │
    └── Machine (machines.py)
        ├── Sybian, DualSybian
        ├── FuckingMachine, PistonMachine, RotatingMachine, TentacleMachine
        ├── MilkingStation, BreastPumps, CockMilker
        └── VibrationPlatform, VibratingChair, VibratingBed

USAGE:
    from typeclasses.objects.furniture import Bed, Stocks, Sybian
    
    # Create furniture
    bed = create_object(Bed, key="four-poster bed", location=room)
    
    # Character uses furniture
    success, msg = bed.use(character, slot_key="mattress")
    
    # Leave furniture
    success, msg = bed.release(character)
    
    # For restraints
    stocks.use(character, slot_key="locked")
    stocks.lock_occupant(character)  # Lock them in
    stocks.unlock_occupant(character)  # Release
    
    # For machines
    sybian.use(character)
    sybian.set_power(PowerLevel.MEDIUM)
    sybian.lock_power()  # Occupant can't change it

POSITION INTEGRATION:
    Positions can require furniture types via FurnitureType enum.
    The position system checks if the target furniture provides the
    right type/tags before allowing the position.
    
    # From positions:
    if furniture.supports_furniture_type(FurnitureType.BED):
        # Position can be used here

TICK INTEGRATION:
    Machines integrate with sexual_tick.py:
    
    # In sexual_tick.py:
    for machine in room.contents_get(content_type="furniture"):
        if hasattr(machine, "process_tick"):
            effects = machine.process_tick()
            for char_dbref, message in effects:
                # Apply arousal, send messages
"""

# =============================================================================
# BASE
# =============================================================================

from .base import (
    # Enums
    FurnitureType,
    FurnitureState,
    OccupantPosition,
    
    # Data classes
    FurnitureSlot,
    Occupant,
    
    # Base class
    Furniture,
)

# =============================================================================
# SEATING
# =============================================================================

from .seating import (
    # Base
    Seating,
    
    # Chairs
    Chair,
    ArmChair,
    DiningChair,
    
    # Benches
    Bench,
    ParkBench,
    PaddedBench,
    
    # Throne
    Throne,
    
    # Stools
    Stool,
    BarStool,
    
    # Couches
    Couch,
    Loveseat,
    Chaise,
)

# =============================================================================
# SURFACES
# =============================================================================

from .surfaces import (
    # Base
    Surface,
    
    # Beds
    Bed,
    SingleBed,
    DoubleBed,
    KingBed,
    FourPosterBed,
    Futon,
    Hammock,
    
    # Tables
    Table,
    DiningTable,
    CoffeeTable,
    PoolTable,
    
    # Altars
    Altar,
    SacrificialAltar,
    
    # Counters
    Counter,
    KitchenCounter,
    BarCounter,
    
    # Desks
    Desk,
    WritingDesk,
    ExecutiveDesk,
)

# =============================================================================
# SUPPORTS
# =============================================================================

from .supports import (
    # Base
    Support,
    
    # Walls
    Wall,
    PaddedWall,
    DungeonWall,
    
    # Pillars
    Pillar,
    OrnamentedPillar,
    BondagePillar,
    
    # Posts
    Post,
    WhippingPost,
    TetherPost,
    HitchingPost,
)

# =============================================================================
# RESTRAINTS
# =============================================================================

from .restraints import (
    # Base
    Restraint,
    
    # Stocks
    Stocks,
    WoodenStocks,
    IronStocks,
    
    # Pillory
    Pillory,
    
    # Crosses
    Cross,
    StAndrewsCross,
    LatinCross,
    
    # Frames
    Frame,
    SpreadFrame,
    SuspensionFrame,
    
    # Cages
    Cage,
    StandingCage,
    KneelingCage,
    DogCage,
    
    # Breeding Bench
    BreedingBench,
    AdjustableBreedingBench,
    
    # Spanking Horse
    SpankingHorse,
    Sawhorse,
    PaddedHorse,
)

# =============================================================================
# MACHINES
# =============================================================================

from .machines import (
    # Enums
    PowerLevel,
    AttachmentType,
    
    # Data classes
    MachineAttachment,
    
    # Base
    Machine,
    
    # Sybians
    Sybian,
    DualSybian,
    
    # Fucking Machines
    FuckingMachine,
    PistonMachine,
    RotatingMachine,
    TentacleMachine,
    
    # Milking
    MilkingStation,
    BreastPumps,
    CockMilker,
    
    # Vibration
    VibrationPlatform,
    VibratingChair,
    VibratingBed,
)


# =============================================================================
# ALL EXPORTS
# =============================================================================

__all__ = [
    # --- Base ---
    "FurnitureType",
    "FurnitureState",
    "OccupantPosition",
    "FurnitureSlot",
    "Occupant",
    "Furniture",
    
    # --- Seating ---
    "Seating",
    "Chair",
    "ArmChair",
    "DiningChair",
    "Bench",
    "ParkBench",
    "PaddedBench",
    "Throne",
    "Stool",
    "BarStool",
    "Couch",
    "Loveseat",
    "Chaise",
    
    # --- Surfaces ---
    "Surface",
    "Bed",
    "SingleBed",
    "DoubleBed",
    "KingBed",
    "FourPosterBed",
    "Futon",
    "Hammock",
    "Table",
    "DiningTable",
    "CoffeeTable",
    "PoolTable",
    "Altar",
    "SacrificialAltar",
    "Counter",
    "KitchenCounter",
    "BarCounter",
    "Desk",
    "WritingDesk",
    "ExecutiveDesk",
    
    # --- Supports ---
    "Support",
    "Wall",
    "PaddedWall",
    "DungeonWall",
    "Pillar",
    "OrnamentedPillar",
    "BondagePillar",
    "Post",
    "WhippingPost",
    "TetherPost",
    "HitchingPost",
    
    # --- Restraints ---
    "Restraint",
    "Stocks",
    "WoodenStocks",
    "IronStocks",
    "Pillory",
    "Cross",
    "StAndrewsCross",
    "LatinCross",
    "Frame",
    "SpreadFrame",
    "SuspensionFrame",
    "Cage",
    "StandingCage",
    "KneelingCage",
    "DogCage",
    "BreedingBench",
    "AdjustableBreedingBench",
    "SpankingHorse",
    "Sawhorse",
    "PaddedHorse",
    
    # --- Machines ---
    "PowerLevel",
    "AttachmentType",
    "MachineAttachment",
    "Machine",
    "Sybian",
    "DualSybian",
    "FuckingMachine",
    "PistonMachine",
    "RotatingMachine",
    "TentacleMachine",
    "MilkingStation",
    "BreastPumps",
    "CockMilker",
    "VibrationPlatform",
    "VibratingChair",
    "VibratingBed",
]
