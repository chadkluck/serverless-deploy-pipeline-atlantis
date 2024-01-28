# Write a python script that asks the user via the command line for each of the following: prefix, s3 bucket prefix, aws account id, and aws region. Then open the file sample-ATLANTIS-CloudFormationServicePolicy.json and do a search and replace for $PREFIX$, $PREFIX_UPPER$, $S3_ORG_PREFIX$ $AWS_ACCOUNT$, and $AWS_REGION$, and makes a copy of that file, storing it in the generated directory
import os
import json
import sys

# Default values - Set any of these defaults to your own in the .defaults file
defaults = {}
defaults["prefix"] = "atlantis"
defaults["s3_bucket_prefix"] = ""
defaults["aws_account_id"] = ""
defaults["aws_region"] = "us-east-1"
defaults["role_path"] = "/"
defaults["permissions_boundary_arn"] = ""

# check if a parameter was passed to script
if len(sys.argv) > 1:
	passed_prefix = sys.argv[1]
	passed_file = ".defaults-"+passed_prefix+".json"
	# check if the parameter is a valid file
	if os.path.isfile(passed_file):
		# read in the parameter file
		with open(passed_file, "r") as f:
			defaults = json.load(f)
			print("\nOffering parameters from "+passed_prefix+" parameter file...\n")
	else:
		print("Parameter "+passed_prefix+" file does not exist")
		sys.exit(1)
else:
	# check if the .defaults.json file exists and if it does read in the 
	if os.path.isfile(".defaults.json"):
		with open(".defaults.json", "r") as f:
			defaults = json.load(f)
			print("\nOffering defaults from .defaults.json file...\n")

# Get the prefix, s3 bucket prefix, aws account id, and aws region from the command line
print("\n==============================================================================")
print("Enter the following information to generate the IAM Service Role and CLI prompts:")
print("Press <RETURN/ENTER> to accept the default in the square brackets [ ] (or dash '-' to clear default)")
print("==============================================================================\n")
parameters = {}
parameters["prefix"] = input("Prefix ["+defaults["prefix"]+"]: ").lower()
parameters["s3_bucket_prefix"] = input("S3 bucket prefix (optional) ["+defaults["s3_bucket_prefix"]+"]: ").lower()
parameters["role_path"] = input("Role Path ["+defaults["role_path"]+"]: ").lower()
parameters["permissions_boundary_arn"] = input("Permissions Boundary ARN ["+defaults["permissions_boundary_arn"]+"]: ").lower()
parameters["aws_account_id"] = input("AWS Account ID ["+defaults["aws_account_id"]+"]: ")
parameters["aws_region"] = input("AWS Region ["+defaults["aws_region"]+"]: ").lower()

print("\n------------------------------------------------------------------------------\n")

# if any input is empty, use the default value


if not parameters["prefix"]:
	parameters["prefix"] = defaults["prefix"]
	print("Using default prefix:", parameters["prefix"])

if not parameters["s3_bucket_prefix"]:
	parameters["s3_bucket_prefix"] = defaults["s3_bucket_prefix"]
	print("Using default S3 bucket prefix:", parameters["s3_bucket_prefix"])

if parameters["s3_bucket_prefix"] == "-":
	parameters["s3_bucket_prefix"] = ""
	print("S3 bucket prefix has been cleared")

if not parameters["role_path"]:
	parameters["role_path"] = defaults["role_path"]
	print("Using default Role Path:", parameters["role_path"])

if parameters["role_path"] == "-":
	parameters["role_path"] = "/"
	print("Role Path has been cleared")

# make sure role_path is either "/" or starts and ends with "/"
if parameters["role_path"] != "/":
	# remove slashes from front and end of role_path
	parameters["role_path"] = parameters["role_path"].strip("/")
	parameters["role_path"] = "/" + parameters["role_path"] + "/"
	print("Role Path has been modified to:", parameters["role_path"])

if not parameters["permissions_boundary_arn"]:
	parameters["permissions_boundary_arn"] = defaults["permissions_boundary_arn"]
	print("Using default Permissions Boundary ARN:", parameters["permissions_boundary_arn"])

