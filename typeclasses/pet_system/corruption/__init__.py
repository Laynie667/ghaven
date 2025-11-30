"""
Corruption & Transformation System
==================================

Progressive transformation paths including:
- Bimboification
- Cow-ification (hucow transformation)
- Sluttification
- Demonic corruption
- Each with stages and point-of-no-return mechanics
"""

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any, Tuple, Callable
from enum import Enum
from datetime import datetime
import random


# =============================================================================
# ENUMS
# =============================================================================

class TransformationType(Enum):
    """Types of transformations."""
    BIMBO = "bimbo"
    HUCOW = "hucow"
    SLUT = "slut"
    DEMON = "demon"
    DOLL = "doll"
    PET = "pet"
    BREEDING_SOW = "breeding_sow"
    FUTA = "futa"


class TransformationStage(Enum):
    """Stages of transformation."""
    UNTOUCHED = "untouched"       # No corruption
    TOUCHED = "touched"           # First signs
    PROGRESSING = "progressing"   # Noticeable changes
    ADVANCED = "advanced"         # Major changes
    NEAR_COMPLETE = "near_complete"  # Point of no return
    COMPLETE = "complete"         # Fully transformed
    PERFECTED = "perfected"       # Beyond complete


class CorruptionSource(Enum):
    """Sources of corruption."""
    CUM = "cum"                   # Demonic/monster seed
    MILK = "milk"                 # Corrupted milk
    MAGIC = "magic"               # Spells
    RITUAL = "ritual"             # Dark rituals
    ITEM = "item"                 # Cursed items
    CONTACT = "contact"           # Physical contact
    MENTAL = "mental"             # Mental corruption
    SUBSTANCE = "substance"       # Potions/drugs


# =============================================================================
# BASE TRANSFORMATION
# =============================================================================

@dataclass
class TransformationProgress:
    """Base transformation tracking."""
    
    transform_type: TransformationType = TransformationType.BIMBO
    
    # Progress
    progress: int = 0             # 0-100
    stage: TransformationStage = TransformationStage.UNTOUCHED
    
    # Point of no return
    point_of_no_return: int = 75  # Progress level where reversal impossible
    is_reversible: bool = True
    
    # Rate
    base_rate: float = 1.0        # Multiplier for progress gain
    resistance: int = 50          # 0-100, reduces progress gain
    
    # Effects
    active_effects: Dict[str, int] = field(default_factory=dict)
    
    # History
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    sources: List[CorruptionSource] = field(default_factory=list)
    
    def add_progress(self, amount: int, source: CorruptionSource = CorruptionSource.MAGIC) -> Tuple[str, bool]:
        """
        Add transformation progress.
        Returns (message, stage_changed).
        """
        if not self.started_at:
            self.started_at = datetime.now()
        
        if source not in self.sources:
            self.sources.append(source)
        
        # Apply resistance
        actual = int(amount * self.base_rate * (1 - self.resistance / 200))
        actual = max(1, actual)  # Always at least 1
        
        old_progress = self.progress
        self.progress = min(100, self.progress + actual)
        
        # Check point of no return
        if old_progress < self.point_of_no_return <= self.progress:
            self.is_reversible = False
        
        # Update stage
        old_stage = self.stage
        self._update_stage()
        
        stage_changed = old_stage != self.stage
        
        if self.progress >= 100 and not self.completed_at:
            self.completed_at = datetime.now()
        
        return f"Progress: {self.progress}/100", stage_changed
    
    def _update_stage(self) -> None:
        """Update stage based on progress."""
        if self.progress >= 100:
            self.stage = TransformationStage.COMPLETE
        elif self.progress >= 80:
            self.stage = TransformationStage.NEAR_COMPLETE
        elif self.progress >= 60:
            self.stage = TransformationStage.ADVANCED
        elif self.progress >= 40:
            self.stage = TransformationStage.PROGRESSING
        elif self.progress >= 20:
            self.stage = TransformationStage.TOUCHED
        else:
            self.stage = TransformationStage.UNTOUCHED
    
    def attempt_reversal(self, power: int = 50) -> Tuple[bool, str]:
        """Attempt to reverse transformation."""
        if not self.is_reversible:
            return False, "Transformation has passed the point of no return."
        
        if self.progress == 0:
            return True, "Nothing to reverse."
        
        reduction = int(power * (1 - self.progress / 200))
        self.progress = max(0, self.progress - reduction)
        self._update_stage()
        
        return True, f"Progress reduced to {self.progress}/100"


