import os
import json
import shutil
import sys
import re

sys.path.append('./lib')
import tools
import atlantis

print("")
tools.printCharStr("=", 80, bookend="|")
tools.printCharStr(" ", 80, bookend="|", text="CloudFormation Template and AWS CLI Command Generator for Atlantis CI/CD")
tools.printCharStr(" ", 80, bookend="|", text="v2024.02.29")
tools.printCharStr("-", 80, bookend="|")
tools.printCharStr(" ", 80, bookend="|", text="Chad Leigh Kluck")
tools.printCharStr(" ", 80, bookend="|", text="https://github.com/chadkluck/serverless-deploy-pipeline-atlantis")
tools.printCharStr("=", 80, bookend="|")
print("")

constraint = {
    "maxLenPrefixProjId": 28,
    "maxLenStage": 6
}

settingsDir = "./settings/"
settingsDirIam = settingsDir+"iam/"
settingsDirCfn = settingsDir+"cfn/"

cliDir = "./cli/"
cliDirIam = cliDir+"iam/"
cliDirCfn = cliDir+"cfn/"

cfnTemplatePipelineDir = "../cloudformation-pipeline-template/"
cfnTemplatePipelineFileName = "pipeline-template.yml"
cfnTemplatePipelineSampleInputFileName = "sample-input-create-stack.json"
cfnTemplatePipelineFileLocation = cfnTemplatePipelineDir+cfnTemplatePipelineFileName
cfnTemplatePipelineSampleInputFileLocation = cfnTemplatePipelineDir+cfnTemplatePipelineSampleInputFileName

iamTemplateServiceDir = "../iam-cloudformation-service-role/"
iamTemplateServiceRoleFileName = "Trust-Policy-for-Service-Role.json"
iamTemplateServicePolicyFileName = "SAMPLE-CloudFormationServicePolicy.json"
iamTemplateServiceRoleFileLocation = iamTemplateServiceDir+iamTemplateServiceRoleFileName
iamTemplateServicePolicyFileLocation = iamTemplateServiceDir+iamTemplateServicePolicyFileName

