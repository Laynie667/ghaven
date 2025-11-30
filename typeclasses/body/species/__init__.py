"""
Body Species Package

Defines species-specific cosmetic features.

Categories:
    Humanoid: human, elf, dwarf, orc, goblin, tiefling
    Canine: canine_generic, wolf, dog, fox, hyena
    Feline: feline_generic, cat, lion, tiger, leopard
    Equine: equine_generic, horse, unicorn, zebra
    Lapine: rabbit, hare
    Reptile: lizard, dragon, kobold, snake
    Avian: bird, raven, eagle
    Aquatic: fish, shark, dolphin
    Demon/Angel: angel, demon, succubus
    Insectoid: bee, ant, spider
    Misc: slime_species, robot

Usage:
    from typeclasses.body.species import get_species, WOLF
    
    species = get_species("fox")
"""

from .base import (
    SpeciesFeatures,
    
    # Humanoid
    HUMAN, ELF, DWARF, ORC, GOBLIN, TIEFLING,
    
    # Canine
    CANINE_GENERIC, WOLF, DOG, FOX, HYENA,
    
    # Feline
    FELINE_GENERIC, CAT, LION, TIGER, LEOPARD,
    
    # Equine
    EQUINE_GENERIC, HORSE, UNICORN, ZEBRA,
    
    # Lapine
    RABBIT, HARE,
    
    # Reptile
    LIZARD, DRAGON, KOBOLD, SNAKE,
    
    # Avian
    BIRD, RAVEN, EAGLE,
    
    # Aquatic
    FISH, SHARK, DOLPHIN,
    
    # Demon/Angel
    ANGEL, DEMON, SUCCUBUS,
    
    # Insectoid
    BEE, ANT, SPIDER,
    
    # Misc
    SLIME_SPECIES, ROBOT,
    
    # Registry
    SPECIES_REGISTRY,
    get_species,
    list_species,
    get_species_by_covering,
)

__all__ = [
    "SpeciesFeatures",
    
    "HUMAN", "ELF", "DWARF", "ORC", "GOBLIN", "TIEFLING",
    "CANINE_GENERIC", "WOLF", "DOG", "FOX", "HYENA",
    "FELINE_GENERIC", "CAT", "LION", "TIGER", "LEOPARD",
    "EQUINE_GENERIC", "HORSE", "UNICORN", "ZEBRA",
    "RABBIT", "HARE",
    "LIZARD", "DRAGON", "KOBOLD", "SNAKE",
    "BIRD", "RAVEN", "EAGLE",
    "FISH", "SHARK", "DOLPHIN",
    "ANGEL", "DEMON", "SUCCUBUS",
    "BEE", "ANT", "SPIDER",
    "SLIME_SPECIES", "ROBOT",
    
    "SPECIES_REGISTRY",
    "get_species",
    "list_species",
    "get_species_by_covering",
]
