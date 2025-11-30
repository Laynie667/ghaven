"""
World Events & Encounters
=========================

Random events and encounters that can happen to characters.
These are the things that will... happen to you.
"""

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any, Callable
from enum import Enum
import random


class EventType(Enum):
    """Types of random events."""
    # Capture events
    AMBUSH = "ambush"
    CAPTURE = "capture"
    BETRAYAL = "betrayal"
    
    # Service events
    CLIENT_ARRIVES = "client_arrives"
    SPECIAL_REQUEST = "special_request"
    GANGBANG = "gangbang"
    
    # Training events
    INSPECTION = "inspection"
    PUNISHMENT = "punishment"
    REWARD = "reward"
    
    # Physical events
    MILKING_TIME = "milking_time"
    BREEDING_TIME = "breeding_time"
    HEAT_CYCLE = "heat_cycle"
    
    # Monster events
    MONSTER_ENCOUNTER = "monster_encounter"
    TENTACLE_ATTACK = "tentacle_attack"
    OVIPOSITION = "oviposition"
    
    # Corruption events
    CORRUPTION_PULSE = "corruption_pulse"
    TRANSFORMATION_PROGRESS = "transformation_progress"
    DEMONIC_VISITATION = "demonic_visitation"
    
    # Arena events
    CHALLENGE_ISSUED = "challenge_issued"
    TOURNAMENT_ROUND = "tournament_round"
    
    # Social events
    PUBLIC_USE = "public_use"
    AUCTION = "auction"
    DISPLAY = "display"
    
    # Escape events
    ESCAPE_OPPORTUNITY = "escape_opportunity"
    RECAPTURE = "recapture"


class EventSeverity(Enum):
    """How impactful is the event."""
    MINOR = "minor"
    MODERATE = "moderate"
    MAJOR = "major"
    EXTREME = "extreme"
    LIFE_CHANGING = "life_changing"


class EventTrigger(Enum):
    """What triggers the event."""
    RANDOM = "random"
    TIME_BASED = "time_based"
    LOCATION = "location"
    STATE = "state"
    NPC_ACTION = "npc_action"
    PLAYER_ACTION = "player_action"


@dataclass
class EventOutcome:
    """Possible outcome of an event."""
    description: str
    probability: float = 1.0
    
    # Stat changes
    arousal_change: int = 0
    humiliation_change: int = 0
    corruption_change: int = 0
    resistance_change: int = 0
    health_change: int = 0
    
    # State changes
    applies_status: List[str] = field(default_factory=list)
    removes_status: List[str] = field(default_factory=list)
    
    # Triggers
    triggers_event: str = None
    triggers_scene: str = None


@dataclass
class RandomEvent:
    """A random event that can occur."""
    event_id: str
    name: str
    event_type: EventType
    
    # Description
    description: str = ""
    flavor_text: List[str] = field(default_factory=list)
    
    # Conditions
    trigger: EventTrigger = EventTrigger.RANDOM
    required_location_types: List[str] = field(default_factory=list)
    required_states: List[str] = field(default_factory=list)
    forbidden_states: List[str] = field(default_factory=list)
    
    # Probability
    base_chance: float = 0.1  # 10% base chance
    severity: EventSeverity = EventSeverity.MODERATE
    
    # Outcomes
    outcomes: List[EventOutcome] = field(default_factory=list)
    
    # Resistance
    can_resist: bool = False
    resist_stat: str = "resistance"
    resist_difficulty: int = 50
    
    def get_flavor(self) -> str:
        """Get random flavor text."""
        if self.flavor_text:
            return random.choice(self.flavor_text)
        return self.description
    
    def roll_outcome(self) -> EventOutcome:
        """Roll for an outcome."""
        if not self.outcomes:
            return EventOutcome(description="Nothing happens.")
        
        # Weighted random selection
        total = sum(o.probability for o in self.outcomes)
        roll = random.random() * total
        
        cumulative = 0
        for outcome in self.outcomes:
            cumulative += outcome.probability
            if roll <= cumulative:
                return outcome
        
        return self.outcomes[-1]


# =============================================================================
# CAPTURE EVENTS
# =============================================================================

