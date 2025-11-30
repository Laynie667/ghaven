"""
Sexual Action Commands
======================

Natural-feeling sexual interaction with:
- Automatic orgasms when arousal peaks
- Rhythm system for sustained action
- Varied, non-repetitive output
- Intelligent position awareness
"""

from random import choice, uniform, random
from typing import Optional, Any, Dict, List

# Evennia imports
try:
    from evennia import Command, CmdSet
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

from typeclasses.positions import (
    PositionManager,
    check_part_access,
    BodyZone,
)


# =============================================================================
# Message Variety
# =============================================================================

THRUST_MESSAGES = {
    "gentle": [
        "{actor} rocks slowly into {target}.",
        "{actor} moves with gentle, rolling thrusts.",
        "{actor} eases in and out, savoring every moment.",
        "{actor} takes {target} with deliberate slowness.",
        "{actor} maintains a tender rhythm.",
    ],
    "steady": [
        "{actor} finds a steady rhythm with {target}.",
        "{actor} thrusts with measured pace.",
        "{actor} keeps up a consistent tempo.",
        "{actor} moves steadily, building momentum.",
        "{actor} settles into a satisfying rhythm.",
    ],
    "hard": [
        "{actor} drives hard into {target}.",
        "{actor} pounds {target} with increasing urgency.",
        "{actor} slams forward, gripping {target} tight.",
        "{actor} takes {target} roughly, breath quickening.",
        "{actor} thrusts with forceful intensity.",
    ],
    "desperate": [
        "{actor} ruts frantically into {target}.",
        "{actor} loses control, pounding desperately.",
        "{actor} slams into {target} with wild abandon.",
        "{actor} can barely contain the building pressure.",
        "{actor} drives deep, chasing release.",
    ],
}

AROUSAL_REACTIONS = {
    "low": [  # 0.3-0.5
        "{name} lets out a soft sound of pleasure.",
        "{name}'s breath catches.",
        "{name} shifts into the sensation.",
        "A quiet moan escapes {name}.",
    ],
    "medium": [  # 0.5-0.7
        "{name} moans appreciatively.",
        "{name}'s hips rock in response.",
        "{name} gasps, clearly enjoying this.",
        "{name} grips tighter, wanting more.",
    ],
    "high": [  # 0.7-0.85
        "{name} moans loudly, getting close.",
        "{name} trembles, breath ragged.",
        "{name}'s whole body tenses with pleasure.",
        "{name} whimpers, on the edge.",
    ],
    "peak": [  # 0.85-0.95
        "{name} cries out, right on the brink.",
        "{name} shudders, barely holding back.",
        "{name} gasps desperately, so close...",
        "{name} is seconds away from release.",
    ],
}

ORGASM_MESSAGES = {
    "actor_in": [
        "{actor} buries deep and cums hard inside {target}.",
        "{actor} hilts completely, pulsing release into {target}.",
        "{actor} groans as orgasm crashes through, filling {target}.",
        "{actor} drives deep one final time, pumping {target} full.",
        "{actor} shudders violently, spilling inside {target}.",
    ],
    "actor_on": [
        "{actor} pulls out and cums across {target}.",
        "{actor} strokes frantically, spraying {target}.",
        "{actor} paints {target} with hot release.",
    ],
    "target": [
        "{target} cries out as orgasm overwhelms them.",
        "{target} clenches tight, cumming hard.",
        "{target} shakes through an intense climax.",
        "{target} arches back, lost in release.",
        "{target}'s whole body spasms with pleasure.",
    ],
    "mutual": [
        "{actor} and {target} cum together, lost in each other.",
        "They peak at the same moment, moaning in unison.",
        "Orgasm crashes through them both simultaneously.",
    ],
}

ORAL_MESSAGES = {
    "giving": [
        "{actor} takes {target}'s {part} into their mouth.",
        "{actor} wraps lips around {target}'s {part}.",
        "{actor} works {target}'s {part} with eager tongue.",
        "{actor} bobs steadily on {target}'s {part}.",
        "{actor} swirls tongue around {target}'s {part}.",
    ],
    "receiving_react": [
        "{target} groans at the wet heat.",
        "{target} tangles fingers in {actor}'s hair.",
        "{target}'s hips twitch involuntarily.",
        "{target} gasps as {actor}'s tongue finds the right spot.",
    ],
}


# =============================================================================
# Core Functions
# =============================================================================

