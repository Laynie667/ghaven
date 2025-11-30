"""
Sexual Mechanics Calculations

This module handles the actual mechanics calculations for:
- Penetration checks (can X fit in Y?)
- Stretch calculations
- Arousal progression
- Pleasure calculations
- Knotting/locking
- Fluids (cum, wetness, etc.)
- Recovery/healing

All mechanical values use consistent units:
- Length: inches
- Girth/circumference: inches
- Time: game ticks (configurable, default 1 tick = 6 seconds)
- Volume: arbitrary units (1.0 = average human cum load)
"""

from dataclasses import dataclass
from typing import Tuple, Optional, List, Dict, Union, TYPE_CHECKING
from enum import Enum

from ..templates.parts_sexual import (
    OrificeMechanics,
    PenetratorMechanics,
    ArousalState,
    OrificeState,
    KnotState,
)

if TYPE_CHECKING:
    from ..state.sexual import OrificeStateData, PenetratorStateData


# =============================================================================
# RESULT TYPES
# =============================================================================

class FitResult(Enum):
    """Result of a penetration fit check."""
    PERFECT = "perfect"          # Fits comfortably
    TIGHT = "tight"              # Fits but stretching
    VERY_TIGHT = "very_tight"    # Barely fits, discomfort/pain
    TOO_BIG = "too_big"          # Cannot fit without injury
    TOO_LONG = "too_long"        # Girth OK but too deep
    IMPOSSIBLE = "impossible"    # Physically cannot fit


@dataclass
class PenetrationResult:
    """Result of a penetration attempt."""
    can_penetrate: bool
    fit: FitResult
    depth_possible: float        # How deep can go
    stretch_amount: float        # How much orifice stretches
    pleasure_giver: float        # Pleasure for penetrator (0.0-1.0)
    pleasure_receiver: float     # Pleasure for receiver (0.0-1.0)
    pain_receiver: float         # Pain for receiver (0.0-1.0)
    message: str                 # Descriptive message
    
    # Special states
    knot_locked: bool = False
    cervix_reached: bool = False
    womb_entered: bool = False


@dataclass
class ArousalChange:
    """Result of arousal change."""
    old_state: ArousalState
    new_state: ArousalState
    pleasure_gained: float
    edging: bool = False         # At max arousal without release
    orgasm: bool = False


# =============================================================================
# CONFIGURATION
# =============================================================================

# Multipliers for various calculations
# These can be adjusted for game balance

STRETCH_PAIN_THRESHOLD = 0.5     # Stretch beyond capacity before pain starts
STRETCH_DAMAGE_THRESHOLD = 1.0   # Stretch beyond capacity before damage risk
LUBRICATION_BONUS = 0.3          # Extra capacity when well-lubricated
AROUSAL_DEPTH_BONUS = 0.2        # Extra depth from arousal (tenting)
VIRGIN_TIGHTNESS_BONUS = 0.3     # Virgins are tighter
RELAXATION_BONUS = 0.2           # Experienced orifices are more relaxed

# Arousal thresholds (pleasure accumulated to change state)
AROUSAL_THRESHOLDS = {
    ArousalState.SOFT: 0.0,
    ArousalState.CHUBBED: 0.2,
    ArousalState.HALF: 0.4,
    ArousalState.HARD: 0.6,
    ArousalState.THROBBING: 0.9,
}

# TODO [CONFIG_SYSTEM]: Make these configurable per-game
# - Allow game owners to adjust difficulty/realism
# - Per-character modifiers (some chars more/less sensitive)
# - Skill-based modifiers (experienced characters)


# =============================================================================
# FIT CALCULATIONS
# =============================================================================

