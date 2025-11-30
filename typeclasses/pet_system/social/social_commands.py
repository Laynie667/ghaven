"""
Social Commands
===============

Commands for relationships and social systems:
- Relationship management
- Reputation viewing
- Harem management
"""

from evennia import Command, CmdSet

from .relationships import (
    RelationshipType, RelationshipStatus, RelationshipManager, Harem
)


class CmdRelationships(Command):
    """
    View your relationships.
    
    Usage:
      relationships
      relationships <character>
    """
    
    key = "relationships"
    aliases = ["rels", "relations"]
    locks = "cmd:all()"
    
    def func(self):
        if not hasattr(self.caller, 'relationships'):
            self.caller.msg("You don't have any relationships tracked.")
            return
        
        if self.args:
            # View specific relationship
            target = self.caller.search(self.args.strip())
            if not target:
                return
            
            rel = self.caller.get_relationship_with(target.dbref)
            if not rel:
                self.caller.msg(f"You have no relationship with {target.key}.")
                return
            
            self.caller.msg(rel.get_summary(self.caller.dbref))
            return
        
        # View all relationships
        rels = self.caller.relationships
        
        if not rels:
            self.caller.msg("You have no relationships.")
            return
        
        lines = ["=== Your Relationships ==="]
        
        for rel in rels.values():
            if rel.status == RelationshipStatus.ACTIVE:
                other_dbref, other_name = rel.get_other_party(self.caller.dbref)
                affection = rel.get_affection(self.caller.dbref)
                lines.append(f"  {other_name}: {rel.relationship_type.value} (Affection: {affection})")
        
        self.caller.msg("\n".join(lines))


class CmdReputation(Command):
    """
    View your reputation with factions.
    
    Usage:
      reputation
      reputation <faction>
    """
    
    key = "reputation"
    aliases = ["rep", "standing"]
    locks = "cmd:all()"
    
    def func(self):
        if not hasattr(self.caller, 'faction_reputations'):
            self.caller.msg("No faction reputations tracked.")
            return
        
        reps = self.caller.faction_reputations
        
        if not reps:
            self.caller.msg("You have no faction reputations.")
            return
        
        lines = ["=== Faction Reputation ==="]
        
        for faction_id, rep in reps.items():
            level = rep.get_level()
            lines.append(f"  {rep.faction_name}: {rep.reputation} ({level.value})")
        
        self.caller.msg("\n".join(lines))


