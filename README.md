# CloudFormation Template for a Deployment Pipeline (CI/CD)

This project template will create an automated deployment pipeline based on changes commited to a branch in CodeCommit. The project to be deployed is built using the Serverless Application Model (SAM).

## Pros to using a template like this:

- Precisely scoped IAM Policies and Roles are created for you (more secure: principle of least privilege)
- Structured naming and tagging (better organization)
- No need to start from scratch
- No reason to create a messy application base and say "I'll structure, organize, and add security controls later"

## Cons to using a template like this:

- You need to understand someone else's code
- It stifles your creativity

I do beleive that the cons are only temporary and I set the toolchain up as a learning experience. As you begin to look under the hood you can use it as a model for learning AWS Cloud Concepts such as Infrastructure as Code (IaC), AWS CodePipeline, AWS Lambda, and CloudFormation.

## Modify to Suit Your Needs

Once an understanding of the `pipeline-toolchain.yml`, `application-infrastructure-sample-code/template.yml`, and IAM policy and role is achieved, they can all be modified to extend a project to use any AWS resource. As demonstrated in the tutorial, the templates are simple and easy to use to create and re-create sandboxes for experiementation.

The application deployed in the tutorials use a sample of the Serverless Application Model that deviates from the traditional "Hello World" example as instead it returns JSON formatted predictions. It is an extention of the [Serverless SAM 8-Ball example](https://github.com/chadkluck/serverless-sam-8ball-example) which I highly recommend checking out for the sake of learning more about the Serverless Application Model.

To deploy application infrastructure and code changes all you need to do is commit to a monitored branch of the repository.

Before skipping over the tutorials you'll need to make sure you have set up required IAM permissions and resources (Refer to documentation).

## Documentation

There are 6 README documents to walk you through setting up the required IAM Policy and Role, CodeCommit Repository for your application's code, and CloudFormation Deploy Stack. 

- [README 0 Start Here](deploy-pipeline-template-v2/README-0-Start-Here.md)
- [README 1 Create IAM Policies](deploy-pipeline-template-v2/README-1-IAM-Policies.md)
- [README 2 Create CodeCommit Repository](deploy-pipeline-template-v2/README-2-CodeCommit-Repository.md)
- [README 3 Create and Update CloudFormation Deploy Pipeline Stack](deploy-pipeline-template-v2/README-3-CloudFormation-Deploy-Stack.md)
- [README 4 Tutorial](deploy-pipeline-template-v2/README-4-Tutorial.md)
- [README 5 Advanced](deploy-pipeline-template-v2/README-5-Advanced.md)
- [CHANGELOG - Updates to Existing Deploy Stacks](CHANGELOG.md)
