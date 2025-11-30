"""
Position Library
================

Comprehensive collection of predefined positions.

Organized by category:
- Penetrative (missionary, doggy, etc.)
- Oral (blowjob, cunnilingus, 69)
- Manual (handjob, fingering)
- Multi-person (threesome configurations)
- Furniture-specific (bent over table, against wall)
- Bondage/restraint (stocks, suspension)
- Intimate/non-sexual (cuddling, lap sitting)
"""

from typing import Dict, Set, Optional, List
from .core import BodyZone, Posture, Mobility, FurnitureType
from .definitions import (
    PositionDefinition,
    PositionRequirement,
    SlotDefinition,
    make_slot,
    FRONT_UPPER, FRONT_LOWER, FRONT_FULL,
    BACK_UPPER, BACK_LOWER, BACK_FULL,
    BEHIND_ACCESS, INTIMATE_FRONT, ALL_ZONES,
    ORAL_GIVER_ACCESS, ORAL_RECEIVER_ACCESS,
    MUTUAL_ORAL_ACCESS, LAP_ACCESS, BENT_OVER_EXPOSED,
)


# ============================================================================
# Position Registry
# ============================================================================

POSITIONS: Dict[str, PositionDefinition] = {}


def register(position: PositionDefinition) -> PositionDefinition:
    """Register a position in the global registry."""
    POSITIONS[position.key] = position
    return position


def get_position(key: str) -> Optional[PositionDefinition]:
    """Get a position by key."""
    return POSITIONS.get(key)


def get_positions_by_tag(tag: str) -> List[PositionDefinition]:
    """Get all positions with a specific tag."""
    return [p for p in POSITIONS.values() if tag in p.tags]


def get_positions_for_furniture(furniture_type: FurnitureType) -> List[PositionDefinition]:
    """Get positions that can use specific furniture."""
    results = []
    for pos in POSITIONS.values():
        if furniture_type in pos.requirements.furniture_types:
            results.append(pos)
        elif not pos.requirements.furniture_required:
            # Also include positions that don't require furniture
            results.append(pos)
    return results


def get_positions_for_participant_count(count: int) -> List[PositionDefinition]:
    """Get positions that support a specific participant count."""
    return [
        p for p in POSITIONS.values()
        if p.requirements.min_participants <= count <= p.requirements.max_participants
    ]


# ============================================================================
# PENETRATIVE POSITIONS - Face to Face
# ============================================================================

register(PositionDefinition(
    key="missionary",
    name="Missionary",
    description="Classic face-to-face position with one partner lying back and the other on top.",
    slots={
        "top": make_slot(
            "top", "top",
            posture=Posture.LYING_FRONT,
            mobility=Mobility.ACTIVE,
            accesses={"bottom": INTIMATE_FRONT | {BodyZone.GROIN, BodyZone.THIGHS}},
            exposed={BodyZone.BACK_UPPER, BodyZone.ASS},
            can_thrust=True,
            controls_pace=True,
            description="on top of {bottom}",
        ),
        "bottom": make_slot(
            "bottom", "bottom",
            posture=Posture.LYING_BACK,
            mobility=Mobility.PASSIVE,
            accesses={"top": {BodyZone.BACK_UPPER, BodyZone.BACK_LOWER, BodyZone.ASS, BodyZone.CHEST, BodyZone.FACE}},
            exposed={BodyZone.FACE, BodyZone.MOUTH, BodyZone.NECK},  # Face accessible from room
            blocked={BodyZone.BACK_UPPER, BodyZone.BACK_LOWER},
            description="beneath {top}",
        ),
    },
    requirements=PositionRequirement(
        furniture_types={FurnitureType.BED, FurnitureType.FLOOR, FurnitureType.COUCH, FurnitureType.TABLE},
    ),
    tags={"penetrative", "intimate", "face_to_face", "classic"},
    aliases=["mish", "missionary position"],
    category="penetrative",
    mood="romantic",
))

register(PositionDefinition(
    key="cowgirl",
    name="Cowgirl",
    description="One partner rides on top, facing forward, controlling the pace.",
    slots={
        "riding": make_slot(
            "riding", "riding",
            posture=Posture.STRADDLING,
            mobility=Mobility.ACTIVE,
            accesses={"ridden": FRONT_FULL | {BodyZone.SHOULDERS}},
            exposed={BodyZone.FACE, BodyZone.BREASTS, BodyZone.BACK_UPPER},
            can_thrust=True,
            controls_pace=True,
            description="riding {ridden}",
        ),
        "ridden": make_slot(
            "ridden", "ridden",
            posture=Posture.LYING_BACK,
            mobility=Mobility.PASSIVE,
            accesses={"riding": {BodyZone.HIPS, BodyZone.THIGHS, BodyZone.ASS, BodyZone.CHEST, BodyZone.BREASTS, BodyZone.BELLY}},
            exposed={BodyZone.FACE, BodyZone.MOUTH},
            blocked={BodyZone.BACK_UPPER, BodyZone.BACK_LOWER},
            description="beneath {riding}",
        ),
    },
    requirements=PositionRequirement(
        furniture_types={FurnitureType.BED, FurnitureType.FLOOR, FurnitureType.COUCH},
    ),
    tags={"penetrative", "riding", "face_to_face", "active_bottom"},
    aliases=["girl on top", "riding"],
    transitions_to={"reverse_cowgirl"},
    category="penetrative",
))

register(PositionDefinition(
    key="reverse_cowgirl",
    name="Reverse Cowgirl",
    description="One partner rides on top, facing away, ass on display.",
    slots={
        "riding": make_slot(
            "riding", "riding",
            posture=Posture.STRADDLING,
            mobility=Mobility.ACTIVE,
            accesses={"ridden": {BodyZone.LEGS, BodyZone.FEET, BodyZone.THIGHS}},
            exposed={BodyZone.ASS, BodyZone.BACK_LOWER, BodyZone.FACE, BodyZone.BREASTS, BodyZone.GROIN},
            can_thrust=True,
            controls_pace=True,
            description="riding {ridden} backwards",
        ),
        "ridden": make_slot(
            "ridden", "ridden",
            posture=Posture.LYING_BACK,
            mobility=Mobility.PASSIVE,
            accesses={"riding": {BodyZone.ASS, BodyZone.BACK_LOWER, BodyZone.HIPS, BodyZone.THIGHS}},
            exposed={BodyZone.FACE, BodyZone.MOUTH, BodyZone.CHEST},
            blocked={BodyZone.BACK_UPPER, BodyZone.BACK_LOWER},
            description="beneath {riding}",
        ),
    },
    requirements=PositionRequirement(
        furniture_types={FurnitureType.BED, FurnitureType.FLOOR, FurnitureType.COUCH},
    ),
    tags={"penetrative", "riding", "ass_view"},
    aliases=["reverse girl on top"],
    transitions_to={"cowgirl"},
    category="penetrative",
))

