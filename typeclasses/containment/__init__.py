"""
Containment System
==================

Focused implementation for cock vore (balls) and unbirthing (womb).
Provides immersive experience for both host and occupant.

Features:
- Bidirectional sensation (host feels occupant, occupant feels environment)
- Communication (muffled speech, movements felt)
- Trapping mechanics (plugs, clothing, muscle control)
- Flooding (cum/fluids filling the space)
- Pleasure/arousal tracking for both parties
- Entry experience (the journey in)
- Scent system

Based on FlexibleSurvival MUD style.
"""

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple, Callable
from enum import Enum
from datetime import datetime


# =============================================================================
# CONTAINMENT TYPES
# =============================================================================

class ContainmentType(Enum):
    """Types of containment supported."""
    COCK_VORE = "cock_vore"  # Absorbed through cock into balls
    UNBIRTH = "unbirth"      # Taken into womb through vagina


class EntryStage(Enum):
    """Stages of entry process."""
    OUTSIDE = "outside"       # Not yet entering
    TIP = "tip"               # Just the entrance
    PARTIAL = "partial"       # Partway in
    DEEP = "deep"             # Mostly inside
    CONTAINED = "contained"   # Fully inside


class ContainmentMood(Enum):
    """How the containment feels for occupant."""
    BLISSFUL = "blissful"
    PLEASURABLE = "pleasurable"
    COMFORTABLE = "comfortable"
    SNUG = "snug"
    CRAMPED = "cramped"
    OVERWHELMED = "overwhelmed"
    STRUGGLING = "struggling"


# =============================================================================
# TRAPPING MECHANICS
# =============================================================================

class TrapType(Enum):
    """Things that can trap occupants inside."""
    NONE = "none"
    PLUG = "plug"             # Cock plug or vaginal plug
    CLOTHING = "clothing"     # Tight underwear, chastity, etc.
    MUSCLE = "muscle"         # Voluntary muscle clenching
    KNOT = "knot"             # Knotted cock blocking exit
    INFLATION = "inflation"   # So full they can't fit through
    MAGIC = "magic"           # Magical binding


@dataclass
class Trap:
    """An active trap preventing exit."""
    trap_type: TrapType
    name: str = ""
    description: str = ""
    
    # How effective (0.0 = easily escaped, 1.0 = impossible)
    strength: float = 0.8
    
    # Can occupant remove it from inside?
    removable_from_inside: bool = False
    
    # Does it cause sensations?
    causes_pleasure: float = 0.0  # Per tick
    causes_pressure: float = 0.0
    
    def describe_from_inside(self) -> str:
        """How occupant perceives this trap."""
        if self.trap_type == TrapType.PLUG:
            return f"A {self.name} blocks the only way out, sealing you inside."
        elif self.trap_type == TrapType.CLOTHING:
            return f"Tight {self.name} presses against the exit, keeping you trapped."
        elif self.trap_type == TrapType.MUSCLE:
            return "Powerful muscles clench tight, refusing to let you leave."
        elif self.trap_type == TrapType.KNOT:
            return "A massive knot plugs the entrance, far too large to squeeze past."
        elif self.trap_type == TrapType.INFLATION:
            return "You're too big with all this fluid to fit back through."
        return "Something is keeping you trapped inside."
    
    def describe_from_outside(self) -> str:
        """How host perceives having this trap active."""
        if self.trap_type == TrapType.PLUG:
            return f"your {self.name} keeping them sealed in"
        elif self.trap_type == TrapType.CLOTHING:
            return f"your {self.name} pressing them deeper"
        elif self.trap_type == TrapType.MUSCLE:
            return "muscles clenched to hold them"
        elif self.trap_type == TrapType.KNOT:
            return "your knot plugging them in"
        return "something holding them inside"


# =============================================================================
# SENSATION SYSTEM
# =============================================================================

@dataclass
class Sensation:
    """A sensation felt by host or occupant."""
    description: str
    intensity: float = 1.0  # 0.0 - 10.0
    
    # Type of sensation
    is_pleasure: bool = False
    is_pressure: bool = False
    is_movement: bool = False
    is_warmth: bool = False
    is_wetness: bool = False
    
    # Source
    source: str = ""  # Who/what caused it
    
    def describe(self) -> str:
        """Get sensation description."""
        intensity_word = ""
        if self.intensity < 2:
            intensity_word = "faint"
        elif self.intensity < 4:
            intensity_word = "gentle"
        elif self.intensity < 6:
            intensity_word = "noticeable"
        elif self.intensity < 8:
            intensity_word = "intense"
        else:
            intensity_word = "overwhelming"
        
        return f"{intensity_word} {self.description}"


