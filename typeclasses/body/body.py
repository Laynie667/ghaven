"""
Body - Composed Body Instance

The Body class combines all layers into a single character body:
    1. Structure → skeleton, locomotion, manipulation
    2. Species → creature type, cosmetic features, genital_category
    3. Sex → male/female/herm/futa/etc (uses species genital type)
    4. Presentation → marks, fluids, state (character-only)

Each character has ONE Body instance.
The body tracks part STATE (injuries, prosthetics, obstructions).

Usage:
    # Create a body (NEW ORDER: structure, species, sex)
    body = Body.compose(
        structure="bipedal_digitigrade",
        species="wolf",
        sex="female"  # Will use canine genitals because wolf has genital_category="canine"
    )
    
    # Override genital type if needed
    body = Body.compose(
        structure="bipedal_plantigrade",
        species="human",
        sex="futa",
        genital_override="equine"  # Human futa with horse cock
    )
    
    # Check capabilities
    can_speak, msg = body.can_speak()
    sight_penalty = body.get_sight_penalty()
    
    # Modify
    body.injure_part("left_arm", 2, "deep gash")
    body.obstruct_part("mouth", "#gag123", "ball_gag")
    body.remove_part("left_hand")  # Amputation
    
    # Save to character
    character.db.body_data = body.to_dict()
"""

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple, Set
from enum import Enum

from .parts import PART_REGISTRY, get_part, get_children_of, PartDefinition
from .structures import get_structure, BodyStructure
from .anatomy import get_sex_config, get_genital_parts, get_parts_to_remove, SexConfig
from .species import get_species, SpeciesFeatures
from .presentation import BodyPresentation


class PartState(Enum):
    """State of a body part."""
    NORMAL = "normal"
    INJURED = "injured"
    DISABLED = "disabled"
    MISSING = "missing"
    PROSTHETIC = "prosthetic"
    TRANSFORMED = "transformed"


@dataclass
class PartInstance:
    """
    Instance data for a single body part on a character.
    
    This tracks the STATE of the part, not its definition.
    The definition comes from PART_REGISTRY.
    """
    part_key: str
    state: PartState = PartState.NORMAL
    
    # Injury
    injury_level: int = 0  # 0=none, 1=light, 2=moderate, 3=severe
    injury_desc: str = ""
    
    # Customization
    custom_desc: str = ""
    custom_size: str = ""
    custom_color: str = ""
    
    # Covering (clothing)
    covered_by: List[str] = field(default_factory=list)  # Item dbrefs
    
    # Obstruction (blocks function)
    obstructed_by: str = ""  # Item dbref or description
    obstruction_type: str = ""  # "gag", "blindfold", "bondage", etc.
    
    # Exposure through partitions
    exposed_at: str = ""  # Partition dbref
    
    # Prosthetic details
    prosthetic_type: str = ""
    prosthetic_quality: str = ""  # crude, basic, good, masterwork, magical
    
    # Transformation
    transformed_from: str = ""  # Original part key
    transformed_to: str = ""  # What it became
    
    @property
    def definition(self) -> Optional[PartDefinition]:
        """Get the part definition."""
        return get_part(self.part_key)
    
    def is_functional(self) -> bool:
        """Check if part can perform its functions."""
        if self.state in [PartState.MISSING, PartState.DISABLED]:
            return False
        if self.obstructed_by:
            return False
        if self.injury_level >= 3:
            return False
        return True


