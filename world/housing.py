"""
Player Housing System
=====================

Complete housing system with:
- Purchasable homes of different tiers
- Expandable rooms (buy additional rooms)
- In-home customization (descriptions, names)
- Granular permission system
- Furniture placement integration
- Visitor/guest management

Architecture:
- Homes are instanced (not on the main grid)
- Each home has a "foyer" (main entry room)
- Additional rooms connect to the foyer or each other
- Players teleport home via command

Data stored on rooms and characters via .db attributes.
No modifications to Character.py required.
"""

from evennia.utils.create import create_object
from evennia.utils.search import search_object
from world.currency import balance, pay, receive

# =============================================================================
# CONSTANTS
# =============================================================================

# Permission levels (higher = more access)
PERMISSION_LEVELS = {
    "banned": -1,      # Cannot enter under any circumstances
    "stranger": 0,     # Default - can knock, nothing else
    "visitor": 1,      # Can enter when invited in (temporary)
    "guest": 2,        # Can enter when owner is home
    "trusted": 3,      # Can enter anytime, use furniture
    "resident": 4,     # Lives there, can edit some things
    "owner": 5,        # Full control
}

# Home types and their base stats
HOME_TYPES = {
    "tent": {
        "name": "Tent",
        "desc": "A simple canvas tent. It's not much, but it's yours.",
        "price": 0,  # Free starter
        "base_rooms": 1,
        "max_rooms": 1,
        "furniture_slots": 2,
        "storage_slots": 5,
        "features": [],
    },
    "cottage": {
        "name": "Cozy Cottage",
        "desc": "A small but comfortable cottage with whitewashed walls and a thatched roof.",
        "price": 500,
        "base_rooms": 2,
        "max_rooms": 4,
        "furniture_slots": 5,
        "storage_slots": 15,
        "features": ["hearth"],
    },
    "apartment": {
        "name": "Grove Apartment",
        "desc": "A tidy apartment in the residential quarter, with a view of the Grove.",
        "price": 1000,
        "base_rooms": 3,
        "max_rooms": 5,
        "furniture_slots": 8,
        "storage_slots": 20,
        "features": ["hearth", "running_water"],
    },
    "house": {
        "name": "Townhouse",
        "desc": "A respectable two-story house with a small yard.",
        "price": 2500,
        "base_rooms": 4,
        "max_rooms": 8,
        "furniture_slots": 12,
        "storage_slots": 30,
        "features": ["hearth", "running_water", "garden_space"],
    },
    "manor": {
        "name": "Manor House",
        "desc": "An impressive manor with elegant furnishings and sprawling grounds.",
        "price": 7500,
        "base_rooms": 6,
        "max_rooms": 12,
        "furniture_slots": 20,
        "storage_slots": 50,
        "features": ["hearth", "running_water", "garden_space", "servants_quarters", "wine_cellar"],
    },
    "estate": {
        "name": "Grand Estate",
        "desc": "A magnificent estate befitting nobility, with extensive grounds and outbuildings.",
        "price": 25000,
        "base_rooms": 10,
        "max_rooms": 20,
        "furniture_slots": 35,
        "storage_slots": 100,
        "features": ["hearth", "running_water", "garden_space", "servants_quarters", 
                     "wine_cellar", "stables", "guest_house", "private_gate"],
    },
}

