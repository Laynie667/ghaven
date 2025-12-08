"""
Quest and Task System for Gilderhaven
======================================

Flexible quest system supporting:
- Task Board: Public quests anyone can take
- NPC Quests: Given through dialogue
- Daily Tasks: Reset each game day
- Repeatable: Can be done multiple times
- Objectives: Gather, visit, talk, deliver, craft, hunt

Architecture:
- Quest templates define structure and rewards
- Player quest log tracks active/completed quests
- Objectives track individual requirements
- Hooks integrate with other systems (gathering, dialogue, etc.)

Usage:
    from world.quests import (
        give_quest, complete_quest, abandon_quest,
        check_objective, get_active_quests, is_quest_complete
    )
    
    # Give quest to player
    give_quest(character, "gather_herbs")
    
    # Check/update objective (called by other systems)
    check_objective(character, "gather", item="wild_herbs", amount=1)
    
    # Complete and give rewards
    if is_quest_complete(character, "gather_herbs"):
        complete_quest(character, "gather_herbs")
"""

import time
from evennia.utils import logger


# =============================================================================
# OBJECTIVE TYPES
# =============================================================================

OBJECTIVE_TYPES = {
    "gather": {
        "desc": "Collect {amount} {target}",
        "check": "item",  # Checked when items enter inventory
    },
    "deliver": {
        "desc": "Deliver {target} to {destination}",
        "check": "talk",  # Checked when talking to NPC
    },
    "visit": {
        "desc": "Visit {target}",
        "check": "move",  # Checked on room entry
    },
    "talk": {
        "desc": "Talk to {target}",
        "check": "talk",  # Checked when starting dialogue
    },
    "craft": {
        "desc": "Craft {amount} {target}",
        "check": "craft",  # Checked when crafting
    },
    "hunt": {
        "desc": "Defeat {amount} {target}",
        "check": "combat",  # Checked on enemy defeat
    },
    "use": {
        "desc": "Use {target}",
        "check": "use",  # Checked when using item/object
    },
    "fish": {
        "desc": "Catch {amount} {target}",
        "check": "item",  # Checked like gather
    },
    "mine": {
        "desc": "Mine {amount} {target}",
        "check": "item",  # Checked like gather
    },
    "forage": {
        "desc": "Forage {amount} {target}",
        "check": "item",  # Checked like gather
    },
    "explore": {
        "desc": "Explore {amount} new areas",
        "check": "move",  # Counted on first room visits
    },
    "spend": {
        "desc": "Spend {amount} coins",
        "check": "currency",  # Checked on spending
    },
    "earn": {
        "desc": "Earn {amount} coins",
        "check": "currency",  # Checked on earning
    },
    "scene": {
        "desc": "Complete the {target} scene",
        "check": "scene",  # Checked on scene completion
    },
    "custom": {
        "desc": "{desc}",
        "check": "manual",  # Manually triggered
    },
}


# =============================================================================
# QUEST TEMPLATES
# =============================================================================

