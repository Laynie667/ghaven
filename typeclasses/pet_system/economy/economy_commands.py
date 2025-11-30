"""
Economy Commands
================

Commands for economy interactions:
- Wallet management
- Shopping
- Market and auctions
- Ownership
"""

from typing import Optional

# Evennia imports - stub for standalone testing
try:
    from evennia import Command, CmdSet
    HAS_EVENNIA = True
except ImportError:
    HAS_EVENNIA = False
    class Command:
        key = ""
        aliases = []
        locks = ""
        help_category = ""
        def parse(self): pass
        def func(self): pass
    class CmdSet:
        def at_cmdset_creation(self): pass
        def add(self, cmd): pass


# =============================================================================
# HELPER FUNCTIONS
# =============================================================================

def find_target(caller, name: str):
    """Find a character in the room by name."""
    if not name:
        return None
    
    candidates = caller.location.contents if caller.location else []
    
    for obj in candidates:
        if obj.key.lower() == name.lower():
            return obj
        if hasattr(obj, 'aliases') and name.lower() in [a.lower() for a in obj.aliases.all()]:
            return obj
    
    return None


# =============================================================================
# WALLET COMMANDS
# =============================================================================

class CmdWallet(Command):
    """
    Check your wallet balance.
    
    Usage:
      wallet
      wallet history
    """
    key = "wallet"
    aliases = ["balance", "money", "gold"]
    locks = "cmd:all()"
    help_category = "Economy"
    
    def func(self):
        if not hasattr(self.caller, 'wallet'):
            self.caller.msg("You don't have a wallet.")
            return
        
        wallet = self.caller.wallet
        
        if "history" in self.args.lower():
            # Show transaction history
            history = wallet.get_history(10)
            if not history:
                self.caller.msg("No transaction history.")
                return
            
            lines = ["=== Recent Transactions ==="]
            for txn in history:
                lines.append(f"  {txn.get_summary()}")
            
            self.caller.msg("\n".join(lines))
        else:
            # Show balance
            self.caller.msg(f"Wallet: {wallet.get_balance_display()}")


class CmdPay(Command):
    """
    Pay money to another character.
    
    Usage:
      pay <target> <amount> [currency]
      
    Examples:
      pay Luna 50
      pay Rex 10 silver
    """
    key = "pay"
    aliases = ["give money"]
    locks = "cmd:all()"
    help_category = "Economy"
    
    def parse(self):
        args = self.args.strip().split()
        self.target_name = args[0] if args else ""
        self.amount = int(args[1]) if len(args) > 1 and args[1].isdigit() else 0
        self.currency_name = args[2] if len(args) > 2 else "gold"
    
    def func(self):
        if not self.target_name or self.amount <= 0:
            self.caller.msg("Usage: pay <target> <amount> [currency]")
            return
        
        target = find_target(self.caller, self.target_name)
        if not target:
            self.caller.msg(f"Can't find '{self.target_name}' here.")
            return
        
        from .economy import CurrencyType
        
        try:
            currency = CurrencyType(self.currency_name.lower())
        except ValueError:
            self.caller.msg(f"Unknown currency: {self.currency_name}")
            return
        
        success, message = self.caller.pay(target, self.amount, currency)
        self.caller.msg(message)
        
        if success:
            from .economy import format_currency
            target.msg(f"{self.caller.key} pays you {format_currency(self.amount, currency)}.")


# =============================================================================
# SHOP COMMANDS
# =============================================================================

class CmdShop(Command):
    """
    Browse a shop's inventory.
    
    Usage:
      shop                   - List shops in room
      shop <name>           - Browse shop inventory
    """
    key = "shop"
    aliases = ["browse", "store"]
    locks = "cmd:all()"
    help_category = "Economy"
    
    def func(self):
        from .shops import ShopManager
        
        manager = ShopManager()
        
        if not self.args.strip():
            # List shops in room
            shops = manager.get_shops_in_location(self.caller.location.dbref if self.caller.location else "")
            
            if not shops:
                self.caller.msg("No shops here.")
                return
            
            lines = ["Shops here:"]
            for shop in shops:
                lines.append(f"  {shop.name} ({shop.shop_type.value})")
            
            self.caller.msg("\n".join(lines))
        else:
            # Browse specific shop
            shop_name = self.args.strip().lower()
            shops = manager.get_shops_in_location(self.caller.location.dbref if self.caller.location else "")
            
            shop = None
            for s in shops:
                if s.name.lower() == shop_name or s.key.lower() == shop_name:
                    shop = s
                    break
            
            if not shop:
                self.caller.msg(f"No shop named '{shop_name}' here.")
                return
            
            buyer_rep = getattr(self.caller, 'reputation', 0)
            self.caller.msg(shop.get_inventory_display(buyer_rep))


