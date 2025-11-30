"""
World NPCs
==========

NPC templates and generators for populating the game world.
These are the characters you'll be... contending with.
"""

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any, Tuple
from enum import Enum
import random


# =============================================================================
# NPC TYPES
# =============================================================================

class NPCRole(Enum):
    """Roles NPCs can fill."""
    # Authority
    SLAVER = "slaver"
    HANDLER = "handler"
    TRAINER = "trainer"
    OVERSEER = "overseer"
    GUARD = "guard"
    
    # Business
    MADAM = "madam"
    PIMP = "pimp"
    AUCTIONEER = "auctioneer"
    MERCHANT = "merchant"
    
    # Specialized
    BREEDER = "breeder"
    MILKER = "milker"
    PONY_TRAINER = "pony_trainer"
    ARENA_MASTER = "arena_master"
    
    # Clientele
    CLIENT = "client"
    PATRON = "patron"
    
    # Dangerous
    MONSTER_KEEPER = "monster_keeper"
    CULTIST = "cultist"
    CORRUPTED = "corrupted"
    
    # Support
    SERVANT = "servant"
    SLAVE = "slave"
    HUCOW = "hucow"
    PONY = "pony"


class Disposition(Enum):
    """How the NPC treats their charges."""
    CRUEL = "cruel"
    STRICT = "strict"
    PROFESSIONAL = "professional"
    INDIFFERENT = "indifferent"
    CARING = "caring"
    PROTECTIVE = "protective"
    SADISTIC = "sadistic"
    PERVERTED = "perverted"


class NPCGender(Enum):
    """NPC genders."""
    MALE = "male"
    FEMALE = "female"
    FUTA = "futa"
    OTHER = "other"


# =============================================================================
# NPC DATA
# =============================================================================

@dataclass
class NPCStats:
    """Combat/interaction stats for NPCs."""
    strength: int = 50
    agility: int = 50
    endurance: int = 50
    charisma: int = 50
    intimidation: int = 50
    seduction: int = 50
    cruelty: int = 50
    
    # Sexual stats
    cock_size: str = "average"  # For males/futas
    cum_volume_ml: int = 30
    stamina: int = 50
    libido: int = 50


@dataclass
class NPCTemplate:
    """Template for generating NPCs."""
    template_id: str
    name: str
    role: NPCRole
    
    # Identity
    gender: NPCGender = NPCGender.MALE
    species: str = "human"
    
    # Personality
    disposition: Disposition = Disposition.PROFESSIONAL
    description: str = ""
    
    # Stats
    stats: NPCStats = field(default_factory=NPCStats)
    
    # Behavior
    greets_with: List[str] = field(default_factory=list)
    punishes_with: List[str] = field(default_factory=list)
    rewards_with: List[str] = field(default_factory=list)
    
    # Preferences
    preferred_methods: List[str] = field(default_factory=list)
    forbidden_methods: List[str] = field(default_factory=list)
    
    # Schedule
    active_hours: Tuple[int, int] = (6, 22)  # Active from 6am to 10pm
    
    def generate_greeting(self, target_name: str) -> str:
        """Generate a greeting for a target."""
        if self.greets_with:
            template = random.choice(self.greets_with)
            return template.replace("{target}", target_name).replace("{name}", self.name)
        return f"{self.name} acknowledges {target_name}."
    
    def generate_punishment(self, target_name: str, reason: str) -> str:
        """Generate a punishment description."""
        if self.punishes_with:
            method = random.choice(self.punishes_with)
            return f"{self.name} punishes {target_name} with {method} for {reason}."
        return f"{self.name} punishes {target_name} for {reason}."


# =============================================================================
# PRESET NPC TEMPLATES
# =============================================================================

