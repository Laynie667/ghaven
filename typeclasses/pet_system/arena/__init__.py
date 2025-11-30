"""
Arena Combat System
===================

Sexual combat and arena mechanics including:
- Combat stats and moves
- Sexual combat resolution
- Defeat consequences
- Gladiator training
- Betting systems
- Tournament brackets
"""

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any, Tuple
from enum import Enum
from datetime import datetime
import random


# =============================================================================
# ENUMS
# =============================================================================

class CombatStyle(Enum):
    """Fighting styles."""
    AGGRESSIVE = "aggressive"     # High damage, low defense
    DEFENSIVE = "defensive"       # Low damage, high defense
    SEDUCTIVE = "seductive"       # Arousal-focused
    DOMINANT = "dominant"         # Control-focused
    SUBMISSIVE = "submissive"     # Counterattack style
    WILD = "wild"                 # Unpredictable
    TECHNICAL = "technical"       # Precise, calculated


class CombatMove(Enum):
    """Combat moves available."""
    # Physical
    GRAPPLE = "grapple"
    PIN = "pin"
    THROW = "throw"
    STRIKE = "strike"
    
    # Sexual
    GROPE = "grope"
    KISS = "kiss"
    FINGER = "finger"
    ORAL = "oral"
    MOUNT = "mount"
    PENETRATE = "penetrate"
    
    # Control
    RESTRAIN = "restrain"
    CHOKE = "choke"
    SPANK = "spank"
    EDGE = "edge"
    FORCE_ORGASM = "force_orgasm"
    
    # Defensive
    ESCAPE = "escape"
    COUNTER = "counter"
    ENDURE = "endure"
    RESIST = "resist"


class DefeatCondition(Enum):
    """How a fight can end."""
    SUBMISSION = "submission"     # Tapped out
    ORGASM = "orgasm"             # Came too many times
    EXHAUSTION = "exhaustion"     # Stamina depleted
    KNOCKOUT = "knockout"         # Physical KO
    PINFALL = "pinfall"           # Held down for count


class DefeatConsequence(Enum):
    """What happens to the loser."""
    NONE = "none"                 # Just the loss
    PUBLIC_USE = "public_use"     # Used by audience
    CLAIMED = "claimed"           # Becomes winner's property
    BREEDING = "breeding"         # Bred by winner
    HUMILIATION = "humiliation"   # Public humiliation
    SERVITUDE = "servitude"       # Temporary service
    SLAVERY = "slavery"           # Permanent enslavement
    GANGBANG = "gangbang"         # Audience gangbang


class ArenaType(Enum):
    """Types of arena matches."""
    STANDARD = "standard"         # Normal 1v1
    TAG_TEAM = "tag_team"         # 2v2
    BATTLE_ROYAL = "battle_royal" # Free for all
    GAUNTLET = "gauntlet"         # One vs many sequential
    HANDICAP = "handicap"         # 1v2 or similar
    CAGE = "cage"                 # No escape
    MUD_PIT = "mud_pit"           # Slippery wrestling
    OIL_RING = "oil_ring"         # Oiled bodies


# =============================================================================
# COMBAT STATS
# =============================================================================

