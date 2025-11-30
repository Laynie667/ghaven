"""
Body Action Framework

Defines possible actions that can be performed with/on bodies.
This is the skeleton for the interaction system.

Actions are divided into categories:
- Penetration actions (fucking, inserting)
- Oral actions (licking, sucking, kissing)
- Manual actions (touching, groping, fingering)
- Stimulation actions (stroking, rubbing)
- Breeding actions (impregnating, knotting)
- Fluid actions (cumming, milking)
- Meta actions (examining, posing)

Each action has:
- Requirements (what parts are needed)
- Effects (what happens to states)
- Results (pleasure, pain, arousal changes)
"""

from dataclasses import dataclass, field
from typing import List, Dict, Optional, Tuple, Callable, TYPE_CHECKING
from enum import Enum

from ..templates.parts_sexual import ArousalState, OrificeState, KnotState
from ..mechanics import (
    calculate_fit,
    calculate_knot_lock,
    calculate_arousal_change,
    PenetrationResult,
    FitResult,
)

if TYPE_CHECKING:
    from ..core.body import Body
    from ..state.sexual import SexualStateManager


# =============================================================================
# ACTION ENUMS
# =============================================================================

class ActionCategory(Enum):
    """Categories of body actions."""
    PENETRATION = "penetration"
    ORAL = "oral"
    MANUAL = "manual"
    STIMULATION = "stimulation"
    BREEDING = "breeding"
    FLUID = "fluid"
    META = "meta"


class ActionResult(Enum):
    """Result of attempting an action."""
    SUCCESS = "success"
    PARTIAL = "partial"           # Worked but with issues
    FAILED_CANT_REACH = "cant_reach"
    FAILED_TOO_BIG = "too_big"
    FAILED_WRONG_PARTS = "wrong_parts"
    FAILED_NOT_READY = "not_ready"
    FAILED_BLOCKED = "blocked"
    FAILED_REFUSED = "refused"


# =============================================================================
# ACTION DEFINITIONS
# =============================================================================

@dataclass
class ActionRequirement:
    """Requirements for an action to be possible."""
    
    # Actor requirements
    actor_needs_part: Optional[str] = None      # Part key actor needs
    actor_part_must_be: Optional[List[str]] = None  # Allowed states
    actor_min_arousal: Optional[ArousalState] = None
    
    # Target requirements
    target_needs_part: Optional[str] = None
    target_part_must_be: Optional[List[str]] = None
    target_min_arousal: Optional[ArousalState] = None
    
    # Both
    must_be_same_location: bool = True
    requires_consent: bool = True


@dataclass
class ActionEffect:
    """Effects of performing an action."""
    
    # Arousal changes
    actor_arousal_change: float = 0.0
    target_arousal_change: float = 0.0
    
    # Pleasure/pain
    actor_pleasure: float = 0.0
    target_pleasure: float = 0.0
    target_pain: float = 0.0
    
    # State changes
    creates_penetration: bool = False
    ends_penetration: bool = False
    causes_orgasm_chance: float = 0.0
    
    # Fluid effects
    transfers_fluid: bool = False
    fluid_type: str = ""
    fluid_amount: float = 0.0


@dataclass
class ActionDefinition:
    """Definition of a body action."""
    
    key: str
    name: str
    category: ActionCategory
    description: str = ""
    
    # Requirements
    requirements: ActionRequirement = field(default_factory=ActionRequirement)
    
    # What parts are involved
    actor_part: str = ""          # Part actor uses (cock, tongue, hand)
    target_part: str = ""         # Part being acted on (pussy, mouth, ass)
    
    # Base effects (modified by mechanics)
    base_effects: ActionEffect = field(default_factory=ActionEffect)
    
    # Intensity levels
    min_intensity: int = 1
    max_intensity: int = 5
    
    # Variations
    variations: List[str] = field(default_factory=list)
    
    # Emote templates
    actor_emote: str = ""         # "{actor} does something to {target}"
    target_emote: str = ""        # "Something is done to you by {actor}"
    room_emote: str = ""          # "{actor} does something to {target}"


