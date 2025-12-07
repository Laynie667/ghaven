"""
Shop System for Gilderhaven
============================

Comprehensive shop management with:
- Shop inventories (template-based stock)
- Dynamic pricing (buy/sell markup)
- NPC shopkeeper integration
- Limited stock with restocking
- Shop specializations
- Sell interface for players

Architecture:
- Shops are data on NPCs or room objects
- Stock defined by templates
- Prices calculated from item base values
- Integration with currency and items

Usage:
    from world.shops import (
        open_shop, buy_item, sell_item,
        get_shop_inventory, setup_shop
    )
    
    # Open shop interface
    open_shop(player, shopkeeper)
    
    # Buy an item
    buy_item(player, shop, "basic_fishing_rod")
    
    # Sell an item
    sell_item(player, shop, item_object)
"""

from evennia import search_object
from evennia.utils import logger

from world.items import (
    ITEM_TEMPLATES, get_item_template, create_item, is_item,
    get_item_data, get_item_value, get_item_display_name,
    give_item, take_item, find_item_in_inventory
)
from world.currency import balance, pay, receive


# =============================================================================
# Shop Types and Templates
# =============================================================================

SHOP_TYPES = {
    "general": {
        "name": "General Store",
        "buy_markup": 1.0,      # Sells at 100% base value
        "sell_markdown": 0.5,   # Buys at 50% base value
        "description": "A shop selling a variety of common goods.",
    },
    "tools": {
        "name": "Tool Shop",
        "buy_markup": 1.1,      # 10% markup
        "sell_markdown": 0.4,   # Buys tools at 40%
        "description": "Specialized tools for every trade.",
    },
    "potions": {
        "name": "Apothecary",
        "buy_markup": 1.2,      # 20% markup for potions
        "sell_markdown": 0.3,   # Low buyback on consumables
        "description": "Potions, medicines, and alchemical supplies.",
    },
    "food": {
        "name": "Tavern/Food Vendor",
        "buy_markup": 0.8,      # Cheap food
        "sell_markdown": 0.2,   # Barely buys food back
        "description": "Fresh food and drink.",
    },
    "equipment": {
        "name": "Outfitter",
        "buy_markup": 1.15,
        "sell_markdown": 0.45,
        "description": "Armor, clothing, and accessories.",
    },
    "luxury": {
        "name": "Luxury Goods",
        "buy_markup": 1.5,      # Expensive
        "sell_markdown": 0.6,   # But buys treasures well
        "description": "Fine goods for discerning customers.",
    },
    "adult": {
        "name": "Intimate Boutique",
        "buy_markup": 1.3,
        "sell_markdown": 0.3,
        "description": "Specialty items for adults.",
        "flags": ["adult"],
    },
    "materials": {
        "name": "Material Buyer",
        "buy_markup": 2.0,      # Doesn't really sell
        "sell_markdown": 0.7,   # But pays well for materials
        "description": "Buying raw materials and resources.",
    },
}


# =============================================================================
# Shop Inventories - What each shop type stocks
# =============================================================================

