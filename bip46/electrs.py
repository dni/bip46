from typing import Optional

import httpx

from .consts import ELECTRS_SERVER


def request(url: str) -> dict:
    with httpx.Client() as client:
        resp = client.get(url)
        resp.raise_for_status()
        return resp.json()


def get_tx(txid: str, electrs_server: str = ELECTRS_SERVER) -> dict:
    """Get a transaction from a block explorer"""
    url = f"{electrs_server}/tx/{txid}"
    return request(url)


def get_txs_from_address(address: str, electrs_server: str = ELECTRS_SERVER) -> dict:
    """Get a transaction from a block explorer"""
    url = f"{electrs_server}/address/{address}/txs"
    return request(url)


def get_vout_from_tx(tx: dict, address: str) -> Optional[tuple[str, int, int]]:
    for i, out in enumerate(tx["vout"]):
        if out["scriptpubkey_address"] == address:
            return tx["txid"], i, out["value"]
    return None


def get_vout_from_txs(txs: dict, address: str) -> Optional[tuple[str, int, int]]:
    for tx in txs:
        vout = get_vout_from_tx(tx, address)
        if vout:
            return vout
    return None
