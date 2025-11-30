"""
Production Commands
===================

Commands for fluid production:
- Lactation management
- Milking operations
"""

from evennia import Command, CmdSet

from .production import (
    FluidType, MilkingMethod, ProductionStats,
    MilkingEquipment, ALL_EQUIPMENT
)


class CmdLactation(Command):
    """
    View or manage lactation.
    
    Usage:
      lactation               - View status
      lactation start         - Start lactating
      lactation stop          - Stop lactating
    """
    
    key = "lactation"
    aliases = ["lactate"]
    locks = "cmd:all()"
    
    def func(self):
        args = self.args.strip().lower() if self.args else ""
        
        if not hasattr(self.caller, 'milk_production'):
            self.caller.msg("This character cannot produce milk.")
            return
        
        if not args:
            # View status
            stats = self.caller.milk_production
            
            if not stats:
                self.caller.msg("You are not lactating.")
                return
            
            level = stats.get_level()
            fullness = stats.get_fullness_percent()
            
            lines = ["=== Lactation Status ==="]
            lines.append(f"Status: {'Producing' if stats.is_producing else 'Not producing'}")
            lines.append(f"Level: {level.value}")
            lines.append(f"Fullness: {fullness}% ({stats.current_ml}/{stats.max_capacity_ml}ml)")
            lines.append(f"Rate: {stats.production_rate_per_hour}ml/hour")
            lines.append(f"Quality: {stats.quality}%")
            
            if stats.is_full:
                lines.append("Status: FULL!")
            if stats.is_leaking:
                lines.append("Status: LEAKING!")
            
            lines.append(f"Total produced: {stats.total_produced_ml}ml")
            lines.append(f"Times milked: {stats.times_milked}")
            
            self.caller.msg("\n".join(lines))
            return
        
        if args == "start":
            message = self.caller.start_lactation()
            self.caller.msg(message)
            return
        
        if args == "stop":
            message = self.caller.stop_lactation()
            self.caller.msg(message)
            return
        
        self.caller.msg("Unknown command. Use 'lactation', 'lactation start', or 'lactation stop'.")


class CmdMilk(Command):
    """
    Milk someone (or yourself).
    
    Usage:
      milk                    - Milk yourself
      milk <target>           - Milk someone else
      milk <target> <method>  - Use specific method
    
    Methods: manual, mouth, pump, magic
    """
    
    key = "milk"
    locks = "cmd:all()"
    
    def func(self):
        args = self.args.strip().split() if self.args else []
        
        if not args:
            target = self.caller
            method = MilkingMethod.MANUAL
        else:
            target_name = args[0]
            target = self.caller.search(target_name)
            if not target:
                return
            
            if len(args) > 1:
                try:
                    method = MilkingMethod(args[1].lower())
                except ValueError:
                    valid = ", ".join([m.value for m in MilkingMethod])
                    self.caller.msg(f"Invalid method. Valid: {valid}")
                    return
            else:
                method = MilkingMethod.MANUAL
        
        if not hasattr(target, 'milk_production'):
            self.caller.msg(f"{target.key} cannot produce milk.")
            return
        
        stats = target.milk_production
        
        if not stats or not stats.is_producing:
            self.caller.msg(f"{target.key} is not lactating.")
            return
        
        if stats.current_ml <= 0:
            self.caller.msg(f"{target.key} has no milk to extract.")
            return
        
        # Extract
        amount, message = stats.extract(200, method)  # Try to extract 200ml
        target.milk_production = stats
        
        if target == self.caller:
            self.caller.msg(f"You milk yourself. {message}")
        else:
            self.caller.msg(f"You milk {target.key}. {message}")
            target.msg(f"{self.caller.key} milks you. {message}")
            self.caller.location.msg_contents(
                f"{self.caller.key} milks {target.key}.",
                exclude=[self.caller, target]
            )


class CmdMilkingStation(Command):
    """
    Use a milking station.
    
    Usage:
      milkstation                      - List stations
      milkstation attach <target>      - Attach someone
      milkstation release              - Release current occupant
      milkstation milk                 - Begin milking
      milkstation collect              - Collect milk
    """
    
    key = "milkstation"
    aliases = ["milker", "station"]
    locks = "cmd:all()"
    
    def func(self):
        args = self.args.strip().split() if self.args else []
        
        if not args:
            # List available stations
            lines = ["=== Milking Equipment ==="]
            for key, equip in ALL_EQUIPMENT.items():
                status = f"Occupied by {equip.occupant_name}" if equip.is_occupied else "Available"
                lines.append(f"  {key}: {equip.name} - {status}")
            self.caller.msg("\n".join(lines))
            return
        
        cmd = args[0].lower()
        
        # For this example, we'll use a default station
        # In real implementation, this would be furniture in the room
        station = ALL_EQUIPMENT.get("breast_pump")
        
        if cmd == "attach":
            if len(args) < 2:
                self.caller.msg("Attach who?")
                return
            
            target = self.caller.search(args[1])
            if not target:
                return
            
            success, message = station.attach(target)
            self.caller.msg(message)
            if success:
                target.msg(f"You are attached to {station.name}.")
        
        elif cmd == "release":
            message = station.release()
            self.caller.msg(message)
        
        elif cmd == "milk":
            if not station.is_occupied:
                self.caller.msg("No one is attached to the station.")
                return
            
            # Find the occupant
            occupant = self.caller.search(station.occupant_dbref)
            if not occupant:
                self.caller.msg("Cannot find occupant.")
                return
            
            if not hasattr(occupant, 'milk_production'):
                self.caller.msg(f"{occupant.key} cannot produce milk.")
                return
            
            stats = occupant.milk_production
            if not stats:
                self.caller.msg(f"{occupant.key} is not lactating.")
                return
            
            collected, message = station.milk(stats, 5)  # 5 minute cycle
            occupant.milk_production = stats
            
            self.caller.msg(message)
            occupant.msg(f"The milking machine extracts {collected}ml from you.")
        
        elif cmd == "collect":
            amount, message = station.empty_container()
            self.caller.msg(message)
        
        else:
            self.caller.msg("Unknown command.")


class ProductionCmdSet(CmdSet):
    """Commands for production systems."""
    
    key = "ProductionCmdSet"
    
    def at_cmdset_creation(self):
        self.add(CmdLactation())
        self.add(CmdMilk())
        self.add(CmdMilkingStation())
