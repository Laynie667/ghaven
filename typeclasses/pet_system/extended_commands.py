"""
Extended System Commands
========================

Commands for modifications, breaking, public use, routines, and auctions.
"""

from evennia import Command, CmdSet


# =============================================================================
# MODIFICATION COMMANDS
# =============================================================================

class CmdEnhanceBreasts(Command):
    """
    Enhance a subject's breasts.
    
    Usage:
      enhancebreasts <target> <amount_cc>
      enhancebreasts <target> implants <size_cc> [silicone|saline]
    """
    key = "enhancebreasts"
    aliases = ["breastenhance", "growbreasts"]
    locks = "cmd:all()"
    
    def func(self):
        if not self.args:
            self.caller.msg("Usage: enhancebreasts <target> <amount>")
            return
        
        args = self.args.strip().split()
        target = self.caller.search(args[0])
        if not target:
            return
        
        from pet_systems.modifications import BodyModifications
        
        # Get or create mods
        if hasattr(target, 'body_mods'):
            mods = target.body_mods
        else:
            mods = BodyModifications(subject_dbref=target.dbref, subject_name=target.key)
        
        if len(args) >= 2 and args[1] == "implants":
            size = int(args[2]) if len(args) > 2 else 400
            implant_type = args[3] if len(args) > 3 else "silicone"
            msg = mods.breasts.add_implants(size, implant_type)
        else:
            amount = int(args[1]) if len(args) > 1 else 100
            msg = mods.breasts.increase_size(amount)
        
        target.body_mods = mods
        
        self.caller.msg(f"You enhance {target.key}'s breasts. {msg}")
        target.msg(f"Your breasts swell! {msg}")


class CmdMakeFuta(Command):
    """
    Give a subject a cock (futanari transformation).
    
    Usage:
      makefuta <target> [length_cm] [with balls]
    """
    key = "makefuta"
    aliases = ["futafy", "addcock"]
    locks = "cmd:all()"
    
    def func(self):
        if not self.args:
            self.caller.msg("Usage: makefuta <target> [length]")
            return
        
        args = self.args.strip().split()
        target = self.caller.search(args[0])
        if not target:
            return
        
        length = 18
        with_balls = True
        
        if len(args) > 1:
            try:
                length = int(args[1])
            except ValueError:
                pass
        
        if "no balls" in self.args.lower():
            with_balls = False
        
        from pet_systems.modifications import BodyModifications
        
        if hasattr(target, 'body_mods'):
            mods = target.body_mods
        else:
            mods = BodyModifications(subject_dbref=target.dbref, subject_name=target.key)
        
        msg = mods.genitals.add_penis(length, int(length * 0.7), with_balls)
        target.body_mods = mods
        
        self.caller.msg(f"You transform {target.key}. {msg}")
        target.msg(f"Your body changes! {msg}")


class CmdPierce(Command):
    """
    Pierce a subject.
    
    Usage:
      pierce <target> <location>
    
    Locations: nipple, clit, nose_ring, tongue, etc.
    """
    key = "pierce"
    locks = "cmd:all()"
    
    def func(self):
        if not self.args:
            self.caller.msg("Usage: pierce <target> <location>")
            return
        
        args = self.args.strip().split(None, 1)
        target = self.caller.search(args[0])
        if not target:
            return
        
        location = args[1] if len(args) > 1 else "nipple_both"
        
        from pet_systems.modifications import BodyModifications, Piercing, PiercingLocation
        
        try:
            loc = PiercingLocation(location.lower())
        except ValueError:
            locs = [l.value for l in PiercingLocation]
            self.caller.msg(f"Valid locations: {', '.join(locs)}")
            return
        
        if hasattr(target, 'body_mods'):
            mods = target.body_mods
        else:
            mods = BodyModifications(subject_dbref=target.dbref, subject_name=target.key)
        
        piercing = Piercing(
            piercing_id=f"PIERCE-{len(mods.piercings)+1}",
            location=loc,
            applied_by=self.caller.key,
        )
        
        msg = mods.add_piercing(piercing)
        target.body_mods = mods
        
        self.caller.msg(f"You pierce {target.key}. {msg}")
        target.msg(f"You are pierced! {msg}")


class CmdBodyMods(Command):
    """
    View body modifications.
    
    Usage:
      bodymods [target]
    """
    key = "bodymods"
    aliases = ["modifications", "mods"]
    locks = "cmd:all()"
    
    def func(self):
        if not self.args:
            target = self.caller
        else:
            target = self.caller.search(self.args.strip())
            if not target:
                return
        
        if not hasattr(target, 'body_mods'):
            self.caller.msg("No modification record.")
            return
        
        mods = target.body_mods
        self.caller.msg(mods.get_summary())