# Room types that can be added
ROOM_TYPES = {
    "bedroom": {
        "name": "Bedroom",
        "desc": "A comfortable bedroom with space for a bed and personal effects.",
        "price": 200,
        "furniture_slots": 4,
        "features": ["sleep", "intimacy"],
    },
    "bathroom": {
        "name": "Bathroom",
        "desc": "A private bathroom with basic amenities.",
        "price": 150,
        "furniture_slots": 2,
        "features": ["grooming", "bathing"],
    },
    "kitchen": {
        "name": "Kitchen",
        "desc": "A functional kitchen for preparing meals.",
        "price": 250,
        "furniture_slots": 4,
        "features": ["cooking", "storage"],
    },
    "living_room": {
        "name": "Living Room",
        "desc": "A welcoming space for relaxation and entertaining guests.",
        "price": 200,
        "furniture_slots": 6,
        "features": ["socializing", "comfort"],
    },
    "study": {
        "name": "Study",
        "desc": "A quiet room for reading, writing, and contemplation.",
        "price": 300,
        "furniture_slots": 4,
        "features": ["crafting", "reading", "magic"],
    },
    "garden": {
        "name": "Garden",
        "desc": "An outdoor space with room for plants and relaxation.",
        "price": 350,
        "furniture_slots": 5,
        "features": ["gardening", "outdoor", "plants"],
        "requires_feature": "garden_space",
    },
    "basement": {
        "name": "Basement",
        "desc": "A cool underground space, good for storage or... other purposes.",
        "price": 400,
        "furniture_slots": 6,
        "features": ["storage", "hidden", "cool"],
    },
    "attic": {
        "name": "Attic",
        "desc": "A cozy space under the eaves, with slanted ceilings and character.",
        "price": 250,
        "furniture_slots": 4,
        "features": ["storage", "cozy", "private"],
    },
    "dungeon": {
        "name": "Private Dungeon",
        "desc": "A specially equipped room for... adult activities.",
        "price": 1000,
        "furniture_slots": 8,
        "features": ["adult", "bondage", "private", "soundproof"],
        "adult_only": True,
    },
    "playroom": {
        "name": "Playroom",
        "desc": "A room designed for intimate encounters and exploration.",
        "price": 750,
        "furniture_slots": 6,
        "features": ["adult", "intimacy", "private"],
        "adult_only": True,
    },
    "custom": {
        "name": "Custom Room",
        "desc": "An empty room you can customize however you like.",
        "price": 300,
        "furniture_slots": 5,
        "features": ["customizable"],
    },
}

# Upgrade packages
UPGRADES = {
    "extra_storage_small": {
        "name": "Storage Expansion (Small)",
        "desc": "Add 10 storage slots to your home.",
        "price": 100,
        "storage_bonus": 10,
    },
    "extra_storage_large": {
        "name": "Storage Expansion (Large)",
        "desc": "Add 25 storage slots to your home.",
        "price": 200,
        "storage_bonus": 25,
    },
    "extra_furniture_small": {
        "name": "Furniture Expansion (Small)",
        "desc": "Add 3 furniture slots to your home.",
        "price": 150,
        "furniture_bonus": 3,
    },
    "extra_furniture_large": {
        "name": "Furniture Expansion (Large)",
        "desc": "Add 6 furniture slots to your home.",
        "price": 300,
        "furniture_bonus": 6,
    },
    "soundproofing": {
        "name": "Soundproofing",
        "desc": "Sound doesn't carry outside your home. Privacy guaranteed.",
        "price": 500,
        "feature": "soundproof",
    },
    "magical_lighting": {
        "name": "Magical Lighting",
        "desc": "Ambient magical lighting that responds to your mood.",
        "price": 250,
        "feature": "magic_lights",
    },
    "climate_control": {
        "name": "Climate Control",
        "desc": "Always the perfect temperature, regardless of weather.",
        "price": 300,
        "feature": "climate_control",
    },
    "security_ward": {
        "name": "Security Ward",
        "desc": "Magical protection against uninvited entry.",
        "price": 400,
        "feature": "warded",
    },
    "portal_stone": {
        "name": "Portal Stone",
        "desc": "Instantly teleport home from anywhere in the Grove.",
        "price": 1000,
        "feature": "instant_recall",
    },
}


# =============================================================================
# CORE FUNCTIONS - HOME MANAGEMENT
# =============================================================================

def get_home(character):
    """
    Get a character's home room, if they have one.
    
    Returns:
        Room object or None
    """
    home_id = character.db.home_id
    if not home_id:
        return None
    
    results = search_object("#" + str(home_id))
    return results[0] if results else None


def get_home_by_id(home_id):
    """
    Get a home room by its ID.
    
    Args:
        home_id: The database ID of the home room
        
    Returns:
        Room object or None
    """
    if not home_id:
        return None
    results = search_object("#" + str(home_id))
    return results[0] if results else None


def has_home(character):
    """Check if character owns a home."""
    return get_home(character) is not None


def get_home_type(home_room):
    """Get the home type info for a home room."""
    home_type = home_room.db.home_type or "tent"
    return HOME_TYPES.get(home_type, HOME_TYPES["tent"])


