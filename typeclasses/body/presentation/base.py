"""
Body Presentation - Surface State

Presentation is the final layer applied to a character's body.
It tracks temporary and permanent surface details:
    - Marks: Tattoos, scars, brands, piercings, birthmarks
    - Fluids: Sweat, cum, slick, saliva, blood, etc.
    - State: Wet, dirty, aroused, flushed, etc.

This layer is ONLY applied at the character level, not to templates.
It changes during gameplay.
"""

from dataclasses import dataclass, field
from typing import List, Dict, Optional
from enum import Enum


# =============================================================================
# MARKS - Permanent or semi-permanent markings
# =============================================================================

class MarkType(Enum):
    """Types of body marks."""
    TATTOO = "tattoo"
    SCAR = "scar"
    BRAND = "brand"
    PIERCING = "piercing"
    BIRTHMARK = "birthmark"
    PAINT = "paint"  # Temporary body paint
    WRITING = "writing"  # Written words
    BRUISE = "bruise"  # Temporary
    BITE_MARK = "bite_mark"  # Temporary
    SCRATCH = "scratch"  # Temporary
    HICKEY = "hickey"  # Temporary
    COLLAR_MARK = "collar_mark"  # From wearing collar
    ROPE_MARK = "rope_mark"  # From bondage


@dataclass
class Mark:
    """
    A mark on a body part.
    """
    mark_type: MarkType
    location: str  # Body part key
    description: str
    
    # Position on the part
    position: str = ""  # "left side", "center", "lower", etc.
    
    # Size
    size: str = "small"  # tiny, small, medium, large, huge
    
    # Visibility
    visible_when_clothed: bool = False
    
    # For temporary marks
    is_temporary: bool = False
    fade_time: int = 0  # Game ticks until fades (0 = permanent)
    
    # Origin
    origin: str = ""  # How it was acquired
    given_by: str = ""  # Who gave it (dbref)
    
    def get_display(self) -> str:
        """Get display text for this mark."""
        return f"A {self.size} {self.mark_type.value} on the {self.location}: {self.description}"


# =============================================================================
# FLUIDS - Body fluids and substances
# =============================================================================

class FluidType(Enum):
    """Types of body fluids."""
    # Natural
    SWEAT = "sweat"
    TEARS = "tears"
    SALIVA = "saliva"
    BLOOD = "blood"
    
    # Sexual
    CUM = "cum"
    PRECUM = "precum"
    SLICK = "slick"  # Vaginal wetness
    FEMCUM = "femcum"
    
    # Other
    MILK = "milk"
    URINE = "urine"
    
    # External
    WATER = "water"
    MUD = "mud"
    OIL = "oil"
    WAX = "wax"
    LUBE = "lube"


@dataclass
class FluidPresence:
    """
    Fluid present on a body part.
    """
    fluid_type: FluidType
    location: str  # Body part key
    amount: str = "trace"  # trace, light, moderate, heavy, dripping, covered
    
    # Source
    source: str = ""  # "self", dbref of other character, "unknown"
    
    # Age
    is_fresh: bool = True
    drying_time: int = 0  # Ticks until dry/faded
    
    def get_display(self) -> str:
        """Get display text for this fluid."""
        fresh = "fresh " if self.is_fresh else ""
        return f"{self.amount.title()} {fresh}{self.fluid_type.value} on the {self.location}"


# =============================================================================
# BODY STATE - Current physical state
# =============================================================================

class BodyStateType(Enum):
    """Types of body state."""
    # Temperature
    COLD = "cold"
    COOL = "cool"
    WARM = "warm"
    HOT = "hot"
    FEVERISH = "feverish"
    
    # Moisture
    DRY = "dry"
    DAMP = "damp"
    WET = "wet"
    SOAKED = "soaked"
    
    # Cleanliness
    CLEAN = "clean"
    DUSTY = "dusty"
    DIRTY = "dirty"
    FILTHY = "filthy"
    
    # Arousal (sexual)
    CALM = "calm"
    INTERESTED = "interested"
    AROUSED = "aroused"
    VERY_AROUSED = "very_aroused"
    DESPERATE = "desperate"
    
    # Physical
    RELAXED = "relaxed"
    TENSE = "tense"
    EXHAUSTED = "exhausted"
    TREMBLING = "trembling"
    
    # Skin state
    FLUSHED = "flushed"
    PALE = "pale"
    GOOSEBUMPS = "goosebumps"