class CmdBuy(Command):
    """
    Buy an item from a shop.
    
    Usage:
      buy <item> from <shop>
      buy <item>              - If only one shop present
      
    Examples:
      buy basic_collar from pet_shop
      buy healing_potion
    """
    key = "buy"
    aliases = ["purchase"]
    locks = "cmd:all()"
    help_category = "Economy"
    
    def parse(self):
        args = self.args.strip()
        
        if " from " in args.lower():
            parts = args.lower().split(" from ")
            self.item_key = parts[0].strip()
            self.shop_name = parts[1].strip()
        else:
            self.item_key = args.lower()
            self.shop_name = ""
    
    def func(self):
        if not self.item_key:
            self.caller.msg("Buy what?")
            return
        
        from .shops import ShopManager
        
        manager = ShopManager()
        shops = manager.get_shops_in_location(self.caller.location.dbref if self.caller.location else "")
        
        if not shops:
            self.caller.msg("No shops here.")
            return
        
        # Find shop
        if self.shop_name:
            shop = None
            for s in shops:
                if s.name.lower() == self.shop_name or s.key.lower() == self.shop_name:
                    shop = s
                    break
            
            if not shop:
                self.caller.msg(f"No shop named '{self.shop_name}' here.")
                return
        else:
            # Use first shop or find one with item
            shop = None
            for s in shops:
                if s.get_item(self.item_key):
                    shop = s
                    break
            
            if not shop:
                self.caller.msg(f"Can't find '{self.item_key}' in any shop here.")
                return
        
        # Attempt purchase
        wallet = self.caller.wallet
        buyer_rep = getattr(self.caller, 'reputation', 0)
        
        success, message, item = shop.purchase_item(wallet, self.item_key, buyer_rep)
        
        if success:
            self.caller.save_wallet(wallet)
            # Would spawn item to inventory here
        
        self.caller.msg(message)


class CmdSell(Command):
    """
    Sell an item to a shop.
    
    Usage:
      sell <item> to <shop>
      sell <item>              - To first shop that accepts it
    """
    key = "sell"
    locks = "cmd:all()"
    help_category = "Economy"
    
    def parse(self):
        args = self.args.strip()
        
        if " to " in args.lower():
            parts = args.lower().split(" to ")
            self.item_name = parts[0].strip()
            self.shop_name = parts[1].strip()
        else:
            self.item_name = args.lower()
            self.shop_name = ""
    
    def func(self):
        if not self.item_name:
            self.caller.msg("Sell what?")
            return
        
        # Find item in inventory
        item = None
        for obj in self.caller.contents:
            if obj.key.lower() == self.item_name:
                item = obj
                break
        
        if not item:
            self.caller.msg(f"You don't have '{self.item_name}'.")
            return
        
        # Get base value
        base_value = getattr(item, 'base_value', 10)
        
        from .shops import ShopManager
        
        manager = ShopManager()
        shops = manager.get_shops_in_location(self.caller.location.dbref if self.caller.location else "")
        
        if not shops:
            self.caller.msg("No shops here.")
            return
        
        # Find shop
        shop = shops[0]  # Simplified - would match by shop type
        
        wallet = self.caller.wallet
        success, message = shop.sell_item_to_shop(wallet, item.key, base_value)
        
        if success:
            self.caller.save_wallet(wallet)
            # Would remove item from inventory here
        
        self.caller.msg(message)


class CmdHaggle(Command):
    """
    Attempt to haggle for a better price.
    
    Usage:
      haggle
      
    Must be shopping at a shop that accepts haggling.
    """
    key = "haggle"
    locks = "cmd:all()"
    help_category = "Economy"
    
    def func(self):
        # Would need to track current shopping session
        self.caller.msg("Haggling system requires active shopping session.")


# =============================================================================
# OWNERSHIP COMMANDS
# =============================================================================