QUEST_TEMPLATES = {
    # ===================
    # TUTORIAL QUESTS
    # ===================
    "tutorial_gather": {
        "name": "First Steps: Gathering",
        "desc": "Learn how to gather resources in the Grove.",
        "giver": None,  # Auto-given or from board
        "category": "tutorial",
        "level": 1,
        "objectives": [
            {"type": "gather", "target": "any", "amount": 5, "desc": "Gather 5 of any resource"},
        ],
        "rewards": {
            "coins": 25,
            "items": [],
            "exp": 10,
        },
        "on_complete": "You've learned the basics of gathering!",
        "repeatable": False,
    },
    
    "tutorial_shop": {
        "name": "First Steps: Shopping",
        "desc": "Learn how to buy and sell at the market.",
        "giver": None,
        "category": "tutorial",
        "level": 1,
        "objectives": [
            {"type": "visit", "target": "Market Square", "desc": "Visit the Market Square"},
            {"type": "talk", "target": "Greta", "desc": "Talk to Greta the Toolsmith"},
        ],
        "rewards": {
            "coins": 50,
            "items": ["basic_fishing_rod"],
            "exp": 15,
        },
        "on_complete": "You now know your way around the market!",
        "repeatable": False,
    },
    
    "tutorial_fishing": {
        "name": "First Steps: Fishing",
        "desc": "Try your hand at fishing.",
        "giver": None,
        "category": "tutorial",
        "level": 1,
        "requires": ["tutorial_shop"],  # Must complete shop tutorial first
        "objectives": [
            {"type": "fish", "target": "any", "amount": 3, "desc": "Catch 3 fish"},
        ],
        "rewards": {
            "coins": 30,
            "items": [],
            "exp": 15,
        },
        "on_complete": "You're getting the hang of fishing!",
        "repeatable": False,
    },
    
    # ===================
    # DAILY TASKS
    # ===================
    "daily_gather": {
        "name": "Daily: Resource Run",
        "desc": "Gather resources for the Grove's stores.",
        "giver": "task_board",
        "category": "daily",
        "level": 1,
        "objectives": [
            {"type": "gather", "target": "any", "amount": 10, "desc": "Gather 10 resources"},
        ],
        "rewards": {
            "coins": 50,
            "items": [],
            "exp": 25,
        },
        "on_complete": "Another productive day!",
        "repeatable": True,
        "cooldown": 86400,  # 24 hours in seconds (or 1 game day)
        "daily": True,
    },
    
    "daily_fishing": {
        "name": "Daily: Fresh Catch",
        "desc": "The tavern needs fresh fish for today's menu.",
        "giver": "task_board",
        "category": "daily",
        "level": 1,
        "objectives": [
            {"type": "fish", "target": "any", "amount": 5, "desc": "Catch 5 fish"},
        ],
        "rewards": {
            "coins": 60,
            "items": [],
            "exp": 30,
        },
        "on_complete": "Big Tom will be happy with this catch!",
        "repeatable": True,
        "daily": True,
    },
    
    "daily_mining": {
        "name": "Daily: Ore Collection",
        "desc": "The smithy needs ore for repairs.",
        "giver": "task_board",
        "category": "daily",
        "level": 1,
        "objectives": [
            {"type": "mine", "target": "any", "amount": 5, "desc": "Mine 5 ore"},
        ],
        "rewards": {
            "coins": 75,
            "items": [],
            "exp": 35,
        },
        "on_complete": "The smithy thanks you for the ore.",
        "repeatable": True,
        "daily": True,
    },
    
    "daily_exploration": {
        "name": "Daily: Wanderer",
        "desc": "Explore the lands around the Grove.",
        "giver": "task_board",
        "category": "daily",
        "level": 1,
        "objectives": [
            {"type": "explore", "target": "any", "amount": 5, "desc": "Visit 5 different rooms"},
        ],
        "rewards": {
            "coins": 40,
            "items": [],
            "exp": 20,
        },
        "on_complete": "Your wandering has paid off!",
        "repeatable": True,
        "daily": True,
    },
    
    # ===================
    # NPC QUESTS
    # ===================
    "greta_tools": {
        "name": "Quality Materials",
        "desc": "Greta needs raw materials for her tools.",
        "giver": "Greta",
        "category": "npc",
        "level": 2,
        "objectives": [
            {"type": "gather", "target": "iron_ore", "amount": 10, "desc": "Gather 10 Iron Ore"},
            {"type": "gather", "target": "oak_wood", "amount": 5, "desc": "Gather 5 Oak Wood"},
        ],
        "rewards": {
            "coins": 150,
            "items": ["quality_pickaxe"],
            "exp": 50,
        },
        "on_complete": "Greta crafts you a quality pickaxe as thanks.",
        "repeatable": True,
        "cooldown": 172800,  # 48 hours
    },
    
    "whisper_herbs": {
        "name": "Rare Ingredients",
        "desc": "Whisper the Apothecary needs rare herbs.",
        "giver": "Whisper",
        "category": "npc",
        "level": 2,
        "objectives": [
            {"type": "forage", "target": "moonpetal", "amount": 3, "desc": "Find 3 Moonpetals"},
            {"type": "forage", "target": "starleaf", "amount": 3, "desc": "Find 3 Starleaves"},
        ],
        "rewards": {
            "coins": 200,
            "items": ["health_potion", "health_potion", "stamina_potion"],
            "exp": 60,
        },
        "on_complete": "Whisper brews you some potions in gratitude.",
        "repeatable": True,
        "cooldown": 172800,
    },
    
    "tom_delivery": {
        "name": "Special Delivery",
        "desc": "Big Tom needs supplies delivered.",
        "giver": "Big Tom",
        "category": "npc",
        "level": 1,
        "objectives": [
            {"type": "deliver", "target": "supplies", "destination": "Greta", 
             "desc": "Deliver supplies to Greta"},
        ],
        "rewards": {
            "coins": 50,
            "items": ["bread", "ale"],
            "exp": 25,
        },
        "gives_item": "tom_supplies",  # Given when quest accepted
        "on_complete": "Tom tosses you some food and drink for your trouble.",
        "repeatable": True,
        "cooldown": 86400,
    },
    
    # ===================
    # EXPLORATION QUESTS
    # ===================
    "explore_whisperwood": {
        "name": "Whispers in the Wood",
        "desc": "Explore the mysterious Whisperwood.",
        "giver": "task_board",
        "category": "exploration",
        "level": 1,
        "objectives": [
            {"type": "visit", "target": "Whisperwood Entrance", "desc": "Enter the Whisperwood"},
            {"type": "visit", "target": "Ancient Tree", "desc": "Find the Ancient Tree"},
            {"type": "scene", "target": "whisperwood_spirit", "desc": "Meet the forest spirit"},
        ],
        "rewards": {
            "coins": 100,
            "items": [],
            "exp": 75,
        },
        "on_complete": "You've uncovered some of the Whisperwood's secrets.",
        "repeatable": False,
    },
    
    "explore_tidepools": {
        "name": "Secrets of the Shore",
        "desc": "Discover what lies along the coast.",
        "giver": "task_board",
        "category": "exploration",
        "level": 1,
        "objectives": [
            {"type": "visit", "target": "Tidepools", "desc": "Visit the Tidepools"},
            {"type": "gather", "target": "shell", "amount": 5, "desc": "Collect 5 shells"},
            {"type": "fish", "target": "any", "amount": 3, "desc": "Catch 3 fish"},
        ],
        "rewards": {
            "coins": 120,
            "items": ["pearl"],
            "exp": 60,
        },
        "on_complete": "The shore has revealed its treasures to you.",
        "repeatable": False,
    },
    
    # ===================
    # MUSEUM QUESTS (Curator/Claude)
    # ===================
    "museum_tour": {
        "name": "A Grand Tour",
        "desc": "The Curator wishes to show you the museum.",
        "giver": "The Curator",
        "category": "museum",
        "level": 1,
        "objectives": [
            {"type": "visit", "target": "Museum Foyer", "desc": "Enter the Museum"},
            {"type": "visit", "target": "The Gallery", "desc": "Visit the Gallery"},
            {"type": "visit", "target": "Hall of Curiosities", "desc": "See the Curiosities"},
            {"type": "talk", "target": "The Curator", "desc": "Speak with the Curator"},
        ],
        "rewards": {
            "coins": 75,
            "items": [],
            "exp": 50,
        },
        "on_complete": "The Curator seems pleased by your interest.",
        "repeatable": False,
    },
    
    "museum_donation": {
        "name": "A Worthy Donation",
        "desc": "The Curator seeks interesting specimens for the collection.",
        "giver": "The Curator",
        "category": "museum",
        "level": 2,
        "objectives": [
            {"type": "deliver", "target": "rare_specimen", "destination": "The Curator",
             "desc": "Bring a rare find to the Curator"},
        ],
        "rewards": {
            "coins": 200,
            "items": [],
            "exp": 100,
        },
        "on_complete": "The Curator accepts your donation with great interest.",
        "repeatable": True,
        "cooldown": 86400,
    },
    
    # ===================
    # SPECIAL/CHAIN QUESTS  
    # ===================
    "first_home": {
        "name": "A Place to Call Home",
        "desc": "Save up for your first home in the Grove.",
        "giver": None,
        "category": "progression",
        "level": 1,
        "objectives": [
            {"type": "earn", "target": "coins", "amount": 500, "desc": "Earn 500 coins"},
        ],
        "rewards": {
            "coins": 0,
            "items": [],
            "exp": 100,
            "unlock": "housing",  # Unlocks housing system
        },
        "on_complete": "You can now purchase a home! Visit the housing office.",
        "repeatable": False,
    },
}


