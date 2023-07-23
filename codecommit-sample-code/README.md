# Serverless Application Model

This sample application is just to seed your first Deploy Pipleline stack.

This is a sample of the Serverless Application Model that deviates from the traditional "Hello World" example as instead it returns JSON formatted predictions.

If you need a basic understanding of AWS SAM I would suggest my first tutorial [Serverless Application Model 8 Ball Example](https://github.com/chadkluck/serverless-sam-8ball-example)

If you want a more advanced application infrastructure stack with internal caching using S3 and DynamoDb and access to SSM Parameter Store for keys and secrets, check out the repository: [Serverless Webservice Template for Pipeline Atlantis](https://github.com/chadkluck/serverless-webservice-template-for-pipeline-atlantis). It is production ready code for a true CI/CD pipeline and I use it as the base of most of my API development.

## Tutorial

If everything went well during deployment, you should be able to access your application endpoint by going to the End Point Test link listed under Resources in your CloudFormation infrastructure stack.

If it did not deploy correctly, please troubleshoot before continuing.

Once everything is tested and working correctly, follow the tutorials for deploying code and adding additional pipelines in [README 4: Atlantis Deploy Pipeline Tutorial](../README-4-Tutorial.md).

When you are ready for a more advanced application tutorial for your Deploy pipeline, check out the repository: [Serverless Webservice Template for Pipeline Atlantis](https://github.com/chadkluck/serverless-webservice-template-for-pipeline-atlantis).
