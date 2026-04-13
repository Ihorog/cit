from datetime import datetime, timezone
from flask import Flask, jsonify, request
from flask_cors import CORS
import json
import os
import sys
import threading
import logging

# Add parent directory to path to allow imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from server.openai_client import OpenAIClient
from config.logging_config import setup_logging, get_logger
from config.paths import CIT_CORE_REGISTRY, get_registry_path
from utils.json_handler import read_json_file, write_json_file
from utils.time_utils import now_utc_formatted

# Configure logging
setup_logging()
logger = get_logger(__name__)

app = Flask(__name__)
CORS(app)

# Use centralized registry path
REGISTRY_PATH = str(CIT_CORE_REGISTRY)

# Initialize OpenAI client
openai_client = OpenAIClient()

def register_subscriber(ip, user_agent):
    """Register a subscriber with proper error handling."""
    try:
        # Load existing data or create new
        data = read_json_file(REGISTRY_PATH, default={"active_subscribers": {}})
        
        # Ensure active_subscribers key exists
        if not isinstance(data, dict) or 'active_subscribers' not in data:
            data = {"active_subscribers": {}}
        
        # Визначення типу абонента
        client_type = "AI_AGENT" if any(x in user_agent.lower() for x in ["python", "curl", "gpt", "gemini", "ai"]) else "WEB_USER"
        
        data["active_subscribers"][ip] = {
            "last_seen": now_utc_formatted(),
            "client_type": client_type,
            "provisioning_status": "package_optimized"
        }
        
        write_json_file(REGISTRY_PATH, data, indent=4)
        
        return client_type
    except Exception as e:
        logger.error(f"Error in register_subscriber: {e}")
        # Return a default value to not break the endpoint
        return "WEB_USER"

@app.route('/health', methods=['GET'])
def health():
    """Health check endpoint returning service status and configuration."""
    try:
        # Get port from environment or default to 5000
        port = int(os.getenv('CIT_PORT', os.getenv('PORT', 5000)))
        
        # Check if OpenAI API key is available
        openai_available = bool(openai_client.api_key)
        
        response = {
            "ok": True,
            "service": "cit",
            "time": now_utc_formatted(),
            "port": port,
            "model": openai_client.model,
            "openai": openai_available
        }
        
        logger.info(f"Health check: openai={openai_available}, model={openai_client.model}")
        return jsonify(response)
    except Exception as e:
        logger.error(f"Health check error: {str(e)}")
        return jsonify({
            "ok": False,
            "service": "cit",
            "time": now_utc_formatted(),
            "error": "Health check failed"
        }), 500


@app.route('/chat', methods=['POST'])
def chat():
    """Chat endpoint that forwards messages to OpenAI API."""
    try:
        # Get request data with error handling
        data = request.get_json(silent=True)
        
        # Check if data exists
        if data is None:
            logger.warning("Chat request with invalid or no JSON body")
            return jsonify({
                "ok": False,
                "cit": "error",
                "time": datetime.now(timezone.utc).isoformat(),
                "model": openai_client.model,
                "reply": "Request body must be valid JSON"
            }), 400
        
        # Get message field with error handling
        message = data.get('message', '')
        
        # Handle empty or whitespace-only messages with a hint (not an error)
        if not message or not message.strip():
            logger.info("Chat request with empty message, returning hint")
            return jsonify({
                "ok": True,
                "cit": "hint",
                "time": datetime.now(timezone.utc).isoformat(),
                "model": openai_client.model,
                "reply": "Hint: Please provide a message in the 'message' field to chat with the AI assistant."
            })
        
        # Check if OpenAI API key is available
        if not openai_client.api_key:
            logger.warning("Chat request without OpenAI API key")
            return jsonify({
                "ok": True,
                "cit": "fallback",
                "time": datetime.now(timezone.utc).isoformat(),
                "model": openai_client.model,
                "reply": "OpenAI API key not configured. Please set OPENAI_API_KEY or CIT_OPENAI_API_KEY environment variable."
            })
        
        # Call OpenAI API
        logger.info(f"Processing chat message: {message[:50]}...")
        result = openai_client.chat(message)
        
        # Check for errors in the result
        if 'error' in result:
            logger.error(f"OpenAI API error: {result.get('error')}")
            return jsonify({
                "ok": False,
                "cit": "error",
                "time": datetime.now(timezone.utc).isoformat(),
                "model": openai_client.model,
                "reply": f"Error communicating with OpenAI API: {result.get('error')}"
            }), 502
        
        # Return successful response
        response = {
            "ok": True,
            "cit": result.get('api', 'unknown'),
            "time": datetime.now(timezone.utc).isoformat(),
            "model": openai_client.model,
            "reply": result.get('reply', '')
        }
        
        logger.info(f"Chat response sent successfully via {result.get('api')}")
        return jsonify(response)
        
    except Exception as e:
        logger.error(f"Chat endpoint error: {str(e)}", exc_info=True)
        return jsonify({
            "ok": False,
            "cit": "error",
            "time": datetime.now(timezone.utc).isoformat(),
            "model": openai_client.model if openai_client else "unknown",
            "reply": f"Internal server error: {str(e)}"
        }), 500


@app.route('/ci1', methods=['GET'])
def ai_passport():
    ua = request.headers.get('User-Agent', '')
    ip = request.remote_addr
    client_type = register_subscriber(ip, ua)
    
    # Пакетне забезпечення залежно від типу
    package = {
        "system": "Cimeika (CIT)",
        "registry_id": f"NODE-{ip}",
        "client_type": client_type,
        "wiki_context": "https://github.com/Ihorog/ciwiki"
    }
    
    if client_type == "AI_AGENT":
        package.update({
            "ebc_components": ["auth_logic", "registry_sync", "gateway_api"],
            "protocol": "JSON_RAW",
            "instructions": "Use One-Shot execution. See CiWiki/protocols."
        })
    else:
        package.update({
            "ui_access": "https://ihorog.github.io/cit",
            "protocol": "WEB_INTERFACE",
            "instructions": "Welcome to Ci-Gateway. Use the dashboard to monitor nodes."
        })
        
    return jsonify(package)


@app.route('/restart', methods=['POST'])
def restart():
    """Restart the CIT server process via API. Localhost only."""
    try:
        # Дозволити перезапуск лише з локального хоста
        remote = request.remote_addr or ''
        if remote not in ('127.0.0.1', '::1', 'localhost'):
            logger.warning(f"Restart denied for remote addr: {remote}")
            return jsonify({
                "ok": False,
                "service": "cit",
                "time": datetime.now(timezone.utc).isoformat(),
                "action": "restart",
                "error": "Restart allowed from localhost only"
            }), 403

        logger.info("Restart requested via /restart endpoint")

        def _do_restart():
            os.execv(sys.executable, [sys.executable] + sys.argv)

        # Виконати перезапуск після відправки відповіді
        t = threading.Timer(1.0, _do_restart)
        t.daemon = True
        t.start()

        return jsonify({
            "ok": True,
            "service": "cit",
            "time": datetime.now(timezone.utc).isoformat(),
            "action": "restart",
            "message": "Server is restarting..."
        })
    except Exception as e:
        logger.error(f"Restart endpoint error: {str(e)}")
        return jsonify({
            "ok": False,
            "service": "cit",
            "time": datetime.now(timezone.utc).isoformat(),
            "action": "restart",
            "error": str(e)
        }), 500

if __name__ == '__main__':
    port = int(os.environ.get('CIT_PORT', 8791))
    app.run(host='0.0.0.0', port=port)
