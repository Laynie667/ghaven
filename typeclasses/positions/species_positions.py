"""
Species-Specific Position Variants
==================================

Positions designed for non-bipedal body types:
- Quadruped positions (feral, mounting)
- Taur positions (centaur-compatible)
- Serpentine positions (naga, lamia)
- Size-difference positions
- Mixed-species positions
"""

from .core import BodyZone, Posture, Mobility, FurnitureType
from .definitions import (
    PositionDefinition,
    PositionRequirement,
    make_slot,
    FRONT_FULL, BACK_FULL, BEHIND_ACCESS, ALL_ZONES,
)
from .library import register


# ============================================================================
# QUADRUPED POSITIONS
# ============================================================================

register(PositionDefinition(
    key="mounted",
    name="Mounted",
    description="Classic quadruped mating - one mounts the other from behind, forepaws gripping flanks.",
    slots={
        "mounting": make_slot(
            "mounting", "mounting",
            posture=Posture.MOUNTED,
            mobility=Mobility.ACTIVE,
            accesses={"mounted": {
                BodyZone.BACK_UPPER, BodyZone.BACK_LOWER, BodyZone.HIPS,
                BodyZone.ASS, BodyZone.GROIN, BodyZone.TAIL, BodyZone.NECK,
                BodyZone.SIDES, BodyZone.SHOULDERS,
            }},
            exposed={BodyZone.BACK_UPPER, BodyZone.GROIN},
            can_thrust=True,
            controls_pace=True,
            description="mounted on {mounted}",
        ),
        "mounted": make_slot(
            "mounted", "mounted",
            posture=Posture.STANDING,  # Quadruped standing
            mobility=Mobility.PASSIVE,
            accesses={"mounting": set()},  # Can't reach behind easily
            exposed={BodyZone.FACE, BodyZone.MOUTH, BodyZone.NECK},
            description="being mounted by {mounting}",
        ),
    },
    requirements=PositionRequirement(
        required_mobility={"quadruped", "taur"},
    ),
    tags={"mounting", "feral", "quadruped", "from_behind", "primal"},
    aliases=["breeding mount", "animal mounting"],
    category="quadruped",
    intensity="rough",
))

register(PositionDefinition(
    key="presenting",
    name="Presenting",
    description="One presents their hindquarters, tail raised, inviting approach.",
    slots={
        "presenting": make_slot(
            "presenting", "presenting",
            posture=Posture.STANDING,
            mobility=Mobility.PASSIVE,
            accesses={},
            exposed={BodyZone.ASS, BodyZone.GROIN, BodyZone.TAIL, BodyZone.BACK_LOWER, 
                    BodyZone.HIPS, BodyZone.THIGHS, BodyZone.FACE, BodyZone.MOUTH},
            description="presenting hindquarters",
        ),
        "approaching": make_slot(
            "approaching", "approaching",
            posture=Posture.STANDING,
            mobility=Mobility.FREE,
            accesses={"presenting": {
                BodyZone.ASS, BodyZone.GROIN, BodyZone.TAIL, BodyZone.BACK_LOWER,
                BodyZone.HIPS, BodyZone.THIGHS, BodyZone.SIDES,
            }},
            exposed={BodyZone.FACE, BodyZone.GROIN},
            can_thrust=True,
            expandable=True,
            max_occupants=3,
            description="behind {presenting}",
        ),
    },
    requirements=PositionRequirement(
        min_participants=1,
        max_participants=4,
    ),
    tags={"presenting", "display", "invitation", "multi_access"},
    aliases=["lordosis", "flagging", "tail up"],
    category="quadruped",
))

register(PositionDefinition(
    key="quadruped_side_lying",
    name="Side by Side (Quadruped)",
    description="Both lying on their sides, one behind the other for gentle mating.",
    slots={
        "front": make_slot(
            "front", "in front",
            posture=Posture.LYING_SIDE,
            mobility=Mobility.PASSIVE,
            accesses={"behind": {BodyZone.GROIN, BodyZone.LEGS}},
            exposed={BodyZone.FACE, BodyZone.BELLY, BodyZone.GROIN},
            description="lying in front",
        ),
        "behind": make_slot(
            "behind", "behind",
            posture=Posture.LYING_SIDE,
            mobility=Mobility.ACTIVE,
            accesses={"front": {
                BodyZone.BACK_LOWER, BodyZone.ASS, BodyZone.GROIN,
                BodyZone.TAIL, BodyZone.HIPS, BodyZone.NECK,
            }},
            exposed={BodyZone.BACK_UPPER},
            can_thrust=True,
            description="spooned behind {front}",
        ),
    },
    requirements=PositionRequirement(
        furniture_types={FurnitureType.FLOOR, FurnitureType.BED, FurnitureType.GRASS},
    ),
    tags={"quadruped", "gentle", "spooning", "lying"},
    aliases=["animal spooning"],
    category="quadruped",
    intensity="gentle",
))

