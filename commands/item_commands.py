"""
Item Commands for Gilderhaven
==============================

Commands for item management.

Commands:
- inventory: View your items
- use: Use a consumable
- eat: Eat food
- equip: Wear equipment
- unequip: Remove equipment
- equipment: View worn items
- examine: Look at item details
- drop: Drop an item
- get/take: Pick up an item
"""

from evennia import Command, CmdSet
from world.items import (
    is_item, get_item_data, get_item_category, get_item_quantity,
    get_item_value, get_item_display_name,
    is_tool, get_tool_type, get_tool_tier,
    is_consumable, use_item,
    is_equipment, get_equipment_slot, equip_item, unequip_item,
    get_equipped, get_all_equipped,
    ITEM_CATEGORIES, EQUIPMENT_SLOTS, ITEM_QUALITIES
)


class CmdInventory(Command):
    """
    View your inventory.
    
    Usage:
        inventory
        inv
        i
        inventory <category>
    
    Shows all items you're carrying. Optionally filter by category:
    material, tool, consumable, equipment, etc.
    """
    
    key = "inventory"
    aliases = ["inv", "i"]
    locks = "cmd:all()"
    help_category = "Items"
    
    def func(self):
        caller = self.caller
        
        # Get all items
        items = [obj for obj in caller.contents if is_item(obj)]
        
        if not items:
            caller.msg("You aren't carrying anything.")
            return
        
        # Filter by category if specified
        filter_cat = self.args.strip().lower() if self.args else None
        if filter_cat:
            items = [i for i in items if get_item_category(i) == filter_cat]
            if not items:
                caller.msg(f"You have no {filter_cat} items.")
                return
        
        # Group by category
        by_category = {}
        for item in items:
            cat = get_item_category(item)
            if cat not in by_category:
                by_category[cat] = []
            by_category[cat].append(item)
        
        # Calculate totals
        total_weight = sum(
            (get_item_data(i).get("weight", 0) * get_item_quantity(i))
            for i in items
        )
        total_value = sum(get_item_value(i, for_sale=True) for i in items)
        
        # Build output
        lines = ["|wInventory|n"]
        lines.append("-" * 50)
        
        for cat, cat_items in sorted(by_category.items()):
            cat_name = ITEM_CATEGORIES.get(cat, cat.title())
            lines.append(f"\n|y{cat_name}:|n")
            
            for item in cat_items:
                name = get_item_display_name(item)
                data = get_item_data(item)
                weight = data.get("weight", 0) * get_item_quantity(item)
                value = get_item_value(item, for_sale=True)
                
                # Show tool durability
                extra = ""
                if is_tool(item) and item.db.tool_data:
                    dur = item.db.tool_data.get("durability", 0)
                    max_dur = item.db.tool_data.get("max_durability", 100)
                    pct = int((dur / max_dur) * 100) if max_dur > 0 else 0
                    if pct < 25:
                        extra = f" |r[{pct}%]|n"
                    elif pct < 50:
                        extra = f" |y[{pct}%]|n"
                
                lines.append(f"  {name}{extra} |x({weight:.1f} lb, {value}c)|n")
        
        lines.append("\n" + "-" * 50)
        lines.append(f"|xTotal: {len(items)} items, {total_weight:.1f} lbs, worth ~{total_value}c|n")
        
        caller.msg("\n".join(lines))


class CmdUse(Command):
    """
    Use a consumable item.
    
    Usage:
        use <item>
    
    Use potions, food, and other consumable items.
    """
    
    key = "use"
    aliases = ["drink", "consume"]
    locks = "cmd:all()"
    help_category = "Items"
    
    def func(self):
        caller = self.caller
        
        if not self.args:
            caller.msg("Use what?")
            return
        
        # Find item in inventory
        item = caller.search(self.args, location=caller, quiet=True)
        if not item:
            item = caller.search(self.args, location=caller)
            return
        
        item = item[0] if isinstance(item, list) else item
        
        if not is_item(item):
            caller.msg(f"{item.key} is not an item.")
            return
        
        if not is_consumable(item):
            caller.msg(f"You can't use {item.key}.")
            return
        
        use_item(caller, item)


class CmdEat(Command):
    """
    Eat food.
    
    Usage:
        eat <food>
    
    Eat edible items to restore hunger.
    """
    
    key = "eat"
    locks = "cmd:all()"
    help_category = "Items"
    
    def func(self):
        caller = self.caller
        
        if not self.args:
            caller.msg("Eat what?")
            return
        
        # Find item
        item = caller.search(self.args, location=caller, quiet=True)
        if not item:
            item = caller.search(self.args, location=caller)
            return
        
        item = item[0] if isinstance(item, list) else item
        
        if not is_item(item):
            caller.msg(f"{item.key} is not an item.")
            return
        
        # Check if edible
        if not item.db.consumable_data or not item.db.consumable_data.get("edible"):
            caller.msg(f"You can't eat {item.key}.")
            return
        
        use_item(caller, item)


