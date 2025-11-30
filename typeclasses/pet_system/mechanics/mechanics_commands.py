"""
Mechanics Commands
==================

Commands for combat and restraint mechanics:
- Grappling
- Rope bondage
- Escape attempts
"""

from evennia import Command, CmdSet

from .grappling import (
    GrappleState, HoldType, GrappleSystem, GrappleInstance, ALL_HOLDS
)
from .rope_bondage import (
    TiePattern, BondagePosition, BondageSystem, Rope, RopeType, ALL_TIES
)


# =============================================================================
# GRAPPLING COMMANDS
# =============================================================================

class CmdGrapple(Command):
    """
    Initiate a grapple with someone.
    
    Usage:
      grapple <target>
    
    Examples:
      grapple Luna
    """
    
    key = "grapple"
    aliases = ["grab", "tackle"]
    locks = "cmd:all()"
    
    def func(self):
        if not self.args:
            self.caller.msg("Grapple who?")
            return
        
        target = self.caller.search(self.args.strip())
        if not target:
            return
        
        if target == self.caller:
            self.caller.msg("You can't grapple yourself.")
            return
        
        # Check if already grappling
        if hasattr(self.caller, 'current_grapple') and self.caller.current_grapple:
            self.caller.msg("You're already in a grapple!")
            return
        
        # Get strength stats
        attacker_str = getattr(self.caller, 'grapple_strength', 50)
        defender_str = getattr(target, 'grapple_strength', 50)
        
        success, message, grapple = GrappleSystem.initiate_grapple(
            self.caller, target, attacker_str, defender_str
        )
        
        self.caller.msg(message)
        target.msg(message)
        self.caller.location.msg_contents(message, exclude=[self.caller, target])
        
        if success and grapple:
            self.caller.current_grapple = grapple
            target.current_grapple = grapple


class CmdHold(Command):
    """
    Apply a hold during a grapple.
    
    Usage:
      hold <type>
    
    Types: wrist_grab, arm_lock, headlock, bear_hug, 
           full_nelson, pin, mount, spread_eagle
    """
    
    key = "hold"
    locks = "cmd:all()"
    
    def func(self):
        if not self.args:
            # List holds
            lines = ["Available holds:"]
            for key, hold in ALL_HOLDS.items():
                lines.append(f"  {key}: {hold.name} (DC {hold.escape_dc})")
            self.caller.msg("\n".join(lines))
            return
        
        if not hasattr(self.caller, 'current_grapple') or not self.caller.current_grapple:
            self.caller.msg("You're not in a grapple.")
            return
        
        grapple = self.caller.current_grapple
        
        # Must be attacker
        if grapple.attacker_dbref != self.caller.dbref:
            self.caller.msg("You're not in control of the grapple.")
            return
        
        hold_key = self.args.strip().lower()
        hold = ALL_HOLDS.get(hold_key)
        
        if not hold:
            self.caller.msg(f"Unknown hold: {hold_key}")
            return
        
        # Check position requirements
        if hold.requires_position and grapple.grapple_state != hold.requires_position:
            self.caller.msg(f"{hold.name} requires {hold.requires_position.value} position.")
            return
        
        message = grapple.apply_hold(hold)
        
        self.caller.current_grapple = grapple
        
        # Update defender
        target = self.caller.search(grapple.defender_dbref)
        if target:
            target.current_grapple = grapple
            target.msg(message)
        
        self.caller.msg(message)
        self.caller.location.msg_contents(message, exclude=[self.caller, target])


class CmdStruggle(Command):
    """
    Struggle to escape a grapple or bondage.
    
    Usage:
      struggle
    """
    
    key = "struggle"
    aliases = ["escape", "resist"]
    locks = "cmd:all()"
    
    def func(self):
        # Check grapple first
        if hasattr(self.caller, 'current_grapple') and self.caller.current_grapple:
            grapple = self.caller.current_grapple
            
            if grapple.defender_dbref != self.caller.dbref:
                self.caller.msg("You're the one doing the grappling!")
                return
            
            strength = getattr(self.caller, 'grapple_strength', 50)
            skill = getattr(self.caller, 'grapple_skill', 50)
            
            result, message = grapple.attempt_escape(strength, skill)
            
            self.caller.msg(message)
            
            # Update both parties
            attacker = self.caller.search(grapple.attacker_dbref)
            
            if result.value == "escape":
                self.caller.current_grapple = None
                if attacker:
                    attacker.current_grapple = None
                    attacker.msg(message)
            else:
                self.caller.current_grapple = grapple
                if attacker:
                    attacker.current_grapple = grapple
                    attacker.msg(message)
            
            return
        
        # Check bondage
        if hasattr(self.caller, 'current_bondage') and self.caller.current_bondage:
            bondage = self.caller.current_bondage
            
            strength = getattr(self.caller, 'grapple_strength', 50)
            skill = getattr(self.caller, 'bondage_skill', 50)
            
            success, message = bondage.attempt_escape(strength, skill)
            
            self.caller.msg(message)
            self.caller.location.msg_contents(message, exclude=[self.caller])
            
            if success:
                self.caller.current_bondage = None
            else:
                self.caller.current_bondage = bondage
            
            return
        
        self.caller.msg("You're not restrained.")


class CmdReleaseGrapple(Command):
    """
    Release someone from a grapple.
    
    Usage:
      release
    """
    
    key = "release"
    locks = "cmd:all()"
    
    def func(self):
        if not hasattr(self.caller, 'current_grapple') or not self.caller.current_grapple:
            # Check if we're the tier in a bondage
            self.caller.msg("You're not restraining anyone.")
            return
        
        grapple = self.caller.current_grapple
        
        if grapple.attacker_dbref != self.caller.dbref:
            self.caller.msg("You're not the one in control.")
            return
        
        message = GrappleSystem.end_grapple(grapple)
        
        self.caller.current_grapple = None
        
        target = self.caller.search(grapple.defender_dbref)
        if target:
            target.current_grapple = None
            target.msg(message)
        
        self.caller.msg(message)
        self.caller.location.msg_contents(message, exclude=[self.caller, target])


