"""
World Locations
===============

Location templates for the game world. These are the places
where bad things happen to good people.
"""

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any
from enum import Enum
import random


class LocationType(Enum):
    """Types of locations."""
    # Slavery
    SLAVE_MARKET = "slave_market"
    AUCTION_HOUSE = "auction_house"
    PROCESSING_CENTER = "processing_center"
    SLAVE_PEN = "slave_pen"
    
    # Training
    TRAINING_FACILITY = "training_facility"
    BREAKING_ROOM = "breaking_room"
    CONDITIONING_CHAMBER = "conditioning_chamber"
    
    # Brothel
    BROTHEL = "brothel"
    PRIVATE_ROOM = "private_room"
    VIP_LOUNGE = "vip_lounge"
    STREET_CORNER = "street_corner"
    
    # Hucow
    DAIRY_FARM = "dairy_farm"
    MILKING_PARLOR = "milking_parlor"
    BREEDING_BARN = "breeding_barn"
    HUCOW_STALL = "hucow_stall"
    
    # Pony
    STABLE = "stable"
    TRAINING_RING = "training_ring"
    SHOW_ARENA = "show_arena"
    CART_PATH = "cart_path"
    
    # Arena
    FIGHTING_PIT = "fighting_pit"
    GLADIATOR_BARRACKS = "gladiator_barracks"
    BETTING_HALL = "betting_hall"
    
    # Monster
    MONSTER_DEN = "monster_den"
    TENTACLE_PIT = "tentacle_pit"
    BREEDING_CAVE = "breeding_cave"
    SLIME_POOL = "slime_pool"
    
    # Corruption
    DARK_TEMPLE = "dark_temple"
    RITUAL_CHAMBER = "ritual_chamber"
    CORRUPTION_POOL = "corruption_pool"
    
    # Public
    PUBLIC_STOCKS = "public_stocks"
    TOWN_SQUARE = "town_square"
    FREE_USE_ZONE = "free_use_zone"


class LocationDanger(Enum):
    """How dangerous is this location."""
    SAFE = "safe"
    LOW = "low"
    MODERATE = "moderate"
    HIGH = "high"
    EXTREME = "extreme"


@dataclass
class LocationTemplate:
    """Template for a location."""
    template_id: str
    name: str
    location_type: LocationType
    
    # Description
    description: str = ""
    smell: str = ""
    sounds: str = ""
    atmosphere: str = ""
    
    # Properties
    danger_level: LocationDanger = LocationDanger.MODERATE
    is_public: bool = False
    is_locked: bool = False
    escape_difficulty: int = 50  # 0-100
    
    # NPCs typically found here
    typical_npcs: List[str] = field(default_factory=list)
    
    # Events that can happen here
    possible_events: List[str] = field(default_factory=list)
    
    # Effects on characters here
    ambient_arousal: int = 0  # Passive arousal gain per hour
    ambient_humiliation: int = 0
    ambient_corruption: int = 0
    
    # Special features
    has_restraints: bool = False
    has_milking_equipment: bool = False
    has_breeding_equipment: bool = False
    has_punishment_equipment: bool = False
    
    def get_entry_description(self) -> str:
        """Get description when entering."""
        parts = [self.description]
        if self.smell:
            parts.append(f"The air smells of {self.smell}.")
        if self.sounds:
            parts.append(f"You hear {self.sounds}.")
        if self.atmosphere:
            parts.append(self.atmosphere)
        return " ".join(parts)


# =============================================================================
# SLAVERY LOCATIONS
# =============================================================================