register(PositionDefinition(
    key="biped_mounts_quadruped",
    name="Biped Mounting Quadruped",
    description="A bipedal character mounts a quadruped from behind, standing or kneeling.",
    slots={
        "rider": make_slot(
            "rider", "rider",
            posture=Posture.STANDING,
            mobility=Mobility.ACTIVE,
            accesses={"beast": {
                BodyZone.BACK_UPPER, BodyZone.BACK_LOWER, BodyZone.HIPS,
                BodyZone.ASS, BodyZone.GROIN, BodyZone.TAIL, BodyZone.SIDES,
            }},
            exposed={BodyZone.FACE, BodyZone.CHEST, BodyZone.GROIN},
            can_thrust=True,
            controls_pace=True,
            description="mounted on {beast}",
        ),
        "beast": make_slot(
            "beast", "beast",
            posture=Posture.STANDING,
            mobility=Mobility.PASSIVE,
            accesses={"rider": set()},
            exposed={BodyZone.FACE, BodyZone.MOUTH, BodyZone.GROIN},  # Can turn head
            description="being mounted by {rider}",
        ),
    },
    requirements=PositionRequirement(),
    tags={"bestiality", "mounting", "interspecies", "from_behind"},
    aliases=["mounting beast", "taking animal"],
    category="interspecies",
))

register(PositionDefinition(
    key="quadruped_oral",
    name="Quadruped Oral Service",
    description="Bipedal partner kneels or lies to service a quadruped's genitals.",
    slots={
        "beast": make_slot(
            "beast", "beast",
            posture=Posture.STANDING,
            mobility=Mobility.LIMITED,
            accesses={"servant": {BodyZone.FACE, BodyZone.HAIR, BodyZone.BACK_UPPER}},
            exposed={BodyZone.GROIN, BodyZone.BELLY},
            description="standing over {servant}",
        ),
        "servant": make_slot(
            "servant", "servicing",
            posture=Posture.LYING_BACK,  # Under the beast
            mobility=Mobility.ACTIVE,
            accesses={"beast": {BodyZone.GROIN, BodyZone.BELLY, BodyZone.THIGHS}},
            exposed={BodyZone.FACE, BodyZone.CHEST, BodyZone.GROIN},
            mouth_free=False,
            description="beneath {beast}",
        ),
    },
    requirements=PositionRequirement(),
    tags={"oral", "interspecies", "service"},
    aliases=["under beast"],
    category="interspecies",
))


# ============================================================================
# TAUR POSITIONS
# ============================================================================

register(PositionDefinition(
    key="taur_mounted_by_biped",
    name="Taur Taken From Behind",
    description="A biped stands behind a taur, taking them from the rear.",
    slots={
        "taker": make_slot(
            "taker", "taker",
            posture=Posture.STANDING,
            mobility=Mobility.ACTIVE,
            accesses={"taur": {
                BodyZone.ASS, BodyZone.GROIN, BodyZone.TAIL, BodyZone.HIPS,
                BodyZone.BACK_LOWER, BodyZone.THIGHS,
            }},
            exposed={BodyZone.FACE, BodyZone.CHEST, BodyZone.GROIN},
            can_thrust=True,
            controls_pace=True,
            description="behind {taur}",
        ),
        "taur": make_slot(
            "taur", "taur",
            posture=Posture.STANDING,
            mobility=Mobility.PASSIVE,
            accesses={"taker": set()},  # Can't easily reach behind
            exposed={BodyZone.FACE, BodyZone.CHEST, BodyZone.BREASTS, BodyZone.MOUTH},
            description="being taken from behind",
        ),
    },
    requirements=PositionRequirement(),
    tags={"taur", "from_behind", "standing", "interspecies"},
    aliases=["behind taur", "taur rear"],
    category="taur",
))

