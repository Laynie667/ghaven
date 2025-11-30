"""
Body Parts - Sexual and Reproductive

This module defines all sexual/reproductive parts with:
- Less clinical naming (cock, pussy, ass, balls, etc.)
- Orifices as first-class mechanical concepts
- Detailed penetration/arousal mechanics
- Species-specific genital variations

ORIFICE MECHANICS:
Every orifice (mouth, pussy, ass) has:
- Base depth (how deep it goes)
- Base stretch (natural capacity)
- Current stretch (can increase with use/arousal)
- Tightness recovery (how fast it returns to baseline)
- Wetness/lubrication (natural or applied)
- Sensitivity zones

PENETRATOR MECHANICS:
Every penetrator (cock types, fingers, toys) has:
- Length (how deep it can go)
- Girth (how much it stretches)
- Shape characteristics (knot, flare, ridges, barbs)
- Arousal states (soft, chubbed, hard, throbbing)
"""

from dataclasses import dataclass, field
from typing import List, Dict, Optional, Set
from enum import Enum


# =============================================================================
# ENUMS FOR SEXUAL MECHANICS
# =============================================================================

class ArousalState(Enum):
    """Arousal states for genitals."""
    SOFT = "soft"
    CHUBBED = "chubbed"      # Starting to get interested
    HALF = "half"            # Half-mast
    HARD = "hard"            # Fully erect
    THROBBING = "throbbing"  # Edge/desperate
    
    # Female equivalents
    DRY = "dry"
    INTERESTED = "interested"
    WET = "wet"
    DRIPPING = "dripping"
    GUSHING = "gushing"


class OrificeState(Enum):
    """States for orifices."""
    VIRGIN = "virgin"        # Never penetrated
    TIGHT = "tight"          # Minimal use
    NORMAL = "normal"        # Average
    RELAXED = "relaxed"      # Well-used but recovers
    LOOSE = "loose"          # Permanently stretched
    GAPING = "gaping"        # Currently stretched open
    PROLAPSED = "prolapsed"  # Extreme (optional mechanic)


class KnotState(Enum):
    """States for knots."""
    DEFLATED = "deflated"
    SWELLING = "swelling"
    FULL = "full"
    LOCKED = "locked"        # Inside an orifice
    DEFLATING = "deflating"


# =============================================================================
# ORIFICE MECHANICS DATACLASS
# =============================================================================

@dataclass
class OrificeMechanics:
    """
    Mechanical properties of an orifice.
    
    These values are used for:
    - Penetration checks (can X fit in Y?)
    - Pleasure calculations
    - Stretch/recovery over time
    - Knotting/locking mechanics
    """
    
    # === BASE STATS (set by part definition) ===
    base_depth: float = 6.0          # Inches of depth at rest
    max_depth: float = 10.0          # Maximum possible depth (cervix/limit)
    base_girth_capacity: float = 1.5 # Inches of girth at comfortable fit
    max_girth_capacity: float = 4.0  # Maximum before damage risk
    
    # === CURRENT STATE (changes with use) ===
    current_stretch: float = 0.0     # How much currently stretched beyond base
    stretch_recovery_rate: float = 1.0  # Points per hour returned to baseline
    
    # === WETNESS/LUBRICATION ===
    natural_lubrication: float = 0.5 # 0.0 = none, 1.0 = very wet naturally
    current_wetness: float = 0.0     # Current lubrication level
    wetness_from_arousal: bool = True  # Does arousal increase wetness?
    
    # === SENSITIVITY ===
    base_sensitivity: float = 1.0    # Multiplier for pleasure
    sensitivity_zones: List[str] = field(default_factory=list)  # "entrance", "g-spot", "deep"
    
    # === STATE TRACKING ===
    is_virgin: bool = True
    times_penetrated: int = 0
    largest_taken_girth: float = 0.0
    largest_taken_length: float = 0.0
    
    # === SPECIAL FLAGS ===
    can_prolapse: bool = False       # Extreme content flag
    can_gape: bool = True            # Can be left open after use
    accepts_knot: bool = True        # Can take and lock on knots
    accepts_eggs: bool = False       # For oviposition content
    can_birth: bool = False          # For pregnancy content


