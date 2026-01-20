import http.server
import json
import os
import urllib.request

API_KEY = os.getenv("OPENAI_API_KEY", "")
MODEL = os.getenv("CIT_MODEL", "gpt-4.1")
PORT = 8791

class Handler(http.server.BaseHTTPRequestHandler):
    def do_OPTIONS(self):
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'POST, GET, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()

    def do_POST(self):
        if self.path == '/chat':
            content_length = int(self.headers.get('Content-Length', 0))
            body = self.rfile.read(content_length)
            try:
                req_data = json.loads(body)
                user_msg = req_data.get('message', '')
                api_req = urllib.request.Request(
                    'https://api.openai.com/v1/chat/completions',
                    headers={
                        'Authorization': f'Bearer {API_KEY}',
                        'Content-Type': 'application/json'
                    },
                    data=json.dumps({
                        'model': MODEL,
                        'messages': [{'role': 'user', 'content': user_msg}],
                        'max_tokens': 1024
                    }).encode()
                )
                reply = ""
                try:
                    with urllib.request.urlopen(api_req, timeout=30) as resp:
                        resp_data = json.loads(resp.read().decode())
                        if resp_data.get('choices'):
                            reply = resp_data['choices'][0]['message']['content']
                except Exception as e:
                    reply = f"Error: {str(e)}"
                
                self.send_response(200)
                self.send_header('Content-Type', 'application/json')
                self.send_header('Access-Control-Allow-Origin', '*')
                self.end_headers()
                self.wfile.write(json.dumps({'reply': reply}).encode())
            except Exception as e:
                self.send_response(500)
                self.send_header('Access-Control-Allow-Origin', '*')
                self.end_headers()

    def log_message(self, format, *args):
        pass

if __name__ == '__main__':
    print(f"CORS Proxy на http://127.0.0.1:{PORT}")
    server = http.server.HTTPServer(('127.0.0.1', PORT), Handler)
    server.serve_forever()
