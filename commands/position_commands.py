"""
Position Commands for Gilderhaven
==================================

Commands for changing character positions and interacting with
furniture and partners.

Commands:
- sit: Sit down (on ground or furniture)
- stand: Stand up
- kneel: Kneel
- lie/lay: Lie down
- position: Set specific position
- positions: List available positions
"""

from evennia import Command, CmdSet
from world.positions import (
    POSITIONS, POSITION_CATEGORIES,
    get_position, get_position_type, get_position_display,
    set_position, clear_position, is_restrained,
    is_standing, can_move, list_positions
)


class CmdSit(Command):
    """
    Sit down on the ground or on furniture.
    
    Usage:
        sit                 - Sit on the ground
        sit <furniture>     - Sit on specific furniture
        sit on <furniture>  - Same as above
    
    Examples:
        sit
        sit chair
        sit on the couch
    """
    
    key = "sit"
    aliases = ["seat"]
    locks = "cmd:all()"
    help_category = "Positions"
    
    def func(self):
        caller = self.caller
        
        # Check if restrained
        if is_restrained(caller):
            caller.msg("You can't move - you're restrained!")
            return
        
        args = self.args.strip()
        
        # Remove "on " prefix if present
        if args.lower().startswith("on "):
            args = args[3:].strip()
        
        if args:
            # Try to find furniture
            furniture = caller.search(args, location=caller.location)
            if not furniture:
                return
            
            from world.furniture import is_furniture, use_furniture
            if not is_furniture(furniture):
                caller.msg(f"You can't sit on {furniture.key}.")
                return
            
            success, msg = use_furniture(caller, furniture, position="seated")
            caller.msg(msg)
        else:
            # Sit on ground
            success, msg = set_position(caller, "sitting")
            if not success:
                caller.msg(msg)


class CmdStand(Command):
    """
    Stand up from your current position.
    
    Usage:
        stand
        stand up
    
    This will release you from furniture but not from restraints.
    """
    
    key = "stand"
    aliases = ["stand up", "rise", "get up"]
    locks = "cmd:all()"
    help_category = "Positions"
    
    def func(self):
        caller = self.caller
        
        if is_standing(caller):
            caller.msg("You're already standing.")
            return
        
        success, msg = clear_position(caller)
        caller.msg(msg)


class CmdKneel(Command):
    """
    Kneel down.
    
    Usage:
        kneel                   - Kneel on the ground
        kneel <furniture>       - Kneel on/at furniture
        kneel before <person>   - Kneel before someone
    
    Examples:
        kneel
        kneel cushion
        kneel before Master
    """
    
    key = "kneel"
    locks = "cmd:all()"
    help_category = "Positions"
    
    def func(self):
        caller = self.caller
        
        if is_restrained(caller):
            caller.msg("You can't move - you're restrained!")
            return
        
        args = self.args.strip()
        
        # Check for "before <person>"
        if args.lower().startswith("before "):
            target_name = args[7:].strip()
            target = caller.search(target_name, location=caller.location)
            if not target:
                return
            
            success, msg = set_position(caller, "kneeling_before", partner=target)
            if not success:
                caller.msg(msg)
            return
        
        # Check for furniture
        if args:
            furniture = caller.search(args, location=caller.location)
            if not furniture:
                return
            
            from world.furniture import is_furniture, use_furniture
            if is_furniture(furniture):
                success, msg = use_furniture(caller, furniture, position="kneeling")
                caller.msg(msg)
                return
        
        # Just kneel on ground
        success, msg = set_position(caller, "kneeling")
        if not success:
            caller.msg(msg)


class CmdLie(Command):
    """
    Lie down.
    
    Usage:
        lie                 - Lie on the ground
        lie <furniture>     - Lie on furniture
        lie on <furniture>  - Same as above
        lay down            - Same as lie
    
    Examples:
        lie
        lie bed
        lie on the couch
    """
    
    key = "lie"
    aliases = ["lay", "lie down", "lay down"]
    locks = "cmd:all()"
    help_category = "Positions"
    
    def func(self):
        caller = self.caller
        
        if is_restrained(caller):
            caller.msg("You can't move - you're restrained!")
            return
        
        args = self.args.strip()
        
        # Remove "on " or "down" prefix
        if args.lower().startswith("on "):
            args = args[3:].strip()
        if args.lower() == "down":
            args = ""
        
        if args:
            furniture = caller.search(args, location=caller.location)
            if not furniture:
                return
            
            from world.furniture import is_furniture, use_furniture
            if not is_furniture(furniture):
                caller.msg(f"You can't lie on {furniture.key}.")
                return
            
            success, msg = use_furniture(caller, furniture, position="lying")
            caller.msg(msg)
        else:
            success, msg = set_position(caller, "lying")
            if not success:
                caller.msg(msg)


