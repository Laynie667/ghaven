"""
Position System for Gilderhaven
================================

Tracks character positions (standing, sitting, kneeling, lying, etc.)
and how they relate to furniture and other characters.

Positions are stored on characters and affect:
- Room descriptions (how others see you)
- Available actions
- Interactions with furniture
- Paired/group activities

Data Storage:
    character.db.position = {
        "pose": "sitting",           # Current position type
        "furniture_id": 123,         # Furniture being used (or None)
        "furniture_slot": "seat_1",  # Which slot on furniture
        "partner_ids": [456],        # Other characters involved
        "custom_desc": "...",        # Optional custom description
        "flags": ["restrained"],     # Position flags
    }

Usage:
    from world.positions import (
        get_position, set_position, clear_position,
        get_position_display, is_standing, can_move
    )
    
    # Set a simple position
    set_position(character, "sitting")
    
    # Set position on furniture
    set_position(character, "sitting", furniture=chair, slot="seat")
    
    # Set paired position
    set_position(character, "cuddling", partner=other_char)
    
    # Check if can move
    if can_move(character):
        character.move_to(destination)
"""

import time
from evennia.utils import logger


# =============================================================================
# Position Definitions
# =============================================================================

POSITIONS = {
    # Basic positions (no furniture required)
    "standing": {
        "name": "standing",
        "desc": "is standing here",
        "category": "basic",
        "mobile": True,
        "requires_furniture": False,
    },
    "sitting": {
        "name": "sitting",
        "desc": "is sitting",
        "category": "basic",
        "mobile": False,
        "requires_furniture": False,
        "ground_desc": "is sitting on the ground",
    },
    "kneeling": {
        "name": "kneeling",
        "desc": "is kneeling",
        "category": "basic",
        "mobile": False,
        "requires_furniture": False,
    },
    "lying": {
        "name": "lying",
        "desc": "is lying down",
        "category": "basic",
        "mobile": False,
        "requires_furniture": False,
        "ground_desc": "is lying on the ground",
    },
    "crouching": {
        "name": "crouching", 
        "desc": "is crouching",
        "category": "basic",
        "mobile": True,
        "requires_furniture": False,
    },
    "leaning": {
        "name": "leaning",
        "desc": "is leaning against the wall",
        "category": "basic",
        "mobile": False,
        "requires_furniture": False,
    },
    
    # Furniture positions
    "seated": {
        "name": "seated",
        "desc": "is seated on {furniture}",
        "category": "furniture",
        "mobile": False,
        "requires_furniture": True,
    },
    "lounging": {
        "name": "lounging",
        "desc": "is lounging on {furniture}",
        "category": "furniture",
        "mobile": False,
        "requires_furniture": True,
    },
    "reclining": {
        "name": "reclining",
        "desc": "is reclining on {furniture}",
        "category": "furniture", 
        "mobile": False,
        "requires_furniture": True,
    },
    "sleeping": {
        "name": "sleeping",
        "desc": "is sleeping on {furniture}",
        "category": "furniture",
        "mobile": False,
        "requires_furniture": True,
        "flags": ["unconscious"],
    },
    
    # Social positions
    "cuddling": {
        "name": "cuddling",
        "desc": "is cuddling with {partner}",
        "category": "social",
        "mobile": False,
        "requires_partner": True,
    },
    "embracing": {
        "name": "embracing",
        "desc": "is embracing {partner}",
        "category": "social",
        "mobile": False,
        "requires_partner": True,
    },
    "holding_hands": {
        "name": "holding hands",
        "desc": "is holding hands with {partner}",
        "category": "social",
        "mobile": True,
        "requires_partner": True,
    },
    "lap_sitting": {
        "name": "sitting in lap",
        "desc": "is sitting in {partner}'s lap",
        "category": "social",
        "mobile": False,
        "requires_partner": True,
    },
    "lap_holding": {
        "name": "holding in lap",
        "desc": "has {partner} sitting in their lap",
        "category": "social",
        "mobile": False,
        "requires_partner": True,
    },
    
    # Submissive positions
    "kneeling_before": {
        "name": "kneeling before",
        "desc": "is kneeling before {partner}",
        "category": "submissive",
        "mobile": False,
        "requires_partner": True,
        "flags": ["submissive"],
    },
    "at_feet": {
        "name": "at feet",
        "desc": "is sitting at {partner}'s feet",
        "category": "submissive",
        "mobile": False,
        "requires_partner": True,
        "flags": ["submissive"],
    },
    "presenting": {
        "name": "presenting",
        "desc": "is presenting themselves",
        "category": "submissive",
        "mobile": False,
        "requires_furniture": False,
        "flags": ["submissive", "exposed", "adult"],
    },
    
    # Restrained positions (furniture-based)
    "bound_standing": {
        "name": "bound standing",
        "desc": "is bound standing to {furniture}",
        "category": "bondage",
        "mobile": False,
        "requires_furniture": True,
        "flags": ["restrained", "adult"],
    },
    "bound_kneeling": {
        "name": "bound kneeling",
        "desc": "is bound kneeling at {furniture}",
        "category": "bondage",
        "mobile": False,
        "requires_furniture": True,
        "flags": ["restrained", "adult"],
    },
    "bound_lying": {
        "name": "bound lying",
        "desc": "is bound to {furniture}",
        "category": "bondage",
        "mobile": False,
        "requires_furniture": True,
        "flags": ["restrained", "adult"],
    },
    "bound_bent": {
        "name": "bound bent over",
        "desc": "is bound bent over {furniture}",
        "category": "bondage",
        "mobile": False,
        "requires_furniture": True,
        "flags": ["restrained", "exposed", "adult"],
    },
    "suspended": {
        "name": "suspended",
        "desc": "is suspended from {furniture}",
        "category": "bondage",
        "mobile": False,
        "requires_furniture": True,
        "flags": ["restrained", "adult"],
    },
    "displayed": {
        "name": "displayed",
        "desc": "is displayed on {furniture}",
        "category": "bondage",
        "mobile": False,
        "requires_furniture": True,
        "flags": ["restrained", "exposed", "adult"],
    },
    
    # Intimate positions
    "straddling": {
        "name": "straddling",
        "desc": "is straddling {partner}",
        "category": "intimate",
        "mobile": False,
        "requires_partner": True,
        "flags": ["intimate", "adult"],
    },
    "mounted": {
        "name": "mounted",
        "desc": "is mounted by {partner}",
        "category": "intimate",
        "mobile": False,
        "requires_partner": True,
        "flags": ["intimate", "adult"],
    },
    "beneath": {
        "name": "beneath",
        "desc": "is lying beneath {partner}",
        "category": "intimate",
        "mobile": False,
        "requires_partner": True,
        "flags": ["intimate", "adult"],
    },
    "atop": {
        "name": "atop",
        "desc": "is atop {partner}",
        "category": "intimate",
        "mobile": False,
        "requires_partner": True,
        "flags": ["intimate", "adult"],
    },
    "entwined": {
        "name": "entwined",
        "desc": "is entwined with {partner}",
        "category": "intimate",
        "mobile": False,
        "requires_partner": True,
        "flags": ["intimate", "adult"],
    },
    "servicing": {
        "name": "servicing",
        "desc": "is servicing {partner}",
        "category": "intimate",
        "mobile": False,
        "requires_partner": True,
        "flags": ["intimate", "submissive", "adult"],
    },
    "being_serviced": {
        "name": "being serviced",
        "desc": "is being serviced by {partner}",
        "category": "intimate",
        "mobile": False,
        "requires_partner": True,
        "flags": ["intimate", "adult"],
    },
    
    # Service positions
    "under_desk": {
        "name": "under desk",
        "desc": "is hidden beneath {furniture}",
        "category": "service",
        "mobile": False,
        "requires_furniture": True,
        "flags": ["submissive", "hidden", "adult"],
    },
    "waiting": {
        "name": "waiting",
        "desc": "is waiting attentively, hands clasped behind their back",
        "category": "service",
        "mobile": False,
        "requires_furniture": False,
        "flags": ["submissive"],
    },
    "collar_presented": {
        "name": "presenting collar",
        "desc": "is kneeling with neck bared, offering themselves",
        "category": "service",
        "mobile": False,
        "requires_furniture": False,
        "flags": ["submissive", "adult"],
    },
    "leashed": {
        "name": "leashed",
        "desc": "is leashed to {partner}",
        "category": "service",
        "mobile": True,  # Can move, but follows
        "requires_partner": True,
        "flags": ["submissive", "adult"],
    },
    "leash_holding": {
        "name": "holding leash",
        "desc": "is holding {partner}'s leash",
        "category": "service",
        "mobile": True,
        "requires_partner": True,
        "flags": ["dominant", "adult"],
    },
    "heel": {
        "name": "at heel",
        "desc": "is following at {partner}'s heel",
        "category": "service",
        "mobile": True,
        "requires_partner": True,
        "flags": ["submissive", "adult"],
    },
    
    # Display positions
    "displayed_as_art": {
        "name": "displayed as art",
        "desc": "is posed motionless on {furniture}, displayed as art",
        "category": "display",
        "mobile": False,
        "requires_furniture": True,
        "flags": ["submissive", "exposed", "adult"],
    },
    "displayed_in_case": {
        "name": "displayed in case",
        "desc": "is on display inside {furniture}",
        "category": "display",
        "mobile": False,
        "requires_furniture": True,
        "flags": ["restrained", "exposed", "adult"],
    },
    "pedestal": {
        "name": "on pedestal",
        "desc": "is standing on {furniture}, on display",
        "category": "display",
        "mobile": False,
        "requires_furniture": True,
        "flags": ["exposed", "adult"],
    },
    
    # Examination positions
    "examination": {
        "name": "being examined",
        "desc": "is laid out on {furniture} for examination",
        "category": "examination",
        "mobile": False,
        "requires_furniture": True,
        "flags": ["submissive", "exposed", "adult"],
    },
    "inspection": {
        "name": "presenting for inspection",
        "desc": "is presenting themselves for inspection",
        "category": "examination",
        "mobile": False,
        "requires_furniture": False,
        "flags": ["submissive", "exposed", "adult"],
    },
    
    # Wall/fixture positions  
    "wall_pinned": {
        "name": "pinned to wall",
        "desc": "is pinned against the wall by {partner}",
        "category": "intimate",
        "mobile": False,
        "requires_partner": True,
        "flags": ["intimate", "adult"],
    },
    "wall_mounted": {
        "name": "wall mounted",
        "desc": "is mounted on the wall via {furniture}",
        "category": "bondage",
        "mobile": False,
        "requires_furniture": True,
        "flags": ["restrained", "exposed", "adult"],
    },
    "hooked": {
        "name": "hooked",
        "desc": "is secured to {furniture}",
        "category": "bondage",
        "mobile": False,
        "requires_furniture": True,
        "flags": ["restrained", "adult"],
    },
}


