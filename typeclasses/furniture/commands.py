"""
Furniture Commands
==================

Commands for interacting with furniture:
- Positioning: sit, lie, kneel, stand, get up
- Restraints: restrain, release, lock, unlock
- Machines: start, stop, speed, pattern
"""

from evennia import Command, CmdSet


# =============================================================================
# HELPER FUNCTIONS
# =============================================================================

def find_furniture(caller, name=None):
    """Find furniture in the room."""
    from .base import Furniture
    
    if name:
        # Search by name
        for obj in caller.location.contents:
            if isinstance(obj, Furniture):
                if name.lower() in obj.key.lower():
                    return obj
        return None
    else:
        # Get all furniture
        return [obj for obj in caller.location.contents if isinstance(obj, Furniture)]


def find_target_in_room(caller, name):
    """Find a character in the room."""
    for obj in caller.location.contents:
        if hasattr(obj, 'msg') and obj != caller:
            if name.lower() in obj.key.lower():
                return obj
    return None


# =============================================================================
# POSITIONING COMMANDS
# =============================================================================

class CmdSit(Command):
    """
    Sit on furniture.
    
    Usage:
        sit <furniture>
        sit on <furniture>
    """
    
    key = "sit"
    locks = "cmd:all()"
    
    def func(self):
        args = self.args.strip()
        if args.startswith("on "):
            args = args[3:]
        
        if not args:
            self.caller.msg("Sit on what?")
            return
        
        furniture = find_furniture(self.caller, args)
        if not furniture:
            self.caller.msg("You don't see that here.")
            return
        
        # Check if already on furniture
        if hasattr(self.caller, 'using_furniture_dbref') and self.caller.using_furniture_dbref:
            self.caller.msg("Get up first.")
            return
        
        # Try to add to a sit slot
        from .base import SlotType
        slots = furniture.get_available_slots(SlotType.SIT)
        if not slots:
            # Try any available slot
            slots = furniture.get_available_slots()
        
        if not slots:
            self.caller.msg(f"There's no room on the {furniture.key}.")
            return
        
        success, msg = furniture.add_occupant(self.caller, slots[0].key)
        self.caller.msg(msg)
        
        if success:
            self.caller.location.msg_contents(
                f"{self.caller.key} sits on the {furniture.key}.",
                exclude=[self.caller]
            )


class CmdLie(Command):
    """
    Lie on furniture.
    
    Usage:
        lie <furniture>
        lie on <furniture>
        lay on <furniture>
    """
    
    key = "lie"
    aliases = ["lay"]
    locks = "cmd:all()"
    
    def func(self):
        args = self.args.strip()
        if args.startswith("on "):
            args = args[3:]
        
        if not args:
            self.caller.msg("Lie on what?")
            return
        
        furniture = find_furniture(self.caller, args)
        if not furniture:
            self.caller.msg("You don't see that here.")
            return
        
        if hasattr(self.caller, 'using_furniture_dbref') and self.caller.using_furniture_dbref:
            self.caller.msg("Get up first.")
            return
        
        from .base import SlotType
        slots = furniture.get_available_slots(SlotType.LIE)
        if not slots:
            slots = furniture.get_available_slots()
        
        if not slots:
            self.caller.msg(f"There's no room on the {furniture.key}.")
            return
        
        success, msg = furniture.add_occupant(self.caller, slots[0].key)
        self.caller.msg(msg)
        
        if success:
            self.caller.location.msg_contents(
                f"{self.caller.key} lies on the {furniture.key}.",
                exclude=[self.caller]
            )


class CmdKneel(Command):
    """
    Kneel on/at furniture.
    
    Usage:
        kneel <furniture>
        kneel on <furniture>
    """
    
    key = "kneel"
    locks = "cmd:all()"
    
    def func(self):
        args = self.args.strip()
        for prefix in ["on ", "at ", "before "]:
            if args.startswith(prefix):
                args = args[len(prefix):]
                break
        
        if not args:
            self.caller.msg("Kneel where?")
            return
        
        furniture = find_furniture(self.caller, args)
        if not furniture:
            self.caller.msg("You don't see that here.")
            return
        
        if hasattr(self.caller, 'using_furniture_dbref') and self.caller.using_furniture_dbref:
            self.caller.msg("Get up first.")
            return
        
        from .base import SlotType
        slots = furniture.get_available_slots(SlotType.KNEEL)
        if not slots:
            slots = furniture.get_available_slots()
        
        if not slots:
            self.caller.msg(f"There's no room at the {furniture.key}.")
            return
        
        success, msg = furniture.add_occupant(self.caller, slots[0].key)
        self.caller.msg(msg)
        
        if success:
            self.caller.location.msg_contents(
                f"{self.caller.key} kneels at the {furniture.key}.",
                exclude=[self.caller]
            )


