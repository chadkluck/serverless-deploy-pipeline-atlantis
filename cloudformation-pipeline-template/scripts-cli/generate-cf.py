import os
import json
import sys
import re

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

constraint = {
    "maxLenPrefixProjId": 28,
    "maxLenStage": 6
}

iamcliInputsDir = "../../iam-cloudformation-service-role/scripts-cli/"
cfcliInputsDir = "./inputs/"

argPrefix = "atlantis"
argProjectId = "myproject"
argStageId = "test"

# Check to make sure there are three arguments. If there are not 3 arguments then display message and exit. If there are 3 arguments set Prefix, ProjectId, and Stage
if len(sys.argv) == 4:
    argPrefix = sys.argv[1]
    argProjectId = sys.argv[2]
    argStageId = sys.argv[3]
else:
    print("\n\nUsage: python generate-cf.py <Prefix> <ProjectId> <StageId>\n\n")
    sys.exit()

# Check to make sure Prefix + ProjectId is less than or equal to maxLenPrefixProjId
if len(argPrefix+argProjectId) > constraint["maxLenPrefixProjId"]:
    print("\n\nError: Prefix + ProjectId is greater than "+str(constraint["maxLenPrefixProjId"])+" characters.")
    print("Because some resources have a maximum length of 63 and require additional descriptors in their name, Prefix + ProjectId is restricted to "+str(constraint["maxLenPrefixProjId"])+" characters.\n\n")
    sys.exit()

# Check to make sure Prefix + ProjectId + Stage is less than or equal to maxLenStage + maxLenPrefixProjId
if len(argPrefix+argProjectId+argStageId) > constraint["maxLenStage"] + constraint["maxLenPrefixProjId"]:
    print("\n\nError: Prefix + ProjectId + Stage is greater than "+str(constraint["maxLenStage"] + constraint["maxLenPrefixProjId"])+" characters.")
    print("Because some resources have a maximum length of 63 and require additional descriptors in their name, Prefix + ProjectId + Stage is restricted to "+str(constraint["maxLenStage"] + constraint["maxLenPrefixProjId"])+" characters.\n\n")
    sys.exit()

defaultsFromIam = [
    {
        "key": "Prefix",
        "mapToSection": "stack_parameters",
    },
    {
        "key": "S3BucketNameOrgPrefix",
        "mapToSection": "stack_parameters",
    },
    {
        "key": "RolePath",
        "mapToSection": "stack_parameters",
    },
    {
        "key": "PermissionsBoundaryARN",
        "mapToSection": "stack_parameters",
    },
    {
        "key": "aws_account_id",
        "mapToSection": "application",
    },
    {
        "key": "aws_region",
        "mapToSection": "application",
    }
]

defaultsFromIamArray = []
defaultsFromIamIndex = {}
# put each key from defaultsFromIam into an array
for item in defaultsFromIam:
    defaultsFromIamArray.append(item["key"])
    defaultsFromIamIndex[item["key"]] = item["mapToSection"]

# Default values - Set any of these defaults to your own in the .defaults file
defaults = {
    "toolchain_template_location": {
        "BucketName": "63klabs",
        "BucketKey": "/atlantis/v2/",
        "FileName": "pipeline-template.yml"
    },
    "application": {
        "aws_account_id": "XXXXXXXXXXXX",
        "aws_region": "us-east-1",
        "service_role_arn": "",
        "name": argPrefix+"-"+argProjectId
    },
    "stack_parameters": {
        "Prefix": argPrefix,
        "ProjectId": argProjectId,
        "StageId": argStageId,
        "S3BucketNameOrgPrefix": "",
        "RolePath": "/",
        "DeployEnvironment": "TEST",
        "ParameterStoreHierarchy": "/",
        "AlarmNotificationEmail": "",
        "PermissionsBoundaryARN": "",
        "CodeCommitRepository": "",
        "CodeCommitBranch": "test"
    }
}

# if stage begins with dev then set DeployEnvironment to DEV, test to TEST, and prod, beta, stage to PROD
if re.match("^dev", argStageId):
    defaults["stack_parameters"]["DeployEnvironment"] = "DEV"

if re.match("^test", argStageId):
    defaults["stack_parameters"]["DeployEnvironment"] = "TEST"

if re.match("^prod|^beta|^stage", argStageId):
    defaults["stack_parameters"]["DeployEnvironment"] = "PROD"

# if stage begins with prod then set CodeCommitBranch to main, otherwise set CodeCommitBranch to the stageId
if re.match("^prod", argStageId):
    defaults["stack_parameters"]["CodeCommitBranch"] = "main"
