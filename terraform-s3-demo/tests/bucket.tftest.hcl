# The entire AWS provider is mocked. These tests never call AWS or use credentials.
mock_provider "aws" {}

run "private_versioned_bucket" {
  command = plan

  assert {
    condition     = aws_s3_bucket.coursework.bucket_prefix == "jvrao24bcs10117-s18-" && !aws_s3_bucket.coursework.force_destroy
    error_message = "Use the student prefix and refuse implicit deletion of bucket contents."
  }

  assert {
    condition = alltrue([
      aws_s3_bucket_public_access_block.coursework.block_public_acls,
      aws_s3_bucket_public_access_block.coursework.block_public_policy,
      aws_s3_bucket_public_access_block.coursework.ignore_public_acls,
      aws_s3_bucket_public_access_block.coursework.restrict_public_buckets,
    ])
    error_message = "All four public-access protections must be enabled."
  }

  assert {
    condition     = aws_s3_bucket_versioning.coursework.versioning_configuration[0].status == "Enabled"
    error_message = "Object versioning must be enabled."
  }

  assert {
    condition     = one(aws_s3_bucket_server_side_encryption_configuration.coursework.rule).apply_server_side_encryption_by_default[0].sse_algorithm == "AES256"
    error_message = "SSE-S3 encryption must be explicitly configured."
  }

  assert {
    condition     = aws_s3_bucket_ownership_controls.coursework.rule[0].object_ownership == "BucketOwnerEnforced"
    error_message = "Use bucket-owner enforcement instead of ACLs."
  }
}

run "reject_invalid_bucket_prefix" {
  command = plan

  variables {
    bucket_prefix = "Invalid_Bucket"
  }

  expect_failures = [var.bucket_prefix]
}
