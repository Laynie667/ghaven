"""
Items
=====

Interactive items with species support:
- Collars (species-appropriate sizes/styles)
- Leashes (various materials/lengths)
- Toys (plugs, vibrators, rings - genital-type aware)
- Restraints (cuffs, ropes, chains, spreaders)
- Gags, blindfolds, muzzles
- Consumables (potions, treats, aphrodisiacs)
"""

from typing import Dict, List, Optional, Tuple
from enum import Enum
from random import randint, choice

from evennia.objects.objects import DefaultObject
from evennia import AttributeProperty


# =============================================================================
# ENUMS
# =============================================================================

class ItemType(Enum):
    COLLAR = "collar"
    LEASH = "leash"
    TOY = "toy"
    RESTRAINT = "restraint"
    PLUG = "plug"
    GAG = "gag"
    BLINDFOLD = "blindfold"
    RING = "ring"
    CONSUMABLE = "consumable"
    HARNESS = "harness"


class WearLocation(Enum):
    NECK = "neck"
    WRISTS = "wrists"
    ANKLES = "ankles"
    EYES = "eyes"
    MOUTH = "mouth"
    NIPPLES = "nipples"
    GENITALS = "genitals"
    ANUS = "anus"
    VAGINA = "vagina"
    TAIL_BASE = "tail_base"
    TORSO = "torso"
    MUZZLE = "muzzle"


class Material(Enum):
    LEATHER = "leather"
    METAL = "metal"
    SILK = "silk"
    ROPE = "rope"
    CHAIN = "chain"
    RUBBER = "rubber"
    GLASS = "glass"
    WOOD = "wood"
    ENCHANTED = "enchanted"


class Size(Enum):
    TINY = "tiny"
    SMALL = "small"
    MEDIUM = "medium"
    LARGE = "large"
    HUGE = "huge"
    ADJUSTABLE = "adjustable"


# =============================================================================
# SPECIES COMPATIBILITY
# =============================================================================

COLLAR_STYLES = {
    "standard": {
        "species": ["human", "elf", "dwarf", "orc", "goblin", "tiefling", 
                    "angel", "demon", "succubus"],
        "width": "narrow",
    },
    "wide": {
        "species": ["human", "elf", "wolf", "dog", "fox", "hyena", 
                    "lion", "tiger", "cat"],
        "width": "wide",
    },
    "canine": {
        "species": ["wolf", "dog", "fox", "hyena", "canine_generic"],
        "width": "wide",
        "has_d_ring": True,
    },
    "feline": {
        "species": ["cat", "lion", "tiger", "leopard", "feline_generic"],
        "width": "medium",
        "has_bell": True,
    },
    "equine": {
        "species": ["horse", "unicorn", "zebra", "equine_generic"],
        "width": "very_wide",
        "has_lead_ring": True,
    },
    "scaled": {
        "species": ["dragon", "lizard", "kobold", "snake"],
        "width": "adjustable",
    },
    "posture": {
        "species": ["human", "elf", "tiefling", "angel", "succubus"],
        "width": "very_wide",
        "restricts_head": True,
    },
    "shock": {
        "species": None,
        "has_shock": True,
    },
}

GENITAL_TOYS = {
    "canine": {
        "toys": ["knot_ring", "sheath_sleeve", "canine_plug", "knot_plug"],
        "compatible_rings": ["knot_ring", "sheath_ring"],
    },
    "equine": {
        "toys": ["flare_ring", "medial_ring", "equine_plug"],
        "compatible_rings": ["flare_ring", "medial_ring"],
    },
    "feline": {
        "toys": ["barb_sleeve", "feline_plug"],
        "compatible_rings": ["barb_ring"],
    },
    "reptile": {
        "toys": ["hemipene_sleeve", "cloaca_plug"],
        "compatible_rings": [],
    },
    "human": {
        "toys": ["cock_ring", "standard_plug", "sleeve", "cage"],
        "compatible_rings": ["cock_ring", "glans_ring"],
    },
    "avian": {
        "toys": ["cloaca_plug", "vent_toy"],
        "compatible_rings": [],
    },
}


# =============================================================================
# BASE ITEM CLASS
# =============================================================================