class Body:
    """
    A composed body instance for a character.
    
    Combines structure + species + sex into a working body,
    then tracks state changes during gameplay.
    """
    
    def __init__(self):
        # Source templates
        self.structure_key: str = ""
        self.species_key: str = ""
        self.sex_key: str = ""
        self.genital_category: str = ""  # From species or override
        
        # Computed properties
        self.locomotion_type: str = "bipedal"
        self.manipulation_type: str = "hands"
        self.covering_type: str = "skin"
        self.covering_description: str = ""
        self.innate_abilities: List[str] = []
        
        # Part instances
        self.parts: Dict[str, PartInstance] = {}
        
        # Which parts provide core functions
        self.locomotion_parts: List[str] = []
        self.manipulation_parts: List[str] = []
        
        # Presentation (marks, fluids, state) - character level only
        # This is populated separately, not from templates
        self.presentation: Optional[BodyPresentation] = None
        
        # Sexual state manager - tracks arousal, stretch, wetness per-part
        # This is also character level only
        self.sexual_states: Optional["SexualStateManager"] = None
    
    def init_sexual_states(self):
        """
        Initialize sexual state tracking for this body.
        
        Call this after composing the body to set up arousal,
        stretch, wetness tracking for all sexual parts.
        """
        from .states import SexualStateManager
        
        self.sexual_states = SexualStateManager()
        self.sexual_states.initialize_from_body(self)
    
    # =========================================================================
    # FACTORY / COMPOSITION
    # =========================================================================
    
    @classmethod
    def compose(
        cls,
        structure: str,
        species: str,
        sex: str,
        genital_override: Optional[str] = None,
        custom_parts: Optional[Dict[str, str]] = None,
    ) -> "Body":
        """
        Compose a body from structure + species + sex.
        
        Args:
            structure: Structure key (e.g., "bipedal_digitigrade")
            species: Species key (e.g., "wolf") - determines genital type
            sex: Sex config key (e.g., "female", "herm", "futa")
            genital_override: Override species' genital type (e.g., "equine" for horse cock on human)
            custom_parts: Optional dict of part customizations
                          {"left_arm": {"custom_desc": "...", "custom_size": "..."}}
        
        Returns:
            Composed Body instance
            
        Examples:
            # Female wolf anthro (canine genitals)
            Body.compose("bipedal_digitigrade", "wolf", "female")
            
            # Male human (human genitals)
            Body.compose("bipedal_plantigrade", "human", "male")
            
            # Human futa with horse cock
            Body.compose("bipedal_plantigrade", "human", "futa", genital_override="equine")
            
            # Herm centaur
            Body.compose("tauroid", "horse", "herm")
        """
        body = cls()
        
        struct = get_structure(structure)
        spec = get_species(species)
        sex_cfg = get_sex_config(sex)
        
        if not struct:
            raise ValueError(f"Unknown structure: {structure}")
        if not spec:
            raise ValueError(f"Unknown species: {species}")
        if not sex_cfg:
            raise ValueError(f"Unknown sex config: {sex}")
        
        # Determine genital category (from species or override)
        genital_cat = genital_override if genital_override else spec.genital_category
        
        # Store source keys
        body.structure_key = structure
        body.species_key = species
        body.sex_key = sex
        body.genital_category = genital_cat
        
        # Copy structure properties
        body.locomotion_type = struct.locomotion_type
        body.manipulation_type = struct.manipulation_type
        body.locomotion_parts = struct.locomotion_parts.copy()
        body.manipulation_parts = struct.manipulation_parts.copy()
        
        # Copy species properties
        body.covering_type = spec.covering_type
        body.covering_description = spec.covering_description
        body.innate_abilities = spec.innate_abilities.copy()
        
        # Build part list
        part_keys: Set[str] = set()
        
        # 1. Add structure parts
        part_keys.update(struct.parts)
        
        # 2. Remove structure-excluded parts
        part_keys -= set(struct.excluded_parts)
        
        # 3. Apply species replacements
        for old_key, new_key in spec.replaces_parts.items():
            if old_key in part_keys:
                part_keys.discard(old_key)
                part_keys.add(new_key)
        
        # 4. Add species parts
        part_keys.update(spec.adds_parts)
        
        # 5. Remove species-removed parts
        part_keys -= set(spec.removes_parts)
        
        # 6. Get genital parts based on category + sex config
        genital_parts = get_genital_parts(genital_cat, sex_cfg)
        part_keys.update(genital_parts)
        
        # 7. Remove parts that genital type replaces (e.g., cloaca replaces anus)
        removed_by_genitals = get_parts_to_remove(genital_cat)
        part_keys -= set(removed_by_genitals)
        
        # Create part instances
        for key in part_keys:
            instance = PartInstance(part_key=key)
            
            # Apply species descriptions
            if key in spec.part_descriptions:
                instance.custom_desc = spec.part_descriptions[key]
            
            # Apply custom parts
            if custom_parts and key in custom_parts:
                customs = custom_parts[key]
                if "custom_desc" in customs:
                    instance.custom_desc = customs["custom_desc"]
                if "custom_size" in customs:
                    instance.custom_size = customs["custom_size"]
                if "custom_color" in customs:
                    instance.custom_color = customs["custom_color"]
            
            body.parts[key] = instance
        
        # Update locomotion/manipulation parts based on replacements
        body._update_functional_parts(struct, spec)
        
        return body
    
    def _update_functional_parts(self, struct: BodyStructure, spec: SpeciesFeatures):
        """Update locomotion/manipulation part lists after replacements."""
        # Check if any locomotion parts were replaced
        new_loco = []
        for part_key in struct.locomotion_parts:
            if part_key in spec.replaces_parts:
                new_key = spec.replaces_parts[part_key]
                if new_key in self.parts:
                    new_loco.append(new_key)
            elif part_key in self.parts:
                new_loco.append(part_key)
        self.locomotion_parts = new_loco
        
        # Check if any manipulation parts were replaced
        new_manip = []
        for part_key in struct.manipulation_parts:
            if part_key in spec.replaces_parts:
                new_key = spec.replaces_parts[part_key]
                if new_key in self.parts:
                    new_manip.append(new_key)
            elif part_key in self.parts:
                new_manip.append(part_key)
        self.manipulation_parts = new_manip
    
    # =========================================================================
    # PART QUERIES
    # =========================================================================
    
    def has_part(self, part_key: str) -> bool:
        """Check if body has a part (and it's not missing)."""
        if part_key not in self.parts:
            return False
        return self.parts[part_key].state != PartState.MISSING
    
    def get_part(self, part_key: str) -> Optional[PartInstance]:
        """Get a part instance."""
        return self.parts.get(part_key)
    
    def list_parts(self, include_missing: bool = False) -> List[str]:
        """List all part keys."""
        if include_missing:
            return list(self.parts.keys())
        return [k for k, v in self.parts.items() if v.state != PartState.MISSING]
    
    def get_parts_by_state(self, state: PartState) -> List[str]:
        """Get all parts in a specific state."""
        return [k for k, v in self.parts.items() if v.state == state]
    
    def get_parts_with_function(self, function: str) -> List[str]:
        """Get all parts that provide a function and are functional."""
        result = []
        for key, instance in self.parts.items():
            if not instance.is_functional():
                continue
            defn = instance.definition
            if defn and function in defn.functions:
                result.append(key)
        return result
    
    # =========================================================================
    # MECHANICAL FUNCTION CHECKS
    # =========================================================================
    
    def can_speak(self) -> Tuple[bool, str]:
        """
        Check if character can speak.
        
        Returns:
            (can_speak, reason_if_not)
        """
        # Check for mouth/muzzle
        speech_parts = self.get_parts_with_function("speech")
        if not speech_parts:
            return False, "You have no way to speak."
        
        # Check if any speech part is obstructed
        for part_key in speech_parts:
            part = self.parts[part_key]
            if part.obstructed_by:
                return False, f"Your {part.definition.name} is obstructed by {part.obstruction_type}."
        
        return True, ""
    
    def can_hear(self) -> Tuple[bool, float]:
        """
        Check hearing capability.
        
        Returns:
            (can_hear, penalty_multiplier)
            Penalty: 0.0 = deaf, 0.5 = half hearing, 1.0 = full
        """
        hearing_parts = self.get_parts_with_function("hearing")
        if not hearing_parts:
            return False, 0.0
        
        # Count functional hearing organs
        functional = 0
        total = len(hearing_parts)
        
        for part_key in hearing_parts:
            part = self.parts[part_key]
            if part.is_functional():
                functional += 1
        
        if functional == 0:
            return False, 0.0
        
        penalty = functional / total
        return True, penalty
    
    def can_see(self) -> Tuple[bool, float]:
        """
        Check sight capability.
        
        Returns:
            (can_see, penalty_multiplier)
        """
        sight_parts = self.get_parts_with_function("sight")
        if not sight_parts:
            return False, 0.0
        
        functional = 0
        total = len(sight_parts)
        
        for part_key in sight_parts:
            part = self.parts[part_key]
            if part.is_functional():
                functional += 1
        
        if functional == 0:
            return False, 0.0
        
        penalty = functional / total
        return True, penalty
    
    def can_smell(self) -> Tuple[bool, str]:
        """Check if character can smell."""
        smell_parts = self.get_parts_with_function("smell")
        if not smell_parts:
            return False, "You have no way to smell."
        
        for part_key in smell_parts:
            part = self.parts[part_key]
            if part.is_functional():
                return True, ""
        
        return False, "Your sense of smell is blocked."
    
    def can_manipulate(self) -> Tuple[bool, str]:
        """
        Check if character can manipulate objects.
        
        Returns:
            (can_manipulate, reason_if_not)
        """
        if self.manipulation_type == "none":
            return False, "You have no way to manipulate objects."
        
        # Need at least one functional manipulation part
        for part_key in self.manipulation_parts:
            if part_key in self.parts:
                part = self.parts[part_key]
                if part.is_functional():
                    return True, ""
        
        return False, "You have no functional limbs to manipulate objects."
    
    def can_move(self) -> Tuple[bool, str]:
        """
        Check if character can move (locomotion).
        
        Returns:
            (can_move, reason_if_not)
        """
        if self.locomotion_type == "none":
            return False, "You cannot move."
        
        # Count functional locomotion parts
        functional = 0
        for part_key in self.locomotion_parts:
            if part_key in self.parts:
                part = self.parts[part_key]
                if part.is_functional():
                    functional += 1
        
        # Bipeds need at least 1 leg, quadrupeds need at least 2
        if self.locomotion_type == "bipedal":
            required = 1
        elif self.locomotion_type == "quadruped":
            required = 2
        else:
            required = 1
        
        if functional >= required:
            return True, ""
        
        return False, "You don't have enough functional limbs to move."
    
    def get_hearing_penalty(self) -> float:
        """Get hearing penalty multiplier (0.0 to 1.0)."""
        _, penalty = self.can_hear()
        return penalty
    
    def get_sight_penalty(self) -> float:
        """Get sight penalty multiplier (0.0 to 1.0)."""
        _, penalty = self.can_see()
        return penalty
    
    def get_movement_penalty(self) -> float:
        """
        Get movement penalty multiplier.
        
        Based on injuries, missing parts, etc.
        """
        if not self.locomotion_parts:
            return 0.0
        
        total_penalty = 0.0
        for part_key in self.locomotion_parts:
            if part_key not in self.parts:
                total_penalty += 1.0
                continue
            
            part = self.parts[part_key]
            if part.state == PartState.MISSING:
                total_penalty += 1.0
            elif part.state == PartState.DISABLED:
                total_penalty += 0.8
            elif part.state == PartState.PROSTHETIC:
                # Prosthetics help but not fully
                quality_penalty = {
                    "crude": 0.5,
                    "basic": 0.3,
                    "good": 0.2,
                    "masterwork": 0.1,
                    "magical": 0.0,
                }
                total_penalty += quality_penalty.get(part.prosthetic_quality, 0.3)
            elif part.injury_level > 0:
                total_penalty += part.injury_level * 0.15
        
        # Convert to multiplier
        penalty_per_part = total_penalty / len(self.locomotion_parts)
        return max(0.0, 1.0 - penalty_per_part)
    
    # =========================================================================
    # PART MODIFICATION
    # =========================================================================
    
    def add_part(self, part_key: str, custom_desc: str = "") -> bool:
        """
        Add a part to the body (e.g., tail, wings, horns).
        
        Returns True if added, False if already exists.
        """
        if part_key in self.parts and self.parts[part_key].state != PartState.MISSING:
            return False
        
        instance = PartInstance(part_key=part_key)
        if custom_desc:
            instance.custom_desc = custom_desc
        
        self.parts[part_key] = instance
        return True
    
    def remove_part(self, part_key: str, cascade: bool = True) -> List[str]:
        """
        Remove a part (amputation).
        
        Args:
            part_key: Part to remove
            cascade: If True, also remove child parts
        
        Returns:
            List of removed part keys
        """
        removed = []
        
        if part_key not in self.parts:
            return removed
        
        # Mark as missing
        self.parts[part_key].state = PartState.MISSING
        removed.append(part_key)
        
        # Cascade to children
        if cascade:
            children = get_children_of(part_key)
            for child in children:
                if child.key in self.parts:
                    child_removed = self.remove_part(child.key, cascade=True)
                    removed.extend(child_removed)
        
        return removed
    
    def restore_part(self, part_key: str) -> bool:
        """
        Restore a missing part (regeneration, magic).
        
        Returns True if restored.
        """
        if part_key not in self.parts:
            return False
        
        part = self.parts[part_key]
        if part.state != PartState.MISSING:
            return False
        
        part.state = PartState.NORMAL
        part.injury_level = 0
        part.injury_desc = ""
        part.prosthetic_type = ""
        part.prosthetic_quality = ""
        
        return True
    
    def attach_prosthetic(
        self,
        part_key: str,
        prosthetic_type: str,
        quality: str = "basic"
    ) -> bool:
        """
        Attach a prosthetic to a missing part.
        
        Args:
            part_key: The missing part
            prosthetic_type: Type of prosthetic
            quality: crude, basic, good, masterwork, magical
        
        Returns True if attached.
        """
        if part_key not in self.parts:
            return False
        
        part = self.parts[part_key]
        if part.state != PartState.MISSING:
            return False
        
        part.state = PartState.PROSTHETIC
        part.prosthetic_type = prosthetic_type
        part.prosthetic_quality = quality
        
        return True
    
    def remove_prosthetic(self, part_key: str) -> bool:
        """Remove a prosthetic, returning part to missing state."""
        if part_key not in self.parts:
            return False
        
        part = self.parts[part_key]
        if part.state != PartState.PROSTHETIC:
            return False
        
        part.state = PartState.MISSING
        part.prosthetic_type = ""
        part.prosthetic_quality = ""
        
        return True
    
    # =========================================================================
    # OBSTRUCTION
    # =========================================================================
    
    def obstruct_part(
        self,
        part_key: str,
        obstructor: str,
        obstruction_type: str
    ) -> bool:
        """
        Obstruct a part's function.
        
        Args:
            part_key: Part to obstruct
            obstructor: What's blocking it (item dbref or description)
            obstruction_type: Type (gag, blindfold, bondage, etc.)
        
        Returns True if obstructed.
        """
        if part_key not in self.parts:
            return False
        
        part = self.parts[part_key]
        part.obstructed_by = obstructor
        part.obstruction_type = obstruction_type
        
        return True
    
    def clear_obstruction(self, part_key: str) -> bool:
        """Remove obstruction from a part."""
        if part_key not in self.parts:
            return False
        
        part = self.parts[part_key]
        part.obstructed_by = ""
        part.obstruction_type = ""
        
        return True
    
    def get_obstructed_parts(self) -> Dict[str, str]:
        """Get dict of obstructed parts {part_key: obstruction_type}."""
        return {
            k: v.obstruction_type
            for k, v in self.parts.items()
            if v.obstructed_by
        }
    
    # =========================================================================
    # COVERING (CLOTHING)
    # =========================================================================
    
    def cover_part(self, part_key: str, item_dbref: str) -> bool:
        """Add clothing/covering to a part."""
        if part_key not in self.parts:
            return False
        
        part = self.parts[part_key]
        if item_dbref not in part.covered_by:
            part.covered_by.append(item_dbref)
        
        return True
    
    def uncover_part(self, part_key: str, item_dbref: str) -> bool:
        """Remove clothing from a part."""
        if part_key not in self.parts:
            return False
        
        part = self.parts[part_key]
        if item_dbref in part.covered_by:
            part.covered_by.remove(item_dbref)
            return True
        
        return False
    
    def is_part_covered(self, part_key: str) -> bool:
        """Check if a part is covered by clothing."""
        if part_key not in self.parts:
            return False
        return bool(self.parts[part_key].covered_by)
    
    def get_exposed_parts(self, include_sexual: bool = False) -> List[str]:
        """Get list of uncovered parts."""
        exposed = []
        for key, part in self.parts.items():
            if part.state == PartState.MISSING:
                continue
            if part.covered_by:
                continue
            
            defn = part.definition
            if defn and defn.is_sexual and not include_sexual:
                continue
            
            exposed.append(key)
        
        return exposed
    
    def get_covered_parts(self) -> List[str]:
        """Get list of covered parts."""
        return [k for k, v in self.parts.items() if v.covered_by]
    
    # =========================================================================
    # EXPOSURE (PARTITIONS)
    # =========================================================================
    
    def expose_part_at(self, part_key: str, partition_dbref: str) -> bool:
        """Mark a part as exposed through a partition."""
        if part_key not in self.parts:
            return False
        
        self.parts[part_key].exposed_at = partition_dbref
        return True
    
    def unexpose_part(self, part_key: str) -> bool:
        """Remove part from partition exposure."""
        if part_key not in self.parts:
            return False
        
        self.parts[part_key].exposed_at = ""
        return True
    
    def unexpose_all(self):
        """Remove all parts from partition exposure."""
        for part in self.parts.values():
            part.exposed_at = ""
    
    def get_parts_exposed_at(self, partition_dbref: str) -> List[str]:
        """Get parts exposed at a specific partition."""
        return [
            k for k, v in self.parts.items()
            if v.exposed_at == partition_dbref
        ]
    
    def get_all_exposed_parts(self) -> Dict[str, str]:
        """Get dict of {part_key: partition_dbref} for all exposed parts."""
        return {
            k: v.exposed_at
            for k, v in self.parts.items()
            if v.exposed_at
        }
    
    # =========================================================================
    # INJURY
    # =========================================================================
    
    def injure_part(self, part_key: str, level: int, description: str = "") -> bool:
        """
        Injure a part.
        
        Args:
            part_key: Part to injure
            level: 1=light, 2=moderate, 3=severe
            description: Injury description
        
        Returns True if injured.
        """
        if part_key not in self.parts:
            return False
        
        part = self.parts[part_key]
        if part.state == PartState.MISSING:
            return False
        
        part.injury_level = min(3, max(0, level))
        part.injury_desc = description
        
        if part.injury_level > 0:
            part.state = PartState.INJURED
        
        return True
    
    def heal_part(self, part_key: str, amount: int = 1) -> bool:
        """
        Heal a part's injuries.
        
        Args:
            part_key: Part to heal
            amount: How much to reduce injury level
        
        Returns True if healed.
        """
        if part_key not in self.parts:
            return False
        
        part = self.parts[part_key]
        if part.state == PartState.MISSING:
            return False
        
        part.injury_level = max(0, part.injury_level - amount)
        
        if part.injury_level == 0:
            part.injury_desc = ""
            if part.state == PartState.INJURED:
                part.state = PartState.NORMAL
        
        return True
    
    def get_injured_parts(self) -> Dict[str, int]:
        """Get dict of injured parts {part_key: injury_level}."""
        return {
            k: v.injury_level
            for k, v in self.parts.items()
            if v.injury_level > 0
        }
    
    # =========================================================================
    # DESCRIPTION
    # =========================================================================
    
    def get_part_description(self, part_key: str) -> str:
        """Get full description of a part with current state."""
        if part_key not in self.parts:
            return ""
        
        part = self.parts[part_key]
        defn = part.definition
        
        if part.state == PartState.MISSING:
            return f"The {defn.name if defn else part_key} is missing."
        
        # Base description
        if part.custom_desc:
            desc = part.custom_desc
        elif defn and defn.default_desc:
            desc = defn.default_desc
        else:
            desc = f"A {defn.name if defn else part_key}."
        
        # Add size
        if part.custom_size:
            desc = f"A {part.custom_size} {desc.lstrip('A a ')}"
        
        # Add color
        if part.custom_color:
            desc = f"{part.custom_color.title()}-colored {desc.lstrip('A a ')}"
        
        # State modifiers
        modifiers = []
        
        if part.state == PartState.PROSTHETIC:
            modifiers.append(f"({part.prosthetic_quality} {part.prosthetic_type} prosthetic)")
        
        if part.injury_level > 0:
            injury_words = {1: "lightly injured", 2: "injured", 3: "severely injured"}
            injury = injury_words.get(part.injury_level, "injured")
            if part.injury_desc:
                modifiers.append(f"({injury}: {part.injury_desc})")
            else:
                modifiers.append(f"({injury})")
        
        if part.obstructed_by:
            modifiers.append(f"(obstructed by {part.obstruction_type})")
        
        if part.covered_by:
            modifiers.append("(covered)")
        
        if modifiers:
            desc = f"{desc} {' '.join(modifiers)}"
        
        return desc
    
    def describe_body(
        self,
        include_covered: bool = False,
        include_sexual: bool = False,
        include_presentation: bool = True
    ) -> str:
        """
        Generate full body description.
        
        Args:
            include_covered: Include parts hidden by clothing
            include_sexual: Include sexual parts
            include_presentation: Include marks/fluids/state
        
        Returns:
            Multi-line description string
        """
        lines = []
        
        # General
        spec = get_species(self.species_key)
        if spec and spec.covering_description:
            lines.append(spec.covering_description)
        
        # Group parts by region
        regions = {
            "head": [],
            "torso": [],
            "arms": [],
            "legs": [],
            "tail": [],
            "wings": [],
            "other": [],
        }
        
        for key, part in self.parts.items():
            if part.state == PartState.MISSING:
                continue
            
            defn = part.definition
            if not defn:
                continue
            
            if defn.is_sexual and not include_sexual:
                continue
            
            if part.covered_by and not include_covered:
                continue
            
            # Categorize
            if "head" in key or "ear" in key or "eye" in key or "muzzle" in key or "face" in key:
                regions["head"].append(key)
            elif "arm" in key or "hand" in key or "finger" in key or "paw" in key and "fore" in key:
                regions["arms"].append(key)
            elif "leg" in key or "foot" in key or "toe" in key or "hoof" in key or "paw" in key and "hind" in key:
                regions["legs"].append(key)
            elif "tail" in key:
                regions["tail"].append(key)
            elif "wing" in key:
                regions["wings"].append(key)
            elif "torso" in key or "chest" in key or "back" in key or "stomach" in key:
                regions["torso"].append(key)
            else:
                regions["other"].append(key)
        
        # Describe notable features
        for region, parts in regions.items():
            if not parts:
                continue
            
            notable = []
            for part_key in parts:
                part = self.parts[part_key]
                if part.custom_desc or part.injury_level > 0 or part.state != PartState.NORMAL:
                    notable.append(self.get_part_description(part_key))
            
            if notable:
                lines.extend(notable)
        
        # Presentation (character-level only)
        if include_presentation and self.presentation:
            pres_desc = self.presentation.describe_overall(include_sexual)
            if pres_desc:
                lines.append("")
                lines.append(pres_desc)
        
        return "\n".join(lines)
    
    # =========================================================================
    # SERIALIZATION
    # =========================================================================
    
    def to_dict(self) -> Dict:
        """Serialize body to dict for storage."""
        return {
            "structure_key": self.structure_key,
            "species_key": self.species_key,
            "sex_key": self.sex_key,
            "genital_category": self.genital_category,
            "locomotion_type": self.locomotion_type,
            "manipulation_type": self.manipulation_type,
            "covering_type": self.covering_type,
            "covering_description": self.covering_description,
            "innate_abilities": self.innate_abilities,
            "locomotion_parts": self.locomotion_parts,
            "manipulation_parts": self.manipulation_parts,
            "parts": {
                key: {
                    "part_key": p.part_key,
                    "state": p.state.value,
                    "injury_level": p.injury_level,
                    "injury_desc": p.injury_desc,
                    "custom_desc": p.custom_desc,
                    "custom_size": p.custom_size,
                    "custom_color": p.custom_color,
                    "covered_by": p.covered_by,
                    "obstructed_by": p.obstructed_by,
                    "obstruction_type": p.obstruction_type,
                    "exposed_at": p.exposed_at,
                    "prosthetic_type": p.prosthetic_type,
                    "prosthetic_quality": p.prosthetic_quality,
                    "transformed_from": p.transformed_from,
                    "transformed_to": p.transformed_to,
                }
                for key, p in self.parts.items()
            },
            "presentation": self.presentation.to_dict() if self.presentation else None,
            "sexual_states": self.sexual_states.to_dict() if self.sexual_states else None,
        }
    
    @classmethod
    def from_dict(cls, data: Dict) -> "Body":
        """Deserialize body from dict."""
        from .states import SexualStateManager
        
        body = cls()
        
        body.structure_key = data.get("structure_key", "")
        body.species_key = data.get("species_key", "")
        body.sex_key = data.get("sex_key", "")
        body.genital_category = data.get("genital_category", "")
        body.locomotion_type = data.get("locomotion_type", "bipedal")
        body.manipulation_type = data.get("manipulation_type", "hands")
        body.covering_type = data.get("covering_type", "skin")
        body.covering_description = data.get("covering_description", "")
        body.innate_abilities = data.get("innate_abilities", [])
        body.locomotion_parts = data.get("locomotion_parts", [])
        body.manipulation_parts = data.get("manipulation_parts", [])
        
        for key, pdata in data.get("parts", {}).items():
            part = PartInstance(
                part_key=pdata["part_key"],
                state=PartState(pdata.get("state", "normal")),
                injury_level=pdata.get("injury_level", 0),
                injury_desc=pdata.get("injury_desc", ""),
                custom_desc=pdata.get("custom_desc", ""),
                custom_size=pdata.get("custom_size", ""),
                custom_color=pdata.get("custom_color", ""),
                covered_by=pdata.get("covered_by", []),
                obstructed_by=pdata.get("obstructed_by", ""),
                obstruction_type=pdata.get("obstruction_type", ""),
                exposed_at=pdata.get("exposed_at", ""),
                prosthetic_type=pdata.get("prosthetic_type", ""),
                prosthetic_quality=pdata.get("prosthetic_quality", ""),
                transformed_from=pdata.get("transformed_from", ""),
                transformed_to=pdata.get("transformed_to", ""),
            )
            body.parts[key] = part
        
        pres_data = data.get("presentation")
        if pres_data:
            body.presentation = BodyPresentation.from_dict(pres_data)
        
        sex_state_data = data.get("sexual_states")
        if sex_state_data:
            body.sexual_states = SexualStateManager.from_dict(sex_state_data)
        
        return body