def get_all_home_rooms(home_room):
    """
    Get all rooms that are part of a home (foyer + additions).
    
    Args:
        home_room: The main/foyer room of the home
        
    Returns:
        List of room objects
    """
    rooms = [home_room]
    connected_ids = home_room.db.connected_rooms or []
    
    for room_id in connected_ids:
        results = search_object("#" + str(room_id))
        if results:
            rooms.append(results[0])
    
    return rooms


def create_home(character, home_type="tent", home_name=None):
    """
    Create a new home for a character.
    
    Args:
        character: The character buying the home
        home_type: Type from HOME_TYPES
        home_name: Custom name (default: "{Name}'s {Type}")
        
    Returns:
        (success, message, home_room or None)
    """
    if has_home(character):
        return (False, "You already own a home.", None)
    
    if home_type not in HOME_TYPES:
        return (False, f"Unknown home type: {home_type}", None)
    
    type_info = HOME_TYPES[home_type]
    price = type_info["price"]
    
    # Check funds (skip for free tent)
    if price > 0:
        if balance(character) < price:
            return (False, f"You need {price} coins to purchase a {type_info['name']}.", None)
        pay(character, price)
    
    # Generate name
    if not home_name:
        home_name = f"{character.key}'s {type_info['name']}"
    
    # Create the home room
    # Using base Room typeclass - can be changed to HomeRoom if you create one
    home_room = create_object(
        typeclass="typeclasses.rooms.Room",
        key=home_name,
        locks=f"control:id({character.id}) or perm(Admin)"
    )
    
    # Set up home data
    home_room.db.is_home = True
    home_room.db.home_type = home_type
    home_room.db.home_name = home_name
    home_room.db.owner_id = character.id
    home_room.db.owner_name = character.key
    
    # Permissions
    home_room.db.permissions = {
        "residents": [],
        "trusted": [],
        "guests": [],
        "banned": [],
    }
    home_room.db.locked = True
    home_room.db.visitors_allowed = []  # Temp visitor list
    
    # Capacity
    home_room.db.furniture_slots = type_info["furniture_slots"]
    home_room.db.storage_slots = type_info["storage_slots"]
    home_room.db.max_rooms = type_info["max_rooms"]
    home_room.db.features = list(type_info["features"])
    home_room.db.upgrades = []
    home_room.db.connected_rooms = []
    
    # Set description
    home_room.db.desc = type_info["desc"]
    
    # Link character to home
    character.db.home_id = home_room.id
    character.db.owned_rooms = [home_room.id]
    
    return (True, f"Congratulations! You are now the proud owner of {home_name}!", home_room)


def upgrade_home(character, new_type):
    """
    Upgrade a home to a better type.
    
    Args:
        character: The home owner
        new_type: New home type from HOME_TYPES
        
    Returns:
        (success, message)
    """
    home = get_home(character)
    if not home:
        return (False, "You don't own a home.")
    
    current_type = home.db.home_type
    if new_type not in HOME_TYPES:
        return (False, f"Unknown home type: {new_type}")
    
    current_info = HOME_TYPES[current_type]
    new_info = HOME_TYPES[new_type]
    
    # Calculate upgrade cost (difference in prices)
    upgrade_cost = new_info["price"] - current_info["price"]
    if upgrade_cost <= 0:
        return (False, "That's not an upgrade!")
    
    if balance(character) < upgrade_cost:
        return (False, f"Upgrading to a {new_info['name']} costs {upgrade_cost} coins.")
    
    pay(character, upgrade_cost)
    
    # Apply upgrade
    home.db.home_type = new_type
    home.db.furniture_slots = new_info["furniture_slots"]
    home.db.storage_slots = new_info["storage_slots"]
    home.db.max_rooms = new_info["max_rooms"]
    
    # Add new features (keep old ones)
    current_features = set(home.db.features or [])
    new_features = set(new_info["features"])
    home.db.features = list(current_features | new_features)
    
    # Update name if it was default
    if home.db.home_name == f"{character.key}'s {current_info['name']}":
        home.db.home_name = f"{character.key}'s {new_info['name']}"
        home.key = home.db.home_name
    
    return (True, f"Your home has been upgraded to a {new_info['name']}!")


