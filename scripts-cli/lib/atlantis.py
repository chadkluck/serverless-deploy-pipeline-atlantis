hello = "Hello, World"


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
# prompts["stack_parameters"]["ProjectId"] = {
#     "name": "Project Id",
#     "required": True,
#     "regex": "^[a-z][a-z0-9-]*[a-z0-9]$",
#     "help": "2 to 64 characters. Alphanumeric lowercase, dashes, and underscores. Must start and end with a letter or number.",
#     "description": "Do NOT include <Prefix> or <StageId>. This is the Project ID for the application. (Minimum 2 characters, suggested maximum of 20) Ex: 'ws-hello-world-test' the Prefix would be 'ws', ProjectId would be 'hello-world', and the StageId would be 'test'. If you get 'S3 bucket name too long' errors then you must shorten the Project ID or use an S3 Org Prefix. Long Project IDs may also be truncated when naming resources.",
#     "examples": "hello-world, finance-app, finance-audit",
#     "default": defaults["stack_parameters"]["ProjectId"]
# }

	"ProjectId": {
		"name": "Project Id",
		"required": True,
		"regex": "^[a-z][a-z0-9-]*[a-z0-9]$",
		"help": "2 to 20 characters. Alphanumeric lowercase, dashes, and underscores. Must start and end with a letter or number. Do NOT include <Prefix> or <StageId>.",
		"description": "What is the project id for this stack?",
		"examples": "hello-world, finance-app, finance-audit",
		"default": "hello-world"
	},
