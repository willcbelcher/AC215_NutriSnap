import base64
import logging
from typing import List

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

# Reuse the core inference logic that downloads the model from GCS and
# performs HF image classification.
from backend import inference as core

logger = logging.getLogger("vertex-app")
logging.basicConfig(level=logging.INFO)


class PredictRequest(BaseModel):
    # List of base64-encoded image bytes.
    instances: List[str]


class Prediction(BaseModel):
    label: str
    score: float


class InstancePrediction(BaseModel):
    top1: List[Prediction]
    topk: List[Prediction]


class PredictResponse(BaseModel):
    predictions: List[InstancePrediction]


app = FastAPI(title="NutriSnap Vertex Inference", version="1.0.0")


@app.on_event("startup")
async def _warm_model():
    """Download and load the model once at startup."""
    try:
        core.get_bundle()
        logger.info("Model bundle loaded successfully.")
    except Exception as exc:
        logger.exception("Failed to load model bundle at startup.")
        raise


@app.get("/health")
async def health():
    return {"status": "ok"}


@app.post("/predict", response_model=PredictResponse)
async def predict(payload: PredictRequest):
    if not payload.instances:
        raise HTTPException(status_code=400, detail="No instances provided")

    predictions: List[InstancePrediction] = []
    for idx, encoded in enumerate(payload.instances):
        try:
            image_bytes = base64.b64decode(encoded, validate=True)
        except Exception:
            raise HTTPException(status_code=400, detail=f"Instance {idx} is not valid base64")

        try:
            result = core.predict(image_bytes)
        except Exception as exc:
            logger.exception("Prediction failed for instance %s", idx)
            raise HTTPException(status_code=500, detail=f"Inference failed for instance {idx}: {exc}") from exc

        predictions.append(InstancePrediction(**result))

    return PredictResponse(predictions=predictions)