@dataclass 
class PenetratorMechanics:
    """
    Mechanical properties of a penetrator (cock, toy, tentacle, etc.)
    
    Used for:
    - Fit calculations with orifices
    - Arousal state tracking
    - Knotting mechanics
    - Pleasure calculations
    """
    
    # === SIZE (at full arousal) ===
    length_soft: float = 3.0         # Inches when soft
    length_hard: float = 6.0         # Inches when fully hard
    girth_soft: float = 1.0          # Circumference soft
    girth_hard: float = 1.5          # Circumference hard
    
    # === SHAPE CHARACTERISTICS ===
    has_knot: bool = False
    knot_girth_deflated: float = 0.0
    knot_girth_full: float = 0.0
    knot_position: float = 0.0       # Inches from base
    
    has_flare: bool = False          # Equine flare
    flare_girth_soft: float = 0.0
    flare_girth_hard: float = 0.0
    
    has_barbs: bool = False          # Feline barbs
    barb_intensity: float = 0.0      # Pain/pleasure modifier
    
    has_ridges: bool = False         # Ridged/ribbed
    ridge_count: int = 0
    
    is_prehensile: bool = False      # Can move/grip on its own
    is_tapered: bool = False         # Pointed tip, easier entry
    
    # === AROUSAL STATE ===
    current_arousal: ArousalState = ArousalState.SOFT
    arousal_speed: float = 1.0       # How fast it gets hard
    refractory_period: float = 5.0   # Minutes before can get hard again
    
    # === PRODUCTION ===
    precum_rate: float = 0.5         # How much precum
    cum_volume: float = 1.0          # Relative cum amount (1.0 = average)
    cum_recharge_rate: float = 1.0   # How fast balls refill
    current_cum_stored: float = 1.0  # 0.0-1.0, percentage full
    
    # === SENSITIVITY ===
    base_sensitivity: float = 1.0
    sensitivity_zones: List[str] = field(default_factory=lambda: ["tip", "shaft", "base"])


# =============================================================================
# SEXUAL PART DEFINITION
# =============================================================================

@dataclass
class SexualPartDefinition:
    """
    Extended part definition for sexual parts.
    Includes all standard part fields plus sexual mechanics.
    """
    
    # === IDENTITY ===
    key: str                          # Unique identifier
    name: str                         # Display name (cock, pussy, ass, etc.)
    plural: str = ""                  # Plural form
    aliases: List[str] = field(default_factory=list)  # Alt names (dick, prick, member)
    
    # === HIERARCHY ===
    parent: Optional[str] = None
    side: str = "center"
    
    # === PART TYPE ===
    is_orifice: bool = False          # Can be penetrated
    is_penetrator: bool = False       # Can penetrate
    is_internal: bool = False
    is_paired: bool = False
    
    # === MECHANICS (for orifices) ===
    orifice_defaults: Optional[OrificeMechanics] = None
    
    # === MECHANICS (for penetrators) ===
    penetrator_defaults: Optional[PenetratorMechanics] = None
    
    # === DISPLAY ===
    default_desc: str = ""
    size_options: List[str] = field(default_factory=list)
    
    # === AROUSAL DESCRIPTIONS ===
    # Maps arousal state to description modifier
    arousal_descs: Dict[str, str] = field(default_factory=dict)


# =============================================================================
# ORIFICES - THE THREE HOLES
# =============================================================================

# -----------------------------------------------------------------------------
# MOUTH (universal orifice)
# -----------------------------------------------------------------------------

MOUTH_ORIFICE = SexualPartDefinition(
    key="mouth",
    name="mouth",
    aliases=["lips", "maw", "muzzle"],
    parent="face",
    is_orifice=True,
    orifice_defaults=OrificeMechanics(
        base_depth=4.0,              # Throat depth varies
        max_depth=8.0,               # Deep throat
        base_girth_capacity=1.5,
        max_girth_capacity=3.0,      # Jaw only opens so wide
        natural_lubrication=0.8,     # Saliva
        wetness_from_arousal=True,   # Drooling when aroused
        sensitivity_zones=["lips", "tongue", "throat"],
        can_prolapse=False,
        can_gape=False,              # Mouth closes
        accepts_knot=True,           # Can be knotted (stuck)
        accepts_eggs=False,
        can_birth=False,
    ),
    arousal_descs={
        "dry": "closed",
        "interested": "slightly parted",
        "wet": "open and wet",
        "dripping": "drooling",
        "gushing": "drooling heavily",
    },
)

# TODO [ORAL_MECHANICS]: Implement oral sex mechanics
# - Gag reflex check based on depth vs throat tolerance
# - Training to suppress gag reflex over time
# - Jaw fatigue for extended use
# - Tooth scraping risk (skill check?)
# - Tongue skill for pleasure multiplier
# - Deep throat bonus/achievement
# - Face-fucking pace/roughness tolerance
# - Lip seal quality for suction
# - Drool production based on arousal + activity
# - Voice muffling when mouth is full
# - Breathing difficulty at various depths
# - Choking/gagging sounds and effects

# -----------------------------------------------------------------------------
# PUSSY / CUNT / VAGINA (female orifice)
# -----------------------------------------------------------------------------

PUSSY = SexualPartDefinition(
    key="pussy",
    name="pussy",
    plural="pussies",
    aliases=["cunt", "slit", "sex", "cunny", "snatch", "twat", "honeypot", "flower"],
    parent="groin",
    is_orifice=True,
    orifice_defaults=OrificeMechanics(
        base_depth=5.0,              # Average vaginal depth
        max_depth=8.0,               # Tenting during arousal
        base_girth_capacity=1.25,    # Virgin/tight
        max_girth_capacity=4.0,      # Can stretch significantly
        natural_lubrication=0.6,
        wetness_from_arousal=True,   # Gets wet when turned on
        sensitivity_zones=["entrance", "g-spot", "a-spot", "cervix", "clit"],
        can_prolapse=True,           # Extreme content
        can_gape=True,
        accepts_knot=True,
        accepts_eggs=True,           # Oviposition
        can_birth=True,
    ),
    size_options=["tiny", "small", "average", "puffy", "large"],
    arousal_descs={
        "dry": "dry",
        "interested": "slightly damp",
        "wet": "wet and glistening",
        "dripping": "dripping wet",
        "gushing": "absolutely soaked, dripping down her thighs",
    },
)