def get_room_manager(location) -> Optional[PositionManager]:
    """Get position manager for a room."""
    if not location:
        return None
    manager = getattr(location, "_position_manager", None)
    if manager is None:
        manager = PositionManager()
        location._position_manager = manager
    return manager


def get_arousal(char) -> float:
    """Get character's arousal (0.0-1.0)."""
    if hasattr(char, "db") and hasattr(char.db, "arousal"):
        return char.db.arousal or 0.0
    return getattr(char, "arousal", 0.0)


def set_arousal(char, value: float):
    """Set arousal, clamped 0-1."""
    value = max(0.0, min(1.0, value))
    if hasattr(char, "db"):
        char.db.arousal = value
    else:
        char.arousal = value


def modify_arousal(char, delta: float) -> float:
    """Modify arousal, return new value."""
    new_val = max(0.0, min(1.0, get_arousal(char) + delta))
    set_arousal(char, new_val)
    return new_val


def is_refractory(char) -> bool:
    """Check if in post-orgasm refractory period."""
    if hasattr(char, "db"):
        return getattr(char.db, "refractory", False)
    return getattr(char, "refractory", False)


def set_refractory(char, value: bool):
    """Set refractory state."""
    if hasattr(char, "db"):
        char.db.refractory = value
    else:
        char.refractory = value


def get_rhythm(char) -> Optional[Dict]:
    """Get active rhythm settings."""
    if hasattr(char, "db"):
        return getattr(char.db, "rhythm", None)
    return getattr(char, "rhythm", None)


def set_rhythm(char, rhythm: Optional[Dict]):
    """Set rhythm settings."""
    if hasattr(char, "db"):
        char.db.rhythm = rhythm
    else:
        char.rhythm = rhythm


def get_position_partner(char) -> Optional[Any]:
    """Get primary partner in current position."""
    location = getattr(char, "location", None)
    manager = get_room_manager(location)
    if not manager:
        return None
    
    active = manager.get_position_for(char)
    if not active:
        return None
    
    for slot_key, occupant in active.occupants.items():
        if occupant.character != char:
            return occupant.character
    return None


def check_orgasm(char, partner=None, location=None, cum_inside=True) -> Optional[str]:
    """
    Check if character should orgasm. Returns message if they do.
    
    Auto-triggers at arousal >= 1.0
    """
    arousal = get_arousal(char)
    
    if arousal < 1.0:
        return None
    
    if is_refractory(char):
        return None
    
    # ORGASM!
    char_name = getattr(char, "key", "Someone")
    
    if partner:
        partner_name = getattr(partner, "key", "someone")
        
        # Check if mutual orgasm
        partner_arousal = get_arousal(partner)
        if partner_arousal >= 0.95 and random() < 0.4:
            # Mutual!
            msg = choice(ORGASM_MESSAGES["mutual"]).format(
                actor=char_name, target=partner_name
            )
            # Both reset
            set_arousal(char, 0.1)
            set_arousal(partner, 0.1)
            set_refractory(char, True)
            set_refractory(partner, True)
            return msg
        
        if cum_inside:
            msg = choice(ORGASM_MESSAGES["actor_in"]).format(
                actor=char_name, target=partner_name
            )
        else:
            msg = choice(ORGASM_MESSAGES["actor_on"]).format(
                actor=char_name, target=partner_name
            )
    else:
        msg = f"{char_name} cums hard, shuddering with release."
    
    set_arousal(char, 0.1)
    set_refractory(char, True)
    
    return msg


def get_arousal_reaction(char) -> Optional[str]:
    """Get appropriate reaction message based on arousal level."""
    arousal = get_arousal(char)
    name = getattr(char, "key", "Someone")
    
    # Only show reactions sometimes to avoid spam
    if random() > 0.4:
        return None
    
    if arousal < 0.3:
        return None
    elif arousal < 0.5:
        return choice(AROUSAL_REACTIONS["low"]).format(name=name)
    elif arousal < 0.7:
        return choice(AROUSAL_REACTIONS["medium"]).format(name=name)
    elif arousal < 0.85:
        return choice(AROUSAL_REACTIONS["high"]).format(name=name)
    else:
        return choice(AROUSAL_REACTIONS["peak"]).format(name=name)


def intensity_to_category(intensity: float) -> str:
    """Map 0-1 intensity to message category."""
    if intensity < 0.35:
        return "gentle"
    elif intensity < 0.6:
        return "steady"
    elif intensity < 0.85:
        return "hard"
    else:
        return "desperate"


# =============================================================================
# Commands
# =============================================================================

