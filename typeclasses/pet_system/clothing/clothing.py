"""
Clothing System
===============

Comprehensive clothing system with:
- Body slots and layering
- Clothing states (worn, lifted, torn, removed)
- Material and coverage properties
- Integration with body exposure mechanics
"""

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any, Set, Tuple
from enum import Enum


# =============================================================================
# ENUMS
# =============================================================================

class ClothingSlot(Enum):
    """Body slots for clothing."""
    # Head
    HEAD = "head"
    FACE = "face"
    NECK = "neck"
    
    # Upper body
    SHOULDERS = "shoulders"
    CHEST = "chest"
    BACK = "back"
    ARMS = "arms"
    HANDS = "hands"
    
    # Lower body
    WAIST = "waist"
    HIPS = "hips"
    GROIN = "groin"
    REAR = "rear"
    THIGHS = "thighs"
    LEGS = "legs"
    FEET = "feet"
    
    # Full body
    FULL_BODY = "full_body"
    
    # Accessories
    EARS = "ears"
    TAIL = "tail"
    WINGS = "wings"


class ClothingLayer(Enum):
    """Layering order for clothing."""
    SKIN = 0        # Bodypaint, tattoo covers
    UNDERWEAR = 1   # Bras, panties, briefs
    BASE = 2        # Shirts, pants, skirts
    MIDDLE = 3      # Sweaters, vests
    OUTER = 4       # Jackets, coats
    ACCESSORY = 5   # Jewelry, belts


class ClothingState(Enum):
    """State of a clothing item."""
    WORN = "worn"           # Normal, fully on
    LIFTED = "lifted"       # Pushed up/aside
    LOWERED = "lowered"     # Pulled down
    UNBUTTONED = "unbuttoned"  # Open but on
    TORN = "torn"           # Damaged
    REMOVED = "removed"     # Taken off


class ClothingMaterial(Enum):
    """Material types affecting properties."""
    COTTON = "cotton"
    SILK = "silk"
    LEATHER = "leather"
    LATEX = "latex"
    RUBBER = "rubber"
    LACE = "lace"
    MESH = "mesh"
    DENIM = "denim"
    WOOL = "wool"
    FUR = "fur"
    METAL = "metal"
    CHAIN = "chain"


class CoverageLevel(Enum):
    """How much the item covers."""
    NONE = 0        # Doesn't cover (jewelry)
    MINIMAL = 1     # String bikini, thong
    PARTIAL = 2     # Normal underwear, crop top
    MODERATE = 3    # T-shirt, shorts
    FULL = 4        # Long pants, full dress
    COMPLETE = 5    # Full coverage suit


# =============================================================================
# CLOTHING ITEM
# =============================================================================

