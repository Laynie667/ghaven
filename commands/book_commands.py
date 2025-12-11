"""
Book Commands for Gilderhaven

Commands for creating, writing, reading, and managing writable books.
Works with WritableBook typeclass from typeclasses/objects/aurias_objects.py
(or wherever you place it).
"""

from evennia import Command, CmdSet


class CmdNewBook(Command):
    """
    Create a new blank book.
    
    Usage:
        newbook <title>
        
    Creates a writable book in your inventory. You can then write in it,
    add pages, and eventually shelve it somewhere.
    """
    key = "newbook"
    aliases = ["createbook", "makebook"]
    locks = "cmd:all()"
    
    def func(self):
        caller = self.caller
        
        if not self.args:
            caller.msg("Usage: newbook <title>")
            return
        
        title = self.args.strip()[:100]  # Cap length
        
        # Import here to avoid circular imports
        from typeclasses.objects.aurias_objects import create_writable_book
        
        book = create_writable_book(author=caller, title=title, location=caller)
        caller.msg(f"You create a new book titled '|w{title}|n'. It has one blank page.")


class CmdWriteBook(Command):
    """
    Write in a book you're holding.
    
    Usage:
        write <text>
        write/page <num> = <text>
        write/append <text>
        
    Writes to the current page of the book you're holding.
    Use /page to write to a specific page number.
    Use /append to add to existing text instead of replacing.
    """
    key = "write"
    aliases = ["writebook"]
    locks = "cmd:all()"
    
    def func(self):
        caller = self.caller
        
        # Find a book in inventory
        from typeclasses.objects.aurias_objects import WritableBook
        books = [obj for obj in caller.contents if isinstance(obj, WritableBook)]
        
        if not books:
            caller.msg("You're not holding a book to write in.")
            return
        
        book = books[0]  # Use first book found
        
        if not self.args:
            caller.msg(f"Usage: write <text>")
            caller.msg(f"Currently editing: '{book.book_title}' (page {book.current_page + 1})")
            return
        
        # Parse switches
        if "page" in self.switches:
            # write/page 2 = Some text here
            if "=" not in self.args:
                caller.msg("Usage: write/page <num> = <text>")
                return
            page_str, text = self.args.split("=", 1)
            try:
                page_num = int(page_str.strip()) - 1  # Convert to 0-indexed
            except ValueError:
                caller.msg("Page number must be a number.")
                return
            success, msg = book.write_page(text.strip(), page_num, caller)
        elif "append" in self.switches:
            success, msg = book.append_to_page(self.args.strip(), writer=caller)
        else:
            success, msg = book.write_page(self.args.strip(), writer=caller)
        
        caller.msg(msg)


class CmdReadBook(Command):
    """
    Read a book.
    
    Usage:
        read <book>
        read/page <num>
        
    Reads from a book in your inventory or the room.
    """
    key = "read"
    aliases = ["readbook"]
    locks = "cmd:all()"
    
    def func(self):
        caller = self.caller
        
        from typeclasses.objects.aurias_objects import WritableBook
        
        book = None
        
        if self.args:
            # Search inventory and room
            book = caller.search(self.args.strip(), 
                                 candidates=list(caller.contents) + list(caller.location.contents))
            if not book:
                return
            if not isinstance(book, WritableBook):
                caller.msg("That's not a readable book.")
                return
        else:
            # Default to first book in inventory
            books = [obj for obj in caller.contents if isinstance(obj, WritableBook)]
            if not books:
                caller.msg("You're not holding a book. Specify which book to read.")
                return
            book = books[0]
        
        # Handle page switch
        if "page" in self.switches:
            try:
                page_num = int(self.args.strip())
                success, msg = book.goto_page(page_num)
                caller.msg(msg)
                return
            except ValueError:
                pass
        
        caller.msg(book.read_page())


class CmdTurnPage(Command):
    """
    Turn to the next or previous page.
    
    Usage:
        turn
        turn next
        turn back
        turn <page number>
        
    Navigates through the book you're holding.
    """
    key = "turn"
    aliases = ["flip", "page"]
    locks = "cmd:all()"
    
    def func(self):
        caller = self.caller
        
        from typeclasses.objects.aurias_objects import WritableBook
        books = [obj for obj in caller.contents if isinstance(obj, WritableBook)]
        
        if not books:
            caller.msg("You're not holding a book.")
            return
        
        book = books[0]
        
        args = self.args.strip().lower() if self.args else "next"
        
        if args in ("next", "forward", ""):
            success, msg = book.turn_page(1)
        elif args in ("back", "prev", "previous"):
            success, msg = book.turn_page(-1)
        else:
            # Try as page number
            try:
                page_num = int(args)
                success, msg = book.goto_page(page_num)
            except ValueError:
                caller.msg("Usage: turn [next|back|<page number>]")
                return
        
        caller.msg(msg)


class CmdAddPage(Command):
    """
    Add a blank page to your book.
    
    Usage:
        addpage
        
    Adds a new page and moves to it.
    """
    key = "addpage"
    aliases = ["newpage"]
    locks = "cmd:all()"
    
    def func(self):
        caller = self.caller
        
        from typeclasses.objects.aurias_objects import WritableBook
        books = [obj for obj in caller.contents if isinstance(obj, WritableBook)]
        
        if not books:
            caller.msg("You're not holding a book.")
            return
        
        success, msg = books[0].add_page()
        caller.msg(msg)


