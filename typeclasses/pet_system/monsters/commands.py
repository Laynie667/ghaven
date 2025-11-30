"""
Monster Commands
================

Commands for monster breeding, oviposition, and parasitic infection.
"""

from evennia import Command, CmdSet
import random


class CmdMonsterStatus(Command):
    """
    View monster breeding status.
    
    Usage:
        monsterstatus [target]
    
    Shows eggs carried, infections, and breeding history.
    """
    
    key = "monsterstatus"
    aliases = ["ovistatus", "eggstatus"]
    locks = "cmd:all()"
    
    def func(self):
        caller = self.caller
        
        target = caller
        if self.args:
            target = caller.search(self.args.strip())
            if not target:
                return
        
        if not hasattr(target, 'oviposition'):
            caller.msg(f"{target.key} has no monster breeding data.")
            return
        
        ovi = target.oviposition
        
        lines = [f"=== Monster Status: {target.key} ==="]
        lines.append(f"Eggs Carried: {ovi.current_eggs}")
        lines.append(f"Belly Distension: {ovi.belly_distension}%")
        lines.append(f"Total Eggs Received: {ovi.total_eggs_received}")
        lines.append(f"Total Eggs Laid: {ovi.total_eggs_laid}")
        
        if hasattr(target, 'parasitic_infection'):
            inf = target.parasitic_infection
            if inf.stage.value != "clean":
                lines.append(f"\n--- Infection ---")
                lines.append(f"Stage: {inf.stage.value}")
                lines.append(f"Progress: {inf.infection_percent}%")
                lines.append(f"Type: {inf.parasite_type}")
        
        caller.msg("\n".join(lines))


class CmdSpawnMonster(Command):
    """
    Spawn a monster for breeding.
    
    Usage:
        spawnmonster <type>
        spawnmonster/list
    
    Types: tentacle_beast, slime, demon, plant, werewolf, dragon, 
           orc, goblin, minotaur, centaur, insectoid, eldritch
    """
    
    key = "spawnmonster"
    locks = "cmd:perm(Builder)"
    
    def func(self):
        caller = self.caller
        
        if "list" in self.switches:
            from ..monsters import MonsterType
            types = [t.value for t in MonsterType]
            caller.msg(f"Monster types: {', '.join(types)}")
            return
        
        if not self.args:
            caller.msg("Spawn which type?")
            return
        
        from ..monsters import MonsterType, MONSTER_PRESETS
        
        try:
            m_type = MonsterType[self.args.strip().upper()]
        except KeyError:
            caller.msg(f"Unknown type. Use spawnmonster/list.")
            return
        
        preset = MONSTER_PRESETS.get(m_type)
        
        if preset:
            caller.msg(f"Spawned: {preset.name}")
            caller.msg(f"  Breeding Method: {preset.breeding_method.value}")
            caller.msg(f"  Cock Size: {preset.cock_size_cm}cm")
            caller.msg(f"  Cum Volume: {preset.cum_volume_ml}ml")
            caller.msg(f"  Corruption: {preset.corruption_amount}")
            if preset.breeding_method.value == "oviposition":
                caller.msg(f"  Eggs per clutch: {preset.eggs_per_clutch}")
            
            # Store in room for later use
            if not caller.location.db.active_monsters:
                caller.location.db.active_monsters = []
            caller.location.db.active_monsters.append(preset.to_dict())
            
            caller.location.msg_contents(
                f"A {preset.name} appears, its intentions clear..."
            )
        else:
            caller.msg("No preset for that monster type.")


