import httpx

from .consts import ELECTRS_SERVER


def get_tx(txid: str, electrs_server: str = ELECTRS_SERVER) -> dict:
    """Get a transaction from a block explorer"""
    url = f"{electrs_server}/tx/{txid}"
    return request(url)


def get_txs_from_address(address: str, electrs_server: str = ELECTRS_SERVER) -> dict:
    """Get a transaction from a block explorer"""
    url = f"{electrs_server}/address/{address}/txs"
    return request(url)


def request(url: str) -> dict:
    with httpx.Client() as client:
        resp = client.get(url)
        resp.raise_for_status()
        return resp.json()
