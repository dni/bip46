from datetime import datetime, timezone

import test_vectors as data
from buidl import HDPrivateKey, WitnessScript

from bip46 import lockdate_to_little_endian, timelock_derivation_path


class TestCreateTimelockAddress:

    def test_create_first_timelock_address(self):
        lock_date = datetime(2020, 1, 1, tzinfo=timezone.utc)
        assert data.first_unix_locktime == int(lock_date.timestamp())

        lock_path = timelock_derivation_path(lock_date)

        hdkey = HDPrivateKey.from_mnemonic(data.mnemonic, network=data.network)
        lock_child = hdkey.traverse(lock_path)
        lock_pubkey = lock_child.pub.sec()

        assert data.first_derived_public_key == lock_pubkey.hex()

        lock_time = lockdate_to_little_endian(lock_date)

        # locktime OP_CLTV OP_DROP pubkey OP_CHECKSIG
        lock_script = WitnessScript([lock_time, 177, 117, lock_pubkey, 172])
        print(lock_script)

        script_pubkey = lock_script.script_pubkey().serialize()
        assert data.first_script_pubkey == script_pubkey.hex()

        lock_address = lock_script.address(network=data.network)
        assert lock_address == data.first_address

        # redeem_script = _redeem_script.serialize()
        # assert data.first_redeemscript == redeem_script.hex()
