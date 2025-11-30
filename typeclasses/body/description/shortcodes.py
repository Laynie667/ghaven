"""
Part Description System

Simple shortcode-based description injection for body parts.

Players set TWO descriptions on their character:
- desc_dressed: How they look with clothes on
- desc_nude: How they look naked

Both can contain shortcodes like [part:cock], [part:breasts], [part:pussy]
that get replaced with the appropriate description based on:
- Dressed vs Nude (which desc is being shown)
- Aroused vs Normal (character's current arousal state)

USAGE IN DESCRIPTIONS:
    desc_dressed = "A tall wolf in a leather jacket. [part:bulge] [part:chest]"
    desc_nude = "A tall wolf with [part:cock] and [part:balls]. [part:breasts]"

SHORTCODE FORMAT:
    [part:key]           - Basic part injection
    [part:key:size]      - With size override (tiny/small/average/large/huge)
    [part:key:size:adj]  - With size and adjective

AVAILABLE SHORTCODES:
    Sexual:
        [part:cock]      - Penis (type based on body's genital_category)
        [part:bulge]     - Clothed cock hint
        [part:balls]     - Testicles
        [part:pussy]     - Vagina
        [part:clit]      - Clitoris
        [part:ass]       - Butt/asshole area
        [part:breasts]   - Chest/breasts
        [part:nipples]   - Nipples specifically
    
    Non-sexual:
        [part:tail]      - Tail if present
        [part:ears]      - Ears
        [part:eyes]      - Eyes
        [part:hair]      - Hair/mane
        [part:wings]     - Wings if present
"""

from dataclasses import dataclass, field
from typing import Dict, Optional, List, Tuple, TYPE_CHECKING
from enum import Enum
import re

if TYPE_CHECKING:
    from ..core.body import Body
    from ..state.sexual import SexualStateManager


# =============================================================================
# DESCRIPTION STATES
# =============================================================================

class ClothingState(Enum):
    """Whether character is dressed or nude."""
    DRESSED = "dressed"
    NUDE = "nude"


class ArousalLevel(Enum):
    """Simplified arousal for descriptions."""
    NORMAL = "normal"
    AROUSED = "aroused"


# =============================================================================
# PART DESCRIPTION TEMPLATES
# =============================================================================

@dataclass
class PartDescriptions:
    """
    Four description variants for a body part.
    
    Each part has descriptions for all four state combinations.
    Supports {size} and {adj} placeholders for customization.
    """
    
    # The four states
    dressed_normal: str = ""
    dressed_aroused: str = ""
    nude_normal: str = ""
    nude_aroused: str = ""
    
    # For parts that might not exist
    fallback: str = ""  # Shown if part doesn't exist on body
    
    def get(self, clothing: ClothingState, arousal: ArousalLevel) -> str:
        """Get the appropriate description for the state."""
        if clothing == ClothingState.DRESSED:
            if arousal == ArousalLevel.AROUSED:
                return self.dressed_aroused
            return self.dressed_normal
        else:
            if arousal == ArousalLevel.AROUSED:
                return self.nude_aroused
            return self.nude_normal


# =============================================================================
# COCK DESCRIPTIONS BY TYPE
# =============================================================================

