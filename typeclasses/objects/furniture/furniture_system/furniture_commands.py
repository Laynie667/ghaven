"""
Furniture Commands
==================

Player-facing commands for interacting with furniture.

Commands:
    sit [on <furniture>]           - Sit on seating furniture
    lie/lay [on <furniture>]       - Lie on beds/surfaces
    stand [against <furniture>]    - Stand against walls/posts
    kneel [at/before <furniture>]  - Kneel at furniture
    
    use <furniture> [slot]         - Generic furniture use
    leave/dismount                 - Leave current furniture
    
    lock <target> [on <furniture>] - Lock someone in restraints
    unlock <target>                - Unlock someone from restraints
    struggle                       - Attempt to escape restraints
    
    power <furniture> <level>      - Set machine power (off/low/med/high/max)
    attach <attachment> to <furn>  - Add attachment to machine
    
    furniture                      - See furniture in room
    fstatus                        - Your furniture status

Examples:
    sit on throne
    lie on bed
    use stocks
    lock Elena on breeding bench
    power sybian high
    struggle
"""

from typing import Optional, Tuple, List, TYPE_CHECKING
from random import choice, randint

# Evennia imports
try:
    from evennia import Command, CmdSet
    from evennia.utils.search import search_object
    if Command is None:
        raise ImportError("Evennia not configured")
    HAS_EVENNIA = True
except (ImportError, Exception):
    HAS_EVENNIA = False
    class Command:
        key = ""
        aliases = []
        locks = ""
        help_category = ""
        args = ""
        caller = None
        def parse(self): pass
        def func(self): pass
    class CmdSet:
        key = ""
        def at_cmdset_creation(self): pass
        def add(self, cmd): pass
    def search_object(*args, **kwargs): return []

# Import furniture system
from typeclasses.objects.furniture import (
    Furniture,
    FurnitureType,
    FurnitureState,
    OccupantPosition,
    Restraint,
    Machine,
    PowerLevel,
    AttachmentType,
)


# =============================================================================
# HELPER FUNCTIONS
# =============================================================================

def find_furniture_by_name(room, name: str) -> Optional[Furniture]:
    """Find furniture in a room by name."""
    name_lower = name.lower()
    for obj in room.contents:
        if isinstance(obj, Furniture):
            if name_lower in obj.key.lower():
                return obj
            # Check aliases
            aliases = getattr(obj.db, "aliases", []) or []
            if any(name_lower in a.lower() for a in aliases):
                return obj
    return None


def find_any_furniture(room, furniture_type: FurnitureType = None) -> Optional[Furniture]:
    """Find any available furniture in room, optionally of specific type."""
    for obj in room.contents:
        if isinstance(obj, Furniture):
            if furniture_type:
                if obj.get_furniture_type() == furniture_type:
                    if obj.is_available():
                        return obj
            else:
                if obj.is_available():
                    return obj
    return None


def get_character_furniture(character) -> Optional[Tuple[Furniture, str]]:
    """Get the furniture a character is currently using."""
    room = character.location
    if not room:
        return None
    
    for obj in room.contents:
        if isinstance(obj, Furniture):
            occupant = obj.get_occupant_by_dbref(character.dbref)
            if occupant:
                return (obj, occupant.slot_key)
    return None


def get_all_room_furniture(room) -> List[Furniture]:
    """Get all furniture in a room."""
    return [obj for obj in room.contents if isinstance(obj, Furniture)]


