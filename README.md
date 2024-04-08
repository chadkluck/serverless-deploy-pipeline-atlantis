# CloudFormation Template for CI/CD using AWS CodePipeline

Monitor and deploy changes to a CodeCommit branch using AWS CodePipeline.

It is recommended that you familiarize yourself with CloudFormation and CodePipeline.

The intent of this Pipeline template is to bridge the gap between pieced together tutorials (and solutions from Stack Overflow) and deploying practical, production ready solutions.

- Precisely scoped IAM Policies and Roles are created for you, your team, and application (more secure, principle of least privilege)
- Structured naming and tagging (better organization)
- No need to start from scratch
- No reason to create a messy application base and say "I'll structure, organize, and add security controls later"
- A tutorial for creating production-ready applications rather than examples pieced together

## About

Each branch will have its own pipeline stack and application infrastructure stack. This allows you to separate dev, test, and prod, grant developer access via CodeCommit policies, and create or destroy temporary or per-developer/feature test and staging branches/pipelines as necessary.

As you begin to look under the hood you can use it as a model for learning AWS Cloud Concepts such as Infrastructure as Code (IaC), CloudFormation, AWS CodePipeline, and serverless architecture. Once you have played around with it, the sky is the limit as you add your own modifications for your own use case.

## File Structure

There are 4 main directories in the root of this repository which corresponds to the 4 main steps necessary to get the solution up and running.

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
|   |- lib/
|   |- settings/
|   |- pipeline-stack.py
|   |- service-role.py
```

### Application Infrastructure directory

This is where your application's CloudFormation template and code reside. This entire directory needs to be placed at the root of your application's repository. CodePipeline will look for `/application-infrastructure/` in your repository during build and deploy.

Utilize `template-configuration.yml` to add custom parameter values and tags to your application resources.

### IAM CloudFormation Service Role directory

CloudFormation needs a service role to assume in order to create and manage the pipeline stacks and this directory contains the Trust and Service Policy for the Service Role.

After running `scripts-cli/service-role.py`, the generated `create-stack` input.json and copy-paste AWS CLI commands will be stored in this directory.

### Pipeline CloudFormation Template directory

This contains `template-pipeline.yml`, the CloudFormation template that defines CodePipeline and associated resources. 

After running `scripts-cli/pipeline-stack.py`, the generated `create-stack` input.json and copy-paste AWS CLI commands will be stored in this directory.

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
