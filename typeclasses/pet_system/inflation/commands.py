"""
Inflation Commands
==================

Commands for body inflation, cum tracking, and drainage.
"""

from evennia import Command, CmdSet
import random


class CmdInflationStatus(Command):
    """
    View inflation status.
    
    Usage:
        inflationstatus [target]
        bloatstatus [target]
    
    Shows current inflation levels and appearance.
    """
    
    key = "inflationstatus"
    aliases = ["bloatstatus", "cumstatus"]
    locks = "cmd:all()"
    
    def func(self):
        caller = self.caller
        
        target = caller
        if self.args:
            target = caller.search(self.args.strip())
            if not target:
                return
        
        if not hasattr(target, 'inflation'):
            caller.msg(f"{target.key} has no inflation data.")
            return
        
        tracker = target.inflation
        caller.msg(tracker.get_status())


class CmdInflate(Command):
    """
    Inflate a body area.
    
    Usage:
        inflate <target> = <location>, <type>, <amount>
        inflate <target> = <location>, <amount>
    
    Locations: belly, womb, stomach, anal, breasts
    Types: cum, water, air, eggs, slime, milk, magical
    """
    
    key = "inflate"
    aliases = ["fill", "pump"]
    locks = "cmd:perm(Builder)"
    
    def func(self):
        caller = self.caller
        
        if "=" not in self.args:
            caller.msg("Usage: inflate <target> = <location>, [type], <amount>")
            return
        
        target_name, rest = self.args.split("=", 1)
        target = caller.search(target_name.strip())
        if not target:
            return
        
        if not hasattr(target, 'inflation'):
            caller.msg(f"{target.key} cannot be inflated.")
            return
        
        parts = [p.strip() for p in rest.split(",")]
        
        if len(parts) >= 3:
            location = parts[0].lower()
            inf_type = parts[1].lower()
            try:
                amount = int(parts[2])
            except ValueError:
                caller.msg("Amount must be a number.")
                return
        elif len(parts) == 2:
            location = parts[0].lower()
            inf_type = "cum"
            try:
                amount = int(parts[1])
            except ValueError:
                caller.msg("Amount must be a number.")
                return
        else:
            caller.msg("Usage: inflate <target> = <location>, [type], <amount>")
            return
        
        tracker = target.inflation
        msg = tracker.inflate(location, inf_type, amount)
        target.db.inflation = tracker.to_dict()
        
        caller.msg(f"Inflated {target.key}'s {location} with {amount}ml {inf_type}. {msg}")
        target.msg(f"Your {location} swells as {amount}ml of {inf_type} fills you... {msg}")
        
        # Show appearance
        caller.msg(tracker.get_appearance_description())


class CmdDrain(Command):
    """
    Drain inflation from a body area.
    
    Usage:
        drain [target]
        drain <target> = <location>
        drain <target> = <location>, <amount>
    
    Drains fluid from a body area.
    """
    
    key = "drain"
    aliases = ["expel", "empty"]
    locks = "cmd:all()"
    
    def func(self):
        caller = self.caller
        
        target = caller
        location = None
        amount = 0
        
        if "=" in self.args:
            target_name, rest = self.args.split("=", 1)
            target = caller.search(target_name.strip())
            if not target:
                return
            
            parts = [p.strip() for p in rest.split(",")]
            location = parts[0].lower()
            
            if len(parts) > 1:
                try:
                    amount = int(parts[1])
                except ValueError:
                    pass
        elif self.args:
            target = caller.search(self.args.strip())
            if not target:
                return
        
        if not hasattr(target, 'inflation'):
            caller.msg(f"{target.key} has nothing to drain.")
            return
        
        tracker = target.inflation
        
        if location:
            msg = tracker.drain_area(location, amount)
        else:
            # Drain all areas
            messages = []
            for loc in ["belly", "womb", "stomach", "anal", "breasts"]:
                area = getattr(tracker, loc)
                if area.total_volume_ml > 0:
                    drained, m = area.drain()
                    messages.append(f"{loc}: {drained}ml")
            msg = " | ".join(messages) if messages else "Nothing to drain."
        
        target.db.inflation = tracker.to_dict()
        
        caller.msg(f"Drained {target.key}. {msg}")
        if target != caller:
            target.msg(f"Fluid drains from your body... {msg}")


class CmdCumDump(Command):
    """
    Large cum deposit (convenience command).
    
    Usage:
        cumdump <target> = <amount>
        cumdump <target>
    
    Dumps a large load into target's womb. Default 500ml.
    """
    
    key = "cumdump"
    aliases = ["creampie", "fill"]
    locks = "cmd:all()"
    
    def func(self):
        caller = self.caller
        
        if "=" in self.args:
            target_name, amount_str = self.args.split("=", 1)
            try:
                amount = int(amount_str.strip())
            except ValueError:
                amount = 500
        else:
            target_name = self.args
            amount = 500
        
        target = caller.search(target_name.strip())
        if not target:
            return
        
        if not hasattr(target, 'inflation'):
            caller.msg(f"{target.key} cannot be filled.")
            return
        
        from ..inflation import cum_dump
        
        tracker = target.inflation
        msg = cum_dump(tracker, amount)
        target.db.inflation = tracker.to_dict()
        
        caller.location.msg_contents(
            f"{caller.key} pumps a massive load into {target.key}!",
            exclude=[caller, target]
        )
        caller.msg(msg)
        target.msg(f"A huge load floods your womb! {msg}")


