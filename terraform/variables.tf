variable "project_name" {
  description = "Project name prefix"
  type        = string
  default     = "ecs-it-tools"
}

variable "aws_region" {
  description = "AWS region"
  type        = string
  default     = "eu-west-2"
}

variable "domain_name" {
  description = "Root domain name"
  type        = string
  default     = "feras-dev.co.uk"
}

variable "subdomain_name" {
  description = "Subdomain for the application"
  type        = string
  default     = "it-tools"
}

variable "vpc_cidr" {
  description = "CIDR block for the VPC"
  type        = string
  default     = "10.0.0.0/16"
}

variable "public_subnet_cidrs" {
  description = "Public subnet CIDR ranges"
  type        = list(string)
  default     = ["10.0.1.0/24", "10.0.2.0/24"]
}

variable "private_subnet_cidrs" {
  description = "Private subnet CIDR ranges"
  type        = list(string)
  default     = ["10.0.11.0/24", "10.0.12.0/24"]
}

variable "availability_zones" {
  description = "Availability zones for the subnets"
  type        = list(string)
  default     = ["eu-west-2a", "eu-west-2b"]
}

variable "certificate_arn" {
  description = "ACM certificate ARN for the ALB"
  type        = string
}
