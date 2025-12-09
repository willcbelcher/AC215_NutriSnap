"""
Quick Vertex AI online prediction test script.

Usage:
  python test_predict.py --image path/to/food.jpg \
    --endpoint projects/<proj>/locations/us-central1/endpoints/<id> \
    --project ac215-471519 --region us-central1
"""

import argparse
import base64
import json
import subprocess
import sys
import urllib.request
import ssl

try:
    import certifi
except ImportError:  # pragma: no cover
    certifi = None


def get_access_token() -> str:
    token = subprocess.check_output(["gcloud", "auth", "print-access-token"]).decode().strip()
    if not token:
        raise RuntimeError("Failed to obtain access token; run `gcloud auth login`.")
    return token


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--image", required=True, help="Path to an image file (jpg/png).")
    parser.add_argument(
        "--endpoint",
        required=True,
        help="Full Vertex endpoint resource: projects/<project>/locations/<region>/endpoints/<id>",
    )
    parser.add_argument("--project", required=True, help="GCP project ID (for logging).")
    parser.add_argument("--region", default="us-central1", help="Vertex region.")
    args = parser.parse_args()

    with open(args.image, "rb") as f:
        encoded = base64.b64encode(f.read()).decode()

    payload = {"instances": [encoded]}
    token = get_access_token()

    url = f"https://{args.region}-aiplatform.googleapis.com/v1/{args.endpoint}:predict"
    body = json.dumps(payload).encode()
    req = urllib.request.Request(
        url,
        data=body,
        headers={
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json",
        },
        method="POST",
    )

    # Use certifi CA bundle when available to avoid macOS CA issues.
    context = None
    if certifi is not None:
        context = ssl.create_default_context(cafile=certifi.where())

    try:
        with urllib.request.urlopen(req, context=context) as resp:
            sys.stdout.write(resp.read().decode() + "\n")
    except Exception as exc:  # pragma: no cover
        sys.stderr.write(f"Request failed: {exc}\n")
        if hasattr(exc, "read"):
            sys.stderr.write(exc.read().decode() + "\n")
        sys.exit(1)


if __name__ == "__main__":
    main()

