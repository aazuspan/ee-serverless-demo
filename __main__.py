from __future__ import annotations

import base64

import pulumi
import pulumi_gcp as gcp


# Enable the required APIs
earthengine = gcp.projects.Service("earthengine-api", service="earthengine.googleapis.com")
cloudbuild = gcp.projects.Service("cloudbuild-api", service="cloudbuild.googleapis.com")
cloudfunctions = gcp.projects.Service("cloudfunctions-api", service="cloudfunctions.googleapis.com")
run = gcp.projects.Service("run-api", service="run.googleapis.com")

# Create a service account that will be used to run authenticated Earth Engine code.
account = gcp.serviceaccount.Account(
    "service-account",
    account_id="demo-service-account",
    display_name="Demo Service Account"
)

# Create an access key for the service account
key = gcp.serviceaccount.Key(
    "service-key",
    service_account_id=account.name,
)

# Create a GCS bucket to store cloud functions
bucket = gcp.storage.Bucket(
    "bucket",
    location="US",
)

# Restrict access to only the service account
gcp.storage.BucketIAMBinding(
    "bucket-binding-admin",
    bucket=bucket.name,
    role="roles/storage.objectAdmin",
    members=[pulumi.Output.concat("serviceAccount:", account.email)],
)

# Write the zipped function to the cloud bucket
function_object = gcp.storage.BucketObject(
    "ee-function-source",
    bucket=bucket.name,
    source=pulumi.FileArchive("./function"),
)

# Create the cloud function
function = gcp.cloudfunctionsv2.Function(
    "ee-function",
    location="us-central1",
    description="A demo serverless EE function",
    build_config={
        "runtime": "python311",
        "entry_point": "main",
        "source": {
            "storage_source": {
                "bucket": function_object.bucket,
                "object": function_object.name,
            },
        },
    },
    service_config={
        "max_instance_count": 1,
        "available_memory": "128Mi",
        "timeout_seconds": 5,
        "environment_variables": {
            "SERVICE_ACCOUNT_KEY": key.private_key.apply(lambda k: base64.b64decode(k).decode()),
        }
    },
    # Wait for required APIs to enable before attempting to build to function
    opts=pulumi.ResourceOptions(depends_on=[cloudbuild, cloudfunctions, run]),
)

# Allow public access to the cloud function
run_invoker = gcp.cloudrun.IamBinding(
    "run-invoker",
    location=function.location,
    service=function.name,
    role="roles/run.invoker",
    members=["allUsers"],
)


# Output the function URL
pulumi.export("function", function.url)