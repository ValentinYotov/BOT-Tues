from flask import Flask, request, jsonify
import boto3
from jose import jwt
import os

app = Flask(__name__)

# MinIO configuration
MINIO_URL = os.getenv("MINIO_URL")
MINIO_ACCESS_KEY = os.getenv("MINIO_ACCESS_KEY")
MINIO_SECRET_KEY = os.getenv("MINIO_SECRET_KEY")
BUCKET_NAME = "my-bucket"

s3_client = boto3.client(
    "s3",
    endpoint_url=MINIO_URL,
    aws_access_key_id=MINIO_ACCESS_KEY,
    aws_secret_access_key=MINIO_SECRET_KEY,
)

# JWT verification
KEYCLOAK_URL = os.getenv("KEYCLOAK_URL")
REALM = os.getenv("KEYCLOAK_REALM")

def verify_token(token):
    try:
        jwks_url = f"{KEYCLOAK_URL}/realms/{REALM}/protocol/openid-connect/certs"
        jwks = requests.get(jwks_url).json()
        return jwt.decode(token, jwks, algorithms=["RS256"], audience="account")
    except Exception as e:
        return None

@app.before_request
def authenticate():
    token = request.headers.get("Authorization")
    if not token or not verify_token(token.split("Bearer ")[-1]):
        return jsonify({"error": "Unauthorized"}), 401

# Endpoints
@app.route("/upload", methods=["POST"])
def upload_file():
    file = request.files.get("file")
    if not file:
        return jsonify({"error": "No file provided"}), 400
    s3_client.upload_fileobj(file, BUCKET_NAME, file.filename)
    return jsonify({"message": "File uploaded successfully", "file_id": file.filename})

@app.route("/download/<file_id>", methods=["GET"])
def download_file(file_id):
    try:
        file_obj = s3_client.get_object(Bucket=BUCKET_NAME, Key=file_id)
        return file_obj["Body"].read(), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 404

@app.route("/update/<file_id>", methods=["PUT"])
def update_file(file_id):
    file = request.files.get("file")
    if not file:
        return jsonify({"error": "No file provided"}), 400
    s3_client.upload_fileobj(file, BUCKET_NAME, file_id)
    return jsonify({"message": "File updated successfully"})

@app.route("/delete/<file_id>", methods=["DELETE"])
def delete_file(file_id):
    try:
        s3_client.delete_object(Bucket=BUCKET_NAME, Key=file_id)
        return jsonify({"message": "File deleted successfully"})
    except Exception as e:
        return jsonify({"error": str(e)}), 404

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
