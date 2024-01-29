import os
import json
import sys
import re

# Default values - Set any of these defaults to your own in the .defaults file
defaults = {}
defaults["toolchain_template_location"]["BucketName"] = "63klabs"
defaults["toolchain_template_location"]["BucketKey"] = "atlantis/v2"
defaults["toolchain_template_location"]["FileName"] = "pipeline-toolchain.yml"

defaults["application"]["aws_account_id"] = "123456789012"
defaults["application"]["aws_region"] = "us-east-1"

defaults["stack_parameters"]["Prefix"] = "atlantis"
defaults["stack_parameters"]["S3BucketNameOrgPrefix"] = ""
defaults["stack_parameters"]["ParameterStoreHierarchy"] = ""
defaults["stack_parameters"]["S3BucketNameOrgPrefix"] = ""
defaults["stack_parameters"]["RolePath"] = ""
defaults["stack_parameters"]["PermissionsBoundaryARN"] = ""

# check if the .defaults.json file exists and if it does read in the defaults
if os.path.isfile(".defaults.json"):
    with open(".defaults.json", "r") as f:
        defaults = json.load(f)
        print("\nFound .defaults.json file...\n")

# Up to 3 parameters may be passed to the script and each parameter will correspond to a default file
# For example, atlantis will use the .defaults-atlantis.json file and will be loaded first. Any values in this file will overwrite values in defaults.
# atlantis myproject will use the .defaults-myproject.json file and will be loaded second. Any values in this file will overwrite values in atlantis.
# atlantis myproject test will use the .defaults-myproject-test.json file and will be loaded third. Any values in this file will overwrite values in myproject.
if len(sys.argv) > 1:
    fname = ".defaults"
    for i in range(1, len(sys.argv)):
        fname += "-"+sys.argv[i]
        if os.path.isfile(fname+".json"):
            with open(".defaults-"+sys.argv[i]+".json", "r") as f:
                temp = json.load(f)
                # iterate through temp 2D array and replace any values in defaults
                for key in temp.keys():
                    for key2 in temp[key].keys():
                        defaults[key][key2] = temp[key][key2]
                print("\nFound "+fname+".json file...\n")





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