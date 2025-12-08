"""
Gathering Commands for Gilderhaven
===================================

Commands for harvesting resources from the world:
- forage: General gathering (flowers, herbs, mushrooms)
- fish: Water resources
- mine: Ore, gems, stone
- catch: Bugs, crabs, small creatures
- gather: Universal fallback
- search: Hidden treasures, rare finds

Each command:
1. Scans room for appropriate resource nodes
2. Allows targeting specific nodes
3. Calls world.resources.harvest()
4. Displays results with rarity colors
5. Can trigger random scenes

Usage:
    forage                  - Forage from first available node
    forage mushroom         - Forage from mushroom patch specifically
    fish                    - Fish from fishing spot
    mine copper             - Mine copper vein
    catch bugs              - Catch bugs from flower patch
    gather                  - Gather from any node
    resources               - List all gatherable nodes in room
"""

from evennia import Command, CmdSet
from evennia.utils import logger
import random
import time

from world.resources import (
    is_resource_node,
    get_resource_data,
    is_available,
    has_required_tool,
    harvest,
    RESOURCE_TYPES,
    RARITY_TIERS,
)


# =============================================================================
# Helper Functions
# =============================================================================

def find_nodes_in_room(room, resource_type=None):
    """
    Find all resource nodes in a room.
    
    Args:
        room: Room to search
        resource_type: Optional filter by type (forage, fishing, mining, etc.)
    
    Returns:
        list: Resource node dicts with 'virtual', 'key', 'data', and optionally 'obj'
    """
    nodes = []
    
    # Check room's resource_nodes attribute (defined in area content)
    room_nodes = room.db.resource_nodes or []
    for node_data in room_nodes:
        # Content files use "type", resources.py uses "resource_type"
        node_type = node_data.get("resource_type") or node_data.get("type", "gather")
        
        # Filter by type if specified
        if resource_type and node_type != resource_type:
            continue
        
        # Normalize the data to always have resource_type
        normalized = dict(node_data)
        normalized["resource_type"] = node_type
        
        nodes.append({
            "virtual": True,
            "key": node_data.get("key", "resource"),
            "data": normalized,
        })
    
    # Check actual objects in room
    for obj in room.contents:
        if is_resource_node(obj):
            data = get_resource_data(obj)
            node_type = data.get("resource_type") or data.get("type", "gather")
            if resource_type and node_type != resource_type:
                continue
            nodes.append({
                "virtual": False,
                "key": obj.key,
                "obj": obj,
                "data": data,
            })
    
    return nodes


def find_node_by_name(room, name, resource_type=None):
    """
    Find a specific resource node by name.
    
    Args:
        room: Room to search
        name: Node name to match (partial match)
        resource_type: Optional filter
    
    Returns:
        dict or None: Node info dict
    """
    nodes = find_nodes_in_room(room, resource_type)
    name_lower = name.lower()
    
    # Exact match first
    for node in nodes:
        if node["key"].lower() == name_lower:
            return node
    
    # Partial match
    for node in nodes:
        if name_lower in node["key"].lower():
            return node
    
    return None


