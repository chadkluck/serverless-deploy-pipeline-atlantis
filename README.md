# CloudFormation Template for CI/CD using AWS Code Pipeline

This CloudFormation template will create an automated deployment pipeline when changes are committed to a monitored CodeCommit branch.

Each branch will have its own deploy stack and application infrastructure stack. This allows you to separate dev, test, prod, grant developer access via CodeCommit policies, and create or destroy test and staging branches/pipelines as necessary.

## Pros to using a template like this:

- Precisely scoped IAM Policies and Roles are created for you (more secure, principle of least privilege)
- Structured naming and tagging (better organization)
- No need to start from scratch
- No reason to create a messy application base and say "I'll structure, organize, and add security controls later"

## Cons to using a template like this:

- You need to understand someone else's code
- It stifles your creativity

However, I do believe that the cons are only temporary and I set the toolchain up as a learning experience. As you begin to look under the hood you can use it as a model for learning AWS Cloud Concepts such as Infrastructure as Code (IaC), CloudFormation, AWS CodePipeline, and serverless architecture. Once you have played around with it, the sky is the limit as you add your own modifications for your own use case.

## Important Files

### Deploy Pipeline IAM Policy Template for CloudFormation Service Role

[deploy-pipeline/iam-policy-template/ATLANTIS-CloudFormationServicePolicy.json](./deploy-pipeline/iam-policy-template/ATLANTIS-CloudFormationServicePolicy.json)

The IAM policy template for the necessary CloudFormation Service Role. You will need to add in some details using a search/replace as instructed in [README 1 Create IAM CloudFormation Service Role](./iam-cloudformation-service-role/README-IAM-CF-Service-Role.md).

### Application Infrastructure Code in CodeCommit

[Sample code for your Application Infrastructure](./application-infrastructure-sample-code/) is available to seed your CodeCommit Repository. Use the sample code for your initial experiments, tutorials, and as a template for structuring your own code to work with the pipeline. (Basically setting up the proper parameters and tags to allow the deploy pipeline to work its magic.)

[README 2 Create CodeCommit Repository](deploy-pipeline/README-2-CodeCommit-Repository.md) goes over creating the CodeCommit repository and branch to deploy from.

### Deploy Pipeline CloudFormation Template

[deploy-pipeline/pipeline-toolchain.yml](./deploy-pipeline/pipeline-toolchain.yml)

The CloudFormation template you will be using to create the Deploy Stack which creates and manages the AWS Code Pipeline. It will utilize the CloudFormation Service Role you created. The Code Pipeline is what builds and deploys your infrastructure stack.

Utilize either the template in the public 63klabs S3 bucket, upload to your own bucket, or upload using the AWS CloudFormation Web Console. Follow the instructions in [README 3 Create and Update CloudFormation Deploy Pipeline Stack](deploy-pipeline/README-3-CloudFormation-Deploy-Stack.md).

## Modify to Suit Your Needs

Once an understanding of the `pipeline-toolchain.yml`, `application-infrastructure-sample-code/template.yml`, and IAM policy and role is achieved, they can all be modified to extend a project or application infrastructure to use any AWS resource. As demonstrated in the tutorial, the templates are simple and easy to use to create and re-create sandboxes for experiementation or move from development to production.

The application deployed in the tutorials deviates from the traditional "Hello World" example as instead it returns JSON formatted predictions. It is an extention of the [Serverless SAM 8-Ball example](https://github.com/chadkluck/serverless-sam-8ball-example) which I highly recommend checking out for the sake of learning more about the Serverless Application Model, Lambda, and API Gateway.

To deploy application infrastructure and code changes all you need to do is commit to a monitored branch of the repository.

Before skipping over the tutorials you'll need to make sure you have set up the required IAM Role and CodeCommit repository [Refer to documentation](deploy-pipeline/README-0-Start-Here.md).

## AWS Costs

This deploy template will create resources necessary to provide an AWS CodePipeline. After performing any tutorials you will want to delete unused stacks so that you do not incur any unexpected costs. However, most experimentation, and even low production loads, rarely rise above [AWS Free Tier](https://aws.amazon.com/free).

> You get 1 free active pipeline per month. New pipelines are free for the first 30 days. "An active pipeline is a pipeline that has existed for more than 30 days and has at least one code change that runs through it during the month. There is no charge for pipelines that have no new code changes running through them during the month." [CodePipeline Pricing](https://aws.amazon.com/codepipeline/pricing)

You are also charged for AWS CodeBuild if you go over 100 build minutes per month. [CodeBuild Pricing](https://aws.amazon.com/codebuild/pricing)

To delete the stacks and resources refer to [README 6: Deleting](deploy-pipeline/README-6-Deleting.md).

## Documentation

README 0 through 3 will get you started quickly as they walk you through setting up the required IAM Policy and Role, CodeCommit Repository for your application's code, and CloudFormation Deploy Stack.

README 4 through 7 will guide you through advanced concepts with a tutorial and additional information about deleting stacks and using the AWS CLI to create stacks.

- [README 0 Start Here](deploy-pipeline/README-0-Start-Here.md)
- [README 1 Create IAM CloudFormation Service Role](deploy-pipeline/README-1-IAM-CloudFormation-Service_Role.md)
- [README 2 Create CodeCommit Repository](deploy-pipeline/README-2-CodeCommit-Repository.md)
- [README 3 Create and Update CloudFormation Deploy Pipeline Stack](deploy-pipeline/README-3-CloudFormation-Deploy-Stack.md)
- [README 4 Tutorial](deploy-pipeline/README-4-Tutorial.md)
- [README 5 Advanced](deploy-pipeline/README-5-Advanced.md)
- [README 6 Deleting](deploy-pipeline/README-6-Deleting.md)
- [README 7 CLI (Create Stack from AWS Command Line Interface)](deploy-pipeline/README-7-CLI.md)
- [CHANGELOG - Updates to Existing Deploy Stacks](CHANGELOG.md)
