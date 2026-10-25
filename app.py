# Import libraries
from pathlib import Path
import os

import joblib
import pandas as pd
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
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


# Model receives user data, predicts salary, and return the results to the user UI
@app.post("/predict")
def predict_salary(data: SalaryInput):
    try:
        # Convert user data to DataFrame
        input_df = pd.DataFrame([{
            'Education Level': data.education_level,
            'Job Title': data.job_title,
            'Years of Experience': data.years_of_experience
        }])

        prediction = model.predict(input_df)
        return {"estimated_salary": round(float(prediction[0]), 2)}

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Prediction error: {str(e)}")


# AWS Lambda Entrypoint
handler = Mangum(app)
