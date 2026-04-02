variable "aws_region" {
  description = "AWS region to deploy into"
  type        = string
  default     = "ap-southeast-2"
}

variable "environment" {
  description = "Deployment environment (dev | staging | prod)"
  type        = string
  validation {
    condition     = contains(["dev", "staging", "prod"], var.environment)
    error_message = "environment must be one of: dev, staging, prod"
  }
}

variable "ecr_repo_url" {
  description = "ECR repository URL for the metrics-service image"
  type        = string
}

variable "image_tag" {
  description = "Docker image tag to deploy (typically a Git SHA)"
  type        = string
  default     = "latest"
}

variable "db_host" {
  description = "RDS PostgreSQL hostname"
  type        = string
}

variable "ssm_prefix" {
  description = "SSM Parameter Store path prefix for secrets (e.g. /helios/prod)"
  type        = string
  default     = "/helios/dev"
}

variable "desired_count" {
  description = "Desired number of ECS task replicas"
  type        = number
  default     = 2
}

variable "alert_email" {
  description = "Email address to receive SNS alert notifications (leave empty to skip)"
  type        = string
  default     = ""
}
