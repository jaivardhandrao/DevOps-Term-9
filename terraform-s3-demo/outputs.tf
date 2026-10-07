output "bucket_name" {
  description = "Actual unique bucket name, assigned only on real AWS apply."
  value       = aws_s3_bucket.coursework.id
}

output "bucket_arn" {
  description = "ARN of the coursework bucket."
  value       = aws_s3_bucket.coursework.arn
}

output "bucket_region" {
  description = "Configured AWS Region."
  value       = var.aws_region
}
