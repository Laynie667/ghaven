# STUBS & INCOMPLETE SYSTEMS
## Reference Document for Future Implementation

This document tracks all stub code, placeholder functions, and systems that need
completion when building out Character.py and other dependent systems.

---

## OVERVIEW

The following files were created as "world systems" that operate independently
of Character.py. They use `.db` attributes and tags rather than typeclass
properties, allowing them to work on ANY object.

**Files Created:**
- `world/currency.py` - Currency management
- `world/effects.py` - Effects, statuses, transformations
- `world/triggers.py` - Event trigger framework
- `world/resources.py` - Gatherable resource nodes
- `world/random_events.py` - Ambient and world events
- `world/traps.py` - Traps, curses, hazards

---

## STUBS BY FILE

### world/currency.py
**Status: COMPLETE** - No stubs, fully functional.

Operates on any object with `.db` storage. No Character.py dependencies.

**Future Enhancement (not required):**
- Add `character.pay()` convenience method to Character.py
- Add `character.balance` property to Character.py
- Currency initialization in character creation hook

---

### world/effects.py

**STUB: Effect Expiry Timer Scripts**
```python
# Location: _start_expiry_timer() and _cancel_expiry_timer()
# What's Missing: Evennia Script creation for auto-removing timed effects
# Why: Scripts require typeclass definition
# Implementation Needed:
```

Create in `typeclasses/scripts.py`:
```python
class EffectExpiryScript(DefaultScript):
    """
    Script that removes an effect after duration expires.
    """
    def at_script_creation(self):
        self.key = f"effect_expiry_{self.db.effect_key}"
        self.interval = self.db.duration
        self.persistent = False
        self.repeats = 1
    
    def at_repeat(self):
        from world.effects import remove_effect
        if self.obj:
            remove_effect(self.obj, self.db.effect_key, expired=True)
        self.delete()
    
    @classmethod
    def create(cls, target, effect_key, duration):
        script = create_script(
            cls,
            key=f"effect_expiry_{effect_key}",
            obj=target,
            interval=duration,
            persistent=False
        )
        script.db.effect_key = effect_key
        script.db.duration = duration
        return script
```

Then update `world/effects.py`:
```python
def _start_expiry_timer(target, effect_key, duration):
    from typeclasses.scripts import EffectExpiryScript
    EffectExpiryScript.create(target, effect_key, duration)

def _cancel_expiry_timer(target, effect_key):
    script_key = f"effect_expiry_{effect_key}"
    scripts = target.scripts.get(script_key)
    for script in scripts:
        script.delete()
```

---

**STUB: Stat Modifiers**
```python
# Location: STAT_MODIFIERS dict at top of file
# What's Missing: Actual stat system integration
# Why: Stats don't exist yet
# Implementation Needed:
```

When stats exist on Character.py, add:
```python
def get_modified_stat(character, stat_name):
    """Get stat value including effect modifiers."""
    base = getattr(character.db, stat_name, 0)
    
    for effect_key, mods in STAT_MODIFIERS.items():
        if has_effect(character, effect_key):
            base += mods.get(stat_name, 0)
    
    return base
```

---

**STUB: Apply/Remove Messages**
```python
# Location: _get_apply_message() and _get_remove_message()
# What's Missing: Comprehensive message dictionary
# Status: Basic implementation exists, expand as needed
```

---

### world/triggers.py
**Status: MOSTLY COMPLETE**

**STUB: exec Effect Type**
```python
# Location: execute_effect(), "exec" type
# What's Missing: Secure code execution for admin triggers
# Status: Disabled for security
# Implementation: Only enable with heavy restrictions if needed at all
```

---

### world/resources.py

**STUB: Skill Level Checks**
```python
# Location: harvest() function
# What's Missing: Skill system doesn't exist
# Implementation Needed:
```

