"""
Scene Generation System
=======================

Dynamic scene and event text generation including:
- Breeding scenes
- Milking scenes
- Training scenes
- Punishment scenes
- Public use scenes
"""

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any, Tuple
from enum import Enum
import random


# =============================================================================
# ENUMS
# =============================================================================

class SceneType(Enum):
    """Types of scenes."""
    BREEDING = "breeding"
    MILKING = "milking"
    TRAINING = "training"
    PUNISHMENT = "punishment"
    PUBLIC_USE = "public_use"
    BREAKING = "breaking"
    AUCTION = "auction"
    INSPECTION = "inspection"


class SceneIntensity(Enum):
    """Intensity levels."""
    GENTLE = "gentle"
    MODERATE = "moderate"
    INTENSE = "intense"
    ROUGH = "rough"
    BRUTAL = "brutal"


class EmotionalTone(Enum):
    """Emotional tone of scene."""
    TENDER = "tender"
    NEUTRAL = "neutral"
    HUMILIATING = "humiliating"
    DEGRADING = "degrading"
    FEARFUL = "fearful"
    BLISSFUL = "blissful"


# =============================================================================
# TEXT POOLS
# =============================================================================

class BreedingTexts:
    """Text fragments for breeding scenes."""
    
    INTRO_HEAT = [
        "{subject}'s heat-scent fills the air, thick and impossible to ignore.",
        "The pheromones rolling off {subject} drive the bull wild with need.",
        "{subject} trembles, body aching with the desperate need to be bred.",
        "Heat radiates from {subject}'s flushed skin, pussy dripping with need.",
        "{subject}'s heat has reached its peak - body screaming to be filled.",
    ]
    
    INTRO_NORMAL = [
        "{subject} is presented for breeding.",
        "{subject} waits nervously for the breeding to begin.",
        "The breeding session begins as {subject} is positioned.",
        "{subject} is secured in the breeding frame.",
    ]
    
    MOUNTING = [
        "{bull} mounts {subject}, thick cock finding its mark.",
        "With a powerful thrust, {bull} hilts inside {subject}.",
        "{bull} drives forward, spreading {subject} wide around the invading shaft.",
        "{subject} gasps as {bull} pushes deep, filling every inch.",
        "{bull} claims {subject}, sinking balls-deep in one stroke.",
    ]
    
    MOUNTING_FUTANARI = [
        "{bull}'s heavy breasts press against {subject}'s back as she mounts.",
        "Despite her feminine curves, {bull}'s cock is all dominance as she takes {subject}.",
        "{bull}'s breasts sway as she thrusts, her thick futa cock claiming {subject}.",
    ]
    
    THRUSTING_GENTLE = [
        "{bull} sets a slow, steady rhythm.",
        "Each thrust is measured, almost tender.",
        "{bull} takes {subject} with surprising gentleness.",
    ]
    
    THRUSTING_MODERATE = [
        "{bull} establishes a firm, rhythmic pace.",
        "The breeding continues with steady, purposeful strokes.",
        "{subject} rocks with each thrust as {bull} works.",
    ]
    
    THRUSTING_ROUGH = [
        "{bull} pounds into {subject} without mercy.",
        "The sound of flesh slapping flesh fills the barn.",
        "{subject} is rocked by the brutal pace {bull} sets.",
        "Each thrust drives the air from {subject}'s lungs.",
    ]
    
    THRUSTING_BRUTAL = [
        "{bull} ruts with savage intensity, treating {subject} as nothing but a breeding hole.",
        "{subject} is used with animal ferocity, body bouncing limply.",
        "The breeding is merciless, {bull} taking pleasure without concern for {subject}.",
    ]
    
    KNOTTING = [
        "{bull}'s knot swells, locking them together.",
        "The knot catches, tying {subject} to {bull}.",
        "{subject} whimpers as the knot stretches her entrance, sealing them.",
        "Locked together by {bull}'s swollen knot, {subject} can only take it.",
    ]
    
    CLIMAX = [
        "{bull} groans as thick ropes of cum flood {subject}'s womb.",
        "With a final thrust, {bull} empties into {subject}.",
        "{subject} feels the hot rush of seed filling her depths.",
        "{bull}'s balls pulse, pumping load after load into {subject}.",
        "Cum floods {subject}'s pussy, overflowing around {bull}'s shaft.",
    ]
    
    CLIMAX_HEAVY = [
        "{bull} unloads a massive amount, belly visibly swelling.",
        "So much cum pumps into {subject} that it leaks out around {bull}'s cock.",
        "{subject}'s womb is absolutely flooded with potent seed.",
    ]
    
    AFTERMATH_CONCEPTION = [
        "Deep inside, seed meets egg. Life begins.",
        "{subject}'s fate is sealed - another belly to be filled.",
        "The breeding takes. {subject} will bear {bull}'s offspring.",
    ]
    
    AFTERMATH_NO_CONCEPTION = [
        "Perhaps next time the breeding will take.",
        "{subject} will need another session.",
        "The seed doesn't take root... yet.",
    ]


