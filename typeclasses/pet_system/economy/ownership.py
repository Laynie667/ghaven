"""
Ownership System
================

Owner/property relationships:
- Claiming and collaring
- Ownership records
- Owner permissions
- Property management
"""

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any, Tuple, Set
from enum import Enum
from datetime import datetime


# =============================================================================
# ENUMS
# =============================================================================

class OwnershipType(Enum):
    """Types of ownership relationships."""
    PET = "pet"               # Pet ownership (playful)
    SLAVE = "slave"           # Full slavery
    SERVANT = "servant"       # Contracted service
    PROPERTY = "property"     # Object-level ownership
    BREEDING_STOCK = "breeding_stock"  # For breeding purposes
    TEMPORARY = "temporary"   # Time-limited ownership


class OwnerPermission(Enum):
    """Permissions an owner has over property."""
    COMMAND = "command"           # Give orders
    PUNISH = "punish"            # Physical punishment
    REWARD = "reward"            # Rewards
    DRESS = "dress"              # Control clothing
    RESTRAIN = "restrain"        # Use restraints
    BREED = "breed"              # Breeding rights
    LOAN = "loan"                # Loan to others
    SELL = "sell"                # Sell/transfer
    RENAME = "rename"            # Change name
    MODIFY = "modify"            # Body modifications
    USE_SEXUALLY = "use_sexually"  # Sexual use
    SHARE = "share"              # Share with others


class CollarType(Enum):
    """Types of ownership collars."""
    BASIC = "basic"              # Simple collar
    TRAINING = "training"        # Training collar
    PERMANENT = "permanent"      # Cannot be removed
    BREEDING = "breeding"        # Marks as breeding stock
    DECORATIVE = "decorative"    # Fancy/display
    PUNISHMENT = "punishment"    # Shock/control collar
    TRACKING = "tracking"        # GPS/tracking


# =============================================================================
# OWNERSHIP COLLAR
# =============================================================================

@dataclass
class OwnershipCollar:
    """A collar marking ownership."""
    collar_id: str
    collar_type: CollarType = CollarType.BASIC
    
    # Owner info
    owner_dbref: str = ""
    owner_name: str = ""
    
    # Properties
    material: str = "leather"
    color: str = "black"
    
    # Inscription
    inscription: str = ""        # "Property of X"
    tag_text: str = ""          # On hanging tag
    
    # State
    is_locked: bool = False
    is_permanent: bool = False   # Cannot be removed even by owner
    
    # Special features
    has_leash_ring: bool = True
    has_bell: bool = False
    has_tracker: bool = False
    
    # Dates
    collared_date: Optional[datetime] = None
    
    def lock(self) -> str:
        """Lock the collar."""
        self.is_locked = True
        return "The collar locks with a click."
    
    def unlock(self) -> Tuple[bool, str]:
        """Attempt to unlock the collar."""
        if self.is_permanent:
            return False, "This collar cannot be removed."
        
        self.is_locked = False
        return True, "The collar unlocks."
    
    def get_description(self) -> str:
        """Get collar description."""
        parts = [f"A {self.color} {self.material} collar"]
        
        if self.inscription:
            parts.append(f'inscribed with "{self.inscription}"')
        
        features = []
        if self.has_leash_ring:
            features.append("a D-ring")
        if self.has_bell:
            features.append("a small bell")
        if self.has_tracker:
            features.append("a tracking device")
        
        if features:
            parts.append(f"with {', '.join(features)}")
        
        if self.is_locked:
            parts.append("(locked)")
        
        return " ".join(parts) + "."
    
    def to_dict(self) -> dict:
        return {
            "collar_id": self.collar_id,
            "collar_type": self.collar_type.value,
            "owner_dbref": self.owner_dbref,
            "owner_name": self.owner_name,
            "material": self.material,
            "color": self.color,
            "inscription": self.inscription,
            "tag_text": self.tag_text,
            "is_locked": self.is_locked,
            "is_permanent": self.is_permanent,
            "has_leash_ring": self.has_leash_ring,
            "has_bell": self.has_bell,
            "has_tracker": self.has_tracker,
            "collared_date": self.collared_date.isoformat() if self.collared_date else None,
        }
    
    @classmethod
    def from_dict(cls, data: dict) -> "OwnershipCollar":
        collar = cls(collar_id=data["collar_id"])
        collar.collar_type = CollarType(data.get("collar_type", "basic"))
        collar.owner_dbref = data.get("owner_dbref", "")
        collar.owner_name = data.get("owner_name", "")
        collar.material = data.get("material", "leather")
        collar.color = data.get("color", "black")
        collar.inscription = data.get("inscription", "")
        collar.tag_text = data.get("tag_text", "")
        collar.is_locked = data.get("is_locked", False)
        collar.is_permanent = data.get("is_permanent", False)
        collar.has_leash_ring = data.get("has_leash_ring", True)
        collar.has_bell = data.get("has_bell", False)
        collar.has_tracker = data.get("has_tracker", False)
        
        if data.get("collared_date"):
            collar.collared_date = datetime.fromisoformat(data["collared_date"])
        
        return collar


