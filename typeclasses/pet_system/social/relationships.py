"""
Relationships System
====================

Relationship and social bond tracking:
- Relationship types and levels
- Reputation with factions
- Social bonds between characters
"""

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any, Tuple, Set
from enum import Enum
from datetime import datetime


# =============================================================================
# ENUMS
# =============================================================================

class RelationshipType(Enum):
    """Types of relationships."""
    ACQUAINTANCE = "acquaintance"
    FRIEND = "friend"
    CLOSE_FRIEND = "close_friend"
    LOVER = "lover"
    PARTNER = "partner"           # Committed relationship
    SPOUSE = "spouse"
    RIVAL = "rival"
    ENEMY = "enemy"
    OWNER = "owner"               # Owns the other
    OWNED = "owned"               # Is owned by the other
    MASTER = "master"             # Trains/dominates
    SUBMISSIVE = "submissive"     # Trained by
    BREEDER = "breeder"           # Breeding relationship
    PACK_MATE = "pack_mate"       # In same pack
    SIBLING = "sibling"
    PARENT = "parent"
    CHILD = "child"
    MATE = "mate"                 # Animal/feral mate


class RelationshipStatus(Enum):
    """Status of a relationship."""
    ACTIVE = "active"
    STRAINED = "strained"
    BROKEN = "broken"
    PENDING = "pending"           # Awaiting acceptance


class ReputationLevel(Enum):
    """Reputation levels."""
    HATED = "hated"               # -100 to -75
    HOSTILE = "hostile"           # -74 to -50
    UNFRIENDLY = "unfriendly"     # -49 to -25
    NEUTRAL = "neutral"           # -24 to 24
    FRIENDLY = "friendly"         # 25 to 49
    HONORED = "honored"           # 50 to 74
    REVERED = "revered"           # 75 to 100


# =============================================================================
# RELATIONSHIP
# =============================================================================

