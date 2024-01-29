import os
import json
import sys
import re

# Default values - Set any of these defaults to your own in the .defaults file
defaults = {}
defaults["Prefix"] = "atlantis"
defaults["S3BucketNameOrgPrefix"] = ""
defaults["aws_account_id"] = ""
defaults["aws_region"] = "us-east-1"
defaults["RolePath"] = "/"
defaults["PermissionsBoundaryARN"] = ""

# check if a parameter was passed to script
if len(sys.argv) > 1:
	passed_prefix = sys.argv[1]
	passed_file = ".defaults-"+passed_prefix+".json"
	# check if the parameter is a valid file
	if os.path.isfile(passed_file):
		# read in the parameter file
		with open(passed_file, "r") as f:
			defaults = json.load(f)
			print("\nOffering default parameters from "+passed_prefix+" file...\n")
	else:
		print("Parameter file '"+passed_prefix+"' does not exist")
		sys.exit(1)
else:
	# check if the .defaults.json file exists and if it does read in the defaults
	if os.path.isfile(".defaults.json"):
		with open(".defaults.json", "r") as f:
			defaults = json.load(f)
			print("\nOffering default parameters from .defaults.json file...\n")

# Get the prefix, s3 bucket prefix, aws account id, and aws region from the command line
print("\n================================================================================")
print("Enter parameter values to generate IAM Service Role and AWS CLI commands:")
print("( Leave blank to accept default in square brackets [] or dash '-' to clear     )")
print("( Enter exclamation point '!' for help.                                        )")
print("( Enter carat '^' at any prompt to exit script                                 )")
print("================================================================================\n")

prompts = {}
prompts["Prefix"] = {
	"name": "Prefix",
	"required": True,
	"regex": "^[a-z][a-z0-9-]{0,12}[a-z0-9]$",
	"help": "2 to 8 characters. Alphanumeric (lower case) and dashes. Must start with a letter and end with a letter or number.",
	"description": "A prefix helps distinguish applications and assign permissions among teams, departments, and organizational units. For example, users with Finance Development roles may be restricted to resources named with the 'finc' prefix or resources tagged with the 'finc' prefix.",
	"examples": "atlantis, finc, ops, dev-ops, b2b",
	"default": defaults["Prefix"],
}
prompts["S3BucketNameOrgPrefix"] = {
	"name": "S3 Bucket Name Org Prefix",
	"required": False,
	"regex": "^[a-z0-9][a-z0-9-]*[a-z0-9]$|^$",
	"help": "S3 bucket prefix must be lowercase, start with a letter, and contain only letters, numbers, and dashes",
	"description": "S3 bucket names must be unique across all AWS accounts. This prefix helps distinguish S3 buckets from each other and will be used in place of using account ID and region to establish uniqueness resulting in shorter bucket names.",
	"examples": "xyzcompany, acme, b2b-solutions-inc",
	"default": defaults["S3BucketNameOrgPrefix"],
}
prompts["RolePath"] = {
	"name": "Role Path",
	"required": False,
	"regex": "^\/[a-zA-Z0-9\/_-]+\/$|^\/$",
	"help": "Role Path must be a single slash OR start and end with a slash, contain alpha numeric characters, dashes, underscores, and slashes.",
	"description": "Role Path is a string of characters that designates the path to the role. For example, the path to the role 'atlantis-admin' is '/atlantis-admin/'.",
	"examples": "/, /atlantis-admin/, /atlantis-admin/dev/, /service-roles/, /application_roles/dev-ops/",
	"default": defaults["RolePath"],
}
prompts["PermissionsBoundaryARN"] = {
	"name": "Permissions Boundary ARN",
	"required": False,
	"regex": "^$|^arn:aws:iam::[0-9]{12}:policy\/[a-zA-Z0-9\/_-]+$",
	"help": "Permissions Boundary ARN must be in the format: arn:aws:iam::{account_id}:policy/{policy_name}",
	"description": "Permissions Boundary is a policy that is attached to the role and can be used to further restrict the permissions of the role. Your organization may or may not require boundaries.",
	"examples": "arn:aws:iam::123456789012:policy/xyz-org-boundary-policy",
	"default": defaults["PermissionsBoundaryARN"],
}
prompts["aws_account_id"] = {
	"name": "AWS Account ID",
	"required": True,
	"regex": "^[0-9]{12}$",
	"help": "AWS Account ID must be 12 digits",
	"description": "AWS Account ID is a 12 digit number that identifies the AWS account.",
	"examples": "123456789012, 123456789013, 123456789014",
	"default": defaults["aws_account_id"],
}
prompts["aws_region"] = {
	"name": "AWS Region",
	"required": True,
	"regex": "^[a-z]{2}-[a-z]+-[0-9]$",
	"help": "AWS Region must be lowercase and in the format: us-east-1",
	"description": "AWS Region is a string that identifies the AWS region. For example, the region 'us-east-1' is located in the United States.",
	"examples": "us-east-1, us-west-1, us-west-2, eu-west-1, ap-southeast-1",
	"default": defaults["aws_region"],
}

