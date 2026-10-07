output "cluster_name" {
  description = "Name of the prospective EKS cluster."
  value       = aws_eks_cluster.coursework.name
}

output "cluster_endpoint" {
  description = "Private EKS API endpoint; an approved VPC network path is needed to reach it."
  value       = aws_eks_cluster.coursework.endpoint
}

output "vpc_id" {
  value = aws_vpc.coursework.id
}

output "private_subnet_ids" {
  value = [for subnet in aws_subnet.private : subnet.id]
}

output "public_subnet_ids" {
  value = [for subnet in aws_subnet.public : subnet.id]
}

output "node_role_arn" {
  description = "Service role for managed nodes; not an administrator identity."
  value       = aws_iam_role.nodes.arn
}
