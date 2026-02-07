"""
FastAPI головний додаток для Cimeika

Забезпечує REST API для всіх формацій організму
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse
import os

from api.kazkar_routes import router as kazkar_router

# Створення FastAPI додатку
app = FastAPI(
    title="Cimeika API",
    description="API для організму інтегральної цілісності",
    version="0.1.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # У продакшені обмежити до конкретних доменів
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Підключення роутерів
app.include_router(kazkar_router, prefix="/api/kazkar", tags=["Казкар"])

# Монтування статичних файлів UI
ui_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "ui")
if os.path.exists(ui_path):
    app.mount("/ui", StaticFiles(directory=ui_path), name="ui")


@app.get("/", response_class=HTMLResponse)
async def root():
    """
    Головна сторінка
    """
    return """
    <!DOCTYPE html>
    <html lang="uk">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Cimeika — Організм Цілісності</title>
        <style>
            body {
                font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                background: radial-gradient(circle, #1b0f2e, #0a0816);
                color: #e7c065;
                margin: 0;
                padding: 20px;
                min-height: 100vh;
                display: flex;
                flex-direction: column;
                align-items: center;
                justify-content: center;
            }
            .container {
                max-width: 800px;
                text-align: center;
            }
            h1 {
                font-size: 3rem;
                margin-bottom: 1rem;
                text-shadow: 0 0 20px rgba(231, 192, 101, 0.5);
            }
            .subtitle {
                font-size: 1.2rem;
                opacity: 0.8;
                margin-bottom: 3rem;
            }
            .links {
                display: flex;
                gap: 2rem;
                justify-content: center;
                flex-wrap: wrap;
            }
            .card {
                background: rgba(231, 192, 101, 0.1);
                padding: 2rem;
                border-radius: 15px;
                border: 2px solid rgba(231, 192, 101, 0.3);
                min-width: 200px;
                transition: all 0.3s ease;
                cursor: pointer;
            }
            .card:hover {
                border-color: #e7c065;
                box-shadow: 0 0 30px rgba(231, 192, 101, 0.3);
                transform: translateY(-5px);
            }
            .card-icon {
                font-size: 3rem;
                margin-bottom: 1rem;
            }
            .card-title {
                font-size: 1.5rem;
                margin-bottom: 0.5rem;
            }
            a {
                color: inherit;
                text-decoration: none;
            }
        </style>
    </head>
    <body>
        <div class="container">
            <h1>✨ Cimeika</h1>
            <div class="subtitle">Організм інтегральної цілісності</div>
            
            <div class="links">
                <a href="/ui/kazkar/index.html">
                    <div class="card">
                        <div class="card-icon">📖</div>
                        <div class="card-title">Казкар</div>
                        <div>Форма Оповіді</div>
                    </div>
                </a>
                
                <a href="/docs">
                    <div class="card">
                        <div class="card-icon">📚</div>
                        <div class="card-title">API Docs</div>
                        <div>Документація</div>
                    </div>
                </a>
            </div>
        </div>
    </body>
    </html>
    """


@app.get("/health")
async def health():
    """
    Health check endpoint
    """
    return {
        "status": "healthy",
        "orhanizm": "Cimeika",
        "versiya": "0.1.0"
    }
