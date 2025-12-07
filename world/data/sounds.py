"""
Sound Profiles and Bleeding

Define what rooms sound like from adjacent areas.
Used for the sound bleeding system.

Sound profiles are strings that describe what you hear from
a room when you're in an adjacent space.

Volume levels:
    quiet - Only audible from directly adjacent rooms
    moderate - Audible with some reduction
    loud - Audible at full strength, may reach 2 rooms
"""

# =============================================================================
# SOUND PROFILES BY AREA TYPE
# =============================================================================

# These are used as room.sound_profile values

PLAZA_SOUNDS = {
    "empty": "Distant echoes from the empty plaza.",
    "normal": "The murmur of plaza activity.",
    "busy": "The clamor of a busy plaza—voices, footsteps, fountain splashing.",
}

MARKET_SOUNDS = {
    "empty": "The eerie quiet of closed market stalls.",
    "normal": "The bustle of commerce—voices haggling, coins clinking.",
    "busy": "A roar of merchant calls and customer chatter.",
}

TAVERN_SOUNDS = {
    "empty": "Silence from the tavern. Unusual.",
    "normal": "Muffled laughter and the clink of mugs from the tavern.",
    "busy": "Raucous noise from the packed tavern—singing, shouting, cheering.",
}

FORGE_SOUNDS = {
    "idle": "The occasional clank from the forge.",
    "active": "The rhythmic ring of hammer on anvil, the hiss of hot metal.",
    "busy": "A cacophony of metalwork—hammering, grinding, shouting.",
}

LIBRARY_SOUNDS = {
    "normal": "Absolute silence. Someone says 'shh.'",
}

WATERFRONT_SOUNDS = {
    "normal": "The gentle lap of water against the shore.",
    "busy": "Splashing, fishing lines casting, quiet conversations.",
}

FOREST_SOUNDS = {
    "day": "Birdsong and rustling leaves from the forest.",
    "night": "Night sounds from the forest—owls, crickets, mysterious rustlings.",
}

MINE_SOUNDS = {
    "idle": "The drip of water echoing from the mines.",
    "active": "Distant pickaxes striking stone, rumbling carts.",
}

QUARRY_SOUNDS = {
    "idle": "Wind whistling across exposed stone.",
    "active": "The crack and chip of stone being worked.",
}

MUSEUM_SOUNDS = {
    "normal": "Hushed voices and echoing footsteps.",
    "empty": "An almost oppressive silence.",
}

RESIDENTIAL_SOUNDS = {
    "morning": "The sounds of people starting their day.",
    "day": "Quiet neighborhood sounds—occasional voices, a barking dog.",
    "evening": "Families settling in for the night.",
    "night": "Peaceful silence, the occasional snore.",
}

# =============================================================================
# GENERIC SOUND DESCRIPTIONS BY VOLUME
# =============================================================================

VOLUME_MODIFIERS = {
    "quiet": {
        "far": "",  # Can't hear quiet sounds from far
        "near": "You hear faint sounds of",
        "adjacent": "From nearby you hear",
    },
    "moderate": {
        "far": "Distant sounds of",
        "near": "You hear",
        "adjacent": "You clearly hear",
    },
    "loud": {
        "far": "You can still hear",
        "near": "Loudly, you hear",
        "adjacent": "Almost overwhelming,",
    },
}

# =============================================================================
# DOOR AND BARRIER EFFECTS
# =============================================================================

BARRIER_SOUND_REDUCTION = {
    "open_doorway": 0.1,      # Almost no reduction
    "open_door": 0.2,         # Slight reduction
    "closed_door": 0.6,       # Significant reduction
    "thick_door": 0.8,        # Heavy reduction
    "stone_wall": 0.95,       # Almost complete block
    "soundproofed": 1.0,      # Complete block
}

# =============================================================================
# WEATHER EFFECTS ON SOUND
# =============================================================================

WEATHER_SOUND_MODS = {
    "clear": 1.0,       # Normal
    "cloudy": 1.0,      # Normal
    "rain": 0.7,        # Rain masks sounds
    "storm": 0.4,       # Storm covers most sounds
    "fog": 1.1,         # Fog can carry sound strangely
    "snow": 0.8,        # Snow muffles
}

# =============================================================================
# HELPER FUNCTIONS
# =============================================================================

def get_sound_from_distance(sound_profile: str, distance: int, volume: str = "moderate") -> str:
    """
    Get appropriate sound description based on distance.
    
    Args:
        sound_profile: The base sound description
        distance: Number of rooms away (1 = adjacent)
        volume: quiet, moderate, or loud
        
    Returns:
        Modified sound description or empty string if too far
    """
    if not sound_profile:
        return ""
    
    # Determine effective distance category
    if distance <= 1:
        dist_cat = "adjacent"
    elif distance <= 2:
        dist_cat = "near"
    else:
        dist_cat = "far"
    
    # Quiet sounds don't travel far
    if volume == "quiet" and distance > 1:
        return ""
    
    # Moderate sounds don't travel very far
    if volume == "moderate" and distance > 2:
        return ""
    
    # Get modifier
    modifiers = VOLUME_MODIFIERS.get(volume, VOLUME_MODIFIERS["moderate"])
    prefix = modifiers.get(dist_cat, "")
    
    if not prefix:
        return ""
    
    return f"{prefix} {sound_profile.lower()}"


def apply_barrier_reduction(sound_profile: str, barrier_type: str) -> str:
    """
    Reduce sound based on barrier type.
    
    Returns empty string if sound is completely blocked.
    """
    reduction = BARRIER_SOUND_REDUCTION.get(barrier_type, 0.5)
    
    if reduction >= 1.0:
        return ""  # Completely blocked
    
    if reduction >= 0.8:
        return f"Muffled {sound_profile.lower()}"
    
    if reduction >= 0.5:
        return f"Faint {sound_profile.lower()}"
    
    return sound_profile


# =============================================================================
# EXPORTS
# =============================================================================

__all__ = [
    "PLAZA_SOUNDS",
    "MARKET_SOUNDS",
    "TAVERN_SOUNDS",
    "FORGE_SOUNDS",
    "LIBRARY_SOUNDS",
    "WATERFRONT_SOUNDS",
    "FOREST_SOUNDS",
    "MINE_SOUNDS",
    "QUARRY_SOUNDS",
    "MUSEUM_SOUNDS",
    "RESIDENTIAL_SOUNDS",
    "VOLUME_MODIFIERS",
    "BARRIER_SOUND_REDUCTION",
    "WEATHER_SOUND_MODS",
    "get_sound_from_distance",
    "apply_barrier_reduction",
]
