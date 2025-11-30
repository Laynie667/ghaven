"""
NPC Behaviors
=============

Behavior mixins for NPCs:
- ConversationMixin: Talk, respond, remember topics
- FlirtationMixin: Romantic interest, advances
- SexualBehaviorMixin: Sexual responses and initiation
- PathfindingMixin: Movement and following
- FeralBehaviorMixin: Instincts, reactions
- PackBehaviorMixin: Pack dynamics
- TerritoryBehaviorMixin: Territory marking, defense
- HuntingBehaviorMixin: Predator behaviors
- MatingBehaviorMixin: Mating behaviors
"""

from typing import Dict, List, Optional, Tuple
from random import choice, random, randint
from enum import Enum

from evennia import AttributeProperty

from .base import BehaviorState, Disposition


# =============================================================================
# CONVERSATION TOPICS
# =============================================================================

class Topic(Enum):
    GREETING = "greeting"
    WEATHER = "weather"
    WORK = "work"
    GOSSIP = "gossip"
    FLIRT = "flirt"
    PERSONAL = "personal"
    REQUEST = "request"
    FAREWELL = "farewell"
    UNKNOWN = "unknown"


TOPIC_KEYWORDS = {
    Topic.GREETING: ["hello", "hi", "hey", "greetings", "good morning", "good evening"],
    Topic.WEATHER: ["weather", "rain", "sun", "cold", "hot", "storm"],
    Topic.WORK: ["work", "job", "trade", "business", "busy"],
    Topic.GOSSIP: ["heard", "rumor", "news", "gossip", "did you know"],
    Topic.FLIRT: ["beautiful", "handsome", "cute", "attractive", "pretty", "sexy"],
    Topic.PERSONAL: ["you", "yourself", "your", "about you", "who are you"],
    Topic.REQUEST: ["want", "need", "can you", "will you", "please"],
    Topic.FAREWELL: ["bye", "goodbye", "farewell", "later", "see you"],
}


def detect_topic(message: str) -> Topic:
    """Detect conversation topic from message."""
    msg = message.lower()
    for topic, keywords in TOPIC_KEYWORDS.items():
        if any(kw in msg for kw in keywords):
            return topic
    return Topic.UNKNOWN


# =============================================================================
# CONVERSATION MIXIN
# =============================================================================

class ConversationMixin:
    """
    Adds conversation capabilities to NPCs.
    
    Attributes to set:
        conversation_responses: Dict[Topic, List[str]]
        conversation_memory: Dict[str, List[str]]
        chattiness: int (0-100)
    """
    
    conversation_responses = AttributeProperty(default=dict)
    conversation_memory = AttributeProperty(default=dict)
    chattiness = AttributeProperty(default=50)
    last_topic = AttributeProperty(default=None)
    
    def get_response(self, topic: Topic, speaker) -> str:
        """Get a response for a topic."""
        responses = self.conversation_responses or {}
        rel = self.get_relationship(speaker) if hasattr(self, 'get_relationship') else None
        
        # Check for topic-specific responses
        topic_responses = responses.get(topic.value, [])
        
        # Modify based on relationship
        if rel:
            disp = rel.disposition.value if isinstance(rel.disposition, Disposition) else rel.disposition
            if disp < 0 and topic != Topic.FAREWELL:
                return choice([
                    "Hmph.",
                    "I have nothing to say to you.",
                    "Leave me alone.",
                ])
        
        if topic_responses:
            return choice(topic_responses)
        
        # Fallback responses
        fallbacks = {
            Topic.GREETING: ["Hello.", "Hi there.", "Greetings."],
            Topic.WEATHER: ["It's been... weather.", "I suppose so."],
            Topic.WORK: ["Work keeps me busy.", "Same as always."],
            Topic.GOSSIP: ["I don't listen to gossip.", "I wouldn't know."],
            Topic.PERSONAL: ["There's not much to tell.", "I'm just me."],
            Topic.REQUEST: ["I'll see what I can do.", "Perhaps."],
            Topic.FAREWELL: ["Goodbye.", "Until next time.", "Take care."],
            Topic.UNKNOWN: ["Hmm.", "I see.", "Interesting."],
        }
        
        return choice(fallbacks.get(topic, ["..."]))
    
    def handle_conversation(self, speaker, message: str) -> str:
        """Process a message and return response."""
        topic = detect_topic(message)
        self.last_topic = topic.value
        
        # Remember this conversation
        if not self.conversation_memory:
            self.conversation_memory = {}
        speaker_key = speaker.dbref if hasattr(speaker, 'dbref') else str(speaker)
        if speaker_key not in self.conversation_memory:
            self.conversation_memory[speaker_key] = []
        self.conversation_memory[speaker_key].append(topic.value)
        
        return self.get_response(topic, speaker)
    
    def maybe_initiate_conversation(self, characters: List) -> Optional[Tuple]:
        """Maybe start a conversation with someone."""
        if random() * 100 > self.chattiness:
            return None
        
        if not characters:
            return None
        
        target = choice(characters)
        rel = self.get_relationship(target) if hasattr(self, 'get_relationship') else None
        
        if rel:
            disp = rel.disposition.value if isinstance(rel.disposition, Disposition) else rel.disposition
            if disp < 0:
                return None
            
            if rel.familiarity > 50:
                greetings = [
                    f"Good to see you again, {target.key}.",
                    f"Ah, {target.key}. How have you been?",
                    f"Hello again, {target.key}.",
                ]
            else:
                greetings = [
                    "Hello there.",
                    "Good day.",
                    "Greetings.",
                ]
        else:
            greetings = ["Hello.", "Hi.", "Greetings."]
        
        return target, choice(greetings)


