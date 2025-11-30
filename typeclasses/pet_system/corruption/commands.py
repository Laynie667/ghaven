"""
Corruption Commands
===================

Commands for transformation and corruption systems.
"""

from evennia import Command, CmdSet


class CmdTransformationStatus(Command):
    """
    View transformation status.
    
    Usage:
        transformstatus [target]
        tfstatus [target]
    
    Shows active transformations and their progress.
    """
    
    key = "transformstatus"
    aliases = ["tfstatus", "corruptionstatus"]
    locks = "cmd:all()"
    
    def func(self):
        caller = self.caller
        
        target = caller
        if self.args:
            target = caller.search(self.args.strip())
            if not target:
                return
        
        if not hasattr(target, 'transformations'):
            caller.msg(f"{target.key} has no transformation data.")
            return
        
        mgr = target.transformations
        caller.msg(mgr.get_summary())


class CmdStartTransformation(Command):
    """
    Begin a transformation on a target.
    
    Usage:
        transform <target> = <type>
        transform/list
    
    Types: bimbo, hucow, slut, demon, doll, pet, breeding_sow, futa
    """
    
    key = "transform"
    aliases = ["starttransform", "corrupt"]
    locks = "cmd:perm(Builder)"
    
    def func(self):
        caller = self.caller
        
        if "list" in self.switches:
            from ..corruption import TransformationType
            types = [t.value for t in TransformationType]
            caller.msg(f"Transformation types: {', '.join(types)}")
            return
        
        if "=" not in self.args:
            caller.msg("Usage: transform <target> = <type>")
            return
        
        target_name, trans_type = self.args.split("=", 1)
        target = caller.search(target_name.strip())
        if not target:
            return
        
        if not hasattr(target, 'transformations'):
            caller.msg(f"{target.key} cannot be transformed.")
            return
        
        from ..corruption import TransformationType
        
        try:
            transformation = TransformationType[trans_type.strip().upper()]
        except KeyError:
            caller.msg(f"Unknown type. Use transform/list to see types.")
            return
        
        mgr = target.transformations
        success, msg = mgr.start_transformation(transformation)
        target.db.transformations = mgr.to_dict()
        
        caller.msg(msg)
        if success:
            target.msg(f"You feel something changing within you... {transformation.value} transformation begins.")


class CmdApplyCorruption(Command):
    """
    Apply corruption to progress a transformation.
    
    Usage:
        applycorruption <target> = <amount>
        applycorruption <target> = <type>, <amount>
    
    Applies corruption points to progress transformations.
    Sources: cum, milk, magic, ritual, item, contact, mental, substance
    """
    
    key = "applycorruption"
    aliases = ["addcorruption", "corrupt"]
    locks = "cmd:perm(Builder)"
    
    def func(self):
        caller = self.caller
        
        if "=" not in self.args:
            caller.msg("Usage: applycorruption <target> = [type,] <amount>")
            return
        
        target_name, rest = self.args.split("=", 1)
        target = caller.search(target_name.strip())
        if not target:
            return
        
        if not hasattr(target, 'transformations'):
            caller.msg(f"{target.key} cannot be corrupted.")
            return
        
        # Parse type and amount
        parts = rest.split(",")
        if len(parts) >= 2:
            source = parts[0].strip().lower()
            try:
                amount = int(parts[1].strip())
            except ValueError:
                caller.msg("Amount must be a number.")
                return
        else:
            source = "magic"
            try:
                amount = int(parts[0].strip())
            except ValueError:
                caller.msg("Amount must be a number.")
                return
        
        mgr = target.transformations
        
        # Apply to all active transformations
        messages = []
        for trans_type, trans in mgr.transformations.items():
            msg, stage_msg = mgr.add_corruption(trans_type, amount, source)
            if msg:
                messages.append(msg)
            if stage_msg:
                messages.append(stage_msg)
        
        target.db.transformations = mgr.to_dict()
        
        if messages:
            caller.msg(" | ".join(messages))
            target.msg(f"Corruption seeps into you... {' | '.join(messages)}")
        else:
            caller.msg("No active transformations to corrupt.")


class CmdRemoveTransformation(Command):
    """
    Remove or reverse a transformation.
    
    Usage:
        removetransform <target> = <type>
        removetransform/force <target> = <type>
    
    Attempts to remove a transformation. /force ignores reversibility.
    """
    
    key = "removetransform"
    aliases = ["cleanse", "purify"]
    locks = "cmd:perm(Builder)"
    
    def func(self):
        caller = self.caller
        
        if "=" not in self.args:
            caller.msg("Usage: removetransform <target> = <type>")
            return
        
        target_name, trans_type = self.args.split("=", 1)
        target = caller.search(target_name.strip())
        if not target:
            return
        
        if not hasattr(target, 'transformations'):
            caller.msg(f"{target.key} has no transformations.")
            return
        
        from ..corruption import TransformationType
        
        try:
            transformation = TransformationType[trans_type.strip().upper()]
        except KeyError:
            caller.msg("Unknown transformation type.")
            return
        
        mgr = target.transformations
        
        if transformation not in mgr.transformations:
            caller.msg(f"{target.key} doesn't have that transformation.")
            return
        
        trans = mgr.transformations[transformation]
        
        if not trans.is_reversible and "force" not in self.switches:
            caller.msg(f"That transformation is permanent. Use /force to override.")
            return
        
        del mgr.transformations[transformation]
        target.db.transformations = mgr.to_dict()
        
        caller.msg(f"Removed {transformation.value} transformation from {target.key}.")
        target.msg(f"The {transformation.value} corruption fades from your body...")