class SensationBuffer:
    """
    Collects sensations to be delivered to a character.
    Combines similar sensations, manages delivery.
    """
    
    def __init__(self):
        self.sensations: List[Sensation] = []
        self.messages: List[str] = []
    
    def add(self, sensation: Sensation):
        """Add a sensation."""
        self.sensations.append(sensation)
    
    def add_message(self, message: str):
        """Add a direct message."""
        self.messages.append(message)
    
    def get_combined_description(self) -> str:
        """Get combined description of all sensations."""
        if not self.sensations:
            return ""
        
        # Group by type
        pleasure = [s for s in self.sensations if s.is_pleasure]
        movement = [s for s in self.sensations if s.is_movement]
        other = [s for s in self.sensations if not s.is_pleasure and not s.is_movement]
        
        parts = []
        
        if movement:
            avg_intensity = sum(s.intensity for s in movement) / len(movement)
            if avg_intensity < 3:
                parts.append("subtle movements")
            elif avg_intensity < 6:
                parts.append("squirming and shifting")
            else:
                parts.append("vigorous struggling")
        
        if pleasure:
            total = sum(s.intensity for s in pleasure)
            if total < 5:
                parts.append("pleasant sensations")
            elif total < 15:
                parts.append("waves of pleasure")
            else:
                parts.append("intense pleasure")
        
        for s in other[:3]:  # Limit to 3 other sensations
            parts.append(s.describe())
        
        return ", ".join(parts) if parts else ""
    
    def clear(self):
        """Clear all buffered sensations."""
        self.sensations.clear()
        self.messages.clear()


# =============================================================================
# OCCUPANT STATE
# =============================================================================

@dataclass
class Occupant:
    """
    Someone contained inside a host.
    """
    # Identity
    character_dbref: str
    character_name: str
    
    # Physical
    scale: float = 1.0  # Size relative to normal
    
    # Position in containment
    entry_stage: EntryStage = EntryStage.CONTAINED
    
    # Current state
    mood: ContainmentMood = ContainmentMood.COMFORTABLE
    
    # Arousal/pleasure tracking
    arousal: float = 0.0  # 0-100
    pleasure_accumulated: float = 0.0
    orgasm_count: int = 0
    
    # Physical state
    is_struggling: bool = False
    struggle_energy: float = 100.0
    escape_progress: float = 0.0
    
    # Fluid exposure
    fluid_exposure_ml: float = 0.0  # How much fluid they're in
    is_submerged: bool = False      # Fully underwater in fluid
    
    # Communication
    can_speak: bool = True  # Can they talk (muffled)
    can_move: bool = True   # Can they move around
    
    # Time tracking
    entered_at: Optional[datetime] = None
    ticks_inside: int = 0
    
    # Scent
    has_absorbed_scent: bool = False
    scent_strength: float = 0.0  # How strongly they smell like host
    
    # Sensation buffer (to deliver to this occupant)
    sensations: SensationBuffer = field(default_factory=SensationBuffer)
    
    def __post_init__(self):
        if not self.entered_at:
            self.entered_at = datetime.now()
    
    def add_arousal(self, amount: float):
        """Add arousal, handle orgasm at 100."""
        self.arousal = min(100, self.arousal + amount)
        self.pleasure_accumulated += max(0, amount)
        
        if self.arousal >= 100:
            self.orgasm()
    
    def orgasm(self):
        """Process orgasm."""
        self.orgasm_count += 1
        self.arousal = 20  # Reset but stay aroused
        self.sensations.add_message("Pleasure overwhelms you as you cum!")
    
    def absorb_scent(self, amount: float = 0.1):
        """Absorb more of the host's scent."""
        self.scent_strength = min(1.0, self.scent_strength + amount)
        if self.scent_strength > 0.3:
            self.has_absorbed_scent = True
    
    def struggle(self) -> Tuple[bool, float, str]:
        """
        Attempt to struggle.
        Returns (success, sensation_for_host, message).
        """
        if self.struggle_energy <= 0:
            return (False, 0, "You're too exhausted to struggle.")
        
        self.is_struggling = True
        self.struggle_energy -= 10
        
        # Struggling causes sensations for host
        host_sensation = 2.0 + (self.scale * 2)
        
        # And arousal for occupant (being squeezed)
        self.add_arousal(1.0)
        
        # Calculate escape progress
        progress = 5.0 / self.scale  # Smaller = easier to escape
        self.escape_progress += progress
        
        if self.escape_progress >= 100:
            return (True, host_sensation, "With a final push, you squeeze toward freedom!")
        
        return (True, host_sensation, f"You squirm and push against the walls. ({self.escape_progress:.0f}%)")
    
    def relax(self):
        """Stop struggling, recover energy."""
        self.is_struggling = False
        self.struggle_energy = min(100, self.struggle_energy + 5)
    
    def tick(self, environment: dict) -> Dict:
        """
        Process one tick of being contained.
        
        Args:
            environment: Dict with 'fluid_level', 'temperature', 'tightness', etc.
        
        Returns dict of effects/events.
        """
        self.ticks_inside += 1
        result = {
            "arousal_gained": 0.0,
            "host_sensation": 0.0,
            "messages": [],
        }
        
        # Base arousal from being contained
        base_arousal = 0.5
        
        # Tightness increases arousal
        tightness = environment.get("tightness", 0.5)
        base_arousal += tightness * 0.5
        
        # Fluid exposure
        fluid = environment.get("fluid_level", 0)
        if fluid > 0:
            self.fluid_exposure_ml = fluid
            # Being in warm fluid is arousing
            base_arousal += min(2.0, fluid / 100)
            
            if fluid > 500:
                self.is_submerged = True
                base_arousal += 1.0
        
        # Movement causes host sensation
        if self.is_struggling:
            result["host_sensation"] += 2.0 * self.scale
        else:
            # Even idle occupants shift around
            result["host_sensation"] += 0.5 * self.scale
        
        # Apply arousal
        self.add_arousal(base_arousal)
        result["arousal_gained"] = base_arousal
        
        # Absorb scent over time
        self.absorb_scent(0.02)
        
        # Update mood based on conditions
        self._update_mood(environment)
        
        # Recover struggle energy when not struggling
        if not self.is_struggling:
            self.relax()
        
        return result
    
    def _update_mood(self, environment: dict):
        """Update mood based on current conditions."""
        tightness = environment.get("tightness", 0.5)
        fluid = environment.get("fluid_level", 0)
        
        if self.arousal > 80:
            self.mood = ContainmentMood.OVERWHELMED
        elif self.is_struggling:
            self.mood = ContainmentMood.STRUGGLING
        elif tightness > 0.8:
            self.mood = ContainmentMood.CRAMPED
        elif self.arousal > 50 or fluid > 200:
            self.mood = ContainmentMood.PLEASURABLE
        elif tightness < 0.3:
            self.mood = ContainmentMood.COMFORTABLE
        else:
            self.mood = ContainmentMood.SNUG
    
    def describe_state(self) -> str:
        """Get description of current state for the occupant."""
        parts = []
        
        # Mood
        mood_desc = {
            ContainmentMood.BLISSFUL: "lost in bliss",
            ContainmentMood.PLEASURABLE: "waves of pleasure washing over you",
            ContainmentMood.COMFORTABLE: "comfortable despite the tight confines",
            ContainmentMood.SNUG: "held snugly by the walls",
            ContainmentMood.CRAMPED: "cramped in the tight space",
            ContainmentMood.OVERWHELMED: "overwhelmed by sensation",
            ContainmentMood.STRUGGLING: "struggling against your confines",
        }
        parts.append(f"You are {mood_desc.get(self.mood, 'contained')}.")
        
        # Fluid
        if self.is_submerged:
            parts.append("Warm fluid surrounds you completely, filling the space.")
        elif self.fluid_exposure_ml > 100:
            parts.append("Warm fluid pools around you, rising steadily.")
        elif self.fluid_exposure_ml > 0:
            parts.append("A slick layer of fluid coats your skin.")
        
        # Arousal
        if self.arousal > 80:
            parts.append("Your body trembles on the edge of release.")
        elif self.arousal > 50:
            parts.append("Arousal burns through you.")
        elif self.arousal > 20:
            parts.append("A warm arousal builds within you.")
        
        return " ".join(parts)


