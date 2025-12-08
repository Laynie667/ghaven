"""
Party System for Gilderhaven

Allows players to form groups for exploration and combat.
Party leader controls movement - all members follow automatically.
Encounters trigger for the entire party together.
"""

from evennia.utils import delay

# =============================================================================
# PARTY CONSTANTS
# =============================================================================

MAX_PARTY_SIZE = 6
INVITE_TIMEOUT = 60  # Seconds before invite expires

PARTY_ROLES = {
    "leader": {
        "name": "Leader",
        "desc": "Controls party movement and can kick members.",
        "can_kick": True,
        "can_invite": True,
        "can_disband": True,
    },
    "officer": {
        "name": "Officer",
        "desc": "Can invite new members.",
        "can_kick": False,
        "can_invite": True,
        "can_disband": False,
    },
    "member": {
        "name": "Member",
        "desc": "Standard party member.",
        "can_kick": False,
        "can_invite": False,
        "can_disband": False,
    },
}

# Party formation types for combat
PARTY_FORMATIONS = {
    "standard": {
        "name": "Standard",
        "desc": "Balanced formation.",
        "front_row": 0.6,  # 60% of party in front
        "back_protected": True,
    },
    "aggressive": {
        "name": "Aggressive",
        "desc": "Everyone in front for maximum damage.",
        "front_row": 1.0,
        "back_protected": False,
        "damage_bonus": 0.1,
    },
    "defensive": {
        "name": "Defensive",
        "desc": "Protect the back line.",
        "front_row": 0.4,
        "back_protected": True,
        "defense_bonus": 0.15,
    },
    "scattered": {
        "name": "Scattered",
        "desc": "Spread out to avoid AoE.",
        "front_row": 0.5,
        "back_protected": False,
        "aoe_reduction": 0.5,
    },
}


# =============================================================================
# Party Data Structure
# =============================================================================

