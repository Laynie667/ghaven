"""
Scene & Narrative System for Gilderhaven
=========================================

Interactive branching narratives for events, encounters, traps, losses,
and any situation that needs text + choices + effects without a full NPC.

Inspired by: Corruption of Champions, Trials in Tainted Space, Nimin, 
Flexible Survival, and similar games where encounters are self-contained
narrative sequences.

A Scene is:
- A collection of nodes (pages of content)
- Each node has text, optional choices, optional effects
- Choices lead to other nodes
- Nodes can auto-advance (no choice needed)
- Conditions can hide/show choices
- Effects fire at specific points
- Multiple possible endings

Usage:
    from world.scenes import Scene, run_scene
    
    # Define a scene as a dict
    GOBLIN_ENCOUNTER = {
        "start": {
            "text": "A goblin leaps out of the bushes!",
            "choices": [
                {"text": "Fight", "goto": "fight_1"},
                {"text": "Run", "goto": "flee_1"},
                {"text": "Seduce", "goto": "seduce_1", "condition": {...}},
            ]
        },
        "fight_1": {...},
        ...
    }
    
    # Run it
    run_scene(character, GOBLIN_ENCOUNTER)
"""

import random
import time
from evennia import CmdSet
from evennia.commands.command import Command
from evennia.utils import logger, evmenu

# =============================================================================
# Scene Data Structure
# =============================================================================

"""
SCENE STRUCTURE:

scene_data = {
    "id": "goblin_loss_01",           # Unique identifier
    "title": "Goblin Ambush",         # Optional display title
    "tags": ["combat", "goblin", "loss"],  # For filtering/searching
    
    "start": {                         # Entry node (required)
        "text": "The goblin pins you...",
        "choices": [
            {
                "text": "Struggle",           # What player sees
                "goto": "struggle_1",         # Node to go to
                "condition": {...},           # Optional: when to show
                "effects": [...],             # Optional: effects on choosing this
            },
        ],
        "effects": [...],              # Effects that fire on entering this node
        "goto": "next_node",           # Auto-advance (no choices)
        "delay": 2,                    # Pause before auto-advance (seconds)
        "end": False,                  # Is this an ending?
    },
    
    "node_name": {...},                # Additional nodes
    
    # Special nodes
    "end_good": {"text": "...", "end": True, "effects": [...]},
    "end_bad": {"text": "...", "end": True, "effects": [...]},
}

NODE PROPERTIES:
- text: str or list[str] (if list, picks randomly)
- choices: list of choice dicts
- effects: list of effect dicts (same format as triggers.py)
- goto: str, auto-advance to this node (mutually exclusive with choices)
- delay: float, seconds to wait before auto-advance
- end: bool, if True this node ends the scene
- on_enter: str, callback function name
- on_exit: str, callback function name

CHOICE PROPERTIES:
- text: str, what the player sees
- goto: str, node to go to
- condition: dict, same format as triggers.py conditions
- effects: list, effects that fire when this choice is selected
- disabled_text: str, shown if condition fails (optional)
- hidden: bool, if True + condition fails, choice not shown at all

TEXT FORMATTING:
- {name} - Character's name
- {pronoun} - he/she/they
- {possessive} - his/her/their  
- {object} - him/her/them
- {currency} - Current gold amount
- |r red |n, |g green |n, |y yellow |n, |m magenta |n, etc.
"""


# =============================================================================
# Scene State
# =============================================================================

class SceneState:
    """
    Tracks a character's progress through a scene.
    Stored on character.db.active_scene during scene.
    """
    
    def __init__(self, scene_id, scene_data, character):
        self.scene_id = scene_id
        self.scene_data = scene_data
        self.character = character
        self.current_node = "start"
        self.history = []  # Nodes visited
        self.flags = {}    # Scene-local flags
        self.started_at = time.time()
    
    def to_dict(self):
        """Serialize for storage."""
        return {
            "scene_id": self.scene_id,
            "current_node": self.current_node,
            "history": self.history,
            "flags": self.flags,
            "started_at": self.started_at,
        }
    
    @classmethod
    def from_dict(cls, data, scene_data, character):
        """Deserialize from storage."""
        state = cls(data["scene_id"], scene_data, character)
        state.current_node = data["current_node"]
        state.history = data["history"]
        state.flags = data["flags"]
        state.started_at = data["started_at"]
        return state


