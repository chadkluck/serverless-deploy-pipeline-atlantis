# Deleting and Clean-Up

To delete stacks you created follow the order of these steps:

1. Empty any S3 buckets created by your Infrastructure stack (In the S3 Web Console, select the S3 bucket and choose Empty)
2. Empty the S3 deploy bucket created to store artifacts by your Pipeline stack.
3. Delete the infrastructure stack through the CloudFormation web console
4. Delete the Pipeline stack through the CloudFormation web console

Failure to follow this order will cause errors. For example, deleting the Pipeline stack first will remove the IAM roles needed to delete the infrastructure stack. Not emptying an S3 bucket will prevent the Delete Stack operation from completing as non-empty buckets cannot be deleted.

## Leaving the Deploy Stack

For non-production environments you may wish to delete the infrastructure stack yet leave the deploy stack available for any future code changes you may push through the pipeline. Deleting unused infrastructure stacks can save money when they incorporate resources that are billed by month and not by usage. (For example CloudWatch Dashboards and Alarms.)

Once an infrastructure stack is deleted it may be rebuilt by either:

1. Going into the associated CodePipeline and choosing "Release change".
2. Committing a code change to the associated branch in your repository.

Releasing a change will rerun the last code committed to the repository branch.

> **NOTE:** Some resources may not have the same name and arn as before which is usually not an issue in Development or Test environments. However, API GateWay will regenerate a random ID for the endpoint so you will need to update anywhere you use the endpoint.
