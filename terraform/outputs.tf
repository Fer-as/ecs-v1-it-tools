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