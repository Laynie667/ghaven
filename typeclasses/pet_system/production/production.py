"""
Production System
=================

Fluid production mechanics:
- Lactation and milking
- Production tracking
- Milking equipment
"""

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any, Tuple
from enum import Enum
from datetime import datetime, timedelta
import random


# =============================================================================
# ENUMS
# =============================================================================

class FluidType(Enum):
    """Types of producible fluids."""
    MILK = "milk"
    CUM = "cum"
    FEMININE_FLUID = "feminine_fluid"
    SALIVA = "saliva"
    SWEAT = "sweat"


class ProductionLevel(Enum):
    """Production levels."""
    NONE = "none"
    MINIMAL = "minimal"
    LOW = "low"
    MODERATE = "moderate"
    HIGH = "high"
    EXCESSIVE = "excessive"
    OVERPRODUCING = "overproducing"


class MilkingMethod(Enum):
    """Methods of extraction."""
    MANUAL = "manual"           # By hand
    MOUTH = "mouth"             # Oral
    PUMP = "pump"               # Mechanical pump
    MAGIC = "magic"             # Magical extraction
    NATURAL = "natural"         # Natural flow/leaking


# =============================================================================
# PRODUCTION STATS
# =============================================================================

@dataclass
class ProductionStats:
    """Fluid production statistics."""
    fluid_type: FluidType = FluidType.MILK
    
    # Capacity and current level
    max_capacity_ml: int = 500
    current_ml: int = 0
    
    # Production rate
    production_rate_per_hour: int = 50
    
    # Quality
    quality: int = 50           # 0-100
    richness: int = 50          # Fat content, thickness
    
    # State
    is_producing: bool = False
    is_full: bool = False
    is_leaking: bool = False
    
    # Tracking
    total_produced_ml: int = 0
    times_milked: int = 0
    last_milked: Optional[datetime] = None
    last_update: Optional[datetime] = None
    
    def update_production(self) -> List[str]:
        """Update production based on time passed."""
        messages = []
        
        if not self.is_producing:
            return messages
        
        now = datetime.now()
        if not self.last_update:
            self.last_update = now
            return messages
        
        # Calculate production
        hours_passed = (now - self.last_update).total_seconds() / 3600
        production = int(self.production_rate_per_hour * hours_passed)
        
        old_level = self.current_ml
        self.current_ml = min(self.max_capacity_ml, self.current_ml + production)
        self.total_produced_ml += self.current_ml - old_level
        
        # Check fullness
        fullness = self.current_ml / self.max_capacity_ml
        
        if fullness >= 1.0:
            self.is_full = True
            self.is_leaking = True
            messages.append(f"Completely full and leaking {self.fluid_type.value}!")
        elif fullness >= 0.9:
            self.is_full = True
            messages.append(f"Almost painfully full of {self.fluid_type.value}.")
        elif fullness >= 0.7:
            messages.append(f"Feeling heavy with {self.fluid_type.value}.")
        
        self.last_update = now
        return messages
    
    def extract(self, amount_ml: int, method: MilkingMethod = MilkingMethod.MANUAL) -> Tuple[int, str]:
        """
        Extract fluid.
        Returns (amount_extracted, message).
        """
        if self.current_ml <= 0:
            return 0, f"Nothing to extract."
        
        # Calculate extraction efficiency
        efficiency = {
            MilkingMethod.MANUAL: 0.7,
            MilkingMethod.MOUTH: 0.8,
            MilkingMethod.PUMP: 0.95,
            MilkingMethod.MAGIC: 1.0,
            MilkingMethod.NATURAL: 0.5,
        }
        
        eff = efficiency.get(method, 0.7)
        max_extract = int(self.current_ml * eff)
        actual = min(amount_ml, max_extract)
        
        self.current_ml -= actual
        self.times_milked += 1
        self.last_milked = datetime.now()
        
        if self.current_ml < self.max_capacity_ml * 0.3:
            self.is_full = False
            self.is_leaking = False
        
        return actual, f"Extracted {actual}ml of {self.fluid_type.value}."
    
    def get_level(self) -> ProductionLevel:
        """Get production level."""
        rate = self.production_rate_per_hour
        
        if not self.is_producing or rate == 0:
            return ProductionLevel.NONE
        elif rate < 20:
            return ProductionLevel.MINIMAL
        elif rate < 50:
            return ProductionLevel.LOW
        elif rate < 100:
            return ProductionLevel.MODERATE
        elif rate < 200:
            return ProductionLevel.HIGH
        elif rate < 500:
            return ProductionLevel.EXCESSIVE
        else:
            return ProductionLevel.OVERPRODUCING
    
    def get_fullness_percent(self) -> int:
        """Get fullness percentage."""
        if self.max_capacity_ml == 0:
            return 0
        return int((self.current_ml / self.max_capacity_ml) * 100)
    
    def to_dict(self) -> dict:
        return {
            "fluid_type": self.fluid_type.value,
            "max_capacity_ml": self.max_capacity_ml,
            "current_ml": self.current_ml,
            "production_rate_per_hour": self.production_rate_per_hour,
            "quality": self.quality,
            "richness": self.richness,
            "is_producing": self.is_producing,
            "is_full": self.is_full,
            "is_leaking": self.is_leaking,
            "total_produced_ml": self.total_produced_ml,
            "times_milked": self.times_milked,
            "last_milked": self.last_milked.isoformat() if self.last_milked else None,
            "last_update": self.last_update.isoformat() if self.last_update else None,
        }
    
    @classmethod
    def from_dict(cls, data: dict) -> "ProductionStats":
        stats = cls()
        stats.fluid_type = FluidType(data.get("fluid_type", "milk"))
        stats.max_capacity_ml = data.get("max_capacity_ml", 500)
        stats.current_ml = data.get("current_ml", 0)
        stats.production_rate_per_hour = data.get("production_rate_per_hour", 50)
        stats.quality = data.get("quality", 50)
        stats.richness = data.get("richness", 50)
        stats.is_producing = data.get("is_producing", False)
        stats.is_full = data.get("is_full", False)
        stats.is_leaking = data.get("is_leaking", False)
        stats.total_produced_ml = data.get("total_produced_ml", 0)
        stats.times_milked = data.get("times_milked", 0)
        
        if data.get("last_milked"):
            stats.last_milked = datetime.fromisoformat(data["last_milked"])
        if data.get("last_update"):
            stats.last_update = datetime.fromisoformat(data["last_update"])
        
        return stats


