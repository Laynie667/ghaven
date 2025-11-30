"""
Body - Part Definitions

Individual part definitions. These are SHARED DATA, not per-character.
Parts define what something IS, not what state it's in.

Organized by body region for clarity.
"""

from dataclasses import dataclass, field
from typing import List, Dict, Optional


@dataclass
class PartDefinition:
    """
    Definition of a body part type.
    Shared data - every "left_hand" uses the same definition.
    """
    
    # Identity
    key: str                          # Unique identifier
    name: str                         # Display name
    plural: str = ""                  # Plural form
    
    # Hierarchy
    parent: Optional[str] = None      # What it's attached to
    side: Optional[str] = None        # "left", "right", "center", None
    
    # Mechanical functions
    functions: List[str] = field(default_factory=list)
    # Core functions:
    # - speech, hearing, smell, sight
    # - manipulate (grab/use things)
    # - locomotion (walking/moving)
    # - consume (eat/drink)
    # - breathe
    
    # Flags
    is_vital: bool = False            # Death if removed
    is_paired: bool = False           # Has left/right versions
    is_optional: bool = False         # Not all bodies have this
    is_sexual: bool = False           # Adult content part
    is_internal: bool = False         # Inside body
    
    # Interaction
    is_targetable: bool = True        # Can be targeted
    is_coverable: bool = True         # Can wear things on it
    is_exposable: bool = True         # Can expose through partitions
    is_removable: bool = True         # Can be amputated
    
    # What can obstruct this part's function
    obstructable_by: List[str] = field(default_factory=list)
    
    # Description
    default_desc: str = ""
    size_options: List[str] = field(default_factory=lambda: ["average"])
    
    def __post_init__(self):
        if not self.plural:
            self.plural = self.name + "s"


# =============================================================================
# HEAD & FACE
# =============================================================================

HEAD = PartDefinition(
    key="head",
    name="head",
    parent=None,
    is_vital=True,
    is_removable=False,
)

FACE = PartDefinition(
    key="face",
    name="face",
    parent="head",
    is_removable=False,
)

SKULL = PartDefinition(
    key="skull",
    name="skull",
    parent="head",
    is_internal=True,
    is_vital=True,
)

HAIR = PartDefinition(
    key="hair",
    name="hair",
    parent="head",
    is_optional=True,
)

# Muzzle variants
MUZZLE = PartDefinition(
    key="muzzle",
    name="muzzle",
    parent="head",
    is_optional=True,
    functions=["smell", "speech", "consume", "breathe"],
    obstructable_by=["muzzle_gag", "tape", "hand"],
)

MUZZLE_CANINE = PartDefinition(
    key="muzzle_canine",
    name="canine muzzle",
    parent="head",
    is_optional=True,
    functions=["smell", "speech", "consume", "breathe"],
    default_desc="A long canine muzzle with a wet nose.",
)

MUZZLE_FELINE = PartDefinition(
    key="muzzle_feline",
    name="feline muzzle",
    parent="head",
    is_optional=True,
    functions=["smell", "speech", "consume", "breathe"],
    default_desc="A short feline muzzle with whiskers.",
)

MUZZLE_EQUINE = PartDefinition(
    key="muzzle_equine",
    name="equine muzzle",
    parent="head",
    is_optional=True,
    functions=["smell", "speech", "consume", "breathe"],
    default_desc="A long equine muzzle with soft lips.",
)

SNOUT = PartDefinition(
    key="snout",
    name="snout",
    parent="head",
    is_optional=True,
    functions=["smell", "speech", "consume", "breathe"],
    default_desc="A pronounced snout.",
)

BEAK = PartDefinition(
    key="beak",
    name="beak",
    parent="head",
    is_optional=True,
    functions=["consume"],  # Limited speech
    default_desc="A hard, curved beak.",
)


# =============================================================================
# SENSORY ORGANS
# =============================================================================

# Eyes
LEFT_EYE = PartDefinition(
    key="left_eye",
    name="left eye",
    plural="eyes",
    parent="face",
    side="left",
    is_paired=True,
    functions=["sight"],
    obstructable_by=["blindfold", "mask", "hand", "darkness"],
)

RIGHT_EYE = PartDefinition(
    key="right_eye",
    name="right eye",
    plural="eyes",
    parent="face",
    side="right",
    is_paired=True,
    functions=["sight"],
    obstructable_by=["blindfold", "mask", "hand", "darkness"],
)

# Ears - Human style
LEFT_EAR = PartDefinition(
    key="left_ear",
    name="left ear",
    plural="ears",
    parent="head",
    side="left",
    is_paired=True,
    functions=["hearing"],
    obstructable_by=["earplugs", "headphones", "hands"],
)

RIGHT_EAR = PartDefinition(
    key="right_ear",
    name="right ear",
    plural="ears",
    parent="head",
    side="right",
    is_paired=True,
    functions=["hearing"],
    obstructable_by=["earplugs", "headphones", "hands"],
)

# Ears - Pointed (elf)
LEFT_EAR_POINTED = PartDefinition(
    key="left_ear_pointed",
    name="left pointed ear",
    plural="pointed ears",
    parent="head",
    side="left",
    is_paired=True,
    is_optional=True,
    functions=["hearing"],
    default_desc="A long, elegantly pointed ear.",
)

