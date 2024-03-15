import os
import shutil
import re
import sys


import tools

hello = "Hello, World"

dirs = {
    "settings": {},
    "cli": {}
}

dirSettings = "./settings/"

dirs["settings"]["Iam"] = dirSettings+"iam/"
dirs["settings"]["Cfn"] = dirSettings+"cfn/"

dirCli = "./cli/"

dirs["cli"]["Iam"] = dirCli+"iam/"
dirs["cli"]["Cfn"] = dirCli+"cfn/"

files = {
    "cfnPipelineTemplate": {},
    "cfnPipelineTemplateInput": {},
    "iamTrustPolicy": {},
    "iamServicePolicy": {},
}

dirs["cfnPipeline"] = "../cloudformation-pipeline-template/"

files["cfnPipelineTemplate"]["name"] = "pipeline-template.yml"
files["cfnPipelineTemplate"]["path"] = dirs["cfnPipeline"]+files["cfnPipelineTemplate"]["name"]

files["cfnPipelineTemplateInput"]["name"] = "sample-input-create-stack.json"
files["cfnPipelineTemplateInput"]["path"] = dirs["cfnPipeline"]+files["cfnPipelineTemplateInput"]["name"]

dirs["iamServiceRole"] = "../iam-cloudformation-service-role/"

files["iamTrustPolicy"]["name"] = "Trust-Policy-for-Service-Role.json"
files["iamTrustPolicy"]["path"] = dirs["iamServiceRole"]+files["iamTrustPolicy"]["name"]

files["iamServicePolicy"]["name"] = "SAMPLE-CloudFormationServicePolicy.json"
files["iamServicePolicy"]["path"] = dirs["iamServiceRole"]+files["iamServicePolicy"]["name"]

dirsAndFiles = [
    {
        "dir": dirs["cli"]["Iam"],
        "files": []
    },
    {
        "dir": dirs["cli"]["Cfn"],
        "files": []
    },
    {
        "dir": dirs["settings"]["Cfn"],
        "files": [
            "sample.tags.json",
            "sample.params.json"
        ],
    },
    {
        "dir": dirs["settings"]["Iam"],
        "files": [
            "sample.tags.json"
        ]
    },
    {
        "dir": dirs["cfnPipeline"],
        "files": [
			files["cfnPipelineTemplate"]["name"]
        ]
    },
    {
        "dir": dirs["iamServiceRole"],
        "files": [
            files["iamTrustPolicy"]["name"],
            files["iamServicePolicy"]["name"]
        ]
    }
]

# loop through dirsAndFiles and check if each dir exists. If it doesn't, create it. 
# Then loop through the files and make sure they exist. If they don't, copy them
for dirAndFile in dirsAndFiles:
    if not os.path.isdir(dirAndFile["dir"]):
        os.makedirs(dirAndFile["dir"])

    for file in dirAndFile["files"]:
        if not os.path.isfile(dirAndFile["dir"]+file):
            shutil.copyfile("./lib/templates/"+file, dirAndFile["dir"]+file)


