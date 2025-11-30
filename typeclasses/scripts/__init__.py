"""
Scripts Module
==============

Game scripts for time-based mechanics.
"""

from .sexual_tick import (
    SexualStateTickScript,
    PositionTickScript,
    get_ticker,
    register_arousal,
    register_rhythm,
    start_refractory,
    is_refractory,
    ensure_room_ticker,
    TICK_INTERVAL,
    AROUSAL_DECAY_RATE,
    REFRACTORY_DURATION,
)

__all__ = [
    "SexualStateTickScript",
    "PositionTickScript",
    "get_ticker",
    "register_arousal",
    "register_rhythm",
    "start_refractory",
    "is_refractory",
    "ensure_room_ticker",
    "TICK_INTERVAL",
    "AROUSAL_DECAY_RATE",
    "REFRACTORY_DURATION",
]
