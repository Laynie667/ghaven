"""
Furniture - Machines

Mechanical furniture: sybians, fucking machines, milking stations.
These have active components that do things to occupants.

Inheritance:
    Furniture
    └── Machine
        ├── Sybian
        │   ├── StandardSybian
        │   └── DualSybian
        ├── FuckingMachine
        │   ├── PistonMachine
        │   ├── RotatingMachine
        │   └── TentacleMachine
        ├── MilkingStation
        │   ├── BreastPumps
        │   └── CockMilker
        └── VibrationPlatform
            ├── VibratingChair
            └── VibratingBed

MECHANICS:
    Machines have:
    - Power state (off, low, medium, high, max)
    - Attachments (dildos, pumps, probes)
    - Automatic arousal buildup
    - Timer-based operation
    - Integration with sexual_tick.py
"""

from dataclasses import dataclass, field
from typing import Dict, Set, Optional, List, Tuple, TYPE_CHECKING
from enum import Enum, auto

from .base import (
    Furniture,
    FurnitureType,
    FurnitureState,
    FurnitureSlot,
    OccupantPosition,
    Occupant,
)

if TYPE_CHECKING:
    from evennia.objects.objects import DefaultCharacter


# =============================================================================
# MACHINE ENUMS
# =============================================================================

class PowerLevel(Enum):
    """Power levels for machines."""
    OFF = "off"
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    MAX = "max"
    
    @property
    def intensity(self) -> float:
        """Get intensity multiplier."""
        return {
            PowerLevel.OFF: 0.0,
            PowerLevel.LOW: 0.25,
            PowerLevel.MEDIUM: 0.5,
            PowerLevel.HIGH: 0.75,
            PowerLevel.MAX: 1.0,
        }[self]


class AttachmentType(Enum):
    """Types of machine attachments."""
    NONE = "none"
    DILDO_SMALL = "small dildo"
    DILDO_MEDIUM = "medium dildo"
    DILDO_LARGE = "large dildo"
    DILDO_HUGE = "huge dildo"
    DILDO_RIBBED = "ribbed dildo"
    DILDO_KNOTTED = "knotted dildo"
    DILDO_DOUBLE = "double dildo"
    VIBRATOR = "vibrator"
    PROBE = "probe"
    SUCTION_CUP = "suction cup"
    PUMP = "pump"
    SLEEVE = "sleeve"
    TENTACLE = "tentacle"


@dataclass
class MachineAttachment:
    """An attachment on a machine."""
    attachment_type: AttachmentType
    target_zone: str  # Which body zone this targets
    size: float = 1.0  # Size multiplier
    texture: str = "smooth"  # smooth, ribbed, bumpy, etc.
    is_active: bool = True


# =============================================================================
# MACHINE BASE
# =============================================================================

