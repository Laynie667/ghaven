"""
Training Commands
=================

Commands for training and conditioning:
- Breaking resistance
- Conditioning behaviors
- Hypnosis
"""

from typing import Optional

# Evennia imports
try:
    from evennia import Command, CmdSet
    HAS_EVENNIA = True
except ImportError:
    HAS_EVENNIA = False
    class Command:
        key = ""
        aliases = []
        locks = ""
        help_category = ""
        def parse(self): pass
        def func(self): pass
    class CmdSet:
        def at_cmdset_creation(self): pass
        def add(self, cmd): pass


# =============================================================================
# HELPER FUNCTIONS
# =============================================================================

def find_target(caller, name: str):
    """Find a character by name."""
    if not name:
        return None
    
    candidates = caller.location.contents if caller.location else []
    
    for obj in candidates:
        if obj.key.lower() == name.lower():
            return obj
        if hasattr(obj, 'aliases') and name.lower() in [a.lower() for a in obj.aliases.all()]:
            return obj
    
    return None


# =============================================================================
# TRAINING COMMANDS
# =============================================================================

class CmdBreak(Command):
    """
    Work on breaking a subject's resistance.
    
    Usage:
      break <target> with <method>
      break <target> status
      break methods                - List available methods
      
    Examples:
      break Luna with spanking
      break Rex with verbal_degradation
      break Luna status
    """
    key = "break"
    aliases = ["train"]
    locks = "cmd:all()"
    help_category = "Training"
    
    def parse(self):
        args = self.args.strip()
        
        if args.lower() == "methods":
            self.show_methods = True
            self.target_name = ""
            self.method = ""
            self.show_status = False
        elif " with " in args.lower():
            parts = args.lower().split(" with ")
            self.target_name = parts[0].strip()
            self.method = parts[1].strip()
            self.show_methods = False
            self.show_status = False
        elif " status" in args.lower():
            self.target_name = args.lower().replace(" status", "").strip()
            self.show_status = True
            self.show_methods = False
            self.method = ""
        else:
            self.target_name = args
            self.method = ""
            self.show_methods = False
            self.show_status = False
    
    def func(self):
        from .training import (
            TRAINING_METHODS, TrainingSystem, 
            get_training_method, ResistanceState
        )
        
        # List methods
        if self.show_methods:
            lines = ["=== Training Methods ==="]
            for key, method in TRAINING_METHODS.items():
                targets = ", ".join([t.value for t in method.targets_resistance])
                lines.append(f"  {key}: {method.name}")
                lines.append(f"    Targets: {targets}")
                lines.append(f"    Reduction: {method.resistance_reduction}")
                if method.min_skill > 0:
                    lines.append(f"    Requires skill: {method.min_skill}")
            
            self.caller.msg("\n".join(lines))
            return
        
        if not self.target_name:
            self.caller.msg("Usage: break <target> with <method>")
            return
        
        target = find_target(self.caller, self.target_name)
        if not target:
            self.caller.msg(f"Can't find '{self.target_name}' here.")
            return
        
        # Show status
        if self.show_status:
            if hasattr(target, 'resistance_state'):
                state = target.resistance_state
                lines = [
                    f"=== {target.key}'s Training Status ===",
                    f"Stage: {state.get_stage().value}",
                    f"Total Resistance: {state.get_total_resistance()}%",
                    f"",
                    f"Physical: {state.physical}%",
                    f"Mental: {state.mental}%",
                    f"Emotional: {state.emotional}%",
                    f"Sexual: {state.sexual}%",
                ]
                self.caller.msg("\n".join(lines))
            else:
                self.caller.msg(f"{target.key} has no training data.")
            return
        
        if not self.method:
            self.caller.msg("What method? Try: break methods")
            return
        
        method = get_training_method(self.method)
        if not method:
            self.caller.msg(f"Unknown method: {self.method}. Try: break methods")
            return
        
        # Check skill
        trainer_skill = getattr(self.caller, 'training_skill', 1)
        if trainer_skill < method.min_skill:
            self.caller.msg(f"{method.name} requires training skill {method.min_skill}.")
            return
        
        # Get or create resistance state
        if hasattr(target, 'resistance_state'):
            resistance = target.resistance_state
        else:
            resistance = ResistanceState()
        
        # Start or get session
        session = TrainingSystem.start_session(self.caller, target)
        
        # Apply method
        success, message, changes = TrainingSystem.apply_method(
            session, resistance, self.method, intensity=5
        )
        
        if success:
            # Save state
            if hasattr(target, 'resistance_state'):
                target.resistance_state = resistance
            
            self.caller.msg(message)
            self.caller.location.msg_contents(
                f"{self.caller.key} applies {method.name} to {target.key}.",
                exclude=[self.caller]
            )
        else:
            self.caller.msg(message)