register(PositionDefinition(
    key="under_taur",
    name="Under the Taur",
    description="A partner lies or kneels beneath a taur's barrel, accessing their underside.",
    slots={
        "taur": make_slot(
            "taur", "taur",
            posture=Posture.STANDING,
            mobility=Mobility.LIMITED,
            accesses={"beneath": {BodyZone.FACE, BodyZone.HAIR}},  # Can look down
            exposed={BodyZone.GROIN, BodyZone.BELLY},  # Underside
            description="standing over {beneath}",
        ),
        "beneath": make_slot(
            "beneath", "beneath",
            posture=Posture.LYING_BACK,
            mobility=Mobility.ACTIVE,
            accesses={"taur": {BodyZone.GROIN, BodyZone.BELLY, BodyZone.THIGHS}},
            exposed={BodyZone.FACE, BodyZone.CHEST, BodyZone.GROIN},
            description="beneath {taur}'s barrel",
        ),
    },
    requirements=PositionRequirement(),
    tags={"taur", "oral", "service", "beneath"},
    aliases=["under centaur", "beneath taur"],
    category="taur",
))

register(PositionDefinition(
    key="taur_rides_taur",
    name="Taur Mounting Taur",
    description="One taur mounts another from behind - their natural mating position.",
    slots={
        "mounting": make_slot(
            "mounting", "mounting",
            posture=Posture.MOUNTED,
            mobility=Mobility.ACTIVE,
            accesses={"mounted": {
                BodyZone.BACK_UPPER, BodyZone.BACK_LOWER, BodyZone.HIPS,
                BodyZone.ASS, BodyZone.GROIN, BodyZone.TAIL,
                BodyZone.SHOULDERS, BodyZone.NECK, BodyZone.EARS,
                BodyZone.CHEST, BodyZone.BREASTS,  # Can reach around
            }},
            exposed={BodyZone.BACK_UPPER},
            can_thrust=True,
            controls_pace=True,
            description="mounted on {mounted}",
        ),
        "mounted": make_slot(
            "mounted", "mounted",
            posture=Posture.STANDING,
            mobility=Mobility.PASSIVE,
            accesses={"mounting": set()},
            exposed={BodyZone.FACE, BodyZone.MOUTH, BodyZone.CHEST, BodyZone.BREASTS},
            description="being mounted by {mounting}",
        ),
    },
    requirements=PositionRequirement(
        required_mobility={"taur"},
    ),
    tags={"taur", "mounting", "from_behind"},
    aliases=["centaur mating"],
    category="taur",
))

register(PositionDefinition(
    key="riding_taur_back",
    name="Riding Taur's Back",
    description="A partner sits on a taur's horse-back, potentially being penetrated from below.",
    slots={
        "taur": make_slot(
            "taur", "taur",
            posture=Posture.STANDING,
            mobility=Mobility.ACTIVE,
            accesses={"rider": {BodyZone.GROIN, BodyZone.ASS, BodyZone.THIGHS, BodyZone.LEGS}},
            exposed={BodyZone.FACE, BodyZone.CHEST, BodyZone.GROIN},
            can_thrust=True,  # From below
            description="carrying {rider}",
        ),
        "rider": make_slot(
            "rider", "rider",
            posture=Posture.STRADDLING,
            mobility=Mobility.LIMITED,
            accesses={"taur": {
                BodyZone.BACK_UPPER, BodyZone.SHOULDERS, BodyZone.NECK,
                BodyZone.HAIR, BodyZone.EARS, BodyZone.SIDES,
            }},
            exposed={BodyZone.BACK_UPPER, BodyZone.ASS},
            description="riding on {taur}'s back",
        ),
    },
    requirements=PositionRequirement(),
    tags={"taur", "riding", "mounted"},
    aliases=["on taur back", "horseback"],
    category="taur",
))

register(PositionDefinition(
    key="taur_oral_service",
    name="Taur Receiving Oral",
    description="Partner kneels before standing taur to service them orally.",
    slots={
        "taur": make_slot(
            "taur", "taur",
            posture=Posture.STANDING,
            mobility=Mobility.LIMITED,
            accesses={"kneeling": {BodyZone.FACE, BodyZone.HAIR, BodyZone.EARS}},
            exposed={BodyZone.GROIN, BodyZone.CHEST, BodyZone.FACE},
            description="standing before {kneeling}",
        ),
        "kneeling": make_slot(
            "kneeling", "kneeling",
            posture=Posture.KNEELING,
            mobility=Mobility.ACTIVE,
            accesses={"taur": {BodyZone.GROIN, BodyZone.THIGHS, BodyZone.BELLY}},
            exposed={BodyZone.BACK_UPPER, BodyZone.ASS},
            mouth_free=False,
            description="kneeling before {taur}",
        ),
    },
    requirements=PositionRequirement(),
    tags={"taur", "oral", "kneeling", "service"},
    aliases=["servicing taur"],
    category="taur",
))


