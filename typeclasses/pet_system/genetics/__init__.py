"""
Breeding Program System
=======================

Comprehensive breeding management including:
- Genetics and trait inheritance
- Lineage tracking
- Breeding optimization
- Offspring management
- Breeding festivals
"""

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any, Tuple, Set
from enum import Enum
from datetime import datetime, timedelta
import random


# =============================================================================
# GENETIC TRAITS
# =============================================================================

class TraitCategory(Enum):
    """Categories of genetic traits."""
    PHYSICAL = "physical"
    LACTATION = "lactation"
    FERTILITY = "fertility"
    TEMPERAMENT = "temperament"
    SEXUAL = "sexual"
    SPECIAL = "special"


class TraitRarity(Enum):
    """Rarity of traits."""
    COMMON = "common"             # 60% inheritance
    UNCOMMON = "uncommon"         # 40% inheritance
    RARE = "rare"                 # 20% inheritance
    LEGENDARY = "legendary"       # 5% inheritance
    UNIQUE = "unique"             # Cannot be inherited naturally


@dataclass
class GeneticTrait:
    """A single genetic trait."""
    
    trait_id: str = ""
    name: str = ""
    category: TraitCategory = TraitCategory.PHYSICAL
    rarity: TraitRarity = TraitRarity.COMMON
    
    description: str = ""
    
    # Effects
    lactation_bonus: float = 0.0
    fertility_bonus: int = 0
    litter_size_bonus: int = 0
    milk_quality_bonus: int = 0
    obedience_bonus: int = 0
    libido_bonus: int = 0
    heat_intensity_bonus: int = 0
    
    # Inheritance
    is_dominant: bool = False     # Dominant traits more likely to pass
    inheritance_chance: float = 0.5
    
    # Conflicts
    incompatible_traits: List[str] = field(default_factory=list)
    
    def calculate_inheritance_chance(self, both_parents_have: bool) -> float:
        """Calculate chance to inherit this trait."""
        base = {
            TraitRarity.COMMON: 0.6,
            TraitRarity.UNCOMMON: 0.4,
            TraitRarity.RARE: 0.2,
            TraitRarity.LEGENDARY: 0.05,
            TraitRarity.UNIQUE: 0.0,
        }.get(self.rarity, 0.3)
        
        if both_parents_have:
            base *= 1.5
        if self.is_dominant:
            base *= 1.3
        
        return min(0.95, base)


# =============================================================================
# PRESET TRAITS
# =============================================================================