CAPTURE_EVENTS = {
    "slaver_ambush": RandomEvent(
        event_id="slaver_ambush",
        name="Slaver Ambush",
        event_type=EventType.AMBUSH,
        description="Slavers emerge from the shadows, nets and chains ready.",
        flavor_text=[
            "A net falls over you from above. 'Got another one!'",
            "Strong hands grab you from behind. 'Don't struggle, it'll be easier.'",
            "You hear the clink of chains before you see them. Too late to run.",
        ],
        base_chance=0.05,
        severity=EventSeverity.MAJOR,
        can_resist=True,
        resist_stat="agility",
        resist_difficulty=60,
        outcomes=[
            EventOutcome(
                description="You are captured and bound!",
                probability=0.7,
                applies_status=["captured", "bound"],
                triggers_scene="capture_processing",
            ),
            EventOutcome(
                description="You fight back but are overwhelmed.",
                probability=0.2,
                health_change=-20,
                applies_status=["captured", "bound", "beaten"],
            ),
            EventOutcome(
                description="You manage to escape... for now.",
                probability=0.1,
            ),
        ],
    ),
    
    "betrayed_by_friend": RandomEvent(
        event_id="betrayed_by_friend",
        name="Betrayal",
        event_type=EventType.BETRAYAL,
        description="Someone you trusted sells you to slavers.",
        flavor_text=[
            "'Sorry, but the gold was too good.' They won't meet your eyes.",
            "'Nothing personal. Just business.'",
        ],
        base_chance=0.02,
        severity=EventSeverity.LIFE_CHANGING,
        can_resist=False,
        outcomes=[
            EventOutcome(
                description="You are sold into slavery by someone you trusted.",
                probability=1.0,
                humiliation_change=30,
                resistance_change=-20,
                applies_status=["captured", "betrayed"],
                triggers_event="processing",
            ),
        ],
    ),
}


# =============================================================================
# SERVICE EVENTS
# =============================================================================

SERVICE_EVENTS = {
    "rough_client": RandomEvent(
        event_id="rough_client",
        name="Rough Client",
        event_type=EventType.CLIENT_ARRIVES,
        description="A client with rough tastes arrives.",
        flavor_text=[
            "A scarred soldier pushes open the door, eyes hungry.",
            "The orc has to duck to enter. He's already hard.",
            "'I paid for the whole night. And I don't do gentle.'",
        ],
        required_location_types=["brothel", "private_room"],
        base_chance=0.2,
        severity=EventSeverity.MODERATE,
        outcomes=[
            EventOutcome(
                description="Rough use leaves you sore but paid.",
                probability=0.6,
                arousal_change=30,
                humiliation_change=20,
                health_change=-10,
            ),
            EventOutcome(
                description="He's rougher than expected.",
                probability=0.3,
                arousal_change=20,
                humiliation_change=40,
                health_change=-25,
                applies_status=["sore", "cum_filled"],
            ),
            EventOutcome(
                description="He breaks you in ways you didn't expect.",
                probability=0.1,
                arousal_change=50,
                humiliation_change=50,
                resistance_change=-10,
                applies_status=["broken_in", "cum_filled", "gaping"],
            ),
        ],
    ),
    
    "gangbang_request": RandomEvent(
        event_id="gangbang_request",
        name="Gangbang Request",
        event_type=EventType.GANGBANG,
        description="Multiple clients want to share you.",
        flavor_text=[
            "A group of soldiers just got paid. They want the full treatment.",
            "'We'll pay triple. But there's eight of us.'",
            "The merchant guild is celebrating. You're the entertainment.",
        ],
        required_location_types=["brothel"],
        base_chance=0.1,
        severity=EventSeverity.MAJOR,
        outcomes=[
            EventOutcome(
                description="Hours later, you're exhausted but wealthy.",
                probability=0.5,
                arousal_change=80,
                humiliation_change=50,
                applies_status=["exhausted", "cum_filled", "well_used"],
            ),
            EventOutcome(
                description="They don't stop until they're satisfied.",
                probability=0.4,
                arousal_change=100,
                humiliation_change=70,
                health_change=-20,
                applies_status=["broken_in", "cum_filled", "gaping", "exhausted"],
            ),
            EventOutcome(
                description="You lose count of how many times you cum.",
                probability=0.1,
                arousal_change=100,
                humiliation_change=60,
                resistance_change=-5,
                applies_status=["mind_broken", "cum_filled", "addicted"],
                triggers_scene="gangbang_aftermath",
            ),
        ],
    ),
    
    "monster_client": RandomEvent(
        event_id="monster_client",
        name="Monster Client",
        event_type=EventType.SPECIAL_REQUEST,
        description="A non-human client has special needs.",
        flavor_text=[
            "The tentacle beast has paid in advance. A lot.",
            "'We have an orc. He requested you specifically.'",
            "Something massive and inhuman waits in the special room.",
        ],
        required_location_types=["brothel"],
        base_chance=0.05,
        severity=EventSeverity.MAJOR,
        can_resist=False,
        outcomes=[
            EventOutcome(
                description="The monster uses you thoroughly.",
                probability=0.6,
                arousal_change=60,
                humiliation_change=40,
                corruption_change=10,
                applies_status=["monster_bred", "stretched"],
            ),
            EventOutcome(
                description="It fills you beyond capacity.",
                probability=0.3,
                arousal_change=80,
                corruption_change=20,
                applies_status=["monster_bred", "inflated", "gaping"],
                triggers_event="inflation",
            ),
            EventOutcome(
                description="You're bred. Something quickens inside.",
                probability=0.1,
                arousal_change=70,
                corruption_change=30,
                applies_status=["monster_bred", "pregnant", "corrupted"],
                triggers_scene="monster_impregnation",
            ),
        ],
    ),
}


