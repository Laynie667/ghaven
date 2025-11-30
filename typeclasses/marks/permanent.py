"""
Permanent Marks System
======================

Marks that don't fade over time:
- Brands (burned into skin)
- Tattoos (inked designs)
- Scars (healed wounds)
- Piercings (holes with jewelry)
- Birthmarks (natural)
"""

from dataclasses import dataclass, field
from typing import Optional, List
from enum import Enum
from datetime import datetime

from .base import Mark, MarkPersistence, SurfaceType


# =============================================================================
# ENUMS
# =============================================================================

class PermanentMarkType(Enum):
    """Types of permanent marks."""
    BRAND = "brand"
    TATTOO = "tattoo"
    SCAR = "scar"
    PIERCING = "piercing"
    BIRTHMARK = "birthmark"


class BrandType(Enum):
    """Types of brands."""
    OWNERSHIP = "ownership"  # Marks ownership
    SLAVE = "slave"
    GUILD = "guild"
    CRIMINAL = "criminal"
    DECORATIVE = "decorative"
    CUSTOM = "custom"


class TattooStyle(Enum):
    """Tattoo artistic styles."""
    TRIBAL = "tribal"
    TRADITIONAL = "traditional"
    REALISTIC = "realistic"
    GEOMETRIC = "geometric"
    MAGICAL = "magical"  # Glowing runes, etc.
    CRUDE = "crude"  # Prison-style
    ORNATE = "ornate"
    MINIMALIST = "minimalist"


class ScarType(Enum):
    """Types of scars."""
    SLASH = "slash"  # From blade
    PUNCTURE = "puncture"  # From piercing
    BURN = "burn"  # From fire/heat
    BITE = "bite"  # From teeth
    CLAW = "claw"  # From claws
    SURGICAL = "surgical"  # Clean, intentional
    DECORATIVE = "decorative"  # Scarification
    HEALED_BRAND = "healed_brand"  # Old brand
    STRETCH = "stretch"  # Stretch marks


class PiercingType(Enum):
    """Types of piercings."""
    STUD = "stud"
    RING = "ring"
    BARBELL = "barbell"
    HOOP = "hoop"
    CHAIN = "chain"
    PLUG = "plug"
    CAPTIVE = "captive_bead"


# =============================================================================
# PERMANENT MARK BASE
# =============================================================================

@dataclass
class PermanentMark(Mark):
    """Base class for permanent marks."""
    
    def __post_init__(self):
        super().__post_init__()
        self.persistence = MarkPersistence.PERMANENT
        self.fade_ticks = 0  # Never fades
    
    def tick(self) -> bool:
        """Permanent marks never fade."""
        return False


# =============================================================================
# BRAND
# =============================================================================

@dataclass
class BrandMark(PermanentMark):
    """
    A brand burned into the skin.
    """
    mark_type: str = "brand"
    
    # Brand specifics
    brand_type: BrandType = BrandType.CUSTOM
    design: str = ""  # What the brand depicts
    
    # Appearance
    raised: bool = True  # Keloid/raised scar
    
    # Meaning
    meaning: str = ""
    owner: str = ""  # If ownership brand, whose
    owner_name: str = ""
    
    # When applied
    is_fresh: bool = False  # Still healing
    
    def __post_init__(self):
        super().__post_init__()
        self.surface = SurfaceType.SKIN
        self.visible = True
    
    def get_display(self, verbose: bool = False) -> str:
        """Get display text for this brand."""
        fresh = "fresh " if self.is_fresh else ""
        raised = "raised " if self.raised else ""
        
        if self.design:
            base = f"a {fresh}{raised}brand of {self.design}"
        else:
            base = f"a {fresh}{raised}brand"
        
        if verbose:
            if self.owner_name:
                base = f"{base} (belongs to {self.owner_name})"
            elif self.meaning:
                base = f"{base} ({self.meaning})"
        
        return base
    
    def to_dict(self):
        data = super().to_dict()
        data.update({
            "brand_type": self.brand_type.value,
            "design": self.design,
            "raised": self.raised,
            "meaning": self.meaning,
            "owner": self.owner,
            "owner_name": self.owner_name,
            "is_fresh": self.is_fresh,
        })
        return data
    
    @classmethod
    def from_dict(cls, data):
        from datetime import datetime
        data = data.copy()
        if "brand_type" in data and isinstance(data["brand_type"], str):
            data["brand_type"] = BrandType(data["brand_type"])
        if "surface" in data and isinstance(data["surface"], str):
            data["surface"] = SurfaceType(data["surface"])
        if "persistence" in data and isinstance(data["persistence"], str):
            data["persistence"] = MarkPersistence(data["persistence"])
        if data.get("created_at") and isinstance(data["created_at"], str):
            data["created_at"] = datetime.fromisoformat(data["created_at"])
        data.pop("mark_class", None)
        valid = {k: v for k, v in data.items() if k in cls.__dataclass_fields__}
        return cls(**valid)


