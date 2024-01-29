# READ ME 3: Create or Update Deploy Pipeline CloudFormation Stack Using pipeline-toolchain.yml

The pipeline-toolchain.yml file is a CloudFormation template that creates the deployment pipeline for your application. The generated CloudFormation stack will have `*-deploy` appended to the name as well as the "stage" assigned to a specific branch in your CodeCommit repository (test, beta, prod, main, etc). There will be a deploy stack for each of the stages/branches you wish to deploy from.

Though you will most likely always have a prod stage tied to your main/master branch, you can always create and destroy stacks related to your test and dev branches as needed. Creating new deploy stacks is as easy as 1. having a branch to deploy from, and 2. following the steps below to create a deploy pipeline stack.

Each deploy pipeline monitors a specific branch in the CodeCommit repository and automatically kicks off a deployment when changes are committed to it. The application has its own CloudFormation infrastructure stack with `*-infrastructure` appended to it. The infrastructure stack manages all the resources (S3, API Gateway, Lambda, DynamoDb, etc) needed to run your application. The deploy stack only manages the pipeline and only needs to be updated if you are modifying the way the pipeline operates.

**REMEMBER:** For each "-deploy" stack, there will be a corresponding "-infrastructure". The deploy stack created the Code Pipeline that monitors the CodeCommit repository. Committing code to a branch monitored by the pipeline will cause it to execute updates to the infrastructure stack. The deploy stack ONLY creates the pipeline for monitoring and executing changes. If you need to modify the pipeline, you can update the deploy stack template. Your application resides in the application infrastructure stack.

## Crate a Deploy Pipeline Stack

There are 3 ways to create the deployment pipeline.

1. Upload `pipeline-toolchain.yml` through the CloudFormation web console (Recommended for starters)
2. Point to the 63K Labs S3 bucket (or your own) through the CloudFormation web console
3. Use the AWS CLI (Command Line Interface) (Advanced)

I will cover "Option 1" for this tutorial, however, as you become familiar with CloudFormation you may explore Options 2 and 3 by using the steps outlined under "Edit or Replace" below.

### Upload pipeline-toolchain.yml from Local Machine

1. Go to the CloudFormation AWS Web Console and choose "Create stack" with new resources.
2. Leave "Template is ready" checked. 
3. Under "Specify template" choose "Upload a template file".
4. Choose the pipeline.toolchain.yml file and upload.
5. "Stack name": `PREFIX-hello-world-test-deploy` (where `PREFIX` is the prefix you chose in your IAM policy)
6. Update the parameters according to the prompts and requirements.
   - For Prefix use the prefix you chose.
   - For ProjectId use `hello-world`
   - You will be using `test` for StageId and `TEST` for DeployEnvironment.
   - Leave S3BucketNameOrgPrefix empty (unless you entered one in the CloudFormation-Service-Role IAM).
   - Enter your email address for the AlarmNotificationEmail.
   - Enter the exact name of the CodeRepository you created and use the `test` branch.