register(PositionDefinition(
    key="lotus",
    name="Lotus",
    description="Seated embrace - one partner sits on the other's lap, face to face, wrapped around each other.",
    slots={
        "seated": make_slot(
            "seated", "seated",
            posture=Posture.SITTING,
            mobility=Mobility.LIMITED,
            accesses={"lap": INTIMATE_FRONT | {BodyZone.GROIN}},
            exposed={BodyZone.BACK_UPPER},
            can_thrust=True,
            description="in {lap}'s lap",
        ),
        "lap": make_slot(
            "lap", "lap",
            posture=Posture.SITTING,
            mobility=Mobility.LIMITED,
            accesses={"seated": INTIMATE_FRONT | {BodyZone.ASS, BodyZone.BACK_LOWER}},
            exposed={BodyZone.BACK_UPPER},
            can_thrust=True,
            description="holding {seated} in their lap",
        ),
    },
    requirements=PositionRequirement(
        furniture_types={FurnitureType.BED, FurnitureType.FLOOR, FurnitureType.COUCH, FurnitureType.CHAIR},
    ),
    tags={"penetrative", "intimate", "face_to_face", "embrace"},
    aliases=["seated embrace", "yab-yum"],
    category="penetrative",
    mood="romantic",
))


# ============================================================================
# PENETRATIVE POSITIONS - From Behind
# ============================================================================

register(PositionDefinition(
    key="doggy",
    name="Doggy Style",
    description="One partner on hands and knees, the other behind. Classic rear entry.",
    slots={
        "behind": make_slot(
            "behind", "behind",
            posture=Posture.KNEELING,
            mobility=Mobility.ACTIVE,
            accesses={"front": BEHIND_ACCESS | {BodyZone.BACK_UPPER, BodyZone.SHOULDERS, BodyZone.HAIR}},
            exposed={BodyZone.FACE, BodyZone.CHEST, BodyZone.GROIN},
            can_thrust=True,
            controls_pace=True,
            description="behind {front}",
        ),
        "front": make_slot(
            "front", "front",
            posture=Posture.HANDS_AND_KNEES,
            mobility=Mobility.PASSIVE,
            accesses={"behind": set()},  # Can't reach behind easily
            exposed={BodyZone.FACE, BodyZone.MOUTH, BodyZone.BREASTS},  # MOUTH ACCESSIBLE
            blocked={BodyZone.BACK_UPPER},
            description="on all fours in front of {behind}",
        ),
    },
    requirements=PositionRequirement(
        furniture_types={FurnitureType.BED, FurnitureType.FLOOR},
    ),
    tags={"penetrative", "from_behind", "classic", "primal"},
    aliases=["doggystyle", "from behind", "on all fours"],
    transitions_to={"prone_bone", "bent_over"},
    category="penetrative",
    intensity="normal",
))

register(PositionDefinition(
    key="prone_bone",
    name="Prone Bone",
    description="One partner lies flat on their stomach while the other lies on top from behind.",
    slots={
        "top": make_slot(
            "top", "top",
            posture=Posture.LYING_FRONT,
            mobility=Mobility.ACTIVE,
            accesses={"bottom": BACK_FULL | {BodyZone.NECK, BodyZone.EARS, BodyZone.HAIR}},
            exposed={BodyZone.BACK_UPPER, BodyZone.ASS},
            can_thrust=True,
            controls_pace=True,
            description="on top of {bottom}",
        ),
        "bottom": make_slot(
            "bottom", "bottom",
            posture=Posture.LYING_FRONT,
            mobility=Mobility.PASSIVE,
            accesses={"top": set()},
            exposed={BodyZone.FACE, BodyZone.MOUTH},  # Head can turn
            blocked={BodyZone.CHEST, BodyZone.BREASTS, BodyZone.BELLY, BodyZone.GROIN},
            hands_free=False,  # Pinned
            description="pinned beneath {top}",
        ),
    },
    requirements=PositionRequirement(
        furniture_types={FurnitureType.BED, FurnitureType.FLOOR},
    ),
    tags={"penetrative", "from_behind", "pinned", "dominant"},
    aliases=["prone", "flat on stomach"],
    transitions_to={"doggy"},
    category="penetrative",
    intensity="rough",
))

register(PositionDefinition(
    key="spooning",
    name="Spooning",
    description="Both partners on their sides, one curled behind the other for gentle, intimate penetration.",
    slots={
        "big_spoon": make_slot(
            "big_spoon", "big spoon",
            posture=Posture.LYING_SIDE,
            mobility=Mobility.ACTIVE,
            accesses={"little_spoon": {BodyZone.NECK, BodyZone.EARS, BodyZone.BACK_UPPER, BodyZone.CHEST, BodyZone.BREASTS, BodyZone.BELLY, BodyZone.GROIN, BodyZone.ASS}},
            exposed={BodyZone.BACK_UPPER},
            can_thrust=True,
            description="curled behind {little_spoon}",
        ),
        "little_spoon": make_slot(
            "little_spoon", "little spoon",
            posture=Posture.LYING_SIDE,
            mobility=Mobility.PASSIVE,
            accesses={"big_spoon": {BodyZone.HANDS, BodyZone.ARMS, BodyZone.THIGHS}},
            exposed={BodyZone.FACE, BodyZone.MOUTH, BodyZone.CHEST},
            description="pressed against {big_spoon}",
        ),
    },
    requirements=PositionRequirement(
        furniture_types={FurnitureType.BED, FurnitureType.COUCH},
    ),
    tags={"penetrative", "intimate", "gentle", "cuddling"},
    aliases=["spooning sex", "side by side"],
    category="penetrative",
    mood="romantic",
    intensity="gentle",
))


# ============================================================================
# PENETRATIVE - Standing
# ============================================================================

register(PositionDefinition(
    key="standing",
    name="Standing",
    description="Both partners standing, face to face. Requires strength or a wall for support.",
    slots={
        "lifted": make_slot(
            "lifted", "lifted",
            posture=Posture.CARRIED,
            mobility=Mobility.PASSIVE,
            accesses={"lifter": INTIMATE_FRONT},
            exposed={BodyZone.BACK_UPPER, BodyZone.ASS},
            hands_free=False,  # Holding on
            description="held up by {lifter}",
        ),
        "lifter": make_slot(
            "lifter", "lifter",
            posture=Posture.STANDING,
            mobility=Mobility.ACTIVE,
            accesses={"lifted": INTIMATE_FRONT | {BodyZone.ASS}},
            exposed={BodyZone.BACK_UPPER},
            hands_free=False,  # Holding partner
            can_thrust=True,
            controls_pace=True,
            description="holding {lifted} up",
        ),
    },
    requirements=PositionRequirement(
        requires_strength=True,
    ),
    tags={"penetrative", "standing", "athletic", "face_to_face"},
    aliases=["standing sex", "carry fuck"],
    category="penetrative",
    intensity="rough",
))