COCK_DESCS: Dict[str, PartDescriptions] = {
    "human": PartDescriptions(
        dressed_normal="a subtle bulge at the crotch",
        dressed_aroused="an obvious bulge straining against the fabric",
        nude_normal="a soft {size} cock resting against their thigh",
        nude_aroused="a {size} cock standing at full attention, tip glistening with precum",
    ),
    
    "canine": PartDescriptions(
        dressed_normal="a subtle bulge hinting at what's sheathed beneath",
        dressed_aroused="a prominent tent, the outline of a pointed tip visible",
        nude_normal="a furry sheath between their legs, the tip of a {size} red cock barely peeking out",
        nude_aroused="a {size} tapered canine cock throbbing eagerly, knot swelling at the base, dripping precum",
    ),
    
    "equine": PartDescriptions(
        dressed_normal="a considerable bulge that's hard to hide",
        dressed_aroused="a massive tent that leaves little to imagination",
        nude_normal="a thick sheath hanging heavily between their legs, the broad head of a {size} horse cock visible",
        nude_aroused="a {size} flared horse cock at full mast, the medial ring pulsing, flat head flaring wider",
    ),
    
    "feline": PartDescriptions(
        dressed_normal="a modest bulge at the crotch",
        dressed_aroused="a noticeable tent with a pointed shape",
        nude_normal="a furry sheath with a {size} barbed cock mostly hidden within",
        nude_aroused="a {size} barbed feline cock emerged and twitching, the backwards-facing spines visible",
    ),
    
    "reptile": PartDescriptions(
        dressed_normal="a smooth crotch with no visible bulge",
        dressed_aroused="twin bulges pressing against the fabric",
        nude_normal="a smooth slit between their legs, hiding what's within",
        nude_aroused="twin {size} hemipenes emerged from their slit, ridged and glistening",
    ),
    
    "dolphin": PartDescriptions(
        dressed_normal="a smooth crotch area",
        dressed_aroused="something writhing beneath the fabric",
        nude_normal="a genital slit with a {size} prehensile cock coiled within",
        nude_aroused="a {size} prehensile dolphin cock extended and curling, seeking on its own",
    ),
    
    "tentacle": PartDescriptions(
        dressed_normal="something squirming beneath the clothes",
        dressed_aroused="multiple somethings writhing and straining against fabric",
        nude_normal="a nest of {size} tentacles where genitals would be, mostly dormant",
        nude_aroused="{size} tentacle cocks writhing eagerly, tips drooling slick fluid",
    ),
}

# Fallback for unknown types
DEFAULT_COCK_DESC = PartDescriptions(
    dressed_normal="a bulge at the crotch",
    dressed_aroused="an obvious aroused state",
    nude_normal="a {size} cock",
    nude_aroused="a {size} cock, visibly aroused",
)


# =============================================================================
# OTHER SEXUAL PART DESCRIPTIONS
# =============================================================================

BALLS_DESC = PartDescriptions(
    dressed_normal="",  # Usually not visible when dressed
    dressed_aroused="",
    nude_normal="{size} balls hanging beneath",
    nude_aroused="{size} balls drawn up tight",
)

PUSSY_DESC = PartDescriptions(
    dressed_normal="",  # Not visible when dressed
    dressed_aroused="a damp spot forming on the fabric",
    nude_normal="a {adj} pussy between their legs",
    nude_aroused="a {adj} pussy glistening with arousal, lips parted and inviting",
)

CLIT_DESC = PartDescriptions(
    dressed_normal="",
    dressed_aroused="",
    nude_normal="a {size} clit peeking from its hood",
    nude_aroused="a {size} clit swollen and throbbing, emerged from its hood",
)

ASS_DESC = PartDescriptions(
    dressed_normal="a {size} rear filling out the clothes nicely",
    dressed_aroused="a {size} rear, tail raised suggestively",
    nude_normal="a {size} {adj} ass",
    nude_aroused="a {size} {adj} ass, hole twitching with anticipation",
)

BREASTS_DESC = PartDescriptions(
    dressed_normal="{size} breasts beneath their clothes",
    dressed_aroused="{size} breasts, nipples visibly hard through the fabric",
    nude_normal="{size} breasts with {adj} nipples",
    nude_aroused="{size} breasts heaving, {adj} nipples stiff and aching",
)

NIPPLES_DESC = PartDescriptions(
    dressed_normal="",  # Covered
    dressed_aroused="nipples poking through the fabric",
    nude_normal="{adj} nipples",
    nude_aroused="{adj} nipples standing stiff",
)

# For lactating characters
BREASTS_LACTATING_DESC = PartDescriptions(
    dressed_normal="{size} milk-heavy breasts, wet spots forming on the fabric",
    dressed_aroused="{size} breasts leaking through their clothes, nipples rock hard",
    nude_normal="{size} breasts heavy with milk, drops beading on {adj} nipples",
    nude_aroused="{size} breasts dripping milk freely, {adj} nipples aching to be suckled",
)


