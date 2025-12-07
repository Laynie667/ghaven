"""
Furniture System for Gilderhaven
=================================

Placeable furniture for homes and public spaces.
Furniture provides positions, storage, effects, and interactions.

Data Storage (on furniture object):
    furniture.db.furniture_type = "bed"
    furniture.db.furniture_data = {
        "capacity": 2,              # Max occupants
        "slots": ["left", "right"], # Named slots
        "supported_positions": [...],
        "effects": {...},
        "flags": ["adult", "bondage"],
    }
    furniture.db.occupants = {"left": char_id, ...}
    furniture.db.owner_id = 123
    furniture.db.placed_in = room_id

Usage:
    from world.furniture import (
        create_furniture, place_furniture, remove_furniture,
        use_furniture, leave_furniture, get_occupants,
        FURNITURE_CATALOG
    )
    
    # Create and place furniture
    chair = create_furniture("wooden_chair", owner)
    place_furniture(chair, room)
    
    # Use furniture
    use_furniture(character, chair, "seat")
    leave_furniture(character)
"""

import time
from evennia import create_object
from evennia.utils import logger


# =============================================================================
# Furniture Catalog
# =============================================================================

FURNITURE_CATALOG = {
    # -------------------------------------------------------------------------
    # Basic Seating
    # -------------------------------------------------------------------------
    "wooden_chair": {
        "key": "wooden chair",
        "desc": "A simple but sturdy wooden chair.",
        "furniture_type": "chair",
        "price": 50,
        "capacity": 1,
        "slots": ["seat"],
        "supported_positions": ["seated", "sitting"],
        "category": "seating",
    },
    "cushioned_chair": {
        "key": "cushioned chair",
        "desc": "A comfortable chair with soft cushions.",
        "furniture_type": "chair",
        "price": 100,
        "capacity": 1,
        "slots": ["seat"],
        "supported_positions": ["seated", "sitting", "lounging"],
        "category": "seating",
    },
    "armchair": {
        "key": "plush armchair",
        "desc": "A luxurious armchair with padded armrests.",
        "furniture_type": "chair",
        "price": 200,
        "capacity": 1,
        "slots": ["seat"],
        "supported_positions": ["seated", "sitting", "lounging", "cuddling"],
        "category": "seating",
    },
    "wooden_bench": {
        "key": "wooden bench",
        "desc": "A long wooden bench that seats several.",
        "furniture_type": "bench",
        "price": 75,
        "capacity": 3,
        "slots": ["left", "center", "right"],
        "supported_positions": ["seated", "sitting", "lying"],
        "category": "seating",
    },
    "cushion": {
        "key": "floor cushion",
        "desc": "A large, soft cushion for sitting on the floor.",
        "furniture_type": "cushion",
        "price": 25,
        "capacity": 1,
        "slots": ["cushion"],
        "supported_positions": ["sitting", "kneeling"],
        "category": "seating",
    },
    "pile_of_cushions": {
        "key": "pile of cushions",
        "desc": "A comfortable pile of soft cushions.",
        "furniture_type": "cushion",
        "price": 100,
        "capacity": 3,
        "slots": ["pile"],
        "supported_positions": ["sitting", "kneeling", "lying", "cuddling"],
        "category": "seating",
    },
    
    # -------------------------------------------------------------------------
    # Couches & Sofas
    # -------------------------------------------------------------------------
    "simple_couch": {
        "key": "simple couch",
        "desc": "A basic couch with worn but comfortable cushions.",
        "furniture_type": "couch",
        "price": 150,
        "capacity": 2,
        "slots": ["left", "right"],
        "supported_positions": ["seated", "sitting", "lounging", "lying", "cuddling"],
        "category": "seating",
    },
    "plush_sofa": {
        "key": "plush sofa",
        "desc": "A luxurious sofa that practically swallows you in comfort.",
        "furniture_type": "couch",
        "price": 350,
        "capacity": 3,
        "slots": ["left", "center", "right"],
        "supported_positions": ["seated", "sitting", "lounging", "lying", "cuddling", "lap_sitting"],
        "category": "seating",
    },
    "loveseat": {
        "key": "loveseat",
        "desc": "A cozy two-person seat, perfect for cuddling.",
        "furniture_type": "couch",
        "price": 250,
        "capacity": 2,
        "slots": ["left", "right"],
        "supported_positions": ["seated", "sitting", "cuddling", "lap_sitting", "lap_holding"],
        "category": "seating",
    },
    
    # -------------------------------------------------------------------------
    # Beds
    # -------------------------------------------------------------------------
    "simple_bed": {
        "key": "simple bed",
        "desc": "A basic bed with a straw mattress.",
        "furniture_type": "bed",
        "price": 100,
        "capacity": 1,
        "slots": ["bed"],
        "supported_positions": ["sitting", "lying", "sleeping", "reclining"],
        "effects": {"rest_quality": 1.0},
        "category": "beds",
    },
    "comfortable_bed": {
        "key": "comfortable bed",
        "desc": "A proper bed with a soft mattress and warm blankets.",
        "furniture_type": "bed",
        "price": 250,
        "capacity": 2,
        "slots": ["left", "right"],
        "supported_positions": ["sitting", "lying", "sleeping", "reclining", "cuddling"],
        "effects": {"rest_quality": 1.5},
        "category": "beds",
    },
    "large_bed": {
        "key": "large four-poster bed",
        "desc": "A grand bed with carved posts and silk curtains.",
        "furniture_type": "bed",
        "price": 500,
        "capacity": 3,
        "slots": ["left", "center", "right"],
        "supported_positions": ["sitting", "lying", "sleeping", "reclining", "cuddling",
                                "straddling", "beneath", "atop", "entwined"],
        "effects": {"rest_quality": 2.0},
        "flags": ["adult"],
        "category": "beds",
    },
    "canopy_bed": {
        "key": "canopy bed",
        "desc": "An elegant bed with flowing fabric canopy providing privacy.",
        "furniture_type": "bed",
        "price": 750,
        "capacity": 2,
        "slots": ["inside"],
        "supported_positions": ["sitting", "lying", "sleeping", "reclining", "cuddling",
                                "straddling", "beneath", "atop", "entwined", "bound_lying"],
        "effects": {"rest_quality": 2.5, "privacy": True},
        "flags": ["adult", "private"],
        "category": "beds",
    },
    "pet_bed": {
        "key": "pet bed",
        "desc": "A large, padded bed suitable for a pet... or a pet.",
        "furniture_type": "cushion",
        "price": 75,
        "capacity": 1,
        "slots": ["bed"],
        "supported_positions": ["lying", "kneeling", "at_feet"],
        "flags": ["adult"],
        "category": "beds",
    },
    
    # -------------------------------------------------------------------------
    # Tables
    # -------------------------------------------------------------------------
    "small_table": {
        "key": "small table",
        "desc": "A simple wooden table.",
        "furniture_type": "table",
        "price": 50,
        "capacity": 0,  # Can't sit on
        "storage_slots": 4,
        "category": "tables",
    },
    "dining_table": {
        "key": "dining table",
        "desc": "A large table suitable for meals.",
        "furniture_type": "table",
        "price": 150,
        "capacity": 0,
        "storage_slots": 8,
        "category": "tables",
    },
    "desk": {
        "key": "writing desk",
        "desc": "A sturdy desk with drawers.",
        "furniture_type": "table",
        "price": 200,
        "capacity": 0,
        "storage_slots": 6,
        "effects": {"crafting_bonus": 0.1},
        "category": "tables",
    },
    
    # -------------------------------------------------------------------------
    # Storage
    # -------------------------------------------------------------------------
    "chest": {
        "key": "wooden chest",
        "desc": "A sturdy wooden chest for storing belongings.",
        "furniture_type": "storage",
        "price": 75,
        "capacity": 0,
        "storage_slots": 10,
        "category": "storage",
    },
    "wardrobe": {
        "key": "wardrobe",
        "desc": "A tall wooden wardrobe for clothing.",
        "furniture_type": "storage",
        "price": 150,
        "capacity": 0,
        "storage_slots": 15,
        "category": "storage",
    },
    "bookshelf": {
        "key": "bookshelf",
        "desc": "A tall shelf for books and curiosities.",
        "furniture_type": "storage",
        "price": 100,
        "capacity": 0,
        "storage_slots": 12,
        "category": "storage",
    },
    
    # -------------------------------------------------------------------------
    # Decorative
    # -------------------------------------------------------------------------
    "mirror": {
        "key": "standing mirror",
        "desc": "A full-length mirror in an ornate frame.",
        "furniture_type": "decor",
        "price": 100,
        "capacity": 0,
        "category": "decor",
    },
    "rug": {
        "key": "woven rug",
        "desc": "A colorful woven rug that softens the floor.",
        "furniture_type": "decor",
        "price": 50,
        "capacity": 0,
        "category": "decor",
    },
    "fireplace": {
        "key": "stone fireplace",
        "desc": "A warm stone fireplace with a crackling fire.",
        "furniture_type": "decor",
        "price": 300,
        "capacity": 0,
        "effects": {"warmth": True, "ambiance": "cozy"},
        "category": "decor",
    },
    
    # -------------------------------------------------------------------------
    # Special / Thrones
    # -------------------------------------------------------------------------
    "throne": {
        "key": "ornate throne",
        "desc": "An imposing throne of carved wood and velvet.",
        "furniture_type": "throne",
        "price": 1000,
        "capacity": 1,
        "slots": ["throne"],
        "supported_positions": ["seated", "lounging", "lap_holding"],
        "effects": {"authority": True},
        "category": "special",
    },
    
    # -------------------------------------------------------------------------
    # Adult / Bondage Furniture
    # -------------------------------------------------------------------------
    "bondage_bed": {
        "key": "bondage bed",
        "desc": "A sturdy bed frame with reinforced attachment points at each corner.",
        "furniture_type": "bed",
        "price": 600,
        "capacity": 2,
        "slots": ["restrained", "free"],
        "supported_positions": ["lying", "sleeping", "bound_lying", "straddling", 
                                "beneath", "atop", "mounted"],
        "flags": ["adult", "bondage"],
        "category": "adult",
    },
    "spanking_bench": {
        "key": "spanking bench",
        "desc": "A padded bench designed to position someone bent over comfortably.",
        "furniture_type": "bench",
        "price": 400,
        "capacity": 1,
        "slots": ["bent"],
        "supported_positions": ["bound_bent", "lying"],
        "flags": ["adult", "bondage"],
        "category": "adult",
    },
    "stocks": {
        "key": "wooden stocks",
        "desc": "Classic wooden stocks that lock head and hands in place.",
        "furniture_type": "stocks",
        "price": 350,
        "capacity": 1,
        "slots": ["locked"],
        "supported_positions": ["bound_standing", "bound_bent"],
        "flags": ["adult", "bondage", "restraint"],
        "category": "adult",
    },
    "saint_andrews_cross": {
        "key": "St. Andrew's cross",
        "desc": "An X-shaped wooden cross with leather restraints at each point.",
        "furniture_type": "cross",
        "price": 500,
        "capacity": 1,
        "slots": ["cross"],
        "supported_positions": ["bound_standing", "displayed"],
        "flags": ["adult", "bondage", "restraint"],
        "category": "adult",
    },
    "suspension_frame": {
        "key": "suspension frame",
        "desc": "A sturdy metal frame with attachment points for rope and restraints.",
        "furniture_type": "frame",
        "price": 800,
        "capacity": 1,
        "slots": ["suspended"],
        "supported_positions": ["bound_standing", "suspended", "displayed"],
        "flags": ["adult", "bondage", "restraint"],
        "category": "adult",
    },
    "cage": {
        "key": "metal cage",
        "desc": "A sturdy cage large enough to hold a person.",
        "furniture_type": "cage",
        "price": 600,
        "capacity": 1,
        "slots": ["inside"],
        "supported_positions": ["kneeling", "sitting", "lying"],
        "flags": ["adult", "bondage", "enclosure"],
        "category": "adult",
    },
    "sybian": {
        "key": "sybian saddle",
        "desc": "A padded saddle-shaped device with... interesting attachments.",
        "furniture_type": "device",
        "price": 500,
        "capacity": 1,
        "slots": ["mounted"],
        "supported_positions": ["straddling", "mounted"],
        "flags": ["adult", "device"],
        "category": "adult",
    },
    "breeding_bench": {
        "key": "breeding bench",
        "desc": "A specialized bench that positions the occupant on all fours.",
        "furniture_type": "bench",
        "price": 450,
        "capacity": 1,
        "slots": ["mounted"],
        "supported_positions": ["bound_bent", "mounted", "presented"],
        "flags": ["adult", "bondage"],
        "category": "adult",
    },
    "display_platform": {
        "key": "display platform",
        "desc": "A raised platform with attachment points, designed to show someone off.",
        "furniture_type": "platform",
        "price": 400,
        "capacity": 1,
        "slots": ["displayed"],
        "supported_positions": ["standing", "kneeling", "displayed", "presenting"],
        "flags": ["adult"],
        "category": "adult",
    },
    "kneeling_mat": {
        "key": "kneeling mat",
        "desc": "A padded mat positioned before a chair or throne.",
        "furniture_type": "mat",
        "price": 50,
        "capacity": 1,
        "slots": ["kneeling"],
        "supported_positions": ["kneeling", "at_feet", "presenting", "servicing"],
        "flags": ["adult"],
        "category": "adult",
    },
    "submissive_cushion": {
        "key": "submissive's cushion",
        "desc": "A plush cushion placed at the foot of a seat for a sub to kneel upon.",
        "furniture_type": "cushion",
        "price": 75,
        "capacity": 1,
        "slots": ["at_feet"],
        "supported_positions": ["kneeling", "sitting", "at_feet"],
        "flags": ["adult"],
        "category": "adult",
    },
    
    # -------------------------------------------------------------------------
    # Museum / Curator Furniture
    # -------------------------------------------------------------------------
    "curators_desk": {
        "key": "Curator's desk",
        "desc": "A massive desk of dark polished wood, imposing and authoritative. "
                "There's space beneath it - not quite hidden from view.",
        "furniture_type": "desk",
        "price": 2000,
        "capacity": 2,
        "slots": ["seated", "beneath"],
        "supported_positions": ["seated", "lounging", "under_desk", "servicing"],
        "storage_slots": 10,
        "effects": {"authority": True},
        "flags": ["adult", "museum"],
        "category": "museum",
    },
    "curators_chair": {
        "key": "Curator's leather chair",
        "desc": "A high-backed leather chair that commands the room. "
                "Whoever sits here is clearly in charge.",
        "furniture_type": "throne",
        "price": 1500,
        "capacity": 1,
        "slots": ["throne"],
        "supported_positions": ["seated", "lounging", "being_serviced", "lap_holding"],
        "effects": {"authority": True},
        "flags": ["adult", "museum"],
        "category": "museum",
    },
    "guest_chair_low": {
        "key": "low guest chair",
        "desc": "A comfortable but notably lower chair, positioned across from a desk. "
                "Whoever sits here looks up at the person behind the desk.",
        "furniture_type": "chair",
        "price": 200,
        "capacity": 1,
        "slots": ["seat"],
        "supported_positions": ["seated", "sitting"],
        "flags": ["museum"],
        "category": "museum",
    },
    "kneeling_cushion_curator": {
        "key": "velvet kneeling cushion",
        "desc": "A plush velvet cushion in deep burgundy, positioned beside a chair. "
                "Its purpose is unmistakable.",
        "furniture_type": "cushion",
        "price": 150,
        "capacity": 1,
        "slots": ["kneeling"],
        "supported_positions": ["kneeling", "at_feet", "waiting", "collar_presented", "servicing"],
        "flags": ["adult", "museum"],
        "category": "museum",
    },
    "examination_table": {
        "key": "examination table",
        "desc": "A padded table with adjustable stirrups and leather restraints at strategic points. "
                "Clinical yet intimate.",
        "furniture_type": "table",
        "price": 800,
        "capacity": 1,
        "slots": ["subject"],
        "supported_positions": ["lying", "examination", "bound_lying", "displayed", "inspection"],
        "flags": ["adult", "bondage", "museum"],
        "category": "museum",
    },
    "display_pedestal": {
        "key": "display pedestal",
        "desc": "A raised circular platform with subtle lighting from below. "
                "Anything placed here becomes the center of attention.",
        "furniture_type": "pedestal",
        "price": 400,
        "capacity": 1,
        "slots": ["displayed"],
        "supported_positions": ["standing", "kneeling", "pedestal", "displayed_as_art", "presenting"],
        "flags": ["adult", "museum"],
        "category": "museum",
    },
    "living_display_case": {
        "key": "glass display case",
        "desc": "A large glass case with climate control and soft lighting. "
                "The lock is on the outside. Large enough to hold a person.",
        "furniture_type": "cage",
        "price": 1200,
        "capacity": 1,
        "slots": ["inside"],
        "supported_positions": ["kneeling", "sitting", "lying", "displayed_in_case"],
        "flags": ["adult", "bondage", "enclosure", "museum"],
        "category": "museum",
    },
    "leash_hook": {
        "key": "wall-mounted leash hook",
        "desc": "A sturdy metal hook mounted at waist height. A short chain dangles from it.",
        "furniture_type": "fixture",
        "price": 100,
        "capacity": 1,
        "slots": ["hooked"],
        "supported_positions": ["standing", "kneeling", "hooked", "waiting"],
        "flags": ["adult", "bondage", "museum"],
        "category": "museum",
    },
    "curators_bed": {
        "key": "Curator's bed",
        "desc": "A grand four-poster bed with dark wood frame and deep red silk sheets. "
                "Subtle attachment points are worked into the ornate carvings. "
                "This is where the Curator rests... and plays.",
        "furniture_type": "bed",
        "price": 3000,
        "capacity": 3,
        "slots": ["center", "left", "right"],
        "supported_positions": ["lying", "sleeping", "reclining", "cuddling", "bound_lying",
                                "straddling", "beneath", "atop", "mounted", "entwined",
                                "servicing", "being_serviced"],
        "effects": {"rest_quality": 3.0, "privacy": True},
        "flags": ["adult", "bondage", "museum"],
        "category": "museum",
    },
    "artifact_case": {
        "key": "artifact display case",
        "desc": "A glass case on a wooden pedestal, designed to showcase precious items.",
        "furniture_type": "storage",
        "price": 300,
        "capacity": 0,
        "storage_slots": 3,
        "flags": ["museum"],
        "category": "museum",
    },
    "velvet_rope": {
        "key": "velvet rope barrier",
        "desc": "A brass post with burgundy velvet rope, marking off restricted areas.",
        "furniture_type": "decor",
        "price": 50,
        "capacity": 0,
        "flags": ["museum"],
        "category": "museum",
    },
    "museum_bench": {
        "key": "museum viewing bench",
        "desc": "A backless padded bench for contemplating the exhibits.",
        "furniture_type": "bench",
        "price": 150,
        "capacity": 3,
        "slots": ["left", "center", "right"],
        "supported_positions": ["seated", "sitting"],
        "flags": ["museum"],
        "category": "museum",
    },
}

