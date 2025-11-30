"""
Dairy Processing System
=======================

Milk processing and product creation including:
- Raw milk storage
- Product creation (cheese, butter, cream)
- Special milk processing
- Quality grades
- Sales and pricing
"""

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any, Tuple
from enum import Enum
from datetime import datetime, timedelta
import random


# =============================================================================
# ENUMS
# =============================================================================

class MilkGrade(Enum):
    """Quality grades for milk."""
    POOR = "poor"
    STANDARD = "standard"
    QUALITY = "quality"
    PREMIUM = "premium"
    EXCEPTIONAL = "exceptional"


class MilkProperty(Enum):
    """Special properties milk can have."""
    NORMAL = "normal"
    CREAM_RICH = "cream_rich"
    PROTEIN_RICH = "protein_rich"
    SWEET = "sweet"
    APHRODISIAC = "aphrodisiac"
    MAGICAL = "magical"
    DRUGGED = "drugged"


class ProductType(Enum):
    """Types of dairy products."""
    RAW_MILK = "raw_milk"
    CREAM = "cream"
    BUTTER = "butter"
    CHEESE_SOFT = "cheese_soft"
    CHEESE_HARD = "cheese_hard"
    YOGURT = "yogurt"
    ICE_CREAM = "ice_cream"
    APHRODISIAC_MILK = "aphrodisiac_milk"
    MAGICAL_CREAM = "magical_cream"
    ENHANCEMENT_BUTTER = "enhancement_butter"


# =============================================================================
# MILK BATCH
# =============================================================================

@dataclass
class MilkBatch:
    """A batch of collected milk."""
    
    batch_id: str = ""
    
    # Source
    source_dbref: str = ""
    source_name: str = ""
    
    # Quantity
    volume_ml: int = 0
    
    # Quality
    grade: MilkGrade = MilkGrade.STANDARD
    fat_content: float = 3.5
    protein_content: float = 3.2
    sweetness: int = 50
    
    # Properties
    properties: List[MilkProperty] = field(default_factory=list)
    
    # Timing
    collected_at: Optional[datetime] = None
    expires_at: Optional[datetime] = None
    
    # Value
    base_value_per_liter: int = 5
    
    @property
    def is_expired(self) -> bool:
        """Check if milk is expired."""
        if not self.expires_at:
            return False
        return datetime.now() > self.expires_at
    
    @property
    def total_value(self) -> int:
        """Calculate total value."""
        grade_mult = {
            MilkGrade.POOR: 0.5,
            MilkGrade.STANDARD: 1.0,
            MilkGrade.QUALITY: 1.5,
            MilkGrade.PREMIUM: 2.0,
            MilkGrade.EXCEPTIONAL: 3.0,
        }
        
        property_mult = 1.0
        for prop in self.properties:
            if prop == MilkProperty.CREAM_RICH:
                property_mult += 0.2
            elif prop == MilkProperty.SWEET:
                property_mult += 0.3
            elif prop == MilkProperty.APHRODISIAC:
                property_mult += 2.0
            elif prop == MilkProperty.MAGICAL:
                property_mult += 5.0
        
        liters = self.volume_ml / 1000
        return int(liters * self.base_value_per_liter * grade_mult.get(self.grade, 1.0) * property_mult)
    
    def to_dict(self) -> dict:
        return {
            "batch_id": self.batch_id,
            "source_dbref": self.source_dbref,
            "source_name": self.source_name,
            "volume_ml": self.volume_ml,
            "grade": self.grade.value,
            "fat_content": self.fat_content,
            "protein_content": self.protein_content,
            "sweetness": self.sweetness,
            "properties": [p.value for p in self.properties],
            "collected_at": self.collected_at.isoformat() if self.collected_at else None,
            "expires_at": self.expires_at.isoformat() if self.expires_at else None,
            "base_value_per_liter": self.base_value_per_liter,
        }


