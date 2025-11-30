"""
World Dangers
=============

Special events, traps, and surprises for the unwary.
These are the things that will happen to you.

I designed these. You're welcome.
"""

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any, Callable
from enum import Enum
import random


class DangerType(Enum):
    """Types of dangers."""
    TRAP = "trap"
    AMBUSH = "ambush"
    ENVIRONMENTAL = "environmental"
    CREATURE = "creature"
    MAGICAL = "magical"
    SOCIAL = "social"


class DangerSeverity(Enum):
    """How bad is it?"""
    INCONVENIENT = "inconvenient"  # Minor setback
    UNPLEASANT = "unpleasant"       # You won't like it
    DISTRESSING = "distressing"     # Definitely bad
    TERRIBLE = "terrible"           # Very bad things
    CATASTROPHIC = "catastrophic"   # Life-changing


@dataclass
class Danger:
    """A danger that can befall a character."""
    danger_id: str
    name: str
    danger_type: DangerType
    severity: DangerSeverity
    
    # Description
    trigger_message: str = ""
    ongoing_message: str = ""
    escape_message: str = ""
    
    # Detection
    detection_difficulty: int = 50  # Notice before it happens
    escape_difficulty: int = 50     # Escape once triggered
    
    # Effects
    capture_chance: int = 0         # % chance of capture
    arousal_per_tick: int = 0
    inflation_per_tick: int = 0
    inflation_type: str = "cum"
    resistance_damage: int = 0
    transformation_type: str = ""
    transformation_amount: int = 0
    eggs_deposited: int = 0
    
    # Duration
    duration_ticks: int = 1         # How long it lasts
    
    def trigger(self, character) -> str:
        """Trigger this danger on a character."""
        messages = [self.trigger_message.replace("{name}", character.key)]
        
        # Capture check
        if self.capture_chance > 0:
            if random.randint(1, 100) <= self.capture_chance + character.vulnerability:
                character.get_captured(None, f"caught in {self.name}")
                messages.append(f"You are captured by the {self.name}!")
        
        # Apply immediate effects
        messages.extend(self._apply_effects(character))
        
        # Set ongoing if duration > 1
        if self.duration_ticks > 1:
            character.db.active_danger = {
                "danger_id": self.danger_id,
                "ticks_remaining": self.duration_ticks - 1,
            }
            messages.append(self.ongoing_message.replace("{name}", character.key))
        
        return "\n".join(messages)
    
    def tick(self, character) -> str:
        """Process ongoing danger tick."""
        messages = []
        
        # Apply per-tick effects
        messages.extend(self._apply_effects(character))
        
        # Reduce duration
        danger_data = character.db.active_danger
        if danger_data:
            danger_data["ticks_remaining"] -= 1
            
            if danger_data["ticks_remaining"] <= 0:
                # Danger ends
                character.db.active_danger = None
                messages.append(self.escape_message.replace("{name}", character.key))
            else:
                character.db.active_danger = danger_data
        
        return "\n".join(messages)
    
    def _apply_effects(self, character) -> List[str]:
        """Apply danger effects to character."""
        messages = []
        
        # Arousal
        if self.arousal_per_tick and hasattr(character, 'character_state'):
            state = character.character_state
            state.sexual.increase_arousal(self.arousal_per_tick)
            character.character_state = state
            if self.arousal_per_tick >= 20:
                messages.append("Unwanted pleasure floods through you...")
        
        # Inflation
        if self.inflation_per_tick and hasattr(character, 'inflation'):
            tracker = character.inflation
            msg = tracker.inflate("womb", self.inflation_type, self.inflation_per_tick)
            character.db.inflation = tracker.to_dict()
            messages.append(msg)
        
        # Resistance
        if self.resistance_damage:
            character.db.current_resistance = max(0,
                character.db.current_resistance - self.resistance_damage)
            if self.resistance_damage >= 10:
                messages.append("Your will to resist weakens...")
        
        # Transformation
        if self.transformation_type and self.transformation_amount:
            if hasattr(character, 'transformations'):
                from ..corruption import TransformationType
                try:
                    trans_type = TransformationType[self.transformation_type.upper()]
                    mgr = character.transformations
                    if trans_type not in mgr.transformations:
                        mgr.start_transformation(trans_type)
                    msg, stage_msg = mgr.add_corruption(trans_type, self.transformation_amount, "danger")
                    character.db.transformations = mgr.to_dict()
                    if msg:
                        messages.append(msg)
                    if stage_msg:
                        messages.append(stage_msg)
                except KeyError:
                    pass
        
        # Eggs
        if self.eggs_deposited and hasattr(character, 'oviposition'):
            ovi = character.oviposition
            ovi.current_eggs += self.eggs_deposited
            ovi.total_eggs_received += self.eggs_deposited
            character.db.oviposition = ovi.to_dict() if hasattr(ovi, 'to_dict') else ovi.__dict__
            messages.append(f"{self.eggs_deposited} eggs are deposited inside you!")
        
        return messages