class CmdClaim(Command):
    """
    Claim ownership of a character.
    
    Usage:
      claim <target> as <type>
      
    Types: pet, slave, servant, property, breeding_stock
    
    Examples:
      claim Luna as pet
      claim captured_elf as slave
    """
    key = "claim"
    aliases = ["own", "enslave"]
    locks = "cmd:all()"
    help_category = "Ownership"
    
    def parse(self):
        args = self.args.strip()
        
        if " as " in args.lower():
            parts = args.lower().split(" as ")
            self.target_name = parts[0].strip()
            self.ownership_type = parts[1].strip()
        else:
            self.target_name = args
            self.ownership_type = "slave"
    
    def func(self):
        if not self.target_name:
            self.caller.msg("Claim whom?")
            return
        
        target = find_target(self.caller, self.target_name)
        if not target:
            self.caller.msg(f"Can't find '{self.target_name}' here.")
            return
        
        from .ownership import OwnershipSystem, OwnershipType
        
        try:
            ownership_type = OwnershipType(self.ownership_type)
        except ValueError:
            valid = [t.value for t in OwnershipType]
            self.caller.msg(f"Valid types: {', '.join(valid)}")
            return
        
        success, message, record = OwnershipSystem.create_ownership(
            self.caller, target, ownership_type
        )
        
        if success and record:
            # Store record on both parties
            if hasattr(self.caller, 'add_property'):
                self.caller.add_property(record)
            if hasattr(target, 'ownership_record'):
                target.ownership_record = record
        
        self.caller.msg(message)
        
        if success:
            target.msg(f"{self.caller.key} has claimed you as their {ownership_type.value}!")
            self.caller.location.msg_contents(
                f"{self.caller.key} claims {target.key} as their {ownership_type.value}.",
                exclude=[self.caller, target]
            )


class CmdRelease(Command):
    """
    Release ownership of someone.
    
    Usage:
      release <property>
    """
    key = "release"
    aliases = ["free"]
    locks = "cmd:all()"
    help_category = "Ownership"
    
    def func(self):
        if not self.args.strip():
            self.caller.msg("Release whom?")
            return
        
        target = find_target(self.caller, self.args.strip())
        if not target:
            self.caller.msg(f"Can't find '{self.args.strip()}' here.")
            return
        
        # Check ownership
        if hasattr(self.caller, 'owns') and not self.caller.owns(target):
            self.caller.msg(f"You don't own {target.key}.")
            return
        
        # Get and update record
        record = self.caller.get_property(target.dbref) if hasattr(self.caller, 'get_property') else None
        
        if record:
            from .ownership import OwnershipSystem
            success, message = OwnershipSystem.release_ownership(record)
            
            if success:
                self.caller.remove_property(target.dbref)
                if hasattr(target, 'ownership_record'):
                    target.ownership_record = None
            
            self.caller.msg(message)
            target.msg(f"{self.caller.key} has released you from ownership.")
        else:
            self.caller.msg(f"You don't own {target.key}.")


class CmdProperties(Command):
    """
    List your owned properties.
    
    Usage:
      properties
      property <name>     - View details
    """
    key = "properties"
    aliases = ["owned", "slaves"]
    locks = "cmd:all()"
    help_category = "Ownership"
    
    def func(self):
        if not hasattr(self.caller, 'owned_properties'):
            self.caller.msg("You can't own properties.")
            return
        
        properties = self.caller.owned_properties
        
        if not properties:
            self.caller.msg("You don't own anyone.")
            return
        
        if self.args.strip():
            # Show specific property
            name = self.args.strip().lower()
            
            for record in properties:
                if record.property_name.lower() == name or record.get_display_name().lower() == name:
                    self.caller.msg(record.get_summary())
                    return
            
            self.caller.msg(f"You don't own anyone named '{name}'.")
        else:
            # List all
            lines = ["=== Your Properties ==="]
            for record in properties:
                lines.append(f"  {record.get_display_name()} ({record.ownership_type.value})")
            
            self.caller.msg("\n".join(lines))


# =============================================================================
# MARKET COMMANDS
# =============================================================================

