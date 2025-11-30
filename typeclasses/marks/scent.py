"""
Scent Marks
===========

Integration between the containment scent system and the marks system.
Allows scent to be tracked as marks on bodies.
"""

from dataclasses import dataclass
from typing import Optional
from datetime import datetime

from .base import Mark, MarkPersistence, SurfaceType


class ScentType:
    """Common scent types."""
    MUSK = "musk"
    CUM = "cum"
    FEMININE = "feminine"
    SWEAT = "sweat"
    AROUSAL = "arousal"
    HEAT = "heat"
    CLAIMED = "claimed"


@dataclass
class ScentMarkMark(Mark):
    """
    A scent mark on a body/surface.
    """
    mark_type: str = "scent"
    
    # Scent details
    scent_type: str = "musk"
    
    # Source
    source_dbref: str = ""
    source_name: str = ""
    
    # Strength 0-1 (affects how noticeable it is)
    strength: float = 0.5
    
    def __post_init__(self):
        super().__post_init__()
        
        self.persistence = MarkPersistence.TEMPORARY
        self.visible = False  # Scent isn't visible, it's smelled
        
        # Stronger scents last longer
        self.fade_ticks = int(100 * self.strength)
    
    def tick(self) -> bool:
        """Process fading."""
        result = super().tick()
        
        # Also reduce strength as it fades
        self.strength = max(0, self.strength - 0.01)
        
        return result or self.strength <= 0
    
    def reinforce(self, amount: float = 0.2):
        """Strengthen the scent mark."""
        self.strength = min(1.0, self.strength + amount)
        self.fade_ticks = int(100 * self.strength)
        self.current_fade = 0  # Reset fade
    
    def get_display(self, verbose: bool = False) -> str:
        """Get description of this scent."""
        if self.strength > 0.8:
            intensity = "strongly"
        elif self.strength > 0.5:
            intensity = "noticeably"
        elif self.strength > 0.2:
            intensity = "faintly"
        else:
            intensity = "barely"
        
        if self.source_name:
            return f"{intensity} smells of {self.source_name}'s {self.scent_type}"
        else:
            return f"{intensity} smells of {self.scent_type}"
    
    def to_dict(self):
        data = super().to_dict()
        data.update({
            "scent_type": self.scent_type,
            "source_dbref": self.source_dbref,
            "source_name": self.source_name,
            "strength": self.strength,
        })
        return data
    
    @classmethod
    def from_dict(cls, data):
        data = data.copy()
        if "surface" in data and isinstance(data["surface"], str):
            data["surface"] = SurfaceType(data["surface"])
        if "persistence" in data and isinstance(data["persistence"], str):
            data["persistence"] = MarkPersistence(data["persistence"])
        if data.get("created_at") and isinstance(data["created_at"], str):
            data["created_at"] = datetime.fromisoformat(data["created_at"])
        data.pop("mark_class", None)
        valid = {k: v for k, v in data.items() if k in cls.__dataclass_fields__}
        return cls(**valid)


def apply_scent_mark(target, 
                     scent_type: str,
                     source_dbref: str,
                     source_name: str,
                     strength: float = 0.5,
                     location: str = "body") -> ScentMarkMark:
    """
    Apply a scent mark to a target (must have MarkableMixin).
    If a scent from same source exists, reinforces it.
    """
    # Check for existing scent from same source
    existing_marks = target.get_marks(mark_type="scent")
    for mark in existing_marks:
        if hasattr(mark, 'source_dbref') and mark.source_dbref == source_dbref:
            # Reinforce existing
            mark.reinforce(strength)
            # Update in storage
            target.update_mark(mark.mark_id, strength=mark.strength)
            return mark
    
    # Create new scent mark
    scent = ScentMarkMark(
        scent_type=scent_type,
        source_dbref=source_dbref,
        source_name=source_name,
        strength=strength,
        location=location,
    )
    target.add_mark(scent)
    return scent


def get_scent_description(target, detailed: bool = False) -> str:
    """
    Get overall scent description for a target.
    """
    scent_marks = [m for m in target.get_marks(mark_type="scent")]
    
    if not scent_marks:
        return ""
    
    # Sort by strength
    sorted_marks = sorted(scent_marks, key=lambda m: m.strength, reverse=True)
    
    # Top 3 scents
    descriptions = []
    for mark in sorted_marks[:3]:
        if hasattr(mark, 'get_display'):
            descriptions.append(mark.get_display())
    
    if not descriptions:
        return ""
    
    if len(descriptions) == 1:
        return descriptions[0]
    
    return "; ".join(descriptions)


def smells_like(target, source_dbref: str, threshold: float = 0.3) -> bool:
    """
    Check if target smells like a specific source.
    """
    scent_marks = target.get_marks(mark_type="scent")
    for mark in scent_marks:
        if (hasattr(mark, 'source_dbref') and 
            mark.source_dbref == source_dbref and 
            mark.strength >= threshold):
            return True
    return False


__all__ = [
    "ScentType",
    "ScentMarkMark",
    "apply_scent_mark",
    "get_scent_description",
    "smells_like",
]
