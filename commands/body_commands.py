"""
Body Commands for Gilderhaven
==============================

Commands for body customization.

Commands:
- body: View your body parts
- bodypart: Create/edit a body part
- bodystate: Set a part's current state
- species: Apply species template
- addpart: Add a part from a species
- modifiers: View body modifiers
- heal/clean: Remove temporary modifiers
"""

from evennia import Command, CmdSet
from world.body import (
    get_body_parts, get_body_states, get_body_modifiers,
    add_part, edit_part, remove_part, set_part_state,
    apply_species, add_species_part, list_species, get_species_template,
    get_body_display, get_modifier_display, process_shortcodes,
    heal_part, heal_all, clean_part, clean_all,
    SPECIES_TEMPLATES, MODIFIER_TYPES
)


class CmdBody(Command):
    """
    View your body configuration.
    
    Usage:
        body              - View all body parts and states
        body <part>       - View specific part details
        body test <text>  - Test shortcode processing
    
    Your body is built from parts, each with state-based descriptions.
    Use shortcodes like <body.eyes> in your description to show them.
    """
    
    key = "body"
    aliases = ["bodycheck", "mybody"]
    locks = "cmd:all()"
    help_category = "Body"
    
    def func(self):
        caller = self.caller
        
        if not self.args:
            # Show full body display
            caller.msg(get_body_display(caller))
            return
        
        args = self.args.strip().split(None, 1)
        
        if args[0] == "test" and len(args) > 1:
            # Test shortcode processing
            result = process_shortcodes(caller, args[1])
            caller.msg(f"|wInput:|n {args[1]}")
            caller.msg(f"|wOutput:|n {result}")
            return
        
        # Show specific part
        part_name = args[0].lower()
        parts = get_body_parts(caller)
        
        if part_name not in parts:
            caller.msg(f"You don't have a '{part_name}' part defined.")
            caller.msg("Use 'bodypart <name>' to create one.")
            return
        
        part_data = parts[part_name]
        lines = [f"|wPart: {part_name}|n"]
        lines.append("-" * 30)
        
        for state, desc in part_data.items():
            current = " |y<current>|n" if state == get_body_states(caller).get(part_name, "default") else ""
            lines.append(f"  {state}: {desc}{current}")
        
        caller.msg("\n".join(lines))


class CmdBodyPart(Command):
    """
    Create or edit a body part.
    
    Usage:
        bodypart <name>                     - Create with default (name as desc)
        bodypart <name> = <description>     - Create/set default description
        bodypart <name> <state> = <desc>    - Set description for a state
        bodypart delete <name>              - Remove a body part
    
    Examples:
        bodypart tail = long fluffy tail
        bodypart tail wagging = excitedly wagging tail
        bodypart tail aroused = tail raised invitingly
        bodypart cock aroused = thick red cock, knot visible
    
    Common states: default, aroused, alert, relaxed, injured
    """
    
    key = "bodypart"
    aliases = ["editpart", "setpart"]
    locks = "cmd:all()"
    help_category = "Body"
    
    def func(self):
        caller = self.caller
        
        if not self.args:
            caller.msg("Usage: bodypart <name> [state] = <description>")
            return
        
        # Check for delete
        if self.args.strip().lower().startswith("delete "):
            part_name = self.args.strip()[7:].lower()
            if remove_part(caller, part_name):
                caller.msg(f"Removed body part: {part_name}")
            else:
                caller.msg(f"No part named '{part_name}' to remove.")
            return
        
        # Parse arguments
        if "=" in self.args:
            left, desc = self.args.split("=", 1)
            left = left.strip()
            desc = desc.strip()
        else:
            left = self.args.strip()
            desc = None
        
        parts = left.split()
        part_name = parts[0].lower()
        state = parts[1].lower() if len(parts) > 1 else "default"
        
        if desc:
            edit_part(caller, part_name, state, desc)
            caller.msg(f"Set {part_name} [{state}]: {desc}")
        else:
            # Just create with default
            add_part(caller, part_name)
            caller.msg(f"Created body part: {part_name}")
            caller.msg("Use 'bodypart <name> = <desc>' to set description.")


class CmdBodyState(Command):
    """
    Set the current state of a body part.
    
    Usage:
        bodystate <part> <state>  - Set part to specific state
        bodystate <part>          - Reset to default state
    
    Examples:
        bodystate tail wagging
        bodystate ears alert
        bodystate cock aroused
        bodystate tail            - Reset to default
    
    Note: The 'aroused' effect automatically switches parts to
    their aroused state if they have one defined.
    """
    
    key = "bodystate"
    aliases = ["partstate"]
    locks = "cmd:all()"
    help_category = "Body"
    
    def func(self):
        caller = self.caller
        
        if not self.args:
            caller.msg("Usage: bodystate <part> [state]")
            return
        
        args = self.args.strip().split()
        part_name = args[0].lower()
        state = args[1].lower() if len(args) > 1 else None
        
        parts = get_body_parts(caller)
        
        if part_name not in parts:
            caller.msg(f"You don't have a '{part_name}' part defined.")
            return
        
        # Check if state exists
        if state and state not in parts[part_name]:
            available = ", ".join(parts[part_name].keys())
            caller.msg(f"'{state}' is not a valid state for {part_name}.")
            caller.msg(f"Available: {available}")
            return
        
        set_part_state(caller, part_name, state)
        
        if state:
            caller.msg(f"Set {part_name} to '{state}' state.")
        else:
            caller.msg(f"Reset {part_name} to default state.")