@dataclass
class Relationship:
    """A relationship between two characters."""
    relationship_id: str
    
    # Parties
    character_a_dbref: str = ""
    character_a_name: str = ""
    character_b_dbref: str = ""
    character_b_name: str = ""
    
    # Type and status
    relationship_type: RelationshipType = RelationshipType.ACQUAINTANCE
    status: RelationshipStatus = RelationshipStatus.ACTIVE
    
    # Feelings (0-100)
    affection_a_to_b: int = 50   # How A feels about B
    affection_b_to_a: int = 50   # How B feels about A
    trust_a_to_b: int = 50
    trust_b_to_a: int = 50
    
    # Dominance dynamic (-100 to 100)
    # Negative = A submits to B, Positive = A dominates B
    dominance_dynamic: int = 0
    
    # History
    established_date: Optional[datetime] = None
    last_interaction: Optional[datetime] = None
    interaction_count: int = 0
    
    # Special
    is_exclusive: bool = False   # Exclusive relationship
    is_public: bool = True       # Publicly known
    
    # Notes
    notes: str = ""
    
    def get_affection(self, from_dbref: str) -> int:
        """Get affection from one party to the other."""
        if from_dbref == self.character_a_dbref:
            return self.affection_a_to_b
        return self.affection_b_to_a
    
    def get_trust(self, from_dbref: str) -> int:
        """Get trust from one party to the other."""
        if from_dbref == self.character_a_dbref:
            return self.trust_a_to_b
        return self.trust_b_to_a
    
    def modify_affection(self, from_dbref: str, amount: int) -> int:
        """Modify affection. Returns new value."""
        if from_dbref == self.character_a_dbref:
            self.affection_a_to_b = max(0, min(100, self.affection_a_to_b + amount))
            return self.affection_a_to_b
        else:
            self.affection_b_to_a = max(0, min(100, self.affection_b_to_a + amount))
            return self.affection_b_to_a
    
    def modify_trust(self, from_dbref: str, amount: int) -> int:
        """Modify trust. Returns new value."""
        if from_dbref == self.character_a_dbref:
            self.trust_a_to_b = max(0, min(100, self.trust_a_to_b + amount))
            return self.trust_a_to_b
        else:
            self.trust_b_to_a = max(0, min(100, self.trust_b_to_a + amount))
            return self.trust_b_to_a
    
    def record_interaction(self) -> None:
        """Record an interaction."""
        self.last_interaction = datetime.now()
        self.interaction_count += 1
    
    def get_other_party(self, my_dbref: str) -> Tuple[str, str]:
        """Get the other party's dbref and name."""
        if my_dbref == self.character_a_dbref:
            return self.character_b_dbref, self.character_b_name
        return self.character_a_dbref, self.character_a_name
    
    def get_summary(self, perspective_dbref: str = "") -> str:
        """Get summary of relationship."""
        if perspective_dbref:
            other_dbref, other_name = self.get_other_party(perspective_dbref)
            affection = self.get_affection(perspective_dbref)
            trust = self.get_trust(perspective_dbref)
            
            return (
                f"{other_name}: {self.relationship_type.value}\n"
                f"  Affection: {affection}/100, Trust: {trust}/100\n"
                f"  Status: {self.status.value}"
            )
        
        return (
            f"{self.character_a_name} <-> {self.character_b_name}\n"
            f"  Type: {self.relationship_type.value}\n"
            f"  Status: {self.status.value}"
        )
    
    def to_dict(self) -> dict:
        return {
            "relationship_id": self.relationship_id,
            "character_a_dbref": self.character_a_dbref,
            "character_a_name": self.character_a_name,
            "character_b_dbref": self.character_b_dbref,
            "character_b_name": self.character_b_name,
            "relationship_type": self.relationship_type.value,
            "status": self.status.value,
            "affection_a_to_b": self.affection_a_to_b,
            "affection_b_to_a": self.affection_b_to_a,
            "trust_a_to_b": self.trust_a_to_b,
            "trust_b_to_a": self.trust_b_to_a,
            "dominance_dynamic": self.dominance_dynamic,
            "established_date": self.established_date.isoformat() if self.established_date else None,
            "last_interaction": self.last_interaction.isoformat() if self.last_interaction else None,
            "interaction_count": self.interaction_count,
            "is_exclusive": self.is_exclusive,
            "is_public": self.is_public,
            "notes": self.notes,
        }
    
    @classmethod
    def from_dict(cls, data: dict) -> "Relationship":
        rel = cls(relationship_id=data["relationship_id"])
        rel.character_a_dbref = data.get("character_a_dbref", "")
        rel.character_a_name = data.get("character_a_name", "")
        rel.character_b_dbref = data.get("character_b_dbref", "")
        rel.character_b_name = data.get("character_b_name", "")
        rel.relationship_type = RelationshipType(data.get("relationship_type", "acquaintance"))
        rel.status = RelationshipStatus(data.get("status", "active"))
        rel.affection_a_to_b = data.get("affection_a_to_b", 50)
        rel.affection_b_to_a = data.get("affection_b_to_a", 50)
        rel.trust_a_to_b = data.get("trust_a_to_b", 50)
        rel.trust_b_to_a = data.get("trust_b_to_a", 50)
        rel.dominance_dynamic = data.get("dominance_dynamic", 0)
        
        if data.get("established_date"):
            rel.established_date = datetime.fromisoformat(data["established_date"])
        if data.get("last_interaction"):
            rel.last_interaction = datetime.fromisoformat(data["last_interaction"])
        
        rel.interaction_count = data.get("interaction_count", 0)
        rel.is_exclusive = data.get("is_exclusive", False)
        rel.is_public = data.get("is_public", True)
        rel.notes = data.get("notes", "")
        
        return rel


# =============================================================================
# FACTION REPUTATION
# =============================================================================

