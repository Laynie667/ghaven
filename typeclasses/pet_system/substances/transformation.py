"""
Transformation System
=====================

Species and body transformations:
- Temporary transformations
- Permanent changes
- Partial transformations
- Transformation stages
"""

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any, Tuple
from enum import Enum
from datetime import datetime, timedelta
import random

from .potions import SubstanceType, EffectIntensity, Substance, SubstanceEffect, EffectCategory


# =============================================================================
# ENUMS
# =============================================================================

class TransformationType(Enum):
    """Types of transformation."""
    SPECIES = "species"           # Full species change
    PARTIAL = "partial"           # Partial features (ears, tail)
    GENDER = "gender"             # Gender/sex change
    SIZE = "size"                 # Size changes
    FEATURE = "feature"           # Specific feature change
    MENTAL = "mental"             # Mental/behavioral


class TransformationDuration(Enum):
    """How long transformation lasts."""
    TEMPORARY = "temporary"       # Hours
    EXTENDED = "extended"         # Days
    SEMI_PERMANENT = "semi_permanent"  # Weeks
    PERMANENT = "permanent"       # Forever


class TransformationStage(Enum):
    """Stage of an active transformation."""
    BEGINNING = "beginning"       # Just started
    PROGRESSING = "progressing"   # Actively changing
    COMPLETE = "complete"         # Fully transformed
    FADING = "fading"            # Reverting
    REVERSED = "reversed"         # Back to normal


# =============================================================================
# BODY CHANGES
# =============================================================================

@dataclass
class BodyChange:
    """A specific change to the body."""
    change_id: str
    name: str
    
    # What's changing
    body_part: str = ""          # "ears", "tail", "skin", etc.
    target_form: str = ""        # What it becomes
    
    # Description
    description: str = ""
    change_message: str = ""
    revert_message: str = ""
    
    def to_dict(self) -> dict:
        return {
            "change_id": self.change_id,
            "name": self.name,
            "body_part": self.body_part,
            "target_form": self.target_form,
            "description": self.description,
            "change_message": self.change_message,
            "revert_message": self.revert_message,
        }
    
    @classmethod
    def from_dict(cls, data: dict) -> "BodyChange":
        return cls(
            change_id=data["change_id"],
            name=data["name"],
            body_part=data.get("body_part", ""),
            target_form=data.get("target_form", ""),
            description=data.get("description", ""),
            change_message=data.get("change_message", ""),
            revert_message=data.get("revert_message", ""),
        )


# Predefined body changes
CHANGE_CAT_EARS = BodyChange(
    change_id="cat_ears",
    name="Cat Ears",
    body_part="ears",
    target_form="feline",
    change_message="Your ears shift and migrate, becoming fuzzy cat ears atop your head.",
    revert_message="Your ears return to their normal form.",
)

CHANGE_CAT_TAIL = BodyChange(
    change_id="cat_tail",
    name="Cat Tail",
    body_part="tail",
    target_form="feline",
    change_message="A long, slender cat tail sprouts from your lower back.",
    revert_message="Your tail shrinks away and disappears.",
)

CHANGE_WOLF_EARS = BodyChange(
    change_id="wolf_ears",
    name="Wolf Ears",
    body_part="ears",
    target_form="lupine",
    change_message="Your ears become tall, pointed wolf ears.",
    revert_message="Your ears return to normal.",
)

CHANGE_WOLF_TAIL = BodyChange(
    change_id="wolf_tail",
    name="Wolf Tail",
    body_part="tail",
    target_form="lupine",
    change_message="A thick, bushy wolf tail grows from your tailbone.",
    revert_message="Your tail withdraws and vanishes.",
)

CHANGE_HORSE_EARS = BodyChange(
    change_id="horse_ears",
    name="Horse Ears",
    body_part="ears",
    target_form="equine",
    change_message="Your ears elongate into horse ears.",
    revert_message="Your ears shrink back to normal.",
)

