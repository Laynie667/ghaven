"""
Body Structures - Base

BodyStructure defines the fundamental skeleton and locomotion type.
This is the first layer of body composition.

Structure types:
    - Bipedal (plantigrade) - walks upright on flat feet
    - Bipedal (digitigrade) - walks upright on toes  
    - Quadruped - four legs
    - Tauroid - humanoid upper, quadruped lower
    - Serpentine - humanoid upper, snake lower
    - Aquatic - humanoid upper, fish lower
    - Avian - bird-like with wings for arms
    - Tentacled - tentacles instead of limbs
"""

from dataclasses import dataclass, field
from typing import List, Dict, Set, Optional


@dataclass
class BodyStructure:
    """
    Base class for body structures.
    
    Defines:
        - Which parts this structure HAS
        - Locomotion type
        - Manipulation type
        - What parts can be ADDED or REPLACED
    """
    
    key: str                          # Structure identifier
    name: str                         # Display name
    description: str = ""             # Structure description
    
    # Core parts this structure includes
    # These are the part keys from parts.py
    parts: List[str] = field(default_factory=list)
    
    # Locomotion
    locomotion_type: str = "bipedal"
    # Types: bipedal, quadruped, slither, swim, fly, float, none
    
    locomotion_parts: List[str] = field(default_factory=list)
    # Which parts provide locomotion
    
    # Manipulation
    manipulation_type: str = "hands"
    # Types: hands, paws, hooves, tentacles, none
    
    manipulation_parts: List[str] = field(default_factory=list)
    # Which parts provide manipulation
    
    # What parts can be replaced with alternatives
    # Example: {"face": ["muzzle", "muzzle_canine", "muzzle_feline"]}
    replaceable_parts: Dict[str, List[str]] = field(default_factory=dict)
    
    # Parts that are excluded (can't have these)
    excluded_parts: List[str] = field(default_factory=list)
    
    # Valid add-ons for this structure
    valid_addons: List[str] = field(default_factory=list)


# =============================================================================
# CORE HUMANOID PARTS
# Shared by most humanoid structures
# =============================================================================

CORE_HEAD_PARTS = [
    "head", "skull", "face",
    "left_eye", "right_eye",
    "left_ear", "right_ear",
    "nose", "mouth", "tongue", "lips", "teeth",
    "neck", "throat", "nape",
]

CORE_TORSO_PARTS = [
    "torso",
    "chest", "back",
    "left_shoulder", "right_shoulder",
    "stomach", "belly", "navel",
    "waist", "hips", "left_hip", "right_hip",
    "lower_back",
    "buttocks", "left_buttock", "right_buttock",
    "groin",
]

CORE_ARM_PARTS = [
    "left_arm", "right_arm",
    "left_upper_arm", "right_upper_arm",
    "left_elbow", "right_elbow",
    "left_forearm", "right_forearm",
    "left_wrist", "right_wrist",
    "left_hand", "right_hand",
    "left_palm", "right_palm",
    "left_fingers", "right_fingers",
    "left_thumb", "right_thumb",
]

CORE_LEG_PARTS_PLANTIGRADE = [
    "left_leg", "right_leg",
    "left_thigh", "right_thigh",
    "left_knee", "right_knee",
    "left_shin", "right_shin",
    "left_calf", "right_calf",
    "left_ankle", "right_ankle",
    "left_foot", "right_foot",
    "left_sole", "right_sole",
    "left_heel", "right_heel",
    "left_toes", "right_toes",
]

CORE_LEG_PARTS_DIGITIGRADE = [
    "left_leg_digi", "right_leg_digi",
    "left_thigh", "right_thigh",
    "left_hindpaw", "right_hindpaw",
    "left_pawpad_hind", "right_pawpad_hind",
    "left_claws_hind", "right_claws_hind",
]


# =============================================================================
# STRUCTURE DEFINITIONS
# =============================================================================

BIPEDAL_PLANTIGRADE = BodyStructure(
    key="bipedal_plantigrade",
    name="Bipedal (Plantigrade)",
    description="Two-legged, walks upright on flat feet. Humans, elves, orcs.",
    
    parts=(
        CORE_HEAD_PARTS +
        CORE_TORSO_PARTS +
        CORE_ARM_PARTS +
        CORE_LEG_PARTS_PLANTIGRADE +
        ["anus"]
    ),
    
    locomotion_type="bipedal",
    locomotion_parts=["left_foot", "right_foot"],
    
    manipulation_type="hands",
    manipulation_parts=["left_hand", "right_hand"],
    
    replaceable_parts={
        "face": ["muzzle", "muzzle_canine", "muzzle_feline", "muzzle_equine", "snout"],
        "left_ear": ["left_ear_pointed", "left_ear_canine", "left_ear_feline", "left_ear_equine", "left_ear_lapine"],
        "right_ear": ["right_ear_pointed", "right_ear_canine", "right_ear_feline", "right_ear_equine", "right_ear_lapine"],
    },
    
    valid_addons=[
        "hair", "mane", "horns", "horns_ram", "horns_demon", "antlers",
        "fangs", "tusks",
        "tail", "tail_canine", "tail_feline", "tail_demon",
        "wings", "wings_feathered", "wings_bat", "wings_dragon",
        "left_claws_hand", "right_claws_hand",
    ],
)


