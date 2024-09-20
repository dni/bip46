from datetime import datetime, timezone

import pytest

from bip46 import (
    DERIVATION_PATH,
    Bip46IndexError,
    Bip46TimeError,
    index_to_lockdate,
    timelock_derivation_path,
)

valid_dates = [
    (0, datetime(2020, 1, 1, tzinfo=timezone.utc)),
    (959, datetime(2099, 12, 1, tzinfo=timezone.utc)),
    (240, datetime(2040, 1, 1, tzinfo=timezone.utc)),
]


class TestTimelockDerivation:

    @pytest.mark.parametrize(
        "lock_date",
        [
            datetime(2019, 12, 1, tzinfo=timezone.utc),
            datetime(2100, 1, 1, tzinfo=timezone.utc),
            datetime(1970, 1, 1, tzinfo=timezone.utc),
        ],
    )
    def test_date_out_of_range(self, lock_date):
        with pytest.raises(Bip46TimeError):
            timelock_derivation_path(lock_date)

    @pytest.mark.parametrize("index, lock_date", valid_dates)
    def test_date_in_range(self, index, lock_date):
        path = timelock_derivation_path(lock_date)
        expected_path = f"{DERIVATION_PATH}/{index}"
        assert path == expected_path

    @pytest.mark.parametrize("path, index, network", [
        ("m/84'/0'/0'/2/0", 0, "mainnet"),
        ("m/84'/1'/0'/2/0", 0, "testnet"),
        ("m/84'/1'/0'/2/0", 0, "signet"),
        ("m/84'/1'/0'/2/0", 0, "regtest"),
    ])
    def test_timelock_derivation_path(self, path, index, network):
        date = index_to_lockdate(index)
        assert timelock_derivation_path(date, network) == path


class TestTimelockIndexToDate:

    @pytest.mark.parametrize("index", [-1, 960])
    def test_index_out_of_range(self, index):
        with pytest.raises(Bip46IndexError):
            index_to_lockdate(index)

    @pytest.mark.parametrize("index, lock_date", valid_dates)
    def test_index_to_date(self, index, lock_date):
        assert index_to_lockdate(index) == lock_date