class CmdCondition(Command):
    """
    Condition a behavior into a subject.
    
    Usage:
      condition <target> <behavior>
      condition <target> list       - Show conditioned behaviors
      condition behaviors           - List available behaviors
      
    Examples:
      condition Luna kneel_on_command
      condition Rex address_master
    """
    key = "condition"
    locks = "cmd:all()"
    help_category = "Training"
    
    def parse(self):
        args = self.args.strip().split()
        
        if args and args[0].lower() == "behaviors":
            self.show_behaviors = True
            self.target_name = ""
            self.behavior = ""
            self.show_list = False
        elif len(args) >= 2:
            self.target_name = args[0]
            if args[1].lower() == "list":
                self.show_list = True
                self.behavior = ""
            else:
                self.behavior = args[1]
                self.show_list = False
            self.show_behaviors = False
        else:
            self.target_name = args[0] if args else ""
            self.behavior = ""
            self.show_behaviors = False
            self.show_list = False
    
    def func(self):
        from .training import (
            PRESET_BEHAVIORS, TrainingSystem, 
            get_preset_behavior, ConditionedBehavior
        )
        
        # List available behaviors
        if self.show_behaviors:
            lines = ["=== Available Behaviors ==="]
            for key, behavior in PRESET_BEHAVIORS.items():
                lines.append(f"  {key}: {behavior.name}")
                lines.append(f"    Type: {behavior.conditioning_type.value}")
                lines.append(f"    Trigger: {behavior.trigger}")
            
            self.caller.msg("\n".join(lines))
            return
        
        if not self.target_name:
            self.caller.msg("Usage: condition <target> <behavior>")
            return
        
        target = find_target(self.caller, self.target_name)
        if not target:
            self.caller.msg(f"Can't find '{self.target_name}' here.")
            return
        
        # Show existing conditioning
        if self.show_list:
            if hasattr(target, 'conditioned_behaviors'):
                behaviors = target.conditioned_behaviors
                if not behaviors:
                    self.caller.msg(f"{target.key} has no conditioned behaviors.")
                    return
                
                lines = [f"=== {target.key}'s Conditioned Behaviors ==="]
                for key, behavior in behaviors.items():
                    lines.append(f"  {behavior.name}: {behavior.strength}% strength")
                    if behavior.trigger:
                        lines.append(f"    Trigger: '{behavior.trigger}'")
                
                self.caller.msg("\n".join(lines))
            else:
                self.caller.msg(f"{target.key} cannot be conditioned.")
            return
        
        if not self.behavior:
            self.caller.msg("What behavior? Try: condition behaviors")
            return
        
        # Get behaviors dict
        if hasattr(target, 'conditioned_behaviors'):
            behaviors = target.conditioned_behaviors
        else:
            self.caller.msg(f"{target.key} cannot be conditioned.")
            return
        
        # Apply conditioning
        success, message = TrainingSystem.condition_behavior(
            behaviors, self.behavior, strength_gain=10
        )
        
        if success:
            target.conditioned_behaviors = behaviors
        
        self.caller.msg(message)


