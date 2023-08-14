# Deleting

You may want to delete stacks you created, however this is an order to deletion.

1. Empty any S3 buckets created by your infrastructure template
2. Delete the infrastructure stack
3. Delete the deploy stack

Failure to delete in this order will cause errors.

> **NOTE:** Deleting the deploy stack is somewhat optional. To save costs you may wish to delete infrastructure stacks when not in use. However, leaving the deploy stack will not incur any costs unless you run code through it. This means you can keep your deploy stack ready and waiting for any code changes you commit to the monitored branch. It will automatically recreate the infrastructure stack for use.