else:
    defaults["stack_parameters"]["CodeCommitBranch"] = argStageId

# Read in defaults
    
print("Loading .default files...")

# Create a file location array - this is the hierarchy of files we will gather defaults from. The most recent file will overwrite previous values
fileLoc = []
fileLoc.append(iamcliInputsDir +".defaults.json")
fileLoc.append(iamcliInputsDir +".defaults-"+argPrefix+".json")
fileLoc.append(cfcliInputsDir +".defaults.json")
fileLoc.append(cfcliInputsDir +".defaults-"+argPrefix+".json")
fileLoc.append(cfcliInputsDir +".defaults-"+argPrefix+"-"+argProjectId+".json")
fileLoc.append(cfcliInputsDir +".defaults-"+argPrefix+"-"+argProjectId+"-"+argStageId+".json")

# iam defaults don't have keysections

for i in range(len(fileLoc)):
    if os.path.isfile(fileLoc[i]):
        with open(fileLoc[i], "r") as f:
            temp = json.load(f)
            for keySection in temp.keys():
                # if keySection is a string and in defaultFromIamIndex then map (it came from IAM)
                if type(keySection) is str and keySection in defaultsFromIamIndex:
                    defaults[defaultsFromIamIndex[keySection]][keySection] = temp[keySection]
                elif type(keySection) is dict:
                    # otherwise loop through
                    for key in keySection.keys():
                        defaults[keySection][key] = keySection[key]
            print("Found "+fileLoc[i] +" file...")
    else:
        print("Did not find "+fileLoc[i] +"...")

# print the defaults
# print(defaults)

# Read in tags
        
print("Loading .tags files...")

tagFileLoc = []
tagFileLoc.append(cfcliInputsDir +".tags.json")
tagFileLoc.append(cfcliInputsDir +".tags-"+argPrefix+".json")
tagFileLoc.append(cfcliInputsDir +".tags-"+argPrefix+"-"+argProjectId+".json")
tagFileLoc.append(cfcliInputsDir +".tags-"+argPrefix+"-"+argProjectId+"-"+argStageId+".json")

# If .tags.json exists, read it in
tags = []

for i in range(len(tagFileLoc)):
    if os.path.isfile(tagFileLoc[i]):
        with open(tagFileLoc[i], "r") as f:
            tagData = json.load(f)
            # Both tags and tagData are arrays with {Key: string, Value: string} elements
            # Loop through the elements in tagData
            #   1. Search tags array for an element with Key == tagData[i].Key
            #   2. If it exists, replace it. Else, append
            for i in range(len(tagData)):
                found = False
                for j in range(len(tags)):
                    if tags[j]["Key"] == tagData[i]["Key"]:
                        tags[j]["Value"] = tagData[i]["Value"]
                        found = True
                        break
                if not found:
                    tags.append(tagData[i])
            

            print("Found "+tagFileLoc[i] +" file...")
    else:
        print("Did not find "+tagFileLoc[i] +"...")

# print the tags
# print(tags)

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
    }
]

prompts = {}
parameters = {}
for item in promptSections:
    prompts[item["key"]] = {}
    parameters[item["key"]] = {}

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
    "regex": "^\/[a-zA-Z0-9\/_-]+\/$|^\/$",
    "help": "S3 bucket key must be lowercase, start and end with a slash and contain only letters, numbers, dashes and underscores",
    "description": "Where is the pipeline template stored?",
    "examples": "/atlantis/v2/, /atlantis/v3/",
    "default": defaults["toolchain_template_location"]["BucketKey"]
}
prompts["toolchain_template_location"]["FileName"] = {
    "name": "Pipeline Template File Name",
    "required": True,
    "regex": "^[a-zA-Z0-9][a-zA-Z0-9-_]*[a-zA-Z0-9]\.(yml|yaml|json)$",
    "help": "File name must be lowercase, start with a letter, and contain only letters, numbers, and dashes",
    "description": "What is the pipeline template file name?",
    "examples": "pipeline-template.yml, pipeline-toolchain.yaml",
    "default": defaults["toolchain_template_location"]["FileName"]
}

