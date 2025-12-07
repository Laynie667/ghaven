"""
Resource Nodes System for Gilderhaven
======================================

Gatherable resource nodes that respawn, require tools, and yield items.
Used for fishing spots, foraging plants, ore veins, bug catching, etc.

Resource nodes are Objects that:
- Can be interacted with to yield resources
- Deplete after harvesting
- Respawn after a time period
- May require specific tools
- May have quality/rarity tiers
- May have seasonal availability
- Track who harvested them (for respawn per-player or global)

Usage:
    # Create a resource node in-game
    @py from world.resources import create_resource_node
    @py create_resource_node(here, "apple_tree", yields=["apple", "apple", "worm"])
    
    # Player interaction (via 'gather', 'fish', 'forage', etc. commands)
    gather apple tree
"""

import random
import time
from evennia import create_object
from evennia.utils import logger

# =============================================================================
# Resource Type Definitions
# =============================================================================

RESOURCE_TYPES = {
    # Foraging
    "forage": {
        "verb": "forage",
        "verb_past": "foraged",
        "tool_required": None,  # No tool needed
        "skill": "foraging",    # STUB: skill system
        "action_msg": "You search through the {node}...",
        "success_msg": "You find {item}!",
        "fail_msg": "You don't find anything useful.",
        "depleted_msg": "There's nothing left to forage here.",
    },
    
    # Fishing
    "fishing": {
        "verb": "fish",
        "verb_past": "fished",
        "tool_required": "fishing_rod",
        "tool_missing_msg": "You need a fishing rod to fish here.",
        "skill": "fishing",
        "action_msg": "You cast your line into {node}...",
        "success_msg": "You caught {item}!",
        "fail_msg": "The fish aren't biting.",
        "depleted_msg": "This fishing spot needs time to recover.",
    },
    
    # Mining
    "mining": {
        "verb": "mine",
        "verb_past": "mined",
        "tool_required": "pickaxe",
        "tool_missing_msg": "You need a pickaxe to mine here.",
        "skill": "mining",
        "action_msg": "You swing your pickaxe at {node}...",
        "success_msg": "You extract {item}!",
        "fail_msg": "You chip away but find nothing valuable.",
        "depleted_msg": "This vein is exhausted.",
    },
    
    # Bug catching
    "bugs": {
        "verb": "catch",
        "verb_past": "caught",
        "tool_required": "net",
        "tool_missing_msg": "You need a net to catch bugs.",
        "skill": "bug_catching",
        "action_msg": "You swing your net at {node}...",
        "success_msg": "You caught {item}!",
        "fail_msg": "The bugs evade your net.",
        "depleted_msg": "The bugs have scattered.",
    },
    
    # Logging
    "logging": {
        "verb": "chop",
        "verb_past": "chopped",
        "tool_required": "axe",
        "tool_missing_msg": "You need an axe to chop wood.",
        "skill": "logging",
        "action_msg": "You swing your axe at {node}...",
        "success_msg": "You harvest {item}!",
        "fail_msg": "Your axe glances off the bark.",
        "depleted_msg": "This tree needs time to recover.",
    },
    
    # Generic gathering (herbs, shells, etc.)
    "gather": {
        "verb": "gather",
        "verb_past": "gathered",
        "tool_required": None,
        "skill": "gathering",
        "action_msg": "You reach for {node}...",
        "success_msg": "You collect {item}!",
        "fail_msg": "You come up empty-handed.",
        "depleted_msg": "There's nothing left to gather.",
    },
}


# Rarity tiers and their probabilities/multipliers
RARITY_TIERS = {
    "common": {"weight": 70, "color": "|w", "value_mult": 1.0},
    "uncommon": {"weight": 20, "color": "|g", "value_mult": 1.5},
    "rare": {"weight": 8, "color": "|c", "value_mult": 3.0},
    "epic": {"weight": 1.8, "color": "|m", "value_mult": 10.0},
    "legendary": {"weight": 0.2, "color": "|y", "value_mult": 50.0},
}


# Seasons affect availability
SEASONS = ["spring", "summer", "autumn", "winter"]


# =============================================================================
# Resource Node Data Structure
# =============================================================================

