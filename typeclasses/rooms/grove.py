"""
Grove Room Presets

Room types specific to The Grove hub area.
These inherit from the base room types and add Grove-specific defaults.
"""

from typing import Optional, Dict, Any, List
# Handle early import during Django migration loading
try:
    from evennia.typeclasses.attributes import AttributeProperty
except (ImportError, TypeError, AttributeError):
    def AttributeProperty(default=None, **kwargs):
        return default
from typeclasses.base_rooms import Room, IndoorRoom, OutdoorRoom, ATMOSPHERE_PRESETS


# =============================================================================
# GROVE ATMOSPHERE PRESETS
# =============================================================================

GROVE_ATMOSPHERES = {
    "grove_plaza": {
        "ambient_sounds": "distant conversations, footsteps on cobblestones, a fountain splashing",
        "ambient_scents": "cooking food, flowers, the earthy smell of Yggdrasil's roots",
        "mood": "bustling",
    },
    "grove_market": {
        "ambient_sounds": "haggling voices, clinking coins, merchants calling wares",
        "ambient_scents": "spices, leather, exotic goods from nine realms",
        "mood": "commercial",
    },
    "grove_orchard": {
        "ambient_sounds": "birdsong, rustling leaves, buzzing insects",
        "ambient_scents": "ripe fruit, wildflowers, fresh grass",
        "mood": "pastoral",
    },
    "grove_waterfront": {
        "ambient_sounds": "lapping water, calling birds, creaking docks",
        "ambient_scents": "clean water, wet wood, fish",
        "mood": "serene",
    },
    "grove_residential": {
        "ambient_sounds": "quiet domesticity, distant neighbors, wind chimes",
        "ambient_scents": "cooking, flowers, home",
        "mood": "peaceful",
    },
    "grove_entertainment": {
        "ambient_sounds": "laughter, music, clinking glasses, dice rolling",
        "ambient_scents": "ale, pipe smoke, perfume",
        "mood": "lively",
    },
}

# Merge into main presets
ATMOSPHERE_PRESETS.update(GROVE_ATMOSPHERES)


# =============================================================================
# BASE GROVE ROOM
# =============================================================================

class GroveRoom(OutdoorRoom):
    """
    Base outdoor room in The Grove.
    
    All outdoor Grove areas inherit from this. Provides:
        - OOC zone protection
        - Grove region defaults
        - Safe zone flag
        
    The Grove is protected from random violence but not from
    documented claims (bounties, debts, ownership).
    """
    
    is_ooc_zone = AttributeProperty(default=True)
    is_safe_zone = AttributeProperty(default=True)
    region = AttributeProperty(default="The Grove")
    
    # Resource spawning for gathering areas
    allows_foraging = AttributeProperty(default=False)
    allows_fishing = AttributeProperty(default=False)
    allows_bug_catching = AttributeProperty(default=False)
    
    resource_tier = AttributeProperty(default="common")  # common, uncommon, rare
    
    def at_object_creation(self):
        """Set Grove defaults."""
        super().at_object_creation()
        self.apply_atmosphere("grove_plaza")  # Default atmosphere


class GroveIndoor(IndoorRoom):
    """
    Base indoor room in The Grove.
    
    Used for shops, museum, homes, etc.
    """
    
    is_ooc_zone = AttributeProperty(default=True)
    is_safe_zone = AttributeProperty(default=True)
    region = AttributeProperty(default="The Grove")
    
    def at_object_creation(self):
        """Set indoor Grove defaults."""
        super().at_object_creation()
        self.lighting = "normal"


# =============================================================================
# DISTRICT-SPECIFIC ROOMS
# =============================================================================

class GatePlazaRoom(GroveRoom):
    """
    Room in the Gate Plaza district.
    
    Where the nine realm gates are located.
    """
    
    zone = AttributeProperty(default="Gate Plaza")
    
    def at_object_creation(self):
        super().at_object_creation()
        self.apply_atmosphere("grove_plaza")


class MarketRoom(GroveRoom):
    """
    Room in the Market Square district.
    
    Outdoor market areas.
    """
    
    zone = AttributeProperty(default="Market Square")
    
    # Merchant stall support
    stall_spots = AttributeProperty(default=0)  # How many stalls can be placed
    rotating_merchants = AttributeProperty(default=False)  # Gets visiting merchants
    
    def at_object_creation(self):
        super().at_object_creation()
        self.apply_atmosphere("grove_market")


class ShopRoom(GroveIndoor):
    """
    Indoor shop in The Grove.
    """
    
    zone = AttributeProperty(default="Market Square")
    room_type = AttributeProperty(default="shop")
    
    # Shop properties
    shop_type = AttributeProperty(default="general")  # general, tools, furniture, etc.
    shopkeeper = AttributeProperty(default=None)  # NPC dbref
    
    def at_object_creation(self):
        super().at_object_creation()
        self.lighting = "bright"


class ServicesRoom(GroveIndoor):
    """
    Service building in The Grove (blacksmith, carpenter, etc).
    """
    
    zone = AttributeProperty(default="Services Row")
    room_type = AttributeProperty(default="workshop")
    
    # Crafting support
    crafting_stations = AttributeProperty(default=list)  # ["forge", "anvil", etc.]
    
    def at_object_creation(self):
        super().at_object_creation()
        self.apply_atmosphere("workshop")


# =============================================================================
# RESIDENTIAL
# =============================================================================

class ResidentialStreet(GroveRoom):
    """
    Exterior street in the Residential Quarter.
    """
    
    zone = AttributeProperty(default="Residential Quarter")
    
    # Home connections
    home_tier = AttributeProperty(default="starter")  # starter, medium, large
    
    def at_object_creation(self):
        super().at_object_creation()
        self.apply_atmosphere("grove_residential")


