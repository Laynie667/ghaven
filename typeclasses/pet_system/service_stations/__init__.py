"""
Service Station System
======================

Glory holes, service booths, and public service infrastructure including:
- Glory hole mechanics
- Service booth management
- Queue systems
- Anonymous service tracking
- Rating systems
"""

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any, Tuple
from enum import Enum
from datetime import datetime, timedelta
import random


# =============================================================================
# ENUMS
# =============================================================================

class StationType(Enum):
    """Types of service stations."""
    GLORY_HOLE = "glory_hole"
    SERVICE_BOOTH = "service_booth"
    BREEDING_STALL = "breeding_stall"
    MILKING_STATION = "milking_station"
    TOILET = "toilet"
    DISPLAY_CASE = "display_case"
    STOCKS = "stocks"
    PILLORY = "pillory"
    BREEDING_BENCH = "breeding_bench"
    WALL_MOUNT = "wall_mount"


class ServiceType(Enum):
    """Types of services offered."""
    ORAL = "oral"
    HAND = "hand"
    BREAST = "breast"
    ANAL = "anal"
    VAGINAL = "vaginal"
    FULL_SERVICE = "full_service"
    WORSHIP = "worship"           # Feet, etc.
    TOILET = "toilet"
    MILKING = "milking"
    DISPLAY = "display"


class QueuePriority(Enum):
    """Priority levels in queue."""
    NORMAL = "normal"
    VIP = "vip"
    OWNER = "owner"
    PRIORITY = "priority"


# =============================================================================
# SERVICE SESSION
# =============================================================================

@dataclass
class ServiceSession:
    """Record of a service session."""
    
    session_id: str = ""
    station_id: str = ""
    
    # Participants
    server_dbref: str = ""
    server_name: str = ""
    client_dbref: str = ""
    client_name: str = ""         # May be "Anonymous"
    is_anonymous: bool = True
    
    # Service
    service_type: ServiceType = ServiceType.ORAL
    
    # Timing
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    duration_seconds: int = 0
    
    # Results
    client_satisfied: bool = True
    client_orgasmed: bool = False
    cum_received: bool = False
    cum_volume_ml: int = 0
    cum_location: str = ""
    
    # Rating
    rating: int = 0               # 1-5 stars
    tip_amount: int = 0
    
    def complete(
        self,
        satisfied: bool = True,
        orgasmed: bool = True,
        cum_volume: int = 0,
        cum_location: str = "",
        rating: int = 3,
        tip: int = 0,
    ) -> str:
        """Complete the service session."""
        self.end_time = datetime.now()
        self.duration_seconds = int((self.end_time - self.start_time).total_seconds())
        
        self.client_satisfied = satisfied
        self.client_orgasmed = orgasmed
        self.cum_received = cum_volume > 0
        self.cum_volume_ml = cum_volume
        self.cum_location = cum_location
        self.rating = rating
        self.tip_amount = tip
        
        # Generate completion message
        client_ref = "Anonymous" if self.is_anonymous else self.client_name
        
        msg = f"{client_ref} finishes"
        if self.cum_received:
            msg += f", depositing {cum_volume}ml in/on {cum_location}"
        msg += f". Rating: {'★' * rating}{'☆' * (5-rating)}"
        if tip > 0:
            msg += f" Tip: {tip} gold"
        
        return msg


# =============================================================================
# QUEUE
# =============================================================================

@dataclass
class QueueEntry:
    """An entry in the service queue."""
    
    client_dbref: str = ""
    client_name: str = ""
    priority: QueuePriority = QueuePriority.NORMAL
    
    requested_service: ServiceType = ServiceType.ORAL
    joined_at: Optional[datetime] = None
    
    is_anonymous: bool = True
    
    @property
    def wait_time_minutes(self) -> int:
        """Get wait time in minutes."""
        if not self.joined_at:
            return 0
        return int((datetime.now() - self.joined_at).total_seconds() / 60)