class MilkingTexts:
    """Text fragments for milking scenes."""
    
    ATTACHMENT = [
        "The suction cups are attached to {subject}'s swollen nipples.",
        "{subject}'s heavy breasts are positioned in the milking frame.",
        "Cool metal cups seal around {subject}'s engorged teats.",
        "The milking apparatus is secured to {subject}'s aching udders.",
    ]
    
    SUCTION_START = [
        "The machine hums to life, suction beginning its rhythmic pull.",
        "Vacuum pressure engages, tugging at {subject}'s nipples.",
        "The pumping begins, drawing milk from {subject}'s full breasts.",
    ]
    
    MILK_FLOW = [
        "Creamy milk streams into the collection tubes.",
        "{subject}'s milk flows steadily, white and rich.",
        "The containers fill with {subject}'s warm, fresh milk.",
        "Milk sprays from {subject}'s nipples with each pulse of suction.",
    ]
    
    HEAVY_FLOW = [
        "Milk gushes from {subject}, barely containable.",
        "The machine struggles to keep up with {subject}'s abundant production.",
        "Rivers of milk pour from {subject}'s overproductive udders.",
    ]
    
    SENSATION_PLEASANT = [
        "{subject} sighs as the pressure in her breasts eases.",
        "Relief washes over {subject} as the engorgement subsides.",
        "The rhythmic suction is almost soothing.",
    ]
    
    SENSATION_AROUSING = [
        "{subject} squirms as pleasure builds from the stimulation.",
        "The suction sends waves of arousal through {subject}.",
        "{subject} moans as the milking becomes increasingly pleasurable.",
        "Each pull of the machine sends sparks of pleasure to {subject}'s core.",
    ]
    
    SENSATION_PAINFUL = [
        "{subject} winces at the aggressive suction.",
        "The milking is harsh, extracting every drop without mercy.",
        "{subject}'s sore nipples ache under the relentless machine.",
    ]
    
    COMPLETION = [
        "The machine slows as {subject}'s breasts empty.",
        "{subject}'s udders are thoroughly drained.",
        "The milking concludes, {subject}'s breasts now soft and depleted.",
        "{amount}ml extracted. A good yield.",
    ]


class PunishmentTexts:
    """Text fragments for punishment scenes."""
    
    INTRO = [
        "{subject} is brought before {punisher} for punishment.",
        "It's time for {subject} to face consequences.",
        "{subject} trembles, knowing what's coming.",
    ]
    
    SPANKING = [
        "{punisher}'s hand cracks against {subject}'s exposed rear.",
        "The sound of palm meeting flesh echoes.",
        "{subject} yelps as another blow lands.",
        "Red handprints bloom across {subject}'s cheeks.",
    ]
    
    CANING = [
        "The cane whistles through the air before striking.",
        "{subject} screams as the cane leaves a welt.",
        "Parallel lines rise on {subject}'s punished flesh.",
    ]
    
    WHIPPING = [
        "The whip cracks against {subject}'s back.",
        "{subject}'s body jerks with each lash.",
        "The leather bites into {subject}'s skin.",
    ]
    
    COUNTING = [
        '"{count}..." {subject} gasps out.',
        '"Th-thank you... {count}..." {subject} manages.',
        "{subject} counts through tears: '{count}...'",
    ]
    
    CRYING = [
        "Tears stream down {subject}'s face.",
        "{subject} sobs, body shaking.",
        "The crying only encourages {punisher}.",
    ]
    
    BEGGING = [
        '"Please... no more..." {subject} begs.',
        '{subject} whimpers, "I\'ll be good..."',
        '"I\'m sorry! Please!" {subject} cries.',
    ]
    
    COMPLETION = [
        "The punishment concludes, lesson delivered.",
        "{subject} is left marked and chastened.",
        "{subject} won't forget this lesson soon.",
    ]


