"""
Shop Commands for Gilderhaven
==============================

Commands for shopping.

Commands:
- shop: Open shop interface / list shops
- buy: Purchase an item
- sell: Sell an item
- browse: View shop inventory
"""

from evennia import Command, CmdSet
from world.shops import (
    is_shop, open_shop, close_shop, get_current_shop,
    buy_item, sell_item, get_shop_data, get_shop_stock,
    get_buy_price, get_sell_price, get_shop_inventory_display,
    ITEM_TEMPLATES
)
from world.items import (
    is_item, get_item_data, get_item_display_name, get_item_value
)
from world.npcs import is_npc
from world.currency import balance


class CmdShop(Command):
    """
    Open a shop or view shop inventory.
    
    Usage:
        shop              - Open nearby shop or list shops
        shop <shopkeeper> - Open specific shop
        browse            - Same as shop
    
    Opens the shop interface where you can buy and sell items.
    """
    
    key = "shop"
    aliases = ["browse", "store"]
    locks = "cmd:all()"
    help_category = "Economy"
    
    def func(self):
        caller = self.caller
        
        if self.args:
            # Open specific shop
            target = caller.search(self.args.strip(), location=caller.location)
            if not target:
                return
            
            if not is_shop(target):
                caller.msg(f"{target.key} doesn't run a shop.")
                return
            
            open_shop(caller, target)
            return
        
        # Check if already in a shop
        current = get_current_shop(caller)
        if current:
            open_shop(caller, current)
            return
        
        # Find shops in room
        if not caller.location:
            caller.msg("You can't shop here.")
            return
        
        shops = [obj for obj in caller.location.contents if is_shop(obj)]
        
        if not shops:
            caller.msg("There are no shops here.")
            return
        
        if len(shops) == 1:
            # Only one shop, open it
            open_shop(caller, shops[0])
        else:
            # Multiple shops, list them
            caller.msg("|wShops here:|n")
            for shop in shops:
                shop_data = get_shop_data(shop)
                shop_name = shop_data.get("name", "Shop")
                caller.msg(f"  |c{shop.key}|n - {shop_name}")
            caller.msg("|xUse 'shop <name>' to open a specific shop.|n")


class CmdBuy(Command):
    """
    Buy an item from a shop.
    
    Usage:
        buy <item>
        buy <quantity> <item>
    
    Examples:
        buy fishing rod
        buy 5 bread
    
    You must have a shop open (use 'shop' command first).
    """
    
    key = "buy"
    aliases = ["purchase"]
    locks = "cmd:all()"
    help_category = "Economy"
    
    def func(self):
        caller = self.caller
        
        if not self.args:
            caller.msg("Buy what?")
            return
        
        # Get current shop
        shop = get_current_shop(caller)
        if not shop:
            # Try to find a shop in room
            if caller.location:
                shops = [obj for obj in caller.location.contents if is_shop(obj)]
                if len(shops) == 1:
                    shop = shops[0]
        
        if not shop:
            caller.msg("You need to open a shop first. Use 'shop' command.")
            return
        
        # Parse quantity and item name
        args = self.args.strip().split()
        quantity = 1
        
        if args[0].isdigit():
            quantity = int(args[0])
            item_name = " ".join(args[1:])
        else:
            item_name = " ".join(args)
        
        if not item_name:
            caller.msg("Buy what?")
            return
        
        # Find matching item in shop stock
        stock = get_shop_stock(shop)
        item_name_lower = item_name.lower()
        
        matching_key = None
        for template_key in stock.keys():
            template = ITEM_TEMPLATES.get(template_key)
            if not template:
                continue
            
            # Check template key
            if item_name_lower == template_key.replace("_", " "):
                matching_key = template_key
                break
            
            # Check item name
            if item_name_lower == template.get("key", "").lower():
                matching_key = template_key
                break
            
            # Check aliases
            aliases = template.get("aliases", [])
            if item_name_lower in [a.lower() for a in aliases]:
                matching_key = template_key
                break
            
            # Partial match
            if item_name_lower in template.get("key", "").lower():
                matching_key = template_key
                # Don't break - might find exact match
        
        if not matching_key:
            caller.msg(f"'{item_name}' isn't sold here.")
            return
        
        # Try to buy
        success, message = buy_item(caller, shop, matching_key, quantity)
        caller.msg(message)
        
        if success:
            # Show remaining balance
            caller.msg(f"|xBalance: {balance(caller)}c|n")


