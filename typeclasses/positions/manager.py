"""
Position Manager
================

Handles tracking active positions and provides the API for commands.
"""

from typing import Dict, Set, Optional, Any, List, Tuple, TYPE_CHECKING
from datetime import datetime
from dataclasses import dataclass, field

from .core import BodyZone, Posture, Mobility, parts_in_zone
from .definitions import PositionDefinition, PositionRequirement
from .active import ActivePosition, SlotOccupant
from .library import POSITIONS, get_position

if TYPE_CHECKING:
    from evennia.objects.objects import DefaultObject


@dataclass
class PositionInvite:
    """Tracks a pending position invitation."""
    position_key: str
    inviter: Any
    slot_for_inviter: str
    invitee: Any
    slot_for_invitee: str
    anchor: Optional[Any] = None
    custom_flavor: str = ""
    created_at: datetime = field(default_factory=datetime.now)
    expires_seconds: int = 60  # Invitation timeout
    
    @property
    def is_expired(self) -> bool:
        elapsed = (datetime.now() - self.created_at).total_seconds()
        return elapsed > self.expires_seconds


class PositionManager:
    """
    Manages position state for a room or globally.
    
    Tracks:
    - Active positions in progress
    - Pending invitations
    - Who can access whom
    
    Usage:
        manager = PositionManager()
        
        # Start a position
        active, msg = manager.start_position(
            position_key="missionary",
            participants={"top": char_a, "bottom": char_b},
            anchor=bed,
            custom_flavor="passionately"
        )
        
        # Check what someone can access
        zones = manager.get_accessible_zones(char_a, char_b)
        parts = manager.get_accessible_parts(char_a, char_b)
        
        # Add someone to an open slot
        success, msg = manager.add_to_position(active, char_c, "front")
        
        # End position
        manager.end_position(active)
    """
    
    def __init__(self):
        # Active positions by a unique ID
        self._active_positions: Dict[int, ActivePosition] = {}
        self._next_id: int = 1
        
        # Quick lookups
        self._char_to_position: Dict[Any, int] = {}  # char -> position_id
        self._pending_invites: Dict[Any, PositionInvite] = {}  # invitee -> invite
    
    # ========================================================================
    # Position Lifecycle
    # ========================================================================
    
    def start_position(
        self,
        position_key: str,
        participants: Dict[str, Any],
        anchor: Optional[Any] = None,
        custom_flavor: str = "",
        initiator: Optional[Any] = None,
    ) -> Tuple[Optional[ActivePosition], str]:
        """
        Start a new position with the given participants.
        
        Args:
            position_key: The position to use
            participants: Dict of {slot_key: character}
            anchor: Optional furniture/object
            custom_flavor: Player's custom description
            initiator: Who started this (for messages)
            
        Returns:
            (ActivePosition or None, message)
        """
        # Get position definition
        position_def = get_position(position_key)
        if not position_def:
            return None, f"Unknown position: {position_key}"
        
        # Check requirements
        can_use, reason = position_def.can_use(
            list(participants.values()),
            anchor
        )
        if not can_use:
            return None, reason
        
        # Check all participants are free
        for slot_key, char in participants.items():
            if char in self._char_to_position:
                char_name = getattr(char, "key", "Someone")
                return None, f"{char_name} is already in a position"
        
        # Validate slot assignments
        for slot_key in participants.keys():
            if slot_key not in position_def.slots:
                return None, f"Unknown slot: {slot_key}"
        
        # Check minimum participants
        if len(participants) < position_def.requirements.min_participants:
            return None, f"Need at least {position_def.requirements.min_participants} participants"
        
        # Create active position
        active = ActivePosition(
            definition=position_def,
            anchor=anchor,
            custom_flavor=custom_flavor,
        )
        
        # Add participants
        for slot_key, char in participants.items():
            active.add_participant(char, slot_key)
        
        # Register
        pos_id = self._next_id
        self._next_id += 1
        self._active_positions[pos_id] = active
        
        # Track character positions
        for char in participants.values():
            self._char_to_position[char] = pos_id
        
        # Build message
        names = [getattr(c, "key", "Someone") for c in participants.values()]
        if len(names) == 2:
            name_str = f"{names[0]} and {names[1]}"
        else:
            name_str = ", ".join(names[:-1]) + f", and {names[-1]}"
        
        msg = f"{name_str} get into {position_def.name}"
        if custom_flavor:
            msg += f" ({custom_flavor})"
        msg += "."
        
        return active, msg
    
    def end_position(
        self,
        active: ActivePosition,
        reason: str = ""
    ) -> str:
        """
        End a position and free all participants.
        
        Returns:
            Message describing the end
        """
        # Find and remove from registry
        pos_id = None
        for pid, pos in self._active_positions.items():
            if pos is active:
                pos_id = pid
                break
        
        if pos_id is None:
            return "Position not found."
        
        # Free participants
        for char in active.get_all_characters():
            if char in self._char_to_position:
                del self._char_to_position[char]
        
        # Remove position
        del self._active_positions[pos_id]
        active.is_active = False
        
        # Build message
        names = [getattr(c, "key", "Someone") for c in active.get_all_characters()]
        if len(names) == 1:
            name_str = names[0]
        elif len(names) == 2:
            name_str = f"{names[0]} and {names[1]}"
        else:
            name_str = ", ".join(names[:-1]) + f", and {names[-1]}"
        
        msg = f"{name_str} disengage from {active.definition.name}"
        if reason:
            msg += f" ({reason})"
        msg += "."
        
        return msg
    
    def add_to_position(
        self,
        active: ActivePosition,
        character: Any,
        slot_key: str,
        flavor_text: str = ""
    ) -> Tuple[bool, str]:
        """
        Add a character to an existing position.
        
        Args:
            active: The active position
            character: Character to add
            slot_key: Which slot to join
            flavor_text: Custom description
            
        Returns:
            (success, message)
        """
        if character in self._char_to_position:
            return False, "Already in a position"
        
        success, reason = active.add_participant(character, slot_key, flavor_text)
        if not success:
            return False, reason
        
        # Track
        pos_id = None
        for pid, pos in self._active_positions.items():
            if pos is active:
                pos_id = pid
                break
        
        if pos_id:
            self._char_to_position[character] = pos_id
        
        char_name = getattr(character, "key", "Someone")
        slot_def = active.definition.get_slot(slot_key)
        slot_name = slot_def.name if slot_def else slot_key
        
        return True, f"{char_name} joins as {slot_name}"
    
    def remove_from_position(
        self,
        character: Any,
        reason: str = ""
    ) -> Tuple[bool, str]:
        """
        Remove a character from their current position.
        
        Returns:
            (success, message)
        """
        pos_id = self._char_to_position.get(character)
        if not pos_id:
            return False, "Not in a position"
        
        active = self._active_positions.get(pos_id)
        if not active:
            del self._char_to_position[character]
            return False, "Position not found"
        
        success, slot_key = active.remove_participant(character)
        if not success:
            return False, "Failed to remove from position"
        
        del self._char_to_position[character]
        
        char_name = getattr(character, "key", "Someone")
        msg = f"{char_name} withdraws from the position"
        if reason:
            msg += f" ({reason})"
        
        # Check if position should end
        remaining = len(active.get_all_characters())
        if remaining < active.definition.requirements.min_participants:
            end_msg = self.end_position(active, "not enough participants")
            msg += f". {end_msg}"
        
        return True, msg
    
    # ========================================================================
    # Invitations
    # ========================================================================
    
    def create_invite(
        self,
        position_key: str,
        inviter: Any,
        slot_for_inviter: str,
        invitee: Any,
        slot_for_invitee: str,
        anchor: Optional[Any] = None,
        custom_flavor: str = ""
    ) -> Tuple[bool, str]:
        """
        Create an invitation for a position.
        
        Returns:
            (success, message)
        """
        # Validate position
        position_def = get_position(position_key)
        if not position_def:
            return False, f"Unknown position: {position_key}"
        
        # Validate slots
        if slot_for_inviter not in position_def.slots:
            return False, f"Unknown slot: {slot_for_inviter}"
        if slot_for_invitee not in position_def.slots:
            return False, f"Unknown slot: {slot_for_invitee}"
        
        # Check neither is busy
        if inviter in self._char_to_position:
            return False, "You're already in a position"
        if invitee in self._char_to_position:
            invitee_name = getattr(invitee, "key", "They")
            return False, f"{invitee_name} is already in a position"
        
        # Check furniture
        can_use, reason = position_def.requirements.check_furniture(anchor)
        if not can_use:
            return False, reason
        
        # Cancel any existing invite to this person
        if invitee in self._pending_invites:
            del self._pending_invites[invitee]
        
        # Create invite
        invite = PositionInvite(
            position_key=position_key,
            inviter=inviter,
            slot_for_inviter=slot_for_inviter,
            invitee=invitee,
            slot_for_invitee=slot_for_invitee,
            anchor=anchor,
            custom_flavor=custom_flavor,
        )
        
        self._pending_invites[invitee] = invite
        
        inviter_name = getattr(inviter, "key", "Someone")
        invitee_name = getattr(invitee, "key", "someone")
        
        return True, f"{inviter_name} invites {invitee_name} to {position_def.name} ({slot_for_invitee})"
    
    def accept_invite(self, invitee: Any) -> Tuple[Optional[ActivePosition], str]:
        """
        Accept a pending invitation.
        
        Returns:
            (ActivePosition or None, message)
        """
        invite = self._pending_invites.get(invitee)
        if not invite:
            return None, "No pending invitation"
        
        if invite.is_expired:
            del self._pending_invites[invitee]
            return None, "Invitation has expired"
        
        # Start the position
        active, msg = self.start_position(
            position_key=invite.position_key,
            participants={
                invite.slot_for_inviter: invite.inviter,
                invite.slot_for_invitee: invite.invitee,
            },
            anchor=invite.anchor,
            custom_flavor=invite.custom_flavor,
        )
        
        # Clear invite
        del self._pending_invites[invitee]
        
        return active, msg
    
    def decline_invite(self, invitee: Any) -> str:
        """Decline a pending invitation."""
        invite = self._pending_invites.get(invitee)
        if not invite:
            return "No pending invitation"
        
        inviter_name = getattr(invite.inviter, "key", "Someone")
        invitee_name = getattr(invitee, "key", "someone")
        
        del self._pending_invites[invitee]
        
        return f"{invitee_name} declines {inviter_name}'s invitation"
    
    def get_pending_invite(self, character: Any) -> Optional[PositionInvite]:
        """Get pending invite for a character."""
        invite = self._pending_invites.get(character)
        if invite and invite.is_expired:
            del self._pending_invites[character]
            return None
        return invite
    
    # ========================================================================
    # Access Queries
    # ========================================================================
    
    def get_position_for(self, character: Any) -> Optional[ActivePosition]:
        """Get the active position a character is in."""
        pos_id = self._char_to_position.get(character)
        if not pos_id:
            return None
        return self._active_positions.get(pos_id)
    
    def is_in_position(self, character: Any) -> bool:
        """Check if a character is in any position."""
        return character in self._char_to_position
    
    def get_accessible_zones(
        self,
        from_char: Any,
        to_char: Any
    ) -> Set[BodyZone]:
        """
        Get zones that from_char can access on to_char.
        
        Considers:
        - Position access if both in same position
        - Room exposure if different positions or no position
        """
        # Check if in same position
        from_pos = self.get_position_for(from_char)
        to_pos = self.get_position_for(to_char)
        
        if from_pos and to_pos and from_pos is to_pos:
            # Same position - use position access
            from_slot = from_pos.get_slot_for_character(from_char)
            to_slot = from_pos.get_slot_for_character(to_char)
            
            if from_slot and to_slot:
                return from_pos.get_accessible_zones(from_slot, to_slot)
        
        # Different positions or no position
        # Check if to_char has exposed zones from their position
        if to_pos:
            to_slot = to_pos.get_slot_for_character(to_char)
            if to_slot:
                return to_pos.get_exposed_zones(to_slot)
        
        # Not in position - default to everything accessible
        # (This would be modified by room rules, consent, etc.)
        return set()  # Or ALL_ZONES depending on game rules
    
    def get_accessible_parts(
        self,
        from_char: Any,
        to_char: Any
    ) -> Set[str]:
        """Get specific parts from_char can access on to_char."""
        zones = self.get_accessible_zones(from_char, to_char)
        
        parts = set()
        for zone in zones:
            parts |= parts_in_zone(zone)
        
        return parts
    
    def can_reach_part(
        self,
        from_char: Any,
        to_char: Any,
        part_key: str
    ) -> bool:
        """Check if from_char can reach a specific part on to_char."""
        return part_key in self.get_accessible_parts(from_char, to_char)
    
    def can_char_thrust(self, character: Any) -> bool:
        """Check if a character can actively thrust in their position."""
        active = self.get_position_for(character)
        if not active:
            return True  # Not in position, can move freely
        return active.can_participant_thrust(character)
    
    def can_char_speak(self, character: Any) -> bool:
        """Check if a character can speak in their position."""
        active = self.get_position_for(character)
        if not active:
            return True
        return active.can_participant_speak(character)
    
    def can_char_use_hands(self, character: Any) -> bool:
        """Check if a character can use their hands."""
        active = self.get_position_for(character)
        if not active:
            return True
        return active.can_participant_use_hands(character)
    
    # ========================================================================
    # Position Queries
    # ========================================================================
    
    def get_positions_in_room(self, room: Any) -> List[ActivePosition]:
        """Get all active positions in a room."""
        positions = []
        for active in self._active_positions.values():
            # Check if any participant is in the room
            for char in active.get_all_characters():
                if getattr(char, "location", None) == room:
                    positions.append(active)
                    break
        return positions
    
    def get_open_slots(self, active: ActivePosition) -> List[str]:
        """Get slots that can accept more participants."""
        open_slots = []
        
        for slot_key, slot_def in active.definition.slots.items():
            current_count = len(active.get_all_participants(slot_key))
            
            if current_count == 0:
                # Empty slot
                open_slots.append(slot_key)
            elif slot_def.expandable and current_count < slot_def.max_occupants:
                # Expandable with room
                open_slots.append(slot_key)
        
        return open_slots
    
    def describe_room_positions(self, room: Any) -> List[str]:
        """Get descriptions of all positions in a room."""
        descriptions = []
        for active in self.get_positions_in_room(room):
            descriptions.append(active.describe())
        return descriptions
    
    # ========================================================================
    # Transitions
    # ========================================================================
    
    def can_transition(
        self,
        active: ActivePosition,
        to_position_key: str
    ) -> Tuple[bool, str]:
        """Check if a position can transition to another."""
        if to_position_key not in active.definition.transitions_to:
            return False, "Can't transition directly to that position"
        
        to_def = get_position(to_position_key)
        if not to_def:
            return False, f"Unknown position: {to_position_key}"
        
        # Check furniture compatibility
        can_use, reason = to_def.requirements.check_furniture(active.anchor)
        if not can_use:
            return False, reason
        
        # Check participant count
        current_count = len(active.get_all_characters())
        can_use, reason = to_def.requirements.check_participants(current_count)
        if not can_use:
            return False, reason
        
        return True, ""
    
    def transition_position(
        self,
        active: ActivePosition,
        to_position_key: str,
        slot_mapping: Optional[Dict[str, str]] = None
    ) -> Tuple[Optional[ActivePosition], str]:
        """
        Transition from one position to another without fully disengaging.
        
        Args:
            active: Current position
            to_position_key: Position to transition to
            slot_mapping: Optional {old_slot: new_slot} mapping
            
        Returns:
            (new ActivePosition or None, message)
        """
        can, reason = self.can_transition(active, to_position_key)
        if not can:
            return None, reason
        
        to_def = get_position(to_position_key)
        
        # Build participant mapping
        participants = {}
        
        if slot_mapping:
            # Use provided mapping
            for old_slot, new_slot in slot_mapping.items():
                chars = active.get_all_participants(old_slot)
                for char in chars:
                    participants[new_slot] = char
        else:
            # Try to auto-map by slot key
            for slot_key in active.definition.slots:
                if slot_key in to_def.slots:
                    chars = active.get_all_participants(slot_key)
                    if chars:
                        participants[slot_key] = chars[0]
        
        if not participants:
            return None, "Could not map participants to new slots"
        
        # End old position quietly
        for char in active.get_all_characters():
            if char in self._char_to_position:
                del self._char_to_position[char]
        
        pos_id = None
        for pid, pos in list(self._active_positions.items()):
            if pos is active:
                pos_id = pid
                del self._active_positions[pid]
                break
        
        # Start new position
        new_active, msg = self.start_position(
            position_key=to_position_key,
            participants=participants,
            anchor=active.anchor,
            custom_flavor=active.custom_flavor,
        )
        
        if new_active:
            msg = f"They shift into {to_def.name}"
        
        return new_active, msg
    
    # ========================================================================
    # Serialization
    # ========================================================================
    
    def to_dict(self) -> dict:
        """Serialize manager state."""
        return {
            "active_positions": {
                str(pid): pos.to_dict()
                for pid, pos in self._active_positions.items()
            },
            "next_id": self._next_id,
        }
    
    def clear(self):
        """Clear all position state."""
        self._active_positions.clear()
        self._char_to_position.clear()
        self._pending_invites.clear()
        self._next_id = 1


# ============================================================================
# Global Manager Instance (optional singleton)
# ============================================================================

_global_manager: Optional[PositionManager] = None


def get_global_manager() -> PositionManager:
    """Get or create the global position manager."""
    global _global_manager
    if _global_manager is None:
        _global_manager = PositionManager()
    return _global_manager


def get_room_manager(room: Any) -> PositionManager:
    """
    Get the position manager for a room.
    
    Rooms can have their own manager stored as an attribute,
    or use the global manager.
    """
    # Check for room-specific manager
    manager = getattr(room, "_position_manager", None)
    if manager is None:
        manager = PositionManager()
        room._position_manager = manager
    return manager
