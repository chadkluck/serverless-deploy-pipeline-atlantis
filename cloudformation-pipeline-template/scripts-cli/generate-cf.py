import os
import json
import sys
import re


def indent(spaces=4, prepend=''):
	return prepend + " " * spaces

# A function that accepts a string and breaks it into lines that are no longer than 80 characters each, breaking only on a whitespace character
def breakLines(string, indent):
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


def charStr(char, num, **kwargs):
    line = char*num

    text = kwargs.get('text', None)
    centered = kwargs.get('centered', None)
    bookend = kwargs.get('bookend', None)
    newline = kwargs.get('newline', None)
    newlines = kwargs.get('newlines', None)

    if text != None:
        text = " "+text+" "
        if centered == True:
            line = text.center(num, char)
        else:
            n = 5
            if char == " ":
                n = 1
            if bookend != None and len(bookend) > n:
                n = len(bookend)
            text = charStr(char, n) + text
            line = text.ljust(num, char)
    if bookend != None:
        n = len(bookend)
        # remove n characters from the beginning and end of the line
        line = line[n:-n]
        # reverse string bookend
        line = bookend + line + bookend[::-1]

    if newline == True:
        line = line + "\n"

    if newlines == True:
        line = "\n" + line + "\n"

    return line



print("")
print(charStr("=", 80, bookend="|"))
print(charStr(" ", 80, bookend="|", text="CloudFormation Template and AWS CLI Command Generator for Atlantis CI/CD"))
print(charStr(" ", 80, bookend="|", text="v2024.02.29"))
print(charStr("-", 80, bookend="|"))
print(charStr(" ", 80, bookend="|", text="Chad Leigh Kluck"))
print(charStr(" ", 80, bookend="|", text="github"))
print(charStr("=", 80, bookend="|"))
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
        "key": "AwsAccountId",
        "mapToSection": "application",
    },
    {
        "key": "AwsRegion",
        "mapToSection": "application",
    },
    {
        "key": "ServiceRoleARN",
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
        "AwsAccountId": "XXXXXXXXXXXX",
        "AwsRegion": "us-east-1",
        "ServiceRoleARN": "",
        "Name": argPrefix+"-"+argProjectId
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
    
print("[ Loading .default files... ]")

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
            for sectionKey in temp.keys():
                # if keySection is a string and in defaultFromIamIndex then map (it came from IAM)
                if type(temp[sectionKey]) is str and sectionKey in defaultsFromIamIndex:
                    defaults[defaultsFromIamIndex[sectionKey]][sectionKey] = temp[sectionKey]
                elif type(temp[sectionKey]) is dict:
                    # otherwise loop through
                    for key in temp[sectionKey].keys():
                        defaults[sectionKey][key] = temp[sectionKey][key]
            print(" + Found "+fileLoc[i])
    else:
        print(" - Did not find "+fileLoc[i])

# print the defaults
# print(defaults)

# Read in Custom Parameters
        
print("\n[ Loading .custom files... ]")

customStackParamsFileLoc = []
customStackParamsFileLoc.append(cfcliInputsDir +".custom.json")
customStackParamsFileLoc.append(cfcliInputsDir +".custom-"+argPrefix+".json")
customStackParamsFileLoc.append(cfcliInputsDir +".custom-"+argPrefix+"-"+argProjectId+".json")
customStackParamsFileLoc.append(cfcliInputsDir +".custom-"+argPrefix+"-"+argProjectId+"-"+argStageId+".json")

# If .custom.json exists, read it in
customStackParams = {}

for i in range(len(customStackParamsFileLoc)):
    if os.path.isfile(customStackParamsFileLoc[i]):
        with open(customStackParamsFileLoc[i], "r") as f:
            customData = json.load(f)
            for key in customData.keys():
                customStackParams[key] = customData[key]
            print(" + Found "+customStackParamsFileLoc[i])
    else:
        print(" - Did not find "+customStackParamsFileLoc[i])

# print the defaults
# print(customStackParams)
        
# Read in Custom Stack Tags
        
print("\n[ Loading .tags files... ]")

tagFileLoc = []
tagFileLoc.append(cfcliInputsDir +".tags.json")
tagFileLoc.append(cfcliInputsDir +".tags-"+argPrefix+".json")
tagFileLoc.append(cfcliInputsDir +".tags-"+argPrefix+"-"+argProjectId+".json")
tagFileLoc.append(cfcliInputsDir +".tags-"+argPrefix+"-"+argProjectId+"-"+argStageId+".json")

# If .tags.json exists, read it in
customStackTags = []

for i in range(len(tagFileLoc)):
    if os.path.isfile(tagFileLoc[i]):
        with open(tagFileLoc[i], "r") as f:
            tagData = json.load(f)
            # Both customStackTags and tagData are arrays with {Key: string, Value: string} elements
            # Loop through the elements in tagData
            #   1. Search customStackTags array for an element with Key == tagData[i].Key
            #   2. If it exists, replace it. Else, append
            for i in range(len(tagData)):
                found = False
                for j in range(len(customStackTags)):
                    if customStackTags[j]["Key"] == tagData[i]["Key"]:
                        customStackTags[j]["Value"] = tagData[i]["Value"]
                        found = True
                        break
                if not found:
                    customStackTags.append(tagData[i])
            

            print(" + Found "+tagFileLoc[i])
    else:
        print(" - Did not find "+tagFileLoc[i])

# print the customStackTags
# print(customStackTags)

# =============================================================================
# PROMPTS
# =============================================================================

print("")
print(charStr("=", 80, bookend="!", text="INSTRUCTIONS"))
print(charStr(" ", 80, bookend="!", text="Enter parameter values to generate CloudFormation Input and AWS CLI commands"))
print(charStr("-", 80, bookend="!"))
print(charStr(" ", 80, bookend="!", text="The script will then generate an input file and CLI cmds to create the stack"))
print(charStr("-", 80, bookend="!"))
print(charStr(" ", 80, bookend="!", text="Leave blank and press Enter/Return to accept default in square brackets []"))
print(charStr(" ", 80, bookend="!", text="Enter a dash '-' to clear default and leave optional responses blank."))
print(charStr(" ", 80, bookend="!", text="Enter question mark '?' for help."))
print(charStr(" ", 80, bookend="!", text="Enter carat '^' at any prompt to exit script."))
print(charStr("=", 80, bookend="!"))
print("")

promptSections = [
    {
        "key": "toolchain_template_location",
        "name": "Pipeline Template Location"
    },

    {
        "key": "stack_parameters",
        "name": "Stack Parameters"
    },
    {
        "key": "application",
        "name": "Application"
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

prompts["application"]["Name"] = {
    "name": "Application Name",
    "required": True,
    "regex": "^[a-zA-Z0-9][a-zA-Z0-9_\-\/\s]{0,62}[a-zA-Z0-9]$",
    "help": "2 to 64 characters. Alphanumeric, dashes, underscores, and spaces. Must start and end with a letter or number.",
    "description": "A descriptive name to identify the main application irregardless of the stage or branch. This is only used in the Tag Name and not visible anywhere else.",
    "examples": "Financial Transaction Processing, Financial Transaction Audit, atlantis-finance-app",
    "default": defaults["application"]["Name"]
}
prompts["application"]["ServiceRoleARN"] = {
	"name": "Service Role ARN",
	"required": False,
	"regex": "^$|^arn:aws:iam::[0-9]{12}:role\/[a-zA-Z0-9\/_-]+$",
	"help": "Service Role ARN must be in the format: arn:aws:iam::{account_id}:role/{policy_name}",
	"description": "The Service Role gives CloudFormation permission to create, delete, and manage stacks on your behalf.",
	"examples": "arn:aws:iam::123456789012:role/ATLANTIS-CloudFormation-Service-Role",
	"default": defaults["application"]["ServiceRoleARN"]
}


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
	print(breakLines(prepend+"REQUIREMENT: "+prompt["help"], indentStr))
	print(breakLines(prepend+"DESCRIPTION: "+prompt["description"], indentStr))
	print(breakLines(prepend+"EXAMPLE(S): "+prompt["examples"], indentStr))
	print("")

#iterate through prompt sections
for section in promptSections:
    sectionKey = section["key"]
    print("\n--- "+section["name"]+": ---\n")
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

print(charStr("-", 80, newlines=True))

# =============================================================================
# Save files
# =============================================================================

print("[ Saving .default files... ]")

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
            "Name"
        ]
    },
    {
        "stack_parameters": [
            "Prefix"
        ],
        "application": [
            "ServiceRoleARN"
        ]
    }
]