SLAVERY_LOCATIONS = {
    "central_market": LocationTemplate(
        template_id="central_market",
        name="The Central Slave Market",
        location_type=LocationType.SLAVE_MARKET,
        description="A large open plaza where slaves are displayed, examined, and sold. Cages line the walls, and raised platforms serve as auction blocks.",
        smell="sweat, fear, and desperation",
        sounds="the crack of whips, the murmur of haggling, the soft sobbing of the newly captured",
        atmosphere="The atmosphere is thick with commerce and human misery.",
        danger_level=LocationDanger.MODERATE,
        is_public=True,
        typical_npcs=["auctioneer", "slaver", "merchant", "guard"],
        possible_events=["auction", "inspection", "purchase", "escape_attempt"],
        ambient_humiliation=20,
        has_restraints=True,
    ),
    
    "processing_center": LocationTemplate(
        template_id="processing_center",
        name="The Processing Center",
        location_type=LocationType.PROCESSING_CENTER,
        description="A clinical facility where new acquisitions are stripped, examined, cleaned, branded, and prepared for sale or training.",
        smell="antiseptic and fear",
        sounds="the hum of machinery, clinical commands, the occasional scream",
        danger_level=LocationDanger.HIGH,
        is_locked=True,
        escape_difficulty=80,
        typical_npcs=["handler", "examiner", "brander"],
        possible_events=["stripping", "examination", "branding", "breaking_start"],
        ambient_humiliation=30,
        has_restraints=True,
        has_punishment_equipment=True,
    ),
    
    "breaking_cells": LocationTemplate(
        template_id="breaking_cells",
        name="The Breaking Cells",
        location_type=LocationType.BREAKING_ROOM,
        description="A row of soundproofed cells where stubborn slaves are broken through various methods. Each cell contains restraints and equipment for different breaking techniques.",
        smell="sweat, tears, and something sweet and cloying",
        sounds="muffled screams, mechanical sounds, soft whimpering",
        danger_level=LocationDanger.EXTREME,
        is_locked=True,
        escape_difficulty=95,
        typical_npcs=["breaker", "handler"],
        possible_events=["isolation", "pleasure_torture", "pain_breaking", "conditioning"],
        ambient_arousal=30,
        ambient_humiliation=40,
        has_restraints=True,
        has_punishment_equipment=True,
    ),
}


# =============================================================================
# BROTHEL LOCATIONS
# =============================================================================

BROTHEL_LOCATIONS = {
    "rose_petal": LocationTemplate(
        template_id="rose_petal",
        name="The Rose Petal",
        location_type=LocationType.BROTHEL,
        description="An upscale brothel with velvet drapes and soft lighting. Beautiful workers lounge on plush furniture, available for those who can pay.",
        smell="perfume, incense, and arousal",
        sounds="soft music, laughter, moans from the private rooms",
        atmosphere="The atmosphere is decadent and inviting.",
        danger_level=LocationDanger.LOW,
        is_public=True,
        typical_npcs=["madam", "courtesan", "client", "guard"],
        possible_events=["client_service", "auction", "special_request", "gangbang"],
        ambient_arousal=20,
    ),
    
    "the_pit": LocationTemplate(
        template_id="the_pit",
        name="The Pit",
        location_type=LocationType.BROTHEL,
        description="A rough, underground brothel catering to those with... particular tastes. The workers here don't always have a choice.",
        smell="sex, sweat, and desperation",
        sounds="grunts, slaps, screams both of pleasure and pain",
        atmosphere="The atmosphere is dangerous and primal.",
        danger_level=LocationDanger.HIGH,
        typical_npcs=["pimp", "whore", "rough_client", "monster_client"],
        possible_events=["rough_service", "gangbang", "monster_service", "punishment"],
        ambient_arousal=30,
        ambient_humiliation=30,
        has_restraints=True,
    ),
    
    "public_stocks": LocationTemplate(
        template_id="public_stocks",
        name="Public Stocks",
        location_type=LocationType.PUBLIC_STOCKS,
        description="Wooden stocks in the town square where slaves are locked for public use as punishment or entertainment.",
        smell="the open air mixed with cum and sweat",
        sounds="the murmur of crowds, crude comments, moans",
        danger_level=LocationDanger.MODERATE,
        is_public=True,
        typical_npcs=["guard", "townsperson", "passerby"],
        possible_events=["public_use", "humiliation", "display", "free_use"],
        ambient_arousal=10,
        ambient_humiliation=50,
        has_restraints=True,
    ),
}


# =============================================================================
# HUCOW LOCATIONS
# =============================================================================

