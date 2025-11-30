"""
Position Commands
=================

Player-facing commands for initiating and managing sexual positions.

Commands:
    position <name> <target> [as <slot>] [on <furniture>] [= <flavor>]
    fuck <target> [<position>] [= <flavor>]
    mount <target> [= <flavor>]
    dismount
    positions [search] - List available positions
    accept - Accept a position invitation
    decline - Decline a position invitation
    
Examples:
    position missionary Elena
    position doggy Elena on bed = roughly, gripping her hips
    fuck Elena missionary
    fuck Elena = slow and deep
    mount Shadow  (for mounting a quadruped)
    positions oral  (search for oral positions)
"""

# Evennia imports
try:
    from evennia import Command, CmdSet
    from evennia.utils import evtable
    from evennia.utils.search import search_object
    if Command is None:
        raise ImportError("Evennia not configured")
    HAS_EVENNIA = True
except (ImportError, Exception):
    HAS_EVENNIA = False
    class Command:
        key = ""
        aliases = []
        locks = ""
        help_category = ""
        def parse(self): pass
        def func(self): pass
    class CmdSet:
        key = ""
        def at_cmdset_creation(self): pass
        def add(self, cmd): pass
    evtable = None
    def search_object(*args, **kwargs): return []

# These would be imported from your positions module
from typeclasses.positions import (
    PositionManager,
    POSITIONS,
    get_position,
    get_positions_by_tag,
    search_positions,
    BodyStructureType,
    SizeCategory,
    check_position_compatibility,
    get_compatible_positions,
    FurnitureType,
)


def get_room_manager(room):
    """Get or create the position manager for a room."""
    manager = getattr(room, "_position_manager", None)
    if manager is None:
        manager = PositionManager()
        room._position_manager = manager
    return manager


def get_character_structure(character):
    """Get the body structure type of a character."""
    # Check body system first
    body = getattr(character, "body", None)
    if body:
        structure = getattr(body, "structure", None)
        if structure:
            locomotion = getattr(structure, "locomotion", "bipedal")
            # Map locomotion to BodyStructureType
            mapping = {
                "bipedal": BodyStructureType.BIPEDAL,
                "digitigrade": BodyStructureType.DIGITIGRADE,
                "quadruped": BodyStructureType.QUADRUPED,
                "taur": BodyStructureType.TAUR,
                "serpentine": BodyStructureType.SERPENTINE,
                "avian": BodyStructureType.AVIAN,
                "aquatic": BodyStructureType.AQUATIC,
            }
            return mapping.get(locomotion, BodyStructureType.BIPEDAL)
    
    # Fallback - check for structure attribute directly
    struct = getattr(character, "body_structure", None)
    if struct and isinstance(struct, BodyStructureType):
        return struct
    
    # Default to bipedal
    return BodyStructureType.BIPEDAL


def get_character_size(character):
    """Get the size category of a character."""
    body = getattr(character, "body", None)
    if body:
        structure = getattr(body, "structure", None)
        if structure:
            size = getattr(structure, "size_category", "medium")
            mapping = {
                "tiny": SizeCategory.TINY,
                "small": SizeCategory.SMALL,
                "medium": SizeCategory.MEDIUM,
                "large": SizeCategory.LARGE,
                "huge": SizeCategory.HUGE,
                "massive": SizeCategory.MASSIVE,
            }
            return mapping.get(size, SizeCategory.MEDIUM)
    return SizeCategory.MEDIUM


def find_furniture_in_room(room, furniture_types):
    """Find furniture in a room that matches the required types."""
    for obj in room.contents:
        obj_tags = getattr(obj, "position_tags", set())
        if isinstance(obj_tags, list):
            obj_tags = set(obj_tags)
        
        for ftype in furniture_types:
            if ftype.value in obj_tags:
                return obj
    return None


