"""
Auction System
==============

Complete auction mechanics including:
- Lot preparation and display
- Bidding management
- Auction events
- Sale completion
"""

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any, Tuple
from enum import Enum
from datetime import datetime, timedelta
import random


# =============================================================================
# ENUMS
# =============================================================================

class AuctionType(Enum):
    """Types of auctions."""
    STANDARD = "standard"         # Normal bidding
    SILENT = "silent"             # Sealed bids
    DUTCH = "dutch"               # Price drops until bought
    RESERVE = "reserve"           # Has minimum price
    NO_RESERVE = "no_reserve"     # Sells to highest bidder
    PRIVATE = "private"           # Invitation only


class LotStatus(Enum):
    """Status of an auction lot."""
    PREPARING = "preparing"
    DISPLAYED = "displayed"
    ACTIVE = "active"
    SOLD = "sold"
    UNSOLD = "unsold"
    WITHDRAWN = "withdrawn"


class DisplayPosition(Enum):
    """Positions for displaying lots."""
    STANDING = "standing"
    KNEELING = "kneeling"
    BENT_OVER = "bent_over"
    SPREADEAGLE = "spreadeagle"
    ON_PLATFORM = "on_platform"
    IN_CAGE = "in_cage"
    ON_BLOCK = "on_block"
    SUSPENDED = "suspended"


# =============================================================================
# BID
# =============================================================================

@dataclass
class Bid:
    """A single bid."""
    
    bid_id: str = ""
    bidder_dbref: str = ""
    bidder_name: str = ""
    
    amount: int = 0
    timestamp: Optional[datetime] = None
    
    is_winning: bool = False
    was_outbid: bool = False


# =============================================================================
# AUCTION LOT
# =============================================================================

