"""
Farm NPCs and Events
====================

NPCs for farm operations and breeding event generation.
"""

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any, Tuple
from enum import Enum
from datetime import datetime
import random


# =============================================================================
# ENUMS
# =============================================================================

class FarmhandRole(Enum):
    """Roles for farm NPCs."""
    MILKER = "milker"             # Operates milking equipment
    BREEDER = "breeder"           # Manages breeding sessions
    HANDLER = "handler"           # Moves and manages hucows
    TRAINER = "trainer"           # Trains new hucows
    VETERINARIAN = "veterinarian" # Medical care
    OVERSEER = "overseer"         # Supervises operations
    PUNISHER = "punisher"         # Disciplines problem hucows


class NPCPersonality(Enum):
    """Personality traits affecting behavior."""
    GENTLE = "gentle"
    PROFESSIONAL = "professional"
    ROUGH = "rough"
    SADISTIC = "sadistic"
    CARING = "caring"
    INDIFFERENT = "indifferent"


# =============================================================================
# FARMHAND NPC
# =============================================================================

@dataclass
class FarmhandNPC:
    """NPC worker on the farm."""
    
    npc_id: str = ""
    name: str = ""
    role: FarmhandRole = FarmhandRole.HANDLER
    personality: NPCPersonality = NPCPersonality.PROFESSIONAL
    
    # Stats
    skill_level: int = 50         # 0-100
    efficiency: int = 50          # 0-100
    gentleness: int = 50          # 0-100, affects hucow comfort
    
    # For breeders specifically
    is_futanari: bool = False     # Can personally breed
    cock_size: int = 0            # If applicable
    
    # Records
    hucows_handled: int = 0
    milk_extracted_liters: float = 0.0
    breedings_performed: int = 0
    
    def get_action_message(self, action: str, target_name: str) -> str:
        """Generate flavor text for an action."""
        
        if action == "milk":
            messages = {
                NPCPersonality.GENTLE: [
                    f"{self.name} gently attaches the milking cups to {target_name}'s swollen teats.",
                    f"{self.name} soothingly strokes {target_name}'s flank while the machine drains her.",
                    f"{self.name} murmurs softly to {target_name} as milk flows into the collectors.",
                ],
                NPCPersonality.PROFESSIONAL: [
                    f"{self.name} efficiently attaches {target_name} to the milking station.",
                    f"{self.name} checks the suction levels as {target_name}'s milk flows steadily.",
                    f"{self.name} notes the yield while {target_name} is drained.",
                ],
                NPCPersonality.ROUGH: [
                    f"{self.name} roughly yanks {target_name}'s teats into the milking cups.",
                    f"{self.name} cranks up the suction, making {target_name} gasp.",
                    f"{self.name} slaps {target_name}'s udders to increase flow.",
                ],
                NPCPersonality.SADISTIC: [
                    f"{self.name} smirks as {target_name} squirms under the punishing suction.",
                    f"{self.name} deliberately overfills {target_name}'s cups, enjoying her discomfort.",
                    f"{self.name} pinches {target_name}'s sensitive teats between adjustments.",
                ],
                NPCPersonality.CARING: [
                    f"{self.name} carefully positions {target_name} for maximum comfort.",
                    f"{self.name} checks that {target_name} isn't in any pain before starting.",
                    f"{self.name} gives {target_name} a treat after a successful milking.",
                ],
                NPCPersonality.INDIFFERENT: [
                    f"{self.name} mechanically hooks {target_name} up without a word.",
                    f"{self.name} barely glances at {target_name} during milking.",
                    f"{self.name} processes {target_name} like any other cow.",
                ],
            }
            return random.choice(messages.get(self.personality, messages[NPCPersonality.PROFESSIONAL]))
        
        elif action == "breed":
            if self.is_futanari:
                messages = {
                    NPCPersonality.GENTLE: [
                        f"{self.name} positions behind {target_name}, easing in slowly.",
                        f"{self.name} strokes {target_name}'s hip while breeding her gently.",
                        f"{self.name} takes her time, ensuring {target_name}'s comfort.",
                    ],
                    NPCPersonality.ROUGH: [
                        f"{self.name} mounts {target_name} without warning, driving deep.",
                        f"{self.name} grips {target_name}'s hips hard, pounding relentlessly.",
                        f"{self.name} breeds {target_name} with brutal efficiency.",
                    ],
                    NPCPersonality.SADISTIC: [
                        f"{self.name} makes {target_name} beg before filling her.",
                        f"{self.name} edges {target_name} cruelly before finally breeding her.",
                        f"{self.name} laughs as {target_name} moans under her assault.",
                    ],
                }
                return random.choice(messages.get(self.personality, messages[NPCPersonality.ROUGH]))
            else:
                return f"{self.name} assists with the breeding session."
        
        elif action == "handle":
            messages = {
                NPCPersonality.GENTLE: f"{self.name} gently leads {target_name} by her collar.",
                NPCPersonality.PROFESSIONAL: f"{self.name} efficiently moves {target_name} to position.",
                NPCPersonality.ROUGH: f"{self.name} drags {target_name} by the leash.",
                NPCPersonality.SADISTIC: f"{self.name} yanks {target_name}'s nose ring sharply.",
                NPCPersonality.CARING: f"{self.name} guides {target_name} with a soothing hand.",
                NPCPersonality.INDIFFERENT: f"{self.name} wordlessly directs {target_name}.",
            }
            return messages.get(self.personality, messages[NPCPersonality.PROFESSIONAL])
        
        elif action == "punish":
            messages = {
                NPCPersonality.GENTLE: f"{self.name} reluctantly disciplines {target_name} with light swats.",
                NPCPersonality.PROFESSIONAL: f"{self.name} administers measured punishment to {target_name}.",
                NPCPersonality.ROUGH: f"{self.name} beats {target_name}'s backside harshly.",
                NPCPersonality.SADISTIC: f"{self.name} gleefully whips {target_name}, savoring every cry.",
                NPCPersonality.CARING: f"{self.name} sighs before giving {target_name} her punishment.",
                NPCPersonality.INDIFFERENT: f"{self.name} mechanically punishes {target_name}.",
            }
            return messages.get(self.personality, messages[NPCPersonality.PROFESSIONAL])
        
        return f"{self.name} interacts with {target_name}."
    
    def to_dict(self) -> dict:
        return {
            "npc_id": self.npc_id,
            "name": self.name,
            "role": self.role.value,
            "personality": self.personality.value,
            "skill_level": self.skill_level,
            "efficiency": self.efficiency,
            "gentleness": self.gentleness,
            "is_futanari": self.is_futanari,
            "cock_size": self.cock_size,
            "hucows_handled": self.hucows_handled,
            "milk_extracted_liters": self.milk_extracted_liters,
            "breedings_performed": self.breedings_performed,
        }
    
    @classmethod
    def from_dict(cls, data: dict) -> "FarmhandNPC":
        npc = cls()
        for key, value in data.items():
            if key == "role":
                npc.role = FarmhandRole(value)
            elif key == "personality":
                npc.personality = NPCPersonality(value)
            elif hasattr(npc, key):
                setattr(npc, key, value)
        return npc


