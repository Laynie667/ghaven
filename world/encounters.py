"""
Encounter System for Gilderhaven

Handles random encounters, multi-wave combat, area danger levels,
and integration with the party system.
"""

from random import random, randint, choice, shuffle
from evennia import create_object
from evennia.utils import delay

# =============================================================================
# ENCOUNTER CONFIGURATION
# =============================================================================

# Base encounter chance per room move (modified by area danger)
BASE_ENCOUNTER_CHANCE = 0.15  # 15%

# Danger levels affect encounter rate and difficulty
DANGER_LEVELS = {
    "safe": {
        "name": "Safe",
        "encounter_mult": 0.0,  # No random encounters
        "difficulty_mult": 1.0,
        "color": "|g",
    },
    "peaceful": {
        "name": "Peaceful",
        "encounter_mult": 0.3,  # 30% of base rate
        "difficulty_mult": 0.8,
        "color": "|G",
    },
    "normal": {
        "name": "Normal",
        "encounter_mult": 1.0,
        "difficulty_mult": 1.0,
        "color": "|y",
    },
    "dangerous": {
        "name": "Dangerous",
        "encounter_mult": 1.5,
        "difficulty_mult": 1.3,
        "color": "|r",
    },
    "deadly": {
        "name": "Deadly",
        "encounter_mult": 2.0,
        "difficulty_mult": 1.6,
        "color": "|R",
    },
}

# Area danger assignments
AREA_DANGER = {
    # Hub areas - safe
    "the_grove": "safe",
    "museum": "safe",
    "market": "safe",
    
    # Newbie areas - peaceful to normal
    "whisperwood": "peaceful",
    "moonshallow": "peaceful",
    "sunny_meadow": "peaceful",
    "tidepools": "safe",  # Beach is safe
    "copper_hill": "normal",
    
    # Deeper areas - dangerous
    "whisperwood_deep": "dangerous",
    "copper_hill_mines": "dangerous",
    
    # End-game areas - deadly
    "the_depths": "deadly",
    "breeding_pits": "deadly",
}

# Default danger for unknown areas
DEFAULT_DANGER = "normal"


# =============================================================================
# ENCOUNTER TEMPLATES
# =============================================================================
# Pre-defined encounter setups beyond just spawning from creature tables