class CmdMonsterBreed(Command):
    """
    Have a monster breed with a target.
    
    Usage:
        monsterbreed <target>
        monsterbreed <monster type> = <target>
    
    Initiates monster breeding with cum/eggs/corruption.
    """
    
    key = "monsterbreed"
    aliases = ["breedwith"]
    locks = "cmd:perm(Builder)"
    
    def func(self):
        caller = self.caller
        
        if "=" in self.args:
            monster_type, target_name = self.args.split("=", 1)
            monster_type = monster_type.strip().upper()
        else:
            target_name = self.args
            monster_type = "TENTACLE_BEAST"
        
        target = caller.search(target_name.strip())
        if not target:
            return
        
        if not hasattr(target, 'oviposition'):
            caller.msg(f"{target.key} cannot be bred by monsters.")
            return
        
        from ..monsters import MonsterType, MONSTER_PRESETS, BreedingMethod
        
        try:
            m_type = MonsterType[monster_type]
        except KeyError:
            caller.msg("Unknown monster type.")
            return
        
        monster = MONSTER_PRESETS.get(m_type)
        if not monster:
            caller.msg("No preset for that monster.")
            return
        
        ovi = target.oviposition
        
        # Process breeding based on method
        if monster.breeding_method == BreedingMethod.OVIPOSITION:
            eggs = monster.eggs_per_clutch
            ovi.current_eggs += eggs
            ovi.total_eggs_received += eggs
            ovi.belly_distension = min(100, ovi.belly_distension + eggs * 5)
            
            caller.msg(f"{monster.name} deposits {eggs} eggs in {target.key}!")
            target.msg(f"You feel {eggs} eggs being pushed deep inside you... your belly swells.")
            
        elif monster.breeding_method == BreedingMethod.TENTACLE:
            cum = monster.cum_volume_ml * random.randint(2, 5)  # Multiple tentacles
            
            caller.msg(f"{monster.name}'s tentacles pump {cum}ml into {target.key}!")
            target.msg(f"Tentacles fill every hole, flooding you with {cum}ml of seed...")
            
            # Apply inflation if available
            if hasattr(target, 'inflation'):
                tracker = target.inflation
                tracker.inflate("womb", "cum", cum // 2)
                tracker.inflate("anal", "cum", cum // 3)
                tracker.inflate("stomach", "cum", cum // 6)
                target.db.inflation = tracker.to_dict()
                
        elif monster.breeding_method == BreedingMethod.CORRUPTION:
            cum = monster.cum_volume_ml
            corruption = monster.corruption_amount
            
            caller.msg(f"{monster.name} corrupts {target.key} with demonic seed!")
            target.msg(f"Dark, corrupting seed floods your womb... you feel it changing you.")
            
            # Apply transformation if available
            if hasattr(target, 'transformations'):
                from ..corruption import TransformationType
                mgr = target.transformations
                if TransformationType.DEMON not in mgr.transformations:
                    mgr.start_transformation(TransformationType.DEMON)
                mgr.add_corruption(TransformationType.DEMON, corruption, "cum")
                target.db.transformations = mgr.to_dict()
                
        elif monster.breeding_method == BreedingMethod.KNOTTING:
            cum = monster.cum_volume_ml
            
            caller.msg(f"{monster.name} knots inside {target.key}, pumping {cum}ml!")
            target.msg(f"The knot swells inside you, locking you together as seed floods your womb...")
            
        else:
            cum = monster.cum_volume_ml
            caller.msg(f"{monster.name} breeds {target.key}, depositing {cum}ml.")
            target.msg(f"You're bred, filled with {cum}ml of monster seed.")
        
        target.db.oviposition = ovi.to_dict() if hasattr(ovi, 'to_dict') else ovi.__dict__


class CmdLayEggs(Command):
    """
    Attempt to lay eggs.
    
    Usage:
        layeggs
    
    Attempts to expel carried eggs.
    """
    
    key = "layeggs"
    aliases = ["pusheggs", "birtheggs"]
    locks = "cmd:all()"
    
    def func(self):
        caller = self.caller
        
        if not hasattr(caller, 'oviposition'):
            caller.msg("You have no eggs to lay.")
            return
        
        ovi = caller.oviposition
        
        if ovi.current_eggs <= 0:
            caller.msg("You're not carrying any eggs.")
            return
        
        # Difficulty based on number of eggs
        eggs = ovi.current_eggs
        difficulty = 50 + eggs * 5
        
        roll = random.randint(1, 100)
        
        if roll < difficulty:
            # Partial success
            laid = random.randint(1, max(1, eggs // 2))
            ovi.current_eggs -= laid
            ovi.total_eggs_laid += laid
            ovi.belly_distension = max(0, ovi.belly_distension - laid * 5)
            
            caller.msg(f"With great effort, you manage to push out {laid} eggs...")
            caller.location.msg_contents(
                f"{caller.key} strains, laying {laid} glistening eggs.",
                exclude=[caller]
            )
        else:
            # Full success
            laid = eggs
            ovi.current_eggs = 0
            ovi.total_eggs_laid += laid
            ovi.belly_distension = 0
            
            caller.msg(f"Your body convulses as all {laid} eggs are pushed out!")
            caller.location.msg_contents(
                f"{caller.key} cries out, birthing {laid} eggs in a rush.",
                exclude=[caller]
            )
        
        caller.db.oviposition = ovi.to_dict() if hasattr(ovi, 'to_dict') else ovi.__dict__


class CmdInfect(Command):
    """
    Infect target with parasites.
    
    Usage:
        infect <target> = <type>
    
    Types: worm, slime_spore, demon_seed, plant_seed, insect_larva
    """
    
    key = "infect"
    aliases = ["parasiteinfect"]
    locks = "cmd:perm(Builder)"
    
    def func(self):
        caller = self.caller
        
        if "=" not in self.args:
            caller.msg("Usage: infect <target> = <type>")
            return
        
        target_name, inf_type = self.args.split("=", 1)
        target = caller.search(target_name.strip())
        if not target:
            return
        
        if not hasattr(target, 'parasitic_infection'):
            caller.msg(f"{target.key} cannot be infected.")
            return
        
        from ..monsters import InfectionStage
        
        infection = target.parasitic_infection
        infection.parasite_type = inf_type.strip()
        infection.stage = InfectionStage.EARLY
        infection.infection_percent = 10
        
        target.db.parasitic_infection = infection.to_dict() if hasattr(infection, 'to_dict') else infection.__dict__
        
        caller.msg(f"Infected {target.key} with {inf_type.strip()}.")
        target.msg(f"Something squirms inside you... an infection has begun.")


class CmdProgressInfection(Command):
    """
    Progress a parasitic infection.
    
    Usage:
        progressinfection <target> [amount]
    
    Advances the infection by a percentage (default 10).
    """
    
    key = "progressinfection"
    locks = "cmd:perm(Builder)"
    
    def func(self):
        caller = self.caller
        
        if not self.args:
            caller.msg("Progress whose infection?")
            return
        
        parts = self.args.split()
        target_name = parts[0]
        amount = 10
        
        if len(parts) > 1:
            try:
                amount = int(parts[1])
            except ValueError:
                pass
        
        target = caller.search(target_name)
        if not target:
            return
        
        if not hasattr(target, 'parasitic_infection'):
            caller.msg(f"{target.key} has no infection.")
            return
        
        from ..monsters import InfectionStage
        
        infection = target.parasitic_infection
        
        if infection.stage == InfectionStage.CLEAN:
            caller.msg(f"{target.key} is not infected.")
            return
        
        infection.infection_percent += amount
        
        # Update stage
        if infection.infection_percent >= 100:
            infection.stage = InfectionStage.TERMINAL
            target.msg("The infection has completely taken over... you feel them moving everywhere.")
        elif infection.infection_percent >= 75:
            infection.stage = InfectionStage.LATE
            target.msg("The parasites are spreading rapidly... you can feel them inside.")
        elif infection.infection_percent >= 50:
            infection.stage = InfectionStage.ADVANCED
            target.msg("The infection grows... strange urges fill your mind.")
        elif infection.infection_percent >= 25:
            infection.stage = InfectionStage.MIDDLE
            target.msg("The infection spreads deeper into your body.")
        
        target.db.parasitic_infection = infection.to_dict() if hasattr(infection, 'to_dict') else infection.__dict__
        
        caller.msg(f"Infection progressed. Now at {infection.infection_percent}% ({infection.stage.value}).")


class CmdCureInfection(Command):
    """
    Cure a parasitic infection.
    
    Usage:
        cureinfection <target>
    
    Removes parasitic infection.
    """
    
    key = "cureinfection"
    locks = "cmd:perm(Builder)"
    
    def func(self):
        caller = self.caller
        
        if not self.args:
            caller.msg("Cure who?")
            return
        
        target = caller.search(self.args.strip())
        if not target:
            return
        
        if not hasattr(target, 'parasitic_infection'):
            caller.msg(f"{target.key} has no infection data.")
            return
        
        from ..monsters import InfectionStage
        
        infection = target.parasitic_infection
        infection.stage = InfectionStage.CLEAN
        infection.infection_percent = 0
        infection.parasite_type = ""
        
        target.db.parasitic_infection = infection.to_dict() if hasattr(infection, 'to_dict') else infection.__dict__
        
        caller.msg(f"Cured {target.key}'s infection.")
        target.msg("The parasites die off... you feel clean again.")


class MonsterCmdSet(CmdSet):
    """Commands for monster breeding system."""
    
    key = "monster_cmdset"
    
    def at_cmdset_creation(self):
        self.add(CmdMonsterStatus())
        self.add(CmdSpawnMonster())
        self.add(CmdMonsterBreed())
        self.add(CmdLayEggs())
        self.add(CmdInfect())
        self.add(CmdProgressInfection())
        self.add(CmdCureInfection())
