# Architecture Blueprint

## Problem statement

Detect suspicious payment transactions in near real time and expose a production-oriented ML service that can be monitored, deployed, and retrained.

## Core components

### 1. Training pipeline

- Input: historical transaction dataset
- Output: trained fraud model artifact
- Tooling: pandas, scikit-learn, MLflow

### 2. Inference API

- Receives transaction features
- Loads the latest approved model artifact
- Returns fraud score and label
- Exposes health and metrics endpoints

### 3. Streaming layer

- Kafka receives live transaction events
- Producer simulates transaction flow during development
- A future consumer can enrich events and call the model service

### 4. Observability

- Prometheus scrapes API metrics
- Grafana visualizes latency, traffic, and fraud rates
- Logs can later be shipped to cloud logging or a data warehouse

### 5. Cloud and DevOps

- Docker packages services
- GitHub Actions runs CI
- Terraform provisions cloud resources
- Kubernetes runs scalable workloads

## Recommended cloud deployment

### AWS option

- `S3` for datasets and model artifacts
- `ECR` for Docker images
- `EKS` for container orchestration
- `MSK` or self-managed Kafka for streaming
- `CloudWatch` for logs
- `IAM` for service access

### GCP option

- `GCS` for datasets and model artifacts
- `Artifact Registry` for images
- `GKE` for orchestration
- `Pub/Sub` or Kafka-compatible setup for streaming
- `Cloud Logging` for logs

## MVP data flow

1. Training script reads CSV data.
2. Model artifact is written to `artifacts/model.joblib`.
3. API service loads the artifact on startup.
4. Producer sends transactions to Kafka.
5. API scores incoming transactions through `/predict`.
6. Prometheus scrapes `/metrics`.

## Stretch goals

- model registry promotion flow
- drift detection
- feature store integration
- batch retraining automation
- canary deployment
- alerting on latency and fraud-rate spikes
