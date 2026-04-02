output "alb_dns" {
  description = "Public DNS name of the Application Load Balancer"
  value       = aws_lb.helios.dns_name
}

output "ecs_cluster_name" {
  description = "ECS cluster name"
  value       = aws_ecs_cluster.helios.name
}

output "metrics_service_url" {
  description = "Base URL for the Helios metrics REST API"
  value       = "http://${aws_lb.helios.dns_name}/api/metrics"
}

output "sns_topic_arn" {
  description = "ARN of the SNS alerts topic"
  value       = aws_sns_topic.alerts.arn
}
