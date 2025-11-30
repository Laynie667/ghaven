"""
Pony Commands
=============

Commands for pony play, cart pulling, shows, and pony management.
"""

from evennia import Command, CmdSet


class CmdPonyStatus(Command):
    """
    View pony status.
    
    Usage:
        ponystatus [target]
    
    Shows pony stats, tack, and condition.
    """
    
    key = "ponystatus"
    aliases = ["pstatus", "ponyinfo"]
    locks = "cmd:all()"
    
    def func(self):
        caller = self.caller
        
        target = caller
        if self.args:
            target = caller.search(self.args.strip())
            if not target:
                return
        
        if not hasattr(target, 'pony_stats'):
            caller.msg(f"{target.key} is not a pony.")
            return
        
        stats = target.pony_stats
        caller.msg(stats.get_summary())


class CmdRegisterPony(Command):
    """
    Register someone as a pony.
    
    Usage:
        registerpony <target>
        registerpony <target> = <type>
    
    Types: draft, riding, show, racing, breeding, pleasure
    """
    
    key = "registerpony"
    aliases = ["makepony"]
    locks = "cmd:perm(Builder)"
    
    def func(self):
        caller = self.caller
        
        if not self.args:
            caller.msg("Register who as a pony?")
            return
        
        if "=" in self.args:
            target_name, pony_type = self.args.split("=", 1)
            pony_type = pony_type.strip().upper()
        else:
            target_name = self.args
            pony_type = "RIDING"
        
        target = caller.search(target_name.strip())
        if not target:
            return
        
        if not hasattr(target, 'pony_stats'):
            caller.msg(f"{target.key} cannot be a pony.")
            return
        
        from ..pony import PonyStats, PonyType
        
        try:
            p_type = PonyType[pony_type]
        except KeyError:
            caller.msg(f"Unknown type. Valid: {[t.value for t in PonyType]}")
            return
        
        stats = PonyStats(
            pony_id=target.dbref,
            pony_name=target.key,
            pony_type=p_type,
        )
        target.db.pony_stats = stats.to_dict()
        
        caller.msg(f"{target.key} registered as {p_type.value} pony.")
        target.msg(f"You have been registered as a {p_type.value} pony. Time to train!")


class CmdEquipTack(Command):
    """
    Equip tack on a pony.
    
    Usage:
        equiptack <pony> = <item>
        equiptack/remove <pony> = <item>
        equiptack/list
    
    Items: bridle, bit, harness, saddle, blinders, hooves, tail, mane, bells, cart_harness
    """
    
    key = "equiptack"
    aliases = ["tack"]
    locks = "cmd:all()"
    
    def func(self):
        caller = self.caller
        
        if "list" in self.switches:
            from ..pony import TackType
            caller.msg(f"Tack types: {', '.join([t.value for t in TackType])}")
            return
        
        if "=" not in self.args:
            caller.msg("Usage: equiptack <pony> = <item>")
            return
        
        target_name, item_name = self.args.split("=", 1)
        target = caller.search(target_name.strip())
        if not target:
            return
        
        if not hasattr(target, 'pony_stats'):
            caller.msg(f"{target.key} is not a pony.")
            return
        
        from ..pony import TackType
        
        try:
            tack = TackType[item_name.strip().upper()]
        except KeyError:
            caller.msg(f"Unknown tack. Use equiptack/list.")
            return
        
        stats = target.pony_stats
        
        if "remove" in self.switches:
            if tack.value in stats.equipped_tack:
                stats.equipped_tack.remove(tack.value)
                target.db.pony_stats = stats.to_dict()
                caller.msg(f"Removed {tack.value} from {target.key}.")
                target.msg(f"Your {tack.value} is removed.")
            else:
                caller.msg(f"{target.key} isn't wearing {tack.value}.")
        else:
            if tack.value not in stats.equipped_tack:
                stats.equipped_tack.append(tack.value)
                target.db.pony_stats = stats.to_dict()
                caller.msg(f"Equipped {tack.value} on {target.key}.")
                target.msg(f"A {tack.value} is fitted on you.")
            else:
                caller.msg(f"{target.key} already has {tack.value} equipped.")


