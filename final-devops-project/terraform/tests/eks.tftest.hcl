# All apply/plan operations in this file are mocked. No resource is created in AWS.
mock_provider "aws" {
  mock_data "aws_availability_zones" {
    defaults = { names = ["ap-south-1a", "ap-south-1b"] }
  }

  mock_resource "aws_launch_template" {
    defaults = {
      id             = "lt-0123456789abcdef0"
      latest_version = 1
    }
  }

  mock_resource "aws_iam_openid_connect_provider" {
    defaults = { arn = "arn:aws:iam::123456789012:oidc-provider/oidc.eks.ap-south-1.amazonaws.com/id/MOCK" }
  }

  mock_resource "aws_eks_cluster" {
    defaults = {
      endpoint = "https://mock-cluster.invalid"
      identity = [{ oidc = [{ issuer = "https://oidc.eks.ap-south-1.amazonaws.com/id/MOCK" }] }]
    }
  }
}

# Distinct role IDs make an accidental cluster/node/CNI role swap detectable.
override_resource {
  target = aws_iam_role.cluster
  values = {
    arn  = "arn:aws:iam::123456789012:role/mock-cluster"
    name = "mock-cluster"
  }
}

override_resource {
  target = aws_iam_role.nodes
  values = {
    arn  = "arn:aws:iam::123456789012:role/mock-nodes"
    name = "mock-nodes"
  }
}

override_resource {
  target = aws_iam_role.cni
  values = {
    arn  = "arn:aws:iam::123456789012:role/mock-cni"
    name = "mock-cni"
  }
}

variables {
  deployment_authorized = true
}

run "private_cluster_with_scoped_roles" {
  # Mock apply resolves computed IDs so assertions can verify actual references and trust policies.
  command = apply

  assert {
    condition     = length(aws_subnet.public) == 2 && length(aws_subnet.private) == 2 && alltrue([for subnet in aws_subnet.private : !subnet.map_public_ip_on_launch])
    error_message = "Two public and two private subnets are required; private nodes must not receive public IPs."
  }

  assert {
    condition     = aws_subnet.private["a"].availability_zone != aws_subnet.private["b"].availability_zone
    error_message = "Private subnets must span distinct Availability Zones."
  }

  assert {
    condition     = toset(aws_eks_node_group.coursework.subnet_ids) == toset([for subnet in aws_subnet.private : subnet.id])
    error_message = "Managed nodes must use only the private subnets."
  }

  assert {
    condition     = one(aws_route_table.private.route).nat_gateway_id == aws_nat_gateway.coursework.id && one(aws_route_table.public.route).gateway_id == aws_internet_gateway.coursework.id
    error_message = "Private egress must use NAT; only the public route table points at the IGW."
  }

  assert {
    condition     = aws_eks_cluster.coursework.vpc_config[0].endpoint_private_access && !aws_eks_cluster.coursework.vpc_config[0].endpoint_public_access
    error_message = "The Kubernetes API must be private."
  }

  assert {
    condition     = aws_eks_cluster.coursework.access_config[0].authentication_mode == "API" && !aws_eks_cluster.coursework.access_config[0].bootstrap_cluster_creator_admin_permissions
    error_message = "Do not silently grant the Terraform caller cluster-admin."
  }

  assert {
    condition     = toset([for attachment in aws_iam_role_policy_attachment.nodes : attachment.policy_arn]) == toset(["arn:aws:iam::aws:policy/AmazonEKSWorkerNodePolicy", "arn:aws:iam::aws:policy/AmazonEC2ContainerRegistryPullOnly"])
    error_message = "The node role must not receive administrator or CNI permissions."
  }

  assert {
    condition     = aws_eks_node_group.coursework.node_role_arn == aws_iam_role.nodes.arn && aws_eks_cluster.coursework.role_arn == aws_iam_role.cluster.arn && aws_iam_role.nodes.arn != aws_iam_role.cni.arn
    error_message = "Cluster, node and CNI identities must remain separate and correctly attached."
  }

  assert {
    condition     = jsondecode(aws_iam_role.cni.assume_role_policy).Statement[0].Condition.StringEquals["${local.oidc_issuer}:sub"] == "system:serviceaccount:kube-system:aws-node" && jsondecode(aws_iam_role.cni.assume_role_policy).Statement[0].Condition.StringEquals["${local.oidc_issuer}:aud"] == "sts.amazonaws.com"
    error_message = "CNI identity must be restricted to aws-node and the STS audience."
  }

  assert {
    condition     = aws_eks_addon.vpc_cni.service_account_role_arn == aws_iam_role.cni.arn && aws_iam_role_policy_attachment.cni.policy_arn == "arn:aws:iam::aws:policy/AmazonEKS_CNI_Policy"
    error_message = "The VPC CNI must use its dedicated service-account role."
  }

  assert {
    condition     = aws_launch_template.nodes.metadata_options[0].http_tokens == "required" && aws_launch_template.nodes.metadata_options[0].http_put_response_hop_limit == 1 && aws_launch_template.nodes.block_device_mappings[0].ebs[0].encrypted
    error_message = "Node instances must require IMDSv2, limit metadata hops and encrypt disks."
  }

  assert {
    condition     = contains(aws_eks_cluster.coursework.enabled_cluster_log_types, "audit") && aws_cloudwatch_log_group.cluster.retention_in_days == 7
    error_message = "Preserve audit logging with explicit lab retention."
  }
}

run "real_deployment_guard" {
  command = plan

  variables {
    deployment_authorized = false
  }

  expect_failures = [aws_vpc.coursework]
}

run "reject_incompatible_node_architecture" {
  command = plan

  variables {
    node_instance_type = "t4g.medium"
  }

  expect_failures = [var.node_instance_type]
}

run "reject_wrong_network_size" {
  command = plan

  variables {
    vpc_cidr = "10.30.0.0/24"
  }

  expect_failures = [var.vpc_cidr]
}