class CmdTrigger(Command):
    """
    Speak a trigger word to activate conditioned behaviors.
    
    Usage:
      trigger <word>
      
    This will check if any conditioned characters in the room
    respond to the trigger word.
    """
    key = "trigger"
    locks = "cmd:all()"
    help_category = "Training"
    
    def func(self):
        if not self.args.strip():
            self.caller.msg("Trigger what word?")
            return
        
        word = self.args.strip()
        
        # Announce the trigger word
        self.caller.location.msg_contents(
            f'{self.caller.key} speaks clearly: "{word}"'
        )
        
        # Check all characters in room
        for obj in self.caller.location.contents:
            if obj == self.caller:
                continue
            
            # Check conditioned behaviors
            if hasattr(obj, 'check_conditioned_response'):
                responses = obj.check_conditioned_response(word)
                for response in responses:
                    self.caller.location.msg_contents(response)
            
            # Check hypnotic triggers
            if hasattr(obj, 'check_hypnotic_triggers'):
                responses = obj.check_hypnotic_triggers(word)
                for response in responses:
                    self.caller.location.msg_contents(f"{obj.key} {response}")


# =============================================================================
# HYPNOSIS COMMANDS
# =============================================================================

class CmdHypnotize(Command):
    """
    Attempt to hypnotize a subject.
    
    Usage:
      hypnotize <target>
      hypnotize <target> with <technique>
      hypnotize techniques         - List techniques
      
    Examples:
      hypnotize Luna
      hypnotize Rex with progressive_relaxation
    """
    key = "hypnotize"
    aliases = ["entrance"]
    locks = "cmd:all()"
    help_category = "Training"
    
    def parse(self):
        args = self.args.strip()
        
        if args.lower() == "techniques":
            self.show_techniques = True
            self.target_name = ""
            self.technique = "eye_fixation"
        elif " with " in args.lower():
            parts = args.lower().split(" with ")
            self.target_name = parts[0].strip()
            self.technique = parts[1].strip()
            self.show_techniques = False
        else:
            self.target_name = args
            self.technique = "eye_fixation"
            self.show_techniques = False
    
    def func(self):
        from .hypnosis import (
            INDUCTION_TECHNIQUES, HypnosisSystem,
            get_induction, TranceState
        )
        
        # List techniques
        if self.show_techniques:
            lines = ["=== Induction Techniques ==="]
            for key, tech in INDUCTION_TECHNIQUES.items():
                lines.append(f"  {key}: {tech.name}")
                lines.append(f"    {tech.description}")
                lines.append(f"    Difficulty: {tech.difficulty}, Min Skill: {tech.min_skill}")
            
            self.caller.msg("\n".join(lines))
            return
        
        if not self.target_name:
            self.caller.msg("Usage: hypnotize <target>")
            return
        
        target = find_target(self.caller, self.target_name)
        if not target:
            self.caller.msg(f"Can't find '{self.target_name}' here.")
            return
        
        # Attempt induction
        success, message, trance = HypnosisSystem.attempt_induction(
            self.caller, target, self.technique
        )
        
        if success and trance:
            # Save trance state
            if hasattr(target, 'trance_state'):
                target.trance_state = trance
            
            # Track subject
            if hasattr(self.caller, 'add_subject'):
                self.caller.add_subject(target.dbref)
        
        self.caller.msg(message)
        
        if success:
            self.caller.location.msg_contents(
                f"{self.caller.key} begins hypnotizing {target.key}...",
                exclude=[self.caller, target]
            )
            target.msg(f"{self.caller.key}'s voice washes over you... {message}")


