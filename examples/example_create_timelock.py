from datetime import datetime

from bip46 import (
    create_lockscript,
    hdkey_derive,
    hdkey_from_mnemonic,
    hdkey_to_pubkey,
    hdkey_to_wif,
    lockdate_to_derivation_path,
    lockscript_address,
    lockscript_pubkey,
)

lock_date = datetime(2042, 6, 1)
lock_path = lockdate_to_derivation_path(lock_date)

hdkey = hdkey_from_mnemonic(
    "abandon abandon abandon abandon abandon abandon"
    " abandon abandon abandon abandon abandon about"
)
lock_key = hdkey_derive(hdkey, lock_path)
lock_priv_key = hdkey_to_wif(lock_key)
lock_pub_key = hdkey_to_pubkey(lock_key)
lock_script = create_lockscript(lock_date, lock_pub_key)
script_pubkey = lockscript_pubkey(lock_script)
script_address = lockscript_address(script_pubkey, network="main")

print(f"lock date: {lock_date}")
print(f"lock path: {lock_path}")
print(f"lock key: {lock_priv_key}")
print(f"lock pubkey: {lock_pub_key.hex()}")
print(f"lock script: {lock_script.hex()}")
print(f"script pubkey: {script_pubkey.hex()}")
print(f"script address: {script_address}")
