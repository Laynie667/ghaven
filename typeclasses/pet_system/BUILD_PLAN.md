# Comprehensive Pet & Expansion Systems Build Plan

## Overview
Building a massive expansion covering pet systems, breeding mechanics, and numerous additional systems.

**Estimated Total: ~25,000+ lines across 40+ files**

---

## Part 1: Pet Systems Core (~4,500 lines)

### 1.1 Feral Pet Expansion (1,200 lines)
- `feral_training.py` - Advanced trick system, training mechanics
- `feral_stats.py` - Pet stats (loyalty, obedience, mood, energy)
- `feral_offspring.py` - Breeding results, inheritance, litters
- `feral_packs.py` - Pack hierarchy, alpha/beta/omega dynamics

### 1.2 Pet Play System (1,800 lines)
- `pet_play.py` - Headspace, pet types, traits
- `pet_gear.py` - Hoods, mitts, tail plugs, bridles, etc.
- `pet_training.py` - Humanoid pet training, conditioning

### 1.3 Harness & Mounting System (1,500 lines)
- `harnesses.py` - Breeding harnesses, belly slings, mounting gear
- `belly_mount.py` - Tauroid/quadruped belly mounting system
- `riding.py` - Saddles, riding mechanics, gait effects

---

## Part 2: Clothing & Appearance (~2,500 lines)

### 2.1 Clothing System (2,000 lines)
- `clothing.py` - Base clothing, slots, layering
- `clothing_types.py` - All clothing items by category
- `clothing_states.py` - Worn, removed, torn, lifted, shifted
- `clothing_commands.py` - wear, remove, strip, tear, lift

### 2.2 Body Modification (500 lines)
- `modifications.py` - Piercings, tattoos, brands, implants

---

## Part 3: Breeding & Offspring (~3,000 lines)

### 3.1 Pregnancy System (2,000 lines)
- `pregnancy.py` - Conception, stages, birth mechanics
- `pregnancy_effects.py` - Physical changes during pregnancy
- `offspring.py` - NPC offspring generation, trait inheritance

### 3.2 Breeding Records (1,000 lines)
- `breeding_records.py` - Stud records, lineage tracking
- `breeding_quality.py` - Breeding stats, fertility, virility

---

## Part 4: Economy & Ownership (~3,000 lines)

### 4.1 Economy System (1,500 lines)
- `economy.py` - Currency, transactions
- `shops.py` - Vendor NPCs, buying/selling
- `pricing.py` - Price lists, haggling

### 4.2 Ownership & Slavery (1,500 lines)
- `ownership.py` - Owner/property relationships
- `slave_market.py` - Auctions, sales, transfers
- `contracts.py` - Ownership contracts, terms

---

## Part 5: Training & Conditioning (~2,000 lines)

### 5.1 Training System (1,200 lines)
- `training.py` - Breaking, conditioning mechanics
- `obedience.py` - Obedience tracking, resistance
- `rewards_punishments.py` - Reinforcement mechanics

### 5.2 Mind Effects (800 lines)
- `hypnosis.py` - Trance, suggestions, triggers
- `conditioning.py` - Long-term behavioral modification

---

## Part 6: Substances & Effects (~1,500 lines)

### 6.1 Potions & Drugs (1,000 lines)
- `potions.py` - Aphrodisiacs, fertility drugs, etc.
- `potion_effects.py` - Effect application and duration

### 6.2 Transformation (500 lines)
- `transformation.py` - Species/body changes via potions

---

## Part 7: Social & Relationship (~1,500 lines)

### 7.1 Relationships (800 lines)
- `relationships.py` - Relationship types, tracking
- `reputation.py` - Reputation with factions/NPCs

### 7.2 Harem/Group (700 lines)
- `harem.py` - Multi-partner management
- `hierarchy.py` - Pecking order among owned

---

## Part 8: Expanded Mechanics (~2,500 lines)

### 8.1 Scent System Expansion (800 lines)
- `scent_expanded.py` - Territory marking, tracking, detection

### 8.2 Combat/Grappling (1,200 lines)
- `grappling.py` - Non-lethal combat, pins, holds
- `escape.py` - Escape mechanics, struggle

### 8.3 Bondage Complexity (500 lines)
- `rope_bondage.py` - Tie patterns, suspension, escape DC

---

## Part 9: Service & Performance (~1,200 lines)

### 9.1 Service Roles (600 lines)
- `service.py` - Maid, butler, servant roles
- `tasks.py` - Task assignment, completion

### 9.2 Exhibition (600 lines)
- `exhibition.py` - Crowds, watchers, performance
- `glory_holes.py` - Anonymous encounter mechanics

