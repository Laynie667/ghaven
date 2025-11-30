"""
Feral Offspring System
======================

Handles feral breeding results:
- Conception and gestation tracking
- Litter generation
- Trait inheritance from parents
- Offspring management
"""

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any, Tuple
from enum import Enum
from datetime import datetime, timedelta
import random
import uuid


# =============================================================================
# ENUMS
# =============================================================================

class GestationStage(Enum):
    """Stages of gestation."""
    CONCEPTION = "conception"    # Just conceived
    EARLY = "early"              # Early pregnancy
    MIDDLE = "middle"            # Visible pregnancy
    LATE = "late"                # Very pregnant
    IMMINENT = "imminent"        # About to give birth
    BORN = "born"                # Already delivered


class OffspringStage(Enum):
    """Life stages for offspring."""
    NEWBORN = "newborn"          # Just born
    NURSING = "nursing"          # Still nursing
    WEANING = "weaning"          # Transitioning to solid food
    JUVENILE = "juvenile"        # Young but independent
    ADOLESCENT = "adolescent"    # Nearly adult
    ADULT = "adult"              # Fully grown


# =============================================================================
# SPECIES BREEDING DATA
# =============================================================================

SPECIES_BREEDING_DATA = {
    # Canines
    "wolf": {
        "gestation_days": 63,
        "litter_min": 4,
        "litter_max": 6,
        "has_knot": True,
        "heat_cycle_days": 180,
        "nursing_days": 56,
        "maturity_days": 365,
    },
    "dog": {
        "gestation_days": 63,
        "litter_min": 4,
        "litter_max": 8,
        "has_knot": True,
        "heat_cycle_days": 180,
        "nursing_days": 49,
        "maturity_days": 365,
    },
    "fox": {
        "gestation_days": 52,
        "litter_min": 3,
        "litter_max": 6,
        "has_knot": True,
        "heat_cycle_days": 365,
        "nursing_days": 42,
        "maturity_days": 300,
    },
    "hyena": {
        "gestation_days": 110,
        "litter_min": 1,
        "litter_max": 3,
        "has_knot": True,
        "heat_cycle_days": 14,
        "nursing_days": 365,
        "maturity_days": 730,
    },
    
    # Felines
    "cat": {
        "gestation_days": 65,
        "litter_min": 3,
        "litter_max": 5,
        "has_knot": False,
        "has_barbs": True,
        "heat_cycle_days": 21,
        "nursing_days": 56,
        "maturity_days": 365,
    },
    "lion": {
        "gestation_days": 110,
        "litter_min": 2,
        "litter_max": 4,
        "has_knot": False,
        "has_barbs": True,
        "heat_cycle_days": 21,
        "nursing_days": 180,
        "maturity_days": 1095,
    },
    "tiger": {
        "gestation_days": 103,
        "litter_min": 2,
        "litter_max": 4,
        "has_knot": False,
        "has_barbs": True,
        "heat_cycle_days": 21,
        "nursing_days": 180,
        "maturity_days": 1095,
    },
    
    # Equines
    "horse": {
        "gestation_days": 340,
        "litter_min": 1,
        "litter_max": 1,
        "has_knot": False,
        "has_flare": True,
        "heat_cycle_days": 21,
        "nursing_days": 180,
        "maturity_days": 1460,
    },
    "pony": {
        "gestation_days": 320,
        "litter_min": 1,
        "litter_max": 1,
        "has_knot": False,
        "has_flare": True,
        "heat_cycle_days": 21,
        "nursing_days": 150,
        "maturity_days": 1095,
    },
    "donkey": {
        "gestation_days": 365,
        "litter_min": 1,
        "litter_max": 1,
        "has_knot": False,
        "has_flare": True,
        "heat_cycle_days": 24,
        "nursing_days": 180,
        "maturity_days": 1095,
    },
    
    # Livestock
    "cow": {
        "gestation_days": 283,
        "litter_min": 1,
        "litter_max": 1,
        "has_knot": False,
        "heat_cycle_days": 21,
        "nursing_days": 240,
        "maturity_days": 730,
    },
    "pig": {
        "gestation_days": 114,
        "litter_min": 8,
        "litter_max": 12,
        "has_knot": False,
        "has_corkscrew": True,
        "heat_cycle_days": 21,
        "nursing_days": 56,
        "maturity_days": 365,
    },
    "goat": {
        "gestation_days": 150,
        "litter_min": 1,
        "litter_max": 3,
        "has_knot": False,
        "heat_cycle_days": 21,
        "nursing_days": 90,
        "maturity_days": 365,
    },
    "sheep": {
        "gestation_days": 147,
        "litter_min": 1,
        "litter_max": 2,
        "has_knot": False,
        "heat_cycle_days": 17,
        "nursing_days": 90,
        "maturity_days": 365,
    },
    
    # Default for unknown species
    "default": {
        "gestation_days": 90,
        "litter_min": 2,
        "litter_max": 4,
        "has_knot": False,
        "heat_cycle_days": 30,
        "nursing_days": 60,
        "maturity_days": 365,
    },
}


