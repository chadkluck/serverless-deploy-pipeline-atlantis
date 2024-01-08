# Tutorials

In order to complete the tutorials you must have completed the steps outlined in [README 1: IAM CloudFormation Service Role](../iam-cloudformation-service-role/README-1-IAM-CF-Service-Role.md), [README 2: CodeCommit Repository](../codecommit-repository/README-2-CodeCommit-Repository.md), and [README 3: CloudFormation Deploy Stack](../deploy-pipeline/README-3-CloudFormation-Deploy-Stack.md).

If you have completed the steps in these 3 READMEs, then congratulations! Your tutorial journey has already begun!

Let us review what has been completed:

1. IAM CloudFormation Service Role
2. CodeCommit Repository
3. Pipeline deploy stack creation

When you create a CloudFormation stack you must assign it a service role so it has permissions to create the resources specified in the CloudFormation stack template. The IAM policy and service role we created grants the deploy stack permission to create the AWS CodePipeline including the AWS CodeBuild and CodeDeploy stages. It also grants access to CodePipeline to monitor repositories assigned to the pipeline using AWS Event Bridge.

The IAM policy and service role is scoped down to just the prefix and resource types assigned to it. So, for example, if you have two teams, Accounting (ACCT) and Engineering (ENGR), each can have their own Service Role to create their own deploy and application stacks. The engineering team will only have access to create stacks under the ENGR prefix, and the accounting team will only have access to create stacks under the ACCT prefix.

Similarly, ENGR deploy stacks can only modify ENGR resources. For example, an ENGR stack cannot delete or modify resources assigned to an ACCT stack. Furthermore, each stack has its own policy that restricts its own access to resources under its name and stage.

Stacks `ENGR-atomic-particle-manager-test-deploy` and `ENGR-atomic-particle-manager-infrastructure` can only modify resources with names (or specified tags) starting with `ENGR-atomic-particle-manager-test-*` and cannot modify resources under the name `ENGR-atomic-particle-manager-beta-*` and certainly not `ACCT-payroll-prod-*`.

The deployment stacks also create Worker Roles specific to the application infrastructure stack. The Worker CFRole takes the place of the Service Role for the infrastructure stack. Just like how the Service Role grants the deploy stack permissions, the Worker CFRole grants the infrastructure stack permission to create all the resources necessary for your application infrastructure.

Right now the infrastructure stack has permission to create resources such as S3, DynamoDb, and Lambda functions. If it tried to create an EC2 instance, Event Bridge rule, or Step Function it would fail due to inadequate permissions.

However, depending on the needs of your application, you can add and remove permissions to these Roles. We will have a tutorial on this later.

For now remember the following:

1. The Service Role grants the deploy stack permission to create the Code Pipeline and worker roles for the application infrastructure stack. If you want to add to your deploy stack such as pipeline execution notifications via SNS or other event triggers, add them to the service role.
2. The worker roles created by the deploy stack grant permission for the infrastructure stack to create all resources and execution roles for your application. If you need your infrastructure stack to create EC2 instances, Databases, and Step Functions, you need to add these permissions to the Worker Role definition in the pipeline-toolchain.yml template.
3. Execution roles are created and defined in the infrastructure stack template. If your application needs additional access to S3 buckets or databases that are not created by the stack then you can add them to the execution role definitions in the template.yml file.

## Tutorial 1: Deploying Changes

Change into the "my8ball" repository directory. (e.g. `cd ../my8ball`)

Checkout the `test` branch:

`git checkout test`

Open the `app/index.js` file.

We added some negative responses last time, so let's add some positive ones!

```javascript
const answers = [ "It is certain",
//... add in any of the following or your own
		"Everything will come up roses",
		"I'd bet my magic on it",
    "Are puppies cute?",
    "Stars are aligned in your favor",
    "I'm pulling for you!",
//...
    "My sources say no",
    "Outlook not so good"
];
```

Add your changes, commit, and push.

`git add --all`

`git commit -m "added new responses"`

`git push`

Go into CloudFormation and go to the pipeline for your test deploy stack to watch the CodeBuild and Deploy process.

When it is done, go into CloudFormation and view the updated test infrastructure stack. Go under Outputs and click on WebApp.

Everything look good? Great! Now we are ready to merge our changes into main and deploy to production!

`git checkout main`

`git merge test`

`git push`

Hopefully you now know your way around the infrastructure and test stacks for test and main so check out the deploy process!

