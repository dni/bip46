from base64 import b64encode
from datetime import datetime, timezone

import test_vectors as data

from bip46 import (
    create_certificate_message,
    hdkey_derive,
    hdkey_from_mnemonic,
    hdkey_to_pubkey,
    lockdate_to_derivation_path,
    recover_from_signature_and_message,
    sign_certificate_message,
)
from bip46.certificate import prepare_certificate_message


class TestCertificateMessage:
    """Test vectors for creating timelock addresses"""

    def test_create_certificate_message(self):
        message = create_certificate_message(data.first_certificate_public_key)
        assert data.first_certificate_message == message
        message_hash = prepare_certificate_message(message)
        assert data.first_certificate_message_hash == message_hash.hex()


    def test_sign_certificate_message(self):
        hdkey = hdkey_from_mnemonic(data.mnemonic, data.network)
        lock_date = datetime(2020, 1, 1, tzinfo=timezone.utc)
        lock_path = lockdate_to_derivation_path(lock_date, data.network)
        redeem_child = hdkey_derive(hdkey, lock_path)
        redeem_pub_key = hdkey_to_pubkey(redeem_child)

        assert redeem_pub_key.hex() == data.first_derived_public_key

        sig = sign_certificate_message(redeem_child.secret, data.first_message)

        recovered_pub_key = recover_from_signature_and_message(
            b64encode(sig).decode(), data.first_message
        )
        assert recovered_pub_key.hex() == redeem_pub_key.hex()

        recovered_pubkey2 = recover_from_signature_and_message(
            data.first_signature, data.first_message
        )
        assert recovered_pubkey2.hex() == redeem_pub_key.hex()

        recovered_pubkey3 = recover_from_signature_and_message(
            data.first_certificate_signature, data.first_certificate_message
        )
        assert recovered_pubkey3.hex() == redeem_pub_key.hex()
