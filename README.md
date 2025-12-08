# Gilderhaven Systems
## Complete MUD Framework for Evennia

A comprehensive system package for building an adult-themed MUD with Evennia, featuring rich gameplay systems, detailed world content, and sophisticated character mechanics.

**Version:** 2.0  
**Lines of Code:** ~40,000+  
**Framework:** Evennia MUD Framework  
**Python:** 3.10+

---

## Quick Start

```python
# 1. Copy to your Evennia game directory
cp -r gilderhaven_systems/* mygame/

# 2. Add command sets to default_cmdsets.py
from commands import (
    HousingCmdSet, GatheringCmdSet, FurnitureCmdSet,
    PositionCmdSet, NPCCmdSet, ItemCmdSet, ShopCmdSet,
    BodyCmdSet, TimeCmdSet, QuestCmdSet, CraftingCmdSet,
    CombatCmdSet, PartyCmdSet
)

class CharacterCmdSet(default_cmds.CharacterCmdSet):
    def at_cmdset_creation(self):
        super().at_cmdset_creation()
        self.add(HousingCmdSet)
        self.add(GatheringCmdSet)
        self.add(FurnitureCmdSet)
        self.add(PositionCmdSet)
        self.add(NPCCmdSet)
        self.add(ItemCmdSet)
        self.add(ShopCmdSet)
        self.add(BodyCmdSet)
        self.add(TimeCmdSet)
        self.add(QuestCmdSet)
        self.add(CraftingCmdSet)
        self.add(CombatCmdSet)
        self.add(PartyCmdSet)

# 3. Use mixins in your typeclasses (optional but recommended)
from typeclasses.mixins import GilderhaveRoomMixin, GilderhaveCharacterMixin

class Room(GilderhaveRoomMixin, DefaultRoom):
    pass

class Character(GilderhaveCharacterMixin, DefaultCharacter):
    pass

# 4. Build the world
@py from content.the_grove import build_all; build_all()
@py from content.builders import build_all_newbie_areas; build_all_newbie_areas()
```

---

## Systems Overview

### Core Systems (~15,500 lines)

| System | File | Lines | Purpose |
|--------|------|-------|---------|
| Currency | `world/currency.py` | ~200 | Money management |
| Effects | `world/effects.py` | ~400 | Statuses, transformations |
| Triggers | `world/triggers.py` | ~350 | Event handling |
| Resources | `world/resources.py` | ~400 | Gatherable nodes |
| Random Events | `world/random_events.py` | ~350 | Ambient events |
| Traps | `world/traps.py` | ~400 | Hazards and curses |
| Scenes | `world/scenes.py` | ~500 | Branching narratives |
| Scene Examples | `world/scenes_examples.py` | ~400 | 20 pre-built scenes |
| Housing | `world/housing.py` | ~900 | Player homes |
| Furniture | `world/furniture.py` | ~1,000 | Interactive furniture |
| Positions | `world/positions.py` | ~1,000 | Character poses |
| NPCs | `world/npcs.py` | ~1,800 | NPC framework |
| Items | `world/items.py` | ~1,600 | Item system |
| Shops | `world/shops.py` | ~750 | Buy/sell interface |
| Body | `world/body.py` | ~1,450 | Body customization |
| Time/Weather | `world/time_weather.py` | ~800 | Game time system |
| Quests | `world/quests.py` | ~1,200 | Quest system |
| Crafting | `world/crafting.py` | ~2,800 | 102 recipes, skills |

### Combat Systems (~5,600 lines)

| System | File | Lines | Purpose |
|--------|------|-------|---------|
| Combat | `world/combat.py` | ~1,800 | Combat engine |
| Creatures | `world/creatures.py` | ~1,050 | 12 creature templates |
| Parties | `world/parties.py` | ~700 | Party formation |
| Encounters | `world/encounters.py` | ~870 | Random encounters |

### Commands (~6,700 lines)

