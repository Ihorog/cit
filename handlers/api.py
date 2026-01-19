import json
from core.openai_client import chat
from core.job_manager import get_job_manager

job_manager = get_job_manager()

def register_api_routes(router):
    @router.route("/api/chat")
    def handle_chat(h):
        from utils.json_helpers import read_json, send_json
        data = read_json(h)
        msg = data.get("message", "")
        if not msg:
            h.send_response(400)
            h.end_headers()
            return
        
        result = chat(msg)
        h.send_response(200)
        h.send_header("Content-Type", "application/json")
        h.end_headers()
        h.wfile.write(json.dumps(result).encode())

    @router.route("/v1/jobs/list")
    def handle_jobs_list(h):
        jobs = job_manager.list_jobs()
        h.send_response(200)
        h.send_header("Content-Type", "application/json")
        h.end_headers()
        h.wfile.write(json.dumps({"jobs": jobs}).encode())