def create_node_data(
    resource_type,
    yields,
    max_harvests=3,
    respawn_time=300,
    tool_required=None,
    skill_required=None,
    min_skill_level=0,
    seasons=None,
    time_available=None,
    quality_range=(1, 10),
    per_player=False,
    rarity_weights=None,
):
    """
    Create resource node data dict.
    
    Args:
        resource_type: Key from RESOURCE_TYPES
        yields: List of possible yields (item keys or yield dicts)
        max_harvests: Times can be harvested before depletion
        respawn_time: Seconds until respawn after depletion
        tool_required: Tool key needed (overrides type default)
        skill_required: Skill key needed (overrides type default)
        min_skill_level: Minimum skill level to harvest
        seasons: List of seasons when available (None = all)
        time_available: List of time periods when available (None = all)
        quality_range: Tuple of (min, max) quality
        per_player: If True, tracks harvests per-player
        rarity_weights: Custom rarity weights dict
    
    Returns:
        dict: Node data to store on object
    """
    type_data = RESOURCE_TYPES.get(resource_type, RESOURCE_TYPES["gather"])
    
    return {
        "resource_type": resource_type,
        "yields": yields,
        "max_harvests": max_harvests,
        "current_harvests": max_harvests,
        "respawn_time": respawn_time,
        "depleted_at": None,
        "tool_required": tool_required or type_data.get("tool_required"),
        "skill_required": skill_required or type_data.get("skill"),
        "min_skill_level": min_skill_level,
        "seasons": seasons,  # None = all seasons
        "time_available": time_available,  # None = all times
        "quality_range": quality_range,
        "per_player": per_player,
        "player_harvests": {},  # {player_id: harvests_remaining}
        "player_cooldowns": {},  # {player_id: cooldown_until}
        "rarity_weights": rarity_weights,
    }


# =============================================================================
# Resource Node Typeclass
# =============================================================================

# STUB: This would be the actual typeclass. For now, we use functions
# that operate on any object with .db.resource_node data.

"""
class ResourceNode(Object):
    '''
    A gatherable resource node.
    '''
    
    def at_object_creation(self):
        super().at_object_creation()
        # Initialize from prototype or defaults
        if not self.db.resource_node:
            self.db.resource_node = create_node_data("gather", ["nothing"])
    
    def get_display_name(self, looker, **kwargs):
        name = super().get_display_name(looker, **kwargs)
        if is_depleted(self, looker):
            return f"|x{name} (depleted)|n"
        return name
"""


# =============================================================================
# Core Functions
# =============================================================================

def setup_resource_node(obj, resource_type, yields, **kwargs):
    """
    Set up an existing object as a resource node.
    
    Args:
        obj: Object to convert to resource node
        resource_type: Type from RESOURCE_TYPES
        yields: List of possible yields
        **kwargs: Additional create_node_data arguments
    """
    obj.db.resource_node = create_node_data(resource_type, yields, **kwargs)
    obj.tags.add("resource_node", category="object_type")
    return obj


def create_resource_node(location, key, resource_type="gather", yields=None, 
                        typeclass="typeclasses.objects.Object", **kwargs):
    """
    Create a new resource node object.
    
    Args:
        location: Where to create the node
        key: Object key/name
        resource_type: Type from RESOURCE_TYPES
        yields: List of possible yields
        typeclass: Typeclass to use
        **kwargs: Additional node data arguments
    
    Returns:
        Object: The created resource node
    """
    yields = yields or ["nothing"]
    
    obj = create_object(typeclass, key=key, location=location)
    setup_resource_node(obj, resource_type, yields, **kwargs)
    
    return obj


def is_resource_node(obj):
    """Check if object is a resource node."""
    return obj.db.resource_node is not None


def get_resource_data(node):
    """
    Get the resource data dict for a node.
    
    Args:
        node: The resource node object
        
    Returns:
        dict or None
    """
    return node.db.resource_node


def is_depleted(node, harvester=None):
    """
    Check if resource node is depleted.
    
    Args:
        node: Resource node object
        harvester: Optional - check per-player depletion
    
    Returns:
        bool: True if depleted
    """
    data = node.db.resource_node
    if not data:
        return True
    
    if data.get("per_player") and harvester:
        player_id = harvester.id
        remaining = data.get("player_harvests", {}).get(player_id)
        if remaining is not None:
            return remaining <= 0
        # Not yet harvested by this player
        return False
    
    return data.get("current_harvests", 0) <= 0


