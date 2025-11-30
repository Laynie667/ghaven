"""
Brothel System
==============

Complete brothel management including:
- Client generation and preferences
- Service menus and pricing
- Reputation and reviews
- Shift scheduling
- Earnings and house cuts
- Specialization training
"""

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any, Tuple
from enum import Enum
from datetime import datetime, time, timedelta
import random


# =============================================================================
# ENUMS
# =============================================================================

class ServiceType(Enum):
    """Types of services offered."""
    COMPANIONSHIP = "companionship"      # Conversation, company
    DANCING = "dancing"                   # Lap dance, strip tease
    MASSAGE = "massage"                   # Sensual massage
    ORAL = "oral"                         # Oral service
    STANDARD = "standard"                 # Vaginal
    ANAL = "anal"                         # Anal service
    BREEDING = "breeding"                 # Unprotected, cum inside
    BDSM_LIGHT = "bdsm_light"            # Light bondage, spanking
    BDSM_HEAVY = "bdsm_heavy"            # Heavy BDSM
    PAIN = "pain"                         # Pain services
    HUMILIATION = "humiliation"           # Verbal degradation
    GANGBANG = "gangbang"                 # Multiple clients
    OVERNIGHT = "overnight"               # Full night
    GIRLFRIEND = "girlfriend"             # GFE
    FETISH = "fetish"                     # Specific fetishes
    LACTATION = "lactation"               # Nursing services
    PREGNANT = "pregnant"                 # Pregnancy fetish


class ClientType(Enum):
    """Types of clients."""
    COMMONER = "commoner"
    MERCHANT = "merchant"
    NOBLE = "noble"
    ROYAL = "royal"
    ADVENTURER = "adventurer"
    SOLDIER = "soldier"
    CLERGY = "clergy"                     # Secretly visiting
    MONSTER = "monster"                   # Non-human
    VIP = "vip"                           # Special treatment


class ClientMood(Enum):
    """Client moods affecting interaction."""
    NERVOUS = "nervous"                   # First timer, gentle
    EAGER = "eager"                       # Excited, quick
    DEMANDING = "demanding"               # Expects perfection
    ROUGH = "rough"                       # Wants it hard
    ROMANTIC = "romantic"                 # Wants connection
    DEGRADING = "degrading"               # Wants to humiliate
    DRUNK = "drunk"                       # Unpredictable
    SHY = "shy"                           # Needs encouragement


class WhoreSpecialization(Enum):
    """Specializations for workers."""
    NONE = "none"
    COURTESAN = "courtesan"               # High-class, conversation
    PAIN_SLUT = "pain_slut"               # BDSM specialist
    BREEDING_WHORE = "breeding_whore"     # Unprotected breeding
    COCK_SLEEVE = "cock_sleeve"           # High volume, any hole
    MILK_MAID = "milk_maid"               # Lactation services
    MONSTER_BRIDE = "monster_bride"       # Serves non-humans
    SUBMISSIVE = "submissive"             # Total submission
    DOMINATRIX = "dominatrix"             # Domination services


class ReviewRating(Enum):
    """Client review ratings."""
    TERRIBLE = 1
    POOR = 2
    AVERAGE = 3
    GOOD = 4
    EXCELLENT = 5
    LEGENDARY = 6


# =============================================================================
# SERVICE DEFINITIONS
# =============================================================================

@dataclass
class Service:
    """A service offered."""
    
    service_type: ServiceType = ServiceType.STANDARD
    name: str = ""
    description: str = ""
    
    # Pricing
    base_price: int = 50
    duration_minutes: int = 30
    
    # Requirements
    min_beauty: int = 0
    min_skill: int = 0
    required_specialization: Optional[WhoreSpecialization] = None
    
    # Effects on worker
    stamina_cost: int = 10
    degradation: int = 5
    arousal_gain: int = 10
    
    # Client satisfaction modifiers
    satisfaction_base: int = 50