def harvest_virtual_node(node_data, harvester):
    """
    Harvest from a virtual node (defined in room data, not an object).
    
    This handles the resource nodes defined in area content files.
    
    Args:
        node_data: The node definition dict
        harvester: Character harvesting
    
    Returns:
        dict: Harvest result
    """
    data = node_data
    # Content files use "type", resources.py uses "resource_type"
    resource_type = data.get("resource_type") or data.get("type", "gather")
    type_data = RESOURCE_TYPES.get(resource_type, RESOURCE_TYPES["gather"])
    
    # Check tool requirement
    tool_required = data.get("tool_required") or type_data.get("tool_required")
    if tool_required:
        has_tool = False
        for obj in harvester.contents:
            if (obj.tags.has(tool_required, category="tool_type") or 
                obj.key.lower() == tool_required.lower()):
                has_tool = True
                break
        
        if not has_tool:
            msg = type_data.get("tool_missing_msg", f"You need a {tool_required}.")
            return {"success": False, "message": msg}
    
    # Check cooldown for this specific node type
    cooldown_key = f"cooldown_{data.get('key', 'node')}".replace(" ", "_")
    cooldowns = harvester.db.resource_cooldowns or {}
    
    if cooldown_key in cooldowns:
        if time.time() < cooldowns[cooldown_key]:
            remaining = int(cooldowns[cooldown_key] - time.time())
            mins = remaining // 60
            secs = remaining % 60
            if mins > 0:
                time_str = f"{mins}m {secs}s"
            else:
                time_str = f"{secs}s"
            return {"success": False, "message": f"You must wait {time_str} before gathering here again."}
    
    # Show action message
    action_msg = type_data.get("action_msg", "You search...").format(
        node=data.get("key", "the area")
    )
    harvester.msg(action_msg)
    
    # Determine yield from harvest table
    # Content files use "yields", check both
    harvest_table = data.get("harvest_table") or data.get("yields", [])
    if not harvest_table:
        return {"success": False, "message": type_data.get("fail_msg", "You find nothing.")}
    
    # Apply luck modifier from effects
    luck_bonus = 0
    try:
        from world.effects import has_effect, get_effect
        if has_effect(harvester, "lucky"):
            luck_bonus = get_effect(harvester, "lucky").get("modifier", 5)
    except ImportError:
        pass
    
    # Weighted random selection
    # Higher weight = more likely
    total_weight = sum(entry.get("weight", 10) for entry in harvest_table)
    
    # Luck bonus shifts toward rarer items by reducing common weights
    roll = random.randint(1, max(1, total_weight - luck_bonus))
    
    cumulative = 0
    result_item = None
    for entry in harvest_table:
        cumulative += entry.get("weight", 10)
        if roll <= cumulative:
            result_item = entry
            break
    
    if not result_item:
        # Fallback to last item
        result_item = harvest_table[-1] if harvest_table else None
    
    if not result_item:
        return {"success": False, "message": type_data.get("fail_msg", "You find nothing.")}
    
    # Set cooldown
    cooldown_time = data.get("cooldown", 60)  # Default 60 seconds
    if not harvester.db.resource_cooldowns:
        harvester.db.resource_cooldowns = {}
    harvester.db.resource_cooldowns[cooldown_key] = time.time() + cooldown_time
    
    # Format result - content files use "key", harvest_table might use "item"
    item_name = result_item.get("key") or result_item.get("item", "something")
    rarity = result_item.get("rarity", "common")
    rarity_data = RARITY_TIERS.get(rarity, RARITY_TIERS["common"])
    
    item_display = f"{rarity_data['color']}{item_name}|n"
    
    success_msg = type_data.get("success_msg", "You find {item}!").format(
        item=item_display
    )
    
    # Create actual item object if template exists
    item_created = False
    try:
        from world.items import give_item, get_item_template
        
        # Try to find matching item template
        # Convert item name to template key (spaces to underscores, lowercase)
        template_key = item_name.lower().replace(" ", "_").replace("'", "")
        
        # Handle common name variations
        template_key_variations = [
            template_key,
            template_key.replace("_of_", "_"),
            template_key.replace("handful_of_", ""),
            template_key.replace("bundle_of_", ""),
            template_key.replace("piece_of_", ""),
            template_key.replace("lump_of_", ""),
            template_key.replace("strand_of_", ""),
            template_key.replace("jar_of_", ""),
            template_key.replace("loaf_of_", ""),
            template_key.replace("mug_of_", ""),
        ]
        
        template = None
        used_key = None
        for key in template_key_variations:
            template = get_item_template(key)
            if template:
                used_key = key
                break
        
        if template:
            # Map rarity to quality
            rarity_to_quality = {
                "common": "common",
                "uncommon": "uncommon",
                "rare": "rare",
                "epic": "epic",
                "legendary": "legendary",
                "junk": "poor",
            }
            quality = rarity_to_quality.get(rarity, "common")
            
            # Give the item
            item = give_item(harvester, used_key, quantity=1, quality=quality)
            if item:
                item_created = True
                # Update message to show it was added to inventory
                success_msg += " |x(Added to inventory)|n"
                
                # Check quest objectives
                try:
                    from world.quests import check_gather_objective
                    check_gather_objective(harvester, used_key, amount=1)
                except ImportError:
                    pass
    except ImportError:
        pass
    
    # Add to inventory as currency if value (fallback for items without templates)
    value = result_item.get("value", 0)
    if value > 0:
        try:
            from world.currency import receive
            receive(harvester, value, silent=True)
            success_msg += f" |y(+{value} gold)|n"
        except (ImportError, TypeError):
            pass
    
    # If no item was created and no value, at least note what they found
    if not item_created and value == 0:
        success_msg += " |x(No matching item template)|n"
    
    # Trigger scene chance
    scene_chance = data.get("scene_chance", 0)
    scene_pool = data.get("scene_pool", [])
    if scene_pool and random.randint(1, 100) <= scene_chance:
        scene_key = random.choice(scene_pool)
        try:
            from world.scenes import start_scene, get_scene
            scene = get_scene(scene_key)
            if scene:
                harvester.msg("\n|y--- Something happens! ---|n\n")
                start_scene(harvester, scene)
        except ImportError:
            pass
    
    return {
        "success": True,
        "message": success_msg,
        "item": item_name,
        "rarity": rarity,
        "value": value,
    }


