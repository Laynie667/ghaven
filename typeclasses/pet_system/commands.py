"""
Master Command Set
==================

Unified command set that combines all pet_systems commands.
Import this to get everything at once.
"""

from evennia import CmdSet

# Import all command sets
from .pets import PetCmdSet
from .mounting import MountCmdSet
from .clothing import ClothingCmdSet
from .breeding import BreedingCmdSet
from .economy import EconomyCmdSet
from .training import TrainingCmdSet
from .substances import SubstanceCmdSet
from .social import SocialCmdSet
from .mechanics import MechanicsCmdSet
from .service import ServiceCmdSet
from .production import ProductionCmdSet
from .slavery import SlaveryCmdSet
from .hucow import HucowCmdSet

# New system commands
from .brothel.commands import BrothelCmdSet
from .corruption.commands import CorruptionCmdSet
from .pony.commands import PonyCmdSet
from .monsters.commands import MonsterCmdSet
from .inflation.commands import InflationCmdSet
from .arena.commands import ArenaCmdSet


class PetSystemsFullCmdSet(CmdSet):
    """
    Complete command set with ALL pet_systems commands.
    Add this to a character to give them access to everything.
    """
    
    key = "pet_systems_full"
    priority = 1
    
    def at_cmdset_creation(self):
        # Core systems
        self.add(PetCmdSet)
        self.add(MountCmdSet)
        self.add(ClothingCmdSet)
        self.add(BreedingCmdSet)
        self.add(EconomyCmdSet)
        self.add(TrainingCmdSet)
        self.add(SubstanceCmdSet)
        self.add(SocialCmdSet)
        self.add(MechanicsCmdSet)
        self.add(ServiceCmdSet)
        self.add(ProductionCmdSet)
        
        # Extended systems
        self.add(SlaveryCmdSet)
        self.add(HucowCmdSet)
        
        # New expansion systems
        self.add(BrothelCmdSet)
        self.add(CorruptionCmdSet)
        self.add(PonyCmdSet)
        self.add(MonsterCmdSet)
        self.add(InflationCmdSet)
        self.add(ArenaCmdSet)


class PetSystemsPlayerCmdSet(CmdSet):
    """
    Command set for players (submissive roles).
    Limited to what a slave/pet/worker would have access to.
    """
    
    key = "pet_systems_player"
    priority = 1
    
    def at_cmdset_creation(self):
        # Basic status commands only
        from .pets.pet_commands import CmdPetStatus
        from .breeding.breeding_commands import CmdFertilityStatus
        from .slavery.commands import CmdSlaveStatus
        from .hucow.commands import CmdHucowStatus
        from .brothel.commands import CmdBrothelStatus, CmdStartShift, CmdEndShift, CmdBrothelEarnings
        from .corruption.commands import CmdTransformationStatus
        from .pony.commands import CmdPonyStatus
        from .monsters.commands import CmdMonsterStatus, CmdLayEggs
        from .inflation.commands import CmdInflationStatus, CmdDrain, CmdInflationAppearance
        from .arena.commands import CmdFighterStatus, CmdChallenge, CmdAcceptChallenge, CmdDeclineChallenge, CmdFightMove, CmdFighterRecord
        
        # Status viewing
        self.add(CmdPetStatus())
        self.add(CmdFertilityStatus())
        self.add(CmdSlaveStatus())
        self.add(CmdHucowStatus())
        self.add(CmdBrothelStatus())
        self.add(CmdTransformationStatus())
        self.add(CmdPonyStatus())
        self.add(CmdMonsterStatus())
        self.add(CmdInflationStatus())
        self.add(CmdInflationAppearance())
        self.add(CmdFighterStatus())
        self.add(CmdFighterRecord())
        
        # Actions players can take
        self.add(CmdStartShift())
        self.add(CmdEndShift())
        self.add(CmdBrothelEarnings())
        self.add(CmdLayEggs())
        self.add(CmdDrain())
        self.add(CmdChallenge())
        self.add(CmdAcceptChallenge())
        self.add(CmdDeclineChallenge())
        self.add(CmdFightMove())


class PetSystemsOwnerCmdSet(CmdSet):
    """
    Command set for owners/dominant roles.
    Full control commands.
    """
    
    key = "pet_systems_owner"
    priority = 1
    
    def at_cmdset_creation(self):
        # All player commands plus control commands
        self.add(PetSystemsPlayerCmdSet)
        
        # Economy/ownership
        self.add(EconomyCmdSet)
        
        # Training/control
        self.add(TrainingCmdSet)
        self.add(MechanicsCmdSet)
        
        # Slave management
        self.add(SlaveryCmdSet)
        
        # Animal management
        from .hucow.commands import CmdMilkHucow, CmdBreedHucow
        from .pony.commands import CmdEquipTack, CmdPonyGait, CmdHitchCart, CmdPullCart, CmdPonyTrain
        
        self.add(CmdMilkHucow())
        self.add(CmdBreedHucow())
        self.add(CmdEquipTack())
        self.add(CmdPonyGait())
        self.add(CmdHitchCart())
        self.add(CmdPullCart())
        self.add(CmdPonyTrain())


class PetSystemsBuilderCmdSet(CmdSet):
    """
    Command set for builders/GMs.
    Includes all administrative and creation commands.
    """
    
    key = "pet_systems_builder"
    priority = 2
    
    def at_cmdset_creation(self):
        # Everything
        self.add(PetSystemsFullCmdSet)


# =============================================================================
# EXPORTS
# =============================================================================

__all__ = [
    "PetSystemsFullCmdSet",
    "PetSystemsPlayerCmdSet",
    "PetSystemsOwnerCmdSet",
    "PetSystemsBuilderCmdSet",
]