When skills exist:
```python
# In harvest():
skill_key = data.get("skill_required")
min_level = data.get("min_skill_level", 0)
if skill_key:
    player_skill = get_skill_level(harvester, skill_key)
    if player_skill < min_level:
        return {"success": False, 
                "message": f"You need {skill_key} level {min_level}."}
    
    # Skill affects success rate
    success_chance = 0.5 + (player_skill * 0.05)  # Example formula
    if random.random() > success_chance:
        # Fail message
```

---

**STUB: Respawn Timer Script**
```python
# Location: _consume_harvest() function
# What's Missing: Script to respawn depleted nodes
# Implementation Needed:
```

Create in `typeclasses/scripts.py`:
```python
class ResourceRespawnScript(DefaultScript):
    """
    Script that respawns a depleted resource node.
    """
    def at_script_creation(self):
        self.key = "resource_respawn"
        self.interval = self.db.respawn_time or 300
        self.persistent = True
        self.repeats = 1
    
    def at_repeat(self):
        from world.resources import respawn_node
        if self.obj:
            respawn_node(self.obj)
        self.delete()
```

---

**STUB: ResourceNode Typeclass**
```python
# Location: Commented out class at top
# What's Missing: Actual typeclass inheriting from Object
# Status: Functions work on any object, typeclass is optional sugar
```

Optional - create `typeclasses/objects.py` addition:
```python
class ResourceNode(Object):
    """Gatherable resource node."""
    
    def at_object_creation(self):
        super().at_object_creation()
        from world.resources import create_node_data
        if not self.db.resource_node:
            self.db.resource_node = create_node_data("gather", ["nothing"])
    
    def get_display_name(self, looker, **kwargs):
        from world.resources import is_depleted
        name = super().get_display_name(looker, **kwargs)
        if is_depleted(self, looker):
            return f"|x{name} (depleted)|n"
        return name
```

---

### world/random_events.py

**STUB: RandomEventTickScript**
```python
# Location: Bottom of file (commented)
# What's Missing: Script to periodically fire random events
# Implementation Needed:
```

Create in `typeclasses/scripts.py`:
```python
class RandomEventTickScript(DefaultScript):
    """
    Global script that fires random events periodically.
    """
    def at_script_creation(self):
        self.key = "random_event_ticker"
        self.desc = "Fires random ambient and world events"
        self.interval = 60  # Every 60 seconds
        self.persistent = True
        self.start_delay = True
    
    def at_repeat(self):
        from world.random_events import tick_random_events
        tick_random_events()
```

Start with: `@py from typeclasses.scripts import RandomEventTickScript; RandomEventTickScript.create()`

---

**STUB: Temporary Object Despawn**
```python
# Location: _execute_room_event_effects(), "spawn_temporary" type
# What's Missing: Despawn script for temporary objects
# Implementation Needed: Similar to EffectExpiryScript
```

---

### world/traps.py

**STUB: Container Typeclass**
```python
# Location: create_trapped_container()
# What's Missing: Actual Container typeclass with open/close
# Workaround: Uses base Object, trap triggers on "get" instead of "open"
```

When Container typeclass exists, update to trigger on "open" action.

---

**STUB: Cure Mechanics**
```python
# Location: get_curse_cure() and attempt_curse_removal()
# What's Missing: Full cure system implementation
# Status: Framework exists, specific cures need implementation
```

Expand as Curator/wardrobe/quest systems are built.

---

### world/scenes.py
**Status: COMPLETE** - Core system functional.

**STUB: Delay/Pause**
```python
# Location: advance_scene(), delay handling
# What's Missing: Actual delay between auto-advance nodes
# Status: Shows "press enter to continue" instead
```

Could be enhanced with Evennia's delay_command utility for timed pauses.

---

**STUB: Callbacks**
```python
# Location: on_enter/on_exit node properties
# What's Missing: Callback function execution
# Status: Properties documented but not implemented
```

Add if custom node behavior needed beyond effects.

---

### world/scenes_examples.py
**Status: EXAMPLE CONTENT**

