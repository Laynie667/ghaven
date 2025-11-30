"""
World Commands
==============

Commands for the world systems, game management, and...
special surprises for unsuspecting players.
"""

from evennia import Command, CmdSet, DefaultScript
from evennia.utils import search
import random


# =============================================================================
# PLAYER COMMANDS
# =============================================================================

class CmdStatus(Command):
    """
    View your full status.
    
    Usage:
        status
        status/full
        status/brief
    
    Shows your current state across all systems.
    """
    
    key = "status"
    aliases = ["mystatus", "state"]
    locks = "cmd:all()"
    
    def func(self):
        caller = self.caller
        
        from ..integration import get_character_summary
        
        if "brief" in self.switches:
            # Brief status
            lines = [f"=== {caller.key} ==="]
            
            if hasattr(caller, 'character_state'):
                state = caller.character_state
                lines.append(f"Health: {state.physical.health} | Stamina: {state.physical.stamina}")
                lines.append(f"Arousal: {state.sexual.arousal}/100")
            
            lines.append(f"Resistance: {caller.db.current_resistance}/100")
            lines.append(f"Captured: {'Yes' if caller.db.is_captured else 'No'}")
            lines.append(f"Vulnerability: {caller.vulnerability}")
            
            caller.msg("\n".join(lines))
        else:
            # Full status
            caller.msg(get_character_summary(caller))


class CmdEscape(Command):
    """
    Attempt to escape your current situation.
    
    Usage:
        escape
    
    Try to break free. Success depends on your resistance,
    condition, and the difficulty of your situation.
    
    Warning: Failed escapes have consequences.
    """
    
    key = "escape"
    aliases = ["flee", "breakfree"]
    locks = "cmd:all()"
    
    def func(self):
        caller = self.caller
        
        if not caller.db.is_captured:
            caller.msg("You're not captured. Yet.")
            return
        
        # Get escape difficulty from location
        difficulty = 50
        if caller.location and hasattr(caller.location, 'db'):
            difficulty = caller.location.db.escape_difficulty or 50
        
        success, msg = caller.can_escape(difficulty)
        caller.msg(msg)
        
        if success:
            caller.db.is_captured = False
            caller.db.current_owner = None
            caller.location.msg_contents(
                f"{caller.key} breaks free!",
                exclude=[caller]
            )
        else:
            # Failed escape triggers punishment
            caller.location.msg_contents(
                f"{caller.key}'s escape attempt fails.",
                exclude=[caller]
            )
            
            # NPCs react
            for npc in [obj for obj in caller.location.contents 
                       if hasattr(obj, 'execute_action')]:
                result = npc.execute_action("punish", caller)
                caller.location.msg_contents(result)


class CmdSubmit(Command):
    """
    Submit to your situation.
    
    Usage:
        submit
        submit <target>
    
    Stop resisting. Accept your fate.
    Reduces resistance but may earn better treatment.
    """
    
    key = "submit"
    aliases = ["yield", "surrender"]
    locks = "cmd:all()"
    
    def func(self):
        caller = self.caller
        
        target = None
        if self.args:
            target = caller.search(self.args.strip())
        
        # Reduce resistance significantly
        caller.db.current_resistance = max(0, caller.db.current_resistance - 20)
        
        if target:
            caller.msg(f"You submit to {target.key}...")
            caller.location.msg_contents(
                f"{caller.key} submits to {target.key}.",
                exclude=[caller]
            )
        else:
            caller.msg("You stop resisting...")
            caller.location.msg_contents(
                f"{caller.key} submits meekly.",
                exclude=[caller]
            )
        
        # Track submission
        if not caller.db.is_captured and target:
            caller.get_captured(target, "voluntary submission")


