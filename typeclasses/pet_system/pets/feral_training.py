"""
Feral Training System
=====================

Advanced trick training for feral pets:
- Trainable tricks with difficulty levels
- Training sessions with progress tracking
- Mastery system
- Species-specific tricks
"""

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any, Tuple
from enum import Enum
import random

from .feral_stats import PetStats, TrainingLevel


# =============================================================================
# TRICK DEFINITIONS
# =============================================================================

class TrickCategory(Enum):
    """Categories of tricks."""
    BASIC = "basic"           # Simple obedience
    MOVEMENT = "movement"     # Gaits, positions
    INTERACTION = "interaction"  # Social behaviors
    UTILITY = "utility"       # Useful commands
    COMBAT = "combat"         # Aggressive commands
    SEXUAL = "sexual"         # Breeding/mating behaviors
    PERFORMANCE = "performance"  # Show tricks
    PONY = "pony"             # Pony-specific
    CANINE = "canine"         # Dog-specific


@dataclass
class Trick:
    """Definition of a trainable trick."""
    key: str
    name: str
    category: TrickCategory
    difficulty: int  # 1-10
    
    # Commands
    command_phrase: str
    aliases: List[str] = field(default_factory=list)
    
    # Requirements
    requires_tricks: List[str] = field(default_factory=list)  # Must know these first
    species_required: List[str] = field(default_factory=list)  # Only these species
    species_bonus: List[str] = field(default_factory=list)  # Easier for these
    
    # Training
    base_sessions_needed: int = 3  # Sessions to learn
    mastery_sessions: int = 10     # Additional sessions to master
    
    # Effects
    description: str = ""
    success_msg: str = ""
    failure_msg: str = ""
    
    # Flags
    requires_target: bool = False
    requires_object: bool = False
    is_sexual: bool = False


# =============================================================================
# TRICK LIBRARY
# =============================================================================