# TODO [PUSSY_MECHANICS]: Implement vaginal mechanics
# - Wetness generation based on arousal level
# - Tenting (depth increase) when highly aroused
# - Kegel/squeeze mechanics for pleasure bonus
# - G-spot and A-spot stimulation tracking
# - Cervix bumping (pleasure or pain depending on preference)
# - Virginity loss event with optional hymen
# - Tightness recovery over time (hours to days)
# - Permanent stretch from extreme sizes (optional)
# - Queefing after certain activities
# - Post-orgasm sensitivity spike
# - Multiple orgasm tracking
# - Squirting mechanic (rare, trainable?)
# - Cream/discharge descriptions based on arousal cycle
# - Heat cycle integration (increased sensitivity, wetness)

# -----------------------------------------------------------------------------
# ASSHOLE / ASS / BACKDOOR (universal orifice)
# -----------------------------------------------------------------------------

ASSHOLE = SexualPartDefinition(
    key="asshole",
    name="asshole",
    aliases=["ass", "anus", "backdoor", "rear", "tailhole", "pucker", "rosebud", "butthole"],
    parent="buttocks",
    is_orifice=True,
    orifice_defaults=OrificeMechanics(
        base_depth=6.0,              # Rectum depth
        max_depth=12.0,              # Deep anal
        base_girth_capacity=0.75,    # Naturally tight
        max_girth_capacity=4.0,      # Can be trained
        natural_lubrication=0.0,     # No natural lube!
        wetness_from_arousal=False,  # Still no natural lube
        sensitivity_zones=["entrance", "prostate", "deep"],
        can_prolapse=True,
        can_gape=True,
        accepts_knot=True,
        accepts_eggs=True,
        can_birth=False,             # Not for babies, but eggs maybe
    ),
    arousal_descs={
        "dry": "clenched tight",
        "interested": "relaxing slightly",
        "wet": "relaxed and ready",  # From applied lube
        "dripping": "lubed and loose",
        "gushing": "gaping and dripping with lube",
    },
)

# TODO [ANAL_MECHANICS]: Implement anal mechanics
# - NO natural lubrication - require lube or saliva
# - Lube depletion over time/thrusts
# - Damage risk without adequate lubrication
# - Sphincter training for easier entry
# - Gaping after use (duration based on stretch)
# - Prostate stimulation for male bodies (pleasure multiplier)
# - Enema/cleaning state tracking
# - "Clean" vs "risky" state
# - Double penetration with pussy (stretch interaction)
# - Prolapse risk at extreme sizes (optional toggle)
# - Plug wearing for training/keeping loose
# - Soreness/recovery tracking
# - Fisting milestone tracking

# -----------------------------------------------------------------------------
# CLOACA (reptile/avian combined orifice)
# -----------------------------------------------------------------------------

CLOACA_ORIFICE = SexualPartDefinition(
    key="cloaca",
    name="cloaca",
    aliases=["vent", "slit"],
    parent="groin",
    is_orifice=True,
    orifice_defaults=OrificeMechanics(
        base_depth=5.0,
        max_depth=8.0,
        base_girth_capacity=1.0,
        max_girth_capacity=3.5,
        natural_lubrication=0.4,     # Some species have lubricating glands
        wetness_from_arousal=True,
        sensitivity_zones=["entrance", "deep"],
        can_prolapse=True,
        can_gape=True,
        accepts_knot=True,
        accepts_eggs=True,           # Egg-laying species
        can_birth=True,              # For live-bearing reptiles
    ),
    arousal_descs={
        "dry": "a thin slit",
        "interested": "a slightly parted slit",
        "wet": "parted and glistening",
        "dripping": "spread open and wet",
    },
)

# TODO [CLOACA_MECHANICS]: Implement cloaca mechanics
# - Combined waste/reproduction functions
# - Hemipenes acceptance for reptiles
# - Egg-laying capacity and mechanics
# - Different from mammalian reproduction
# - Can function as both penetrator receiver and egg depositor


# =============================================================================
# COCKS - PENETRATORS BY TYPE
# =============================================================================

# -----------------------------------------------------------------------------
# HUMAN COCK
# -----------------------------------------------------------------------------

COCK_HUMAN = SexualPartDefinition(
    key="cock_human",
    name="cock",
    aliases=["dick", "penis", "member", "shaft", "prick", "manhood"],
    parent="groin",
    is_penetrator=True,
    penetrator_defaults=PenetratorMechanics(
        length_soft=3.5,
        length_hard=6.0,             # Average human
        girth_soft=1.0,
        girth_hard=1.5,              # ~4.7" circumference
        has_knot=False,
        has_flare=False,
        has_barbs=False,
        is_tapered=False,
        sensitivity_zones=["tip", "frenulum", "shaft", "base"],
    ),
    size_options=["tiny", "small", "average", "large", "huge", "massive"],
    arousal_descs={
        "soft": "soft and hanging",
        "chubbed": "starting to swell",
        "half": "at half-mast",
        "hard": "standing at full attention",
        "throbbing": "rock hard and twitching",
    },
)

