"""
Hucow Farm Commands
===================

Commands for managing hucows, bulls, and farm facilities.
"""

from evennia import Command, CmdSet


# =============================================================================
# HUCOW MANAGEMENT
# =============================================================================

class CmdMakeHucow(Command):
    """
    Register someone as a hucow.
    
    Usage:
      makehucow <target> [cow name]
    """
    key = "makehucow"
    aliases = ["registerhucow", "cowify"]
    locks = "cmd:all()"
    
    def func(self):
        if not self.args:
            self.caller.msg("Make who into a hucow?")
            return
        
        args = self.args.strip().split(None, 1)
        target = self.caller.search(args[0])
        if not target:
            return
        
        cow_name = args[1] if len(args) > 1 else ""
        
        if not hasattr(target, 'initialize_hucow'):
            self.caller.msg("Target doesn't support hucow status.")
            return
        
        msg = target.initialize_hucow(self.caller, cow_name)
        
        self.caller.msg(f"You register {target.key} as a hucow. {msg}")
        target.msg(f"You have been registered as a hucow by {self.caller.key}. {msg}")


class CmdHucowStatus(Command):
    """
    View hucow status.
    
    Usage:
      hucowstatus [target]
      cowstatus [target]
    """
    key = "hucowstatus"
    aliases = ["cowstatus", "hstatus"]
    locks = "cmd:all()"
    
    def func(self):
        if not self.args:
            target = self.caller
        else:
            target = self.caller.search(self.args.strip())
            if not target:
                return
        
        if not hasattr(target, 'hucow_stats'):
            self.caller.msg("No hucow status available.")
            return
        
        if not target.is_hucow:
            self.caller.msg(f"{target.key} is not registered as a hucow.")
            return
        
        stats = target.hucow_stats
        self.caller.msg(stats.get_status_display())


class CmdInduceLactation(Command):
    """
    Begin lactation induction on a hucow.
    
    Usage:
      inducelactation <target>
    """
    key = "inducelactation"
    aliases = ["startlactation", "induce"]
    locks = "cmd:all()"
    
    def func(self):
        if not self.args:
            self.caller.msg("Induce who?")
            return
        
        target = self.caller.search(self.args.strip())
        if not target:
            return
        
        if not hasattr(target, 'hucow_stats') or not target.is_hucow:
            self.caller.msg("Not a registered hucow.")
            return
        
        stats = target.hucow_stats
        msg = stats.lactation.induce_lactation()
        target.save_hucow_stats(stats)
        
        self.caller.msg(f"You begin lactation induction on {target.key}. {msg}")
        target.msg(f"Lactation induction begins. Your breasts tingle as the treatment takes effect...")


class CmdMilk(Command):
    """
    Milk a hucow.
    
    Usage:
      milk <target>
    """
    key = "milk"
    locks = "cmd:all()"
    
    def func(self):
        if not self.args:
            self.caller.msg("Milk who?")
            return
        
        target = self.caller.search(self.args.strip())
        if not target:
            return
        
        if not hasattr(target, 'hucow_stats') or not target.is_hucow:
            self.caller.msg("Not a registered hucow.")
            return
        
        stats = target.hucow_stats
        
        if not target.is_lactating:
            self.caller.msg(f"{target.key} is not lactating.")
            return
        
        amount, msg = stats.lactation.milk()
        target.save_hucow_stats(stats)
        
        self.caller.msg(f"You milk {target.key}. {msg}")
        target.msg(f"You are milked by {self.caller.key}. Relief washes over you as {amount}ml flows out...")
        
        if self.caller.location:
            self.caller.location.msg_contents(
                f"{self.caller.key} milks {target.key}.",
                exclude=[self.caller, target]
            )


class CmdProduceMilk(Command):
    """
    Simulate milk production over time.
    
    Usage:
      producemilk <target> [hours]
    """
    key = "producemilk"
    locks = "cmd:perm(Builder)"
    
    def func(self):
        if not self.args:
            self.caller.msg("Usage: producemilk <target> [hours]")
            return
        
        args = self.args.strip().split()
        target = self.caller.search(args[0])
        if not target:
            return
        
        hours = float(args[1]) if len(args) > 1 else 1.0
        
        if not hasattr(target, 'hucow_stats') or not target.is_hucow:
            self.caller.msg("Not a hucow.")
            return
        
        stats = target.hucow_stats
        produced = stats.lactation.produce_milk(hours)
        target.save_hucow_stats(stats)
        
        self.caller.msg(f"{target.key} produced {produced}ml over {hours} hours. "
                       f"Fill: {stats.lactation.fill_percentage:.0f}%")


# =============================================================================
# BULL MANAGEMENT
# =============================================================================

