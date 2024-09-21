from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey
from cryptography.x509 import (
    BasicConstraints,
    CertificateBuilder,
    KeyUsage,
    SubjectKeyIdentifier,
)
from cryptography.x509 import random_serial_number as X509_random_serial_number
from cryptography.x509 import Name as X509_Name
from cryptography.x509 import NameAttribute as X509_NameAttribute
from cryptography.x509.oid import NameOID as X509_NameOID
from cryptography.hazmat.primitives.serialization import (
    Encoding,
    NoEncryption,
    PrivateFormat,
)
from datetime import datetime, timedelta
from os import path


from utils.file_reader import readFileContentInBytes


class X509_Certificates:
    def __init__(
        self,
        certificate_filename: str = "ca.crt",
        certificate_key_filename: str = "ca.key",
        certificate_name: str = None,
        city: str = None,
        country_code: str = None,
        days_to_live: int = 365,
        organization_name: str = None,
        state_code: str = None,
    ) -> None:
        """
        Initialize the X509_Certificates class object

        Args:
        certificate_filename (str): To be updated; default: "ca.crt"
        certificate_key_filename (str) To be updated; default: "ca.key"
        certificate_name (str): The name of the CA.
        city (str): To be updated.
        country_code (str): To be updated.
        days_to_live (int): To be updated.
        organization_name (str): To be updated.
        state_code (str): To be updated.

        BuiltIn:
        valid_from (datetime.datetime): The start date of the certificate validity.
        valid_to (datetime.datetime): The end date of the certificate validity.
        """

        self.certificate_filename = certificate_filename
        self.certificate_key_filename = certificate_key_filename
        self.certificate_name = certificate_name
        self.city = city
        self.country_code = country_code
        self.organization_name = organization_name
        self.state_code = state_code
        self.valid_from = datetime.now()
        self.valid_to = datetime.now() + timedelta(days=days_to_live)

    def generate_ca_cert(self) -> tuple:
        """
        Generates a self-signed CA certificate using Ed25519.

        Returns:
            tuple: A tuple containing the CA certificate and private key.
        """

        # If CA certificate and key files already exists, load them instead of creating a new pair
        if path.exists(self.certificate_filename) and path.exists(
            self.certificate_key_filename
        ):
            certificate_content: bytes = readFileContentInBytes(
                self.certificate_filename
            )
            encoded_private_key: bytes = readFileContentInBytes(
                self.certificate_key_filename
            )

        else:
            # Generate Ed25519 private key
            private_key_content = Ed25519PrivateKey.generate()

            # Create subject and issuer
            subject = issuer = X509_Name(
                [
                    X509_NameAttribute(X509_NameOID.COUNTRY_NAME, self.country_code),
                    X509_NameAttribute(
                        X509_NameOID.STATE_OR_PROVINCE_NAME, self.state_code
                    ),
                    X509_NameAttribute(X509_NameOID.LOCALITY_NAME, self.city),
                    X509_NameAttribute(
                        X509_NameOID.ORGANIZATION_NAME, self.organization_name
                    ),
                    X509_NameAttribute(X509_NameOID.COMMON_NAME, self.certificate_name),
                ]
            )

            # Create certificate builder
            cert_builder = (
                CertificateBuilder()
                .subject_name(subject)
                .issuer_name(issuer)
                .public_key(private_key_content.public_key())
                .serial_number(X509_random_serial_number())
                .not_valid_before(self.valid_from)
                .not_valid_after(self.valid_to)
                .add_extension(
                    BasicConstraints(ca=True, path_length=None),
                    critical=True,
                )
                .add_extension(
                    KeyUsage(
                        key_cert_sign=True,
                        crl_sign=True,
                        digital_signature=False,
                        content_commitment=False,
                        key_encipherment=False,
                        data_encipherment=False,
                        key_agreement=False,
                        encipher_only=False,
                        decipher_only=False,
                    ),
                    critical=True,
                )
                .add_extension(
                    SubjectKeyIdentifier.from_public_key(
                        private_key_content.public_key()
                    ),
                    critical=False,
                )
            )

            # Sign the certificate
            cert = cert_builder.sign(private_key=private_key_content, algorithm=None)
            certificate_content: bytes = cert.public_bytes(encoding=Encoding.PEM)

            encoded_private_key: bytes = private_key_content.private_bytes(
                encoding=Encoding.PEM,
                format=PrivateFormat.PKCS8,
                encryption_algorithm=NoEncryption(),
            )

        return certificate_content, encoded_private_key