def format_furniture_status(furniture: Furniture) -> str:
    """Format furniture status for display."""
    lines = []
    lines.append(f"|w{furniture.key}|n ({furniture.get_furniture_type().value})")
    
    state = furniture.db.state
    if state == FurnitureState.BROKEN:
        lines.append("  |rBROKEN|n")
    elif state == FurnitureState.LOCKED:
        lines.append("  |yLocked|n")
    
    # Show occupants
    occupants = furniture.get_occupants()
    if occupants:
        lines.append("  |yOccupied by:|n")
        for occ in occupants:
            locked = " |r[LOCKED]|n" if occ.is_locked else ""
            lines.append(f"    {occ.character_name} ({occ.slot_key}){locked}")
    else:
        slots = furniture.get_available_slots()
        if slots:
            lines.append(f"  |gAvailable slots:|n {', '.join(slots.keys())}")
    
    # Machine info
    if isinstance(furniture, Machine):
        power = furniture.db.power_level
        if power != PowerLevel.OFF:
            lines.append(f"  |cPower:|n {power.value}")
            if furniture.db.power_locked:
                lines.append("  |r[Controls locked]|n")
    
    return "\n".join(lines)


# =============================================================================
# SIT COMMAND
# =============================================================================

class CmdSit(Command):
    """
    Sit on furniture.
    
    Usage:
        sit [on <furniture>]
        sit [<furniture>]
        
    Examples:
        sit                   - Sit on any available seating
        sit on throne         - Sit on the throne
        sit chair             - Sit on a chair
    """
    
    key = "sit"
    locks = "cmd:all()"
    help_category = "Furniture"
    
    def parse(self):
        self.furniture_name = None
        args = self.args.strip()
        
        if args.startswith("on "):
            self.furniture_name = args[3:].strip()
        elif args:
            self.furniture_name = args
    
    def func(self):
        caller = self.caller
        room = caller.location
        
        # Check if already on furniture
        current = get_character_furniture(caller)
        if current:
            furn, slot = current
            caller.msg(f"You're already on the {furn.key}. Use 'leave' first.")
            return
        
        # Find furniture
        if self.furniture_name:
            furniture = find_furniture_by_name(room, self.furniture_name)
            if not furniture:
                caller.msg(f"You don't see '{self.furniture_name}' here.")
                return
        else:
            # Find any seating
            furniture = find_any_furniture(room, FurnitureType.CHAIR)
            if not furniture:
                furniture = find_any_furniture(room, FurnitureType.BENCH)
            if not furniture:
                furniture = find_any_furniture(room, FurnitureType.THRONE)
            if not furniture:
                furniture = find_any_furniture(room, FurnitureType.COUCH)
            
            if not furniture:
                caller.msg("There's nothing to sit on here.")
                return
        
        # Check if it supports sitting
        if not furniture.supports_position(OccupantPosition.SITTING):
            caller.msg(f"You can't sit on the {furniture.key}.")
            return
        
        # Find a sitting slot
        slots = furniture.get_slots()
        sit_slot = None
        for key, slot in slots.items():
            if OccupantPosition.SITTING in slot.positions:
                # Check availability
                avail = furniture.get_available_slots()
                if key in avail:
                    sit_slot = key
                    break
        
        if not sit_slot:
            caller.msg(f"There's no room to sit on the {furniture.key}.")
            return
        
        # Sit!
        success, msg = furniture.use(caller, slot_key=sit_slot, position=OccupantPosition.SITTING)
        
        if success:
            room.msg_contents(f"{caller.key} sits on the {furniture.key}.", exclude=[caller])
            caller.msg(f"You sit on the {furniture.key}.")
        else:
            caller.msg(f"|r{msg}|n")


# =============================================================================
# LIE COMMAND
# =============================================================================

