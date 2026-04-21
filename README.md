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

4. Open the API docs at `http://127.0.0.1:8000/docs`

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

Note: when using the Kaggle `creditcard.csv` dataset, the preprocessing step maps the original anonymized features into the app's business-style feature schema so the trained model remains compatible with the live dashboard and API.

## Run as a website

Start the app:

```bash
uvicorn app.api.main:app --reload
```

Then open `http://127.0.0.1:8000/`

## Run tests

```bash
pytest
```

Current coverage includes:

- API health, prediction, and stream ingest behavior
- dashboard history/stats updates
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

- `api` on `http://127.0.0.1:8000/`
- `zookeeper`
- `kafka`
- `consumer` for stream ingestion
- `producer` for continuous transaction generation

The full container flow becomes:

`producer container -> Kafka -> consumer container -> FastAPI -> dashboard`

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

## Project outcome

By the end, this repo can become a portfolio-grade system with:

- a trained fraud model
- a low-latency prediction service
- a Kafka-based event flow
- reproducible training runs
- cloud deployment manifests
- CI/CD and monitoring

## Next build steps

Start with the docs in [docs/architecture.md](/C:/Users/umaab/Documents/Codex/2026-04-20-i-want-to-build-ml-project/docs/architecture.md:1) and [docs/roadmap.md](/C:/Users/umaab/Documents/Codex/2026-04-20-i-want-to-build-ml-project/docs/roadmap.md:1), then implement the baseline model in [training/pipelines/train.py](/C:/Users/umaab/Documents/Codex/2026-04-20-i-want-to-build-ml-project/training/pipelines/train.py:1).