@dataclass
class BodyState:
    """
    Current state of a body or body part.
    """
    state_type: BodyStateType
    location: Optional[str] = None  # None = whole body, else specific part
    intensity: str = "light"  # light, moderate, strong
    
    def get_display(self) -> str:
        """Get display text for this state."""
        if self.location:
            return f"The {self.location} is {self.state_type.value}"
        return f"Body is {self.state_type.value}"


# =============================================================================
# PRESENTATION TRACKER
# =============================================================================

class BodyPresentation:
    """
    Tracks all presentation elements for a character's body.
    
    This is stored on the character and updated during gameplay.
    """
    
    def __init__(self):
        self.marks: List[Mark] = []
        self.fluids: List[FluidPresence] = []
        self.states: List[BodyState] = []
    
    # =========================================================================
    # MARKS
    # =========================================================================
    
    def add_mark(self, mark: Mark):
        """Add a mark to the body."""
        self.marks.append(mark)
    
    def remove_mark(self, mark: Mark):
        """Remove a mark."""
        if mark in self.marks:
            self.marks.remove(mark)
    
    def get_marks_on(self, location: str) -> List[Mark]:
        """Get all marks on a specific body part."""
        return [m for m in self.marks if m.location == location]
    
    def get_marks_by_type(self, mark_type: MarkType) -> List[Mark]:
        """Get all marks of a specific type."""
        return [m for m in self.marks if m.mark_type == mark_type]
    
    def get_visible_marks(self, include_clothed: bool = False) -> List[Mark]:
        """Get marks that are currently visible."""
        if include_clothed:
            return self.marks.copy()
        return [m for m in self.marks if m.visible_when_clothed]
    
    def has_mark_on(self, location: str) -> bool:
        """Check if a body part has any marks."""
        return any(m.location == location for m in self.marks)
    
    # =========================================================================
    # FLUIDS
    # =========================================================================
    
    def add_fluid(self, fluid: FluidPresence):
        """Add fluid to a body part."""
        # Check if same fluid type already on same location
        existing = None
        for f in self.fluids:
            if f.fluid_type == fluid.fluid_type and f.location == fluid.location:
                existing = f
                break
        
        if existing:
            # Increase amount
            amounts = ["trace", "light", "moderate", "heavy", "dripping", "covered"]
            curr_idx = amounts.index(existing.amount)
            new_idx = amounts.index(fluid.amount)
            existing.amount = amounts[min(len(amounts) - 1, curr_idx + new_idx + 1)]
            existing.is_fresh = True
        else:
            self.fluids.append(fluid)
    
    def remove_fluid(self, location: str, fluid_type: Optional[FluidType] = None):
        """Remove fluid from a body part."""
        if fluid_type:
            self.fluids = [f for f in self.fluids 
                         if not (f.location == location and f.fluid_type == fluid_type)]
        else:
            self.fluids = [f for f in self.fluids if f.location != location]
    
    def clear_all_fluids(self):
        """Remove all fluids (bathing/cleaning)."""
        self.fluids.clear()
    
    def get_fluids_on(self, location: str) -> List[FluidPresence]:
        """Get all fluids on a specific body part."""
        return [f for f in self.fluids if f.location == location]
    
    def get_fluids_by_type(self, fluid_type: FluidType) -> List[FluidPresence]:
        """Get all instances of a fluid type."""
        return [f for f in self.fluids if f.fluid_type == fluid_type]
    
    def has_fluid_on(self, location: str) -> bool:
        """Check if a body part has any fluids."""
        return any(f.location == location for f in self.fluids)
    
    def is_messy(self) -> bool:
        """Check if body has significant fluid coverage."""
        heavy_amounts = ["heavy", "dripping", "covered"]
        return any(f.amount in heavy_amounts for f in self.fluids)
    
    # =========================================================================
    # STATES
    # =========================================================================
    
    def set_state(self, state: BodyState):
        """Set a body state, replacing conflicting states."""
        # Remove conflicting states (same category on same location)
        category = self._get_state_category(state.state_type)
        self.states = [
            s for s in self.states
            if not (s.location == state.location and 
                   self._get_state_category(s.state_type) == category)
        ]
        self.states.append(state)
    
    def clear_state(self, state_type: BodyStateType, location: Optional[str] = None):
        """Clear a specific state."""
        self.states = [
            s for s in self.states
            if not (s.state_type == state_type and s.location == location)
        ]
    
    def get_states(self, location: Optional[str] = None) -> List[BodyState]:
        """Get all states, optionally filtered by location."""
        if location is None:
            return self.states.copy()
        return [s for s in self.states if s.location == location or s.location is None]
    
    def has_state(self, state_type: BodyStateType) -> bool:
        """Check if body has a specific state."""
        return any(s.state_type == state_type for s in self.states)
    
    def get_arousal_level(self) -> str:
        """Get current arousal state."""
        arousal_states = [
            BodyStateType.CALM,
            BodyStateType.INTERESTED,
            BodyStateType.AROUSED,
            BodyStateType.VERY_AROUSED,
            BodyStateType.DESPERATE,
        ]
        for state in self.states:
            if state.state_type in arousal_states:
                return state.state_type.value
        return "calm"
    
    def _get_state_category(self, state_type: BodyStateType) -> str:
        """Get the category of a state type."""
        categories = {
            "temperature": [BodyStateType.COLD, BodyStateType.COOL, BodyStateType.WARM,
                          BodyStateType.HOT, BodyStateType.FEVERISH],
            "moisture": [BodyStateType.DRY, BodyStateType.DAMP, BodyStateType.WET,
                        BodyStateType.SOAKED],
            "cleanliness": [BodyStateType.CLEAN, BodyStateType.DUSTY, BodyStateType.DIRTY,
                           BodyStateType.FILTHY],
            "arousal": [BodyStateType.CALM, BodyStateType.INTERESTED, BodyStateType.AROUSED,
                       BodyStateType.VERY_AROUSED, BodyStateType.DESPERATE],
            "physical": [BodyStateType.RELAXED, BodyStateType.TENSE, BodyStateType.EXHAUSTED,
                        BodyStateType.TREMBLING],
            "skin": [BodyStateType.FLUSHED, BodyStateType.PALE, BodyStateType.GOOSEBUMPS],
        }
        for cat, types in categories.items():
            if state_type in types:
                return cat
        return "other"
    
    # =========================================================================
    # TICK / DECAY
    # =========================================================================
    
    def tick(self):
        """
        Process time passing - fade temporary marks, dry fluids, etc.
        
        Call this periodically (e.g., every game tick).
        """
        # Fade temporary marks
        for mark in self.marks[:]:
            if mark.is_temporary and mark.fade_time > 0:
                mark.fade_time -= 1
                if mark.fade_time <= 0:
                    self.marks.remove(mark)
        
        # Dry fluids
        for fluid in self.fluids[:]:
            if fluid.drying_time > 0:
                fluid.drying_time -= 1
                fluid.is_fresh = False
                if fluid.drying_time <= 0:
                    # Reduce amount or remove
                    amounts = ["trace", "light", "moderate", "heavy", "dripping", "covered"]
                    curr_idx = amounts.index(fluid.amount)
                    if curr_idx > 0:
                        fluid.amount = amounts[curr_idx - 1]
                        fluid.drying_time = 10  # Reset timer for further drying
                    else:
                        self.fluids.remove(fluid)
    
    # =========================================================================
    # DESCRIPTION
    # =========================================================================
    
    def describe_part(self, location: str, include_sexual: bool = False) -> str:
        """Get description of presentation elements on a body part."""
        lines = []
        
        # Marks
        for mark in self.get_marks_on(location):
            lines.append(mark.get_display())
        
        # Fluids
        for fluid in self.get_fluids_on(location):
            if not include_sexual and fluid.fluid_type in [
                FluidType.CUM, FluidType.PRECUM, FluidType.SLICK, FluidType.FEMCUM
            ]:
                continue
            lines.append(fluid.get_display())
        
        # States specific to this part
        for state in self.get_states(location):
            if state.location == location:
                lines.append(state.get_display())
        
        return "\n".join(lines)
    
    def describe_overall(self, include_sexual: bool = False) -> str:
        """Get overall presentation description."""
        lines = []
        
        # Overall states
        for state in self.states:
            if state.location is None:
                lines.append(state.get_display())
        
        # Count marks
        if self.marks:
            tattoos = len(self.get_marks_by_type(MarkType.TATTOO))
            scars = len(self.get_marks_by_type(MarkType.SCAR))
            piercings = len(self.get_marks_by_type(MarkType.PIERCING))
            
            if tattoos:
                lines.append(f"Has {tattoos} tattoo{'s' if tattoos > 1 else ''}.")
            if scars:
                lines.append(f"Has {scars} scar{'s' if scars > 1 else ''}.")
            if piercings:
                lines.append(f"Has {piercings} piercing{'s' if piercings > 1 else ''}.")
        
        # Messiness
        if self.is_messy():
            lines.append("Body is messy with fluids.")
        
        return "\n".join(lines)
    
    # =========================================================================
    # SERIALIZATION
    # =========================================================================
    
    def to_dict(self) -> Dict:
        """Serialize to dict for storage."""
        return {
            "marks": [
                {
                    "mark_type": m.mark_type.value,
                    "location": m.location,
                    "description": m.description,
                    "position": m.position,
                    "size": m.size,
                    "visible_when_clothed": m.visible_when_clothed,
                    "is_temporary": m.is_temporary,
                    "fade_time": m.fade_time,
                    "origin": m.origin,
                    "given_by": m.given_by,
                }
                for m in self.marks
            ],
            "fluids": [
                {
                    "fluid_type": f.fluid_type.value,
                    "location": f.location,
                    "amount": f.amount,
                    "source": f.source,
                    "is_fresh": f.is_fresh,
                    "drying_time": f.drying_time,
                }
                for f in self.fluids
            ],
            "states": [
                {
                    "state_type": s.state_type.value,
                    "location": s.location,
                    "intensity": s.intensity,
                }
                for s in self.states
            ],
        }
    
    @classmethod
    def from_dict(cls, data: Dict) -> "BodyPresentation":
        """Deserialize from dict."""
        pres = cls()
        
        for m in data.get("marks", []):
            pres.marks.append(Mark(
                mark_type=MarkType(m["mark_type"]),
                location=m["location"],
                description=m["description"],
                position=m.get("position", ""),
                size=m.get("size", "small"),
                visible_when_clothed=m.get("visible_when_clothed", False),
                is_temporary=m.get("is_temporary", False),
                fade_time=m.get("fade_time", 0),
                origin=m.get("origin", ""),
                given_by=m.get("given_by", ""),
            ))
        
        for f in data.get("fluids", []):
            pres.fluids.append(FluidPresence(
                fluid_type=FluidType(f["fluid_type"]),
                location=f["location"],
                amount=f.get("amount", "trace"),
                source=f.get("source", ""),
                is_fresh=f.get("is_fresh", True),
                drying_time=f.get("drying_time", 0),
            ))
        
        for s in data.get("states", []):
            pres.states.append(BodyState(
                state_type=BodyStateType(s["state_type"]),
                location=s.get("location"),
                intensity=s.get("intensity", "light"),
            ))
        
        return pres
