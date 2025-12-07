# Scene Writing Guide

Scenes are self-contained branching narratives. The "NPCs" in scenes don't exist as game objects—they exist only as text. Effects they apply persist, but the characters themselves don't.

## When to Use Scenes vs Full NPCs

**Use Scenes for:**
- Random encounters (goblin ambush, creature attack)
- Trap consequences (cursed item effects)
- Resource hazards (fishing mishaps)
- One-time events (gate malfunction)
- Loss/victory sequences
- Environmental storytelling
- Any encounter where the NPC doesn't need to persist

**Use Full NPCs for:**
- Named characters with ongoing relationships
- Shopkeepers, quest givers
- Characters who remember you
- AI-integrated entities (the Curator)
- Anyone who exists before AND after the encounter

---

## Scene Structure

```python
SCENE_NAME = {
    "id": "unique_scene_id",           # For registry lookup
    "title": "Display Title",          # Optional
    "tags": ["tag1", "tag2"],          # For filtering/searching
    
    "start": {                         # Entry node (required, must be named "start")
        "text": "What the player sees...",
        "choices": [...],              # Player options
        "effects": [...],              # Fire on entering this node
    },
    
    "other_node": {...},               # Additional nodes
    "another_node": {...},
    
    "end_good": {
        "text": "Good ending text.",
        "effects": [...],
        "end": True                    # Marks this as an ending
    },
}
```

---

## Node Properties

| Property | Type | Description |
|----------|------|-------------|
| `text` | str or list | What player sees. If list, picks randomly. |
| `choices` | list | Player options (see below) |
| `effects` | list | Effects that fire when entering this node |
| `goto` | str or list | Auto-advance to this node (no choices). If list, picks randomly. |
| `delay` | float | Seconds to wait before auto-advance |
| `end` | bool | If True, this node ends the scene |

**Note:** `choices` and `goto` are mutually exclusive. Use one or the other.

---

## Choice Properties

```python
{
    "text": "What the player sees",
    "goto": "node_to_go_to",
    "condition": {...},              # Optional: when to show this choice
    "effects": [...],                # Optional: fire when this choice selected
    "hidden": True,                  # If True + condition fails, hide choice
    "disabled_text": "Grayed out"    # Shown if hidden=False and condition fails
}
```

### Conditional Choices

```python
# Only show if player has an item
{"text": "Use the key", "goto": "unlock", 
 "condition": {"type": "has_item", "item": "rusty key"}}

# Only show if player has enough gold
{"text": "Pay the toll (50g)", "goto": "paid",
 "condition": {"type": "currency_gte", "amount": 50}}

# Only show if player has an effect
{"text": "Give in to the heat...", "goto": "submit",
 "condition": {"type": "has_effect", "effect": "pollen_heat"}}

# Only show if player visited a previous node
{"text": "Mention what you saw earlier", "goto": "reference",
 "condition": {"type": "visited_node", "node": "saw_the_thing"}}

# Random availability
{"text": "Lucky option", "goto": "lucky",
 "condition": {"type": "random", "chance": 0.1}}

# Scene-local flag
{"text": "Use the rope", "goto": "rope",
 "condition": {"type": "scene_flag", "flag": "found_rope"}}
```

---

## Text Formatting

### Substitutions

```python
"text": "Hello {name}, you have {currency} gold."
```

| Placeholder | Value |
|-------------|-------|
| `{name}` | Character's name |
| `{pronoun}` | he/she/they |
| `{possessive}` | his/her/their |
| `{object}` | him/her/them |
| `{currency}` | Current gold amount |
| `{flag_name}` | Any scene flag value |

### Colors (Evennia codes)

```python
"|rRed text|n"
"|gGreen text|n"
"|yYellow text|n"
"|bBlue text|n"
"|mMagenta text|n"
"|cCyan text|n"
"|wWhite/bold text|n"
"|xGray/dark text|n"
```

### Random Text

```python
"text": [
    "The goblin grins wickedly.",
    "The goblin licks her lips.",
    "The goblin's tail swishes excitedly.",
]
```