class CmdBendOver(Command):
    """
    Bend over furniture.
    
    Usage:
        bend over <furniture>
        bend <furniture>
    """
    
    key = "bend"
    locks = "cmd:all()"
    
    def func(self):
        args = self.args.strip()
        if args.startswith("over "):
            args = args[5:]
        
        if not args:
            self.caller.msg("Bend over what?")
            return
        
        furniture = find_furniture(self.caller, args)
        if not furniture:
            self.caller.msg("You don't see that here.")
            return
        
        if hasattr(self.caller, 'using_furniture_dbref') and self.caller.using_furniture_dbref:
            self.caller.msg("Get up first.")
            return
        
        from .base import SlotType
        slots = furniture.get_available_slots(SlotType.BEND)
        if not slots:
            slots = furniture.get_available_slots()
        
        if not slots:
            self.caller.msg(f"There's no room at the {furniture.key}.")
            return
        
        success, msg = furniture.add_occupant(self.caller, slots[0].key)
        self.caller.msg(msg)
        
        if success:
            self.caller.location.msg_contents(
                f"{self.caller.key} bends over the {furniture.key}.",
                exclude=[self.caller]
            )


class CmdGetUp(Command):
    """
    Get up from furniture.
    
    Usage:
        get up
        stand
        leave <furniture>
    """
    
    key = "get up"
    aliases = ["stand", "getup"]
    locks = "cmd:all()"
    
    def func(self):
        if not hasattr(self.caller, 'using_furniture_dbref'):
            self.caller.msg("You're not on any furniture.")
            return
        
        if not self.caller.using_furniture_dbref:
            self.caller.msg("You're not on any furniture.")
            return
        
        # Find the furniture
        from evennia.utils.search import search_object
        try:
            results = search_object(self.caller.using_furniture_dbref)
            furniture = results[0] if results else None
        except Exception:
            furniture = None
        
        if not furniture:
            # Clear the reference anyway
            self.caller.using_furniture_dbref = None
            self.caller.furniture_slot = None
            self.caller.msg("You get up.")
            return
        
        success, msg = furniture.remove_occupant(self.caller)
        self.caller.msg(msg)
        
        if success:
            self.caller.location.msg_contents(
                f"{self.caller.key} gets up from the {furniture.key}.",
                exclude=[self.caller]
            )


class CmdUseFurniture(Command):
    """
    Use furniture in a specific way.
    
    Usage:
        use <furniture>
        use <furniture> <slot>
    
    Shows available slots if no slot specified.
    """
    
    key = "use"
    locks = "cmd:all()"
    
    def func(self):
        args = self.args.split()
        if not args:
            self.caller.msg("Use what?")
            return
        
        furniture_name = args[0]
        slot_name = args[1] if len(args) > 1 else None
        
        furniture = find_furniture(self.caller, furniture_name)
        if not furniture:
            self.caller.msg("You don't see that here.")
            return
        
        if hasattr(self.caller, 'using_furniture_dbref') and self.caller.using_furniture_dbref:
            self.caller.msg("Get up first.")
            return
        
        if slot_name:
            # Use specific slot
            slot = furniture.get_slot(slot_name)
            if not slot:
                self.caller.msg(f"No '{slot_name}' position on that.")
                return
            
            if not slot.is_available():
                self.caller.msg("That position is occupied.")
                return
            
            success, msg = furniture.add_occupant(self.caller, slot_name)
        else:
            # Show available slots
            available = furniture.get_available_slots()
            if not available:
                self.caller.msg(f"No available positions on the {furniture.key}.")
                return
            
            if len(available) == 1:
                success, msg = furniture.add_occupant(self.caller, available[0].key)
            else:
                slot_list = ", ".join(s.key for s in available)
                self.caller.msg(f"Available positions: {slot_list}")
                self.caller.msg(f"Use: use {furniture.key} <position>")
                return
        
        self.caller.msg(msg)
        if success:
            self.caller.location.msg_contents(
                f"{self.caller.key} uses the {furniture.key}.",
                exclude=[self.caller]
            )


