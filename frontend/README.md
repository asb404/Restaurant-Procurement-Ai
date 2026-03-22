# Frontend – Restaurant Procurement AI

## Overview

This frontend is a Streamlit-based UI for Restaurant Procurement AI.
It provides an interactive interface to run and visualize the procurement pipeline end-to-end.
The app presents each stage clearly: menu parsing → pricing → distributors → quotes → recommendation.

## Features

- Input restaurant name, location, and menu URL
- Run the end-to-end pipeline
- View parsed dishes and extracted ingredients
- View ingredient pricing with trend indicators (📈 / 📉)
- View identified distributors and contact details
- View RFP status
- Generate and compare distributor quotes
- View recommended distributor

## How to Run

1. Navigate to the frontend directory.

2. Run the app:

   ```bash
   streamlit run app.py
   ```

3. Open in browser:

   http://localhost:8501

## How It Works

- The UI sends requests to backend APIs:
  - `/process-menu`
  - `/generate-mock-quotes/{rfp_id}`
  - `/compare-quotes/{rfp_id}`

- Uses Streamlit session state to persist:
  - parsed menu
  - pricing
  - distributors
  - RFP status
  - quotes

- Displays results step-by-step using a card-based layout.

## UI Design

- Card-based layout for each pipeline step
- Status indicators (pending, done, error)
- Pricing table with trend indicators
- Scrollable sections for readability

## Notes

- Requires backend running on `http://127.0.0.1:8000`
- UI updates dynamically after each step
- Uses lightweight styling for a clean dashboard experience