SLAVERS = {
    "stern_slaver": NPCTemplate(
        template_id="stern_slaver",
        name="Harkon",
        role=NPCRole.SLAVER,
        gender=NPCGender.MALE,
        disposition=Disposition.STRICT,
        description="A stern-faced man with cold eyes and a whip at his belt. He views slaves as property to be properly broken and trained.",
        stats=NPCStats(
            strength=70, intimidation=80, cruelty=60,
            cock_size="large", cum_volume_ml=50
        ),
        greets_with=[
            "{name} looks {target} over with appraising eyes. 'Fresh stock.'",
            "{name} cracks his whip. 'Another one for processing.'",
            "'On your knees,' {name} commands {target}.",
        ],
        punishes_with=["the whip", "the cane", "public humiliation", "the stocks"],
        preferred_methods=["breaking", "discipline", "obedience training"],
    ),
    
    "cruel_mistress": NPCTemplate(
        template_id="cruel_mistress",
        name="Lady Vex",
        role=NPCRole.SLAVER,
        gender=NPCGender.FEMALE,
        disposition=Disposition.SADISTIC,
        description="A beautiful woman with a cruel smile. She takes pleasure in breaking the will of her charges.",
        stats=NPCStats(
            charisma=75, intimidation=70, cruelty=90, seduction=80
        ),
        greets_with=[
            "{name} smiles coldly at {target}. 'Oh, this one has spirit. I'll enjoy breaking it.'",
            "'Kneel.' {name}'s voice brooks no argument.",
            "{name} circles {target} like a predator. 'You belong to me now.'",
        ],
        punishes_with=["denial", "edging", "public use", "sensory deprivation"],
        preferred_methods=["psychological breaking", "pleasure torture", "conditioning"],
    ),
    
    "monster_breeder": NPCTemplate(
        template_id="monster_breeder",
        name="Grimshaw",
        role=NPCRole.MONSTER_KEEPER,
        gender=NPCGender.MALE,
        disposition=Disposition.PERVERTED,
        description="A rough man who breeds monsters and isn't above using captured women to satisfy his 'pets.'",
        stats=NPCStats(
            strength=65, cruelty=75, libido=80
        ),
        greets_with=[
            "{name} leers at {target}. 'The beasts will like this one.'",
            "'Another breeder,' {name} grunts. 'The tentacle pit needs feeding.'",
        ],
        punishes_with=["monster breeding", "oviposition", "the slime pit"],
        preferred_methods=["monster breeding", "forced impregnation", "corruption"],
    ),
}


HANDLERS = {
    "kind_handler": NPCTemplate(
        template_id="kind_handler",
        name="Maya",
        role=NPCRole.HANDLER,
        gender=NPCGender.FEMALE,
        disposition=Disposition.CARING,
        description="A gentle woman who treats her charges well, though she still expects obedience.",
        stats=NPCStats(
            charisma=70, seduction=60, cruelty=20
        ),
        greets_with=[
            "{name} smiles warmly at {target}. 'Come, let me take care of you.'",
            "'Poor thing,' {name} murmurs to {target}. 'Let me help.'",
        ],
        rewards_with=["gentle praise", "treats", "orgasm permission", "soft touches"],
        preferred_methods=["positive reinforcement", "gentle training", "affection"],
    ),
    
    "efficient_handler": NPCTemplate(
        template_id="efficient_handler",
        name="Viktor",
        role=NPCRole.HANDLER,
        gender=NPCGender.MALE,
        disposition=Disposition.PROFESSIONAL,
        description="A no-nonsense handler who runs his section like clockwork. Fair but firm.",
        stats=NPCStats(
            intimidation=60, charisma=50, cruelty=40,
            cock_size="average", cum_volume_ml=35
        ),
        greets_with=[
            "{name} nods curtly at {target}. 'Fall in line.'",
            "'Processing time,' {name} announces to {target}.",
        ],
        punishes_with=["extra duties", "reduced rations", "isolation"],
        preferred_methods=["efficiency", "routine", "discipline"],
    ),
}


BROTHEL_NPCS = {
    "stern_madam": NPCTemplate(
        template_id="stern_madam",
        name="Madame Scarlet",
        role=NPCRole.MADAM,
        gender=NPCGender.FEMALE,
        disposition=Disposition.STRICT,
        description="The iron-fisted madam of the Rose Petal. She runs a tight ship and her girls earn their keep.",
        stats=NPCStats(
            charisma=80, intimidation=65, seduction=70
        ),
        greets_with=[
            "{name} looks {target} over critically. 'You'll do. Get to work.'",
            "'Fresh meat,' {name} declares. 'Time to earn your keep, {target}.'",
        ],
        punishes_with=["extra clients", "the rough rooms", "public auction"],
        preferred_methods=["work assignments", "client management", "earnings quotas"],
    ),
    
    "sleazy_pimp": NPCTemplate(
        template_id="sleazy_pimp",
        name="Gregor",
        role=NPCRole.PIMP,
        gender=NPCGender.MALE,
        disposition=Disposition.CRUEL,
        description="A greasy man who views his 'merchandise' as disposable. Takes the lion's share of earnings.",
        stats=NPCStats(
            charisma=40, intimidation=70, cruelty=80,
            cock_size="small", libido=70
        ),
        greets_with=[
            "{name} grabs {target}'s chin. 'You work for me now.'",
            "'Another whore for my stable,' {name} sneers at {target}.",
        ],
        punishes_with=["the rough clients", "street corners", "beatings"],
        preferred_methods=["intimidation", "threats", "violence"],
    ),
}


