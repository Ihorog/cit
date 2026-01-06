from flask import Flask, request, jsonify
from datetime import datetime
import asyncio
import os
import json

try:
    from orchestrator import TaskOrchestrator, TaskPriority
    from ci_mitca_sense import SensomatykaAnalyzer
    ORCHESTRATOR_AVAILABLE = True
except ImportError:
    ORCHESTRATOR_AVAILABLE = False
    print("⚠️ Orchestrator modules not available, running in basic mode")

app = Flask(__name__)

# Initialize components
orchestrator = TaskOrchestrator() if ORCHESTRATOR_AVAILABLE else None
sensomatyka = SensomatykaAnalyzer() if ORCHESTRATOR_AVAILABLE else None

@app.get("/health")
def health():
    """Health check endpoint with system status"""
    status = {
        "ok": True,
        "persona": "ci",
        "timestamp": datetime.now().isoformat(),
        "orchestrator": ORCHESTRATOR_AVAILABLE,
        "sensomatyka": ORCHESTRATOR_AVAILABLE,
        "version": "1.0.0"
    }

    # Add orchestrator stats if available
    if orchestrator:
        status["tasks_active"] = len([t for t in orchestrator.tasks.values() if t.status == "in_progress"])
        status["tasks_total"] = len(orchestrator.tasks)

    return jsonify(status)

@app.post("/chat")
def chat():
    """Main chat endpoint with orchestrator integration"""
    try:
        data = request.get_json(force=True)
        user_input = data.get("input", "").strip()

        if not user_input:
            return jsonify({"response": "Будь ласка, введіть повідомлення.", "error": "empty_input"})

        # Create orchestrator task if available
        task_id = None
        if orchestrator:
            task_id = orchestrator.create_task(f"Chat response for: {user_input[:50]}...")
            # Analyze with sensomatyka for priority
            if sensomatyka:
                priority_score = sensomatyka.analyze_task_importance(user_input)
                if priority_score > 0.7:
                    orchestrator.tasks[task_id].priority = TaskPriority.HIGH
                elif priority_score > 0.4:
                    orchestrator.tasks[task_id].priority = TaskPriority.MEDIUM

        # Basic response logic (can be enhanced with OpenAI integration)
        response = generate_response(user_input)

        # Mark task as completed
        if task_id and orchestrator:
            orchestrator.tasks[task_id].status = "completed"

        return jsonify({
            "response": response,
            "task_id": task_id,
            "timestamp": datetime.now().isoformat()
        })

    except Exception as e:
        app.logger.exception("Unhandled exception while processing request")
        return jsonify({
            "response": "Вибачте, сталася помилка при обробці вашого запиту.",
            "error_code": "internal_error",
            "timestamp": datetime.now().isoformat()
        }), 500

@app.get("/tasks")
def get_tasks():
    """Get current orchestrator tasks"""
    if not orchestrator:
        return jsonify({"error": "Orchestrator not available"}), 503

    tasks = []
    for task_id, task in orchestrator.tasks.items():
        tasks.append({
            "id": task_id,
            "name": task.name,
            "status": task.status.value,
            "priority": task.priority.value,
            "created_at": task.created_at.isoformat(),
            "log_count": len(task.log)
        })

    return jsonify({"tasks": tasks, "total": len(tasks)})

@app.post("/task/<task_id>/run")
def run_task(task_id):
    """Execute a specific task"""
    if not orchestrator:
        return jsonify({"error": "Orchestrator not available"}), 503

    if task_id not in orchestrator.tasks:
        return jsonify({"error": "Task not found"}), 404

    try:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        loop.run_until_complete(orchestrator.run_task(task_id))
        loop.close()

        return jsonify({"status": "completed", "task_id": task_id})
    except Exception as e:
        return jsonify({"error": str(e), "task_id": task_id}), 500

def generate_response(user_input: str) -> str:
    """Generate response based on input (placeholder for OpenAI integration)"""
    # Basic pattern matching for demo
    input_lower = user_input.lower()

    if "привіт" in input_lower or "hello" in input_lower:
        return "Привіт! Я Ci, ваш помічник у системі Cimeika. Чим можу допомогти?"
    elif "статус" in input_lower or "status" in input_lower:
        return "Система Cimeika працює нормально. Всі модулі активні."
    elif "допомога" in input_lower or "help" in input_lower:
        return "Я можу допомогти з плануванням подій, емоційним аналізом, навчанням та творчістю. Спробуйте запитати про щось конкретне!"
    else:
        return f"Дякую за ваше повідомлення: '{user_input}'. Це базова відповідь - скоро буде інтегровано з OpenAI для кращих відповідей."

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8790))
    print(f"🚀 Starting Ci API server on port {port}")
    print(f"Orchestrator: {'Available' if ORCHESTRATOR_AVAILABLE else 'Not available'}")
    app.run(host="0.0.0.0", port=port, debug=False)
