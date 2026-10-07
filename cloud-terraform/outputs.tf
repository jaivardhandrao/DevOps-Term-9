output "vpc_id" {
  description = "VPC managed by this stack."
  value       = aws_vpc.coursework.id
}

output "subnet_id" {
  description = "Public subnet with its internet route."
  value       = aws_subnet.public.id
}

output "security_group_id" {
  description = "Security group allowing only the configured HTTP source."
  value       = aws_security_group.web.id
}

output "instance_id" {
  description = "EC2 instance ID for console inspection."
  value       = aws_instance.web.id
}

output "website_url" {
  description = "HTTP lab URL; accessible only from allowed_http_cidr after cloud-init completes."
  value       = "http://${aws_instance.web.public_ip}"
}

output "bucket_name" {
  description = "Private S3 artifact bucket; the web page does not require S3 credentials."
  value       = aws_s3_bucket.artifacts.id
}
