# Known Limitations

This project is intentionally scoped as an MVP. These are known gaps.

## Data and modeling

- The Kaggle-to-business feature mapping is an approximation, not a domain-perfect transformation.
- No drift detection is implemented yet.
- No scheduled retraining pipeline is automated yet.

## Serving and storage

- Dashboard history is in-memory and resets on restart.
- No persistent transaction store is configured yet.
- No authentication/authorization layer is enabled.

## Streaming

- Local Kafka flow is implemented, but cloud-managed streaming (MSK/Kinesis/PubSub) is not wired yet.
- Consumer retry/backoff and dead-letter handling are basic.

## MLOps and observability

- MLflow integration is present in dependencies but experiment tracking is not fully operationalized.
- Metrics are exposed, but alert policies and SLO dashboards are not finalized.

## Deployment

- ECS Fargate path is implemented for the API service first.
- Full cloud deployment of producer/consumer streaming services is not completed in Terraform.

## Security and production hardening

- Secrets management uses environment variables in the current setup.
- No WAF/rate-limiting policy is configured yet.
- TLS/domain setup is not included in this MVP deployment path.