class Party:
    """
    Represents a group of players.
    
    Stored on leader as leader.ndb.party
    Members have member.ndb.party pointing to same object
    """
    
    def __init__(self, leader):
        """Create a new party with the given leader."""
        self.leader = leader
        self.members = [leader]  # Leader is always first member
        self.roles = {leader: "leader"}
        self.formation = "standard"
        self.pending_invites = {}  # {character: expire_time}
        self.loot_mode = "ffa"  # ffa, round_robin, leader
        self.active = True
        
        # Link to leader
        leader.ndb.party = self
    
    def add_member(self, character):
        """Add a member to the party."""
        if len(self.members) >= MAX_PARTY_SIZE:
            return False, "Party is full."
        
        if character in self.members:
            return False, "Already in party."
        
        self.members.append(character)
        self.roles[character] = "member"
        character.ndb.party = self
        
        # Remove from pending invites
        if character in self.pending_invites:
            del self.pending_invites[character]
        
        return True, f"{character.key} joined the party."
    
    def remove_member(self, character, reason="left"):
        """Remove a member from the party."""
        if character not in self.members:
            return False, "Not in party."
        
        if character == self.leader:
            # Leader leaving disbands or transfers
            if len(self.members) > 1:
                # Transfer leadership
                new_leader = self.members[1]
                self.leader = new_leader
                self.roles[new_leader] = "leader"
            else:
                # Disband
                self.disband()
                return True, "Party disbanded."
        
        self.members.remove(character)
        del self.roles[character]
        character.ndb.party = None
        
        return True, f"{character.key} {reason} the party."
    
    def kick_member(self, kicker, target):
        """Kick a member from the party."""
        kicker_role = self.roles.get(kicker)
        if not kicker_role:
            return False, "You're not in this party."
        
        role_data = PARTY_ROLES.get(kicker_role, {})
        if not role_data.get("can_kick") and kicker != self.leader:
            return False, "You can't kick members."
        
        if target == self.leader:
            return False, "Can't kick the leader."
        
        if target not in self.members:
            return False, "They're not in the party."
        
        return self.remove_member(target, "was kicked from")
    
    def promote(self, character, new_role):
        """Change a member's role."""
        if character not in self.members:
            return False, "Not in party."
        
        if character == self.leader and new_role != "leader":
            return False, "Can't demote leader without transferring leadership."
        
        if new_role not in PARTY_ROLES:
            return False, "Invalid role."
        
        self.roles[character] = new_role
        return True, f"{character.key} is now {PARTY_ROLES[new_role]['name']}."
    
    def transfer_leadership(self, new_leader):
        """Transfer party leadership."""
        if new_leader not in self.members:
            return False, "Not in party."
        
        old_leader = self.leader
        self.roles[old_leader] = "member"
        self.roles[new_leader] = "leader"
        self.leader = new_leader
        
        return True, f"{new_leader.key} is now the party leader."
    
    def invite(self, inviter, target):
        """Invite a player to the party."""
        inviter_role = self.roles.get(inviter)
        if not inviter_role:
            return False, "You're not in this party."
        
        role_data = PARTY_ROLES.get(inviter_role, {})
        if not role_data.get("can_invite"):
            return False, "You can't invite members."
        
        if len(self.members) >= MAX_PARTY_SIZE:
            return False, "Party is full."
        
        if target in self.members:
            return False, "Already in party."
        
        if target.ndb.party:
            return False, "They're already in a party."
        
        # Add to pending
        self.pending_invites[target] = True
        
        # Schedule expiration
        def expire_invite():
            if target in self.pending_invites:
                del self.pending_invites[target]
                if hasattr(target, "msg"):
                    target.msg(f"Party invitation from {inviter.key} has expired.")
        
        delay(INVITE_TIMEOUT, expire_invite)
        
        return True, f"Invited {target.key} to the party."
    
    def accept_invite(self, character):
        """Accept a pending invite."""
        if character not in self.pending_invites:
            return False, "No pending invite."
        
        return self.add_member(character)
    
    def decline_invite(self, character):
        """Decline a pending invite."""
        if character not in self.pending_invites:
            return False, "No pending invite."
        
        del self.pending_invites[character]
        return True, "Invite declined."
    
    def disband(self):
        """Disband the party entirely."""
        self.active = False
        
        for member in self.members[:]:  # Copy to avoid modification during iteration
            member.ndb.party = None
            if hasattr(member, "msg"):
                member.msg("|yThe party has been disbanded.|n")
        
        self.members = []
        self.roles = {}
    
    def set_formation(self, formation_key):
        """Set party combat formation."""
        if formation_key not in PARTY_FORMATIONS:
            return False, f"Unknown formation. Options: {', '.join(PARTY_FORMATIONS.keys())}"
        
        self.formation = formation_key
        formation = PARTY_FORMATIONS[formation_key]
        return True, f"Formation set to {formation['name']}."
    
    def set_loot_mode(self, mode):
        """Set loot distribution mode."""
        valid_modes = ["ffa", "round_robin", "leader"]
        if mode not in valid_modes:
            return False, f"Invalid mode. Options: {', '.join(valid_modes)}"
        
        self.loot_mode = mode
        return True, f"Loot mode set to {mode}."
    
    def msg_party(self, message, exclude=None):
        """Send a message to all party members."""
        for member in self.members:
            if exclude and member in exclude:
                continue
            if hasattr(member, "msg"):
                member.msg(message)
    
    def get_display(self, viewer=None):
        """Get formatted party display."""
        lines = ["|w=== PARTY ===|n"]
        
        formation = PARTY_FORMATIONS.get(self.formation, {})
        lines.append(f"Formation: |c{formation.get('name', 'Unknown')}|n")
        lines.append(f"Loot: |c{self.loot_mode}|n")
        lines.append("")
        
        for member in self.members:
            role = self.roles.get(member, "member")
            role_name = PARTY_ROLES.get(role, {}).get("name", "Member")
            
            # Role indicator
            if role == "leader":
                role_marker = "|y★|n "
            elif role == "officer":
                role_marker = "|c◆|n "
            else:
                role_marker = "  "
            
            # Location indicator
            if viewer and member.location != viewer.location:
                loc_marker = " |x(elsewhere)|n"
            else:
                loc_marker = ""
            
            # Health bar (simplified)
            from world.combat import get_resource, get_max_resource
            hp = get_resource(member, "hp")
            max_hp = get_max_resource(member, "hp")
            hp_pct = int((hp / max_hp) * 100) if max_hp > 0 else 100
            
            if hp_pct > 75:
                hp_color = "|g"
            elif hp_pct > 25:
                hp_color = "|y"
            else:
                hp_color = "|r"
            
            lines.append(
                f"{role_marker}|w{member.key}|n [{role_name}] "
                f"{hp_color}{hp_pct}% HP|n{loc_marker}"
            )
        
        # Pending invites
        if self.pending_invites:
            lines.append("")
            lines.append("|xPending invites:|n")
            for char in self.pending_invites:
                lines.append(f"  {char.key}")
        
        return "\n".join(lines)