# TODO [COCK_MECHANICS]: Implement cock mechanics
# - Arousal progression (soft -> chubbed -> half -> hard -> throbbing)
# - Arousal decay when not stimulated
# - Precum generation based on arousal level + time
# - Edging mechanic (staying at throbbing without release)
# - Blue balls effect from extended edging
# - Refractory period after orgasm
# - Multiple orgasm capability (rare, trainable?)
# - Sensitivity spike right after orgasm
# - Morning wood / random arousal events
# - Size variation based on arousal (grower vs shower)
# - Circumcised vs uncircumcised variants
# - Foreskin retraction state

# -----------------------------------------------------------------------------
# CANINE COCK (knot)
# -----------------------------------------------------------------------------

COCK_CANINE = SexualPartDefinition(
    key="cock_canine",
    name="canine cock",
    aliases=["dog cock", "wolf cock", "red rocket", "knotted cock"],
    parent="groin",
    is_penetrator=True,
    penetrator_defaults=PenetratorMechanics(
        length_soft=2.0,             # Mostly in sheath
        length_hard=7.0,
        girth_soft=0.5,
        girth_hard=1.5,
        has_knot=True,
        knot_girth_deflated=1.5,     # Same as shaft
        knot_girth_full=3.0,         # Doubles in size
        knot_position=1.0,           # 1 inch from base
        is_tapered=True,             # Pointed tip
        sensitivity_zones=["tip", "shaft", "knot"],
    ),
    size_options=["small", "average", "large", "huge", "alpha"],
    arousal_descs={
        "soft": "hidden in its sheath",
        "chubbed": "peeking from its sheath",
        "half": "emerging, red and tapered",
        "hard": "fully unsheathed, knot visible",
        "throbbing": "throbbing, knot swelling",
    },
)

# TODO [KNOT_MECHANICS]: Implement knotting mechanics
# - Knot inflation timing (swells during/after penetration)
# - Knot lock check: knot_girth vs orifice_capacity
# - Lock duration: 5-30 minutes depending on size difference
# - Forced pull-out damage (to both parties)
# - Knot deflation over time
# - Cum pumping while locked (multiple spurts)
# - Breeding bonus while knotted (for pregnancy system)
# - Knot addiction/preference tracking (kink system)
# - Squeeze/clench effects on knot deflation time
# - Emergency deflation (ice water, distraction)

# -----------------------------------------------------------------------------
# EQUINE COCK (flare)
# -----------------------------------------------------------------------------

COCK_EQUINE = SexualPartDefinition(
    key="cock_equine",
    name="horse cock",
    aliases=["equine cock", "stallion cock", "horsecock"],
    parent="groin",
    is_penetrator=True,
    penetrator_defaults=PenetratorMechanics(
        length_soft=8.0,             # Still big soft
        length_hard=18.0,            # Average horse
        girth_soft=2.0,
        girth_hard=3.0,
        has_flare=True,
        flare_girth_soft=3.0,
        flare_girth_hard=4.5,        # Flares out significantly
        is_tapered=False,            # Blunt, flat head
        sensitivity_zones=["tip", "medial ring", "shaft", "base"],
        cum_volume=3.0,              # Horses cum a lot
    ),
    size_options=["average", "large", "huge", "monster", "impossible"],
    arousal_descs={
        "soft": "hanging heavily from its sheath",
        "chubbed": "dropping from the sheath",
        "half": "swinging free, head visible",
        "hard": "fully erect, flat head flaring",
        "throbbing": "flared wide and pulsing",
    },
)

# TODO [FLARE_MECHANICS]: Implement flare mechanics
# - Flare expansion during orgasm
# - Medial ring stimulation
# - Extreme depth requirements
# - Womb entry possible at full insertion
# - Cervix dilation check for deep penetration
# - Belly bulge visual at full insertion
# - Cum inflation due to volume
# - Recovery time longer due to size
# - Size queen achievement tracking

# -----------------------------------------------------------------------------
# FELINE COCK (barbs)
# -----------------------------------------------------------------------------

COCK_FELINE = SexualPartDefinition(
    key="cock_feline",
    name="feline cock",
    aliases=["cat cock", "barbed cock"],
    parent="groin",
    is_penetrator=True,
    penetrator_defaults=PenetratorMechanics(
        length_soft=1.5,
        length_hard=5.0,             # Cats are smaller
        girth_soft=0.5,
        girth_hard=1.0,
        has_barbs=True,
        barb_intensity=0.5,          # Pain/pleasure modifier
        is_tapered=True,
        sensitivity_zones=["tip", "barbs", "shaft"],
        cum_volume=0.3,              # Small loads
        arousal_speed=2.0,           # Quick to arousal
    ),
    size_options=["small", "average", "large"],
    arousal_descs={
        "soft": "retracted into its sheath",
        "chubbed": "tip emerging",
        "half": "extending, barbs visible",
        "hard": "fully erect, barbs raised",
        "throbbing": "quivering, barbs flared",
    },
)

