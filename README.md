# Real-Time Fraud Detection System

Production-style machine learning project that scores payment transactions in near real time and demonstrates end-to-end MLOps, cloud deployment, and DevOps practices.

## Why this project

This project is designed to help you showcase:

- Machine learning for fraud detection
- Real-time inference with an API service
- Event-driven architecture
- Containerization and CI/CD
- Cloud deployment and observability
- Infrastructure as code

## Project notes

- Engineering tradeoffs: [DECISIONS.md](/C:/Users/umaab/Documents/Codex/2026-04-20-i-want-to-build-ml-project/DECISIONS.md)
- Current known gaps: [KNOWN_LIMITATIONS.md](/C:/Users/umaab/Documents/Codex/2026-04-20-i-want-to-build-ml-project/KNOWN_LIMITATIONS.md)

## Target architecture

```text
Transaction Producer -> Kafka -> Feature/Scoring Service -> Prediction API
                                                |
                                                v
                                           MLflow Registry
                                                |
                                                v
                                          Model Artifacts

Prediction API -> Metrics -> Prometheus -> Grafana
Prediction Logs -> Object Storage / Warehouse
CI/CD -> GitHub Actions -> Docker Registry -> Kubernetes
IaC -> Terraform
```

## Repository structure

```text
app/
  api/              FastAPI inference service
  core/             config and shared utilities
  schemas/          request/response schemas
training/
  pipelines/        training and evaluation pipeline
  features/         feature engineering code
streaming/
  producer/         transaction simulator
infra/
  docker/           local container setup
  terraform/        cloud infrastructure skeleton
.github/workflows/  CI/CD pipelines
docs/               architecture and roadmap
```

## Recommended stack

- Python
- FastAPI
- scikit-learn or XGBoost
- Kafka
- Docker
- Kubernetes
- MLflow
- Prometheus + Grafana
- GitHub Actions
- Terraform
- AWS EKS or GCP GKE

## Suggested delivery phases

1. Build a baseline fraud classifier on historical transactions.
2. Expose the model through a FastAPI `/predict` endpoint.
3. Simulate incoming transactions with Kafka.
4. Containerize services with Docker Compose.
5. Add experiment tracking with MLflow.
6. Add CI/CD with GitHub Actions.
7. Provision cloud infrastructure with Terraform.
8. Deploy to Kubernetes and add monitoring.

## Implementation status

Completed in this repo:

- baseline fraud model training and evaluation
- FastAPI prediction API and dashboard website
- streaming producer and consumer flow
- Docker Compose local stack
- GitHub Actions CI/CD scaffolding
- Terraform ECS deployment scaffolding
- Kubernetes manifests for API and worker deployments
- MLflow training run logging and model metadata output
- Prometheus and Grafana local monitoring configuration
- persistent JSONL prediction logging for scored transactions
- S3-compatible prediction log export utility

Still remaining for the full production target:

- MLflow model registry promotion workflow
- live prediction log export scheduling to S3 or a warehouse
- Kubernetes cluster rollout with real registry images and Kafka
- live cloud deployment execution in your AWS account
- auth, analyst workflows, and deeper production hardening

## Quick start

1. Create a virtual environment.
2. Install dependencies:

```bash
pip install -r requirements.txt
```

3. Run the API locally:

```bash
uvicorn app.api.main:app --reload
```

4. Open the API docs at `http://127.0.0.1:8765/docs`

## Fresh clone setup (recommended)

For anyone cloning this repo, the smoothest path is:

```powershell
.\scripts\bootstrap.ps1
.\scripts\run-local.ps1
```

This handles:

- virtual environment setup
- dependency install
- sample data generation
- data preprocessing
- baseline model training
- app startup

Note: `run-local.ps1` tries `8765` first, then auto-selects a free local port from `8000`, `8001`, `8002`, or `8080` if needed.

## Train on a real dataset

The project now supports two CSV shapes:

- Business fraud schema:
  `transaction_amount, customer_age, merchant_risk_score, transaction_velocity_1h, card_present, international, is_fraud`
- Kaggle credit card fraud schema:
  `Time, V1..V28, Amount, Class`

Place your raw file at `data/raw/creditcard.csv` and run:

```bash
python -m training.pipelines.prepare_real_data
python -m training.pipelines.train
```

This writes:

- processed training data to `data/processed/transactions_processed.csv`
- trained model to `artifacts/model.joblib`
- evaluation metrics to `artifacts/metrics.txt`
- model metadata to `artifacts/model_metadata.json`
- MLflow runs to `mlruns/`

Note: when using the Kaggle `creditcard.csv` dataset, the preprocessing step maps the original anonymized features into the app's business-style feature schema so the trained model remains compatible with the live dashboard and API.

## MLflow tracking

Every training run now logs parameters, metrics, and the serialized scikit-learn model to MLflow.

After training, you can inspect local runs with:

```bash
mlflow ui --backend-store-uri file:./mlruns
```

Then open `http://127.0.0.1:5000/`

## Prediction log export

Prediction events are written locally to `artifacts/prediction_log.jsonl`. The repo now includes an S3-compatible export utility:

```bash
python scripts/export_prediction_logs.py
```

Set these environment variables first:

- `PREDICTION_EXPORT_BUCKET`
- `PREDICTION_EXPORT_PREFIX` (optional, defaults to `prediction-logs`)
- `AWS_REGION` (optional)
- `S3_ENDPOINT_URL` (optional, useful for S3-compatible object stores)