class CmdSpecies(Command):
    """
    Apply a species template or view available species.
    
    Usage:
        species                   - List available species
        species <name>            - View species details
        species apply <name>      - Apply species (adds parts)
        species replace <name>    - Replace all parts with species
    
    Examples:
        species canine
        species apply wolf
        species replace futa_canine
    
    Species provide pre-made body parts and genital mechanics.
    You can customize any part after applying.
    """
    
    key = "species"
    locks = "cmd:all()"
    help_category = "Body"
    
    def func(self):
        caller = self.caller
        
        if not self.args:
            # List all species
            lines = ["|wAvailable Species:|n"]
            lines.append("-" * 40)
            
            # Group by category
            humanoid = []
            canine = []
            feline = []
            other = []
            
            for key, data in SPECIES_TEMPLATES.items():
                entry = f"  {key}: {data['name']}"
                
                if key in ("human", "elf", "dwarf", "orc", "goblin"):
                    humanoid.append(entry)
                elif "canine" in key or key in ("wolf", "fox"):
                    canine.append(entry)
                elif "feline" in key or key in ("lion", "tiger"):
                    feline.append(entry)
                else:
                    other.append(entry)
            
            if humanoid:
                lines.append("|cHumanoid:|n")
                lines.extend(humanoid)
            if canine:
                lines.append("|cCanine:|n")
                lines.extend(canine)
            if feline:
                lines.append("|cFeline:|n")
                lines.extend(feline)
            if other:
                lines.append("|cOther:|n")
                lines.extend(other)
            
            lines.append("")
            lines.append("Use 'species <name>' for details.")
            lines.append("Use 'species apply <name>' to apply.")
            
            caller.msg("\n".join(lines))
            return
        
        args = self.args.strip().split()
        
        if args[0].lower() in ("apply", "replace"):
            if len(args) < 2:
                caller.msg(f"Usage: species {args[0]} <species_name>")
                return
            
            species_key = args[1].lower()
            replace = args[0].lower() == "replace"
            
            if apply_species(caller, species_key, replace=replace):
                template = get_species_template(species_key)
                caller.msg(f"|gApplied species template: {template['name']}|n")
                if replace:
                    caller.msg("All previous parts replaced.")
                else:
                    caller.msg("Parts added (existing parts kept).")
                
                # Show mechanics
                from world.body import get_genital_mechanics
                mechanics = get_genital_mechanics(caller)
                if mechanics:
                    caller.msg(f"Genital mechanics: {', '.join(mechanics)}")
            else:
                caller.msg(f"Unknown species: {args[1]}")
            return
        
        # View species details
        species_key = args[0].lower()
        template = get_species_template(species_key)
        
        if not template:
            caller.msg(f"Unknown species: {species_key}")
            caller.msg("Use 'species' to list available species.")
            return
        
        lines = [f"|w{template['name']}|n"]
        lines.append("-" * 40)
        lines.append(template.get("desc", ""))
        lines.append("")
        lines.append(f"Covering: {template.get('covering', 'skin')}")
        lines.append(f"Genital category: {template.get('genital_category', 'human')}")
        
        from world.body import GENITAL_MECHANICS
        mechanics = GENITAL_MECHANICS.get(template.get("genital_category", "human"), [])
        if mechanics:
            lines.append(f"Mechanics: {', '.join(mechanics)}")
        
        abilities = template.get("abilities", [])
        if abilities:
            lines.append(f"Abilities: {', '.join(abilities)}")
        
        lines.append("")
        lines.append("|cIncluded parts:|n")
        for part_name, part_data in template.get("parts", {}).items():
            states = list(part_data.keys())
            lines.append(f"  {part_name}: {', '.join(states)}")
        
        caller.msg("\n".join(lines))


class CmdAddPart(Command):
    """
    Add a single part from a species template.
    
    Usage:
        addpart <species>.<part>
    
    Examples:
        addpart canine.cock     - Add canine cock with knot mechanics
        addpart feline.ears     - Add cat ears
        addpart equine.cock     - Add horse cock with flare mechanics
    
    This lets you mix and match parts from different species.
    """
    
    key = "addpart"
    locks = "cmd:all()"
    help_category = "Body"
    
    def func(self):
        caller = self.caller
        
        if not self.args or "." not in self.args:
            caller.msg("Usage: addpart <species>.<part>")
            caller.msg("Example: addpart canine.cock")
            return
        
        species_key, part_name = self.args.strip().lower().split(".", 1)
        
        if add_species_part(caller, species_key, part_name):
            caller.msg(f"|gAdded {part_name} from {species_key} template.|n")
            
            # If it's genitals, show new mechanics
            if part_name == "cock":
                from world.body import get_genital_mechanics
                mechanics = get_genital_mechanics(caller)
                if mechanics:
                    caller.msg(f"Genital mechanics: {', '.join(mechanics)}")
        else:
            caller.msg(f"Could not find {part_name} in {species_key} template.")