class CmdThrust(Command):
    """
    Thrust while in a penetrative position.
    
    Usage:
        thrust [intensity] [= flavor]
        thrust hard
        thrust gentle = teasing her
        
    Intensity: gentle, slow, steady, hard, rough, fast, brutal
    Or just use the command repeatedly - intensity auto-adjusts based on arousal.
    
    Must be in a position that allows thrusting.
    """
    
    key = "thrust"
    aliases = ["pump", "pound", "rut"]
    locks = "cmd:all()"
    help_category = "Intimate"
    
    INTENSITY_WORDS = {
        "gentle": 0.25, "slow": 0.3, "soft": 0.25,
        "steady": 0.5, "moderate": 0.5,
        "hard": 0.7, "fast": 0.7, "rough": 0.75,
        "brutal": 0.9, "relentless": 0.85, "desperate": 0.95,
    }
    
    def parse(self):
        self.intensity = None
        self.flavor = ""
        
        args = self.args.strip()
        
        if "=" in args:
            args, self.flavor = args.split("=", 1)
            self.flavor = self.flavor.strip()
            args = args.strip()
        
        # Check for intensity word
        for word, val in self.INTENSITY_WORDS.items():
            if word in args.lower():
                self.intensity = val
                break
    
    def func(self):
        caller = self.caller
        location = caller.location
        
        manager = get_room_manager(location)
        active = manager.get_position_for(caller) if manager else None
        
        if not active:
            caller.msg("You're not in a position.")
            return
        
        if not active.can_participant_thrust(caller):
            caller.msg("You can't thrust from your current position.")
            return
        
        target = get_position_partner(caller)
        if not target:
            caller.msg("No one to thrust into.")
            return
        
        # Auto-calculate intensity based on arousal if not specified
        if self.intensity is None:
            arousal = get_arousal(caller)
            # Higher arousal = harder thrusting naturally
            self.intensity = 0.3 + (arousal * 0.5) + (random() * 0.2)
        
        # Apply arousal changes
        actor_gain = 0.08 + (self.intensity * 0.12)
        target_gain = 0.06 + (self.intensity * 0.1)
        
        # Randomize slightly
        actor_gain *= (0.8 + random() * 0.4)
        target_gain *= (0.8 + random() * 0.4)
        
        new_actor = modify_arousal(caller, actor_gain)
        new_target = modify_arousal(target, target_gain)
        
        # Build message
        actor_name = caller.key
        target_name = target.key
        
        category = intensity_to_category(self.intensity)
        msg = choice(THRUST_MESSAGES[category]).format(
            actor=actor_name, target=target_name
        )
        
        if self.flavor:
            msg = msg.rstrip(".") + f", {self.flavor}."
        
        # Add reactions
        parts = [msg]
        
        reaction = get_arousal_reaction(target)
        if reaction:
            parts.append(reaction)
        
        # Check for orgasms
        actor_cum = check_orgasm(caller, target, location)
        if actor_cum:
            parts.append(actor_cum)
        else:
            target_cum = check_orgasm(target, caller, location, cum_inside=False)
            if target_cum:
                parts.append(target_cum)
        
        location.msg_contents(" ".join(parts))


