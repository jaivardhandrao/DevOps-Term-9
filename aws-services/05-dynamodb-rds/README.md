# DynamoDB and RDS — Database services

## DynamoDB and NoSQL

Amazon DynamoDB is a managed, serverless NoSQL database supporting key-value and document data. AWS manages the underlying servers. Its design is useful when an application knows how it will look up data and needs scalable, low-latency access. NoSQL does not mean that data has no structure: the application still needs a suitable key design. [AWS: What is DynamoDB?](https://docs.aws.amazon.com/amazondynamodb/latest/developerguide/Introduction.html)

| Component | Meaning |
| --- | --- |
| Table | Collection of related items, such as `Orders`. |
| Item | One record in a table. |
| Attribute | A named value in an item, such as `status` or `total`. Non-key attributes can vary between items. |
| Partition key | Required primary-key component. Its value is hashed to determine data placement. With a simple primary key, this value must be unique. |
| Sort key | Optional second primary-key component. With a composite key, items can share a partition key but must have distinct sort keys. It supports ordered/range queries within that partition-key value. |

For example, an `Orders` table could use `customer_id` as the partition key and `order_id` as the sort key. The pair identifies an order; querying a customer retrieves that customer's orders. [AWS: Core components](https://docs.aws.amazon.com/amazondynamodb/latest/developerguide/HowItWorks.CoreComponents.html)

Choose partition keys that spread activity across many values to avoid concentrating traffic on a few keys. Design around access patterns before importing relational-style tables. [AWS: Partition-key design](https://docs.aws.amazon.com/amazondynamodb/latest/developerguide/bp-partition-key-design.html)

Example uses include shopping carts, session records, game-player state and device-event lookups. These are a good fit when key-based access matches the application; complex arbitrary joins usually suggest a relational design instead. [AWS: DynamoDB overview](https://docs.aws.amazon.com/amazondynamodb/latest/developerguide/Introduction.html)

## RDS and relational databases

Amazon Relational Database Service (RDS) manages database infrastructure and tasks such as backups and maintenance. A relational database stores rows in tables with defined columns and relationships, and supports SQL queries and transactions. Applications still own their schema, queries and data permissions.

A **DB instance** supplies the database engine, compute/memory capacity, storage and connection endpoint. The instance class determines capacity; it is separate from the engine and version. Standard RDS engines are **IBM Db2, MariaDB, Microsoft SQL Server, MySQL, Oracle Database and PostgreSQL**. Availability and features depend on engine, version and Region. [AWS: RDS overview and engines](https://docs.aws.amazon.com/AmazonRDS/latest/UserGuide/Welcome.html)

**Amazon Aurora** is also part of the RDS service family, with MySQL-compatible and PostgreSQL-compatible engines and its own cluster architecture. It should not be confused with ordinary RDS MySQL/PostgreSQL instances. [AWS: Aurora overview](https://docs.aws.amazon.com/AmazonRDS/latest/AuroraUserGuide/CHAP_AuroraOverview.html)

## RDS security and backups

Place application databases in private subnets and allow the database port only from the application Security Group. Use database users with limited privileges, TLS for connections, and encryption at rest. IAM controls AWS resource-management access; database authentication and SQL privileges are separate concerns, with IAM database authentication available for supported engines. [AWS: RDS security](https://docs.aws.amazon.com/AmazonRDS/latest/UserGuide/UsingWithRDS.html)

**Automated backups** support point-in-time recovery within the configured retention period. **Manual snapshots** capture a chosen recovery point and remain until explicitly deleted. Restore procedures should be tested: having a backup alone does not demonstrate that an application can recover successfully. [AWS: RDS backups](https://docs.aws.amazon.com/AmazonRDS/latest/UserGuide/USER_WorkingWithAutomatedBackups.html), [DB snapshots](https://docs.aws.amazon.com/AmazonRDS/latest/UserGuide/USER_CreateSnapshot.html)

## Multi-AZ and read replicas

| Deployment | Purpose | Important distinction |
| --- | --- | --- |
| Multi-AZ DB instance | Availability and automatic failover | Synchronously maintains a standby in another Availability Zone. That standby does not serve application read queries. |
| DB instance read replica | Scale read-heavy workloads or support recovery designs | Replicates asynchronously, so reads can lag behind the writer. Applications must connect to the replica to use its read capacity. Engine-specific restrictions apply. |
| Multi-AZ DB cluster | Availability plus readable replicas | One writer and two readers across three Availability Zones; uses semisynchronous replication. This is a different deployment model from a single-standby Multi-AZ instance and from Aurora. |

See AWS documentation for [Multi-AZ instances](https://docs.aws.amazon.com/AmazonRDS/latest/UserGuide/Concepts.MultiAZSingleStandby.html), [read replicas](https://docs.aws.amazon.com/AmazonRDS/latest/UserGuide/USER_ReadRepl.html), and [Multi-AZ clusters](https://docs.aws.amazon.com/AmazonRDS/latest/UserGuide/multi-az-db-clusters-concepts.html). Replication and failover do not replace backups: unwanted data changes can also replicate.

RDS suits an order-processing system joining customers, orders and payments, or an existing SQL application needing a managed database. A reporting workload can use a read replica if some replication delay is acceptable. DynamoDB suits predictable key-based lookups with flexible item attributes; RDS suits relational queries and constraints. These are design examples, not deployed services.

Research notes checked against official AWS documentation on 7 October 2026.

[Back to homework](../../README.md)
