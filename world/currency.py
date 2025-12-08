"""
Currency System for Gilderhaven
================================

Simple currency management that operates on any object with .db storage.
Does NOT require Character.py modifications - currency is just an attribute.

Usage:
    from world.currency import pay, receive, balance, transfer, can_afford
    
    # Check balance
    gold = balance(character)
    
    # Give money
    receive(character, 100, reason="quest reward")
    
    # Take money (returns True/False)
    if pay(character, 50, reason="shop purchase"):
        # purchase succeeded
    
    # Transfer between characters
    transfer(sender, receiver, 75, reason="trade")
"""

# Currency name - change this to rename your currency globally
CURRENCY_NAME = "gold"
CURRENCY_PLURAL = "gold"
STARTING_CURRENCY = 100


def balance(target):
    """
    Get current currency balance.
    
    Args:
        target: Any object with .db (Character, Account, NPC, etc.)
    
    Returns:
        int: Current balance (0 if not set)
    """
    return target.db.currency or 0


def receive(target, amount, reason=None, silent=False):
    """
    Add currency to target.
    
    Args:
        target: Any object with .db
        amount: int, amount to add (must be positive)
        reason: str, optional reason for logging
        silent: bool, if True don't message the target
    
    Returns:
        int: New balance
    """
    if amount < 0:
        raise ValueError("Cannot receive negative currency. Use pay() instead.")
    
    current = balance(target)
    new_balance = current + amount
    target.db.currency = new_balance
    
    # Log the transaction
    _log_transaction(target, amount, "receive", reason)
    
    # Notify target if they can receive messages
    if not silent and hasattr(target, 'msg'):
        if reason:
            target.msg(f"|gYou receive {amount} {CURRENCY_PLURAL}|n ({reason}).")
        else:
            target.msg(f"|gYou receive {amount} {CURRENCY_PLURAL}|n.")
    
    return new_balance


def pay(target, amount, reason=None, silent=False, force=False):
    """
    Remove currency from target.
    
    Args:
        target: Any object with .db
        amount: int, amount to remove (must be positive)
        reason: str, optional reason for logging
        silent: bool, if True don't message the target
        force: bool, if True allow negative balance (debt)
    
    Returns:
        bool: True if payment succeeded, False if insufficient funds
    """
    if amount < 0:
        raise ValueError("Cannot pay negative currency. Use receive() instead.")
    
    current = balance(target)
    
    if current < amount and not force:
        if not silent and hasattr(target, 'msg'):
            target.msg(f"|rYou don't have enough {CURRENCY_PLURAL}.|n "
                      f"(Need {amount}, have {current})")
        return False
    
    new_balance = current - amount
    target.db.currency = new_balance
    
    # Log the transaction
    _log_transaction(target, -amount, "pay", reason)
    
    if not silent and hasattr(target, 'msg'):
        if reason:
            target.msg(f"|yYou pay {amount} {CURRENCY_PLURAL}|n ({reason}).")
        else:
            target.msg(f"|yYou pay {amount} {CURRENCY_PLURAL}|n.")
    
    return True


def can_afford(target, amount):
    """
    Check if target can afford an amount.
    
    Args:
        target: Any object with .db
        amount: int, amount to check
    
    Returns:
        bool: True if balance >= amount
    """
    return balance(target) >= amount


def transfer(sender, receiver, amount, reason=None, silent=False):
    """
    Transfer currency between two targets.
    
    Args:
        sender: Object paying
        receiver: Object receiving
        amount: int, amount to transfer
        reason: str, optional reason
        silent: bool, suppress messages
    
    Returns:
        bool: True if transfer succeeded
    """
    if not can_afford(sender, amount):
        if not silent and hasattr(sender, 'msg'):
            sender.msg(f"|rYou don't have enough {CURRENCY_PLURAL} to transfer.|n")
        return False
    
    # Perform atomic-ish transfer
    sender.db.currency = balance(sender) - amount
    receiver.db.currency = balance(receiver) + amount
    
    _log_transaction(sender, -amount, "transfer_out", reason)
    _log_transaction(receiver, amount, "transfer_in", reason)
    
    if not silent:
        if hasattr(sender, 'msg'):
            receiver_name = getattr(receiver, 'key', 'someone')
            sender.msg(f"|yYou transfer {amount} {CURRENCY_PLURAL} to {receiver_name}|n.")
        if hasattr(receiver, 'msg'):
            sender_name = getattr(sender, 'key', 'someone')
            receiver.msg(f"|g{sender_name} transfers {amount} {CURRENCY_PLURAL} to you|n.")
    
    return True


def set_balance(target, amount, reason=None):
    """
    Set currency to exact amount (admin function).
    
    Args:
        target: Any object with .db
        amount: int, new balance
        reason: str, optional reason
    
    Returns:
        int: New balance
    """
    old_balance = balance(target)
    target.db.currency = amount
    _log_transaction(target, amount - old_balance, "set", reason)
    return amount


def initialize_currency(target, amount=None):
    """
    Initialize currency for a new character/account.
    Called when character is created.
    
    Args:
        target: Object to initialize
        amount: Starting amount (uses STARTING_CURRENCY if None)
    
    Returns:
        int: Starting balance
    """
    if amount is None:
        amount = STARTING_CURRENCY
    
    if target.db.currency is None:
        target.db.currency = amount
        _log_transaction(target, amount, "initialize", "new character")
    
    return target.db.currency


def _log_transaction(target, amount, transaction_type, reason=None):
    """
    Log a currency transaction for history/debugging.
    
    Stores last 50 transactions on the target.
    """
    import time
    
    if target.db.currency_log is None:
        target.db.currency_log = []
    
    log = target.db.currency_log
    log.append({
        "amount": amount,
        "type": transaction_type,
        "reason": reason,
        "timestamp": time.time(),
        "balance_after": balance(target)
    })
    
    # Keep only last 50 entries
    if len(log) > 50:
        target.db.currency_log = log[-50:]


def get_transaction_log(target, count=10):
    """
    Get recent transaction history.
    
    Args:
        target: Object to check
        count: Number of recent transactions
    
    Returns:
        list: Recent transactions (newest first)
    """
    log = target.db.currency_log or []
    return list(reversed(log[-count:]))


# =============================================================================
# Display Helpers
# =============================================================================

def format_balance(target):
    """Get formatted balance string."""
    amt = balance(target)
    return f"{amt} {CURRENCY_PLURAL if amt != 1 else CURRENCY_NAME}"


def format_price(amount):
    """Get formatted price string."""
    return f"{amount} {CURRENCY_PLURAL if amount != 1 else CURRENCY_NAME}"
