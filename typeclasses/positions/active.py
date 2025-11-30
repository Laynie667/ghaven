"""
Active position tracking.

Handles runtime state when characters are actually in positions.
"""

from dataclasses import dataclass, field
from typing import Dict, Set, Optional, Any, List, TYPE_CHECKING
from datetime import datetime

from .core import BodyZone, Posture, Mobility, parts_in_zone
from .definitions import PositionDefinition, SlotDefinition

if TYPE_CHECKING:
    from evennia.objects.objects import DefaultObject


@dataclass
class SlotOccupant:
    """
    Tracks who's occupying a slot and any modifications to their state.
    """
    character: Any                         # The character in this slot
    slot_key: str                          # Which slot they're in
    joined_at: datetime = field(default_factory=datetime.now)
    
    # Custom modifications
    custom_access_granted: Set[BodyZone] = field(default_factory=set)  # Extra zones
    custom_access_revoked: Set[BodyZone] = field(default_factory=set)  # Blocked zones
    
    # State overrides
    is_restrained: bool = False            # Overrides mobility
    is_gagged: bool = False                # Blocks mouth
    is_blindfolded: bool = False           # Cosmetic/RP
    
    # Custom flavor
    flavor_text: str = ""                  # Player's custom description
    
    def get_effective_mobility(self, slot_def: SlotDefinition) -> Mobility:
        """Get mobility considering restraints."""
        if self.is_restrained:
            return Mobility.RESTRAINED
        return slot_def.mobility
    
    def can_speak(self, slot_def: SlotDefinition) -> bool:
        """Check if this occupant can speak."""
        if self.is_gagged:
            return False
        return slot_def.mouth_free
    
    def can_use_hands(self, slot_def: SlotDefinition) -> bool:
        """Check if this occupant can use their hands."""
        if self.is_restrained:
            return False
        return slot_def.hands_free


