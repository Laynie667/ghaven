"""
Furniture Commands for Gilderhaven
===================================

Commands for purchasing, placing, and managing furniture.

Commands:
- furniture: Main furniture command (list, buy, place, remove)
- furnish: Alias for furniture place
"""

from evennia import Command, CmdSet
from world.furniture import (
    FURNITURE_CATALOG, FURNITURE_CATEGORIES,
    get_catalog_item, list_catalog, create_furniture,
    purchase_furniture, place_furniture, remove_furniture,
    use_furniture, leave_furniture, get_occupants,
    get_available_slots, is_furniture, is_adult_furniture,
    get_furniture_for_room
)


class CmdFurniture(Command):
    """
    Manage furniture - browse catalog, purchase, and place.
    
    Usage:
        furniture                       - Show furniture in room
        furniture catalog               - Browse furniture catalog
        furniture catalog <category>    - Browse specific category
        furniture catalog adult         - Include adult furniture
        furniture info <item>           - Details about catalog item
        furniture buy <item>            - Purchase from catalog
        furniture place <furniture>     - Place owned furniture
        furniture remove <furniture>    - Pick up furniture
        furniture use <furniture>       - Use/sit on furniture
        furniture leave                 - Get off furniture
    
    Categories:
        seating, beds, tables, storage, decor, special, adult
    
    Examples:
        furniture catalog beds
        furniture buy comfortable_bed
        furniture place comfortable bed
        furniture use bed
    """
    
    key = "furniture"
    aliases = ["furn"]
    locks = "cmd:all()"
    help_category = "Home"
    
    def func(self):
        caller = self.caller
        
        if not self.args:
            self.show_room_furniture()
            return
        
        args = self.args.strip().lower()
        parts = args.split(None, 1)
        cmd = parts[0]
        subargs = parts[1] if len(parts) > 1 else ""
        
        if cmd in ("catalog", "browse", "shop", "list"):
            self.browse_catalog(subargs)
        elif cmd == "info":
            self.show_info(subargs)
        elif cmd in ("buy", "purchase"):
            self.buy_furniture(subargs)
        elif cmd == "place":
            self.place_furniture(subargs)
        elif cmd in ("remove", "pickup", "take"):
            self.remove_furniture(subargs)
        elif cmd == "use":
            self.use_furniture(subargs)
        elif cmd == "leave":
            self.leave_furniture()
        else:
            # Maybe they're trying to use/interact with furniture by name
            self.use_furniture(args)
    
    def show_room_furniture(self):
        """Show furniture in current room."""
        caller = self.caller
        room = caller.location
        
        if not room:
            caller.msg("You're not in a room.")
            return
        
        furniture = get_furniture_for_room(room)
        
        if not furniture:
            caller.msg("There's no furniture in this room.")
            caller.msg("|xUse 'furniture catalog' to browse available furniture.|n")
            return
        
        lines = ["|wFurniture in this room:|n"]
        lines.append("-" * 40)
        
        for furn in furniture:
            occupants = get_occupants(furn)
            status = ""
            
            if occupants:
                occ_names = [o.key for o in occupants]
                status = f" |c({', '.join(occ_names)})|n"
            else:
                slots = get_available_slots(furn)
                if slots:
                    capacity = len(furn.db.furniture_data.get("slots", []))
                    status = f" |g({len(slots)}/{capacity} free)|n"
            
            adult = "|r[A]|n " if is_adult_furniture(furn) else ""
            lines.append(f"  {adult}{furn.key}{status}")
        
        lines.append("-" * 40)
        lines.append("|xCommands: furniture use <name>, furniture catalog|n")
        
        caller.msg("\n".join(lines))
    
    def browse_catalog(self, args):
        """Browse the furniture catalog."""
        caller = self.caller
        
        show_adult = "adult" in args.lower()
        category = None
        
        # Parse category
        for cat in FURNITURE_CATEGORIES.keys():
            if cat in args.lower():
                category = cat
                break
        
        catalog = list_catalog(category=category, adult=show_adult)
        
        if not catalog:
            caller.msg("No furniture found matching that criteria.")
            return
        
        # Group by category
        by_category = {}
        for key, item in catalog.items():
            cat = item.get("category", "misc")
            if cat not in by_category:
                by_category[cat] = []
            by_category[cat].append((key, item))
        
        lines = ["|wFurniture Catalog:|n"]
        lines.append("-" * 50)
        
        for cat, items in sorted(by_category.items()):
            cat_name = FURNITURE_CATEGORIES.get(cat, cat.title())
            lines.append(f"\n|y{cat_name}:|n")
            
            for key, item in sorted(items, key=lambda x: x[1].get("price", 0)):
                name = item.get("key", key)
                price = item.get("price", 0)
                capacity = item.get("capacity", 0)
                
                adult = "|r[A]|n " if "adult" in item.get("flags", []) else ""
                cap_str = f" ({capacity} seats)" if capacity > 0 else ""
                
                lines.append(f"  {adult}{key:<25} |y{price:>5}g|n{cap_str}")
        
        lines.append("-" * 50)
        lines.append("|xUse 'furniture info <item>' for details.|n")
        lines.append("|xUse 'furniture buy <item>' to purchase.|n")
        
        if not show_adult:
            lines.append("|xUse 'furniture catalog adult' to include adult items.|n")
        
        caller.msg("\n".join(lines))
    
    def show_info(self, args):
        """Show details about a catalog item."""
        caller = self.caller
        
        if not args:
            caller.msg("Usage: furniture info <item>")
            return
        
        item_key = args.replace(" ", "_").lower()
        item = get_catalog_item(item_key)
        
        if not item:
            caller.msg(f"Unknown item: {args}")
            caller.msg("Use 'furniture catalog' to see available items.")
            return
        
        lines = [f"|w{item.get('key', item_key)}|n"]
        lines.append("-" * 40)
        lines.append(item.get("desc", "A piece of furniture."))
        lines.append("")
        lines.append(f"|yPrice:|n {item.get('price', 0)} gold")
        
        capacity = item.get("capacity", 0)
        if capacity > 0:
            lines.append(f"|yCapacity:|n {capacity} people")
            slots = item.get("slots", [])
            if slots:
                lines.append(f"|ySlots:|n {', '.join(slots)}")
        
        positions = item.get("supported_positions", [])
        if positions:
            lines.append(f"|yPositions:|n {', '.join(positions[:5])}")
            if len(positions) > 5:
                lines.append(f"           ...and {len(positions) - 5} more")
        
        storage = item.get("storage_slots", 0)
        if storage > 0:
            lines.append(f"|yStorage:|n {storage} slots")
        
        effects = item.get("effects", {})
        if effects:
            effect_strs = [f"{k}={v}" for k, v in effects.items()]
            lines.append(f"|yEffects:|n {', '.join(effect_strs)}")
        
        flags = item.get("flags", [])
        if flags:
            lines.append(f"|yFlags:|n {', '.join(flags)}")
        
        lines.append("-" * 40)
        lines.append(f"|xUse 'furniture buy {item_key}' to purchase.|n")
        
        caller.msg("\n".join(lines))
    
    def buy_furniture(self, args):
        """Purchase furniture from catalog."""
        caller = self.caller
        
        if not args:
            caller.msg("Usage: furniture buy <item>")
            caller.msg("Use 'furniture catalog' to see available items.")
            return
        
        item_key = args.replace(" ", "_").lower()
        
        success, msg, furniture = purchase_furniture(caller, item_key)
        caller.msg(msg)
        
        if success and furniture:
            caller.msg(f"|xUse 'furniture place {furniture.key}' to place it.|n")
    
    def place_furniture(self, args):
        """Place owned furniture in current room."""
        caller = self.caller
        room = caller.location
        
        if not args:
            caller.msg("Usage: furniture place <furniture>")
            # List furniture in inventory
            owned = [obj for obj in caller.contents if is_furniture(obj)]
            if owned:
                caller.msg("|wFurniture you're carrying:|n")
                for furn in owned:
                    caller.msg(f"  {furn.key}")
            return
        
        # Find furniture in inventory
        furniture = caller.search(args, location=caller)
        if not furniture:
            return
        
        if not is_furniture(furniture):
            caller.msg(f"{furniture.key} isn't furniture.")
            return
        
        # Check room allows placement
        if room.db.is_home or room.db.is_home_room:
            # Check ownership/permission
            from world.housing import get_permission_level, get_home_by_id, PERMISSION_LEVELS
            home = room
            if room.db.is_home_room:
                home = get_home_by_id(room.db.parent_home_id)
            
            if home:
                perm = get_permission_level(home, caller)
                perm_level = PERMISSION_LEVELS.get(perm, 0)
                if perm_level < 4:  # Need resident or higher
                    caller.msg("You need to be a resident to place furniture here.")
                    return
        
        success, msg = place_furniture(furniture, room)
        caller.msg(msg)
        
        if success:
            room.msg_contents(
                f"|c{caller.key}|n places {furniture.key} in the room.",
                exclude=[caller]
            )
    
    def remove_furniture(self, args):
        """Remove furniture from room back to inventory."""
        caller = self.caller
        room = caller.location
        
        if not args:
            caller.msg("Usage: furniture remove <furniture>")
            return
        
        furniture = caller.search(args, location=room)
        if not furniture:
            return
        
        if not is_furniture(furniture):
            caller.msg(f"{furniture.key} isn't furniture.")
            return
        
        # Check ownership/permission
        owner_id = furniture.db.owner_id
        if owner_id and owner_id != caller.id:
            if not caller.check_permstring("Admin"):
                caller.msg("You don't own this furniture.")
                return
        
        success, msg = remove_furniture(furniture, caller)
        caller.msg(msg)
        
        if success:
            room.msg_contents(
                f"|c{caller.key}|n picks up {furniture.key}.",
                exclude=[caller]
            )
    
    def use_furniture(self, args):
        """Use furniture (sit on it, etc.)."""
        caller = self.caller
        room = caller.location
        
        if not args:
            caller.msg("Usage: furniture use <furniture>")
            return
        
        furniture = caller.search(args, location=room)
        if not furniture:
            return
        
        if not is_furniture(furniture):
            caller.msg(f"You can't use {furniture.key} as furniture.")
            return
        
        success, msg = use_furniture(caller, furniture)
        caller.msg(msg)
        
        if success:
            room.msg_contents(
                f"|c{caller.key}|n uses {furniture.key}.",
                exclude=[caller]
            )
    
    def leave_furniture(self):
        """Leave current furniture."""
        caller = self.caller
        
        success, msg = leave_furniture(caller)
        caller.msg(msg)


class CmdUse(Command):
    """
    Use furniture or an interactive object.
    
    Usage:
        use <object>
    
    For furniture, this will sit/use it.
    Other objects may have their own use behavior.
    """
    
    key = "use"
    locks = "cmd:all()"
    help_category = "General"
    
    def func(self):
        caller = self.caller
        
        if not self.args:
            caller.msg("Use what?")
            return
        
        target = caller.search(self.args.strip(), location=caller.location)
        if not target:
            return
        
        # Check if it's furniture
        if is_furniture(target):
            success, msg = use_furniture(caller, target)
            caller.msg(msg)
            if success and caller.location:
                caller.location.msg_contents(
                    f"|c{caller.key}|n uses {target.key}.",
                    exclude=[caller]
                )
            return
        
        # Check if object has a use hook
        if hasattr(target, "at_use"):
            target.at_use(caller)
            return
        
        caller.msg(f"You can't figure out how to use {target.key}.")


# =============================================================================
# Command Set
# =============================================================================

class FurnitureCmdSet(CmdSet):
    """
    Commands for furniture management.
    """
    
    key = "furniture"
    priority = 1
    
    def at_cmdset_creation(self):
        self.add(CmdFurniture())
        self.add(CmdUse())