TRICKS: Dict[str, Trick] = {
    # ----- BASIC TRICKS -----
    "sit": Trick(
        key="sit",
        name="Sit",
        category=TrickCategory.BASIC,
        difficulty=1,
        command_phrase="Sit!",
        aliases=["sit down"],
        base_sessions_needed=1,
        description="The pet sits on their haunches.",
        success_msg="{pet} obediently sits down.",
        failure_msg="{pet} ignores the command.",
    ),
    "stay": Trick(
        key="stay",
        name="Stay",
        category=TrickCategory.BASIC,
        difficulty=2,
        command_phrase="Stay!",
        requires_tricks=["sit"],
        base_sessions_needed=2,
        description="The pet remains in place until released.",
        success_msg="{pet} stays put, waiting obediently.",
        failure_msg="{pet} fidgets and moves despite the command.",
    ),
    "come": Trick(
        key="come",
        name="Come",
        category=TrickCategory.BASIC,
        difficulty=1,
        command_phrase="Come!",
        aliases=["here", "come here"],
        base_sessions_needed=1,
        description="The pet comes to the handler.",
        success_msg="{pet} trots over eagerly.",
        failure_msg="{pet} stays where they are.",
    ),
    "down": Trick(
        key="down",
        name="Down",
        category=TrickCategory.BASIC,
        difficulty=2,
        command_phrase="Down!",
        aliases=["lie down", "lay"],
        base_sessions_needed=2,
        description="The pet lies down.",
        success_msg="{pet} drops to the ground.",
        failure_msg="{pet} remains standing.",
    ),
    "heel": Trick(
        key="heel",
        name="Heel",
        category=TrickCategory.BASIC,
        difficulty=3,
        command_phrase="Heel!",
        requires_tricks=["come"],
        base_sessions_needed=3,
        description="The pet walks alongside the handler.",
        success_msg="{pet} falls in step beside you.",
        failure_msg="{pet} wanders off instead.",
    ),
    
    # ----- MOVEMENT TRICKS -----
    "roll_over": Trick(
        key="roll_over",
        name="Roll Over",
        category=TrickCategory.MOVEMENT,
        difficulty=3,
        command_phrase="Roll over!",
        requires_tricks=["down"],
        base_sessions_needed=4,
        description="The pet rolls onto their back.",
        success_msg="{pet} rolls over, exposing their belly.",
        failure_msg="{pet} just lies there.",
    ),
    "shake": Trick(
        key="shake",
        name="Shake",
        category=TrickCategory.MOVEMENT,
        difficulty=2,
        command_phrase="Shake!",
        aliases=["paw", "give paw"],
        requires_tricks=["sit"],
        base_sessions_needed=2,
        description="The pet offers their paw.",
        success_msg="{pet} offers their paw politely.",
        failure_msg="{pet} keeps their paws to themselves.",
    ),
    "spin": Trick(
        key="spin",
        name="Spin",
        category=TrickCategory.MOVEMENT,
        difficulty=3,
        command_phrase="Spin!",
        base_sessions_needed=3,
        description="The pet spins in a circle.",
        success_msg="{pet} spins around excitedly.",
        failure_msg="{pet} looks confused.",
    ),
    "crawl": Trick(
        key="crawl",
        name="Crawl",
        category=TrickCategory.MOVEMENT,
        difficulty=4,
        command_phrase="Crawl!",
        requires_tricks=["down"],
        base_sessions_needed=5,
        description="The pet crawls forward on their belly.",
        success_msg="{pet} crawls forward submissively.",
        failure_msg="{pet} refuses to crawl.",
    ),
    "jump": Trick(
        key="jump",
        name="Jump",
        category=TrickCategory.MOVEMENT,
        difficulty=3,
        command_phrase="Jump!",
        aliases=["up", "hup"],
        base_sessions_needed=3,
        description="The pet jumps up.",
        success_msg="{pet} leaps into the air.",
        failure_msg="{pet} stays grounded.",
    ),
    
    # ----- INTERACTION TRICKS -----
    "speak": Trick(
        key="speak",
        name="Speak",
        category=TrickCategory.INTERACTION,
        difficulty=2,
        command_phrase="Speak!",
        aliases=["bark", "voice"],
        base_sessions_needed=2,
        description="The pet vocalizes on command.",
        success_msg="{pet} barks/vocalizes loudly.",
        failure_msg="{pet} remains silent.",
        species_bonus=["wolf", "dog", "fox", "hyena"],
    ),
    "quiet": Trick(
        key="quiet",
        name="Quiet",
        category=TrickCategory.INTERACTION,
        difficulty=3,
        command_phrase="Quiet!",
        aliases=["shush", "silence"],
        requires_tricks=["speak"],
        base_sessions_needed=3,
        description="The pet stops vocalizing.",
        success_msg="{pet} falls silent.",
        failure_msg="{pet} continues making noise.",
    ),
    "beg": Trick(
        key="beg",
        name="Beg",
        category=TrickCategory.INTERACTION,
        difficulty=3,
        command_phrase="Beg!",
        requires_tricks=["sit"],
        base_sessions_needed=4,
        description="The pet sits up and begs.",
        success_msg="{pet} sits up on their haunches, begging adorably.",
        failure_msg="{pet} just sits there.",
    ),
    "kiss": Trick(
        key="kiss",
        name="Kiss",
        category=TrickCategory.INTERACTION,
        difficulty=2,
        command_phrase="Kiss!",
        aliases=["lick", "give kiss"],
        base_sessions_needed=2,
        requires_target=True,
        description="The pet licks the target.",
        success_msg="{pet} licks {target} affectionately.",
        failure_msg="{pet} turns away.",
    ),
    "nuzzle": Trick(
        key="nuzzle",
        name="Nuzzle",
        category=TrickCategory.INTERACTION,
        difficulty=2,
        command_phrase="Nuzzle!",
        base_sessions_needed=2,
        requires_target=True,
        description="The pet nuzzles against the target.",
        success_msg="{pet} nuzzles against {target} warmly.",
        failure_msg="{pet} ignores the command.",
    ),
    
    # ----- UTILITY TRICKS -----
    "fetch": Trick(
        key="fetch",
        name="Fetch",
        category=TrickCategory.UTILITY,
        difficulty=4,
        command_phrase="Fetch!",
        aliases=["get it", "retrieve"],
        requires_tricks=["come"],
        base_sessions_needed=5,
        requires_object=True,
        description="The pet retrieves an object.",
        success_msg="{pet} retrieves the {object} and brings it back.",
        failure_msg="{pet} ignores the thrown object.",
        species_bonus=["dog", "wolf", "fox"],
    ),
    "drop_it": Trick(
        key="drop_it",
        name="Drop It",
        category=TrickCategory.UTILITY,
        difficulty=3,
        command_phrase="Drop it!",
        aliases=["drop", "release", "let go"],
        base_sessions_needed=3,
        description="The pet releases what they're holding.",
        success_msg="{pet} drops the item obediently.",
        failure_msg="{pet} keeps hold of it.",
    ),
    "find": Trick(
        key="find",
        name="Find",
        category=TrickCategory.UTILITY,
        difficulty=5,
        command_phrase="Find!",
        aliases=["search", "seek"],
        requires_tricks=["come"],
        base_sessions_needed=6,
        requires_target=True,
        description="The pet searches for someone/something.",
        success_msg="{pet} sniffs around and locates {target}.",
        failure_msg="{pet} can't find the scent.",
        species_bonus=["wolf", "dog", "fox", "hyena"],
    ),
    "guard": Trick(
        key="guard",
        name="Guard",
        category=TrickCategory.UTILITY,
        difficulty=6,
        command_phrase="Guard!",
        aliases=["watch", "protect"],
        requires_tricks=["stay"],
        base_sessions_needed=8,
        description="The pet guards a location or person.",
        success_msg="{pet} takes up a protective stance, alert and watchful.",
        failure_msg="{pet} loses focus.",
    ),
    "track": Trick(
        key="track",
        name="Track",
        category=TrickCategory.UTILITY,
        difficulty=6,
        command_phrase="Track!",
        aliases=["trail", "follow scent"],
        requires_tricks=["find"],
        base_sessions_needed=8,
        description="The pet follows a scent trail.",
        success_msg="{pet} puts nose to ground and follows the trail.",
        failure_msg="{pet} loses the scent.",
        species_bonus=["wolf", "dog", "fox", "hyena"],
    ),
    
    # ----- COMBAT TRICKS -----
    "attack": Trick(
        key="attack",
        name="Attack",
        category=TrickCategory.COMBAT,
        difficulty=7,
        command_phrase="Attack!",
        aliases=["sic", "kill"],
        requires_tricks=["guard"],
        base_sessions_needed=10,
        requires_target=True,
        description="The pet attacks a target.",
        success_msg="{pet} lunges at {target} with teeth bared!",
        failure_msg="{pet} hesitates, unwilling to attack.",
    ),
    "hold": Trick(
        key="hold",
        name="Hold",
        category=TrickCategory.COMBAT,
        difficulty=6,
        command_phrase="Hold!",
        aliases=["pin", "restrain"],
        requires_tricks=["attack"],
        base_sessions_needed=8,
        requires_target=True,
        description="The pet pins down a target.",
        success_msg="{pet} pins {target} to the ground.",
        failure_msg="{pet} can't get a grip.",
    ),
    "release_target": Trick(
        key="release_target",
        name="Release",
        category=TrickCategory.COMBAT,
        difficulty=5,
        command_phrase="Release!",
        aliases=["let them go", "off"],
        requires_tricks=["hold"],
        base_sessions_needed=5,
        description="The pet releases their grip on a target.",
        success_msg="{pet} releases {target} and backs off.",
        failure_msg="{pet} refuses to let go.",
    ),
    
    # ----- SEXUAL TRICKS -----
    "present": Trick(
        key="present",
        name="Present",
        category=TrickCategory.SEXUAL,
        difficulty=4,
        command_phrase="Present!",
        aliases=["show", "display"],
        requires_tricks=["down"],
        base_sessions_needed=5,
        description="The pet presents their hindquarters.",
        success_msg="{pet} turns and presents, tail raised invitingly.",
        failure_msg="{pet} refuses to present.",
        is_sexual=True,
    ),
    "mount": Trick(
        key="mount",
        name="Mount",
        category=TrickCategory.SEXUAL,
        difficulty=5,
        command_phrase="Mount!",
        aliases=["breed", "take"],
        base_sessions_needed=6,
        requires_target=True,
        description="The pet mounts a target.",
        success_msg="{pet} mounts {target}, gripping their hips.",
        failure_msg="{pet} seems uninterested.",
        is_sexual=True,
    ),
    "dismount": Trick(
        key="dismount",
        name="Dismount",
        category=TrickCategory.SEXUAL,
        difficulty=4,
        command_phrase="Dismount!",
        aliases=["off", "down boy"],
        requires_tricks=["mount"],
        base_sessions_needed=4,
        description="The pet dismounts from their partner.",
        success_msg="{pet} pulls out and dismounts.",
        failure_msg="{pet} refuses to stop.",
        is_sexual=True,
    ),
    "knot": Trick(
        key="knot",
        name="Knot",
        category=TrickCategory.SEXUAL,
        difficulty=6,
        command_phrase="Knot!",
        aliases=["tie", "lock"],
        requires_tricks=["mount"],
        base_sessions_needed=7,
        requires_target=True,
        description="The pet pushes their knot in (if applicable).",
        success_msg="{pet} drives forward, knotting {target} deeply.",
        failure_msg="{pet} can't manage to tie.",
        is_sexual=True,
        species_required=["wolf", "dog", "fox", "hyena"],
    ),
    "service": Trick(
        key="service",
        name="Service",
        category=TrickCategory.SEXUAL,
        difficulty=5,
        command_phrase="Service!",
        aliases=["lick", "pleasure"],
        requires_tricks=["kiss"],
        base_sessions_needed=6,
        requires_target=True,
        description="The pet orally services a target.",
        success_msg="{pet} eagerly services {target} with their tongue.",
        failure_msg="{pet} turns away.",
        is_sexual=True,
    ),
    "breed_stand": Trick(
        key="breed_stand",
        name="Breed Stand",
        category=TrickCategory.SEXUAL,
        difficulty=5,
        command_phrase="Stand for breeding!",
        aliases=["breed stand", "brace"],
        requires_tricks=["stay", "present"],
        base_sessions_needed=6,
        description="The pet braces for breeding, remaining still.",
        success_msg="{pet} braces themselves, ready to be bred.",
        failure_msg="{pet} keeps moving around.",
        is_sexual=True,
    ),
    
    # ----- PERFORMANCE TRICKS -----
    "play_dead": Trick(
        key="play_dead",
        name="Play Dead",
        category=TrickCategory.PERFORMANCE,
        difficulty=4,
        command_phrase="Play dead!",
        aliases=["bang", "dead"],
        requires_tricks=["roll_over"],
        base_sessions_needed=5,
        description="The pet falls over and plays dead.",
        success_msg="{pet} dramatically collapses and lies still.",
        failure_msg="{pet} just looks at you.",
    ),
    "dance": Trick(
        key="dance",
        name="Dance",
        category=TrickCategory.PERFORMANCE,
        difficulty=5,
        command_phrase="Dance!",
        requires_tricks=["spin", "jump"],
        base_sessions_needed=7,
        description="The pet dances on hind legs.",
        success_msg="{pet} prances around on their hind legs.",
        failure_msg="{pet} stumbles.",
    ),
    "bow": Trick(
        key="bow",
        name="Bow",
        category=TrickCategory.PERFORMANCE,
        difficulty=3,
        command_phrase="Bow!",
        base_sessions_needed=3,
        description="The pet bows with front legs extended.",
        success_msg="{pet} stretches into an elegant play bow.",
        failure_msg="{pet} doesn't understand.",
    ),
    "circle": Trick(
        key="circle",
        name="Circle",
        category=TrickCategory.PERFORMANCE,
        difficulty=4,
        command_phrase="Circle!",
        aliases=["around"],
        requires_tricks=["heel"],
        base_sessions_needed=5,
        requires_target=True,
        description="The pet circles around the target.",
        success_msg="{pet} trots in a circle around {target}.",
        failure_msg="{pet} wanders off course.",
    ),
    
    # ----- PONY TRICKS -----
    "trot": Trick(
        key="trot",
        name="Trot",
        category=TrickCategory.PONY,
        difficulty=3,
        command_phrase="Trot!",
        base_sessions_needed=4,
        description="The pony moves at a trot.",
        success_msg="{pet} breaks into a smart trot.",
        failure_msg="{pet} maintains their current gait.",
        species_required=["horse", "pony", "donkey", "zebra", "unicorn"],
    ),
    "canter": Trick(
        key="canter",
        name="Canter",
        category=TrickCategory.PONY,
        difficulty=4,
        command_phrase="Canter!",
        requires_tricks=["trot"],
        base_sessions_needed=5,
        description="The pony moves at a canter.",
        success_msg="{pet} transitions into a smooth canter.",
        failure_msg="{pet} can't maintain the gait.",
        species_required=["horse", "pony", "donkey", "zebra", "unicorn"],
    ),
    "gallop": Trick(
        key="gallop",
        name="Gallop",
        category=TrickCategory.PONY,
        difficulty=5,
        command_phrase="Gallop!",
        requires_tricks=["canter"],
        base_sessions_needed=6,
        description="The pony moves at full gallop.",
        success_msg="{pet} surges into a thundering gallop.",
        failure_msg="{pet} stumbles at the faster pace.",
        species_required=["horse", "pony", "donkey", "zebra", "unicorn"],
    ),
    "halt": Trick(
        key="halt",
        name="Halt",
        category=TrickCategory.PONY,
        difficulty=3,
        command_phrase="Whoa!",
        aliases=["halt", "stop"],
        base_sessions_needed=3,
        description="The pony stops immediately.",
        success_msg="{pet} comes to an immediate halt.",
        failure_msg="{pet} takes a few more steps before stopping.",
        species_required=["horse", "pony", "donkey", "zebra", "unicorn"],
    ),
    "rear": Trick(
        key="rear",
        name="Rear",
        category=TrickCategory.PONY,
        difficulty=5,
        command_phrase="Up!",
        aliases=["rear"],
        base_sessions_needed=6,
        description="The pony rears up on hind legs.",
        success_msg="{pet} rears up majestically, hooves pawing the air.",
        failure_msg="{pet} refuses to rear.",
        species_required=["horse", "pony", "donkey", "zebra", "unicorn"],
    ),
    "kneel_pony": Trick(
        key="kneel_pony",
        name="Kneel",
        category=TrickCategory.PONY,
        difficulty=4,
        command_phrase="Kneel!",
        base_sessions_needed=5,
        description="The pony kneels for mounting/dismounting.",
        success_msg="{pet} kneels down, making it easy to mount.",
        failure_msg="{pet} stays standing.",
        species_required=["horse", "pony", "donkey", "zebra", "unicorn"],
    ),
}