def get_species_breeding_data(species: str) -> dict:
    """Get breeding data for a species."""
    return SPECIES_BREEDING_DATA.get(species.lower(), SPECIES_BREEDING_DATA["default"])


# =============================================================================
# INHERITABLE TRAITS
# =============================================================================

@dataclass
class InheritableTraits:
    """Traits that can be inherited from parents."""
    
    # Physical
    coat_color: str = ""
    coat_pattern: str = ""
    eye_color: str = ""
    size: str = "medium"      # tiny, small, medium, large, huge
    build: str = "average"    # slim, average, muscular, heavy
    
    # Genital traits (for breeding stock)
    genital_size: str = "average"  # small, average, large, huge
    fertility: int = 50            # 0-100
    virility: int = 50             # 0-100
    
    # Temperament
    dominance: int = 50
    aggression: int = 30
    trainability: int = 50
    
    # Special
    has_knot: bool = False
    knot_size: str = "average"
    
    def to_dict(self) -> dict:
        return {
            "coat_color": self.coat_color,
            "coat_pattern": self.coat_pattern,
            "eye_color": self.eye_color,
            "size": self.size,
            "build": self.build,
            "genital_size": self.genital_size,
            "fertility": self.fertility,
            "virility": self.virility,
            "dominance": self.dominance,
            "aggression": self.aggression,
            "trainability": self.trainability,
            "has_knot": self.has_knot,
            "knot_size": self.knot_size,
        }
    
    @classmethod
    def from_dict(cls, data: dict) -> "InheritableTraits":
        return cls(**{k: v for k, v in data.items() if k in cls.__dataclass_fields__})


# =============================================================================
# PREGNANCY
# =============================================================================