class CmdPonyGait(Command):
    """
    Command a pony to change gait.
    
    Usage:
        gait <pony> = <gait>
        gait/list
    
    Gaits: stand, walk, trot, canter, gallop, prance
    """
    
    key = "gait"
    aliases = ["ponygait"]
    locks = "cmd:all()"
    
    def func(self):
        caller = self.caller
        
        if "list" in self.switches:
            from ..pony import PonyGait
            caller.msg(f"Gaits: {', '.join([g.value for g in PonyGait])}")
            return
        
        if "=" not in self.args:
            caller.msg("Usage: gait <pony> = <gait>")
            return
        
        target_name, gait_name = self.args.split("=", 1)
        target = caller.search(target_name.strip())
        if not target:
            return
        
        if not hasattr(target, 'pony_stats'):
            caller.msg(f"{target.key} is not a pony.")
            return
        
        from ..pony import PonyGait
        
        try:
            gait = PonyGait[gait_name.strip().upper()]
        except KeyError:
            caller.msg(f"Unknown gait. Use gait/list.")
            return
        
        stats = target.pony_stats
        stats.current_gait = gait
        target.db.pony_stats = stats.to_dict()
        
        gait_messages = {
            PonyGait.STAND: f"{target.key} comes to a halt, standing at attention.",
            PonyGait.WALK: f"{target.key} begins walking with measured steps.",
            PonyGait.TROT: f"{target.key} breaks into a trot, hooves clip-clopping rhythmically.",
            PonyGait.CANTER: f"{target.key} canters forward, a smooth rolling gait.",
            PonyGait.GALLOP: f"{target.key} gallops at full speed!",
            PonyGait.PRANCE: f"{target.key} prances prettily, high-stepping with elegance.",
        }
        
        msg = gait_messages.get(gait, f"{target.key} changes gait to {gait.value}.")
        caller.location.msg_contents(msg)


class CmdHitchCart(Command):
    """
    Hitch a pony to a cart.
    
    Usage:
        hitch <pony>
        unhitch <pony>
    
    Hitches or unhitches a pony from the cart in this room.
    """
    
    key = "hitch"
    aliases = ["unhitch"]
    locks = "cmd:all()"
    
    def func(self):
        caller = self.caller
        
        if not self.args:
            caller.msg("Hitch which pony?")
            return
        
        target = caller.search(self.args.strip())
        if not target:
            return
        
        if not hasattr(target, 'pony_stats'):
            caller.msg(f"{target.key} is not a pony.")
            return
        
        stats = target.pony_stats
        
        if "unhitch" in self.cmdstring:
            if not stats.is_hitched:
                caller.msg(f"{target.key} is not hitched to anything.")
                return
            
            stats.is_hitched = False
            stats.hitched_to = None
            target.db.pony_stats = stats.to_dict()
            
            caller.location.msg_contents(
                f"{target.key} is unhitched from the cart."
            )
        else:
            if stats.is_hitched:
                caller.msg(f"{target.key} is already hitched.")
                return
            
            # Check for cart harness
            if "cart_harness" not in stats.equipped_tack:
                caller.msg(f"{target.key} needs a cart harness first.")
                return
            
            stats.is_hitched = True
            stats.hitched_to = "cart"
            target.db.pony_stats = stats.to_dict()
            
            caller.location.msg_contents(
                f"{target.key} is hitched to the cart, ready to pull."
            )


class CmdPullCart(Command):
    """
    Command a pony to pull the cart.
    
    Usage:
        pull <direction>
        pull <pony> = <direction>
    
    Makes the hitched pony pull the cart in a direction.
    """
    
    key = "pull"
    aliases = ["cartpull"]
    locks = "cmd:all()"
    
    def func(self):
        caller = self.caller
        
        # Find hitched pony
        pony = None
        direction = self.args.strip() if self.args else None
        
        if "=" in self.args:
            pony_name, direction = self.args.split("=", 1)
            pony = caller.search(pony_name.strip())
            direction = direction.strip()
        else:
            # Look for any hitched pony in the room
            for obj in caller.location.contents:
                if hasattr(obj, 'pony_stats'):
                    stats = obj.pony_stats
                    if stats.is_hitched:
                        pony = obj
                        break
        
        if not pony:
            caller.msg("No hitched pony found.")
            return
        
        if not direction:
            caller.msg("Pull in which direction?")
            return
        
        stats = pony.pony_stats
        
        # Calculate stamina cost based on gait
        from ..pony import PonyGait
        
        gait_cost = {
            PonyGait.WALK: 5,
            PonyGait.TROT: 10,
            PonyGait.CANTER: 15,
            PonyGait.GALLOP: 25,
        }
        
        cost = gait_cost.get(stats.current_gait, 10)
        
        if stats.stamina < cost:
            caller.msg(f"{pony.key} is too exhausted to pull.")
            return
        
        stats.stamina -= cost
        stats.total_distance_pulled += 1
        pony.db.pony_stats = stats.to_dict()
        
        caller.location.msg_contents(
            f"{pony.key} strains against the harness, pulling the cart {direction}!"
        )
        
        # Would trigger actual movement here


