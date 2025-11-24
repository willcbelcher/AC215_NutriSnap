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

### 3.3. Design Patterns

- **Component-Based Architecture**: Frontend is built using small, reusable Vue components.
- **MVC (Model-View-Controller)**: Backend separates data models (SQLAlchemy), schemas (Pydantic), and controller logic (FastAPI routes).
- **Repository Pattern**: (Implicit) Database access is abstracted via SQLAlchemy sessions passed to route handlers.
- **Containerization**: The entire stack is defined in `docker-compose.yml`, ensuring consistent environments across development and deployment.

## 4. User Interface Design

- **Dashboard**: Provides an at-a-glance view of recent activity, symptom trends (charts), and potential triggers.
- **Log Activity**: A tabbed interface for distinct actions—uploading food photos and logging symptoms—keeping the workflow clean and focused.
- **Responsive**: The UI is designed to work seamlessly on both desktop and mobile devices.
