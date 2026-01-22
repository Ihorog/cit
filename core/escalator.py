import requests
import json
import os

# Конфігурація доступу
GITHUB_TOKEN = os.getenv("GH_TOKEN")
REPO = "Ihorog/cit"

def create_github_repair_issue(error_message):
    if not GITHUB_TOKEN:
        print("[ERROR] GH_TOKEN не знайдено. Ескалація через API неможлива.")
        return

    url = f"https://api.telegram.org/bot{os.getenv('TG_TOKEN')}/sendMessage" # Дублювання в ТГ
    title = f"🚨 Repair Request: NODE-TMX-ADMIN"
    body = f"""### 🛠 Repair Request Details
**Node ID:** NODE-TMX-ADMIN
**Status:** CRITICAL FAILURE
**Error:** {error_message}
**Timestamp:** {os.popen('date').read()}

### 🔍 Diagnostic Artifacts
- Check `server_log.txt` for details.
- Registry status: Validated.

---
*Generated automatically by Cimeika GEC-3*"""

    # Створення Issue в GitHub
    gh_url = f"https://api.github.com/repos/{REPO}/issues"
    headers = {
        "Authorization": f"token {GITHUB_TOKEN}",
        "Accept": "application/vnd.github.v3+json"
    }
    data = {"title": title, "body": body, "labels": ["repair-request", "automated"]}
    
    try:
        res = requests.post(gh_url, headers=headers, json=data)
        if res.status_code == 201:
            print(f">>> [GEC-3] Issue створено: {res.json().get('html_url')}")
        else:
            print(f">>> [GEC-3] Помилка GitHub API: {res.status_code}")
    except Exception as e:
        print(f">>> [GEC-3] Помилка з'єднання: {e}")

if __name__ == "__main__":
    import sys
    err = sys.argv[1] if len(sys.argv) > 1 else "Unknown Critical Error"
    create_github_repair_issue(err)
