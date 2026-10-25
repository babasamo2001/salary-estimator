# Import libraries
from fastapi.testclient import TestClient
from app import app

client = TestClient(app)

# Test model prediction
def test_predict_endpoint():
    # Send test data to FastAPI server
    payload = {
        "Education Level": "Bachelor's",
        "Job Title": "Software Engineer",
        "Years of Experience": 4.0
    }

    # Receive server response
    response = client.post("/predict", json=payload)

    assert response.status_code == 200

    # 2. Parse JSON response
    data = response.json()

    # Confirm the prediction key exists in the output
    assert "estimated_salary" in data

    # 4. Confirm predicted value is realistic
    assert isinstance(data["estimated_salary"], (int, float))
    assert data["estimated_salary"] > 0

    # Output the prediction
    print(f"\nPrediction successful! Returned salary: {data['estimated_salary']}")