# =============================================================================
# Scene Registry
# =============================================================================

# Global registry of all scenes
SCENE_REGISTRY = {}


def register_scene(scene_id, scene_data):
    """
    Register a scene in the global registry.
    
    Args:
        scene_id: Unique identifier
        scene_data: Scene dict
    """
    scene_data["id"] = scene_id
    SCENE_REGISTRY[scene_id] = scene_data


def get_scene(scene_id):
    """Get a scene from the registry."""
    return SCENE_REGISTRY.get(scene_id)


def get_scenes_by_tag(tag):
    """Get all scenes with a specific tag."""
    return [s for s in SCENE_REGISTRY.values() if tag in s.get("tags", [])]


# =============================================================================
# Text Formatting
# =============================================================================

def format_scene_text(text, character, state=None):
    """
    Format scene text with character-specific substitutions.
    
    Args:
        text: Raw text with {placeholders}
        character: Character object
        state: Optional SceneState for scene-local data
    
    Returns:
        str: Formatted text
    """
    if isinstance(text, list):
        text = random.choice(text)
    
    # Character substitutions
    # STUB: Pull actual pronouns from character when that system exists
    pronouns = character.db.pronouns or {"subject": "they", "object": "them", "possessive": "their"}
    
    from world.currency import balance
    
    subs = {
        "name": character.key,
        "pronoun": pronouns.get("subject", "they"),
        "possessive": pronouns.get("possessive", "their"),
        "object": pronouns.get("object", "them"),
        "currency": balance(character),
    }
    
    # Add state flags if present
    if state:
        subs.update(state.flags)
    
    # Safe format (ignore missing keys)
    try:
        return text.format(**subs)
    except KeyError as e:
        logger.log_warn(f"Scene text missing substitution: {e}")
        return text


# =============================================================================
# Condition Checking (reuse from triggers.py)
# =============================================================================

def check_scene_condition(condition, character, state=None):
    """
    Check if a scene condition is met.
    Extends trigger conditions with scene-specific checks.
    
    Args:
        condition: Condition dict
        character: Character to check
        state: Optional SceneState
    
    Returns:
        bool: True if condition met
    """
    cond_type = condition.get("type")
    
    # Scene-specific conditions
    if cond_type == "scene_flag":
        flag = condition.get("flag")
        value = condition.get("value", True)
        if state:
            return state.flags.get(flag) == value
        return False
    
    if cond_type == "visited_node":
        node = condition.get("node")
        if state:
            return node in state.history
        return False
    
    if cond_type == "not_visited_node":
        node = condition.get("node")
        if state:
            return node not in state.history
        return False
    
    if cond_type == "random":
        chance = condition.get("chance", 0.5)
        return random.random() < chance
    
    # Delegate to trigger system for standard conditions
    from world.triggers import check_condition
    return check_condition(condition, character, target=None, context={"state": state})


def check_all_scene_conditions(conditions, character, state=None):
    """Check if all conditions pass."""
    if not conditions:
        return True
    
    # Normalize to list if single dict passed
    if isinstance(conditions, dict):
        conditions = [conditions]
    elif not isinstance(conditions, list):
        return True
    
    for condition in conditions:
        if not isinstance(condition, dict):
            continue
        if not check_scene_condition(condition, character, state):
            return False
    return True


# =============================================================================
# Effect Execution (reuse from triggers.py with scene extensions)
# =============================================================================

def execute_scene_effect(effect, character, state=None):
    """
    Execute a scene effect.
    Extends trigger effects with scene-specific effects.
    
    Args:
        effect: Effect dict
        character: Character receiving effect
        state: Optional SceneState
    
    Returns:
        bool: True if effect executed
    """
    effect_type = effect.get("type")
    
    # Scene-specific effects
    if effect_type == "set_flag":
        flag = effect.get("flag")
        value = effect.get("value", True)
        if state:
            state.flags[flag] = value
        return True
    
    if effect_type == "clear_flag":
        flag = effect.get("flag")
        if state and flag in state.flags:
            del state.flags[flag]
        return True
    
    if effect_type == "random_goto":
        # Handled specially by scene runner
        return True
    
    if effect_type == "end_scene":
        # Handled specially by scene runner
        return True
    
    # Delegate to trigger system for standard effects
    from world.triggers import execute_effect
    return execute_effect(effect, character, target=None, context={"state": state})