@dataclass
class CombatStats:
    """Combat statistics for a fighter."""
    
    fighter_id: str = ""
    fighter_name: str = ""
    
    # Base stats
    strength: int = 50            # Physical power
    agility: int = 50             # Speed and dodging
    endurance: int = 50           # Stamina
    technique: int = 50           # Skill level
    
    # Sexual stats
    seduction: int = 50           # Arousal attacks
    resistance: int = 50          # Resist arousal
    recovery: int = 50            # Recover from arousal
    
    # Current state
    current_stamina: int = 100
    max_stamina: int = 100
    current_arousal: int = 0
    max_arousal: int = 100        # Orgasm threshold
    
    # Combat style
    style: CombatStyle = CombatStyle.AGGRESSIVE
    signature_move: CombatMove = CombatMove.GRAPPLE
    
    # Position
    is_pinned: bool = False
    is_restrained: bool = False
    is_mounted: bool = False
    is_penetrated: bool = False
    
    # Orgasm tracking
    orgasms_this_fight: int = 0
    orgasm_limit: int = 3         # Lose after this many
    
    # Record
    wins: int = 0
    losses: int = 0
    draws: int = 0
    
    @property
    def win_rate(self) -> float:
        """Calculate win rate."""
        total = self.wins + self.losses + self.draws
        return (self.wins / total * 100) if total > 0 else 0
    
    def take_stamina_damage(self, amount: int) -> Tuple[int, bool]:
        """
        Take stamina damage.
        Returns (damage_taken, is_exhausted).
        """
        actual = min(amount, self.current_stamina)
        self.current_stamina -= actual
        return actual, self.current_stamina <= 0
    
    def take_arousal(self, amount: int) -> Tuple[int, bool]:
        """
        Take arousal damage.
        Returns (arousal_gained, triggered_orgasm).
        """
        # Resistance reduces arousal gain
        resist_mult = 1 - (self.resistance / 200)
        actual = int(amount * resist_mult)
        
        self.current_arousal += actual
        
        if self.current_arousal >= self.max_arousal:
            self.current_arousal = 0
            self.orgasms_this_fight += 1
            return actual, True
        
        return actual, False
    
    def recover_arousal(self, amount: int = 0) -> int:
        """Recover from arousal."""
        if amount == 0:
            amount = self.recovery // 2
        
        recovered = min(amount, self.current_arousal)
        self.current_arousal -= recovered
        return recovered
    
    def reset_for_fight(self) -> None:
        """Reset stats for new fight."""
        self.current_stamina = self.max_stamina
        self.current_arousal = 0
        self.orgasms_this_fight = 0
        self.is_pinned = False
        self.is_restrained = False
        self.is_mounted = False
        self.is_penetrated = False
    
    def get_status(self) -> str:
        """Get fighter status."""
        lines = [f"=== {self.fighter_name} ==="]
        lines.append(f"Style: {self.style.value}")
        lines.append(f"Record: {self.wins}W - {self.losses}L - {self.draws}D ({self.win_rate:.0f}%)")
        
        lines.append(f"\n--- Stats ---")
        lines.append(f"STR: {self.strength} | AGI: {self.agility} | END: {self.endurance}")
        lines.append(f"TEC: {self.technique} | SED: {self.seduction} | RES: {self.resistance}")
        
        lines.append(f"\n--- Current ---")
        lines.append(f"Stamina: {self.current_stamina}/{self.max_stamina}")
        lines.append(f"Arousal: {self.current_arousal}/{self.max_arousal}")
        lines.append(f"Orgasms: {self.orgasms_this_fight}/{self.orgasm_limit}")
        
        status = []
        if self.is_pinned:
            status.append("PINNED")
        if self.is_restrained:
            status.append("RESTRAINED")
        if self.is_mounted:
            status.append("MOUNTED")
        if self.is_penetrated:
            status.append("PENETRATED")
        if status:
            lines.append(f"Status: {', '.join(status)}")
        
        return "\n".join(lines)
    
    def to_dict(self) -> dict:
        return {
            "fighter_id": self.fighter_id,
            "fighter_name": self.fighter_name,
            "strength": self.strength,
            "agility": self.agility,
            "endurance": self.endurance,
            "technique": self.technique,
            "seduction": self.seduction,
            "resistance": self.resistance,
            "recovery": self.recovery,
            "max_stamina": self.max_stamina,
            "max_arousal": self.max_arousal,
            "style": self.style.value,
            "wins": self.wins,
            "losses": self.losses,
            "draws": self.draws,
        }
    
    @classmethod
    def from_dict(cls, data: dict) -> "CombatStats":
        stats = cls()
        for key, value in data.items():
            if key == "style":
                stats.style = CombatStyle(value)
            elif hasattr(stats, key):
                setattr(stats, key, value)
        return stats


# =============================================================================
# COMBAT MOVES
# =============================================================================