@dataclass
class Pregnancy:
    """Tracks a pregnancy."""
    pregnancy_id: str
    mother_dbref: str
    mother_name: str
    father_dbref: str
    father_name: str
    
    # Species
    mother_species: str
    father_species: str
    offspring_species: str  # Usually mother's species
    
    # Timing
    conceived_at: datetime = field(default_factory=datetime.now)
    due_date: Optional[datetime] = None
    born_at: Optional[datetime] = None
    
    # Stage
    stage: GestationStage = GestationStage.CONCEPTION
    
    # Offspring
    litter_size: int = 1
    offspring_ids: List[str] = field(default_factory=list)
    
    # Parent traits for inheritance
    mother_traits: Optional[InheritableTraits] = None
    father_traits: Optional[InheritableTraits] = None
    
    # Status
    is_active: bool = True
    complications: List[str] = field(default_factory=list)
    
    def __post_init__(self):
        """Initialize due date if not set."""
        if not self.due_date:
            breeding_data = get_species_breeding_data(self.offspring_species)
            gestation_days = breeding_data["gestation_days"]
            self.due_date = self.conceived_at + timedelta(days=gestation_days)
    
    def get_days_pregnant(self) -> int:
        """Get number of days pregnant."""
        return (datetime.now() - self.conceived_at).days
    
    def get_days_remaining(self) -> int:
        """Get days until due date."""
        if self.due_date:
            remaining = (self.due_date - datetime.now()).days
            return max(0, remaining)
        return 0
    
    def get_progress_percentage(self) -> float:
        """Get pregnancy progress as percentage."""
        breeding_data = get_species_breeding_data(self.offspring_species)
        total_days = breeding_data["gestation_days"]
        days_pregnant = self.get_days_pregnant()
        return min(100.0, (days_pregnant / total_days) * 100)
    
    def update_stage(self):
        """Update gestation stage based on progress."""
        if not self.is_active:
            return
        
        progress = self.get_progress_percentage()
        
        if progress >= 95:
            self.stage = GestationStage.IMMINENT
        elif progress >= 75:
            self.stage = GestationStage.LATE
        elif progress >= 40:
            self.stage = GestationStage.MIDDLE
        elif progress >= 10:
            self.stage = GestationStage.EARLY
        else:
            self.stage = GestationStage.CONCEPTION
    
    def get_belly_description(self) -> str:
        """Get description of pregnant belly."""
        stage_descs = {
            GestationStage.CONCEPTION: "",
            GestationStage.EARLY: "a slight swelling in the lower belly",
            GestationStage.MIDDLE: "a visibly rounded belly, clearly pregnant",
            GestationStage.LATE: "a heavily swollen belly, very pregnant",
            GestationStage.IMMINENT: "a massively distended belly, ready to burst",
        }
        return stage_descs.get(self.stage, "")
    
    def is_due(self) -> bool:
        """Check if pregnancy is at or past due date."""
        return datetime.now() >= self.due_date if self.due_date else False
    
    def to_dict(self) -> dict:
        return {
            "pregnancy_id": self.pregnancy_id,
            "mother_dbref": self.mother_dbref,
            "mother_name": self.mother_name,
            "father_dbref": self.father_dbref,
            "father_name": self.father_name,
            "mother_species": self.mother_species,
            "father_species": self.father_species,
            "offspring_species": self.offspring_species,
            "conceived_at": self.conceived_at.isoformat(),
            "due_date": self.due_date.isoformat() if self.due_date else None,
            "born_at": self.born_at.isoformat() if self.born_at else None,
            "stage": self.stage.value,
            "litter_size": self.litter_size,
            "offspring_ids": self.offspring_ids,
            "mother_traits": self.mother_traits.to_dict() if self.mother_traits else None,
            "father_traits": self.father_traits.to_dict() if self.father_traits else None,
            "is_active": self.is_active,
            "complications": self.complications,
        }
    
    @classmethod
    def from_dict(cls, data: dict) -> "Pregnancy":
        preg = cls(
            pregnancy_id=data["pregnancy_id"],
            mother_dbref=data["mother_dbref"],
            mother_name=data["mother_name"],
            father_dbref=data["father_dbref"],
            father_name=data["father_name"],
            mother_species=data["mother_species"],
            father_species=data["father_species"],
            offspring_species=data["offspring_species"],
        )
        
        preg.conceived_at = datetime.fromisoformat(data["conceived_at"])
        if data.get("due_date"):
            preg.due_date = datetime.fromisoformat(data["due_date"])
        if data.get("born_at"):
            preg.born_at = datetime.fromisoformat(data["born_at"])
        
        preg.stage = GestationStage(data.get("stage", "conception"))
        preg.litter_size = data.get("litter_size", 1)
        preg.offspring_ids = data.get("offspring_ids", [])
        
        if data.get("mother_traits"):
            preg.mother_traits = InheritableTraits.from_dict(data["mother_traits"])
        if data.get("father_traits"):
            preg.father_traits = InheritableTraits.from_dict(data["father_traits"])
        
        preg.is_active = data.get("is_active", True)
        preg.complications = data.get("complications", [])
        
        return preg


