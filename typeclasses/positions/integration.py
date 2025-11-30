"""
Position-Body Integration
=========================

Connects the position system to the body system so that:
- Actions check position access before executing
- Part interactions respect position constraints
- Sexual mechanics flow through positions

This module provides:
- Access validation based on current position
- Action execution with position awareness
- Combined state queries (position + arousal + fit)
"""

from typing import TYPE_CHECKING, Optional, Set, Tuple, Any, Dict, List
from dataclasses import dataclass

# Import from submodules to avoid circular import
from .manager import PositionManager
from .active import ActivePosition
from .core import BodyZone, PART_TO_ZONE, parts_in_zone

# Define which parts are orifices and penetrators
ORIFICE_PARTS = {"mouth", "pussy", "ass", "anus", "cloaca", "tailhole"}
PENETRATOR_PARTS = {"cock", "penis", "hemipenes", "tentacle_cock"}

if TYPE_CHECKING:
    from evennia.objects.objects import DefaultObject

# Try to import body system components - they may not be fully set up
try:
    from typeclasses.body import Body
    from typeclasses.body.mechanics import calculate_fit, calculate_arousal_change
    from typeclasses.body.state import SexualStateManager
    BODY_SYSTEM_AVAILABLE = True
except ImportError:
    BODY_SYSTEM_AVAILABLE = False
    # Stub classes for when body isn't available
    class Body:
        pass
    def calculate_fit(*args, **kwargs):
        return None
    def calculate_arousal_change(*args, **kwargs):
        return 0.0


@dataclass
class AccessResult:
    """Result of checking if someone can access a body part."""
    allowed: bool
    reason: str = ""
    zone: Optional[BodyZone] = None
    requires_position: bool = False
    suggested_positions: List[str] = None
    
    def __post_init__(self):
        if self.suggested_positions is None:
            self.suggested_positions = []


@dataclass
class InteractionResult:
    """Result of a sexual interaction between parts."""
    success: bool
    message: str
    fit: Optional[Any] = None  # FitResult when body system available
    arousal_change_actor: float = 0.0
    arousal_change_target: float = 0.0
    penetration_occurred: bool = False
    virginity_lost: bool = False


def get_room_manager(location) -> PositionManager:
    """Get the position manager for a room."""
    manager = getattr(location, "_position_manager", None)
    if manager is None:
        manager = PositionManager()
        location._position_manager = manager
    return manager


def get_part_zone(part_key: str) -> Optional[BodyZone]:
    """Get the body zone a part belongs to."""
    return PART_TO_ZONE.get(part_key)


def check_part_access(
    actor: Any,
    target: Any,
    part_key: str,
    require_position: bool = False
) -> AccessResult:
    """
    Check if actor can access a specific part on target.
    
    Args:
        actor: The character trying to access
        target: The character being accessed
        part_key: The body part key (e.g., "pussy", "cock", "mouth")
        require_position: If True, must be in a position to access
        
    Returns:
        AccessResult with allowed status and reason
    """
    # Get the zone for this part
    zone = get_part_zone(part_key)
    if zone is None:
        # Unknown part - check if it's a variant
        for z, parts in PART_TO_ZONE.items():
            if part_key in parts:
                zone = z
                break
    
    if zone is None:
        return AccessResult(
            allowed=False,
            reason=f"Unknown body part: {part_key}"
        )
    
    # Check if in same location
    if getattr(actor, "location", None) != getattr(target, "location", None):
        return AccessResult(
            allowed=False,
            reason="Not in the same location",
            zone=zone
        )
    
    # Get position manager
    location = getattr(actor, "location", None)
    if not location:
        return AccessResult(
            allowed=False,
            reason="No valid location",
            zone=zone
        )
    
    manager = get_room_manager(location)
    
    # Check if in same position
    actor_pos = manager.get_position_for(actor)
    target_pos = manager.get_position_for(target)
    
    if actor_pos and target_pos and actor_pos is target_pos:
        # In same position - check position access
        actor_slot = actor_pos.get_slot_for_character(actor)
        target_slot = actor_pos.get_slot_for_character(target)
        
        if actor_slot and target_slot:
            accessible_zones = actor_pos.get_accessible_zones(actor_slot, target_slot)
            
            if zone in accessible_zones or BodyZone.WHOLE_BODY in accessible_zones:
                return AccessResult(
                    allowed=True,
                    zone=zone
                )
            else:
                return AccessResult(
                    allowed=False,
                    reason=f"Can't reach {part_key} from your position",
                    zone=zone,
                    requires_position=True
                )
    
    # Check if target has exposed zones (from their position)
    if target_pos:
        target_slot = target_pos.get_slot_for_character(target)
        if target_slot:
            exposed = target_pos.get_exposed_zones(target_slot)
            if zone in exposed:
                return AccessResult(
                    allowed=True,
                    zone=zone,
                    reason="Exposed from their position"
                )
    
    # Not in position together
    if require_position:
        # Suggest positions that would allow access
        from typeclasses.positions import POSITIONS
        
        suggestions = []
        for pos_key, pos_def in POSITIONS.items():
            # Check if this position grants access to the zone
            for slot in pos_def.slots.values():
                for target_slot_key, zones in slot.can_access.items():
                    if zone in zones:
                        suggestions.append(pos_key)
                        break
        
        return AccessResult(
            allowed=False,
            reason="Not in a position - intimate contact requires a position",
            zone=zone,
            requires_position=True,
            suggested_positions=suggestions[:5]
        )
    
    # No position required - allow access (for non-sexual touches)
    return AccessResult(
        allowed=True,
        zone=zone
    )