class CmdMarket(Command):
    """
    Browse the slave market.
    
    Usage:
      market                  - View active listings
      market auctions         - View active auctions
      market list <property> <price>  - List for sale
      market auction <property> <starting_bid>  - Start auction
    """
    key = "market"
    aliases = ["slavemarket"]
    locks = "cmd:all()"
    help_category = "Economy"
    
    def parse(self):
        args = self.args.strip().split()
        self.subcommand = args[0].lower() if args else "browse"
        self.args_rest = " ".join(args[1:]) if len(args) > 1 else ""
    
    def func(self):
        from .slave_market import SlaveMarket
        
        market = SlaveMarket()
        
        if self.subcommand in ("browse", ""):
            listings = market.get_active_listings()
            
            if not listings:
                self.caller.msg("No active listings.")
                return
            
            lines = ["=== Slave Market ==="]
            for listing in listings:
                lines.append(listing.get_summary())
            
            self.caller.msg("\n".join(lines))
            
        elif self.subcommand == "auctions":
            auctions = market.get_active_auctions()
            
            if not auctions:
                self.caller.msg("No active auctions.")
                return
            
            lines = ["=== Active Auctions ==="]
            for auction in auctions:
                lines.append(auction.get_auction_summary())
                lines.append("")
            
            self.caller.msg("\n".join(lines))
            
        elif self.subcommand == "list":
            # List for sale
            parts = self.args_rest.split()
            if len(parts) < 2:
                self.caller.msg("Usage: market list <property> <price>")
                return
            
            target_name = parts[0]
            try:
                price = int(parts[1])
            except ValueError:
                self.caller.msg("Price must be a number.")
                return
            
            target = find_target(self.caller, target_name)
            if not target:
                self.caller.msg(f"Can't find '{target_name}' here.")
                return
            
            from .economy import CurrencyType
            
            success, message, listing = market.create_listing(
                self.caller, target, price, CurrencyType.GOLD
            )
            self.caller.msg(message)
            
        elif self.subcommand == "auction":
            # Start auction
            parts = self.args_rest.split()
            if len(parts) < 2:
                self.caller.msg("Usage: market auction <property> <starting_bid>")
                return
            
            target_name = parts[0]
            try:
                starting_bid = int(parts[1])
            except ValueError:
                self.caller.msg("Starting bid must be a number.")
                return
            
            target = find_target(self.caller, target_name)
            if not target:
                self.caller.msg(f"Can't find '{target_name}' here.")
                return
            
            from .economy import CurrencyType
            
            success, message, auction = market.create_auction(
                self.caller, target, starting_bid, CurrencyType.GOLD
            )
            self.caller.msg(message)
        
        else:
            self.caller.msg("Unknown subcommand. Use: browse, auctions, list, auction")


class CmdBid(Command):
    """
    Place a bid on an auction.
    
    Usage:
      bid <amount> on <auction_id>
      
    Example:
      bid 150 on LST-20240101-1234
    """
    key = "bid"
    locks = "cmd:all()"
    help_category = "Economy"
    
    def parse(self):
        args = self.args.strip()
        
        if " on " in args.lower():
            parts = args.split(" on ")
            try:
                self.amount = int(parts[0].strip())
            except ValueError:
                self.amount = 0
            self.auction_id = parts[1].strip()
        else:
            self.amount = 0
            self.auction_id = ""
    
    def func(self):
        if self.amount <= 0 or not self.auction_id:
            self.caller.msg("Usage: bid <amount> on <auction_id>")
            return
        
        from .slave_market import SlaveMarket
        
        market = SlaveMarket()
        success, message = market.place_bid(self.caller, self.auction_id, self.amount)
        self.caller.msg(message)


class CmdAppraise(Command):
    """
    Appraise a character's market value.
    
    Usage:
      appraise <target>
    """
    key = "appraise"
    aliases = ["value"]
    locks = "cmd:all()"
    help_category = "Economy"
    
    def func(self):
        if not self.args.strip():
            self.caller.msg("Appraise whom?")
            return
        
        target = find_target(self.caller, self.args.strip())
        if not target:
            self.caller.msg(f"Can't find '{self.args.strip()}' here.")
            return
        
        from .slave_market import appraise_character
        
        appraisal = appraise_character(target)
        self.caller.msg(appraisal.get_summary())


# =============================================================================
# COMMAND SET
# =============================================================================

class EconomyCmdSet(CmdSet):
    """Command set for economy."""
    
    key = "EconomyCmdSet"
    
    def at_cmdset_creation(self):
        # Wallet
        self.add(CmdWallet())
        self.add(CmdPay())
        
        # Shopping
        self.add(CmdShop())
        self.add(CmdBuy())
        self.add(CmdSell())
        self.add(CmdHaggle())
        
        # Ownership
        self.add(CmdClaim())
        self.add(CmdRelease())
        self.add(CmdProperties())
        
        # Market
        self.add(CmdMarket())
        self.add(CmdBid())
        self.add(CmdAppraise())


__all__ = [
    "CmdWallet",
    "CmdPay",
    "CmdShop",
    "CmdBuy",
    "CmdSell",
    "CmdHaggle",
    "CmdClaim",
    "CmdRelease",
    "CmdProperties",
    "CmdMarket",
    "CmdBid",
    "CmdAppraise",
    "EconomyCmdSet",
]