class CmdDeepen(Command):
    """
    Deepen a subject's trance.
    
    Usage:
      deepen <target>
    """
    key = "deepen"
    locks = "cmd:all()"
    help_category = "Training"
    
    def func(self):
        if not self.args.strip():
            self.caller.msg("Deepen whose trance?")
            return
        
        target = find_target(self.caller, self.args.strip())
        if not target:
            self.caller.msg(f"Can't find '{self.args.strip()}' here.")
            return
        
        from .hypnosis import HypnosisSystem
        
        if not hasattr(target, 'trance_state'):
            self.caller.msg(f"{target.key} cannot be hypnotized.")
            return
        
        trance = target.trance_state
        
        if not trance.is_in_trance():
            self.caller.msg(f"{target.key} is not in trance.")
            return
        
        if trance.hypnotist_dbref != self.caller.dbref:
            self.caller.msg(f"{target.key} is entranced by {trance.hypnotist_name}, not you.")
            return
        
        new_depth, message = HypnosisSystem.deepen_trance(trance, 15)
        target.trance_state = trance
        
        self.caller.msg(f"{target.key} {message}")
        target.msg(f"You sink deeper... {message}")


class CmdSuggest(Command):
    """
    Implant a hypnotic suggestion.
    
    Usage:
      suggest <target> <type> "<content>" [trigger "<word>"]
      suggest types                - List suggestion types
      
    Types: behavior, belief, sensation, emotion, trigger
    
    Examples:
      suggest Luna behavior "kneel when I snap my fingers" trigger "snap"
      suggest Rex emotion "feel aroused when collar is touched"
    """
    key = "suggest"
    aliases = ["implant"]
    locks = "cmd:all()"
    help_category = "Training"
    
    def parse(self):
        args = self.args.strip()
        
        if args.lower() == "types":
            self.show_types = True
            self.target_name = ""
            self.sug_type = ""
            self.content = ""
            self.trigger_word = ""
            return
        
        self.show_types = False
        
        # Parse complex command
        import re
        
        # Extract trigger word if present
        trigger_match = re.search(r'trigger\s+"([^"]+)"', args)
        if trigger_match:
            self.trigger_word = trigger_match.group(1)
            args = args[:trigger_match.start()].strip()
        else:
            self.trigger_word = ""
        
        # Extract content
        content_match = re.search(r'"([^"]+)"', args)
        if content_match:
            self.content = content_match.group(1)
            args = args[:content_match.start()].strip()
        else:
            self.content = ""
        
        # Remaining is target and type
        parts = args.split()
        self.target_name = parts[0] if parts else ""
        self.sug_type = parts[1] if len(parts) > 1 else "behavior"
    
    def func(self):
        from .hypnosis import (
            SuggestionType, HypnosisSystem
        )
        
        # List types
        if self.show_types:
            lines = ["=== Suggestion Types ==="]
            for stype in SuggestionType:
                lines.append(f"  {stype.value}")
            self.caller.msg("\n".join(lines))
            return
        
        if not self.target_name or not self.content:
            self.caller.msg('Usage: suggest <target> <type> "<content>"')
            return
        
        target = find_target(self.caller, self.target_name)
        if not target:
            self.caller.msg(f"Can't find '{self.target_name}' here.")
            return
        
        # Validate type
        try:
            suggestion_type = SuggestionType(self.sug_type.lower())
        except ValueError:
            valid = [t.value for t in SuggestionType]
            self.caller.msg(f"Valid types: {', '.join(valid)}")
            return
        
        # Check trance
        if not hasattr(target, 'trance_state'):
            self.caller.msg(f"{target.key} cannot be hypnotized.")
            return
        
        trance = target.trance_state
        
        if not trance.is_in_trance():
            self.caller.msg(f"{target.key} must be in trance to receive suggestions.")
            return
        
        if trance.hypnotist_dbref != self.caller.dbref:
            self.caller.msg(f"{target.key} is entranced by someone else.")
            return
        
        # Implant suggestion
        success, message, suggestion = HypnosisSystem.implant_suggestion(
            self.caller, target, trance,
            suggestion_type, self.content, self.trigger_word
        )
        
        if success and suggestion:
            # Save suggestion
            if hasattr(target, 'add_suggestion'):
                target.add_suggestion(suggestion)
            
            self.caller.msg(message)
            
            if self.trigger_word:
                self.caller.msg(f"Trigger word: '{self.trigger_word}'")
        else:
            self.caller.msg(message)