# =============================================================================
# BIMBOIFICATION
# =============================================================================

@dataclass
class BimboTransformation(TransformationProgress):
    """Bimboification transformation."""
    
    transform_type: TransformationType = field(default=TransformationType.BIMBO)
    
    # Bimbo-specific stats
    intelligence_drain: int = 0   # How much INT lost
    original_intelligence: int = 100
    current_intelligence: int = 100
    
    breast_growth: int = 0        # CC added
    lip_plumpness: int = 0        # 0-100
    ass_growth: int = 0           # Size increase
    
    libido_increase: int = 0      # Added libido
    attention_span: int = 100     # Decreases
    vocabulary_reduction: int = 0 # Simpler words
    
    # Behavioral changes
    giggliness: int = 0           # 0-100
    obedience: int = 0            # 0-100
    vanity: int = 0               # 0-100
    cock_fixation: int = 0        # 0-100
    
    def apply_stage_effects(self) -> str:
        """Apply effects based on current stage."""
        effects = []
        
        if self.stage == TransformationStage.TOUCHED:
            self.intelligence_drain = 10
            self.breast_growth = 50
            self.lip_plumpness = 10
            self.giggliness = 20
            effects.append("Thoughts occasionally scatter. Lips feel fuller.")
            
        elif self.stage == TransformationStage.PROGRESSING:
            self.intelligence_drain = 25
            self.breast_growth = 150
            self.lip_plumpness = 30
            self.ass_growth = 20
            self.libido_increase = 30
            self.giggliness = 40
            self.attention_span = 70
            effects.append("Hard to focus. Breasts swelling noticeably. Everything seems funnier.")
            
        elif self.stage == TransformationStage.ADVANCED:
            self.intelligence_drain = 50
            self.breast_growth = 400
            self.lip_plumpness = 60
            self.ass_growth = 50
            self.libido_increase = 60
            self.giggliness = 70
            self.attention_span = 40
            self.vocabulary_reduction = 40
            self.obedience = 50
            self.cock_fixation = 50
            effects.append("Big words are, like, hard? Boobies are getting SO big! Boys are yummy...")
            
        elif self.stage == TransformationStage.NEAR_COMPLETE:
            self.intelligence_drain = 75
            self.breast_growth = 800
            self.lip_plumpness = 80
            self.ass_growth = 80
            self.libido_increase = 80
            self.giggliness = 90
            self.attention_span = 20
            self.vocabulary_reduction = 70
            self.obedience = 80
            self.cock_fixation = 80
            self.vanity = 70
            effects.append("*giggle* What was I... ooh, shiny! Mmm, need cock so bad...")
            
        elif self.stage == TransformationStage.COMPLETE:
            self.intelligence_drain = 90
            self.breast_growth = 1200
            self.lip_plumpness = 100
            self.ass_growth = 100
            self.libido_increase = 100
            self.giggliness = 100
            self.attention_span = 5
            self.vocabulary_reduction = 90
            self.obedience = 100
            self.cock_fixation = 100
            self.vanity = 100
            effects.append("*gigglegiggle* Bimbo love cock! Bimbo pretty! Bimbo fuck now? Pleeeease?")
        
        self.current_intelligence = max(10, self.original_intelligence - self.intelligence_drain)
        
        self.active_effects = {
            "intelligence": -self.intelligence_drain,
            "breast_size": self.breast_growth,
            "libido": self.libido_increase,
            "obedience": self.obedience,
        }
        
        return "\n".join(effects)
    
    def get_speech_filter(self, text: str) -> str:
        """Filter speech through bimbo vocabulary."""
        if self.vocabulary_reduction < 30:
            return text
        
        # Simple word replacements
        replacements = {
            "think": "like, think",
            "want": "totally want",
            "good": "sooo good",
            "yes": "like, yes!",
            "no": "nuh-uh",
            "please": "pleeeease",
            "hello": "hiii!",
            "I": "like, I",
        }
        
        result = text.lower()
        for old, new in replacements.items():
            result = result.replace(old, new)
        
        # Add giggles
        if self.giggliness > 50 and random.random() < self.giggliness / 100:
            result = "*giggle* " + result
        
        return result
    
    def get_status(self) -> str:
        """Get bimbo transformation status."""
        lines = [f"=== Bimboification: {self.stage.value.upper()} ==="]
        lines.append(f"Progress: {self.progress}/100 {'(IRREVERSIBLE)' if not self.is_reversible else ''}")
        
        lines.append(f"\n--- Mental Changes ---")
        lines.append(f"Intelligence: {self.current_intelligence}/100 (-{self.intelligence_drain})")
        lines.append(f"Attention Span: {self.attention_span}/100")
        lines.append(f"Vocabulary: {100 - self.vocabulary_reduction}/100")
        
        lines.append(f"\n--- Physical Changes ---")
        lines.append(f"Breast Growth: +{self.breast_growth}cc")
        lines.append(f"Lip Plumpness: {self.lip_plumpness}/100")
        lines.append(f"Ass Growth: +{self.ass_growth}%")
        
        lines.append(f"\n--- Behavioral ---")
        lines.append(f"Giggliness: {self.giggliness}/100")
        lines.append(f"Obedience: {self.obedience}/100")
        lines.append(f"Cock Fixation: {self.cock_fixation}/100")
        lines.append(f"Libido: +{self.libido_increase}")
        
        return "\n".join(lines)


