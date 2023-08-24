# Create Stack from CLI (Command Line Interface)

Instead of creating a stack through the AWS Web Console, stacks may be created from the AWS CLI.

## What you will need

- Python installed
- AWS CLI installed
- AWS Credentials with a proper Role that can create stacks from the CLI
- Access to an S3 bucket that contains, or will contain, the `pipeline-toolchain.yml` template. (The latest toolchain from the author is available from [the 63K Labs S3 Bucket](https://63klabs.s3.amazonaws.com/atlantis/pipeline-toolchain.yml))

## Basic Steps

1. Update [config stack json](./config-stack.json)
2. Run the generate input Python script: `py generate.py`
3. IF you are using your own S3 bucket for `pipeline-toolchain.yml` upload it using the S3 copy command listed in the output of generate-input.
4. Run the CloudFormation create-stack command listed in the output of generate-input.