# =============================================================================
# ACTION REGISTRY
# =============================================================================

ACTIONS: Dict[str, ActionDefinition] = {}


def register_action(action: ActionDefinition):
    """Register an action definition."""
    ACTIONS[action.key] = action


def get_action(key: str) -> Optional[ActionDefinition]:
    """Get an action by key."""
    return ACTIONS.get(key)


def get_actions_by_category(category: ActionCategory) -> List[ActionDefinition]:
    """Get all actions in a category."""
    return [a for a in ACTIONS.values() if a.category == category]


# =============================================================================
# PENETRATION ACTIONS
# =============================================================================

register_action(ActionDefinition(
    key="penetrate",
    name="Penetrate",
    category=ActionCategory.PENETRATION,
    description="Insert a penetrator into an orifice.",
    requirements=ActionRequirement(
        actor_needs_part="penetrator",  # Any penetrator
        actor_min_arousal=ArousalState.HALF,
        target_needs_part="orifice",    # Any orifice
    ),
    actor_part="penetrator",
    target_part="orifice",
    base_effects=ActionEffect(
        actor_arousal_change=0.1,
        target_arousal_change=0.1,
        actor_pleasure=0.3,
        target_pleasure=0.3,
        creates_penetration=True,
    ),
    variations=["gentle", "rough", "deep", "shallow", "fast", "slow"],
    actor_emote="{actor} pushes into {target}'s {part}",
    target_emote="{actor} enters you",
    room_emote="{actor} penetrates {target}",
))

register_action(ActionDefinition(
    key="thrust",
    name="Thrust",
    category=ActionCategory.PENETRATION,
    description="Thrust while penetrating.",
    requirements=ActionRequirement(
        # Requires ongoing penetration
    ),
    actor_part="penetrator",
    target_part="orifice",
    base_effects=ActionEffect(
        actor_arousal_change=0.15,
        target_arousal_change=0.15,
        actor_pleasure=0.4,
        target_pleasure=0.4,
        causes_orgasm_chance=0.1,
    ),
    min_intensity=1,
    max_intensity=10,
    variations=["deep", "shallow", "grinding", "pounding", "slow", "frantic"],
))

register_action(ActionDefinition(
    key="withdraw",
    name="Pull Out",
    category=ActionCategory.PENETRATION,
    description="Remove penetrator from orifice.",
    base_effects=ActionEffect(
        ends_penetration=True,
    ),
    actor_emote="{actor} pulls out of {target}",
))

register_action(ActionDefinition(
    key="knot",
    name="Knot",
    category=ActionCategory.PENETRATION,
    description="Push knot inside and lock.",
    requirements=ActionRequirement(
        actor_needs_part="cock_canine",
        actor_min_arousal=ArousalState.HARD,
        target_needs_part="orifice",
    ),
    base_effects=ActionEffect(
        actor_arousal_change=0.3,
        target_arousal_change=0.2,
        actor_pleasure=0.6,
        target_pleasure=0.5,
        target_pain=0.2,
    ),
    actor_emote="{actor} pushes their knot inside {target}, locking them together",
))

# =============================================================================
# ORAL ACTIONS
# =============================================================================

register_action(ActionDefinition(
    key="lick",
    name="Lick",
    category=ActionCategory.ORAL,
    description="Lick a body part.",
    actor_part="tongue",
    base_effects=ActionEffect(
        actor_arousal_change=0.05,
        target_arousal_change=0.1,
        target_pleasure=0.2,
    ),
    variations=["gentle", "teasing", "long", "quick", "slobbery"],
))

register_action(ActionDefinition(
    key="suck",
    name="Suck",
    category=ActionCategory.ORAL,
    description="Suck on a body part.",
    actor_part="mouth",
    base_effects=ActionEffect(
        actor_arousal_change=0.1,
        target_arousal_change=0.15,
        target_pleasure=0.3,
    ),
))