# =============================================================================
# INTERIOR SPACE
# =============================================================================

@dataclass
class InteriorSpace:
    """
    The interior environment (womb or balls).
    """
    # Type
    containment_type: ContainmentType
    
    # Owner
    host_dbref: str = ""
    host_name: str = ""
    host_scale: float = 1.0
    
    # Capacity (scales with host)
    base_capacity: float = 100.0  # "body units"
    stretch: float = 1.0
    max_stretch: float = 50.0
    elasticity: float = 5.0
    
    # Current occupants
    occupants: List[Occupant] = field(default_factory=list)
    
    # Fluid inside
    fluid_ml: float = 0.0
    fluid_type: str = "cum"  # cum, femcum, etc.
    fluid_production_rate: float = 0.0  # ml per tick
    
    # Active traps
    traps: List[Trap] = field(default_factory=list)
    
    # Muscle control
    is_clenching: bool = False
    clench_strength: float = 0.5
    
    # Environment
    temperature: float = 1.0  # 1.0 = body temp
    
    # Description templates
    desc_empty: str = ""
    desc_occupied: str = ""
    walls_desc: str = ""
    ambient_sounds: str = ""
    ambient_scent: str = ""
    
    # Sensation buffer (to deliver to host)
    host_sensations: SensationBuffer = field(default_factory=SensationBuffer)
    
    # Room reference (if using Evennia rooms)
    interior_room_dbref: str = ""
    
    def __post_init__(self):
        self._setup_descriptions()
    
    def _setup_descriptions(self):
        """Set up descriptions based on type."""
        if self.containment_type == ContainmentType.COCK_VORE:
            self.desc_empty = (
                "The warm, churning interior of massive balls surrounds you. "
                "The walls pulse rhythmically, thick and muscular. "
                "The air is heavy with musk, and pools of cum slosh beneath you."
            )
            self.desc_occupied = (
                "You're held within the churning confines of a massive ballsack. "
                "The walls squeeze and relax around you in a steady rhythm. "
                "Warm cum pools around you, steadily rising."
            )
            self.walls_desc = "the thick, muscular walls of the balls"
            self.ambient_sounds = "constant churning and your host's heartbeat"
            self.ambient_scent = "overwhelming musk and the thick scent of cum"
            self.fluid_type = "cum"
            
        elif self.containment_type == ContainmentType.UNBIRTH:
            self.desc_empty = (
                "The soft, wet walls of the womb surround you in warmth. "
                "Everything pulses with a gentle heartbeat. "
                "The space is dark and intimate, flesh pressing close."
            )
            self.desc_occupied = (
                "You're cradled within the warm embrace of a womb. "
                "Soft walls pulse around you, holding you close. "
                "The rhythmic heartbeat fills your awareness."
            )
            self.walls_desc = "the soft, pulsing walls of the womb"
            self.ambient_sounds = "the steady heartbeat and quiet wet sounds"
            self.ambient_scent = "intimate feminine musk"
            self.fluid_type = "femcum"
    
    @property
    def capacity(self) -> float:
        """Current capacity with stretch."""
        return self.base_capacity * (self.host_scale ** 3) * self.stretch
    
    @property
    def total_occupant_size(self) -> float:
        """Combined size of all occupants."""
        return sum(o.scale for o in self.occupants) * 100
    
    @property
    def fill_percent(self) -> float:
        """How full with occupants (not fluid)."""
        if self.capacity <= 0:
            return 0
        return (self.total_occupant_size / self.capacity) * 100
    
    @property
    def tightness(self) -> float:
        """How tight it feels (0-1)."""
        base = self.fill_percent / 100
        if self.is_clenching:
            base += self.clench_strength * 0.5
        return min(1.0, base)
    
    @property
    def is_empty(self) -> bool:
        return len(self.occupants) == 0
    
    @property
    def is_trapped(self) -> bool:
        """Is exit blocked?"""
        return len(self.traps) > 0 or self.is_clenching
    
    def can_fit(self, prey_scale: float) -> Tuple[bool, str]:
        """Check if something can fit inside."""
        needed = prey_scale * 100
        available = self.capacity - self.total_occupant_size
        
        if needed <= available:
            return (True, "There's room.")
        elif needed <= available * self.elasticity:
            # Can stretch
            return (True, "It'll be a tight squeeze...")
        else:
            return (False, "There's not enough room.")
    
    def add_occupant(self, 
                     char_dbref: str, 
                     char_name: str, 
                     scale: float = 1.0) -> Occupant:
        """Add an occupant."""
        occupant = Occupant(
            character_dbref=char_dbref,
            character_name=char_name,
            scale=scale,
        )
        self.occupants.append(occupant)
        
        # Stretch to accommodate
        needed = (self.total_occupant_size) / (self.base_capacity * (self.host_scale ** 3))
        if needed > self.stretch:
            self.stretch = min(self.max_stretch, needed)
        
        # Host feels them enter
        self.host_sensations.add(Sensation(
            description=f"{char_name} settling inside",
            intensity=3.0 + scale * 2,
            is_pressure=True,
            is_pleasure=True,
            source=char_dbref,
        ))
        
        return occupant
    
    def remove_occupant(self, char_dbref: str) -> Optional[Occupant]:
        """Remove an occupant."""
        for i, o in enumerate(self.occupants):
            if o.character_dbref == char_dbref:
                removed = self.occupants.pop(i)
                
                # Host feels them leave
                self.host_sensations.add(Sensation(
                    description=f"{removed.character_name} sliding out",
                    intensity=4.0 + removed.scale * 2,
                    is_movement=True,
                    is_pleasure=True,
                    source=char_dbref,
                ))
                
                return removed
        return None
    
    def get_occupant(self, char_dbref: str) -> Optional[Occupant]:
        """Get occupant by dbref."""
        for o in self.occupants:
            if o.character_dbref == char_dbref:
                return o
        return None
    
    def add_trap(self, trap: Trap):
        """Add a trap."""
        self.traps.append(trap)
        
        # Notify occupants
        for o in self.occupants:
            o.sensations.add_message(trap.describe_from_inside())
    
    def remove_trap(self, trap_type: TrapType) -> bool:
        """Remove a trap by type."""
        for i, t in enumerate(self.traps):
            if t.trap_type == trap_type:
                self.traps.pop(i)
                return True
        return False
    
    def clench(self, strength: float = 0.5):
        """Clench muscles to hold occupants."""
        self.is_clenching = True
        self.clench_strength = strength
        
        # Occupants feel it
        for o in self.occupants:
            o.sensations.add(Sensation(
                description="walls squeezing tight around you",
                intensity=3.0 + strength * 3,
                is_pressure=True,
                is_pleasure=True,
            ))
            o.add_arousal(strength * 2)
    
    def relax_clench(self):
        """Stop clenching."""
        self.is_clenching = False
        self.clench_strength = 0
    
    def add_fluid(self, amount_ml: float, source_name: str = ""):
        """Add fluid to the interior."""
        self.fluid_ml += amount_ml
        
        # Notify occupants
        for o in self.occupants:
            if amount_ml > 50:
                o.sensations.add_message(
                    f"Warm {self.fluid_type} floods in around you!"
                )
            elif amount_ml > 10:
                o.sensations.add_message(
                    f"More {self.fluid_type} flows in, the level rising."
                )
            
            # Being flooded is arousing
            o.add_arousal(amount_ml / 50)
    
    def can_escape(self, occupant: Occupant) -> Tuple[bool, str]:
        """Check if occupant can escape."""
        if self.is_clenching:
            return (False, "Powerful muscles hold you in place.")
        
        for trap in self.traps:
            if trap.strength > 0.5:
                return (False, trap.describe_from_inside())
        
        if occupant.escape_progress < 100:
            return (False, "You haven't worked your way to the exit yet.")
        
        return (True, "The way out is clear!")
    
    def tick(self) -> Dict:
        """
        Process one tick.
        Returns events/effects.
        """
        result = {
            "host_arousal": 0.0,
            "host_messages": [],
            "occupant_results": {},
        }
        
        # Natural fluid production
        if self.fluid_production_rate > 0:
            self.add_fluid(self.fluid_production_rate)
        
        # Build environment for occupants
        environment = {
            "tightness": self.tightness,
            "fluid_level": self.fluid_ml,
            "temperature": self.temperature,
        }
        
        # Process each occupant
        total_host_sensation = 0.0
        for occupant in self.occupants:
            occ_result = occupant.tick(environment)
            result["occupant_results"][occupant.character_dbref] = occ_result
            total_host_sensation += occ_result.get("host_sensation", 0)
            
            # Trap effects
            for trap in self.traps:
                if trap.causes_pleasure > 0:
                    occupant.add_arousal(trap.causes_pleasure)
        
        # Host feels occupants
        if total_host_sensation > 0:
            self.host_sensations.add(Sensation(
                description="movement inside",
                intensity=total_host_sensation,
                is_movement=True,
                is_pleasure=total_host_sensation > 2,
            ))
            result["host_arousal"] = total_host_sensation * 0.5
        
        return result
    
    def get_interior_description(self, viewer_dbref: str = "") -> str:
        """Get the room description for occupants."""
        if self.is_empty:
            desc = self.desc_empty
        else:
            desc = self.desc_occupied
        
        parts = [desc]
        
        # Fluid level
        if self.fluid_ml > 500:
            parts.append(
                f"You're nearly submerged in warm {self.fluid_type}, "
                f"the thick fluid filling most of the space."
            )
        elif self.fluid_ml > 100:
            parts.append(
                f"Warm {self.fluid_type} pools around you, "
                f"sloshing with every movement."
            )
        elif self.fluid_ml > 10:
            parts.append(f"A slick layer of {self.fluid_type} coats everything.")
        
        # Tightness
        if self.tightness > 0.8:
            parts.append("The walls press tight against you, barely leaving room to breathe.")
        elif self.tightness > 0.5:
            parts.append("The walls press snugly around you.")
        
        # Traps
        for trap in self.traps:
            parts.append(trap.describe_from_inside())
        
        # Other occupants
        others = [o for o in self.occupants if o.character_dbref != viewer_dbref]
        if others:
            names = [o.character_name for o in others]
            parts.append(f"You share this space with: {', '.join(names)}")
        
        # Ambient
        parts.append(f"\nYou can hear {self.ambient_sounds}.")
        parts.append(f"The scent of {self.ambient_scent} fills your awareness.")
        
        return "\n\n".join(parts)
    
    def describe_from_outside(self) -> str:
        """Describe what host sees/feels."""
        if self.is_empty:
            return ""
        
        location = "balls" if self.containment_type == ContainmentType.COCK_VORE else "womb"
        
        # Size description
        fill = self.fill_percent
        if fill < 20:
            size_desc = "a subtle bulge"
        elif fill < 50:
            size_desc = "a noticeable bulge"
        elif fill < 80:
            size_desc = "a large, obvious bulge"
        elif fill < 120:
            size_desc = "a massive, taut bulge"
        else:
            size_desc = "an enormous, straining bulge"
        
        names = [o.character_name for o in self.occupants]
        occupant_str = ", ".join(names)
        
        parts = [f"{size_desc} in your {location} from {occupant_str}"]
        
        # Activity
        struggling = [o for o in self.occupants if o.is_struggling]
        if struggling:
            parts.append("you can feel them squirming inside")
        
        # Traps
        for trap in self.traps:
            parts.append(trap.describe_from_outside())
        
        return "; ".join(parts)


