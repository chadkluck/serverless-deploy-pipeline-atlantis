# Advanced

## Project IDs

TODO

## Stages and Environments

Stage related to branch. Environment is related to provisioning.

Each stage corresponds to a branch, so we don't need to fill in the branch variable (though you can have multiple stages deploy from the same branch, but I'll explain later).

There are three different environments, "DEV", "TEST", and "PROD", and any environment can be assigned to any stage as they are not related.

Think of *stages* as a stage or branch in your development pipeline. Various branches in your repository, each at a different stage of development, can be pushed to their own deploy for review and testing. Each developer may have their own personal branch tied to their own personal deployment stage that they merge into the next branch taking it to the next stage towards production.

Alice's code gets merged from branch `alice` into `dev` and at a certain point all changes from `dev` progress into `test`. Then maybe `review` and finally `prod`. You can have as many stages as you want.

Not every branch needs a deployment stage. Developers may merge working code into the `dev` branch throughout the day and there is no need to deploy every 15 minutes or so. However, as mentioned, each developer may have their own stage deploy instance.

Other than being used to name and distinguish deploy instances, the stage name is not used for any logic and is arbitrary.

Environments, however, deal with the type of resources, tests, alarms, and compute provisioned for your deployment. They can be used in the SAM template to make logical decisions.

For example, in a `DEV` environment you may supply limited compute and memory to your Lambda function. You may also decide not to deploy CloudWatch dashboards, full test suites, or be notified by text or email if an application is in alarm. 

For `TEST` you may ramp up the number of tests you do. You may still not deploy a CloudWatch dashboard or alarms. Or, you may have alarms specific to thresholds you want to monitor during testing.

In a `PROD` environment you might run a whole bunch of performance tests prior to deploy, maybe even simulated loads. You'll want alarms triggered, and you'll want to set up a gradual deploy that way if there are any issues your application can roll back. You certainly wouldn't want traffic to gradually switch from the old version to the new in a `TEST` or `DEV` environment.

Below is an example of conditionals and an alarm in a SAM template:

```YAML
Conditions:
  IsProduction: !Equals [!Ref DeployEnvironment, "PROD"]
  IsTest: !Equals [!Ref DeployEnvironment, "TEST"]
  IsDevelopment: !Equals [!Ref DeployEnvironment, "DEV"]

Globals:
  Function:
    Runtime: nodejs12.x
    AutoPublishAlias: live
    DeploymentPreference:
      Enabled: True
      Type: !If [ IsProduction, "Canary10Percent30Minutes", "AllAtOnce"]
      Role: !Ref DeployRole

Resources:
  # Log Group with a retention policy
  AppLogGroup:
    Type: AWS::Logs::LogGroup
    DependsOn: "AppFunction"
    Condition: IsProduction
    Properties: 
      LogGroupName: !Sub "/aws/lambda/${AppFunction}"
      RetentionInDays: 90
```

So, just as a recap, stage is related to a branch. Environment is related to the resources provisioned. To help in infrastructure code reviews, stages are in all lower case and can be any name, environment is in all upper and can only be `DEV`, `TEST`, or `PROD`.

### One more thing about stages

You may have one final question.

What do I do with the "main" branch?

You have two options.

First, know that the stage name does not need to correspond to the name of the branch. You could have a main branch that deploys to the `prod` stage. So, any commits into main would then deploy to `prod`. To achieve this just set "stage" to `prod` and "branch" to `main`.

```JSON
  "id": "my8ball",
  "stage": "prod",
  "env": "PROD",
  "branch": "main"
```

Or, you could name your production stage `main`, but that would just be weird.

Your other option is to not deploy at all from the main branch, but rather once the code has been in production long enough, it is deemed stable, and then moved into main. The benefit of this is that main essentially becomes a repository from which you, or others in your organization, can pull from and run their own instances.

```TEXT
dev -> test -> pre -> prod -> main
       TEST    PROD   PROD    (no deploy)

Move you code through each branch until production. Then eventually move on to "main" where it can be considered "released" to others in your organization (or the public).
```

I'm not suggesting you use your production as a test environment, I completely believe in heavy testing before production, but you'd probably want to take a taste of your pudding before serving it to a wider audience.

## Multiple stages off single branch

To make the "use main as release code" even sweeter, you can have multiple deploy instances run off of the same branch.

Suppose you have an application that is used by multiple departments in your organization, and they each prefer to run their own instance because they have their own settings. If the apps don't need to talk to each other or use the same database (but they could) you could get around coding your app to handle multiple settings by just deploying the same app multiple times. And wouldn't it be great if just by pushing to the main branch it would deploy to the pool of apps?