# Standard service menu
SERVICE_MENU = {
    ServiceType.COMPANIONSHIP: Service(
        service_type=ServiceType.COMPANIONSHIP,
        name="Companionship",
        description="Pleasant conversation and company",
        base_price=20,
        duration_minutes=60,
        stamina_cost=5,
        degradation=0,
        arousal_gain=0,
        satisfaction_base=40,
    ),
    ServiceType.DANCING: Service(
        service_type=ServiceType.DANCING,
        name="Private Dance",
        description="Sensual dance and strip tease",
        base_price=30,
        duration_minutes=15,
        min_beauty=40,
        stamina_cost=15,
        degradation=5,
        arousal_gain=10,
        satisfaction_base=50,
    ),
    ServiceType.MASSAGE: Service(
        service_type=ServiceType.MASSAGE,
        name="Sensual Massage",
        description="Full body massage with happy ending",
        base_price=40,
        duration_minutes=45,
        min_skill=20,
        stamina_cost=15,
        degradation=5,
        arousal_gain=15,
        satisfaction_base=55,
    ),
    ServiceType.ORAL: Service(
        service_type=ServiceType.ORAL,
        name="Oral Service",
        description="Skilled mouth work",
        base_price=50,
        duration_minutes=20,
        min_skill=30,
        stamina_cost=15,
        degradation=15,
        arousal_gain=10,
        satisfaction_base=60,
    ),
    ServiceType.STANDARD: Service(
        service_type=ServiceType.STANDARD,
        name="Standard Service",
        description="Full intercourse",
        base_price=80,
        duration_minutes=30,
        stamina_cost=20,
        degradation=20,
        arousal_gain=30,
        satisfaction_base=65,
    ),
    ServiceType.ANAL: Service(
        service_type=ServiceType.ANAL,
        name="Anal Service",
        description="Backdoor access",
        base_price=100,
        duration_minutes=30,
        min_skill=30,
        stamina_cost=25,
        degradation=25,
        arousal_gain=20,
        satisfaction_base=70,
    ),
    ServiceType.BREEDING: Service(
        service_type=ServiceType.BREEDING,
        name="Breeding Service",
        description="Unprotected, finish inside",
        base_price=150,
        duration_minutes=45,
        required_specialization=WhoreSpecialization.BREEDING_WHORE,
        stamina_cost=25,
        degradation=30,
        arousal_gain=40,
        satisfaction_base=80,
    ),
    ServiceType.BDSM_LIGHT: Service(
        service_type=ServiceType.BDSM_LIGHT,
        name="Light BDSM",
        description="Bondage, spanking, light pain",
        base_price=100,
        duration_minutes=45,
        min_skill=40,
        stamina_cost=25,
        degradation=30,
        arousal_gain=25,
        satisfaction_base=65,
    ),
    ServiceType.BDSM_HEAVY: Service(
        service_type=ServiceType.BDSM_HEAVY,
        name="Heavy BDSM",
        description="Intense bondage, pain, submission",
        base_price=200,
        duration_minutes=90,
        min_skill=60,
        required_specialization=WhoreSpecialization.PAIN_SLUT,
        stamina_cost=40,
        degradation=50,
        arousal_gain=30,
        satisfaction_base=75,
    ),
    ServiceType.HUMILIATION: Service(
        service_type=ServiceType.HUMILIATION,
        name="Humiliation Play",
        description="Verbal degradation and humiliation",
        base_price=80,
        duration_minutes=30,
        required_specialization=WhoreSpecialization.SUBMISSIVE,
        stamina_cost=15,
        degradation=40,
        arousal_gain=15,
        satisfaction_base=70,
    ),
    ServiceType.GANGBANG: Service(
        service_type=ServiceType.GANGBANG,
        name="Gangbang",
        description="Service multiple clients at once",
        base_price=300,
        duration_minutes=120,
        min_skill=50,
        required_specialization=WhoreSpecialization.COCK_SLEEVE,
        stamina_cost=60,
        degradation=60,
        arousal_gain=50,
        satisfaction_base=85,
    ),
    ServiceType.OVERNIGHT: Service(
        service_type=ServiceType.OVERNIGHT,
        name="Overnight",
        description="Full night of service",
        base_price=500,
        duration_minutes=480,
        min_beauty=50,
        stamina_cost=50,
        degradation=40,
        arousal_gain=60,
        satisfaction_base=75,
    ),
    ServiceType.GIRLFRIEND: Service(
        service_type=ServiceType.GIRLFRIEND,
        name="Girlfriend Experience",
        description="Intimate, romantic, affectionate",
        base_price=200,
        duration_minutes=180,
        min_beauty=60,
        min_skill=50,
        required_specialization=WhoreSpecialization.COURTESAN,
        stamina_cost=30,
        degradation=10,
        arousal_gain=40,
        satisfaction_base=80,
    ),
    ServiceType.LACTATION: Service(
        service_type=ServiceType.LACTATION,
        name="Nursing Service",
        description="Breastfeeding and lactation play",
        base_price=120,
        duration_minutes=45,
        required_specialization=WhoreSpecialization.MILK_MAID,
        stamina_cost=20,
        degradation=20,
        arousal_gain=30,
        satisfaction_base=75,
    ),
}


# =============================================================================
# CLIENT
# =============================================================================

