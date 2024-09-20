from datetime import datetime, timezone

DERIVATION_PATH = "m/84'/0'/0'/2"
DERIVATION_PATH_TESTNET = "m/84'/1'/0'/2"

class Bip46TimeError(Exception):
    """Raised when a locktime is not in the valid range for BIP46 timelocks"""


class Bip46IndexError(Exception):
    """Raised when a locktime index is not in the valid range for BIP46 timelocks"""


def index_to_lockdate(index: int) -> datetime:
    """Convert a BIP46 timelock index to a datetime"""
    if index < 0 or index > 959:
        raise Bip46IndexError("index must be between 0 and 959")
    year = 2020 + index // 12
    month = 1 + index % 12
    day = 1
    return datetime(year, month, day, tzinfo=timezone.utc)


def lockdate_to_index(lock_date: datetime) -> int:
    """Convert a datetime to a BIP46 timelock index"""
    if lock_date.year < 2020:
        raise Bip46TimeError("lock_date must be after 2020")
    if lock_date.year > 2099:
        raise Bip46TimeError("lock_date must be before 2100")
    return (lock_date.year - 2020) * 12 + lock_date.month - 1


def lockdate_to_derivation_path(lock_date: datetime, network: str = "mainnet") -> str:
    """Derive the path for a BIP46 timelock"""
    i = lockdate_to_index(lock_date)
    path = DERIVATION_PATH if network == "mainnet" else DERIVATION_PATH_TESTNET
    return f"{path}/{i}"


def lockdate_to_little_endian(locktime: datetime) -> bytes:
    """Convert a lockdate to little-endian bytes for use in a script"""
    # max signed int for 4bytes
    max_int = 2 ** 31 - 1
    ts = int(locktime.timestamp())
    size = 4 if ts <= max_int else 5
    return ts.to_bytes(size, "little")
