# FITAI PRO — Muscular 3D Trainer

Made by Souvik Dey.

## Run locally

```bash
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\\Scripts\\activate
pip install -r requirements.txt
streamlit run app.py
```

The trainer uses a procedural stylized muscular figure with selectable muscle-group highlights. Three.js is loaded from jsDelivr at runtime, so an internet connection and WebGL-enabled browser are required for the 3D scene. The model is educational/stylized, not a medical-grade anatomy atlas.

## Streamlit Community Cloud

Set the app entry point to `app.py`, and ensure `requirements.txt` is in the same directory. The 3D model is drawn in an embedded component; no API key is required.
