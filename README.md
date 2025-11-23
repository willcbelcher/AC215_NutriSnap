# AC215 - Milestone2 - NutriSnap

**Team Members**
William Belcher, Prakrit Baruah, Vineet Jammalamadaka

**Group Name**
NutriSnap

**Project**
The project aims to simplify the process of food tracking and nutritional analysis by replacing cumbersome manual data entry with a seamless, AI-powered system that accepts multi-modal input like photos and voice.

### Milestone2

In this milestone, we have the components for data management, including versioning, as well as the computer vision and language models.

**Data**
We use the Food 101 dataset from HuggingFace for
- Size and scope: 101,000 RGB food images across 101 classes (≈1,000 per class).
- Standard split: ~75,750 for training and ~25,250 for validation/test (per class: 750 train, 250 val/test).
- Source: Collected from Foodspotting; images vary in resolution and background context.
- Typical use: Benchmark for image classification and transfer learning (often resized to 224×224, normalized with ImageNet stats).
- Evaluation: Commonly reported with top-1 accuracy on the validation/test split.

**Model Finetuning Overview**
## Training setup
- No layers are frozen. We use full fine-tuning.
- TrainingArguments: batch size 64 (train) / 64 (eval), lr=5e-5, epochs = 1 (fast) or 3 (full), weight decay 0.0.
- Mixed precision (fp16) on CUDA; otherwise CPU. MPS detection exists but not enabled.
- No periodic eval/checkpointing configured during training; final eval after training.
- Default LR scheduler (linear, no warmup) implied.
- Experiment with finetuning both `google/vit-base-patch16-224-in21k` and `facebook/deit-tiny-patch16-224` 

## Metrics
- Custom compute_metrics: reports Top-1 and Top-5 accuracy from logits.
- Initializes Weights & Biases run with minimal config.

## Results
See the training loss curve at: `docs/train_loss.png`
Best results are from model `facebook/deit-tiny-patch16-224`
- eval_top_1: 0.613
- eval_top_5: 0.866

where top_*n* means the true label is in the top *n* predictions from the model

**Data Pipeline**

## Versioned Data Pipeline Overview

All processed artifacts are written to Google Cloud Storage so we can track versions by folder name (default `v1`). Authentication relies on Application Default Credentials (ADC), so set `GOOGLE_APPLICATION_CREDENTIALS=/path/to/service-account.json` (or use `gcloud auth application-default login`) before running the scripts.

Environment overrides:
- `GCS_PROJECT` (default `ac215-471519`)
- `GCS_BUCKET` (default `nutrisnap-data`)
- `GCS_DATA_VERSION` (default `v1`)

1. **`src/preprocess/preprocess.py`**  
   Downloads Food-101, builds label maps/metadata, materializes the pixel-value tensors, and saves those processed datasets plus `metadata.json` to `gs://<bucket>/<version>/train|eval`.

2. **`src/train/train.py`**  
   Loads the processed datasets from GCS, configures the Hugging Face `Trainer`, and fine-tunes the ViT model end-to-end.

`src/preprocess/Dockerfile` and `src/train/Dockerfile` build the respective containers; they require ADC credentials to be mounted so the python scripts can reach GCS.

## Running

1. Authenticate for GCS access (choose one):
   ```bash
   export GOOGLE_APPLICATION_CREDENTIALS=/path/to/sa.json
   # or
   gcloud auth application-default login   # persists ADC credentials locally
   ```
2. (Optional) point to a different bucket/version:
   ```bash
   export GCS_BUCKET=nutrisnap-data
   export GCS_DATA_VERSION=v1
   
3. Launch Docker and preprocess:
   ```bash
   docker-compose up -d
   docker exec -it ns-preprocess python preprocess/preprocess.py
   ```
4. Train with the saved versioned data:
   ```bash
   docker exec -it ns-train python train/train.py
   ```

## App Mockup

[Here](https://www.figma.com/proto/Ztdsl6iNBXV3wxQly5oRDY/Tummy?node-id=117-429&t=Cqv92EjHamGnqijE-1) is a link to our Figma mockup of a potential prototype of this application.

## Artifacts

In the `docs` folder we have uploaded screenshots to satisfy the requirements for milestone 2. For objective 1, the virtual environments, the relevant image is `environment.jpeg`. For the containerized pipeline, the `modelrun.jpeg` files show the output of our model running on a small set of data. The full model is being trained in GCP. The pipeline is split into preprocessing and training steps.
