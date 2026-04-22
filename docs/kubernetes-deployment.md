# Kubernetes deployment

This repo now includes a first-pass Kubernetes deployment path under [infra/kubernetes](C:/Users/umaab/Documents/Codex/2026-04-20-i-want-to-build-ml-project/infra/kubernetes).

## What is included

- namespace manifest
- shared ConfigMap for API and worker settings
- API Deployment and Service
- API Ingress example
- consumer Deployment
- producer Deployment
- Kustomize entrypoint

## Assumptions

- the API image is pushed to a registry such as ECR
- the worker image is pushed to a registry such as ECR
- Kafka is available separately, for example through MSK, Strimzi, or another managed Kafka service
- your cluster has an ingress controller such as NGINX

## Files

- [infra/kubernetes/kustomization.yaml](C:/Users/umaab/Documents/Codex/2026-04-20-i-want-to-build-ml-project/infra/kubernetes/kustomization.yaml)
- [infra/kubernetes/configmap.yaml](C:/Users/umaab/Documents/Codex/2026-04-20-i-want-to-build-ml-project/infra/kubernetes/configmap.yaml)
- [infra/kubernetes/api-deployment.yaml](C:/Users/umaab/Documents/Codex/2026-04-20-i-want-to-build-ml-project/infra/kubernetes/api-deployment.yaml)
- [infra/kubernetes/api-service.yaml](C:/Users/umaab/Documents/Codex/2026-04-20-i-want-to-build-ml-project/infra/kubernetes/api-service.yaml)
- [infra/kubernetes/api-ingress.yaml](C:/Users/umaab/Documents/Codex/2026-04-20-i-want-to-build-ml-project/infra/kubernetes/api-ingress.yaml)
- [infra/kubernetes/consumer-deployment.yaml](C:/Users/umaab/Documents/Codex/2026-04-20-i-want-to-build-ml-project/infra/kubernetes/consumer-deployment.yaml)
- [infra/kubernetes/producer-deployment.yaml](C:/Users/umaab/Documents/Codex/2026-04-20-i-want-to-build-ml-project/infra/kubernetes/producer-deployment.yaml)

## Before applying

Update these placeholders first:

- replace `your-ecr-repository/fraudshield-api:latest`
- replace `your-ecr-repository/fraudshield-worker:latest`
- set `KAFKA_BOOTSTRAP_SERVERS` in [infra/kubernetes/configmap.yaml](C:/Users/umaab/Documents/Codex/2026-04-20-i-want-to-build-ml-project/infra/kubernetes/configmap.yaml)
- change the ingress host from `fraudshield.local` to your real domain

## Apply

```bash
kubectl apply -k infra/kubernetes
```

## Verify

```bash
kubectl get pods -n fraudshield
kubectl get svc -n fraudshield
kubectl get ingress -n fraudshield
```

## Next production hardening steps

- move non-secret config to `ConfigMap` and secrets to `Secret`
- add HorizontalPodAutoscaler
- add network policies
- add persistent storage or remote log export for prediction logs
- point the manifests to your registry and cluster-specific observability stack
