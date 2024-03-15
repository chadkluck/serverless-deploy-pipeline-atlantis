import os
import json
import sys
import re

sys.path.append('./lib')
import tools
import atlantis

print("")
tools.printCharStr("=", 80, bookend="|")
tools.printCharStr(" ", 80, bookend="|", text="CloudFormation Service Role and AWS CLI Command Generator for Atlantis CI/CD")
tools.printCharStr(" ", 80, bookend="|", text="v2024.02.29")
tools.printCharStr("-", 80, bookend="|")
tools.printCharStr(" ", 80, bookend="|", text="Chad Leigh Kluck")
tools.printCharStr(" ", 80, bookend="|", text="https://github.com/chadkluck/serverless-deploy-pipeline-atlantis")
tools.printCharStr("=", 80, bookend="|")
print("")

argPrefix = "atlantis"
argAcceptDefaults = False
scriptName = sys.argv[0]

# Check to make sure there are at least three arguments. If there are not 3 arguments then display message and exit. If there are 3 arguments set Prefix, ProjectId, and Stage
if len(sys.argv) > 1:
    argPrefix = sys.argv[1]
else:
    print("\n\nUsage: python "+scriptName+" <Prefix> <ProjectId> <StageId>\n\n")
    sys.exit()

# Default values - Set any of these defaults to your own in the .defaults file
defaults = {
	"general": {
		"Prefix": "atlantis",
		"S3BucketNameOrgPrefix": "",
		"AwsAccountId": "",
		"AwsRegion": "us-east-1",
		"RolePath": "/",
		"PermissionsBoundaryARN": "",
		"ServiceRoleARN": ""
	}
}

# Read in defaults
    
print("[ Loading .default files... ]")

# Create a file location array - this is the hierarchy of files we will gather defaults from. The most recent file appended (lower on list) will overwrite previous values
fileLoc = []
fileLoc.append(atlantis.dirs["settings"]["Iam"]+".defaults.json")
fileLoc.append(atlantis.dirs["settings"]["Iam"]+".defaults-"+argPrefix+".json")

# iam defaults don't have keysections
for i in range(len(fileLoc)):
	if os.path.isfile(fileLoc[i]):
		with open(fileLoc[i], "r") as f:
			temp = json.load(f)
			for key in temp.keys():
				defaults["general"][key] = temp[key]
		print(" + Found "+fileLoc[i])
	else:
		print(" - Did not find "+fileLoc[i])

# Read in Custom Stack Tags
        
print("\n[ Loading .tags files... ]")

tagFileLoc = []
tagFileLoc.append(atlantis.dirs["settings"]["Iam"]+".tags.json")
tagFileLoc.append(atlantis.dirs["settings"]["Iam"]+".tags-"+argPrefix+".json")

# If .tags.json exists, read it in
customSvcRoleTags = []

for i in range(len(tagFileLoc)):
    if os.path.isfile(tagFileLoc[i]):
        with open(tagFileLoc[i], "r") as f:
            tagData = json.load(f)
            # Both customSvcRoleTags and tagData are arrays with {Key: string, Value: string} elements
            # Loop through the elements in tagData
            #   1. Search customSvcRoleTags array for an element with Key == tagData[i].Key
            #   2. If it exists, replace it. Else, append
            for i in range(len(tagData)):
                found = False
                for j in range(len(customSvcRoleTags)):
                    if customSvcRoleTags[j]["Key"] == tagData[i]["Key"]:
                        customSvcRoleTags[j]["Value"] = tagData[i]["Value"]
                        found = True
                        break
                if not found:
                    customSvcRoleTags.append(tagData[i])
            

            print(" + Found "+tagFileLoc[i])
    else:
        print(" - Did not find "+tagFileLoc[i])

# print the customSvcRoleTags
# print(customSvcRoleTags)

# =============================================================================
# PROMPTS
# =============================================================================

