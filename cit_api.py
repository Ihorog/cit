from flask import Flask, request, jsonify
app = Flask(__name__)

@app.get("/health")
def health():
    return jsonify({"ok": True, "persona": "ci"})

@app.post("/chat")
def chat():
    data = request.get_json(force=True)
    user = data.get("input", "")
    reply = f"Привіт! Ти сказав: {user}"
    return jsonify({"response": reply})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8790)
