"""
Universal Marks System
======================

A system for tracking marks on any surface - rooms, objects, bodies, body parts.

MARK TYPES:
    - Writing: Text written on surfaces
    - Drawing: Images drawn on surfaces
    - Fluids: Cum, urine, blood, etc. (with amount tracking)
    - Damage: Bruises, welts, cuts (fade over time)
    - Permanent: Brands, tattoos, scars, piercings

USAGE:
    # Make any typeclass markable
    class MyRoom(MarkableMixin, DefaultRoom):
        def at_object_creation(self):
            self.init_markable(surfaces=ROOM_SURFACES)
    
    # Add marks
    room.add_mark(WritingMark(
        text="Kilroy was here",
        location="north_wall",
        tool=WritingTool.CHARCOAL
    ))
    
    # Add fluids with amount tracking
    room.add_mark(FluidMark(
        fluid_type=FluidType.CUM,
        location="floor",
        amount_ml=25.0,
        source_name="Bob"
    ))
    
    # Damage on bodies
    body.add_mark(BruiseMark(
        location="left_cheek",
        severity=DamageSeverity.MODERATE,
        caused_by_name="Alice"
    ))
    
    # Internal fluids
    body.add_mark(InternalFluid(
        fluid_type=FluidType.CUM,
        cavity="womb",
        amount_ml=50.0,
        source_name="Bob"
    ))

ARCHITECTURE:
    marks/
    ├── base.py      - Mark base class, MarkableMixin, Surface
    ├── writing.py   - WritingMark, DrawingMark, SymbolMark
    ├── fluids.py    - FluidMark, InternalFluid, amount tracking
    ├── damage.py    - DamageMark, BruiseMark, WeltMark, etc.
    └── permanent.py - BrandMark, TattooMark, ScarMark, PiercingMark
"""

# =============================================================================
# BASE
# =============================================================================
from .base import (
    # Enums
    SurfaceType,
    SurfaceMaterial,
    MarkPersistence,
    
    # Classes
    Mark,
    Surface,
    MarkableMixin,
    
    # Registry
    register_mark_class,
    _MARK_CLASS_REGISTRY,
)

# =============================================================================
# WRITING
# =============================================================================
from .writing import (
    # Enums
    WritingTool,
    WritingStyle,
    
    # Classes
    WritingMark,
    DrawingMark,
    SymbolMark,
)

# =============================================================================
# FLUIDS
# =============================================================================
from .fluids import (
    # Enums
    FluidType,
    FluidState,
    
    # Classes
    FluidMark,
    InternalFluid,
    
    # Amount system
    AMOUNT_THRESHOLDS,
    amount_to_word,
    word_to_amount,
    describe_fluid_amount,
    describe_internal_amount,
)

# =============================================================================
# DAMAGE
# =============================================================================
from .damage import (
    # Enums
    DamageType,
    DamageSeverity,
    DamageState,
    
    # Classes
    DamageMark,
    BruiseMark,
    WeltMark,
    BiteMark,
    HandprintMark,
    RopeMarkMark,
    
    # Helpers
    create_slap_mark,
    create_spanking_marks,
    create_whip_marks,
    describe_damage_state,
)

# =============================================================================
# PERMANENT
# =============================================================================
from .permanent import (
    # Enums
    PermanentMarkType,
    BrandType,
    TattooStyle,
    ScarType,
    PiercingType,
    
    # Classes
    PermanentMark,
    BrandMark,
    TattooMark,
    ScarMark,
    PiercingMark,
    BirthmarkMark,
    
    # Helpers
    create_ownership_brand,
    create_slave_brand,
    damage_to_scar,
    describe_permanent_marks,
)


# =============================================================================
# REGISTER ALL MARK CLASSES
# =============================================================================
# This allows proper deserialization from stored dicts

# Writing
register_mark_class(WritingMark)
register_mark_class(DrawingMark)
register_mark_class(SymbolMark)

# Fluids
register_mark_class(FluidMark)
register_mark_class(InternalFluid)

# Damage
register_mark_class(DamageMark)
register_mark_class(BruiseMark)
register_mark_class(WeltMark)
register_mark_class(BiteMark)
register_mark_class(HandprintMark)
register_mark_class(RopeMarkMark)

# Permanent
register_mark_class(PermanentMark)
register_mark_class(BrandMark)
register_mark_class(TattooMark)
register_mark_class(ScarMark)
register_mark_class(PiercingMark)
register_mark_class(BirthmarkMark)


# =============================================================================
# SCENT
# =============================================================================
from .scent import (
    ScentType,
    ScentMarkMark,
    apply_scent_mark,
    get_scent_description,
    smells_like,
)

register_mark_class(ScentMarkMark)


# =============================================================================
# SURFACE PRESETS
# =============================================================================