dirsAndFiles = [
    {
        "dir": cliDirIam,
        "files": []
    },
    {
        "dir": cliDirCfn,
        "files": []
    },
    {
        "dir": settingsDirCfn,
        "files": [
            "sample.tags.json",
            "sample.params.json"
        ],
    },
    {
        "dir": settingsDirIam,
        "files": [
            "sample.tags.json"
        ]
    },
    {
        "dir": cfnTemplatePipelineDir,
        "files": [
			cfnTemplatePipelineSampleInputFileName
        ]
    },
    {
        "dir": iamTemplateServiceDir,
        "files": [
            iamTemplateServiceRoleFileName,
            iamTemplateServicePolicyFileName
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

argPrefix = "atlantis"
argProjectId = "myproject"
argStageId = "test"
argAcceptDefaults = False
scriptName = sys.argv[0]

# Check to make sure there are at least three arguments. If there are not 3 arguments then display message and exit. If there are 3 arguments set Prefix, ProjectId, and Stage
if len(sys.argv) > 3:
    argPrefix = sys.argv[1]
    argProjectId = sys.argv[2]
    argStageId = sys.argv[3]
else:
    print("\n\nUsage: python "+scriptName+" <Prefix> <ProjectId> <StageId>\n\n")
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
        "FileName": cfnTemplatePipelineFileName
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
        "S3BucketNameOrgPrefix": atlantis.prompts["S3BucketNameOrgPrefix"],
        "RolePath": atlantis.prompts["RolePath"],
        "DeployEnvironment": atlantis.prompts["DeployEnvironment"],
        "ParameterStoreHierarchy": atlantis.prompts["ParameterStoreHierarchy"],
        "AlarmNotificationEmail": "",
        "PermissionsBoundaryARN": "",
        "CodeCommitRepository": "",
        "CodeCommitBranch": atlantis.prompts["CodeCommitBranch"]
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
fileLoc.append(settingsDirIam+".defaults.json")
fileLoc.append(settingsDirIam+".defaults-"+argPrefix+".json")
fileLoc.append(settingsDirCfn+".defaults.json")
fileLoc.append(settingsDirCfn+".defaults-"+argPrefix+".json")
fileLoc.append(settingsDirCfn+".defaults-"+argPrefix+"-"+argProjectId+".json")
fileLoc.append(settingsDirCfn+".defaults-"+argPrefix+"-"+argProjectId+"-"+argStageId+".json")

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
        
print("\n[ Loading .params files... ]")

customStackParamsFileLoc = []
customStackParamsFileLoc.append(settingsDirCfn+".params.json")
customStackParamsFileLoc.append(settingsDirCfn+".params-"+argPrefix+".json")
customStackParamsFileLoc.append(settingsDirCfn+".params-"+argPrefix+"-"+argProjectId+".json")
customStackParamsFileLoc.append(settingsDirCfn+".params-"+argPrefix+"-"+argProjectId+"-"+argStageId+".json")

# If .params.json exists, read it in
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
tagFileLoc.append(settingsDirCfn+".tags.json")
tagFileLoc.append(settingsDirCfn+".tags-"+argPrefix+".json")
tagFileLoc.append(settingsDirCfn+".tags-"+argPrefix+"-"+argProjectId+".json")
tagFileLoc.append(settingsDirCfn+".tags-"+argPrefix+"-"+argProjectId+"-"+argStageId+".json")

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
tools.printCharStr("=", 80, bookend="!", text="INSTRUCTIONS")
tools.printCharStr(" ", 80, bookend="!", text="Enter parameter values to generate CloudFormation Input and AWS CLI commands")
tools.printCharStr("-", 80, bookend="!")
tools.printCharStr(" ", 80, bookend="!", text="The script will then generate an input file and CLI cmds to create the stack")
tools.printCharStr("-", 80, bookend="!")
tools.printCharStr(" ", 80, bookend="!", text="Leave blank and press Enter/Return to accept default in square brackets []")
tools.printCharStr(" ", 80, bookend="!", text="Enter a dash '-' to clear default and leave optional responses blank.")
tools.printCharStr(" ", 80, bookend="!", text="Enter question mark '?' for help.")
tools.printCharStr(" ", 80, bookend="!", text="Enter carat '^' at any prompt to exit script.")
tools.printCharStr("=", 80, bookend="!")
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

prompts["toolchain_template_location"]["BucketName"] = atlantis.prompts["toolchain_template_location-BucketName"]
prompts["toolchain_template_location"]["BucketName"]["default"] = defaults["toolchain_template_location"]["BucketName"]

prompts["toolchain_template_location"]["BucketKey"] = atlantis.prompts["toolchain_template_location-BucketKey"]
prompts["toolchain_template_location"]["BucketKey"]["default"] = defaults["toolchain_template_location"]["BucketKey"]

prompts["toolchain_template_location"]["FileName"] = atlantis.prompts["toolchain_template_location-FileName"]
prompts["toolchain_template_location"]["FileName"]["default"] = defaults["toolchain_template_location"]["FileName"]


prompts["stack_parameters"]["Prefix"] = atlantis.prompts["Prefix"]
prompts["stack_parameters"]["Prefix"]["default"] = defaults["stack_parameters"]["Prefix"]

prompts["stack_parameters"]["ProjectId"] = atlantis.prompts["ProjectId"]
prompts["stack_parameters"]["ProjectId"]["default"] = defaults["stack_parameters"]["ProjectId"]

prompts["stack_parameters"]["StageId"] = atlantis.prompts["StageId"]
prompts["stack_parameters"]["StageId"]["default"] = defaults["stack_parameters"]["StageId"]

prompts["stack_parameters"]["S3BucketNameOrgPrefix"] = atlantis.prompts["S3BucketNameOrgPrefix"]
prompts["stack_parameters"]["S3BucketNameOrgPrefix"]["default"] = defaults["stack_parameters"]["S3BucketNameOrgPrefix"]

prompts["stack_parameters"]["RolePath"] = atlantis.prompts["RolePath"]
prompts["stack_parameters"]["RolePath"]["default"] = defaults["stack_parameters"]["RolePath"]

prompts["stack_parameters"]["DeployEnvironment"] = atlantis.prompts["DeployEnvironment"]
prompts["stack_parameters"]["DeployEnvironment"]["default"] = defaults["stack_parameters"]["DeployEnvironment"]

prompts["stack_parameters"]["ParameterStoreHierarchy"] = atlantis.prompts["ParameterStoreHierarchy"]
prompts["stack_parameters"]["ParameterStoreHierarchy"]["default"] = defaults["stack_parameters"]["ParameterStoreHierarchy"]

prompts["stack_parameters"]["AlarmNotificationEmail"] = atlantis.prompts["AlarmNotificationEmail"]
prompts["stack_parameters"]["AlarmNotificationEmail"]["default"] = defaults["stack_parameters"]["AlarmNotificationEmail"]

prompts["stack_parameters"]["PermissionsBoundaryARN"] = atlantis.prompts["PermissionsBoundaryARN"]
prompts["stack_parameters"]["PermissionsBoundaryARN"]["default"] = defaults["stack_parameters"]["PermissionsBoundaryARN"]

prompts["stack_parameters"]["CodeCommitRepository"] = atlantis.prompts["CodeCommitRepository"]
prompts["stack_parameters"]["CodeCommitRepository"]["default"] = defaults["stack_parameters"]["CodeCommitRepository"]

prompts["stack_parameters"]["CodeCommitBranch"] = atlantis.prompts["CodeCommitBranch"]
prompts["stack_parameters"]["CodeCommitBranch"]["default"] = defaults["stack_parameters"]["CodeCommitBranch"]

prompts["application"]["Name"] = atlantis.prompts["application-Name"]
prompts["application"]["Name"]["default"] = defaults["application"]["Name"]

prompts["application"]["ServiceRoleARN"] = atlantis.prompts["ServiceRoleARN"]
prompts["application"]["ServiceRoleARN"]["default"] = defaults["application"]["ServiceRoleARN"]


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
    settingsDirCfn+".defaults-"+tf["Prefix"]+"-"+tf["ProjectId"]+"-"+tf["StageId"]+".json",
    settingsDirCfn+".defaults-"+tf["Prefix"]+"-"+tf["ProjectId"]+".json",
    settingsDirCfn+".defaults-"+tf["Prefix"]+".json",
    settingsDirCfn+".defaults.json"
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
        # loop and remove any empty parameters from CFN.

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

    fileName = cliDirCfn+"input-create-stack-"+parameters["stack_parameters"]["Prefix"]+"-"+parameters["stack_parameters"]["ProjectId"]+"-"+parameters["stack_parameters"]["StageId"]+".json"
    myFile = open(fileName, "w")
    n = myFile.write(string)
    myFile.close()

    print("")
    tools.printCharStr("-", 80, text=fileName)
    print(string)
    tools.printCharStr("-", 80)

    return fileName

print ("\n[ Loading sample-input-create-stack.json... ]")
# Bring in the input template file
with open(cfnTemplatePipelineSampleInputFileLocation) as templateCFN_file:
    templateCFN = json.load(templateCFN_file)

# check to see if customStackParams is empty
if len(customStackParams) == 0:
    print(" - No Custom Stack Parameters to add from .params files")
else:
    # Add Custom Stack Parameters to input template. Not only are new parameters added, existing ones in the template can be overridden
    print(" + Adding Custom Stack Parameters from .params files...")
    for key in customStackParams.keys():
        customStackParam = { "ParameterKey": key, "ParameterValue": customStackParams[key], "UsePreviousValue": True }
        found = False
        for i in range(len(templateCFN["Parameters"])):
            if templateCFN["Parameters"][i]["ParameterKey"] == key:
                templateCFN["Parameters"][i] = customStackParam
                found = True
                break
        if not found:
            templateCFN["Parameters"].append(customStackParam)

# check to see if customStackTags is empty
if len(customStackTags) == 0:
    print(" - No Custom Stack Tags to add from .tags files")
else:
    print(" + Adding Custom Stack Tags from .tags files...")
    # Add Custom Tags to the input template. Not only are new tags added, existing ones in the template can be overridden
    for i in range(len(customStackTags)):
        found = False
        for j in range(len(templateCFN["Tags"])):
            if templateCFN["Tags"][j]["Key"] == customStackTags[i]["Key"]:
                templateCFN["Tags"][j]["Value"] = customStackTags[i]["Value"]
                found = True
                break
        if not found:
            templateCFN["Tags"].append(customStackTags[i])

print("")
tools.printCharStr("-", 80, text="Updated input template file")
print(json.dumps(templateCFN, indent=4))
tools.printCharStr("-", 80)

inputCFNFilename = saveInputFile(templateCFN)

print("")
tools.printCharStr("=", 80, bookend="!", text="CREATE STACK INSTRUCTIONS")
tools.printCharStr(" ", 80, bookend="!", text="Execute the following AWS CLI commands in order to create the stack.")
tools.printCharStr(" ", 80, bookend="!", text="A copy of the commands have been saved to inputs/ for later use.")
tools.printCharStr("-", 80, bookend="!")
tools.printCharStr(" ", 80, bookend="!", text="Make sure you are logged into AWS CLI with a user role holding permissions")
tools.printCharStr(" ", 80, bookend="!", text="to create the CloudFormation Stack!")
tools.printCharStr("-", 80, bookend="!")
tools.printCharStr(" ", 80, bookend="!", text="Alternately, you can create the stack manually via the AWS Web Console using")
tools.printCharStr(" ", 80, bookend="!", text="values from the CloudFormation input JSON file found in inputs/")
tools.printCharStr("=", 80, bookend="!")
print("")

stringS3Text = """

# -----------------------------------------------------------------------------
# If you need to upload $TOOLCHAIN_FILENAME$ to S3, 
# Run the following commands (adjust paths as needed):

cd $CLI_DIR_CFN_TOOLCHAIN$
aws s3 cp $TOOLCHAIN_FILENAME$ s3://$TOOLCHAIN_BUCKETNAME$$TOOLCHAIN_BUCKETKEY$$TOOLCHAIN_FILENAME$

"""
stringS3 = ""
if parameters["toolchain_template_location"]["BucketName"] != "63klab":
    stringS3 = stringS3Text

stringCFN = """
# -----------------------------------------------------------------------------
# Run cloudformation create-stack command from the $ROOT_CLI_DIR_CFN$ directory (adjust path as needed)

cd $CLI_DIR_CFN$
aws cloudformation create-stack --cli-input-json file://$INPUTCFNFILENAME$

# -----------------------------------------------------------------------------
# Check progress:

aws cloudformation describe-stacks --stack-name $PREFIX$-$PROJECT_ID$-$STAGE_ID$-deploy

"""

cliCommands = stringS3 + stringCFN

cliCommands = subPlaceholders(cliCommands)

cliCommands = cliCommands.replace("$INPUTCFNFILENAME$", inputCFNFilename.replace(cliDirCfn, ""))
cliCommands = cliCommands.replace("$CLI_DIR_CFN$", cliDirCfn)
cliCommands = cliCommands.replace("$CLI_DIR_CFN_TOOLCHAIN$", cfnTemplatePipelineDir)
cliCommands = cliCommands.replace("$ROOT_CLI_DIR_CFN$", cliDirCfn.replace("./", "/scripts-cli/"))

# save cliCommands to cli-<Prefix>-<ProjectId>-<StageId>.txt
cliCommandsFilename = cliDirCfn+"cli-"+parameters["stack_parameters"]["Prefix"]+"-"+parameters["stack_parameters"]["ProjectId"]+"-"+parameters["stack_parameters"]["StageId"]+".txt"
myFile = open(cliCommandsFilename, "w")
n = myFile.write(cliCommands)

print(cliCommands)