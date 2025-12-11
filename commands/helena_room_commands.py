"""
Helena's Room Commands

Commands for interacting with Helena's Room:
- Kennel: enter, leave, lock, unlock, curtain
- Bed: clean, soil, rip
- Desk: drawer, mechanism
- Tapestry: move
- Trapdoor: open, close

Add to your default cmdset or create a room-based cmdset.
"""

from evennia import Command, CmdSet


# =============================================================================
# KENNEL COMMANDS
# =============================================================================

class CmdEnterKennel(Command):
    """
    Enter the kennel beneath the bed.
    
    Usage:
        enter kennel
        crawl into kennel
    
    Crawl into the kennel space beneath Helena's bed.
    Once inside, you can see the room through the bars.
    """
    
    key = "enter kennel"
    aliases = ["crawl into kennel", "go into kennel", "get in kennel"]
    locks = "cmd:all()"
    help_category = "Helena's Room"
    
    def func(self):
        caller = self.caller
        
        # Find kennel
        from world.build_helenas_room import HelenaKennel
        
        kennel = None
        if caller.location:
            for obj in caller.location.contents:
                if isinstance(obj, HelenaKennel):
                    kennel = obj
                    break
        
        if not kennel:
            caller.msg("There's no kennel here.")
            return
        
        success, msg = kennel.enter_kennel(caller)
        caller.msg(msg)
        
        if success and caller.location:
            caller.location.msg_contents(
                f"{caller.key} crawls into the kennel beneath the bed.",
                exclude=[caller]
            )


class CmdLeaveKennel(Command):
    """
    Leave the kennel.
    
    Usage:
        leave kennel
        crawl out
        exit kennel
    
    Crawl out of the kennel back into the room.
    Only works if the kennel door is unlocked.
    """
    
    key = "leave kennel"
    aliases = ["crawl out", "exit kennel", "get out", "out of kennel"]
    locks = "cmd:all()"
    help_category = "Helena's Room"
    
    def func(self):
        caller = self.caller
        
        from world.build_helenas_room import HelenaKennel
        
        kennel = None
        if caller.location:
            for obj in caller.location.contents:
                if isinstance(obj, HelenaKennel):
                    kennel = obj
                    break
        
        if not kennel:
            caller.msg("There's no kennel here.")
            return
        
        if not kennel.is_character_inside(caller):
            caller.msg("You're not inside the kennel.")
            return
        
        success, msg = kennel.leave_kennel(caller)
        caller.msg(msg)
        
        if success and caller.location:
            caller.location.msg_contents(
                f"{caller.key} crawls out of the kennel.",
                exclude=[caller]
            )


class CmdLockKennel(Command):
    """
    Lock or unlock the kennel door.
    
    Usage:
        lock kennel
        unlock kennel
    
    Must be outside the kennel to use.
    No key required.
    """
    
    key = "lock kennel"
    aliases = ["unlock kennel"]
    locks = "cmd:all()"
    help_category = "Helena's Room"
    
    def func(self):
        caller = self.caller
        
        from world.build_helenas_room import HelenaKennel
        
        kennel = None
        if caller.location:
            for obj in caller.location.contents:
                if isinstance(obj, HelenaKennel):
                    kennel = obj
                    break
        
        if not kennel:
            caller.msg("There's no kennel here.")
            return
        
        # Must be outside
        if kennel.is_character_inside(caller):
            caller.msg("You can't reach the lock from inside.")
            return
        
        # Check which command was used
        if self.cmdstring.startswith("unlock"):
            msg = kennel.unlock()
        else:
            msg = kennel.lock()
        
        caller.msg(msg)
        
        if caller.location:
            if "lock" in msg.lower() and "already" not in msg.lower():
                caller.location.msg_contents(
                    f"{caller.key} {'un' if 'unlock' in msg.lower() else ''}locks the kennel door.",
                    exclude=[caller]
                )


class CmdKennelCurtain(Command):
    """
    Open or close the curtain at the back of the kennel.
    
    Usage:
        open curtain
        close curtain
    
    Must be inside the kennel to use.
    When open, reveals passage to Birthing Den.
    """
    
    key = "open curtain"
    aliases = ["close curtain", "draw curtain", "pull curtain"]
    locks = "cmd:all()"
    help_category = "Helena's Room"
    
    def func(self):
        caller = self.caller
        
        from world.build_helenas_room import HelenaKennel
        
        kennel = None
        if caller.location:
            for obj in caller.location.contents:
                if isinstance(obj, HelenaKennel):
                    kennel = obj
                    break
        
        if not kennel:
            caller.msg("There's no kennel here.")
            return
        
        # Must be inside
        if not kennel.is_character_inside(caller):
            caller.msg("You need to be inside the kennel to reach the curtain.")
            return
        
        # Check which command
        if "close" in self.cmdstring:
            msg = kennel.close_curtain()
        else:
            msg = kennel.open_curtain()
        
        caller.msg(msg)