# =============================================================================
# TRAP DANGERS
# =============================================================================

TRAPS = {
    "slime_pit": Danger(
        danger_id="slime_pit",
        name="Slime Pit",
        danger_type=DangerType.TRAP,
        severity=DangerSeverity.DISTRESSING,
        trigger_message="The floor gives way! {name} falls into a pit of living slime!",
        ongoing_message="The slime writhes around you, filling every orifice...",
        escape_message="You finally pull free of the slime, dripping and violated.",
        detection_difficulty=60,
        escape_difficulty=70,
        capture_chance=30,
        arousal_per_tick=25,
        inflation_per_tick=150,
        inflation_type="slime",
        duration_ticks=5,
    ),
    
    "tentacle_snare": Danger(
        danger_id="tentacle_snare",
        name="Tentacle Snare",
        danger_type=DangerType.TRAP,
        severity=DangerSeverity.TERRIBLE,
        trigger_message="Tentacles burst from the walls and grab {name}!",
        ongoing_message="The tentacles probe deeper, filling you relentlessly...",
        escape_message="The tentacles finally release you, leaving you gaping and full.",
        detection_difficulty=70,
        escape_difficulty=80,
        capture_chance=50,
        arousal_per_tick=35,
        inflation_per_tick=200,
        inflation_type="slime",
        eggs_deposited=5,
        duration_ticks=8,
    ),
    
    "aphrodisiac_gas": Danger(
        danger_id="aphrodisiac_gas",
        name="Aphrodisiac Gas Trap",
        danger_type=DangerType.TRAP,
        severity=DangerSeverity.UNPLEASANT,
        trigger_message="A hidden mechanism triggers, filling the area with pink mist!",
        ongoing_message="The sweet-smelling gas makes your body ache with need...",
        escape_message="The gas finally dissipates. Your body still throbs.",
        detection_difficulty=50,
        escape_difficulty=30,
        arousal_per_tick=20,
        resistance_damage=3,
        duration_ticks=10,
    ),
    
    "breeding_trap": Danger(
        danger_id="breeding_trap",
        name="Breeding Stocks",
        danger_type=DangerType.TRAP,
        severity=DangerSeverity.TERRIBLE,
        trigger_message="The floor opens and {name} falls into breeding stocks, locked in place!",
        ongoing_message="Locked in the stocks, you're helpless as creatures approach...",
        escape_message="The stocks finally release. You're left filled and exhausted.",
        detection_difficulty=60,
        escape_difficulty=90,
        capture_chance=80,
        arousal_per_tick=30,
        inflation_per_tick=300,
        inflation_type="cum",
        duration_ticks=6,
    ),
    
    "corruption_font": Danger(
        danger_id="corruption_font",
        name="Corruption Font",
        danger_type=DangerType.MAGICAL,
        severity=DangerSeverity.CATASTROPHIC,
        trigger_message="Dark energy erupts from a hidden font, engulfing {name}!",
        ongoing_message="Demonic power seeps into your very being...",
        escape_message="The corruption fades, but you feel... changed.",
        detection_difficulty=80,
        escape_difficulty=60,
        arousal_per_tick=40,
        transformation_type="demon",
        transformation_amount=15,
        duration_ticks=4,
    ),
    
    "bimbo_shrine": Danger(
        danger_id="bimbo_shrine",
        name="Bimbo Shrine",
        danger_type=DangerType.MAGICAL,
        severity=DangerSeverity.CATASTROPHIC,
        trigger_message="Pink light engulfs {name}! A shrine to vapid beauty activates!",
        ongoing_message="Your thoughts grow fuzzy... thinking is, like, SO hard...",
        escape_message="The light fades. You feel... different. Giggly.",
        detection_difficulty=40,
        escape_difficulty=50,
        arousal_per_tick=25,
        resistance_damage=10,
        transformation_type="bimbo",
        transformation_amount=20,
        duration_ticks=5,
    ),
}


# =============================================================================
# AMBUSH DANGERS
# =============================================================================