# =============================================================================
# NPC FACTORY
# =============================================================================

# Name pools
FEMALE_NAMES = [
    "Helena", "Marta", "Ingrid", "Olga", "Helga", "Brunhilde", "Greta",
    "Katja", "Sonja", "Ilse", "Frieda", "Astrid", "Sigrid", "Ursula",
]

FUTANARI_NAMES = [
    "Dominique", "Sasha", "Morgan", "Alex", "Jordan", "Riley", "Quinn",
    "Ash", "Storm", "Raven", "Phoenix", "Hunter", "Sage", "Blake",
]

MALE_NAMES = [
    "Hans", "Klaus", "Otto", "Fritz", "Heinrich", "Wilhelm", "Franz",
    "Karl", "Dieter", "Gunther", "Wolfgang", "Rolf", "Horst", "Ulrich",
]


def generate_farmhand(
    role: FarmhandRole,
    is_futanari: bool = False,
    personality: Optional[NPCPersonality] = None,
) -> FarmhandNPC:
    """Generate a random farmhand NPC."""
    
    # Pick name based on type
    if is_futanari:
        name = random.choice(FUTANARI_NAMES)
    elif role in [FarmhandRole.BREEDER]:
        name = random.choice(MALE_NAMES + FUTANARI_NAMES)
    else:
        name = random.choice(FEMALE_NAMES)
    
    # Random personality if not specified
    if personality is None:
        weights = {
            NPCPersonality.GENTLE: 15,
            NPCPersonality.PROFESSIONAL: 30,
            NPCPersonality.ROUGH: 20,
            NPCPersonality.SADISTIC: 10,
            NPCPersonality.CARING: 15,
            NPCPersonality.INDIFFERENT: 10,
        }
        personality = random.choices(
            list(weights.keys()),
            weights=list(weights.values())
        )[0]
    
    # Generate stats based on role
    skill = random.randint(40, 80)
    efficiency = random.randint(40, 80)
    
    # Gentleness based on personality
    gentleness_map = {
        NPCPersonality.GENTLE: random.randint(70, 95),
        NPCPersonality.PROFESSIONAL: random.randint(40, 60),
        NPCPersonality.ROUGH: random.randint(15, 35),
        NPCPersonality.SADISTIC: random.randint(0, 20),
        NPCPersonality.CARING: random.randint(75, 100),
        NPCPersonality.INDIFFERENT: random.randint(30, 50),
    }
    gentleness = gentleness_map.get(personality, 50)
    
    cock_size = 0
    if is_futanari:
        cock_size = random.randint(15, 28)
    
    return FarmhandNPC(
        npc_id=f"FH-{datetime.now().strftime('%Y%m%d%H%M%S')}-{random.randint(100, 999)}",
        name=name,
        role=role,
        personality=personality,
        skill_level=skill,
        efficiency=efficiency,
        gentleness=gentleness,
        is_futanari=is_futanari,
        cock_size=cock_size,
    )


