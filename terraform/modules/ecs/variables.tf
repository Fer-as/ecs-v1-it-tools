variable "project_name" {
  description = "Project name prefix for ECS resources"
  type        = string
}

variable "aws_region" {
  description = "AWS region for container logging"
  type        = string
}

variable "vpc_id" {
  description = "VPC ID for the ECS task security group"
  type        = string
}

variable "alb_security_group_id" {
  description = "ALB security group allowed to reach the application"
  type        = string
}

variable "ecr_repository_url" {
  description = "ECR repository URL without an image tag"
  type        = string
}

variable "image_tag" {
  description = "Explicit application version or commit SHA tag"
  type        = string
  nullable    = false

  validation {
    condition = (
      can(regex("^[A-Za-z0-9_][A-Za-z0-9_.-]{0,127}$", var.image_tag)) &&
      lower(var.image_tag) != "latest"
    )
    error_message = "Provide a valid explicit version or commit SHA tag; latest is not allowed."
  }
}

variable "private_subnet_ids" {
  description = "Private subnet IDs for ECS service tasks"
  type        = list(string)
}

variable "target_group_arn" {
  description = "ALB target group ARN for the application on port 8080"
  type        = string
}
