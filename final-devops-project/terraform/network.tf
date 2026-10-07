data "aws_availability_zones" "available" {
  state = "available"
}

locals {
  zones = { a = 0, b = 1 }
}

resource "aws_vpc" "coursework" {
  cidr_block           = var.vpc_cidr
  enable_dns_support   = true
  enable_dns_hostnames = true
  tags                 = { Name = "${var.cluster_name}-vpc" }

  lifecycle {
    precondition {
      condition     = var.deployment_authorized
      error_message = "Real AWS deployment is not authorized by default. This stack creates paid infrastructure and service roles. Use the mocked tests; obtain a separately reviewed deployment decision before changing deployment_authorized."
    }
  }
}

resource "aws_subnet" "public" {
  for_each                = local.zones
  vpc_id                  = aws_vpc.coursework.id
  cidr_block              = cidrsubnet(var.vpc_cidr, 8, each.value)
  availability_zone       = data.aws_availability_zones.available.names[each.value]
  map_public_ip_on_launch = false

  tags = {
    Name                     = "${var.cluster_name}-public-${each.key}"
    "kubernetes.io/role/elb" = "1"
  }
}

resource "aws_subnet" "private" {
  for_each                = local.zones
  vpc_id                  = aws_vpc.coursework.id
  cidr_block              = cidrsubnet(var.vpc_cidr, 8, 10 + each.value)
  availability_zone       = data.aws_availability_zones.available.names[each.value]
  map_public_ip_on_launch = false

  tags = {
    Name                              = "${var.cluster_name}-private-${each.key}"
    "kubernetes.io/role/internal-elb" = "1"
  }
}

resource "aws_internet_gateway" "coursework" {
  vpc_id = aws_vpc.coursework.id
  tags   = { Name = "${var.cluster_name}-igw" }
}

resource "aws_route_table" "public" {
  vpc_id = aws_vpc.coursework.id

  route {
    cidr_block = "0.0.0.0/0"
    gateway_id = aws_internet_gateway.coursework.id
  }

  tags = { Name = "${var.cluster_name}-public" }
}

resource "aws_route_table_association" "public" {
  for_each       = local.zones
  subnet_id      = aws_subnet.public[each.key].id
  route_table_id = aws_route_table.public.id
}

resource "aws_eip" "nat" {
  domain = "vpc"
  tags   = { Name = "${var.cluster_name}-nat" }
}

# One NAT is a classroom cost tradeoff, not a multi-AZ egress availability claim.
resource "aws_nat_gateway" "coursework" {
  allocation_id = aws_eip.nat.id
  subnet_id     = aws_subnet.public["a"].id
  tags          = { Name = "${var.cluster_name}-nat" }
  depends_on    = [aws_internet_gateway.coursework]
}

resource "aws_route_table" "private" {
  vpc_id = aws_vpc.coursework.id

  route {
    cidr_block     = "0.0.0.0/0"
    nat_gateway_id = aws_nat_gateway.coursework.id
  }

  tags = { Name = "${var.cluster_name}-private" }
}

resource "aws_route_table_association" "private" {
  for_each       = local.zones
  subnet_id      = aws_subnet.private[each.key].id
  route_table_id = aws_route_table.private.id
}