# =============================================================================
# RESTRAINT COMMANDS
# =============================================================================

class CmdRestrainOn(Command):
    """
    Restrain someone on furniture.
    
    Usage:
        restrain <target> on <furniture>
        strap <target> to <furniture>
    """
    
    key = "restrain"
    aliases = ["strap"]
    locks = "cmd:all()"
    
    def parse(self):
        args = self.args.strip()
        self.target_name = ""
        self.furniture_name = ""
        
        for sep in [" on ", " to ", " in "]:
            if sep in args:
                parts = args.split(sep, 1)
                self.target_name = parts[0].strip()
                self.furniture_name = parts[1].strip()
                break
        
        if not self.target_name:
            self.target_name = args
    
    def func(self):
        if not self.target_name:
            self.caller.msg("Restrain who?")
            return
        
        target = find_target_in_room(self.caller, self.target_name)
        if not target:
            self.caller.msg("You don't see them here.")
            return
        
        # Find furniture - either specified or what they're on
        if self.furniture_name:
            furniture = find_furniture(self.caller, self.furniture_name)
            if not furniture:
                self.caller.msg("You don't see that furniture.")
                return
        else:
            # Check if target is on furniture
            if hasattr(target, 'using_furniture_dbref') and target.using_furniture_dbref:
                from evennia.utils.search import search_object
                try:
                    results = search_object(target.using_furniture_dbref)
                    furniture = results[0] if results else None
                except:
                    furniture = None
            else:
                furniture = None
        
        if not furniture:
            self.caller.msg("They need to be on furniture first.")
            return
        
        if not furniture.can_restrain():
            self.caller.msg(f"The {furniture.key} can't restrain anyone.")
            return
        
        success, msg = furniture.restrain_occupant(target)
        self.caller.msg(msg)
        
        if success:
            target.msg(f"{self.caller.key} restrains you on the {furniture.key}!")
            self.caller.location.msg_contents(
                f"{self.caller.key} restrains {target.key} on the {furniture.key}.",
                exclude=[self.caller, target]
            )


class CmdReleaseFrom(Command):
    """
    Release someone from furniture restraints.
    
    Usage:
        release <target>
        free <target>
    """
    
    key = "release"
    aliases = ["free"]
    locks = "cmd:all()"
    
    def func(self):
        if not self.args:
            self.caller.msg("Release who?")
            return
        
        target = find_target_in_room(self.caller, self.args.strip())
        if not target:
            self.caller.msg("You don't see them here.")
            return
        
        # Find their furniture
        if not hasattr(target, 'using_furniture_dbref') or not target.using_furniture_dbref:
            self.caller.msg("They're not on any furniture.")
            return
        
        from evennia.utils.search import search_object
        try:
            results = search_object(target.using_furniture_dbref)
            furniture = results[0] if results else None
        except:
            furniture = None
        
        if not furniture:
            self.caller.msg("Can't find their furniture.")
            return
        
        if not furniture.is_occupant_restrained(target):
            self.caller.msg("They're not restrained.")
            return
        
        success, msg = furniture.release_occupant(target)
        self.caller.msg(msg)
        
        if success:
            target.msg(f"{self.caller.key} releases you from the {furniture.key}.")


class CmdLockFurniture(Command):
    """
    Lock furniture (cages, etc).
    
    Usage:
        lock <furniture>
    """
    
    key = "lock"
    locks = "cmd:all()"
    
    def func(self):
        if not self.args:
            self.caller.msg("Lock what?")
            return
        
        furniture = find_furniture(self.caller, self.args.strip())
        if not furniture:
            self.caller.msg("You don't see that here.")
            return
        
        if not hasattr(furniture, 'lock'):
            self.caller.msg(f"The {furniture.key} can't be locked.")
            return
        
        success, msg = furniture.lock()
        self.caller.msg(msg)


