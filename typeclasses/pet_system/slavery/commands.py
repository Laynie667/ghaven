"""
Slavery Commands
================

Commands for the slavery system.
"""

from evennia import Command, CmdSet
from evennia.utils.utils import inherits_from


# =============================================================================
# ACQUISITION COMMANDS
# =============================================================================

class CmdCapture(Command):
    """
    Attempt to capture someone.
    
    Usage:
      capture <target>
      capture <target> with <method>
    
    Methods: ambush, net, combat, subdue
    """
    key = "capture"
    locks = "cmd:all()"
    
    def func(self):
        if not self.args:
            self.caller.msg("Capture who?")
            return
        
        args = self.args.strip()
        method = "subdued"
        
        if " with " in args:
            target_name, method = args.split(" with ", 1)
        else:
            target_name = args
        
        target = self.caller.search(target_name)
        if not target:
            return
        
        # Import here to avoid circular imports
        from .acquisition import AcquisitionSystem, CaptureMethod
        
        # Get capture method
        try:
            cap_method = CaptureMethod(method.lower())
        except ValueError:
            cap_method = CaptureMethod.SUBDUED
        
        # Create acquisition record
        record = AcquisitionSystem.create_capture(
            captive=target,
            captor=self.caller,
            method=cap_method,
            location=self.caller.location.key if self.caller.location else "",
            resisted=True,
        )
        
        # Store on target
        if hasattr(target, 'acquisition_record'):
            target.acquisition_record = record
        
        # Update slave status
        if hasattr(target, 'slave_status'):
            status = target.slave_status
            status.enslave(self.caller.dbref, self.caller.key, "capture")
            target.save_slave_status(status)
        
        # Update owner
        if hasattr(self.caller, 'add_slave'):
            self.caller.add_slave(target.dbref)
        
        self.caller.msg(f"You capture {target.key}!")
        target.msg(f"You have been captured by {self.caller.key}!")
        
        if self.caller.location:
            self.caller.location.msg_contents(
                f"{self.caller.key} captures {target.key}!",
                exclude=[self.caller, target]
            )


class CmdEnslave(Command):
    """
    Enslave someone through various methods.
    
    Usage:
      enslave <target> debt <amount>
      enslave <target> sentence <crime> <days>
      enslave <target> purchase <amount>
    """
    key = "enslave"
    locks = "cmd:all()"
    
    def func(self):
        if not self.args:
            self.caller.msg("Usage: enslave <target> <method> [args]")
            return
        
        args = self.args.strip().split()
        if len(args) < 2:
            self.caller.msg("Specify a method: debt, sentence, purchase")
            return
        
        target = self.caller.search(args[0])
        if not target:
            return
        
        method = args[1].lower()
        
        from .acquisition import AcquisitionSystem, DebtType, SentenceType
        
        if method == "debt" and len(args) >= 3:
            try:
                amount = int(args[2])
            except ValueError:
                self.caller.msg("Amount must be a number.")
                return
            
            record = AcquisitionSystem.create_debt_slavery(
                debtor=target,
                creditor=self.caller,
                amount=amount,
            )
            
            if hasattr(target, 'acquisition_record'):
                target.acquisition_record = record
            
            if hasattr(target, 'slave_status'):
                status = target.slave_status
                status.enslave(self.caller.dbref, self.caller.key, "debt")
                status.remaining_debt = amount
                target.save_slave_status(status)
            
            self.caller.msg(f"{target.key} is now your debt slave for {amount} gold.")
            target.msg(f"You are now enslaved for a debt of {amount} gold.")
        
        elif method == "sentence" and len(args) >= 4:
            crime = args[2]
            try:
                days = int(args[3])
            except ValueError:
                self.caller.msg("Days must be a number.")
                return
            
            try:
                crime_type = SentenceType(crime.lower())
            except ValueError:
                crime_type = SentenceType.THEFT
            
            record = AcquisitionSystem.create_sentence(
                criminal=target,
                crime=crime_type,
                sentence_days=days,
                assigned_to=self.caller,
            )
            
            if hasattr(target, 'acquisition_record'):
                target.acquisition_record = record
            
            if hasattr(target, 'slave_status'):
                status = target.slave_status
                status.enslave(self.caller.dbref, self.caller.key, "sentence")
                status.remaining_sentence_days = days
                target.save_slave_status(status)
            
            self.caller.msg(f"{target.key} sentenced to {days} days of slavery.")
            target.msg(f"You have been sentenced to {days} days of slavery for {crime}.")
        
        else:
            self.caller.msg("Unknown method. Use: debt, sentence, purchase")