class Machine(Furniture):
    """
    Base class for mechanical furniture.
    
    Machines can:
    - Be turned on/off
    - Have variable power levels
    - Have attachments
    - Automatically affect occupants over time
    - Integrate with the sexual tick system
    """
    
    def at_object_creation(self):
        super().at_object_creation()
        self.db.furniture_type = FurnitureType.FUCKING_MACHINE
        self.db.position_tags = {"machine", "mechanical"}
        
        # Power
        self.db.power_level = PowerLevel.OFF
        self.db.power_locked = False  # Can occupant change power?
        
        # Attachments
        self.db.attachments = []  # List of MachineAttachment
        
        # Arousal generation
        self.db.base_arousal_rate = 5.0  # Per tick at max power
        self.db.orgasm_enabled = True  # Can force orgasms
        self.db.edging_mode = False  # Stop just before orgasm
        
        # Timer
        self.db.timer_duration = 0  # 0 = indefinite
        self.db.timer_remaining = 0
        
        # Counters
        self.db.forced_orgasms = 0
    
    # -------------------------------------------------------------------------
    # POWER CONTROL
    # -------------------------------------------------------------------------
    
    def set_power(self, level: PowerLevel) -> str:
        """Set the power level."""
        if self.db.power_locked:
            return "The power controls are locked."
        
        old_level = self.db.power_level
        self.db.power_level = level
        
        if level == PowerLevel.OFF:
            return f"The {self.key} powers down."
        elif old_level == PowerLevel.OFF:
            return f"The {self.key} hums to life at {level.value} power."
        else:
            return f"The {self.key} adjusts to {level.value} power."
    
    def power_up(self) -> str:
        """Increase power one level."""
        levels = list(PowerLevel)
        current_idx = levels.index(self.db.power_level)
        if current_idx < len(levels) - 1:
            return self.set_power(levels[current_idx + 1])
        return f"The {self.key} is already at maximum power."
    
    def power_down(self) -> str:
        """Decrease power one level."""
        levels = list(PowerLevel)
        current_idx = levels.index(self.db.power_level)
        if current_idx > 0:
            return self.set_power(levels[current_idx - 1])
        return f"The {self.key} is already off."
    
    def lock_power(self) -> str:
        """Lock the power controls."""
        self.db.power_locked = True
        return f"The {self.key}'s controls are now locked."
    
    def unlock_power(self) -> str:
        """Unlock the power controls."""
        self.db.power_locked = False
        return f"The {self.key}'s controls are now unlocked."
    
    # -------------------------------------------------------------------------
    # ATTACHMENTS
    # -------------------------------------------------------------------------
    
    def add_attachment(
        self,
        attachment_type: AttachmentType,
        target_zone: str,
        size: float = 1.0,
        texture: str = "smooth"
    ) -> str:
        """Add an attachment to the machine."""
        attachment = MachineAttachment(
            attachment_type=attachment_type,
            target_zone=target_zone,
            size=size,
            texture=texture,
        )
        
        attachments = self.db.attachments or []
        attachments.append(attachment)
        self.db.attachments = attachments
        
        return f"You attach a {attachment_type.value} targeting the {target_zone}."
    
    def remove_attachment(self, target_zone: str) -> str:
        """Remove an attachment by target zone."""
        attachments = self.db.attachments or []
        new_attachments = [a for a in attachments if a.target_zone != target_zone]
        
        if len(new_attachments) == len(attachments):
            return f"No attachment found targeting {target_zone}."
        
        self.db.attachments = new_attachments
        return f"You remove the attachment targeting {target_zone}."
    
    def get_attachments(self) -> List[MachineAttachment]:
        """Get all attachments."""
        return self.db.attachments or []
    
    # -------------------------------------------------------------------------
    # TICK PROCESSING
    # -------------------------------------------------------------------------
    
    def get_arousal_rate(self) -> float:
        """Get current arousal generation rate."""
        power = self.db.power_level
        if power == PowerLevel.OFF:
            return 0.0
        return self.db.base_arousal_rate * power.intensity
    
    def process_tick(self) -> List[Tuple[str, str]]:
        """
        Process one tick of machine operation.
        Returns list of (character_dbref, message) for effects.
        
        This would be called by sexual_tick.py
        """
        if self.db.power_level == PowerLevel.OFF:
            return []
        
        effects = []
        arousal_rate = self.get_arousal_rate()
        
        for occupant in self.get_occupants():
            # Generate arousal message
            if arousal_rate > 0:
                intensity = self._get_intensity_word()
                effects.append((
                    occupant.character_dbref,
                    f"The {self.key} {intensity} stimulates you..."
                ))
        
        # Handle timer
        if self.db.timer_remaining > 0:
            self.db.timer_remaining -= 1
            if self.db.timer_remaining <= 0:
                self.set_power(PowerLevel.OFF)
                effects.append((None, f"The {self.key} finishes its cycle and powers down."))
        
        return effects
    
    def _get_intensity_word(self) -> str:
        """Get word describing current intensity."""
        level = self.db.power_level
        return {
            PowerLevel.OFF: "barely",
            PowerLevel.LOW: "gently",
            PowerLevel.MEDIUM: "steadily",
            PowerLevel.HIGH: "intensely",
            PowerLevel.MAX: "relentlessly",
        }.get(level, "")
    
    # -------------------------------------------------------------------------
    # TIMER
    # -------------------------------------------------------------------------
    
    def set_timer(self, ticks: int) -> str:
        """Set a timer for automatic shutoff."""
        self.db.timer_duration = ticks
        self.db.timer_remaining = ticks
        minutes = ticks  # Assuming 1 tick = ~1 minute
        return f"The {self.key} is set to run for {minutes} minutes."
    
    def clear_timer(self) -> str:
        """Clear the timer."""
        self.db.timer_duration = 0
        self.db.timer_remaining = 0
        return f"The {self.key}'s timer is cleared."