---

## Part 10: Production & Milking (~800 lines)

### 10.1 Milking Stations (500 lines)
- `milking_station.py` - Automated milking, production tracking

### 10.2 Fluid Production (300 lines)
- `production.py` - Milk/cum production rates, storage

---

## Part 11: Commands (~3,000 lines)

### 11.1 Pet Commands (600 lines)
- `pet_commands.py` - All pet play commands

### 11.2 Breeding Commands (400 lines)
- `breeding_commands.py` - Harness, mount, breed commands

### 11.3 Economy Commands (400 lines)
- `economy_commands.py` - Buy, sell, shop commands

### 11.4 Training Commands (400 lines)
- `training_commands.py` - Train, condition, hypnotize

### 11.5 Clothing Commands (300 lines)
- `clothing_commands.py` - Wear, strip, tear

### 11.6 Social Commands (300 lines)
- `social_commands.py` - Relationships, reputation

### 11.7 Combat Commands (300 lines)
- `combat_commands.py` - Grapple, pin, escape

### 11.8 Service Commands (300 lines)
- `service_commands.py` - Tasks, service roles

---

## File Structure

```
expansion/
├── __init__.py
├── BUILD_PLAN.md
│
├── pets/
│   ├── __init__.py
│   ├── feral_training.py
│   ├── feral_stats.py
│   ├── feral_offspring.py
│   ├── feral_packs.py
│   ├── pet_play.py
│   ├── pet_gear.py
│   ├── pet_training.py
│   └── pet_commands.py
│
├── mounting/
│   ├── __init__.py
│   ├── harnesses.py
│   ├── belly_mount.py
│   ├── riding.py
│   └── mounting_commands.py
│
├── clothing/
│   ├── __init__.py
│   ├── clothing.py
│   ├── clothing_types.py
│   ├── clothing_states.py
│   ├── modifications.py
│   └── clothing_commands.py
│
├── breeding/
│   ├── __init__.py
│   ├── pregnancy.py
│   ├── pregnancy_effects.py
│   ├── offspring.py
│   ├── breeding_records.py
│   ├── breeding_quality.py
│   └── breeding_commands.py
│
├── economy/
│   ├── __init__.py
│   ├── economy.py
│   ├── shops.py
│   ├── pricing.py
│   ├── ownership.py
│   ├── slave_market.py
│   ├── contracts.py
│   └── economy_commands.py
│
├── training/
│   ├── __init__.py
│   ├── training.py
│   ├── obedience.py
│   ├── rewards_punishments.py
│   ├── hypnosis.py
│   ├── conditioning.py
│   └── training_commands.py
│
├── substances/
│   ├── __init__.py
│   ├── potions.py
│   ├── potion_effects.py
│   └── transformation.py
│
├── social/
│   ├── __init__.py
│   ├── relationships.py
│   ├── reputation.py
│   ├── harem.py
│   ├── hierarchy.py
│   └── social_commands.py
│
├── mechanics/
│   ├── __init__.py
│   ├── scent_expanded.py
│   ├── grappling.py
│   ├── escape.py
│   ├── rope_bondage.py
│   └── combat_commands.py
│
├── service/
│   ├── __init__.py
│   ├── service.py
│   ├── tasks.py
│   ├── exhibition.py
│   ├── glory_holes.py
│   └── service_commands.py
│
└── production/
    ├── __init__.py
    ├── milking_station.py
    └── production.py
```

---

## Build Order

1. **Pets Core** - Foundation for pet systems
2. **Mounting/Harnesses** - Breeding equipment
3. **Clothing** - Wearables system
4. **Breeding** - Pregnancy and offspring
5. **Training** - Conditioning mechanics
6. **Economy** - Currency and shops
7. **Social** - Relationships
8. **Mechanics** - Scent, combat, bondage
9. **Service** - Roles and exhibition
10. **Production** - Milking stations
11. **Commands** - All command sets
12. **Package Init** - Wire it all together

---

## Integration Points

| New System | Connects To |
|------------|-------------|
| Pet Play | Collars, leashes, cages, kennels |
| Harnesses | Furniture (breeding bench), positions |
| Belly Mount | Structures (tauroid), positions |
| Clothing | Description system, body parts |
| Pregnancy | Breeding, species, anatomy |
| Training | NPCs, obedience, pet play |
| Economy | Items, ownership |
| Scent | Marks system, heat cycles |
| Grappling | Positions, damage, restraints |
| Milking | Lactation system, machines |

---

## Starting Now...