# =============================================================================
# Base Gathering Command
# =============================================================================

class CmdGatherBase(Command):
    """
    Base class for all gathering commands.
    Subclasses set resource_type and customize messaging.
    """
    
    key = "gather"
    aliases = []
    locks = "cmd:all()"
    help_category = "Gathering"
    
    # Override in subclasses
    resource_type = None  # None = any type
    verb = "gather"
    verb_past = "gathered"
    no_nodes_msg = "There's nothing to gather here."
    
    def func(self):
        caller = self.caller
        room = caller.location
        
        if not room:
            caller.msg("You can't gather anything here.")
            return
        
        # Parse target
        target = self.args.strip().lower() if self.args else None
        
        # Find nodes
        if target:
            node = find_node_by_name(room, target, self.resource_type)
            if not node:
                # Try without type filter
                node = find_node_by_name(room, target)
                if node:
                    # Found but wrong type
                    caller.msg(f"You can't {self.verb} that. Try a different command.")
                else:
                    caller.msg(f"You don't see any '{target}' to {self.verb} here.")
                return
            nodes = [node]
        else:
            nodes = find_nodes_in_room(room, self.resource_type)
        
        if not nodes:
            caller.msg(self.no_nodes_msg)
            return
        
        # Take first available node
        node = nodes[0]
        
        # Harvest
        if node.get("virtual"):
            result = harvest_virtual_node(node["data"], caller)
        else:
            result = harvest(node["obj"], caller)
        
        # Display result
        caller.msg(result["message"])
        
        # Announce to room on success
        if result.get("success"):
            room.msg_contents(
                f"|c{caller.key}|n {self.verb_past} something from {node['key']}.",
                exclude=[caller]
            )


# =============================================================================
# Specific Gathering Commands
# =============================================================================

class CmdForage(CmdGatherBase):
    """
    Forage for plants, herbs, mushrooms, and other natural items.
    
    Usage:
        forage                  - Forage from first available spot
        forage <target>         - Forage from specific source
    
    Examples:
        forage
        forage mushrooms
        forage berry bush
    
    Foraging doesn't require tools and can find:
    - Herbs and plants
    - Berries and fruits
    - Mushrooms
    - Flowers
    - Seeds
    """
    
    key = "forage"
    aliases = ["scavenge"]
    resource_type = "forage"
    verb = "forage"
    verb_past = "foraged"
    no_nodes_msg = "There's nothing to forage here. Try a forest or meadow."


class CmdFish(CmdGatherBase):
    """
    Fish in bodies of water.
    
    Usage:
        fish                    - Fish at first available spot
        fish <target>           - Fish at specific spot
    
    Examples:
        fish
        fish deep pool
        fish river
    
    Fishing requires a fishing rod and can catch:
    - Various fish species
    - Shellfish
    - Treasure (rarely)
    - Junk items
    """
    
    key = "fish"
    aliases = ["angle"]
    resource_type = "fishing"
    verb = "fish"
    verb_past = "fished"
    no_nodes_msg = "There's nowhere to fish here. Find water!"


class CmdMine(CmdGatherBase):
    """
    Mine ore, gems, and stone from rock formations.
    
    Usage:
        mine                    - Mine at first available vein
        mine <target>           - Mine specific vein
    
    Examples:
        mine
        mine copper vein
        mine crystal
    
    Mining requires a pickaxe and can yield:
    - Ores (copper, iron, silver, gold)
    - Gems (quartz, ruby, emerald, diamond)
    - Stone and clay
    - Fossils (rarely)
    """
    
    key = "mine"
    aliases = ["dig"]
    resource_type = "mining"
    verb = "mine"
    verb_past = "mined"
    no_nodes_msg = "There's nothing to mine here. Find a cave or quarry."


