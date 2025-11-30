"""
NPC Types
=========

Specialized NPC classes:
- AmbientNPC: Background atmosphere
- ServiceNPC: Shopkeepers, bartenders
- CompanionNPC: Can follow, bond
- FeralNPC: Animals, instinct-driven
- GuardNPC: Security, patrols
- UniqueNPC: Story characters
"""

from typing import List, Optional
from random import choice, random

from evennia import AttributeProperty

from .base import NPC, NPCType, BehaviorState, Disposition


# =============================================================================
# AMBIENT NPC
# =============================================================================

class AmbientNPC(NPC):
    """Background characters for atmosphere."""
    
    npc_type = AttributeProperty(default=NPCType.AMBIENT)
    
    ambient_actions = AttributeProperty(default=list)
    ambient_frequency = AttributeProperty(default=0.05)
    
    def ai_tick(self):
        if random() < self.ambient_frequency:
            self._do_ambient()
    
    def _do_ambient(self):
        actions = self.ambient_actions or []
        if actions and self.location:
            self.location.msg_contents(f"{self.key} {choice(actions)}")
    
    def on_spoken_to(self, speaker, message):
        responses = [
            "grunts noncommittally.",
            "nods vaguely.",
            "doesn't seem interested.",
        ]
        if self.location:
            self.location.msg_contents(f"{self.key} {choice(responses)}")


# =============================================================================
# SERVICE NPC
# =============================================================================

class ServiceNPC(NPC):
    """NPCs that provide services."""
    
    npc_type = AttributeProperty(default=NPCType.SERVICE)
    behavior_state = AttributeProperty(default=BehaviorState.WORKING)
    
    service_type = AttributeProperty(default="generic")
    work_greeting = AttributeProperty(default="How can I help you?")
    is_working = AttributeProperty(default=True)
    
    def on_spoken_to(self, speaker, message):
        if not self.is_working:
            if self.location:
                self.location.msg_contents(f'{self.key} says, "I\'m not working right now."')
            return
        
        msg = message.lower()
        
        if any(w in msg for w in ["buy", "purchase", "price"]):
            response = "Let me show you what we have..."
        elif any(w in msg for w in ["drink", "ale", "beer"]):
            response = "Coming right up."
        elif any(w in msg for w in ["room", "stay"]):
            response = "Rooms are 5 gold per night."
        else:
            response = self.work_greeting
        
        if self.location:
            self.location.msg_contents(f'{self.key} says, "{response}"')


# =============================================================================
# COMPANION NPC
# =============================================================================

class CompanionNPC(NPC):
    """NPCs that can form bonds and follow."""
    
    npc_type = AttributeProperty(default=NPCType.COMPANION)
    
    following = AttributeProperty(default=None)
    bonded_to = AttributeProperty(default=None)
    loyalty = AttributeProperty(default=50)
    
    def follow(self, character) -> tuple:
        rel = self.get_relationship(character)
        if rel.trust < 30:
            return False, f"{self.key} doesn't trust you enough."
        
        self.following = character.dbref
        self.behavior_state = BehaviorState.FOLLOWING
        return True, f"{self.key} will follow you."
    
    def stop_following(self) -> tuple:
        self.following = None
        self.behavior_state = BehaviorState.IDLE
        return True, f"{self.key} stops following."
    
    def bond_with(self, character) -> tuple:
        rel = self.get_relationship(character)
        if rel.trust < 70:
            return False, f"{self.key} doesn't trust you enough."
        
        self.bonded_to = character.dbref
        return True, f"{self.key} bonds with you."
    
    def on_character_arrives(self, character):
        super().on_character_arrives(character)
        if character.dbref == self.bonded_to and self.location:
            self.location.msg_contents(f"{self.key}'s eyes light up!")
    
    def on_character_leaves(self, character, destination):
        if self.following == character.dbref:
            self.move_to(destination)


# =============================================================================
# FERAL NPC
# =============================================================================