@dataclass
class ServiceQueue:
    """Queue for a service station."""
    
    queue_id: str = ""
    station_id: str = ""
    
    entries: List[QueueEntry] = field(default_factory=list)
    max_size: int = 20
    
    # Stats
    total_served: int = 0
    average_wait_minutes: float = 0.0
    
    def add_to_queue(
        self,
        client_dbref: str,
        client_name: str,
        service: ServiceType,
        priority: QueuePriority = QueuePriority.NORMAL,
        anonymous: bool = True,
    ) -> Tuple[int, str]:
        """
        Add someone to the queue.
        Returns (position, message).
        """
        if len(self.entries) >= self.max_size:
            return -1, "Queue is full."
        
        entry = QueueEntry(
            client_dbref=client_dbref,
            client_name=client_name,
            priority=priority,
            requested_service=service,
            joined_at=datetime.now(),
            is_anonymous=anonymous,
        )
        
        # Insert based on priority
        insert_pos = len(self.entries)
        for i, existing in enumerate(self.entries):
            if priority.value > existing.priority.value:
                insert_pos = i
                break
        
        self.entries.insert(insert_pos, entry)
        
        return insert_pos + 1, f"Added to queue at position {insert_pos + 1}."
    
    def get_next(self) -> Optional[QueueEntry]:
        """Get next person in queue."""
        if not self.entries:
            return None
        return self.entries.pop(0)
    
    def get_position(self, client_dbref: str) -> int:
        """Get someone's position in queue."""
        for i, entry in enumerate(self.entries):
            if entry.client_dbref == client_dbref:
                return i + 1
        return -1
    
    def remove(self, client_dbref: str) -> bool:
        """Remove someone from queue."""
        for i, entry in enumerate(self.entries):
            if entry.client_dbref == client_dbref:
                self.entries.pop(i)
                return True
        return False
    
    @property
    def length(self) -> int:
        return len(self.entries)
    
    def get_display(self) -> str:
        """Get queue display."""
        if not self.entries:
            return "Queue is empty."
        
        lines = [f"Queue ({len(self.entries)}/{self.max_size}):"]
        for i, entry in enumerate(self.entries):
            name = "Anonymous" if entry.is_anonymous else entry.client_name
            wait = entry.wait_time_minutes
            lines.append(f"  {i+1}. {name} - {entry.requested_service.value} ({wait}min wait)")
        
        return "\n".join(lines)


# =============================================================================
# GLORY HOLE
# =============================================================================

