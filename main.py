#!/usr/bin/env python3
import sys
import signal
from pathlib import Path
from http.server import HTTPServer, BaseHTTPRequestHandler

# Додаємо поточну директорію до шляхів пошуку модулів
BASE_DIR = Path(__file__).parent.resolve()
sys.path.insert(0, str(BASE_DIR))

try:
    from core.router import get_router
    from core.logger import get_logger
    from core.config import get_config
    from core.database import init_db
    from handlers import register_sys_routes, register_io_routes, register_api_routes
except ImportError as e:
    print(f"❌ Помилка імпорту: {e}")
    print("Переконайтеся, що ви знаходитесь у директорії ~/cimeika/cit")
    sys.exit(1)

# Ініціалізація компонентів
config = get_config()
logger = get_logger("cit-server")
init_db()  # Створює таблиці SQLite
router = get_router()

# Реєстрація маршрутів
from handlers import register_all
register_all(router)

class CITHandler(BaseHTTPRequestHandler):
    def log_message(self, format, *args):
        logger.info(f"{self.address_string()} - {args[0]}")

    def do_OPTIONS(self):
        self.send_response(204)
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET,POST,OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        self.end_headers()

    def do_GET(self):
        router.dispatch(self, method="GET")

    def do_POST(self):
        router.dispatch(self, method="POST")

def run():
    host = config.get("server.host", "0.0.0.0")
    port = int(config.get("server.port", 8792))
    
    server = HTTPServer((host, port), CITHandler)
    server.allow_reuse_address = True
    
    def signal_handler(sig, frame):
        print("\n🛑 Зупинка сервера...")
        server.server_close()
        sys.exit(0)
        
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    print(f"🚀 CIT v2.2 запущено на http://{host}:{port}")
    server.serve_forever()

if __name__ == "__main__":
    run()
