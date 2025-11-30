"""
Feral Pack System
=================

Pack dynamics for feral pets:
- Pack formation and management
- Alpha/beta/omega hierarchy
- Pack bonuses and behaviors
- Territory and pack interactions
"""

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any, Set
from enum import Enum
from datetime import datetime
import random


# =============================================================================
# ENUMS
# =============================================================================

class PackRank(Enum):
    """Rank within a pack."""
    ALPHA = "alpha"          # Pack leader
    BETA = "beta"            # Second in command
    GAMMA = "gamma"          # Senior member
    DELTA = "delta"          # Regular member
    OMEGA = "omega"          # Lowest rank, submissive
    OUTCAST = "outcast"      # Rejected from pack


class PackRole(Enum):
    """Specialized roles within pack."""
    LEADER = "leader"        # Makes decisions
    HUNTER = "hunter"        # Leads hunts
    SCOUT = "scout"          # Explores territory
    GUARDIAN = "guardian"    # Protects pack
    BREEDER = "breeder"      # Primary breeding stock
    CARETAKER = "caretaker"  # Tends to young/injured
    ENFORCER = "enforcer"    # Maintains discipline


class PackBehavior(Enum):
    """Pack behavioral states."""
    RESTING = "resting"      # Relaxed, idle
    HUNTING = "hunting"      # Searching for prey
    PATROLLING = "patrolling"  # Checking territory
    MATING = "mating"        # Breeding season activity
    DEFENDING = "defending"  # Protecting territory
    MIGRATING = "migrating"  # Moving to new area


# =============================================================================
# PACK MEMBER
# =============================================================================

@dataclass
class PackMember:
    """A member of a pack."""
    dbref: str
    name: str
    
    # Position
    rank: PackRank = PackRank.DELTA
    roles: List[PackRole] = field(default_factory=list)
    
    # Stats within pack
    dominance: int = 50      # 0-100, affects rank challenges
    submission: int = 50     # 0-100, willingness to submit
    pack_loyalty: int = 50   # 0-100, loyalty to pack
    
    # Breeding
    is_breeding_stock: bool = False
    matings_in_pack: int = 0
    offspring_in_pack: int = 0
    
    # Participation
    hunts_participated: int = 0
    hunts_successful: int = 0
    challenges_won: int = 0
    challenges_lost: int = 0
    
    # Timestamps
    joined_at: Optional[datetime] = None
    last_active: Optional[datetime] = None
    
    def get_dominance_score(self) -> int:
        """Calculate overall dominance score for challenges."""
        score = self.dominance
        
        # Rank bonuses
        rank_bonus = {
            PackRank.ALPHA: 30,
            PackRank.BETA: 20,
            PackRank.GAMMA: 10,
            PackRank.DELTA: 0,
            PackRank.OMEGA: -20,
            PackRank.OUTCAST: -30,
        }
        score += rank_bonus.get(self.rank, 0)
        
        # Experience bonus
        score += min(20, self.challenges_won * 2)
        score -= min(10, self.challenges_lost)
        
        return score
    
    def to_dict(self) -> dict:
        return {
            "dbref": self.dbref,
            "name": self.name,
            "rank": self.rank.value,
            "roles": [r.value for r in self.roles],
            "dominance": self.dominance,
            "submission": self.submission,
            "pack_loyalty": self.pack_loyalty,
            "is_breeding_stock": self.is_breeding_stock,
            "matings_in_pack": self.matings_in_pack,
            "offspring_in_pack": self.offspring_in_pack,
            "hunts_participated": self.hunts_participated,
            "hunts_successful": self.hunts_successful,
            "challenges_won": self.challenges_won,
            "challenges_lost": self.challenges_lost,
            "joined_at": self.joined_at.isoformat() if self.joined_at else None,
            "last_active": self.last_active.isoformat() if self.last_active else None,
        }
    
    @classmethod
    def from_dict(cls, data: dict) -> "PackMember":
        member = cls(
            dbref=data["dbref"],
            name=data["name"],
        )
        member.rank = PackRank(data.get("rank", "delta"))
        member.roles = [PackRole(r) for r in data.get("roles", [])]
        member.dominance = data.get("dominance", 50)
        member.submission = data.get("submission", 50)
        member.pack_loyalty = data.get("pack_loyalty", 50)
        member.is_breeding_stock = data.get("is_breeding_stock", False)
        member.matings_in_pack = data.get("matings_in_pack", 0)
        member.offspring_in_pack = data.get("offspring_in_pack", 0)
        member.hunts_participated = data.get("hunts_participated", 0)
        member.hunts_successful = data.get("hunts_successful", 0)
        member.challenges_won = data.get("challenges_won", 0)
        member.challenges_lost = data.get("challenges_lost", 0)
        
        if data.get("joined_at"):
            member.joined_at = datetime.fromisoformat(data["joined_at"])
        if data.get("last_active"):
            member.last_active = datetime.fromisoformat(data["last_active"])
        
        return member


