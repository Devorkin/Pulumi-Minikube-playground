from pulumi import ResourceOptions
from pulumi_kubernetes.helm.v3 import (
    Release,
    ReleaseArgs,
    RepositoryOptsArgs,
)


def setup_prometheus_stack(dependencies: list = None, namespace: str = None) -> Release:

    # Deploy Prometheus via Helm
    prometheus_community_chart = Release(
        "prometheus",
        ReleaseArgs(
            chart="kube-prometheus-stack",
            create_namespace=False,
            namespace=namespace,
            repository_opts=RepositoryOptsArgs(
                repo="https://prometheus-community.github.io/helm-charts"
            ),
            values={
                "grafana": {
                    "adminPassword": "admin",
                    "ingress": {
                        "enabled": "true",
                        "annotations": {
                            "cert-manager.io/cluster-issuer": "cert-manager-ca-issuer"
                        },
                        "hosts": ["grafana.tests.net"],
                        "ingressClassName": "nginx",
                        "path": "/",
                        "tls": [
                            {
                                "hosts": ["grafana.tests.net"],
                                "secretName": "grafana-tls",
                            },
                        ],
                    },
                },
                "persistence": {
                    "accessModes": ["ReadWriteOnce"],
                    "enabled": "true",
                    "finalizers": ["kubernetes.io/pvc-protection"],
                    "size": "4Gi",
                    "type": "pvc",
                },
                "prometheus": {
                    "ingress": {
                        "enabled": "true",
                        "annotations": {
                            "cert-manager.io/cluster-issuer": "cert-manager-ca-issuer"
                        },
                        "hosts": ["prometheus.tests.net"],
                        "ingressClassName": "nginx",
                        "path": "/",
                        "tls": [
                            {
                                "hosts": ["prometheus.tests.net"],
                                "secretName": "prometheus-tls",
                            },
                        ],
                    },
                    "prometheusSpec": {
                        "retention": "31d",
                        "storageSpec": {
                            "volumeClaimTemplate": {
                                "spec": {
                                    "accessModes": ["ReadWriteOnce"],
                                    "resources": {
                                        "requests": {
                                            "storage": "10Gi",
                                        },
                                    },
                                },
                            },
                        },
                    },
                },
                "thanosRuler": {
                    "thanosRulerSpec": {
                        "storage": {
                            "volumeClaimTemplate": {
                                "spec": {
                                    "accessModes": ["ReadWriteOnce"],
                                    "resources": {
                                        "requests": {
                                            "storage": "10Gi",
                                        },
                                    },
                                },
                            },
                        },
                    },
                },
            },
            timeout=120,
        ),
        opts=ResourceOptions(depends_on=dependencies),
    )

    return prometheus_community_chart