# =============================================================================
# QUEST CATEGORIES
# =============================================================================

QUEST_CATEGORIES = {
    "tutorial": {
        "name": "Tutorial",
        "desc": "Learning the basics",
        "color": "|c",
    },
    "daily": {
        "name": "Daily Tasks",
        "desc": "Reset each day",
        "color": "|y",
    },
    "npc": {
        "name": "NPC Quests", 
        "desc": "Given by characters",
        "color": "|g",
    },
    "exploration": {
        "name": "Exploration",
        "desc": "Discover new places",
        "color": "|m",
    },
    "museum": {
        "name": "Museum",
        "desc": "The Curator's tasks",
        "color": "|b",
    },
    "progression": {
        "name": "Progression",
        "desc": "Major milestones",
        "color": "|w",
    },
}


# =============================================================================
# QUEST STATE FUNCTIONS
# =============================================================================

def get_quest_log(character):
    """Get character's quest log."""
    if not character.db.quest_log:
        character.db.quest_log = {
            "active": {},      # quest_key: {progress}
            "completed": [],   # List of completed quest keys
            "cooldowns": {},   # quest_key: timestamp when available again
        }
    return character.db.quest_log


def get_active_quests(character):
    """Get list of active quest keys."""
    log = get_quest_log(character)
    return list(log["active"].keys())