ENCOUNTER_TEMPLATES = {
    # === Single Creature Encounters ===
    "lone_wolf": {
        "name": "Lone Wolf",
        "desc": "A solitary wolf, probably separated from its pack.",
        "creatures": [{"key": "wolf", "count": 1}],
        "waves": 1,
        "flee_chance": 0.3,  # 30% chance creature flees if outmatched
    },
    
    "hungry_slime": {
        "name": "Hungry Slime",
        "desc": "A quivering mass of gel blocks your path.",
        "creatures": [{"key": "green_slime", "count": 1}],
        "waves": 1,
    },
    
    # === Pack Encounters ===
    "wolf_pack": {
        "name": "Wolf Pack",
        "desc": "A pack of wolves surrounds you!",
        "creatures": [{"key": "wolf", "count": (2, 4)}],  # 2-4 wolves
        "waves": 1,
        "pack_tactics": True,  # Wolves coordinate
    },
    
    "wolf_pack_alpha": {
        "name": "Wolf Pack with Alpha",
        "desc": "A wolf pack led by a massive alpha!",
        "creatures": [
            {"key": "wolf", "count": (2, 3)},
            {"key": "alpha_wolf", "count": 1},
        ],
        "waves": 1,
        "pack_tactics": True,
        "boss_encounter": True,
    },
    
    "goblin_patrol": {
        "name": "Goblin Patrol",
        "desc": "A group of goblins spots you!",
        "creatures": [{"key": "goblin", "count": (2, 4)}],
        "waves": 1,
        "loot_bonus": 1.5,
    },
    
    "goblin_raiding_party": {
        "name": "Goblin Raiding Party",
        "desc": "A goblin raiding party led by a shaman!",
        "creatures": [
            {"key": "goblin", "count": (3, 5)},
            {"key": "goblin_shaman", "count": 1},
        ],
        "waves": 1,
        "boss_encounter": True,
    },
    
    # === Multi-Wave Encounters ===
    "slime_swarm": {
        "name": "Slime Swarm",
        "desc": "Slimes keep coming!",
        "waves": 3,
        "wave_creatures": [
            [{"key": "green_slime", "count": 2}],
            [{"key": "green_slime", "count": 2}, {"key": "pink_slime", "count": 1}],
            [{"key": "pink_slime", "count": 2}],
        ],
        "wave_delay": 2,  # Seconds between waves
        "can_flee_between_waves": True,
    },
    
    "goblin_ambush": {
        "name": "Goblin Ambush",
        "desc": "It's an ambush! More goblins emerge!",
        "waves": 2,
        "wave_creatures": [
            [{"key": "goblin", "count": 2}],
            [{"key": "goblin", "count": 3}, {"key": "goblin_shaman", "count": 1}],
        ],
        "wave_delay": 1,
        "ambush": True,  # Players can't flee wave 1
    },
    
    "vine_tangle": {
        "name": "Vine Tangle",
        "desc": "The vines close in around you!",
        "waves": 2,
        "wave_creatures": [
            [{"key": "grabbing_vine", "count": 2}],
            [{"key": "grabbing_vine", "count": 1}, {"key": "tentacle_blossom", "count": 1}],
        ],
        "wave_delay": 3,
    },
    
    # === Boss Encounters ===
    "lamia_lair": {
        "name": "Lamia's Lair",
        "desc": "You've stumbled into a lamia's territory!",
        "creatures": [{"key": "lamia", "count": 1}],
        "waves": 1,
        "boss_encounter": True,
        "no_flee": True,  # Can't flee from boss
        "intro_text": "A beautiful woman's voice calls out... but her lower half is that of a massive serpent!",
    },
    
    "harpy_nest": {
        "name": "Harpy Nest",
        "desc": "You've disturbed a harpy nest!",
        "creatures": [{"key": "harpy", "count": (2, 3)}],
        "waves": 1,
        "boss_encounter": True,
        "intro_text": "Screeching fills the air as winged figures descend!",
    },
    
    # === Special Encounters ===
    "mimic_trap": {
        "name": "Mimic!",
        "desc": "That wasn't a treasure chest!",
        "creatures": [{"key": "mimic", "count": 1}],
        "waves": 1,
        "surprise_round": True,  # Mimic acts first
        "trigger": "interact",  # Triggered by interaction, not movement
    },
    
    "wisp_dance": {
        "name": "Wisp Dance",
        "desc": "Glowing lights surround you, drawing you in...",
        "creatures": [{"key": "wisp", "count": (2, 4)}],
        "waves": 1,
        "can_befriend": True,
        "flee_easy": True,
    },
}


# =============================================================================
# AREA ENCOUNTER TABLES
# =============================================================================
# What encounters can occur in each area

AREA_ENCOUNTERS = {
    "whisperwood": {
        "common": ["hungry_slime", "lone_wolf"],
        "uncommon": ["wolf_pack", "vine_tangle"],
        "rare": ["wisp_dance", "slime_swarm"],
        "weights": {"common": 0.6, "uncommon": 0.3, "rare": 0.1},
    },
    "whisperwood_deep": {
        "common": ["wolf_pack", "vine_tangle"],
        "uncommon": ["wolf_pack_alpha", "slime_swarm"],
        "rare": ["lamia_lair"],
        "weights": {"common": 0.5, "uncommon": 0.35, "rare": 0.15},
    },
    "moonshallow": {
        "common": ["hungry_slime", "wisp_dance"],
        "uncommon": ["slime_swarm"],
        "rare": [],
        "weights": {"common": 0.7, "uncommon": 0.3, "rare": 0.0},
    },
    "sunny_meadow": {
        "common": [],
        "uncommon": ["wisp_dance"],
        "rare": ["vine_tangle"],
        "weights": {"common": 0.0, "uncommon": 0.7, "rare": 0.3},
    },
    "copper_hill": {
        "common": ["goblin_patrol"],
        "uncommon": ["goblin_ambush", "mimic_trap"],
        "rare": ["goblin_raiding_party"],
        "weights": {"common": 0.6, "uncommon": 0.3, "rare": 0.1},
    },
    "copper_hill_heights": {
        "common": ["goblin_patrol"],
        "uncommon": ["harpy_nest"],
        "rare": [],
        "weights": {"common": 0.6, "uncommon": 0.4, "rare": 0.0},
    },
}