# =============================================================================
# NON-SEXUAL PART DESCRIPTIONS
# =============================================================================

TAIL_DESCS: Dict[str, PartDescriptions] = {
    "canine": PartDescriptions(
        dressed_normal="a {adj} canine tail swaying behind them",
        dressed_aroused="a {adj} canine tail wagging eagerly",
        nude_normal="a {adj} canine tail swaying behind them",
        nude_aroused="a {adj} canine tail wagging frantically, lifted to expose their rear",
    ),
    "feline": PartDescriptions(
        dressed_normal="a {adj} feline tail curling lazily",
        dressed_aroused="a {adj} feline tail lashing with excitement",
        nude_normal="a {adj} feline tail curling lazily",
        nude_aroused="a {adj} feline tail raised high, quivering",
    ),
    "equine": PartDescriptions(
        dressed_normal="a {adj} flowing tail",
        dressed_aroused="a {adj} tail flagged high",
        nude_normal="a {adj} flowing tail",
        nude_aroused="a {adj} tail flagged high, presenting",
    ),
    "reptile": PartDescriptions(
        dressed_normal="a {adj} scaled tail dragging behind",
        dressed_aroused="a {adj} scaled tail thrashing",
        nude_normal="a {adj} scaled tail",
        nude_aroused="a {adj} scaled tail coiling with agitation",
    ),
    "default": PartDescriptions(
        dressed_normal="a tail behind them",
        dressed_aroused="a tail swishing with excitement",
        nude_normal="a tail behind them",
        nude_aroused="a tail raised",
    ),
}

EARS_DESC = PartDescriptions(
    dressed_normal="{adj} ears atop their head",
    dressed_aroused="{adj} ears perked forward attentively",
    nude_normal="{adj} ears atop their head",
    nude_aroused="{adj} ears flattened back",
)

EYES_DESC = PartDescriptions(
    dressed_normal="{adj} eyes",
    dressed_aroused="{adj} eyes with dilated pupils",
    nude_normal="{adj} eyes",
    nude_aroused="{adj} eyes dark with desire",
)

WINGS_DESC = PartDescriptions(
    dressed_normal="{adj} wings folded against their back",
    dressed_aroused="{adj} wings half-spread, trembling",
    nude_normal="{adj} wings folded against their back",
    nude_aroused="{adj} wings spread wide, feathers ruffled",
)


# =============================================================================
# SIZE AND ADJECTIVE MAPPINGS
# =============================================================================

SIZE_WORDS = {
    "tiny": ["tiny", "minuscule", "itty-bitty", "dainty"],
    "small": ["small", "petite", "modest", "little"],
    "average": ["average", "normal", "moderate", "typical"],
    "large": ["large", "big", "sizeable", "generous"],
    "huge": ["huge", "massive", "enormous", "impressive"],
    "massive": ["massive", "gigantic", "monstrous", "overwhelming"],
}

# Default adjectives for parts when none specified
DEFAULT_ADJS = {
    "pussy": ["pink", "smooth", "soft", "delicate"],
    "ass": ["round", "firm", "plump", "shapely"],
    "nipples": ["pert", "pink", "sensitive", "soft"],
    "ears": ["pointed", "fuzzy", "alert", "expressive"],
    "eyes": ["bright", "deep", "striking", "captivating"],
    "tail": ["long", "fluffy", "sleek", "bushy"],
    "wings": ["broad", "elegant", "powerful", "graceful"],
}


# =============================================================================
# SHORTCODE PROCESSOR
# =============================================================================

