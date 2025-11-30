"""
Pet Gear System
===============

Wearable gear for pet play:
- Pet hoods and masks
- Mitts and paw gloves
- Tail plugs
- Bridles and bits
- Ear accessories
- Pet collars and tags
"""

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any, Set
from enum import Enum


# =============================================================================
# ENUMS
# =============================================================================

class PetGearSlot(Enum):
    """Slots for pet gear."""
    HEAD = "head"
    FACE = "face"
    MOUTH = "mouth"
    EARS = "ears"
    NECK = "neck"
    HANDS = "hands"
    TORSO = "torso"
    WAIST = "waist"
    LEGS = "legs"
    FEET = "feet"
    TAIL = "tail"       # Tail plug slot
    GENITALS = "genitals"


class GearEffect(Enum):
    """Effects that gear can apply."""
    # Appearance changes
    EARS_ADD = "ears_add"
    TAIL_ADD = "tail_add"
    HORNS_ADD = "horns_add"
    MUZZLE_ADD = "muzzle_add"
    PAW_APPEAR = "paw_appear"
    HOOF_APPEAR = "hoof_appear"
    
    # Restrictions
    HAND_RESTRICT = "hand_restrict"
    SPEECH_RESTRICT = "speech_restrict"
    VISION_RESTRICT = "vision_restrict"
    HEARING_RESTRICT = "hearing_restrict"
    
    # Functional
    LEASH_POINT = "leash_point"
    HANDLE_GRIPS = "handle_grips"
    BELL_SOUND = "bell_sound"
    TAG_DISPLAY = "tag_display"
    
    # Special
    WAG_ABLE = "wag_able"
    POSTURE_FORCE = "posture_force"
    CRAWL_COMFORT = "crawl_comfort"
    MILKING_ACCESS = "milking_access"


# =============================================================================
# BASE PET GEAR
# =============================================================================

@dataclass
class PetGear:
    """Base class for pet play gear."""
    key: str
    name: str
    
    # Slot and wearing
    slot: PetGearSlot = PetGearSlot.NECK
    is_lockable: bool = False
    is_locked: bool = False
    
    # Effects
    effects: List[GearEffect] = field(default_factory=list)
    
    # Appearance
    appearance_add: str = ""  # Added to description
    color: str = ""
    material: str = "leather"
    
    # Pet type associations
    pet_types: List[str] = field(default_factory=list)  # Which pet types use this
    
    # Description
    short_desc: str = ""
    worn_desc: str = ""
    
    def get_effects_list(self) -> List[str]:
        """Get list of effect names."""
        return [e.value for e in self.effects]
    
    def has_effect(self, effect: GearEffect) -> bool:
        """Check if gear has specific effect."""
        return effect in self.effects
    
    def lock(self) -> bool:
        """Lock the gear if lockable."""
        if self.is_lockable:
            self.is_locked = True
            return True
        return False
    
    def unlock(self) -> bool:
        """Unlock the gear."""
        if self.is_locked:
            self.is_locked = False
            return True
        return False
    
    def get_worn_description(self, wearer_name: str = "they") -> str:
        """Get description when worn."""
        if self.worn_desc:
            return self.worn_desc.format(wearer=wearer_name)
        return f"wearing a {self.color} {self.material} {self.name}".strip()
    
    def to_dict(self) -> dict:
        return {
            "key": self.key,
            "name": self.name,
            "slot": self.slot.value,
            "is_lockable": self.is_lockable,
            "is_locked": self.is_locked,
            "effects": [e.value for e in self.effects],
            "appearance_add": self.appearance_add,
            "color": self.color,
            "material": self.material,
            "pet_types": self.pet_types,
            "short_desc": self.short_desc,
            "worn_desc": self.worn_desc,
        }
    
    @classmethod
    def from_dict(cls, data: dict) -> "PetGear":
        gear = cls(
            key=data["key"],
            name=data["name"],
        )
        gear.slot = PetGearSlot(data.get("slot", "neck"))
        gear.is_lockable = data.get("is_lockable", False)
        gear.is_locked = data.get("is_locked", False)
        gear.effects = [GearEffect(e) for e in data.get("effects", [])]
        gear.appearance_add = data.get("appearance_add", "")
        gear.color = data.get("color", "")
        gear.material = data.get("material", "leather")
        gear.pet_types = data.get("pet_types", [])
        gear.short_desc = data.get("short_desc", "")
        gear.worn_desc = data.get("worn_desc", "")
        return gear


