"""
Position definition classes.

These are the templates that define what positions exist and how they work.
"""

from dataclasses import dataclass, field
from typing import Dict, Set, Optional, List, Any, TYPE_CHECKING

from .core import BodyZone, Posture, Mobility, FurnitureType

if TYPE_CHECKING:
    from evennia.objects.objects import DefaultObject


@dataclass
class SlotDefinition:
    """
    Defines a role/slot within a position.
    
    Each position has one or more slots that participants occupy.
    Slots define what that participant can access and what's exposed.
    
    Example:
        # The "bottom" slot in missionary position
        SlotDefinition(
            key="bottom",
            name="bottom",
            posture=Posture.LYING_BACK,
            mobility=Mobility.PASSIVE,
            can_access={"top": {BodyZone.CHEST, BodyZone.FACE, BodyZone.BACK_UPPER}},
            exposed_to_room={BodyZone.FACE, BodyZone.MOUTH},
            description="lying on their back beneath {top}"
        )
    """
    key: str                           # Internal identifier
    name: str                          # Display name
    posture: Posture                   # Physical posture
    mobility: Mobility = Mobility.FREE
    
    # What zones this slot can access on OTHER slots
    # Format: {other_slot_key: {zones...}}
    can_access: Dict[str, Set[BodyZone]] = field(default_factory=dict)
    
    # What zones are exposed to NON-participants in the room
    # This enables "open" positions where outsiders can interact
    exposed_to_room: Set[BodyZone] = field(default_factory=set)
    
    # What zones are completely blocked (can't be accessed by anyone)
    blocked: Set[BodyZone] = field(default_factory=set)
    
    # Can this participant use their hands freely?
    hands_free: bool = True
    
    # Can this participant speak freely?
    mouth_free: bool = True
    
    # Movement/thrust capability
    can_thrust: bool = False  # Can actively thrust/move
    controls_pace: bool = False  # Sets the rhythm
    
    # Description templates
    # {other_slot} placeholders get replaced with participant names
    description: str = ""  # "is lying beneath {top}"
    entry_msg: str = ""    # "lies down beneath {top}"
    exit_msg: str = ""     # "slides out from under {top}"
    
    # For expandable slots (multiple people in same role)
    expandable: bool = False
    max_occupants: int = 1
    
    def get_access_to(self, other_slot: str) -> Set[BodyZone]:
        """Get zones this slot can access on another slot."""
        return self.can_access.get(other_slot, set())
    
    def can_reach_zone(self, other_slot: str, zone: BodyZone) -> bool:
        """Check if this slot can reach a specific zone on another slot."""
        accessible = self.can_access.get(other_slot, set())
        return zone in accessible or BodyZone.WHOLE_BODY in accessible


@dataclass
class PositionRequirement:
    """
    Requirements for using a position.
    """
    # Participant count
    min_participants: int = 2
    max_participants: int = 2
    
    # Furniture/anchor requirements
    # Empty set = no furniture needed (floor/standing)
    furniture_types: Set[FurnitureType] = field(default_factory=set)
    furniture_required: bool = False  # Must have matching furniture?
    
    # Object requirements (restraints, toys, etc.)
    required_object_tags: Set[str] = field(default_factory=set)
    
    # Physical requirements (checked against character's body structure)
    required_mobility: Set[str] = field(default_factory=set)  # e.g., {"bipedal", "quadruped"}
    requires_flexibility: bool = False
    requires_strength: bool = False
    
    # Size compatibility
    size_compatible: bool = True  # Whether size differences matter
    max_size_difference: int = 3  # Max size category difference
    
    # Special flags
    requires_consent: bool = True  # Always true for most positions
    allows_restraints: bool = True  # Can participants be restrained?
    
    def check_furniture(self, furniture: Optional[Any]) -> tuple:
        """
        Check if furniture meets requirements.
        
        Returns:
            (success: bool, reason: str)
        """
        if not self.furniture_required and not self.furniture_types:
            return True, ""
        
        if self.furniture_required and furniture is None:
            return False, f"Requires furniture: {', '.join(f.value for f in self.furniture_types)}"
        
        if furniture is None:
            return True, ""  # Not required, not provided = ok
        
        # Check furniture tags
        furniture_tags = getattr(furniture, "position_tags", set())
        if isinstance(furniture_tags, list):
            furniture_tags = set(furniture_tags)
        
        # Convert to FurnitureType values for comparison
        tag_values = {f.value for f in self.furniture_types}
        
        if not tag_values.intersection(furniture_tags):
            return False, f"Furniture doesn't support this position"
        
        return True, ""
    
    def check_participants(self, count: int) -> tuple:
        """
        Check if participant count is valid.
        
        Returns:
            (success: bool, reason: str)
        """
        if count < self.min_participants:
            return False, f"Requires at least {self.min_participants} participants"
        if count > self.max_participants:
            return False, f"Maximum {self.max_participants} participants"
        return True, ""


