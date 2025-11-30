"""
Body Description Generator

Generates dynamic, state-aware descriptions of bodies and body parts.
Considers:
- Base part definitions
- Current arousal state
- Injuries/conditions
- Covering (clothing)
- Species customizations
- Presentation (marks, fluids)
"""

from typing import Optional, List, Dict, TYPE_CHECKING
from enum import Enum

from .parts_sexual import (
    ArousalState,
    OrificeState,
    KnotState,
    get_sexual_part,
    SEXUAL_PART_REGISTRY,
)
from .parts import get_part, PART_REGISTRY
from .species import get_species
from .structures import get_structure

if TYPE_CHECKING:
    from .body import Body
    from .states import SexualStateManager


class DescriptionMode(Enum):
    """How detailed/explicit the description should be."""
    CLINICAL = "clinical"      # Medical/technical terms
    CASUAL = "casual"          # Normal everyday language
    EROTIC = "erotic"          # Explicit, sexy language
    POETIC = "poetic"          # Flowery, metaphorical
    BRIEF = "brief"            # Just the essentials


class DescriptionPerspective(Enum):
    """Who is viewing/describing."""
    FIRST = "first"            # "You have..."
    SECOND = "second"          # "You see..."
    THIRD = "third"            # "She has..."


# =============================================================================
# DESCRIPTION TEMPLATES
# =============================================================================

# Arousal descriptions by mode
AROUSAL_DESCRIPTIONS = {
    DescriptionMode.EROTIC: {
        ArousalState.SOFT: "soft and relaxed",
        ArousalState.CHUBBED: "starting to swell with interest",
        ArousalState.HALF: "growing harder, filling with blood",
        ArousalState.HARD: "rock hard and eager",
        ArousalState.THROBBING: "throbbing desperately, aching for release",
    },
    DescriptionMode.CASUAL: {
        ArousalState.SOFT: "soft",
        ArousalState.CHUBBED: "slightly aroused",
        ArousalState.HALF: "semi-erect",
        ArousalState.HARD: "erect",
        ArousalState.THROBBING: "very aroused",
    },
    DescriptionMode.CLINICAL: {
        ArousalState.SOFT: "flaccid",
        ArousalState.CHUBBED: "tumescent",
        ArousalState.HALF: "partially erect",
        ArousalState.HARD: "fully erect",
        ArousalState.THROBBING: "maximally engorged",
    },
}

# Wetness descriptions
WETNESS_DESCRIPTIONS = {
    DescriptionMode.EROTIC: {
        0.0: "dry",
        0.2: "slightly damp",
        0.4: "wet and ready",
        0.6: "dripping with arousal",
        0.8: "absolutely soaked, juices running down",
        1.0: "gushing, a puddle forming beneath",
    },
    DescriptionMode.CASUAL: {
        0.0: "dry",
        0.3: "damp",
        0.5: "wet",
        0.7: "very wet",
        1.0: "soaking wet",
    },
}

# Size descriptions
SIZE_WORDS = {
    "tiny": ["tiny", "minuscule", "itty-bitty"],
    "small": ["small", "petite", "modest"],
    "average": ["average", "normal-sized", "typical"],
    "large": ["large", "big", "sizeable"],
    "huge": ["huge", "massive", "enormous"],
    "massive": ["massive", "gigantic", "monstrous"],
}

# Cock type flavor
COCK_TYPE_DESCRIPTIONS = {
    "cock_human": "human cock",
    "cock_canine": "tapered canine cock with a knot at the base",
    "cock_equine": "massive flared horse cock",
    "cock_feline": "barbed feline cock",
    "cock_reptile": "ridged reptilian cock",
    "cock_dolphin": "prehensile dolphin cock",
    "cock_tentacle": "writhing tentacle cock",
    "hemipenes": "twin hemipenes",
}


# =============================================================================
# MAIN DESCRIPTION GENERATOR
# =============================================================================

