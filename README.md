# CloudFormation Template for CI/CD using AWS CodePipeline

This CloudFormation template will create an AWS CodePipeline that monitors a single CodeCommit branch for changes and then deploys the application to a separate application infrastructure stack. It is recommended that you familiarize yourself with CloudFormation and CodePipeline.

The intent is to bridge the gap between pieced together tutorials (and solutions from Stack Overflow) and deploying practical, production ready solutions.

- Precisely scoped IAM Policies and Roles are created for you, your team, and application (more secure, principle of least privilege)
- Structured naming and tagging (better organization)
- No need to start from scratch
- No reason to create a messy application base and say "I'll structure, organize, and add security controls later"
- A tutorial for creating production-ready applications rather than examples pieced together

## About

Each branch will have its own pipeline stack and application infrastructure stack. This allows you to separate dev, test, and prod, grant developer access via CodeCommit policies, and create or destroy temporary or per-developer/feature test and staging branches/pipelines as necessary.

- The CloudFormation Pipeline stack template creates the CodePipeline and resources (such as IAM roles and S3 artifact buckets). It only runs when you need to make changes to how the Pipeline operates.
- The AWS CodePipeline receives an event notification from the repository branch and in turn builds and deploys the application infrastructure template.
- The CloudFormation Infrastructure stack manages actual application resources.

The templates, documentation, and tutorials were created by an AWS Certified developer in hopes to bridge the gap between quick-start online examples and well-architected production-ready applications. The template is actively used in production and receives periodic updates for security and industry best practices.

This template can serve as a base or example template modified to meet your needs. It is developed with the Principle of Least Privilege, and can deploy applications that utilize S3, DynamoDb, Lambda, API Gateway, CloudWatch Logs, Alarms, and Dashboards right out of the box. The templates can be extended to meet your needs simply by adding the appropriate IAM policies to the CloudFormation Role. For example, your developers cannot add Event Bridge or EC2 instances to their application infrastructure unless you first add the appropriate IAM policies to the CodePipeline Cloud Formation Role.

As you begin to look under the hood you can use it as a model for learning AWS Cloud Concepts such as Infrastructure as Code (IaC), CloudFormation, AWS CodePipeline, and serverless architecture. Once you have played around with it, the sky is the limit as you add your own modifications for your own use case.

## AWS Costs

