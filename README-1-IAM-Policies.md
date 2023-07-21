# Create IAM Policies

In order for the Deploy Pipeline stack to execute, it will need to assume an IAM role with proper permissions. A CloudFormation service role will need to be created before you can create any Deploy Pipeline stacks.

## Create Project Stack Service Role

We will create a policy (`ATLANTIS-CloudFormationServicePolicy`) and attach to a new role (`ATLANTIS-CloudFormation-Service-Role`).

You will only need to do this once.

If you have chosen a prefix other than `ATLANTIS` use that instead when naming your policy and role.

### Step 1: Get the CloudFormationServicePolicy.json file ready

1. In the `/iam-policy-template` folder, make a copy of `ATLANTIS-CloudFormationServicePolicy.json`
2. Open the document copy and do a Find and Replace for each of the following:
   - `$AWS_ACCT$` = Your AWS account number. (ex: 990123456789)
   - `$AWS_REGION$` = Your AWS region (ex: us-east-1) This must be the region you will be deploying in.
   - `$PREFIX$` = The prefix (lowercase) you chose. You can use `atlantis` if you wish but do not have to.
   - `$PREFIX_UPPER$` = The prefix (uppercase) you chose. (ex: `ATLANTIS`)
   - `$S3_ORG_PREFIX$` = Either replace with an empty string, or if you prefer, your organization's prefix for S3 buckets followed by a dash. (Example: [empty] or `acme-`)

### Step 2: Go to IAM in the Web Console

1. In the AWS Web Console go to IAM and create a new role
2. From the Use Case list choose CloudFormation and then go to "Next: Permissions"

### Step 3: Create the CloudFormation Service Policy

1. Choose "Create Policy" (it will open in a new window)
2. In the new tab/window, click on the JSON tab and paste in the json contents of the file you modified from [`iam-policy-template/ATLANTIS-CloudFormationServicePolicy.json`](iam-policy-template/ATLANTIS-CloudFormationServicePolicy.json)
3. Go on to "tags".
4. Add a tag `Atlantis` with value `TRUE` and any additional tags you may want (like creator and purpose). Then Review.
5. Give it the name `PREFIX-CloudFormation-Service-Role` (replacing PREFIX with your chosen prefix) and a description such as `Created by [you] to create CloudFormation stacks for deployment pipelines` and hit Create Policy
6. Close that browser tab/window and go back to the Create Role tab in your browser. 

### Step 4: Add the Policy to the CloudFormation Service Role

1. Back on the Create Role page, hit the refresh icon.
2. In Filter policies search box, type in `ATLANTIS` (or your chosen prefix)
3. Check the boxes next to "_PREFIX_-CloudFormationServicePolicy"
4. Go on to Next and enter a enter a tag `Atlantis` with value `TRUE` and any additional tags. Then Review.
5. Give it the name `PREFIX-CloudFormation-Service-Role` and a description such as `Created by [you] to create CloudFormation stacks for deployment pipelines`
6. Create the Role

Note: Again, you can create roles and stacks so that you can segment permissions among your functional teams (e.g. `websvc` or `accounting`). Cool, huh?! Just make another copy of `ATLANTIS-CloudFormationServicePolicy.json` and do a new search/replace.

### Step 5: Update user to assume role

The user role you use to access the Web Console or submit CLI commands will need the following IAM Policy added (Replace $AWS_ACCT$ and $PREFIX$ with appropriate values): 

```JSON
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Sid": "AllowUserToPassAtlantisCloudFormationServiceRole",
            "Effect": "Allow",
            "Action": "iam:PassRole",
            "Resource": "arn:aws:iam::$AWS_ACCT$:role/$PREFIX$-CloudFormation-Service-Role"
        }
    ]
}
```

## Documentation

There are 5 README documents to walk you through setting up the required IAM Policies and Roles, CodeCommit Repository, and Deploy CloudFormation Stack. 

IAM Policies and Roles only need to be set up once. CodeCommit Repositories only need to be set up once per application. A deploy pipeline stack needs to be set up for each deployment stage of an application (test, beta, prod).

- [README 1 Create IAM Policies](README-1-IAM-Policies.md)
- [README 2 Create CodeCommit Repository](README-2-CodeCommit-Repository.md)
- [README 3 Create and Update CloudFormation Deploy Pipeline Stack](README-3-CloudFormation-Deploy-Stack.md)
- [README 4 Tutorial](README-4-Tutorial.md)
- [README 5 Advanced](README-5-Advanced.md)
- [CHANGELOG - Updates to Existing Deploy Stacks](CHANGELOG.md)
