from dataclasses import dataclass
from datetime import datetime, timezone

import test_vectors as data

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


@dataclass
class Expected:
    unix_locktime: int
    derived_public_key: str
    derived_private_key: str
    script_pubkey: str
    address: str
    redeem_script: str
    path: str


def _assert_script(lock_date: datetime, expected: Expected):
    unix_locktime = int(lock_date.timestamp())
    assert expected.unix_locktime == unix_locktime

    lock_path = lockdate_to_derivation_path(lock_date)
    assert expected.path == lock_path

    hdkey = hdkey_from_mnemonic(data.mnemonic)
    lock_child = hdkey_derive(hdkey, lock_path)
    lock_priv_key = hdkey_to_wif(lock_child)
    lock_pub_key = hdkey_to_pubkey(lock_child)

    assert expected.derived_public_key == lock_pub_key.hex()
    assert expected.derived_private_key == lock_priv_key

    lock_script = create_lockscript(lock_date, lock_pub_key)
    pubkey = lockscript_pubkey(lock_script)
    assert expected.script_pubkey == pubkey.hex()

    address = lockscript_address(pubkey, network=data.network)
    assert expected.address == address

    # redeem_script = _redeem_script.serialize()
    # assert data.first_redeemscript == redeem_script.hex()


class TestCreateTimelockAddress:
    """Test vectors for creating timelock addresses"""

    def test_create_first_timelock_address(self):
        lock_date = datetime(2020, 1, 1, tzinfo=timezone.utc)
        expected = Expected(
            path="m/84'/0'/0'/2/0",
            unix_locktime=data.first_unix_locktime,
            derived_public_key=data.first_derived_public_key,
            derived_private_key=data.first_derived_private_key,
            script_pubkey=data.first_script_pubkey,
            address=data.first_address,
            redeem_script=data.first_redeemscript,
        )
        _assert_script(lock_date, expected)

    def test_create_second_timelock_address(self):
        lock_date = datetime(2020, 2, 1, tzinfo=timezone.utc)
        expected = Expected(
            path="m/84'/0'/0'/2/1",
            unix_locktime=data.second_unix_locktime,
            derived_public_key=data.second_derived_public_key,
            derived_private_key=data.second_derived_private_key,
            script_pubkey=data.second_script_pubkey,
            address=data.second_address,
            redeem_script=data.second_redeemscript,
        )
        _assert_script(lock_date, expected)

    def test_create_third_timelock_address(self):
        lock_date = datetime(2040, 1, 1, tzinfo=timezone.utc)
        expected = Expected(
            path="m/84'/0'/0'/2/240",
            unix_locktime=data.third_unix_locktime,
            derived_public_key=data.third_derived_public_key,
            derived_private_key=data.third_derived_private_key,
            script_pubkey=data.third_script_pubkey,
            address=data.third_address,
            redeem_script=data.third_redeemscript,
        )
        _assert_script(lock_date, expected)

    def test_create_last_timelock_address(self):
        lock_date = datetime(2099, 12, 1, tzinfo=timezone.utc)
        expected = Expected(
            path="m/84'/0'/0'/2/959",
            unix_locktime=data.last_unix_locktime,
            derived_public_key=data.last_derived_public_key,
            derived_private_key=data.last_derived_private_key,
            script_pubkey=data.last_script_pubkey,
            address=data.last_address,
            redeem_script=data.last_redeemscript,
        )
        _assert_script(lock_date, expected)