@dataclass
class MoveResult:
    """Result of a combat move."""
    
    move: CombatMove = CombatMove.GRAPPLE
    success: bool = False
    
    stamina_damage: int = 0
    arousal_damage: int = 0
    
    caused_orgasm: bool = False
    caused_exhaustion: bool = False
    
    position_change: str = ""
    description: str = ""


MOVE_DATA = {
    # Physical moves
    CombatMove.GRAPPLE: {
        "stamina_cost": 10,
        "stamina_damage": 15,
        "arousal_damage": 5,
        "stat_check": "strength",
        "descriptions": [
            "wraps arms around opponent, squeezing tight",
            "tackles and grapples, bodies entangled",
            "locks in a powerful hold",
        ],
    },
    CombatMove.PIN: {
        "stamina_cost": 15,
        "stamina_damage": 10,
        "arousal_damage": 10,
        "stat_check": "strength",
        "requires_grappled": True,
        "sets_pinned": True,
        "descriptions": [
            "forces opponent down, pinning them beneath",
            "straddles and pins, holding wrists down",
            "presses full weight down, immobilizing",
        ],
    },
    CombatMove.STRIKE: {
        "stamina_cost": 8,
        "stamina_damage": 20,
        "arousal_damage": 0,
        "stat_check": "strength",
        "descriptions": [
            "lands a solid blow",
            "strikes with force",
            "delivers a punishing hit",
        ],
    },
    
    # Sexual moves
    CombatMove.GROPE: {
        "stamina_cost": 5,
        "stamina_damage": 0,
        "arousal_damage": 15,
        "stat_check": "seduction",
        "descriptions": [
            "hands roam over sensitive areas",
            "gropes and squeezes, teasing flesh",
            "finds and exploits sensitive spots",
        ],
    },
    CombatMove.KISS: {
        "stamina_cost": 5,
        "stamina_damage": 0,
        "arousal_damage": 20,
        "stat_check": "seduction",
        "descriptions": [
            "captures lips in a deep, demanding kiss",
            "forces a passionate kiss",
            "tongue invades mouth dominantly",
        ],
    },
    CombatMove.FINGER: {
        "stamina_cost": 8,
        "stamina_damage": 0,
        "arousal_damage": 25,
        "stat_check": "technique",
        "descriptions": [
            "fingers find their mark, working skillfully",
            "plunges fingers inside, pumping",
            "digits probe and stimulate mercilessly",
        ],
    },
    CombatMove.ORAL: {
        "stamina_cost": 12,
        "stamina_damage": 0,
        "arousal_damage": 35,
        "stat_check": "technique",
        "requires_pinned": True,
        "descriptions": [
            "mouth descends, tongue working",
            "licks and sucks with devastating skill",
            "oral assault overwhelms the senses",
        ],
    },
    CombatMove.MOUNT: {
        "stamina_cost": 15,
        "stamina_damage": 5,
        "arousal_damage": 20,
        "stat_check": "agility",
        "requires_pinned": True,
        "sets_mounted": True,
        "descriptions": [
            "straddles opponent, taking dominant position",
            "mounts and grinds down",
            "sits atop, asserting control",
        ],
    },
    CombatMove.PENETRATE: {
        "stamina_cost": 20,
        "stamina_damage": 10,
        "arousal_damage": 40,
        "stat_check": "strength",
        "requires_mounted": True,
        "sets_penetrated": True,
        "descriptions": [
            "thrusts inside with a single powerful motion",
            "hilts completely, filling utterly",
            "penetrates deep, claiming completely",
        ],
    },
    CombatMove.FORCE_ORGASM: {
        "stamina_cost": 25,
        "stamina_damage": 0,
        "arousal_damage": 50,
        "stat_check": "technique",
        "requires_penetrated": True,
        "descriptions": [
            "pounds relentlessly toward forced climax",
            "works body expertly toward inevitable orgasm",
            "drives toward completion with merciless skill",
        ],
    },
    
    # Control moves
    CombatMove.RESTRAIN: {
        "stamina_cost": 12,
        "stamina_damage": 5,
        "arousal_damage": 10,
        "stat_check": "technique",
        "sets_restrained": True,
        "descriptions": [
            "binds arms behind back",
            "restrains in an inescapable hold",
            "locks limbs in submission hold",
        ],
    },
    CombatMove.SPANK: {
        "stamina_cost": 8,
        "stamina_damage": 10,
        "arousal_damage": 15,
        "stat_check": "strength",
        "requires_pinned": True,
        "descriptions": [
            "hand cracks across ass cheek",
            "delivers punishing spanks",
            "reddens flesh with sharp slaps",
        ],
    },
    CombatMove.EDGE: {
        "stamina_cost": 15,
        "stamina_damage": 0,
        "arousal_damage": 30,
        "stat_check": "technique",
        "descriptions": [
            "brings to the edge then cruelly stops",
            "teases to near-orgasm then denies",
            "edges mercilessly, building unbearable need",
        ],
    },
    
    # Defensive
    CombatMove.ESCAPE: {
        "stamina_cost": 20,
        "stamina_damage": 0,
        "arousal_damage": 0,
        "stat_check": "agility",
        "clears_positions": True,
        "descriptions": [
            "wriggles free from the hold",
            "breaks away with sudden burst",
            "escapes the compromising position",
        ],
    },
    CombatMove.COUNTER: {
        "stamina_cost": 15,
        "stamina_damage": 15,
        "arousal_damage": 10,
        "stat_check": "technique",
        "descriptions": [
            "reverses the attack into an advantage",
            "counters and turns the tables",
            "uses momentum against attacker",
        ],
    },
    CombatMove.ENDURE: {
        "stamina_cost": 5,
        "stamina_damage": 0,
        "arousal_damage": -10,
        "stat_check": "endurance",
        "descriptions": [
            "grits teeth and endures",
            "focuses and resists the sensation",
            "holds on through sheer willpower",
        ],
    },
}


