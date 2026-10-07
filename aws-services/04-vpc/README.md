# Amazon VPC — Networking

- **Name:** Jaivardhan D. Rao
- **Enrollment number:** 24BCS10117
- **Status:** Study notes complete. The network below is a design example, not a deployed environment.
- **Documentation checked:** 7 October 2026.

## What is VPC?

Amazon Virtual Private Cloud (VPC) is a logically isolated virtual network for AWS resources.
It lets us choose IP ranges, divide resources into subnets, configure traffic routes, and
control network access. A VPC can contain subnets in multiple Availability Zones; each subnet
belongs to one zone. [AWS: What is Amazon VPC?](https://docs.aws.amazon.com/vpc/latest/userguide/what-is-amazon-vpc.html)

## CIDR and subnets

**CIDR** means Classless Inter-Domain Routing. The suffix is the number of network-prefix bits:
`10.20.0.0/16` contains 65,536 IPv4 addresses, while `10.20.1.0/24` contains 256. A larger suffix
means a smaller address block. A VPC's IPv4 block can range from `/16` to `/28`.
[AWS: VPC CIDR blocks](https://docs.aws.amazon.com/vpc/latest/userguide/vpc-cidr-blocks.html)

A **subnet** takes an address range from the VPC. Subnet ranges cannot overlap. For ordinary
AWS IPv4 subnets, the first four addresses and the last address are reserved, so a `/24` has
251 addresses available to resources. [AWS: Subnet CIDR blocks](https://docs.aws.amazon.com/vpc/latest/userguide/subnet-sizing.html)

Example addressing plan:

| Resource | CIDR | Intended role |
| --- | --- | --- |
| VPC | `10.20.0.0/16` | Whole application network. |
| Public subnet, zone A | `10.20.1.0/24` | Internet-facing entry point and a public NAT gateway. |
| Private subnet, zone A | `10.20.2.0/24` | Application instances without direct internet access. |

## Route tables

A route table maps a **destination** to a **target**, such as an internet gateway or NAT
gateway. Every subnet uses a route table through an explicit association or the VPC's main
table. Routes determine the network path; firewall rules still determine whether traffic is
allowed. [AWS: Route tables](https://docs.aws.amazon.com/vpc/latest/userguide/VPC_Route_Tables.html),
[AWS: Subnet routing](https://docs.aws.amazon.com/vpc/latest/userguide/configure-subnets.html#subnet-routing)

Illustrative IPv4 routes for this design:

| Associated subnet | Destination | Target | Purpose |
| --- | --- | --- | --- |
| Both | `10.20.0.0/16` | `local` | Route within the VPC. |
| Public | `0.0.0.0/0` | Internet gateway | Internet destinations outside the local range. |
| Private | `0.0.0.0/0` | Public NAT gateway | Outbound internet traffic through address translation. |

The VPC CIDR contributes a local route. The public/private routing pattern follows
[AWS's example architecture](https://docs.aws.amazon.com/vpc/latest/userguide/vpc-example-private-subnets-nat.html).

## Internet Gateway and NAT Gateway

An **Internet Gateway (IGW)** connects a VPC to the internet. For an EC2 instance to communicate
directly over IPv4, the subnet needs an IGW route, the instance needs a public IPv4 address or
Elastic IP, and security rules must permit the traffic. A route alone does not make an
instance reachable. [AWS: Internet gateway](https://docs.aws.amazon.com/vpc/latest/userguide/VPC_Internet_Gateway.html)

A **NAT Gateway** translates addresses for connections initiated from inside the VPC. In this
zonal example, a public NAT gateway sits in the public subnet with an Elastic IP and forwards
internet traffic through the IGW. Private instances can download updates and receive replies
without accepting unsolicited inbound internet connections. A private NAT gateway is for
private connectivity and does not provide internet access through an IGW.
[AWS: NAT gateways](https://docs.aws.amazon.com/vpc/latest/userguide/vpc-nat-gateway.html)

```text
Private instance -> private route table -> public NAT gateway
                 -> public subnet route table -> Internet Gateway -> internet
```

## Security Groups and Network ACLs

Both filter traffic, but they operate at different boundaries:

| Feature | Security Group (SG) | Network ACL (NACL) |
| --- | --- | --- |
| Scope | Associated resources, such as an EC2 instance's network interface. | Traffic entering or leaving associated subnets. |
| Rules | Allow rules; traffic without an applicable allow is denied. | Allow and deny rules. |
| Evaluation | Applicable allow rules combine. | Lowest rule number first; first matching rule decides. |
| Connection state | Stateful: replies to permitted traffic are automatically allowed. | Stateless: rules must also allow return traffic. |
| Example | Allow the application's port only from the load balancer's SG. | Deny a particular external CIDR at the subnet boundary. |

[AWS: Compare security groups and network ACLs](https://docs.aws.amazon.com/vpc/latest/userguide/infrastructure-security.html#VPC_Security_Comparison)

NACL rules also need to allow the relevant ephemeral return ports. They are checked when
traffic enters or leaves a subnet, not when it travels between resources inside that subnet.
[AWS: Network ACLs](https://docs.aws.amazon.com/vpc/latest/userguide/vpc-network-acls.html)

## Public versus private subnet

| Public subnet | Private subnet |
| --- | --- |
| Has a direct route to an IGW. | Has no direct route to an IGW. |
| Can host an internet-facing entry point. | Can host application or database tiers. |
| Direct IPv4 internet access additionally requires a public IP and permitted traffic. | Can use NAT for outbound IPv4 internet access or VPC endpoints for supported AWS services. |

The route table determines the classification; naming a subnet `public` does not configure
internet connectivity. Private does not necessarily mean fully isolated: NAT, endpoints, VPNs,
or other routes may still provide connectivity.
[AWS: Subnet types](https://docs.aws.amazon.com/vpc/latest/userguide/configure-subnets.html#subnet-types),
[AWS: Gateways and endpoints](https://docs.aws.amazon.com/vpc/latest/userguide/what-is-amazon-vpc.html#vpc-features)