# =============================================================================
# SYBIAN
# =============================================================================

class Sybian(Machine):
    """
    A sybian - vibrating saddle for riding.
    
    The rider straddles it and it vibrates/rotates.
    """
    
    def at_object_creation(self):
        super().at_object_creation()
        self.db.furniture_type = FurnitureType.SYBIAN
        self.db.position_tags = {
            "machine", "sybian", "riding",
            "straddling", "vibration",
        }
        self.db.max_total_occupants = 1
        self.db.base_arousal_rate = 8.0  # Intense
        self.db.material = "padded leather"
        self.db.desc = (
            "A padded saddle-shaped device with controls on the side. "
            "A powerful vibration motor hums within."
        )
        
        # Sybian-specific
        self.db.has_attachment = False
        self.db.attachment_type = AttachmentType.NONE
        self.db.rotation_enabled = False
    
    def get_slots(self) -> Dict[str, FurnitureSlot]:
        return {
            "mounted": FurnitureSlot(
                key="mounted",
                name="mounted on the sybian",
                max_occupants=1,
                positions={
                    OccupantPosition.STRADDLING,
                    OccupantPosition.MOUNTED,
                },
                is_restraint=False,  # Can dismount
                exposed_zones={"groin", "thighs", "chest", "back", "ass"},
                description="{name} straddles the sybian, grinding against it",
            ),
        }
    
    def set_attachment(self, attachment: AttachmentType) -> str:
        """Set the sybian's attachment."""
        if attachment == AttachmentType.NONE:
            self.db.has_attachment = False
            self.db.attachment_type = AttachmentType.NONE
            return "You remove the attachment from the sybian."
        else:
            self.db.has_attachment = True
            self.db.attachment_type = attachment
            return f"You attach a {attachment.value} to the sybian."
    
    def toggle_rotation(self) -> str:
        """Toggle the rotation feature."""
        self.db.rotation_enabled = not self.db.rotation_enabled
        if self.db.rotation_enabled:
            return "The sybian's rotation activates, adding a swirling motion."
        else:
            return "The sybian's rotation stops."


class DualSybian(Sybian):
    """
    A sybian with two saddles - for two riders.
    """
    
    def at_object_creation(self):
        super().at_object_creation()
        self.db.max_total_occupants = 2
        self.db.desc = (
            "A double-wide sybian with two saddles side by side. "
            "Separate controls for each seat."
        )
    
    def get_slots(self) -> Dict[str, FurnitureSlot]:
        return {
            "left": FurnitureSlot(
                key="left",
                name="on the left saddle",
                max_occupants=1,
                positions={OccupantPosition.STRADDLING, OccupantPosition.MOUNTED},
                exposed_zones={"groin", "thighs", "chest"},
                description="{name} rides the left saddle",
            ),
            "right": FurnitureSlot(
                key="right",
                name="on the right saddle",
                max_occupants=1,
                positions={OccupantPosition.STRADDLING, OccupantPosition.MOUNTED},
                exposed_zones={"groin", "thighs", "chest"},
                description="{name} rides the right saddle",
            ),
        }


# =============================================================================
# FUCKING MACHINE
# =============================================================================