# =============================================================================
# GEAR DEFINITIONS
# =============================================================================

# ----- HEAD GEAR -----

PUPPY_HOOD = PetGear(
    key="puppy_hood",
    name="Puppy Hood",
    slot=PetGearSlot.HEAD,
    is_lockable=True,
    effects=[GearEffect.EARS_ADD, GearEffect.MUZZLE_ADD, GearEffect.VISION_RESTRICT],
    appearance_add="floppy puppy ears and a cute muzzle",
    material="leather",
    pet_types=["puppy", "wolf"],
    short_desc="A leather hood shaped like a puppy's head with floppy ears.",
    worn_desc="{wearer}'s face is hidden behind a puppy hood, floppy ears framing their muzzle",
)

KITTEN_HOOD = PetGear(
    key="kitten_hood",
    name="Kitten Hood",
    slot=PetGearSlot.HEAD,
    is_lockable=True,
    effects=[GearEffect.EARS_ADD, GearEffect.VISION_RESTRICT],
    appearance_add="pointed cat ears",
    material="latex",
    pet_types=["kitten"],
    short_desc="A sleek latex hood with pointed cat ears.",
    worn_desc="{wearer}'s features are smoothed behind a kitten hood, pointed ears perked",
)

PONY_HOOD = PetGear(
    key="pony_hood",
    name="Pony Hood",
    slot=PetGearSlot.HEAD,
    is_lockable=True,
    effects=[GearEffect.EARS_ADD, GearEffect.VISION_RESTRICT, GearEffect.HEARING_RESTRICT],
    appearance_add="horse ears and blinders",
    material="leather",
    pet_types=["pony"],
    short_desc="A leather pony hood with upright ears and blinders.",
    worn_desc="{wearer} wears a pony hood, blinders limiting their vision to straight ahead",
)

PIG_HOOD = PetGear(
    key="pig_hood",
    name="Pig Hood",
    slot=PetGearSlot.HEAD,
    is_lockable=True,
    effects=[GearEffect.EARS_ADD, GearEffect.MUZZLE_ADD],
    appearance_add="pig ears and a snout",
    material="rubber",
    pet_types=["piggy"],
    short_desc="A rubber hood with pig ears and a prominent snout.",
    worn_desc="{wearer}'s face is transformed by a pig hood, snout protruding obscenely",
)

COW_HOOD = PetGear(
    key="cow_hood",
    name="Cow Hood",
    slot=PetGearSlot.HEAD,
    is_lockable=True,
    effects=[GearEffect.EARS_ADD, GearEffect.HORNS_ADD],
    appearance_add="cow ears and small horns",
    material="leather",
    pet_types=["cow"],
    short_desc="A leather hood with floppy cow ears and small horns.",
    worn_desc="{wearer} wears a cow hood, small horns poking up between floppy ears",
)

# ----- EAR ACCESSORIES -----

PUPPY_EARS = PetGear(
    key="puppy_ears",
    name="Puppy Ears Headband",
    slot=PetGearSlot.EARS,
    is_lockable=False,
    effects=[GearEffect.EARS_ADD],
    appearance_add="floppy puppy ears",
    material="faux fur",
    pet_types=["puppy"],
    short_desc="A headband with floppy faux fur puppy ears.",
    worn_desc="{wearer} has adorable floppy puppy ears on a headband",
)

