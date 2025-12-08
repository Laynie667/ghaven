"""
Combat Commands for Gilderhaven

Commands for engaging in and managing combat encounters.
"""

from evennia import Command, CmdSet
from evennia.utils import evtable

from world.combat import (
    is_in_combat, get_combat, can_initiate_combat,
    start_combat, start_pvp_combat, process_defeat,
    COMBAT_ACTIONS, COMBAT_STATES, PRIMARY_ATTRIBUTES,
    COMBAT_SKILLS, RESOURCE_POOLS,
    get_attribute, set_attribute, get_resource, get_max_resource,
    get_combat_skill, get_combat_skill_exp,
    get_attribute_display, get_combat_skills_display,
    get_all_resources_display, initialize_combat_stats,
    restore_all_resources, STARTING_ATTRIBUTE_POINTS
)


class CmdCombatStatus(Command):
    """
    View current combat status.
    
    Usage:
        combat
        status
        
    Shows your current combat state, resources, and available actions.
    """
    key = "combat"
    aliases = ["status", "cs"]
    locks = "cmd:all()"
    
    def func(self):
        caller = self.caller
        
        if is_in_combat(caller):
            combat = get_combat(caller)
            self.caller.msg(combat.get_status_display(caller))
        else:
            # Show out-of-combat status
            lines = ["|w=== STATUS ===|n", ""]
            lines.append(get_all_resources_display(caller))
            lines.append("")
            lines.append("|wNot currently in combat.|n")
            self.caller.msg("\n".join(lines))


class CmdAttack(Command):
    """
    Attack an enemy in combat.
    
    Usage:
        attack [target]
        hit [target]
        
    Basic attack using your equipped weapon or fists.
    """
    key = "attack"
    aliases = ["hit", "strike"]
    locks = "cmd:all()"
    
    def func(self):
        caller = self.caller
        
        if not is_in_combat(caller):
            self.caller.msg("You're not in combat.")
            return
        
        combat = get_combat(caller)
        
        # Check if it's our turn
        if combat.get_current_combatant() != caller:
            self.caller.msg("It's not your turn!")
            return
        
        # Get target
        target = None
        if self.args:
            # Find target by name
            enemies = combat.get_enemies(caller)
            for enemy in enemies:
                if enemy.key.lower().startswith(self.args.lower().strip()):
                    target = enemy
                    break
            if not target:
                self.caller.msg("No such target in combat.")
                return
        
        # Execute attack
        result = combat.execute_action(caller, "attack", target)
        
        # Display results
        for msg in result.get("messages", []):
            combat.location.msg_contents(msg)
        
        # Advance turn if successful
        if result.get("success"):
            combat.advance_turn()
            self._prompt_next_turn(combat)
    
    def _prompt_next_turn(self, combat):
        """Prompt the next combatant."""
        if not combat.active:
            return
        
        next_char = combat.get_current_combatant()
        if next_char and hasattr(next_char, "msg"):
            next_char.msg("|yYour turn!|n")
            if hasattr(next_char, "db") and next_char.db.is_npc:
                # Trigger NPC AI
                from evennia.utils import delay
                delay(1, self._npc_turn, combat, next_char)
    
    def _npc_turn(self, combat, npc):
        """Handle NPC turn."""
        if not combat.active:
            return
        
        # Simple AI - just attack
        enemies = combat.get_enemies(npc)
        if enemies:
            target = enemies[0]
            result = combat.execute_action(npc, "attack", target)
            for msg in result.get("messages", []):
                combat.location.msg_contents(msg)
            
            if result.get("success"):
                combat.advance_turn()
                self._prompt_next_turn(combat)


