"""
Housing Commands
================

Player commands for the housing system.

Commands:
- home          - Go home or view home info
- home buy      - Purchase a home
- home upgrade  - Upgrade home type or add rooms
- home edit     - Customize descriptions
- home perms    - Manage permissions
- home lock     - Lock/unlock door
- knock         - Knock on someone's door
- invite        - Invite someone in
- kick          - Remove someone from your home
"""

from evennia import Command, CmdSet
from evennia.utils.search import search_object
from world.housing import (
    # Core
    get_home, has_home, create_home, upgrade_home, add_room, purchase_upgrade,
    get_all_home_rooms, get_home_type,
    # Permissions
    get_permission_level, can_enter, set_permission, invite_visitor,
    revoke_visitor, kick_from_home,
    # Customization
    set_home_name, set_room_description, lock_home,
    # Display
    get_home_info, get_permission_list, list_available_homes,
    list_available_rooms, list_available_upgrades,
    # Constants
    HOME_TYPES, ROOM_TYPES, UPGRADES, PERMISSION_LEVELS,
)
from world.currency import balance


class CmdHome(Command):
    """
    Go home or manage your home.
    
    Usage:
      home                  - Go to your home (or view info if already there)
      home info             - View detailed home information
      home buy <type>       - Purchase a home
      home upgrade <type>   - Upgrade to a better home type
      home addroom <type>   - Add a new room
      home buyupgrade <key> - Purchase an upgrade
      home name <new name>  - Rename your home
      home desc             - Set room description (interactive)
      home lock             - Lock your home
      home unlock           - Unlock your home
      home perms            - View permissions
      home perms <name> <level> - Set someone's permission level
      home invite <name>    - Invite someone to enter
      home kick <name>      - Kick someone out
      
    Permission levels: banned, stranger, visitor, guest, trusted, resident
    
    Examples:
      home buy cottage
      home addroom bedroom
      home perms Alice trusted
      home invite Bob
    """
    
    key = "home"
    aliases = ["house", "housing"]
    locks = "cmd:all()"
    help_category = "Housing"
    
    def func(self):
        caller = self.caller
        args = self.args.strip().split()
        
        if not args:
            # No args - go home or show info
            self.go_home()
            return
        
        subcmd = args[0].lower()
        subargs = args[1:] if len(args) > 1 else []
        
        if subcmd == "info":
            self.show_info()
        elif subcmd == "buy":
            self.buy_home(subargs)
        elif subcmd == "upgrade":
            self.upgrade_type(subargs)
        elif subcmd == "addroom":
            self.add_room(subargs)
        elif subcmd == "buyupgrade":
            self.buy_upgrade(subargs)
        elif subcmd == "name":
            self.set_name(subargs)
        elif subcmd == "desc":
            self.set_desc()
        elif subcmd == "lock":
            self.lock_door(True)
        elif subcmd == "unlock":
            self.lock_door(False)
        elif subcmd == "perms":
            if subargs:
                self.set_perm(subargs)
            else:
                self.show_perms()
        elif subcmd == "invite":
            self.invite(subargs)
        elif subcmd == "kick":
            self.kick(subargs)
        elif subcmd == "types":
            self.caller.msg(list_available_homes())
        elif subcmd == "rooms":
            self.list_rooms()
        elif subcmd == "upgrades":
            self.list_upgrades()
        else:
            self.caller.msg(f"Unknown subcommand: {subcmd}. See 'help home'.")
    
    def go_home(self):
        """Teleport home or show info if already there."""
        home = get_home(self.caller)
        
        if not home:
            self.caller.msg("You don't have a home. Use 'home buy <type>' to purchase one.")
            self.caller.msg("Use 'home types' to see available homes.")
            return
        
        # Check if already home
        current = self.caller.location
        if current and current.db.is_home:
            # Get the main home
            if current.db.is_home_room:
                main_home = search_object("#" + str(current.db.parent_home_id))
                main_home = main_home[0] if main_home else None
            else:
                main_home = current
            
            if main_home and main_home.db.owner_id == self.caller.id:
                # Already home - show info
                self.caller.msg(get_home_info(home))
                return
        
        # Go home
        self.caller.msg("You head home...")
        self.caller.move_to(home, quiet=False)
    
    def show_info(self):
        """Show home information."""
        home = get_home(self.caller)
        if not home:
            self.caller.msg("You don't have a home.")
            return
        self.caller.msg(get_home_info(home))
    
    def buy_home(self, args):
        """Purchase a home."""
        if has_home(self.caller):
            self.caller.msg("You already own a home. Use 'home upgrade' to upgrade it.")
            return
        
        if not args:
            self.caller.msg("Usage: home buy <type>")
            self.caller.msg(list_available_homes())
            return
        
        home_type = args[0].lower()
        
        if home_type not in HOME_TYPES:
            self.caller.msg(f"Unknown home type: {home_type}")
            self.caller.msg(f"Available types: {', '.join(HOME_TYPES.keys())}")
            return
        
        success, msg, home = create_home(self.caller, home_type)
        self.caller.msg(msg)
        
        if success:
            self.caller.msg("Use 'home' to visit your new home!")
    
    def upgrade_type(self, args):
        """Upgrade home to better type."""
        home = get_home(self.caller)
        if not home:
            self.caller.msg("You don't have a home to upgrade.")
            return
        
        if not args:
            self.caller.msg("Usage: home upgrade <type>")
            self.caller.msg(f"Current type: {home.db.home_type}")
            self.caller.msg(list_available_homes())
            return
        
        new_type = args[0].lower()
        success, msg = upgrade_home(self.caller, new_type)
        self.caller.msg(msg)
    
    def add_room(self, args):
        """Add a new room."""
        home = get_home(self.caller)
        if not home:
            self.caller.msg("You don't have a home.")
            return
        
        if not args:
            self.caller.msg("Usage: home addroom <type>")
            self.caller.msg(list_available_rooms(home))
            return
        
        room_type = args[0].lower()
        success, msg, room = add_room(self.caller, room_type)
        self.caller.msg(msg)
    
    def buy_upgrade(self, args):
        """Purchase an upgrade."""
        home = get_home(self.caller)
        if not home:
            self.caller.msg("You don't have a home.")
            return
        
        if not args:
            self.caller.msg("Usage: home buyupgrade <key>")
            self.caller.msg(list_available_upgrades(home))
            return
        
        upgrade_key = args[0].lower()
        success, msg = purchase_upgrade(self.caller, upgrade_key)
        self.caller.msg(msg)
    
    def set_name(self, args):
        """Rename home."""
        home = get_home(self.caller)
        if not home:
            self.caller.msg("You don't have a home.")
            return
        
        if not args:
            self.caller.msg("Usage: home name <new name>")
            return
        
        new_name = " ".join(args)
        success, msg = set_home_name(home, self.caller, new_name)
        self.caller.msg(msg)
    
    def set_desc(self):
        """Set room description - interactive."""
        room = self.caller.location
        if not room or not room.db.is_home:
            self.caller.msg("You need to be in your home to edit its description.")
            return
        
        self.caller.msg("|wEnter the new room description (end with @@ on a new line):|n")
        
        # Use EvMenu or a simple input handler
        from evennia.utils.eveditor import EvEditor
        
        def save_desc(caller, buffer):
            text = "\n".join(buffer)
            success, msg = set_room_description(room, caller, text)
            caller.msg(msg)
        
        def quit_editor(caller):
            caller.msg("Description editing cancelled.")
        
        EvEditor(
            self.caller,
            loadfunc=lambda c: room.db.desc or "",
            savefunc=save_desc,
            quitfunc=quit_editor,
            key="Room Description"
        )
    
    def lock_door(self, lock):
        """Lock or unlock home."""
        home = get_home(self.caller)
        if not home:
            self.caller.msg("You don't have a home.")
            return
        
        success, msg = lock_home(home, self.caller, lock)
        self.caller.msg(msg)
    
    def show_perms(self):
        """Show permissions."""
        home = get_home(self.caller)
        if not home:
            self.caller.msg("You don't have a home.")
            return
        self.caller.msg(get_permission_list(home))
    
    def set_perm(self, args):
        """Set someone's permission level."""
        home = get_home(self.caller)
        if not home:
            self.caller.msg("You don't have a home.")
            return
        
        if len(args) < 2:
            self.caller.msg("Usage: home perms <name> <level>")
            self.caller.msg(f"Levels: {', '.join(PERMISSION_LEVELS.keys())}")
            return
        
        target_name = args[0]
        level = args[1].lower()
        
        # Find target
        target = self.caller.search(target_name, global_search=True)
        if not target:
            return
        
        success, msg = set_permission(home, self.caller, target, level)
        self.caller.msg(msg)
    
    def invite(self, args):
        """Invite someone to enter."""
        home = get_home(self.caller)
        if not home:
            self.caller.msg("You don't have a home.")
            return
        
        if not args:
            self.caller.msg("Usage: home invite <name>")
            return
        
        target_name = args[0]
        target = self.caller.search(target_name, global_search=True)
        if not target:
            return
        
        success, msg = invite_visitor(home, self.caller, target)
        self.caller.msg(msg)
        
        if success:
            target.msg(f"{self.caller.key} has invited you to their home.")
    
    def kick(self, args):
        """Kick someone from home."""
        home = get_home(self.caller)
        if not home:
            self.caller.msg("You don't have a home.")
            return
        
        if not args:
            self.caller.msg("Usage: home kick <name>")
            return
        
        target_name = args[0]
        target = self.caller.search(target_name, global_search=True)
        if not target:
            return
        
        success, msg = kick_from_home(home, self.caller, target)
        self.caller.msg(msg)
    
    def list_rooms(self):
        """List available room types."""
        home = get_home(self.caller)
        if not home:
            self.caller.msg("You don't have a home.")
            return
        self.caller.msg(list_available_rooms(home))
    
    def list_upgrades(self):
        """List available upgrades."""
        home = get_home(self.caller)
        if not home:
            self.caller.msg("You don't have a home.")
            return
        self.caller.msg(list_available_upgrades(home))


