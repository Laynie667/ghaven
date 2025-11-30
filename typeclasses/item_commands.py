"""
Item Commands
=============

Commands for interacting with items:
- Collar/uncolllar
- Leash/unleash/tug
- Use (toys, consumables)
- Restrain/free
- Gag/ungag
- Blindfold
"""

from evennia import Command, CmdSet
from evennia.utils.search import search_object


# =============================================================================
# HELPER FUNCTIONS
# =============================================================================

def find_item_on_char(character, item_type_or_key, location=None):
    """Find item worn by or held by character."""
    from .items import ItemType
    
    for obj in character.contents:
        # Check by item type
        if hasattr(obj, 'item_type'):
            itype = obj.item_type
            itype_val = itype.value if hasattr(itype, 'value') else itype
            
            if item_type_or_key == itype_val:
                if location and hasattr(obj, 'wear_location'):
                    loc = obj.wear_location
                    loc_val = loc.value if hasattr(loc, 'value') else loc
                    if loc_val == location:
                        return obj
                else:
                    return obj
        
        # Check by key
        if obj.key.lower() == item_type_or_key.lower():
            return obj
    
    return None


def find_target(caller, target_name):
    """Find target character in room."""
    if not target_name:
        return None
    
    candidates = caller.search(target_name, location=caller.location)
    if not candidates:
        return None
    return candidates


# =============================================================================
# COLLAR COMMANDS
# =============================================================================

class CmdCollar(Command):
    """
    Put a collar on someone.
    
    Usage:
        collar <target>
        collar <target> with <collar>
    
    You must be holding a collar to use this command.
    """
    
    key = "collar"
    locks = "cmd:all()"
    
    def parse(self):
        args = self.args.strip()
        self.target_name = ""
        self.collar_name = ""
        
        if " with " in args:
            parts = args.split(" with ", 1)
            self.target_name = parts[0].strip()
            self.collar_name = parts[1].strip()
        else:
            self.target_name = args
    
    def func(self):
        from .items import Collar
        
        if not self.target_name:
            self.caller.msg("Collar who?")
            return
        
        target = find_target(self.caller, self.target_name)
        if not target:
            self.caller.msg(f"Can't find '{self.target_name}'.")
            return
        
        # Find collar
        collar = None
        if self.collar_name:
            collar = self.caller.search(self.collar_name, location=self.caller)
        else:
            # Find first collar in inventory
            for obj in self.caller.contents:
                if isinstance(obj, Collar) and not obj.worn_by:
                    collar = obj
                    break
        
        if not collar:
            self.caller.msg("You're not holding a collar.")
            return
        
        if not isinstance(collar, Collar):
            self.caller.msg(f"{collar.key} isn't a collar.")
            return
        
        # Check if target already collared
        existing = find_item_on_char(target, "collar", "neck")
        if existing:
            self.caller.msg(f"{target.key} is already wearing a collar.")
            return
        
        # Try to put collar on
        success, msg = collar.wear(target)
        
        if success:
            collar.set_owner(self.caller)
            self.caller.msg(f"You fasten {collar.key} around {target.key}'s neck.")
            target.msg(f"{self.caller.key} fastens {collar.key} around your neck.")
            self.caller.location.msg_contents(
                f"{self.caller.key} fastens a collar around {target.key}'s neck.",
                exclude=[self.caller, target]
            )
        else:
            self.caller.msg(msg)


class CmdUncollar(Command):
    """
    Remove a collar from someone.
    
    Usage:
        uncollar <target>
        uncollar me
    """
    
    key = "uncollar"
    aliases = ["remove collar"]
    locks = "cmd:all()"
    
    def func(self):
        target_name = self.args.strip()
        
        if not target_name or target_name.lower() == "me":
            target = self.caller
        else:
            target = find_target(self.caller, target_name)
            if not target:
                self.caller.msg(f"Can't find '{target_name}'.")
                return
        
        collar = find_item_on_char(target, "collar", "neck")
        if not collar:
            self.caller.msg(f"{'You aren' if target == self.caller else target.key + ' isn'}t wearing a collar.")
            return
        
        success, msg = collar.remove()
        
        if success:
            collar.location = self.caller
            if target == self.caller:
                self.caller.msg(f"You remove your {collar.key}.")
            else:
                self.caller.msg(f"You remove {target.key}'s {collar.key}.")
                target.msg(f"{self.caller.key} removes your {collar.key}.")
        else:
            self.caller.msg(msg)