class CmdVolunteer(Command):
    """
    Voluntarily submit to slavery.
    
    Usage:
      volunteer to <master>
      volunteer to <master> for <days>
      volunteer to <master> permanent
    """
    key = "volunteer"
    locks = "cmd:all()"
    
    def func(self):
        if not self.args:
            self.caller.msg("Usage: volunteer to <master> [for <days>|permanent]")
            return
        
        args = self.args.strip()
        
        if not args.startswith("to "):
            self.caller.msg("Usage: volunteer to <master>")
            return
        
        args = args[3:]  # Remove "to "
        
        is_permanent = False
        days = 365
        
        if " permanent" in args:
            args = args.replace(" permanent", "")
            is_permanent = True
        elif " for " in args:
            parts = args.split(" for ")
            args = parts[0]
            try:
                days = int(parts[1].replace(" days", "").strip())
            except ValueError:
                days = 365
        
        master = self.caller.search(args)
        if not master:
            return
        
        from .acquisition import AcquisitionSystem, VoluntaryReason
        
        record = AcquisitionSystem.create_voluntary(
            submitter=self.caller,
            master=master,
            reason=VoluntaryReason.DESIRE,
            is_permanent=is_permanent,
            duration_days=days,
        )
        
        if hasattr(self.caller, 'acquisition_record'):
            self.caller.acquisition_record = record
        
        if hasattr(self.caller, 'slave_status'):
            status = self.caller.slave_status
            status.enslave(master.dbref, master.key, "voluntary")
            status.can_revoke = not is_permanent
            self.caller.save_slave_status(status)
        
        if hasattr(master, 'add_slave'):
            master.add_slave(self.caller.dbref)
        
        duration = "permanently" if is_permanent else f"for {days} days"
        self.caller.msg(f"You submit yourself to {master.key} {duration}.")
        master.msg(f"{self.caller.key} has submitted to you {duration}!")


class CmdFree(Command):
    """
    Free a slave.
    
    Usage:
      free <slave>
    """
    key = "free"
    aliases = ["manumit"]
    locks = "cmd:all()"
    
    def func(self):
        if not self.args:
            self.caller.msg("Free who?")
            return
        
        target = self.caller.search(self.args.strip())
        if not target:
            return
        
        if not hasattr(target, 'slave_status'):
            self.caller.msg("They don't have slave status tracking.")
            return
        
        status = target.slave_status
        
        if not status.is_slave:
            self.caller.msg(f"{target.key} is not a slave.")
            return
        
        if status.owner_dbref != self.caller.dbref:
            self.caller.msg(f"You don't own {target.key}.")
            return
        
        # Free them
        msg = status.free()
        target.save_slave_status(status)
        
        # Remove from owner's list
        if hasattr(self.caller, 'remove_slave'):
            self.caller.remove_slave(target.dbref)
        
        # Create manumission papers
        from .documentation import DocumentManager
        papers = DocumentManager.create_manumission(
            slave=target,
            former_owner=self.caller,
            registration_number=status.registration_number,
        )
        
        self.caller.msg(f"You have freed {target.key}.")
        target.msg(f"You have been granted freedom by {self.caller.key}!")


# =============================================================================
# PROCESSING COMMANDS
# =============================================================================