@dataclass
class AuctionLot:
    """A lot being auctioned."""
    
    lot_id: str = ""
    lot_number: int = 1
    
    # Subject
    subject_dbref: str = ""
    subject_name: str = ""
    
    # Seller
    seller_dbref: str = ""
    seller_name: str = ""
    
    # Pricing
    starting_bid: int = 100
    reserve_price: int = 0
    current_bid: int = 0
    buy_now_price: int = 0        # Instant purchase price (0 = not available)
    
    # Bids
    bids: List[Bid] = field(default_factory=list)
    bid_increment: int = 10       # Minimum bid increase
    
    # Status
    status: LotStatus = LotStatus.PREPARING
    
    # Display
    display_position: DisplayPosition = DisplayPosition.ON_BLOCK
    is_nude: bool = True
    is_bound: bool = False
    is_gagged: bool = False
    
    # Description
    description: str = ""
    features: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)
    
    # Subject stats (for display)
    grade: str = ""
    training: str = ""
    value_estimate: int = 0
    
    # Virginity status
    vaginal_virgin: bool = False
    anal_virgin: bool = False
    oral_virgin: bool = False
    
    # Special features
    is_pregnant: bool = False
    is_lactating: bool = False
    is_in_heat: bool = False
    is_futanari: bool = False
    
    # Timing
    auction_start: Optional[datetime] = None
    auction_end: Optional[datetime] = None
    
    # Results
    winning_bidder_dbref: str = ""
    winning_bidder_name: str = ""
    final_price: int = 0
    
    @property
    def highest_bidder(self) -> Optional[Bid]:
        """Get the highest bid."""
        if not self.bids:
            return None
        return max(self.bids, key=lambda b: b.amount)
    
    @property
    def bid_count(self) -> int:
        """Get number of bids."""
        return len(self.bids)
    
    def place_bid(self, bidder_dbref: str, bidder_name: str, amount: int) -> Tuple[bool, str]:
        """
        Place a bid.
        Returns (success, message).
        """
        # Validate bid
        min_bid = self.starting_bid if not self.bids else self.current_bid + self.bid_increment
        
        if amount < min_bid:
            return False, f"Bid must be at least {min_bid} gold."
        
        # Check for buy now
        if self.buy_now_price > 0 and amount >= self.buy_now_price:
            return self.buy_now(bidder_dbref, bidder_name)
        
        # Mark previous winning bid as outbid
        if self.bids:
            highest = self.highest_bidder
            if highest:
                highest.is_winning = False
                highest.was_outbid = True
        
        # Create new bid
        bid = Bid(
            bid_id=f"BID-{datetime.now().strftime('%H%M%S')}-{random.randint(100, 999)}",
            bidder_dbref=bidder_dbref,
            bidder_name=bidder_name,
            amount=amount,
            timestamp=datetime.now(),
            is_winning=True,
        )
        
        self.bids.append(bid)
        self.current_bid = amount
        
        return True, f"{bidder_name} bids {amount} gold!"
    
    def buy_now(self, buyer_dbref: str, buyer_name: str) -> Tuple[bool, str]:
        """Execute buy now."""
        if self.buy_now_price <= 0:
            return False, "Buy now not available."
        
        # Create final bid
        bid = Bid(
            bid_id=f"BID-NOW-{random.randint(1000, 9999)}",
            bidder_dbref=buyer_dbref,
            bidder_name=buyer_name,
            amount=self.buy_now_price,
            timestamp=datetime.now(),
            is_winning=True,
        )
        
        self.bids.append(bid)
        self.current_bid = self.buy_now_price
        
        # Complete sale
        self.complete_sale(buyer_dbref, buyer_name, self.buy_now_price)
        
        return True, f"SOLD! {buyer_name} uses Buy Now for {self.buy_now_price} gold!"
    
    def complete_sale(self, buyer_dbref: str, buyer_name: str, price: int) -> str:
        """Complete the sale."""
        self.status = LotStatus.SOLD
        self.winning_bidder_dbref = buyer_dbref
        self.winning_bidder_name = buyer_name
        self.final_price = price
        self.auction_end = datetime.now()
        
        return f"SOLD! {self.subject_name} goes to {buyer_name} for {price} gold!"
    
    def fail_to_sell(self) -> str:
        """Mark as unsold."""
        self.status = LotStatus.UNSOLD
        self.auction_end = datetime.now()
        
        if self.reserve_price > 0 and self.current_bid < self.reserve_price:
            return f"Reserve not met. {self.subject_name} did not sell."
        return f"No bids. {self.subject_name} did not sell."
    
    def get_display_description(self) -> str:
        """Get the auctioneer's description."""
        lines = []
        
        # Opening
        lines.append(f"=== LOT #{self.lot_number}: {self.subject_name} ===")
        
        # Position description
        pos_descs = {
            DisplayPosition.STANDING: "stands on the block",
            DisplayPosition.KNEELING: "kneels on the platform",
            DisplayPosition.BENT_OVER: "is bent over the display rail",
            DisplayPosition.SPREADEAGLE: "is spread wide for inspection",
            DisplayPosition.ON_PLATFORM: "is displayed on the rotating platform",
            DisplayPosition.IN_CAGE: "waits in a display cage",
            DisplayPosition.ON_BLOCK: "stands upon the auction block",
            DisplayPosition.SUSPENDED: "hangs suspended for viewing",
        }
        lines.append(f"\n{self.subject_name} {pos_descs.get(self.display_position, 'is presented')}.")
        
        # Condition
        if self.is_nude:
            lines.append("Completely nude for inspection.")
        if self.is_bound:
            lines.append("Bound and restrained.")
        if self.is_gagged:
            lines.append("Gagged for silence.")
        
        # Grade and training
        if self.grade:
            lines.append(f"\nGrade: {self.grade.upper()}")
        if self.training:
            lines.append(f"Training: {self.training}")
        
        # Special features
        specials = []
        if self.vaginal_virgin:
            specials.append("VAGINAL VIRGIN")
        if self.anal_virgin:
            specials.append("ANAL VIRGIN")
        if self.oral_virgin:
            specials.append("ORAL VIRGIN")
        if self.is_pregnant:
            specials.append("PREGNANT")
        if self.is_lactating:
            specials.append("LACTATING")
        if self.is_in_heat:
            specials.append("IN HEAT")
        if self.is_futanari:
            specials.append("FUTANARI")
        
        if specials:
            lines.append(f"\n*** {' | '.join(specials)} ***")
        
        # Features
        if self.features:
            lines.append("\nFeatures:")
            for feature in self.features:
                lines.append(f"  • {feature}")
        
        # Warnings
        if self.warnings:
            lines.append("\nWarnings:")
            for warning in self.warnings:
                lines.append(f"  ⚠ {warning}")
        
        # Description
        if self.description:
            lines.append(f"\n{self.description}")
        
        # Pricing
        lines.append(f"\n--- Bidding ---")
        lines.append(f"Starting Bid: {self.starting_bid} gold")
        if self.reserve_price:
            lines.append(f"Reserve: {'MET' if self.current_bid >= self.reserve_price else 'NOT MET'}")
        if self.buy_now_price:
            lines.append(f"Buy Now: {self.buy_now_price} gold")
        lines.append(f"Current Bid: {self.current_bid} gold ({self.bid_count} bids)")
        
        if self.highest_bidder:
            lines.append(f"High Bidder: {self.highest_bidder.bidder_name}")
        
        return "\n".join(lines)
    
    def to_dict(self) -> dict:
        return {
            "lot_id": self.lot_id,
            "lot_number": self.lot_number,
            "subject_dbref": self.subject_dbref,
            "subject_name": self.subject_name,
            "seller_dbref": self.seller_dbref,
            "seller_name": self.seller_name,
            "starting_bid": self.starting_bid,
            "reserve_price": self.reserve_price,
            "current_bid": self.current_bid,
            "buy_now_price": self.buy_now_price,
            "bid_count": self.bid_count,
            "status": self.status.value,
            "final_price": self.final_price,
            "winning_bidder_name": self.winning_bidder_name,
        }