# =============================================================================
# MILKING EQUIPMENT
# =============================================================================

@dataclass
class MilkingEquipment:
    """Milking equipment/station."""
    key: str
    name: str
    
    # Capability
    extraction_method: MilkingMethod = MilkingMethod.PUMP
    extraction_rate: int = 100  # ml per minute
    
    # Capacity
    container_capacity_ml: int = 2000
    current_collected_ml: int = 0
    
    # Settings
    suction_strength: int = 50  # 0-100
    causes_arousal: bool = True
    arousal_rate: int = 5       # Per minute
    
    # Restraint
    restrains_user: bool = False
    escape_dc: int = 50
    
    # Status
    is_occupied: bool = False
    occupant_dbref: str = ""
    occupant_name: str = ""
    
    def attach(self, target) -> Tuple[bool, str]:
        """Attach someone to the equipment."""
        if self.is_occupied:
            return False, f"{self.name} is already occupied by {self.occupant_name}."
        
        self.is_occupied = True
        self.occupant_dbref = target.dbref
        self.occupant_name = target.key
        
        return True, f"{target.key} is attached to {self.name}."
    
    def release(self) -> str:
        """Release the occupant."""
        if not self.is_occupied:
            return f"{self.name} is not occupied."
        
        name = self.occupant_name
        self.is_occupied = False
        self.occupant_dbref = ""
        self.occupant_name = ""
        
        return f"{name} is released from {self.name}."
    
    def milk(self, production: ProductionStats, duration_minutes: int = 5) -> Tuple[int, str]:
        """
        Milk for a duration.
        Returns (amount_collected, message).
        """
        if not self.is_occupied:
            return 0, "No one is attached."
        
        # Calculate potential extraction
        potential = self.extraction_rate * duration_minutes
        
        # Extract from production
        extracted, _ = production.extract(potential, self.extraction_method)
        
        # Add to container
        space = self.container_capacity_ml - self.current_collected_ml
        collected = min(extracted, space)
        self.current_collected_ml += collected
        
        overflow = extracted - collected
        overflow_msg = f" ({overflow}ml overflow)" if overflow > 0 else ""
        
        return collected, f"Collected {collected}ml of {production.fluid_type.value}.{overflow_msg}"
    
    def empty_container(self) -> Tuple[int, str]:
        """Empty the collection container."""
        amount = self.current_collected_ml
        self.current_collected_ml = 0
        return amount, f"Collected {amount}ml from {self.name}."
    
    def to_dict(self) -> dict:
        return {
            "key": self.key,
            "name": self.name,
            "extraction_method": self.extraction_method.value,
            "extraction_rate": self.extraction_rate,
            "container_capacity_ml": self.container_capacity_ml,
            "current_collected_ml": self.current_collected_ml,
            "suction_strength": self.suction_strength,
            "causes_arousal": self.causes_arousal,
            "arousal_rate": self.arousal_rate,
            "restrains_user": self.restrains_user,
            "escape_dc": self.escape_dc,
            "is_occupied": self.is_occupied,
            "occupant_dbref": self.occupant_dbref,
            "occupant_name": self.occupant_name,
        }
    
    @classmethod
    def from_dict(cls, data: dict) -> "MilkingEquipment":
        equip = cls(
            key=data["key"],
            name=data["name"],
        )
        equip.extraction_method = MilkingMethod(data.get("extraction_method", "pump"))
        equip.extraction_rate = data.get("extraction_rate", 100)
        equip.container_capacity_ml = data.get("container_capacity_ml", 2000)
        equip.current_collected_ml = data.get("current_collected_ml", 0)
        equip.suction_strength = data.get("suction_strength", 50)
        equip.causes_arousal = data.get("causes_arousal", True)
        equip.arousal_rate = data.get("arousal_rate", 5)
        equip.restrains_user = data.get("restrains_user", False)
        equip.escape_dc = data.get("escape_dc", 50)
        equip.is_occupied = data.get("is_occupied", False)
        equip.occupant_dbref = data.get("occupant_dbref", "")
        equip.occupant_name = data.get("occupant_name", "")
        return equip