class CmdLie(Command):
    """
    Lie down on furniture.
    
    Usage:
        lie [on <furniture>]
        lay [on <furniture>]
        
    Examples:
        lie on bed
        lay down
    """
    
    key = "lie"
    aliases = ["lay"]
    locks = "cmd:all()"
    help_category = "Furniture"
    
    def parse(self):
        self.furniture_name = None
        args = self.args.strip()
        
        # Handle "lie down" / "lay down"
        if args.lower() in ("down", "back"):
            args = ""
        
        if args.startswith("on "):
            self.furniture_name = args[3:].strip()
        elif args and args.lower() not in ("down", "back"):
            self.furniture_name = args
    
    def func(self):
        caller = self.caller
        room = caller.location
        
        # Check if already on furniture
        current = get_character_furniture(caller)
        if current:
            furn, slot = current
            caller.msg(f"You're already on the {furn.key}. Use 'leave' first.")
            return
        
        # Find furniture
        if self.furniture_name:
            furniture = find_furniture_by_name(room, self.furniture_name)
            if not furniture:
                caller.msg(f"You don't see '{self.furniture_name}' here.")
                return
        else:
            # Find any lying surface
            furniture = find_any_furniture(room, FurnitureType.BED)
            if not furniture:
                furniture = find_any_furniture(room, FurnitureType.COUCH)
            
            if not furniture:
                caller.msg("There's nothing to lie on here.")
                return
        
        # Check if it supports lying
        can_lie = (
            furniture.supports_position(OccupantPosition.LYING_BACK) or
            furniture.supports_position(OccupantPosition.LYING_FRONT) or
            furniture.supports_position(OccupantPosition.LYING_SIDE)
        )
        if not can_lie:
            caller.msg(f"You can't lie on the {furniture.key}.")
            return
        
        # Find a lying slot
        slots = furniture.get_slots()
        lie_slot = None
        lie_pos = OccupantPosition.LYING_BACK
        for key, slot in slots.items():
            for pos in [OccupantPosition.LYING_BACK, OccupantPosition.LYING_FRONT, OccupantPosition.LYING_SIDE]:
                if pos in slot.positions:
                    avail = furniture.get_available_slots()
                    if key in avail:
                        lie_slot = key
                        lie_pos = pos
                        break
            if lie_slot:
                break
        
        if not lie_slot:
            caller.msg(f"There's no room to lie on the {furniture.key}.")
            return
        
        # Lie down!
        success, msg = furniture.use(caller, slot_key=lie_slot, position=lie_pos)
        
        if success:
            room.msg_contents(f"{caller.key} lies down on the {furniture.key}.", exclude=[caller])
            caller.msg(f"You lie down on the {furniture.key}.")
        else:
            caller.msg(f"|r{msg}|n")


# =============================================================================
# STAND COMMAND (against furniture)
# =============================================================================

class CmdStandAgainst(Command):
    """
    Stand against furniture (walls, posts, pillars).
    
    Usage:
        stand against <furniture>
        lean against <furniture>
        
    Examples:
        stand against wall
        lean against pillar
    """
    
    key = "stand"
    aliases = ["lean"]
    locks = "cmd:all()"
    help_category = "Furniture"
    
    def parse(self):
        self.furniture_name = None
        args = self.args.strip()
        
        if args.startswith("against "):
            self.furniture_name = args[8:].strip()
        elif args.startswith("on "):
            self.furniture_name = args[3:].strip()
        elif args:
            self.furniture_name = args
    
    def func(self):
        caller = self.caller
        room = caller.location
        
        if not self.furniture_name:
            # Just standing, not against furniture
            current = get_character_furniture(caller)
            if current:
                furn, slot = current
                # Leave current furniture
                success, msg = furn.release(caller)
                if success:
                    room.msg_contents(f"{caller.key} stands up from the {furn.key}.", exclude=[caller])
                    caller.msg(f"You stand up from the {furn.key}.")
                else:
                    caller.msg(f"|r{msg}|n")
            else:
                caller.msg("You're already standing.")
            return
        
        # Check if already on furniture
        current = get_character_furniture(caller)
        if current:
            furn, slot = current
            caller.msg(f"You're already on the {furn.key}. Use 'leave' first.")
            return
        
        # Find furniture
        furniture = find_furniture_by_name(room, self.furniture_name)
        if not furniture:
            caller.msg(f"You don't see '{self.furniture_name}' here.")
            return
        
        # Check if it supports standing
        if not furniture.supports_position(OccupantPosition.STANDING):
            caller.msg(f"You can't stand against the {furniture.key}.")
            return
        
        # Find a standing slot
        slots = furniture.get_slots()
        stand_slot = None
        for key, slot in slots.items():
            if OccupantPosition.STANDING in slot.positions:
                avail = furniture.get_available_slots()
                if key in avail:
                    stand_slot = key
                    break
        
        if not stand_slot:
            caller.msg(f"There's no room at the {furniture.key}.")
            return
        
        # Stand!
        success, msg = furniture.use(caller, slot_key=stand_slot, position=OccupantPosition.STANDING)
        
        if success:
            room.msg_contents(f"{caller.key} moves to the {furniture.key}.", exclude=[caller])
            caller.msg(f"You stand against the {furniture.key}.")
        else:
            caller.msg(f"|r{msg}|n")