BIPEDAL_DIGITIGRADE = BodyStructure(
    key="bipedal_digitigrade",
    name="Bipedal (Digitigrade)",
    description="Two-legged, walks upright on toes/paws. Anthro canines, felines.",
    
    parts=(
        CORE_HEAD_PARTS +
        CORE_TORSO_PARTS +
        CORE_ARM_PARTS +
        CORE_LEG_PARTS_DIGITIGRADE +
        ["anus", "tailhole"]
    ),
    
    locomotion_type="bipedal",
    locomotion_parts=["left_hindpaw", "right_hindpaw"],
    
    manipulation_type="hands",
    manipulation_parts=["left_hand", "right_hand"],
    
    replaceable_parts={
        "face": ["muzzle", "muzzle_canine", "muzzle_feline", "muzzle_equine", "snout"],
        "left_ear": ["left_ear_canine", "left_ear_feline", "left_ear_equine", "left_ear_lapine"],
        "right_ear": ["right_ear_canine", "right_ear_feline", "right_ear_equine", "right_ear_lapine"],
        "left_hand": ["left_forepaw"],
        "right_hand": ["right_forepaw"],
    },
    
    excluded_parts=[
        # No human-style feet
        "left_foot", "right_foot",
        "left_sole", "right_sole",
        "left_heel", "right_heel",
        "left_toes", "right_toes",
        "left_ankle", "right_ankle",
    ],
    
    valid_addons=[
        "hair", "mane", "horns",
        "fangs",
        "scruff",
        "tail_canine", "tail_feline", "tail_vulpine", "tail_lapine",
        "left_claws_hand", "right_claws_hand",
        "left_claws_fore", "right_claws_fore",
    ],
)


BIPEDAL_DIGITIGRADE_PAWS = BodyStructure(
    key="bipedal_digitigrade_paws",
    name="Bipedal Digitigrade (Paws)",
    description="Two-legged digitigrade with paws instead of hands.",
    
    parts=(
        CORE_HEAD_PARTS +
        CORE_TORSO_PARTS +
        [  # Arms with paws
            "left_arm", "right_arm",
            "left_upper_arm", "right_upper_arm",
            "left_elbow", "right_elbow",
            "left_forearm", "right_forearm",
            "left_forepaw", "right_forepaw",
            "left_pawpad_fore", "right_pawpad_fore",
            "left_claws_fore", "right_claws_fore",
        ] +
        CORE_LEG_PARTS_DIGITIGRADE +
        ["anus", "tailhole"]
    ),
    
    locomotion_type="bipedal",
    locomotion_parts=["left_hindpaw", "right_hindpaw"],
    
    manipulation_type="paws",
    manipulation_parts=["left_forepaw", "right_forepaw"],
    
    replaceable_parts={
        "face": ["muzzle", "muzzle_canine", "muzzle_feline", "snout"],
        "left_ear": ["left_ear_canine", "left_ear_feline"],
        "right_ear": ["right_ear_canine", "right_ear_feline"],
    },
    
    excluded_parts=[
        "left_hand", "right_hand",
        "left_fingers", "right_fingers",
        "left_foot", "right_foot",
    ],
    
    valid_addons=[
        "mane", "scruff",
        "fangs",
        "tail_canine", "tail_feline", "tail_vulpine",
    ],
)