GENETIC_TRAITS = {
    # Physical traits
    "large_breasts": GeneticTrait(
        trait_id="large_breasts",
        name="Large Breasts",
        category=TraitCategory.PHYSICAL,
        rarity=TraitRarity.COMMON,
        description="Naturally large breasts",
        lactation_bonus=0.2,
        is_dominant=True,
    ),
    "wide_hips": GeneticTrait(
        trait_id="wide_hips",
        name="Wide Hips",
        category=TraitCategory.PHYSICAL,
        rarity=TraitRarity.COMMON,
        description="Breeding hips for easier births",
        fertility_bonus=10,
        is_dominant=True,
    ),
    "hyper_breasts": GeneticTrait(
        trait_id="hyper_breasts",
        name="Hyper Breasts",
        category=TraitCategory.PHYSICAL,
        rarity=TraitRarity.RARE,
        description="Massively oversized breasts",
        lactation_bonus=0.5,
        incompatible_traits=["small_breasts"],
    ),
    
    # Lactation traits
    "heavy_milker": GeneticTrait(
        trait_id="heavy_milker",
        name="Heavy Milker",
        category=TraitCategory.LACTATION,
        rarity=TraitRarity.UNCOMMON,
        description="Produces significantly more milk",
        lactation_bonus=0.4,
        milk_quality_bonus=10,
    ),
    "cream_producer": GeneticTrait(
        trait_id="cream_producer",
        name="Cream Producer",
        category=TraitCategory.LACTATION,
        rarity=TraitRarity.RARE,
        description="Milk has extra high fat content",
        milk_quality_bonus=25,
    ),
    "endless_milk": GeneticTrait(
        trait_id="endless_milk",
        name="Endless Milk",
        category=TraitCategory.LACTATION,
        rarity=TraitRarity.LEGENDARY,
        description="Never stops producing, never runs dry",
        lactation_bonus=1.0,
    ),
    "sweet_milk": GeneticTrait(
        trait_id="sweet_milk",
        name="Sweet Milk",
        category=TraitCategory.LACTATION,
        rarity=TraitRarity.UNCOMMON,
        description="Naturally sweet, prized milk",
        milk_quality_bonus=20,
    ),
    "aphrodisiac_milk": GeneticTrait(
        trait_id="aphrodisiac_milk",
        name="Aphrodisiac Milk",
        category=TraitCategory.LACTATION,
        rarity=TraitRarity.RARE,
        description="Milk has arousing properties",
        milk_quality_bonus=30,
    ),
    
    # Fertility traits
    "hyper_fertile": GeneticTrait(
        trait_id="hyper_fertile",
        name="Hyper Fertile",
        category=TraitCategory.FERTILITY,
        rarity=TraitRarity.UNCOMMON,
        description="Extremely high conception rate",
        fertility_bonus=30,
    ),
    "twin_bearer": GeneticTrait(
        trait_id="twin_bearer",
        name="Twin Bearer",
        category=TraitCategory.FERTILITY,
        rarity=TraitRarity.RARE,
        description="High chance of multiple offspring",
        litter_size_bonus=1,
    ),
    "perpetual_heat": GeneticTrait(
        trait_id="perpetual_heat",
        name="Perpetual Heat",
        category=TraitCategory.FERTILITY,
        rarity=TraitRarity.RARE,
        description="Always in heat, always ready for breeding",
        heat_intensity_bonus=30,
        fertility_bonus=15,
    ),
    "quick_recovery": GeneticTrait(
        trait_id="quick_recovery",
        name="Quick Recovery",
        category=TraitCategory.FERTILITY,
        rarity=TraitRarity.UNCOMMON,
        description="Returns to breedable state quickly after birth",
        fertility_bonus=10,
    ),
    
    # Temperament traits
    "natural_submissive": GeneticTrait(
        trait_id="natural_submissive",
        name="Natural Submissive",
        category=TraitCategory.TEMPERAMENT,
        rarity=TraitRarity.UNCOMMON,
        description="Naturally docile and obedient",
        obedience_bonus=20,
        is_dominant=True,
    ),
    "eager_breeder": GeneticTrait(
        trait_id="eager_breeder",
        name="Eager Breeder",
        category=TraitCategory.TEMPERAMENT,
        rarity=TraitRarity.UNCOMMON,
        description="Actively desires breeding",
        libido_bonus=20,
        heat_intensity_bonus=15,
    ),
    "pain_tolerant": GeneticTrait(
        trait_id="pain_tolerant",
        name="Pain Tolerant",
        category=TraitCategory.TEMPERAMENT,
        rarity=TraitRarity.UNCOMMON,
        description="High pain tolerance, easier handling",
        obedience_bonus=10,
    ),
    "addictive_personality": GeneticTrait(
        trait_id="addictive_personality",
        name="Addictive Personality",
        category=TraitCategory.TEMPERAMENT,
        rarity=TraitRarity.RARE,
        description="Easily becomes dependent and addicted",
        obedience_bonus=15,
    ),
    
    # Sexual traits
    "multiorgasmic": GeneticTrait(
        trait_id="multiorgasmic",
        name="Multi-Orgasmic",
        category=TraitCategory.SEXUAL,
        rarity=TraitRarity.UNCOMMON,
        description="Capable of continuous orgasms",
        libido_bonus=15,
    ),
    "sensitive_body": GeneticTrait(
        trait_id="sensitive_body",
        name="Sensitive Body",
        category=TraitCategory.SEXUAL,
        rarity=TraitRarity.COMMON,
        description="Heightened sensitivity all over",
        libido_bonus=20,
    ),
    "pheromone_producer": GeneticTrait(
        trait_id="pheromone_producer",
        name="Pheromone Producer",
        category=TraitCategory.SEXUAL,
        rarity=TraitRarity.RARE,
        description="Produces arousing pheromones",
        heat_intensity_bonus=25,
    ),
    
    # Special traits
    "futanari_gene": GeneticTrait(
        trait_id="futanari_gene",
        name="Futanari Gene",
        category=TraitCategory.SPECIAL,
        rarity=TraitRarity.RARE,
        description="Carries the futanari trait",
    ),
    "magical_milk": GeneticTrait(
        trait_id="magical_milk",
        name="Magical Milk",
        category=TraitCategory.SPECIAL,
        rarity=TraitRarity.LEGENDARY,
        description="Milk has magical properties",
        milk_quality_bonus=50,
    ),
}