@dataclass
class ClothingItem:
    """A piece of clothing."""
    key: str
    name: str
    
    # Where it goes
    slots: List[ClothingSlot] = field(default_factory=list)
    layer: ClothingLayer = ClothingLayer.BASE
    
    # Properties
    material: ClothingMaterial = ClothingMaterial.COTTON
    color: str = "white"
    coverage: CoverageLevel = CoverageLevel.MODERATE
    
    # State
    state: ClothingState = ClothingState.REMOVED
    
    # Durability
    durability: int = 100  # 0-100, damaged when low
    can_tear: bool = True
    is_waterproof: bool = False
    
    # Features
    is_lockable: bool = False
    is_locked: bool = False
    has_zipper: bool = False
    has_buttons: bool = False
    has_snap: bool = False      # Easy removal
    
    # Access features
    has_crotch_access: bool = False     # Can be opened for access
    has_breast_access: bool = False
    has_rear_access: bool = False
    crotch_open: bool = False
    breast_open: bool = False
    rear_open: bool = False
    
    # Description
    short_desc: str = ""
    worn_desc: str = ""
    
    def get_covered_slots(self) -> List[ClothingSlot]:
        """Get slots currently covered based on state."""
        if self.state in (ClothingState.REMOVED, ClothingState.TORN):
            return []
        
        if self.state == ClothingState.LIFTED:
            # Lifted items don't cover lower slots
            return [s for s in self.slots if s not in (
                ClothingSlot.GROIN, ClothingSlot.REAR, ClothingSlot.THIGHS
            )]
        
        if self.state == ClothingState.LOWERED:
            # Lowered items don't cover upper slots
            return [s for s in self.slots if s not in (
                ClothingSlot.CHEST, ClothingSlot.SHOULDERS
            )]
        
        return self.slots
    
    def is_covering(self, slot: ClothingSlot) -> bool:
        """Check if currently covering a slot."""
        return slot in self.get_covered_slots()
    
    def get_transparency(self) -> float:
        """Get transparency level 0-1 based on material."""
        transparency = {
            ClothingMaterial.MESH: 0.8,
            ClothingMaterial.LACE: 0.6,
            ClothingMaterial.SILK: 0.2,
            ClothingMaterial.LATEX: 0.0,
            ClothingMaterial.LEATHER: 0.0,
            ClothingMaterial.COTTON: 0.0,
            ClothingMaterial.DENIM: 0.0,
        }
        return transparency.get(self.material, 0.0)
    
    def lift(self) -> str:
        """Lift/push up the clothing."""
        if self.state == ClothingState.REMOVED:
            return f"The {self.name} isn't being worn."
        
        if self.is_locked:
            return f"The {self.name} is locked and can't be lifted."
        
        self.state = ClothingState.LIFTED
        return f"You lift the {self.name}, exposing what's beneath."
    
    def lower(self) -> str:
        """Lower/pull down the clothing."""
        if self.state == ClothingState.REMOVED:
            return f"The {self.name} isn't being worn."
        
        if self.is_locked:
            return f"The {self.name} is locked and can't be lowered."
        
        self.state = ClothingState.LOWERED
        return f"You lower the {self.name}."
    
    def restore(self) -> str:
        """Restore clothing to normal worn state."""
        if self.state == ClothingState.REMOVED:
            return f"The {self.name} isn't being worn."
        
        if self.state == ClothingState.TORN:
            return f"The {self.name} is too damaged to restore."
        
        self.state = ClothingState.WORN
        return f"You straighten the {self.name}."
    
    def tear(self, force: int = 50) -> str:
        """Attempt to tear the clothing."""
        if not self.can_tear:
            return f"The {self.name} can't be torn."
        
        # Material resistance
        resistance = {
            ClothingMaterial.LEATHER: 30,
            ClothingMaterial.DENIM: 25,
            ClothingMaterial.LATEX: 20,
            ClothingMaterial.COTTON: 10,
            ClothingMaterial.SILK: 5,
            ClothingMaterial.LACE: 0,
            ClothingMaterial.MESH: 0,
        }
        
        required = resistance.get(self.material, 10)
        
        if force >= required:
            self.state = ClothingState.TORN
            self.durability = 0
            return f"You tear the {self.name} apart!"
        
        self.durability -= force // 2
        return f"The {self.name} holds, but is damaged."
    
    def open_access(self, area: str) -> str:
        """Open an access point."""
        if area == "crotch" and self.has_crotch_access:
            self.crotch_open = True
            return f"You open the crotch access on the {self.name}."
        elif area == "breast" and self.has_breast_access:
            self.breast_open = True
            return f"You open the breast access on the {self.name}."
        elif area == "rear" and self.has_rear_access:
            self.rear_open = True
            return f"You open the rear access on the {self.name}."
        
        return f"The {self.name} doesn't have {area} access."
    
    def close_access(self, area: str) -> str:
        """Close an access point."""
        if area == "crotch":
            self.crotch_open = False
        elif area == "breast":
            self.breast_open = False
        elif area == "rear":
            self.rear_open = False
        
        return f"You close the {area} access on the {self.name}."
    
    def lock(self) -> bool:
        """Lock the clothing on."""
        if self.is_lockable:
            self.is_locked = True
            return True
        return False
    
    def unlock(self) -> bool:
        """Unlock the clothing."""
        self.is_locked = False
        return True
    
    def to_dict(self) -> dict:
        return {
            "key": self.key,
            "name": self.name,
            "slots": [s.value for s in self.slots],
            "layer": self.layer.value,
            "material": self.material.value,
            "color": self.color,
            "coverage": self.coverage.value,
            "state": self.state.value,
            "durability": self.durability,
            "can_tear": self.can_tear,
            "is_waterproof": self.is_waterproof,
            "is_lockable": self.is_lockable,
            "is_locked": self.is_locked,
            "has_zipper": self.has_zipper,
            "has_buttons": self.has_buttons,
            "has_snap": self.has_snap,
            "has_crotch_access": self.has_crotch_access,
            "has_breast_access": self.has_breast_access,
            "has_rear_access": self.has_rear_access,
            "crotch_open": self.crotch_open,
            "breast_open": self.breast_open,
            "rear_open": self.rear_open,
            "short_desc": self.short_desc,
            "worn_desc": self.worn_desc,
        }
    
    @classmethod
    def from_dict(cls, data: dict) -> "ClothingItem":
        item = cls(
            key=data["key"],
            name=data["name"],
        )
        item.slots = [ClothingSlot(s) for s in data.get("slots", [])]
        item.layer = ClothingLayer(data.get("layer", 2))
        item.material = ClothingMaterial(data.get("material", "cotton"))
        item.color = data.get("color", "white")
        item.coverage = CoverageLevel(data.get("coverage", 3))
        item.state = ClothingState(data.get("state", "removed"))
        item.durability = data.get("durability", 100)
        item.can_tear = data.get("can_tear", True)
        item.is_waterproof = data.get("is_waterproof", False)
        item.is_lockable = data.get("is_lockable", False)
        item.is_locked = data.get("is_locked", False)
        item.has_zipper = data.get("has_zipper", False)
        item.has_buttons = data.get("has_buttons", False)
        item.has_snap = data.get("has_snap", False)
        item.has_crotch_access = data.get("has_crotch_access", False)
        item.has_breast_access = data.get("has_breast_access", False)
        item.has_rear_access = data.get("has_rear_access", False)
        item.crotch_open = data.get("crotch_open", False)
        item.breast_open = data.get("breast_open", False)
        item.rear_open = data.get("rear_open", False)
        item.short_desc = data.get("short_desc", "")
        item.worn_desc = data.get("worn_desc", "")
        return item


