variable "aws_region" {
  description = "AWS Region for the prospective EKS stack; no deployment is performed by tests."
  type        = string
  default     = "ap-south-1"
}

variable "cluster_name" {
  description = "Unique name for the coursework cluster and its resources."
  type        = string
  default     = "jvrao-term9-final"

  validation {
    condition     = can(regex("^[a-z][a-z0-9-]{2,29}$", var.cluster_name))
    error_message = "Use 3–30 lowercase letters, digits and hyphens, starting with a letter."
  }
}

variable "kubernetes_version" {
  description = "Explicit EKS Kubernetes version. Recheck regional support before any future deployment."
  type        = string
  default     = "1.35"

  validation {
    condition     = can(regex("^1\\.[0-9]{2}$", var.kubernetes_version))
    error_message = "Use a Kubernetes minor version such as 1.35."
  }
}

variable "vpc_cidr" {
  description = "IPv4 /16 for this isolated stack."
  type        = string
  default     = "10.30.0.0/16"

  validation {
    condition     = can(cidrnetmask(var.vpc_cidr)) && can(regex("/16$", var.vpc_cidr))
    error_message = "Use a valid IPv4 /16; subnet offsets rely on this size."
  }
}

variable "node_instance_type" {
  description = "Small x86_64 managed-node size compatible with the AL2023 node AMI."
  type        = string
  default     = "t3.medium"

  validation {
    condition     = contains(["t3.medium", "t3.large"], var.node_instance_type)
    error_message = "Use t3.medium or t3.large; the node AMI is x86_64."
  }
}

variable "deployment_authorized" {
  description = "Explicit guard for a future reviewed deployment that creates paid AWS resources and service roles. Keep false for normal work; mock tests override it internally."
  type        = bool
  default     = false
}