def execute_move(attacker: CombatStats, defender: CombatStats, move: CombatMove) -> MoveResult:
    """Execute a combat move."""
    result = MoveResult(move=move)
    move_data = MOVE_DATA.get(move, {})
    
    # Check stamina cost
    cost = move_data.get("stamina_cost", 10)
    if attacker.current_stamina < cost:
        result.description = f"{attacker.fighter_name} is too exhausted!"
        return result
    
    # Check position requirements
    if move_data.get("requires_pinned") and not defender.is_pinned:
        result.description = "Target must be pinned first!"
        return result
    if move_data.get("requires_mounted") and not defender.is_mounted:
        result.description = "Must be mounted first!"
        return result
    if move_data.get("requires_penetrated") and not defender.is_penetrated:
        result.description = "Must be penetrating first!"
        return result
    
    # Pay stamina cost
    attacker.current_stamina -= cost
    
    # Calculate success chance
    stat_name = move_data.get("stat_check", "strength")
    attacker_stat = getattr(attacker, stat_name, 50)
    defender_stat = getattr(defender, stat_name, 50)
    
    # Style modifiers
    style_bonus = 0
    if attacker.style == CombatStyle.AGGRESSIVE and move in [CombatMove.STRIKE, CombatMove.GRAPPLE]:
        style_bonus = 15
    elif attacker.style == CombatStyle.SEDUCTIVE and move in [CombatMove.GROPE, CombatMove.KISS, CombatMove.FINGER]:
        style_bonus = 15
    elif attacker.style == CombatStyle.DOMINANT and move in [CombatMove.PIN, CombatMove.RESTRAIN, CombatMove.MOUNT]:
        style_bonus = 15
    elif attacker.style == CombatStyle.TECHNICAL and move in [CombatMove.COUNTER, CombatMove.EDGE, CombatMove.ORAL]:
        style_bonus = 15
    
    # Roll for success
    attack_roll = random.randint(1, 100) + attacker_stat + style_bonus
    defense_roll = random.randint(1, 100) + defender_stat
    
    if attack_roll > defense_roll:
        result.success = True
        
        # Apply damage
        result.stamina_damage = move_data.get("stamina_damage", 0)
        result.arousal_damage = move_data.get("arousal_damage", 0)
        
        # Seduction stat affects arousal damage
        if result.arousal_damage > 0:
            result.arousal_damage = int(result.arousal_damage * (attacker.seduction / 50))
        
        # Apply to defender
        if result.stamina_damage > 0:
            _, exhausted = defender.take_stamina_damage(result.stamina_damage)
            result.caused_exhaustion = exhausted
        
        if result.arousal_damage > 0:
            _, orgasmed = defender.take_arousal(result.arousal_damage)
            result.caused_orgasm = orgasmed
        elif result.arousal_damage < 0:
            # Healing/recovery move
            defender.recover_arousal(abs(result.arousal_damage))
        
        # Set positions
        if move_data.get("sets_pinned"):
            defender.is_pinned = True
            result.position_change = "PINNED"
        if move_data.get("sets_mounted"):
            defender.is_mounted = True
            result.position_change = "MOUNTED"
        if move_data.get("sets_penetrated"):
            defender.is_penetrated = True
            result.position_change = "PENETRATED"
        if move_data.get("sets_restrained"):
            defender.is_restrained = True
            result.position_change = "RESTRAINED"
        if move_data.get("clears_positions"):
            defender.is_pinned = False
            defender.is_mounted = False
            defender.is_penetrated = False
            defender.is_restrained = False
            result.position_change = "ESCAPED"
        
        # Get description
        descriptions = move_data.get("descriptions", ["attacks"])
        result.description = f"{attacker.fighter_name} {random.choice(descriptions)}"
        
        if result.caused_orgasm:
            result.description += f"\n{defender.fighter_name} CUMS! (Orgasm {defender.orgasms_this_fight}/{defender.orgasm_limit})"
        
    else:
        result.description = f"{attacker.fighter_name} attempts {move.value} but {defender.fighter_name} evades!"
    
    return result