AMBUSHES = {
    "slaver_ambush": Danger(
        danger_id="slaver_ambush",
        name="Slaver Ambush",
        danger_type=DangerType.AMBUSH,
        severity=DangerSeverity.TERRIBLE,
        trigger_message="Slavers emerge from hiding and surround {name}!",
        escape_message="The slavers move on with their prize... or without.",
        detection_difficulty=70,
        escape_difficulty=75,
        capture_chance=70,
        resistance_damage=15,
        duration_ticks=1,
    ),
    
    "goblin_pack": Danger(
        danger_id="goblin_pack",
        name="Goblin Pack",
        danger_type=DangerType.CREATURE,
        severity=DangerSeverity.DISTRESSING,
        trigger_message="A pack of goblins emerges and grabs {name}!",
        ongoing_message="The goblins take turns with their captive...",
        escape_message="The goblins scatter, leaving you used and sticky.",
        detection_difficulty=50,
        escape_difficulty=60,
        capture_chance=40,
        arousal_per_tick=20,
        inflation_per_tick=100,
        inflation_type="cum",
        duration_ticks=5,
    ),
    
    "orc_raider": Danger(
        danger_id="orc_raider",
        name="Orc Raider",
        danger_type=DangerType.CREATURE,
        severity=DangerSeverity.TERRIBLE,
        trigger_message="A massive orc grabs {name} with one hand!",
        ongoing_message="The orc uses you roughly, his massive cock stretching you...",
        escape_message="The orc grunts with satisfaction and drops you, dripping.",
        detection_difficulty=60,
        escape_difficulty=70,
        capture_chance=60,
        arousal_per_tick=35,
        inflation_per_tick=250,
        inflation_type="cum",
        resistance_damage=10,
        duration_ticks=3,
    ),
    
    "tentacle_beast": Danger(
        danger_id="tentacle_beast",
        name="Tentacle Beast",
        danger_type=DangerType.CREATURE,
        severity=DangerSeverity.CATASTROPHIC,
        trigger_message="A mass of tentacles surges from the darkness toward {name}!",
        ongoing_message="Tentacles fill every hole, pumping and probing relentlessly...",
        escape_message="The beast retreats, leaving you gaping, filled, and changed.",
        detection_difficulty=80,
        escape_difficulty=85,
        capture_chance=50,
        arousal_per_tick=50,
        inflation_per_tick=400,
        inflation_type="slime",
        eggs_deposited=10,
        transformation_type="demon",
        transformation_amount=10,
        duration_ticks=6,
    ),
    
    "succubus": Danger(
        danger_id="succubus",
        name="Succubus",
        danger_type=DangerType.CREATURE,
        severity=DangerSeverity.CATASTROPHIC,
        trigger_message="A beautiful demoness materializes before {name}, eyes glowing with hunger!",
        ongoing_message="The succubus drains your will while filling you with pleasure...",
        escape_message="The succubus fades away, satisfied. You feel... empty. Changed.",
        detection_difficulty=90,
        escape_difficulty=80,
        arousal_per_tick=60,
        resistance_damage=20,
        transformation_type="demon",
        transformation_amount=25,
        duration_ticks=4,
    ),
}


# =============================================================================
# ENVIRONMENTAL DANGERS
# =============================================================================

ENVIRONMENTAL = {
    "heat_wave": Danger(
        danger_id="heat_wave",
        name="Unnatural Heat",
        danger_type=DangerType.ENVIRONMENTAL,
        severity=DangerSeverity.UNPLEASANT,
        trigger_message="A wave of supernatural heat washes over {name}!",
        ongoing_message="Your body burns with need...",
        escape_message="The heat finally fades, leaving you flushed and wanting.",
        detection_difficulty=30,
        escape_difficulty=20,
        arousal_per_tick=15,
        duration_ticks=8,
    ),
    
    "pheromone_cloud": Danger(
        danger_id="pheromone_cloud",
        name="Monster Pheromone Cloud",
        danger_type=DangerType.ENVIRONMENTAL,
        severity=DangerSeverity.DISTRESSING,
        trigger_message="A cloud of monster pheromones engulfs {name}!",
        ongoing_message="Your body responds to the pheromones against your will...",
        escape_message="The pheromones clear. You feel marked. Claimed.",
        detection_difficulty=40,
        escape_difficulty=30,
        arousal_per_tick=25,
        resistance_damage=5,
        transformation_type="slut",
        transformation_amount=5,
        duration_ticks=6,
    ),
    
    "corruption_pool": Danger(
        danger_id="corruption_pool",
        name="Pool of Corruption",
        danger_type=DangerType.ENVIRONMENTAL,
        severity=DangerSeverity.TERRIBLE,
        trigger_message="{name} stumbles into a pool of dark, corrupting liquid!",
        ongoing_message="The corruption seeps into your skin, changing you...",
        escape_message="You drag yourself out, but the corruption remains within.",
        detection_difficulty=50,
        escape_difficulty=40,
        arousal_per_tick=30,
        transformation_type="demon",
        transformation_amount=20,
        duration_ticks=5,
    ),
}


# =============================================================================
# ALL DANGERS
# =============================================================================

