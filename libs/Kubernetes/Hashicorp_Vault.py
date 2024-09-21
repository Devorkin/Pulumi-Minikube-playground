from pulumi import ResourceOptions
from pulumi_kubernetes.helm.v3 import (
    Release,
    ReleaseArgs,
    RepositoryOptsArgs,
)


def setup_vault(dependencies: list = None, namespace: str = None) -> Release:

    # Deploy Hashicorp Vault via Helm
    hashicorp_vault_chart = Release(
        "hashicorp-vault",
        ReleaseArgs(
            chart="vault",
            create_namespace=False,
            namespace=namespace,
            repository_opts=RepositoryOptsArgs(
                repo="https://helm.releases.hashicorp.com"
            ),
            values={
                "global": {"enabled": True, "tlsDisable": True},
                "server": {
                    "dev": {"devRootToken": "ThisIsMyT0k3n", "enabled": True},
                    "enterpriseLicense": {"secretName": None},
                    "ha": {"enabled": False},
                    "image": {"pullPolicy": "IfNotPresent"},
                    "ingress": {
                        "enabled": True,
                        "annotations": {
                            "cert-manager.io/cluster-issuer": "cert-manager-ca-issuer"
                        },
                        "hosts": [
                            {
                                "host": "vault.tests.net",
                                "path": "/",
                            }
                        ],
                        "ingressClassName": "nginx",
                        "path": "/",
                        "tls": [
                            {"hosts": ["vault.tests.net"], "secretName": "vault-tls"}
                        ],
                    },
                    "livenessProbe": {
                        "enabled": True,
                        "initialDelaySeconds": 60,
                        "path": "/v1/sys/health?standbyok=true",
                    },
                    "logFormat": "standard",
                    "logLevel": "info",
                    "priorityClassName": "medium-priority",
                    "readinessProbe": {
                        "enabled": True,
                        "path": "/v1/sys/health?standbyok=true&sealedcode=204&uninitcode=204",
                    },
                    "resources": {
                        "limits": {"memory": "1Gi"},
                        "requests": {"memory": "500Mi"},
                    },
                    "service": {
                        "enabled": True,
                        "port": 8200,
                        "targetport": 8200,
                        "type": "ClusterIP",
                    },
                    "standalone": {"enabled": False},
                },
                "ui": {"enabled": True},
            },
            timeout=120,
        ),
        opts=ResourceOptions(depends_on=dependencies),
    )
    return hashicorp_vault_chart
