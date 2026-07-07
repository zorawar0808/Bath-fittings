from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from app.core.config import settings
from app.db.session import engine, Base
from app.api import auth, inventory, customers, jobs, suppliers, alerts, audit, chatbot
import logging

# Configure basic console logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Automate table creation on startup
try:
    Base.metadata.create_all(bind=engine)
    logger.info("Successfully established PostgreSQL connections and verified database schemas.")
except Exception as e:
    logger.error(f"Failed to initialize PostgreSQL tables: {str(e)}")

app = FastAPI(
    title=settings.PROJECT_NAME,
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Set CORS origins for frontend dev server
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # open for development ease, restrict in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register routers under prefix '/api'
app.include_router(auth.router, prefix="/api")
app.include_router(inventory.router, prefix="/api")
app.include_router(customers.router, prefix="/api")
app.include_router(jobs.router, prefix="/api")
app.include_router(suppliers.router, prefix="/api")
app.include_router(alerts.router, prefix="/api")
app.include_router(audit.router, prefix="/api")
app.include_router(chatbot.router, prefix="/api")

@app.exception_handler(Exception)
def global_exception_handler(request: Request, exc: Exception):
    logger.exception(f"Unhandled operational exception occurred: {str(exc)}")
    return JSONResponse(
        status_code=500,
        content={"detail": "An internal server error occurred. Please contact the administrator."}
    )

@app.get("/")
def health_check():
    return {"status": "healthy", "project": settings.PROJECT_NAME, "version": "1.0.0"}