# ============================================================================
# SERPENTINE POSITIONS
# ============================================================================

register(PositionDefinition(
    key="coiled_embrace",
    name="Coiled Embrace",
    description="Serpentine wraps their coils around a partner, holding them face to face.",
    slots={
        "serpent": make_slot(
            "serpent", "serpent",
            posture=Posture.LYING_SIDE,  # Coiled
            mobility=Mobility.ACTIVE,
            accesses={"wrapped": {
                BodyZone.FACE, BodyZone.MOUTH, BodyZone.NECK, BodyZone.CHEST,
                BodyZone.BREASTS, BodyZone.BELLY, BodyZone.GROIN, BodyZone.ASS,
                BodyZone.BACK_UPPER, BodyZone.BACK_LOWER, BodyZone.WHOLE_BODY,
            }},
            exposed={BodyZone.FACE, BodyZone.CHEST, BodyZone.GROIN},
            can_thrust=True,
            controls_pace=True,
            description="coiled around {wrapped}",
        ),
        "wrapped": make_slot(
            "wrapped", "wrapped",
            posture=Posture.HELD,
            mobility=Mobility.HELD,
            accesses={"serpent": {
                BodyZone.FACE, BodyZone.MOUTH, BodyZone.NECK, BodyZone.CHEST,
                BodyZone.BREASTS, BodyZone.SHOULDERS,
            }},
            exposed={BodyZone.FACE},  # Only face visible through coils
            hands_free=False,  # Arms pinned by coils
            description="wrapped in {serpent}'s coils",
        ),
    },
    requirements=PositionRequirement(
        required_mobility={"serpentine"},
    ),
    tags={"serpentine", "coiling", "constriction", "intimate", "restraint"},
    aliases=["naga embrace", "lamia coils"],
    category="serpentine",
    mood="dominant",
))

register(PositionDefinition(
    key="coiled_binding",
    name="Coiled and Bound",
    description="Serpentine fully restrains partner in coils, completely immobilizing them.",
    slots={
        "serpent": make_slot(
            "serpent", "serpent",
            posture=Posture.LYING_SIDE,
            mobility=Mobility.FREE,
            accesses={"bound": ALL_ZONES},  # Full access
            exposed={BodyZone.FACE, BodyZone.GROIN},
            can_thrust=True,
            controls_pace=True,
            description="binding {bound} in coils",
        ),
        "bound": make_slot(
            "bound", "bound",
            posture=Posture.HELD,
            mobility=Mobility.IMMOBILE,
            accesses={},  # Can't move at all
            exposed={BodyZone.FACE, BodyZone.GROIN},  # What serpent exposes
            hands_free=False,
            description="completely bound in {serpent}'s coils",
        ),
    },
    requirements=PositionRequirement(
        required_mobility={"serpentine"},
    ),
    tags={"serpentine", "bondage", "constriction", "helpless", "restraint"},
    aliases=["coil bondage", "snake binding"],
    category="serpentine",
    intensity="rough",
    mood="dominant",
))

register(PositionDefinition(
    key="serpent_from_behind",
    name="Taking the Serpent",
    description="Partner takes a serpentine from behind their humanoid portion.",
    slots={
        "taker": make_slot(
            "taker", "taker",
            posture=Posture.KNEELING,
            mobility=Mobility.ACTIVE,
            accesses={"serpent": {
                BodyZone.BACK_UPPER, BodyZone.BACK_LOWER, BodyZone.HIPS,
                BodyZone.GROIN, BodyZone.TAIL, BodyZone.SHOULDERS, BodyZone.NECK,
            }},
            exposed={BodyZone.FACE, BodyZone.CHEST, BodyZone.GROIN},
            can_thrust=True,
            controls_pace=True,
            description="behind {serpent}",
        ),
        "serpent": make_slot(
            "serpent", "serpent",
            posture=Posture.LYING_FRONT,
            mobility=Mobility.PASSIVE,
            accesses={"taker": set()},  # Tail could wrap
            exposed={BodyZone.FACE, BodyZone.MOUTH, BodyZone.BREASTS},
            description="being taken from behind",
        ),
    },
    requirements=PositionRequirement(),
    tags={"serpentine", "from_behind", "interspecies"},
    aliases=["naga rear", "behind serpent"],
    category="serpentine",
))

