"""
Slave Market & Auction System
=============================

Systems for trading owned characters:
- Slave market listings
- Auctions
- Direct sales
- Appraisal
"""

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any, Tuple
from enum import Enum
from datetime import datetime, timedelta
import random

from .economy import CurrencyType, format_currency, EconomyManager, Wallet
from .ownership import OwnershipType, OwnershipRecord, OwnershipSystem


# =============================================================================
# ENUMS
# =============================================================================

class ListingType(Enum):
    """Types of market listings."""
    SALE = "sale"              # Fixed price sale
    AUCTION = "auction"        # Timed auction
    RENTAL = "rental"          # Temporary loan
    BREEDING = "breeding"      # Breeding services
    TRADE = "trade"            # Trade for other property


class ListingStatus(Enum):
    """Status of a listing."""
    ACTIVE = "active"
    SOLD = "sold"
    EXPIRED = "expired"
    CANCELLED = "cancelled"
    PENDING = "pending"        # Awaiting approval


class AuctionStatus(Enum):
    """Status of an auction."""
    UPCOMING = "upcoming"
    ACTIVE = "active"
    ENDING_SOON = "ending_soon"  # Last hour
    ENDED = "ended"
    CANCELLED = "cancelled"


# =============================================================================
# APPRAISAL
# =============================================================================

@dataclass
class Appraisal:
    """Appraisal of a character's market value."""
    target_dbref: str
    target_name: str
    
    # Base value factors
    base_value: int = 100
    
    # Modifiers
    species_modifier: float = 1.0
    training_modifier: float = 1.0
    appearance_modifier: float = 1.0
    fertility_modifier: float = 1.0
    obedience_modifier: float = 1.0
    special_traits_modifier: float = 1.0
    
    # Final value
    appraised_value: int = 100
    
    # Notes
    notes: List[str] = field(default_factory=list)
    
    # Timestamp
    appraisal_date: Optional[datetime] = None
    
    def calculate_value(self) -> int:
        """Calculate final appraised value."""
        value = self.base_value
        value *= self.species_modifier
        value *= self.training_modifier
        value *= self.appearance_modifier
        value *= self.fertility_modifier
        value *= self.obedience_modifier
        value *= self.special_traits_modifier
        
        self.appraised_value = int(value)
        return self.appraised_value
    
    def get_summary(self) -> str:
        """Get appraisal summary."""
        lines = [
            f"=== Appraisal for {self.target_name} ===",
            f"Base Value: {self.base_value} gold",
            f"",
            "Modifiers:",
            f"  Species: x{self.species_modifier:.2f}",
            f"  Training: x{self.training_modifier:.2f}",
            f"  Appearance: x{self.appearance_modifier:.2f}",
            f"  Fertility: x{self.fertility_modifier:.2f}",
            f"  Obedience: x{self.obedience_modifier:.2f}",
            f"  Special Traits: x{self.special_traits_modifier:.2f}",
            f"",
            f"Final Appraised Value: {format_currency(self.appraised_value, CurrencyType.GOLD)}",
        ]
        
        if self.notes:
            lines.append("")
            lines.append("Notes:")
            for note in self.notes:
                lines.append(f"  - {note}")
        
        return "\n".join(lines)