class CmdProcess(Command):
    """
    Begin or continue processing a slave.
    
    Usage:
      process <target> intake
      process <target> examine physical|sexual|mental
      process <target> test
      process <target> classify
      process <target> status
    """
    key = "process"
    locks = "cmd:all()"
    
    def func(self):
        if not self.args:
            self.caller.msg("Usage: process <target> <action>")
            return
        
        args = self.args.strip().split()
        if len(args) < 2:
            self.caller.msg("Specify an action: intake, examine, test, classify, status")
            return
        
        target = self.caller.search(args[0])
        if not target:
            return
        
        action = args[1].lower()
        
        from .processing import ProcessingSystem, ProcessingStage
        
        if action == "intake":
            record = ProcessingSystem.begin_intake(
                subject=target,
                facility="",
            )
            
            if hasattr(target, 'processing_record'):
                target.processing_record = record
            
            self.caller.msg(f"Intake begun for {target.key}.")
            target.msg("You are being processed for intake.")
        
        elif action == "examine":
            if len(args) < 3:
                self.caller.msg("Examine type: physical, sexual, mental")
                return
            
            exam_type = args[2].lower()
            
            # Get or create processing record
            if hasattr(target, 'processing_record') and target.processing_record:
                record = target.processing_record
            else:
                record = ProcessingSystem.begin_intake(target)
            
            if exam_type == "physical":
                exam = ProcessingSystem.perform_physical_exam(record, self.caller.key)
                self.caller.msg(f"Physical examination complete.\n"
                              f"Appearance: {exam.get_appearance_score()}/100\n"
                              f"Fitness: {exam.get_fitness_score()}/100")
            
            elif exam_type == "sexual":
                exam = ProcessingSystem.perform_sexual_exam(record, self.caller.key)
                self.caller.msg(f"Sexual examination complete.\n"
                              f"Sexual value: {exam.get_sexual_value_score()}/100\n"
                              f"Virginity: {exam.virginity}")
            
            elif exam_type == "mental":
                exam = ProcessingSystem.perform_mental_exam(record, self.caller.key)
                self.caller.msg(f"Mental examination complete.\n"
                              f"Trainability: {exam.get_trainability_score()}/100\n"
                              f"Break difficulty: {exam.estimated_break_difficulty}/100")
            
            if hasattr(target, 'processing_record'):
                target.processing_record = record
            
            target.msg(f"You undergo a {exam_type} examination.")
        
        elif action == "test":
            if hasattr(target, 'processing_record') and target.processing_record:
                record = target.processing_record
            else:
                self.caller.msg("Must perform examinations first.")
                return
            
            test = ProcessingSystem.perform_aptitude_testing(record, self.caller.key)
            
            if hasattr(target, 'processing_record'):
                target.processing_record = record
            
            self.caller.msg(f"Aptitude testing complete.\n"
                          f"Recommended track: {test.primary_recommendation}\n"
                          f"Aptitudes: {test.aptitudes}")
            target.msg("Your aptitudes have been tested.")
        
        elif action == "classify":
            if hasattr(target, 'processing_record') and target.processing_record:
                record = target.processing_record
            else:
                self.caller.msg("Must complete testing first.")
                return
            
            classif = ProcessingSystem.perform_classification(record, self.caller.key)
            ProcessingSystem.complete_processing(record)
            
            if hasattr(target, 'processing_record'):
                target.processing_record = record
            
            # Update slave status
            if hasattr(target, 'slave_status'):
                status = target.slave_status
                status.training_track = classif.training_track.value
                status.value_grade = classif.value_grade.value
                status.current_value = classif.estimated_value
                target.save_slave_status(status)
            
            self.caller.msg(classif.get_classification_display())
            target.msg(f"You have been classified as: {classif.training_track.value}")
        
        elif action == "status":
            if hasattr(target, 'processing_record') and target.processing_record:
                record = target.processing_record
                self.caller.msg(record.get_status_display())
            else:
                self.caller.msg(f"{target.key} has no processing record.")
        
        else:
            self.caller.msg("Unknown action. Use: intake, examine, test, classify, status")


# =============================================================================
# DOCUMENT COMMANDS
# =============================================================================

class CmdRegister(Command):
    """
    Register a slave officially.
    
    Usage:
      register <slave> [track]
    """
    key = "register"
    locks = "cmd:all()"
    
    def func(self):
        if not self.args:
            self.caller.msg("Register who?")
            return
        
        args = self.args.strip().split()
        target = self.caller.search(args[0])
        if not target:
            return
        
        track = args[1] if len(args) > 1 else ""
        
        from .documentation import DocumentManager
        
        reg = DocumentManager.create_registration(
            slave=target,
            owner=self.caller,
            training_track=track,
        )
        
        if hasattr(target, 'slave_registration'):
            target.slave_registration = reg
        
        if hasattr(target, 'slave_status'):
            status = target.slave_status
            status.registration_number = reg.registration_number
            target.save_slave_status(status)
        
        self.caller.msg(reg.get_papers_display())
        target.msg(f"You have been registered as slave #{reg.registration_number}")