This deploy template will create resources necessary to provide an AWS CodePipeline. After performing any tutorials you will want to delete unused stacks so that you do not incur any unexpected costs. However, most experimentation, and even low production loads, rarely rise above [AWS Free Tier](https://aws.amazon.com/free).

> You get 1 free active pipeline per month. New pipelines are free for the first 30 days. "An active pipeline is a pipeline that has existed for more than 30 days and has at least one code change that runs through it during the month. There is no charge for pipelines that have no new code changes running through them during the month." [CodePipeline Pricing](https://aws.amazon.com/codepipeline/pricing)

In short: Pipelines can sit idle without incurring any cost.

You are also charged for AWS CodeBuild if you go over 100 build minutes per month. If you are committing and deploying only a few changes a month you should not see any charges for CodeBuild. If you are frequently committing changes for deployment several times a day, several days a week during the month, you may see charges. [CodeBuild Pricing](https://aws.amazon.com/codebuild/pricing)

To delete the stacks and resources refer to the Clean Up section.

## File Structure

There are 4 main directories in the root of this repository which corresponds to the 4 main steps necessary to get the solution up and running.

```text
/
|- application-infrastructure/
|   |- app/
|   |- buildspec.yml
|   |- template-configuration.json
|   |- template.yml
| 
|- cloudformation-pipeline-template/
|   |- template-pipeline.yml
|
|- iam-cloudformation-service-role/
|   |- SAMPLE-CloudFormationServicePolicy.json
|   |- Trust-Policy-for-Service-Role.json
|
|- scripts-cli/
|   |- settings/
|   |- cli/
|   |- pipeline-stack.py
|   |- service-role.py
```

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
|   |- settings/
|   |- cli/
|   |- pipeline-stack.py
|   |- service-role.py
```

### Application Infrastructure directory

This is where your application CloudFormation template and code reside. This entire directory needs to be placed at the root of your repository. CodePipeline will look for `/application-infrastructure/` in your repository when executing.

AWS CodePipeline will use `buildspec.yml` to run the build process and then utilize the CloudFormation template `template.yml` to create an application infrastructure stack.

The buildspec and template files are structured to receive environment variables to execute logic based on whether it is building a DEV, TEST, or PROD environment. You will not need separate buildspec files (such as `buildspec-test.yml`) for each environment. Utilize parameters and environment variables.

Utilize `template-configuration.yml` to add custom parameter values and tags to your application resources.

### Pipeline CloudFormation Template directory

This contains `template-pipeline.yml`, the CloudFormation template that defines CodePipeline and associated resources. This can be moved to where your organization stores and maintains cloud infrastructure templates (such as Terraform or AWS CDK scripts). You can convert the pipeline to a Terraform or CDK script, upload it through the console, or use the AWS CLI.

The pipeline template is also available from a public S3 bucket if you wish to use the latest version as-is.

There is a `scripts-cli/` directory that assists in generating input.json files and copy-paste commands for use with the AWS CLI rather than uploading the template through the web console.

### IAM CloudFormation Service Role directory

You will need permission to create the CloudFormation stack that in turn creates the AWS Pipeline and associated resources. CloudFormation needs a service role to assume and you need permission to use that service role.

This directory contains the Trust Policy and Service Policy that can be copied and pasted into the IAM console, or invoked using the AWS CLI. You can also use these files as templates to create Terraform or AWS CDK implementations to provision the roles and policies.

## Usage

Before you start you will need to think through and establish a `PREFIX`. It is recommended that your first time through you use the given prefix `acme`. Once you have completed your first run-though of the steps you will have a better understanding of how you can group permissions using different prefixes for your applications. Each prefix and service role can be assigned to different departments, teams, or application groups in your organization. A prefix is 2 to 8 characters (`acme`, `finc`, `ws`, `ops`, `dev-ops`, `sec`), all lower-case.

In the following steps you can replace `acme` with your own prefix. When `acme` is in all lower-case, use your prefix in all lower-case. When `ACME` is in all upper-case, replace it with your prefix in all upper-case. (However, when `acme` appears in tag keys leave it as-is.)

There are 3 main steps:

1. Create the CloudFormation Service Role and grant users access to assume it (Only needs to be done once per prefix used)
2. Create CodeCommit repository for your application infrastructure and code (Only needs to be done once per application)
3. Create Pipeline CloudFormation stack that provisions the CodePipeline which will deploy your application code (Can be done many times, once for each branch you wish to deploy to a separate instance)

### IAM: Create CloudFormation Service Role and Update User Roles to Use It

In order for the Deploy Pipeline stack to execute, it will need to assume an IAM role with proper permissions. A CloudFormation service role will need to be created before you can create any Pipeline stacks.

We will create a policy (`ACME-CloudFormationServicePolicy`) and attach to a new role (`ACME-CloudFormation-Service-Role`).

You will only need to do this once per prefix.

If you have chosen a prefix other than `acme` use that instead when naming your policy and role. A prefix can be your company or organization's stock ticker, abbreviation, or the abbreviation of an internal organization unit, department, or team. This helps identify ownership and delegate permissions. (Accounting (`acct`) developers may not update stacks assigned to Operations (`ops`)). You will use this prefix again when you create your deploy stack.

#### IAM Step 0: Make sure you have permissions to create roles

There are two ways to check this, either navigate through IAM and see what your permissions are, or try to create the role and see if it fails due to permissions. If you don't have permissions to create a role, either add the following to your user role permissions or contact your administrator:

```JSON
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Sid": "CRUDAtlantisServiceRole",
            "Effect": "Allow",
            "Action": [
                "iam:CreateRole",
                "iam:AttachRolePolicy",
                "iam:DetachRolePolicy",
                "iam:PutRolePolicy",
                "iam:GetRole",
                "iam:DeleteRole",
                "iam:TagRole",
                "iam:UntagRole",
                "iam:PassRole"
            ],
            "Resource": "*"
        }
    ]
}
```

This is an overly permissive statement as it allows you access to update any role (`"Resource": "*"`). If it is your own, personal AWS account that is fine, but if you are part of an organization you may be required to add a permissions boundary or scope down the resource to just the role you wish to manage (`arn:aws:iam::990123456789:role/ACME-CloudFormation-Service-Role`).

Also note that if you are passing this information to an administrator, they should also update any user roles that only need access to `iam:PassRole` as outlined in IAM Step 3. (Though you'll need the role ARN, this can be done before creating the role.)

#### IAM Step 1: Get the CloudFormationServicePolicy.json file ready

You can generate the CloudFormation Service Policy one of two ways:

1. Manually copy the file and do a manual search/replace for each of the parameters (denoted with '$' bookends such as $PARAM$).
2. Use the /scripts-cli/service-role.py script to easily generate ready-to-use files and AWS CLI commands.

##### Manually Copy and Perform Search/Replace

1. In the `/iam-cloudformation-service-role/` folder, make a copy of `SAMPLE-CloudFormationServicePolicy.json` and name the copy with your prefix instead of SAMPLE. The following command will do this assuming you are in the iam directory: `cp SAMPLE-CloudFormationServicePolicy.json ACME-CloudFormationServicePolicy.json`
2. Open the copy and do a Find and Replace for each of the following:
   - `$AWS_ACCOUNT$` = Your AWS account number. (ex: 990123456789)
   - `$AWS_REGION$` = Your AWS region (ex: us-east-1) This must be the region you will be deploying in.
   - `$PREFIX$` = The prefix (lower case) you chose. You can use `acme` if you wish but do not have to.
   - `$PREFIX_UPPER$` = The prefix (upper case) you chose. (ex: `ACME`). If you choose to do everything in lower case you can use lower case.
   - `$S3_ORG_PREFIX$` = Either replace with an empty string, or if you prefer, your organization's prefix for S3 buckets followed by a dash. (Example: `acme-` or leave empty) This is the only time you will append a dash to the end of any parameter.

> Note: This is the only time we will include an Upper-case Prefix. Instead, we use lower-case because S3 buckets must be in all lower-case and it would complicate automated provisioning if UPPERCASE, CamelCase, _and_ lowercase had to be accounted for. Also, mixing cases and using them inconsistently can be confusing.

##### Use the Script to Perform Copy and Replace

From within the `/scripts-cli/` directory, run the `service-role.py` script with your chosen prefix as an argument and follow the prompts. A default value will be listed within the square brackets, hit enter to accept the default value or enter your own.

(Note invoking Python via `python`, `py` or `python3` may differ depending on your set-up.)

`python service-role.py acme`

Additional information about [using the scripts and CLI](./scripts-cli/README.md) may be found in the READ ME located in the scripts-cli directory.

Once the script runs it will provide you with the two AWS CLI commands to create the role. You can choose to use the CLI commands or create the role through the Web Console and copy/paste the generated file manually. For either, follow the instructions below.

#### IAM Step 2: Create Service Role

The following instructions walk you though creating the role manually through the AWS Web Console. Instructions for creating the role using the AWS CLI are under IAM AWS CLI Step 2B: Create Service Role via AWS CLI. (You can also use it as a basis for Terraform or AWS CDK.)

You should still review Web Console instructions before proceeding to CLI instructions.

##### IAM Web Console Step 2A: Create Service Role via Web Console

###### IAM Web Console Step 2A.1: Create the CloudFormation Service Policy

Before we can attach a policy to the role we need to create the policy!

1. In the AWS Web Console go to IAM > Policies and "Create policy"
2. Click on the JSON button and paste in the json contents of `scripts-cli/cli/iam/ACME-CloudFormationServicePolicy.json` (the file you generated)
3. Go on to "Next".
4. Give it the name `ACME-CloudFormation-Service-Role` (replacing `ACME` with your chosen prefix in UPPER CASE) and a description such as `Created by [you] to create CloudFormation stacks for deployment pipelines`.
5. Add at least 2 tags. Note the casing and `:` in the tag keys. More on tags later.
   -  `Atlantis` with value `iam`
   -  `atlantis:Prefix` with the value of your prefix (lower case), and any additional tags you may want (like creator and purpose). 
6. Click on Create Policy.

###### IAM Web Console Step 2A.2: Add the Policy to the CloudFormation Service Role

1. Under IAM in the Web Console, choose "Roles" from the left-hand side.
2. Click on "Create role"
2. Leave "Trusted entity type" as AWS service, and from the "Use case list" choose CloudFormation. Go to "Next: Permissions"
2. In Filter policies search box, type in `ACME` (or your chosen prefix)
3. Check the box next to "_ACME_-CloudFormationServicePolicy" and click Next
4. Give it the name `ACME-CloudFormation-Service-Role` and a description such as `Allows CloudFormation to create and manage AWS stacks and resources on your behalf.`
5. Enter a tag `Atlantis` with value `iam`, `atlantis:Prefix` with the value of your prefix (lower case), and any additional tags you may want.
6. Create the Role

> Note: Again, you can create roles and stacks to segment permissions among your functional teams (e.g. `websvc` or `accounting`). Cool, huh?! Just make another copy of `ACME-CloudFormationServicePolicy.json` and do a new search/replace.

##### IAM AWS CLI Step 2B: Create Service Role via AWS CLI

Two Policy Documents are necessary:

- `/iam-cloudformation-service-role/Trust-Policy-for-Service-Role.json` (Same for all CloudFormation Service Roles)
- `/scripts-cli/cli/iam/ACME-CloudFormationServicePolicy.json` (Generated per prefix.)

You will find the CLI commands for `iam create-role` and `iam put-policy` in the cli-acme.txt document.

The Trust Policy specifies the trusted service (CloudFormation) which is allowed to assume the role we will be creating. This policy is the same for all service roles we will create for CloudFormation and must be attached to the role using the `--assume-role-policy-document` parameter during the create role process.

The Service Policy specifies the permissions the CloudFormation service will have when it assumes the CloudFormation Service Role and creates, updates, or deletes the CodePipeline and associated resources. The sample service policy must be updated to reflect your AWS Account ID, Region, Bucket Prefix, and your Prefix.


##### IAM AWS CLI Step 2B.1: Create Role and attach Assume Role and Service Policies

We will need to use two commands, `aws iam create-role` to create the role, attach the assume role policy, and tag it. Then, we will use `aws iam put-role-policy` to put the necessary permissions on the policy.

Follow instructions in the cli-*.txt document making sure you are executing the commands from the /scripts-cli/cli/iam directory. Adjust the `file://` location to the trust policy and policy document if necessary.