class CmdRhythm(Command):
    """
    Set an automatic rhythm for sustained action.
    
    Usage:
        rhythm <pace>
        rhythm stop
        rhythm
        
    Paces: slow, steady, fast, brutal
    
    Once set, your character will automatically thrust at the set pace
    every few seconds until you stop or cum.
    
    Examples:
        rhythm steady    - Maintain a steady pace
        rhythm fast      - Pick up the tempo
        rhythm stop      - Stop and catch your breath
    """
    
    key = "rhythm"
    aliases = ["pace", "tempo"]
    locks = "cmd:all()"
    help_category = "Intimate"
    
    PACES = {
        "slow": {"intensity": 0.3, "interval": 8},
        "gentle": {"intensity": 0.25, "interval": 10},
        "steady": {"intensity": 0.5, "interval": 5},
        "fast": {"intensity": 0.7, "interval": 3},
        "hard": {"intensity": 0.75, "interval": 4},
        "brutal": {"intensity": 0.9, "interval": 2},
    }
    
    def func(self):
        caller = self.caller
        args = self.args.strip().lower()
        
        # Check current rhythm
        current = get_rhythm(caller)
        
        if not args:
            if current:
                caller.msg(f"Current rhythm: |w{current['pace']}|n")
            else:
                caller.msg("No rhythm set. Use |wrhythm <pace>|n to start.")
            return
        
        if args in ("stop", "off", "none"):
            if current:
                set_rhythm(caller, None)
                caller.location.msg_contents(f"{caller.key} slows to a stop, catching their breath.")
            else:
                caller.msg("No rhythm to stop.")
            return
        
        if args not in self.PACES:
            paces = ", ".join(self.PACES.keys())
            caller.msg(f"Unknown pace. Options: {paces}")
            return
        
        # Check if in position that allows thrusting
        manager = get_room_manager(caller.location)
        active = manager.get_position_for(caller) if manager else None
        
        if not active:
            caller.msg("You need to be in a position first.")
            return
        
        if not active.can_participant_thrust(caller):
            caller.msg("You can't thrust from your current position.")
            return
        
        pace_data = self.PACES[args]
        rhythm = {
            "pace": args,
            "intensity": pace_data["intensity"],
            "interval": pace_data["interval"],
        }
        
        set_rhythm(caller, rhythm)
        
        target = get_position_partner(caller)
        target_name = target.key if target else "their partner"
        
        if args == "slow":
            msg = f"{caller.key} settles into a slow, deliberate rhythm with {target_name}."
        elif args == "steady":
            msg = f"{caller.key} finds a steady, satisfying pace with {target_name}."
        elif args == "fast":
            msg = f"{caller.key} picks up the pace, thrusting faster into {target_name}."
        elif args == "brutal":
            msg = f"{caller.key} loses control, pounding {target_name} with abandon."
        else:
            msg = f"{caller.key} adjusts their rhythm with {target_name}."
        
        caller.location.msg_contents(msg)
        
        # Note: The actual auto-thrusting would be handled by a ticker script
        # that checks for active rhythms and executes thrust logic


class CmdLick(Command):
    """
    Use your mouth on someone.
    
    Usage:
        lick <target> [part]
        lick Elena
        lick Elena pussy
        lick Elena neck
    """
    
    key = "lick"
    aliases = ["taste", "tongue"]
    locks = "cmd:all()"
    help_category = "Intimate"
    
    def func(self):
        caller = self.caller
        args = self.args.strip().split()
        
        if not args:
            caller.msg("Lick whom?")
            return
        
        target = caller.search(args[0], location=caller.location)
        if not target:
            return
        
        part = args[1].lower() if len(args) > 1 else None
        
        # Default part based on what's accessible
        if not part:
            manager = get_room_manager(caller.location)
            active = manager.get_position_for(caller) if manager else None
            
            if active:
                # Check what zones are accessible
                my_slot = active.get_slot_for_character(caller)
                their_slot = active.get_slot_for_character(target)
                if my_slot and their_slot:
                    zones = active.get_accessible_zones(my_slot, their_slot)
                    if BodyZone.GROIN in zones:
                        part = "pussy"  # or cock, would need to check anatomy
                    elif BodyZone.CHEST in zones:
                        part = "nipples"
            
            if not part:
                part = "lips"
        
        # Arousal based on part
        arousal_map = {
            "pussy": 0.15, "clit": 0.2, "cock": 0.18,
            "nipples": 0.08, "neck": 0.05, "lips": 0.06,
            "ass": 0.1, "thighs": 0.05, "ear": 0.04,
        }
        
        gain = arousal_map.get(part, 0.05)
        new_arousal = modify_arousal(target, gain)
        
        actor_name = caller.key
        target_name = target.key
        
        if part in ("pussy", "cock", "clit"):
            msg = choice(ORAL_MESSAGES["giving"]).format(
                actor=actor_name, target=target_name, part=part
            )
            reaction = choice(ORAL_MESSAGES["receiving_react"]).format(
                actor=actor_name, target=target_name
            )
            msg = f"{msg} {reaction}"
        else:
            verbs = ["licks", "traces tongue across", "kisses and licks"]
            msg = f"{actor_name} {choice(verbs)} {target_name}'s {part}."
        
        # Check for orgasm
        cum_msg = check_orgasm(target, caller, caller.location, cum_inside=False)
        if cum_msg:
            msg = f"{msg} {cum_msg}"
        
        caller.location.msg_contents(msg)