register(PositionDefinition(
    key="against_wall",
    name="Against Wall",
    description="One partner pinned against the wall, the other pressing into them.",
    slots={
        "pinning": make_slot(
            "pinning", "pinning",
            posture=Posture.STANDING,
            mobility=Mobility.ACTIVE,
            accesses={"pinned": FRONT_FULL | {BodyZone.NECK, BodyZone.HAIR}},
            exposed={BodyZone.BACK_UPPER, BodyZone.ASS},
            can_thrust=True,
            controls_pace=True,
            description="pinning {pinned} to the wall",
        ),
        "pinned": make_slot(
            "pinned", "pinned",
            posture=Posture.LEANING,
            mobility=Mobility.HELD,
            accesses={"pinning": {BodyZone.CHEST, BodyZone.FACE, BodyZone.SHOULDERS}},
            exposed={BodyZone.FACE, BodyZone.MOUTH},  # Face visible
            blocked={BodyZone.BACK_UPPER, BodyZone.BACK_LOWER},
            description="pressed against the wall by {pinning}",
        ),
    },
    requirements=PositionRequirement(
        furniture_types={FurnitureType.WALL},
        furniture_required=True,
    ),
    tags={"penetrative", "standing", "wall", "dominant", "rough"},
    aliases=["wall sex", "pinned to wall"],
    category="penetrative",
    intensity="rough",
    mood="dominant",
))

register(PositionDefinition(
    key="from_behind_standing",
    name="Standing From Behind",
    description="Both standing, one bent forward slightly while taken from behind.",
    slots={
        "behind": make_slot(
            "behind", "behind",
            posture=Posture.STANDING,
            mobility=Mobility.ACTIVE,
            accesses={"front": BEHIND_ACCESS | {BodyZone.SHOULDERS, BodyZone.HAIR, BodyZone.BREASTS}},
            exposed={BodyZone.FACE, BodyZone.CHEST},
            can_thrust=True,
            controls_pace=True,
            description="standing behind {front}",
        ),
        "front": make_slot(
            "front", "front",
            posture=Posture.BENT_FORWARD,
            mobility=Mobility.PASSIVE,
            accesses={"behind": set()},
            exposed={BodyZone.FACE, BodyZone.MOUTH, BodyZone.BREASTS},
            description="bent forward in front of {behind}",
        ),
    },
    requirements=PositionRequirement(
        furniture_types={FurnitureType.WALL, FurnitureType.TABLE, FurnitureType.DESK},
    ),
    tags={"penetrative", "standing", "from_behind"},
    aliases=["standing doggy"],
    category="penetrative",
))


# ============================================================================
# PENETRATIVE - Furniture Specific
# ============================================================================

register(PositionDefinition(
    key="bent_over_furniture",
    name="Bent Over Furniture",
    description="One partner bent over furniture (table, desk, bed edge) while taken from behind. Mouth accessible.",
    slots={
        "behind": make_slot(
            "behind", "behind",
            posture=Posture.STANDING,
            mobility=Mobility.ACTIVE,
            accesses={"bent": BEHIND_ACCESS | {BodyZone.BACK_UPPER, BodyZone.HAIR}},
            exposed={BodyZone.FACE, BodyZone.CHEST, BodyZone.GROIN},
            can_thrust=True,
            controls_pace=True,
            description="standing behind {bent}",
        ),
        "bent": make_slot(
            "bent", "bent",
            posture=Posture.BENT_OVER,
            mobility=Mobility.PASSIVE,
            accesses={"behind": set()},
            exposed=BENT_OVER_EXPOSED,  # Face, mouth, breasts all accessible!
            blocked={BodyZone.BELLY},
            hands_free=False,
            description="bent over the furniture",
        ),
        "front": make_slot(  # Optional third for mouth access
            "front", "front",
            posture=Posture.STANDING,
            mobility=Mobility.ACTIVE,
            accesses={"bent": {BodyZone.FACE, BodyZone.MOUTH, BodyZone.HAIR}},
            exposed={BodyZone.GROIN, BodyZone.CHEST},
            can_thrust=True,
            expandable=True,  # Multiple can use this slot
            max_occupants=2,
            description="in front of {bent}",
        ),
    },
    requirements=PositionRequirement(
        min_participants=2,
        max_participants=4,  # Bent + behind + up to 2 in front
        furniture_types={FurnitureType.TABLE, FurnitureType.DESK, FurnitureType.BED, FurnitureType.BENCH, FurnitureType.BREEDING_BENCH},
        furniture_required=True,
    ),
    tags={"penetrative", "from_behind", "furniture", "multi_access", "spitroast_ready"},
    aliases=["bent over table", "bent over desk", "over the edge"],
    category="penetrative",
))

register(PositionDefinition(
    key="edge_of_bed",
    name="Edge of Bed",
    description="One partner lies at the edge of the bed while the other stands/kneels between their legs.",
    slots={
        "standing": make_slot(
            "standing", "standing",
            posture=Posture.STANDING,
            mobility=Mobility.ACTIVE,
            accesses={"lying": FRONT_FULL | {BodyZone.THIGHS}},
            exposed={BodyZone.FACE, BodyZone.CHEST, BodyZone.GROIN},
            can_thrust=True,
            controls_pace=True,
            description="between {lying}'s legs",
        ),
        "lying": make_slot(
            "lying", "lying",
            posture=Posture.LYING_BACK,
            mobility=Mobility.PASSIVE,
            accesses={"standing": {BodyZone.HIPS, BodyZone.THIGHS, BodyZone.BELLY}},
            exposed={BodyZone.FACE, BodyZone.MOUTH, BodyZone.BREASTS},
            blocked={BodyZone.BACK_UPPER, BodyZone.BACK_LOWER},
            description="lying at the edge of the bed",
        ),
    },
    requirements=PositionRequirement(
        furniture_types={FurnitureType.BED, FurnitureType.TABLE},
        furniture_required=True,
    ),
    tags={"penetrative", "furniture", "bed", "face_to_face"},
    aliases=["bed edge"],
    category="penetrative",
))