# =============================================================================
# CLOTHING DEFINITIONS
# =============================================================================

# ----- UNDERWEAR -----

PANTIES = ClothingItem(
    key="panties",
    name="Panties",
    slots=[ClothingSlot.GROIN, ClothingSlot.HIPS],
    layer=ClothingLayer.UNDERWEAR,
    material=ClothingMaterial.COTTON,
    coverage=CoverageLevel.PARTIAL,
    short_desc="Simple cotton panties.",
)

THONG = ClothingItem(
    key="thong",
    name="Thong",
    slots=[ClothingSlot.GROIN],
    layer=ClothingLayer.UNDERWEAR,
    material=ClothingMaterial.LACE,
    coverage=CoverageLevel.MINIMAL,
    short_desc="A skimpy lace thong.",
)

LACE_PANTIES = ClothingItem(
    key="lace_panties",
    name="Lace Panties",
    slots=[ClothingSlot.GROIN, ClothingSlot.HIPS],
    layer=ClothingLayer.UNDERWEAR,
    material=ClothingMaterial.LACE,
    coverage=CoverageLevel.PARTIAL,
    short_desc="Delicate lace panties.",
)

CROTCHLESS_PANTIES = ClothingItem(
    key="crotchless_panties",
    name="Crotchless Panties",
    slots=[ClothingSlot.HIPS],
    layer=ClothingLayer.UNDERWEAR,
    material=ClothingMaterial.LACE,
    coverage=CoverageLevel.MINIMAL,
    has_crotch_access=True,
    crotch_open=True,
    short_desc="Decorative panties with an open crotch.",
)

BRA = ClothingItem(
    key="bra",
    name="Bra",
    slots=[ClothingSlot.CHEST],
    layer=ClothingLayer.UNDERWEAR,
    material=ClothingMaterial.COTTON,
    coverage=CoverageLevel.PARTIAL,
    short_desc="A supportive bra.",
)

LACE_BRA = ClothingItem(
    key="lace_bra",
    name="Lace Bra",
    slots=[ClothingSlot.CHEST],
    layer=ClothingLayer.UNDERWEAR,
    material=ClothingMaterial.LACE,
    coverage=CoverageLevel.PARTIAL,
    short_desc="A delicate lace bra.",
)