register_action(ActionDefinition(
    key="blowjob",
    name="Give Head",
    category=ActionCategory.ORAL,
    description="Perform oral on a cock.",
    requirements=ActionRequirement(
        target_needs_part="penetrator",
    ),
    actor_part="mouth",
    target_part="penetrator",
    base_effects=ActionEffect(
        actor_arousal_change=0.1,
        target_arousal_change=0.2,
        actor_pleasure=0.2,
        target_pleasure=0.5,
        causes_orgasm_chance=0.15,
    ),
    variations=["deepthroat", "teasing", "sloppy", "skilled"],
))

register_action(ActionDefinition(
    key="cunnilingus",
    name="Eat Out",
    category=ActionCategory.ORAL,
    description="Perform oral on a pussy.",
    requirements=ActionRequirement(
        target_needs_part="pussy",
    ),
    actor_part="tongue",
    target_part="pussy",
    base_effects=ActionEffect(
        actor_arousal_change=0.1,
        target_arousal_change=0.25,
        target_pleasure=0.5,
        causes_orgasm_chance=0.2,
    ),
    variations=["teasing", "focused", "deep", "clit-focused"],
))

register_action(ActionDefinition(
    key="rimjob",
    name="Rim",
    category=ActionCategory.ORAL,
    description="Lick the asshole.",
    requirements=ActionRequirement(
        target_needs_part="asshole",
    ),
    actor_part="tongue",
    target_part="asshole",
    base_effects=ActionEffect(
        actor_arousal_change=0.1,
        target_arousal_change=0.15,
        target_pleasure=0.3,
    ),
))

register_action(ActionDefinition(
    key="kiss",
    name="Kiss",
    category=ActionCategory.ORAL,
    description="Kiss lips or body.",
    actor_part="mouth",
    base_effects=ActionEffect(
        actor_arousal_change=0.05,
        target_arousal_change=0.05,
    ),
    variations=["gentle", "passionate", "deep", "quick"],
))

# =============================================================================
# MANUAL ACTIONS
# =============================================================================

register_action(ActionDefinition(
    key="touch",
    name="Touch",
    category=ActionCategory.MANUAL,
    description="Touch a body part.",
    actor_part="hand",
    base_effects=ActionEffect(
        target_arousal_change=0.05,
    ),
    variations=["gentle", "firm", "teasing", "exploring"],
))

register_action(ActionDefinition(
    key="grope",
    name="Grope",
    category=ActionCategory.MANUAL,
    description="Grope/squeeze a body part.",
    actor_part="hand",
    base_effects=ActionEffect(
        actor_arousal_change=0.05,
        target_arousal_change=0.1,
        target_pleasure=0.15,
    ),
))

register_action(ActionDefinition(
    key="finger",
    name="Finger",
    category=ActionCategory.MANUAL,
    description="Insert fingers into an orifice.",
    requirements=ActionRequirement(
        target_needs_part="orifice",
    ),
    actor_part="fingers",
    target_part="orifice",
    base_effects=ActionEffect(
        actor_arousal_change=0.05,
        target_arousal_change=0.2,
        target_pleasure=0.3,
        creates_penetration=True,
    ),
    variations=["one finger", "two fingers", "three fingers", "curled", "thrusting"],
))

register_action(ActionDefinition(
    key="handjob",
    name="Stroke",
    category=ActionCategory.MANUAL,
    description="Stroke a cock with hand.",
    requirements=ActionRequirement(
        target_needs_part="penetrator",
    ),
    actor_part="hand",
    target_part="penetrator",
    base_effects=ActionEffect(
        actor_arousal_change=0.05,
        target_arousal_change=0.2,
        target_pleasure=0.4,
        causes_orgasm_chance=0.15,
    ),
))

register_action(ActionDefinition(
    key="fist",
    name="Fist",
    category=ActionCategory.MANUAL,
    description="Insert entire fist into orifice.",
    requirements=ActionRequirement(
        target_needs_part="orifice",
    ),
    actor_part="fist",
    target_part="orifice",
    base_effects=ActionEffect(
        actor_arousal_change=0.1,
        target_arousal_change=0.2,
        target_pleasure=0.4,
        target_pain=0.3,
        creates_penetration=True,
    ),
))