class CmdTitleBook(Command):
    """
    Set or change a book's title.
    
    Usage:
        title <new title>
        
    Changes the title of the book you're holding.
    """
    key = "title"
    aliases = ["titlebook", "rename"]
    locks = "cmd:all()"
    
    def func(self):
        caller = self.caller
        
        if not self.args:
            caller.msg("Usage: title <new title>")
            return
        
        from typeclasses.objects.aurias_objects import WritableBook
        books = [obj for obj in caller.contents if isinstance(obj, WritableBook)]
        
        if not books:
            caller.msg("You're not holding a book.")
            return
        
        success, msg = books[0].set_title(self.args.strip(), caller)
        caller.msg(msg)


class CmdFinishBook(Command):
    """
    Finish a book, locking it from further edits.
    
    Usage:
        finishbook
        
    Once finished, a book cannot be edited. This is permanent.
    """
    key = "finishbook"
    aliases = ["finish", "completebook"]
    locks = "cmd:all()"
    
    def func(self):
        caller = self.caller
        
        from typeclasses.objects.aurias_objects import WritableBook
        books = [obj for obj in caller.contents if isinstance(obj, WritableBook)]
        
        if not books:
            caller.msg("You're not holding a book.")
            return
        
        book = books[0]
        
        # Confirm
        if "confirm" not in self.switches:
            caller.msg(f"This will permanently lock '{book.book_title}' from further edits.")
            caller.msg("Use |wfinishbook/confirm|n to proceed.")
            return
        
        success, msg = book.finish_book(caller)
        caller.msg(msg)


class CmdShelveBook(Command):
    """
    Place a book on a bookcase.
    
    Usage:
        shelve <book>
        shelve <book> on <bookcase>
        
    Shelves a book from your inventory onto a bookcase in the room.
    """
    key = "shelve"
    aliases = ["shelvebook"]
    locks = "cmd:all()"
    
    def func(self):
        caller = self.caller
        
        if not self.args:
            caller.msg("Usage: shelve <book> [on <bookcase>]")
            return
        
        from typeclasses.objects.aurias_objects import WritableBook, AuriaBookcase
        
        # Parse "book on bookcase" syntax
        if " on " in self.args.lower():
            parts = self.args.lower().split(" on ", 1)
            book_name = parts[0].strip()
            case_name = parts[1].strip()
        else:
            book_name = self.args.strip()
            case_name = None
        
        # Find the book in inventory
        book = caller.search(book_name, candidates=list(caller.contents))
        if not book:
            return
        
        if not isinstance(book, WritableBook):
            caller.msg("That's not a book you can shelve.")
            return
        
        # Find bookcase
        if case_name:
            bookcase = caller.search(case_name, candidates=list(caller.location.contents))
        else:
            # Find any bookcase in room
            cases = [obj for obj in caller.location.contents if isinstance(obj, AuriaBookcase)]
            if not cases:
                caller.msg("There's no bookcase here to shelve books on.")
                return
            bookcase = cases[0]
        
        if not bookcase:
            return
        
        if not isinstance(bookcase, AuriaBookcase):
            caller.msg("You can't shelve books on that.")
            return
        
        success, msg = bookcase.shelve_book(book, caller)
        caller.msg(msg)
        
        if success:
            caller.location.msg_contents(
                f"{caller.key} slides a book onto the shelf.",
                exclude=[caller]
            )


class CmdTakeBook(Command):
    """
    Take a book from a bookcase.
    
    Usage:
        takebook <title>
        takebook <title> from <bookcase>
        
    Borrows a book from a bookcase.
    """
    key = "takebook"
    aliases = ["borrowbook", "getbook"]
    locks = "cmd:all()"
    
    def func(self):
        caller = self.caller
        
        if not self.args:
            caller.msg("Usage: takebook <title> [from <bookcase>]")
            return
        
        from typeclasses.objects.aurias_objects import AuriaBookcase
        
        # Parse "title from bookcase" syntax
        if " from " in self.args.lower():
            parts = self.args.lower().split(" from ", 1)
            book_title = parts[0].strip()
            case_name = parts[1].strip()
        else:
            book_title = self.args.strip()
            case_name = None
        
        # Find bookcase
        if case_name:
            bookcase = caller.search(case_name, candidates=list(caller.location.contents))
        else:
            cases = [obj for obj in caller.location.contents if isinstance(obj, AuriaBookcase)]
            if not cases:
                caller.msg("There's no bookcase here.")
                return
            bookcase = cases[0]
        
        if not bookcase:
            return
        
        if not isinstance(bookcase, AuriaBookcase):
            caller.msg("That's not a bookcase.")
            return
        
        success, msg, book = bookcase.take_book(book_title, caller)
        caller.msg(msg)
        
        if success:
            caller.location.msg_contents(
                f"{caller.key} takes a book from the shelf.",
                exclude=[caller]
            )


# =============================================================================
# Command Set
# =============================================================================

class BookCmdSet(CmdSet):
    """Commands for writable books."""
    
    key = "BookCmdSet"
    
    def at_cmdset_creation(self):
        self.add(CmdNewBook())
        self.add(CmdWriteBook())
        self.add(CmdReadBook())
        self.add(CmdTurnPage())
        self.add(CmdAddPage())
        self.add(CmdTitleBook())
        self.add(CmdFinishBook())
        self.add(CmdShelveBook())
        self.add(CmdTakeBook())
