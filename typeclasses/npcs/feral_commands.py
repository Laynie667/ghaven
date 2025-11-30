"""
Feral Commands
==============

Commands for interacting with feral NPCs:
- Trust building: pet, feed, tame, train
- Sexual: present, breed
- Leash: leash, unleash, tug
- Status: feral, knot, struggle
"""

from evennia import Command, CmdSet
from random import randint, choice


# =============================================================================
# HELPER FUNCTIONS
# =============================================================================

def find_feral_in_room(caller, target_name=None):
    """Find a feral NPC in the room."""
    from .npc_types import FeralNPC
    
    for obj in caller.location.contents:
        if not isinstance(obj, FeralNPC):
            continue
        if target_name and target_name.lower() not in obj.key.lower():
            continue
        return obj
    return None


def get_ferals_in_room(caller):
    """Get all feral NPCs in room."""
    from .npc_types import FeralNPC
    return [obj for obj in caller.location.contents if isinstance(obj, FeralNPC)]


# =============================================================================
# PET MESSAGES
# =============================================================================

PET_MESSAGES = {
    "wary": [
        "{name} flinches at your touch but doesn't flee.",
        "{name} eyes you warily as you pet them.",
        "{name} tolerates your touch, tense and ready to bolt.",
    ],
    "neutral": [
        "{name}'s ears flick as you pet them.",
        "{name} allows your touch without reaction.",
        "{name} glances at you as you pet them.",
    ],
    "friendly": [
        "{name}'s tail wags as you pet them.",
        "{name} leans into your touch happily.",
        "{name} makes a pleased sound as you pet them.",
    ],
    "bonded": [
        "{name} practically melts under your touch.",
        "{name} wriggles with joy as you pet them.",
        "{name} nuzzles against your hand affectionately.",
    ],
}

FEED_MESSAGES = {
    "hungry": [
        "{name} devours the food eagerly, tail wagging.",
        "{name} gobbles up the offering with enthusiasm.",
        "{name} eats ravenously, clearly very hungry.",
    ],
    "normal": [
        "{name} eats the offered food.",
        "{name} accepts the food and eats it.",
        "{name} takes the food and chews contentedly.",
    ],
    "full": [
        "{name} sniffs at the food with little interest.",
        "{name} takes a small bite, clearly not very hungry.",
        "{name} ignores the food for now.",
    ],
}


# =============================================================================
# TRUST BUILDING COMMANDS
# =============================================================================

class CmdPet(Command):
    """
    Pet a feral animal.
    
    Usage:
        pet <animal>
    
    Builds trust slowly. Reaction depends on current trust level.
    """
    
    key = "pet"
    locks = "cmd:all()"
    
    def func(self):
        if not self.args:
            self.caller.msg("Pet what?")
            return
        
        target = find_feral_in_room(self.caller, self.args.strip())
        if not target:
            self.caller.msg("You don't see that here.")
            return
        
        # Get relationship
        rel = target.get_relationship(self.caller)
        trust = rel.trust if rel else 30
        
        # Determine tier
        if trust >= 80:
            tier = "bonded"
            trust_gain = 1
        elif trust >= 50:
            tier = "friendly"
            trust_gain = 2
        elif trust >= 30:
            tier = "neutral"
            trust_gain = 3
        else:
            tier = "wary"
            trust_gain = 2
            # Check fear
            if hasattr(target, 'get_instinct'):
                fear = target.get_instinct("fear_level", 50)
                if fear > 70:
                    self.caller.msg(f"{target.key} shies away from your hand, too afraid.")
                    return
        
        # Update trust
        target.update_relationship(self.caller, trust_change=trust_gain)
        
        # Reduce fear
        if hasattr(target, 'modify_instinct'):
            target.modify_instinct("fear_level", -2)
        
        # Message
        msg = choice(PET_MESSAGES[tier]).format(name=target.key)
        self.caller.msg(msg)
        self.caller.location.msg_contents(
            f"{self.caller.key} pets {target.key}.",
            exclude=[self.caller]
        )