def appraise_character(character) -> Appraisal:
    """
    Appraise a character's market value.
    """
    appraisal = Appraisal(
        target_dbref=character.dbref,
        target_name=character.key,
        base_value=100,
        appraisal_date=datetime.now(),
    )
    
    # Species modifier
    species = getattr(character, 'species', 'human')
    species_values = {
        'human': 1.0,
        'elf': 1.5,
        'catfolk': 1.3,
        'wolfkin': 1.2,
        'dragon': 3.0,
        'centaur': 2.0,
        'demon': 2.5,
        'angel': 3.0,
    }
    appraisal.species_modifier = species_values.get(species.lower(), 1.0)
    
    # Training modifier - check if they have training stats
    if hasattr(character, 'pet_stats'):
        stats = character.pet_stats
        training_level = len(getattr(stats, 'tricks_learned', []))
        appraisal.training_modifier = 1.0 + (training_level * 0.05)
        appraisal.notes.append(f"Knows {training_level} tricks")
    
    # Obedience modifier
    if hasattr(character, 'pet_stats'):
        obedience = getattr(character.pet_stats, 'obedience', 50)
        appraisal.obedience_modifier = 0.5 + (obedience / 100)
        if obedience >= 80:
            appraisal.notes.append("Highly obedient")
        elif obedience <= 20:
            appraisal.notes.append("Disobedient - needs breaking")
    
    # Fertility modifier
    if hasattr(character, 'fertility'):
        fertility = character.fertility
        appraisal.fertility_modifier = 0.8 + (fertility / 100) * 0.4
        if fertility >= 80:
            appraisal.notes.append("Highly fertile - excellent for breeding")
    
    # Special traits
    special_count = 0
    if hasattr(character, 'can_lactate') and character.can_lactate:
        special_count += 1
        appraisal.notes.append("Lactating")
    if hasattr(character, 'is_pregnant') and character.is_pregnant():
        special_count += 1
        appraisal.notes.append("Currently pregnant")
    if hasattr(character, 'has_knot') and character.has_knot:
        special_count += 1
        appraisal.notes.append("Has knot")
    
    appraisal.special_traits_modifier = 1.0 + (special_count * 0.2)
    
    # Calculate final value
    appraisal.calculate_value()
    
    return appraisal


# =============================================================================
# MARKET LISTING
# =============================================================================

@dataclass
class MarketListing:
    """A listing on the slave market."""
    listing_id: str
    
    # Seller
    seller_dbref: str = ""
    seller_name: str = ""
    
    # Property
    property_dbref: str = ""
    property_name: str = ""
    property_description: str = ""
    
    # Listing type
    listing_type: ListingType = ListingType.SALE
    status: ListingStatus = ListingStatus.ACTIVE
    
    # Pricing
    asking_price: int = 0
    currency: CurrencyType = CurrencyType.GOLD
    minimum_price: int = 0      # For negotiation
    buyout_price: int = 0       # Instant buy for auctions
    
    # Rental specific
    rental_duration_days: int = 0
    rental_price_per_day: int = 0
    
    # Timestamps
    created_at: Optional[datetime] = None
    expires_at: Optional[datetime] = None
    sold_at: Optional[datetime] = None
    
    # Buyer (when sold)
    buyer_dbref: str = ""
    buyer_name: str = ""
    final_price: int = 0
    
    def is_expired(self) -> bool:
        """Check if listing has expired."""
        if self.expires_at and datetime.now() >= self.expires_at:
            return True
        return False
    
    def can_purchase(self, buyer_wallet: Wallet) -> Tuple[bool, str]:
        """Check if buyer can purchase."""
        if self.status != ListingStatus.ACTIVE:
            return False, f"Listing is {self.status.value}."
        
        if self.is_expired():
            return False, "Listing has expired."
        
        if not buyer_wallet.can_afford(self.currency, self.asking_price):
            return False, f"Cannot afford {format_currency(self.asking_price, self.currency)}."
        
        return True, ""
    
    def get_summary(self) -> str:
        """Get listing summary."""
        lines = [
            f"[{self.listing_id}] {self.property_name}",
            f"  Type: {self.listing_type.value.title()}",
            f"  Price: {format_currency(self.asking_price, self.currency)}",
        ]
        
        if self.buyout_price > 0:
            lines.append(f"  Buyout: {format_currency(self.buyout_price, self.currency)}")
        
        if self.property_description:
            lines.append(f"  {self.property_description}")
        
        return "\n".join(lines)
    
    def to_dict(self) -> dict:
        return {
            "listing_id": self.listing_id,
            "seller_dbref": self.seller_dbref,
            "seller_name": self.seller_name,
            "property_dbref": self.property_dbref,
            "property_name": self.property_name,
            "property_description": self.property_description,
            "listing_type": self.listing_type.value,
            "status": self.status.value,
            "asking_price": self.asking_price,
            "currency": self.currency.value,
            "minimum_price": self.minimum_price,
            "buyout_price": self.buyout_price,
            "rental_duration_days": self.rental_duration_days,
            "rental_price_per_day": self.rental_price_per_day,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "expires_at": self.expires_at.isoformat() if self.expires_at else None,
            "sold_at": self.sold_at.isoformat() if self.sold_at else None,
            "buyer_dbref": self.buyer_dbref,
            "buyer_name": self.buyer_name,
            "final_price": self.final_price,
        }
    
    @classmethod
    def from_dict(cls, data: dict) -> "MarketListing":
        listing = cls(listing_id=data["listing_id"])
        listing.seller_dbref = data.get("seller_dbref", "")
        listing.seller_name = data.get("seller_name", "")
        listing.property_dbref = data.get("property_dbref", "")
        listing.property_name = data.get("property_name", "")
        listing.property_description = data.get("property_description", "")
        listing.listing_type = ListingType(data.get("listing_type", "sale"))
        listing.status = ListingStatus(data.get("status", "active"))
        listing.asking_price = data.get("asking_price", 0)
        listing.currency = CurrencyType(data.get("currency", "gold"))
        listing.minimum_price = data.get("minimum_price", 0)
        listing.buyout_price = data.get("buyout_price", 0)
        listing.rental_duration_days = data.get("rental_duration_days", 0)
        listing.rental_price_per_day = data.get("rental_price_per_day", 0)
        
        if data.get("created_at"):
            listing.created_at = datetime.fromisoformat(data["created_at"])
        if data.get("expires_at"):
            listing.expires_at = datetime.fromisoformat(data["expires_at"])
        if data.get("sold_at"):
            listing.sold_at = datetime.fromisoformat(data["sold_at"])
        
        listing.buyer_dbref = data.get("buyer_dbref", "")
        listing.buyer_name = data.get("buyer_name", "")
        listing.final_price = data.get("final_price", 0)
        
        return listing


