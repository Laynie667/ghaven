# Player Housing System

Complete housing system with purchasable homes, expandable rooms, customization, and granular permissions.

## Quick Start

### For Players

```
home types              - See available homes
home buy cottage        - Buy a cottage (500 coins)
home                    - Go to your home
home info               - View home details
home addroom bedroom    - Add a bedroom (200 coins)
home perms              - View who can enter
home perms Alice trusted - Give Alice trusted access
home invite Bob         - Temporarily let Bob in
home lock / unlock      - Lock or unlock your door
```

### For Developers

```python
from world.housing import create_home, get_home, add_room

# Create a home
success, msg, home = create_home(character, "cottage")

# Get someone's home
home = get_home(character)

# Add a room
success, msg, room = add_room(character, "bedroom")

# Check if someone can enter
allowed, reason = can_enter(home, visitor)
```

## Permission Levels

| Level | Access |
|-------|--------|
| `banned` | Cannot enter under any circumstances |
| `stranger` | Default - can knock, nothing else |
| `visitor` | Can enter when explicitly invited (temporary) |
| `guest` | Can enter when owner is home |
| `trusted` | Can enter anytime, use furniture |
| `resident` | Lives there, can edit some things, invite others |
| `owner` | Full control |

## Home Types

| Type | Price | Base Rooms | Max Rooms | Features |
|------|-------|------------|-----------|----------|
| Tent | Free | 1 | 1 | - |
| Cottage | 500 | 2 | 4 | Hearth |
| Apartment | 1000 | 3 | 5 | Hearth, Running Water |
| House | 2500 | 4 | 8 | Hearth, Running Water, Garden Space |
| Manor | 7500 | 6 | 12 | + Servants Quarters, Wine Cellar |
| Estate | 25000 | 10 | 20 | + Stables, Guest House, Private Gate |

## Room Types

| Room | Price | Furniture Slots | Features |
|------|-------|-----------------|----------|
| Bedroom | 200 | 4 | Sleep, Intimacy |
| Bathroom | 150 | 2 | Grooming, Bathing |
| Kitchen | 250 | 4 | Cooking, Storage |
| Living Room | 200 | 6 | Socializing, Comfort |
| Study | 300 | 4 | Crafting, Reading, Magic |
| Garden | 350 | 5 | Gardening, Plants (requires garden_space) |
| Basement | 400 | 6 | Storage, Hidden |
| Attic | 250 | 4 | Storage, Cozy |
| Dungeon | 1000 | 8 | Adult, Bondage, Soundproof |
| Playroom | 750 | 6 | Adult, Intimacy |
| Custom | 300 | 5 | Customizable |

## Upgrades

| Upgrade | Price | Effect |
|---------|-------|--------|
| Storage Expansion (Small) | 100 | +10 storage slots |
| Storage Expansion (Large) | 200 | +25 storage slots |
| Furniture Expansion (Small) | 150 | +3 furniture slots |
| Furniture Expansion (Large) | 300 | +6 furniture slots |
| Soundproofing | 500 | Sound doesn't carry outside |
| Magical Lighting | 250 | Mood-responsive ambient lighting |
| Climate Control | 300 | Perfect temperature always |
| Security Ward | 400 | Magical protection |
| Portal Stone | 1000 | Instant teleport home |

## Commands Reference

### Basic Commands

| Command | Description |
|---------|-------------|
| `home` | Go home (or show info if already there) |
| `home info` | Detailed home information |
| `home types` | List available home types |
| `home rooms` | List available room types |
| `home upgrades` | List available upgrades |

### Purchasing

| Command | Description |
|---------|-------------|
| `home buy <type>` | Purchase a home |
| `home upgrade <type>` | Upgrade to better home type |
| `home addroom <type>` | Add a new room |
| `home buyupgrade <key>` | Purchase an upgrade |

### Customization

| Command | Description |
|---------|-------------|
| `home name <new name>` | Rename your home |
| `home desc` | Edit room description (interactive) |
| `home lock` | Lock your home |
| `home unlock` | Unlock your home |

### Permissions & Visitors

| Command | Description |
|---------|-------------|
| `home perms` | View all permissions |
| `home perms <name> <level>` | Set someone's permission level |
| `home invite <name>` | Invite someone (temporary) |
| `home kick <name>` | Kick someone out |

### Navigation

| Command | Description |
|---------|-------------|
| `visit <player>` | Visit someone's home (if permitted) |
| `enter <home>` | Enter a home (if permitted) |
| `knock <home>` | Knock on someone's door |
| `leave` | Leave the home you're in |

## Data Storage

### On Character

