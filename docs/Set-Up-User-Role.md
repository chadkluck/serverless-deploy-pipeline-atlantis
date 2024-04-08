# User Roles

## Create Roles

Make sure you have permissions to create roles

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

## Assume Role

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