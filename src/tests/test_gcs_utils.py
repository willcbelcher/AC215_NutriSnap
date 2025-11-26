import os
import pytest
import sys
from pathlib import Path

# Add src to path
src_dir = Path(__file__).parent.parent
sys.path.insert(0, str(src_dir))

from gcs_utils import gcs_base_uri, gcs_uri


def test_gcs_base_uri(monkeypatch):
    """Test GCS base URI construction"""
    monkeypatch.setenv("GCS_BUCKET", "test-bucket")
    monkeypatch.setenv("GCS_DATA_VERSION", "v1")

    result = gcs_base_uri()
    assert result == "gs://test-bucket/v1"


def test_gcs_uri_with_parts(monkeypatch):
    """Test GCS URI construction with path parts"""
    monkeypatch.setenv("GCS_BUCKET", "test-bucket")
    monkeypatch.setenv("GCS_DATA_VERSION", "v1")

    result = gcs_uri("train", "data.json")
    assert result == "gs://test-bucket/v1/train/data.json"


def test_gcs_uri_no_parts(monkeypatch):
    """Test GCS URI construction without parts"""
    monkeypatch.setenv("GCS_BUCKET", "test-bucket")
    monkeypatch.setenv("GCS_DATA_VERSION", "v1")

    result = gcs_uri()
    assert result == "gs://test-bucket/v1"


def test_gcs_uri_with_slashes(monkeypatch):
    """Test GCS URI handles leading/trailing slashes correctly"""
    monkeypatch.setenv("GCS_BUCKET", "test-bucket")
    monkeypatch.setenv("GCS_DATA_VERSION", "v1")

    result = gcs_uri("/train/", "/data.json")
    assert result == "gs://test-bucket/v1/train/data.json"
