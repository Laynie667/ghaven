"""
Arena Commands
==============

Commands for sexual combat, arena fights, tournaments, and betting.
"""

from evennia import Command, CmdSet
import random


class CmdFighterStatus(Command):
    """
    View fighter status.
    
    Usage:
        fighterstatus [target]
    
    Shows combat stats, record, and current state.
    """
    
    key = "fighterstatus"
    aliases = ["combatstat", "fstatus"]
    locks = "cmd:all()"
    
    def func(self):
        caller = self.caller
        
        target = caller
        if self.args:
            target = caller.search(self.args.strip())
            if not target:
                return
        
        if not hasattr(target, 'combat_stats'):
            caller.msg(f"{target.key} is not a fighter.")
            return
        
        stats = target.combat_stats
        caller.msg(stats.get_summary())


class CmdRegisterFighter(Command):
    """
    Register as an arena fighter.
    
    Usage:
        registerfighter <target>
        registerfighter <target> = <style>
    
    Styles: aggressive, defensive, seductive, dominant, submissive, wild, technical
    """
    
    key = "registerfighter"
    aliases = ["makefighter"]
    locks = "cmd:perm(Builder)"
    
    def func(self):
        caller = self.caller
        
        if not self.args:
            caller.msg("Register who?")
            return
        
        if "=" in self.args:
            target_name, style = self.args.split("=", 1)
            style = style.strip().upper()
        else:
            target_name = self.args
            style = "AGGRESSIVE"
        
        target = caller.search(target_name.strip())
        if not target:
            return
        
        if not hasattr(target, 'combat_stats'):
            caller.msg(f"{target.key} cannot be a fighter.")
            return
        
        from ..arena import CombatStats, CombatStyle
        
        try:
            combat_style = CombatStyle[style]
        except KeyError:
            caller.msg(f"Unknown style. Valid: {[s.value for s in CombatStyle]}")
            return
        
        stats = CombatStats(
            fighter_id=target.dbref,
            fighter_name=target.key,
            style=combat_style,
        )
        target.db.combat_stats = stats.to_dict()
        
        caller.msg(f"{target.key} registered as {combat_style.value} fighter.")
        target.msg(f"You are now registered as an arena fighter! Style: {combat_style.value}")


class CmdChallenge(Command):
    """
    Challenge someone to a fight.
    
    Usage:
        challenge <target>
    
    Issues a challenge for arena combat.
    """
    
    key = "challenge"
    aliases = ["fightme"]
    locks = "cmd:all()"
    
    def func(self):
        caller = self.caller
        
        if not self.args:
            caller.msg("Challenge who?")
            return
        
        target = caller.search(self.args.strip())
        if not target:
            return
        
        if not hasattr(caller, 'combat_stats') or not caller.is_fighter:
            caller.msg("You need to be a registered fighter.")
            return
        
        if not hasattr(target, 'combat_stats') or not target.is_fighter:
            caller.msg(f"{target.key} is not a registered fighter.")
            return
        
        # Store pending challenge
        target.db.pending_challenge = caller.dbref
        
        caller.location.msg_contents(
            f"{caller.key} challenges {target.key} to arena combat!"
        )
        target.msg(f"{caller.key} has challenged you! Use 'accept' or 'decline'.")


class CmdAcceptChallenge(Command):
    """
    Accept a challenge.
    
    Usage:
        accept
    """
    
    key = "accept"
    locks = "cmd:all()"
    
    def func(self):
        caller = self.caller
        
        challenger_dbref = caller.db.pending_challenge
        if not challenger_dbref:
            caller.msg("No pending challenge.")
            return
        
        challenger = caller.search(f"#{challenger_dbref}")
        if not challenger:
            caller.msg("Challenger not found.")
            caller.db.pending_challenge = None
            return
        
        caller.db.pending_challenge = None
        
        # Start fight
        from ..arena import Fight
        
        fight = Fight(
            fight_id=f"fight_{random.randint(1000, 9999)}",
            fighter1_id=challenger.dbref,
            fighter1_name=challenger.key,
            fighter2_id=caller.dbref,
            fighter2_name=caller.key,
        )
        
        # Store fight in room
        caller.location.db.active_fight = fight.to_dict()
        
        caller.location.msg_contents(
            f"\n{'='*50}\n"
            f"FIGHT BEGINS: {challenger.key} vs {caller.key}!\n"
            f"{'='*50}\n"
            f"Use 'move <action>' to attack. Available moves:\n"
            f"  grapple, pin, strike, grope, kiss, finger, mount, restrain, escape\n"
        )