# =============================================================================
# STIMULATION ACTIONS
# =============================================================================

register_action(ActionDefinition(
    key="rub",
    name="Rub",
    category=ActionCategory.STIMULATION,
    description="Rub a body part.",
    base_effects=ActionEffect(
        target_arousal_change=0.1,
        target_pleasure=0.2,
    ),
))

register_action(ActionDefinition(
    key="rub_clit",
    name="Rub Clit",
    category=ActionCategory.STIMULATION,
    description="Stimulate the clitoris.",
    requirements=ActionRequirement(
        target_needs_part="clit",
    ),
    target_part="clit",
    base_effects=ActionEffect(
        target_arousal_change=0.25,
        target_pleasure=0.5,
        causes_orgasm_chance=0.2,
    ),
))

register_action(ActionDefinition(
    key="nipple_play",
    name="Play with Nipples",
    category=ActionCategory.STIMULATION,
    description="Stimulate nipples.",
    requirements=ActionRequirement(
        target_needs_part="nipple_left",
    ),
    target_part="nipple",
    base_effects=ActionEffect(
        target_arousal_change=0.15,
        target_pleasure=0.25,
    ),
    variations=["pinch", "twist", "lick", "suck", "bite"],
))

register_action(ActionDefinition(
    key="edge",
    name="Edge",
    category=ActionCategory.STIMULATION,
    description="Bring close to orgasm then stop.",
    base_effects=ActionEffect(
        target_arousal_change=0.3,
        target_pleasure=0.6,
        causes_orgasm_chance=0.0,  # Intentionally avoiding orgasm
    ),
))

# =============================================================================
# BREEDING ACTIONS
# =============================================================================

register_action(ActionDefinition(
    key="breed",
    name="Breed",
    category=ActionCategory.BREEDING,
    description="Attempt to impregnate.",
    requirements=ActionRequirement(
        actor_needs_part="penetrator",
        target_needs_part="womb",
    ),
    base_effects=ActionEffect(
        actor_arousal_change=0.3,
        target_arousal_change=0.2,
        causes_orgasm_chance=0.5,
        transfers_fluid=True,
        fluid_type="cum",
    ),
))

register_action(ActionDefinition(
    key="creampie",
    name="Creampie",
    category=ActionCategory.BREEDING,
    description="Cum inside.",
    requirements=ActionRequirement(
        actor_needs_part="penetrator",
        target_needs_part="orifice",
    ),
    base_effects=ActionEffect(
        causes_orgasm_chance=1.0,  # This IS the orgasm
        transfers_fluid=True,
        fluid_type="cum",
    ),
))

# =============================================================================
# FLUID ACTIONS
# =============================================================================

register_action(ActionDefinition(
    key="cum",
    name="Cum",
    category=ActionCategory.FLUID,
    description="Orgasm and release cum.",
    base_effects=ActionEffect(
        causes_orgasm_chance=1.0,
        transfers_fluid=True,
        fluid_type="cum",
    ),
))

register_action(ActionDefinition(
    key="cum_on",
    name="Cum On",
    category=ActionCategory.FLUID,
    description="Cum on a body part.",
    base_effects=ActionEffect(
        causes_orgasm_chance=1.0,
        transfers_fluid=True,
        fluid_type="cum",
    ),
))

register_action(ActionDefinition(
    key="milk",
    name="Milk",
    category=ActionCategory.FLUID,
    description="Express milk from breasts.",
    requirements=ActionRequirement(
        target_needs_part="breast_left",
        # Target must be lactating (checked in executor)
    ),
    target_part="breast",
    base_effects=ActionEffect(
        target_pleasure=0.2,
        transfers_fluid=True,
        fluid_type="milk",
    ),
))

