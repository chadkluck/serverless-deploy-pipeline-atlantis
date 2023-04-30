# IAM Policies

A service role will need to be created for `*-deploy` CloudFormation stacks to assume when it deploys the application's infrastructure stack.

## Create CodeStar Service Role

Create a policy (`CodeStarTaggingPolicy`) and attach to a new role (`aws-codestar-service-role`).

1. In the AWS Web Console go to IAM and create a new role
2. From the Use Case list choose CloudFormation and then go to "Next: Permissions"

### Create the CodeStar Tagging Policy

1. Choose "Create Policy" (it will open in a new browser tab/window)
2. In the new tab/window, click on the JSON tab and paste in the json contents of [`iam-policy-templates/CodeStarTaggingPolicy.json`](iam-policy-templates/CodeStarTaggingPolicy.json)
3. Go on to "tags".
4. Add a tag `CodeStarProjectPolicy` with value `YES` and any additional tags you may want (like creator and purpose). Then Review.
5. Give it the name `CodeStarTaggingPolicy` and a description such as `Created by [you] to allow for tagging of CodeStar project roles` and hit Create Policy
6. Close that browser tab/window and go back to the Create Role tab in your browser. Hit the refresh icon.

### Add the Policy to the CodeStar Service Role

1. In Filter policies search box, type in `CodeStar`
2. Check the boxes next to "CodeStarTaggingPolicy" and "AWSCodeStarServiceRole"
3. Go on to Next and enter a enter a tag `CodeStarProjectPolicy` with value `YES` and any additional tags. Then Review.
4. Give it the name `aws-codestar-service-role` and a description such as `Created by [you] to allow for CodeStar creation of resources.`
5. Create the Role

## Create Project Stack Service Role

Create 2 policies (`ProjectStackTaggingPolicy` and `ProjectStackServicePolicy`) and attach to a new role (`projectstack-service-role`).

You'll only need to do this once. This will be similar to the first few steps in **CodeStar Service Role** but with a few changes so that it is specific to project stacks.

1. In the AWS Web Console go to IAM and create a new role
2. From the Use Case list choose CloudFormation and then go to "Next: Permissions"

### Create the Project Stack Tagging Policy

1. Choose "Create Policy" (it will open in a new window)
2. In the new tab/window, click on the JSON tab and paste in the json contents of [`iam-policy-templates/ProjectStackTaggingPolicy.json`](iam-policy-templates/ProjectStackTaggingPolicy.json)
3. Go on to "tags".
4. Add a tag `CodeStarProjectPolicy` with value `YES` and any additional tags you may want (like creator and purpose). Then Review.
5. Give it the name `ProjectStackTaggingPolicy` and a description such as `Created by [you] to allow for tagging of CodeStar-like project roles` and hit Create Policy
6. Close that browser tab/window and go back to the Create Role tab in your browser.

### Create the Project Stack Service Policy

1. Instead of using a managed policy like "AWSCodeStarServiceRole" we will be creating our own specific to the prefix "projectstack-". Again, choose "Create Policy" (it will again open in a new window)
2. In the new tab/window, click on the JSON tab and paste in the json contents of [`iam-policy-templates/ProjectStackServicePolicy.json`](iam-policy-templates/ProjectStackServicePolicy.json)
3. Go on to "tags".
4. Add a tag `CodeStarProjectPolicy` with value `YES` and any additional tags you may want (like creator and purpose). Then Review.
5. Give it the name `ProjectStackServicePolicy` and a description such as `Created by [you] to allow for CodeStar-like creation of resources` and hit Create Policy
6. Close that browser tab/window and go back to the Create Role tab in your browser. 

### Add the Policies to the Project Stack Service Role

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
            "Sid": "AllowUserToPassProjectStackServiceRole",
            "Effect": "Allow",
            "Action": "iam:PassRole",
            "Resource": "arn:aws:iam::*:role/projectstack-service-role"
        }
    ]
}
```

