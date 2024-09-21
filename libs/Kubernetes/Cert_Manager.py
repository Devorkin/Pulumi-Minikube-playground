from pulumi.dynamic import Resource as Pulumi_Dynamic_Resource
from pulumi_kubernetes.core.v1 import Secret as Pulumi_K8s_Secret
from pulumi_kubernetes.helm.v4 import Chart as helm_v4_Chart
from pulumi_kubernetes.helm.v4 import RepositoryOptsArgs


from libs.Kubernetes.Namespaces import cert_manager_ns
from libs.Kubernetes.Secrets import generate_tls_cert_secret
from libs.pulumi_custom_resources.ca_certificate import pulumi_new_ca_authority_rsc

from utils.x509_certificates import X509_Certificates


# Create CA certificate
obj_x509 = X509_Certificates(
    certificate_name="minikube_test_ca",
    city="Petah Tiqwa",
    country_code="IL",
    organization_name="tests.net",
    state_code="TLV",
)


# Create a new CA certificate & key files and Pulumi resources if these do not exists
certificate_content: bytes = None
encoded_private_key: bytes = None

certificate_content, encoded_private_key = obj_x509.generate_ca_cert()
certificate_file: Pulumi_Dynamic_Resource = pulumi_new_ca_authority_rsc(
    "certFile",
    content=certificate_content.decode("utf-8"),
    path=obj_x509.certificate_filename,
)
certificate_key_file: Pulumi_Dynamic_Resource = pulumi_new_ca_authority_rsc(
    "certKeyFile",
    content=encoded_private_key.decode("utf-8"),
    path=obj_x509.certificate_key_filename,
)


# Deploy Cert-Manager
def setup_cert_manager() -> helm_v4_Chart:
    cert_manager_chart = helm_v4_Chart(
        "cert-manager",
        chart="cert-manager",
        namespace=cert_manager_ns.metadata["name"],
        repository_opts=RepositoryOptsArgs(
            repo="https://charts.jetstack.io",
        ),
        values={"crds": {"enabled": True}},
    )

    return cert_manager_chart


def generate_tls_secret() -> Pulumi_K8s_Secret:
    cert_manager_ca_secret: Pulumi_K8s_Secret = generate_tls_cert_secret(
        certificate_name=obj_x509.certificate_name.replace("_", "-"),
        certificate_content=certificate_content,
        encoded_private_key=encoded_private_key,
        namespace=cert_manager_ns.metadata["name"],
    )

    return cert_manager_ca_secret