# =============================================================================
# KNEEL COMMAND
# =============================================================================

class CmdKneel(Command):
    """
    Kneel at furniture.
    
    Usage:
        kneel [at/before/by <furniture>]
        
    Examples:
        kneel at throne
        kneel before altar
    """
    
    key = "kneel"
    locks = "cmd:all()"
    help_category = "Furniture"
    
    def parse(self):
        self.furniture_name = None
        args = self.args.strip()
        
        for prefix in ("at ", "before ", "by ", "on "):
            if args.startswith(prefix):
                self.furniture_name = args[len(prefix):].strip()
                return
        
        if args:
            self.furniture_name = args
    
    def func(self):
        caller = self.caller
        room = caller.location
        
        # Check if already on furniture
        current = get_character_furniture(caller)
        if current:
            furn, slot = current
            caller.msg(f"You're already on the {furn.key}. Use 'leave' first.")
            return
        
        if not self.furniture_name:
            caller.msg("Kneel at what?")
            return
        
        # Find furniture
        furniture = find_furniture_by_name(room, self.furniture_name)
        if not furniture:
            caller.msg(f"You don't see '{self.furniture_name}' here.")
            return
        
        # Check if it supports kneeling
        if not furniture.supports_position(OccupantPosition.KNEELING):
            caller.msg(f"You can't kneel at the {furniture.key}.")
            return
        
        # Find a kneeling slot
        slots = furniture.get_slots()
        kneel_slot = None
        for key, slot in slots.items():
            if OccupantPosition.KNEELING in slot.positions:
                avail = furniture.get_available_slots()
                if key in avail:
                    kneel_slot = key
                    break
        
        if not kneel_slot:
            caller.msg(f"There's no room to kneel at the {furniture.key}.")
            return
        
        # Kneel!
        success, msg = furniture.use(caller, slot_key=kneel_slot, position=OccupantPosition.KNEELING)
        
        if success:
            room.msg_contents(f"{caller.key} kneels at the {furniture.key}.", exclude=[caller])
            caller.msg(f"You kneel at the {furniture.key}.")
        else:
            caller.msg(f"|r{msg}|n")


# =============================================================================
# USE COMMAND (generic)
# =============================================================================