@dataclass
class GloryHole:
    """A glory hole station."""
    
    station_id: str = ""
    name: str = "Glory Hole"
    location: str = ""
    
    station_type: StationType = StationType.GLORY_HOLE
    
    # Configuration
    hole_height_cm: int = 90      # Standard height
    hole_diameter_cm: int = 12
    has_padding: bool = True
    has_restraints: bool = False
    
    # Server side
    server_dbref: str = ""
    server_name: str = ""
    server_restrained: bool = False
    server_blindfolded: bool = True
    
    # Client side
    is_occupied: bool = False
    current_client_dbref: str = ""
    current_client_name: str = ""
    
    # Queue
    queue: ServiceQueue = field(default_factory=ServiceQueue)
    
    # Services offered
    services_offered: List[ServiceType] = field(default_factory=lambda: [
        ServiceType.ORAL, ServiceType.HAND
    ])
    
    # Stats
    total_sessions: int = 0
    total_loads_received: int = 0
    total_volume_ml: int = 0
    average_rating: float = 3.0
    
    # Current session
    current_session: Optional[ServiceSession] = None
    
    # History
    recent_sessions: List[ServiceSession] = field(default_factory=list)
    
    def assign_server(self, server_dbref: str, server_name: str, restrained: bool = False) -> str:
        """Assign someone to work the hole."""
        self.server_dbref = server_dbref
        self.server_name = server_name
        self.server_restrained = restrained
        
        msg = f"{server_name} is assigned to the glory hole"
        if restrained:
            msg += ", restrained in position"
        if self.server_blindfolded:
            msg += ", blindfolded"
        msg += "."
        
        return msg
    
    def release_server(self) -> str:
        """Release the current server."""
        name = self.server_name
        self.server_dbref = ""
        self.server_name = ""
        self.server_restrained = False
        
        return f"{name} is released from the glory hole."
    
    def begin_service(
        self,
        client_dbref: str,
        client_name: str,
        service: ServiceType,
        anonymous: bool = True,
    ) -> Tuple[bool, str]:
        """Begin a service session."""
        if not self.server_dbref:
            return False, "No one assigned to serve."
        
        if self.is_occupied:
            return False, "Station occupied."
        
        if service not in self.services_offered:
            return False, f"{service.value} not offered here."
        
        self.is_occupied = True
        self.current_client_dbref = client_dbref
        self.current_client_name = client_name if not anonymous else "Anonymous"
        
        session = ServiceSession(
            session_id=f"SVC-{datetime.now().strftime('%H%M%S')}-{random.randint(100, 999)}",
            station_id=self.station_id,
            server_dbref=self.server_dbref,
            server_name=self.server_name,
            client_dbref=client_dbref,
            client_name=client_name,
            is_anonymous=anonymous,
            service_type=service,
            start_time=datetime.now(),
        )
        
        self.current_session = session
        
        # Generate message
        client_ref = "Someone" if anonymous else client_name
        
        if self.server_blindfolded:
            server_msg = f"Something pushes through the hole..."
        else:
            server_msg = f"{client_ref} approaches the hole."
        
        return True, server_msg
    
    def end_service(
        self,
        cum_volume: int = 0,
        cum_location: str = "mouth",
        rating: int = 3,
        tip: int = 0,
    ) -> str:
        """End current service session."""
        if not self.current_session:
            return "No active session."
        
        msg = self.current_session.complete(
            satisfied=True,
            orgasmed=cum_volume > 0,
            cum_volume=cum_volume,
            cum_location=cum_location,
            rating=rating,
            tip=tip,
        )
        
        # Update stats
        self.total_sessions += 1
        if cum_volume > 0:
            self.total_loads_received += 1
            self.total_volume_ml += cum_volume
        
        # Update average rating
        self.average_rating = (
            (self.average_rating * (self.total_sessions - 1) + rating)
            / self.total_sessions
        )
        
        # Save to history
        self.recent_sessions.append(self.current_session)
        if len(self.recent_sessions) > 50:
            self.recent_sessions.pop(0)
        
        # Clear current
        self.is_occupied = False
        self.current_client_dbref = ""
        self.current_client_name = ""
        self.current_session = None
        
        return msg
    
    def get_status(self) -> str:
        """Get station status."""
        lines = [f"=== {self.name} ==="]
        
        if self.server_dbref:
            lines.append(f"Server: {self.server_name}")
            if self.server_restrained:
                lines.append("  [RESTRAINED]")
            if self.server_blindfolded:
                lines.append("  [BLINDFOLDED]")
        else:
            lines.append("Server: None assigned")
        
        lines.append(f"\nStatus: {'OCCUPIED' if self.is_occupied else 'Available'}")
        
        lines.append(f"\nServices: {', '.join(s.value for s in self.services_offered)}")
        
        lines.append(f"\n--- Statistics ---")
        lines.append(f"Total Sessions: {self.total_sessions}")
        lines.append(f"Loads Received: {self.total_loads_received}")
        lines.append(f"Total Volume: {self.total_volume_ml}ml")
        lines.append(f"Average Rating: {'★' * int(self.average_rating)}{'☆' * (5-int(self.average_rating))} ({self.average_rating:.1f})")
        
        lines.append(f"\n{self.queue.get_display()}")
        
        return "\n".join(lines)


# =============================================================================
# SERVICE BOOTH
# =============================================================================

