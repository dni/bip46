""" bip46 CLI """


import os
import sys
from datetime import datetime, timezone

import click
from embit.bip32 import HDKey

from bip46 import (
    create_redeemscript,
    hdkey_derive,
    hdkey_from_mnemonic,
    hdkey_from_seed,
    hdkey_scan,
    hdkey_scan_all,
    hdkey_to_pubkey,
    index_to_lockdate,
    lockdate_to_derivation_path,
    redeemscript_address,
    redeemscript_pubkey,
)
from bip46.consts import DEFAULT_NETWORK

# disable tracebacks on exceptions
sys.tracebacklimit = 0

def _check_private_key(network: str) -> HDKey:
    """check if the environment is set"""
    if "SEED" in os.environ:
        return hdkey_from_seed(os.environ["SEED"].encode(), network)
    elif "MNEMONIC" in os.environ:
        return hdkey_from_mnemonic(os.environ["MNEMONIC"], network)
    else:
        click.echo("please set `SEED` or `MNEMONIC` environment variable")
        sys.exit(1)


@click.group()
def command_group():
    """
    Python CLI for bip46 timelocks\n
    set `SEED` or `MNEMONIC` environment variable to set the seed
    """


@click.command()
@click.argument("network", type=str, default=DEFAULT_NETWORK)
def scan_all(network: str):
    """
    scan for all timelocks
    """
    key = _check_private_key(network)
    bonds = hdkey_scan_all(key, network)
    print(f"Found {len(bonds)} timelocked bonds:")
    for bond in bonds:
        print(bond.index, bond.txid, bond.address)

@click.command()
@click.argument("index", type=int)
@click.argument("network", type=str, default=DEFAULT_NETWORK)
def scan(index: int, network: str):
    """
    scan for all timelocks
    """
    key = _check_private_key(network)
    print("key:", key)
    print("key:", key.key)
    bonds = hdkey_scan(index, key, network)
    print(f"Found {len(bonds)} timelocked bonds")
    for bond in bonds:
        print(bond.index, bond.txid, bond.address)


@click.command()
@click.argument("year", type=int)
@click.argument("month", type=int)
@click.argument("network", type=str, default=DEFAULT_NETWORK)
def create_timelock(year: int, month: int, network: str):
    """
    create a timelock address
    """
    key = _check_private_key(network)
    lock_date = datetime(year, month, 1, tzinfo=timezone.utc)
    lock_path = lockdate_to_derivation_path(lock_date, network)
    redeem_child = hdkey_derive(key, lock_path)
    redeem_pub_key = hdkey_to_pubkey(redeem_child)
    redeem_script = create_redeemscript(lock_date, redeem_pub_key)
    script_pubkey = redeemscript_pubkey(redeem_script)
    script_address = redeemscript_address(script_pubkey, network=network)

    print(f"network: {network}")
    print(f"lock_date: {lock_date.isoformat()}")
    print(f"lock_path: {lock_path}")
    print(f"script address: {script_address}")


@click.command()
@click.argument("year", type=int)
@click.argument("month", type=int)
@click.argument("network", type=str, default=DEFAULT_NETWORK)
def get_derivation_path(year: int, month: int, network: str):
    """
    create a timelock address
    """
    lock_date = datetime(year, month, 1, tzinfo=timezone.utc)
    lock_path = lockdate_to_derivation_path(lock_date, network)
    print(lock_path)


@click.command()
@click.argument("index", type=int)
def get_lockdate(index: int):
    """
    get the lock date from an index
    """
    lock_path = index_to_lockdate(index)
    print(lock_path.isoformat())


def main():
    """main function"""
    command_group.add_command(create_timelock)
    command_group.add_command(scan)
    command_group.add_command(scan_all)
    command_group.add_command(get_derivation_path)
    command_group.add_command(get_lockdate)
    command_group()


if __name__ == "__main__":
    main()