# Position categories for filtering
POSITION_CATEGORIES = {
    "basic": "Basic positions anyone can use",
    "furniture": "Positions requiring furniture",
    "social": "Positions with a partner",
    "submissive": "Submissive/service positions",
    "bondage": "Restrained positions (requires bondage furniture)",
    "intimate": "Intimate positions (adult)",
    "service": "Service and attendance positions",
    "display": "Display and exhibition positions",
    "examination": "Examination and inspection positions",
}


# =============================================================================
# Core Functions
# =============================================================================

def get_position(character):
    """
    Get character's current position data.
    
    Returns:
        dict: Position data or None if standing
    """
    return character.db.position


def get_position_type(character):
    """
    Get the position type string.
    
    Returns:
        str: Position type (e.g., "sitting", "kneeling") or "standing"
    """
    pos = character.db.position
    if not pos:
        return "standing"
    return pos.get("pose", "standing")


def get_position_info(position_type):
    """
    Get the definition for a position type.
    
    Returns:
        dict: Position definition or None
    """
    return POSITIONS.get(position_type)


def is_standing(character):
    """Check if character is standing (default position)."""
    pos = character.db.position
    return not pos or pos.get("pose") == "standing"


def is_mobile(character):
    """Check if character can move in their current position."""
    pos = character.db.position
    if not pos:
        return True
    
    pose = pos.get("pose", "standing")
    pos_info = POSITIONS.get(pose, {})
    
    # Check position mobility
    if not pos_info.get("mobile", True):
        return False
    
    # Check if restrained
    if "restrained" in pos.get("flags", []):
        return False
    
    return True