# =============================================================================
# FIGHT
# =============================================================================

@dataclass
class Fight:
    """A single fight."""
    
    fight_id: str = ""
    
    # Fighters
    fighter1: Optional[CombatStats] = None
    fighter2: Optional[CombatStats] = None
    
    # Fight settings
    arena_type: ArenaType = ArenaType.STANDARD
    defeat_condition: DefeatCondition = DefeatCondition.ORGASM
    defeat_consequence: DefeatConsequence = DefeatConsequence.NONE
    
    # State
    is_active: bool = False
    round_number: int = 0
    current_turn: int = 1         # 1 or 2
    
    # Results
    winner: Optional[CombatStats] = None
    loser: Optional[CombatStats] = None
    finish_method: Optional[DefeatCondition] = None
    
    # Log
    fight_log: List[str] = field(default_factory=list)
    
    # Betting
    total_bets_fighter1: int = 0
    total_bets_fighter2: int = 0
    
    def start_fight(self) -> str:
        """Start the fight."""
        if not self.fighter1 or not self.fighter2:
            return "Need two fighters!"
        
        self.is_active = True
        self.round_number = 1
        self.current_turn = 1
        
        self.fighter1.reset_for_fight()
        self.fighter2.reset_for_fight()
        
        intro = f"=== FIGHT START ===\n"
        intro += f"{self.fighter1.fighter_name} vs {self.fighter2.fighter_name}\n"
        intro += f"Arena: {self.arena_type.value}\n"
        intro += f"Win Condition: {self.defeat_condition.value}\n"
        intro += f"Stakes: {self.defeat_consequence.value}"
        
        self.fight_log.append(intro)
        
        return intro
    
    def execute_turn(self, move: CombatMove) -> str:
        """Execute current fighter's turn."""
        if not self.is_active:
            return "Fight not active."
        
        attacker = self.fighter1 if self.current_turn == 1 else self.fighter2
        defender = self.fighter2 if self.current_turn == 1 else self.fighter1
        
        result = execute_move(attacker, defender, move)
        
        self.fight_log.append(f"R{self.round_number}: {result.description}")
        
        # Check for fight end
        end_msg = self._check_fight_end()
        if end_msg:
            return f"{result.description}\n\n{end_msg}"
        
        # Switch turns
        if self.current_turn == 1:
            self.current_turn = 2
        else:
            self.current_turn = 1
            self.round_number += 1
        
        return result.description
    
    def _check_fight_end(self) -> Optional[str]:
        """Check if fight should end."""
        for fighter, opponent in [(self.fighter1, self.fighter2), (self.fighter2, self.fighter1)]:
            # Orgasm defeat
            if self.defeat_condition == DefeatCondition.ORGASM:
                if fighter.orgasms_this_fight >= fighter.orgasm_limit:
                    return self._end_fight(opponent, fighter, DefeatCondition.ORGASM)
            
            # Exhaustion defeat
            if self.defeat_condition == DefeatCondition.EXHAUSTION:
                if fighter.current_stamina <= 0:
                    return self._end_fight(opponent, fighter, DefeatCondition.EXHAUSTION)
            
            # Submission (check arousal + exhaustion)
            if self.defeat_condition == DefeatCondition.SUBMISSION:
                if fighter.current_stamina < 20 and fighter.current_arousal > 80:
                    return self._end_fight(opponent, fighter, DefeatCondition.SUBMISSION)
        
        return None
    
    def _end_fight(self, winner: CombatStats, loser: CombatStats, method: DefeatCondition) -> str:
        """End the fight."""
        self.is_active = False
        self.winner = winner
        self.loser = loser
        self.finish_method = method
        
        winner.wins += 1
        loser.losses += 1
        
        msg = f"\n{'='*40}\n"
        msg += f"WINNER: {winner.fighter_name}!\n"
        msg += f"By: {method.value.upper()}\n"
        msg += f"Rounds: {self.round_number}\n"
        msg += f"{'='*40}\n"
        
        # Apply consequences
        if self.defeat_consequence != DefeatConsequence.NONE:
            msg += f"\nConsequence: {loser.fighter_name} will be {self.defeat_consequence.value}!"
        
        self.fight_log.append(msg)
        
        return msg
    
    def get_state(self) -> str:
        """Get current fight state."""
        if not self.is_active:
            return "No active fight."
        
        lines = [f"=== Round {self.round_number} ==="]
        
        for i, fighter in enumerate([self.fighter1, self.fighter2], 1):
            turn_marker = ">>>" if self.current_turn == i else "   "
            lines.append(f"\n{turn_marker} {fighter.fighter_name}")
            lines.append(f"    Stamina: {fighter.current_stamina}/{fighter.max_stamina}")
            lines.append(f"    Arousal: {fighter.current_arousal}/{fighter.max_arousal}")
            lines.append(f"    Orgasms: {fighter.orgasms_this_fight}/{fighter.orgasm_limit}")
            
            status = []
            if fighter.is_pinned:
                status.append("PINNED")
            if fighter.is_mounted:
                status.append("MOUNTED")
            if fighter.is_penetrated:
                status.append("PENETRATED")
            if status:
                lines.append(f"    Status: {', '.join(status)}")
        
        return "\n".join(lines)


