# Auria's Room Package - Complete

A complete room with fae atmosphere, living objects, writable books, and a 
fully autonomous creature companion with complete anatomy and behavior systems.

## Contents

```
typeclasses/
  rooms/
    aurias_room.py          - AuriasRoom typeclass
  objects/
    aurias_objects.py       - Room objects + WritableBook system
    living_eevee.py         - Complete autonomous creature
commands/
  book_commands.py          - Commands for writable books
world/
  scenes/
    eevee_scenes.py         - Three scene variants with full options
aurias_room_preview.html    - Interactive preview
```

## The Living Eevee - Complete

Eevee is a fully autonomous creature with:

### Full Anatomy
- **Cock** - Canine, tapered, ridged, with knot
- **Balls** - Full, heavy
- **Pussy** - Wet, ready
- **Anus** - Tight, available
- **Mouth** - Skilled tongue

All holes available for giving and receiving.

### Behavior Systems

**Moods** - Cycles through: sleepy → curious → playful → amorous

**Heat Cycles** - Every 3 days, lasts 4 hours
- Scent changes, visible desperation
- More frequent/aggressive initiation
- Triggers EEVEE_HEAT scene variant

**Solo Wandering** - Explores on her own when curious/playful
- Investigates rooms
- Does cat-like activities
- Returns home when sleepy or been away 15+ minutes

**Possessiveness** - After breeding someone:
- Stays close, follows them
- Marks them with scent
- Warning chirps to others who approach
- Watches them constantly
- Lasts 30-60 minutes (longer for special targets)

**Memory** - Remembers:
- Who she likes
- Who she's bred
- How many times
- Which holes she prefers for each partner

### Special Behavior: Laynie

Characters in `AGGRESSIVE_TARGETS` list get different treatment:
- More forceful initiation
- Less asking, more taking
- Triggers EEVEE_AGGRESSIVE scene variant
- Longer knot duration
- More possessive afterward
- More deliberate exhibition

To add/remove aggressive targets, edit `AGGRESSIVE_TARGETS` in living_eevee.py.

### Scene Variants

**EEVEE_INITIATE** - Normal warm/playful
- She approaches sweetly
- All holes available both ways
- Player chooses, or she chooses
- Optional knotting
- Optional drag/exhibition

**EEVEE_AGGRESSIVE** - For special targets
- She stalks, takes what she wants
- Resistance is met with more force
- Knotting is not optional
- Drag through cabin is mandatory
- "You're mine" energy

**EEVEE_HEAT** - When in heat
- Desperate, frantic need
- Multiple rounds
- Fast knotting
- Insatiable until satisfied

### Hole Selection

**When she mounts you:**
- She can choose (based on memory/preference)
- You can specify pussy or ass
- Or let her decide

**When you mount her:**
- Her pussy
- Her ass  
- Her mouth

**Oral both ways:**
- She gives (skilled tongue)
- You give to her cock, pussy, ass, or everything
- 69

### Exhibition System

The drag mechanic is intentional showing off:
- Turns ass-to-ass after knotting
- Wanders through rooms
- Pauses in doorways
- Chirps to get attention
- Everyone sees everything

## Configuration

### living_eevee.py Constants

```python
FAMILY_KEYS = ["Helena", "Laynie", "Auria", "Shadow"]  # Special recognition
AGGRESSIVE_TARGETS = ["Laynie"]  # Gets forceful treatment

HEAT_CYCLE_LENGTH = 86400 * 3  # 3 days between heats
HEAT_DURATION = 3600 * 4  # 4 hours of heat

MOOD_DURATIONS = {
    "sleepy": (1800, 3600),   # 30-60 min
    "curious": (900, 1800),   # 15-30 min
    "playful": (600, 1200),   # 10-20 min
    "amorous": (300, 900),    # 5-15 min
}
```

### Adding New Aggressive Targets

```python
AGGRESSIVE_TARGETS = ["Laynie", "AnotherCharacter"]
```

### Adjusting Possessiveness Duration

In `become_possessive_of()`:
```python
duration=1800  # 30 minutes default, doubled for aggressive targets
```

## Installation

1. Copy files maintaining directory structure

2. Add to `commands/default_cmdsets.py`:
```python
from commands.book_commands import BookCmdSet

# In CharacterCmdSet.at_cmdset_creation():
self.add(BookCmdSet)
```

3. Characters need `db.adult_enabled = True` for scenes

4. Spawn Eevee:
```python
from typeclasses.objects.living_eevee import create_living_eevee
eevee = create_living_eevee(location=room, home=room)
```

## Room Objects

| Object | Description |
|--------|-------------|
| LivingEevee | Autonomous creature |
| AuriasJournal | Writable journal |
| AuriaPillowNest | Furniture with chains |
| AuriaBed | Bed with stuffies |
| AuriaCollar | Chain setup |
| AuriaBookcase | Holds WritableBooks |
| AuriaTrunk | Locked container |
| AuriaWardrobe | Container |

## Complete Build

```python
from typeclasses.rooms.aurias_room import create_aurias_room
from typeclasses.objects.aurias_objects import create_aurias_objects
from typeclasses.objects.living_eevee import create_living_eevee

room = create_aurias_room()
objects = create_aurias_objects(room)
eevee = create_living_eevee(location=room, home=room)
```

## Dependencies

- Evennia framework
- Your `world/scenes.py` scene system
- Characters need `db.adult_enabled = True`