class CmdPosition(Command):
    """
    Initiate a sexual position with another character.
    
    Usage:
        position <position_name> <target> [as <slot>] [on <furniture>] [= <flavor>]
        position list [category]
        position info <position_name>
        
    Examples:
        position missionary Elena
        position doggy Elena as behind on bed
        position bent_over_furniture Elena on desk = pinning her down
        position list oral
        position info spitroast
        
    Use 'positions' to see all available positions.
    """
    
    key = "position"
    aliases = ["pos"]
    locks = "cmd:all()"
    help_category = "Social"
    
    def parse(self):
        """Parse the command arguments."""
        self.position_key = None
        self.target = None
        self.slot = None
        self.furniture = None
        self.flavor = ""
        self.list_mode = False
        self.info_mode = False
        self.category = None
        
        args = self.args.strip()
        
        if not args:
            return
        
        # Check for list/info mode
        if args.startswith("list"):
            self.list_mode = True
            rest = args[4:].strip()
            if rest:
                self.category = rest
            return
        
        if args.startswith("info "):
            self.info_mode = True
            self.position_key = args[5:].strip()
            return
        
        # Split by = for flavor text
        if "=" in args:
            args, self.flavor = args.split("=", 1)
            self.flavor = self.flavor.strip()
            args = args.strip()
        
        # Split by "on" for furniture
        if " on " in args:
            args, furniture_str = args.rsplit(" on ", 1)
            self.furniture = furniture_str.strip()
            args = args.strip()
        
        # Split by "as" for slot
        if " as " in args:
            args, slot_str = args.rsplit(" as ", 1)
            self.slot = slot_str.strip()
            args = args.strip()
        
        # What remains should be: position_name target
        parts = args.split(None, 1)
        if len(parts) >= 1:
            self.position_key = parts[0].lower()
        if len(parts) >= 2:
            self.target = parts[1].strip()
    
    def func(self):
        """Execute the command."""
        caller = self.caller
        
        if self.list_mode:
            self.list_positions()
            return
        
        if self.info_mode:
            self.show_position_info()
            return
        
        if not self.position_key:
            caller.msg("Usage: position <position_name> <target>")
            caller.msg("       position list [category]")
            return
        
        if not self.target:
            caller.msg("Who do you want to get into position with?")
            return
        
        # Find target
        target = caller.search(self.target, location=caller.location)
        if not target:
            return
        
        if target == caller:
            caller.msg("You can't get into a position with yourself.")
            return
        
        # Get position definition
        position = get_position(self.position_key)
        if not position:
            # Try fuzzy search
            matches = [p for p in POSITIONS.values() 
                      if self.position_key in p.key.lower() 
                      or self.position_key in p.name.lower()
                      or any(self.position_key in a.lower() for a in p.aliases)]
            if len(matches) == 1:
                position = matches[0]
            elif len(matches) > 1:
                caller.msg(f"Multiple positions match '{self.position_key}':")
                for p in matches[:5]:
                    caller.msg(f"  {p.key} - {p.name}")
                return
            else:
                caller.msg(f"Unknown position: {self.position_key}")
                caller.msg("Use 'position list' to see available positions.")
                return
        
        # Check species compatibility
        my_structure = get_character_structure(caller)
        their_structure = get_character_structure(target)
        my_size = get_character_size(caller)
        their_size = get_character_size(target)
        
        compat = check_position_compatibility(
            position.key, my_structure, their_structure, my_size, their_size
        )
        
        if not compat.compatible:
            caller.msg(f"|rIncompatible:|n {compat.reason}")
            if compat.suggested_variant:
                caller.msg(f"Try: |w{compat.suggested_variant}|n instead.")
            return
        
        if compat.warnings:
            for warning in compat.warnings:
                caller.msg(f"|yNote:|n {warning}")
        
        # Find furniture if specified or required
        furniture_obj = None
        if self.furniture:
            furniture_obj = caller.search(self.furniture, location=caller.location)
            if not furniture_obj:
                return
        elif position.requirements.furniture_required:
            # Try to find suitable furniture
            furniture_obj = find_furniture_in_room(
                caller.location, 
                position.requirements.furniture_types
            )
            if not furniture_obj:
                types = ", ".join(f.value for f in position.requirements.furniture_types)
                caller.msg(f"|rThis position requires furniture:|n {types}")
                return
        
        # Check furniture compatibility
        if furniture_obj:
            can_use, reason = position.requirements.check_furniture(furniture_obj)
            if not can_use:
                caller.msg(f"|r{reason}|n")
                return
        
        # Determine slot assignments
        slots = list(position.slots.keys())
        if len(slots) < 2:
            caller.msg("This position doesn't support two participants.")
            return
        
        # Assign slots
        if self.slot:
            if self.slot not in position.slots:
                caller.msg(f"Unknown slot: {self.slot}")
                caller.msg(f"Available slots: {', '.join(slots)}")
                return
            my_slot = self.slot
            # Give target the other slot
            other_slots = [s for s in slots if s != my_slot]
            their_slot = other_slots[0] if other_slots else slots[1]
        else:
            # Default: caller takes first slot, target takes second
            my_slot = slots[0]
            their_slot = slots[1]
        
        # Get room manager
        manager = get_room_manager(caller.location)
        
        # Check if either is already in a position
        if manager.is_in_position(caller):
            caller.msg("You're already in a position. Use |wdismount|n first.")
            return
        if manager.is_in_position(target):
            caller.msg(f"{target.key} is already in a position.")
            return
        
        # TODO: Add consent check here
        # For now, create an invitation
        success, msg = manager.create_invite(
            position.key,
            inviter=caller,
            slot_for_inviter=my_slot,
            invitee=target,
            slot_for_invitee=their_slot,
            anchor=furniture_obj,
            custom_flavor=self.flavor
        )
        
        if not success:
            caller.msg(f"|r{msg}|n")
            return
        
        # Notify both parties
        slot_def = position.slots.get(their_slot)
        slot_name = slot_def.name if slot_def else their_slot
        
        caller.msg(f"You invite {target.key} to |w{position.name}|n as {slot_name}.")
        
        invite_msg = f"{caller.key} invites you to |w{position.name}|n as {slot_name}."
        if self.flavor:
            invite_msg += f" ({self.flavor})"
        invite_msg += "\nUse |waccept|n or |wdecline|n to respond."
        target.msg(invite_msg)
        
        # Notify room (excluding participants)
        room_msg = f"{caller.key} propositions {target.key}."
        caller.location.msg_contents(room_msg, exclude=[caller, target])
    
    def list_positions(self):
        """List available positions."""
        caller = self.caller
        
        if self.category:
            # Search by category or tag
            positions = search_positions(
                query=self.category,
                category=self.category if self.category in set(p.category for p in POSITIONS.values()) else None,
                tags={self.category} if self.category not in set(p.category for p in POSITIONS.values()) else None
            )
            if not positions:
                # Try as tag
                positions = get_positions_by_tag(self.category)
            
            if not positions:
                caller.msg(f"No positions found for '{self.category}'")
                return
            
            caller.msg(f"|wPositions matching '{self.category}':|n")
        else:
            positions = list(POSITIONS.values())
            caller.msg("|wAll Positions:|n")
        
        # Group by category
        by_category = {}
        for pos in positions:
            by_category.setdefault(pos.category, []).append(pos)
        
        for category in sorted(by_category.keys()):
            caller.msg(f"\n|y{category.title()}:|n")
            for pos in sorted(by_category[category], key=lambda p: p.name):
                caller.msg(f"  |w{pos.key}|n - {pos.name}")
    
    def show_position_info(self):
        """Show detailed info about a position."""
        caller = self.caller
        
        position = get_position(self.position_key)
        if not position:
            caller.msg(f"Unknown position: {self.position_key}")
            return
        
        caller.msg(f"|w{position.name}|n ({position.key})")
        caller.msg(f"|n{position.description}")
        caller.msg("")
        
        caller.msg(f"|yCategory:|n {position.category}")
        caller.msg(f"|yTags:|n {', '.join(sorted(position.tags))}")
        caller.msg(f"|yParticipants:|n {position.requirements.min_participants}-{position.requirements.max_participants}")
        
        if position.requirements.furniture_required:
            types = ", ".join(f.value for f in position.requirements.furniture_types)
            caller.msg(f"|yRequires furniture:|n {types}")
        elif position.requirements.furniture_types:
            types = ", ".join(f.value for f in position.requirements.furniture_types)
            caller.msg(f"|yWorks with:|n {types}")
        
        caller.msg(f"\n|ySlots:|n")
        for slot_key, slot_def in position.slots.items():
            extras = []
            if slot_def.can_thrust:
                extras.append("can thrust")
            if slot_def.controls_pace:
                extras.append("controls pace")
            if not slot_def.hands_free:
                extras.append("hands occupied")
            if not slot_def.mouth_free:
                extras.append("mouth occupied")
            if slot_def.expandable:
                extras.append(f"up to {slot_def.max_occupants}")
            
            extra_str = f" ({', '.join(extras)})" if extras else ""
            caller.msg(f"  |w{slot_key}|n: {slot_def.posture.value}{extra_str}")