# =============================================================================
# OWNERSHIP RECORD
# =============================================================================

@dataclass
class OwnershipRecord:
    """Record of an ownership relationship."""
    record_id: str
    
    # Parties
    owner_dbref: str = ""
    owner_name: str = ""
    property_dbref: str = ""
    property_name: str = ""
    
    # Type and terms
    ownership_type: OwnershipType = OwnershipType.SLAVE
    permissions: Set[str] = field(default_factory=set)  # OwnerPermission values
    
    # Dates
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None  # For temporary ownership
    
    # Collar
    collar: Optional[OwnershipCollar] = None
    
    # Property name (renamed)
    property_title: str = ""     # "slave", "pet", etc.
    given_name: str = ""         # Name given by owner
    
    # Restrictions/rules
    rules: List[str] = field(default_factory=list)
    
    # Stats
    times_punished: int = 0
    times_rewarded: int = 0
    times_bred: int = 0
    times_loaned: int = 0
    
    # Status
    is_active: bool = True
    
    def has_permission(self, permission: OwnerPermission) -> bool:
        """Check if owner has a permission."""
        return permission.value in self.permissions
    
    def grant_permission(self, permission: OwnerPermission) -> None:
        """Grant a permission."""
        self.permissions.add(permission.value)
    
    def revoke_permission(self, permission: OwnerPermission) -> None:
        """Revoke a permission."""
        self.permissions.discard(permission.value)
    
    def add_rule(self, rule: str) -> None:
        """Add a rule for the property."""
        if rule not in self.rules:
            self.rules.append(rule)
    
    def remove_rule(self, rule: str) -> bool:
        """Remove a rule."""
        if rule in self.rules:
            self.rules.remove(rule)
            return True
        return False
    
    def is_temporary(self) -> bool:
        """Check if ownership is temporary."""
        return self.end_date is not None
    
    def is_expired(self) -> bool:
        """Check if temporary ownership has expired."""
        if self.end_date and datetime.now() >= self.end_date:
            return True
        return False
    
    def get_display_name(self) -> str:
        """Get display name for property."""
        if self.given_name:
            return self.given_name
        return self.property_name
    
    def get_summary(self) -> str:
        """Get summary of ownership."""
        lines = [
            f"Owner: {self.owner_name}",
            f"Property: {self.get_display_name()} ({self.property_title})",
            f"Type: {self.ownership_type.value}",
        ]
        
        if self.start_date:
            lines.append(f"Since: {self.start_date.strftime('%Y-%m-%d')}")
        
        if self.is_temporary():
            if self.is_expired():
                lines.append("Status: EXPIRED")
            else:
                lines.append(f"Until: {self.end_date.strftime('%Y-%m-%d')}")
        
        if self.rules:
            lines.append(f"Rules: {len(self.rules)}")
        
        return "\n".join(lines)
    
    def to_dict(self) -> dict:
        return {
            "record_id": self.record_id,
            "owner_dbref": self.owner_dbref,
            "owner_name": self.owner_name,
            "property_dbref": self.property_dbref,
            "property_name": self.property_name,
            "ownership_type": self.ownership_type.value,
            "permissions": list(self.permissions),
            "start_date": self.start_date.isoformat() if self.start_date else None,
            "end_date": self.end_date.isoformat() if self.end_date else None,
            "collar": self.collar.to_dict() if self.collar else None,
            "property_title": self.property_title,
            "given_name": self.given_name,
            "rules": self.rules,
            "times_punished": self.times_punished,
            "times_rewarded": self.times_rewarded,
            "times_bred": self.times_bred,
            "times_loaned": self.times_loaned,
            "is_active": self.is_active,
        }
    
    @classmethod
    def from_dict(cls, data: dict) -> "OwnershipRecord":
        record = cls(record_id=data["record_id"])
        record.owner_dbref = data.get("owner_dbref", "")
        record.owner_name = data.get("owner_name", "")
        record.property_dbref = data.get("property_dbref", "")
        record.property_name = data.get("property_name", "")
        record.ownership_type = OwnershipType(data.get("ownership_type", "slave"))
        record.permissions = set(data.get("permissions", []))
        
        if data.get("start_date"):
            record.start_date = datetime.fromisoformat(data["start_date"])
        if data.get("end_date"):
            record.end_date = datetime.fromisoformat(data["end_date"])
        if data.get("collar"):
            record.collar = OwnershipCollar.from_dict(data["collar"])
        
        record.property_title = data.get("property_title", "")
        record.given_name = data.get("given_name", "")
        record.rules = data.get("rules", [])
        record.times_punished = data.get("times_punished", 0)
        record.times_rewarded = data.get("times_rewarded", 0)
        record.times_bred = data.get("times_bred", 0)
        record.times_loaned = data.get("times_loaned", 0)
        record.is_active = data.get("is_active", True)
        
        return record