@dataclass
class ServiceBooth:
    """A service booth (more interactive than glory hole)."""
    
    station_id: str = ""
    name: str = "Service Booth"
    location: str = ""
    
    station_type: StationType = StationType.SERVICE_BOOTH
    
    # Configuration
    is_private: bool = False      # Has curtain/door
    has_bed: bool = True
    has_restraints: bool = True
    has_cleaning: bool = True     # Cleanup supplies
    
    # Server
    server_dbref: str = ""
    server_name: str = ""
    server_position: str = "kneeling"
    
    # Pricing
    prices: Dict[ServiceType, int] = field(default_factory=lambda: {
        ServiceType.ORAL: 10,
        ServiceType.HAND: 5,
        ServiceType.BREAST: 15,
        ServiceType.ANAL: 25,
        ServiceType.VAGINAL: 20,
        ServiceType.FULL_SERVICE: 50,
    })
    
    # Queue
    queue: ServiceQueue = field(default_factory=ServiceQueue)
    
    # Stats
    total_sessions: int = 0
    total_earnings: int = 0
    
    # Current
    is_occupied: bool = False
    current_session: Optional[ServiceSession] = None
    
    def assign_server(self, server_dbref: str, server_name: str, position: str = "kneeling") -> str:
        """Assign a server to the booth."""
        self.server_dbref = server_dbref
        self.server_name = server_name
        self.server_position = position
        
        return f"{server_name} takes position ({position}) in the service booth."
    
    def get_menu(self) -> str:
        """Get service menu."""
        lines = [f"=== {self.name} Menu ==="]
        lines.append(f"Server: {self.server_name or 'None'}")
        lines.append("\nServices:")
        
        for service, price in self.prices.items():
            lines.append(f"  • {service.value.title()}: {price} gold")
        
        return "\n".join(lines)
    
    def purchase_service(
        self,
        client_dbref: str,
        client_name: str,
        service: ServiceType,
    ) -> Tuple[bool, str, int]:
        """
        Purchase a service.
        Returns (success, message, cost).
        """
        if not self.server_dbref:
            return False, "No server available.", 0
        
        if self.is_occupied:
            return False, "Booth occupied.", 0
        
        if service not in self.prices:
            return False, "Service not available.", 0
        
        cost = self.prices[service]
        
        self.is_occupied = True
        
        session = ServiceSession(
            session_id=f"BOOTH-{datetime.now().strftime('%H%M%S')}-{random.randint(100, 999)}",
            station_id=self.station_id,
            server_dbref=self.server_dbref,
            server_name=self.server_name,
            client_dbref=client_dbref,
            client_name=client_name,
            is_anonymous=False,
            service_type=service,
            start_time=datetime.now(),
        )
        
        self.current_session = session
        
        return True, f"{client_name} purchases {service.value} from {self.server_name} for {cost} gold.", cost


# =============================================================================
# PUBLIC TOILET
# =============================================================================

@dataclass
class HumanToilet:
    """A human toilet station."""
    
    station_id: str = ""
    name: str = "Public Toilet"
    location: str = ""
    
    station_type: StationType = StationType.TOILET
    
    # Configuration
    is_installed: bool = False    # Permanently installed
    position: str = "floor"       # "floor", "wall", "seat"
    has_restraints: bool = True
    has_funnel: bool = False      # Funnel gag
    
    # Occupant
    occupant_dbref: str = ""
    occupant_name: str = ""
    is_restrained: bool = False
    
    # Stats
    times_used: int = 0
    total_users: int = 0
    
    def install_toilet(self, subject_dbref: str, subject_name: str, restrained: bool = True) -> str:
        """Install someone as the toilet."""
        self.occupant_dbref = subject_dbref
        self.occupant_name = subject_name
        self.is_restrained = restrained
        self.is_installed = True
        
        msg = f"{subject_name} is installed as the public toilet"
        if restrained:
            msg += ", securely restrained"
        if self.has_funnel:
            msg += " with funnel gag"
        msg += "."
        
        return msg
    
    def use(self, user_name: str, use_type: str = "piss") -> str:
        """Use the toilet."""
        if not self.is_installed:
            return "No toilet installed."
        
        self.times_used += 1
        
        msgs = {
            "piss": f"{user_name} relieves themselves using {self.occupant_name}.",
            "spit": f"{user_name} spits into {self.occupant_name}'s mouth.",
        }
        
        return msgs.get(use_type, f"{user_name} uses {self.occupant_name}.")
    
    def get_status(self) -> str:
        """Get status."""
        if not self.is_installed:
            return "Toilet not currently installed."
        
        lines = [f"=== {self.name} ==="]
        lines.append(f"Installed: {self.occupant_name}")
        lines.append(f"Position: {self.position}")
        if self.is_restrained:
            lines.append("[RESTRAINED]")
        if self.has_funnel:
            lines.append("[FUNNEL GAG]")
        lines.append(f"\nTimes Used: {self.times_used}")
        
        return "\n".join(lines)


# =============================================================================
# SERVICE COMPLEX
# =============================================================================