# =============================================================================
# TATTOO
# =============================================================================

@dataclass
class TattooMark(PermanentMark):
    """
    A tattoo on the skin.
    """
    mark_type: str = "tattoo"
    
    # Tattoo specifics
    design: str = ""  # What it depicts
    style: TattooStyle = TattooStyle.TRADITIONAL
    
    # Colors
    colors: List[str] = field(default_factory=lambda: ["black"])
    is_colored: bool = False
    
    # Quality
    quality: str = "decent"  # crude, rough, decent, good, excellent, masterwork
    
    # Artist
    artist: str = ""
    artist_name: str = ""
    
    # Meaning
    meaning: str = ""
    personal: bool = False  # Has personal meaning to wearer
    
    def __post_init__(self):
        super().__post_init__()
        self.surface = SurfaceType.SKIN
        self.is_colored = len(self.colors) > 1 or self.colors[0] != "black"
    
    def get_display(self, verbose: bool = False) -> str:
        """Get display text for this tattoo."""
        quality_word = ""
        if self.quality in ("crude", "rough"):
            quality_word = f"{self.quality} "
        elif self.quality in ("excellent", "masterwork"):
            quality_word = f"{self.quality} "
        
        color_word = ""
        if self.is_colored:
            if len(self.colors) == 1:
                color_word = f"{self.colors[0]} "
            else:
                color_word = "colorful "
        
        style_word = ""
        if self.style != TattooStyle.TRADITIONAL:
            style_word = f"{self.style.value} "
        
        if self.design:
            base = f"a {quality_word}{color_word}{style_word}tattoo of {self.design}"
        else:
            base = f"a {quality_word}{color_word}{style_word}tattoo"
        
        if verbose and self.meaning:
            base = f"{base} ({self.meaning})"
        
        return base
    
    def to_dict(self):
        data = super().to_dict()
        data.update({
            "design": self.design,
            "style": self.style.value,
            "colors": self.colors,
            "is_colored": self.is_colored,
            "quality": self.quality,
            "artist": self.artist,
            "artist_name": self.artist_name,
            "meaning": self.meaning,
            "personal": self.personal,
        })
        return data
    
    @classmethod
    def from_dict(cls, data):
        from datetime import datetime
        data = data.copy()
        # Handle enums
        if "style" in data and isinstance(data["style"], str):
            data["style"] = TattooStyle(data["style"])
        if "surface" in data and isinstance(data["surface"], str):
            data["surface"] = SurfaceType(data["surface"])
        if "persistence" in data and isinstance(data["persistence"], str):
            data["persistence"] = MarkPersistence(data["persistence"])
        if data.get("created_at") and isinstance(data["created_at"], str):
            data["created_at"] = datetime.fromisoformat(data["created_at"])
        data.pop("mark_class", None)
        valid = {k: v for k, v in data.items() if k in cls.__dataclass_fields__}
        return cls(**valid)


