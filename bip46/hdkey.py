from dataclasses import dataclass

from embit.bip32 import HDKey
from embit.bip39 import mnemonic_to_seed

from .consts import DEFAULT_NETWORK, MAX_INDEX, NETWORKS
from .derivation import index_to_lockdate, lockindex_to_derivation_path
from .electrs import get_txs_from_address
from .exceptions import Bip46PathError
from .script import create_redeemscript, redeemscript_address, redeemscript_pubkey


@dataclass
class Bond:
    index: int
    address: str
    txid: str
    hdkey: HDKey


def hdkey_scan(index: int, hdkey: HDKey, network: str = DEFAULT_NETWORK) -> list[Bond]:
    """
    Scan a path for all possible keys timelocks
    """
    bonds = []
    path = lockindex_to_derivation_path(index, network)
    hdkey_i = hdkey.derive(path)
    pubkey = hdkey_to_pubkey(hdkey_i)
    lock_date = index_to_lockdate(index)
    redeemscript = create_redeemscript(lock_date, pubkey)
    address = redeemscript_address(redeemscript_pubkey(redeemscript), network)
    print(f"({index}/{MAX_INDEX}) Scanning timelocks for address {address}")
    txs = get_txs_from_address(address)
    if len(txs) > 0:
        print(f"Found {len(txs)} timelocks for index {index} !!!")
        for tx in txs:
            bonds.append(Bond(index, address, tx.get("txid"), hdkey_i))
    return bonds


def hdkey_scan_all(hdkey: HDKey, network: str = DEFAULT_NETWORK) -> list[Bond]:
    """
    Scan a path for all possible keys timelocks
    """
    bonds = []
    for i in range(MAX_INDEX):
        bonds.extend(hdkey_scan(i, hdkey, network))
    return bonds


def hdkey_from_seed(seed: bytes, network: str = DEFAULT_NETWORK) -> HDKey:
    """Create a HDKey from a seed"""
    version = NETWORKS[network]["xprv"]
    master = HDKey.from_seed(seed, version=version)
    return master


def hdkey_from_mnemonic(mnemonic: str, network: str = DEFAULT_NETWORK) -> HDKey:
    """Create a HDKey from a mnemonic"""
    seed = mnemonic_to_seed(mnemonic)
    return hdkey_from_seed(seed, network)


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


def hdkey_to_pubkey(hdkey: HDKey) -> bytes:
    """Get the pubkey from an HDKey"""
    return hdkey.get_public_key().sec()