class CmdUse(Command):
    """
    Use furniture (generic command for any furniture).
    
    Usage:
        use <furniture> [<slot>]
        
    Examples:
        use bed
        use stocks          - Gets in the stocks yourself (voluntary)
        use sybian
        use breeding bench
    """
    
    key = "use"
    locks = "cmd:all()"
    help_category = "Furniture"
    
    def parse(self):
        self.furniture_name = None
        self.slot = None
        args = self.args.strip()
        
        if not args:
            return
        
        parts = args.rsplit(None, 1)
        self.furniture_name = parts[0]
        
        # Check if last word is a slot name
        if len(parts) > 1:
            # We'll check if it's a valid slot after finding furniture
            self.potential_slot = parts[1]
        else:
            self.potential_slot = None
    
    def func(self):
        caller = self.caller
        room = caller.location
        
        if not self.furniture_name:
            caller.msg("Use what?")
            return
        
        # Check if already on furniture
        current = get_character_furniture(caller)
        if current:
            furn, slot = current
            caller.msg(f"You're already using the {furn.key}. Use 'leave' first.")
            return
        
        # Find furniture
        furniture = find_furniture_by_name(room, self.furniture_name)
        if not furniture:
            # Maybe the "slot" was part of the name
            if self.potential_slot:
                full_name = f"{self.furniture_name} {self.potential_slot}"
                furniture = find_furniture_by_name(room, full_name)
                if furniture:
                    self.potential_slot = None
        
        if not furniture:
            caller.msg(f"You don't see '{self.furniture_name}' here.")
            return
        
        # Check for specified slot
        avail = furniture.get_available_slots()
        if not avail:
            caller.msg(f"The {furniture.key} is fully occupied.")
            return
        
        slot_key = None
        if self.potential_slot and self.potential_slot in avail:
            slot_key = self.potential_slot
        else:
            # Pick first available
            slot_key = list(avail.keys())[0]
        
        slot_def = furniture.get_slots().get(slot_key)
        if not slot_def:
            caller.msg("Error finding slot.")
            return
        
        # Pick appropriate position
        position = list(slot_def.positions)[0]  # First valid position
        
        # Use the furniture
        success, msg = furniture.use(
            caller,
            slot_key=slot_key,
            position=position,
            voluntary=True
        )
        
        if success:
            # Different messages for different furniture types
            ftype = furniture.get_furniture_type()
            if ftype in (FurnitureType.STOCKS, FurnitureType.PILLORY, FurnitureType.CROSS):
                room.msg_contents(f"{caller.key} climbs into the {furniture.key}.", exclude=[caller])
                caller.msg(f"You position yourself in the {furniture.key}.")
            elif ftype == FurnitureType.CAGE:
                room.msg_contents(f"{caller.key} crawls into the {furniture.key}.", exclude=[caller])
                caller.msg(f"You crawl into the {furniture.key}.")
            elif ftype == FurnitureType.SYBIAN:
                room.msg_contents(f"{caller.key} straddles the {furniture.key}.", exclude=[caller])
                caller.msg(f"You mount the {furniture.key}.")
            else:
                room.msg_contents(f"{caller.key} uses the {furniture.key}.", exclude=[caller])
                caller.msg(f"You use the {furniture.key}.")
        else:
            caller.msg(f"|r{msg}|n")


# =============================================================================
# LEAVE COMMAND
# =============================================================================

class CmdLeave(Command):
    """
    Leave/dismount from furniture.
    
    Usage:
        leave
        dismount
        get up
        
    If you're locked in restraints, you'll need to be released or struggle free.
    """
    
    key = "leave"
    aliases = ["dismount", "getup"]
    locks = "cmd:all()"
    help_category = "Furniture"
    
    def func(self):
        caller = self.caller
        room = caller.location
        
        current = get_character_furniture(caller)
        if not current:
            caller.msg("You're not using any furniture.")
            return
        
        furniture, slot = current
        occupant = furniture.get_occupant_by_dbref(caller.dbref)
        
        if occupant and occupant.is_locked:
            caller.msg(f"You're locked in the {furniture.key}! Try 'struggle' or wait to be released.")
            return
        
        # Leave
        success, msg = furniture.release(caller)
        
        if success:
            room.msg_contents(f"{caller.key} gets up from the {furniture.key}.", exclude=[caller])
            caller.msg(f"You leave the {furniture.key}.")
        else:
            caller.msg(f"|r{msg}|n")


# =============================================================================
# LOCK COMMAND (restraints)
# =============================================================================