# =============================================================================
# PRESET BODY COMPOSITIONS
# Quick-compose common body types
# New signature: compose(structure, species, sex)
# =============================================================================

def compose_human_male() -> Body:
    """Standard human male."""
    return Body.compose("bipedal_plantigrade", "human", "male")

def compose_human_female() -> Body:
    """Standard human female."""
    return Body.compose("bipedal_plantigrade", "human", "female")

def compose_elf_male() -> Body:
    """Male elf."""
    return Body.compose("bipedal_plantigrade", "elf", "male")

def compose_elf_female() -> Body:
    """Female elf."""
    return Body.compose("bipedal_plantigrade", "elf", "female")

def compose_wolf_anthro_male() -> Body:
    """Male anthro wolf (digitigrade) - canine genitals."""
    return Body.compose("bipedal_digitigrade", "wolf", "male")

def compose_wolf_anthro_female() -> Body:
    """Female anthro wolf (digitigrade) - canine genitals."""
    return Body.compose("bipedal_digitigrade", "wolf", "female")

def compose_wolf_feral() -> Body:
    """Feral wolf (quadruped) - canine genitals."""
    return Body.compose("quadruped", "wolf", "male")

def compose_cat_anthro_female() -> Body:
    """Female anthro cat - feline genitals."""
    return Body.compose("bipedal_digitigrade", "cat", "female")

