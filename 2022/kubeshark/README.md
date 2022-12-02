# Kubeshark (formally known as Mizu)

Tech radar: https://www.thoughtworks.com/radar/tools?blipid=202210007

Github: https://github.com/kubeshark/kubeshark

Homepage: https://kubeshark.co/

## Prereqs

Install the kubeshark binary
- either with their install script: https://docs.kubeshark.co/en/install
- or from the Github Releases (recommended): https://github.com/kubeshark/kubeshark/releases
- or by cloning their repo and running `make build`

Make sure you have these installed too:
- docker: https://docs.docker.com/get-docker/
- kind: https://kind.sigs.k8s.io/docs/user/quick-start/
- kubectl: https://kubernetes.io/docs/tasks/tools/
- helm: https://helm.sh/docs/intro/install/

Make sure you're in the right directory:
```
cd 2022/kubeshark
```

And then start up a Kubernetes cluster with:

```
kind create cluster --config kind/config.yaml
```

## Deploy some apps

Deploy ingress-nginx with:

```
helm repo add ingress-nginx https://kubernetes.github.io/ingress-nginx
helm install ingress-nginx ingress-nginx/ingress-nginx --values ingress-nginx/values.yaml --namespace kube-system
```

Deploy wordpress with:

```
helm repo add bitnami https://charts.bitnami.com/bitnami
helm install wordpress bitnami/wordpress --values wordpress/values.yaml
```

The end of the output from helm will give you a command to run to grab the default user's password.

You'll then be able to reach WordPress at: http://wordpress.127.0.0.1.nip.io/

## Kubeshark demo

Targeting just one namespace:

```
kubeshark deploy
```

Launches the pods:
- `ks-hub`
- `ks-front`

Deploy DaemonSet to all nodes, to intercept traffic from all pods in all namespaces:

```
kubeshark deploy -A
```

Launches an additional Pod from the DaemonSet, named like:
- `ks-worker-daemon-set-l59nb`

## Alternatives

ksniff

Or maybe something like a service mesh?
- LinkerD: https://linkerd.io/
- Istio: https://istio.io/
- Cilium + Hubble: https://github.com/cilium/hubble
- Pixie: https://px.dev/

LinkerD

## Cons

- repo and docs aren't complete (because of recent name change?)
- no homebrew install option yet
  - upstream issue: https://github.com/kubeshark/kubeshark/issues/1229
- no helm chart?
