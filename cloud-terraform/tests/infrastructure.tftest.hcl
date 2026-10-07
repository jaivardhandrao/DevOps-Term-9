# No real AWS provider calls. The AMI and AZ are public-shaped, fictitious fixtures.
mock_provider "aws" {
  mock_data "aws_availability_zones" {
    defaults = { names = ["ap-south-1a", "ap-south-1b"] }
  }

  mock_data "aws_ssm_parameter" {
    defaults = { value = "ami-0123456789abcdef0" }
  }
}

run "network_and_compute_contract" {
  command = plan

  assert {
    condition     = aws_vpc.coursework.cidr_block == "10.20.0.0/16" && aws_subnet.public.cidr_block == "10.20.1.0/24"
    error_message = "The lab must use the expected VPC and derived subnet."
  }

  assert {
    condition     = one(aws_route_table.public.route).cidr_block == "0.0.0.0/0"
    error_message = "The public subnet needs a default route via the internet gateway."
  }

  assert {
    condition     = aws_vpc_security_group_ingress_rule.http.cidr_ipv4 == "203.0.113.10/32" && aws_vpc_security_group_ingress_rule.http.from_port == 80 && aws_vpc_security_group_ingress_rule.http.to_port == 80
    error_message = "HTTP ingress must be limited to the configured client CIDR and port."
  }

  assert {
    condition     = aws_instance.web.metadata_options[0].http_tokens == "required" && aws_instance.web.root_block_device[0].encrypted
    error_message = "The web instance must require IMDSv2 and encrypted EBS."
  }

  assert {
    condition     = aws_instance.web.associate_public_ip_address && aws_instance.web.instance_type == "t3.micro"
    error_message = "The demo web instance needs an explicit public IP and the small x86 instance type."
  }

  assert {
    condition = alltrue([
      aws_s3_bucket_public_access_block.artifacts.block_public_acls,
      aws_s3_bucket_public_access_block.artifacts.block_public_policy,
      aws_s3_bucket_public_access_block.artifacts.ignore_public_acls,
      aws_s3_bucket_public_access_block.artifacts.restrict_public_buckets,
    ]) && !aws_s3_bucket.artifacts.force_destroy
    error_message = "Artifact storage must remain private and resist accidental content deletion."
  }

  assert {
    condition     = strcontains(aws_instance.web.user_data, "Hello from jvrao-term9") && strcontains(aws_instance.web.user_data, "systemctl enable --now nginx")
    error_message = "Bootstrapping must install/start the page's web server."
  }
}

run "reject_public_ingress" {
  command = plan

  variables {
    allowed_http_cidr = "0.0.0.0/0"
  }

  expect_failures = [var.allowed_http_cidr]
}

run "reject_wrong_vpc_size" {
  command = plan

  variables {
    vpc_cidr = "10.20.0.0/24"
  }

  expect_failures = [var.vpc_cidr]
}

run "reject_incompatible_arm_instance" {
  command = plan

  variables {
    instance_type = "t4g.micro"
  }

  expect_failures = [var.instance_type]
}
