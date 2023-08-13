# Changelog

All notable changes to this project will be documented in this file.

NOTE: The **Deploy** template is for **Deploy** stacks! **NOT** your **Infrastructure** stacks! Your Deploy stack is for the Code Pipeline.

You can add updates manually by following instructions and updating the template directly in CloudFormation or by uploading the new template to your CloudFormation stack. Review the updates and then follow instructions for applying the new template to existing CloudFormation stacks.

Updates are listed in chronological order to aid in applying any manual updates. It is recommended you only do one version update at a time and await a successful deployment.

## 2023-07-22

Reworked the template and removed the ability to deploy using CodeStar. This simplified maintaining and using the template for both the deploy and infrastructure stack. The old templates have been moved to the `/x-deprecated-versions` directory.
