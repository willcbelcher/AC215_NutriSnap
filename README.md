# AC215 - Milestone2 - NutriSnap

**Team Members**
William Belcher, Prakrit Baruah, Vineet Jammalamadaka

**Group Name**
NutriSnap

**Project**
The project aims to simplify the process of food tracking and nutritional analysis by replacing cumbersome manual data entry with a seamless, AI-powered system that accepts multi-modal input like photos and voice.

## Milestone2

In this milestone, we have the components for data management, including versioning, as well as the computer vision and language models.

**Data**
We use the Food 101 dataset from HuggingFace for

- Size and scope: 101,000 RGB food images across 101 classes (≈1,000 per class).
- Standard split: ~75,750 for training and ~25,250 for validation/test (per class: 750 train, 250 val/test).
- Source: Collected from Foodspotting; images vary in resolution and background context.
- Typical use: Benchmark for image classification and transfer learning (often resized to 224×224, normalized with ImageNet stats).
- Evaluation: Commonly reported with top-1 accuracy on the validation/test split.

**Model Finetuning Overview**

### Training setup

- No layers are frozen. We use full fine-tuning.
- TrainingArguments: batch size 64 (train) / 64 (eval), lr=5e-5, epochs = 1 (fast) or 3 (full), weight decay 0.0.
- Mixed precision (fp16) on CUDA; otherwise CPU. MPS detection exists but not enabled.
- No periodic eval/checkpointing configured during training; final eval after training.
- Default LR scheduler (linear, no warmup) implied.
- Experiment with finetuning both `google/vit-base-patch16-224-in21k` and `facebook/deit-tiny-patch16-224`

### Metrics

- Custom compute_metrics: reports Top-1 and Top-5 accuracy from logits.
- Initializes Weights & Biases run with minimal config.

### Results

See the training loss curve at: `docs/train_loss.png`
Best results are from model `facebook/deit-tiny-patch16-224`

- eval_top_1: 0.613
- eval_top_5: 0.866

where top\__n_ means the true label is in the top _n_ predictions from the model

**Data Pipeline**

### Versioned Data Pipeline Overview

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