class CmdModifiers(Command):
    """
    View your body modifiers.
    
    Usage:
        modifiers         - View all modifiers
        modifiers types   - List modifier types
    
    Modifiers are temporary or permanent changes to body parts,
    like marks, inflation, piercings, writing, etc.
    """
    
    key = "modifiers"
    aliases = ["bodymod", "bodymods"]
    locks = "cmd:all()"
    help_category = "Body"
    
    def func(self):
        caller = self.caller
        
        if self.args and self.args.strip().lower() == "types":
            lines = ["|wModifier Types:|n"]
            lines.append("-" * 40)
            
            for mod_type, mod_info in MODIFIER_TYPES.items():
                permanent = " (can be permanent)" if mod_info.get("can_be_permanent") else ""
                lines.append(f"  {mod_type}{permanent}")
            
            caller.msg("\n".join(lines))
            return
        
        caller.msg(get_modifier_display(caller))


class CmdHeal(Command):
    """
    Heal temporary marks from your body.
    
    Usage:
        heal          - Heal all temporary marks
        heal <part>   - Heal marks on specific part
    
    Removes: hickeys, bruises, bites, scratches, etc.
    Does NOT remove: piercings, tattoos, brands.
    """
    
    key = "heal"
    locks = "cmd:all()"
    help_category = "Body"
    
    def func(self):
        caller = self.caller
        
        if self.args:
            part_name = self.args.strip().lower()
            heal_part(caller, part_name)
            caller.msg(f"Healed marks on your {part_name}.")
        else:
            heal_all(caller)
            caller.msg("Healed all temporary marks.")


class CmdClean(Command):
    """
    Clean writing and fluids from your body.
    
    Usage:
        clean         - Clean entire body
        clean <part>  - Clean specific part
    
    Removes: writing, cum, other fluids.
    Does NOT remove: tattoos, brands, piercings.
    """
    
    key = "clean"
    aliases = ["wash"]
    locks = "cmd:all()"
    help_category = "Body"
    
    def func(self):
        caller = self.caller
        
        if self.args:
            part_name = self.args.strip().lower()
            clean_part(caller, part_name)
            caller.msg(f"Cleaned your {part_name}.")
        else:
            clean_all(caller)
            caller.msg("Cleaned your entire body.")


class CmdPronouns(Command):
    """
    Set your pronouns.
    
    Usage:
        pronouns                    - View current
        pronouns <subject/object/possessive>
    
    Examples:
        pronouns she/her/her
        pronouns he/him/his
        pronouns they/them/their
        pronouns ze/zir/zirs
    
    Used in shortcodes: <pronoun.subject>, <pronoun.object>, etc.
    """
    
    key = "pronouns"
    locks = "cmd:all()"
    help_category = "Body"
    
    def func(self):
        caller = self.caller
        
        if not self.args:
            current = caller.db.pronouns or "they/them/their"
            caller.msg(f"Your pronouns: {current}")
            caller.msg("Use 'pronouns <subject/object/possessive>' to change.")
            return
        
        pronouns = self.args.strip().lower()
        
        # Validate format
        parts = pronouns.split("/")
        if len(parts) != 3:
            caller.msg("Format: <subject>/<object>/<possessive>")
            caller.msg("Example: she/her/her or they/them/their")
            return
        
        caller.db.pronouns = pronouns
        caller.msg(f"Set pronouns to: {pronouns}")


class CmdPreview(Command):
    """
    Preview how your description will look with shortcodes.
    
    Usage:
        preview <text with shortcodes>
    
    Examples:
        preview A tall figure with <body.eyes> and <body.tail>.
        preview <pronoun.subject> has <body.fur> covering <pronoun.possessive> body.
    
    This shows what others would see when looking at you.
    """
    
    key = "preview"
    aliases = ["descpreview"]
    locks = "cmd:all()"
    help_category = "Body"
    
    def func(self):
        caller = self.caller
        
        if not self.args:
            # Preview current desc if set
            desc = caller.db.desc or "No description set."
            result = process_shortcodes(caller, desc)
            caller.msg("|wYour current description:|n")
            caller.msg(result)
            return
        
        result = process_shortcodes(caller, self.args.strip())
        caller.msg("|wPreview:|n")
        caller.msg(result)


# =============================================================================
# Command Set
# =============================================================================

class BodyCmdSet(CmdSet):
    """Body customization commands."""
    
    key = "body"
    priority = 1
    
    def at_cmdset_creation(self):
        self.add(CmdBody())
        self.add(CmdBodyPart())
        self.add(CmdBodyState())
        self.add(CmdSpecies())
        self.add(CmdAddPart())
        self.add(CmdModifiers())
        self.add(CmdHeal())
        self.add(CmdClean())
        self.add(CmdPronouns())
        self.add(CmdPreview())
