# Import Fixes Required

The project currently imports `Room` from `base.py`, but `base.py` contains the Body Action Framework,
not a Room class. These changes are needed to make the room system work.

## Option 1: Create rooms.py (Recommended)

Create a new file `rooms.py` in your typeclasses folder with the Room base class,
then update indoor.py and outdoor.py to import from it.

### Step 1: Copy rooms.py

Copy `/home/claude/clean_output/rooms.py` to your project's typeclasses directory.

### Step 2: Update indoor.py

Change line 8 in `indoor.py`:

```python
# OLD:
from .base import Room

# NEW:
from .rooms import Room
```

### Step 3: Update outdoor.py

Change line 8 in `outdoor.py`:

```python
# OLD:
from .base import Room

# NEW:
from .rooms import Room
```

---

## Option 2: Add Room to base.py

If you prefer not to create a new file, you could add the Room class to base.py,
but this would mix room code with body action code, which isn't clean.

---

## Full rooms.py Content

The rooms.py file includes:

```python
"""
Room Base
=========

Base room class that IndoorRoom and OutdoorRoom inherit from.
"""

from typing import Dict, List, Optional
from random import choice, random

from evennia.objects.objects import DefaultRoom
from evennia import AttributeProperty


class Room(DefaultRoom):
    """
    Base room class for all locations.
    
    Provides:
    - Furniture management
    - NPC population  
    - Partition system
    - Atmosphere/ambient system
    - Shortcode processing
    """
    
    # Basic properties
    short_desc = AttributeProperty(default="")
    is_private = AttributeProperty(default=False)
    is_public = AttributeProperty(default=True)
    room_type = AttributeProperty(default="generic")
    
    # Furniture system
    furniture_list = AttributeProperty(default=list)
    
    # Atmosphere
    atmosphere_preset = AttributeProperty(default="")
    scent = AttributeProperty(default="")
    sounds = AttributeProperty(default="")
    ambient_messages = AttributeProperty(default=list)
    ambient_frequency = AttributeProperty(default=0.1)
    
    # ... (full implementation in rooms.py)
```

See the full file for complete implementation with:
- Furniture management (get, add, remove, filter by type)
- NPC management (get, filter, populate)
- Partition system for cross-room interactions
- Atmosphere presets and ambient messages
- Shortcode processing (<obj:key>, <sys:time>, <cond:...>)
- Enhanced appearance with scent/sounds
- Time-based ambient message triggers

---

## Furniture Integration

After fixing imports, add furniture support to your rooms:

### In your Character class:

```python
from typeclasses.character_mixins import CharacterMixins

class Character(CharacterMixins, DefaultCharacter):
    # ... existing code
```

### In your default cmdset:

```python
from typeclasses.furniture.commands import FurnitureCmdSet

class CharacterCmdSet(default_cmds.CharacterCmdSet):
    def at_cmdset_creation(self):
        super().at_cmdset_creation()
        self.add(FurnitureCmdSet())
```

---

## Testing the Fix

After making changes, test with:

```python
# In Evennia shell
from typeclasses.indoor import IndoorRoom
from typeclasses.outdoor import OutdoorRoom

# Should work without import errors
print(IndoorRoom.__bases__)
print(OutdoorRoom.__bases__)
```
