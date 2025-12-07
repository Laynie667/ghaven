"""
Gilderhaven World Systems
=========================

Core gameplay systems that operate independently of Character.py.
These systems use .db attributes and tags, working on any object.

Systems:
- currency: Money management
- effects: Statuses, transformations, curses
- triggers: Event trigger framework
- resources: Gatherable resource nodes
- random_events: Ambient and world events
- traps: Hazards, curses, defensive mechanisms
- scenes: Branching narrative interactions
- housing: Player homes and permissions
- furniture: Interactive furniture with slots
- positions: Character interaction positions
- npcs: NPC framework with dialogue trees
- items: Item system with tools, consumables, equipment
- shops: Buy/sell interface with shopkeeper NPCs
- body: Body parts, species, modifiers, shortcodes

Usage:
    from world.currency import balance, pay, receive
    from world.effects import apply_effect, has_effect, remove_effect
    from world.triggers import add_trigger, check_room_triggers
    from world.resources import create_resource_node, harvest
    from world.random_events import fire_ambient_event, tick_random_events
    from world.traps import create_cursed_item, check_trap
    from world.furniture import create_furniture, use_furniture, is_furniture
    from world.positions import set_position, clear_position, get_position_display
    from world.npcs import create_npc, start_dialogue, is_npc
    from world.items import create_item, give_item, has_tool, use_item
    from world.shops import setup_shop, open_shop, buy_item, sell_item
    from world.body import apply_species, add_part, mark, process_shortcodes
"""

# Currency
from .currency import (
    balance,
    pay,
    receive,
    transfer,
    can_afford,
    initialize_currency,
    format_balance,
    format_price,
    CURRENCY_NAME,
    CURRENCY_PLURAL,
)

# Effects
from .effects import (
    apply_effect,
    remove_effect,
    has_effect,
    get_effects,
    get_effect_data,
    clear_all_effects,
    is_transformed,
    is_cursed,
    apply_transformation,
    revert_transformation,
    can_perform,
    # Convenience functions
    poison,
    paralyze,
    induce_heat,
    curse,
    mark_displayed,
    enter_breeding_program,
)

# Triggers
from .triggers import (
    add_trigger,
    remove_trigger,
    check_room_triggers,
    check_object_triggers,
    check_and_fire_triggers,
    # Templates
    add_entry_message_trigger,
    add_first_visit_trigger,
    add_pickup_curse_trigger,
    add_trap_trigger,
)

# Resources
from .resources import (
    create_resource_node,
    setup_resource_node,
    harvest,
    is_resource_node,
    is_depleted,
    respawn_node,
    # Templates
    create_apple_tree,
    create_fishing_spot,
    create_ore_vein,
    create_herb_patch,
    create_bug_spot,
)

# Random Events
from .random_events import (
    fire_ambient_event,
    fire_room_event,
    fire_personal_event,
    fire_world_event,
    tick_random_events,
    register_ambient_events,
    register_room_events,
)

# Traps
from .traps import (
    create_cursed_item,
    create_hazardous_plant,
    create_defensive_creature,
    create_trapped_container,
    setup_hazard_room,
    check_trap,
    check_room_hazard,
    attempt_curse_removal,
)

# Scenes (branching narratives)
from .scenes import (
    start_scene,
    advance_scene,
    end_scene,
    get_active_scene,
    is_in_scene,
    register_scene,
    get_scene,
    get_scenes_by_tag,
    trigger_scene,
    # Builders
    simple_scene,
    confirm_scene,
    linear_scene,
)

# Load example scenes (registers them)
from . import scenes_examples

# Housing
from .housing import (
    get_home,
    has_home,
    create_home,
    upgrade_home,
    add_room,
    purchase_upgrade,
    get_all_home_rooms,
    get_home_type,
    get_permission_level,
    can_enter,
    set_permission,
    invite_visitor,
    revoke_visitor,
    kick_from_home,
    set_home_name,
    set_room_description,
    lock_home,
    get_home_info,
    get_permission_list,
    list_available_homes,
    list_available_rooms,
    list_available_upgrades,
    HOME_TYPES,
    ROOM_TYPES,
    UPGRADES,
    PERMISSION_LEVELS,
)