class CmdMakeBull(Command):
    """
    Register someone as a bull.
    
    Usage:
      makebull <target> [name]
      makebull <target> futa [name]
    """
    key = "makebull"
    aliases = ["registerbull"]
    locks = "cmd:all()"
    
    def func(self):
        if not self.args:
            self.caller.msg("Make who into a bull?")
            return
        
        args = self.args.strip().split()
        target = self.caller.search(args[0])
        if not target:
            return
        
        is_futa = "futa" in args
        name = ""
        for arg in args[1:]:
            if arg != "futa":
                name = arg
                break
        
        if not hasattr(target, 'initialize_bull'):
            self.caller.msg("Target doesn't support bull status.")
            return
        
        from .bulls import BullType
        bull_type = BullType.FUTANARI if is_futa else BullType.NATURAL
        
        msg = target.initialize_bull(self.caller, name, bull_type, is_futa)
        
        self.caller.msg(f"You register {target.key} as a bull. {msg}")
        target.msg(f"You have been registered as a bull by {self.caller.key}. {msg}")


class CmdBullStatus(Command):
    """
    View bull status.
    
    Usage:
      bullstatus [target]
    """
    key = "bullstatus"
    aliases = ["bstatus"]
    locks = "cmd:all()"
    
    def func(self):
        if not self.args:
            target = self.caller
        else:
            target = self.caller.search(self.args.strip())
            if not target:
                return
        
        if not hasattr(target, 'bull_stats'):
            self.caller.msg("No bull status available.")
            return
        
        if not target.is_bull:
            self.caller.msg(f"{target.key} is not registered as a bull.")
            return
        
        stats = target.bull_stats
        self.caller.msg(stats.get_status_display())


class CmdBreed(Command):
    """
    Have a bull breed a hucow.
    
    Usage:
      breed <bull> with <hucow>
    """
    key = "breed"
    locks = "cmd:all()"
    
    def func(self):
        if not self.args or " with " not in self.args:
            self.caller.msg("Usage: breed <bull> with <hucow>")
            return
        
        bull_name, hucow_name = self.args.strip().split(" with ", 1)
        
        bull = self.caller.search(bull_name)
        if not bull:
            return
        
        hucow = self.caller.search(hucow_name)
        if not hucow:
            return
        
        # Verify both have proper stats
        if not hasattr(bull, 'bull_stats') or not bull.is_bull:
            self.caller.msg(f"{bull.key} is not a registered bull.")
            return
        
        if not hasattr(hucow, 'hucow_stats') or not hucow.is_hucow:
            self.caller.msg(f"{hucow.key} is not a registered hucow.")
            return
        
        bull_stats = bull.bull_stats
        hucow_stats = hucow.hucow_stats
        
        # Check if bull is ready
        if not bull_stats.breeding.is_ready:
            self.caller.msg(f"{bull.key} is not ready to breed (state: {bull_stats.breeding.rut_state.value}).")
            return
        
        # Check if hucow can be bred
        if hucow_stats.breeding.is_pregnant:
            self.caller.msg(f"{hucow.key} is already pregnant.")
            return
        
        if not hucow_stats.breeding.in_heat:
            self.caller.msg(f"{hucow.key} is not in heat. Breeding anyway...")
        
        # Perform breeding
        breeding_msg, pleasure = bull_stats.breeding.perform_breeding(hucow.key)
        
        # Calculate conception
        conception_chance = bull_stats.breeding.calculate_conception_chance(
            hucow_stats.breeding.fertility_rating
        )
        
        success, result_msg = hucow_stats.breeding.breed(bull.dbref, bull.key)
        
        if success:
            bull_stats.breeding.successful_impregnations += 1
        
        # Save stats
        bull.save_bull_stats(bull_stats)
        hucow.save_hucow_stats(hucow_stats)
        
        # Messages
        self.caller.msg(f"{bull.key} {breeding_msg}")
        self.caller.msg(result_msg)
        
        bull.msg(f"You breed {hucow.key}. {result_msg}")
        hucow.msg(f"You are bred by {bull.key}! {result_msg}")
        
        if self.caller.location:
            self.caller.location.msg_contents(
                f"{bull.key} breeds {hucow.key}!",
                exclude=[self.caller, bull, hucow]
            )


class CmdTriggerHeat(Command):
    """
    Trigger heat cycle in a hucow.
    
    Usage:
      triggerheat <target>
    """
    key = "triggerheat"
    aliases = ["induceheat"]
    locks = "cmd:all()"
    
    def func(self):
        if not self.args:
            self.caller.msg("Trigger heat in who?")
            return
        
        target = self.caller.search(self.args.strip())
        if not target:
            return
        
        if not hasattr(target, 'hucow_stats') or not target.is_hucow:
            self.caller.msg("Not a hucow.")
            return
        
        stats = target.hucow_stats
        msg = stats.breeding.trigger_heat()
        target.save_hucow_stats(stats)
        
        self.caller.msg(f"You trigger heat in {target.key}. {msg}")
        target.msg(f"Heat washes over you! Your body burns with need... {msg}")