def calculate_fit(
    orifice: OrificeMechanics,
    orifice_state: Union[OrificeState, "OrificeStateData"],
    penetrator: PenetratorMechanics,
    penetrator_arousal: ArousalState,
    lubrication: float = 0.0,
) -> PenetrationResult:
    """
    Calculate if a penetrator can fit in an orifice.
    
    Args:
        orifice: The orifice mechanics (base stats)
        orifice_state: Current state - either OrificeState enum or OrificeStateData object
        penetrator: The penetrator mechanics
        penetrator_arousal: Current arousal of penetrator
        lubrication: Current lubrication level (0.0-1.0)
    
    Returns:
        PenetrationResult with fit analysis
    """
    # Get current sizes based on arousal
    if penetrator_arousal == ArousalState.SOFT:
        pen_length = penetrator.length_soft
        pen_girth = penetrator.girth_soft
    elif penetrator_arousal == ArousalState.CHUBBED:
        pen_length = (penetrator.length_soft + penetrator.length_hard) / 2 * 0.6
        pen_girth = (penetrator.girth_soft + penetrator.girth_hard) / 2 * 0.6
    elif penetrator_arousal == ArousalState.HALF:
        pen_length = (penetrator.length_soft + penetrator.length_hard) / 2
        pen_girth = (penetrator.girth_soft + penetrator.girth_hard) / 2
    else:  # HARD or THROBBING
        pen_length = penetrator.length_hard
        pen_girth = penetrator.girth_hard
    
    # Calculate effective orifice capacity
    base_girth_cap = orifice.base_girth_capacity
    
    # Handle both OrificeState enum and OrificeStateData object
    if isinstance(orifice_state, OrificeState):
        current_orifice_state = orifice_state
        current_stretch = 0.0
    else:
        # It's an OrificeStateData object
        current_orifice_state = orifice_state.orifice_state
        current_stretch = orifice_state.current_stretch
    
    # Adjust for virginity
    if current_orifice_state == OrificeState.VIRGIN:
        base_girth_cap *= (1.0 - VIRGIN_TIGHTNESS_BONUS)
    elif current_orifice_state in (OrificeState.RELAXED, OrificeState.LOOSE):
        base_girth_cap *= (1.0 + RELAXATION_BONUS)
    
    # Adjust for current stretch (if already stretched)
    base_girth_cap += current_stretch
    
    # Adjust for lubrication
    effective_lube = max(lubrication, orifice.natural_lubrication)
    lube_bonus = effective_lube * LUBRICATION_BONUS
    effective_cap = base_girth_cap + lube_bonus
    
    # Calculate depth
    effective_depth = orifice.base_depth
    # TODO: Add arousal-based tenting for vaginas
    
    # Determine fit
    girth_diff = pen_girth - effective_cap
    length_diff = pen_length - effective_depth
    
    # Determine result
    if pen_girth > orifice.max_girth_capacity:
        fit = FitResult.IMPOSSIBLE
        can_penetrate = False
        message = "It's physically impossible to fit."
    elif girth_diff > STRETCH_DAMAGE_THRESHOLD:
        fit = FitResult.TOO_BIG
        can_penetrate = False
        message = "It's too thick - would cause injury."
    elif girth_diff > STRETCH_PAIN_THRESHOLD:
        fit = FitResult.VERY_TIGHT
        can_penetrate = True
        message = "An extremely tight fit that borders on painful."
    elif girth_diff > 0:
        fit = FitResult.TIGHT
        can_penetrate = True
        message = "A tight fit that stretches nicely."
    else:
        fit = FitResult.PERFECT
        can_penetrate = True
        message = "A comfortable fit."
    
    # Check depth
    if can_penetrate and pen_length > orifice.max_depth:
        fit = FitResult.TOO_LONG
        message += " But it's too long to go all the way."
    
    # Calculate pleasure/pain
    if can_penetrate:
        stretch = max(0, girth_diff)
        pleasure_receiver = calculate_pleasure(stretch, effective_lube, orifice.base_sensitivity)
        pain_receiver = calculate_pain(stretch, effective_lube)
        pleasure_giver = calculate_giver_pleasure(fit, penetrator.base_sensitivity)
    else:
        pleasure_receiver = 0.0
        pain_receiver = 0.5 if fit == FitResult.TOO_BIG else 0.0
        pleasure_giver = 0.0
        stretch = 0.0
    
    return PenetrationResult(
        can_penetrate=can_penetrate,
        fit=fit,
        depth_possible=min(pen_length, orifice.max_depth),
        stretch_amount=max(0, girth_diff),
        pleasure_giver=pleasure_giver,
        pleasure_receiver=pleasure_receiver,
        pain_receiver=pain_receiver,
        message=message,
        cervix_reached=pen_length >= orifice.base_depth,
        womb_entered=pen_length >= orifice.max_depth and orifice.can_birth,
    )