# =============================================================================
# FLIRTATION MIXIN
# =============================================================================

class FlirtationMixin:
    """
    Adds flirtation capabilities.
    
    Attributes:
        flirt_responses: Dict[str, List[str]]
        flirt_initiations: List[str]
        flirt_threshold: int (relationship attraction needed)
    """
    
    flirt_responses = AttributeProperty(default=dict)
    flirt_initiations = AttributeProperty(default=list)
    flirt_threshold = AttributeProperty(default=30)
    is_flirting_with = AttributeProperty(default=None)
    
    def handle_flirt(self, speaker, intensity: str = "mild") -> str:
        """Respond to flirtation."""
        rel = self.get_relationship(speaker) if hasattr(self, 'get_relationship') else None
        prefs = self.get_preferences() if hasattr(self, 'get_preferences') else None
        
        # Check if attracted
        if rel and prefs:
            # Check if speaker matches preferences
            speaker_body = speaker.get_body() if hasattr(speaker, 'get_body') else None
            if speaker_body:
                speaker_sex = getattr(speaker_body, 'sex', 'unknown')
                if speaker_sex not in prefs.attracted_to:
                    return choice([
                        "I'm flattered, but you're not my type.",
                        "That's... nice of you to say.",
                        "I appreciate it, but no.",
                    ])
        
        responses = self.flirt_responses or {}
        
        if rel:
            if rel.attraction > 70:
                tier = "interested"
            elif rel.attraction > 40:
                tier = "receptive"
            else:
                tier = "polite"
        else:
            tier = "polite"
        
        tier_responses = responses.get(tier, [])
        
        if tier_responses:
            response = choice(tier_responses)
        else:
            defaults = {
                "polite": ["Thank you.", "That's kind.", "You're sweet."],
                "receptive": ["Oh? Do go on...", "You're quite charming.", "I like your confidence."],
                "interested": ["Mmm, I like the sound of that.", "You know just what to say.", 
                              "Keep talking like that and..."],
            }
            response = choice(defaults.get(tier, ["..."]))
        
        # Update attraction
        if rel and hasattr(self, 'update_relationship'):
            self.update_relationship(speaker, attraction_change=randint(1, 5))
        
        return response
    
    def maybe_flirt(self, target) -> Optional[str]:
        """Maybe initiate flirtation."""
        rel = self.get_relationship(target) if hasattr(self, 'get_relationship') else None
        prefs = self.get_preferences() if hasattr(self, 'get_preferences') else None
        
        if not rel or not prefs:
            return None
        
        # Check forwardness
        if random() * 100 > prefs.forwardness:
            return None
        
        # Check attraction threshold
        if rel.attraction < self.flirt_threshold:
            return None
        
        # Check if target matches preferences
        target_body = target.get_body() if hasattr(target, 'get_body') else None
        if target_body:
            target_sex = getattr(target_body, 'sex', 'unknown')
            if target_sex not in prefs.attracted_to:
                return None
        
        initiations = self.flirt_initiations or [
            "You look nice today.",
            "Has anyone told you that you're attractive?",
            "I couldn't help but notice you...",
        ]
        
        self.is_flirting_with = target.dbref if hasattr(target, 'dbref') else str(target)
        return choice(initiations)
    
    def escalate_flirt(self, target) -> Optional[str]:
        """Escalate existing flirtation."""
        rel = self.get_relationship(target) if hasattr(self, 'get_relationship') else None
        
        if not rel or rel.attraction < 60:
            return None
        
        escalations = [
            "I find myself thinking about you...",
            "There's something about you I can't resist.",
            "I wonder what it would be like to...",
            "You're making it hard to concentrate.",
        ]
        
        return choice(escalations)


