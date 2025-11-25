import io
import json
import os
import shutil
from pathlib import Path
from typing import Dict, List

import gcsfs
import torch
from PIL import Image
from transformers import AutoImageProcessor, AutoModelForImageClassification


MODEL_GCS_URI = os.getenv("MODEL_GCS_URI")
MODEL_CACHE_DIR = Path(os.getenv("MODEL_CACHE_DIR", "/tmp/nutrisnap-model"))
MODEL_BASE_PROCESSOR = os.getenv("MODEL_BASE_PROCESSOR")
MODEL_DEFAULT_MODEL_TYPE = os.getenv("MODEL_DEFAULT_MODEL_TYPE", "vit")
_BUNDLE = None


def _gcs_path() -> str:
    if not MODEL_GCS_URI or not MODEL_GCS_URI.startswith("gs://"):
        raise RuntimeError("MODEL_GCS_URI must be set to gs://bucket/path")
    return MODEL_GCS_URI[5:]


def _artifact_dir() -> Path:
    target = MODEL_CACHE_DIR / "artifact"
    target.mkdir(parents=True, exist_ok=True)
    return target


def _locate_model_root(base_dir: Path) -> Path:
    matches = sorted(base_dir.rglob("config.json"), key=lambda p: len(p.relative_to(base_dir).parts))
    return matches[0].parent if matches else base_dir


def _download_model() -> Path:
    target = _artifact_dir()
    sentinel = target / ".ready"
    if sentinel.exists():
        return _locate_model_root(target)

    if target.exists():
        shutil.rmtree(target)
        target.mkdir(parents=True, exist_ok=True)

    remote = _gcs_path()
    fs = gcsfs.GCSFileSystem()
    if not fs.exists(remote):
        raise FileNotFoundError(f"GCS path gs://{remote} does not exist")
    fs.get(remote, str(target), recursive=True)
    sentinel.touch()
    return _locate_model_root(target)


def _inject_model_type(model_dir: Path) -> None:
    config_path = model_dir / "config.json"
    if not config_path.exists():
        return
    with config_path.open("r") as f:
        data = json.load(f)
    if "model_type" not in data:
        data["model_type"] = MODEL_DEFAULT_MODEL_TYPE
        with config_path.open("w") as f:
            json.dump(data, f)


def _load_bundle():
    model_dir = _download_model()
    _inject_model_type(model_dir)

    model = AutoModelForImageClassification.from_pretrained(str(model_dir))
    candidates = [str(model_dir)]
    fallback = MODEL_BASE_PROCESSOR or getattr(model.config, "_name_or_path", None)
    if fallback and fallback not in candidates:
        candidates.append(fallback)

    processor = None
    for source in candidates:
        try:
            processor = AutoImageProcessor.from_pretrained(source)
            break
        except Exception:
            continue
    if processor is None:
        raise RuntimeError("Failed to load AutoImageProcessor; set MODEL_BASE_PROCESSOR.")

    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    model.to(device).eval()

    return {"processor": processor, "model": model, "device": device, "id2label": model.config.id2label}


def get_bundle():
    global _BUNDLE
    if _BUNDLE is None:
        _BUNDLE = _load_bundle()
    return _BUNDLE


def predict(image_bytes: bytes) -> Dict[str, List[Dict[str, float]]]:
    bundle = get_bundle()
    processor = bundle["processor"]
    model = bundle["model"]
    device = bundle["device"]
    id2label = bundle["id2label"]

    with Image.open(io.BytesIO(image_bytes)) as img:
        image = img.convert("RGB")

    inputs = processor(images=image, return_tensors="pt")
    inputs = {k: v.to(device) for k, v in inputs.items()}

    with torch.no_grad():
        logits = model(**inputs).logits
        probs = torch.softmax(logits, dim=-1).squeeze(0)

    top_k = min(5, probs.shape[0])
    values, indices = torch.topk(probs, k=top_k)

    predictions = []
    for score, idx in zip(values.tolist(), indices.tolist()):
        label = id2label.get(int(idx), str(idx))
        predictions.append({"label": label, "score": float(score)})

    return {"top1": predictions[:1], "topk": predictions}