# TODO [BARB_MECHANICS]: Implement barb mechanics
# - Barbs cause pain/pleasure on withdrawal (not entry)
# - Barbs induce ovulation in felines (breeding mechanic)
# - Scratching sensation description
# - Barb intensity affected by arousal
# - Some find barbs pleasurable (kink flag)
# - Withdrawal speed affects sensation
# - Possible minor injury from rough withdrawal

# -----------------------------------------------------------------------------
# REPTILE COCK / HEMIPENES
# -----------------------------------------------------------------------------

COCK_REPTILE = SexualPartDefinition(
    key="cock_reptile",
    name="reptile cock",
    aliases=["hemipenis", "lizard cock", "snake cock"],
    parent="groin",
    is_penetrator=True,
    penetrator_defaults=PenetratorMechanics(
        length_soft=0.0,             # Fully internal
        length_hard=6.0,
        girth_soft=0.0,
        girth_hard=1.25,
        has_ridges=True,
        ridge_count=6,
        is_tapered=True,
        sensitivity_zones=["tip", "ridges", "base"],
    ),
    size_options=["small", "average", "large"],
    arousal_descs={
        "soft": "hidden within the cloaca",
        "chubbed": "beginning to evert",
        "half": "partially emerged",
        "hard": "fully everted, ridged and glistening",
        "throbbing": "pulsing, ready to breed",
    },
)

HEMIPENES = SexualPartDefinition(
    key="hemipenes",
    name="hemipenes",
    aliases=["twin cocks", "forked cocks"],
    parent="groin",
    is_penetrator=True,
    penetrator_defaults=PenetratorMechanics(
        length_soft=0.0,
        length_hard=5.0,             # Each one
        girth_soft=0.0,
        girth_hard=1.0,              # Each one
        has_ridges=True,
        ridge_count=4,
        is_tapered=True,
    ),
    arousal_descs={
        "soft": "hidden within the cloaca",
        "hard": "both emerged, glistening and ready",
    },
)

# TODO [HEMIPENES_MECHANICS]: Implement hemipenes mechanics
# - Two independent penetrators
# - Can use one or both
# - Double penetration of same orifice possible
# - Alternating thrust pattern
# - Independent arousal tracking?

# -----------------------------------------------------------------------------
# DOLPHIN COCK (prehensile)
# -----------------------------------------------------------------------------

COCK_DOLPHIN = SexualPartDefinition(
    key="cock_dolphin",
    name="dolphin cock",
    aliases=["prehensile cock", "cetacean cock"],
    parent="groin",
    is_penetrator=True,
    penetrator_defaults=PenetratorMechanics(
        length_soft=6.0,
        length_hard=12.0,
        girth_soft=1.5,
        girth_hard=2.0,
        is_prehensile=True,          # Can move on its own
        is_tapered=True,
        sensitivity_zones=["tip", "shaft"],
        cum_volume=2.0,
    ),
    size_options=["average", "large", "huge"],
    arousal_descs={
        "soft": "retracted in its slit",
        "hard": "extended and seeking, moving on its own",
        "throbbing": "writhing and prehensile",
    },
)

# TODO [PREHENSILE_MECHANICS]: Implement prehensile mechanics
# - Can seek and find orifices on its own
# - No hands needed for penetration
# - Can grip and pull
# - Thrusting independent of hip movement
# - Curved/seeking behavior
# - Can "look around" for entrance

# -----------------------------------------------------------------------------
# TENTACLE COCK
# -----------------------------------------------------------------------------

COCK_TENTACLE = SexualPartDefinition(
    key="cock_tentacle",
    name="tentacle cock",
    aliases=["tentacock", "tendril"],
    parent="groin",
    is_penetrator=True,
    penetrator_defaults=PenetratorMechanics(
        length_soft=8.0,
        length_hard=14.0,            # Very long
        girth_soft=1.0,
        girth_hard=1.5,
        is_prehensile=True,
        is_tapered=True,
        has_ridges=True,
        ridge_count=20,              # Suckers/ridges
        sensitivity_zones=["tip", "suckers", "entire_length"],
        cum_volume=2.5,
    ),
    size_options=["average", "large", "huge", "massive"],
    arousal_descs={
        "soft": "coiled loosely",
        "hard": "writhing and reaching",
        "throbbing": "pulsing along its entire length",
    },
)

# TODO [TENTACLE_MECHANICS]: Implement tentacle mechanics
# - Extreme flexibility for unusual positions
# - Can reach around obstacles
# - Multiple simultaneous if character has multiple
# - Sucker stimulation
# - Constriction/gripping
# - Oviposition variant (egg-laying tentacle)


# =============================================================================
# SUPPORTING PARTS
# =============================================================================