# Furniture
from .furniture import (
    FURNITURE_CATALOG,
    FURNITURE_CATEGORIES,
    get_catalog_item,
    list_catalog,
    create_furniture,
    purchase_furniture,
    place_furniture,
    remove_furniture,
    use_furniture,
    leave_furniture,
    get_occupants,
    get_available_slots,
    is_furniture,
    is_bondage_furniture,
    is_adult_furniture,
    get_furniture_display,
    get_furniture_for_room,
)

# Positions
from .positions import (
    POSITIONS,
    POSITION_CATEGORIES,
    get_position,
    get_position_type,
    get_position_info,
    is_standing,
    is_mobile,
    can_move,
    has_flag,
    is_restrained,
    is_exposed,
    set_position,
    clear_position,
    force_clear_position,
    get_position_display,
    get_position_for_room,
    get_partner,
    get_partners,
    add_partner,
    remove_partner,
    get_furniture as get_character_furniture,
    get_furniture_slot,
    list_positions,
    get_positions_for_furniture,
)

# NPCs
from .npcs import (
    NPC_TEMPLATES,
    DIALOGUE_TREES,
    create_npc,
    setup_npc,
    is_npc,
    get_npc_data,
    get_npc_memory,
    set_npc_memory,
    has_npc_flag,
    set_npc_flag,
    clear_npc_flag,
    get_dialogue_node,
    start_dialogue,
    process_dialogue_choice,
    end_dialogue,
    is_in_dialogue,
    npc_ambient_action,
    npc_react_to,
    get_scheduled_location,
    move_npc_to_schedule,
)

# Items
from .items import (
    ITEM_TEMPLATES,
    ITEM_CATEGORIES,
    ITEM_QUALITIES,
    EQUIPMENT_SLOTS,
    get_item_template,
    list_templates,
    create_item,
    is_item,
    get_item_data,
    get_item_category,
    get_item_quantity,
    set_item_quantity,
    add_to_stack,
    remove_from_stack,
    get_item_value,
    get_item_display_name,
    is_tool,
    get_tool_type,
    get_tool_tier,
    get_tool_bonus,
    has_tool,
    get_best_tool,
    damage_tool,
    repair_tool,
    is_consumable,
    use_item,
    is_equipment,
    get_equipment_slot,
    equip_item,
    unequip_item,
    get_equipped,
    get_all_equipped,
    find_item_in_inventory,
    count_items,
    give_item,
    take_item,
)

# Shops
from .shops import (
    SHOP_TYPES,
    SHOP_INVENTORIES,
    SHOPKEEPER_TEMPLATES,
    setup_shop,
    is_shop,
    get_shop_data,
    get_shop_stock,
    get_buy_price,
    get_sell_price,
    open_shop,
    close_shop,
    get_current_shop,
    buy_item,
    sell_item,
    restock_shop,
    restock_all_shops,
)

# Body System
from .body import (
    SPECIES_TEMPLATES,
    GENITAL_MECHANICS,
    MODIFIER_TYPES,
    # Part management
    get_body_parts,
    get_body_states,
    has_part,
    add_part,
    edit_part,
    remove_part,
    set_part_state,
    get_part_state,
    # Species
    get_species_template,
    list_species,
    apply_species,
    add_species_part,
    get_genital_category,
    get_genital_mechanics,
    has_mechanic,
    has_ability,
    # Modifiers
    get_body_modifiers,
    add_modifier,
    remove_modifier,
    get_part_modifiers,
    clean_expired_modifiers,
    # Modifier shortcuts
    mark,
    write_on,
    inflate,
    resize,
    bind_part,
    pierce,
    tattoo,
    brand,
    drip,
    gape,
    heal_part,
    heal_all,
    clean_part,
    clean_all,
    # Shortcodes
    get_part_description,
    get_worn_description,
    process_shortcodes,
    # Display
    get_body_display,
    get_modifier_display,
)
