"""
KrishiMitra AI - Multi-Crop Leaf Disease Detection

Model: MobileNetV3Large (TensorFlow Lite)
Dataset: PlantVillage
Classes: 38 crop-condition categories

Features:
- Crop identification
- Leaf disease classification
- Confidence score
- Top 3 predictions
- Treatment recommendations
- Healthy leaf identification
"""

import io
import json
import threading
from pathlib import Path

import numpy as np
import tensorflow as tf
from PIL import Image, UnidentifiedImageError


# ================= CONFIGURATION =================

ROOT = Path(__file__).resolve().parent.parent

MODEL_PATH = ROOT / "models" / "disease_model.tflite"
LABELS_PATH = ROOT / "models" / "class_names.json"

CONFIDENCE_THRESHOLD = 0.65

LOCK = threading.Lock()


# ================= LOAD CLASS NAMES =================

with open(LABELS_PATH, "r", encoding="utf-8") as f:
    CLASS_NAMES = json.load(f)

if not isinstance(CLASS_NAMES, list) or not CLASS_NAMES:
    raise ValueError("Invalid class_names.json")

if not all(isinstance(name, str) for name in CLASS_NAMES):
    raise ValueError("Class names must be strings")


# ================= LOAD TFLITE MODEL =================

print("Loading KrishiMitra AI TFLite model...")

interpreter = tf.lite.Interpreter(
    model_path=str(MODEL_PATH)
)

interpreter.allocate_tensors()

INPUT = interpreter.get_input_details()[0]
OUTPUT = interpreter.get_output_details()[0]

print("Model loaded successfully!")
print("Input shape:", INPUT["shape"])
print("Output shape:", OUTPUT["shape"])
print("Total classes:", len(CLASS_NAMES))

if int(OUTPUT["shape"][-1]) != len(CLASS_NAMES):
    raise ValueError(
        "Model output classes do not match class_names.json"
    )


# ================= DISEASE GUIDANCE =================

GUIDANCE = {

    "Early_blight": {
        "organic": "Remove severely affected leaves and improve airflow.",
        "chemical": "Consult a local expert about registered fungicides.",
        "prevention": "Use healthy planting material and avoid overhead irrigation."
    },

    "Late_blight": {
        "organic": "Remove infected plant material and reduce leaf wetness.",
        "chemical": "Seek prompt advice about locally approved fungicides.",
        "prevention": "Improve drainage and monitor plants during humid weather."
    },

    "Bacterial_spot": {
        "organic": "Remove infected debris and avoid handling wet plants.",
        "chemical": "Consult an agricultural expert about approved treatments.",
        "prevention": "Use disease-free seeds and avoid overhead watering."
    },

    "Leaf_Mold": {
        "organic": "Improve ventilation and remove badly affected leaves.",
        "chemical": "Use only locally registered treatments after expert advice.",
        "prevention": "Reduce humidity and improve airflow."
    },

    "Septoria_leaf_spot": {
        "organic": "Remove infected lower leaves and clear plant debris.",
        "chemical": "Consult an expert about approved fungicides.",
        "prevention": "Use crop rotation and avoid splashing water."
    },

    "Spider_mites": {
        "organic": "Inspect leaf undersides and remove severely affected foliage.",
        "chemical": "Seek advice about registered mite-control products.",
        "prevention": "Monitor regularly and protect beneficial insects."
    },

    "Target_Spot": {
        "organic": "Remove infected debris and improve air circulation.",
        "chemical": "Consult an expert about registered disease-control products.",
        "prevention": "Rotate crops and reduce prolonged leaf wetness."
    },

    "Tomato_mosaic_virus": {
        "organic": "Remove infected plants where appropriate and disinfect tools.",
        "chemical": "There is no chemical cure for an infected plant.",
        "prevention": "Use clean tools and disease-free seedlings."
    },

    "Tomato_Yellow_Leaf_Curl_Virus": {
        "organic": "Monitor whiteflies and remove severely infected plants.",
        "chemical": "Consult an expert about approved whitefly management.",
        "prevention": "Use healthy seedlings and resistant varieties."
    },

    "Apple_scab": {
        "organic": "Remove fallen infected leaves and improve airflow.",
        "chemical": "Consult an expert about registered apple-scab fungicides.",
        "prevention": "Maintain orchard hygiene and monitor during wet weather."
    },

    "Black_rot": {
        "organic": "Remove infected plant debris where appropriate.",
        "chemical": "Consult an expert about crop-specific registered treatments.",
        "prevention": "Improve airflow and maintain crop sanitation."
    },

    "Common_rust": {
        "organic": "Remove heavily infected debris where appropriate.",
        "chemical": "Seek advice about registered rust-control products.",
        "prevention": "Use resistant varieties and monitor crops regularly."
    },

    "Powdery_mildew": {
        "organic": "Improve airflow and remove severely affected foliage.",
        "chemical": "Consult an expert about crop-approved fungicides.",
        "prevention": "Avoid overcrowding and monitor plants regularly."
    },

    "Leaf_scorch": {
        "organic": "Remove severely affected leaves when appropriate.",
        "chemical": "Seek crop-specific disease-management advice.",
        "prevention": "Maintain crop hygiene and healthy growing conditions."
    },

    "Cedar_apple_rust": {
        "organic": "Remove infected debris and monitor nearby host plants.",
        "chemical": "Consult an expert about registered rust-control products.",
        "prevention": "Use resistant varieties where available."
    },

    "Northern_Leaf_Blight": {
        "organic": "Remove infected crop debris where appropriate.",
        "chemical": "Consult an expert about approved disease-management products.",
        "prevention": "Rotate crops and use resistant varieties."
    },

    "Esca": {
        "organic": "Remove severely affected plant material under expert guidance.",
        "chemical": "There is no reliable chemical cure for infected grapevines.",
        "prevention": "Maintain vine health and follow recommended pruning practices."
    },

    "Haunglongbing": {
        "organic": "Consult a local citrus specialist and monitor insect vectors.",
        "chemical": "There is no established chemical cure for infected citrus trees.",
        "prevention": "Use certified disease-free planting material."
    },

    "Huanglongbing": {
        "organic": "Consult a local citrus specialist and monitor insect vectors.",
        "chemical": "There is no established chemical cure for infected citrus trees.",
        "prevention": "Use certified disease-free planting material."
    }
}


