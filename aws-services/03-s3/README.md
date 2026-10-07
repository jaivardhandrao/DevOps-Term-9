# Amazon S3 — Storage

- **Name:** Jaivardhan D. Rao
- **Enrollment number:** 24BCS10117
- **Status:** Study notes complete. Examples are conceptual; no AWS resources were created or tested.
- **Documentation checked:** 7 October 2026.

## What is S3?

Amazon Simple Storage Service (S3) stores data as objects. Applications upload and retrieve
objects through APIs without managing a storage server. These notes focus on general purpose
buckets. [AWS: What is Amazon S3?](https://docs.aws.amazon.com/AmazonS3/latest/userguide/Welcome.html)

## Buckets and objects

| Term | Meaning | Example |
| --- | --- | --- |
| Bucket | A container for objects, created in an AWS Region; settings control access and data management. | A bucket dedicated to coursework files. |
| Object | The stored data plus metadata. Its key identifies it within the bucket. | A PDF with the key `assignments/report.pdf`. |
| Prefix | The beginning of an object key used to group objects. In a general purpose bucket, a displayed folder is a naming convention. | `assignments/` groups related keys. |

A bucket and key identify an object; versioned objects also have a version ID.
[AWS: S3 concepts](https://docs.aws.amazon.com/AmazonS3/latest/userguide/Welcome.html#CoreConcepts)

## Storage classes

Choose a class by access frequency, retrieval delay, and resilience requirements.
The main choices below are summarized from [AWS's storage-class comparison](https://docs.aws.amazon.com/AmazonS3/latest/userguide/storage-class-intro.html#sc-compare).

| Class | Suitable data and tradeoff |
| --- | --- |
| S3 Standard | Frequently accessed files with millisecond retrieval. |
| S3 Intelligent-Tiering | Unpredictable access; automatically changes access tiers and has monitoring charges. Optional archive tiers require restoration. |
| S3 Standard-IA | Infrequently read data needing immediate access; retrieval fees apply. |
| S3 One Zone-IA | Re-creatable, infrequently read data; stored in one Availability Zone and not resilient to losing that zone. |
| S3 Glacier Instant Retrieval | Archive data that still needs millisecond reads; retrieval fees apply. |
| S3 Glacier Flexible Retrieval | Archives that can wait minutes to hours for restoration. |
| S3 Glacier Deep Archive | Long-term archives that can wait hours for restoration. |
| S3 Express One Zone | Latency-sensitive workloads in directory buckets; data remains in one Availability Zone. |

Storage cost alone is insufficient: minimum storage durations and retrieval charges can make
frequent access or early deletion expensive. [AWS: Storage classes](https://docs.aws.amazon.com/AmazonS3/latest/userguide/storage-class-intro.html)

## Versioning

Versioning retains multiple versions of the same key. After enabling it, overwriting
`report.pdf` creates a new version while preserving the earlier one. A delete without a
version ID adds a delete marker, allowing recovery; deleting a specific version can remove
it permanently. Each retained version incurs storage charges. Versioning starts disabled
and can be suspended after activation, but the bucket cannot return to an unversioned state.
[AWS: S3 Versioning](https://docs.aws.amazon.com/AmazonS3/latest/userguide/Versioning.html),
[AWS: Deleting objects and versions](https://docs.aws.amazon.com/AmazonS3/latest/userguide/delete-multiple-objects.html)

## Lifecycle policies

A lifecycle configuration automates retention with two main actions: **transition** objects
to another storage class and **expire** objects when no longer needed. Rules also affect
matching objects already in the bucket. For example, a log-retention design could transition
older logs to an archive class and expire them after the required retention period.
[AWS: Object lifecycle](https://docs.aws.amazon.com/AmazonS3/latest/userguide/object-lifecycle-mgmt.html)

In a versioned bucket, expiring the current object does not automatically erase its older
versions. Noncurrent-version expiration needs its own configuration.
[AWS: Versioning with Lifecycle](https://docs.aws.amazon.com/AmazonS3/latest/userguide/Versioning.html#VersioningOverviewLifecycle)

## Encryption

- **In transit:** use HTTPS/TLS to protect data travelling to and from S3.
- **At rest:** new uploads receive server-side encryption automatically; SSE-S3 uses keys managed by S3.
- **Other choices:** SSE-KMS uses AWS KMS keys; DSSE-KMS provides two encryption layers. Client-side encryption encrypts data before upload.
- Changing a bucket's default encryption does not rewrite existing objects with the new encryption type.

[AWS: Protecting data with encryption](https://docs.aws.amazon.com/AmazonS3/latest/userguide/UsingEncryption.html)

## Bucket policies

A bucket policy is a JSON resource policy. It identifies the principal, allowed or denied
actions, resources, and optional conditions. For example, it can grant a specific application
role read access to a prefix or reject requests that do not use TLS. Encryption protects data;
permissions decide who can access it. [AWS: Bucket policies](https://docs.aws.amazon.com/AmazonS3/latest/userguide/bucket-policies.html)

Keep Block Public Access enabled for private coursework data. It helps prevent public grants
through bucket policies or ACLs. [AWS: Block Public Access](https://docs.aws.amazon.com/AmazonS3/latest/userguide/access-control-block-public-access.html)

## Common use cases

S3 fits backups, long-term archives, application uploads, static assets, and data lakes for
analytics. An example student application could keep uploaded images in S3, store their keys
in a database, and apply a retention policy to temporary uploads.
[AWS: S3 use cases](https://aws.amazon.com/s3/)