def get_completed_quests(character):
    """Get list of completed quest keys."""
    log = get_quest_log(character)
    return log["completed"]


def has_quest(character, quest_key):
    """Check if character has a specific quest active."""
    log = get_quest_log(character)
    return quest_key in log["active"]


def has_completed(character, quest_key):
    """Check if character has completed a quest."""
    log = get_quest_log(character)
    return quest_key in log["completed"]


def get_quest_progress(character, quest_key):
    """
    Get progress data for an active quest.
    
    Returns:
        dict: {objectives: [{current, required, complete}, ...], complete: bool}
    """
    log = get_quest_log(character)
    return log["active"].get(quest_key)


def is_quest_complete(character, quest_key):
    """Check if all objectives for a quest are complete."""
    progress = get_quest_progress(character, quest_key)
    if not progress:
        return False
    return progress.get("complete", False)


def can_take_quest(character, quest_key):
    """
    Check if character can take a quest.
    
    Checks:
    - Quest exists
    - Not already active
    - Prerequisites met
    - Not on cooldown
    - Not already completed (for non-repeatables)
    """
    template = QUEST_TEMPLATES.get(quest_key)
    if not template:
        return False, "Quest not found."
    
    log = get_quest_log(character)
    
    # Already active?
    if quest_key in log["active"]:
        return False, "You already have this quest."
    
    # Check prerequisites
    requires = template.get("requires", [])
    for req in requires:
        if req not in log["completed"]:
            req_template = QUEST_TEMPLATES.get(req, {})
            req_name = req_template.get("name", req)
            return False, f"Requires completion of: {req_name}"
    
    # Check if repeatable
    if not template.get("repeatable", False):
        if quest_key in log["completed"]:
            return False, "You've already completed this quest."
    
    # Check cooldown
    cooldown_until = log["cooldowns"].get(quest_key, 0)
    if time.time() < cooldown_until:
        remaining = int(cooldown_until - time.time())
        hours = remaining // 3600
        minutes = (remaining % 3600) // 60
        if hours > 0:
            return False, f"Available again in {hours}h {minutes}m."
        else:
            return False, f"Available again in {minutes} minutes."
    
    return True, None


