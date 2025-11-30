"""
Body Modification System
========================

Permanent and semi-permanent body modifications including:
- Breast enhancement/reduction
- Lactation boosting
- Fertility treatments
- Genital modifications
- Branding, piercing, tattoos
- Surgical alterations
"""

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any, Tuple
from enum import Enum
from datetime import datetime, timedelta
import random


# =============================================================================
# ENUMS
# =============================================================================

class ModificationType(Enum):
    """Categories of body modification."""
    BREAST = "breast"
    GENITAL = "genital"
    FERTILITY = "fertility"
    LACTATION = "lactation"
    COSMETIC = "cosmetic"
    SURGICAL = "surgical"
    MARKING = "marking"
    IMPLANT = "implant"
    HORMONAL = "hormonal"
    MAGICAL = "magical"


class ModificationMethod(Enum):
    """How the modification is applied."""
    INJECTION = "injection"
    SURGERY = "surgery"
    IMPLANT = "implant"
    BRANDING = "branding"
    PIERCING = "piercing"
    TATTOO = "tattoo"
    SCARIFICATION = "scarification"
    POTION = "potion"
    SPELL = "spell"
    GRADUAL = "gradual"           # Over time through use
    PUMP = "pump"                 # Suction-based
    STRETCHING = "stretching"


class BreastSize(Enum):
    """Breast size classifications."""
    FLAT = "flat"
    TINY = "tiny"
    SMALL = "small"
    MODEST = "modest"
    AVERAGE = "average"
    FULL = "full"
    LARGE = "large"
    HUGE = "huge"
    MASSIVE = "massive"
    HYPER = "hyper"
    IMMOBILE = "immobile"


class PiercingLocation(Enum):
    """Locations for piercings."""
    NIPPLE_LEFT = "nipple_left"
    NIPPLE_RIGHT = "nipple_right"
    NIPPLE_BOTH = "nipple_both"
    CLIT = "clit"
    CLIT_HOOD = "clit_hood"
    LABIA = "labia"
    NOSE = "nose"
    NOSE_RING = "nose_ring"       # Bull-style
    SEPTUM = "septum"
    EAR = "ear"
    TONGUE = "tongue"
    BELLY = "belly"
    COCK = "cock"
    COCK_HEAD = "cock_head"
    SCROTUM = "scrotum"


class TattooLocation(Enum):
    """Locations for tattoos."""
    PUBIC = "pubic"
    LOWER_BACK = "lower_back"     # Tramp stamp
    BREAST_LEFT = "breast_left"
    BREAST_RIGHT = "breast_right"
    INNER_THIGH = "inner_thigh"
    BUTTOCK = "buttock"
    WOMB = "womb"                 # Womb tattoo
    FACE = "face"
    NECK = "neck"
    FULL_BODY = "full_body"


# =============================================================================
# MODIFICATION RECORDS
# =============================================================================