CUPLESS_BRA = ClothingItem(
    key="cupless_bra",
    name="Cupless Bra",
    slots=[ClothingSlot.CHEST],
    layer=ClothingLayer.UNDERWEAR,
    material=ClothingMaterial.LEATHER,
    coverage=CoverageLevel.MINIMAL,
    has_breast_access=True,
    breast_open=True,
    short_desc="A bra that frames but doesn't cover.",
)

BRIEFS = ClothingItem(
    key="briefs",
    name="Briefs",
    slots=[ClothingSlot.GROIN, ClothingSlot.HIPS],
    layer=ClothingLayer.UNDERWEAR,
    material=ClothingMaterial.COTTON,
    coverage=CoverageLevel.PARTIAL,
    short_desc="Standard cotton briefs.",
)

BOXERS = ClothingItem(
    key="boxers",
    name="Boxers",
    slots=[ClothingSlot.GROIN, ClothingSlot.HIPS, ClothingSlot.THIGHS],
    layer=ClothingLayer.UNDERWEAR,
    material=ClothingMaterial.COTTON,
    coverage=CoverageLevel.MODERATE,
    short_desc="Loose cotton boxer shorts.",
)

JOCKSTRAP = ClothingItem(
    key="jockstrap",
    name="Jockstrap",
    slots=[ClothingSlot.GROIN],
    layer=ClothingLayer.UNDERWEAR,
    material=ClothingMaterial.COTTON,
    coverage=CoverageLevel.MINIMAL,
    has_rear_access=True,
    rear_open=True,
    short_desc="An athletic jockstrap leaving the rear bare.",
)

# ----- TOPS -----

TSHIRT = ClothingItem(
    key="tshirt",
    name="T-Shirt",
    slots=[ClothingSlot.CHEST, ClothingSlot.BACK, ClothingSlot.SHOULDERS],
    layer=ClothingLayer.BASE,
    material=ClothingMaterial.COTTON,
    coverage=CoverageLevel.MODERATE,
    short_desc="A casual cotton t-shirt.",
)

CROP_TOP = ClothingItem(
    key="crop_top",
    name="Crop Top",
    slots=[ClothingSlot.CHEST],
    layer=ClothingLayer.BASE,
    material=ClothingMaterial.COTTON,
    coverage=CoverageLevel.PARTIAL,
    short_desc="A short top exposing the midriff.",
)

BLOUSE = ClothingItem(
    key="blouse",
    name="Blouse",
    slots=[ClothingSlot.CHEST, ClothingSlot.BACK, ClothingSlot.SHOULDERS],
    layer=ClothingLayer.BASE,
    material=ClothingMaterial.SILK,
    coverage=CoverageLevel.MODERATE,
    has_buttons=True,
    short_desc="An elegant silk blouse.",
)

TANK_TOP = ClothingItem(
    key="tank_top",
    name="Tank Top",
    slots=[ClothingSlot.CHEST, ClothingSlot.BACK],
    layer=ClothingLayer.BASE,
    material=ClothingMaterial.COTTON,
    coverage=CoverageLevel.PARTIAL,
    short_desc="A sleeveless tank top.",
)

CORSET = ClothingItem(
    key="corset",
    name="Corset",
    slots=[ClothingSlot.CHEST, ClothingSlot.WAIST],
    layer=ClothingLayer.BASE,
    material=ClothingMaterial.LEATHER,
    coverage=CoverageLevel.MODERATE,
    can_tear=False,
    is_lockable=True,
    short_desc="A tight-lacing corset.",
)

LATEX_TOP = ClothingItem(
    key="latex_top",
    name="Latex Top",
    slots=[ClothingSlot.CHEST, ClothingSlot.BACK],
    layer=ClothingLayer.BASE,
    material=ClothingMaterial.LATEX,
    coverage=CoverageLevel.MODERATE,
    can_tear=False,
    has_zipper=True,
    short_desc="A shiny, form-fitting latex top.",
)

# ----- BOTTOMS -----