def execute_scene_effects(effects, character, state=None):
    """Execute all effects in a list."""
    if not effects:
        return
    
    for effect in effects:
        execute_scene_effect(effect, character, state)


# =============================================================================
# Scene Display & Navigation
# =============================================================================

def display_node(character, node_data, state):
    """
    Display a scene node to the character.
    
    Args:
        character: Character viewing
        node_data: Node dict
        state: SceneState
    """
    # Format and display text
    text = node_data.get("text", "")
    formatted = format_scene_text(text, character, state)
    
    character.msg("\n" + formatted + "\n")
    
    # Execute node entry effects
    effects = node_data.get("effects", [])
    execute_scene_effects(effects, character, state)


def get_available_choices(node_data, character, state):
    """
    Get choices available to the character.
    
    Args:
        node_data: Node dict
        character: Character
        state: SceneState
    
    Returns:
        list: Available choice dicts with index
    """
    choices = node_data.get("choices", [])
    available = []
    
    for i, choice in enumerate(choices):
        condition = choice.get("condition")
        hidden = choice.get("hidden", True)  # Default: hide if condition fails
        
        if condition:
            # Normalize condition to list of dicts
            if isinstance(condition, dict):
                cond_list = [condition]
            elif isinstance(condition, list):
                cond_list = condition
            else:
                # Invalid condition format, treat as no condition
                cond_list = []
            
            if not cond_list or check_all_scene_conditions(cond_list, character, state):
                available.append({"index": i + 1, **choice})
            elif not hidden:
                # Show disabled choice
                disabled_text = choice.get("disabled_text", f"|x{choice['text']} (unavailable)|n")
                available.append({"index": i + 1, "text": disabled_text, "disabled": True})
        else:
            available.append({"index": i + 1, **choice})
    
    return available


def display_choices(character, choices):
    """
    Display available choices to the character.
    
    Args:
        character: Character
        choices: List of available choice dicts
    """
    if not choices:
        return
    
    character.msg("")  # Blank line
    for choice in choices:
        if choice.get("disabled"):
            character.msg(f"  {choice['index']}. {choice['text']}")
        else:
            character.msg(f"  |w{choice['index']}.|n {choice['text']}")
    character.msg("")


# =============================================================================
# Scene Running
# =============================================================================

def start_scene(character, scene_data, scene_id=None):
    """
    Start a scene for a character.
    
    Args:
        character: Character to run scene for
        scene_data: Scene dict (or scene_id string)
        scene_id: Optional scene ID if scene_data is a dict
    
    Returns:
        SceneState: The created scene state
    """
    # Handle scene_id lookup
    if isinstance(scene_data, str):
        scene_id = scene_data
        scene_data = get_scene(scene_id)
        if not scene_data:
            character.msg(f"|rError: Scene '{scene_id}' not found.|n")
            return None
    
    scene_id = scene_id or scene_data.get("id", "unnamed_scene")
    
    # Check if already in a scene
    if character.db.active_scene:
        character.msg("|yYou're already in a scene. Use 'scene abort' to exit.|n")
        return None
    
    # Create state
    state = SceneState(scene_id, scene_data, character)
    
    # Store on character
    character.db.active_scene = state.to_dict()
    character.db.active_scene_data = scene_data  # Store full data for recovery
    
    # Add scene command set
    character.cmdset.add(SceneCmdSet, persistent=False)
    
    # Display first node
    advance_scene(character, state)
    
    return state


