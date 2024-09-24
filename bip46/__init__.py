from datetime import datetime, timezone
from hashlib import sha256

import bech32
from embit.bip32 import HDKey
from embit.bip39 import mnemonic_to_seed
from embit.networks import NETWORKS

DERIVATION_PATH = "m/84'/0'/0'/2"
DERIVATION_PATH_TESTNET = "m/84'/1'/0'/2"


class Bip46TimeError(Exception):
    """Raised when a locktime is not in the valid range for BIP46 timelocks"""


class Bip46IndexError(Exception):
    """Raised when a locktime index is not in the valid range for BIP46 timelocks"""


class Bip46PathError(Exception):
    """Raised when the derivation path is invalid"""


class Bip46Bech32Error(Exception):
    """Raised when the bech32 encoding fails"""


def create_redeemscript(lock_date: datetime, pubkey: bytes) -> bytes:
    """Create a redeemscript pubkey for a BIP46 timelock"""
    locktime_bytes = lockdate_to_little_endian(lock_date)
    return (
        bytes([len(locktime_bytes)])  # 1 byte len of locktime
        + locktime_bytes  # 4 or 5 bytes of locktime
        + bytes([177, 117]) # OP_CLTV OP_DROP
        + bytes([len(pubkey)]) # 1 byte len of pubkey
        + pubkey # pubkey
        + bytes([172]) # OP_CHECKSIG
    )


def redeemscript_pubkey(redeemscript: bytes) -> bytes:
    """Create a redeemscript pubkey for a BIP46 timelock"""
    encoded = sha256(redeemscript).digest()
    return bytes([0, len(encoded)]) + encoded


def redeemscript_address(script_pubkey: bytes, network: str = "main") -> str:
    """Create a p2wpkh_address redeemscript address for a BIP46 timelock"""
    hrp = NETWORKS[network]["bech32"]
    address = bech32.encode(hrp, 0, script_pubkey[2:])
    if not address:
        raise Bip46Bech32Error("Could not encode address")
    return address


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


def lockdate_to_derivation_path(lock_date: datetime, network: str = "main") -> str:
    """Derive the path for a BIP46 timelock"""
    i = lockdate_to_index(lock_date)
    path = DERIVATION_PATH if network == "main" else DERIVATION_PATH_TESTNET
    return f"{path}/{i}"


def lockdate_to_little_endian(locktime: datetime) -> bytes:
    """Convert a lockdate to little-endian bytes for use in a script"""
    # max signed int for 4bytes
    max_int = 2**31 - 1
    ts = int(locktime.timestamp())
    size = 4 if ts <= max_int else 5
    return ts.to_bytes(size, "little")


def hdkey_from_mnemonic(mnemonic: str, network: str = "main") -> HDKey:
    """Create a HDKey from a mnemonic"""
    seed = mnemonic_to_seed(mnemonic)
    version = NETWORKS[network]["xprv"]
    master = HDKey.from_seed(seed, version=version)
    return master


def hdkey_derive(hdkey: HDKey, path: str) -> HDKey:
    """
    Derive a child key from a hdkey
    Path should be in the form of m/x/y/z where x' means hardened
    first child path for mainnet is m/84'/0'/0'/2/0
    """
    if not path.startswith("m"):
        raise Bip46PathError(f"Invalid Path, should start with `m`: {path}")
    if not path.endswith(f"/2/{path.split('/')[-1]}"):
        raise Bip46PathError(f"Invalid Path, should end with `/2/x`: {path}")
    return hdkey.derive(path)


def hdkey_to_wif(hdkey: HDKey) -> str:
    """Get the WIF from an HDKey"""
    return str(hdkey.key)


def hdkey_to_pubkey(hdkey: HDKey) -> bytes:
    """Get the pubkey from an HDKey"""
    return hdkey.get_public_key().sec()
