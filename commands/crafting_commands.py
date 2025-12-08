"""
Crafting Commands for Gilderhaven
==================================

Commands for the crafting system.

Commands:
- craft <recipe>     - Craft an item
- recipes [category] - List available recipes
- recipe <name>      - View recipe details
- skills             - View crafting skills
- workstation        - Use/examine workstation
"""

from evennia import Command, CmdSet
from evennia.utils.evtable import EvTable


class CmdCraft(Command):
    """
    Craft an item from a recipe.
    
    Usage:
        craft <recipe>
        craft <recipe> x<amount>
        
    Examples:
        craft health_potion
        craft copper_ingot x5
        
    You must have the required ingredients, skill level, and 
    workstation (if needed) to craft.
    """
    
    key = "craft"
    aliases = ["make", "create"]
    locks = "cmd:all()"
    help_category = "Crafting"
    
    def func(self):
        caller = self.caller
        
        if not self.args:
            caller.msg("Usage: craft <recipe>")
            caller.msg("Use 'recipes' to see available recipes.")
            return
        
        from world.crafting import (
            can_craft, craft_item, get_recipe,
            has_discovered_recipe, check_craft_objective
        )
        
        # Parse arguments
        args = self.args.strip().lower()
        amount = 1
        
        if " x" in args:
            parts = args.rsplit(" x", 1)
            args = parts[0]
            try:
                amount = int(parts[1])
                amount = max(1, min(amount, 10))  # Cap at 10
            except ValueError:
                amount = 1
        
        recipe_key = args.replace(" ", "_")
        
        # Check recipe exists
        recipe = get_recipe(recipe_key)
        if not recipe:
            # Try to find partial match
            from world.crafting import RECIPE_TEMPLATES
            matches = [k for k in RECIPE_TEMPLATES.keys() if args in k]
            if matches:
                caller.msg(f"Unknown recipe '{args}'. Did you mean: {', '.join(matches[:5])}?")
            else:
                caller.msg(f"Unknown recipe: {args}")
            return
        
        # Check if discovered
        if not has_discovered_recipe(caller, recipe_key):
            caller.msg("You haven't learned that recipe yet.")
            return
        
        # Craft items
        success_count = 0
        total_exp = 0
        created_items = []
        final_level_up = False
        
        for i in range(amount):
            # Check if can craft
            can, reason = can_craft(caller, recipe_key)
            if not can:
                if i == 0:
                    caller.msg(f"|rCannot craft:|n {reason}")
                    return
                else:
                    caller.msg(f"|yAfter {i} crafts:|n {reason}")
                    break
            
            # Do the craft
            result = craft_item(caller, recipe_key)
            
            if result["success"]:
                success_count += 1
                total_exp += result["exp_gained"]
                created_items.extend(result.get("items", []))
                if result["leveled_up"]:
                    final_level_up = True
                    final_level = result["new_level"]
            else:
                caller.msg(f"|rCraft failed:|n {result['message']}")
                break
        
        # Report results
        if success_count > 0:
            recipe_name = recipe.get("name", recipe_key)
            
            if amount == 1:
                caller.msg(result["message"])
            else:
                quality = result.get("quality", "common")
                from world.crafting import QUALITY_TIERS
                qcolor = QUALITY_TIERS.get(quality, {}).get("color", "|w")
                caller.msg(f"You crafted {success_count}x {qcolor}{quality}|n {recipe_name}! (+{total_exp} exp)")
            
            if final_level_up:
                category = recipe.get("category")
                from world.crafting import CRAFTING_CATEGORIES
                cat_name = CRAFTING_CATEGORIES.get(category, {}).get("name", category)
                caller.msg(f"|y{cat_name} skill increased to {final_level}!|n")
            
            # Quest integration
            check_craft_objective(caller, recipe_key, success_count)
            
            # Room message
            caller.location.msg_contents(
                f"{caller.name} finishes crafting.",
                exclude=[caller]
            )