class CmdSetResistance(Command):
    """
    Set transformation resistance.
    
    Usage:
        setresistance <target> = <amount>
    
    Sets base transformation resistance (0-100).
    """
    
    key = "setresistance"
    aliases = ["tfresistance"]
    locks = "cmd:perm(Builder)"
    
    def func(self):
        caller = self.caller
        
        if "=" not in self.args:
            caller.msg("Usage: setresistance <target> = <amount>")
            return
        
        target_name, amount_str = self.args.split("=", 1)
        target = caller.search(target_name.strip())
        if not target:
            return
        
        try:
            amount = int(amount_str.strip())
            amount = max(0, min(100, amount))
        except ValueError:
            caller.msg("Amount must be 0-100.")
            return
        
        if not hasattr(target, 'transformations'):
            caller.msg(f"{target.key} cannot be transformed.")
            return
        
        mgr = target.transformations
        mgr.transformation_resistance = amount
        target.db.transformations = mgr.to_dict()
        
        caller.msg(f"{target.key}'s transformation resistance set to {amount}.")


class CmdBimbofy(Command):
    """
    Quick bimbofication.
    
    Usage:
        bimbofy <target>
        bimbofy <target> = <amount>
    
    Applies bimbo transformation corruption. Default 25 points.
    """
    
    key = "bimbofy"
    locks = "cmd:perm(Builder)"
    
    def func(self):
        caller = self.caller
        
        if not self.args:
            caller.msg("Bimbofy who?")
            return
        
        if "=" in self.args:
            target_name, amount_str = self.args.split("=", 1)
            try:
                amount = int(amount_str.strip())
            except ValueError:
                amount = 25
        else:
            target_name = self.args
            amount = 25
        
        target = caller.search(target_name.strip())
        if not target:
            return
        
        if not hasattr(target, 'transformations'):
            caller.msg(f"{target.key} cannot be bimbofied.")
            return
        
        from ..corruption import TransformationType
        
        mgr = target.transformations
        
        # Start if not started
        if TransformationType.BIMBO not in mgr.transformations:
            mgr.start_transformation(TransformationType.BIMBO)
        
        msg, stage_msg = mgr.add_corruption(TransformationType.BIMBO, amount, "magic")
        target.db.transformations = mgr.to_dict()
        
        result = f"Applied {amount} bimbo corruption to {target.key}."
        if msg:
            result += f" {msg}"
        if stage_msg:
            result += f" {stage_msg}"
        
        caller.msg(result)
        
        # Flavor text for target
        trans = mgr.transformations[TransformationType.BIMBO]
        if trans.progress < 30:
            target.msg("You feel... giggly. Was thinking always this hard?")
        elif trans.progress < 60:
            target.msg("Like, whatever! Your thoughts feel all soft and fuzzy~")
        elif trans.progress < 90:
            target.msg("Omigosh! You feel SO much better not thinking so much!")
        else:
            target.msg("Teehee! Thinking is, like, totally overrated! You just wanna be pretty and make people happy~")


class CmdDemonize(Command):
    """
    Apply demonic corruption.
    
    Usage:
        demonize <target>
        demonize <target> = <amount>
    
    Applies demon transformation. Default 20 points.
    """
    
    key = "demonize"
    aliases = ["demoncorrupt"]
    locks = "cmd:perm(Builder)"
    
    def func(self):
        caller = self.caller
        
        if not self.args:
            caller.msg("Demonize who?")
            return
        
        if "=" in self.args:
            target_name, amount_str = self.args.split("=", 1)
            try:
                amount = int(amount_str.strip())
            except ValueError:
                amount = 20
        else:
            target_name = self.args
            amount = 20
        
        target = caller.search(target_name.strip())
        if not target:
            return
        
        if not hasattr(target, 'transformations'):
            caller.msg(f"{target.key} cannot be demonized.")
            return
        
        from ..corruption import TransformationType
        
        mgr = target.transformations
        
        if TransformationType.DEMON not in mgr.transformations:
            mgr.start_transformation(TransformationType.DEMON)
        
        msg, stage_msg = mgr.add_corruption(TransformationType.DEMON, amount, "corruption")
        target.db.transformations = mgr.to_dict()
        
        caller.msg(f"Applied {amount} demonic corruption to {target.key}. {msg} {stage_msg}")
        
        trans = mgr.transformations[TransformationType.DEMON]
        if trans.progress < 30:
            target.msg("A dark warmth spreads through you... your eyes flash red for a moment.")
        elif trans.progress < 60:
            target.msg("Horns begin to bud from your forehead. Your desires grow... darker.")
        else:
            target.msg("Infernal power courses through you. You hunger for mortal souls...")


class CorruptionCmdSet(CmdSet):
    """Commands for corruption system."""
    
    key = "corruption_cmdset"
    
    def at_cmdset_creation(self):
        self.add(CmdTransformationStatus())
        self.add(CmdStartTransformation())
        self.add(CmdApplyCorruption())
        self.add(CmdRemoveTransformation())
        self.add(CmdSetResistance())
        self.add(CmdBimbofy())
        self.add(CmdDemonize())