@dataclass
class Client:
    """A brothel client."""
    
    client_id: str = ""
    name: str = ""
    
    # Type and status
    client_type: ClientType = ClientType.COMMONER
    mood: ClientMood = ClientMood.EAGER
    is_vip: bool = False
    is_regular: bool = False
    
    # Finances
    wealth: int = 100             # How much they can spend
    tip_tendency: float = 1.0     # Multiplier for tips
    
    # Preferences
    preferred_services: List[ServiceType] = field(default_factory=list)
    kinks: List[str] = field(default_factory=list)
    dislikes: List[str] = field(default_factory=list)
    
    # Physical preferences
    prefers_body_type: str = ""   # "slim", "curvy", "thick", "any"
    prefers_breast_size: str = "" # "small", "large", "huge", "any"
    prefers_species: str = ""     # "human", "elf", "catgirl", "any"
    
    # Stats
    stamina: int = 50             # How long they last
    cock_size: str = "average"    # "small", "average", "large", "huge"
    roughness: int = 50           # 0-100, how rough they are
    
    # History
    visits: int = 0
    total_spent: int = 0
    favorite_worker: str = ""
    
    def get_payment_ability(self) -> int:
        """Get how much they can pay."""
        type_mult = {
            ClientType.COMMONER: 1.0,
            ClientType.MERCHANT: 2.0,
            ClientType.NOBLE: 5.0,
            ClientType.ROYAL: 10.0,
            ClientType.ADVENTURER: 1.5,
            ClientType.SOLDIER: 0.8,
            ClientType.CLERGY: 1.5,
            ClientType.MONSTER: 0.5,
            ClientType.VIP: 8.0,
        }
        return int(self.wealth * type_mult.get(self.client_type, 1.0))
    
    def calculate_tip(self, satisfaction: int, base_price: int) -> int:
        """Calculate tip based on satisfaction."""
        if satisfaction < 50:
            return 0
        
        tip_percent = (satisfaction - 50) * 2  # 0-100%
        tip = int(base_price * (tip_percent / 100) * self.tip_tendency)
        
        # Mood affects tipping
        if self.mood == ClientMood.ROMANTIC:
            tip = int(tip * 1.5)
        elif self.mood == ClientMood.DEMANDING:
            tip = int(tip * 0.5)
        elif self.mood == ClientMood.DRUNK:
            tip = int(tip * random.uniform(0.5, 2.0))
        
        return tip


@dataclass
class ClientReview:
    """A client's review."""
    
    review_id: str = ""
    client_name: str = ""
    worker_name: str = ""
    worker_dbref: str = ""
    
    # Rating
    rating: ReviewRating = ReviewRating.AVERAGE
    
    # Details
    service_type: ServiceType = ServiceType.STANDARD
    satisfaction: int = 50
    
    # Comments
    comment: str = ""
    
    # Timing
    date: Optional[datetime] = None
    
    def generate_comment(self) -> str:
        """Generate a review comment."""
        if self.rating == ReviewRating.LEGENDARY:
            comments = [
                f"Best night of my life. {self.worker_name} is a goddess.",
                f"I'm ruined for anyone else. {self.worker_name} is perfection.",
                f"Worth every gold piece and more. Absolutely incredible.",
            ]
        elif self.rating == ReviewRating.EXCELLENT:
            comments = [
                f"{self.worker_name} knows exactly what they're doing.",
                f"Highly recommend. Will definitely return.",
                f"Exceeded all expectations.",
            ]
        elif self.rating == ReviewRating.GOOD:
            comments = [
                f"Pleasant experience with {self.worker_name}.",
                f"Good service, fair price.",
                f"Would visit again.",
            ]
        elif self.rating == ReviewRating.AVERAGE:
            comments = [
                "It was fine.",
                "Got what I paid for.",
                "Nothing special but no complaints.",
            ]
        elif self.rating == ReviewRating.POOR:
            comments = [
                "Disappointing.",
                "Expected more for the price.",
                "Won't be returning.",
            ]
        else:
            comments = [
                "Waste of money.",
                "Terrible experience.",
                "Avoid.",
            ]
        
        self.comment = random.choice(comments)
        return self.comment


# =============================================================================
# CLIENT GENERATOR
# =============================================================================

# Name pools
MALE_NAMES = [
    "Aldric", "Bram", "Corvin", "Darian", "Edmund", "Felix", "Gareth",
    "Henrik", "Ivan", "Jasper", "Kael", "Lucian", "Marcus", "Nikolai",
    "Orion", "Pierce", "Quinn", "Roland", "Sebastian", "Theron",
]

NOBLE_TITLES = ["Lord", "Baron", "Count", "Duke", "Sir"]
MERCHANT_TITLES = ["Master", "Guildsman"]