| Commands | File | Lines |
|----------|------|-------|
| Housing | `commands/housing_commands.py` | ~650 |
| Gathering | `commands/gathering_commands.py` | ~500 |
| Furniture | `commands/furniture_commands.py` | ~450 |
| Positions | `commands/position_commands.py` | ~550 |
| NPCs | `commands/npc_commands.py` | ~400 |
| Items | `commands/item_commands.py` | ~600 |
| Shops | `commands/shop_commands.py` | ~400 |
| Body | `commands/body_commands.py` | ~550 |
| Time | `commands/time_commands.py` | ~450 |
| Quests | `commands/quest_commands.py` | ~500 |
| Crafting | `commands/crafting_commands.py` | ~500 |
| Combat | `commands/combat_commands.py` | ~1,050 |
| Party | `commands/party_commands.py` | ~700 |

### Content (~8,500 lines)

| Area | File | Rooms | Purpose |
|------|------|-------|---------|
| The Grove Hub | `content/the_grove.py` | 28 | Central hub |
| Museum | `content/museum.py` | 8 | Curator's domain |
| Market | `content/market.py` | 5 | Shopping district |
| Whisperwood | `content/whisperwood.py` | 6 | Forest area |
| Moonshallow | `content/moonshallow.py` | 4 | Pond/fishing |
| Sunny Meadow | `content/sunny_meadow.py` | 4 | Flower fields |
| Copper Hill | `content/copper_hill.py` | 6 | Mining area |
| Tidepools | `content/tidepools.py` | 6 | Beach area |

**Total: ~67 rooms across 8 areas**

---

## The Grove Hub

The central safe zone at the roots of Yggdrasil.

### Districts

| District | Rooms | Features |
|----------|-------|----------|
| **Gate Plaza** | 2 | 9 realm gates, Gatekeepers' Office |
| **Town Square** | 2 | Central fountain, Wishing Well |
| **Tavern Row** | 8 | Tipsy Sprite, Wanderer's Rest Inn, Bath House, Lucky Coin |
| **Residential** | 3 | Housing Office, Furniture Emporium |
| **Waterfront** | 3 | Fishing Dock, Boat Rental |
| **Orchards** | 3 | Apple Grove, Berry Bushes |
| **Services Row** | 4 | Smithery, Crafter's Hall, Training Yard |
| **Guild Hall** | 2 | Guild registration, Meeting rooms |
| **Museum** | 8 | All wings, Curator's office |
| **Market** | 5 | 4 shops with NPCs |

### Grove NPCs

| NPC | Location | Role |
|-----|----------|------|
| Big Tom | Tipsy Sprite | Tavern owner, food/drink |
| Martha | Wanderer's Rest | Innkeeper, rooms |
| Attendant Lin | Bath House | Bath services |
| Fingers | Lucky Coin | Gambling, information |
| Clerk Pembrook | Housing Office | Property sales |
| Madame Velvet | Furniture Emporium | Furniture sales |
| Old Barnaby | Boat Rental | Boats, fishing tips |
| Guildmaster Vera | Guild Hall | Guild registration |
| Greta Ironhand | Smithery | Smithing, tools |
| Whisper | Bubbling Flask | Alchemy, potions |
| The Curator | Museum | Collections, secrets |

---

## Combat System

### Resource Pools

| Pool | Color | At Zero | Regen |
|------|-------|---------|-------|
| **HP** | Red | Knocked out | 1/tick |
| **Stamina** | Yellow | Exhausted, can't flee | 2/tick |
| **Composure** | Magenta | Overwhelmed | 3/tick |

### Primary Attributes

| Attribute | Abbrev | Affects |
|-----------|--------|---------|
| Strength | STR | Melee damage, grapple, HP |
| Agility | AGI | Dodge, flee, initiative |
| Endurance | END | HP pool, stamina pool |
| Willpower | WIL | Composure, resistance |
| Charisma | CHA | Intimidate, seduce, befriend |

### Combat Actions

**Offensive:** attack, power, grapple, tease, seduce  
**Defensive:** defend (+30 defense), dodge (+25 evasion)  
**Utility:** flee, struggle, intimidate, befriend, submit

### Creatures (12 types)

| Creature | Level | Behavior | Primary Attack |
|----------|-------|----------|----------------|
| Green Slime | 1 | Lustful | Engulf |
| Pink Slime | 3 | Lustful | Aphrodisiac Embrace |
| Wolf | 3 | Pack | Bite, Pounce |
| Alpha Wolf | 6 | Pack | Savage Bite |
| Grabbing Vine | 2 | Ambusher | Constrict |
| Tentacle Blossom | 5 | Lustful | Probing Tendrils |
| Goblin | 2 | Aggressive | Club Swing |
| Goblin Shaman | 4 | Defensive | Hex, Lust Curse |
| Lustful Wisp | 4 | Lustful | Euphoric Touch |
| Harpy | 5 | Predatory | Talon Strike |
| Mimic | 4 | Ambusher | Adhesive Tongue |
| Lamia | 7 | Predatory | Constrict, Mesmerize |