class CmdCheckPregnancy(Command):
    """
    Check pregnancy status.
    
    Usage:
      checkpregnancy <target>
    """
    key = "checkpregnancy"
    aliases = ["pregcheck", "pregnancy"]
    locks = "cmd:all()"
    
    def func(self):
        if not self.args:
            self.caller.msg("Check who?")
            return
        
        target = self.caller.search(self.args.strip())
        if not target:
            return
        
        if not hasattr(target, 'hucow_stats') or not target.is_hucow:
            self.caller.msg("Not a hucow.")
            return
        
        stats = target.hucow_stats
        breeding = stats.breeding
        
        if not breeding.is_pregnant:
            self.caller.msg(f"{target.key} is not pregnant.")
            return
        
        self.caller.msg(f"=== Pregnancy Status: {target.key} ===")
        self.caller.msg(f"Day: {breeding.pregnancy_day}/{breeding.pregnancy_duration}")
        self.caller.msg(f"Progress: {breeding.pregnancy_progress:.1f}%")
        self.caller.msg(f"Trimester: {breeding.trimester}")
        self.caller.msg(f"Sire: {breeding.sire_name}")
        self.caller.msg(f"Expected Offspring: {breeding.litter_size}")


class CmdAdvancePregnancy(Command):
    """
    Advance pregnancy by days.
    
    Usage:
      advancepregnancy <target> [days]
    """
    key = "advancepregnancy"
    locks = "cmd:perm(Builder)"
    
    def func(self):
        if not self.args:
            self.caller.msg("Usage: advancepregnancy <target> [days]")
            return
        
        args = self.args.strip().split()
        target = self.caller.search(args[0])
        if not target:
            return
        
        days = int(args[1]) if len(args) > 1 else 1
        
        if not hasattr(target, 'hucow_stats') or not target.is_hucow:
            self.caller.msg("Not a hucow.")
            return
        
        stats = target.hucow_stats
        
        for _ in range(days):
            gave_birth, msg = stats.breeding.advance_pregnancy()
            if gave_birth:
                self.caller.msg(msg)
                target.msg(f"You give birth! {msg}")
                break
        
        target.save_hucow_stats(stats)
        self.caller.msg(f"Advanced pregnancy by {days} days. "
                       f"Now at day {stats.breeding.pregnancy_day}")


# =============================================================================
# FARM MANAGEMENT
# =============================================================================

class CmdCreateFarm(Command):
    """
    Create a new farm.
    
    Usage:
      createfarm <name>
    """
    key = "createfarm"
    locks = "cmd:perm(Builder)"
    
    def func(self):
        if not self.args:
            self.caller.msg("Name the farm.")
            return
        
        from .facilities import create_standard_farm
        
        farm = create_standard_farm(
            self.args.strip(),
            self.caller.dbref,
            self.caller.key,
        )
        
        # Store on caller
        self.caller.db.owned_farm = farm.to_dict()
        
        self.caller.msg(f"Created farm: {farm.name}")
        self.caller.msg(farm.get_status_display())


class CmdFarmStatus(Command):
    """
    View farm status.
    
    Usage:
      farmstatus
    """
    key = "farmstatus"
    locks = "cmd:all()"
    
    def func(self):
        if not self.caller.db.owned_farm:
            self.caller.msg("You don't own a farm.")
            return
        
        from .facilities import Farm
        farm = Farm.from_dict(self.caller.db.owned_farm)
        
        self.caller.msg(farm.get_status_display())


class CmdAddToHerd(Command):
    """
    Add a hucow to the farm's herd.
    
    Usage:
      addtoherd <hucow>
    """
    key = "addtoherd"
    locks = "cmd:all()"
    
    def func(self):
        if not self.args:
            self.caller.msg("Add who?")
            return
        
        if not self.caller.db.owned_farm:
            self.caller.msg("You don't own a farm.")
            return
        
        target = self.caller.search(self.args.strip())
        if not target:
            return
        
        if not hasattr(target, 'is_hucow') or not target.is_hucow:
            self.caller.msg("Not a hucow.")
            return
        
        from .facilities import Farm
        farm = Farm.from_dict(self.caller.db.owned_farm)
        
        # Add to first herd
        if farm.herds:
            herd = list(farm.herds.values())[0]
            msg = herd.add_member(target.dbref)
            self.caller.db.owned_farm = farm.to_dict()
            self.caller.msg(msg)
            target.msg(f"You have been added to the herd at {farm.name}.")
        else:
            self.caller.msg("No herds on this farm.")


# =============================================================================
# COMMAND SET
# =============================================================================

class HucowCmdSet(CmdSet):
    """Commands for hucow farm system."""
    
    key = "hucow_cmdset"
    
    def at_cmdset_creation(self):
        # Hucow management
        self.add(CmdMakeHucow())
        self.add(CmdHucowStatus())
        self.add(CmdInduceLactation())
        self.add(CmdMilk())
        self.add(CmdProduceMilk())
        
        # Bull management
        self.add(CmdMakeBull())
        self.add(CmdBullStatus())
        self.add(CmdBreed())
        self.add(CmdTriggerHeat())
        self.add(CmdCheckPregnancy())
        self.add(CmdAdvancePregnancy())
        
        # Farm management
        self.add(CmdCreateFarm())
        self.add(CmdFarmStatus())
        self.add(CmdAddToHerd())