register(PositionDefinition(
    key="tail_wrapped_fuck",
    name="Tail-Wrapped",
    description="Serpentine wraps tail around partner's lower body during penetration.",
    slots={
        "serpent": make_slot(
            "serpent", "serpent",
            posture=Posture.LYING_FRONT,
            mobility=Mobility.ACTIVE,
            accesses={"wrapped": {
                BodyZone.FACE, BodyZone.CHEST, BodyZone.BREASTS,
                BodyZone.GROIN, BodyZone.HIPS, BodyZone.THIGHS,
            }},
            exposed={BodyZone.BACK_UPPER, BodyZone.ASS},
            can_thrust=True,
            description="tail wrapped around {wrapped}",
        ),
        "wrapped": make_slot(
            "wrapped", "wrapped",
            posture=Posture.LYING_BACK,
            mobility=Mobility.LIMITED,
            accesses={"serpent": {
                BodyZone.FACE, BodyZone.CHEST, BodyZone.BREASTS,
                BodyZone.GROIN, BodyZone.SHOULDERS,
            }},
            exposed={BodyZone.FACE, BodyZone.CHEST},
            description="wrapped in {serpent}'s tail",
        ),
    },
    requirements=PositionRequirement(
        furniture_types={FurnitureType.BED, FurnitureType.FLOOR},
    ),
    tags={"serpentine", "tail", "penetrative", "restraint"},
    aliases=["tail sex"],
    category="serpentine",
))


# ============================================================================
# SIZE DIFFERENCE POSITIONS
# ============================================================================

register(PositionDefinition(
    key="size_diff_standing",
    name="Size Difference Standing",
    description="Large partner standing, smaller partner at convenient height for access.",
    slots={
        "large": make_slot(
            "large", "large",
            posture=Posture.STANDING,
            mobility=Mobility.ACTIVE,
            accesses={"small": {
                BodyZone.FACE, BodyZone.MOUTH, BodyZone.HAIR,
                BodyZone.CHEST, BodyZone.BACK_UPPER,
            }},
            exposed={BodyZone.GROIN, BodyZone.THIGHS, BodyZone.BELLY},
            can_thrust=True,
            description="towering over {small}",
        ),
        "small": make_slot(
            "small", "small",
            posture=Posture.STANDING,
            mobility=Mobility.ACTIVE,
            accesses={"large": {
                BodyZone.GROIN, BodyZone.THIGHS, BodyZone.BELLY,
                BodyZone.HIPS,
            }},
            exposed={BodyZone.FACE, BodyZone.CHEST, BodyZone.GROIN},
            mouth_free=False,  # At convenient height
            description="before {large}",
        ),
    },
    requirements=PositionRequirement(
        size_compatible=True,
        max_size_difference=3,
    ),
    tags={"size_difference", "standing", "height_play"},
    aliases=["tall and short"],
    category="size",
))

register(PositionDefinition(
    key="size_diff_carried",
    name="Carried (Size Difference)",
    description="Large partner holds and carries smaller partner during penetration.",
    slots={
        "carrier": make_slot(
            "carrier", "carrier",
            posture=Posture.STANDING,
            mobility=Mobility.ACTIVE,
            accesses={"carried": {
                BodyZone.FACE, BodyZone.MOUTH, BodyZone.CHEST, BodyZone.BREASTS,
                BodyZone.GROIN, BodyZone.ASS, BodyZone.THIGHS, BodyZone.BACK_LOWER,
            }},
            exposed={BodyZone.FACE, BodyZone.CHEST},
            hands_free=False,  # Holding partner
            can_thrust=True,
            controls_pace=True,
            description="carrying {carried}",
        ),
        "carried": make_slot(
            "carried", "carried",
            posture=Posture.CARRIED,
            mobility=Mobility.PASSIVE,
            accesses={"carrier": {
                BodyZone.FACE, BodyZone.NECK, BodyZone.SHOULDERS,
                BodyZone.CHEST, BodyZone.BACK_UPPER,
            }},
            exposed={BodyZone.BACK_UPPER, BodyZone.ASS},
            hands_free=False,  # Holding on
            description="held by {carrier}",
        ),
    },
    requirements=PositionRequirement(
        size_compatible=True,
        max_size_difference=2,
        requires_strength=True,
    ),
    tags={"size_difference", "carried", "strength", "dominant"},
    aliases=["pick up fuck", "held up"],
    category="size",
    intensity="rough",
))

