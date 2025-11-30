"""
Monster Breeding System
=======================

Monster and tentacle breeding including:
- Monster types (tentacle, slime, demon, plant)
- Oviposition and egg-laying
- Parasite infection
- Corruption spreading
- Hybrid offspring
"""

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any, Tuple
from enum import Enum
from datetime import datetime, timedelta
import random


# =============================================================================
# ENUMS
# =============================================================================

class MonsterType(Enum):
    """Types of breeding monsters."""
    TENTACLE_BEAST = "tentacle_beast"
    SLIME = "slime"
    DEMON = "demon"
    PLANT = "plant"
    WEREWOLF = "werewolf"
    DRAGON = "dragon"
    ORC = "orc"
    GOBLIN = "goblin"
    MINOTAUR = "minotaur"
    CENTAUR = "centaur"
    INSECTOID = "insectoid"
    ELDRITCH = "eldritch"


class BreedingMethod(Enum):
    """How monsters breed."""
    STANDARD = "standard"         # Normal penetration
    OVIPOSITION = "oviposition"   # Egg laying
    ABSORPTION = "absorption"     # Slime absorption
    PARASITIC = "parasitic"       # Parasites
    CORRUPTION = "corruption"     # Corrupting seed
    TENTACLE = "tentacle"         # Multiple tentacles
    KNOTTING = "knotting"         # Canine knotting


class EggType(Enum):
    """Types of eggs for oviposition."""
    INSECT = "insect"             # Small, numerous
    REPTILE = "reptile"           # Medium, leathery
    SLIME = "slime"               # Gel-like, dissolving
    PLANT = "plant"               # Seed pods
    DEMON = "demon"               # Corrupting eggs
    ELDRITCH = "eldritch"         # Reality-warping


class InfectionStage(Enum):
    """Stages of parasitic infection."""
    CLEAN = "clean"
    EXPOSED = "exposed"
    INFECTED = "infected"
    SPREADING = "spreading"
    ADVANCED = "advanced"
    CONTROLLED = "controlled"     # Host mind affected
    TRANSFORMED = "transformed"   # Fully converted


class HybridType(Enum):
    """Types of hybrid offspring."""
    HALF_DEMON = "half_demon"
    HALF_BEAST = "half_beast"
    SLIME_HYBRID = "slime_hybrid"
    PLANT_HYBRID = "plant_hybrid"
    TENTACLE_SPAWN = "tentacle_spawn"
    CORRUPTED = "corrupted"


# =============================================================================
# MONSTER STATS
# =============================================================================

@dataclass
class MonsterBreeder:
    """A monster that can breed."""
    
    monster_id: str = ""
    name: str = ""
    monster_type: MonsterType = MonsterType.TENTACLE_BEAST
    
    # Breeding stats
    virility: int = 70            # 0-100
    cum_volume_ml: int = 100
    breeding_method: BreedingMethod = BreedingMethod.STANDARD
    
    # For tentacle types
    tentacle_count: int = 0
    tentacle_length_cm: int = 0
    tentacle_thickness_cm: int = 0
    
    # For ovipositors
    has_ovipositor: bool = False
    egg_type: EggType = EggType.INSECT
    eggs_per_clutch: int = 0
    egg_size_cm: int = 0
    
    # For knotting types
    has_knot: bool = False
    knot_size_cm: int = 0
    
    # Corruption
    corruption_potency: int = 0   # 0-100
    corruption_type: str = ""
    
    # Parasite production
    produces_parasites: bool = False
    parasite_type: str = ""
    
    # Breeding history
    times_bred: int = 0
    offspring_produced: int = 0
    hosts_infected: int = 0
    
    def get_breeding_description(self) -> str:
        """Get description of breeding method."""
        descs = {
            MonsterType.TENTACLE_BEAST: f"Writhing mass with {self.tentacle_count} tentacles, each {self.tentacle_length_cm}cm long",
            MonsterType.SLIME: "Amorphous blob that absorbs and breeds through osmosis",
            MonsterType.DEMON: "Corrupting essence that taints with every thrust",
            MonsterType.PLANT: "Vines and tendrils that implant seeds deep within",
            MonsterType.WEREWOLF: f"Massive knotted cock ({self.knot_size_cm}cm knot) that ties during breeding",
            MonsterType.DRAGON: "Scaled member with ridges and massive cum production",
            MonsterType.INSECTOID: f"Ovipositor that lays clutches of {self.eggs_per_clutch} eggs",
        }
        return descs.get(self.monster_type, "Unknown breeding method")