class CmdTag(Command):
    """
    Set or read a collar tag.
    
    Usage:
        tag <target>
        tag <target> = <text>
    """
    
    key = "tag"
    locks = "cmd:all()"
    
    def func(self):
        if "=" in self.args:
            target_name, text = self.args.split("=", 1)
            target_name = target_name.strip()
            text = text.strip()
        else:
            target_name = self.args.strip()
            text = None
        
        if not target_name:
            self.caller.msg("Tag whose collar?")
            return
        
        target = find_target(self.caller, target_name)
        if not target:
            self.caller.msg(f"Can't find '{target_name}'.")
            return
        
        collar = find_item_on_char(target, "collar", "neck")
        if not collar:
            self.caller.msg(f"{target.key} isn't wearing a collar.")
            return
        
        if text:
            collar.set_tag(text)
            self.caller.msg(f"You engrave '{text}' on {target.key}'s collar tag.")
            target.msg(f"{self.caller.key} engraves something on your collar tag.")
        else:
            if collar.has_tag and collar.tag_text:
                self.caller.msg(f"{target.key}'s collar tag reads: '{collar.tag_text}'")
            else:
                self.caller.msg(f"{target.key}'s collar has no tag or the tag is blank.")


# =============================================================================
# LEASH COMMANDS
# =============================================================================

class CmdLeash(Command):
    """
    Attach a leash to someone's collar.
    
    Usage:
        leash <target>
        leash <target> with <leash>
    """
    
    key = "leash"
    locks = "cmd:all()"
    
    def parse(self):
        args = self.args.strip()
        self.target_name = ""
        self.leash_name = ""
        
        if " with " in args:
            parts = args.split(" with ", 1)
            self.target_name = parts[0].strip()
            self.leash_name = parts[1].strip()
        else:
            self.target_name = args
    
    def func(self):
        from .items import Leash, Collar
        
        if not self.target_name:
            self.caller.msg("Leash who?")
            return
        
        target = find_target(self.caller, self.target_name)
        if not target:
            self.caller.msg(f"Can't find '{self.target_name}'.")
            return
        
        # Find leash
        leash = None
        if self.leash_name:
            leash = self.caller.search(self.leash_name, location=self.caller)
        else:
            for obj in self.caller.contents:
                if isinstance(obj, Leash) and not obj.attached_to:
                    leash = obj
                    break
        
        if not leash or not isinstance(leash, Leash):
            self.caller.msg("You're not holding a leash.")
            return
        
        # Find target's collar
        collar = find_item_on_char(target, "collar", "neck")
        if not collar or not isinstance(collar, Collar):
            self.caller.msg(f"{target.key} isn't wearing a collar.")
            return
        
        success, msg = leash.attach_to_collar(collar, self.caller)
        
        if success:
            self.caller.msg(msg)
            target.msg(f"{self.caller.key} clips a leash to your collar.")
            self.caller.location.msg_contents(
                f"{self.caller.key} clips a leash to {target.key}'s collar.",
                exclude=[self.caller, target]
            )
        else:
            self.caller.msg(msg)


class CmdUnleash(Command):
    """
    Remove a leash.
    
    Usage:
        unleash
        unleash <target>
    """
    
    key = "unleash"
    aliases = ["unclip leash"]
    locks = "cmd:all()"
    
    def func(self):
        from .items import Leash
        
        # Find leash being held or attached
        leash = None
        for obj in self.caller.contents:
            if isinstance(obj, Leash) and obj.attached_to:
                leash = obj
                break
        
        if not leash:
            self.caller.msg("You're not holding an attached leash.")
            return
        
        creature = leash.get_leashed_creature()
        success, msg = leash.detach()
        
        if success:
            name = creature.key if creature else "them"
            self.caller.msg(f"You unclip the leash from {name}'s collar.")
            if creature:
                creature.msg(f"{self.caller.key} unclips the leash from your collar.")
        else:
            self.caller.msg(msg)