class CmdWake(Command):
    """
    Wake a subject from trance.
    
    Usage:
      wake <target>
    """
    key = "wake"
    aliases = ["awaken"]
    locks = "cmd:all()"
    help_category = "Training"
    
    def func(self):
        if not self.args.strip():
            self.caller.msg("Wake whom?")
            return
        
        target = find_target(self.caller, self.args.strip())
        if not target:
            self.caller.msg(f"Can't find '{self.args.strip()}' here.")
            return
        
        from .hypnosis import HypnosisSystem
        
        if not hasattr(target, 'trance_state'):
            self.caller.msg(f"{target.key} isn't hypnotized.")
            return
        
        trance = target.trance_state
        
        if not trance.is_in_trance():
            self.caller.msg(f"{target.key} isn't in trance.")
            return
        
        message = HypnosisSystem.wake_subject(trance)
        target.trance_state = trance
        
        # Remove from subjects
        if hasattr(self.caller, 'remove_subject'):
            self.caller.remove_subject(target.dbref)
        
        self.caller.msg(f"{target.key} {message}")
        target.msg(f"You {message}")
        
        self.caller.location.msg_contents(
            f"{target.key} wakes from their trance.",
            exclude=[self.caller, target]
        )


class CmdTranceStatus(Command):
    """
    Check a subject's trance status.
    
    Usage:
      trancestatus <target>
    """
    key = "trancestatus"
    aliases = ["hypnostatus"]
    locks = "cmd:all()"
    help_category = "Training"
    
    def func(self):
        if not self.args.strip():
            self.caller.msg("Check whose status?")
            return
        
        target = find_target(self.caller, self.args.strip())
        if not target:
            self.caller.msg(f"Can't find '{self.args.strip()}' here.")
            return
        
        if not hasattr(target, 'trance_state'):
            self.caller.msg(f"{target.key} has no hypnosis data.")
            return
        
        trance = target.trance_state
        
        lines = [
            f"=== {target.key}'s Hypnosis Status ===",
            f"Trance Depth: {trance.depth.value}",
            f"Susceptibility: {trance.susceptibility}%",
            f"Times Hypnotized: {trance.times_hypnotized}",
            f"Total Trance Time: {trance.total_trance_time} minutes",
        ]
        
        if trance.is_in_trance():
            lines.append(f"Hypnotist: {trance.hypnotist_name}")
        
        # Show suggestions if we're the hypnotist
        if hasattr(target, 'hypnotic_suggestions'):
            suggestions = target.hypnotic_suggestions
            active = [s for s in suggestions if s.is_active]
            
            if active:
                lines.append(f"\nActive Suggestions: {len(active)}")
                for sug in active[:5]:
                    lines.append(f"  - {sug.content[:40]}... ({sug.strength_value}%)")
        
        self.caller.msg("\n".join(lines))


# =============================================================================
# COMMAND SET
# =============================================================================

class TrainingCmdSet(CmdSet):
    """Command set for training."""
    
    key = "TrainingCmdSet"
    
    def at_cmdset_creation(self):
        # Training
        self.add(CmdBreak())
        self.add(CmdCondition())
        self.add(CmdTrigger())
        
        # Hypnosis
        self.add(CmdHypnotize())
        self.add(CmdDeepen())
        self.add(CmdSuggest())
        self.add(CmdWake())
        self.add(CmdTranceStatus())


__all__ = [
    "CmdBreak",
    "CmdCondition",
    "CmdTrigger",
    "CmdHypnotize",
    "CmdDeepen",
    "CmdSuggest",
    "CmdWake",
    "CmdTranceStatus",
    "TrainingCmdSet",
]