KITTEN_EARS = PetGear(
    key="kitten_ears",
    name="Kitten Ears Headband",
    slot=PetGearSlot.EARS,
    is_lockable=False,
    effects=[GearEffect.EARS_ADD],
    appearance_add="pointed cat ears",
    material="faux fur",
    pet_types=["kitten"],
    short_desc="A headband with pointed faux fur cat ears.",
    worn_desc="{wearer} wears cute pointed kitten ears",
)

BUNNY_EARS = PetGear(
    key="bunny_ears",
    name="Bunny Ears Headband",
    slot=PetGearSlot.EARS,
    is_lockable=False,
    effects=[GearEffect.EARS_ADD],
    appearance_add="long floppy bunny ears",
    material="faux fur",
    pet_types=["bunny"],
    short_desc="A headband with long, floppy bunny ears.",
    worn_desc="{wearer} has long floppy bunny ears bouncing with each movement",
)

# ----- MOUTH GEAR -----

PONY_BIT = PetGear(
    key="pony_bit",
    name="Pony Bit Gag",
    slot=PetGearSlot.MOUTH,
    is_lockable=True,
    effects=[GearEffect.SPEECH_RESTRICT],
    material="metal and leather",
    pet_types=["pony"],
    short_desc="A metal bit on leather straps, like a horse's bridle.",
    worn_desc="{wearer} has a metal bit between their teeth, drool escaping around it",
)

PONY_BRIDLE = PetGear(
    key="pony_bridle",
    name="Full Pony Bridle",
    slot=PetGearSlot.FACE,
    is_lockable=True,
    effects=[GearEffect.SPEECH_RESTRICT, GearEffect.VISION_RESTRICT, GearEffect.HANDLE_GRIPS],
    appearance_add="a full bridle with blinders and reins",
    material="leather",
    pet_types=["pony"],
    short_desc="A complete leather bridle with bit, blinders, and reins.",
    worn_desc="{wearer} is bridled like a pony, bit in mouth, blinders restricting vision, reins dangling",
)

BONE_GAG = PetGear(
    key="bone_gag",
    name="Bone Gag",
    slot=PetGearSlot.MOUTH,
    is_lockable=True,
    effects=[GearEffect.SPEECH_RESTRICT],
    material="rubber",
    pet_types=["puppy", "wolf"],
    short_desc="A rubber bone-shaped gag.",
    worn_desc="{wearer} has a rubber bone wedged between their teeth",
)

# ----- HAND GEAR -----

PUPPY_MITTS = PetGear(
    key="puppy_mitts",
    name="Puppy Mitts",
    slot=PetGearSlot.HANDS,
    is_lockable=True,
    effects=[GearEffect.HAND_RESTRICT, GearEffect.PAW_APPEAR, GearEffect.CRAWL_COMFORT],
    appearance_add="padded paw mitts",
    material="leather",
    pet_types=["puppy", "kitten", "wolf", "fox"],
    short_desc="Padded leather mitts that make hands look like paws.",
    worn_desc="{wearer}'s hands are encased in padded paw mitts, fingers useless",
)

HOOF_GLOVES = PetGear(
    key="hoof_gloves",
    name="Hoof Gloves",
    slot=PetGearSlot.HANDS,
    is_lockable=True,
    effects=[GearEffect.HAND_RESTRICT, GearEffect.HOOF_APPEAR],
    appearance_add="hoof-shaped hand covers",
    material="leather",
    pet_types=["pony", "cow"],
    short_desc="Leather gloves that encase hands in hoof shapes.",
    worn_desc="{wearer}'s hands are locked inside hoof gloves, completely useless",
)

TROTTER_GLOVES = PetGear(
    key="trotter_gloves",
    name="Trotter Gloves",
    slot=PetGearSlot.HANDS,
    is_lockable=True,
    effects=[GearEffect.HAND_RESTRICT],
    appearance_add="pig trotter mittens",
    material="rubber",
    pet_types=["piggy"],
    short_desc="Rubber mittens shaped like pig trotters.",
    worn_desc="{wearer}'s hands are trapped in rubber trotter mittens",
)

# ----- FOOT GEAR -----

