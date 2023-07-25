import json
import sys

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


def inputFile(template, filename):

    string = json.dumps(template, indent=4)
    string = string.replace("$NAME$", proj_name)
    string = string.replace("$DESCRIPTION$", proj_desc)
    string = string.replace("$STAGE$", proj_deploy_stage)
    string = string.replace("$ENV$", proj_deploy_env)
    string = string.replace("$PROJECT_ID$", proj_id)
    string = string.replace("$PROJECT_STAGE_ID$", proj_stage_id)
    string = string.replace("$PREFIX$", proj_prefix)
    string = string.replace("$AWS_ACCT$", proj_account)
    string = string.replace("$AWS_REGION$", proj_region)
    string = string.replace("$REPOSITORY$", code_repository)
    string = string.replace("$REPOSITORY_BRANCH$", code_branch)
    string = string.replace("$DEFAULT_BRANCH$", default_branch)
    string = string.replace("$TOOLCHAIN_BUCKETNAME$", toolchain_BucketName)
    string = string.replace("$TOOLCHAIN_BUCKETKEY$", toolchain_BucketKey)
    string = string.replace("$SRC_BUCKETNAME$", source_BucketName)
    string = string.replace("$SRC_BUCKETKEY$", source_BucketKey)


    if filename == "cloudformation" or filename == "codestar" or filename == "codecommit":
        # convert back to array
        # remove empty param: ['Parameters']
        # remove empty tags
        # will need conditionals for type

        myData = json.loads(string)

        if filename == "cloudformation":

            myData['Parameters'] = deleteEmptyValues(myData['Parameters'], "indexed", "ParameterValue")
            # if tags are empty, delete
            if len(myData['Parameters']) == 0:
                del myData['Parameters']

            myData['Tags'] = deleteEmptyValues(myData['Tags'], "indexed", "Value")
            # if tags are empty, delete
            if len(myData['Tags']) == 0:
                del myData['Tags']


        elif filename == "codestar":

            myData['toolchain']['stackParameters'] = deleteEmptyValues(myData['toolchain']['stackParameters'], "dict", "")
            # if tags are empty, delete
            if len(myData['toolchain']['stackParameters']) == 0:
                del myData['toolchain']['stackParameters']

            myData['tags'] = deleteEmptyValues(myData['tags'], "dict", "")
            # if tags are empty, delete
            if len(myData['tags']) == 0:
                del myData['tags']

        elif filename == "codecommit":

            myData['tags'] = deleteEmptyValues(myData['tags'], "dict", "")
            # if tags are empty, delete
            if len(myData['tags']) == 0:
                del myData['tags']

        string = json.dumps(myData, indent=4)

    myFile = open("input/"+filename+".json", "w")
    n = myFile.write(string)
    myFile.close()

    print("\n\n======================== input/"+filename+".json ========================\n\n")
    print(string)
    print("\n\n=================== input/"+filename+".json COMPLETE! ===================\n\n")


# Bring in the template files
with open('./input-templates/input-template-cloudformation.json') as templateCF_file:
    templateCF = json.load(templateCF_file)

with open('./input-templates/input-template-codestar.json') as templateCStar_file:
    templateCStar = json.load(templateCStar_file)

with open('./input-templates/input-template-codecommit.json') as templateRepo_file:
    templateRepo = json.load(templateRepo_file)

# TODO if no config file as param, then check to see if config-project exists. 
# TODO if not, then copy the config-project template and instruct user to fill it out
# Bring in the project config file
with open('./config-project.json') as config_file:
    config = json.load(config_file)

# settings
default_branch = "master" # main - CodeStar still places the initial commit to the master branch - This may change March 4, 2021 as CF's default will change to main. CodeStar may change at the same time or be delayed. Note: Once CF starts using main, it needs to be updated in the toolchain