class CmdDeclineChallenge(Command):
    """
    Decline a challenge.
    
    Usage:
        decline
    """
    
    key = "decline"
    locks = "cmd:all()"
    
    def func(self):
        caller = self.caller
        
        if not caller.db.pending_challenge:
            caller.msg("No pending challenge.")
            return
        
        caller.db.pending_challenge = None
        caller.location.msg_contents(f"{caller.key} declines the challenge.")


class CmdFightMove(Command):
    """
    Execute a combat move.
    
    Usage:
        move <action>
        move/list
    
    Actions: grapple, pin, throw, strike, grope, kiss, finger, 
             oral, mount, penetrate, restrain, choke, spank, edge, 
             force_orgasm, escape
    """
    
    key = "move"
    aliases = ["attack", "fmove"]
    locks = "cmd:all()"
    
    def func(self):
        caller = self.caller
        
        if "list" in self.switches:
            from ..arena import CombatMove
            moves = [m.value for m in CombatMove]
            caller.msg(f"Available moves: {', '.join(moves)}")
            return
        
        if not self.args:
            caller.msg("Usage: move <action>")
            return
        
        # Check for active fight
        fight_data = caller.location.db.active_fight
        if not fight_data:
            caller.msg("No active fight here.")
            return
        
        from ..arena import Fight, CombatMove, execute_move
        
        # Reconstruct fight (simplified)
        # In real implementation, would properly deserialize
        
        move_name = self.args.strip().upper()
        
        try:
            move = CombatMove[move_name]
        except KeyError:
            caller.msg(f"Unknown move. Use move/list.")
            return
        
        # Determine opponent
        if str(caller.dbref) == fight_data.get("fighter1_id"):
            opponent_id = fight_data.get("fighter2_id")
        elif str(caller.dbref) == fight_data.get("fighter2_id"):
            opponent_id = fight_data.get("fighter1_id")
        else:
            caller.msg("You're not in this fight.")
            return
        
        opponent = caller.search(f"#{opponent_id}")
        if not opponent:
            caller.msg("Opponent not found.")
            return
        
        # Get stats
        attacker_stats = caller.combat_stats
        defender_stats = opponent.combat_stats
        
        # Execute move
        result = execute_move(move, attacker_stats, defender_stats)
        
        # Update stats
        caller.db.combat_stats = attacker_stats.to_dict()
        opponent.db.combat_stats = defender_stats.to_dict()
        
        # Announce result
        caller.location.msg_contents(
            f"\n{caller.key} uses {move.value}!\n{result.description}"
        )
        
        if result.damage > 0:
            caller.location.msg_contents(
                f"  → {opponent.key} takes {result.damage} damage!"
            )
        if result.arousal_change > 0:
            caller.location.msg_contents(
                f"  → {opponent.key}'s arousal increases by {result.arousal_change}!"
            )
        
        # Check for victory conditions
        if defender_stats.arousal >= 100:
            caller.location.msg_contents(
                f"\n{'='*50}\n"
                f"{opponent.key} ORGASMS! {caller.key} WINS!\n"
                f"{'='*50}"
            )
            
            # Update records
            attacker_stats.wins += 1
            attacker_stats.current_streak += 1
            defender_stats.losses += 1
            defender_stats.current_streak = 0
            
            caller.db.combat_stats = attacker_stats.to_dict()
            opponent.db.combat_stats = defender_stats.to_dict()
            
            caller.location.db.active_fight = None