# -----------------------------------------------------------------------------
# BALLS / TESTICLES
# -----------------------------------------------------------------------------

BALLS = SexualPartDefinition(
    key="balls",
    name="balls",
    aliases=["testicles", "nuts", "sack", "testes", "nads"],
    parent="groin",
    is_penetrator=False,
    is_orifice=False,
    size_options=["tiny", "small", "average", "large", "huge", "massive"],
    default_desc="A pair of balls.",
    arousal_descs={
        "soft": "hanging loosely",
        "hard": "drawn up tight",
        "throbbing": "churning and tight",
    },
)

# TODO [BALLS_MECHANICS]: Implement testicle mechanics
# - Cum production rate
# - Cum storage capacity
# - Fullness tracking (time since last orgasm)
# - "Full" bonus to cum volume
# - "Drained" state after multiple orgasms
# - Ball size affects cum capacity
# - Sensitivity (painful if struck)
# - Draw-up reflex near orgasm
# - Blue balls from extended denial

SCROTUM = SexualPartDefinition(
    key="scrotum",
    name="scrotum",
    aliases=["sack", "ballsack"],
    parent="balls",
    default_desc="The skin containing the testicles.",
)

# -----------------------------------------------------------------------------
# SHEATH
# -----------------------------------------------------------------------------

SHEATH = SexualPartDefinition(
    key="sheath",
    name="sheath",
    aliases=["prepuce"],
    parent="groin",
    default_desc="A protective sheath for the penis.",
    arousal_descs={
        "soft": "containing the cock fully",
        "chubbed": "with the tip peeking out",
        "hard": "stretched around the base of the emerged cock",
    },
)

# TODO [SHEATH_MECHANICS]: Implement sheath mechanics
# - Sheath stuffing kink
# - Sheath play sensitivity
# - Cleaning/hygiene
# - Sheath size relative to cock size

# -----------------------------------------------------------------------------
# KNOT (as separate trackable part)
# -----------------------------------------------------------------------------

KNOT = SexualPartDefinition(
    key="knot",
    name="knot",
    aliases=["bulge", "bulb"],
    parent="cock_canine",
    size_options=["small", "average", "large", "huge"],
    arousal_descs={
        "soft": "deflated at the base",
        "hard": "swelling visibly",
        "throbbing": "fully engorged and pulsing",
    },
)

# -----------------------------------------------------------------------------
# FORESKIN
# -----------------------------------------------------------------------------

FORESKIN = SexualPartDefinition(
    key="foreskin",
    name="foreskin",
    aliases=["hood"],
    parent="cock_human",
    default_desc="Retractable foreskin covering the glans.",
)

# -----------------------------------------------------------------------------
# GLANS / COCKHEAD
# -----------------------------------------------------------------------------

GLANS = SexualPartDefinition(
    key="glans",
    name="cockhead",
    aliases=["head", "tip", "glans"],
    parent="cock_human",
    default_desc="The sensitive head of the cock.",
)

# -----------------------------------------------------------------------------
# CLIT
# -----------------------------------------------------------------------------

CLIT = SexualPartDefinition(
    key="clit",
    name="clit",
    aliases=["clitoris", "button", "nub", "pearl"],
    parent="pussy",
    size_options=["tiny", "small", "average", "large", "huge"],
    default_desc="A sensitive nub at the top of the slit.",
    arousal_descs={
        "dry": "hidden under its hood",
        "interested": "peeking out",
        "wet": "swollen and exposed",
        "dripping": "throbbing and erect",
    },
)

# TODO [CLIT_MECHANICS]: Implement clit mechanics
# - Swelling with arousal
# - Hood retraction
# - Direct stimulation sensitivity (can be too much)
# - Clit orgasm vs penetration orgasm tracking
# - Large clit can be "jerked off"
# - Hyper clit variant (cock-like size)

CLIT_HOOD = SexualPartDefinition(
    key="clit_hood",
    name="clitoral hood",
    aliases=["hood"],
    parent="clit",
    default_desc="A small hood of skin protecting the clitoris.",
)

# -----------------------------------------------------------------------------
# LABIA
# -----------------------------------------------------------------------------

LABIA = SexualPartDefinition(
    key="labia",
    name="lips",
    aliases=["labia", "pussy lips", "petals", "folds"],
    parent="pussy",
    size_options=["small", "average", "large", "puffy"],
    default_desc="The outer lips of the pussy.",
    arousal_descs={
        "dry": "closed together",
        "wet": "parted and glistening",
        "dripping": "spread and dripping",
    },
)

# -----------------------------------------------------------------------------
# INTERNAL FEMALE
# -----------------------------------------------------------------------------

CERVIX = SexualPartDefinition(
    key="cervix",
    name="cervix",
    parent="pussy",
    is_internal=True,
    default_desc="The entrance to the womb.",
)

# TODO [CERVIX_MECHANICS]: Implement cervix mechanics
# - Cervix depth varies with arousal (tenting)
# - Cervix bumping: pleasure or pain (preference flag)
# - Cervix penetration (extreme, requires dilation)
# - Cervix dilation for birth/extreme play
# - Mucus plug during pregnancy
# - Cervix position in cycle (fertility tracking)