prompts = {
	"Prefix": {
		"name": "Prefix",
		"required": True,
		"regex": "^[a-z][a-z0-9-]{0,12}[a-z0-9]$",
		"help": "2 to 8 characters. Alphanumeric (lower case) and dashes. Must start with a letter and end with a letter or number.",
		"description": "What is the prefix for this stack?",
		"examples": "atlantis, atlantis-dev, atlantis-prod",
		"default": "atlantis"
	},

	"ProjectId": {
		"name": "Project Id",
		"required": True,
		"regex": "^[a-z][a-z0-9-]*[a-z0-9]$",
		"help": "2 to 20 characters. Alphanumeric lowercase, dashes, and underscores. Must start and end with a letter or number. Do NOT include <Prefix> or <StageId>.",
		"description": "What is the project id for this stack?",
		"examples": "hello-world, finance-app, finance-audit",
		"default": "hello-world"
	},

	"StageId": {
		"name": "Stage Id",
		"required": True,
		"regex": "^[a-z][a-z0-9-]{2,8}[a-z0-9]$",
		"help": "2 to 8 characters. Alphanumeric lowercase, dashes, and underscores. Must start and end with a letter or number.",
		"description": "May be the same, similar, or a short version of the branch name.",
		"examples": "test, stage, beta, test-joe, prod, t95",
		"default": "test"
	},

	"S3BucketNameOrgPrefix": {
		"name": "S3 Bucket Name Org Prefix",
		"required": False,
		"regex": "^[a-z0-9][a-z0-9-]*[a-z0-9]$|^$",
		"help": "S3 bucket prefix must be lowercase, start with a letter, and contain only letters, numbers, and dashes",
		"description": "S3 bucket names must be unique across all AWS accounts. This prefix helps distinguish S3 buckets from each other and will be used in place of using account ID and region to establish uniqueness resulting in shorter bucket names.",
		"examples": "xyzcompany, acme, b2b-solutions-inc",
		"default": ""
	},

	"RolePath": {
		"name": "Role Path",
		"required": True,
		"regex": "^\/[a-zA-Z0-9\/_-]+\/$|^\/$",
		"help": "Role Path must be a single slash OR start and end with a slash, contain alpha numeric characters, dashes, underscores, and slashes.",
		"description": "Role Path is a string of characters that designates the path to the role. For example, the path to the role 'atlantis-admin' is '/atlantis-admin/'.",
		"examples": "/, /atlantis-admin/, /atlantis-admin/dev/, /service-roles/, /application_roles/dev-ops/",
		"default": "/"
	},

	"DeployEnvironment": {
		"name": "Deploy Environment",
		"required": True,
		"regex": "^(DEV|TEST|PROD)$",
		"help": "Deploy Environment must be DEV, TEST, or PROD",
		"description": "What deploy/testing environment will this run under? An environment can contain multiple stages and in coordination with run different tests. Utilize this environment variable to determine your tests, logging levels, and deployment strategies. Can be used for conditionals in the template.",
		"examples": "DEV, TEST, PROD",
		"default": "TEST"
	},

	"ParameterStoreHierarchy": {
		"name": "Parameter Store Hierarchy",
		"required": True,
		"regex": "^\/([a-zA-Z0-9_.-]*[\/])+$|^\/$",
		"help": "Must either be a single slash OR start and end with a slash, contain alpha numeric characters, dashes, underscores, and slashes.",
		"description": "Parameters may be organized within a hierarchy based on your organizational or operations structure. The application will create its parameters within this hierarchy. For example, /Finance/ops/ for this value would then generate /Finance/ops/<env>/<prefix>-<project_id>-<stage>/<parameterName>.",
		"examples": "/, /Finance/, /Finance/ops/, /Finance/ops/dev/",
		"default": "/"
	},

	"AlarmNotificationEmail": {
		"name": "Alarm Notification Email",
		"required": True,
		"regex": "^[a-zA-Z0-9+_.-]+@[a-zA-Z0-9.-]+[a-zA-Z0-9]$",
		"help": "Alarm Notification Email must be in the format: user@example.com",
		"description": "Alarm Notification Email is the email address that will receive CloudWatch alarms.",
		"examples": "user@example.com, finance@example.com, xyzcompany@example.com",
		"default": ""
	},

	"PermissionsBoundaryARN": {
		"name": "Permissions Boundary ARN",
		"required": False,
		"regex": "^$|^arn:aws:iam::[0-9]{12}:policy\/[a-zA-Z0-9\/_-]+$",
		"help": "Permissions Boundary ARN must be in the format: arn:aws:iam::{account_id}:policy/{policy_name}",
		"description": "Permissions Boundary is a policy that is attached to the role and can be used to further restrict the permissions of the role. Your organization may or may not require boundaries.",
		"examples": "arn:aws:iam::123456789012:policy/xyz-org-boundary-policy",
		"default": ""
	},

	"CodeCommitRepository": {
		"name": "CodeCommit Repository",
		"required": True,
		"regex": "^[a-zA-Z0-9][a-zA-Z0-9_\-]{0,62}[a-zA-Z0-9]$",
		"help": "2 to 64 characters. Alphanumeric, dashes, underscores, and spaces. Must start and end with a letter or number.",
		"description": "Identifies the CodeCommit repository which contains the source code to deploy.",
		"examples": "atlantis-financial-application, atlantis-financial-api, atlantis_ui",
		"default": ""
	},

	"CodeCommitBranch": {
		"name": "CodeCommit Branch",
		"required": True,
		"regex": "^[a-zA-Z0-9][a-zA-Z0-9_\-\/]{0,14}[a-zA-Z0-9]$",
		"help": "2 to 16 characters. Alphanumeric, dashes and underscores. Must start and end with a letter or number.",
		"description": "Identifies the CodeCommit branch which contains the source code to deploy.",
		"examples": "main, dev, beta, feature/atlantis-ui",
		"default": "test"
	},

	# Application specific - pipeline-stack.py

	"application-Name": {
		"name": "Application Name",
		"required": True,
		"regex": "^[a-zA-Z0-9][a-zA-Z0-9_\-\/\s]{0,62}[a-zA-Z0-9]$",
		"help": "2 to 64 characters. Alphanumeric, dashes, underscores, and spaces. Must start and end with a letter or number.",
		"description": "A descriptive name to identify the main application irregardless of the stage or branch. This is only used in the Tag Name and not visible anywhere else.",
		"examples": "Financial Transaction Processing, Financial Transaction Audit, atlantis-finance-app",
		"default": ""
	},

	"ServiceRoleARN": {
		"name": "Service Role ARN",
		"required": True,
		"regex": "^$|^arn:aws:iam::[0-9]{12}:role\/[a-zA-Z0-9\/_-]+$",
		"help": "Service Role ARN must be in the format: arn:aws:iam::{account_id}:role/{policy_name}",
		"description": "The Service Role gives CloudFormation permission to create, delete, and manage stacks on your behalf.",
		"examples": "arn:aws:iam::123456789012:role/ATLANTIS-CloudFormation-Service-Role",
		"default": ""
	},

	# Toolchain specific - pipeline-stack.py

	"toolchain_template_location-BucketName": {
		"name": "S3 Bucket Name for Pipeline Template",
		"required": True,
		"regex": "^[a-z0-9][a-z0-9-]*[a-z0-9]$|^$",
		"help": "S3 bucket name must be lowercase, start with a letter, and contain only letters, numbers, and dashes",
		"description": "Where is the pipeline template stored?",
		"examples": "63klabs, mybucket",
		"default": "63klabs"
	},

	"toolchain_template_location-BucketKey": {
		"name": "S3 Bucket Key for Pipeline Template",
		"required": True,
		"regex": "^\/[a-zA-Z0-9\/_-]+\/$|^\/$",
		"help": "S3 bucket key must be lowercase, start and end with a slash and contain only letters, numbers, dashes and underscores",
		"description": "Where is the pipeline template stored?",
		"examples": "/atlantis/v2/, /atlantis/v3/",
		"default": "/atlantis/v2/"
	},

	"toolchain_template_location-FileName": {
		"name": "Pipeline Template File Name",
		"required": True,
		"regex": "^[a-zA-Z0-9][a-zA-Z0-9-_]*[a-zA-Z0-9]\.(yml|yaml|json)$",
		"help": "File name must be lowercase, start with a letter, and contain only letters, numbers, and dashes",
		"description": "What is the pipeline template file name?",
		"examples": "pipeline-template.yml, pipeline-toolchain.yaml",
		"default": "pipeline-template.yml"
	},

	"AwsAccountId": {
        "name": "AWS Account ID",
        "required": True,
		"regex": "^[0-9]{12}$",
		"help": "AWS Account ID must be 12 digits",
		"description": "AWS Account ID is a 12 digit number that identifies the AWS account.",
		"examples": "123456789012, 123456789013, 123456789014",
        "default": ""
    },
    
	"AwsRegion": {
		"name": "AWS Region",
		"required": True,
		"regex": "^[a-z]{2}-[a-z]+-[0-9]$",
		"help": "AWS Region must be lowercase and in the format: us-east-1",
		"description": "AWS Region is a string that identifies the AWS region. For example, the region 'us-east-1' is located in the United States.",
		"examples": "us-east-1, us-west-1, us-west-2, eu-west-1, ap-southeast-1",
		"default": "us-east-1"
	}
}

def getUserInput(prompts, parameters, promptSections):
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
					tools.displayHelp(prompt, False)
					continue

				# If the user left blank, use the default value, otherwise, If the user entered a dash, clear the parameter value
				if pInput == "":
					pInput = prompt["default"]
				elif pInput == "-":
					pInput = ""

				# Validate the input based on regex and re-prompt if invalid
				if prompt["regex"] != "":
					if not re.match(prompt["regex"], pInput):
						tools.displayHelp(prompt, True)
						continue
				break

			parameters[sectionKey][key] = pInput

	tools.printCharStr("-", 80, newlines=True)	
