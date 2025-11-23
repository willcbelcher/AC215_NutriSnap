import os
from functools import lru_cache

import gcsfs


GCS_PROJECT = os.getenv("GCS_PROJECT")
GCS_BUCKET = os.getenv("GCS_BUCKET")
GCS_DATA_VERSION = os.getenv("GCS_DATA_VERSION")

@lru_cache(maxsize=1)
def get_gcs_fs() -> gcsfs.GCSFileSystem:
    """Return a cached filesystem client authenticated via ADC."""
    return gcsfs.GCSFileSystem(project=GCS_PROJECT, token="google_default")


def gcs_base_uri() -> str:
    return f"gs://{GCS_BUCKET}/{GCS_DATA_VERSION}".rstrip("/")


def gcs_uri(*parts: str) -> str:
    cleaned = [str(part).strip("/") for part in parts if part]
    suffix = "/".join(cleaned)
    base = gcs_base_uri()
    return f"{base}/{suffix}" if suffix else base