# =============================================================================
# HUCOW TRANSFORMATION
# =============================================================================

@dataclass
class HucowTransformation(TransformationProgress):
    """Cow-ification transformation."""
    
    transform_type: TransformationType = field(default=TransformationType.HUCOW)
    
    # Physical changes
    breast_growth: int = 0        # CC added
    nipple_enlargement: int = 0   # Size increase
    areola_growth: int = 0        # Size increase
    hip_widening: int = 0         # For calving
    
    # Lactation
    lactation_capacity: int = 0   # ml capacity
    milk_production_rate: int = 0 # ml per hour
    letdown_sensitivity: int = 0  # Easier milk letdown
    
    # Cow features
    ear_changes: int = 0          # Becoming bovine
    tail_growth: int = 0          # Cow tail
    horn_buds: int = 0            # Small horns
    nose_ring_sensitivity: int = 0
    hide_patches: int = 0         # Cow-print patches
    
    # Mental changes
    docility: int = 0             # 0-100
    herd_mentality: int = 0       # Following others
    breeding_drive: int = 0       # Need to be bred
    grazing_urges: int = 0        # Want to eat grass
    mooing_tendency: int = 0      # Replacing speech
    
    def apply_stage_effects(self) -> str:
        """Apply effects based on current stage."""
        effects = []
        
        if self.stage == TransformationStage.TOUCHED:
            self.breast_growth = 100
            self.nipple_enlargement = 10
            self.lactation_capacity = 100
            self.docility = 10
            effects.append("Breasts feel tender and swollen. A strange calm settles.")
            
        elif self.stage == TransformationStage.PROGRESSING:
            self.breast_growth = 300
            self.nipple_enlargement = 30
            self.areola_growth = 20
            self.lactation_capacity = 300
            self.milk_production_rate = 10
            self.docility = 30
            self.ear_changes = 20
            self.breeding_drive = 20
            effects.append("Nipples darkening and enlarging. Milk beginning to form. Ears feel... different.")
            
        elif self.stage == TransformationStage.ADVANCED:
            self.breast_growth = 600
            self.nipple_enlargement = 60
            self.areola_growth = 50
            self.hip_widening = 30
            self.lactation_capacity = 600
            self.milk_production_rate = 30
            self.letdown_sensitivity = 50
            self.docility = 60
            self.ear_changes = 50
            self.tail_growth = 30
            self.breeding_drive = 50
            self.herd_mentality = 40
            self.mooing_tendency = 20
            effects.append("Udders heavy with milk. Tail sprouting. The barn feels like home. Mooo...")
            
        elif self.stage == TransformationStage.NEAR_COMPLETE:
            self.breast_growth = 1000
            self.nipple_enlargement = 80
            self.areola_growth = 70
            self.hip_widening = 60
            self.lactation_capacity = 1000
            self.milk_production_rate = 50
            self.letdown_sensitivity = 80
            self.docility = 80
            self.ear_changes = 80
            self.tail_growth = 70
            self.horn_buds = 30
            self.hide_patches = 40
            self.breeding_drive = 80
            self.herd_mentality = 70
            self.grazing_urges = 50
            self.mooing_tendency = 60
            effects.append("Massive udders need milking constantly. Cow ears and tail. Need... breeding... mooooo!")
            
        elif self.stage == TransformationStage.COMPLETE:
            self.breast_growth = 1500
            self.nipple_enlargement = 100
            self.areola_growth = 100
            self.hip_widening = 100
            self.lactation_capacity = 2000
            self.milk_production_rate = 80
            self.letdown_sensitivity = 100
            self.docility = 100
            self.ear_changes = 100
            self.tail_growth = 100
            self.horn_buds = 60
            self.hide_patches = 70
            self.breeding_drive = 100
            self.herd_mentality = 100
            self.grazing_urges = 80
            self.mooing_tendency = 100
            self.nose_ring_sensitivity = 100
            effects.append("Moooo! *dripping milk* Need milking! Need breeding! Good cow. Happy cow. Mooooo~")
        
        self.active_effects = {
            "breast_size": self.breast_growth,
            "milk_capacity": self.lactation_capacity,
            "production_rate": self.milk_production_rate,
            "docility": self.docility,
        }
        
        return "\n".join(effects)
    
    def get_status(self) -> str:
        """Get hucow transformation status."""
        lines = [f"=== Cow-ification: {self.stage.value.upper()} ==="]
        lines.append(f"Progress: {self.progress}/100 {'(IRREVERSIBLE)' if not self.is_reversible else ''}")
        
        lines.append(f"\n--- Udder Development ---")
        lines.append(f"Breast Growth: +{self.breast_growth}cc")
        lines.append(f"Nipple Size: +{self.nipple_enlargement}%")
        lines.append(f"Milk Capacity: {self.lactation_capacity}ml")
        lines.append(f"Production: {self.milk_production_rate}ml/hour")
        
        lines.append(f"\n--- Bovine Features ---")
        lines.append(f"Cow Ears: {self.ear_changes}%")
        lines.append(f"Tail: {self.tail_growth}%")
        lines.append(f"Horns: {self.horn_buds}%")
        lines.append(f"Hide Patches: {self.hide_patches}%")
        
        lines.append(f"\n--- Mental Changes ---")
        lines.append(f"Docility: {self.docility}/100")
        lines.append(f"Breeding Drive: {self.breeding_drive}/100")
        lines.append(f"Herd Mentality: {self.herd_mentality}/100")
        lines.append(f"Mooing: {self.mooing_tendency}%")
        
        return "\n".join(lines)


