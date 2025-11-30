"""
Pet Systems Integration
=======================

Master integration layer that combines all subsystems into cohesive
character classes, provides cross-system hooks, and manages state
synchronization between systems.

This is the recommended import point for game integration.
"""

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any, Tuple, TYPE_CHECKING
from enum import Enum
from datetime import datetime
import random

# =============================================================================
# SUBSYSTEM IMPORTS
# =============================================================================

# Core economy
from ..economy import WalletMixin, OwnerMixin, PropertyMixin

# Pet systems
from ..pets import PetStatsMixin
from ..mounting import MountMixin, RiderMixin

# Training systems
from ..training import TraineeMixin
from ..substances import SubstanceAffectedMixin, TransformableMixin

# Social systems
from ..social import RelationshipMixin

# Physical mechanics
from ..mechanics import GrappleMixin, BondageMixin

# Service systems
from ..service import ServantMixin
from ..production import ProducerMixin

# Slavery
from ..slavery import SlaveMixin, SlaveOwnerMixin

# Hucow
from ..hucow import HucowMixin

# New systems
from ..brothel import WhoreMixin
from ..corruption import TransformationMixin
from ..pony import PonyMixin
from ..monsters import MonsterBreedingMixin
from ..inflation import InflationMixin
from ..arena import CombatMixin
from ..modifications import BodyModificationMixin
from ..breaking import BreakingMixin
from ..public_use import PublicUseMixin
from ..state import CharacterStateMixin


# =============================================================================
# UNIFIED CHARACTER MIXINS
# =============================================================================

class PetSystemsBaseMixin(
    WalletMixin,
    RelationshipMixin,
    SubstanceAffectedMixin,
):
    """
    Base mixin for all characters.
    Provides: wallet, relationships, substance effects.
    """
    pass


class PetSystemsSubmissiveMixin(
    PetSystemsBaseMixin,
    PropertyMixin,
    TraineeMixin,
    GrappleMixin,
    BondageMixin,
    ServantMixin,
    SlaveMixin,
    TransformableMixin,
    TransformationMixin,
    BodyModificationMixin,
    BreakingMixin,
    PublicUseMixin,
    InflationMixin,
    CharacterStateMixin,
):
    """
    Full mixin for submissive/slave characters.
    Includes all systems that apply to owned/used characters.
    """
    pass


class PetSystemsDominantMixin(
    PetSystemsBaseMixin,
    OwnerMixin,
    SlaveOwnerMixin,
    RiderMixin,
):
    """
    Mixin for dominant/owner characters.
    Includes ownership and control systems.
    """
    pass


class PetSystemsPetMixin(
    PetSystemsSubmissiveMixin,
    PetStatsMixin,
    MountMixin,
):
    """
    Mixin for pet characters (feral pets).
    Includes pet stats and mountability.
    """
    pass


class PetSystemsHucowMixin(
    PetSystemsSubmissiveMixin,
    HucowMixin,
    ProducerMixin,
):
    """
    Mixin for hucow characters.
    Includes lactation and production.
    """
    pass


class PetSystemsPonyMixin(
    PetSystemsSubmissiveMixin,
    PonyMixin,
    MountMixin,
):
    """
    Mixin for pony play characters.
    Includes pony stats and cart pulling.
    """
    pass


class PetSystemsWhoreMixin(
    PetSystemsSubmissiveMixin,
    WhoreMixin,
):
    """
    Mixin for brothel workers.
    Includes whore stats and services.
    """
    pass


class PetSystemsFighterMixin(
    PetSystemsBaseMixin,
    CombatMixin,
):
    """
    Mixin for arena fighters.
    Can be combined with other mixins.
    """
    pass


class PetSystemsMonsterHostMixin(
    PetSystemsSubmissiveMixin,
    MonsterBreedingMixin,
):
    """
    Mixin for monster breeding hosts.
    Includes oviposition and parasitic infection.
    """
    pass


