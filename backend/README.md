# Backend – Restaurant Procurement AI

## Overview

The backend implements the end-to-end procurement pipeline for Restaurant Procurement AI.
It handles menu parsing, ingredient extraction, pricing + trend enrichment, distributor discovery,
RFP email generation/sending, quote ingestion, and quote comparison/recommendation.

## How to Setup

1. Create and activate a virtual environment:

   ```bash
   python -m venv venv
   source venv/bin/activate
   ```

   On Windows (PowerShell):

   ```powershell
   python -m venv venv
   .\venv\Scripts\Activate.ps1
   ```

2. Install dependencies:

   ```bash
   pip install -r requirements.txt
   ```

## How to Run

- Start the server:

  ```bash
  uvicorn app.main:app --reload
  ```

- Default URL:

  ```
  http://127.0.0.1:8000
  ```

## Pipeline Flow

- `POST /process-menu`
  - Parses menu input
  - Extracts dishes, ingredients, and quantities
  - Stores normalized data in the database
  - Fetches ingredient pricing and computes trends
  - Finds matching distributors
  - Creates RFP and sends emails

- `POST /generate-mock-quotes/{rfp_id}`
  - Simulates distributor quote responses

- `POST /ingest-quotes/{rfp_id}`
  - Parses and stores quote data

- `GET /compare-quotes/{rfp_id}`
  - Computes distributor totals
  - Recommends the best distributor

## Project Structure

- `app/api/routes` → API endpoints
- `app/services` → Business logic (pricing, email, distributor, input)
- `app/models` → Database models
- `app/db` → Database session and base
- `app/agents` → Parsing + automation logic
- `app/orchestrator` → Pipeline coordination

## Database

- Uses SQLite (`app.db`)
- Stores normalized procurement entities
- Stores ingredient pricing as time-series for trend computation

## Notes

- Pricing simulates USDA data with deterministic variation
- Email flow uses mock/test addresses
- Quote ingestion simulates a real-world procurement workflow
