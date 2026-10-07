variable "aws_region" {
  description = "AWS Region for the isolated coursework bucket."
  type        = string
  default     = "ap-south-1"

  validation {
    condition     = can(regex("^[a-z]{2}(-[a-z]+)+-[0-9]+$", var.aws_region))
    error_message = "Use an AWS Region name such as ap-south-1."
  }
}

variable "bucket_prefix" {
  description = "Public lowercase name prefix; AWS provider appends a unique suffix. Not a credential."
  type        = string
  default     = "jvrao24bcs10117-s18-"

  validation {
    condition     = can(regex("^[a-z0-9][a-z0-9-]{1,35}-$", var.bucket_prefix))
    error_message = "Use 3–37 lowercase letters, digits and hyphens, starting with a letter/digit and ending with a hyphen."
  }
}
