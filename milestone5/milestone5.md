# Milestone 5

This document covers milestone 5, which is the final cloud deployment of the application.

## Medium Blog Post

### The Problem

### The Solution

### Technical Implementation

NutriSnap is a full-stack application that uses a combination of computer vision and natural language processing to analyze food images and provide nutritional information. The application is built using Python, FastAPI, and Nuxt.js.

The application is deployed on Google Cloud Platform (GCP) using Google Kubernetes Engine (GKE) to host the backend (FastAPI), the frontend (Nuxt.js), and the database (PostgreSQL). The application is containerized using Docker and the container images are stored in Google Container Registry (GCR). The computer vision model to identify food items is deployed separately into a Vertex AI model and is called from the backend using the Vertex AI Python client library.

### Impact