# =============================================================================
# AUCTION
# =============================================================================

@dataclass
class Bid:
    """A bid in an auction."""
    bidder_dbref: str
    bidder_name: str
    amount: int
    timestamp: datetime
    
    def to_dict(self) -> dict:
        return {
            "bidder_dbref": self.bidder_dbref,
            "bidder_name": self.bidder_name,
            "amount": self.amount,
            "timestamp": self.timestamp.isoformat(),
        }
    
    @classmethod
    def from_dict(cls, data: dict) -> "Bid":
        return cls(
            bidder_dbref=data["bidder_dbref"],
            bidder_name=data["bidder_name"],
            amount=data["amount"],
            timestamp=datetime.fromisoformat(data["timestamp"]),
        )


@dataclass
class Auction(MarketListing):
    """An auction listing."""
    # Auction specific
    starting_bid: int = 0
    bid_increment: int = 10
    reserve_price: int = 0      # Minimum to sell
    
    # Bids
    bids: List[Bid] = field(default_factory=list)
    
    # Auction status
    auction_status: AuctionStatus = AuctionStatus.UPCOMING
    
    def __post_init__(self):
        self.listing_type = ListingType.AUCTION
    
    @property
    def current_bid(self) -> int:
        """Get current highest bid."""
        if self.bids:
            return self.bids[-1].amount
        return self.starting_bid
    
    @property
    def current_bidder(self) -> Optional[str]:
        """Get current highest bidder."""
        if self.bids:
            return self.bids[-1].bidder_name
        return None
    
    @property
    def minimum_next_bid(self) -> int:
        """Get minimum amount for next bid."""
        return self.current_bid + self.bid_increment
    
    def place_bid(self, bidder_dbref: str, bidder_name: str, amount: int) -> Tuple[bool, str]:
        """Place a bid."""
        if self.auction_status not in (AuctionStatus.ACTIVE, AuctionStatus.ENDING_SOON):
            return False, "Auction is not active."
        
        if amount < self.minimum_next_bid:
            return False, f"Minimum bid is {format_currency(self.minimum_next_bid, self.currency)}."
        
        # Check if buyout
        if self.buyout_price > 0 and amount >= self.buyout_price:
            return self._buyout(bidder_dbref, bidder_name, amount)
        
        # Place bid
        bid = Bid(
            bidder_dbref=bidder_dbref,
            bidder_name=bidder_name,
            amount=amount,
            timestamp=datetime.now(),
        )
        self.bids.append(bid)
        
        return True, f"Bid of {format_currency(amount, self.currency)} placed!"
    
    def _buyout(self, buyer_dbref: str, buyer_name: str, amount: int) -> Tuple[bool, str]:
        """Execute buyout."""
        self.auction_status = AuctionStatus.ENDED
        self.status = ListingStatus.SOLD
        self.buyer_dbref = buyer_dbref
        self.buyer_name = buyer_name
        self.final_price = self.buyout_price
        self.sold_at = datetime.now()
        
        return True, f"Buyout successful at {format_currency(self.buyout_price, self.currency)}!"
    
    def end_auction(self) -> Tuple[bool, str, Optional[str], int]:
        """
        End the auction.
        Returns (sold, message, winner_dbref, final_price).
        """
        self.auction_status = AuctionStatus.ENDED
        
        if not self.bids:
            self.status = ListingStatus.EXPIRED
            return False, "Auction ended with no bids.", None, 0
        
        final_bid = self.bids[-1]
        
        # Check reserve
        if self.reserve_price > 0 and final_bid.amount < self.reserve_price:
            self.status = ListingStatus.EXPIRED
            return False, f"Reserve price of {format_currency(self.reserve_price, self.currency)} not met.", None, 0
        
        # Sold!
        self.status = ListingStatus.SOLD
        self.buyer_dbref = final_bid.bidder_dbref
        self.buyer_name = final_bid.bidder_name
        self.final_price = final_bid.amount
        self.sold_at = datetime.now()
        
        return True, f"Sold to {final_bid.bidder_name} for {format_currency(final_bid.amount, self.currency)}!", final_bid.bidder_dbref, final_bid.amount
    
    def get_auction_summary(self) -> str:
        """Get detailed auction summary."""
        lines = [
            f"=== Auction: {self.property_name} ===",
            f"Status: {self.auction_status.value.upper()}",
            f"Current Bid: {format_currency(self.current_bid, self.currency)}",
        ]
        
        if self.current_bidder:
            lines.append(f"Leading Bidder: {self.current_bidder}")
        
        lines.append(f"Next Minimum: {format_currency(self.minimum_next_bid, self.currency)}")
        
        if self.buyout_price > 0:
            lines.append(f"Buyout Price: {format_currency(self.buyout_price, self.currency)}")
        
        if self.expires_at:
            remaining = self.expires_at - datetime.now()
            if remaining.total_seconds() > 0:
                hours = remaining.seconds // 3600
                minutes = (remaining.seconds % 3600) // 60
                lines.append(f"Time Remaining: {hours}h {minutes}m")
        
        lines.append(f"Total Bids: {len(self.bids)}")
        
        return "\n".join(lines)
    
    def to_dict(self) -> dict:
        data = super().to_dict()
        data.update({
            "starting_bid": self.starting_bid,
            "bid_increment": self.bid_increment,
            "reserve_price": self.reserve_price,
            "bids": [b.to_dict() for b in self.bids],
            "auction_status": self.auction_status.value,
        })
        return data
    
    @classmethod
    def from_dict(cls, data: dict) -> "Auction":
        auction = cls(listing_id=data["listing_id"])
        
        # Load base listing data
        auction.seller_dbref = data.get("seller_dbref", "")
        auction.seller_name = data.get("seller_name", "")
        auction.property_dbref = data.get("property_dbref", "")
        auction.property_name = data.get("property_name", "")
        auction.property_description = data.get("property_description", "")
        auction.status = ListingStatus(data.get("status", "active"))
        auction.asking_price = data.get("asking_price", 0)
        auction.currency = CurrencyType(data.get("currency", "gold"))
        auction.buyout_price = data.get("buyout_price", 0)
        
        if data.get("created_at"):
            auction.created_at = datetime.fromisoformat(data["created_at"])
        if data.get("expires_at"):
            auction.expires_at = datetime.fromisoformat(data["expires_at"])
        if data.get("sold_at"):
            auction.sold_at = datetime.fromisoformat(data["sold_at"])
        
        auction.buyer_dbref = data.get("buyer_dbref", "")
        auction.buyer_name = data.get("buyer_name", "")
        auction.final_price = data.get("final_price", 0)
        
        # Auction specific
        auction.starting_bid = data.get("starting_bid", 0)
        auction.bid_increment = data.get("bid_increment", 10)
        auction.reserve_price = data.get("reserve_price", 0)
        auction.bids = [Bid.from_dict(b) for b in data.get("bids", [])]
        auction.auction_status = AuctionStatus(data.get("auction_status", "upcoming"))
        
        return auction


