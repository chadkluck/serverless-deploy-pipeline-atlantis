# Write a python script that asks the user via the command line for each of the following: prefix, s3 bucket prefix, aws account id, and aws region. Then open the file sample-ATLANTIS-CloudFormationServicePolicy.json and do a search and replace for $PREFIX$, $PREFIX_UPPER$, $S3_ORG_PREFIX$ $AWS_ACCOUNT$, and $AWS_REGION$, and makes a copy of that file, storing it in the generated directory
import os
import json

# Default values - Set any of these defaults to your own in the .defaults file
default_prefix = "atlantis"
default_s3_bucket_prefix = ""
default_aws_account_id = ""
default_aws_region = "us-east-1"
default_role_path = "/"
default_permissions_boundary_arn = ""

# check if the .defaults.json file exists and if it does read in the 
if os.path.isfile(".defaults.json"):
	with open(".defaults.json", "r") as f:
		defaults = json.load(f)
		default_prefix = defaults["prefix"]
		default_s3_bucket_prefix = defaults["s3_bucket_prefix"]
		default_aws_account_id = defaults["aws_account_id"]
		default_aws_region = defaults["aws_region"]
		default_role_path = defaults["role_path"]
		default_permissions_boundary_arn = defaults["permissions_boundary_arn"]
		print("\nOffering defaults from .defaults.json file...\n")

# Get the prefix, s3 bucket prefix, aws account id, and aws region from the command line
print("\n==============================================================================")
print("Enter the following information to generate the IAM Service Role and CLI prompts:")
print("Press <RETURN/ENTER> to accept the default in the square brackets [ ]")
print("==============================================================================\n")
prefix = input("Prefix ["+default_prefix+"]: ").lower()
s3_bucket_prefix = input("S3 bucket prefix (optional) ["+default_s3_bucket_prefix+"]: ").lower()
role_path = input("Role Path ["+default_role_path+"]: ").lower()
permissions_boundary_arn = input("Permissions Boundary ARN ["+default_permissions_boundary_arn+"]: ").lower()
aws_account_id = input("AWS Account ID ["+default_aws_account_id+"]: ")
aws_region = input("AWS Region ["+default_aws_region+"]: ").lower()

print("\n------------------------------------------------------------------------------\n")

# if any input is empty, use the default value
if not prefix:
	prefix = default_prefix
	print("Using default prefix:", prefix)

if not s3_bucket_prefix:
	s3_bucket_prefix = default_s3_bucket_prefix
	print("Using default S3 bucket prefix:", s3_bucket_prefix)

if not role_path:
	role_path = default_role_path
	print("Using default Role Path:", role_path)

# make sure role_path is either "/" or starts and ends with "/"
if role_path != "/":
	# remove slashes from front and end of role_path
	role_path = role_path.strip("/")
	role_path = "/" + role_path + "/"
	print("Role Path has been modified to:", role_path)

if not permissions_boundary_arn:
	permissions_boundary_arn = default_permissions_boundary_arn
	print("Using default Permissions Boundary ARN:", permissions_boundary_arn)

permissions_boundary_conditional = ""
permissions_boundary_cli = ""

if permissions_boundary_arn:
	permissions_boundary_conditional = """,
			"Condition": {
				"StringLike": {
					"$PERMISSIONS_BOUNDARY_ARN$"
				}
			}"""
	permissions_boundary_cli = " --permissions-boundary "+permissions_boundary_arn+" \\\n\t"

if not aws_account_id:
	aws_account_id = default_aws_account_id
	print("Using default AWS Account ID:", aws_account_id)

if not aws_region:
	aws_region = default_aws_region
	print("Using default AWS Region:", aws_region)

# If .defaults.json does not exist, create it and write out the current values in JSON format
if not os.path.isfile(".defaults.json"):
	print("Creating .defaults.json file...")
	# Write the current values to the .defaults.json file in JSON format
	with open(".defaults.json", "w") as f:
		f.write('{"prefix":"'+prefix+'", "s3_bucket_prefix":"'+s3_bucket_prefix+'", "role_path":"'+role_path+'", "permissions_boundary_arn":"'+permissions_boundary_arn+'", "aws_account_id":"'+aws_account_id+'", "aws_region":"'+aws_region+'"}')

print("\n------------------------------------------------------------------------------\n")

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
	contents = contents.replace("$ROLE_PATH$", role_path)
	contents = contents.replace("$AWS_ACCOUNT$", aws_account_id)
	contents = contents.replace("$AWS_REGION$", aws_region)
	contents = contents.replace(",\"Condition\": \"$PERMISSIONS_BOUNDARY_CONDITIONAL$\"", permissions_boundary_conditional)
	contents = contents.replace("$PERMISSIONS_BOUNDARY_ARN$", permissions_boundary_arn)
	# if s3_bucket_prefix is provided, replace the placeholder with the value from the command line followed by a hyphen, else replace with blank
	if not s3_bucket_prefix:
		contents = contents.replace("$S3_ORG_PREFIX$", "")
		print("No S3 bucket prefix provided. Using blank string for s3_bucket_prefix.")
	else:
		contents = contents.replace("$S3_ORG_PREFIX$", s3_bucket_prefix + "-")
	# Write the updated contents to a new file in the generated directory
	new_file_name = prefix.upper()+"-CloudFormationServicePolicy.json"
	with open(os.path.join(generated_dir, new_file_name), "w") as g:
		g.write(contents)
		g.close()
		f.close()

		# Print a message indicating that the file has been copied
		print("File copied and updated successfully!")
		print(os.path.join(generated_dir, new_file_name))

		print("\n==============================================================================")
		print("================================= COMPLETE! ==================================\n")

		# Print a message indicating the aws iam cli commands to create the role and policy and attach it to the role
		print("To create the role attach the permissions policy, execute the following AWS CLI commands (Make sure you are logged into AWS CLI with a user role holding permissions to create the service role!):\n")

		print("aws iam create-role --path "+role_path+" \\\n\t --role-name "+prefix.upper()+"-CloudFormation-Service-Role \\\n\t --assume-role-policy-document file://../Trust-Policy-for-Service-Role.json \\\n\t"+permissions_boundary_cli+" --tags '{\"Key\": \"Atlantis\", \"Value\": \"iam\"}' '{\"Key\": \"atlantis:Prefix\", \"Value\": \""+prefix+"\"}'\n")
		print("aws iam put-role-policy --role-name "+prefix.upper()+"-CloudFormation-Service-Role \\\n\t --policy-name "+prefix.upper()+"-CloudFormationServicePolicy \\\n\t --policy-document file://generated/"+new_file_name+"\n")

		print("==============================================================================\n")
