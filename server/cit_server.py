from flask import Flask, jsonify
from flask_cors import CORS
import json
import os

app = Flask(__name__)
CORS(app)

# Шлях для Linux/Termux
DB_PATH = os.path.join("storage", "ci_asset_db.json")

@app.route('/api/state', methods=['GET'])
def get_state():
    try:
        # Шукаємо файл у корені або на рівень вище
        path = DB_PATH if os.path.exists(DB_PATH) else os.path.join("..", DB_PATH)
        with open(path, "r", encoding="utf-8") as f:
            return jsonify(json.load(f))
    except Exception as e:
        return jsonify({"error": str(e), "possibilities": []}), 500

if __name__ == '__main__':
    print("--- [TERMUX CI SERVER] СТАРТ НА ПОРТУ 5000 ---")
    app.run(host='0.0.0.0', port=5000)