PANTS = ClothingItem(
    key="pants",
    name="Pants",
    slots=[ClothingSlot.HIPS, ClothingSlot.GROIN, ClothingSlot.REAR, ClothingSlot.THIGHS, ClothingSlot.LEGS],
    layer=ClothingLayer.BASE,
    material=ClothingMaterial.COTTON,
    coverage=CoverageLevel.FULL,
    has_zipper=True,
    short_desc="Standard pants.",
)

JEANS = ClothingItem(
    key="jeans",
    name="Jeans",
    slots=[ClothingSlot.HIPS, ClothingSlot.GROIN, ClothingSlot.REAR, ClothingSlot.THIGHS, ClothingSlot.LEGS],
    layer=ClothingLayer.BASE,
    material=ClothingMaterial.DENIM,
    coverage=CoverageLevel.FULL,
    has_zipper=True,
    short_desc="Durable denim jeans.",
)

SHORTS = ClothingItem(
    key="shorts",
    name="Shorts",
    slots=[ClothingSlot.HIPS, ClothingSlot.GROIN, ClothingSlot.REAR, ClothingSlot.THIGHS],
    layer=ClothingLayer.BASE,
    material=ClothingMaterial.COTTON,
    coverage=CoverageLevel.MODERATE,
    has_zipper=True,
    short_desc="Casual shorts.",
)

SKIRT = ClothingItem(
    key="skirt",
    name="Skirt",
    slots=[ClothingSlot.HIPS, ClothingSlot.GROIN, ClothingSlot.REAR, ClothingSlot.THIGHS],
    layer=ClothingLayer.BASE,
    material=ClothingMaterial.COTTON,
    coverage=CoverageLevel.MODERATE,
    short_desc="A knee-length skirt.",
)

MINI_SKIRT = ClothingItem(
    key="mini_skirt",
    name="Mini Skirt",
    slots=[ClothingSlot.HIPS, ClothingSlot.GROIN, ClothingSlot.REAR],
    layer=ClothingLayer.BASE,
    material=ClothingMaterial.COTTON,
    coverage=CoverageLevel.PARTIAL,
    short_desc="A very short mini skirt.",
)

LATEX_PANTS = ClothingItem(
    key="latex_pants",
    name="Latex Pants",
    slots=[ClothingSlot.HIPS, ClothingSlot.GROIN, ClothingSlot.REAR, ClothingSlot.THIGHS, ClothingSlot.LEGS],
    layer=ClothingLayer.BASE,
    material=ClothingMaterial.LATEX,
    coverage=CoverageLevel.FULL,
    can_tear=False,
    has_crotch_access=True,
    short_desc="Skin-tight latex pants with crotch zipper.",
)

LEATHER_PANTS = ClothingItem(
    key="leather_pants",
    name="Leather Pants",
    slots=[ClothingSlot.HIPS, ClothingSlot.GROIN, ClothingSlot.REAR, ClothingSlot.THIGHS, ClothingSlot.LEGS],
    layer=ClothingLayer.BASE,
    material=ClothingMaterial.LEATHER,
    coverage=CoverageLevel.FULL,
    can_tear=False,
    has_zipper=True,
    short_desc="Tight leather pants.",
)

CHAPS = ClothingItem(
    key="chaps",
    name="Leather Chaps",
    slots=[ClothingSlot.THIGHS, ClothingSlot.LEGS],
    layer=ClothingLayer.BASE,
    material=ClothingMaterial.LEATHER,
    coverage=CoverageLevel.PARTIAL,
    can_tear=False,
    short_desc="Assless leather chaps.",
)

# ----- DRESSES -----

DRESS = ClothingItem(
    key="dress",
    name="Dress",
    slots=[ClothingSlot.CHEST, ClothingSlot.BACK, ClothingSlot.WAIST, 
           ClothingSlot.HIPS, ClothingSlot.GROIN, ClothingSlot.REAR, ClothingSlot.THIGHS],
    layer=ClothingLayer.BASE,
    material=ClothingMaterial.COTTON,
    coverage=CoverageLevel.MODERATE,
    has_zipper=True,
    short_desc="A simple dress.",
)