# =============================================================================
# BED COMMANDS
# =============================================================================

class CmdBed(Command):
    """
    Interact with Helena's bed.
    
    Usage:
        bed                 - Look at the bed
        bed clean           - Clean up the bed one step
        bed clean/full      - Fully clean and make the bed
        bed soil            - Make the bed messier
        bed rip             - Tear the sheets (rough activity)
    
    The bed state decays naturally toward 'fresh' over time.
    """
    
    key = "bed"
    locks = "cmd:all()"
    help_category = "Helena's Room"
    
    def func(self):
        caller = self.caller
        
        from world.build_helenas_room import HelenaBed
        
        bed = None
        if caller.location:
            for obj in caller.location.contents:
                if isinstance(obj, HelenaBed):
                    bed = obj
                    break
        
        if not bed:
            caller.msg("There's no bed here.")
            return
        
        args = self.args.strip().lower() if self.args else ""
        
        if not args:
            # Just look at bed
            caller.msg(bed.return_appearance(caller))
            return
        
        if args == "clean":
            if "full" in self.switches:
                msg = bed.clean_fully()
            else:
                msg = bed.clean()
            caller.msg(msg)
            if caller.location and "already" not in msg.lower():
                caller.location.msg_contents(
                    f"{caller.key} tidies up the bed.",
                    exclude=[caller]
                )
        
        elif args == "soil":
            msg = bed.soil()
            caller.msg(msg)
        
        elif args == "rip":
            msg = bed.rip()
            caller.msg(msg)
            if caller.location:
                caller.location.msg_contents(
                    f"The sound of tearing fabric comes from the bed.",
                    exclude=[caller]
                )
        
        else:
            caller.msg("Usage: bed [clean|soil|rip]")


# =============================================================================
# DESK COMMANDS
# =============================================================================

class CmdDesk(Command):
    """
    Interact with Helena's desk.
    
    Usage:
        desk                    - Look at the desk
        desk open <1-4>         - Open a drawer
        desk close <1-4>        - Close a drawer
    
    Drawer 4 contains a hidden mechanism.
    """
    
    key = "desk"
    locks = "cmd:all()"
    help_category = "Helena's Room"
    
    def func(self):
        caller = self.caller
        
        from world.build_helenas_room import HelenaDesk
        
        desk = None
        if caller.location:
            for obj in caller.location.contents:
                if isinstance(obj, HelenaDesk):
                    desk = obj
                    break
        
        if not desk:
            caller.msg("There's no desk here.")
            return
        
        args = self.args.strip().lower() if self.args else ""
        
        if not args:
            caller.msg(desk.return_appearance(caller))
            return
        
        # Parse "open 2" or "close 3"
        parts = args.split()
        if len(parts) >= 2:
            action = parts[0]
            try:
                drawer_num = int(parts[1])
            except ValueError:
                caller.msg("Usage: desk open <1-4> | desk close <1-4>")
                return
            
            if action == "open":
                success, msg = desk.open_drawer(drawer_num)
                caller.msg(msg)
            elif action == "close":
                success, msg = desk.close_drawer(drawer_num)
                caller.msg(msg)
            else:
                caller.msg("Usage: desk open <1-4> | desk close <1-4>")
        else:
            caller.msg("Usage: desk open <1-4> | desk close <1-4>")


class CmdDrawer(Command):
    """
    Open or close a desk drawer directly.
    
    Usage:
        open drawer <1-4>
        close drawer <1-4>
    """
    
    key = "open drawer"
    aliases = ["close drawer"]
    locks = "cmd:all()"
    help_category = "Helena's Room"
    
    def func(self):
        caller = self.caller
        
        from world.build_helenas_room import HelenaDesk
        
        desk = None
        if caller.location:
            for obj in caller.location.contents:
                if isinstance(obj, HelenaDesk):
                    desk = obj
                    break
        
        if not desk:
            caller.msg("There's no desk here.")
            return
        
        if not self.args:
            caller.msg("Which drawer? (1-4)")
            return
        
        try:
            drawer_num = int(self.args.strip())
        except ValueError:
            caller.msg("Drawer number must be 1-4.")
            return
        
        if "close" in self.cmdstring:
            success, msg = desk.close_drawer(drawer_num)
        else:
            success, msg = desk.open_drawer(drawer_num)
        
        caller.msg(msg)


