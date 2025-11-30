"""
Brothel Commands
================

Commands for brothel workers, madams, and clients.
"""

from evennia import Command, CmdSet
from evennia.utils import evtable


class CmdBrothelStatus(Command):
    """
    View brothel or worker status.
    
    Usage:
        brothelstatus
        brothelstatus <brothel>
        whorestatus [target]
    
    Shows status of a brothel or worker.
    """
    
    key = "brothelstatus"
    aliases = ["whorestatus", "wstatus"]
    locks = "cmd:all()"
    
    def func(self):
        caller = self.caller
        
        if "whore" in self.cmdstring or "wstatus" in self.cmdstring:
            # Worker status
            target = caller
            if self.args:
                target = caller.search(self.args.strip())
                if not target:
                    return
            
            if not hasattr(target, 'whore_stats'):
                caller.msg(f"{target.key} has no brothel data.")
                return
            
            stats = target.whore_stats
            caller.msg(stats.get_summary())
        else:
            # Brothel status
            if not self.args:
                # Show brothel in current room
                brothel = caller.location.db.brothel
                if not brothel:
                    caller.msg("No brothel here.")
                    return
            else:
                # Would search for named brothel
                caller.msg("Brothel search not implemented.")
                return
            
            caller.msg(brothel.get_status())


class CmdRegisterWhore(Command):
    """
    Register as a brothel worker.
    
    Usage:
        registerwhore <target>
        registerwhore <target> = <brothel>
    
    Registers a character as a brothel worker.
    """
    
    key = "registerwhore"
    locks = "cmd:all()"
    
    def func(self):
        caller = self.caller
        
        if not self.args:
            caller.msg("Register who?")
            return
        
        if "=" in self.args:
            target_name, brothel_name = self.args.split("=", 1)
            target_name = target_name.strip()
            brothel_name = brothel_name.strip()
        else:
            target_name = self.args.strip()
            brothel_name = None
        
        target = caller.search(target_name)
        if not target:
            return
        
        if not hasattr(target, 'whore_stats'):
            caller.msg(f"{target.key} cannot be a brothel worker.")
            return
        
        from ..brothel import WhoreStats
        
        stats = WhoreStats(
            worker_dbref=target.dbref,
            worker_name=target.key,
        )
        target.db.whore_stats = stats.to_dict()
        
        caller.msg(f"{target.key} is now registered as a brothel worker.")
        target.msg("You have been registered as a brothel worker.")


class CmdSetServices(Command):
    """
    Set services offered by a worker.
    
    Usage:
        setservices <target> = <service1>, <service2>, ...
        setservices/forbid <target> = <service1>, ...
        setservices/list
    
    Sets which services a worker offers or forbids.
    """
    
    key = "setservices"
    locks = "cmd:all()"
    
    def func(self):
        caller = self.caller
        
        if "list" in self.switches:
            from ..brothel import ServiceType
            services = [s.value for s in ServiceType]
            caller.msg("Available services: " + ", ".join(services))
            return
        
        if "=" not in self.args:
            caller.msg("Usage: setservices <target> = <services>")
            return
        
        target_name, services_str = self.args.split("=", 1)
        target = caller.search(target_name.strip())
        if not target:
            return
        
        if not hasattr(target, 'whore_stats'):
            caller.msg(f"{target.key} is not a brothel worker.")
            return
        
        from ..brothel import ServiceType, WhoreStats
        
        stats = target.whore_stats
        services = [s.strip().upper() for s in services_str.split(",")]
        
        valid_services = []
        for s in services:
            try:
                service = ServiceType[s]
                valid_services.append(service)
            except KeyError:
                caller.msg(f"Unknown service: {s}")
        
        if "forbid" in self.switches:
            stats.services_forbidden.extend(valid_services)
            target.whore_stats = stats
            caller.msg(f"Forbidden services updated for {target.key}.")
        else:
            stats.services_offered = valid_services
            target.whore_stats = stats
            caller.msg(f"Services updated for {target.key}.")