# Categories for display
FURNITURE_CATEGORIES = {
    "seating": "Chairs, Couches & Seating",
    "beds": "Beds & Sleeping",
    "tables": "Tables & Desks",
    "storage": "Storage & Organization",
    "decor": "Decorative Items",
    "special": "Special Furniture",
    "adult": "Adult Furniture",
    "museum": "Museum & Curator's Collection",
}


# =============================================================================
# Core Functions
# =============================================================================

def get_catalog_item(item_key):
    """Get an item from the furniture catalog."""
    return FURNITURE_CATALOG.get(item_key)


def list_catalog(category=None, adult=False):
    """
    List furniture catalog items.
    
    Args:
        category: Filter by category
        adult: Include adult items
    
    Returns:
        dict: Filtered catalog
    """
    result = {}
    
    for key, item in FURNITURE_CATALOG.items():
        # Filter by category
        if category and item.get("category") != category:
            continue
        
        # Filter adult content
        if not adult and "adult" in item.get("flags", []):
            continue
        
        result[key] = item
    
    return result


# =============================================================================
# Furniture Creation
# =============================================================================

def create_furniture(catalog_key, owner=None, typeclass="typeclasses.objects.Object"):
    """
    Create a furniture object from catalog.
    
    Args:
        catalog_key: Key from FURNITURE_CATALOG
        owner: Optional owner character
        typeclass: Typeclass to use
    
    Returns:
        Object: Created furniture or None
    """
    template = FURNITURE_CATALOG.get(catalog_key)
    if not template:
        return None
    
    # Create the object
    furniture = create_object(
        typeclass,
        key=template["key"],
    )
    
    # Set description
    furniture.db.desc = template.get("desc", "A piece of furniture.")
    
    # Set furniture data
    furniture.db.furniture_type = template.get("furniture_type", "generic")
    furniture.db.furniture_template = catalog_key
    furniture.db.furniture_data = {
        "capacity": template.get("capacity", 1),
        "slots": template.get("slots", ["default"]),
        "supported_positions": template.get("supported_positions", ["sitting"]),
        "storage_slots": template.get("storage_slots", 0),
        "effects": template.get("effects", {}),
        "flags": template.get("flags", []),
    }
    furniture.db.occupants = {}
    furniture.db.owner_id = owner.id if owner else None
    furniture.db.placed_in = None
    
    # Tag it as furniture
    furniture.tags.add("furniture", category="object_type")
    
    # Add category tags
    if "adult" in template.get("flags", []):
        furniture.tags.add("adult", category="content")
    if "bondage" in template.get("flags", []):
        furniture.tags.add("bondage", category="content")
    
    return furniture


