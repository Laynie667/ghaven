"""
Body Mechanics - Calculations

Handles all mechanical calculations for body interactions:
- Fit checks (penetration sizing)
- Arousal progression
- Pleasure/pain calculations
- Knot mechanics
- Fluid tracking
"""

from .sexual import (
    # Result types
    FitResult,
    PenetrationResult,
    ArousalChange,
    
    # Fit calculations
    calculate_fit,
    get_fit_description,
    
    # Knot mechanics
    calculate_knot_lock,
    calculate_knot_unlock_time,
    
    # Arousal
    calculate_arousal_change,
    calculate_arousal_decay,
    
    # Fluids
    calculate_cum_production,
    calculate_cum_volume,
    calculate_cum_capacity,
    calculate_natural_wetness,
    calculate_lube_depletion,
    
    # Recovery
    calculate_stretch_recovery,
    calculate_permanent_stretch,
    
    # Virginity
    check_virginity_loss,
    
    # Zones
    calculate_zone_stimulation,
    
    # Conception
    calculate_conception_chance,
)

__all__ = [
    # Result types
    "FitResult",
    "PenetrationResult",
    "ArousalChange",
    
    # Fit
    "calculate_fit",
    "get_fit_description",
    
    # Knot
    "calculate_knot_lock",
    "calculate_knot_unlock_time",
    
    # Arousal
    "calculate_arousal_change",
    "calculate_arousal_decay",
    
    # Fluids
    "calculate_cum_production",
    "calculate_cum_volume",
    "calculate_cum_capacity",
    "calculate_natural_wetness",
    "calculate_lube_depletion",
    
    # Recovery
    "calculate_stretch_recovery",
    "calculate_permanent_stretch",
    
    # Virginity
    "check_virginity_loss",
    
    # Zones
    "calculate_zone_stimulation",
    
    # Conception
    "calculate_conception_chance",
]