class CmdTug(Command):
    """
    Tug on a leash you're holding.
    
    Usage:
        tug
        tug hard
    """
    
    key = "tug"
    locks = "cmd:all()"
    
    def func(self):
        from .items import Leash
        
        intensity = "light"
        if self.args.strip().lower() in ["hard", "firmly", "rough"]:
            intensity = "hard"
        elif self.args.strip().lower() in ["firm", "sharply"]:
            intensity = "firm"
        
        leash = None
        for obj in self.caller.contents:
            if isinstance(obj, Leash) and obj.attached_to:
                leash = obj
                break
        
        if not leash:
            self.caller.msg("You're not holding an attached leash.")
            return
        
        msg = leash.tug(intensity)
        self.caller.msg(msg)
        
        creature = leash.get_leashed_creature()
        if creature:
            tug_msgs = {
                "light": "You feel a light tug on your collar.",
                "firm": "Your collar tugs firmly, getting your attention.",
                "hard": "Your collar yanks sharply, pulling you!",
            }
            creature.msg(tug_msgs.get(intensity, tug_msgs["light"]))
            self.caller.location.msg_contents(msg, exclude=[self.caller, creature])


# =============================================================================
# TOY/USE COMMANDS
# =============================================================================

class CmdUse(Command):
    """
    Use an item on yourself or another.
    
    Usage:
        use <item>
        use <item> on <target>
    """
    
    key = "use"
    locks = "cmd:all()"
    
    def parse(self):
        args = self.args.strip()
        self.item_name = ""
        self.target_name = ""
        
        if " on " in args:
            parts = args.split(" on ", 1)
            self.item_name = parts[0].strip()
            self.target_name = parts[1].strip()
        else:
            self.item_name = args
    
    def func(self):
        from .items import Consumable, Treat, Toy
        
        if not self.item_name:
            self.caller.msg("Use what?")
            return
        
        item = self.caller.search(self.item_name, location=self.caller)
        if not item:
            return
        
        target = self.caller
        if self.target_name:
            target = find_target(self.caller, self.target_name)
            if not target:
                self.caller.msg(f"Can't find '{self.target_name}'.")
                return
        
        # Handle different item types
        if isinstance(item, Treat):
            if target == self.caller:
                self.caller.msg("You should use treats on animals, not yourself.")
                return
            success, msg = item.use_on(self.caller, target)
            self.caller.msg(msg)
            if success:
                target.msg(f"{self.caller.key} gives you a treat!")
            return
        
        if isinstance(item, Consumable):
            success, msg = item.use(target)
            if target == self.caller:
                self.caller.msg(msg)
            else:
                self.caller.msg(f"You give {item.key} to {target.key}.")
                target.msg(msg)
            return
        
        if isinstance(item, Toy):
            if item.is_vibrating:
                # Toggle vibration
                current = item.vibration_level or 0
                new_level = (current + 1) % 6
                success, msg = item.set_vibration(new_level)
                self.caller.msg(msg)
                return
            
            if item.is_inflatable and not item.worn_by:
                success, msg = item.inflate()
                self.caller.msg(msg)
                return
        
        self.caller.msg(f"You're not sure how to use {item.key}.")