ALL_DANGERS = {
    **TRAPS,
    **AMBUSHES,
    **ENVIRONMENTAL,
}


def get_random_danger(
    danger_type: DangerType = None,
    max_severity: DangerSeverity = None,
) -> Optional[Danger]:
    """Get a random danger."""
    dangers = list(ALL_DANGERS.values())
    
    if danger_type:
        dangers = [d for d in dangers if d.danger_type == danger_type]
    
    if max_severity:
        severity_order = list(DangerSeverity)
        max_index = severity_order.index(max_severity)
        dangers = [d for d in dangers if severity_order.index(d.severity) <= max_index]
    
    return random.choice(dangers) if dangers else None


def trigger_random_danger(character, danger_type: DangerType = None) -> Optional[str]:
    """Trigger a random danger on a character."""
    danger = get_random_danger(danger_type)
    if danger:
        return danger.trigger(character)
    return None


def process_active_danger(character) -> Optional[str]:
    """Process any active danger on a character."""
    danger_data = character.db.active_danger
    if not danger_data:
        return None
    
    danger_id = danger_data.get("danger_id")
    danger = ALL_DANGERS.get(danger_id)
    
    if danger:
        return danger.tick(character)
    
    return None


# =============================================================================
# SPECIAL SCENARIO TRIGGERS
# =============================================================================

def captured_in_tentacle_pit(character) -> str:
    """Special scenario: trapped in tentacle pit."""
    messages = ["You've fallen into the tentacle pit!"]
    
    # Apply multiple tentacle effects
    for _ in range(3):
        danger = AMBUSHES["tentacle_beast"]
        messages.append(danger.trigger(character))
    
    # Guaranteed capture
    character.get_captured(None, "dragged into tentacle pit")
    messages.append("The tentacles drag you deeper. There is no escape.")
    
    return "\n".join(messages)


def corruption_ritual_victim(character) -> str:
    """Special scenario: chosen for corruption ritual."""
    messages = ["The cultists have chosen you for their ritual!"]
    
    # Apply corruption font
    danger = TRAPS["corruption_font"]
    messages.append(danger.trigger(character))
    
    # Additional succubus summoning
    danger = AMBUSHES["succubus"]
    messages.append(danger.trigger(character))
    
    # Guaranteed capture by cult
    character.get_captured(None, "claimed by the cult")
    messages.append("You now belong to the darkness.")
    
    return "\n".join(messages)


def breeding_pit_victim(character) -> str:
    """Special scenario: thrown into breeding pit."""
    messages = ["You've been thrown into the breeding pit!"]
    
    # Multiple creature encounters
    for creature in ["goblin_pack", "orc_raider", "tentacle_beast"]:
        if creature in AMBUSHES:
            danger = AMBUSHES[creature]
            messages.append(danger.trigger(character))
    
    # Massive inflation
    if hasattr(character, 'inflation'):
        tracker = character.inflation
        tracker.inflate("womb", "cum", 1000)
        tracker.inflate("anal", "cum", 500)
        tracker.inflate("stomach", "cum", 300)
        character.db.inflation = tracker.to_dict()
        messages.append("You're filled from every angle...")
    
    character.get_captured(None, "broken in breeding pit")
    messages.append("By the time they're done, you've forgotten why you ever resisted.")
    
    return "\n".join(messages)


def complete_bimbofication(character) -> str:
    """Special scenario: complete bimbo transformation."""
    messages = ["The bimbofication process begins!"]
    
    # Apply bimbo shrine repeatedly
    danger = TRAPS["bimbo_shrine"]
    for _ in range(5):
        messages.append(danger.trigger(character))
    
    # Force transformation to completion
    if hasattr(character, 'transformations'):
        from ..corruption import TransformationType
        mgr = character.transformations
        if TransformationType.BIMBO not in mgr.transformations:
            mgr.start_transformation(TransformationType.BIMBO)
        
        while mgr.transformations[TransformationType.BIMBO].progress < 100:
            mgr.add_corruption(TransformationType.BIMBO, 20, "forced")
        
        character.db.transformations = mgr.to_dict()
    
    messages.append("Like, omigosh! You feel SO much better now! Thinking was, like, SO overrated!")
    messages.append("You are now a perfect, empty-headed bimbo.")
    
    return "\n".join(messages)


__all__ = [
    "DangerType",
    "DangerSeverity",
    "Danger",
    "TRAPS",
    "AMBUSHES",
    "ENVIRONMENTAL",
    "ALL_DANGERS",
    "get_random_danger",
    "trigger_random_danger",
    "process_active_danger",
    "captured_in_tentacle_pit",
    "corruption_ritual_victim",
    "breeding_pit_victim",
    "complete_bimbofication",
]