# =============================================================================
# Helper Functions
# =============================================================================

def get_party(character):
    """Get a character's party (or None)."""
    return character.ndb.party if hasattr(character, "ndb") else None


def is_in_party(character):
    """Check if character is in a party."""
    return get_party(character) is not None


def is_party_leader(character):
    """Check if character is a party leader."""
    party = get_party(character)
    return party and party.leader == character


def get_party_members(character):
    """Get all members of a character's party."""
    party = get_party(character)
    return party.members if party else [character]


def get_party_leader(character):
    """Get the leader of a character's party."""
    party = get_party(character)
    return party.leader if party else character


def create_party(leader):
    """Create a new party with the given leader."""
    if is_in_party(leader):
        return None, "Already in a party."
    
    party = Party(leader)
    return party, f"Party created with {leader.key} as leader."


def disband_party(character):
    """Disband a character's party (must be leader)."""
    party = get_party(character)
    if not party:
        return False, "Not in a party."
    
    if party.leader != character:
        return False, "Only the leader can disband the party."
    
    party.disband()
    return True, "Party disbanded."


def leave_party(character):
    """Leave current party."""
    party = get_party(character)
    if not party:
        return False, "Not in a party."
    
    return party.remove_member(character, "left")


def invite_to_party(inviter, target):
    """Invite someone to your party."""
    party = get_party(inviter)
    
    if not party:
        # Create a new party first
        party, msg = create_party(inviter)
        if not party:
            return False, msg
    
    return party.invite(inviter, target)


def accept_party_invite(character, party_leader):
    """Accept an invite from a specific party."""
    party = get_party(party_leader)
    if not party:
        return False, "That party no longer exists."
    
    return party.accept_invite(character)


def decline_party_invite(character, party_leader):
    """Decline an invite from a specific party."""
    party = get_party(party_leader)
    if not party:
        return False, "That party no longer exists."
    
    return party.decline_invite(character)


def get_pending_invites(character):
    """Get list of parties that have invited this character."""
    # Search all active parties for invites to this character
    # This is a bit inefficient but works for small player counts
    invites = []
    
    # Check all characters in the same location and connected rooms
    if hasattr(character, "location") and character.location:
        for obj in character.location.contents:
            if hasattr(obj, "ndb") and obj.ndb.party:
                party = obj.ndb.party
                if character in party.pending_invites:
                    invites.append(party)
    
    return invites


# =============================================================================
# Party Movement System
# =============================================================================

def party_move(leader, destination, quiet=False):
    """
    Move entire party to a new location.
    
    Called when party leader moves - all members follow.
    
    Args:
        leader: The party leader initiating movement
        destination: Target room
        quiet: Whether to suppress movement messages
        
    Returns:
        list: Members who successfully moved
    """
    party = get_party(leader)
    if not party or party.leader != leader:
        return []
    
    moved = []
    
    for member in party.members:
        if member == leader:
            continue  # Leader moves themselves normally
        
        if member.location == leader.location:
            # Member is with leader, move them
            old_loc = member.location
            
            # Announce departure
            if not quiet and old_loc:
                old_loc.msg_contents(
                    f"{member.key} follows {leader.key}.",
                    exclude=[member]
                )
            
            # Move member
            member.move_to(destination, quiet=True)
            
            # Announce arrival
            if not quiet:
                destination.msg_contents(
                    f"{member.key} arrives, following {leader.key}.",
                    exclude=[member, leader]
                )
                member.msg(f"You follow {leader.key}.")
            
            moved.append(member)
    
    return moved


def sync_party_location(character):
    """
    Sync a character's location with their party leader.
    
    Used when someone joins a party or reconnects.
    """
    party = get_party(character)
    if not party:
        return False
    
    leader = party.leader
    if character == leader:
        return True  # Leader is always in sync
    
    if character.location != leader.location:
        character.move_to(leader.location, quiet=True)
        character.msg(f"You've been moved to {leader.key}'s location.")
        return True
    
    return True


def party_recall(leader):
    """
    Teleport all party members to the leader's location.
    
    Useful if party gets separated.
    """
    party = get_party(leader)
    if not party or party.leader != leader:
        return False, "You're not a party leader."
    
    recalled = []
    for member in party.members:
        if member == leader:
            continue
        if member.location != leader.location:
            member.move_to(leader.location, quiet=True)
            member.msg(f"|yYou've been recalled to {leader.key}'s location.|n")
            recalled.append(member)
    
    if recalled:
        names = ", ".join([m.key for m in recalled])
        return True, f"Recalled: {names}"
    else:
        return True, "Party is already together."