class CmdVibrate(Command):
    """
    Set vibration level on a toy.
    
    Usage:
        vibrate <item> <level>
        vibrate <item> off
    """
    
    key = "vibrate"
    locks = "cmd:all()"
    
    def func(self):
        from .items import Toy
        
        args = self.args.split()
        if len(args) < 2:
            self.caller.msg("Usage: vibrate <item> <level/off>")
            return
        
        item_name = args[0]
        level_str = args[1]
        
        item = self.caller.search(item_name, location=self.caller)
        if not item:
            return
        
        if not isinstance(item, Toy):
            self.caller.msg(f"{item.key} isn't a toy.")
            return
        
        if not item.is_vibrating:
            self.caller.msg(f"{item.key} doesn't vibrate.")
            return
        
        if level_str.lower() == "off":
            level = 0
        else:
            try:
                level = int(level_str)
            except ValueError:
                self.caller.msg("Level must be a number 0-5 or 'off'.")
                return
        
        success, msg = item.set_vibration(level)
        self.caller.msg(msg)
        
        # Notify wearer
        wearer = item.get_wearer()
        if wearer and wearer != self.caller:
            wearer.msg(msg)


class CmdInflate(Command):
    """
    Inflate/deflate an inflatable toy.
    
    Usage:
        inflate <item>
        deflate <item>
    """
    
    key = "inflate"
    aliases = ["pump"]
    locks = "cmd:all()"
    
    def func(self):
        from .items import Toy
        
        item_name = self.args.strip()
        if not item_name:
            self.caller.msg("Inflate what?")
            return
        
        item = self.caller.search(item_name, location=self.caller)
        if not item:
            return
        
        if not isinstance(item, Toy) or not item.is_inflatable:
            self.caller.msg(f"{item.key} can't be inflated.")
            return
        
        success, msg = item.inflate()
        self.caller.msg(msg)
        
        wearer = item.get_wearer()
        if wearer and wearer != self.caller:
            wearer.msg(msg)


class CmdDeflate(Command):
    """Deflate an inflatable toy."""
    
    key = "deflate"
    locks = "cmd:all()"
    
    def func(self):
        from .items import Toy
        
        item_name = self.args.strip()
        if not item_name:
            self.caller.msg("Deflate what?")
            return
        
        item = self.caller.search(item_name, location=self.caller)
        if not item:
            return
        
        if not isinstance(item, Toy) or not item.is_inflatable:
            self.caller.msg(f"{item.key} can't be deflated.")
            return
        
        success, msg = item.deflate()
        self.caller.msg(msg)


# =============================================================================
# RESTRAINT COMMANDS
# =============================================================================

class CmdRestrain(Command):
    """
    Restrain someone with cuffs/rope.
    
    Usage:
        restrain <target>
        restrain <target> with <restraint>
    """
    
    key = "restrain"
    aliases = ["bind", "tie"]
    locks = "cmd:all()"
    
    def parse(self):
        args = self.args.strip()
        self.target_name = ""
        self.item_name = ""
        
        if " with " in args:
            parts = args.split(" with ", 1)
            self.target_name = parts[0].strip()
            self.item_name = parts[1].strip()
        else:
            self.target_name = args
    
    def func(self):
        from .items import Restraint
        
        if not self.target_name:
            self.caller.msg("Restrain who?")
            return
        
        target = find_target(self.caller, self.target_name)
        if not target:
            self.caller.msg(f"Can't find '{self.target_name}'.")
            return
        
        restraint = None
        if self.item_name:
            restraint = self.caller.search(self.item_name, location=self.caller)
        else:
            for obj in self.caller.contents:
                if isinstance(obj, Restraint) and not obj.worn_by:
                    restraint = obj
                    break
        
        if not restraint or not isinstance(restraint, Restraint):
            self.caller.msg("You're not holding any restraints.")
            return
        
        success, msg = restraint.wear(target)
        
        if success:
            loc = restraint.binding_location
            self.caller.msg(f"You bind {target.key}'s {loc} with {restraint.key}.")
            target.msg(f"{self.caller.key} binds your {loc} with {restraint.key}.")
            self.caller.location.msg_contents(
                f"{self.caller.key} binds {target.key} with {restraint.key}.",
                exclude=[self.caller, target]
            )
        else:
            self.caller.msg(msg)


