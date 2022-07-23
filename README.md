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

## Tutorial 1: CodeStar via Web Console

Using the template and starter source is as simple as having access to the toolchain and zipped code from an S3 bucket, providing information in `config-projects/config-projects.json`, generating the input files, and executing an AWS CLI to create either a CodeStar project or CloudFormation stack.

While just knowing CloudFormation and SAM is a great start, alone it does not allow you to manage production code. This project template can be used to further your understanding, experience, and implementation of a full production pipeline using SAM and CloudFormation.

### Step 0: Prerequisites and creating CodeStar Service Role

1. Understanding of SAM (Serverless Application Model)
2. A computer with AWS CLI, git, bash (or gitbash), and Python installed
3. Ability to run simple AWS CLI, git, bash, and Python commands (they will be provided for you)
4. An AWS account

If you don't meet these first set of requirements, then I recommend you check out the GitHub repository for 8Ball. It will walk you through setting up your computer and deploying your first SAM application. This tutorial will build upon that experience so it is recommended that you have created and deployed SAM projects using the AWS CLI prior.

And finally, prerequisite #5 is to create CodeStar Service roles.

#### Create CodeStar Service role

1. In the AWS Web Console go to IAM and create a new role
2. From the Use Case list choose CloudFormation and then go to "Next: Permissions"

Create the CodeStarTaggingPolicy:

1. Choose "Create Policy" (it will open in a new browser tab/window)
2. In the new tab/window, click on the JSON tab and paste in the json contents of `templates/policy-template-CodeStarTaggingPolicy.json`
3. Go on to "tags".
4. Add a tag `CodeStarProjectPolicy` with value `YES` and any additional tags you may want (like creator and purpose). Then Review.
5. Give it the name `CodeStarTaggingPolicy` and a description such as `Created by [you] to allow for tagging of CodeStar project roles` and hit Create Policy
6. Close that browser tab/window and go back to the Create Role tab in your browser. Hit the refresh icon.

Add the policies to the role:

1. In Filter policies search box, type in `CodeStar`
2. Check the boxes next to "CodeStarTaggingPolicy" and "AWSCodeStarServiceRole"
3. Go on to Next and enter a enter a tag `CodeStarProjectPolicy` with value `YES` and any additional tags. Then Review.
4. Give it the name `aws-codestar-service-role` and a description such as `Created by [you] to allow for CodeStar creation of resources.`
5. Create the Role

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

#### CodeStar Service Role permissions (add tagging for IAM resources created by CodeStar)

You may have noticed that in the config-project.json file there was a field for `role_arn` but we left it blank so that we could utilize the service role we created in the previous CodeStar tutorial. `arn:aws:iam::${acct}:role/service-role/aws-codestar-service-role`

However, let's modify that service role to add a policy to allow for tagging of created IAM resources (why this isn't included in the AWSCodeStarServiceRole I do not know)

1. Go into IAM and under roles, search for `aws-codestar-service-role`
2. Click on "Add inline policy" and go to the JSON editor. Paste in the json from `templates/policy-template-CodeStarTaggingPolicy.json` and go on to Review Policy.
3. Give it the name `CodeStarIAMTagging-inline` and hit "Create policy"

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

## Tutorial 3: CloudFormation project stack from the CLI

A CodeStar project is good for quick and dirty applications. Maybe proof of concepts, sandboxes, etc., but doesn't really have a development to production pipeline. Plus, it has limitations, such as:

- 15 character limit on ID
- Single branch/stage

If you want to push your project further and use CodeCommit for your complete development pipeline where each branch represents a depoloy stage (test, qa, production) then you will want to explore creating a project stack using CloudFormation.

It is a little more complex to set up but it is a lot easier now that you've done one or two CodeStar creations! So, if you skipped the CodeStar CLI tutorials go back and do them!

Once you've laid the groundwork in setting up your first project, adding additional stages and projects will go like clockwork.

Since we'll be adding additional deployment stages to our development pipeline, we'll start with a test stage in a test environment.

Go into `config-project.json` and set `stage` to `test` and `env` to `TEST` (case matters on both!). 

```JSON
  "id": "my8ball",
  "stage": "test",
  "env": "TEST",
```