def generate_client(
    client_type: Optional[ClientType] = None,
    mood: Optional[ClientMood] = None,
) -> Client:
    """Generate a random client."""
    
    # Random type if not specified
    if client_type is None:
        weights = [40, 20, 10, 2, 15, 10, 2, 1, 0]  # Commoner most common
        types = list(ClientType)
        client_type = random.choices(types, weights=weights)[0]
    
    # Random mood if not specified
    if mood is None:
        mood = random.choice(list(ClientMood))
    
    # Generate name
    base_name = random.choice(MALE_NAMES)
    if client_type == ClientType.NOBLE:
        name = f"{random.choice(NOBLE_TITLES)} {base_name}"
    elif client_type == ClientType.MERCHANT:
        name = f"{random.choice(MERCHANT_TITLES)} {base_name}"
    else:
        name = base_name
    
    # Wealth based on type
    wealth_ranges = {
        ClientType.COMMONER: (30, 100),
        ClientType.MERCHANT: (100, 300),
        ClientType.NOBLE: (300, 1000),
        ClientType.ROYAL: (1000, 5000),
        ClientType.ADVENTURER: (50, 500),
        ClientType.SOLDIER: (20, 80),
        ClientType.CLERGY: (50, 200),
        ClientType.MONSTER: (10, 100),
        ClientType.VIP: (500, 2000),
    }
    wealth_min, wealth_max = wealth_ranges.get(client_type, (50, 150))
    
    # Random preferences
    services = [
        ServiceType.STANDARD,
        ServiceType.ORAL,
        ServiceType.ANAL,
        ServiceType.MASSAGE,
    ]
    if client_type == ClientType.NOBLE:
        services.append(ServiceType.GIRLFRIEND)
    if mood == ClientMood.ROUGH:
        services.extend([ServiceType.BDSM_LIGHT, ServiceType.BDSM_HEAVY])
    
    # Kinks
    all_kinks = [
        "big breasts", "small breasts", "lactation", "pregnant",
        "anal", "deepthroat", "bondage", "spanking", "feet",
        "roleplay", "uniforms", "public", "breeding",
    ]
    kinks = random.sample(all_kinks, k=random.randint(1, 3))
    
    # Roughness based on mood
    if mood == ClientMood.ROUGH:
        roughness = random.randint(60, 100)
    elif mood == ClientMood.ROMANTIC:
        roughness = random.randint(10, 40)
    elif mood == ClientMood.DEMANDING:
        roughness = random.randint(50, 80)
    else:
        roughness = random.randint(30, 70)
    
    return Client(
        client_id=f"CLI-{datetime.now().strftime('%H%M%S')}-{random.randint(100, 999)}",
        name=name,
        client_type=client_type,
        mood=mood,
        is_vip=client_type in [ClientType.NOBLE, ClientType.ROYAL, ClientType.VIP],
        wealth=random.randint(wealth_min, wealth_max),
        tip_tendency=random.uniform(0.5, 2.0),
        preferred_services=random.sample(services, k=min(3, len(services))),
        kinks=kinks,
        stamina=random.randint(20, 80),
        cock_size=random.choice(["small", "average", "average", "large", "huge"]),
        roughness=roughness,
    )


# =============================================================================
# WORK SESSION
# =============================================================================

