import re
import requests

README_KEYWORDS = ["project", "tech stack", "how to run"]

def validate_github_repo(url):
    if not url.startswith("https://github.com/"):
        return False, "❌ Invalid GitHub URL."
    match = re.match(r"https://github.com/([\w\-]+)/([\w\-]+)", url)
    if not match:
        return False, "❌ GitHub URL format is incorrect."
    owner, repo = match.groups()
    api_base = f"https://api.github.com/repos/{owner}/{repo}"
    try:
        r = requests.get(f"{api_base}/readme", headers={'Accept': 'application/vnd.github.v3.raw'})
        if r.status_code != 200 or len(r.text.strip()) < 30:
            return False, "❌ README.md too short or missing."
        if not any(k in r.text.lower() for k in README_KEYWORDS):
            return False, "❌ README.md lacks required content."
        return True, "✅ Repo valid and meets content standards."
    except Exception as e:
        return False, f"❌ GitHub validation failed: {str(e)}"