def calculate_pleasure(stretch: float, lubrication: float, sensitivity: float) -> float:
    """
    Calculate pleasure for the receiver.
    
    Some stretch is pleasurable, too much is painful.
    Good lubrication increases pleasure.
    """
    # Base pleasure from being filled
    fill_pleasure = min(stretch * 2, 0.5)  # Caps at 0.5
    
    # Lubrication smoothness bonus
    lube_pleasure = lubrication * 0.3
    
    # Sensitivity multiplier
    total = (fill_pleasure + lube_pleasure) * sensitivity
    
    # Reduce pleasure if stretch is painful
    if stretch > STRETCH_PAIN_THRESHOLD:
        pain_reduction = (stretch - STRETCH_PAIN_THRESHOLD) * 0.5
        total = max(0, total - pain_reduction)
    
    return min(1.0, total)


def calculate_pain(stretch: float, lubrication: float) -> float:
    """
    Calculate pain for the receiver.
    
    Pain starts when stretch exceeds threshold.
    Lubrication reduces pain.
    """
    if stretch <= STRETCH_PAIN_THRESHOLD:
        return 0.0
    
    excess_stretch = stretch - STRETCH_PAIN_THRESHOLD
    base_pain = excess_stretch * 0.5
    
    # Lubrication reduces pain
    lube_reduction = lubrication * 0.3
    
    return max(0, min(1.0, base_pain - lube_reduction))


def calculate_giver_pleasure(fit: FitResult, sensitivity: float) -> float:
    """Calculate pleasure for the one penetrating."""
    fit_pleasure = {
        FitResult.PERFECT: 0.5,
        FitResult.TIGHT: 0.8,
        FitResult.VERY_TIGHT: 0.9,
        FitResult.TOO_BIG: 0.3,      # Some pleasure from trying
        FitResult.TOO_LONG: 0.6,
        FitResult.IMPOSSIBLE: 0.0,
    }
    return fit_pleasure.get(fit, 0.5) * sensitivity


# =============================================================================
# KNOT MECHANICS
# =============================================================================

def calculate_knot_lock(
    orifice: OrificeMechanics,
    orifice_state: Union[OrificeState, "OrificeStateData"],
    knot_girth: float,
    lubrication: float,
) -> Tuple[bool, str]:
    """
    Calculate if a knot can lock inside an orifice.
    
    Args:
        orifice: Orifice mechanics
        orifice_state: Current state - either OrificeState enum or OrificeStateData object
        knot_girth: Size of the fully swollen knot
        lubrication: Current lubrication
    
    Returns:
        (can_lock, message)
    """
    if not orifice.accepts_knot:
        return False, "This orifice cannot accept a knot."
    
    # Handle both OrificeState enum and OrificeStateData object
    if isinstance(orifice_state, OrificeState):
        current_orifice_state = orifice_state
        current_stretch = 0.0
    else:
        current_orifice_state = orifice_state.orifice_state
        current_stretch = orifice_state.current_stretch
    
    # Effective capacity (same calc as fit check)
    effective_cap = orifice.base_girth_capacity
    if current_orifice_state == OrificeState.VIRGIN:
        effective_cap *= (1.0 - VIRGIN_TIGHTNESS_BONUS)
    elif current_orifice_state in (OrificeState.RELAXED, OrificeState.LOOSE):
        effective_cap *= (1.0 + RELAXATION_BONUS)
    effective_cap += lubrication * LUBRICATION_BONUS
    effective_cap += current_stretch
    
    # Knot needs to fit during inflation
    if knot_girth > orifice.max_girth_capacity:
        return False, "The knot is too large to fit safely."
    
    if knot_girth > effective_cap + STRETCH_DAMAGE_THRESHOLD:
        return False, "The knot would stretch too painfully."
    
    return True, "The knot swells, locking inside."