# =============================================================================
# LINEAGE
# =============================================================================

@dataclass
class LineageRecord:
    """Record of an individual in the breeding program."""
    
    record_id: str = ""
    subject_dbref: str = ""
    subject_name: str = ""
    
    # Parents
    dam_dbref: str = ""           # Mother
    dam_name: str = ""
    sire_dbref: str = ""          # Father
    sire_name: str = ""
    
    # Grandparents
    maternal_granddam: str = ""
    maternal_grandsire: str = ""
    paternal_granddam: str = ""
    paternal_grandsire: str = ""
    
    # Birth info
    birth_date: Optional[datetime] = None
    birth_location: str = ""
    litter_id: str = ""           # If part of multiple birth
    litter_position: int = 1      # 1st, 2nd, etc.
    
    # Genetics
    traits: List[str] = field(default_factory=list)  # Trait IDs
    recessive_traits: List[str] = field(default_factory=list)  # Carried but not expressed
    
    # Breeding record
    times_bred: int = 0
    offspring_count: int = 0
    offspring_ids: List[str] = field(default_factory=list)
    
    # Value
    genetic_value: int = 0        # Based on traits
    breeding_value: int = 0       # Based on offspring quality
    
    # Generation
    generation: int = 1           # F1, F2, etc.
    inbreeding_coefficient: float = 0.0
    
    def calculate_genetic_value(self) -> int:
        """Calculate value based on traits."""
        value = 100  # Base value
        
        for trait_id in self.traits:
            trait = GENETIC_TRAITS.get(trait_id)
            if trait:
                rarity_bonus = {
                    TraitRarity.COMMON: 10,
                    TraitRarity.UNCOMMON: 25,
                    TraitRarity.RARE: 100,
                    TraitRarity.LEGENDARY: 500,
                }.get(trait.rarity, 10)
                value += rarity_bonus
        
        self.genetic_value = value
        return value
    
    def get_full_pedigree(self) -> str:
        """Get formatted pedigree display."""
        lines = [f"=== Pedigree: {self.subject_name} ==="]
        lines.append(f"Generation: F{self.generation}")
        lines.append(f"Inbreeding Coefficient: {self.inbreeding_coefficient:.2%}")
        
        lines.append(f"\n--- Parents ---")
        lines.append(f"Dam (Mother): {self.dam_name or 'Unknown'}")
        lines.append(f"Sire (Father): {self.sire_name or 'Unknown'}")
        
        lines.append(f"\n--- Grandparents ---")
        lines.append(f"Maternal Granddam: {self.maternal_granddam or 'Unknown'}")
        lines.append(f"Maternal Grandsire: {self.maternal_grandsire or 'Unknown'}")
        lines.append(f"Paternal Granddam: {self.paternal_granddam or 'Unknown'}")
        lines.append(f"Paternal Grandsire: {self.paternal_grandsire or 'Unknown'}")
        
        lines.append(f"\n--- Traits ---")
        for trait_id in self.traits:
            trait = GENETIC_TRAITS.get(trait_id)
            if trait:
                lines.append(f"  • {trait.name} ({trait.rarity.value})")
        
        if self.recessive_traits:
            lines.append(f"\nRecessive (Carried):")
            for trait_id in self.recessive_traits:
                trait = GENETIC_TRAITS.get(trait_id)
                if trait:
                    lines.append(f"  ○ {trait.name}")
        
        lines.append(f"\n--- Breeding Record ---")
        lines.append(f"Times Bred: {self.times_bred}")
        lines.append(f"Offspring: {self.offspring_count}")
        lines.append(f"Genetic Value: {self.genetic_value}")
        lines.append(f"Breeding Value: {self.breeding_value}")
        
        return "\n".join(lines)


# =============================================================================
# BREEDING PAIR ANALYSIS
# =============================================================================

