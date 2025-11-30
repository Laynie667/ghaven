"""
Shops System
============

Vendor shops for buying and selling:
- Shop types (general, specialty, black market)
- Inventory management
- Buy/sell mechanics
- Haggling
"""

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any, Tuple, Callable
from enum import Enum
from datetime import datetime
import random

from .economy import CurrencyType, format_currency, EconomyManager, Wallet


# =============================================================================
# ENUMS
# =============================================================================

class ShopType(Enum):
    """Types of shops."""
    GENERAL = "general"           # Common goods
    ARMORY = "armory"            # Weapons, armor
    CLOTHIER = "clothier"        # Clothing
    APOTHECARY = "apothecary"    # Potions, drugs
    SLAVE_MARKET = "slave_market"  # Slaves/pets
    BROTHEL = "brothel"          # Services
    PET_SHOP = "pet_shop"        # Pets and supplies
    TACK_SHOP = "tack_shop"      # Harnesses, saddles, leashes
    BLACK_MARKET = "black_market"  # Illegal goods
    AUCTION_HOUSE = "auction_house"  # Auctions


class ShopStatus(Enum):
    """Shop operational status."""
    OPEN = "open"
    CLOSED = "closed"
    BUSY = "busy"
    OUT_OF_STOCK = "out_of_stock"


# =============================================================================
# SHOP ITEM
# =============================================================================