class CmdRecipes(Command):
    """
    View available crafting recipes.
    
    Usage:
        recipes              - List all categories
        recipes <category>   - List recipes in category
        recipes all          - List all discovered recipes
        
    Categories:
        alchemy, smithing, cooking, tailoring,
        woodworking, jewelcrafting, leatherworking
    """
    
    key = "recipes"
    aliases = ["recipelist", "recipe list"]
    locks = "cmd:all()"
    help_category = "Crafting"
    
    def func(self):
        caller = self.caller
        
        from world.crafting import (
            CRAFTING_CATEGORIES, get_available_recipes,
            get_category_recipe_list, get_skill_level
        )
        
        args = self.args.strip().lower() if self.args else ""
        
        if not args:
            # Show categories
            lines = ["|w=== Crafting Categories ===|n", ""]
            
            for cat_key, cat_data in CRAFTING_CATEGORIES.items():
                icon = cat_data.get("icon", "•")
                name = cat_data.get("name", cat_key)
                desc = cat_data.get("desc", "")
                skill = get_skill_level(caller, cat_key)
                
                # Count recipes
                recipes = get_available_recipes(caller, category=cat_key)
                count = len(recipes)
                
                lines.append(f"{icon} |c{name}|n (Skill: {skill})")
                lines.append(f"   {desc}")
                lines.append(f"   |x{count} recipes discovered|n")
                lines.append("")
            
            lines.append("Use |wrecipes <category>|n to see recipes.")
            caller.msg("\n".join(lines))
            return
        
        if args == "all":
            # Show all discovered recipes
            all_recipes = get_available_recipes(caller)
            if not all_recipes:
                caller.msg("You haven't discovered any recipes yet.")
                return
            
            lines = ["|w=== All Discovered Recipes ===|n", ""]
            
            # Group by category
            by_category = {}
            for key, recipe in all_recipes.items():
                cat = recipe.get("category", "unknown")
                if cat not in by_category:
                    by_category[cat] = []
                by_category[cat].append((key, recipe))
            
            for cat_key, recipes in sorted(by_category.items()):
                cat_name = CRAFTING_CATEGORIES.get(cat_key, {}).get("name", cat_key)
                lines.append(f"|c{cat_name}|n:")
                for key, recipe in sorted(recipes, key=lambda x: x[1].get("skill_required", 0)):
                    name = recipe.get("name", key)
                    req = recipe.get("skill_required", 0)
                    lines.append(f"  • {name} |x(skill {req})|n")
                lines.append("")
            
            caller.msg("\n".join(lines))
            return
        
        # Show specific category
        category = args.replace(" ", "")
        if category not in CRAFTING_CATEGORIES:
            # Try partial match
            matches = [k for k in CRAFTING_CATEGORIES.keys() if args in k]
            if matches:
                category = matches[0]
            else:
                caller.msg(f"Unknown category: {args}")
                caller.msg(f"Categories: {', '.join(CRAFTING_CATEGORIES.keys())}")
                return
        
        output = get_category_recipe_list(caller, category)
        caller.msg(output)


class CmdRecipe(Command):
    """
    View details of a specific recipe.
    
    Usage:
        recipe <name>
        
    Examples:
        recipe health_potion
        recipe iron_pickaxe
    """
    
    key = "recipe"
    aliases = ["recipeinfo"]
    locks = "cmd:all()"
    help_category = "Crafting"
    
    def func(self):
        caller = self.caller
        
        if not self.args:
            caller.msg("Usage: recipe <name>")
            return
        
        from world.crafting import (
            get_recipe, get_recipe_display, 
            has_discovered_recipe, RECIPE_TEMPLATES
        )
        
        recipe_key = self.args.strip().lower().replace(" ", "_")
        
        # Try to find recipe
        recipe = get_recipe(recipe_key)
        if not recipe:
            # Partial match
            matches = [k for k in RECIPE_TEMPLATES.keys() if self.args.lower() in k]
            if matches:
                caller.msg(f"Unknown recipe. Did you mean: {', '.join(matches[:5])}?")
            else:
                caller.msg(f"Unknown recipe: {self.args}")
            return
        
        # Check if discovered
        if not has_discovered_recipe(caller, recipe_key):
            caller.msg("You haven't learned that recipe yet.")
            caller.msg("|xIt might be taught by an NPC or found in the world.|n")
            return
        
        output = get_recipe_display(recipe_key, caller)
        caller.msg(output)