@dataclass
class BreedingPairAnalysis:
    """Analysis of a potential breeding pair."""
    
    dam_dbref: str = ""
    dam_name: str = ""
    sire_dbref: str = ""
    sire_name: str = ""
    
    # Compatibility
    compatibility_score: int = 0  # 0-100
    inbreeding_risk: float = 0.0
    
    # Predicted traits
    likely_traits: List[Tuple[str, float]] = field(default_factory=list)  # (trait_id, chance)
    possible_traits: List[Tuple[str, float]] = field(default_factory=list)
    
    # Predicted stats
    predicted_fertility: int = 0
    predicted_lactation: float = 0.0
    predicted_litter_size: float = 1.0
    predicted_obedience: int = 0
    
    # Value prediction
    predicted_offspring_value: int = 0
    
    # Warnings
    warnings: List[str] = field(default_factory=list)
    
    def get_report(self) -> str:
        """Get breeding pair analysis report."""
        lines = [f"=== Breeding Analysis ==="]
        lines.append(f"Dam: {self.dam_name}")
        lines.append(f"Sire: {self.sire_name}")
        
        lines.append(f"\nCompatibility: {self.compatibility_score}/100")
        lines.append(f"Inbreeding Risk: {self.inbreeding_risk:.1%}")
        
        lines.append(f"\n--- Predicted Traits ---")
        lines.append("Likely (>50%):")
        for trait_id, chance in self.likely_traits:
            trait = GENETIC_TRAITS.get(trait_id)
            if trait:
                lines.append(f"  • {trait.name}: {chance:.0%}")
        
        lines.append("\nPossible (20-50%):")
        for trait_id, chance in self.possible_traits:
            trait = GENETIC_TRAITS.get(trait_id)
            if trait:
                lines.append(f"  ○ {trait.name}: {chance:.0%}")
        
        lines.append(f"\n--- Predicted Stats ---")
        lines.append(f"Fertility Bonus: +{self.predicted_fertility}")
        lines.append(f"Lactation Bonus: +{self.predicted_lactation:.0%}")
        lines.append(f"Average Litter: {self.predicted_litter_size:.1f}")
        lines.append(f"Obedience Bonus: +{self.predicted_obedience}")
        
        lines.append(f"\nPredicted Offspring Value: {self.predicted_offspring_value}")
        
        if self.warnings:
            lines.append(f"\n⚠ WARNINGS:")
            for warning in self.warnings:
                lines.append(f"  • {warning}")
        
        return "\n".join(lines)


# =============================================================================
# BREEDING PROGRAM
# =============================================================================

