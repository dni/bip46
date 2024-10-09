from base64 import b64decode
from datetime import datetime, timezone
from hashlib import sha256

import bech32

# from coincurve import PublicKey, PrivateKey as CoincurvePrivateKey
from embit.bip32 import HDKey
from embit.bip39 import mnemonic_to_seed
from embit.ec import PrivateKey as EmbitPrivateKey

# from embit.ec import PrivateKey
from embit.networks import NETWORKS
from secp256k1 import PrivateKey, PublicKey

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


class Bip46RecoveredPubkeyError(Exception):
    """Raised when we could not recover the pubkey from signature and message"""


def create_certificate_message(
    pubkey: str,
    message: str = "fidelity-bond-cert",
    expiry: int = 375
) -> str:
    """Create a certificate message for a BIP46 timelock"""
    return f"{message}|{pubkey}|{expiry}"


def prepare_certificate_message(message: str) -> bytes:
    msg = message.encode()
    prefix = b"\x18Bitcoin Signed Message:\n"
    data = prefix + bytes([len(msg)]) + msg
    return sha256(sha256(data).digest()).digest()


def sign_certificate_message(private_key: bytes, message: str) -> bytes:
    """Sign a certificate message for a BIP46 timelock"""
    message_hash = prepare_certificate_message(message)
    key = PrivateKey(private_key)
    raw_sig = key.ecdsa_sign_recoverable(message_hash, raw=True)
    sig, recid = key.ecdsa_recoverable_serialize(raw_sig)
    # 31 for p2pkh_address
    return bytes([recid + 31]) + sig


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


def hdkey_from_seed(seed: bytes, network: str = "main") -> HDKey:
    """Create a HDKey from a seed"""
    version = NETWORKS[network]["xprv"]
    master = HDKey.from_seed(seed, version=version)
    return master


def hdkey_from_mnemonic(mnemonic: str, network: str = "main") -> HDKey:
    """Create a HDKey from a mnemonic"""
    seed = mnemonic_to_seed(mnemonic)
    return hdkey_from_seed(seed, network)


def hdkey_from_wif(wif: str, network: str = "main") -> HDKey:
    """Create a HDKey from a WIF"""
    privkey = EmbitPrivateKey.from_wif(wif)
    assert wif, privkey.wif()
    return hdkey_from_seed(privkey.secret, network)


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


def convert_recoverable_message_signature(sig_base64: str) -> tuple[bytes, int, bool]:
    """ Convert a recoverable signature to a normal signature """
    sig = b64decode(sig_base64)
    if len(sig) != 65:
        raise Bip46RecoveredPubkeyError("Invalid signature length")
    header = int(sig[0])
    if header < 27 or header > 42:
        raise Bip46RecoveredPubkeyError(f"Header out of range: {header}")
    r = sig[1:33]
    s = sig[33:]
    compressed = False
    if(header >= 39): # this is a bech32 signature
        header -= 12
        compressed = True
    # this is a segwit p2sh signature
    elif header >= 35:
        header -= 8
        compressed = True
    # this is a compressed key signature
    elif header >= 31:
        compressed = True
        header -= 4
    rec_id = header - 27
    return r + s, rec_id, compressed


def recover_from_signature_and_message(sig_base64: str, message: str) -> bytes:
    """Recover a pubkey from signature and message"""
    message_hash = prepare_certificate_message(message)
    sig, recid, _ = convert_recoverable_message_signature(sig_base64)
    empty = PublicKey()
    sig = empty.ecdsa_recoverable_deserialize(sig, recid)
    pubkey = empty.ecdsa_recover(message_hash, sig, raw=True)
    return PublicKey(pubkey).serialize()