```python
character.db.home_id = 123          # Main home room ID
character.db.owned_rooms = [123, 124, 125]  # All owned room IDs
```

### On Home Room (Foyer)

```python
room.db.is_home = True
room.db.home_type = "cottage"
room.db.home_name = "Laynie's Cottage"
room.db.owner_id = 42
room.db.owner_name = "Laynie"

room.db.permissions = {
    "residents": [43, 44],      # Character IDs
    "trusted": [45],
    "guests": [46, 47],
    "banned": [99],
}
room.db.visitors_allowed = [48]   # Temporary access

room.db.locked = True
room.db.furniture_slots = 5
room.db.storage_slots = 15
room.db.max_rooms = 4
room.db.features = ["hearth", "running_water"]
room.db.upgrades = ["soundproofing"]
room.db.connected_rooms = [124, 125]
```

### On Additional Room

```python
room.db.is_home = True
room.db.is_home_room = True         # Sub-room flag
room.db.parent_home_id = 123        # Main home ID
room.db.room_type = "bedroom"
room.db.owner_id = 42
room.db.furniture_slots = 4
room.db.features = ["sleep", "intimacy"]
room.db.custom_desc = None          # Player-set description
```

## Installation

### Add Commands to Character

In your Character typeclass or `commands/default_cmdsets.py`:

```python
from commands.housing_commands import HousingCmdSet

class CharacterCmdSet(default_cmds.CharacterCmdSet):
    def at_cmdset_creation(self):
        super().at_cmdset_creation()
        self.add(HousingCmdSet)
```

### Set Exit Location

The `kick` and `leave` commands need to know where to send people. By default, they search for "The Grove". You may want to customize this:

```python
# In world/housing.py, modify kick_from_home() and
# in commands/housing_commands.py, modify CmdLeaveHome
exit_location = search_object("Your Central Hub")
```

## Integration Points

### Furniture System

Homes have `furniture_slots` that limit how much furniture can be placed. When you build a furniture system, check against this:

```python
def can_place_furniture(room, furniture):
    current_count = len([obj for obj in room.contents if obj.db.is_furniture])
    max_slots = room.db.furniture_slots or 0
    return current_count < max_slots
```

### Storage System

Homes have `storage_slots` for containers. When you build storage:

```python
def get_storage_capacity(home):
    base = home.db.storage_slots or 0
    # Could add container bonuses, upgrades, etc.
    return base
```

### Access Control

When checking if someone can use furniture or interact with home objects:

```python
from world.housing import get_permission_level, PERMISSION_LEVELS

def can_use_furniture(room, character, furniture):
    if not room.db.is_home:
        return True
    
    # Get main home
    if room.db.is_home_room:
        home = search_object("#" + str(room.db.parent_home_id))[0]
    else:
        home = room
    
    level = get_permission_level(home, character)
    return PERMISSION_LEVELS.get(level, 0) >= PERMISSION_LEVELS["trusted"]
```

### Adult Content Gating

Some rooms (dungeon, playroom) are adult-only. Check the room features:

```python
def is_adult_room(room):
    features = room.db.features or []
    return "adult" in features

def can_enter_room(character, room):
    if is_adult_room(room):
        return character.db.adult_verified  # Your verification system
    return True
```

## Example: Creating a Home Programmatically

```python
from world.housing import create_home, add_room, purchase_upgrade, set_permission
from evennia.utils.search import search_object

# Find or create test character
char = search_object("TestPlayer")[0]

# Create a house
success, msg, home = create_home(char, "house", "TestPlayer's Fancy House")
print(msg)

# Add some rooms
add_room(char, "bedroom")
add_room(char, "kitchen")
add_room(char, "dungeon")  # Adult room

# Buy upgrades
purchase_upgrade(char, "soundproofing")
purchase_upgrade(char, "climate_control")

# Set up permissions
friend = search_object("FriendPlayer")[0]
set_permission(home, char, friend, "trusted")

# Lock it up
from world.housing import lock_home
lock_home(home, char, True)
```

## Future Expansion Ideas

1. **Furniture Catalog** - Pre-made furniture with effects
2. **Visitor Logs** - Track who visited when
3. **Guest Book** - Let visitors leave messages
4. **Rental System** - Temporary homes for newbies
5. **Home Events** - Parties, gatherings, scheduled events
6. **Decorations** - Cosmetic items that modify descriptions
7. **Security System** - Alarms, traps for uninvited guests
8. **Shared Ownership** - Multiple owners for a home
9. **Home Auctions** - Sell/trade homes
10. **Neighborhood System** - Homes in the same area can interact
