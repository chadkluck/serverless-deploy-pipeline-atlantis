# Write a python script that asks the user via the command line for each of the following: prefix, s3 bucket prefix, aws account id, and aws region. Then open the file sample-ATLANTIS-CloudFormationServicePolicy.json and do a search and replace for $PREFIX$, $PREFIX_UPPER$, $S3_ORG_PREFIX$ $AWS_ACCOUNT$, and $AWS_REGION$, and makes a copy of that file, storing it in the generated directory
import os
import sys

# Default values - Set any of these defaults to your own for future use
default_prefix = "atlantis"
default_s3_bucket_prefix = ""
default_aws_account_id = "" # You can set this to your own for future use
default_aws_region = "us-east-1"

# Get the prefix, s3 bucket prefix, aws account id, and aws region from the command line
prefix = input("Enter the prefix ["+default_prefix+"]: ")
s3_bucket_prefix = input("Enter the s3 bucket prefix (optional) ["+default_s3_bucket_prefix+"]:")
aws_account_id = input("Enter the aws account id ["+default_aws_account_id+"]:")
aws_region = input("Enter the aws region ["+default_aws_region+"]: ")

# if any input is empty, use the default value
if not prefix:
	prefix = default_prefix
	print("Using default prefix:", prefix)

if not s3_bucket_prefix:
	s3_bucket_prefix = default_s3_bucket_prefix
	print("Using default s3 bucket prefix:", s3_bucket_prefix)

if not aws_account_id:
	aws_account_id = default_aws_account_id
	print("Using default aws account id:", aws_account_id)

if not aws_region:
	aws_region = default_aws_region
	print("Using default aws region:", aws_region)

# Get the current working directory
cwd = os.getcwd()
# Get the path to the generated directory
generated_dir = os.path.join(cwd, "generated")
# Open the sample-ATLANTIS-CloudFormationServicePolicy.json file
with open(
	os.path.join(cwd, "../sample-ATLANTIS-CloudFormationServicePolicy.json"), "r"
) as f:
	# Read the contents of the file
	contents = f.read()
	# Replace the placeholders with the values from the command line
	contents = contents.replace("$PREFIX$", prefix)
	contents = contents.replace("$PREFIX_UPPER$", prefix.upper())
	contents = contents.replace("$AWS_ACCOUNT$", aws_account_id)
	contents = contents.replace("$AWS_REGION$", aws_region)
	# if s3_bucket_prefix is provided, replace the placeholder with the value from the command line followed by a hyphen, else replace with blank
	if not s3_bucket_prefix:
		contents = contents.replace("$S3_ORG_PREFIX$", "")
		print("No s3 bucket prefix provided. Using blank string for s3_bucket_prefix.")
	else:
		contents = contents.replace("$S3_ORG_PREFIX$", s3_bucket_prefix + "-")
	# Write the updated contents to a new file in the generated directory
	with open(os.path.join(generated_dir, "generated-policy.json"), "w") as g:
		g.write(contents)
		g.close()
		f.close()

		# Print a message indicating that the file has been copied
		print("File copied successfully!")
		print(os.path.join(generated_dir, "generated-policy.json"))
		print(os.path.join(cwd, "sample-ATLANTIS-CloudFormationServicePolicy.json"))