COCKTAIL_DRESS = ClothingItem(
    key="cocktail_dress",
    name="Cocktail Dress",
    slots=[ClothingSlot.CHEST, ClothingSlot.BACK, ClothingSlot.WAIST,
           ClothingSlot.HIPS, ClothingSlot.GROIN, ClothingSlot.REAR],
    layer=ClothingLayer.BASE,
    material=ClothingMaterial.SILK,
    coverage=CoverageLevel.MODERATE,
    has_zipper=True,
    short_desc="An elegant short cocktail dress.",
)

LATEX_DRESS = ClothingItem(
    key="latex_dress",
    name="Latex Dress",
    slots=[ClothingSlot.CHEST, ClothingSlot.BACK, ClothingSlot.WAIST,
           ClothingSlot.HIPS, ClothingSlot.GROIN, ClothingSlot.REAR],
    layer=ClothingLayer.BASE,
    material=ClothingMaterial.LATEX,
    coverage=CoverageLevel.MODERATE,
    can_tear=False,
    has_zipper=True,
    short_desc="A shiny, form-hugging latex dress.",
)

# ----- FULL BODY -----

CATSUIT = ClothingItem(
    key="catsuit",
    name="Catsuit",
    slots=[ClothingSlot.FULL_BODY],
    layer=ClothingLayer.BASE,
    material=ClothingMaterial.LATEX,
    coverage=CoverageLevel.COMPLETE,
    can_tear=False,
    has_zipper=True,
    has_crotch_access=True,
    short_desc="A full-body latex catsuit.",
)

BODYSUIT = ClothingItem(
    key="bodysuit",
    name="Bodysuit",
    slots=[ClothingSlot.CHEST, ClothingSlot.BACK, ClothingSlot.WAIST,
           ClothingSlot.HIPS, ClothingSlot.GROIN],
    layer=ClothingLayer.BASE,
    material=ClothingMaterial.COTTON,
    coverage=CoverageLevel.MODERATE,
    has_snap=True,
    has_crotch_access=True,
    short_desc="A one-piece bodysuit with snap crotch.",
)

# ----- OUTERWEAR -----

JACKET = ClothingItem(
    key="jacket",
    name="Jacket",
    slots=[ClothingSlot.CHEST, ClothingSlot.BACK, ClothingSlot.SHOULDERS, ClothingSlot.ARMS],
    layer=ClothingLayer.OUTER,
    material=ClothingMaterial.LEATHER,
    coverage=CoverageLevel.MODERATE,
    has_zipper=True,
    short_desc="A leather jacket.",
)

ROBE = ClothingItem(
    key="robe",
    name="Robe",
    slots=[ClothingSlot.FULL_BODY],
    layer=ClothingLayer.OUTER,
    material=ClothingMaterial.SILK,
    coverage=CoverageLevel.FULL,
    short_desc="A flowing silk robe.",
)


# =============================================================================
# CLOTHING REGISTRY
# =============================================================================

ALL_CLOTHING: Dict[str, ClothingItem] = {
    # Underwear
    "panties": PANTIES,
    "thong": THONG,
    "lace_panties": LACE_PANTIES,
    "crotchless_panties": CROTCHLESS_PANTIES,
    "bra": BRA,
    "lace_bra": LACE_BRA,
    "cupless_bra": CUPLESS_BRA,
    "briefs": BRIEFS,
    "boxers": BOXERS,
    "jockstrap": JOCKSTRAP,
    # Tops
    "tshirt": TSHIRT,
    "crop_top": CROP_TOP,
    "blouse": BLOUSE,
    "tank_top": TANK_TOP,
    "corset": CORSET,
    "latex_top": LATEX_TOP,
    # Bottoms
    "pants": PANTS,
    "jeans": JEANS,
    "shorts": SHORTS,
    "skirt": SKIRT,
    "mini_skirt": MINI_SKIRT,
    "latex_pants": LATEX_PANTS,
    "leather_pants": LEATHER_PANTS,
    "chaps": CHAPS,
    # Dresses
    "dress": DRESS,
    "cocktail_dress": COCKTAIL_DRESS,
    "latex_dress": LATEX_DRESS,
    # Full body
    "catsuit": CATSUIT,
    "bodysuit": BODYSUIT,
    # Outerwear
    "jacket": JACKET,
    "robe": ROBE,
}