class FeralNPC(NPC):
    """Animals driven by instinct."""
    
    npc_type = AttributeProperty(default=NPCType.FERAL)
    
    animal_type = AttributeProperty(default="generic")
    
    hunger = AttributeProperty(default=50)
    fear_level = AttributeProperty(default=0)
    aggression = AttributeProperty(default=0)
    arousal_level = AttributeProperty(default=0)
    
    is_domesticated = AttributeProperty(default=False)
    owner = AttributeProperty(default=None)
    trained_commands = AttributeProperty(default=list)
    
    sounds = AttributeProperty(default=dict)
    
    def make_sound(self, mood: str = "neutral"):
        if not self.location:
            return
        sounds = self.sounds or {}
        mood_sounds = sounds.get(mood, sounds.get("neutral", ["makes a sound."]))
        if mood_sounds:
            self.location.msg_contents(f"{self.key} {choice(mood_sounds)}")
    
    def ai_tick(self):
        if self.hunger > 70:
            self.behavior_state = BehaviorState.WANDERING
        elif self.fear_level > 60:
            self.behavior_state = BehaviorState.AFRAID
        elif self.aggression > 70:
            self.behavior_state = BehaviorState.AGGRESSIVE
        elif self.arousal_level > 70:
            self.behavior_state = BehaviorState.INTERESTED
    
    def on_spoken_to(self, speaker, message):
        rel = self.get_relationship(speaker)
        if speaker.dbref == self.owner:
            self.make_sound("happy")
        elif rel.trust > 50:
            self.make_sound("neutral")
        else:
            self.make_sound("wary")


# =============================================================================
# GUARD NPC
# =============================================================================

class GuardNPC(NPC):
    """Security NPCs."""
    
    npc_type = AttributeProperty(default=NPCType.GUARD)
    behavior_state = AttributeProperty(default=BehaviorState.WORKING)
    
    patrol_route = AttributeProperty(default=list)
    patrol_index = AttributeProperty(default=0)
    alert_level = AttributeProperty(default=0)
    
    def ai_tick(self):
        if self.patrol_route and random() < 0.2:
            self._patrol_next()
    
    def _patrol_next(self):
        if not self.patrol_route:
            return
        self.patrol_index = (self.patrol_index + 1) % len(self.patrol_route)
        next_room = self.patrol_route[self.patrol_index]
        try:
            from evennia.utils.search import search_object
            room = search_object(next_room)
            if room:
                self.move_to(room[0])
        except Exception:
            pass


# =============================================================================
# UNIQUE NPC
# =============================================================================

class UniqueNPC(NPC):
    """Named story characters with dialogue."""
    
    npc_type = AttributeProperty(default=NPCType.UNIQUE)
    
    unique_id = AttributeProperty(default="")
    dialogue_tree = AttributeProperty(default=dict)
    dialogue_state = AttributeProperty(default="start")
    quest_flags = AttributeProperty(default=dict)
    
    def get_dialogue(self) -> str:
        tree = self.dialogue_tree or {}
        state = tree.get(self.dialogue_state, {})
        return state.get("text", "...")
    
    def choose_option(self, index: int) -> str:
        tree = self.dialogue_tree or {}
        state = tree.get(self.dialogue_state, {})
        options = state.get("options", [])
        
        if 0 <= index < len(options):
            option = options[index]
            self.dialogue_state = option.get("next", self.dialogue_state)
            return self.get_dialogue()
        return "..."
    
    def on_spoken_to(self, speaker, message):
        msg = message.lower()
        tree = self.dialogue_tree or {}
        state = tree.get(self.dialogue_state, {})
        options = state.get("options", [])
        
        for i, opt in enumerate(options):
            keywords = opt.get("keywords", [])
            if any(kw in msg for kw in keywords):
                response = self.choose_option(i)
                if self.location:
                    self.location.msg_contents(f'{self.key} says, "{response}"')
                return
        
        if self.location:
            self.location.msg_contents(f'{self.key} says, "{self.get_dialogue()}"')


__all__ = [
    "AmbientNPC", "ServiceNPC", "CompanionNPC",
    "FeralNPC", "GuardNPC", "UniqueNPC",
]