# Set the standard variables
proj_name = config['project']['name']
proj_desc = config['project']['description']
proj_deploy_stage = config['project']['stage']
proj_deploy_env = config['project']['env']
proj_id = config['project']['id']
proj_stage_id = config['project']['id']
proj_account = config['project']['aws_account']
proj_region = config['project']['aws_region']
toolchain_BucketName = config['source_files']['toolchain_bucketname']
toolchain_BucketKey = config['source_files']['toolchain_bucketkey']
source_BucketName = config['source_files']['src_bucketname']
source_BucketKey = config['source_files']['src_bucketkey']
code_repository = config['project']['repository']
code_branch = config['project']['branch']
proj_prefix = "projectstack" # However, CodeStar projects will be awscodestar no matter what

if proj_deploy_stage != "":
    proj_stage_id = proj_stage_id + "-" + proj_deploy_stage

# role ARN - if specified, we replace the template. Otherwise we just keep the template
if config['project']['role_arn'] != "":
    templateCF['RoleARN'] = config['project']['role_arn']
    templateCStar['toolchain']['roleArn'] = config['project']['role_arn']

# Prefix of project. This is pre-pended to all resource names. Default is "project" for cloudformation but "awscodestar" for CodeStar projects
# In order to use "project" or any other prefix, an Inline Policy must be added to the service role (aws-cloudformation-service-role) using the templates/project-service-role.json
# To create a new Prefix, create a new json policy where "project-" is replaced with your new prefix under each resource section.
if config['project']['prefix'] != "":
    proj_prefix = config['project']['prefix']

#------------------------------------------------------------------------------
# CodeCommit
#------------------------------------------------------------------------------
# If we do not name a repository then awscodestar-[projectID] or [projectID] 
# will be used. By default, non-CodeStar projects will use a CodeCommit
# repository with just the base ID (no prefix). 
# The default branch will also be used unless specified
# CodeStar cannot use a repository other than awscodestar-[ProjectID]

if code_repository == "":
    code_repository = proj_prefix +"-"+ proj_id

if code_branch == "":
    if proj_deploy_stage != "":
        code_branch = proj_deploy_stage
    else:
        code_branch = default_branch

#------------------------------------------------------------------------------
# Check for required fields
#------------------------------------------------------------------------------

if toolchain_BucketName == "":
    sys.exit("ERROR: A bucket must be specified for toolchain location.")

#------------------------------------------------------------------------------
# Fill in Name and Description
#------------------------------------------------------------------------------

if proj_name == "":
    proj_name = proj_stage_id

if proj_desc == "":
    proj_desc = "Project: "+proj_id
    if proj_deploy_stage != "":
        proj_desc += " Stage: "+proj_deploy_stage
    if proj_deploy_env != "":
        proj_desc += " Env: "+proj_deploy_env
    if proj_id != "":
        proj_desc += " Repo: "+proj_id
    if code_branch != "":
        proj_desc += " Branch: "+code_branch
#------------------------------------------------------------------------------
#  PARAMETERS
#------------------------------------------------------------------------------

# default param fields

defaultParams = {
    "DeployStage": "$STAGE$",
    "DeployEnvironment": "$ENV$",
    "ParameterStoreBasePath": "",
}

#------------------------------------------------------------------------------
# ParameterStoreBasePath

# We'll copy it over if not empty. This one is special because we have to normalize it
# Then we make sure the template does not have a "" or single "/" value.
# Finally, we make sure that each end of the path contains a "/"

if "ParameterStoreBasePath" in config['stack_parameters'] and config['stack_parameters']['ParameterStoreBasePath'] != "":
    # set template
    defaultParams['ParameterStoreBasePath'] = config['stack_parameters']['ParameterStoreBasePath']

# we strip for 2 reasons: so we can check to see if anything remains "//" to "" and to normalize /asdf to asdf so we can easily place / on either side
defaultParams['ParameterStoreBasePath'] = defaultParams['ParameterStoreBasePath'].strip('/')

if defaultParams['ParameterStoreBasePath'] != "":
    defaultParams['ParameterStoreBasePath'] = "/"+defaultParams['ParameterStoreBasePath']+"/"

