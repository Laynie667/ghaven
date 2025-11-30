"""
Writing and Drawing Marks
=========================

Marks created by writing or drawing on surfaces.
"""

from dataclasses import dataclass, field
from typing import Optional
from enum import Enum

from .base import Mark, MarkPersistence, SurfaceType


class WritingTool(Enum):
    """What was used to write/draw."""
    FINGER = "finger"  # Written with finger (in dust, fluid, etc.)
    CHARCOAL = "charcoal"
    CHALK = "chalk"
    INK = "ink"
    PAINT = "paint"
    BLOOD = "blood"
    CUM = "cum"
    LIPSTICK = "lipstick"
    MARKER = "marker"
    CARVED = "carved"  # Carved into surface
    BRANDED = "branded"  # Burned in
    SCRATCHED = "scratched"


class WritingStyle(Enum):
    """Style of writing."""
    NEAT = "neat"
    MESSY = "messy"
    HASTY = "hasty"
    ELEGANT = "elegant"
    CRUDE = "crude"
    BLOCKY = "blocky"
    CURSIVE = "cursive"
    SCRAWLED = "scrawled"


@dataclass
class WritingMark(Mark):
    """
    Text written on a surface.
    """
    mark_type: str = "writing"
    
    # Writing content
    text: str = ""
    
    # Style
    tool: WritingTool = WritingTool.INK
    style: WritingStyle = WritingStyle.NEAT
    
    # Optional signature
    signed: bool = False
    signature: str = ""
    
    def __post_init__(self):
        super().__post_init__()
        
        # Set persistence based on tool
        if self.tool in (WritingTool.FINGER, WritingTool.CHALK):
            self.persistence = MarkPersistence.TEMPORARY
            if not self.fade_ticks:
                self.fade_ticks = 100  # Fades relatively quickly
        elif self.tool in (WritingTool.CARVED, WritingTool.BRANDED):
            self.persistence = MarkPersistence.PERMANENT
        else:
            self.persistence = MarkPersistence.SEMI_PERMANENT
            if not self.fade_ticks:
                self.fade_ticks = 1000  # Takes a while to fade
        
        # Set color based on tool if not specified
        if not self.color:
            tool_colors = {
                WritingTool.CHARCOAL: "black",
                WritingTool.CHALK: "white",
                WritingTool.INK: "black",
                WritingTool.BLOOD: "dark red",
                WritingTool.CUM: "white",
                WritingTool.LIPSTICK: "red",
            }
            self.color = tool_colors.get(self.tool, "")
    
    def get_display(self, verbose: bool = False) -> str:
        """Get display text for this writing."""
        style_desc = ""
        if self.style in (WritingStyle.HASTY, WritingStyle.SCRAWLED, WritingStyle.CRUDE):
            style_desc = f"{self.style.value} "
        
        tool_desc = ""
        if self.tool == WritingTool.BLOOD:
            tool_desc = "written in blood: "
        elif self.tool == WritingTool.CUM:
            tool_desc = "written in cum: "
        elif self.tool == WritingTool.CARVED:
            tool_desc = "carved: "
        elif self.tool == WritingTool.BRANDED:
            tool_desc = "branded: "
        
        text = f'"{self.text}"'
        
        base = f"{style_desc}{tool_desc}{text}"
        
        if self.signed and self.signature:
            base = f"{base} - {self.signature}"
        
        return base
    
    def to_dict(self):
        data = super().to_dict()
        data.update({
            "text": self.text,
            "tool": self.tool.value,
            "style": self.style.value,
            "signed": self.signed,
            "signature": self.signature,
        })
        return data
    
    @classmethod
    def from_dict(cls, data):
        data = data.copy()
        data["tool"] = WritingTool(data.get("tool", "ink"))
        data["style"] = WritingStyle(data.get("style", "neat"))
        data["surface"] = SurfaceType(data.get("surface", "surface"))
        data["persistence"] = MarkPersistence(data.get("persistence", "temporary"))
        return cls(**{k: v for k, v in data.items() if k in cls.__dataclass_fields__})


@dataclass
class DrawingMark(Mark):
    """
    An image or symbol drawn on a surface.
    """
    mark_type: str = "drawing"
    
    # Drawing content
    subject: str = ""  # What is drawn ("a heart", "a crude penis", "a wolf")
    
    # Style
    tool: WritingTool = WritingTool.INK
    quality: str = "crude"  # crude, rough, decent, good, skilled, masterful
    
    # Is it recognizable?
    recognizable: bool = True
    
    def __post_init__(self):
        super().__post_init__()
        
        # Set persistence based on tool
        if self.tool in (WritingTool.FINGER, WritingTool.CHALK):
            self.persistence = MarkPersistence.TEMPORARY
            if not self.fade_ticks:
                self.fade_ticks = 100
        elif self.tool in (WritingTool.CARVED, WritingTool.BRANDED):
            self.persistence = MarkPersistence.PERMANENT
        else:
            self.persistence = MarkPersistence.SEMI_PERMANENT
            if not self.fade_ticks:
                self.fade_ticks = 1000
    
    def get_display(self, verbose: bool = False) -> str:
        """Get display text for this drawing."""
        quality_desc = ""
        if self.quality in ("crude", "rough"):
            quality_desc = f"a {self.quality} drawing of "
        elif self.quality in ("good", "skilled", "masterful"):
            quality_desc = f"a {self.quality}ly drawn "
        else:
            quality_desc = "a drawing of "
        
        if not self.recognizable:
            return f"an unrecognizable scribble"
        
        return f"{quality_desc}{self.subject}"
    
    def to_dict(self):
        data = super().to_dict()
        data.update({
            "subject": self.subject,
            "tool": self.tool.value,
            "quality": self.quality,
            "recognizable": self.recognizable,
        })
        return data


@dataclass
class SymbolMark(Mark):
    """
    A specific symbol (rune, sigil, sign) on a surface.
    """
    mark_type: str = "symbol"
    
    # Symbol
    symbol_type: str = ""  # "rune", "sigil", "brand_mark", "gang_sign", etc.
    symbol_name: str = ""  # Specific symbol name
    
    # Meaning
    meaning: str = ""  # What it means (if known)
    recognized_by: str = ""  # Who would recognize it
    
    tool: WritingTool = WritingTool.INK
    
    def get_display(self, verbose: bool = False) -> str:
        if self.symbol_name:
            base = f"the symbol of {self.symbol_name}"
        else:
            base = f"a {self.symbol_type}" if self.symbol_type else "a strange symbol"
        
        if verbose and self.meaning:
            base = f"{base} (meaning: {self.meaning})"
        
        return base
    
    def to_dict(self):
        data = super().to_dict()
        data.update({
            "symbol_type": self.symbol_type,
            "symbol_name": self.symbol_name,
            "meaning": self.meaning,
            "recognized_by": self.recognized_by,
            "tool": self.tool.value,
        })
        return data