register(PositionDefinition(
    key="lap_sitting",
    name="Lap Sitting",
    description="One partner sitting in a chair/throne, the other sitting on their lap facing forward or backward.",
    slots={
        "seated": make_slot(
            "seated", "seated",
            posture=Posture.SITTING,
            mobility=Mobility.LIMITED,
            accesses={"lap": LAP_ACCESS | {BodyZone.BACK_LOWER}},
            exposed={BodyZone.FACE, BodyZone.MOUTH, BodyZone.BREASTS, BodyZone.GROIN},
            can_thrust=True,
            description="sitting on {lap}'s lap",
        ),
        "lap": make_slot(
            "lap", "lap",
            posture=Posture.SITTING,
            mobility=Mobility.LIMITED,
            accesses={"seated": {BodyZone.HIPS, BodyZone.THIGHS, BodyZone.CHEST, BodyZone.BREASTS, BodyZone.BELLY, BodyZone.GROIN}},
            exposed={BodyZone.FACE, BodyZone.MOUTH},
            blocked={BodyZone.BACK_LOWER},
            can_thrust=True,
            description="beneath {seated}",
        ),
    },
    requirements=PositionRequirement(
        furniture_types={FurnitureType.CHAIR, FurnitureType.THRONE, FurnitureType.COUCH},
        furniture_required=True,
    ),
    tags={"penetrative", "sitting", "furniture", "lap"},
    aliases=["in lap", "chair sex", "throne"],
    category="penetrative",
))


# ============================================================================
# ORAL POSITIONS
# ============================================================================

register(PositionDefinition(
    key="kneeling_oral",
    name="Kneeling Oral",
    description="One partner kneels to service the other's genitals.",
    slots={
        "standing": make_slot(
            "standing", "standing",
            posture=Posture.STANDING,
            mobility=Mobility.LIMITED,
            accesses={"kneeling": ORAL_RECEIVER_ACCESS},
            exposed={BodyZone.GROIN, BodyZone.FACE, BodyZone.CHEST},
            description="standing before {kneeling}",
        ),
        "kneeling": make_slot(
            "kneeling", "kneeling",
            posture=Posture.KNEELING,
            mobility=Mobility.ACTIVE,
            accesses={"standing": ORAL_GIVER_ACCESS},
            exposed={BodyZone.FACE, BodyZone.BACK_UPPER},
            mouth_free=False,  # Mouth occupied
            description="kneeling before {standing}",
        ),
    },
    requirements=PositionRequirement(
        furniture_types=set(),  # No furniture needed
    ),
    tags={"oral", "kneeling", "servicing"},
    aliases=["blowjob", "on knees", "sucking"],
    category="oral",
))

register(PositionDefinition(
    key="lying_oral",
    name="Lying Oral",
    description="One partner lies back while the other positions between their legs for oral.",
    slots={
        "lying": make_slot(
            "lying", "lying",
            posture=Posture.LYING_BACK,
            mobility=Mobility.PASSIVE,
            accesses={"giver": {BodyZone.HAIR, BodyZone.EARS, BodyZone.FACE}},
            exposed={BodyZone.FACE, BodyZone.CHEST, BodyZone.BREASTS, BodyZone.GROIN},
            blocked={BodyZone.BACK_UPPER, BodyZone.BACK_LOWER},
            description="lying back",
        ),
        "giver": make_slot(
            "giver", "giver",
            posture=Posture.LYING_FRONT,
            mobility=Mobility.ACTIVE,
            accesses={"lying": ORAL_GIVER_ACCESS | {BodyZone.ASS}},
            exposed={BodyZone.ASS, BodyZone.BACK_UPPER},
            mouth_free=False,
            description="between {lying}'s legs",
        ),
    },
    requirements=PositionRequirement(
        furniture_types={FurnitureType.BED, FurnitureType.COUCH, FurnitureType.FLOOR},
    ),
    tags={"oral", "lying", "cunnilingus"},
    aliases=["eating out", "going down"],
    category="oral",
))

register(PositionDefinition(
    key="sixty_nine",
    name="Sixty-Nine",
    description="Mutual oral - both partners pleasure each other simultaneously, head to groin.",
    slots={
        "top": make_slot(
            "top", "top",
            posture=Posture.LYING_FRONT,
            mobility=Mobility.ACTIVE,
            accesses={"bottom": MUTUAL_ORAL_ACCESS},
            exposed={BodyZone.ASS, BodyZone.GROIN},
            mouth_free=False,
            description="on top in 69 with {bottom}",
        ),
        "bottom": make_slot(
            "bottom", "bottom",
            posture=Posture.LYING_BACK,
            mobility=Mobility.ACTIVE,
            accesses={"top": MUTUAL_ORAL_ACCESS},
            exposed={BodyZone.GROIN},  # Top's head is there
            blocked={BodyZone.FACE},  # Face occupied
            mouth_free=False,
            description="beneath {top} in 69",
        ),
    },
    requirements=PositionRequirement(
        furniture_types={FurnitureType.BED, FurnitureType.FLOOR},
    ),
    tags={"oral", "mutual", "69"},
    aliases=["69", "mutual oral"],
    category="oral",
))

register(PositionDefinition(
    key="face_sitting",
    name="Face Sitting",
    description="One partner sits on the other's face, grinding against their mouth.",
    slots={
        "sitting": make_slot(
            "sitting", "sitting",
            posture=Posture.STRADDLING,
            mobility=Mobility.ACTIVE,
            accesses={"face": {BodyZone.FACE, BodyZone.HAIR, BodyZone.EARS, BodyZone.CHEST}},
            exposed={BodyZone.BACK_UPPER, BodyZone.ASS, BodyZone.CHEST, BodyZone.BREASTS},
            controls_pace=True,
            description="sitting on {face}'s face",
        ),
        "face": make_slot(
            "face", "face",
            posture=Posture.LYING_BACK,
            mobility=Mobility.PASSIVE,
            accesses={"sitting": {BodyZone.GROIN, BodyZone.ASS, BodyZone.THIGHS}},
            exposed={BodyZone.GROIN, BodyZone.CHEST},  # Body accessible
            blocked={BodyZone.FACE, BodyZone.MOUTH},  # Face covered
            mouth_free=False,
            description="beneath {sitting}",
        ),
    },
    requirements=PositionRequirement(
        furniture_types={FurnitureType.BED, FurnitureType.FLOOR, FurnitureType.COUCH},
    ),
    tags={"oral", "facesitting", "dominant", "smothering"},
    aliases=["queening", "throne", "sit on face"],
    category="oral",
    mood="dominant",
))

register(PositionDefinition(
    key="throat_fuck",
    name="Throat Fuck",
    description="Aggressive oral where the giver takes the receiver deep, often with hands on head.",
    slots={
        "fucking": make_slot(
            "fucking", "fucking",
            posture=Posture.STANDING,
            mobility=Mobility.ACTIVE,
            accesses={"taking": {BodyZone.FACE, BodyZone.MOUTH, BodyZone.HAIR, BodyZone.NECK, BodyZone.EARS}},
            exposed={BodyZone.GROIN, BodyZone.CHEST},
            can_thrust=True,
            controls_pace=True,
            description="fucking {taking}'s throat",
        ),
        "taking": make_slot(
            "taking", "taking",
            posture=Posture.KNEELING,
            mobility=Mobility.HELD,
            accesses={"fucking": {BodyZone.THIGHS, BodyZone.HIPS}},
            exposed={BodyZone.BACK_UPPER, BodyZone.ASS},
            mouth_free=False,
            hands_free=False,  # Often restrained or braced
            description="taking {fucking} down their throat",
        ),
    },
    requirements=PositionRequirement(),
    tags={"oral", "rough", "dominant", "deepthroat"},
    aliases=["deepthroat", "skullfuck"],
    category="oral",
    intensity="rough",
    mood="dominant",
))


