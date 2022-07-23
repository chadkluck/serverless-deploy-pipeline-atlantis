# Serverless Application Model + CodeStar

This is a sample of the Serverless Application Model that deviates from the traditional "Hello World" example as instead it returns JSON formatted predictions.

It is an extention of the SAM 8-Ball example. This version modifies the SAM 8-Ball example by placing it inside of a CodeStar project.

Once the CodeStar project has been created, you may access the CodeCommit repository and utilize local `sam` commands to develop and test locally. To deploy your code all you need to do is commit to the `master` branch of the repository.

## Set Up Local Machine

AWS SAM CLI extends the AWS CLI, so if you already have AWS CLI installed, you may be able to skip a few steps.

The following steps are taken from chapter 2 of _Running Serverless_ by Gojko Adzic.

### Python

Check python to make sure it is installed. Install it if it is not already.

`python --version`

<https://www.python.org>

### PIP

Do same with pip

`pip --version`

<https://pip.pypa.io>

### AWS CLI

`aws --version`

If not installed:

`pip install awscli`

<https://docs.aws.amazon.com/cli>

### Docker

Install Docker to simulate the Lambda execution environment. The free community Docker Desktop tools is all you need for local testing.

<https://www.docker.com/products/docker-desktop>

NOTE: Docker will not run on Windows 10 Home Edition.

### Node

`node --version`

<https://nodejs.org>

I recommend 12 or later.

### SAM Command Line Tools

#### Homebrew

`brew tap aws/tap`
`brew install aws-sam-cli`

#### Not Homebrew

`pip install aws-sam-cli`

#### Verify

After install:

`sam --version`

And you should get something like: `SAM CLI, version 0.16.1`

## Set up your access credentials

AWS SAM CLI uses the same credentials from AWS CLI. You can skip this step if you are already using AWS CLI to access your AWS resources.

You will need an access key ID and secret key ID (Note: For enterprise managed accounts this is set up differently)

Note that there are many ways to do this so that the IAM user has restricted access. If you are on your personal account the following steps are okay, after all, you are master of your own domain. If you are on an organizationl account where changes will impact other projects and people, follow the practices of your IT org.

The following steps are (for the most part) taken from chapter 2 of _Running Serverless_ by Gojko Adzic. For any alternate steps, or troubleshooting, I would refer you to the book.

1. Sign into the AWS Web Console at <https://aws.amazon.com>
2. Select the IAM service
3. In the left-hand IAM menu, select Users
4. Click on the Add User button
5. On the next screen, enter a name for the user account then, in the "Select AWS access type" section, select Programmatic acccess.
6. Click the Next button to assign permissions, then select Attach existing policies directly
7. In the list of policies, find the PowerUserAccess and IAMFullAccess policies and tick the check boxes next to them
8. You can skip the remaining wizard steps.
9. The final page will show you the access key ID and show a link to reveal the secret key. Reveal the secret key and copy both keys somewhere.

Once you have the keys run the following: `aws configure`

Paste in the keys when prompted. For region use `us-east-2` or whatever your default region should be. For default output use `json` or press Enter to keep it unset.

Check it out: `aws sts get-caller-identity`

### If you already have a user account

Make sure the following roles/permissions are set up:

- arn:aws:iam::aws:policy/AWSLambdaFullAccess
- arn:aws:iam::aws:policy/AmazonAPIGatewayAdministrator
- arn:aws:iam::aws:policy/IAMFullAccess

Also create a new policy for CloudFormation:

```JSON
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Effect": "Allow",
            "Action": "cloudformation:*",
            "Resource": "*"
        }
    ]
}
```

These are still pretty wide permissions, and are best reserved for sandbox and development, not production environments. Typically you'll want to segregate dev units by naming conventions in the arn. We'll get to that later.

## Tutorial

The book _Running Serverless_ by Gojko Adzic will walk you through creating a CloudFormation template and Node.js script and is highly recommended.

The commands below will give you a quick hands on approach, but the actions behind the commands are explained better in the book.

One key to understanding SAM and eventually CodeStar is to occasionally look under the hood and understanding as you progress. A lot is automactially done for you as you start out, but as you see and begin to understand the magic, you can wield the power offered by the platform.

If you just want to take SAM for a test drive without diving into the file structure you can do so now with the 8 Ball app.

