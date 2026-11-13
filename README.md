# 🚀 Serverless Salary Estimator App

A production-ready, zero-cost serverless machine learning application that predicts candidate salaries based on professional demographics and experience. Built with a decoupled architecture featuring a **React.js** frontend and a containerized **FastAPI** backend deployed on **AWS Lambda** and **API Gateway**.

---

## 🏗️ Architecture & Cost Strategy

* **Frontend:** Static React.js application communicating via REST API.
* **Backend:** FastAPI running inside an AWS Lambda container via the `Mangum` adapter.
* **ML Core:** Scikit-learn pipeline serialized with `joblib`, featuring automated data hygiene and a `RandomForestRegressor`.
* **Cost Optimization:** Leverages permanent lifetime free tiers (**AWS Lambda:** 1M requests/mo + 3.2M compute seconds; **API Gateway:** 1M calls/mo) for $0/month maintenance.

---

## 📁 Project Structure

```text
salary-estimator-app/
├── salary_data.csv
│   
├── frontend/
│   ├── public/
│   │   └── index.html
│   ├── src/
│   │   ├── pages/
│   │   │   └── Home.js
│   │   ├── App.css
│   │   └── index.js
│   └── package.json
├── models/
│   └── salary_pipeline.joblib
├── notebooks/
│   └── training.ipynb
├── src/
│   ├── __init__.py
│   └── pipeline.py
├── tests/
│   └── test_app.py
├── app.py
├── Dockerfile
├── requirements.txt
└── README.md

📊 Data Schema & Modeling Approach
The model trains on structured tabular data containing the following features:

Age (Numeric)

Gender (Categorical)

Education (Categorical)

Job Title (Categorical / Ordinal)

Years of Experience (Numeric)

Salary (Target Variable)


Encoding Strategy:
Following our architecture rules, categorical and ordinal features (including Job Title and Education) are handled directly via One-Hot Encoding (OneHotEncoder). Because the underlying algorithm is a tree-based ensemble (RandomForestRegressor), the trees naturally evaluate categorical splits and thresholds efficiently without requiring manual ordinal integer mapping.


🛠️ Local Development & Setup
1. Clone & Setup Backend Environment

# Install Python dependencies
pip install -r requirements.txt

# Train and serialize the machine learning pipeline
python src/pipeline.py

# Run unit tests
pytest tests/

2. Run FastAPI Locally
uvicorn app:app --reload --port 8000

3. Run React Frontend Locally
cd frontend
npm install
npm start

The React app will run on http://localhost:3000 and point to your local FastAPI server on port 8000.

🐳 Docker & AWS Lambda Deployment
Build the Docker Image:
docker build -t salary-estimator-api .

Test Container Locally (AWS Lambda Emulation):
docker run -p 9000:8080 salary-estimator-api

Deploy to AWS ECR & Lambda:
Push the container image to Amazon Elastic Container Registry (ECR).

Create an AWS Lambda function using the container image.

Configure an AWS API Gateway (HTTP API) trigger pointing to your Lambda function.

Set your React production environment variable (REACT_APP_API_URL) to your live API Gateway endpoint URL.