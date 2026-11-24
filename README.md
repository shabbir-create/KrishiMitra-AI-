# KrishiMitra AI — Starter Project

A Hindi-first agricultural assistant MVP with:
- Leaf-image disease screening using a MobileNetV3 transfer-learning model.
- A small, editable disease guidance knowledge base.
- Hindi agricultural Q&A.
- Optional Whisper speech-to-text and Hindi text-to-speech.
- FastAPI backend and Streamlit frontend.

**Safety:** This is an educational prototype, not a validated diagnostic tool. Model outputs can be wrong. Confirm disease diagnosis with a KVK/agriculture officer. No pesticide dose is hard-coded; always follow current locally approved product labels and expert guidance.

## Deploy to Streamlit Community Cloud

Select the branch containing the trained model and use `frontend/cloud_app.py` as the main file. The launcher serves the Streamlit UI and FastAPI together. Cloud installs the inference dependencies from `frontend/requirements.txt`.

Leaf screening and the built-in FAQ work without credentials. To enable open-ended AI answers, add `OPENROUTER_API_KEY` in the app's Streamlit Secrets settings. You can also set `OPENROUTER_MODEL` there.

## Setup (Windows / VS Code)

Use Python 3.10 or 3.11.

```powershell
py -3.10 -m venv .venv
.venv\Scripts\activate
python -m pip install --upgrade pip
pip install -r requirements.txt
copy .env.example .env
```

## Dataset and training

Arrange a licensed image dataset into class folders, for example:

```text
datasets/plant_disease/
├── Tomato___Early_blight/
├── Tomato___Late_blight/
└── Tomato___healthy/
```

Then train:

```powershell
python ml/train_mobilenet.py --data-dir datasets/plant_disease --epochs 10
```

This creates `models/disease_model.keras` and `models/class_names.json`.

PlantVillage is useful for a first experiment but controlled-background images may not generalize to real farms. Create an independent Rajasthan field-image test set. Report per-class precision, recall, F1, confusion matrix and calibration; do not report validation accuracy as real-world accuracy.

## Run the app

Terminal 1:

```powershell
uvicorn backend.main:app --reload
```

Terminal 2:

```powershell
streamlit run frontend/app.py
```

Open the Streamlit URL shown in the terminal. API docs are at `http://127.0.0.1:8000/docs`.

## Optional voice input

```powershell
pip install faster-whisper
```

Set `WHISPER_MODEL=base` in `.env`. The first run downloads model weights. Hindi TTS uses gTTS and requires internet access.

## MySQL (optional for this MVP)

Run `database/schema.sql` in MySQL and set `DATABASE_URL` in `.env`. The starter UI currently does not persist farmer records; the schema is a foundation for a later integration.

## API

- `GET /health`
- `GET /disease/classes`
- `POST /disease/predict` — JPG/PNG/WEBP image
- `POST /assistant/ask` — JSON `{ "question": "...", "language": "hi" }`
- `POST /voice/transcribe` — audio upload

## Next steps

1. Decide the initial crop and disease label list with an agricultural expert.
2. Replace starter advice with reviewed ICAR/KVK/state agriculture material.
3. Collect field images under different lighting, phone cameras and disease stages.
4. Add an explicit uncertain/unknown path and validate confidence calibration.
5. Add user authentication and MySQL persistence only after the core flow is tested.
6. Evaluate Marwari speech recognition separately; do not assume Hindi models understand Marwari well.