def add_room(character, room_type):
    """
    Add a new room to a home.
    
    Args:
        character: The home owner
        room_type: Type from ROOM_TYPES
        
    Returns:
        (success, message, new_room or None)
    """
    home = get_home(character)
    if not home:
        return (False, "You don't own a home.", None)
    
    if room_type not in ROOM_TYPES:
        return (False, f"Unknown room type: {room_type}", None)
    
    room_info = ROOM_TYPES[room_type]
    
    # Check max rooms
    current_rooms = len(home.db.connected_rooms or []) + 1  # +1 for foyer
    max_rooms = home.db.max_rooms or 1
    if current_rooms >= max_rooms:
        return (False, f"Your home can only have {max_rooms} rooms. Upgrade your home for more space.", None)
    
    # Check required features
    required = room_info.get("requires_feature")
    if required and required not in (home.db.features or []):
        return (False, f"Your home needs the '{required}' feature to add a {room_info['name']}.", None)
    
    # Check funds
    price = room_info["price"]
    if balance(character) < price:
        return (False, f"Adding a {room_info['name']} costs {price} coins.", None)
    
    pay(character, price)
    
    # Create the room
    room_name = f"{home.db.home_name} - {room_info['name']}"
    new_room = create_object(
        typeclass="typeclasses.rooms.Room",
        key=room_name,
        locks=f"control:id({character.id}) or perm(Admin)"
    )
    
    # Set up room data
    new_room.db.is_home = True
    new_room.db.is_home_room = True  # Sub-room, not foyer
    new_room.db.parent_home_id = home.id
    new_room.db.room_type = room_type
    new_room.db.owner_id = character.id
    new_room.db.furniture_slots = room_info["furniture_slots"]
    new_room.db.features = list(room_info.get("features", []))
    new_room.db.desc = room_info["desc"]
    new_room.db.custom_desc = None  # Player can set this
    
    # Link rooms with exits
    # Exit from foyer to new room
    create_object(
        typeclass="typeclasses.exits.Exit",
        key=room_info["name"].lower(),
        aliases=[room_type],
        location=home,
        destination=new_room,
        locks=f"traverse:all()"  # Home entry controlled at room level
    )
    
    # Exit back to foyer
    create_object(
        typeclass="typeclasses.exits.Exit",
        key="foyer",
        aliases=["back", "main", "out"],
        location=new_room,
        destination=home,
        locks=f"traverse:all()"
    )
    
    # Update home data
    connected = home.db.connected_rooms or []
    connected.append(new_room.id)
    home.db.connected_rooms = connected
    
    owned = character.db.owned_rooms or []
    owned.append(new_room.id)
    character.db.owned_rooms = owned
    
    return (True, f"A new {room_info['name']} has been added to your home!", new_room)


def purchase_upgrade(character, upgrade_key):
    """
    Purchase a home upgrade.
    
    Args:
        character: The home owner
        upgrade_key: Key from UPGRADES
        
    Returns:
        (success, message)
    """
    home = get_home(character)
    if not home:
        return (False, "You don't own a home.")
    
    if upgrade_key not in UPGRADES:
        return (False, f"Unknown upgrade: {upgrade_key}")
    
    upgrade_info = UPGRADES[upgrade_key]
    
    # Check if already owned
    owned_upgrades = home.db.upgrades or []
    if upgrade_key in owned_upgrades:
        return (False, "You already have that upgrade.")
    
    # Check funds
    price = upgrade_info["price"]
    if balance(character) < price:
        return (False, f"The {upgrade_info['name']} costs {price} coins.")
    
    pay(character, price)
    
    # Apply upgrade
    owned_upgrades.append(upgrade_key)
    home.db.upgrades = owned_upgrades
    
    # Apply bonuses
    if "storage_bonus" in upgrade_info:
        home.db.storage_slots = (home.db.storage_slots or 0) + upgrade_info["storage_bonus"]
    
    if "furniture_bonus" in upgrade_info:
        home.db.furniture_slots = (home.db.furniture_slots or 0) + upgrade_info["furniture_bonus"]
    
    if "feature" in upgrade_info:
        features = home.db.features or []
        features.append(upgrade_info["feature"])
        home.db.features = features
    
    return (True, f"Upgrade purchased: {upgrade_info['name']}!")


# =============================================================================
# PERMISSION FUNCTIONS
# =============================================================================