class CmdPapers(Command):
    """
    View slave papers and documents.
    
    Usage:
      papers [target]
      papers <target> registration
      papers <target> ownership
      papers <target> contract
    """
    key = "papers"
    aliases = ["documents", "docs"]
    locks = "cmd:all()"
    
    def func(self):
        if not self.args:
            target = self.caller
        else:
            args = self.args.strip().split()
            target = self.caller.search(args[0])
            if not target:
                return
        
        doc_type = "all"
        if len(self.args.strip().split()) > 1:
            doc_type = self.args.strip().split()[1].lower()
        
        output = []
        
        if doc_type in ["all", "registration"]:
            if hasattr(target, 'slave_registration') and target.slave_registration:
                output.append(target.slave_registration.get_papers_display())
        
        if doc_type in ["all", "ownership"]:
            if hasattr(target, 'ownership_certificate') and target.ownership_certificate:
                output.append(target.ownership_certificate.get_certificate_display())
        
        if doc_type in ["all", "contract"]:
            if hasattr(target, 'service_contract') and target.service_contract:
                output.append(target.service_contract.get_contract_display())
        
        if output:
            self.caller.msg("\n\n".join(output))
        else:
            self.caller.msg(f"No documents found for {target.key}.")


class CmdContract(Command):
    """
    Create or sign a contract.
    
    Usage:
      contract create <slave> <type> [days]
      contract sign <slave>
      contract view <slave>
    
    Types: debt, voluntary, lease, training
    """
    key = "contract"
    locks = "cmd:all()"
    
    def func(self):
        if not self.args:
            self.caller.msg("Usage: contract <create|sign|view> <slave> [args]")
            return
        
        args = self.args.strip().split()
        if len(args) < 2:
            self.caller.msg("Specify action and target.")
            return
        
        action = args[0].lower()
        target = self.caller.search(args[1])
        if not target:
            return
        
        from .documentation import ServiceContract, ContractType, DocumentStatus
        from datetime import datetime, timedelta
        import random
        
        if action == "create":
            contract_type = args[2] if len(args) > 2 else "voluntary"
            days = int(args[3]) if len(args) > 3 else 365
            
            try:
                ctype = ContractType(contract_type.lower())
            except ValueError:
                ctype = ContractType.VOLUNTARY
            
            contract = ServiceContract(
                contract_id=f"CON-{random.randint(10000, 99999)}",
                slave_dbref=target.dbref,
                slave_name=target.key,
                owner_dbref=self.caller.dbref,
                owner_name=self.caller.key,
                contract_type=ctype,
                start_date=datetime.now(),
                end_date=datetime.now() + timedelta(days=days),
                service_type=contract_type,
            )
            
            if hasattr(target, 'service_contract'):
                target.service_contract = contract
            
            self.caller.msg(f"Contract created for {target.key}.")
            self.caller.msg(contract.get_contract_display())
        
        elif action == "sign":
            if not hasattr(target, 'service_contract') or not target.service_contract:
                self.caller.msg("No contract exists.")
                return
            
            contract = target.service_contract
            
            # Determine who is signing
            if self.caller.dbref == contract.owner_dbref:
                msg = contract.sign_owner()
            elif self.caller.dbref == contract.slave_dbref:
                msg = contract.sign_slave()
            else:
                self.caller.msg("You are not party to this contract.")
                return
            
            target.service_contract = contract
            self.caller.msg(msg)
        
        elif action == "view":
            if hasattr(target, 'service_contract') and target.service_contract:
                self.caller.msg(target.service_contract.get_contract_display())
            else:
                self.caller.msg("No contract found.")
        
        else:
            self.caller.msg("Unknown action. Use: create, sign, view")


# =============================================================================
# TRAINING COMMANDS
# =============================================================================