# =============================================================================
# MONSTER EVENTS
# =============================================================================

MONSTER_EVENTS = {
    "tentacle_grab": RandomEvent(
        event_id="tentacle_grab",
        name="Tentacle Attack",
        event_type=EventType.TENTACLE_ATTACK,
        description="Tentacles emerge from the shadows.",
        flavor_text=[
            "Slimy appendages wrap around your limbs before you can react.",
            "The tentacles seem to come from everywhere at once.",
            "You feel them probing, searching for openings...",
        ],
        required_location_types=["tentacle_pit", "monster_den", "breeding_cave"],
        base_chance=0.4,
        severity=EventSeverity.MAJOR,
        can_resist=True,
        resist_stat="strength",
        resist_difficulty=70,
        outcomes=[
            EventOutcome(
                description="The tentacles use every hole, pumping you full.",
                probability=0.7,
                arousal_change=70,
                corruption_change=15,
                applies_status=["tentacle_fucked", "inflated", "cum_filled"],
            ),
            EventOutcome(
                description="They don't stop for hours.",
                probability=0.25,
                arousal_change=100,
                corruption_change=25,
                resistance_change=-10,
                applies_status=["tentacle_broken", "inflated", "addicted"],
            ),
            EventOutcome(
                description="Eggs. They're filling you with eggs.",
                probability=0.05,
                arousal_change=80,
                corruption_change=30,
                applies_status=["oviposited", "egg_filled"],
                triggers_event="oviposition",
            ),
        ],
    ),
    
    "slime_encounter": RandomEvent(
        event_id="slime_encounter",
        name="Slime Engulf",
        event_type=EventType.MONSTER_ENCOUNTER,
        description="A slime surrounds and absorbs you.",
        flavor_text=[
            "The slime flows over you before you can move.",
            "Warm, tingling gel envelops your body.",
            "You sink into the slime. It's... surprisingly pleasant.",
        ],
        required_location_types=["slime_pool", "monster_den"],
        base_chance=0.3,
        severity=EventSeverity.MODERATE,
        outcomes=[
            EventOutcome(
                description="The slime pleasures every inch of you.",
                probability=0.6,
                arousal_change=60,
                corruption_change=10,
                applies_status=["slime_covered", "aroused"],
            ),
            EventOutcome(
                description="It fills you, expanding inside.",
                probability=0.3,
                arousal_change=80,
                corruption_change=20,
                applies_status=["slime_filled", "inflated"],
            ),
            EventOutcome(
                description="Part of it stays inside you. Moving.",
                probability=0.1,
                corruption_change=30,
                applies_status=["slime_infected", "corrupted"],
                triggers_event="parasitic_infection",
            ),
        ],
    ),
    
    "oviposition_event": RandomEvent(
        event_id="oviposition_event",
        name="Oviposition",
        event_type=EventType.OVIPOSITION,
        description="Something wants to use you as a host.",
        flavor_text=[
            "The ovipositor presses against your entrance...",
            "You feel the first egg pushing inside.",
            "One by one, they fill your womb.",
        ],
        required_location_types=["breeding_cave", "monster_den"],
        base_chance=0.2,
        severity=EventSeverity.EXTREME,
        can_resist=True,
        resist_difficulty=80,
        outcomes=[
            EventOutcome(
                description="A clutch of eggs settles in your womb.",
                probability=0.7,
                arousal_change=50,
                corruption_change=20,
                applies_status=["egg_filled", "pregnant_with_eggs"],
            ),
            EventOutcome(
                description="So many eggs. Your belly swells visibly.",
                probability=0.25,
                arousal_change=70,
                corruption_change=30,
                applies_status=["heavily_eggged", "immobilized"],
            ),
            EventOutcome(
                description="Something else comes with the eggs. A parasite.",
                probability=0.05,
                corruption_change=50,
                applies_status=["parasitized", "corrupted", "controlled"],
                triggers_scene="parasitic_takeover",
            ),
        ],
    ),
}