class CmdMechanism(Command):
    """
    Use the mechanism in drawer 4.
    
    Usage:
        pull lever
        use mechanism
    
    Drawer 4 must be open. Toggles the trapdoor to the laboratory.
    """
    
    key = "pull lever"
    aliases = ["use mechanism", "pull mechanism", "use lever"]
    locks = "cmd:all()"
    help_category = "Helena's Room"
    
    def func(self):
        caller = self.caller
        
        from world.build_helenas_room import HelenaDesk
        
        desk = None
        if caller.location:
            for obj in caller.location.contents:
                if isinstance(obj, HelenaDesk):
                    desk = obj
                    break
        
        if not desk:
            caller.msg("There's no mechanism here.")
            return
        
        msg = desk.use_mechanism(caller)
        caller.msg(msg)
        
        if caller.location and "trapdoor" in msg.lower():
            if "open" in msg.lower():
                caller.location.msg_contents(
                    "A grinding sound—a trapdoor opens in the floor near the desk.",
                    exclude=[caller]
                )
            else:
                caller.location.msg_contents(
                    "A heavy thunk—the trapdoor swings closed.",
                    exclude=[caller]
                )


# =============================================================================
# TAPESTRY COMMANDS
# =============================================================================

class CmdMoveTapestry(Command):
    """
    Move a tapestry aside or back into place.
    
    Usage:
        move tapestry <direction>
        move northern tapestry
        move south tapestry
        
    Directions: north, south, east
    
    Reveals or hides the doorway behind.
    """
    
    key = "move tapestry"
    aliases = [
        "move northern tapestry", "move southern tapestry", "move eastern tapestry",
        "move north tapestry", "move south tapestry", "move east tapestry",
        "push tapestry", "pull tapestry"
    ]
    locks = "cmd:all()"
    help_category = "Helena's Room"
    
    def func(self):
        caller = self.caller
        
        from world.build_helenas_room import TapestryExit
        
        # Find tapestries
        tapestries = []
        if caller.location:
            tapestries = [obj for obj in caller.location.contents 
                         if isinstance(obj, TapestryExit)]
        
        if not tapestries:
            caller.msg("There are no tapestries here.")
            return
        
        # Parse direction from command or args
        direction = None
        
        # Check cmdstring first
        for d in ["north", "south", "east"]:
            if d in self.cmdstring.lower():
                direction = d
                break
        
        # Then check args
        if not direction and self.args:
            args = self.args.strip().lower()
            for d in ["north", "south", "east"]:
                if d in args:
                    direction = d
                    break
        
        if not direction:
            caller.msg("Which tapestry? (north, south, east)")
            return
        
        # Find matching tapestry
        target = None
        for tap in tapestries:
            if tap.db.direction == direction:
                target = tap
                break
        
        if not target:
            caller.msg(f"There's no tapestry on the {direction} wall.")
            return
        
        msg = target.toggle()
        caller.msg(msg)
        
        if caller.location:
            if target.is_open:
                caller.location.msg_contents(
                    f"{caller.key} pushes the {direction}ern tapestry aside.",
                    exclude=[caller]
                )
            else:
                caller.location.msg_contents(
                    f"{caller.key} lets the {direction}ern tapestry fall back into place.",
                    exclude=[caller]
                )


# =============================================================================
# TRAPDOOR COMMANDS
# =============================================================================

class CmdTrapdoor(Command):
    """
    Interact with the trapdoor.
    
    Usage:
        open trapdoor
        close trapdoor
    
    The trapdoor must first be revealed by the desk mechanism.
    """
    
    key = "open trapdoor"
    aliases = ["close trapdoor"]
    locks = "cmd:all()"
    help_category = "Helena's Room"
    
    def func(self):
        caller = self.caller
        
        from world.build_helenas_room import HiddenTrapdoor
        
        trapdoor = None
        if caller.location:
            for obj in caller.location.contents:
                if isinstance(obj, HiddenTrapdoor):
                    trapdoor = obj
                    break
        
        if not trapdoor:
            caller.msg("There's no trapdoor here.")
            return
        
        if not trapdoor.is_revealed:
            caller.msg("You don't see any trapdoor.")
            return
        
        # Trapdoor is always "open" when revealed - can close via mechanism
        caller.msg("The trapdoor is controlled by the mechanism in the desk.")


# =============================================================================
# COMMAND SET
# =============================================================================

class HelenaRoomCmdSet(CmdSet):
    """
    Commands for Helena's Room.
    
    Add to default cmdset:
        from commands.helena_room_commands import HelenaRoomCmdSet
        self.add(HelenaRoomCmdSet)
    """
    
    key = "helena_room"
    priority = 1
    
    def at_cmdset_creation(self):
        # Kennel
        self.add(CmdEnterKennel())
        self.add(CmdLeaveKennel())
        self.add(CmdLockKennel())
        self.add(CmdKennelCurtain())
        
        # Bed
        self.add(CmdBed())
        
        # Desk
        self.add(CmdDesk())
        self.add(CmdDrawer())
        self.add(CmdMechanism())
        
        # Tapestry
        self.add(CmdMoveTapestry())
        
        # Trapdoor
        self.add(CmdTrapdoor())