class CmdGangbangInflation(Command):
    """
    Multiple loads (gangbang simulation).
    
    Usage:
        gangbangfill <target> = <num_loads>
        gangbangfill <target>
    
    Simulates being filled by multiple sources. Default 10 loads.
    """
    
    key = "gangbangfill"
    aliases = ["gangfill"]
    locks = "cmd:perm(Builder)"
    
    def func(self):
        caller = self.caller
        
        if "=" in self.args:
            target_name, loads_str = self.args.split("=", 1)
            try:
                num_loads = int(loads_str.strip())
            except ValueError:
                num_loads = 10
        else:
            target_name = self.args
            num_loads = 10
        
        target = caller.search(target_name.strip())
        if not target:
            return
        
        if not hasattr(target, 'inflation'):
            caller.msg(f"{target.key} cannot be filled.")
            return
        
        from ..inflation import gangbang_inflation
        
        tracker = target.inflation
        msg = gangbang_inflation(tracker, num_loads)
        target.db.inflation = tracker.to_dict()
        
        caller.msg(msg)
        target.msg(f"Load after load pumps into you... {msg}")


class CmdSlimeEngulf(Command):
    """
    Slime fills all holes.
    
    Usage:
        slimefill <target> = <amount>
        slimefill <target>
    
    Floods target with slime in all orifices. Default 1000ml.
    """
    
    key = "slimefill"
    aliases = ["slimeengulf"]
    locks = "cmd:perm(Builder)"
    
    def func(self):
        caller = self.caller
        
        if "=" in self.args:
            target_name, amount_str = self.args.split("=", 1)
            try:
                amount = int(amount_str.strip())
            except ValueError:
                amount = 1000
        else:
            target_name = self.args
            amount = 1000
        
        target = caller.search(target_name.strip())
        if not target:
            return
        
        if not hasattr(target, 'inflation'):
            caller.msg(f"{target.key} cannot be filled.")
            return
        
        from ..inflation import slime_engulf
        
        tracker = target.inflation
        msg = slime_engulf(tracker, amount)
        target.db.inflation = tracker.to_dict()
        
        caller.msg(msg)
        target.msg(f"Slime floods every opening! {msg}")


class CmdSetCapacity(Command):
    """
    Set inflation capacity for a body area.
    
    Usage:
        setcapacity <target> = <location>, <amount>
    
    Sets maximum capacity in ml for an area.
    """
    
    key = "setcapacity"
    locks = "cmd:perm(Builder)"
    
    def func(self):
        caller = self.caller
        
        if "=" not in self.args:
            caller.msg("Usage: setcapacity <target> = <location>, <amount>")
            return
        
        target_name, rest = self.args.split("=", 1)
        target = caller.search(target_name.strip())
        if not target:
            return
        
        parts = [p.strip() for p in rest.split(",")]
        if len(parts) < 2:
            caller.msg("Need location and amount.")
            return
        
        location = parts[0].lower()
        try:
            amount = int(parts[1])
        except ValueError:
            caller.msg("Amount must be a number.")
            return
        
        if not hasattr(target, 'inflation'):
            caller.msg(f"{target.key} has no inflation data.")
            return
        
        tracker = target.inflation
        area = getattr(tracker, location, None)
        
        if not area:
            caller.msg(f"Unknown location: {location}")
            return
        
        area.base_capacity_ml = amount
        target.db.inflation = tracker.to_dict()
        
        caller.msg(f"Set {target.key}'s {location} capacity to {amount}ml.")


class CmdInflationAppearance(Command):
    """
    Show visual description of inflation.
    
    Usage:
        bloated [target]
    
    Shows how inflated the character appears.
    """
    
    key = "bloated"
    aliases = ["inflatedlook", "bellylook"]
    locks = "cmd:all()"
    
    def func(self):
        caller = self.caller
        
        target = caller
        if self.args:
            target = caller.search(self.args.strip())
            if not target:
                return
        
        if not hasattr(target, 'inflation'):
            caller.msg(f"{target.key} appears normal.")
            return
        
        tracker = target.inflation
        caller.msg(tracker.get_appearance_description())


class CmdProcessTime(Command):
    """
    Process time passing for inflation.
    
    Usage:
        processtime <target> = <hours>
    
    Processes leakage and absorption over time.
    """
    
    key = "processtime"
    aliases = ["timepasses"]
    locks = "cmd:perm(Builder)"
    
    def func(self):
        caller = self.caller
        
        if "=" not in self.args:
            caller.msg("Usage: processtime <target> = <hours>")
            return
        
        target_name, hours_str = self.args.split("=", 1)
        target = caller.search(target_name.strip())
        if not target:
            return
        
        try:
            hours = float(hours_str.strip())
        except ValueError:
            hours = 1.0
        
        if not hasattr(target, 'inflation'):
            caller.msg(f"{target.key} has no inflation data.")
            return
        
        tracker = target.inflation
        messages = tracker.process_time(hours)
        target.db.inflation = tracker.to_dict()
        
        if messages:
            caller.msg(f"After {hours} hours: " + " | ".join(messages))
        else:
            caller.msg(f"No changes after {hours} hours.")


class InflationCmdSet(CmdSet):
    """Commands for inflation system."""
    
    key = "inflation_cmdset"
    
    def at_cmdset_creation(self):
        self.add(CmdInflationStatus())
        self.add(CmdInflate())
        self.add(CmdDrain())
        self.add(CmdCumDump())
        self.add(CmdGangbangInflation())
        self.add(CmdSlimeEngulf())
        self.add(CmdSetCapacity())
        self.add(CmdInflationAppearance())
        self.add(CmdProcessTime())
