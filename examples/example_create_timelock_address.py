# import os
# from datetime import datetime, timezone

# from buidl import HDPrivateKey, WitnessScript, Tx, TxIn, TxOut
# from bip46 import timelock_derivation_path, lockdate_to_little_endian


# NETWORK = "testnet"
# SEED = os.environ.get("SEED")
# # NETWORK = "mainnet"

# fee = 600
# amount_send = 60000
# lock_date = datetime(2023, 10, 1, tzinfo=timezone.utc)

# # change_path = "m/84'/1'/0'/1/47"
# # input_path = "m/84'/1'/0'/0/15"
# # prev_txid = "7566245951f6a16b062ae8db02aa95ed1878afe015e4a4251e3188109348cf79"
# # vout = 1

# withdraw_path = "m/84'/1'/0'/0/16"

# lock_txid = "49702a3c03c2a8d2f151dc3dc8f6076498002e2898a0746760f4699e97b252e8"
# lock_vout = 0


# if not SEED:
#     raise ValueError("SEED environment variable not set")


# hdkey = HDPrivateKey.from_mnemonic(SEED, network=NETWORK)
# lock_path = timelock_derivation_path(lock_date)
# lock_time = lockdate_to_little_endian(lock_date)
# lock_child = hdkey.traverse(lock_path)
# lock_pubkey = lock_child.pub.sec()

# # locktime OP_CLTV OP_DROP pubkey OP_CHECKSIG
# lock_script = WitnessScript([lock_time, 177, 117, lock_pubkey, 172])
# # lock_address = lock_script.address(network=NETWORK)

# # change_child = hdkey.traverse(change_path)
# # change_address = change_child.p2wpkh_address()

# # print(f"lock_date: {lock_date}")
# # print(f"lock_path: {lock_path}")
# # print(f"lock address: {lock_address}")
# # print(f"change address {change_path}: {change_address}")

# # input_child = hdkey.traverse(input_path)
# # tx_in = TxIn(bytes.fromhex(prev_txid), vout)

# withdraw_child = hdkey.traverse(withdraw_path)
# withdraw_address = withdraw_child.p2wpkh_address()

# tx_in = TxIn(bytes.fromhex(lock_txid), lock_vout)
# # tx_in.finalize_p2wpkh(sig, lock_child.sec(), redeem_script=lock_script)

# utxo_amount = tx_in.value(network=NETWORK)
# amount2 = utxo_amount - amount_send - fee

# tx_out = TxOut.to_address(amount=amount_send, address=withdraw_address)
# # tx_change = TxOut.to_address(amount=amount2, address=change_address)

# tx = Tx(version=2, locktime=0, tx_ins=[tx_in], tx_outs=[tx_out])
# tx.sign_input(0, lock_child.private_key)  # , lock_script)


# print("tx signed:")
# print(bytes.hex(tx.serialize_segwit()))