# Predefined equipment
EQUIPMENT_HAND_PUMP = MilkingEquipment(
    key="hand_pump",
    name="Hand Pump",
    extraction_method=MilkingMethod.PUMP,
    extraction_rate=50,
    container_capacity_ml=500,
    suction_strength=30,
    causes_arousal=True,
    arousal_rate=3,
    restrains_user=False,
)

EQUIPMENT_BREAST_PUMP = MilkingEquipment(
    key="breast_pump",
    name="Breast Pump Station",
    extraction_method=MilkingMethod.PUMP,
    extraction_rate=100,
    container_capacity_ml=2000,
    suction_strength=50,
    causes_arousal=True,
    arousal_rate=5,
    restrains_user=True,
    escape_dc=40,
)

EQUIPMENT_INDUSTRIAL_MILKER = MilkingEquipment(
    key="industrial_milker",
    name="Industrial Milking Machine",
    extraction_method=MilkingMethod.PUMP,
    extraction_rate=200,
    container_capacity_ml=5000,
    suction_strength=70,
    causes_arousal=True,
    arousal_rate=10,
    restrains_user=True,
    escape_dc=60,
)

EQUIPMENT_MAGIC_EXTRACTOR = MilkingEquipment(
    key="magic_extractor",
    name="Magical Extraction Crystal",
    extraction_method=MilkingMethod.MAGIC,
    extraction_rate=150,
    container_capacity_ml=3000,
    suction_strength=60,
    causes_arousal=True,
    arousal_rate=8,
    restrains_user=True,
    escape_dc=70,
)

ALL_EQUIPMENT: Dict[str, MilkingEquipment] = {
    "hand_pump": EQUIPMENT_HAND_PUMP,
    "breast_pump": EQUIPMENT_BREAST_PUMP,
    "industrial_milker": EQUIPMENT_INDUSTRIAL_MILKER,
    "magic_extractor": EQUIPMENT_MAGIC_EXTRACTOR,
}


# =============================================================================
# PRODUCTION MIXIN
# =============================================================================

class ProducerMixin:
    """
    Mixin for characters that can produce fluids.
    """
    
    @property
    def milk_production(self) -> Optional[ProductionStats]:
        """Get milk production stats."""
        data = self.attributes.get("milk_production")
        if data:
            return ProductionStats.from_dict(data)
        return None
    
    @milk_production.setter
    def milk_production(self, stats: Optional[ProductionStats]):
        """Set milk production."""
        if stats:
            self.attributes.add("milk_production", stats.to_dict())
        else:
            self.attributes.remove("milk_production")
    
    def start_lactation(self, rate: int = 50, capacity: int = 500) -> str:
        """Start lactation."""
        stats = ProductionStats(
            fluid_type=FluidType.MILK,
            max_capacity_ml=capacity,
            production_rate_per_hour=rate,
            is_producing=True,
            last_update=datetime.now(),
        )
        self.milk_production = stats
        return "Lactation begins."
    
    def stop_lactation(self) -> str:
        """Stop lactation."""
        stats = self.milk_production
        if stats:
            stats.is_producing = False
            self.milk_production = stats
            return "Lactation stops."
        return "Not lactating."
    
    def is_lactating(self) -> bool:
        """Check if lactating."""
        stats = self.milk_production
        return stats is not None and stats.is_producing
    
    def is_full_of_milk(self) -> bool:
        """Check if breasts are full."""
        stats = self.milk_production
        return stats is not None and stats.is_full
    
    def get_milk_level(self) -> int:
        """Get current milk level in ml."""
        stats = self.milk_production
        if stats:
            return stats.current_ml
        return 0
    
    def update_lactation(self) -> List[str]:
        """Update lactation and return any messages."""
        stats = self.milk_production
        if not stats:
            return []
        
        messages = stats.update_production()
        self.milk_production = stats
        return messages


__all__ = [
    "FluidType",
    "ProductionLevel",
    "MilkingMethod",
    "ProductionStats",
    "MilkingEquipment",
    "ALL_EQUIPMENT",
    "ProducerMixin",
]