---

## Effects

Effects use the same format as the trigger system.

### Messages
```python
{"type": "message", "text": "You feel strange..."}
{"type": "message_room", "text": "A scream echoes.", "exclude_actor": True}
```

### Status Effects
```python
{"type": "apply_effect", "effect_key": "poisoned", "category": "debuff", "duration": 300}
{"type": "apply_effect", "effect_key": "cursed", "category": "curse"}  # Permanent
{"type": "remove_effect", "effect_key": "blessed"}
```

### Transformations
```python
{"type": "transform", "transform_key": "wolf_form", "species": "wolf", "duration": 3600}
```

### Currency
```python
{"type": "give_currency", "amount": 50}
{"type": "take_currency", "amount": 25}
```

### Items
```python
{"type": "give_item", "key": "goblin collar", "typeclass": "typeclasses.objects.Object"}
{"type": "take_item", "key": "gold pouch"}
```

### Movement
```python
{"type": "teleport", "destination": "dark_forest_01"}
```

### Tags & Attributes
```python
{"type": "add_tag", "tag": "goblin_marked", "category": "encounters"}
{"type": "remove_tag", "tag": "innocent"}
{"type": "set_attr", "attr": "goblin_encounters", "value": 1}
```

### Scene-Specific
```python
{"type": "set_flag", "flag": "found_rope", "value": True}
{"type": "clear_flag", "flag": "found_rope"}
```

### Chain to Another Scene
```python
{"type": "start_scene", "scene": "aftermath_scene_01"}
```

---

## Complete Example: Simple Trap

```python
POISON_NEEDLE_TRAP = {
    "id": "poison_needle_01",
    "title": "Poison Needle",
    "tags": ["trap", "poison", "container"],
    
    "start": {
        "text": """
As you open the chest, you hear a soft |rclick|n. A needle springs 
from the lock mechanism, piercing your finger before you can react.

The wound is tiny, but you feel the venom spreading immediately—a 
cold numbness creeping up your hand.
""",
        "effects": [
            {"type": "apply_effect", "effect_key": "poisoned", 
             "category": "debuff", "duration": 600}
        ],
        "choices": [
            {"text": "Suck the poison out", "goto": "suck"},
            {"text": "Bandage it and hope for the best", "goto": "bandage"},
            {"text": "Use antidote", "goto": "antidote",
             "condition": {"type": "has_item", "item": "antidote"}},
        ]
    },
    
    "suck": {
        "text": """
You put your finger to your mouth and suck hard, spitting the 
tainted blood onto the ground. It helps—a little. The numbness 
recedes slightly, but doesn't disappear entirely.

You'll live, but you're going to feel this for a while.
""",
        "effects": [
            {"type": "remove_effect", "effect_key": "poisoned"},
            {"type": "apply_effect", "effect_key": "weakened", 
             "category": "debuff", "duration": 300}
        ],
        "end": True
    },
    
    "bandage": {
        "text": """
You wrap the wound tightly, but the poison is already in your 
bloodstream. The numbness spreads to your whole arm.

This is going to get worse before it gets better.
""",
        "end": True
    },
    
    "antidote": {
        "text": """
You quickly uncork your antidote and down it in one gulp. The 
effect is immediate—warmth floods through you, pushing back the 
creeping cold of the venom.

Within moments, you feel fine. Good thing you came prepared.
""",
        "effects": [
            {"type": "take_item", "key": "antidote"},
            {"type": "remove_effect", "effect_key": "poisoned"}
        ],
        "end": True
    }
}

register_scene("poison_needle_01", POISON_NEEDLE_TRAP)
```

---

## Complete Example: Branching Encounter