# =============================================================================
# SEXUAL BEHAVIOR MIXIN
# =============================================================================

class SexualBehaviorMixin:
    """
    Adds sexual behavior capabilities.
    
    Attributes:
        arousal_threshold: int (when to show interest)
        initiation_chance: float
        preferred_positions: List[str]
    """
    
    arousal_level = AttributeProperty(default=0)
    arousal_threshold = AttributeProperty(default=50)
    initiation_chance = AttributeProperty(default=0.1)
    preferred_positions = AttributeProperty(default=list)
    
    def get_arousal_state(self) -> str:
        """Get description of arousal state."""
        level = self.arousal_level or 0
        if level < 20:
            return "calm"
        elif level < 40:
            return "slightly aroused"
        elif level < 60:
            return "aroused"
        elif level < 80:
            return "very aroused"
        else:
            return "desperately aroused"
    
    def modify_arousal(self, amount: int):
        """Modify arousal level."""
        self.arousal_level = max(0, min(100, (self.arousal_level or 0) + amount))
    
    def should_initiate(self, target) -> bool:
        """Check if should initiate sexual activity."""
        if (self.arousal_level or 0) < self.arousal_threshold:
            return False
        
        if random() > self.initiation_chance:
            return False
        
        rel = self.get_relationship(target) if hasattr(self, 'get_relationship') else None
        if rel:
            # Need trust and attraction
            if rel.trust < 50 or rel.attraction < 50:
                return False
        
        return True
    
    def get_sexual_response(self, action: str, actor) -> str:
        """Get response to sexual action."""
        rel = self.get_relationship(actor) if hasattr(self, 'get_relationship') else None
        prefs = self.get_preferences() if hasattr(self, 'get_preferences') else None
        
        # Check limits
        if prefs and action in prefs.hard_limits:
            return choice([
                "No. Absolutely not.",
                "That's off limits.",
                "I don't do that.",
            ])
        
        # Arousal-based responses
        arousal = self.arousal_level or 0
        
        if arousal > 70:
            responses = [
                "Yes... please...",
                "More...",
                "Don't stop...",
            ]
        elif arousal > 40:
            responses = [
                "Mmm...",
                "That feels good...",
                "Keep going...",
            ]
        else:
            responses = [
                "Oh...",
                "Okay...",
                "Ah...",
            ]
        
        # Increase arousal
        self.modify_arousal(randint(5, 15))
        
        return choice(responses)


# =============================================================================
# PATHFINDING MIXIN
# =============================================================================

