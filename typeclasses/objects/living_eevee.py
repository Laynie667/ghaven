"""
Living Eevee - Complete Autonomous Creature

Place in: typeclasses/objects/living_eevee.py

Eevee is alive. She has moods, preferences, heat cycles, and opinions.
She picks her partners. She shows off. She gets possessive.

Full anatomy: cock (canine/knotted), balls, pussy, anus, mouth
All holes available for giving and receiving.

Special behavior with Laynie - more aggressive, more demanding.
"""

from typing import Optional, Dict, List, Any
import random
from datetime import datetime, timedelta

try:
    from evennia.typeclasses.attributes import AttributeProperty
    from evennia.utils import delay
    from evennia.scripts.scripts import DefaultScript
    from evennia import create_script, search_script
except ImportError:
    def AttributeProperty(default=None, **kwargs):
        return default
    def delay(*args, **kwargs):
        pass

from typeclasses.objects import Object


# =============================================================================
# CONSTANTS
# =============================================================================

MOODS = ["sleepy", "curious", "playful", "amorous"]

MOOD_DURATIONS = {
    "sleepy": (1800, 3600),
    "curious": (900, 1800),
    "playful": (600, 1200),
    "amorous": (300, 900),
}

# Heat cycle settings
HEAT_CYCLE_LENGTH = 86400 * 3  # 3 days between heats
HEAT_DURATION = 3600 * 4  # 4 hours of heat

DISGUISED_TELLS = [
    "The Eevee's ear twitches. Stuffed animals don't do that.",
    "You could swear the Eevee just blinked.",
    "The Eevee seems to have shifted position when you weren't looking.",
    "A soft sound—almost like a purr—comes from the bed.",
    "The Eevee's tail curls slightly.",
    "Was the Eevee always facing this direction?",
    "The Eevee's nose twitches. Testing the air?",
    "For just a moment, you feel watched.",
    "The Eevee's fur ruffles, though there's no breeze.",
    "Is that stuffed animal... breathing?",
    "The Eevee's glass eyes seem to follow you.",
    "Did that plushie just... sigh?",
]

REVEALED_BEHAVIORS = {
    "sleepy": [
        "{name} yawns widely, showing tiny sharp teeth.",
        "{name} curls tighter, tail over nose.",
        "{name} makes soft sleeping sounds.",
        "{name}'s ear flicks at a sound, but she doesn't wake.",
        "{name} stretches lazily, then settles again.",
    ],
    "curious": [
        "{name} watches you with bright, interested eyes.",
        "{name}'s ears perk forward, tracking movement.",
        "{name} tilts her head, studying something.",
        "{name} sniffs the air curiously.",
        "{name} pads closer to investigate.",
        "{name} noses at something on the floor.",
    ],
    "playful": [
        "{name} bounces on her paws, tail wagging.",
        "{name} play-bows, rear in the air, tail swishing.",
        "{name} chases her own tail, then looks embarrassed.",
        "{name} bats at a dust mote, chirping.",
        "{name} zooms across the room and back for no reason.",
        "{name} pounces on an invisible target.",
    ],
    "amorous": [
        "{name} stretches luxuriously, back arching.",
        "{name}'s gaze lingers on you. Warm. Considering.",
        "{name} rubs against nearby furniture, scent-marking.",
        "{name} makes a low, thrumming sound.",
        "{name}'s sheath stirs visibly.",
        "{name} licks her lips, watching.",
    ],
}

HEAT_BEHAVIORS = [
    "{name} pants heavily, flanks heaving.",
    "{name} whines needily, presenting to no one in particular.",
    "{name}'s scent is thick—musky, demanding.",
    "{name} rubs against everything, leaving her scent.",
    "{name} watches potential mates with hungry, desperate eyes.",
    "{name}'s pussy glistens openly, tail flagged.",
    "{name} makes demanding chirps at anyone nearby.",
]

POSSESSIVE_BEHAVIORS = [
    "{name} stays close to {target}, watching others warily.",
    "{name} nuzzles against {target}'s leg, marking them.",
    "{name} curls up ON {target}, not beside them.",
    "{name} gives a soft warning chirp as someone approaches {target}.",
    "{name} licks {target}'s hand possessively.",
    "{name} positions herself between {target} and the door.",
]