# =============================================================================
# OWNERSHIP SYSTEM
# =============================================================================

class OwnershipSystem:
    """
    Manages ownership relationships.
    """
    
    # Default permissions by ownership type
    DEFAULT_PERMISSIONS = {
        OwnershipType.PET: [
            OwnerPermission.COMMAND,
            OwnerPermission.REWARD,
            OwnerPermission.DRESS,
            OwnerPermission.RESTRAIN,
        ],
        OwnershipType.SLAVE: [
            OwnerPermission.COMMAND,
            OwnerPermission.PUNISH,
            OwnerPermission.REWARD,
            OwnerPermission.DRESS,
            OwnerPermission.RESTRAIN,
            OwnerPermission.BREED,
            OwnerPermission.LOAN,
            OwnerPermission.USE_SEXUALLY,
            OwnerPermission.SHARE,
        ],
        OwnershipType.SERVANT: [
            OwnerPermission.COMMAND,
            OwnerPermission.REWARD,
            OwnerPermission.DRESS,
        ],
        OwnershipType.PROPERTY: [
            OwnerPermission.COMMAND,
            OwnerPermission.PUNISH,
            OwnerPermission.REWARD,
            OwnerPermission.DRESS,
            OwnerPermission.RESTRAIN,
            OwnerPermission.BREED,
            OwnerPermission.LOAN,
            OwnerPermission.SELL,
            OwnerPermission.RENAME,
            OwnerPermission.MODIFY,
            OwnerPermission.USE_SEXUALLY,
            OwnerPermission.SHARE,
        ],
        OwnershipType.BREEDING_STOCK: [
            OwnerPermission.COMMAND,
            OwnerPermission.RESTRAIN,
            OwnerPermission.BREED,
            OwnerPermission.LOAN,
            OwnerPermission.SELL,
        ],
        OwnershipType.TEMPORARY: [
            OwnerPermission.COMMAND,
            OwnerPermission.RESTRAIN,
        ],
    }
    
    @staticmethod
    def generate_id() -> str:
        """Generate unique ID."""
        import random
        timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
        rand = random.randint(1000, 9999)
        return f"OWN-{timestamp}-{rand}"
    
    @staticmethod
    def create_ownership(
        owner,
        property_obj,
        ownership_type: OwnershipType,
        duration_days: Optional[int] = None,
        collar_type: CollarType = CollarType.BASIC,
        given_name: str = "",
    ) -> Tuple[bool, str, Optional[OwnershipRecord]]:
        """
        Create a new ownership relationship.
        """
        # Check if property is already owned
        existing = getattr(property_obj, 'ownership_record', None)
        if existing and existing.is_active:
            return False, f"{property_obj.key} is already owned by {existing.owner_name}.", None
        
        # Create record
        record = OwnershipRecord(
            record_id=OwnershipSystem.generate_id(),
            owner_dbref=owner.dbref,
            owner_name=owner.key,
            property_dbref=property_obj.dbref,
            property_name=property_obj.key,
            ownership_type=ownership_type,
            start_date=datetime.now(),
            property_title=ownership_type.value,
            given_name=given_name,
        )
        
        # Set end date for temporary
        if duration_days:
            from datetime import timedelta
            record.end_date = datetime.now() + timedelta(days=duration_days)
        
        # Grant default permissions
        default_perms = OwnershipSystem.DEFAULT_PERMISSIONS.get(ownership_type, [])
        for perm in default_perms:
            record.grant_permission(perm)
        
        # Create collar
        collar = OwnershipCollar(
            collar_id=f"COL-{record.record_id}",
            collar_type=collar_type,
            owner_dbref=owner.dbref,
            owner_name=owner.key,
            collared_date=datetime.now(),
            inscription=f"Property of {owner.key}",
        )
        record.collar = collar
        
        return True, f"{property_obj.key} is now owned by {owner.key}.", record
    
    @staticmethod
    def transfer_ownership(
        record: OwnershipRecord,
        new_owner,
        transfer_type: str = "sale",
    ) -> Tuple[bool, str]:
        """
        Transfer ownership to a new owner.
        """
        if not record.is_active:
            return False, "This ownership is no longer active."
        
        old_owner_name = record.owner_name
        
        # Update record
        record.owner_dbref = new_owner.dbref
        record.owner_name = new_owner.key
        
        # Update collar
        if record.collar:
            record.collar.owner_dbref = new_owner.dbref
            record.collar.owner_name = new_owner.key
            record.collar.inscription = f"Property of {new_owner.key}"
        
        return True, f"Ownership transferred from {old_owner_name} to {new_owner.key}."
    
    @staticmethod
    def release_ownership(
        record: OwnershipRecord,
        reason: str = "",
    ) -> Tuple[bool, str]:
        """
        Release/free the property.
        """
        if not record.is_active:
            return False, "This ownership is no longer active."
        
        record.is_active = False
        
        return True, f"{record.property_name} has been released from ownership."
    
    @staticmethod
    def check_permission(
        record: OwnershipRecord,
        actor_dbref: str,
        permission: OwnerPermission,
    ) -> bool:
        """
        Check if actor has permission over the property.
        """
        if not record.is_active:
            return False
        
        if record.is_expired():
            return False
        
        # Owner always has their granted permissions
        if actor_dbref == record.owner_dbref:
            return record.has_permission(permission)
        
        return False