class Item(DefaultObject):
    """Base class for all interactive items."""
    
    item_type = AttributeProperty(default=ItemType.TOY)
    wear_location = AttributeProperty(default=None)
    is_wearable = AttributeProperty(default=False)
    is_lockable = AttributeProperty(default=False)
    is_locked = AttributeProperty(default=False)
    
    allowed_species = AttributeProperty(default=None)
    blocked_species = AttributeProperty(default=list)
    required_genital = AttributeProperty(default=None)
    
    worn_by = AttributeProperty(default=None)
    held_by = AttributeProperty(default=None)
    attached_to = AttributeProperty(default=None)
    
    material = AttributeProperty(default=Material.LEATHER)
    quality = AttributeProperty(default=50)
    size = AttributeProperty(default=Size.MEDIUM)
    durability = AttributeProperty(default=100)
    
    def can_be_used_by(self, character) -> Tuple[bool, str]:
        """Check species/genital compatibility."""
        body = character.get_body() if hasattr(character, 'get_body') else None
        if body:
            species = getattr(body, 'species_key', 'human')
            genital = getattr(body, 'genital_category', 'human')
            
            if species in (self.blocked_species or []):
                return False, f"Not compatible with {species}."
            if self.allowed_species and species not in self.allowed_species:
                return False, "Designed for other species."
            if self.required_genital and genital != self.required_genital:
                return False, f"Requires {self.required_genital} anatomy."
        return True, ""
    
    def wear(self, character, force: bool = False) -> Tuple[bool, str]:
        if not self.is_wearable:
            return False, f"{self.key} can't be worn."
        if self.worn_by:
            return False, f"{self.key} is already worn."
        if not force:
            can, reason = self.can_be_used_by(character)
            if not can:
                return False, reason
        self.worn_by = character.dbref
        self.location = character
        return True, f"You put on {self.key}."
    
    def remove(self, force: bool = False) -> Tuple[bool, str]:
        if not self.worn_by:
            return False, f"{self.key} isn't being worn."
        if self.is_locked and not force:
            return False, f"{self.key} is locked on."
        self.worn_by = None
        return True, f"{self.key} removed."
    
    def lock(self) -> Tuple[bool, str]:
        if not self.is_lockable:
            return False, f"{self.key} can't be locked."
        if self.is_locked:
            return False, f"{self.key} is already locked."
        self.is_locked = True
        return True, f"{self.key} clicks locked."
    
    def unlock(self) -> Tuple[bool, str]:
        if not self.is_locked:
            return False, f"{self.key} isn't locked."
        self.is_locked = False
        return True, f"{self.key} unlocks."
    
    def get_wearer(self):
        if not self.worn_by:
            return None
        try:
            from evennia.utils.search import search_object
            results = search_object(self.worn_by)
            return results[0] if results else None
        except Exception:
            return None
    
    def get_description(self) -> str:
        mat = self.material.value if isinstance(self.material, Material) else self.material
        return f"A {mat} {self.key}."


# =============================================================================
# COLLARS
# =============================================================================

class Collar(Item):
    """Collars for marking ownership."""
    
    item_type = AttributeProperty(default=ItemType.COLLAR)
    wear_location = AttributeProperty(default=WearLocation.NECK)
    is_wearable = AttributeProperty(default=True)
    is_lockable = AttributeProperty(default=True)
    
    collar_style = AttributeProperty(default="standard")
    has_ring = AttributeProperty(default=True)
    has_tag = AttributeProperty(default=False)
    tag_text = AttributeProperty(default="")
    has_bell = AttributeProperty(default=False)
    has_shock = AttributeProperty(default=False)
    owner_dbref = AttributeProperty(default=None)
    
    def at_object_creation(self):
        super().at_object_creation()
        style = COLLAR_STYLES.get(self.collar_style, COLLAR_STYLES["standard"])
        if style.get("species"):
            self.allowed_species = style["species"]
        if style.get("has_bell"):
            self.has_bell = True
        if style.get("has_shock"):
            self.has_shock = True
    
    def set_tag(self, text: str):
        self.has_tag = True
        self.tag_text = text
    
    def set_owner(self, owner):
        self.owner_dbref = owner.dbref if hasattr(owner, 'dbref') else str(owner)
    
    def trigger_shock(self, intensity: int = 1) -> str:
        if not self.has_shock:
            return ""
        wearer = self.get_wearer()
        if not wearer:
            return ""
        messages = {
            1: f"{wearer.key} flinches as the collar buzzes.",
            2: f"{wearer.key} yelps as the collar zaps them.",
            3: f"{wearer.key} cries out as the collar shocks them!",
        }
        return messages.get(min(3, intensity), messages[3])
    
    def get_description(self) -> str:
        mat = self.material.value if isinstance(self.material, Material) else self.material
        desc = f"A {mat} {self.collar_style} collar"
        if self.has_ring:
            desc += " with a metal ring"
        if self.has_bell:
            desc += " and a small bell"
        if self.has_shock:
            desc += " (shock-enabled)"
        if self.has_tag and self.tag_text:
            desc += f'. Tag: "{self.tag_text}"'
        return desc + "."