class CmdFuck(Command):
    """
    Quick command to initiate sex with someone.
    
    Usage:
        fuck <target> [position] [= flavor]
        
    Examples:
        fuck Elena
        fuck Elena missionary
        fuck Elena doggy = hard and rough
        
    If no position is specified, picks an appropriate one based on
    your body types and available furniture.
    """
    
    key = "fuck"
    aliases = ["sex", "mate", "breed"]
    locks = "cmd:all()"
    help_category = "Social"
    
    def parse(self):
        self.target = None
        self.position_key = None
        self.flavor = ""
        
        args = self.args.strip()
        if not args:
            return
        
        # Split by = for flavor
        if "=" in args:
            args, self.flavor = args.split("=", 1)
            self.flavor = self.flavor.strip()
            args = args.strip()
        
        parts = args.split(None, 1)
        if len(parts) >= 1:
            self.target = parts[0]
        if len(parts) >= 2:
            self.position_key = parts[1].lower()
    
    def func(self):
        caller = self.caller
        
        if not self.target:
            caller.msg("Who do you want to fuck?")
            return
        
        target = caller.search(self.target, location=caller.location)
        if not target:
            return
        
        if target == caller:
            caller.msg("That would be impressive, but no.")
            return
        
        # Get body structures
        my_structure = get_character_structure(caller)
        their_structure = get_character_structure(target)
        
        # If no position specified, pick one
        if not self.position_key:
            # Get compatible positions
            compatible = get_compatible_positions(my_structure, their_structure)
            
            # Prefer penetrative
            penetrative = [p for p in compatible 
                          if p in [pos.key for pos in get_positions_by_tag("penetrative")]]
            
            if penetrative:
                # Check for furniture
                room = caller.location
                has_bed = find_furniture_in_room(room, {FurnitureType.BED})
                has_wall = find_furniture_in_room(room, {FurnitureType.WALL})
                
                if has_bed and "missionary" in penetrative:
                    self.position_key = "missionary"
                elif has_bed and "doggy" in penetrative:
                    self.position_key = "doggy"
                elif "standing" in penetrative:
                    self.position_key = "standing"
                elif has_wall and "against_wall" in penetrative:
                    self.position_key = "against_wall"
                elif "mounted" in penetrative:
                    self.position_key = "mounted"
                elif "biped_mounts_quadruped" in penetrative:
                    self.position_key = "biped_mounts_quadruped"
                else:
                    self.position_key = penetrative[0]
            elif compatible:
                self.position_key = compatible[0]
            else:
                caller.msg("No compatible positions found for your body types.")
                return
        
        # Execute as position command
        position_cmd = f"position {self.position_key} {target.key}"
        if self.flavor:
            position_cmd += f" = {self.flavor}"
        
        caller.execute_cmd(position_cmd)


