"""
Stat Commands
==============

Player commands for viewing and interacting with the stat system.

Commands:
    stats       - View your current stats
    condition   - Quick status check
    rest        - Recover stamina (if safe)
    compose     - Attempt to recover composure
"""

from evennia import Command, CmdSet
from evennia.utils import delay


class CmdStats(Command):
    """
    View your current stats.
    
    Usage:
        stats
        stats <target>  (admin only)
        
    Shows your resource stats (stamina, composure, arousal),
    threshold stats (willpower, sensitivity, resilience),
    and accumulation stats (corruption, notoriety).
    """
    
    key = "stats"
    aliases = ["stat", "status"]
    locks = "cmd:all()"
    help_category = "Character"
    
    def func(self):
        caller = self.caller
        
        # Admin check for viewing others
        if self.args and caller.check_permstring("Admin"):
            target = caller.search(self.args.strip())
            if not target:
                return
        else:
            target = caller
        
        from world.stats import display_stats
        caller.msg(display_stats(target))


class CmdCondition(Command):
    """
    Quick check of your current condition.
    
    Usage:
        condition
        cond
        
    Shows a brief summary of your physical and mental state.
    """
    
    key = "condition"
    aliases = ["cond", "state"]
    locks = "cmd:all()"
    help_category = "Character"
    
    def func(self):
        caller = self.caller
        
        from world.stats import (
            get_stamina_state, get_composure_state, get_arousal_state,
            get_combined_states, is_collapsed, is_broken, can_move
        )
        
        stamina_state = get_stamina_state(caller)
        composure_state = get_composure_state(caller)
        arousal_state = get_arousal_state(caller)
        combined = get_combined_states(caller)
        
        # Build message
        lines = []
        lines.append(f"|wYou are:|n {stamina_state}, {composure_state}, {arousal_state}")
        
        if combined:
            lines.append(f"|wConditions:|n {', '.join(combined)}")
        
        # Warnings
        if is_collapsed(caller):
            lines.append("|r[COLLAPSED - Cannot move]|n")
        elif not can_move(caller):
            lines.append("|r[Movement restricted]|n")
        
        if is_broken(caller):
            lines.append("|r[BROKEN - Cannot resist]|n")
        
        if caller.db.orgasm_denied:
            lines.append("|m[Denied]|n")
        
        caller.msg("\n".join(lines))