prompts["application"]["aws_account_id"] = {
	"name": "AWS Account ID",
	"required": True,
	"regex": "^[0-9]{12}$",
	"help": "AWS Account ID must be 12 digits",
	"description": "AWS Account ID is a 12 digit number that identifies the AWS account.",
	"examples": "123456789012, 123456789013, 123456789014",
	"default": defaults["application"]["aws_account_id"]
}
prompts["application"]["aws_region"] = {
	"name": "AWS Region",
	"required": True,
	"regex": "^[a-z]{2}-[a-z]+-[0-9]$",
	"help": "AWS Region must be lowercase and in the format: us-east-1",
	"description": "AWS Region is a string that identifies the AWS region. For example, the region 'us-east-1' is located in the United States.",
	"examples": "us-east-1, us-west-1, us-west-2, eu-west-1, ap-southeast-1",
	"default": defaults["application"]["aws_region"]
}
prompts["application"]["name"] = {
    "name": "Application Name",
    "required": True,
    "regex": "^[a-zA-Z0-9][a-zA-Z0-9_\-\/\s]{0,62}[a-zA-Z0-9]$",
    "help": "2 to 64 characters. Alphanumeric, dashes, underscores, and spaces. Must start and end with a letter or number.",
    "description": "Application name is a string that identifies the main application irregardless of the stage or branch.",
    "examples": "Financial Transaction Processing, Financial Transaction Audit, atlantis-finance-app",
    "default": defaults["application"]["name"]
}

