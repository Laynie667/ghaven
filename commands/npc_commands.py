"""
NPC Commands for Gilderhaven
=============================

Commands for interacting with NPCs.

Commands:
- talk: Start conversation with an NPC
- say: Continue dialogue (pick choice)
- npcs: List NPCs in room
"""

from evennia import Command, CmdSet
from world.npcs import (
    is_npc, start_dialogue, process_dialogue_choice,
    is_in_dialogue, end_dialogue, get_npc_data,
    get_npc_memory, npc_ambient_action
)


class CmdTalk(Command):
    """
    Talk to an NPC.
    
    Usage:
        talk <npc>
        talk to <npc>
        
    Examples:
        talk curator
        talk to the shopkeeper
    
    Start a conversation with an NPC. Once in conversation,
    use numbers to select dialogue choices.
    """
    
    key = "talk"
    aliases = ["speak", "converse", "chat"]
    locks = "cmd:all()"
    help_category = "Social"
    
    def func(self):
        caller = self.caller
        
        if not self.args:
            caller.msg("Talk to whom?")
            return
        
        args = self.args.strip()
        
        # Remove "to " prefix
        if args.lower().startswith("to "):
            args = args[3:].strip()
        
        # Check if already in dialogue
        if is_in_dialogue(caller):
            caller.msg("You're already in a conversation. Finish it first or use 'end conversation'.")
            return
        
        # Find the NPC
        target = caller.search(args, location=caller.location)
        if not target:
            return
        
        if not is_npc(target):
            caller.msg(f"{target.key} doesn't seem interested in conversation.")
            return
        
        # Start dialogue
        start_dialogue(caller, target)


class CmdSay(Command):
    """
    Select a dialogue choice or say something.
    
    Usage:
        <number>        - Select dialogue choice
        say <number>    - Same as above
        1, 2, 3...      - Quick choice selection
    
    When in conversation with an NPC, use numbers to
    select your response.
    """
    
    key = "say"
    aliases = ["1", "2", "3", "4", "5", "6", "7", "8", "9"]
    locks = "cmd:all()"
    help_category = "Social"
    
    def func(self):
        caller = self.caller
        
        # Check if in dialogue
        if not is_in_dialogue(caller):
            # If not in dialogue and they used "say", just emote
            if self.cmdstring == "say" and self.args:
                caller.location.msg_contents(
                    f'{caller.key} says, "{self.args.strip()}"',
                    exclude=[]
                )
                return
            elif self.cmdstring.isdigit():
                caller.msg("You're not in a conversation. Use 'talk <npc>' to start one.")
                return
            return
        
        # Get choice number
        if self.cmdstring.isdigit():
            choice_num = int(self.cmdstring)
        elif self.args and self.args.strip().isdigit():
            choice_num = int(self.args.strip())
        else:
            caller.msg("Enter a number to select your dialogue choice.")
            return
        
        # Process choice
        process_dialogue_choice(caller, choice_num)


class CmdEndConversation(Command):
    """
    End current conversation with an NPC.
    
    Usage:
        end conversation
        stop talking
        leave conversation
    
    Abruptly ends any ongoing NPC dialogue.
    """
    
    key = "end conversation"
    aliases = ["stop talking", "leave conversation", "end dialogue", "quit talking"]
    locks = "cmd:all()"
    help_category = "Social"
    
    def func(self):
        caller = self.caller
        
        if not is_in_dialogue(caller):
            caller.msg("You're not in a conversation.")
            return
        
        end_dialogue(caller)
        caller.msg("You end the conversation.")


class CmdNPCs(Command):
    """
    List NPCs in the current room.
    
    Usage:
        npcs
        who's here
    
    Shows all NPCs present and their current status.
    """
    
    key = "npcs"
    aliases = ["who's here", "whos here", "list npcs"]
    locks = "cmd:all()"
    help_category = "Social"
    
    def func(self):
        caller = self.caller
        room = caller.location
        
        if not room:
            caller.msg("You're nowhere.")
            return
        
        npcs = [obj for obj in room.contents if is_npc(obj)]
        
        if not npcs:
            caller.msg("There are no NPCs here.")
            return
        
        lines = ["|wNPCs present:|n"]
        lines.append("-" * 40)
        
        for npc in npcs:
            npc_data = get_npc_data(npc)
            flags = npc_data.get("flags", [])
            
            status = ""
            if npc.db.npc_state and npc.db.npc_state.get("talking_to"):
                if npc.db.npc_state["talking_to"] == caller.id:
                    status = " |c(talking to you)|n"
                else:
                    status = " |x(busy)|n"
            
            markers = []
            if "merchant" in flags:
                markers.append("|y[Shop]|n")
            if "important" in flags:
                markers.append("|m[!]|n")
            
            marker_str = " ".join(markers)
            if marker_str:
                marker_str = " " + marker_str
            
            lines.append(f"  |c{npc.key}|n{marker_str}{status}")
        
        lines.append("-" * 40)
        lines.append("|xUse 'talk <npc>' to start a conversation.|n")
        
        caller.msg("\n".join(lines))


class CmdGreet(Command):
    """
    Greet an NPC (shortcut for talk).
    
    Usage:
        greet <npc>
        hello <npc>
    
    A friendly way to start a conversation.
    """
    
    key = "greet"
    aliases = ["hello", "hi", "hey"]
    locks = "cmd:all()"
    help_category = "Social"
    
    def func(self):
        caller = self.caller
        
        if not self.args:
            # Generic greeting
            if caller.location:
                caller.location.msg_contents(
                    f"{caller.key} waves hello.",
                    exclude=[]
                )
            return
        
        args = self.args.strip()
        
        # Check if in dialogue
        if is_in_dialogue(caller):
            caller.msg("You're already in a conversation.")
            return
        
        # Find the NPC
        target = caller.search(args, location=caller.location)
        if not target:
            return
        
        if not is_npc(target):
            # Just greet non-NPCs
            caller.location.msg_contents(
                f"{caller.key} greets {target.key}.",
                exclude=[]
            )
            return
        
        # Start dialogue
        start_dialogue(caller, target)


class CmdBow(Command):
    """
    Bow to someone, particularly an NPC.
    
    Usage:
        bow
        bow <target>
        bow to <target>
    
    Shows respect. Some NPCs may react to this.
    """
    
    key = "bow"
    aliases = ["curtsy"]
    locks = "cmd:all()"
    help_category = "Social"
    
    def func(self):
        caller = self.caller
        room = caller.location
        
        if not room:
            return
        
        if not self.args:
            room.msg_contents(f"{caller.key} bows respectfully.", exclude=[])
            return
        
        args = self.args.strip()
        if args.lower().startswith("to "):
            args = args[3:].strip()
        
        target = caller.search(args, location=room)
        if not target:
            return
        
        room.msg_contents(
            f"{caller.key} bows respectfully to {target.key}.",
            exclude=[]
        )
        
        # NPC reaction
        if is_npc(target):
            from world.npcs import npc_react_to
            reaction = npc_react_to(target, "character_bows", caller)
            if reaction:
                room.msg_contents(reaction, exclude=[])


# =============================================================================
# Command Set
# =============================================================================

class NPCCmdSet(CmdSet):
    """
    Commands for NPC interaction.
    """
    
    key = "npcs"
    priority = 1
    
    def at_cmdset_creation(self):
        self.add(CmdTalk())
        self.add(CmdSay())
        self.add(CmdEndConversation())
        self.add(CmdNPCs())
        self.add(CmdGreet())
        self.add(CmdBow())