def check_penetration_access(
    actor: Any,
    target: Any,
    penetrator_key: str,
    orifice_key: str
) -> AccessResult:
    """
    Check if actor can penetrate target's orifice with their penetrator.
    
    This is stricter - always requires being in an appropriate position.
    """
    # Check penetrator access
    penetrator_check = check_part_access(actor, target, penetrator_key, require_position=False)
    if not penetrator_check.allowed:
        return penetrator_check
    
    # Check orifice access - this DOES require position
    orifice_check = check_part_access(actor, target, orifice_key, require_position=True)
    return orifice_check


def execute_penetration(
    actor: Any,
    target: Any,
    penetrator_key: str,
    orifice_key: str,
    force: float = 0.5
) -> InteractionResult:
    """
    Execute a penetration action between two characters.
    
    Args:
        actor: Character doing the penetrating
        target: Character being penetrated
        penetrator_key: Part key of the penetrator (e.g., "cock")
        orifice_key: Part key of the orifice (e.g., "pussy")
        force: How forcefully (0.0-1.0)
        
    Returns:
        InteractionResult with outcome details
    """
    # Check access
    access = check_penetration_access(actor, target, penetrator_key, orifice_key)
    if not access.allowed:
        return InteractionResult(
            success=False,
            message=access.reason
        )
    
    # Get bodies
    actor_body = getattr(actor, "body", None)
    target_body = getattr(target, "body", None)
    
    if not actor_body or not target_body:
        return InteractionResult(
            success=False,
            message="Missing body data"
        )
    
    # Get state managers
    actor_state = actor_body.get_sexual_state_manager()
    target_state = target_body.get_sexual_state_manager()
    
    if not actor_state or not target_state:
        return InteractionResult(
            success=False,
            message="Missing state data"
        )
    
    # Get penetrator state
    penetrator_state = actor_state.get_penetrator_state(penetrator_key)
    if not penetrator_state:
        return InteractionResult(
            success=False,
            message=f"No penetrator data for {penetrator_key}"
        )
    
    # Get orifice state
    orifice_state = target_state.get_orifice_state(orifice_key)
    if not orifice_state:
        return InteractionResult(
            success=False,
            message=f"No orifice data for {orifice_key}"
        )
    
    # Get penetrator definition for size/type
    penetrator_part = actor_body.get_part(penetrator_key)
    if not penetrator_part:
        return InteractionResult(
            success=False,
            message=f"No {penetrator_key} found"
        )
    
    # Calculate fit
    fit = calculate_fit(penetrator_part, orifice_state)
    
    # Check if penetration is possible
    if fit.category == "impossible":
        return InteractionResult(
            success=False,
            message=fit.description,
            fit=fit
        )
    
    # Check virginity
    virginity_lost = False
    if orifice_state.virgin:
        virginity_lost = True
        orifice_state.virgin = False
        target_state.set_orifice_state(orifice_key, orifice_state)
    
    # Calculate arousal changes
    actor_arousal = calculate_arousal_change(
        penetrator_state, 
        stimulus_intensity=0.5 + (fit.tightness_factor * 0.3),
        duration=1.0
    )
    
    target_arousal = calculate_arousal_change(
        orifice_state,
        stimulus_intensity=0.4 + (force * 0.4),
        duration=1.0
    )
    
    # Apply arousal changes
    actor_state.modify_arousal(penetrator_key, actor_arousal)
    target_state.modify_arousal(orifice_key, target_arousal)
    
    # Update stretch if applicable
    if fit.stretch_required > 0:
        new_stretch = min(1.0, orifice_state.current_stretch + (fit.stretch_required * force * 0.1))
        orifice_state.current_stretch = new_stretch
        target_state.set_orifice_state(orifice_key, orifice_state)
    
    # Build message
    actor_name = getattr(actor, "key", "Someone")
    target_name = getattr(target, "key", "someone")
    
    messages = []
    
    if virginity_lost:
        messages.append(f"{actor_name} takes {target_name}'s virginity!")
    
    messages.append(f"{actor_name} penetrates {target_name}. ({fit.description})")
    
    return InteractionResult(
        success=True,
        message=" ".join(messages),
        fit=fit,
        arousal_change_actor=actor_arousal,
        arousal_change_target=target_arousal,
        penetration_occurred=True,
        virginity_lost=virginity_lost
    )


