"""
State Commands for Gilderhaven

Commands for viewing and managing character states like
energy, arousal, condition, etc.
"""

from evennia import Command, CmdSet

from world.states import (
    get_state_display, get_state_summary, initialize_states,
    get_energy, get_arousal, get_condition, get_cleanliness, get_intoxication,
    get_energy_level, get_arousal_level, get_condition_level,
    get_cleanliness_level, get_intoxication_level,
    modify_energy, modify_arousal, modify_condition,
    modify_cleanliness, modify_intoxication,
    restore_all_states, clean, arouse, intoxicate,
    MAX_ENERGY, MAX_AROUSAL, MAX_CONDITION, MAX_CLEANLINESS, MAX_INTOXICATION,
)


class CmdStatus(Command):
    """
    View your current status.
    
    Usage:
        status
        status verbose
        
    Shows energy, condition, arousal, cleanliness, and intoxication.
    Use 'verbose' to see exact numbers.
    """
    key = "status"
    aliases = ["state", "condition", "vitals"]
    locks = "cmd:all()"
    
    def func(self):
        caller = self.caller
        
        # Initialize states if needed
        initialize_states(caller)
        
        verbose = "verbose" in self.args.lower() if self.args else False
        
        self.caller.msg(get_state_display(caller, verbose=verbose))


class CmdEnergy(Command):
    """
    View your energy level.
    
    Usage:
        energy
        
    Energy affects gathering efficiency and movement.
    Rest to recover energy faster.
    """
    key = "energy"
    aliases = ["stamina", "tired"]
    locks = "cmd:all()"
    
    def func(self):
        caller = self.caller
        initialize_states(caller)
        
        energy = get_energy(caller)
        level = get_energy_level(caller)
        
        bar = _make_bar(energy, MAX_ENERGY, level.get("color", "|g"))
        
        lines = [
            f"|wEnergy:|n {bar} {energy}/{MAX_ENERGY}",
            f"Status: {level['color']}{level['display']}|n",
        ]
        
        if level.get("desc"):
            lines.append(f"  {level['desc']}")
        
        # Show modifiers
        gather_mod = level.get("gather_penalty", 1.0)
        if gather_mod != 1.0:
            lines.append(f"  Gathering efficiency: {int(gather_mod * 100)}%")
        
        self.caller.msg("\n".join(lines))


class CmdArousal(Command):
    """
    View your arousal level.
    
    Usage:
        arousal
        
    Arousal affects your appearance and some interactions.
    It naturally decays over time.
    """
    key = "arousal"
    aliases = ["horny", "lust"]
    locks = "cmd:all()"
    
    def func(self):
        caller = self.caller
        initialize_states(caller)
        
        arousal = get_arousal(caller)
        level = get_arousal_level(caller)
        
        # Heart-based display
        hearts = "|m" + "♥" * arousal + "|n" + "♡" * (MAX_AROUSAL - arousal)
        
        lines = [
            f"|wArousal:|n {hearts}",
            f"Status: {level['color']}{level['display']}|n",
        ]
        
        if level.get("desc"):
            # Process pronouns in desc
            desc = level['desc']
            pronouns = caller.db.pronouns or {}
            subject = pronouns.get("subject", "they")
            desc = desc.replace("&they", subject)
            desc = desc.replace("&They", subject.capitalize())
            lines.append(f"  {desc}")
        
        self.caller.msg("\n".join(lines))


class CmdWash(Command):
    """
    Clean yourself.
    
    Usage:
        wash
        bathe
        
    Requires being near water (bath house, waterfront, etc.)
    """
    key = "wash"
    aliases = ["bathe", "clean", "shower"]
    locks = "cmd:all()"
    
    def func(self):
        caller = self.caller
        location = caller.location
        
        # Check for bath/water tag
        can_wash = False
        wash_type = "wash"
        
        if location:
            if location.tags.has("bath", category="room_flag"):
                can_wash = True
                wash_type = "bath"
            elif location.tags.has("water", category="room_flag"):
                can_wash = True
                wash_type = "swim"
            elif location.tags.has("fishing", category="room_flag"):
                can_wash = True
                wash_type = "swim"
        
        if not can_wash:
            self.caller.msg("There's nowhere to wash here. Find a bath house or water source.")
            return
        
        clean(caller, wash_type)
        
        new_level = get_cleanliness_level(caller)
        
        if wash_type == "bath":
            self.caller.msg("|cYou sink into the warm water and scrub yourself clean.|n")
        elif wash_type == "swim":
            self.caller.msg("|cYou wash off in the water, feeling refreshed.|n")
        else:
            self.caller.msg("|cYou clean yourself up.|n")
        
        self.caller.msg(f"Cleanliness: {new_level['color']}{new_level['display']}|n")