CHANGE_HORSE_TAIL = BodyChange(
    change_id="horse_tail",
    name="Horse Tail",
    body_part="tail",
    target_form="equine",
    change_message="A long, flowing horse tail grows from your rear.",
    revert_message="Your tail falls away.",
)

CHANGE_COW_HORNS = BodyChange(
    change_id="cow_horns",
    name="Cow Horns",
    body_part="horns",
    target_form="bovine",
    change_message="Small horns push through your scalp and curve slightly.",
    revert_message="Your horns crumble away.",
)

CHANGE_COW_TAIL = BodyChange(
    change_id="cow_tail",
    name="Cow Tail",
    body_part="tail",
    target_form="bovine",
    change_message="A thin tail with a tuft at the end grows from your tailbone.",
    revert_message="Your tail disappears.",
)

CHANGE_SCALES = BodyChange(
    change_id="scales",
    name="Scales",
    body_part="skin",
    target_form="reptilian",
    change_message="Scales begin spreading across your skin.",
    revert_message="Your scales soften and fade back to normal skin.",
)

CHANGE_FUR = BodyChange(
    change_id="fur",
    name="Fur Coat",
    body_part="skin",
    target_form="furred",
    change_message="Soft fur sprouts across your body.",
    revert_message="Your fur sheds and disappears.",
)

CHANGE_CLAWS = BodyChange(
    change_id="claws",
    name="Claws",
    body_part="hands",
    target_form="clawed",
    change_message="Your nails extend into sharp claws.",
    revert_message="Your claws retract back to normal nails.",
)

CHANGE_FANGS = BodyChange(
    change_id="fangs",
    name="Fangs",
    body_part="teeth",
    target_form="fanged",
    change_message="Your canines grow into pronounced fangs.",
    revert_message="Your fangs shrink back to normal.",
)


# =============================================================================
# TRANSFORMATION DEFINITION
# =============================================================================

@dataclass
class Transformation:
    """A transformation template."""
    key: str
    name: str
    transformation_type: TransformationType = TransformationType.PARTIAL
    
    # Target
    target_species: str = ""     # For full species change
    body_changes: List[BodyChange] = field(default_factory=list)
    
    # Duration
    duration_type: TransformationDuration = TransformationDuration.TEMPORARY
    base_duration_hours: int = 4
    
    # Intensity affects how complete the transformation is
    intensity: EffectIntensity = EffectIntensity.MODERATE
    
    # Requirements
    requires_species: List[str] = field(default_factory=list)  # Only these can transform
    excludes_species: List[str] = field(default_factory=list)  # These cannot
    
    # Description
    description: str = ""
    begin_message: str = "Your body begins to change..."
    complete_message: str = "The transformation is complete."
    fade_message: str = "The transformation begins to fade."
    
    def get_duration_hours(self) -> int:
        """Get actual duration."""
        multipliers = {
            TransformationDuration.TEMPORARY: 1,
            TransformationDuration.EXTENDED: 6,
            TransformationDuration.SEMI_PERMANENT: 24,
            TransformationDuration.PERMANENT: 0,  # Never ends
        }
        return self.base_duration_hours * multipliers.get(self.duration_type, 1)
    
    def to_dict(self) -> dict:
        return {
            "key": self.key,
            "name": self.name,
            "transformation_type": self.transformation_type.value,
            "target_species": self.target_species,
            "body_changes": [bc.to_dict() for bc in self.body_changes],
            "duration_type": self.duration_type.value,
            "base_duration_hours": self.base_duration_hours,
            "intensity": self.intensity.value,
            "requires_species": self.requires_species,
            "excludes_species": self.excludes_species,
            "description": self.description,
            "begin_message": self.begin_message,
            "complete_message": self.complete_message,
            "fade_message": self.fade_message,
        }
    
    @classmethod
    def from_dict(cls, data: dict) -> "Transformation":
        tf = cls(
            key=data["key"],
            name=data["name"],
        )
        tf.transformation_type = TransformationType(data.get("transformation_type", "partial"))
        tf.target_species = data.get("target_species", "")
        tf.body_changes = [BodyChange.from_dict(bc) for bc in data.get("body_changes", [])]
        tf.duration_type = TransformationDuration(data.get("duration_type", "temporary"))
        tf.base_duration_hours = data.get("base_duration_hours", 4)
        tf.intensity = EffectIntensity(data.get("intensity", "moderate"))
        tf.requires_species = data.get("requires_species", [])
        tf.excludes_species = data.get("excludes_species", [])
        tf.description = data.get("description", "")
        tf.begin_message = data.get("begin_message", "")
        tf.complete_message = data.get("complete_message", "")
        tf.fade_message = data.get("fade_message", "")
        return tf