def make_room_surfaces() -> list:
    """Create standard surfaces for a room."""
    return [
        Surface("north_wall", SurfaceType.WALL, SurfaceMaterial.STONE, "north wall"),
        Surface("south_wall", SurfaceType.WALL, SurfaceMaterial.STONE, "south wall"),
        Surface("east_wall", SurfaceType.WALL, SurfaceMaterial.STONE, "east wall"),
        Surface("west_wall", SurfaceType.WALL, SurfaceMaterial.STONE, "west wall"),
        Surface("floor", SurfaceType.FLOOR, SurfaceMaterial.STONE, "floor"),
        Surface("ceiling", SurfaceType.CEILING, SurfaceMaterial.STONE, "ceiling"),
    ]


def make_wood_room_surfaces() -> list:
    """Create surfaces for a wooden room."""
    return [
        Surface("north_wall", SurfaceType.WALL, SurfaceMaterial.WOOD, "north wall"),
        Surface("south_wall", SurfaceType.WALL, SurfaceMaterial.WOOD, "south wall"),
        Surface("east_wall", SurfaceType.WALL, SurfaceMaterial.WOOD, "east wall"),
        Surface("west_wall", SurfaceType.WALL, SurfaceMaterial.WOOD, "west wall"),
        Surface("floor", SurfaceType.FLOOR, SurfaceMaterial.WOOD, "wooden floor"),
        Surface("ceiling", SurfaceType.CEILING, SurfaceMaterial.WOOD, "ceiling"),
    ]


def make_bed_surfaces() -> list:
    """Create surfaces for a bed."""
    return [
        Surface("mattress", SurfaceType.MATTRESS, SurfaceMaterial.FABRIC, "mattress"),
        Surface("sheets", SurfaceType.SURFACE, SurfaceMaterial.FABRIC, "sheets"),
        Surface("pillow", SurfaceType.CUSHION, SurfaceMaterial.FABRIC, "pillow"),
        Surface("headboard", SurfaceType.HEADBOARD, SurfaceMaterial.WOOD, "headboard"),
        Surface("footboard", SurfaceType.FOOTBOARD, SurfaceMaterial.WOOD, "footboard"),
    ]


def make_chair_surfaces() -> list:
    """Create surfaces for a chair."""
    return [
        Surface("seat", SurfaceType.SEAT, SurfaceMaterial.FABRIC, "seat"),
        Surface("back", SurfaceType.BACK, SurfaceMaterial.FABRIC, "back"),
        Surface("armrests", SurfaceType.ARMREST, SurfaceMaterial.WOOD, "armrests"),
    ]


def make_table_surfaces() -> list:
    """Create surfaces for a table."""
    return [
        Surface("top", SurfaceType.TABLE_TOP, SurfaceMaterial.WOOD, "table top"),
        Surface("underside", SurfaceType.SURFACE, SurfaceMaterial.WOOD, "underside"),
    ]


def make_book_surfaces() -> list:
    """Create surfaces for a book."""
    return [
        Surface("cover", SurfaceType.COVER, SurfaceMaterial.LEATHER, "cover"),
        Surface("pages", SurfaceType.PAGE, SurfaceMaterial.PAPER, "pages"),
        Surface("spine", SurfaceType.SURFACE, SurfaceMaterial.LEATHER, "spine"),
    ]


