# AWS Deployment Guide

## Deployment target

This project uses `AWS ECS Fargate` as the first cloud deployment target.

Why this path:

- easier than EKS for a first deployment
- still strong for resume value
- includes Terraform, ECR, ECS, ALB, IAM, CloudWatch, and S3

## What Terraform creates

- VPC with two public subnets
- Internet gateway and public route table
- Application Load Balancer
- Security groups
- ECR repository
- S3 bucket for artifacts
- CloudWatch log group
- ECS cluster
- ECS task definition
- ECS Fargate service
- IAM execution role

## Before you deploy

1. Install and configure:
   - AWS CLI
   - Terraform
   - Docker Desktop
2. Authenticate AWS:

```bash
aws configure
```

3. Copy the example variables:

```powershell
Copy-Item infra/terraform/terraform.tfvars.example infra/terraform/terraform.tfvars
```

## Deploy workflow

### 1. Create AWS infrastructure

```bash
cd infra/terraform
terraform init
terraform plan
terraform apply
```

After apply, note the output:

- `ecr_repository_url`

At this stage, the ECS service is intentionally not created yet. That avoids deployment failures before the image exists in ECR.

### 2. Build and push the Docker image

Authenticate Docker to ECR:

```bash
aws ecr get-login-password --region ap-south-1 | docker login --username AWS --password-stdin <your-ecr-repository-url-without-tag>
```

Build and tag:

```bash
docker build -f infra/docker/Dockerfile.api -t fraudshield-app:latest .
docker tag fraudshield-app:latest <ecr_repository_url>:latest
docker push <ecr_repository_url>:latest
```

### 3. Enable the ECS service

Set this in `infra/terraform/terraform.tfvars`:

```hcl
deploy_app_service = true
```

Then apply again:

```powershell
terraform apply
```

### 4. Open the deployed app

Use the Terraform output:

- `alb_dns_name`

Then open:

```text
http://<alb_dns_name>/
```

## Notes

- The current Terraform path deploys the API and frontend together as one service.
- Kafka streaming is not deployed to AWS yet in this first path.
- This is the right first deployment target; Kafka can be added later via MSK or separate ECS services.

## GitHub Actions deployment

The repo now includes:

- `.github/workflows/ci.yml` for running tests on pull requests and pushes
- `.github/workflows/deploy-aws.yml` for building the Docker image, pushing to ECR, and triggering an ECS rollout

### Required GitHub secrets

Add these repository secrets before using the deploy workflow:

- `AWS_ACCESS_KEY_ID`
- `AWS_SECRET_ACCESS_KEY`
- `AWS_REGION`
- `ECR_REPOSITORY`
- `ECS_CLUSTER`
- `ECS_SERVICE`

### How the deploy workflow works

1. Runs the test suite
2. Builds the API image from `infra/docker/Dockerfile.api`
3. Pushes the image to ECR with both the commit SHA tag and `latest`
4. Calls `aws ecs update-service --force-new-deployment`