class CmdCatch(CmdGatherBase):
    """
    Catch bugs, crabs, and small creatures.
    
    Usage:
        catch                   - Catch from first available spot
        catch <target>          - Catch from specific spot
    
    Examples:
        catch
        catch butterflies
        catch tidepools
    
    Catching usually requires a net and can snag:
    - Butterflies and moths
    - Beetles and bugs
    - Crabs and shellfish
    - Small creatures
    """
    
    key = "catch"
    aliases = ["snag", "net"]
    resource_type = "bugs"
    verb = "catch"
    verb_past = "caught"
    no_nodes_msg = "There's nothing to catch here. Try a meadow or beach."


class CmdGather(CmdGatherBase):
    """
    General gathering - works on any resource type.
    
    Usage:
        gather                  - Gather from first available node
        gather <target>         - Gather from specific source
    
    Examples:
        gather
        gather shells
        gather herbs
    
    Gather is a universal command that works with any resource.
    For best results, use the specific command (forage, fish, mine, catch).
    """
    
    key = "gather"
    aliases = ["harvest", "collect"]
    resource_type = None  # Any type
    verb = "gather"
    verb_past = "gathered"
    no_nodes_msg = "There's nothing to gather here."


# =============================================================================
# Search Command (Special)
# =============================================================================

class CmdSearch(Command):
    """
    Search the area for hidden items, secrets, and treasures.
    
    Usage:
        search                  - Search the room
        search <target>         - Search specific thing
    
    Examples:
        search
        search bushes
        search under rocks
    
    Searching can reveal:
    - Hidden items
    - Secret passages
    - Buried treasure
    - Clues and lore
    
    Some areas have better search results than others.
    Searching has a cooldown to prevent spam.
    """
    
    key = "search"
    aliases = ["look around", "examine area"]
    locks = "cmd:all()"
    help_category = "Gathering"
    
    def func(self):
        caller = self.caller
        room = caller.location
        
        if not room:
            caller.msg("There's nothing to search here.")
            return
        
        # Check cooldown (30 seconds)
        cooldown_key = f"search_{room.id}"
        cooldowns = caller.db.resource_cooldowns or {}
        
        if cooldown_key in cooldowns:
            if time.time() < cooldowns[cooldown_key]:
                remaining = int(cooldowns[cooldown_key] - time.time())
                caller.msg(f"You've already searched here recently. Wait {remaining}s.")
                return
        
        # Set cooldown
        if not caller.db.resource_cooldowns:
            caller.db.resource_cooldowns = {}
        caller.db.resource_cooldowns[cooldown_key] = time.time() + 30
        
        caller.msg("You search the area carefully...")
        
        # Check room for search results
        search_data = room.db.search_results or []
        
        if not search_data:
            # Generic failure
            failures = [
                "You don't find anything unusual.",
                "Your search turns up nothing of interest.",
                "Nothing catches your eye.",
                "The area seems thoroughly ordinary.",
                "You find only dirt and disappointment.",
            ]
            caller.msg(random.choice(failures))
            room.msg_contents(
                f"|c{caller.key}|n searches the area but finds nothing.",
                exclude=[caller]
            )
            return
        
        # Roll for discovery
        luck_bonus = 0
        try:
            from world.effects import has_effect, get_effect
            if has_effect(caller, "lucky"):
                luck_bonus = get_effect(caller, "lucky").get("modifier", 5)
            if has_effect(caller, "keen_eye"):
                luck_bonus += 10
        except ImportError:
            pass
        
        roll = random.randint(1, 100) + luck_bonus
        
        result = None
        for entry in search_data:
            if roll <= entry.get("chance", 20):
                result = entry
                break
        
        if not result:
            caller.msg("You search thoroughly but find nothing of interest.")
            return
        
        # Display find
        item = result.get("item", "something")
        desc = result.get("description", f"You find {item}!")
        
        rarity = result.get("rarity", "common")
        rarity_data = RARITY_TIERS.get(rarity, RARITY_TIERS["common"])
        
        caller.msg(f"{rarity_data['color']}{desc}|n")
        
        # Award value if any
        value = result.get("value", 0)
        if value > 0:
            try:
                from world.currency import receive
                receive(caller, value, silent=True)
                caller.msg(f"|y(+{value} gold)|n")
            except (ImportError, TypeError):
                pass
        
        # Trigger scene if defined
        scene_key = result.get("trigger_scene")
        if scene_key:
            try:
                from world.scenes import start_scene, get_scene
                scene = get_scene(scene_key)
                if scene:
                    caller.msg("\n|y--- Something happens! ---|n\n")
                    start_scene(caller, scene)
            except ImportError:
                pass
        
        room.msg_contents(
            f"|c{caller.key}|n found something while searching!",
            exclude=[caller]
        )


