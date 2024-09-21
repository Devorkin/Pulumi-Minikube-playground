from pulumi_kubernetes import Provider as k8s_provider
from pulumi_kubernetes.apiextensions import CustomResource as k8s_api_CustomResource
from pulumi_kubernetes.core.v1 import Secret as Pulumi_K8s_Secret
from pulumi_kubernetes.helm.v3 import Release
from pulumi_kubernetes.helm.v4 import Chart as helm_v4_Chart


from libs.Kubernetes.Cert_Manager import generate_tls_secret, setup_cert_manager
from libs.Kubernetes.Custom_Resources import generate_cluster_issuer
from libs.Kubernetes.Hashicorp_Vault import setup_vault
from libs.Kubernetes.Ingress_Nginx import setup_ingress_nginx
from libs.Kubernetes.Namespaces import (
    hashicorp_ns,
    ingress_nginx_ns,
    monitoring_ns,
)

from libs.Kubernetes.PriorityClasses import low_priority, medium_priority, high_priority

from libs.Kubernetes.Prometheus_stack import setup_prometheus_stack


# K8s manifest
k8s_provider = k8s_provider("minikube-k8s", context="minikube")


cert_manager_chart: helm_v4_Chart = setup_cert_manager()
cert_manager_ca_secret: Pulumi_K8s_Secret = generate_tls_secret()

cluster_issuer: k8s_api_CustomResource = generate_cluster_issuer(
    api_version="cert-manager.io/v1",
    cluster_issuer_name="cert-manager-issuer",
    secret_name=cert_manager_ca_secret.metadata["name"],
    dependencies=[cert_manager_chart],
)

ingress_nginx_chart: Release = setup_ingress_nginx(
    dependencies=[cluster_issuer, cert_manager_chart, ingress_nginx_ns],
    namespace=ingress_nginx_ns.metadata["name"],
)

prometheus_community_chart: Release = setup_prometheus_stack(
    dependencies=[
        ingress_nginx_chart,
        monitoring_ns,
    ],
    namespace=monitoring_ns.metadata["name"],
)

hashicorp_vault_chart: Release = setup_vault(
    dependencies=[
        ingress_nginx_chart,
        hashicorp_ns,
    ],
    namespace=hashicorp_ns.metadata["name"],
)