# =============================================================================
# SCAR
# =============================================================================

@dataclass
class ScarMark(PermanentMark):
    """
    A scar from healed wound.
    """
    mark_type: str = "scar"
    
    # Scar specifics
    scar_type: ScarType = ScarType.SLASH
    
    # Appearance
    raised: bool = False  # Keloid
    indented: bool = False
    smooth: bool = True
    
    # Age
    old: bool = False  # Old faded scar
    
    # Origin
    origin_story: str = ""  # How it was gotten
    intentional: bool = False  # Decorative scarification
    
    def __post_init__(self):
        super().__post_init__()
        self.surface = SurfaceType.SKIN
        
        # Set color based on age
        if not self.color:
            self.color = "pale" if self.old else "pink"
    
    def get_display(self, verbose: bool = False) -> str:
        """Get display text for this scar."""
        age_word = "old " if self.old else ""
        
        texture_word = ""
        if self.raised:
            texture_word = "raised "
        elif self.indented:
            texture_word = "indented "
        
        scar_desc = self.scar_type.value.replace("_", " ")
        
        base = f"a {age_word}{texture_word}{scar_desc} scar"
        
        if verbose and self.origin_story:
            base = f"{base} ({self.origin_story})"
        
        return base
    
    def to_dict(self):
        data = super().to_dict()
        data.update({
            "scar_type": self.scar_type.value,
            "raised": self.raised,
            "indented": self.indented,
            "smooth": self.smooth,
            "old": self.old,
            "origin_story": self.origin_story,
            "intentional": self.intentional,
        })
        return data
    
    @classmethod
    def from_dict(cls, data):
        from datetime import datetime
        data = data.copy()
        if "scar_type" in data and isinstance(data["scar_type"], str):
            data["scar_type"] = ScarType(data["scar_type"])
        if "surface" in data and isinstance(data["surface"], str):
            data["surface"] = SurfaceType(data["surface"])
        if "persistence" in data and isinstance(data["persistence"], str):
            data["persistence"] = MarkPersistence(data["persistence"])
        if data.get("created_at") and isinstance(data["created_at"], str):
            data["created_at"] = datetime.fromisoformat(data["created_at"])
        data.pop("mark_class", None)
        valid = {k: v for k, v in data.items() if k in cls.__dataclass_fields__}
        return cls(**valid)


# =============================================================================
# PIERCING
# =============================================================================

@dataclass
class PiercingMark(PermanentMark):
    """
    A body piercing with jewelry.
    """
    mark_type: str = "piercing"
    
    # Piercing specifics
    piercing_type: PiercingType = PiercingType.RING
    
    # Jewelry
    jewelry_material: str = "silver"  # gold, silver, steel, titanium, bone
    jewelry_description: str = ""  # "a small silver ring", etc.
    has_jewelry: bool = True  # False if hole is empty
    
    # State
    is_fresh: bool = False  # Still healing
    stretched: bool = False  # Gauge stretched
    gauge: str = ""  # Size if stretched
    
    def __post_init__(self):
        super().__post_init__()
        self.surface = SurfaceType.SKIN
    
    def get_display(self, verbose: bool = False) -> str:
        """Get display text for this piercing."""
        if not self.has_jewelry:
            return "an empty piercing hole"
        
        fresh = "fresh " if self.is_fresh else ""
        
        if self.jewelry_description:
            return f"{fresh}{self.jewelry_description}"
        
        material = self.jewelry_material
        ptype = self.piercing_type.value.replace("_", " ")
        
        return f"a {fresh}{material} {ptype}"
    
    def to_dict(self):
        data = super().to_dict()
        data.update({
            "piercing_type": self.piercing_type.value,
            "jewelry_material": self.jewelry_material,
            "jewelry_description": self.jewelry_description,
            "has_jewelry": self.has_jewelry,
            "is_fresh": self.is_fresh,
            "stretched": self.stretched,
            "gauge": self.gauge,
        })
        return data
    
    @classmethod
    def from_dict(cls, data):
        from datetime import datetime
        data = data.copy()
        if "piercing_type" in data and isinstance(data["piercing_type"], str):
            data["piercing_type"] = PiercingType(data["piercing_type"])
        if "surface" in data and isinstance(data["surface"], str):
            data["surface"] = SurfaceType(data["surface"])
        if "persistence" in data and isinstance(data["persistence"], str):
            data["persistence"] = MarkPersistence(data["persistence"])
        if data.get("created_at") and isinstance(data["created_at"], str):
            data["created_at"] = datetime.fromisoformat(data["created_at"])
        data.pop("mark_class", None)
        valid = {k: v for k, v in data.items() if k in cls.__dataclass_fields__}
        return cls(**valid)


