"""
Breeding Commands
=================

Commands for breeding and pregnancy management:
- Breeding attempts
- Pregnancy tracking
- Birth
- Offspring management
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
# BREEDING COMMANDS
# =============================================================================

class CmdBreed(Command):
    """
    Attempt to breed two characters/pets.
    
    Usage:
      breed <male> with <female>
      breed <male> <female>
      
    Factors affecting conception:
    - Female in heat (+30%)
    - Knotting occurred (+20%)
    - Breeding harness (+10-25%)
    - Base fertility/virility stats
    
    Examples:
      breed Rex with Luna
      breed Thunderhoof Luna
    """
    key = "breed"
    locks = "cmd:all()"
    help_category = "Breeding"
    
    def parse(self):
        args = self.args.strip()
        
        if " with " in args.lower():
            parts = args.lower().split(" with ")
            self.male_name = parts[0].strip()
            self.female_name = parts[1].strip()
        else:
            parts = args.split()
            self.male_name = parts[0] if parts else ""
            self.female_name = parts[1] if len(parts) > 1 else ""
    
    def func(self):
        if not self.male_name or not self.female_name:
            self.caller.msg("Usage: breed <male> with <female>")
            return
        
        male = find_target(self.caller, self.male_name)
        female = find_target(self.caller, self.female_name)
        
        if not male:
            self.caller.msg(f"Can't find '{self.male_name}' here.")
            return
        
        if not female:
            self.caller.msg(f"Can't find '{self.female_name}' here.")
            return
        
        # Check if female already pregnant
        if hasattr(female, 'is_pregnant') and female.is_pregnant():
            self.caller.msg(f"{female.key} is already pregnant!")
            return
        
        from .pets.feral_offspring import BreedingSystem
        
        # Gather modifiers
        was_knotted = False  # Would check sexual state
        breeding_harness = False
        
        if hasattr(female, 'worn_harness'):
            harness = female.worn_harness
            if harness and harness.breeding_bonus > 0:
                breeding_harness = True
        
        # Attempt conception
        conceived, pregnancy, message = BreedingSystem.attempt_conception(
            female, male,
            was_knotted=was_knotted,
            breeding_harness=breeding_harness
        )
        
        self.caller.msg(message)
        
        if conceived:
            self.caller.location.msg_contents(
                f"{male.key} breeds {female.key} successfully!",
                exclude=[self.caller]
            )
        else:
            self.caller.location.msg_contents(
                f"{male.key} breeds {female.key}.",
                exclude=[self.caller]
            )


class CmdPregnancy(Command):
    """
    Check pregnancy status.
    
    Usage:
      pregnancy <target>
      pregnancy me
    """
    key = "pregnancy"
    aliases = ["pregnant", "pregstatus"]
    locks = "cmd:all()"
    help_category = "Breeding"
    
    def func(self):
        target_name = self.args.strip() if self.args else "me"
        
        if target_name.lower() == "me":
            target = self.caller
        else:
            target = find_target(self.caller, target_name)
        
        if not target:
            self.caller.msg(f"Can't find '{target_name}' here.")
            return
        
        if not hasattr(target, 'current_pregnancy'):
            self.caller.msg(f"{target.key} can't get pregnant.")
            return
        
        pregnancy = target.current_pregnancy
        
        if not pregnancy or not pregnancy.is_active:
            self.caller.msg(f"{target.key} is not pregnant.")
            return
        
        lines = [f"|wPregnancy Status for {target.key}|n"]
        lines.append(f"Father: {pregnancy.father_name} ({pregnancy.father_species})")
        lines.append(f"Stage: {pregnancy.stage.value}")
        lines.append(f"Progress: {pregnancy.get_progress_percentage():.1f}%")
        lines.append(f"Days pregnant: {pregnancy.get_days_pregnant()}")
        lines.append(f"Days remaining: {pregnancy.get_days_remaining()}")
        lines.append(f"Expected litter size: {pregnancy.litter_size}")
        lines.append(f"Belly: {pregnancy.get_belly_description()}")
        
        if pregnancy.complications:
            lines.append(f"|rComplications: {', '.join(pregnancy.complications)}|n")
        
        self.caller.msg("\n".join(lines))


class CmdGiveBirth(Command):
    """
    Trigger birth when pregnancy is ready.
    
    Usage:
      givebirth
      givebirth <target>
    """
    key = "givebirth"
    aliases = ["birth", "deliver"]
    locks = "cmd:all()"
    help_category = "Breeding"
    
    def func(self):
        target_name = self.args.strip() if self.args else ""
        
        if not target_name:
            target = self.caller
        else:
            target = find_target(self.caller, target_name)
        
        if not target:
            self.caller.msg(f"Can't find '{target_name}' here.")
            return
        
        if not hasattr(target, 'current_pregnancy'):
            self.caller.msg(f"{target.key} can't give birth.")
            return
        
        pregnancy = target.current_pregnancy
        
        if not pregnancy or not pregnancy.is_active:
            self.caller.msg(f"{target.key} is not pregnant.")
            return
        
        if not pregnancy.is_due():
            progress = pregnancy.get_progress_percentage()
            self.caller.msg(f"{target.key} is only {progress:.1f}% through pregnancy. Not ready yet.")
            return
        
        from .pets.feral_offspring import BreedingSystem
        
        # Give birth
        offspring_list = BreedingSystem.give_birth(pregnancy)
        
        # Update target's pregnancy state
        target.attributes.add("current_pregnancy", pregnancy.to_dict())
        
        # Add offspring to history
        for offspring in offspring_list:
            target.add_offspring(offspring)
        
        # Generate birth message
        litter_desc = BreedingSystem.get_litter_description(offspring_list)
        
        self.caller.msg(f"|y{target.key} gives birth!|n\n{litter_desc}")
        self.caller.location.msg_contents(
            f"|y{target.key} gives birth to {len(offspring_list)} offspring!|n",
            exclude=[self.caller]
        )


class CmdOffspring(Command):
    """
    View offspring information.
    
    Usage:
      offspring <target>
      offspring me
      offspring <target> history
    """
    key = "offspring"
    aliases = ["litter", "children"]
    locks = "cmd:all()"
    help_category = "Breeding"
    
    def parse(self):
        args = self.args.strip().split()
        self.target_name = args[0] if args else "me"
        self.show_history = "history" in args
    
    def func(self):
        if self.target_name.lower() == "me":
            target = self.caller
        else:
            target = find_target(self.caller, self.target_name)
        
        if not target:
            self.caller.msg(f"Can't find '{self.target_name}' here.")
            return
        
        if not hasattr(target, 'offspring_history'):
            self.caller.msg(f"{target.key} has no offspring records.")
            return
        
        history = target.offspring_history
        
        if not history:
            self.caller.msg(f"{target.key} has no offspring.")
            return
        
        lines = [f"|wOffspring of {target.key}|n"]
        lines.append(f"Total offspring: {len(history)}")
        lines.append("")
        
        for offspring_data in history[-10:]:  # Show last 10
            from .pets.feral_offspring import Offspring
            offspring = Offspring.from_dict(offspring_data)
            
            status = "|g(alive)|n" if offspring.is_alive else "|r(deceased)|n"
            lines.append(f"  {offspring.name} - {offspring.sex} {offspring.species} {status}")
            lines.append(f"    Age: {offspring.get_age_days()} days ({offspring.stage.value})")
        
        if len(history) > 10:
            lines.append(f"  ... and {len(history) - 10} more")
        
        self.caller.msg("\n".join(lines))


class CmdBreedingRecords(Command):
    """
    View breeding records and lineage.
    
    Usage:
      breedrecords <target>
      breedrecords me
    """
    key = "breedrecords"
    aliases = ["lineage", "pedigree"]
    locks = "cmd:all()"
    help_category = "Breeding"
    
    def func(self):
        target_name = self.args.strip() if self.args else "me"
        
        if target_name.lower() == "me":
            target = self.caller
        else:
            target = find_target(self.caller, target_name)
        
        if not target:
            self.caller.msg(f"Can't find '{target_name}' here.")
            return
        
        lines = [f"|wBreeding Records for {target.key}|n"]
        
        # Pregnancy history
        if hasattr(target, 'pregnancy_history'):
            preg_history = target.pregnancy_history
            lines.append(f"\nPregnancies: {len(preg_history)}")
            
            for preg_data in preg_history[-5:]:
                from .pets.feral_offspring import Pregnancy
                preg = Pregnancy.from_dict(preg_data)
                lines.append(f"  Sired by {preg.father_name}, litter of {preg.litter_size}")
        
        # Offspring count
        if hasattr(target, 'offspring_history'):
            offspring = target.offspring_history
            lines.append(f"\nTotal offspring: {len(offspring)}")
            
            # Count by species
            species_count = {}
            for o in offspring:
                sp = o.get('species', 'unknown')
                species_count[sp] = species_count.get(sp, 0) + 1
            
            for sp, count in species_count.items():
                lines.append(f"  {sp}: {count}")
        
        # Siring history (if male)
        if hasattr(target, 'siring_history'):
            sired = target.siring_history
            lines.append(f"\nOffspring sired: {len(sired)}")
        
        self.caller.msg("\n".join(lines))


class CmdHeat(Command):
    """
    Check or induce heat cycle.
    
    Usage:
      heat <target>           - Check heat status
      heat <target> induce    - Induce heat (requires item/ability)
    """
    key = "heat"
    aliases = ["heatcycle", "estrus"]
    locks = "cmd:all()"
    help_category = "Breeding"
    
    def parse(self):
        args = self.args.strip().split()
        self.target_name = args[0] if args else ""
        self.induce = len(args) > 1 and args[1].lower() == "induce"
    
    def func(self):
        if not self.target_name:
            self.caller.msg("Check heat on whom?")
            return
        
        target = find_target(self.caller, self.target_name)
        if not target:
            self.caller.msg(f"Can't find '{self.target_name}' here.")
            return
        
        # Check for heat status
        in_heat = getattr(target, 'in_heat', False)
        heat_cycle_day = getattr(target, 'heat_cycle_day', 0)
        
        if self.induce:
            # Would require specific item or ability
            self.caller.msg("Heat induction requires a fertility potion or special ability.")
            return
        
        if in_heat:
            self.caller.msg(f"|r{target.key} is in heat!|n They are highly fertile.")
        else:
            self.caller.msg(f"{target.key} is not in heat. (Cycle day: {heat_cycle_day})")


class CmdFertility(Command):
    """
    Check fertility stats.
    
    Usage:
      fertility <target>
    """
    key = "fertility"
    aliases = ["fertile"]
    locks = "cmd:all()"
    help_category = "Breeding"
    
    def func(self):
        target_name = self.args.strip() if self.args else "me"
        
        if target_name.lower() == "me":
            target = self.caller
        else:
            target = find_target(self.caller, target_name)
        
        if not target:
            self.caller.msg(f"Can't find '{target_name}' here.")
            return
        
        lines = [f"|wFertility Stats for {target.key}|n"]
        
        # Get stats from various sources
        fertility = getattr(target, 'fertility', 50)
        virility = getattr(target, 'virility', 50)
        in_heat = getattr(target, 'in_heat', False)
        
        if hasattr(target, 'current_pregnancy') and target.current_pregnancy:
            lines.append("|yCurrently pregnant|n")
        
        lines.append(f"Fertility: {fertility}/100")
        lines.append(f"Virility: {virility}/100")
        lines.append(f"In heat: {'|rYes|n' if in_heat else 'No'}")
        
        # Calculate base conception chance
        from .pets.feral_offspring import BreedingSystem
        
        base_chance = BreedingSystem.calculate_conception_chance(
            fertility, virility, False, in_heat, False
        )
        lines.append(f"Base conception chance: {base_chance}%")
        
        with_knot = BreedingSystem.calculate_conception_chance(
            fertility, virility, True, in_heat, False
        )
        lines.append(f"With knotting: {with_knot}%")
        
        with_harness = BreedingSystem.calculate_conception_chance(
            fertility, virility, True, in_heat, True
        )
        lines.append(f"With harness + knot: {with_harness}%")
        
        self.caller.msg("\n".join(lines))


class CmdNameOffspring(Command):
    """
    Name an offspring.
    
    Usage:
      nameoffspring <id> <name>
    """
    key = "nameoffspring"
    locks = "cmd:all()"
    help_category = "Breeding"
    
    def parse(self):
        args = self.args.strip().split(None, 1)
        self.offspring_id = args[0] if args else ""
        self.new_name = args[1] if len(args) > 1 else ""
    
    def func(self):
        if not self.offspring_id or not self.new_name:
            self.caller.msg("Usage: nameoffspring <id> <name>")
            return
        
        # Would search through offspring records and update name
        self.caller.msg(f"Offspring {self.offspring_id} named '{self.new_name}'.")


# =============================================================================
# COMMAND SET
# =============================================================================

class BreedingCmdSet(CmdSet):
    """Command set for breeding systems."""
    
    key = "BreedingCmdSet"
    
    def at_cmdset_creation(self):
        self.add(CmdBreed())
        self.add(CmdPregnancy())
        self.add(CmdGiveBirth())
        self.add(CmdOffspring())
        self.add(CmdBreedingRecords())
        self.add(CmdHeat())
        self.add(CmdFertility())
        self.add(CmdNameOffspring())


__all__ = [
    "CmdBreed",
    "CmdPregnancy",
    "CmdGiveBirth",
    "CmdOffspring",
    "CmdBreedingRecords",
    "CmdHeat",
    "CmdFertility",
    "CmdNameOffspring",
    "BreedingCmdSet",
]