class CmdStartShift(Command):
    """
    Start working a shift.
    
    Usage:
        startshift
        startshift <time>
    
    Starts working at the brothel. Times: morning, afternoon, evening, night.
    """
    
    key = "startshift"
    aliases = ["workshift", "onduty"]
    locks = "cmd:all()"
    
    def func(self):
        caller = self.caller
        
        if not hasattr(caller, 'whore_stats'):
            caller.msg("You're not a brothel worker.")
            return
        
        stats = caller.whore_stats
        
        if stats.is_working:
            caller.msg("You're already working.")
            return
        
        shift = self.args.strip().lower() if self.args else "evening"
        
        stats.is_working = True
        stats.current_shift = shift
        caller.db.whore_stats = stats.to_dict()
        
        caller.msg(f"You start your {shift} shift. Time to earn your keep.")
        caller.location.msg_contents(
            f"{caller.key} is now available for service.",
            exclude=[caller]
        )


class CmdEndShift(Command):
    """
    End your shift.
    
    Usage:
        endshift
    
    Ends your current working shift.
    """
    
    key = "endshift"
    aliases = ["offduty"]
    locks = "cmd:all()"
    
    def func(self):
        caller = self.caller
        
        if not hasattr(caller, 'whore_stats'):
            caller.msg("You're not a brothel worker.")
            return
        
        stats = caller.whore_stats
        
        if not stats.is_working:
            caller.msg("You're not currently working.")
            return
        
        earnings = stats.earnings_today
        clients = stats.clients_today
        
        stats.is_working = False
        stats.current_shift = None
        caller.db.whore_stats = stats.to_dict()
        
        caller.msg(f"Shift complete. You served {clients} clients and earned {earnings}g.")


class CmdServiceClient(Command):
    """
    Service a client.
    
    Usage:
        service <client>
        service <client> = <service type>
    
    Begins servicing a client with a specific service.
    """
    
    key = "service"
    locks = "cmd:all()"
    
    def func(self):
        caller = self.caller
        
        if not hasattr(caller, 'whore_stats'):
            caller.msg("You're not a brothel worker.")
            return
        
        stats = caller.whore_stats
        
        if not stats.is_working:
            caller.msg("Start your shift first.")
            return
        
        if stats.is_with_client:
            caller.msg("You're already with a client.")
            return
        
        if not self.args:
            caller.msg("Service who?")
            return
        
        if "=" in self.args:
            client_name, service_type = self.args.split("=", 1)
        else:
            client_name = self.args
            service_type = "standard"
        
        client = caller.search(client_name.strip())
        if not client:
            return
        
        from ..brothel import ServiceType
        
        try:
            service = ServiceType[service_type.strip().upper()]
        except KeyError:
            service = ServiceType.STANDARD
        
        # Check if service is offered
        if service in stats.services_forbidden:
            caller.msg(f"You don't offer {service.value} services.")
            return
        
        # Start session
        stats.is_with_client = True
        stats.current_client = client.dbref
        caller.db.whore_stats = stats.to_dict()
        
        caller.msg(f"You begin {service.value} service for {client.key}...")
        client.msg(f"{caller.key} begins servicing you.")


class CmdFinishService(Command):
    """
    Finish servicing a client.
    
    Usage:
        finishservice
        finishservice <satisfaction 1-100>
    
    Completes service and calculates payment/review.
    """
    
    key = "finishservice"
    aliases = ["doneservice"]
    locks = "cmd:all()"
    
    def func(self):
        caller = self.caller
        
        if not hasattr(caller, 'whore_stats'):
            caller.msg("You're not a brothel worker.")
            return
        
        stats = caller.whore_stats
        
        if not stats.is_with_client:
            caller.msg("You're not with a client.")
            return
        
        # Calculate satisfaction
        satisfaction = 70  # Default
        if self.args:
            try:
                satisfaction = int(self.args.strip())
                satisfaction = max(1, min(100, satisfaction))
            except ValueError:
                pass
        
        # Get base price
        from ..brothel import SERVICE_MENU
        base_price = 25  # Default
        
        # Calculate tip
        tip = 0
        if satisfaction >= 80:
            tip = int(base_price * (satisfaction - 50) / 100)
        
        total = base_price + tip
        
        # Update stats
        stats.is_with_client = False
        stats.current_client = None
        stats.clients_today += 1
        stats.clients_total += 1
        stats.earnings_today += total
        stats.earnings_total += total
        
        # Record review rating
        if satisfaction >= 90:
            rating = "EXCELLENT"
        elif satisfaction >= 70:
            rating = "GOOD"
        elif satisfaction >= 50:
            rating = "AVERAGE"
        else:
            rating = "POOR"
        
        caller.db.whore_stats = stats.to_dict()
        
        caller.msg(f"Service complete! Earned {base_price}g + {tip}g tip = {total}g. Rating: {rating}")