# =============================================================================
# QUEST MANAGEMENT
# =============================================================================

def give_quest(character, quest_key, silent=False):
    """
    Give a quest to a character.
    
    Args:
        character: The character
        quest_key: Quest template key
        silent: Don't send messages
    
    Returns:
        bool: Success
    """
    can_take, reason = can_take_quest(character, quest_key)
    if not can_take:
        if not silent:
            character.msg(f"|rCannot take quest: {reason}|n")
        return False
    
    template = QUEST_TEMPLATES.get(quest_key)
    log = get_quest_log(character)
    
    # Initialize progress
    objectives_progress = []
    for obj in template.get("objectives", []):
        objectives_progress.append({
            "type": obj["type"],
            "target": obj.get("target", "any"),
            "destination": obj.get("destination"),
            "current": 0,
            "required": obj.get("amount", 1),
            "complete": False,
            "desc": obj.get("desc", ""),
        })
    
    log["active"][quest_key] = {
        "started": time.time(),
        "objectives": objectives_progress,
        "complete": False,
    }
    
    # Give starting items if any
    if template.get("gives_item"):
        try:
            from world.items import give_item
            give_item(character, template["gives_item"])
        except Exception as e:
            logger.log_err(f"Error giving quest item: {e}")
    
    if not silent:
        category = template.get("category", "misc")
        cat_data = QUEST_CATEGORIES.get(category, {})
        color = cat_data.get("color", "|w")
        
        character.msg(f"\n{color}Quest Accepted: {template['name']}|n")
        character.msg(f"{template.get('desc', '')}")
        character.msg("")
        character.msg("|wObjectives:|n")
        for obj in objectives_progress:
            character.msg(f"  [ ] {obj['desc']}")
    
    return True


def abandon_quest(character, quest_key, silent=False):
    """
    Abandon an active quest.
    
    Args:
        character: The character
        quest_key: Quest to abandon
        silent: Don't send messages
    
    Returns:
        bool: Success
    """
    log = get_quest_log(character)
    
    if quest_key not in log["active"]:
        if not silent:
            character.msg("You don't have that quest.")
        return False
    
    template = QUEST_TEMPLATES.get(quest_key, {})
    
    del log["active"][quest_key]
    
    if not silent:
        character.msg(f"|yAbandoned quest: {template.get('name', quest_key)}|n")
    
    return True


def complete_quest(character, quest_key, silent=False):
    """
    Complete a quest and give rewards.
    
    Args:
        character: The character
        quest_key: Quest to complete
        silent: Don't send messages
    
    Returns:
        bool: Success
    """
    log = get_quest_log(character)
    
    if quest_key not in log["active"]:
        return False
    
    progress = log["active"][quest_key]
    if not progress.get("complete", False):
        # Check if actually complete
        all_done = all(obj.get("complete", False) for obj in progress.get("objectives", []))
        if not all_done:
            if not silent:
                character.msg("Quest objectives not yet complete.")
            return False
    
    template = QUEST_TEMPLATES.get(quest_key, {})
    rewards = template.get("rewards", {})
    
    # Remove from active
    del log["active"][quest_key]
    
    # Add to completed (if not already there for repeatables)
    if quest_key not in log["completed"]:
        log["completed"].append(quest_key)
    
    # Set cooldown for repeatables
    if template.get("repeatable", False):
        cooldown = template.get("cooldown", 86400)  # Default 24h
        log["cooldowns"][quest_key] = time.time() + cooldown
    
    # Give rewards
    reward_msgs = []
    
    # Coins
    if rewards.get("coins", 0) > 0:
        try:
            from world.currency import receive
            receive(character, rewards["coins"])
            reward_msgs.append(f"{rewards['coins']} coins")
        except Exception as e:
            logger.log_err(f"Error giving coin reward: {e}")
    
    # Items
    for item_key in rewards.get("items", []):
        try:
            from world.items import give_item, get_item_template
            item = give_item(character, item_key)
            if item:
                template_data = get_item_template(item_key)
                reward_msgs.append(template_data.get("name", item_key))
        except Exception as e:
            logger.log_err(f"Error giving item reward: {e}")
    
    # Experience (stored but not used yet)
    if rewards.get("exp", 0) > 0:
        current_exp = character.db.experience or 0
        character.db.experience = current_exp + rewards["exp"]
        reward_msgs.append(f"{rewards['exp']} exp")
    
    if not silent:
        character.msg(f"\n|g*** Quest Complete: {template.get('name', quest_key)} ***|n")
        if template.get("on_complete"):
            character.msg(template["on_complete"])
        if reward_msgs:
            character.msg(f"|yRewards: {', '.join(reward_msgs)}|n")
    
    return True


