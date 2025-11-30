"""
Economy System
==============

Currency and transaction management:
- Multiple currency types
- Wallet management
- Transactions and history
- Exchange rates
"""

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any, Tuple
from enum import Enum
from datetime import datetime
import random


# =============================================================================
# ENUMS
# =============================================================================

class CurrencyType(Enum):
    """Types of currency."""
    GOLD = "gold"              # Standard currency
    SILVER = "silver"          # Common currency
    COPPER = "copper"          # Small currency
    MARKS = "marks"            # Trade marks
    TOKENS = "tokens"          # Special tokens (brothel, etc.)
    REPUTATION = "reputation"  # Non-tradeable, earned


class TransactionType(Enum):
    """Types of transactions."""
    PURCHASE = "purchase"
    SALE = "sale"
    GIFT = "gift"
    THEFT = "theft"
    REWARD = "reward"
    FINE = "fine"
    TRADE = "trade"
    AUCTION_WIN = "auction_win"
    AUCTION_SELL = "auction_sell"
    SERVICE = "service"
    CONTRACT = "contract"


# =============================================================================
# EXCHANGE RATES
# =============================================================================

# Base exchange rates (all relative to copper)
EXCHANGE_RATES = {
    CurrencyType.COPPER: 1,
    CurrencyType.SILVER: 100,      # 1 silver = 100 copper
    CurrencyType.GOLD: 10000,      # 1 gold = 100 silver = 10000 copper
    CurrencyType.MARKS: 5000,      # Trade marks
    CurrencyType.TOKENS: 50,       # Special tokens
    CurrencyType.REPUTATION: 0,    # Cannot be exchanged
}


def convert_currency(amount: int, from_type: CurrencyType, to_type: CurrencyType) -> int:
    """Convert between currency types."""
    if from_type == CurrencyType.REPUTATION or to_type == CurrencyType.REPUTATION:
        return 0  # Can't convert reputation
    
    # Convert to copper first, then to target
    copper_value = amount * EXCHANGE_RATES[from_type]
    return copper_value // EXCHANGE_RATES[to_type]


def format_currency(amount: int, currency_type: CurrencyType) -> str:
    """Format currency amount nicely."""
    symbols = {
        CurrencyType.GOLD: "gp",
        CurrencyType.SILVER: "sp",
        CurrencyType.COPPER: "cp",
        CurrencyType.MARKS: "marks",
        CurrencyType.TOKENS: "tokens",
        CurrencyType.REPUTATION: "rep",
    }
    return f"{amount:,} {symbols.get(currency_type, currency_type.value)}"


def auto_format_value(copper_value: int) -> str:
    """Auto-format a copper value into mixed currency."""
    if copper_value <= 0:
        return "0 cp"
    
    parts = []
    remaining = copper_value
    
    # Gold
    gold = remaining // EXCHANGE_RATES[CurrencyType.GOLD]
    if gold > 0:
        parts.append(f"{gold:,} gp")
        remaining -= gold * EXCHANGE_RATES[CurrencyType.GOLD]
    
    # Silver
    silver = remaining // EXCHANGE_RATES[CurrencyType.SILVER]
    if silver > 0:
        parts.append(f"{silver} sp")
        remaining -= silver * EXCHANGE_RATES[CurrencyType.SILVER]
    
    # Copper
    if remaining > 0 or not parts:
        parts.append(f"{remaining} cp")
    
    return ", ".join(parts)


# =============================================================================
# TRANSACTION
# =============================================================================