register_action(ActionDefinition(
    key="squirt",
    name="Squirt",
    category=ActionCategory.FLUID,
    description="Female ejaculation.",
    requirements=ActionRequirement(
        actor_needs_part="pussy",
    ),
    base_effects=ActionEffect(
        causes_orgasm_chance=1.0,
        transfers_fluid=True,
        fluid_type="femcum",
    ),
))

# =============================================================================
# META ACTIONS
# =============================================================================

register_action(ActionDefinition(
    key="examine",
    name="Examine",
    category=ActionCategory.META,
    description="Look closely at a body part.",
    requirements=ActionRequirement(
        requires_consent=False,  # Can look without consent (in public)
    ),
))

register_action(ActionDefinition(
    key="expose",
    name="Expose",
    category=ActionCategory.META,
    description="Reveal a body part.",
))

register_action(ActionDefinition(
    key="cover",
    name="Cover",
    category=ActionCategory.META,
    description="Hide a body part.",
))

register_action(ActionDefinition(
    key="pose",
    name="Pose",
    category=ActionCategory.META,
    description="Take a pose/position.",
    variations=["bend over", "spread legs", "on knees", "on back", "on all fours"],
))


# =============================================================================
# ACTION EXECUTOR
# =============================================================================

@dataclass
class ActionAttempt:
    """An attempt to perform an action."""
    
    action_key: str
    actor_body: "Body"
    actor_states: "SexualStateManager"
    target_body: Optional["Body"] = None
    target_states: Optional["SexualStateManager"] = None
    
    # Specifics
    actor_part_key: str = ""      # Specific part to use
    target_part_key: str = ""     # Specific part to target
    intensity: int = 5            # 1-10 scale
    variation: str = ""           # e.g., "rough", "gentle"


@dataclass
class ActionOutcome:
    """Result of executing an action."""
    
    result: ActionResult
    message: str
    
    # Effects applied
    actor_arousal_change: float = 0.0
    target_arousal_change: float = 0.0
    actor_pleasure: float = 0.0
    target_pleasure: float = 0.0
    target_pain: float = 0.0
    
    # State changes
    penetration_started: bool = False
    penetration_ended: bool = False
    knot_locked: bool = False
    orgasm_triggered: bool = False
    fluid_transferred: str = ""
    fluid_amount: float = 0.0
    
    # For display
    actor_emote: str = ""
    target_emote: str = ""
    room_emote: str = ""


def check_action_requirements(
    action: ActionDefinition,
    attempt: ActionAttempt,
) -> Tuple[bool, str]:
    """
    Check if action requirements are met.
    
    Returns:
        (success, error_message)
    """
    req = action.requirements
    
    # Check actor has needed part
    if req.actor_needs_part:
        if req.actor_needs_part == "penetrator":
            # Any penetrator
            has_pen = any(k.startswith("cock_") or k == "hemipenes" 
                        for k in attempt.actor_body.parts)
            if not has_pen:
                return False, "You don't have the right equipment."
        elif req.actor_needs_part not in attempt.actor_body.parts:
            return False, f"You need a {req.actor_needs_part}."
    
    # Check actor arousal
    if req.actor_min_arousal:
        current = attempt.actor_states.arousal_state
        # Compare arousal levels
        levels = [ArousalState.SOFT, ArousalState.CHUBBED, ArousalState.HALF, 
                 ArousalState.HARD, ArousalState.THROBBING]
        if levels.index(current) < levels.index(req.actor_min_arousal):
            return False, "You're not aroused enough for that."
    
    # Check target has needed part
    if req.target_needs_part and attempt.target_body:
        if req.target_needs_part == "orifice":
            # Any orifice
            has_orif = any(k in ["mouth", "pussy", "asshole", "cloaca"]
                         for k in attempt.target_body.parts)
            if not has_orif:
                return False, "They don't have the right... opening."
        elif req.target_needs_part == "penetrator":
            has_pen = any(k.startswith("cock_") or k == "hemipenes"
                        for k in attempt.target_body.parts)
            if not has_pen:
                return False, "They don't have the right equipment."
        elif req.target_needs_part not in attempt.target_body.parts:
            return False, f"They need a {req.target_needs_part}."
    
    return True, ""