# =============================================================================
# Encounter State Machine
# =============================================================================

class Encounter:
    """
    Manages a multi-wave encounter.
    
    Stored as room.ndb.encounter or combat.ndb.encounter
    """
    
    def __init__(self, template_key, location, participants):
        """
        Initialize an encounter.
        
        Args:
            template_key: Key from ENCOUNTER_TEMPLATES
            location: Room where encounter occurs
            participants: List of player characters
        """
        self.template_key = template_key
        self.template = ENCOUNTER_TEMPLATES.get(template_key, {})
        self.location = location
        self.participants = participants
        
        self.current_wave = 0
        self.total_waves = self.template.get("waves", 1)
        self.active = True
        self.combat = None
        self.spawned_creatures = []
        self.defeated_creatures = []
        self.loot_pool = []
        self.exp_pool = 0
        
        # Link to location
        location.ndb.encounter = self
        
        # Link to participants
        for char in participants:
            char.ndb.encounter = self
    
    def start(self):
        """Start the encounter with wave 1."""
        template = self.template
        
        # Show intro text
        intro = template.get("intro_text")
        if intro:
            for char in self.participants:
                char.msg(f"|y{intro}|n")
        
        # Spawn wave 1
        self.spawn_wave(1)
    
    def spawn_wave(self, wave_num):
        """Spawn creatures for a specific wave."""
        self.current_wave = wave_num
        
        template = self.template
        
        # Get creatures for this wave
        if "wave_creatures" in template:
            # Multi-wave with specific creatures per wave
            wave_index = wave_num - 1
            if wave_index < len(template["wave_creatures"]):
                creature_list = template["wave_creatures"][wave_index]
            else:
                creature_list = []
        else:
            # Single wave or repeated waves
            creature_list = template.get("creatures", [])
        
        # Spawn each creature type
        spawned = []
        for creature_def in creature_list:
            key = creature_def["key"]
            count = creature_def["count"]
            
            # Handle count ranges
            if isinstance(count, tuple):
                count = randint(count[0], count[1])
            
            for _ in range(count):
                creature = spawn_creature(key, self.location)
                if creature:
                    spawned.append(creature)
                    self.spawned_creatures.append(creature)
        
        # Start or update combat
        if spawned:
            if self.combat and self.combat.active:
                # Add to existing combat
                for creature in spawned:
                    self.combat.add_combatant(creature, "enemy")
                
                # Announce reinforcements
                names = ", ".join([c.key for c in spawned])
                for char in self.participants:
                    char.msg(f"|r=== WAVE {wave_num} ===|n")
                    char.msg(f"Reinforcements arrive: {names}!")
            else:
                # Start new combat
                from world.parties import start_party_combat
                
                # Check for party
                from world.parties import get_party
                party = get_party(self.participants[0]) if self.participants else None
                
                if party:
                    self.combat = start_party_combat(
                        party.leader, spawned, self.location,
                        self.template_key
                    )
                else:
                    from world.combat import start_combat
                    self.combat = start_combat(
                        self.participants[0], spawned, self.location,
                        self.template_key
                    )
                
                # Handle surprise round
                if template.get("surprise_round") and wave_num == 1:
                    for char in self.participants:
                        char.msg("|rSurprise! The enemy acts first!|n")
                    # Enemies go first - would modify turn order
                
                # Handle ambush (no flee wave 1)
                if template.get("ambush") and wave_num == 1:
                    for char in self.participants:
                        char.msg("|rIt's an ambush! You can't escape!|n")
        
        return spawned
    
    def on_wave_complete(self):
        """Called when current wave is defeated."""
        # Collect loot from defeated creatures
        from world.creatures import get_loot_drops, get_creature_exp
        
        for creature in self.spawned_creatures:
            if creature not in self.defeated_creatures:
                self.defeated_creatures.append(creature)
                
                # Get creature type
                creature_key = creature.db.creature_type if hasattr(creature, "db") else None
                if creature_key:
                    # Add loot
                    drops = get_loot_drops(creature_key)
                    self.loot_pool.extend(drops)
                    
                    # Add exp
                    self.exp_pool += get_creature_exp(creature_key)
                
                # Clean up creature object
                creature.delete()
        
        # Check for next wave
        if self.current_wave < self.total_waves:
            wave_delay = self.template.get("wave_delay", 2)
            
            # Announce incoming wave
            for char in self.participants:
                char.msg(f"|yWave {self.current_wave} complete! Wave {self.current_wave + 1} incoming...|n")
                
                # Allow flee between waves?
                if self.template.get("can_flee_between_waves"):
                    char.msg("|wYou have a moment to flee if you wish.|n")
            
            # Schedule next wave
            def next_wave():
                if self.active:
                    self.spawn_wave(self.current_wave + 1)
            
            delay(wave_delay, next_wave)
        else:
            # Encounter complete!
            self.complete()
    
    def complete(self):
        """Encounter completed successfully."""
        self.active = False
        
        # Apply loot bonus
        loot_bonus = self.template.get("loot_bonus", 1.0)
        
        # Distribute rewards
        from world.parties import get_party, distribute_loot, distribute_exp
        
        party = get_party(self.participants[0]) if self.participants else None
        
        if party:
            # Party distribution
            distribute_loot(party, self.loot_pool, self.template.get("name", "enemy"))
            distribute_exp(party, self.exp_pool, self.template.get("name", "enemy"))
        else:
            # Solo distribution
            for char in self.participants:
                char.msg(f"|c+{self.exp_pool} experience|n")
                for item_key, amount in self.loot_pool:
                    char.msg(f"|gObtained: {item_key} x{amount}|n")
        
        # Victory message
        for char in self.participants:
            char.msg("|g=== VICTORY ===|n")
            if self.template.get("boss_encounter"):
                char.msg("|yYou have defeated a powerful foe!|n")
        
        # Cleanup
        self.cleanup()
    
    def fail(self, reason="defeated"):
        """Encounter failed."""
        self.active = False
        
        # Handle defeat based on encounter type
        for char in self.participants:
            char.msg(f"|r=== DEFEAT ===|n")
        
        # Cleanup spawned creatures
        for creature in self.spawned_creatures:
            if creature not in self.defeated_creatures:
                creature.delete()
        
        self.cleanup()
    
    def flee(self, character):
        """Handle a character fleeing the encounter."""
        if self.template.get("no_flee"):
            return False, "You cannot flee from this encounter!"
        
        if self.template.get("ambush") and self.current_wave == 1:
            return False, "It's an ambush! You can't escape yet!"
        
        # Remove from participants
        if character in self.participants:
            self.participants.remove(character)
            character.ndb.encounter = None
        
        # Check if all participants fled
        if not self.participants:
            self.fail("all fled")
        
        return True, "You escape the encounter!"
    
    def cleanup(self):
        """Clean up encounter references."""
        # Unlink from location
        if self.location and hasattr(self.location, "ndb"):
            self.location.ndb.encounter = None
        
        # Unlink from participants
        for char in self.participants:
            if hasattr(char, "ndb"):
                char.ndb.encounter = None


