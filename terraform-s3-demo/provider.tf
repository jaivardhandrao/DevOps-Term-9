terraform {
  required_version = ">= 1.7, < 2.0"

  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "= 6.58.0"
    }
  }
}

provider "aws" {
  region = var.aws_region

  default_tags {
    tags = {
      Project    = "DevOps-Term-9"
      Session    = "18"
      ManagedBy  = "Terraform"
      Enrollment = "24BCS10117"
    }
  }
}
