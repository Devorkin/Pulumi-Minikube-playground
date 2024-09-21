# Pulumi-Minikube-playground

This is a Pulumi playground project - based on Minikube platform

## Prerequisites

1. [Install Pulumi](https://www.pulumi.com/docs/reference/install/)
2. [Install Minikube](https://minikube.sigs.k8s.io/docs/start/?arch=%2Fmacos%2Farm64%2Fstable%2Fbinary+download)
3. [Configure Pulumi for Python](https://www.pulumi.com/docs/reference/python/)

<br /><br /><br />

## Deploying and running the Pulumi project

1. Set Local backend

    ```bash
    pulumi login --local
    ```

2. Create a new stack:

    ```bash
    pulumi stack init playground
    ```

3. Start Minikube - this playground was developed over Kubernets version 1.30

    ```bash
    minikube start --kubernetes-version=1.30
    ```

4. Install all needed Pulumi packages

    ```bash
    pulumi install
    ```

5. Start the Pulumi project

    ```bash
    pulumi up
    ```

6. Verify that the project ran well

    ```bash
    kubectl get all
    ```

7. Access the cluster Ingress port via Minikube service, run the below command to enable Minikube service on a specific namespaced Service

    ```bash
    minikube service -n ingress-nginx $(kubectl -n ingress-nginx get svc --no-headers=true | grep -v admission | tr -s ' ' | cut -d ' ' -f1)
    ```

8. From the retrieved STDOUT, grab the bottom port on the list, you should use this to access the Minikube cluster

9. Add the FQDNs `grafana.tests.net`, `prometheus.tests.net`, and `vault.tests.net` to your OS hosts file

    ```bash
    sudo echo '127.0.0.1     grafana.tests.net prometheus.tests.net vault.tests.net' >> /etc/hosts
    ```

10. Now you should be able to access these services via your favorite browser -- `https://prometheus.tests.net:55762` for example.

<br /><br /><br />

## Destroy \ reset the environment

1. Teardown Pulumi

    ```bash
    pulumi down --yes
    ```

2. Teardown Minikube

    ```bash
    minikube delete
    ```

<br /><br /><br />

## Project services details

### Hashicorp Vault

* Default token: 'ThisIsMyT0k3n'