class CmdKnock(Command):
    """
    Knock on someone's door.
    
    Usage:
      knock <home name or owner name>
      
    The owner (if online and home) will be notified.
    """
    
    key = "knock"
    locks = "cmd:all()"
    help_category = "Housing"
    
    def func(self):
        if not self.args:
            self.caller.msg("Knock on whose home?")
            return
        
        # Search for a home by name or owner
        search_term = self.args.strip()
        
        # Try to find by home name first
        results = search_object(search_term)
        home = None
        
        for obj in results:
            if hasattr(obj, 'db') and obj.db.is_home and not obj.db.is_home_room:
                home = obj
                break
        
        # Try by owner name
        if not home:
            owner = self.caller.search(search_term, global_search=True)
            if owner:
                home = get_home(owner)
        
        if not home:
            self.caller.msg(f"Couldn't find a home matching '{search_term}'.")
            return
        
        # Check if already inside
        if self.caller.location == home:
            self.caller.msg("You're already inside!")
            return
        
        # Knock
        self.caller.msg(f"You knock on the door of {home.db.home_name}.")
        
        # Notify owner if online and home
        owner_id = home.db.owner_id
        for obj in home.contents:
            if hasattr(obj, 'id') and obj.id == owner_id:
                obj.msg(f"|y{self.caller.key} is knocking at your door.|n")
                break
        
        # Also notify anyone else in the home
        for obj in home.contents:
            if hasattr(obj, 'msg') and obj != self.caller:
                if not (hasattr(obj, 'id') and obj.id == owner_id):
                    obj.msg(f"Someone is knocking at the door.")