# =============================================================================
# ACTIVE TRANSFORMATION
# =============================================================================

@dataclass
class ActiveTransformation:
    """An active transformation on a character."""
    transformation: Transformation
    
    # State
    stage: TransformationStage = TransformationStage.BEGINNING
    progress: int = 0            # 0-100
    
    # Original state (for reverting)
    original_species: str = ""
    original_features: Dict[str, str] = field(default_factory=dict)
    
    # Timing
    started_at: Optional[datetime] = None
    expires_at: Optional[datetime] = None
    
    @property
    def is_complete(self) -> bool:
        """Check if transformation is complete."""
        return self.stage == TransformationStage.COMPLETE
    
    @property
    def is_expired(self) -> bool:
        """Check if transformation should end."""
        if self.transformation.duration_type == TransformationDuration.PERMANENT:
            return False
        if self.expires_at and datetime.now() >= self.expires_at:
            return True
        return False
    
    @property
    def remaining_hours(self) -> int:
        """Get remaining duration."""
        if not self.expires_at:
            return 999  # Permanent
        delta = self.expires_at - datetime.now()
        return max(0, int(delta.total_seconds() / 3600))
    
    def advance(self, amount: int = 10) -> Tuple[bool, str]:
        """
        Advance transformation progress.
        Returns (stage_changed, message).
        """
        if self.stage == TransformationStage.COMPLETE:
            return False, ""
        
        self.progress += amount
        
        if self.progress >= 100:
            self.progress = 100
            self.stage = TransformationStage.COMPLETE
            return True, self.transformation.complete_message
        elif self.progress >= 50 and self.stage == TransformationStage.BEGINNING:
            self.stage = TransformationStage.PROGRESSING
            return True, "The transformation intensifies..."
        
        return False, ""
    
    def begin_fade(self) -> str:
        """Begin reverting the transformation."""
        self.stage = TransformationStage.FADING
        return self.transformation.fade_message
    
    def to_dict(self) -> dict:
        return {
            "transformation": self.transformation.to_dict(),
            "stage": self.stage.value,
            "progress": self.progress,
            "original_species": self.original_species,
            "original_features": self.original_features,
            "started_at": self.started_at.isoformat() if self.started_at else None,
            "expires_at": self.expires_at.isoformat() if self.expires_at else None,
        }
    
    @classmethod
    def from_dict(cls, data: dict) -> "ActiveTransformation":
        at = cls(
            transformation=Transformation.from_dict(data["transformation"]),
        )
        at.stage = TransformationStage(data.get("stage", "beginning"))
        at.progress = data.get("progress", 0)
        at.original_species = data.get("original_species", "")
        at.original_features = data.get("original_features", {})
        
        if data.get("started_at"):
            at.started_at = datetime.fromisoformat(data["started_at"])
        if data.get("expires_at"):
            at.expires_at = datetime.fromisoformat(data["expires_at"])
        
        return at


# =============================================================================
# PREDEFINED TRANSFORMATIONS
# =============================================================================

TF_CATGIRL = Transformation(
    key="catgirl",
    name="Catgirl Transformation",
    transformation_type=TransformationType.PARTIAL,
    body_changes=[CHANGE_CAT_EARS, CHANGE_CAT_TAIL, CHANGE_FANGS],
    duration_type=TransformationDuration.TEMPORARY,
    base_duration_hours=4,
    description="Gain cat ears, tail, and fangs.",
    begin_message="Your body tingles as feline features begin to emerge.",
    complete_message="You now have adorable cat ears, a swishing tail, and cute little fangs!",
)