# =============================================================================
# TRAINING SESSION
# =============================================================================

@dataclass
class TrainingSession:
    """Tracks a training session in progress."""
    trick_key: str
    trainer_dbref: str
    pet_dbref: str
    
    # Progress
    sessions_completed: int = 0
    successful_attempts: int = 0
    failed_attempts: int = 0
    
    # State
    is_learned: bool = False
    is_mastered: bool = False
    
    def get_trick(self) -> Optional[Trick]:
        """Get the trick being trained."""
        return TRICKS.get(self.trick_key)
    
    def get_progress_percentage(self) -> float:
        """Get training progress as percentage."""
        trick = self.get_trick()
        if not trick:
            return 0.0
        
        if self.is_mastered:
            return 100.0
        elif self.is_learned:
            mastery_progress = (self.sessions_completed - trick.base_sessions_needed) / trick.mastery_sessions
            return 50.0 + (mastery_progress * 50.0)
        else:
            learn_progress = self.sessions_completed / trick.base_sessions_needed
            return min(50.0, learn_progress * 50.0)
    
    def to_dict(self) -> dict:
        return {
            "trick_key": self.trick_key,
            "trainer_dbref": self.trainer_dbref,
            "pet_dbref": self.pet_dbref,
            "sessions_completed": self.sessions_completed,
            "successful_attempts": self.successful_attempts,
            "failed_attempts": self.failed_attempts,
            "is_learned": self.is_learned,
            "is_mastered": self.is_mastered,
        }
    
    @classmethod
    def from_dict(cls, data: dict) -> "TrainingSession":
        return cls(**data)