def execute_thrust(
    actor: Any,
    target: Any,
    penetrator_key: str,
    orifice_key: str,
    intensity: float = 0.5,
    count: int = 1
) -> InteractionResult:
    """
    Execute thrusting while already penetrating.
    
    Requires actor to be able to thrust in their position.
    """
    # Check position allows thrusting
    location = getattr(actor, "location", None)
    if location:
        manager = get_room_manager(location)
        if not manager.can_char_thrust(actor):
            return InteractionResult(
                success=False,
                message="Can't thrust from your current position"
            )
    
    # Get state managers
    actor_body = getattr(actor, "body", None)
    target_body = getattr(target, "body", None)
    
    if not actor_body or not target_body:
        return InteractionResult(
            success=False,
            message="Missing body data"
        )
    
    actor_state = actor_body.get_sexual_state_manager()
    target_state = target_body.get_sexual_state_manager()
    
    if not actor_state or not target_state:
        return InteractionResult(
            success=False,
            message="Missing state data"
        )
    
    # Get states
    penetrator_state = actor_state.get_penetrator_state(penetrator_key)
    orifice_state = target_state.get_orifice_state(orifice_key)
    
    if not penetrator_state or not orifice_state:
        return InteractionResult(
            success=False,
            message="Not currently penetrating"
        )
    
    # Calculate arousal for each thrust
    total_actor_arousal = 0.0
    total_target_arousal = 0.0
    
    for _ in range(count):
        actor_change = calculate_arousal_change(
            penetrator_state,
            stimulus_intensity=intensity,
            duration=0.5
        )
        target_change = calculate_arousal_change(
            orifice_state,
            stimulus_intensity=intensity * 0.8,
            duration=0.5
        )
        
        total_actor_arousal += actor_change
        total_target_arousal += target_change
    
    # Apply arousal
    actor_state.modify_arousal(penetrator_key, total_actor_arousal)
    target_state.modify_arousal(orifice_key, total_target_arousal)
    
    # Check for orgasm
    actor_arousal = actor_state.get_arousal(penetrator_key)
    target_arousal = target_state.get_arousal(orifice_key)
    
    messages = []
    
    intensity_word = "gently" if intensity < 0.3 else "steadily" if intensity < 0.7 else "roughly"
    actor_name = getattr(actor, "key", "Someone")
    
    messages.append(f"{actor_name} thrusts {intensity_word}.")
    
    if actor_arousal >= 0.9:
        messages.append(f"{actor_name} is close to climax!")
    if target_arousal >= 0.9:
        target_name = getattr(target, "key", "They")
        messages.append(f"{target_name} is close to climax!")
    
    return InteractionResult(
        success=True,
        message=" ".join(messages),
        arousal_change_actor=total_actor_arousal,
        arousal_change_target=total_target_arousal
    )


def execute_oral(
    giver: Any,
    receiver: Any,
    giver_part: str = "mouth",
    receiver_part: str = "cock"
) -> InteractionResult:
    """
    Execute oral sex action.
    
    Requires giver's mouth to be free and have access to receiver's part.
    """
    # Check position allows mouth use
    location = getattr(giver, "location", None)
    if location:
        manager = get_room_manager(location)
        if not manager.can_char_speak(giver):
            # If can't speak, mouth is probably occupied
            return InteractionResult(
                success=False,
                message="Your mouth is occupied"
            )
    
    # Check access
    access = check_part_access(giver, receiver, receiver_part, require_position=True)
    if not access.allowed:
        return InteractionResult(
            success=False,
            message=access.reason
        )
    
    # Get bodies
    giver_body = getattr(giver, "body", None)
    receiver_body = getattr(receiver, "body", None)
    
    if not giver_body or not receiver_body:
        return InteractionResult(
            success=False,
            message="Missing body data"
        )
    
    receiver_state = receiver_body.get_sexual_state_manager()
    if not receiver_state:
        return InteractionResult(
            success=False,
            message="Missing state data"
        )
    
    # Calculate arousal
    if receiver_part in PENETRATOR_PARTS:
        state = receiver_state.get_penetrator_state(receiver_part)
    elif receiver_part in ORIFICE_PARTS:
        state = receiver_state.get_orifice_state(receiver_part)
    else:
        state = None
    
    if state:
        arousal_change = calculate_arousal_change(
            state,
            stimulus_intensity=0.6,
            duration=1.0
        )
        receiver_state.modify_arousal(receiver_part, arousal_change)
    else:
        arousal_change = 0.0
    
    giver_name = getattr(giver, "key", "Someone")
    receiver_name = getattr(receiver, "key", "someone")
    
    if receiver_part == "cock":
        verb = "takes"
        obj = f"{receiver_name}'s cock in their mouth"
    elif receiver_part == "pussy":
        verb = "licks"
        obj = f"{receiver_name}'s pussy"
    else:
        verb = "puts their mouth on"
        obj = f"{receiver_name}'s {receiver_part}"
    
    return InteractionResult(
        success=True,
        message=f"{giver_name} {verb} {obj}.",
        arousal_change_target=arousal_change
    )