# =============================================================================
# BETTING
# =============================================================================

@dataclass
class Bet:
    """A bet on a fight."""
    
    bet_id: str = ""
    bettor_dbref: str = ""
    bettor_name: str = ""
    
    fight_id: str = ""
    fighter_picked: str = ""      # Fighter name
    
    amount: int = 0
    odds: float = 1.0             # Payout multiplier
    
    is_resolved: bool = False
    won: bool = False
    payout: int = 0


@dataclass
class BettingPool:
    """Manages betting for fights."""
    
    pool_id: str = ""
    fight_id: str = ""
    
    # Fighters
    fighter1_name: str = ""
    fighter2_name: str = ""
    
    # Bets
    bets: List[Bet] = field(default_factory=list)
    total_pool: int = 0
    fighter1_total: int = 0
    fighter2_total: int = 0
    
    # Status
    is_open: bool = True
    
    def calculate_odds(self, fighter_name: str) -> float:
        """Calculate current odds for a fighter."""
        if self.total_pool == 0:
            return 2.0  # Even odds
        
        if fighter_name == self.fighter1_name:
            other_total = self.fighter2_total
        else:
            other_total = self.fighter1_total
        
        # Odds = total pool / amount bet on this fighter
        fighter_total = self.total_pool - other_total
        if fighter_total == 0:
            return 2.0
        
        return self.total_pool / fighter_total
    
    def place_bet(self, bettor_dbref: str, bettor_name: str, fighter_name: str, amount: int) -> Tuple[bool, str]:
        """Place a bet."""
        if not self.is_open:
            return False, "Betting is closed."
        
        if fighter_name not in [self.fighter1_name, self.fighter2_name]:
            return False, "Invalid fighter."
        
        odds = self.calculate_odds(fighter_name)
        
        bet = Bet(
            bet_id=f"BET-{datetime.now().strftime('%H%M%S')}-{random.randint(100, 999)}",
            bettor_dbref=bettor_dbref,
            bettor_name=bettor_name,
            fight_id=self.fight_id,
            fighter_picked=fighter_name,
            amount=amount,
            odds=odds,
        )
        
        self.bets.append(bet)
        self.total_pool += amount
        
        if fighter_name == self.fighter1_name:
            self.fighter1_total += amount
        else:
            self.fighter2_total += amount
        
        return True, f"Bet placed: {amount}g on {fighter_name} at {odds:.2f}x odds"
    
    def resolve(self, winner_name: str) -> List[Tuple[str, int]]:
        """
        Resolve all bets.
        Returns list of (bettor_name, payout).
        """
        self.is_open = False
        payouts = []
        
        for bet in self.bets:
            bet.is_resolved = True
            
            if bet.fighter_picked == winner_name:
                bet.won = True
                bet.payout = int(bet.amount * bet.odds)
                payouts.append((bet.bettor_name, bet.payout))
            else:
                bet.won = False
                bet.payout = 0
        
        return payouts
    
    def get_status(self) -> str:
        """Get betting pool status."""
        lines = [f"=== Betting Pool ==="]
        lines.append(f"Fight: {self.fighter1_name} vs {self.fighter2_name}")
        lines.append(f"Status: {'OPEN' if self.is_open else 'CLOSED'}")
        lines.append(f"Total Pool: {self.total_pool}g")
        
        odds1 = self.calculate_odds(self.fighter1_name)
        odds2 = self.calculate_odds(self.fighter2_name)
        
        lines.append(f"\n{self.fighter1_name}: {self.fighter1_total}g ({odds1:.2f}x)")
        lines.append(f"{self.fighter2_name}: {self.fighter2_total}g ({odds2:.2f}x)")
        
        lines.append(f"\nBets Placed: {len(self.bets)}")
        
        return "\n".join(lines)