TRAINERS = {
    "hucow_trainer": NPCTemplate(
        template_id="hucow_trainer",
        name="Dairy Master Holt",
        role=NPCRole.MILKER,
        gender=NPCGender.MALE,
        disposition=Disposition.PROFESSIONAL,
        description="A farmer who treats his hucows like livestock - fed well, milked regularly, bred efficiently.",
        stats=NPCStats(
            strength=60, charisma=40, libido=60,
            cock_size="large", cum_volume_ml=60
        ),
        greets_with=[
            "{name} examines {target}'s breasts. 'Good udders. You'll produce well.'",
            "'Into the stall with you,' {name} tells {target}.",
        ],
        preferred_methods=["milking schedules", "breeding programs", "lactation enhancement"],
    ),
    
    "pony_trainer": NPCTemplate(
        template_id="pony_trainer",
        name="Mistress Ride",
        role=NPCRole.PONY_TRAINER,
        gender=NPCGender.FUTA,
        disposition=Disposition.STRICT,
        description="An athletic futa who trains human ponies with crop and command. She rides what she trains.",
        stats=NPCStats(
            strength=70, agility=75, intimidation=65, seduction=60,
            cock_size="huge", cum_volume_ml=80
        ),
        greets_with=[
            "{name} circles {target}, crop in hand. 'You'll make a fine pony.'",
            "'Gait!' {name} commands {target}. 'Let me see you walk.'",
        ],
        punishes_with=["the crop", "extra laps", "the breeding bench"],
        preferred_methods=["gait training", "cart pulling", "dressage"],
    ),
    
    "arena_master": NPCTemplate(
        template_id="arena_master",
        name="Brutus",
        role=NPCRole.ARENA_MASTER,
        gender=NPCGender.MALE,
        disposition=Disposition.PROFESSIONAL,
        description="A scarred veteran who runs the fighting pits. Victory earns freedom - eventually.",
        stats=NPCStats(
            strength=85, agility=60, intimidation=75, cruelty=50,
            cock_size="large"
        ),
        greets_with=[
            "{name} looks {target} over. 'Can you fight? You'll learn.'",
            "'Fresh gladiator,' {name} announces. 'Train hard or die entertaining.'",
        ],
        preferred_methods=["combat training", "tournament management", "betting pools"],
    ),
    
    "corruption_cultist": NPCTemplate(
        template_id="corruption_cultist",
        name="High Priestess Lilith",
        role=NPCRole.CULTIST,
        gender=NPCGender.FUTA,
        disposition=Disposition.PERVERTED,
        description="A demon-touched priestess who converts the unwilling through pleasure and corruption.",
        stats=NPCStats(
            charisma=85, seduction=90, cruelty=70,
            cock_size="monster", cum_volume_ml=200
        ),
        greets_with=[
            "{name}'s eyes glow red as she beholds {target}. 'Another soul for my lord.'",
            "'Resistance is futile,' {name} purrs to {target}. 'And so much more fun.'",
        ],
        punishes_with=["forced transformation", "demonic breeding", "corruption rituals"],
        preferred_methods=["corruption", "demonic breeding", "bimboification"],
    ),
}