class PartShortcodeProcessor:
    """
    Processes [part:X] shortcodes in character descriptions.
    
    Usage:
        processor = PartShortcodeProcessor(body, sexual_states)
        result = processor.process(desc_text, ClothingState.NUDE, ArousalLevel.AROUSED)
    """
    
    # Pattern: [part:key] or [part:key:size] or [part:key:size:adj]
    PATTERN = re.compile(r'\[part:(\w+)(?::(\w+))?(?::(\w+))?\]')
    
    def __init__(
        self,
        body: "Body",
        sexual_states: Optional["SexualStateManager"] = None,
    ):
        """
        Initialize processor.
        
        Args:
            body: The character's body
            sexual_states: Sexual state manager (for lactation, etc.)
        """
        self.body = body
        self.sexual_states = sexual_states
    
    def process(
        self,
        text: str,
        clothing: ClothingState,
        arousal: ArousalLevel,
    ) -> str:
        """
        Process all [part:X] shortcodes in text.
        
        Args:
            text: Description text with shortcodes
            clothing: Current clothing state
            arousal: Current arousal level
        
        Returns:
            Text with shortcodes replaced
        """
        def replacer(match):
            part_key = match.group(1)
            size_override = match.group(2)
            adj_override = match.group(3)
            
            return self._get_part_desc(
                part_key, clothing, arousal,
                size_override, adj_override
            )
        
        return self.PATTERN.sub(replacer, text)
    
    def _get_part_desc(
        self,
        part_key: str,
        clothing: ClothingState,
        arousal: ArousalLevel,
        size_override: Optional[str] = None,
        adj_override: Optional[str] = None,
    ) -> str:
        """Get description for a specific part."""
        
        # Route to appropriate handler
        handlers = {
            "cock": self._desc_cock,
            "bulge": self._desc_bulge,
            "balls": self._desc_balls,
            "pussy": self._desc_pussy,
            "clit": self._desc_clit,
            "ass": self._desc_ass,
            "breasts": self._desc_breasts,
            "chest": self._desc_breasts,  # Alias
            "nipples": self._desc_nipples,
            "tail": self._desc_tail,
            "ears": self._desc_ears,
            "eyes": self._desc_eyes,
            "wings": self._desc_wings,
        }
        
        handler = handlers.get(part_key)
        if handler:
            return handler(clothing, arousal, size_override, adj_override)
        
        # Unknown part - return empty or placeholder
        return f"[unknown part: {part_key}]"
    
    def _get_size_word(self, size: Optional[str], default: str = "average") -> str:
        """Get a size word, with some randomization."""
        size = size or default
        words = SIZE_WORDS.get(size, SIZE_WORDS["average"])
        # Just use first for consistency, could randomize
        return words[0]
    
    def _get_adj(self, part_key: str, override: Optional[str] = None) -> str:
        """Get an adjective for a part."""
        if override:
            return override
        adjs = DEFAULT_ADJS.get(part_key, [""])
        return adjs[0] if adjs else ""
    
    # =========================================================================
    # PART DESCRIPTION HANDLERS
    # =========================================================================
    
    def _desc_cock(
        self,
        clothing: ClothingState,
        arousal: ArousalLevel,
        size: Optional[str],
        adj: Optional[str],
    ) -> str:
        """Get cock description."""
        # Check if body has a cock
        cock_keys = [k for k in self.body.parts if k.startswith("cock_")]
        if not cock_keys:
            return ""  # No cock, return nothing
        
        # Get genital category for description type
        genital_cat = self.body.genital_category or "human"
        descs = COCK_DESCS.get(genital_cat, DEFAULT_COCK_DESC)
        
        # Get part instance for size
        cock_part = self.body.parts.get(cock_keys[0])
        part_size = size or (cock_part.custom_size if cock_part else None) or "average"
        
        desc = descs.get(clothing, arousal)
        return desc.format(size=self._get_size_word(part_size), adj=adj or "")
    
    def _desc_bulge(
        self,
        clothing: ClothingState,
        arousal: ArousalLevel,
        size: Optional[str],
        adj: Optional[str],
    ) -> str:
        """Get bulge description (clothed cock hint)."""
        # Only show bulge when dressed
        if clothing == ClothingState.NUDE:
            return ""
        
        # Check if body has a cock
        cock_keys = [k for k in self.body.parts if k.startswith("cock_")]
        if not cock_keys:
            return ""
        
        genital_cat = self.body.genital_category or "human"
        descs = COCK_DESCS.get(genital_cat, DEFAULT_COCK_DESC)
        
        # Bulge uses dressed descriptions
        if arousal == ArousalLevel.AROUSED:
            return descs.dressed_aroused
        return descs.dressed_normal
    
    def _desc_balls(
        self,
        clothing: ClothingState,
        arousal: ArousalLevel,
        size: Optional[str],
        adj: Optional[str],
    ) -> str:
        """Get balls description."""
        if "balls" not in self.body.parts:
            return ""
        
        part = self.body.parts.get("balls")
        part_size = size or (part.custom_size if part else None) or "average"
        
        desc = BALLS_DESC.get(clothing, arousal)
        if not desc:
            return ""
        return desc.format(size=self._get_size_word(part_size))
    
    def _desc_pussy(
        self,
        clothing: ClothingState,
        arousal: ArousalLevel,
        size: Optional[str],
        adj: Optional[str],
    ) -> str:
        """Get pussy description."""
        if "pussy" not in self.body.parts:
            return ""
        
        part_adj = adj or self._get_adj("pussy")
        
        desc = PUSSY_DESC.get(clothing, arousal)
        if not desc:
            return ""
        return desc.format(adj=part_adj, size=size or "")
    
    def _desc_clit(
        self,
        clothing: ClothingState,
        arousal: ArousalLevel,
        size: Optional[str],
        adj: Optional[str],
    ) -> str:
        """Get clit description."""
        if "clit" not in self.body.parts:
            return ""
        
        part = self.body.parts.get("clit")
        part_size = size or (part.custom_size if part else None) or "small"
        
        desc = CLIT_DESC.get(clothing, arousal)
        if not desc:
            return ""
        return desc.format(size=self._get_size_word(part_size))
    
    def _desc_ass(
        self,
        clothing: ClothingState,
        arousal: ArousalLevel,
        size: Optional[str],
        adj: Optional[str],
    ) -> str:
        """Get ass/butt description."""
        part = self.body.parts.get("buttocks")
        part_size = size or (part.custom_size if part else None) or "average"
        part_adj = adj or self._get_adj("ass")
        
        desc = ASS_DESC.get(clothing, arousal)
        return desc.format(size=self._get_size_word(part_size), adj=part_adj)
    
    def _desc_breasts(
        self,
        clothing: ClothingState,
        arousal: ArousalLevel,
        size: Optional[str],
        adj: Optional[str],
    ) -> str:
        """Get breasts description."""
        breast_keys = [k for k in self.body.parts if k.startswith("breast_")]
        if not breast_keys:
            # No breasts - maybe flat chest?
            if clothing == ClothingState.NUDE:
                return "a flat chest"
            return ""
        
        # Get size from part
        part = self.body.parts.get(breast_keys[0])
        part_size = size or (part.custom_size if part else None) or "average"
        
        # Check for lactation
        is_lactating = False
        if self.sexual_states:
            for bk in breast_keys:
                state = self.sexual_states.get_breast_state(bk)
                if state and state.is_lactating:
                    is_lactating = True
                    break
        
        # Choose description set
        descs = BREASTS_LACTATING_DESC if is_lactating else BREASTS_DESC
        
        # Nipple adjective
        nipple_adj = adj or self._get_adj("nipples")
        
        desc = descs.get(clothing, arousal)
        return desc.format(size=self._get_size_word(part_size), adj=nipple_adj)
    
    def _desc_nipples(
        self,
        clothing: ClothingState,
        arousal: ArousalLevel,
        size: Optional[str],
        adj: Optional[str],
    ) -> str:
        """Get nipples description."""
        nipple_keys = [k for k in self.body.parts if k.startswith("nipple_")]
        if not nipple_keys:
            return ""
        
        part_adj = adj or self._get_adj("nipples")
        
        desc = NIPPLES_DESC.get(clothing, arousal)
        if not desc:
            return ""
        return desc.format(adj=part_adj)
    
    def _desc_tail(
        self,
        clothing: ClothingState,
        arousal: ArousalLevel,
        size: Optional[str],
        adj: Optional[str],
    ) -> str:
        """Get tail description."""
        tail_keys = [k for k in self.body.parts if "tail" in k]
        if not tail_keys:
            return ""
        
        # Determine tail type from species
        species_key = self.body.species_key or ""
        
        # Map species to tail type
        tail_type = "default"
        if any(x in species_key for x in ["wolf", "dog", "fox", "canine"]):
            tail_type = "canine"
        elif any(x in species_key for x in ["cat", "lion", "tiger", "feline"]):
            tail_type = "feline"
        elif any(x in species_key for x in ["horse", "equine", "zebra"]):
            tail_type = "equine"
        elif any(x in species_key for x in ["lizard", "dragon", "snake", "reptile"]):
            tail_type = "reptile"
        
        descs = TAIL_DESCS.get(tail_type, TAIL_DESCS["default"])
        part_adj = adj or self._get_adj("tail")
        
        desc = descs.get(clothing, arousal)
        return desc.format(adj=part_adj)
    
    def _desc_ears(
        self,
        clothing: ClothingState,
        arousal: ArousalLevel,
        size: Optional[str],
        adj: Optional[str],
    ) -> str:
        """Get ears description."""
        ear_keys = [k for k in self.body.parts if "ear" in k]
        if not ear_keys:
            return ""
        
        part_adj = adj or self._get_adj("ears")
        desc = EARS_DESC.get(clothing, arousal)
        return desc.format(adj=part_adj)
    
    def _desc_eyes(
        self,
        clothing: ClothingState,
        arousal: ArousalLevel,
        size: Optional[str],
        adj: Optional[str],
    ) -> str:
        """Get eyes description."""
        part = self.body.parts.get("eyes")
        part_adj = adj or (part.custom_color if part else None) or self._get_adj("eyes")
        
        desc = EYES_DESC.get(clothing, arousal)
        return desc.format(adj=part_adj)
    
    def _desc_wings(
        self,
        clothing: ClothingState,
        arousal: ArousalLevel,
        size: Optional[str],
        adj: Optional[str],
    ) -> str:
        """Get wings description."""
        wing_keys = [k for k in self.body.parts if "wing" in k]
        if not wing_keys:
            return ""
        
        part_adj = adj or self._get_adj("wings")
        desc = WINGS_DESC.get(clothing, arousal)
        return desc.format(adj=part_adj)


