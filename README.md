# CloudFormation Template for CI/CD using AWS Code Pipeline

## About

This CloudFormation template will create an AWS CodePipeline that monitors a single CodeCommit branch for changes and then deploys the application to a separate application infrastructure stack. It is recommended that you familiarize yourself with CloudFormation, CloudFormation templates, and CodePipeline.

Each branch will have its own deploy stack and application infrastructure stack. This allows you to separate dev, test, prod, grant developer access via CodeCommit policies, and create or destroy temporary or per-developer/feature test and staging branches/pipelines as necessary.

- The Deploy CloudFormation stack template creates the Pipeline and resources for the pipeline to operate (such as IAM roles and S3 artifact buckets). It only runs when you need to make changes to HOW the Pipeline works.
- The AWS CodePipeline receives an event notification from the repository branch and builds and deploys the application infrastructure template.
- The CloudFormation Infrastructure stack manages actual application resources.

The templates, documentation, and tutorials were created by an AWS Certified developer in hopes to bridge the gap between quick-start online examples and well-architected production-ready applications. The template is actively used in production and receives periodic updates for security and best practices from AWS.

This template can serve as a base or example template as you modify it to meet your needs. It is developed with the Principle of Least Privilege, and can deploy applications that utilize S3, DynamoDb, Lambda, API Gateway, CloudWatch Logs, Alarms, and Dashboards right out of the box. The templates can be extended to meet your needs simply by adding the appropriate IAM policies to the CloudFormation Role. For example, your developers cannot add Event Bridge or EC2 instances to their application infrastructure unless you first add the appropriate IAM policies to the CodePipeline Cloud Formation Role.

As you begin to look under the hood you can use it as a model for learning AWS Cloud Concepts such as Infrastructure as Code (IaC), CloudFormation, AWS CodePipeline, and serverless architecture. Once you have played around with it, the sky is the limit as you add your own modifications for your own use case.

### Pros to using a template like this:

- Precisely scoped IAM Policies and Roles are created for you, your team, and application (more secure, principle of least privilege)
- Structured naming and tagging (better organization)
- No need to start from scratch
- No reason to create a messy application base and say "I'll structure, organize, and add security controls later"
- Provides a tutorial for creating production-ready applications rather than examples pieced together

## Usage

### File Structure

There are 3 main directories in the root of this repository.

```text
/
| - application-infrastructure/
|   | - app/
|   | - buildspec.yml
|   | - template-configuration.json
|   | - template.yml
| 
| - deploy-pipeline/
|   | - scripts-cli/
|   | - pipeline-toolchain.yml
|
| - iam-cloudformation-service-role/
    | - scripts-cli/
    | - CloudFormationServicePolicy.json
```

#### Application Infrastructure directory

This is where your application CloudFormation template and code reside. This entire directory needs to be placed at the root of your repository. CodePipeline will look for `/application-infrastructure/` when executing.

AWS pipeline will use the `buildspec.yml` to run the build and then the CloudFormation template `template.yml` to deploy an application infrastructure stack.

The buildspec and template files are structured to receive environment variables to execute logic based on whether it is building a DEV, TEST, or PROD environment. You will not need separate buildspec files (such as `buildspec-test.yml`) for each environment. Utilize parameters and environment variables.

#### Deploy Pipeline directory

This contains `pipeline-toolchain.yml` which is the CloudFormation template that defines the CloudFormation stack which creates and maintains the AWS CodePipeline. This can be kept in the application repository, or moved to where your organization stores and maintains cloud infrastructure templates (such as Terraform or AWS CDK scripts). You can convert the pipeline to a Terraform or CDK script, upload it through the console, or use the AWS CLI.

The pipeline toolchain is also available from a public S3 bucket if you wish to use the latest version as-is.

There is a `scripts-cli/` directory that assists in generating input.json files for use with the AWS CLI rather than uploading the template through the web console.

#### CloudFormation Service Role directory


## AWS Costs