def indent(spaces=4, prepend=''):
	return prepend + " " * spaces

# A function that accepts a string and breaks it into lines that are no longer than 80 characters each, breaking only on a whitespace character
def break_lines(string, indent):
	break_at = 80

	lines = []
	line = ""

	# Break the string into words and loop through each, creating a line that is no longer than 80 characters
	words = string.split(" ")
	for word in words:
		if len(line) + len(word) >= break_at:
			lines.append(line.rstrip())
			line = indent
		line += word + " "

	# Add the last line to the list of lines
	lines.append(line)

	# Convert the list of lines to a string where each line has trailing whitespace removed ends with \n except for the last line
	lines = "\n".join(lines)

	return lines

# A function that accepts the prompt parameter, whether it is an error or info, and displays help, description, and examples
def display_help(prompt, error):

	spaces = 5

	prepend = "!!! "
	label = "INFO"
	message = prompt["name"]

	if error:
		prepend = ">>> "
		label = "ERROR"
		message = "MESSAGE: The value for parameter "+prompt["name"]+" is invalid.\n"+indent(9,prepend)+"Please try again."

	indentStr = indent(spaces, prepend)

	print("\n"+prepend+"------ "+label+" ------")
	print(prepend+message)
	print(break_lines(prepend+"REQUIREMENT: "+prompt["help"], indentStr))
	print(break_lines(prepend+"DESCRIPTION: "+prompt["description"], indentStr))
	print(break_lines(prepend+"EXAMPLE(S): "+prompt["examples"], indentStr))
	print("")

parameters = {}

# loop through each parameter and prompt the user for it, then validate input based on requirement and regex
for key in prompts:
	prompt = prompts[key]
	req = ""
	if prompt["required"]:
		req = " (required)"
	
	# Loop until the user enters a valid value for the parameter
	while True:
		# Prompt the user for the parameter value
		pInput = input(prompt['name']+req+" ["+prompt["default"]+"] : ")

		# Allow user to enter ^ to exit script
		if pInput == "^":
			sys.exit(0)

		# Allow user to enter ! for help and then go back to start of loop
		if pInput == "!":
			display_help(prompt, False)
			continue

		# If the user left blank, use the default value, otherwise, If the user entered a dash, clear the parameter value
		if pInput == "":
			pInput = prompt["default"]
		elif pInput == "-":
			pInput = ""

		# Validate the input based on regex and re-prompt if invalid
		if prompt["regex"] != "":
			if not re.match(prompt["regex"], pInput):
				display_help(prompt, True)
				continue
		break

	parameters[key] = pInput

print("\n------------------------------------------------------------------------------\n")

permissions_boundary_conditional = ""
permissions_boundary_cli = ""

if parameters["PermissionsBoundaryARN"]:
	permissions_boundary_conditional = """,
			"Condition": {
				"StringLike": {
					"$PERMISSIONS_BOUNDARY_ARN$"
				}
			}"""
	permissions_boundary_cli = " --permissions-boundary "+parameters["PermissionsBoundaryARN"]+" \\\n\t"

# set json_contents to stringified json parameters
json_contents = json.dumps(parameters)

# If .defaults.json does not exist, create it and write out the current values in JSON format
if not os.path.isfile(".defaults.json"):
	print("Creating .defaults.json file...")
	# Write the current values to the .defaults.json file in JSON format
	with open(".defaults.json", "w") as f:
		f.write(json_contents)
		f.close()