def purchase_furniture(character, catalog_key):
    """
    Purchase furniture from catalog.
    
    Args:
        character: Character buying
        catalog_key: Item to buy
    
    Returns:
        tuple: (success, message, furniture or None)
    """
    template = FURNITURE_CATALOG.get(catalog_key)
    if not template:
        return False, f"Unknown furniture: {catalog_key}", None
    
    price = template.get("price", 0)
    
    # Check balance
    try:
        from world.currency import balance, pay
        if balance(character) < price:
            return False, f"You need {price} gold. You have {balance(character)}.", None
        
        # Deduct cost
        pay(character, price)
    except ImportError:
        pass  # Currency system not available
    
    # Create furniture
    furniture = create_furniture(catalog_key, owner=character)
    if not furniture:
        return False, "Failed to create furniture.", None
    
    # Put in character's inventory
    furniture.move_to(character, quiet=True)
    
    return True, f"You purchased {template['key']} for {price} gold.", furniture


# =============================================================================
# Furniture Placement
# =============================================================================

def place_furniture(furniture, room, position_desc=None):
    """
    Place furniture in a room.
    
    Args:
        furniture: Furniture object
        room: Room to place in
        position_desc: Optional description of placement
    
    Returns:
        tuple: (success, message)
    """
    # Check if room allows furniture
    max_slots = room.db.furniture_slots
    if max_slots is None:
        max_slots = 5  # Default for non-home rooms
    
    # Count existing furniture
    current_count = len([obj for obj in room.contents 
                        if obj.tags.has("furniture", category="object_type")])
    
    if current_count >= max_slots:
        return False, f"This room can only hold {max_slots} pieces of furniture."
    
    # Move furniture to room
    furniture.move_to(room, quiet=True)
    furniture.db.placed_in = room.id
    
    if position_desc:
        furniture.db.position_desc = position_desc
    
    return True, f"You place {furniture.key} in the room."


