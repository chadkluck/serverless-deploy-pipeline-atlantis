# Changelog

All notable changes to this project will be documented in this file.

NOTE: The **Deploy** template is for **Deploy** stacks! **NOT** your **Infrastructure** stacks! Your Deploy stack is for the CI/CD (Deployment) pipeline.

You can add updates manually by following instructions and updating the template directly in CloudFormation or by uploading the new template to your CloudFormation stack. Review the updates and then follow instructions for applying the new template to existing CloudFormation stacks.

Updates are listed in cronological order to aid in applying any manual updates. It is recommended you only do one version update at a time and await a successful deployment.

## 2023-04-28

- Update: CodeBuild now has a newer instance to support Node.js 16.x during build (12 was supported previously)
- Update: CodeBuild log retention to be 90 days. Previous was never expire.
- Chore: Cleaned up CodeBuild resource implementation by re-ordering statements and providing additional comments

### Instructions for 2023-04-28

Add the following lines of code or replace the template with the new one (your customizations will be lost).

#### Update CodeBuild Image

1. In your Deploy stack CloudFormation template, find the CodeBuild resource. (Do a search for `AWS::CodeBuild::Project` in the template)
2. Identify Image under Environment and change it to the standard:4.0

```yaml
        #Image: aws/codebuild/amazonlinux2-x86_64-standard:3.0 # Up to Node 12
        Image: aws/codebuild/amazonlinux2-x86_64-standard:4.0 # Up to Node 16
```

This image is compatible with the small compute type and will allow you to bump the build runtime up to Node 16 (rather than 12)

Note: To take advantage of Node 16 (or any other latest runtime) you will need to update your buildspec.yml phases/install/runtime-versions in your project to use `nodejs: latest`.

Learn more about ComputeType, Environment Type, runtime versions from AWS User Guides: 

- [AWS User Guide: Build Environment Compute Types](https://docs.aws.amazon.com/codebuild/latest/userguide/build-env-ref-compute-types.html)
- [AWS User Guide: Runtime Versions](https://docs.aws.amazon.com/codebuild/latest/userguide/runtime-versions.html)
- [AWS User Guide: Available Runtimes](https://docs.aws.amazon.com/codebuild/latest/userguide/available-runtimes.html)

Be sure to note your changes in the comments at the top of the template, including updating the version of the template v2023-04-28

#### Update CodeBuild Log Retention

You will need to delete existing CodeBuild logs. These are just logs of your builds and not tied to your application. (Make sure you delete the correct ones starting with `/aws/codebuild/`) They must be deleted so that you can add the resource, otherwise the CF update will fail (LogGroup already exists).

1. Delete existing CodeBuild logs. Go to CloudWatch and under LogGroups find the corresponding group starting with `/aws/codebuild/{{stack-name}}-Build`
2. In your Deploy stack CloudFormation template, find the CodeBuild resource. (Do a search for `AWS::CodeBuild::Project` in the template)
3. Below the CodeBuild resource, add the resource for CodeBuildLogGroup:

```yaml
  # ---------------------------------------------------------------------------
  # -- Log Group for CodeBuild Project --
  # -- (Just so we can add a retention policy)

  CodeBuildLogGroup:
    Type: AWS::Logs::LogGroup
    Properties:
      LogGroupName: !Sub "/aws/codebuild/${Prefix}-${ProjectStageId}-Build"
      RetentionInDays: 90 # Set to your own retention policy - how long do you want to keep build logs?
```

Be sure to note your changes in the comments at the top of the template, including updating the version of the template v2023-04-28