class CmdSell(Command):
    """
    Sell an item to a shop.
    
    Usage:
        sell <item>
        sell <quantity> <item>
        sell all <item>
    
    Examples:
        sell herbs
        sell 10 copper ore
        sell all fish
    
    You must have a shop open (use 'shop' command first).
    """
    
    key = "sell"
    locks = "cmd:all()"
    help_category = "Economy"
    
    def func(self):
        caller = self.caller
        
        if not self.args:
            caller.msg("Sell what?")
            return
        
        # Get current shop
        shop = get_current_shop(caller)
        if not shop:
            if caller.location:
                shops = [obj for obj in caller.location.contents if is_shop(obj)]
                if len(shops) == 1:
                    shop = shops[0]
        
        if not shop:
            caller.msg("You need to open a shop first. Use 'shop' command.")
            return
        
        # Parse quantity and item name
        args = self.args.strip().split()
        quantity = 1
        sell_all = False
        
        if args[0].lower() == "all":
            sell_all = True
            item_name = " ".join(args[1:])
        elif args[0].isdigit():
            quantity = int(args[0])
            item_name = " ".join(args[1:])
        else:
            item_name = " ".join(args)
        
        if not item_name:
            caller.msg("Sell what?")
            return
        
        # Find item in inventory
        item = caller.search(item_name, location=caller, quiet=True)
        if not item:
            caller.msg(f"You don't have '{item_name}'.")
            return
        
        item = item[0] if isinstance(item, list) else item
        
        if not is_item(item):
            caller.msg(f"You can't sell {item.key}.")
            return
        
        # Check price first
        price = get_sell_price(shop, item)
        if price <= 0:
            caller.msg(f"This shop doesn't buy {item.key}.")
            return
        
        # Handle quantity for stacks
        item_data = get_item_data(item)
        if sell_all and item_data.get("stackable"):
            quantity = item_data.get("quantity", 1)
        
        # Try to sell
        success, message = sell_item(caller, shop, item, quantity)
        caller.msg(message)
        
        if success:
            caller.msg(f"|xBalance: {balance(caller)}c|n")


class CmdValue(Command):
    """
    Check how much an item is worth.
    
    Usage:
        value <item>
        appraise <item>
    
    Shows the buy price (from shops) and sell price (to shops).
    """
    
    key = "value"
    aliases = ["appraise", "price"]
    locks = "cmd:all()"
    help_category = "Economy"
    
    def func(self):
        caller = self.caller
        
        if not self.args:
            caller.msg("Value what?")
            return
        
        # Find item
        item = caller.search(self.args.strip(), location=caller, quiet=True)
        if not item:
            item = caller.search(self.args.strip(), location=caller.location, quiet=True)
        
        if not item:
            caller.msg(f"You don't see '{self.args}'.")
            return
        
        item = item[0] if isinstance(item, list) else item
        
        if not is_item(item):
            caller.msg(f"{item.key} has no trade value.")
            return
        
        # Get base value
        from world.items import get_item_value, ITEM_QUALITIES
        item_data = get_item_data(item)
        
        base_value = get_item_value(item, for_sale=False)
        sell_value = get_item_value(item, for_sale=True)
        
        lines = [f"|wValue of {item.key}:|n"]
        lines.append(f"  Base value: {base_value}c")
        lines.append(f"  Typical sell price: ~{sell_value}c")
        
        # If shop is open, show specific price
        shop = get_current_shop(caller)
        if shop:
            shop_price = get_sell_price(shop, item)
            if shop_price > 0:
                lines.append(f"  |yThis shop pays: {shop_price}c|n")
            else:
                lines.append(f"  |xThis shop doesn't buy this item.|n")
        
        # Show quantity if stacked
        if item_data.get("stackable"):
            qty = item_data.get("quantity", 1)
            if qty > 1:
                lines.append(f"  Stack of {qty} = ~{sell_value}c total")
        
        caller.msg("\n".join(lines))


class CmdLeaveShop(Command):
    """
    Leave the current shop.
    
    Usage:
        leave shop
        close shop
    
    Closes the shop interface.
    """
    
    key = "leave shop"
    aliases = ["close shop", "exit shop"]
    locks = "cmd:all()"
    help_category = "Economy"
    
    def func(self):
        caller = self.caller
        
        shop = get_current_shop(caller)
        if not shop:
            caller.msg("You don't have a shop open.")
            return
        
        close_shop(caller)
        caller.msg("You step away from the shop.")


class CmdBalance(Command):
    """
    Check your money.
    
    Usage:
        balance
        money
        gold
    
    Shows how much currency you have.
    """
    
    key = "balance"
    aliases = ["money", "gold", "coins", "wealth"]
    locks = "cmd:all()"
    help_category = "Economy"
    
    def func(self):
        caller = self.caller
        current = balance(caller)
        caller.msg(f"|yYou have {current} coins.|n")


# =============================================================================
# Command Set
# =============================================================================

class ShopCmdSet(CmdSet):
    """
    Commands for shopping.
    """
    
    key = "shops"
    priority = 1
    
    def at_cmdset_creation(self):
        self.add(CmdShop())
        self.add(CmdBuy())
        self.add(CmdSell())
        self.add(CmdValue())
        self.add(CmdLeaveShop())
        self.add(CmdBalance())
