"""
Party Commands for Gilderhaven

Commands for forming, managing, and interacting with parties.
"""

from evennia import Command, CmdSet

from world.parties import (
    get_party, is_in_party, is_party_leader,
    get_party_members, get_party_leader,
    create_party, disband_party, leave_party,
    invite_to_party, accept_party_invite, decline_party_invite,
    get_pending_invites, party_chat, party_emote,
    party_recall, sync_party_location,
    PARTY_ROLES, PARTY_FORMATIONS, MAX_PARTY_SIZE,
)


class CmdParty(Command):
    """
    View your party status.
    
    Usage:
        party
        
    Shows your current party, members, and status.
    """
    key = "party"
    aliases = ["group", "team"]
    locks = "cmd:all()"
    
    def func(self):
        caller = self.caller
        party = get_party(caller)
        
        if not party:
            self.caller.msg("You're not in a party.")
            self.caller.msg("Use |wparty invite <player>|n to form a party.")
            return
        
        self.caller.msg(party.get_display(caller))


class CmdPartyInvite(Command):
    """
    Invite a player to your party.
    
    Usage:
        party invite <player>
        invite <player>
        
    Creates a party if you don't have one.
    """
    key = "party invite"
    aliases = ["invite", "pinvite"]
    locks = "cmd:all()"
    
    def func(self):
        caller = self.caller
        
        if not self.args:
            self.caller.msg("Invite who?")
            return
        
        target = caller.search(self.args.strip(), location=caller.location)
        if not target:
            return
        
        if target == caller:
            self.caller.msg("You can't invite yourself.")
            return
        
        if not hasattr(target, "msg"):
            self.caller.msg("You can't invite that.")
            return
        
        success, message = invite_to_party(caller, target)
        self.caller.msg(message)
        
        if success:
            # Notify target
            party = get_party(caller)
            target.msg(
                f"|y{caller.key} has invited you to join their party!|n\n"
                f"Use |wparty accept {caller.key}|n to join, or "
                f"|wparty decline {caller.key}|n to refuse."
            )


class CmdPartyAccept(Command):
    """
    Accept a party invitation.
    
    Usage:
        party accept <leader>
        paccept <leader>
        
    Accepts an invite from the specified player's party.
    """
    key = "party accept"
    aliases = ["paccept", "accept party"]
    locks = "cmd:all()"
    
    def func(self):
        caller = self.caller
        
        if is_in_party(caller):
            self.caller.msg("You're already in a party. Leave first.")
            return
        
        # Find invites
        invites = get_pending_invites(caller)
        
        if not invites and not self.args:
            self.caller.msg("No pending party invitations.")
            return
        
        if not self.args:
            if len(invites) == 1:
                # Accept the only invite
                party = invites[0]
            else:
                self.caller.msg("Multiple invitations. Specify which: party accept <leader>")
                for party in invites:
                    self.caller.msg(f"  - {party.leader.key}")
                return
        else:
            # Find specific party
            leader_name = self.args.strip().lower()
            party = None
            for p in invites:
                if p.leader.key.lower().startswith(leader_name):
                    party = p
                    break
            
            if not party:
                # Maybe search for leader in room
                leader = caller.search(self.args.strip(), location=caller.location)
                if leader:
                    party = get_party(leader)
        
        if not party:
            self.caller.msg("No such party invitation.")
            return
        
        success, message = party.accept_invite(caller)
        
        if success:
            # Announce to party
            party.msg_party(f"|g{caller.key} has joined the party!|n", exclude=[caller])
            self.caller.msg(f"|gYou have joined {party.leader.key}'s party!|n")
            
            # Sync location
            sync_party_location(caller)
        else:
            self.caller.msg(message)


class CmdPartyDecline(Command):
    """
    Decline a party invitation.
    
    Usage:
        party decline <leader>
        pdecline <leader>
    """
    key = "party decline"
    aliases = ["pdecline", "decline party"]
    locks = "cmd:all()"
    
    def func(self):
        caller = self.caller
        
        invites = get_pending_invites(caller)
        
        if not invites:
            self.caller.msg("No pending party invitations.")
            return
        
        if not self.args:
            if len(invites) == 1:
                party = invites[0]
            else:
                self.caller.msg("Multiple invitations. Specify which: party decline <leader>")
                return
        else:
            leader_name = self.args.strip().lower()
            party = None
            for p in invites:
                if p.leader.key.lower().startswith(leader_name):
                    party = p
                    break
        
        if not party:
            self.caller.msg("No such party invitation.")
            return
        
        success, message = party.decline_invite(caller)
        self.caller.msg("Invitation declined.")
        party.leader.msg(f"{caller.key} declined the party invitation.")


