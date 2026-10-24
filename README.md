# FITAI PRO 3D — Made by Souvik Dey

A Streamlit fitness dashboard with workout logging, balanced meal ideas, progress and hydration tracking, a no-API rule-based coach, and an interactive animated 3D trainer motion lab.

## Run locally

```bash
python -m venv .venv
# Windows: .venv\Scripts\activate
# Linux/macOS: source .venv/bin/activate
pip install -r requirements.txt
streamlit run app.py
```

## 3D Trainer Studio
Choose Chest, Back, Shoulders, Biceps, Triceps, Legs/Quads, Glutes, Core/Abs, Calves, or Full body. The articulated mannequin is a simplified educational motion preview with Play/Pause and a phase slider. It is not a recorded workout video, medical anatomy model, or substitute for professional technique guidance.

## Notes
- The built-in fitness coach does not require an OpenAI API key.
- SQLite stores activity on the app's local filesystem. On hosted platforms, local files may not be persistent across rebuilds/redeployments.
- This app provides general fitness education, not medical advice.
