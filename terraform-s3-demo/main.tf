resource "aws_s3_bucket" "coursework" {
  bucket_prefix = var.bucket_prefix
  force_destroy = false
}

resource "aws_s3_bucket_public_access_block" "coursework" {
  bucket                  = aws_s3_bucket.coursework.id
  block_public_acls       = true
  block_public_policy     = true
  ignore_public_acls      = true
  restrict_public_buckets = true
}

resource "aws_s3_bucket_ownership_controls" "coursework" {
  bucket = aws_s3_bucket.coursework.id

  rule {
    object_ownership = "BucketOwnerEnforced"
  }
}

resource "aws_s3_bucket_versioning" "coursework" {
  bucket = aws_s3_bucket.coursework.id

  versioning_configuration {
    status = "Enabled"
  }
}

resource "aws_s3_bucket_server_side_encryption_configuration" "coursework" {
  bucket = aws_s3_bucket.coursework.id

  rule {
    apply_server_side_encryption_by_default {
      sse_algorithm = "AES256"
    }
  }
}