RIGHT_EAR_POINTED = PartDefinition(
    key="right_ear_pointed",
    name="right pointed ear",
    plural="pointed ears",
    parent="head",
    side="right",
    is_paired=True,
    is_optional=True,
    functions=["hearing"],
    default_desc="A long, elegantly pointed ear.",
)

# Ears - Animal style (on top of head)
LEFT_EAR_CANINE = PartDefinition(
    key="left_ear_canine",
    name="left canine ear",
    plural="canine ears",
    parent="head",
    side="left",
    is_paired=True,
    is_optional=True,
    functions=["hearing"],
    default_desc="A pointed, furred ear that swivels.",
)

RIGHT_EAR_CANINE = PartDefinition(
    key="right_ear_canine",
    name="right canine ear",
    plural="canine ears",
    parent="head",
    side="right",
    is_paired=True,
    is_optional=True,
    functions=["hearing"],
)

LEFT_EAR_FELINE = PartDefinition(
    key="left_ear_feline",
    name="left feline ear",
    plural="feline ears",
    parent="head",
    side="left",
    is_paired=True,
    is_optional=True,
    functions=["hearing"],
    default_desc="A triangular, tufted ear.",
)

RIGHT_EAR_FELINE = PartDefinition(
    key="right_ear_feline",
    name="right feline ear",
    plural="feline ears",
    parent="head",
    side="right",
    is_paired=True,
    is_optional=True,
    functions=["hearing"],
)

LEFT_EAR_EQUINE = PartDefinition(
    key="left_ear_equine",
    name="left equine ear",
    plural="equine ears",
    parent="head",
    side="left",
    is_paired=True,
    is_optional=True,
    functions=["hearing"],
    default_desc="A long, mobile ear.",
)

RIGHT_EAR_EQUINE = PartDefinition(
    key="right_ear_equine",
    name="right equine ear",
    plural="equine ears",
    parent="head",
    side="right",
    is_paired=True,
    is_optional=True,
    functions=["hearing"],
)

LEFT_EAR_LAPINE = PartDefinition(
    key="left_ear_lapine",
    name="left lapine ear",
    plural="lapine ears",
    parent="head",
    side="left",
    is_paired=True,
    is_optional=True,
    functions=["hearing"],
    default_desc="A very long, floppy ear.",
)

RIGHT_EAR_LAPINE = PartDefinition(
    key="right_ear_lapine",
    name="right lapine ear",
    plural="lapine ears",
    parent="head",
    side="right",
    is_paired=True,
    is_optional=True,
    functions=["hearing"],
)

# Nose
NOSE = PartDefinition(
    key="nose",
    name="nose",
    parent="face",
    functions=["smell", "breathe"],
    obstructable_by=["clothespin", "hand", "mask"],
)

# Mouth
MOUTH = PartDefinition(
    key="mouth",
    name="mouth",
    parent="face",
    functions=["speech", "consume", "breathe"],
    obstructable_by=["gag", "ball_gag", "ring_gag", "tape", "hand", "muzzle_gag", "other"],
    is_exposable=True,
)

TONGUE = PartDefinition(
    key="tongue",
    name="tongue",
    parent="mouth",
    is_exposable=True,
)

TONGUE_FORKED = PartDefinition(
    key="tongue_forked",
    name="forked tongue",
    parent="mouth",
    is_optional=True,
    is_exposable=True,
    default_desc="A long, forked serpentine tongue.",
)

LIPS = PartDefinition(
    key="lips",
    name="lips",
    parent="mouth",
)

TEETH = PartDefinition(
    key="teeth",
    name="teeth",
    parent="mouth",
)

FANGS = PartDefinition(
    key="fangs",
    name="fangs",
    parent="mouth",
    is_optional=True,
    default_desc="Sharp, elongated fangs.",
)

TUSKS = PartDefinition(
    key="tusks",
    name="tusks",
    parent="mouth",
    is_optional=True,
    default_desc="Prominent tusks jutting from the lower jaw.",
)


# =============================================================================
# HEAD EXTRAS
# =============================================================================

HORNS = PartDefinition(
    key="horns",
    name="horns",
    parent="head",
    is_optional=True,
    is_paired=True,
)

HORNS_RAM = PartDefinition(
    key="horns_ram",
    name="ram horns",
    parent="head",
    is_optional=True,
    default_desc="Curled ram horns.",
)

HORNS_DEMON = PartDefinition(
    key="horns_demon",
    name="demon horns",
    parent="head",
    is_optional=True,
    default_desc="Curved demonic horns.",
)

ANTLERS = PartDefinition(
    key="antlers",
    name="antlers",
    parent="head",
    is_optional=True,
    default_desc="Branching antlers.",
)

ANTENNAE = PartDefinition(
    key="antennae",
    name="antennae",
    parent="head",
    is_optional=True,
    is_paired=True,
    functions=["smell", "hearing"],
    default_desc="Thin, sensitive antennae.",
)

CREST = PartDefinition(
    key="crest",
    name="crest",
    parent="head",
    is_optional=True,
    default_desc="A raised crest.",
)

MANE = PartDefinition(
    key="mane",
    name="mane",
    parent="head",
    is_optional=True,
    default_desc="A thick mane of hair.",
)


# =============================================================================
# NECK
# =============================================================================

NECK = PartDefinition(
    key="neck",
    name="neck",
    parent="head",
)

