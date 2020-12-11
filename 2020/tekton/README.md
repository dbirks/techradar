# Tekton

Tech Radar:

https://www.thoughtworks.com/radar/platforms?blipid=202010094

Homepage:

https://tekton.dev/

Katacoda playground:

https://tekton.dev/try/

## About

Several components:

https://tekton.dev/docs/overview/#what-are-the-components-of-tekton

## Demo

Modified from:

https://github.com/tektoncd/pipeline/blob/master/docs/tutorial.md

### Goal

Build a busybox image.

### Prereqs

- [kind](https://kind.sigs.k8s.io/)
- [helm](https://helm.sh/)
- [tekton-cli](https://github.com/tektoncd/cli)

Start up local Kubernetes cluster:

```
kind create cluster --config kind/config.yaml
```

Set up ingress-nginx, so we can view the dashboard from localhost:

```
kubectl create namespace ingress

helm repo add ingress-nginx https://kubernetes.github.io/ingress-nginx
helm repo update

helm install \
  nginx \
  --namespace ingress \
  --values ingress-nginx/values.yaml \
  ingress-nginx/ingress-nginx
```

Install Tekton Pipelines:

```
kubectl apply -f https://storage.googleapis.com/tekton-releases/pipeline/previous/v0.19.0/release.yaml
```

Apply the `PipelineResource` and `Task`:

```
kubectl apply -f build-busybox-image.yaml
```

View created Tekton resources:

```
tkn resource list
tkn task list
```

Start a TaskRun:

```
tkn task start build-busybox-image --inputresource=source-repo=busybox-git
```

View build logs:

```
tkn taskrun list
tkn taskrun logs build-busybox-image-run-v5wl7 -f
```

Install Tekton Dashboard:

```
kubectl apply -f https://github.com/tektoncd/dashboard/releases/download/v0.11.1/tekton-dashboard-release.yaml
kubectl apply -f tekton-dashboard/ingress.yaml
```

You'll now be able to see the dashboard at:

http://tekton-dashboard.127.0.0.1.xip.io

Clean up:

```
kind delete cluster
```
