from datetime import datetime

from bip46 import (
    create_redeemscript,
    hdkey_derive,
    hdkey_from_mnemonic,
    hdkey_to_pubkey,
    lockdate_to_derivation_path,
    redeemscript_address,
    redeemscript_pubkey,
)

lock_date = datetime(2042, 6, 1)
lock_path = lockdate_to_derivation_path(lock_date)

hdkey = hdkey_from_mnemonic(
    "abandon abandon abandon abandon abandon abandon"
    " abandon abandon abandon abandon abandon about"
)
redeem_key = hdkey_derive(hdkey, lock_path)
redeem_pub_key = hdkey_to_pubkey(redeem_key)
redeem_script = create_redeemscript(lock_date, redeem_pub_key)
script_pubkey = redeemscript_pubkey(redeem_script)
script_address = redeemscript_address(script_pubkey)

print(f"lock date: {lock_date}")
print(f"lock path: {lock_path}")
print(f"lock pubkey: {redeem_pub_key.hex()}")
print(f"redeem script: {redeem_script.hex()}")
print(f"script pubkey: {script_pubkey.hex()}")
print(f"script address: {script_address}")
