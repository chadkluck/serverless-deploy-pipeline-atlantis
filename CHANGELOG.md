# Changelog

All notable changes to this project will be documented in this file.

NOTE: The **Deploy** template is for **Deploy** stacks! **NOT** your **Infrastructure** stacks! Your Deploy stack is for the CI/CD (Deployment) pipeline.

## Template Updates

You can add updates manually by following instructions and updating the template directly in CloudFormation or by uploading the new template to your CloudFormation stack. Review the updates and then follow instructions for applying the new template to existing CloudFormation stacks.

Updates are listed in cronological order to aid in applying any manual updates. It is recommended you only do one version update at a time and await a successful deployment.

### 2023-04-28

- Update: CodeBuild now has a newer instance to support Node.js 16.x during build (12 was supported previously)
- Update: CodeBuild log retention to be 90 days. Previous was never expire.
- Chore: Cleaned up CodeBuild resource implementation by re-ordering statements and providing additional comments

#### Instructions for 2023-04-28

Add the following lines of code or replace the template with the new one (your customizations will be lost).

##### Update CodeBuild Image

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

##### Update CodeBuild Log Retention

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

## Edit and Updating Existing CloudFormation Stacks

NOTE: The **Deploy** template is for **Deploy (-deploy)** stacks! **NOT** your **Infrastructure (-infrastructure)** stacks!

If you are replacing the entire contents of the template file then you can do this one of two ways:

1. Upload a copy from your local machine
2. Point to the 63klabs S3 Bucket
3. Edit Template "In Place" in the Template Designer

Note! If you have made your own modifications by adding additional permissions or resources, replacing the entire template will remove your changes. In that case, it is recommended you either manually update the pieces of code that need updating following the instructions in each update, or make note of your changes and re-implement them.

If you are updating pieces of the template manually "In Place" by following the update instructions then you can edit the appropriate areas in the template editor.

### Option 1: Upload from Local Machine

1. Download the new template.yml file and edit as needed (if adding customizations).
2. Go to your `-deploy` stack and choose Update
3. Choose "Replace current template"
4. Choose "Upload a template file"
5. Upload your file
6. Update any Parameters and Tags on the next page
7. Choose the deployment role (Typically something like `projectstack-service-role`) If unsure look at the Stack Info/Overview/IAM Role assigned to similar Deploy stacks.
8. Check the box for acknowledging AWS may create resources.
9. Watch the stack update progress. Hopefully it is successful!

### Option 2: Point to the S3 Bucket

1. Go to your `-deploy` stack and choose Update
2. Choose "Replace current template"
3. Choose "Amazon S3 URL" and enter in `https://63klabs.s3.amazonaws.com/projectstack-templates/atlantis/toolchain.yml`
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
