"""
Pet Commands
============

Commands for pet systems:
- Feral pet training and management
- Pet play headspace
- Pet gear
- Pack management
"""

from typing import Optional

# Evennia imports - stub for standalone testing
try:
    from evennia import Command, CmdSet
    from evennia.utils import search
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
    """Find a character/NPC in the room by name."""
    if not name:
        return None
    
    # Search room contents
    candidates = caller.location.contents if caller.location else []
    
    for obj in candidates:
        if obj.key.lower() == name.lower():
            return obj
        if hasattr(obj, 'aliases') and name.lower() in [a.lower() for a in obj.aliases.all()]:
            return obj
    
    return None


def find_pet(caller, name: str):
    """Find a pet owned by caller."""
    target = find_target(caller, name)
    
    if not target:
        return None, f"Can't find '{name}' here."
    
    # Check if it's a pet
    if hasattr(target, 'pet_stats'):
        stats = target.pet_stats
        if stats.owner_dbref == caller.dbref:
            return target, ""
        return None, f"{target.key} is not your pet."
    
    return None, f"{target.key} is not a pet."


# =============================================================================
# FERAL TRAINING COMMANDS
# =============================================================================

class CmdTrain(Command):
    """
    Train a pet in a trick.
    
    Usage:
      train <pet> <trick>
      train <pet> list
      
    Examples:
      train Fido sit
      train Fido list
      train Rex roll over
    """
    key = "train"
    locks = "cmd:all()"
    help_category = "Pets"
    
    def parse(self):
        args = self.args.strip().split(None, 1)
        self.pet_name = args[0] if args else ""
        self.trick_name = args[1] if len(args) > 1 else ""
    
    def func(self):
        if not self.pet_name:
            self.caller.msg("Train which pet?")
            return
        
        pet, error = find_pet(self.caller, self.pet_name)
        if not pet:
            self.caller.msg(error)
            return
        
        from .pets.feral_training import TrainingSystem, TRICKS
        
        # List available tricks
        if self.trick_name.lower() == "list":
            available = TrainingSystem.get_available_tricks(pet, self.caller)
            
            if not available:
                self.caller.msg(f"{pet.key} has learned all available tricks!")
                return
            
            lines = [f"Tricks available to train {pet.key}:"]
            for trick in available:
                status = ""
                if trick.key in pet.pet_stats.tricks_mastered:
                    status = " |g(mastered)|n"
                elif trick.key in pet.pet_stats.tricks_learned:
                    status = " |y(learned)|n"
                lines.append(f"  {trick.name} (difficulty {trick.difficulty}){status}")
            
            self.caller.msg("\n".join(lines))
            return
        
        if not self.trick_name:
            self.caller.msg("Train them in which trick? Use 'train <pet> list' to see options.")
            return
        
        # Find trick by name
        trick_key = None
        for key, trick in TRICKS.items():
            if trick.name.lower() == self.trick_name.lower():
                trick_key = key
                break
            if key.lower() == self.trick_name.lower().replace(" ", "_"):
                trick_key = key
                break
        
        if not trick_key:
            self.caller.msg(f"Unknown trick: {self.trick_name}")
            return
        
        # Conduct training
        success, message = TrainingSystem.conduct_training(pet, trick_key, self.caller)
        self.caller.msg(message)
        
        # Notify room
        if success:
            self.caller.location.msg_contents(
                f"{self.caller.key} trains {pet.key}.",
                exclude=[self.caller]
            )


class CmdOrder(Command):
    """
    Command a pet to perform a learned trick.
    
    Usage:
      order <pet> <trick> [target]
      
    Examples:
      order Fido sit
      order Rex attack goblin
      order Luna fetch ball
    """
    key = "order"
    aliases = ["command"]
    locks = "cmd:all()"
    help_category = "Pets"
    
    def parse(self):
        args = self.args.strip().split()
        self.pet_name = args[0] if args else ""
        self.trick_name = args[1] if len(args) > 1 else ""
        self.target_name = args[2] if len(args) > 2 else ""
    
    def func(self):
        if not self.pet_name:
            self.caller.msg("Order which pet?")
            return
        
        pet, error = find_pet(self.caller, self.pet_name)
        if not pet:
            self.caller.msg(error)
            return
        
        if not self.trick_name:
            self.caller.msg("Order them to do what?")
            return
        
        from .pets.feral_training import TrainingSystem, get_trick_by_command, TRICKS
        
        # Find trick
        trick = get_trick_by_command(self.trick_name)
        if not trick:
            # Try by key
            trick_key = self.trick_name.lower().replace(" ", "_")
            trick = TRICKS.get(trick_key)
        
        if not trick:
            self.caller.msg(f"Unknown trick: {self.trick_name}")
            return
        
        # Find target if needed
        target = None
        if trick.requires_target:
            if not self.target_name:
                self.caller.msg(f"{trick.name} requires a target.")
                return
            target = find_target(self.caller, self.target_name)
            if not target:
                self.caller.msg(f"Can't find '{self.target_name}' here.")
                return
        
        # Command the trick
        success, message = TrainingSystem.command_trick(pet, trick.key, target)
        
        # Announce
        self.caller.location.msg_contents(
            f'{self.caller.key} commands "{trick.command_phrase}"',
            exclude=[]
        )
        self.caller.location.msg_contents(message, exclude=[])


