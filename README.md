# Gilderhaven World Systems

A collection of standalone game systems for Evennia MUD framework. These systems operate independently of Character.py using `.db` attributes and tags, allowing you to build the world before building characters.

## Installation

```bash
cd ~/Gilderhaven/gilderhaven
unzip -o world_systems_v3.zip
```

## Systems Overview

| System | File | Purpose |
|--------|------|---------|
| Currency | `world/currency.py` | Gold/money management |
| Effects | `world/effects.py` | Buffs, debuffs, curses, transformations |
| Triggers | `world/triggers.py` | Event-driven actions (when X happens, do Y) |
| Resources | `world/resources.py` | Gatherable nodes (fishing, foraging, mining) |
| Random Events | `world/random_events.py` | Ambient flavor and world events |
| Traps | `world/traps.py` | Hazards, curses, defensive creatures |
| Scenes | `world/scenes.py` | Branching interactive narratives |

---

## Currency System

Simple money tracking on any object.

```python
from world.currency import balance, receive, pay, transfer, can_afford

# Give gold
receive(character, 100)  # "You receive 100 gold."

# Check balance
gold = balance(character)  # Returns int

# Spend gold (returns False if broke)
if pay(character, 50):
    print("Paid!")

# Transfer between entities
transfer(alice, bob, 25)

# Check affordability
if can_afford(character, 200):
    print("Can afford it")
```

**Storage:** `character.db.currency` (int)
**Transaction Log:** `character.db.currency_log` (last 50 transactions)

---

## Effects System

Status effects, transformations, curses - anything temporary or permanent that "happens to" someone.

```python
from world.effects import (
    apply_effect, remove_effect, has_effect, get_effects,
    apply_transformation, revert_transformation,
    can_perform
)

# Apply a timed debuff (duration in seconds, 0 = permanent)
apply_effect(character, "poisoned", category="debuff", duration=300)

# Apply permanent curse
apply_effect(character, "in_heat", category="curse")

# Check for effect
if has_effect(character, "transformed"):
    pass

# Get all effects in category
curses = get_effects(character, category="curse")

# Remove effect
remove_effect(character, "poisoned")

# Check if action is blocked
can_act, blocker = can_perform(character, "move")
# Returns (False, "paralyzed") if paralyzed blocks movement

# Transformations (special handling)
apply_transformation(character, "mare_form",
    species="fae_horse",
    features={"ears": "equine", "tail": "horse"},
    duration=86400
)
revert_transformation(character)
```

### Effect Categories
- `buff` - Positive temporary effects
- `debuff` - Negative temporary effects  
- `curse` - Requires cure/removal
- `transformation` - Physical form changes
- `status` - General flags
- `breeding` - Heat, fertility, breeding program
- `museum` - Curator-imposed effects
- `environmental` - Weather/location effects
- `quest` - Quest-related flags

### Blocking Effects
Some effects prevent actions:
- `paralyzed` → blocks: move, attack, flee
- `silenced` → blocks: speak, cast
- `bound` → blocks: move, attack, flee, get, drop
- `blinded` → blocks: look, aim
- `sleeping` → blocks: all
- `stunned` → blocks: all

**Storage:** `character.db.effects` (dict of effect data)

---

## Triggers System

"When X happens, do Y" - the core event engine.

```python
from world.triggers import (
    add_trigger, remove_trigger, check_and_fire_triggers,
    add_entry_message_trigger, add_first_visit_trigger,
    add_pickup_curse_trigger, add_trap_trigger
)

# Add a custom trigger
add_trigger(
    room,
    "enter",  # Trigger type
    effects=[
        {"type": "message", "text": "A chill runs down your spine..."},
        {"type": "apply_effect", "effect_key": "spooked", "duration": 300}
    ],
    conditions=[
        {"type": "time_is", "value": "night"},
        {"type": "random", "chance": 0.3}
    ],
    trigger_id="spooky_entrance",
    once=False,  # Can trigger multiple times
    cooldown=60  # 60 second cooldown per player
)

# Convenience functions
add_entry_message_trigger(room, "The air feels heavy here.")
add_first_visit_trigger(room, "You've never been here before...")
add_pickup_curse_trigger(item, "cursed", duration=3600)
add_trap_trigger(item, "get", "poison", duration=300, chance=0.5)
```

