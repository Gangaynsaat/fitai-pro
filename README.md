# FITAI PRO — Trainer-only upgrade

This package preserves the existing FITAI PRO pages and replaces only the 3D Trainer page with a muscular articulated figure and exercise-specific movement previews. Blue highlights mark the selected muscle group.

## Update
Back up your current `app.py`, then replace it with this package's `app.py`. Keep `requirements.txt` updated. Commit the files to GitHub and wait for Streamlit Community Cloud to redeploy.

The embedded 3D component loads Three.js from jsDelivr, so an internet connection and WebGL are required. The animation is a procedural instructional approximation, not motion-capture-verified biomechanics. For genuinely precise movement, use a professionally rigged anatomical model with reviewed animation clips.