This deploy template will create resources necessary to provide an AWS CodePipeline. After performing any tutorials you will want to delete unused stacks so that you do not incur any unexpected costs. However, most experimentation, and even low production loads, rarely rise above [AWS Free Tier](https://aws.amazon.com/free).

> You get 1 free active pipeline per month. New pipelines are free for the first 30 days. "An active pipeline is a pipeline that has existed for more than 30 days and has at least one code change that runs through it during the month. There is no charge for pipelines that have no new code changes running through them during the month." [CodePipeline Pricing](https://aws.amazon.com/codepipeline/pricing)

In short: Pipelines can sit idle without incurring any cost.

You are also charged for AWS CodeBuild if you go over 100 build minutes per month. If you are committing and deploying only a few changes a month you should not see any charges for CodeBuild. If you are frequently committing changes for deployment several times a day, several days a week during the month, you may see charges. [CodeBuild Pricing](https://aws.amazon.com/codebuild/pricing)

To delete the stacks and resources refer to the Clean Up section.

### Quick Start


### Deploy Pipeline IAM Policy Template for CloudFormation Service Role

[deploy-pipeline/iam-policy-template/ATLANTIS-CloudFormationServicePolicy.json](./iam-cloudformation-service-role/ATLANTIS-CloudFormationServicePolicy.json)

The IAM policy template for the necessary CloudFormation Service Role. You will need to add in some details using a search/replace as instructed in [README 1 Create IAM CloudFormation Service Role](./iam-cloudformation-service-role/README-1-IAM-CF-Service-Role.md).

Why this is important: If you have ever created resources via the AWS Console, you may have had to create, or check a box to automatically create, a service role for the resource to operate. This Service Role will be the one used by your CloudFormation stack when it deploys your infrastructure. As such, it needs the necessary permissions to create and manage the necessary resources for your application. Some basic permissions have been added to get you started (DynamoDb, S3, Lambda, etc.). As you expand the resources you require you may add them to the service role.

### Application Infrastructure Code in CodeCommit

[Application Infrastructure](./application-infrastructure/) is available to seed your CodeCommit repository. Use the sample code for your initial experiments, tutorials, and as a template for structuring your own code to work with the pipeline. (Basically setting up the proper parameters and tags to allow the deploy pipeline to work its magic.)

Make sure the `/application-infrastructure` directory stays in the root of your repository or Code Pipeline will not know where to find your code! (Unless you know how to update the locations in the deploy pipeline template)

[README 2 Create CodeCommit Repository](/codecommit-repository/README-2-CodeCommit-Repository.md) goes over creating the CodeCommit repository and branch to deploy from.

### Deploy Pipeline CloudFormation Template

[deploy-pipeline/pipeline-toolchain.yml](./deploy-pipeline/pipeline-toolchain.yml)

This is the CloudFormation template you will be using to create the Deploy Stack which creates and manages the AWS Code Pipeline. It will utilize the CloudFormation Service Role you created. The Code Pipeline is what builds and deploys your infrastructure stack.

Utilize either the template in the public 63klabs S3 bucket, upload to your own bucket, or upload using the AWS CloudFormation Web Console. Follow the instructions in [README 3 Create and Update CloudFormation Deploy Pipeline Stack](deploy-pipeline/README-3-CloudFormation-Deploy-Stack.md).

You can keep the toolchain in your repository, or move/convert to a central repository your organization uses to manage infrastructure. You may find the need to convert it to a Terraform template or AWS CDK.

## Modify to Suit Your Needs

Once an understanding of the `pipeline-toolchain.yml`, `application-infrastructure/template.yml`, and IAM policy and role is achieved, they can all be modified to extend a project or application infrastructure to use any AWS resource. As demonstrated in the tutorial, the templates are simple and easy to use to create and re-create sandboxes for experimentation or move from development to production.

The application deployed in the tutorials deviates from the traditional "Hello World" example as instead it returns JSON formatted predictions. It is an extension of the [Serverless SAM 8-Ball example tutorial](https://github.com/chadkluck/serverless-sam-8ball-example) which I highly recommend checking out for the sake of learning more about the Serverless Application Model, Lambda, and API Gateway.

To deploy application infrastructure and code changes all you need to do is commit to a monitored branch of the repository.

Before skipping over the tutorials you'll need to make sure you have set up the required IAM Role and CodeCommit repository [Refer to documentation](./docs/README-0-Start-Here.md).

## AWS Costs

This deploy template will create resources necessary to provide an AWS CodePipeline. After performing any tutorials you will want to delete unused stacks so that you do not incur any unexpected costs. However, most experimentation, and even low production loads, rarely rise above [AWS Free Tier](https://aws.amazon.com/free).

> You get 1 free active pipeline per month. New pipelines are free for the first 30 days. "An active pipeline is a pipeline that has existed for more than 30 days and has at least one code change that runs through it during the month. There is no charge for pipelines that have no new code changes running through them during the month." [CodePipeline Pricing](https://aws.amazon.com/codepipeline/pricing)

In short: Pipelines can sit idle without incurring any cost.

You are also charged for AWS CodeBuild if you go over 100 build minutes per month. If you are committing and deploying only a few changes a month you should not see any charges for CodeBuild. If you are frequently committing changes for deployment several times a day, several days a week during the month, you may see charges. [CodeBuild Pricing](https://aws.amazon.com/codebuild/pricing)

To delete the stacks and resources refer to [README 6: Deleting](./docs/README-6-Deleting.md).

## Documentation

README 0 through 3 will get you started quickly as they walk you through setting up the required IAM Policy and Role, CodeCommit Repository for your application's code, and CloudFormation Deploy Stack.

README 4 through 6 will guide you through advanced concepts with a tutorial and additional information.

- [README 0: Start Here](./docs/README-0-Start-Here.md)
- [README 1: Create IAM CloudFormation Service Role](./iam-cloudformation-service-role/README-1-IAM-CF-Service-Role.md)
- [README 2: Create CodeCommit Repository](./codecommit-repository/README-2-CodeCommit-Repository.md)
- [README 3: Create and Update Deploy Pipeline CloudFormation Stack](./deploy-pipeline/README-3-CloudFormation-Deploy-Stack.md)
  - [README 3.1: Use AWS CLI to Create and Update Deploy Pipeline CloudFormation Stack](./deploy-pipeline/cli/README-CLI.md)
- [README 4 Tutorial](./docs/README-4-Tutorial.md)
- [README 5: Advanced](./docs/README-5-Advanced.md)
- [README 6: Deleting](./docs/README-6-Deleting.md)
- [CHANGELOG - Updates to Existing Deploy Stacks](CHANGELOG.md)
