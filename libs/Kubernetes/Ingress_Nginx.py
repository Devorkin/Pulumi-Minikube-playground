from pulumi import ResourceOptions
from pulumi_kubernetes.helm.v3 import (
    Release,
    ReleaseArgs,
    RepositoryOptsArgs,
)


def setup_ingress_nginx(dependencies: list = None, namespace: str = None) -> Release:

    # Deploy Nginx Ingress Controller via Helm
    ingress_nginx_chart = Release(
        "ingress-nginx",
        ReleaseArgs(
            chart="ingress-nginx",
            create_namespace=False,
            namespace=namespace,
            repository_opts=RepositoryOptsArgs(
                repo="https://kubernetes.github.io/ingress-nginx"
            ),
            values={
                "controller": {
                    "service": {
                        "type": "NodePort",
                        "nodePorts": {"http": 30208, "https": 30209},
                    },
                },
            },
            timeout=120,
        ),
        opts=ResourceOptions(depends_on=dependencies),
    )

    return ingress_nginx_chart