# =============================================================================
# Helper Functions
# =============================================================================

def get_area_danger(area_key):
    """Get danger level for an area."""
    danger_key = AREA_DANGER.get(area_key, DEFAULT_DANGER)
    return DANGER_LEVELS.get(danger_key, DANGER_LEVELS["normal"])


def get_room_danger(room):
    """Get danger level for a specific room."""
    # Check room override
    if hasattr(room, "db") and room.db.danger_level:
        danger_key = room.db.danger_level
        return DANGER_LEVELS.get(danger_key, DANGER_LEVELS["normal"])
    
    # Check area
    area_key = room.db.area if hasattr(room, "db") else None
    if area_key:
        return get_area_danger(area_key)
    
    return DANGER_LEVELS.get(DEFAULT_DANGER)


def check_random_encounter(character, room):
    """
    Check if a random encounter triggers when entering a room.
    
    Args:
        character: The character entering
        room: The room being entered
        
    Returns:
        str or None: Encounter template key or None
    """
    # Skip if already in encounter or combat
    if hasattr(character, "ndb"):
        if character.ndb.encounter or character.ndb.combat:
            return None
    
    # Get danger level
    danger = get_room_danger(room)
    
    # Calculate encounter chance
    encounter_mult = danger.get("encounter_mult", 1.0)
    encounter_chance = BASE_ENCOUNTER_CHANCE * encounter_mult
    
    # Party size modifier (slightly reduced chance for parties)
    from world.parties import get_party_members
    party_size = len(get_party_members(character))
    if party_size > 1:
        encounter_chance *= (0.8 + party_size * 0.05)  # Slight increase for larger parties
    
    # Roll for encounter
    if random() > encounter_chance:
        return None
    
    # Get area encounter table
    area_key = room.db.area if hasattr(room, "db") else None
    encounter_table = AREA_ENCOUNTERS.get(area_key)
    
    if not encounter_table:
        return None
    
    # Roll for encounter rarity
    weights = encounter_table.get("weights", {})
    roll = random()
    cumulative = 0
    selected_tier = None
    
    for tier in ["rare", "uncommon", "common"]:
        cumulative += weights.get(tier, 0)
        if roll < cumulative:
            selected_tier = tier
            break
    
    if not selected_tier:
        return None
    
    # Get encounters from tier
    encounters = encounter_table.get(selected_tier, [])
    if not encounters:
        # Fall back to lower tiers
        for tier in ["common", "uncommon", "rare"]:
            encounters = encounter_table.get(tier, [])
            if encounters:
                break
    
    if not encounters:
        return None
    
    return choice(encounters)


