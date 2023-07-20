# Create CodeCommit Repository for Application Infrastructure

Once the service roles are created it is time to set up the CodeCommit repository to store your application infrastructure.

Committing changes to your application infrastructure repository will kick off an automated deploy.

You can set up multiple deployment branches such as test, beta, prod (main), or separate feature/developer branches.

You will need to create the CodeCommit repository and seed it with your application infrastructure before you can create the deploy pipeline. To get you started, you can use the code found in the `/codecommit-repository-sample-code` directory.

## Documentation

There are 5 README documents to walk you through setting up the required IAM Policies and Roles, CodeCommit Repository, and Deploy CloudFormation Stack. 

IAM Policies and Roles only need to be set up once. CodeCommit Repositories only need to be set up once per application. A deploy stack needs to be set up for each deployment stage of an application (test, beta, prod).

- [README 1 Create IAM Policies](README-1-IAM-Policies.md)
- [README 2 Create CodeCommit Repository](README-2-CodeCommit-Repository.md)
- [README 3 Create and Update CloudFormation Deploy Pipeline Stack](README-3-CloudFormation-Deploy-Stack.md)
- [README 4 Tutorial](README-4-Tutorial.md)
- [README 5 Advanced](README-5-Advanced.md)
- [CHANGELOG - Updates to Existing Deploy Stacks](CHANGELOG.md)