# =============================================================================
# BREAKING COMMANDS
# =============================================================================

class CmdBreak(Command):
    """
    Apply breaking methods to a subject.
    
    Usage:
      break <target> <method> [intensity]
    
    Methods: isolation, pain, pleasure, edging, denial, humiliation, etc.
    """
    key = "break"
    locks = "cmd:all()"
    
    def func(self):
        if not self.args:
            self.caller.msg("Usage: break <target> <method> [intensity]")
            return
        
        args = self.args.strip().split()
        target = self.caller.search(args[0])
        if not target:
            return
        
        method_name = args[1] if len(args) > 1 else "pain"
        intensity = int(args[2]) if len(args) > 2 else 50
        
        from pet_systems.breaking import MentalStatus, BreakingMethod
        
        try:
            method = BreakingMethod(method_name.lower())
        except ValueError:
            methods = [m.value for m in BreakingMethod]
            self.caller.msg(f"Valid methods: {', '.join(methods)}")
            return
        
        if hasattr(target, 'mental_status'):
            status = target.mental_status
        else:
            status = MentalStatus(subject_dbref=target.dbref, subject_name=target.key)
        
        msg, reduction = status.apply_breaking_method(method, intensity)
        target.mental_status = status
        
        self.caller.msg(f"You apply {method.value} to {target.key}.")
        self.caller.msg(msg)
        self.caller.msg(f"Resistance reduced by {reduction}. Now: {status.resistance}/100")
        
        target.msg(msg)


class CmdCondition(Command):
    """
    Install a conditioned trigger.
    
    Usage:
      condition <target> <stimulus> = <response>
    
    Example: condition slave kneel = kneel
    """
    key = "condition"
    aliases = ["installtrigger"]
    locks = "cmd:all()"
    
    def func(self):
        if not self.args or "=" not in self.args:
            self.caller.msg("Usage: condition <target> <stimulus> = <response>")
            return
        
        parts = self.args.strip().split("=")
        left = parts[0].strip().split()
        response_name = parts[1].strip()
        
        target = self.caller.search(left[0])
        if not target:
            return
        
        stimulus = " ".join(left[1:])
        
        from pet_systems.breaking import MentalStatus, TriggerType, ConditionedResponse
        
        try:
            response = ConditionedResponse(response_name.lower())
        except ValueError:
            responses = [r.value for r in ConditionedResponse]
            self.caller.msg(f"Valid responses: {', '.join(responses)}")
            return
        
        if hasattr(target, 'mental_status'):
            status = target.mental_status
        else:
            status = MentalStatus(subject_dbref=target.dbref, subject_name=target.key)
        
        trigger = status.install_trigger(
            TriggerType.WORD,
            stimulus,
            response,
            self.caller.key,
        )
        
        target.mental_status = status
        
        self.caller.msg(f"Trigger installed: '{stimulus}' → {response.value}")
        target.msg(f"Something changes in your mind...")


class CmdMentalStatus(Command):
    """
    View mental/breaking status.
    
    Usage:
      mentalstatus [target]
    """
    key = "mentalstatus"
    aliases = ["mstatus", "breakstatus"]
    locks = "cmd:all()"
    
    def func(self):
        if not self.args:
            target = self.caller
        else:
            target = self.caller.search(self.args.strip())
            if not target:
                return
        
        if hasattr(target, 'mental_status'):
            status = target.mental_status
            self.caller.msg(status.get_status_display())
        else:
            self.caller.msg("No mental status record.")


# =============================================================================
# PUBLIC USE COMMANDS
# =============================================================================

class CmdSetPublicUse(Command):
    """
    Set public use status.
    
    Usage:
      setpublicuse <target> <status>
    
    Status: private, available, free_use, breeding_stock, oral_only
    """
    key = "setpublicuse"
    aliases = ["publicuse"]
    locks = "cmd:all()"
    
    def func(self):
        if not self.args:
            self.caller.msg("Usage: setpublicuse <target> <status>")
            return
        
        args = self.args.strip().split()
        target = self.caller.search(args[0])
        if not target:
            return
        
        status_name = args[1] if len(args) > 1 else "available"
        
        from pet_systems.public_use import PublicUseRecord, PublicUseStatus
        
        try:
            new_status = PublicUseStatus(status_name.lower())
        except ValueError:
            statuses = [s.value for s in PublicUseStatus]
            self.caller.msg(f"Valid statuses: {', '.join(statuses)}")
            return
        
        if hasattr(target, 'public_use'):
            record = target.public_use
        else:
            record = PublicUseRecord(subject_dbref=target.dbref, subject_name=target.key)
        
        record.owner_dbref = self.caller.dbref
        record.owner_name = self.caller.key
        msg = record.set_status(new_status)
        
        target.public_use = record
        
        self.caller.msg(msg)
        target.msg(msg)
        
        if self.caller.location:
            self.caller.location.msg_contents(msg, exclude=[self.caller, target])


