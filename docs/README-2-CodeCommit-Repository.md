# README 2: Create CodeCommit Repository for Application Infrastructure

Once the service roles are created it is time to set up your CodeCommit repository to store your application infrastructure.

You will need to create the CodeCommit repository and seed it with your application infrastructure before you can create the deploy pipeline. To get started, place the `/application-infrastructure` into the root of the repository. You can replace it later with more functional code such as [Serverless Web Service Template for Pipeline Atlantis](https://github.com/chadkluck/serverless-webservice-template-for-pipeline-atlantis).

## Create the Repository

1. Create a code commit repository. (You can name it `hello-world`)
2. Clone the repository to your local machine.
3. Copy the `/application-infrastructure` directory into the root of the repository and commit.
4. Create `dev` and `test` branches (you can create additional branches later)

You should now have a repository with 3 branches:

- main (sometimes master)
- test
- dev

Each branch should contain the same code.

When we create the first Deploy Pipeline CloudFormation stack we will have it monitor the "test" branch. Upon successful completion of the test deployment, we will create a production deployment from the "main" branch.

We will leave "dev" as a branch that doesn't have an automatic deploy. You can also create individual developer and feature branches in the future.

## File Structure

> **NOTE:** The deployment pipeline expects to find the application-infrastructure directory containing your application code and infrastructure template in your repository.

```
Repository
| - application-infrastructure/   <-- contains template and application code
|   | - app/
|   | - template.yml
|   | - ...
| - deploy-pipeline/              <-- (optional) contains a copy of your deploy pipeline and CloudFormation input generators
    | - pipeline-toolchain.yml
```

The deploy-pipeline directory is optional and can be helpful if you modify the pipeline-toolchain. You can also move it (and iam-cloudformation-service-role) to where your organization manages set-up templates centrally or convert to Terraform or AWS CDK script. 

The codecommit-repository, iam-cloudformation-service-role, and doc directories do not have to be copied over to your application repository.

When the deploy pipeline stack is set up, you will choose a branch to monitor and deploy from.

Once you are comfortable setting up deploy pipelines and connecting branches, you can manage multiple deployments such as test, beta, prod (main), or for separate feature/developer branches.

It is recommended you have a base or work-in-progress branch (such as `dev`) that you can commit code to without initiating a deploy.

## Related

- [AWS Documentation: CodeCommit ](https://docs.aws.amazon.com/codecommit/latest/userguide/welcome.html)
- [AWS Documentation: AWS Serverless Application Model (SAM)](https://docs.aws.amazon.com/serverless-application-model/latest/developerguide/what-is-sam.html)

## Documentation

TODO