def spawn_creature(creature_key, location):
    """
    Spawn a creature object.
    
    Args:
        creature_key: Key from CREATURE_TEMPLATES
        location: Room to spawn in
        
    Returns:
        Character object or None
    """
    from world.creatures import get_creature_template, get_creature_stats
    
    template = get_creature_template(creature_key)
    if not template:
        return None
    
    # Create creature
    creature = create_object(
        "typeclasses.characters.Character",
        key=template["name"],
        location=location,
    )
    
    # Set up stats
    stats = get_creature_stats(creature_key)
    creature.db.is_npc = True
    creature.db.creature_type = creature_key
    creature.db.resources = {
        "hp": stats["max_hp"],
        "stamina": stats["max_stamina"],
        "composure": stats["max_composure"],
    }
    creature.db.attributes = stats["attributes"]
    creature.db.combat_skills = stats["skills"]
    creature.db.befriendable = template.get("befriendable", False)
    creature.db.befriend_difficulty = template.get("befriend_difficulty", 20)
    
    # Set description
    creature.db.desc = template.get("desc", "A creature.")
    
    return creature


def trigger_encounter(character, encounter_key, force=False):
    """
    Trigger a specific encounter.
    
    Args:
        character: Character triggering encounter
        encounter_key: Key from ENCOUNTER_TEMPLATES
        force: Bypass normal checks
        
    Returns:
        Encounter object or None
    """
    # Check if already in encounter
    if not force and hasattr(character, "ndb"):
        if character.ndb.encounter or character.ndb.combat:
            return None
    
    template = ENCOUNTER_TEMPLATES.get(encounter_key)
    if not template:
        return None
    
    location = character.location
    
    # Get participants (party or solo)
    from world.parties import get_party_for_combat
    participants = get_party_for_combat(character)
    
    # Create and start encounter
    encounter = Encounter(encounter_key, location, participants)
    encounter.start()
    
    return encounter


def on_room_enter(character, room):
    """
    Called when a character enters a room.
    Checks for random encounters.
    
    Hook into room.at_object_receive or character movement.
    """
    encounter_key = check_random_encounter(character, room)
    
    if encounter_key:
        trigger_encounter(character, encounter_key)


def get_active_encounter(character):
    """Get a character's active encounter."""
    return character.ndb.encounter if hasattr(character, "ndb") else None


def is_in_encounter(character):
    """Check if character is in an encounter."""
    encounter = get_active_encounter(character)
    return encounter is not None and encounter.active


