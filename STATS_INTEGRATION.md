# STATS SYSTEM INTEGRATION GUIDE

## Overview

This document explains how to integrate the hard mode stats system into your Evennia game.

---

## FILES INCLUDED

```
world/stats.py          - Core stat system
commands/stat_commands.py - Player and admin commands
```

---

## INSTALLATION

### Step 1: Copy Files

```bash
cp world/stats.py ~/Gilderhaven/gilderhaven/world/
cp commands/stat_commands.py ~/Gilderhaven/gilderhaven/commands/
```

### Step 2: Add Commands to Default CmdSet

Edit `commands/default_cmdsets.py`:

```python
from commands.stat_commands import StatsCmdSet

class CharacterCmdSet(default_cmds.CharacterCmdSet):
    def at_cmdset_creation(self):
        super().at_cmdset_creation()
        self.add(StatsCmdSet)  # Add this line
```

### Step 3: Initialize Stats on Character Creation

Edit `typeclasses/characters.py`, add to `at_object_creation`:

```python
def at_object_creation(self):
    super().at_object_creation()
    
    # Initialize stats
    from world.stats import initialize_stats
    initialize_stats(self, "default")
```

### Step 4: Block Movement When Collapsed

Edit `typeclasses/characters.py`, add hook:

```python
def at_pre_move(self, destination, **kwargs):
    """Check if movement is allowed."""
    from world.stats import can_move, is_collapsed
    
    if not can_move(self):
        if is_collapsed(self):
            self.msg("You're too exhausted to move.")
        else:
            self.msg("You can't move right now.")
        return False
    
    return super().at_pre_move(destination, **kwargs)
```

### Step 5: Reload

```bash
evennia reload
```

---

## SHORTCODE INTEGRATION

To use stats in room/object descriptions, update your shortcode processor.

In `world/shortcodes.py` or wherever you process `<char.X>` tags:

```python
from world.stats import get_stat_shortcodes

def process_shortcodes(character, text, location=None):
    """Process all shortcodes in text."""
    
    # Get stat shortcodes
    stat_codes = get_stat_shortcodes(character)
    
    # Replace stat shortcodes
    for code, value in stat_codes.items():
        text = text.replace(f"<{code}>", value)
    
    # ... other shortcode processing ...
    
    return text
```

### Available Shortcodes

**Raw Values:**
- `<char.stamina>` → "75"
- `<char.composure>` → "45"
- `<char.arousal>` → "82"
- `<char.corruption>` → "30"
- `<char.willpower>` → "12"

**State Names:**
- `<char.stamina_state>` → "tired"
- `<char.composure_state>` → "shaken"
- `<char.arousal_state>` → "desperate"
- `<char.corruption_state>` → "tainted"

**Boolean Checks:**
- `<char.is_collapsed>` → "true" or "false"
- `<char.is_broken>` → "true" or "false"
- `<char.is_helpless>` → "true" or "false"
- `<char.is_in_heat>` → "true" or "false"
- `<char.can_resist>` → "true" or "false"

**Combined States:**
- `<char.states>` → "desperate, pliable" or "none"

---

## USAGE EXAMPLES

### In Room Descriptions

```
The creature eyes you, sensing your <char.arousal_state> state.
```
→ "The creature eyes you, sensing your desperate state."

### In NPC Dialogue

```python
if character.db.stats.get("composure", 100) < 20:
    npc.msg_contents(f'The Curator smiles. "So close to breaking, aren\'t you?"')
```

### In Scene/Encounter Code

```python
from world.stats import (
    is_helpless, can_resist, drain_composure, 
    build_arousal, check_willpower
)

# Check if player can resist
if not can_resist(player):
    # Auto-success for captor
    capture_player(player)
else:
    # Willpower check
    success, margin = check_willpower(player, difficulty=15)
    if success:
        player.msg("You steel yourself and resist.")
    else:
        drain_composure(player, 10, "failed resistance")
        player.msg("Your resistance crumbles.")
```

### Arousal Building with Sensitivity

```python
from world.stats import build_arousal

# This respects the character's sensitivity stat
# High sensitivity = more arousal gained
build_arousal(player, 15, "teasing")
```

### Checking Combined States

```python
from world.stats import get_combined_states, is_desperate

# Check for specific compound vulnerability
if is_desperate(player):
    # They're low composure + high arousal
    # Will do anything for release
    pass

# Get all active states
states = get_combined_states(player)
if "helpless" in states:
    # They're collapsed or broken or both critical
    pass
```

---

## HARD MODE CONSEQUENCES

### Stamina = 0 (Collapsed)
- `can_move()` returns False
- Movement blocked
- Cannot flee
- Cannot struggle
- Easy to capture/use

### Composure = 0 (Broken)
- `can_resist()` returns False
- Cannot refuse commands
- Vulnerable to conditioning
- NPCs can command freely

