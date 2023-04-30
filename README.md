# Project Stack Template with CI/CD

This project template will create an automated deployment pipeline based on changes commited to a branch in CodeCommit. The project to be deployed is built using the Serverless Application Model (SAM).

Pros to using a template like this:

- IAM Policies and Roles are created for you (more secure)
- Structured naming and tagging (better organization)
- No need to start from scratch
- No reason to create a messy application base and say "I'll structure and organize it for production later"

While the deploy template is based on CodeStar Toolchains, it can be used as a ProjectStack (CloudFormation Only) template without an attached CodeStar project. Using this template and the source will provide you with:

- Scripts to assist with CodeStar, CloudFormation, and CodeCommit creation specific to your project.
- A toolchain to create multiple deploy pipelines for each development, test, or production stage
- Sample Lambda SAM project using API GateWay and code that starts with a simple `Hello World`-type example but can be extended with provided code snippits to include:
  - S3 Data Storage
  - DynamoDb Data Storage
  - IAM policy samples
  - Access to Parameter Store
  - CloudWatch Alarms
  - CloudWatch Dashboard

Additional AWS resources may be added to the application CloudFormation template. You can modify and host your own versions of this starter package using steps found in the "Advanced Usage" section.

Each deploy instance has it's own IAM policies to keep your deploy and app separate from other stacks you may have on your account. Simple naming conventions are used on which IAM policies may implement access restrictions to users/developers of a team.

Once an understanding of the `toolchain.yml`, `s3-src/template.yml`, and IAM policies is acheived, they can all be modified to extend a project to use any AWS resource. As demonstrated in the tutorial, the templates are simple and easy to use to create and re-create sandboxes for experiementation.

Understanding CodeStar, CloudFormation, IAM, and Pipelines is complex, and difficult to describe without prior experience. Therefore this document will start with a Tutorial which will walk you through setting up the prerequisites. If you wish to skip, just go to the "Usage" section for advanced information.

If you plan on skipping the tutorials please note that the start of each tutorial has a ***Step 0*** which includes set-up information. Be sure to follow those instructions to get your account set up to use the project templates.

The application deployed in the tutorials use a sample of the Serverless Application Model that deviates from the traditional "Hello World" example as instead it returns JSON formatted predictions.

It is an extention of the SAM 8-Ball example. This version modifies the SAM 8-Ball example by placing it inside of a managed stack (either CodeStar or a project stack in CloudFormation).

Once projects have been created, you may access the CodeCommit repository and utilize local sam commands to develop and test locally. To deploy your code all you need to do is commit to a branch of the repository.

Before blindly skipping over the tutorials you'll need to make sure you have completed Step 0 in each of the tutorials to set up required permissions and resources.