class CmdBet(Command):
    """
    Place a bet on a fight.
    
    Usage:
        bet <fighter> = <amount>
    
    Places a gold bet on a fighter.
    """
    
    key = "bet"
    aliases = ["wager"]
    locks = "cmd:all()"
    
    def func(self):
        caller = self.caller
        
        if "=" not in self.args:
            caller.msg("Usage: bet <fighter> = <amount>")
            return
        
        fighter_name, amount_str = self.args.split("=", 1)
        fighter = caller.search(fighter_name.strip())
        if not fighter:
            return
        
        try:
            amount = int(amount_str.strip())
        except ValueError:
            caller.msg("Amount must be a number.")
            return
        
        # Check wallet
        if hasattr(caller, 'wallet'):
            wallet = caller.wallet
            if wallet.gold < amount:
                caller.msg(f"You don't have {amount}g. Balance: {wallet.gold}g")
                return
            wallet.gold -= amount
            caller.wallet = wallet
        
        # Store bet
        fight_data = caller.location.db.active_fight
        if not fight_data:
            caller.msg("No active fight to bet on.")
            return
        
        if not caller.location.db.fight_bets:
            caller.location.db.fight_bets = {}
        
        caller.location.db.fight_bets[caller.dbref] = {
            "fighter": fighter.dbref,
            "amount": amount
        }
        
        caller.msg(f"Bet {amount}g on {fighter.key}!")
        caller.location.msg_contents(
            f"{caller.key} places a {amount}g bet on {fighter.key}!",
            exclude=[caller]
        )


class CmdCreateTournament(Command):
    """
    Create a tournament.
    
    Usage:
        createtournament <name> = <prize>
    
    Creates a new elimination tournament.
    """
    
    key = "createtournament"
    aliases = ["newtourney"]
    locks = "cmd:perm(Builder)"
    
    def func(self):
        caller = self.caller
        
        if "=" not in self.args:
            caller.msg("Usage: createtournament <name> = <prize>")
            return
        
        name, prize_str = self.args.split("=", 1)
        
        try:
            prize = int(prize_str.strip())
        except ValueError:
            prize = 1000
        
        from ..arena import Tournament
        
        tournament = Tournament(
            tournament_id=f"tourney_{random.randint(1000, 9999)}",
            name=name.strip(),
            prize_gold=prize,
        )
        
        caller.location.db.tournament = tournament.to_dict()
        
        caller.location.msg_contents(
            f"\n{'='*50}\n"
            f"TOURNAMENT ANNOUNCED: {name.strip()}\n"
            f"Prize: {prize}g\n"
            f"Use 'jointourney' to enter!\n"
            f"{'='*50}"
        )


class CmdJoinTournament(Command):
    """
    Join a tournament.
    
    Usage:
        jointourney
    
    Enters you in the active tournament.
    """
    
    key = "jointourney"
    aliases = ["entertourney"]
    locks = "cmd:all()"
    
    def func(self):
        caller = self.caller
        
        tourney_data = caller.location.db.tournament
        if not tourney_data:
            caller.msg("No active tournament here.")
            return
        
        if not hasattr(caller, 'combat_stats') or not caller.is_fighter:
            caller.msg("You must be a registered fighter.")
            return
        
        # Add to participants
        if "participants" not in tourney_data:
            tourney_data["participants"] = {}
        
        stats = caller.combat_stats
        tourney_data["participants"][caller.dbref] = {
            "name": caller.key,
            "wins": stats.wins,
            "losses": stats.losses,
        }
        
        caller.location.db.tournament = tourney_data
        
        num_fighters = len(tourney_data["participants"])
        caller.location.msg_contents(
            f"{caller.key} enters the tournament! ({num_fighters} fighters registered)"
        )


