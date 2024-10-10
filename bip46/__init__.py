from embit.script import address_to_scriptpubkey
from embit.transaction import Transaction, TransactionInput, TransactionOutput

from .certificate import (
    create_certificate_message,
    recover_from_signature_and_message,
    sign_certificate_message,
)
from .derivation import (
    index_to_lockdate,
    lockdate_to_derivation_path,
    lockdate_to_index,
    lockindex_to_derivation_path,
)
from .exceptions import (
    Bip46Bech32Error,
    Bip46IndexError,
    Bip46PathError,
    Bip46RecoverPubkeyError,
    Bip46TimeError,
)
from .hdkey import (
    hdkey_derive,
    hdkey_from_mnemonic,
    hdkey_from_seed,
    hdkey_from_wif,
    hdkey_scan,
    hdkey_scan_all,
    hdkey_to_pubkey,
    hdkey_to_wif,
)
from .script import create_redeemscript, redeemscript_address, redeemscript_pubkey


# WIP
def create_redeem_transaction(
    prevtxid: str,
    vout: int,
    redeemscript: bytes,
    address: str,
    fee_sats_vbyte: int = 10,
    # network: str = DEFAULT_NETWORK,
) -> str:
    """Create a redeem transaction for a BIP46 timelock"""
    tx_size = 100
    amount = 100000 - fee_sats_vbyte * tx_size
    receive_address = address_to_scriptpubkey(address)
    txout = TransactionOutput(amount, receive_address)
    txin = TransactionInput(prevtxid, vout, redeemscript)
    tx = Transaction(2, [txin], [txout])
    return tx.serialize().hex()


__all__ = [
    # exceptions
    "Bip46Bech32Error",
    "Bip46IndexError",
    "Bip46PathError",
    "Bip46RecoverPubkeyError",
    "Bip46TimeError",
    # certificate
    "create_certificate_message",
    "recover_from_signature_and_message",
    "sign_certificate_message",
    # hdkey
    "hdkey_scan",
    "hdkey_scan_all",
    "hdkey_derive",
    "hdkey_to_pubkey",
    "hdkey_to_wif",
    "hdkey_from_wif",
    "hdkey_from_seed",
    "hdkey_from_mnemonic",
    # derivation
    "index_to_lockdate",
    "lockdate_to_derivation_path",
    "lockdate_to_index",
    "lockindex_to_derivation_path",
    # script
    "create_redeemscript",
    "redeemscript_pubkey",
    "redeemscript_address",
]