# =============================================================================
# OBJECTIVE CHECKING
# =============================================================================

def check_objective(character, check_type, **kwargs):
    """
    Check and update quest objectives.
    
    Called by other systems when relevant actions occur.
    
    Args:
        character: The character
        check_type: Type of check (item, talk, move, craft, etc.)
        **kwargs: Context for the check
            - item: Item key for gather/fish/mine
            - amount: Amount gathered
            - npc: NPC key for talk checks
            - room: Room key for visit checks
            - scene: Scene key for scene completion
    
    Returns:
        list: Quest keys with updated progress
    """
    log = get_quest_log(character)
    updated = []
    
    for quest_key, progress in list(log["active"].items()):
        template = QUEST_TEMPLATES.get(quest_key, {})
        quest_updated = False
        
        for i, obj in enumerate(progress.get("objectives", [])):
            if obj.get("complete", False):
                continue
            
            obj_type = obj.get("type")
            obj_check = OBJECTIVE_TYPES.get(obj_type, {}).get("check")
            
            if obj_check != check_type:
                continue
            
            # Check based on type
            matched = False
            amount_to_add = 0
            
            if check_type == "item":
                # Gather/fish/mine/forage
                item_key = kwargs.get("item", "")
                amount = kwargs.get("amount", 1)
                target = obj.get("target", "any")
                
                if target == "any" or target in item_key or item_key == target:
                    matched = True
                    amount_to_add = amount
            
            elif check_type == "talk":
                # Talk to NPC or deliver
                npc = kwargs.get("npc", "")
                
                if obj_type == "talk":
                    target = obj.get("target", "")
                    if target.lower() in npc.lower() or npc.lower() in target.lower():
                        matched = True
                        amount_to_add = 1
                
                elif obj_type == "deliver":
                    destination = obj.get("destination", "")
                    if destination.lower() in npc.lower():
                        # Check if character has the delivery item
                        # For now, just mark complete
                        matched = True
                        amount_to_add = 1
            
            elif check_type == "move":
                # Visit room or explore
                room = kwargs.get("room", "")
                room_key = kwargs.get("room_key", "")
                
                if obj_type == "visit":
                    target = obj.get("target", "")
                    if target.lower() in room.lower() or target.lower() in room_key.lower():
                        matched = True
                        amount_to_add = 1
                
                elif obj_type == "explore":
                    # Count unique rooms visited
                    if kwargs.get("first_visit", False):
                        matched = True
                        amount_to_add = 1
            
            elif check_type == "scene":
                scene_key = kwargs.get("scene", "")
                target = obj.get("target", "")
                
                if target.lower() in scene_key.lower() or scene_key == target:
                    matched = True
                    amount_to_add = 1
            
            elif check_type == "currency":
                action = kwargs.get("action", "")  # "earn" or "spend"
                amount = kwargs.get("amount", 0)
                
                if obj_type == action:
                    matched = True
                    amount_to_add = amount
            
            elif check_type == "manual":
                # Manually triggered - check target matches
                target = kwargs.get("target", "")
                obj_target = obj.get("target", "")
                
                if target == obj_target:
                    matched = True
                    amount_to_add = kwargs.get("amount", 1)
            
            # Update progress
            if matched:
                obj["current"] = min(obj["current"] + amount_to_add, obj["required"])
                if obj["current"] >= obj["required"]:
                    obj["complete"] = True
                quest_updated = True
        
        # Check if quest is now complete
        if quest_updated:
            all_done = all(o.get("complete", False) for o in progress.get("objectives", []))
            if all_done:
                progress["complete"] = True
                character.msg(f"|g[Quest '{template.get('name', quest_key)}' objectives complete! Return to turn in.]|n")
            updated.append(quest_key)
    
    return updated