class CmdPowerAttack(Command):
    """
    Perform a powerful but less accurate attack.
    
    Usage:
        power [target]
        smash [target]
        
    Deals 50% more damage but has -15 accuracy.
    Costs more stamina.
    """
    key = "power"
    aliases = ["smash", "powerattack"]
    locks = "cmd:all()"
    
    def func(self):
        caller = self.caller
        
        if not is_in_combat(caller):
            self.caller.msg("You're not in combat.")
            return
        
        combat = get_combat(caller)
        
        if combat.get_current_combatant() != caller:
            self.caller.msg("It's not your turn!")
            return
        
        target = None
        if self.args:
            enemies = combat.get_enemies(caller)
            for enemy in enemies:
                if enemy.key.lower().startswith(self.args.lower().strip()):
                    target = enemy
                    break
        
        result = combat.execute_action(caller, "power_attack", target)
        
        for msg in result.get("messages", []):
            combat.location.msg_contents(msg)
        
        if result.get("success"):
            combat.advance_turn()


class CmdGrapple(Command):
    """
    Attempt to grapple an enemy.
    
    Usage:
        grapple [target]
        grab [target]
        
    Drains stamina and restrains the target.
    Grappled targets cannot flee.
    """
    key = "grapple"
    aliases = ["grab", "wrestle"]
    locks = "cmd:all()"
    
    def func(self):
        caller = self.caller
        
        if not is_in_combat(caller):
            self.caller.msg("You're not in combat.")
            return
        
        combat = get_combat(caller)
        
        if combat.get_current_combatant() != caller:
            self.caller.msg("It's not your turn!")
            return
        
        target = None
        if self.args:
            enemies = combat.get_enemies(caller)
            for enemy in enemies:
                if enemy.key.lower().startswith(self.args.lower().strip()):
                    target = enemy
                    break
        
        result = combat.execute_action(caller, "grapple", target)
        
        for msg in result.get("messages", []):
            combat.location.msg_contents(msg)
        
        if result.get("success"):
            combat.advance_turn()


class CmdDefend(Command):
    """
    Take a defensive stance.
    
    Usage:
        defend
        block
        
    Increases defense by 30 but reduces attack.
    Lasts until your next action.
    """
    key = "defend"
    aliases = ["block", "guard"]
    locks = "cmd:all()"
    
    def func(self):
        caller = self.caller
        
        if not is_in_combat(caller):
            self.caller.msg("You're not in combat.")
            return
        
        combat = get_combat(caller)
        
        if combat.get_current_combatant() != caller:
            self.caller.msg("It's not your turn!")
            return
        
        result = combat.execute_action(caller, "defend")
        
        for msg in result.get("messages", []):
            combat.location.msg_contents(msg)
        
        if result.get("success"):
            combat.advance_turn()


class CmdDodge(Command):
    """
    Focus on evading attacks.
    
    Usage:
        dodge
        evade
        
    Increases evasion by 25 but you cannot attack.
    Lasts until your next action.
    """
    key = "dodge"
    aliases = ["evade"]
    locks = "cmd:all()"
    
    def func(self):
        caller = self.caller
        
        if not is_in_combat(caller):
            self.caller.msg("You're not in combat.")
            return
        
        combat = get_combat(caller)
        
        if combat.get_current_combatant() != caller:
            self.caller.msg("It's not your turn!")
            return
        
        result = combat.execute_action(caller, "dodge")
        
        for msg in result.get("messages", []):
            combat.location.msg_contents(msg)
        
        if result.get("success"):
            combat.advance_turn()


class CmdFlee(Command):
    """
    Attempt to escape from combat.
    
    Usage:
        flee
        run
        escape
        
    Roll evasion vs enemy grappling to escape.
    Cannot flee while grappled - struggle first.
    Costs 15 stamina.
    """
    key = "flee"
    aliases = ["run", "escape"]
    locks = "cmd:all()"
    
    def func(self):
        caller = self.caller
        
        if not is_in_combat(caller):
            self.caller.msg("You're not in combat.")
            return
        
        combat = get_combat(caller)
        
        if combat.get_current_combatant() != caller:
            self.caller.msg("It's not your turn!")
            return
        
        # Check encounter restrictions
        from world.encounters import get_active_encounter, on_player_flee
        encounter = get_active_encounter(caller)
        if encounter:
            can_flee, reason = on_player_flee(caller, combat)
            if not can_flee:
                self.caller.msg(reason)
                return
        
        result = combat.execute_action(caller, "flee")
        
        for msg in result.get("messages", []):
            combat.location.msg_contents(msg)
        
        if result.get("fled"):
            # Combat ended, player escaped
            caller.msg("|gYou escape the fight!|n")
            # Check if combat should end
            ended, winner, condition = combat.check_victory()
            if ended:
                combat.end_combat(winner, condition)
                # Hook encounter system
                if encounter:
                    from world.encounters import on_combat_end
                    on_combat_end(combat, winner, condition)
        elif result.get("success"):
            combat.advance_turn()