if not os.path.isdir(cfcliInputsDir):
	print("Creating "+cfcliInputsDir+" directory...")
	os.mkdir(cfcliInputsDir)
	print("Created "+cfcliInputsDir+" directory.")

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
    print(" * Saving "+file+"...")
    with open(file, "w") as f:
        f.write(d)
        f.close()

# =============================================================================
# Generate
# =============================================================================


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

def subPlaceholders(string):
    string = string.replace("$TOOLCHAIN_BUCKETNAME$", parameters["toolchain_template_location"]["BucketName"])
    string = string.replace("$TOOLCHAIN_BUCKETKEY$", parameters["toolchain_template_location"]["BucketKey"])
    string = string.replace("$TOOLCHAIN_FILENAME$", parameters["toolchain_template_location"]["FileName"])

    string = string.replace("$AWS_ACCOUNT$", defaults["application"]["AwsAccountId"]) # not used in sample-input-create-stack
    string = string.replace("$AWS_REGION$", defaults["application"]["AwsRegion"]) # not used in sample-input-create-stack
    string = string.replace("$SERVICE_ROLE_ARN$", parameters["application"]["ServiceRoleARN"])
    string = string.replace("$NAME$", parameters["application"]["Name"])

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

    return string 

def saveInputFile(template):

    string = json.dumps(template, indent=4)

    string = subPlaceholders(string)

    # convert back to array
    # remove empty Parameters
    # remove empty Tags

    myData = json.loads(string)

    myData['Parameters'] = deleteEmptyValues(myData['Parameters'], "indexed", "ParameterValue")
    # if Parameters are empty, delete
    if len(myData['Parameters']) == 0:
        del myData['Parameters']

    myData['Tags'] = deleteEmptyValues(myData['Tags'], "indexed", "Value")
    # if tags are empty, delete
    if len(myData['Tags']) == 0:
        del myData['Tags']

    string = json.dumps(myData, indent=4)

    filename = cfcliInputsDir+"input-create-stack-"+parameters["stack_parameters"]["Prefix"]+"-"+parameters["stack_parameters"]["ProjectId"]+"-"+parameters["stack_parameters"]["StageId"]+".json"
    myFile = open(filename, "w")
    n = myFile.write(string)
    myFile.close()

    print("")
    print(charStr("-", 80, text=filename))
    print(string)
    print(charStr("-", 80))

    return filename