### Arousal = 100 (Overwhelmed)
- **If denied:** Stuck at edge, loses 15 composure, arousal drops to 95
- **If not denied:** Forced orgasm, arousal drops to 10, loses 20 stamina

### Combined States

| State | Trigger | Effect |
|-------|---------|--------|
| helpless | stamina ≤20 AND composure ≤20 | Cannot resist anything |
| desperate | composure ≤30 AND arousal ≥70 | Will do anything for release |
| broken_in | composure ≤10 AND corruption ≥50 | Conditioning taking hold |
| feral | stamina ≤10 AND arousal ≥80 | Body acts on instinct |
| pliable | stamina ≤40 AND composure ≤40 | Easy to manipulate |
| in_heat | arousal ≥85 | Arousal dominant, reduced thinking |
| marked | corruption ≥70 | Corruption visibly showing |

---

## COMMANDS REFERENCE

### Player Commands

| Command | Usage | Effect |
|---------|-------|--------|
| `stats` | `stats` | View all your stats |
| `condition` | `cond` | Quick status check |
| `rest` | `rest` | Recover stamina (if safe) |
| `compose` | `compose` | Recover composure |

### Admin Commands

| Command | Usage | Effect |
|---------|-------|--------|
| `deny` | `deny <target>` | Toggle orgasm denial |
| `edge` | `edge <target> = 20` | Build arousal |
| `drain` | `drain <target> stamina 30` | Drain a resource stat |
| `setstat` | `setstat <target> arousal = 50` | Set stat directly |
| `initstats` | `initstats <target> = sensitive` | Initialize with template |

---

## TEMPLATES

When initializing stats, you can use these templates:

### default
Balanced starting stats. Standard new character.

### resilient
- Willpower: 14 (higher)
- Sensitivity: 8 (lower)
- Resilience: 14 (higher)

Good for characters who resist manipulation.

### sensitive
- Willpower: 6 (lower)
- Sensitivity: 16 (higher)
- Resilience: 8 (lower)
- Starting Arousal: 10

Easily aroused, harder to resist.

### corrupted
- Composure: 80 (lower starting)
- Arousal: 20 (higher starting)
- Willpower: 8 (lower)
- Sensitivity: 14 (higher)
- Corruption: 30 (starting corrupted)
- Notoriety: 10 (already known)

For characters with history.

---

## HOOKING INTO OTHER SYSTEMS

### Furniture System

When a character sits on furniture:
```python
def on_sit(character, furniture):
    # Comfortable furniture restores composure
    if furniture.db.is_comfortable:
        from world.stats import restore_composure
        restore_composure(character, 5, "comfortable seat")
```

### NPC Reactions

NPCs can check player state:
```python
def on_player_arrives(self, player):
    from world.stats import is_desperate, get_arousal_state
    
    if is_desperate(player):
        self.msg_contents(
            f'{self.key} notices {player.key}\'s desperate state and smiles.'
        )
```

### Combat/Capture

```python
from world.stats import is_helpless, drain_stamina

def attempt_capture(captor, target):
    # Helpless targets auto-captured
    if is_helpless(target):
        return True, "too weak to resist"
    
    # Otherwise requires catching them
    # Drain their stamina from the chase
    drain_stamina(target, 20, "fleeing")
    # ... capture logic ...
```

### Heat/Breeding

```python
from world.stats import is_in_heat, build_arousal, get_stat

def check_heat_effects(character):
    if is_in_heat(character):
        # Slow passive arousal build
        build_arousal(character, 2, "heat")
        
        # Reduced willpower while in heat
        # (This is already factored into checks)
```

---

## RECOVERY RATES

### Stamina Recovery

| Location | Amount | Notes |
|----------|--------|-------|
| Home | +25 | Your own home |
| Safe room | +20 | Inns, safe zones |
| Grove | +15 | Grove areas |
| Normal | +5 | Anywhere else |
| Dangerous | 0 | Cannot rest |
| Collapsed | Half | Recovery slowed |

### Composure Recovery

| Condition | Amount | Notes |
|-----------|--------|-------|
| Safe + calm | +15 | Arousal under 50 |
| Safe + aroused | +10 | Arousal 50+ |
| Unsafe | +5 | Any non-safe area |
| Broken | +5 | Slow recovery |
| High arousal | -5 penalty | Arousal 70+ reduces gain |

### Arousal Decay

Arousal decays slowly over time if not stimulated:
- Natural decay: -1 per game hour
- Cold water/shock: -20 immediate
- Orgasm (if permitted): -90 (drops to 10)

---

## NOTES

- All stats persist across sessions (stored in `character.db.stats`)
- Orgasm denial is stored in `character.db.orgasm_denied`
- Orgasm count tracked in `character.db.orgasm_count`
- Denied orgasm count in `character.db.denied_orgasms`
- Active states in `character.db.active_states`

This is HARD MODE. Manage your resources or face the consequences.