```python
SLIME_ENCOUNTER = {
    "id": "slime_encounter_01",
    "title": "Slime Encounter", 
    "tags": ["encounter", "slime", "forest", "loss"],
    
    "start": {
        "text": """
A quivering mass of translucent blue goo drops from the tree above, 
landing directly on your head. Before you can react, it's sliding 
down your body, enveloping you in cool, tingling slime.

The creature isn't heavy, but it's |yeverywhere|n—seeping into your 
clothes, coating your skin, probing curiously at every inch of you.
""",
        "choices": [
            {"text": "Struggle violently", "goto": "struggle"},
            {"text": "Try to peel it off carefully", "goto": "peel"},
            {"text": "Stay still and see what it wants", "goto": "still"},
        ]
    },
    
    "struggle": {
        "text": """
You thrash and flail, trying to throw the creature off. But it's 
like fighting water—your hands pass through it, and it simply 
reforms around you.

Worse, your struggling seems to |yexcite|n it. The tingling 
intensifies, and the slime begins to pulse rhythmically against 
your skin.

|mOh. Oh no.|n
""",
        "effects": [
            {"type": "apply_effect", "effect_key": "slime_aroused", 
             "category": "debuff", "duration": 300}
        ],
        "choices": [
            {"text": "Keep struggling", "goto": "struggle_more"},
            {"text": "Go limp", "goto": "give_up"},
        ]
    },
    
    "peel": {
        "text": """
You try to find an edge, somewhere to grip and pull. Your fingers 
sink into the goo uselessly. It's like trying to peel off your own 
shadow.

The slime makes a sound—a wet, gurgling noise that might be 
laughter. It knows you can't remove it.

It seems content to just... cling to you. For now.
""",
        "choices": [
            {"text": "Accept your new companion", "goto": "accept"},
            {"text": "Find water to wash it off", "goto": "water"},
        ]
    },
    
    "still": {
        "text": """
You force yourself to stay calm, letting the slime explore. It 
seems surprised by your lack of resistance—the probing becomes 
gentler, almost curious rather than aggressive.

After a long moment, it makes a satisfied burbling sound and 
settles around you like a second skin. Not unpleasant, really. 
Just... strange.
""",
        "effects": [
            {"type": "set_flag", "flag": "slime_friendly", "value": True}
        ],
        "choices": [
            {"text": "Try to communicate", "goto": "communicate"},
            {"text": "Gently try to remove it now", "goto": "gentle_remove"},
        ]
    },
    
    "struggle_more": {
        "text": """
Your continued resistance only makes things worse. The slime's 
pulsing becomes more insistent, more |yintimate|n. You can feel 
it everywhere, touching you in ways that make your face burn.

By the time it's done with you, you're lying on the forest floor, 
gasping, covered in rapidly-evaporating goo. The slime burbles 
contentedly and oozes away into the underbrush.

You should probably never speak of this.
""",
        "effects": [
            {"type": "apply_effect", "effect_key": "used", 
             "category": "status", "duration": 300},
            {"type": "apply_effect", "effect_key": "satisfied", 
             "category": "buff", "duration": 1800},
            {"type": "apply_effect", "effect_key": "slime_coated", 
             "category": "debuff", "duration": 600}
        ],
        "end": True
    },
    
    "give_up": {
        "text": """
You stop fighting. The slime seems pleased by your surrender, its 
touch becoming almost gentle as it continues its exploration.

It's not painful. It's not even unpleasant, really. Just... 
thorough. Very, very thorough.

When it finally slides off you and disappears into the forest, 
you're left feeling strangely relaxed. And very sticky.
""",
        "effects": [
            {"type": "apply_effect", "effect_key": "slime_coated", 
             "category": "debuff", "duration": 600},
            {"type": "apply_effect", "effect_key": "relaxed", 
             "category": "buff", "duration": 1800}
        ],
        "end": True
    },
    
    "accept": {
        "text": """
Fine. You have a slime now. It seems happy about this arrangement, 
settling into a comfortable position around your torso like a very 
wet, very clingy vest.

It's... actually kind of warm. And the tingling is almost pleasant 
once you stop fighting it.

Maybe this won't be so bad.
""",
        "effects": [
            {"type": "apply_effect", "effect_key": "slime_companion", 
             "category": "status", "duration": 7200},
            {"type": "add_tag", "tag": "befriended_slime", "category": "encounters"}
        ],
        "end": True
    },
    
    "water": {
        "text": """
You stumble toward the sound of running water—a stream, just ahead. 
The slime seems to realize your intent, clinging tighter, but water 
is its weakness.

You plunge in. The slime lets out a distressed gurgle and releases 
you, dissolving into the current and washing away downstream.

You're free. And absolutely soaked. But free.
""",
        "effects": [
            {"type": "apply_effect", "effect_key": "soaked", 
             "category": "debuff", "duration": 600}
        ],
        "end": True
    },
    
    "communicate": {
        "text": """
"Hello?" you try. "Can you understand me?"

The slime pulses once. Twice. Then it forms a crude shape on your 
shoulder—something like a face, with indentations for eyes.

It |ycan|n understand. Or at least, it's trying to.

"What do you want?"

The slime-face looks at you for a long moment. Then it makes a 
sound that might be a sigh, and settles back into a formless blob. 
Apparently the conversation is over.

But you get the sense it just wanted... company. For a while.
""",
        "effects": [
            {"type": "set_flag", "flag": "slime_communicated", "value": True}
        ],
        "goto": "accept"
    },
    
    "gentle_remove": {
        "text": """
Now that it's calm, the slime lets you ease it off. It clings 
briefly, reluctantly, but eventually slides free and drops to 
the ground with a wet plop.

It looks up at you—if a blob can look—and makes a sad little 
burble before oozing away into the undergrowth.

You feel oddly guilty. It just wanted a friend.
""",
        "effects": [
            {"type": "apply_effect", "effect_key": "slime_residue", 
             "category": "debuff", "duration": 300}
        ],
        "end": True
    }
}

register_scene("slime_encounter_01", SLIME_ENCOUNTER)
```