# prompts["stack_parameters"]["StageId"] = {
#     "name": "Stage Id",
#     "required": True,
#     "regex": "^[a-z][a-z0-9-]{2,"+str(constraint["maxLenStage"])+"}[a-z0-9]$",
#     "help": "2 to "+str(constraint["maxLenStage"])+" characters. Alphanumeric lowercase, dashes, and underscores. Must start and end with a letter or number.",
#     "description": "Do NOT include <Prefix> or <ProjectId>. <StageId> does not need to match <DeployEnvironment> or <CodeCommitBranch>. You can have multiple stages in the TEST environment (e.g. test, john-test), and multiple stages in PROD (e.g. stage, beta, prod). Ex: 'ws-hello-world-test' the Prefix would be 'ws', ProjectId would be 'hello-world', and the StageId would be 'test'.",
#     "examples": "test, stage, beta, test-joe, prod",
#     "default": defaults["stack_parameters"]["StageId"]
# }	
	"StageId": {
		"name": "Stage Id",
		"required": True,
		"regex": "^[a-z][a-z0-9-]{2,8}[a-z0-9]$",
		"help": "2 to 8 characters. Alphanumeric lowercase, dashes, and underscores. Must start and end with a letter or number.",
		"description": "May be the same, similar, or a short version of the branch name.",
		"examples": "test, stage, beta, test-joe, prod, t95",
		"default": "test"
	},

	# 	prompts["stack_parameters"]["S3BucketNameOrgPrefix"] = {
	# 	"name": "S3 Bucket Name Org Prefix",
	# 	"required": False,
	# 	"regex": "^[a-z0-9][a-z0-9-]*[a-z0-9]$|^$",
	# 	"help": "S3 bucket prefix must be lowercase, start with a letter, and contain only letters, numbers, and dashes",
	# 	"description": "S3 bucket names must be unique across all AWS accounts. This prefix helps distinguish S3 buckets from each other and will be used in place of using account ID and region to establish uniqueness resulting in shorter bucket names.",
	# 	"examples": "xyzcompany, acme, b2b-solutions-inc",
	# 	"default": defaults["stack_parameters"]["S3BucketNameOrgPrefix"]
	# }

	"S3BucketNameOrgPrefix": {
		"name": "S3 Bucket Name Org Prefix",
		"required": False,
		"regex": "^[a-z0-9][a-z0-9-]*[a-z0-9]$|^$",
		"help": "S3 bucket prefix must be lowercase, start with a letter, and contain only letters, numbers, and dashes",
		"description": "S3 bucket names must be unique across all AWS accounts. This prefix helps distinguish S3 buckets from each other and will be used in place of using account ID and region to establish uniqueness resulting in shorter bucket names.",
		"examples": "xyzcompany, acme, b2b-solutions-inc",
		"default": ""
	},
	# prompts["stack_parameters"]["RolePath"] = {
	# 	"name": "Role Path",
	# 	"required": True,
	# 	"regex": "^\/[a-zA-Z0-9\/_-]+\/$|^\/$",
	# 	"help": "Role Path must be a single slash OR start and end with a slash, contain alpha numeric characters, dashes, underscores, and slashes.",
	# 	"description": "Role Path is a string of characters that designates the path to the role. For example, the path to the role 'atlantis-admin' is '/atlantis-admin/'.",
	# 	"examples": "/, /atlantis-admin/, /atlantis-admin/dev/, /service-roles/, /application_roles/dev-ops/",
	# 	"default": defaults["stack_parameters"]["RolePath"]
	# }
	"RolePath": {
		"name": "Role Path",
		"required": True,
		"regex": "^\/[a-zA-Z0-9\/_-]+\/$|^\/$",
		"help": "Role Path must be a single slash OR start and end with a slash, contain alpha numeric characters, dashes, underscores, and slashes.",
		"description": "Role Path is a string of characters that designates the path to the role. For example, the path to the role 'atlantis-admin' is '/atlantis-admin/'.",
		"examples": "/, /atlantis-admin/, /atlantis-admin/dev/, /service-roles/, /application_roles/dev-ops/",
		"default": "/"
	},
	# prompts["stack_parameters"]["DeployEnvironment"] = {
	#     "name": "Deploy Environment",
	#     "required": True,
	#     "regex": "^(DEV|TEST|PROD)$",
	#     "help": "Deploy Environment must be DEV, TEST, or PROD",
	#     "description": "What deploy/testing environment will this run under? An environment can contain multiple stages and in coordination with run different tests. Utilize this environment variable to determine your tests and app logging levels during deploy. This can be used for conditionals in the template. For example, PROD will use gradual deployment while DEV and TEST is AllAtOnce. Other resources, such as dashboards are created in PROD and not DEV or TEST. Suggested use: DEV for local SAM deployment, TEST for cloud deployment, PROD for stage, beta, and main/prod deployment.",
	#     "examples": "DEV, TEST, PROD",
	#     "default": defaults["stack_parameters"]["DeployEnvironment"]
	# }
	"DeployEnvironment": {
		"name": "Deploy Environment",
		"required": True,
		"regex": "^(DEV|TEST|PROD)$",
		"help": "Deploy Environment must be DEV, TEST, or PROD",
		"description": "What deploy/testing environment will this run under? An environment can contain multiple stages and in coordination with run different tests. Utilize this environment variable to determine your tests, logging levels, and deployment strategies. Can be used for conditionals in the template.",
		"examples": "DEV, TEST, PROD",
		"default": "TEST"
	},
	

	# prompts["stack_parameters"]["ParameterStoreHierarchy"] = {
	#     "name": "Parameter Store Hierarchy",
	#     "required": True,
	#     "regex": "^\/([a-zA-Z0-9_.-]*[\/])+$|^\/$",
	#     "help": "Must either be a single slash OR start and end with a slash, contain alpha numeric characters, dashes, underscores, and slashes.",
	#     "description": "Parameters may be organized within a hierarchy based on your organizational or operations structure. The application will create its parameters within this hierarchy. For example, /Finance/ops/ for this value would then generate /Finance/ops/<env>/<prefix>-<project_id>-<stage>/<parameterName>. Must either be a single '/' or begin and end with a '/'.",
	#     "examples": "/, /Finance/, /Finance/ops/, /Finance/ops/dev/",
	#     "default": defaults["stack_parameters"]["ParameterStoreHierarchy"]
	# }

	"ParameterStoreHierarchy": {
		"name": "Parameter Store Hierarchy",
		"required": True,
		"regex": "^\/([a-zA-Z0-9_.-]*[\/])+$|^\/$",
		"help": "Must either be a single slash OR start and end with a slash, contain alpha numeric characters, dashes, underscores, and slashes.",
		"description": "Parameters may be organized within a hierarchy based on your organizational or operations structure. The application will create its parameters within this hierarchy. For example, /Finance/ops/ for this value would then generate /Finance/ops/<env>/<prefix>-<project_id>-<stage>/<parameterName>.",
		"examples": "/, /Finance/, /Finance/ops/, /Finance/ops/dev/",
		"default": "/"
	},

	# prompts["stack_parameters"]["AlarmNotificationEmail"] = {
	#     "name": "Alarm Notification Email",
	# 	"required": True,
	# 	"regex": "^[A-Za-z0-9+_.-]+@[A-Za-z0-9.-]+$",
	# 	"help": "Alarm Notification Email must be in the format: user@example.com",
	# 	"description": "Alarm Notification Email is the email address that will receive CloudWatch alarms.",
	# 	"examples": "user@example.com, finance@example.com, xyzcompany@example.com",
	# 	"default": defaults["stack_parameters"]["AlarmNotificationEmail"]

	"AlarmNotificationEmail": {
		"name": "Alarm Notification Email",
		"required": True,
		"regex": "^[a-zA-Z0-9+_.-]+@[a-zA-Z0-9.-]+[a-zA-Z0-9]$",
		"help": "Alarm Notification Email must be in the format: user@example.com",
		"description": "Alarm Notification Email is the email address that will receive CloudWatch alarms.",
		"examples": "user@example.com, finance@example.com, xyzcompany@example.com",
		"default": ""
	},

	# }
	# prompts["stack_parameters"]["PermissionsBoundaryARN"] = {
	# 	"name": "Permissions Boundary ARN",
	# 	"required": False,
	# 	"regex": "^$|^arn:aws:iam::[0-9]{12}:policy\/[a-zA-Z0-9\/_-]+$",
	# 	"help": "Permissions Boundary ARN must be in the format: arn:aws:iam::{account_id}:policy/{policy_name}",
	# 	"description": "Permissions Boundary is a policy that is attached to the role and can be used to further restrict the permissions of the role. Your organization may or may not require boundaries.",
	# 	"examples": "arn:aws:iam::123456789012:policy/xyz-org-boundary-policy",
	# 	"default": defaults["stack_parameters"]["PermissionsBoundaryARN"]
	# }

	"PermissionsBoundaryARN": {
		"name": "Permissions Boundary ARN",
		"required": False,
		"regex": "^$|^arn:aws:iam::[0-9]{12}:policy\/[a-zA-Z0-9\/_-]+$",
		"help": "Permissions Boundary ARN must be in the format: arn:aws:iam::{account_id}:policy/{policy_name}",
		"description": "Permissions Boundary is a policy that is attached to the role and can be used to further restrict the permissions of the role. Your organization may or may not require boundaries.",
		"examples": "arn:aws:iam::123456789012:policy/xyz-org-boundary-policy",
		"default": ""
	},

	# prompts["stack_parameters"]["CodeCommitRepository"] = {
	#     "name": "CodeCommit Repository",
	#     "required": True,
	#     "regex": "^[a-zA-Z0-9][a-zA-Z0-9_\-]{0,62}[a-zA-Z0-9]$",
	#     "help": "2 to 64 characters. Alphanumeric, dashes, underscores, and spaces. Must start and end with a letter or number.",
	#     "description": "Identifies the CodeCommit repository which contains the source code to deploy.",
	#     "examples": "atlantis-financial-application, atlantis-financial-api, atlantis_ui",
	#     "default": defaults["stack_parameters"]["CodeCommitRepository"]
	# }

	"CodeCommitRepository": {
		"name": "CodeCommit Repository",
		"required": True,
		"regex": "^[a-zA-Z0-9][a-zA-Z0-9_\-]{0,62}[a-zA-Z0-9]$",
		"help": "2 to 64 characters. Alphanumeric, dashes, underscores, and spaces. Must start and end with a letter or number.",
		"description": "Identifies the CodeCommit repository which contains the source code to deploy.",
		"examples": "atlantis-financial-application, atlantis-financial-api, atlantis_ui",
		"default": ""
	},

	# prompts["stack_parameters"]["CodeCommitBranch"] = {
	#     "name": "CodeCommit Branch",
	#     "required": True,
	#     "regex": "^[a-zA-Z0-9][a-zA-Z0-9_\-\/]{0,14}[a-zA-Z0-9]$",
	#     "help": "2 to 16 characters. Alphanumeric, dashes and underscores. Must start and end with a letter or number.",
	#     "description": "Identifies the CodeCommit branch which contains the source code to deploy.",
	#     "examples": "main, dev, feature/atlantis-ui",
	#     "default": defaults["stack_parameters"]["CodeCommitBranch"]
	# }

	"CodeCommitBranch": {
		"name": "CodeCommit Branch",
		"required": True,
		"regex": "^[a-zA-Z0-9][a-zA-Z0-9_\-\/]{0,14}[a-zA-Z0-9]$",
		"help": "2 to 16 characters. Alphanumeric, dashes and underscores. Must start and end with a letter or number.",
		"description": "Identifies the CodeCommit branch which contains the source code to deploy.",
		"examples": "main, dev, beta, feature/atlantis-ui",
		"default": "test"
	},

	# prompts["application"]["Name"] = {
	#     "name": "Application Name",
	#     "required": True,
	#     "regex": "^[a-zA-Z0-9][a-zA-Z0-9_\-\/\s]{0,62}[a-zA-Z0-9]$",
	#     "help": "2 to 64 characters. Alphanumeric, dashes, underscores, and spaces. Must start and end with a letter or number.",
	#     "description": "A descriptive name to identify the main application irregardless of the stage or branch. This is only used in the Tag Name and not visible anywhere else.",
	#     "examples": "Financial Transaction Processing, Financial Transaction Audit, atlantis-finance-app",
	#     "default": defaults["application"]["Name"]
	# }

	"application-Name": {
		"name": "Application Name",
		"required": True,
		"regex": "^[a-zA-Z0-9][a-zA-Z0-9_\-\/\s]{0,62}[a-zA-Z0-9]$",
		"help": "2 to 64 characters. Alphanumeric, dashes, underscores, and spaces. Must start and end with a letter or number.",
		"description": "A descriptive name to identify the main application irregardless of the stage or branch. This is only used in the Tag Name and not visible anywhere else.",
		"examples": "Financial Transaction Processing, Financial Transaction Audit, atlantis-finance-app",
		"default": ""
	},

	# prompts["application"]["ServiceRoleARN"] = {
	# 	"name": "Service Role ARN",
	# 	"required": False,
	# 	"regex": "^$|^arn:aws:iam::[0-9]{12}:role\/[a-zA-Z0-9\/_-]+$",
	# 	"help": "Service Role ARN must be in the format: arn:aws:iam::{account_id}:role/{policy_name}",
	# 	"description": "The Service Role gives CloudFormation permission to create, delete, and manage stacks on your behalf.",
	# 	"examples": "arn:aws:iam::123456789012:role/ATLANTIS-CloudFormation-Service-Role",
	# 	"default": defaults["application"]["ServiceRoleARN"]
	# }

	"ServiceRoleARN": {
		"name": "Service Role ARN",
		"required": True,
		"regex": "^$|^arn:aws:iam::[0-9]{12}:role\/[a-zA-Z0-9\/_-]+$",
		"help": "Service Role ARN must be in the format: arn:aws:iam::{account_id}:role/{policy_name}",
		"description": "The Service Role gives CloudFormation permission to create, delete, and manage stacks on your behalf.",
		"examples": "arn:aws:iam::123456789012:role/ATLANTIS-CloudFormation-Service-Role",
		"default": ""
	},


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
	}
}