# ============================================================================
# MULTI-PERSON POSITIONS
# ============================================================================

register(PositionDefinition(
    key="spitroast",
    name="Spitroast",
    description="One partner in the middle, penetrated from behind while using their mouth on another.",
    slots={
        "behind": make_slot(
            "behind", "behind",
            posture=Posture.KNEELING,
            mobility=Mobility.ACTIVE,
            accesses={"middle": BEHIND_ACCESS | {BodyZone.BACK_UPPER}},
            exposed={BodyZone.FACE, BodyZone.CHEST, BodyZone.GROIN},
            can_thrust=True,
            controls_pace=True,
            description="behind {middle}",
        ),
        "middle": make_slot(
            "middle", "middle",
            posture=Posture.HANDS_AND_KNEES,
            mobility=Mobility.PASSIVE,
            accesses={"front": {BodyZone.GROIN, BodyZone.THIGHS}, "behind": set()},
            exposed={BodyZone.BREASTS},  # Hanging
            mouth_free=False,
            hands_free=False,
            description="between {behind} and {front}",
        ),
        "front": make_slot(
            "front", "front",
            posture=Posture.KNEELING,
            mobility=Mobility.ACTIVE,
            accesses={"middle": {BodyZone.FACE, BodyZone.MOUTH, BodyZone.HAIR, BodyZone.BREASTS}},
            exposed={BodyZone.GROIN, BodyZone.CHEST},
            can_thrust=True,
            description="in front of {middle}",
        ),
    },
    requirements=PositionRequirement(
        min_participants=3,
        max_participants=3,
        furniture_types={FurnitureType.BED, FurnitureType.FLOOR},
    ),
    tags={"multi", "threesome", "penetrative", "oral"},
    aliases=["eiffel tower", "spit roast"],
    category="multi",
))

register(PositionDefinition(
    key="double_penetration",
    name="Double Penetration",
    description="One partner takes two penetrations simultaneously - typically one in front, one behind.",
    slots={
        "front": make_slot(
            "front", "front",
            posture=Posture.LYING_BACK,
            mobility=Mobility.ACTIVE,
            accesses={"middle": FRONT_FULL},
            exposed={BodyZone.FACE},
            can_thrust=True,
            description="beneath {middle}",
        ),
        "middle": make_slot(
            "middle", "middle",
            posture=Posture.STRADDLING,
            mobility=Mobility.LIMITED,  # Sandwiched
            accesses={"front": FRONT_FULL, "behind": {BodyZone.THIGHS}},
            exposed={BodyZone.FACE, BodyZone.MOUTH, BodyZone.SHOULDERS},
            description="between {front} and {behind}",
        ),
        "behind": make_slot(
            "behind", "behind",
            posture=Posture.KNEELING,
            mobility=Mobility.ACTIVE,
            accesses={"middle": {BodyZone.ASS, BodyZone.BACK_LOWER, BodyZone.HIPS, BodyZone.SHOULDERS}},
            exposed={BodyZone.FACE, BodyZone.CHEST},
            can_thrust=True,
            description="behind {middle}",
        ),
    },
    requirements=PositionRequirement(
        min_participants=3,
        max_participants=3,
        furniture_types={FurnitureType.BED, FurnitureType.FLOOR},
    ),
    tags={"multi", "threesome", "dp", "penetrative", "intense"},
    aliases=["DP", "sandwich", "stuffed"],
    category="multi",
    intensity="rough",
))

register(PositionDefinition(
    key="daisy_chain",
    name="Daisy Chain",
    description="A circle of oral - each participant pleasures the next, completing a loop.",
    slots={
        "position_1": make_slot(
            "position_1", "position 1",
            posture=Posture.LYING_SIDE,
            mobility=Mobility.ACTIVE,
            accesses={"position_2": MUTUAL_ORAL_ACCESS},
            exposed={BodyZone.GROIN, BodyZone.ASS},
            mouth_free=False,
            expandable=True,
            max_occupants=1,
            description="pleasuring the next in the chain",
        ),
        "position_2": make_slot(
            "position_2", "position 2",
            posture=Posture.LYING_SIDE,
            mobility=Mobility.ACTIVE,
            accesses={"position_3": MUTUAL_ORAL_ACCESS},
            exposed={BodyZone.GROIN, BodyZone.ASS},
            mouth_free=False,
            description="pleasuring the next in the chain",
        ),
        "position_3": make_slot(
            "position_3", "position 3",
            posture=Posture.LYING_SIDE,
            mobility=Mobility.ACTIVE,
            accesses={"position_1": MUTUAL_ORAL_ACCESS},
            exposed={BodyZone.GROIN, BodyZone.ASS},
            mouth_free=False,
            description="pleasuring the next in the chain",
        ),
    },
    requirements=PositionRequirement(
        min_participants=3,
        max_participants=6,
        furniture_types={FurnitureType.BED, FurnitureType.FLOOR},
    ),
    tags={"multi", "oral", "group", "mutual"},
    aliases=["circle", "oral chain"],
    category="multi",
))

register(PositionDefinition(
    key="gangbang_center",
    name="Center of Attention",
    description="One participant at the center with multiple partners accessing different parts.",
    slots={
        "center": make_slot(
            "center", "center",
            posture=Posture.HANDS_AND_KNEES,
            mobility=Mobility.PASSIVE,
            accesses={},  # Overwhelmed, minimal reaching
            exposed=ALL_ZONES,  # Everything accessible
            mouth_free=False,
            hands_free=True,  # Can use hands on partners
            description="at the center of attention",
        ),
        "behind": make_slot(
            "behind", "behind",
            posture=Posture.KNEELING,
            mobility=Mobility.ACTIVE,
            accesses={"center": BEHIND_ACCESS},
            exposed={BodyZone.GROIN},
            can_thrust=True,
            expandable=True,
            max_occupants=2,
            description="behind {center}",
        ),
        "front": make_slot(
            "front", "front",
            posture=Posture.KNEELING,
            mobility=Mobility.ACTIVE,
            accesses={"center": {BodyZone.FACE, BodyZone.MOUTH, BodyZone.BREASTS}},
            exposed={BodyZone.GROIN},
            expandable=True,
            max_occupants=3,
            description="in front of {center}",
        ),
        "sides": make_slot(
            "sides", "side",
            posture=Posture.KNEELING,
            mobility=Mobility.ACTIVE,
            accesses={"center": {BodyZone.HANDS, BodyZone.SIDES, BodyZone.BREASTS}},
            exposed={BodyZone.GROIN},
            expandable=True,
            max_occupants=2,
            description="beside {center}",
        ),
    },
    requirements=PositionRequirement(
        min_participants=3,
        max_participants=8,
        furniture_types={FurnitureType.BED, FurnitureType.FLOOR},
    ),
    tags={"multi", "group", "gangbang", "overwhelmed"},
    aliases=["gangbang", "surrounded", "free use"],
    category="multi",
    intensity="rough",
))