def get_clothing(key: str) -> Optional[ClothingItem]:
    """Get clothing item by key."""
    item = ALL_CLOTHING.get(key)
    if item:
        # Return a copy so original isn't modified
        return ClothingItem.from_dict(item.to_dict())
    return None


def get_clothing_by_slot(slot: ClothingSlot) -> List[ClothingItem]:
    """Get all clothing that covers a slot."""
    return [c for c in ALL_CLOTHING.values() if slot in c.slots]


# =============================================================================
# WARDROBE SYSTEM
# =============================================================================

@dataclass
class Wardrobe:
    """Manages what a character is wearing."""
    worn_items: Dict[str, dict] = field(default_factory=dict)  # key -> item dict
    
    def get_worn_item(self, key: str) -> Optional[ClothingItem]:
        """Get a worn item by key."""
        data = self.worn_items.get(key)
        if data:
            return ClothingItem.from_dict(data)
        return None
    
    def get_all_worn(self) -> List[ClothingItem]:
        """Get all worn items."""
        return [ClothingItem.from_dict(d) for d in self.worn_items.values()]
    
    def get_items_in_slot(self, slot: ClothingSlot) -> List[ClothingItem]:
        """Get items covering a slot, sorted by layer."""
        items = []
        for data in self.worn_items.values():
            item = ClothingItem.from_dict(data)
            if item.is_covering(slot):
                items.append(item)
        
        return sorted(items, key=lambda i: i.layer.value, reverse=True)
    
    def is_slot_covered(self, slot: ClothingSlot) -> bool:
        """Check if a slot is covered by any clothing."""
        for item in self.get_all_worn():
            if item.is_covering(slot):
                return True
        return False
    
    def get_coverage_level(self, slot: ClothingSlot) -> CoverageLevel:
        """Get the coverage level for a slot (highest of all items)."""
        items = self.get_items_in_slot(slot)
        if not items:
            return CoverageLevel.NONE
        
        return max(items, key=lambda i: i.coverage.value).coverage
    
    def can_wear(self, item: ClothingItem) -> Tuple[bool, str]:
        """Check if an item can be worn."""
        # Check for conflicts at same layer and slot
        for slot in item.slots:
            existing = self.get_items_in_slot(slot)
            for existing_item in existing:
                if existing_item.layer == item.layer:
                    return False, f"Already wearing {existing_item.name} in that slot."
        
        return True, ""
    
    def wear(self, item: ClothingItem) -> str:
        """Wear an item."""
        can_wear, reason = self.can_wear(item)
        if not can_wear:
            return reason
        
        item.state = ClothingState.WORN
        self.worn_items[item.key] = item.to_dict()
        return f"You put on the {item.name}."
    
    def remove(self, key: str, force: bool = False) -> Tuple[Optional[ClothingItem], str]:
        """Remove an item."""
        item = self.get_worn_item(key)
        if not item:
            return None, f"Not wearing {key}."
        
        if item.is_locked and not force:
            return None, f"The {item.name} is locked on!"
        
        item.state = ClothingState.REMOVED
        del self.worn_items[key]
        return item, f"You remove the {item.name}."
    
    def strip_all(self, force: bool = False) -> List[str]:
        """Remove all clothing."""
        messages = []
        keys = list(self.worn_items.keys())
        
        for key in keys:
            item, msg = self.remove(key, force)
            messages.append(msg)
        
        return messages
    
    def get_description(self) -> str:
        """Get description of worn clothing."""
        items = self.get_all_worn()
        
        if not items:
            return "completely naked"
        
        # Group by general area
        top_items = [i for i in items if ClothingSlot.CHEST in i.slots]
        bottom_items = [i for i in items if ClothingSlot.GROIN in i.slots or ClothingSlot.LEGS in i.slots]
        
        parts = []
        
        if top_items:
            names = [i.name.lower() for i in top_items]
            parts.append(f"wearing {', '.join(names)} on top")
        
        if bottom_items:
            names = [i.name.lower() for i in bottom_items]
            if parts:
                parts.append(f"and {', '.join(names)} below")
            else:
                parts.append(f"wearing {', '.join(names)}")
        
        return " ".join(parts) if parts else "barely dressed"
    
    def get_exposed_slots(self) -> Set[ClothingSlot]:
        """Get slots that are not covered."""
        important_slots = {
            ClothingSlot.CHEST,
            ClothingSlot.GROIN,
            ClothingSlot.REAR,
        }
        
        exposed = set()
        for slot in important_slots:
            if not self.is_slot_covered(slot):
                exposed.add(slot)
        
        return exposed
    
    def to_dict(self) -> dict:
        return {"worn_items": self.worn_items}
    
    @classmethod
    def from_dict(cls, data: dict) -> "Wardrobe":
        wardrobe = cls()
        wardrobe.worn_items = data.get("worn_items", {})
        return wardrobe


