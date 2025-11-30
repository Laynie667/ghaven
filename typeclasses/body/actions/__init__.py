"""
Body Actions - Interaction Framework

Defines and executes body actions:
- Penetration actions (fuck, thrust, withdraw)
- Oral actions (lick, suck, kiss)
- Manual actions (touch, grope, finger)
- Stimulation actions (rub, edge)
- Breeding actions (breed, creampie)
- Fluid actions (cum, milk)
- Meta actions (examine, pose)
"""

from .base import (
    # Enums
    ActionCategory,
    ActionResult,
    
    # Definitions
    ActionRequirement,
    ActionEffect,
    ActionDefinition,
    
    # Execution
    ActionAttempt,
    ActionOutcome,
    
    # Registry
    ACTIONS,
    get_action,
    get_actions_by_category,
    get_available_actions,
    get_actions_for_part,
    
    # Execution
    execute_action,
    check_action_requirements,
)

__all__ = [
    # Enums
    "ActionCategory",
    "ActionResult",
    
    # Definitions
    "ActionRequirement",
    "ActionEffect",
    "ActionDefinition",
    
    # Execution
    "ActionAttempt",
    "ActionOutcome",
    
    # Registry
    "ACTIONS",
    "get_action",
    "get_actions_by_category",
    "get_available_actions",
    "get_actions_for_part",
    
    # Execution
    "execute_action",
    "check_action_requirements",
]