# =============================================================================
# AUCTION
# =============================================================================

@dataclass
class Auction:
    """A complete auction event."""
    
    auction_id: str = ""
    name: str = "Slave Auction"
    
    # Type
    auction_type: AuctionType = AuctionType.STANDARD
    
    # Location
    location: str = ""
    location_dbref: str = ""
    
    # Host
    auctioneer_name: str = ""
    auctioneer_dbref: str = ""
    
    # Lots
    lots: List[AuctionLot] = field(default_factory=list)
    current_lot_index: int = 0
    
    # Timing
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    is_active: bool = False
    
    # Bidders
    registered_bidders: List[str] = field(default_factory=list)
    
    # Results
    total_lots: int = 0
    lots_sold: int = 0
    lots_unsold: int = 0
    total_revenue: int = 0
    
    @property
    def current_lot(self) -> Optional[AuctionLot]:
        """Get current lot being auctioned."""
        if 0 <= self.current_lot_index < len(self.lots):
            return self.lots[self.current_lot_index]
        return None
    
    def add_lot(self, lot: AuctionLot) -> str:
        """Add a lot to the auction."""
        lot.lot_number = len(self.lots) + 1
        self.lots.append(lot)
        self.total_lots += 1
        return f"Lot #{lot.lot_number} added: {lot.subject_name}"
    
    def register_bidder(self, bidder_dbref: str) -> str:
        """Register a bidder."""
        if bidder_dbref in self.registered_bidders:
            return "Already registered."
        self.registered_bidders.append(bidder_dbref)
        return "Registered for bidding."
    
    def start_auction(self) -> str:
        """Start the auction."""
        if not self.lots:
            return "No lots to auction."
        
        self.is_active = True
        self.start_time = datetime.now()
        self.current_lot_index = 0
        
        # Set first lot to active
        self.lots[0].status = LotStatus.ACTIVE
        self.lots[0].auction_start = datetime.now()
        
        return f"{self.name} begins! {len(self.lots)} lots to be sold."
    
    def call_lot(self) -> str:
        """Call the current lot (auctioneer announcement)."""
        lot = self.current_lot
        if not lot:
            return "No lot to call."
        
        return lot.get_display_description()
    
    def accept_bid(self, bidder_dbref: str, bidder_name: str, amount: int) -> Tuple[bool, str]:
        """Accept a bid on current lot."""
        if not self.is_active:
            return False, "Auction not active."
        
        if bidder_dbref not in self.registered_bidders:
            return False, "Not a registered bidder."
        
        lot = self.current_lot
        if not lot:
            return False, "No active lot."
        
        return lot.place_bid(bidder_dbref, bidder_name, amount)
    
    def close_lot(self) -> str:
        """Close bidding on current lot."""
        lot = self.current_lot
        if not lot:
            return "No lot to close."
        
        # Determine outcome
        if lot.bids:
            highest = lot.highest_bidder
            if highest:
                # Check reserve
                if lot.reserve_price and lot.current_bid < lot.reserve_price:
                    msg = lot.fail_to_sell()
                    self.lots_unsold += 1
                else:
                    msg = lot.complete_sale(
                        highest.bidder_dbref,
                        highest.bidder_name,
                        highest.amount
                    )
                    self.lots_sold += 1
                    self.total_revenue += highest.amount
        else:
            msg = lot.fail_to_sell()
            self.lots_unsold += 1
        
        return msg
    
    def next_lot(self) -> Tuple[bool, str]:
        """
        Move to next lot.
        Returns (has_next, message).
        """
        self.current_lot_index += 1
        
        if self.current_lot_index >= len(self.lots):
            return False, "No more lots."
        
        lot = self.current_lot
        lot.status = LotStatus.ACTIVE
        lot.auction_start = datetime.now()
        
        return True, f"Now presenting Lot #{lot.lot_number}: {lot.subject_name}"
    
    def end_auction(self) -> str:
        """End the auction."""
        self.is_active = False
        self.end_time = datetime.now()
        
        lines = [f"=== {self.name} Concluded ==="]
        lines.append(f"Total Lots: {self.total_lots}")
        lines.append(f"Sold: {self.lots_sold}")
        lines.append(f"Unsold: {self.lots_unsold}")
        lines.append(f"Total Revenue: {self.total_revenue} gold")
        
        return "\n".join(lines)
    
    def get_status(self) -> str:
        """Get auction status."""
        lines = [f"=== {self.name} ==="]
        lines.append(f"Status: {'ACTIVE' if self.is_active else 'INACTIVE'}")
        lines.append(f"Type: {self.auction_type.value}")
        lines.append(f"Auctioneer: {self.auctioneer_name}")
        lines.append(f"\nLots: {self.current_lot_index + 1}/{len(self.lots)}")
        lines.append(f"Registered Bidders: {len(self.registered_bidders)}")
        
        if self.current_lot:
            lines.append(f"\nCurrent Lot: #{self.current_lot.lot_number} - {self.current_lot.subject_name}")
            lines.append(f"Current Bid: {self.current_lot.current_bid} gold")
        
        lines.append(f"\nRevenue So Far: {self.total_revenue} gold")
        
        return "\n".join(lines)


