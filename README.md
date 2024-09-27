# Earth Engine Serverless Function Demo

This project demonstrates deploying a serverless Earth Engine function to Google Cloud Platform using infrastructure-as-code. [Pulumi](https://www.pulumi.com/) handles building, configuring, authenticating, and deploying the full infrastructure for a minimal Earth Engine cloud function.

Demo deployment: https://ee-function-38e19d5-225331302352.us-central1.run.app/

For more details see the [blog post](http://aazuspan.dev/blog/deploying-earth-engine-cloud-functions-using-iac/).

## Setup

> [!CAUTION]
> This deploys a public cloud function that **will incur costs**.

1. Run `pip install -r requirements.txt` in a virtual environment.
1. [Create a Google Cloud Project](https://cloud.google.com/resource-manager/docs/creating-managing-projects) and copy its full ID into `Pulumi.dev.yaml`. 
1. Add [billing info](https://cloud.google.com/billing/docs/how-to/modify-project) to the project and register it with Earth Engine.
1. [Install Pulumi](https://www.pulumi.com/docs/iac/download-install/).
1. Run `pulumi up` to create the cloud infrastructure and deploy 

## Tear Down

1. Run `pulumi destroy` to remove all cloud infrastructure.
1. Consider disabling billing or deleting the cloud project.