# Monster presets
MONSTER_PRESETS = {
    "tentacle_beast": MonsterBreeder(
        monster_id="TENT-001",
        name="Tentacle Horror",
        monster_type=MonsterType.TENTACLE_BEAST,
        virility=80,
        cum_volume_ml=500,
        breeding_method=BreedingMethod.TENTACLE,
        tentacle_count=8,
        tentacle_length_cm=60,
        tentacle_thickness_cm=8,
        corruption_potency=30,
    ),
    "breeding_slime": MonsterBreeder(
        monster_id="SLIM-001",
        name="Breeding Slime",
        monster_type=MonsterType.SLIME,
        virility=90,
        cum_volume_ml=1000,
        breeding_method=BreedingMethod.ABSORPTION,
        corruption_potency=50,
        corruption_type="slime",
    ),
    "demon_lord": MonsterBreeder(
        monster_id="DEMO-001",
        name="Demon Lord",
        monster_type=MonsterType.DEMON,
        virility=95,
        cum_volume_ml=200,
        breeding_method=BreedingMethod.CORRUPTION,
        corruption_potency=80,
        corruption_type="demonic",
        has_knot=True,
        knot_size_cm=12,
    ),
    "plant_creature": MonsterBreeder(
        monster_id="PLNT-001",
        name="Breeding Vine",
        monster_type=MonsterType.PLANT,
        virility=70,
        cum_volume_ml=300,
        breeding_method=BreedingMethod.OVIPOSITION,
        has_ovipositor=True,
        egg_type=EggType.PLANT,
        eggs_per_clutch=20,
        egg_size_cm=3,
        tentacle_count=12,
        tentacle_length_cm=100,
    ),
    "insectoid": MonsterBreeder(
        monster_id="INSC-001",
        name="Insect Queen",
        monster_type=MonsterType.INSECTOID,
        virility=100,
        cum_volume_ml=50,
        breeding_method=BreedingMethod.OVIPOSITION,
        has_ovipositor=True,
        egg_type=EggType.INSECT,
        eggs_per_clutch=50,
        egg_size_cm=2,
        produces_parasites=True,
        parasite_type="breeding_larva",
    ),
    "werewolf_alpha": MonsterBreeder(
        monster_id="WOLF-001",
        name="Alpha Werewolf",
        monster_type=MonsterType.WEREWOLF,
        virility=85,
        cum_volume_ml=150,
        breeding_method=BreedingMethod.KNOTTING,
        has_knot=True,
        knot_size_cm=15,
    ),
    "eldritch_horror": MonsterBreeder(
        monster_id="ELDR-001",
        name="Eldritch Abomination",
        monster_type=MonsterType.ELDRITCH,
        virility=100,
        cum_volume_ml=2000,
        breeding_method=BreedingMethod.TENTACLE,
        tentacle_count=100,
        tentacle_length_cm=200,
        tentacle_thickness_cm=20,
        has_ovipositor=True,
        egg_type=EggType.ELDRITCH,
        eggs_per_clutch=10,
        egg_size_cm=10,
        corruption_potency=100,
        corruption_type="madness",
    ),
}


# =============================================================================
# OVIPOSITION
# =============================================================================