def is_available(node, harvester=None):
    """
    Check if resource node is currently available.
    Considers season, time of day, and depletion.
    
    Returns:
        tuple: (bool available, str reason if not available)
    """
    data = node.db.resource_node
    if not data:
        return False, "This isn't a resource node."
    
    # Check depletion
    if is_depleted(node, harvester):
        return False, _get_depleted_message(data)
    
    # Check per-player cooldown
    if data.get("per_player") and harvester:
        player_id = harvester.id
        cooldown_until = data.get("player_cooldowns", {}).get(player_id, 0)
        if time.time() < cooldown_until:
            remaining = int(cooldown_until - time.time())
            return False, f"You must wait {remaining} seconds before harvesting again."
    
    # Check season
    seasons = data.get("seasons")
    if seasons:
        try:
            from world.world_state import get_season
            current_season = get_season()
            if current_season not in seasons:
                return False, f"This can only be harvested in {', '.join(seasons)}."
        except ImportError:
            pass  # World state not available, skip check
    
    # Check time of day
    time_available = data.get("time_available")
    if time_available:
        try:
            from world.world_state import get_time_period
            current_time = get_time_period()
            if current_time not in time_available:
                return False, f"This can only be harvested during {', '.join(time_available)}."
        except ImportError:
            pass
    
    return True, None


def has_required_tool(harvester, node):
    """
    Check if harvester has the required tool.
    
    Returns:
        tuple: (bool has_tool, Object tool or None, str message if missing)
    """
    data = node.db.resource_node
    if not data:
        return False, None, "Invalid node."
    
    tool_key = data.get("tool_required")
    if not tool_key:
        return True, None, None  # No tool required
    
    # Search harvester's inventory
    for obj in harvester.contents:
        if obj.tags.has(tool_key, category="tool_type") or obj.key.lower() == tool_key.lower():
            return True, obj, None
    
    # Get tool missing message
    type_data = RESOURCE_TYPES.get(data.get("resource_type", "gather"), {})
    msg = type_data.get("tool_missing_msg", f"You need a {tool_key} to harvest this.")
    
    return False, None, msg


def harvest(node, harvester, tool=None):
    """
    Attempt to harvest from a resource node.
    
    Args:
        node: Resource node object
        harvester: Character harvesting
        tool: Tool being used (optional, will auto-detect)
    
    Returns:
        dict: {
            "success": bool,
            "message": str,
            "yield": Object or None,
            "quality": int or None,
            "rarity": str or None,
        }
    """
    data = node.db.resource_node
    if not data:
        return {"success": False, "message": "This isn't harvestable."}
    
    type_data = RESOURCE_TYPES.get(data.get("resource_type", "gather"), RESOURCE_TYPES["gather"])
    
    # Check availability
    available, reason = is_available(node, harvester)
    if not available:
        return {"success": False, "message": reason}
    
    # Check tool
    has_tool, found_tool, tool_msg = has_required_tool(harvester, node)
    if not has_tool:
        return {"success": False, "message": tool_msg}
    tool = tool or found_tool
    
    # STUB: Check skill level
    # skill_key = data.get("skill_required")
    # min_level = data.get("min_skill_level", 0)
    # if skill_key and get_skill_level(harvester, skill_key) < min_level:
    #     return {"success": False, "message": f"You need {skill_key} level {min_level}."}
    
    # Show action message
    action_msg = type_data.get("action_msg", "You attempt to harvest...").format(
        node=node.key
    )
    harvester.msg(action_msg)
    
    # Determine success (STUB: factor in skill)
    # For now, always succeed if available
    success = True
    
    if not success:
        fail_msg = type_data.get("fail_msg", "You fail to harvest anything.")
        return {"success": False, "message": fail_msg}
    
    # Determine yield
    yield_result = _determine_yield(data)
    
    if not yield_result:
        fail_msg = type_data.get("fail_msg", "You don't find anything.")
        _consume_harvest(node, harvester, data)
        return {"success": False, "message": fail_msg}
    
    # Create the yielded item
    item = _create_yield_item(yield_result, harvester, data)
    
    # Consume harvest
    _consume_harvest(node, harvester, data)
    
    # Build success message
    rarity = yield_result.get("rarity", "common")
    rarity_data = RARITY_TIERS.get(rarity, RARITY_TIERS["common"])
    item_display = f"{rarity_data['color']}{item.key}|n"
    
    success_msg = type_data.get("success_msg", "You harvest {item}!").format(
        item=item_display
    )
    
    return {
        "success": True,
        "message": success_msg,
        "yield": item,
        "quality": yield_result.get("quality"),
        "rarity": rarity,
    }