@dataclass
class PositionDefinition:
    """
    Template definition for a position.
    
    Positions are templates - when characters actually get into
    a position, an ActivePosition instance is created.
    
    Example:
        MISSIONARY = PositionDefinition(
            key="missionary",
            name="Missionary",
            description="Classic face-to-face position with one partner on top.",
            slots={
                "top": SlotDefinition(...),
                "bottom": SlotDefinition(...)
            },
            requirements=PositionRequirement(furniture_types={FurnitureType.BED}),
            tags={"penetrative", "intimate", "face_to_face"}
        )
    """
    key: str                              # Unique identifier
    name: str                             # Display name
    description: str                       # Player-facing description
    
    # The slots/roles in this position
    slots: Dict[str, SlotDefinition] = field(default_factory=dict)
    
    # Requirements to use this position
    requirements: PositionRequirement = field(default_factory=PositionRequirement)
    
    # Tags for categorization and search
    tags: Set[str] = field(default_factory=set)
    
    # Alternative names for command matching
    aliases: List[str] = field(default_factory=list)
    
    # Description templates
    start_msg: str = ""     # "{top} and {bottom} get into position"
    end_msg: str = ""       # "{top} and {bottom} disengage"
    ambient_msg: str = ""   # Periodic description while in position
    
    # Transition options
    # What positions can be transitioned to without fully disengaging
    transitions_to: Set[str] = field(default_factory=set)
    
    # Intensity/mood
    intensity: str = "normal"  # "gentle", "normal", "rough", "extreme"
    mood: str = "neutral"      # "romantic", "passionate", "dominant", "playful"
    
    # For display grouping
    category: str = "general"  # "penetrative", "oral", "manual", "bondage", etc.
    
    def get_slot(self, slot_key: str) -> Optional[SlotDefinition]:
        """Get a slot definition by key."""
        return self.slots.get(slot_key)
    
    def get_slot_names(self) -> List[str]:
        """Get list of slot keys."""
        return list(self.slots.keys())
    
    def get_access_map(self, from_slot: str, to_slot: str) -> Set[BodyZone]:
        """Get what zones from_slot can access on to_slot."""
        slot = self.slots.get(from_slot)
        if not slot:
            return set()
        return slot.get_access_to(to_slot)
    
    def get_all_access_for_slot(self, slot_key: str) -> Dict[str, Set[BodyZone]]:
        """Get all access this slot has to other slots."""
        slot = self.slots.get(slot_key)
        if not slot:
            return {}
        return slot.can_access.copy()
    
    def can_use(
        self,
        participants: List[Any],
        furniture: Optional[Any] = None
    ) -> tuple:
        """
        Check if the given participants can use this position.
        
        Args:
            participants: List of character objects
            furniture: Optional furniture/anchor object
            
        Returns:
            (success: bool, reason: str)
        """
        # Check participant count
        success, reason = self.requirements.check_participants(len(participants))
        if not success:
            return False, reason
        
        # Check furniture
        success, reason = self.requirements.check_furniture(furniture)
        if not success:
            return False, reason
        
        # Check mobility requirements
        if self.requirements.required_mobility:
            for char in participants:
                body = getattr(char, "body", None)
                if body:
                    structure = getattr(body, "structure", None)
                    if structure:
                        mobility = getattr(structure, "locomotion", "bipedal")
                        if mobility not in self.requirements.required_mobility:
                            char_name = getattr(char, "key", "Someone")
                            return False, f"{char_name}'s body structure isn't compatible"
        
        return True, ""
    
    def matches_search(self, query: str) -> bool:
        """Check if this position matches a search query."""
        query_lower = query.lower()
        
        # Check key
        if query_lower in self.key.lower():
            return True
        
        # Check name
        if query_lower in self.name.lower():
            return True
        
        # Check aliases
        for alias in self.aliases:
            if query_lower in alias.lower():
                return True
        
        # Check tags
        for tag in self.tags:
            if query_lower in tag.lower():
                return True
        
        return False