if not os.path.isfile(".defaults-"+parameters["Prefix"]+".json"):
	print("Creating .defaults-"+parameters["Prefix"]+".json file...")

# Write the current values to the .defaults-PREFIX.json file in JSON format
with open(".defaults-"+parameters["Prefix"]+".json", "w") as f:
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
	contents = contents.replace("$PREFIX$", parameters["Prefix"])
	contents = contents.replace("$PREFIX_UPPER$", parameters["Prefix"].upper())
	contents = contents.replace("$ROLE_PATH$", parameters["RolePath"])
	contents = contents.replace("$AWS_ACCOUNT$", parameters["aws_account_id"])
	contents = contents.replace("$AWS_REGION$", parameters["aws_region"])

	# Replace permissions boundary placeholder which is complex:
	contents = contents.replace(",\"Condition\": \"$PERMISSIONS_BOUNDARY_CONDITIONAL$\"", permissions_boundary_conditional)
	contents = contents.replace("$PERMISSIONS_BOUNDARY_ARN$", parameters["PermissionsBoundaryARN"])

	# if s3_bucket_prefix is provided, replace the placeholder with the value from the command line followed by a hyphen, else replace with blank
	if not parameters["S3BucketNameOrgPrefix"]:
		contents = contents.replace("$S3_ORG_PREFIX$", "")
		print("No S3 bucket prefix provided. Using blank string for s3_bucket_prefix.")
	else:
		contents = contents.replace("$S3_ORG_PREFIX$", parameters["S3BucketNameOrgPrefix"] + "-")

	# Write the updated contents to a new file in the generated directory
	new_file_name = parameters["Prefix"].upper()+"-CloudFormationServicePolicy.json"
	with open(os.path.join(generated_dir, new_file_name), "w") as g:
		g.write(contents)
		g.close()
		f.close()

		# Print a message indicating that the file has been copied
		print("File copied and updated successfully!")
		print(os.path.join(generated_dir, new_file_name))

		# If .tags.json exists, read it in and generate key value pairs for --tags as a formatted string
		tags = []
		
		if os.path.isfile(".tags.json"):
			with open(".tags.json", "r") as f:
				tags = json.load(f)
				f.close()

		# Prepend {"Key": "Atlantis", "Value": "iam"} and {"Key": "atlantis:Prefix", "Value": prefix} to tags list
		tags.insert(0, {"Key": "Atlantis", "Value": "iam"})
		tags.insert(1, {"Key": "atlantis:Prefix", "Value": parameters["Prefix"]})

		tags_cli = "--tags "
		for tag in tags:
			tags_cli += "'{\"Key\": \""+tag["Key"]+"\", \"Value\": \""+tag["Value"]+"\"}' "

		tags_cli = tags_cli.rstrip()

		print("\n==============================================================================")
		print("================================= COMPLETE! ==================================\n")

		# Print a message indicating the aws iam cli commands to create the role and policy and attach it to the role
		print("To create the role attach the permissions policy, execute the following AWS CLI commands (Make sure you are logged into AWS CLI with a user role holding permissions to create the service role!):\n")

		# Generate the CLI command for create-role
		create_role = []
		create_role.append("aws iam create-role --path "+parameters["RolePath"])
		create_role.append("--role-name "+parameters["Prefix"].upper()+"-CloudFormation-Service-Role")
		create_role.append("--description 'Service Role for CloudFormation Service to create and manage pipelines under the '"+parameters["Prefix"]+"' prefix'")
		create_role.append("--assume-role-policy-document file://../Trust-Policy-for-Service-Role.json")
		if parameters["PermissionsBoundaryARN"]:
			create_role.append("--permissions-boundary "+parameters["PermissionsBoundaryARN"])
		create_role.append(tags_cli)

		print(" \\\n\t".join(create_role))
		print("")

		put_policy = []
		put_policy.append("aws iam put-role-policy --role-name "+parameters["Prefix"].upper()+"-CloudFormation-Service-Role")
		put_policy.append("--policy-name "+parameters["Prefix"].upper()+"-CloudFormationServicePolicy")
		put_policy.append("--policy-document file://generated/"+new_file_name)
		print(" \\\n\t".join(put_policy))
		print("")

		print("==============================================================================\n")
