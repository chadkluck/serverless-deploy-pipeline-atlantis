import os
import json
import sys
import re


constraint = {}
constraint["maxLenPrefixProjId"] = 28
constraint["maxLenStage"] = 6

prefixDefaultDir = "../../iam-cloudformation-service-role/scripts-cli/"

argPrefix = "atlantis"
argProjectId = "myproject"
argStage = "test"

print("")
print("")
print("|==============================================================================|")
print("| CloudFormation Template and AWS CLI Command Generator for Atlantis CI/CD     |")
print("| v2024.02.29                                                                  |")
print("|------------------------------------------------------------------------------|")
print("| Chad Leigh Kluck                                                             |")
print("| github                                                                       |")
print("|==============================================================================|")
print("")

# Default values - Set any of these defaults to your own in the .defaults file
defaults = {}
defaults["toolchain_template_location"]["BucketName"] = "63klabs"
defaults["toolchain_template_location"]["BucketKey"] = "atlantis/v2"
defaults["toolchain_template_location"]["FileName"] = "pipeline-toolchain.yml"

defaults["application"]["aws_account_id"] = "123456789012"
defaults["application"]["aws_region"] = "us-east-1"

defaults["stack_parameters"]["Prefix"] = argPrefix
defaults["stack_parameters"]["S3BucketNameOrgPrefix"] = ""
defaults["stack_parameters"]["ParameterStoreHierarchy"] = ""
defaults["stack_parameters"]["S3BucketNameOrgPrefix"] = ""
defaults["stack_parameters"]["RolePath"] = ""
defaults["stack_parameters"]["PermissionsBoundaryARN"] = ""

# Check to make sure there are three arguments. If there are not 3 arguments then display message and exit. If there are 3 arguments set Prefix, ProjectId, and Stage
if len(sys.argv) == 3:
    argPrefix = sys.argv[1]
    argProjectId = sys.argv[2]
    argStage = sys.argv[3]
else:
    print("\n\nUsage: python generate-cf.py <prefix> <project-id> <stage>\n\n")
    sys.exit()

# Check to make sure Prefix + ProjectId is less than or equal to maxLenPrefixProjId
if len(argPrefix+argProjectId) > constraint["maxLenPrefixProjId"]:
    print("\n\nError: Prefix + ProjectId is greater than "+str(constraint["maxLenPrefixProjId"])+" characters.")
    print("Because some resources have a maximum length of 63 and require additional descriptors in their name, Prefix + ProjectId is restricted to "+str(constraint["maxLenPrefixProjId"])+" characters.\n\n")
    sys.exit()

# Check to make sure Prefix + ProjectId + Stage is less than or equal to maxLenStage + maxLenPrefixProjId
if len(argPrefix+argProjectId+argStage) > constraint["maxLenStage"] + constraint["maxLenPrefixProjId"]:
    print("\n\nError: Prefix + ProjectId + Stage is greater than "+str(constraint["maxLenStage"] + constraint["maxLenPrefixProjId"])+" characters.")
    print("Because some resources have a maximum length of 63 and require additional descriptors in their name, Prefix + ProjectId + Stage is restricted to "+str(constraint["maxLenStage"] + constraint["maxLenPrefixProjId"])+" characters.\n\n")
    sys.exit()

# Create a file location array
fileLoc = []
fileLoc.append(prefixDefaultDir +".defaults.json")
fileLoc.append(prefixDefaultDir +".defaults-"+argPrefix+".json")
fileLoc.append("./.defaults.json")
fileLoc.append("./.defaults-"+argPrefix+".json")
fileLoc.append("./.defaults-"+argPrefix+"-"+argProjectId+".json")
fileLoc.append("./.defaults-"+argPrefix+"-"+argProjectId+"-"+argStage+".json")

for i in range(len(fileLoc)):
    if os.path.isfile(fileLoc[i]):
        with open(fileLoc[i], "r") as f:
            temp = json.load(f)
            for keySection in temp.keys():
                for key in keySection.keys():
                    defaults[keySection][key] = keySection[key]
            print("\nFound "+fileLoc[i] +" file...\n")
    else:
        print("\nDid not find "+fileLoc[i] +"...\n")

# Get the prefix, s3 bucket prefix, aws account id, and aws region from the command line
print("")
print("!==== INSTRUCTIONS ============================================================!")
print("! Enter parameter values to generate CloudFormation Input and AWS CLI commands !")
print("!------------------------------------------------------------------------------!")
print("! The script will then generate an input file and CLI cmds to create the stack !")
print("!------------------------------------------------------------------------------!")
print("! Leave blank and press Enter/Return to accept default in square brackets []   !")
print("! Enter a dash '-' to clear default and leave optional responses blank.        !")
print("! Enter question mark '?' for help.                                            !")
print("! Enter carat '^' at any prompt to exit script.                                !")
print("!==============================================================================!")
print("")