HUCOW_LOCATIONS = {
    "green_pastures_dairy": LocationTemplate(
        template_id="green_pastures_dairy",
        name="Green Pastures Dairy",
        location_type=LocationType.DAIRY_FARM,
        description="A large dairy farm where human hucows are kept like livestock. Rows of stalls house mooing cattle-girls, their heavy breasts swaying.",
        smell="milk, hay, and animal musk",
        sounds="mechanical pumping, cowbells, soft lowing sounds",
        atmosphere="The atmosphere is efficient and agricultural.",
        danger_level=LocationDanger.MODERATE,
        is_locked=True,
        escape_difficulty=70,
        typical_npcs=["dairy_master", "handler", "bull"],
        possible_events=["milking", "breeding", "feeding", "auction"],
        ambient_arousal=20,
        ambient_humiliation=20,
        has_milking_equipment=True,
        has_breeding_equipment=True,
    ),
    
    "milking_parlor": LocationTemplate(
        template_id="milking_parlor",
        name="The Milking Parlor",
        location_type=LocationType.MILKING_PARLOR,
        description="A sterile room with multiple milking stations. Hucows are locked into position as machines drain their heavy breasts.",
        smell="fresh milk and machinery oil",
        sounds="rhythmic pumping, soft moans, the splash of milk into containers",
        danger_level=LocationDanger.LOW,
        is_locked=True,
        typical_npcs=["milker", "handler"],
        possible_events=["milking", "milking_punishment", "overproduction"],
        ambient_arousal=30,
        has_milking_equipment=True,
        has_restraints=True,
    ),
    
    "bull_pen": LocationTemplate(
        template_id="bull_pen",
        name="The Bull Pen",
        location_type=LocationType.BREEDING_BARN,
        description="A heavily-reinforced area where breeding bulls are kept. The air is thick with pheromones and the sounds of... activity.",
        smell="musk, cum, and heat",
        sounds="grunts, bellowing, the slap of flesh",
        danger_level=LocationDanger.HIGH,
        is_locked=True,
        escape_difficulty=85,
        typical_npcs=["bull", "breeder"],
        possible_events=["breeding", "knotting", "impregnation", "gangbang"],
        ambient_arousal=50,
        has_breeding_equipment=True,
        has_restraints=True,
    ),
}


# =============================================================================
# PONY LOCATIONS  
# =============================================================================

PONY_LOCATIONS = {
    "silver_bridle_stables": LocationTemplate(
        template_id="silver_bridle_stables",
        name="Silver Bridle Stables",
        location_type=LocationType.STABLE,
        description="A well-maintained stable where human ponies are housed. Each stall contains a pony in full tack, ready for training or use.",
        smell="leather, hay, and sweat",
        sounds="the clink of harnesses, clip-clop of hooves, soft neighing",
        danger_level=LocationDanger.MODERATE,
        is_locked=True,
        typical_npcs=["pony_trainer", "groom", "owner"],
        possible_events=["grooming", "tacking", "training", "breeding"],
        ambient_humiliation=30,
        has_restraints=True,
    ),
    
    "training_ring": LocationTemplate(
        template_id="training_ring",
        name="The Training Ring",
        location_type=LocationType.TRAINING_RING,
        description="A circular arena where ponies are trained in gaits, pulling, and obedience. A trainer stands in the center with crop in hand.",
        smell="dust and leather",
        sounds="commands, the crack of crops, hoof beats",
        danger_level=LocationDanger.MODERATE,
        typical_npcs=["pony_trainer"],
        possible_events=["gait_training", "cart_training", "punishment", "show_prep"],
        has_punishment_equipment=True,
    ),
}


# =============================================================================
# ARENA LOCATIONS
# =============================================================================

ARENA_LOCATIONS = {
    "crimson_pit": LocationTemplate(
        template_id="crimson_pit",
        name="The Crimson Pit",
        location_type=LocationType.FIGHTING_PIT,
        description="A sunken arena surrounded by tiers of seats. The sand is stained with... various fluids. Fighters enter but only the victor leaves unchanged.",
        smell="blood, sweat, sex, and victory",
        sounds="roaring crowds, the sounds of combat, cries of defeat",
        atmosphere="The atmosphere is electric with anticipation and lust.",
        danger_level=LocationDanger.HIGH,
        is_public=True,
        typical_npcs=["arena_master", "fighter", "bettor", "crowd"],
        possible_events=["fight", "tournament", "defeat_consequences", "victory_celebration"],
        ambient_arousal=30,
        has_restraints=True,
    ),
    
    "gladiator_barracks": LocationTemplate(
        template_id="gladiator_barracks",
        name="Gladiator Barracks",
        location_type=LocationType.GLADIATOR_BARRACKS,
        description="Spartan quarters where arena fighters live and train. Beds line the walls, and a training area occupies the center.",
        smell="sweat and determination",
        sounds="grunts of exertion, the clack of practice weapons",
        danger_level=LocationDanger.MODERATE,
        is_locked=True,
        typical_npcs=["fighter", "trainer"],
        possible_events=["training", "rest", "fighter_interaction"],
    ),
}


# =============================================================================
# MONSTER LOCATIONS
# =============================================================================

