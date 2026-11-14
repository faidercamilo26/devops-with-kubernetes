# Knative Serving (exercise 5.6)

Cluster without Traefik (Kubernetes 1.34.1):

```
k3d cluster create --port 8082:30080@agent:0 -p 8081:80@loadbalancer --agents 2 --k3s-arg "--disable=traefik@server:0" --image rancher/k3s:v1.34.1-k3s1
```

Install Knative Serving 1.23.0 with Kourier and Magic DNS (sslip.io):

```
S=https://github.com/knative/serving/releases/download/knative-v1.23.0
K=https://github.com/knative-extensions/net-kourier/releases/download/knative-v1.23.0
kubectl apply -f $S/serving-crds.yaml
kubectl apply -f $S/serving-core.yaml
kubectl apply -f $K/kourier.yaml
kubectl patch configmap/config-network -n knative-serving --type merge -p '{"data":{"ingress-class":"kourier.ingress.networking.knative.dev"}}'
kubectl apply -f $S/serving-default-domain.yaml
```

## The crash loop

With the latest release (1.24.0) the `webhook`, `controller` and `net-kourier-controller` pods went into `CrashLoopBackOff`.
`kubectl logs -n knative-serving deploy/webhook` shows the cause:

```
Version check failed ... kubernetes version "1.34.1+k3s1" is not compatible, need at least "1.35.0-0"
```

Knative 1.24.0 needs Kubernetes 1.35 and the cluster is 1.34.1, so the fix is to install Knative 1.23.0.

## Examples

- Deploying a Knative Service: `kubectl apply -f hello.yaml`
- Traffic splitting (50/50 between revisions `hello-v1` and `hello-v2`): `kubectl apply -f traffic-splitting.yaml`
- Autoscaling (target concurrency 10, max 5 pods): `kubectl apply -f autoscale.yaml`

```
curl -H "Host: hello.default.172.18.0.3.sslip.io" http://localhost:8081
```