PONY_BOOTS = PetGear(
    key="pony_boots",
    name="Pony Hoof Boots",
    slot=PetGearSlot.FEET,
    is_lockable=True,
    effects=[GearEffect.HOOF_APPEAR, GearEffect.POSTURE_FORCE],
    appearance_add="hoof boots forcing them onto their toes",
    material="leather",
    pet_types=["pony"],
    short_desc="Ballet-style boots with hoof-shaped soles.",
    worn_desc="{wearer} totters on pony boots, forced onto their toes like hooves",
)

KNEE_PADS = PetGear(
    key="knee_pads",
    name="Pet Knee Pads",
    slot=PetGearSlot.LEGS,
    is_lockable=False,
    effects=[GearEffect.CRAWL_COMFORT],
    material="padded leather",
    pet_types=["puppy", "kitten", "piggy", "bunny"],
    short_desc="Padded knee pads for comfortable crawling.",
    worn_desc="{wearer} wears padded knee pads for crawling",
)

# ----- NECK GEAR -----

PET_COLLAR = PetGear(
    key="pet_collar",
    name="Pet Collar",
    slot=PetGearSlot.NECK,
    is_lockable=True,
    effects=[GearEffect.LEASH_POINT, GearEffect.TAG_DISPLAY],
    material="leather",
    pet_types=["puppy", "kitten", "bunny", "fox", "wolf"],
    short_desc="A sturdy collar with D-ring for leash attachment.",
    worn_desc="{wearer} wears a collar around their neck",
)

COW_BELL_COLLAR = PetGear(
    key="cow_bell_collar",
    name="Cow Bell Collar",
    slot=PetGearSlot.NECK,
    is_lockable=True,
    effects=[GearEffect.LEASH_POINT, GearEffect.BELL_SOUND],
    appearance_add="a bell that jingles with movement",
    material="leather",
    pet_types=["cow"],
    short_desc="A thick collar with a dangling cow bell.",
    worn_desc="{wearer} wears a collar with a bell that jingles with every movement",
)

PONY_COLLAR = PetGear(
    key="pony_collar",
    name="Pony Posture Collar",
    slot=PetGearSlot.NECK,
    is_lockable=True,
    effects=[GearEffect.LEASH_POINT, GearEffect.POSTURE_FORCE],
    material="leather",
    pet_types=["pony"],
    short_desc="A wide posture collar that keeps the head held high.",
    worn_desc="{wearer}'s head is held proudly high by a stiff posture collar",
)

# ----- TORSO GEAR -----

PET_HARNESS = PetGear(
    key="pet_harness",
    name="Pet Body Harness",
    slot=PetGearSlot.TORSO,
    is_lockable=True,
    effects=[GearEffect.HANDLE_GRIPS, GearEffect.LEASH_POINT],
    material="leather",
    pet_types=["puppy", "kitten", "bunny", "fox", "wolf"],
    short_desc="A body harness with handles and leash attachment points.",
    worn_desc="{wearer} is strapped into a body harness with convenient handles",
)

PONY_HARNESS = PetGear(
    key="pony_harness",
    name="Pony Harness",
    slot=PetGearSlot.TORSO,
    is_lockable=True,
    effects=[GearEffect.HANDLE_GRIPS, GearEffect.LEASH_POINT],
    appearance_add="straps and rings for cart attachment",
    material="leather",
    pet_types=["pony"],
    short_desc="A complex harness with straps for cart or sulky attachment.",
    worn_desc="{wearer} is fitted with a pony harness, ready to be hitched",
)

COW_HARNESS = PetGear(
    key="cow_harness",
    name="Milking Harness",
    slot=PetGearSlot.TORSO,
    is_lockable=True,
    effects=[GearEffect.HANDLE_GRIPS, GearEffect.MILKING_ACCESS],
    appearance_add="openings for easy milking access",
    material="leather",
    pet_types=["cow"],
    short_desc="A harness with openings that expose the chest for milking.",
    worn_desc="{wearer} wears a milking harness, breasts exposed and accessible",
)

