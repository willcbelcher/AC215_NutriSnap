# Application Design Document: NutriSnap

## 1. Introduction

NutriSnap is an AI-powered food tracking and nutritional analysis application designed to simplify the process of logging meals and identifying potential dietary triggers for symptoms. By leveraging computer vision and natural language processing, NutriSnap reduces the friction of manual data entry, allowing users to focus on their health.

## 2. Solution Architecture

The NutriSnap solution is built as a modern, containerized web application consisting of three main components:

### 2.1. High-Level Components

- **Frontend (Client)**: A responsive web interface where users interact with the application. It handles image uploads, displays dashboards, and manages user input for symptom logging.
- **Backend (API)**: A RESTful API that processes requests, manages business logic, interfaces with the AI models (simulated for prototype), and persists data.
- **Database**: A relational database storing user profiles, meal logs, symptom entries, and nutritional data.
- **AI/ML Computer Vision Service**: A component responsible for analyzing food images to extract ingredients and nutritional content.

### 2.2. Data Flow

1.  **User Action**: User uploads a meal photo via the Frontend.
2.  **Request**: Frontend sends the image to the Backend API.
3.  **Processing**: Backend processes the image to identify foods and calculate macros.
4.  **Persistence**: Backend saves the meal data and analysis results to the Database.
5.  **Response**: Backend returns the analyzed data to the Frontend.
6.  **Visualization**: Frontend updates the Dashboard to show the new meal and updates trend charts.

## 3. Technical Architecture

### 3.1. Technology Stack

- **Frontend**:
  - **Framework**: Vue.js 3 with Nuxt 4 (SSR/SSG capabilities).
  - **Styling**: Tailwind CSS for utility-first, responsive design.
  - **Visualization**: ApexCharts (via `vue3-apexcharts`) for interactive data visualization.
  - **State Management**: Nuxt `useState` and Composables.
- **Backend**:
  - **Framework**: FastAPI (Python) for high-performance, asynchronous API endpoints.
  - **ORM**: SQLAlchemy for database interactions.
  - **Validation**: Pydantic for data validation and serialization.
- **Database**:
  - **System**: PostgreSQL 14.
  - **Driver**: `psycopg2-binary` / `asyncpg`.
- **Infrastructure**:
  - **Containerization**: Docker & Docker Compose for orchestration.

### 3.2. Code Organization

#### Frontend (`/frontend`)

- `pages/`: Application routes (e.g., `index.vue` for Dashboard, `log.vue` for Logging).
- `components/`: Reusable UI components.
- `layouts/`: Page layouts (e.g., `default.vue` with navigation).
- `public/`: Static assets.
- `nuxt.config.ts`: Nuxt configuration.

#### Backend (`/backend`)

- `main.py`: Entry point, API route definitions, and controller logic.
- `models.py`: SQLAlchemy database models (`User`, `Meal`, `Symptom`).
- `schemas.py`: Pydantic schemas for request/response validation.
- `database.py`: Database connection and session management.
- `seed.py`: Script to populate the database with initial demo data.
- `inference.py`: Script to load model from GCP and run inference on pictures of food

### 3.3. Design Patterns

- **Component-Based Architecture**: Frontend is built using small, reusable Vue components.
- **MVC (Model-View-Controller)**: Backend separates data models (SQLAlchemy), schemas (Pydantic), and controller logic (FastAPI routes).
- **Repository Pattern**: (Implicit) Database access is abstracted via SQLAlchemy sessions passed to route handlers.
- **Containerization**: The entire stack is defined in `docker-compose.yml`, ensuring consistent environments across development and deployment.

## 4. User Interface Design

- **Dashboard**: Provides an at-a-glance view of recent activity, symptom trends (charts), and potential triggers.
- **Log Activity**: A tabbed interface for distinct actions—uploading food photos and logging symptoms—keeping the workflow clean and focused.
- **Responsive**: The UI is designed to work seamlessly on both desktop and mobile devices.

## 5. Data Versioning and Reproducibility

