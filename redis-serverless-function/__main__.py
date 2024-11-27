from __future__ import annotations

import base64

import pulumi
import pulumi_gcp as gcp


def enable_apis() -> list[gcp.projects.Service]:
    """Enable all APIs required for the stack."""
    return [
        gcp.projects.Service(f"{api}-api", service=f"{api}.googleapis.com")
        for api in [
            "vpcaccess",
            "cloudbuild",
            "cloudfunctions",
            "earthengine",
            "run",
            "redis",
        ]
    ]


def build_service_key() -> gcp.serviceaccount.Key:
    """Create a service account and key for the function."""
    account = gcp.serviceaccount.Account(
        "service-account",
        account_id="demo-service-account",
        display_name="Demo Service Account"
    )

    return gcp.serviceaccount.Key(
        "service-key",
        service_account_id=account.name,
    )


def build_vpc(
    apis: list[gcp.projects.Service],
) -> tuple[gcp.compute.Network, gcp.vpcaccess.Connector]:
    """Build a VPC and connector to allow communication between function and cache."""
    vpc = gcp.compute.Network(
        "vpc",
        auto_create_subnetworks=True,
        opts=pulumi.ResourceOptions(depends_on=apis),
    )

    vpc_connector = gcp.vpcaccess.Connector(
        "vpc-connector",
        ip_cidr_range="10.8.0.0/28",
        machine_type="f1-micro",
        min_instances=2,
        max_instances=3,
        network=vpc.self_link,
        region="us-central1",
    )

    return vpc, vpc_connector


def build_cache(vpc: gcp.compute.Network) -> gcp.redis.Instance:
    """Build a Redis cache instance."""
    return gcp.redis.Instance(
        "redis-cache",
        memory_size_gb=1,
        region="us-central1",
        replica_count=0,
        tier="BASIC",
        authorized_network=vpc.self_link,
    )


def build_cloud_function(
    *,
    path: str,
    vpc_connector: gcp.vpcaccess.Connector,
    cache: gcp.redis.Instance,
    key: gcp.serviceaccount.Key,
) -> gcp.cloudfunctionsv2.Function:
    """Build a Cloud Run function that talks to the cache via the VPC."""
    src_bucket = gcp.storage.Bucket(
        "src-bucket",
        location="US",
    )

    src_archive = gcp.storage.BucketObject(
        "src-archive",
        bucket=src_bucket.name,
        source=pulumi.asset.FileArchive(path),
    )

    cloud_function = gcp.cloudfunctionsv2.Function(
        "cloud-function",
        location="us-central1",
        build_config={
            "runtime": "python311",
            "entry_point": "main",
            "source": {
                "storage_source": {
                    "bucket": src_archive.bucket,
                    "object": src_archive.name,
                },
            },
        },
        service_config={
            "max_instance_count": 1,
            "available_memory": "128Mi",
            "timeout_seconds": 5,
            "environment_variables": {
                "REDIS_HOST": cache.host,
                "REDIS_PORT": cache.port,
                "SERVICE_ACCOUNT_KEY": key.private_key.apply(lambda k: base64.b64decode(k).decode()),
            },
            "vpc_connector": vpc_connector.name,
            "vpc_connector_egress_settings": "PRIVATE_RANGES_ONLY",
        },
        opts=pulumi.ResourceOptions(depends_on=[cache]),
    )

    gcp.cloudrun.IamBinding(
        "cloud-function-invoker",
        location=cloud_function.location,
        service=cloud_function.name,
        role="roles/run.invoker",
        members=["allUsers"],
    )

    return cloud_function


apis = enable_apis()
vpc, vpc_connector = build_vpc(apis)

cloudrun = build_cloud_function(
    path="./src", 
    vpc_connector=vpc_connector, 
    cache=build_cache(vpc), 
    key=build_service_key(),
)

pulumi.export("function-url", cloudrun.url)