If you are developing serverless, there is no cost increase in running multiple copies of the same app (as long as it doesn't use non-serverless resources such as EC2 or ElasticBeanstalk). You are charged per use of a lambda function whether the use is to a single function, or divided among 15 copies of the same function.

So, you could have multiple copies of project stacks monitoring a single, shared branch. It could be the main branch, or even a "pool" branch. Once code is committed to that branch it will kick off deploys for each copy.

- dev branch (no deploy)
- test branch (deploy to my8ball-test stage)
- prod branch (deploy to my8ball-prod stage)
- main branch
  - (deploy to my8ball-acct stage)
  - (deploy to my8ball-sales stage)
  - (deploy to my8ball-hr stage)


The most likely time you will want your branch name to deviate from the stage is when deploying to `prod` (production) from the `main` branch. (Though I do a lot of development to share, so I have a prod branch that deploys to prod, and then after a while I'll merge it into `main` which pushes to a public GitHub repository, but that's just how I do it.)

The `env` variable can be set to `DEV`, `TEST`, or `PROD` and can be used to switch various pieces of a deploy on or off. Maybe you don't need heavy error reporting in `PROD` or maybe you want to ramp up automated testing in `TEST` but not `DEV` as it could be costly as devs check in code throughout the day.

## Least Privilage and Naming Conventions

Both of these options use the same CloudFormation template (`codestar-files/toolchain.yml`) which utilizes CodeStar practices of applying best practice IAM policies to the app (the app only has access to the resources it creates) and its deployment pipelines. Because of this, some resources such as IAM policies will still have CodeStar in their name which can be used as a signifier that it was created using these practices and for permissions.

### awscodestar-* and projectstack-* and creating your own prefix

All resource names should be in `[Prefix]-[ProjectStageId]-*` format as IAM policies are keyed on in the ARN and allow access based on this naming convention. This makes sure that only resources named `[Prefix]-[ProjectStageId]-*` only have access to other resources named `[Prefix]-[ProjectStageId]-*`.

`awscodestar` is the prefix used for CodeStar projects and cannot be changed. `projectstack` is the default prefix for non-CodeStar projects. If you add other prefixes (which can be used for namespaces to separate your organizations departments!) you will need to add additional Service Roles (See "Additional Project Namespaces (Prefixes)")

IAM policies differ slightly as you'll see `CodeStar-*` used.

You can create different namespaces for projects beyond `awscodestar-*` and `projectstack-*` for example `acct-*`.

This is useful so that you can put various groups into their own namespace with their own permissions. Maybe a team has access to `acct-*` resources but not `sales-*`

To do this create a copy of `policy-template-ProjectStackServicePolicy.json` and `policy-template-ProjectStackTaggingPolicy.json` and change `projectstack` to whatever you want. Then create a new role just the way you did in Step 0 for the CloudFormation project stack tutorial, for example, `acct-service-role`.

### ProjectId and ProjectStageId

`ProjectId` is the base ID of your project without the stage name attached to it. The script `generate.py` will create these names for you.

For example, if the `ProjectId` is `orion` and you are creating a `test` stage, then the `ProjectStageId` would be the project ID with the stage appeneded to it: `orion-test`.

Note that for CodeStar projects there is no stage and therefore the ProjectId is the same as the ProjectStateId. So, in the following example where ProjectId was `orion`, the ProjectStageId would also be `orion`. You could name your ProjectId `orion-test` if you needed to distinguish it from another project ID of `orion`.

Also note that for CodeStar projects the CodeCommit repository will be named `awscodestar-orion` (denoting it is part of the CodeStar project) while for the CloudFormation Stack the CodeCommit repository will simply be named `orion`. For CodeStar it is again important to note that the repository is part of the project and if the project is deleted the repository will be deleted as well.

Example IDs and repository names:

- CodeStar Project
  - Stage: (none)
    - ProjectId: `saturn`
    - ProjectStageId: `saturn`
    - Repository: `awscodestar-saturn`

- CodeStar Project
  - Stage: `v2`
    - ProjectId: `saturn-v2`
    - ProjectStageId: `saturn-v2`
    - Repository: `awscodestar-saturn-v2`

- CloudFormation Project
  - Stage: `prod`
    - ProjectId: `saturn`
    - ProjectStageId: `saturn-prod`
    - Repository: `saturn`
  - Stage: `test`
    - ProjectId: `saturn`
    - ProjectStageId: `saturn-test`
    - Repository: `saturn`

## Starter Source Code

The `s3-src` folder contains a sample CloudFormation template and serverless application code to start with. When you run the upload script these files are zipped and placed in an S3 bucket. You may initialize a repository with these files to quickly get your development started. CodeStar will initialize the repository automatically, if using a CloudFormation Stack you will need to create the repository and initialize it with these files yourself.

### Source Features

The serverless application template and code contains a robust definition for an application that utilizes API Gateway, Lambda, and Parameter Store. Code for leveraging S3 and DynamoDb is also included.

Additional resources can be used, API Gateway can be removed, but the code and template represent most common applications my group develops.

You can always point to another source repository. However, since the application IAM deploy and execution policies are based on ARNs which includes the `codestar-*` identifier in resource names among other things, it is best to reference the current source code to make sure your application is able to be deployed using this template.

Speaking of IAM execution and deploy policies, the toolchain automatically provisions permissions for S3, DynamoDb, Parameter Store, API Gateway, and Parameter Store. If you want to add additional resource types you will need modify and extend the permissions in `codestar-files/toolchain.yml`. Instructions on how to do so are beyond the scope of this template. Once you familiarize yourself with the process and principles of a CodeStar deployment with custom toolchains, you should be able to begin to poke around and create your own toolchain.

### s3-src/app

Node.js code for a Lambda function. Contains code snipits for initializing and loading from Parameter Store asyncronously as well as some sample code to get started. 

Includes code snip-its for accessing S3 and DynamoDb.

### build.yml

Utilizing environment variables, the buildspec can adjust a build specification depending upon the deployment environment. 

Builds have access to Parameter Store.

### template.yml

Utilizing environment variables and parameters, the CloudFormation template has snip-its ready to adust for various deployment environments through the use of conditionals. This can assist in determining if a production environment needs additional resources, or what deploy method is used (immediate, canary, or linear), and if admins get alerted if certain error thresholds are met.

The API Gateway and Lambda function are filled out more than typical bare bones templates, representing some of the more common uses.

Also includes snip-its for provisioning a private S3 bucket, DynamoDb, and CloudWatch Dashboard.

#### Stack Parameters

Two parameters (which are required) are provided for you: `ParameterStoreBasePath` and `DeployEnvironment`

#### Parameter Store Base Path

The parameter `ParameterStoreBasePath` allows you to organize your SSM Parameter Store. The CodeStar template will organize all application variables within a directory denoted by `<project_id>`. For exmample, if you set `ParameterStoreBasePath` to `"/"` and your project is named `myproject` then it will store variables at `/myproject/<appvars>`. If you set `ParameterStoreBasePath` to `"/webapis/"` and your project has stage set to `test` then it will store variables at `/webapis/myproject-test/<appvars>`.

By default `ParameterStoreBasePath` is set to `""` which is equal to `"/"`.

#### Deploy Environment

Similar to `stage`, Deploy Environment will also be turned into an environment variable for CodeBuild (`DEPLOY_ENVIRONMENT`) and passed to your application as a CloudFormation template parameter `DeployEnvironment` so you can use it to perform logical operations based on the deploy environment.

Unlike `stage` or `DeployStage`, Deploy Environment is not used in the CodeStar template. Instead, it is up to you to determine how you might use Environment. It may be helpful to think of Environment at a higher level than stage. For example, a `DEV` environment may contain the stages `dev`, `test`, `review` and `qa` and a `PROD` environment may contain `beta` and `prod`.

You can use the deploy environment to set your deployment strategy (linear/canary), perform limited or full tests, and more.

Where `stage` can be lowercase, `DeployEnvironment` must be upper alphanumic with no spaces, dashes, or special characters.

Note: If you wish to change the accepted character format for stage and environment, you may change the `AllowedPattern` for `DeployStage` and `DeployEnvironment` in both `codestar-files/toolchain.yml` and `s3-src/template.yml`.

## Using your own custom toolchain

### Step 1: Upload src and toolchain

This step is only if you are maintaining your own copy of the src.zip and toolchain.yml files in your own S3 bucket.

If you are using the files at `S3://63klabs/projectstack-templates/atlantis` or elsewhere, you may skip this step.

Upload your custom toolchain.yml file to an accessible S3 bucket. It doesn't have to be public, but the user executing generate.py script should have access to the bucket and the toolchain.

If you are creating a CodeStar project, then the ZIP copy of the src folder must be uploaded as well. If doing a pure CloudFormation deploy then you can just populate your Code Commit repository with the code.

## Quick Guide

First, complete Step 0 in each of the tutorials to set up your IAM policies

Once the IAM policies are set, it is important to take a careful look at your `config-project.json` file and make sure you have everything set correctly. After you've created your first project and set up the role_arn, account, region, tags, etc. you'll want to make sure you update project id, stage, env, repo, and branch for every project. (Leave project id as an existing project if you are just creating a new deploy off an existing repo).

### CodeStar

Remember, you can only have 1 branch in your repo for CodeStar. Great for sandboxes and temporary projects.

1. Update config-project.json
2. `py generate.py`
3. That's it!

### CloudFormation project stack

1. Update config-project.json
2. `py generate.py`
3. Create repository using the CLI examples generated from `generate.py`
4. Create stack using the CLI examples generated from `generate.py`

#### Adding a new deploy

1. Create branch and merge current source into it
2. Update `config-project.json` by updating the `stage`, `env` and pointing to the new `branch`.
3. `py generate.py`
4. Create stack using the CLI examples generated from `generate.py`

## Documentation

There are 5 README documents to walk you through setting up the required IAM Policies and Roles, CodeCommit Repository, and Deploy CloudFormation Stack. 

IAM Policies and Roles only need to be set up once. CodeCommit Repositories only need to be set up once per application. A deploy stack needs to be set up for each deployment stage of an application (test, beta, prod).

- [README 1 Create IAM Policies](README-1-IAM-Policies.md)
- [README 2 Create CodeCommit Repository](README-2-CodeCommit-Repository.md)
- [README 3 Create and Update CloudFormation Deploy Pipeline Stack](README-3-CloudFormation-Deploy-Stack.md)
- [README 4 Tutorial](README-4-Tutorial.md)
- [README 5 Advanced](README-5-Advanced.md)
