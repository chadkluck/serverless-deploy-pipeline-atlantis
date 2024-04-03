# Set Up: Easy as 1-2-3!

Once you have read the [root READ ME](../README.md) and [Tutorials](./Tutorials.md), you'll notice it all comes down to:

1. Create an IAM Role for your CloudFormation Service using the scripts and CLI commands
2. Create a CodeCommit repository for your code and place `/application-infratructure/` at the root.
3. Create a CloudFormation Pipeline stack using the scripts and CLI commands

## Service Role

This only needs to be done once per Prefix.

From the /scripts-cli/ directory run `python service-role.py acme` replacing `acme` with your prefix and following on-screen prompts.

Follow instructions displayed after script has run. A copy of the CLI commands will be stored in /scripts-cli/cli/iam/

## Create a CodeCommit repository

Once created, clone to your workstation and populate it with the `/application-infrastructure/` directory. The `/application-infrastructure/` directory should be at the root of your repository.

Commit your code and then create and push a `dev` and `test` branch in addition to your `main` branch.

Your repository is now primed for the next step.

## Create the Pipeline

From the /scripts-cli/ directory, run `python pipeline-stack.py acme yourprojectname test` replacing acme and yourprojectname with appropriate values (your prefix and project name). Leave test as is.

Follow on-screen prompts.

Follow instructions displayed after script has run. A copy of the CLI commands will be stored in /scripts-cli/cli/cfn/

Once you have a successful deploy, create your Production pipeline:

`python pipeline-stack.py acme yourprojectname prod`

Follow the same on-screen and CLI steps as you did for your test pipeline.