We'll leave the project id the same (I'll explain later).

I'll also explain the difference between "stage" and "env" later as well.

### IAM Set-Up

Now that we've updated the config, let's get ready to add a few more IAM policies! You'll only need to do this once. This will be similar to the first few steps in **Tutorial 1** but with a few changes so that it is specific to project stacks.


1. In the AWS Web Console go to IAM and create a new role
2. From the Use Case list choose CloudFormation and then go to "Next: Permissions"

Create the ProjectStackTaggingPolicy:

1. Choose "Create Policy" (it will open in a new window)
2. In the new tab/window, click on the JSON tab and paste in the json contents of `templates/policy-template-ProjectStackTaggingPolicy.json`
3. Go on to "tags".
4. Add a tag `CodeStarProjectPolicy` with value `YES` and any additional tags you may want (like creator and purpose). Then Review.
5. Give it the name `ProjectStackTaggingPolicy` and a description such as `Created by [you] to allow for tagging of CodeStar-like project roles` and hit Create Policy
6. Close that browser tab/window and go back to the Create Role tab in your browser.

Create the ProjectStackServicePolicy:

1. Instead of using a managed policy like "AWSCodeStarServiceRole" we will be creating our own specific to the prefix "projectstack-". Again, choose "Create Policy" (it will again open in a new window)
2. In the new tab/window, click on the JSON tab and paste in the json contents of `templates/policy-template-ProjectStackServicePolicy.json`
3. Go on to "tags".
4. Add a tag `CodeStarProjectPolicy` with value `YES` and any additional tags you may want (like creator and purpose). Then Review.
5. Give it the name `ProjectStackServicePolicy` and a description such as `Created by [you] to allow for CodeStar-like creation of resources` and hit Create Policy
6. Close that browser tab/window and go back to the Create Role tab in your browser. 

Add the policies to the role:

1. Back on the Create Role page, hit the refresh icon.
2. In Filter policies search box, type in `ProjectStack`
3. Check the boxes next to "ProjectStackServicePolicy" and "ProjectStackTaggingPolicy"
4. Go on to Next and enter a enter a tag `CodeStarProjectPolicy` with value `YES` and any additional tags. Then Review.
5. Give it the name `projectstack-service-role` and a description such as `Created by [you] to allow for CodeStar-like creation of resources.`
6. Create the Role

Note: Again, this is very similar to creating the CodeStar role prior. The main difference in the policies is the prefix used (`projectstack-` instead of `CodeStar-`). Compare the JSON of the two polcies in each Role. If you want to create your own prefixes you can replace `projectstack` with what ever you like (e.g. `accounting`) and create roles to segment development teams. Cool, huh?! But hold off on that now.

### Update user to assume role

The account you use to submit the CLI commands will need the following IAM Policy added: 

```JSON
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Sid": "VisualEditor0",
            "Effect": "Allow",
            "Action": "iam:PassRole",
            "Resource": "arn:aws:iam::*:role/projectstack-service-role"
        }
    ]
}
```

### Create CodeCommit repository

With the roles created, and `config-project.json` updated, let's Generate Py! Yum!

In the CLI, run the command:

`py generate.py`

In the previous tutorial we created an input file for your CodeStar project using the `generate.py` script. There were input files generated to create your code repository as well.

Creating a CodeCommit repository, initializing it, and creating a branch isn't a single command line. You need to run a code commit create command and then run two more lines to create the branch you will be using for deployments.

You can just create the CodeCommit repository using the AWS Web Console but you will have to add your tags manually, create a first file, and create a new branch.