prompts["stack_parameters"]["Prefix"] = {
	"name": "Prefix",
	"required": True,
	"regex": "^[a-z][a-z0-9-]{0,12}[a-z0-9]$",
	"help": "2 to 8 characters. Alphanumeric (lower case) and dashes. Must start with a letter and end with a letter or number.",
	"description": "A prefix helps distinguish applications and assign permissions among teams, departments, and organizational units. For example, users with Finance Development roles may be restricted to resources named with the 'finc' prefix or resources tagged with the 'finc' prefix.",
	"examples": "atlantis, finc, ops, dev-ops, b2b",
	"default": defaults["stack_parameters"]["Prefix"]
}
prompts["stack_parameters"]["ProjectId"] = {
    "name": "Project Id",
    "required": True,
    "regex": "^[a-z][a-z0-9-]*[a-z0-9]$",
    "help": "2 to 64 characters. Alphanumeric lowercase, dashes, and underscores. Must start and end with a letter or number.",
    "description": "Do NOT include <Prefix> or <StageId>. This is the Project ID for the application. (Minimum 2 characters, suggested maximum of 20) Ex: 'ws-hello-world-test' the Prefix would be 'ws', ProjectId would be 'hello-world', and the StageId would be 'test'. If you get 'S3 bucket name too long' errors then you must shorten the Project ID or use an S3 Org Prefix. Long Project IDs may also be truncated when naming resources.",
    "examples": "hello-world, finance-app, finance-audit",
    "default": defaults["stack_parameters"]["ProjectId"]
}
prompts["stack_parameters"]["StageId"] = {
    "name": "Stage Id",
    "required": True,
    "regex": "^[a-z][a-z0-9-]{2,"+str(constraint["maxLenStage"])+"}[a-z0-9]$",
    "help": "2 to "+str(constraint["maxLenStage"])+" characters. Alphanumeric lowercase, dashes, and underscores. Must start and end with a letter or number.",
    "description": "Do NOT include <Prefix> or <ProjectId>. <StageId> does not need to match <DeployEnvironment> or <CodeCommitBranch>. You can have multiple stages in the TEST environment (e.g. test, john-test), and multiple stages in PROD (e.g. stage, beta, prod). Ex: 'ws-hello-world-test' the Prefix would be 'ws', ProjectId would be 'hello-world', and the StageId would be 'test'.",
    "examples": "test, stage, beta, test-joe, prod",
    "default": defaults["stack_parameters"]["StageId"]
}
prompts["stack_parameters"]["S3BucketNameOrgPrefix"] = {
	"name": "S3 Bucket Name Org Prefix",
	"required": False,
	"regex": "^[a-z0-9][a-z0-9-]*[a-z0-9]$|^$",
	"help": "S3 bucket prefix must be lowercase, start with a letter, and contain only letters, numbers, and dashes",
	"description": "S3 bucket names must be unique across all AWS accounts. This prefix helps distinguish S3 buckets from each other and will be used in place of using account ID and region to establish uniqueness resulting in shorter bucket names.",
	"examples": "xyzcompany, acme, b2b-solutions-inc",
	"default": defaults["stack_parameters"]["S3BucketNameOrgPrefix"]
}
prompts["stack_parameters"]["RolePath"] = {
	"name": "Role Path",
	"required": True,
	"regex": "^\/[a-zA-Z0-9\/_-]+\/$|^\/$",
	"help": "Role Path must be a single slash OR start and end with a slash, contain alpha numeric characters, dashes, underscores, and slashes.",
	"description": "Role Path is a string of characters that designates the path to the role. For example, the path to the role 'atlantis-admin' is '/atlantis-admin/'.",
	"examples": "/, /atlantis-admin/, /atlantis-admin/dev/, /service-roles/, /application_roles/dev-ops/",
	"default": defaults["stack_parameters"]["RolePath"]
}
prompts["stack_parameters"]["DeployEnvironment"] = {
    "name": "Deploy Environment",
    "required": True,
    "regex": "^(DEV|TEST|PROD)$",
    "help": "Deploy Environment must be DEV, TEST, or PROD",
    "description": "What deploy/testing environment will this run under? An environment can contain multiple stages and in coordination with run different tests. Utilize this environment variable to determine your tests and app logging levels during deploy. This can be used for conditionals in the template. For example, PROD will use gradual deployment while DEV and TEST is AllAtOnce. Other resources, such as dashboards are created in PROD and not DEV or TEST. Suggested use: DEV for local SAM deployment, TEST for cloud deployment, PROD for stage, beta, and main/prod deployment.",
    "examples": "DEV, TEST, PROD",
    "default": defaults["stack_parameters"]["DeployEnvironment"]
}
prompts["stack_parameters"]["ParameterStoreHierarchy"] = {
    "name": "Parameter Store Hierarchy",
    "required": True,
    "regex": "^\/([a-zA-Z0-9_.-]*[\/])+$|^\/$",
    "help": "Must either be a single slash OR start and end with a slash, contain alpha numeric characters, dashes, underscores, and slashes.",
    "description": "Parameters may be organized within a hierarchy based on your organizational or operations structure. The application will create its parameters within this hierarchy. For example, /Finance/ops/ for this value would then generate /Finance/ops/<env>/<prefix>-<project_id>-<stage>/<parameterName>. Must either be a single '/' or begin and end with a '/'.",
    "examples": "/, /Finance/, /Finance/ops/, /Finance/ops/dev/",
    "default": defaults["stack_parameters"]["ParameterStoreHierarchy"]
}
prompts["stack_parameters"]["AlarmNotificationEmail"] = {
    "name": "Alarm Notification Email",
	"required": True,
	"regex": "^[A-Za-z0-9+_.-]+@[A-Za-z0-9.-]+$",
	"help": "Alarm Notification Email must be in the format: user@example.com",
	"description": "Alarm Notification Email is the email address that will receive CloudWatch alarms.",
	"examples": "user@example.com, finance@example.com, xyzcompany@example.com",
	"default": defaults["stack_parameters"]["AlarmNotificationEmail"]
}
prompts["stack_parameters"]["PermissionsBoundaryARN"] = {
	"name": "Permissions Boundary ARN",
	"required": False,
	"regex": "^$|^arn:aws:iam::[0-9]{12}:policy\/[a-zA-Z0-9\/_-]+$",
	"help": "Permissions Boundary ARN must be in the format: arn:aws:iam::{account_id}:policy/{policy_name}",
	"description": "Permissions Boundary is a policy that is attached to the role and can be used to further restrict the permissions of the role. Your organization may or may not require boundaries.",
	"examples": "arn:aws:iam::123456789012:policy/xyz-org-boundary-policy",
	"default": defaults["stack_parameters"]["PermissionsBoundaryARN"]
}
prompts["stack_parameters"]["CodeCommitRepository"] = {
    "name": "CodeCommit Repository",
    "required": True,
    "regex": "^[a-zA-Z0-9][a-zA-Z0-9_\-]{0,62}[a-zA-Z0-9]$",
    "help": "2 to 64 characters. Alphanumeric, dashes, underscores, and spaces. Must start and end with a letter or number.",
    "description": "Identifies the CodeCommit repository which contains the source code to deploy.",
    "examples": "atlantis-financial-application, atlantis-financial-api, atlantis_ui",
    "default": defaults["stack_parameters"]["CodeCommitRepository"]
}
prompts["stack_parameters"]["CodeCommitBranch"] = {
    "name": "CodeCommit Branch",
    "required": True,
    "regex": "^[a-zA-Z0-9][a-zA-Z0-9_\-\/]{0,14}[a-zA-Z0-9]$",
    "help": "2 to 16 characters. Alphanumeric, dashes and underscores. Must start and end with a letter or number.",
    "description": "Identifies the CodeCommit branch which contains the source code to deploy.",
    "examples": "main, dev, feature/atlantis-ui",
    "default": defaults["stack_parameters"]["CodeCommitBranch"]
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

#iterate through prompt sections
for section in promptSections:
    sectionKey = section["key"]
    # loop through each parameter and prompt the user for it, then validate input based on requirement and regex
    for key in prompts[sectionKey]:
        prompt = prompts[sectionKey][key]
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

        parameters[sectionKey][key] = pInput

print("\n------------------------------------------------------------------------------\n")
                    
configStackJson = "config-deploy-stack.json"
tf = {
    "Prefix": parameters["stack_parameters"]["Prefix"],
    "ProjectId": parameters["stack_parameters"]["ProjectId"],
    "StageId": parameters["stack_parameters"]["StageId"],
}
# we list the files in reverse as we work up the normal read-in chain
cliInputsFiles = [
    cfcliInputsDir+".defaults-"+tf["Prefix"]+"-"+tf["ProjectId"]+"-"+tf["StageId"]+".json",
    cfcliInputsDir+".defaults-"+tf["Prefix"]+"-"+tf["ProjectId"]+".json",
    cfcliInputsDir+".defaults-"+tf["Prefix"]+".json",
    cfcliInputsDir+".defaults.json"
]

# we will progressively remove data as we save up the chain of files
# to do this we will list the data to remove in reverse order
removals = [
    {
        "stack_parameters": [
            "StageId", "CodeCommitBranch", "DeployEnvironment"
        ]
    },
    {
        "stack_parameters": [
            "ProjectId", "CodeCommitRepository"
        ],
        "application": [
            "name"
        ]
    },
    {
        "stack_parameters": [
            "Prefix"
        ]
    }
]

if not os.path.isdir("inputs"):
	print("Creating inputs/ directory...")
	os.mkdir("inputs")
	print("Created inputs/ directory.")

data = []
data.append(json.dumps(parameters, indent=4))
limitedParam = json.dumps(parameters)

# loop through the removals array and remove the keys from the limitedParam array before appending to data
for removal in removals:
    d = json.loads(limitedParam)
    for key in removal.keys():
        for item in removal[key]:
            d[key].pop(item)
    limitedParam = json.dumps(d, indent=4)
    data.append(limitedParam)

# go through each index of the cliInputFiles array and write out the corresponding data element and add the corresponding element at index in data
numFiles = len(cliInputsFiles)

for i in range(numFiles):
    file = cliInputsFiles[i]
    d = data[i]
    # create or overwrite file with d
    print("Saving "+file+"...")
    with open(file, "w") as f:
        f.write(d)
        f.close()

        
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


def inputFile(template):

    string = json.dumps(template, indent=4)

    string = string.replace("$TOOLCHAIN_BUCKETNAME$", parameters["toolchain_template_location"]["BucketName"])
    string = string.replace("$TOOLCHAIN_BUCKETKEY$", parameters["toolchain_template_location"]["BucketKey"])
    string = string.replace("$TOOLCHAIN_FILENAME$", parameters["toolchain_template_location"]["FileName"])

    string = string.replace("$AWS_ACCOUNT$", parameters["application"]["aws_account_id"]) # not used in sample-input-create-stack
    string = string.replace("$AWS_REGION$", parameters["application"]["aws_region"])
    string = string.replace("$SERVICE_ROLE_ARN$", parameters["application"]["service_role_arn"])
    string = string.replace("$NAME$", parameters["application"]["name"])

    string = string.replace("$PREFIX_UPPER$", parameters["stack_parameters"]["Prefix"].upper())
    string = string.replace("$PREFIX$", parameters["stack_parameters"]["Prefix"])
    string = string.replace("$PROJECT_ID$", parameters["stack_parameters"]["ProjectId"])
    string = string.replace("$STAGE_ID$", parameters["stack_parameters"]["StageId"])
    string = string.replace("$S3_ORG_PREFIX$", parameters["stack_parameters"]["S3BucketNameOrgPrefix"])
    string = string.replace("$ROLE_PATH$", parameters["stack_parameters"]["RolePath"])
    string = string.replace("$DEPLOY_ENVIRONMENT$", parameters["stack_parameters"]["DeployEnvironment"])
    string = string.replace("$PARAM_STORE_HIERARCHY$", parameters["stack_parameters"]["ParameterStoreHierarchy"])
    string = string.replace("$ALARM_NOTIFICATION_EMAIL$", parameters["stack_parameters"]["AlarmNotificationEmail"])
    string = string.replace("$PERMISSIONS_BOUNDARY_ARN$", parameters["stack_parameters"]["PermissionsBoundaryARN"])
    string = string.replace("$REPOSITORY$", parameters["stack_parameters"]["CodeCommitRepository"])
    string = string.replace("$REPOSITORY_BRANCH$", parameters["stack_parameters"]["CodeCommitBranch"])


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

# exit script
sys.exit(0)

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