class FuckingMachine(Machine):
    """
    A mechanical fucking machine with a thrusting attachment.
    """
    
    def at_object_creation(self):
        super().at_object_creation()
        self.db.furniture_type = FurnitureType.FUCKING_MACHINE
        self.db.position_tags = {
            "machine", "fucking_machine",
            "doggy", "prone", "penetration",
        }
        self.db.max_total_occupants = 1
        self.db.base_arousal_rate = 10.0  # Very intense
        self.db.desc = (
            "A mechanical device with a motorized piston arm. "
            "Various attachments can be mounted on the end."
        )
        
        # Machine-specific
        self.db.stroke_length = "medium"  # short, medium, long, brutal
        self.db.current_attachment = AttachmentType.DILDO_MEDIUM
    
    def get_slots(self) -> Dict[str, FurnitureSlot]:
        return {
            "receiving": FurnitureSlot(
                key="receiving",
                name="positioned before the machine",
                max_occupants=1,
                positions={
                    OccupantPosition.BENT_OVER,
                    OccupantPosition.LYING_BACK,
                    OccupantPosition.LYING_FRONT,
                    OccupantPosition.BOUND_BENT,
                },
                is_restraint=False,  # Machine doesn't restrain by default
                exposed_zones={"groin", "ass", "thighs"},
                description="{name} is positioned to receive the machine's thrusts",
            ),
        }
    
    def set_stroke_length(self, length: str) -> str:
        """Set the stroke length."""
        if length in ("short", "medium", "long", "brutal"):
            self.db.stroke_length = length
            return f"The machine adjusts to {length} strokes."
        return "Invalid length. Use: short, medium, long, or brutal."
    
    def set_attachment(self, attachment: AttachmentType) -> str:
        """Set the machine's attachment."""
        self.db.current_attachment = attachment
        return f"You mount a {attachment.value} on the machine."


class PistonMachine(FuckingMachine):
    """Standard piston-style fucking machine."""
    pass


class RotatingMachine(FuckingMachine):
    """A machine that rotates as well as thrusts."""
    
    def at_object_creation(self):
        super().at_object_creation()
        self.db.rotation_speed = "medium"
        self.db.desc = (
            "A fucking machine with a rotating attachment. "
            "It spirals as it thrusts."
        )


class TentacleMachine(FuckingMachine):
    """
    A machine with multiple flexible tentacle-like arms.
    Can target multiple zones simultaneously.
    """
    
    def at_object_creation(self):
        super().at_object_creation()
        self.db.position_tags.update({"tentacle", "multi"})
        self.db.base_arousal_rate = 15.0  # Very intense
        self.db.num_tentacles = 4
        self.db.desc = (
            "A nightmarish machine with multiple writhing mechanical tentacles. "
            "Each can be fitted with different attachments."
        )
        
        # Multiple attachments
        self.db.attachments = [
            MachineAttachment(AttachmentType.TENTACLE, "pussy"),
            MachineAttachment(AttachmentType.TENTACLE, "ass"),
            MachineAttachment(AttachmentType.TENTACLE, "mouth"),
            MachineAttachment(AttachmentType.TENTACLE, "breasts"),
        ]


# =============================================================================
# MILKING STATION
# =============================================================================

class MilkingStation(Machine):
    """
    Base class for milking machines.
    """
    
    def at_object_creation(self):
        super().at_object_creation()
        self.db.furniture_type = FurnitureType.MILKING_STATION
        self.db.position_tags = {
            "machine", "milking",
            "lactation", "extraction",
        }
        self.db.base_arousal_rate = 4.0  # Moderate
        self.db.extraction_rate = 1.0  # Fluid per tick


class BreastPumps(MilkingStation):
    """
    A milking station with breast pumps.
    Extracts milk from lactating characters.
    """
    
    def at_object_creation(self):
        super().at_object_creation()
        self.db.position_tags.update({"breast_pump", "lactation"})
        self.db.max_total_occupants = 1
        self.db.desc = (
            "A milking station with two clear suction cups designed to "
            "fit over breasts. Tubes lead to collection containers."
        )
        
        # Pump-specific
        self.db.suction_level = "medium"  # low, medium, high
        self.db.collected_ml = 0.0
    
    def get_slots(self) -> Dict[str, FurnitureSlot]:
        return {
            "milking": FurnitureSlot(
                key="milking",
                name="hooked up to the pumps",
                max_occupants=1,
                positions={
                    OccupantPosition.SITTING,
                    OccupantPosition.KNEELING,
                    OccupantPosition.STANDING,
                    OccupantPosition.BOUND_KNEELING,
                },
                is_restraint=False,
                exposed_zones={"breasts", "chest"},
                description="{name} has breast pumps attached, rhythmically extracting",
            ),
        }
    
    def set_suction(self, level: str) -> str:
        """Set suction level."""
        if level in ("low", "medium", "high"):
            self.db.suction_level = level
            return f"The suction adjusts to {level}."
        return "Invalid level. Use: low, medium, or high."
    
    def get_collected(self) -> float:
        """Get amount of collected milk."""
        return self.db.collected_ml
    
    def empty_collection(self) -> str:
        """Empty the collection container."""
        amount = self.db.collected_ml
        self.db.collected_ml = 0.0
        return f"You empty {amount:.0f}ml of collected milk."