SHOP_INVENTORIES = {
    "general": {
        "items": [
            # Tools - basic tier
            {"template": "basic_fishing_rod", "stock": 5, "restock_rate": 1},
            {"template": "basic_pickaxe", "stock": 5, "restock_rate": 1},
            {"template": "bug_net", "stock": 5, "restock_rate": 1},
            {"template": "foraging_basket", "stock": 5, "restock_rate": 1},
            {"template": "beach_bucket", "stock": 5, "restock_rate": 1},
            # Basic consumables
            {"template": "bread", "stock": 20, "restock_rate": 5},
            {"template": "health_potion_minor", "stock": 10, "restock_rate": 2},
            # Basic equipment
            {"template": "leather_gloves", "stock": 3, "restock_rate": 1},
            {"template": "work_boots", "stock": 3, "restock_rate": 1},
        ],
        "buys_categories": ["material", "junk", "treasure"],
    },
    
    "tools": {
        "items": [
            # Fishing
            {"template": "basic_fishing_rod", "stock": 5, "restock_rate": 2},
            {"template": "quality_fishing_rod", "stock": 3, "restock_rate": 1},
            {"template": "master_fishing_rod", "stock": 1, "restock_rate": 0},
            # Mining
            {"template": "basic_pickaxe", "stock": 5, "restock_rate": 2},
            {"template": "quality_pickaxe", "stock": 3, "restock_rate": 1},
            {"template": "master_pickaxe", "stock": 1, "restock_rate": 0},
            # Other
            {"template": "bug_net", "stock": 5, "restock_rate": 2},
            {"template": "quality_bug_net", "stock": 3, "restock_rate": 1},
            {"template": "foraging_basket", "stock": 5, "restock_rate": 2},
            {"template": "herbalist_satchel", "stock": 3, "restock_rate": 1},
            {"template": "beach_bucket", "stock": 5, "restock_rate": 2},
        ],
        "buys_categories": ["tool"],
    },
    
    "potions": {
        "items": [
            {"template": "health_potion_minor", "stock": 20, "restock_rate": 5},
            {"template": "health_potion_major", "stock": 10, "restock_rate": 2},
            {"template": "stamina_potion", "stock": 15, "restock_rate": 3},
            {"template": "antidote", "stock": 10, "restock_rate": 2},
            {"template": "aphrodisiac_potion", "stock": 5, "restock_rate": 1, "flags": ["adult"]},
        ],
        "buys_categories": ["consumable"],
        "buys_subcategories": ["herb", "potion"],
    },
    
    "food": {
        "items": [
            {"template": "bread", "stock": 50, "restock_rate": 20},
            {"template": "cooked_fish", "stock": 20, "restock_rate": 5},
            {"template": "ale", "stock": 30, "restock_rate": 10},
        ],
        "buys_categories": [],
        "buys_subcategories": ["fish", "food_raw"],
    },
    
    "equipment": {
        "items": [
            {"template": "leather_gloves", "stock": 5, "restock_rate": 2},
            {"template": "work_boots", "stock": 5, "restock_rate": 2},
            {"template": "simple_ring", "stock": 3, "restock_rate": 1},
        ],
        "buys_categories": ["equipment"],
    },
    
    "adult": {
        "items": [
            {"template": "collar_leather", "stock": 5, "restock_rate": 1},
            {"template": "collar_elegant", "stock": 2, "restock_rate": 0},
            {"template": "aphrodisiac_potion", "stock": 10, "restock_rate": 2},
        ],
        "buys_categories": ["adult"],
        "flags": ["adult"],
    },
    
    "materials": {
        "items": [],  # Doesn't sell much
        "buys_categories": ["material", "treasure"],
    },
}


# =============================================================================
# Shop Setup and Management
# =============================================================================

def setup_shop(obj, shop_type, custom_inventory=None):
    """
    Set up a shop on an NPC or object.
    
    Args:
        obj: The NPC or object to make a shop
        shop_type: Key from SHOP_TYPES
        custom_inventory: Optional custom stock list
    
    Returns:
        bool: Success
    """
    shop_data = SHOP_TYPES.get(shop_type)
    if not shop_data:
        return False
    
    inventory_data = SHOP_INVENTORIES.get(shop_type, {"items": [], "buys_categories": []})
    
    obj.db.shop_data = {
        "shop_type": shop_type,
        "name": shop_data["name"],
        "buy_markup": shop_data["buy_markup"],
        "sell_markdown": shop_data["sell_markdown"],
        "description": shop_data.get("description", ""),
        "flags": shop_data.get("flags", []),
    }
    
    # Initialize stock from template
    obj.db.shop_stock = {}
    items_list = custom_inventory if custom_inventory else inventory_data.get("items", [])
    
    for item_entry in items_list:
        template_key = item_entry["template"]
        obj.db.shop_stock[template_key] = {
            "current_stock": item_entry.get("stock", 10),
            "max_stock": item_entry.get("stock", 10),
            "restock_rate": item_entry.get("restock_rate", 1),
            "flags": item_entry.get("flags", []),
        }
    
    obj.db.shop_buys = {
        "categories": inventory_data.get("buys_categories", []),
        "subcategories": inventory_data.get("buys_subcategories", []),
        "templates": inventory_data.get("buys_templates", []),
    }
    
    obj.tags.add("shop", category="object_type")
    
    return True