class PublicUseTexts:
    """Text fragments for public use scenes."""
    
    DISPLAY = [
        "{subject} is displayed for public use.",
        "Anyone may use {subject} - all holes available.",
        "{subject} waits, exposed and available.",
    ]
    
    APPROACH = [
        "{user} approaches {subject}.",
        "Another user steps up to {subject}.",
        "{user} decides to take a turn with {subject}.",
    ]
    
    ORAL = [
        "{user}'s cock pushes past {subject}'s lips.",
        "{subject}'s mouth is filled.",
        "{subject} services {user} with practiced skill.",
        "{user} uses {subject}'s throat.",
    ]
    
    VAGINAL = [
        "{user} takes {subject}'s pussy.",
        "{subject} is filled from behind.",
        "{user} helps themselves to {subject}.",
    ]
    
    ANAL = [
        "{user} claims {subject}'s ass.",
        "{subject}'s tight rear is taken.",
        "{user} pushes into {subject}'s back entrance.",
    ]
    
    CUM_INSIDE = [
        "{user} finishes inside {subject}.",
        "Another load joins the cum already inside {subject}.",
        "{subject} takes {user}'s seed.",
    ]
    
    CUM_ON = [
        "{user} pulls out to finish on {subject}.",
        "Cum splatters across {subject}'s {location}.",
        "{subject} is marked with another load.",
    ]
    
    STATE_DESCRIPTIONS = [
        "{subject} drips with the cum of multiple users.",
        "{subject} has lost count of how many have used them.",
        "{subject}'s holes are stretched and leaking.",
        "Cum coats {subject}'s face, hair, and body.",
    ]


class BreakingTexts:
    """Text fragments for breaking scenes."""
    
    RESISTANCE = [
        "{subject} still fights, but the resistance is fading.",
        "Defiance flickers in {subject}'s eyes, dimming.",
        "Each session chips away at {subject}'s will.",
    ]
    
    ISOLATION = [
        "Alone in the darkness, {subject}'s mind begins to crack.",
        "The silence presses in, eroding sanity.",
        "With nothing but their thoughts, {subject} starts to break.",
    ]
    
    PLEASURE = [
        "Pleasure is rewired into obedience.",
        "{subject}'s body betrays them, responding to conditioning.",
        "Orgasm after forced orgasm reprograms {subject}'s mind.",
    ]
    
    EDGING = [
        "{subject} is kept on the edge, desperate for release.",
        "Hours of denial leave {subject} willing to do anything.",
        "The need becomes unbearable.",
    ]
    
    HUMILIATION = [
        "Shame and degradation erode {subject}'s sense of self.",
        "Public humiliation breaks down pride.",
        "{subject} is reduced, stripped of dignity.",
    ]
    
    BREAKING_MOMENT = [
        "Something fundamental shatters.",
        "{subject}'s eyes go vacant, resistance gone.",
        "The breaking is complete. What remains is obedient.",
        "{subject} finally breaks, submitting completely.",
    ]
    
    POST_BREAK = [
        "{subject} is now compliant, eager to please.",
        "The fight is gone from {subject}'s eyes.",
        "Conditioning has replaced free will.",
    ]


# =============================================================================
# SCENE GENERATOR
# =============================================================================

@dataclass
class SceneContext:
    """Context for scene generation."""
    
    # Participants
    subject_name: str = ""
    actor_name: str = ""          # Bull, punisher, user, etc.
    
    # Scene type
    scene_type: SceneType = SceneType.BREEDING
    intensity: SceneIntensity = SceneIntensity.MODERATE
    tone: EmotionalTone = EmotionalTone.NEUTRAL
    
    # Flags
    subject_in_heat: bool = False
    actor_is_futanari: bool = False
    actor_has_knot: bool = False
    
    # For breeding
    conception: bool = False
    cum_volume: int = 20
    
    # For milking
    milk_amount: int = 500
    
    # For punishment
    strike_count: int = 10
    
    # For public use
    cum_location: str = "inside"
    use_type: str = "full"