promptSections = [
    {
        "key": "toolchain_template_location",
        "name": "Pipeline Template Location"
    },
    {
        "key": "application",
        "name": "Application"
    },
    {
        "key": "stack_parameters",
        "name": "Stack Parameters"
    },
    {
        "key": "custom_parameters",
        "name": "Custom Parameters"
    },
    {
        "key": "custom_tags",
        "name": "Stack Tags"
    }
]

prompts = {}
prompts["toolchain_template_location"]["BucketName"] = {
    "name": "S3 Bucket Name for Pipeline Template",
    "required": True,
    "regex": "^[a-z0-9][a-z0-9-]*[a-z0-9]$|^$",
    "help": "S3 bucket name must be lowercase, start with a letter, and contain only letters, numbers, and dashes",
    "description": "Where is the pipeline template stored?",
    "examples": "63klabs, mybucket",
    "default": defaults["toolchain_template_location"]["BucketName"]
}
prompts["toolchain_template_location"]["BucketKey"] = {
    "name": "S3 Bucket Key for Pipeline Template",
    "required": True,
    "regex": "^[a-z0-9][a-z0-9-]*[a-z0-9]$|^$",
    "help": "S3 bucket key must be lowercase, start with a letter, and contain only letters, numbers, and dashes",
    "description": "Where is the pipeline template stored?",
    "examples": "atlantis/v2, atlantis/v3",
    "default": defaults["toolchain_template_location"]["BucketKey"]
}
prompts["toolchain_template_location"]["FileName"] = {
    "name": "Pipeline Template File Name",
    "required": True,
    "regex": "^[a-z0-9][a-z0-9-]*[a-z0-9]$|^$",
    "help": "File name must be lowercase, start with a letter, and contain only letters, numbers, and dashes",
    "description": "What is the pipeline template file name?",
    "examples": "pipeline-toolchain.yml, pipeline-toolchain.yaml",
    "default": defaults["toolchain_template_location"]["FileName"]
}