class CmdPartyLeave(Command):
    """
    Leave your current party.
    
    Usage:
        party leave
        pleave
    """
    key = "party leave"
    aliases = ["pleave", "leave party"]
    locks = "cmd:all()"
    
    def func(self):
        caller = self.caller
        
        if not is_in_party(caller):
            self.caller.msg("You're not in a party.")
            return
        
        party = get_party(caller)
        
        # Notify party before leaving
        party.msg_party(f"|y{caller.key} is leaving the party.|n", exclude=[caller])
        
        success, message = leave_party(caller)
        self.caller.msg(message)


class CmdPartyKick(Command):
    """
    Kick a member from your party.
    
    Usage:
        party kick <player>
        pkick <player>
        
    Only the party leader can kick members.
    """
    key = "party kick"
    aliases = ["pkick", "kick"]
    locks = "cmd:all()"
    
    def func(self):
        caller = self.caller
        
        if not is_in_party(caller):
            self.caller.msg("You're not in a party.")
            return
        
        party = get_party(caller)
        
        if not self.args:
            self.caller.msg("Kick who?")
            return
        
        target_name = self.args.strip().lower()
        target = None
        for member in party.members:
            if member.key.lower().startswith(target_name):
                target = member
                break
        
        if not target:
            self.caller.msg("That player is not in your party.")
            return
        
        success, message = party.kick_member(caller, target)
        
        if success:
            party.msg_party(f"|y{target.key} has been kicked from the party.|n")
            target.msg(f"|yYou have been kicked from the party by {caller.key}.|n")
        else:
            self.caller.msg(message)


class CmdPartyDisband(Command):
    """
    Disband your party.
    
    Usage:
        party disband
        pdisband
        
    Only the party leader can disband.
    """
    key = "party disband"
    aliases = ["pdisband", "disband party"]
    locks = "cmd:all()"
    
    def func(self):
        caller = self.caller
        
        if not is_party_leader(caller):
            self.caller.msg("Only the party leader can disband the party.")
            return
        
        success, message = disband_party(caller)
        self.caller.msg(message)


class CmdPartyPromote(Command):
    """
    Promote a party member or transfer leadership.
    
    Usage:
        party promote <player>
        party promote <player> officer
        party promote <player> leader
        
    Promoting to leader transfers party control.
    """
    key = "party promote"
    aliases = ["ppromote"]
    locks = "cmd:all()"
    
    def func(self):
        caller = self.caller
        
        if not is_party_leader(caller):
            self.caller.msg("Only the party leader can promote members.")
            return
        
        party = get_party(caller)
        
        args = self.args.split()
        if not args:
            self.caller.msg("Promote who?")
            return
        
        target_name = args[0].lower()
        new_role = args[1].lower() if len(args) > 1 else "officer"
        
        target = None
        for member in party.members:
            if member.key.lower().startswith(target_name):
                target = member
                break
        
        if not target:
            self.caller.msg("That player is not in your party.")
            return
        
        if new_role == "leader":
            success, message = party.transfer_leadership(target)
        else:
            success, message = party.promote(target, new_role)
        
        if success:
            party.msg_party(f"|c{message}|n")
        else:
            self.caller.msg(message)


