# Gilderhaven World Map
## Complete Location Reference

---

## Overview

```
                              ┌─────────────┐
                              │  GATE PLAZA │
                              │  (9 gates)  │
                              └──────┬──────┘
                                     │
         ┌───────────────────────────┼───────────────────────────┐
         │                           │                           │
    ┌────┴────┐               ┌──────┴──────┐               ┌────┴────┐
    │ TAVERN  │               │    TOWN     │               │SERVICES │
    │   ROW   │───────────────│   SQUARE    │───────────────│   ROW   │
    └────┬────┘               └──────┬──────┘               └────┬────┘
         │                    │      │      │                    │
    ┌────┴────┐          ┌────┴─┐  ┌─┴───┐ ┌┴────┐          ┌────┴────┐
    │ BATH    │          │MARKET│  │WELL │ │RESID│          │ GUILD   │
    │ HOUSE   │          └──────┘  └─────┘ └─────┘          │  HALL   │
    └─────────┘               │                              └─────────┘
                         ┌────┴────┐
                         │ MUSEUM  │
                         └────┬────┘
                              │
                    ┌─────────┴─────────┐
                    │                   │
              ┌─────┴─────┐       ┌─────┴─────┐
              │WATERFRONT │       │  ORCHARDS │
              └─────┬─────┘       └───────────┘
                    │
         ┌──────────┼──────────┐
         │          │          │
    ┌────┴────┐ ┌───┴───┐ ┌────┴────┐
    │MOONSHA- │ │WHISPER│ │  SUNNY  │
    │  LLOW   │ │ WOOD  │ │ MEADOW  │
    └─────────┘ └───────┘ └─────────┘
         │          │          │
    ┌────┴────┐     │     ┌────┴────┐
    │TIDEPOOLS│     │     │ COPPER  │
    └─────────┘     │     │  HILL   │
                    │     └─────────┘
              (deeper areas)
```

---

## The Grove (Central Hub)

**Danger Level:** SAFE (no random encounters)

### Gate Plaza District

| Room | Key | Exits | Features |
|------|-----|-------|----------|
| Gate Plaza | `gate_plaza` | S→Town Square, E→Gatekeepers Office | 9 realm gates, notice board |
| Gatekeepers' Office | `gatekeepers_office` | W→Gate Plaza | Travel permits, bounty verification |

### Town Square District

| Room | Key | Exits | Features |
|------|-----|-------|----------|
| Town Square | `town_square` | N→Gate Plaza, E→Market, S→Museum, W→Tavern Row, NW→Residential, SE→Waterfront, NE→Services, SW→Well | Central fountain, notice board, hub |
| The Wishing Well | `wishing_well` | NE→Town Square | Daily wishes |

### Tavern Row District

| Room | Key | Exits | Features |
|------|-----|-------|----------|
| Tavern Row | `tavern_row` | E→Town Square, N→Tipsy Sprite, S→Inn, W→Bath House, NW→Lucky Coin | Street with establishments |
| The Tipsy Sprite | `tipsy_sprite_tavern` | S→Tavern Row, W→Kitchen | Big Tom's tavern, food/drink shop |
| Tipsy Sprite Kitchen | `tipsy_sprite_kitchen` | E→Tavern | Cooking workstation |
| The Wanderer's Rest | `wanderers_rest` | N→Tavern Row, Up→Hallway | Martha's inn, rooms for rent |
| Inn Hallway | `inn_hallway` | Down→Lobby, E→Guest Room | Upper floor |
| Guest Room | `inn_guest_room` | W→Hallway | Rentable room |
| Grove Bath House | `bath_house_entrance` | E→Tavern Row, W→Main Baths, S→Private | Lin's domain |
| Main Baths | `bath_house_main` | E→Entrance | Hot/cold pools, social bathing |
| Private Bath Room | `bath_house_private` | N→Entrance | Private room, adult content |
| The Lucky Coin | `lucky_coin` | SE→Tavern Row | Fingers' gambling den |

### Residential District

| Room | Key | Exits | Features |
|------|-----|-------|----------|
| Residential Quarter | `residential_entrance` | SE→Town Square, N→Housing Office, E→Furniture | Access to player homes |
| Housing Office | `housing_office` | S→Residential | Pembrook, property sales |
| Furniture Emporium | `furniture_emporium` | W→Residential | Madame Velvet, furniture shop |

### Waterfront District

| Room | Key | Exits | Features |
|------|-----|-------|----------|
| The Waterfront | `waterfront` | NW→Town Square, E→Fishing Dock, W→Boat Rental, S→Orchards, SE→Moonshallow | Lake shore |
| Fishing Dock | `fishing_dock` | W→Waterfront | Fishing resource node |
| Boat Rental | `boat_rental` | E→Waterfront | Old Barnaby, boat rentals |

### Orchards District

| Room | Key | Exits | Features |
|------|-----|-------|----------|
| The Orchards | `orchards_entrance` | N→Waterfront, E→Apple Grove, W→Berry Bushes | Grove foraging |
| Apple Grove | `apple_grove` | W→Orchards | Apples, honey, bees |
| Berry Bushes | `berry_bushes` | E→Orchards | Berries, thorns |

