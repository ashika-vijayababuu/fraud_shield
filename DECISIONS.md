# Engineering Decisions

This file explains why major choices were made in this project.

## 1) First cloud target: ECS Fargate (not EKS)

I chose ECS Fargate for the first deployment because it is faster to ship and easier to debug for a single-service ML API.
EKS is a valid future target, but it adds cluster and operations overhead too early in the project.

## 2) Keep API schema stable while supporting Kaggle data

The UI and API use business-style fields (`transaction_amount`, `merchant_risk_score`, etc.).
The public Kaggle credit-card dataset uses anonymized features (`V1..V28`), so preprocessing maps Kaggle features into the app schema.
This keeps serving interfaces stable while still letting us train with real public data.

## 3) Start with in-memory event history

Recent predictions are stored in memory for the dashboard.
This is enough for a local MVP and avoids introducing a database before API/data contracts are stable.
A database is planned once alert workflows are finalized.

## 4) Add streaming as an integration path, not a hard dependency

There are two ingestion paths:
- Manual prediction (`/predict`) for interactive testing
- Stream ingest (`/api/ingest-transaction`) for producer/consumer flow

This lets the app be usable without Kafka while still demonstrating real-time architecture.

## 5) Keep initial model simple and reproducible

A tree-based baseline model was chosen for reliability and quick iteration.
The project currently emphasizes system integration and deployment discipline before model complexity.

## 6) Infrastructure staged in two applies

Terraform creates infrastructure first, then app service deployment is enabled.
This prevents first-run failures when ECS references an image that has not yet been pushed to ECR.