WOMB = SexualPartDefinition(
    key="womb",
    name="womb",
    aliases=["uterus"],
    parent="cervix",
    is_internal=True,
    default_desc="The reproductive chamber.",
)

# TODO [WOMB_MECHANICS]: Implement womb mechanics  
# - Cum storage (creampie tracking)
# - Cum capacity before overflow
# - Womb bulge at extreme cum amounts
# - Fertility state
# - Pregnancy capacity (single, twins, litter)
# - Egg implantation for oviposition
# - Womb tattoo/marking (magical brand)
# - "Claiming" mechanic

OVARIES = SexualPartDefinition(
    key="ovaries",
    name="ovaries",
    parent="womb",
    is_internal=True,
    is_paired=True,
    default_desc="Egg-producing organs.",
)

# TODO [OVARY_MECHANICS]: Implement ovary mechanics
# - Egg production rate
# - Ovulation timing
# - Fertility cycle
# - Egg count remaining (biological clock?)

# -----------------------------------------------------------------------------
# BREASTS
# -----------------------------------------------------------------------------

BREAST_LEFT = SexualPartDefinition(
    key="breast_left",
    name="left breast",
    aliases=["left tit", "left boob"],
    parent="chest",
    side="left",
    is_paired=True,
    size_options=["flat", "tiny", "small", "average", "large", "huge", "massive", "hyper"],
)

BREAST_RIGHT = SexualPartDefinition(
    key="breast_right",
    name="right breast",
    aliases=["right tit", "right boob"],
    parent="chest",
    side="right",
    is_paired=True,
    size_options=["flat", "tiny", "small", "average", "large", "huge", "massive", "hyper"],
)

NIPPLE_LEFT = SexualPartDefinition(
    key="nipple_left",
    name="left nipple",
    aliases=["left nip"],
    parent="breast_left",
    side="left",
    size_options=["tiny", "small", "average", "large", "puffy"],
    arousal_descs={
        "soft": "soft",
        "hard": "stiff and erect",
        "throbbing": "achingly hard",
    },
)

NIPPLE_RIGHT = SexualPartDefinition(
    key="nipple_right",
    name="right nipple",
    aliases=["right nip"],
    parent="breast_right",
    side="right",
    size_options=["tiny", "small", "average", "large", "puffy"],
)

# TODO [BREAST_MECHANICS]: Implement breast mechanics
# - Bounce physics description
# - Sensitivity (higher during cycle, pregnancy, lactation)
# - Lactation enable/disable
# - Milk production rate
# - Milk storage capacity
# - Engorgement when full
# - Let-down reflex triggers
# - Nipple erection tracking
# - Nipple piercings interaction
# - Breast size affecting various activities
# - Titfuck mechanics

# -----------------------------------------------------------------------------
# NIPPLE PENETRATION (extreme)
# -----------------------------------------------------------------------------

NIPPLE_ORIFICE = SexualPartDefinition(
    key="nipple_orifice",
    name="nipple opening",
    parent="nipple_left",  # Template, applied to both
    is_orifice=True,
    orifice_defaults=OrificeMechanics(
        base_depth=0.5,
        max_depth=2.0,
        base_girth_capacity=0.1,     # Very small
        max_girth_capacity=0.5,      # Can be stretched
        natural_lubrication=0.2,     # Milk if lactating
        can_prolapse=False,
        can_gape=False,
        accepts_knot=False,
        accepts_eggs=False,
    ),
)

# TODO [NIPPLE_PENETRATION]: Implement nipple penetration (extreme content)
# - Only enabled with specific flag
# - Requires significant stretching/training
# - Sound (medical) insertion
# - Milk production interaction
# - Pain/pleasure balance


# =============================================================================
# OVIPOSITION PARTS
# =============================================================================

OVIPOSITOR = SexualPartDefinition(
    key="ovipositor",
    name="ovipositor",
    aliases=["egg-layer", "breeding tube"],
    parent="groin",
    is_penetrator=True,
    penetrator_defaults=PenetratorMechanics(
        length_soft=4.0,
        length_hard=8.0,
        girth_soft=0.5,
        girth_hard=1.0,              # Thin for eggs
        is_tapered=True,
        is_prehensile=True,
        sensitivity_zones=["tip", "egg_channel"],
    ),
    default_desc="A tubular organ for depositing eggs.",
)

# TODO [OVIPOSITION_MECHANICS]: Implement oviposition mechanics
# - Egg production rate
# - Egg size options
# - Egg capacity (how many stored)
# - Egg laying process (time, stretch)
# - Receiving eggs mechanics
# - Egg incubation in recipient
# - Egg hardness (soft/hard shell)
# - Hatching (or just passing them)
# - Forced oviposition (parasitic)
# - Consensual egg-play


# =============================================================================
# PROSTATE (for anal pleasure on male bodies)
# =============================================================================