QUADRUPED = BodyStructure(
    key="quadruped",
    name="Quadruped",
    description="Four-legged, no humanoid upper body. Dogs, wolves, horses.",
    
    parts=[
        # Head
        "head", "skull",
        "left_eye", "right_eye",
        "nose", "mouth", "tongue", "teeth",
        "neck", "throat", "nape", "scruff",
        
        # Body (no humanoid torso)
        "torso", "chest", "back", "lower_back",
        "stomach", "belly",
        "hips",
        "buttocks",
        "groin",
        
        # Four legs with paws
        "left_forepaw", "right_forepaw",
        "left_pawpad_fore", "right_pawpad_fore",
        "left_claws_fore", "right_claws_fore",
        "left_hindpaw", "right_hindpaw",
        "left_pawpad_hind", "right_pawpad_hind",
        "left_claws_hind", "right_claws_hind",
        
        "anus", "tailhole",
    ],
    
    locomotion_type="quadruped",
    locomotion_parts=["left_forepaw", "right_forepaw", "left_hindpaw", "right_hindpaw"],
    
    manipulation_type="none",
    manipulation_parts=[],
    
    replaceable_parts={
        "left_forepaw": ["left_hoof_fore"],
        "right_forepaw": ["right_hoof_fore"],
        "left_hindpaw": ["left_hoof_hind"],
        "right_hindpaw": ["right_hoof_hind"],
    },
    
    excluded_parts=[
        # No humanoid parts
        "face", "shoulders", "waist",
        "left_arm", "right_arm",
        "left_hand", "right_hand",
        "left_leg", "right_leg",
        "left_foot", "right_foot",
    ],
    
    valid_addons=[
        "mane", "muzzle", "muzzle_canine", "muzzle_feline", "muzzle_equine",
        "left_ear_canine", "right_ear_canine",
        "left_ear_feline", "right_ear_feline",
        "left_ear_equine", "right_ear_equine",
        "tail_canine", "tail_feline", "tail_equine",
        "fangs",
    ],
)


QUADRUPED_HOOVED = BodyStructure(
    key="quadruped_hooved",
    name="Quadruped (Hooved)",
    description="Four-legged with hooves. Horses, deer, cattle.",
    
    parts=[
        # Head
        "head", "skull",
        "left_eye", "right_eye",
        "nose", "mouth", "tongue", "teeth",
        "neck", "throat", "nape",
        
        # Body
        "torso", "chest", "back", "lower_back",
        "stomach", "belly",
        "hips",
        "buttocks",
        "groin",
        
        # Four legs with hooves
        "left_hoof_fore", "right_hoof_fore",
        "left_hoof_hind", "right_hoof_hind",
        
        "anus", "tailhole",
    ],
    
    locomotion_type="quadruped",
    locomotion_parts=["left_hoof_fore", "right_hoof_fore", "left_hoof_hind", "right_hoof_hind"],
    
    manipulation_type="none",
    manipulation_parts=[],
    
    valid_addons=[
        "mane", "muzzle_equine",
        "left_ear_equine", "right_ear_equine",
        "tail_equine",
        "horns", "antlers",
    ],
)


TAUROID = BodyStructure(
    key="tauroid",
    name="Tauroid",
    description="Humanoid upper body, quadruped lower body. Centaurs, driders.",
    
    parts=(
        CORE_HEAD_PARTS +
        CORE_TORSO_PARTS +
        CORE_ARM_PARTS +
        [
            # Tauroid lower body
            "tauroid_body", "tauroid_barrel",
            "tauroid_forelegs", "tauroid_hindlegs",
            "tauroid_hindquarters",
            "left_hoof_fore", "right_hoof_fore",
            "left_hoof_hind", "right_hoof_hind",
            "anus", "tailhole",
        ]
    ),
    
    locomotion_type="quadruped",
    locomotion_parts=["left_hoof_fore", "right_hoof_fore", "left_hoof_hind", "right_hoof_hind"],
    
    manipulation_type="hands",
    manipulation_parts=["left_hand", "right_hand"],
    
    replaceable_parts={
        "left_hoof_fore": ["left_forepaw"],
        "right_hoof_fore": ["right_forepaw"],
        "left_hoof_hind": ["left_hindpaw"],
        "right_hoof_hind": ["right_hindpaw"],
    },
    
    excluded_parts=[
        # No humanoid legs
        "left_leg", "right_leg",
        "left_thigh", "right_thigh",
        "left_knee", "right_knee",
        "left_shin", "right_shin",
        "left_calf", "right_calf",
        "left_ankle", "right_ankle",
        "left_foot", "right_foot",
    ],
    
    valid_addons=[
        "hair", "mane",
        "horns", "antlers",
        "tail_equine", "tail_canine",
        "left_ear_pointed", "right_ear_pointed",
        "left_ear_equine", "right_ear_equine",
    ],
)


SERPENTINE = BodyStructure(
    key="serpentine",
    name="Serpentine",
    description="Humanoid upper body, snake lower body. Lamia, nagas.",
    
    parts=(
        CORE_HEAD_PARTS +
        CORE_TORSO_PARTS +
        CORE_ARM_PARTS +
        [
            # Serpent lower body
            "serpent_body", "serpent_coils", "serpent_tip",
            "anus",
        ]
    ),
    
    locomotion_type="slither",
    locomotion_parts=["serpent_body"],
    
    manipulation_type="hands",
    manipulation_parts=["left_hand", "right_hand"],
    
    replaceable_parts={
        "tongue": ["tongue_forked"],
    },
    
    excluded_parts=[
        # No legs
        "hips", "left_hip", "right_hip",
        "buttocks", "left_buttock", "right_buttock",
        "left_leg", "right_leg",
        "left_foot", "right_foot",
    ],
    
    valid_addons=[
        "hair", "horns", "fangs",
        "left_ear_pointed", "right_ear_pointed",
        "tail_reptile",
    ],
)