def calculate_knot_unlock_time(
    knot_girth: float,
    orifice_capacity: float,
) -> int:
    """
    Calculate how many ticks until the knot deflates enough to pull out.
    
    Returns:
        Number of game ticks
    """
    size_diff = knot_girth - orifice_capacity
    
    if size_diff <= 0:
        return 0  # Already can pull out
    
    # Base time: 50 ticks (5 minutes at 6 sec/tick)
    # Plus 20 ticks per inch of size difference
    base_time = 50
    size_time = int(size_diff * 20)
    
    return base_time + size_time


# TODO [KNOT_ADVANCED]: Implement advanced knot mechanics
# - Squeeze/clench affects deflation time (can speed up or slow down)
# - Forced pullout damage calculation
# - Cumming while locked extends lock time
# - Multiple loads while locked
# - Partner's arousal affects grip tightness
# - Knot "popping" sound/description when entering/exiting


# =============================================================================
# AROUSAL SYSTEM
# =============================================================================

def calculate_arousal_change(
    current_pleasure: float,
    current_arousal: ArousalState,
    stimulation: float,
    time_since_orgasm: int,
    is_refractory: bool,
) -> ArousalChange:
    """
    Calculate change in arousal from stimulation.
    
    Args:
        current_pleasure: Accumulated pleasure (0.0-1.0)
        current_arousal: Current arousal state
        stimulation: Pleasure gained this tick
        time_since_orgasm: Ticks since last orgasm
        is_refractory: Whether in refractory period
    
    Returns:
        ArousalChange with new state
    """
    if is_refractory:
        # In refractory period - arousal stays low
        return ArousalChange(
            old_state=current_arousal,
            new_state=ArousalState.SOFT,
            pleasure_gained=0,
            edging=False,
            orgasm=False,
        )
    
    new_pleasure = current_pleasure + stimulation
    
    # Determine new arousal state
    new_state = current_arousal
    for state, threshold in sorted(AROUSAL_THRESHOLDS.items(), key=lambda x: x[1], reverse=True):
        if new_pleasure >= threshold:
            new_state = state
            break
    
    # Check for orgasm
    orgasm = new_pleasure >= 1.0 and current_arousal == ArousalState.THROBBING
    edging = new_pleasure >= 0.95 and not orgasm
    
    return ArousalChange(
        old_state=current_arousal,
        new_state=new_state,
        pleasure_gained=stimulation,
        edging=edging,
        orgasm=orgasm,
    )


def calculate_arousal_decay(
    current_arousal: ArousalState,
    ticks_without_stimulation: int,
    base_decay_rate: float = 0.01,
) -> ArousalState:
    """
    Calculate arousal decay from lack of stimulation.
    
    Args:
        current_arousal: Current state
        ticks_without_stimulation: How long since last stimulation
        base_decay_rate: Decay per tick
    
    Returns:
        New arousal state
    """
    if current_arousal == ArousalState.SOFT:
        return ArousalState.SOFT
    
    decay = ticks_without_stimulation * base_decay_rate
    current_value = AROUSAL_THRESHOLDS[current_arousal]
    new_value = max(0, current_value - decay)
    
    # Find new state
    for state, threshold in sorted(AROUSAL_THRESHOLDS.items(), key=lambda x: x[1], reverse=True):
        if new_value >= threshold:
            return state
    
    return ArousalState.SOFT


# TODO [AROUSAL_ADVANCED]: Implement advanced arousal mechanics
# - Different body parts have different sensitivity
# - Arousal affects other stats (perception, concentration)
# - "Desperate" state from prolonged edging
# - Blue balls debuff from extended arousal without release
# - Multiple orgasms (rare ability, trainable)
# - Dry orgasms
# - Ruined orgasms
# - Forced orgasms (from over-stimulation)


# =============================================================================
# CUM/FLUIDS
# =============================================================================