# =============================================================================
# OFFSPRING
# =============================================================================

@dataclass
class Offspring:
    """A born offspring."""
    offspring_id: str
    name: str
    
    # Parents
    mother_dbref: str
    mother_name: str
    father_dbref: str
    father_name: str
    pregnancy_id: str
    
    # Species/Type
    species: str
    sex: str  # "male" or "female"
    
    # Birth
    born_at: datetime = field(default_factory=datetime.now)
    birth_order: int = 1  # Position in litter
    litter_size: int = 1  # Total litter size
    
    # Stage
    stage: OffspringStage = OffspringStage.NEWBORN
    
    # Inherited traits
    traits: Optional[InheritableTraits] = None
    
    # Status
    is_alive: bool = True
    is_weaned: bool = False
    location_dbref: str = ""  # Where they are
    
    # If converted to NPC
    npc_dbref: str = ""
    
    def get_age_days(self) -> int:
        """Get age in days."""
        return (datetime.now() - self.born_at).days
    
    def update_stage(self):
        """Update life stage based on age."""
        breeding_data = get_species_breeding_data(self.species)
        nursing_days = breeding_data["nursing_days"]
        maturity_days = breeding_data["maturity_days"]
        
        age = self.get_age_days()
        
        if age >= maturity_days:
            self.stage = OffspringStage.ADULT
        elif age >= maturity_days * 0.7:
            self.stage = OffspringStage.ADOLESCENT
        elif age >= maturity_days * 0.3:
            self.stage = OffspringStage.JUVENILE
        elif age >= nursing_days:
            self.stage = OffspringStage.WEANING
            self.is_weaned = True
        elif age >= nursing_days * 0.5:
            self.stage = OffspringStage.NURSING
        else:
            self.stage = OffspringStage.NEWBORN
    
    def get_description(self) -> str:
        """Get description of offspring."""
        age_desc = {
            OffspringStage.NEWBORN: "a tiny newborn",
            OffspringStage.NURSING: "a small nursing",
            OffspringStage.WEANING: "a young",
            OffspringStage.JUVENILE: "a juvenile",
            OffspringStage.ADOLESCENT: "an adolescent",
            OffspringStage.ADULT: "an adult",
        }
        
        base = age_desc.get(self.stage, "a")
        
        traits_desc = ""
        if self.traits:
            if self.traits.coat_color:
                traits_desc = f" {self.traits.coat_color}"
        
        return f"{base}{traits_desc} {self.sex} {self.species}"
    
    def to_dict(self) -> dict:
        return {
            "offspring_id": self.offspring_id,
            "name": self.name,
            "mother_dbref": self.mother_dbref,
            "mother_name": self.mother_name,
            "father_dbref": self.father_dbref,
            "father_name": self.father_name,
            "pregnancy_id": self.pregnancy_id,
            "species": self.species,
            "sex": self.sex,
            "born_at": self.born_at.isoformat(),
            "birth_order": self.birth_order,
            "litter_size": self.litter_size,
            "stage": self.stage.value,
            "traits": self.traits.to_dict() if self.traits else None,
            "is_alive": self.is_alive,
            "is_weaned": self.is_weaned,
            "location_dbref": self.location_dbref,
            "npc_dbref": self.npc_dbref,
        }
    
    @classmethod
    def from_dict(cls, data: dict) -> "Offspring":
        off = cls(
            offspring_id=data["offspring_id"],
            name=data["name"],
            mother_dbref=data["mother_dbref"],
            mother_name=data["mother_name"],
            father_dbref=data["father_dbref"],
            father_name=data["father_name"],
            pregnancy_id=data["pregnancy_id"],
            species=data["species"],
            sex=data["sex"],
        )
        
        off.born_at = datetime.fromisoformat(data["born_at"])
        off.birth_order = data.get("birth_order", 1)
        off.litter_size = data.get("litter_size", 1)
        off.stage = OffspringStage(data.get("stage", "newborn"))
        
        if data.get("traits"):
            off.traits = InheritableTraits.from_dict(data["traits"])
        
        off.is_alive = data.get("is_alive", True)
        off.is_weaned = data.get("is_weaned", False)
        off.location_dbref = data.get("location_dbref", "")
        off.npc_dbref = data.get("npc_dbref", "")
        
        return off