# =============================================================================
# CLOTHING MIXIN
# =============================================================================

class ClothingMixin:
    """
    Mixin for characters that can wear clothing.
    """
    
    @property
    def wardrobe(self) -> Wardrobe:
        """Get character's wardrobe."""
        data = self.attributes.get("wardrobe", {})
        return Wardrobe.from_dict(data)
    
    @wardrobe.setter
    def wardrobe(self, value: Wardrobe):
        """Set character's wardrobe."""
        self.attributes.add("wardrobe", value.to_dict())
    
    def save_wardrobe(self):
        """Save wardrobe changes."""
        self.wardrobe = self.wardrobe
    
    def wear_clothing(self, item: ClothingItem) -> str:
        """Wear a clothing item."""
        wardrobe = self.wardrobe
        result = wardrobe.wear(item)
        self.wardrobe = wardrobe
        return result
    
    def remove_clothing(self, key: str, force: bool = False) -> str:
        """Remove a clothing item."""
        wardrobe = self.wardrobe
        item, result = wardrobe.remove(key, force)
        self.wardrobe = wardrobe
        return result
    
    def lift_clothing(self, key: str) -> str:
        """Lift a clothing item."""
        wardrobe = self.wardrobe
        item = wardrobe.get_worn_item(key)
        if not item:
            return f"Not wearing {key}."
        
        result = item.lift()
        wardrobe.worn_items[key] = item.to_dict()
        self.wardrobe = wardrobe
        return result
    
    def lower_clothing(self, key: str) -> str:
        """Lower a clothing item."""
        wardrobe = self.wardrobe
        item = wardrobe.get_worn_item(key)
        if not item:
            return f"Not wearing {key}."
        
        result = item.lower()
        wardrobe.worn_items[key] = item.to_dict()
        self.wardrobe = wardrobe
        return result
    
    def is_naked(self) -> bool:
        """Check if wearing nothing."""
        return len(self.wardrobe.worn_items) == 0
    
    def is_slot_exposed(self, slot: ClothingSlot) -> bool:
        """Check if a body slot is exposed."""
        return not self.wardrobe.is_slot_covered(slot)
    
    def get_clothing_description(self) -> str:
        """Get description of what character is wearing."""
        return self.wardrobe.get_description()


# =============================================================================
# OUTFIT PRESETS
# =============================================================================

OUTFIT_PRESETS: Dict[str, List[str]] = {
    "casual": ["bra", "panties", "tshirt", "jeans"],
    "formal": ["bra", "panties", "blouse", "skirt"],
    "lingerie": ["lace_bra", "lace_panties"],
    "latex": ["latex_top", "latex_pants"],
    "leather": ["cupless_bra", "leather_pants"],
    "minimal": ["thong", "crop_top"],
    "full_latex": ["catsuit"],
    "nothing": [],
}


def get_outfit_preset(name: str) -> List[ClothingItem]:
    """Get clothing items for a preset outfit."""
    keys = OUTFIT_PRESETS.get(name, [])
    return [get_clothing(k) for k in keys if get_clothing(k)]


__all__ = [
    "ClothingSlot",
    "ClothingLayer",
    "ClothingState",
    "ClothingMaterial",
    "CoverageLevel",
    "ClothingItem",
    "ALL_CLOTHING",
    "get_clothing",
    "get_clothing_by_slot",
    "Wardrobe",
    "ClothingMixin",
    "OUTFIT_PRESETS",
    "get_outfit_preset",
]