class CmdSkills(Command):
    """
    View your crafting skills.
    
    Usage:
        skills              - View all crafting skills
        skills <category>   - View specific skill details
        
    Examples:
        skills
        skills alchemy
    """
    
    key = "skills"
    aliases = ["craftskills", "craftingskills"]
    locks = "cmd:all()"
    help_category = "Crafting"
    
    def func(self):
        caller = self.caller
        
        from world.crafting import (
            get_skill_display, CRAFTING_CATEGORIES,
            get_skill_level, get_skill_exp, EXP_PER_LEVEL,
            get_available_recipes
        )
        
        args = self.args.strip().lower() if self.args else ""
        
        if not args:
            # Show all skills
            output = get_skill_display(caller)
            caller.msg(output)
            return
        
        # Show specific category
        category = args.replace(" ", "")
        if category not in CRAFTING_CATEGORIES:
            matches = [k for k in CRAFTING_CATEGORIES.keys() if args in k]
            if matches:
                category = matches[0]
            else:
                caller.msg(f"Unknown category: {args}")
                return
        
        cat_data = CRAFTING_CATEGORIES[category]
        level = get_skill_level(caller, category)
        exp = get_skill_exp(caller, category)
        recipes = get_available_recipes(caller, category=category)
        
        lines = []
        lines.append(f"|w=== {cat_data['name']} ===|n")
        lines.append(f"|x{cat_data.get('desc', '')}|n")
        lines.append("")
        lines.append(f"Skill Level: |c{level}|n")
        lines.append(f"Experience: {exp}/{EXP_PER_LEVEL}")
        lines.append(f"Recipes Known: {len(recipes)}")
        lines.append("")
        
        # Show unlockable recipes
        from world.crafting import RECIPE_TEMPLATES
        upcoming = []
        for key, recipe in RECIPE_TEMPLATES.items():
            if recipe.get("category") != category:
                continue
            req = recipe.get("skill_required", 0)
            if req > level and req <= level + 20:
                upcoming.append((key, recipe.get("name", key), req))
        
        if upcoming:
            lines.append("|wUpcoming Recipes:|n")
            for key, name, req in sorted(upcoming, key=lambda x: x[2]):
                lines.append(f"  • {name} |x(unlocks at skill {req})|n")
        
        caller.msg("\n".join(lines))


