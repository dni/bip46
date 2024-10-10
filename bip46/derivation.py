from datetime import datetime, timezone

from .consts import DEFAULT_NETWORK, DERIVATION_PATH, DERIVATION_PATH_TESTNET
from .exceptions import Bip46IndexError, Bip46TimeError


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


def lockdate_to_derivation_path(
    lock_date: datetime, network: str = DEFAULT_NETWORK
) -> str:
    """Derive the path for a BIP46 timelock from a date"""
    i = lockdate_to_index(lock_date)
    return lockindex_to_derivation_path(i, network)


def lockindex_to_derivation_path(index: int, network: str = DEFAULT_NETWORK) -> str:
    """Derive the path for a BIP46 timelock from an index"""
    path = DERIVATION_PATH if network == "main" else DERIVATION_PATH_TESTNET
    return f"{path}/{index}"