def can_move(character):
    """
    Check if character can move to another room.
    Same as is_mobile but with additional checks.
    """
    if not is_mobile(character):
        return False
    
    # Check if on furniture
    pos = character.db.position
    if pos and pos.get("furniture_id"):
        return False
    
    # Check if partnered with non-mobile position
    if pos and pos.get("partner_ids"):
        pose = pos.get("pose", "standing")
        pos_info = POSITIONS.get(pose, {})
        if not pos_info.get("mobile", True):
            return False
    
    return True


def has_flag(character, flag):
    """Check if character's position has a specific flag."""
    pos = character.db.position
    if not pos:
        return False
    return flag in pos.get("flags", [])


def is_restrained(character):
    """Check if character is restrained."""
    return has_flag(character, "restrained")


def is_exposed(character):
    """Check if character is in an exposed position."""
    return has_flag(character, "exposed")


# =============================================================================
# Position Management
# =============================================================================

def set_position(character, pose, furniture=None, slot=None, partner=None, 
                 custom_desc=None, flags=None, silent=False):
    """
    Set a character's position.
    
    Args:
        character: Character to set position for
        pose: Position type string (e.g., "sitting", "kneeling")
        furniture: Optional furniture object being used
        slot: Optional slot name on furniture
        partner: Optional partner character
        custom_desc: Optional custom description override
        flags: Optional additional flags
        silent: If True, don't send messages
    
    Returns:
        tuple: (success, message)
    """
    pos_info = POSITIONS.get(pose)
    if not pos_info:
        return False, f"Unknown position: {pose}"
    
    # Check requirements
    if pos_info.get("requires_furniture") and not furniture:
        return False, f"The '{pose}' position requires furniture."
    
    if pos_info.get("requires_partner") and not partner:
        return False, f"The '{pose}' position requires a partner."
    
    # Build position data
    position_data = {
        "pose": pose,
        "furniture_id": furniture.id if furniture else None,
        "furniture_slot": slot,
        "partner_ids": [partner.id] if partner else [],
        "custom_desc": custom_desc,
        "flags": list(pos_info.get("flags", [])),
        "set_at": time.time(),
    }
    
    # Add extra flags
    if flags:
        position_data["flags"].extend(flags)
    
    # Clear old position first
    old_pos = character.db.position
    if old_pos:
        _cleanup_old_position(character, old_pos)
    
    # Set new position
    character.db.position = position_data
    
    # Update furniture occupancy
    if furniture:
        _occupy_furniture(furniture, character, slot)
    
    # Update partner's position reference
    if partner:
        _link_partner(character, partner)
    
    # Send messages
    if not silent:
        desc = get_position_display(character)
        character.msg(f"You are now {desc}.")
        if character.location:
            character.location.msg_contents(
                f"|c{character.key}|n is now {desc}.",
                exclude=[character]
            )
    
    return True, f"Position set to {pose}."