@dataclass
class BreastModification:
    """Record of breast modifications."""
    
    mod_id: str = ""
    
    # Current state
    current_size: BreastSize = BreastSize.AVERAGE
    size_cc: int = 300            # Volume in CC
    
    # Natural vs enhanced
    natural_size: BreastSize = BreastSize.AVERAGE
    natural_cc: int = 300
    enhancement_cc: int = 0       # Added volume
    
    # Implants
    has_implants: bool = False
    implant_type: str = ""        # "saline", "silicone", "magical"
    implant_cc: int = 0
    
    # Sensitivity
    sensitivity: int = 50         # 0-100
    enhanced_sensitivity: bool = False
    
    # Lactation capacity
    lactation_enhanced: bool = False
    lactation_multiplier: float = 1.0
    
    # Shape
    shape: str = "natural"        # "natural", "round", "teardrop", "torpedo"
    firmness: int = 50            # 0-100
    sag: int = 20                 # 0-100, increases with size
    
    # Modifications applied
    modifications: List[str] = field(default_factory=list)
    
    def get_size_description(self) -> str:
        """Get descriptive text for breast size."""
        descs = {
            BreastSize.FLAT: "completely flat chest",
            BreastSize.TINY: "barely-there breasts",
            BreastSize.SMALL: "small, perky breasts",
            BreastSize.MODEST: "modest breasts",
            BreastSize.AVERAGE: "average breasts",
            BreastSize.FULL: "full, round breasts",
            BreastSize.LARGE: "large, heavy breasts",
            BreastSize.HUGE: "huge, pendulous breasts",
            BreastSize.MASSIVE: "massive udders",
            BreastSize.HYPER: "impossibly huge milk tanks",
            BreastSize.IMMOBILE: "breasts so large they impede movement",
        }
        return descs.get(self.current_size, "breasts")
    
    def increase_size(self, cc_amount: int, method: str = "injection") -> str:
        """Increase breast size."""
        self.enhancement_cc += cc_amount
        self.size_cc = self.natural_cc + self.enhancement_cc
        
        # Update size category
        old_size = self.current_size
        self.current_size = self._cc_to_size(self.size_cc)
        
        # Increase sag with size
        if self.size_cc > 500:
            self.sag = min(100, self.sag + cc_amount // 50)
        
        self.modifications.append(f"{method}: +{cc_amount}cc")
        
        if old_size != self.current_size:
            return f"Breasts grow from {old_size.value} to {self.current_size.value}!"
        return f"Breasts swell by {cc_amount}cc."
    
    def add_implants(self, implant_cc: int, implant_type: str = "silicone") -> str:
        """Add breast implants."""
        self.has_implants = True
        self.implant_type = implant_type
        self.implant_cc = implant_cc
        self.enhancement_cc += implant_cc
        self.size_cc = self.natural_cc + self.enhancement_cc
        
        # Implants change shape and firmness
        self.shape = "round"
        self.firmness = min(90, self.firmness + 30)
        
        self.current_size = self._cc_to_size(self.size_cc)
        self.modifications.append(f"implants: {implant_type} {implant_cc}cc")
        
        return f"{implant_type.title()} implants ({implant_cc}cc) installed. Now {self.current_size.value}."
    
    def enhance_sensitivity(self, multiplier: float = 1.5) -> str:
        """Enhance nipple sensitivity."""
        self.enhanced_sensitivity = True
        old_sens = self.sensitivity
        self.sensitivity = min(100, int(self.sensitivity * multiplier))
        self.modifications.append(f"sensitivity enhancement: {old_sens} → {self.sensitivity}")
        return f"Nipple sensitivity increased to {self.sensitivity}/100."
    
    def enhance_lactation(self, multiplier: float = 2.0) -> str:
        """Enhance lactation capacity."""
        self.lactation_enhanced = True
        self.lactation_multiplier *= multiplier
        self.modifications.append(f"lactation boost: {multiplier}x")
        return f"Lactation capacity boosted to {self.lactation_multiplier}x normal."
    
    def _cc_to_size(self, cc: int) -> BreastSize:
        """Convert CC to size category."""
        if cc < 50:
            return BreastSize.FLAT
        elif cc < 100:
            return BreastSize.TINY
        elif cc < 200:
            return BreastSize.SMALL
        elif cc < 300:
            return BreastSize.MODEST
        elif cc < 400:
            return BreastSize.AVERAGE
        elif cc < 600:
            return BreastSize.FULL
        elif cc < 900:
            return BreastSize.LARGE
        elif cc < 1500:
            return BreastSize.HUGE
        elif cc < 3000:
            return BreastSize.MASSIVE
        elif cc < 6000:
            return BreastSize.HYPER
        else:
            return BreastSize.IMMOBILE
    
    def to_dict(self) -> dict:
        return {
            "mod_id": self.mod_id,
            "current_size": self.current_size.value,
            "size_cc": self.size_cc,
            "natural_size": self.natural_size.value,
            "natural_cc": self.natural_cc,
            "enhancement_cc": self.enhancement_cc,
            "has_implants": self.has_implants,
            "implant_type": self.implant_type,
            "implant_cc": self.implant_cc,
            "sensitivity": self.sensitivity,
            "enhanced_sensitivity": self.enhanced_sensitivity,
            "lactation_enhanced": self.lactation_enhanced,
            "lactation_multiplier": self.lactation_multiplier,
            "shape": self.shape,
            "firmness": self.firmness,
            "sag": self.sag,
            "modifications": self.modifications,
        }
    
    @classmethod
    def from_dict(cls, data: dict) -> "BreastModification":
        mod = cls()
        for key, value in data.items():
            if key == "current_size":
                mod.current_size = BreastSize(value)
            elif key == "natural_size":
                mod.natural_size = BreastSize(value)
            elif hasattr(mod, key):
                setattr(mod, key, value)
        return mod


@dataclass
class GenitalModification:
    """Record of genital modifications."""
    
    mod_id: str = ""
    
    # Sex configuration
    has_vagina: bool = True
    has_penis: bool = False
    
    # Vaginal modifications
    vaginal_tightness: int = 50   # 0-100
    vaginal_depth_cm: int = 15
    vaginal_enhanced: bool = False
    
    # Clitoral modifications
    clit_size: str = "normal"     # "tiny", "small", "normal", "large", "huge", "cock-like"
    clit_sensitivity: int = 70
    clit_enhanced: bool = False
    
    # Penis modifications (for futanari/male)
    penis_length_cm: int = 0
    penis_girth_cm: int = 0
    penis_enhanced: bool = False
    has_knot: bool = False
    knot_size_cm: int = 0
    
    # Balls (for futanari/male)
    has_balls: bool = False
    ball_size: str = "none"       # "none", "small", "average", "large", "huge", "hyper"
    cum_production: int = 0       # ml per ejaculation
    
    # Modifications applied
    modifications: List[str] = field(default_factory=list)
    
    def add_penis(
        self,
        length_cm: int = 15,
        girth_cm: int = 12,
        with_balls: bool = True,
    ) -> str:
        """Add a penis (futanari transformation)."""
        self.has_penis = True
        self.penis_length_cm = length_cm
        self.penis_girth_cm = girth_cm
        
        if with_balls:
            self.has_balls = True
            self.ball_size = "average"
            self.cum_production = 15
        
        self.modifications.append(f"penis growth: {length_cm}cm")
        return f"A {length_cm}cm cock grows, making you a futanari!"
    
    def enhance_penis(self, length_gain: int = 5, girth_gain: int = 3) -> str:
        """Enhance existing penis."""
        if not self.has_penis:
            return "No penis to enhance."
        
        self.penis_length_cm += length_gain
        self.penis_girth_cm += girth_gain
        self.penis_enhanced = True
        
        self.modifications.append(f"penis enhancement: +{length_gain}cm length, +{girth_gain}cm girth")
        return f"Penis grows to {self.penis_length_cm}cm long, {self.penis_girth_cm}cm thick."
    
    def add_knot(self, knot_size_cm: int = 8) -> str:
        """Add a knot to the penis."""
        if not self.has_penis:
            return "No penis to add knot to."
        
        self.has_knot = True
        self.knot_size_cm = knot_size_cm
        
        self.modifications.append(f"knot growth: {knot_size_cm}cm")
        return f"A {knot_size_cm}cm knot develops at the base of your cock!"
    
    def tighten_vagina(self, amount: int = 20) -> str:
        """Tighten vaginal muscles."""
        if not self.has_vagina:
            return "No vagina to tighten."
        
        old = self.vaginal_tightness
        self.vaginal_tightness = min(100, self.vaginal_tightness + amount)
        self.vaginal_enhanced = True
        
        self.modifications.append(f"vaginal tightening: {old} → {self.vaginal_tightness}")
        return f"Vagina tightened to {self.vaginal_tightness}/100."
    
    def loosen_vagina(self, amount: int = 20) -> str:
        """Loosen/stretch vagina for larger insertions."""
        if not self.has_vagina:
            return "No vagina to stretch."
        
        old = self.vaginal_tightness
        self.vaginal_tightness = max(0, self.vaginal_tightness - amount)
        self.vaginal_depth_cm += amount // 5
        
        self.modifications.append(f"vaginal stretching: {old} → {self.vaginal_tightness}")
        return f"Vagina loosened. Tightness: {self.vaginal_tightness}/100, Depth: {self.vaginal_depth_cm}cm."
    
    def enhance_clit(self, growth: str = "large") -> str:
        """Enhance clitoris size."""
        if not self.has_vagina:
            return "No clitoris to enhance."
        
        self.clit_size = growth
        self.clit_sensitivity = min(100, self.clit_sensitivity + 20)
        self.clit_enhanced = True
        
        self.modifications.append(f"clit enhancement: {growth}")
        
        if growth == "cock-like":
            return "Clitoris grows into a small cock-like nub, incredibly sensitive!"
        return f"Clitoris grows to {growth} size."
    
    def enhance_cum_production(self, multiplier: float = 2.0) -> str:
        """Increase cum production."""
        if not self.has_balls:
            return "No balls to enhance."
        
        old = self.cum_production
        self.cum_production = int(self.cum_production * multiplier)
        
        # Increase ball size
        sizes = ["small", "average", "large", "huge", "hyper"]
        current_idx = sizes.index(self.ball_size) if self.ball_size in sizes else 1
        if current_idx < len(sizes) - 1:
            self.ball_size = sizes[current_idx + 1]
        
        self.modifications.append(f"cum production: {old}ml → {self.cum_production}ml")
        return f"Balls swell to {self.ball_size}. Cum production: {self.cum_production}ml."
    
    def to_dict(self) -> dict:
        return {
            "mod_id": self.mod_id,
            "has_vagina": self.has_vagina,
            "has_penis": self.has_penis,
            "vaginal_tightness": self.vaginal_tightness,
            "vaginal_depth_cm": self.vaginal_depth_cm,
            "vaginal_enhanced": self.vaginal_enhanced,
            "clit_size": self.clit_size,
            "clit_sensitivity": self.clit_sensitivity,
            "clit_enhanced": self.clit_enhanced,
            "penis_length_cm": self.penis_length_cm,
            "penis_girth_cm": self.penis_girth_cm,
            "penis_enhanced": self.penis_enhanced,
            "has_knot": self.has_knot,
            "knot_size_cm": self.knot_size_cm,
            "has_balls": self.has_balls,
            "ball_size": self.ball_size,
            "cum_production": self.cum_production,
            "modifications": self.modifications,
        }
    
    @classmethod
    def from_dict(cls, data: dict) -> "GenitalModification":
        mod = cls()
        for key, value in data.items():
            if hasattr(mod, key):
                setattr(mod, key, value)
        return mod


@dataclass
class Piercing:
    """A single piercing."""
    
    piercing_id: str = ""
    location: PiercingLocation = PiercingLocation.EAR
    
    jewelry_type: str = "ring"    # "ring", "barbell", "stud", "chain"
    jewelry_material: str = "steel"
    jewelry_description: str = ""
    
    # Effects
    sensitivity_mod: int = 0      # Added sensitivity
    is_locked: bool = False       # Can't be removed
    has_chain: bool = False       # Connected to something
    chain_to: str = ""            # What it's chained to
    
    # Ownership
    applied_by: str = ""
    applied_date: Optional[datetime] = None
    
    def get_description(self) -> str:
        """Get piercing description."""
        desc = f"a {self.jewelry_material} {self.jewelry_type} through the {self.location.value}"
        if self.is_locked:
            desc += " (locked)"
        if self.has_chain:
            desc += f" chained to {self.chain_to}"
        return desc


@dataclass
class Tattoo:
    """A single tattoo."""
    
    tattoo_id: str = ""
    location: TattooLocation = TattooLocation.LOWER_BACK
    
    design: str = ""              # Description of the tattoo
    text: str = ""                # Any text in the tattoo
    color: str = "black"
    size: str = "medium"          # "small", "medium", "large", "full"
    
    # Special types
    is_ownership_mark: bool = False
    owner_name: str = ""
    
    is_womb_tattoo: bool = False  # Special marking
    is_slave_number: bool = False
    
    # Magical tattoos
    is_magical: bool = False
    magical_effect: str = ""
    
    applied_by: str = ""
    applied_date: Optional[datetime] = None
    
    def get_description(self) -> str:
        """Get tattoo description."""
        desc = f"a {self.size} {self.color} tattoo on the {self.location.value}"
        if self.design:
            desc += f" depicting {self.design}"
        if self.text:
            desc += f" reading '{self.text}'"
        if self.is_ownership_mark:
            desc += f" (property of {self.owner_name})"
        return desc


@dataclass
class Brand:
    """A brand mark."""
    
    brand_id: str = ""
    location: str = ""            # Where on the body
    
    design: str = ""              # What the brand depicts
    size_cm: int = 5
    
    brand_type: str = "burn"      # "burn", "freeze", "chemical", "magical"
    
    # Ownership
    is_ownership_brand: bool = True
    owner_name: str = ""
    owner_symbol: str = ""
    
    applied_by: str = ""
    applied_date: Optional[datetime] = None
    
    def get_description(self) -> str:
        """Get brand description."""
        desc = f"a {self.size_cm}cm {self.brand_type} brand on the {self.location}"
        if self.design:
            desc += f" in the shape of {self.design}"
        if self.is_ownership_brand:
            desc += f" marking them as property of {self.owner_name}"
        return desc


# =============================================================================
# FERTILITY MODIFICATIONS
# =============================================================================

@dataclass
class FertilityModification:
    """Record of fertility modifications."""
    
    mod_id: str = ""
    
    # Base fertility
    base_fertility: int = 50      # 0-100
    current_fertility: int = 50
    
    # Enhancements
    fertility_enhanced: bool = False
    fertility_multiplier: float = 1.0
    
    # Heat cycle modifications
    natural_cycle_days: int = 28
    current_cycle_days: int = 28
    heat_intensity_mod: int = 0   # Added to natural intensity
    permanent_heat: bool = False  # Always in heat
    
    # Pregnancy modifications
    pregnancy_speed: float = 1.0  # Multiplier for pregnancy duration
    litter_size_mod: int = 0      # Added to base litter size
    guaranteed_conception: bool = False
    
    # Sterilization
    is_sterilized: bool = False
    sterilization_reversible: bool = True
    
    # Modifications applied
    modifications: List[str] = field(default_factory=list)
    
    def boost_fertility(self, amount: int = 20) -> str:
        """Increase fertility rating."""
        old = self.current_fertility
        self.current_fertility = min(100, self.current_fertility + amount)
        self.fertility_enhanced = True
        
        self.modifications.append(f"fertility boost: {old} → {self.current_fertility}")
        return f"Fertility increased to {self.current_fertility}/100."
    
    def induce_permanent_heat(self) -> str:
        """Make subject permanently in heat."""
        self.permanent_heat = True
        self.heat_intensity_mod = 30
        
        self.modifications.append("permanent heat induction")
        return "Permanently locked in heat! Body constantly aches for breeding."
    
    def shorten_cycle(self, new_days: int = 7) -> str:
        """Shorten heat cycle for more frequent breeding."""
        old = self.current_cycle_days
        self.current_cycle_days = new_days
        
        self.modifications.append(f"cycle shortened: {old} → {new_days} days")
        return f"Heat cycle shortened to {new_days} days."
    
    def enhance_litter_size(self, additional: int = 1) -> str:
        """Increase potential litter size."""
        self.litter_size_mod += additional
        
        self.modifications.append(f"litter enhancement: +{additional}")
        return f"Litter size potential increased by {additional}."
    
    def speed_pregnancy(self, multiplier: float = 2.0) -> str:
        """Speed up pregnancy duration."""
        self.pregnancy_speed = multiplier
        
        self.modifications.append(f"pregnancy acceleration: {multiplier}x")
        return f"Pregnancy will progress {multiplier}x faster."
    
    def sterilize(self, reversible: bool = True) -> str:
        """Sterilize the subject."""
        self.is_sterilized = True
        self.sterilization_reversible = reversible
        self.current_fertility = 0
        
        perm = "temporarily" if reversible else "permanently"
        self.modifications.append(f"sterilization ({perm})")
        return f"Subject {perm} sterilized."
    
    def to_dict(self) -> dict:
        return {
            "mod_id": self.mod_id,
            "base_fertility": self.base_fertility,
            "current_fertility": self.current_fertility,
            "fertility_enhanced": self.fertility_enhanced,
            "fertility_multiplier": self.fertility_multiplier,
            "natural_cycle_days": self.natural_cycle_days,
            "current_cycle_days": self.current_cycle_days,
            "heat_intensity_mod": self.heat_intensity_mod,
            "permanent_heat": self.permanent_heat,
            "pregnancy_speed": self.pregnancy_speed,
            "litter_size_mod": self.litter_size_mod,
            "guaranteed_conception": self.guaranteed_conception,
            "is_sterilized": self.is_sterilized,
            "sterilization_reversible": self.sterilization_reversible,
            "modifications": self.modifications,
        }
    
    @classmethod
    def from_dict(cls, data: dict) -> "FertilityModification":
        mod = cls()
        for key, value in data.items():
            if hasattr(mod, key):
                setattr(mod, key, value)
        return mod


# =============================================================================
# COMPLETE MODIFICATION RECORD
# =============================================================================

@dataclass
class BodyModifications:
    """Complete record of all body modifications."""
    
    subject_dbref: str = ""
    subject_name: str = ""
    
    # Sub-records
    breasts: BreastModification = field(default_factory=BreastModification)
    genitals: GenitalModification = field(default_factory=GenitalModification)
    fertility: FertilityModification = field(default_factory=FertilityModification)
    
    # Piercings
    piercings: List[Piercing] = field(default_factory=list)
    
    # Tattoos
    tattoos: List[Tattoo] = field(default_factory=list)
    
    # Brands
    brands: List[Brand] = field(default_factory=list)
    
    # Other modifications
    other_mods: List[str] = field(default_factory=list)
    
    # Tracking
    total_procedures: int = 0
    last_modification: Optional[datetime] = None
    
    def add_piercing(self, piercing: Piercing) -> str:
        """Add a piercing."""
        self.piercings.append(piercing)
        self.total_procedures += 1
        self.last_modification = datetime.now()
        return f"Piercing added: {piercing.get_description()}"
    
    def add_tattoo(self, tattoo: Tattoo) -> str:
        """Add a tattoo."""
        self.tattoos.append(tattoo)
        self.total_procedures += 1
        self.last_modification = datetime.now()
        return f"Tattoo added: {tattoo.get_description()}"
    
    def add_brand(self, brand: Brand) -> str:
        """Add a brand."""
        self.brands.append(brand)
        self.total_procedures += 1
        self.last_modification = datetime.now()
        return f"Branded: {brand.get_description()}"
    
    @property
    def is_futanari(self) -> bool:
        """Check if subject is futanari."""
        return self.genitals.has_vagina and self.genitals.has_penis
    
    def get_summary(self) -> str:
        """Get modification summary."""
        lines = [f"=== Body Modifications: {self.subject_name} ==="]
        
        # Breasts
        lines.append(f"\n--- Breasts ---")
        lines.append(f"Size: {self.breasts.current_size.value} ({self.breasts.size_cc}cc)")
        if self.breasts.has_implants:
            lines.append(f"Implants: {self.breasts.implant_type} ({self.breasts.implant_cc}cc)")
        lines.append(f"Sensitivity: {self.breasts.sensitivity}/100")
        if self.breasts.lactation_enhanced:
            lines.append(f"Lactation: {self.breasts.lactation_multiplier}x enhanced")
        
        # Genitals
        lines.append(f"\n--- Genitals ---")
        if self.genitals.has_vagina:
            lines.append(f"Vagina: tightness {self.genitals.vaginal_tightness}/100, depth {self.genitals.vaginal_depth_cm}cm")
            lines.append(f"Clit: {self.genitals.clit_size}")
        if self.genitals.has_penis:
            lines.append(f"Penis: {self.genitals.penis_length_cm}cm x {self.genitals.penis_girth_cm}cm")
            if self.genitals.has_knot:
                lines.append(f"Knot: {self.genitals.knot_size_cm}cm")
            if self.genitals.has_balls:
                lines.append(f"Balls: {self.genitals.ball_size}, {self.genitals.cum_production}ml")
        
        # Fertility
        lines.append(f"\n--- Fertility ---")
        lines.append(f"Rating: {self.fertility.current_fertility}/100")
        lines.append(f"Cycle: {self.fertility.current_cycle_days} days")
        if self.fertility.permanent_heat:
            lines.append("PERMANENTLY IN HEAT")
        if self.fertility.is_sterilized:
            lines.append("STERILIZED")
        
        # Markings
        if self.piercings:
            lines.append(f"\n--- Piercings ({len(self.piercings)}) ---")
            for p in self.piercings[:5]:
                lines.append(f"  • {p.get_description()}")
        
        if self.tattoos:
            lines.append(f"\n--- Tattoos ({len(self.tattoos)}) ---")
            for t in self.tattoos[:5]:
                lines.append(f"  • {t.get_description()}")
        
        if self.brands:
            lines.append(f"\n--- Brands ({len(self.brands)}) ---")
            for b in self.brands:
                lines.append(f"  • {b.get_description()}")
        
        lines.append(f"\nTotal Procedures: {self.total_procedures}")
        
        return "\n".join(lines)
    
    def to_dict(self) -> dict:
        return {
            "subject_dbref": self.subject_dbref,
            "subject_name": self.subject_name,
            "breasts": self.breasts.to_dict(),
            "genitals": self.genitals.to_dict(),
            "fertility": self.fertility.to_dict(),
            "piercings": [{"location": p.location.value, "jewelry_type": p.jewelry_type, 
                          "is_locked": p.is_locked} for p in self.piercings],
            "tattoos": [{"location": t.location.value, "design": t.design, 
                        "text": t.text} for t in self.tattoos],
            "brands": [{"location": b.location, "design": b.design,
                       "owner_name": b.owner_name} for b in self.brands],
            "other_mods": self.other_mods,
            "total_procedures": self.total_procedures,
            "last_modification": self.last_modification.isoformat() if self.last_modification else None,
        }
    
    @classmethod
    def from_dict(cls, data: dict) -> "BodyModifications":
        mods = cls()
        mods.subject_dbref = data.get("subject_dbref", "")
        mods.subject_name = data.get("subject_name", "")
        
        if "breasts" in data:
            mods.breasts = BreastModification.from_dict(data["breasts"])
        if "genitals" in data:
            mods.genitals = GenitalModification.from_dict(data["genitals"])
        if "fertility" in data:
            mods.fertility = FertilityModification.from_dict(data["fertility"])
        
        mods.other_mods = data.get("other_mods", [])
        mods.total_procedures = data.get("total_procedures", 0)
        
        if data.get("last_modification"):
            mods.last_modification = datetime.fromisoformat(data["last_modification"])
        
        return mods


# =============================================================================
# MODIFICATION MIXIN
# =============================================================================

class BodyModificationMixin:
    """Mixin for characters that can have body modifications."""
    
    @property
    def body_mods(self) -> BodyModifications:
        """Get body modifications."""
        data = self.db.body_modifications
        if data:
            return BodyModifications.from_dict(data)
        return BodyModifications(subject_dbref=self.dbref, subject_name=self.key)
    
    @body_mods.setter
    def body_mods(self, mods: BodyModifications) -> None:
        """Set body modifications."""
        self.db.body_modifications = mods.to_dict()
    
    def save_body_mods(self, mods: BodyModifications) -> None:
        """Save body modifications."""
        self.db.body_modifications = mods.to_dict()


__all__ = [
    "ModificationType",
    "ModificationMethod",
    "BreastSize",
    "PiercingLocation",
    "TattooLocation",
    "BreastModification",
    "GenitalModification",
    "Piercing",
    "Tattoo",
    "Brand",
    "FertilityModification",
    "BodyModifications",
    "BodyModificationMixin",
]