# =============================================================================
# SLUTTIFICATION
# =============================================================================

@dataclass
class SlutTransformation(TransformationProgress):
    """Sluttification transformation."""
    
    transform_type: TransformationType = field(default=TransformationType.SLUT)
    
    # Arousal changes
    base_arousal: int = 0         # Minimum arousal level
    arousal_rate: int = 0         # How fast arousal builds
    orgasm_threshold: int = 100   # Decreases - easier to cum
    
    # Shame erosion
    original_shame: int = 100
    current_shame: int = 100      # Decreases
    shame_resistance: int = 0     # Immunity to embarrassment
    
    # Physical sensitivity
    nipple_sensitivity: int = 50
    clit_sensitivity: int = 50
    skin_sensitivity: int = 50
    erogenous_expansion: int = 0  # More of body becomes sensitive
    
    # Mental changes
    cock_craving: int = 0         # Need for penetration
    cum_addiction: int = 0        # Need for cum
    exhibitionism: int = 0        # Enjoyment of being seen
    submission_tendency: int = 0  # Natural submission
    degradation_enjoyment: int = 0  # Getting off on humiliation
    
    # Behavioral
    flirtatiousness: int = 0
    clothing_preference: int = 100  # Decreases - prefers less
    public_display: int = 0       # Willingness to be lewd in public
    
    def apply_stage_effects(self) -> str:
        """Apply effects based on current stage."""
        effects = []
        
        if self.stage == TransformationStage.TOUCHED:
            self.base_arousal = 10
            self.current_shame = 90
            self.nipple_sensitivity = 60
            self.flirtatiousness = 20
            effects.append("A persistent warmth between the legs. Flirting comes easier.")
            
        elif self.stage == TransformationStage.PROGRESSING:
            self.base_arousal = 25
            self.arousal_rate = 20
            self.orgasm_threshold = 80
            self.current_shame = 70
            self.nipple_sensitivity = 75
            self.clit_sensitivity = 70
            self.cock_craving = 30
            self.flirtatiousness = 40
            self.clothing_preference = 80
            effects.append("Constantly thinking about sex. Tight clothes feel restricting. Eyes wander to crotches.")
            
        elif self.stage == TransformationStage.ADVANCED:
            self.base_arousal = 40
            self.arousal_rate = 40
            self.orgasm_threshold = 60
            self.current_shame = 40
            self.shame_resistance = 30
            self.nipple_sensitivity = 90
            self.clit_sensitivity = 85
            self.erogenous_expansion = 30
            self.cock_craving = 60
            self.cum_addiction = 40
            self.exhibitionism = 40
            self.submission_tendency = 40
            self.flirtatiousness = 70
            self.clothing_preference = 50
            self.public_display = 30
            effects.append("Can't stop touching yourself. Love the way people look. Need to be filled...")
            
        elif self.stage == TransformationStage.NEAR_COMPLETE:
            self.base_arousal = 60
            self.arousal_rate = 70
            self.orgasm_threshold = 40
            self.current_shame = 15
            self.shame_resistance = 70
            self.nipple_sensitivity = 100
            self.clit_sensitivity = 100
            self.erogenous_expansion = 60
            self.cock_craving = 85
            self.cum_addiction = 70
            self.exhibitionism = 70
            self.submission_tendency = 70
            self.degradation_enjoyment = 50
            self.flirtatiousness = 90
            self.clothing_preference = 20
            self.public_display = 60
            effects.append("Always wet. Always ready. Being called a slut feels SO good. Need cock. Need cum. Need to be USED.")
            
        elif self.stage == TransformationStage.COMPLETE:
            self.base_arousal = 80
            self.arousal_rate = 100
            self.orgasm_threshold = 20
            self.current_shame = 0
            self.shame_resistance = 100
            self.nipple_sensitivity = 100
            self.clit_sensitivity = 100
            self.skin_sensitivity = 100
            self.erogenous_expansion = 100
            self.cock_craving = 100
            self.cum_addiction = 100
            self.exhibitionism = 100
            self.submission_tendency = 100
            self.degradation_enjoyment = 100
            self.flirtatiousness = 100
            self.clothing_preference = 0
            self.public_display = 100
            effects.append("I am a slut. I exist to be fucked. Any hole, anywhere, anyone. Please use me. I need it. I NEED IT.")
        
        self.active_effects = {
            "arousal_min": self.base_arousal,
            "shame": -self.current_shame,
            "sensitivity": self.nipple_sensitivity,
            "cock_craving": self.cock_craving,
        }
        
        return "\n".join(effects)
    
    def get_status(self) -> str:
        """Get slut transformation status."""
        lines = [f"=== Sluttification: {self.stage.value.upper()} ==="]
        lines.append(f"Progress: {self.progress}/100 {'(IRREVERSIBLE)' if not self.is_reversible else ''}")
        
        lines.append(f"\n--- Arousal Changes ---")
        lines.append(f"Base Arousal: {self.base_arousal}/100")
        lines.append(f"Arousal Rate: +{self.arousal_rate}%")
        lines.append(f"Orgasm Threshold: {self.orgasm_threshold}/100")
        
        lines.append(f"\n--- Shame Erosion ---")
        lines.append(f"Shame: {self.current_shame}/100")
        lines.append(f"Shame Resistance: {self.shame_resistance}%")
        
        lines.append(f"\n--- Sensitivity ---")
        lines.append(f"Nipples: {self.nipple_sensitivity}/100")
        lines.append(f"Clit: {self.clit_sensitivity}/100")
        lines.append(f"Erogenous Expansion: {self.erogenous_expansion}%")
        
        lines.append(f"\n--- Mental Changes ---")
        lines.append(f"Cock Craving: {self.cock_craving}/100")
        lines.append(f"Cum Addiction: {self.cum_addiction}/100")
        lines.append(f"Exhibitionism: {self.exhibitionism}/100")
        lines.append(f"Degradation Enjoyment: {self.degradation_enjoyment}/100")
        
        return "\n".join(lines)


