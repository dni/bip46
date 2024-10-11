ELECTRS_SERVER = "https://testnet-electrs.b1tco1n.org"
MAX_INDEX = 959
DEFAULT_NETWORK = "testnet"
NETWORKS = {
    "mainnet": {
        "bech32": "bc",
        "xprv": b"\x04\x88\xad\xe4",
        "bip32": 0,  # coin type for bip32 derivation
    },
    "testnet": {
        "bech32": "tb",
        "xprv": b"\x04\x35\x83\x94",
        "bip32": 1,
    },
    "regtest": {
        "bech32": "bcrt",
        "xprv": b"\x04\x35\x83\x94",
        "bip32": 1,
    },
    "signet": {
        "bech32": "tb",
        "xprv": b"\x04\x35\x83\x94",
        "bip32": 1,
    },
}