# =============================================================================
# BREEDING SYSTEM
# =============================================================================

class BreedingSystem:
    """
    Handles breeding, conception, and birth.
    """
    
    @staticmethod
    def calculate_conception_chance(
        mother_fertility: int = 50,
        father_virility: int = 50,
        was_knotted: bool = False,
        mother_in_heat: bool = False,
        breeding_harness: bool = False,
    ) -> float:
        """
        Calculate chance of conception.
        
        Returns:
            Percentage chance (0-100)
        """
        # Base chance from fertility/virility
        base = (mother_fertility + father_virility) / 4  # 0-50
        
        # Heat bonus
        if mother_in_heat:
            base += 30
        
        # Knotting bonus
        if was_knotted:
            base += 20
        
        # Harness bonus
        if breeding_harness:
            base += 10
        
        return min(95, max(5, base))
    
    @staticmethod
    def attempt_conception(
        mother,
        father,
        was_knotted: bool = False,
        breeding_harness: bool = False,
    ) -> Tuple[bool, Optional[Pregnancy], str]:
        """
        Attempt to conceive.
        
        Returns:
            (conceived: bool, pregnancy: Optional[Pregnancy], message: str)
        """
        # Get species data
        mother_species = getattr(mother, 'species', 'default')
        father_species = getattr(father, 'species', 'default')
        
        # Get traits
        mother_fertility = getattr(mother, 'fertility', 50)
        father_virility = getattr(father, 'virility', 50)
        mother_in_heat = getattr(mother, 'in_heat', False)
        
        # Check existing pregnancy
        existing = getattr(mother, 'current_pregnancy', None)
        if existing:
            return False, None, f"{mother.key} is already pregnant."
        
        # Calculate chance
        chance = BreedingSystem.calculate_conception_chance(
            mother_fertility=mother_fertility,
            father_virility=father_virility,
            was_knotted=was_knotted,
            mother_in_heat=mother_in_heat,
            breeding_harness=breeding_harness,
        )
        
        # Roll
        roll = random.randint(1, 100)
        conceived = roll <= chance
        
        if not conceived:
            return False, None, f"Breeding did not result in conception ({chance:.0f}% chance)."
        
        # Create pregnancy
        pregnancy = BreedingSystem.create_pregnancy(mother, father)
        
        return True, pregnancy, f"{mother.key} has been impregnated! Due in {pregnancy.get_days_remaining()} days."
    
    @staticmethod
    def create_pregnancy(mother, father) -> Pregnancy:
        """Create a new pregnancy."""
        mother_species = getattr(mother, 'species', 'default')
        father_species = getattr(father, 'species', 'default')
        
        # Offspring species is usually mother's
        offspring_species = mother_species
        
        # Get breeding data
        breeding_data = get_species_breeding_data(offspring_species)
        
        # Determine litter size
        litter_min = breeding_data["litter_min"]
        litter_max = breeding_data["litter_max"]
        litter_size = random.randint(litter_min, litter_max)
        
        # Create pregnancy
        pregnancy = Pregnancy(
            pregnancy_id=f"preg_{uuid.uuid4().hex[:8]}",
            mother_dbref=mother.dbref,
            mother_name=mother.key,
            father_dbref=father.dbref,
            father_name=father.key,
            mother_species=mother_species,
            father_species=father_species,
            offspring_species=offspring_species,
            litter_size=litter_size,
        )
        
        # Extract parent traits if available
        if hasattr(mother, 'inheritable_traits'):
            pregnancy.mother_traits = mother.inheritable_traits
        if hasattr(father, 'inheritable_traits'):
            pregnancy.father_traits = father.inheritable_traits
        
        return pregnancy
    
    @staticmethod
    def inherit_trait(
        mother_value: Any,
        father_value: Any,
        mutation_chance: float = 0.1
    ) -> Any:
        """
        Determine inherited trait value.
        
        Args:
            mother_value: Mother's trait value
            father_value: Father's trait value
            mutation_chance: Chance of random mutation
            
        Returns:
            Inherited value
        """
        # Check for mutation
        if random.random() < mutation_chance:
            # Return a random variant
            if isinstance(mother_value, int):
                return random.randint(
                    max(0, min(mother_value, father_value) - 20),
                    min(100, max(mother_value, father_value) + 20)
                )
            elif isinstance(mother_value, str):
                # For strings, just pick one randomly
                return random.choice([mother_value, father_value])
        
        # Normal inheritance
        if isinstance(mother_value, int):
            # Average with some variance
            avg = (mother_value + father_value) // 2
            variance = random.randint(-10, 10)
            return max(0, min(100, avg + variance))
        elif isinstance(mother_value, bool):
            # Either parent
            return random.choice([mother_value, father_value])
        else:
            # Pick one
            return random.choice([mother_value, father_value])
    
    @staticmethod
    def generate_offspring_traits(pregnancy: Pregnancy) -> InheritableTraits:
        """Generate traits for an offspring based on parents."""
        traits = InheritableTraits()
        
        mother_traits = pregnancy.mother_traits or InheritableTraits()
        father_traits = pregnancy.father_traits or InheritableTraits()
        
        # Inherit each trait
        traits.coat_color = BreedingSystem.inherit_trait(
            mother_traits.coat_color, father_traits.coat_color
        )
        traits.coat_pattern = BreedingSystem.inherit_trait(
            mother_traits.coat_pattern, father_traits.coat_pattern
        )
        traits.eye_color = BreedingSystem.inherit_trait(
            mother_traits.eye_color, father_traits.eye_color
        )
        traits.size = BreedingSystem.inherit_trait(
            mother_traits.size, father_traits.size
        )
        traits.build = BreedingSystem.inherit_trait(
            mother_traits.build, father_traits.build
        )
        traits.genital_size = BreedingSystem.inherit_trait(
            mother_traits.genital_size, father_traits.genital_size
        )
        traits.fertility = BreedingSystem.inherit_trait(
            mother_traits.fertility, father_traits.fertility
        )
        traits.virility = BreedingSystem.inherit_trait(
            mother_traits.virility, father_traits.virility
        )
        traits.dominance = BreedingSystem.inherit_trait(
            mother_traits.dominance, father_traits.dominance
        )
        traits.aggression = BreedingSystem.inherit_trait(
            mother_traits.aggression, father_traits.aggression
        )
        traits.trainability = BreedingSystem.inherit_trait(
            mother_traits.trainability, father_traits.trainability
        )
        traits.has_knot = BreedingSystem.inherit_trait(
            mother_traits.has_knot, father_traits.has_knot
        )
        traits.knot_size = BreedingSystem.inherit_trait(
            mother_traits.knot_size, father_traits.knot_size
        )
        
        return traits
    
    @staticmethod
    def give_birth(pregnancy: Pregnancy) -> List[Offspring]:
        """
        Process birth, creating offspring.
        
        Returns:
            List of born offspring
        """
        offspring_list = []
        
        for i in range(pregnancy.litter_size):
            # Determine sex
            sex = random.choice(["male", "female"])
            
            # Generate traits
            traits = BreedingSystem.generate_offspring_traits(pregnancy)
            
            # Generate name
            name = f"Pup #{i+1}"  # Default, can be renamed
            
            offspring = Offspring(
                offspring_id=f"off_{uuid.uuid4().hex[:8]}",
                name=name,
                mother_dbref=pregnancy.mother_dbref,
                mother_name=pregnancy.mother_name,
                father_dbref=pregnancy.father_dbref,
                father_name=pregnancy.father_name,
                pregnancy_id=pregnancy.pregnancy_id,
                species=pregnancy.offspring_species,
                sex=sex,
                birth_order=i + 1,
                litter_size=pregnancy.litter_size,
                traits=traits,
            )
            
            offspring_list.append(offspring)
            pregnancy.offspring_ids.append(offspring.offspring_id)
        
        # Update pregnancy
        pregnancy.born_at = datetime.now()
        pregnancy.stage = GestationStage.BORN
        pregnancy.is_active = False
        
        return offspring_list
    
    @staticmethod
    def get_litter_description(offspring_list: List[Offspring]) -> str:
        """Get description of a litter."""
        if not offspring_list:
            return "no offspring"
        
        count = len(offspring_list)
        males = sum(1 for o in offspring_list if o.sex == "male")
        females = count - males
        
        species = offspring_list[0].species
        
        if count == 1:
            return f"a single {offspring_list[0].sex} {species}"
        else:
            parts = []
            if males:
                parts.append(f"{males} male{'s' if males > 1 else ''}")
            if females:
                parts.append(f"{females} female{'s' if females > 1 else ''}")
            
            return f"a litter of {count} {species}s ({' and '.join(parts)})"