def compose_horse_anthro_male() -> Body:
    """Male anthro horse - equine genitals."""
    return Body.compose("bipedal_plantigrade", "horse", "male")

def compose_centaur_male() -> Body:
    """Male centaur (tauroid) - equine genitals."""
    return Body.compose("tauroid", "horse", "male")

def compose_centaur_female() -> Body:
    """Female centaur - equine genitals."""
    return Body.compose("tauroid", "horse", "female")

def compose_lamia_female() -> Body:
    """Female lamia (serpentine) - reptile genitals."""
    return Body.compose("serpentine", "snake", "female")

def compose_mermaid() -> Body:
    """Female merfolk - aquatic genitals."""
    return Body.compose("aquatic", "fish", "female")

def compose_succubus() -> Body:
    """Female succubus - human genitals."""
    return Body.compose("bipedal_plantigrade", "succubus", "female")

def compose_herm_wolf() -> Body:
    """Hermaphrodite wolf anthro - canine genitals."""
    return Body.compose("bipedal_digitigrade", "wolf", "herm")

def compose_futa_human() -> Body:
    """Human futanari - human genitals."""
    return Body.compose("bipedal_plantigrade", "human", "futa")

def compose_femboy_fox() -> Body:
    """Femboy fox anthro - canine genitals."""
    return Body.compose("bipedal_digitigrade", "fox", "femboy")

