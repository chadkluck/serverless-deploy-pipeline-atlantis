# READ ME 1: Create IAM Policies

In order for the Deploy Pipeline stack to execute, it will need to assume an IAM role with proper permissions. A CloudFormation service role will need to be created before you can create any Deploy Pipeline stacks.

## Create Project Stack Service Role

We will create a policy (`ATLANTIS-CloudFormationServicePolicy`) and attach to a new role (`ATLANTIS-CloudFormation-Service-Role`).

You will only need to do this once.

If you have chosen a prefix other than `ATLANTIS` use that instead when naming your policy and role.

### Step 1: Get the CloudFormationServicePolicy.json file ready

1. In the `/iam-service-role` folder, make a copy of `ATLANTIS-CloudFormationServicePolicy.json`
2. Open the document copy and do a Find and Replace for each of the following:
   - `$AWS_ACCOUNT$` = Your AWS account number. (ex: 990123456789)
   - `$AWS_REGION$` = Your AWS region (ex: us-east-1) This must be the region you will be deploying in.
   - `$PREFIX$` = The prefix (lower case) you chose. You can use `atlantis` if you wish but do not have to.
   - `$PREFIX_UPPER$` = The prefix (upper case) you chose. (ex: `ATLANTIS`). If you choose to do everything in lower case you can use lower case.
   - `$S3_ORG_PREFIX$` = Either replace with an empty string, or if you prefer, your organization's prefix for S3 buckets followed by a dash. (Example: [empty] or `acme-`) This is the only time you will append a dash to the end of the S3 organization prefix.

Note: There are few times we use an Uppercase Prefix. Instead we typically use lower case because S3 buckets must be in all lower case and it would complicate automated provisioning if UPPERCASE, CamelCase, _and_ lowercase had to be accounted for. Also, mixing cases can be confusing. However, when I manually create resources I will sometimes call out the Prefix or Environment (PROD, DEV, TEST). It just helps me in identifying automated verses manually created resources. You can choose whatever makes sense for you and your organization.

### Step 2: Go to IAM in the Web Console

1. In the AWS Web Console go to IAM > Roles and "Create a Role"
2. Leave "Trusted entity type" as AWS service, and from the "Use case list" choose CloudFormation. Go to "Next: Permissions"

### Step 3: Create the CloudFormation Service Policy

1. Choose "Create Policy" (it will open in a new window)
2. In the new tab/window, click on the JSON tab and paste in the json contents of the file you modified from [`iam-service-role/ATLANTIS-CloudFormationServicePolicy.json`](iam-service-role/ATLANTIS-CloudFormationServicePolicy.json)
3. Go on to "Next".
4. Give it the name `PREFIX_UPPER-CloudFormation-Service-Role` (replacing `PREFIX_UPPER` with your chosen prefix) and a description such as `Created by [you] to create CloudFormation stacks for deployment pipelines`.
5. Add a tag `Atlantis` with value `iam`, `atlantis:Prefix` with the value of your prefix (lower case), and any additional tags you may want (like creator and purpose). Note the casing and `:` in the tag keys. More on tags later.
6. Click on Create Policy.
7. Close that browser tab/window and go back to the Create Role tab in your browser.

### Step 4: Add the Policy to the CloudFormation Service Role

1. Back on the Create Role page, hit the refresh icon.
2. In Filter policies search box, type in `ATLANTIS` (or your chosen prefix)
3. Check the boxes next to "_PREFIX_-CloudFormationServicePolicy"
4. Give it the name `PREFIX_UPPER-CloudFormation-Service-Role` and a description such as `Allows CloudFormation to create and manage AWS stacks and resources on your behalf.`
5. Enter a tag `Atlantis` with value `iam`, `atlantis:Prefix` with the value of your prefix (lower case), and any additional tags you may want.
6. Create the Role

Note: Again, you can create roles and stacks so that you can segment permissions among your functional teams (e.g. `websvc` or `accounting`). Cool, huh?! Just make another copy of `ATLANTIS-CloudFormationServicePolicy.json` and do a new search/replace.

### Step 5: Update user to assume role

The user role you use to access the Web Console or submit CLI commands will need the following IAM Policy added (Replace `$AWS_ACCOUNT$` and `$PREFIX$` with appropriate values). You can create it as a stand alone policy and attach it to a role, or add it to the inline policy statement. If you create it as a stand alone policy I recommend tagging it with: `Atlantis` with value `iam`, `atlantis:Prefix` with the value of your prefix (lowercase), and any additional tags you may want.

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

For example, if you were updating a role used by your Web Service developers in account 990123456780 and you created `WEBSVC-CloudFormation-Service-Role`, you would add something like the following to their IAM role policy statement:

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

## Related

- [AWS Documentation: Granting a user permissions to pass a role to an AWS service](https://docs.aws.amazon.com/IAM/latest/UserGuide/id_roles_use_passrole.html)
- [AWS Documentation: Tagging your AWS resources](https://docs.aws.amazon.com/tag-editor/latest/userguide/tagging.html)

## Documentation

There are 5 README documents to walk you through setting up the required IAM Policies and Roles, CodeCommit Repository, and Deploy CloudFormation Stack. 

IAM Policies and Roles only need to be set up once. CodeCommit Repositories only need to be set up once per application. A deploy pipeline stack needs to be set up for each deployment stage of an application (test, beta, prod).

- [README 1 Create IAM Policies](README-1-IAM-Policies.md)
- [README 2 Create CodeCommit Repository](README-2-CodeCommit-Repository.md)
- [README 3 Create and Update CloudFormation Deploy Pipeline Stack](README-3-CloudFormation-Deploy-Stack.md)
- [README 4 Tutorial](README-4-Tutorial.md)
- [README 5 Advanced](README-5-Advanced.md)
- [CHANGELOG - Updates to Existing Deploy Stacks](CHANGELOG.md)