class CmdPartyFormation(Command):
    """
    Set party combat formation.
    
    Usage:
        party formation
        party formation <formation>
        
    Formations:
        standard   - Balanced (60% front)
        aggressive - All front (+10% damage)
        defensive  - More back (+15% defense)
        scattered  - Spread out (AoE reduction)
    """
    key = "party formation"
    aliases = ["pformation", "formation"]
    locks = "cmd:all()"
    
    def func(self):
        caller = self.caller
        
        if not is_in_party(caller):
            self.caller.msg("You're not in a party.")
            return
        
        party = get_party(caller)
        
        if not self.args:
            # Show current and options
            current = PARTY_FORMATIONS.get(party.formation, {})
            lines = [f"|wCurrent formation: |c{current.get('name', 'Unknown')}|n"]
            lines.append(f"  {current.get('desc', '')}")
            lines.append("")
            lines.append("|wAvailable formations:|n")
            for key, data in PARTY_FORMATIONS.items():
                lines.append(f"  |w{key}|n - {data['desc']}")
            self.caller.msg("\n".join(lines))
            return
        
        if not is_party_leader(caller):
            self.caller.msg("Only the party leader can change formation.")
            return
        
        formation_key = self.args.strip().lower()
        success, message = party.set_formation(formation_key)
        
        if success:
            party.msg_party(f"|c{caller.key} changed formation to {formation_key}.|n")
        else:
            self.caller.msg(message)


class CmdPartyLoot(Command):
    """
    Set party loot distribution mode.
    
    Usage:
        party loot
        party loot <mode>
        
    Modes:
        ffa         - Free for all (leader gets)
        round_robin - Rotates through members
        leader      - Leader distributes manually
    """
    key = "party loot"
    aliases = ["ploot"]
    locks = "cmd:all()"
    
    def func(self):
        caller = self.caller
        
        if not is_in_party(caller):
            self.caller.msg("You're not in a party.")
            return
        
        party = get_party(caller)
        
        if not self.args:
            self.caller.msg(f"Current loot mode: |c{party.loot_mode}|n")
            self.caller.msg("Options: ffa, round_robin, leader")
            return
        
        if not is_party_leader(caller):
            self.caller.msg("Only the party leader can change loot mode.")
            return
        
        mode = self.args.strip().lower()
        success, message = party.set_loot_mode(mode)
        
        if success:
            party.msg_party(f"|c{caller.key} changed loot mode to {mode}.|n")
        else:
            self.caller.msg(message)


class CmdPartyChat(Command):
    """
    Send a message to your party.
    
    Usage:
        party say <message>
        psay <message>
        p <message>
    """
    key = "party say"
    aliases = ["psay", "p"]
    locks = "cmd:all()"
    
    def func(self):
        caller = self.caller
        
        if not is_in_party(caller):
            self.caller.msg("You're not in a party.")
            return
        
        if not self.args:
            self.caller.msg("Say what?")
            return
        
        party_chat(caller, self.args.strip())


class CmdPartyEmote(Command):
    """
    Send an emote to your party.
    
    Usage:
        party emote <action>
        pemote <action>
    """
    key = "party emote"
    aliases = ["pemote"]
    locks = "cmd:all()"
    
    def func(self):
        caller = self.caller
        
        if not is_in_party(caller):
            self.caller.msg("You're not in a party.")
            return
        
        if not self.args:
            self.caller.msg("Emote what?")
            return
        
        party_emote(caller, self.args.strip())


class CmdPartyRecall(Command):
    """
    Teleport all party members to your location.
    
    Usage:
        party recall
        precall
        
    Only the party leader can recall members.
    """
    key = "party recall"
    aliases = ["precall"]
    locks = "cmd:all()"
    
    def func(self):
        caller = self.caller
        
        if not is_party_leader(caller):
            self.caller.msg("Only the party leader can recall the party.")
            return
        
        success, message = party_recall(caller)
        self.caller.msg(message)
        
        if success:
            party = get_party(caller)
            party.msg_party(
                f"|y{caller.key} has recalled the party to their location.|n",
                exclude=[caller]
            )


class CmdPartyFollow(Command):
    """
    Follow your party leader (sync location).
    
    Usage:
        party follow
        follow
        
    Teleports you to the party leader's location.
    """
    key = "party follow"
    aliases = ["follow", "pfollow"]
    locks = "cmd:all()"
    
    def func(self):
        caller = self.caller
        
        if not is_in_party(caller):
            self.caller.msg("You're not in a party.")
            return
        
        if is_party_leader(caller):
            self.caller.msg("You're the leader - others follow you!")
            return
        
        if sync_party_location(caller):
            leader = get_party_leader(caller)
            self.caller.msg(f"You've caught up with {leader.key}.")