# =============================================================================
# SLAVE MARKET
# =============================================================================

class SlaveMarket:
    """
    Manages the slave market.
    """
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._listings = {}
            cls._instance._auctions = {}
        return cls._instance
    
    @staticmethod
    def generate_id() -> str:
        """Generate unique listing ID."""
        timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
        rand = random.randint(1000, 9999)
        return f"LST-{timestamp}-{rand}"
    
    def create_listing(
        self,
        seller,
        property_obj,
        price: int,
        currency: CurrencyType = CurrencyType.GOLD,
        description: str = "",
        duration_days: int = 7,
    ) -> Tuple[bool, str, Optional[MarketListing]]:
        """Create a sale listing."""
        # Verify ownership
        if not hasattr(seller, 'owns') or not seller.owns(property_obj):
            return False, f"You don't own {property_obj.key}.", None
        
        listing = MarketListing(
            listing_id=self.generate_id(),
            seller_dbref=seller.dbref,
            seller_name=seller.key,
            property_dbref=property_obj.dbref,
            property_name=property_obj.key,
            property_description=description,
            listing_type=ListingType.SALE,
            asking_price=price,
            currency=currency,
            created_at=datetime.now(),
            expires_at=datetime.now() + timedelta(days=duration_days),
        )
        
        self._listings[listing.listing_id] = listing
        
        return True, f"Listed {property_obj.key} for {format_currency(price, currency)}.", listing
    
    def create_auction(
        self,
        seller,
        property_obj,
        starting_bid: int,
        currency: CurrencyType = CurrencyType.GOLD,
        description: str = "",
        duration_hours: int = 24,
        reserve_price: int = 0,
        buyout_price: int = 0,
        bid_increment: int = 10,
    ) -> Tuple[bool, str, Optional[Auction]]:
        """Create an auction listing."""
        # Verify ownership
        if not hasattr(seller, 'owns') or not seller.owns(property_obj):
            return False, f"You don't own {property_obj.key}.", None
        
        auction = Auction(
            listing_id=self.generate_id(),
            seller_dbref=seller.dbref,
            seller_name=seller.key,
            property_dbref=property_obj.dbref,
            property_name=property_obj.key,
            property_description=description,
            starting_bid=starting_bid,
            asking_price=starting_bid,
            currency=currency,
            reserve_price=reserve_price,
            buyout_price=buyout_price,
            bid_increment=bid_increment,
            created_at=datetime.now(),
            expires_at=datetime.now() + timedelta(hours=duration_hours),
            auction_status=AuctionStatus.ACTIVE,
        )
        
        self._auctions[auction.listing_id] = auction
        
        return True, f"Auction created for {property_obj.key}!", auction
    
    def get_listing(self, listing_id: str) -> Optional[MarketListing]:
        """Get a listing by ID."""
        return self._listings.get(listing_id)
    
    def get_auction(self, listing_id: str) -> Optional[Auction]:
        """Get an auction by ID."""
        return self._auctions.get(listing_id)
    
    def get_active_listings(self) -> List[MarketListing]:
        """Get all active sale listings."""
        return [l for l in self._listings.values() 
                if l.status == ListingStatus.ACTIVE and not l.is_expired()]
    
    def get_active_auctions(self) -> List[Auction]:
        """Get all active auctions."""
        return [a for a in self._auctions.values()
                if a.auction_status in (AuctionStatus.ACTIVE, AuctionStatus.ENDING_SOON)]
    
    def purchase_listing(
        self,
        buyer,
        listing_id: str,
    ) -> Tuple[bool, str]:
        """Purchase from a listing."""
        listing = self.get_listing(listing_id)
        if not listing:
            return False, "Listing not found."
        
        if not hasattr(buyer, 'wallet'):
            return False, "You don't have a wallet."
        
        buyer_wallet = buyer.wallet
        
        can_buy, reason = listing.can_purchase(buyer_wallet)
        if not can_buy:
            return False, reason
        
        # Process payment
        success, msg, txn = EconomyManager.pay_npc(
            buyer_wallet,
            listing.asking_price,
            listing.currency,
            f"Slave Market ({listing.seller_name})",
            description=f"Purchased {listing.property_name}",
            item_name=listing.property_name,
        )
        
        if not success:
            return False, msg
        
        buyer.save_wallet(buyer_wallet)
        
        # Update listing
        listing.status = ListingStatus.SOLD
        listing.buyer_dbref = buyer.dbref
        listing.buyer_name = buyer.key
        listing.final_price = listing.asking_price
        listing.sold_at = datetime.now()
        
        # Transfer ownership would happen here
        # OwnershipSystem.transfer_ownership(...)
        
        return True, f"Purchased {listing.property_name} for {format_currency(listing.asking_price, listing.currency)}!"
    
    def place_bid(
        self,
        bidder,
        auction_id: str,
        amount: int,
    ) -> Tuple[bool, str]:
        """Place a bid on an auction."""
        auction = self.get_auction(auction_id)
        if not auction:
            return False, "Auction not found."
        
        return auction.place_bid(bidder.dbref, bidder.key, amount)
    
    def cancel_listing(self, listing_id: str, requester_dbref: str) -> Tuple[bool, str]:
        """Cancel a listing."""
        listing = self._listings.get(listing_id) or self._auctions.get(listing_id)
        
        if not listing:
            return False, "Listing not found."
        
        if listing.seller_dbref != requester_dbref:
            return False, "Only the seller can cancel this listing."
        
        if listing.status == ListingStatus.SOLD:
            return False, "Cannot cancel a completed sale."
        
        listing.status = ListingStatus.CANCELLED
        
        if isinstance(listing, Auction):
            listing.auction_status = AuctionStatus.CANCELLED
        
        return True, "Listing cancelled."
    
    def process_expired(self) -> List[str]:
        """Process expired listings and auctions. Returns messages."""
        messages = []
        
        # Process listings
        for listing in self._listings.values():
            if listing.status == ListingStatus.ACTIVE and listing.is_expired():
                listing.status = ListingStatus.EXPIRED
                messages.append(f"Listing for {listing.property_name} has expired.")
        
        # Process auctions
        for auction in self._auctions.values():
            if auction.auction_status == AuctionStatus.ACTIVE:
                if auction.is_expired():
                    sold, msg, winner, price = auction.end_auction()
                    messages.append(msg)
                elif auction.expires_at:
                    remaining = auction.expires_at - datetime.now()
                    if remaining.total_seconds() <= 3600:
                        auction.auction_status = AuctionStatus.ENDING_SOON
        
        return messages


__all__ = [
    "ListingType",
    "ListingStatus",
    "AuctionStatus",
    "Appraisal",
    "appraise_character",
    "MarketListing",
    "Bid",
    "Auction",
    "SlaveMarket",
]