def respawn_node(node):
    """
    Respawn a depleted resource node.
    
    Called by respawn script or manually.
    """
    data = node.db.resource_node
    if not data:
        return
    
    data["current_harvests"] = data.get("max_harvests", 3)
    data["depleted_at"] = None
    data["player_harvests"] = {}
    
    # Announce respawn if in a room
    if node.location:
        node.location.msg_contents(
            f"|g{node.key} has replenished.|n",
            exclude=[]
        )


# =============================================================================
# Internal Helpers
# =============================================================================

def _get_depleted_message(data):
    """Get depleted message for resource type."""
    type_data = RESOURCE_TYPES.get(data.get("resource_type", "gather"), {})
    return type_data.get("depleted_msg", "This resource is depleted.")


def _determine_yield(data):
    """
    Determine what gets yielded from harvest.
    
    Returns:
        dict: Yield result or None
    """
    yields = data.get("yields", [])
    if not yields:
        return None
    
    # Yields can be:
    # - Simple string: item key
    # - Dict: {"key": "item", "rarity": "common", "weight": 10, "typeclass": "..."}
    
    # Build weighted list
    weighted = []
    for y in yields:
        if isinstance(y, str):
            weighted.append({"key": y, "rarity": "common", "weight": 10})
        elif isinstance(y, dict):
            weight = y.get("weight", 10)
            # Apply rarity weight
            rarity = y.get("rarity", "common")
            rarity_weight = RARITY_TIERS.get(rarity, {}).get("weight", 50)
            weighted.append({**y, "weight": weight * (rarity_weight / 50)})
    
    if not weighted:
        return None
    
    # Weighted random selection
    total_weight = sum(y["weight"] for y in weighted)
    roll = random.random() * total_weight
    
    cumulative = 0
    for y in weighted:
        cumulative += y["weight"]
        if roll <= cumulative:
            # Determine quality
            quality_range = data.get("quality_range", (1, 10))
            quality = random.randint(quality_range[0], quality_range[1])
            
            return {
                "key": y.get("key", "item"),
                "rarity": y.get("rarity", "common"),
                "quality": quality,
                "typeclass": y.get("typeclass"),
                "attributes": y.get("attributes", {}),
            }
    
    return weighted[0] if weighted else None


def _create_yield_item(yield_result, harvester, node_data):
    """
    Create the yielded item object.
    
    Args:
        yield_result: Dict from _determine_yield
        harvester: Who harvested
        node_data: Resource node data
    
    Returns:
        Object: Created item
    """
    typeclass = yield_result.get("typeclass", "typeclasses.objects.Object")
    key = yield_result.get("key", "item")
    
    item = create_object(typeclass, key=key, location=harvester)
    
    # Set attributes
    item.db.quality = yield_result.get("quality", 5)
    item.db.rarity = yield_result.get("rarity", "common")
    item.db.harvested_by = harvester.key
    item.db.harvested_at = time.time()
    
    # Set resource type tag
    resource_type = node_data.get("resource_type", "gather")
    item.tags.add(resource_type, category="resource_source")
    
    # Apply any custom attributes
    for attr, value in yield_result.get("attributes", {}).items():
        setattr(item.db, attr, value)
    
    return item


