output "ecr_repository_url" {
  description = "ECR repository URL for Docker image pushes"
  value       = module.ecr.repository_url
}

output "ecr_repository_name" {
  description = "ECR repository name"
  value       = module.ecr.repository_name
}

output "vpc_id" {
  description = "Project VPC ID"
  value       = module.vpc.vpc_id
}

output "public_subnet_ids" {
  description = "Public subnet IDs used by the ALB"
  value       = module.vpc.public_subnet_ids
}

output "private_subnet_ids" {
  description = "Private subnet IDs intended for ECS tasks"
  value       = module.vpc.private_subnet_ids
}

output "alb_dns_name" {
  description = "AWS-generated ALB DNS name"
  value       = module.alb.alb_dns_name
}

output "target_group_arn" {
  description = "ALB target group ARN for ECS integration"
  value       = module.alb.target_group_arn
}

output "ecs_cluster_name" {
  description = "ECS cluster name"
  value       = module.ecs.cluster_name
}

output "ecs_cluster_arn" {
  description = "ECS cluster ARN"
  value       = module.ecs.cluster_arn
}

output "ecs_task_definition_arn" {
  description = "ECS task definition ARN including revision"
  value       = module.ecs.task_definition_arn
}

output "ecs_task_security_group_id" {
  description = "Security group ID for ECS tasks"
  value       = module.ecs.task_security_group_id
}

output "ecs_execution_role_arn" {
  description = "IAM execution role ARN used by ECS"
  value       = module.ecs.execution_role_arn
}

output "ecs_log_group_name" {
  description = "CloudWatch log group for container logs"
  value       = module.ecs.log_group_name
}

output "ecs_service_name" {
  description = "ECS service name"
  value       = module.ecs.service_name
}

output "application_url" {
  description = "Application HTTPS URL"
  value       = "https://${aws_route53_record.app.fqdn}"
}

output "acm_certificate_arn" {
  description = "Validated ACM certificate ARN"
  value       = aws_acm_certificate_validation.this.certificate_arn
}