class CmdWorkstation(Command):
    """
    Use or examine a crafting workstation.
    
    Usage:
        workstation              - List workstations in this room
        workstation <name>       - Examine a workstation
        workstation use <name>   - Alias for looking (you craft AT workstations)
        
    Workstations enable crafting of specific categories.
    Use 'craft' at a location with the required workstation.
    """
    
    key = "workstation"
    aliases = ["ws", "station", "bench"]
    locks = "cmd:all()"
    help_category = "Crafting"
    
    def func(self):
        caller = self.caller
        room = caller.location
        
        from world.crafting import WORKSTATION_TEMPLATES, CRAFTING_CATEGORIES
        
        # Find workstations in room
        workstations = []
        for obj in room.contents:
            if obj.db.workstation_type:
                workstations.append(obj)
        
        args = self.args.strip().lower() if self.args else ""
        
        if not args:
            if not workstations:
                caller.msg("There are no crafting workstations here.")
                return
            
            lines = ["|w=== Workstations Here ===|n", ""]
            for ws in workstations:
                ws_type = ws.db.workstation_type
                ws_data = WORKSTATION_TEMPLATES.get(ws_type, {})
                category = ws_data.get("category", "unknown")
                cat_name = CRAFTING_CATEGORIES.get(category, {}).get("name", category)
                
                lines.append(f"|c{ws.key}|n ({cat_name})")
            
            lines.append("")
            lines.append("Use |wcraft <recipe>|n at a workstation to craft.")
            caller.msg("\n".join(lines))
            return
        
        # Handle 'use' prefix
        if args.startswith("use "):
            args = args[4:]
        
        # Find specific workstation
        target = None
        for ws in workstations:
            if args in ws.key.lower() or args == ws.db.workstation_type:
                target = ws
                break
        
        if not target:
            caller.msg(f"No workstation matching '{args}' found here.")
            return
        
        # Display workstation info
        ws_type = target.db.workstation_type
        ws_data = WORKSTATION_TEMPLATES.get(ws_type, {})
        category = ws_data.get("category", "unknown")
        cat_data = CRAFTING_CATEGORIES.get(category, {})
        
        lines = []
        lines.append(f"|w{target.key}|n")
        lines.append(target.db.desc or ws_data.get("desc", "A crafting workstation."))
        lines.append("")
        lines.append(f"Crafting Type: |c{cat_data.get('name', category)}|n")
        
        bonus = ws_data.get("quality_bonus", 0)
        if bonus > 0:
            lines.append(f"Quality Bonus: |g+{bonus}|n")
        
        lines.append("")
        lines.append("Use |wrecipes " + category + "|n to see craftable recipes.")
        
        caller.msg("\n".join(lines))


class CmdLearnRecipe(Command):
    """
    Learn a new recipe (admin/debug command).
    
    Usage:
        learnrecipe <recipe>
        learnrecipe all
        
    Note: Most recipes are discovered by default or learned
    from NPCs and exploration.
    """
    
    key = "learnrecipe"
    aliases = ["discoverrecipe"]
    locks = "cmd:perm(Builder) or perm(Admin)"
    help_category = "Crafting"
    
    def func(self):
        caller = self.caller
        
        if not self.args:
            caller.msg("Usage: learnrecipe <recipe> | all")
            return
        
        from world.crafting import (
            discover_recipe, RECIPE_TEMPLATES,
            has_discovered_recipe
        )
        
        args = self.args.strip().lower()
        
        if args == "all":
            count = 0
            for recipe_key in RECIPE_TEMPLATES:
                if not has_discovered_recipe(caller, recipe_key):
                    discover_recipe(caller, recipe_key)
                    count += 1
            caller.msg(f"Learned {count} new recipes!")
            return
        
        recipe_key = args.replace(" ", "_")
        
        if recipe_key not in RECIPE_TEMPLATES:
            caller.msg(f"Unknown recipe: {args}")
            return
        
        if has_discovered_recipe(caller, recipe_key):
            caller.msg("You already know that recipe.")
            return
        
        discover_recipe(caller, recipe_key)
        recipe = RECIPE_TEMPLATES[recipe_key]
        caller.msg(f"|gLearned recipe: {recipe.get('name', recipe_key)}!|n")