Note that since we set the `env` for main/production to `PROD` there will be a gradual deploy so you may not see your new sayings in production for a while.

## Tutorial 2: Expanding Infrastructure Stack

Infrastructure Stack permissions come from the IAM Worker defined in the Deploy Pipeline Stack.


Commit a few changes, and you're a pro!

## Tutorial 3: Expanding Deploy Stack

Deploy stack permissions come from the Service Role.

### Deleting stacks

You can add stacks all day long, you can also delete them without affecting the branches. However, there is an order for deleting:

1. Delete the infrastructure stack. You may need to disable termination protection.
2. Empty the S3 bucket for the deploy. The bucket with the format: `${AWS::Region}-${AWS::AccountId}-${ProjectStageId}-deploy`
3. Delete the deploy stack. Again, you may need to disable termination protection.

### Congratulations!

You made it all the way through the tutorials.

Once you feel comfortable creating projects using CodeStar and CloudFormation, check out the advanced README.

## Documentation

Next: [README 5: Advanced](./README-5-Advanced.md)
Previous: [README 1-2-3: Set-Up](./README-1-2-3-Set-Up.md)
Back to the Beginning: [README 0: Start Here](./README-0-Start-Here.md)

When you are ready for a more advanced application tutorial for your CI/CD pipeline, check out the repository: [Serverless Web Service Template for Pipeline Atlantis](https://github.com/chadkluck/serverless-webservice-template-for-pipeline-atlantis).

## TO DELETE

## Tutorial 1: CodeStar via Web Console

Using the template and starter source is as simple as having access to the toolchain and zipped code from an S3 bucket, providing information in `config-projects/config-projects.json`, generating the input files, and executing an AWS CLI to create either a CodeStar project or CloudFormation stack.

While just knowing CloudFormation and SAM is a great start, alone it does not allow you to manage production code. This project template can be used to further your understanding, experience, and implementation of a full production pipeline using SAM and CloudFormation.

### Step 0: Prerequisites and creating CodeStar Service Role

1. Understanding of SAM (Serverless Application Model)
2. A computer with AWS CLI, git, bash (or gitbash), and Python installed
3. Ability to run simple AWS CLI, git, bash, and Python commands (they will be provided for you)
4. An AWS account

If you don't meet these first set of requirements, then I recommend you check out the GitHub repository for 8Ball. It will walk you through setting up your computer and deploying your first SAM application. This tutorial will build upon that experience so it is recommended that you have created and deployed SAM projects using the AWS CLI prior.

And finally, prerequisite #5 is to create CodeStar Service roles which can be found in [README #1 IAM Policies](README-1-IAM-Policies.md).

### Create your first CodeStar Project

If you have used CodeStar from the AWS Web Console before, you may skip this step.

We will first create a test project in CodeStar and review the resources it created. We will create a Serverless Lambda function which will not incur any costs. (Anything using EC2 and ELB would incur costs.)

1. Go to: <https://aws.amazon.com/codestar/>
2. Choose Create Project
3. From the Choose a project template page find the Node.js Web Application using the AWS service Lambda. (you can filter by "AWS Lambda," "Node.js," and "Web application")
4. Give the project a name such as `My Test` and an ID such as `mytest`
5. Keep CodeCommit as the repository and leave the repository as is (it should have automatically filled in your test name).
6. Review the information and choose "Create project"
7. The project will be provisioned which will include the code and deploy pipeline.
8. Once the project has been created, click "View application". You will be taken to currently static web page served up through API Gateway.

Go back to your CodeStar project and look at each of these under project resources by clicking on the link and exploring the resource in the web console

- AWS Lambda: Click on the resource link and explore the Lambda console.
- IAM Policies: These allow CodeStar to submit changes and manage your application. CodeStarWorker policies have permissions specific to this application, they cannot be used to manage other applications. This is good practice. This CodeStar project only has access to update and deploy *this* project.
- AWS CodePipeline: This uses CodeBuild and CodeDeploy to *build* and *deploy* your SAM application. You do not need to do builds and deploys from the command line. You only need to submit your changes to CodeCommit and the build and deploy process will automatically be kicked off.
- CodeCommit: Go into CodeCommit and feel free to clone the repository to your local machine and make a change and submit. Or make the change in the web console. Right now changes to the main branch kick off a deploy. If you wanted to add additional branches (such as `dev`) you could, and you could push changes to the `dev` branch without kicking off a deploy. You could also use SAM to locally test on your machine before merging changes into `main`.
- Amazon S3: Two S3 buckets are produced. One is used for the build and deploy (aws-codestar-*-pipe) and the other is a public bucket used to store static content for your web application.
- Amazon API Gateway: This is the endpoint for your application.

### Code Structure

What created all these resources? The entire CodeStar project was created using two CloudFormation templates (one for the deploy pipeline) and another for the application which you are free to modify and add your own resources for the project.

Let's take a look at these files.

Go into your CodeStar project and find the Repository tab.

From here you can get the HTTPS link to clone the repository or click on the Repository name to go to CodeCommit. Click on the repository name.

If you are familiar with SAM, you'll see the basic files. The index.js file in which the Node.js for Lambda is found, a buildspec, and template.yml.

If you go into `template.yml` you'll find that CodeStar passed 3 parameters to your application: ProjectId, CodeDeployRole, and Stage. You'll also notice that many of the resources are named following the `awscodestar-${ProjectId}-lambda-GetHelloWorld` convention. There are also policies and roles created. The structure of the names and arns are very important as that is what grants your application and the deploy permission to act on itself. `awscodestar-${ProjectId}-*` will be found in many of the policies if you looked at the IAM permissions.

If you make any changes to the template, code or anything in this repository and push a commit, then it will kick off the deploy pipeline.

### Pipeline

Let's look at the pipeline by going back into your CodeStar project and clicking on the Pipeline tab.

You'll see that the source from the CodeCommit repository is Built and then Deployed. When you push changes to the repository you can monitor the build and deploy progress here.

This pipeline was created using a CloudFormation template separate from your application's CloudFormation template. While you can change the way your application behaves by changing the template in the code repository, this template, or toolchain, resides outside the repository. We can, however, take a look at it by going into CloudFormation.

### CloudFormation toolchain

Go into CloudFormation via the web console and note that there are two stacks with your project ID. `awscodestar-${projectId}` and `awscodestar-${projectId}-infrastructure`.

`awscodestar-${projectId}-infrastructure` is your application's code, the stack that is created and modified when you commit changes to your repository. Remember the basic rule of SAM is "Infrastructure as Code." You can explore that stack if you want, be we are more interested in the stack that performs the deploys.

Go into the stack for `awscodestar-${projectId}` and click on the "Template" tab.

Under Resources you'll see resources such as Roles, CodeBuild, CodeDeploy, CodeCommit, the creation of the S3 bucket where the artifacts from the build are placed when ready for deploy, and the Pipeline that ties it all together.

The main idea here is the permissions given to all the resources. Each resource, even resources you are not yet using, are either given permission to act on other resources with an arn structure of `arn:${AWS::Partition}:lambda:${AWS::Region}:${AWS::AccountId}:function:awscodestar-${ProjectId}-` or resources with that arn structure (the ones you created) have permissions to perform actions. 

Look over the policies and see what has access to perform actions on your resources, and what actions your resources can perform on others.

These policies create a least privilage structure. Your application only has permission to perform actions it needs to. Your application cannot utilize an S3 bucket it did not create. A lambda function in another application does not have access to this application's resources. 

And, if you were to create a test and dev stage, yourApp-test would not have access to yourApp-dev resources. Everything is segmented (and secured!).

While you can't readily update the permissions (suppose you want to add another AWS product not listed such as IoT, or add a connection to a shared database) you can use this framework as a base and extend it. That is where Project Stacks come in.

While the permissions make up a bulk of the deploy template, the other part is mainly creating the build and deploy pipeline.

## Tutorial 2: CodeStar via CLI using project stack templates

While CodeStar via the console is great for learning and small projects, it is difficult to expand into complex projects and deployment pipelines.

You can, however, take what CodeStar gives us in terms of a framework, and expand it's usefullness when we begin to create projects via the AWS Command Line Interface (CLI).

In your CLI, run the following command (it will not actually create a project):

`aws codestar create-project --generate-cli-skeleton`

You should see something similar to this:

```JSON
{
    "name": "",
    "id": "",
    "description": "",
    "clientRequestToken": "",
    "sourceCode": [
        {
            "source": {
                "s3": {
                    "bucketName": "",
                    "bucketKey": ""
                }
            },
            "destination": {
                "codeCommit": {
                    "name": ""
                },
                "gitHub": {
                    "name": "",
                    "description": "",
                    "type": "",
                    "owner": "",
                    "privateRepository": true,
                    "issuesEnabled": true,
                    "token": ""
                }
            }
        }
    ],
    "toolchain": {
        "source": {
            "s3": {
                "bucketName": "",
                "bucketKey": ""
            }
        },
        "roleArn": "",
        "stackParameters": {
            "KeyName": ""
        }
    },
    "tags": {
        "KeyName": ""
    }
}
```

If you were to fill this out and save it as an `input.json` file, you could pass it into a `codestar create-project` command and create your own projects from the command line.

Note the `sourceCode` section that references a bucket and bucket key. That is where CodeStar will retreive a .zip file containing the application source code, buildspec, and CF template to provision your app resources and create your Lambda function. Yes, the code will need to be zipped and placed in an S3 bucket you have access to. (For the tutorial you will have access to an already existing S3 bucket.)

Note that the source code can either be sent to a CodeCommit or GitHub repository. We'll be using CodeCommit.

Also note the `toolchain` section. That section lets CodeStar know where to get the toolchain template (the one that provisions the IAM policies and deploy pipeline which in turn deploys your application resources contained within the src zip file). (Also note, that for the tutorial you will have access to an already existing S3 bucket.) You already viewed a toolchain template in CloudFormation during the previous tutorial, but you can find [another example of a CodeStar Toolchain template](https://docs.aws.amazon.com/code-samples/latest/catalog/cloudformation-codestar-template-create-codestar-toolchain-codecommit.yml.html) on the AWS documentation site.

`stackParameters` is a list of key-value pairs for passing to your application (infrastructure) stack.

`tags` is a list of key-value pairs for applying to EVERY resource created by your application (infrastructure) stack. Very helpful for making sure you don't miss tagging any resources!

A similar skeleton input file can be created for CloudFormation if you prefer to use that over CodeStar (which is a very valid preference).

Run the following command (it will not create a stack):

`aws cloudformation create-stack --generate-cli-skeleton`

And you will receive output such as:

```JSON
{
    "StackName": "",
    "TemplateBody": "",
    "TemplateURL": "",
    "Parameters": [
        {
            "ParameterKey": "",
            "ParameterValue": "",
            "UsePreviousValue": true,
            "ResolvedValue": ""
        }
    ],
    "DisableRollback": true,
    "RollbackConfiguration": {
        "RollbackTriggers": [
            {
                "Arn": "",
                "Type": ""
            }
        ],
        "MonitoringTimeInMinutes": 0
    },
    "TimeoutInMinutes": 0,
    "NotificationARNs": [
        ""
    ],
    "Capabilities": [
        "CAPABILITY_IAM"
    ],
    "ResourceTypes": [
        ""
    ],
    "RoleARN": "",
    "OnFailure": "DO_NOTHING",
    "StackPolicyBody": "",
    "StackPolicyURL": "",
    "Tags": [
        {
            "Key": "",
            "Value": ""
        }
    ],
    "ClientRequestToken": "",
    "EnableTerminationProtection": true
}
```

You'll see that the Parameters and Tags are in a different format. They are not a list of key-value pairs, but rather indexed arrays with keys and values placed in values of keys and values. (The good thing is we have scripts to create both of these input files from a common structure. We'll look at the generated input files later.)

Notice it doesn't ask for your application's source code, or a code commit repository. That is because when we use CloudFormation to create our deploy pipeline we will be creating our repository on the side. (I should note here that it is good practice to keep your repo separate from your CF created deploy pipeline, because if you delete the stack that created your repo and deploy pipeline, your repo is gone too! That is one drawback to CodeStar, the repo is tied to your project. Delete the CodeStar project, delete the repo! (there are ways around that but that is beyond the scope of this project and tutorial)).

The CloudFormation template does ask for a "toolchain" however via the `templateURL` which is the public web (`https`) url of your toolchain template. Yes, with a few modifications you can take a CodeStar toolchain template and use it for non-CodeStar projects. Essentially you are creating CodeStar-like projects with the benefits of the CodeStar framework, but without the limitations!

Project Stacks does take the best of both worlds. You can use it to create (via the AWS CLI) either a CodeStar project or a CloudFormation stack. You get to choose the best fit for your particular project. What is the best fit? Use the following tutorials and decide for yourself. There is not a one solution fits all approach, which is why both approaches are included in Project Stacks.

### Step 0: Set up the project scripts and permissions

You will need to download [atlantis.zip](https://63klabs.s3.amazonaws.com/projectstack-templates/atlantis/atlantis.zip) and extract it.

The file structure will be:


- config-projects/
  - (empty)
- input/
  - (empty)
- s3-src/
  - app/
    - index.js
    - package.json
  - buildspec.yml
  - README.md
  - template-configuration.json
  - template.yml
- s3-toolchain/
  - toolchain.yml
- templates/
  - config-template.json
  - input-template-cloudformation.json
  - input-template-codestar.json
  - policy-template-CodeStarTaggingPolicy.json
  - policy-template-ProjectStackServicePolicy.json
  - policy-template-ProjectStackTaggingPolicy.json
- generate.py

Next, you will need to make a copy of `templates/config-template.json`, place it in the `config-projects` directory, and rename the copy `config-project.json`. (To make this easier, you can run the following command):

`cp ./templates/config-template.json ./config-projects/config-project.json`

So, the sole file in `config-projects/` should now be `config-project.json` which will contain the settings we'll use to create the input.json files for both CodeStar and CloudFormation (the skeleton json samples we saw in the commands earlier).

#### config-projects/config-project.json

```JSON
{
    "source_files": {
        "toolchain_bucketname": "63klabs",
        "toolchain_bucketkey": "projectstack-templates/atlantis",
        "src_bucketname": "63klabs",
        "src_bucketkey": "projectstack-templates/atlantis"
    },
    "project": {
        "aws_account": "9912345678900",
        "aws_region": "us-east-1",
        "id": "my8ball",
        "stage": "",
        "env": "",
        "name": "",
        "description": "",
        "repository": "",
        "branch": "",
        "prefix": "",
        "role_arn": ""
    },
    "stack_parameters": {
        "ParameterStoreBasePath": ""
    },
    "tags": {}
}
```

For the tutorials we will leave the `source_files` section as is and will use the toolchain and src files from http://63klabs.s3.amazonaws.com/projectstack-templates/atlantis/

Under project make sure to provide your `aws_account` and `aws_region`.

Use a simple `id` such as `mycsproject` but keep it under 15 characters for CodeStar. (Later on we'll create a non-CodeStar project and there will not be a 15 character limit.)

We'll leave `stack_parameters` and `tags` as is for now.

Save your changes to the file.

### Generate the input files and get ready for some CLI action!

From within your command line, run `py generate.py`

You'll see a flurry of action displayed on your console as the input files are generated. Once complete note the final output of commands:

```
=========================================================================
--------------------------------- DONE! ---------------------------------
=========================================================================
Now run the necessary commands to create what you need:
-------------------------------------------------------------------------
aws codecommit create-repository --repository-name cobalt-cs --cli-input-json file://input/codecommit.json
aws cloudformation create-stack --cli-input-json file://input/cloudformation.json
aws codestar create-project --cli-input-json file://input/codestar.json
=========================================================================
```

### CodeStar from the CLI using generated input files

We'll use the third command:

`aws codestar create-project --cli-input-json file://input/codestar.json`

We can check its progress by using the next command:

`aws codestar describe-project --id my8ball`

(Be sure to change "my8ball" to what ever id you gave it in the config file.)

While we wait for the project to create, let's take a look at the input file we used in the create-project command `file://input/codestar.json`

```JSON
{
    "name": "8 Ball",
    "id": "my8ball",
    "description": "Project: my8ball Repo: my8ball Branch: main",
    "sourceCode": [
        {
            "source": {
                "s3": {
                    "bucketName": "63klabs",
                    "bucketKey": "projectstack-templates/atlantis/src.zip"
                }
            },
            "destination": {
                "codeCommit": {
                    "name": "awscodestar-my8ball"
                }
            }
        }
    ],
    "toolchain": {
        "source": {
            "s3": {
                "bucketName": "63klabs",
                "bucketKey": "projectstack-templates/atlantis/toolchain.yml"
            }
        },
        "roleArn": "arn:aws:iam::99999999999:role/service-role/aws-codestar-service-role",
        "stackParameters": {
            "ProjectId": "my8ball",
            "ProjectStageId": "my8ball",
            "CodeCommitBranch": "main"
        }
    },
    "tags": {
        "ProjectStackType": "awscodestar",
        "ProjectStackProjectID": "us-east-2/99999999999/awscodestar-my8ball",
        "ProjectStackProjectStageID": "us-east-2/99999999999/awscodestar-my8ball",
        "CodeCommitRepo": "awscodestar-my8ball",
        "CodeCommitBranch": "awscodestar-my8ball:main",
        "ProjectStackTemplate": "Atlantis.v01"
    }
}
```

You'll notice it took the skeleton and the config file and merged them together into the proper format. (You can also look at `input/cloudformation.json` and see that it took the same settings and put them into the proper format for a CloudFormation stack creation input file.)

You'll also notice that even though we left `tags` blank in the config, it added some standard tags to help us keep our resources organized and searchable. If you had any common tags to use across your projects such as creator, department, cost center, etc, you could add them to the config and they would be included.

Let's check the creation progress by using the the describe command again:

`aws codestar describe-project --id my8ball`

Once you see the `"state": "CreateComplete"` go to the AWS web console and navigate to the CodeStar project.

In the console for your CodeStar project you'll see you have all the resources as before when you created a CodeStar project through the Web Console.

Take it for a test drive:

- Click on the "View application" button and hit refresh a few times (don't forget to ask a yes or no question!)
- Go back to the dashboard and look at the chart for errors and invocations.
- Look through the resources
- Go into CodeCommit and make a change to `app/index.js` by adding a few more items to the array of responses such as "I dunno" or "Best you don't know".

```javascript
const answers = [ "It is certain",
//... add in any of the following or your own
		"I dunno",
		"Your guess is as good as mine",
		"You tell me",
		"Check back later",
		"Best you don't know",
    "That's a hard no",
    "Please don't ask that question again",
//...
    "My sources say no",
    "Outlook not so good"
];
```
Double check your commas and commit the changes. Then go back to the dashboard to view the Pipeline status.

## Naming resources

I briefly touched on how the IAM policies grant access based upon the structure of the name or ARN of a resource. If you look at the template file for your application you'll notice that resource name is explicitly given as `Name: !Sub '${Prefix}-${ProjectStageId}-lambda'` which will become `awscodestar-my8ball-lambda`.

Or, in the case of S3 buckets, CodeStar has a different format by placing a hyphen in the normal CodeStar:

```YAML
BucketName: !Join 
  - '-'
  - - !If [ IsCodeStar, 'aws-codestar', !Ref Prefix ] 
    - !Ref AWS::Region
    - !Ref AWS::AccountId
    - !Ref ProjectStageId
    - 'appdata'
```

And, in the toolchain.yml you'll see things like:

```YAML
PolicyName: !If [ IsCodeStar, "CodeStarWorkerCodeBuildPolicy", !Sub "${Prefix}WorkerCodeBuildPolicy"]
```

So, instead of using just `awscodestar` which is what we use for the value of `Prefix` in CodeStar projects, CodeStar also uses mixed case `CodeStar` for policies, and hyphens for S3 buckets as in `aws-codestar`.

This complicates things requiring the addition of `!If`s and `!Join`s when accomodating CodeStar. It also means that we need to explicitly name some resources even when we've been taught it is best SAM practice to just let CloudFormation name our resources for us. When resources are not given a name they are typically assigned a name by CloudFormation in the `${StackID}-${resourceLogicalId}-${randomchars}` format. This still would have worked very well in assigning IAM policies based on resource names except for Policy and S3 bucket names.

Unless we take the AWSCodeStarServiceRole and make our own copy with these corrections (removing the hyphen, lowercasing all references to the awscodestar prefix) we must continue to use the complicated exceptions for CodeStar projects. But, if we make our own AWSCodeStarServiceRole then we loose the benefits of having an AWS managed role.

In the next tutorial we'll actually use modified copy of the AWSCodeStarServiceRole so that `${Prefix}` is used in all resource names. While you can still keep the Ifs and Joins in resource name fields to keep your SAM template compatible with CodeStar, you can remove them if you have no plans on using CodeStar.

## Why you might still use CodeStar

While CodeStar isn't the best option for multi-stage, multi-deployment projects, it is good for smaller projects and experimentation. Sometimes it is nice to take a copy of your code and spin up an instance outside of, and isolated from, your development pipeline as you experiment or prototype in a sandbox. CodeStar creates your repository and deployment in one step, therefore it is easy to create sandboxes, prototypes, or learning labs without worry of the code being merged back into your development pipeline.

When you are done experimenting and learning, and perhaps obliterating any once-working code, you can just take what you learned, destroy the instance and either start over with a fresh copy or head back to regular development.

So, before you strip out all references to CodeStar in your SAM template, consider the benefits of having CodeStar as a sandboxing tool at your disposal.

## Documentation

TODO
