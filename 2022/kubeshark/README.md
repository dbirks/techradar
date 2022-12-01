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
helm install ingress-nginx ingress-nginx/ingress-nginx --values ingress-nginx/values.yaml
```

Deploy wordpress with:

```
helm repo add bitnami https://charts.bitnami.com/bitnami
helm install wordpress bitnami/wordpress
helm install wordpress bitnami/wordpress --values wordpress/values.yaml
```

## Kubeshark demo

kubeshark deploy

ks-hub
ks-front



kubeshark deploy -A

intercepts traffic from all pods in all namespaces

ks-worker-daemon-set-l59nb




todo:
- ingress-nginx
- wordpress
- 



## Alternatives

ksniff

Cillium + Pixie ?

LinkerD





## Cons

repo in flux
no brew yet
no helm chart?