class CmdEnterHome(Command):
    """
    Enter someone's home.
    
    Usage:
      enter <home name or owner name>
      
    You must have permission to enter.
    """
    
    key = "enter"
    locks = "cmd:all()"
    help_category = "Housing"
    
    def func(self):
        if not self.args:
            self.caller.msg("Enter whose home?")
            return
        
        search_term = self.args.strip()
        
        # Try to find by home name first
        results = search_object(search_term)
        home = None
        
        for obj in results:
            if hasattr(obj, 'db') and obj.db.is_home and not obj.db.is_home_room:
                home = obj
                break
        
        # Try by owner name
        if not home:
            owner = self.caller.search(search_term, global_search=True)
            if owner:
                home = get_home(owner)
        
        if not home:
            self.caller.msg(f"Couldn't find a home matching '{search_term}'.")
            return
        
        # Check if already inside
        current = self.caller.location
        if current and current.db.is_home:
            if current.db.is_home_room:
                parent_id = current.db.parent_home_id
            else:
                parent_id = current.id
            
            if parent_id == home.id:
                self.caller.msg("You're already in this home!")
                return
        
        # Check permission
        allowed, reason = can_enter(home, self.caller)
        
        if not allowed:
            self.caller.msg(reason or "You can't enter this home.")
            return
        
        # Enter
        self.caller.msg(f"You enter {home.db.home_name}.")
        self.caller.move_to(home, quiet=False)
        
        # Clear visitor status after entering
        visitors = home.db.visitors_allowed or []
        if self.caller.id in visitors:
            visitors.remove(self.caller.id)
            home.db.visitors_allowed = visitors