class CmdStruggle(Command):
    """
    Attempt to break free from a grapple.
    
    Usage:
        struggle
        breakfree
        
    Contest your grappling skill against the grappler.
    """
    key = "struggle"
    aliases = ["breakfree", "escape_grapple"]
    locks = "cmd:all()"
    
    def func(self):
        caller = self.caller
        
        if not is_in_combat(caller):
            self.caller.msg("You're not in combat.")
            return
        
        combat = get_combat(caller)
        
        if combat.get_current_combatant() != caller:
            self.caller.msg("It's not your turn!")
            return
        
        result = combat.execute_action(caller, "struggle")
        
        for msg in result.get("messages", []):
            combat.location.msg_contents(msg)
        
        if result.get("success"):
            combat.advance_turn()


class CmdTease(Command):
    """
    Attempt to fluster your opponent.
    
    Usage:
        tease [target]
        flirt [target]
        
    Deals composure damage based on charisma and seduction skill.
    """
    key = "tease"
    aliases = ["flirt", "taunt"]
    locks = "cmd:all()"
    
    def func(self):
        caller = self.caller
        
        if not is_in_combat(caller):
            self.caller.msg("You're not in combat.")
            return
        
        combat = get_combat(caller)
        
        if combat.get_current_combatant() != caller:
            self.caller.msg("It's not your turn!")
            return
        
        target = None
        if self.args:
            enemies = combat.get_enemies(caller)
            for enemy in enemies:
                if enemy.key.lower().startswith(self.args.lower().strip()):
                    target = enemy
                    break
        
        result = combat.execute_action(caller, "tease", target)
        
        for msg in result.get("messages", []):
            combat.location.msg_contents(msg)
        
        if result.get("success"):
            combat.advance_turn()


class CmdSeduce(Command):
    """
    Attempt to overwhelm your opponent with charm.
    
    Usage:
        seduce [target]
        charm [target]
        
    Contested seduction vs resistance.
    Deals significant composure damage on success.
    """
    key = "seduce"
    aliases = ["charm"]
    locks = "cmd:all()"
    
    def func(self):
        caller = self.caller
        
        if not is_in_combat(caller):
            self.caller.msg("You're not in combat.")
            return
        
        combat = get_combat(caller)
        
        if combat.get_current_combatant() != caller:
            self.caller.msg("It's not your turn!")
            return
        
        target = None
        if self.args:
            enemies = combat.get_enemies(caller)
            for enemy in enemies:
                if enemy.key.lower().startswith(self.args.lower().strip()):
                    target = enemy
                    break
        
        result = combat.execute_action(caller, "seduce", target)
        
        for msg in result.get("messages", []):
            combat.location.msg_contents(msg)
        
        if result.get("success"):
            combat.advance_turn()


class CmdIntimidate(Command):
    """
    Try to scare off your opponent.
    
    Usage:
        intimidate [target]
        scare [target]
        
    Contested intimidation vs resistance.
    On strong success, enemy flees.
    """
    key = "intimidate"
    aliases = ["scare", "threaten"]
    locks = "cmd:all()"
    
    def func(self):
        caller = self.caller
        
        if not is_in_combat(caller):
            self.caller.msg("You're not in combat.")
            return
        
        combat = get_combat(caller)
        
        if combat.get_current_combatant() != caller:
            self.caller.msg("It's not your turn!")
            return
        
        target = None
        if self.args:
            enemies = combat.get_enemies(caller)
            for enemy in enemies:
                if enemy.key.lower().startswith(self.args.lower().strip()):
                    target = enemy
                    break
        
        result = combat.execute_action(caller, "intimidate", target)
        
        for msg in result.get("messages", []):
            combat.location.msg_contents(msg)
        
        if result.get("success"):
            combat.advance_turn()