class CmdSuck(Command):
    """
    Suck on a body part.
    
    Usage:
        suck <target> [part]
        suck Elena cock
        suck Elena nipple
    """
    
    key = "suck"
    aliases = ["blow"]
    locks = "cmd:all()"
    help_category = "Intimate"
    
    def func(self):
        caller = self.caller
        args = self.args.strip().split()
        
        if not args:
            caller.msg("Suck whom?")
            return
        
        target = caller.search(args[0], location=caller.location)
        if not target:
            return
        
        part = args[1].lower() if len(args) > 1 else "cock"
        
        arousal_map = {
            "cock": 0.18, "clit": 0.2, "nipples": 0.1,
            "nipple": 0.1, "fingers": 0.03, "tongue": 0.05,
        }
        
        gain = arousal_map.get(part, 0.08)
        modify_arousal(target, gain)
        
        actor_name = caller.key
        target_name = target.key
        
        if part == "cock":
            messages = [
                f"{actor_name} takes {target_name}'s cock deep.",
                f"{actor_name} bobs eagerly on {target_name}'s length.",
                f"{actor_name} wraps lips around {target_name}, sucking hard.",
                f"{actor_name} works {target_name}'s cock with skilled mouth.",
            ]
        elif part in ("nipple", "nipples"):
            messages = [
                f"{actor_name} sucks {target_name}'s nipple between their lips.",
                f"{actor_name} teases {target_name}'s nipple with tongue and teeth.",
            ]
        else:
            messages = [f"{actor_name} sucks on {target_name}'s {part}."]
        
        msg = choice(messages)
        
        reaction = get_arousal_reaction(target)
        if reaction:
            msg = f"{msg} {reaction}"
        
        cum_msg = check_orgasm(target, caller, caller.location, cum_inside=False)
        if cum_msg:
            msg = f"{msg} {cum_msg}"
        
        caller.location.msg_contents(msg)


class CmdFinger(Command):
    """
    Finger someone.
    
    Usage:
        finger <target> [part]
        finger Elena
        finger Elena ass
    """
    
    key = "finger"
    locks = "cmd:all()"
    help_category = "Intimate"
    
    def func(self):
        caller = self.caller
        args = self.args.strip().split()
        
        if not args:
            caller.msg("Finger whom?")
            return
        
        target = caller.search(args[0], location=caller.location)
        if not target:
            return
        
        part = args[1].lower() if len(args) > 1 else "pussy"
        
        gain = 0.12 if part == "pussy" else 0.1
        modify_arousal(target, gain)
        
        actor_name = caller.key
        target_name = target.key
        
        messages = [
            f"{actor_name} slides fingers into {target_name}'s {part}.",
            f"{actor_name} works fingers inside {target_name}.",
            f"{actor_name} curls fingers inside {target_name}'s {part}, searching.",
        ]
        
        msg = choice(messages)
        
        reaction = get_arousal_reaction(target)
        if reaction:
            msg = f"{msg} {reaction}"
        
        cum_msg = check_orgasm(target, caller, caller.location)
        if cum_msg:
            msg = f"{msg} {cum_msg}"
        
        caller.location.msg_contents(msg)


class CmdGrope(Command):
    """
    Grope/fondle someone.
    
    Usage:
        grope <target> [part]
        grope Elena breasts
        grope Elena ass
    """
    
    key = "grope"
    aliases = ["fondle", "squeeze", "grab"]
    locks = "cmd:all()"
    help_category = "Intimate"
    
    def func(self):
        caller = self.caller
        args = self.args.strip().split()
        
        if not args:
            caller.msg("Grope whom?")
            return
        
        target = caller.search(args[0], location=caller.location)
        if not target:
            return
        
        part = args[1].lower() if len(args) > 1 else "ass"
        
        arousal_map = {
            "breasts": 0.08, "breast": 0.08, "tits": 0.08,
            "ass": 0.07, "butt": 0.07, "thighs": 0.05,
            "cock": 0.1, "pussy": 0.1, "crotch": 0.09,
        }
        
        gain = arousal_map.get(part, 0.05)
        modify_arousal(target, gain)
        
        verbs = ["gropes", "squeezes", "grabs", "fondles", "kneads"]
        
        caller.location.msg_contents(
            f"{caller.key} {choice(verbs)} {target.key}'s {part}."
        )