def is_shop(obj):
    """Check if object is a shop."""
    return obj.tags.has("shop", category="object_type")


def get_shop_data(obj):
    """Get shop configuration."""
    return obj.db.shop_data or {}


def get_shop_stock(obj):
    """Get current shop stock."""
    return obj.db.shop_stock or {}


# =============================================================================
# Pricing Functions
# =============================================================================

def get_buy_price(shop, template_key):
    """
    Get the price to buy an item from a shop.
    
    Args:
        shop: The shop object
        template_key: Item template key
    
    Returns:
        int: Price in coins, or 0 if not for sale
    """
    shop_data = get_shop_data(shop)
    stock = get_shop_stock(shop)
    
    if template_key not in stock:
        return 0
    
    if stock[template_key].get("current_stock", 0) <= 0:
        return 0
    
    template = get_item_template(template_key)
    if not template:
        return 0
    
    base_value = template.get("base_value", 0)
    markup = shop_data.get("buy_markup", 1.0)
    
    return max(1, int(base_value * markup))


def get_sell_price(shop, item):
    """
    Get the price a shop will pay for an item.
    
    Args:
        shop: The shop object
        item: The item object
    
    Returns:
        int: Price in coins, or 0 if shop won't buy
    """
    if not is_item(item):
        return 0
    
    shop_data = get_shop_data(shop)
    buys = shop.db.shop_buys or {}
    item_data = get_item_data(item)
    
    # Check if shop buys this category
    category = item_data.get("category")
    subcategory = item_data.get("subcategory")
    template = item.db.item_template
    
    will_buy = False
    
    if category in buys.get("categories", []):
        will_buy = True
    elif subcategory in buys.get("subcategories", []):
        will_buy = True
    elif template in buys.get("templates", []):
        will_buy = True
    
    if not will_buy:
        return 0
    
    # Check for no_sell flag
    if "no_sell" in item_data.get("flags", []):
        return 0
    
    # Calculate price
    base_value = get_item_value(item, for_sale=False)
    markdown = shop_data.get("sell_markdown", 0.5)
    
    return max(1, int(base_value * markdown))


# =============================================================================
# Shop Interface
# =============================================================================

def get_shop_inventory_display(shop, viewer, show_adult=False):
    """
    Get formatted shop inventory for display.
    
    Args:
        shop: The shop object
        viewer: Who's viewing
        show_adult: Include adult items
    
    Returns:
        str: Formatted inventory
    """
    shop_data = get_shop_data(shop)
    stock = get_shop_stock(shop)
    
    lines = []
    lines.append(f"|w{shop_data.get('name', 'Shop')}|n")
    lines.append(shop_data.get("description", ""))
    lines.append("-" * 50)
    lines.append("|yFor Sale:|n")
    lines.append("")
    
    # Group by category
    by_category = {}
    for template_key, stock_data in stock.items():
        template = get_item_template(template_key)
        if not template:
            continue
        
        # Skip adult items if not showing
        if not show_adult and "adult" in stock_data.get("flags", []):
            continue
        if not show_adult and "adult" in template.get("flags", []):
            continue
        
        current = stock_data.get("current_stock", 0)
        if current <= 0:
            continue
        
        cat = template.get("category", "misc")
        if cat not in by_category:
            by_category[cat] = []
        
        price = get_buy_price(shop, template_key)
        by_category[cat].append({
            "key": template_key,
            "name": template.get("key", template_key),
            "price": price,
            "stock": current,
        })
    
    if not by_category:
        lines.append("  |xNothing for sale.|n")
    else:
        for cat, items in sorted(by_category.items()):
            lines.append(f"|c{cat.title()}:|n")
            for item in items:
                stock_str = f"x{item['stock']}" if item['stock'] < 99 else ""
                lines.append(f"  |w{item['name']}|n - {item['price']}c {stock_str}")
            lines.append("")
    
    lines.append("-" * 50)
    lines.append("|xUse 'buy <item>' to purchase.|n")
    lines.append("|xUse 'sell <item>' to sell from inventory.|n")
    
    return "\n".join(lines)