class CmdPosition(Command):
    """
    Set a specific position.
    
    Usage:
        position <pose>                     - Set position
        position <pose> on <furniture>      - Position on furniture
        position <pose> with <person>       - Position with partner
    
    Examples:
        position lounging
        position seated on throne
        position cuddling with Alice
        position kneeling_before with Master
    
    Use 'positions' to see available positions.
    """
    
    key = "position"
    aliases = ["pose"]
    locks = "cmd:all()"
    help_category = "Positions"
    
    def func(self):
        caller = self.caller
        
        if not self.args:
            # Show current position
            current = get_position_display(caller)
            caller.msg(f"You are currently {current}.")
            return
        
        if is_restrained(caller):
            caller.msg("You can't move - you're restrained!")
            return
        
        args = self.args.strip().lower()
        furniture = None
        partner = None
        
        # Parse "on <furniture>"
        if " on " in args:
            parts = args.split(" on ", 1)
            args = parts[0].strip()
            furn_name = parts[1].strip()
            furniture = caller.search(furn_name, location=caller.location)
            if not furniture:
                return
        
        # Parse "with <partner>"
        if " with " in args:
            parts = args.split(" with ", 1)
            args = parts[0].strip()
            partner_name = parts[1].strip()
            partner = caller.search(partner_name, location=caller.location)
            if not partner:
                return
        
        pose = args.replace(" ", "_")
        
        # Validate position exists
        if pose not in POSITIONS:
            caller.msg(f"Unknown position: {pose}. Use 'positions' to see available positions.")
            return
        
        pos_info = POSITIONS[pose]
        
        # Check adult content flag if needed
        if "adult" in pos_info.get("flags", []):
            # STUB: Check if room allows adult content
            pass
        
        # Use furniture if specified
        if furniture:
            from world.furniture import is_furniture, use_furniture
            if not is_furniture(furniture):
                caller.msg(f"You can't use {furniture.key} for positions.")
                return
            success, msg = use_furniture(caller, furniture, position=pose)
            caller.msg(msg)
            return
        
        # Set position
        success, msg = set_position(caller, pose, partner=partner, furniture=furniture)
        if not success:
            caller.msg(msg)


class CmdPositions(Command):
    """
    List available positions.
    
    Usage:
        positions                   - List all positions
        positions <category>        - List positions in category
        positions adult             - Include adult positions
    
    Categories:
        basic       - Simple positions (sit, stand, kneel, etc.)
        furniture   - Positions on furniture
        social      - Positions with partners
        submissive  - Submissive positions
        bondage     - Restrained positions (requires furniture)
        intimate    - Adult intimate positions
    """
    
    key = "positions"
    aliases = ["poses"]
    locks = "cmd:all()"
    help_category = "Positions"
    
    def func(self):
        caller = self.caller
        args = self.args.strip().lower()
        
        show_adult = "adult" in args
        category = None
        
        # Parse category
        for cat in POSITION_CATEGORIES.keys():
            if cat in args:
                category = cat
                break
        
        positions = list_positions(category=category, adult=show_adult)
        
        if not positions:
            caller.msg("No positions found matching that criteria.")
            return
        
        # Group by category
        by_category = {}
        for key, pos in positions.items():
            cat = pos.get("category", "basic")
            if cat not in by_category:
                by_category[cat] = []
            by_category[cat].append((key, pos))
        
        lines = ["|wAvailable Positions:|n"]
        lines.append("-" * 50)
        
        for cat, poses in sorted(by_category.items()):
            cat_name = POSITION_CATEGORIES.get(cat, cat.title())
            lines.append(f"\n|y{cat_name}:|n")
            
            for key, pos in sorted(poses, key=lambda x: x[0]):
                name = pos.get("name", key)
                flags = pos.get("flags", [])
                
                markers = []
                if pos.get("requires_furniture"):
                    markers.append("|c[F]|n")
                if pos.get("requires_partner"):
                    markers.append("|m[P]|n")
                if "adult" in flags:
                    markers.append("|r[A]|n")
                if "restrained" in flags:
                    markers.append("|x[R]|n")
                
                marker_str = " ".join(markers)
                if marker_str:
                    lines.append(f"  {key:<20} {marker_str}")
                else:
                    lines.append(f"  {key}")
        
        lines.append("-" * 50)
        lines.append("|xLegend: [F]=Furniture [P]=Partner [A]=Adult [R]=Restrained|n")
        
        if not show_adult:
            lines.append("|xUse 'positions adult' to include adult positions.|n")
        
        caller.msg("\n".join(lines))


class CmdCuddle(Command):
    """
    Cuddle with someone.
    
    Usage:
        cuddle <person>
    
    Both people will be put in a cuddling position together.
    """
    
    key = "cuddle"
    aliases = ["snuggle"]
    locks = "cmd:all()"
    help_category = "Positions"
    
    def func(self):
        caller = self.caller
        
        if not self.args:
            caller.msg("Cuddle with whom?")
            return
        
        if is_restrained(caller):
            caller.msg("You can't move - you're restrained!")
            return
        
        target = caller.search(self.args.strip(), location=caller.location)
        if not target:
            return
        
        if target == caller:
            caller.msg("You can't cuddle yourself.")
            return
        
        # Check if target is restrained
        if is_restrained(target):
            caller.msg(f"{target.key} can't move to cuddle.")
            return
        
        # Set both to cuddling
        success, msg = set_position(caller, "cuddling", partner=target)
        if success:
            set_position(target, "cuddling", partner=caller, silent=True)
            target.msg(f"|c{caller.key}|n cuddles up with you.")


class CmdLeave(Command):
    """
    Leave furniture you're currently using.
    
    Usage:
        leave
    
    This stands you up and removes you from any furniture.
    Same as 'stand' when on furniture.
    """
    
    key = "leave"
    aliases = ["dismount", "get off", "exit furniture"]
    locks = "cmd:all()"
    help_category = "Positions"
    
    def func(self):
        caller = self.caller
        
        from world.furniture import leave_furniture
        from world.positions import get_furniture
        
        furniture = get_furniture(caller)
        if not furniture:
            caller.msg("You're not using any furniture. Use 'stand' to stand up.")
            return
        
        success, msg = leave_furniture(caller)
        caller.msg(msg)


# =============================================================================
# Command Set
# =============================================================================

class PositionCmdSet(CmdSet):
    """
    Commands for character positions.
    """
    
    key = "positions"
    priority = 1
    
    def at_cmdset_creation(self):
        self.add(CmdSit())
        self.add(CmdStand())
        self.add(CmdKneel())
        self.add(CmdLie())
        self.add(CmdPosition())
        self.add(CmdPositions())
        self.add(CmdCuddle())
        self.add(CmdLeave())
