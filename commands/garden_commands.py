"""
Garden of Knowledge Commands

Commands for interacting with the Garden of Knowledge room:
- desk write/read/clean/soil
- browse <section> for bookshelves

Add to your default cmdset or create a room-based cmdset.
"""

from evennia import Command, CmdSet


class CmdDesk(Command):
    """
    Interact with the root desk in the Garden of Knowledge.
    
    Usage:
        desk                    - Look at the desk
        desk write <message>    - Leave a note on the desk
        desk read               - Read notes on the desk
        desk clean              - Clean the desk one step
        desk clean/full         - Clean the desk completely
        desk soil               - Make the desk messier (after activity)
    """
    
    key = "desk"
    aliases = ["rootdesk", "root desk"]
    locks = "cmd:all()"
    help_category = "Garden"
    
    def func(self):
        caller = self.caller
        
        # Find the desk in the room
        from world.build_garden_knowledge import RootDesk
        
        desk = None
        if caller.location:
            for obj in caller.location.contents:
                if isinstance(obj, RootDesk):
                    desk = obj
                    break
        
        if not desk:
            caller.msg("There's no desk here.")
            return
        
        # No args - just look at the desk
        if not self.args and not self.switches:
            caller.msg(desk.return_appearance(caller))
            return
        
        args = self.args.strip() if self.args else ""
        
        # Parse subcommand
        if args.startswith("write "):
            # desk write <message>
            message = args[6:].strip()
            if not message:
                caller.msg("Write what? Usage: desk write <message>")
                return
            
            desk.add_note(caller, message)
            caller.msg("You scribble a note on the desk.")
            
            # Notify others
            if caller.location:
                caller.location.msg_contents(
                    f"{caller.key} writes something on the desk.",
                    exclude=[caller]
                )
        
        elif args == "read":
            # desk read
            caller.msg(desk.read_notes())
        
        elif args == "clean":
            # desk clean
            if "full" in self.switches:
                result = desk.clean_fully()
            else:
                result = desk.clean()
            caller.msg(result)
            
            if caller.location:
                caller.location.msg_contents(
                    f"{caller.key} tidies up the desk.",
                    exclude=[caller]
                )
        
        elif args == "soil":
            # desk soil (make messier)
            result = desk.soil()
            caller.msg(result)
        
        else:
            # Unknown subcommand
            caller.msg(
                "Usage: desk [write <message>|read|clean|soil]\n"
                "Or just 'desk' to look at it."
            )


class CmdBrowse(Command):
    """
    Browse a section of the bookshelves.
    
    Usage:
        browse                  - List available sections
        browse <section>        - Read about a section
        
    Sections:
        grimoires   - Magical tomes and spell books
        science     - History, biology, reference
        fiction     - Novels, fairy tales, stories
        hentai      - The MLP section. For unknown reasons.
    """
    
    key = "browse"
    aliases = ["section", "shelf"]
    locks = "cmd:all()"
    help_category = "Garden"
    
    def func(self):
        caller = self.caller
        
        # Find bookshelves in the room
        from world.build_garden_knowledge import LivingBookshelves
        
        shelves = None
        if caller.location:
            for obj in caller.location.contents:
                if isinstance(obj, LivingBookshelves):
                    shelves = obj
                    break
        
        if not shelves:
            caller.msg("There are no bookshelves here to browse.")
            return
        
        if not self.args:
            # List sections
            caller.msg(f"|wAvailable sections:|n {shelves.list_sections()}")
            caller.msg("Use 'browse <section>' to examine one.")
            return
        
        section_name = self.args.strip().lower()
        desc = shelves.get_section(section_name)
        
        if desc:
            caller.msg(f"|w{section_name.title()} Section|n\n\n{desc}")
        else:
            caller.msg(
                f"No section called '{section_name}'. "
                f"Available: {shelves.list_sections()}"
            )


class CmdWriteDesk(Command):
    """
    Shortcut to write a note on the desk.
    
    Usage:
        write <message>     - If at desk, leaves a note
        
    Note: If you're holding a book, this will write in the book instead.
    This command only works if no book is in inventory.
    """
    
    key = "write"
    locks = "cmd:all()"
    help_category = "Garden"
    # Lower priority so book write takes precedence
    priority = -1
    
    def func(self):
        caller = self.caller
        
        # Check if holding a WritableBook - if so, let book command handle it
        try:
            from typeclasses.objects.aurias_objects import WritableBook
            books = [obj for obj in caller.contents if isinstance(obj, WritableBook)]
            if books:
                # Has a book - this command shouldn't fire, but just in case
                caller.msg("You're holding a book. Use 'write' to write in it.")
                return
        except ImportError:
            pass
        
        # No book - try desk
        if not self.args:
            caller.msg("Write what?")
            return
        
        # Find desk
        from world.build_garden_knowledge import RootDesk
        
        desk = None
        if caller.location:
            for obj in caller.location.contents:
                if isinstance(obj, RootDesk):
                    desk = obj
                    break
        
        # Also check for AuriasJournal
        journal = None
        if caller.location:
            try:
                from typeclasses.objects.aurias_objects import AuriasJournal
                for obj in caller.location.contents:
                    if isinstance(obj, AuriasJournal):
                        journal = obj
                        break
            except ImportError:
                pass
        
        if desk:
            desk.add_note(caller, self.args.strip())
            caller.msg("You scribble a note on the desk.")
            if caller.location:
                caller.location.msg_contents(
                    f"{caller.key} writes something on the desk.",
                    exclude=[caller]
                )
        elif journal:
            journal.add_entry(caller, self.args.strip())
            caller.msg("You add your words to the journal.")
            if caller.location:
                caller.location.msg_contents(
                    f"{caller.key} writes in the journal.",
                    exclude=[caller]
                )
        else:
            caller.msg("There's nothing here to write on.")


class GardenCmdSet(CmdSet):
    """
    Commands for Garden of Knowledge.
    
    Add to default cmdset:
        from commands.garden_commands import GardenCmdSet
        self.add(GardenCmdSet)
    """
    
    key = "garden"
    priority = 1
    
    def at_cmdset_creation(self):
        self.add(CmdDesk())
        self.add(CmdBrowse())
        self.add(CmdWriteDesk())