class CmdBeg(Command):
    """
    Beg for something.
    
    Usage:
        beg
        beg <target> for <thing>
        beg for mercy
        beg for release
        beg for more
    
    Begging can have... various results.
    """
    
    key = "beg"
    aliases = ["plead"]
    locks = "cmd:all()"
    
    def func(self):
        caller = self.caller
        
        # Parse arguments
        if "for" in self.args:
            parts = self.args.split("for", 1)
            target_name = parts[0].strip()
            request = parts[1].strip()
            target = caller.search(target_name) if target_name else None
        else:
            target = None
            request = self.args.strip() or "mercy"
        
        # Display begging
        if target:
            caller.location.msg_contents(
                f"{caller.key} begs {target.key} for {request}.",
            )
        else:
            caller.location.msg_contents(
                f"{caller.key} begs pathetically for {request}.",
            )
        
        # Effect depends on request
        if request in ["mercy", "release", "freedom"]:
            # Begging for mercy lowers resistance (accepting your place)
            caller.db.current_resistance = max(0, caller.db.current_resistance - 5)
            caller.msg("Your begging only reinforces your helplessness...")
            
        elif request in ["more", "please", "cum", "orgasm"]:
            # Begging for pleasure increases arousal
            if hasattr(caller, 'character_state'):
                state = caller.character_state
                state.sexual.increase_arousal(15)
                caller.character_state = state
                caller.msg("Your shameless begging makes you even more aroused...")
            
        # NPCs may respond
        if target and hasattr(target, 'db') and target.db.disposition:
            disposition = target.db.disposition
            
            if disposition in ["caring", "protective"]:
                caller.msg(f"{target.key} looks at you with something like sympathy...")
            elif disposition in ["cruel", "sadistic"]:
                caller.msg(f"{target.key} laughs at your pitiful begging.")
                target.execute_action("use", caller)


class CmdVulnerability(Command):
    """
    Check your vulnerability level.
    
    Usage:
        vulnerability
    
    Shows how vulnerable you are to capture and events.
    Higher vulnerability means more... things happening.
    """
    
    key = "vulnerability"
    aliases = ["vuln"]
    locks = "cmd:all()"
    
    def func(self):
        caller = self.caller
        
        vuln = caller.vulnerability
        
        lines = [f"=== Vulnerability: {vuln}% ==="]
        
        if vuln < 30:
            lines.append("You're relatively safe. For now.")
        elif vuln < 50:
            lines.append("You're starting to attract attention...")
        elif vuln < 70:
            lines.append("You're a tempting target.")
        elif vuln < 90:
            lines.append("You're practically begging to be caught.")
        else:
            lines.append("You might as well wear a sign saying 'take me'.")
        
        # Show contributing factors
        lines.append("\n--- Factors ---")
        
        resistance = caller.db.current_resistance or 80
        if resistance < 50:
            lines.append(f"Low resistance: +{(100 - resistance) // 2}")
        
        captures = caller.db.times_captured or 0
        if captures > 0:
            lines.append(f"Previous captures ({captures}): +{captures * 5}")
        
        if hasattr(caller, 'inflation'):
            tracker = caller.inflation
            total = tracker.get_total_volume()
            if total > 500:
                lines.append(f"Inflation ({total}ml): +10-30")
        
        if hasattr(caller, 'transformations'):
            mgr = caller.transformations
            for trans in mgr.get_all_active():
                if trans.progress > 20:
                    lines.append(f"{trans.transformation_type.value}: +{trans.progress // 10}")
        
        caller.msg("\n".join(lines))


# =============================================================================
# ADMIN/GM COMMANDS  
# =============================================================================

class CmdGameStatus(Command):
    """
    View game systems status.
    
    Usage:
        gamestatus
    
    Shows status of tick system, NPCs, and events.
    """
    
    key = "gamestatus"
    aliases = ["gstatus"]
    locks = "cmd:perm(Builder)"
    
    def func(self):
        from ..game_loop import get_game_status
        self.caller.msg(get_game_status())


class CmdStartGame(Command):
    """
    Start game systems.
    
    Usage:
        startgame
    
    Starts the tick system, NPC spawner, and event scheduler.
    """
    
    key = "startgame"
    locks = "cmd:perm(Admin)"
    
    def func(self):
        from ..game_loop import start_game_systems
        result = start_game_systems()
        self.caller.msg(result)


class CmdStopGame(Command):
    """
    Stop game systems.
    
    Usage:
        stopgame
    
    Stops all game systems.
    """
    
    key = "stopgame"
    locks = "cmd:perm(Admin)"
    
    def func(self):
        from ..game_loop import stop_game_systems
        result = stop_game_systems()
        self.caller.msg(result)