THROAT = PartDefinition(
    key="throat",
    name="throat",
    parent="neck",
)

NAPE = PartDefinition(
    key="nape",
    name="nape",
    parent="neck",
    default_desc="The back of the neck.",
)

SCRUFF = PartDefinition(
    key="scruff",
    name="scruff",
    parent="neck",
    is_optional=True,
    default_desc="The loose skin at the back of the neck.",
)

GILLS = PartDefinition(
    key="gills",
    name="gills",
    parent="neck",
    is_optional=True,
    functions=["breathe"],
    default_desc="Gill slits for breathing underwater.",
)


# =============================================================================
# TORSO - UPPER
# =============================================================================

TORSO = PartDefinition(
    key="torso",
    name="torso",
    parent=None,
    is_vital=True,
    is_removable=False,
)

CHEST = PartDefinition(
    key="chest",
    name="chest",
    parent="torso",
)

BACK = PartDefinition(
    key="back",
    name="back",
    parent="torso",
)

SHOULDERS = PartDefinition(
    key="shoulders",
    name="shoulders",
    parent="torso",
)

LEFT_SHOULDER = PartDefinition(
    key="left_shoulder",
    name="left shoulder",
    plural="shoulders",
    parent="torso",
    side="left",
    is_paired=True,
)

RIGHT_SHOULDER = PartDefinition(
    key="right_shoulder",
    name="right shoulder",
    plural="shoulders",
    parent="torso",
    side="right",
    is_paired=True,
)

# Breasts - various configurations
BREASTS = PartDefinition(
    key="breasts",
    name="breasts",
    parent="chest",
    is_optional=True,
    is_sexual=True,
    size_options=["flat", "small", "modest", "average", "large", "huge", "massive"],
)

LEFT_BREAST = PartDefinition(
    key="left_breast",
    name="left breast",
    plural="breasts",
    parent="chest",
    side="left",
    is_paired=True,
    is_optional=True,
    is_sexual=True,
)

RIGHT_BREAST = PartDefinition(
    key="right_breast",
    name="right breast",
    plural="breasts",
    parent="chest",
    side="right",
    is_paired=True,
    is_optional=True,
    is_sexual=True,
)

LEFT_NIPPLE = PartDefinition(
    key="left_nipple",
    name="left nipple",
    plural="nipples",
    parent="left_breast",
    side="left",
    is_paired=True,
    is_optional=True,
    is_sexual=True,
)

RIGHT_NIPPLE = PartDefinition(
    key="right_nipple",
    name="right nipple",
    plural="nipples",
    parent="right_breast",
    side="right",
    is_paired=True,
    is_optional=True,
    is_sexual=True,
)

# For multi-breasted species
UPPER_BREASTS = PartDefinition(
    key="upper_breasts",
    name="upper breasts",
    parent="chest",
    is_optional=True,
    is_sexual=True,
)

LOWER_BREASTS = PartDefinition(
    key="lower_breasts",
    name="lower breasts",
    parent="stomach",
    is_optional=True,
    is_sexual=True,
)

PECS = PartDefinition(
    key="pecs",
    name="pecs",
    parent="chest",
    is_optional=True,
    default_desc="Well-defined pectoral muscles.",
)


# =============================================================================
# TORSO - LOWER
# =============================================================================

STOMACH = PartDefinition(
    key="stomach",
    name="stomach",
    parent="torso",
)

BELLY = PartDefinition(
    key="belly",
    name="belly",
    parent="stomach",
)

NAVEL = PartDefinition(
    key="navel",
    name="navel",
    parent="belly",
)

WAIST = PartDefinition(
    key="waist",
    name="waist",
    parent="torso",
)

HIPS = PartDefinition(
    key="hips",
    name="hips",
    parent="torso",
)

LEFT_HIP = PartDefinition(
    key="left_hip",
    name="left hip",
    plural="hips",
    parent="torso",
    side="left",
    is_paired=True,
)

RIGHT_HIP = PartDefinition(
    key="right_hip",
    name="right hip",
    plural="hips",
    parent="torso",
    side="right",
    is_paired=True,
)

LOWER_BACK = PartDefinition(
    key="lower_back",
    name="lower back",
    parent="back",
)


# =============================================================================
# GROIN & REAR
# =============================================================================

GROIN = PartDefinition(
    key="groin",
    name="groin",
    parent="torso",
    is_sexual=True,
)

PUBIC_MOUND = PartDefinition(
    key="pubic_mound",
    name="pubic mound",
    parent="groin",
    is_sexual=True,
)

BUTTOCKS = PartDefinition(
    key="buttocks",
    name="buttocks",
    parent="torso",
)

LEFT_BUTTOCK = PartDefinition(
    key="left_buttock",
    name="left buttock",
    plural="buttocks",
    parent="torso",
    side="left",
    is_paired=True,
)

RIGHT_BUTTOCK = PartDefinition(
    key="right_buttock",
    name="right buttock",
    plural="buttocks",
    parent="torso",
    side="right",
    is_paired=True,
)

ANUS = PartDefinition(
    key="anus",
    name="anus",
    parent="buttocks",
    is_sexual=True,
    is_exposable=True,
)

TAILHOLE = PartDefinition(
    key="tailhole",
    name="tailhole",
    parent="buttocks",
    is_optional=True,
    is_sexual=True,
    is_exposable=True,
    default_desc="The pucker beneath the tail.",
)