@dataclass
class Transaction:
    """Record of a financial transaction."""
    transaction_id: str
    timestamp: datetime
    
    # Parties
    from_dbref: str = ""
    from_name: str = ""
    to_dbref: str = ""
    to_name: str = ""
    
    # Amount
    amount: int = 0
    currency: CurrencyType = CurrencyType.GOLD
    
    # Type and description
    transaction_type: TransactionType = TransactionType.PURCHASE
    description: str = ""
    
    # Item reference if applicable
    item_dbref: str = ""
    item_name: str = ""
    
    def to_dict(self) -> dict:
        return {
            "transaction_id": self.transaction_id,
            "timestamp": self.timestamp.isoformat(),
            "from_dbref": self.from_dbref,
            "from_name": self.from_name,
            "to_dbref": self.to_dbref,
            "to_name": self.to_name,
            "amount": self.amount,
            "currency": self.currency.value,
            "transaction_type": self.transaction_type.value,
            "description": self.description,
            "item_dbref": self.item_dbref,
            "item_name": self.item_name,
        }
    
    @classmethod
    def from_dict(cls, data: dict) -> "Transaction":
        return cls(
            transaction_id=data["transaction_id"],
            timestamp=datetime.fromisoformat(data["timestamp"]),
            from_dbref=data.get("from_dbref", ""),
            from_name=data.get("from_name", ""),
            to_dbref=data.get("to_dbref", ""),
            to_name=data.get("to_name", ""),
            amount=data.get("amount", 0),
            currency=CurrencyType(data.get("currency", "gold")),
            transaction_type=TransactionType(data.get("transaction_type", "purchase")),
            description=data.get("description", ""),
            item_dbref=data.get("item_dbref", ""),
            item_name=data.get("item_name", ""),
        )
    
    def get_summary(self) -> str:
        """Get one-line summary."""
        if self.transaction_type == TransactionType.PURCHASE:
            return f"Bought {self.item_name or 'item'} for {format_currency(self.amount, self.currency)}"
        elif self.transaction_type == TransactionType.SALE:
            return f"Sold {self.item_name or 'item'} for {format_currency(self.amount, self.currency)}"
        elif self.transaction_type == TransactionType.GIFT:
            return f"Gift of {format_currency(self.amount, self.currency)} to {self.to_name}"
        elif self.transaction_type == TransactionType.REWARD:
            return f"Reward: {format_currency(self.amount, self.currency)}"
        else:
            return f"{self.transaction_type.value}: {format_currency(self.amount, self.currency)}"


# =============================================================================
# WALLET
# =============================================================================

@dataclass
class Wallet:
    """A character's currency wallet."""
    owner_dbref: str = ""
    owner_name: str = ""
    
    # Balances by currency type
    balances: Dict[str, int] = field(default_factory=dict)
    
    # Transaction history (last N transactions)
    history: List[dict] = field(default_factory=list)
    max_history: int = 100
    
    def get_balance(self, currency: CurrencyType) -> int:
        """Get balance of a currency type."""
        return self.balances.get(currency.value, 0)
    
    def set_balance(self, currency: CurrencyType, amount: int) -> None:
        """Set balance of a currency type."""
        self.balances[currency.value] = max(0, amount)
    
    def add(self, currency: CurrencyType, amount: int) -> int:
        """Add currency. Returns new balance."""
        current = self.get_balance(currency)
        new_balance = max(0, current + amount)
        self.set_balance(currency, new_balance)
        return new_balance
    
    def subtract(self, currency: CurrencyType, amount: int) -> Tuple[bool, int]:
        """
        Subtract currency if possible.
        Returns (success, new_balance).
        """
        current = self.get_balance(currency)
        if current < amount:
            return False, current
        
        new_balance = current - amount
        self.set_balance(currency, new_balance)
        return True, new_balance
    
    def can_afford(self, currency: CurrencyType, amount: int) -> bool:
        """Check if wallet can afford an amount."""
        return self.get_balance(currency) >= amount
    
    def get_total_value(self) -> int:
        """Get total value in copper."""
        total = 0
        for currency_str, amount in self.balances.items():
            try:
                currency = CurrencyType(currency_str)
                if currency != CurrencyType.REPUTATION:
                    total += amount * EXCHANGE_RATES[currency]
            except ValueError:
                pass
        return total
    
    def add_transaction(self, transaction: Transaction) -> None:
        """Add transaction to history."""
        self.history.insert(0, transaction.to_dict())
        
        # Trim history
        if len(self.history) > self.max_history:
            self.history = self.history[:self.max_history]
    
    def get_history(self, count: int = 10) -> List[Transaction]:
        """Get recent transactions."""
        return [Transaction.from_dict(t) for t in self.history[:count]]
    
    def get_balance_display(self) -> str:
        """Get formatted display of all balances."""
        lines = []
        for currency in CurrencyType:
            balance = self.get_balance(currency)
            if balance > 0:
                lines.append(format_currency(balance, currency))
        
        if not lines:
            return "Empty wallet"
        
        return " | ".join(lines)
    
    def to_dict(self) -> dict:
        return {
            "owner_dbref": self.owner_dbref,
            "owner_name": self.owner_name,
            "balances": self.balances,
            "history": self.history,
            "max_history": self.max_history,
        }
    
    @classmethod
    def from_dict(cls, data: dict) -> "Wallet":
        wallet = cls()
        wallet.owner_dbref = data.get("owner_dbref", "")
        wallet.owner_name = data.get("owner_name", "")
        wallet.balances = data.get("balances", {})
        wallet.history = data.get("history", [])
        wallet.max_history = data.get("max_history", 100)
        return wallet