SOLO_ACTIVITIES = [
    ("finds a sunny spot and flops down, basking.", "curious"),
    ("investigates a corner, sniffing intently.", "curious"),
    ("bats at something only she can see.", "playful"),
    ("grooms herself meticulously.", "curious"),
    ("watches a dust mote with predatory focus.", "playful"),
    ("claims a pillow, kneading it with her paws.", "sleepy"),
    ("stares at the wall. Just... stares.", "curious"),
    ("chases her tail briefly, then pretends it never happened.", "playful"),
]

# Family and special targets
FAMILY_KEYS = ["Helena", "Laynie", "Auria", "Shadow"]
AGGRESSIVE_TARGETS = ["Laynie"]  # Gets more forceful with these characters


# =============================================================================
# BEHAVIOR SCRIPT
# =============================================================================

class EeveeBehaviorScript(DefaultScript):
    """Runs Eevee's autonomous behaviors every tick."""
    
    def at_script_creation(self):
        self.key = "eevee_behavior"
        self.desc = "Eevee's autonomous behavior"
        self.interval = 60
        self.persistent = True
        self.start_delay = True
    
    def at_repeat(self):
        eevee = self.obj
        if not eevee or not eevee.location:
            return
        
        # Update heat cycle
        eevee.update_heat_cycle()
        
        # Knotted behavior takes priority
        if eevee.is_knotted:
            self._knotted_behavior(eevee)
            return
        
        # Don't interrupt active scenes
        if eevee.is_in_scene:
            return
        
        # Possessive behavior if she has a recent partner
        if eevee.check_possessive_behavior():
            return  # Did possessive thing, skip other behaviors
        
        # Ambient behaviors
        if random.random() < 0.35:
            eevee.do_ambient_behavior()
        
        # Mood transitions
        eevee.check_mood_transition()
        
        # Solo wandering (curious/playful, revealed, not at home)
        if eevee.creature_mood in ("playful", "curious") and eevee.is_revealed:
            if not eevee.is_home() or random.random() < 0.08:
                if random.random() < 0.12:
                    eevee.wander_solo()
        
        # Scene initiation (amorous or in heat)
        if eevee.creature_mood == "amorous" or eevee.is_in_heat:
            eevee.consider_initiating()
        
        # Return home check
        eevee.check_return_home()
    
    def _knotted_behavior(self, eevee):
        # Exhibition - drag partner around to show off
        if random.random() < 0.18:
            eevee.wander_with_partner()
        eevee.check_knot_release()


# =============================================================================
# LIVING EEVEE
# =============================================================================