```bash
aws iam create-role --path /dev-ops/ \
	--role-name ACME-CloudFormation-Service-Role \
	--description 'Service Role for CloudFormation Service to create and manage pipelines under the 'acme' prefix' \
	--assume-role-policy-document file://../../../iam-cloudformation-service-role/Trust-Policy-for-Service-Role.json \
	--tags '{"Key": "Atlantis", "Value": "iam"}' '{"Key": "atlantis:Prefix", "Value": "acme"}' '{"Key": "Department", "Value": "Acme Web Services"}' '{"Key": "Creator", "Value": "Jane Doe"}'

```

You'll then see output upon successful completion of the role's creation. Now you need to attach the policy:

```bash
aws iam put-role-policy --role-name ACME-CloudFormation-Service-Role \
	--policy-name ACME-CloudFormationServicePolicy \
	--policy-document file://ACME-CloudFormationServicePolicy.json
```

More information on creating and updating an IAM Role Using CLI:

- [AWS Documentation: Creating IAM Role using AWS CLI](https://awscli.amazonaws.com/v2/documentation/api/latest/reference/iam/create-role.html)
- [AWS Documentation: Updating IAM Role using AWS CLI](https://awscli.amazonaws.com/v2/documentation/api/latest/reference/iam/update-role.html)

##### IAM Alternate Step 2C: Terraform or CDK

You can always take the trust and permissions policy and adapt it to a Terraform or AWS CDK process for creating and maintaining your roles.

#### IAM Step 3: Update User to Assume Role

Note that if you are the only user in your account and/or you will be using the same user role that you gave the CreateRole permissions to in IAM Step 0, this has already been done if you kept `iam:PassRole` in the `Action` field from before. You may then skip this step.

The user role you use to access the Web Console or submit CLI commands will need the following IAM Policy added (Replace `$AWS_ACCOUNT$` and `$PREFIX_UPPER$` with appropriate values). You can create it as a stand alone policy and attach it to a role, or add it to the inline policy statement. If you create it as a stand alone policy I recommend tagging it with: `Atlantis` with value `iam`, `atlantis:Prefix` with the value of your prefix (lowercase), and any additional tags you may want.

```JSON
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Sid": "AllowUserToPassSpecificCloudFormationServiceRole",
            "Effect": "Allow",
            "Action": [
                "iam:GetRole",
                "iam:PassRole" 
            ],
            "Resource": "arn:aws:iam::$AWS_ACCOUNT$:role/$PREFIX_UPPER$-CloudFormation-Service-Role"
        }
    ]
}
```

For example, if you were updating a role used by your Web Service developers in account `990123456780` and you created `WEBSVC-CloudFormation-Service-Role`, you would add something like the following to their IAM role policy statement:

```JSON
{
    "Sid": "AllowUserToPassSpecificCloudFormationServiceRole",
    "Effect": "Allow",
    "Action": [
        "iam:GetRole",
        "iam:PassRole" 
    ],
    "Resource": "arn:aws:iam::990123456780:role/WEBSVC-CloudFormation-Service-Role"
}
```

More Information on granting users permissions to pass roles:

- [AWS Documentation: Granting a user permissions to pass a role to an AWS service](https://docs.aws.amazon.com/IAM/latest/UserGuide/id_roles_use_passrole.html)
- [AWS Documentation: Tagging your AWS resources](https://docs.aws.amazon.com/tag-editor/latest/userguide/tagging.html)

### CodeCommit: Create Repository and Structure It

Once the service role is created it is time to set up your CodeCommit repository to store your application infrastructure.

You will need to create the CodeCommit repository and seed it with your application infrastructure before you can create the deploy pipeline. To get started, place the `/application-infrastructure/` into the root of the repository. You can replace it later with more functional code such as [Serverless Web Service Template for Pipeline Atlantis](https://github.com/chadkluck/serverless-webservice-template-for-pipeline-atlantis).

#### CodeCommit Step 1: Create the Repository

1. Create a code commit repository. (You can name it `hello-world`)
2. Clone the repository to your local machine.
3. Copy the `/application-infrastructure/` directory into the root of the repository and commit.
4. Create `dev` and `test` branches (you can create additional branches later)

Make sure the `/application-infrastructure/` directory stays in the root of your repository or CodePipeline will not know where to find your code!

You should now have a repository with 3 branches:

- main (sometimes master)
- test
- dev

Each branch should contain the same code.

When we create the first Deploy Pipeline CloudFormation stack we will have it monitor the "test" branch. Upon successful completion of the test deployment, we will create a production deployment from the "main" branch.

We will leave "dev" as a branch that doesn't have an automatic deploy. You can also create individual developer and feature branches in the future.

- [AWS Documentation: CodeCommit ](https://docs.aws.amazon.com/codecommit/latest/userguide/welcome.html)
- [AWS Documentation: AWS Serverless Application Model (SAM)](https://docs.aws.amazon.com/serverless-application-model/latest/developerguide/what-is-sam.html)

### CloudFormation: Create Deploy Pipeline Stack

The template-pipeline.yml file is a CloudFormation template that creates the deployment pipeline for your application. The generated CloudFormation stack will have `*-pipeline` appended to the stack name as well as the "stage" assigned to a specific branch in your CodeCommit repository (test, beta, prod, main, etc). There will be a pipeline stack for each of the stages/branches you wish to deploy from.

Though you will most likely always have a prod stage tied to your main/master branch, you can always create and destroy stacks related to your test and dev branches (and feature test branches) as needed. Creating new pipeline stacks is as easy as 1. having a branch to deploy from, and 2. following the steps below to create a deploy pipeline stack.

Each deploy pipeline monitors a specific branch in the CodeCommit repository and automatically kicks off a deployment when changes are committed to it. The application has its own CloudFormation infrastructure stack with `*-infrastructure` appended to the stack name. The infrastructure stack manages all the resources (S3, API Gateway, Lambda, DynamoDb, etc) needed to run your application. The deploy stack only manages the pipeline and only needs to be updated if you are modifying the way the pipeline operates.

**REMEMBER:** For each "-pipeline" stack, there will be a corresponding "-infrastructure" stack. The pipeline stack created the CodePipeline and EventBridge rules that monitors the CodeCommit repository branch. Committing code to a branch monitored by the pipeline will cause it to execute updates to the infrastructure stack. The pipeline stack ONLY creates the pipeline resources for monitoring and executing changes. If you need to modify the pipeline, you can update the pipeline stack template. Your application resides in the application infrastructure stack.

There are 3 ways to create the deployment pipeline.

1. Upload `template-pipeline.yml` through the CloudFormation web console (Recommended for starters)
2. Point to the 63K Labs S3 bucket (or your own) through the CloudFormation web console
3. Use the AWS CLI (Command Line Interface) (Advanced)

#### CloudFormation Option 1: Upload template-pipeline.yml from Local Machine

1. Go to the CloudFormation AWS Web Console and choose "Create stack" with new resources.
2. Leave "Template is ready" checked. 
3. Under "Specify template" choose "Upload a template file".
4. Choose the template-pipeline.yml file and upload.
5. "Stack name": `PREFIX-hello-world-test-pipeline` (where `PREFIX` is the prefix you chose in your IAM policy)
6. Update the parameters according to the prompts and requirements.
   - For Prefix use the prefix you chose.
   - For ProjectId use `hello-world`
   - You will be using `test` for StageId and `TEST` for DeployEnvironment.
   - Leave S3BucketNameOrgPrefix empty (unless you entered one in the CloudFormation-Service-Role IAM).
   - Enter your email address for the AlarmNotificationEmail.
   - Enter the exact name of the CodeRepository you created and use the `test` branch.
7. Go to next and enter the following tags (we'll only create 2 for now):
   - For key enter `Atlantis` with value `application-pipeline`
   - For key enter `atlantis:Prefix` with your prefix value lower case
8. Under Permissions choose the IAM role `PREFIX-CloudFormation-Service-Role`.
9. For Stack failure options choose Roll back all stack resources.
10. Click Next.
11. Check the box for acknowledging AWS may create resources. (So you don't incur charges after this tutorial is created you may delete the infrastructure stack and then the deploy stack.)
12. Watch the stack update progress. Hopefully it is successful!

Once the deploy stack is finished creating the pipeline, it will check the CodeCommit repository and begin creation of the infrastructure stack.

You can always check the progress of the pipeline by going to the deploy stack in CloudFormation > Outputs > Pipeline.

#### CloudFormation Option 2: Point to Template in S3 Bucket

You can either upload the `template-pipeline.yml` file to your own S3 bucket, or use the one at `https://63klabs.s3.amazonaws.com/atlantis/v2/pipeline-template.yml`

If you use your own, you will need to list the path as `https://yourbucketname.s3.amazonaws.com/pathtoyourfile/pipeline-template.yml` even if it is not publicly accesible (public access blocked). It cannot be listed with the `s3:` protocol.

Use the same steps as in Option 1 but instead of choosing "Upload a template file" in step 3, choose S3 bucket and enter in the URL to the file.

#### CloudFormation Option 3: Use AWS CLI cloudformation create-stack

While you may think using the CLI requires a lot of typing, I have included scripts in /scripts-cli/ that make it super-easy and saves the CLI commands and input files you can use and re-use as you build, tweak, destroy, and re-build your stacks.

Instead of spending your time hand entering all the parameters and tags via the Web Console, you can just answer some prompts and have the scripts generate CLI commands to cut and paste! Plus, all the info is saved so you can just re-create stacks all over the place!

#### Run the Script and Execute CLI commands

From within the `/scripts-cli/` directory, run the `pipeline-stack.py` script with your chosen prefix, project ID, and stage ID as arguments and follow the prompts. A default value will be listed within the square brackets, hit enter to accept the default value or enter your own.

(Note invoking Python via `python`, `py` or `python3` may differ depending on your set-up.)

`python service-role.py acme sales-api test`

Additional information about [using the scripts and CLI](./scripts-cli/README.md) may be found in the READ ME located in the scripts-cli directory.

Once the script runs it will provide you with the AWS CLI commands to create the stack.

## Customizing your Pipeline Template

Right now the `template-pipeline.yml` template creates a Code Pipeline with the proper permissions to create an infrastructure stack with a Lambda function, API Gateway, DynamoDb, S3 buckets, alarms, CloudWatch logs, and CloudWatch Events.

You may want to add additional resources such as databases, EC2 instances, VPC connections, and more. Following the principle of least privilege, the current pipeline template does not have permission to add these to the infrastructure stack.

You can add additional permissions to the ${Prefix}-Worker-${ProjectId}-${StageId}-CodePipelineRolePolicy IAM policy in template-pipeline.yml and update the CloudFormation stack.

You may also make other modifications as necessary. However, outside of adding additional IAM policies, reducing policy scope, or adding suggested tweaks, the pipeline stack will rarely be updated.

If you make customizations to the template-pipeline template, you may wish to store a copy in the repository with your infrastructure template. Though updating the deploy stack is not automatic, it will help you keep tabs on your deploy template.

Once you have made modifications to your deploy pipeline template follow the instructions below to update.

## Create, Edit, or Replace Existing CloudFormation -pipeline Stacks

NOTE: This **template-pipeline.yml** template is for a **Deploy Pipeline (-pipeline)** stack! **NOT** your application **Infrastructure (-infrastructure)** stack!

If you are replacing the entire contents of the template file then you can do this one of four ways:

1. Upload `template-pipeline.yml` from your local machine
2. Point to the 63klabs S3 Bucket (or your own bucket)
3. Edit Template "In Place" in the Template Designer
4. Create or Update the stack using AWS CLI (Command Line Interface)

Note! If you have made your own modifications by adding additional permissions or resources, replacing the entire template will remove your changes. In that case, it is recommended you either manually update the pieces of code that need updating following the instructions in each update, or make note of your changes and re-implement them.

If you are updating pieces of the template manually "In Place" by following the update instructions then you can edit the appropriate areas in the template editor.

### Option 1: Upload from Local Machine

1. Go to your `-pipeline` stack in the CloudFormation AWS Web Console and choose Update
2. Choose "Replace current template"
3. Choose "Upload a template file"
4. Upload your file
5. Update any Parameters and Tags on the next page
6. Choose the deployment role (Typically something like `ACME-CloudFormationServiceRole`) If unsure look at the Stack Info/Overview/IAM Role assigned to similar Deploy stacks.
7. Check the box for acknowledging AWS may create resources.
8. Watch the stack update progress. Hopefully it is successful!

### Option 2: Point to the S3 Bucket

1. Go to your `-pipeline` stack and choose Update
2. Choose "Replace current template"
3. Choose "Amazon S3 URL" and enter in `https://63klabs.s3.amazonaws.com/atlantis/v2/template-pipeline.yml` (Or from your own bucket--must be publicly available)
4. Update any Parameters and Tags on the next page
5. Choose the deployment role (Typically something like `ACME-CloudFormationServiceRole`) If unsure look at the Stack Info/Overview/IAM Role assigned to similar Deploy stacks.
6. Check the box for acknowledging AWS may create resources.
7. Watch the stack update progress. Hopefully it is successful!

### Option 3: Edit Template "In Place" in the Template Designer

1. Go to your `-pipeline` stack and choose Update
2. Choose "Edit template in designer" and then the button "View in Designer"
3. You will see a code section at the bottom of the diagram.
4. You can do one of two things:
    1. Copy the entire contents of the new template file and paste it into the designer
    2. Perform edits within the designer
5. When finished, choose "Validate"
6. Once validated, choose "Upload" (Cloud icon with up arrow)
7. Update any Parameters and Tags on the next page
5. Choose the deployment role (Typically something like `ACME-CloudFormationServiceRole`) If unsure look at the Stack Info/Overview/IAM Role assigned to similar Deploy stacks.
6. Check the box for acknowledging AWS may create resources.
7. Watch the stack update progress. Hopefully it is successful!

### Option 4: Create or Update using the AWS CLI

This option is outlined in [README: Use AWS CLI](./scripts-cli/README-CLI.md).

It may be beneficial to use this option as you can maintain input files that define your stack using parameters and tags. This is helpful as it avoids manual entry, is re-producible, self-documents, and maintains the concept of infrastructure as code.

Other similar options that avoid the Web Console and follow Infrastructure as Code are using Terraform and AWS CDK for the process of creating and updating the deploy pipeline stack. (Exploring and implementing those options are far beyond the scope of this template and tutorial.)

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