class BodyDescriber:
    """
    Generates descriptions of bodies and parts.
    """
    
    def __init__(
        self,
        mode: DescriptionMode = DescriptionMode.EROTIC,
        perspective: DescriptionPerspective = DescriptionPerspective.SECOND,
    ):
        self.mode = mode
        self.perspective = perspective
    
    def describe_full_body(
        self,
        body: "Body",
        sexual_states: Optional["SexualStateManager"] = None,
        include_covered: bool = False,
        include_sexual: bool = True,
        observer: Optional[str] = None,
    ) -> str:
        """
        Generate a full body description.
        
        Args:
            body: The body to describe
            sexual_states: Sexual state manager (for arousal, etc.)
            include_covered: Include parts that are covered by clothing
            include_sexual: Include sexual parts
            observer: Who is looking (for perspective)
        
        Returns:
            Multi-line description string
        """
        lines = []
        
        # Get species info
        spec = get_species(body.species_key)
        struct = get_structure(body.structure_key)
        
        # Opening line
        subject = self._get_subject(body, observer)
        if spec:
            lines.append(f"{subject} is a {spec.name.lower()}.")
            if spec.covering_description:
                lines.append(spec.covering_description)
        
        # Structure description
        if struct:
            lines.append(self._describe_structure(struct.key))
        
        # Notable features
        notable = []
        
        # Head/face
        head_desc = self._describe_region(body, "head", sexual_states, include_covered)
        if head_desc:
            notable.append(head_desc)
        
        # Torso
        torso_desc = self._describe_region(body, "torso", sexual_states, include_covered)
        if torso_desc:
            notable.append(torso_desc)
        
        # Sexual parts (if showing)
        if include_sexual:
            sexual_desc = self._describe_sexual_parts(body, sexual_states, include_covered)
            if sexual_desc:
                notable.append(sexual_desc)
        
        # Limbs
        limb_desc = self._describe_limbs(body, sexual_states)
        if limb_desc:
            notable.append(limb_desc)
        
        # Special features (tail, wings, etc.)
        special_desc = self._describe_special_features(body)
        if special_desc:
            notable.append(special_desc)
        
        # Combine
        if notable:
            lines.extend(notable)
        
        # Presentation (marks, fluids)
        if body.presentation:
            pres_desc = self._describe_presentation(body)
            if pres_desc:
                lines.append(pres_desc)
        
        return "\n".join(lines)
    
    def describe_part(
        self,
        body: "Body",
        part_key: str,
        sexual_states: Optional["SexualStateManager"] = None,
    ) -> str:
        """
        Describe a single body part.
        
        Args:
            body: The body
            part_key: Which part to describe
            sexual_states: Sexual states for dynamic info
        
        Returns:
            Description string
        """
        if part_key not in body.parts:
            return f"No {part_key} present."
        
        part_instance = body.parts[part_key]
        
        # Check if it's a sexual part
        sex_part = get_sexual_part(part_key)
        if sex_part:
            return self._describe_sexual_part(part_key, body, sexual_states)
        
        # Regular part
        part_def = get_part(part_key)
        if not part_def:
            return part_instance.custom_desc or f"A {part_key}."
        
        desc = part_instance.custom_desc or part_def.default_desc or f"A {part_def.name}."
        
        # Add state modifiers
        if part_instance.state.value != "normal":
            desc += f" It is {part_instance.state.value}."
        
        if part_instance.injury_level > 0:
            desc += f" {part_instance.injury_desc}"
        
        return desc
    
    def describe_genitals(
        self,
        body: "Body",
        sexual_states: Optional["SexualStateManager"] = None,
    ) -> str:
        """
        Describe just the genital region.
        """
        return self._describe_sexual_parts(body, sexual_states, include_covered=False)
    
    # =========================================================================
    # INTERNAL METHODS
    # =========================================================================
    
    def _get_subject(self, body: "Body", observer: Optional[str]) -> str:
        """Get the subject pronoun/name based on perspective."""
        if self.perspective == DescriptionPerspective.FIRST:
            return "You"
        elif self.perspective == DescriptionPerspective.SECOND:
            # Would use body's name if available
            return "They"
        else:
            return "They"
    
    def _describe_structure(self, structure_key: str) -> str:
        """Describe the body structure."""
        descriptions = {
            "bipedal_plantigrade": "They stand upright on two legs.",
            "bipedal_digitigrade": "They stand upright on digitigrade legs, walking on their toes.",
            "quadruped": "They move on four legs.",
            "quadruped_hooved": "They stand on four hooved legs.",
            "tauroid": "They have a humanoid upper body atop a four-legged lower body.",
            "serpentine": "Their humanoid torso gives way to a long serpentine tail.",
            "aquatic": "Their upper body is humanoid, but below the waist is a powerful fish tail.",
            "avian": "Their arms are great feathered wings.",
            "tentacled": "Multiple tentacles serve as their limbs.",
        }
        return descriptions.get(structure_key, "")
    
    def _describe_region(
        self,
        body: "Body",
        region: str,
        sexual_states: Optional["SexualStateManager"],
        include_covered: bool,
    ) -> str:
        """Describe a body region (head, torso, etc.)."""
        parts_in_region = []
        
        # Map regions to parent parts
        region_parents = {
            "head": ["head", "face", "muzzle"],
            "torso": ["chest", "torso", "back"],
        }
        
        parents = region_parents.get(region, [region])
        
        for part_key, part_instance in body.parts.items():
            part_def = get_part(part_key)
            if not part_def:
                continue
            
            if part_def.parent in parents or part_key in parents:
                # Skip covered unless requested
                if part_instance.covered_by and not include_covered:
                    continue
                
                # Skip internal parts
                if part_def.is_internal:
                    continue
                
                parts_in_region.append(part_key)
        
        if not parts_in_region:
            return ""
        
        # Build description
        notable = []
        for part_key in parts_in_region:
            part_def = get_part(part_key)
            if part_def and (part_def.is_optional or part_key in ["muzzle", "horns", "tail"]):
                notable.append(part_def.name)
        
        if notable:
            return f"Notable features include: {', '.join(notable)}."
        
        return ""
    
    def _describe_sexual_parts(
        self,
        body: "Body",
        sexual_states: Optional["SexualStateManager"],
        include_covered: bool,
    ) -> str:
        """Describe sexual parts with current state."""
        lines = []
        
        # Breasts
        breast_desc = self._describe_breasts(body, sexual_states)
        if breast_desc:
            lines.append(breast_desc)
        
        # Genitals
        genital_desc = self._describe_genitals(body, sexual_states)
        if genital_desc:
            lines.append(genital_desc)
        
        return " ".join(lines)
    
    def _describe_breasts(
        self,
        body: "Body",
        sexual_states: Optional["SexualStateManager"],
    ) -> str:
        """Describe breasts if present."""
        breast_parts = [k for k in body.parts.keys() if k.startswith("breast_")]
        
        if not breast_parts:
            return ""
        
        count = len(breast_parts)
        
        # Get size from instance
        size = "average"
        for bp in breast_parts:
            if bp in body.parts:
                custom_size = body.parts[bp].custom_size
                if custom_size:
                    size = custom_size
                    break
        
        size_word = SIZE_WORDS.get(size, ["average"])[0]
        
        if count == 2:
            desc = f"A pair of {size_word} breasts"
        elif count == 4:
            desc = f"Two rows of {size_word} breasts"
        elif count == 6:
            desc = f"Three rows of {size_word} breasts"
        else:
            desc = f"{count // 2} pairs of {size_word} breasts"
        
        # Add nipple state if available
        if sexual_states:
            for bp in breast_parts:
                state = sexual_states.get_breast_state(bp)
                if state:
                    if state.is_lactating:
                        desc += ", heavy with milk"
                    if state.nipple_erect:
                        desc += ", nipples stiff"
                    break
        
        return desc + "."
    
    def _describe_genitals(
        self,
        body: "Body",
        sexual_states: Optional["SexualStateManager"],
    ) -> str:
        """Describe genital area."""
        lines = []
        
        # Find cock
        cock_parts = [k for k in body.parts.keys() if k.startswith("cock_") or k == "hemipenes"]
        for cock_key in cock_parts:
            desc = self._describe_cock(cock_key, body, sexual_states)
            if desc:
                lines.append(desc)
        
        # Find pussy
        if "pussy" in body.parts:
            desc = self._describe_pussy(body, sexual_states)
            if desc:
                lines.append(desc)
        
        # Cloaca
        if "cloaca" in body.parts and "pussy" not in body.parts:
            lines.append("A smooth cloaca between the legs.")
        
        # Balls
        if "balls" in body.parts:
            size = body.parts["balls"].custom_size or "average"
            size_word = SIZE_WORDS.get(size, ["average"])[0]
            
            state_desc = ""
            if sexual_states:
                state = sexual_states.get_penetrator_state("balls")
                # Balls don't have their own state, but cum storage is tracked on cock
                for cock_key in cock_parts:
                    pen_state = sexual_states.get_penetrator_state(cock_key)
                    if pen_state:
                        if pen_state.cum_stored >= 0.9:
                            state_desc = ", looking full and heavy"
                        elif pen_state.cum_stored <= 0.2:
                            state_desc = ", looking drained"
                        break
            
            lines.append(f"A {size_word} pair of balls{state_desc}.")
        
        return " ".join(lines)
    
    def _describe_cock(
        self,
        part_key: str,
        body: "Body",
        sexual_states: Optional["SexualStateManager"],
    ) -> str:
        """Describe a specific cock with current state."""
        if part_key not in body.parts:
            return ""
        
        part = body.parts[part_key]
        sex_part = get_sexual_part(part_key)
        
        # Base type description
        type_desc = COCK_TYPE_DESCRIPTIONS.get(part_key, "cock")
        
        # Size
        size = part.custom_size or "average"
        size_word = SIZE_WORDS.get(size, ["average"])[0]
        
        # Get arousal state
        arousal_desc = "soft"
        knot_desc = ""
        
        if sexual_states:
            state = sexual_states.get_penetrator_state(part_key)
            if state:
                arousal = state.arousal
                arousal_descs = AROUSAL_DESCRIPTIONS.get(self.mode, AROUSAL_DESCRIPTIONS[DescriptionMode.EROTIC])
                arousal_desc = arousal_descs.get(arousal, "")
                
                # Knot state
                if state.knot_state == KnotState.SWELLING:
                    knot_desc = ", its knot beginning to swell"
                elif state.knot_state == KnotState.FULL:
                    knot_desc = ", its knot fully engorged"
                elif state.knot_state == KnotState.LOCKED:
                    knot_desc = f", its knot locked inside"
        
        # Build description
        if self.mode == DescriptionMode.EROTIC:
            return f"A {size_word} {type_desc}, currently {arousal_desc}{knot_desc}."
        else:
            return f"A {size_word} {type_desc}."
    
    def _describe_pussy(
        self,
        body: "Body",
        sexual_states: Optional["SexualStateManager"],
    ) -> str:
        """Describe pussy with current state."""
        if "pussy" not in body.parts:
            return ""
        
        wetness_desc = ""
        virgin_desc = ""
        gape_desc = ""
        cum_desc = ""
        
        if sexual_states:
            state = sexual_states.get_orifice_state("pussy")
            if state:
                # Wetness
                wetness = state.current_wetness
                wetness_descs = WETNESS_DESCRIPTIONS.get(self.mode, WETNESS_DESCRIPTIONS[DescriptionMode.EROTIC])
                for threshold, desc in sorted(wetness_descs.items(), reverse=True):
                    if wetness >= threshold:
                        wetness_desc = desc
                        break
                
                # Virginity
                if state.orifice_state == OrificeState.VIRGIN:
                    virgin_desc = "virgin "
                
                # Gaping
                if state.is_gaping:
                    gape_desc = ", gaping open"
                
                # Cum inside
                if state.cum_inside > 0.5:
                    cum_desc = ", cum oozing out"
                elif state.cum_inside > 0:
                    cum_desc = ", traces of cum visible"
        
        if self.mode == DescriptionMode.EROTIC:
            return f"A {virgin_desc}pussy, {wetness_desc or 'dry'}{gape_desc}{cum_desc}."
        else:
            return "A pussy."
    
    def _describe_sexual_part(
        self,
        part_key: str,
        body: "Body",
        sexual_states: Optional["SexualStateManager"],
    ) -> str:
        """Describe any sexual part."""
        if part_key.startswith("cock_") or part_key == "hemipenes":
            return self._describe_cock(part_key, body, sexual_states)
        elif part_key == "pussy":
            return self._describe_pussy(body, sexual_states)
        elif part_key.startswith("breast"):
            return self._describe_breasts(body, sexual_states)
        else:
            # Generic
            sex_part = get_sexual_part(part_key)
            if sex_part:
                return sex_part.default_desc or f"A {sex_part.name}."
            return ""
    
    def _describe_limbs(
        self,
        body: "Body",
        sexual_states: Optional["SexualStateManager"],
    ) -> str:
        """Describe limbs briefly."""
        # Just note anything unusual
        notes = []
        
        # Check for missing limbs
        for limb in ["left_arm", "right_arm", "left_leg", "right_leg"]:
            if limb in body.parts:
                part = body.parts[limb]
                if part.state.value == "missing":
                    notes.append(f"missing {part.part_key.replace('_', ' ')}")
                elif part.state.value == "prosthetic":
                    notes.append(f"prosthetic {part.part_key.replace('_', ' ')}")
        
        # Check for extra limbs
        if "wings" in body.parts or "wing_left" in body.parts:
            wing_part = body.parts.get("wings") or body.parts.get("wing_left")
            notes.append("a pair of wings")
        
        if notes:
            return "Notable: " + ", ".join(notes) + "."
        
        return ""
    
    def _describe_special_features(self, body: "Body") -> str:
        """Describe special features like tail, wings, horns."""
        features = []
        
        # Tail
        tail_parts = [k for k in body.parts.keys() if "tail" in k and not k.startswith("fish")]
        if tail_parts:
            tail_key = tail_parts[0]
            part = body.parts[tail_key]
            part_def = get_part(tail_key)
            if part_def:
                features.append(f"a {part_def.name}")
        
        # Horns
        horn_parts = [k for k in body.parts.keys() if "horn" in k]
        if horn_parts:
            if len(horn_parts) == 1:
                features.append("a horn")
            else:
                features.append("horns")
        
        # Wings (if not already mentioned in limbs)
        # Already handled in limbs
        
        if features:
            return "They have " + ", ".join(features) + "."
        
        return ""
    
    def _describe_presentation(self, body: "Body") -> str:
        """Describe marks, fluids, and body state from presentation layer."""
        if not body.presentation:
            return ""
        
        lines = []
        
        # Visible marks
        visible_marks = body.presentation.get_visible_marks()
        if visible_marks:
            mark_descs = []
            for mark in visible_marks[:3]:  # Limit to 3 most notable
                mark_descs.append(f"{mark.mark_type.value} on {mark.location}: {mark.description}")
            if mark_descs:
                lines.append("Marks: " + "; ".join(mark_descs))
        
        # Body state
        states = body.presentation.get_states()
        if states:
            state_words = [s.state_type.value for s in states]
            if state_words:
                lines.append(f"Currently: {', '.join(state_words)}")
        
        # Messiness
        if body.presentation.is_messy():
            lines.append("Visibly messy with various fluids.")
        
        return " ".join(lines)


# =============================================================================
# CONVENIENCE FUNCTIONS
# =============================================================================

def describe_body(
    body: "Body",
    sexual_states: Optional["SexualStateManager"] = None,
    mode: DescriptionMode = DescriptionMode.EROTIC,
    include_sexual: bool = True,
) -> str:
    """
    Quick function to describe a body.
    
    Args:
        body: Body to describe
        sexual_states: Optional state manager
        mode: Description mode
        include_sexual: Whether to include sexual parts
    
    Returns:
        Description string
    """
    describer = BodyDescriber(mode=mode)
    return describer.describe_full_body(
        body,
        sexual_states=sexual_states,
        include_sexual=include_sexual,
    )


def describe_part(
    body: "Body",
    part_key: str,
    sexual_states: Optional["SexualStateManager"] = None,
    mode: DescriptionMode = DescriptionMode.EROTIC,
) -> str:
    """Quick function to describe a single part."""
    describer = BodyDescriber(mode=mode)
    return describer.describe_part(body, part_key, sexual_states)