class PathfindingMixin:
    """
    Adds movement and following capabilities.
    
    Attributes:
        home_location: str (dbref)
        following: str (dbref)
        wander_range: int
    """
    
    home_location = AttributeProperty(default=None)
    following = AttributeProperty(default=None)
    wander_range = AttributeProperty(default=3)
    
    def follow_target(self, target) -> bool:
        """Set following target."""
        self.following = target.dbref if hasattr(target, 'dbref') else str(target)
        return True
    
    def stop_following(self):
        """Stop following."""
        self.following = None
    
    def go_home(self) -> bool:
        """Return to home location."""
        if not self.home_location:
            return False
        
        try:
            from evennia.utils.search import search_object
            home = search_object(self.home_location)
            if home:
                self.move_to(home[0])
                return True
        except Exception:
            pass
        
        return False
    
    def wander(self) -> bool:
        """Move to a random adjacent room."""
        if not self.location:
            return False
        
        exits = list(self.location.exits)
        if not exits:
            return False
        
        exit_obj = choice(exits)
        destination = exit_obj.destination
        
        if destination:
            self.move_to(destination)
            return True
        
        return False
    
    def follow_tick(self):
        """Called each tick to follow target."""
        if not self.following:
            return
        
        try:
            from evennia.utils.search import search_object
            target = search_object(self.following)
            if target and target[0].location != self.location:
                self.move_to(target[0].location)
        except Exception:
            pass


# =============================================================================
# COMBINED BEHAVIORAL NPC
# =============================================================================

class BehavioralNPC(ConversationMixin, FlirtationMixin, SexualBehaviorMixin, PathfindingMixin):
    """
    Mixin combining all behaviors.
    Add to NPC classes for full behavior support.
    """
    
    def ai_tick(self):
        """Main AI tick - handle all behaviors."""
        # Following
        if self.following:
            self.follow_tick()
            return
        
        # Sexual interest
        if self.should_initiate_check():
            return
        
        # Conversation
        if hasattr(self.location, 'get_characters'):
            chars = self.location.get_characters()
            result = self.maybe_initiate_conversation(chars)
            if result:
                target, message = result
                if self.location:
                    self.location.msg_contents(f'{self.key} says to {target.key}, "{message}"')
                return
        
        # Flirtation
        if hasattr(self.location, 'get_characters'):
            for char in self.location.get_characters():
                flirt = self.maybe_flirt(char)
                if flirt:
                    if self.location:
                        self.location.msg_contents(f'{self.key} says to {char.key}, "{flirt}"')
                    return
    
    def should_initiate_check(self) -> bool:
        """Check if should initiate sexual activity with anyone."""
        if not hasattr(self.location, 'get_characters'):
            return False
        
        for char in self.location.get_characters():
            if self.should_initiate(char):
                if self.location:
                    self.location.msg_contents(
                        f"{self.key} moves closer to {char.key} with clear intent..."
                    )
                return True
        
        return False


# =============================================================================
# FERAL BEHAVIOR MIXIN
# =============================================================================