@dataclass
class FactionReputation:
    """Reputation with a faction."""
    faction_id: str
    faction_name: str
    
    # Reputation (-100 to 100)
    reputation: int = 0
    
    # Tracking
    actions_positive: int = 0
    actions_negative: int = 0
    
    def get_level(self) -> ReputationLevel:
        """Get reputation level."""
        if self.reputation <= -75:
            return ReputationLevel.HATED
        elif self.reputation <= -50:
            return ReputationLevel.HOSTILE
        elif self.reputation <= -25:
            return ReputationLevel.UNFRIENDLY
        elif self.reputation <= 24:
            return ReputationLevel.NEUTRAL
        elif self.reputation <= 49:
            return ReputationLevel.FRIENDLY
        elif self.reputation <= 74:
            return ReputationLevel.HONORED
        else:
            return ReputationLevel.REVERED
    
    def modify(self, amount: int) -> Tuple[int, bool]:
        """
        Modify reputation.
        Returns (new_value, level_changed).
        """
        old_level = self.get_level()
        self.reputation = max(-100, min(100, self.reputation + amount))
        
        if amount > 0:
            self.actions_positive += 1
        elif amount < 0:
            self.actions_negative += 1
        
        new_level = self.get_level()
        return self.reputation, old_level != new_level
    
    def to_dict(self) -> dict:
        return {
            "faction_id": self.faction_id,
            "faction_name": self.faction_name,
            "reputation": self.reputation,
            "actions_positive": self.actions_positive,
            "actions_negative": self.actions_negative,
        }
    
    @classmethod
    def from_dict(cls, data: dict) -> "FactionReputation":
        rep = cls(
            faction_id=data["faction_id"],
            faction_name=data["faction_name"],
        )
        rep.reputation = data.get("reputation", 0)
        rep.actions_positive = data.get("actions_positive", 0)
        rep.actions_negative = data.get("actions_negative", 0)
        return rep


# =============================================================================
# HAREM SYSTEM
# =============================================================================

@dataclass
class HaremMember:
    """A member of a harem."""
    member_dbref: str
    member_name: str
    
    # Position
    rank: int = 0                # 0 = lowest, higher = more important
    title: str = ""              # "First Wife", "Concubine", etc.
    
    # Stats
    favor: int = 50              # Owner's favor (0-100)
    jealousy: int = 0            # Jealousy of other members (0-100)
    
    # Dates
    added_date: Optional[datetime] = None
    
    def to_dict(self) -> dict:
        return {
            "member_dbref": self.member_dbref,
            "member_name": self.member_name,
            "rank": self.rank,
            "title": self.title,
            "favor": self.favor,
            "jealousy": self.jealousy,
            "added_date": self.added_date.isoformat() if self.added_date else None,
        }
    
    @classmethod
    def from_dict(cls, data: dict) -> "HaremMember":
        member = cls(
            member_dbref=data["member_dbref"],
            member_name=data["member_name"],
        )
        member.rank = data.get("rank", 0)
        member.title = data.get("title", "")
        member.favor = data.get("favor", 50)
        member.jealousy = data.get("jealousy", 0)
        
        if data.get("added_date"):
            member.added_date = datetime.fromisoformat(data["added_date"])
        
        return member


