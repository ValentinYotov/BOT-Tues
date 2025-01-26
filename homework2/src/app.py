import os
import boto3
import jwt
from flask import Flask, request, jsonify, send_file
from io import BytesIO

app = Flask(__name__)

MINIO_ENDPOINT = os.getenv("MINIO_ENDPOINT", "http://localhost:9000")
MINIO_ACCESS_KEY = os.getenv("MINIO_ACCESS_KEY", "minioadmin")
MINIO_SECRET_KEY = os.getenv("MINIO_SECRET_KEY", "minioadmin")
BUCKET_NAME = os.getenv("BUCKET_NAME", "files")

KEYCLOAK_PUBLIC_KEY = """-----BEGIN PUBLIC KEY-----KpEDKVda3-_rwCDoIyR6wrQseyMdgKgDt0o752ewhmw-----END PUBLIC KEY-----"""

s3_client = boto3.client(
    "s3",
    endpoint_url=MINIO_ENDPOINT,
    aws_access_key_id=MINIO_ACCESS_KEY,
    aws_secret_access_key=MINIO_SECRET_KEY,
)

def verify_jwt(token):
    try:
        decoded = jwt.decode(token, KEYCLOAK_PUBLIC_KEY, algorithms=["RS256"])
        return decoded
    except Exception as e:
        return None

@app.route("/upload", methods=["POST"])
def upload_file():
    token = request.headers.get("Authorization", "").replace("Bearer ", "")
    if not verify_jwt(token):
        return jsonify({"error": "Unauthorized"}), 401

    file = request.files.get("file")
    if not file:
        return jsonify({"error": "No file provided"}), 400

    s3_client.upload_fileobj(file, BUCKET_NAME, file.filename)
    return jsonify({"message": "File uploaded successfully", "file": file.filename}), 200

@app.route("/download/<file_id>", methods=["GET"])
def download_file(file_id):
    token = request.headers.get("Authorization", "").replace("Bearer ", "")
    if not verify_jwt(token):
        return jsonify({"error": "Unauthorized"}), 401

    try:
        file_obj = s3_client.get_object(Bucket=BUCKET_NAME, Key=file_id)
        return send_file(
            BytesIO(file_obj["Body"].read()),
            mimetype=file_obj["ContentType"],
            as_attachment=True,
            download_name=file_id,
        )
    except Exception as e:
        return jsonify({"error": str(e)}), 404

@app.route("/update/<file_id>", methods=["PUT"])
def update_file(file_id):
    token = request.headers.get("Authorization", "").replace("Bearer ", "")
    if not verify_jwt(token):
        return jsonify({"error": "Unauthorized"}), 401

    file = request.files.get("file")
    if not file:
        return jsonify({"error": "No file provided"}), 400

    s3_client.delete_object(Bucket=BUCKET_NAME, Key=file_id)
    s3_client.upload_fileobj(file, BUCKET_NAME, file_id)
    return jsonify({"message": "File updated successfully", "file": file_id}), 200

@app.route("/delete/<file_id>", methods=["DELETE"])
def delete_file(file_id):
    token = request.headers.get("Authorization", "").replace("Bearer ", "")
    if not verify_jwt(token):
        return jsonify({"error": "Unauthorized"}), 401

    try:
        s3_client.delete_object(Bucket=BUCKET_NAME, Key=file_id)
        return jsonify({"message": "File deleted successfully", "file": file_id}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 404

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)