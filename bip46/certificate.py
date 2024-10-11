from base64 import b64decode
from hashlib import sha256

from secp256k1 import PrivateKey, PublicKey

from .exceptions import Bip46RecoverPubkeyError


def create_certificate_message(
    pubkey: str,
    message: str = "fidelity-bond-cert",
    expiry: int = 375
) -> str:
    """Create a certificate message for a BIP46 timelock"""
    return f"{message}|{pubkey}|{expiry}"


def prepare_certificate_message(message: str) -> bytes:
    """ message hash for signing """
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


def convert_recoverable_message_signature(sig_base64: str) -> tuple[bytes, int, bool]:
    """ Convert a recoverable signature to a normal signature """
    sig = b64decode(sig_base64)
    if len(sig) != 65:
        raise Bip46RecoverPubkeyError("Invalid signature length")
    header = int(sig[0])
    if header < 27 or header > 42:
        raise Bip46RecoverPubkeyError(f"Header out of range: {header}")
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