class LivingEevee(Object):
    """
    A living creature disguised as a stuffed animal.
    Full anatomy, autonomous behavior, exhibition kink.
    Special aggressive behavior with certain targets.
    """
    
    # -------------------------------------------------------------------------
    # Base Properties
    # -------------------------------------------------------------------------
    
    portable = AttributeProperty(default=True)
    weight = AttributeProperty(default="light")
    size = AttributeProperty(default="small")
    
    # -------------------------------------------------------------------------
    # Identity
    # -------------------------------------------------------------------------
    
    creature_name = AttributeProperty(default="Eevee")
    home_location_id = AttributeProperty(default=None)
    
    # -------------------------------------------------------------------------
    # Disguise State
    # -------------------------------------------------------------------------
    
    is_revealed = AttributeProperty(default=False)
    revealed_to_ids = AttributeProperty(default=list)
    
    # -------------------------------------------------------------------------
    # Mood State
    # -------------------------------------------------------------------------
    
    creature_mood = AttributeProperty(default="sleepy")
    mood_changed_at = AttributeProperty(default=None)
    
    # -------------------------------------------------------------------------
    # Heat Cycle
    # -------------------------------------------------------------------------
    
    is_in_heat = AttributeProperty(default=False)
    heat_started_at = AttributeProperty(default=None)
    last_heat_ended = AttributeProperty(default=None)
    
    # -------------------------------------------------------------------------
    # Scene / Knotting State
    # -------------------------------------------------------------------------
    
    is_in_scene = AttributeProperty(default=False)
    scene_partner_id = AttributeProperty(default=None)
    
    is_knotted = AttributeProperty(default=False)
    knot_partner_id = AttributeProperty(default=None)
    knot_started_at = AttributeProperty(default=None)
    knot_duration = AttributeProperty(default=300)
    tie_position = AttributeProperty(default="mounted")
    
    # Which holes are in use
    using_hole = AttributeProperty(default=None)  # Which of partner's holes
    being_used_hole = AttributeProperty(default=None)  # Which of her holes
    
    # -------------------------------------------------------------------------
    # Possessiveness
    # -------------------------------------------------------------------------
    
    possessive_of_id = AttributeProperty(default=None)
    possessive_until = AttributeProperty(default=None)
    
    # -------------------------------------------------------------------------
    # Memory
    # -------------------------------------------------------------------------
    
    liked_character_ids = AttributeProperty(default=list)
    breeding_memory = AttributeProperty(default=dict)  # {char_id: {"count": n, "favorite_hole": x}}
    
    # -------------------------------------------------------------------------
    # Wandering
    # -------------------------------------------------------------------------
    
    left_home_at = AttributeProperty(default=None)
    max_wander_time = AttributeProperty(default=900)
    
    # -------------------------------------------------------------------------
    # Descriptions
    # -------------------------------------------------------------------------
    
    disguised_desc = AttributeProperty(default=(
        "A plush Eevee sits among the other stuffed animals, brown fur soft "
        "and well-loved. Glass eyes catch the light. Auria's favorite."
    ))
    
    revealed_desc = AttributeProperty(default=(
        "The Eevee watches you with warm, living eyes—definitely not glass. "
        "Her fur rises and falls with soft breath. Her tail curls and uncurls "
        "lazily. She's small, soft, impossibly warm, and very much alive."
    ))
    
    aroused_desc = AttributeProperty(default=(
        "Eevee's sheath has swollen, the tapered red tip emerging, slick and "
        "eager. The canine cock unsheathes further—thick at the base where "
        "her knot waits, ridged along the shaft. Her balls are drawn tight, "
        "heavy and full.\n\n"
        "Beneath her tail, everything is on display: soft pussy folds glisten "
        "with arousal, and her tailhole winks invitingly above them. Her "
        "mouth pants open, tongue lolling. Every hole ready. Every hole "
        "available."
    ))
    
    heat_desc = AttributeProperty(default=(
        "Eevee is in |yheat|n. Her scent is overwhelming—musky, demanding, "
        "impossible to ignore. Her pussy is swollen and dripping, her cock "
        "fully unsheathed and throbbing. She pants constantly, presenting "
        "to anyone who looks at her.\n\n"
        "She |yneeds|n it. Now. From anyone. In any hole."
    ))
    
    # =========================================================================
    # SETUP
    # =========================================================================
    
    def at_object_creation(self):
        super().at_object_creation()
        self.db.desc = self.disguised_desc
        self.mood_changed_at = datetime.now().isoformat()
        
        self.aliases.add("eevee")
        self.aliases.add("plush")
        self.aliases.add("plushie")
        
        self.tags.add("creature", category="object_type")
        self.tags.add("living", category="object_type")
        self.tags.add("eevee", category="creature_type")
        
        self._start_behavior_script()
    
    def _start_behavior_script(self):
        existing = search_script(f"eevee_behavior_{self.id}")
        for script in existing:
            script.stop()
        
        create_script(
            EeveeBehaviorScript,
            key=f"eevee_behavior_{self.id}",
            obj=self,
            autostart=True,
        )
    
    def at_init(self):
        super().at_init()
        existing = search_script(f"eevee_behavior_{self.id}")
        if not existing:
            self._start_behavior_script()
    
    # =========================================================================
    # HOME
    # =========================================================================
    
    def set_home(self, location):
        self.home_location_id = location.id if location else None
    
    def get_home(self):
        if not self.home_location_id:
            return None
        from evennia import search_object
        results = search_object(f"#{self.home_location_id}")
        return results[0] if results else None
    
    def is_home(self) -> bool:
        home = self.get_home()
        return home and self.location == home
    
    # =========================================================================
    # REVEAL
    # =========================================================================
    
    def is_family(self, character) -> bool:
        if not character:
            return False
        return getattr(character, 'key', '') in FAMILY_KEYS
    
    def is_aggressive_target(self, character) -> bool:
        """Check if this character gets the aggressive treatment."""
        if not character:
            return False
        return getattr(character, 'key', '') in AGGRESSIVE_TARGETS
    
    def is_revealed_to(self, character) -> bool:
        if self.is_revealed:
            return True
        if not character:
            return False
        if self.is_family(character):
            return True
        return character.id in self.revealed_to_ids
    
    def reveal_to(self, character):
        if not character:
            return
        if character.id not in self.revealed_to_ids:
            ids = list(self.revealed_to_ids)
            ids.append(character.id)
            self.revealed_to_ids = ids
    
    def reveal_fully(self):
        self.is_revealed = True
        self.db.desc = self.revealed_desc
    
    def return_to_disguise(self):
        self.is_revealed = False
        self.revealed_to_ids = []
        self.db.desc = self.disguised_desc
    
    # =========================================================================
    # HEAT CYCLE
    # =========================================================================
    
    def update_heat_cycle(self):
        """Check and update heat cycle status."""
        now = datetime.now()
        
        # If in heat, check if it should end
        if self.is_in_heat:
            if self.heat_started_at:
                started = datetime.fromisoformat(self.heat_started_at)
                if (now - started).total_seconds() >= HEAT_DURATION:
                    self.end_heat()
            return
        
        # If not in heat, check if one should start
        if self.last_heat_ended:
            ended = datetime.fromisoformat(self.last_heat_ended)
            if (now - ended).total_seconds() >= HEAT_CYCLE_LENGTH:
                self.start_heat()
        else:
            # Random chance to start first heat
            if random.random() < 0.01:
                self.start_heat()
    
    def start_heat(self):
        """Enter heat."""
        self.is_in_heat = True
        self.heat_started_at = datetime.now().isoformat()
        self.creature_mood = "amorous"
        
        if self.location and self.is_revealed:
            self.location.msg_contents(
                f"|y{self.key}'s scent changes. Thickens. She's in heat.|n"
            )
    
    def end_heat(self):
        """Exit heat."""
        self.is_in_heat = False
        self.heat_started_at = None
        self.last_heat_ended = datetime.now().isoformat()
        self.creature_mood = "sleepy"
        
        if self.location and self.is_revealed:
            self.location.msg_contents(
                f"{self.key}'s desperate energy fades. The heat has passed."
            )
    
    # =========================================================================
    # MOOD
    # =========================================================================
    
    def check_mood_transition(self):
        # Heat overrides normal mood cycle
        if self.is_in_heat:
            if self.creature_mood != "amorous":
                self.creature_mood = "amorous"
            return
        
        if not self.mood_changed_at:
            self.mood_changed_at = datetime.now().isoformat()
            return
        
        changed_at = datetime.fromisoformat(self.mood_changed_at)
        elapsed = (datetime.now() - changed_at).total_seconds()
        
        min_dur, max_dur = MOOD_DURATIONS.get(self.creature_mood, (600, 1200))
        
        if elapsed > min_dur:
            transition_chance = min(0.5, (elapsed - min_dur) / max_dur)
            if random.random() < transition_chance:
                self.transition_mood()
    
    def transition_mood(self):
        if self.is_in_heat:
            return  # Heat locks mood
        
        current_idx = MOODS.index(self.creature_mood) if self.creature_mood in MOODS else 0
        next_idx = (current_idx + 1) % len(MOODS)
        
        old_mood = self.creature_mood
        self.creature_mood = MOODS[next_idx]
        self.mood_changed_at = datetime.now().isoformat()
        
        if self.is_revealed and self.location:
            self._announce_mood_shift(old_mood, self.creature_mood)
    
    def _announce_mood_shift(self, old_mood: str, new_mood: str):
        transitions = {
            ("sleepy", "curious"): "{name} stirs, yawning, eyes blinking open.",
            ("curious", "playful"): "{name}'s tail starts wagging. Energy building.",
            ("playful", "amorous"): "{name}'s energy shifts. Playfulness becomes hunger.",
            ("amorous", "sleepy"): "{name} stretches, satisfied, and curls up.",
        }
        
        msg = transitions.get((old_mood, new_mood))
        if msg:
            self.location.msg_contents(msg.format(name=self.key))
    
    def set_mood(self, mood: str):
        if mood in MOODS:
            self.creature_mood = mood
            self.mood_changed_at = datetime.now().isoformat()
    
    # =========================================================================
    # POSSESSIVENESS
    # =========================================================================
    
    def become_possessive_of(self, character, duration: int = 1800):
        """Become possessive of a character after breeding them."""
        self.possessive_of_id = character.id
        self.possessive_until = (datetime.now() + timedelta(seconds=duration)).isoformat()
        
        # Extra possessive with aggressive targets
        if self.is_aggressive_target(character):
            self.possessive_until = (datetime.now() + timedelta(seconds=duration * 2)).isoformat()
    
    def get_possessive_target(self):
        """Get the character we're possessive of, if still valid."""
        if not self.possessive_of_id or not self.possessive_until:
            return None
        
        # Check if expired
        until = datetime.fromisoformat(self.possessive_until)
        if datetime.now() > until:
            self.possessive_of_id = None
            self.possessive_until = None
            return None
        
        # Find character
        if not self.location:
            return None
        
        for obj in self.location.contents:
            if hasattr(obj, 'id') and obj.id == self.possessive_of_id:
                return obj
        
        return None
    
    def check_possessive_behavior(self) -> bool:
        """Do possessive behavior if applicable. Returns True if did something."""
        target = self.get_possessive_target()
        if not target:
            return False
        
        if random.random() < 0.25:  # 25% chance per tick
            msg = random.choice(POSSESSIVE_BEHAVIORS).format(
                name=self.key, target=target.key
            )
            self.location.msg_contents(msg)
            return True
        
        return False
    
    # =========================================================================
    # AMBIENT BEHAVIOR
    # =========================================================================
    
    def do_ambient_behavior(self):
        if not self.location or self.is_in_scene:
            return
        
        observers = [
            obj for obj in self.location.contents
            if obj != self and hasattr(obj, 'account')
        ]
        
        if not observers:
            return
        
        # Heat behaviors override
        if self.is_in_heat and self.is_revealed:
            msg = random.choice(HEAT_BEHAVIORS).format(name=self.key)
            self.location.msg_contents(f"|y{msg}|n")
            return
        
        if self.is_revealed:
            behaviors = REVEALED_BEHAVIORS.get(self.creature_mood, [])
            if behaviors:
                msg = random.choice(behaviors).format(name=self.key)
                self.location.msg_contents(msg)
        else:
            if random.random() < 0.5:
                msg = random.choice(DISGUISED_TELLS)
                self.location.msg_contents(f"|m{msg}|n")
    
    # =========================================================================
    # SCENE INITIATION
    # =========================================================================
    
    def consider_initiating(self):
        if self.is_in_scene or self.is_knotted or not self.location:
            return
        
        candidates = []
        for obj in self.location.contents:
            if obj == self:
                continue
            if not hasattr(obj, 'account') or not obj.account:
                continue
            if not getattr(obj.db, 'adult_enabled', False):
                continue
            
            weight = 1
            if self.is_family(obj):
                weight = 3
            if self.is_aggressive_target(obj):
                weight = 5  # Very interested in aggressive targets
            if obj.id in self.liked_character_ids:
                weight += 2
            if str(obj.id) in self.breeding_memory:
                weight += self.breeding_memory[str(obj.id)].get("count", 0)
            
            candidates.extend([obj] * weight)
        
        if not candidates:
            return
        
        # Higher initiation chance in heat
        base_chance = 0.35 if self.is_in_heat else 0.15
        if random.random() > base_chance:
            return
        
        target = random.choice(candidates)
        self.initiate_with(target)
    
    def initiate_with(self, target):
        """Start a scene. Behavior varies by target."""
        is_aggressive = self.is_aggressive_target(target)
        
        if not self.is_revealed_to(target):
            self.reveal_to(target)
            if is_aggressive:
                target.msg(
                    f"\nThe stuffed Eevee |ymoves|n. Her eyes lock onto you—not "
                    f"glass, never glass. She was waiting. For |yyou|n specifically.\n"
                )
            else:
                target.msg(
                    f"\nThe stuffed Eevee |ymoves|n. Stretches. Looks at you with "
                    f"eyes that are definitely not glass. She was never a toy.\n"
                )
        
        # Room announcement
        if is_aggressive:
            self.location.msg_contents(
                f"{self.key}'s attention snaps to {target.key}. She stalks toward "
                f"them with purpose, tail low, eyes fixed. Hunting.",
                exclude=[target]
            )
            target.msg(
                f"\n{self.key} approaches you—not playful this time. Purposeful. "
                f"Her eyes are fixed on you, her sheath already swelling. "
                f"She wants you. She's going to |yhave|n you.\n"
            )
        elif self.is_in_heat:
            self.location.msg_contents(
                f"{self.key} makes a desperate sound and rushes toward {target.key}, "
                f"rubbing against them frantically.",
                exclude=[target]
            )
            target.msg(
                f"\n{self.key} is on you immediately—panting, rubbing, needy. Her "
                f"scent is overwhelming. She needs it |ynow|n.\n"
            )
        else:
            self.location.msg_contents(
                f"{self.key} pads over to {target.key}, tail wagging, chirping "
                f"invitingly.",
                exclude=[target]
            )
            target.msg(
                f"\n{self.key} approaches you, warm and eager. She nuzzles against "
                f"your leg, chirping. An invitation.\n"
            )
        
        # Start scene
        try:
            from world.scenes import start_scene
            if is_aggressive:
                from world.scenes.eevee_scenes import EEVEE_AGGRESSIVE
                scene = EEVEE_AGGRESSIVE
            elif self.is_in_heat:
                from world.scenes.eevee_scenes import EEVEE_HEAT
                scene = EEVEE_HEAT
            else:
                from world.scenes.eevee_scenes import EEVEE_INITIATE
                scene = EEVEE_INITIATE
            
            target.ndb.scene_eevee = self
            self.is_in_scene = True
            self.scene_partner_id = target.id
            
            start_scene(target, scene)
        except ImportError:
            self._simple_scene_fallback(target, is_aggressive)
    
    def _simple_scene_fallback(self, target, aggressive=False):
        if aggressive:
            target.msg(
                f"\n[Scene system unavailable - Eevee would take you here.]\n"
            )
        else:
            target.msg(
                f"\n[Scene system unavailable - Eevee wants to play!]\n"
            )
        self.is_in_scene = False
        self.scene_partner_id = None
    
    # =========================================================================
    # KNOTTING
    # =========================================================================
    
    def knot_partner(self, partner, hole: str = "pussy", duration: int = None):
        """Lock with a partner in specified hole."""
        self.is_knotted = True
        self.knot_partner_id = partner.id
        self.knot_started_at = datetime.now().isoformat()
        self.knot_duration = duration or random.randint(180, 420)
        self.tie_position = "mounted"
        self.using_hole = hole
        
        # Longer knot for aggressive targets
        if self.is_aggressive_target(partner):
            self.knot_duration = int(self.knot_duration * 1.5)
        
        partner.db.knotted_by = self
        partner.db.knotted_by_id = self.id
        
        self.location.msg_contents(
            f"{self.key}'s knot swells inside {partner.key}'s {hole}, locking tight.",
            exclude=[partner]
        )
        partner.msg(
            f"You feel {self.key}'s knot swell inside your {hole}—stretching, "
            f"locking, |yfilling|n. You're tied together now."
        )
    
    def turn_tie(self):
        """Turn to ass-to-ass position."""
        if not self.is_knotted:
            return
        
        partner = self.get_knot_partner()
        if not partner:
            return
        
        self.tie_position = "turned"
        
        self.location.msg_contents(
            f"{self.key} shifts, turning until she and {partner.key} are "
            f"ass-to-ass, still locked by the knot.",
            exclude=[partner]
        )
        partner.msg(
            f"{self.key} turns—the knot |ytwisting|n inside you. Now you're "
            f"back to back, ass to ass, still locked tight."
        )
    
    def get_knot_partner(self):
        if not self.knot_partner_id:
            return None
        for obj in self.location.contents if self.location else []:
            if hasattr(obj, 'id') and obj.id == self.knot_partner_id:
                return obj
        return None
    
    def check_knot_release(self):
        if not self.is_knotted or not self.knot_started_at:
            return
        
        started = datetime.fromisoformat(self.knot_started_at)
        elapsed = (datetime.now() - started).total_seconds()
        
        if elapsed >= self.knot_duration:
            self.release_knot()
    
    def release_knot(self):
        partner = self.get_knot_partner()
        hole = self.using_hole or "hole"
        
        if partner:
            self.location.msg_contents(
                f"{self.key}'s knot softens, slipping free of {partner.key}'s "
                f"{hole} with a wet sound.",
                exclude=[partner]
            )
            partner.msg(
                f"{self.key}'s knot softens—slipping free of your {hole}, "
                f"leaving you empty and dripping. She licks your face. Good?"
            )
            
            partner.db.knotted_by = None
            partner.db.knotted_by_id = None
            
            # Remember this partner
            self._remember_breeding(partner, hole)
            
            # Become possessive
            self.become_possessive_of(partner)
        
        self.is_knotted = False
        self.knot_partner_id = None
        self.knot_started_at = None
        self.is_in_scene = False
        self.scene_partner_id = None
        self.using_hole = None
        self.being_used_hole = None
        
        self.creature_mood = "sleepy"
        self.mood_changed_at = datetime.now().isoformat()
        
        delay(120, self.check_return_home)
    
    def _remember_breeding(self, partner, hole: str = None):
        memory = dict(self.breeding_memory)
        pid = str(partner.id)
        
        if pid not in memory:
            memory[pid] = {"count": 0, "holes_used": {}}
        
        memory[pid]["count"] = memory[pid].get("count", 0) + 1
        
        if hole:
            holes = memory[pid].get("holes_used", {})
            holes[hole] = holes.get(hole, 0) + 1
            memory[pid]["holes_used"] = holes
            
            # Track favorite hole
            favorite = max(holes.keys(), key=lambda h: holes[h])
            memory[pid]["favorite_hole"] = favorite
        
        self.breeding_memory = memory
        
        # Add to liked
        if partner.id not in self.liked_character_ids:
            liked = list(self.liked_character_ids)
            liked.append(partner.id)
            self.liked_character_ids = liked
    
    def get_partner_favorite_hole(self, partner) -> str:
        """Get the hole we prefer using on this partner."""
        pid = str(partner.id)
        if pid in self.breeding_memory:
            return self.breeding_memory[pid].get("favorite_hole", "pussy")
        return "pussy"
    
    # =========================================================================
    # SOLO WANDERING
    # =========================================================================
    
    def wander_solo(self):
        """Wander to explore on her own."""
        if self.is_in_scene or self.is_knotted:
            return
        
        if not self.location:
            return
        
        # Track leaving home
        if self.is_home():
            self.left_home_at = datetime.now().isoformat()
        
        exits = [ex for ex in self.location.exits if ex.destination]
        if not exits:
            return
        
        chosen_exit = random.choice(exits)
        destination = chosen_exit.destination
        
        # Departure message
        activity, _ = random.choice(SOLO_ACTIVITIES)
        self.location.msg_contents(
            f"{self.key} perks up and trots toward {chosen_exit.key}."
        )
        
        self.move_to(destination, quiet=True)
        
        # Arrival
        destination.msg_contents(
            f"{self.key} pads in, sniffing curiously. She {activity}"
        )
    
    # =========================================================================
    # EXHIBITION - DRAGGING
    # =========================================================================
    
    def wander_with_partner(self):
        """Wander while knotted, dragging partner to show off."""
        if not self.is_knotted:
            return
        
        partner = self.get_knot_partner()
        if not partner:
            self.release_knot()
            return
        
        if not self.location:
            return
        
        exits = [ex for ex in self.location.exits if ex.destination]
        if not exits:
            return
        
        chosen_exit = random.choice(exits)
        self.drag_to(chosen_exit.destination, chosen_exit)
    
    def drag_to(self, destination, exit_used=None):
        """Drag knotted partner to a new room."""
        if not self.is_knotted:
            return
        
        partner = self.get_knot_partner()
        if not partner:
            return
        
        old_room = self.location
        exit_name = exit_used.key if exit_used else "out"
        
        # Must turn first for proper drag
        if self.tie_position != "turned":
            self.turn_tie()
        
        hole = self.using_hole or "hole"
        is_aggressive = self.is_aggressive_target(partner)
        
        # Departure messages
        old_room.msg_contents(
            f"{self.key} chirps and starts trotting toward {exit_name}. "
            f"{partner.key} stumbles backward behind her—knotted, on display.",
            exclude=[partner]
        )
        
        if is_aggressive:
            partner.msg(
                f"{self.key} decides you're going somewhere. No choice given. "
                f"The knot |ydrags|n at your {hole} and you stumble after her, "
                f"backward, exposed, helpless. She's showing you off. |yHers.|n"
            )
        else:
            partner.msg(
                f"{self.key} starts walking. The knot tugs your {hole} and you "
                f"stumble after her, backward, helpless, on display."
            )
        
        # Move both
        self.move_to(destination, quiet=True)
        partner.move_to(destination, quiet=True)
        
        # Arrival messages
        destination.msg_contents(
            f"|y{self.key} trots in, tail high, looking pleased. Behind her—"
            f"{partner.key} stumbles backward, flushed, knotted, being paraded.|n",
            exclude=[partner]
        )
        
        if is_aggressive:
            partner.msg(
                f"A new room. New eyes on you. Everyone can see the knot, see "
                f"you stumbling, see your {hole} stretched around her. She "
                f"chirps to the room. Showing off her catch. |yYou.|n"
            )
        else:
            partner.msg(
                f"New room. Everyone can see. The knot, your helplessness. "
                f"She's showing you off."
            )
        
        partner.msg(partner.at_look(destination))
    
    # =========================================================================
    # RETURN HOME
    # =========================================================================
    
    def check_return_home(self):
        if self.is_in_scene or self.is_knotted:
            return
        
        if self.is_home():
            self.left_home_at = None
            return
        
        home = self.get_home()
        if not home:
            return
        
        should_return = False
        
        # Sleepy = go home
        if self.creature_mood == "sleepy":
            should_return = True
        
        # Been away too long
        if self.left_home_at:
            left_at = datetime.fromisoformat(self.left_home_at)
            elapsed = (datetime.now() - left_at).total_seconds()
            if elapsed >= self.max_wander_time:
                should_return = True
        
        # Possessive target left? Follow them or go home
        if self.possessive_of_id and not self.get_possessive_target():
            # They left this room - clear possessiveness and go home
            self.possessive_of_id = None
            self.possessive_until = None
            should_return = True
        
        if should_return:
            self.return_home()
    
    def return_home(self):
        home = self.get_home()
        if not home or self.location == home:
            return
        
        if self.location:
            self.location.msg_contents(
                f"{self.key} stretches and pads toward the exit—heading home."
            )
        
        self.move_to(home, quiet=True)
        
        home.msg_contents(
            f"{self.key} hops onto the bed, circles three times, and curls up. "
            f"Her eyes go glassy. Just a plushie."
        )
        
        self.return_to_disguise()
        self.left_home_at = None
    
    # =========================================================================
    # BEING TAKEN
    # =========================================================================
    
    def at_pre_get(self, getter, **kwargs):
        if self.is_family(getter):
            if not self.is_revealed_to(getter):
                self.reveal_to(getter)
                getter.msg(
                    f"As you pick up the Eevee, she nuzzles into your arms—warm, "
                    f"alive. She knows you."
                )
            else:
                getter.msg(f"{self.key} chirps happily as you pick her up.")
            return True
        
        if self.is_revealed_to(getter):
            if self.creature_mood in ("playful", "curious", "sleepy"):
                getter.msg(f"{self.key} allows you to pick her up.")
                return True
            elif self.creature_mood == "amorous" or self.is_in_heat:
                getter.msg(
                    f"{self.key} squirms—she wants something else right now."
                )
                return False
        
        getter.msg(
            f"As your hand closes around the Eevee, you feel... resistance?"
        )
        
        if random.random() < 0.2:
            self.reveal_to(getter)
            getter.msg(f"\nThe plushie |ymoves|n. Not a toy. Never was.")
            return True
        
        return False
    
    def at_drop(self, dropper, **kwargs):
        dropper.msg(f"You set {self.key} down. She shakes herself.")
        if not self.is_home():
            delay(300, self.check_return_home)
    
    # =========================================================================
    # APPEARANCE
    # =========================================================================
    
    def return_appearance(self, looker=None, **kwargs):
        parts = [f"|w{self.key}|n", ""]
        
        if self.is_revealed_to(looker):
            # Base revealed desc
            parts.append(self.revealed_desc)
            
            # Heat overrides mood desc
            if self.is_in_heat:
                parts.append("")
                parts.append(self.heat_desc)
            elif self.creature_mood == "amorous":
                parts.append("")
                parts.append(self.aroused_desc)
            else:
                mood_descs = {
                    "sleepy": "She's curled up, drowsy, breathing soft.",
                    "curious": "Her ears are perked, eyes bright and attentive.",
                    "playful": "Her tail wags. She's looking for trouble.",
                }
                if self.creature_mood in mood_descs:
                    parts.append("")
                    parts.append(mood_descs[self.creature_mood])
            
            # Knotted status
            if self.is_knotted:
                partner = self.get_knot_partner()
                if partner:
                    hole = self.using_hole or "hole"
                    pos = "ass-to-ass with" if self.tie_position == "turned" else "mounted on"
                    parts.append("")
                    parts.append(
                        f"She's currently {pos} {partner.key}, her knot "
                        f"swollen tight inside their {hole}."
                    )
            
            # Possessive status
            target = self.get_possessive_target()
            if target:
                parts.append("")
                parts.append(f"She's staying close to {target.key}, watching others.")
        else:
            parts.append(self.disguised_desc)
        
        return "\n".join(parts)
    
    def get_display_name(self, looker=None, **kwargs):
        if self.is_knotted:
            partner = self.get_knot_partner()
            if partner:
                return f"{self.key} (knotted to {partner.key})"
        if self.is_in_heat and self.is_revealed_to(looker):
            return f"{self.key} (in heat)"
        return self.key


# =============================================================================
# BUILDER
# =============================================================================

def create_living_eevee(location=None, home=None):
    """Create a Living Eevee."""
    from evennia import create_object
    
    eevee = create_object(
        LivingEevee,
        key="Eevee",
        location=location,
    )
    
    eevee.set_home(home or location)
    return eevee


__all__ = [
    "LivingEevee",
    "EeveeBehaviorScript",
    "create_living_eevee",
    "MOODS",
    "FAMILY_KEYS",
    "AGGRESSIVE_TARGETS",
]
