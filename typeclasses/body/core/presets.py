"""
Preset Body Compositions

Quick-compose common body types using Body.compose().
These are convenience functions for common character archetypes.

Usage:
    from typeclasses.body.core.presets import compose_wolf_anthro_male
    body = compose_wolf_anthro_male()
"""

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .body import Body


def _get_body_class():
    """Lazy import to avoid circular dependency."""
    from .body import Body
    return Body


# =============================================================================
# HUMANOID PRESETS
# =============================================================================

def compose_human_male() -> "Body":
    """Standard human male."""
    return _get_body_class().compose("bipedal_plantigrade", "human", "male")


def compose_human_female() -> "Body":
    """Standard human female."""
    return _get_body_class().compose("bipedal_plantigrade", "human", "female")


def compose_elf_male() -> "Body":
    """Male elf."""
    return _get_body_class().compose("bipedal_plantigrade", "elf", "male")


def compose_elf_female() -> "Body":
    """Female elf."""
    return _get_body_class().compose("bipedal_plantigrade", "elf", "female")


# =============================================================================
# ANTHRO PRESETS
# =============================================================================

def compose_wolf_anthro_male() -> "Body":
    """Male anthro wolf (digitigrade) - canine genitals."""
    return _get_body_class().compose("bipedal_digitigrade", "wolf", "male")


def compose_wolf_anthro_female() -> "Body":
    """Female anthro wolf (digitigrade) - canine genitals."""
    return _get_body_class().compose("bipedal_digitigrade", "wolf", "female")


def compose_cat_anthro_female() -> "Body":
    """Female anthro cat - feline genitals."""
    return _get_body_class().compose("bipedal_digitigrade", "cat", "female")


def compose_horse_anthro_male() -> "Body":
    """Male anthro horse - equine genitals."""
    return _get_body_class().compose("bipedal_plantigrade", "horse", "male")


def compose_femboy_fox() -> "Body":
    """Femboy fox anthro - canine genitals."""
    return _get_body_class().compose("bipedal_digitigrade", "fox", "femboy")


def compose_dickgirl_cat() -> "Body":
    """Dickgirl cat anthro - feline genitals."""
    return _get_body_class().compose("bipedal_digitigrade", "cat", "dickgirl")


# =============================================================================
# FERAL PRESETS
# =============================================================================

def compose_wolf_feral() -> "Body":
    """Feral wolf (quadruped) - canine genitals."""
    return _get_body_class().compose("quadruped", "wolf", "male")


# =============================================================================
# TAUR/HYBRID PRESETS
# =============================================================================

def compose_centaur_male() -> "Body":
    """Male centaur (tauroid) - equine genitals."""
    return _get_body_class().compose("tauroid", "horse", "male")


def compose_centaur_female() -> "Body":
    """Female centaur - equine genitals."""
    return _get_body_class().compose("tauroid", "horse", "female")


def compose_lamia_female() -> "Body":
    """Female lamia (serpentine) - reptile genitals."""
    return _get_body_class().compose("serpentine", "snake", "female")


def compose_mermaid() -> "Body":
    """Female merfolk - aquatic genitals."""
    return _get_body_class().compose("aquatic", "fish", "female")


# =============================================================================
# FANTASY PRESETS
# =============================================================================

def compose_succubus() -> "Body":
    """Female succubus - human genitals."""
    return _get_body_class().compose("bipedal_plantigrade", "succubus", "female")


# =============================================================================
# HERM/FUTA PRESETS
# =============================================================================

def compose_herm_wolf() -> "Body":
    """Hermaphrodite wolf anthro - canine genitals."""
    return _get_body_class().compose("bipedal_digitigrade", "wolf", "herm")


def compose_futa_human() -> "Body":
    """Human futanari - human genitals."""
    return _get_body_class().compose("bipedal_plantigrade", "human", "futa")


def compose_futa_horse_human() -> "Body":
    """Human futanari with horse cock."""
    return _get_body_class().compose("bipedal_plantigrade", "human", "futa", genital_override="equine")