def calculate_cum_production(
    ball_size: str,
    time_since_orgasm: int,
    base_rate: float = 0.01,
) -> float:
    """
    Calculate cum production rate.
    
    Args:
        ball_size: Size of balls (affects capacity and rate)
        time_since_orgasm: Ticks since last orgasm
        base_rate: Base production per tick
    
    Returns:
        Current fill level (0.0-1.0)
    """
    size_multipliers = {
        "tiny": 0.3,
        "small": 0.6,
        "average": 1.0,
        "large": 1.5,
        "huge": 2.5,
        "massive": 4.0,
    }
    
    multiplier = size_multipliers.get(ball_size, 1.0)
    production = time_since_orgasm * base_rate * multiplier
    
    return min(1.0, production)


def calculate_cum_volume(
    fill_level: float,
    ball_size: str,
    arousal_duration: int,
) -> float:
    """
    Calculate how much cum is released on orgasm.
    
    Args:
        fill_level: Current ball fill (0.0-1.0)
        ball_size: Size of balls
        arousal_duration: How long aroused before orgasm (edging bonus)
    
    Returns:
        Volume in arbitrary units (1.0 = average human load)
    """
    size_multipliers = {
        "tiny": 0.2,
        "small": 0.5,
        "average": 1.0,
        "large": 2.0,
        "huge": 4.0,
        "massive": 8.0,
    }
    
    base_volume = size_multipliers.get(ball_size, 1.0)
    fill_volume = base_volume * fill_level
    
    # Edging bonus (more cum from longer buildup)
    edging_bonus = min(arousal_duration * 0.01, 0.5)
    
    return fill_volume * (1.0 + edging_bonus)


def calculate_cum_capacity(orifice: OrificeMechanics) -> float:
    """
    Calculate how much cum an orifice can hold before overflow.
    
    Returns:
        Capacity in cum units
    """
    # Base capacity from depth
    base = orifice.base_depth * 0.5
    
    # Womb adds extra capacity
    if orifice.can_birth:
        base *= 2.0
    
    return base


# TODO [CUM_ADVANCED]: Implement advanced cum mechanics
# - Cum inflation visuals at high volumes
# - Cum leaking/dripping descriptions
# - Cum taste/smell by species
# - Cum inside tracking per-orifice
# - Cum cleanup requirements
# - Cum marking/scent (territory)
# - Cum addiction (kink system)
# - Creampie vs pullout distinction
# - Multiple loads stacking


# =============================================================================
# WETNESS/LUBRICATION
# =============================================================================

def calculate_natural_wetness(
    base_lubrication: float,
    arousal_state: ArousalState,
    has_wetness_from_arousal: bool,
) -> float:
    """
    Calculate natural wetness based on arousal.
    
    Args:
        base_lubrication: Orifice's natural lubrication
        arousal_state: Current arousal
        has_wetness_from_arousal: Whether arousal increases wetness
    
    Returns:
        Current wetness level (0.0-1.0)
    """
    wetness = base_lubrication
    
    if has_wetness_from_arousal:
        arousal_bonus = {
            ArousalState.DRY: 0.0,
            ArousalState.INTERESTED: 0.1,
            ArousalState.WET: 0.3,
            ArousalState.DRIPPING: 0.5,
            ArousalState.GUSHING: 0.8,
            ArousalState.SOFT: 0.0,
            ArousalState.CHUBBED: 0.05,
            ArousalState.HALF: 0.1,
            ArousalState.HARD: 0.15,
            ArousalState.THROBBING: 0.2,
        }
        wetness += arousal_bonus.get(arousal_state, 0.0)
    
    return min(1.0, wetness)


def calculate_lube_depletion(
    current_lube: float,
    activity_intensity: float,
    natural_replenish: float,
) -> float:
    """
    Calculate lube depletion from activity.
    
    Args:
        current_lube: Current lubrication level
        activity_intensity: How vigorous (0.0-1.0)
        natural_replenish: Natural lubrication rate
    
    Returns:
        New lubrication level
    """
    depletion = activity_intensity * 0.05
    replenish = natural_replenish * 0.02
    
    new_lube = current_lube - depletion + replenish
    return max(0.0, min(1.0, new_lube))


