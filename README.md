# FITAI PRO — Made by Souvik Dey

A Streamlit fitness-tracking starter app with workout logging, workout templates, balanced meal ideas, progress charts, hydration tracking, and a built-in coaching knowledge base.

## Run locally (Ubuntu/Linux)

```bash
cd fitai-pro
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
streamlit run app.py
```

Open http://localhost:8501.

## Files
- `app.py`: application
- `requirements.txt`: Python dependencies
- `.gitignore`: excludes local database, virtual environment, and secrets

## Notes
- The coach is rule-based and is not connected to a live AI model yet.
- SQLite data is local. A public multi-user deployment needs persistent storage and authentication before real users' data is stored.
- Do not commit passwords, API keys, private tokens, `fitai.db`, or the `venv/` folder.
- Fitness and meal content is general education, not individualized medical advice.

Created by Souvik Dey.