class CmdInvite(Command):
    """
    Invite someone into your home.
    
    Usage:
      invite <name>
      
    Must be used while you're in your home.
    The invited person can then use 'enter' to come in.
    """
    
    key = "invite"
    locks = "cmd:all()"
    help_category = "Housing"
    
    def func(self):
        if not self.args:
            self.caller.msg("Invite who?")
            return
        
        # Must be in a home
        room = self.caller.location
        if not room or not room.db.is_home:
            self.caller.msg("You need to be in your home to invite someone.")
            return
        
        # Get main home
        if room.db.is_home_room:
            home = search_object("#" + str(room.db.parent_home_id))
            home = home[0] if home else None
        else:
            home = room
        
        if not home:
            self.caller.msg("Error finding home.")
            return
        
        target = self.caller.search(self.args.strip(), global_search=True)
        if not target:
            return
        
        success, msg = invite_visitor(home, self.caller, target)
        self.caller.msg(msg)
        
        if success:
            target.msg(f"|y{self.caller.key} has invited you to enter {home.db.home_name}.|n")
            target.msg(f"Use 'enter {home.db.home_name}' to enter.")


class CmdLeaveHome(Command):
    """
    Leave the home you're currently in.
    
    Usage:
      leave
      
    Returns you to the Grove.
    """
    
    key = "leave"
    aliases = ["exit home", "go outside"]
    locks = "cmd:all()"
    help_category = "Housing"
    
    def func(self):
        room = self.caller.location
        if not room or not room.db.is_home:
            self.caller.msg("You're not in a home.")
            return
        
        # Find the Grove or default exit
        exit_location = search_object("The Grove", typeclass="typeclasses.rooms.Room")
        if exit_location:
            exit_location = exit_location[0]
        else:
            self.caller.msg("Error: No exit location defined.")
            return
        
        self.caller.msg("You leave the home.")
        self.caller.move_to(exit_location, quiet=False)


class CmdVisit(Command):
    """
    Visit someone's home (if you have permission).
    
    Usage:
      visit <player name>
      
    You must be a guest, trusted, or resident to visit.
    """
    
    key = "visit"
    locks = "cmd:all()"
    help_category = "Housing"
    
    def func(self):
        if not self.args:
            self.caller.msg("Visit whose home?")
            return
        
        target = self.caller.search(self.args.strip(), global_search=True)
        if not target:
            return
        
        home = get_home(target)
        if not home:
            self.caller.msg(f"{target.key} doesn't have a home.")
            return
        
        # Check permission
        allowed, reason = can_enter(home, self.caller)
        
        if not allowed:
            self.caller.msg(reason or "You don't have permission to visit.")
            return
        
        self.caller.msg(f"You visit {home.db.home_name}...")
        self.caller.move_to(home, quiet=False)


# =============================================================================
# COMMAND SET
# =============================================================================

class HousingCmdSet(CmdSet):
    """Housing commands."""
    
    key = "housing_commands"
    
    def at_cmdset_creation(self):
        self.add(CmdHome())
        self.add(CmdKnock())
        self.add(CmdEnterHome())
        self.add(CmdInvite())
        self.add(CmdLeaveHome())
        self.add(CmdVisit())


# =============================================================================
# INSTALLATION HELPER
# =============================================================================

def install_housing_commands():
    """
    Add housing commands to the default character cmdset.
    
    Add to your Character typeclass:
        from commands.housing_commands import HousingCmdSet
        self.cmdset.add(HousingCmdSet, persistent=True)
    
    Or call this function with a character:
        install_housing_commands()
    """
    print("""
To install housing commands, add to your Character typeclass's at_object_creation:

    from commands.housing_commands import HousingCmdSet
    self.cmdset.add(HousingCmdSet, persistent=True)

Or add to your default command set in commands/default_cmdsets.py:

    from commands.housing_commands import HousingCmdSet
    
    class CharacterCmdSet(default_cmds.CharacterCmdSet):
        def at_cmdset_creation(self):
            super().at_cmdset_creation()
            self.add(HousingCmdSet)
""")