---

## Triggering Scenes

### From Room Entry (Random Encounter)
```python
from world.triggers import add_trigger

add_trigger(
    forest_room,
    "enter",
    effects=[{"type": "start_scene", "scene": "goblin_ambush_01"}],
    conditions=[
        {"type": "random", "chance": 0.1},
        {"type": "time_is", "value": "night"}
    ]
)
```

### From Object Interaction
```python
from world.triggers import add_trigger

add_trigger(
    cursed_idol,
    "get",
    effects=[{"type": "start_scene", "scene": "curse_activation_01"}]
)
```

### From Code
```python
from world.scenes import start_scene, get_scene

start_scene(character, get_scene("slime_encounter_01"))
```

### From Resource Hazard
```python
# In custom harvest logic
if random.random() < 0.05:
    from world.scenes import start_scene, get_scene
    start_scene(character, get_scene("fishing_tentacle_01"))
```

---

## Player Commands During Scenes

When in a scene, players can:

| Input | Action |
|-------|--------|
| `1`, `2`, `3`... | Select choice by number |
| `choose 1` | Select choice by number |
| `scene` | Show current scene status |
| `scene abort` | Force-exit the scene |

---

## Tips for Writing Good Scenes

1. **Show, don't tell.** Describe sensations, actions, reactions.

2. **Keep nodes focused.** One beat per node. If you're writing more than 2-3 paragraphs, split it.

3. **Make choices meaningful.** Each choice should lead somewhere different, even if they eventually converge.

4. **Use conditional choices.** Reward players who have the right items/effects.

5. **Apply effects at the right time.** Usually at scene end or at the moment something happens, not at the start.

6. **Test your scenes.** Walk through every path.

7. **Consider re-encounters.** What happens if they meet this creature again? Use tags to track.

---

## Scene Registry

All scenes should be registered for easy lookup:

```python
from world.scenes import register_scene

register_scene("my_scene_id", MY_SCENE_DICT)
```

Then trigger with:
```python
{"type": "start_scene", "scene": "my_scene_id"}
```

Or organize scenes into files by area/type:
- `world/scenes/grove_encounters.py`
- `world/scenes/museum_events.py`
- `world/scenes/fishing_hazards.py`