# ============================================================================
# BONDAGE & RESTRAINT POSITIONS
# ============================================================================

register(PositionDefinition(
    key="stocks",
    name="In the Stocks",
    description="One partner locked in stocks - head and hands restrained, ass and mouth exposed.",
    slots={
        "locked": make_slot(
            "locked", "locked",
            posture=Posture.BENT_FORWARD,
            mobility=Mobility.RESTRAINED,
            accesses={},  # Can't reach anyone
            exposed=ALL_ZONES - {BodyZone.HANDS, BodyZone.ARMS},  # Everything but hands
            hands_free=False,
            description="locked in the stocks",
        ),
        "using_back": make_slot(
            "using_back", "behind",
            posture=Posture.STANDING,
            mobility=Mobility.FREE,
            accesses={"locked": BEHIND_ACCESS | {BodyZone.BACK_UPPER, BodyZone.TAIL}},
            exposed={BodyZone.GROIN, BodyZone.CHEST},
            can_thrust=True,
            expandable=True,
            max_occupants=2,
            description="behind {locked}",
        ),
        "using_front": make_slot(
            "using_front", "front",
            posture=Posture.STANDING,
            mobility=Mobility.FREE,
            accesses={"locked": {BodyZone.FACE, BodyZone.MOUTH, BodyZone.BREASTS}},
            exposed={BodyZone.GROIN},
            can_thrust=True,
            expandable=True,
            max_occupants=2,
            description="in front of {locked}",
        ),
    },
    requirements=PositionRequirement(
        min_participants=1,
        max_participants=5,
        furniture_types={FurnitureType.STOCKS, FurnitureType.PILLORY},
        furniture_required=True,
    ),
    tags={"bondage", "restraint", "stocks", "helpless", "multi_access"},
    aliases=["pillory", "stocked"],
    category="bondage",
    intensity="rough",
    mood="dominant",
))

register(PositionDefinition(
    key="suspended",
    name="Suspended",
    description="One partner suspended from above - fully exposed and helpless.",
    slots={
        "hanging": make_slot(
            "hanging", "hanging",
            posture=Posture.SUSPENDED,
            mobility=Mobility.IMMOBILE,
            accesses={},  # Can't reach anything
            exposed=ALL_ZONES,  # Everything accessible
            hands_free=False,
            description="suspended in the air",
        ),
        "using": make_slot(
            "using", "using",
            posture=Posture.STANDING,
            mobility=Mobility.FREE,
            accesses={"hanging": ALL_ZONES},
            exposed={BodyZone.FACE, BodyZone.CHEST, BodyZone.GROIN},
            can_thrust=True,
            controls_pace=True,
            expandable=True,
            max_occupants=4,
            description="using {hanging}",
        ),
    },
    requirements=PositionRequirement(
        min_participants=1,
        max_participants=5,
        furniture_types={FurnitureType.SUSPENSION_POINT, FurnitureType.SWING, FurnitureType.SLING},
        furniture_required=True,
        required_object_tags={"restraints", "rope", "chains"},
    ),
    tags={"bondage", "suspension", "helpless", "extreme"},
    aliases=["hanging", "strung up"],
    category="bondage",
    intensity="extreme",
))

register(PositionDefinition(
    key="spread_eagle",
    name="Spread Eagle",
    description="Limbs spread and restrained to four points - completely exposed.",
    slots={
        "spread": make_slot(
            "spread", "spread",
            posture=Posture.SPREAD,
            mobility=Mobility.RESTRAINED,
            accesses={},
            exposed=ALL_ZONES,
            hands_free=False,
            description="spread-eagled and helpless",
        ),
        "using": make_slot(
            "using", "using",
            posture=Posture.KNEELING,
            mobility=Mobility.FREE,
            accesses={"spread": ALL_ZONES},
            exposed={BodyZone.GROIN, BodyZone.CHEST},
            can_thrust=True,
            expandable=True,
            max_occupants=3,
            description="between {spread}'s legs",
        ),
    },
    requirements=PositionRequirement(
        min_participants=1,
        max_participants=4,
        furniture_types={FurnitureType.BED, FurnitureType.CROSS},
        furniture_required=True,
        required_object_tags={"restraints"},
    ),
    tags={"bondage", "spread", "helpless", "exposed"},
    aliases=["tied spread", "x-frame"],
    category="bondage",
))

register(PositionDefinition(
    key="breeding_bench",
    name="Breeding Bench",
    description="Strapped to a breeding bench - designed for easy access from behind.",
    slots={
        "strapped": make_slot(
            "strapped", "strapped",
            posture=Posture.BENT_OVER,
            mobility=Mobility.RESTRAINED,
            accesses={},
            exposed=BENT_OVER_EXPOSED | {BodyZone.BACK_UPPER},
            hands_free=False,
            description="strapped to the breeding bench",
        ),
        "breeding": make_slot(
            "breeding", "breeding",
            posture=Posture.STANDING,
            mobility=Mobility.FREE,
            accesses={"strapped": BEHIND_ACCESS | {BodyZone.BACK_UPPER, BodyZone.HAIR}},
            exposed={BodyZone.GROIN, BodyZone.CHEST},
            can_thrust=True,
            controls_pace=True,
            expandable=True,
            max_occupants=3,
            description="using {strapped}",
        ),
        "mouth_use": make_slot(
            "mouth_use", "using mouth",
            posture=Posture.STANDING,
            mobility=Mobility.FREE,
            accesses={"strapped": {BodyZone.FACE, BodyZone.MOUTH, BodyZone.HAIR}},
            exposed={BodyZone.GROIN},
            can_thrust=True,
            expandable=True,
            max_occupants=2,
            description="in front of {strapped}",
        ),
    },
    requirements=PositionRequirement(
        min_participants=1,
        max_participants=6,
        furniture_types={FurnitureType.BREEDING_BENCH},
        furniture_required=True,
    ),
    tags={"bondage", "furniture", "breeding", "multi_access"},
    aliases=["breeding stand"],
    category="bondage",
    mood="dominant",
))