def clear_position(character, silent=False):
    """
    Clear character's position (return to standing).
    
    Args:
        character: Character to clear position for
        silent: If True, don't send messages
    
    Returns:
        tuple: (success, message)
    """
    pos = character.db.position
    if not pos or pos.get("pose") == "standing":
        return True, "Already standing."
    
    # Check if restrained
    if "restrained" in pos.get("flags", []):
        return False, "You can't move - you're restrained!"
    
    # Cleanup old position
    _cleanup_old_position(character, pos)
    
    # Clear position
    character.db.position = None
    
    if not silent:
        character.msg("You stand up.")
        if character.location:
            character.location.msg_contents(
                f"|c{character.key}|n stands up.",
                exclude=[character]
            )
    
    return True, "Now standing."


def force_clear_position(character, silent=False):
    """
    Force clear position even if restrained.
    Use for admin commands or when furniture is destroyed.
    """
    pos = character.db.position
    if pos:
        _cleanup_old_position(character, pos)
    
    character.db.position = None
    
    if not silent:
        character.msg("You are released and stand up.")


# =============================================================================
# Display Functions
# =============================================================================

def get_position_display(character, viewer=None):
    """
    Get a display string for character's current position.
    
    Args:
        character: Character whose position to describe
        viewer: Optional - who is viewing (for perspective)
    
    Returns:
        str: Position description (e.g., "sitting on the wooden chair")
    """
    pos = character.db.position
    
    if not pos or pos.get("pose") == "standing":
        return "standing"
    
    pose = pos.get("pose", "standing")
    pos_info = POSITIONS.get(pose, {})
    
    # Use custom description if set
    if pos.get("custom_desc"):
        return pos["custom_desc"]
    
    desc = pos_info.get("desc", f"is {pose}")
    
    # Remove "is " prefix for return value
    if desc.startswith("is "):
        desc = desc[3:]
    
    # Substitute furniture name
    if "{furniture}" in desc:
        furniture = _get_furniture(pos.get("furniture_id"))
        if furniture:
            desc = desc.replace("{furniture}", furniture.get_display_name(character))
        else:
            desc = desc.replace("{furniture}", "something")
    
    # Substitute partner name
    if "{partner}" in desc:
        partner_ids = pos.get("partner_ids", [])
        if partner_ids:
            partner = _get_character(partner_ids[0])
            if partner:
                desc = desc.replace("{partner}", partner.get_display_name(character))
            else:
                desc = desc.replace("{partner}", "someone")
        else:
            desc = desc.replace("{partner}", "someone")
    
    return desc