# =============================================================================
# CONVENIENCE FUNCTIONS
# =============================================================================

def process_description(
    text: str,
    body: "Body",
    clothing: ClothingState = ClothingState.DRESSED,
    arousal: ArousalLevel = ArousalLevel.NORMAL,
    sexual_states: Optional["SexualStateManager"] = None,
) -> str:
    """
    Process a description string, replacing all [part:X] shortcodes.
    
    Args:
        text: Description with shortcodes
        body: Character's body
        clothing: DRESSED or NUDE
        arousal: NORMAL or AROUSED
        sexual_states: Optional state manager
    
    Returns:
        Processed description string
    """
    processor = PartShortcodeProcessor(body, sexual_states)
    return processor.process(text, clothing, arousal)


def get_character_description(
    body: "Body",
    desc_dressed: str,
    desc_nude: str,
    is_nude: bool = False,
    is_aroused: bool = False,
    sexual_states: Optional["SexualStateManager"] = None,
) -> str:
    """
    Get the appropriate character description based on state.
    
    Args:
        body: Character's body
        desc_dressed: Player's dressed description
        desc_nude: Player's nude description
        is_nude: Whether currently nude
        is_aroused: Whether currently aroused
        sexual_states: Optional state manager
    
    Returns:
        Fully processed description string
    """
    clothing = ClothingState.NUDE if is_nude else ClothingState.DRESSED
    arousal = ArousalLevel.AROUSED if is_aroused else ArousalLevel.NORMAL
    
    text = desc_nude if is_nude else desc_dressed
    
    return process_description(
        text, body, clothing, arousal,
        sexual_states
    )