register(PositionDefinition(
    key="size_diff_in_hand",
    name="In Hand",
    description="Massive partner holds tiny partner in their hand. For extreme size differences.",
    slots={
        "giant": make_slot(
            "giant", "giant",
            posture=Posture.SITTING,
            mobility=Mobility.FREE,
            accesses={"tiny": ALL_ZONES},  # Complete access
            exposed={BodyZone.FACE, BodyZone.CHEST, BodyZone.GROIN},
            description="holding {tiny} in their hand",
        ),
        "tiny": make_slot(
            "tiny", "tiny",
            posture=Posture.HELD,
            mobility=Mobility.LIMITED,
            accesses={"giant": {BodyZone.HANDS}},  # Only what's near
            exposed=ALL_ZONES,  # Completely exposed
            description="held in {giant}'s palm",
        ),
    },
    requirements=PositionRequirement(
        size_compatible=True,
        max_size_difference=4,  # Needs to be MUCH bigger
    ),
    tags={"size_difference", "extreme", "macro", "held"},
    aliases=["palm held", "giant holding"],
    category="size",
))

register(PositionDefinition(
    key="size_diff_oral_service",
    name="Size Difference Oral",
    description="Smaller partner orally services a much larger partner's massive genitals.",
    slots={
        "large": make_slot(
            "large", "large",
            posture=Posture.STANDING,
            mobility=Mobility.LIMITED,
            accesses={"small": {BodyZone.FACE, BodyZone.HAIR, BodyZone.SHOULDERS}},
            exposed={BodyZone.GROIN, BodyZone.BELLY, BodyZone.THIGHS},
            description="looming over {small}",
        ),
        "small": make_slot(
            "small", "small",
            posture=Posture.KNEELING,
            mobility=Mobility.ACTIVE,
            accesses={"large": {BodyZone.GROIN, BodyZone.THIGHS, BodyZone.BELLY}},
            exposed={BodyZone.BACK_UPPER, BodyZone.ASS},
            mouth_free=False,
            description="worshipping {large}",
        ),
    },
    requirements=PositionRequirement(
        size_compatible=True,
        max_size_difference=3,
    ),
    tags={"size_difference", "oral", "worship", "service"},
    aliases=["worshipping giant"],
    category="size",
))


# ============================================================================
# WING/AVIAN SPECIFIC
# ============================================================================

register(PositionDefinition(
    key="avian_standing",
    name="Avian Standing",
    description="Position accommodating wings - both standing, with wing-room.",
    slots={
        "winged": make_slot(
            "winged", "winged",
            posture=Posture.STANDING,
            mobility=Mobility.ACTIVE,
            accesses={"partner": FRONT_FULL},
            exposed={BodyZone.FACE, BodyZone.CHEST, BodyZone.GROIN},  # Wings spread
            description="wings spread",
        ),
        "partner": make_slot(
            "partner", "partner",
            posture=Posture.STANDING,
            mobility=Mobility.ACTIVE,
            accesses={"winged": FRONT_FULL | {BodyZone.SIDES}},  # Can reach under wings
            exposed={BodyZone.FACE, BodyZone.BACK_UPPER},
            can_thrust=True,
            description="facing {winged}",
        ),
    },
    requirements=PositionRequirement(),
    tags={"avian", "wings", "standing", "face_to_face"},
    aliases=["winged standing"],
    category="avian",
))

register(PositionDefinition(
    key="avian_front_lying",
    name="Avian Prone",
    description="Winged partner lies on front (wings folded or spread), taken from behind.",
    slots={
        "behind": make_slot(
            "behind", "behind",
            posture=Posture.KNEELING,
            mobility=Mobility.ACTIVE,
            accesses={"winged": BEHIND_ACCESS | {BodyZone.BACK_UPPER, BodyZone.SHOULDERS}},
            exposed={BodyZone.FACE, BodyZone.CHEST, BodyZone.GROIN},
            can_thrust=True,
            controls_pace=True,
            description="over {winged}",
        ),
        "winged": make_slot(
            "winged", "winged",
            posture=Posture.LYING_FRONT,
            mobility=Mobility.PASSIVE,
            accesses={"behind": set()},
            exposed={BodyZone.FACE, BodyZone.MOUTH},  # Can turn head
            description="lying with wings folded",
        ),
    },
    requirements=PositionRequirement(
        furniture_types={FurnitureType.BED, FurnitureType.FLOOR},
    ),
    tags={"avian", "wings", "from_behind", "lying"},
    aliases=["winged prone"],
    category="avian",
))


