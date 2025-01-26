FROM python:3.9

WORKDIR /app

COPY . .

RUN pip install --no-cache-dir Flask minio flask-jwt-extended python-keycloak boto3

EXPOSE 5000

CMD ["python", "app.py"]