# =============================================================================
# LEASHES
# =============================================================================

class Leash(Item):
    """Leashes for leading collared creatures."""
    
    item_type = AttributeProperty(default=ItemType.LEASH)
    
    length = AttributeProperty(default=3)
    strength = AttributeProperty(default=50)
    attached_to = AttributeProperty(default=None)
    
    def attach_to_collar(self, collar, holder) -> Tuple[bool, str]:
        if not isinstance(collar, Collar):
            return False, "Can only attach to collars."
        if not collar.has_ring:
            return False, "Collar has no ring."
        if self.attached_to:
            return False, "Already attached."
        
        self.attached_to = collar.dbref
        self.held_by = holder.dbref
        self.location = holder
        
        wearer = collar.get_wearer()
        name = wearer.key if wearer else "them"
        return True, f"You clip the leash to {name}'s collar."
    
    def detach(self) -> Tuple[bool, str]:
        if not self.attached_to:
            return False, "Leash not attached."
        self.attached_to = None
        return True, "You unclip the leash."
    
    def get_attached_collar(self):
        if not self.attached_to:
            return None
        try:
            from evennia.utils.search import search_object
            results = search_object(self.attached_to)
            return results[0] if results else None
        except Exception:
            return None
    
    def get_leashed_creature(self):
        collar = self.get_attached_collar()
        return collar.get_wearer() if collar else None
    
    def tug(self, intensity: str = "light") -> str:
        creature = self.get_leashed_creature()
        if not creature:
            return "The leash isn't attached."
        messages = {
            "light": f"You give {creature.key}'s leash a light tug.",
            "firm": f"You tug firmly on {creature.key}'s leash.",
            "hard": f"You yank hard on {creature.key}'s leash!",
        }
        return messages.get(intensity, messages["light"])


# =============================================================================
# TOYS
# =============================================================================

class Toy(Item):
    """Base class for toys."""
    
    item_type = AttributeProperty(default=ItemType.TOY)
    is_wearable = AttributeProperty(default=True)
    
    size = AttributeProperty(default=Size.MEDIUM)
    is_vibrating = AttributeProperty(default=False)
    vibration_level = AttributeProperty(default=0)
    is_inflatable = AttributeProperty(default=False)
    inflation_level = AttributeProperty(default=0)
    is_warming = AttributeProperty(default=False)
    
    def set_vibration(self, level: int) -> Tuple[bool, str]:
        if not self.is_vibrating:
            return False, "Doesn't vibrate."
        self.vibration_level = max(0, min(5, level))
        if level == 0:
            return True, f"{self.key} stops vibrating."
        messages = {
            1: f"{self.key} hums gently.",
            2: f"{self.key} vibrates softly.",
            3: f"{self.key} buzzes steadily.",
            4: f"{self.key} vibrates intensely.",
            5: f"{self.key} buzzes powerfully!",
        }
        return True, messages.get(level, messages[3])
    
    def inflate(self, amount: int = 1) -> Tuple[bool, str]:
        if not self.is_inflatable:
            return False, "Can't inflate."
        new = min(5, self.inflation_level + amount)
        if new == self.inflation_level:
            return False, "Can't inflate further."
        self.inflation_level = new
        return True, f"{self.key} swells larger."
    
    def deflate(self) -> Tuple[bool, str]:
        if not self.is_inflatable:
            return False, "Can't deflate."
        self.inflation_level = 0
        return True, f"{self.key} deflates."
    
    def get_arousal_bonus(self) -> int:
        bonus = 0
        if self.vibration_level > 0:
            bonus += self.vibration_level * 3
        if self.inflation_level > 0:
            bonus += self.inflation_level * 2
        if self.is_warming:
            bonus += 2
        return bonus


