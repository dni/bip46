from datetime import datetime, timezone
import test_vectors as data
from base64 import b64encode

from hashlib import sha256

from embit.ec import PrivateKey
from embit.base58 import encode

from bip46 import (
    create_lockscript,
    create_certificate_message,
    hdkey_derive,
    hdkey_from_mnemonic,
    hdkey_to_wif,
    hdkey_to_pubkey,
    lockscript_pubkey,
    lockscript_address,
    lockdate_to_derivation_path,
)


class TestCertificateMessage:
    """Test vectors for creating timelock addresses"""

    def test_sign_certificate_message(self):
        hdkey = hdkey_from_mnemonic(data.mnemonic)
        lock_date = datetime(2020, 1, 1, tzinfo=timezone.utc)
        lock_path = lockdate_to_derivation_path(lock_date)
        lock_child = hdkey_derive(hdkey, lock_path)
        lock_priv_key = hdkey_to_wif(lock_child)
        lock_pub_key = hdkey_to_pubkey(lock_child)

        assert data.first_bond_private_key == lock_priv_key

        lockscript = create_lockscript(lock_date, lock_pub_key)
        script_pubkey = lockscript_pubkey(lockscript)
        assert data.first_script_pubkey ==script_pubkey.hex()

        cert_priv_key = PrivateKey.from_wif(data.first_certificate_private_key)
        cert_pub_key = cert_priv_key.sec().hex()

        assert data.first_certificate_private_key == cert_priv_key.wif()
        assert data.first_certificate_public_key == cert_pub_key

        message = create_certificate_message(cert_pub_key)
        assert data.first_certificate_message == message

        message_hash = sha256(message.encode()).digest()

        sig = lock_child.sign(message_hash)
        assert lock_child.verify(sig, message_hash)

        # assert data.first_certificate_signature == b64encode(sig.serialize()).decode()
        assert data.first_certificate_signature == encode(sig.serialize())


        #
        # pubkey = lockscript_pubkey(lock_script)
        # assert expected.script_pubkey == pubkey.hex()
        #
        # address = lockscript_address(pubkey, network=data.network)
        # assert expected.address == address