TF_WOLFKIN = Transformation(
    key="wolfkin",
    name="Wolf Features",
    transformation_type=TransformationType.PARTIAL,
    body_changes=[CHANGE_WOLF_EARS, CHANGE_WOLF_TAIL, CHANGE_FANGS, CHANGE_CLAWS],
    duration_type=TransformationDuration.TEMPORARY,
    base_duration_hours=6,
    description="Gain wolf ears, tail, fangs, and claws.",
    begin_message="A primal energy flows through you as wolf features emerge.",
    complete_message="You've gained the features of a wolf - ears, tail, fangs and claws!",
)

TF_COWGIRL = Transformation(
    key="cowgirl",
    name="Cow Features",
    transformation_type=TransformationType.PARTIAL,
    body_changes=[CHANGE_COW_HORNS, CHANGE_COW_TAIL],
    duration_type=TransformationDuration.EXTENDED,
    base_duration_hours=8,
    description="Gain cow horns and tail.",
    begin_message="You feel pressure at your temples as bovine features develop.",
    complete_message="Small horns crown your head and a thin tail swishes behind you.",
)

TF_PONYGIRL = Transformation(
    key="ponygirl",
    name="Pony Features",
    transformation_type=TransformationType.PARTIAL,
    body_changes=[CHANGE_HORSE_EARS, CHANGE_HORSE_TAIL],
    duration_type=TransformationDuration.TEMPORARY,
    base_duration_hours=4,
    description="Gain horse ears and tail.",
    begin_message="Equine energy flows through you.",
    complete_message="Your horse ears perk up and your new tail swishes!",
)

TF_FULL_CATFOLK = Transformation(
    key="full_catfolk",
    name="Full Catfolk",
    transformation_type=TransformationType.SPECIES,
    target_species="catfolk",
    body_changes=[CHANGE_CAT_EARS, CHANGE_CAT_TAIL, CHANGE_FANGS, CHANGE_FUR, CHANGE_CLAWS],
    duration_type=TransformationDuration.SEMI_PERMANENT,
    base_duration_hours=24,
    intensity=EffectIntensity.STRONG,
    description="Full transformation into a catfolk.",
    begin_message="The transformation is intense - your entire body is changing!",
    complete_message="You are now fully catfolk, covered in soft fur with feline features.",
)

TF_DRAGONKIN = Transformation(
    key="dragonkin",
    name="Dragon Features",
    transformation_type=TransformationType.PARTIAL,
    body_changes=[CHANGE_SCALES, CHANGE_CLAWS, CHANGE_FANGS],
    duration_type=TransformationDuration.EXTENDED,
    base_duration_hours=12,
    intensity=EffectIntensity.STRONG,
    description="Gain dragon scales, claws, and fangs.",
    begin_message="Draconic power surges through your veins!",
    complete_message="Scales cover your skin and your claws gleam dangerously.",
)


# =============================================================================
# TRANSFORMATION POTIONS
# =============================================================================

POTION_CATGIRL = Substance(
    key="catgirl_potion",
    name="Essence of Feline",
    substance_type=SubstanceType.POTION,
    effects=[],  # Effects handled by transformation system
    color="amber",
    taste="fishy",
    smell="musky",
    base_value=150,
    rarity="uncommon",
    description="Grants temporary cat features.",
    consume_message="You drink the amber potion. It tastes faintly of fish.",
)

POTION_WOLFKIN = Substance(
    key="wolfkin_potion",
    name="Wolf's Blood",
    substance_type=SubstanceType.POTION,
    effects=[],
    color="deep red",
    taste="metallic",
    smell="wild",
    base_value=200,
    rarity="uncommon",
    description="Grants temporary wolf features.",
    consume_message="The blood-red potion courses through you with primal power.",
)