prompts["stack_parameters"]["Prefix"] = {
	"name": "Prefix",
	"required": True,
	"regex": "^[a-z][a-z0-9-]{0,12}[a-z0-9]$",
	"help": "2 to 8 characters. Alphanumeric (lower case) and dashes. Must start with a letter and end with a letter or number.",
	"description": "A prefix helps distinguish applications and assign permissions among teams, departments, and organizational units. For example, users with Finance Development roles may be restricted to resources named with the 'finc' prefix or resources tagged with the 'finc' prefix.",
	"examples": "atlantis, finc, ops, dev-ops, b2b",
	"default": defaults["Prefix"]
}
prompts["stack_parameters"]["S3BucketNameOrgPrefix"] = {
	"name": "S3 Bucket Name Org Prefix",
	"required": False,
	"regex": "^[a-z0-9][a-z0-9-]*[a-z0-9]$|^$",
	"help": "S3 bucket prefix must be lowercase, start with a letter, and contain only letters, numbers, and dashes",
	"description": "S3 bucket names must be unique across all AWS accounts. This prefix helps distinguish S3 buckets from each other and will be used in place of using account ID and region to establish uniqueness resulting in shorter bucket names.",
	"examples": "xyzcompany, acme, b2b-solutions-inc",
	"default": defaults["S3BucketNameOrgPrefix"]
}
prompts["stack_parameters"]["RolePath"] = {
	"name": "Role Path",
	"required": False,
	"regex": "^\/[a-zA-Z0-9\/_-]+\/$|^\/$",
	"help": "Role Path must be a single slash OR start and end with a slash, contain alpha numeric characters, dashes, underscores, and slashes.",
	"description": "Role Path is a string of characters that designates the path to the role. For example, the path to the role 'atlantis-admin' is '/atlantis-admin/'.",
	"examples": "/, /atlantis-admin/, /atlantis-admin/dev/, /service-roles/, /application_roles/dev-ops/",
	"default": defaults["RolePath"]
}
prompts["stack_parameters"]["PermissionsBoundaryARN"] = {
	"name": "Permissions Boundary ARN",
	"required": False,
	"regex": "^$|^arn:aws:iam::[0-9]{12}:policy\/[a-zA-Z0-9\/_-]+$",
	"help": "Permissions Boundary ARN must be in the format: arn:aws:iam::{account_id}:policy/{policy_name}",
	"description": "Permissions Boundary is a policy that is attached to the role and can be used to further restrict the permissions of the role. Your organization may or may not require boundaries.",
	"examples": "arn:aws:iam::123456789012:policy/xyz-org-boundary-policy",
	"default": defaults["PermissionsBoundaryARN"]
}
prompts["application"]["aws_account_id"] = {
	"name": "AWS Account ID",
	"required": True,
	"regex": "^[0-9]{12}$",
	"help": "AWS Account ID must be 12 digits",
	"description": "AWS Account ID is a 12 digit number that identifies the AWS account.",
	"examples": "123456789012, 123456789013, 123456789014",
	"default": defaults["aws_account_id"]
}
prompts["application"]["aws_region"] = {
	"name": "AWS Region",
	"required": True,
	"regex": "^[a-z]{2}-[a-z]+-[0-9]$",
	"help": "AWS Region must be lowercase and in the format: us-east-1",
	"description": "AWS Region is a string that identifies the AWS region. For example, the region 'us-east-1' is located in the United States.",
	"examples": "us-east-1, us-west-1, us-west-2, eu-west-1, ap-southeast-1",
	"default": defaults["aws_region"]
}
prompts["application"]["name"] = {
    "name": "Application Name",
    "required": True,
    "regex": "^[a-zA-Z0-9]{1,64}$",
    "help": "2 to 64 characters. Alphanumeric (lower case) and dashes. Must start with a letter and end with a letter or number.",
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

	prepend = "??? "
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
	req = " "
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
		if pInput == "?":
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



configStackJson = "config-deploy-stack.json"
saveToDir = "" # ex: "custom/" or "" (same dir)

def deleteEmptyValues(data, listtype, valuekey):

    if listtype == "indexed":

        #------------------------------------------------------------------------------
        # loop and remove any empty parameters from CF.

        delList = []
        length = len(data)
        for i in range(length):
            if data[i][valuekey] == "":
                delList.append(i)

        delList.sort(reverse=True)

        length = len(delList)
        for i in range(length):
            data.pop(delList[i])

    else:

        #-----------------------------------------------------------------------------
        # loop and remove empty from CodeStar input

        delList = []
        for key in data.keys():
            if data[key] == "":
                delList.append(key)

        length = len(delList)
        for i in range(length):
            key = delList[i]
            del data[key]
            
    return data


def inputFile(template, filetype):

    string = json.dumps(template, indent=4)

    string = string.replace("$TOOLCHAIN_BUCKETNAME$", toolchain_BucketName)
    string = string.replace("$TOOLCHAIN_BUCKETKEY$", toolchain_BucketKey)
    string = string.replace("$TOOLCHAIN_FILENAME$", toolchain_FileName)

    string = string.replace("$AWS_ACCOUNT$", app_aws_account_id)
    string = string.replace("$AWS_REGION$", app_aws_region)
    string = string.replace("$NAME$", app_name)

    string = string.replace("$PREFIX_UPPER$", stack_param_Prefix.upper())
    string = string.replace("$PREFIX$", stack_param_Prefix)
    string = string.replace("$PROJECT_ID$", stack_param_ProjectId)
    string = string.replace("$STAGE_ID$", stack_param_StageId)
    string = string.replace("$S3_ORG_PREFIX$", stack_param_S3BucketNameOrgPrefix)
    string = string.replace("$DEPLOY_ENVIRONMENT$", stack_param_DeployEnvironment)
    string = string.replace("$PARAM_STORE_HIERARCHY$", stack_param_ParameterStoreHierarchy)
    string = string.replace("$ALARM_NOTIFICATION_EMAIL$", stack_param_AlarmNotificationEmail)
    string = string.replace("$REPOSITORY$", stack_param_CodeCommitRepository)
    string = string.replace("$REPOSITORY_BRANCH$", stack_param_CodeCommitBranch)

    if filetype == "cloudformation":
        # convert back to array
        # remove empty param: ['Parameters']
        # remove empty tags
        # will need conditionals for type

        myData = json.loads(string)

        myData['Parameters'] = deleteEmptyValues(myData['Parameters'], "indexed", "ParameterValue")
        # if tags are empty, delete
        if len(myData['Parameters']) == 0:
            del myData['Parameters']

        myData['Tags'] = deleteEmptyValues(myData['Tags'], "indexed", "Value")
        # if tags are empty, delete
        if len(myData['Tags']) == 0:
            del myData['Tags']

        string = json.dumps(myData, indent=4)

    filename = saveToDir+"input-"+filetype+"-"+stack_param_Prefix+"-"+stack_param_ProjectId+"-"+stack_param_StageId+".json"
    myFile = open(filename, "w")
    n = myFile.write(string)
    myFile.close()

    print("\n\n================== "+filename+" ==================\n\n")
    print(string)
    print("\n\n============= "+filename+" COMPLETE! =============\n\n")

    return filename


# Bring in the template files
with open('./input-templates/input-template-cloudformation.json') as templateCF_file:
    templateCF = json.load(templateCF_file)

# TODO if no config file as param, then check to see if config-project exists. 
# TODO if not, then copy the config-project template and instruct user to fill it out
# Bring in the project config file
with open('./'+configStackJson) as config_file:
    config = json.load(config_file)

# Set the standard variables
toolchain_BucketName = config['toolchain_template_location']['BucketName']
toolchain_BucketKey = config['toolchain_template_location']['BucketKey']
toolchain_FileName = config['toolchain_template_location']['FileName']

app_aws_account_id = config['application']['aws_account_id']
app_aws_region = config['application']['aws_region']
app_name = config['application']['name']

stack_param_Prefix = config['stack_parameters']['Prefix']
stack_param_ProjectId = config['stack_parameters']['ProjectId']
stack_param_StageId = config['stack_parameters']['StageId']
stack_param_S3BucketNameOrgPrefix = config['stack_parameters']['S3BucketNameOrgPrefix']
stack_param_DeployEnvironment = config['stack_parameters']['DeployEnvironment']
stack_param_ParameterStoreHierarchy = config['stack_parameters']['ParameterStoreHierarchy']
stack_param_AlarmNotificationEmail = config['stack_parameters']['AlarmNotificationEmail'] 
stack_param_CodeCommitRepository = config['stack_parameters']['CodeCommitRepository']
stack_param_CodeCommitBranch = config['stack_parameters']['CodeCommitBranch']

#------------------------------------------------------------------------------
# Check for required fields
#------------------------------------------------------------------------------

if toolchain_BucketName == "":
    sys.exit("ERROR: A bucket must be specified for toolchain location.")

#------------------------------------------------------------------------------
# Fill in Name and Description
#------------------------------------------------------------------------------

if app_name != "":
    app_name = app_name + " " # add a space

app_name = app_name + stack_param_Prefix + "-" + stack_param_ProjectId

#------------------------------------------------------------------------------
#  CUSTOM PARAMETERS
#------------------------------------------------------------------------------

stackParameters = {}
stackParameters.update(config['custom_parameters'])

#------------------------------------------------------------------------------
# place parameters in the CF input

if len(stackParameters) > 0:
    for key in stackParameters.keys():
        item = {"ParameterKey": key, "ParameterValue": stackParameters[key], "UsePreviousValue": False }
        templateCF['Parameters'].append(item)

#------------------------------------------------------------------------------
#  CUSTOM TAGS
#------------------------------------------------------------------------------

stackTags = {}
stackTags.update(config['custom_tags'])

#------------------------------------------------------------------------------
# place tags in the CF input

if len(stackTags) > 0:
    for key in stackTags.keys():
        item = {"Key": key, "Value": stackTags[key] }
        templateCF['Tags'].append(item)

# =============================================================================
# Export to input.json files

inputCFFilename = inputFile(templateCF, "cloudformation")

stringDone = """
=========================================================================
--------------------------------- DONE! ---------------------------------
=========================================================================

The CloudFormation input JSON file for this project has been saved to 
$INPUTCFFILENAME$
and may now be used as the --cli-input-json parameter when creating or 
updating the CloudFormation stack.

"""

stringS3Text = """
=========================================================================
IF YOU NEED TO UPLOAD pipeline-toolchain.yml to S3, run the following command:
-------------------------------------------------------------------------
aws s3 cp ../$TOOLCHAIN_FILENAME$ s3://$TOOLCHAIN_BUCKETNAME$/$TOOLCHAIN_BUCKETKEY$/$TOOLCHAIN_FILENAME$
=========================================================================

"""
stringS3 = ""
if toolchain_BucketName != "63klabs":
    stringS3 = stringS3Text

stringCF = """
=========================================================================
Run cloudformation create-stack command
-------------------------------------------------------------------------
aws cloudformation create-stack --cli-input-json file://$INPUTCFFILENAME$
=========================================================================

=========================================================================
Check progress:
-------------------------------------------------------------------------
aws cloudformation describe-stacks --stack-name $PREFIX$-$PROJECT_ID$-$STAGE_ID$-deploy
=========================================================================
"""

string = stringDone + stringCF + stringS3

string = string.replace("$STAGE_ID$", stack_param_StageId)
string = string.replace("$PROJECT_ID$", stack_param_ProjectId)
string = string.replace("$PREFIX$", stack_param_Prefix)

string = string.replace("$TOOLCHAIN_BUCKETNAME$", toolchain_BucketName)
string = string.replace("$TOOLCHAIN_BUCKETKEY$", toolchain_BucketKey)
string = string.replace("$TOOLCHAIN_FILENAME$", toolchain_FileName)

string = string.replace("$INPUTCFFILENAME$", inputCFFilename)

print(string)