class CmdFeed(Command):
    """
    Feed a feral animal.
    
    Usage:
        feed <animal>
        feed <animal> with <food>
    
    Builds trust, especially when hungry.
    """
    
    key = "feed"
    locks = "cmd:all()"
    
    def parse(self):
        args = self.args.strip()
        self.target_name = ""
        self.food_name = ""
        
        if " with " in args:
            parts = args.split(" with ", 1)
            self.target_name = parts[0].strip()
            self.food_name = parts[1].strip()
        else:
            self.target_name = args
    
    def func(self):
        if not self.target_name:
            self.caller.msg("Feed what?")
            return
        
        target = find_feral_in_room(self.caller, self.target_name)
        if not target:
            self.caller.msg("You don't see that here.")
            return
        
        # Check for food item
        food = None
        if self.food_name:
            food = self.caller.search(self.food_name, location=self.caller)
            if not food:
                return
        
        # Get hunger
        hunger = 50
        if hasattr(target, 'get_instinct'):
            hunger = target.get_instinct("hunger", 50)
        
        # Determine tier
        if hunger > 70:
            tier = "hungry"
            trust_gain = 5
        elif hunger > 30:
            tier = "normal"
            trust_gain = 3
        else:
            tier = "full"
            trust_gain = 1
        
        # If using treat, get bonus
        if food and hasattr(food, 'trust_bonus'):
            from ..items import Treat
            if isinstance(food, Treat):
                success, msg = food.use_on(self.caller, target)
                self.caller.msg(msg)
                return
        
        # Update relationship
        target.update_relationship(self.caller, trust_change=trust_gain)
        
        # Reduce hunger
        if hasattr(target, 'modify_instinct'):
            target.modify_instinct("hunger", -30)
        
        # Consume food if provided
        if food and hasattr(food, 'uses_remaining'):
            food.uses_remaining -= 1
            if food.uses_remaining <= 0:
                food.delete()
        
        # Message
        msg = choice(FEED_MESSAGES[tier]).format(name=target.key)
        self.caller.msg(msg)


class CmdTame(Command):
    """
    Attempt to tame a feral animal.
    
    Usage:
        tame <animal>
    
    Requires high trust (70+). Success based on trust level.
    """
    
    key = "tame"
    locks = "cmd:all()"
    
    def func(self):
        if not self.args:
            self.caller.msg("Tame what?")
            return
        
        target = find_feral_in_room(self.caller, self.args.strip())
        if not target:
            self.caller.msg("You don't see that here.")
            return
        
        # Check if already tamed
        if hasattr(target, 'is_domesticated') and target.is_domesticated:
            owner_dbref = getattr(target, 'owner', None)
            if owner_dbref == self.caller.dbref:
                self.caller.msg(f"{target.key} is already your pet.")
            else:
                self.caller.msg(f"{target.key} already has an owner.")
            return
        
        # Check trust
        rel = target.get_relationship(self.caller)
        trust = rel.trust if rel else 0
        
        if trust < 70:
            self.caller.msg(f"{target.key} doesn't trust you enough yet. (Need 70, have {trust})")
            return
        
        # Roll for success
        roll = randint(1, 100)
        target_dc = 100 - (trust - 20)  # Higher trust = easier
        
        if roll > target_dc:
            # Success
            target.is_domesticated = True
            target.owner = self.caller.dbref
            
            self.caller.msg(f"After patient work, {target.key} accepts you as their owner!")
            self.caller.location.msg_contents(
                f"{self.caller.key} has tamed {target.key}!",
                exclude=[self.caller]
            )
        else:
            self.caller.msg(f"{target.key} isn't ready to be tamed yet. Keep building trust.")


class CmdTrain(Command):
    """
    Train a tamed animal to learn a command.
    
    Usage:
        train <animal> <command>
    
    Available commands: sit, stay, come, heel, mount, present, guard, attack
    """
    
    key = "train"
    locks = "cmd:all()"
    
    TRAINABLE = ["sit", "stay", "come", "heel", "mount", "present", "guard", "attack"]
    
    def func(self):
        args = self.args.split()
        if len(args) < 2:
            self.caller.msg(f"Usage: train <animal> <command>")
            self.caller.msg(f"Commands: {', '.join(self.TRAINABLE)}")
            return
        
        target_name = args[0]
        command = args[1].lower()
        
        target = find_feral_in_room(self.caller, target_name)
        if not target:
            self.caller.msg("You don't see that here.")
            return
        
        # Check ownership
        if not hasattr(target, 'owner') or target.owner != self.caller.dbref:
            self.caller.msg(f"{target.key} isn't your pet to train.")
            return
        
        if command not in self.TRAINABLE:
            self.caller.msg(f"Unknown command. Available: {', '.join(self.TRAINABLE)}")
            return
        
        # Check if already knows
        trained = getattr(target, 'trained_commands', None) or []
        if command in trained:
            self.caller.msg(f"{target.key} already knows '{command}'.")
            return
        
        # Train (always succeeds for owned pets)
        if not trained:
            trained = []
        trained.append(command)
        target.trained_commands = trained
        
        self.caller.msg(f"You teach {target.key} to '{command}'.")
        self.caller.location.msg_contents(
            f"{self.caller.key} trains {target.key}.",
            exclude=[self.caller]
        )


# =============================================================================
# SEXUAL COMMANDS
# =============================================================================