# =============================================================================
# ARMS - HUMANOID
# =============================================================================

LEFT_ARM = PartDefinition(
    key="left_arm",
    name="left arm",
    plural="arms",
    parent="left_shoulder",
    side="left",
    is_paired=True,
)

RIGHT_ARM = PartDefinition(
    key="right_arm",
    name="right arm",
    plural="arms",
    parent="right_shoulder",
    side="right",
    is_paired=True,
)

LEFT_UPPER_ARM = PartDefinition(
    key="left_upper_arm",
    name="left upper arm",
    parent="left_arm",
    side="left",
)

RIGHT_UPPER_ARM = PartDefinition(
    key="right_upper_arm",
    name="right upper arm",
    parent="right_arm",
    side="right",
)

LEFT_ELBOW = PartDefinition(
    key="left_elbow",
    name="left elbow",
    plural="elbows",
    parent="left_arm",
    side="left",
    is_paired=True,
)

RIGHT_ELBOW = PartDefinition(
    key="right_elbow",
    name="right elbow",
    plural="elbows",
    parent="right_arm",
    side="right",
    is_paired=True,
)

LEFT_FOREARM = PartDefinition(
    key="left_forearm",
    name="left forearm",
    parent="left_arm",
    side="left",
)

RIGHT_FOREARM = PartDefinition(
    key="right_forearm",
    name="right forearm",
    parent="right_arm",
    side="right",
)

LEFT_WRIST = PartDefinition(
    key="left_wrist",
    name="left wrist",
    plural="wrists",
    parent="left_forearm",
    side="left",
    is_paired=True,
)

RIGHT_WRIST = PartDefinition(
    key="right_wrist",
    name="right wrist",
    plural="wrists",
    parent="right_forearm",
    side="right",
    is_paired=True,
)


# =============================================================================
# HANDS
# =============================================================================

LEFT_HAND = PartDefinition(
    key="left_hand",
    name="left hand",
    plural="hands",
    parent="left_wrist",
    side="left",
    is_paired=True,
    functions=["manipulate"],
    obstructable_by=["mittens", "bondage", "restraint", "holding_item"],
    is_exposable=True,
)

RIGHT_HAND = PartDefinition(
    key="right_hand",
    name="right hand",
    plural="hands",
    parent="right_wrist",
    side="right",
    is_paired=True,
    functions=["manipulate"],
    obstructable_by=["mittens", "bondage", "restraint", "holding_item"],
    is_exposable=True,
)

LEFT_PALM = PartDefinition(
    key="left_palm",
    name="left palm",
    plural="palms",
    parent="left_hand",
    side="left",
    is_paired=True,
)

RIGHT_PALM = PartDefinition(
    key="right_palm",
    name="right palm",
    plural="palms",
    parent="right_hand",
    side="right",
    is_paired=True,
)

LEFT_FINGERS = PartDefinition(
    key="left_fingers",
    name="left fingers",
    plural="fingers",
    parent="left_hand",
    side="left",
    functions=["manipulate"],
    is_exposable=True,
)

RIGHT_FINGERS = PartDefinition(
    key="right_fingers",
    name="right fingers",
    plural="fingers",
    parent="right_hand",
    side="right",
    functions=["manipulate"],
    is_exposable=True,
)

LEFT_THUMB = PartDefinition(
    key="left_thumb",
    name="left thumb",
    plural="thumbs",
    parent="left_hand",
    side="left",
    is_paired=True,
)

RIGHT_THUMB = PartDefinition(
    key="right_thumb",
    name="right thumb",
    plural="thumbs",
    parent="right_hand",
    side="right",
    is_paired=True,
)

# Clawed hands
LEFT_CLAWS_HAND = PartDefinition(
    key="left_claws_hand",
    name="left hand claws",
    plural="claws",
    parent="left_fingers",
    side="left",
    is_optional=True,
)

RIGHT_CLAWS_HAND = PartDefinition(
    key="right_claws_hand",
    name="right hand claws",
    plural="claws",
    parent="right_fingers",
    side="right",
    is_optional=True,
)


# =============================================================================
# PAWS (Anthro/Feral)
# =============================================================================

LEFT_FOREPAW = PartDefinition(
    key="left_forepaw",
    name="left forepaw",
    plural="forepaws",
    parent="left_forearm",
    side="left",
    is_paired=True,
    is_optional=True,
    functions=["manipulate"],
    default_desc="A furred paw with paw pads.",
)

RIGHT_FOREPAW = PartDefinition(
    key="right_forepaw",
    name="right forepaw",
    plural="forepaws",
    parent="right_forearm",
    side="right",
    is_paired=True,
    is_optional=True,
    functions=["manipulate"],
)

LEFT_PAWPAD_FORE = PartDefinition(
    key="left_pawpad_fore",
    name="left forepaw pad",
    plural="paw pads",
    parent="left_forepaw",
    side="left",
    is_optional=True,
)

RIGHT_PAWPAD_FORE = PartDefinition(
    key="right_pawpad_fore",
    name="right forepaw pad",
    plural="paw pads",
    parent="right_forepaw",
    side="right",
    is_optional=True,
)

LEFT_CLAWS_FORE = PartDefinition(
    key="left_claws_fore",
    name="left forepaw claws",
    plural="claws",
    parent="left_forepaw",
    side="left",
    is_optional=True,
)

