""" embit sanity example """
from embit.bip32 import HDKey
from embit.bip39 import mnemonic_to_seed
from embit.networks import NETWORKS

mnemonic = (
    "abandon abandon abandon abandon abandon abandon"
    " abandon abandon abandon abandon abandon about"
)
print(f"mnemonic: {mnemonic}")
seed = mnemonic_to_seed(mnemonic)
version = NETWORKS["test"]["xprv"]
print(f"version: {version}")
master = HDKey.from_seed(seed, version=version)

path = "m/84'/1'/0'/2/0"
derived = master.derive(path)

print(f"path: {path}")
print(f"Derived private key: {derived.key.serialize().hex()}")
print(f"Derived public key: {derived.get_public_key().serialize().hex()}")