def advance_scene(character, state=None, choice_index=None):
    """
    Advance to the next node in a scene.
    
    Args:
        character: Character in scene
        state: SceneState (will load from character if None)
        choice_index: Which choice was selected (1-indexed)
    """
    # Load state if not provided
    if state is None:
        state = get_active_scene(character)
        if not state:
            character.msg("|rYou're not in a scene.|n")
            return
    
    scene_data = state.scene_data
    current_node = state.current_node
    node_data = scene_data.get(current_node)
    
    if not node_data:
        character.msg(f"|rError: Node '{current_node}' not found in scene.|n")
        end_scene(character, state)
        return
    
    # If a choice was made, process it
    if choice_index is not None:
        choices = get_available_choices(node_data, character, state)
        
        # Find the choice
        selected = None
        for choice in choices:
            if choice["index"] == choice_index:
                if choice.get("disabled"):
                    character.msg("|rThat option is not available.|n")
                    display_choices(character, choices)
                    return
                selected = choice
                break
        
        if not selected:
            character.msg("|rInvalid choice.|n")
            display_choices(character, choices)
            return
        
        # Execute choice effects
        execute_scene_effects(selected.get("effects", []), character, state)
        
        # Move to next node
        next_node = selected.get("goto")
        if next_node:
            state.history.append(current_node)
            state.current_node = next_node
            character.db.active_scene = state.to_dict()
            
            # Display new node
            advance_scene(character, state)
            return
    
    # Display current node
    display_node(character, node_data, state)
    
    # Check for end
    if node_data.get("end"):
        end_scene(character, state)
        return
    
    # Check for auto-advance
    goto = node_data.get("goto")
    if goto:
        state.history.append(current_node)
        
        # Handle random goto
        if isinstance(goto, list):
            goto = random.choice(goto)
        
        state.current_node = goto
        character.db.active_scene = state.to_dict()
        
        # Delay if specified
        delay = node_data.get("delay", 0)
        if delay:
            # STUB: Use delay_command or script for actual delay
            character.msg("|x(Press enter to continue...)|n")
            # For now, just advance immediately
        
        advance_scene(character, state)
        return
    
    # Show choices
    choices = get_available_choices(node_data, character, state)
    if choices:
        display_choices(character, choices)
    else:
        # No choices and no goto = stuck, treat as end
        character.msg("|x(Scene ends)|n")
        end_scene(character, state)


def end_scene(character, state=None):
    """
    End a scene and clean up.
    
    Args:
        character: Character in scene
        state: SceneState (optional)
    """
    # Clear state
    character.db.active_scene = None
    character.db.active_scene_data = None
    
    # Remove command set
    character.cmdset.remove(SceneCmdSet)
    
    # Optional: Log completion
    if state:
        logger.log_info(f"Scene '{state.scene_id}' completed by {character.key}")


def get_active_scene(character):
    """
    Get the character's active scene state.
    
    Returns:
        SceneState or None
    """
    state_data = character.db.active_scene
    scene_data = character.db.active_scene_data
    
    if not state_data or not scene_data:
        return None
    
    return SceneState.from_dict(state_data, scene_data, character)


def is_in_scene(character):
    """Check if character is currently in a scene."""
    return character.db.active_scene is not None


# =============================================================================
# Scene Commands
# =============================================================================

class CmdSceneChoice(Command):
    """
    Make a choice in a scene.
    
    Usage:
        1, 2, 3, etc.
        choose <number>
    """
    key = "choose"
    aliases = ["1", "2", "3", "4", "5", "6", "7", "8", "9"]
    locks = "cmd:all()"
    help_category = "Scene"
    
    def func(self):
        if not is_in_scene(self.caller):
            self.caller.msg("You're not in a scene.")
            return
        
        # Parse choice number
        if self.cmdstring.isdigit():
            choice = int(self.cmdstring)
        elif self.args:
            try:
                choice = int(self.args.strip())
            except ValueError:
                self.caller.msg("Enter a number to choose.")
                return
        else:
            self.caller.msg("Enter a number to choose.")
            return
        
        advance_scene(self.caller, choice_index=choice)


class CmdSceneContinue(Command):
    """
    Continue/advance in a scene (for auto-advance nodes).
    
    Usage:
        continue
        c
        (just press enter)
    """
    key = "continue"
    aliases = ["c", ""]
    locks = "cmd:all()"
    help_category = "Scene"
    
    def func(self):
        if not is_in_scene(self.caller):
            # Don't error on empty input when not in scene
            if self.cmdstring == "":
                return
            self.caller.msg("You're not in a scene.")
            return
        
        advance_scene(self.caller)


class CmdSceneAbort(Command):
    """
    Abort/exit the current scene.
    
    Usage:
        abort
        quit scene
        exit scene
    """
    key = "abort"
    aliases = ["quit scene", "exit scene", "leave scene"]
    locks = "cmd:all()"
    help_category = "Scene"
    
    def func(self):
        if not is_in_scene(self.caller):
            self.caller.msg("You're not in a scene.")
            return
        
        self.caller.msg("|yYou forcefully exit the scene.|n")
        end_scene(self.caller)