class CmdPresent(Command):
    """
    Present yourself to a feral.
    
    Usage:
        present
        present to <animal>
    
    Signals availability. Ferals may respond based on arousal and attraction.
    """
    
    key = "present"
    locks = "cmd:all()"
    
    def func(self):
        target = None
        if self.args:
            target_name = self.args.replace("to ", "").strip()
            target = find_feral_in_room(self.caller, target_name)
            if not target:
                self.caller.msg("You don't see that here.")
                return
        
        self.caller.location.msg_contents(
            f"{self.caller.key} presents themselves invitingly.",
            exclude=[]
        )
        
        # Check feral reactions
        ferals = [target] if target else get_ferals_in_room(self.caller)
        
        for feral in ferals:
            if not hasattr(feral, 'get_instinct'):
                continue
            
            arousal = feral.get_instinct("arousal_level", 0)
            
            # Heat bonus
            if hasattr(feral, 'is_in_heat') and feral.is_in_heat():
                arousal += 30
            
            # Check attraction
            rel = feral.get_relationship(self.caller)
            attraction = rel.attraction if rel else 30
            
            total = arousal + (attraction // 2)
            
            if total > 80:
                self.caller.location.msg_contents(
                    f"{feral.key} immediately moves toward {self.caller.key} with clear intent.",
                    exclude=[]
                )
            elif total > 50:
                self.caller.location.msg_contents(
                    f"{feral.key} shows interest in {self.caller.key}'s display.",
                    exclude=[]
                )
            elif total > 30:
                self.caller.location.msg_contents(
                    f"{feral.key} glances at {self.caller.key} briefly.",
                    exclude=[]
                )


class CmdBreed(Command):
    """
    Allow a feral to mount you.
    
    Usage:
        breed
        breed with <animal>
    
    Initiates mating. If the feral can knot, knotting will follow.
    """
    
    key = "breed"
    aliases = ["mate"]
    locks = "cmd:all()"
    
    def func(self):
        target = None
        if self.args:
            target_name = self.args.replace("with ", "").strip()
            target = find_feral_in_room(self.caller, target_name)
            if not target:
                self.caller.msg("You don't see that here.")
                return
        else:
            # Find first interested feral
            ferals = get_ferals_in_room(self.caller)
            for f in ferals:
                if hasattr(f, 'get_instinct'):
                    arousal = f.get_instinct("arousal_level", 0)
                    if arousal > 30:
                        target = f
                        break
            
            if not target:
                self.caller.msg("No interested ferals here.")
                return
        
        # Check feral arousal
        if hasattr(target, 'get_instinct'):
            arousal = target.get_instinct("arousal_level", 0)
            if arousal < 30:
                self.caller.msg(f"{target.key} doesn't seem interested right now.")
                return
        
        self.caller.location.msg_contents(
            f"{self.caller.key} signals acceptance as {target.key} mounts them.",
            exclude=[]
        )
        
        # Check if can knot
        if hasattr(target, 'can_knot') and target.can_knot():
            self.caller.msg(f"You feel {target.key}'s knot beginning to swell...")
            
            # Initiate knotting after delay
            if hasattr(target, 'initiate_knot'):
                try:
                    from evennia.utils import delay
                    delay(10, target.initiate_knot, self.caller)
                except ImportError:
                    target.initiate_knot(self.caller)


# =============================================================================
# STATUS COMMANDS
# =============================================================================

class CmdFeralStatus(Command):
    """
    Check a feral's status.
    
    Usage:
        feral
        feral <animal>
    """
    
    key = "feral"
    locks = "cmd:all()"
    
    def func(self):
        if self.args:
            target = find_feral_in_room(self.caller, self.args.strip())
        else:
            ferals = get_ferals_in_room(self.caller)
            target = ferals[0] if ferals else None
        
        if not target:
            self.caller.msg("No ferals here.")
            return
        
        lines = [f"|c{target.key}|n"]
        
        # Type
        body = target.get_body() if hasattr(target, 'get_body') else None
        species = getattr(body, 'species_key', 'unknown') if body else 'unknown'
        lines.append(f"Type: Feral ({species})")
        
        # Domestication
        if hasattr(target, 'is_domesticated'):
            if target.is_domesticated:
                owner_dbref = getattr(target, 'owner', None)
                owner_name = "Unknown"
                if owner_dbref:
                    try:
                        from evennia.utils.search import search_object
                        results = search_object(owner_dbref)
                        if results:
                            owner_name = results[0].key
                    except:
                        pass
                lines.append(f"Domesticated: Yes, owned by {owner_name}")
            else:
                lines.append("Domesticated: No (wild)")
        
        # Instincts
        if hasattr(target, 'instincts') and target.instincts:
            inst = target.instincts
            parts = []
            if 'hunger' in inst:
                parts.append(f"Hunger {inst['hunger']}")
            if 'fear_level' in inst:
                parts.append(f"Fear {inst['fear_level']}")
            if 'arousal_level' in inst:
                parts.append(f"Arousal {inst['arousal_level']}")
            if parts:
                lines.append(f"Instincts: {', '.join(parts)}")
        
        # Heat
        if hasattr(target, 'get_heat_phase'):
            phase = target.get_heat_phase()
            if hasattr(phase, 'value'):
                phase = phase.value
            lines.append(f"Heat: {phase} phase")
        
        # Knot
        if hasattr(target, 'is_tied') and target.is_tied():
            if hasattr(target, 'get_knot_status'):
                lines.append(f"Tied: {target.get_knot_status()}")
        
        # Leash
        if hasattr(target, 'is_leashed') and target.is_leashed():
            if hasattr(target, 'get_leash_status'):
                lines.append(f"Leash: {target.get_leash_status()}")
        
        # Trained commands
        if hasattr(target, 'trained_commands') and target.trained_commands:
            lines.append(f"Commands: {', '.join(target.trained_commands)}")
        
        self.caller.msg("\n".join(lines))


class CmdKnotStatus(Command):
    """
    Check knot/tie status.
    
    Usage:
        knot
        tie
    """
    
    key = "knot"
    aliases = ["tie"]
    locks = "cmd:all()"
    
    def func(self):
        if hasattr(self.caller, 'is_tied') and self.caller.is_tied():
            if hasattr(self.caller, 'tie_data') and self.caller.tie_data:
                data = self.caller.tie_data
                partner_name = data.get("partner_name", "someone")
                role = data.get("role", "unknown")
                state = data.get("knot_state", "unknown")
                
                if hasattr(state, 'value'):
                    state = state.value
                
                lines = ["|cKnot Status|n"]
                lines.append(f"Partner: {partner_name}")
                lines.append(f"Role: {role}")
                lines.append(f"State: {state}")
                
                if state == "locked":
                    # Get time remaining
                    if hasattr(self.caller, 'get_tie_time_remaining'):
                        remaining = self.caller.get_tie_time_remaining()
                        mins = remaining // 60
                        secs = remaining % 60
                        lines.append(f"Time remaining: {mins}m {secs}s")
                
                self.caller.msg("\n".join(lines))
            else:
                self.caller.msg("You're tied but status is unclear.")
        else:
            self.caller.msg("You're not currently knotted.")


class CmdStruggle(Command):
    """
    Struggle against knot or leash.
    
    Usage:
        struggle
    
    Warning: Forcing out of a knot may cause damage!
    """
    
    key = "struggle"
    locks = "cmd:all()"
    
    def func(self):
        # Check knot
        if hasattr(self.caller, 'is_tied') and self.caller.is_tied():
            if hasattr(self.caller, 'tie_data'):
                data = self.caller.tie_data
                state = data.get("knot_state", "")
                
                if hasattr(state, 'value'):
                    state = state.value
                
                if state == "locked":
                    self.caller.msg(
                        "|rWarning: The knot is fully locked! "
                        "Forcing free could cause pain and damage.|n"
                    )
                    self.caller.msg("Use 'struggle confirm' if you really want to try.")
                    return
                elif state in ["swelling", "deflating"]:
                    self.caller.msg("You tug and squirm against the swelling knot...")
                    # Roll for escape
                    if randint(1, 100) > 70:
                        self.caller.msg("You manage to pull free before it locks!")
                        # Clear tie data
                        self.caller.tie_data = None
                    else:
                        self.caller.msg("You can't get free - it's swelling too fast!")
                    return
        
        # Check leash
        if hasattr(self.caller, 'is_leashed') and self.caller.is_leashed():
            self.caller.msg("You strain against the leash...")
            
            # Roll against leash strength
            leash_strength = 50  # Default
            if hasattr(self.caller, 'leash_data') and self.caller.leash_data:
                leash_strength = self.caller.leash_data.get("strength", 50)
            
            roll = randint(1, 100)
            if roll > leash_strength:
                self.caller.msg("You break free from the leash!")
                self.caller.leash_data = None
            else:
                self.caller.msg("The leash holds firm.")
            return
        
        self.caller.msg("You're not restrained by anything you can struggle against.")


# =============================================================================
# CMDSET
# =============================================================================

class FeralCmdSet(CmdSet):
    """Commands for feral NPC interaction."""
    
    key = "FeralCmdSet"
    
    def at_cmdset_creation(self):
        self.add(CmdPet())
        self.add(CmdFeed())
        self.add(CmdTame())
        self.add(CmdTrain())
        self.add(CmdPresent())
        self.add(CmdBreed())
        self.add(CmdFeralStatus())
        self.add(CmdKnotStatus())
        self.add(CmdStruggle())


__all__ = [
    "FeralCmdSet",
    "CmdPet", "CmdFeed", "CmdTame", "CmdTrain",
    "CmdPresent", "CmdBreed",
    "CmdFeralStatus", "CmdKnotStatus", "CmdStruggle",
    "find_feral_in_room", "get_ferals_in_room",
]