# ----- TAIL GEAR -----

PUPPY_TAIL_PLUG = PetGear(
    key="puppy_tail_plug",
    name="Puppy Tail Plug",
    slot=PetGearSlot.TAIL,
    is_lockable=False,
    effects=[GearEffect.TAIL_ADD, GearEffect.WAG_ABLE],
    appearance_add="a wagging puppy tail",
    material="silicone with faux fur",
    pet_types=["puppy"],
    short_desc="A plug with an attached floppy puppy tail that can wag.",
    worn_desc="{wearer} has a fluffy puppy tail that wags when they're happy",
)

KITTEN_TAIL_PLUG = PetGear(
    key="kitten_tail_plug",
    name="Kitten Tail Plug",
    slot=PetGearSlot.TAIL,
    is_lockable=False,
    effects=[GearEffect.TAIL_ADD],
    appearance_add="a long, elegant cat tail",
    material="silicone with faux fur",
    pet_types=["kitten"],
    short_desc="A plug with a long, elegant cat tail.",
    worn_desc="{wearer} has a graceful cat tail swishing behind them",
)

BUNNY_TAIL_PLUG = PetGear(
    key="bunny_tail_plug",
    name="Bunny Tail Plug",
    slot=PetGearSlot.TAIL,
    is_lockable=False,
    effects=[GearEffect.TAIL_ADD],
    appearance_add="a fluffy cotton bunny tail",
    material="silicone with faux fur",
    pet_types=["bunny"],
    short_desc="A plug with a puffy cotton ball bunny tail.",
    worn_desc="{wearer} has an adorable fluffy bunny tail",
)

PONY_TAIL_PLUG = PetGear(
    key="pony_tail_plug",
    name="Pony Tail Plug",
    slot=PetGearSlot.TAIL,
    is_lockable=False,
    effects=[GearEffect.TAIL_ADD],
    appearance_add="a long flowing horse tail",
    material="silicone with hair",
    pet_types=["pony"],
    short_desc="A plug with a long, flowing horse hair tail.",
    worn_desc="{wearer} has a magnificent flowing pony tail",
)

PIG_TAIL_PLUG = PetGear(
    key="pig_tail_plug",
    name="Pig Tail Plug",
    slot=PetGearSlot.TAIL,
    is_lockable=False,
    effects=[GearEffect.TAIL_ADD],
    appearance_add="a curly pig tail",
    material="rubber",
    pet_types=["piggy"],
    short_desc="A plug with a curly pink pig tail.",
    worn_desc="{wearer} has a curly little pig tail poking out",
)

FOX_TAIL_PLUG = PetGear(
    key="fox_tail_plug",
    name="Fox Tail Plug",
    slot=PetGearSlot.TAIL,
    is_lockable=False,
    effects=[GearEffect.TAIL_ADD],
    appearance_add="a bushy red fox tail",
    material="silicone with faux fur",
    pet_types=["fox"],
    short_desc="A plug with a bushy orange and white fox tail.",
    worn_desc="{wearer} has a gorgeous bushy fox tail",
)

WOLF_TAIL_PLUG = PetGear(
    key="wolf_tail_plug",
    name="Wolf Tail Plug",
    slot=PetGearSlot.TAIL,
    is_lockable=False,
    effects=[GearEffect.TAIL_ADD, GearEffect.WAG_ABLE],
    appearance_add="a thick, bushy wolf tail",
    material="silicone with faux fur",
    pet_types=["wolf"],
    short_desc="A plug with a thick, impressive wolf tail.",
    worn_desc="{wearer} has a magnificent wolf tail",
)

# ----- ACCESSORIES -----

PET_BOWL = PetGear(
    key="pet_bowl",
    name="Pet Food Bowl",
    slot=PetGearSlot.NECK,  # Not worn, but tracked
    is_lockable=False,
    effects=[],
    material="stainless steel",
    pet_types=["puppy", "kitten", "piggy"],
    short_desc="A stainless steel pet bowl, sometimes with a name engraved.",
)