# =============================================================================
# PREGNANCY MIXIN
# =============================================================================

class PregnancyMixin:
    """
    Mixin for characters/NPCs that can become pregnant.
    """
    
    @property
    def current_pregnancy(self) -> Optional[Pregnancy]:
        """Get current pregnancy if any."""
        data = self.attributes.get("current_pregnancy")
        if data:
            return Pregnancy.from_dict(data)
        return None
    
    @current_pregnancy.setter
    def current_pregnancy(self, pregnancy: Optional[Pregnancy]):
        """Set current pregnancy."""
        if pregnancy:
            self.attributes.add("current_pregnancy", pregnancy.to_dict())
        else:
            self.attributes.remove("current_pregnancy")
    
    def is_pregnant(self) -> bool:
        """Check if currently pregnant."""
        preg = self.current_pregnancy
        return preg is not None and preg.is_active
    
    def get_pregnancy_stage(self) -> Optional[GestationStage]:
        """Get current pregnancy stage."""
        preg = self.current_pregnancy
        if preg:
            preg.update_stage()
            return preg.stage
        return None
    
    def get_belly_description(self) -> str:
        """Get belly description based on pregnancy."""
        preg = self.current_pregnancy
        if preg and preg.is_active:
            return preg.get_belly_description()
        return ""
    
    @property
    def offspring_history(self) -> List[Offspring]:
        """Get list of all offspring ever born."""
        data = self.attributes.get("offspring_history", [])
        return [Offspring.from_dict(d) for d in data]
    
    def add_offspring(self, offspring: Offspring):
        """Add offspring to history."""
        history = self.attributes.get("offspring_history", [])
        history.append(offspring.to_dict())
        self.attributes.add("offspring_history", history)
    
    @property
    def pregnancy_history(self) -> List[Pregnancy]:
        """Get list of all pregnancies."""
        data = self.attributes.get("pregnancy_history", [])
        return [Pregnancy.from_dict(d) for d in data]
    
    def add_pregnancy_to_history(self, pregnancy: Pregnancy):
        """Add pregnancy to history."""
        history = self.attributes.get("pregnancy_history", [])
        history.append(pregnancy.to_dict())
        self.attributes.add("pregnancy_history", history)


__all__ = [
    "GestationStage",
    "OffspringStage",
    "SPECIES_BREEDING_DATA",
    "get_species_breeding_data",
    "InheritableTraits",
    "Pregnancy",
    "Offspring",
    "BreedingSystem",
    "PregnancyMixin",
]