- **Approach**: Instead of DVC, NutriSnap stores large artifacts in Google Cloud Storage (GCS) under versioned prefixes (`gs://nutrisnap-data/<version>/...`). This keeps 100GB-scale tensors out of Git, matches our GCP hosting stack, and lets any container pull the exact snapshot it needs.
- **Owned artifacts**:
  - `src/preprocess/preprocess.py` downloads the Food-101 raw data, builds label maps + tensors, then writes them to `train/` and `eval/` folders inside the selected version prefix.
  - `src/train/train.py` consumes the processed tensors directly from the same prefix so that preprocessing and training remain tightly coupled to a version id.
- **Environment switches** (wired into Docker Compose and CI settings): `GCS_PROJECT=ac215-471519`, `GCS_BUCKET=nutrisnap-data`, `GCS_DATA_VERSION=v1`. Changing the version variable is sufficient to branch experiments.
- **Version history**:
  - `v1` – Baseline preprocessing of the full Food-101 dataset (224×224 resize, ImageNet normalization) created on 2024-11-10; corresponding model artifacts live at `gs://nutrisnap-data/models/v1`.
  - `v2` – More pictures and classes included for diversity of training
  - Future experiments must append `v3`, `v4`, etc., and log the rationale plus command history in the milestone notes before promotion.
- **Repro recipe**:
  1. Authenticate to GCP via `gcloud auth application-default login` or set `GOOGLE_APPLICATION_CREDENTIALS=/path/to/sa.json`.
  2. (Optional) override bucket/version: `export GCS_BUCKET=...`, `export GCS_DATA_VERSION=v1`.
  3. Rebuild the processed tensors (idempotent): `docker compose run --rm --profile ml nutrisnap-preprocess`.
  4. Pull an existing snapshot locally when needed: `gsutil -m rsync -r gs://$GCS_BUCKET/$GCS_DATA_VERSION ./data/$GCS_DATA_VERSION`.
  5. Training/inference jobs read from the same versioned prefix, so any prediction can be traced back to the dataset snapshot plus git commit.

## 6. Model Fine-Tuning

- **Code + configs**:
  - `src/train/train.py` wraps Hugging Face `Trainer` with `TrainingArguments` (batch size 64, learning rate 5e-5, 1–3 epochs, fp16 when CUDA available) and a custom `compute_metrics` function emitting Top-1/Top-5 accuracy.
  - `src/train/Dockerfile` plus the `ml` Docker Compose profile install dependencies so `docker compose run --rm --profile ml nutrisnap-training` exactly reproduces the run.
  - Runs are logged to Weights & Biases (`project=nutrisnap`, run name `nutrisnap-food101`) for experiment tracking and loss curves.
- **Dataset reference**: Training always reads from `gs://$GCS_BUCKET/$GCS_DATA_VERSION`, so specifying `GCS_DATA_VERSION=v1` ties the checkpoint to the `v1` snapshot of the processed Food-101 dataset.
- **Latest experiment log**:
  - Backbones tested: `google/vit-base-patch16-224-in21k` and `facebook/deit-tiny-patch16-224`.
  - Best run (DeiT-tiny, 3 epochs) achieved `eval_top_1=0.613` and `eval_top_5=0.866`. Loss curves are saved at `docs/train_loss.png`; full hyperparameters + outputs live in the W&B run linked from the README.
- **Deployment impact**:
  - Exported checkpoints are synced to weights and biases, and then the best model is pulled into `gs://nutrisnap-models/<VERSION>` for inferencing
  - The FastAPI backend loads the artifact on startup using `MODEL_GCS_URI`, `MODEL_BASE_PROCESSOR`, and `MODEL_DEFAULT_MODEL_TYPE`. Rotating to a new fine-tuned model simply swaps the URI and restarts the backend container—no code changes required.
  - Because preprocessing, training, and inference all reference the same versioned prefixes, every prediction served to end users is reproducible given the stored dataset + checkpoint combination.