PET_TAG = PetGear(
    key="pet_tag",
    name="Pet ID Tag",
    slot=PetGearSlot.NECK,
    is_lockable=False,
    effects=[GearEffect.TAG_DISPLAY],
    material="metal",
    pet_types=["puppy", "kitten", "bunny", "fox", "wolf"],
    short_desc="A metal tag that can be engraved with a pet name and owner info.",
)


# =============================================================================
# GEAR REGISTRY
# =============================================================================

ALL_PET_GEAR: Dict[str, PetGear] = {
    # Hoods
    "puppy_hood": PUPPY_HOOD,
    "kitten_hood": KITTEN_HOOD,
    "pony_hood": PONY_HOOD,
    "pig_hood": PIG_HOOD,
    "cow_hood": COW_HOOD,
    # Ears
    "puppy_ears": PUPPY_EARS,
    "kitten_ears": KITTEN_EARS,
    "bunny_ears": BUNNY_EARS,
    # Mouth
    "pony_bit": PONY_BIT,
    "pony_bridle": PONY_BRIDLE,
    "bone_gag": BONE_GAG,
    # Hands
    "puppy_mitts": PUPPY_MITTS,
    "hoof_gloves": HOOF_GLOVES,
    "trotter_gloves": TROTTER_GLOVES,
    # Feet
    "pony_boots": PONY_BOOTS,
    "knee_pads": KNEE_PADS,
    # Neck
    "pet_collar": PET_COLLAR,
    "cow_bell_collar": COW_BELL_COLLAR,
    "pony_collar": PONY_COLLAR,
    # Torso
    "pet_harness": PET_HARNESS,
    "pony_harness": PONY_HARNESS,
    "cow_harness": COW_HARNESS,
    # Tails
    "puppy_tail_plug": PUPPY_TAIL_PLUG,
    "kitten_tail_plug": KITTEN_TAIL_PLUG,
    "bunny_tail_plug": BUNNY_TAIL_PLUG,
    "pony_tail_plug": PONY_TAIL_PLUG,
    "pig_tail_plug": PIG_TAIL_PLUG,
    "fox_tail_plug": FOX_TAIL_PLUG,
    "wolf_tail_plug": WOLF_TAIL_PLUG,
    # Accessories
    "pet_bowl": PET_BOWL,
    "pet_tag": PET_TAG,
}


def get_gear(key: str) -> Optional[PetGear]:
    """Get gear by key."""
    return ALL_PET_GEAR.get(key)


def get_gear_for_pet_type(pet_type: str) -> List[PetGear]:
    """Get all gear suitable for a pet type."""
    return [g for g in ALL_PET_GEAR.values() if pet_type in g.pet_types]


def get_gear_by_slot(slot: PetGearSlot) -> List[PetGear]:
    """Get all gear for a specific slot."""
    return [g for g in ALL_PET_GEAR.values() if g.slot == slot]


# =============================================================================
# PET GEAR MIXIN
# =============================================================================

