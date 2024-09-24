# from base64 import b64encode
from datetime import datetime, timezone
from hashlib import sha256

import test_vectors as data

# from embit.base58 import encode
from embit.ec import PrivateKey, secp256k1

from bip46 import (
    create_certificate_message,
    create_redeemscript,
    hdkey_derive,
    hdkey_from_mnemonic,
    hdkey_to_pubkey,
    hdkey_to_wif,
    lockdate_to_derivation_path,
    redeemscript_pubkey,
)


class TestCertificateMessage:
    """Test vectors for creating timelock addresses"""

    def test_sign_certificate_message(self):
        hdkey = hdkey_from_mnemonic(data.mnemonic)
        lock_date = datetime(2020, 1, 1, tzinfo=timezone.utc)
        lock_path = lockdate_to_derivation_path(lock_date)
        redeem_child = hdkey_derive(hdkey, lock_path)
        redeem_priv_key = hdkey_to_wif(redeem_child)
        redeem_pub_key = hdkey_to_pubkey(redeem_child)

        assert data.first_bond_private_key == redeem_priv_key

        redeemscript = create_redeemscript(lock_date, redeem_pub_key)
        script_pubkey = redeemscript_pubkey(redeemscript)
        assert data.first_script_pubkey == script_pubkey.hex()

        cert_priv_key = PrivateKey.from_wif(data.first_certificate_private_key)
        cert_pub_key = cert_priv_key.get_public_key()

        assert data.first_certificate_private_key == cert_priv_key.wif()
        assert data.first_certificate_public_key == cert_pub_key.sec().hex()

        message = create_certificate_message(cert_pub_key.sec().hex())
        assert data.first_certificate_message == message

        message_hash = sha256(message.encode()).digest()

        sig = cert_priv_key.sign(message_hash)
        assert cert_priv_key.get_public_key().verify(sig, message_hash)

        sig2 = redeem_child.sign(message_hash)
        assert redeem_child.verify(sig2, message_hash)

        # sig_rec, sig_rec_id = _sign_recoverable(cert_priv_key.secret, message_hash)
        sig2_rec, sig2_rec_id = _sign_recoverable(redeem_child.secret, message_hash)

        # pub = _verify_recoverable_signature(sig_rec, sig_rec_id, message_hash)
        pub2 = _verify_recoverable_signature(sig2_rec, sig2_rec_id, message_hash)

        # assert pub.hex() == data.first_certificate_public_key
        assert pub2.hex() == data.first_derived_public_key

        # assert b64encode(sig_rec).decode() == data.first_certificate_signature


def _sign_recoverable(message_hash: bytes, secret: bytes) -> tuple[bytes, int]:
    sig_rec = secp256k1.ecdsa_sign_recoverable(message_hash, secret)
    return secp256k1.ecdsa_recoverable_signature_serialize_compact(sig_rec)


def _verify_recoverable_signature(
    sig: bytes, sig_rec_id: int, message_hash: bytes
) -> bytes:
    _sig = secp256k1.ecdsa_recoverable_signature_parse_compact(sig, sig_rec_id)
    recovered_pubkey = secp256k1.ecdsa_recover(_sig, message_hash)
    sig_conv = secp256k1.ecdsa_recoverable_signature_convert(_sig)
    assert secp256k1.ecdsa_verify(sig_conv, message_hash, recovered_pubkey)
    pubkey = secp256k1.ec_pubkey_serialize(recovered_pubkey, secp256k1.EC_COMPRESSED)
    assert pubkey
    return pubkey
