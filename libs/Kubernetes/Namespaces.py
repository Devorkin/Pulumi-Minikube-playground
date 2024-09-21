from pulumi_kubernetes.core.v1 import Namespace
from pulumi_kubernetes.meta.v1 import ObjectMetaArgs

cert_manager_ns = Namespace(
    "cert-manager", metadata=ObjectMetaArgs(name="cert-manager")
)

hashicorp_ns = Namespace("hashicorp", metadata=ObjectMetaArgs(name="hashicorp"))

monitoring_ns = Namespace("monitoring", metadata=ObjectMetaArgs(name="monitoring"))

ingress_nginx_ns = Namespace(
    "ingress_nginx", metadata=ObjectMetaArgs(name="ingress-nginx")
)

playground_ns = Namespace("playground-ns", metadata=ObjectMetaArgs(name="playground"))