MONSTER_LOCATIONS = {
    "tentacle_pit": LocationTemplate(
        template_id="tentacle_pit",
        name="The Tentacle Pit",
        location_type=LocationType.TENTACLE_PIT,
        description="A deep pit filled with writhing tentacles. Victims are lowered in and... used. Extensively.",
        smell="slime and something alien",
        sounds="wet slithering, muffled screams, inhuman chittering",
        danger_level=LocationDanger.EXTREME,
        is_locked=True,
        escape_difficulty=95,
        typical_npcs=["monster_keeper", "tentacle_beast"],
        possible_events=["tentacle_breeding", "inflation", "multiple_penetration"],
        ambient_arousal=60,
        ambient_corruption=20,
        has_restraints=True,
    ),
    
    "slime_pool": LocationTemplate(
        template_id="slime_pool",
        name="The Slime Pool",
        location_type=LocationType.SLIME_POOL,
        description="A warm pool filled with semi-sentient slime. It pulls victims in and fills every orifice.",
        smell="something sweet and intoxicating",
        sounds="bubbling, squelching, echoing moans",
        danger_level=LocationDanger.HIGH,
        typical_npcs=["slime"],
        possible_events=["slime_engulf", "inflation", "absorption"],
        ambient_arousal=40,
        ambient_corruption=30,
    ),
    
    "breeding_cave": LocationTemplate(
        template_id="breeding_cave",
        name="The Breeding Cave",
        location_type=LocationType.BREEDING_CAVE,
        description="A dark cave system where monsters breed with captured humanoids. Eggs and offspring from past... couplings can be seen.",
        smell="musk, cum, and something ancient",
        sounds="growls, moans, the wet sounds of breeding",
        danger_level=LocationDanger.EXTREME,
        escape_difficulty=90,
        typical_npcs=["monster_keeper", "various_monsters"],
        possible_events=["monster_breeding", "oviposition", "corruption", "transformation"],
        ambient_arousal=40,
        ambient_corruption=40,
        has_breeding_equipment=True,
    ),
}


# =============================================================================
# CORRUPTION LOCATIONS
# =============================================================================

CORRUPTION_LOCATIONS = {
    "temple_of_lilith": LocationTemplate(
        template_id="temple_of_lilith",
        name="Temple of Lilith",
        location_type=LocationType.DARK_TEMPLE,
        description="A dark temple dedicated to demonic pleasures. Cultists perform rituals that transform the unwilling into willing servants of lust.",
        smell="incense and demonic essence",
        sounds="chanting, moans of ecstasy, otherworldly whispers",
        danger_level=LocationDanger.EXTREME,
        is_locked=True,
        escape_difficulty=85,
        typical_npcs=["cultist", "corrupted", "demon"],
        possible_events=["ritual", "corruption", "transformation", "demonic_breeding"],
        ambient_arousal=50,
        ambient_corruption=50,
    ),
    
    "bimbo_spa": LocationTemplate(
        template_id="bimbo_spa",
        name="The Pink Pearl Spa",
        location_type=LocationType.CORRUPTION_POOL,
        description="A seemingly innocent spa where treatments slowly transform guests into giggling, empty-headed bimbos.",
        smell="perfume and something sweet",
        sounds="giggles, vapid chatter, moans",
        atmosphere="Everything is pink and sparkly and makes you feel... fuzzy.",
        danger_level=LocationDanger.MODERATE,
        typical_npcs=["bimbo_attendant", "client"],
        possible_events=["bimbofication", "intelligence_drain", "breast_growth"],
        ambient_arousal=30,
        ambient_corruption=40,
    ),
}


# =============================================================================
# ALL LOCATIONS
# =============================================================================

ALL_LOCATION_TEMPLATES = {
    **SLAVERY_LOCATIONS,
    **BROTHEL_LOCATIONS,
    **HUCOW_LOCATIONS,
    **PONY_LOCATIONS,
    **ARENA_LOCATIONS,
    **MONSTER_LOCATIONS,
    **CORRUPTION_LOCATIONS,
}


def get_location(template_id: str) -> Optional[LocationTemplate]:
    """Get a location template by ID."""
    return ALL_LOCATION_TEMPLATES.get(template_id)


def get_locations_by_type(loc_type: LocationType) -> List[LocationTemplate]:
    """Get all locations of a specific type."""
    return [loc for loc in ALL_LOCATION_TEMPLATES.values() if loc.location_type == loc_type]


__all__ = [
    "LocationType",
    "LocationDanger",
    "LocationTemplate",
    "SLAVERY_LOCATIONS",
    "BROTHEL_LOCATIONS",
    "HUCOW_LOCATIONS",
    "PONY_LOCATIONS",
    "ARENA_LOCATIONS",
    "MONSTER_LOCATIONS",
    "CORRUPTION_LOCATIONS",
    "ALL_LOCATION_TEMPLATES",
    "get_location",
    "get_locations_by_type",
]