def remove_furniture(furniture, character):
    """
    Remove furniture from a room (back to inventory).
    
    Args:
        furniture: Furniture to remove
        character: Character removing it
    
    Returns:
        tuple: (success, message)
    """
    # Check if anyone is using it
    occupants = get_occupants(furniture)
    if occupants:
        # Force everyone off
        for occ in occupants:
            from world.positions import force_clear_position
            force_clear_position(occ, silent=True)
            occ.msg(f"You're forced to stand as {furniture.key} is removed.")
    
    # Move to character's inventory
    furniture.move_to(character, quiet=True)
    furniture.db.placed_in = None
    
    return True, f"You pick up {furniture.key}."


# =============================================================================
# Furniture Usage
# =============================================================================

def use_furniture(character, furniture, slot=None, position="seated"):
    """
    Have a character use furniture.
    
    Args:
        character: Character using furniture
        furniture: Furniture to use
        slot: Which slot to occupy
        position: Position to assume
    
    Returns:
        tuple: (success, message)
    """
    data = furniture.db.furniture_data
    if not data:
        return False, "This isn't usable furniture."
    
    # Check capacity
    capacity = data.get("capacity", 1)
    if capacity <= 0:
        return False, f"You can't sit on {furniture.key}."
    
    current_occupants = len(furniture.db.occupants or {})
    if current_occupants >= capacity:
        return False, f"{furniture.key} is full."
    
    # Determine slot
    available_slots = data.get("slots", ["default"])
    if slot:
        if slot not in available_slots:
            return False, f"Invalid slot. Available: {', '.join(available_slots)}"
        if slot in (furniture.db.occupants or {}):
            return False, f"That spot is taken."
    else:
        # Find first available slot
        slot = None
        for s in available_slots:
            if s not in (furniture.db.occupants or {}):
                slot = s
                break
        if not slot:
            return False, f"{furniture.key} is full."
    
    # Check if position is supported
    supported = data.get("supported_positions", ["sitting"])
    if position not in supported:
        # Try to find a valid default
        if "seated" in supported:
            position = "seated"
        elif "sitting" in supported:
            position = "sitting"
        elif supported:
            position = supported[0]
        else:
            return False, f"You can't use {furniture.key} that way."
    
    # Set position
    from world.positions import set_position
    success, msg = set_position(character, position, furniture=furniture, slot=slot)
    
    if success:
        return True, f"You {position} on {furniture.key}."
    else:
        return False, msg


