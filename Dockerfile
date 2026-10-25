#Import libraries
FROM public.ecr.aws/lambda/python:3.10

COPY requirements.txt ${LAMBDA_TASK_ROOT}
RUN pip install --no-cache-dir -r requirements.txt

COPY app.py ${LAMBDA_TASK_ROOT}
COPY models/salary_pipeline.joblib ${LAMBDA_TASK_ROOT}/models/

CMD ["app.handler"]