@dataclass
class EggClutch:
    """A clutch of eggs implanted in a host."""
    
    clutch_id: str = ""
    egg_type: EggType = EggType.INSECT
    
    # Source
    source_monster_id: str = ""
    source_monster_name: str = ""
    
    # Count
    egg_count: int = 10
    eggs_laid: int = 0            # Already expelled
    eggs_remaining: int = 10
    
    # Size
    egg_size_cm: int = 2
    
    # Location
    implant_location: str = "womb"
    
    # Development
    development_hours: int = 24
    hours_since_implant: float = 0
    development_percent: float = 0
    
    # Status
    is_hatched: bool = False
    is_expelled: bool = False
    
    def advance_time(self, hours: float) -> Tuple[str, bool]:
        """
        Advance egg development.
        Returns (message, hatching_event).
        """
        self.hours_since_implant += hours
        self.development_percent = min(100, (self.hours_since_implant / self.development_hours) * 100)
        
        messages = []
        hatching = False
        
        if self.development_percent >= 100 and not self.is_hatched:
            self.is_hatched = True
            hatching = True
            messages.append(f"The eggs begin to hatch inside!")
        elif self.development_percent >= 75:
            messages.append("Eggs squirming and shifting inside...")
        elif self.development_percent >= 50:
            messages.append("Belly distended with developing eggs.")
        elif self.development_percent >= 25:
            messages.append("Can feel eggs growing inside.")
        
        return "\n".join(messages) if messages else "", hatching
    
    def expel_eggs(self, count: int = 0) -> Tuple[int, str]:
        """
        Expel eggs from body.
        Returns (eggs_expelled, message).
        """
        if count == 0:
            count = self.eggs_remaining
        
        expelled = min(count, self.eggs_remaining)
        self.eggs_laid += expelled
        self.eggs_remaining -= expelled
        
        if self.eggs_remaining <= 0:
            self.is_expelled = True
        
        return expelled, f"Expels {expelled} eggs with a gush!"
    
    def get_status(self) -> str:
        """Get egg status."""
        lines = [f"=== Egg Clutch: {self.egg_type.value} ==="]
        lines.append(f"Source: {self.source_monster_name}")
        lines.append(f"Count: {self.eggs_remaining}/{self.egg_count} remaining")
        lines.append(f"Size: {self.egg_size_cm}cm each")
        lines.append(f"Development: {self.development_percent:.0f}%")
        lines.append(f"Location: {self.implant_location}")
        
        if self.is_hatched:
            lines.append("STATUS: HATCHED")
        
        return "\n".join(lines)


@dataclass
class OvipositionRecord:
    """Tracks oviposition for a host."""
    
    host_dbref: str = ""
    host_name: str = ""
    
    # Current clutches
    clutches: List[EggClutch] = field(default_factory=list)
    
    # Capacity
    max_eggs: int = 100           # How many eggs can hold
    current_eggs: int = 0
    
    # History
    total_clutches_received: int = 0
    total_eggs_received: int = 0
    total_eggs_laid: int = 0
    
    # Effects
    belly_distension: int = 0     # 0-100
    stretch_damage: int = 0       # Permanent stretching
    
    @property
    def is_full(self) -> bool:
        """Check if at egg capacity."""
        return self.current_eggs >= self.max_eggs
    
    def receive_clutch(self, clutch: EggClutch) -> Tuple[bool, str]:
        """Receive a new egg clutch."""
        if self.current_eggs + clutch.egg_count > self.max_eggs:
            # Partial deposit
            can_receive = self.max_eggs - self.current_eggs
            clutch.egg_count = can_receive
            clutch.eggs_remaining = can_receive
        
        if clutch.egg_count <= 0:
            return False, "Already full of eggs!"
        
        self.clutches.append(clutch)
        self.current_eggs += clutch.egg_count
        self.total_clutches_received += 1
        self.total_eggs_received += clutch.egg_count
        
        # Update distension
        self.belly_distension = min(100, int((self.current_eggs / self.max_eggs) * 100))
        
        return True, f"Implanted with {clutch.egg_count} {clutch.egg_type.value} eggs!"
    
    def update(self, hours: float) -> List[str]:
        """Update all clutches. Returns messages."""
        messages = []
        
        for clutch in self.clutches:
            msg, hatching = clutch.advance_time(hours)
            if msg:
                messages.append(msg)
        
        return messages
    
    def lay_eggs(self) -> Tuple[int, str]:
        """Attempt to lay eggs."""
        total_laid = 0
        messages = []
        
        for clutch in self.clutches:
            if clutch.development_percent >= 100 or clutch.is_hatched:
                laid, msg = clutch.expel_eggs()
                total_laid += laid
                messages.append(msg)
        
        self.current_eggs = max(0, self.current_eggs - total_laid)
        self.total_eggs_laid += total_laid
        self.belly_distension = int((self.current_eggs / self.max_eggs) * 100)
        
        # Remove empty clutches
        self.clutches = [c for c in self.clutches if not c.is_expelled]
        
        return total_laid, "\n".join(messages) if messages else "Nothing to lay."
    
    def get_status(self) -> str:
        """Get oviposition status."""
        lines = [f"=== Oviposition Status: {self.host_name} ==="]
        lines.append(f"Current Eggs: {self.current_eggs}/{self.max_eggs}")
        lines.append(f"Belly Distension: {self.belly_distension}%")
        lines.append(f"Active Clutches: {len(self.clutches)}")
        
        for i, clutch in enumerate(self.clutches):
            lines.append(f"\n  Clutch {i+1}: {clutch.egg_type.value}")
            lines.append(f"    {clutch.eggs_remaining} eggs, {clutch.development_percent:.0f}% developed")
        
        lines.append(f"\n--- History ---")
        lines.append(f"Total Clutches: {self.total_clutches_received}")
        lines.append(f"Total Eggs Received: {self.total_eggs_received}")
        lines.append(f"Total Eggs Laid: {self.total_eggs_laid}")
        
        return "\n".join(lines)