def make_body_surfaces() -> list:
    """
    Create surfaces for a character body.
    This maps to body parts for the marking system.
    """
    return [
        # Head
        Surface("face", SurfaceType.SKIN, SurfaceMaterial.SKIN, "face"),
        Surface("forehead", SurfaceType.SKIN, SurfaceMaterial.SKIN, "forehead"),
        Surface("cheeks", SurfaceType.SKIN, SurfaceMaterial.SKIN, "cheeks"),
        Surface("lips", SurfaceType.SKIN, SurfaceMaterial.SKIN, "lips"),
        Surface("neck", SurfaceType.SKIN, SurfaceMaterial.SKIN, "neck"),
        Surface("throat", SurfaceType.SKIN, SurfaceMaterial.SKIN, "throat"),
        
        # Torso
        Surface("chest", SurfaceType.SKIN, SurfaceMaterial.SKIN, "chest"),
        Surface("breasts", SurfaceType.SKIN, SurfaceMaterial.SKIN, "breasts"),
        Surface("stomach", SurfaceType.SKIN, SurfaceMaterial.SKIN, "stomach"),
        Surface("belly", SurfaceType.SKIN, SurfaceMaterial.SKIN, "belly"),
        Surface("back", SurfaceType.SKIN, SurfaceMaterial.SKIN, "back"),
        Surface("lower_back", SurfaceType.SKIN, SurfaceMaterial.SKIN, "lower back"),
        Surface("sides", SurfaceType.SKIN, SurfaceMaterial.SKIN, "sides"),
        
        # Arms
        Surface("shoulders", SurfaceType.SKIN, SurfaceMaterial.SKIN, "shoulders"),
        Surface("upper_arms", SurfaceType.SKIN, SurfaceMaterial.SKIN, "upper arms"),
        Surface("forearms", SurfaceType.SKIN, SurfaceMaterial.SKIN, "forearms"),
        Surface("wrists", SurfaceType.SKIN, SurfaceMaterial.SKIN, "wrists"),
        Surface("hands", SurfaceType.SKIN, SurfaceMaterial.SKIN, "hands"),
        
        # Lower body
        Surface("hips", SurfaceType.SKIN, SurfaceMaterial.SKIN, "hips"),
        Surface("ass", SurfaceType.SKIN, SurfaceMaterial.SKIN, "ass"),
        Surface("thighs", SurfaceType.SKIN, SurfaceMaterial.SKIN, "thighs"),
        Surface("inner_thighs", SurfaceType.SKIN, SurfaceMaterial.SKIN, "inner thighs"),
        Surface("calves", SurfaceType.SKIN, SurfaceMaterial.SKIN, "calves"),
        Surface("ankles", SurfaceType.SKIN, SurfaceMaterial.SKIN, "ankles"),
        Surface("feet", SurfaceType.SKIN, SurfaceMaterial.SKIN, "feet"),
        
        # Intimate
        Surface("groin", SurfaceType.SKIN, SurfaceMaterial.SKIN, "groin"),
        Surface("pubic_area", SurfaceType.SKIN, SurfaceMaterial.SKIN, "pubic area"),
        
        # Internal cavities
        Surface("mouth", SurfaceType.CAVITY, SurfaceMaterial.FLESH, "mouth"),
        Surface("throat_cavity", SurfaceType.CAVITY, SurfaceMaterial.FLESH, "throat"),
        Surface("vagina", SurfaceType.CAVITY, SurfaceMaterial.FLESH, "vagina"),
        Surface("womb", SurfaceType.CAVITY, SurfaceMaterial.FLESH, "womb"),
        Surface("ass_cavity", SurfaceType.CAVITY, SurfaceMaterial.FLESH, "ass"),
    ]


# Preset constants
ROOM_SURFACES = make_room_surfaces()
WOOD_ROOM_SURFACES = make_wood_room_surfaces()
BED_SURFACES = make_bed_surfaces()
CHAIR_SURFACES = make_chair_surfaces()
TABLE_SURFACES = make_table_surfaces()
BOOK_SURFACES = make_book_surfaces()
BODY_SURFACES = make_body_surfaces()


__all__ = [
    # Base
    "SurfaceType",
    "SurfaceMaterial",
    "MarkPersistence",
    "Mark",
    "Surface",
    "MarkableMixin",
    "register_mark_class",
    
    # Writing
    "WritingTool",
    "WritingStyle",
    "WritingMark",
    "DrawingMark",
    "SymbolMark",
    
    # Fluids
    "FluidType",
    "FluidState",
    "FluidMark",
    "InternalFluid",
    "AMOUNT_THRESHOLDS",
    "amount_to_word",
    "word_to_amount",
    "describe_fluid_amount",
    "describe_internal_amount",
    
    # Damage
    "DamageType",
    "DamageSeverity",
    "DamageState",
    "DamageMark",
    "BruiseMark",
    "WeltMark",
    "BiteMark",
    "HandprintMark",
    "RopeMarkMark",
    "create_slap_mark",
    "create_spanking_marks",
    "create_whip_marks",
    "describe_damage_state",
    
    # Permanent
    "PermanentMarkType",
    "BrandType",
    "TattooStyle",
    "ScarType",
    "PiercingType",
    "PermanentMark",
    "BrandMark",
    "TattooMark",
    "ScarMark",
    "PiercingMark",
    "BirthmarkMark",
    "create_ownership_brand",
    "create_slave_brand",
    "damage_to_scar",
    "describe_permanent_marks",
    
    # Scent
    "ScentType",
    "ScentMarkMark",
    "apply_scent_mark",
    "get_scent_description",
    "smells_like",
    
    # Surface presets
    "make_room_surfaces",
    "make_wood_room_surfaces",
    "make_bed_surfaces",
    "make_chair_surfaces",
    "make_table_surfaces",
    "make_book_surfaces",
    "make_body_surfaces",
    "ROOM_SURFACES",
    "WOOD_ROOM_SURFACES",
    "BED_SURFACES",
    "CHAIR_SURFACES",
    "TABLE_SURFACES",
    "BOOK_SURFACES",
    "BODY_SURFACES",
]