The exporter uploads the JSONL file as an object key partitioned by date.

## Run as a website

Start the app:

```bash
uvicorn app.api.main:app --reload
```

Then open `http://127.0.0.1:8765/`

## Run tests

```bash
pytest
```

Current coverage includes:

- API health, prediction, and stream ingest behavior
- dashboard history/stats updates
- persistent prediction log writes
- real-data preprocessing for both supported dataset schemas

## Live streaming modes

### Local demo mode

This sends a generated transaction straight into the app so the dashboard updates without Kafka:

```bash
python -m streaming.simulate_live_feed
```

### Kafka mode

1. Start Kafka with Docker Compose.
2. Start the API.
3. Start the consumer:

```bash
python -m streaming.consumer.consume_and_score
```

4. Start the producer:

```bash
python -m streaming.producer.simulate_transactions
```

In Kafka mode, events flow as:

`producer -> Kafka topic -> consumer -> FastAPI ingest endpoint -> dashboard`

## Docker Compose stack

Run the full local stack with:

```bash
docker compose -f infra/docker/docker-compose.yml up --build
```

This starts:

- `api` on `http://127.0.0.1:8765/`
- `zookeeper`
- `kafka`
- `consumer` for stream ingestion
- `producer` for continuous transaction generation
- `prometheus` on `http://127.0.0.1:9090/`
- `grafana` on `http://127.0.0.1:3000/` with `admin/admin`

The full container flow becomes:

`producer container -> Kafka -> consumer container -> FastAPI -> dashboard`

The monitoring flow becomes:

`FastAPI /metrics -> Prometheus -> Grafana dashboard`

If you want to stop the stack:

```bash
docker compose -f infra/docker/docker-compose.yml down
```

## AWS deployment

The project now includes an `AWS ECS Fargate` deployment path with Terraform.

Infrastructure files:

- [infra/terraform/main.tf](/C:/Users/umaab/Documents/Codex/2026-04-20-i-want-to-build-ml-project/infra/terraform/main.tf:1)
- [infra/terraform/variables.tf](/C:/Users/umaab/Documents/Codex/2026-04-20-i-want-to-build-ml-project/infra/terraform/variables.tf:1)
- [infra/terraform/outputs.tf](/C:/Users/umaab/Documents/Codex/2026-04-20-i-want-to-build-ml-project/infra/terraform/outputs.tf:1)
- [infra/terraform/terraform.tfvars.example](/C:/Users/umaab/Documents/Codex/2026-04-20-i-want-to-build-ml-project/infra/terraform/terraform.tfvars.example:1)

Full deployment guide:

- [docs/aws-deployment.md](/C:/Users/umaab/Documents/Codex/2026-04-20-i-want-to-build-ml-project/docs/aws-deployment.md:1)

CI/CD workflows:

- [.github/workflows/ci.yml](/C:/Users/umaab/Documents/Codex/2026-04-20-i-want-to-build-ml-project/.github/workflows/ci.yml:1)
- [.github/workflows/deploy-aws.yml](/C:/Users/umaab/Documents/Codex/2026-04-20-i-want-to-build-ml-project/.github/workflows/deploy-aws.yml:1)

## Kubernetes deployment

The repo now includes Kubernetes manifests for the API, producer, and consumer services.

Files:

- [infra/kubernetes/kustomization.yaml](/C:/Users/umaab/Documents/Codex/2026-04-20-i-want-to-build-ml-project/infra/kubernetes/kustomization.yaml:1)
- [infra/kubernetes/api-deployment.yaml](/C:/Users/umaab/Documents/Codex/2026-04-20-i-want-to-build-ml-project/infra/kubernetes/api-deployment.yaml:1)
- [infra/kubernetes/api-service.yaml](/C:/Users/umaab/Documents/Codex/2026-04-20-i-want-to-build-ml-project/infra/kubernetes/api-service.yaml:1)
- [infra/kubernetes/consumer-deployment.yaml](/C:/Users/umaab/Documents/Codex/2026-04-20-i-want-to-build-ml-project/infra/kubernetes/consumer-deployment.yaml:1)
- [infra/kubernetes/producer-deployment.yaml](/C:/Users/umaab/Documents/Codex/2026-04-20-i-want-to-build-ml-project/infra/kubernetes/producer-deployment.yaml:1)
- [docs/kubernetes-deployment.md](/C:/Users/umaab/Documents/Codex/2026-04-20-i-want-to-build-ml-project/docs/kubernetes-deployment.md:1)

Apply with:

```bash
kubectl apply -k infra/kubernetes
```

## Project outcome

This repo now provides:

- a trained fraud model
- a low-latency prediction service
- a Kafka-based event flow
- reproducible training runs
- local MLflow experiment tracking
- local Prometheus and Grafana monitoring
- persistent prediction logs
- S3-compatible prediction log export
- cloud deployment manifests
- Kubernetes deployment manifests
- CI/CD scaffolding

## Next build steps

The strongest remaining steps are:

- connect prediction logs to S3 or a warehouse sink
- schedule automated prediction log export jobs
- promote models through MLflow registry stages
- deploy the Kubernetes manifests to a real cluster with registry-backed images
- finish live AWS rollout with Terraform apply, ECR push, and ECS service launch
- add authentication and analyst case-management actions