print("")
tools.printCharStr("=", 80, bookend="!", text="INSTRUCTIONS")
tools.printCharStr(" ", 80, bookend="!", text="Enter parameter values to generate IAM Service Role and AWS CLI commands")
tools.printCharStr("-", 80, bookend="!")
tools.printCharStr(" ", 80, bookend="!", text="The script will then generate a policy and CLI commands to create the role")
tools.printCharStr("-", 80, bookend="!")
tools.printCharStr(" ", 80, bookend="!", text="Leave blank and press Enter/Return to accept default in square brackets []")
tools.printCharStr(" ", 80, bookend="!", text="Enter a dash '-' to clear default and leave optional responses blank.")
tools.printCharStr(" ", 80, bookend="!", text="Enter question mark '?' for help.")
tools.printCharStr(" ", 80, bookend="!", text="Enter carat '^' at any prompt to exit script.")
tools.printCharStr("=", 80, bookend="!")
print("")

promptSections = [
    {
        "key": "general",
        "name": "General Information"
    }
]

prompts = {}
parameters = {}
for item in promptSections:
    prompts[item["key"]] = {}
    parameters[item["key"]] = {}

prompts["general"]["Prefix"] = atlantis.prompts["Prefix"]
prompts["general"]["Prefix"]["default"] = defaults["general"]["Prefix"]

prompts["general"]["S3BucketNameOrgPrefix"] = atlantis.prompts["S3BucketNameOrgPrefix"]
prompts["general"]["S3BucketNameOrgPrefix"]["default"] = defaults["general"]["S3BucketNameOrgPrefix"]

prompts["general"]["RolePath"] = atlantis.prompts["RolePath"]
prompts["general"]["RolePath"]["default"] = defaults["general"]["RolePath"]

prompts["general"]["PermissionsBoundaryARN"] = atlantis.prompts["PermissionsBoundaryARN"]
prompts["general"]["PermissionsBoundaryARN"]["default"] = defaults["general"]["PermissionsBoundaryARN"]

prompts["general"]["AwsAccountId"] = atlantis.prompts["AwsAccountId"]
prompts["general"]["AwsAccountId"]["default"] = defaults["general"]["AwsAccountId"]

prompts["general"]["AwsRegion"] = atlantis.prompts["AwsRegion"]
prompts["general"]["AwsRegion"]["default"] = defaults["general"]["AwsRegion"]

atlantis.getUserInput(prompts, parameters, promptSections)

# =============================================================================
# Set Values
# =============================================================================

parameters["general"]["ServiceRoleARN"] = "arn:aws:iam::"+parameters["general"]["AwsAccountId"]+":role"+parameters["general"]["RolePath"]+parameters["general"]["Prefix"].upper()+"-CloudFormation-Service-Role"

permissions_boundary_conditional = ""
permissions_boundary_cli = ""

if parameters["general"]["PermissionsBoundaryARN"]:
	permissions_boundary_conditional = """,
			"Condition": {
				"StringLike": {
					"iam:PermissionsBoundary": "$PERMISSIONS_BOUNDARY_ARN$"
				}
			}"""
	permissions_boundary_cli = " --permissions-boundary "+parameters["general"]["PermissionsBoundaryARN"]+" \\\n\t"

# =============================================================================
# Save files
# =============================================================================

print("[ Saving .default files... ]")

tf = {
    "Prefix": parameters["general"]["Prefix"],
}

# we list the files in reverse as we work up the normal read-in chain
iamInputsFiles = [
    atlantis.dirs["settings"]["Iam"]+".defaults-"+tf["Prefix"]+".json",
    atlantis.dirs["settings"]["Iam"]+".defaults.json"
]

# we will progressively remove data as we save up the chain of files
# to do this we will list the data to remove in reverse order
removals = [
    {
        "general": [
            "Prefix", "ServiceRoleARN"
        ]
    }
]

data = []
data.append(json.dumps(parameters["general"], indent=4))
limitedParam = json.dumps(parameters)