# we're done with it
del config['stack_parameters']['ParameterStoreBasePath']

#------------------------------------------------------------------------------
# Merge in any additional params from config and place in input template array

stackParameters = {}
stackParameters.update(config['stack_parameters'])
stackParameters.update(defaultParams)


#------------------------------------------------------------------------------
# place parameters in the CF input

if len(stackParameters) > 0:
    for key in stackParameters.keys():
        item = {"ParameterKey": key, "ParameterValue": stackParameters[key], "UsePreviousValue": False }
        templateCF['Parameters'].append(item)


#-----------------------------------------------------------------------------
# place parameters in the CodeStar input

templateCStar['toolchain']['stackParameters'].update(stackParameters)

# =============================================================================
# Update cloudformation template tags section
#
#    "tags": {}

# Default set

defaultTags = {
    "ProjectStackTemplate": "Atlantis.v01",
    "stage": "$STAGE$",
    "env": "$ENV$"  
}
# note that the tag "CodeStar" will be updated in the CodeStar input json file to "CodeStarProject"

#------------------------------------------------------------------------------
# Merge in any additional tags from config and place in input template array

stackTags = {}
stackTags.update(config['tags'])
stackTags.update(defaultTags)

#------------------------------------------------------------------------------
# place tags in the CF input

if len(stackTags) > 0:
    for key in stackTags.keys():
        item = {"Key": key, "Value": stackTags[key] }
        templateCF['Tags'].append(item)

#-----------------------------------------------------------------------------
# place tags in the CodeStar input

templateCStar['tags'].update(stackTags)



#------------------------------------------------------------------------------
# remove tags that don't apply to CodeCommit

codeCommitTags = stackTags
del codeCommitTags['stage']
del codeCommitTags['env'] 

#-----------------------------------------------------------------------------
# place tags in the CodeCommit input

templateRepo['tags'].update(codeCommitTags)


# =============================================================================
# Export to input.json files

inputFile(templateCF, "cloudformation")
inputFile(templateCStar, "codestar")
inputFile(templateRepo, "codecommit")

with open('./input-templates/input-template-codecommit-init.json', 'r') as init_file:
    data = json.load(init_file)

inputFile(data, "codecommit-init")

with open('./input-templates/input-template-codecommit-branch.json', 'r') as branch_file:
    data = json.load(branch_file)

inputFile(data, "codecommit-branch")



string = """
=========================================================================
--------------------------------- DONE! ---------------------------------
=========================================================================

=========================================================================
For non-CodeStar projects, create and init a repository if you don't 
already have one:
-------------------------------------------------------------------------
aws codecommit create-repository --cli-input-json file://input/codecommit.json
aws codecommit put-file --cli-input-json file://input/codecommit-init.json
aws codecommit create-branch --commit-id [PASTE_commitId_HERE] --cli-input-json file://input/codecommit-branch.json
aws codecommit get-repository --repository-name $REPOSITORY$
-------------------------------------------------------------------------
If you already have one, then create a new branch for your deploy stack
=========================================================================

=========================================================================
Now run the necessary commands to create what you need:
-------------------------------------------------------------------------
aws cloudformation create-stack --cli-input-json file://input/cloudformation.json
aws codestar create-project --cli-input-json file://input/codestar.json
=========================================================================

=========================================================================
Check progress:
-------------------------------------------------------------------------
aws cloudformation describe-stacks --stack-name $prefix$-$yourprojectstageid$-deploy
aws codestar describe-project --id $yourprojectstageid$
=========================================================================
"""

string = string.replace("$yourprojectstageid$", proj_stage_id)
string = string.replace("$yourprojectid$", proj_id)
string = string.replace("$prefix$", proj_prefix)
string = string.replace("$REPOSITORY$", code_repository)
string = string.replace("$AWS_ACCT$", proj_account)
string = string.replace("$AWS_REGION$", proj_region)

print(string)