class CmdKiss(Command):
    """
    Kiss someone.
    
    Usage:
        kiss <target> [part]
        kiss Elena
        kiss Elena neck
    """
    
    key = "kiss"
    locks = "cmd:all()"
    help_category = "Intimate"
    
    def func(self):
        caller = self.caller
        args = self.args.strip().split()
        
        if not args:
            caller.msg("Kiss whom?")
            return
        
        target = caller.search(args[0], location=caller.location)
        if not target:
            return
        
        part = args[1].lower() if len(args) > 1 else None
        
        arousal_map = {
            None: 0.05, "lips": 0.05, "neck": 0.06,
            "ear": 0.04, "cheek": 0.02, "forehead": 0.01,
        }
        
        gain = arousal_map.get(part, 0.03)
        modify_arousal(target, gain)
        modify_arousal(caller, gain * 0.5)
        
        if part and part != "lips":
            msg = f"{caller.key} kisses {target.key}'s {part}."
        else:
            messages = [
                f"{caller.key} kisses {target.key}.",
                f"{caller.key} presses lips to {target.key}'s.",
                f"{caller.key} captures {target.key}'s lips.",
            ]
            msg = choice(messages)
        
        caller.location.msg_contents(msg)


class CmdCum(Command):
    """
    Force an orgasm (if close enough) or control where you cum.
    
    Usage:
        cum
        cum in <target>
        cum on <target> [part]
        
    Normally orgasms happen automatically when arousal peaks.
    Use this to force it early (requires 70%+ arousal) or to
    control where you finish.
    """
    
    key = "cum"
    aliases = ["orgasm", "climax", "finish"]
    locks = "cmd:all()"
    help_category = "Intimate"
    
    def func(self):
        caller = self.caller
        args = self.args.strip()
        
        arousal = get_arousal(caller)
        
        if arousal < 0.7:
            caller.msg(f"You're not aroused enough. ({arousal:.0%})")
            return
        
        if is_refractory(caller):
            caller.msg("You need a moment to recover.")
            return
        
        target = None
        cum_inside = True
        part = None
        
        if args.startswith("in "):
            target = caller.search(args[3:].strip(), location=caller.location)
            cum_inside = True
        elif args.startswith("on "):
            rest = args[3:].strip().split()
            if rest:
                target = caller.search(rest[0], location=caller.location)
                cum_inside = False
                if len(rest) > 1:
                    part = rest[1]
        elif args:
            target = caller.search(args, location=caller.location)
        else:
            target = get_position_partner(caller)
        
        # Force the orgasm
        set_arousal(caller, 1.0)
        msg = check_orgasm(caller, target, caller.location, cum_inside)
        
        if msg:
            caller.location.msg_contents(msg)
        else:
            caller.location.msg_contents(f"{caller.key} cums hard.")


class CmdArousal(Command):
    """
    Check arousal level.
    
    Usage:
        arousal
        arousal <target>  (if in position with them)
    """
    
    key = "arousal"
    aliases = ["horny", "turned on"]
    locks = "cmd:all()"
    help_category = "Intimate"
    
    def func(self):
        caller = self.caller
        args = self.args.strip()
        
        if args:
            target = caller.search(args, location=caller.location)
            if not target:
                return
            
            # Can check partner's arousal if in same position
            manager = get_room_manager(caller.location)
            if manager:
                my_pos = manager.get_position_for(caller)
                their_pos = manager.get_position_for(target)
                
                if my_pos and my_pos is their_pos:
                    arousal = get_arousal(target)
                    if arousal < 0.3:
                        desc = "hasn't warmed up yet"
                    elif arousal < 0.6:
                        desc = "is getting into it"
                    elif arousal < 0.85:
                        desc = "is really enjoying this"
                    else:
                        desc = "is on the edge"
                    
                    caller.msg(f"{target.key} {desc}.")
                    return
            
            caller.msg("You can only sense a partner's arousal.")
            return
        
        arousal = get_arousal(caller)
        
        if arousal < 0.1:
            desc = "calm"
        elif arousal < 0.3:
            desc = "a little warm"
        elif arousal < 0.5:
            desc = "turned on"
        elif arousal < 0.7:
            desc = "very aroused"
        elif arousal < 0.85:
            desc = "aching for release"
        elif arousal < 0.95:
            desc = "right on the edge"
        else:
            desc = "about to explode"
        
        caller.msg(f"You're feeling {desc}. ({arousal:.0%})")


class SexualCmdSet(CmdSet):
    """Sexual action commands."""
    
    key = "sexual_cmdset"
    
    def at_cmdset_creation(self):
        self.add(CmdThrust())
        self.add(CmdRhythm())
        self.add(CmdLick())
        self.add(CmdSuck())
        self.add(CmdFinger())
        self.add(CmdGrope())
        self.add(CmdKiss())
        self.add(CmdCum())
        self.add(CmdArousal())