### Services Row District

| Room | Key | Exits | Features |
|------|-----|-------|----------|
| Services Row | `services_row` | SW→Town Square, N→Smithery, E→Crafters Hall, S→Training, W→Guild | Crafting street |
| The Smithery | `smithery` | S→Services | Greta, forge workstation |
| Crafter's Hall | `crafters_hall` | W→Services | Multi-craft workstations |
| Training Yard | `training_yard` | N→Services | Practice combat |
| Guild Hall | `guild_hall` | E→Services, Up→Meeting Room | Vera, guild registration |
| Guild Meeting Room | `guild_meeting_room` | Down→Guild Hall | Private meetings |

### Museum District (8 rooms)

| Room | Key | Exits | Features |
|------|-----|-------|----------|
| Museum Entrance | `museum_entrance` | N→Town Square, various wings | Grand foyer |
| Natural History Wing | - | Entrance | Creature exhibits |
| Artifact Gallery | - | Entrance | Magical items |
| Art Wing | - | Entrance | Player submissions |
| Library | - | Entrance | Books, research |
| Curator's Office | - | Entrance | The Curator |
| Storage | - | Office | Museum storage |
| The Basement | - | Office | Private, adult content |

### Market District (5 rooms)

| Room | Key | Exits | Features |
|------|-----|-------|----------|
| Market Entrance | `market_entrance` | W→Town Square | Market square |
| Honest Work Tools | - | Market | Greta's shop |
| The Bubbling Flask | - | Market | Whisper's alchemy |
| General Goods | - | Market | Basic supplies |
| Exotic Imports | - | Market | Rare items |

---

## Newbie Areas

### Whisperwood (Forest)
**Danger Level:** PEACEFUL (~5% encounter rate)

| Room | Key | Exits | Resources |
|------|-----|-------|-----------|
| Forest Edge | `whisperwood_edge` | Grove, deeper | Tutorial, common bugs |
| Shady Paths | `whisperwood_paths` | Edge, clearing | Mushrooms, bugs |
| Mossy Clearing | `whisperwood_clearing` | Paths, stump | Herbs, flowers |
| Ancient Stump | `whisperwood_stump` | Clearing | Rare bugs, scene trigger |
| Mushroom Grove | `whisperwood_mushrooms` | Paths | Mushrooms, slimes |
| Deep Woods | `whisperwood_deep` | Stump | Higher danger |

**Encounters:** Green Slime, Lone Wolf, Wolf Pack, Grabbing Vine, Wisp Dance

### Moonshallow Pond
**Danger Level:** PEACEFUL

| Room | Key | Exits | Resources |
|------|-----|-------|-----------|
| Moonshallow Pond | `moonshallow_pond` | Waterfront, shore | View point |
| Pond Shore | `moonshallow_shore` | Pond, shallows | Basic fishing |
| Shallow Waters | `moonshallow_shallows` | Shore, deep | Frogs, lily pads |
| Deep Water | `moonshallow_deep` | Shallows, cove | Better fishing |
| Hidden Cove | `moonshallow_cove` | Deep | Rare fish, scene |

**Encounters:** Green Slime, Wisp Dance, Slime Swarm (rare)

### Sunny Meadow
**Danger Level:** PEACEFUL

| Room | Key | Exits | Resources |
|------|-----|-------|-----------|
| Meadow Gate | `sunny_meadow_gate` | Grove, fields | Entry point |
| Flower Fields | `sunny_meadow_fields` | Gate, garden | Flowers, butterflies |
| Bee Garden | `sunny_meadow_garden` | Fields, hilltop | Honey, bees |
| Hilltop View | `sunny_meadow_hilltop` | Garden | Rare flowers, scene |

**Encounters:** Pink Slime, Wisp Dance, Vine Tangle (rare)

### Copper Hill (Mining)
**Danger Level:** NORMAL (~15% encounter rate)

| Room | Key | Exits | Resources |
|------|-----|-------|-----------|
| Hill Base | `copper_hill_base` | Grove, entrance | View point |
| Mine Entrance | `copper_hill_entrance` | Base, tunnels | Basic ore |
| Winding Tunnels | `copper_hill_tunnels` | Entrance, cavern | Copper, iron |
| Crystal Cavern | `copper_hill_cavern` | Tunnels, deep | Gems, crystals |
| Deep Shafts | `copper_hill_deep` | Cavern | Rare ore, danger |
| Abandoned Camp | `copper_hill_camp` | Tunnels | Goblin territory |

**Encounters:** Goblin Patrol, Goblin Ambush, Mimic, Goblin Raiding Party

### Tidepools (Beach)
**Danger Level:** SAFE

| Room | Key | Exits | Resources |
|------|-----|-------|-----------|
| Sandy Beach | `tidepools_beach` | Moonshallow, shore | Shells, sand |
| Rocky Shore | `tidepools_shore` | Beach, pools | Crabs, seaweed |
| Tidal Pools | `tidepools_pools` | Shore, cove | Sea creatures |
| Sea Cove | `tidepools_cove` | Pools | Hidden treasures |
| Driftwood Point | `tidepools_driftwood` | Beach | Wood, flotsam |
| Coral Shallows | `tidepools_coral` | Pools | Rare shells |

