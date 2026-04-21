# 30-Day Roadmap

## Week 1: Baseline ML

- Choose a fraud dataset from Kaggle.
- Standardize feature columns used by the API.
- Train a first model and save `artifacts/model.joblib`.
- Record baseline precision, recall, F1, and ROC-AUC.

## Week 2: Serving and Streaming

- Finish the FastAPI prediction service.
- Add request validation and response schemas.
- Start Kafka locally with Docker Compose.
- Run the transaction simulator.

## Week 3: MLOps and DevOps

- Add MLflow experiment tracking.
- Add tests for feature selection and prediction endpoint.
- Extend CI to run tests on pull requests.
- Build and push Docker images through GitHub Actions.

## Week 4: Cloud Deployment

- Add Terraform resources for your chosen cloud.
- Deploy the API to Kubernetes.
- Add Prometheus and Grafana dashboards.
- Prepare architecture diagram and portfolio README screenshots.

## Resume bullets this project can support

- Built a real-time fraud detection API serving ML predictions with FastAPI and Docker.
- Designed a streaming transaction pipeline using Kafka for near real-time scoring.
- Automated CI/CD and infrastructure provisioning with GitHub Actions and Terraform.
- Instrumented model-serving metrics for observability with Prometheus and Grafana.