class CmdPonyShow(Command):
    """
    Enter a pony in a show.
    
    Usage:
        ponyshow <pony> = <category>
        ponyshow/start <name>
        ponyshow/judge
    
    Categories: dressage, speed, endurance, beauty, obedience
    """
    
    key = "ponyshow"
    locks = "cmd:all()"
    
    def func(self):
        caller = self.caller
        
        if "start" in self.switches:
            # Would create a new show
            caller.msg("Show started!")
            return
        
        if "judge" in self.switches:
            # Would judge current show
            caller.msg("Judging...")
            return
        
        if "=" not in self.args:
            caller.msg("Usage: ponyshow <pony> = <category>")
            return
        
        target_name, category = self.args.split("=", 1)
        target = caller.search(target_name.strip())
        if not target:
            return
        
        if not hasattr(target, 'pony_stats'):
            caller.msg(f"{target.key} is not a pony.")
            return
        
        from ..pony import ShowCategory
        
        try:
            cat = ShowCategory[category.strip().upper()]
        except KeyError:
            caller.msg(f"Unknown category. Valid: {[c.value for c in ShowCategory]}")
            return
        
        stats = target.pony_stats
        
        # Calculate score based on stats
        score_map = {
            ShowCategory.DRESSAGE: stats.agility,
            ShowCategory.SPEED: stats.speed,
            ShowCategory.ENDURANCE: stats.endurance,
            ShowCategory.BEAUTY: stats.beauty,
            ShowCategory.OBEDIENCE: stats.training_level,
        }
        
        base_score = score_map.get(cat, 50)
        final_score = base_score + random.randint(-10, 10)
        
        caller.msg(f"{target.key} competes in {cat.value}!")
        caller.msg(f"Score: {final_score}")
        
        if final_score >= 90:
            caller.msg("FIRST PLACE! The crowd cheers!")
        elif final_score >= 75:
            caller.msg("Second place. A respectable showing.")
        elif final_score >= 60:
            caller.msg("Third place. Room for improvement.")
        else:
            caller.msg("No placement. More training needed.")


class CmdBreedPonies(Command):
    """
    Breed two ponies.
    
    Usage:
        breedponies <stallion> = <mare>
    
    Attempts to breed two ponies to produce a foal.
    """
    
    key = "breedponies"
    aliases = ["ponybreed"]
    locks = "cmd:perm(Builder)"
    
    def func(self):
        caller = self.caller
        
        if "=" not in self.args:
            caller.msg("Usage: breedponies <stallion> = <mare>")
            return
        
        sire_name, dam_name = self.args.split("=", 1)
        sire = caller.search(sire_name.strip())
        dam = caller.search(dam_name.strip())
        
        if not sire or not dam:
            return
        
        if not hasattr(sire, 'pony_stats') or not hasattr(dam, 'pony_stats'):
            caller.msg("Both must be registered ponies.")
            return
        
        from ..pony import breed_ponies
        
        sire_stats = sire.pony_stats
        dam_stats = dam.pony_stats
        
        success, msg, foal = breed_ponies(sire_stats, dam_stats)
        
        sire.db.pony_stats = sire_stats.to_dict()
        dam.db.pony_stats = dam_stats.to_dict()
        
        caller.msg(msg)
        
        if success and foal:
            caller.msg(f"Foal stats - Speed: {foal.speed}, Endurance: {foal.endurance}, Beauty: {foal.beauty}")


class CmdPonyTrain(Command):
    """
    Train a pony stat.
    
    Usage:
        ponytrain <pony> = <stat>
    
    Stats: speed, endurance, agility, strength, beauty, obedience
    """
    
    key = "ponytrain"
    locks = "cmd:all()"
    
    def func(self):
        caller = self.caller
        
        if "=" not in self.args:
            caller.msg("Usage: ponytrain <pony> = <stat>")
            return
        
        target_name, stat = self.args.split("=", 1)
        target = caller.search(target_name.strip())
        if not target:
            return
        
        if not hasattr(target, 'pony_stats'):
            caller.msg(f"{target.key} is not a pony.")
            return
        
        stat = stat.strip().lower()
        valid_stats = ["speed", "endurance", "agility", "strength", "beauty", "obedience"]
        
        if stat not in valid_stats:
            caller.msg(f"Valid stats: {', '.join(valid_stats)}")
            return
        
        stats = target.pony_stats
        
        # Training gains
        import random
        gain = random.randint(1, 3)
        
        if stat == "obedience":
            stats.training_level = min(100, stats.training_level + gain)
        else:
            current = getattr(stats, stat, 50)
            setattr(stats, stat, min(100, current + gain))
        
        target.db.pony_stats = stats.to_dict()
        
        caller.msg(f"Trained {target.key}'s {stat}. +{gain} points!")
        target.msg(f"Your {stat} improves from training.")


# Need random for show scoring
import random


class PonyCmdSet(CmdSet):
    """Commands for pony play system."""
    
    key = "pony_cmdset"
    
    def at_cmdset_creation(self):
        self.add(CmdPonyStatus())
        self.add(CmdRegisterPony())
        self.add(CmdEquipTack())
        self.add(CmdPonyGait())
        self.add(CmdHitchCart())
        self.add(CmdPullCart())
        self.add(CmdPonyShow())
        self.add(CmdBreedPonies())
        self.add(CmdPonyTrain())