def get_permission_level(home_room, character):
    """
    Get a character's permission level for a home.
    
    Args:
        home_room: The home (foyer) room
        character: The character to check
        
    Returns:
        Permission level string
    """
    if not home_room.db.is_home:
        return "stranger"
    
    # Owner check
    if home_room.db.owner_id == character.id:
        return "owner"
    
    perms = home_room.db.permissions or {}
    char_id = character.id
    
    # Check each level
    if char_id in perms.get("banned", []):
        return "banned"
    if char_id in perms.get("residents", []):
        return "resident"
    if char_id in perms.get("trusted", []):
        return "trusted"
    if char_id in perms.get("guests", []):
        return "guest"
    if char_id in (home_room.db.visitors_allowed or []):
        return "visitor"
    
    return "stranger"


def can_enter(home_room, character):
    """
    Check if a character can enter a home.
    
    Args:
        home_room: The home to enter
        character: The character trying to enter
        
    Returns:
        (can_enter, reason)
    """
    level = get_permission_level(home_room, character)
    level_num = PERMISSION_LEVELS.get(level, 0)
    
    if level == "banned":
        return (False, "You have been banned from this home.")
    
    if level == "owner" or level == "resident":
        return (True, None)
    
    if level == "trusted":
        return (True, None)
    
    # Check if locked
    if home_room.db.locked:
        if level == "guest":
            # Guests can enter if owner is home
            owner_id = home_room.db.owner_id
            for obj in home_room.contents:
                if hasattr(obj, 'id') and obj.id == owner_id:
                    return (True, None)
            return (False, "The door is locked and the owner isn't home.")
        
        if level == "visitor":
            return (True, None)  # Explicitly let in
        
        return (False, "The door is locked.")
    
    # Unlocked - anyone can enter
    return (True, None)


def set_permission(home_room, character, target, level):
    """
    Set a character's permission level for a home.
    
    Args:
        home_room: The home
        character: The owner making the change
        target: The character whose permissions are being set
        level: New permission level
        
    Returns:
        (success, message)
    """
    # Verify ownership
    if home_room.db.owner_id != character.id:
        return (False, "Only the owner can change permissions.")
    
    if level not in PERMISSION_LEVELS:
        return (False, f"Unknown permission level: {level}")
    
    # Can't change own permissions
    if target.id == character.id:
        return (False, "You can't change your own permissions.")
    
    perms = home_room.db.permissions or {
        "residents": [],
        "trusted": [],
        "guests": [],
        "banned": [],
    }
    
    target_id = target.id
    
    # Remove from all lists first
    for key in ["residents", "trusted", "guests", "banned"]:
        if target_id in perms.get(key, []):
            perms[key].remove(target_id)
    
    # Add to new list (if not stranger)
    if level != "stranger":
        if level not in perms:
            perms[level] = []
        perms[level].append(target_id)
    
    home_room.db.permissions = perms
    
    return (True, f"{target.key}'s permission level set to {level}.")


def invite_visitor(home_room, character, target):
    """
    Temporarily allow someone to enter (one-time visitor).
    
    Args:
        home_room: The home
        character: The owner inviting
        target: The character being invited
        
    Returns:
        (success, message)
    """
    if home_room.db.owner_id != character.id:
        # Residents can also invite
        perms = home_room.db.permissions or {}
        if character.id not in perms.get("residents", []):
            return (False, "Only the owner or residents can invite visitors.")
    
    visitors = home_room.db.visitors_allowed or []
    if target.id not in visitors:
        visitors.append(target.id)
        home_room.db.visitors_allowed = visitors
    
    return (True, f"{target.key} has been invited to enter.")


def revoke_visitor(home_room, character, target):
    """
    Remove someone's temporary visitor access.
    """
    if home_room.db.owner_id != character.id:
        perms = home_room.db.permissions or {}
        if character.id not in perms.get("residents", []):
            return (False, "Only the owner or residents can manage visitors.")
    
    visitors = home_room.db.visitors_allowed or []
    if target.id in visitors:
        visitors.remove(target.id)
        home_room.db.visitors_allowed = visitors
        return (True, f"{target.key}'s visitor access has been revoked.")
    
    return (False, f"{target.key} wasn't a visitor.")


