output "alb_dns_name" {
  value       = aws_lb.app.dns_name
  description = "Public DNS name of the application load balancer"
}

output "ecr_repository_url" {
  value       = aws_ecr_repository.app.repository_url
  description = "ECR repository URL for the app image"
}

output "artifacts_bucket_name" {
  value       = aws_s3_bucket.artifacts.bucket
  description = "S3 bucket for model and dataset artifacts"
}

output "prediction_logs_bucket_name" {
  value       = aws_s3_bucket.prediction_logs.bucket
  description = "S3 bucket for exported prediction logs"
}

output "ecs_cluster_name" {
  value       = aws_ecs_cluster.main.name
  description = "ECS cluster name"
}

output "ecs_service_name" {
  value       = var.deploy_app_service ? aws_ecs_service.app[0].name : null
  description = "ECS service name"
}