class CmdBefriend(Command):
    """
    Attempt to calm a creature and end combat peacefully.
    
    Usage:
        befriend [target]
        calm [target]
        
    Only works on befriendable creatures.
    Based on charisma vs creature's disposition.
    """
    key = "befriend"
    aliases = ["calm", "pacify"]
    locks = "cmd:all()"
    
    def func(self):
        caller = self.caller
        
        if not is_in_combat(caller):
            self.caller.msg("You're not in combat.")
            return
        
        combat = get_combat(caller)
        
        if combat.get_current_combatant() != caller:
            self.caller.msg("It's not your turn!")
            return
        
        target = None
        if self.args:
            enemies = combat.get_enemies(caller)
            for enemy in enemies:
                if enemy.key.lower().startswith(self.args.lower().strip()):
                    target = enemy
                    break
        
        result = combat.execute_action(caller, "befriend", target)
        
        for msg in result.get("messages", []):
            combat.location.msg_contents(msg)
        
        if result.get("success"):
            combat.advance_turn()


class CmdSubmit(Command):
    """
    Surrender to your opponent.
    
    Usage:
        submit
        surrender
        yield
        
    Immediately ends combat in defeat.
    What happens next depends on who defeated you.
    """
    key = "submit"
    aliases = ["surrender", "yield", "give up"]
    locks = "cmd:all()"
    
    def func(self):
        caller = self.caller
        
        if not is_in_combat(caller):
            self.caller.msg("You're not in combat.")
            return
        
        combat = get_combat(caller)
        
        # Can submit on any turn
        result = combat.execute_action(caller, "submit")
        
        for msg in result.get("messages", []):
            combat.location.msg_contents(msg)


class CmdChallenge(Command):
    """
    Challenge another player to combat.
    
    Usage:
        challenge <player>
        duel <player>
        
    Target must have PvP enabled.
    """
    key = "challenge"
    aliases = ["duel", "fight"]
    locks = "cmd:all()"
    
    def func(self):
        caller = self.caller
        
        if not self.args:
            self.caller.msg("Challenge who?")
            return
        
        can_fight, reason = can_initiate_combat(caller)
        if not can_fight:
            self.caller.msg(reason)
            return
        
        # Find target in room
        target = caller.search(self.args.strip(), location=caller.location)
        if not target:
            return
        
        if target == caller:
            self.caller.msg("You can't fight yourself.")
            return
        
        if not hasattr(target, "db"):
            self.caller.msg("You can't fight that.")
            return
        
        # Check PvP settings
        if not target.db.pvp_enabled:
            self.caller.msg(f"{target.key} has PvP disabled.")
            return
        
        if not caller.db.pvp_enabled:
            self.caller.msg("You need to enable PvP first. Use: pvp on")
            return
        
        # Start PvP combat
        combat, message = start_pvp_combat(caller, target, caller.location)
        if not combat:
            self.caller.msg(message)
            return


class CmdPvPToggle(Command):
    """
    Toggle PvP mode on or off.
    
    Usage:
        pvp
        pvp on
        pvp off
        
    When PvP is enabled, other players can challenge you.
    """
    key = "pvp"
    locks = "cmd:all()"
    
    def func(self):
        caller = self.caller
        
        current = caller.db.pvp_enabled or False
        
        if not self.args:
            status = "|gON|n" if current else "|rOFF|n"
            self.caller.msg(f"PvP is currently: {status}")
            return
        
        arg = self.args.strip().lower()
        
        if arg == "on":
            caller.db.pvp_enabled = True
            self.caller.msg("|gPvP enabled.|n Other players can now challenge you.")
        elif arg == "off":
            if is_in_combat(caller):
                self.caller.msg("You can't disable PvP while in combat!")
                return
            caller.db.pvp_enabled = False
            self.caller.msg("|rPvP disabled.|n")
        else:
            self.caller.msg("Usage: pvp on/off")