**Encounters:** None (safe area)

---

## Connection Graph

```
LIMBO
  └── Grove (Gate Plaza)
        │
        ├── Town Square (CENTRAL HUB)
        │     ├── Wishing Well
        │     ├── Market District (5 rooms)
        │     │     └── 4 Shops
        │     ├── Museum District (8 rooms)
        │     │     └── Curator's domain
        │     ├── Tavern Row (10 rooms)
        │     │     ├── Tipsy Sprite + Kitchen
        │     │     ├── Wanderer's Rest + Rooms
        │     │     ├── Bath House (3 rooms)
        │     │     └── Lucky Coin
        │     ├── Residential (3 rooms)
        │     │     ├── Housing Office
        │     │     └── Furniture Shop
        │     ├── Services Row (5 rooms)
        │     │     ├── Smithery
        │     │     ├── Crafter's Hall
        │     │     ├── Training Yard
        │     │     └── Guild Hall + Meeting
        │     └── Waterfront (3 rooms)
        │           ├── Fishing Dock
        │           └── Boat Rental
        │
        ├── Orchards (3 rooms)
        │     ├── Apple Grove
        │     └── Berry Bushes
        │
        └── Gate Plaza
              ├── Gatekeepers Office
              └── [Future: 9 Realm Gates]

WATERFRONT
  └── Moonshallow Pond (5 rooms)
        └── Tidepools (6 rooms)

GROVE PATHS
  ├── Whisperwood (6 rooms)
  │     └── [Future: Deep Forest]
  ├── Sunny Meadow (4 rooms)
  │     └── Copper Hill (6 rooms)
  │           └── [Future: Deep Mines]
  └── [Future: More areas]
```

---

## Room Counts by Area

| Area | Rooms | NPCs | Danger |
|------|-------|------|--------|
| Gate Plaza | 2 | Gatekeepers | Safe |
| Town Square | 2 | — | Safe |
| Tavern Row | 10 | 4 | Safe |
| Residential | 3 | 2 | Safe |
| Waterfront | 3 | 1 | Safe |
| Orchards | 3 | — | Safe |
| Services Row | 5 | 2 | Safe |
| Museum | 8 | 1 | Safe |
| Market | 5 | 4 | Safe |
| **Grove Total** | **41** | **14** | **Safe** |
| Whisperwood | 6 | — | Peaceful |
| Moonshallow | 5 | — | Peaceful |
| Sunny Meadow | 4 | — | Peaceful |
| Copper Hill | 6 | — | Normal |
| Tidepools | 6 | — | Safe |
| **Newbie Total** | **27** | **0** | **Mixed** |
| **GRAND TOTAL** | **68** | **14** | — |

---

## NPC Locations

| NPC | Location | Services |
|-----|----------|----------|
| Big Tom | Tipsy Sprite Tavern | Food, drink, cooking recipes |
| Martha | Wanderer's Rest | Inn rooms |
| Attendant Lin | Bath House | Bath services |
| Fingers | Lucky Coin | Gambling, information |
| Clerk Pembrook | Housing Office | Property sales |
| Madame Velvet | Furniture Emporium | Furniture |
| Old Barnaby | Boat Rental | Boats, fishing tips |
| Guildmaster Vera | Guild Hall | Guild registration |
| Greta Ironhand | Smithery / Market | Tools, smithing |
| Whisper | Bubbling Flask | Alchemy, potions |
| The Curator | Museum Office | Collections, secrets |
| Market NPCs (2) | Market stalls | General goods |

---

## Resource Locations

| Resource Type | Locations |
|--------------|-----------|
| **Fishing** | Fishing Dock, Moonshallow (all), Tidepools |
| **Foraging** | Apple Grove, Berry Bushes, Whisperwood, Sunny Meadow |
| **Mining** | Copper Hill (all rooms) |
| **Bug Catching** | Whisperwood, Sunny Meadow |
| **Shell Gathering** | Tidepools |

---

## Workstation Locations

| Workstation | Location |
|-------------|----------|
| Cooking | Tipsy Sprite Kitchen |
| Smithing | The Smithery |
| Woodworking | Crafter's Hall |
| Tailoring | Crafter's Hall |
| Jewelcrafting | Crafter's Hall |
| Leatherworking | Crafter's Hall |
| Alchemy | Bubbling Flask |

---

## Build Commands

```python
# Build the Grove hub
@py from content.the_grove import build_all; build_all()

# Build newbie areas
@py from content.builders import build_all_newbie_areas; build_all_newbie_areas()

# Build individual areas
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

## Future Areas (Planned)

| Area | Access | Theme |
|------|--------|-------|
| Realm Gates (9) | Gate Plaza | IC dangerous areas |
| Deep Forest | Whisperwood | Higher danger forest |
| Deep Mines | Copper Hill | Rare ores, bosses |
| The Docks | Tidepools | Sea travel, trade |
| Underwater | Docks | Merfolk, treasure |