def generate_farm_staff(
    num_milkers: int = 2,
    num_handlers: int = 2,
    num_breeders: int = 1,
    futa_chance: float = 0.3,
) -> List[FarmhandNPC]:
    """Generate a full farm staff."""
    staff = []
    
    for _ in range(num_milkers):
        is_futa = random.random() < futa_chance
        staff.append(generate_farmhand(FarmhandRole.MILKER, is_futa))
    
    for _ in range(num_handlers):
        is_futa = random.random() < futa_chance
        staff.append(generate_farmhand(FarmhandRole.HANDLER, is_futa))
    
    for _ in range(num_breeders):
        # Breeders more likely to be futa
        is_futa = random.random() < max(futa_chance, 0.5)
        staff.append(generate_farmhand(FarmhandRole.BREEDER, is_futa))
    
    # Add one trainer
    staff.append(generate_farmhand(FarmhandRole.TRAINER, random.random() < futa_chance))
    
    # Add one vet
    staff.append(generate_farmhand(FarmhandRole.VETERINARIAN, False))
    
    return staff


# =============================================================================
# BREEDING EVENT GENERATOR
# =============================================================================

@dataclass
class BreedingEvent:
    """Generated breeding scene."""
    
    event_id: str = ""
    bull_name: str = ""
    hucow_name: str = ""
    
    # Scene details
    location: str = "breeding pen"
    position: str = "mounted from behind"
    intensity: str = "vigorous"
    
    # Results
    duration_minutes: int = 15
    cum_volume_ml: int = 20
    conception: bool = False
    
    # Narration
    intro_text: str = ""
    action_text: str = ""
    climax_text: str = ""
    aftermath_text: str = ""
    
    def get_full_scene(self) -> str:
        """Get the complete breeding scene text."""
        return f"{self.intro_text}\n\n{self.action_text}\n\n{self.climax_text}\n\n{self.aftermath_text}"