# =============================================================================
# PACK
# =============================================================================

@dataclass
class Pack:
    """A pack of feral animals."""
    pack_id: str
    name: str
    
    # Members
    members: Dict[str, PackMember] = field(default_factory=dict)  # dbref -> member
    
    # Leadership
    alpha_dbref: str = ""
    beta_dbref: str = ""
    
    # Territory
    territory_rooms: Set[str] = field(default_factory=set)  # Room dbrefs
    home_room: str = ""
    
    # State
    behavior: PackBehavior = PackBehavior.RESTING
    
    # Stats
    pack_strength: int = 50   # Overall pack power
    pack_cohesion: int = 50   # How unified the pack is
    territory_control: int = 50  # How secure territory is
    
    # Breeding
    breeding_season: bool = False
    
    # History
    formed_at: Optional[datetime] = None
    total_hunts: int = 0
    successful_hunts: int = 0
    
    # Owner (if owned pack)
    owner_dbref: str = ""
    
    @property
    def size(self) -> int:
        """Get pack size."""
        return len(self.members)
    
    @property
    def alpha(self) -> Optional[PackMember]:
        """Get alpha member."""
        return self.members.get(self.alpha_dbref)
    
    @property
    def beta(self) -> Optional[PackMember]:
        """Get beta member."""
        return self.members.get(self.beta_dbref)
    
    def add_member(self, dbref: str, name: str, rank: PackRank = PackRank.DELTA) -> PackMember:
        """Add a new member to the pack."""
        member = PackMember(
            dbref=dbref,
            name=name,
            rank=rank,
            joined_at=datetime.now(),
            last_active=datetime.now(),
        )
        
        self.members[dbref] = member
        
        # If first member, make alpha
        if len(self.members) == 1:
            member.rank = PackRank.ALPHA
            self.alpha_dbref = dbref
            member.roles.append(PackRole.LEADER)
        
        self._update_pack_strength()
        return member
    
    def remove_member(self, dbref: str) -> bool:
        """Remove a member from the pack."""
        if dbref not in self.members:
            return False
        
        member = self.members[dbref]
        
        # Handle alpha removal
        if dbref == self.alpha_dbref:
            self.alpha_dbref = ""
            self._select_new_alpha()
        
        # Handle beta removal
        if dbref == self.beta_dbref:
            self.beta_dbref = ""
            self._select_new_beta()
        
        del self.members[dbref]
        self._update_pack_strength()
        return True
    
    def _select_new_alpha(self):
        """Select a new alpha from remaining members."""
        if not self.members:
            return
        
        # Beta becomes alpha if exists
        if self.beta_dbref and self.beta_dbref in self.members:
            self.alpha_dbref = self.beta_dbref
            self.members[self.alpha_dbref].rank = PackRank.ALPHA
            if PackRole.LEADER not in self.members[self.alpha_dbref].roles:
                self.members[self.alpha_dbref].roles.append(PackRole.LEADER)
            self._select_new_beta()
            return
        
        # Otherwise, highest dominance
        candidates = [(m.dominance, m.dbref) for m in self.members.values()]
        candidates.sort(reverse=True)
        
        if candidates:
            new_alpha_dbref = candidates[0][1]
            self.alpha_dbref = new_alpha_dbref
            self.members[new_alpha_dbref].rank = PackRank.ALPHA
            if PackRole.LEADER not in self.members[new_alpha_dbref].roles:
                self.members[new_alpha_dbref].roles.append(PackRole.LEADER)
    
    def _select_new_beta(self):
        """Select a new beta from remaining members."""
        if len(self.members) < 2:
            self.beta_dbref = ""
            return
        
        # Highest dominance that isn't alpha
        candidates = [
            (m.dominance, m.dbref) 
            for m in self.members.values() 
            if m.dbref != self.alpha_dbref
        ]
        candidates.sort(reverse=True)
        
        if candidates:
            new_beta_dbref = candidates[0][1]
            self.beta_dbref = new_beta_dbref
            self.members[new_beta_dbref].rank = PackRank.BETA
    
    def _update_pack_strength(self):
        """Update pack strength based on members."""
        if not self.members:
            self.pack_strength = 0
            return
        
        # Base from size
        base = min(100, len(self.members) * 10)
        
        # Bonus from high-dominance members
        avg_dom = sum(m.dominance for m in self.members.values()) / len(self.members)
        base += int((avg_dom - 50) / 5)
        
        # Bonus from cohesion
        base += self.pack_cohesion // 10
        
        self.pack_strength = max(0, min(100, base))
    
    def get_members_by_rank(self) -> Dict[PackRank, List[PackMember]]:
        """Get members organized by rank."""
        result = {rank: [] for rank in PackRank}
        for member in self.members.values():
            result[member.rank].append(member)
        return result
    
    def get_breeding_stock(self) -> List[PackMember]:
        """Get members marked as breeding stock."""
        return [m for m in self.members.values() if m.is_breeding_stock]
    
    def challenge_for_rank(self, challenger_dbref: str, defender_dbref: str) -> Tuple[bool, str]:
        """
        Resolve a dominance challenge between two pack members.
        
        Returns:
            (challenger_won: bool, message: str)
        """
        if challenger_dbref not in self.members or defender_dbref not in self.members:
            return False, "Both participants must be pack members."
        
        challenger = self.members[challenger_dbref]
        defender = self.members[defender_dbref]
        
        # Can't challenge lower ranks
        rank_order = list(PackRank)
        if rank_order.index(challenger.rank) < rank_order.index(defender.rank):
            return False, "Cannot challenge a lower-ranked member."
        
        # Calculate scores
        challenger_score = challenger.get_dominance_score() + random.randint(-20, 20)
        defender_score = defender.get_dominance_score() + random.randint(-20, 20)
        
        # Defender has slight home advantage
        defender_score += 5
        
        challenger_won = challenger_score > defender_score
        
        if challenger_won:
            # Swap ranks
            old_challenger_rank = challenger.rank
            challenger.rank = defender.rank
            defender.rank = old_challenger_rank
            
            # Update alpha/beta if necessary
            if defender.dbref == self.alpha_dbref:
                self.alpha_dbref = challenger.dbref
            elif defender.dbref == self.beta_dbref:
                self.beta_dbref = challenger.dbref
            
            # Update stats
            challenger.challenges_won += 1
            challenger.dominance = min(100, challenger.dominance + 10)
            defender.challenges_lost += 1
            defender.dominance = max(0, defender.dominance - 10)
            defender.submission = min(100, defender.submission + 5)
            
            msg = f"{challenger.name} defeats {defender.name} and takes their rank as {challenger.rank.value}!"
        else:
            # Challenger loses
            challenger.challenges_lost += 1
            challenger.dominance = max(0, challenger.dominance - 5)
            challenger.submission = min(100, challenger.submission + 10)
            defender.challenges_won += 1
            defender.dominance = min(100, defender.dominance + 5)
            
            msg = f"{defender.name} successfully defends their rank against {challenger.name}."
        
        # Cohesion decreases from challenges
        self.pack_cohesion = max(0, self.pack_cohesion - 5)
        
        return challenger_won, msg
    
    def submit_to_member(self, submitter_dbref: str, dominant_dbref: str) -> str:
        """A member submits to another, reinforcing hierarchy."""
        if submitter_dbref not in self.members or dominant_dbref not in self.members:
            return "Both must be pack members."
        
        submitter = self.members[submitter_dbref]
        dominant = self.members[dominant_dbref]
        
        # Update stats
        submitter.submission = min(100, submitter.submission + 5)
        dominant.dominance = min(100, dominant.dominance + 2)
        
        # Improves cohesion
        self.pack_cohesion = min(100, self.pack_cohesion + 2)
        
        return f"{submitter.name} shows submission to {dominant.name}."
    
    def conduct_hunt(self, participants: List[str]) -> Tuple[bool, str]:
        """
        Conduct a pack hunt.
        
        Returns:
            (success: bool, result_message: str)
        """
        if not participants:
            return False, "No participants for hunt."
        
        # Filter to actual members
        hunters = [self.members[p] for p in participants if p in self.members]
        if not hunters:
            return False, "No valid pack members participating."
        
        self.total_hunts += 1
        
        # Calculate hunt success
        base_chance = 30
        
        # More hunters = better
        base_chance += len(hunters) * 10
        
        # Hunter skill (from successful hunts)
        for hunter in hunters:
            if hunter.hunts_successful > 10:
                base_chance += 5
            elif hunter.hunts_successful > 5:
                base_chance += 3
        
        # Pack strength bonus
        base_chance += self.pack_strength // 10
        
        # Alpha leading bonus
        if self.alpha_dbref in [h.dbref for h in hunters]:
            base_chance += 15
        
        # Cap
        base_chance = min(95, base_chance)
        
        roll = random.randint(1, 100)
        success = roll <= base_chance
        
        # Update stats
        for hunter in hunters:
            hunter.hunts_participated += 1
            hunter.last_active = datetime.now()
            if success:
                hunter.hunts_successful += 1
        
        if success:
            self.successful_hunts += 1
            self.pack_cohesion = min(100, self.pack_cohesion + 3)
            return True, f"The hunt is successful! {len(hunters)} pack members bring down prey."
        else:
            return False, f"The hunt fails. The prey escapes {len(hunters)} hunters."
    
    def set_breeding_season(self, active: bool):
        """Set breeding season status."""
        self.breeding_season = active
        if active:
            # Increase breeding drive for all members
            for member in self.members.values():
                member.is_breeding_stock = True  # All participate in season
    
    def get_pack_info(self) -> str:
        """Get formatted pack information."""
        lines = []
        
        lines.append(f"=== {self.name} ===")
        lines.append(f"Size: {self.size} members")
        lines.append(f"Strength: {self.pack_strength}/100")
        lines.append(f"Cohesion: {self.pack_cohesion}/100")
        lines.append(f"Behavior: {self.behavior.value}")
        lines.append(f"Territory: {len(self.territory_rooms)} rooms")
        
        if self.breeding_season:
            lines.append("|rBreeding Season Active|n")
        
        lines.append("")
        lines.append("--- Hierarchy ---")
        
        for rank in PackRank:
            members = [m for m in self.members.values() if m.rank == rank]
            if members:
                names = ", ".join(m.name for m in members)
                lines.append(f"  {rank.value.title()}: {names}")
        
        lines.append("")
        lines.append(f"Hunt success: {self.successful_hunts}/{self.total_hunts}")
        
        return "\n".join(lines)
    
    def to_dict(self) -> dict:
        return {
            "pack_id": self.pack_id,
            "name": self.name,
            "members": {k: v.to_dict() for k, v in self.members.items()},
            "alpha_dbref": self.alpha_dbref,
            "beta_dbref": self.beta_dbref,
            "territory_rooms": list(self.territory_rooms),
            "home_room": self.home_room,
            "behavior": self.behavior.value,
            "pack_strength": self.pack_strength,
            "pack_cohesion": self.pack_cohesion,
            "territory_control": self.territory_control,
            "breeding_season": self.breeding_season,
            "formed_at": self.formed_at.isoformat() if self.formed_at else None,
            "total_hunts": self.total_hunts,
            "successful_hunts": self.successful_hunts,
            "owner_dbref": self.owner_dbref,
        }
    
    @classmethod
    def from_dict(cls, data: dict) -> "Pack":
        pack = cls(
            pack_id=data["pack_id"],
            name=data["name"],
        )
        
        pack.members = {
            k: PackMember.from_dict(v) 
            for k, v in data.get("members", {}).items()
        }
        pack.alpha_dbref = data.get("alpha_dbref", "")
        pack.beta_dbref = data.get("beta_dbref", "")
        pack.territory_rooms = set(data.get("territory_rooms", []))
        pack.home_room = data.get("home_room", "")
        pack.behavior = PackBehavior(data.get("behavior", "resting"))
        pack.pack_strength = data.get("pack_strength", 50)
        pack.pack_cohesion = data.get("pack_cohesion", 50)
        pack.territory_control = data.get("territory_control", 50)
        pack.breeding_season = data.get("breeding_season", False)
        
        if data.get("formed_at"):
            pack.formed_at = datetime.fromisoformat(data["formed_at"])
        
        pack.total_hunts = data.get("total_hunts", 0)
        pack.successful_hunts = data.get("successful_hunts", 0)
        pack.owner_dbref = data.get("owner_dbref", "")
        
        return pack