# =============================================================================
# PARASITIC INFECTION
# =============================================================================

@dataclass
class ParasiticInfection:
    """Tracks parasitic infection."""
    
    host_dbref: str = ""
    host_name: str = ""
    
    # Source
    source_monster_id: str = ""
    parasite_type: str = ""
    
    # Stage
    stage: InfectionStage = InfectionStage.CLEAN
    infection_percent: int = 0    # 0-100
    
    # Progression
    hours_infected: float = 0
    spread_rate: float = 1.0      # Multiplier
    
    # Effects
    host_arousal_mod: int = 0     # Added to arousal
    host_obedience_mod: int = 0   # Added to obedience
    host_sensitivity_mod: int = 0
    
    # Mind effects
    alien_thoughts: int = 0       # 0-100
    breeding_urge: int = 0        # 0-100
    hive_connection: int = 0      # 0-100
    
    # Physical changes
    visible_changes: List[str] = field(default_factory=list)
    
    def progress_infection(self, hours: float) -> Tuple[str, bool]:
        """
        Progress the infection.
        Returns (message, stage_changed).
        """
        if self.stage == InfectionStage.CLEAN:
            return "", False
        
        self.hours_infected += hours
        
        # Calculate progression
        base_progress = hours * 2 * self.spread_rate
        self.infection_percent = min(100, self.infection_percent + int(base_progress))
        
        old_stage = self.stage
        self._update_stage()
        
        stage_changed = old_stage != self.stage
        
        # Apply effects based on stage
        self._apply_stage_effects()
        
        return self._get_progression_message(), stage_changed
    
    def _update_stage(self) -> None:
        """Update infection stage."""
        if self.infection_percent >= 100:
            self.stage = InfectionStage.TRANSFORMED
        elif self.infection_percent >= 80:
            self.stage = InfectionStage.CONTROLLED
        elif self.infection_percent >= 60:
            self.stage = InfectionStage.ADVANCED
        elif self.infection_percent >= 40:
            self.stage = InfectionStage.SPREADING
        elif self.infection_percent >= 20:
            self.stage = InfectionStage.INFECTED
        elif self.infection_percent > 0:
            self.stage = InfectionStage.EXPOSED
    
    def _apply_stage_effects(self) -> None:
        """Apply effects based on stage."""
        if self.stage == InfectionStage.EXPOSED:
            self.host_arousal_mod = 10
            self.breeding_urge = 10
            
        elif self.stage == InfectionStage.INFECTED:
            self.host_arousal_mod = 25
            self.host_sensitivity_mod = 20
            self.breeding_urge = 30
            self.alien_thoughts = 15
            self.visible_changes = ["Slightly flushed skin"]
            
        elif self.stage == InfectionStage.SPREADING:
            self.host_arousal_mod = 50
            self.host_sensitivity_mod = 40
            self.host_obedience_mod = 20
            self.breeding_urge = 50
            self.alien_thoughts = 35
            self.visible_changes = ["Flushed skin", "Eyes occasionally glaze"]
            
        elif self.stage == InfectionStage.ADVANCED:
            self.host_arousal_mod = 75
            self.host_sensitivity_mod = 60
            self.host_obedience_mod = 50
            self.breeding_urge = 75
            self.alien_thoughts = 60
            self.hive_connection = 30
            self.visible_changes = ["Skin slightly discolored", "Visible veins", "Constant arousal"]
            
        elif self.stage == InfectionStage.CONTROLLED:
            self.host_arousal_mod = 90
            self.host_sensitivity_mod = 80
            self.host_obedience_mod = 80
            self.breeding_urge = 90
            self.alien_thoughts = 80
            self.hive_connection = 60
            self.visible_changes = ["Skin discoloration", "Eyes changed", "Compulsive breeding"]
            
        elif self.stage == InfectionStage.TRANSFORMED:
            self.host_arousal_mod = 100
            self.host_sensitivity_mod = 100
            self.host_obedience_mod = 100
            self.breeding_urge = 100
            self.alien_thoughts = 100
            self.hive_connection = 100
            self.visible_changes = ["Fully transformed", "Now part of the hive", "Exists to breed"]
    
    def _get_progression_message(self) -> str:
        """Get progression message."""
        msgs = {
            InfectionStage.EXPOSED: "Strange tingling sensation...",
            InfectionStage.INFECTED: "Body feels hot. Strange urges emerging.",
            InfectionStage.SPREADING: "Can't stop thinking about breeding. It's spreading.",
            InfectionStage.ADVANCED: "Thoughts becoming... not entirely your own.",
            InfectionStage.CONTROLLED: "The hive whispers. Must obey. Must breed.",
            InfectionStage.TRANSFORMED: "One with the hive. Purpose clear. Breed. Spread. Serve.",
        }
        return msgs.get(self.stage, "")
    
    def attempt_cure(self, cure_power: int) -> Tuple[bool, str]:
        """Attempt to cure infection."""
        if self.stage in [InfectionStage.CONTROLLED, InfectionStage.TRANSFORMED]:
            return False, "Too far gone to cure."
        
        reduction = cure_power - (self.infection_percent // 2)
        if reduction > 0:
            self.infection_percent = max(0, self.infection_percent - reduction)
            self._update_stage()
            
            if self.infection_percent == 0:
                self.stage = InfectionStage.CLEAN
                return True, "Infection purged!"
            
            return True, f"Infection reduced to {self.infection_percent}%"
        
        return False, "Cure too weak."
    
    def get_status(self) -> str:
        """Get infection status."""
        lines = [f"=== Parasitic Infection: {self.host_name} ==="]
        lines.append(f"Type: {self.parasite_type}")
        lines.append(f"Stage: {self.stage.value.upper()}")
        lines.append(f"Progress: {self.infection_percent}%")
        
        lines.append(f"\n--- Effects ---")
        lines.append(f"Arousal Mod: +{self.host_arousal_mod}")
        lines.append(f"Sensitivity Mod: +{self.host_sensitivity_mod}")
        lines.append(f"Breeding Urge: {self.breeding_urge}/100")
        lines.append(f"Alien Thoughts: {self.alien_thoughts}/100")
        
        if self.hive_connection:
            lines.append(f"Hive Connection: {self.hive_connection}/100")
        
        if self.visible_changes:
            lines.append(f"\n--- Visible Changes ---")
            for change in self.visible_changes:
                lines.append(f"  • {change}")
        
        return "\n".join(lines)


# =============================================================================
# MONSTER BREEDING SESSION
# =============================================================================

@dataclass
class MonsterBreedingSession:
    """A monster breeding session."""
    
    session_id: str = ""
    
    # Participants
    monster: Optional[MonsterBreeder] = None
    host_dbref: str = ""
    host_name: str = ""
    
    # Method
    breeding_method: BreedingMethod = BreedingMethod.STANDARD
    
    # Intensity
    intensity: int = 50           # 0-100
    duration_minutes: int = 30
    
    # Results
    cum_deposited_ml: int = 0
    eggs_implanted: int = 0
    corruption_applied: int = 0
    parasites_implanted: bool = False
    
    # Orgasms
    host_orgasms: int = 0
    
    # Generated description
    description: str = ""
    
    def generate_breeding(self) -> str:
        """Generate the breeding scene."""
        if not self.monster:
            return "No monster."
        
        parts = []
        
        # Intro based on monster type
        intros = {
            MonsterType.TENTACLE_BEAST: f"Tentacles writhe and coil, wrapping around limbs before finding eager holes.",
            MonsterType.SLIME: f"The slime engulfs, warm gel pressing into every opening.",
            MonsterType.DEMON: f"Demonic presence overwhelms, corrupting touch spreading fire.",
            MonsterType.PLANT: f"Vines snake forward, finding purchase in warm flesh.",
            MonsterType.WEREWOLF: f"The beast mounts, massive knotted cock demanding entry.",
            MonsterType.INSECTOID: f"Chitinous limbs pin down as the ovipositor extends.",
            MonsterType.ELDRITCH: f"Reality warps as impossible appendages claim their prize.",
        }
        parts.append(intros.get(self.monster.monster_type, "The monster approaches."))
        
        # Breeding method specific
        if self.monster.breeding_method == BreedingMethod.TENTACLE:
            parts.append(f"{self.monster.tentacle_count} tentacles probe and fill every hole simultaneously.")
            parts.append("Stretched beyond belief, stuffed completely full.")
            
        elif self.monster.breeding_method == BreedingMethod.OVIPOSITION:
            parts.append("The ovipositor pushes deep, seeking the womb.")
            parts.append(f"Eggs begin flowing in - {self.monster.eggs_per_clutch} of them, each {self.monster.egg_size_cm}cm.")
            self.eggs_implanted = self.monster.eggs_per_clutch
            
        elif self.monster.breeding_method == BreedingMethod.ABSORPTION:
            parts.append("Absorbed into the slime, every inch of skin stimulated.")
            parts.append("Gel probes internally, filling completely.")
            
        elif self.monster.breeding_method == BreedingMethod.KNOTTING:
            parts.append("Thrust deep, feeling the knot swell at the base.")
            parts.append(f"The {self.monster.knot_size_cm}cm knot pops inside, locking them together.")
            
        elif self.monster.breeding_method == BreedingMethod.CORRUPTION:
            parts.append("Each thrust spreads corruption deeper.")
            parts.append("Can feel the taint seeping into flesh and soul.")
            self.corruption_applied = self.monster.corruption_potency
        
        # Climax
        parts.append(f"\n{self.monster.cum_volume_ml}ml of seed floods inside.")
        self.cum_deposited_ml = self.monster.cum_volume_ml
        
        # Effects
        if self.monster.corruption_potency > 0:
            parts.append(f"Corruption seeps in with every drop.")
        
        if self.monster.produces_parasites:
            parts.append("Something else was deposited... parasites taking hold.")
            self.parasites_implanted = True
        
        # Orgasms based on intensity
        self.host_orgasms = max(1, self.intensity // 20)
        parts.append(f"\nForced through {self.host_orgasms} screaming orgasm{'s' if self.host_orgasms > 1 else ''}.")
        
        self.description = "\n\n".join(parts)
        return self.description
    
    def get_summary(self) -> str:
        """Get session summary."""
        lines = [f"=== Monster Breeding Session ==="]
        lines.append(f"Monster: {self.monster.name if self.monster else 'Unknown'}")
        lines.append(f"Method: {self.breeding_method.value}")
        lines.append(f"Duration: {self.duration_minutes} minutes")
        lines.append(f"Intensity: {self.intensity}/100")
        
        lines.append(f"\n--- Results ---")
        lines.append(f"Cum: {self.cum_deposited_ml}ml")
        if self.eggs_implanted:
            lines.append(f"Eggs: {self.eggs_implanted}")
        if self.corruption_applied:
            lines.append(f"Corruption: {self.corruption_applied}")
        if self.parasites_implanted:
            lines.append("PARASITES IMPLANTED")
        lines.append(f"Orgasms: {self.host_orgasms}")
        
        return "\n".join(lines)


# =============================================================================
# HYBRID OFFSPRING
# =============================================================================

@dataclass
class HybridOffspring:
    """A hybrid offspring from monster breeding."""
    
    offspring_id: str = ""
    name: str = ""
    hybrid_type: HybridType = HybridType.CORRUPTED
    
    # Parents
    mother_dbref: str = ""
    mother_name: str = ""
    monster_parent: str = ""
    monster_type: MonsterType = MonsterType.DEMON
    
    # Birth
    birth_date: Optional[datetime] = None
    gestation_days: int = 30
    
    # Traits
    human_traits: int = 50        # 0-100 human appearance
    monster_traits: int = 50      # 0-100 monster traits
    
    # Abilities
    abilities: List[str] = field(default_factory=list)
    
    # For breeding hybrids
    is_fertile: bool = True
    can_breed_humans: bool = True
    can_breed_monsters: bool = True


def determine_hybrid_type(monster: MonsterBreeder) -> HybridType:
    """Determine what type of hybrid would result."""
    type_map = {
        MonsterType.DEMON: HybridType.HALF_DEMON,
        MonsterType.SLIME: HybridType.SLIME_HYBRID,
        MonsterType.PLANT: HybridType.PLANT_HYBRID,
        MonsterType.TENTACLE_BEAST: HybridType.TENTACLE_SPAWN,
        MonsterType.WEREWOLF: HybridType.HALF_BEAST,
        MonsterType.DRAGON: HybridType.HALF_BEAST,
    }
    return type_map.get(monster.monster_type, HybridType.CORRUPTED)


# =============================================================================
# MONSTER BREEDING MIXIN
# =============================================================================

class MonsterBreedingMixin:
    """Mixin for hosts of monster breeding."""
    
    @property
    def oviposition(self) -> OvipositionRecord:
        """Get oviposition record."""
        data = self.db.oviposition
        if data:
            record = OvipositionRecord()
            record.host_dbref = data.get("host_dbref", self.dbref)
            record.host_name = data.get("host_name", self.key)
            record.current_eggs = data.get("current_eggs", 0)
            record.total_eggs_received = data.get("total_eggs_received", 0)
            record.total_eggs_laid = data.get("total_eggs_laid", 0)
            record.belly_distension = data.get("belly_distension", 0)
            return record
        return OvipositionRecord(host_dbref=self.dbref, host_name=self.key)
    
    @property
    def parasitic_infection(self) -> ParasiticInfection:
        """Get parasitic infection."""
        data = self.db.parasitic_infection
        if data:
            infection = ParasiticInfection()
            infection.host_dbref = data.get("host_dbref", self.dbref)
            infection.host_name = data.get("host_name", self.key)
            infection.stage = InfectionStage(data.get("stage", "clean"))
            infection.infection_percent = data.get("infection_percent", 0)
            infection.parasite_type = data.get("parasite_type", "")
            return infection
        return ParasiticInfection(host_dbref=self.dbref, host_name=self.key)


__all__ = [
    "MonsterType",
    "BreedingMethod",
    "EggType",
    "InfectionStage",
    "HybridType",
    "MonsterBreeder",
    "MONSTER_PRESETS",
    "EggClutch",
    "OvipositionRecord",
    "ParasiticInfection",
    "MonsterBreedingSession",
    "HybridOffspring",
    "determine_hybrid_type",
    "MonsterBreedingMixin",
    "MonsterCmdSet",
]

# Import commands
from .commands import MonsterCmdSet