class CmdFree(Command):
    """
    Free someone from restraints.
    
    Usage:
        free <target>
    """
    
    key = "free"
    aliases = ["untie", "unbind"]
    locks = "cmd:all()"
    
    def func(self):
        from .items import Restraint
        
        target_name = self.args.strip()
        if not target_name:
            self.caller.msg("Free who?")
            return
        
        target = find_target(self.caller, target_name)
        if not target:
            self.caller.msg(f"Can't find '{target_name}'.")
            return
        
        # Find restraints on target
        restraints = [obj for obj in target.contents 
                     if isinstance(obj, Restraint) and obj.worn_by]
        
        if not restraints:
            self.caller.msg(f"{target.key} isn't restrained.")
            return
        
        freed = []
        for r in restraints:
            success, msg = r.remove()
            if success:
                r.location = self.caller
                freed.append(r.key)
            else:
                self.caller.msg(f"Can't remove {r.key}: {msg}")
        
        if freed:
            self.caller.msg(f"You free {target.key} from {', '.join(freed)}.")
            target.msg(f"{self.caller.key} frees you from your restraints.")


class CmdStruggle(Command):
    """
    Try to escape restraints.
    
    Usage:
        struggle
    """
    
    key = "struggle"
    aliases = ["escape"]
    locks = "cmd:all()"
    
    def func(self):
        from .items import Restraint
        
        restraints = [obj for obj in self.caller.contents 
                     if isinstance(obj, Restraint) and obj.worn_by]
        
        if not restraints:
            self.caller.msg("You're not restrained.")
            return
        
        for r in restraints:
            success, msg = r.struggle(self.caller)
            self.caller.msg(msg)
            if success:
                r.location = self.caller.location  # Drop on floor
                self.caller.location.msg_contents(
                    f"{self.caller.key} struggles free of {r.key}!",
                    exclude=[self.caller]
                )
                return
        
        self.caller.location.msg_contents(
            f"{self.caller.key} struggles against their restraints.",
            exclude=[self.caller]
        )


# =============================================================================
# GAG COMMANDS
# =============================================================================

class CmdGag(Command):
    """
    Gag someone.
    
    Usage:
        gag <target>
        gag <target> with <gag>
    """
    
    key = "gag"
    locks = "cmd:all()"
    
    def parse(self):
        args = self.args.strip()
        self.target_name = ""
        self.item_name = ""
        
        if " with " in args:
            parts = args.split(" with ", 1)
            self.target_name = parts[0].strip()
            self.item_name = parts[1].strip()
        else:
            self.target_name = args
    
    def func(self):
        from .items import Gag
        
        if not self.target_name:
            self.caller.msg("Gag who?")
            return
        
        target = find_target(self.caller, self.target_name)
        if not target:
            self.caller.msg(f"Can't find '{self.target_name}'.")
            return
        
        gag = None
        if self.item_name:
            gag = self.caller.search(self.item_name, location=self.caller)
        else:
            for obj in self.caller.contents:
                if isinstance(obj, Gag) and not obj.worn_by:
                    gag = obj
                    break
        
        if not gag or not isinstance(gag, Gag):
            self.caller.msg("You're not holding a gag.")
            return
        
        existing = find_item_on_char(target, "gag", "mouth")
        if existing:
            self.caller.msg(f"{target.key} is already gagged.")
            return
        
        success, msg = gag.wear(target)
        
        if success:
            self.caller.msg(f"You push {gag.key} into {target.key}'s mouth.")
            target.msg(f"{self.caller.key} pushes {gag.key} into your mouth!")
        else:
            self.caller.msg(msg)


class CmdUngag(Command):
    """
    Remove a gag.
    
    Usage:
        ungag <target>
    """
    
    key = "ungag"
    locks = "cmd:all()"
    
    def func(self):
        target_name = self.args.strip()
        
        if not target_name:
            self.caller.msg("Ungag who?")
            return
        
        target = find_target(self.caller, target_name)
        if not target:
            self.caller.msg(f"Can't find '{target_name}'.")
            return
        
        gag = find_item_on_char(target, "gag", "mouth")
        if not gag:
            self.caller.msg(f"{target.key} isn't gagged.")
            return
        
        success, msg = gag.remove()
        
        if success:
            gag.location = self.caller
            self.caller.msg(f"You remove {target.key}'s gag.")
            target.msg(f"{self.caller.key} removes your gag. You can speak again!")
        else:
            self.caller.msg(msg)


