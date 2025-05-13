import zipfile
import os

REQUIRED_STRUCTURE = {
    "folders": ["notebooks", "docs", "src"],
    "files": ["README.md"]
}

README_KEYWORDS = ["project", "tech stack", "how to run"]

def validate_zip_file(zip_path):
    try:
        with zipfile.ZipFile(zip_path, 'r') as zip_ref:
            contents = zip_ref.namelist()
            top_items = [item.split('/')[0] for item in contents if '/' in item]
            missing_folders = [f for f in REQUIRED_STRUCTURE["folders"] if f not in top_items]
            missing_files = [f for f in REQUIRED_STRUCTURE["files"] if not any(f in z for z in contents)]
            readme_content = ""
            for file in contents:
                if file.endswith("README.md"):
                    readme_content = zip_ref.read(file).decode("utf-8")
                    break
            if not readme_content or len(readme_content.strip()) < 30:
                return False, "README.md is too short or missing."
            if not any(k in readme_content.lower() for k in README_KEYWORDS):
                return False, "README.md lacks key sections."
            if missing_folders or missing_files:
                return False, f"Missing: {', '.join(missing_folders + missing_files)}"
        if os.path.getsize(zip_path) > 50 * 1024 * 1024:
            return False, "ZIP file exceeds 50MB."
        return True, "✅ ZIP file passed all validations."
    except Exception as e:
        return False, str(e)