# =============================================================================
# ECONOMY MANAGER
# =============================================================================

class EconomyManager:
    """
    Manages global economy operations.
    """
    
    @staticmethod
    def generate_transaction_id() -> str:
        """Generate unique transaction ID."""
        timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
        rand = random.randint(1000, 9999)
        return f"TXN-{timestamp}-{rand}"
    
    @staticmethod
    def transfer(
        from_wallet: Wallet,
        to_wallet: Wallet,
        amount: int,
        currency: CurrencyType,
        transaction_type: TransactionType = TransactionType.GIFT,
        description: str = "",
        item_name: str = "",
    ) -> Tuple[bool, str, Optional[Transaction]]:
        """
        Transfer currency between wallets.
        Returns (success, message, transaction).
        """
        # Check if sender can afford
        if not from_wallet.can_afford(currency, amount):
            return False, f"Cannot afford {format_currency(amount, currency)}", None
        
        # Perform transfer
        from_wallet.subtract(currency, amount)
        to_wallet.add(currency, amount)
        
        # Create transaction record
        txn = Transaction(
            transaction_id=EconomyManager.generate_transaction_id(),
            timestamp=datetime.now(),
            from_dbref=from_wallet.owner_dbref,
            from_name=from_wallet.owner_name,
            to_dbref=to_wallet.owner_dbref,
            to_name=to_wallet.owner_name,
            amount=amount,
            currency=currency,
            transaction_type=transaction_type,
            description=description,
            item_name=item_name,
        )
        
        # Record in both wallets
        from_wallet.add_transaction(txn)
        to_wallet.add_transaction(txn)
        
        return True, f"Transferred {format_currency(amount, currency)} to {to_wallet.owner_name}", txn
    
    @staticmethod
    def pay_npc(
        wallet: Wallet,
        amount: int,
        currency: CurrencyType,
        npc_name: str,
        transaction_type: TransactionType = TransactionType.PURCHASE,
        description: str = "",
        item_name: str = "",
    ) -> Tuple[bool, str, Optional[Transaction]]:
        """
        Pay money to an NPC (money disappears).
        """
        if not wallet.can_afford(currency, amount):
            return False, f"Cannot afford {format_currency(amount, currency)}", None
        
        wallet.subtract(currency, amount)
        
        txn = Transaction(
            transaction_id=EconomyManager.generate_transaction_id(),
            timestamp=datetime.now(),
            from_dbref=wallet.owner_dbref,
            from_name=wallet.owner_name,
            to_dbref="",
            to_name=npc_name,
            amount=amount,
            currency=currency,
            transaction_type=transaction_type,
            description=description,
            item_name=item_name,
        )
        
        wallet.add_transaction(txn)
        
        return True, f"Paid {format_currency(amount, currency)} to {npc_name}", txn
    
    @staticmethod
    def receive_from_npc(
        wallet: Wallet,
        amount: int,
        currency: CurrencyType,
        npc_name: str,
        transaction_type: TransactionType = TransactionType.SALE,
        description: str = "",
        item_name: str = "",
    ) -> Tuple[bool, str, Optional[Transaction]]:
        """
        Receive money from an NPC (money created).
        """
        wallet.add(currency, amount)
        
        txn = Transaction(
            transaction_id=EconomyManager.generate_transaction_id(),
            timestamp=datetime.now(),
            from_dbref="",
            from_name=npc_name,
            to_dbref=wallet.owner_dbref,
            to_name=wallet.owner_name,
            amount=amount,
            currency=currency,
            transaction_type=transaction_type,
            description=description,
            item_name=item_name,
        )
        
        wallet.add_transaction(txn)
        
        return True, f"Received {format_currency(amount, currency)} from {npc_name}", txn
    
    @staticmethod
    def grant_reward(
        wallet: Wallet,
        amount: int,
        currency: CurrencyType,
        reason: str = "",
    ) -> Transaction:
        """Grant a reward (money created from nothing)."""
        wallet.add(currency, amount)
        
        txn = Transaction(
            transaction_id=EconomyManager.generate_transaction_id(),
            timestamp=datetime.now(),
            from_dbref="",
            from_name="System",
            to_dbref=wallet.owner_dbref,
            to_name=wallet.owner_name,
            amount=amount,
            currency=currency,
            transaction_type=TransactionType.REWARD,
            description=reason,
        )
        
        wallet.add_transaction(txn)
        return txn
    
    @staticmethod
    def apply_fine(
        wallet: Wallet,
        amount: int,
        currency: CurrencyType,
        reason: str = "",
    ) -> Tuple[bool, Transaction]:
        """
        Apply a fine (money destroyed).
        Returns (full_payment, transaction).
        """
        current = wallet.get_balance(currency)
        actual_amount = min(current, amount)
        full_payment = current >= amount
        
        wallet.subtract(currency, actual_amount)
        
        txn = Transaction(
            transaction_id=EconomyManager.generate_transaction_id(),
            timestamp=datetime.now(),
            from_dbref=wallet.owner_dbref,
            from_name=wallet.owner_name,
            to_dbref="",
            to_name="System",
            amount=actual_amount,
            currency=currency,
            transaction_type=TransactionType.FINE,
            description=reason,
        )
        
        wallet.add_transaction(txn)
        return full_payment, txn


