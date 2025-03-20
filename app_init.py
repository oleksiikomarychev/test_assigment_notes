import os
import google.generativeai as genai
from dotenv import load_dotenv
from fastapi import FastAPI, APIRouter
from contextlib import contextmanager, asynccontextmanager
from src.database import engine
from src.exception_handlers import setup_exception_handlers
from src.models import Base
from src.routers import crud_router, ai_router


load_dotenv()

def init_db():
    Base.metadata.create_all(bind=engine)

def dispose_db():
    engine.dispose()

@contextmanager
def db_lifespan(app: FastAPI):
    init_db()
    yield
    dispose_db()

def init_gemini():
    gemini_api_key = os.getenv("GEMINI_API_KEY")
    if not gemini_api_key:
        raise ValueError("GEMINI_API_KEY environment variable not set.")
    genai.configure(api_key=gemini_api_key)

@contextmanager
def gemini_lifespan(app: FastAPI):
    init_gemini()
    yield

@asynccontextmanager
async def lifespan(app: FastAPI):
    init_db()
    init_gemini()
    yield
    dispose_db()


def create_app():
    app = FastAPI(
        title="Notes API",
        description="API for managing notes with summarization and analytics.",
        version="0.1.0",
        lifespan=lifespan,
    )

    setup_exception_handlers(app)

    default_routers: list[APIRouter] = [
        crud_router,
        ai_router,
    ]

    for router in default_routers:
        app.include_router(router)

    return app