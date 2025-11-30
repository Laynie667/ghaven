"""
Marks System - Base Classes
===========================

Universal marking system that can be applied to any object:
- Rooms (walls, floor, ceiling)
- Objects (furniture, books, surfaces)
- Bodies (skin, parts)
- Body parts (specific locations)

The MarkableMixin provides all marking functionality to any typeclass.
"""

from dataclasses import dataclass, field
from typing import List, Dict, Optional, Set, Any, Union
from enum import Enum, auto
from datetime import datetime


# =============================================================================
# SURFACE TYPES - What can be marked
# =============================================================================

class SurfaceType(Enum):
    """Types of surfaces that can hold marks."""
    # Room surfaces
    WALL = "wall"
    FLOOR = "floor"
    CEILING = "ceiling"
    DOOR = "door"
    WINDOW = "window"
    
    # Furniture surfaces
    TABLE_TOP = "table_top"
    SEAT = "seat"
    BACK = "back"
    HEADBOARD = "headboard"
    FOOTBOARD = "footboard"
    MATTRESS = "mattress"
    CUSHION = "cushion"
    ARMREST = "armrest"
    
    # Object surfaces
    COVER = "cover"  # Book cover, lid
    PAGE = "page"
    SURFACE = "surface"  # Generic flat surface
    INSIDE = "inside"
    OUTSIDE = "outside"
    
    # Body surfaces
    SKIN = "skin"
    HAIR = "hair"
    SCALES = "scales"
    FUR = "fur"
    FEATHERS = "feathers"
    
    # Internal (for fluids)
    INTERNAL = "internal"
    CAVITY = "cavity"


class SurfaceMaterial(Enum):
    """Material affects what marks can be applied."""
    STONE = "stone"
    WOOD = "wood"
    METAL = "metal"
    FABRIC = "fabric"
    LEATHER = "leather"
    PAPER = "paper"
    GLASS = "glass"
    SKIN = "skin"
    FUR = "fur"
    SCALES = "scales"
    FLESH = "flesh"  # Internal


# =============================================================================
# MARK PERSISTENCE
# =============================================================================

class MarkPersistence(Enum):
    """How long a mark lasts."""
    TEMPORARY = "temporary"      # Fades over time, can be cleaned
    SEMI_PERMANENT = "semi"      # Fades slowly, hard to remove
    PERMANENT = "permanent"      # Never fades, requires special removal


# =============================================================================
# BASE MARK CLASS
# =============================================================================