RIGHT_CLAWS_FORE = PartDefinition(
    key="right_claws_fore",
    name="right forepaw claws",
    plural="claws",
    parent="right_forepaw",
    side="right",
    is_optional=True,
)


# =============================================================================
# LEGS - HUMANOID (Plantigrade)
# =============================================================================

LEFT_LEG = PartDefinition(
    key="left_leg",
    name="left leg",
    plural="legs",
    parent="left_hip",
    side="left",
    is_paired=True,
)

RIGHT_LEG = PartDefinition(
    key="right_leg",
    name="right leg",
    plural="legs",
    parent="right_hip",
    side="right",
    is_paired=True,
)

LEFT_THIGH = PartDefinition(
    key="left_thigh",
    name="left thigh",
    parent="left_leg",
    side="left",
)

RIGHT_THIGH = PartDefinition(
    key="right_thigh",
    name="right thigh",
    parent="right_leg",
    side="right",
)

LEFT_KNEE = PartDefinition(
    key="left_knee",
    name="left knee",
    plural="knees",
    parent="left_leg",
    side="left",
    is_paired=True,
)

RIGHT_KNEE = PartDefinition(
    key="right_knee",
    name="right knee",
    plural="knees",
    parent="right_leg",
    side="right",
    is_paired=True,
)

LEFT_SHIN = PartDefinition(
    key="left_shin",
    name="left shin",
    parent="left_leg",
    side="left",
)

RIGHT_SHIN = PartDefinition(
    key="right_shin",
    name="right shin",
    parent="right_leg",
    side="right",
)

LEFT_CALF = PartDefinition(
    key="left_calf",
    name="left calf",
    parent="left_leg",
    side="left",
)

RIGHT_CALF = PartDefinition(
    key="right_calf",
    name="right calf",
    parent="right_leg",
    side="right",
)

LEFT_ANKLE = PartDefinition(
    key="left_ankle",
    name="left ankle",
    plural="ankles",
    parent="left_calf",
    side="left",
    is_paired=True,
)

RIGHT_ANKLE = PartDefinition(
    key="right_ankle",
    name="right ankle",
    plural="ankles",
    parent="right_calf",
    side="right",
    is_paired=True,
)


# =============================================================================
# FEET - HUMANOID
# =============================================================================

LEFT_FOOT = PartDefinition(
    key="left_foot",
    name="left foot",
    plural="feet",
    parent="left_ankle",
    side="left",
    is_paired=True,
    functions=["locomotion"],
    obstructable_by=["shackles", "bondage", "injury"],
)

RIGHT_FOOT = PartDefinition(
    key="right_foot",
    name="right foot",
    plural="feet",
    parent="right_ankle",
    side="right",
    is_paired=True,
    functions=["locomotion"],
    obstructable_by=["shackles", "bondage", "injury"],
)

LEFT_SOLE = PartDefinition(
    key="left_sole",
    name="left sole",
    plural="soles",
    parent="left_foot",
    side="left",
    is_paired=True,
)

RIGHT_SOLE = PartDefinition(
    key="right_sole",
    name="right sole",
    plural="soles",
    parent="right_foot",
    side="right",
    is_paired=True,
)

LEFT_HEEL = PartDefinition(
    key="left_heel",
    name="left heel",
    plural="heels",
    parent="left_foot",
    side="left",
    is_paired=True,
)

RIGHT_HEEL = PartDefinition(
    key="right_heel",
    name="right heel",
    plural="heels",
    parent="right_foot",
    side="right",
    is_paired=True,
)

LEFT_TOES = PartDefinition(
    key="left_toes",
    name="left toes",
    plural="toes",
    parent="left_foot",
    side="left",
)

RIGHT_TOES = PartDefinition(
    key="right_toes",
    name="right toes",
    plural="toes",
    parent="right_foot",
    side="right",
)


# =============================================================================
# LEGS/FEET - DIGITIGRADE
# =============================================================================

LEFT_LEG_DIGI = PartDefinition(
    key="left_leg_digi",
    name="left digitigrade leg",
    plural="digitigrade legs",
    parent="left_hip",
    side="left",
    is_paired=True,
    is_optional=True,
    default_desc="A digitigrade leg with reversed knee joint.",
)

RIGHT_LEG_DIGI = PartDefinition(
    key="right_leg_digi",
    name="right digitigrade leg",
    plural="digitigrade legs",
    parent="right_hip",
    side="right",
    is_paired=True,
    is_optional=True,
)

LEFT_HINDPAW = PartDefinition(
    key="left_hindpaw",
    name="left hindpaw",
    plural="hindpaws",
    parent="left_leg_digi",
    side="left",
    is_paired=True,
    is_optional=True,
    functions=["locomotion"],
    default_desc="A furred paw with tough pads.",
)

RIGHT_HINDPAW = PartDefinition(
    key="right_hindpaw",
    name="right hindpaw",
    plural="hindpaws",
    parent="right_leg_digi",
    side="right",
    is_paired=True,
    is_optional=True,
    functions=["locomotion"],
)

LEFT_PAWPAD_HIND = PartDefinition(
    key="left_pawpad_hind",
    name="left hindpaw pad",
    plural="paw pads",
    parent="left_hindpaw",
    side="left",
    is_optional=True,
)