# =============================================================================
# ENTRY EXPERIENCE
# =============================================================================

@dataclass
class EntrySequence:
    """
    Manages the experience of entering a host.
    """
    # Participants
    prey_dbref: str
    prey_name: str
    prey_scale: float
    
    host_dbref: str
    host_name: str
    
    # Type
    containment_type: ContainmentType
    
    # Progress
    current_stage: EntryStage = EntryStage.OUTSIDE
    progress: float = 0.0  # 0-100 within current stage
    
    # Is entry consensual/willing?
    is_willing: bool = True
    
    # Arousal generated during entry
    prey_arousal: float = 0.0
    host_arousal: float = 0.0
    
    def get_stage_description_prey(self) -> str:
        """What prey experiences at current stage."""
        if self.containment_type == ContainmentType.COCK_VORE:
            descs = {
                EntryStage.OUTSIDE: f"You face the massive cock before you, its slit gaping hungrily.",
                EntryStage.TIP: "The cockhead engulfs your head, hot flesh stretching around you. Musk overwhelms your senses.",
                EntryStage.PARTIAL: "You slide deeper into the shaft, tight walls rippling around you, pulling you inward.",
                EntryStage.DEEP: "The shaft squeezes you along, your body distending the cock obscenely. You can feel the balls below.",
                EntryStage.CONTAINED: "With a final squeeze, you slip into the churning balls, warm cum enveloping you.",
            }
        else:  # UNBIRTH
            descs = {
                EntryStage.OUTSIDE: f"The wet pussy spreads before you, inviting you inside.",
                EntryStage.TIP: "Your head pushes past the outer lips, surrounded by warm, wet flesh.",
                EntryStage.PARTIAL: "You slide deeper, the vaginal walls squeezing and pulling you inward.",
                EntryStage.DEEP: "You're deep inside now, pressing against the cervix. It slowly dilates for you.",
                EntryStage.CONTAINED: "You slip through the cervix into the womb, cradled in its soft embrace.",
            }
        return descs.get(self.current_stage, "")
    
    def get_stage_description_host(self) -> str:
        """What host experiences at current stage."""
        name = self.prey_name
        if self.containment_type == ContainmentType.COCK_VORE:
            descs = {
                EntryStage.OUTSIDE: f"{name} presses against your cock.",
                EntryStage.TIP: f"Your cock stretches around {name}'s head, engulfing them.",
                EntryStage.PARTIAL: f"{name} slides deeper into your shaft, the bulge traveling down.",
                EntryStage.DEEP: f"{name} is almost there, stretching your cock wonderfully as they descend.",
                EntryStage.CONTAINED: f"With a satisfying *schlorp*, {name} slips into your balls.",
            }
        else:
            descs = {
                EntryStage.OUTSIDE: f"{name} presses against your entrance.",
                EntryStage.TIP: f"Your lips spread around {name}, taking them in.",
                EntryStage.PARTIAL: f"{name} slides deeper inside you, stretching you pleasurably.",
                EntryStage.DEEP: f"{name} presses against your cervix, about to enter your womb.",
                EntryStage.CONTAINED: f"{name} slips through into your womb, settling inside you.",
            }
        return descs.get(self.current_stage, "")
    
    def advance(self, amount: float = 25.0) -> Tuple[bool, str, str]:
        """
        Advance the entry.
        Returns (stage_changed, prey_message, host_message).
        """
        self.progress += amount
        
        stages = [
            EntryStage.OUTSIDE,
            EntryStage.TIP,
            EntryStage.PARTIAL,
            EntryStage.DEEP,
            EntryStage.CONTAINED,
        ]
        current_idx = stages.index(self.current_stage)
        
        if self.progress >= 100 and current_idx < len(stages) - 1:
            # Move to next stage
            self.progress = 0
            self.current_stage = stages[current_idx + 1]
            
            # Arousal for stage transition
            self.prey_arousal += 10.0
            self.host_arousal += 10.0 * self.prey_scale
            
            return (
                True,
                self.get_stage_description_prey(),
                self.get_stage_description_host(),
            )
        
        # No stage change, but arousal builds
        self.prey_arousal += 2.0
        self.host_arousal += 2.0 * self.prey_scale
        
        return (False, "", "")
    
    @property
    def is_complete(self) -> bool:
        return self.current_stage == EntryStage.CONTAINED