def leave_furniture(character):
    """
    Have a character leave furniture they're using.
    
    Args:
        character: Character to remove
    
    Returns:
        tuple: (success, message)
    """
    from world.positions import clear_position, get_furniture
    
    furniture = get_furniture(character)
    if not furniture:
        return False, "You're not using any furniture."
    
    return clear_position(character)


def get_occupants(furniture):
    """
    Get list of characters using this furniture.
    
    Args:
        furniture: Furniture to check
    
    Returns:
        list: Character objects
    """
    occupants = furniture.db.occupants or {}
    result = []
    
    for slot, char_id in occupants.items():
        try:
            from evennia.objects.models import ObjectDB
            char = ObjectDB.objects.get(id=char_id)
            result.append(char)
        except:
            pass
    
    return result


def get_available_slots(furniture):
    """
    Get list of unoccupied slots.
    
    Args:
        furniture: Furniture to check
    
    Returns:
        list: Available slot names
    """
    data = furniture.db.furniture_data or {}
    all_slots = data.get("slots", ["default"])
    occupied = furniture.db.occupants or {}
    
    return [s for s in all_slots if s not in occupied]


def is_furniture(obj):
    """Check if an object is furniture."""
    return obj.tags.has("furniture", category="object_type")


def is_bondage_furniture(obj):
    """Check if furniture is bondage type."""
    data = obj.db.furniture_data or {}
    return "bondage" in data.get("flags", [])


def is_adult_furniture(obj):
    """Check if furniture is adult-only."""
    data = obj.db.furniture_data or {}
    return "adult" in data.get("flags", [])


# =============================================================================
# Furniture Display
# =============================================================================

def get_furniture_display(furniture, looker=None):
    """
    Get display string for furniture including occupants.
    
    Args:
        furniture: Furniture to describe
        looker: Who is looking
    
    Returns:
        str: Description with occupant info
    """
    desc = furniture.db.desc or "A piece of furniture."
    
    occupants = get_occupants(furniture)
    if occupants:
        occ_names = [occ.get_display_name(looker) for occ in occupants]
        if len(occ_names) == 1:
            desc += f"\n{occ_names[0]} is using it."
        else:
            desc += f"\n{', '.join(occ_names[:-1])} and {occ_names[-1]} are using it."
    
    return desc


def get_furniture_for_room(room):
    """
    Get all furniture in a room.
    
    Args:
        room: Room to check
    
    Returns:
        list: Furniture objects
    """
    return [obj for obj in room.contents 
            if obj.tags.has("furniture", category="object_type")]
