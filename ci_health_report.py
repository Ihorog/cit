import json, os, datetime

LOG = os.path.expanduser("~/cimeika/cit/logs/watchdog.log")
OUT = os.path.expanduser("~/cimeika/cit/logs/health_report.json")

def main():
    if not os.path.exists(LOG): 
        print("❌ watchdog.log відсутній."); return
    with open(LOG) as f: lines=[json.loads(l) for l in f if l.strip()]
    last_24h = [x for x in lines if (datetime.datetime.now() - datetime.datetime.fromisoformat(x["timestamp"])).total_seconds()<86400]
    ok=sum(1 for x in last_24h if x["status"]=="ok")
    warn=sum(1 for x in last_24h if x["status"]!="ok")
    report={"checked":len(last_24h),"ok":ok,"issues":warn,"uptime":round((ok/(ok+warn))*100,2) if ok+warn>0 else 0}
    with open(OUT,"w") as f: json.dump(report,f,indent=2,ensure_ascii=False)
    print(f"📊 Звіт сформовано: {OUT}")

if __name__=="__main__": main()
