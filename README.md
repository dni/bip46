# BIP46 - Address Scheme for Timelocked Fidelity Bonds

this library is alpha and a work in progress

## example
### create a lockscript
```python
lock_date = datetime(2042, 6, 1)
lock_path = lockdate_to_derivation_path(lock_date)

hdkey = hdkey_from_mnemonic(
    "abandon abandon abandon abandon abandon abandon"
    " abandon abandon abandon abandon abandon about"
)
lock_key = hdkey_derive(hdkey, lock_path)
lock_pub_key = hdkey_to_pubkey(lock_key)
lock_script = create_lockscript(lock_date, lock_pub_key)
script_pubkey = lockscript_pubkey(lock_script)
script_address = lockscript_address(script_pubkey, network="mainnet")
```
