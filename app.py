import os
import traceback
from pathlib import Path

import joblib
import pandas as pd
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, HTMLResponse
from fastapi.staticfiles import StaticFiles
from mangum import Mangum
from pydantic import BaseModel, Field, field_validator

app = FastAPI(title="Salary Estimator API", version="1.0")

# Enable server access for user http request
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Load the pipeline for prediction
if "LAMBDA_TASK_ROOT" in os.environ:
    PROJECT_ROOT = Path(os.environ["LAMBDA_TASK_ROOT"])
    MODEL_PATH = PROJECT_ROOT / "models" / "salary_pipeline.joblib"
else:
    PROJECT_ROOT = Path(__file__).resolve().parent
    MODEL_PATH = PROJECT_ROOT / "models" / "salary_pipeline.joblib"

try:
    model = joblib.load(MODEL_PATH)
except Exception as e:
    raise RuntimeError(f"Failed to load model from {MODEL_PATH}: {e}")

# Determine frontend build directory path early
FRONTEND_BUILD_DIR = PROJECT_ROOT / "frontend" / "build"


# Extract user data for prediction
class SalaryInput(BaseModel):
    education_level: str = Field(..., alias="Education Level", min_length=1,
                                 description="Education level cannot be empty")
    job_title: str = Field(..., alias="Job Title", min_length=1, description="Job title cannot be empty")
    years_of_experience: float = Field(..., alias="Years of Experience", ge=0.0, le=50.0,
                                       description="Experience must be between 0 and 50 years")

    @field_validator('education_level', 'job_title')
    @classmethod
    def sanitize_strings(cls, v: str) -> str:
        cleaned = v.strip()
        if not cleaned:
            raise ValueError("Field cannot be blank or whitespace only.")
        return cleaned

    class Config:
        populate_by_name = True


# Model receives user data, predicts salary, and sends the results to the frontend UI
@app.post("/predict")
def predict_salary(data: SalaryInput):
    try:
        input_df = pd.DataFrame([{
            'Education Level': data.education_level,
            'Job Title': data.job_title,
            'Years of Experience': data.years_of_experience
        }])

        prediction = model.predict(input_df)
        return {"estimated_salary": round(float(prediction[0]), 2)}

    except Exception as e:
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))


# Debug route to inspect container layout and path existence
@app.get("/debug-paths")
def debug_paths():
    return {
        "lambda_task_root": os.environ.get("LAMBDA_TASK_ROOT"),
        "project_root": str(PROJECT_ROOT),
        "frontend_build_dir": str(FRONTEND_BUILD_DIR),
        "frontend_build_exists": FRONTEND_BUILD_DIR.exists(),
        "cwd_contents": os.listdir(os.getcwd()) if os.path.exists(os.getcwd()) else [],
        "task_root_contents": os.listdir(os.environ.get("LAMBDA_TASK_ROOT", ".")) if "LAMBDA_TASK_ROOT" in os.environ and os.path.exists(os.environ.get("LAMBDA_TASK_ROOT")) else []
    }


# Serve frontend static files if built and included in the container
if FRONTEND_BUILD_DIR.exists():
    if (FRONTEND_BUILD_DIR / "static").exists():
        app.mount("/static", StaticFiles(directory=str(FRONTEND_BUILD_DIR / "static")), name="static")
    if (FRONTEND_BUILD_DIR / "assets").exists():
        app.mount("/assets", StaticFiles(directory=str(FRONTEND_BUILD_DIR / "assets")), name="assets")

    @app.get("/")
    def serve_root():
        index_file = FRONTEND_BUILD_DIR / "index.html"
        if index_file.is_file():
            return FileResponse(str(index_file))
        return {"status": "online", "message": "API is running, but index.html is missing from frontend build."}

else:
    @app.get("/")
    def serve_root_fallback():
        return {"status": "online", "message": "API is running. Frontend build directory not found."}


# AWS Lambda Entrypoint
handler = Mangum(app)