class CmdEquip(Command):
    """
    Equip an item.
    
    Usage:
        equip <item>
        wear <item>
    
    Put on equipment like armor, jewelry, or collars.
    """
    
    key = "equip"
    aliases = ["wear", "put on"]
    locks = "cmd:all()"
    help_category = "Items"
    
    def func(self):
        caller = self.caller
        
        if not self.args:
            caller.msg("Equip what?")
            return
        
        # Find item
        item = caller.search(self.args, location=caller, quiet=True)
        if not item:
            item = caller.search(self.args, location=caller)
            return
        
        item = item[0] if isinstance(item, list) else item
        
        if not is_item(item):
            caller.msg(f"{item.key} is not an item.")
            return
        
        if not is_equipment(item):
            caller.msg(f"You can't equip {item.key}.")
            return
        
        equip_item(caller, item)


class CmdUnequip(Command):
    """
    Remove equipped item.
    
    Usage:
        unequip <item>
        remove <item>
    
    Take off equipment you're wearing.
    """
    
    key = "unequip"
    aliases = ["remove"]
    locks = "cmd:all()"
    help_category = "Items"
    
    def func(self):
        caller = self.caller
        
        if not self.args:
            caller.msg("Unequip what?")
            return
        
        # First check equipped items
        equipped = get_all_equipped(caller)
        
        search_term = self.args.strip().lower()
        found = None
        
        for slot, item in equipped.items():
            if search_term in item.key.lower() or search_term in slot.lower():
                found = item
                break
        
        if not found:
            # Try searching inventory
            item = caller.search(self.args, location=caller, quiet=True)
            if item:
                found = item[0] if isinstance(item, list) else item
        
        if not found:
            caller.msg(f"You're not wearing anything like '{self.args}'.")
            return
        
        unequip_item(caller, found)


class CmdEquipment(Command):
    """
    View equipped items.
    
    Usage:
        equipment
        eq
        worn
    
    Shows all items you currently have equipped.
    """
    
    key = "equipment"
    aliases = ["eq", "worn", "wearing"]
    locks = "cmd:all()"
    help_category = "Items"
    
    def func(self):
        caller = self.caller
        
        equipped = get_all_equipped(caller)
        
        lines = ["|wEquipment|n"]
        lines.append("-" * 40)
        
        if not equipped:
            lines.append("  You have nothing equipped.")
        else:
            for slot in EQUIPMENT_SLOTS:
                slot_name = EQUIPMENT_SLOTS[slot]
                item = equipped.get(slot)
                
                if item:
                    name = get_item_display_name(item, include_quantity=False)
                    lines.append(f"  |c{slot_name}:|n {name}")
                else:
                    lines.append(f"  |x{slot_name}: empty|n")
        
        lines.append("-" * 40)
        caller.msg("\n".join(lines))