def execute_action(attempt: ActionAttempt) -> ActionOutcome:
    """
    Execute a body action and return the outcome.
    
    This is the main entry point for the action system.
    """
    action = get_action(attempt.action_key)
    if not action:
        return ActionOutcome(
            result=ActionResult.FAILED_WRONG_PARTS,
            message=f"Unknown action: {attempt.action_key}",
        )
    
    # Check requirements
    can_do, error = check_action_requirements(action, attempt)
    if not can_do:
        return ActionOutcome(
            result=ActionResult.FAILED_WRONG_PARTS,
            message=error,
        )
    
    # Get base effects
    effects = action.base_effects
    
    # Modify by intensity
    intensity_mult = attempt.intensity / 5.0  # 5 is "normal"
    
    arousal_actor = effects.actor_arousal_change * intensity_mult
    arousal_target = effects.target_arousal_change * intensity_mult
    pleasure_actor = effects.actor_pleasure * intensity_mult
    pleasure_target = effects.target_pleasure * intensity_mult
    pain_target = effects.target_pain * intensity_mult
    
    # Apply effects to states
    attempt.actor_states.add_arousal(arousal_actor)
    if attempt.target_states:
        attempt.target_states.add_arousal(arousal_target)
    
    # Check for orgasm
    orgasm = False
    fluid_transferred = ""
    fluid_amount = 0.0
    
    import random
    if effects.causes_orgasm_chance > 0:
        # Higher arousal = higher orgasm chance
        arousal_bonus = attempt.actor_states.overall_arousal * 0.3
        total_chance = effects.causes_orgasm_chance + arousal_bonus
        
        if random.random() < total_chance:
            orgasm = True
            # Trigger orgasm
            released = attempt.actor_states.trigger_orgasm()
            if released:
                fluid_transferred = "cum"
                fluid_amount = sum(released.values())
    
    # Penetration state
    pen_started = effects.creates_penetration
    pen_ended = effects.ends_penetration
    
    # Build emotes
    actor_emote = action.actor_emote
    # TODO: Fill in template variables
    
    return ActionOutcome(
        result=ActionResult.SUCCESS,
        message=f"You {action.name.lower()}.",
        actor_arousal_change=arousal_actor,
        target_arousal_change=arousal_target,
        actor_pleasure=pleasure_actor,
        target_pleasure=pleasure_target,
        target_pain=pain_target,
        penetration_started=pen_started,
        penetration_ended=pen_ended,
        orgasm_triggered=orgasm,
        fluid_transferred=fluid_transferred,
        fluid_amount=fluid_amount,
        actor_emote=actor_emote,
    )


# =============================================================================
# ACTION HELPERS
# =============================================================================

def get_available_actions(
    actor_body: "Body",
    actor_states: "SexualStateManager",
    target_body: Optional["Body"] = None,
) -> List[ActionDefinition]:
    """
    Get list of actions the actor can currently perform.
    
    Filters based on:
    - Parts available
    - Current arousal
    - Target's parts (if any)
    """
    available = []
    
    for action in ACTIONS.values():
        # Create mock attempt to check requirements
        attempt = ActionAttempt(
            action_key=action.key,
            actor_body=actor_body,
            actor_states=actor_states,
            target_body=target_body,
            target_states=None,
        )
        
        can_do, _ = check_action_requirements(action, attempt)
        if can_do:
            available.append(action)
    
    return available


def get_actions_for_part(part_key: str) -> List[ActionDefinition]:
    """Get actions that can be performed on/with a specific part."""
    actions = []
    
    for action in ACTIONS.values():
        if action.actor_part == part_key or action.target_part == part_key:
            actions.append(action)
        # Also check generic matches
        if part_key.startswith("cock_") and action.target_part == "penetrator":
            actions.append(action)
        if part_key in ["pussy", "asshole", "mouth"] and action.target_part == "orifice":
            actions.append(action)
    
    return actions