class CmdLock(Command):
    """
    Lock someone in restraint furniture.
    
    Usage:
        lock <target> [on/in <furniture>]
        
    Examples:
        lock Elena                  - Lock Elena in whatever she's in
        lock Elena on stocks        - Put Elena in stocks and lock
        lock Elena in cage          - Put Elena in cage and lock
        
    The target must be on the furniture already, or you can force them
    onto it (if they're not resisting).
    """
    
    key = "lock"
    locks = "cmd:all()"
    help_category = "Furniture"
    
    def parse(self):
        self.target_name = None
        self.furniture_name = None
        args = self.args.strip()
        
        if not args:
            return
        
        # Split by on/in
        for sep in (" on ", " in ", " into "):
            if sep in args:
                parts = args.split(sep, 1)
                self.target_name = parts[0].strip()
                self.furniture_name = parts[1].strip()
                return
        
        self.target_name = args
    
    def func(self):
        caller = self.caller
        room = caller.location
        
        if not self.target_name:
            caller.msg("Lock who?")
            return
        
        # Find target
        target = caller.search(self.target_name, location=room)
        if not target:
            return
        
        if target == caller:
            caller.msg("You can't lock yourself. Use 'use' and have someone else lock you.")
            return
        
        # Find furniture
        furniture = None
        if self.furniture_name:
            furniture = find_furniture_by_name(room, self.furniture_name)
            if not furniture:
                caller.msg(f"You don't see '{self.furniture_name}' here.")
                return
        else:
            # Check if target is already on something
            current = get_character_furniture(target)
            if current:
                furniture = current[0]
            else:
                # Find any restraint furniture
                for obj in room.contents:
                    if isinstance(obj, Restraint) and obj.is_available():
                        furniture = obj
                        break
        
        if not furniture:
            caller.msg("No restraint furniture available.")
            return
        
        if not isinstance(furniture, Restraint):
            caller.msg(f"The {furniture.key} doesn't have locks.")
            return
        
        # Check if target is already on this furniture
        occupant = furniture.get_occupant_by_dbref(target.dbref)
        
        if not occupant:
            # Need to put them on it first
            # Find a restraint slot
            slots = furniture.get_slots()
            restraint_slot = None
            for key, slot in slots.items():
                if slot.is_restraint:
                    avail = furniture.get_available_slots()
                    if key in avail:
                        restraint_slot = key
                        break
            
            if not restraint_slot:
                caller.msg(f"No restraint slots available on the {furniture.key}.")
                return
            
            slot_def = slots[restraint_slot]
            position = list(slot_def.positions)[0]
            
            # Force them onto it
            success, msg = furniture.use(
                target,
                slot_key=restraint_slot,
                position=position,
                voluntary=False
            )
            
            if not success:
                caller.msg(f"|rFailed: {msg}|n")
                return
            
            room.msg_contents(
                f"{caller.key} forces {target.key} into the {furniture.key}.",
                exclude=[caller, target]
            )
            caller.msg(f"You force {target.key} into the {furniture.key}.")
            target.msg(f"{caller.key} forces you into the {furniture.key}!")
        
        # Now lock them
        success, msg = furniture.lock_occupant(target, lock_dbref=caller.dbref)
        
        if success:
            room.msg_contents(
                f"{caller.key} locks {target.key} in the {furniture.key}.",
                exclude=[caller, target]
            )
            caller.msg(f"You lock {target.key} in the {furniture.key}. They're not going anywhere.")
            target.msg(f"|r{caller.key} locks you in the {furniture.key}!|n You're trapped!")
        else:
            caller.msg(f"|r{msg}|n")


# =============================================================================
# UNLOCK COMMAND
# =============================================================================

class CmdUnlock(Command):
    """
    Unlock someone from restraint furniture.
    
    Usage:
        unlock <target>
        release <target>
        
    Examples:
        unlock Elena
        release Elena
    """
    
    key = "unlock"
    aliases = ["release"]
    locks = "cmd:all()"
    help_category = "Furniture"
    
    def func(self):
        caller = self.caller
        room = caller.location
        args = self.args.strip()
        
        if not args:
            caller.msg("Unlock who?")
            return
        
        # Find target
        target = caller.search(args, location=room)
        if not target:
            return
        
        # Find what they're locked in
        current = get_character_furniture(target)
        if not current:
            caller.msg(f"{target.key} isn't in any furniture.")
            return
        
        furniture, slot = current
        occupant = furniture.get_occupant_by_dbref(target.dbref)
        
        if not occupant or not occupant.is_locked:
            caller.msg(f"{target.key} isn't locked in.")
            return
        
        # Unlock them
        success, msg = furniture.unlock_occupant(target, key_dbref=caller.dbref)
        
        if success:
            room.msg_contents(
                f"{caller.key} unlocks {target.key} from the {furniture.key}.",
                exclude=[caller, target]
            )
            caller.msg(f"You unlock {target.key} from the {furniture.key}.")
            target.msg(f"{caller.key} unlocks you from the {furniture.key}. You can leave now.")
        else:
            caller.msg(f"|r{msg}|n")