### Encounter Types

| Type | Waves | Special |
|------|-------|---------|
| Single creature | 1 | Basic encounter |
| Pack encounters | 1 | Multiple enemies |
| Multi-wave | 2-3 | Reinforcements arrive |
| Boss encounters | 1 | Can't flee, special rewards |
| Ambush | 2 | Can't flee wave 1 |

### Danger Levels

| Level | Encounter Rate | Areas |
|-------|----------------|-------|
| Safe | 0% | Grove, Museum, Market |
| Peaceful | ~5% | Newbie areas |
| Normal | ~15% | Copper Hill |
| Dangerous | ~23% | Deep areas |
| Deadly | ~30% | End-game |

---

## Party System

- **Max Size:** 6 members
- **Movement:** Leader controls, members auto-follow
- **Combat:** Whole party enters together
- **Loot Modes:** FFA, Round Robin, Leader distributes

### Formations

| Formation | Front Row | Bonus |
|-----------|-----------|-------|
| Standard | 60% | Balanced |
| Aggressive | 100% | +10% damage |
| Defensive | 40% | +15% defense |
| Scattered | 50% | -50% AoE damage |

---

## Crafting System

### Categories & Recipes

| Category | Recipes | NPC Teacher |
|----------|---------|-------------|
| Alchemy | 18 | Whisper, Curator |
| Smithing | 16 | Greta, Curator |
| Cooking | 14 | Big Tom, Curator |
| Tailoring | 14 | Skill-based, Curator |
| Woodworking | 14 | Default, Curator |
| Jewelcrafting | 12 | Skill-based, Curator |
| Leatherworking | 14 | Default, Curator |

**Total: 102 recipes**

### Discovery Sources

- **Default:** Everyone knows
- **Skill-based:** Auto-learn at skill level
- **NPC-taught:** Learn from specific NPCs
- **Scene-unlock:** Complete specific scenes

---

## Body System

### Species (25+ templates)

Human, Elf, Orc, Demon, Angel, Neko, Kitsune, Wolf, Dragon, Lamia, Slime, Fairy, Centaur, Minotaur, Goblin, Imp, Succubus, Incubus, Vampire, Werewolf, Harpy, Mermaid, Dryad, Satyr, Custom

### Gender Configs (12)

male, female, futa, herm, dickgirl, cuntboy, trap, femboy, nulled, doll, hucow, breeder

### Shortcodes

```
<time>, <weather>, <season>
<body.cock>, <body.pussy>, <body.breasts>
<pronoun.subject>, <pronoun.object>, <pronoun.possessive>
<n> (character name)
```

---

## Time & Weather

- **Scale:** 1 real hour ≈ 1 game day
- **Periods:** Dawn, Morning, Noon, Afternoon, Dusk, Evening, Night
- **Seasons:** Spring, Summer, Autumn, Winter
- **Weather:** Clear, Cloudy, Rain, Storm, Fog, Snow, Blizzard, Hot, Windy, Magical

---

## Command Reference

### Movement & Exploration
```
look, go <direction>, enter, leave
danger - Check area danger level
```

### Combat
```
attack <target>, power <target>, grapple <target>
tease <target>, seduce <target>, intimidate <target>
defend, dodge, flee, struggle, submit, befriend <target>
combat - View combat status
rest - Recover resources
attributes, cskills - View stats
defeatprefs - Set defeat preferences
pvp on/off, challenge <player>
```

### Party
```
party - View party
invite <player>, party accept/decline
party leave, party kick <player>
party disband, party promote <player>
party formation <type>, party loot <mode>
p <message> - Party chat
party recall, follow
```

### Gathering
```
forage, fish, mine, catch, search, gather
resources - View nearby resources
```

### Crafting
```
craft <recipe>, recipes, recipe <n>
skills - View crafting skills
```

