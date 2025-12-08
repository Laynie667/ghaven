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
- body: Body parts, species, gender, modifiers, shortcodes
- time_weather: Game time, seasons, weather conditions
- quests: Quest and task system
- crafting: Recipe-based item creation with skills
- combat: Combat system with stats, actions, state machine
- creatures: Creature templates, AI behaviors, spawn tables
- parties: Party formation, movement, combat coordination
- encounters: Random encounters, multi-wave combat, danger levels

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
    from world.body import apply_species, apply_gender_config, mark, process_shortcodes
    from world.time_weather import get_time, get_period, get_weather, is_night
    from world.quests import give_quest, check_objective, complete_quest
    from world.crafting import craft_item, can_craft, get_recipe, get_skill_level
    from world.combat import start_combat, is_in_combat, get_resource
    from world.creatures import get_creature_template, spawn_creature
    from world.parties import create_party, get_party, party_move
    from world.encounters import trigger_encounter, check_random_encounter
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
    GENDER_CONFIGS,
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
    # Gender
    get_gender_config,
    list_gender_configs,
    apply_gender_config,
    has_cock,
    has_pussy,
    has_breasts,
    has_womb,
    is_futa,
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

# Time and Weather
from .time_weather import (
    # Time constants
    TIME_PERIODS,
    DAYS_OF_WEEK,
    MONTHS,
    SEASONS,
    WEATHER_CONDITIONS,
    # Time functions
    get_time,
    get_hour,
    get_period,
    get_period_description,
    get_formatted_time,
    get_time_string,
    is_daytime,
    is_night,
    is_dawn,
    is_dusk,
    get_day_of_week,
    get_month,
    get_season,
    get_season_description,
    get_year,
    # Weather functions
    get_weather,
    get_global_weather,
    get_weather_description,
    get_weather_effects,
    has_weather_effect,
    set_weather,
    # NPC integration
    get_npc_schedule_period,
    # Admin
    advance_time,
    set_time_of_day,
    set_season,
    force_weather,
    get_time_debug,
)

# Quests
from .quests import (
    QUEST_TEMPLATES,
    QUEST_CATEGORIES,
    OBJECTIVE_TYPES,
    # Quest state
    get_quest_log,
    get_active_quests,
    get_completed_quests,
    has_quest,
    has_completed,
    get_quest_progress,
    is_quest_complete,
    can_take_quest,
    # Quest management
    give_quest,
    abandon_quest,
    complete_quest,
    # Objective checking
    check_objective,
    check_gather_objective,
    check_talk_objective,
    check_visit_objective,
    check_scene_objective,
    # Display
    get_quest_display,
    get_quest_list_display,
    get_board_display,
    # Task board
    get_available_board_quests,
    # NPC integration
    get_npc_quests,
    npc_has_quest,
    npc_can_complete_quest,
    # Daily reset
    reset_daily_quests,
    check_daily_reset,
)

# Crafting
from .crafting import (
    CRAFTING_CATEGORIES,
    RECIPE_TEMPLATES,
    WORKSTATION_TEMPLATES,
    QUALITY_TIERS,
    # Skills
    get_skill_level,
    get_skill_exp,
    get_skill_title,
    add_skill_exp,
    get_all_skills,
    # Recipes
    get_recipe,
    get_recipes_by_category,
    has_discovered_recipe,
    discover_recipe,
    get_available_recipes,
    get_discovery_hint,
    teach_npc_recipes,
    teach_scene_recipes,
    # Workstations
    get_workstation,
    has_workstation,
    # Crafting
    can_craft,
    craft_item,
    calculate_quality,
    # Display
    get_recipe_display,
    get_skill_display,
    get_category_recipe_list,
    # Quest integration
    check_craft_objective,
    # Initialize
    initialize_crafting,
)