### Trigger Types
**Room:** `enter`, `exit`, `look`, `stay`, `time`, `weather`, `night`, `dawn`
**Object:** `get`, `drop`, `give`, `use`, `look`, `touch`, `equip`, `unequip`, `break`

### Condition Types
```python
{"type": "time_is", "value": "night"}
{"type": "time_in", "values": ["dawn", "dusk"]}
{"type": "weather_is", "value": "storm"}
{"type": "weather_in", "values": ["rain", "storm"]}
{"type": "has_item", "item": "torch"}
{"type": "lacks_item", "item": "key"}
{"type": "has_effect", "effect": "cursed"}
{"type": "lacks_effect", "effect": "immune"}
{"type": "has_tag", "tag": "guild_member", "category": "factions"}
{"type": "lacks_tag", "tag": "banned"}
{"type": "currency_gte", "amount": 100}
{"type": "currency_lt", "amount": 50}
{"type": "random", "chance": 0.3}  # 30% chance
{"type": "first_visit"}
{"type": "is_player"}
{"type": "is_npc"}
{"type": "attr_equals", "attr": "species", "value": "human"}
{"type": "always"}
{"type": "never"}
```

### Effect Types
```python
{"type": "message", "text": "You feel strange..."}
{"type": "message_room", "text": "The torches flicker.", "exclude_actor": True}
{"type": "apply_effect", "effect_key": "cursed", "category": "curse", "duration": 3600}
{"type": "remove_effect", "effect_key": "blessed"}
{"type": "transform", "transform_key": "wolf", "species": "wolf", "duration": 3600}
{"type": "give_currency", "amount": 50}
{"type": "take_currency", "amount": 25}
{"type": "teleport", "destination": "#123"}  # dbref or key
{"type": "give_item", "key": "rusty key", "typeclass": "typeclasses.objects.Object"}
{"type": "take_item", "key": "entry pass"}
{"type": "set_attr", "attr": "visited", "value": True}
{"type": "add_tag", "tag": "marked", "category": "curses"}
{"type": "remove_tag", "tag": "innocent"}
{"type": "spawn_object", "key": "ghost", "typeclass": "..."}
{"type": "chain_trigger", "trigger_id": "second_trap"}
{"type": "start_scene", "scene": "goblin_ambush_01"}
```

**Storage:** `object.db.triggers` (list of trigger dicts)

---

## Resources System

Gatherable nodes - fishing spots, fruit trees, ore veins, herb patches.

```python
from world.resources import (
    create_resource_node, harvest, is_depleted, respawn_node,
    create_apple_tree, create_fishing_spot, create_ore_vein,
    create_herb_patch, create_bug_spot
)

# Create custom resource
node = create_resource_node(
    room,
    "apple tree",
    resource_type="forage",
    yields=[
        {"key": "apple", "rarity": "common", "weight": 80},
        {"key": "golden apple", "rarity": "rare", "weight": 5},
        {"key": "worm", "rarity": "uncommon", "weight": 15},
    ],
    max_harvests=5,
    respawn_time=600,  # 10 minutes
    seasons=["summer", "autumn"],
    per_player=False  # Global depletion
)

# Pre-built templates
create_apple_tree(room)
create_fishing_spot(room, "quiet pond")
create_ore_vein(room, "gold")
create_herb_patch(room)
create_bug_spot(room, "flower garden")

# Harvest
result = harvest(node, character)
# Returns: {
#   "success": True,
#   "message": "You pick a ripe apple!",
#   "yield": <Object>,
#   "quality": 7,
#   "rarity": "common"
# }
```

### Resource Types
| Type | Tool Required | Default Verb |
|------|---------------|--------------|
| forage | None | pick |
| fishing | fishing rod | catch |
| mining | pickaxe | mine |
| bugs | net | catch |
| logging | axe | chop |
| gather | None | gather |

### Rarity Tiers
- `common` - 70% base weight
- `uncommon` - 20%
- `rare` - 8%
- `epic` - 1.8%
- `legendary` - 0.2%

**Storage:** `node.db.resource_*` (various attributes)

---

## Random Events System

Ambient flavor and mechanical events that happen in the world.