### Items & Economy
```
inventory, get <item>, drop <item>
use <item>, equip <item>, examine <item>
shop, buy <item>, sell <item>, value <item>
balance
```

### Housing
```
home, home info, home name <n>
home upgrade <type>, home room add <type>
invite <player>, kick <player>
visit <player>, knock
```

### Social
```
talk <npc>, greet <npc>, bow <npc>
sit <furniture>, stand, kneel, lie
position <pose>, cuddle <player>
```

### Body & Character
```
species <type>, gender <config>
body, body <part>, body set <part> <desc>
pronouns, pronouns set <type> <value>
```

### Time & Environment
```
time, weather, calendar
```

### Quests
```
quests, quest <n>, tasks
abandon <quest>, turnin
```

---

## File Structure

```
gilderhaven_systems/
├── world/                    # Core systems
│   ├── __init__.py          # System imports
│   ├── currency.py          # Money
│   ├── effects.py           # Statuses
│   ├── triggers.py          # Events
│   ├── resources.py         # Gathering
│   ├── random_events.py     # Ambient events
│   ├── traps.py             # Hazards
│   ├── scenes.py            # Branching stories
│   ├── scenes_examples.py   # Pre-built scenes
│   ├── housing.py           # Player homes
│   ├── furniture.py         # Furniture
│   ├── positions.py         # Poses
│   ├── npcs.py              # NPC framework
│   ├── items.py             # Items
│   ├── shops.py             # Shops
│   ├── body.py              # Body system
│   ├── time_weather.py      # Time/weather
│   ├── quests.py            # Quests
│   ├── crafting.py          # Crafting
│   ├── combat.py            # Combat engine
│   ├── creatures.py         # Creature templates
│   ├── parties.py           # Party system
│   └── encounters.py        # Encounter system
├── commands/                 # Player commands
│   ├── __init__.py
│   ├── housing_commands.py
│   ├── gathering_commands.py
│   ├── furniture_commands.py
│   ├── position_commands.py
│   ├── npc_commands.py
│   ├── item_commands.py
│   ├── shop_commands.py
│   ├── body_commands.py
│   ├── time_commands.py
│   ├── quest_commands.py
│   ├── crafting_commands.py
│   ├── combat_commands.py
│   └── party_commands.py
├── content/                  # World content
│   ├── __init__.py
│   ├── the_grove.py         # Central hub (28 rooms)
│   ├── museum.py            # Museum area (8 rooms)
│   ├── market.py            # Market area (5 rooms)
│   ├── whisperwood.py       # Forest area (6 rooms)
│   ├── moonshallow.py       # Pond area (4 rooms)
│   ├── sunny_meadow.py      # Meadow area (4 rooms)
│   ├── copper_hill.py       # Mining area (6 rooms)
│   ├── tidepools.py         # Beach area (6 rooms)
│   └── builders.py          # Build utilities
├── typeclasses/              # Evennia extensions
│   ├── __init__.py
│   └── mixins.py            # Room/Character mixins
├── README.md                 # This file
├── WORLDMAP.md              # Complete world map
├── HOUSING.md               # Housing documentation
└── SCENES.md                # Scene system docs
```

---

## Building the World

```python
# Build everything
@py from content.the_grove import build_all; build_all()
@py from content.builders import build_all_newbie_areas; build_all_newbie_areas()

# Or build individually
@py from content.the_grove import build_grove; build_grove()
@py from content.the_grove import spawn_grove_npcs; spawn_grove_npcs()
@py from content.builders import build_museum; build_museum()
@py from content.builders import build_market; build_market()
@py from content.builders import build_whisperwood; build_whisperwood()
@py from content.builders import build_moonshallow; build_moonshallow()
@py from content.builders import build_sunny_meadow; build_sunny_meadow()
@py from content.builders import build_copper_hill; build_copper_hill()
@py from content.builders import build_tidepools; build_tidepools()
```

---

## Design Principles

1. **No Death** - Combat results in capture/defeat, not killing
2. **Consent Layers** - Players control what content they experience
3. **Safe Zones** - The Grove is protected from violence
4. **Consequences** - Actions have results, but everything is reversible
5. **Player Agency** - Even in defeat, players have choices
6. **Modular Systems** - Each system works independently
7. **Extensible** - Easy to add new content

---

## License

Created for private use. Evennia framework is BSD licensed.
