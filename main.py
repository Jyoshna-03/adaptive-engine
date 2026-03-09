from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

from app.database import connect_db, close_db
from app.routes import sessions, questions


@asynccontextmanager
async def lifespan(app: FastAPI):
    await connect_db()
    yield
    await close_db()


app = FastAPI(
    title="AI-Driven Adaptive Diagnostic Engine",
    description="A 1-Dimension Adaptive Testing system using Item Response Theory (IRT).",
    version="1.0.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(sessions.router)
app.include_router(questions.router)


@app.get("/", tags=["Health"])
async def root():
    return {
        "message": "🧠 Adaptive Diagnostic Engine is running!",
        "docs": "/docs",
        "endpoints": {
            "start_session": "POST /session/start",
            "next_question": "GET /session/{id}/next-question",
            "submit_answer": "POST /session/{id}/submit-answer",
            "get_report": "GET /session/{id}/report",
            "session_status": "GET /session/{id}/status",
        },
    }


@app.get("/health", tags=["Health"])
async def health():
    return {"status": "ok"}