def _consume_harvest(node, harvester, data):
    """Reduce remaining harvests, set depletion if needed."""
    if data.get("per_player"):
        player_id = harvester.id
        
        # Initialize if needed
        if player_id not in data.get("player_harvests", {}):
            if "player_harvests" not in data:
                data["player_harvests"] = {}
            data["player_harvests"][player_id] = data.get("max_harvests", 3)
        
        data["player_harvests"][player_id] -= 1
        
        # Set per-player respawn cooldown
        if data["player_harvests"][player_id] <= 0:
            if "player_cooldowns" not in data:
                data["player_cooldowns"] = {}
            data["player_cooldowns"][player_id] = time.time() + data.get("respawn_time", 300)
    else:
        # Global depletion
        data["current_harvests"] = data.get("current_harvests", 1) - 1
        
        if data["current_harvests"] <= 0:
            data["depleted_at"] = time.time()
            
            # STUB: Start respawn timer script
            # RespawnScript.create(node, data.get("respawn_time", 300))


# =============================================================================
# Predefined Resource Templates
# =============================================================================

def create_apple_tree(location, **kwargs):
    """Create an apple tree forage node."""
    return create_resource_node(
        location, 
        "apple tree",
        resource_type="forage",
        yields=[
            {"key": "apple", "rarity": "common", "weight": 80},
            {"key": "golden apple", "rarity": "rare", "weight": 5},
            {"key": "worm", "rarity": "uncommon", "weight": 15},
        ],
        max_harvests=5,
        respawn_time=600,
        seasons=["summer", "autumn"],
        **kwargs
    )


def create_fishing_spot(location, name="fishing spot", **kwargs):
    """Create a fishing spot."""
    return create_resource_node(
        location,
        name,
        resource_type="fishing",
        yields=[
            {"key": "small fish", "rarity": "common", "weight": 50},
            {"key": "medium fish", "rarity": "uncommon", "weight": 30},
            {"key": "large fish", "rarity": "rare", "weight": 15},
            {"key": "boot", "rarity": "common", "weight": 5},
        ],
        max_harvests=10,
        respawn_time=900,
        per_player=True,
        **kwargs
    )


def create_ore_vein(location, ore_type="iron", **kwargs):
    """Create a mining ore vein."""
    yields = {
        "iron": [
            {"key": "iron ore", "rarity": "common", "weight": 70},
            {"key": "iron chunk", "rarity": "uncommon", "weight": 25},
            {"key": "ruby", "rarity": "rare", "weight": 5},
        ],
        "copper": [
            {"key": "copper ore", "rarity": "common", "weight": 75},
            {"key": "copper chunk", "rarity": "uncommon", "weight": 20},
            {"key": "emerald", "rarity": "rare", "weight": 5},
        ],
        "gold": [
            {"key": "gold ore", "rarity": "uncommon", "weight": 60},
            {"key": "gold nugget", "rarity": "rare", "weight": 30},
            {"key": "diamond", "rarity": "epic", "weight": 10},
        ],
    }
    
    return create_resource_node(
        location,
        f"{ore_type} vein",
        resource_type="mining",
        yields=yields.get(ore_type, yields["iron"]),
        max_harvests=8,
        respawn_time=1800,  # 30 minutes
        **kwargs
    )


def create_herb_patch(location, herb_type="healing herb", **kwargs):
    """Create a foraging herb patch."""
    return create_resource_node(
        location,
        herb_type,
        resource_type="forage",
        yields=[
            {"key": herb_type, "rarity": "common", "weight": 80},
            {"key": f"rare {herb_type}", "rarity": "rare", "weight": 15},
            {"key": "seeds", "rarity": "uncommon", "weight": 5},
        ],
        max_harvests=3,
        respawn_time=1200,  # 20 minutes
        **kwargs
    )


def create_bug_spot(location, name="flower patch", **kwargs):
    """Create a bug catching spot."""
    return create_resource_node(
        location,
        name,
        resource_type="bugs",
        yields=[
            {"key": "common butterfly", "rarity": "common", "weight": 40},
            {"key": "bee", "rarity": "common", "weight": 30},
            {"key": "dragonfly", "rarity": "uncommon", "weight": 20},
            {"key": "golden beetle", "rarity": "rare", "weight": 8},
            {"key": "rainbow moth", "rarity": "epic", "weight": 2},
        ],
        max_harvests=5,
        respawn_time=600,
        time_available=["morning", "day", "evening"],  # Not at night
        per_player=True,
        **kwargs
    )