class CmdAttributes(Command):
    """
    View or manage your attributes.
    
    Usage:
        attributes
        attr
        stats
        
    Shows your primary attributes and their effects.
    """
    key = "attributes"
    aliases = ["attr", "stats"]
    locks = "cmd:all()"
    
    def func(self):
        caller = self.caller
        
        # Initialize if needed
        initialize_combat_stats(caller)
        
        lines = ["|w=== ATTRIBUTES ===|n", ""]
        lines.append(get_attribute_display(caller))
        lines.append("")
        lines.append("|wResource Pools:|n")
        lines.append(get_all_resources_display(caller))
        
        self.caller.msg("\n".join(lines))


class CmdCombatSkills(Command):
    """
    View your combat skills.
    
    Usage:
        cskills
        combatskills
        
    Shows your combat skill levels and experience progress.
    """
    key = "cskills"
    aliases = ["combatskills"]
    locks = "cmd:all()"
    
    def func(self):
        caller = self.caller
        
        initialize_combat_stats(caller)
        
        self.caller.msg(get_combat_skills_display(caller))


class CmdRest(Command):
    """
    Rest to recover resources.
    
    Usage:
        rest
        
    Restores HP, stamina, and composure over time.
    Cannot rest while in combat.
    """
    key = "rest"
    aliases = ["recover"]
    locks = "cmd:all()"
    
    def func(self):
        caller = self.caller
        
        if is_in_combat(caller):
            self.caller.msg("You can't rest during combat!")
            return
        
        restore_all_resources(caller)
        
        caller.location.msg_contents(
            f"{caller.key} takes a moment to rest.",
            exclude=[caller]
        )
        self.caller.msg("|gYou rest and recover fully.|n")
        self.caller.msg(get_all_resources_display(caller))


class CmdDefeatPrefs(Command):
    """
    Set your defeat scene preferences.
    
    Usage:
        defeatprefs
        defeatprefs <option>
        
    Options:
        fade    - Skip scenes, just wake up after (fade to black)
        summary - Brief text description of what happened
        full    - Detailed, interactive scenes
        choice  - Ask each time
        
    This determines what happens when you're defeated in combat.
    """
    key = "defeatprefs"
    aliases = ["defeatpreferences", "captureprefs"]
    locks = "cmd:all()"
    
    def func(self):
        caller = self.caller
        
        options = {
            "fade": "Fade to black - skip scenes entirely",
            "summary": "Brief summary text",
            "full": "Full detailed scenes",
            "choice": "Ask each time",
        }
        
        current = caller.db.defeat_preferences or "choice"
        
        if not self.args:
            lines = ["|w=== DEFEAT PREFERENCES ===|n", ""]
            lines.append(f"Current setting: |c{current}|n")
            lines.append("")
            lines.append("Available options:")
            for key, desc in options.items():
                marker = " |y<- current|n" if key == current else ""
                lines.append(f"  |w{key}|n: {desc}{marker}")
            lines.append("")
            lines.append("Use: defeatprefs <option> to change")
            self.caller.msg("\n".join(lines))
            return
        
        choice = self.args.strip().lower()
        
        if choice not in options:
            self.caller.msg(f"Invalid option. Choose from: {', '.join(options.keys())}")
            return
        
        caller.db.defeat_preferences = choice
        self.caller.msg(f"|gDefeat preference set to: {choice}|n")


