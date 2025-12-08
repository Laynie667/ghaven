"""
Gilderhaven Typeclasses
=======================

Mixins and helpers for Evennia typeclasses.

These are designed to be added to your existing typeclasses
without replacing Evennia's defaults.

Usage:
    # In typeclasses/rooms.py
    from evennia import DefaultRoom
    from typeclasses.mixins import GilderhaveRoomMixin
    
    class Room(GilderhaveRoomMixin, DefaultRoom):
        '''Room with dynamic descriptions.'''
        pass
    
    # In typeclasses/characters.py
    from evennia import DefaultCharacter
    from typeclasses.mixins import GilderhaveCharacterMixin
    
    class Character(GilderhaveCharacterMixin, DefaultCharacter):
        '''Character with dynamic descriptions.'''
        pass

Mixins available:
    - DynamicDescMixin: Process shortcodes in descriptions
    - TimeAwareMixin: Time-based convenience methods
    - WeatherAwareMixin: Weather-based convenience methods
    - GilderhaveRoomMixin: Combined room mixin (all features)
    - GilderhaveCharacterMixin: Combined character mixin
"""

from .mixins import (
    DynamicDescMixin,
    TimeAwareMixin,
    WeatherAwareMixin,
    GilderhaveRoomMixin,
    GilderhaveCharacterMixin,
)