class CmdUnlockFurniture(Command):
    """
    Unlock furniture.
    
    Usage:
        unlock <furniture>
    """
    
    key = "unlock"
    locks = "cmd:all()"
    
    def func(self):
        if not self.args:
            self.caller.msg("Unlock what?")
            return
        
        furniture = find_furniture(self.caller, self.args.strip())
        if not furniture:
            self.caller.msg("You don't see that here.")
            return
        
        if not hasattr(furniture, 'unlock'):
            self.caller.msg(f"The {furniture.key} can't be unlocked.")
            return
        
        success, msg = furniture.unlock()
        self.caller.msg(msg)


# =============================================================================
# MACHINE COMMANDS
# =============================================================================

class CmdStartMachine(Command):
    """
    Turn on a machine.
    
    Usage:
        start <machine>
        turn on <machine>
    """
    
    key = "start"
    aliases = ["turn on"]
    locks = "cmd:all()"
    
    def func(self):
        args = self.args.strip()
        if not args:
            self.caller.msg("Start what?")
            return
        
        furniture = find_furniture(self.caller, args)
        if not furniture:
            self.caller.msg("You don't see that here.")
            return
        
        if not hasattr(furniture, 'turn_on'):
            self.caller.msg(f"The {furniture.key} isn't a machine.")
            return
        
        success, msg = furniture.turn_on()
        self.caller.msg(msg)
        
        if success:
            self.caller.location.msg_contents(
                f"{self.caller.key} turns on the {furniture.key}.",
                exclude=[self.caller]
            )


class CmdStopMachine(Command):
    """
    Turn off a machine.
    
    Usage:
        stop <machine>
        turn off <machine>
    """
    
    key = "stop"
    aliases = ["turn off"]
    locks = "cmd:all()"
    
    def func(self):
        args = self.args.strip()
        if not args:
            self.caller.msg("Stop what?")
            return
        
        furniture = find_furniture(self.caller, args)
        if not furniture:
            self.caller.msg("You don't see that here.")
            return
        
        if not hasattr(furniture, 'turn_off'):
            self.caller.msg(f"The {furniture.key} isn't a machine.")
            return
        
        success, msg = furniture.turn_off()
        self.caller.msg(msg)


class CmdSetSpeed(Command):
    """
    Set machine speed.
    
    Usage:
        speed <machine> <level>
        speed <machine> up
        speed <machine> down
    """
    
    key = "speed"
    locks = "cmd:all()"
    
    def func(self):
        args = self.args.split()
        if len(args) < 2:
            self.caller.msg("Usage: speed <machine> <level/up/down>")
            return
        
        furniture_name = args[0]
        setting = args[1].lower()
        
        furniture = find_furniture(self.caller, furniture_name)
        if not furniture:
            self.caller.msg("You don't see that here.")
            return
        
        if not hasattr(furniture, 'set_speed'):
            self.caller.msg(f"The {furniture.key} doesn't have speed control.")
            return
        
        if setting == "up":
            success, msg = furniture.increase_speed()
        elif setting == "down":
            success, msg = furniture.decrease_speed()
        else:
            try:
                level = int(setting)
                success, msg = furniture.set_speed(level)
            except ValueError:
                self.caller.msg("Speed must be a number, 'up', or 'down'.")
                return
        
        self.caller.msg(msg)


class CmdInflateKnot(Command):
    """
    Inflate the knot on a breeding mount.
    
    Usage:
        inflate knot
        inflate <machine>
    """
    
    key = "inflate"
    locks = "cmd:all()"
    
    def func(self):
        args = self.args.strip()
        if args == "knot":
            args = ""
        
        # Find breeding mount
        if args:
            furniture = find_furniture(self.caller, args)
        else:
            # Find any breeding mount
            from .machines import BreedingMount
            for obj in self.caller.location.contents:
                if isinstance(obj, BreedingMount):
                    furniture = obj
                    break
            else:
                furniture = None
        
        if not furniture:
            self.caller.msg("No breeding mount here.")
            return
        
        if not hasattr(furniture, 'inflate_knot'):
            self.caller.msg(f"The {furniture.key} doesn't have an inflatable knot.")
            return
        
        success, msg = furniture.inflate_knot()
        self.caller.msg(msg)
        
        if success:
            self.caller.location.msg_contents(msg, exclude=[self.caller])