# =============================================================================
# DEMONIC CORRUPTION
# =============================================================================

@dataclass
class DemonTransformation(TransformationProgress):
    """Demonic corruption transformation."""
    
    transform_type: TransformationType = field(default=TransformationType.DEMON)
    
    # Corruption spread
    corruption_marks: int = 0     # Visible marks
    mark_spread: int = 0          # How much body covered
    mark_glow: int = 0            # Intensity of glow
    
    # Physical changes
    horn_growth: int = 0          # 0-100
    tail_growth: int = 0          # Demon tail
    wing_buds: int = 0            # Small wings
    eye_change: int = 0           # Demonic eyes
    skin_tint: int = 0            # Color change
    fang_growth: int = 0          # Fangs
    claw_growth: int = 0          # Claws
    
    # Demonic features
    heat_resistance: int = 0
    dark_vision: int = 0
    pheromone_production: int = 0 # Seductive aura
    life_drain_ability: int = 0   # Drain through sex
    
    # Mental changes
    cruelty: int = 0              # Sadistic tendencies
    lust_intensity: int = 0       # Overwhelming lust
    soul_hunger: int = 0          # Need to corrupt others
    demonic_thoughts: int = 0     # Alien thought patterns
    morality_erosion: int = 0     # Loss of moral compass
    
    # Powers
    seduction_power: int = 0
    corruption_touch: int = 0     # Can corrupt others
    demonic_strength: int = 0
    
    def apply_stage_effects(self) -> str:
        """Apply effects based on current stage."""
        effects = []
        
        if self.stage == TransformationStage.TOUCHED:
            self.corruption_marks = 10
            self.mark_spread = 5
            self.lust_intensity = 20
            self.eye_change = 10
            effects.append("Strange marks appear on skin. Eyes flash red in dim light. Dark urges whisper.")
            
        elif self.stage == TransformationStage.PROGRESSING:
            self.corruption_marks = 30
            self.mark_spread = 20
            self.mark_glow = 10
            self.horn_growth = 20
            self.tail_growth = 20
            self.eye_change = 40
            self.lust_intensity = 40
            self.cruelty = 30
            self.pheromone_production = 30
            effects.append("Marks spread and pulse. Small horn nubs form. Tail emerging. Others seem... drawn to you.")
            
        elif self.stage == TransformationStage.ADVANCED:
            self.corruption_marks = 60
            self.mark_spread = 50
            self.mark_glow = 40
            self.horn_growth = 50
            self.tail_growth = 60
            self.wing_buds = 30
            self.eye_change = 70
            self.skin_tint = 40
            self.fang_growth = 50
            self.lust_intensity = 70
            self.cruelty = 60
            self.soul_hunger = 50
            self.pheromone_production = 60
            self.seduction_power = 50
            self.morality_erosion = 50
            effects.append("Horns curve elegantly. Tail prehensile. Skin taking demonic hue. The hunger for souls grows...")
            
        elif self.stage == TransformationStage.NEAR_COMPLETE:
            self.corruption_marks = 80
            self.mark_spread = 80
            self.mark_glow = 70
            self.horn_growth = 80
            self.tail_growth = 90
            self.wing_buds = 60
            self.eye_change = 90
            self.skin_tint = 70
            self.fang_growth = 80
            self.claw_growth = 50
            self.lust_intensity = 90
            self.cruelty = 80
            self.soul_hunger = 80
            self.demonic_thoughts = 70
            self.pheromone_production = 80
            self.seduction_power = 80
            self.corruption_touch = 50
            self.morality_erosion = 80
            self.dark_vision = 60
            effects.append("Wings strain against skin. Mortals kneel before your presence. Their souls smell... delicious.")
            
        elif self.stage == TransformationStage.COMPLETE:
            self.corruption_marks = 100
            self.mark_spread = 100
            self.mark_glow = 100
            self.horn_growth = 100
            self.tail_growth = 100
            self.wing_buds = 100
            self.eye_change = 100
            self.skin_tint = 100
            self.fang_growth = 100
            self.claw_growth = 80
            self.heat_resistance = 100
            self.dark_vision = 100
            self.lust_intensity = 100
            self.cruelty = 100
            self.soul_hunger = 100
            self.demonic_thoughts = 100
            self.pheromone_production = 100
            self.seduction_power = 100
            self.corruption_touch = 100
            self.life_drain_ability = 80
            self.demonic_strength = 60
            self.morality_erosion = 100
            effects.append("Ascension complete. Demon in full. Mortals exist to serve, to corrupt, to consume. Their pleasure feeds your power.")
        
        self.active_effects = {
            "horn_size": self.horn_growth,
            "seduction": self.seduction_power,
            "corruption_aura": self.corruption_touch,
            "demonic_power": self.demonic_strength,
        }
        
        return "\n".join(effects)
    
    def get_status(self) -> str:
        """Get demon transformation status."""
        lines = [f"=== Demonic Corruption: {self.stage.value.upper()} ==="]
        lines.append(f"Progress: {self.progress}/100 {'(IRREVERSIBLE)' if not self.is_reversible else ''}")
        
        lines.append(f"\n--- Corruption Marks ---")
        lines.append(f"Mark Intensity: {self.corruption_marks}/100")
        lines.append(f"Body Coverage: {self.mark_spread}%")
        lines.append(f"Glow: {self.mark_glow}/100")
        
        lines.append(f"\n--- Physical Changes ---")
        lines.append(f"Horns: {self.horn_growth}%")
        lines.append(f"Tail: {self.tail_growth}%")
        lines.append(f"Wings: {self.wing_buds}%")
        lines.append(f"Eyes: {self.eye_change}% demonic")
        lines.append(f"Skin Tint: {self.skin_tint}%")
        
        lines.append(f"\n--- Demonic Powers ---")
        lines.append(f"Seduction Aura: {self.seduction_power}/100")
        lines.append(f"Corruption Touch: {self.corruption_touch}/100")
        lines.append(f"Pheromones: {self.pheromone_production}/100")
        
        lines.append(f"\n--- Mental Changes ---")
        lines.append(f"Lust: {self.lust_intensity}/100")
        lines.append(f"Cruelty: {self.cruelty}/100")
        lines.append(f"Soul Hunger: {self.soul_hunger}/100")
        lines.append(f"Morality Erosion: {self.morality_erosion}%")
        
        return "\n".join(lines)