CLIENTS = {
    "nervous_noble": NPCTemplate(
        template_id="nervous_noble",
        name="Lord Ashworth",
        role=NPCRole.CLIENT,
        gender=NPCGender.MALE,
        disposition=Disposition.CARING,
        description="A nervous noble visiting the brothel in secret. Inexperienced but wealthy.",
        stats=NPCStats(
            charisma=60, intimidation=20, seduction=30,
            cock_size="average", cum_volume_ml=25, stamina=30
        ),
        greets_with=[
            "{name} fidgets nervously. 'Um... hello, {target}. You're very... lovely.'",
        ],
        preferred_methods=["gentle service", "girlfriend experience"],
    ),
    
    "rough_soldier": NPCTemplate(
        template_id="rough_soldier",
        name="Sergeant Krag",
        role=NPCRole.CLIENT,
        gender=NPCGender.MALE,
        disposition=Disposition.CRUEL,
        description="A scarred soldier who takes what he wants. Rough and demanding.",
        stats=NPCStats(
            strength=75, intimidation=70, cruelty=65,
            cock_size="large", cum_volume_ml=50, stamina=70
        ),
        greets_with=[
            "{name} grabs {target} roughly. 'You're mine for the night.'",
            "'On your knees,' {name} growls at {target}.",
        ],
        preferred_methods=["rough use", "degradation", "pain"],
    ),
    
    "monster_client": NPCTemplate(
        template_id="monster_client",
        name="Groth",
        role=NPCRole.CLIENT,
        gender=NPCGender.MALE,
        species="orc",
        disposition=Disposition.CRUEL,
        description="A massive orc with very specific needs. Not gentle.",
        stats=NPCStats(
            strength=90, intimidation=85, cruelty=70,
            cock_size="monster", cum_volume_ml=150, stamina=80, libido=90
        ),
        greets_with=[
            "{name} leers at {target} with tusked grin. 'Small. But will do.'",
        ],
        preferred_methods=["rough breeding", "inflation", "size difference"],
    ),
}


# =============================================================================
# NPC GENERATOR
# =============================================================================

def generate_npc(
    role: NPCRole = None,
    disposition: Disposition = None,
    gender: NPCGender = None,
) -> NPCTemplate:
    """Generate a random NPC."""
    
    if role:
        # Find templates matching role
        all_templates = {**SLAVERS, **HANDLERS, **BROTHEL_NPCS, **TRAINERS, **CLIENTS}
        matching = [t for t in all_templates.values() if t.role == role]
        if matching:
            template = random.choice(matching)
            return template
    
    # Generate random NPC
    names_male = ["Marcus", "Viktor", "Harkon", "Gregor", "Brutus", "Drake", "Varn"]
    names_female = ["Maya", "Lilith", "Vex", "Scarlet", "Elena", "Mira", "Sera"]
    names_futa = ["Alexia", "Morgan", "Phoenix", "Raven", "Storm"]
    
    if gender is None:
        gender = random.choice(list(NPCGender))
    
    if gender == NPCGender.MALE:
        name = random.choice(names_male)
    elif gender == NPCGender.FEMALE:
        name = random.choice(names_female)
    else:
        name = random.choice(names_futa)
    
    if role is None:
        role = random.choice(list(NPCRole))
    
    if disposition is None:
        disposition = random.choice(list(Disposition))
    
    cock_sizes = ["small", "average", "large", "huge", "monster"]
    
    return NPCTemplate(
        template_id=f"generated_{random.randint(1000, 9999)}",
        name=name,
        role=role,
        gender=gender,
        disposition=disposition,
        stats=NPCStats(
            strength=random.randint(30, 80),
            charisma=random.randint(30, 80),
            intimidation=random.randint(30, 80),
            cruelty=random.randint(20, 90),
            seduction=random.randint(30, 80),
            cock_size=random.choice(cock_sizes) if gender != NPCGender.FEMALE else "none",
            cum_volume_ml=random.randint(20, 100) if gender != NPCGender.FEMALE else 0,
        ),
    )


# =============================================================================
# ALL PRESETS
# =============================================================================

ALL_NPC_TEMPLATES = {
    **SLAVERS,
    **HANDLERS,
    **BROTHEL_NPCS,
    **TRAINERS,
    **CLIENTS,
}


__all__ = [
    "NPCRole",
    "Disposition",
    "NPCGender",
    "NPCStats",
    "NPCTemplate",
    "SLAVERS",
    "HANDLERS",
    "BROTHEL_NPCS",
    "TRAINERS",
    "CLIENTS",
    "ALL_NPC_TEMPLATES",
    "generate_npc",
]