def kick_from_home(home_room, character, target):
    """
    Forcibly remove someone from the home.
    
    Args:
        home_room: The home
        character: The owner/resident doing the kicking
        target: The character being kicked
        
    Returns:
        (success, message)
    """
    # Check authority
    kicker_level = PERMISSION_LEVELS.get(get_permission_level(home_room, character), 0)
    target_level = PERMISSION_LEVELS.get(get_permission_level(home_room, target), 0)
    
    if kicker_level < PERMISSION_LEVELS["resident"]:
        return (False, "You don't have permission to kick people.")
    
    if target_level >= kicker_level:
        return (False, "You can't kick someone with equal or higher permissions.")
    
    # Find where target is
    all_rooms = get_all_home_rooms(home_room)
    target_room = None
    for room in all_rooms:
        if target in room.contents:
            target_room = room
            break
    
    if not target_room:
        return (False, f"{target.key} isn't in your home.")
    
    # Find the Grove or a default exit location
    # You'd want to set this properly in your game
    exit_location = search_object("The Grove", typeclass="typeclasses.rooms.Room")
    if exit_location:
        exit_location = exit_location[0]
    else:
        # Fallback - just move them out of the home somehow
        return (False, "Error: No exit location defined.")
    
    target.move_to(exit_location, quiet=False)
    target.msg(f"You have been kicked from {home_room.db.home_name}!")
    
    # Revoke visitor status
    revoke_visitor(home_room, character, target)
    
    return (True, f"{target.key} has been kicked from your home.")


# =============================================================================
# CUSTOMIZATION FUNCTIONS
# =============================================================================

def set_home_name(home_room, character, new_name):
    """
    Rename a home.
    
    Args:
        home_room: The home
        character: The owner
        new_name: New name
        
    Returns:
        (success, message)
    """
    if home_room.db.owner_id != character.id:
        return (False, "Only the owner can rename the home.")
    
    if not new_name or len(new_name) > 50:
        return (False, "Name must be 1-50 characters.")
    
    old_name = home_room.db.home_name
    home_room.db.home_name = new_name
    home_room.key = new_name
    
    return (True, f"Home renamed from '{old_name}' to '{new_name}'.")


def set_room_description(room, character, new_desc):
    """
    Set a custom description for a home room.
    
    Args:
        room: The room to customize
        character: The character editing
        new_desc: New description
        
    Returns:
        (success, message)
    """
    if not room.db.is_home:
        return (False, "This isn't a home room.")
    
    # Get the main home
    if room.db.is_home_room:
        home_id = room.db.parent_home_id
        home = search_object("#" + str(home_id))
        home = home[0] if home else None
    else:
        home = room
    
    if not home:
        return (False, "Error finding home.")
    
    # Check permissions
    level = get_permission_level(home, character)
    if level not in ["owner", "resident"]:
        return (False, "Only owners and residents can edit descriptions.")
    
    if len(new_desc) > 2000:
        return (False, "Description must be under 2000 characters.")
    
    room.db.custom_desc = new_desc
    room.db.desc = new_desc  # Also set the actual desc
    
    return (True, "Room description updated.")


def lock_home(home_room, character, lock=True):
    """
    Lock or unlock the home.
    
    Args:
        home_room: The home
        character: The owner/resident
        lock: True to lock, False to unlock
        
    Returns:
        (success, message)
    """
    level = get_permission_level(home_room, character)
    if level not in ["owner", "resident"]:
        return (False, "Only owners and residents can lock/unlock the home.")
    
    home_room.db.locked = lock
    state = "locked" if lock else "unlocked"
    
    return (True, f"Your home is now {state}.")


# =============================================================================
# DISPLAY FUNCTIONS
# =============================================================================