PROSTATE = SexualPartDefinition(
    key="prostate",
    name="prostate",
    aliases=["p-spot", "male g-spot"],
    parent="asshole",
    is_internal=True,
    default_desc="A sensitive gland accessible through the rectum.",
)

# TODO [PROSTATE_MECHANICS]: Implement prostate mechanics
# - Only on male/herm bodies
# - Stimulation multiplier for anal
# - Prostate orgasm (different from penile)
# - Prostate milking
# - Hands-free orgasm from prostate alone
# - Cum dribbling vs shooting from prostate stimulation


# =============================================================================
# REGISTRY
# =============================================================================

SEXUAL_PART_REGISTRY: Dict[str, SexualPartDefinition] = {
    # Orifices
    "mouth": MOUTH_ORIFICE,
    "pussy": PUSSY,
    "asshole": ASSHOLE,
    "cloaca": CLOACA_ORIFICE,
    
    # Cocks
    "cock_human": COCK_HUMAN,
    "cock_canine": COCK_CANINE,
    "cock_equine": COCK_EQUINE,
    "cock_feline": COCK_FELINE,
    "cock_reptile": COCK_REPTILE,
    "hemipenes": HEMIPENES,
    "cock_dolphin": COCK_DOLPHIN,
    "cock_tentacle": COCK_TENTACLE,
    
    # Supporting male
    "balls": BALLS,
    "scrotum": SCROTUM,
    "sheath": SHEATH,
    "knot": KNOT,
    "foreskin": FORESKIN,
    "glans": GLANS,
    
    # Supporting female
    "clit": CLIT,
    "clit_hood": CLIT_HOOD,
    "labia": LABIA,
    "cervix": CERVIX,
    "womb": WOMB,
    "ovaries": OVARIES,
    
    # Breasts
    "breast_left": BREAST_LEFT,
    "breast_right": BREAST_RIGHT,
    "nipple_left": NIPPLE_LEFT,
    "nipple_right": NIPPLE_RIGHT,
    "nipple_orifice": NIPPLE_ORIFICE,
    
    # Special
    "ovipositor": OVIPOSITOR,
    "prostate": PROSTATE,
}


def get_sexual_part(key: str) -> Optional[SexualPartDefinition]:
    """Get a sexual part definition by key."""
    return SEXUAL_PART_REGISTRY.get(key)


def get_orifices() -> List[SexualPartDefinition]:
    """Get all orifice parts."""
    return [p for p in SEXUAL_PART_REGISTRY.values() if p.is_orifice]


def get_penetrators() -> List[SexualPartDefinition]:
    """Get all penetrator parts."""
    return [p for p in SEXUAL_PART_REGISTRY.values() if p.is_penetrator]


def get_cock_by_category(category: str) -> Optional[SexualPartDefinition]:
    """
    Get cock definition by genital category.
    
    Args:
        category: human, canine, equine, feline, reptile, aquatic, tentacle
    
    Returns:
        The appropriate cock definition
    """
    mapping = {
        "human": COCK_HUMAN,
        "canine": COCK_CANINE,
        "equine": COCK_EQUINE,
        "feline": COCK_FELINE,
        "reptile": COCK_REPTILE,
        "aquatic": COCK_DOLPHIN,
        "dolphin": COCK_DOLPHIN,
        "tentacle": COCK_TENTACLE,
        "avian": COCK_REPTILE,       # Birds use cloaca but similar
        "insect": COCK_TENTACLE,     # Closest match
    }
    return mapping.get(category)


# =============================================================================
# GENITAL PART SETS FOR SEX CONFIGS
# =============================================================================

def get_male_parts(genital_category: str) -> List[str]:
    """
    Get the part keys for male genitals of a given category.
    
    Args:
        genital_category: human, canine, equine, etc.
    
    Returns:
        List of part keys to add
    """
    base_cock = f"cock_{genital_category}"
    if genital_category == "aquatic":
        base_cock = "cock_dolphin"
    elif genital_category == "avian":
        return ["cloaca"]  # Birds have cloaca
    
    parts = [base_cock, "balls"]
    
    # Add category-specific parts
    if genital_category == "canine":
        parts.extend(["sheath", "knot"])
    elif genital_category in ("equine", "feline"):
        parts.append("sheath")
    elif genital_category == "human":
        parts.extend(["scrotum", "foreskin", "glans"])
    elif genital_category == "reptile":
        parts = ["hemipenes", "cloaca"]  # Reptiles use cloaca
    
    return parts


def get_female_parts(genital_category: str) -> List[str]:
    """
    Get the part keys for female genitals.
    
    Pussy is pussy regardless of species, but some variations exist.
    """
    if genital_category in ("reptile", "avian"):
        return ["cloaca", "womb", "ovaries"]
    
    return ["pussy", "clit", "clit_hood", "labia", "cervix", "womb", "ovaries"]


def get_breast_parts(count: int = 2) -> List[str]:
    """Get breast part keys."""
    if count <= 2:
        return ["breast_left", "breast_right", "nipple_left", "nipple_right"]
    else:
        # Multi-row breasts would need additional parts defined
        return ["breast_left", "breast_right", "nipple_left", "nipple_right"]