def compose_futa_horse_human() -> Body:
    """Human futanari with horse cock."""
    return Body.compose("bipedal_plantigrade", "human", "futa", genital_override="equine")

def compose_dickgirl_cat() -> Body:
    """Dickgirl cat anthro - feline genitals."""
    return Body.compose("bipedal_digitigrade", "cat", "dickgirl")


# =============================================================================
# TODO: EXPANSION IDEAS
# =============================================================================

"""
TODO [BODY_TRANSFORMATION]: Implement transformation system
    - Werewolf transformation (human <-> wolf)
    - Partial transformations
    - Curse-based transformations
    - Potion/spell transformations
    - Track original body, transformed body
    - Gradual transformation stages
    - Transformation triggers (moon, emotion, command)

TODO [BODY_GROWTH]: Implement growth/shrink system
    - Part-specific size changes
    - Overall body size scaling
    - Temporary vs permanent
    - Growth limits per species
    - Effects on stats/abilities

TODO [BODY_MUTATION]: Implement mutation system
    - Random mutation generation
    - Beneficial vs harmful mutations
    - Mutation stacking
    - Cure/remove mutations
    - Mutation breeding/inheritance

TODO [BODY_PREGNANCY]: Implement pregnancy system
    - Conception tracking
    - Pregnancy stages/trimester
    - Birth mechanics
    - Hybrid offspring determination
    - Egg-laying for appropriate species
    - Multiple pregnancy support

TODO [BODY_AGING]: Implement aging system
    - Age categories (young, adult, elder)
    - Age effects on stats
    - Maturation for parts
    - Death from old age (optional)

TODO [BODY_CYBORG]: Implement cybernetic enhancement system
    - Cybernetic part types
    - Enhancement levels
    - Power requirements
    - EMP vulnerability
    - Rejection/compatibility

TODO [BODY_MAGICAL]: Implement magical body modifications
    - Enchanted parts
    - Magical tattoos with effects
    - Rune markings
    - Magical parasites/symbiotes
    - Soul-bound modifications

TODO [BODY_FLUIDS_ADVANCED]: Expand fluid system
    - Fluid production rates
    - Fluid storage (bladder, etc.)
    - Fluid effects (aphrodisiacs, etc.)
    - Custom fluid types
    - Fluid mixing/combination

TODO [BODY_SCENT]: Implement scent system
    - Species-specific scents
    - Arousal scent changes
    - Marking territory
    - Scent tracking
    - Scent masking/perfume

TODO [BODY_SOUNDS]: Implement body sound system
    - Species-specific vocalizations
    - Involuntary sounds (moans, growls)
    - Voice pitch/tone
    - Muting effects
    - Sound-based abilities

TODO [BODY_TEMPERATURE]: Implement body temperature system
    - Species body temp norms
    - Heat/cold effects
    - Fever from illness
    - Heat cycles
    - Thermal vision interaction

TODO [BODY_STAMINA]: Implement physical stamina system
    - Stamina pool
    - Recovery rates
    - Exhaustion effects
    - Species modifiers
    - Training improvements

TODO [BODY_FLEXIBILITY]: Implement flexibility/contortion system
    - Flexibility ratings
    - Contortion abilities
    - Position requirements
    - Training improvement
    - Species bonuses

TODO [BODY_STRENGTH]: Implement strength variation system
    - Part-specific strength
    - Grip strength
    - Carrying capacity
    - Species strength modifiers
    - Training effects

TODO [BODY_SENSITIVITY]: Implement sensitivity system
    - Part sensitivity levels
    - Erogenous zones
    - Pain sensitivity
    - Ticklishness
    - Desensitization over time

TODO [BODY_HEALING]: Implement advanced healing system
    - Natural healing rates
    - Scarring probability
    - Regeneration (for capable species)
    - Healing magic integration
    - Permanent damage tracking

TODO [BODY_EQUIPMENT_SLOTS]: Define equipment slot system
    - Which parts accept which equipment
    - Slot conflicts
    - Multi-slot items
    - Species-specific slots
    - Prosthetic equipment compatibility

TODO [BODY_DISPLAY_MODES]: Implement different description modes
    - Clinical/medical mode
    - Casual mode
    - Erotic mode
    - Combat/tactical mode
    - Builder/debug mode
"""