class CmdMount(Command):
    """
    Mount another character (typically for quadruped/taur interactions).
    
    Usage:
        mount <target> [= flavor]
        
    Examples:
        mount Shadow
        mount Chiron = climbing onto their back
        
    Automatically picks the appropriate mounting position based on
    body types.
    """
    
    key = "mount"
    aliases = ["ride"]
    locks = "cmd:all()"
    help_category = "Social"
    
    def func(self):
        caller = self.caller
        args = self.args.strip()
        
        flavor = ""
        if "=" in args:
            args, flavor = args.split("=", 1)
            flavor = flavor.strip()
            args = args.strip()
        
        if not args:
            caller.msg("Who do you want to mount?")
            return
        
        target = caller.search(args, location=caller.location)
        if not target:
            return
        
        my_structure = get_character_structure(caller)
        their_structure = get_character_structure(target)
        
        # Pick appropriate mounting position
        if their_structure == BodyStructureType.QUADRUPED:
            if my_structure == BodyStructureType.BIPEDAL:
                position_key = "biped_mounts_quadruped"
            else:
                position_key = "mounted"
        elif their_structure == BodyStructureType.TAUR:
            if my_structure in (BodyStructureType.BIPEDAL, BodyStructureType.DIGITIGRADE):
                position_key = "riding_taur_back"
            else:
                position_key = "taur_rides_taur"
        elif my_structure == BodyStructureType.QUADRUPED:
            position_key = "mounted"
        else:
            # Default to cowgirl for bipeds
            position_key = "cowgirl"
        
        cmd = f"position {position_key} {target.key}"
        if flavor:
            cmd += f" = {flavor}"
        caller.execute_cmd(cmd)


class CmdDismount(Command):
    """
    Leave your current position.
    
    Usage:
        dismount [reason]
        
    Examples:
        dismount
        dismount pulling out slowly
    """
    
    key = "dismount"
    aliases = ["withdraw", "pull out", "stop", "disengage"]
    locks = "cmd:all()"
    help_category = "Social"
    
    def func(self):
        caller = self.caller
        reason = self.args.strip()
        
        manager = get_room_manager(caller.location)
        
        if not manager.is_in_position(caller):
            caller.msg("You're not in a position.")
            return
        
        success, msg = manager.remove_from_position(caller, reason)
        
        if success:
            caller.location.msg_contents(msg)
        else:
            caller.msg(f"|r{msg}|n")