# =============================================================================
# OWNERSHIP MIXINS
# =============================================================================

class OwnerMixin:
    """
    Mixin for characters that can own others.
    """
    
    @property
    def owned_properties(self) -> List[OwnershipRecord]:
        """Get list of owned properties."""
        data = self.attributes.get("owned_properties", [])
        return [OwnershipRecord.from_dict(d) for d in data if d.get("is_active", True)]
    
    def add_property(self, record: OwnershipRecord) -> None:
        """Add an ownership record."""
        properties = self.attributes.get("owned_properties", [])
        properties.append(record.to_dict())
        self.attributes.add("owned_properties", properties)
    
    def remove_property(self, property_dbref: str) -> Optional[OwnershipRecord]:
        """Remove ownership of a property."""
        properties = self.attributes.get("owned_properties", [])
        
        for i, data in enumerate(properties):
            if data.get("property_dbref") == property_dbref:
                record = OwnershipRecord.from_dict(data)
                record.is_active = False
                properties[i] = record.to_dict()
                self.attributes.add("owned_properties", properties)
                return record
        
        return None
    
    def get_property(self, property_dbref: str) -> Optional[OwnershipRecord]:
        """Get ownership record for a property."""
        for record in self.owned_properties:
            if record.property_dbref == property_dbref:
                return record
        return None
    
    def owns(self, target) -> bool:
        """Check if this character owns target."""
        record = self.get_property(target.dbref)
        return record is not None and record.is_active
    
    def can_do_to_property(self, target, permission: OwnerPermission) -> bool:
        """Check if can perform action on owned property."""
        record = self.get_property(target.dbref)
        if not record:
            return False
        return OwnershipSystem.check_permission(record, self.dbref, permission)


class PropertyMixin:
    """
    Mixin for characters that can be owned.
    """
    
    @property
    def ownership_record(self) -> Optional[OwnershipRecord]:
        """Get ownership record if owned."""
        data = self.attributes.get("ownership_record")
        if data:
            record = OwnershipRecord.from_dict(data)
            if record.is_active and not record.is_expired():
                return record
        return None
    
    @ownership_record.setter
    def ownership_record(self, record: Optional[OwnershipRecord]):
        """Set ownership record."""
        if record:
            self.attributes.add("ownership_record", record.to_dict())
        else:
            self.attributes.remove("ownership_record")
    
    def is_owned(self) -> bool:
        """Check if currently owned."""
        record = self.ownership_record
        return record is not None and record.is_active
    
    def get_owner_dbref(self) -> str:
        """Get owner's dbref if owned."""
        record = self.ownership_record
        return record.owner_dbref if record else ""
    
    def get_owner_name(self) -> str:
        """Get owner's name if owned."""
        record = self.ownership_record
        return record.owner_name if record else ""
    
    def get_collar(self) -> Optional[OwnershipCollar]:
        """Get ownership collar if any."""
        record = self.ownership_record
        return record.collar if record else None
    
    def get_owned_name(self) -> str:
        """Get name as given by owner, or real name."""
        record = self.ownership_record
        if record and record.given_name:
            return record.given_name
        return self.key
    
    def get_ownership_desc(self) -> str:
        """Get description of ownership status."""
        record = self.ownership_record
        if not record:
            return ""
        
        collar_desc = record.collar.get_description() if record.collar else ""
        
        return f"Owned by {record.owner_name}. {collar_desc}"


__all__ = [
    "OwnershipType",
    "OwnerPermission",
    "CollarType",
    "OwnershipCollar",
    "OwnershipRecord",
    "OwnershipSystem",
    "OwnerMixin",
    "PropertyMixin",
]
