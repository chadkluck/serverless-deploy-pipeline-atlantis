# Using the script and CLI

Full usage instructions can be found in the Serverless Deploy Pipeline Atlantis README.

## Basic

From within the `scripts-cli/` directory run the Python script `copy-policy.py`.

`py copy-policy.py` or `python3 copy-policy.py` or some variation depending on how you execute Python scripts on your machine.

The script will prompt you for 4 values:

- Prefix
- S3 Bucket Prefix
- Account ID
- AWS Region

Default values will show in the square brackets, to accept the default value just hit Enter.

Once the 4 values are entered, the script will generate a CloudFormationServicePolicy.json file in the `generated/` directory. The script will also display two CLI commands to execute to create the CloudFormation-Service-Role.

Before executing the commands, make sure you are logged into AWS CLI with a user role holding permissions to create the service role.

If you do not have AWS CLI installed, you can use the generated CloudFormationServicePolicy JSON and create the role manually via the Web Console.

## Default Values

Default values were saved to `.default.json` from the first execution of the script on your machine. You can reset them by either modifying `.default.json` or deleting it.

By default, the `.default.json` file is ignored by git so that it isn't included in your repository. If you wish to include it in your repository, just comment out the `.default.json` line in the `.gitignore` file in the `scripts-cli/` directory.

## Where does the `iam-cloudformation-service-role` directory go?

Typically the iam directory is not stored with the application code. Instead it should be stored in a separate repository where your organization's overall infrastructure is managed.