class CmdAccept(Command):
    """
    Accept a position invitation.
    
    Usage:
        accept
    """
    
    key = "accept"
    locks = "cmd:all()"
    help_category = "Social"
    
    def func(self):
        caller = self.caller
        manager = get_room_manager(caller.location)
        
        invite = manager.get_pending_invite(caller)
        if not invite:
            caller.msg("You don't have any pending invitations.")
            return
        
        active, msg = manager.accept_invite(caller)
        
        if active:
            # Notify room
            caller.location.msg_contents(msg)
            
            # Show position description
            desc = active.describe()
            caller.location.msg_contents(desc)
        else:
            caller.msg(f"|r{msg}|n")


class CmdDecline(Command):
    """
    Decline a position invitation.
    
    Usage:
        decline
    """
    
    key = "decline"
    aliases = ["reject", "refuse"]
    locks = "cmd:all()"
    help_category = "Social"
    
    def func(self):
        caller = self.caller
        manager = get_room_manager(caller.location)
        
        invite = manager.get_pending_invite(caller)
        if not invite:
            caller.msg("You don't have any pending invitations.")
            return
        
        msg = manager.decline_invite(caller)
        
        # Notify the inviter
        invite.inviter.msg(f"{caller.key} declines your invitation.")
        caller.msg("You decline the invitation.")


class CmdJoin(Command):
    """
    Join an existing position in progress.
    
    Usage:
        join <target> [as <slot>] [= flavor]
        
    Examples:
        join Elena as front
        join Elena = eagerly
        
    Joins a position someone else is already in, if there's an open slot.
    """
    
    key = "join"
    locks = "cmd:all()"
    help_category = "Social"
    
    def func(self):
        caller = self.caller
        args = self.args.strip()
        
        if not args:
            caller.msg("Who do you want to join?")
            return
        
        flavor = ""
        slot = None
        
        if "=" in args:
            args, flavor = args.split("=", 1)
            flavor = flavor.strip()
            args = args.strip()
        
        if " as " in args:
            args, slot = args.rsplit(" as ", 1)
            slot = slot.strip()
            args = args.strip()
        
        target = caller.search(args, location=caller.location)
        if not target:
            return
        
        manager = get_room_manager(caller.location)
        
        # Check if caller is already in position
        if manager.is_in_position(caller):
            caller.msg("You're already in a position.")
            return
        
        # Find target's position
        active = manager.get_position_for(target)
        if not active:
            caller.msg(f"{target.key} isn't in a position.")
            return
        
        # Find open slots
        open_slots = manager.get_open_slots(active)
        if not open_slots:
            caller.msg("No open slots in that position.")
            return
        
        if slot:
            if slot not in open_slots:
                caller.msg(f"Slot '{slot}' isn't available.")
                caller.msg(f"Open slots: {', '.join(open_slots)}")
                return
        else:
            slot = open_slots[0]
        
        # Add to position
        success, msg = manager.add_to_position(active, caller, slot, flavor)
        
        if success:
            caller.location.msg_contents(msg + ".")
        else:
            caller.msg(f"|r{msg}|n")