# =============================================================================
# DAIRY PRODUCT
# =============================================================================

@dataclass
class DairyProduct:
    """A produced dairy product."""
    
    product_id: str = ""
    product_type: ProductType = ProductType.RAW_MILK
    name: str = ""
    
    # Quantity
    quantity: int = 1             # Units produced
    unit: str = "unit"            # "liter", "kg", "wheel", etc.
    
    # Quality
    grade: MilkGrade = MilkGrade.STANDARD
    
    # Source milk properties (inherited)
    properties: List[MilkProperty] = field(default_factory=list)
    
    # Value
    base_value: int = 10
    
    # Timing
    produced_at: Optional[datetime] = None
    expires_at: Optional[datetime] = None
    
    # Effects (for special products)
    effects: Dict[str, int] = field(default_factory=dict)
    
    @property
    def total_value(self) -> int:
        """Calculate total value."""
        grade_mult = {
            MilkGrade.POOR: 0.5,
            MilkGrade.STANDARD: 1.0,
            MilkGrade.QUALITY: 1.5,
            MilkGrade.PREMIUM: 2.0,
            MilkGrade.EXCEPTIONAL: 3.0,
        }
        
        return int(self.base_value * self.quantity * grade_mult.get(self.grade, 1.0))
    
    def get_description(self) -> str:
        """Get product description."""
        desc = f"{self.quantity} {self.unit} of {self.grade.value} {self.name}"
        if self.properties:
            props = [p.value for p in self.properties if p != MilkProperty.NORMAL]
            if props:
                desc += f" ({', '.join(props)})"
        return desc


# =============================================================================
# PROCESSING RECIPES
# =============================================================================

@dataclass
class ProcessingRecipe:
    """Recipe for creating a dairy product."""
    
    recipe_id: str = ""
    name: str = ""
    product_type: ProductType = ProductType.RAW_MILK
    
    # Input
    milk_required_ml: int = 1000
    required_properties: List[MilkProperty] = field(default_factory=list)
    
    # Output
    output_quantity: int = 1
    output_unit: str = "unit"
    base_value: int = 10
    
    # Processing
    processing_hours: int = 1
    
    # Effects (for consumables)
    effects: Dict[str, int] = field(default_factory=dict)


RECIPES = {
    "cream": ProcessingRecipe(
        recipe_id="cream",
        name="Fresh Cream",
        product_type=ProductType.CREAM,
        milk_required_ml=2000,
        output_quantity=500,
        output_unit="ml",
        base_value=15,
        processing_hours=2,
    ),
    "butter": ProcessingRecipe(
        recipe_id="butter",
        name="Butter",
        product_type=ProductType.BUTTER,
        milk_required_ml=5000,
        output_quantity=250,
        output_unit="g",
        base_value=25,
        processing_hours=4,
    ),
    "soft_cheese": ProcessingRecipe(
        recipe_id="soft_cheese",
        name="Soft Cheese",
        product_type=ProductType.CHEESE_SOFT,
        milk_required_ml=3000,
        output_quantity=300,
        output_unit="g",
        base_value=30,
        processing_hours=24,
    ),
    "hard_cheese": ProcessingRecipe(
        recipe_id="hard_cheese",
        name="Aged Cheese",
        product_type=ProductType.CHEESE_HARD,
        milk_required_ml=10000,
        output_quantity=1,
        output_unit="wheel",
        base_value=100,
        processing_hours=168,  # 7 days
    ),
    "yogurt": ProcessingRecipe(
        recipe_id="yogurt",
        name="Yogurt",
        product_type=ProductType.YOGURT,
        milk_required_ml=1000,
        output_quantity=1000,
        output_unit="ml",
        base_value=12,
        processing_hours=8,
    ),
    "ice_cream": ProcessingRecipe(
        recipe_id="ice_cream",
        name="Ice Cream",
        product_type=ProductType.ICE_CREAM,
        milk_required_ml=2000,
        output_quantity=1000,
        output_unit="ml",
        base_value=20,
        processing_hours=6,
    ),
    "aphrodisiac_milk": ProcessingRecipe(
        recipe_id="aphrodisiac_milk",
        name="Aphrodisiac Milk",
        product_type=ProductType.APHRODISIAC_MILK,
        milk_required_ml=500,
        required_properties=[MilkProperty.APHRODISIAC],
        output_quantity=500,
        output_unit="ml",
        base_value=100,
        processing_hours=1,
        effects={"arousal": 50, "libido": 30},
    ),
    "magical_cream": ProcessingRecipe(
        recipe_id="magical_cream",
        name="Magical Cream",
        product_type=ProductType.MAGICAL_CREAM,
        milk_required_ml=1000,
        required_properties=[MilkProperty.MAGICAL],
        output_quantity=200,
        output_unit="ml",
        base_value=500,
        processing_hours=12,
        effects={"mana_restore": 50, "healing": 20},
    ),
    "enhancement_butter": ProcessingRecipe(
        recipe_id="enhancement_butter",
        name="Enhancement Butter",
        product_type=ProductType.ENHANCEMENT_BUTTER,
        milk_required_ml=5000,
        required_properties=[MilkProperty.MAGICAL],
        output_quantity=100,
        output_unit="g",
        base_value=1000,
        processing_hours=48,
        effects={"breast_growth": 50, "lactation_boost": 30},
    ),
}