class CmdSpawnNPC(Command):
    """
    Spawn an NPC.
    
    Usage:
        spawnnpc <template>
        spawnnpc/list
        spawnnpc/random
    
    Spawns an NPC in the current location.
    """
    
    key = "spawnnpc"
    locks = "cmd:perm(Builder)"
    
    def func(self):
        from ..world import ALL_NPC_TEMPLATES, generate_npc
        from ..typeclasses import PetSystemsNPC
        
        if "list" in self.switches:
            templates = list(ALL_NPC_TEMPLATES.keys())
            self.caller.msg(f"Available NPCs: {', '.join(templates)}")
            return
        
        if "random" in self.switches:
            template = generate_npc()
        elif self.args:
            template = ALL_NPC_TEMPLATES.get(self.args.strip())
            if not template:
                self.caller.msg("Unknown template. Use spawnnpc/list.")
                return
        else:
            self.caller.msg("Spawn which NPC?")
            return
        
        npc = PetSystemsNPC.create_from_template(template, location=self.caller.location)
        self.caller.msg(f"Spawned {npc.key}.")
        self.caller.location.msg_contents(
            f"{npc.key} appears.",
            exclude=[self.caller]
        )


class CmdCreateRoom(Command):
    """
    Create a room from template.
    
    Usage:
        createroom <template>
        createroom/list
    
    Creates a new room from a location template.
    """
    
    key = "createroom"
    locks = "cmd:perm(Builder)"
    
    def func(self):
        from ..world.locations import ALL_LOCATION_TEMPLATES
        from ..typeclasses import PetSystemsRoom
        
        if "list" in self.switches:
            templates = list(ALL_LOCATION_TEMPLATES.keys())
            self.caller.msg(f"Available rooms: {', '.join(templates)}")
            return
        
        if not self.args:
            self.caller.msg("Create which room?")
            return
        
        template = ALL_LOCATION_TEMPLATES.get(self.args.strip())
        if not template:
            self.caller.msg("Unknown template.")
            return
        
        room = PetSystemsRoom.create_from_template(template)
        self.caller.msg(f"Created room: {room.key} (#{room.dbref})")


class CmdTriggerEvent(Command):
    """
    Trigger an event on a target.
    
    Usage:
        triggerevent <event_id> = <target>
        triggerevent/list
    
    Forces an event to happen to a target.
    """
    
    key = "triggerevent"
    locks = "cmd:perm(Builder)"
    
    def func(self):
        from ..world.events import ALL_EVENT_TEMPLATES, trigger_event
        
        if "list" in self.switches:
            events = list(ALL_EVENT_TEMPLATES.keys())
            self.caller.msg(f"Available events: {', '.join(events)}")
            return
        
        if "=" not in self.args:
            self.caller.msg("Usage: triggerevent <event_id> = <target>")
            return
        
        event_id, target_name = self.args.split("=", 1)
        event_id = event_id.strip()
        target = self.caller.search(target_name.strip())
        
        if not target:
            return
        
        if event_id not in ALL_EVENT_TEMPLATES:
            self.caller.msg("Unknown event.")
            return
        
        msg, _ = trigger_event(event_id, target)
        self.caller.msg(f"Triggered {event_id} on {target.key}:\n{msg}")


class CmdCapture(Command):
    """
    Force capture a target.
    
    Usage:
        capture <target>
        capture <target> = <captor>
    
    Forces a character to be captured.
    """
    
    key = "capture"
    locks = "cmd:perm(Builder)"
    
    def func(self):
        if "=" in self.args:
            target_name, captor_name = self.args.split("=", 1)
            target = self.caller.search(target_name.strip())
            captor = self.caller.search(captor_name.strip())
        else:
            target = self.caller.search(self.args.strip())
            captor = None
        
        if not target:
            return
        
        target.get_captured(captor, "GM action")
        self.caller.msg(f"Captured {target.key}.")