class PetSystemsFullMixin(
    PetSystemsBaseMixin,
    # Ownership (can own and be owned)
    OwnerMixin,
    PropertyMixin,
    SlaveOwnerMixin,
    SlaveMixin,
    # Pet systems
    PetStatsMixin,
    MountMixin,
    RiderMixin,
    # Training
    TraineeMixin,
    TransformableMixin,
    TransformationMixin,
    # Physical
    GrappleMixin,
    BondageMixin,
    BodyModificationMixin,
    BreakingMixin,
    # Service
    ServantMixin,
    ProducerMixin,
    # Specialized
    HucowMixin,
    PonyMixin,
    WhoreMixin,
    MonsterBreedingMixin,
    InflationMixin,
    PublicUseMixin,
    CombatMixin,
    CharacterStateMixin,
):
    """
    Full mixin with ALL systems.
    Use for player characters that might do anything.
    """
    pass


# =============================================================================
# CROSS-SYSTEM HOOKS
# =============================================================================

class SystemHooks:
    """
    Central hook system for cross-system events.
    Systems register callbacks, other systems trigger them.
    """
    
    _hooks: Dict[str, List[callable]] = {}
    
    @classmethod
    def register(cls, event_name: str, callback: callable):
        """Register a callback for an event."""
        if event_name not in cls._hooks:
            cls._hooks[event_name] = []
        cls._hooks[event_name].append(callback)
    
    @classmethod
    def trigger(cls, event_name: str, **kwargs) -> List[Any]:
        """Trigger all callbacks for an event."""
        results = []
        for callback in cls._hooks.get(event_name, []):
            try:
                result = callback(**kwargs)
                results.append(result)
            except Exception as e:
                results.append(f"Error: {e}")
        return results
    
    @classmethod
    def clear(cls, event_name: str = None):
        """Clear hooks."""
        if event_name:
            cls._hooks.pop(event_name, None)
        else:
            cls._hooks.clear()


# =============================================================================
# EVENT TYPES
# =============================================================================

class SystemEvent(Enum):
    """Events that can trigger cross-system effects."""
    
    # Sexual events
    ORGASM = "orgasm"
    CUM_RECEIVED = "cum_received"
    BREEDING_ATTEMPT = "breeding_attempt"
    CONCEPTION = "conception"
    
    # Physical events
    MILKING = "milking"
    INFLATION = "inflation"
    DEFLATION = "deflation"
    PAIN_RECEIVED = "pain_received"
    
    # Mental events
    BREAKING_SESSION = "breaking_session"
    RESISTANCE_BROKEN = "resistance_broken"
    TRIGGER_ACTIVATED = "trigger_activated"
    
    # Service events
    SERVICE_COMPLETE = "service_complete"
    CLIENT_SATISFIED = "client_satisfied"
    SHIFT_END = "shift_end"
    
    # Transformation events
    TRANSFORMATION_PROGRESS = "transformation_progress"
    TRANSFORMATION_STAGE = "transformation_stage"
    TRANSFORMATION_COMPLETE = "transformation_complete"
    
    # Combat events
    FIGHT_START = "fight_start"
    FIGHT_END = "fight_end"
    DEFEAT = "defeat"
    VICTORY = "victory"
    
    # Economy events
    SOLD = "sold"
    PURCHASED = "purchased"
    EARNINGS = "earnings"
    
    # Time events
    TICK = "tick"
    HOUR_PASSED = "hour_passed"
    DAY_PASSED = "day_passed"


# =============================================================================
# DEFAULT HOOK IMPLEMENTATIONS
# =============================================================================