# loop through the removals array and remove the keys from the limitedParam array before appending to data
for removal in removals:
    d = json.loads(limitedParam)
    for key in removal.keys():
        for item in removal[key]:
            d[key].pop(item)
    limitedParam = json.dumps(d, indent=4)
    data.append(json.dumps(d["general"], indent=4))

# go through each index of the cliInputFiles array and write out the corresponding data element and add the corresponding element at index in data
numFiles = len(iamInputsFiles)

for i in range(numFiles):
    file = iamInputsFiles[i]
    d = data[i]
    # create or overwrite file with d
    print(" * Saving "+file+"...")
    with open(file, "w") as f:
        f.write(d)
        f.close()

# =============================================================================
# Generate
# =============================================================================

tools.printCharStr("-", 80)

# Get the current working directory
cwd = os.getcwd()
# Get the path to the generated directory
cli_output_dir = os.path.join(cwd, atlantis.dirs["cli"]["Iam"])
# Open the sample-ATLANTIS-CloudFormationServicePolicy.json file
with open(
	os.path.join(cwd, atlantis.files["iamServicePolicy"]["path"]), "r"
) as f:
	# Read the contents of the file
	contents = f.read()
	# Replace the placeholders with the values from the command line
	contents = contents.replace("$PREFIX$", parameters["general"]["Prefix"])
	contents = contents.replace("$PREFIX_UPPER$", parameters["general"]["Prefix"].upper())
	contents = contents.replace("$ROLE_PATH$", parameters["general"]["RolePath"])
	contents = contents.replace("$AWS_ACCOUNT$", parameters["general"]["AwsAccountId"])
	contents = contents.replace("$AWS_REGION$", parameters["general"]["AwsRegion"])

	# Replace permissions boundary placeholder which is complex:
	contents = contents.replace(",\"Condition\": \"$PERMISSIONS_BOUNDARY_CONDITIONAL$\"", permissions_boundary_conditional)
	contents = contents.replace("$PERMISSIONS_BOUNDARY_ARN$", parameters["general"]["PermissionsBoundaryARN"])

	# if s3_bucket_prefix is provided, replace the placeholder with the value from the command line followed by a hyphen, else replace with blank
	if not parameters["general"]["S3BucketNameOrgPrefix"]:
		contents = contents.replace("$S3_ORG_PREFIX$", "")
	else:
		contents = contents.replace("$S3_ORG_PREFIX$", parameters["general"]["S3BucketNameOrgPrefix"] + "-")

	# Write the updated contents to a new file in the generated directory
	new_file_name = parameters["general"]["Prefix"].upper()+"-CloudFormationServicePolicy.json"
	with open(os.path.join(cli_output_dir, new_file_name), "w") as g:
		g.write(contents)
		g.close()
		f.close()

		# Print a message indicating that the file has been copied
		print("File copied and updated successfully!")
		print(os.path.join(cli_output_dir, new_file_name))

		# Prepend {"Key": "Atlantis", "Value": "iam"} and {"Key": "atlantis:Prefix", "Value": prefix} to tags list
		customSvcRoleTags.insert(0, {"Key": "Atlantis", "Value": "iam"})
		customSvcRoleTags.insert(1, {"Key": "atlantis:Prefix", "Value": parameters["general"]["Prefix"]})

		tags_cli = "--tags "
		for tag in customSvcRoleTags:
			tags_cli += "'{\"Key\": \""+tag["Key"]+"\", \"Value\": \""+tag["Value"]+"\"}' "

		tags_cli = tags_cli.rstrip()

		print("")
		tools.printCharStr("=", 80, bookend="!", text="CREATE ROLE INSTRUCTIONS")
		tools.printCharStr(" ", 80, bookend="!", text="Execute the following AWS CLI commands in order to create the role.")
		tools.printCharStr(" ", 80, bookend="!", text="A copy of the commands have been saved to inputs/ for later use.")
		tools.printCharStr("-", 80, bookend="!")
		tools.printCharStr(" ", 80, bookend="!", text="Make sure you are logged into AWS CLI with a user role holding permissions")
		tools.printCharStr(" ", 80, bookend="!", text="to create the service role!")
		tools.printCharStr("-", 80, bookend="!")
		tools.printCharStr(" ", 80, bookend="!", text="Alternately, you can create the role manually via the AWS Web Console using")
		tools.printCharStr(" ", 80, bookend="!", text="the CloudFormationServicePolicy found in cli/iam/")
		tools.printCharStr("=", 80, bookend="!")
		print("")
            
		win_cmd = []
		msgForWinCLI_1 = "# NOTE FOR BASH ON WINDOWS USERS: When using Bash on Windows you may need to execute the following export command first if you receive the following error:"
		msgForWinCLI_2 = "# ValidationError when calling the CreateRole operation: The specified value for path is invalid."
		win_cmd.append(tools.breakLines(msgForWinCLI_1, tools.indent(4, '#')))
		win_cmd.append(tools.breakLines(msgForWinCLI_2, tools.indent(4, '#')))
		win_cmd.append("")
		win_cmd.append("export MSYS_NO_PATHCONV=1")
            
		stringWinCmd = "\n".join(win_cmd)
    
		# detect if user is on windows and print a message to export MSYS_NO_PATHCONV variable
		if os.name == "nt":
			print(stringWinCmd)

		# Print a message indicating the aws iam cli commands to create the role and policy and attach it to the role

		create_role_comment = []
		create_role_comment.append("# -----------------------------------------------------------------------------")
		create_role_comment.append("# Run iam create-role command from the $ROOT_CLI_DIR_IAM$ directory (adjust path as needed)")
            
		stringCliRoleComment = "\n".join(create_role_comment)
            
		# Generate the CLI command for create-role
		create_role = []
		create_role.append("aws iam create-role --path "+parameters["general"]["RolePath"])
		create_role.append("--role-name "+parameters["general"]["Prefix"].upper()+"-CloudFormation-Service-Role")
		create_role.append("--description 'Service Role for CloudFormation Service to create and manage pipelines under the '"+parameters["general"]["Prefix"]+"' prefix'")
		create_role.append("--assume-role-policy-document file://../Trust-Policy-for-Service-Role.json")
		if parameters["general"]["PermissionsBoundaryARN"]:
			create_role.append("--permissions-boundary "+parameters["general"]["PermissionsBoundaryARN"])
		create_role.append(tags_cli)

		stringCliRole = " \\\n\t".join(create_role)

		put_policy_comment = []
		put_policy_comment.append("# -----------------------------------------------------------------------------")
		put_policy_comment.append("# Run iam put-policy command from the $ROOT_CLI_DIR_IAM$ directory (adjust path as needed)")
            
		stringCliPolicyComment = "\n".join(put_policy_comment)
            
		put_policy = []
		put_policy.append("aws iam put-role-policy --role-name "+parameters["general"]["Prefix"].upper()+"-CloudFormation-Service-Role")
		put_policy.append("--policy-name "+parameters["general"]["Prefix"].upper()+"-CloudFormationServicePolicy")
		put_policy.append("--policy-document file://generated/"+new_file_name)
		
		stringCliPolicy = " \\\n\t".join(put_policy)
        
		cliCommands = stringCliRoleComment + "\n\n" + stringCliRole + "\n\n" + stringCliPolicyComment + "\n\n" + stringCliPolicy + "\n"
            
		# save cliCommands to cli-<Prefix>.txt
		cliCommandsFilename = atlantis.dirs["cli"]["Iam"]+"cli-"+parameters["general"]["Prefix"]+".txt"
		myFile = open(cliCommandsFilename, "w")
		n = myFile.write(stringWinCmd+"\n\n"+cliCommands)

		print(cliCommands)