While you could use CloudFormation, like CodeStar does, it seems silly to maintain a stack for a single resource. (However, if you were to expand your repository's functionality with additional triggers, notifications, work-flows, etc, a CloudFormation template would assist in maintaining and replicating it.)

The nice thing about using the AWS CLI with the input file is that it uses what you put in the config and it takes less than 20 seconds (Depending on how quickly you can cut and paste 3 lines of commands).

So, just for experience, let's use the AWS CLI to create our repository and branch.

We'll be using 3 input files generated by the Python script, feel free to inspect them prior to submitting the commands.

1. Create the repository:
  - `aws codecommit create-repository --cli-input-json file://input/codecommit.json`
2. Perform the initial commit and make the "main" branch default:
  - `aws codecommit create-commit --cli-input-json file://input/codecommit-init.json`
  - `aws codecommit put-file --cli-input-json file://input/codecommit-init.json`
3. Create the "test" branch (since we are creating the "test" stage):
  - You will need to copy the `commitId` from the previous command result into `[commitId]`
  - `aws codecommit create-branch --commit-id [commitId] --cli-input-json file://input/codecommit-branch.json`
4. Check your work: 
  - `aws codecommit get-repository --repository-name my8ball`
  - Note the `cloneUrlHttp` value, you'll use this later to clone the repository to your local machine later.

You're done getting your repository ready!

A few notes:

- If you wanted a different branch in your new repository as default, you could change the branch in `codecommit-init.json` to whatever you want as the default branch. But most repositories use "main" or "master" as their default.
- You'll notice that in order to initialize the repository, we created a single text file called "hello.txt" with the contents "Hello, World" (which is "SGVsbG8sIFdvcmxk" encoded in base64 necessary for `fileContent`)
- In this example we are using the "test" branch. If we were going to use the "main" branch we wouldn't need to perform step 3 as we created "main" during the initial commit in step 2.
- You could also use `git` commands to create a new branch (e.g. `git checkout -b dev` and then `git push --set-upstream origin dev`).
- If you inspect the codecommit-branch.json file, you'll see that a commitId is already filled in with placeholder text. Placing the `--commit-id` parameter in the command will override this. So, essentially, the commitId in the input file is just a placeholder as it is required to be there, but not used.

### Load up your SAM application using git

Let's run the "get repository" command again to get the clone URL.

`aws codecommit get-repository --repository-name my8ball`

Copy the `cloneUrlHttp` value.

We are now ready to run the `git clone` command once you change directories in your command prompt to the directory you wish to clone the repository to.

Such as:

`cd ..` (to get out of the project stack directory)

`git clone [paste_cloneUrlHttp_here]` (will clone it into a new directory, `my8ball`)

Or, `git clone [paste_cloneUrlHttp_here] repo_my8ball` will clone it into a directory called `repo_my8ball`

Once you have cloned your repository, `cd` into that directory check out branches:

`git branch -a`

You should see:

```
* main
  remotes/origin/HEAD -> origin/main
  remotes/origin/main
  remotes/origin/test
```

Checkout the test branch:

`git checkout test`

If you perform `git branch` you should see that you are now in the test branch. (If you haven't already, you may want to make sure you are using a command line window that is set up with git or gitbash so that your working branch is displayed in your command prompt.)

```
clkluck@wallace-ii MINGW64 ~/projects/demo/v2/repos/my8ball (main)
$ git branch -a
* main
  remotes/origin/HEAD -> origin/main
  remotes/origin/main
  remotes/origin/test

clkluck@wallace-ii MINGW64 ~/projects/demo/v2/repos/my8ball (main)
$ git checkout test
Switched to a new branch 'test'
Branch 'test' set up to track remote branch 'test' from 'origin'.

clkluck@wallace-ii MINGW64 ~/projects/demo/v2/repos/my8ball (test)
$ git branch
  main
* test

```

Now, take the source files for your SAM application and place them into your repository directory.

When you run a `dir` or `ls` you should now see:

```
clkluck@wallace-ii MINGW64 ~/projects/demo/v2/repos/my8ball (test)
$ dir
app  buildspec.yml  hello.txt  README.md  template.yml  template-configuration.json
```

Feel free to delete the "hello.txt" file.

`rm hello.txt`

Now (assuming you have your git config set up with your credentials, email, and username) go ahead and push your changes which will now kick off a deploy!

`git add --all`

`git commit -m "Placed application in repo"`

`git push`

We'll also merge the changes into "main"

`git checkout main`

`git merge test`

`git push`

In the future, as you add more deployments you'll need to add the branch the project stack will deploy from first. Just create a new branch in the repository based off another branch before creating the new project deploy stack.

### Create Project Deploy Stack

We are now ready to create your project deploy stack!

Feel free to inspect the input file. You'll immediately notice it has a different structure from the codestar input file, especially the Tag and Parameter object. Since each generate.py creates both a CodeStar and CloudFormation input file you can compare them side by side.

Run the following to create the project stack.

`aws cloudformation create-stack --cli-input-json file://input/cloudformation.json`

Watch the progress on the AWS Console.

When it is complete you can go to the Outputs tab and use the link to go to the ProjectPipeline.

You should see that it detected a commit, and then built, or is building, the code which it will then deploy.

When the infrastructure stack has completed deploying, go into it's Output section and click on the WebAPI link. (Don't forget to ask a yes or no question!)

### Create another deploy stack

So the app is performing well, let's deploy it to production by attaching a production deploy stage to the "main" branch.

The stage name does not have to match the branch name.

In `config-projects.json` set the following:

```json
  "stage": "prod",
  "env": "PROD",
  "name": "",
  "description": "",
  "branch": "main"
```

Run the command:

`py generate.py`

Now run the command to create the stack:

`aws cloudformation create-stack --cli-input-json file://input/cloudformation.json`

Check progress in CloudFormation. Once the deploy stack is complete, go under Outputs and click on the Pipeline link and watch the CodeBuild and Deploy process.

After it is complete you'll see the new infrastructure stack. Go to its Output section and click on the WebAPI link (be sure to ask a Yes or No question!)

### Deploying changes

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

## Tutorial 4: On your own

Go ahead and update config-project.json for another stage and branch and create it. (You can use `staging`, `dev`, `qa`). Don't forget to set your env variable to `DEV` or `TEST`.

Once you've added a few new stages and branches, create a new project, maybe give it an ID of `my8ballv2`

`py generate.py` and create the CodeCommit, branches, and cloudformation stack.

Commit a few changes, and you're a pro!

### Deleting stacks

You can add stacks all day long, you can also delete them without affecting the branches. However, there is an order for deleting:

1. Delete the infrastructure stack. You may need to disable termination protection.
2. Empty the S3 bucket for the deploy. The bucket with the format: `${AWS::Region}-${AWS::AccountId}-${ProjectStageId}-deploy`
3. Delete the deploy stack. Again, you may need to disable termination protection.

### Congratulations!

You made it all the way through the tutorials.

Once you feel comfortable creating projects using CodeStar and CloudFormation, check out the advanced section below.

## Advanced

### Project IDs


### Stages and Environments

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

### Multiple stages off single branch

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

### Least Privilage and Naming Conventions

Both of these options use the same CloudFormation template (`codestar-files/toolchain.yml`) which utilizes CodeStar practices of applying best practice IAM policies to the app (the app only has access to the resources it creates) and its deployment pipelines. Because of this, some resources such as IAM policies will still have CodeStar in their name which can be used as a signifier that it was created using these practices and for permissions.

#### awscodestar-* and projectstack-* and creating your own prefix

All resource names should be in `[Prefix]-[ProjectStageId]-*` format as IAM policies are keyed on in the ARN and allow access based on this naming convention. This makes sure that only resources named `[Prefix]-[ProjectStageId]-*` only have access to other resources named `[Prefix]-[ProjectStageId]-*`.

`awscodestar` is the prefix used for CodeStar projects and cannot be changed. `projectstack` is the default prefix for non-CodeStar projects. If you add other prefixes (which can be used for namespaces to separate your organizations departments!) you will need to add additional Service Roles (See "Additional Project Namespaces (Prefixes)")

IAM policies differ slightly as you'll see `CodeStar-*` used.

You can create different namespaces for projects beyond `awscodestar-*` and `projectstack-*` for example `acct-*`.

This is useful so that you can put various groups into their own namespace with their own permissions. Maybe a team has access to `acct-*` resources but not `sales-*`

To do this create a copy of `policy-template-ProjectStackServicePolicy.json` and `policy-template-ProjectStackTaggingPolicy.json` and change `projectstack` to whatever you want. Then create a new role just the way you did in Step 0 for the CloudFormation project stack tutorial, for example, `acct-service-role`.

#### ProjectId and ProjectStageId

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