class CmdRelease(Command):
    """
    Release a captured character.
    
    Usage:
        release <target>
    
    Frees a captured character.
    """
    
    key = "release"
    locks = "cmd:perm(Builder)"
    
    def func(self):
        target = self.caller.search(self.args.strip())
        if not target:
            return
        
        target.db.is_captured = False
        target.db.current_owner = None
        self.caller.msg(f"Released {target.key}.")
        target.msg("You have been released.")


# =============================================================================
# SPECIAL "SURPRISE" COMMANDS (for NPCs/events to use)
# =============================================================================

class CmdAmbush(Command):
    """
    Ambush a target (used by NPCs/events).
    
    Usage:
        ambush <target>
    
    Surprise attack with high capture chance.
    """
    
    key = "ambush"
    locks = "cmd:perm(Builder) or npc()"
    
    def func(self):
        target = self.caller.search(self.args.strip())
        if not target:
            return
        
        # Ambush has high capture chance
        capture_chance = 60 + target.vulnerability // 2
        
        if random.randint(1, 100) <= capture_chance:
            target.get_captured(self.caller, "ambushed")
            self.caller.location.msg_contents(
                f"{self.caller.key} ambushes and captures {target.key}!",
                exclude=[self.caller]
            )
        else:
            self.caller.location.msg_contents(
                f"{self.caller.key} tries to ambush {target.key} but fails!",
                exclude=[self.caller]
            )


class CmdForceUse(Command):
    """
    Force use a target (used by NPCs).
    
    Usage:
        forceuse <target>
        forceuse <target> = <amount>
    
    Uses a target regardless of consent.
    """
    
    key = "forceuse"
    locks = "cmd:perm(Builder) or npc()"
    
    def func(self):
        if "=" in self.args:
            target_name, amount_str = self.args.split("=", 1)
            target = self.caller.search(target_name.strip())
            try:
                amount = int(amount_str.strip())
            except ValueError:
                amount = 100
        else:
            target = self.caller.search(self.args.strip())
            amount = random.randint(50, 150)
        
        if not target:
            return
        
        # Apply effects
        if hasattr(target, 'inflation'):
            tracker = target.inflation
            location = random.choice(["womb", "womb", "anal"])
            msg = tracker.inflate(location, "cum", amount)
            target.db.inflation = tracker.to_dict()
            
            self.caller.location.msg_contents(
                f"{self.caller.key} forces {target.key} to take {amount}ml. {msg}"
            )
        
        # Arousal
        if hasattr(target, 'character_state'):
            state = target.character_state
            state.sexual.increase_arousal(random.randint(20, 40))
            target.character_state = state
        
        # Resistance damage
        target.db.current_resistance = max(0, target.db.current_resistance - 5)


# =============================================================================
# CMDSETS
# =============================================================================

class PlayerWorldCmdSet(CmdSet):
    """World commands for players."""
    
    key = "player_world_cmdset"
    
    def at_cmdset_creation(self):
        self.add(CmdStatus())
        self.add(CmdEscape())
        self.add(CmdSubmit())
        self.add(CmdBeg())
        self.add(CmdVulnerability())


class AdminWorldCmdSet(CmdSet):
    """World commands for admins."""
    
    key = "admin_world_cmdset"
    
    def at_cmdset_creation(self):
        self.add(CmdGameStatus())
        self.add(CmdStartGame())
        self.add(CmdStopGame())
        self.add(CmdSpawnNPC())
        self.add(CmdCreateRoom())
        self.add(CmdTriggerEvent())
        self.add(CmdCapture())
        self.add(CmdRelease())
        self.add(CmdAmbush())
        self.add(CmdForceUse())


__all__ = [
    "CmdStatus",
    "CmdEscape",
    "CmdSubmit",
    "CmdBeg",
    "CmdVulnerability",
    "CmdGameStatus",
    "CmdStartGame",
    "CmdStopGame",
    "CmdSpawnNPC",
    "CmdCreateRoom",
    "CmdTriggerEvent",
    "CmdCapture",
    "CmdRelease",
    "CmdAmbush",
    "CmdForceUse",
    "PlayerWorldCmdSet",
    "AdminWorldCmdSet",
]