class CmdExamine(Command):
    """
    Examine an item in detail.
    
    Usage:
        examine <item>
        exam <item>
    
    Get detailed information about an item including
    its value, weight, and special properties.
    """
    
    key = "examine"
    aliases = ["exam", "inspect"]
    locks = "cmd:all()"
    help_category = "Items"
    
    def func(self):
        caller = self.caller
        
        if not self.args:
            caller.msg("Examine what?")
            return
        
        # Search inventory first, then room
        item = caller.search(self.args, location=caller, quiet=True)
        if not item:
            item = caller.search(self.args, location=caller.location, quiet=True)
        if not item:
            caller.msg(f"You don't see '{self.args}' here.")
            return
        
        item = item[0] if isinstance(item, list) else item
        
        # Basic description
        lines = [f"|w{item.key}|n"]
        lines.append("-" * 40)
        lines.append(item.db.desc or "You see nothing special.")
        
        if is_item(item):
            data = get_item_data(item)
            lines.append("")
            
            # Category
            cat = data.get("category", "misc")
            cat_name = ITEM_CATEGORIES.get(cat, cat.title())
            lines.append(f"|yCategory:|n {cat_name}")
            
            # Quality
            quality = data.get("quality", "common")
            quality_data = ITEM_QUALITIES.get(quality, {})
            quality_name = quality_data.get("name", "Common")
            lines.append(f"|yQuality:|n {quality_name}")
            
            # Stack info
            if data.get("stackable"):
                qty = data.get("quantity", 1)
                max_stack = data.get("max_stack", 1)
                lines.append(f"|yQuantity:|n {qty}/{max_stack}")
            
            # Weight and value
            weight = data.get("weight", 0)
            value = get_item_value(item, for_sale=False)
            sell_value = get_item_value(item, for_sale=True)
            lines.append(f"|yWeight:|n {weight:.1f} lbs")
            lines.append(f"|yValue:|n {value}c (sells for {sell_value}c)")
            
            # Tool info
            if is_tool(item) and item.db.tool_data:
                lines.append("")
                lines.append("|cTool Properties:|n")
                tool_type = item.db.tool_data.get("tool_type", "unknown")
                tier = item.db.tool_data.get("tool_tier", 1)
                bonus = item.db.tool_data.get("gathering_bonus", 0)
                dur = item.db.tool_data.get("durability", 0)
                max_dur = item.db.tool_data.get("max_durability", 100)
                
                lines.append(f"  Type: {tool_type}")
                lines.append(f"  Tier: {tier}")
                if bonus:
                    lines.append(f"  Gathering Bonus: +{bonus}%")
                lines.append(f"  Durability: {dur}/{max_dur}")
            
            # Equipment info
            if is_equipment(item) and item.db.equipment_data:
                lines.append("")
                lines.append("|cEquipment Properties:|n")
                slot = item.db.equipment_data.get("slot")
                slot_name = EQUIPMENT_SLOTS.get(slot, slot)
                lines.append(f"  Slot: {slot_name}")
                
                armor = item.db.equipment_data.get("armor", 0)
                if armor:
                    lines.append(f"  Armor: +{armor}")
            
            # Consumable info
            if is_consumable(item) and item.db.consumable_data:
                lines.append("")
                lines.append("|cConsumable:|n")
                if item.db.consumable_data.get("edible"):
                    hunger = item.db.consumable_data.get("hunger_restore", 0)
                    lines.append(f"  Restores {hunger} hunger")
                if item.db.consumable_data.get("use_effect"):
                    effect = item.db.consumable_data["use_effect"]
                    lines.append(f"  Effect: {effect.get('type', 'unknown')}")
            
            # Flags
            flags = data.get("flags", [])
            if flags:
                flag_str = ", ".join(flags)
                lines.append(f"|yFlags:|n {flag_str}")
        
        lines.append("-" * 40)
        caller.msg("\n".join(lines))


class CmdDrop(Command):
    """
    Drop an item.
    
    Usage:
        drop <item>
        drop all
    
    Drop an item from your inventory onto the ground.
    """
    
    key = "drop"
    locks = "cmd:all()"
    help_category = "Items"
    
    def func(self):
        caller = self.caller
        
        if not self.args:
            caller.msg("Drop what?")
            return
        
        if not caller.location:
            caller.msg("You can't drop things here.")
            return
        
        # Find item
        item = caller.search(self.args, location=caller, quiet=True)
        if not item:
            caller.msg(f"You don't have '{self.args}'.")
            return
        
        item = item[0] if isinstance(item, list) else item
        
        # Check for no_drop flag
        if is_item(item):
            data = get_item_data(item)
            if "no_drop" in data.get("flags", []):
                caller.msg(f"You can't drop {item.key}.")
                return
        
        # Drop it
        item.move_to(caller.location, quiet=True)
        caller.msg(f"You drop {item.key}.")
        caller.location.msg_contents(
            f"{caller.key} drops {item.key}.",
            exclude=[caller]
        )


class CmdGet(Command):
    """
    Pick up an item.
    
    Usage:
        get <item>
        take <item>
        pick up <item>
    
    Pick up an item from the ground.
    """
    
    key = "get"
    aliases = ["take", "pick up", "grab"]
    locks = "cmd:all()"
    help_category = "Items"
    
    def func(self):
        caller = self.caller
        
        if not self.args:
            caller.msg("Get what?")
            return
        
        if not caller.location:
            return
        
        # Find item in room
        item = caller.search(self.args, location=caller.location, quiet=True)
        if not item:
            caller.msg(f"You don't see '{self.args}' here.")
            return
        
        item = item[0] if isinstance(item, list) else item
        
        # Make sure it's gettable (not an exit, room feature, etc.)
        if item.destination:  # It's an exit
            caller.msg("You can't pick that up.")
            return
        
        # Pick it up
        item.move_to(caller, quiet=True)
        caller.msg(f"You pick up {item.key}.")
        caller.location.msg_contents(
            f"{caller.key} picks up {item.key}.",
            exclude=[caller]
        )


# =============================================================================
# Command Set
# =============================================================================

class ItemCmdSet(CmdSet):
    """
    Commands for item management.
    """
    
    key = "items"
    priority = 1
    
    def at_cmdset_creation(self):
        self.add(CmdInventory())
        self.add(CmdUse())
        self.add(CmdEat())
        self.add(CmdEquip())
        self.add(CmdUnequip())
        self.add(CmdEquipment())
        self.add(CmdExamine())
        self.add(CmdDrop())
        self.add(CmdGet())
