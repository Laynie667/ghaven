"""
Quest Commands for Gilderhaven
===============================

Commands for managing quests and tasks.

Commands:
- quests: View active quests
- quest: View specific quest details
- tasks/board: View task board
- task accept: Accept a task from board
- abandon: Abandon a quest
"""

from evennia import Command, CmdSet
from world.quests import (
    get_quest_log, get_active_quests, has_quest, has_completed,
    get_quest_progress, is_quest_complete, can_take_quest,
    give_quest, abandon_quest, complete_quest,
    get_quest_display, get_quest_list_display, get_board_display,
    get_available_board_quests, get_npc_quests, check_daily_reset,
    QUEST_TEMPLATES, QUEST_CATEGORIES
)


class CmdQuests(Command):
    """
    View your active quests.
    
    Usage:
        quests              - List all active quests
        quests completed    - List completed quests
        quests all          - List all including completed
        quests <category>   - Filter by category
    
    Categories: tutorial, daily, npc, exploration, museum, progression
    """
    
    key = "quests"
    aliases = ["questlog", "journal"]
    locks = "cmd:all()"
    help_category = "Quests"
    
    def func(self):
        caller = self.caller
        
        # Check for daily reset
        check_daily_reset(caller)
        
        log = get_quest_log(caller)
        
        if not self.args:
            # Show active quests
            caller.msg(get_quest_list_display(caller))
            return
        
        arg = self.args.strip().lower()
        
        if arg == "completed":
            lines = ["|wCompleted Quests|n", "-" * 40]
            
            if not log["completed"]:
                lines.append("No quests completed yet.")
            else:
                for quest_key in log["completed"]:
                    template = QUEST_TEMPLATES.get(quest_key, {})
                    lines.append(f"  |g[X]|n {template.get('name', quest_key)}")
            
            caller.msg("\n".join(lines))
            return
        
        if arg == "all":
            # Show both
            caller.msg(get_quest_list_display(caller))
            caller.msg("")
            
            lines = ["|wCompleted:|n"]
            for quest_key in log["completed"][:10]:  # Last 10
                template = QUEST_TEMPLATES.get(quest_key, {})
                lines.append(f"  |g[X]|n {template.get('name', quest_key)}")
            
            if len(log["completed"]) > 10:
                lines.append(f"  ... and {len(log['completed']) - 10} more")
            
            caller.msg("\n".join(lines))
            return
        
        # Check if category
        if arg in QUEST_CATEGORIES:
            caller.msg(get_quest_list_display(caller, category=arg))
            return
        
        # Try to find quest by partial name
        for quest_key in log["active"]:
            template = QUEST_TEMPLATES.get(quest_key, {})
            if arg in quest_key.lower() or arg in template.get("name", "").lower():
                caller.msg(get_quest_display(caller, quest_key))
                return
        
        caller.msg(f"No active quest matching '{arg}'.")


class CmdQuest(Command):
    """
    View details of a specific quest.
    
    Usage:
        quest <name>    - View quest details
        quest           - View first active quest
    
    Shows objectives, progress, and rewards.
    """
    
    key = "quest"
    locks = "cmd:all()"
    help_category = "Quests"
    
    def func(self):
        caller = self.caller
        log = get_quest_log(caller)
        
        if not self.args:
            # Show first active quest
            active = get_active_quests(caller)
            if not active:
                caller.msg("No active quests. Check the task board!")
                return
            
            caller.msg(get_quest_display(caller, active[0]))
            return
        
        arg = self.args.strip().lower()
        
        # Find quest by partial name
        for quest_key in log["active"]:
            template = QUEST_TEMPLATES.get(quest_key, {})
            if arg in quest_key.lower() or arg in template.get("name", "").lower():
                caller.msg(get_quest_display(caller, quest_key))
                return
        
        # Also check completed
        for quest_key in log["completed"]:
            template = QUEST_TEMPLATES.get(quest_key, {})
            if arg in quest_key.lower() or arg in template.get("name", "").lower():
                lines = [f"|w{template.get('name', quest_key)}|n"]
                lines.append("|g(Completed)|n")
                lines.append(template.get("desc", ""))
                caller.msg("\n".join(lines))
                return
        
        caller.msg(f"No quest found matching '{arg}'.")