POTION_COWGIRL = Substance(
    key="cowgirl_potion",
    name="Bovine Elixir",
    substance_type=SubstanceType.POTION,
    effects=[],
    color="creamy white",
    taste="milky",
    smell="grassy",
    base_value=150,
    rarity="uncommon",
    description="Grants cow features.",
    consume_message="The creamy potion slides down your throat.",
)

POTION_PONYGIRL = Substance(
    key="ponygirl_potion",
    name="Equine Essence",
    substance_type=SubstanceType.POTION,
    effects=[],
    color="golden",
    taste="oaty",
    smell="hay-like",
    base_value=175,
    rarity="uncommon",
    description="Grants pony features.",
    consume_message="You drink the golden elixir.",
)


# =============================================================================
# REGISTRIES
# =============================================================================

ALL_TRANSFORMATIONS: Dict[str, Transformation] = {
    "catgirl": TF_CATGIRL,
    "wolfkin": TF_WOLFKIN,
    "cowgirl": TF_COWGIRL,
    "ponygirl": TF_PONYGIRL,
    "full_catfolk": TF_FULL_CATFOLK,
    "dragonkin": TF_DRAGONKIN,
}

# Map potions to transformations
POTION_TRANSFORMATION_MAP: Dict[str, str] = {
    "catgirl_potion": "catgirl",
    "wolfkin_potion": "wolfkin",
    "cowgirl_potion": "cowgirl",
    "ponygirl_potion": "ponygirl",
}


def get_transformation(key: str) -> Optional[Transformation]:
    """Get a transformation by key."""
    template = ALL_TRANSFORMATIONS.get(key)
    if template:
        return Transformation.from_dict(template.to_dict())
    return None


# =============================================================================
# TRANSFORMATION SYSTEM
# =============================================================================

class TransformationSystem:
    """
    Manages transformations.
    """
    
    @staticmethod
    def can_transform(
        character,
        transformation: Transformation,
    ) -> Tuple[bool, str]:
        """Check if character can undergo transformation."""
        current_species = getattr(character, 'species', 'human')
        
        # Check requirements
        if transformation.requires_species:
            if current_species.lower() not in [s.lower() for s in transformation.requires_species]:
                return False, f"This transformation requires species: {', '.join(transformation.requires_species)}"
        
        # Check exclusions
        if transformation.excludes_species:
            if current_species.lower() in [s.lower() for s in transformation.excludes_species]:
                return False, f"This transformation cannot affect {current_species}."
        
        # Check for existing transformation
        if hasattr(character, 'active_transformation'):
            existing = character.active_transformation
            if existing and not existing.is_expired:
                return False, "Already undergoing a transformation."
        
        return True, ""
    
    @staticmethod
    def begin_transformation(
        character,
        transformation: Transformation,
    ) -> Tuple[bool, str]:
        """Begin a transformation."""
        can_tf, reason = TransformationSystem.can_transform(character, transformation)
        if not can_tf:
            return False, reason
        
        # Store original state
        original_species = getattr(character, 'species', 'human')
        original_features = {}
        
        for change in transformation.body_changes:
            feature_attr = f"has_{change.body_part}"
            if hasattr(character, feature_attr):
                original_features[change.body_part] = getattr(character, feature_attr)
        
        # Create active transformation
        active = ActiveTransformation(
            transformation=transformation,
            stage=TransformationStage.BEGINNING,
            original_species=original_species,
            original_features=original_features,
            started_at=datetime.now(),
        )
        
        # Set expiration
        duration_hours = transformation.get_duration_hours()
        if duration_hours > 0:
            active.expires_at = datetime.now() + timedelta(hours=duration_hours)
        
        # Start with some progress
        active.advance(25)
        
        character.active_transformation = active
        
        return True, transformation.begin_message
    
    @staticmethod
    def process_transformation(character) -> List[str]:
        """Process ongoing transformation. Returns messages."""
        if not hasattr(character, 'active_transformation'):
            return []
        
        active = character.active_transformation
        if not active:
            return []
        
        messages = []
        
        # Check expiration
        if active.is_expired and active.stage != TransformationStage.FADING:
            messages.append(active.begin_fade())
            character.active_transformation = active
        
        # Advance progress if not complete
        if active.stage in (TransformationStage.BEGINNING, TransformationStage.PROGRESSING):
            changed, msg = active.advance(random.randint(5, 15))
            if changed:
                messages.append(msg)
            
            # Apply body changes based on progress
            if active.progress >= 100:
                TransformationSystem._apply_changes(character, active)
            
            character.active_transformation = active
        
        # Handle fading
        elif active.stage == TransformationStage.FADING:
            active.progress -= 10
            
            if active.progress <= 0:
                TransformationSystem._revert_changes(character, active)
                active.stage = TransformationStage.REVERSED
                messages.append("The transformation has fully reverted.")
                character.active_transformation = None
            else:
                character.active_transformation = active
        
        return messages
    
    @staticmethod
    def _apply_changes(character, active: ActiveTransformation) -> None:
        """Apply the body changes from transformation."""
        for change in active.transformation.body_changes:
            # Set feature on character
            feature_attr = f"has_{change.body_part}"
            if hasattr(character, feature_attr):
                setattr(character, feature_attr, change.target_form)
        
        # Handle full species change
        if active.transformation.transformation_type == TransformationType.SPECIES:
            if active.transformation.target_species:
                character.species = active.transformation.target_species
    
    @staticmethod
    def _revert_changes(character, active: ActiveTransformation) -> None:
        """Revert body changes to original."""
        for change in active.transformation.body_changes:
            feature_attr = f"has_{change.body_part}"
            original = active.original_features.get(change.body_part)
            if hasattr(character, feature_attr):
                setattr(character, feature_attr, original)
        
        # Revert species
        if active.transformation.transformation_type == TransformationType.SPECIES:
            character.species = active.original_species
    
    @staticmethod
    def force_revert(character) -> str:
        """Force immediate reversion."""
        if not hasattr(character, 'active_transformation'):
            return "No transformation to revert."
        
        active = character.active_transformation
        if not active:
            return "No transformation to revert."
        
        TransformationSystem._revert_changes(character, active)
        character.active_transformation = None
        
        return "The transformation has been forcibly reversed."


