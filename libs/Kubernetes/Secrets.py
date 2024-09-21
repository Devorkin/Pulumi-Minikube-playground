from base64 import b64encode

from pulumi_kubernetes.core.v1 import Secret
from pulumi_kubernetes.meta.v1 import ObjectMetaArgs


def generate_tls_cert_secret(
    certificate_name: str = None,
    certificate_content: bytes = None,
    encoded_private_key: bytes = None,
    namespace: str = None,
) -> Secret:

    # Deploy the Secret resource
    tls_cert_secret = Secret(
        certificate_name,
        metadata=ObjectMetaArgs(
            name=certificate_name,
            namespace=namespace,
        ),
        type="kubernetes.io/tls",
        data={
            "tls.crt": b64encode(certificate_content).decode("utf-8"),
            "tls.key": b64encode(encoded_private_key).decode("utf-8"),
        },
    )

    return tls_cert_secret
