import json, os, datetime
LOG = os.path.expanduser("~/cimeika/cit/logs/autosync.log")
data = {
    "timestamp": datetime.datetime.now().isoformat(),
    "status": "ok",
    "message": "CIT AutoSync завершено успішно"
}
with open(LOG, "a") as f:
    f.write(json.dumps(data, ensure_ascii=False) + "\n")
print("📡 AutoSync Report записано:", LOG)
