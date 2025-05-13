
from flask import Flask, request, jsonify, render_template
from validator_v2 import validate_zip_file
from github_auto_intake import validate_github_repo

app = Flask(__name__)

@app.route('/')
def index():
    return render_template("index.html")

@app.route('/validate_zip', methods=['POST'])
def validate_zip():
    file = request.files.get('file')
    if not file:
        return jsonify({"success": False, "message": "No file uploaded."}), 400
    path = f"temp_uploads/{file.filename}"
    file.save(path)
    is_valid, msg = validate_zip_file(path)
    return jsonify({"success": is_valid, "message": msg})

@app.route('/validate_github', methods=['POST'])
def validate_github():
    url = request.form.get("url")
    if not url:
        return jsonify({"success": False, "message": "GitHub URL missing."}), 400
    is_valid, msg = validate_github_repo(url)
    return jsonify({"success": is_valid, "message": msg})

if __name__ == "__main__":
    app.run(debug=True)
