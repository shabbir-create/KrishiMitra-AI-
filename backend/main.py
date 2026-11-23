"""
KrishiMitra AI - FastAPI Backend

Features:
- Multi-Crop Leaf Disease Detection
- TensorFlow Lite CNN Inference
- Agricultural Assistant
- Treatment Recommendations
"""

from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from backend.assistant import answer_question
from backend.disease_service import predict_disease, get_classes


# ================= FASTAPI APP =================

app = FastAPI(
    title="KrishiMitra AI",
    description="Multi-Crop Leaf Disease Detection and Farmer Assistance",
    version="3.0.0"
)


# ================= CORS =================

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:8501",
        "http://127.0.0.1:8501"
    ],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"]
)


# ================= HOME =================

@app.get("/")
def home():

    return {
        "application": "KrishiMitra AI",
        "message": "Welcome to KrishiMitra AI",
        "model": "MobileNetV3Large",
        "framework": "TensorFlow Lite"
    }


# ================= HEALTH =================

@app.get("/health")
def health():

    return {
        "status": "healthy",
        "model": "MobileNetV3Large",
        "framework": "TensorFlow Lite",
        "total_classes": len(get_classes())
    }


# ================= CLASSES =================

@app.get("/disease/classes")
def classes():

    class_names = get_classes()

    return {
        "total_classes": len(class_names),
        "classes": class_names
    }


# ================= DISEASE PREDICTION =================

@app.post("/disease/predict")
async def detect_disease(file: UploadFile = File(...)):

    allowed_types = [
        "image/jpeg",
        "image/png",
        "image/webp"
    ]

    if file.content_type not in allowed_types:
        raise HTTPException(
            status_code=400,
            detail="Upload a JPG, PNG or WebP image."
        )

    max_size = 10 * 1024 * 1024

    image_bytes = await file.read(max_size + 1)

    if len(image_bytes) > max_size:
        raise HTTPException(
            status_code=413,
            detail="Maximum image size is 10 MB."
        )

    if not image_bytes:
        raise HTTPException(
            status_code=400,
            detail="Uploaded image is empty."
        )

    try:
        return predict_disease(image_bytes)

    except ValueError as exc:
        raise HTTPException(
            status_code=400,
            detail=str(exc)
        )

    except Exception:
        raise HTTPException(
            status_code=500,
            detail="Disease prediction failed."
        )


# ================= AGRICULTURAL ASSISTANT =================

class QuestionRequest(BaseModel):
    question: str
    language: str = "en"


@app.post("/assistant/ask")
def ask_assistant(request: QuestionRequest):

    result = answer_question(
        request.question,
        request.language
    )

    if isinstance(result, dict):
        return {
            **result,
            "language": request.language
        }

    return {
        "answer": str(result),
        "language": request.language
    }


# ================= LOCAL EXECUTION =================

if __name__ == "__main__":

    import uvicorn

    uvicorn.run(
        "backend.main:app",
        host="127.0.0.1",
        port=8000,
        reload=True
    )