# ============================================================================
# AQUATIC/MERFOLK
# ============================================================================

register(PositionDefinition(
    key="mer_shallow_water",
    name="Shallow Water Mating",
    description="In shallow water - merfolk can lie back with tail submerged, partner between.",
    slots={
        "mer": make_slot(
            "mer", "mer",
            posture=Posture.LYING_BACK,
            mobility=Mobility.PASSIVE,
            accesses={"partner": FRONT_FULL},
            exposed={BodyZone.FACE, BodyZone.CHEST, BodyZone.BREASTS, BodyZone.GROIN},
            description="floating on their back",
        ),
        "partner": make_slot(
            "partner", "partner",
            posture=Posture.KNEELING,
            mobility=Mobility.ACTIVE,
            accesses={"mer": FRONT_FULL | {BodyZone.TAIL}},
            exposed={BodyZone.FACE, BodyZone.CHEST, BodyZone.GROIN},
            can_thrust=True,
            description="between {mer}'s tail",
        ),
    },
    requirements=PositionRequirement(
        furniture_types={FurnitureType.POOL, FurnitureType.BATH},
        furniture_required=True,
    ),
    tags={"aquatic", "water", "merfolk"},
    aliases=["mermaid mating"],
    category="aquatic",
))

register(PositionDefinition(
    key="mer_surface",
    name="At the Surface",
    description="Merfolk at water's edge, humanoid partner on land reaching into water.",
    slots={
        "mer": make_slot(
            "mer", "mer",
            posture=Posture.LYING_FRONT,  # Propped at edge
            mobility=Mobility.LIMITED,
            accesses={"land": {BodyZone.GROIN, BodyZone.THIGHS, BodyZone.HANDS}},
            exposed={BodyZone.FACE, BodyZone.CHEST, BodyZone.BREASTS, BodyZone.GROIN},
            description="at the water's edge",
        ),
        "land": make_slot(
            "land", "on land",
            posture=Posture.KNEELING,
            mobility=Mobility.ACTIVE,
            accesses={"mer": {
                BodyZone.FACE, BodyZone.CHEST, BodyZone.BREASTS,
                BodyZone.GROIN, BodyZone.TAIL,
            }},
            exposed={BodyZone.FACE, BodyZone.CHEST, BodyZone.GROIN},
            can_thrust=True,
            description="kneeling at the edge",
        ),
    },
    requirements=PositionRequirement(
        furniture_types={FurnitureType.POOL, FurnitureType.BATH},
        furniture_required=True,
    ),
    tags={"aquatic", "water", "edge", "interspecies"},
    aliases=["poolside mer", "edge mating"],
    category="aquatic",
))


# ============================================================================
# MULTI-LIMBED
# ============================================================================

register(PositionDefinition(
    key="multi_arm_embrace",
    name="Many-Armed Embrace",
    description="Multi-limbed partner wraps multiple arms around partner, accessing everywhere.",
    slots={
        "multi": make_slot(
            "multi", "multi-armed",
            posture=Posture.STANDING,
            mobility=Mobility.ACTIVE,
            accesses={"wrapped": ALL_ZONES},  # Extra arms reach everywhere
            exposed={BodyZone.BACK_UPPER},
            can_thrust=True,
            controls_pace=True,
            description="embracing {wrapped} with many arms",
        ),
        "wrapped": make_slot(
            "wrapped", "wrapped",
            posture=Posture.STANDING,
            mobility=Mobility.HELD,
            accesses={"multi": {BodyZone.CHEST, BodyZone.FACE, BodyZone.SHOULDERS}},
            exposed={BodyZone.FACE},  # Surrounded by arms
            hands_free=False,  # Arms pinned
            description="held in {multi}'s many arms",
        ),
    },
    requirements=PositionRequirement(),
    tags={"multi_limbed", "embrace", "overwhelming"},
    aliases=["spider embrace", "many hands"],
    category="special",
))


# Update position count
from .library import POSITION_COUNT