class Plug(Toy):
    """Anal/vaginal plugs."""
    
    item_type = AttributeProperty(default=ItemType.PLUG)
    wear_location = AttributeProperty(default=WearLocation.ANUS)
    
    plug_type = AttributeProperty(default="standard")
    has_tail = AttributeProperty(default=False)
    tail_type = AttributeProperty(default=None)
    
    def get_description(self) -> str:
        mat = self.material.value if isinstance(self.material, Material) else self.material
        sz = self.size.value if isinstance(self.size, Size) else self.size
        desc = f"A {sz} {mat} {self.plug_type} plug"
        if self.has_tail:
            desc += f" with a {self.tail_type} tail"
        features = []
        if self.is_vibrating:
            features.append("vibrating")
        if self.is_inflatable:
            features.append("inflatable")
        if features:
            desc += f" ({', '.join(features)})"
        return desc + "."


class CockRing(Toy):
    """Rings for genitalia."""
    
    item_type = AttributeProperty(default=ItemType.RING)
    wear_location = AttributeProperty(default=WearLocation.GENITALS)
    
    ring_type = AttributeProperty(default="standard")
    prevents_orgasm = AttributeProperty(default=False)


# =============================================================================
# RESTRAINTS
# =============================================================================

class Restraint(Item):
    """Cuffs, ropes, chains."""
    
    item_type = AttributeProperty(default=ItemType.RESTRAINT)
    is_wearable = AttributeProperty(default=True)
    is_lockable = AttributeProperty(default=True)
    
    restraint_type = AttributeProperty(default="cuffs")
    binding_location = AttributeProperty(default="wrists")
    escape_difficulty = AttributeProperty(default=50)
    restricts_movement = AttributeProperty(default=True)
    restricts_hands = AttributeProperty(default=False)
    
    def struggle(self, character, bonus: int = 0) -> Tuple[bool, str]:
        if self.is_locked:
            return False, "Locked tight."
        roll = randint(1, 100) + bonus
        material_mod = {
            Material.ROPE: 10,
            Material.SILK: 15,
            Material.LEATHER: 0,
            Material.METAL: -10,
            Material.CHAIN: -15,
        }
        mat = self.material if isinstance(self.material, Material) else Material.LEATHER
        roll += material_mod.get(mat, 0)
        
        if roll > self.escape_difficulty:
            self.worn_by = None
            return True, f"You escape the {self.key}!"
        if roll > self.escape_difficulty - 20:
            return False, f"You almost slip free of the {self.key}..."
        return False, f"Can't escape the {self.key}."


