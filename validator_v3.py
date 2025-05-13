
import re
from datetime import datetime
from flask import Flask, request, jsonify
from werkzeug.utils import secure_filename
import os

app = Flask(__name__)
UPLOAD_FOLDER = "uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

@app.route("/", methods=["GET"])
def home():
    return open("templates/index.html").read()

@app.route("/validate_zip", methods=["POST"])
def validate_zip():
    if "zip_file" not in request.files:
        return jsonify({"error": "No file part"}), 400

    file = request.files["zip_file"]
    filename = secure_filename(file.filename)

    # Validate format
    pattern = r"^TVH_[A-Za-z]+(?:_[A-Za-z]+)*_[A-Za-z0-9]+\.zip$"
    if not re.match(pattern, filename):
        return jsonify({
            "error": "Invalid filename format. Use TVH_FullName_EmailPrefix.zip (e.g., TVH_Akash_Verma_akash123.zip)"
        }), 400

    # Append timestamp for uniqueness
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    base_name = filename[:-4]
    final_filename = f"{base_name}_{timestamp}.zip"
    save_path = os.path.join(UPLOAD_FOLDER, final_filename)

    file.save(save_path)
    return jsonify({"message": f"✅ File received and saved as {final_filename}"}), 200

if __name__ == "__main__":
    app.run(debug=True)