class CmdHarem(Command):
    """
    Manage your harem.
    
    Usage:
      harem                     - View harem
      harem create <name>       - Create a harem
      harem add <character>     - Add to harem
      harem remove <character>  - Remove from harem
      harem rank <char> <rank>  - Set member rank
      harem favor <char> <+/->  - Modify favor
    """
    
    key = "harem"
    locks = "cmd:all()"
    
    def func(self):
        args = self.args.strip().split() if self.args else []
        
        if not args:
            # View harem
            if not hasattr(self.caller, 'harem'):
                self.caller.msg("You don't have a harem.")
                return
            
            harem = self.caller.harem
            if not harem:
                self.caller.msg("You don't have a harem. Use 'harem create <name>' to create one.")
                return
            
            self.caller.msg(harem.get_display())
            return
        
        cmd = args[0].lower()
        
        if cmd == "create":
            if len(args) < 2:
                name = "Harem"
            else:
                name = " ".join(args[1:])
            
            harem = self.caller.create_harem(name)
            self.caller.msg(f"Created harem: {name}")
            return
        
        # All other commands require existing harem
        if not hasattr(self.caller, 'harem') or not self.caller.harem:
            self.caller.msg("You don't have a harem.")
            return
        
        harem = self.caller.harem
        
        if cmd == "add":
            if len(args) < 2:
                self.caller.msg("Add who?")
                return
            
            target = self.caller.search(" ".join(args[1:]))
            if not target:
                return
            
            success, msg = harem.add_member(target.dbref, target.key)
            self.caller.harem = harem
            self.caller.msg(msg)
            
            if success:
                target.msg(f"You have been added to {self.caller.key}'s harem.")
            return
        
        elif cmd == "remove":
            if len(args) < 2:
                self.caller.msg("Remove who?")
                return
            
            target_name = " ".join(args[1:])
            
            # Find member
            member = None
            for m in harem.members:
                if m.member_name.lower() == target_name.lower():
                    member = m
                    break
            
            if not member:
                self.caller.msg(f"{target_name} is not in your harem.")
                return
            
            success, msg = harem.remove_member(member.member_dbref)
            self.caller.harem = harem
            self.caller.msg(msg)
            return
        
        elif cmd == "rank":
            if len(args) < 3:
                self.caller.msg("Usage: harem rank <character> <rank>")
                return
            
            target_name = args[1]
            try:
                new_rank = int(args[2])
            except ValueError:
                self.caller.msg("Rank must be a number.")
                return
            
            # Find member
            member = None
            for m in harem.members:
                if m.member_name.lower() == target_name.lower():
                    member = m
                    break
            
            if not member:
                self.caller.msg(f"{target_name} is not in your harem.")
                return
            
            msg = harem.set_rank(member.member_dbref, new_rank)
            self.caller.harem = harem
            self.caller.msg(msg)
            return
        
        elif cmd == "favor":
            if len(args) < 3:
                self.caller.msg("Usage: harem favor <character> <+/-amount>")
                return
            
            target_name = args[1]
            try:
                amount = int(args[2])
            except ValueError:
                self.caller.msg("Amount must be a number (e.g., +10 or -5).")
                return
            
            # Find member
            member = None
            for m in harem.members:
                if m.member_name.lower() == target_name.lower():
                    member = m
                    break
            
            if not member:
                self.caller.msg(f"{target_name} is not in your harem.")
                return
            
            msg = harem.modify_favor(member.member_dbref, amount)
            self.caller.harem = harem
            self.caller.msg(msg)
            return
        
        else:
            self.caller.msg("Unknown harem command.")


class CmdPropose(Command):
    """
    Propose a relationship to someone.
    
    Usage:
      propose <type> to <character>
    
    Types: friend, lover, partner, mate
    
    Examples:
      propose friend to Luna
      propose lover to Rex
    """
    
    key = "propose"
    locks = "cmd:all()"
    
    def func(self):
        if not self.args or " to " not in self.args.lower():
            self.caller.msg("Usage: propose <type> to <character>")
            return
        
        parts = self.args.lower().split(" to ")
        if len(parts) != 2:
            self.caller.msg("Usage: propose <type> to <character>")
            return
        
        rel_type_str = parts[0].strip()
        target_name = parts[1].strip()
        
        # Map type string to enum
        type_map = {
            "friend": RelationshipType.FRIEND,
            "close_friend": RelationshipType.CLOSE_FRIEND,
            "lover": RelationshipType.LOVER,
            "partner": RelationshipType.PARTNER,
            "mate": RelationshipType.MATE,
        }
        
        rel_type = type_map.get(rel_type_str)
        if not rel_type:
            valid = ", ".join(type_map.keys())
            self.caller.msg(f"Invalid relationship type. Valid types: {valid}")
            return
        
        target = self.caller.search(target_name)
        if not target:
            return
        
        # Check for existing relationship
        existing = self.caller.get_relationship_with(target.dbref)
        if existing:
            self.caller.msg(f"You already have a relationship with {target.key}.")
            return
        
        # Create the relationship
        rel = RelationshipManager.create_relationship(
            self.caller, target, rel_type
        )
        
        self.caller.save_relationship(rel)
        if hasattr(target, 'save_relationship'):
            target.save_relationship(rel)
        
        self.caller.msg(f"You are now {rel_type.value}s with {target.key}!")
        target.msg(f"{self.caller.key} has become your {rel_type.value}!")


class SocialCmdSet(CmdSet):
    """Commands for social systems."""
    
    key = "SocialCmdSet"
    
    def at_cmdset_creation(self):
        self.add(CmdRelationships())
        self.add(CmdReputation())
        self.add(CmdHarem())
        self.add(CmdPropose())