AQUATIC = BodyStructure(
    key="aquatic",
    name="Aquatic",
    description="Humanoid upper body, fish tail. Merfolk.",
    
    parts=(
        CORE_HEAD_PARTS +
        CORE_TORSO_PARTS +
        CORE_ARM_PARTS +
        [
            # Fish lower body
            "fish_tail", "tail_fin",
            "anus",
            # Aquatic features
            "gills",
        ]
    ),
    
    locomotion_type="swim",
    locomotion_parts=["fish_tail"],
    
    manipulation_type="hands",
    manipulation_parts=["left_hand", "right_hand"],
    
    excluded_parts=[
        "hips", "left_hip", "right_hip",
        "buttocks", "left_buttock", "right_buttock",
        "left_leg", "right_leg",
        "left_foot", "right_foot",
    ],
    
    valid_addons=[
        "hair",
        "dorsal_fin", "pectoral_fins",
        "left_ear_pointed", "right_ear_pointed",
    ],
)


AVIAN = BodyStructure(
    key="avian",
    name="Avian",
    description="Bird-like with wings for arms. Harpies.",
    
    parts=(
        CORE_HEAD_PARTS +
        [
            # Body
            "torso", "chest", "back",
            "stomach", "belly",
            "waist", "hips",
            "buttocks",
            "groin",
        ] +
        [
            # Wings instead of arms
            "wings_feathered",
            "left_wing", "right_wing",
        ] +
        [
            # Taloned legs
            "left_leg", "right_leg",
            "left_thigh", "right_thigh",
            "left_knee", "right_knee",
            "left_shin", "right_shin",
            "left_foot", "right_foot",  # Talons
            "left_toes", "right_toes",
        ] +
        ["anus"]
    ),
    
    locomotion_type="fly",
    locomotion_parts=["wings_feathered", "left_foot", "right_foot"],
    
    manipulation_type="none",
    manipulation_parts=[],  # No hands
    
    replaceable_parts={
        "mouth": ["beak"],
    },
    
    excluded_parts=[
        "left_arm", "right_arm",
        "left_hand", "right_hand",
    ],
    
    valid_addons=[
        "hair", "crest",
        "tail",
    ],
)


TENTACLED = BodyStructure(
    key="tentacled",
    name="Tentacled",
    description="Humanoid with tentacles. Mind flayers, tentacle beings.",
    
    parts=(
        CORE_HEAD_PARTS +
        CORE_TORSO_PARTS +
        [
            # Tentacles instead of limbs
            "tentacles",
            "tentacle_arms",
            "tentacle_lower",
        ] +
        ["anus"]
    ),
    
    locomotion_type="float",
    locomotion_parts=["tentacle_lower"],
    
    manipulation_type="tentacles",
    manipulation_parts=["tentacle_arms"],
    
    excluded_parts=[
        "left_arm", "right_arm",
        "left_hand", "right_hand",
        "left_leg", "right_leg",
        "left_foot", "right_foot",
    ],
    
    valid_addons=[
        "tentacle_face",
    ],
)


# =============================================================================
# STRUCTURE REGISTRY
# =============================================================================

STRUCTURE_REGISTRY: Dict[str, BodyStructure] = {
    "bipedal_plantigrade": BIPEDAL_PLANTIGRADE,
    "bipedal_digitigrade": BIPEDAL_DIGITIGRADE,
    "bipedal_digitigrade_paws": BIPEDAL_DIGITIGRADE_PAWS,
    "quadruped": QUADRUPED,
    "quadruped_hooved": QUADRUPED_HOOVED,
    "tauroid": TAUROID,
    "serpentine": SERPENTINE,
    "aquatic": AQUATIC,
    "avian": AVIAN,
    "tentacled": TENTACLED,
}


def get_structure(key: str) -> Optional[BodyStructure]:
    """Get a body structure by key."""
    return STRUCTURE_REGISTRY.get(key)


def list_structures() -> List[str]:
    """List all structure keys."""
    return list(STRUCTURE_REGISTRY.keys())


def get_structures_by_locomotion(locomotion_type: str) -> List[BodyStructure]:
    """Get all structures with a specific locomotion type."""
    return [s for s in STRUCTURE_REGISTRY.values() if s.locomotion_type == locomotion_type]