class BreedingEventGenerator:
    """Generates detailed breeding scenes."""
    
    POSITIONS = [
        "mounted from behind",
        "pinned to the breeding frame",
        "bent over the railing",
        "on all fours in the hay",
        "pressed against the stall wall",
        "suspended in the breeding harness",
        "spread on the breeding bench",
    ]
    
    INTENSITIES = [
        ("gentle", "slow", "tender"),
        ("steady", "rhythmic", "measured"),
        ("vigorous", "eager", "enthusiastic"),
        ("rough", "aggressive", "forceful"),
        ("brutal", "savage", "relentless"),
        ("marathon", "tireless", "insatiable"),
    ]
    
    @classmethod
    def generate(
        cls,
        bull_name: str,
        hucow_name: str,
        bull_is_futanari: bool = False,
        bull_aggression: int = 50,
        hucow_in_heat: bool = True,
        conception: bool = False,
    ) -> BreedingEvent:
        """Generate a breeding event."""
        
        event = BreedingEvent(
            event_id=f"BE-{datetime.now().strftime('%Y%m%d%H%M%S')}-{random.randint(100, 999)}",
            bull_name=bull_name,
            hucow_name=hucow_name,
            conception=conception,
        )
        
        # Select position
        event.position = random.choice(cls.POSITIONS)
        
        # Select intensity based on aggression
        if bull_aggression >= 80:
            event.intensity = random.choice(cls.INTENSITIES[4])  # brutal
        elif bull_aggression >= 60:
            event.intensity = random.choice(cls.INTENSITIES[3])  # rough
        elif bull_aggression >= 40:
            event.intensity = random.choice(cls.INTENSITIES[2])  # vigorous
        else:
            event.intensity = random.choice(cls.INTENSITIES[1])  # steady
        
        # Duration and volume
        event.duration_minutes = random.randint(10, 45)
        event.cum_volume_ml = random.randint(15, 60)
        
        # Generate intro
        intro_options = [
            f"{bull_name} eyes {hucow_name} with naked hunger as she's led into the breeding pen.",
            f"{hucow_name} trembles as {bull_name} approaches, already visibly aroused.",
            f"The handlers position {hucow_name} {event.position}, presenting her to {bull_name}.",
        ]
        
        if hucow_in_heat:
            intro_options.extend([
                f"{hucow_name}'s heat-scent drives {bull_name} wild as she's brought before him.",
                f"Pheromones thick in the air, {bull_name} needs no encouragement to approach the eager {hucow_name}.",
            ])
        
        event.intro_text = random.choice(intro_options)
        
        # Generate action
        bull_pronoun = "her" if bull_is_futanari else "his"
        
        action_options = [
            f"{bull_name} mounts {hucow_name}, {event.intensity} thrusts filling her completely. "
            f"Each stroke drives deeper as {bull_pronoun} hips slap against her backside.",
            
            f"With {event.intensity} intensity, {bull_name} claims {hucow_name}. "
            f"The breeding pen fills with the wet sounds of mating and {hucow_name}'s helpless moans.",
            
            f"{bull_name} grips {hucow_name}'s hips tight, breeding her with {event.intensity} determination. "
            f"{hucow_name} can only hold on as {bull_pronoun} cock reshapes her inside.",
        ]
        
        if bull_is_futanari:
            action_options.append(
                f"{bull_name}'s heavy breasts swing with each thrust as she breeds {hucow_name} {event.intensity}ly. "
                f"Her futanari cock stretches {hucow_name} deliciously with every stroke."
            )
        
        event.action_text = random.choice(action_options)
        
        # Generate climax
        climax_options = [
            f"With a final deep thrust, {bull_name} hilts inside {hucow_name} and releases. "
            f"{event.cum_volume_ml}ml of hot seed floods {hucow_name}'s womb.",
            
            f"{bull_name} roars as {bull_pronoun} climax hits, pumping load after load into {hucow_name}. "
            f"The hucow's belly visibly swells with the volume.",
            
            f"Locking deep, {bull_name} empties {bull_pronoun}self into {hucow_name}. "
            f"The breeding is complete as cum drips from the stuffed hucow.",
        ]
        
        event.climax_text = random.choice(climax_options)
        
        # Generate aftermath
        if conception:
            aftermath_options = [
                f"{hucow_name} lies trembling in the aftermath, {bull_name}'s seed taking root in her womb. "
                f"The breeding was successful.",
                
                f"As {bull_name} pulls free, {hucow_name} is already pregnant. "
                f"Her belly will soon swell with {bull_name}'s offspring.",
                
                f"Cum pools beneath {hucow_name} as she's led away, bred and pregnant. "
                f"Another successful breeding for the farm's records.",
            ]
        else:
            aftermath_options = [
                f"{hucow_name} is left leaking {bull_name}'s seed, but no conception this time. "
                f"She'll be bred again tomorrow.",
                
                f"Despite the thorough breeding, {hucow_name} hasn't caught. "
                f"More sessions will be required.",
                
                f"{bull_name} finishes with {hucow_name}, who will need another breeding session soon.",
            ]
        
        event.aftermath_text = random.choice(aftermath_options)
        
        return event


# =============================================================================
# PRESET NPCS
# =============================================================================

PRESET_FARMHANDS = {
    "gentle_milker": FarmhandNPC(
        npc_id="PRESET-001",
        name="Helena",
        role=FarmhandRole.MILKER,
        personality=NPCPersonality.GENTLE,
        skill_level=70,
        gentleness=90,
    ),
    "rough_handler": FarmhandNPC(
        npc_id="PRESET-002",
        name="Ingrid",
        role=FarmhandRole.HANDLER,
        personality=NPCPersonality.ROUGH,
        skill_level=75,
        gentleness=25,
    ),
    "futa_breeder": FarmhandNPC(
        npc_id="PRESET-003",
        name="Dominique",
        role=FarmhandRole.BREEDER,
        personality=NPCPersonality.ROUGH,
        skill_level=80,
        gentleness=30,
        is_futanari=True,
        cock_size=22,
    ),
    "sadistic_overseer": FarmhandNPC(
        npc_id="PRESET-004",
        name="Helga",
        role=FarmhandRole.OVERSEER,
        personality=NPCPersonality.SADISTIC,
        skill_level=85,
        gentleness=10,
    ),
    "caring_trainer": FarmhandNPC(
        npc_id="PRESET-005",
        name="Marta",
        role=FarmhandRole.TRAINER,
        personality=NPCPersonality.CARING,
        skill_level=75,
        gentleness=85,
    ),
    "futa_punisher": FarmhandNPC(
        npc_id="PRESET-006",
        name="Storm",
        role=FarmhandRole.PUNISHER,
        personality=NPCPersonality.SADISTIC,
        skill_level=70,
        gentleness=5,
        is_futanari=True,
        cock_size=26,
    ),
}


__all__ = [
    "FarmhandRole",
    "NPCPersonality",
    "FarmhandNPC",
    "generate_farmhand",
    "generate_farm_staff",
    "BreedingEvent",
    "BreedingEventGenerator",
    "PRESET_FARMHANDS",
]