def open_shop(character, shop):
    """
    Open shop interface for a character.
    
    Args:
        character: The customer
        shop: The shop object/NPC
    """
    if not is_shop(shop):
        character.msg(f"{shop.key} doesn't have anything for sale.")
        return
    
    # Store current shop for buy/sell commands
    character.db.current_shop = shop.id
    
    # Show inventory
    show_adult = character.db.show_adult_content if hasattr(character.db, 'show_adult_content') else False
    display = get_shop_inventory_display(shop, character, show_adult)
    character.msg(display)


def close_shop(character):
    """Close shop interface."""
    character.db.current_shop = None


def get_current_shop(character):
    """Get the shop a character has open."""
    shop_id = character.db.current_shop
    if not shop_id:
        return None
    
    try:
        from evennia.objects.models import ObjectDB
        return ObjectDB.objects.get(id=shop_id)
    except:
        return None


# =============================================================================
# Buy/Sell Functions
# =============================================================================

def buy_item(character, shop, template_key, quantity=1):
    """
    Buy an item from a shop.
    
    Args:
        character: The buyer
        shop: The shop
        template_key: Item template to buy
        quantity: How many
    
    Returns:
        tuple: (success, message)
    """
    if not is_shop(shop):
        return (False, "This isn't a shop.")
    
    stock = get_shop_stock(shop)
    
    # Check if item is in stock
    if template_key not in stock:
        return (False, "That item isn't sold here.")
    
    current_stock = stock[template_key].get("current_stock", 0)
    if current_stock <= 0:
        return (False, "That item is out of stock.")
    
    if quantity > current_stock:
        return (False, f"Only {current_stock} in stock.")
    
    # Get price
    unit_price = get_buy_price(shop, template_key)
    total_price = unit_price * quantity
    
    # Check if buyer can afford
    buyer_balance = balance(character)
    if buyer_balance < total_price:
        return (False, f"You can't afford that. (Need {total_price}c, have {buyer_balance}c)")
    
    # Process transaction
    if not pay(character, total_price):
        return (False, "Transaction failed.")
    
    # Reduce stock
    shop.db.shop_stock[template_key]["current_stock"] = current_stock - quantity
    
    # Give item to buyer
    template = get_item_template(template_key)
    item_name = template.get("key", template_key) if template else template_key
    
    for _ in range(quantity):
        give_item(character, template_key)
    
    return (True, f"You bought {item_name}" + (f" x{quantity}" if quantity > 1 else "") + f" for {total_price}c.")


def sell_item(character, shop, item, quantity=1):
    """
    Sell an item to a shop.
    
    Args:
        character: The seller
        shop: The shop
        item: Item object to sell
        quantity: How many (for stacks)
    
    Returns:
        tuple: (success, message)
    """
    if not is_shop(shop):
        return (False, "This isn't a shop.")
    
    if not is_item(item):
        return (False, "That's not an item.")
    
    # Get price
    unit_price = get_sell_price(shop, item)
    if unit_price <= 0:
        return (False, f"This shop doesn't buy {item.key}.")
    
    # Check quantity for stacks
    item_data = get_item_data(item)
    if item_data.get("stackable"):
        current_qty = item_data.get("quantity", 1)
        if quantity > current_qty:
            return (False, f"You only have {current_qty}.")
        total_price = unit_price * quantity
    else:
        quantity = 1
        total_price = unit_price
    
    # Process transaction
    item_name = item.key
    
    # Remove item from inventory
    from world.items import remove_from_stack
    if item_data.get("stackable"):
        removed = remove_from_stack(item, quantity)
    else:
        item.delete()
        removed = 1
    
    # Pay seller
    receive(character, total_price)
    
    return (True, f"You sold {item_name}" + (f" x{quantity}" if quantity > 1 else "") + f" for {total_price}c.")


# =============================================================================
# Stock Management
# =============================================================================