# =============================================================================
# BLINDFOLD COMMANDS
# =============================================================================

class CmdBlindfold(Command):
    """
    Blindfold someone.
    
    Usage:
        blindfold <target>
        blindfold <target> with <blindfold>
    """
    
    key = "blindfold"
    locks = "cmd:all()"
    
    def parse(self):
        args = self.args.strip()
        self.target_name = ""
        self.item_name = ""
        
        if " with " in args:
            parts = args.split(" with ", 1)
            self.target_name = parts[0].strip()
            self.item_name = parts[1].strip()
        else:
            self.target_name = args
    
    def func(self):
        from .items import Blindfold
        
        if not self.target_name:
            self.caller.msg("Blindfold who?")
            return
        
        target = find_target(self.caller, self.target_name)
        if not target:
            self.caller.msg(f"Can't find '{self.target_name}'.")
            return
        
        item = None
        if self.item_name:
            item = self.caller.search(self.item_name, location=self.caller)
        else:
            for obj in self.caller.contents:
                if isinstance(obj, Blindfold) and not obj.worn_by:
                    item = obj
                    break
        
        if not item or not isinstance(item, Blindfold):
            self.caller.msg("You're not holding a blindfold.")
            return
        
        existing = find_item_on_char(target, "blindfold", "eyes")
        if existing:
            self.caller.msg(f"{target.key} is already blindfolded.")
            return
        
        success, msg = item.wear(target)
        
        if success:
            self.caller.msg(f"You cover {target.key}'s eyes with {item.key}.")
            target.msg(f"{self.caller.key} covers your eyes. Everything goes dark!")
        else:
            self.caller.msg(msg)


class CmdUnblindfold(Command):
    """
    Remove a blindfold.
    
    Usage:
        unblindfold <target>
    """
    
    key = "unblindfold"
    locks = "cmd:all()"
    
    def func(self):
        target_name = self.args.strip()
        
        if not target_name:
            self.caller.msg("Unblindfold who?")
            return
        
        target = find_target(self.caller, target_name)
        if not target:
            self.caller.msg(f"Can't find '{target_name}'.")
            return
        
        item = find_item_on_char(target, "blindfold", "eyes")
        if not item:
            self.caller.msg(f"{target.key} isn't blindfolded.")
            return
        
        success, msg = item.remove()
        
        if success:
            item.location = self.caller
            self.caller.msg(f"You remove {target.key}'s blindfold.")
            target.msg(f"{self.caller.key} removes your blindfold. Light floods your vision!")
        else:
            self.caller.msg(msg)


# =============================================================================
# LOCK COMMANDS
# =============================================================================

class CmdLockItem(Command):
    """
    Lock an item (collar, restraints, etc).
    
    Usage:
        lock <item>
        lock <target>'s collar
    """
    
    key = "lock"
    locks = "cmd:all()"
    
    def func(self):
        args = self.args.strip()
        
        if not args:
            self.caller.msg("Lock what?")
            return
        
        # Check if targeting someone's item
        if "'s " in args.lower():
            parts = args.split("'s ", 1)
            target_name = parts[0]
            item_hint = parts[1].strip() if len(parts) > 1 else ""
            
            target = find_target(self.caller, target_name)
            if not target:
                self.caller.msg(f"Can't find '{target_name}'.")
                return
            
            item = None
            for obj in target.contents:
                if hasattr(obj, 'is_lockable') and obj.is_lockable:
                    if not item_hint or item_hint.lower() in obj.key.lower():
                        item = obj
                        break
            
            if not item:
                self.caller.msg(f"Can't find a lockable item on {target.key}.")
                return
        else:
            item = self.caller.search(args, location=self.caller)
            if not item:
                return
        
        if not hasattr(item, 'lock'):
            self.caller.msg(f"{item.key} can't be locked.")
            return
        
        success, msg = item.lock()
        self.caller.msg(msg)


