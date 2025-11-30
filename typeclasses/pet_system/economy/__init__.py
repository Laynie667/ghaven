"""
Economy Package
===============

Economy, shops, ownership, and market systems:
- Currency and transactions
- Shops and vendors
- Ownership relationships
- Slave market and auctions
"""

from .economy import (
    CurrencyType,
    TransactionType,
    EXCHANGE_RATES,
    convert_currency,
    format_currency,
    auto_format_value,
    Transaction,
    Wallet,
    EconomyManager,
    WalletMixin,
)

from .shops import (
    ShopType,
    ShopStatus,
    ShopItem,
    Shop,
    SHOP_PRESETS,
    create_shop_from_preset,
    create_pet_shop,
    create_tack_shop,
    create_clothier,
    create_apothecary,
    ShopManager,
)

from .ownership import (
    OwnershipType,
    OwnerPermission,
    CollarType,
    OwnershipCollar,
    OwnershipRecord,
    OwnershipSystem,
    OwnerMixin,
    PropertyMixin,
)

from .slave_market import (
    ListingType,
    ListingStatus,
    AuctionStatus,
    Appraisal,
    appraise_character,
    MarketListing,
    Bid,
    Auction,
    SlaveMarket,
)


__all__ = [
    # Economy
    "CurrencyType",
    "TransactionType",
    "EXCHANGE_RATES",
    "convert_currency",
    "format_currency",
    "auto_format_value",
    "Transaction",
    "Wallet",
    "EconomyManager",
    "WalletMixin",
    
    # Shops
    "ShopType",
    "ShopStatus",
    "ShopItem",
    "Shop",
    "SHOP_PRESETS",
    "create_shop_from_preset",
    "create_pet_shop",
    "create_tack_shop",
    "create_clothier",
    "create_apothecary",
    "ShopManager",
    
    # Ownership
    "OwnershipType",
    "OwnerPermission",
    "CollarType",
    "OwnershipCollar",
    "OwnershipRecord",
    "OwnershipSystem",
    "OwnerMixin",
    "PropertyMixin",
    
    # Slave Market
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