# =============================================================================
# STRUGGLE COMMAND
# =============================================================================

STRUGGLE_MESSAGES = {
    "fail": [
        "{name} strains against the {furniture} but can't break free.",
        "{name} struggles helplessly in the {furniture}.",
        "{name} writhes in the {furniture} to no avail.",
        "{name} pulls at the {furniture} but it holds firm.",
        "The {furniture} creaks but holds {name} tight.",
    ],
    "success": [
        "{name} wrenches free from the {furniture}!",
        "{name} manages to slip out of the {furniture}!",
        "With a final heave, {name} breaks free!",
        "{name} escapes from the {furniture}!",
    ],
}


class CmdStruggle(Command):
    """
    Attempt to escape from restraint furniture.
    
    Usage:
        struggle
        escape
        
    Success depends on the furniture type and your strength.
    Some restraints are nearly impossible to escape.
    """
    
    key = "struggle"
    aliases = ["escape"]
    locks = "cmd:all()"
    help_category = "Furniture"
    
    def func(self):
        caller = self.caller
        room = caller.location
        
        current = get_character_furniture(caller)
        if not current:
            caller.msg("You're not restrained.")
            return
        
        furniture, slot = current
        
        if not isinstance(furniture, Restraint):
            caller.msg(f"The {furniture.key} isn't restraining you. Just 'leave'.")
            return
        
        occupant = furniture.get_occupant_by_dbref(caller.dbref)
        if not occupant or not occupant.is_locked:
            caller.msg("You're not locked in. Just 'leave'.")
            return
        
        # Get strength bonus (if body system available)
        strength_bonus = 0
        body = getattr(caller, "body", None)
        if body:
            # Try to get strength from body
            strength_bonus = getattr(body, "strength_modifier", 0)
        
        # Attempt escape
        success, msg = furniture.attempt_escape(caller, strength_bonus)
        
        if success:
            room.msg_contents(
                choice(STRUGGLE_MESSAGES["success"]).format(
                    name=caller.key,
                    furniture=furniture.key
                ),
                exclude=[caller]
            )
            caller.msg(f"|gYou break free from the {furniture.key}!|n")
        else:
            room.msg_contents(
                choice(STRUGGLE_MESSAGES["fail"]).format(
                    name=caller.key,
                    furniture=furniture.key
                ),
                exclude=[caller]
            )
            caller.msg(f"|yYou struggle but can't escape the {furniture.key}.|n")


# =============================================================================
# POWER COMMAND (machines)
# =============================================================================

class CmdPower(Command):
    """
    Control machine power level.
    
    Usage:
        power <furniture> <level>
        power <furniture> up/down
        
    Levels: off, low, medium/med, high, max
    
    Examples:
        power sybian low
        power fucking machine high
        power sybian off
        power machine up
    """
    
    key = "power"
    locks = "cmd:all()"
    help_category = "Furniture"
    
    def parse(self):
        self.furniture_name = None
        self.level = None
        args = self.args.strip()
        
        if not args:
            return
        
        # Last word is level
        parts = args.rsplit(None, 1)
        if len(parts) == 2:
            self.furniture_name = parts[0]
            self.level = parts[1].lower()
        else:
            self.furniture_name = args
    
    def func(self):
        caller = self.caller
        room = caller.location
        
        if not self.furniture_name:
            caller.msg("Usage: power <furniture> <level>")
            return
        
        if not self.level:
            caller.msg("What power level? (off, low, medium, high, max, up, down)")
            return
        
        # Find machine
        furniture = find_furniture_by_name(room, self.furniture_name)
        if not furniture:
            caller.msg(f"You don't see '{self.furniture_name}' here.")
            return
        
        if not isinstance(furniture, Machine):
            caller.msg(f"The {furniture.key} doesn't have power controls.")
            return
        
        # Handle up/down
        if self.level == "up":
            msg = furniture.power_up()
            room.msg_contents(msg)
            return
        elif self.level == "down":
            msg = furniture.power_down()
            room.msg_contents(msg)
            return
        
        # Map level string to enum
        level_map = {
            "off": PowerLevel.OFF,
            "low": PowerLevel.LOW,
            "medium": PowerLevel.MEDIUM,
            "med": PowerLevel.MEDIUM,
            "high": PowerLevel.HIGH,
            "max": PowerLevel.MAX,
            "maximum": PowerLevel.MAX,
        }
        
        level = level_map.get(self.level)
        if not level:
            caller.msg("Invalid level. Use: off, low, medium, high, max")
            return
        
        msg = furniture.set_power(level)
        room.msg_contents(msg)


