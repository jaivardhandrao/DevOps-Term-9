# IAM — Governance and access

AWS Identity and Access Management (IAM) controls who can use AWS resources and which actions they can perform. **Authentication** establishes the caller's identity; **authorization** checks whether the requested action is permitted. [AWS: What is IAM?](https://docs.aws.amazon.com/IAM/latest/UserGuide/introduction.html)

## Users, groups and roles

| Concept | Meaning | Example |
| --- | --- | --- |
| IAM user | An identity in one AWS account. It can have a console password or long-term access keys. | A legacy integration that cannot use temporary credentials. |
| IAM group | A collection of IAM users that share attached permission policies. Groups cannot sign in, contain roles, or contain other groups. | Apply the same support permissions to several existing IAM users. |
| IAM role | An identity that a trusted caller assumes to receive temporary credentials. It has no permanent password or access keys. | Give an EC2 application access to an S3 bucket. |

A role's **trust policy** specifies who may assume it; its **permissions policies** specify what the role can do. AWS recommends federation and temporary credentials for people and workloads wherever possible. [AWS: Users](https://docs.aws.amazon.com/IAM/latest/UserGuide/id_users.html), [groups](https://docs.aws.amazon.com/IAM/latest/UserGuide/id_groups.html), [roles](https://docs.aws.amazon.com/IAM/latest/UserGuide/id_roles.html)

## Policies and permissions

A permission is authorization to perform an action on a resource. A policy is the document expressing that authorization, usually in JSON. Identity policies attach to users, groups or roles; resource policies attach to resources such as S3 buckets.

Important policy fields are `Effect` (`Allow` or `Deny`), `Action`, `Resource`, and optional `Condition`. Resource policies also identify the `Principal`. A managed policy can be reused across identities; an inline policy belongs to one identity. [AWS: Policies and permissions](https://docs.aws.amazon.com/IAM/latest/UserGuide/access_policies.html)

Requests need an applicable allow, and an applicable explicit deny overrides an allow. Permissions boundaries and organization policies can further restrict access; attaching one permissive policy does not bypass them. [AWS: Policy evaluation](https://docs.aws.amazon.com/IAM/latest/UserGuide/reference_policies_evaluation-logic.html)

## Least privilege

Grant only the actions, resources and conditions needed for a specific job. For example, an application that downloads one configuration object should not receive administrator access. This illustrative identity policy grants only object retrieval at one placeholder path:

```json
{
  "Version": "2012-10-17",
  "Statement": [{
    "Effect": "Allow",
    "Action": "s3:GetObject",
    "Resource": "arn:aws:s3:::example-course-config/app/config.json"
  }]
}
```

It does not grant bucket listing, uploads or deletion. The complete request still depends on other applicable policies and, for a KMS-encrypted object, relevant key permissions. [AWS: Policies and permissions](https://docs.aws.amazon.com/IAM/latest/UserGuide/access_policies.html)

## Best practices and common use cases

- Use IAM Identity Center/federation for human access and IAM roles for workloads.
- Require MFA, protect the root identity, and reserve root access for tasks that require it.
- Start with narrowly scoped permissions; review unused access and remove unnecessary credentials.
- Validate policies and inspect unintended public or cross-account access with IAM Access Analyzer.
- Keep credentials out of code and use temporary credentials wherever supported.

These practices support separate developer and administrator access, application access to AWS services, and temporary cross-account audit access. [AWS: IAM security best practices](https://docs.aws.amazon.com/IAM/latest/UserGuide/best-practices.html), [role use cases](https://docs.aws.amazon.com/IAM/latest/UserGuide/id_roles.html)

Research notes checked against official AWS documentation on 7 October 2026. The policy above is an example, not a record of an applied account change.

[Back to homework](../../README.md)