class CmdWhoreRank(Command):
    """
    Check or set whore rank.
    
    Usage:
        whorerank [target]
        whorerank/set <target> = <rank>
    
    Ranks: street_whore, common_whore, skilled_whore, 
           house_favorite, elite_courtesan, oiran
    """
    
    key = "whorerank"
    locks = "cmd:all()"
    
    def func(self):
        caller = self.caller
        
        if "set" in self.switches:
            if "=" not in self.args:
                caller.msg("Usage: whorerank/set <target> = <rank>")
                return
            
            target_name, rank_name = self.args.split("=", 1)
            target = caller.search(target_name.strip())
            if not target:
                return
            
            if not hasattr(target, 'whore_stats'):
                caller.msg(f"{target.key} is not a brothel worker.")
                return
            
            from ..brothel import WhoreSpecialization
            
            try:
                rank = WhoreSpecialization[rank_name.strip().upper()]
            except KeyError:
                caller.msg(f"Unknown rank. Valid: {[r.value for r in WhoreSpecialization]}")
                return
            
            stats = target.whore_stats
            stats.specialization = rank
            target.whore_stats = stats
            
            caller.msg(f"{target.key}'s rank set to {rank.value}.")
        else:
            target = caller
            if self.args:
                target = caller.search(self.args.strip())
                if not target:
                    return
            
            if not hasattr(target, 'whore_stats'):
                caller.msg(f"{target.key} is not a brothel worker.")
                return
            
            stats = target.whore_stats
            caller.msg(f"{target.key}'s rank: {stats.specialization.value if stats.specialization else 'None'}")


class CmdBrothelEarnings(Command):
    """
    View earnings.
    
    Usage:
        earnings
        earnings <target>
    
    Shows earnings for today and total.
    """
    
    key = "earnings"
    aliases = ["myearnings"]
    locks = "cmd:all()"
    
    def func(self):
        caller = self.caller
        
        target = caller
        if self.args:
            target = caller.search(self.args.strip())
            if not target:
                return
        
        if not hasattr(target, 'whore_stats'):
            caller.msg(f"{target.key} has no brothel data.")
            return
        
        stats = target.whore_stats
        
        caller.msg(f"=== {target.key}'s Earnings ===")
        caller.msg(f"Today: {stats.earnings_today}g ({stats.clients_today} clients)")
        caller.msg(f"Total: {stats.earnings_total}g ({stats.clients_total} clients)")
        caller.msg(f"Average per client: {stats.earnings_total // max(1, stats.clients_total)}g")


class CmdGenerateClient(Command):
    """
    Generate a random client (GM/testing).
    
    Usage:
        genclient
        genclient <tier>
    
    Generates a random NPC client for the brothel.
    """
    
    key = "genclient"
    locks = "cmd:perm(Builder)"
    
    def func(self):
        caller = self.caller
        
        from ..brothel import generate_client
        
        tier = self.args.strip().lower() if self.args else "common"
        
        client = generate_client(tier=tier)
        
        caller.msg(f"Generated client: {client.name}")
        caller.msg(f"  Type: {client.client_type.value}")
        caller.msg(f"  Mood: {client.mood.value}")
        caller.msg(f"  Gold: {client.gold_available}g")
        caller.msg(f"  Preferences: {[s.value for s in client.preferences.preferred_services]}")


class BrothelCmdSet(CmdSet):
    """Commands for the brothel system."""
    
    key = "brothel_cmdset"
    
    def at_cmdset_creation(self):
        self.add(CmdBrothelStatus())
        self.add(CmdRegisterWhore())
        self.add(CmdSetServices())
        self.add(CmdStartShift())
        self.add(CmdEndShift())
        self.add(CmdServiceClient())
        self.add(CmdFinishService())
        self.add(CmdWhoreRank())
        self.add(CmdBrothelEarnings())
        self.add(CmdGenerateClient())