class CmdRest(Command):
    """
    Rest to recover stamina.
    
    Usage:
        rest
        
    You must be in a safe location to rest effectively.
    Resting takes time and can be interrupted.
    
    Recovery rates:
        Safe room (home, inn): +20 stamina
        Grove areas: +15 stamina
        Other areas: +5 stamina
        Dangerous areas: Cannot rest
    """
    
    key = "rest"
    locks = "cmd:all()"
    help_category = "Character"
    
    def func(self):
        caller = self.caller
        location = caller.location
        
        from world.stats import get_stat, restore_stamina, is_collapsed
        
        # Check if already at max
        current_stamina = get_stat(caller, "stamina")
        if current_stamina >= 100:
            caller.msg("You're already fully rested.")
            return
        
        # Check location safety
        is_safe = getattr(location.db, 'is_safe', False) or getattr(location, 'is_safe', False)
        is_home = getattr(location.db, 'owner', None) == caller.dbref
        is_grove = getattr(location.db, 'is_grove', False) or "grove" in location.key.lower()
        is_dangerous = getattr(location.db, 'is_dangerous', False)
        
        if is_dangerous:
            caller.msg("You can't rest here—it's too dangerous.")
            return
        
        # Determine recovery amount
        if is_home:
            amount = 25
            msg = "You rest in the comfort of your home."
        elif is_safe:
            amount = 20
            msg = "You find a safe spot to rest."
        elif is_grove:
            amount = 15
            msg = "You rest in the relative safety of the Grove."
        else:
            amount = 5
            msg = "You rest uneasily, one eye open."
        
        # Collapsed characters recover more slowly
        if is_collapsed(caller):
            amount = max(5, amount // 2)
            msg = "You lie still, trying to recover your strength."
        
        # Apply rest
        caller.msg(msg)
        caller.location.msg_contents(
            f"{caller.key} settles down to rest.",
            exclude=[caller]
        )
        
        # Delayed recovery (5 seconds to simulate resting)
        def complete_rest():
            new_stamina = restore_stamina(caller, amount, "resting")
            caller.msg(f"|gYou feel more rested. (Stamina: {new_stamina}/100)|n")
        
        caller.msg("|xResting...|n")
        delay(5, complete_rest)


class CmdCompose(Command):
    """
    Attempt to compose yourself and recover composure.
    
    Usage:
        compose
        
    Take a moment to steady yourself. More effective in safe areas.
    Less effective when aroused or in dangerous situations.
    
    Recovery rates:
        Safe area, low arousal: +15 composure
        Safe area, high arousal: +10 composure
        Unsafe area: +5 composure
        Broken state: Minimal recovery
    """
    
    key = "compose"
    aliases = ["calm", "steady"]
    locks = "cmd:all()"
    help_category = "Character"
    
    def func(self):
        caller = self.caller
        location = caller.location
        
        from world.stats import (
            get_stat, restore_composure, is_broken, is_collapsed
        )
        
        # Check if already at max
        current_composure = get_stat(caller, "composure")
        if current_composure >= 100:
            caller.msg("You're already fully composed.")
            return
        
        # Can't compose if collapsed
        if is_collapsed(caller):
            caller.msg("You can barely stay conscious, let alone compose yourself.")
            return
        
        # Check conditions
        is_safe = getattr(location.db, 'is_safe', False) or getattr(location, 'is_safe', False)
        arousal = get_stat(caller, "arousal")
        was_broken = is_broken(caller)
        
        # Determine recovery
        if was_broken:
            # Broken characters recover very slowly
            amount = 5
            msg = "You try to piece yourself back together..."
        elif is_safe and arousal < 50:
            amount = 15
            msg = "You take a deep breath and steady yourself."
        elif is_safe:
            amount = 10
            msg = "You try to compose yourself, though the heat makes it difficult."
        else:
            amount = 5
            msg = "You try to calm down, but this isn't exactly a relaxing place."
        
        # High arousal penalty
        if arousal >= 70:
            amount = max(3, amount - 5)
        
        # Apply
        caller.msg(msg)
        
        def complete_compose():
            new_composure = restore_composure(caller, amount, "composing")
            caller.msg(f"|gYou feel more composed. (Composure: {new_composure}/100)|n")
        
        caller.msg("|xComposing yourself...|n")
        delay(3, complete_compose)


class CmdDeny(Command):
    """
    Toggle orgasm denial status (admin/owner command).
    
    Usage:
        deny <target>
        deny <target> = on/off
        
    When denied, hitting 100 arousal causes composure damage
    instead of release.
    """
    
    key = "deny"
    locks = "cmd:perm(Admin) or perm(Builder)"
    help_category = "Admin"
    
    def func(self):
        caller = self.caller
        
        if not self.args:
            caller.msg("Usage: deny <target> [= on/off]")
            return
        
        if "=" in self.args:
            target_name, setting = self.args.split("=", 1)
            target_name = target_name.strip()
            setting = setting.strip().lower()
        else:
            target_name = self.args.strip()
            setting = None
        
        target = caller.search(target_name)
        if not target:
            return
        
        current = target.db.orgasm_denied or False
        
        if setting == "on":
            new_state = True
        elif setting == "off":
            new_state = False
        else:
            new_state = not current
        
        target.db.orgasm_denied = new_state
        
        if new_state:
            caller.msg(f"|m{target.key} is now denied.|n")
            target.msg("|mYou feel it lock into place. You are denied.|n")
        else:
            caller.msg(f"|g{target.key} is no longer denied.|n")
            target.msg("|gThe denial lifts. Release is possible again.|n")


class CmdEdge(Command):
    """
    Force a character to edge (admin/owner command).
    
    Usage:
        edge <target>
        edge <target> = <amount>
        
    Builds arousal toward the edge without release.
    Default amount is 20.
    """
    
    key = "edge"
    locks = "cmd:perm(Admin) or perm(Builder)"
    help_category = "Admin"
    
    def func(self):
        caller = self.caller
        
        if not self.args:
            caller.msg("Usage: edge <target> [= amount]")
            return
        
        if "=" in self.args:
            target_name, amount_str = self.args.split("=", 1)
            target_name = target_name.strip()
            try:
                amount = int(amount_str.strip())
            except ValueError:
                amount = 20
        else:
            target_name = self.args.strip()
            amount = 20
        
        target = caller.search(target_name)
        if not target:
            return
        
        from world.stats import build_arousal, get_stat, get_arousal_state
        
        old_arousal = get_stat(target, "arousal")
        new_arousal = build_arousal(target, amount, "edging")
        new_state = get_arousal_state(target)
        
        caller.msg(f"|mEdged {target.key}: {old_arousal} -> {new_arousal} ({new_state})|n")


class CmdDrain(Command):
    """
    Drain a character's stamina or composure (admin command).
    
    Usage:
        drain <target> stamina <amount>
        drain <target> composure <amount>
    """
    
    key = "drain"
    locks = "cmd:perm(Admin)"
    help_category = "Admin"
    
    def func(self):
        caller = self.caller
        
        if not self.args:
            caller.msg("Usage: drain <target> stamina/composure <amount>")
            return
        
        parts = self.args.split()
        if len(parts) < 3:
            caller.msg("Usage: drain <target> stamina/composure <amount>")
            return
        
        target_name = parts[0]
        stat_type = parts[1].lower()
        try:
            amount = int(parts[2])
        except ValueError:
            caller.msg("Amount must be a number.")
            return
        
        target = caller.search(target_name)
        if not target:
            return
        
        from world.stats import drain_stamina, drain_composure, get_stat
        
        if stat_type == "stamina":
            new_val = drain_stamina(target, amount, "admin drain")
            caller.msg(f"Drained {amount} stamina from {target.key}. Now: {new_val}")
        elif stat_type == "composure":
            new_val = drain_composure(target, amount, "admin drain")
            caller.msg(f"Drained {amount} composure from {target.key}. Now: {new_val}")
        else:
            caller.msg("Stat type must be 'stamina' or 'composure'.")


class CmdSetStat(Command):
    """
    Set a character's stat directly (admin command).
    
    Usage:
        setstat <target> <stat> = <value>
        
    Stats: stamina, composure, arousal, willpower, sensitivity,
           resilience, corruption, notoriety
    """
    
    key = "setstat"
    locks = "cmd:perm(Admin)"
    help_category = "Admin"
    
    def func(self):
        caller = self.caller
        
        if not self.args or "=" not in self.args:
            caller.msg("Usage: setstat <target> <stat> = <value>")
            return
        
        left, value_str = self.args.split("=", 1)
        parts = left.strip().split()
        
        if len(parts) < 2:
            caller.msg("Usage: setstat <target> <stat> = <value>")
            return
        
        target_name = parts[0]
        stat_name = parts[1].lower()
        
        try:
            value = int(value_str.strip())
        except ValueError:
            caller.msg("Value must be a number.")
            return
        
        target = caller.search(target_name)
        if not target:
            return
        
        valid_stats = [
            "stamina", "composure", "arousal",
            "willpower", "sensitivity", "resilience",
            "corruption", "notoriety"
        ]
        
        if stat_name not in valid_stats:
            caller.msg(f"Invalid stat. Choose from: {', '.join(valid_stats)}")
            return
        
        from world.stats import set_stat, get_stat
        
        old_val = get_stat(target, stat_name)
        new_val = set_stat(target, stat_name, value)
        
        caller.msg(f"Set {target.key}'s {stat_name}: {old_val} -> {new_val}")


class CmdInitStats(Command):
    """
    Initialize stats for a character (admin command).
    
    Usage:
        initstats <target>
        initstats <target> = <template>
        
    Templates: default, resilient, sensitive, corrupted
    """
    
    key = "initstats"
    locks = "cmd:perm(Admin)"
    help_category = "Admin"
    
    def func(self):
        caller = self.caller
        
        if not self.args:
            caller.msg("Usage: initstats <target> [= template]")
            return
        
        if "=" in self.args:
            target_name, template = self.args.split("=", 1)
            target_name = target_name.strip()
            template = template.strip().lower()
        else:
            target_name = self.args.strip()
            template = "default"
        
        target = caller.search(target_name)
        if not target:
            return
        
        from world.stats import initialize_stats
        
        stats = initialize_stats(target, template)
        caller.msg(f"Initialized {target.key}'s stats with template '{template}':")
        for stat, value in stats.items():
            caller.msg(f"  {stat}: {value}")


# =============================================================================
# COMMAND SET
# =============================================================================

class StatsCmdSet(CmdSet):
    """Commands for the stats system."""
    
    key = "stats_cmdset"
    
    def at_cmdset_creation(self):
        self.add(CmdStats())
        self.add(CmdCondition())
        self.add(CmdRest())
        self.add(CmdCompose())
        self.add(CmdDeny())
        self.add(CmdEdge())
        self.add(CmdDrain())
        self.add(CmdSetStat())
        self.add(CmdInitStats())