class CmdCombatHelp(Command):
    """
    Get help with combat commands.
    
    Usage:
        combathelp
        fighthelp
        
    Lists all combat commands and their uses.
    """
    key = "combathelp"
    aliases = ["fighthelp", "chelp"]
    locks = "cmd:all()"
    
    def func(self):
        lines = [
            "|w=== COMBAT HELP ===|n",
            "",
            "|yIn Combat:|n",
            "  |wattack|n <target>   - Basic attack",
            "  |wpower|n <target>    - Heavy attack (more damage, less accuracy)",
            "  |wgrapple|n <target>  - Grab and restrain",
            "  |wtease|n <target>    - Composure damage",
            "  |wseduce|n <target>   - Strong composure attack",
            "  |wintimidate|n <target> - Try to scare off enemy",
            "  |wbefriend|n <target> - Calm a creature (if possible)",
            "",
            "  |wdefend|n            - Defensive stance (+30 defense)",
            "  |wdodge|n             - Evasion stance (+25 evasion)",
            "  |wflee|n              - Attempt to escape",
            "  |wstruggle|n          - Break free from grapple",
            "  |wsubmit|n            - Surrender",
            "",
            "  |wcombat|n            - View combat status",
            "",
            "|yOut of Combat:|n",
            "  |wchallenge|n <player> - PvP duel",
            "  |wpvp|n on/off        - Toggle PvP mode",
            "  |wrest|n              - Recover resources",
            "  |wattributes|n        - View stats",
            "  |wcskills|n           - View combat skills",
            "  |wdefeatprefs|n       - Scene preferences",
            "",
            "|yResource Pools:|n",
            "  |rHP|n - Physical health (0 = knocked out)",
            "  |yStamina|n - Energy (0 = exhausted, can't flee)",
            "  |mComposure|n - Mental state (0 = overwhelmed)",
        ]
        
        self.caller.msg("\n".join(lines))


# =============================================================================
# Admin Commands
# =============================================================================

class CmdSpawnCreature(Command):
    """
    Spawn a creature for testing.
    
    Usage:
        spawncreature <creature_key>
        
    Admin command to spawn creatures.
    """
    key = "spawncreature"
    aliases = ["spawnmob"]
    locks = "cmd:perm(Admin)"
    
    def func(self):
        if not self.args:
            from world.creatures import CREATURE_TEMPLATES
            keys = ", ".join(CREATURE_TEMPLATES.keys())
            self.caller.msg(f"Available creatures: {keys}")
            return
        
        creature_key = self.args.strip().lower()
        
        from world.creatures import get_creature_template, get_creature_stats
        
        template = get_creature_template(creature_key)
        if not template:
            self.caller.msg(f"Unknown creature: {creature_key}")
            return
        
        # Create a temporary NPC for the creature
        from evennia import create_object
        
        creature = create_object(
            "typeclasses.characters.Character",
            key=template["name"],
            location=self.caller.location,
        )
        
        # Set up creature stats
        stats = get_creature_stats(creature_key)
        creature.db.is_npc = True
        creature.db.creature_type = creature_key
        creature.db.resources = {
            "hp": stats["max_hp"],
            "stamina": stats["max_stamina"],
            "composure": stats["max_composure"],
        }
        creature.db.attributes = stats["attributes"]
        creature.db.combat_skills = stats["skills"]
        creature.db.befriendable = template.get("befriendable", False)
        creature.db.befriend_difficulty = template.get("befriend_difficulty", 20)
        
        self.caller.msg(f"|gSpawned {creature.key}.|n")
        
        # Optionally start combat
        combat = start_combat(self.caller, [creature], self.caller.location)