```python
from world.random_events import (
    fire_ambient_event, fire_room_event, fire_personal_event,
    fire_world_event, tick_random_events, register_ambient_events
)

# Register which ambient events can fire in a room
register_ambient_events(room, ["rustling_leaves", "bird_song", "whispers"])

# Fire events manually
fire_ambient_event(room)      # Random flavor text
fire_room_event(room)         # Event with possible effects
fire_personal_event(character) # Something happens TO them
fire_world_event()            # Global event (shooting star, eclipse)

# Tick function (call from global script)
tick_random_events()  # Processes all occupied rooms
```

### Event Categories

**Ambient (flavor only):**
`rustling_leaves`, `bird_song`, `owl_hoot`, `distant_thunder`, `merchant_call`, `magical_shimmer`, `whispers`, `scurrying`

**Room Events (can spawn objects):**
`wandering_merchant`, `guard_patrol`, `dropped_coin`, `rare_butterfly`

**Personal Events:**
`pocket_lint`, `sneeze`, `yawn`, `pocket_picked` (lose gold), `lucky_find` (gain gold)

**World Events:**
`shooting_star`, `rainbow`, `eclipse`, `market_sale`

---

## Traps System

Hazardous objects, cursed items, defensive flora/fauna.

```python
from world.traps import (
    create_cursed_item, create_hazardous_plant, create_defensive_creature,
    create_trapped_container, setup_hazard_room, check_trap
)

# Cursed artifact
idol = create_cursed_item(room, "ancient idol", 
    curse_type="transformation_gradual",
    chance=1.0,
    species="frog"
)

# Hazardous plant
bloom = create_hazardous_plant(room, "passion bloom",
    hazard_type="pollen_fertility",
    chance=0.3
)

# Defensive creature
beetle = create_defensive_creature(room, "musk beetle",
    defense_type="spray_pheromone",
    chance=0.5
)

# Trapped chest
chest = create_trapped_container(room, "ornate chest",
    trap_effect="sting_venom",
    loot=["gold coins", "ruby"]
)

# Environmental hazard (affects all who enter)
setup_hazard_room(room, "pollen_fertility", chance=0.2)
```

### Curse Types
`transformation_gradual`, `transformation_instant`, `compulsion`, `attraction`, `heat_permanent`, `size_change`, `gender_change`, `species_drift`

### Defense Mechanisms
`spray_pheromone`, `sting_venom`, `spores_parasitic`, `ink_blind`, `song_compel`, `touch_bond`, `pollen_fertility`, `sap_adhesive`, `thorns_aphrodisiac`, `scent_predator`, `nectar_addiction`

---

## Scenes System

Branching interactive narratives for encounters, events, and anything that needs text + choices + effects without building a full NPC.

See **SCENES.md** for complete documentation.

```python
from world.scenes import start_scene, get_scene, register_scene

# Start a registered scene
start_scene(character, get_scene("goblin_ambush_01"))

# Or define and start inline
my_scene = {
    "start": {
        "text": "Something happens!",
        "choices": [
            {"text": "Do thing A", "goto": "result_a"},
            {"text": "Do thing B", "goto": "result_b"},
        ]
    },
    "result_a": {"text": "A happened.", "end": True},
    "result_b": {"text": "B happened.", "end": True},
}
start_scene(character, my_scene)
```

---

## Integration Hooks

Add these to your typeclasses when ready:

### typeclasses/objects.py
```python
def at_get(self, getter, **kwargs):
    from world.triggers import check_and_fire_triggers
    from world.traps import check_trap
    check_trap(self, getter, "get")
    check_and_fire_triggers(self, "get", getter)
```

### typeclasses/rooms.py  
```python
def at_object_receive(self, obj, source_location, **kwargs):
    if obj.has_account:  # Is a character
        from world.triggers import check_and_fire_triggers
        from world.traps import check_room_hazard
        check_and_fire_triggers(self, "enter", obj)
        check_room_hazard(self, obj)
```

---

## Quick Test Commands

```
# Currency
@py from world.currency import receive, balance; receive(me, 100); balance(me)

# Effects  
@py from world.effects import apply_effect, has_effect; apply_effect(me, "test", duration=60); has_effect(me, "test")

# Scene
@py from world.scenes import start_scene, get_scene; start_scene(me, get_scene("goblin_ambush_01"))

# Clear scene if stuck
@py me.db.active_scene = None; me.db.active_scene_data = None; me.cmdset.remove("scene_commands")
```