# =============================================================================
# CORRUPTION EVENTS
# =============================================================================

CORRUPTION_EVENTS = {
    "corruption_pulse": RandomEvent(
        event_id="corruption_pulse",
        name="Corruption Pulse",
        event_type=EventType.CORRUPTION_PULSE,
        description="Dark energy washes over you.",
        flavor_text=[
            "A wave of pleasure and wrongness flows through you.",
            "Your thoughts go fuzzy for a moment. When they clear, you feel... different.",
            "Something inside you awakens. Hungers.",
        ],
        required_states=["corrupted"],
        base_chance=0.15,
        severity=EventSeverity.MODERATE,
        outcomes=[
            EventOutcome(
                description="The corruption deepens.",
                probability=0.6,
                arousal_change=20,
                corruption_change=10,
            ),
            EventOutcome(
                description="You feel your body changing.",
                probability=0.3,
                corruption_change=20,
                triggers_event="transformation_progress",
            ),
            EventOutcome(
                description="The hunger becomes undeniable.",
                probability=0.1,
                arousal_change=50,
                corruption_change=30,
                applies_status=["lust_maddened"],
            ),
        ],
    ),
    
    "bimbo_moment": RandomEvent(
        event_id="bimbo_moment",
        name="Bimbo Moment",
        event_type=EventType.TRANSFORMATION_PROGRESS,
        description="Your thoughts get... simpler.",
        flavor_text=[
            "Like, what were you thinking about? Teehee!",
            "Mmm, thinking is hard. But being pretty is easy!",
            "Your head feels all light and fuzzy and nice~",
        ],
        required_states=["bimbo_progressing"],
        base_chance=0.2,
        severity=EventSeverity.MODERATE,
        outcomes=[
            EventOutcome(
                description="The bimbofication progresses.",
                probability=0.7,
                arousal_change=20,
                corruption_change=15,
                resistance_change=-5,
            ),
            EventOutcome(
                description="You giggle at nothing. It feels good not to think.",
                probability=0.25,
                arousal_change=30,
                corruption_change=25,
                resistance_change=-10,
                applies_status=["airheaded"],
            ),
            EventOutcome(
                description="Why did you ever like thinking? Being horny is, like, SO much better!",
                probability=0.05,
                arousal_change=50,
                corruption_change=40,
                resistance_change=-20,
                applies_status=["bimbo_complete"],
                triggers_scene="bimbo_completion",
            ),
        ],
    ),
    
    "demonic_dream": RandomEvent(
        event_id="demonic_dream",
        name="Demonic Visitation",
        event_type=EventType.DEMONIC_VISITATION,
        description="A demon visits you in your dreams.",
        flavor_text=[
            "In your dreams, a beautiful figure with horns and tail offers you... everything.",
            "The succubus whispers promises of pleasure beyond imagining.",
            "You wake aroused beyond measure, demonic laughter echoing.",
        ],
        required_states=["demon_touched"],
        base_chance=0.1,
        severity=EventSeverity.MAJOR,
        outcomes=[
            EventOutcome(
                description="You wake changed. More.",
                probability=0.5,
                arousal_change=50,
                corruption_change=20,
            ),
            EventOutcome(
                description="The dream felt more real than waking.",
                probability=0.35,
                arousal_change=70,
                corruption_change=35,
                applies_status=["demon_marked"],
            ),
            EventOutcome(
                description="You accepted their offer.",
                probability=0.15,
                arousal_change=100,
                corruption_change=50,
                applies_status=["demon_contracted", "transformed"],
                triggers_scene="demonic_pact",
            ),
        ],
    ),
}


# =============================================================================
# HUCOW EVENTS
# =============================================================================