## Build, Package, and Deploy

First, you will need a bucket to store your build package. If you do not yet have one, run the following command:

`aws s3 mb s3://<BUCKET-NAME>`

(Replace `BUCKET-NAME` with your own bucket name, perhaps with _yourname-test_ so you remember to delete it when finished. You'll actually want a bucket with proper security and retention policies anyway when you move to real, production-type projects.)

`sam build`

`sam package --s3-bucket <BUCKET-NAME> --output-template-file output.yaml`

(Replace `BUCKET-NAME` with your own bucket name)

`sam deploy --template-file output.yaml --stack-name sam-8ball-1 --capabilities CAPABILITY_IAM`

## You can also try

You can also change `sam-8ball-1` to another name and have a second stack. For example, you could have a test and production stack such as `sam-8ball-test` and `sam-8ball-prod`

`sam deploy --template-file output.yaml --stack-name sam-8ball-test --capabilities CAPABILITY_IAM`

`sam deploy --template-file output.yaml --stack-name sam-8ball-prod --capabilities CAPABILITY_IAM`

You can then deploy your code changes to either the test or prod stack.

Once the stack is deployed, you can go into AWS Console and poke around the stack in CloudFormation. You'll notice resources, outputs, and the template used.

You will need to find the API URI in the Stack resources to call up a prediction. To do this you can go into your Stack within CloudFormation, click on the resources tab and then click on the Physical ID for ServerlessRestAPI. This will take you to API Gateway. (You could have just gone to API Gateway directly but you would have missed this tour.) Across the top you'll see APIs > sam-8ball-1 (somerandchars) where somerandchars is the ID of your API.

Copy those random characters and make a link like so:

`https://<somerandchars>.execute-api.<region>.amazonaws.com/Prod/`

Be sure to replace `<somerandchars>` and `<region>` with your own.

Think of a Yes/No question and then head to that link for your answer. Think of new questions and hit refresh.

## CloudWatch Logs

Cloudwatch logs were also created for you automatically with your Lambda function. To view your logs go to CloudWatch and click on Log Groups. You can do a search for `/aws/lambda/sam-8ball-1-EightBallFunction` to view the logs. (There won't be anything, not even a Cold Start notification if you haven't run your function yet. Remember, Lambda functions are only "running" when triggered! It's serverless! No trigger, no boot, no run!).

You should see a COLD BOOT notification. This runs when your Lambda function executes for the first time after deploy, or idle timeout (30-45min).

You'll notice that if you hit refresh for a prediction (after a few seconds) you'll get a new log entry and you won't have a cold start. That's because Lambda is already loaded and remains ready while in idle. This idle state can last between 30 and 45 minutes. Come back in an hour and hit refresh and you should see a Cold Start. If your function is triggered regularly within that window you'll see fewer cold starts.

Oh, and of course you'll notice a log of predictions. You can format log outputs so they can be easily parsed by CloudWatch dashboards. But that is beyond the scope of this simple app.

Oh, and you can view real-time logs from the AWS-CLI without having to go into CloudWatch:

`sam logs -n EightBallFunction --stack-name sam-8ball-1`

By default this will be 10 minutes worth of logs. You can specify start and end times as well. You'll have to Google how to do that later othwerwise you'll never get through this README.

You can also get continuous logs:

`sam logs -n EightBallFunction --stack-name sam-8ball-1 --tail`

(It will, however, go back to the regular command prompt after a few minutes)

Now hit refresh on your browser and watch the log update! (after a few second delay)

Note how the logs give some additional diagnostics such as duration and memory used. Compare duration of log entries for Cold Starts vs non-cold starts. We're talking milliseconds in this example, barely noticable. It depends on how much housekeeping you have to do during cold start initialization (load external files, get parameters from parameter store, etc).

## Define your own API Gateway

Because the Lambda function uses an API event, CloudFormation automatically created a basic API Gateway resource for you.

This is fine, but as you create advanced applications you may want to define your own API Gateway with advanced functions such as request or IP blocking, or even routing endpoint paths to different Lambda functions.

In `template.yml` you'll notice several commented out lines. Uncomment them (except for the real comments) and re-build, re-package, and re-deploy your application.

During the CloudFormation stack changeset display you'll notice the old ServerlessRestAPI will be deleted and replaced with the new one.

After the deploy you'll also notice a new output after CloudFormation completes, called `Outputs`. It was created by the `Outputs` section in your template. This lists the new domain to access your app. This domain will not change unless you delete the API resource from your template, or give it a new logical name. You can add things like notes in this section.

It is important to note that CloudFormation does not delete already created resources from your template. It just updates them if there are any changes.

From the `Outputs`, copy the new URL and go there in your browser. From here on out, unless you delete the resource (or rename it) in your template, this shouldn't change between deploys.

## Resource names

In the template example, resources are not given names, we have allowed CloudFormation to generate random resource names. While recommended practice, in some environments this may not be desired. For one, you can't create IAM policies that restrict users to resources based on name. For example, if your organization uses a prefix to identify resources that belong to org units.

One of the reasons it is bad practice to give your resource a name in a template is that you can't deploy the same template twice as there would be name conflicts. In the `sam-8ball-test` and `sam-8ball-dev` example, if we were to have given our resources names in the template the second deployment would have failed because there would be a naming conflict.

One way to get past that is to pass a parameter for _environment_ and tack that on the end of resource names. However, if you were deploying a cache invalidator for several different departments you may still come up with a conflict.

One solution to allow for naming within the template is to use the method AWS CodeStar uses. It generates names based on a unique project ID. Because CodeStar Project IDs need to be unique within an account, it can enforce uniqueness. (It also adds the region and account id to S3 buckets so they can be unique)

So, for CodeStar projects, a Stage and Project ID parameter are passed to the template and used in generation of the resource names.

## Repository

You can commit your code to a repository. Just have a `.gitignore` file with the following:

```TEXT
.*
!/.gitignore
output.yaml
```

Temporary build and package files are placed in an _.aws-sam_ folder so you don't need that in your repo, and you don't need _output.yaml_ either.

After you commit your changes and are ready for a deploy, just build and deploy.

## Pipeline and AWS CodeStar

If you are familiar with Code Pipeline you've probably noticed that you are manually performing the Build and Deploy steps.

If you are not familiar with Code Pipeline, well, you are manually performing the Build, Package, and Deploy steps and you can actually automate this.

Typically, when creating a development pipeline, there is a branch in your Code Repository that you commit finished code to. Suppose you develop and test locally from the _dev_ branch. When you are ready for the next stage, you can merge your changes into the next branch such as _test_ or _production_.

If you create a CodePipeline then when you merge and push your changes to your _test_ or _production_ branch Code Pipeline monitors these branches for changes and when new changes are commited, kicks off a build, package, and deploy process.

This is where I make a plug for AWS CodeStar. However, learning CodeStar and then CodeStar CLI is another progression in understanding SAM. Once you have a lot of concepts of SAM figured out, you may want to start looking into seeing if CodeStar is right for you.

If you are fine setting up your repo, building, packaging, and deploying manually from the CLI, then that's okay. But if you need more automation then look into CodeStar.

CodeStar will build you a repository, a pipeline, and a project dashboard. It will also allow you to add team members and connect to issue trackers like JIRA.

As a bonus, you still get AWS-SAM-CLI functions such as `sam logs -n EightBallFunction --stack-name sam-8ball-1 --tail` in CodeStar because it is all CloudFormation Stack and SAM based.

Also, CodeStar uses a standard naming convention for all resources which makes it easier to set up permissions boundaries between groups within an organization. (For example, if you name all your projects with a `dept-projectname` ID where `dept` is your department/unit, then you can set up IAM policies that allow developers in that department/unit to have access to only resources with the `dept-` prefix. (`awscodestar-dept-*` to be exact.)). Note that CodeStar project IDs are limited to 15 characters, so after you add a 3 to 4 letter department code and a dash, we're basically back to 8 character filename days of DOS.)

First, in the CodeStar online console, use one of the templates to start a test project. I doubt any real production projects will come out of this so think of it as a sandbox to just play around in. Note that templates with things like Elastic Beanstalk and EC2 will cost money. Be sure to delete those projects when done.

After you have built a few projects using the web console, start checking out tutorials on using CodeStar from the AWS-CLI. That is where the fun comes in! Once you learn more about CodeStar templates (which are templates that create your development environment wrapped around your application template and code) you can create project templates that lock down IAM policies and expand your project to have multiple pipelines (such as test and production).
