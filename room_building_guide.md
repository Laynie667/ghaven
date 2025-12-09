# Room Building Guide - Gilderhaven
## Complete Reference for Room Creation

---

## Table of Contents

1. [Room Type Hierarchy](#room-type-hierarchy)
2. [Basic Room Creation](#basic-room-creation)
3. [Grid Rooms (Positions Within Rooms)](#grid-rooms)
4. [Spatial Awareness (Between Rooms)](#spatial-awareness)
5. [Partitions](#partitions)
6. [Overlooks (Balconies, Windows)](#overlooks)
7. [Adjacency (Nearby Rooms)](#adjacency)
8. [Combining Systems](#combining-systems)
9. [Builder Commands](#builder-commands)
10. [Examples by Location Type](#examples)

---

## Room Type Hierarchy

```
DefaultRoom (Evennia)
    └── Room (base_rooms.py)
            ├── IndoorRoom
            │       └── GridIndoorRoom
            └── OutdoorRoom
                    └── GridOutdoorRoom
                    
SpatialMixin can be added to ANY of these:
    class MyRoom(SpatialMixin, IndoorRoom):
        pass
```

### When to Use What

| Room Type | Use For |
|-----------|---------|
| `Room` | Generic spaces |
| `IndoorRoom` | Buildings, caves, enclosed spaces |
| `OutdoorRoom` | Streets, plazas, forests |
| `GridRoom` | Large spaces where position matters |
| `SpatialMixin` | Rooms that see/hear other rooms |

---

## Basic Room Creation

### Minimal Room

```python
from evennia import create_object

room = create_object(
    "typeclasses.rooms.Room",
    key="Market Square",
    attributes=[
        ("desc", "A bustling market square filled with vendors.")
    ]
)
```

### Indoor Room with Atmosphere

```python
from typeclasses.rooms import IndoorRoom
from typeclasses.base_rooms import ATMOSPHERE_PRESETS

room = create_object(
    IndoorRoom,
    key="Dusty Library",
    attributes=[
        ("desc", "Tall shelves line every wall, heavy with ancient tomes."),
        ("atmosphere", ATMOSPHERE_PRESETS["dusty"]),
    ]
)
```

### Outdoor Room with Time/Weather

```python
from typeclasses.rooms import OutdoorRoom

room = create_object(
    OutdoorRoom,
    key="Forest Path",
    attributes=[
        ("desc", "A winding path through ancient oaks."),
        ("time_descriptions", {
            "dawn": "Golden light filters through the leaves.",
            "day": "Dappled sunlight plays across the path.",
            "dusk": "Long shadows stretch between the trees.",
            "night": "Moonlight barely penetrates the canopy.",
        }),
    ]
)
```

---

## Grid Rooms

Grid rooms track WHERE in the room someone is. Use for large spaces where position matters.

### Creating a Grid Room

```python
from typeclasses.rooms.grid import GridRoom, GridPosition, create_plaza_grid

# Method 1: Use helper function
room = create_object(GridRoom, key="Town Square")
create_plaza_grid(room, size=5)  # Creates center, edges, corners

# Method 2: Manual positions
room = create_object(GridRoom, key="Long Hall")
room.add_position(GridPosition(
    name="entrance",
    x=0, y=0,
    desc="You stand near the grand entrance doors.",
    short_desc="by the entrance"
))
room.add_position(GridPosition(
    name="throne",
    x=0, y=4,
    desc="The throne looms before you, carved from black stone.",
    short_desc="before the throne"
))
room.default_position = "entrance"
```

### Grid Position Properties

```python
GridPosition(
    name="fountain",           # Position name
    x=2, y=2,                  # Coordinates
    desc="...",                # Full description when here
    short_desc="...",          # Brief location note
    features=["fountain"],     # Interactable things here
    blocks_movement=False,     # Can't walk through?
    blocks_sight=False,        # Can't see past?
)
```

### Moving Characters Within Grid

```python
# Set someone's position
room.set_character_position(character, "fountain")

# Get someone's position
pos = room.get_character_position(character)
print(pos.name)  # "fountain"

# Get everyone at a position
chars = room.get_characters_at_position("fountain")

# Check visibility between positions
visible = room.get_visible_positions("entrance")
```

---

## Spatial Awareness

The Spatial system handles perception BETWEEN rooms. Three tools:

1. **Adjacency** - Nearby rooms (market stalls)
2. **Overlooks** - Vertical views (balconies)
3. **Partitions** - Barriers (iron bars, glass)

### Adding SpatialMixin

```python
from typeclasses.rooms.spatial import SpatialMixin
from typeclasses.rooms import IndoorRoom

class MuseumRoom(SpatialMixin, IndoorRoom):
    """Museum room with spatial awareness."""
    pass
```

Or use `SpatialRoom` directly:

```python
from typeclasses.rooms.spatial import SpatialRoom

room = create_object(SpatialRoom, key="Guard Post")
```

---

## Partitions

Barriers between spaces that control what senses pass through.

### Partition Types

| Type | See | Hear | Smell | Pass |
|------|-----|------|-------|------|
| `OPEN` | ✓ | ✓ | ✓ | ✓ |
| `IRON_BARS` | ✓ | ✓ | ✓ | ✗ |
| `GLASS_WALL` | ✓ | muffled | ✗ | ✗ |
| `WINDOW_CLOSED` | ✓ | muffled | ✗ | ✗ |
| `WINDOW_OPEN` | ✓ | ✓ | ✓ | ✗ |
| `GRATE` | ✓ | ✓ | ✓ | ✗ |
| `CURTAIN` | ✗ | ✓ | ✓ | ✓ |
| `THIN_WALL` | ✗ | muffled | ✗ | ✗ |
| `THICK_WALL` | ✗ | ✗ | ✗ | ✗ |
| `DOOR_CLOSED` | ✗ | muffled | ✗ | ✗ |
| `DOOR_OPEN` | ✓ | ✓ | ✓ | ✓ |
| `WATER_SURFACE` | distorted | muffled | ✗ | ✓ |

### Creating Partitions

```python
from typeclasses.rooms.spatial import (
    setup_partition, PartitionType, PartitionLink
)

# Helper function (recommended)
setup_partition(
    guard_room, cell_1,
    PartitionType.IRON_BARS,
    desc="iron bars",
    bidirectional=True
)

# Manual method
guard_room.add_partition(PartitionLink(
    room_key=cell_1.key,
    partition_type=PartitionType.IRON_BARS,
    desc="iron bars",
    can_toggle=False,
))
```

### Toggleable Partitions (Windows, Doors)

```python
setup_partition(
    bedroom, balcony,
    PartitionType.WINDOW_CLOSED,
    desc="glass window",
    can_toggle=True,
    toggle_to=PartitionType.WINDOW_OPEN
)

# Later, to toggle:
bedroom.toggle_partition(balcony.key)
```

---

## Overlooks

One-way vertical views - balconies, cliffs, towers.

### Creating an Overlook

```python
from typeclasses.rooms.spatial import (
    setup_overlook, Distance, Direction, Overlook
)

# Helper function
setup_overlook(
    balcony, main_hall,
    view_desc="The grand hall spreads below, marble floors gleaming.",
    distance=Distance.MEDIUM,
    perceive_watcher=True,
    watcher_desc="A figure watches from the balcony above."
)

# Manual method
balcony.add_overlook(Overlook(
    room_key=main_hall.key,
    direction=Direction.BELOW,
    distance=Distance.MEDIUM,
    view_desc="The grand hall spreads below...",
    perceive_watcher=True,
    watcher_desc="A figure watches from the balcony above."
))
```

### Distance Affects Detail

| Distance | What You See |
|----------|--------------|
| `CLOSE` | Names, actions, hear conversation |
| `MEDIUM` | Names, general activity |
| `FAR` | Count ("several figures") |
| `DISTANT` | Presence only ("movement") |

### What People Below See

When `perceive_watcher=True`, people in the overlooked room see:

```
Grand Hall
[description]

A figure watches from the balcony above.
```

---

## Adjacency

Nearby rooms you can perceive but must move to reach.

### Creating Adjacency

```python
from typeclasses.rooms.spatial import (
    link_adjacent_rooms, Adjacency, Distance
)

# Helper (bidirectional)
link_adjacent_rooms(
    stall_north, stall_south,
    direction1="south",
    direction2="north",
    distance=Distance.CLOSE,
    view_desc1="A fish stall with the day's catch.",
    view_desc2="A fruit vendor arranging apples."
)

# Manual (one-way)
stall_north.add_adjacent(Adjacency(
    room_key=stall_south.key,
    direction="south",
    distance=Distance.CLOSE,
    view_desc="A fish stall with the day's catch."
))
```

### What Players See

```
Fruit Stall
You stand at Mira's fruit stall...

Nearby you can see:
  South: A fish stall with the day's catch. (Grum, a customer)
  East: A spice merchant's tent. (Empty)
  North: The main square. (Several figures)
```

---

## Combining Systems

### Grid Room + Spatial Awareness

A large hall with positions AND views to other rooms:

```python
from typeclasses.rooms.spatial import SpatialMixin
from typeclasses.rooms.grid import GridRoomMixin, GridPosition
from typeclasses.rooms import IndoorRoom

class GrandHall(SpatialMixin, GridRoomMixin, IndoorRoom):
    """Large hall with internal positions and external views."""
    pass

# Create
hall = create_object(GrandHall, key="Grand Hall")

# Add internal positions
hall.add_position(GridPosition(name="entrance", x=2, y=0))
hall.add_position(GridPosition(name="center", x=2, y=2))
hall.add_position(GridPosition(name="throne", x=2, y=4))

# Add overlook from balcony
setup_overlook(balcony, hall, view_desc="The hall below...")

# Add partition to side chamber
setup_partition(hall, side_chamber, PartitionType.CURTAIN, desc="velvet curtain")
```

### Museum Example

```python
# Main hall with display alcoves behind glass
setup_partition(
    main_hall, fossil_display,
    PartitionType.GLASS_WALL,
    desc="thick display glass"
)

# Curator can watch from office window
setup_overlook(
    curator_office, main_hall,
    view_desc="The main exhibition hall, visitors wandering between displays.",
    distance=Distance.MEDIUM,
    watcher_desc="Someone watches from an office window above."
)

# Holding cells with iron bars
setup_partition(
    guard_station, cell_1,
    PartitionType.IRON_BARS,
    desc="iron bars"
)
```

### Jail Block Example

```python
# Guard station sees all cells
for i, cell in enumerate(cells):
    setup_partition(
        guard_station, cell,
        PartitionType.IRON_BARS,
        desc=f"iron bars of cell {i+1}"
    )

# Cells don't see each other (stone walls between)
# No partition = no perception
```

### Tavern Private Rooms

```python
# Private booth behind curtain
setup_partition(
    main_bar, private_booth,
    PartitionType.CURTAIN,
    desc="heavy curtain"
)
# Can't see through, CAN hear (gossip risk!)
```

---

## Builder Commands

### In-Game Room Creation

```
@create/drop Market Stall:typeclasses.rooms.spatial.SpatialRoom
@desc here = A cramped market stall...
```

### Adding Spatial Links In-Game

You'll want to create builder commands. Example command structure:

```python
# @partition here = other_room : iron_bars : "iron bars"
# @overlook here = lower_room : "The courtyard below" : medium
# @adjacent here = next_room : north : "A neighboring stall" : close
```

### Batch Building

```python
# In a batch file or script:
from typeclasses.rooms.spatial import *

rooms = {
    "guard": create_object(SpatialRoom, key="Guard Station"),
    "cell1": create_object(SpatialRoom, key="Cell 1"),
    "cell2": create_object(SpatialRoom, key="Cell 2"),
}

setup_partition(rooms["guard"], rooms["cell1"], PartitionType.IRON_BARS, "iron bars")
setup_partition(rooms["guard"], rooms["cell2"], PartitionType.IRON_BARS, "iron bars")
```

---

## Examples by Location Type

### Market District

```python
# Create stalls as adjacent rooms
stalls = []
for i, name in enumerate(["Fish", "Fruit", "Spice", "Cloth"]):
    stall = create_object(SpatialRoom, key=f"{name} Stall")
    stalls.append(stall)

# Link them all as adjacent (can see neighbors)
for i, stall in enumerate(stalls):
    if i > 0:
        link_adjacent_rooms(
            stalls[i-1], stall,
            direction1="east", direction2="west",
            distance=Distance.CLOSE
        )
```

### Prison Block

```python
guard = create_object(SpatialRoom, key="Guard Station")
cells = [create_object(SpatialRoom, key=f"Cell {i}") for i in range(1, 5)]

for cell in cells:
    setup_partition(guard, cell, PartitionType.IRON_BARS, "iron bars")
    # Guard sees all cells, cells see guard, cells don't see each other
```

### Mansion with Balcony

```python
ballroom = create_object(SpatialRoom, key="Ballroom")
balcony = create_object(SpatialRoom, key="Upper Balcony")

setup_overlook(
    balcony, ballroom,
    view_desc="The ballroom spreads below, couples dancing across marble.",
    distance=Distance.MEDIUM
)

# Connect with stairs (normal exit)
create_object(
    "typeclasses.exits.Exit",
    key="stairs down",
    location=balcony,
    destination=ballroom
)
```

### Museum Display

```python
main_hall = create_object(SpatialRoom, key="Fossil Hall")
display = create_object(SpatialRoom, key="T-Rex Display")

setup_partition(
    main_hall, display,
    PartitionType.GLASS_WALL,
    desc="reinforced display glass"
)
# Players can see the fossil but can't touch it
```

---

## Quick Reference

### Imports

```python
# Grid system
from typeclasses.rooms.grid import (
    GridRoom, GridPosition, GridRoomMixin,
    create_plaza_grid, create_linear_grid
)

# Spatial system
from typeclasses.rooms.spatial import (
    SpatialMixin, SpatialRoom,
    Adjacency, Overlook, PartitionLink,
    Distance, Direction, PartitionType,
    link_adjacent_rooms, setup_overlook, setup_partition
)

# Base rooms
from typeclasses.rooms import Room, IndoorRoom, OutdoorRoom
```

### Perception Summary

| System | What It Does | Example |
|--------|--------------|---------|
| Grid Positions | Where in THIS room | "by the fountain" |
| Adjacency | See into NEARBY rooms | Market stall neighbors |
| Overlooks | See DOWN/UP into rooms | Balcony → hall |
| Partitions | See THROUGH barriers | Iron bars, glass |

### Sensory Propagation

```python
# Sound travels through partitions that allow it
room.propagate_sound("Help! Guards!", volume="shout")

# Gets sent to:
# - Adjacent rooms (based on distance + volume)
# - Partitioned rooms (if can_hear is True)
# - Overlooked rooms (sound carries)
```

---

## Troubleshooting

### "Room doesn't have SpatialMixin"

Make sure your room class inherits from `SpatialMixin`:

```python
class MyRoom(SpatialMixin, Room):
    pass
```

### Partitions not showing

Check that both rooms have the mixin and the partition is set up:

```python
print(room1.get_all_partitions())  # Should show the partition
print(room2.get_all_partitions())  # If bidirectional
```

### Overlooks not registering watchers

The target room needs `overlooked_by` populated. Use `setup_overlook()` which does this automatically, or manually:

```python
target_room.overlooked_by = ["balcony_room_key"]
```

### Grid positions not tracking

Make sure characters enter through proper hooks:

```python
# Characters need to trigger at_object_receive
character.move_to(room)  # This triggers hooks
```

---

*Last updated: December 2024*
*For Gilderhaven MUD - Evennia Framework*