class CmdTasks(Command):
    """
    View the task board.
    
    Usage:
        tasks           - View available tasks
        board           - Same as tasks
        task accept <n> - Accept a task by name
        task info <n>  - View task details before accepting
    
    The task board shows daily tasks and public quests
    that anyone can take.
    """
    
    key = "tasks"
    aliases = ["board", "task", "taskboard"]
    locks = "cmd:all()"
    help_category = "Quests"
    
    def func(self):
        caller = self.caller
        
        # Check for daily reset
        check_daily_reset(caller)
        
        if not self.args:
            caller.msg(get_board_display(caller))
            return
        
        args = self.args.strip().lower().split(None, 1)
        
        if args[0] == "accept" and len(args) > 1:
            quest_name = args[1]
            
            # Find matching quest on board
            available = get_available_board_quests(caller)
            
            for quest_key in available:
                template = QUEST_TEMPLATES.get(quest_key, {})
                name = template.get("name", "").lower()
                
                if quest_name in name or quest_name in quest_key.lower():
                    give_quest(caller, quest_key)
                    return
            
            caller.msg(f"No available task matching '{quest_name}'.")
            return
        
        if args[0] == "info" and len(args) > 1:
            quest_name = args[1]
            
            available = get_available_board_quests(caller)
            
            for quest_key in available:
                template = QUEST_TEMPLATES.get(quest_key, {})
                name = template.get("name", "").lower()
                
                if quest_name in name or quest_name in quest_key.lower():
                    # Show details without accepting
                    lines = [f"|w{template.get('name', quest_key)}|n"]
                    lines.append(template.get("desc", ""))
                    lines.append("")
                    lines.append("|wObjectives:|n")
                    for obj in template.get("objectives", []):
                        lines.append(f"  [ ] {obj.get('desc', '???')}")
                    
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
                    
                    lines.append("")
                    lines.append("Use 'task accept <n>' to accept this task.")
                    
                    caller.msg("\n".join(lines))
                    return
            
            caller.msg(f"No task found matching '{quest_name}'.")
            return
        
        # If just a name, treat as info
        quest_name = self.args.strip().lower()
        available = get_available_board_quests(caller)
        
        for quest_key in available:
            template = QUEST_TEMPLATES.get(quest_key, {})
            name = template.get("name", "").lower()
            
            if quest_name in name or quest_name in quest_key.lower():
                caller.msg(get_quest_display(caller, quest_key))
                caller.msg("")
                caller.msg("Use 'task accept <n>' to accept this task.")
                return
        
        # Not found, show board
        caller.msg(get_board_display(caller))


class CmdAbandon(Command):
    """
    Abandon an active quest.
    
    Usage:
        abandon <quest>     - Abandon a quest by name
        abandon confirm     - Confirm abandonment
    
    Warning: This will lose all progress on the quest!
    Some quests may have cooldowns before you can retake them.
    """
    
    key = "abandon"
    locks = "cmd:all()"
    help_category = "Quests"
    
    def func(self):
        caller = self.caller
        
        if not self.args:
            caller.msg("Abandon which quest? Use 'abandon <quest name>'")
            return
        
        arg = self.args.strip().lower()
        log = get_quest_log(caller)
        
        # Find quest
        found_key = None
        for quest_key in log["active"]:
            template = QUEST_TEMPLATES.get(quest_key, {})
            if arg in quest_key.lower() or arg in template.get("name", "").lower():
                found_key = quest_key
                break
        
        if not found_key:
            caller.msg(f"No active quest matching '{arg}'.")
            return
        
        template = QUEST_TEMPLATES.get(found_key, {})
        quest_name = template.get("name", found_key)
        
        # Check for pending confirmation
        if caller.db.abandon_confirm == found_key:
            abandon_quest(caller, found_key)
            caller.db.abandon_confirm = None
            return
        
        # Ask for confirmation
        caller.db.abandon_confirm = found_key
        caller.msg(f"|yAre you sure you want to abandon '{quest_name}'?|n")
        caller.msg("All progress will be lost!")
        caller.msg(f"Type 'abandon {arg}' again to confirm.")