RIGHT_PAWPAD_HIND = PartDefinition(
    key="right_pawpad_hind",
    name="right hindpaw pad",
    plural="paw pads",
    parent="right_hindpaw",
    side="right",
    is_optional=True,
)

LEFT_CLAWS_HIND = PartDefinition(
    key="left_claws_hind",
    name="left hindpaw claws",
    plural="claws",
    parent="left_hindpaw",
    side="left",
    is_optional=True,
)

RIGHT_CLAWS_HIND = PartDefinition(
    key="right_claws_hind",
    name="right hindpaw claws",
    plural="claws",
    parent="right_hindpaw",
    side="right",
    is_optional=True,
)


# =============================================================================
# HOOVES
# =============================================================================

LEFT_HOOF_FORE = PartDefinition(
    key="left_hoof_fore",
    name="left fore hoof",
    plural="hooves",
    parent="left_forearm",
    side="left",
    is_paired=True,
    is_optional=True,
    functions=["locomotion"],
)

RIGHT_HOOF_FORE = PartDefinition(
    key="right_hoof_fore",
    name="right fore hoof",
    plural="hooves",
    parent="right_forearm",
    side="right",
    is_paired=True,
    is_optional=True,
    functions=["locomotion"],
)

LEFT_HOOF_HIND = PartDefinition(
    key="left_hoof_hind",
    name="left hind hoof",
    plural="hooves",
    parent="left_leg",
    side="left",
    is_paired=True,
    is_optional=True,
    functions=["locomotion"],
)

RIGHT_HOOF_HIND = PartDefinition(
    key="right_hoof_hind",
    name="right hind hoof",
    plural="hooves",
    parent="right_leg",
    side="right",
    is_paired=True,
    is_optional=True,
    functions=["locomotion"],
)


# =============================================================================
# TAILS
# =============================================================================

TAIL = PartDefinition(
    key="tail",
    name="tail",
    parent="lower_back",
    is_optional=True,
)

TAIL_CANINE = PartDefinition(
    key="tail_canine",
    name="canine tail",
    parent="lower_back",
    is_optional=True,
    default_desc="A bushy, expressive canine tail.",
)

TAIL_FELINE = PartDefinition(
    key="tail_feline",
    name="feline tail",
    parent="lower_back",
    is_optional=True,
    default_desc="A long, flexible feline tail.",
)

TAIL_EQUINE = PartDefinition(
    key="tail_equine",
    name="equine tail",
    parent="lower_back",
    is_optional=True,
    default_desc="A long, flowing tail.",
)

TAIL_LAPINE = PartDefinition(
    key="tail_lapine",
    name="cotton tail",
    parent="lower_back",
    is_optional=True,
    default_desc="A small, fluffy cotton tail.",
)

TAIL_VULPINE = PartDefinition(
    key="tail_vulpine",
    name="fox tail",
    parent="lower_back",
    is_optional=True,
    default_desc="A large, fluffy fox tail.",
)

TAIL_REPTILE = PartDefinition(
    key="tail_reptile",
    name="reptilian tail",
    parent="lower_back",
    is_optional=True,
    default_desc="A thick, scaled tail.",
)

TAIL_DEMON = PartDefinition(
    key="tail_demon",
    name="demon tail",
    parent="lower_back",
    is_optional=True,
    default_desc="A long, pointed tail with a spade tip.",
)

TAIL_PREHENSILE = PartDefinition(
    key="tail_prehensile",
    name="prehensile tail",
    parent="lower_back",
    is_optional=True,
    functions=["manipulate"],
    default_desc="A strong, prehensile tail capable of gripping.",
)


# =============================================================================
# WINGS
# =============================================================================

WINGS = PartDefinition(
    key="wings",
    name="wings",
    parent="back",
    is_optional=True,
    is_paired=True,
)

LEFT_WING = PartDefinition(
    key="left_wing",
    name="left wing",
    plural="wings",
    parent="back",
    side="left",
    is_paired=True,
    is_optional=True,
)

RIGHT_WING = PartDefinition(
    key="right_wing",
    name="right wing",
    plural="wings",
    parent="back",
    side="right",
    is_paired=True,
    is_optional=True,
)

WINGS_FEATHERED = PartDefinition(
    key="wings_feathered",
    name="feathered wings",
    parent="back",
    is_optional=True,
    functions=["flight"],
    default_desc="Large, feathered wings.",
)

WINGS_BAT = PartDefinition(
    key="wings_bat",
    name="bat wings",
    parent="back",
    is_optional=True,
    functions=["flight"],
    default_desc="Leathery, bat-like wings.",
)

WINGS_INSECT = PartDefinition(
    key="wings_insect",
    name="insect wings",
    parent="back",
    is_optional=True,
    functions=["flight"],
    default_desc="Gossamer insect wings.",
)

WINGS_DRAGON = PartDefinition(
    key="wings_dragon",
    name="dragon wings",
    parent="back",
    is_optional=True,
    functions=["flight"],
    default_desc="Massive, scaled dragon wings.",
)


# =============================================================================
# SERPENTINE LOWER BODY
# =============================================================================

SERPENT_BODY = PartDefinition(
    key="serpent_body",
    name="serpent body",
    parent="waist",
    is_optional=True,
    functions=["locomotion"],
    default_desc="A long, powerful serpent body.",
)

SERPENT_COILS = PartDefinition(
    key="serpent_coils",
    name="coils",
    parent="serpent_body",
    is_optional=True,
    default_desc="Powerful coils capable of constriction.",
)