register(PositionDefinition(
    key="hogtied",
    name="Hogtied",
    description="Wrists and ankles bound together behind the back - maximum helplessness.",
    slots={
        "bound": make_slot(
            "bound", "bound",
            posture=Posture.LYING_FRONT,
            mobility=Mobility.IMMOBILE,
            accesses={},
            exposed={BodyZone.FACE, BodyZone.MOUTH, BodyZone.ASS, BodyZone.GROIN, BodyZone.BACK_UPPER},
            blocked={BodyZone.CHEST, BodyZone.BREASTS, BodyZone.BELLY},
            hands_free=False,
            description="hogtied and helpless",
        ),
        "using": make_slot(
            "using", "using",
            posture=Posture.KNEELING,
            mobility=Mobility.FREE,
            accesses={"bound": {BodyZone.FACE, BodyZone.MOUTH, BodyZone.ASS, BodyZone.GROIN, BodyZone.BACK_UPPER}},
            exposed={BodyZone.GROIN},
            description="over {bound}",
        ),
    },
    requirements=PositionRequirement(
        min_participants=1,
        max_participants=2,
        required_object_tags={"rope", "restraints"},
    ),
    tags={"bondage", "hogtie", "helpless", "floor"},
    aliases=["hogtie"],
    category="bondage",
    intensity="extreme",
))


# ============================================================================
# SEX SWING & SPECIAL FURNITURE
# ============================================================================

register(PositionDefinition(
    key="sex_swing",
    name="In the Swing",
    description="One partner suspended in a sex swing at perfect height for penetration.",
    slots={
        "swinging": make_slot(
            "swinging", "in swing",
            posture=Posture.SUSPENDED,
            mobility=Mobility.LIMITED,
            accesses={"user": {BodyZone.CHEST, BodyZone.FACE, BodyZone.HIPS}},
            exposed=ALL_ZONES,
            can_thrust=False,  # Swing does the movement
            description="suspended in the swing",
        ),
        "user": make_slot(
            "user", "using",
            posture=Posture.STANDING,
            mobility=Mobility.FREE,
            accesses={"swinging": FRONT_FULL | {BodyZone.ASS}},  # Can spin them around
            exposed={BodyZone.FACE, BodyZone.CHEST, BodyZone.GROIN},
            can_thrust=True,
            controls_pace=True,
            description="standing at {swinging}",
        ),
    },
    requirements=PositionRequirement(
        furniture_types={FurnitureType.SWING, FurnitureType.SLING},
        furniture_required=True,
    ),
    tags={"swing", "suspension", "penetrative", "easy_access"},
    aliases=["swing", "sling"],
    category="furniture",
))

register(PositionDefinition(
    key="sybian",
    name="Riding the Sybian",
    description="One partner straddles a vibrating saddle while others interact.",
    slots={
        "riding": make_slot(
            "riding", "riding",
            posture=Posture.STRADDLING,
            mobility=Mobility.LIMITED,
            accesses={"user": {BodyZone.GROIN, BodyZone.FACE, BodyZone.CHEST}},
            exposed={BodyZone.FACE, BodyZone.MOUTH, BodyZone.BREASTS, BodyZone.BACK_UPPER},
            description="riding the sybian",
        ),
        "user": make_slot(
            "user", "using",
            posture=Posture.STANDING,
            mobility=Mobility.FREE,
            accesses={"riding": {BodyZone.FACE, BodyZone.MOUTH, BodyZone.BREASTS, BodyZone.HAIR}},
            exposed={BodyZone.GROIN},
            expandable=True,
            max_occupants=2,
            description="using {riding}",
        ),
    },
    requirements=PositionRequirement(
        min_participants=1,
        max_participants=3,
        furniture_types={FurnitureType.SYBIAN},
        furniture_required=True,
    ),
    tags={"toy", "machine", "vibration", "forced_orgasm"},
    aliases=["vibrating saddle"],
    category="furniture",
))


# ============================================================================
# INTIMATE / NON-SEXUAL POSITIONS
# ============================================================================

register(PositionDefinition(
    key="cuddling",
    name="Cuddling",
    description="Wrapped in each other's arms, face to face or spooned.",
    slots={
        "holder": make_slot(
            "holder", "holding",
            posture=Posture.LYING_SIDE,
            mobility=Mobility.FREE,
            accesses={"held": INTIMATE_FRONT | {BodyZone.BACK_UPPER, BodyZone.HAIR}},
            exposed={BodyZone.BACK_UPPER},
            description="holding {held}",
        ),
        "held": make_slot(
            "held", "held",
            posture=Posture.LYING_SIDE,
            mobility=Mobility.FREE,
            accesses={"holder": INTIMATE_FRONT},
            exposed={BodyZone.BACK_UPPER},
            description="in {holder}'s arms",
        ),
    },
    requirements=PositionRequirement(
        furniture_types={FurnitureType.BED, FurnitureType.COUCH, FurnitureType.FLOOR},
    ),
    tags={"intimate", "cuddling", "gentle", "romantic"},
    aliases=["holding", "snuggling"],
    category="intimate",
    mood="romantic",
    intensity="gentle",
))

register(PositionDefinition(
    key="lap_cuddle",
    name="Lap Cuddle",
    description="One partner curled in the other's lap.",
    slots={
        "lap": make_slot(
            "lap", "lap",
            posture=Posture.SITTING,
            mobility=Mobility.FREE,
            accesses={"curled": INTIMATE_FRONT | {BodyZone.HAIR, BodyZone.BACK_UPPER}},
            exposed={BodyZone.FACE, BodyZone.CHEST},
            description="with {curled} in their lap",
        ),
        "curled": make_slot(
            "curled", "curled",
            posture=Posture.SITTING,
            mobility=Mobility.FREE,
            accesses={"lap": {BodyZone.CHEST, BodyZone.FACE, BodyZone.ARMS}},
            exposed={BodyZone.FACE, BodyZone.BACK_UPPER},
            description="curled in {lap}'s lap",
        ),
    },
    requirements=PositionRequirement(
        furniture_types={FurnitureType.COUCH, FurnitureType.CHAIR, FurnitureType.BED},
    ),
    tags={"intimate", "cuddling", "lap", "comfort"},
    aliases=["in lap"],
    category="intimate",
    mood="romantic",
))

register(PositionDefinition(
    key="embrace_standing",
    name="Standing Embrace",
    description="Standing and holding each other close.",
    slots={
        "embracer": make_slot(
            "embracer", "embracing",
            posture=Posture.STANDING,
            mobility=Mobility.FREE,
            accesses={"embraced": INTIMATE_FRONT | BACK_UPPER},
            exposed={BodyZone.BACK_UPPER},
            description="holding {embraced}",
        ),
        "embraced": make_slot(
            "embraced", "embraced",
            posture=Posture.STANDING,
            mobility=Mobility.FREE,
            accesses={"embracer": INTIMATE_FRONT | BACK_UPPER},
            exposed={BodyZone.BACK_UPPER},
            description="in {embracer}'s arms",
        ),
    },
    requirements=PositionRequirement(),
    tags={"intimate", "embrace", "standing"},
    aliases=["hug", "hugging", "holding"],
    category="intimate",
    mood="romantic",
))