@dataclass
class ServiceComplex:
    """A complex with multiple service stations."""
    
    complex_id: str = ""
    name: str = "Service Complex"
    location: str = ""
    
    # Stations
    glory_holes: Dict[str, GloryHole] = field(default_factory=dict)
    booths: Dict[str, ServiceBooth] = field(default_factory=dict)
    toilets: Dict[str, HumanToilet] = field(default_factory=dict)
    
    # Management
    owner_dbref: str = ""
    owner_name: str = ""
    
    # Pricing
    base_prices: Dict[ServiceType, int] = field(default_factory=dict)
    house_cut: float = 0.2        # 20% to the house
    
    # Stats
    total_revenue: int = 0
    total_sessions: int = 0
    
    def add_glory_hole(self, name: str = "Glory Hole") -> GloryHole:
        """Add a glory hole."""
        gh_id = f"GH-{len(self.glory_holes)+1}"
        gh = GloryHole(
            station_id=gh_id,
            name=name,
            location=self.location,
        )
        gh.queue = ServiceQueue(queue_id=f"Q-{gh_id}", station_id=gh_id)
        self.glory_holes[gh_id] = gh
        return gh
    
    def add_booth(self, name: str = "Booth") -> ServiceBooth:
        """Add a service booth."""
        b_id = f"BOOTH-{len(self.booths)+1}"
        booth = ServiceBooth(
            station_id=b_id,
            name=name,
            location=self.location,
        )
        booth.queue = ServiceQueue(queue_id=f"Q-{b_id}", station_id=b_id)
        self.booths[b_id] = booth
        return booth
    
    def add_toilet(self, name: str = "Toilet") -> HumanToilet:
        """Add a toilet station."""
        t_id = f"TOILET-{len(self.toilets)+1}"
        toilet = HumanToilet(
            station_id=t_id,
            name=name,
            location=self.location,
        )
        self.toilets[t_id] = toilet
        return toilet
    
    def get_directory(self) -> str:
        """Get complex directory."""
        lines = [f"=== {self.name} Directory ==="]
        
        if self.glory_holes:
            lines.append("\n--- Glory Holes ---")
            for gh_id, gh in self.glory_holes.items():
                status = "OCCUPIED" if gh.is_occupied else ("Available" if gh.server_dbref else "Unstaffed")
                lines.append(f"  {gh.name}: {status}")
                if gh.server_name:
                    lines.append(f"    Server: {gh.server_name}")
        
        if self.booths:
            lines.append("\n--- Service Booths ---")
            for b_id, booth in self.booths.items():
                status = "OCCUPIED" if booth.is_occupied else ("Available" if booth.server_dbref else "Unstaffed")
                lines.append(f"  {booth.name}: {status}")
                if booth.server_name:
                    lines.append(f"    Server: {booth.server_name}")
        
        if self.toilets:
            lines.append("\n--- Toilets ---")
            for t_id, toilet in self.toilets.items():
                status = f"Installed: {toilet.occupant_name}" if toilet.is_installed else "Empty"
                lines.append(f"  {toilet.name}: {status}")
        
        lines.append(f"\nTotal Revenue: {self.total_revenue} gold")
        lines.append(f"Total Sessions: {self.total_sessions}")
        
        return "\n".join(lines)


# =============================================================================
# FACTORY FUNCTIONS
# =============================================================================

def create_glory_hole_row(count: int = 5, location: str = "") -> List[GloryHole]:
    """Create a row of glory holes."""
    holes = []
    for i in range(count):
        gh = GloryHole(
            station_id=f"GH-{i+1}",
            name=f"Hole #{i+1}",
            location=location,
        )
        gh.queue = ServiceQueue(queue_id=f"Q-GH-{i+1}", station_id=gh.station_id)
        holes.append(gh)
    return holes


def create_standard_complex(name: str, location: str) -> ServiceComplex:
    """Create a standard service complex."""
    complex = ServiceComplex(
        complex_id=f"COMPLEX-{datetime.now().strftime('%Y%m%d%H%M%S')}",
        name=name,
        location=location,
    )
    
    # Add stations
    for i in range(3):
        complex.add_glory_hole(f"Glory Hole #{i+1}")
    
    for i in range(2):
        complex.add_booth(f"Private Booth #{i+1}")
    
    complex.add_toilet("Public Toilet")
    
    return complex


__all__ = [
    "StationType",
    "ServiceType",
    "QueuePriority",
    "ServiceSession",
    "QueueEntry",
    "ServiceQueue",
    "GloryHole",
    "ServiceBooth",
    "HumanToilet",
    "ServiceComplex",
    "create_glory_hole_row",
    "create_standard_complex",
]