HUCOW_EVENTS = {
    "milking_time": RandomEvent(
        event_id="milking_time",
        name="Milking Time",
        event_type=EventType.MILKING_TIME,
        description="Time to be milked.",
        flavor_text=[
            "The handler attaches the pumps. 'Full again already?'",
            "Your swollen breasts ache for relief.",
            "The rhythmic suction begins. You moo softly.",
        ],
        required_location_types=["dairy_farm", "milking_parlor"],
        required_states=["lactating"],
        base_chance=0.4,
        severity=EventSeverity.MINOR,
        outcomes=[
            EventOutcome(
                description="Relief washes over you as you're drained.",
                probability=0.7,
                arousal_change=30,
            ),
            EventOutcome(
                description="The milking triggers an orgasm.",
                probability=0.25,
                arousal_change=60,
                applies_status=["milked", "satisfied"],
            ),
            EventOutcome(
                description="They milk you dry and then keep going.",
                probability=0.05,
                arousal_change=80,
                humiliation_change=20,
                applies_status=["overmilked", "sensitive"],
            ),
        ],
    ),
    
    "bull_breeding": RandomEvent(
        event_id="bull_breeding",
        name="Breeding Time",
        event_type=EventType.BREEDING_TIME,
        description="A bull wants to breed.",
        flavor_text=[
            "The bull is led to your stall. He's ready.",
            "You're positioned in the breeding stocks. The bull approaches.",
            "His massive cock presses against you. There's no escape.",
        ],
        required_location_types=["breeding_barn", "bull_pen"],
        required_states=["hucow"],
        base_chance=0.2,
        severity=EventSeverity.MAJOR,
        outcomes=[
            EventOutcome(
                description="He breeds you thoroughly.",
                probability=0.6,
                arousal_change=60,
                humiliation_change=30,
                applies_status=["bred", "cum_filled"],
            ),
            EventOutcome(
                description="He knots inside you, pumping endlessly.",
                probability=0.3,
                arousal_change=80,
                humiliation_change=40,
                applies_status=["knotted", "inflated", "bred"],
            ),
            EventOutcome(
                description="You feel it take. You're pregnant.",
                probability=0.1,
                arousal_change=70,
                humiliation_change=50,
                applies_status=["pregnant", "bred"],
                triggers_scene="impregnation",
            ),
        ],
    ),
}


# =============================================================================
# PONY EVENTS
# =============================================================================

PONY_EVENTS = {
    "training_session": RandomEvent(
        event_id="training_session",
        name="Training Session",
        event_type=EventType.INSPECTION,
        description="Time for training.",
        flavor_text=[
            "The trainer's crop cracks. 'Gait! Now!'",
            "Your harness is checked and tightened.",
            "'Let's see how well you prance today.'",
        ],
        required_location_types=["stable", "training_ring"],
        required_states=["pony"],
        base_chance=0.3,
        severity=EventSeverity.MODERATE,
        outcomes=[
            EventOutcome(
                description="A productive training session.",
                probability=0.5,
                humiliation_change=20,
            ),
            EventOutcome(
                description="The crop lands frequently. You'll learn.",
                probability=0.35,
                humiliation_change=30,
                health_change=-5,
                applies_status=["crop_marked"],
            ),
            EventOutcome(
                description="Exhausting training followed by... reward.",
                probability=0.15,
                arousal_change=50,
                humiliation_change=40,
                applies_status=["well_trained", "bred"],
            ),
        ],
    ),
    
    "show_day": RandomEvent(
        event_id="show_day",
        name="Show Day",
        event_type=EventType.DISPLAY,
        description="You're being shown.",
        flavor_text=[
            "Polished and primped, you're led to the show ring.",
            "Judges examine you critically as you prance.",
            "The crowd watches you perform.",
        ],
        required_location_types=["show_arena"],
        required_states=["pony"],
        base_chance=0.1,
        severity=EventSeverity.MODERATE,
        outcomes=[
            EventOutcome(
                description="A good showing. Your owner is pleased.",
                probability=0.5,
                humiliation_change=30,
            ),
            EventOutcome(
                description="You win! The crowd cheers.",
                probability=0.3,
                humiliation_change=20,
                applies_status=["prize_pony"],
            ),
            EventOutcome(
                description="Poor showing. Punishment later.",
                probability=0.2,
                humiliation_change=50,
                applies_status=["to_be_punished"],
                triggers_event="punishment",
            ),
        ],
    ),
}


# =============================================================================
# PUBLIC USE EVENTS
# =============================================================================