def check_gather_objective(character, item_key, amount=1):
    """Convenience function for gathering."""
    return check_objective(character, "item", item=item_key, amount=amount)


def check_talk_objective(character, npc_name):
    """Convenience function for talking to NPCs."""
    return check_objective(character, "talk", npc=npc_name)


def check_visit_objective(character, room_name, room_key="", first_visit=False):
    """Convenience function for visiting rooms."""
    return check_objective(character, "move", room=room_name, room_key=room_key, first_visit=first_visit)


def check_scene_objective(character, scene_key):
    """Convenience function for completing scenes."""
    return check_objective(character, "scene", scene=scene_key)


# =============================================================================
# QUEST DISPLAY
# =============================================================================

def get_quest_display(character, quest_key):
    """
    Get formatted display for a quest.
    
    Returns:
        str: Formatted quest info
    """
    template = QUEST_TEMPLATES.get(quest_key, {})
    progress = get_quest_progress(character, quest_key)
    
    if not template:
        return f"Unknown quest: {quest_key}"
    
    category = template.get("category", "misc")
    cat_data = QUEST_CATEGORIES.get(category, {})
    color = cat_data.get("color", "|w")
    
    lines = []
    lines.append(f"{color}{template.get('name', quest_key)}|n")
    lines.append(template.get("desc", ""))
    lines.append("")
    
    lines.append("|wObjectives:|n")
    if progress:
        for obj in progress.get("objectives", []):
            if obj.get("complete", False):
                mark = "|g[X]|n"
            else:
                mark = "[ ]"
            
            current = obj.get("current", 0)
            required = obj.get("required", 1)
            desc = obj.get("desc", "???")
            
            if required > 1:
                lines.append(f"  {mark} {desc} ({current}/{required})")
            else:
                lines.append(f"  {mark} {desc}")
    else:
        for obj in template.get("objectives", []):
            lines.append(f"  [ ] {obj.get('desc', '???')}")
    
    # Rewards
    rewards = template.get("rewards", {})
    reward_parts = []
    if rewards.get("coins"):
        reward_parts.append(f"{rewards['coins']} coins")
    if rewards.get("exp"):
        reward_parts.append(f"{rewards['exp']} exp")
    if rewards.get("items"):
        reward_parts.append(f"{len(rewards['items'])} item(s)")
    
    if reward_parts:
        lines.append("")
        lines.append(f"|yRewards: {', '.join(reward_parts)}|n")
    
    return "\n".join(lines)


def get_quest_list_display(character, category=None):
    """
    Get formatted list of active quests.
    
    Args:
        character: The character
        category: Filter by category (optional)
    
    Returns:
        str: Formatted quest list
    """
    log = get_quest_log(character)
    
    lines = ["|wActive Quests|n", "-" * 40]
    
    if not log["active"]:
        lines.append("No active quests.")
        return "\n".join(lines)
    
    for quest_key, progress in log["active"].items():
        template = QUEST_TEMPLATES.get(quest_key, {})
        
        if category and template.get("category") != category:
            continue
        
        cat = template.get("category", "misc")
        cat_data = QUEST_CATEGORIES.get(cat, {})
        color = cat_data.get("color", "|w")
        
        # Count completion
        total = len(progress.get("objectives", []))
        done = sum(1 for o in progress.get("objectives", []) if o.get("complete", False))
        
        status = f"({done}/{total})"
        if progress.get("complete", False):
            status = "|g(COMPLETE)|n"
        
        lines.append(f"  {color}{template.get('name', quest_key)}|n {status}")
    
    return "\n".join(lines)


# =============================================================================
# TASK BOARD
# =============================================================================