@dataclass
class BreedingProgram:
    """Manages a breeding program."""
    
    program_id: str = ""
    name: str = "Breeding Program"
    owner_dbref: str = ""
    owner_name: str = ""
    
    # Stock
    breeding_stock: Dict[str, LineageRecord] = field(default_factory=dict)  # dbref -> record
    stud_registry: Dict[str, LineageRecord] = field(default_factory=dict)
    
    # Goals
    target_traits: List[str] = field(default_factory=list)
    breeding_goals: str = ""
    
    # History
    total_breedings: int = 0
    total_offspring: int = 0
    successful_trait_transfers: int = 0
    
    # Current generation
    current_generation: int = 1
    
    def register_stock(self, record: LineageRecord, is_stud: bool = False) -> str:
        """Register breeding stock."""
        if is_stud:
            self.stud_registry[record.subject_dbref] = record
            return f"Stud registered: {record.subject_name}"
        else:
            self.breeding_stock[record.subject_dbref] = record
            return f"Breeding stock registered: {record.subject_name}"
    
    def analyze_pair(
        self,
        dam_dbref: str,
        sire_dbref: str,
    ) -> BreedingPairAnalysis:
        """Analyze a potential breeding pair."""
        
        dam = self.breeding_stock.get(dam_dbref)
        sire = self.stud_registry.get(sire_dbref)
        
        if not dam or not sire:
            return BreedingPairAnalysis()
        
        analysis = BreedingPairAnalysis(
            dam_dbref=dam_dbref,
            dam_name=dam.subject_name,
            sire_dbref=sire_dbref,
            sire_name=sire.subject_name,
        )
        
        # Check inbreeding
        if dam.sire_dbref == sire_dbref:
            analysis.inbreeding_risk = 0.25
            analysis.warnings.append("FATHER-DAUGHTER breeding!")
        elif dam.dam_dbref == sire.dam_dbref:
            analysis.inbreeding_risk = 0.125
            analysis.warnings.append("Half-siblings (same mother)")
        elif dam.sire_dbref == sire.sire_dbref:
            analysis.inbreeding_risk = 0.125
            analysis.warnings.append("Half-siblings (same father)")
        
        # Analyze trait inheritance
        all_dam_traits = set(dam.traits + dam.recessive_traits)
        all_sire_traits = set(sire.traits + sire.recessive_traits)
        
        for trait_id in all_dam_traits | all_sire_traits:
            trait = GENETIC_TRAITS.get(trait_id)
            if not trait:
                continue
            
            dam_has = trait_id in dam.traits
            dam_carries = trait_id in dam.recessive_traits
            sire_has = trait_id in sire.traits
            sire_carries = trait_id in sire.recessive_traits
            
            both_express = dam_has and sire_has
            both_carry = (dam_has or dam_carries) and (sire_has or sire_carries)
            
            chance = trait.calculate_inheritance_chance(both_express)
            
            if both_carry:
                chance = min(0.95, chance * 1.3)
            
            if chance >= 0.5:
                analysis.likely_traits.append((trait_id, chance))
            elif chance >= 0.2:
                analysis.possible_traits.append((trait_id, chance))
        
        # Calculate predicted stats
        for trait_id, chance in analysis.likely_traits + analysis.possible_traits:
            trait = GENETIC_TRAITS.get(trait_id)
            if trait:
                analysis.predicted_fertility += int(trait.fertility_bonus * chance)
                analysis.predicted_lactation += trait.lactation_bonus * chance
                analysis.predicted_litter_size += trait.litter_size_bonus * chance
                analysis.predicted_obedience += int(trait.obedience_bonus * chance)
        
        # Calculate compatibility
        compatibility = 70  # Base
        compatibility -= int(analysis.inbreeding_risk * 100)
        compatibility += len(analysis.likely_traits) * 5
        
        for target in self.target_traits:
            if any(t[0] == target for t in analysis.likely_traits):
                compatibility += 10
        
        analysis.compatibility_score = max(0, min(100, compatibility))
        
        # Predict value
        analysis.predicted_offspring_value = (
            100 +
            analysis.predicted_fertility * 2 +
            int(analysis.predicted_lactation * 100) +
            analysis.predicted_obedience * 3 +
            len(analysis.likely_traits) * 50
        )
        
        return analysis
    
    def breed(
        self,
        dam_dbref: str,
        sire_dbref: str,
    ) -> Tuple[bool, str, Optional[List[LineageRecord]]]:
        """
        Perform a breeding.
        Returns (success, message, offspring_records).
        """
        dam = self.breeding_stock.get(dam_dbref)
        sire = self.stud_registry.get(sire_dbref)
        
        if not dam:
            return False, "Dam not in breeding stock.", None
        if not sire:
            return False, "Sire not in stud registry.", None
        
        # Update breeding counts
        dam.times_bred += 1
        sire.times_bred += 1
        self.total_breedings += 1
        
        # Determine litter size
        base_litter = 1
        for trait_id in dam.traits:
            trait = GENETIC_TRAITS.get(trait_id)
            if trait:
                base_litter += trait.litter_size_bonus
        
        # Random variation
        litter_size = base_litter
        if random.random() < 0.15:
            litter_size += 1
        if random.random() < 0.03:
            litter_size += 1
        
        # Generate offspring
        offspring = []
        litter_id = f"LITTER-{datetime.now().strftime('%Y%m%d%H%M%S')}"
        
        for i in range(litter_size):
            child = self._generate_offspring(dam, sire, litter_id, i + 1)
            offspring.append(child)
            dam.offspring_ids.append(child.record_id)
            sire.offspring_ids.append(child.record_id)
        
        dam.offspring_count += litter_size
        sire.offspring_count += litter_size
        self.total_offspring += litter_size
        
        msg = f"Breeding successful! {dam.subject_name} bears {litter_size} offspring by {sire.subject_name}."
        
        return True, msg, offspring
    
    def _generate_offspring(
        self,
        dam: LineageRecord,
        sire: LineageRecord,
        litter_id: str,
        position: int,
    ) -> LineageRecord:
        """Generate a single offspring."""
        
        offspring = LineageRecord(
            record_id=f"OFF-{datetime.now().strftime('%Y%m%d%H%M%S')}-{random.randint(100, 999)}",
            dam_dbref=dam.subject_dbref,
            dam_name=dam.subject_name,
            sire_dbref=sire.subject_dbref,
            sire_name=sire.subject_name,
            maternal_granddam=dam.dam_name,
            maternal_grandsire=dam.sire_name,
            paternal_granddam=sire.dam_name,
            paternal_grandsire=sire.sire_name,
            birth_date=datetime.now(),
            litter_id=litter_id,
            litter_position=position,
            generation=max(dam.generation, sire.generation) + 1,
        )
        
        # Calculate inbreeding
        if dam.sire_dbref == sire.subject_dbref:
            offspring.inbreeding_coefficient = 0.25
        elif dam.dam_dbref == sire.dam_dbref or dam.sire_dbref == sire.sire_dbref:
            offspring.inbreeding_coefficient = 0.125
        
        # Inherit traits
        all_dam_traits = dam.traits + dam.recessive_traits
        all_sire_traits = sire.traits + sire.recessive_traits
        
        for trait_id in set(all_dam_traits + all_sire_traits):
            trait = GENETIC_TRAITS.get(trait_id)
            if not trait:
                continue
            
            dam_has = trait_id in dam.traits
            sire_has = trait_id in sire.traits
            
            chance = trait.calculate_inheritance_chance(dam_has and sire_has)
            
            if random.random() < chance:
                # Check for incompatibilities
                if not any(inc in offspring.traits for inc in trait.incompatible_traits):
                    offspring.traits.append(trait_id)
                    self.successful_trait_transfers += 1
            elif random.random() < chance * 0.5:
                # Becomes recessive carrier
                offspring.recessive_traits.append(trait_id)
        
        offspring.calculate_genetic_value()
        
        return offspring
    
    def get_status(self) -> str:
        """Get program status."""
        lines = [f"=== {self.name} ==="]
        lines.append(f"Owner: {self.owner_name}")
        lines.append(f"Current Generation: F{self.current_generation}")
        
        lines.append(f"\n--- Stock ---")
        lines.append(f"Breeding Stock: {len(self.breeding_stock)}")
        lines.append(f"Studs: {len(self.stud_registry)}")
        
        lines.append(f"\n--- Statistics ---")
        lines.append(f"Total Breedings: {self.total_breedings}")
        lines.append(f"Total Offspring: {self.total_offspring}")
        lines.append(f"Successful Trait Transfers: {self.successful_trait_transfers}")
        
        if self.target_traits:
            lines.append(f"\n--- Goals ---")
            lines.append("Target Traits:")
            for trait_id in self.target_traits:
                trait = GENETIC_TRAITS.get(trait_id)
                if trait:
                    lines.append(f"  • {trait.name}")
        
        return "\n".join(lines)