class CmdPetStats(Command):
    """
    View a pet's stats and training.
    
    Usage:
      petstats <pet>
    """
    key = "petstats"
    aliases = ["pstats"]
    locks = "cmd:all()"
    help_category = "Pets"
    
    def func(self):
        if not self.args.strip():
            self.caller.msg("Check stats of which pet?")
            return
        
        pet, error = find_pet(self.caller, self.args.strip())
        if not pet:
            self.caller.msg(error)
            return
        
        self.caller.msg(pet.pet_stats.get_status_display())


class CmdReward(Command):
    """
    Reward a pet for good behavior.
    
    Usage:
      reward <pet>
    """
    key = "reward"
    aliases = ["goodpet", "good"]
    locks = "cmd:all()"
    help_category = "Pets"
    
    def func(self):
        if not self.args.strip():
            self.caller.msg("Reward which pet?")
            return
        
        pet, error = find_pet(self.caller, self.args.strip())
        if not pet:
            self.caller.msg(error)
            return
        
        pet.pet_stats.apply_reward(10)
        pet.save_pet_stats()
        
        desc = pet.get_mood_desc() if hasattr(pet, 'get_mood_desc') else ""
        
        self.caller.msg(f"You reward {pet.key}. {desc}")
        self.caller.location.msg_contents(
            f"{self.caller.key} rewards {pet.key}.",
            exclude=[self.caller]
        )


class CmdPunish(Command):
    """
    Discipline a pet for bad behavior.
    
    Usage:
      punish <pet>
    """
    key = "punish"
    aliases = ["badpet", "bad", "discipline"]
    locks = "cmd:all()"
    help_category = "Pets"
    
    def func(self):
        if not self.args.strip():
            self.caller.msg("Punish which pet?")
            return
        
        pet, error = find_pet(self.caller, self.args.strip())
        if not pet:
            self.caller.msg(error)
            return
        
        pet.pet_stats.apply_punishment(10)
        pet.save_pet_stats()
        
        desc = pet.get_mood_desc() if hasattr(pet, 'get_mood_desc') else ""
        
        self.caller.msg(f"You discipline {pet.key}. {desc}")
        self.caller.location.msg_contents(
            f"{self.caller.key} disciplines {pet.key}.",
            exclude=[self.caller]
        )


# =============================================================================
# PET PLAY COMMANDS
# =============================================================================

class CmdPetMode(Command):
    """
    Enter or exit pet play headspace.
    
    Usage:
      petmode <type> [petname]
      petmode off
      petmode status
      
    Types: puppy, kitten, pony, cow, bunny, piggy, fox, wolf
    
    Examples:
      petmode puppy Fido
      petmode kitten
      petmode off
    """
    key = "petmode"
    aliases = ["petplay"]
    locks = "cmd:all()"
    help_category = "Pet Play"
    
    def parse(self):
        args = self.args.strip().split(None, 1)
        self.pet_type = args[0].lower() if args else ""
        self.pet_name = args[1] if len(args) > 1 else ""
    
    def func(self):
        if not hasattr(self.caller, 'enter_pet_mode'):
            self.caller.msg("You don't have pet play capabilities.")
            return
        
        if not self.pet_type:
            self.caller.msg("Usage: petmode <type> [name] or petmode off")
            return
        
        if self.pet_type == "off":
            result = self.caller.exit_pet_mode()
            self.caller.msg(result)
            self.caller.location.msg_contents(
                f"{self.caller.key} seems to come back to themselves.",
                exclude=[self.caller]
            )
            return
        
        if self.pet_type == "status":
            hs = self.caller.pet_headspace
            self.caller.msg(hs.get_status_display())
            return
        
        from .pets.pet_play import list_pet_types
        
        valid_types = list_pet_types()
        if self.pet_type not in valid_types:
            self.caller.msg(f"Valid pet types: {', '.join(valid_types)}")
            return
        
        result = self.caller.enter_pet_mode(self.pet_type, self.pet_name)
        self.caller.msg(result)
        
        name_str = f" '{self.pet_name}'" if self.pet_name else ""
        self.caller.location.msg_contents(
            f"{self.caller.key} slips into {self.pet_type} headspace{name_str}.",
            exclude=[self.caller]
        )