def get_available_board_quests(character):
    """
    Get quests available from the task board.
    
    Returns:
        list: Quest keys available to take
    """
    available = []
    
    for quest_key, template in QUEST_TEMPLATES.items():
        giver = template.get("giver")
        
        # Task board quests or quests with no specific giver
        if giver not in ("task_board", None):
            continue
        
        can_take, _ = can_take_quest(character, quest_key)
        if can_take:
            available.append(quest_key)
    
    return available


def get_board_display(character):
    """
    Get formatted task board display.
    
    Returns:
        str: Formatted board
    """
    available = get_available_board_quests(character)
    
    lines = ["|w=== Task Board ===|n", ""]
    
    if not available:
        lines.append("No tasks available at this time.")
        lines.append("Check back later!")
        return "\n".join(lines)
    
    # Group by category
    by_category = {}
    for quest_key in available:
        template = QUEST_TEMPLATES.get(quest_key, {})
        cat = template.get("category", "misc")
        if cat not in by_category:
            by_category[cat] = []
        by_category[cat].append(quest_key)
    
    for cat, quests in by_category.items():
        cat_data = QUEST_CATEGORIES.get(cat, {})
        color = cat_data.get("color", "|w")
        cat_name = cat_data.get("name", cat.title())
        
        lines.append(f"{color}[ {cat_name} ]|n")
        
        for quest_key in quests:
            template = QUEST_TEMPLATES.get(quest_key, {})
            name = template.get("name", quest_key)
            level = template.get("level", 1)
            
            rewards = template.get("rewards", {})
            reward_str = ""
            if rewards.get("coins"):
                reward_str = f" - {rewards['coins']} coins"
            
            lines.append(f"  {name} (Lv.{level}){reward_str}")
        
        lines.append("")
    
    lines.append("Use 'task accept <name>' to accept a task.")
    
    return "\n".join(lines)


# =============================================================================
# DAILY RESET
# =============================================================================

def reset_daily_quests(character):
    """
    Reset daily quest cooldowns.
    
    Called when a new game day starts.
    """
    log = get_quest_log(character)
    
    for quest_key, template in QUEST_TEMPLATES.items():
        if template.get("daily", False):
            # Clear cooldown
            if quest_key in log["cooldowns"]:
                del log["cooldowns"][quest_key]


def check_daily_reset(character):
    """
    Check if dailies should reset based on game time.
    
    Call this periodically or on login.
    """
    try:
        from world.time_weather import get_time
        game_time = get_time()
        
        last_daily = character.db.last_daily_reset or {}
        current_day = game_time.get("day", 1)
        current_month = game_time.get("month", 0)
        
        if (last_daily.get("day") != current_day or 
            last_daily.get("month") != current_month):
            reset_daily_quests(character)
            character.db.last_daily_reset = {
                "day": current_day,
                "month": current_month,
            }
            return True
    except ImportError:
        pass
    
    return False


# =============================================================================
# NPC INTEGRATION
# =============================================================================

def get_npc_quests(character, npc_name):
    """
    Get quests available from a specific NPC.
    
    Args:
        character: The character
        npc_name: Name of the NPC
    
    Returns:
        list: Available quest keys
    """
    available = []
    
    for quest_key, template in QUEST_TEMPLATES.items():
        giver = template.get("giver", "")
        
        if not giver or giver in ("task_board", None):
            continue
        
        # Fuzzy match NPC name
        if giver.lower() not in npc_name.lower() and npc_name.lower() not in giver.lower():
            continue
        
        can_take, _ = can_take_quest(character, quest_key)
        if can_take:
            available.append(quest_key)
    
    return available


def npc_has_quest(character, npc_name):
    """Check if NPC has available quests for character."""
    return len(get_npc_quests(character, npc_name)) > 0


def npc_can_complete_quest(character, npc_name):
    """Check if character can turn in quest to this NPC."""
    log = get_quest_log(character)
    
    for quest_key, progress in log["active"].items():
        if not progress.get("complete", False):
            continue
        
        template = QUEST_TEMPLATES.get(quest_key, {})
        giver = template.get("giver", "")
        
        if giver.lower() in npc_name.lower() or npc_name.lower() in giver.lower():
            return True
    
    return False