def get_position_for_room(character):
    """
    Get position string formatted for room description.
    
    Returns:
        str: Full sentence like "CharName is sitting on the chair."
    """
    pos = character.db.position
    
    if not pos or pos.get("pose") == "standing":
        return None  # Don't show standing characters specially
    
    pose = pos.get("pose", "standing")
    pos_info = POSITIONS.get(pose, {})
    desc = pos_info.get("desc", f"is {pose}")
    
    # Use custom description if set
    if pos.get("custom_desc"):
        desc = f"is {pos['custom_desc']}"
    
    # Substitute furniture name
    if "{furniture}" in desc:
        furniture = _get_furniture(pos.get("furniture_id"))
        if furniture:
            desc = desc.replace("{furniture}", furniture.key)
        else:
            desc = desc.replace("{furniture}", "something")
    
    # Substitute partner name
    if "{partner}" in desc:
        partner_ids = pos.get("partner_ids", [])
        if partner_ids:
            partner = _get_character(partner_ids[0])
            if partner:
                desc = desc.replace("{partner}", partner.key)
            else:
                desc = desc.replace("{partner}", "someone")
        else:
            desc = desc.replace("{partner}", "someone")
    
    return f"|c{character.key}|n {desc}."


# =============================================================================
# Partner Management
# =============================================================================

def get_partner(character):
    """Get character's position partner, if any."""
    pos = character.db.position
    if not pos:
        return None
    
    partner_ids = pos.get("partner_ids", [])
    if not partner_ids:
        return None
    
    return _get_character(partner_ids[0])


def get_partners(character):
    """Get all of character's position partners."""
    pos = character.db.position
    if not pos:
        return []
    
    partner_ids = pos.get("partner_ids", [])
    partners = []
    for pid in partner_ids:
        p = _get_character(pid)
        if p:
            partners.append(p)
    return partners


def add_partner(character, partner):
    """Add a partner to character's current position."""
    pos = character.db.position
    if not pos:
        return False, "You're not in a position that supports partners."
    
    if "partner_ids" not in pos:
        pos["partner_ids"] = []
    
    if partner.id not in pos["partner_ids"]:
        pos["partner_ids"].append(partner.id)
    
    _link_partner(character, partner)
    return True, f"Added {partner.key} as partner."


def remove_partner(character, partner):
    """Remove a partner from character's position."""
    pos = character.db.position
    if not pos:
        return False, "No position to remove partner from."
    
    if partner.id in pos.get("partner_ids", []):
        pos["partner_ids"].remove(partner.id)
    
    _unlink_partner(character, partner)
    return True, f"Removed {partner.key} as partner."


# =============================================================================
# Furniture Integration
# =============================================================================

def get_furniture(character):
    """Get the furniture character is using, if any."""
    pos = character.db.position
    if not pos:
        return None
    
    furniture_id = pos.get("furniture_id")
    if not furniture_id:
        return None
    
    return _get_furniture(furniture_id)


def get_furniture_slot(character):
    """Get which furniture slot character is using."""
    pos = character.db.position
    if not pos:
        return None
    return pos.get("furniture_slot")