# =============================================================================
# AUCTIONEER PHRASES
# =============================================================================

class AuctioneerPhrases:
    """Canned phrases for auction flavor."""
    
    LOT_INTROS = [
        "Ladies and gentlemen, feast your eyes on this fine specimen!",
        "What we have here is truly a prize catch!",
        "Behold! Fresh meat for your consideration!",
        "Now this one will make an excellent addition to any collection!",
        "A rare find! Don't miss your chance!",
    ]
    
    CALLING_BIDS = [
        "Do I hear {amount}?",
        "Who'll give me {amount}?",
        "Looking for {amount}, anyone?",
        "{amount} gold, who's interested?",
        "Can I get {amount} for this lovely piece?",
    ]
    
    BID_RECEIVED = [
        "{amount} from {bidder}!",
        "We have {amount}! Thank you, {bidder}!",
        "{bidder} with {amount}!",
        "The bid is {amount} from {bidder}!",
    ]
    
    ENCOURAGING_BIDS = [
        "Surely she's worth more than that!",
        "Look at those curves! Bid higher!",
        "Prime breeding stock! Don't be shy!",
        "You won't find better at this price!",
        "Think of the value! The potential!",
    ]
    
    GOING_ONCE = [
        "Going once...",
        "{amount} going once...",
        "At {amount}, going once...",
        "Do I hear more? Going once...",
    ]
    
    GOING_TWICE = [
        "Going twice...",
        "{amount} going twice...",
        "Last chance! Going twice...",
        "Final warning! Going twice...",
    ]
    
    SOLD = [
        "SOLD to {buyer} for {amount} gold!",
        "SOLD! {buyer} takes home this prize for {amount}!",
        "The hammer falls! SOLD to {buyer}!",
        "Congratulations {buyer}! She's yours for {amount}!",
    ]
    
    @classmethod
    def random_intro(cls) -> str:
        return random.choice(cls.LOT_INTROS)
    
    @classmethod
    def call_for_bid(cls, amount: int) -> str:
        return random.choice(cls.CALLING_BIDS).format(amount=amount)
    
    @classmethod
    def announce_bid(cls, amount: int, bidder: str) -> str:
        return random.choice(cls.BID_RECEIVED).format(amount=amount, bidder=bidder)
    
    @classmethod
    def encourage(cls) -> str:
        return random.choice(cls.ENCOURAGING_BIDS)
    
    @classmethod
    def going_once(cls, amount: int) -> str:
        return random.choice(cls.GOING_ONCE).format(amount=amount)
    
    @classmethod
    def going_twice(cls, amount: int) -> str:
        return random.choice(cls.GOING_TWICE).format(amount=amount)
    
    @classmethod
    def sold(cls, buyer: str, amount: int) -> str:
        return random.choice(cls.SOLD).format(buyer=buyer, amount=amount)


__all__ = [
    "AuctionType",
    "LotStatus",
    "DisplayPosition",
    "Bid",
    "AuctionLot",
    "Auction",
    "AuctioneerPhrases",
]
