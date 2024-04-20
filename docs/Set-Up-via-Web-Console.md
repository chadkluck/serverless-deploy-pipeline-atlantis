# Set-Up and Use via AWS Web Console

The service role and pipeline can be created using the Web Console which may be preferable if you are just starting out and want to visually see the components and their settings.

1. Create an IAM Role for your CloudFormation Service
2. Create a CodeCommit repository for your code and place `/application-infrastructure/` at the root
3. Create a CloudFormation Pipeline stack

> As an alternative to setting up manually via the Web Console, [AWS CLI commands](./Set-Up-via-AWS-CLI.md) can be used to create the service role and stack.

## 1. Create Service Role in IAM Console

### 1a: Manually Copy and Perform Search/Replace

1. In the `/iam-cloudformation-service-role/` folder, make a copy of `SAMPLE-CloudFormationServicePolicy.json` and name the copy with your prefix instead of SAMPLE. The following command will do this assuming you are in the iam directory: `cp SAMPLE-CloudFormationServicePolicy.json ACME-CloudFormationServicePolicy.json`
2. Open the copy and do a Find and Replace for each of the following:
   - `$AWS_ACCOUNT$` = Your AWS account number. (ex: 990123456789)
   - `$AWS_REGION$` = Your AWS region (ex: us-east-1) This must be the region you will be deploying in.
   - `$PREFIX$` = The prefix (lower case) you chose. You can use `acme` if you wish but do not have to.
   - `$PREFIX_UPPER$` = The prefix (upper case) you chose. (ex: `ACME`). If you choose to do everything in lower case you can use lower case.
   - `$S3_ORG_PREFIX$` = Either replace with an empty string, or if you prefer, your organization's prefix for S3 buckets followed by a dash. (Example: `acme-` or leave empty) This is the only time you will append a dash to the end of any parameter.

> Note: This is the only time we will include an Upper-case Prefix. Instead, we use lower-case because S3 buckets must be in all lower-case and it would complicate automated provisioning if UPPERCASE, CamelCase, _and_ lowercase had to be accounted for. Also, mixing cases and using them inconsistently can be confusing.

### 1b: Create the CloudFormation Service Policy

Before we can attach a policy to the role we need to create the policy!

1. In the AWS Web Console go to IAM > Policies and "Create policy"
2. Click on the JSON button and paste in the json contents of `scripts-cli/cli/iam/ACME-CloudFormationServicePolicy.json` (the file you generated)
3. Go on to "Next".
4. Give it the name `ACME-CloudFormation-Service-Role` (replacing `ACME` with your chosen prefix in UPPER CASE) and a description such as `Created by [you] to create CloudFormation stacks for deployment pipelines`.
5. Add at least 2 tags. Note the casing and `:` in the tag keys. More on tags later.
   -  `Atlantis` with value `iam`
   -  `atlantis:Prefix` with the value of your prefix (lower case), and any additional tags you may want (like creator and purpose). 
6. Click on Create Policy.

### 1c: Add the Policy to the CloudFormation Service Role

1. Under IAM in the Web Console, choose "Roles" from the left-hand side.
2. Click on "Create role"
2. Leave "Trusted entity type" as AWS service, and from the "Use case list" choose CloudFormation. Go to "Next: Permissions"
2. In Filter policies search box, type in `ACME` (or your chosen prefix)
3. Check the box next to "_ACME_-CloudFormationServicePolicy" and click Next
4. Give it the name `ACME-CloudFormation-Service-Role` and a description such as `Allows CloudFormation to create and manage AWS stacks and resources on your behalf.`
5. Enter a tag `Atlantis` with value `iam`, `atlantis:Prefix` with the value of your prefix (lower case), and any additional tags you may want.
6. Create the Role

> Note: Again, you can create roles and stacks to segment permissions among your functional teams (e.g. `websvc` or `accounting`). Cool, huh?! Just make another copy of `ACME-CloudFormationServicePolicy.json` and do a new search/replace.

## 2: Create the CodeCommit repository

Place the `application-infrastructure/` directory at the root of your repository.

Commit your code and then create and push a `dev` and `test` branch in addition to your `main` branch.

Your repository is now primed for the next step.

## 3: Create a CloudFormation Pipeline stack

TODO
