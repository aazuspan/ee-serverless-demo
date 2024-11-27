import datetime
import logging
import os

import ee
from flask import jsonify
import redis
import functions_framework


try:
    redis_host = os.environ["REDIS_HOST"]
    redis_port = int(os.environ["REDIS_PORT"])

    redis_client = redis.Redis(
        host=redis_host,
        port=redis_port,
        socket_connect_timeout=5,
    )
    redis_client.ping()
except Exception as e:
    logging.error(e, exc_info=True)
    redis_client = None


def calculate_last_cloud_cover() -> float:
    """Calculate the cloud cover of the last Landsat 9 image."""
    key_data = os.environ["SERVICE_ACCOUNT_KEY"]

    credentials = ee.ServiceAccountCredentials(None, key_data=key_data)
    ee.Initialize(credentials)

    now = datetime.datetime.now(datetime.timezone.utc).timestamp() * 1000    
    last_cloud_cover = (
        ee.ImageCollection("LANDSAT/LC09/C02/T1")
        .filterDate(now - 172_800_000, now)
        .sort("system:time_start", False)
        .first()
        .get("CLOUD_COVER")
    )

    return last_cloud_cover.getInfo()


@functions_framework.http
def main(_):
    if redis_client is None:
        return jsonify({"error": "Internal error"}), 500

    last_cloud_cover = redis_client.get("last_cloud_cover")

    if last_cloud_cover is None:
        from_cache = False

        try:
            last_cloud_cover = calculate_last_cloud_cover()
            redis_client.set("last_cloud_cover", last_cloud_cover, ex=3600)
        except Exception as e:
            logging.error(e, exc_info=True)
            last_cloud_cover = -1.0

    else:
        from_cache = True
        last_cloud_cover = float(last_cloud_cover)

    return jsonify(
        {
            "last_cloud_cover": last_cloud_cover,
            "from_cache": from_cache,
        }
    )