def restock_shop(shop):
    """
    Restock a shop's inventory.
    
    Should be called periodically (e.g., daily).
    
    Args:
        shop: The shop to restock
    """
    if not is_shop(shop):
        return
    
    stock = get_shop_stock(shop)
    
    for template_key, stock_data in stock.items():
        current = stock_data.get("current_stock", 0)
        maximum = stock_data.get("max_stock", 10)
        rate = stock_data.get("restock_rate", 1)
        
        if current < maximum and rate > 0:
            new_stock = min(maximum, current + rate)
            shop.db.shop_stock[template_key]["current_stock"] = new_stock


def restock_all_shops():
    """Restock all shops in the game."""
    shops = search_object(None, typeclass="typeclasses.characters.Character")
    for obj in shops:
        if is_shop(obj):
            restock_shop(obj)


# =============================================================================
# Shop NPC Templates
# =============================================================================

SHOPKEEPER_TEMPLATES = {
    "general_merchant": {
        "key": "General Merchant",
        "aliases": ["merchant", "shopkeeper"],
        "desc": """
A friendly merchant stands behind the counter, ready to assist.
They have an easy smile and the practiced patience of someone who's
dealt with every kind of customer.
""",
        "shop_type": "general",
        "dialogue_root": "shopkeeper_greeting",
    },
    
    "tool_vendor": {
        "key": "Tool Vendor",
        "aliases": ["vendor", "tool seller"],
        "desc": """
A weathered craftsperson tends this stall, surrounded by tools of
every variety. Their hands are calloused from years of honest work.
""",
        "shop_type": "tools",
        "dialogue_root": "tool_vendor_greeting",
    },
    
    "apothecary": {
        "key": "Apothecary",
        "aliases": ["alchemist", "potion seller"],
        "desc": """
The apothecary peers at you through thick spectacles, surrounded by
bubbling vials and dried herbs. The air smells of strange botanicals.
""",
        "shop_type": "potions",
        "dialogue_root": "apothecary_greeting",
    },
    
    "tavern_keeper": {
        "key": "Tavern Keeper",
        "aliases": ["barkeep", "innkeeper"],
        "desc": """
The tavern keeper wipes down the bar with a practiced hand, nodding
as you approach. They've heard every story and seen every type.
""",
        "shop_type": "food",
        "dialogue_root": "tavern_greeting",
    },
    
    "material_buyer": {
        "key": "Resource Buyer",
        "aliases": ["buyer", "trader"],
        "desc": """
A shrewd-looking trader examines samples with a jeweler's loupe.
They buy raw materials at fair prices - if you have what they want.
""",
        "shop_type": "materials",
        "dialogue_root": "buyer_greeting",
    },
}


# =============================================================================
# Shop Dialogues
# =============================================================================