@dataclass
class Harem:
    """A collection of romantic/sexual partners."""
    owner_dbref: str
    owner_name: str
    
    # Name for the harem
    name: str = "Harem"
    
    # Members
    members: List[HaremMember] = field(default_factory=list)
    
    # Settings
    max_size: int = 10
    hierarchy_matters: bool = True
    
    def add_member(self, dbref: str, name: str, rank: int = 0, title: str = "") -> Tuple[bool, str]:
        """Add a member to the harem."""
        if len(self.members) >= self.max_size:
            return False, "Harem is full."
        
        if any(m.member_dbref == dbref for m in self.members):
            return False, f"{name} is already in the harem."
        
        member = HaremMember(
            member_dbref=dbref,
            member_name=name,
            rank=rank,
            title=title,
            added_date=datetime.now(),
        )
        self.members.append(member)
        
        # Increase jealousy in other members
        for m in self.members:
            if m.member_dbref != dbref:
                m.jealousy = min(100, m.jealousy + 10)
        
        return True, f"{name} has been added to the harem."
    
    def remove_member(self, dbref: str) -> Tuple[bool, str]:
        """Remove a member from the harem."""
        for i, m in enumerate(self.members):
            if m.member_dbref == dbref:
                name = m.member_name
                self.members.pop(i)
                return True, f"{name} has been removed from the harem."
        
        return False, "Member not found."
    
    def get_member(self, dbref: str) -> Optional[HaremMember]:
        """Get a member by dbref."""
        for m in self.members:
            if m.member_dbref == dbref:
                return m
        return None
    
    def set_rank(self, dbref: str, new_rank: int) -> str:
        """Set a member's rank."""
        member = self.get_member(dbref)
        if not member:
            return "Member not found."
        
        old_rank = member.rank
        member.rank = new_rank
        
        # Adjust jealousy based on rank changes
        if new_rank > old_rank:
            for m in self.members:
                if m.member_dbref != dbref and m.rank <= new_rank:
                    m.jealousy = min(100, m.jealousy + 15)
        
        return f"{member.member_name}'s rank changed to {new_rank}."
    
    def modify_favor(self, dbref: str, amount: int) -> str:
        """Modify favor for a member."""
        member = self.get_member(dbref)
        if not member:
            return "Member not found."
        
        member.favor = max(0, min(100, member.favor + amount))
        
        # Favor changes cause jealousy
        if amount > 0:
            for m in self.members:
                if m.member_dbref != dbref:
                    m.jealousy = min(100, m.jealousy + amount // 2)
        
        return f"{member.member_name}'s favor is now {member.favor}."
    
    def get_ranked_list(self) -> List[HaremMember]:
        """Get members sorted by rank (highest first)."""
        return sorted(self.members, key=lambda m: m.rank, reverse=True)
    
    def get_display(self) -> str:
        """Get display of harem."""
        if not self.members:
            return f"{self.name}: Empty"
        
        lines = [f"=== {self.name} ==="]
        
        for m in self.get_ranked_list():
            title_str = f" ({m.title})" if m.title else ""
            lines.append(f"  [{m.rank}] {m.member_name}{title_str} - Favor: {m.favor}")
        
        return "\n".join(lines)
    
    def to_dict(self) -> dict:
        return {
            "owner_dbref": self.owner_dbref,
            "owner_name": self.owner_name,
            "name": self.name,
            "members": [m.to_dict() for m in self.members],
            "max_size": self.max_size,
            "hierarchy_matters": self.hierarchy_matters,
        }
    
    @classmethod
    def from_dict(cls, data: dict) -> "Harem":
        harem = cls(
            owner_dbref=data["owner_dbref"],
            owner_name=data["owner_name"],
        )
        harem.name = data.get("name", "Harem")
        harem.members = [HaremMember.from_dict(m) for m in data.get("members", [])]
        harem.max_size = data.get("max_size", 10)
        harem.hierarchy_matters = data.get("hierarchy_matters", True)
        return harem


# =============================================================================
# RELATIONSHIP MANAGER
# =============================================================================

class RelationshipManager:
    """
    Manages relationships and reputation.
    """
    
    @staticmethod
    def generate_id() -> str:
        """Generate unique ID."""
        import random
        timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
        rand = random.randint(1000, 9999)
        return f"REL-{timestamp}-{rand}"
    
    @staticmethod
    def create_relationship(
        char_a,
        char_b,
        relationship_type: RelationshipType,
        initial_affection: int = 50,
        initial_trust: int = 50,
    ) -> Relationship:
        """Create a new relationship between two characters."""
        rel = Relationship(
            relationship_id=RelationshipManager.generate_id(),
            character_a_dbref=char_a.dbref,
            character_a_name=char_a.key,
            character_b_dbref=char_b.dbref,
            character_b_name=char_b.key,
            relationship_type=relationship_type,
            affection_a_to_b=initial_affection,
            affection_b_to_a=initial_affection,
            trust_a_to_b=initial_trust,
            trust_b_to_a=initial_trust,
            established_date=datetime.now(),
        )
        
        return rel
    
    @staticmethod
    def upgrade_relationship(
        relationship: Relationship,
        new_type: RelationshipType,
    ) -> str:
        """Upgrade relationship to a new type."""
        old_type = relationship.relationship_type
        relationship.relationship_type = new_type
        
        return f"Relationship upgraded from {old_type.value} to {new_type.value}."
    
    @staticmethod
    def break_relationship(relationship: Relationship, reason: str = "") -> str:
        """End a relationship."""
        relationship.status = RelationshipStatus.BROKEN
        relationship.notes = reason
        
        return f"The relationship between {relationship.character_a_name} and {relationship.character_b_name} has ended."


# =============================================================================
# RELATIONSHIP MIXIN
# =============================================================================

class RelationshipMixin:
    """
    Mixin for characters with relationships.
    """
    
    @property
    def relationships(self) -> Dict[str, Relationship]:
        """Get all relationships."""
        data = self.attributes.get("relationships", {})
        return {k: Relationship.from_dict(v) for k, v in data.items()}
    
    def save_relationship(self, relationship: Relationship) -> None:
        """Save a relationship."""
        rels = self.attributes.get("relationships", {})
        rels[relationship.relationship_id] = relationship.to_dict()
        self.attributes.add("relationships", rels)
    
    def get_relationship_with(self, other_dbref: str) -> Optional[Relationship]:
        """Get relationship with another character."""
        for rel in self.relationships.values():
            if rel.character_a_dbref == other_dbref or rel.character_b_dbref == other_dbref:
                return rel
        return None
    
    def get_relationships_by_type(self, rel_type: RelationshipType) -> List[Relationship]:
        """Get all relationships of a type."""
        return [r for r in self.relationships.values() if r.relationship_type == rel_type]
    
    @property
    def faction_reputations(self) -> Dict[str, FactionReputation]:
        """Get faction reputations."""
        data = self.attributes.get("faction_reputations", {})
        return {k: FactionReputation.from_dict(v) for k, v in data.items()}
    
    def get_reputation(self, faction_id: str) -> int:
        """Get reputation with a faction."""
        reps = self.faction_reputations
        if faction_id in reps:
            return reps[faction_id].reputation
        return 0
    
    def modify_reputation(self, faction_id: str, faction_name: str, amount: int) -> Tuple[int, bool]:
        """Modify reputation with a faction."""
        reps = self.attributes.get("faction_reputations", {})
        
        if faction_id not in reps:
            reps[faction_id] = FactionReputation(faction_id, faction_name).to_dict()
        
        rep = FactionReputation.from_dict(reps[faction_id])
        new_value, level_changed = rep.modify(amount)
        reps[faction_id] = rep.to_dict()
        
        self.attributes.add("faction_reputations", reps)
        
        return new_value, level_changed
    
    @property
    def harem(self) -> Optional[Harem]:
        """Get harem if owner has one."""
        data = self.attributes.get("harem")
        if data:
            return Harem.from_dict(data)
        return None
    
    @harem.setter
    def harem(self, harem: Optional[Harem]):
        """Set harem."""
        if harem:
            self.attributes.add("harem", harem.to_dict())
        else:
            self.attributes.remove("harem")
    
    def create_harem(self, name: str = "Harem") -> Harem:
        """Create a new harem."""
        harem = Harem(
            owner_dbref=self.dbref,
            owner_name=self.key,
            name=name,
        )
        self.harem = harem
        return harem


__all__ = [
    "RelationshipType",
    "RelationshipStatus",
    "ReputationLevel",
    "Relationship",
    "FactionReputation",
    "HaremMember",
    "Harem",
    "RelationshipManager",
    "RelationshipMixin",
]