# =============================================================================
# BREEDING FESTIVAL
# =============================================================================

@dataclass
class BreedingFestival:
    """A breeding festival event."""
    
    festival_id: str = ""
    name: str = "Breeding Festival"
    location: str = ""
    
    # Timing
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    is_active: bool = False
    
    # Participants
    hucows_entered: List[str] = field(default_factory=list)  # dbrefs
    bulls_entered: List[str] = field(default_factory=list)
    
    # Events
    breeding_rounds: int = 0
    successful_conceptions: int = 0
    
    # Competition categories
    most_bred: str = ""
    most_conceptions: str = ""
    best_milk_producer: str = ""
    
    # Prizes
    prizes: Dict[str, int] = field(default_factory=dict)  # category -> gold
    
    def start(self) -> str:
        """Start the festival."""
        self.is_active = True
        self.start_time = datetime.now()
        return f"The {self.name} begins! {len(self.hucows_entered)} hucows and {len(self.bulls_entered)} bulls compete!"
    
    def record_breeding(self, hucow_name: str, bull_name: str, conception: bool) -> str:
        """Record a breeding at the festival."""
        self.breeding_rounds += 1
        if conception:
            self.successful_conceptions += 1
        
        return f"Round {self.breeding_rounds}: {bull_name} breeds {hucow_name}. {'CONCEPTION!' if conception else 'No conception.'}"
    
    def end(self) -> str:
        """End the festival and determine winners."""
        self.is_active = False
        self.end_time = datetime.now()
        
        lines = [f"=== {self.name} Concluded ==="]
        lines.append(f"Total Breeding Rounds: {self.breeding_rounds}")
        lines.append(f"Successful Conceptions: {self.successful_conceptions}")
        lines.append(f"Conception Rate: {(self.successful_conceptions/self.breeding_rounds*100) if self.breeding_rounds else 0:.1f}%")
        
        return "\n".join(lines)


__all__ = [
    "TraitCategory",
    "TraitRarity",
    "GeneticTrait",
    "GENETIC_TRAITS",
    "LineageRecord",
    "BreedingPairAnalysis",
    "BreedingProgram",
    "BreedingFestival",
]