class CockMilker(MilkingStation):
    """
    A milking machine for cocks.
    Extracts cum through suction/stimulation.
    """
    
    def at_object_creation(self):
        super().at_object_creation()
        self.db.position_tags = {
            "machine", "milking",
            "cock_milking", "extraction",
        }
        self.db.base_arousal_rate = 8.0
        self.db.max_total_occupants = 1
        self.db.desc = (
            "A milking machine with a clear sleeve attachment. "
            "It rhythmically massages and suctions to extract cum."
        )
        
        # Milker-specific
        self.db.sleeve_type = "standard"  # standard, ribbed, tentacle
        self.db.forced_orgasms = 0
        self.db.collected_ml = 0.0
    
    def get_slots(self) -> Dict[str, FurnitureSlot]:
        return {
            "milking": FurnitureSlot(
                key="milking",
                name="being milked",
                max_occupants=1,
                positions={
                    OccupantPosition.SITTING,
                    OccupantPosition.STANDING,
                    OccupantPosition.LYING_BACK,
                    OccupantPosition.BOUND_STANDING,
                },
                is_restraint=False,
                exposed_zones={"groin", "cock"},
                description="{name} has their cock enclosed in the milking sleeve",
            ),
        }


# =============================================================================
# VIBRATION PLATFORMS
# =============================================================================

class VibrationPlatform(Machine):
    """
    Base class for vibrating furniture.
    """
    
    def at_object_creation(self):
        super().at_object_creation()
        self.db.position_tags = {"machine", "vibration"}
        self.db.base_arousal_rate = 3.0  # Lower than direct machines


class VibratingChair(VibrationPlatform):
    """
    A chair that vibrates.
    """
    
    def at_object_creation(self):
        super().at_object_creation()
        self.db.furniture_type = FurnitureType.CHAIR
        self.db.position_tags = {"sitting", "vibration", "machine"}
        self.db.max_total_occupants = 1
        self.db.desc = "A chair with a powerful vibration motor in the seat."
    
    def get_slots(self) -> Dict[str, FurnitureSlot]:
        return {
            "seat": FurnitureSlot(
                key="seat",
                name="seated",
                max_occupants=1,
                positions={OccupantPosition.SITTING},
                exposed_zones={"groin", "thighs"},
                description="{name} sits on the vibrating chair",
            ),
        }


class VibratingBed(VibrationPlatform):
    """
    A bed that vibrates.
    """
    
    def at_object_creation(self):
        super().at_object_creation()
        self.db.furniture_type = FurnitureType.BED
        self.db.position_tags = {"lying", "vibration", "machine", "bed"}
        self.db.max_total_occupants = 2
        self.db.base_arousal_rate = 2.0  # Gentle
        self.db.desc = "A bed with a 'magic fingers' vibration feature."
    
    def get_slots(self) -> Dict[str, FurnitureSlot]:
        return {
            "mattress": FurnitureSlot(
                key="mattress",
                name="on the vibrating bed",
                max_occupants=2,
                positions={
                    OccupantPosition.LYING_BACK,
                    OccupantPosition.LYING_FRONT,
                    OccupantPosition.LYING_SIDE,
                },
                exposed_zones={"all"},
                description="{name} lies on the gently vibrating mattress",
            ),
        }


# =============================================================================
# EXPORTS
# =============================================================================

__all__ = [
    # Enums
    "PowerLevel",
    "AttachmentType",
    
    # Data classes
    "MachineAttachment",
    
    # Base
    "Machine",
    
    # Sybians
    "Sybian",
    "DualSybian",
    
    # Fucking Machines
    "FuckingMachine",
    "PistonMachine",
    "RotatingMachine",
    "TentacleMachine",
    
    # Milking
    "MilkingStation",
    "BreastPumps",
    "CockMilker",
    
    # Vibration
    "VibrationPlatform",
    "VibratingChair",
    "VibratingBed",
]