Contains working example scenes:
- `passion_bloom_01` - Plant trap, 4 nodes
- `goblin_ambush_01` - Full encounter, 20+ nodes, multiple paths
- `gate_malfunction_01` - Gate mishap, leads to Curator
- `found_coin_01` - Simple single-node scene
- `fishing_tentacle_01` - Hazard encounter, multiple branches

Add more scenes here or create separate files per content area.

---

## CONTENT MODULES

Pre-built area content in the `content/` directory:

### content/whisperwood.py
**Status: COMPLETE**
- Resources: 8 gatherable nodes (bugs, berries, mushrooms, herbs, amber)
- Hazards: 4 light flora hazards (drowsy, giggle, sticky, blush)
- Triggers: Entry messages, ambient events, time-based effects
- Scenes: 
  - `whisperwood_slime_01` - Curious forest slime (cute)
  - `whisperwood_bugmishap_01` - Hornet nest mishap (comedy)
  - `whisperwood_night_01` - Fae trader encounter (mysterious, has curse path)
  - `whisperwood_mushroom_01` - Strange mushroom (mild hazard)

### content/moonshallow.py
**Status: COMPLETE**
- Resources: 8 gatherable nodes (fish, frogs, lilies, algae)
- Triggers: Entry messages, time-of-day effects
- Scenes:
  - `moonshallow_fishing_01` - Turtle on the line (comedy)
  - `moonshallow_frogs_01` - Frog swarm (cute)
  - `moonshallow_deep_01` - Ancient pond entity (mysterious)
  - `moonshallow_moonlit_01` - Moonlight fish catch (magical)

### content/sunny_meadow.py
**Status: COMPLETE**
- Resources: 10 gatherable nodes (flowers, herbs, butterflies, beehives)
- Hazards: 4 flora hazards (blush rose, passion poppy, dream lily, honey trap)
- Triggers: Entry messages, pollen effects, seasonal
- Scenes:
  - `meadow_bees_01` - Bee nest encounter
  - `meadow_poppy_01` - Passion poppy field (mild adult-adjacent)
  - `meadow_guardian_01` - Flower guardian (rare, rewards/punishes)

### content/copper_hill.py
**Status: COMPLETE**
- Resources: 12 gatherable nodes (ore, gems, fossils, cave bugs, glowing mushrooms)
- Triggers: Cave ambiance, dripping water, ominous sounds
- Scenes:
  - `copper_stuck_01` - Getting stuck in a crevice (comedy)
  - `copper_creature_01` - Something in the dark (mysterious, can bless/warn)
  - `copper_cavein_01` - Cave collapse (action)
  - `copper_crystal_01` - Hidden geode discovery (moral choice)

### content/tidepools.py
**Status: COMPLETE**
- Resources: 10 gatherable nodes (shells, crabs, sea glass, fish, treasure)
- Triggers: Waves, seagulls, tide warnings
- Scenes:
  - `tidepools_crab_01` - Aggressive crab (comedy)
  - `tidepools_tide_01` - Rising tide hazard (action)
  - `tidepools_grab_01` - Something in the pool (mysterious creature)
  - `tidepools_treasure_01` - Buried treasure chest (adventure)
  - `tidepools_mermaid_01` - Mermaid sighting (rare, magical)

---

## INTEGRATION HOOKS

These hooks should be added to typeclasses when building Character.py:

### Trigger → Scene Integration
Add to `world/triggers.py` in `execute_effect()`:
```python
if effect_type == "start_scene":
    from world.scenes import trigger_scene
    return trigger_scene(effect.get("scene"), actor)
```

This allows triggers to start scenes:
```python
add_trigger(room, "enter",
    effects=[{"type": "start_scene", "scene": "goblin_ambush_01"}],
    conditions=[{"type": "random", "chance": 0.1}]
)
```

### typeclasses/objects.py
```python
class Object(DefaultObject):
    def at_get(self, getter, **kwargs):
        """Called after object is picked up."""
        super().at_get(getter, **kwargs)
        # Check for traps
        from world.traps import check_trap
        check_trap(self, getter, "get")
        
        # Check for triggers
        from world.triggers import check_object_triggers
        check_object_triggers(self, getter, "get")
```