### Running

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

   ```
3. Launch the preprocessing job (builds the image the first time and mounts `./secrets/nutrisnap-sa.json` inside the container):
   ```bash
   docker compose run --rm --profile ml nutrisnap-preprocess
   ```
4. Train with the saved versioned data:
   ```bash
   docker compose run --rm --profile ml nutrisnap-training
   ```

### Model artifact storage

To serve the latest fine-tuned ViT from the app backend:

1. Export the Hugging Face model directory so it contains at least `config.json`, `model.safetensors`, `preprocessor_config.json`, `tokenizer.json`, and `tokenizer_config.json`.
2. Upload the folder to Google Cloud Storage (adjust the path if you keep a different version directory):
   ```bash
   export MODEL_DIR=./food101-vit-model
   export MODEL_VERSION=v1
   gsutil -m rsync -r "${MODEL_DIR}" "gs://nutrisnap-models/${MODEL_VERSION}"
   ```
3. Point the backend to that folder via environment variables:
   ```bash
   export MODEL_GCS_URI="gs://nutrisnap-models/${MODEL_VERSION}"
   # Optional: set when the exported folder lacks tokenizer/preprocessor files
   export MODEL_BASE_PROCESSOR="google/vit-base-patch16-224-in21k"
   # Optional: set when config.json lacks a model_type field
   export MODEL_DEFAULT_MODEL_TYPE="vit"
   export GOOGLE_APPLICATION_CREDENTIALS=$PWD/secrets/nutrisnap-sa.json
   ```
4. When running with Docker Compose (see below), those variables are injected into the backend container so it can download and cache the artifact during startup.

### Docker Compose Profiles

- `app`: Spins up the PostgreSQL database, FastAPI backend, and Nuxt frontend (`docker compose --profile app up -d`).
- `ml`: Builds and runs the data preprocessing and training jobs on demand, persisting shared artifacts via the `shared-data` volume (`docker compose run --rm --profile ml …`).

### App Mockup

[Here](https://www.figma.com/proto/Ztdsl6iNBXV3wxQly5oRDY/Tummy?node-id=117-429&t=Cqv92EjHamGnqijE-1) is a link to our Figma mockup of a potential prototype of this application.

### Artifacts

In the `docs` folder we have uploaded screenshots to satisfy the requirements for milestone 2. For objective 1, the virtual environments, the relevant image is `environment.jpeg`. For the containerized pipeline, the `modelrun.jpeg` files show the output of our model running on a small set of data. The full model is being trained in GCP. The pipeline is split into preprocessing and training steps.

## Milestone 4

Milestone 4 covers application development prior to cloud deployment.

1. Application Design Document - located in the `docs/` folder.
2. API and Frontend - there are associated frontend and backend folders. The application can be started via commands below.
3. CI and Testing - Automated testing and CI/CD pipeline implemented (see Testing section below).
4. Data versioning and reproducibility: PB to do
5. PB TODO

To run the application, after cloning, simply run:

```bash
docker compose --profile app up -d --build # Starts the frontend, backend, and database in containers
docker compose --profile app exec ns_backend python seed.py # Seeds the database
```

The frontend can then be accessed via http://localhost:3000

## Testing

NutriSnap includes comprehensive automated testing across all components to ensure code quality and reliability.

### Test Coverage

- **Backend**: 60-70% coverage (API endpoints, database models, schemas)
- **ML Pipeline**: 40-50% coverage (GCS utilities, data transforms)
- **Frontend**: 30-40% coverage (component rendering, basic functionality)
- **Overall Target**: 50%+ coverage

### Running Tests Locally

**Backend Tests:**
```bash
cd backend
pip install -r requirements.txt
pytest --cov=. --cov-report=term
```

**ML Pipeline Tests:**
```bash
cd src
pip install -e .
pytest tests/ --cov=. --cov-report=term
```

**Frontend Tests:**
```bash
cd frontend
npm install
npm run test
# Or with coverage:
npm run test:coverage
```

### CI/CD Pipeline

GitHub Actions automatically runs tests on every push and pull request to `main` and `develop` branches.

**Pipeline Jobs:**
- **Backend Tests**: Runs pytest with PostgreSQL service container, generates coverage reports
- **ML Tests**: Tests GCS utilities and data processing functions
- **Frontend Tests**: Runs Vitest component tests with coverage
- **Linting**: Checks Python code with Ruff and TypeScript/Vue with ESLint (errors only, relaxed mode)

**Viewing Results:**
- CI status: Check the Actions tab in the GitHub repository
- Coverage reports: Uploaded to Codecov after each CI run
- Target: All tests must pass before merging

### Test Structure

```
backend/tests/
  conftest.py           # Pytest fixtures (test DB, mocked inference)
  test_main.py          # 10 API endpoint tests
  test_models.py        # 2 database model tests

src/tests/
  test_gcs_utils.py     # 4 GCS utility tests

frontend/tests/
  pages/
    index.spec.ts       # 2 dashboard component tests
```

### Key Testing Features

1. **Mocked Dependencies**: ML inference and GCS operations are mocked for fast, reliable tests
2. **In-Memory Database**: Backend tests use SQLite for speed
3. **Parallel Execution**: CI runs backend, ML, and frontend tests in parallel
4. **Coverage Reporting**: Automated coverage reports uploaded to Codecov
5. **Relaxed Linting**: Only errors block CI, not style warnings

### Testing inference end-to-end

1. Ensure the model artifact is uploaded and the backend has access to credentials (see *Model artifact storage* above).
2. Start the stack with the `app` profile so the backend downloads the model into its container (include `MODEL_BASE_PROCESSOR` when tokenizer files are absent and `MODEL_DEFAULT_MODEL_TYPE` when `config.json` lacks that key):
   ```bash
   MODEL_GCS_URI=gs://nutrisnap-models/v1 \
   MODEL_BASE_PROCESSOR=google/vit-base-patch16-224-in21k \
   MODEL_DEFAULT_MODEL_TYPE=vit \
   docker compose --profile app up -d --build
   ```
3. Send a request to `POST /log/food` with any JPG/PNG file to verify inference:
   ```bash
   curl -X POST http://localhost:8000/log/food \
     -H "Content-Type: multipart/form-data" \
     -F "file=@/path/to/food.jpg"
   ```
   The JSON response should include `identified_foods` populated with the model’s top predictions.
4. To rotate to a new model version, re-upload the folder to a new GCS path, update `MODEL_GCS_URI` (plus `MODEL_BASE_PROCESSOR`/`MODEL_DEFAULT_MODEL_TYPE` when relevant), and restart the backend container:
   ```bash
   export MODEL_GCS_URI=gs://nutrisnap-models/v1
   docker compose --profile app up -d --build backend
   ```