# TODO [LUBE_ADVANCED]: Implement advanced lubrication mechanics
# - Different lube types (saliva, slick, artificial)
# - Lube application action
# - Lube duration by type
# - Friction damage without lube (especially anal)
# - Squirting mechanic
# - Arousal fluid descriptions


# =============================================================================
# STRETCH AND RECOVERY
# =============================================================================

def calculate_stretch_recovery(
    current_stretch: float,
    recovery_rate: float,
    ticks: int,
) -> float:
    """
    Calculate how much an orifice recovers from stretching.
    
    Args:
        current_stretch: Current stretch amount
        recovery_rate: Recovery rate per tick
        ticks: Number of ticks elapsed
    
    Returns:
        New stretch amount
    """
    recovery = ticks * recovery_rate
    return max(0.0, current_stretch - recovery)


def calculate_permanent_stretch(
    current_permanent: float,
    stretch_amount: float,
    times_stretched: int,
) -> float:
    """
    Calculate if extreme stretching causes permanent changes.
    
    Only applies to EXTREME content (configurable).
    
    Args:
        current_permanent: Current permanent stretch modifier
        stretch_amount: How much stretched this time
        times_stretched: Total times stretched beyond threshold
    
    Returns:
        New permanent stretch modifier
    """
    # Only applies if stretch is significant
    if stretch_amount < STRETCH_DAMAGE_THRESHOLD:
        return current_permanent
    
    # Very gradual permanent change
    # 1000 extreme stretches = 1 inch permanent change
    increment = 0.001
    
    return current_permanent + increment


# TODO [STRETCH_ADVANCED]: Implement advanced stretch mechanics
# - Gaping duration based on stretch amount
# - Visual descriptions of gaping states
# - Plug training for capacity increase
# - Fisting milestones
# - "Broken in" state
# - Recovery items/magic


# =============================================================================
# VIRGINITY
# =============================================================================

def check_virginity_loss(
    orifice_state: Union[OrificeState, "OrificeStateData"],
    penetrator_girth: float,
) -> Tuple[bool, str]:
    """
    Check if this penetration would cause virginity loss.
    
    Args:
        orifice_state: Current orifice state - either OrificeState enum or OrificeStateData object
        penetrator_girth: Size of penetrator
    
    Returns:
        (lost_virginity, message)
    """
    # Handle both types
    if isinstance(orifice_state, OrificeState):
        current_state = orifice_state
    else:
        current_state = orifice_state.orifice_state
    
    if current_state != OrificeState.VIRGIN:
        return False, ""
    
    # Virginity lost on any penetration
    return True, "First time - the hymen stretches and gives way."


# TODO [VIRGINITY_ADVANCED]: Implement advanced virginity mechanics
# - Different hymens (some stretch, some tear)
# - Pain/bleeding from first time
# - Emotional/psychological effects
# - "Technical virgin" states
# - Virginity regeneration (magic/items)
# - Multiple virginities (oral, anal, vaginal tracked separately)


# =============================================================================
# SENSITIVITY ZONES
# =============================================================================

def calculate_zone_stimulation(
    penetration_depth: float,
    orifice: OrificeMechanics,
    thrust_angle: float = 0.0,
) -> Dict[str, float]:
    """
    Calculate which sensitivity zones are stimulated.
    
    Args:
        penetration_depth: Current depth
        orifice: Orifice being penetrated
        thrust_angle: Angle of thrust (for g-spot hitting)
    
    Returns:
        Dict of zone -> stimulation amount
    """
    zones = {}
    
    for zone in orifice.sensitivity_zones:
        if zone == "entrance":
            zones[zone] = 0.5  # Always stimulated
        elif zone == "g-spot":
            # G-spot at ~2-3 inches, needs right angle
            if 2.0 <= penetration_depth <= 4.0:
                zones[zone] = 0.3 + (thrust_angle * 0.3)
            else:
                zones[zone] = 0.1
        elif zone == "a-spot":
            # A-spot deeper, around 5-6 inches
            if penetration_depth >= 5.0:
                zones[zone] = 0.4
            else:
                zones[zone] = 0.0
        elif zone == "cervix":
            if penetration_depth >= orifice.base_depth:
                zones[zone] = 0.3  # Can be pleasure or pain
            else:
                zones[zone] = 0.0
        elif zone == "prostate":
            # Prostate at ~3-4 inches
            if 3.0 <= penetration_depth <= 5.0:
                zones[zone] = 0.5
            else:
                zones[zone] = 0.1
        elif zone == "deep":
            if penetration_depth >= orifice.base_depth * 0.8:
                zones[zone] = 0.4
            else:
                zones[zone] = penetration_depth / orifice.base_depth * 0.2
        else:
            zones[zone] = 0.2  # Default
    
    return zones