class CmdDeflateKnot(Command):
    """
    Deflate the knot on a breeding mount.
    
    Usage:
        deflate knot
        deflate <machine>
    """
    
    key = "deflate"
    locks = "cmd:all()"
    
    def func(self):
        args = self.args.strip()
        if args == "knot":
            args = ""
        
        if args:
            furniture = find_furniture(self.caller, args)
        else:
            from .machines import BreedingMount
            for obj in self.caller.location.contents:
                if isinstance(obj, BreedingMount):
                    furniture = obj
                    break
            else:
                furniture = None
        
        if not furniture:
            self.caller.msg("No breeding mount here.")
            return
        
        if not hasattr(furniture, 'deflate_knot'):
            self.caller.msg(f"The {furniture.key} doesn't have an inflatable knot.")
            return
        
        success, msg = furniture.deflate_knot()
        self.caller.msg(msg)
        
        if success:
            self.caller.location.msg_contents(msg, exclude=[self.caller])


# =============================================================================
# INFO COMMANDS
# =============================================================================

class CmdExamineFurniture(Command):
    """
    Examine furniture in detail.
    
    Usage:
        examine <furniture>
        look <furniture>
    """
    
    key = "examine"
    aliases = ["look at"]
    locks = "cmd:all()"
    
    def func(self):
        if not self.args:
            self.caller.msg("Examine what?")
            return
        
        furniture = find_furniture(self.caller, self.args.strip())
        if not furniture:
            self.caller.msg("You don't see that here.")
            return
        
        # Get detailed description
        lines = [f"|c{furniture.key}|n"]
        lines.append(furniture.db.desc or f"A {furniture.key}.")
        
        # List slots
        slots = furniture.get_slots()
        if slots:
            lines.append("\n|wPositions:|n")
            for slot in slots:
                status = "available" if slot.is_available() else "occupied"
                restraint = " (can restrain)" if slot.can_restrain else ""
                lines.append(f"  {slot.key}: {status}{restraint}")
                
                # Show occupants
                if slot.current_occupants:
                    from evennia.utils.search import search_object
                    for dbref in slot.current_occupants:
                        try:
                            results = search_object(dbref)
                            if results:
                                name = results[0].key
                                if slot.is_restrained(dbref):
                                    name += " (restrained)"
                                lines.append(f"    - {name}")
                        except:
                            pass
        
        # Machine status
        if hasattr(furniture, 'is_powered'):
            if furniture.is_powered:
                lines.append(f"\n|wStatus:|n Running at {furniture.get_speed_desc()} (level {furniture.speed})")
            else:
                lines.append("\n|wStatus:|n Off")
        
        self.caller.msg("\n".join(lines))


# =============================================================================
# CMDSET
# =============================================================================

class FurnitureCmdSet(CmdSet):
    """Commands for furniture interaction."""
    
    key = "FurnitureCmdSet"
    
    def at_cmdset_creation(self):
        # Positioning
        self.add(CmdSit())
        self.add(CmdLie())
        self.add(CmdKneel())
        self.add(CmdBendOver())
        self.add(CmdGetUp())
        self.add(CmdUseFurniture())
        # Restraints
        self.add(CmdRestrainOn())
        self.add(CmdReleaseFrom())
        self.add(CmdLockFurniture())
        self.add(CmdUnlockFurniture())
        # Machines
        self.add(CmdStartMachine())
        self.add(CmdStopMachine())
        self.add(CmdSetSpeed())
        self.add(CmdInflateKnot())
        self.add(CmdDeflateKnot())
        # Info
        self.add(CmdExamineFurniture())


__all__ = [
    "FurnitureCmdSet",
    # Positioning
    "CmdSit", "CmdLie", "CmdKneel", "CmdBendOver", "CmdGetUp", "CmdUseFurniture",
    # Restraints
    "CmdRestrainOn", "CmdReleaseFrom", "CmdLockFurniture", "CmdUnlockFurniture",
    # Machines
    "CmdStartMachine", "CmdStopMachine", "CmdSetSpeed", "CmdInflateKnot", "CmdDeflateKnot",
    # Info
    "CmdExamineFurniture",
    # Helpers
    "find_furniture",
]