# =============================================================================
# BONDAGE COMMANDS
# =============================================================================

class CmdTie(Command):
    """
    Tie someone up with rope.
    
    Usage:
      tie <target>                    - Start tying
      tie <target> <pattern>          - Apply specific tie
      tie <target> <pattern> <position>
    
    Patterns: wrists_front, wrists_back, ankles, hogtie, box_tie,
              spread_eagle, crotch_rope, breast_harness, full_body,
              frogtie, suspension
    
    Positions: standing, kneeling, sitting, lying_face_up,
               lying_face_down, bent_over, suspended
    """
    
    key = "tie"
    aliases = ["bind", "rope"]
    locks = "cmd:all()"
    
    def func(self):
        if not self.args:
            self.caller.msg("Tie who?")
            return
        
        args = self.args.strip().split()
        target_name = args[0]
        pattern_name = args[1] if len(args) > 1 else None
        position_name = args[2] if len(args) > 2 else None
        
        target = self.caller.search(target_name)
        if not target:
            return
        
        if target == self.caller:
            self.caller.msg("You can't tie yourself.")
            return
        
        # Get or create bondage instance
        bondage = None
        if hasattr(target, 'current_bondage'):
            bondage = target.current_bondage
        
        if not bondage:
            # Start new bondage
            rope = Rope(rope_type=RopeType.JUTE)
            success, message, bondage = BondageSystem.start_bondage(
                self.caller, target, rope
            )
            
            if not success:
                self.caller.msg(message)
                return
            
            self.caller.msg(message)
            target.msg(message)
        
        # Apply pattern if specified
        if pattern_name:
            try:
                pattern = TiePattern(pattern_name)
            except ValueError:
                valid = ", ".join([t.value for t in TiePattern])
                self.caller.msg(f"Unknown pattern. Valid: {valid}")
                return
            
            position = None
            if position_name:
                try:
                    position = BondagePosition(position_name)
                except ValueError:
                    valid = ", ".join([p.value for p in BondagePosition])
                    self.caller.msg(f"Unknown position. Valid: {valid}")
                    return
            
            success, message = BondageSystem.apply_tie(bondage, pattern, position)
            
            if not success:
                self.caller.msg(message)
                return
            
            self.caller.msg(message)
            target.msg(message)
            self.caller.location.msg_contents(message, exclude=[self.caller, target])
        
        target.current_bondage = bondage


class CmdUntie(Command):
    """
    Untie someone.
    
    Usage:
      untie <target>
    """
    
    key = "untie"
    aliases = ["unbind", "unrope"]
    locks = "cmd:all()"
    
    def func(self):
        if not self.args:
            self.caller.msg("Untie who?")
            return
        
        target = self.caller.search(self.args.strip())
        if not target:
            return
        
        if not hasattr(target, 'current_bondage') or not target.current_bondage:
            self.caller.msg(f"{target.key} is not tied up.")
            return
        
        bondage = target.current_bondage
        message = BondageSystem.release(bondage)
        
        target.current_bondage = None
        
        self.caller.msg(message)
        target.msg(message)
        self.caller.location.msg_contents(message, exclude=[self.caller, target])


class CmdBondageStatus(Command):
    """
    View bondage status.
    
    Usage:
      bondagestatus
      bondagestatus <target>
    """
    
    key = "bondagestatus"
    aliases = ["bstatus", "ropes"]
    locks = "cmd:all()"
    
    def func(self):
        if self.args:
            target = self.caller.search(self.args.strip())
            if not target:
                return
        else:
            target = self.caller
        
        if not hasattr(target, 'current_bondage') or not target.current_bondage:
            if target == self.caller:
                self.caller.msg("You are not bound.")
            else:
                self.caller.msg(f"{target.key} is not bound.")
            return
        
        bondage = target.current_bondage
        
        lines = [f"=== Bondage Status: {target.key} ==="]
        lines.append(f"Tied by: {bondage.tier_name}")
        lines.append(f"Position: {bondage.position.value}")
        
        if bondage.active_ties:
            lines.append("Active ties:")
            for pattern in bondage.active_ties:
                tie_def = ALL_TIES.get(pattern.value)
                if tie_def:
                    lines.append(f"  - {tie_def.name}")
        
        lines.append(f"Escape DC: {bondage.get_total_escape_dc()}")
        
        if bondage.rope_loosened > 0:
            lines.append(f"Ropes loosened: {bondage.rope_loosened}%")
        
        self.caller.msg("\n".join(lines))


class CmdGrappleStatus(Command):
    """
    View grapple status.
    
    Usage:
      grapplestatus
    """
    
    key = "grapplestatus"
    aliases = ["gstatus"]
    locks = "cmd:all()"
    
    def func(self):
        if not hasattr(self.caller, 'current_grapple') or not self.caller.current_grapple:
            self.caller.msg("You're not in a grapple.")
            return
        
        grapple = self.caller.current_grapple
        self.caller.msg(grapple.get_status())


class MechanicsCmdSet(CmdSet):
    """Commands for combat and restraint."""
    
    key = "MechanicsCmdSet"
    
    def at_cmdset_creation(self):
        # Grappling
        self.add(CmdGrapple())
        self.add(CmdHold())
        self.add(CmdStruggle())
        self.add(CmdReleaseGrapple())
        self.add(CmdGrappleStatus())
        
        # Bondage
        self.add(CmdTie())
        self.add(CmdUntie())
        self.add(CmdBondageStatus())
