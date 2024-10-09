""" Custom exceptions for the bip46 module """


class Bip46TimeError(Exception):
    """Raised when a locktime is not in the valid range for BIP46 timelocks"""


class Bip46IndexError(Exception):
    """Raised when a locktime index is not in the valid range for BIP46 timelocks"""


class Bip46PathError(Exception):
    """Raised when the derivation path is invalid"""


class Bip46Bech32Error(Exception):
    """Raised when the bech32 encoding fails"""


class Bip46RecoverPubkeyError(Exception):
    """Raised when we could not recover the pubkey from signature and message"""