class CmdSceneStatus(Command):
    """
    Check current scene status.
    
    Usage:
        scene
        scene status
    """
    key = "scene"
    aliases = ["scene status"]
    locks = "cmd:all()"
    help_category = "Scene"
    
    def func(self):
        state = get_active_scene(self.caller)
        if not state:
            self.caller.msg("You're not currently in a scene.")
            return
        
        self.caller.msg(f"|wScene:|n {state.scene_id}")
        self.caller.msg(f"|wCurrent node:|n {state.current_node}")
        self.caller.msg(f"|wNodes visited:|n {len(state.history)}")
        
        # Re-display current node
        node_data = state.scene_data.get(state.current_node, {})
        choices = get_available_choices(node_data, self.caller, state)
        if choices:
            display_choices(self.caller, choices)


class SceneCmdSet(CmdSet):
    """Command set added during scenes."""
    key = "scene_commands"
    priority = 10  # Higher priority to capture number inputs
    
    def at_cmdset_creation(self):
        self.add(CmdSceneChoice())
        self.add(CmdSceneContinue())
        self.add(CmdSceneAbort())
        self.add(CmdSceneStatus())


# =============================================================================
# Integration with Triggers
# =============================================================================

def trigger_scene(scene_id_or_data, character):
    """
    Trigger a scene from the trigger system.
    Can be used as an effect type.
    
    Args:
        scene_id_or_data: Scene ID string or scene dict
        character: Character to run scene for
    """
    if isinstance(scene_id_or_data, str):
        scene_data = get_scene(scene_id_or_data)
        if not scene_data:
            logger.log_warn(f"Trigger tried to start unknown scene: {scene_id_or_data}")
            return False
        start_scene(character, scene_data, scene_id_or_data)
    else:
        start_scene(character, scene_id_or_data)
    return True


# Register "start_scene" as a trigger effect type
# Add to world/triggers.py execute_effect():
#
# if effect_type == "start_scene":
#     from world.scenes import trigger_scene
#     return trigger_scene(effect.get("scene"), actor)


# =============================================================================
# Scene Builder Helpers
# =============================================================================

def simple_scene(text, effects=None, title=None):
    """
    Create a simple single-node scene (no choices).
    
    Args:
        text: Text to display
        effects: Effects to apply
        title: Optional title
    
    Returns:
        dict: Scene data
    """
    return {
        "id": f"simple_{hash(text) % 10000}",
        "title": title,
        "start": {
            "text": text,
            "effects": effects or [],
            "end": True
        }
    }


def confirm_scene(text, confirm_text="Yes", cancel_text="No",
                 confirm_effects=None, cancel_effects=None,
                 confirm_goto=None, cancel_goto=None):
    """
    Create a simple yes/no confirmation scene.
    
    Args:
        text: Prompt text
        confirm_text: Text for confirm option
        cancel_text: Text for cancel option
        confirm_effects: Effects if confirmed
        cancel_effects: Effects if cancelled
        confirm_goto: Node to go to on confirm (or ends)
        cancel_goto: Node to go to on cancel (or ends)
    
    Returns:
        dict: Scene data
    """
    scene = {
        "start": {
            "text": text,
            "choices": [
                {
                    "text": confirm_text,
                    "goto": confirm_goto or "confirmed",
                    "effects": confirm_effects or []
                },
                {
                    "text": cancel_text,
                    "goto": cancel_goto or "cancelled",
                    "effects": cancel_effects or []
                }
            ]
        },
        "confirmed": {
            "text": "",
            "end": True
        },
        "cancelled": {
            "text": "",
            "end": True
        }
    }
    
    return scene


def linear_scene(pages, final_effects=None):
    """
    Create a linear scene (no choices, just pages of text).
    
    Args:
        pages: List of text strings
        final_effects: Effects to apply at end
    
    Returns:
        dict: Scene data
    """
    scene = {}
    
    for i, page in enumerate(pages):
        node_name = f"page_{i}" if i > 0 else "start"
        next_node = f"page_{i + 1}" if i < len(pages) - 1 else None
        
        node = {"text": page}
        
        if next_node:
            node["goto"] = next_node
        else:
            node["end"] = True
            if final_effects:
                node["effects"] = final_effects
        
        scene[node_name] = node
    
    return scene