@dataclass
class Mark:
    """
    Base class for all marks.
    
    A mark is anything applied to a surface - writing, fluids, 
    damage, tattoos, etc.
    """
    # Identity
    mark_id: str = ""  # Unique identifier
    mark_type: str = "generic"  # Subclass should override
    
    # Location
    surface: SurfaceType = SurfaceType.SURFACE
    location: str = ""  # Specific location descriptor ("left wall", "page 12", "left_arm")
    position: str = ""  # Position on location ("upper", "center", "near the door")
    
    # Appearance
    description: str = ""
    size: str = "small"  # tiny, small, medium, large, huge, massive
    color: str = ""
    
    # Visibility
    visible: bool = True
    visible_distance: str = "near"  # touch, near, far, any
    
    # Persistence
    persistence: MarkPersistence = MarkPersistence.TEMPORARY
    created_at: Optional[datetime] = None
    fade_ticks: int = 0  # Ticks until fades (0 = based on persistence)
    current_fade: int = 0  # Current fade progress
    
    # Origin
    created_by: str = ""  # Character dbref or "unknown"
    source: str = ""  # What made this mark
    
    def __post_init__(self):
        if not self.mark_id:
            self.mark_id = f"{self.mark_type}_{id(self)}"
        if not self.created_at:
            self.created_at = datetime.now()
    
    def get_display(self, verbose: bool = False) -> str:
        """Get human-readable description of this mark."""
        parts = []
        
        if self.size and self.size != "medium":
            parts.append(self.size)
        
        if self.color:
            parts.append(self.color)
        
        parts.append(self.description or self.mark_type)
        
        base = " ".join(parts)
        
        if verbose and self.position:
            base = f"{base} ({self.position})"
        
        return base
    
    def tick(self) -> bool:
        """
        Process one tick of time.
        Returns True if mark should be removed (fully faded).
        """
        if self.persistence == MarkPersistence.PERMANENT:
            return False
        
        if self.fade_ticks > 0:
            self.current_fade += 1
            if self.current_fade >= self.fade_ticks:
                return True
        
        return False
    
    def get_fade_percent(self) -> float:
        """Get fade progress as 0.0-1.0."""
        if self.fade_ticks <= 0:
            return 0.0
        return min(1.0, self.current_fade / self.fade_ticks)
    
    def is_fading(self) -> bool:
        """Check if mark is partially faded."""
        return self.get_fade_percent() > 0.3
    
    def to_dict(self) -> Dict:
        """Serialize to dict for storage."""
        return {
            "mark_id": self.mark_id,
            "mark_type": self.mark_type,
            "mark_class": self.__class__.__name__,  # Track the actual class
            "surface": self.surface.value,
            "location": self.location,
            "position": self.position,
            "description": self.description,
            "size": self.size,
            "color": self.color,
            "visible": self.visible,
            "visible_distance": self.visible_distance,
            "persistence": self.persistence.value,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "fade_ticks": self.fade_ticks,
            "current_fade": self.current_fade,
            "created_by": self.created_by,
            "source": self.source,
        }
    
    @classmethod
    def from_dict(cls, data: Dict) -> "Mark":
        """Deserialize from dict."""
        data = data.copy()
        
        # Get correct class if this is being called on base Mark
        if cls == Mark and "mark_class" in data:
            # Look up the right class from registry
            mark_class = _MARK_CLASS_REGISTRY.get(data["mark_class"], Mark)
            if mark_class != Mark:
                return mark_class.from_dict(data)
        
        # Filter to only valid fields for this class
        valid_fields = set(cls.__dataclass_fields__.keys()) if hasattr(cls, "__dataclass_fields__") else set()
        
        # Handle enum conversions
        if "surface" in data:
            data["surface"] = SurfaceType(data.get("surface", "surface"))
        if "persistence" in data:
            data["persistence"] = MarkPersistence(data.get("persistence", "temporary"))
        if data.get("created_at") and isinstance(data["created_at"], str):
            data["created_at"] = datetime.fromisoformat(data["created_at"])
        
        # Remove mark_class from data
        data.pop("mark_class", None)
        
        # Filter to valid fields
        if valid_fields:
            filtered = {k: v for k, v in data.items() if k in valid_fields}
        else:
            filtered = data
        
        return cls(**filtered)


# Registry for deserializing to correct subclass
_MARK_CLASS_REGISTRY: Dict[str, type] = {
    "Mark": Mark,
}


def register_mark_class(cls: type):
    """Register a mark class for deserialization."""
    _MARK_CLASS_REGISTRY[cls.__name__] = cls
    return cls


# =============================================================================
# SURFACE DEFINITION
# =============================================================================

@dataclass
class Surface:
    """
    Defines a markable surface on an object.
    
    Objects can have multiple surfaces (a room has walls, floor, ceiling).
    """
    key: str  # Unique key for this surface
    surface_type: SurfaceType
    material: SurfaceMaterial
    
    # Display
    name: str = ""  # Display name ("north wall", "seat cushion")
    description: str = ""
    
    # Properties
    size: str = "medium"  # tiny, small, medium, large, huge, massive
    can_write: bool = True  # Can text be written here?
    can_draw: bool = True  # Can images be drawn?
    can_stain: bool = True  # Do fluids leave marks?
    can_brand: bool = False  # Can be permanently branded?
    can_tattoo: bool = False  # Can be tattooed (skin only)
    can_scar: bool = False  # Can be scarred (flesh only)
    
    # Cleaning
    absorbs_fluid: bool = False  # Does fluid soak in?
    easy_clean: bool = True  # Can be wiped clean easily?
    
    def __post_init__(self):
        if not self.name:
            self.name = self.key.replace("_", " ")
        
        # Auto-set properties based on material
        if self.material == SurfaceMaterial.SKIN:
            self.can_brand = True
            self.can_tattoo = True
            self.can_scar = True
            self.absorbs_fluid = True
            self.easy_clean = True
        elif self.material == SurfaceMaterial.FABRIC:
            self.absorbs_fluid = True
            self.easy_clean = False
        elif self.material in (SurfaceMaterial.STONE, SurfaceMaterial.METAL):
            self.absorbs_fluid = False
            self.easy_clean = True
        elif self.material == SurfaceMaterial.PAPER:
            self.absorbs_fluid = True
            self.can_brand = False
            self.easy_clean = False