print ("\n[ Loading sample-input-create-stack.json... ]")
# Bring in the input template file
with open('./sample-input-create-stack.json') as templateCF_file:
    templateCF = json.load(templateCF_file)

# check to see if customStackParams is empty
if len(customStackParams) == 0:
    print(" - No Custom Stack Parameters to add from .custom files")
else:
    # Add Custom Stack Parameters to input template. Not only are new parameters added, existing ones in the template can be overridden
    print(" + Adding Custom Stack Parameters from .custom files...")
    for key in customStackParams.keys():
        customStackParam = { "ParameterKey": key, "ParameterValue": customStackParams[key], "UsePreviousValue": True }
        found = False
        for i in range(len(templateCF["Parameters"])):
            if templateCF["Parameters"][i]["ParameterKey"] == key:
                templateCF["Parameters"][i] = customStackParam
                found = True
                break
        if not found:
            templateCF["Parameters"].append(customStackParam)

# check to see if customStackTags is empty
if len(customStackTags) == 0:
    print(" - No Custom Stack Tags to add from .tags files")
else:
    print(" + Adding Custom Stack Tags from .tags files...")
    # Add Custom Tags to the input template. Not only are new tags added, existing ones in the template can be overridden
    for i in range(len(customStackTags)):
        found = False
        for j in range(len(templateCF["Tags"])):
            if templateCF["Tags"][j]["Key"] == customStackTags[i]["Key"]:
                templateCF["Tags"][j]["Value"] = customStackTags[i]["Value"]
                found = True
                break
        if not found:
            templateCF["Tags"].append(customStackTags[i])

print("")
print(charStr("-", 80, text="Updated input template file"))
print(json.dumps(templateCF, indent=4))
print(charStr("-", 80))

inputCFFilename = saveInputFile(templateCF)

print("")
print(charStr("=", 80, bookend="!", text="CREATE STACK INSTRUCTIONS"))
print(charStr(" ", 80, bookend="!", text="Execute the following AWS CLI commands in order to create the stack."))
print(charStr(" ", 80, bookend="!", text="A copy of the commands have been saved to inputs/ for later use."))
print(charStr("-", 80, bookend="!"))
print(charStr(" ", 80, bookend="!", text="Make sure you are logged into AWS CLI with a user role holding permissions"))
print(charStr(" ", 80, bookend="!", text="to create the CloudFormation Stack!"))
print(charStr("-", 80, bookend="!"))
print(charStr(" ", 80, bookend="!", text="Alternately, you can create the stack manually via the AWS Web Console using"))
print(charStr(" ", 80, bookend="!", text="values from the CloudFormation input JSON file found in inputs/"))
print(charStr("=", 80, bookend="!"))
print("")

stringS3Text = """

# -----------------------------------------------------------------------------
# IF YOU NEED TO UPLOAD $TOOLCHAIN_FILENAME$ to S3, run the following command from the directory containing your pipeline CloudFormation template:

aws s3 cp $TOOLCHAIN_FILENAME$ s3://$TOOLCHAIN_BUCKETNAME$$TOOLCHAIN_BUCKETKEY$$TOOLCHAIN_FILENAME$

"""
stringS3 = ""
if parameters["toolchain_template_location"]["BucketName"] != "63klabs":
    stringS3 = stringS3Text

stringCF = """
# -----------------------------------------------------------------------------
# Run cloudformation create-stack command

aws cloudformation create-stack --cli-input-json file://$INPUTCFFILENAME$

# -----------------------------------------------------------------------------
# Check progress:

aws cloudformation describe-stacks --stack-name $PREFIX$-$PROJECT_ID$-$STAGE_ID$-deploy

"""

cliCommands = stringCF + stringS3

cliCommands = subPlaceholders(cliCommands)

cliCommands = cliCommands.replace("$INPUTCFFILENAME$", inputCFFilename)

# save cliCommands to cli-<Prefix>-<ProjectId>-<StageId>.txt
cliCommandsFilename = cfcliInputsDir+"cli-"+parameters["stack_parameters"]["Prefix"]+"-"+parameters["stack_parameters"]["ProjectId"]+"-"+parameters["stack_parameters"]["StageId"]+".txt"
myFile = open(cliCommandsFilename, "w")
n = myFile.write(cliCommands)

print(cliCommands)