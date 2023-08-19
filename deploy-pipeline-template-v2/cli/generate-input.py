import json
import sys

configProjectJson = "config-project.json"

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

    string = string.replace("$TOOLCHAIN_BUCKETNAME$", toolchain_BucketName)
    string = string.replace("$TOOLCHAIN_BUCKETKEY$", toolchain_BucketKey)
    string = string.replace("$TOOLCHAIN_FILENAME$", toolchain_FileName)

    string = string.replace("$AWS_ACCOUNT$", proj_aws_account)
    string = string.replace("$AWS_REGION$", proj_aws_region)
    string = string.replace("$NAME$", proj_name)
    string = string.replace("$DESCRIPTION$", proj_desc)

    string = string.replace("$PREFIX_UPPER$", stack_param_Prefix.upper())
    string = string.replace("$PREFIX$", stack_param_Prefix)
    string = string.replace("$PROJECT_ID$", stack_param__ProjectId)
    string = string.replace("$STAGE_ID$", stack_param_StageId)
    string = string.replace("$S3_ORG_PREFIX$", stack_param_S3BucketNameOrgPrefix)
    string = string.replace("$DEPLOY_ENVIRONMENT$", stack_param_DeployEnvironment)
    string = string.replace("$PARAM_STORE_HIERARCHY$", stack_param_ParameterStoreHierarchy)
    string = string.replace("$ALARM_NOTIFICATION_EMAIL$", stack_param_AlarmNotificationEmail)
    string = string.replace("$REPOSITORY$", stack_param_CodeCommitRepository)
    string = string.replace("$REPOSITORY_BRANCH$", stack_param_CodeCommitBranch)

    if filename == "cloudformation":
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

# TODO if no config file as param, then check to see if config-project exists. 
# TODO if not, then copy the config-project template and instruct user to fill it out
# Bring in the project config file
with open('./'+configProjectJson) as config_file:
    config = json.load(config_file)

# Set the standard variables
toolchain_BucketName = config['toolchain_template_location']['BucketName']
toolchain_BucketKey = config['toolchain_template_location']['BucketKey']
toolchain_FileName = config['toolchain_template_location']['FileName']

proj_aws_account = config['project']['aws_account']
proj_aws_region = config['project']['aws_region']
proj_name = config['project']['name']
proj_desc = config['project']['description']

stack_param_Prefix = config['stack_parameters']['Prefix']
stack_param__ProjectId = config['stack_parameters']['ProjectId']
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

if proj_name != "":
    proj_name = proj_name + " " # add a space

proj_name = proj_name + stack_param_Prefix + "-" + stack_param__ProjectId

if proj_desc == "":
    proj_desc = "Project: "+stack_param_Prefix + "-" + stack_param__ProjectId
    if stack_param_StageId != "":
        proj_desc += " Stage: " + stack_param_StageId
    if stack_param_DeployEnvironment != "":
        proj_desc += " Env: " + stack_param_DeployEnvironment
    if stack_param__ProjectId != "":
        proj_desc += " Repo: " + stack_param_CodeCommitRepository
    if stack_param_CodeCommitBranch != "":
        proj_desc += " Branch: " + stack_param_CodeCommitBranch

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

inputFile(templateCF, "cloudformation")

stringDone = """
=========================================================================
--------------------------------- DONE! ---------------------------------
=========================================================================

The CloudFormation input JSON file for this project has been saved to the 
input folder and may now be used as the --cli-input-json parameter when
creating the CloudFormation stack.

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
aws cloudformation create-stack --cli-input-json file://input/cloudformation.json
=========================================================================

=========================================================================
Check progress:
-------------------------------------------------------------------------
aws cloudformation describe-stacks --stack-name $PREFIX$-$PROJECT_ID$-$STAGE_ID$-deploy
=========================================================================
"""

string = stringDone + stringCF + stringS3

string = string.replace("$STAGE_ID$", stack_param_StageId)
string = string.replace("$PROJECT_ID$", stack_param__ProjectId)
string = string.replace("$PREFIX$", stack_param_Prefix)

string = string.replace("$TOOLCHAIN_BUCKETNAME$", toolchain_BucketName)
string = string.replace("$TOOLCHAIN_BUCKETKEY$", toolchain_BucketKey)
string = string.replace("$TOOLCHAIN_FILENAME$", toolchain_FileName)

print(string)