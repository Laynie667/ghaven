"""
Mounting Commands
=================

Commands for harnesses, belly mounting, and riding:
- Harness management
- Belly sling operations
- Saddle and riding
- Gait control
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
# HARNESS COMMANDS
# =============================================================================

class CmdHarness(Command):
    """
    Put a harness on someone.
    
    Usage:
      harness <target> <harness_type>
      harness <target> remove
      harness list
      
    Harness types:
      basic_breeding, locking_breeding, training_breeding
      pony_breeding, double, milking_breeding
      mounting_assist, stability
      basic_belly_sling, concealed_belly_sling, breeding_belly_sling
      
    Examples:
      harness Luna breeding
      harness Starlight belly_sling
      harness Luna remove
    """
    key = "harness"
    locks = "cmd:all()"
    help_category = "Mounting"
    
    def parse(self):
        args = self.args.strip().split()
        self.target_name = args[0] if args else ""
        self.harness_type = args[1] if len(args) > 1 else ""
    
    def func(self):
        if not self.target_name:
            self.caller.msg("Harness whom?")
            return
        
        if self.target_name.lower() == "list":
            from .mounting.harnesses import ALL_HARNESSES
            
            lines = ["Available harnesses:"]
            for key, harness in ALL_HARNESSES.items():
                lines.append(f"  {key}: {harness.name}")
            
            self.caller.msg("\n".join(lines))
            return
        
        target = find_target(self.caller, self.target_name)
        if not target:
            self.caller.msg(f"Can't find '{self.target_name}' here.")
            return
        
        if self.harness_type.lower() == "remove":
            if hasattr(target, 'remove_harness'):
                result = target.remove_harness()
                self.caller.msg(result)
            else:
                self.caller.msg(f"{target.key} can't wear harnesses.")
            return
        
        if not self.harness_type:
            self.caller.msg("Which type of harness?")
            return
        
        from .mounting.harnesses import get_harness, ALL_HARNESSES
        
        # Find harness by partial match
        harness = get_harness(self.harness_type)
        
        if not harness:
            # Try partial match
            for key in ALL_HARNESSES:
                if self.harness_type.lower() in key:
                    harness = ALL_HARNESSES[key]
                    break
        
        if not harness:
            self.caller.msg(f"Unknown harness type: {self.harness_type}")
            return
        
        if hasattr(target, 'put_on_harness'):
            result = target.put_on_harness(harness)
            self.caller.msg(result)
            self.caller.location.msg_contents(
                f"{self.caller.key} straps a {harness.name} onto {target.key}.",
                exclude=[self.caller]
            )
        else:
            self.caller.msg(f"{target.key} can't wear harnesses.")


class CmdLockHarness(Command):
    """
    Lock a harness on someone.
    
    Usage:
      lockharness <target>
      unlockharness <target>
    """
    key = "lockharness"
    aliases = ["harnesslock"]
    locks = "cmd:all()"
    help_category = "Mounting"
    
    def func(self):
        if not self.args.strip():
            self.caller.msg("Lock harness on whom?")
            return
        
        target = find_target(self.caller, self.args.strip())
        if not target:
            self.caller.msg(f"Can't find '{self.args.strip()}' here.")
            return
        
        if not hasattr(target, 'worn_harness') or not target.worn_harness:
            self.caller.msg(f"{target.key} isn't wearing a harness.")
            return
        
        harness = target.worn_harness
        
        if not harness.is_lockable:
            self.caller.msg("This harness can't be locked.")
            return
        
        harness.lock()
        # Save updated harness
        target.worn_harness = harness
        
        self.caller.msg(f"You lock the {harness.name} on {target.key}.")
        target.msg(f"{self.caller.key} locks your harness. You can't remove it!")


class CmdUnlockHarness(Command):
    """
    Unlock a harness.
    
    Usage:
      unlockharness <target>
    """
    key = "unlockharness"
    aliases = ["harnessunlock"]
    locks = "cmd:all()"
    help_category = "Mounting"
    
    def func(self):
        if not self.args.strip():
            self.caller.msg("Unlock harness on whom?")
            return
        
        target = find_target(self.caller, self.args.strip())
        if not target:
            self.caller.msg(f"Can't find '{self.args.strip()}' here.")
            return
        
        if not hasattr(target, 'worn_harness') or not target.worn_harness:
            self.caller.msg(f"{target.key} isn't wearing a harness.")
            return
        
        harness = target.worn_harness
        harness.unlock()
        target.worn_harness = harness
        
        self.caller.msg(f"You unlock the {harness.name} on {target.key}.")
        target.msg(f"{self.caller.key} unlocks your harness.")


# =============================================================================
# BELLY MOUNT COMMANDS
# =============================================================================

class CmdSling(Command):
    """
    Mount someone in a belly sling beneath a tauroid/quadruped.
    
    Usage:
      sling <passenger> beneath <carrier>
      sling <passenger> off
      
    Examples:
      sling Lyra beneath Thunderhoof
      sling Lyra off
    """
    key = "sling"
    aliases = ["bellymount"]
    locks = "cmd:all()"
    help_category = "Mounting"
    
    def parse(self):
        args = self.args.strip()
        
        if " beneath " in args.lower():
            parts = args.lower().split(" beneath ")
            self.passenger_name = parts[0].strip()
            self.carrier_name = parts[1].strip()
            self.action = "mount"
        elif " off" in args.lower():
            self.passenger_name = args.lower().replace(" off", "").strip()
            self.carrier_name = ""
            self.action = "unmount"
        else:
            self.passenger_name = args
            self.carrier_name = ""
            self.action = ""
    
    def func(self):
        if not self.passenger_name:
            self.caller.msg("Usage: sling <passenger> beneath <carrier>")
            return
        
        passenger = find_target(self.caller, self.passenger_name)
        if not passenger:
            self.caller.msg(f"Can't find '{self.passenger_name}' here.")
            return
        
        from .mounting.belly_mount import BellyMountSystem
        
        if self.action == "unmount":
            # Find who they're mounted to
            carrier_ref = getattr(passenger, 'belly_mounted_to', '')
            if not carrier_ref:
                self.caller.msg(f"{passenger.key} is not belly mounted.")
                return
            
            # Would need to look up carrier by dbref
            self.caller.msg(f"You release {passenger.key} from the belly sling.")
            return
        
        if not self.carrier_name:
            self.caller.msg("Sling them beneath whom?")
            return
        
        carrier = find_target(self.caller, self.carrier_name)
        if not carrier:
            self.caller.msg(f"Can't find '{self.carrier_name}' here.")
            return
        
        success, message = BellyMountSystem.mount_passenger(carrier, passenger)
        self.caller.msg(message)
        
        if success:
            self.caller.location.msg_contents(
                f"{self.caller.key} secures {passenger.key} in a belly sling beneath {carrier.key}.",
                exclude=[self.caller]
            )


class CmdBellyPosition(Command):
    """
    Change position of someone in a belly sling.
    
    Usage:
      bellyposition <carrier> <position>
      
    Positions:
      belly_slung - Generic, against belly
      sheath_mount - Impaled on sheath (male carriers)
      sheath_oral - Oral service (male carriers)
      udder_mount - Nursing at udders (female carriers)
      breeding_slung - Rear exposed for breeding
      inverted - Upside down
      
    Examples:
      bellyposition Thunderhoof sheath_mount
    """
    key = "bellyposition"
    aliases = ["slingposition"]
    locks = "cmd:all()"
    help_category = "Mounting"
    
    def parse(self):
        args = self.args.strip().split()
        self.carrier_name = args[0] if args else ""
        self.position = args[1] if len(args) > 1 else ""
    
    def func(self):
        if not self.carrier_name:
            self.caller.msg("Change position on which carrier?")
            return
        
        carrier = find_target(self.caller, self.carrier_name)
        if not carrier:
            self.caller.msg(f"Can't find '{self.carrier_name}' here.")
            return
        
        if not self.position:
            from .mounting.belly_mount import BELLY_POSITIONS
            
            lines = ["Available positions:"]
            for key, pos in BELLY_POSITIONS.items():
                lines.append(f"  {key}: {pos.name}")
            
            self.caller.msg("\n".join(lines))
            return
        
        from .mounting.belly_mount import BellyMountSystem
        
        success, message = BellyMountSystem.change_position(carrier, self.position)
        self.caller.msg(message)


class CmdBlanket(Command):
    """
    Manage saddle blanket for concealment.
    
    Usage:
      blanket <carrier>        - Cover with blanket
      blanket lift <carrier>   - Lift blanket to reveal
      blanket drop <carrier>   - Drop blanket back down
    """
    key = "blanket"
    locks = "cmd:all()"
    help_category = "Mounting"
    
    def parse(self):
        args = self.args.strip().split()
        
        if args and args[0].lower() in ("lift", "drop"):
            self.action = args[0].lower()
            self.carrier_name = args[1] if len(args) > 1 else ""
        else:
            self.action = "cover"
            self.carrier_name = args[0] if args else ""
    
    def func(self):
        if not self.carrier_name:
            self.caller.msg("Blanket which carrier?")
            return
        
        carrier = find_target(self.caller, self.carrier_name)
        if not carrier:
            self.caller.msg(f"Can't find '{self.carrier_name}' here.")
            return
        
        from .mounting.belly_mount import BellyMountSystem, SaddleBlanket
        
        if self.action == "cover":
            blanket = SaddleBlanket()
            result = BellyMountSystem.apply_blanket(carrier, blanket)
            self.caller.msg(result)
            
        elif self.action == "lift":
            result = BellyMountSystem.lift_blanket(carrier)
            self.caller.msg(result)
            self.caller.location.msg_contents(
                f"{self.caller.key} lifts the saddle blanket on {carrier.key}...",
                exclude=[self.caller]
            )
            
        elif self.action == "drop":
            result = BellyMountSystem.drop_blanket(carrier)
            self.caller.msg(result)


# =============================================================================
# RIDING COMMANDS
# =============================================================================

class CmdSaddle(Command):
    """
    Saddle a mount.
    
    Usage:
      saddle <mount> [type]
      saddle <mount> remove
      saddle list
      
    Types: basic, english, western, bareback, breeding, bondage, war, tandem
    """
    key = "saddle"
    locks = "cmd:all()"
    help_category = "Mounting"
    
    def parse(self):
        args = self.args.strip().split()
        self.mount_name = args[0] if args else ""
        self.saddle_type = args[1] if len(args) > 1 else "basic"
    
    def func(self):
        if not self.mount_name:
            self.caller.msg("Saddle whom?")
            return
        
        if self.mount_name.lower() == "list":
            from .mounting.riding import ALL_SADDLES
            
            lines = ["Available saddles:"]
            for key, saddle in ALL_SADDLES.items():
                lines.append(f"  {key}: {saddle.name}")
            
            self.caller.msg("\n".join(lines))
            return
        
        mount = find_target(self.caller, self.mount_name)
        if not mount:
            self.caller.msg(f"Can't find '{self.mount_name}' here.")
            return
        
        from .mounting.riding import RidingSystem, get_saddle, ALL_SADDLES
        
        if self.saddle_type.lower() == "remove":
            result = RidingSystem.unsaddle_mount(mount)
            self.caller.msg(result)
            return
        
        # Find saddle
        saddle_key = f"{self.saddle_type}_saddle"
        saddle = get_saddle(saddle_key)
        
        if not saddle:
            saddle = get_saddle(self.saddle_type)
        
        if not saddle:
            self.caller.msg(f"Unknown saddle type: {self.saddle_type}")
            return
        
        result = RidingSystem.saddle_mount(mount, saddle)
        self.caller.msg(result)


class CmdMount(Command):
    """
    Mount a rideable character.
    
    Usage:
      mount <target>
      mount <target> <position>
      
    Positions: astride, sidesaddle, backward, lying_forward, lying_backward
    """
    key = "mount"
    aliases = ["ride"]
    locks = "cmd:all()"
    help_category = "Mounting"
    
    def parse(self):
        args = self.args.strip().split()
        self.mount_name = args[0] if args else ""
        self.position = args[1] if len(args) > 1 else "astride"
    
    def func(self):
        if not self.mount_name:
            self.caller.msg("Mount whom?")
            return
        
        mount = find_target(self.caller, self.mount_name)
        if not mount:
            self.caller.msg(f"Can't find '{self.mount_name}' here.")
            return
        
        from .mounting.riding import RidingSystem, RidingPosition
        
        try:
            position = RidingPosition(self.position.lower())
        except ValueError:
            valid = [p.value for p in RidingPosition]
            self.caller.msg(f"Valid positions: {', '.join(valid)}")
            return
        
        success, message = RidingSystem.mount_rider(mount, self.caller, position)
        self.caller.msg(message)
        
        if success:
            self.caller.location.msg_contents(
                message,
                exclude=[self.caller]
            )


class CmdDismount(Command):
    """
    Dismount from what you're riding.
    
    Usage:
      dismount
    """
    key = "dismount"
    locks = "cmd:all()"
    help_category = "Mounting"
    
    def func(self):
        mount_ref = getattr(self.caller, 'mounted_on', '')
        
        if not mount_ref:
            self.caller.msg("You're not mounted on anything.")
            return
        
        # Would need to look up mount by dbref
        # For now, simplified implementation
        self.caller.attributes.remove("mounted_on")
        self.caller.msg("You dismount.")


class CmdGait(Command):
    """
    Change gait/speed when being ridden or carrying someone.
    
    Usage:
      gait <speed>
      
    Speeds: standing, walking, trotting, cantering, galloping
    """
    key = "gait"
    aliases = ["trot", "gallop", "walk", "canter"]
    locks = "cmd:all()"
    help_category = "Mounting"
    
    def func(self):
        # Check if caller can change gait (must be a mount)
        from .mounting.belly_mount import BellyMountSystem, CarrierGait
        from .mounting.riding import RidingSystem
        
        # Determine gait from command or args
        if self.cmdstring in ("trot", "gallop", "walk", "canter"):
            gait_name = self.cmdstring + "ing" if self.cmdstring != "trot" else "trotting"
            if self.cmdstring == "gallop":
                gait_name = "galloping"
        else:
            gait_name = self.args.strip().lower() if self.args else "standing"
        
        # Try to set gait
        try:
            gait = CarrierGait(gait_name)
        except ValueError:
            valid = [g.value for g in CarrierGait]
            self.caller.msg(f"Valid gaits: {', '.join(valid)}")
            return
        
        result = BellyMountSystem.change_gait(self.caller, gait)
        self.caller.msg(result)
        
        if gait != CarrierGait.STANDING:
            self.caller.location.msg_contents(
                result,
                exclude=[self.caller]
            )


class CmdBindToSaddle(Command):
    """
    Bind a rider to the saddle.
    
    Usage:
      bindsaddle <rider> on <mount>
      unbindsaddle <rider> on <mount>
    """
    key = "bindsaddle"
    aliases = ["saddlebind"]
    locks = "cmd:all()"
    help_category = "Mounting"
    
    def parse(self):
        args = self.args.strip()
        
        if " on " in args.lower():
            parts = args.lower().split(" on ")
            self.rider_name = parts[0].strip()
            self.mount_name = parts[1].strip()
        else:
            self.rider_name = args
            self.mount_name = ""
    
    def func(self):
        if not self.rider_name:
            self.caller.msg("Bind whom to the saddle?")
            return
        
        rider = find_target(self.caller, self.rider_name)
        if not rider:
            self.caller.msg(f"Can't find '{self.rider_name}' here.")
            return
        
        if not self.mount_name:
            # Try to find what they're mounted on
            self.caller.msg("Bind them to which mount's saddle?")
            return
        
        mount = find_target(self.caller, self.mount_name)
        if not mount:
            self.caller.msg(f"Can't find '{self.mount_name}' here.")
            return
        
        from .mounting.riding import RidingSystem
        
        success, message = RidingSystem.bind_rider_to_saddle(mount, rider)
        self.caller.msg(message)
        
        if success:
            rider.msg(f"{self.caller.key} binds you to the saddle! You can't dismount!")


class CmdUnbindSaddle(Command):
    """
    Release a rider from saddle bindings.
    
    Usage:
      unbindsaddle <rider> on <mount>
    """
    key = "unbindsaddle"
    locks = "cmd:all()"
    help_category = "Mounting"
    
    def parse(self):
        args = self.args.strip()
        
        if " on " in args.lower():
            parts = args.lower().split(" on ")
            self.rider_name = parts[0].strip()
            self.mount_name = parts[1].strip()
        else:
            self.rider_name = args
            self.mount_name = ""
    
    def func(self):
        if not self.rider_name or not self.mount_name:
            self.caller.msg("Usage: unbindsaddle <rider> on <mount>")
            return
        
        rider = find_target(self.caller, self.rider_name)
        mount = find_target(self.caller, self.mount_name)
        
        if not rider or not mount:
            self.caller.msg("Can't find one of those characters.")
            return
        
        from .mounting.riding import RidingSystem
        
        success, message = RidingSystem.unbind_rider(mount, rider)
        self.caller.msg(message)


# =============================================================================
# COMMAND SET
# =============================================================================

class MountingCmdSet(CmdSet):
    """Command set for mounting systems."""
    
    key = "MountingCmdSet"
    
    def at_cmdset_creation(self):
        # Harness commands
        self.add(CmdHarness())
        self.add(CmdLockHarness())
        self.add(CmdUnlockHarness())
        
        # Belly mount commands
        self.add(CmdSling())
        self.add(CmdBellyPosition())
        self.add(CmdBlanket())
        
        # Riding commands
        self.add(CmdSaddle())
        self.add(CmdMount())
        self.add(CmdDismount())
        self.add(CmdGait())
        self.add(CmdBindToSaddle())
        self.add(CmdUnbindSaddle())


__all__ = [
    "CmdHarness",
    "CmdLockHarness",
    "CmdUnlockHarness",
    "CmdSling",
    "CmdBellyPosition",
    "CmdBlanket",
    "CmdSaddle",
    "CmdMount",
    "CmdDismount",
    "CmdGait",
    "CmdBindToSaddle",
    "CmdUnbindSaddle",
    "MountingCmdSet",
]
