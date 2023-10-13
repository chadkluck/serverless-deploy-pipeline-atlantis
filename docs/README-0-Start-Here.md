# Start Here

A series of READMEs will walk you through the 3 concepts to get you started:

1. Create an IAM Role for your CloudFormation Service
2. Create a CodeCommit repository you will store your code in
3. Create a CloudFormation stack that will create an AWS CodePipeline to deploy your code

This will begin your wonderful journey into Infrastructure as Code (IaC) and Continuous Integration and Continuous Deployment (CI/CD) pipelines.

Enjoy!

## IAM CloudFormation Service Role

An IAM CloudFormation Service Role is necessary in order for your deploy stack to create pipeline resources.

You will first create a policy and then attach it to the new service role.

The policy template is included in the [iam service role directory](../iam-cloudformation-service-role/ATLANTIS-CloudFormationServicePolicy.json).

[README 1: IAM CloudFormation Service Role](../iam-cloudformation-service-role/README-1-IAM-CF-Service-Role.md) will walk you through creating the policy and attaching it to a CloudFormation Service Role.

You only need to do this once for any number of pipelines. You can also create a service role for each unit, team, or department in your organization to separate permissions.

## Create a CodeCommit Repository

Place the entire directory and contents of the [application infrastructure sample code](../application-infrastructure/) into a new CodeCommit repository. Use the sample code given here for your first test. You can use more advanced templates later. 

[README 2: CodeCommit Repository](./README-2-CodeCommit-Repository.md) will walk you through this.

## Create the Deploy Pipeline Stack in CloudFormation

Use the [Pipeline Toolchain YAML CloudFormation template](./pipeline-toolchain.yml) to manually create a new deploy stack.

[README 3: CloudFormation Deploy Stack](./README-3-CloudFormation-Deploy-Stack.md) 

If you wish to use the AWS CLI you will find instructions in [README 7: CLI](./README-7-CLI.md).

Once the Deploy stack is created it will automatically grab your code from the repository branch and create the Infrastructure stack.

## Make Application Code Changes

Make sure your application infrastructure deployed correctly and use the test link listed in the infrastructure's Output section. To deploy changes, all you need to do is commit to the monitored branch and CodePipeline will take care of the rest!

[README 4: Tutorial](./README-4-Tutorial.md) will walk you through a tutorial to introduce you to the deploy and infrastructure stack as well as create additional deploy stacks for testing.

[README 5: Advanced](./README-5-Advanced.md) goes over advanced concepts.

## Customize the Pipeline Toolchain

If you need to modify the way the CodePipeline performs (maybe you need to give it permissions to create infrastructure stacks with EC2 instances or VPCs), update the pipeline-toolchain.yml and then perform a manual stack update in CloudFormation.

The following READMEs will be helpful.

- [README 3: CloudFormation Deploy Stack](./README-3-CloudFormation-Deploy-Stack.md)
- [README 5: Advanced](./README-5-Advanced.md) goes over advanced concepts.

## Deleting Stacks

To conserve resources of unused stacks or to "start over" with a mangled stack, you will want to delete stacks.

[README 6: Deleting](./README-6-Deleting.md)

## Use the CLI to Create Stacks

To assist with entering parameters and tags for your CloudFormation deploy stack, a [project configuration JSON file](./cli/config-stack.json) and `generate.py` Python script is included in the [CLI directory](./cli/).

Filling in the information and running the script will give you all you need to run a `aws cloudformation create-stack` command from the AWS Command Line Interface without having to go through the console.

Make sure you have AWS CLI installed and the proper credentials and role to submit `create-stack` commands.

[README 7: CLI](./README-7-CLI.md)