class CmdCraftingAdmin(Command):
    """
    Admin commands for crafting system.
    
    Usage:
        craftadmin setskill <player> <category> <level>
        craftadmin addexp <player> <category> <amount>
        craftadmin spawn <workstation_type>
        craftadmin list workstations
        craftadmin list recipes [category]
    """
    
    key = "craftadmin"
    aliases = ["craftingadmin"]
    locks = "cmd:perm(Admin)"
    help_category = "Admin"
    
    def func(self):
        caller = self.caller
        
        if not self.args:
            caller.msg("Usage: craftadmin <subcommand> [args]")
            caller.msg("Subcommands: setskill, addexp, spawn, list")
            return
        
        args = self.args.strip().split()
        subcmd = args[0].lower()
        
        from world.crafting import (
            CRAFTING_CATEGORIES, WORKSTATION_TEMPLATES,
            RECIPE_TEMPLATES, add_skill_exp
        )
        
        if subcmd == "setskill" and len(args) >= 4:
            from evennia import search_object
            target = search_object(args[1])
            if not target:
                caller.msg(f"Player not found: {args[1]}")
                return
            target = target[0]
            
            category = args[2].lower()
            if category not in CRAFTING_CATEGORIES:
                caller.msg(f"Invalid category: {category}")
                return
            
            try:
                level = int(args[3])
            except ValueError:
                caller.msg("Level must be a number.")
                return
            
            if not target.db.crafting_skills:
                target.db.crafting_skills = {}
            target.db.crafting_skills[category] = max(0, min(100, level))
            caller.msg(f"Set {target.name}'s {category} skill to {level}.")
            
        elif subcmd == "addexp" and len(args) >= 4:
            from evennia import search_object
            target = search_object(args[1])
            if not target:
                caller.msg(f"Player not found: {args[1]}")
                return
            target = target[0]
            
            category = args[2].lower()
            if category not in CRAFTING_CATEGORIES:
                caller.msg(f"Invalid category: {category}")
                return
            
            try:
                amount = int(args[3])
            except ValueError:
                caller.msg("Amount must be a number.")
                return
            
            new_level, leveled = add_skill_exp(target, category, amount)
            caller.msg(f"Added {amount} exp to {target.name}'s {category}. Level: {new_level}")
            
        elif subcmd == "spawn" and len(args) >= 2:
            ws_type = args[1].lower()
            if ws_type not in WORKSTATION_TEMPLATES:
                caller.msg(f"Unknown workstation type: {ws_type}")
                caller.msg(f"Available: {', '.join(WORKSTATION_TEMPLATES.keys())}")
                return
            
            ws_data = WORKSTATION_TEMPLATES[ws_type]
            from evennia import create_object
            ws = create_object(
                "evennia.objects.objects.DefaultObject",
                key=ws_data["key"],
                location=caller.location
            )
            ws.db.desc = ws_data.get("desc", "A workstation.")
            ws.db.workstation_type = ws_type
            caller.msg(f"Spawned {ws.key}.")
            
        elif subcmd == "list":
            if len(args) < 2:
                caller.msg("Usage: craftadmin list workstations|recipes [category]")
                return
            
            list_type = args[1].lower()
            
            if list_type == "workstations":
                lines = ["|wWorkstation Types:|n"]
                for key, data in WORKSTATION_TEMPLATES.items():
                    lines.append(f"  {key}: {data['key']} ({data['category']})")
                caller.msg("\n".join(lines))
                
            elif list_type == "recipes":
                category = args[2].lower() if len(args) > 2 else None
                lines = ["|wRecipe Templates:|n"]
                
                for key, recipe in sorted(RECIPE_TEMPLATES.items()):
                    if category and recipe.get("category") != category:
                        continue
                    lines.append(f"  {key}: {recipe['name']} ({recipe.get('category')}, skill {recipe.get('skill_required', 0)})")
                
                caller.msg("\n".join(lines))
        else:
            caller.msg("Unknown subcommand or missing arguments.")


# =============================================================================
# Command Set
# =============================================================================

class CraftingCmdSet(CmdSet):
    """Crafting commands."""
    
    key = "CraftingCmdSet"
    
    def at_cmdset_creation(self):
        self.add(CmdCraft())
        self.add(CmdRecipes())
        self.add(CmdRecipe())
        self.add(CmdSkills())
        self.add(CmdWorkstation())
        self.add(CmdLearnRecipe())
        self.add(CmdCraftingAdmin())