# =============================================================================
# TRANSFORMATION MANAGER
# =============================================================================

@dataclass
class TransformationManager:
    """Manages all transformations for a character."""
    
    subject_dbref: str = ""
    subject_name: str = ""
    
    # Active transformations
    transformations: Dict[TransformationType, TransformationProgress] = field(default_factory=dict)
    
    # Susceptibility
    transformation_resistance: int = 50  # General resistance
    specific_resistances: Dict[TransformationType, int] = field(default_factory=dict)
    
    # History
    completed_transformations: List[TransformationType] = field(default_factory=list)
    
    def start_transformation(self, transform_type: TransformationType) -> str:
        """Start a new transformation."""
        if transform_type in self.transformations:
            return "Already undergoing this transformation."
        
        # Create appropriate transformation
        if transform_type == TransformationType.BIMBO:
            trans = BimboTransformation()
        elif transform_type == TransformationType.HUCOW:
            trans = HucowTransformation()
        elif transform_type == TransformationType.SLUT:
            trans = SlutTransformation()
        elif transform_type == TransformationType.DEMON:
            trans = DemonTransformation()
        else:
            trans = TransformationProgress(transform_type=transform_type)
        
        # Apply resistance
        trans.resistance = self.specific_resistances.get(
            transform_type, self.transformation_resistance
        )
        
        self.transformations[transform_type] = trans
        
        return f"{transform_type.value.title()} transformation begun."
    
    def progress_transformation(
        self,
        transform_type: TransformationType,
        amount: int,
        source: CorruptionSource = CorruptionSource.MAGIC,
    ) -> Tuple[str, Optional[str]]:
        """
        Progress a transformation.
        Returns (progress_msg, stage_change_msg if stage changed).
        """
        if transform_type not in self.transformations:
            self.start_transformation(transform_type)
        
        trans = self.transformations[transform_type]
        
        msg, stage_changed = trans.add_progress(amount, source)
        
        stage_msg = None
        if stage_changed:
            # Apply stage effects
            if hasattr(trans, 'apply_stage_effects'):
                stage_msg = trans.apply_stage_effects()
            
            # Check for completion
            if trans.stage == TransformationStage.COMPLETE:
                if transform_type not in self.completed_transformations:
                    self.completed_transformations.append(transform_type)
        
        return msg, stage_msg
    
    def get_transformation(self, transform_type: TransformationType) -> Optional[TransformationProgress]:
        """Get a specific transformation."""
        return self.transformations.get(transform_type)
    
    def get_all_active(self) -> List[TransformationProgress]:
        """Get all active transformations."""
        return list(self.transformations.values())
    
    def get_summary(self) -> str:
        """Get transformation summary."""
        lines = [f"=== Transformations: {self.subject_name} ==="]
        lines.append(f"Base Resistance: {self.transformation_resistance}/100")
        
        if not self.transformations:
            lines.append("\nNo active transformations.")
        else:
            for trans_type, trans in self.transformations.items():
                reversible = "✓" if trans.is_reversible else "✗"
                lines.append(f"\n{trans_type.value.upper()}: {trans.progress}% [{trans.stage.value}] Rev:{reversible}")
        
        if self.completed_transformations:
            lines.append(f"\nCompleted: {', '.join(t.value for t in self.completed_transformations)}")
        
        return "\n".join(lines)
    
    def to_dict(self) -> dict:
        transformations_data = {}
        for t_type, trans in self.transformations.items():
            transformations_data[t_type.value] = {
                "progress": trans.progress,
                "stage": trans.stage.value,
                "is_reversible": trans.is_reversible,
            }
        
        return {
            "subject_dbref": self.subject_dbref,
            "subject_name": self.subject_name,
            "transformations": transformations_data,
            "transformation_resistance": self.transformation_resistance,
            "completed": [t.value for t in self.completed_transformations],
        }


# =============================================================================
# TRANSFORMATION MIXIN
# =============================================================================

class TransformationMixin:
    """Mixin for characters that can be transformed."""
    
    @property
    def transformations(self) -> TransformationManager:
        """Get transformation manager."""
        data = self.db.transformations
        if data:
            mgr = TransformationManager()
            mgr.subject_dbref = data.get("subject_dbref", self.dbref)
            mgr.subject_name = data.get("subject_name", self.key)
            mgr.transformation_resistance = data.get("transformation_resistance", 50)
            # Would need to reconstruct transformations from saved data
            return mgr
        return TransformationManager(subject_dbref=self.dbref, subject_name=self.key)
    
    @transformations.setter
    def transformations(self, mgr: TransformationManager) -> None:
        """Set transformation manager."""
        self.db.transformations = mgr.to_dict()


__all__ = [
    "TransformationType",
    "TransformationStage",
    "CorruptionSource",
    "TransformationProgress",
    "BimboTransformation",
    "HucowTransformation",
    "SlutTransformation",
    "DemonTransformation",
    "TransformationManager",
    "TransformationMixin",
    "CorruptionCmdSet",
]

# Import commands
from .commands import CorruptionCmdSet