# ================= DEFAULT GUIDANCE =================

DEFAULT_GUIDANCE = {
    "organic": (
        "Inspect the affected plant and consult "
        "a local agricultural expert."
    ),
    "chemical": (
        "Use only registered crop-specific products "
        "under local expert guidance."
    ),
    "prevention": (
        "Maintain crop hygiene, use healthy planting "
        "material and monitor plants regularly."
    )
}


# ================= GET CLASSES =================

def get_classes():
    return CLASS_NAMES


# ================= IMAGE PREPROCESSING =================

def preprocess_image(image):

    height = int(INPUT["shape"][1])
    width = int(INPUT["shape"][2])

    image = image.convert("RGB")
    image = image.resize((width, height))

    # MobileNetV3 includes preprocessing.
    # Keep pixel values in the 0-255 range.
    array = np.asarray(image, dtype=np.float32)

    array = np.expand_dims(array, axis=0)

    dtype = INPUT["dtype"]

    if np.issubdtype(dtype, np.integer):

        scale, zero_point = INPUT["quantization"]

        if scale <= 0:
            raise ValueError("Invalid input quantization parameters")

        array = np.round(array / scale + zero_point)

        limits = np.iinfo(dtype)

        array = np.clip(
            array,
            limits.min,
            limits.max
        )

    return array.astype(dtype)


# ================= PARSE CLASS NAME =================

def parse_label(label):

    parts = label.split("___", 1)

    crop = parts[0].replace("_", " ").strip()

    if len(parts) > 1:
        disease = parts[1].replace("_", " ").strip()
    else:
        disease = label.replace("_", " ").strip()

    return crop, disease


# ================= GET TREATMENT =================

def get_treatment(label, healthy):

    if healthy:
        return {
            "organic": "No treatment is indicated from this prediction.",
            "chemical": "No chemical treatment is indicated.",
            "prevention": (
                "Continue regular monitoring, proper irrigation "
                "and good crop hygiene."
            )
        }

    for key, advice in GUIDANCE.items():

        if key.lower() in label.lower():
            return advice

    return DEFAULT_GUIDANCE.copy()


# ================= PREDICTION =================

def predict_disease(image_bytes):

    # ---------- Validate image ----------

    try:
        image = Image.open(io.BytesIO(image_bytes))
        image.load()

    except (UnidentifiedImageError, OSError, ValueError):
        raise ValueError(
            "Please upload a valid JPG, PNG or WebP image."
        )

    # ---------- Preprocess ----------

    input_data = preprocess_image(image)

    # ---------- Run TFLite inference ----------

    with LOCK:

        interpreter.set_tensor(
            INPUT["index"],
            input_data
        )

        interpreter.invoke()

        scores = interpreter.get_tensor(
            OUTPUT["index"]
        )[0].astype(np.float32)

    # ---------- Dequantize output ----------

    if np.issubdtype(OUTPUT["dtype"], np.integer):

        scale, zero_point = OUTPUT["quantization"]

        if scale <= 0:
            raise ValueError("Invalid output quantization parameters")

        scores = (scores - zero_point) * scale

    if not np.all(np.isfinite(scores)):
        raise ValueError("Model returned invalid predictions.")

    # ---------- Convert logits if needed ----------

    if (
        np.any(scores < 0)
        or np.any(scores > 1)
        or not np.isclose(scores.sum(), 1, atol=0.02)
    ):

        exp_scores = np.exp(scores - np.max(scores))

        scores = exp_scores / np.sum(exp_scores)

    # ---------- Prediction ----------

    index = int(np.argmax(scores))

    label = CLASS_NAMES[index]

    confidence = float(scores[index])

    crop, disease = parse_label(label)

    healthy = disease.casefold() == "healthy"

    uncertain = confidence < CONFIDENCE_THRESHOLD

    # ---------- Treatment ----------

    advice = get_treatment(label, healthy)

    # ---------- Top 3 predictions ----------

    top_indices = np.argsort(scores)[::-1][:3]

    top_predictions = []

    for i in top_indices:

        top_predictions.append({
            "label": CLASS_NAMES[int(i)],
            "confidence": round(float(scores[i]) * 100, 2)
        })

    # ---------- Response ----------

    return {
        "crop": crop,
        "disease": disease,
        "label": label,
        "confidence": round(confidence * 100, 2),
        "status": "uncertain" if uncertain else "success",
        "healthy": healthy,
        "organic_treatment": advice["organic"],
        "chemical_treatment": advice["chemical"],
        "prevention": advice["prevention"],
        "top_predictions": top_predictions
    }