class CmdDrink(Command):
    """
    Have an alcoholic drink.
    
    Usage:
        drink
        drink <item>
        
    Increases intoxication. Effects vary by drink.
    """
    key = "drink"
    aliases = ["booze"]
    locks = "cmd:all()"
    
    def func(self):
        caller = self.caller
        
        # Check if in tavern/bar
        location = caller.location
        can_drink = False
        
        if location:
            if location.tags.has("shop", category="room_flag"):
                can_drink = True
            if "tavern" in location.key.lower() or "bar" in location.key.lower():
                can_drink = True
            if "tipsy" in location.key.lower():
                can_drink = True
        
        if not can_drink:
            self.caller.msg("Find a tavern or bar to get a drink.")
            return
        
        # Simple drinking - would integrate with shop/item system
        old_level = get_intoxication_level(caller)
        intoxicate(caller, 15, "drink")
        new_level = get_intoxication_level(caller)
        
        self.caller.msg("|yYou order a drink and knock it back.|n")
        self.caller.msg(f"Feeling: {new_level['color']}{new_level['display']}|n")
        
        # Notify room if notably drunk
        if get_intoxication(caller) >= 30:
            caller.location.msg_contents(
                f"{caller.key} orders another drink.",
                exclude=[caller]
            )


class CmdSoberUp(Command):
    """
    Try to sober up.
    
    Usage:
        soberup
        
    Drink water, eat food, or just wait it out.
    """
    key = "soberup"
    aliases = ["sober"]
    locks = "cmd:all()"
    
    def func(self):
        caller = self.caller
        
        intox = get_intoxication(caller)
        
        if intox <= 10:
            self.caller.msg("You're already sober.")
            return
        
        # Reduce intoxication slightly
        modify_intoxication(caller, -10)
        
        new_level = get_intoxication_level(caller)
        
        self.caller.msg("|wYou take a moment to collect yourself.|n")
        self.caller.msg(f"Feeling: {new_level['color']}{new_level['display']}|n")


# =============================================================================
# Admin Commands
# =============================================================================

class CmdSetState(Command):
    """
    Set a character's state value.
    
    Usage:
        setstate <state> <value>
        setstate <character> <state> <value>
        
    States: energy, arousal, condition, cleanliness, intoxication
    """
    key = "setstate"
    locks = "cmd:perm(Admin)"
    
    def func(self):
        if not self.args:
            self.caller.msg("Usage: setstate <state> <value>")
            self.caller.msg("States: energy, arousal, condition, cleanliness, intoxication")
            return
        
        args = self.args.split()
        
        if len(args) == 2:
            target = self.caller
            state_key = args[0].lower()
            try:
                value = int(args[1])
            except ValueError:
                self.caller.msg("Value must be a number.")
                return
        elif len(args) >= 3:
            target = self.caller.search(args[0])
            if not target:
                return
            state_key = args[1].lower()
            try:
                value = int(args[2])
            except ValueError:
                self.caller.msg("Value must be a number.")
                return
        else:
            self.caller.msg("Usage: setstate [target] <state> <value>")
            return
        
        initialize_states(target)
        
        if state_key == "energy":
            from world.states import set_energy
            set_energy(target, value)
        elif state_key == "arousal":
            from world.states import set_arousal
            set_arousal(target, value)
        elif state_key == "condition":
            from world.states import set_condition
            set_condition(target, value)
        elif state_key in ("cleanliness", "clean"):
            from world.states import set_cleanliness
            set_cleanliness(target, value)
        elif state_key in ("intoxication", "drunk"):
            from world.states import set_intoxication
            set_intoxication(target, value)
        else:
            self.caller.msg(f"Unknown state: {state_key}")
            return
        
        self.caller.msg(f"Set {target.key}'s {state_key} to {value}.")


class CmdRestoreStates(Command):
    """
    Restore all states to default.
    
    Usage:
        restorestates
        restorestates <character>
    """
    key = "restorestates"
    locks = "cmd:perm(Admin)"
    
    def func(self):
        if self.args:
            target = self.caller.search(self.args.strip())
            if not target:
                return
        else:
            target = self.caller
        
        restore_all_states(target)
        self.caller.msg(f"Restored all states for {target.key}.")


# =============================================================================
# Helper Functions
# =============================================================================

def _make_bar(current, maximum, color, length=10):
    """Create a visual bar."""
    filled = int((current / maximum) * length) if maximum > 0 else 0
    empty = length - filled
    return f"{color}{'█' * filled}|n{'░' * empty}"


# =============================================================================
# Command Sets
# =============================================================================

class StateCmdSet(CmdSet):
    """State viewing commands."""
    
    key = "state_cmdset"
    
    def at_cmdset_creation(self):
        self.add(CmdStatus())
        self.add(CmdEnergy())
        self.add(CmdArousal())
        self.add(CmdWash())
        self.add(CmdDrink())
        self.add(CmdSoberUp())


class StateAdminCmdSet(CmdSet):
    """State admin commands."""
    
    key = "state_admin_cmdset"
    
    def at_cmdset_creation(self):
        self.add(CmdSetState())
        self.add(CmdRestoreStates())
