import os, json, subprocess, datetime

LOG = os.path.expanduser("~/cimeika/cit/logs/gitcheck.log")
ROOT = os.path.expanduser("~/cimeika/cit")

def log(m):
    with open(LOG,"a") as f: f.write(f"{datetime.datetime.now().isoformat()} | {m}\n")
    print(m)

def main():
    os.chdir(ROOT)
    try:
        out = subprocess.check_output(["git","status"],stderr=subprocess.STDOUT).decode()
        if "nothing to commit" not in out:
            subprocess.run(["git","add","."],check=True)
            subprocess.run(["git","commit","-m","[AUTO] Periodic sync"],check=True)
        subprocess.run(["git","pull","--rebase"],check=True)
        subprocess.run(["git","push"],check=True)
        log("✅ Git репозиторій оновлено успішно.")
    except subprocess.CalledProcessError as e:
        log(f"⚠️ Git sync error: {e.output.decode(errors='ignore')}")

if __name__=="__main__": main()