# =============================================================================
# PACK MANAGER
# =============================================================================

class PackManager:
    """
    Manages all packs in the game.
    """
    
    def __init__(self, storage=None):
        """
        Initialize pack manager.
        
        Args:
            storage: Object with attributes for persistent storage
        """
        self.storage = storage
        self._packs: Dict[str, Pack] = {}
        self._member_to_pack: Dict[str, str] = {}  # dbref -> pack_id
        
        if storage:
            self._load()
    
    def _load(self):
        """Load packs from storage."""
        if not self.storage:
            return
        
        data = self.storage.attributes.get("packs_data", {})
        
        for pack_id, pack_data in data.get("packs", {}).items():
            pack = Pack.from_dict(pack_data)
            self._packs[pack_id] = pack
            
            for member_dbref in pack.members:
                self._member_to_pack[member_dbref] = pack_id
    
    def _save(self):
        """Save packs to storage."""
        if not self.storage:
            return
        
        data = {
            "packs": {pid: p.to_dict() for pid, p in self._packs.items()}
        }
        
        self.storage.attributes.add("packs_data", data)
    
    def create_pack(self, name: str, founder_dbref: str, founder_name: str) -> Pack:
        """Create a new pack with a founding member."""
        import uuid
        
        pack_id = f"pack_{uuid.uuid4().hex[:8]}"
        
        pack = Pack(
            pack_id=pack_id,
            name=name,
            formed_at=datetime.now(),
        )
        
        # Add founder as alpha
        pack.add_member(founder_dbref, founder_name, PackRank.ALPHA)
        
        self._packs[pack_id] = pack
        self._member_to_pack[founder_dbref] = pack_id
        
        self._save()
        return pack
    
    def get_pack(self, pack_id: str) -> Optional[Pack]:
        """Get a pack by ID."""
        return self._packs.get(pack_id)
    
    def get_member_pack(self, dbref: str) -> Optional[Pack]:
        """Get the pack a member belongs to."""
        pack_id = self._member_to_pack.get(dbref)
        if pack_id:
            return self._packs.get(pack_id)
        return None
    
    def join_pack(self, pack_id: str, member_dbref: str, member_name: str) -> Tuple[bool, str]:
        """Add a member to a pack."""
        pack = self._packs.get(pack_id)
        if not pack:
            return False, "Pack not found."
        
        # Check if already in a pack
        if member_dbref in self._member_to_pack:
            return False, f"{member_name} is already in a pack."
        
        pack.add_member(member_dbref, member_name)
        self._member_to_pack[member_dbref] = pack_id
        
        self._save()
        return True, f"{member_name} has joined {pack.name}."
    
    def leave_pack(self, member_dbref: str) -> Tuple[bool, str]:
        """Remove a member from their pack."""
        pack_id = self._member_to_pack.get(member_dbref)
        if not pack_id:
            return False, "Not in a pack."
        
        pack = self._packs.get(pack_id)
        if not pack:
            return False, "Pack not found."
        
        member = pack.members.get(member_dbref)
        name = member.name if member else "Member"
        
        pack.remove_member(member_dbref)
        del self._member_to_pack[member_dbref]
        
        # Disband if empty
        if not pack.members:
            del self._packs[pack_id]
        
        self._save()
        return True, f"{name} has left {pack.name}."
    
    def disband_pack(self, pack_id: str) -> Tuple[bool, str]:
        """Disband a pack entirely."""
        pack = self._packs.get(pack_id)
        if not pack:
            return False, "Pack not found."
        
        # Remove all member mappings
        for dbref in list(pack.members.keys()):
            if dbref in self._member_to_pack:
                del self._member_to_pack[dbref]
        
        name = pack.name
        del self._packs[pack_id]
        
        self._save()
        return True, f"{name} has been disbanded."
    
    def get_all_packs(self) -> List[Pack]:
        """Get all packs."""
        return list(self._packs.values())
    
    def get_packs_in_room(self, room_dbref: str) -> List[Pack]:
        """Get packs that have territory in a room."""
        return [p for p in self._packs.values() if room_dbref in p.territory_rooms]
    
    def claim_territory(self, pack_id: str, room_dbref: str) -> Tuple[bool, str]:
        """Claim a room as pack territory."""
        pack = self._packs.get(pack_id)
        if not pack:
            return False, "Pack not found."
        
        # Check if already claimed by another pack
        for other_pack in self._packs.values():
            if other_pack.pack_id != pack_id and room_dbref in other_pack.territory_rooms:
                return False, f"Territory already claimed by {other_pack.name}."
        
        pack.territory_rooms.add(room_dbref)
        pack.territory_control = min(100, pack.territory_control + 5)
        
        self._save()
        return True, f"{pack.name} claims this territory."
    
    def abandon_territory(self, pack_id: str, room_dbref: str) -> Tuple[bool, str]:
        """Abandon a territory."""
        pack = self._packs.get(pack_id)
        if not pack:
            return False, "Pack not found."
        
        if room_dbref in pack.territory_rooms:
            pack.territory_rooms.remove(room_dbref)
            self._save()
            return True, f"{pack.name} abandons this territory."
        
        return False, "This is not pack territory."