SHOP_DIALOGUES = {
    "shopkeeper_greeting": {
        "text": """
"Welcome, welcome! Take a look around - I've got a little bit of
everything. Tools, supplies, the essentials."

They gesture at the goods on display.

"What can I help you with today?"
""",
        "choices": [
            {
                "text": "Show me what you have for sale.",
                "next": None,
                "action": "open_shop",
            },
            {
                "text": "I have some things to sell.",
                "next": "shopkeeper_selling",
            },
            {
                "text": "Just looking, thanks.",
                "next": None,
                "exit_text": "\"Take your time! I'll be here if you need anything.\"",
            },
        ],
    },
    
    "shopkeeper_selling": {
        "text": """
"Buying, eh? Let me see what you've got."

They lean forward with interest.

"I'll take most common goods - materials, tools, odds and ends. 
Show me your inventory and I'll make you an offer."
""",
        "choices": [
            {
                "text": "Open selling interface.",
                "next": None,
                "action": "open_shop",
            },
            {
                "text": "Never mind.",
                "next": None,
                "exit_text": "\"No problem. Come back if you change your mind.\"",
            },
        ],
    },
    
    "tool_vendor_greeting": {
        "text": """
"Good tools make good work." The vendor sets down a file and looks
up at you. "I've got the best in the Grove - fishing rods, pickaxes,
nets, baskets. All hand-crafted."

"What do you need?"
""",
        "choices": [
            {
                "text": "Show me your tools.",
                "next": None,
                "action": "open_shop",
            },
            {
                "text": "What's your best equipment?",
                "next": "tool_vendor_best",
            },
            {
                "text": "Just browsing.",
                "next": None,
                "exit_text": "\"Take a look around. Quality speaks for itself.\"",
            },
        ],
    },
    
    "tool_vendor_best": {
        "text": """
"Ah, you want the good stuff." They lean in conspiratorially.

"I've got master-quality tools - fishing rods that practically catch
fish themselves, pickaxes that bite through stone like butter. Not
cheap, mind you, but they last forever and work twice as well."

"The basic gear will get you started, but if you're serious about
gathering... you want the master tier."
""",
        "choices": [
            {
                "text": "Show me everything.",
                "next": None,
                "action": "open_shop",
            },
            {
                "text": "I'll start with basic gear.",
                "next": None,
                "action": "open_shop",
            },
        ],
    },
    
    "apothecary_greeting": {
        "text": """
The apothecary looks up from a bubbling concoction.

"Hmm? Oh, a customer. Yes, yes." They wave vaguely at the shelves.
"Potions, medicines, remedies. Health, stamina, cures for various...
afflictions."

They peer at you over their spectacles.

"What ails you?"
""",
        "choices": [
            {
                "text": "I need healing potions.",
                "next": None,
                "action": "open_shop",
            },
            {
                "text": "Do you have anything... special?",
                "next": "apothecary_special",
            },
            {
                "text": "Nothing right now.",
                "next": None,
                "exit_text": "\"Mm. Come back when something ails you. Something always does, eventually.\"",
            },
        ],
    },
    
    "apothecary_special": {
        "text": """
The apothecary's eyebrows rise slightly.

"Special? I have... a few things. Not on the main shelves."

They glance around and lower their voice.

"Aphrodisiacs. Sensitivity enhancers. Things for... adult pursuits.
All perfectly safe, mind you. Just... discreet."

"Interested?"
""",
        "choices": [
            {
                "text": "Show me everything, including those.",
                "next": None,
                "action": "open_shop_adult",
            },
            {
                "text": "Just the regular potions, please.",
                "next": None,
                "action": "open_shop",
            },
        ],
    },
    
    "tavern_greeting": {
        "text": """
"What'll it be?" The tavern keeper sets down a glass and looks at
you expectantly.

"Got ale, got food, got a warm fire. Not much else, but what else
do you need?"
""",
        "choices": [
            {
                "text": "I'll take some food and drink.",
                "next": None,
                "action": "open_shop",
            },
            {
                "text": "Just passing through.",
                "next": None,
                "exit_text": "\"Suit yourself. Door's always open.\"",
            },
        ],
    },
    
    "buyer_greeting": {
        "text": """
The trader looks up from examining a gemstone.

"You have materials to sell? I buy ore, herbs, fish, shells -
anything raw that craftspeople need."

They set down the loupe.

"I pay fair prices. Better than most. What have you got?"
""",
        "choices": [
            {
                "text": "Let me show you what I have.",
                "next": None,
                "action": "open_shop",
            },
            {
                "text": "What pays the best?",
                "next": "buyer_best",
            },
            {
                "text": "Nothing right now.",
                "next": None,
                "exit_text": "\"Come back when your pockets are full. I'll be here.\"",
            },
        ],
    },
    
    "buyer_best": {
        "text": """
"Best prices?" They tick off on their fingers.

"Ore - especially silver and gold. Gems, always. Pearls from the
river. Rare moths and butterflies fetch good coin too."

"The common stuff - berries, basic fish, shells - I'll take it, but
don't expect to get rich on it."

"Find me the rare materials and we'll both do well."
""",
        "choices": [
            {
                "text": "Let's see what I can sell.",
                "next": None,
                "action": "open_shop",
            },
            {
                "text": "Good to know. I'll be back.",
                "next": None,
                "exit_text": "\"Looking forward to it. Good hunting.\"",
            },
        ],
    },
}
