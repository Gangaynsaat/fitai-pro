# FITAI PRO 3D — Made by Souvik Dey

A Streamlit fitness tracker with an interactive Plotly 3D fitness scene and a built-in rule-based coach. No OpenAI API key or paid API billing is required.

## Features
- Dashboard with interactive 3D figure, orbit graphics, and daily metrics
- Workout planner and workout log
- Balanced meal ideas
- Progress tracker and charts
- Hydration tracker
- Built-in coach for general fitness education (works without an API key)
- SQLite local data storage

## Run locally
1. Install Python 3.10 or newer.
2. Open a terminal in this folder.
3. Run `python -m venv .venv`
4. Activate it: Windows PowerShell: `.venv\Scripts\Activate.ps1`; Linux/macOS: `source .venv/bin/activate`
5. Run `pip install -r requirements.txt`
6. Run `streamlit run app.py`

## Deploy on Streamlit Community Cloud
Upload `app.py`, `requirements.txt`, and this README to the root of your GitHub repository, then select `app.py` as the app file. No Secrets are needed for the built-in coach.

## Data note
SQLite data saved on a hosted Streamlit app may not persist across some redeployments/restarts. Keep backups for important records.

Fitness education only, not medical advice. Start comfortably and stop if you experience pain or unusual symptoms.