class CmdTrain(Command):
    """
    Train a slave.
    
    Usage:
      train <slave> start <track>
      train <slave> session [hours]
      train <slave> status
    
    Tracks: hucow, pleasure, pony, breeding, house, pet, toy, concubine
    """
    key = "train"
    locks = "cmd:all()"
    
    def func(self):
        if not self.args:
            self.caller.msg("Usage: train <slave> <action>")
            return
        
        args = self.args.strip().split()
        if len(args) < 2:
            self.caller.msg("Specify an action: start, session, status")
            return
        
        target = self.caller.search(args[0])
        if not target:
            return
        
        action = args[1].lower()
        
        from .training_tracks import TrackSystem, TrackType, get_track
        
        if action == "start":
            if len(args) < 3:
                tracks = [t.value for t in TrackType]
                self.caller.msg(f"Available tracks: {', '.join(tracks)}")
                return
            
            track_name = args[2].lower()
            
            try:
                track_type = TrackType(track_name)
            except ValueError:
                self.caller.msg(f"Unknown track: {track_name}")
                return
            
            progress = TrackSystem.start_track(
                subject=target,
                track_type=track_type,
                trainer=self.caller,
            )
            
            if hasattr(target, 'track_progress'):
                target.track_progress = progress
            
            if hasattr(target, 'slave_status'):
                status = target.slave_status
                status.training_track = track_name
                target.save_slave_status(status)
            
            track = get_track(track_name)
            self.caller.msg(f"Started {track.name} for {target.key}.")
            target.msg(f"Your training as a {track_name} begins.")
        
        elif action == "session":
            hours = int(args[2]) if len(args) > 2 else 1
            
            if not hasattr(target, 'track_progress') or not target.track_progress:
                self.caller.msg("No training in progress.")
                return
            
            progress = target.track_progress
            track = get_track(progress.track_type.value)
            
            if not track:
                self.caller.msg("Invalid track.")
                return
            
            msg, gains = TrackSystem.do_training(progress, hours)
            
            target.track_progress = progress
            
            if hasattr(target, 'slave_status'):
                status = target.slave_status
                status.training_days += 1
                target.save_slave_status(status)
            
            self.caller.msg(msg)
            if gains:
                gain_str = ", ".join(f"{k}: +{v}" for k, v in gains.items())
                self.caller.msg(f"Skill gains: {gain_str}")
            
            target.msg("You undergo a training session.")
        
        elif action == "status":
            if hasattr(target, 'track_progress') and target.track_progress:
                self.caller.msg(target.track_progress.get_progress_display())
            else:
                self.caller.msg("No training in progress.")
        
        else:
            self.caller.msg("Unknown action. Use: start, session, status")


# =============================================================================
# STATUS COMMANDS
# =============================================================================

class CmdSlaveStatus(Command):
    """
    View slave status.
    
    Usage:
      slavestatus [target]
    """
    key = "slavestatus"
    aliases = ["sstatus", "slavestat"]
    locks = "cmd:all()"
    
    def func(self):
        if not self.args:
            target = self.caller
        else:
            target = self.caller.search(self.args.strip())
            if not target:
                return
        
        if not hasattr(target, 'slave_status'):
            self.caller.msg("No slave status tracking available.")
            return
        
        status = target.slave_status
        self.caller.msg(status.get_status_display(target.key))


class CmdMySlaves(Command):
    """
    List your owned slaves.
    
    Usage:
      myslaves
    """
    key = "myslaves"
    aliases = ["slaves", "property"]
    locks = "cmd:all()"
    
    def func(self):
        if not hasattr(self.caller, 'get_slaves'):
            self.caller.msg("You can't own slaves.")
            return
        
        slaves = self.caller.get_slaves()
        
        if not slaves:
            self.caller.msg("You don't own any slaves.")
            return
        
        lines = [f"=== Your Slaves ({len(slaves)}) ==="]
        
        for slave in slaves:
            if hasattr(slave, 'slave_status'):
                status = slave.slave_status
                track = status.training_track or "untrained"
                grade = status.value_grade or "ungraded"
                lines.append(f"  {slave.key} - {track} ({grade})")
            else:
                lines.append(f"  {slave.key}")
        
        self.caller.msg("\n".join(lines))