class Gag(Item):
    """Gags to prevent speech."""
    
    item_type = AttributeProperty(default=ItemType.GAG)
    wear_location = AttributeProperty(default=WearLocation.MOUTH)
    is_wearable = AttributeProperty(default=True)
    is_lockable = AttributeProperty(default=True)
    
    gag_type = AttributeProperty(default="ball")
    speech_reduction = AttributeProperty(default=100)
    drool_factor = AttributeProperty(default=50)
    
    def filter_speech(self, text: str) -> str:
        if self.speech_reduction >= 100:
            return choice(["Mmmmph!", "Mmm mmm...", "Nngh..."])
        if self.gag_type == "ring":
            vowels = "aeiouAEIOU"
            result = ""
            for c in text:
                if c in vowels or c == " ":
                    result += c
                else:
                    result += choice(["h", "l", "th", ""])
            return result or "Aaah..."
        if self.gag_type == "bit":
            return text.replace("s", "th").replace("r", "w")[:len(text)//2] + "..."
        return "Mmph mmm..."


class Blindfold(Item):
    """Blindfolds."""
    
    item_type = AttributeProperty(default=ItemType.BLINDFOLD)
    wear_location = AttributeProperty(default=WearLocation.EYES)
    is_wearable = AttributeProperty(default=True)
    is_lockable = AttributeProperty(default=True)
    
    blindfold_type = AttributeProperty(default="cloth")
    allows_light = AttributeProperty(default=False)
    is_hood = AttributeProperty(default=False)


# =============================================================================
# CONSUMABLES
# =============================================================================

class Consumable(Item):
    """Items consumed on use."""
    
    item_type = AttributeProperty(default=ItemType.CONSUMABLE)
    
    uses_remaining = AttributeProperty(default=1)
    effect_type = AttributeProperty(default="none")
    effect_strength = AttributeProperty(default=50)
    effect_duration = AttributeProperty(default=300)
    species_effects = AttributeProperty(default=dict)
    
    def use(self, character) -> Tuple[bool, str]:
        if self.uses_remaining <= 0:
            return False, "Empty."
        self.uses_remaining -= 1
        msg = self._apply_effect(character)
        if self.uses_remaining <= 0:
            self.delete()
        return True, msg
    
    def _apply_effect(self, character) -> str:
        body = character.get_body() if hasattr(character, 'get_body') else None
        species = getattr(body, 'species_key', 'human') if body else 'human'
        species_effect = (self.species_effects or {}).get(species, {})
        
        messages = {
            "aphrodisiac": "Warmth spreads through your body...",
            "fertility": "You feel strangely receptive...",
            "stamina": "Energy courses through you!",
            "heat_trigger": "A burning need awakens...",
            "sensitivity": "Your nerves tingle...",
            "none": f"You consume {self.key}.",
        }
        msg = messages.get(self.effect_type, f"You consume {self.key}.")
        
        if species_effect.get("triggers_heat") and hasattr(character, 'trigger_heat'):
            character.trigger_heat()
            msg += " The heat takes hold."
        
        return msg


class Treat(Consumable):
    """Treats for ferals."""
    
    trust_bonus = AttributeProperty(default=5)
    hunger_reduction = AttributeProperty(default=20)
    preferred_by = AttributeProperty(default=list)
    
    def use_on(self, giver, target) -> Tuple[bool, str]:
        if self.uses_remaining <= 0:
            return False, f"No {self.key} left."
        self.uses_remaining -= 1
        
        body = target.get_body() if hasattr(target, 'get_body') else None
        species = getattr(body, 'species_key', '') if body else ''
        
        bonus = self.trust_bonus
        if species in (self.preferred_by or []):
            bonus = int(bonus * 1.5)
        
        if hasattr(target, 'update_relationship'):
            target.update_relationship(giver, trust_change=bonus)
        
        if hasattr(target, 'instincts'):
            instincts = target.instincts or {}
            if 'hunger' in instincts:
                instincts['hunger'] = max(0, instincts['hunger'] - self.hunger_reduction)
                target.instincts = instincts
        
        if self.uses_remaining <= 0:
            self.delete()
        
        return True, f"You give {target.key} the {self.key}."


# =============================================================================
# TEMPLATES
# =============================================================================

ITEM_TEMPLATES = {
    # Collars
    "leather_collar": {"key": "leather collar", "collar_style": "standard"},
    "pet_collar": {"key": "pet collar", "collar_style": "wide", "has_tag": True},
    "canine_collar": {"key": "canine collar", "collar_style": "canine"},
    "feline_collar": {"key": "feline collar", "collar_style": "feline", "has_bell": True},
    "posture_collar": {"key": "posture collar", "collar_style": "posture"},
    "shock_collar": {"key": "shock collar", "collar_style": "shock", "has_shock": True},
    
    # Leashes
    "leather_leash": {"key": "leather leash", "length": 3, "strength": 50},
    "chain_leash": {"key": "chain leash", "material": Material.CHAIN, "length": 2, "strength": 80},
    "silk_lead": {"key": "silk lead", "material": Material.SILK, "length": 4, "strength": 30},
    
    # Plugs
    "standard_plug": {"key": "rubber plug", "size": Size.MEDIUM, "material": Material.RUBBER},
    "small_plug": {"key": "small plug", "size": Size.SMALL},
    "large_plug": {"key": "large plug", "size": Size.LARGE},
    "knotted_plug": {"key": "knotted plug", "plug_type": "knotted", "size": Size.LARGE},
    "inflatable_plug": {"key": "inflatable plug", "is_inflatable": True},
    "vibrating_plug": {"key": "vibrating plug", "is_vibrating": True},
    "tail_plug_canine": {"key": "canine tail plug", "has_tail": True, "tail_type": "canine"},
    "tail_plug_feline": {"key": "feline tail plug", "has_tail": True, "tail_type": "feline", "size": Size.SMALL},
    "tail_plug_fox": {"key": "fox tail plug", "has_tail": True, "tail_type": "fox"},
    "tail_plug_bunny": {"key": "bunny tail plug", "has_tail": True, "tail_type": "bunny", "size": Size.SMALL},
    "tail_plug_equine": {"key": "equine tail plug", "has_tail": True, "tail_type": "equine", "size": Size.LARGE},
    
    # Rings
    "cock_ring": {"key": "cock ring", "ring_type": "standard"},
    "knot_ring": {"key": "knot ring", "ring_type": "knot", "required_genital": "canine"},
    "flare_ring": {"key": "flare ring", "ring_type": "flare", "required_genital": "equine"},
    "denial_ring": {"key": "denial ring", "ring_type": "denial", "prevents_orgasm": True},
    
    # Restraints
    "leather_cuffs": {"key": "leather cuffs", "restraint_type": "cuffs", "escape_difficulty": 40},
    "metal_shackles": {"key": "metal shackles", "restraint_type": "shackles", "material": Material.METAL, "escape_difficulty": 70},
    "rope_binding": {"key": "rope binding", "restraint_type": "rope", "material": Material.ROPE, "is_lockable": False},
    "spreader_bar": {"key": "spreader bar", "restraint_type": "spreader", "binding_location": "ankles"},
    "armbinder": {"key": "armbinder", "restraint_type": "armbinder", "binding_location": "arms", "restricts_hands": True},
    
    # Gags
    "ball_gag": {"key": "ball gag", "gag_type": "ball"},
    "ring_gag": {"key": "ring gag", "gag_type": "ring", "speech_reduction": 50, "drool_factor": 80},
    "bit_gag": {"key": "bit gag", "gag_type": "bit", "speech_reduction": 70},
    "muzzle": {"key": "muzzle", "gag_type": "muzzle", "speech_reduction": 90,
               "allowed_species": ["wolf", "dog", "fox", "hyena", "cat", "lion", "tiger"]},
    
    # Blindfolds
    "silk_blindfold": {"key": "silk blindfold", "material": Material.SILK},
    "leather_blindfold": {"key": "leather blindfold", "blindfold_type": "padded"},
    "hood": {"key": "leather hood", "blindfold_type": "hood", "is_hood": True},
    
    # Consumables
    "love_potion": {"key": "love potion", "effect_type": "aphrodisiac", "effect_strength": 70,
                   "species_effects": {"wolf": {"triggers_heat": True}, "dog": {"triggers_heat": True},
                                       "fox": {"triggers_heat": True}, "cat": {"triggers_heat": True}}},
    "heat_inducer": {"key": "heat inducer", "effect_type": "heat_trigger", "effect_strength": 90},
    "stamina_potion": {"key": "stamina potion", "effect_type": "stamina", "effect_duration": 1800},
    
    # Treats
    "meat_treat": {"key": "meat treat", "trust_bonus": 5, "hunger_reduction": 20,
                   "preferred_by": ["wolf", "dog", "fox", "hyena", "lion", "tiger"]},
    "fish_treat": {"key": "fish treat", "trust_bonus": 5, "hunger_reduction": 20,
                   "preferred_by": ["cat", "feline_generic", "shark", "dolphin"]},
    "sugar_cube": {"key": "sugar cube", "trust_bonus": 5, "hunger_reduction": 10,
                   "preferred_by": ["horse", "unicorn", "zebra", "equine_generic"]},
}


def get_compatible_toys(genital_type: str) -> List[str]:
    """Get toy templates compatible with genital type."""
    toys_data = GENITAL_TOYS.get(genital_type, GENITAL_TOYS["human"])
    return toys_data.get("toys", [])


def get_compatible_collars(species: str) -> List[str]:
    """Get collar styles compatible with species."""
    compatible = []
    for style_key, style_data in COLLAR_STYLES.items():
        species_list = style_data.get("species")
        if species_list is None or species in species_list:
            compatible.append(style_key)
    return compatible


__all__ = [
    "ItemType", "WearLocation", "Material", "Size",
    "COLLAR_STYLES", "GENITAL_TOYS",
    "Item", "Collar", "Leash", "Toy", "Plug", "CockRing",
    "Restraint", "Gag", "Blindfold", "Consumable", "Treat",
    "ITEM_TEMPLATES",
    "get_compatible_toys", "get_compatible_collars",
]