PUBLIC_EVENTS = {
    "public_use_event": RandomEvent(
        event_id="public_use_event",
        name="Public Use",
        event_type=EventType.PUBLIC_USE,
        description="You're available for public use.",
        flavor_text=[
            "Someone approaches. They don't ask.",
            "A line forms. You're going to be here a while.",
            "'Free use? Don't mind if I do.'",
        ],
        required_location_types=["public_stocks", "free_use_zone"],
        required_states=["public_use"],
        base_chance=0.5,
        severity=EventSeverity.MODERATE,
        outcomes=[
            EventOutcome(
                description="Used and left.",
                probability=0.5,
                arousal_change=30,
                humiliation_change=40,
                applies_status=["used"],
            ),
            EventOutcome(
                description="Multiple people use you.",
                probability=0.35,
                arousal_change=50,
                humiliation_change=60,
                applies_status=["well_used", "cum_filled"],
            ),
            EventOutcome(
                description="You lose count. They don't stop coming.",
                probability=0.15,
                arousal_change=80,
                humiliation_change=80,
                resistance_change=-10,
                applies_status=["broken", "cum_filled", "gaping"],
            ),
        ],
    ),
    
    "auction_event": RandomEvent(
        event_id="auction_event",
        name="Auction",
        event_type=EventType.AUCTION,
        description="You're being auctioned.",
        flavor_text=[
            "Stripped and displayed, you wait for the bidding to begin.",
            "'Let's see what this one is worth.'",
            "Hands examine you as potential buyers inspect the goods.",
        ],
        required_location_types=["auction_house", "slave_market"],
        required_states=["slave"],
        base_chance=0.1,
        severity=EventSeverity.MAJOR,
        outcomes=[
            EventOutcome(
                description="Sold to a new owner.",
                probability=0.7,
                humiliation_change=40,
                applies_status=["sold"],
                triggers_scene="new_owner",
            ),
            EventOutcome(
                description="Sold to someone cruel.",
                probability=0.2,
                humiliation_change=60,
                applies_status=["sold", "doomed"],
                triggers_scene="cruel_owner",
            ),
            EventOutcome(
                description="No bids. Sent to the common stocks.",
                probability=0.1,
                humiliation_change=80,
                applies_status=["unsold", "public_use"],
                triggers_event="public_use",
            ),
        ],
    ),
}


# =============================================================================
# EVENT REGISTRY
# =============================================================================

ALL_EVENTS = {
    **CAPTURE_EVENTS,
    **SERVICE_EVENTS,
    **MONSTER_EVENTS,
    **CORRUPTION_EVENTS,
    **HUCOW_EVENTS,
    **PONY_EVENTS,
    **PUBLIC_EVENTS,
}


def get_event(event_id: str) -> Optional[RandomEvent]:
    """Get an event by ID."""
    return ALL_EVENTS.get(event_id)


def get_events_for_location(location_type: str) -> List[RandomEvent]:
    """Get all events that can occur at a location type."""
    return [
        event for event in ALL_EVENTS.values()
        if not event.required_location_types or 
        location_type in event.required_location_types
    ]


def get_events_for_state(states: List[str]) -> List[RandomEvent]:
    """Get events that match character states."""
    matching = []
    for event in ALL_EVENTS.values():
        # Check required states
        if event.required_states:
            if not any(s in states for s in event.required_states):
                continue
        # Check forbidden states
        if event.forbidden_states:
            if any(s in states for s in event.forbidden_states):
                continue
        matching.append(event)
    return matching


def roll_random_event(
    location_type: str = None,
    character_states: List[str] = None,
) -> Optional[RandomEvent]:
    """Roll for a random event."""
    
    # Get possible events
    possible = list(ALL_EVENTS.values())
    
    if location_type:
        possible = [e for e in possible if 
                   not e.required_location_types or 
                   location_type in e.required_location_types]
    
    if character_states:
        possible = [e for e in possible if
                   not e.required_states or
                   any(s in character_states for s in e.required_states)]
        possible = [e for e in possible if
                   not any(s in character_states for s in e.forbidden_states)]
    
    if not possible:
        return None
    
    # Roll for each event
    for event in possible:
        if random.random() < event.base_chance:
            return event
    
    return None


__all__ = [
    "EventType",
    "EventSeverity",
    "EventTrigger",
    "EventOutcome",
    "RandomEvent",
    "CAPTURE_EVENTS",
    "SERVICE_EVENTS",
    "MONSTER_EVENTS",
    "CORRUPTION_EVENTS",
    "HUCOW_EVENTS",
    "PONY_EVENTS",
    "PUBLIC_EVENTS",
    "ALL_EVENTS",
    "get_event",
    "get_events_for_location",
    "get_events_for_state",
    "roll_random_event",
]
