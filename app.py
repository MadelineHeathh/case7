from flask import Flask, jsonify, request, render_template
from azure.storage.blob import BlobServiceClient, ContentSettings
# Load environment variables from .env
from dotenv import load_dotenv
import os
load_dotenv()

app = Flask(__name__)

AZURE_STORAGE_CONNECTION_STRING = os.getenv("AZURE_STORAGE_CONNECTION_STRING")
IMAGES_CONTAINER = "images-demo"
bsc = BlobServiceClient.from_connection_string(AZURE_STORAGE_CONNECTION_STRING)

@app.route('/api/v1/health', methods=['GET'])
def health():
	"""Simple health endpoint returning HTTP 200 and a small JSON payload."""
	return jsonify(status='ok'), 200

@app.route('/api/v1/gallery', methods=['GET'])
def gallery():
    """Endpoint to retrieve list of uploaded images."""
    container_client = bsc.get_container_client(IMAGES_CONTAINER)
    blob_list = container_client.list_blobs()
    image_urls = [f"https://{bsc.account_name}.blob.core.windows.net/{IMAGES_CONTAINER}/{blob.name}" for blob in blob_list]
    print(image_urls)
    return jsonify(ok=True,gallery=image_urls), 200

@app.route('/api/v1/upload', methods=['POST'])
def upload():
    f = request.files["file"]
    filename = f.filename
    print(filename)
    try:
    
        img_bc = bsc.get_blob_client(IMAGES_CONTAINER, filename)
        img_bc.upload_blob(f, overwrite=True, content_settings=ContentSettings(content_type="image/jpeg"))
        image_url = f"https://{bsc.account_name}.blob.core.windows.net/{IMAGES_CONTAINER}/{filename}"
    except Exception as e:
        return jsonify(ok=False, error=str(e)), 500
    """Endpoint to handle file uploads."""
    # Implementation for file upload goes here
    return jsonify(ok=True, url=image_url), 200

@app.get("/")
def index():
    return render_template("index.html")

if __name__ == '__main__':
	# Run the app on localhost:5000 so it's easy to test locally.
	app.run(host='127.0.0.1', port=5000)