SERPENT_TIP = PartDefinition(
    key="serpent_tip",
    name="tail tip",
    parent="serpent_body",
    is_optional=True,
)


# =============================================================================
# TAUROID LOWER BODY
# =============================================================================

TAUROID_BODY = PartDefinition(
    key="tauroid_body",
    name="lower body",
    parent="waist",
    is_optional=True,
    default_desc="A powerful quadruped lower body.",
)

TAUROID_BARREL = PartDefinition(
    key="tauroid_barrel",
    name="barrel",
    parent="tauroid_body",
    is_optional=True,
    default_desc="The broad barrel of the lower body.",
)

TAUROID_FORELEGS = PartDefinition(
    key="tauroid_forelegs",
    name="forelegs",
    parent="tauroid_body",
    is_optional=True,
    functions=["locomotion"],
)

TAUROID_HINDLEGS = PartDefinition(
    key="tauroid_hindlegs",
    name="hindlegs",
    parent="tauroid_body",
    is_optional=True,
    functions=["locomotion"],
)

TAUROID_HINDQUARTERS = PartDefinition(
    key="tauroid_hindquarters",
    name="hindquarters",
    parent="tauroid_body",
    is_optional=True,
)


# =============================================================================
# AQUATIC LOWER BODY
# =============================================================================

FISH_TAIL = PartDefinition(
    key="fish_tail",
    name="fish tail",
    parent="waist",
    is_optional=True,
    functions=["locomotion"],
    default_desc="A powerful, scaled fish tail.",
)

TAIL_FIN = PartDefinition(
    key="tail_fin",
    name="tail fin",
    parent="fish_tail",
    is_optional=True,
)

DORSAL_FIN = PartDefinition(
    key="dorsal_fin",
    name="dorsal fin",
    parent="back",
    is_optional=True,
)

PECTORAL_FINS = PartDefinition(
    key="pectoral_fins",
    name="pectoral fins",
    parent="torso",
    is_optional=True,
    is_paired=True,
)


# =============================================================================
# GENITALIA - MALE
# =============================================================================

# Generic penis
PENIS = PartDefinition(
    key="penis",
    name="penis",
    parent="groin",
    is_optional=True,
    is_sexual=True,
    is_exposable=True,
    size_options=["tiny", "small", "average", "large", "huge", "massive"],
)

# Type-specific penises
PENIS_HUMAN = PartDefinition(
    key="penis_human",
    name="penis",
    parent="groin",
    is_optional=True,
    is_sexual=True,
    is_exposable=True,
    default_desc="A human-type penis.",
    size_options=["small", "average", "large", "huge"],
)

PENIS_CANINE = PartDefinition(
    key="penis_canine",
    name="canine penis",
    parent="groin",
    is_optional=True,
    is_sexual=True,
    is_exposable=True,
    default_desc="A tapered canine penis with a knot at the base.",
    size_options=["small", "average", "large", "huge"],
)

PENIS_EQUINE = PartDefinition(
    key="penis_equine",
    name="equine penis",
    parent="groin",
    is_optional=True,
    is_sexual=True,
    is_exposable=True,
    default_desc="A large, flared equine penis.",
    size_options=["large", "huge", "massive"],
)

PENIS_FELINE = PartDefinition(
    key="penis_feline",
    name="feline penis",
    parent="groin",
    is_optional=True,
    is_sexual=True,
    is_exposable=True,
    default_desc="A barbed feline penis.",
    size_options=["small", "average", "large"],
)

PENIS_REPTILE = PartDefinition(
    key="penis_reptile",
    name="reptilian penis",
    parent="groin",
    is_optional=True,
    is_sexual=True,
    is_exposable=True,
    default_desc="A smooth, tapered reptilian penis.",
)

HEMIPENES = PartDefinition(
    key="hemipenes",
    name="hemipenes",
    parent="groin",
    is_optional=True,
    is_sexual=True,
    is_exposable=True,
    default_desc="Twin reptilian hemipenes.",
)

PENIS_DOLPHIN = PartDefinition(
    key="penis_dolphin",
    name="dolphin penis",
    parent="groin",
    is_optional=True,
    is_sexual=True,
    is_exposable=True,
    default_desc="A prehensile dolphin penis.",
)

PENIS_TENTACLE = PartDefinition(
    key="penis_tentacle",
    name="tentacle cock",
    parent="groin",
    is_optional=True,
    is_sexual=True,
    is_exposable=True,
    default_desc="A writhing tentacle-like phallus.",
)

# Supporting male parts
KNOT = PartDefinition(
    key="knot",
    name="knot",
    parent="penis_canine",
    is_optional=True,
    is_sexual=True,
    default_desc="A swollen knot at the base.",
)

SHEATH = PartDefinition(
    key="sheath",
    name="sheath",
    parent="groin",
    is_optional=True,
    is_sexual=True,
    default_desc="A protective sheath.",
)

TESTICLES = PartDefinition(
    key="testicles",
    name="testicles",
    parent="groin",
    is_optional=True,
    is_sexual=True,
    size_options=["small", "average", "large", "huge"],
)

SCROTUM = PartDefinition(
    key="scrotum",
    name="scrotum",
    parent="groin",
    is_optional=True,
    is_sexual=True,
)