### typeclasses/rooms/base_rooms.py
```python
class Room(DefaultRoom):
    def at_object_receive(self, obj, source_location, **kwargs):
        """Called when object enters room."""
        super().at_object_receive(obj, source_location, **kwargs)
        
        # Only for characters with accounts (players)
        if hasattr(obj, 'account') and obj.account:
            # Check room triggers
            from world.triggers import check_room_triggers
            check_room_triggers(self, obj, "enter")
            
            # Check environmental hazards
            from world.traps import check_room_hazard
            check_room_hazard(self, obj)
    
    def at_object_leave(self, obj, target_location, **kwargs):
        """Called when object leaves room."""
        super().at_object_leave(obj, target_location, **kwargs)
        
        if hasattr(obj, 'account') and obj.account:
            from world.triggers import check_room_triggers
            check_room_triggers(self, obj, "exit")
```

### typeclasses/characters.py
```python
class Character(DefaultCharacter):
    def at_object_creation(self):
        """Called when character is first created."""
        super().at_object_creation()
        
        # Initialize currency
        from world.currency import initialize_currency
        initialize_currency(self)
```

---

## SCRIPTS NEEDED

Create these in `typeclasses/scripts.py`:

1. **EffectExpiryScript** - Auto-removes timed effects
2. **ResourceRespawnScript** - Respawns depleted resource nodes
3. **RandomEventTickScript** - Fires ambient/world events
4. **TemporaryObjectScript** - Despawns temporary objects

---

## COMMANDS NEEDED

Create these in `commands/`:

1. **gather/forage/fish/mine** - Harvest from resource nodes
2. **effects/status** - View current effects on self
3. **cure** - Attempt curse removal (if applicable)

---

## TESTING CHECKLIST

After integration, test:

- [ ] Currency: `@py from world.currency import *; receive(me, 100); balance(me)`
- [ ] Effects: `@py from world.effects import *; apply_effect(me, "test", duration=60)`
- [ ] Triggers: Add trigger to room, walk in/out
- [ ] Resources: Create node, harvest multiple times, check depletion
- [ ] Traps: Create cursed item, pick up, verify effect applied
- [ ] Random Events: Start ticker script, wait for events

---

## PRIORITY ORDER

When building Character.py and integrating:

1. **First:** Add hooks to objects.py and base_rooms.py
2. **Second:** Create script typeclasses
3. **Third:** Create gathering commands
4. **Fourth:** Test all systems together
5. **Fifth:** Expand content (more effects, triggers, resources)

---

*Document created: Session of world systems implementation*
*Last updated: Current session*

---

## HOUSING SYSTEM

### world/housing.py
**Status: COMPLETE**

Full player housing with:
- 6 home types (tent through estate)
- 11 room types (bedroom, dungeon, custom, etc.)
- 5 permission levels (stranger through owner)
- 9 purchasable upgrades
- Integration points for furniture/storage

See HOUSING.md for full documentation.

### commands/housing_commands.py
**Status: COMPLETE**

Player commands:
- `home` - Go home / view info / manage home
- `home buy <type>` - Purchase a home
- `home upgrade <type>` - Upgrade to better type
- `home addroom <type>` - Add additional rooms
- `home buyupgrade <key>` - Purchase upgrades
- `home name/desc` - Customization
- `home lock/unlock` - Lock door
- `home perms [name level]` - Manage permissions
- `home invite/kick` - Visitor management
- `knock/enter/visit/leave` - Navigation

**Integration Required:**
Add to default_cmdsets.py:
```python
from commands.housing_commands import HousingCmdSet

class CharacterCmdSet(default_cmds.CharacterCmdSet):
    def at_cmdset_creation(self):
        super().at_cmdset_creation()
        self.add(HousingCmdSet)
```
