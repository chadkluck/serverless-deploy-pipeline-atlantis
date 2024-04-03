# CloudFormation Template for CI/CD using AWS CodePipeline

This CloudFormation template will create an AWS CodePipeline that monitors a single CodeCommit branch for changes and then deploys the application a CloudFormation stack. It is recommended that you familiarize yourself with CloudFormation and CodePipeline.

The intent is to bridge the gap between pieced together tutorials (and solutions from Stack Overflow) and deploying practical, production ready solutions.

- Precisely scoped IAM Policies and Roles are created for you, your team, and application (more secure, principle of least privilege)
- Structured naming and tagging (better organization)
- No need to start from scratch
- No reason to create a messy application base and say "I'll structure, organize, and add security controls later"
- A tutorial for creating production-ready applications rather than examples pieced together

## About

Each branch will have its own pipeline stack and application infrastructure stack. This allows you to separate dev, test, and prod, grant developer access via CodeCommit policies, and create or destroy temporary or per-developer/feature test and staging branches/pipelines as necessary.

As you begin to look under the hood you can use it as a model for learning AWS Cloud Concepts such as Infrastructure as Code (IaC), CloudFormation, AWS CodePipeline, and serverless architecture. Once you have played around with it, the sky is the limit as you add your own modifications for your own use case.

## AWS Costs

This deploy template will create resources necessary to provide an AWS CodePipeline. After performing any tutorials you will want to delete unused stacks so that you do not incur any unexpected costs. However, most experimentation, and even low production loads, rarely rise above [AWS Free Tier](https://aws.amazon.com/free).

> You get 1 free active pipeline per month. New pipelines are free for the first 30 days. "An active pipeline is a pipeline that has existed for more than 30 days and has at least one code change that runs through it during the month. There is no charge for pipelines that have no new code changes running through them during the month." [CodePipeline Pricing](https://aws.amazon.com/codepipeline/pricing)

In short: Pipelines can sit idle without incurring any cost.

You are also charged for AWS CodeBuild if you go over 100 build minutes per month. If you are committing and deploying only a few changes a month you should not see any charges for CodeBuild. If you are frequently committing changes for deployment several times a day, several days a week during the month, you may see charges. [CodeBuild Pricing](https://aws.amazon.com/codebuild/pricing)

To delete the stacks and resources refer to the Clean Up section.

## File Structure

There are 4 main directories in the root of this repository which corresponds to the 4 main steps necessary to get the solution up and running.

```text
/
|- application-infrastructure/
|   |- app/
|   |- buildspec.yml
|   |- template-configuration.json
|   |- template.yml
| 
|- cloudformation-pipeline-template/
|   |- template-pipeline.yml
|
|- iam-cloudformation-service-role/
|   |- SAMPLE-CloudFormationServicePolicy.json
|   |- Trust-Policy-for-Service-Role.json
|
|- scripts-cli/
|   |- settings/
|   |- cli/
|   |- pipeline-stack.py
|   |- service-role.py
```

Recommended practice is that you separate this into two repositories. One for your application infrastructure, and another for your development operations.

Application Repository:

```text
/
|- application-infrastructure/
|   |- app/
|   |- buildspec.yml
|   |- template-configuration.json
|   |- template.yml
```

DevOps Repository:

```text
/
|- cloudformation-pipeline-template/
|   |- template-pipeline.yml
|
|- iam-cloudformation-service-role/
|   |- SAMPLE-CloudFormationServicePolicy.json
|   |- Trust-Policy-for-Service-Role.json
|
|- scripts-cli/
|   |- settings/
|   |- cli/
|   |- pipeline-stack.py
|   |- service-role.py
```

### Application Infrastructure directory

This is where your application CloudFormation template and code reside. This entire directory needs to be placed at the root of your repository. CodePipeline will look for `/application-infrastructure/` in your repository when executing.

AWS CodePipeline will use `buildspec.yml` to run the build process and then utilize the CloudFormation template `template.yml` to create an application infrastructure stack.

The buildspec and template files are structured to receive environment variables to execute logic based on whether it is building a DEV, TEST, or PROD environment. You will not need separate buildspec files (such as `buildspec-test.yml`) for each environment. Utilize parameters and environment variables.

Utilize `template-configuration.yml` to add custom parameter values and tags to your application resources.

### Pipeline CloudFormation Template directory

This contains `template-pipeline.yml`, the CloudFormation template that defines CodePipeline and associated resources. This can be moved to where your organization stores and maintains cloud infrastructure templates (such as Terraform or AWS CDK scripts). You can convert the pipeline to a Terraform or CDK script, upload it through the console, or use the AWS CLI.

The pipeline template is also available from a public S3 bucket if you wish to use the latest version as-is.

There is a `scripts-cli/` directory that assists in generating input.json files and copy-paste commands for use with the AWS CLI rather than uploading the template through the web console.

### IAM CloudFormation Service Role directory

You will need permission to create the CloudFormation stack that in turn creates the AWS Pipeline and associated resources. CloudFormation needs a service role to assume and you need permission to use that service role.

This directory contains the Trust Policy and Service Policy that can be copied and pasted into the IAM console, or invoked using the AWS CLI. You can also use these files as templates to create Terraform or AWS CDK implementations to provision the roles and policies.

## Parameters

TODO

## Usage

Before you start you will need to think through and establish a `PREFIX`. It is recommended that for your first time through use the given prefix `acme`. Once you have completed your first run-though of the steps you will have a better understanding of how you can group permissions using different prefixes for your applications. Each prefix and service role can be assigned to different departments, teams, or application groups in your organization. A prefix is 2 to 8 characters (`acme`, `finc`, `ws`, `ops`, `dev-ops`, `sec`), all lower-case.

In the following steps you can replace `acme` with your own prefix. When `acme` is in all lower-case, use your prefix in all lower-case. When `ACME` is in all upper-case, replace it with your prefix in all upper-case.

There are 3 main steps:

1. Create the CloudFormation Service Role and grant users access to assume it (Only needs to be done once per prefix used)
2. Create CodeCommit repository for your application infrastructure and code (Only needs to be done once per application)
3. Create Pipeline CloudFormation stack that provisions the CodePipeline which will deploy your application code (Can be done many times, once for each branch you wish to deploy to a separate instance)

## Review Change Log

Once you have your pipeline set up you may want to watch the [CloudFormation Template for a Deployment Pipeline (CI/CD)](https://github.com/chadkluck/serverless-deploy-pipeline-atlantis) repository for any updates. Using the instructions for editing your deployment pipeline stack above you can walk through the instructions in the Change Log and make updates to your deploy pipeline stack.

## Additional Documentation

Additional documentation is found in the /docs/ directory as well as /scripts-cli/ and /application-infrastructure/

- [1-2-3 Set-Up](./docs/1-2-3-Set-Up.md)
- [Pipeline Parameters Reference](./docs/Pipeline-Parameters-Reference.md)
- [Deleting and Clean-Up](./docs/Deleting-and-Clean-Up.md)
- [Tutorials](./docs/Tutorials.md)
- [Advanced](./docs/Advanced.md)
- [Scripts and CLI](./scripts-cli/README-CLI.md)