# =============================================================================
# Combat Integration Hooks
# =============================================================================

def on_combat_end(combat, winner, condition):
    """
    Called when combat ends.
    Hooks into encounter wave progression.
    """
    # Find associated encounter
    encounter = None
    for char in combat.participants:
        if hasattr(char, "ndb") and char.ndb.encounter:
            encounter = char.ndb.encounter
            break
    
    if not encounter:
        return
    
    if winner == "player":
        # Players won - check for next wave
        encounter.on_wave_complete()
    elif winner == "enemy":
        # Players lost
        encounter.fail("defeated")


def on_player_flee(character, combat):
    """
    Called when a player flees combat.
    Updates encounter if applicable.
    """
    encounter = get_active_encounter(character)
    if encounter:
        return encounter.flee(character)
    return True, "You flee!"


# =============================================================================
# Scaling Functions
# =============================================================================

def scale_encounter_to_party(encounter_key, party_size):
    """
    Scale an encounter based on party size.
    
    Returns modified creature counts.
    """
    template = ENCOUNTER_TEMPLATES.get(encounter_key, {})
    
    if party_size <= 1:
        return template  # No scaling for solo
    
    # Clone template
    scaled = dict(template)
    
    # Scale creature counts
    if "creatures" in scaled:
        scaled_creatures = []
        for creature_def in scaled["creatures"]:
            new_def = dict(creature_def)
            count = new_def["count"]
            
            if isinstance(count, tuple):
                # Scale range
                min_c = int(count[0] * (1 + (party_size - 1) * 0.3))
                max_c = int(count[1] * (1 + (party_size - 1) * 0.3))
                new_def["count"] = (min_c, max_c)
            else:
                # Scale fixed count
                new_def["count"] = int(count * (1 + (party_size - 1) * 0.3))
            
            scaled_creatures.append(new_def)
        scaled["creatures"] = scaled_creatures
    
    # Scale waves
    if "wave_creatures" in scaled:
        scaled_waves = []
        for wave in scaled["wave_creatures"]:
            scaled_wave = []
            for creature_def in wave:
                new_def = dict(creature_def)
                count = new_def["count"]
                
                if isinstance(count, tuple):
                    min_c = int(count[0] * (1 + (party_size - 1) * 0.25))
                    max_c = int(count[1] * (1 + (party_size - 1) * 0.25))
                    new_def["count"] = (min_c, max_c)
                else:
                    new_def["count"] = int(count * (1 + (party_size - 1) * 0.25))
                
                scaled_wave.append(new_def)
            scaled_waves.append(scaled_wave)
        scaled["wave_creatures"] = scaled_waves
    
    return scaled


def get_encounter_difficulty(encounter_key, party_size=1):
    """
    Estimate encounter difficulty for a party.
    
    Returns: "trivial", "easy", "normal", "hard", "deadly"
    """
    template = ENCOUNTER_TEMPLATES.get(encounter_key, {})
    
    # Calculate total enemy "power"
    total_enemy_level = 0
    
    from world.creatures import get_creature_template
    
    creatures = template.get("creatures", [])
    for creature_def in creatures:
        creature_template = get_creature_template(creature_def["key"])
        if creature_template:
            level = creature_template.get("level", 1)
            count = creature_def["count"]
            if isinstance(count, tuple):
                count = (count[0] + count[1]) // 2  # Average
            total_enemy_level += level * count
    
    # Add wave creatures
    for wave in template.get("wave_creatures", []):
        for creature_def in wave:
            creature_template = get_creature_template(creature_def["key"])
            if creature_template:
                level = creature_template.get("level", 1)
                count = creature_def["count"]
                if isinstance(count, tuple):
                    count = (count[0] + count[1]) // 2
                total_enemy_level += level * count
    
    # Compare to party
    # Assume average player "level" of 3
    party_power = party_size * 3
    
    ratio = total_enemy_level / party_power if party_power > 0 else 999
    
    if ratio < 0.5:
        return "trivial"
    elif ratio < 0.8:
        return "easy"
    elif ratio < 1.2:
        return "normal"
    elif ratio < 1.8:
        return "hard"
    else:
        return "deadly"