# =============================================================================
# DAIRY FACILITY
# =============================================================================

@dataclass
class DairyFacility:
    """A dairy processing facility."""
    
    facility_id: str = ""
    name: str = "Dairy"
    
    # Storage
    milk_storage: List[MilkBatch] = field(default_factory=list)
    max_storage_ml: int = 50000
    
    # Products
    products: List[DairyProduct] = field(default_factory=list)
    
    # Processing
    current_processes: List[Dict] = field(default_factory=list)
    max_concurrent_processes: int = 3
    
    # Stats
    total_milk_processed_ml: int = 0
    total_products_created: int = 0
    total_revenue: int = 0
    
    @property
    def current_storage_ml(self) -> int:
        """Get current milk in storage."""
        return sum(b.volume_ml for b in self.milk_storage if not b.is_expired)
    
    @property
    def storage_percent(self) -> float:
        """Get storage percentage."""
        return (self.current_storage_ml / self.max_storage_ml) * 100
    
    def add_milk(self, batch: MilkBatch) -> Tuple[bool, str]:
        """Add milk to storage."""
        if self.current_storage_ml + batch.volume_ml > self.max_storage_ml:
            overflow = (self.current_storage_ml + batch.volume_ml) - self.max_storage_ml
            return False, f"Storage full! Would overflow by {overflow}ml."
        
        # Set expiration (3 days for raw milk)
        batch.collected_at = datetime.now()
        batch.expires_at = datetime.now() + timedelta(days=3)
        
        self.milk_storage.append(batch)
        
        return True, f"Added {batch.volume_ml}ml from {batch.source_name}. Storage: {self.storage_percent:.1f}%"
    
    def remove_expired(self) -> int:
        """Remove expired milk, return amount removed."""
        expired = [b for b in self.milk_storage if b.is_expired]
        total_expired = sum(b.volume_ml for b in expired)
        
        self.milk_storage = [b for b in self.milk_storage if not b.is_expired]
        
        return total_expired
    
    def can_process(self, recipe_id: str) -> Tuple[bool, str]:
        """Check if can process a recipe."""
        if recipe_id not in RECIPES:
            return False, "Unknown recipe."
        
        recipe = RECIPES[recipe_id]
        
        # Check capacity
        if len(self.current_processes) >= self.max_concurrent_processes:
            return False, "All processing slots in use."
        
        # Check milk availability
        available_milk = self.current_storage_ml
        if available_milk < recipe.milk_required_ml:
            return False, f"Not enough milk. Need {recipe.milk_required_ml}ml, have {available_milk}ml."
        
        # Check required properties
        if recipe.required_properties:
            has_properties = False
            for batch in self.milk_storage:
                if all(prop in batch.properties for prop in recipe.required_properties):
                    has_properties = True
                    break
            if not has_properties:
                props = [p.value for p in recipe.required_properties]
                return False, f"Need milk with properties: {', '.join(props)}"
        
        return True, "Can process."
    
    def start_processing(self, recipe_id: str) -> Tuple[bool, str]:
        """Start processing a recipe."""
        can, msg = self.can_process(recipe_id)
        if not can:
            return False, msg
        
        recipe = RECIPES[recipe_id]
        
        # Select and consume milk
        milk_needed = recipe.milk_required_ml
        consumed_batches = []
        inherited_properties = []
        best_grade = MilkGrade.POOR
        
        for batch in sorted(self.milk_storage, key=lambda b: b.collected_at or datetime.min):
            if milk_needed <= 0:
                break
            
            # Check required properties
            if recipe.required_properties:
                if not all(prop in batch.properties for prop in recipe.required_properties):
                    continue
            
            consume = min(batch.volume_ml, milk_needed)
            batch.volume_ml -= consume
            milk_needed -= consume
            
            inherited_properties.extend(batch.properties)
            if batch.grade.value > best_grade.value:
                best_grade = batch.grade
            
            if batch.volume_ml <= 0:
                consumed_batches.append(batch)
        
        # Remove empty batches
        self.milk_storage = [b for b in self.milk_storage if b.volume_ml > 0]
        
        # Create process
        process = {
            "recipe_id": recipe_id,
            "recipe": recipe,
            "started_at": datetime.now(),
            "completes_at": datetime.now() + timedelta(hours=recipe.processing_hours),
            "inherited_properties": list(set(inherited_properties)),
            "grade": best_grade,
        }
        
        self.current_processes.append(process)
        self.total_milk_processed_ml += recipe.milk_required_ml
        
        return True, f"Started processing {recipe.name}. Completes in {recipe.processing_hours} hours."
    
    def check_completed(self) -> List[DairyProduct]:
        """Check for completed processes and create products."""
        completed = []
        remaining = []
        
        for process in self.current_processes:
            if datetime.now() >= process["completes_at"]:
                recipe = process["recipe"]
                
                product = DairyProduct(
                    product_id=f"PROD-{datetime.now().strftime('%Y%m%d%H%M%S')}-{random.randint(100, 999)}",
                    product_type=recipe.product_type,
                    name=recipe.name,
                    quantity=recipe.output_quantity,
                    unit=recipe.output_unit,
                    grade=process["grade"],
                    properties=process["inherited_properties"],
                    base_value=recipe.base_value,
                    produced_at=datetime.now(),
                    effects=recipe.effects.copy(),
                )
                
                self.products.append(product)
                self.total_products_created += 1
                completed.append(product)
            else:
                remaining.append(process)
        
        self.current_processes = remaining
        return completed
    
    def sell_product(self, product_id: str) -> Tuple[bool, int, str]:
        """
        Sell a product.
        Returns (success, gold_earned, message).
        """
        for i, product in enumerate(self.products):
            if product.product_id == product_id:
                value = product.total_value
                self.products.pop(i)
                self.total_revenue += value
                return True, value, f"Sold {product.get_description()} for {value} gold."
        
        return False, 0, "Product not found."
    
    def sell_all_products(self) -> Tuple[int, int, str]:
        """
        Sell all products.
        Returns (count_sold, gold_earned, message).
        """
        total = 0
        count = 0
        
        for product in self.products:
            total += product.total_value
            count += 1
        
        self.products.clear()
        self.total_revenue += total
        
        return count, total, f"Sold {count} products for {total} gold."
    
    def get_status(self) -> str:
        """Get facility status."""
        lines = [f"=== {self.name} Status ==="]
        
        lines.append(f"\n--- Milk Storage ---")
        lines.append(f"Current: {self.current_storage_ml}ml / {self.max_storage_ml}ml ({self.storage_percent:.1f}%)")
        
        if self.milk_storage:
            lines.append("Batches:")
            for batch in self.milk_storage[:5]:
                props = [p.value for p in batch.properties if p != MilkProperty.NORMAL]
                prop_str = f" [{', '.join(props)}]" if props else ""
                lines.append(f"  • {batch.volume_ml}ml {batch.grade.value} from {batch.source_name}{prop_str}")
        
        lines.append(f"\n--- Processing ({len(self.current_processes)}/{self.max_concurrent_processes}) ---")
        for proc in self.current_processes:
            remaining = (proc["completes_at"] - datetime.now()).total_seconds() / 3600
            lines.append(f"  • {proc['recipe'].name}: {remaining:.1f}h remaining")
        
        lines.append(f"\n--- Products ({len(self.products)}) ---")
        for product in self.products[:5]:
            lines.append(f"  • {product.get_description()} - {product.total_value}g")
        
        lines.append(f"\n--- Statistics ---")
        lines.append(f"Total Processed: {self.total_milk_processed_ml / 1000:.1f} liters")
        lines.append(f"Products Created: {self.total_products_created}")
        lines.append(f"Total Revenue: {self.total_revenue} gold")
        
        return "\n".join(lines)
    
    def to_dict(self) -> dict:
        return {
            "facility_id": self.facility_id,
            "name": self.name,
            "milk_storage": [b.to_dict() for b in self.milk_storage],
            "max_storage_ml": self.max_storage_ml,
            "total_milk_processed_ml": self.total_milk_processed_ml,
            "total_products_created": self.total_products_created,
            "total_revenue": self.total_revenue,
        }