@dataclass
class ActivePosition:
    """
    Represents a position currently in use.
    
    Created when characters enter a position, destroyed when they leave.
    Tracks participants, custom modifications, and provides access queries.
    
    Example:
        active = ActivePosition(
            definition=MISSIONARY,
            occupants={
                "top": SlotOccupant(character=dom_char, slot_key="top"),
                "bottom": SlotOccupant(character=sub_char, slot_key="bottom")
            },
            anchor=bed_object,
            custom_flavor="with passionate intensity"
        )
        
        # What can top access on bottom?
        zones = active.get_accessible_zones("top", "bottom")
        
        # What parts specifically?
        parts = active.get_accessible_parts("top", "bottom")
    """
    definition: PositionDefinition
    occupants: Dict[str, SlotOccupant] = field(default_factory=dict)
    anchor: Optional[Any] = None           # Furniture/object being used
    
    # Custom description added by initiating player
    custom_flavor: str = ""
    
    # Timing
    started_at: datetime = field(default_factory=datetime.now)
    last_action_at: datetime = field(default_factory=datetime.now)
    
    # State
    is_active: bool = True
    intensity: str = "normal"              # Can be modified during position
    
    # For multi-occupant expandable slots
    # Format: {slot_key: [additional occupants beyond first]}
    additional_occupants: Dict[str, List[SlotOccupant]] = field(default_factory=dict)
    
    # ========================================================================
    # Participant Management
    # ========================================================================
    
    def add_participant(
        self,
        character: Any,
        slot_key: str,
        flavor_text: str = ""
    ) -> tuple:
        """
        Add a participant to a slot.
        
        Returns:
            (success: bool, reason: str)
        """
        slot_def = self.definition.get_slot(slot_key)
        if not slot_def:
            return False, f"Unknown slot: {slot_key}"
        
        # Check if slot is occupied
        if slot_key in self.occupants:
            if not slot_def.expandable:
                return False, f"Slot '{slot_key}' is already occupied"
            
            # Check max occupants for expandable slot
            current_count = 1 + len(self.additional_occupants.get(slot_key, []))
            if current_count >= slot_def.max_occupants:
                return False, f"Slot '{slot_key}' is at capacity"
            
            # Add to additional occupants
            if slot_key not in self.additional_occupants:
                self.additional_occupants[slot_key] = []
            
            self.additional_occupants[slot_key].append(
                SlotOccupant(
                    character=character,
                    slot_key=slot_key,
                    flavor_text=flavor_text
                )
            )
        else:
            # First occupant of slot
            self.occupants[slot_key] = SlotOccupant(
                character=character,
                slot_key=slot_key,
                flavor_text=flavor_text
            )
        
        return True, ""
    
    def remove_participant(self, character: Any) -> tuple:
        """
        Remove a participant from the position.
        
        Returns:
            (success: bool, slot_key: str)
        """
        # Check main occupants
        for slot_key, occupant in list(self.occupants.items()):
            if occupant.character == character:
                del self.occupants[slot_key]
                return True, slot_key
        
        # Check additional occupants
        for slot_key, extras in list(self.additional_occupants.items()):
            for i, occupant in enumerate(extras):
                if occupant.character == character:
                    extras.pop(i)
                    return True, slot_key
        
        return False, ""
    
    def get_participant(self, slot_key: str) -> Optional[Any]:
        """Get the character in a slot (first occupant if expandable)."""
        occupant = self.occupants.get(slot_key)
        return occupant.character if occupant else None
    
    def get_all_participants(self, slot_key: str) -> List[Any]:
        """Get all characters in a slot (for expandable slots)."""
        result = []
        
        if slot_key in self.occupants:
            result.append(self.occupants[slot_key].character)
        
        if slot_key in self.additional_occupants:
            result.extend([o.character for o in self.additional_occupants[slot_key]])
        
        return result
    
    def get_occupant(self, character: Any) -> Optional[SlotOccupant]:
        """Get the SlotOccupant for a character."""
        for occupant in self.occupants.values():
            if occupant.character == character:
                return occupant
        
        for extras in self.additional_occupants.values():
            for occupant in extras:
                if occupant.character == character:
                    return occupant
        
        return None
    
    def get_slot_for_character(self, character: Any) -> Optional[str]:
        """Get which slot a character is in."""
        for slot_key, occupant in self.occupants.items():
            if occupant.character == character:
                return slot_key
        
        for slot_key, extras in self.additional_occupants.items():
            for occupant in extras:
                if occupant.character == character:
                    return slot_key
        
        return None
    
    def get_all_characters(self) -> List[Any]:
        """Get all characters in this position."""
        chars = [o.character for o in self.occupants.values()]
        for extras in self.additional_occupants.values():
            chars.extend([o.character for o in extras])
        return chars
    
    # ========================================================================
    # Access Queries
    # ========================================================================
    
    def get_accessible_zones(
        self,
        from_slot: str,
        to_slot: str
    ) -> Set[BodyZone]:
        """
        Get zones that from_slot can access on to_slot.
        
        Considers:
        - Base slot access from definition
        - Custom granted access
        - Custom revoked access
        - Restraint status
        """
        # Get base access from definition
        slot_def = self.definition.get_slot(from_slot)
        if not slot_def:
            return set()
        
        base_access = slot_def.get_access_to(to_slot)
        
        # Get occupant modifications
        from_occupant = self.occupants.get(from_slot)
        to_occupant = self.occupants.get(to_slot)
        
        if not to_occupant:
            return set()
        
        # Start with base access
        accessible = base_access.copy()
        
        # Apply from_occupant's granted access
        if from_occupant:
            accessible |= from_occupant.custom_access_granted
        
        # Apply to_occupant's revoked access
        accessible -= to_occupant.custom_access_revoked
        
        # If to_occupant has blocked zones in their slot, remove those
        to_slot_def = self.definition.get_slot(to_slot)
        if to_slot_def:
            accessible -= to_slot_def.blocked
        
        return accessible
    
    def get_accessible_parts(
        self,
        from_slot: str,
        to_slot: str
    ) -> Set[str]:
        """
        Get specific part keys that from_slot can access on to_slot.
        
        Resolves zones to actual parts.
        """
        zones = self.get_accessible_zones(from_slot, to_slot)
        
        parts = set()
        for zone in zones:
            parts |= parts_in_zone(zone)
        
        return parts
    
    def can_reach_part(
        self,
        from_slot: str,
        to_slot: str,
        part_key: str
    ) -> bool:
        """Check if from_slot can reach a specific part on to_slot."""
        accessible_parts = self.get_accessible_parts(from_slot, to_slot)
        return part_key in accessible_parts
    
    def get_exposed_zones(self, slot_key: str) -> Set[BodyZone]:
        """
        Get zones exposed to non-participants (the room).
        
        Used for open positions where outsiders can join in.
        """
        slot_def = self.definition.get_slot(slot_key)
        if not slot_def:
            return set()
        
        exposed = slot_def.exposed_to_room.copy()
        
        # Check occupant modifications
        occupant = self.occupants.get(slot_key)
        if occupant:
            exposed -= occupant.custom_access_revoked
        
        return exposed
    
    def get_exposed_parts(self, slot_key: str) -> Set[str]:
        """Get specific parts exposed to the room."""
        zones = self.get_exposed_zones(slot_key)
        
        parts = set()
        for zone in zones:
            parts |= parts_in_zone(zone)
        
        return parts
    
    def is_zone_accessible_from_room(
        self,
        slot_key: str,
        zone: BodyZone
    ) -> bool:
        """Check if a zone is accessible to non-participants."""
        return zone in self.get_exposed_zones(slot_key)
    
    # ========================================================================
    # State Modifications
    # ========================================================================
    
    def grant_access(
        self,
        from_character: Any,
        to_slot: str,
        zones: Set[BodyZone]
    ) -> bool:
        """Grant extra access to a participant."""
        occupant = self.get_occupant(from_character)
        if not occupant:
            return False
        
        occupant.custom_access_granted |= zones
        return True
    
    def revoke_access(
        self,
        character: Any,
        zones: Set[BodyZone]
    ) -> bool:
        """Block access to zones on a character."""
        occupant = self.get_occupant(character)
        if not occupant:
            return False
        
        occupant.custom_access_revoked |= zones
        return True
    
    def set_restrained(self, character: Any, restrained: bool = True) -> bool:
        """Set a participant as restrained."""
        occupant = self.get_occupant(character)
        if not occupant:
            return False
        
        occupant.is_restrained = restrained
        return True
    
    def set_gagged(self, character: Any, gagged: bool = True) -> bool:
        """Set a participant as gagged."""
        occupant = self.get_occupant(character)
        if not occupant:
            return False
        
        occupant.is_gagged = gagged
        return True
    
    def set_flavor(self, character: Any, flavor: str) -> bool:
        """Set custom flavor text for a participant."""
        occupant = self.get_occupant(character)
        if not occupant:
            return False
        
        occupant.flavor_text = flavor
        return True
    
    # ========================================================================
    # Status Queries
    # ========================================================================
    
    def can_participant_thrust(self, character: Any) -> bool:
        """Check if a participant can actively thrust/move."""
        slot_key = self.get_slot_for_character(character)
        if not slot_key:
            return False
        
        slot_def = self.definition.get_slot(slot_key)
        if not slot_def:
            return False
        
        occupant = self.get_occupant(character)
        if occupant and occupant.is_restrained:
            return False
        
        return slot_def.can_thrust
    
    def can_participant_speak(self, character: Any) -> bool:
        """Check if a participant can speak."""
        slot_key = self.get_slot_for_character(character)
        if not slot_key:
            return False
        
        slot_def = self.definition.get_slot(slot_key)
        if not slot_def:
            return False
        
        occupant = self.get_occupant(character)
        if not occupant:
            return False
        
        return occupant.can_speak(slot_def)
    
    def can_participant_use_hands(self, character: Any) -> bool:
        """Check if a participant can use their hands."""
        slot_key = self.get_slot_for_character(character)
        if not slot_key:
            return False
        
        slot_def = self.definition.get_slot(slot_key)
        if not slot_def:
            return False
        
        occupant = self.get_occupant(character)
        if not occupant:
            return False
        
        return occupant.can_use_hands(slot_def)
    
    def get_participant_posture(self, character: Any) -> Optional[Posture]:
        """Get the posture of a participant."""
        slot_key = self.get_slot_for_character(character)
        if not slot_key:
            return None
        
        slot_def = self.definition.get_slot(slot_key)
        if not slot_def:
            return None
        
        return slot_def.posture
    
    def get_participant_mobility(self, character: Any) -> Optional[Mobility]:
        """Get the effective mobility of a participant."""
        slot_key = self.get_slot_for_character(character)
        if not slot_key:
            return None
        
        slot_def = self.definition.get_slot(slot_key)
        if not slot_def:
            return None
        
        occupant = self.get_occupant(character)
        if not occupant:
            return slot_def.mobility
        
        return occupant.get_effective_mobility(slot_def)
    
    # ========================================================================
    # Descriptions
    # ========================================================================
    
    def describe(self) -> str:
        """Generate a description of the current position."""
        parts = [self.definition.name]
        
        if self.custom_flavor:
            parts.append(f"({self.custom_flavor})")
        
        # Describe participants
        participant_descs = []
        for slot_key, occupant in self.occupants.items():
            char_name = getattr(occupant.character, "key", "Someone")
            slot_def = self.definition.get_slot(slot_key)
            
            if slot_def and slot_def.description:
                # Format description with participant names
                desc = slot_def.description
                for other_key, other_occ in self.occupants.items():
                    other_name = getattr(other_occ.character, "key", "someone")
                    desc = desc.replace(f"{{{other_key}}}", other_name)
                participant_descs.append(f"{char_name} {desc}")
            else:
                participant_descs.append(f"{char_name} as {slot_key}")
            
            # Add flavor if present
            if occupant.flavor_text:
                participant_descs[-1] += f" ({occupant.flavor_text})"
        
        if participant_descs:
            parts.append(" - ")
            parts.append(", ".join(participant_descs))
        
        return "".join(parts)
    
    def get_entry_message(self, character: Any) -> str:
        """Get the message for a character entering the position."""
        slot_key = self.get_slot_for_character(character)
        if not slot_key:
            return ""
        
        slot_def = self.definition.get_slot(slot_key)
        if not slot_def or not slot_def.entry_msg:
            return ""
        
        msg = slot_def.entry_msg
        
        # Replace placeholders
        for other_key, occupant in self.occupants.items():
            other_name = getattr(occupant.character, "key", "someone")
            msg = msg.replace(f"{{{other_key}}}", other_name)
        
        return msg
    
    # ========================================================================
    # Serialization
    # ========================================================================
    
    def to_dict(self) -> dict:
        """Serialize for storage."""
        return {
            "definition_key": self.definition.key,
            "occupants": {
                slot: {
                    "character_id": getattr(occ.character, "id", None),
                    "joined_at": occ.joined_at.isoformat(),
                    "custom_access_granted": [z.value for z in occ.custom_access_granted],
                    "custom_access_revoked": [z.value for z in occ.custom_access_revoked],
                    "is_restrained": occ.is_restrained,
                    "is_gagged": occ.is_gagged,
                    "is_blindfolded": occ.is_blindfolded,
                    "flavor_text": occ.flavor_text,
                }
                for slot, occ in self.occupants.items()
            },
            "anchor_id": getattr(self.anchor, "id", None) if self.anchor else None,
            "custom_flavor": self.custom_flavor,
            "started_at": self.started_at.isoformat(),
            "intensity": self.intensity,
        }
