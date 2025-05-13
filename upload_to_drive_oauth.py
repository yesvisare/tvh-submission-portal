
import os
import pickle
import gspread
from flask import Flask, request, jsonify, render_template
from werkzeug.utils import secure_filename
from datetime import datetime
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request

# Flask setup
app = Flask(__name__)
UPLOAD_FOLDER = "uploads"
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER
ALLOWED_EXTENSIONS = {"zip"}

# Define scopes for Google APIs
SCOPES = ["https://www.googleapis.com/auth/drive", "https://www.googleapis.com/auth/spreadsheets"]

# Step 1: Get credentials using OAuth
def get_oauth_credentials():
    creds = None
    if os.path.exists("token.pickle"):
        with open("token.pickle", "rb") as token:
            creds = pickle.load(token)
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file("client_secret.json", SCOPES)
            creds = flow.run_local_server(port=0)
        with open("token.pickle", "wb") as token:
            pickle.dump(creds, token)
    return creds

# Step 2: Append row to Google Sheet
def append_submission_to_sheet(creds, name, email, file_name, github_link, upload_type, file_id):
    sheets_client = gspread.authorize(creds)
    sheet = sheets_client.open("TVH Project Submissions").sheet1
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    email_prefix = email.split("@")[0]
    file_link = f"https://drive.google.com/file/d/{file_id}/view"
    row_link = f'=HYPERLINK("{file_link}", "Open File")'
    row_data = [timestamp, name, email_prefix, file_name, github_link, upload_type, file_id, row_link]
    sheet.append_row(row_data)

# Step 3: Upload route
@app.route("/", methods=["GET", "POST"])
def upload_file():
    if request.method == "POST":
        creds = get_oauth_credentials()
        name = request.form.get("name")
        email = request.form.get("email")
        github_link = request.form.get("github_link")
        upload_type = "ZIP"

        if "file" not in request.files:
            return jsonify(success=False, message="No file part in the request.")
        file = request.files["file"]
        if file.filename == "":
            return jsonify(success=False, message="No selected file.")
        if file and file.filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS:
            filename = secure_filename(file.filename)
            local_path = os.path.join(app.config["UPLOAD_FOLDER"], filename)
            file.save(local_path)

            # Upload to Drive
            drive_service = build("drive", "v3", credentials=creds)
            file_metadata = {"name": filename, "parents": ["<YOUR_FOLDER_ID>"]}
            media = MediaFileUpload(local_path, resumable=True)
            uploaded_file = drive_service.files().create(body=file_metadata, media_body=media, fields="id").execute()
            file_id = uploaded_file.get("id")

            # Log to Google Sheets
            append_submission_to_sheet(creds, name, email, filename, github_link, upload_type, file_id)
            return jsonify(success=True, message="Upload and log successful.")
        else:
            return jsonify(success=False, message="Invalid file type. Please upload a ZIP.")
    return render_template("upload.html")
