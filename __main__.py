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


##### Playground code to setup Graylog #####
from pulumi import ResourceOptions
from pulumi_kubernetes.core.v1 import Namespace
from pulumi_kubernetes.helm.v3 import (
    Release,
    ReleaseArgs,
    RepositoryOptsArgs,
)

# Setup OpenSearch
opensearch_namespace = Namespace(
    "opensearch",
    metadata={"name": "opensearch"},
)

opensearch_chart = Release(
    "opensearch",
    ReleaseArgs(
        chart="opensearch",
        create_namespace=False,
        namespace=opensearch_namespace.metadata["name"],
        repository_opts=RepositoryOptsArgs(
            repo="https://opensearch-project.github.io/helm-charts"
        ),
        values={
            "config": {
                "opensearch.yml": """
action.auto_create_index: true
bootstrap.memory_lock: true
network.host: 0.0.0.0
plugins.security.disabled: true
                """,
            },
            "clusterName": "opensearch-cluster",
            "extraEnvs": [
                {
                    "name": "DISABLE_INSTALL_DEMO_CONFIG",
                    "value": "true",
                },
                {
                    "name": "DISABLE_SECURITY_PLUGIN",
                    "value": "true",
                },
                {
                    "name": "OPENSEARCH_INITIAL_ADMIN_PASSWORD",
                    "value": "Vto0kvhu,!Cl ntuvc"
                },
            ],
            # The service that non master groups will try to connect to when joining the cluster
            # This should be set to clusterName + "-" + nodeGroup for your master group
            "masterService": "opensearch-cluster-master",
            "nodeGroup": "master",
            "persistence": {
                "enabled": False,
            },
            "service": {
                "type": "ClusterIP",
            },
            "replicas": 1,
            "roles": ["master", "ingest", "data", "remote_cluster_client"],
        },
    ),
    opts=ResourceOptions(depends_on=[opensearch_namespace]),
)

# Deploy OpenSearch Dashboards
opensearch_dashboards_chart = Release(
    "opensearch-dashboards",
    ReleaseArgs(
        chart="opensearch-dashboards",
        namespace=opensearch_namespace.metadata["name"],
        repository_opts=RepositoryOptsArgs(
            repo="http://opensearch-project.github.io/helm-charts"
        ),
        values={
            "extraEnvs": [
                {
                    "name": "DISABLE_SECURITY_DASHBOARDS_PLUGIN",
                    "value": "true"
                },
                {
                    "name": "OPENSEARCH_HOSTS",
                    "value": "http://opensearch-cluster-master-headless.opensearch.svc:9200"
                },
                {
                    "name": "SERVER_HOST",
                    "value": "0.0.0.0"
                }
            ],
            "persistence": {
                "enabled": False,
            },
            "service": {
                "type": "ClusterIP",
            },
            "livenessProbe": {
                "tcpSocket": {
                    "port": 5601,
                },
                "periodSeconds": 20,
                "timeoutSeconds": 5,
                "failureThreshold": 10,
                "successThreshold": 1,
                "initialDelaySeconds": 10,
            },
            "startupProbe": {
                "tcpSocket": {
                    "port": 5601
                },
                "periodSeconds": 10,
                "timeoutSeconds": 5,
                "failureThreshold": 20,
                "successThreshold": 1,
                "initialDelaySeconds": 10,
            },
            "readinessProbe": {
                "tcpSocket": {
                    "port": 5601,
                },
                "periodSeconds": 20,
                "timeoutSeconds": 5,
                "failureThreshold": 10,
                "successThreshold": 1,
                "initialDelaySeconds": 10,
            },
        },
    ),
    opts=ResourceOptions(depends_on=[opensearch_chart]),
)

# Deploy Fluent Bit
fluent_bit_namespace = Namespace(
    "fluent_bit",
    metadata={"name": "fluent-bit"},
)

fluent_bit_chart = Release(
    "fluent-bit",
    ReleaseArgs(
        chart="fluent-bit",
        namespace=fluent_bit_namespace.metadata["name"],
        repository_opts=RepositoryOptsArgs(
            repo="https://fluent.github.io/helm-charts"
        ),
        values = {
            "kind": "DaemonSet",
            "image": {
                "repository": "cr.fluentbit.io/fluent/fluent-bit",
                "pullPolicy": "IfNotPresent",
            },
            "testFramework": {
                "enabled": True,
                "image": {
                    "repository": "busybox",
                    "pullPolicy": "Always",
                    "tag": "latest",
                }
            },
            "serviceAccount": {
                "create": True,
                "name": "fluent-bit-sa",
            },
            "rbac": {
                "create": True,
                "nodeAccess": True,
                "eventsAccess": True,
            },
            "hostNetwork": False,
            "dnsPolicy": "ClusterFirst",
            "service": {
                "type": "ClusterIP",
                "port": 2020,
            },
            "livenessProbe": {
                "httpGet": {
                    "path": "/",
                    "port": "http",
                }
            },
            "readinessProbe": {
                "httpGet": {
                    "path": "/api/v1/health",
                    "port": "http",
                }
            },
            "flush": 1,
            "metricsPort": 2020,
            "config": {
                "service": "[SERVICE]\n    Daemon Off\n    Flush 1\n    Log_Level info\n    Parsers_File /fluent-bit/etc/parsers.conf\n    Parsers_File /fluent-bit/etc/conf/custom_parsers.conf\n    HTTP_Server On\n    HTTP_Listen 0.0.0.0\n    HTTP_Port 2020\n    Health_Check On",
                "inputs": "[INPUT]\n    Name kubernetes_events\n    db /tmp/k8s_events.db\n    Tag kube-events\n\n[INPUT]\n    Name tail\n    DB /var/log/flb_kube.db\n    Mem_Buf_Limit 50MB\n    Path /var/log/containers/*.log\n    Skip_Long_Lines On\n    Tag kubernetes.*\n    multiline.parser cri, docker\n\n[INPUT]\n    Name tail\n    DB /var/log/flb_node.db\n    Mem_Buf_Limit 50MB\n    Path /var/log/messages\n    Parser syslog\n    Skip_Long_Lines On\n    Tag node.*",
                "outputs": "[OUTPUT]\n    Name opensearch\n    Host opensearch-cluster-master.opensearch.svc\n    Index fluent-bit\n    Logstash_format Off\n    Match *\   n    Port 9200\n    Type _doc\n    Suppress_Type_Name On\n\n",
                "customParsers": "[PARSER]\n    Name docker\n    Format json\n    Time_key time\n    Time_format %Y-%m-%dT%H:%M:%S.%L\n    Time_keep On\n\n[PARSER]\n    Name syslog\n    Format regex\n    Regex ^(?<time>[^ ]+ [^ ]+) (?<message>.*)$\n    Time_key time\n    Time_format %Y-%m-%dT%H:%M:%S.%L"
            },
        },
    ),
    opts=ResourceOptions(depends_on=[fluent_bit_namespace]),
)
#####