7. Go to next and enter the following tags (we'll only create 2 for now):
   - For key enter `Atlantis` with value `application-deploy`
   - For key enter `atlantis:Prefix` with value `PREFIX` (Your prefix value lower case)
8. Under Permissions choose the IAM role `PREFIX-CloudFormation-Service-Role`.
9. For Stack failure options choose Roll back all stack resources.
10. Click Next.
11. Check the box for acknowledging AWS may create resources. (So you don't incur charges after this tutorial is created you may delete the infrastructure stack and then the deploy stack.)
12. Watch the stack update progress. Hopefully it is successful!

Once the deploy stack is finished creating the pipeline, it will check the CodeCommit repository and begin creation of the infrastructure stack.

You can always check the progress of the pipeline by going to the deploy stack in CloudFormation > Outputs > Pipeline.

## Customizing your Pipeline Toolchain

Right now the `pipeline-toolchain.yml` template creates a Code Pipeline with the proper permissions to create an infrastructure stack with a Lambda function, API Gateway, DynamoDb, S3 buckets, alarms, CloudWatch logs, and CloudWatch Events.

You may want to add additional resources such as databases, EC2 instances, VPC connections, and more. Following the principle of least privilege, the current toolchain does not have permission to add these to the infrastructure stack.

You can add additional permissions to the ${Prefix}-Worker-${ProjectId}-${StageId}-CodePipelineRolePolicy IAM policy in pipeline-toolchain.yml and update the CloudFormation stack.

You may also make other modifications as necessary. However, outside of adding additional IAM policies, reducing policy scope, or adding suggested tweaks, the pipeline stack will rarely be updated.

If you make customizations to the pipeline-toolchain template, you may wish to store a copy in the repository with your infrastructure template. Though updating the deploy stack is not automatic, it will help you keep tabs on your deploy template.

Once you have made modifications to your deploy pipeline template follow the instructions below to update.

## Create, Edit, or Replace Existing CloudFormation -deploy Stacks

NOTE: This **pipeline-toolchain.yml** template is for a **Deploy Pipeline (-deploy)** stack! **NOT** your application **Infrastructure (-infrastructure)** stack!

If you are replacing the entire contents of the template file then you can do this one of two ways:

1. Upload `pipeline-toolchain.yml` from your local machine
2. Point to the 63klabs S3 Bucket (or your own bucket)
3. Edit Template "In Place" in the Template Designer
4. Create or Update the stack using AWS CLI (Command Line Interface)

Note! If you have made your own modifications by adding additional permissions or resources, replacing the entire template will remove your changes. In that case, it is recommended you either manually update the pieces of code that need updating following the instructions in each update, or make note of your changes and re-implement them.

If you are updating pieces of the template manually "In Place" by following the update instructions then you can edit the appropriate areas in the template editor.

### Option 1: Upload from Local Machine

1. Go to your `-deploy` stack in the CloudFormation AWS Web Console and choose Update
2. Choose "Replace current template"
3. Choose "Upload a template file"
4. Upload your file
5. Update any Parameters and Tags on the next page
6. Choose the deployment role (Typically something like `projectstack-service-role`) If unsure look at the Stack Info/Overview/IAM Role assigned to similar Deploy stacks.
7. Check the box for acknowledging AWS may create resources.
8. Watch the stack update progress. Hopefully it is successful!

### Option 2: Point to the S3 Bucket

1. Go to your `-deploy` stack and choose Update
2. Choose "Replace current template"
3. Choose "Amazon S3 URL" and enter in `https://63klabs.s3.amazonaws.com/projectstack-templates/atlantis/toolchain.yml` (Or from your own bucket--must be publicly available)
4. Update any Parameters and Tags on the next page
5. Choose the deployment role (Typically something like `projectstack-service-role`) If unsure look at the Stack Info/Overview/IAM Role assigned to similar Deploy stacks.
6. Check the box for acknowledging AWS may create resources.
7. Watch the stack update progress. Hopefully it is successful!

### Option 3: Edit Template "In Place" in the Template Designer

1. Go to your `-deploy` stack and choose Update
2. Choose "Edit template in designer" and then the button "View in Designer"
3. You will see a code section at the bottom of the diagram.
4. You can do one of two things:
    1. Copy the entire contents of the new template file and paste it into the designer
    2. Perform edits within the designer
5. When finished, choose "Validate"
6. Once validated, choose "Upload" (Cloud icon with up arrow)
7. Update any Parameters and Tags on the next page
5. Choose the deployment role (Typically something like `projectstack-service-role`) If unsure look at the Stack Info/Overview/IAM Role assigned to similar Deploy stacks.
6. Check the box for acknowledging AWS may create resources.
7. Watch the stack update progress. Hopefully it is successful!

### Option 4: Create or Update using the AWS CLI

This option is outlined in [README: Use AWS CLI to Create and Update Deploy Pipeline CloudFormation Stack](./cli/README-CLI.md).

It may be beneficial to use this option as you can maintain input files that define your stack using parameters and tags. This is helpful as it avoids manual entry, is re-producible, self-documents, and maintains the concept of infrastructure as code.

Other similar options that avoid the Web Console and follow Infrastructure as Code are using Terraform and AWS CDK for the process of creating and updating the deploy pipeline stack. (Exploring and implementing those options are far beyond the scope of this template and tutorial.)

## Change Log

Once you have your pipeline set up you may want to watch the [CloudFormation Template for a Deployment Pipeline (CI/CD)](https://github.com/chadkluck/serverless-deploy-pipeline-atlantis) repository for any updates. Using the instructions for editing your deployment pipeline stack above you can walk through the instructions in the Change Log and make updates to your deploy pipeline stack.

## Documentation

Next: [README 4: Tutorial](../doc/README-4-Tutorial.md)
Previous: [README 2: CodeCommit Repository](../doc/README-2-CodeCommit-Repository.md)
Back to the Beginning: [README 0: Start Here](./README-0-Start-Here.md)
