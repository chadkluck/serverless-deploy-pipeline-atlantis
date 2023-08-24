# Deleting

You may want to delete stacks you created, however this is an order to deletion.

1. Empty any S3 buckets created by your infrastructure template
2. Delete the infrastructure stack
3. Delete the deploy stack

Failure to delete in this order will cause errors.

## Leaving the Deploy Stack

For non-production environments you may wish to delete the infrastructure stack yet leave the deploy stack available for any future code changes you may push through the pipeline. Deleting unused infrastructure stacks can save money when they incorporate resources that are billed by number and not by usage. (For example CloudWatch Dashboards and Alarms.)

Once an infrastructure stack is deleted it may be rebuilt by either:

1. Going into the associated CodePipeline and choosing "Release change".
2. Committing a code change to the associated branch in your repository.

Releasing a change will rerun the last code commited to the repository branch.

> **NOTE:** Some resources may not have the same name and arn as before which is usually not an issue in Development or Test environments. However, API GateWay will regenerate a random ID for the endpoint so you will need to update the domain of the endpoint you use for testing.

## Documentation

- [README 0 Start Here](./README-0-Start-Here.md)
- [README 1 Create IAM CloudFormation Service Role](./README-1-IAM-CloudFormation-Service_Role.md)
- [README 2 Create CodeCommit Repository](./README-2-CodeCommit-Repository.md)
- [README 3 Create and Update CloudFormation Deploy Pipeline Stack](./README-3-CloudFormation-Deploy-Stack.md)
- [README 4 Tutorial](./README-4-Tutorial.md)
- [README 5 Advanced](./README-5-Advanced.md)
- **README 6 Deleting**
- [README 7 CLI (Create Stack from AWS Command Line Interface)](./README-7-CLI.md)
- [CHANGELOG - Updates to Existing Deploy Stacks](../CHANGELOG.md)