# =============================================================================
# FURNITURE LIST COMMAND
# =============================================================================

class CmdFurniture(Command):
    """
    List furniture in the current room.
    
    Usage:
        furniture
        furn
    """
    
    key = "furniture"
    aliases = ["furn"]
    locks = "cmd:all()"
    help_category = "Furniture"
    
    def func(self):
        caller = self.caller
        room = caller.location
        
        furniture_list = get_all_room_furniture(room)
        
        if not furniture_list:
            caller.msg("There's no furniture here.")
            return
        
        caller.msg("|wFurniture in this room:|n")
        for furn in furniture_list:
            caller.msg(format_furniture_status(furn))
            caller.msg("")  # Blank line between items


# =============================================================================
# FURNITURE STATUS COMMAND
# =============================================================================

class CmdFurnitureStatus(Command):
    """
    Check your current furniture status.
    
    Usage:
        fstatus
        furnstatus
    """
    
    key = "fstatus"
    aliases = ["furnstatus", "fs"]
    locks = "cmd:all()"
    help_category = "Furniture"
    
    def func(self):
        caller = self.caller
        
        current = get_character_furniture(caller)
        if not current:
            caller.msg("You're not using any furniture.")
            return
        
        furniture, slot_key = current
        occupant = furniture.get_occupant_by_dbref(caller.dbref)
        slot_def = furniture.get_slots().get(slot_key)
        
        caller.msg(f"|wFurniture:|n {furniture.key}")
        caller.msg(f"|wType:|n {furniture.get_furniture_type().value}")
        caller.msg(f"|wSlot:|n {slot_key}")
        
        if occupant:
            caller.msg(f"|wPosition:|n {occupant.position.value}")
            if occupant.is_locked:
                caller.msg("|r[LOCKED]|n - You cannot leave voluntarily")
            else:
                caller.msg("|g[UNLOCKED]|n - You can leave freely")
        
        if slot_def:
            if slot_def.exposed_zones:
                zones = ", ".join(sorted(slot_def.exposed_zones))
                caller.msg(f"|yExposed:|n {zones}")
            if slot_def.blocked_zones:
                zones = ", ".join(sorted(slot_def.blocked_zones))
                caller.msg(f"|yBlocked:|n {zones}")
        
        # Machine info
        if isinstance(furniture, Machine):
            power = furniture.db.power_level
            caller.msg(f"|cPower level:|n {power.value}")
            if furniture.db.power_locked:
                caller.msg("|r[Controls locked - you can't change power]|n")


# =============================================================================
# CMDSET
# =============================================================================

class FurnitureCmdSet(CmdSet):
    """Commands for furniture interaction."""
    
    key = "furniture_cmdset"
    
    def at_cmdset_creation(self):
        self.add(CmdSit())
        self.add(CmdLie())
        self.add(CmdStandAgainst())
        self.add(CmdKneel())
        self.add(CmdUse())
        self.add(CmdLeave())
        self.add(CmdLock())
        self.add(CmdUnlock())
        self.add(CmdStruggle())
        self.add(CmdPower())
        self.add(CmdFurniture())
        self.add(CmdFurnitureStatus())