@dataclass
class WorkSession:
    """A single work session with a client."""
    
    session_id: str = ""
    
    # Participants
    worker_dbref: str = ""
    worker_name: str = ""
    client: Optional[Client] = None
    
    # Service
    service: Optional[Service] = None
    
    # Timing
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    actual_duration: int = 0
    
    # Financial
    base_price: int = 0
    modifiers: Dict[str, float] = field(default_factory=dict)
    final_price: int = 0
    tip: int = 0
    house_cut: int = 0
    worker_earnings: int = 0
    
    # Performance
    client_satisfaction: int = 50
    worker_performance: int = 50
    
    # Effects on worker
    stamina_spent: int = 0
    degradation_gained: int = 0
    arousal_gained: int = 0
    orgasms: int = 0
    cum_received_ml: int = 0
    
    # Notes
    events: List[str] = field(default_factory=list)
    
    def calculate_price(self, worker_beauty: int, worker_skill: int, reputation: int) -> int:
        """Calculate final price with modifiers."""
        if not self.service:
            return 0
        
        self.base_price = self.service.base_price
        
        # Beauty modifier
        if worker_beauty >= 80:
            self.modifiers["beauty_premium"] = 1.5
        elif worker_beauty >= 60:
            self.modifiers["beauty_premium"] = 1.2
        
        # Skill modifier
        if worker_skill >= 80:
            self.modifiers["skill_premium"] = 1.3
        elif worker_skill >= 60:
            self.modifiers["skill_premium"] = 1.1
        
        # Reputation modifier
        if reputation >= 80:
            self.modifiers["reputation"] = 1.4
        elif reputation >= 60:
            self.modifiers["reputation"] = 1.2
        elif reputation < 30:
            self.modifiers["reputation"] = 0.8
        
        # Client type modifier
        if self.client:
            if self.client.is_vip:
                self.modifiers["vip"] = 1.5
            if self.client.client_type == ClientType.NOBLE:
                self.modifiers["noble"] = 1.3
            elif self.client.client_type == ClientType.ROYAL:
                self.modifiers["royal"] = 2.0
        
        # Calculate final
        total_mult = 1.0
        for mult in self.modifiers.values():
            total_mult *= mult
        
        self.final_price = int(self.base_price * total_mult)
        return self.final_price
    
    def calculate_satisfaction(
        self,
        worker_skill: int,
        worker_beauty: int,
        worker_enthusiasm: int,
    ) -> int:
        """Calculate client satisfaction."""
        if not self.service or not self.client:
            return 50
        
        satisfaction = self.service.satisfaction_base
        
        # Skill contribution
        satisfaction += (worker_skill - 50) // 2
        
        # Beauty contribution
        satisfaction += (worker_beauty - 50) // 4
        
        # Enthusiasm
        satisfaction += (worker_enthusiasm - 50) // 3
        
        # Client mood effects
        if self.client.mood == ClientMood.DEMANDING:
            satisfaction -= 10  # Harder to please
        elif self.client.mood == ClientMood.EAGER:
            satisfaction += 10  # Easy to please
        elif self.client.mood == ClientMood.NERVOUS:
            satisfaction += 5   # Grateful
        
        # Kink matching would add bonus here
        
        # Clamp
        self.client_satisfaction = max(0, min(100, satisfaction))
        return self.client_satisfaction
    
    def complete(self, house_cut_percent: float = 0.5) -> str:
        """Complete the session and calculate earnings."""
        self.end_time = datetime.now()
        
        if self.client:
            self.tip = self.client.calculate_tip(self.client_satisfaction, self.final_price)
        
        total = self.final_price + self.tip
        self.house_cut = int(total * house_cut_percent)
        self.worker_earnings = total - self.house_cut
        
        # Effects
        if self.service:
            self.stamina_spent = self.service.stamina_cost
            self.degradation_gained = self.service.degradation
            self.arousal_gained = self.service.arousal_gain
        
        # Cum received (based on service type and client)
        if self.service and self.service.service_type in [
            ServiceType.STANDARD, ServiceType.ANAL, ServiceType.BREEDING,
            ServiceType.GANGBANG
        ]:
            base_cum = 20
            if self.client and self.client.cock_size == "large":
                base_cum = 30
            elif self.client and self.client.cock_size == "huge":
                base_cum = 50
            
            if self.service.service_type == ServiceType.GANGBANG:
                base_cum *= 5  # Multiple clients
            
            self.cum_received_ml = base_cum
        
        return self.get_summary()
    
    def get_summary(self) -> str:
        """Get session summary."""
        lines = [f"=== Session Complete ==="]
        lines.append(f"Worker: {self.worker_name}")
        lines.append(f"Client: {self.client.name if self.client else 'Unknown'}")
        lines.append(f"Service: {self.service.name if self.service else 'Unknown'}")
        lines.append(f"")
        lines.append(f"Satisfaction: {self.client_satisfaction}/100")
        lines.append(f"Price: {self.final_price}g + {self.tip}g tip")
        lines.append(f"House Cut: {self.house_cut}g")
        lines.append(f"Worker Earnings: {self.worker_earnings}g")
        
        return "\n".join(lines)


# =============================================================================
# WORKER STATS
# =============================================================================