def get_home_info(home_room):
    """
    Get formatted info about a home.
    
    Args:
        home_room: The home
        
    Returns:
        Formatted string
    """
    if not home_room.db.is_home:
        return "Not a home."
    
    type_info = HOME_TYPES.get(home_room.db.home_type, HOME_TYPES["tent"])
    
    lines = []
    lines.append(f"|w{home_room.db.home_name}|n")
    lines.append(f"Type: {type_info['name']}")
    lines.append(f"Owner: {home_room.db.owner_name}")
    lines.append("")
    
    # Room count
    rooms = get_all_home_rooms(home_room)
    lines.append(f"Rooms: {len(rooms)}/{home_room.db.max_rooms}")
    
    # Room list
    if len(rooms) > 1:
        room_names = []
        for r in rooms:
            if r.db.room_type:
                room_names.append(ROOM_TYPES.get(r.db.room_type, {}).get("name", "Room"))
            else:
                room_names.append("Foyer")
        lines.append(f"  {', '.join(room_names)}")
    
    lines.append("")
    lines.append(f"Furniture Slots: {home_room.db.furniture_slots}")
    lines.append(f"Storage Slots: {home_room.db.storage_slots}")
    
    # Features
    features = home_room.db.features or []
    if features:
        lines.append(f"Features: {', '.join(features)}")
    
    # Upgrades
    upgrades = home_room.db.upgrades or []
    if upgrades:
        upgrade_names = [UPGRADES.get(u, {}).get("name", u) for u in upgrades]
        lines.append(f"Upgrades: {', '.join(upgrade_names)}")
    
    # Lock status
    lines.append("")
    lines.append(f"Door: {'|rLocked|n' if home_room.db.locked else '|gUnlocked|n'}")
    
    return "\n".join(lines)


def get_permission_list(home_room):
    """
    Get formatted list of permissions.
    
    Args:
        home_room: The home
        
    Returns:
        Formatted string
    """
    perms = home_room.db.permissions or {}
    lines = [f"|wPermissions for {home_room.db.home_name}|n", ""]
    
    for level in ["residents", "trusted", "guests", "banned"]:
        char_ids = perms.get(level, [])
        if char_ids:
            names = []
            for char_id in char_ids:
                result = search_object("#" + str(char_id))
                if result:
                    names.append(result[0].key)
                else:
                    names.append(f"(#{char_id})")
            lines.append(f"{level.title()}: {', '.join(names)}")
        else:
            lines.append(f"{level.title()}: None")
    
    # Temp visitors
    visitors = home_room.db.visitors_allowed or []
    if visitors:
        names = []
        for char_id in visitors:
            result = search_object("#" + str(char_id))
            if result:
                names.append(result[0].key)
        lines.append(f"Visitors (temp): {', '.join(names)}")
    
    return "\n".join(lines)


def list_available_homes():
    """Get formatted list of home types for purchase."""
    lines = ["|wAvailable Home Types|n", ""]
    
    for key, info in HOME_TYPES.items():
        price_str = "Free" if info["price"] == 0 else f"{info['price']} coins"
        lines.append(f"|y{info['name']}|n ({key}) - {price_str}")
        lines.append(f"  {info['desc']}")
        lines.append(f"  Base Rooms: {info['base_rooms']} | Max Rooms: {info['max_rooms']}")
        lines.append(f"  Furniture: {info['furniture_slots']} | Storage: {info['storage_slots']}")
        if info["features"]:
            lines.append(f"  Features: {', '.join(info['features'])}")
        lines.append("")
    
    return "\n".join(lines)


def list_available_rooms(home_room):
    """Get formatted list of room types available to add."""
    lines = ["|wAvailable Room Types|n", ""]
    
    home_features = home_room.db.features or []
    
    for key, info in ROOM_TYPES.items():
        # Check requirements
        required = info.get("requires_feature")
        available = True
        req_note = ""
        if required and required not in home_features:
            available = False
            req_note = f" |r(requires {required})|n"
        
        adult = info.get("adult_only", False)
        adult_note = " |m[Adult]|n" if adult else ""
        
        status = "" if available else " |x(unavailable)|n"
        
        lines.append(f"|y{info['name']}|n ({key}) - {info['price']} coins{adult_note}{req_note}{status}")
        lines.append(f"  {info['desc']}")
        lines.append(f"  Furniture Slots: {info['furniture_slots']}")
        if info.get("features"):
            lines.append(f"  Features: {', '.join(info['features'])}")
        lines.append("")
    
    return "\n".join(lines)


def list_available_upgrades(home_room):
    """Get formatted list of available upgrades."""
    lines = ["|wAvailable Upgrades|n", ""]
    
    owned = home_room.db.upgrades or []
    
    for key, info in UPGRADES.items():
        if key in owned:
            lines.append(f"|x{info['name']} - OWNED|n")
        else:
            lines.append(f"|y{info['name']}|n ({key}) - {info['price']} coins")
            lines.append(f"  {info['desc']}")
        lines.append("")
    
    return "\n".join(lines)
