# FITAI PRO — Made by Souvik Dey

A Streamlit fitness tracking starter app with:
- Dashboard
- Workout planner and logger
- Balanced meal ideas
- Progress tracking
- Hydration tracking
- Optional OpenAI-powered fitness coach

## Deploy on Streamlit Community Cloud
1. Upload `app.py`, `requirements.txt`, and `README.md` to the root of your GitHub repository.
2. Deploy `app.py` on Streamlit Community Cloud.
3. In app settings, add secrets:
   ```toml
   OPENAI_API_KEY = "your-private-api-key"
   OPENAI_MODEL = "your-available-model-name"
   ```
4. Set `OPENAI_MODEL` to a model available to your OpenAI API account. API billing is separate from a ChatGPT subscription.

Keep API keys private. Never commit keys to GitHub.

## Run locally
```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
streamlit run app.py
```

The app stores its local tracking data in `fitai_pro.db`. On hosted deployments, local storage may not be permanent across all redeployments.