# Combat System
from .combat import (
    PRIMARY_ATTRIBUTES,
    RESOURCE_POOLS,
    COMBAT_SKILLS,
    COMBAT_ACTIONS,
    DAMAGE_TYPES,
    COMBAT_STATES,
    EQUIPMENT_SLOTS as COMBAT_EQUIPMENT_SLOTS,
    WEAPON_TYPES,
    VICTORY_CONDITIONS,
    # Attributes
    get_attribute,
    set_attribute,
    # Resources
    get_resource,
    set_resource,
    modify_resource,
    get_max_resource,
    restore_all_resources,
    get_resource_display,
    get_all_resources_display,
    # Combat skills
    get_combat_skill,
    get_combat_skill_exp,
    add_combat_skill_exp,
    maybe_train_skill,
    # Calculations
    calculate_initiative,
    calculate_accuracy,
    calculate_evasion,
    calculate_defense,
    calculate_damage,
    calculate_composure_damage,
    roll_contest,
    # Combat state
    is_in_combat,
    get_combat,
    can_initiate_combat,
    start_combat,
    start_pvp_combat,
    process_defeat,
    initialize_combat_stats,
    CombatInstance,
    # Display
    get_attribute_display,
    get_combat_skills_display,
)

# Creatures
from .creatures import (
    CREATURE_CATEGORIES,
    AI_BEHAVIORS,
    CREATURE_TEMPLATES,
    SPAWN_TABLES,
    get_creature_template,
    get_spawn_table,
    roll_encounter,
    get_creature_stats,
    select_creature_attack,
    calculate_creature_damage,
    get_loot_drops,
    get_creature_exp,
    is_befriendable,
    get_befriend_difficulty,
    get_pack_size,
    get_defeat_type,
)

# Parties
from .parties import (
    PARTY_ROLES,
    PARTY_FORMATIONS,
    MAX_PARTY_SIZE,
    Party,
    get_party,
    is_in_party,
    is_party_leader,
    get_party_members,
    get_party_leader,
    create_party,
    disband_party,
    leave_party,
    invite_to_party,
    accept_party_invite,
    decline_party_invite,
    get_pending_invites,
    party_move,
    sync_party_location,
    party_recall,
    get_party_for_combat,
    start_party_combat,
    distribute_loot,
    distribute_exp,
    party_chat,
    party_emote,
)

# Encounters
from .encounters import (
    BASE_ENCOUNTER_CHANCE,
    DANGER_LEVELS,
    AREA_DANGER,
    ENCOUNTER_TEMPLATES,
    AREA_ENCOUNTERS,
    Encounter,
    get_area_danger,
    get_room_danger,
    check_random_encounter,
    spawn_creature,
    trigger_encounter,
    on_room_enter,
    get_active_encounter,
    is_in_encounter,
    on_combat_end,
    on_player_flee,
    scale_encounter_to_party,
    get_encounter_difficulty,
)

# Character States
from .states import (
    AROUSAL_LEVELS,
    ENERGY_LEVELS,
    CONDITION_LEVELS,
    CLEANLINESS_LEVELS,
    INTOXICATION_LEVELS,
    MAX_AROUSAL,
    MAX_ENERGY,
    MAX_CONDITION,
    MAX_CLEANLINESS,
    MAX_INTOXICATION,
    # Getters
    get_arousal,
    get_energy,
    get_condition,
    get_cleanliness,
    get_intoxication,
    get_arousal_level,
    get_energy_level,
    get_condition_level,
    get_cleanliness_level,
    get_intoxication_level,
    # Setters
    set_arousal,
    set_energy,
    set_condition,
    set_cleanliness,
    set_intoxication,
    # Modifiers
    modify_arousal,
    modify_energy,
    modify_condition,
    modify_cleanliness,
    modify_intoxication,
    # Actions
    arouse,
    calm_down,
    spend_energy,
    can_afford_energy,
    dirty,
    clean,
    intoxicate,
    sober_up,
    # Checks
    is_aroused,
    is_desperate,
    is_dirty,
    is_filthy,
    is_drunk,
    is_wasted,
    get_activity_modifier,
    # Display
    get_state_summary,
    get_state_display,
    # Initialization
    initialize_states,
    restore_all_states,
    # Tick functions
    tick_arousal_decay,
    tick_energy_regen,
    tick_condition_regen,
    tick_intoxication_decay,
    tick_all_states,
    # Shortcodes
    process_state_shortcodes,
)