# =============================================================================
# TRAINING SYSTEM
# =============================================================================

class TrainingSystem:
    """
    Handles training pets in tricks.
    """
    
    @staticmethod
    def get_available_tricks(pet, trainer) -> List[Trick]:
        """
        Get list of tricks available to train.
        
        Returns tricks the pet:
        - Doesn't already know
        - Meets prerequisites for
        - Is the right species for
        """
        stats = pet.pet_stats
        available = []
        
        for key, trick in TRICKS.items():
            # Skip if already mastered
            if key in stats.tricks_mastered:
                continue
            
            # Check species requirements
            if trick.species_required:
                pet_species = getattr(pet, 'species', None)
                if pet_species and pet_species not in trick.species_required:
                    continue
            
            # Check prerequisites
            if trick.requires_tricks:
                if not all(req in stats.tricks_learned for req in trick.requires_tricks):
                    continue
            
            available.append(trick)
        
        return available
    
    @staticmethod
    def can_train_trick(pet, trick_key: str) -> Tuple[bool, str]:
        """
        Check if pet can learn a specific trick.
        
        Returns:
            (can_train: bool, reason: str)
        """
        trick = TRICKS.get(trick_key)
        if not trick:
            return False, f"Unknown trick: {trick_key}"
        
        stats = pet.pet_stats
        
        # Already mastered
        if trick_key in stats.tricks_mastered:
            return False, f"{pet.key} has already mastered {trick.name}."
        
        # Check species
        if trick.species_required:
            pet_species = getattr(pet, 'species', None)
            if pet_species and pet_species not in trick.species_required:
                return False, f"{trick.name} can only be taught to {', '.join(trick.species_required)}."
        
        # Check prerequisites
        if trick.requires_tricks:
            missing = [t for t in trick.requires_tricks if t not in stats.tricks_learned]
            if missing:
                missing_names = [TRICKS[m].name for m in missing if m in TRICKS]
                return False, f"{pet.key} must first learn: {', '.join(missing_names)}"
        
        return True, ""
    
    @staticmethod
    def get_or_create_session(pet, trick_key: str, trainer) -> TrainingSession:
        """Get existing training session or create new one."""
        # Check for existing session in pet's attributes
        sessions_data = pet.attributes.get("training_sessions", {})
        
        if trick_key in sessions_data:
            return TrainingSession.from_dict(sessions_data[trick_key])
        
        # Create new session
        session = TrainingSession(
            trick_key=trick_key,
            trainer_dbref=trainer.dbref,
            pet_dbref=pet.dbref,
        )
        
        # Save
        sessions_data[trick_key] = session.to_dict()
        pet.attributes.add("training_sessions", sessions_data)
        
        return session
    
    @staticmethod
    def save_session(pet, session: TrainingSession):
        """Save training session."""
        sessions_data = pet.attributes.get("training_sessions", {})
        sessions_data[session.trick_key] = session.to_dict()
        pet.attributes.add("training_sessions", sessions_data)
    
    @staticmethod
    def conduct_training(pet, trick_key: str, trainer) -> Tuple[bool, str]:
        """
        Conduct a training session.
        
        Returns:
            (success: bool, message: str)
        """
        # Verify can train
        can_train, reason = TrainingSystem.can_train_trick(pet, trick_key)
        if not can_train:
            return False, reason
        
        trick = TRICKS[trick_key]
        stats = pet.pet_stats
        session = TrainingSystem.get_or_create_session(pet, trick_key, trainer)
        
        # Calculate success chance
        base_chance = 50
        
        # Obedience modifier
        base_chance += (stats.obedience - 50) // 2
        
        # Difficulty modifier
        base_chance -= trick.difficulty * 5
        
        # Bond modifier
        from .feral_stats import BondLevel
        bond_mods = {
            BondLevel.NONE: -30,
            BondLevel.WARY: -15,
            BondLevel.TOLERANT: 0,
            BondLevel.FRIENDLY: 10,
            BondLevel.BONDED: 20,
            BondLevel.DEVOTED: 30,
            BondLevel.SOULBOUND: 40,
        }
        base_chance += bond_mods.get(stats.bond_level, 0)
        
        # Species bonus
        pet_species = getattr(pet, 'species', None)
        if pet_species and pet_species in trick.species_bonus:
            base_chance += 15
        
        # Energy penalty
        if stats.energy < 30:
            base_chance -= 20
        elif stats.energy < 60:
            base_chance -= 10
        
        # Mood effects
        from .feral_stats import PetMood
        mood_mods = {
            PetMood.ECSTATIC: 15,
            PetMood.HAPPY: 10,
            PetMood.CONTENT: 0,
            PetMood.ANXIOUS: -10,
            PetMood.FEARFUL: -20,
            PetMood.AGGRESSIVE: -25,
            PetMood.DEPRESSED: -15,
            PetMood.AROUSED: -5,
            PetMood.EXHAUSTED: -30,
        }
        base_chance += mood_mods.get(stats.mood, 0)
        
        # Roll
        roll = random.randint(1, 100)
        success = roll <= base_chance
        
        # Update session
        if success:
            session.successful_attempts += 1
            session.sessions_completed += 1
        else:
            session.failed_attempts += 1
            # Failed attempts still give partial progress
            if random.random() < 0.3:
                session.sessions_completed += 1
        
        # Check for learning
        messages = []
        
        if not session.is_learned:
            if session.sessions_completed >= trick.base_sessions_needed:
                session.is_learned = True
                stats.tricks_learned.append(trick_key)
                stats.update_training_level()
                messages.append(f"|g{pet.key} has learned {trick.name}!|n")
        
        # Check for mastery
        if session.is_learned and not session.is_mastered:
            mastery_sessions = session.sessions_completed - trick.base_sessions_needed
            if mastery_sessions >= trick.mastery_sessions:
                session.is_mastered = True
                stats.tricks_mastered.append(trick_key)
                if trick_key not in stats.tricks_learned:
                    stats.tricks_learned.append(trick_key)
                stats.update_training_level()
                messages.append(f"|y{pet.key} has mastered {trick.name}!|n")
        
        # Training affects stats
        if success:
            stats.modify_stat("obedience", 1)
            stats.modify_stat("bond_strength", 1)
        
        # Energy cost
        stats.modify_stat("energy", -5)
        
        # Save everything
        TrainingSystem.save_session(pet, session)
        pet.save_pet_stats()
        
        # Build result message
        if success:
            result = trick.success_msg.format(pet=pet.key, target="target")
            messages.insert(0, f"|gSuccess!|n {result}")
        else:
            result = trick.failure_msg.format(pet=pet.key, target="target")
            messages.insert(0, f"|rFailed.|n {result}")
        
        progress = session.get_progress_percentage()
        messages.append(f"Progress: {progress:.0f}%")
        
        return success, "\n".join(messages)
    
    @staticmethod
    def command_trick(pet, trick_key: str, target=None) -> Tuple[bool, str]:
        """
        Command a pet to perform a learned trick.
        
        Returns:
            (success: bool, message: str)
        """
        trick = TRICKS.get(trick_key)
        if not trick:
            return False, f"Unknown trick: {trick_key}"
        
        stats = pet.pet_stats
        
        # Must have learned it
        if trick_key not in stats.tricks_learned:
            return False, f"{pet.key} doesn't know {trick.name}."
        
        # Check target requirement
        if trick.requires_target and not target:
            return False, f"{trick.name} requires a target."
        
        # Check obedience
        success = stats.check_obedience(
            difficulty=trick.difficulty * 10,
            trick_name=trick_key
        )
        
        if success:
            # Format message
            msg = trick.success_msg.format(
                pet=pet.key,
                target=target.key if target else "target",
                object="object"
            )
            
            # Energy cost
            stats.modify_stat("energy", -trick.difficulty)
            pet.save_pet_stats()
            
            return True, msg
        else:
            msg = trick.failure_msg.format(
                pet=pet.key,
                target=target.key if target else "target"
            )
            pet.save_pet_stats()
            return False, msg
    
    @staticmethod
    def get_trick_list(category: Optional[TrickCategory] = None) -> List[Trick]:
        """Get list of all tricks, optionally filtered by category."""
        if category:
            return [t for t in TRICKS.values() if t.category == category]
        return list(TRICKS.values())


# =============================================================================
# HELPER FUNCTIONS
# =============================================================================

def get_trick(trick_key: str) -> Optional[Trick]:
    """Get a trick by key."""
    return TRICKS.get(trick_key)


def list_tricks_by_category() -> Dict[TrickCategory, List[Trick]]:
    """Get all tricks organized by category."""
    result = {cat: [] for cat in TrickCategory}
    for trick in TRICKS.values():
        result[trick.category].append(trick)
    return result


def get_trick_by_command(command: str) -> Optional[Trick]:
    """Find a trick by its command phrase or aliases."""
    command_lower = command.lower().strip()
    
    for trick in TRICKS.values():
        if trick.command_phrase.lower().rstrip('!') == command_lower:
            return trick
        if command_lower in [a.lower() for a in trick.aliases]:
            return trick
    
    return None


__all__ = [
    "TrickCategory",
    "Trick",
    "TRICKS",
    "TrainingSession",
    "TrainingSystem",
    "get_trick",
    "list_tricks_by_category",
    "get_trick_by_command",
]