FORESKIN = PartDefinition(
    key="foreskin",
    name="foreskin",
    parent="penis",
    is_optional=True,
    is_sexual=True,
)

GLANS = PartDefinition(
    key="glans",
    name="glans",
    parent="penis",
    is_optional=True,
    is_sexual=True,
)

URETHRA_MALE = PartDefinition(
    key="urethra_male",
    name="urethra",
    parent="penis",
    is_internal=True,
    is_sexual=True,
)


# =============================================================================
# GENITALIA - FEMALE
# =============================================================================

VULVA = PartDefinition(
    key="vulva",
    name="vulva",
    parent="groin",
    is_optional=True,
    is_sexual=True,
    is_exposable=True,
)

VAGINA = PartDefinition(
    key="vagina",
    name="vagina",
    parent="vulva",
    is_optional=True,
    is_sexual=True,
    is_exposable=True,
)

LABIA = PartDefinition(
    key="labia",
    name="labia",
    parent="vulva",
    is_optional=True,
    is_sexual=True,
)

CLITORIS = PartDefinition(
    key="clitoris",
    name="clitoris",
    parent="vulva",
    is_optional=True,
    is_sexual=True,
)

CLITORAL_HOOD = PartDefinition(
    key="clitoral_hood",
    name="clitoral hood",
    parent="vulva",
    is_optional=True,
    is_sexual=True,
)

URETHRA_FEMALE = PartDefinition(
    key="urethra_female",
    name="urethra",
    parent="vulva",
    is_internal=True,
    is_sexual=True,
)

# Internal
CERVIX = PartDefinition(
    key="cervix",
    name="cervix",
    parent="vagina",
    is_internal=True,
    is_sexual=True,
)

WOMB = PartDefinition(
    key="womb",
    name="womb",
    parent="cervix",
    is_internal=True,
    is_sexual=True,
)

OVARIES = PartDefinition(
    key="ovaries",
    name="ovaries",
    parent="womb",
    is_internal=True,
    is_sexual=True,
)


# =============================================================================
# GENITALIA - CLOACA
# =============================================================================

CLOACA = PartDefinition(
    key="cloaca",
    name="cloaca",
    parent="groin",
    is_optional=True,
    is_sexual=True,
    is_exposable=True,
    default_desc="A multi-purpose cloaca.",
)

VENT = PartDefinition(
    key="vent",
    name="vent",
    parent="groin",
    is_optional=True,
    is_sexual=True,
    is_exposable=True,
    default_desc="A genital vent.",
)


# =============================================================================
# INSECTOID PARTS
# =============================================================================

EXOSKELETON = PartDefinition(
    key="exoskeleton",
    name="exoskeleton",
    parent=None,
    is_optional=True,
    is_removable=False,
    default_desc="A hard chitin exoskeleton.",
)

MANDIBLES = PartDefinition(
    key="mandibles",
    name="mandibles",
    parent="head",
    is_optional=True,
    functions=["consume"],
)

COMPOUND_EYES = PartDefinition(
    key="compound_eyes",
    name="compound eyes",
    parent="head",
    is_optional=True,
    functions=["sight"],
)

OVIPOSITOR = PartDefinition(
    key="ovipositor",
    name="ovipositor",
    parent="groin",
    is_optional=True,
    is_sexual=True,
)

STINGER = PartDefinition(
    key="stinger",
    name="stinger",
    parent="tail",
    is_optional=True,
)


# =============================================================================
# TENTACLES
# =============================================================================

TENTACLES = PartDefinition(
    key="tentacles",
    name="tentacles",
    parent="torso",
    is_optional=True,
    functions=["manipulate", "locomotion"],
)

TENTACLE_ARMS = PartDefinition(
    key="tentacle_arms",
    name="tentacle arms",
    parent="torso",
    is_optional=True,
    functions=["manipulate"],
)

TENTACLE_LOWER = PartDefinition(
    key="tentacle_lower",
    name="lower tentacles",
    parent="waist",
    is_optional=True,
    functions=["locomotion"],
)

TENTACLE_FACE = PartDefinition(
    key="tentacle_face",
    name="face tentacles",
    parent="face",
    is_optional=True,
)


# =============================================================================
# PART REGISTRY
# =============================================================================

PART_REGISTRY: Dict[str, PartDefinition] = {}

# Auto-populate registry from module globals
import sys
_current_module = sys.modules[__name__]
for _name in dir(_current_module):
    _obj = getattr(_current_module, _name)
    if isinstance(_obj, PartDefinition):
        PART_REGISTRY[_obj.key] = _obj


def get_part(key: str) -> Optional[PartDefinition]:
    """Look up a part definition by key."""
    return PART_REGISTRY.get(key)


def get_parts_with_function(function: str) -> List[PartDefinition]:
    """Get all parts that provide a specific function."""
    return [p for p in PART_REGISTRY.values() if function in p.functions]


def get_children_of(parent_key: str) -> List[PartDefinition]:
    """Get all parts that are children of the given part."""
    return [p for p in PART_REGISTRY.values() if p.parent == parent_key]


def list_optional_parts() -> List[str]:
    """List all optional part keys."""
    return [k for k, v in PART_REGISTRY.items() if v.is_optional]


def list_sexual_parts() -> List[str]:
    """List all sexual part keys."""
    return [k for k, v in PART_REGISTRY.items() if v.is_sexual]
