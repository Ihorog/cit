import os, time, datetime, json, requests, subprocess

ROOT = os.path.expanduser("~/cimeika/cit")
LOG_PATH = f"{ROOT}/logs/autosync.log"
WD_LOG = f"{ROOT}/logs/watchdog.log"
START_SCRIPT = f"{ROOT}/../ci_start.sh"
LIMIT_HOURS = 12
CHAT_WEBHOOK = "http://127.0.0.1:5050/notify"

def send_chat(msg, lvl="info"):
    try:
        requests.post(CHAT_WEBHOOK, json={"source":"watchdog","level":lvl,"text":msg}, timeout=3)
        print(f"💬 CIT Chat: {msg}")
    except Exception as e:
        print(f"⚠️ Chat error: {e}")

def log(msg, st="ok"):
    d = {"timestamp": datetime.datetime.now().isoformat(), "status": st, "message": msg}
    os.makedirs(os.path.dirname(WD_LOG), exist_ok=True)
    with open(WD_LOG,"a") as f: f.write(json.dumps(d, ensure_ascii=False)+"\n")
    print(f"[{st.upper()}] {msg}")

def restart():
    try:
        subprocess.run(["bash", START_SCRIPT], check=True)
        m="♻️ AutoSync перезапущено через збій."
        log(m,"restart"); send_chat(m,"restart")
    except Exception as e:
        log(f"❌ Не вдалося перезапустити: {e}","error")
        send_chat(f"❌ Перезапуск провалився: {e}","error")

def main():
    if not os.path.exists(LOG_PATH):
        m="❌ autosync.log відсутній — система зависла."
        log(m,"error"); send_chat(m,"error"); restart(); return
    diff=(time.time()-os.path.getmtime(LOG_PATH))/3600
    if diff>LIMIT_HOURS:
        m=f"⚠️ AutoSync не оновлювався {int(diff)} годин — виконую перезапуск."
        log(m,"warning"); send_chat(m,"warning"); restart()
    else:
        m="✅ AutoSync стабільно активний."
        log(m,"ok"); send_chat(m,"ok")

if __name__=="__main__": main()