# =============================================================================
# Resources List Command
# =============================================================================

class CmdResources(Command):
    """
    List all gatherable resources in the current room.
    
    Usage:
        resources               - Show all resource nodes
        resources <type>        - Filter by type (forage, fish, mine, catch)
    
    Examples:
        resources
        resources fish
        resources mine
    """
    
    key = "resources"
    aliases = ["nodes", "gathering"]
    locks = "cmd:all()"
    help_category = "Gathering"
    
    def func(self):
        caller = self.caller
        room = caller.location
        
        if not room:
            caller.msg("You're not in a location.")
            return
        
        # Parse filter
        filter_type = self.args.strip().lower() if self.args else None
        
        # Map aliases to resource types
        type_aliases = {
            "forage": "forage",
            "foraging": "forage",
            "fish": "fishing",
            "fishing": "fishing",
            "mine": "mining",
            "mining": "mining",
            "catch": "bugs",
            "bugs": "bugs",
            "bug": "bugs",
        }
        
        if filter_type:
            filter_type = type_aliases.get(filter_type, filter_type)
        
        nodes = find_nodes_in_room(room, filter_type)
        
        if not nodes:
            if filter_type:
                caller.msg(f"No {filter_type} resources here.")
            else:
                caller.msg("There are no gatherable resources in this area.")
            return
        
        # Build display
        lines = ["|wGatherable Resources:|n"]
        lines.append("-" * 40)
        
        type_icons = {
            "forage": "|g[F]|n",
            "fishing": "|c[W]|n",
            "mining": "|y[M]|n",
            "bugs": "|m[B]|n",
            "gather": "|w[G]|n",
            "logging": "|r[L]|n",
        }
        
        for node in nodes:
            data = node["data"]
            rtype = data.get("resource_type") or data.get("type", "gather")
            icon = type_icons.get(rtype, "|w[?]|n")
            
            # Check availability
            if node.get("virtual"):
                # Check cooldown
                cooldown_key = f"cooldown_{data.get('key', 'node')}".replace(" ", "_")
                cooldowns = caller.db.resource_cooldowns or {}
                
                if cooldown_key in cooldowns and time.time() < cooldowns[cooldown_key]:
                    remaining = int(cooldowns[cooldown_key] - time.time())
                    status = f"|x(wait {remaining}s)|n"
                else:
                    status = "|g(ready)|n"
            else:
                available, reason = is_available(node["obj"], caller)
                if available:
                    status = "|g(ready)|n"
                else:
                    short_reason = reason[:12] + "..." if len(reason) > 15 else reason
                    status = f"|x({short_reason})|n"
            
            # Tool indicator
            tool = data.get("tool_required")
            type_tool = RESOURCE_TYPES.get(rtype, {}).get("tool_required")
            tool = tool or type_tool
            
            if tool:
                tool_str = f" |x[{tool}]|n"
            else:
                tool_str = ""
            
            lines.append(f"  {icon} {node['key']}{tool_str} {status}")
        
        lines.append("-" * 40)
        lines.append("|xCommands: forage, fish, mine, catch, gather, search|n")
        
        caller.msg("\n".join(lines))


# =============================================================================
# Command Set
# =============================================================================

class GatheringCmdSet(CmdSet):
    """
    Command set containing all gathering commands.
    
    Add to character with:
        character.cmdset.add("commands.gathering_commands.GatheringCmdSet", persistent=True)
    """
    
    key = "gathering"
    priority = 1
    
    def at_cmdset_creation(self):
        self.add(CmdForage())
        self.add(CmdFish())
        self.add(CmdMine())
        self.add(CmdCatch())
        self.add(CmdGather())
        self.add(CmdSearch())
        self.add(CmdResources())