# =============================================================================
# BIRTHMARK
# =============================================================================

@dataclass
class BirthmarkMark(PermanentMark):
    """
    A natural birthmark.
    """
    mark_type: str = "birthmark"
    
    # Appearance
    shape: str = ""  # "irregular", "heart-shaped", "crescent"
    
    def __post_init__(self):
        super().__post_init__()
        self.surface = SurfaceType.SKIN
        if not self.color:
            self.color = "brown"
    
    def get_display(self, verbose: bool = False) -> str:
        """Get display text for this birthmark."""
        shape_word = f"{self.shape} " if self.shape else ""
        color_word = f"{self.color} " if self.color else ""
        
        return f"a {self.size} {shape_word}{color_word}birthmark"
    
    def to_dict(self):
        data = super().to_dict()
        data.update({
            "shape": self.shape,
        })
        return data


# =============================================================================
# HELPER FUNCTIONS
# =============================================================================

def create_ownership_brand(design: str,
                          location: str,
                          owner: str,
                          owner_name: str,
                          created_by: str = "") -> BrandMark:
    """Create an ownership brand."""
    return BrandMark(
        design=design,
        location=location,
        brand_type=BrandType.OWNERSHIP,
        owner=owner,
        owner_name=owner_name,
        meaning=f"Property of {owner_name}",
        created_by=created_by,
    )


def create_slave_brand(location: str = "inner_thigh",
                      owner: str = "",
                      owner_name: str = "",
                      created_by: str = "") -> BrandMark:
    """Create a slave brand."""
    return BrandMark(
        design="a slave mark",
        location=location,
        brand_type=BrandType.SLAVE,
        owner=owner,
        owner_name=owner_name,
        meaning="slave",
        created_by=created_by,
    )


def damage_to_scar(damage_mark) -> ScarMark:
    """Convert a healed damage mark to a scar."""
    from .damage import DamageType
    
    # Map damage types to scar types
    scar_mapping = {
        DamageType.CUT: ScarType.SLASH,
        DamageType.SCRATCH: ScarType.SLASH,
        DamageType.BITE: ScarType.BITE,
        DamageType.WHIP_MARK: ScarType.SLASH,
        DamageType.FRICTION_BURN: ScarType.BURN,
    }
    
    scar_type = scar_mapping.get(damage_mark.damage_type, ScarType.SLASH)
    
    return ScarMark(
        location=damage_mark.location,
        position=damage_mark.position,
        size=damage_mark.size,
        scar_type=scar_type,
        origin_story=f"from {damage_mark.cause}" if damage_mark.cause else "",
        created_by=damage_mark.caused_by,
    )


def describe_permanent_marks(marks: List[PermanentMark], location: str) -> str:
    """Get natural description of permanent marks on a location."""
    if not marks:
        return ""
    
    descriptions = [m.get_display() for m in marks]
    
    if len(descriptions) == 1:
        return descriptions[0]
    elif len(descriptions) == 2:
        return f"{descriptions[0]} and {descriptions[1]}"
    else:
        return ", ".join(descriptions[:-1]) + f", and {descriptions[-1]}"