class CmdUse(Command):
    """
    Use someone who is available.
    
    Usage:
      use <target> [type]
    
    Types: oral, vaginal, anal, full
    """
    key = "use"
    locks = "cmd:all()"
    
    def func(self):
        if not self.args:
            self.caller.msg("Usage: use <target> [type]")
            return
        
        args = self.args.strip().split()
        target = self.caller.search(args[0])
        if not target:
            return
        
        use_type_name = args[1] if len(args) > 1 else "full"
        
        from pet_systems.public_use import PublicUseRecord, UseType, UsePosition
        
        try:
            use_type = UseType(use_type_name.lower())
        except ValueError:
            use_type = UseType.FULL
        
        if hasattr(target, 'public_use'):
            record = target.public_use
        else:
            self.caller.msg(f"{target.key} has no public use record.")
            return
        
        success, msg, session = record.begin_use(
            self.caller.dbref,
            self.caller.key,
            use_type,
            UsePosition.BENT_OVER,
        )
        
        if success:
            target.public_use = record
            self.caller.msg(msg)
            target.msg(msg)
            
            if self.caller.location:
                self.caller.location.msg_contents(msg, exclude=[self.caller, target])
        else:
            self.caller.msg(msg)


class CmdFinishUse(Command):
    """
    Finish using someone.
    
    Usage:
      finishuse <target> [cum_location] [volume]
    """
    key = "finishuse"
    aliases = ["cum"]
    locks = "cmd:all()"
    
    def func(self):
        if not self.args:
            self.caller.msg("Usage: finishuse <target> [location] [volume]")
            return
        
        args = self.args.strip().split()
        target = self.caller.search(args[0])
        if not target:
            return
        
        cum_loc = args[1] if len(args) > 1 else "inside"
        volume = int(args[2]) if len(args) > 2 else 20
        
        if not hasattr(target, 'public_use'):
            self.caller.msg("No use session.")
            return
        
        record = target.public_use
        
        if not record.is_currently_in_use:
            self.caller.msg("Not currently in use.")
            return
        
        # Find the session
        if record.recent_sessions:
            session = record.recent_sessions[-1]
            msg = record.end_use(session, volume, cum_loc)
        else:
            msg = record.end_use(None, volume, cum_loc)
        
        target.public_use = record
        
        self.caller.msg(msg)
        target.msg(msg)


class CmdUseStatus(Command):
    """
    View public use status.
    
    Usage:
      usestatus [target]
    """
    key = "usestatus"
    locks = "cmd:all()"
    
    def func(self):
        if not self.args:
            target = self.caller
        else:
            target = self.caller.search(self.args.strip())
            if not target:
                return
        
        if hasattr(target, 'public_use'):
            record = target.public_use
            self.caller.msg(record.get_status_display())
        else:
            self.caller.msg("No public use record.")


# =============================================================================
# ROUTINE COMMANDS
# =============================================================================

class CmdSchedule(Command):
    """
    View or create daily schedule.
    
    Usage:
      schedule [target]
      schedule <target> hucow|breeding|freeuse
    """
    key = "schedule"
    aliases = ["routine"]
    locks = "cmd:all()"
    
    def func(self):
        if not self.args:
            target = self.caller
            schedule_type = None
        else:
            args = self.args.strip().split()
            target = self.caller.search(args[0])
            if not target:
                return
            schedule_type = args[1] if len(args) > 1 else None
        
        from pet_systems.routines import (
            DailySchedule,
            create_hucow_schedule,
            create_breeding_stock_schedule,
            create_free_use_schedule,
        )
        
        if schedule_type:
            if schedule_type == "hucow":
                schedule = create_hucow_schedule(target.key, target.dbref)
            elif schedule_type == "breeding":
                schedule = create_breeding_stock_schedule(target.key, target.dbref)
            elif schedule_type == "freeuse":
                schedule = create_free_use_schedule(target.key, target.dbref)
            else:
                self.caller.msg("Unknown schedule type. Use: hucow, breeding, freeuse")
                return
            
            target.db.daily_schedule = schedule.to_dict() if hasattr(schedule, 'to_dict') else None
            self.caller.msg(f"Schedule set for {target.key}.")
        
        # Display schedule
        if hasattr(target.db, 'daily_schedule') and target.db.daily_schedule:
            schedule_data = target.db.daily_schedule
            # Simplified display
            self.caller.msg(f"Schedule for {target.key} is set.")
        else:
            self.caller.msg("No schedule set.")


