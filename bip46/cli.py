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
    hdkey_to_pubkey,
    hdkey_scan,
    hdkey_scan_all,
    # index_to_lockdate,
    lockdate_to_derivation_path,
    # lockindex_to_derivation_path,
    redeemscript_address,
    redeemscript_pubkey,
)

# disable tracebacks on exceptions
sys.tracebacklimit = 0

def _check_private_key() -> HDKey:
    """check if the environment is set"""
    if "SEED" in os.environ:
        return hdkey_from_seed(os.environ["SEED"].encode())
    elif "MNEMONIC" in os.environ:
        return hdkey_from_mnemonic(os.environ["MNEMONIC"])
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
@click.argument("network", type=str, default="main")
def scan_all(network: str):
    """
    scan for all timelocks
    """
    key = _check_private_key()
    bonds = hdkey_scan_all(key)
    print(f"Found {len(bonds)} timelocked bonds:")
    for bond in bonds:
        print(bond.index, bond.txid, bond.address)

@click.command()
@click.argument("index", type=int)
@click.argument("network", type=str, default="main")
def scan(index: int, network: str):
    """
    scan for all timelocks
    """
    key = _check_private_key()
    bonds = hdkey_scan(index, key)
    print(f"Found {len(bonds)} timelocked bonds")
    for bond in bonds:
        print(bond.index, bond.txid, bond.address)


@click.command()
@click.argument("year", type=int)
@click.argument("month", type=int)
@click.argument("network", type=str, default="main")
def create_timelock(year: int, month: int, network: str):
    """
    create a timelock address
    """
    key = _check_private_key()
    lock_date = datetime(year, month, 1, tzinfo=timezone.utc)
    lock_path = lockdate_to_derivation_path(lock_date)
    redeem_child = hdkey_derive(key, lock_path)
    redeem_pub_key = hdkey_to_pubkey(redeem_child)
    redeem_script = create_redeemscript(lock_date, redeem_pub_key)
    script_pubkey = redeemscript_pubkey(redeem_script)
    script_address = redeemscript_address(script_pubkey, network="main")

    print(f"network: {network}")
    print(f"lock_date: {lock_date.isoformat()}")
    print(f"lock_path: {lock_path}")
    print(f"script address: {script_address}")


# @click.command()
# @click.argument("previous_txid", type=str)
# @click.argument("vout", type=int)
# @click.argument("lock_index", type=int)
# @click.argument("receive_address", type=str)
# @click.argument("network", type=str, default="main")
# def redeem_timelock(previous_txid: str, vout: int, lock_index: int, receive_address: str, network: str):
#     """
#     create a timelock address
#     """
#     key = _check_private_key()
#     lock_path = lockindex_to_derivation_path(lock_index)
#     lock_date = index_to_lockdate(lock_index)
#     redeem_child = hdkey_derive(key, lock_path)
#     redeem_pub_key = hdkey_to_pubkey(redeem_child)
#     redeem_script = create_redeemscript(lock_date, redeem_pub_key)
#     script_pubkey = redeemscript_pubkey(redeem_script)
#
#     print(f"network: {network}")
#     print(f"lock_date: {lock_date.isoformat()}")
#     # print(f"script address: {script_address}")


@click.command()
@click.argument("pubkey", type=str)
# @click.argument("ignore_exceptions", type=bool, default=True)
# @click.argument("strict", type=bool, default=False)
def create_certificate(pubkey: str):
    """
    create a certificate
    """
    click.echo("create_certificate")


def main():
    """main function"""
    command_group.add_command(create_certificate)
    command_group.add_command(create_timelock)
    command_group.add_command(scan)
    command_group.add_command(scan_all)
    command_group()


if __name__ == "__main__":
    main()
