# Earth Engine + Redis Serverless Function Demo

This project demonstrates deploying a serverless Earth Engine function to Google Cloud Platform with caching via Redis using infrastructure-as-code. The cloud function computes the cloud cover of the last ingested Landsat 9 image and caches results to speed up subsequent requests. [Pulumi](https://www.pulumi.com/) handles building, configuring, authenticating, and deploying the full infrastructure.

For more details, see the [blog post](https://www.aazuspan.dev/blog/earth-engine--cloud-run--redis/).

## Setup

> [!CAUTION]
> This deploys a public cloud function that **will incur costs**, even without use.

1. [Create a Google Cloud Project](https://cloud.google.com/resource-manager/docs/creating-managing-projects) and copy its full ID into `Pulumi.dev.yaml`. 
1. Add [billing info](https://cloud.google.com/billing/docs/how-to/modify-project) to the project and [register it with Earth Engine](https://code.earthengine.google.com/register).
1. [Install Pulumi](https://www.pulumi.com/docs/iac/download-install/) and [uv](https://docs.astral.sh/uv/getting-started/installation/).
1. Run `pulumi up` to create the cloud infrastructure and deploy 

## Tear Down

1. Run `pulumi destroy` to remove all cloud infrastructure.
1. Consider disabling billing or deleting the cloud project.