# =============================================================================
# TRANSFORMATION MIXIN
# =============================================================================

class TransformableMixin:
    """
    Mixin for characters that can be transformed.
    """
    
    @property
    def active_transformation(self) -> Optional[ActiveTransformation]:
        """Get active transformation."""
        data = self.attributes.get("active_transformation")
        if data:
            return ActiveTransformation.from_dict(data)
        return None
    
    @active_transformation.setter
    def active_transformation(self, tf: Optional[ActiveTransformation]):
        """Set active transformation."""
        if tf:
            self.attributes.add("active_transformation", tf.to_dict())
        else:
            self.attributes.remove("active_transformation")
    
    def is_transformed(self) -> bool:
        """Check if currently transformed."""
        tf = self.active_transformation
        return tf is not None and tf.stage == TransformationStage.COMPLETE
    
    def get_transformation_desc(self) -> str:
        """Get description of current transformation."""
        tf = self.active_transformation
        if not tf:
            return ""
        
        if tf.stage == TransformationStage.COMPLETE:
            return f"Transformed: {tf.transformation.name} ({tf.remaining_hours}h remaining)"
        elif tf.stage in (TransformationStage.BEGINNING, TransformationStage.PROGRESSING):
            return f"Transforming: {tf.transformation.name} ({tf.progress}% complete)"
        elif tf.stage == TransformationStage.FADING:
            return f"Reverting: {tf.transformation.name} ({tf.progress}% remaining)"
        
        return ""


__all__ = [
    "TransformationType",
    "TransformationDuration",
    "TransformationStage",
    "BodyChange",
    "Transformation",
    "ActiveTransformation",
    "ALL_TRANSFORMATIONS",
    "POTION_TRANSFORMATION_MAP",
    "get_transformation",
    "TransformationSystem",
    "TransformableMixin",
]