# TODO [SENSITIVITY_ADVANCED]: Implement advanced sensitivity mechanics
# - Individual zone sensitivity training
# - Desensitization from overuse
# - Hypersensitivity (from denial, edging)
# - Erogenous zone discovery (first time bonus)
# - Nipple/clit sensitivity scaling


# =============================================================================
# BREEDING/PREGNANCY (STUBS)
# =============================================================================

def calculate_conception_chance(
    womb_state: str,
    fertility: float,
    cum_volume: float,
    is_knotted: bool,
) -> float:
    """
    Calculate chance of conception.
    
    Args:
        womb_state: State of womb (heat, fertile, etc.)
        fertility: Base fertility (0.0-1.0)
        cum_volume: Amount of cum deposited
        is_knotted: Whether knotted during (bonus)
    
    Returns:
        Conception probability (0.0-1.0)
    """
    # TODO [PREGNANCY_FULL]: Implement full pregnancy system
    # - Heat cycles
    # - Fertility windows
    # - Sperm survival time
    # - Multiple partners mixing
    # - Birth control effects
    # - Species compatibility
    # - Hybrid offspring
    
    # Basic calculation for now
    base_chance = fertility * 0.1
    
    # More cum = higher chance
    cum_bonus = min(cum_volume * 0.05, 0.2)
    
    # Knotting keeps it inside
    knot_bonus = 0.1 if is_knotted else 0.0
    
    # Heat state bonus
    heat_bonuses = {
        "normal": 0.0,
        "fertile": 0.2,
        "heat": 0.4,
        "peak_heat": 0.6,
    }
    heat_bonus = heat_bonuses.get(womb_state, 0.0)
    
    total = base_chance + cum_bonus + knot_bonus + heat_bonus
    return min(0.9, total)  # Never 100%


# =============================================================================
# UTILITY FUNCTIONS
# =============================================================================

def get_size_description(girth: float) -> str:
    """Get a descriptive word for a girth measurement."""
    if girth < 1.0:
        return "tiny"
    elif girth < 1.3:
        return "small"
    elif girth < 1.6:
        return "average"
    elif girth < 2.0:
        return "large"
    elif girth < 3.0:
        return "huge"
    else:
        return "massive"


def get_depth_description(depth: float) -> str:
    """Get a descriptive word for depth."""
    if depth < 4.0:
        return "shallow"
    elif depth < 6.0:
        return "average"
    elif depth < 8.0:
        return "deep"
    elif depth < 12.0:
        return "very deep"
    else:
        return "impossibly deep"


def get_fit_description(result: PenetrationResult) -> str:
    """Get a descriptive message for a penetration fit."""
    fit_messages = {
        FitResult.PERFECT: "It slides in perfectly, filling without stretching.",
        FitResult.TIGHT: "A deliciously tight fit that grips and stretches.",
        FitResult.VERY_TIGHT: "An almost painfully tight squeeze that stretches to the limit.",
        FitResult.TOO_BIG: "It's simply too big to fit without causing harm.",
        FitResult.TOO_LONG: "It fits, but there's more length than there is depth.",
        FitResult.IMPOSSIBLE: "There's no way that's fitting in there.",
    }
    
    base = fit_messages.get(result.fit, "")
    
    if result.cervix_reached:
        base += " The deepest thrust bumps against the cervix."
    
    if result.womb_entered:
        base += " The tip breaches past the cervix into the womb itself."
    
    return base