class PlayerHome(GroveIndoor):
    """
    Player-owned home.
    
    Can be broken into. Can be customized.
    """
    
    zone = AttributeProperty(default="Residential Quarter")
    room_type = AttributeProperty(default="home")
    is_private = AttributeProperty(default=True)
    
    # Ownership
    owner = AttributeProperty(default=None)  # Player dbref
    home_tier = AttributeProperty(default="starter")  # starter, medium, large
    
    # Security
    lock_quality = AttributeProperty(default=10)  # DC to break in
    has_alarm = AttributeProperty(default=False)
    
    # Customization
    storage_slots = AttributeProperty(default=10)
    display_slots = AttributeProperty(default=5)
    furniture_slots = AttributeProperty(default=3)
    
    def is_owner(self, character) -> bool:
        """Check if character owns this home."""
        if self.owner:
            return character.dbref == self.owner
        return False
    
    def set_owner(self, character) -> None:
        """Set the owner of this home."""
        self.owner = character.dbref


# =============================================================================
# GATHERING AREAS
# =============================================================================

class OrchardRoom(GroveRoom):
    """
    Room in the Orchards for foraging.
    """
    
    zone = AttributeProperty(default="The Orchards")
    allows_foraging = AttributeProperty(default=True)
    allows_bug_catching = AttributeProperty(default=True)
    
    # Spawns
    forage_table = AttributeProperty(default=dict)  # {"apple": 30, "mushroom": 20, ...}
    bug_table = AttributeProperty(default=dict)  # {"butterfly": 50, "beetle": 30, ...}
    
    def at_object_creation(self):
        super().at_object_creation()
        self.apply_atmosphere("grove_orchard")


class WaterfrontRoom(GroveRoom):
    """
    Room at the Waterfront for fishing.
    """
    
    zone = AttributeProperty(default="The Waterfront")
    allows_fishing = AttributeProperty(default=True)
    
    # Fishing properties
    water_type = AttributeProperty(default="fresh")  # fresh, salt, brackish
    fish_table = AttributeProperty(default=dict)  # {"trout": 40, "bass": 30, ...}
    depth = AttributeProperty(default="shallow")  # shallow, medium, deep
    
    def at_object_creation(self):
        super().at_object_creation()
        self.apply_atmosphere("grove_waterfront")


# =============================================================================
# ENTERTAINMENT
# =============================================================================

class TavernRoom(GroveIndoor):
    """
    Tavern/pub in Entertainment Row.
    """
    
    zone = AttributeProperty(default="Entertainment Row")
    room_type = AttributeProperty(default="tavern")
    
    # Tavern features
    has_bar = AttributeProperty(default=True)
    has_stage = AttributeProperty(default=False)
    has_fireplace = AttributeProperty(default=True)
    
    def at_object_creation(self):
        super().at_object_creation()
        self.apply_atmosphere("tavern")


class GamblingRoom(GroveIndoor):
    """
    Gambling den in Entertainment Row.
    """
    
    zone = AttributeProperty(default="Entertainment Row")
    room_type = AttributeProperty(default="gambling")
    
    # Gambling properties
    games_available = AttributeProperty(default=list)  # ["dice", "cards", "wheel"]
    minimum_bet = AttributeProperty(default=1)
    house_cut = AttributeProperty(default=0.1)  # 10%
    
    def at_object_creation(self):
        super().at_object_creation()
        self.apply_atmosphere("tavern")
        self.lighting = "dim"


class BathhouseRoom(GroveIndoor):
    """
    Bath house room.
    """
    
    zone = AttributeProperty(default="Entertainment Row")
    room_type = AttributeProperty(default="bathhouse")
    
    # Bath properties
    bath_type = AttributeProperty(default="public")  # public, private
    is_rentable = AttributeProperty(default=False)
    
    def at_object_creation(self):
        super().at_object_creation()
        self.apply_atmosphere("bathhouse")


class InnRoom(GroveIndoor):
    """
    Inn/hotel guest room.
    """
    
    zone = AttributeProperty(default="Entertainment Row")
    room_type = AttributeProperty(default="inn_room")
    
    is_rentable = AttributeProperty(default=True)
    rented_by = AttributeProperty(default=None)  # Current renter
    rental_expires = AttributeProperty(default=None)  # Expiration time
    
    def is_rented(self) -> bool:
        """Check if room is currently rented."""
        return self.rented_by is not None


# =============================================================================
# SCENIC/SPECIAL
# =============================================================================

class OverlookRoom(GroveRoom):
    """
    Yggdrasil Overlook - scenic viewpoint.
    """
    
    zone = AttributeProperty(default="Yggdrasil Overlook")
    
    # Special properties
    meditation_spot = AttributeProperty(default=True)
    
    def at_object_creation(self):
        super().at_object_creation()
        self.apply_atmosphere("peaceful")


# =============================================================================
# EXPORTS
# =============================================================================

__all__ = [
    # Base
    "GroveRoom",
    "GroveIndoor",
    
    # Districts
    "GatePlazaRoom",
    "MarketRoom",
    "ShopRoom",
    "ServicesRoom",
    
    # Museum
    "MuseumRoom",
    "MuseumBasement",
    
    # Residential
    "ResidentialStreet",
    "PlayerHome",
    
    # Gathering
    "OrchardRoom",
    "WaterfrontRoom",
    
    # Entertainment
    "TavernRoom",
    "GamblingRoom",
    "BathhouseRoom",
    "InnRoom",
    
    # Special
    "OverlookRoom",
]