# =============================================================================
# Position Queries
# =============================================================================

def list_positions(category=None, adult=False):
    """
    List available positions.
    
    Args:
        category: Optional category filter
        adult: If False, exclude adult positions
    
    Returns:
        dict: Filtered positions
    """
    result = {}
    
    for key, pos in POSITIONS.items():
        # Filter by category
        if category and pos.get("category") != category:
            continue
        
        # Filter adult content
        if not adult and "adult" in pos.get("flags", []):
            continue
        
        result[key] = pos
    
    return result


def get_positions_for_furniture(furniture):
    """
    Get positions that can be used with specific furniture.
    
    Args:
        furniture: Furniture object
    
    Returns:
        list: Position type strings
    """
    # Get furniture's supported positions
    supported = furniture.db.supported_positions or []
    
    if supported:
        return supported
    
    # Default positions based on furniture type
    ftype = furniture.db.furniture_type or "generic"
    
    defaults = {
        "chair": ["seated", "sitting"],
        "couch": ["seated", "sitting", "lounging", "lying", "cuddling"],
        "bed": ["sitting", "lying", "lounging", "sleeping", "cuddling", 
                "straddling", "beneath", "atop", "entwined"],
        "table": ["sitting", "lying", "bound_lying", "displayed"],
        "bench": ["seated", "sitting", "lying", "bound_lying"],
        "stocks": ["bound_standing", "bound_bent"],
        "cross": ["bound_standing", "displayed", "suspended"],
        "cage": ["kneeling", "sitting", "lying"],
        "pole": ["bound_standing", "displayed"],
        "frame": ["bound_standing", "bound_lying", "suspended", "displayed"],
        "altar": ["kneeling", "lying", "bound_lying", "displayed"],
        "throne": ["seated", "lounging"],
        "cushion": ["sitting", "kneeling", "at_feet"],
        "mat": ["kneeling", "lying", "presenting"],
    }
    
    return defaults.get(ftype, ["sitting", "standing"])


# =============================================================================
# Internal Helpers
# =============================================================================

def _get_furniture(furniture_id):
    """Get furniture object by ID."""
    if not furniture_id:
        return None
    try:
        from evennia.objects.models import ObjectDB
        return ObjectDB.objects.get(id=furniture_id)
    except:
        return None


def _get_character(char_id):
    """Get character object by ID."""
    if not char_id:
        return None
    try:
        from evennia.objects.models import ObjectDB
        return ObjectDB.objects.get(id=char_id)
    except:
        return None


def _cleanup_old_position(character, old_pos):
    """Clean up references from old position."""
    # Remove from furniture
    if old_pos.get("furniture_id"):
        furniture = _get_furniture(old_pos["furniture_id"])
        if furniture:
            _vacate_furniture(furniture, character)
    
    # Unlink partners
    for partner_id in old_pos.get("partner_ids", []):
        partner = _get_character(partner_id)
        if partner:
            _unlink_partner(character, partner)


def _occupy_furniture(furniture, character, slot=None):
    """Add character to furniture's occupants."""
    if not furniture.db.occupants:
        furniture.db.occupants = {}
    
    slot = slot or "default"
    furniture.db.occupants[slot] = character.id


def _vacate_furniture(furniture, character):
    """Remove character from furniture's occupants."""
    if not furniture.db.occupants:
        return
    
    # Find and remove character from any slot
    to_remove = []
    for slot, occupant_id in furniture.db.occupants.items():
        if occupant_id == character.id:
            to_remove.append(slot)
    
    for slot in to_remove:
        del furniture.db.occupants[slot]


def _link_partner(character, partner):
    """Create mutual partner link."""
    partner_pos = partner.db.position
    if partner_pos:
        if "partner_ids" not in partner_pos:
            partner_pos["partner_ids"] = []
        if character.id not in partner_pos["partner_ids"]:
            partner_pos["partner_ids"].append(character.id)


def _unlink_partner(character, partner):
    """Remove mutual partner link."""
    partner_pos = partner.db.position
    if partner_pos and "partner_ids" in partner_pos:
        if character.id in partner_pos["partner_ids"]:
            partner_pos["partner_ids"].remove(character.id)