@dataclass
class WhoreStats:
    """Stats for a brothel worker."""
    
    worker_dbref: str = ""
    worker_name: str = ""
    
    # Appearance
    beauty: int = 50              # 0-100
    body_type: str = "average"    # "slim", "average", "curvy", "thick"
    breast_size: str = "average"
    
    # Skills
    oral_skill: int = 30
    sex_skill: int = 30
    anal_skill: int = 30
    seduction: int = 30
    dancing: int = 30
    massage: int = 30
    bdsm_skill: int = 0
    
    # Specialization
    specialization: WhoreSpecialization = WhoreSpecialization.NONE
    
    # Reputation
    reputation: int = 50          # 0-100
    reviews: List[ClientReview] = field(default_factory=list)
    average_rating: float = 3.0
    
    # Work stats
    clients_served: int = 0
    total_earnings: int = 0
    sessions_today: int = 0
    earnings_today: int = 0
    
    # Current state
    current_stamina: int = 100
    current_arousal: int = 0
    degradation_level: int = 0
    
    # Availability
    is_working: bool = False
    current_client: Optional[str] = None
    shift_start: Optional[time] = None
    shift_end: Optional[time] = None
    
    @property
    def overall_skill(self) -> int:
        """Get overall skill average."""
        return (self.oral_skill + self.sex_skill + self.anal_skill + 
                self.seduction + self.dancing) // 5
    
    def add_review(self, review: ClientReview) -> None:
        """Add a review and update rating."""
        self.reviews.append(review)
        
        # Recalculate average
        total = sum(r.rating.value for r in self.reviews)
        self.average_rating = total / len(self.reviews)
        
        # Update reputation based on reviews
        if self.average_rating >= 5:
            self.reputation = min(100, self.reputation + 5)
        elif self.average_rating >= 4:
            self.reputation = min(100, self.reputation + 2)
        elif self.average_rating < 3:
            self.reputation = max(0, self.reputation - 3)
    
    def can_perform(self, service: Service) -> Tuple[bool, str]:
        """Check if can perform a service."""
        if service.min_beauty > self.beauty:
            return False, f"Need {service.min_beauty} beauty (have {self.beauty})"
        
        if service.min_skill > self.overall_skill:
            return False, f"Need {service.min_skill} skill (have {self.overall_skill})"
        
        if service.required_specialization:
            if self.specialization != service.required_specialization:
                return False, f"Need {service.required_specialization.value} specialization"
        
        if service.stamina_cost > self.current_stamina:
            return False, f"Too exhausted (need {service.stamina_cost} stamina)"
        
        return True, "Can perform"
    
    def complete_session(self, session: WorkSession) -> str:
        """Process completed session effects."""
        self.clients_served += 1
        self.sessions_today += 1
        self.total_earnings += session.worker_earnings
        self.earnings_today += session.worker_earnings
        
        self.current_stamina = max(0, self.current_stamina - session.stamina_spent)
        self.current_arousal = min(100, self.current_arousal + session.arousal_gained)
        self.degradation_level = min(100, self.degradation_level + session.degradation_gained)
        
        # Skill gains from practice
        if session.service:
            if session.service.service_type == ServiceType.ORAL:
                self.oral_skill = min(100, self.oral_skill + 1)
            elif session.service.service_type in [ServiceType.STANDARD, ServiceType.BREEDING]:
                self.sex_skill = min(100, self.sex_skill + 1)
            elif session.service.service_type == ServiceType.ANAL:
                self.anal_skill = min(100, self.anal_skill + 1)
        
        self.is_working = False
        self.current_client = None
        
        return f"Session complete. Earned {session.worker_earnings}g. Stamina: {self.current_stamina}/100"
    
    def rest(self, hours: float = 8.0) -> str:
        """Rest to recover stamina."""
        recovery = int(hours * 10)
        self.current_stamina = min(100, self.current_stamina + recovery)
        
        # Degradation fades slowly
        self.degradation_level = max(0, self.degradation_level - int(hours))
        
        return f"Rested {hours} hours. Stamina: {self.current_stamina}/100"
    
    def daily_reset(self) -> None:
        """Reset daily counters."""
        self.sessions_today = 0
        self.earnings_today = 0
    
    def get_status(self) -> str:
        """Get worker status."""
        lines = [f"=== {self.worker_name} ==="]
        
        lines.append(f"\n--- Appearance ---")
        lines.append(f"Beauty: {self.beauty}/100")
        lines.append(f"Body: {self.body_type}, {self.breast_size} breasts")
        
        lines.append(f"\n--- Skills ---")
        lines.append(f"Oral: {self.oral_skill} | Sex: {self.sex_skill} | Anal: {self.anal_skill}")
        lines.append(f"Seduction: {self.seduction} | Dancing: {self.dancing}")
        if self.specialization != WhoreSpecialization.NONE:
            lines.append(f"Specialization: {self.specialization.value}")
        
        lines.append(f"\n--- Reputation ---")
        lines.append(f"Rating: {self.average_rating:.1f}/6 ({len(self.reviews)} reviews)")
        lines.append(f"Reputation: {self.reputation}/100")
        
        lines.append(f"\n--- Today ---")
        lines.append(f"Sessions: {self.sessions_today}")
        lines.append(f"Earnings: {self.earnings_today}g")
        lines.append(f"Stamina: {self.current_stamina}/100")
        
        lines.append(f"\n--- Career ---")
        lines.append(f"Total Clients: {self.clients_served}")
        lines.append(f"Total Earnings: {self.total_earnings}g")
        
        return "\n".join(lines)
    
    def to_dict(self) -> dict:
        return {
            "worker_dbref": self.worker_dbref,
            "worker_name": self.worker_name,
            "beauty": self.beauty,
            "body_type": self.body_type,
            "breast_size": self.breast_size,
            "oral_skill": self.oral_skill,
            "sex_skill": self.sex_skill,
            "anal_skill": self.anal_skill,
            "seduction": self.seduction,
            "specialization": self.specialization.value,
            "reputation": self.reputation,
            "average_rating": self.average_rating,
            "clients_served": self.clients_served,
            "total_earnings": self.total_earnings,
        }
    
    @classmethod
    def from_dict(cls, data: dict) -> "WhoreStats":
        stats = cls()
        for key, value in data.items():
            if key == "specialization":
                stats.specialization = WhoreSpecialization(value)
            elif hasattr(stats, key):
                setattr(stats, key, value)
        return stats


# =============================================================================
# BROTHEL
# =============================================================================

