# Dataset Guide

## Supported input formats

### 1. Business fraud schema

Use this if you already have a dataset shaped like the app:

- `transaction_amount`
- `customer_age`
- `merchant_risk_score`
- `transaction_velocity_1h`
- `card_present`
- `international`
- `is_fraud`

### 2. Kaggle credit card fraud schema

Use the common Kaggle file with:

- `Time`
- `V1` to `V28`
- `Amount`
- `Class`

## Preprocessing behavior

If the raw file matches the business schema, preprocessing mainly validates and normalizes the types.

If the raw file matches the Kaggle schema, preprocessing creates the app-compatible features by:

- mapping `Amount` to `transaction_amount`
- deriving `merchant_risk_score` from strong fraud-related latent signals
- estimating `transaction_velocity_1h` from time deltas
- projecting anonymized signals into `card_present`, `international`, and `customer_age` proxies

These projections are approximations intended to keep the live API schema stable while letting you train on a real public dataset.

## Commands

```bash
python -m training.pipelines.prepare_real_data
python -m training.pipelines.train
```

## Outputs

- `data/processed/transactions_processed.csv`
- `artifacts/model.joblib`
- `artifacts/metrics.txt`