class CmdBrand(Command):
    """
    Brand a slave.
    
    Usage:
      brand <slave> <location> <design>
    
    Locations: left_shoulder, right_shoulder, left_hip, right_hip,
               lower_back, inner_thigh, pubic, breast, buttock, neck
    """
    key = "brand"
    locks = "cmd:all()"
    
    def func(self):
        if not self.args:
            self.caller.msg("Usage: brand <slave> <location> <design>")
            return
        
        args = self.args.strip().split(None, 2)
        if len(args) < 3:
            self.caller.msg("Specify slave, location, and design.")
            return
        
        target = self.caller.search(args[0])
        if not target:
            return
        
        location = args[1]
        design = args[2]
        
        from .documentation import BrandRegistry, BrandLocation, BrandType
        import random
        
        try:
            brand_loc = BrandLocation(location.lower())
        except ValueError:
            locs = [l.value for l in BrandLocation]
            self.caller.msg(f"Valid locations: {', '.join(locs)}")
            return
        
        registry = BrandRegistry(
            registry_id=f"BRD-{random.randint(10000, 99999)}",
            slave_dbref=target.dbref,
            slave_name=target.key,
            brand_type=BrandType.BRAND,
            brand_location=brand_loc,
            brand_design=design,
            owner_dbref=self.caller.dbref,
            owner_name=self.caller.key,
        )
        
        if hasattr(target, 'brand_registry'):
            target.brand_registry = registry
        
        if hasattr(target, 'slave_status'):
            status = target.slave_status
            status.is_branded = True
            status.brand_location = location
            status.brand_design = design
            target.save_slave_status(status)
        
        self.caller.msg(f"You brand {target.key} on the {location} with: {design}")
        target.msg(f"You are branded on your {location}! The mark reads: {design}")


class CmdPunish(Command):
    """
    Punish a slave.
    
    Usage:
      punish <slave> [severity]
    
    Severity: 1-5 (default 2)
    """
    key = "punish"
    locks = "cmd:all()"
    
    def func(self):
        if not self.args:
            self.caller.msg("Punish who?")
            return
        
        args = self.args.strip().split()
        target = self.caller.search(args[0])
        if not target:
            return
        
        severity = 2
        if len(args) > 1:
            try:
                severity = min(5, max(1, int(args[1])))
            except ValueError:
                severity = 2
        
        if hasattr(target, 'slave_status'):
            status = target.slave_status
            status.add_punishment(severity)
            target.save_slave_status(status)
        
        punishments = {
            1: "a stern reprimand",
            2: "a firm spanking",
            3: "a severe beating",
            4: "time in the punishment cell",
            5: "an extended session of discipline",
        }
        
        self.caller.msg(f"You give {target.key} {punishments.get(severity, 'punishment')}.")
        target.msg(f"You receive {punishments.get(severity, 'punishment')} from {self.caller.key}.")


class CmdReward(Command):
    """
    Reward a slave.
    
    Usage:
      reward <slave>
    """
    key = "reward"
    locks = "cmd:all()"
    
    def func(self):
        if not self.args:
            self.caller.msg("Reward who?")
            return
        
        target = self.caller.search(self.args.strip())
        if not target:
            return
        
        if hasattr(target, 'slave_status'):
            status = target.slave_status
            status.add_reward()
            target.save_slave_status(status)
        
        self.caller.msg(f"You reward {target.key} for good behavior.")
        target.msg(f"You are rewarded by {self.caller.key}!")


# =============================================================================
# COMMAND SET
# =============================================================================

class SlaveryCmdSet(CmdSet):
    """Commands for slavery system."""
    
    key = "slavery_cmdset"
    
    def at_cmdset_creation(self):
        self.add(CmdCapture())
        self.add(CmdEnslave())
        self.add(CmdVolunteer())
        self.add(CmdFree())
        self.add(CmdProcess())
        self.add(CmdRegister())
        self.add(CmdPapers())
        self.add(CmdContract())
        self.add(CmdTrain())
        self.add(CmdSlaveStatus())
        self.add(CmdMySlaves())
        self.add(CmdBrand())
        self.add(CmdPunish())
        self.add(CmdReward())
