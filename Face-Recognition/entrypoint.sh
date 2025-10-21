#!/bin/bash

# Run database seeding (creates tables and populates with sample data)
python seed_data.py

# Start the FastAPI application
uvicorn main:app --host 0.0.0.0 --port 8000

