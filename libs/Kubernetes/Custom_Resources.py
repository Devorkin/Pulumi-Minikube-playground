from pulumi import ResourceOptions
from pulumi_kubernetes.apiextensions import CustomResource as k8s_api_CustomResource
from pulumi_kubernetes.meta.v1 import ObjectMetaArgs


def generate_cluster_issuer(
    api_version: str = None,
    cluster_issuer_name: str = None,
    dependencies: list = None,
    secret_name: str = None,
) -> k8s_api_CustomResource:

    cluster_issuer = k8s_api_CustomResource(
        cluster_issuer_name,
        api_version=api_version,
        kind="ClusterIssuer",
        metadata=ObjectMetaArgs(name=cluster_issuer_name),
        spec={
            "ca": {
                "secretName": secret_name,
            },
        },
        opts=ResourceOptions(depends_on=dependencies),
    )

    return cluster_issuer