def on_cum_received(character, amount_ml: int, source: str, location: str) -> str:
    """
    Handle cum received - update inflation, arousal, breeding chance.
    """
    messages = []
    
    # Inflation
    if hasattr(character, 'inflation'):
        tracker = character.inflation
        msg = tracker.inflate(location, "cum", amount_ml)
        character.inflation = tracker
        messages.append(msg)
    
    # Arousal
    if hasattr(character, 'character_state'):
        state = character.character_state
        arousal_gain = min(20, amount_ml // 10)
        state.sexual.increase_arousal(arousal_gain)
        character.character_state = state
    
    # Breeding check (if in womb)
    if location == "womb" and hasattr(character, 'fertility'):
        # Would check fertility and trigger conception
        pass
    
    # Corruption (if demonic source)
    if "demon" in source.lower() and hasattr(character, 'transformations'):
        mgr = character.transformations
        mgr.apply_corruption("demon", amount_ml // 10)
        character.transformations = mgr
        messages.append("Demonic essence seeps in...")
    
    return " | ".join(messages) if messages else "Cum received."


def on_orgasm(character, forced: bool = False) -> str:
    """
    Handle orgasm - update stats, check triggers.
    """
    messages = []
    
    # Update sexual state
    if hasattr(character, 'character_state'):
        state = character.character_state
        state.sexual.orgasm(forced=forced)
        character.character_state = state
        messages.append("Orgasm!")
    
    # Check conditioned triggers
    if hasattr(character, 'mental_status'):
        mental = character.mental_status
        # Orgasm might be a trained response
        if forced:
            mental.obedience += 1
        character.mental_status = mental
    
    # Lactation letdown
    if hasattr(character, 'hucow_stats'):
        stats = character.hucow_stats
        if stats.is_lactating:
            messages.append("Milk spurts from nipples!")
    
    return " | ".join(messages)


def on_milking(character, amount_ml: int) -> str:
    """
    Handle milking complete - update stats, earnings.
    """
    messages = []
    
    # Update hucow stats
    if hasattr(character, 'hucow_stats'):
        stats = character.hucow_stats
        stats.milk_produced_today += amount_ml
        stats.milk_produced_total += amount_ml
        character.hucow_stats = stats
        messages.append(f"Produced {amount_ml}ml")
    
    # Update physical state
    if hasattr(character, 'character_state'):
        state = character.character_state
        state.physical.breast_fullness = max(0, state.physical.breast_fullness - 50)
        state.physical.milk_pressure = 0
        character.character_state = state
    
    # Arousal from milking
    if hasattr(character, 'character_state'):
        state = character.character_state
        state.sexual.increase_arousal(15)
        character.character_state = state
    
    return " | ".join(messages)


def on_defeat(character, victor) -> str:
    """
    Handle defeat in combat - apply consequences.
    """
    messages = []
    
    # Update combat stats
    if hasattr(character, 'combat_stats'):
        stats = character.combat_stats
        stats.losses += 1
        stats.current_streak = 0
        character.combat_stats = stats
    
    # Apply consequence based on arena rules
    # This would be determined by the fight/arena
    messages.append(f"Defeated by {victor.key if hasattr(victor, 'key') else victor}!")
    
    return " | ".join(messages)


# Register default hooks
SystemHooks.register(SystemEvent.CUM_RECEIVED.value, on_cum_received)
SystemHooks.register(SystemEvent.ORGASM.value, on_orgasm)
SystemHooks.register(SystemEvent.MILKING.value, on_milking)
SystemHooks.register(SystemEvent.DEFEAT.value, on_defeat)


# =============================================================================
# TIME TICK HANDLER
# =============================================================================

def process_time_tick(character, hours: float = 1.0) -> List[str]:
    """
    Process time passing for all systems on a character.
    Call this periodically (e.g., every game hour).
    """
    messages = []
    
    # Physical needs
    if hasattr(character, 'character_state'):
        state = character.character_state
        need_msgs = state.update_all(hours)
        messages.extend(need_msgs)
        character.character_state = state
    
    # Inflation processing (leakage, absorption)
    if hasattr(character, 'inflation'):
        tracker = character.inflation
        inflation_msgs = tracker.process_time(hours)
        messages.extend(inflation_msgs)
        character.inflation = tracker
    
    # Lactation buildup
    if hasattr(character, 'hucow_stats'):
        stats = character.hucow_stats
        if stats.is_lactating:
            buildup = int(stats.production_rate_ml_hour * hours)
            # Would update breast fullness
            if buildup > 50:
                messages.append("Breasts growing fuller...")
    
    # Arousal decay (if not denied)
    if hasattr(character, 'character_state'):
        state = character.character_state
        if not state.sexual.denied:
            decay = int(2 * hours)
            state.sexual.arousal = max(0, state.sexual.arousal - decay)
        character.character_state = state
    
    # Transformation progress
    if hasattr(character, 'transformations'):
        mgr = character.transformations
        # Ongoing transformations might progress
        for trans_type, trans in mgr.transformations.items():
            if trans.progress > 0 and trans.progress < 100:
                # Passive progression
                pass
    
    # Heat cycle
    if hasattr(character, 'fertility_mods'):
        mods = character.fertility_mods
        # Would update heat cycle
        pass
    
    # Trigger hooks
    SystemHooks.trigger(SystemEvent.TICK.value, character=character, hours=hours)
    
    if hours >= 1.0:
        SystemHooks.trigger(SystemEvent.HOUR_PASSED.value, character=character)
    
    return messages


# =============================================================================
# CONVENIENCE FUNCTIONS
# =============================================================================

def get_character_summary(character) -> str:
    """Get a comprehensive summary of all systems on a character."""
    lines = [f"=== {character.key} - Full Status ==="]
    
    # Core identity
    if hasattr(character, 'character_state'):
        state = character.character_state
        lines.append(f"Role: {state.current_role.value if state.current_role else 'Free'}")
        if state.owner_name:
            lines.append(f"Owner: {state.owner_name}")
    
    # Physical
    lines.append("\n--- Physical ---")
    if hasattr(character, 'character_state'):
        state = character.character_state
        lines.append(f"Health: {state.physical.health}/100")
        lines.append(f"Stamina: {state.physical.stamina}/100")
        lines.append(f"Condition: {state.physical.condition.value}")
    
    # Sexual
    lines.append("\n--- Sexual ---")
    if hasattr(character, 'character_state'):
        state = character.character_state
        lines.append(f"Arousal: {state.sexual.arousal}/100 [{state.sexual.state.value}]")
        if state.sexual.denied:
            lines.append(f"DENIED: {state.sexual.hours_denied} hours")
    
    # Mental (if broken)
    if hasattr(character, 'mental_status'):
        mental = character.mental_status
        if mental.resistance < 100:
            lines.append("\n--- Mental ---")
            lines.append(f"Resistance: {mental.resistance}/100 [{mental.resistance_level.value}]")
            lines.append(f"Obedience: {mental.obedience}/100")
    
    # Inflation
    if hasattr(character, 'inflation'):
        tracker = character.inflation
        total = tracker.get_total_volume()
        if total > 0:
            lines.append(f"\n--- Inflation ---")
            lines.append(f"Total: {total}ml")
            lines.append(tracker.get_appearance_description())
    
    # Transformations
    if hasattr(character, 'transformations'):
        mgr = character.transformations
        active = mgr.get_all_active()
        if active:
            lines.append("\n--- Transformations ---")
            for trans in active:
                lines.append(f"  {trans.transformation_type.value}: {trans.progress}%")
    
    # Specialized roles
    if hasattr(character, 'hucow_stats') and character.hucow_stats.is_registered:
        lines.append("\n--- Hucow ---")
        lines.append(f"Grade: {character.hucow_stats.grade}")
        lines.append(f"Milk Today: {character.hucow_stats.milk_produced_today}ml")
    
    if hasattr(character, 'pony_stats') and character.is_pony:
        lines.append("\n--- Pony ---")
        lines.append(f"Type: {character.pony_stats.pony_type.value}")
    
    if hasattr(character, 'whore_stats') and character.whore_stats.is_working:
        lines.append("\n--- Brothel ---")
        lines.append(f"Clients Today: {character.whore_stats.clients_today}")
    
    if hasattr(character, 'combat_stats') and character.is_fighter:
        lines.append("\n--- Fighter ---")
        stats = character.combat_stats
        lines.append(f"Record: {stats.wins}W-{stats.losses}L")
    
    # Economy
    if hasattr(character, 'wallet'):
        lines.append(f"\n--- Wallet ---")
        lines.append(f"Gold: {character.wallet.gold}g")
    
    return "\n".join(lines)


def initialize_character(character, role: str = "free") -> str:
    """
    Initialize all relevant systems on a character.
    Call when a character is first created or converted.
    """
    messages = []
    
    # Initialize character state
    if hasattr(character, 'character_state'):
        from ..state import CharacterState
        state = CharacterState(character_dbref=character.dbref, character_name=character.key)
        character.character_state = state
        messages.append("Character state initialized.")
    
    # Initialize inflation tracker
    if hasattr(character, 'inflation'):
        from ..inflation import InflationTracker
        tracker = InflationTracker(subject_dbref=character.dbref, subject_name=character.key)
        character.inflation = tracker
        messages.append("Inflation tracker initialized.")
    
    # Initialize wallet
    if hasattr(character, 'wallet'):
        from ..economy import Wallet
        wallet = Wallet()
        wallet.add_gold(100)  # Starting gold
        character.wallet = wallet
        messages.append("Wallet initialized with 100g.")
    
    # Initialize based on role
    role_initializers = {
        "hucow": _init_as_hucow,
        "pony": _init_as_pony,
        "slave": _init_as_slave,
        "whore": _init_as_whore,
        "fighter": _init_as_fighter,
        "pet": _init_as_pet,
    }
    
    initializer = role_initializers.get(role.lower())
    if initializer:
        role_msg = initializer(character)
        messages.append(role_msg)
    
    return " | ".join(messages)


def _init_as_hucow(character) -> str:
    """Initialize as hucow."""
    if hasattr(character, 'hucow_stats'):
        from ..hucow import HucowStats
        stats = HucowStats(
            cow_id=character.dbref,
            cow_name=character.key,
            is_registered=True,
            is_lactating=True,
        )
        character.hucow_stats = stats
    return "Registered as hucow."


def _init_as_pony(character) -> str:
    """Initialize as pony."""
    if hasattr(character, 'pony_stats'):
        from ..pony import PonyStats, PonyType
        stats = PonyStats(
            pony_id=character.dbref,
            pony_name=character.key,
            pony_type=PonyType.RIDING,
        )
        character.pony_stats = stats
    return "Registered as pony."


def _init_as_slave(character) -> str:
    """Initialize as slave."""
    if hasattr(character, 'slave_record'):
        from ..slavery import SlaveRecord
        record = SlaveRecord(
            slave_dbref=character.dbref,
            slave_name=character.key,
        )
        character.slave_record = record
    return "Registered as slave."


def _init_as_whore(character) -> str:
    """Initialize as brothel worker."""
    if hasattr(character, 'whore_stats'):
        from ..brothel import WhoreStats
        stats = WhoreStats(
            worker_dbref=character.dbref,
            worker_name=character.key,
        )
        character.whore_stats = stats
    return "Registered as brothel worker."


def _init_as_fighter(character) -> str:
    """Initialize as arena fighter."""
    if hasattr(character, 'combat_stats'):
        from ..arena import CombatStats
        stats = CombatStats(
            fighter_id=character.dbref,
            fighter_name=character.key,
        )
        character.combat_stats = stats
    return "Registered as arena fighter."


def _init_as_pet(character) -> str:
    """Initialize as pet."""
    if hasattr(character, 'pet_stats'):
        from ..pets import PetStats
        stats = PetStats(
            pet_id=character.dbref,
            pet_name=character.key,
        )
        character.pet_stats = stats
    return "Registered as pet."


# =============================================================================
# EXPORTS
# =============================================================================

__all__ = [
    # Unified mixins
    "PetSystemsBaseMixin",
    "PetSystemsSubmissiveMixin",
    "PetSystemsDominantMixin",
    "PetSystemsPetMixin",
    "PetSystemsHucowMixin",
    "PetSystemsPonyMixin",
    "PetSystemsWhoreMixin",
    "PetSystemsFighterMixin",
    "PetSystemsMonsterHostMixin",
    "PetSystemsFullMixin",
    
    # Hook system
    "SystemHooks",
    "SystemEvent",
    
    # Default hooks
    "on_cum_received",
    "on_orgasm",
    "on_milking",
    "on_defeat",
    
    # Time processing
    "process_time_tick",
    
    # Utilities
    "get_character_summary",
    "initialize_character",
]
