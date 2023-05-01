# IAM Policy Templates

Refer to [README 1 - IAM Policies](../README-1-IAM-Policies.md) for setting up required IAM Roles and Policies.

These are IAM policy templates to attach to service roles.

When you create a Deploy Stack you must provide a Service Role. This role is assumed by CloudFormation to create and update resources in the Application Infrastructure stack as it moves through the deployment pipeline.

IAM Service Roles only need to be created once and can be re-used for any project using the same prefix (such as `awscodestar-*`, `projectstack-*`, or your own custom prefix).

## Separating Projects and Development Teams with Custom Prefixes

If you create your own prefix you will need to create a new Service Role for that prefix. Make a copy of ProjectStackServicePolicy.json and ProjectStackTaggingPolicy.json and replace references in Resources to `projectstack` with `yourcustom` prefix.

Then create a new service role for that prefix and attach the service and tagging policies.

In the example below a new tagging policy replaces `projectstack` with `websvc`. This can help distinguish and separate permissions between different development teams.

```json
"Resource": [
	"arn:aws:iam::*:role/projectstackWorker*",
	"arn:aws:iam::*:policy/projectstackWorker*",
	"arn:aws:iam::*:instance-profile/projectstack-*"
]

// Replace 'projectstack' with 'websvc':

"Resource": [
	"arn:aws:iam::*:role/websvcWorker*",
	"arn:aws:iam::*:policy/websvcWorker*",
	"arn:aws:iam::*:instance-profile/websvc-*"
]			
```
