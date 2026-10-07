variable "aws_region" {
  description = "Region for this disposable coursework stack."
  type        = string
  default     = "ap-south-1"
}

variable "project_name" {
  description = "Short lowercase project name used for tags and unique bucket prefix."
  type        = string
  default     = "jvrao-term9"

  validation {
    condition     = can(regex("^[a-z][a-z0-9-]{2,19}$", var.project_name))
    error_message = "Use 3–20 lowercase letters/digits/hyphens, starting with a letter."
  }
}

variable "vpc_cidr" {
  description = "IPv4 VPC range; the first /24 subnet is derived from this /16."
  type        = string
  default     = "10.20.0.0/16"

  validation {
    condition     = can(cidrnetmask(var.vpc_cidr)) && can(regex("/16$", var.vpc_cidr))
    error_message = "Provide a valid IPv4 /16 CIDR such as 10.20.0.0/16."
  }
}

variable "allowed_http_cidr" {
  description = "Your public IPv4 address with /32, or a trusted /24-or-smaller classroom range. Replace the documentation-only default before deployment."
  type        = string
  default     = "203.0.113.10/32"

  validation {
    condition     = can(cidrnetmask(var.allowed_http_cidr)) && try(tonumber(split("/", var.allowed_http_cidr)[1]) >= 24, false)
    error_message = "Use a valid IPv4 /24 through /32; do not expose the lab to all internet addresses."
  }
}

variable "instance_type" {
  description = "Small x86_64 instance compatible with the selected Amazon Linux AMI; AWS charges may apply."
  type        = string
  default     = "t3.micro"

  validation {
    condition     = contains(["t3.micro", "t3.small"], var.instance_type)
    error_message = "This lab supports t3.micro or t3.small (x86_64)."
  }
}