if parameters["permissions_boundary_arn"] == "-":
	parameters["permissions_boundary_arn"] = ""
	print("Permissions Boundary ARN has been cleared")

permissions_boundary_conditional = ""
permissions_boundary_cli = ""

if parameters["permissions_boundary_arn"]:
	permissions_boundary_conditional = """,
			"Condition": {
				"StringLike": {
					"$PERMISSIONS_BOUNDARY_ARN$"
				}
			}"""
	permissions_boundary_cli = " --permissions-boundary "+parameters["permissions_boundary_arn"]+" \\\n\t"

if not parameters["aws_account_id"]:
	parameters["aws_account_id"] = defaults["aws_account_id"]
	print("Using default AWS Account ID:", parameters["aws_account_id"])

if not parameters["aws_region"]:
	parameters["aws_region"] = defaults["aws_region"]
	print("Using default AWS Region:", parameters["aws_region"])

# set json_contents to stringified json parameters
json_contents = json.dumps(parameters)

# If .defaults.json does not exist, create it and write out the current values in JSON format
if not os.path.isfile(".defaults.json"):
	print("Creating .defaults.json file...")
	# Write the current values to the .defaults.json file in JSON format
	with open(".defaults.json", "w") as f:
		f.write(json_contents)
		f.close()

if not os.path.isfile(".defaults-"+parameters["prefix"]+".json"):
	print("Creating .defaults-"+parameters["prefix"]+".json file...")

# Write the current values to the .defaults-PREFIX.json file in JSON format
with open(".defaults-"+parameters["prefix"]+".json", "w") as f:
	f.write(json_contents)
	f.close()

if not os.path.isdir("generated"):
	print("Creating generated directory...")
	os.mkdir("generated")
	print("Created generated directory.")

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
	contents = contents.replace("$PREFIX$", parameters["prefix"])
	contents = contents.replace("$PREFIX_UPPER$", parameters["prefix"].upper())
	contents = contents.replace("$ROLE_PATH$", parameters["role_path"])
	contents = contents.replace("$AWS_ACCOUNT$", parameters["aws_account"])
	contents = contents.replace("$AWS_REGION$", parameters["aws_region"])
	contents = contents.replace(",\"Condition\": \"$PERMISSIONS_BOUNDARY_CONDITIONAL$\"", permissions_boundary_conditional)
	contents = contents.replace("$PERMISSIONS_BOUNDARY_ARN$", parameters["permissions_boundary_arn"])
	# if s3_bucket_prefix is provided, replace the placeholder with the value from the command line followed by a hyphen, else replace with blank
	if not parameters["s3_bucket_prefix"]:
		contents = contents.replace("$S3_ORG_PREFIX$", "")
		print("No S3 bucket prefix provided. Using blank string for s3_bucket_prefix.")
	else:
		contents = contents.replace("$S3_ORG_PREFIX$", parameters["s3_bucket_prefix"] + "-")
	# Write the updated contents to a new file in the generated directory
	new_file_name = parameters["prefix"].upper()+"-CloudFormationServicePolicy.json"
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

		print("aws iam create-role --path "+parameters["role_path"]+" \\\n\t --role-name "+parameters["prefix"].upper()+"-CloudFormation-Service-Role \\\n\t --assume-role-policy-document file://../Trust-Policy-for-Service-Role.json \\\n\t"+permissions_boundary_cli+" --tags '{\"Key\": \"Atlantis\", \"Value\": \"iam\"}' '{\"Key\": \"atlantis:Prefix\", \"Value\": \""+parameters["prefix"]+"\"}'\n")
		print("aws iam put-role-policy --role-name "+parameters["prefix"].upper()+"-CloudFormation-Service-Role \\\n\t --policy-name "+parameters["prefix"].upper()+"-CloudFormationServicePolicy \\\n\t --policy-document file://generated/"+new_file_name+"\n")

		print("==============================================================================\n")