class FeralBehaviorMixin:
    """
    Adds feral animal behaviors.
    
    Attributes:
        instincts: Dict (hunger, fear_level, aggression, arousal_level)
        territorial: bool
        territory_rooms: List[str] (dbrefs)
        pack_role: str (alpha, beta, omega, lone)
        pack_members: List[str] (dbrefs)
    """
    
    instincts = AttributeProperty(default=dict)
    territorial = AttributeProperty(default=False)
    territory_rooms = AttributeProperty(default=list)
    pack_role = AttributeProperty(default="lone")
    pack_members = AttributeProperty(default=list)
    
    def get_instinct(self, key: str, default: int = 50) -> int:
        """Get an instinct value."""
        return (self.instincts or {}).get(key, default)
    
    def set_instinct(self, key: str, value: int):
        """Set an instinct value."""
        if not self.instincts:
            self.instincts = {}
        self.instincts[key] = max(0, min(100, value))
    
    def modify_instinct(self, key: str, amount: int):
        """Modify an instinct value."""
        current = self.get_instinct(key)
        self.set_instinct(key, current + amount)
    
    def get_dominant_instinct(self) -> Tuple[str, int]:
        """Get the strongest instinct."""
        instincts = self.instincts or {}
        if not instincts:
            return "idle", 0
        
        dominant = max(instincts.items(), key=lambda x: x[1])
        return dominant
    
    def react_to_stranger(self, stranger) -> str:
        """React when a stranger enters territory/space."""
        fear = self.get_instinct("fear_level", 30)
        aggression = self.get_instinct("aggression", 30)
        
        if fear > 70:
            return "cower"
        elif aggression > 70:
            return "aggressive"
        elif fear > aggression:
            return "wary"
        else:
            return "curious"
    
    def react_to_pet(self, petter) -> str:
        """React to being petted."""
        rel = self.get_relationship(petter) if hasattr(self, 'get_relationship') else None
        trust = rel.trust if rel else 30
        fear = self.get_instinct("fear_level", 50)
        
        if trust > 70:
            self.modify_instinct("fear_level", -5)
            return "happy"
        elif trust > 40:
            self.modify_instinct("fear_level", -2)
            return "tolerant"
        elif fear > 60:
            return "flinch"
        else:
            return "wary"
    
    def react_to_feed(self, feeder) -> str:
        """React to being fed."""
        hunger = self.get_instinct("hunger", 50)
        
        if hunger > 70:
            return "eager"
        elif hunger > 40:
            return "interested"
        else:
            return "sniff"
    
    def tick_instincts(self):
        """Called periodically to update instincts."""
        # Hunger increases slowly
        self.modify_instinct("hunger", 1)
        
        # Fear decays slowly
        fear = self.get_instinct("fear_level", 50)
        if fear > 30:
            self.modify_instinct("fear_level", -1)
        
        # Arousal decays slowly unless in heat
        if not (hasattr(self, 'is_in_heat') and self.is_in_heat()):
            arousal = self.get_instinct("arousal_level", 0)
            if arousal > 0:
                self.modify_instinct("arousal_level", -2)
    
    def is_hungry(self) -> bool:
        return self.get_instinct("hunger", 50) > 60
    
    def is_afraid(self) -> bool:
        return self.get_instinct("fear_level", 50) > 60
    
    def is_aroused(self) -> bool:
        return self.get_instinct("arousal_level", 0) > 50
    
    def calm_down(self, amount: int = 20):
        """Reduce fear and aggression."""
        self.modify_instinct("fear_level", -amount)
        self.modify_instinct("aggression", -amount // 2)


# =============================================================================
# PACK BEHAVIOR MIXIN
# =============================================================================

class PackBehaviorMixin:
    """
    Adds pack dynamics for feral animals.
    
    Attributes:
        pack_id: str (identifier for pack)
        pack_role: str (alpha, beta, omega, lone)
        pack_loyalty: int (0-100)
    """
    
    pack_id = AttributeProperty(default=None)
    pack_role = AttributeProperty(default="lone")
    pack_loyalty = AttributeProperty(default=50)
    
    def is_in_pack(self) -> bool:
        return bool(self.pack_id)
    
    def is_alpha(self) -> bool:
        return self.pack_role == "alpha"
    
    def get_pack_members(self) -> List:
        """Get other members of this pack in same location."""
        if not self.pack_id or not self.location:
            return []
        
        members = []
        for obj in self.location.contents:
            if hasattr(obj, 'pack_id') and obj.pack_id == self.pack_id:
                if obj != self:
                    members.append(obj)
        return members
    
    def follow_alpha(self) -> bool:
        """Follow pack alpha if present."""
        if self.is_alpha():
            return False
        
        for member in self.get_pack_members():
            if member.pack_role == "alpha":
                self.following = member.dbref
                return True
        return False
    
    def respond_to_alpha_call(self) -> Optional[str]:
        """Respond when alpha calls."""
        if self.is_alpha():
            return None
        
        responses = {
            "alpha": None,
            "beta": "perks up and moves closer",
            "omega": "submissively approaches",
            "lone": None,
        }
        return responses.get(self.pack_role)
    
    def assert_dominance(self, target) -> str:
        """Assert dominance over another pack member."""
        if not hasattr(target, 'pack_role'):
            return "ignore"
        
        my_rank = {"alpha": 4, "beta": 3, "omega": 1, "lone": 2}
        their_rank = {"alpha": 4, "beta": 3, "omega": 1, "lone": 2}
        
        my_r = my_rank.get(self.pack_role, 2)
        their_r = their_rank.get(target.pack_role, 2)
        
        if my_r > their_r:
            return "dominate"
        elif my_r < their_r:
            return "submit"
        else:
            return "challenge"
    
    def pack_howl(self) -> str:
        """Emit a pack howl/call."""
        if self.is_alpha():
            return f"{self.key} raises their head and lets out a commanding howl."
        else:
            return f"{self.key} joins in with a responding howl."


# =============================================================================
# TERRITORY BEHAVIOR MIXIN
# =============================================================================

class TerritoryBehaviorMixin:
    """
    Adds territorial behaviors.
    
    Attributes:
        territory_rooms: List[str] (dbrefs of territory rooms)
        territory_aggression: int (how aggressive about territory)
        marking_interval: int (how often to mark)
    """
    
    territory_rooms = AttributeProperty(default=list)
    territory_aggression = AttributeProperty(default=30)
    marking_interval = AttributeProperty(default=3600)
    last_marking = AttributeProperty(default=None)
    
    def is_in_territory(self) -> bool:
        """Check if currently in owned territory."""
        if not self.location or not self.territory_rooms:
            return False
        return self.location.dbref in self.territory_rooms
    
    def add_territory(self, room):
        """Add a room to territory."""
        if not self.territory_rooms:
            self.territory_rooms = []
        dbref = room.dbref if hasattr(room, 'dbref') else str(room)
        if dbref not in self.territory_rooms:
            self.territory_rooms.append(dbref)
    
    def remove_territory(self, room):
        """Remove a room from territory."""
        dbref = room.dbref if hasattr(room, 'dbref') else str(room)
        if self.territory_rooms and dbref in self.territory_rooms:
            self.territory_rooms.remove(dbref)
    
    def react_to_intruder(self, intruder) -> str:
        """React to intruder in territory."""
        if not self.is_in_territory():
            return "ignore"
        
        aggression = self.territory_aggression
        
        # Check if intruder is known
        if hasattr(self, 'get_relationship'):
            rel = self.get_relationship(intruder)
            if rel.trust > 70:
                return "allow"
            elif rel.trust > 40:
                return "watch"
        
        if aggression > 70:
            return "attack"
        elif aggression > 40:
            return "threaten"
        else:
            return "watch"
    
    def mark_territory(self) -> str:
        """Mark territory (scent marking)."""
        from datetime import datetime
        self.last_marking = datetime.now()
        return f"{self.key} marks their territory."
    
    def should_mark(self) -> bool:
        """Check if should mark territory."""
        if not self.is_in_territory():
            return False
        
        if not self.last_marking:
            return True
        
        from datetime import datetime
        elapsed = (datetime.now() - self.last_marking).total_seconds()
        return elapsed >= self.marking_interval


# =============================================================================
# HUNTING BEHAVIOR MIXIN
# =============================================================================

class HuntingBehaviorMixin:
    """
    Adds hunting behaviors for predatory ferals.
    
    Attributes:
        is_predator: bool
        prey_species: List[str]
        hunt_skill: int (0-100)
    """
    
    is_predator = AttributeProperty(default=True)
    prey_species = AttributeProperty(default=list)
    hunt_skill = AttributeProperty(default=50)
    is_hunting = AttributeProperty(default=False)
    
    def can_hunt(self, target) -> bool:
        """Check if target is valid prey."""
        if not self.is_predator:
            return False
        
        body = target.get_body() if hasattr(target, 'get_body') else None
        if not body:
            return False
        
        species = getattr(body, 'species_key', '')
        if self.prey_species and species not in self.prey_species:
            return False
        
        return True
    
    def stalk(self, target) -> str:
        """Stalk prey."""
        self.is_hunting = True
        return f"{self.key} begins stalking {target.key}."
    
    def pounce(self, target) -> Tuple[bool, str]:
        """Attempt to pounce on prey."""
        skill = self.hunt_skill
        roll = randint(1, 100)
        
        if roll <= skill:
            return True, f"{self.key} pounces on {target.key}!"
        else:
            return False, f"{self.key} misses their pounce on {target.key}!"
    
    def give_up_hunt(self):
        """Stop hunting."""
        self.is_hunting = False


# =============================================================================
# MATING BEHAVIOR MIXIN
# =============================================================================

class MatingBehaviorMixin:
    """
    Adds mating behaviors for ferals.
    
    Works with heat cycle system.
    """
    
    seeking_mate = AttributeProperty(default=False)
    courting = AttributeProperty(default=None)  # dbref of target
    
    def is_receptive(self) -> bool:
        """Check if receptive to mating."""
        if hasattr(self, 'is_in_heat') and self.is_in_heat():
            return True
        
        arousal = 0
        if hasattr(self, 'get_instinct'):
            arousal = self.get_instinct("arousal_level", 0)
        
        return arousal > 70
    
    def find_mate(self) -> Optional:
        """Find potential mate in room."""
        if not self.location:
            return None
        
        for obj in self.location.contents:
            if obj == self:
                continue
            
            # Check if compatible
            if hasattr(obj, 'is_receptive') and obj.is_receptive():
                return obj
        
        return None
    
    def court(self, target) -> str:
        """Begin courting behavior."""
        self.courting = target.dbref if hasattr(target, 'dbref') else str(target)
        
        messages = [
            f"{self.key} approaches {target.key} with interest.",
            f"{self.key} sniffs at {target.key} curiously.",
            f"{self.key} circles around {target.key}.",
        ]
        return choice(messages)
    
    def respond_to_courting(self, suitor) -> str:
        """Respond to being courted."""
        if not self.is_receptive():
            return f"{self.key} rebuffs {suitor.key}'s advances."
        
        # Check attraction
        rel = self.get_relationship(suitor) if hasattr(self, 'get_relationship') else None
        
        if rel and rel.attraction > 50:
            return f"{self.key} responds favorably to {suitor.key}'s attention."
        else:
            return f"{self.key} seems uncertain about {suitor.key}."
    
    def present_to_mate(self) -> str:
        """Present for mating."""
        return f"{self.key} presents themselves invitingly."


# =============================================================================
# COMBINED FERAL NPC
# =============================================================================

class FullFeralBehavior(
    FeralBehaviorMixin,
    PackBehaviorMixin,
    TerritoryBehaviorMixin,
    HuntingBehaviorMixin,
    MatingBehaviorMixin,
    PathfindingMixin
):
    """
    Mixin combining all feral behaviors.
    Add to FeralNPC classes for full behavior support.
    """
    
    def feral_ai_tick(self):
        """Main AI tick for feral behaviors."""
        # Update instincts
        if hasattr(self, 'tick_instincts'):
            self.tick_instincts()
        
        # Check dominant instinct
        instinct, level = self.get_dominant_instinct()
        
        # Hunger - seek food
        if instinct == "hunger" and level > 70:
            if self.is_hungry():
                # Look for food or beg from characters
                chars = self.location.get_characters() if hasattr(self.location, 'get_characters') else []
                if chars:
                    target = choice(chars)
                    self.location.msg_contents(
                        f"{self.key} looks hungrily at {target.key}."
                    )
                return
        
        # Fear - flee or cower
        if instinct == "fear_level" and level > 70:
            if self.is_afraid():
                if random() > 0.7:
                    self.wander()
                return
        
        # Arousal - seek mate
        if instinct == "arousal_level" and level > 60:
            if self.is_receptive():
                mate = self.find_mate()
                if mate:
                    msg = self.court(mate)
                    self.location.msg_contents(msg)
                return
        
        # Territory marking
        if hasattr(self, 'should_mark') and self.should_mark():
            msg = self.mark_territory()
            self.location.msg_contents(msg)
            return
        
        # Pack behavior
        if self.is_in_pack() and not self.is_alpha():
            if random() > 0.8:
                self.follow_alpha()
                return
        
        # Random wandering
        if random() > 0.9:
            self.wander()


__all__ = [
    "Topic", "TOPIC_KEYWORDS", "detect_topic",
    "ConversationMixin", "FlirtationMixin",
    "SexualBehaviorMixin", "PathfindingMixin",
    "BehavioralNPC",
    "FeralBehaviorMixin", "PackBehaviorMixin",
    "TerritoryBehaviorMixin", "HuntingBehaviorMixin",
    "MatingBehaviorMixin", "FullFeralBehavior",
]
