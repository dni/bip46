""" Example of a timelock withdrawal transaction """

from embit.script import Script, Witness, address_to_scriptpubkey
from embit.transaction import Transaction, TransactionInput, TransactionOutput

from bip46.derivation import index_to_lockdate, lockindex_to_derivation_path
from bip46.electrs import get_txs_from_address, get_vout_from_txs
from bip46.hdkey import hdkey_derive, hdkey_from_mnemonic, hdkey_to_pubkey
from bip46.script import create_redeemscript

NETWORK = "testnet"
MNEMONIC = (
    "abandon abandon abandon abandon abandon abandon"
    " abandon abandon abandon abandon abandon about"
)

# address used to fund the testnet timelock
RECEIVE_ADDRESS = "tb1qzafmult395n8dlflv8ez5ja9rqg0gdlc20rw0p"
TIMELOCK_ADDRESS = "tb1q7war3lusq3ez633rzzfkp75unfcgrqqcu80sgp0ellhrdvkzxh5srftzav"
TIMELOCK_INDEX = 0

fee_sats_vbyte = 20
tx_size = 200
fee_sats = fee_sats_vbyte * tx_size

# recreate redeem script
lock_path = lockindex_to_derivation_path(TIMELOCK_INDEX, NETWORK)
lock_date = index_to_lockdate(TIMELOCK_INDEX)
hdkey = hdkey_from_mnemonic(MNEMONIC, NETWORK)
redeem_child = hdkey_derive(hdkey, lock_path)
redeem_pub_key = hdkey_to_pubkey(redeem_child)
redeem_script = create_redeemscript(lock_date, redeem_pub_key)

# get onchain data
txs = get_txs_from_address(TIMELOCK_ADDRESS)
output = get_vout_from_txs(txs, TIMELOCK_ADDRESS)
assert output, f"No timelock output found for address {TIMELOCK_ADDRESS}"
prevtxid, vout, value = output

# prepare transaction
receive_address = address_to_scriptpubkey(RECEIVE_ADDRESS)
txout = TransactionOutput(value - fee_sats, receive_address)
# sequence for rbf / absolute locktime
txin = TransactionInput(bytes.fromhex(prevtxid), vout, sequence=0xfffffffd)
# proper locktime is needed for OP_CLTV
locktime = int(lock_date.timestamp())
tx = Transaction(vin=[txin], vout=[txout], locktime=locktime)

# sign transaction
script = Script(data=redeem_script)
h = tx.sighash_segwit(0, script, value)
sig = redeem_child.sign(h).serialize() + bytes([0x01]) # SIGHASH.ALL
witness_script = Witness(items=[sig, redeem_script])
tx.vin[0].witness = witness_script

print(f"raw transaction: {tx.serialize().hex()}")
