# Changelog

All notable changes to this project will be documented in this file.

NOTE: The **Pipeline** template is for **Pipeline** stacks! **NOT** your **Application Infrastructure** stacks!

You can add updates to your own copy of the pipeline stack template by manually following instructions and updating the template directly in CloudFormation or by uploading the new template to your CloudFormation stack. Review the updates and then follow instructions for applying the new template to existing CloudFormation stacks.

Updates are listed in **chronological** order to aid in applying any manual updates. It is recommended you only do one version update at a time and await a successful deployment.

## v2024.04.21 Release

Reworked the template and removed the ability to deploy using CodeStar (which is being retired by AWS summer of 2024 anyway). The new template and CLI commands simplified maintaining and using the template for both the pipeline and infrastructure stack. The [old template is still available on S3](https://63klabs.s3.us-east-2.amazonaws.com/atlantis/v0/atlantis-pipeline-files-v0-deprecated.zip).

Version 2 now has clearer parameter naming conventions, improved parameter constraints, CLI scripts, and instructions.

File versions included:

- v2024.02.29 : template-pipeline.yml
- v2024.02.29 : service-role.py
- v2024.02.29 : pipeline-stack.py
- v2024.02.29 : lib/atlantis.py
- v2024.02.29 : lib/tools.py

The main instructions have been updated, however the tutorial has not. A new tutorial should be released in Summer of 2024.

## v2024.06.17 Release

For the pipeline template, added caching to the CodeBuild Project, and a CloudFormation stack parameter "DeployBucket" to use an existing S3 bucket for artifact storage rather than creating one for each pipeline.

Includes a fix to CloudFormationServicePolicy (IAM) by adding "iam:UpdateRoleDescription" Action to ManageWorkerRolesByResourcePrefix.

Templates and Scripts Updated:

- v2024.06.17 : template-pipeline.yml
- v2024.06.17 : pipeline-stack.py
- v2024.06.17 : lib/atlantis.py
- v2024.06.17 : lib/templates/sample-input-create-stack.json

To update CloudFormation-Service-Role, re-run the service-role.py script for the Prefix you wish to update. Then update the role's policy with the generated JSON policy found in the roles directory.
