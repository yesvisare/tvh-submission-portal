
import os
import gspread
from flask import Flask, request, jsonify, render_template
from werkzeug.utils import secure_filename
from datetime import datetime
from google.oauth2.service_account import Credentials
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload

app = Flask(__name__)
UPLOAD_FOLDER = "uploads"
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER
ALLOWED_EXTENSIONS = {"zip"}

# Load Google credentials
SCOPES = ["https://www.googleapis.com/auth/drive", "https://www.googleapis.com/auth/spreadsheets"]
creds = Credentials.from_service_account_file("tvh-oauth.json", scopes=SCOPES)

# Initialize Drive and Sheets clients
drive_service = build("drive", "v3", credentials=creds)
sheets_client = gspread.authorize(creds)

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def append_submission_to_sheet(name, email, file_name, github_link, upload_type, file_id):
    sheet = sheets_client.open("TVH Project Submissions").sheet1
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    email_prefix = email.split("@")[0]
    file_link = f"https://drive.google.com/file/d/{file_id}/view"
    row_link = f'=HYPERLINK("{file_link}", "Open File")'
    row_data = [timestamp, name, email_prefix, file_name, github_link, upload_type, file_id, row_link]
    sheet.append_row(row_data)

@app.route("/", methods=["GET", "POST"])
def upload_file():
    if request.method == "POST":
        name = request.form.get("name")
        email = request.form.get("email")
        github_link = request.form.get("github_link")
        upload_type = "ZIP"

        if "file" not in request.files:
            return jsonify(success=False, message="No file part in the request.")

        file = request.files["file"]
        if file.filename == "":
            return jsonify(success=False, message="No selected file.")

        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            local_path = os.path.join(app.config["UPLOAD_FOLDER"], filename)
            file.save(local_path)

            # Upload to Google Drive
            file_metadata = {"name": filename, "parents": ["1AbCdEfGh123456789XYZExampleID"]}
            media = MediaFileUpload(local_path, resumable=True)
            uploaded_file = drive_service.files().create(body=file_metadata, media_body=media, fields="id").execute()
            file_id = uploaded_file.get("id")

            # Append to sheet
            append_submission_to_sheet(name, email, filename, github_link, upload_type, file_id)

            return jsonify(success=True, message="File uploaded and logged successfully.")
        else:
            return jsonify(success=False, message="Invalid file type. Please upload a ZIP file.")
    return render_template("upload.html")