# =============================================================================
# SCENT SYSTEM
# =============================================================================

@dataclass
class ScentMark:
    """A scent mark on a character."""
    scent_type: str  # "musk", "cum", "feminine", etc.
    source_dbref: str
    source_name: str
    
    # Strength 0-1
    strength: float = 0.5
    
    # Location on body
    location: str = "body"  # "body", "groin", "face", etc.
    
    # Decay
    fade_rate: float = 0.01  # Per tick
    
    def tick(self) -> bool:
        """Process decay. Returns True if should be removed."""
        self.strength -= self.fade_rate
        return self.strength <= 0
    
    def describe(self) -> str:
        """Get description of this scent."""
        if self.strength > 0.8:
            intensity = "strongly"
        elif self.strength > 0.5:
            intensity = "noticeably"
        elif self.strength > 0.2:
            intensity = "faintly"
        else:
            intensity = "barely"
        
        return f"{intensity} smells of {self.source_name}'s {self.scent_type}"


@dataclass
class ScentProfile:
    """
    Tracks scent marks on a character.
    """
    # This character's natural scent
    natural_scent: str = "neutral"
    
    # Acquired scent marks
    marks: List[ScentMark] = field(default_factory=list)
    
    def add_mark(self, 
                 scent_type: str,
                 source_dbref: str,
                 source_name: str,
                 strength: float = 0.5,
                 location: str = "body"):
        """Add a scent mark."""
        # Check for existing mark from same source
        for mark in self.marks:
            if mark.source_dbref == source_dbref and mark.location == location:
                # Strengthen existing
                mark.strength = min(1.0, mark.strength + strength)
                return
        
        self.marks.append(ScentMark(
            scent_type=scent_type,
            source_dbref=source_dbref,
            source_name=source_name,
            strength=strength,
            location=location,
        ))
    
    def tick(self):
        """Process scent decay."""
        self.marks = [m for m in self.marks if not m.tick()]
    
    def get_dominant_scent(self) -> Optional[ScentMark]:
        """Get the strongest scent mark."""
        if not self.marks:
            return None
        return max(self.marks, key=lambda m: m.strength)
    
    def describe(self) -> str:
        """Get overall scent description."""
        if not self.marks:
            return f"smells of {self.natural_scent}"
        
        # Sort by strength
        sorted_marks = sorted(self.marks, key=lambda m: m.strength, reverse=True)
        
        descriptions = [m.describe() for m in sorted_marks[:3]]
        return "; ".join(descriptions)
    
    def smells_like(self, source_dbref: str) -> bool:
        """Check if this character smells like another."""
        for mark in self.marks:
            if mark.source_dbref == source_dbref and mark.strength > 0.3:
                return True
        return False