class SceneGenerator:
    """Generates dynamic scene text."""
    
    def generate_breeding_scene(self, ctx: SceneContext) -> str:
        """Generate a breeding scene."""
        parts = []
        
        # Intro
        if ctx.subject_in_heat:
            parts.append(random.choice(BreedingTexts.INTRO_HEAT).format(
                subject=ctx.subject_name, bull=ctx.actor_name
            ))
        else:
            parts.append(random.choice(BreedingTexts.INTRO_NORMAL).format(
                subject=ctx.subject_name, bull=ctx.actor_name
            ))
        
        # Mounting
        if ctx.actor_is_futanari:
            parts.append(random.choice(BreedingTexts.MOUNTING_FUTANARI).format(
                subject=ctx.subject_name, bull=ctx.actor_name
            ))
        else:
            parts.append(random.choice(BreedingTexts.MOUNTING).format(
                subject=ctx.subject_name, bull=ctx.actor_name
            ))
        
        # Thrusting based on intensity
        if ctx.intensity == SceneIntensity.GENTLE:
            parts.append(random.choice(BreedingTexts.THRUSTING_GENTLE).format(
                subject=ctx.subject_name, bull=ctx.actor_name
            ))
        elif ctx.intensity == SceneIntensity.MODERATE:
            parts.append(random.choice(BreedingTexts.THRUSTING_MODERATE).format(
                subject=ctx.subject_name, bull=ctx.actor_name
            ))
        elif ctx.intensity in [SceneIntensity.ROUGH, SceneIntensity.INTENSE]:
            parts.append(random.choice(BreedingTexts.THRUSTING_ROUGH).format(
                subject=ctx.subject_name, bull=ctx.actor_name
            ))
        else:
            parts.append(random.choice(BreedingTexts.THRUSTING_BRUTAL).format(
                subject=ctx.subject_name, bull=ctx.actor_name
            ))
        
        # Knotting if applicable
        if ctx.actor_has_knot:
            parts.append(random.choice(BreedingTexts.KNOTTING).format(
                subject=ctx.subject_name, bull=ctx.actor_name
            ))
        
        # Climax
        parts.append(random.choice(BreedingTexts.CLIMAX).format(
            subject=ctx.subject_name, bull=ctx.actor_name
        ))
        
        if ctx.cum_volume > 40:
            parts.append(random.choice(BreedingTexts.CLIMAX_HEAVY).format(
                subject=ctx.subject_name, bull=ctx.actor_name
            ))
        
        # Aftermath
        if ctx.conception:
            parts.append(random.choice(BreedingTexts.AFTERMATH_CONCEPTION).format(
                subject=ctx.subject_name, bull=ctx.actor_name
            ))
        else:
            parts.append(random.choice(BreedingTexts.AFTERMATH_NO_CONCEPTION).format(
                subject=ctx.subject_name, bull=ctx.actor_name
            ))
        
        return "\n\n".join(parts)
    
    def generate_milking_scene(self, ctx: SceneContext) -> str:
        """Generate a milking scene."""
        parts = []
        
        # Attachment
        parts.append(random.choice(MilkingTexts.ATTACHMENT).format(
            subject=ctx.subject_name
        ))
        
        # Start
        parts.append(random.choice(MilkingTexts.SUCTION_START).format(
            subject=ctx.subject_name
        ))
        
        # Flow
        if ctx.milk_amount > 1000:
            parts.append(random.choice(MilkingTexts.HEAVY_FLOW).format(
                subject=ctx.subject_name
            ))
        else:
            parts.append(random.choice(MilkingTexts.MILK_FLOW).format(
                subject=ctx.subject_name
            ))
        
        # Sensation based on tone
        if ctx.tone == EmotionalTone.TENDER:
            parts.append(random.choice(MilkingTexts.SENSATION_PLEASANT).format(
                subject=ctx.subject_name
            ))
        elif ctx.tone == EmotionalTone.BLISSFUL:
            parts.append(random.choice(MilkingTexts.SENSATION_AROUSING).format(
                subject=ctx.subject_name
            ))
        elif ctx.tone in [EmotionalTone.DEGRADING, EmotionalTone.FEARFUL]:
            parts.append(random.choice(MilkingTexts.SENSATION_PAINFUL).format(
                subject=ctx.subject_name
            ))
        
        # Completion
        parts.append(random.choice(MilkingTexts.COMPLETION).format(
            subject=ctx.subject_name, amount=ctx.milk_amount
        ))
        
        return "\n\n".join(parts)
    
    def generate_punishment_scene(self, ctx: SceneContext) -> str:
        """Generate a punishment scene."""
        parts = []
        
        # Intro
        parts.append(random.choice(PunishmentTexts.INTRO).format(
            subject=ctx.subject_name, punisher=ctx.actor_name
        ))
        
        # Select punishment type based on intensity
        if ctx.intensity == SceneIntensity.GENTLE:
            strike_text = PunishmentTexts.SPANKING
        elif ctx.intensity in [SceneIntensity.MODERATE, SceneIntensity.INTENSE]:
            strike_text = PunishmentTexts.SPANKING
        elif ctx.intensity == SceneIntensity.ROUGH:
            strike_text = PunishmentTexts.CANING
        else:
            strike_text = PunishmentTexts.WHIPPING
        
        # Punishment sequence
        for i in range(min(ctx.strike_count, 5)):
            parts.append(random.choice(strike_text).format(
                subject=ctx.subject_name, punisher=ctx.actor_name
            ))
            
            if i > 2:
                parts.append(random.choice(PunishmentTexts.COUNTING).format(
                    subject=ctx.subject_name, count=i+1
                ))
        
        # Reactions
        if ctx.strike_count > 5:
            parts.append(random.choice(PunishmentTexts.CRYING).format(
                subject=ctx.subject_name
            ))
        
        if ctx.intensity in [SceneIntensity.ROUGH, SceneIntensity.BRUTAL]:
            parts.append(random.choice(PunishmentTexts.BEGGING).format(
                subject=ctx.subject_name
            ))
        
        # Completion
        parts.append(random.choice(PunishmentTexts.COMPLETION).format(
            subject=ctx.subject_name, punisher=ctx.actor_name
        ))
        
        return "\n\n".join(parts)
    
    def generate_public_use_scene(self, ctx: SceneContext) -> str:
        """Generate a public use scene."""
        parts = []
        
        # Display
        parts.append(random.choice(PublicUseTexts.DISPLAY).format(
            subject=ctx.subject_name
        ))
        
        # Approach
        parts.append(random.choice(PublicUseTexts.APPROACH).format(
            subject=ctx.subject_name, user=ctx.actor_name
        ))
        
        # Use type
        if ctx.use_type == "oral":
            parts.append(random.choice(PublicUseTexts.ORAL).format(
                subject=ctx.subject_name, user=ctx.actor_name
            ))
        elif ctx.use_type == "anal":
            parts.append(random.choice(PublicUseTexts.ANAL).format(
                subject=ctx.subject_name, user=ctx.actor_name
            ))
        else:
            parts.append(random.choice(PublicUseTexts.VAGINAL).format(
                subject=ctx.subject_name, user=ctx.actor_name
            ))
        
        # Finish
        if ctx.cum_location == "inside":
            parts.append(random.choice(PublicUseTexts.CUM_INSIDE).format(
                subject=ctx.subject_name, user=ctx.actor_name
            ))
        else:
            parts.append(random.choice(PublicUseTexts.CUM_ON).format(
                subject=ctx.subject_name, user=ctx.actor_name, location=ctx.cum_location
            ))
        
        return "\n\n".join(parts)
    
    def generate_breaking_scene(self, ctx: SceneContext) -> str:
        """Generate a breaking scene."""
        parts = []
        
        # Current state
        parts.append(random.choice(BreakingTexts.RESISTANCE).format(
            subject=ctx.subject_name
        ))
        
        # Method based on intensity
        if ctx.intensity == SceneIntensity.GENTLE:
            parts.append(random.choice(BreakingTexts.ISOLATION).format(
                subject=ctx.subject_name
            ))
        elif ctx.intensity == SceneIntensity.MODERATE:
            parts.append(random.choice(BreakingTexts.PLEASURE).format(
                subject=ctx.subject_name
            ))
        elif ctx.intensity == SceneIntensity.INTENSE:
            parts.append(random.choice(BreakingTexts.EDGING).format(
                subject=ctx.subject_name
            ))
        else:
            parts.append(random.choice(BreakingTexts.HUMILIATION).format(
                subject=ctx.subject_name
            ))
        
        # Breaking point (if applicable based on context)
        if ctx.tone == EmotionalTone.DEGRADING:
            parts.append(random.choice(BreakingTexts.BREAKING_MOMENT).format(
                subject=ctx.subject_name
            ))
            parts.append(random.choice(BreakingTexts.POST_BREAK).format(
                subject=ctx.subject_name
            ))
        
        return "\n\n".join(parts)
    
    def generate(self, ctx: SceneContext) -> str:
        """Generate scene based on type."""
        generators = {
            SceneType.BREEDING: self.generate_breeding_scene,
            SceneType.MILKING: self.generate_milking_scene,
            SceneType.PUNISHMENT: self.generate_punishment_scene,
            SceneType.PUBLIC_USE: self.generate_public_use_scene,
            SceneType.BREAKING: self.generate_breaking_scene,
        }
        
        generator = generators.get(ctx.scene_type)
        if generator:
            return generator(ctx)
        
        return f"Scene type {ctx.scene_type.value} not implemented."


# Singleton generator instance
scene_generator = SceneGenerator()


__all__ = [
    "SceneType",
    "SceneIntensity",
    "EmotionalTone",
    "SceneContext",
    "SceneGenerator",
    "scene_generator",
    "BreedingTexts",
    "MilkingTexts",
    "PunishmentTexts",
    "PublicUseTexts",
    "BreakingTexts",
]