class CmdPositions(Command):
    """
    List or search available positions.
    
    Usage:
        positions [search_term]
        positions categories
        positions for <species> <species>
        
    Examples:
        positions
        positions oral
        positions bondage
        positions for taur bipedal
        positions categories
    """
    
    key = "positions"
    locks = "cmd:all()"
    help_category = "Social"
    
    def func(self):
        caller = self.caller
        args = self.args.strip()
        
        if args == "categories":
            categories = sorted(set(p.category for p in POSITIONS.values()))
            caller.msg("|wPosition Categories:|n")
            for cat in categories:
                count = len([p for p in POSITIONS.values() if p.category == cat])
                caller.msg(f"  |w{cat}|n: {count} positions")
            return
        
        if args.startswith("for "):
            parts = args[4:].split()
            if len(parts) < 2:
                caller.msg("Usage: positions for <species1> <species2>")
                return
            
            # Map species names to types
            mapping = {
                "human": BodyStructureType.BIPEDAL,
                "bipedal": BodyStructureType.BIPEDAL,
                "anthro": BodyStructureType.DIGITIGRADE,
                "digitigrade": BodyStructureType.DIGITIGRADE,
                "feral": BodyStructureType.QUADRUPED,
                "quadruped": BodyStructureType.QUADRUPED,
                "taur": BodyStructureType.TAUR,
                "centaur": BodyStructureType.TAUR,
                "naga": BodyStructureType.SERPENTINE,
                "serpentine": BodyStructureType.SERPENTINE,
                "lamia": BodyStructureType.SERPENTINE,
            }
            
            struct_a = mapping.get(parts[0].lower())
            struct_b = mapping.get(parts[1].lower())
            
            if not struct_a or not struct_b:
                caller.msg("Unknown species. Options: human, anthro, feral, taur, naga")
                return
            
            compatible = get_compatible_positions(struct_a, struct_b)
            caller.msg(f"|wCompatible positions for {parts[0]} + {parts[1]}:|n {len(compatible)}")
            
            # Group by category
            by_cat = {}
            for key in compatible:
                pos = get_position(key)
                if pos:
                    by_cat.setdefault(pos.category, []).append(pos)
            
            for cat in sorted(by_cat.keys()):
                caller.msg(f"\n|y{cat.title()}:|n")
                for pos in sorted(by_cat[cat], key=lambda p: p.name):
                    caller.msg(f"  {pos.key} - {pos.name}")
            return
        
        # Regular search
        if args:
            positions = search_positions(query=args)
            if not positions:
                positions = get_positions_by_tag(args)
            
            if not positions:
                caller.msg(f"No positions found matching '{args}'")
                return
            
            caller.msg(f"|wPositions matching '{args}':|n")
        else:
            positions = list(POSITIONS.values())
            caller.msg(f"|wAll Positions:|n ({len(positions)} total)")
        
        # Group by category
        by_cat = {}
        for pos in positions:
            by_cat.setdefault(pos.category, []).append(pos)
        
        for cat in sorted(by_cat.keys()):
            caller.msg(f"\n|y{cat.title()}:|n")
            for pos in sorted(by_cat[cat], key=lambda p: p.name):
                caller.msg(f"  |w{pos.key}|n - {pos.name}")


class CmdPositionStatus(Command):
    """
    See your current position status.
    
    Usage:
        pstatus
    """
    
    key = "pstatus"
    aliases = ["positionstatus", "ps"]
    locks = "cmd:all()"
    help_category = "Social"
    
    def func(self):
        caller = self.caller
        manager = get_room_manager(caller.location)
        
        active = manager.get_position_for(caller)
        if not active:
            caller.msg("You're not in a position.")
            
            # Check for pending invite
            invite = manager.get_pending_invite(caller)
            if invite:
                caller.msg(f"\nPending invitation from {invite.inviter.key}")
                pos = get_position(invite.position_key)
                if pos:
                    caller.msg(f"Position: {pos.name} as {invite.slot_for_invitee}")
            return
        
        caller.msg(f"|wCurrent Position:|n {active.definition.name}")
        if active.custom_flavor:
            caller.msg(f"|yStyle:|n {active.custom_flavor}")
        
        my_slot = active.get_slot_for_character(caller)
        caller.msg(f"|yYour role:|n {my_slot}")
        
        # Show other participants
        caller.msg("|yParticipants:|n")
        for slot_key, occupant in active.occupants.items():
            char_name = occupant.character.key
            slot_def = active.definition.get_slot(slot_key)
            posture = slot_def.posture.value if slot_def else "unknown"
            marker = " (you)" if occupant.character == caller else ""
            caller.msg(f"  {char_name} as {slot_key} - {posture}{marker}")
        
        # Show what you can do
        caller.msg("|yYour status:|n")
        can_thrust = active.can_participant_thrust(caller)
        can_speak = active.can_participant_speak(caller)
        can_hands = active.can_participant_use_hands(caller)
        
        abilities = []
        if can_thrust:
            abilities.append("can thrust")
        if can_speak:
            abilities.append("can speak")
        if can_hands:
            abilities.append("hands free")
        else:
            abilities.append("hands occupied")
        
        caller.msg(f"  {', '.join(abilities)}")


class PositionCmdSet(CmdSet):
    """Commands for sexual positions."""
    
    key = "position_cmdset"
    
    def at_cmdset_creation(self):
        self.add(CmdPosition())
        self.add(CmdFuck())
        self.add(CmdMount())
        self.add(CmdDismount())
        self.add(CmdAccept())
        self.add(CmdDecline())
        self.add(CmdJoin())
        self.add(CmdPositions())
        self.add(CmdPositionStatus())