# =============================================================================
# WALLET MIXIN
# =============================================================================

class WalletMixin:
    """
    Mixin for characters with wallets.
    """
    
    @property
    def wallet(self) -> Wallet:
        """Get character's wallet."""
        data = self.attributes.get("wallet")
        if data:
            wallet = Wallet.from_dict(data)
        else:
            wallet = Wallet(
                owner_dbref=self.dbref,
                owner_name=self.key,
            )
        return wallet
    
    @wallet.setter
    def wallet(self, wallet: Wallet):
        """Set wallet."""
        self.attributes.add("wallet", wallet.to_dict())
    
    def save_wallet(self, wallet: Wallet):
        """Save wallet changes."""
        self.wallet = wallet
    
    def get_balance(self, currency: CurrencyType = CurrencyType.GOLD) -> int:
        """Get balance of a currency."""
        return self.wallet.get_balance(currency)
    
    def can_afford(self, amount: int, currency: CurrencyType = CurrencyType.GOLD) -> bool:
        """Check if can afford amount."""
        return self.wallet.can_afford(currency, amount)
    
    def add_money(self, amount: int, currency: CurrencyType = CurrencyType.GOLD) -> int:
        """Add money. Returns new balance."""
        wallet = self.wallet
        new_balance = wallet.add(currency, amount)
        self.save_wallet(wallet)
        return new_balance
    
    def remove_money(self, amount: int, currency: CurrencyType = CurrencyType.GOLD) -> Tuple[bool, int]:
        """Remove money if possible. Returns (success, new_balance)."""
        wallet = self.wallet
        success, new_balance = wallet.subtract(currency, amount)
        if success:
            self.save_wallet(wallet)
        return success, new_balance
    
    def pay(self, target, amount: int, currency: CurrencyType = CurrencyType.GOLD,
            description: str = "") -> Tuple[bool, str]:
        """Pay another character."""
        if not hasattr(target, 'wallet'):
            return False, f"{target.key} cannot receive money."
        
        my_wallet = self.wallet
        their_wallet = target.wallet
        
        success, message, txn = EconomyManager.transfer(
            my_wallet, their_wallet, amount, currency,
            TransactionType.GIFT, description
        )
        
        if success:
            self.save_wallet(my_wallet)
            target.save_wallet(their_wallet)
        
        return success, message
    
    def get_wealth_display(self) -> str:
        """Get formatted wealth display."""
        return self.wallet.get_balance_display()


__all__ = [
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
]