# ============================================================================
# MANUAL / HAND POSITIONS
# ============================================================================

register(PositionDefinition(
    key="handjob_standing",
    name="Standing Handjob",
    description="One partner manually stimulates the other while standing.",
    slots={
        "giving": make_slot(
            "giving", "giving",
            posture=Posture.STANDING,
            mobility=Mobility.FREE,
            accesses={"receiving": {BodyZone.GROIN, BodyZone.CHEST, BodyZone.NECK, BodyZone.FACE}},
            exposed={BodyZone.FACE, BodyZone.CHEST, BodyZone.GROIN},
            description="stroking {receiving}",
        ),
        "receiving": make_slot(
            "receiving", "receiving",
            posture=Posture.STANDING,
            mobility=Mobility.PASSIVE,
            accesses={"giving": {BodyZone.GROIN, BodyZone.CHEST, BodyZone.ASS}},
            exposed={BodyZone.FACE, BodyZone.CHEST, BodyZone.GROIN},
            description="being stroked by {giving}",
        ),
    },
    requirements=PositionRequirement(),
    tags={"manual", "handjob", "standing"},
    aliases=["jacking off", "stroking"],
    category="manual",
))

register(PositionDefinition(
    key="fingering",
    name="Fingering",
    description="One partner fingering the other.",
    slots={
        "fingering": make_slot(
            "fingering", "fingering",
            posture=Posture.SITTING,  # Or various
            mobility=Mobility.FREE,
            accesses={"fingered": {BodyZone.GROIN, BodyZone.ASS, BodyZone.THIGHS, BodyZone.CHEST, BodyZone.MOUTH}},
            exposed={BodyZone.FACE, BodyZone.CHEST},
            description="fingering {fingered}",
        ),
        "fingered": make_slot(
            "fingered", "fingered",
            posture=Posture.LYING_BACK,
            mobility=Mobility.PASSIVE,
            accesses={"fingering": {BodyZone.ARMS, BodyZone.HANDS, BodyZone.CHEST}},
            exposed={BodyZone.FACE, BodyZone.CHEST, BodyZone.GROIN},
            description="being fingered by {fingering}",
        ),
    },
    requirements=PositionRequirement(
        furniture_types={FurnitureType.BED, FurnitureType.COUCH, FurnitureType.FLOOR},
    ),
    tags={"manual", "fingering", "intimate"},
    aliases=["finger", "fingers"],
    category="manual",
))


# ============================================================================
# SPECIAL / EXHIBITIONIST
# ============================================================================

register(PositionDefinition(
    key="glory_hole",
    name="Glory Hole",
    description="Anonymous encounter through a partition - only certain parts accessible.",
    slots={
        "offering": make_slot(
            "offering", "offering",
            posture=Posture.STANDING,
            mobility=Mobility.LIMITED,
            accesses={},  # Can't see/reach the other side
            exposed={BodyZone.GROIN},  # Only what's through the hole
            blocked=ALL_ZONES - {BodyZone.GROIN},  # Everything else blocked
            description="presenting through the glory hole",
        ),
        "servicing": make_slot(
            "servicing", "servicing",
            posture=Posture.KNEELING,
            mobility=Mobility.FREE,
            accesses={"offering": {BodyZone.GROIN}},  # Only what's through
            exposed={BodyZone.FACE, BodyZone.MOUTH},  # For those on same side
            mouth_free=False,
            description="servicing through the glory hole",
        ),
    },
    requirements=PositionRequirement(
        furniture_types={FurnitureType.WALL},  # Special partition
        furniture_required=True,
    ),
    tags={"anonymous", "glory_hole", "partition", "oral"},
    aliases=["through wall", "anonymous"],
    category="special",
))

register(PositionDefinition(
    key="window_display",
    name="Window Display",
    description="One partner displayed in a window for voyeurs outside.",
    slots={
        "displayed": make_slot(
            "displayed", "displayed",
            posture=Posture.STANDING,  # Or various
            mobility=Mobility.LIMITED,
            accesses={"partner": FRONT_FULL},
            exposed=FRONT_FULL,  # Exposed to outside
            description="displayed in the window",
        ),
        "partner": make_slot(
            "partner", "partner",
            posture=Posture.STANDING,
            mobility=Mobility.FREE,
            accesses={"displayed": BACK_FULL | {BodyZone.HIPS, BodyZone.GROIN}},
            exposed={BodyZone.ASS, BodyZone.BACK_UPPER},  # Back to room
            can_thrust=True,
            description="using {displayed} at the window",
        ),
    },
    requirements=PositionRequirement(
        furniture_types={FurnitureType.WINDOWSILL},
        furniture_required=True,
    ),
    tags={"exhibitionist", "window", "display", "voyeur"},
    aliases=["at window", "on display"],
    category="special",
    mood="exhibitionist",
))


# ============================================================================
# UTILITY FUNCTIONS
# ============================================================================

def search_positions(
    query: str = "",
    tags: Optional[Set[str]] = None,
    category: Optional[str] = None,
    min_participants: Optional[int] = None,
    max_participants: Optional[int] = None,
    furniture: Optional[FurnitureType] = None,
    requires_furniture: Optional[bool] = None,
) -> List[PositionDefinition]:
    """
    Search positions with multiple filters.
    
    Args:
        query: Text search in name/description/aliases
        tags: Must have ALL of these tags
        category: Must be in this category
        min_participants: Position must support at least this many
        max_participants: Position must support at most this many
        furniture: Must work with this furniture type
        requires_furniture: True = must require furniture, False = must not
        
    Returns:
        List of matching positions
    """
    results = []
    
    for pos in POSITIONS.values():
        # Text search
        if query and not pos.matches_search(query):
            continue
        
        # Tag filter
        if tags and not tags.issubset(pos.tags):
            continue
        
        # Category filter
        if category and pos.category != category:
            continue
        
        # Participant count
        if min_participants and pos.requirements.max_participants < min_participants:
            continue
        if max_participants and pos.requirements.min_participants > max_participants:
            continue
        
        # Furniture filter
        if furniture:
            if pos.requirements.furniture_required:
                if furniture not in pos.requirements.furniture_types:
                    continue
            elif pos.requirements.furniture_types:
                if furniture not in pos.requirements.furniture_types:
                    continue
        
        # Requires furniture filter
        if requires_furniture is not None:
            if requires_furniture and not pos.requirements.furniture_required:
                continue
            if not requires_furniture and pos.requirements.furniture_required:
                continue
        
        results.append(pos)
    
    return results


def list_categories() -> List[str]:
    """Get all position categories."""
    return list(set(pos.category for pos in POSITIONS.values()))


def list_tags() -> Set[str]:
    """Get all position tags."""
    tags = set()
    for pos in POSITIONS.values():
        tags.update(pos.tags)
    return tags


# Export count for verification
POSITION_COUNT = len(POSITIONS)
