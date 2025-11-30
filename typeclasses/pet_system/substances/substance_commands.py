"""
Substance Commands
==================

Commands for potions and substances:
- Consuming potions
- Forcing substances
- Viewing effects
- Transformation
"""

from evennia import Command, CmdSet

from .potions import (
    get_substance, SubstanceSystem, ALL_SUBSTANCES
)
from .transformation import (
    get_transformation, TransformationSystem,
    POTION_TRANSFORMATION_MAP, TransformationType
)


class CmdDrink(Command):
    """
    Drink a potion or consume a substance.
    
    Usage:
      drink <potion>
      consume <substance>
    
    Examples:
      drink aphrodisiac
      drink fertility potion
    """
    
    key = "drink"
    aliases = ["consume", "quaff"]
    locks = "cmd:all()"
    
    def func(self):
        if not self.args:
            self.caller.msg("Drink what?")
            return
        
        potion_name = self.args.strip().lower()
        
        # Find the substance
        substance = None
        for key, sub in ALL_SUBSTANCES.items():
            if key == potion_name or sub.name.lower() == potion_name:
                substance = get_substance(key)
                break
        
        if not substance:
            self.caller.msg(f"You don't have any '{self.args.strip()}'.")
            return
        
        # Check for transformation potion
        if substance.key in POTION_TRANSFORMATION_MAP:
            tf_key = POTION_TRANSFORMATION_MAP[substance.key]
            transformation = get_transformation(tf_key)
            
            if transformation:
                success, msg = TransformationSystem.begin_transformation(
                    self.caller, transformation
                )
                self.caller.msg(f"{substance.get_consume_message()} {msg}")
                if success:
                    self.caller.location.msg_contents(
                        f"{self.caller.key}'s body begins to change...",
                        exclude=[self.caller]
                    )
                return
        
        # Normal substance consumption
        success, message = self.caller.consume_substance(substance)
        self.caller.msg(message)
        
        if success:
            self.caller.location.msg_contents(
                f"{self.caller.key} drinks a {substance.name}.",
                exclude=[self.caller]
            )


class CmdForce(Command):
    """
    Force someone to consume a substance.
    
    Usage:
      force <target> to drink <potion>
    
    Examples:
      force Luna to drink aphrodisiac
    """
    
    key = "force"
    locks = "cmd:all()"
    
    def func(self):
        if not self.args or " to drink " not in self.args.lower():
            self.caller.msg("Usage: force <target> to drink <potion>")
            return
        
        parts = self.args.lower().split(" to drink ")
        if len(parts) != 2:
            self.caller.msg("Usage: force <target> to drink <potion>")
            return
        
        target_name = parts[0].strip()
        potion_name = parts[1].strip()
        
        # Find target
        target = self.caller.search(target_name)
        if not target:
            return
        
        # Find substance
        substance = None
        for key, sub in ALL_SUBSTANCES.items():
            if key == potion_name or sub.name.lower() == potion_name:
                substance = get_substance(key)
                break
        
        if not substance:
            self.caller.msg(f"You don't have any '{parts[1].strip()}'.")
            return
        
        # Force consumption
        success, message = SubstanceSystem.apply_force(target, substance, self.caller)
        
        self.caller.msg(message)
        target.msg(f"{self.caller.key} forces you to consume {substance.name}! {message}")
        self.caller.location.msg_contents(
            message,
            exclude=[self.caller, target]
        )


class CmdEffects(Command):
    """
    View active substance effects.
    
    Usage:
      effects
      effects <target>
    """
    
    key = "effects"
    aliases = ["activeeffects"]
    locks = "cmd:all()"
    
    def func(self):
        if self.args:
            target = self.caller.search(self.args.strip())
            if not target:
                return
        else:
            target = self.caller
        
        if not hasattr(target, 'get_active_effects_display'):
            self.caller.msg(f"{target.key} is not affected by substances.")
            return
        
        display = target.get_active_effects_display()
        
        if target == self.caller:
            self.caller.msg(display)
        else:
            self.caller.msg(f"{target.key}'s {display}")


class CmdTransform(Command):
    """
    View transformation status or force revert.
    
    Usage:
      transform
      transform revert
      transform <target>
    """
    
    key = "transform"
    aliases = ["transformation", "tf"]
    locks = "cmd:all()"
    
    def func(self):
        args = self.args.strip().lower() if self.args else ""
        
        if args == "revert":
            message = TransformationSystem.force_revert(self.caller)
            self.caller.msg(message)
            return
        
        if args:
            target = self.caller.search(args)
            if not target:
                return
        else:
            target = self.caller
        
        if not hasattr(target, 'get_transformation_desc'):
            self.caller.msg(f"{target.key} cannot be transformed.")
            return
        
        desc = target.get_transformation_desc()
        
        if not desc:
            if target == self.caller:
                self.caller.msg("You are not currently transformed.")
            else:
                self.caller.msg(f"{target.key} is not transformed.")
        else:
            if target == self.caller:
                self.caller.msg(f"Transformation: {desc}")
            else:
                self.caller.msg(f"{target.key}: {desc}")


class CmdPotions(Command):
    """
    List available potions.
    
    Usage:
      potions
      potions <category>
    """
    
    key = "potions"
    aliases = ["substances", "drugs"]
    locks = "cmd:all()"
    
    def func(self):
        lines = ["=== Available Potions ==="]
        
        for key, substance in ALL_SUBSTANCES.items():
            effects = ", ".join([e.name for e in substance.effects])
            if not effects:
                # Check if it's a transformation potion
                if key in POTION_TRANSFORMATION_MAP:
                    effects = f"Transformation: {POTION_TRANSFORMATION_MAP[key]}"
            
            lines.append(f"  {substance.name} ({key}): {effects}")
        
        self.caller.msg("\n".join(lines))


class SubstanceCmdSet(CmdSet):
    """Commands for substances."""
    
    key = "SubstanceCmdSet"
    
    def at_cmdset_creation(self):
        self.add(CmdDrink())
        self.add(CmdForce())
        self.add(CmdEffects())
        self.add(CmdTransform())
        self.add(CmdPotions())