@dataclass
class ShopItem:
    """An item for sale in a shop."""
    key: str
    name: str
    
    # Pricing
    base_price: int = 100
    currency: CurrencyType = CurrencyType.GOLD
    
    # Stock
    quantity: int = -1           # -1 = unlimited
    max_quantity: int = -1       # Max stock
    restock_rate: int = 0        # Per day
    
    # Item reference
    item_typeclass: str = ""     # Evennia typeclass for spawning
    item_prototype: str = ""     # Or prototype key
    
    # Requirements
    min_reputation: int = 0      # Min rep to purchase
    required_flags: List[str] = field(default_factory=list)
    
    # Description
    description: str = ""
    
    def get_price(self, buyer_reputation: int = 0, haggle_bonus: int = 0) -> int:
        """Calculate final price with modifiers."""
        price = self.base_price
        
        # Reputation discount (up to 20%)
        if buyer_reputation > 0:
            rep_discount = min(20, buyer_reputation // 10)
            price = int(price * (100 - rep_discount) / 100)
        
        # Haggle discount
        if haggle_bonus > 0:
            price = int(price * (100 - haggle_bonus) / 100)
        
        return max(1, price)
    
    def is_available(self) -> bool:
        """Check if item is in stock."""
        return self.quantity != 0
    
    def purchase_one(self) -> bool:
        """Reduce stock by one. Returns success."""
        if self.quantity == 0:
            return False
        
        if self.quantity > 0:
            self.quantity -= 1
        
        return True
    
    def restock(self, amount: int = 1) -> None:
        """Add stock."""
        if self.max_quantity < 0:
            self.quantity = -1  # Unlimited
        else:
            self.quantity = min(self.max_quantity, self.quantity + amount)
    
    def to_dict(self) -> dict:
        return {
            "key": self.key,
            "name": self.name,
            "base_price": self.base_price,
            "currency": self.currency.value,
            "quantity": self.quantity,
            "max_quantity": self.max_quantity,
            "restock_rate": self.restock_rate,
            "item_typeclass": self.item_typeclass,
            "item_prototype": self.item_prototype,
            "min_reputation": self.min_reputation,
            "required_flags": self.required_flags,
            "description": self.description,
        }
    
    @classmethod
    def from_dict(cls, data: dict) -> "ShopItem":
        item = cls(
            key=data["key"],
            name=data["name"],
        )
        item.base_price = data.get("base_price", 100)
        item.currency = CurrencyType(data.get("currency", "gold"))
        item.quantity = data.get("quantity", -1)
        item.max_quantity = data.get("max_quantity", -1)
        item.restock_rate = data.get("restock_rate", 0)
        item.item_typeclass = data.get("item_typeclass", "")
        item.item_prototype = data.get("item_prototype", "")
        item.min_reputation = data.get("min_reputation", 0)
        item.required_flags = data.get("required_flags", [])
        item.description = data.get("description", "")
        return item


# =============================================================================
# SHOP
# =============================================================================

@dataclass
class Shop:
    """A shop that sells items."""
    key: str
    name: str
    shop_type: ShopType = ShopType.GENERAL
    
    # Owner/Location
    owner_dbref: str = ""
    owner_name: str = ""
    location_dbref: str = ""
    
    # Status
    status: ShopStatus = ShopStatus.OPEN
    
    # Inventory
    inventory: Dict[str, dict] = field(default_factory=dict)
    
    # Settings
    buy_rate: float = 0.5        # What shop pays when buying from players
    sell_markup: float = 1.0     # Markup on base price
    accepts_haggling: bool = True
    max_haggle_discount: int = 30  # Max % discount from haggling
    
    # Reputation
    faction: str = ""            # Associated faction for reputation
    
    # Currency accepted
    accepted_currencies: List[CurrencyType] = field(
        default_factory=lambda: [CurrencyType.GOLD, CurrencyType.SILVER, CurrencyType.COPPER]
    )
    
    # Description
    description: str = ""
    welcome_message: str = "Welcome to {name}! How can I help you?"
    
    def get_item(self, item_key: str) -> Optional[ShopItem]:
        """Get an item from inventory."""
        data = self.inventory.get(item_key)
        if data:
            return ShopItem.from_dict(data)
        return None
    
    def add_item(self, item: ShopItem) -> None:
        """Add item to inventory."""
        self.inventory[item.key] = item.to_dict()
    
    def remove_item(self, item_key: str) -> Optional[ShopItem]:
        """Remove item from inventory."""
        data = self.inventory.pop(item_key, None)
        if data:
            return ShopItem.from_dict(data)
        return None
    
    def get_available_items(self, buyer_reputation: int = 0, buyer_flags: List[str] = None) -> List[ShopItem]:
        """Get items available to a buyer."""
        available = []
        buyer_flags = buyer_flags or []
        
        for data in self.inventory.values():
            item = ShopItem.from_dict(data)
            
            # Check stock
            if not item.is_available():
                continue
            
            # Check reputation
            if buyer_reputation < item.min_reputation:
                continue
            
            # Check flags
            if item.required_flags:
                if not all(f in buyer_flags for f in item.required_flags):
                    continue
            
            available.append(item)
        
        return available
    
    def get_sell_price(self, item: ShopItem, buyer_rep: int = 0, haggle: int = 0) -> int:
        """Get price the shop sells for."""
        base = item.get_price(buyer_rep, haggle)
        return int(base * self.sell_markup)
    
    def get_buy_price(self, base_value: int) -> int:
        """Get price the shop pays when buying."""
        return int(base_value * self.buy_rate)
    
    def attempt_haggle(self, buyer_charisma: int = 10) -> Tuple[bool, int]:
        """
        Attempt to haggle for a discount.
        Returns (success, discount_percent).
        """
        if not self.accepts_haggling:
            return False, 0
        
        # Base success chance: 30% + charisma bonus
        base_chance = 30 + (buyer_charisma - 10) * 2
        
        if random.randint(1, 100) <= base_chance:
            # Success - random discount up to max
            discount = random.randint(5, self.max_haggle_discount)
            return True, discount
        
        return False, 0
    
    def purchase_item(
        self,
        buyer_wallet: Wallet,
        item_key: str,
        buyer_rep: int = 0,
        haggle_discount: int = 0,
    ) -> Tuple[bool, str, Optional[ShopItem]]:
        """
        Purchase an item from the shop.
        Returns (success, message, item).
        """
        if self.status != ShopStatus.OPEN:
            return False, f"{self.name} is currently {self.status.value}.", None
        
        item = self.get_item(item_key)
        if not item:
            return False, f"'{item_key}' not found in inventory.", None
        
        if not item.is_available():
            return False, f"{item.name} is out of stock.", None
        
        # Calculate price
        price = self.get_sell_price(item, buyer_rep, haggle_discount)
        currency = item.currency
        
        # Check currency accepted
        if currency not in self.accepted_currencies:
            currency = self.accepted_currencies[0]
        
        # Check affordability
        if not buyer_wallet.can_afford(currency, price):
            return False, f"Cannot afford {item.name} ({format_currency(price, currency)}).", None
        
        # Process purchase
        success, message, txn = EconomyManager.pay_npc(
            buyer_wallet,
            price,
            currency,
            self.name,
            description=f"Purchased {item.name}",
            item_name=item.name,
        )
        
        if not success:
            return False, message, None
        
        # Reduce stock
        item.purchase_one()
        self.inventory[item_key] = item.to_dict()
        
        return True, f"Purchased {item.name} for {format_currency(price, currency)}.", item
    
    def sell_item_to_shop(
        self,
        seller_wallet: Wallet,
        item_name: str,
        base_value: int,
    ) -> Tuple[bool, str]:
        """
        Sell an item to the shop.
        Returns (success, message).
        """
        if self.status != ShopStatus.OPEN:
            return False, f"{self.name} is currently {self.status.value}."
        
        # Calculate buy price
        price = self.get_buy_price(base_value)
        
        if price <= 0:
            return False, f"{self.name} isn't interested in that item."
        
        currency = self.accepted_currencies[0]
        
        # Pay the seller
        success, message, txn = EconomyManager.receive_from_npc(
            seller_wallet,
            price,
            currency,
            self.name,
            description=f"Sold {item_name}",
            item_name=item_name,
        )
        
        return success, f"Sold {item_name} for {format_currency(price, currency)}."
    
    def daily_restock(self) -> None:
        """Perform daily restocking."""
        for item_key, data in self.inventory.items():
            item = ShopItem.from_dict(data)
            if item.restock_rate > 0:
                item.restock(item.restock_rate)
                self.inventory[item_key] = item.to_dict()
    
    def get_inventory_display(self, buyer_rep: int = 0) -> str:
        """Get formatted inventory list."""
        items = self.get_available_items(buyer_rep)
        
        if not items:
            return "Nothing available for sale."
        
        lines = [f"=== {self.name} ==="]
        
        for item in items:
            price = self.get_sell_price(item, buyer_rep)
            stock = "∞" if item.quantity < 0 else str(item.quantity)
            lines.append(
                f"  {item.name}: {format_currency(price, item.currency)} (stock: {stock})"
            )
        
        return "\n".join(lines)
    
    def to_dict(self) -> dict:
        return {
            "key": self.key,
            "name": self.name,
            "shop_type": self.shop_type.value,
            "owner_dbref": self.owner_dbref,
            "owner_name": self.owner_name,
            "location_dbref": self.location_dbref,
            "status": self.status.value,
            "inventory": self.inventory,
            "buy_rate": self.buy_rate,
            "sell_markup": self.sell_markup,
            "accepts_haggling": self.accepts_haggling,
            "max_haggle_discount": self.max_haggle_discount,
            "faction": self.faction,
            "accepted_currencies": [c.value for c in self.accepted_currencies],
            "description": self.description,
            "welcome_message": self.welcome_message,
        }
    
    @classmethod
    def from_dict(cls, data: dict) -> "Shop":
        shop = cls(
            key=data["key"],
            name=data["name"],
        )
        shop.shop_type = ShopType(data.get("shop_type", "general"))
        shop.owner_dbref = data.get("owner_dbref", "")
        shop.owner_name = data.get("owner_name", "")
        shop.location_dbref = data.get("location_dbref", "")
        shop.status = ShopStatus(data.get("status", "open"))
        shop.inventory = data.get("inventory", {})
        shop.buy_rate = data.get("buy_rate", 0.5)
        shop.sell_markup = data.get("sell_markup", 1.0)
        shop.accepts_haggling = data.get("accepts_haggling", True)
        shop.max_haggle_discount = data.get("max_haggle_discount", 30)
        shop.faction = data.get("faction", "")
        shop.accepted_currencies = [
            CurrencyType(c) for c in data.get("accepted_currencies", ["gold"])
        ]
        shop.description = data.get("description", "")
        shop.welcome_message = data.get("welcome_message", "Welcome!")
        return shop


# =============================================================================
# SHOP PRESETS
# =============================================================================

def create_pet_shop() -> Shop:
    """Create a pet shop with default inventory."""
    shop = Shop(
        key="pet_shop",
        name="Creature Comforts Pet Shop",
        shop_type=ShopType.PET_SHOP,
        description="A shop selling pets and pet supplies.",
        welcome_message="Welcome to Creature Comforts! Looking for a new companion?",
    )
    
    # Add items
    shop.add_item(ShopItem(
        key="basic_collar",
        name="Basic Pet Collar",
        base_price=5,
        description="A simple leather collar for pets.",
    ))
    shop.add_item(ShopItem(
        key="leather_leash",
        name="Leather Leash",
        base_price=10,
        description="A sturdy leather leash.",
    ))
    shop.add_item(ShopItem(
        key="pet_treats",
        name="Training Treats",
        base_price=2,
        quantity=50,
        restock_rate=10,
        description="Tasty treats for training.",
    ))
    
    return shop


def create_tack_shop() -> Shop:
    """Create a tack shop for riding/harness equipment."""
    shop = Shop(
        key="tack_shop",
        name="Stable Supplies Tack Shop",
        shop_type=ShopType.TACK_SHOP,
        description="Equipment for mounts and beasts of burden.",
        welcome_message="Need gear for your mount? You've come to the right place!",
    )
    
    shop.add_item(ShopItem(
        key="basic_saddle",
        name="Basic Saddle",
        base_price=50,
        description="A simple riding saddle.",
    ))
    shop.add_item(ShopItem(
        key="breeding_harness",
        name="Breeding Harness",
        base_price=75,
        min_reputation=10,
        description="A harness designed for breeding.",
    ))
    shop.add_item(ShopItem(
        key="belly_sling",
        name="Belly Sling",
        base_price=100,
        min_reputation=20,
        description="A sling for carrying beneath a tauroid.",
    ))
    shop.add_item(ShopItem(
        key="bridle",
        name="Pony Bridle",
        base_price=30,
        description="A bridle with bit.",
    ))
    
    return shop


def create_clothier() -> Shop:
    """Create a clothing shop."""
    shop = Shop(
        key="clothier",
        name="Fine Fabrics Clothier",
        shop_type=ShopType.CLOTHIER,
        description="Quality clothing for all occasions.",
    )
    
    shop.add_item(ShopItem(key="shirt", name="Cotton Shirt", base_price=10))
    shop.add_item(ShopItem(key="pants", name="Cotton Pants", base_price=12))
    shop.add_item(ShopItem(key="dress", name="Simple Dress", base_price=25))
    shop.add_item(ShopItem(key="corset", name="Boned Corset", base_price=60))
    shop.add_item(ShopItem(key="stockings", name="Silk Stockings", base_price=15))
    
    return shop


def create_apothecary() -> Shop:
    """Create a potion/drug shop."""
    shop = Shop(
        key="apothecary",
        name="Mystic Brews Apothecary",
        shop_type=ShopType.APOTHECARY,
        description="Potions and elixirs for various needs.",
    )
    
    shop.add_item(ShopItem(
        key="healing_potion",
        name="Healing Potion",
        base_price=25,
        quantity=20,
        restock_rate=5,
    ))
    shop.add_item(ShopItem(
        key="stamina_potion",
        name="Stamina Elixir",
        base_price=30,
        quantity=15,
        restock_rate=3,
    ))
    shop.add_item(ShopItem(
        key="aphrodisiac",
        name="Passion Potion",
        base_price=50,
        min_reputation=10,
        quantity=10,
        restock_rate=2,
        description="Increases arousal significantly.",
    ))
    shop.add_item(ShopItem(
        key="fertility_potion",
        name="Fertility Draught",
        base_price=100,
        min_reputation=20,
        quantity=5,
        restock_rate=1,
        description="Greatly increases chance of conception.",
    ))
    
    return shop


SHOP_PRESETS = {
    "pet_shop": create_pet_shop,
    "tack_shop": create_tack_shop,
    "clothier": create_clothier,
    "apothecary": create_apothecary,
}


def create_shop_from_preset(preset_key: str) -> Optional[Shop]:
    """Create a shop from a preset."""
    creator = SHOP_PRESETS.get(preset_key)
    if creator:
        return creator()
    return None


# =============================================================================
# SHOP MANAGER
# =============================================================================

class ShopManager:
    """
    Manages all shops in the game.
    """
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._shops = {}
        return cls._instance
    
    def register_shop(self, shop: Shop) -> None:
        """Register a shop."""
        self._shops[shop.key] = shop
    
    def get_shop(self, key: str) -> Optional[Shop]:
        """Get shop by key."""
        return self._shops.get(key)
    
    def get_shops_in_location(self, location_dbref: str) -> List[Shop]:
        """Get all shops in a location."""
        return [s for s in self._shops.values() if s.location_dbref == location_dbref]
    
    def get_shops_by_type(self, shop_type: ShopType) -> List[Shop]:
        """Get all shops of a type."""
        return [s for s in self._shops.values() if s.shop_type == shop_type]
    
    def daily_restock_all(self) -> None:
        """Restock all shops."""
        for shop in self._shops.values():
            shop.daily_restock()


__all__ = [
    "ShopType",
    "ShopStatus",
    "ShopItem",
    "Shop",
    "SHOP_PRESETS",
    "create_shop_from_preset",
    "create_pet_shop",
    "create_tack_shop",
    "create_clothier",
    "create_apothecary",
    "ShopManager",
]
