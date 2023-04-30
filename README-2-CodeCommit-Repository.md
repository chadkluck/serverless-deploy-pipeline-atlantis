# Create CodeCommit Repository for Application Infrastructure

Once the service roles are created it is time to set up the CodeCommit repository to store your application infrastructure.

Commiting changes to your application infrastructure repository will kick off an automated deploy.

Except for CodeStar projects, you can set up multiple deployment branches such as test, beta, prod (main), or separate feature/developer branches. While a CodeStar repository can have multiple branches, only the main branch will deploy.

CodeStar is great for experiments, learning, and proof of concepts. Larger production projects will want to move beyond CodeStar and use regular CloudFormation stacks.

## For CodeStar Projects

When creating a CodeStar project, the CodeCommit repository will be created for you. However, you will need to have your application infrastructure stored in an S3 bucket as a ZIP file to seed your repository.

ZIP the contents of `codecommit-lambda-infrastructure` (or another compatible package) and upload the ZIP file into an S3 bucket.

## For Non-CodeStar Projects

When creating a project stack outside of CodeStar, you will need to create the CodeCommit repository and seed it with your application infrastructure before you can create the deploy pipeline.

You can create the repository using the command line or using the web console.

## Documentation

There are 5 README documents to walk you through setting up the required IAM Policies and Roles, CodeCommit Repository, and Deploy CloudFormation Stack. 

IAM Policies and Roles only need to be set up once. CodeCommit Repositories only need to be set up once per application. A deploy stack needs to be set up for each deployment stage of an application (test, beta, prod).

- [README 1 Create IAM Policies](README-1-IAM-Policies.md)
- [README 2 Create CodeCommit Repository](README-2-CodeCommit-Repository.md)
- [README 3 Create and Update CloudFormation Deploy Pipeline Stack](README-3-CloudFormation-Deploy-Stack.md)
- [README 4 Tutorial](README-4-Tutorial.md)
- [README 5 Advanced](README-5-Advanced.md)