class CmdSetAttribute(Command):
    """
    Set a character's attribute.
    
    Usage:
        setattr <attribute> <value>
        setattr <character> <attribute> <value>
        
    Admin command to modify attributes.
    """
    key = "setattr"
    locks = "cmd:perm(Admin)"
    
    def func(self):
        if not self.args:
            attrs = ", ".join(PRIMARY_ATTRIBUTES.keys())
            self.caller.msg(f"Usage: setattr <attr> <value>\nAttributes: {attrs}")
            return
        
        args = self.args.split()
        
        if len(args) == 2:
            target = self.caller
            attr_key = args[0].lower()
            try:
                value = int(args[1])
            except ValueError:
                self.caller.msg("Value must be a number.")
                return
        elif len(args) >= 3:
            target = self.caller.search(args[0])
            if not target:
                return
            attr_key = args[1].lower()
            try:
                value = int(args[2])
            except ValueError:
                self.caller.msg("Value must be a number.")
                return
        else:
            self.caller.msg("Usage: setattr [target] <attribute> <value>")
            return
        
        if attr_key not in PRIMARY_ATTRIBUTES:
            self.caller.msg(f"Unknown attribute. Options: {', '.join(PRIMARY_ATTRIBUTES.keys())}")
            return
        
        set_attribute(target, attr_key, value)
        self.caller.msg(f"Set {target.key}'s {attr_key} to {value}.")


class CmdTriggerEncounter(Command):
    """
    Trigger a specific encounter.
    
    Usage:
        triggerencounter <encounter_key>
        triggerencounter
        
    Admin command to trigger encounters for testing.
    """
    key = "triggerencounter"
    aliases = ["spawnencounter"]
    locks = "cmd:perm(Admin)"
    
    def func(self):
        from world.encounters import ENCOUNTER_TEMPLATES, trigger_encounter
        
        if not self.args:
            keys = ", ".join(ENCOUNTER_TEMPLATES.keys())
            self.caller.msg(f"Available encounters:\n{keys}")
            return
        
        encounter_key = self.args.strip().lower()
        
        if encounter_key not in ENCOUNTER_TEMPLATES:
            self.caller.msg(f"Unknown encounter: {encounter_key}")
            return
        
        encounter = trigger_encounter(self.caller, encounter_key, force=True)
        
        if encounter:
            self.caller.msg(f"|gTriggered encounter: {encounter_key}|n")
        else:
            self.caller.msg("Failed to trigger encounter.")


class CmdSetDanger(Command):
    """
    Set danger level for current room.
    
    Usage:
        setdanger <level>
        setdanger
        
    Levels: safe, peaceful, normal, dangerous, deadly
    """
    key = "setdanger"
    locks = "cmd:perm(Admin)"
    
    def func(self):
        from world.encounters import DANGER_LEVELS
        
        room = self.caller.location
        if not room:
            self.caller.msg("You're not in a room.")
            return
        
        if not self.args:
            current = room.db.danger_level or "default"
            levels = ", ".join(DANGER_LEVELS.keys())
            self.caller.msg(f"Current: {current}\nOptions: {levels}")
            return
        
        level = self.args.strip().lower()
        
        if level not in DANGER_LEVELS:
            self.caller.msg(f"Invalid level. Options: {', '.join(DANGER_LEVELS.keys())}")
            return
        
        room.db.danger_level = level
        self.caller.msg(f"Set room danger to: {level}")


# =============================================================================
# Command Set
# =============================================================================

class CombatCmdSet(CmdSet):
    """Combat commands."""
    
    key = "combat_cmdset"
    
    def at_cmdset_creation(self):
        self.add(CmdCombatStatus())
        self.add(CmdAttack())
        self.add(CmdPowerAttack())
        self.add(CmdGrapple())
        self.add(CmdDefend())
        self.add(CmdDodge())
        self.add(CmdFlee())
        self.add(CmdStruggle())
        self.add(CmdTease())
        self.add(CmdSeduce())
        self.add(CmdIntimidate())
        self.add(CmdBefriend())
        self.add(CmdSubmit())
        self.add(CmdChallenge())
        self.add(CmdPvPToggle())
        self.add(CmdAttributes())
        self.add(CmdCombatSkills())
        self.add(CmdRest())
        self.add(CmdDefeatPrefs())
        self.add(CmdCombatHelp())


class CombatAdminCmdSet(CmdSet):
    """Admin combat commands."""
    
    key = "combat_admin_cmdset"
    
    def at_cmdset_creation(self):
        self.add(CmdSpawnCreature())
        self.add(CmdSetAttribute())
        self.add(CmdTriggerEncounter())
        self.add(CmdSetDanger())
