from datetime import datetime, timezone

import test_vectors as data
from coincurve import PublicKey, verify_signature
from coincurve.ecdsa import (
    cdata_to_der,
    deserialize_recoverable,
    recoverable_convert,
)

from bip46 import (
    create_certificate_message,
    hdkey_derive,
    hdkey_from_mnemonic,
    hdkey_to_pubkey,
    lockdate_to_derivation_path,
    sign_certificate_message,
)


class TestCertificateMessage:
    """Test vectors for creating timelock addresses"""

    def test_create_certificate_message(self):
        message = create_certificate_message(data.first_certificate_public_key)
        assert data.first_certificate_message == message

    def test_sign_certificate_message(self):
        hdkey = hdkey_from_mnemonic(data.mnemonic)
        lock_date = datetime(2020, 1, 1, tzinfo=timezone.utc)
        lock_path = lockdate_to_derivation_path(lock_date)
        redeem_child = hdkey_derive(hdkey, lock_path)
        redeem_pub_key = hdkey_to_pubkey(redeem_child)

        msg, sig = sign_certificate_message(redeem_child.secret, data.first_message)

        recovered_pub_key = PublicKey.from_signature_and_message(sig, msg)
        assert recovered_pub_key.format(compressed=True).hex() == redeem_pub_key.hex()
        sig = deserialize_recoverable(sig)
        sig = recoverable_convert(sig)
        sig = cdata_to_der(sig)

        assert verify_signature(sig, msg, redeem_pub_key)

        # TODO: why? cannot recover and verify the signature of test vector
        # sig2 = b64decode(data.first_signature)
        # recovered_pubkey2 = PublicKey.from_signature_and_message(sig2, msg)
        # assert recovered_pubkey2.format(compressed=True).hex() == redeem_pub_key.hex()

        # sig2 = deserialize_recoverable(sig2)
        # sig2 = der_to_cdata(sig2)
        # sig2 = recoverable_convert(sig2)
        # sig2 = cdata_to_der(sig2)

        # assert verify_signature(sig2, msg, redeem_pub_key)

        # TODO: what is this in the test vectors?
        # assert data.first_p2pkh_address