# =============================================================================
# Party Combat Integration
# =============================================================================

def get_party_for_combat(character):
    """
    Get all party members for a combat encounter.
    
    Returns list of characters who should join combat.
    Only includes members in the same location.
    """
    party = get_party(character)
    if not party:
        return [character]
    
    # Only include members in same location
    location = character.location
    combatants = []
    
    for member in party.members:
        if member.location == location:
            combatants.append(member)
    
    return combatants


def start_party_combat(leader, enemies, location, encounter_type="hostile"):
    """
    Start combat with entire party vs enemies.
    
    Args:
        leader: Party leader (or solo player)
        enemies: List of enemy creatures
        location: Combat location
        encounter_type: Type of encounter
        
    Returns:
        CombatInstance
    """
    from world.combat import CombatInstance, initialize_combat_stats
    
    # Get all party members in this location
    party_members = get_party_for_combat(leader)
    
    # Build participant list
    participants = []
    for member in party_members:
        initialize_combat_stats(member)
        participants.append((member, "player"))
    
    for enemy in enemies:
        participants.append((enemy, "enemy"))
    
    # Create combat
    combat = CombatInstance(participants, location, encounter_type)
    
    # Announce to party
    enemy_names = ", ".join([e.key for e in enemies])
    for member in party_members:
        member.msg(f"|r=== COMBAT BEGINS ===|n")
        member.msg(f"Your party is attacked by: {enemy_names}!")
        member.msg(combat.get_status_display(member))
    
    return combat


def distribute_loot(party, loot_items, source_name=""):
    """
    Distribute loot among party members based on loot mode.
    
    Args:
        party: Party object (or None for solo)
        loot_items: List of (item_key, amount) tuples
        source_name: Name of loot source for messages
        
    Returns:
        dict: {character: [(item, amount), ...]}
    """
    from world.items import create_item, give_item
    
    if not party:
        return {}
    
    distributions = {member: [] for member in party.members}
    
    if party.loot_mode == "ffa":
        # Free for all - first come first served
        # In practice, goes to party leader
        for item_key, amount in loot_items:
            leader = party.leader
            distributions[leader].append((item_key, amount))
            leader.msg(f"|gYou obtained: {item_key} x{amount}|n")
    
    elif party.loot_mode == "round_robin":
        # Rotate through members
        member_index = 0
        for item_key, amount in loot_items:
            member = party.members[member_index]
            distributions[member].append((item_key, amount))
            member.msg(f"|gYou obtained: {item_key} x{amount}|n")
            member_index = (member_index + 1) % len(party.members)
    
    elif party.loot_mode == "leader":
        # Leader gets all
        leader = party.leader
        for item_key, amount in loot_items:
            distributions[leader].append((item_key, amount))
            leader.msg(f"|gYou obtained: {item_key} x{amount}|n")
    
    # Actually create and give items
    for member, items in distributions.items():
        for item_key, amount in items:
            item = create_item(item_key, location=member)
            if item and amount > 1:
                item.db.quantity = amount
    
    return distributions


def distribute_exp(party, exp_amount, source_name=""):
    """
    Distribute experience among party members.
    
    Splits evenly with a bonus for grouping.
    """
    if not party:
        return {}
    
    # Group bonus: +10% per member beyond first
    group_bonus = 1.0 + (len(party.members) - 1) * 0.1
    total_exp = int(exp_amount * group_bonus)
    per_member = total_exp // len(party.members)
    
    distributions = {}
    for member in party.members:
        distributions[member] = per_member
        # Would add to character's exp here
        member.msg(f"|c+{per_member} experience from {source_name}|n")
    
    return distributions


# =============================================================================
# Party Chat
# =============================================================================

def party_chat(sender, message):
    """Send a message to party chat."""
    party = get_party(sender)
    if not party:
        return False, "Not in a party."
    
    formatted = f"|M[Party] {sender.key}: {message}|n"
    party.msg_party(formatted)
    return True, ""


def party_emote(sender, emote):
    """Send an emote to party chat."""
    party = get_party(sender)
    if not party:
        return False, "Not in a party."
    
    formatted = f"|M[Party] * {sender.key} {emote}|n"
    party.msg_party(formatted)
    return True, ""
