# EC2 — Compute

Amazon Elastic Compute Cloud (EC2) provides virtual servers called **instances**. An instance runs an operating system and applications using selected compute, memory, storage and networking resources. EC2 suits workloads needing control over the operating system, such as web servers, build workers and batch processing. [AWS: What is EC2?](https://docs.aws.amazon.com/AWSEC2/latest/UserGuide/concepts.html)

## AMIs and instance types

An **Amazon Machine Image (AMI)** is the launch image containing the operating system and software configuration. Select a trusted, maintained image compatible with the instance's CPU architecture. AMIs are regional; an image must exist in the Region where the instance is launched. [AWS: AMIs](https://docs.aws.amazon.com/AWSEC2/latest/UserGuide/AMIs.html)

The **instance type** selects the hardware capacity. Family and size are different choices: a compute-focused family changes the resource balance, while a larger size supplies more capacity.

| Category | Typical workload |
| --- | --- |
| General purpose | Web applications and development environments |
| Compute optimized | CPU-heavy processing and builds |
| Memory optimized | Large in-memory datasets |
| Storage optimized | Workloads needing high local storage throughput |
| Accelerated computing | GPU/accelerator workloads, including machine learning |
| High-performance computing | Scientific simulations |

Burstable T-family instances use CPU credits, so they are different from instances intended for sustained CPU demand. Choose for measured application requirements and regional availability. [AWS: Instance types](https://docs.aws.amazon.com/ec2/latest/instancetypes/instance-types.html)

## Key pairs and Security Groups

A **key pair** has a public key and a private key. For Linux SSH, the server stores the public key and the administrator uses the private key. For supported Windows launches, the private key decrypts the initial administrator password. Protect the private key; AWS does not keep a recoverable copy of it. [AWS: EC2 key pairs](https://docs.aws.amazon.com/AWSEC2/latest/UserGuide/ec2-key-pairs.html)

A **Security Group** controls allowed inbound and outbound traffic at network interfaces. It is stateful: return traffic for an allowed connection is permitted automatically. Rules allow traffic; they do not express explicit denies. For a web server, allow HTTPS from its intended clients and restrict administration to approved sources. A permitted port also needs a reachable network path and a listening service. [AWS: EC2 Security Groups](https://docs.aws.amazon.com/AWSEC2/latest/UserGuide/ec2-security-groups.html)

## EBS and IP addresses

**Elastic Block Store (EBS)** supplies persistent block volumes, commonly used as boot disks or data disks. Volumes attach to instances in the same Availability Zone. Unlike temporary instance-store storage, EBS data can survive an instance stop. Snapshots provide point-in-time backups. [AWS: EBS volumes](https://docs.aws.amazon.com/ebs/latest/userguide/ebs-volumes.html)

| IPv4 address | Purpose and lifecycle |
| --- | --- |
| Private IP | Internal communication within the VPC or connected private networks; retained across stop/start. It does not provide direct internet reachability. |
| Automatically assigned public IP | Internet communication when routes and security rules permit it; normally released on stop and replaced on start. |
| Elastic IP | An allocated public IPv4 address that can be retained and reassociated when a stable public address is needed. |

AWS charges for public IPv4 addresses, including Elastic IPs. A public IP alone does not make an instance reachable: its subnet also needs the appropriate Internet Gateway route. [AWS: Instance IP addressing](https://docs.aws.amazon.com/AWSEC2/latest/UserGuide/using-instance-addressing.html)

## Instance lifecycle

```text
launch → pending → running
running → stopping → stopped → pending → running
running/stopped → shutting-down → terminated
```

| Action | Effect |
| --- | --- |
| Reboot | Restarts the OS on the same host; preserves attached storage and IP addresses. |
| Stop/start | Supported for EBS-backed instances; preserves EBS and private IP, but loses instance-store data and may change host/public IP. |
| Hibernate | When supported and configured, saves RAM to the EBS root volume for resumption. |
| Terminate | Permanently removes the instance. Each EBS volume's `DeleteOnTermination` setting determines whether it survives; the root volume is normally deleted. |

Stopped instances do not accrue running-instance usage charges, but retained storage and other billable resources can still incur charges. [AWS: Instance lifecycle](https://docs.aws.amazon.com/AWSEC2/latest/UserGuide/ec2-instance-lifecycle.html)

Research notes checked against official AWS documentation on 7 October 2026; no instance launch or lifecycle action is claimed here.

[Back to homework](../../README.md)