# ============================================================================
# Slot Builder Helpers
# ============================================================================

def make_slot(
    key: str,
    name: str,
    posture: Posture,
    mobility: Mobility = Mobility.FREE,
    accesses: Optional[Dict[str, Set[BodyZone]]] = None,
    exposed: Optional[Set[BodyZone]] = None,
    blocked: Optional[Set[BodyZone]] = None,
    hands_free: bool = True,
    mouth_free: bool = True,
    can_thrust: bool = False,
    controls_pace: bool = False,
    description: str = "",
    expandable: bool = False,
    max_occupants: int = 1
) -> SlotDefinition:
    """
    Convenience builder for SlotDefinition.
    
    Example:
        top_slot = make_slot(
            "top", "top",
            posture=Posture.LYING_FRONT,
            mobility=Mobility.ACTIVE,
            accesses={"bottom": FRONT_ACCESS},
            can_thrust=True,
            controls_pace=True
        )
    """
    return SlotDefinition(
        key=key,
        name=name,
        posture=posture,
        mobility=mobility,
        can_access=accesses or {},
        exposed_to_room=exposed or set(),
        blocked=blocked or set(),
        hands_free=hands_free,
        mouth_free=mouth_free,
        can_thrust=can_thrust,
        controls_pace=controls_pace,
        description=description,
        expandable=expandable,
        max_occupants=max_occupants
    )


# ============================================================================
# Common Zone Sets
# ============================================================================

# Pre-defined zone sets for common access patterns
FRONT_UPPER = {BodyZone.FACE, BodyZone.MOUTH, BodyZone.NECK, BodyZone.CHEST, BodyZone.BREASTS}
FRONT_LOWER = {BodyZone.BELLY, BodyZone.GROIN, BodyZone.HIPS, BodyZone.THIGHS}
FRONT_FULL = FRONT_UPPER | FRONT_LOWER

BACK_UPPER = {BodyZone.BACK_UPPER, BodyZone.SHOULDERS, BodyZone.NECK}
BACK_LOWER = {BodyZone.BACK_LOWER, BodyZone.ASS, BodyZone.HIPS}
BACK_FULL = BACK_UPPER | BACK_LOWER | {BodyZone.TAIL}

# Access from behind (ass/groin accessible)
BEHIND_ACCESS = {BodyZone.ASS, BodyZone.GROIN, BodyZone.HIPS, BodyZone.THIGHS, BodyZone.BACK_LOWER, BodyZone.TAIL}

# Face-to-face intimate access
INTIMATE_FRONT = FRONT_FULL | {BodyZone.EARS, BodyZone.HAIR}

# Full body access (for suspension, etc.)
ALL_ZONES = {z for z in BodyZone if z != BodyZone.WHOLE_BODY}

# Oral focus
ORAL_GIVER_ACCESS = {BodyZone.GROIN, BodyZone.THIGHS, BodyZone.BELLY, BodyZone.HIPS}
ORAL_RECEIVER_ACCESS = {BodyZone.HAIR, BodyZone.EARS, BodyZone.FACE}  # Can grab head

# For 69 position
MUTUAL_ORAL_ACCESS = {BodyZone.GROIN, BodyZone.ASS, BodyZone.THIGHS}

# Seated access (lap dance, riding)
LAP_ACCESS = {BodyZone.GROIN, BodyZone.THIGHS, BodyZone.HIPS, BodyZone.ASS}

# What's typically exposed when bent over
BENT_OVER_EXPOSED = {BodyZone.MOUTH, BodyZone.FACE, BodyZone.ASS, BodyZone.GROIN, BodyZone.BREASTS}