class CmdPetSound(Command):
    """
    Make a pet sound appropriate to your pet type.
    
    Usage:
      petsound
      bark
      meow
      neigh
      moo
    """
    key = "petsound"
    aliases = ["bark", "meow", "moo", "neigh", "oink", "squeak", "howl", "purr"]
    locks = "cmd:all()"
    help_category = "Pet Play"
    
    def func(self):
        if not hasattr(self.caller, 'make_pet_sound'):
            self.caller.msg("You're not in pet mode.")
            return
        
        if not self.caller.is_in_pet_mode():
            self.caller.msg("You're not in pet mode.")
            return
        
        sound = self.caller.make_pet_sound()
        
        if sound:
            self.caller.location.msg_contents(
                f"{self.caller.key}: {sound}",
                exclude=[]
            )
        else:
            self.caller.msg("You can't seem to make the right sound.")


class CmdWearPetGear(Command):
    """
    Wear a piece of pet gear.
    
    Usage:
      weargear <item>
      weargear list
    """
    key = "weargear"
    locks = "cmd:all()"
    help_category = "Pet Play"
    
    def func(self):
        if not self.args.strip():
            self.caller.msg("Wear which gear?")
            return
        
        if self.args.strip().lower() == "list":
            from .pets.pet_gear import ALL_PET_GEAR
            
            lines = ["Available pet gear:"]
            for key, gear in ALL_PET_GEAR.items():
                lines.append(f"  {gear.name} ({gear.slot.value})")
            
            self.caller.msg("\n".join(lines))
            return
        
        # Find gear in inventory
        gear_name = self.args.strip().lower()
        
        for obj in self.caller.contents:
            if obj.key.lower() == gear_name:
                if hasattr(obj, 'pet_gear_data'):
                    result = self.caller.wear_pet_gear(obj.pet_gear_data)
                    self.caller.msg(result)
                    return
        
        self.caller.msg(f"You don't have '{gear_name}' in your inventory.")


class CmdRemovePetGear(Command):
    """
    Remove a piece of pet gear.
    
    Usage:
      removegear <slot>
      removegear all
    """
    key = "removegear"
    locks = "cmd:all()"
    help_category = "Pet Play"
    
    def func(self):
        if not self.args.strip():
            self.caller.msg("Remove gear from which slot?")
            return
        
        from .pets.pet_gear import PetGearSlot
        
        slot_name = self.args.strip().lower()
        
        if slot_name == "all":
            # Remove all gear
            for slot in PetGearSlot:
                result = self.caller.remove_pet_gear(slot)
            self.caller.msg("You remove all pet gear.")
            return
        
        try:
            slot = PetGearSlot(slot_name)
        except ValueError:
            valid = [s.value for s in PetGearSlot]
            self.caller.msg(f"Valid slots: {', '.join(valid)}")
            return
        
        result = self.caller.remove_pet_gear(slot)
        self.caller.msg(result)


# =============================================================================
# PACK COMMANDS
# =============================================================================

class CmdPack(Command):
    """
    Manage pet packs.
    
    Usage:
      pack                   - View your pack
      pack create <name>     - Create a new pack
      pack add <pet>         - Add pet to your pack
      pack remove <pet>      - Remove pet from pack
      pack disband           - Disband your pack
      pack hunt              - Start a pack hunt
    """
    key = "pack"
    locks = "cmd:all()"
    help_category = "Pets"
    
    def parse(self):
        args = self.args.strip().split(None, 1)
        self.subcommand = args[0].lower() if args else "view"
        self.target = args[1] if len(args) > 1 else ""
    
    def func(self):
        # Would need PackManager instance from game
        # This is a simplified implementation
        
        if self.subcommand == "view" or not self.subcommand:
            self.caller.msg("Pack management not yet fully implemented.")
            return
        
        self.caller.msg(f"Pack {self.subcommand}: {self.target}")


# =============================================================================
# COMMAND SET
# =============================================================================

class PetCmdSet(CmdSet):
    """Command set for pet systems."""
    
    key = "PetCmdSet"
    
    def at_cmdset_creation(self):
        # Training
        self.add(CmdTrain())
        self.add(CmdOrder())
        self.add(CmdPetStats())
        self.add(CmdReward())
        self.add(CmdPunish())
        
        # Pet Play
        self.add(CmdPetMode())
        self.add(CmdPetSound())
        self.add(CmdWearPetGear())
        self.add(CmdRemovePetGear())
        
        # Packs
        self.add(CmdPack())


__all__ = [
    "CmdTrain",
    "CmdOrder",
    "CmdPetStats",
    "CmdReward",
    "CmdPunish",
    "CmdPetMode",
    "CmdPetSound",
    "CmdWearPetGear",
    "CmdRemovePetGear",
    "CmdPack",
    "PetCmdSet",
]