class CmdStartTournament(Command):
    """
    Start the tournament.
    
    Usage:
        starttourney
    
    Begins the tournament and generates brackets.
    """
    
    key = "starttourney"
    locks = "cmd:perm(Builder)"
    
    def func(self):
        caller = self.caller
        
        tourney_data = caller.location.db.tournament
        if not tourney_data:
            caller.msg("No tournament to start.")
            return
        
        participants = tourney_data.get("participants", {})
        if len(participants) < 2:
            caller.msg("Need at least 2 fighters.")
            return
        
        # Generate first round matches
        fighter_list = list(participants.items())
        random.shuffle(fighter_list)
        
        matches = []
        for i in range(0, len(fighter_list), 2):
            if i + 1 < len(fighter_list):
                matches.append({
                    "fighter1": fighter_list[i],
                    "fighter2": fighter_list[i + 1],
                    "winner": None
                })
            else:
                # Bye
                matches.append({
                    "fighter1": fighter_list[i],
                    "fighter2": ("BYE", {"name": "BYE"}),
                    "winner": fighter_list[i][0]
                })
        
        tourney_data["matches"] = matches
        tourney_data["current_round"] = 1
        tourney_data["is_active"] = True
        
        caller.location.db.tournament = tourney_data
        
        # Display bracket
        caller.location.msg_contents(
            f"\n{'='*50}\n"
            f"TOURNAMENT BEGINS!\n"
            f"{'='*50}\n"
            f"Round 1 Matches:"
        )
        
        for i, match in enumerate(matches):
            f1_name = match["fighter1"][1]["name"]
            f2_name = match["fighter2"][1]["name"]
            caller.location.msg_contents(f"  Match {i+1}: {f1_name} vs {f2_name}")


class CmdTournamentBracket(Command):
    """
    View tournament bracket.
    
    Usage:
        bracket
    """
    
    key = "bracket"
    aliases = ["tourneybracket"]
    locks = "cmd:all()"
    
    def func(self):
        caller = self.caller
        
        tourney_data = caller.location.db.tournament
        if not tourney_data:
            caller.msg("No active tournament.")
            return
        
        caller.msg(f"=== {tourney_data.get('name', 'Tournament')} ===")
        caller.msg(f"Prize: {tourney_data.get('prize_gold', 0)}g")
        caller.msg(f"Round: {tourney_data.get('current_round', 0)}")
        
        matches = tourney_data.get("matches", [])
        for i, match in enumerate(matches):
            f1_name = match["fighter1"][1]["name"]
            f2_name = match["fighter2"][1]["name"]
            winner = match.get("winner")
            
            if winner:
                winner_name = tourney_data["participants"].get(winner, {}).get("name", "?")
                caller.msg(f"  Match {i+1}: {f1_name} vs {f2_name} → Winner: {winner_name}")
            else:
                caller.msg(f"  Match {i+1}: {f1_name} vs {f2_name} [PENDING]")


class CmdFighterRecord(Command):
    """
    View win/loss record.
    
    Usage:
        record [target]
    """
    
    key = "record"
    aliases = ["fightrecord"]
    locks = "cmd:all()"
    
    def func(self):
        caller = self.caller
        
        target = caller
        if self.args:
            target = caller.search(self.args.strip())
            if not target:
                return
        
        if not hasattr(target, 'combat_stats'):
            caller.msg(f"{target.key} is not a fighter.")
            return
        
        stats = target.combat_stats
        
        total = stats.wins + stats.losses
        win_rate = (stats.wins / total * 100) if total > 0 else 0
        
        caller.msg(f"=== {target.key}'s Record ===")
        caller.msg(f"Wins: {stats.wins}")
        caller.msg(f"Losses: {stats.losses}")
        caller.msg(f"Win Rate: {win_rate:.1f}%")
        caller.msg(f"Current Streak: {stats.current_streak}")
        caller.msg(f"Best Streak: {stats.best_streak}")


class ArenaCmdSet(CmdSet):
    """Commands for arena combat system."""
    
    key = "arena_cmdset"
    
    def at_cmdset_creation(self):
        self.add(CmdFighterStatus())
        self.add(CmdRegisterFighter())
        self.add(CmdChallenge())
        self.add(CmdAcceptChallenge())
        self.add(CmdDeclineChallenge())
        self.add(CmdFightMove())
        self.add(CmdBet())
        self.add(CmdCreateTournament())
        self.add(CmdJoinTournament())
        self.add(CmdStartTournament())
        self.add(CmdTournamentBracket())
        self.add(CmdFighterRecord())