# =============================================================================
# PACK MIXIN
# =============================================================================

class PackMixin:
    """
    Mixin for characters/NPCs to have pack membership.
    """
    
    @property
    def pack_member_data(self) -> Optional[PackMember]:
        """Get pack membership data if in a pack."""
        # This would need the pack manager to look up
        # Implementation depends on how manager is accessed
        return None
    
    def is_pack_alpha(self) -> bool:
        """Check if this character is a pack alpha."""
        member = self.pack_member_data
        return member and member.rank == PackRank.ALPHA
    
    def is_pack_omega(self) -> bool:
        """Check if this character is a pack omega."""
        member = self.pack_member_data
        return member and member.rank == PackRank.OMEGA
    
    def get_pack_rank_desc(self) -> str:
        """Get description of pack rank."""
        member = self.pack_member_data
        if not member:
            return "not part of a pack"
        
        return f"the {member.rank.value} of their pack"


# =============================================================================
# HELPER FUNCTIONS
# =============================================================================

def calculate_pack_compatibility(pet1_species: str, pet2_species: str) -> int:
    """
    Calculate how well two species work together in a pack.
    
    Returns:
        Compatibility score 0-100
    """
    # Same species = best
    if pet1_species == pet2_species:
        return 100
    
    # Species families
    canines = {"wolf", "dog", "fox", "jackal", "coyote", "hyena"}
    felines = {"cat", "lion", "tiger", "leopard", "panther", "lynx"}
    equines = {"horse", "pony", "donkey", "zebra", "unicorn"}
    
    # Same family = good
    for family in [canines, felines, equines]:
        if pet1_species in family and pet2_species in family:
            return 75
    
    # Mixed predators = okay
    predators = canines | felines
    if pet1_species in predators and pet2_species in predators:
        return 50
    
    # Very different = poor
    return 25


def get_rank_display(rank: PackRank) -> str:
    """Get display string for a rank."""
    displays = {
        PackRank.ALPHA: "|yAlpha|n",
        PackRank.BETA: "|cBeta|n",
        PackRank.GAMMA: "|gGamma|n",
        PackRank.DELTA: "Delta",
        PackRank.OMEGA: "|rOmega|n",
        PackRank.OUTCAST: "|xOutcast|n",
    }
    return displays.get(rank, rank.value)


__all__ = [
    "PackRank",
    "PackRole",
    "PackBehavior",
    "PackMember",
    "Pack",
    "PackManager",
    "PackMixin",
    "calculate_pack_compatibility",
    "get_rank_display",
]
