# Deleting

You may want to delete stacks you created, however there is a proper order to follow:

1. Empty any S3 buckets created by your infrastructure template
2. Delete the infrastructure stack
3. Delete the deploy stack

Failure to follow this order will cause errors.

## Leaving the Deploy Stack

For non-production environments you may wish to delete the infrastructure stack yet leave the deploy stack available for any future code changes you may push through the pipeline. Deleting unused infrastructure stacks can save money when they incorporate resources that are billed by number and not by usage. (For example CloudWatch Dashboards and Alarms.)

Once an infrastructure stack is deleted it may be rebuilt by either:

1. Going into the associated CodePipeline and choosing "Release change".
2. Committing a code change to the associated branch in your repository.

Releasing a change will rerun the last code committed to the repository branch.

> **NOTE:** Some resources may not have the same name and arn as before which is usually not an issue in Development or Test environments. However, API GateWay will regenerate a random ID for the endpoint so you will need to update the domain of the endpoint you use for testing.

## Documentation


