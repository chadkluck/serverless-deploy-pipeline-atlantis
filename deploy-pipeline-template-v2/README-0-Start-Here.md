# Start Here

## IAM Policy and Role

You will need an IAM policy and role (CloudFormation-Service-Role) in order for your deploy pipeline to function.

The policy template to use is included in the [iam policy template directory](./iam-policy-template/ATLANTIS-CloudFormationServicePolicy.json).

[README 1 IAM Policies](./README-1-IAM-Policies.md) will walk you through creating the policy and CloudFormation Service Role that will give your deploy stack the proper permissions.

You only need to do this once for any number of pipelines.

## Create a CodeCommit Repository

Place the entire contents of the [application infrastructure sample code](../application-infrastructure-sample-code/) into a new CodeCommit repository. Use the sample code given here for your first test. You can use more advanced templates later. 

[README 2: CodeCommit Repository](./README-2-CodeCommit-Repository.md) will walk you through this.

> **TIP:** I typically save a copy of the pipeline-toolchain.yml file in the root of the CodeCommit Respository. This is helpful if you make any customizations or wish to add default values to the parameters. While commiting changes to the toolchain file will not refresh the Deploy stack, it may be helpful to have a local copy.

## Create the Deploy Pipeline Stack in CloudFormation

Use the [Pipeline Toolchain YAML CloudFormation template](./pipeline-toolchain.yml) to manually create a new deploy stack.

[README 3: CloudFormation Deploy Stack](./README-3-CloudFormation-Deploy-Stack.md) 

If you wish to use the CLI, instructions will be made available in the future, however you may find [the CLI directory](./cli/) useful (though currently out of date).

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
