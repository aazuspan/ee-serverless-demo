"""
A demo Earth Engine cloud function.
"""

import datetime
import logging
import os

import ee
import functions_framework


@functions_framework.http
def main(_):
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
    
    try:
        return f"The last Landsat 9 image was {last_cloud_cover.getInfo():.2f}% cloudy."
    except Exception as e:
        logging.error(e)
        return "No new Landsat 9 acquisitions in the last 48 hours..."


if __name__ == "__main__":
    main()