# =============================================================================
# MARKABLE MIXIN
# =============================================================================

class MarkableMixin:
    """
    Mixin that provides marking functionality to any typeclass.
    
    Add to rooms, objects, characters, or body parts to allow
    them to have marks, fluids, writing, damage, etc.
    
    Usage:
        class MyRoom(MarkableMixin, DefaultRoom):
            pass
        
        room.add_mark(WritingMark(text="Kilroy was here", surface="wall"))
        room.add_fluid(FluidMark(fluid_type="cum", location="floor", amount=50))
    """
    
    # =========================================================================
    # INITIALIZATION
    # =========================================================================
    
    def init_markable(self, surfaces: Optional[List[Surface]] = None):
        """
        Initialize marking system.
        
        Call this in at_object_creation() or similar.
        """
        if not hasattr(self, "db"):
            # Not an Evennia object, use regular attributes
            self._marks_data = {
                "marks": [],
                "surfaces": {},
            }
        else:
            if not self.db.marks_data:
                self.db.marks_data = {
                    "marks": [],
                    "surfaces": {},
                }
        
        if surfaces:
            for surface in surfaces:
                self._register_surface(surface)
    
    def _get_marks_data(self) -> Dict:
        """Get marks data storage."""
        if hasattr(self, "db") and hasattr(self.db, "marks_data"):
            if not self.db.marks_data:
                self.db.marks_data = {"marks": [], "surfaces": {}}
            return self.db.marks_data
        if not hasattr(self, "_marks_data"):
            self._marks_data = {"marks": [], "surfaces": {}}
        return self._marks_data
    
    def _save_marks_data(self, data: Dict):
        """Save marks data."""
        if hasattr(self, "db"):
            self.db.marks_data = data
        else:
            self._marks_data = data
    
    # =========================================================================
    # SURFACE MANAGEMENT
    # =========================================================================
    
    def _register_surface(self, surface: Surface):
        """Register a surface that can be marked."""
        data = self._get_marks_data()
        if "surfaces" not in data:
            data["surfaces"] = {}
        data["surfaces"][surface.key] = {
            "type": surface.surface_type.value,
            "material": surface.material.value,
            "name": surface.name,
            "can_write": surface.can_write,
            "can_draw": surface.can_draw,
            "can_stain": surface.can_stain,
            "can_brand": surface.can_brand,
            "can_tattoo": surface.can_tattoo,
            "can_scar": surface.can_scar,
            "absorbs_fluid": surface.absorbs_fluid,
            "easy_clean": surface.easy_clean,
        }
        self._save_marks_data(data)
    
    def get_surface(self, key: str) -> Optional[Dict]:
        """Get surface definition by key."""
        data = self._get_marks_data()
        return data.get("surfaces", {}).get(key)
    
    def get_surfaces(self) -> Dict[str, Dict]:
        """Get all registered surfaces."""
        return self._get_marks_data().get("surfaces", {})
    
    def has_surface(self, key: str) -> bool:
        """Check if a surface exists."""
        return key in self._get_marks_data().get("surfaces", {})
    
    # =========================================================================
    # MARK MANAGEMENT
    # =========================================================================
    
    def add_mark(self, mark: Mark) -> bool:
        """
        Add a mark to this object.
        
        Returns True if added successfully.
        """
        data = self._get_marks_data()
        if "marks" not in data:
            data["marks"] = []
        
        data["marks"].append(mark.to_dict())
        self._save_marks_data(data)
        return True
    
    def remove_mark(self, mark_id: str) -> bool:
        """Remove a mark by ID."""
        data = self._get_marks_data()
        marks = data.get("marks", [])
        
        for i, m in enumerate(marks):
            if m.get("mark_id") == mark_id:
                marks.pop(i)
                self._save_marks_data(data)
                return True
        return False
    
    def get_mark(self, mark_id: str) -> Optional[Mark]:
        """Get a specific mark by ID."""
        data = self._get_marks_data()
        for m in data.get("marks", []):
            if m.get("mark_id") == mark_id:
                return Mark.from_dict(m)
        return None
    
    def get_marks(self, 
                  location: Optional[str] = None,
                  surface: Optional[SurfaceType] = None,
                  mark_type: Optional[str] = None,
                  visible_only: bool = False) -> List[Mark]:
        """
        Get marks matching criteria.
        
        Args:
            location: Filter by location string
            surface: Filter by surface type
            mark_type: Filter by mark type
            visible_only: Only return visible marks
        """
        data = self._get_marks_data()
        results = []
        
        for m_data in data.get("marks", []):
            mark = Mark.from_dict(m_data)
            
            if location and mark.location != location:
                continue
            if surface and mark.surface != surface:
                continue
            if mark_type and mark.mark_type != mark_type:
                continue
            if visible_only and not mark.visible:
                continue
            
            results.append(mark)
        
        return results
    
    def get_marks_on_surface(self, surface_key: str) -> List[Mark]:
        """Get all marks on a specific surface."""
        return self.get_marks(location=surface_key)
    
    def has_marks(self, location: Optional[str] = None) -> bool:
        """Check if there are any marks (optionally at location)."""
        return len(self.get_marks(location=location)) > 0
    
    def count_marks(self, mark_type: Optional[str] = None) -> int:
        """Count marks of a type."""
        return len(self.get_marks(mark_type=mark_type))
    
    # =========================================================================
    # MARK UPDATES
    # =========================================================================
    
    def update_mark(self, mark_id: str, **updates) -> bool:
        """Update a mark's properties."""
        data = self._get_marks_data()
        
        for m in data.get("marks", []):
            if m.get("mark_id") == mark_id:
                m.update(updates)
                self._save_marks_data(data)
                return True
        return False
    
    def tick_marks(self) -> List[str]:
        """
        Process time passing for all marks.
        
        Returns list of mark IDs that were removed (faded).
        """
        data = self._get_marks_data()
        removed = []
        remaining = []
        
        for m_data in data.get("marks", []):
            mark = Mark.from_dict(m_data)
            if mark.tick():
                removed.append(mark.mark_id)
            else:
                remaining.append(mark.to_dict())
        
        data["marks"] = remaining
        self._save_marks_data(data)
        return removed
    
    # =========================================================================
    # CLEANING
    # =========================================================================
    
    def clean_surface(self, 
                      surface_key: str, 
                      thorough: bool = False) -> List[str]:
        """
        Clean a surface, removing temporary marks.
        
        Args:
            surface_key: Which surface to clean
            thorough: If True, removes semi-permanent marks too
        
        Returns list of removed mark IDs.
        """
        data = self._get_marks_data()
        removed = []
        remaining = []
        
        for m_data in data.get("marks", []):
            mark = Mark.from_dict(m_data)
            
            if mark.location != surface_key:
                remaining.append(m_data)
                continue
            
            # Check if cleanable
            if mark.persistence == MarkPersistence.PERMANENT:
                remaining.append(m_data)
            elif mark.persistence == MarkPersistence.SEMI_PERMANENT and not thorough:
                remaining.append(m_data)
            else:
                removed.append(mark.mark_id)
        
        data["marks"] = remaining
        self._save_marks_data(data)
        return removed
    
    def clean_all(self, thorough: bool = False) -> List[str]:
        """Clean all surfaces."""
        removed = []
        for surface_key in self.get_surfaces():
            removed.extend(self.clean_surface(surface_key, thorough))
        return removed
    
    # =========================================================================
    # DISPLAY
    # =========================================================================
    
    def describe_marks(self, 
                       location: Optional[str] = None,
                       verbose: bool = False) -> str:
        """Get description of marks on this object."""
        marks = self.get_marks(location=location, visible_only=True)
        
        if not marks:
            return ""
        
        descriptions = []
        for mark in marks:
            desc = mark.get_display(verbose=verbose)
            if mark.is_fading():
                desc = f"a fading {desc}"
            descriptions.append(desc)
        
        if len(descriptions) == 1:
            return descriptions[0]
        elif len(descriptions) == 2:
            return f"{descriptions[0]} and {descriptions[1]}"
        else:
            return ", ".join(descriptions[:-1]) + f", and {descriptions[-1]}"
    
    # =========================================================================
    # SERIALIZATION
    # =========================================================================
    
    def export_marks(self) -> Dict:
        """Export all marks data for saving."""
        return self._get_marks_data()
    
    def import_marks(self, data: Dict):
        """Import marks data."""
        self._save_marks_data(data)