class PetGearMixin:
    """
    Mixin for characters that can wear pet gear.
    """
    
    @property
    def worn_pet_gear(self) -> Dict[str, dict]:
        """Get dictionary of worn pet gear by slot."""
        return self.attributes.get("worn_pet_gear", {})
    
    def get_worn_gear_in_slot(self, slot: PetGearSlot) -> Optional[PetGear]:
        """Get gear worn in a specific slot."""
        worn = self.worn_pet_gear
        data = worn.get(slot.value)
        if data:
            return PetGear.from_dict(data)
        return None
    
    def can_wear_gear(self, gear: PetGear) -> tuple[bool, str]:
        """Check if character can wear the gear."""
        # Check slot availability
        if self.get_worn_gear_in_slot(gear.slot):
            return False, f"Already wearing something in {gear.slot.value} slot."
        
        return True, ""
    
    def wear_pet_gear(self, gear: PetGear) -> str:
        """Wear a piece of pet gear."""
        can_wear, reason = self.can_wear_gear(gear)
        if not can_wear:
            return reason
        
        worn = self.worn_pet_gear.copy()
        worn[gear.slot.value] = gear.to_dict()
        self.attributes.add("worn_pet_gear", worn)
        
        return f"You put on the {gear.name}."
    
    def remove_pet_gear(self, slot: PetGearSlot, force: bool = False) -> str:
        """Remove pet gear from a slot."""
        gear = self.get_worn_gear_in_slot(slot)
        if not gear:
            return f"Nothing worn in {slot.value} slot."
        
        if gear.is_locked and not force:
            return f"The {gear.name} is locked on!"
        
        worn = self.worn_pet_gear.copy()
        del worn[slot.value]
        self.attributes.add("worn_pet_gear", worn)
        
        return f"You remove the {gear.name}."
    
    def get_all_worn_gear(self) -> List[PetGear]:
        """Get list of all worn pet gear."""
        worn = self.worn_pet_gear
        return [PetGear.from_dict(data) for data in worn.values()]
    
    def get_gear_effects(self) -> Set[GearEffect]:
        """Get set of all active effects from worn gear."""
        effects = set()
        for gear in self.get_all_worn_gear():
            effects.update(gear.effects)
        return effects
    
    def has_gear_effect(self, effect: GearEffect) -> bool:
        """Check if any worn gear provides an effect."""
        return effect in self.get_gear_effects()
    
    def get_pet_gear_description(self) -> str:
        """Get description of all worn pet gear."""
        gear_list = self.get_all_worn_gear()
        if not gear_list:
            return ""
        
        descriptions = []
        for gear in gear_list:
            if gear.worn_desc:
                descriptions.append(gear.worn_desc.format(wearer="They"))
            elif gear.appearance_add:
                descriptions.append(f"They have {gear.appearance_add}")
        
        return " ".join(descriptions)
    
    def is_hands_restricted(self) -> bool:
        """Check if hands are restricted by gear."""
        return self.has_gear_effect(GearEffect.HAND_RESTRICT)
    
    def is_speech_restricted(self) -> bool:
        """Check if speech is restricted by gear."""
        return self.has_gear_effect(GearEffect.SPEECH_RESTRICT)
    
    def has_leash_point(self) -> bool:
        """Check if character has a leash attachment point."""
        return self.has_gear_effect(GearEffect.LEASH_POINT)


# =============================================================================
# COMPLETE GEAR SETS
# =============================================================================

GEAR_SETS: Dict[str, List[str]] = {
    "puppy_full": [
        "puppy_hood", "puppy_mitts", "knee_pads", 
        "pet_collar", "pet_harness", "puppy_tail_plug"
    ],
    "kitten_full": [
        "kitten_hood", "puppy_mitts", "knee_pads",
        "pet_collar", "pet_harness", "kitten_tail_plug"
    ],
    "pony_full": [
        "pony_hood", "pony_bridle", "hoof_gloves",
        "pony_boots", "pony_collar", "pony_harness", "pony_tail_plug"
    ],
    "cow_full": [
        "cow_hood", "hoof_gloves", "cow_bell_collar",
        "cow_harness"
    ],
    "bunny_basic": [
        "bunny_ears", "pet_collar", "bunny_tail_plug"
    ],
    "piggy_full": [
        "pig_hood", "trotter_gloves", "knee_pads",
        "pet_collar", "pig_tail_plug"
    ],
}


def get_gear_set(set_name: str) -> List[PetGear]:
    """Get all gear in a named set."""
    keys = GEAR_SETS.get(set_name, [])
    return [get_gear(k) for k in keys if get_gear(k)]


__all__ = [
    "PetGearSlot",
    "GearEffect",
    "PetGear",
    "ALL_PET_GEAR",
    "get_gear",
    "get_gear_for_pet_type",
    "get_gear_by_slot",
    "PetGearMixin",
    "GEAR_SETS",
    "get_gear_set",
]