def get_combined_state(
    character: Any,
) -> Dict[str, Any]:
    """
    Get combined position + body state for a character.
    
    Returns dict with:
    - position: Current position name or None
    - slot: Current slot in position
    - posture: Current posture
    - mobility: Current mobility level
    - can_thrust: Whether can actively thrust
    - can_speak: Whether can speak
    - hands_free: Whether hands are free
    - arousal: Dict of arousal by part
    - accessible_zones: Zones character can access on others
    """
    location = getattr(character, "location", None)
    if not location:
        return {"error": "No location"}
    
    manager = get_room_manager(location)
    active = manager.get_position_for(character)
    
    result = {
        "position": None,
        "slot": None,
        "posture": None,
        "mobility": None,
        "can_thrust": True,
        "can_speak": True,
        "hands_free": True,
        "arousal": {},
        "accessible_zones": {},
    }
    
    if active:
        result["position"] = active.definition.name
        result["slot"] = active.get_slot_for_character(character)
        
        posture = active.get_participant_posture(character)
        if posture:
            result["posture"] = posture.value
        
        mobility = active.get_participant_mobility(character)
        if mobility:
            result["mobility"] = mobility.value
        
        result["can_thrust"] = active.can_participant_thrust(character)
        result["can_speak"] = active.can_participant_speak(character)
        result["hands_free"] = active.can_participant_use_hands(character)
        
        # Get accessible zones for each other participant
        my_slot = active.get_slot_for_character(character)
        for slot_key, occupant in active.occupants.items():
            if occupant.character != character:
                zones = active.get_accessible_zones(my_slot, slot_key)
                result["accessible_zones"][occupant.character.key] = [z.value for z in zones]
    
    # Get arousal from body
    body = getattr(character, "body", None)
    if body:
        state_manager = body.get_sexual_state_manager()
        if state_manager:
            for part_key in PENETRATOR_PARTS:
                arousal = state_manager.get_arousal(part_key)
                if arousal > 0:
                    result["arousal"][part_key] = arousal
            
            for part_key in ORIFICE_PARTS:
                arousal = state_manager.get_arousal(part_key)
                if arousal > 0:
                    result["arousal"][part_key] = arousal
    
    return result


# ============================================================================
# Consent Integration Stub
# ============================================================================

def check_consent(
    actor: Any,
    target: Any,
    action: str
) -> Tuple[bool, str]:
    """
    Check if target consents to action from actor.
    
    TODO: Implement full consent system with:
    - Pre-established consent levels
    - Real-time consent requests
    - Safeword handling
    - Consent memory
    
    For now, returns True (assume consent for testing).
    """
    # Placeholder - always consent for now
    return True, ""


# ============================================================================
# Action Wrappers for Commands
# ============================================================================

def do_fuck(
    actor: Any,
    target: Any,
    penetrator_key: str = "cock",
    orifice_key: str = "pussy",
    intensity: float = 0.5
) -> str:
    """
    High-level fuck action - handles all the details.
    
    Returns message string.
    """
    # Check consent
    consented, reason = check_consent(actor, target, "penetration")
    if not consented:
        return f"No consent: {reason}"
    
    # Check position access
    access = check_penetration_access(actor, target, penetrator_key, orifice_key)
    if not access.allowed:
        if access.requires_position:
            suggestions = access.suggested_positions[:3]
            return f"{access.reason}. Try: {', '.join(suggestions)}"
        return access.reason
    
    # Execute penetration
    result = execute_penetration(actor, target, penetrator_key, orifice_key, intensity)
    
    return result.message


def do_thrust(
    actor: Any,
    target: Any,
    penetrator_key: str = "cock",
    orifice_key: str = "pussy",
    intensity: float = 0.5,
    count: int = 1
) -> str:
    """
    High-level thrust action.
    """
    result = execute_thrust(actor, target, penetrator_key, orifice_key, intensity, count)
    return result.message


def do_lick(
    giver: Any,
    receiver: Any,
    target_part: str = "pussy"
) -> str:
    """
    High-level lick/oral action.
    """
    consented, reason = check_consent(giver, receiver, "oral")
    if not consented:
        return f"No consent: {reason}"
    
    result = execute_oral(giver, receiver, "mouth", target_part)
    return result.message
