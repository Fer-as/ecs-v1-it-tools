output "cluster_name" {
  description = "ECS cluster name"
  value       = aws_ecs_cluster.this.name
}

output "cluster_arn" {
  description = "ECS cluster ARN"
  value       = aws_ecs_cluster.this.arn
}

output "task_definition_arn" {
  description = "ECS task definition ARN including revision"
  value       = aws_ecs_task_definition.this.arn
}

output "task_security_group_id" {
  description = "Security group ID for ECS tasks"
  value       = aws_security_group.task.id
}

output "execution_role_arn" {
  description = "IAM execution role ARN used by ECS"
  value       = aws_iam_role.execution.arn
}

output "log_group_name" {
  description = "CloudWatch log group for container logs"
  value       = aws_cloudwatch_log_group.this.name
}