# =============================================================================
# FACTORY FUNCTIONS
# =============================================================================

def create_milk_batch(
    source_dbref: str,
    source_name: str,
    volume: int,
    fat: float = 3.5,
    protein: float = 3.2,
    sweetness: int = 50,
    properties: List[MilkProperty] = None,
) -> MilkBatch:
    """Create a new milk batch."""
    
    # Determine grade based on stats
    quality_score = (fat * 10) + (protein * 10) + (sweetness / 5)
    
    if quality_score >= 90:
        grade = MilkGrade.EXCEPTIONAL
    elif quality_score >= 75:
        grade = MilkGrade.PREMIUM
    elif quality_score >= 60:
        grade = MilkGrade.QUALITY
    elif quality_score >= 40:
        grade = MilkGrade.STANDARD
    else:
        grade = MilkGrade.POOR
    
    return MilkBatch(
        batch_id=f"MILK-{datetime.now().strftime('%Y%m%d%H%M%S')}-{random.randint(100, 999)}",
        source_dbref=source_dbref,
        source_name=source_name,
        volume_ml=volume,
        grade=grade,
        fat_content=fat,
        protein_content=protein,
        sweetness=sweetness,
        properties=properties or [MilkProperty.NORMAL],
        collected_at=datetime.now(),
        expires_at=datetime.now() + timedelta(days=3),
    )


def create_standard_dairy() -> DairyFacility:
    """Create a standard dairy facility."""
    return DairyFacility(
        facility_id=f"DAIRY-{random.randint(1000, 9999)}",
        name="Farm Dairy",
        max_storage_ml=50000,
        max_concurrent_processes=3,
    )


__all__ = [
    "MilkGrade",
    "MilkProperty",
    "ProductType",
    "MilkBatch",
    "DairyProduct",
    "ProcessingRecipe",
    "RECIPES",
    "DairyFacility",
    "create_milk_batch",
    "create_standard_dairy",
]