class CmdTurnIn(Command):
    """
    Turn in a completed quest.
    
    Usage:
        turnin          - Turn in any completed quest
        turnin <quest>  - Turn in specific quest
    
    Some quests must be turned in to the NPC who gave them.
    Use 'talk' to interact with quest-giving NPCs.
    """
    
    key = "turnin"
    aliases = ["complete", "finish"]
    locks = "cmd:all()"
    help_category = "Quests"
    
    def func(self):
        caller = self.caller
        log = get_quest_log(caller)
        
        if not self.args:
            # Try to complete any finished quest
            for quest_key, progress in log["active"].items():
                if progress.get("complete", False):
                    template = QUEST_TEMPLATES.get(quest_key, {})
                    giver = template.get("giver")
                    
                    # Check if needs specific turn-in location
                    if giver and giver not in ("task_board", None):
                        caller.msg(f"'{template.get('name', quest_key)}' must be turned in to {giver}.")
                        continue
                    
                    complete_quest(caller, quest_key)
                    return
            
            caller.msg("No quests ready to turn in.")
            caller.msg("(Some quests must be turned in to specific NPCs)")
            return
        
        arg = self.args.strip().lower()
        
        # Find specific quest
        for quest_key in log["active"]:
            template = QUEST_TEMPLATES.get(quest_key, {})
            if arg in quest_key.lower() or arg in template.get("name", "").lower():
                progress = log["active"][quest_key]
                
                if not progress.get("complete", False):
                    caller.msg("That quest isn't complete yet.")
                    caller.msg(get_quest_display(caller, quest_key))
                    return
                
                giver = template.get("giver")
                if giver and giver not in ("task_board", None):
                    caller.msg(f"This quest must be turned in to {giver}.")
                    return
                
                complete_quest(caller, quest_key)
                return
        
        caller.msg(f"No quest matching '{arg}'.")


class CmdQuestAdmin(Command):
    """
    Admin commands for quests.
    
    Usage:
        questadmin give <player> <quest>    - Give quest to player
        questadmin complete <player> <quest> - Complete quest for player
        questadmin reset <player>           - Reset player's quest log
        questadmin progress <player> <quest> <obj#> <amount> - Set progress
        questadmin list                     - List all quests
    """
    
    key = "questadmin"
    aliases = ["@quest"]
    locks = "cmd:perm(Admin) or perm(Developer)"
    help_category = "Admin"
    
    def func(self):
        caller = self.caller
        
        if not self.args:
            caller.msg("Usage: questadmin <give|complete|reset|progress|list> ...")
            return
        
        args = self.args.strip().split()
        cmd = args[0].lower()
        
        if cmd == "list":
            lines = ["|wAll Quests|n", "-" * 40]
            
            by_cat = {}
            for key, template in QUEST_TEMPLATES.items():
                cat = template.get("category", "misc")
                if cat not in by_cat:
                    by_cat[cat] = []
                by_cat[cat].append((key, template))
            
            for cat, quests in sorted(by_cat.items()):
                lines.append(f"\n|c{cat.upper()}|n")
                for key, template in quests:
                    lines.append(f"  {key}: {template.get('name', '???')}")
            
            caller.msg("\n".join(lines))
            return
        
        if cmd == "give" and len(args) >= 3:
            target_name = args[1]
            quest_key = args[2]
            
            target = caller.search(target_name)
            if not target:
                return
            
            if quest_key not in QUEST_TEMPLATES:
                caller.msg(f"Unknown quest: {quest_key}")
                return
            
            # Force give (bypass checks)
            log = get_quest_log(target)
            template = QUEST_TEMPLATES[quest_key]
            
            objectives_progress = []
            for obj in template.get("objectives", []):
                objectives_progress.append({
                    "type": obj["type"],
                    "target": obj.get("target", "any"),
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
            
            caller.msg(f"Gave quest '{quest_key}' to {target.key}.")
            target.msg(f"|g[Admin gave you quest: {template.get('name', quest_key)}]|n")
            return
        
        if cmd == "complete" and len(args) >= 3:
            target_name = args[1]
            quest_key = args[2]
            
            target = caller.search(target_name)
            if not target:
                return
            
            log = get_quest_log(target)
            
            if quest_key not in log["active"]:
                caller.msg(f"{target.key} doesn't have quest '{quest_key}'.")
                return
            
            # Force complete all objectives
            progress = log["active"][quest_key]
            for obj in progress.get("objectives", []):
                obj["current"] = obj["required"]
                obj["complete"] = True
            progress["complete"] = True
            
            complete_quest(target, quest_key)
            caller.msg(f"Completed quest '{quest_key}' for {target.key}.")
            return
        
        if cmd == "reset" and len(args) >= 2:
            target_name = args[1]
            
            target = caller.search(target_name)
            if not target:
                return
            
            target.db.quest_log = None
            caller.msg(f"Reset quest log for {target.key}.")
            target.msg("|y[Admin reset your quest log]|n")
            return
        
        caller.msg("Usage: questadmin <give|complete|reset|progress|list> ...")


# Need to import time for admin command
import time


# =============================================================================
# Command Set
# =============================================================================

class QuestCmdSet(CmdSet):
    """Quest and task commands."""
    
    key = "quests"
    priority = 1
    
    def at_cmdset_creation(self):
        self.add(CmdQuests())
        self.add(CmdQuest())
        self.add(CmdTasks())
        self.add(CmdAbandon())
        self.add(CmdTurnIn())
        self.add(CmdQuestAdmin())