@dataclass
class Brothel:
    """A brothel establishment."""
    
    brothel_id: str = ""
    name: str = "The Velvet Rose"
    
    # Location
    location_dbref: str = ""
    
    # Owner
    owner_dbref: str = ""
    owner_name: str = ""
    madam_dbref: str = ""
    madam_name: str = ""
    
    # Workers
    workers: Dict[str, WhoreStats] = field(default_factory=dict)
    max_workers: int = 10
    
    # Finances
    house_cut_percent: float = 0.5
    gold_balance: int = 1000
    daily_expenses: int = 50
    
    # Reputation
    reputation: int = 50
    tier: str = "common"          # "dive", "common", "upscale", "luxury", "legendary"
    
    # Services offered
    services_offered: List[ServiceType] = field(default_factory=list)
    
    # Stats
    total_clients: int = 0
    total_revenue: int = 0
    daily_clients: int = 0
    daily_revenue: int = 0
    
    # Current
    clients_waiting: List[Client] = field(default_factory=list)
    active_sessions: List[WorkSession] = field(default_factory=list)
    
    def add_worker(self, worker_dbref: str, worker_name: str) -> str:
        """Add a worker to the brothel."""
        if len(self.workers) >= self.max_workers:
            return "Brothel is at capacity."
        
        stats = WhoreStats(worker_dbref=worker_dbref, worker_name=worker_name)
        self.workers[worker_dbref] = stats
        
        return f"{worker_name} has joined {self.name}."
    
    def remove_worker(self, worker_dbref: str) -> str:
        """Remove a worker."""
        if worker_dbref in self.workers:
            name = self.workers[worker_dbref].worker_name
            del self.workers[worker_dbref]
            return f"{name} has left {self.name}."
        return "Worker not found."
    
    def generate_clients(self, count: int = 3) -> List[Client]:
        """Generate waiting clients based on reputation."""
        clients = []
        
        for _ in range(count):
            # Higher reputation = better clients
            if self.reputation >= 80:
                type_weights = [10, 30, 30, 10, 10, 5, 3, 1, 1]
            elif self.reputation >= 60:
                type_weights = [30, 30, 20, 5, 10, 3, 1, 0, 1]
            elif self.reputation >= 40:
                type_weights = [50, 25, 10, 2, 8, 3, 1, 1, 0]
            else:
                type_weights = [60, 20, 5, 0, 5, 5, 2, 3, 0]
            
            client_type = random.choices(list(ClientType), weights=type_weights)[0]
            client = generate_client(client_type)
            clients.append(client)
        
        self.clients_waiting.extend(clients)
        return clients
    
    def assign_client(self, worker_dbref: str, client_id: str, service_type: ServiceType) -> Tuple[bool, str, Optional[WorkSession]]:
        """Assign a client to a worker."""
        if worker_dbref not in self.workers:
            return False, "Worker not found.", None
        
        worker = self.workers[worker_dbref]
        
        # Find client
        client = None
        for c in self.clients_waiting:
            if c.client_id == client_id:
                client = c
                break
        
        if not client:
            return False, "Client not found.", None
        
        # Get service
        if service_type not in SERVICE_MENU:
            return False, "Service not available.", None
        
        service = SERVICE_MENU[service_type]
        
        # Check if worker can perform
        can, msg = worker.can_perform(service)
        if not can:
            return False, msg, None
        
        # Check if client can afford
        if client.get_payment_ability() < service.base_price:
            return False, "Client cannot afford this service.", None
        
        # Create session
        session = WorkSession(
            session_id=f"SESS-{datetime.now().strftime('%Y%m%d%H%M%S')}-{random.randint(100, 999)}",
            worker_dbref=worker_dbref,
            worker_name=worker.worker_name,
            client=client,
            service=service,
            start_time=datetime.now(),
        )
        
        # Calculate price
        session.calculate_price(worker.beauty, worker.overall_skill, worker.reputation)
        
        # Remove client from waiting
        self.clients_waiting.remove(client)
        
        # Mark worker as busy
        worker.is_working = True
        worker.current_client = client.client_id
        
        # Add to active sessions
        self.active_sessions.append(session)
        
        return True, f"{worker.worker_name} takes {client.name} for {service.name}.", session
    
    def complete_session(self, session_id: str, worker_enthusiasm: int = 50) -> Tuple[bool, str]:
        """Complete an active session."""
        session = None
        for s in self.active_sessions:
            if s.session_id == session_id:
                session = s
                break
        
        if not session:
            return False, "Session not found."
        
        worker = self.workers.get(session.worker_dbref)
        if not worker:
            return False, "Worker not found."
        
        # Calculate satisfaction
        session.calculate_satisfaction(
            worker.overall_skill,
            worker.beauty,
            worker_enthusiasm,
        )
        
        # Complete and calculate earnings
        session.complete(self.house_cut_percent)
        
        # Update worker
        worker.complete_session(session)
        
        # Create review
        if session.client_satisfaction >= 90:
            rating = ReviewRating.LEGENDARY if random.random() < 0.2 else ReviewRating.EXCELLENT
        elif session.client_satisfaction >= 70:
            rating = ReviewRating.GOOD
        elif session.client_satisfaction >= 50:
            rating = ReviewRating.AVERAGE
        elif session.client_satisfaction >= 30:
            rating = ReviewRating.POOR
        else:
            rating = ReviewRating.TERRIBLE
        
        review = ClientReview(
            review_id=f"REV-{random.randint(1000, 9999)}",
            client_name=session.client.name if session.client else "Unknown",
            worker_name=worker.worker_name,
            worker_dbref=worker.worker_dbref,
            rating=rating,
            service_type=session.service.service_type if session.service else ServiceType.STANDARD,
            satisfaction=session.client_satisfaction,
            date=datetime.now(),
        )
        review.generate_comment()
        worker.add_review(review)
        
        # Update brothel stats
        self.gold_balance += session.house_cut
        self.total_clients += 1
        self.total_revenue += session.final_price + session.tip
        self.daily_clients += 1
        self.daily_revenue += session.final_price + session.tip
        
        # Update reputation based on satisfaction
        if session.client_satisfaction >= 80:
            self.reputation = min(100, self.reputation + 1)
        elif session.client_satisfaction < 40:
            self.reputation = max(0, self.reputation - 1)
        
        # Remove from active
        self.active_sessions.remove(session)
        
        return True, session.get_summary()
    
    def end_day(self) -> str:
        """Process end of day."""
        lines = [f"=== {self.name} Daily Report ==="]
        
        # Pay expenses
        self.gold_balance -= self.daily_expenses
        
        lines.append(f"Clients Served: {self.daily_clients}")
        lines.append(f"Daily Revenue: {self.daily_revenue}g")
        lines.append(f"House Cut: {int(self.daily_revenue * self.house_cut_percent)}g")
        lines.append(f"Expenses: {self.daily_expenses}g")
        lines.append(f"Balance: {self.gold_balance}g")
        
        # Reset daily counters
        self.daily_clients = 0
        self.daily_revenue = 0
        
        for worker in self.workers.values():
            worker.daily_reset()
        
        return "\n".join(lines)
    
    def get_status(self) -> str:
        """Get brothel status."""
        lines = [f"=== {self.name} ==="]
        lines.append(f"Tier: {self.tier.upper()}")
        lines.append(f"Reputation: {self.reputation}/100")
        
        lines.append(f"\n--- Finances ---")
        lines.append(f"Balance: {self.gold_balance}g")
        lines.append(f"House Cut: {self.house_cut_percent * 100:.0f}%")
        lines.append(f"Daily Expenses: {self.daily_expenses}g")
        
        lines.append(f"\n--- Workers ({len(self.workers)}/{self.max_workers}) ---")
        for worker in self.workers.values():
            status = "BUSY" if worker.is_working else "Available"
            lines.append(f"  {worker.worker_name}: {status} | Rating: {worker.average_rating:.1f}")
        
        lines.append(f"\n--- Current ---")
        lines.append(f"Clients Waiting: {len(self.clients_waiting)}")
        lines.append(f"Active Sessions: {len(self.active_sessions)}")
        
        lines.append(f"\n--- Today ---")
        lines.append(f"Clients: {self.daily_clients}")
        lines.append(f"Revenue: {self.daily_revenue}g")
        
        lines.append(f"\n--- Lifetime ---")
        lines.append(f"Total Clients: {self.total_clients}")
        lines.append(f"Total Revenue: {self.total_revenue}g")
        
        return "\n".join(lines)
    
    def to_dict(self) -> dict:
        return {
            "brothel_id": self.brothel_id,
            "name": self.name,
            "owner_dbref": self.owner_dbref,
            "reputation": self.reputation,
            "tier": self.tier,
            "gold_balance": self.gold_balance,
            "house_cut_percent": self.house_cut_percent,
            "total_clients": self.total_clients,
            "total_revenue": self.total_revenue,
            "workers": {k: v.to_dict() for k, v in self.workers.items()},
        }


# =============================================================================
# WHORE MIXIN
# =============================================================================

class WhoreMixin:
    """Mixin for brothel workers."""
    
    @property
    def whore_stats(self) -> WhoreStats:
        """Get whore stats."""
        data = self.db.whore_stats
        if data:
            return WhoreStats.from_dict(data)
        return WhoreStats(worker_dbref=self.dbref, worker_name=self.key)
    
    @whore_stats.setter
    def whore_stats(self, stats: WhoreStats) -> None:
        """Set whore stats."""
        self.db.whore_stats = stats.to_dict()


__all__ = [
    "ServiceType",
    "ClientType",
    "ClientMood",
    "WhoreSpecialization",
    "ReviewRating",
    "Service",
    "SERVICE_MENU",
    "Client",
    "ClientReview",
    "generate_client",
    "WorkSession",
    "WhoreStats",
    "Brothel",
    "WhoreMixin",
    "BrothelCmdSet",
]

# Import commands
from .commands import BrothelCmdSet