# =============================================================================
# CONTAINMENT MANAGER
# =============================================================================

@dataclass
class ContainmentManager:
    """
    Manages containment capabilities for a character (as host).
    """
    # Owner
    host_dbref: str = ""
    host_name: str = ""
    host_scale: float = 1.0
    
    # Available spaces
    balls: Optional[InteriorSpace] = None
    womb: Optional[InteriorSpace] = None
    
    # Host's scent profile
    scent_profile: Optional[ScentProfile] = None
    
    # Host arousal tracking
    arousal: float = 0.0
    
    def __post_init__(self):
        if self.scent_profile is None:
            self.scent_profile = ScentProfile()
    
    def enable_cock_vore(self, 
                         base_capacity: float = 100.0,
                         cum_production: float = 1.0):
        """Enable cock vore capability."""
        self.balls = InteriorSpace(
            containment_type=ContainmentType.COCK_VORE,
            host_dbref=self.host_dbref,
            host_name=self.host_name,
            host_scale=self.host_scale,
            base_capacity=base_capacity,
            fluid_production_rate=cum_production,
        )
    
    def enable_unbirth(self, base_capacity: float = 100.0):
        """Enable unbirth capability."""
        self.womb = InteriorSpace(
            containment_type=ContainmentType.UNBIRTH,
            host_dbref=self.host_dbref,
            host_name=self.host_name,
            host_scale=self.host_scale,
            base_capacity=base_capacity,
        )
    
    def get_space(self, ctype: ContainmentType) -> Optional[InteriorSpace]:
        """Get interior space by type."""
        if ctype == ContainmentType.COCK_VORE:
            return self.balls
        elif ctype == ContainmentType.UNBIRTH:
            return self.womb
        return None
    
    def start_entry(self,
                    ctype: ContainmentType,
                    prey_dbref: str,
                    prey_name: str,
                    prey_scale: float = 1.0,
                    willing: bool = True) -> Tuple[bool, str, Optional[EntrySequence]]:
        """
        Start the entry process.
        Returns (success, message, entry_sequence).
        """
        space = self.get_space(ctype)
        if not space:
            type_name = "cock vore" if ctype == ContainmentType.COCK_VORE else "unbirthing"
            return (False, f"Can't perform {type_name}.", None)
        
        can_fit, msg = space.can_fit(prey_scale)
        if not can_fit:
            return (False, msg, None)
        
        entry = EntrySequence(
            prey_dbref=prey_dbref,
            prey_name=prey_name,
            prey_scale=prey_scale,
            host_dbref=self.host_dbref,
            host_name=self.host_name,
            containment_type=ctype,
            is_willing=willing,
        )
        
        return (True, "Entry begins...", entry)
    
    def complete_entry(self, entry: EntrySequence) -> Occupant:
        """Complete entry, adding occupant to interior."""
        space = self.get_space(entry.containment_type)
        occupant = space.add_occupant(
            entry.prey_dbref,
            entry.prey_name,
            entry.prey_scale,
        )
        
        # Mark prey with host's scent
        scent_type = "musk" if entry.containment_type == ContainmentType.COCK_VORE else "feminine musk"
        occupant.absorb_scent(0.5)  # Immediate strong scent from entry
        
        return occupant
    
    def release(self, 
                char_dbref: str,
                method: str = "normal") -> Tuple[bool, str, Optional[Occupant]]:
        """
        Release an occupant.
        method: "normal", "force", "cum", "birth"
        Returns (success, message, released_occupant).
        """
        # Find them
        for space in [self.balls, self.womb]:
            if space is None:
                continue
            
            occupant = space.get_occupant(char_dbref)
            if occupant:
                # Check if can escape (unless forcing)
                if method not in ("force", "cum", "birth"):
                    can_escape, reason = space.can_escape(occupant)
                    if not can_escape:
                        return (False, reason, None)
                
                removed = space.remove_occupant(char_dbref)
                
                # Determine release message
                if space.containment_type == ContainmentType.COCK_VORE:
                    if method == "cum":
                        msg = f"{self.host_name} cums out {removed.character_name} in a flood of cum!"
                    else:
                        msg = f"{removed.character_name} slides out of {self.host_name}'s cock."
                else:
                    if method == "birth":
                        msg = f"{self.host_name} births {removed.character_name} from their womb."
                    else:
                        msg = f"{removed.character_name} slides out of {self.host_name}'s pussy."
                
                return (True, msg, removed)
        
        return (False, "They're not inside you.", None)
    
    def add_trap(self, ctype: ContainmentType, trap: Trap) -> bool:
        """Add a trap to a space."""
        space = self.get_space(ctype)
        if space:
            space.add_trap(trap)
            return True
        return False
    
    def clench(self, ctype: ContainmentType, strength: float = 0.5):
        """Clench muscles in a space."""
        space = self.get_space(ctype)
        if space:
            space.clench(strength)
    
    def release_clench(self, ctype: ContainmentType):
        """Release muscle clench."""
        space = self.get_space(ctype)
        if space:
            space.relax_clench()
    
    def flood(self, ctype: ContainmentType, amount_ml: float):
        """Add fluid to a space."""
        space = self.get_space(ctype)
        if space:
            space.add_fluid(amount_ml)
            
            # Also arousing for host
            self.arousal = min(100, self.arousal + amount_ml / 100)
    
    def tick(self) -> Dict:
        """Process one tick for all spaces."""
        result = {
            "balls": None,
            "womb": None,
            "host_arousal_gained": 0.0,
        }
        
        for name, space in [("balls", self.balls), ("womb", self.womb)]:
            if space is None:
                continue
            
            space_result = space.tick()
            result[name] = space_result
            result["host_arousal_gained"] += space_result.get("host_arousal", 0)
        
        self.arousal = min(100, self.arousal + result["host_arousal_gained"])
        
        return result
    
    def get_all_occupants(self) -> List[Occupant]:
        """Get all occupants across all spaces."""
        result = []
        if self.balls:
            result.extend(self.balls.occupants)
        if self.womb:
            result.extend(self.womb.occupants)
        return result
    
    def describe_bulges(self) -> str:
        """Get description of all visible bulges."""
        parts = []
        if self.balls and not self.balls.is_empty:
            parts.append(self.balls.describe_from_outside())
        if self.womb and not self.womb.is_empty:
            parts.append(self.womb.describe_from_outside())
        return "; ".join(parts) if parts else ""
    
    def get_stats(self) -> Dict:
        """Get stats for debugging/display."""
        stats = {
            "host": self.host_name,
            "arousal": self.arousal,
        }
        
        if self.balls:
            stats["balls"] = {
                "occupants": [o.character_name for o in self.balls.occupants],
                "fill_percent": self.balls.fill_percent,
                "fluid_ml": self.balls.fluid_ml,
                "trapped": self.balls.is_trapped,
            }
        
        if self.womb:
            stats["womb"] = {
                "occupants": [o.character_name for o in self.womb.occupants],
                "fill_percent": self.womb.fill_percent,
                "fluid_ml": self.womb.fluid_ml,
                "trapped": self.womb.is_trapped,
            }
        
        return stats


__all__ = [
    # Types
    "ContainmentType",
    "EntryStage",
    "ContainmentMood",
    "TrapType",
    
    # Classes
    "Trap",
    "Sensation",
    "SensationBuffer",
    "Occupant",
    "InteriorSpace",
    "EntrySequence",
    "ScentMark",
    "ScentProfile",
    "ContainmentManager",
]