class CmdUnlockItem(Command):
    """
    Unlock an item.
    
    Usage:
        unlock <item>
        unlock <target>'s collar
    """
    
    key = "unlock"
    locks = "cmd:all()"
    
    def func(self):
        args = self.args.strip()
        
        if not args:
            self.caller.msg("Unlock what?")
            return
        
        if "'s " in args.lower():
            parts = args.split("'s ", 1)
            target_name = parts[0]
            item_hint = parts[1].strip() if len(parts) > 1 else ""
            
            target = find_target(self.caller, target_name)
            if not target:
                self.caller.msg(f"Can't find '{target_name}'.")
                return
            
            item = None
            for obj in target.contents:
                if hasattr(obj, 'is_locked') and obj.is_locked:
                    if not item_hint or item_hint.lower() in obj.key.lower():
                        item = obj
                        break
            
            if not item:
                self.caller.msg(f"Can't find a locked item on {target.key}.")
                return
        else:
            item = self.caller.search(args, location=self.caller)
            if not item:
                return
        
        if not hasattr(item, 'unlock'):
            self.caller.msg(f"{item.key} can't be unlocked.")
            return
        
        success, msg = item.unlock()
        self.caller.msg(msg)


# =============================================================================
# SHOCK COMMAND
# =============================================================================

class CmdShock(Command):
    """
    Activate a shock collar.
    
    Usage:
        shock <target>
        shock <target> <1-3>
    """
    
    key = "shock"
    aliases = ["zap"]
    locks = "cmd:all()"
    
    def func(self):
        args = self.args.split()
        
        if not args:
            self.caller.msg("Shock who?")
            return
        
        target_name = args[0]
        intensity = 1
        if len(args) > 1:
            try:
                intensity = int(args[1])
            except ValueError:
                intensity = 1
        
        target = find_target(self.caller, target_name)
        if not target:
            self.caller.msg(f"Can't find '{target_name}'.")
            return
        
        from .items import Collar
        collar = find_item_on_char(target, "collar", "neck")
        
        if not collar or not isinstance(collar, Collar):
            self.caller.msg(f"{target.key} isn't wearing a collar.")
            return
        
        if not collar.has_shock:
            self.caller.msg(f"{target.key}'s collar doesn't have a shock function.")
            return
        
        msg = collar.trigger_shock(intensity)
        if msg:
            self.caller.location.msg_contents(msg)
        else:
            self.caller.msg("Nothing happens.")


# =============================================================================
# CMDSET
# =============================================================================

class ItemCmdSet(CmdSet):
    """Commands for item interaction."""
    
    key = "ItemCmdSet"
    
    def at_cmdset_creation(self):
        self.add(CmdCollar())
        self.add(CmdUncollar())
        self.add(CmdTag())
        self.add(CmdLeash())
        self.add(CmdUnleash())
        self.add(CmdTug())
        self.add(CmdUse())
        self.add(CmdVibrate())
        self.add(CmdInflate())
        self.add(CmdDeflate())
        self.add(CmdRestrain())
        self.add(CmdFree())
        self.add(CmdStruggle())
        self.add(CmdGag())
        self.add(CmdUngag())
        self.add(CmdBlindfold())
        self.add(CmdUnblindfold())
        self.add(CmdLockItem())
        self.add(CmdUnlockItem())
        self.add(CmdShock())


__all__ = [
    "ItemCmdSet",
    "CmdCollar", "CmdUncollar", "CmdTag",
    "CmdLeash", "CmdUnleash", "CmdTug",
    "CmdUse", "CmdVibrate", "CmdInflate", "CmdDeflate",
    "CmdRestrain", "CmdFree", "CmdStruggle",
    "CmdGag", "CmdUngag",
    "CmdBlindfold", "CmdUnblindfold",
    "CmdLockItem", "CmdUnlockItem", "CmdShock",
]