# =============================================================================
# TOURNAMENT
# =============================================================================

@dataclass
class TournamentMatch:
    """A match in a tournament."""
    
    match_id: str = ""
    round_number: int = 1
    match_number: int = 1
    
    fighter1_id: str = ""
    fighter2_id: str = ""
    winner_id: str = ""
    
    is_complete: bool = False


@dataclass
class Tournament:
    """A tournament bracket."""
    
    tournament_id: str = ""
    name: str = ""
    
    # Settings
    defeat_condition: DefeatCondition = DefeatCondition.ORGASM
    defeat_consequence: DefeatConsequence = DefeatConsequence.CLAIMED
    
    # Participants
    participants: Dict[str, CombatStats] = field(default_factory=dict)
    
    # Bracket
    matches: List[TournamentMatch] = field(default_factory=list)
    current_round: int = 1
    
    # Prize
    prize_gold: int = 1000
    prize_description: str = ""
    
    # Status
    is_active: bool = False
    is_complete: bool = False
    champion: str = ""
    
    def generate_bracket(self) -> str:
        """Generate tournament bracket."""
        fighters = list(self.participants.keys())
        random.shuffle(fighters)
        
        # Ensure power of 2
        while len(fighters) & (len(fighters) - 1) != 0:
            fighters.append("")  # Bye
        
        match_num = 1
        for i in range(0, len(fighters), 2):
            match = TournamentMatch(
                match_id=f"TM-{self.tournament_id}-{match_num}",
                round_number=1,
                match_number=match_num,
                fighter1_id=fighters[i],
                fighter2_id=fighters[i + 1] if i + 1 < len(fighters) else "",
            )
            
            # Handle byes
            if not match.fighter2_id:
                match.winner_id = match.fighter1_id
                match.is_complete = True
            
            self.matches.append(match)
            match_num += 1
        
        self.is_active = True
        
        return f"Bracket generated with {len(self.participants)} fighters!"
    
    def record_match_result(self, match_id: str, winner_id: str) -> str:
        """Record a match result."""
        for match in self.matches:
            if match.match_id == match_id:
                match.winner_id = winner_id
                match.is_complete = True
                
                # Check if round is complete
                round_matches = [m for m in self.matches if m.round_number == self.current_round]
                if all(m.is_complete for m in round_matches):
                    return self._advance_round()
                
                return f"Match recorded. {winner_id} advances."
        
        return "Match not found."
    
    def _advance_round(self) -> str:
        """Advance to next round."""
        # Get winners from current round
        winners = [m.winner_id for m in self.matches if m.round_number == self.current_round]
        
        if len(winners) == 1:
            # Tournament complete
            self.is_complete = True
            self.champion = winners[0]
            return f"TOURNAMENT COMPLETE! Champion: {self.champion}"
        
        self.current_round += 1
        
        # Create next round matches
        match_num = len(self.matches) + 1
        for i in range(0, len(winners), 2):
            match = TournamentMatch(
                match_id=f"TM-{self.tournament_id}-{match_num}",
                round_number=self.current_round,
                match_number=match_num,
                fighter1_id=winners[i],
                fighter2_id=winners[i + 1] if i + 1 < len(winners) else "",
            )
            self.matches.append(match)
            match_num += 1
        
        return f"Round {self.current_round} begins!"
    
    def get_bracket(self) -> str:
        """Get visual bracket."""
        lines = [f"=== {self.name} ==="]
        lines.append(f"Round: {self.current_round}")
        lines.append(f"Prize: {self.prize_gold}g")
        
        for round_num in range(1, self.current_round + 1):
            lines.append(f"\n--- Round {round_num} ---")
            round_matches = [m for m in self.matches if m.round_number == round_num]
            
            for match in round_matches:
                f1 = self.participants.get(match.fighter1_id)
                f2 = self.participants.get(match.fighter2_id)
                
                f1_name = f1.fighter_name if f1 else "BYE"
                f2_name = f2.fighter_name if f2 else "BYE"
                
                if match.is_complete:
                    winner = self.participants.get(match.winner_id)
                    w_name = winner.fighter_name if winner else "?"
                    lines.append(f"  {f1_name} vs {f2_name} -> Winner: {w_name}")
                else:
                    lines.append(f"  {f1_name} vs {f2_name} [PENDING]")
        
        if self.is_complete:
            lines.append(f"\n*** CHAMPION: {self.champion} ***")
        
        return "\n".join(lines)


# =============================================================================
# COMBAT MIXIN
# =============================================================================

class CombatMixin:
    """Mixin for fighters."""
    
    @property
    def combat_stats(self) -> CombatStats:
        """Get combat stats."""
        data = self.db.combat_stats
        if data:
            return CombatStats.from_dict(data)
        return CombatStats(fighter_id=self.dbref, fighter_name=self.key)
    
    @combat_stats.setter
    def combat_stats(self, stats: CombatStats) -> None:
        """Set combat stats."""
        self.db.combat_stats = stats.to_dict()
    
    @property
    def is_fighter(self) -> bool:
        """Check if registered as fighter."""
        return bool(self.db.combat_stats)


__all__ = [
    "CombatStyle",
    "CombatMove",
    "DefeatCondition",
    "DefeatConsequence",
    "ArenaType",
    "CombatStats",
    "MoveResult",
    "MOVE_DATA",
    "execute_move",
    "Fight",
    "Bet",
    "BettingPool",
    "TournamentMatch",
    "Tournament",
    "CombatMixin",
    "ArenaCmdSet",
]

# Import commands
from .commands import ArenaCmdSet
