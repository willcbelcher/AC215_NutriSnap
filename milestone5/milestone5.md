# Milestone 5

This document covers milestone 5, which is the final cloud deployment of the application.

## Medium Blog Post

### The Problem

### The Solution

### Technical Implementation

NutriSnap is a full-stack application that uses a combination of computer vision and natural language processing to analyze food images and provide nutritional information. The application is built using Python, FastAPI, and Nuxt.js.

The application is deployed on Google Cloud Platform (GCP) using Google Kubernetes Engine (GKE) to host the backend (FastAPI), the frontend (Nuxt.js), and the database (PostgreSQL). The application is containerized using Docker and the container images are stored in Google Artifact Registry. The computer vision model to identify food items is deployed separately into a Vertex AI model and is called from the backend using the Vertex AI Python client library.

There are three primary models used in the application. First, the computer vision model, which is trained on over 100,000 food images with over 1.8 Billion parameters. This identifies food images the users upload. Next, the nutrition model, which is a Gemini Pro model that is used to determine potential triggers of the food item. Finally, there is a deterministic model used to determine top triggers for the user based on their symptom and meal history.

The application also utilizes a CI/CD pipeline using GitHub Actions to automate testing and deployment. All components are orchestrated within a Google Kubernetes Engine (GKE) cluster, communicating within a secure VPC to ensure low latency, scalability, and high availability.

### Impact