class CmdPartyHelp(Command):
    """
    Get help with party commands.
    
    Usage:
        partyhelp
    """
    key = "partyhelp"
    aliases = ["phelp", "party help"]
    locks = "cmd:all()"
    
    def func(self):
        lines = [
            "|w=== PARTY COMMANDS ===|n",
            "",
            "|yGeneral:|n",
            "  |wparty|n                    - View party status",
            "  |wparty invite|n <player>    - Invite to party",
            "  |wparty accept|n <leader>    - Accept invitation",
            "  |wparty decline|n <leader>   - Decline invitation",
            "  |wparty leave|n              - Leave your party",
            "",
            "|yLeader Only:|n",
            "  |wparty kick|n <player>      - Kick a member",
            "  |wparty disband|n            - Disband party",
            "  |wparty promote|n <player>   - Promote/transfer lead",
            "  |wparty formation|n <type>   - Set combat formation",
            "  |wparty loot|n <mode>        - Set loot distribution",
            "  |wparty recall|n             - Summon party to you",
            "",
            "|yCommunication:|n",
            "  |wp|n <message>              - Party chat",
            "  |wpemote|n <action>          - Party emote",
            "",
            "|yMovement:|n",
            "  |wfollow|n                   - Catch up to leader",
            "  Party members auto-follow when leader moves.",
            "",
            f"|wMax party size: {MAX_PARTY_SIZE}|n",
        ]
        
        self.caller.msg("\n".join(lines))


# =============================================================================
# Encounter Commands
# =============================================================================

class CmdEncounter(Command):
    """
    View current encounter status.
    
    Usage:
        encounter
        enc
    """
    key = "encounter"
    aliases = ["enc"]
    locks = "cmd:all()"
    
    def func(self):
        caller = self.caller
        
        from world.encounters import get_active_encounter, ENCOUNTER_TEMPLATES
        
        encounter = get_active_encounter(caller)
        
        if not encounter or not encounter.active:
            self.caller.msg("No active encounter.")
            return
        
        template = encounter.template
        lines = [f"|r=== ENCOUNTER: {template.get('name', 'Unknown')} ===|n"]
        lines.append(f"Wave: {encounter.current_wave}/{encounter.total_waves}")
        lines.append("")
        
        if encounter.combat and encounter.combat.active:
            lines.append(encounter.combat.get_status_display(caller))
        
        self.caller.msg("\n".join(lines))


class CmdDanger(Command):
    """
    Check the danger level of your current area.
    
    Usage:
        danger
    """
    key = "danger"
    aliases = ["dangerlevel"]
    locks = "cmd:all()"
    
    def func(self):
        caller = self.caller
        
        from world.encounters import get_room_danger
        
        if not caller.location:
            self.caller.msg("You're nowhere.")
            return
        
        danger = get_room_danger(caller.location)
        color = danger.get("color", "|w")
        name = danger.get("name", "Unknown")
        
        self.caller.msg(f"Danger level: {color}{name}|n")
        
        mult = danger.get("encounter_mult", 1.0)
        if mult == 0:
            self.caller.msg("This area is safe from random encounters.")
        elif mult < 1:
            self.caller.msg("Random encounters are less common here.")
        elif mult > 1:
            self.caller.msg("Random encounters are more common here!")


# =============================================================================
# Command Set
# =============================================================================

class PartyCmdSet(CmdSet):
    """Party and encounter commands."""
    
    key = "party_cmdset"
    
    def at_cmdset_creation(self):
        # Party management
        self.add(CmdParty())
        self.add(CmdPartyInvite())
        self.add(CmdPartyAccept())
        self.add(CmdPartyDecline())
        self.add(CmdPartyLeave())
        self.add(CmdPartyKick())
        self.add(CmdPartyDisband())
        self.add(CmdPartyPromote())
        self.add(CmdPartyFormation())
        self.add(CmdPartyLoot())
        self.add(CmdPartyChat())
        self.add(CmdPartyEmote())
        self.add(CmdPartyRecall())
        self.add(CmdPartyFollow())
        self.add(CmdPartyHelp())
        
        # Encounters
        self.add(CmdEncounter())
        self.add(CmdDanger())