# =============================================================================
# AUCTION COMMANDS
# =============================================================================

class CmdStartAuction(Command):
    """
    Start a new auction.
    
    Usage:
      startauction <name>
    """
    key = "startauction"
    locks = "cmd:perm(Builder)"
    
    def func(self):
        if not self.args:
            self.caller.msg("Name the auction.")
            return
        
        from pet_systems.auction import Auction
        import random
        from datetime import datetime
        
        auction = Auction(
            auction_id=f"AUC-{datetime.now().strftime('%Y%m%d')}-{random.randint(100, 999)}",
            name=self.args.strip(),
            auctioneer_name=self.caller.key,
            auctioneer_dbref=self.caller.dbref,
            location=self.caller.location.key if self.caller.location else "",
        )
        
        # Store in room or on caller
        self.caller.db.current_auction = auction.to_dict() if hasattr(auction, 'to_dict') else None
        
        self.caller.msg(f"Auction '{auction.name}' created. Add lots with 'addlot'.")


class CmdAddLot(Command):
    """
    Add a lot to the auction.
    
    Usage:
      addlot <target> <starting_bid>
    """
    key = "addlot"
    locks = "cmd:perm(Builder)"
    
    def func(self):
        if not self.args:
            self.caller.msg("Usage: addlot <target> <starting_bid>")
            return
        
        args = self.args.strip().split()
        target = self.caller.search(args[0])
        if not target:
            return
        
        starting_bid = int(args[1]) if len(args) > 1 else 100
        
        from pet_systems.auction import AuctionLot, DisplayPosition
        import random
        
        lot = AuctionLot(
            lot_id=f"LOT-{random.randint(1000, 9999)}",
            subject_dbref=target.dbref,
            subject_name=target.key,
            seller_dbref=self.caller.dbref,
            seller_name=self.caller.key,
            starting_bid=starting_bid,
        )
        
        # Add features from target
        if hasattr(target, 'hucow_stats') and target.is_hucow:
            lot.is_lactating = True
            lot.features.append("Lactating hucow")
        
        if hasattr(target, 'body_mods'):
            mods = target.body_mods
            if mods.is_futanari:
                lot.is_futanari = True
                lot.features.append("Futanari")
        
        self.caller.msg(f"Lot added: {target.key} (starting bid: {starting_bid})")
        self.caller.msg(lot.get_display_description())


class CmdBid(Command):
    """
    Place a bid at auction.
    
    Usage:
      bid <amount>
    """
    key = "bid"
    locks = "cmd:all()"
    
    def func(self):
        if not self.args:
            self.caller.msg("Usage: bid <amount>")
            return
        
        try:
            amount = int(self.args.strip())
        except ValueError:
            self.caller.msg("Amount must be a number.")
            return
        
        from pet_systems.auction import AuctioneerPhrases
        
        # Would need to find active auction in room
        self.caller.msg(f"You bid {amount} gold.")
        
        if self.caller.location:
            self.caller.location.msg_contents(
                AuctioneerPhrases.announce_bid(amount, self.caller.key),
                exclude=[self.caller]
            )


# =============================================================================
# COMMAND SET
# =============================================================================

class ExtendedCmdSet(CmdSet):
    """Extended commands for modifications, breaking, public use, etc."""
    
    key = "extended_cmdset"
    
    def at_cmdset_creation(self):
        # Modifications
        self.add(CmdEnhanceBreasts())
        self.add(CmdMakeFuta())
        self.add(CmdPierce())
        self.add(CmdBodyMods())
        
        # Breaking
        self.add(CmdBreak())
        self.add(CmdCondition())
        self.add(CmdMentalStatus())
        
        # Public use
        self.add(CmdSetPublicUse())
        self.add(CmdUse())
        self.add(CmdFinishUse())
        self.add(CmdUseStatus())
        
        # Routines
        self.add(CmdSchedule())
        
        # Auctions
        self.add(CmdStartAuction())
        self.add(CmdAddLot())
        self.add(CmdBid())
