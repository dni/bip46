from datetime import datetime
from hashlib import sha256

import bech32

from .consts import DEFAULT_NETWORK, NETWORKS
from .exceptions import Bip46Bech32Error


def lockdate_to_little_endian(locktime: datetime) -> bytes:
    """Convert a lockdate to little-endian bytes for use in a script"""
    # max signed int for 4bytes
    max_int = 2**31 - 1
    ts = int(locktime.timestamp())
    size = 4 if ts <= max_int else 5
    return ts.to_bytes(size, "little")


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
    hashed = sha256(redeemscript).digest()
    return bytes([0, len(hashed)]) + hashed


def redeemscript_address(script_pubkey: bytes, network: str = DEFAULT_NETWORK) -> str:
    """Create a p2wpkh_address redeemscript address for a BIP46 timelock"""
    hrp = NETWORKS[network]["bech32"]
    address = bech32.encode(str(hrp), 0, script_pubkey[2:])
    if not address:
        raise Bip46Bech32Error("Could not encode address")
    return address
