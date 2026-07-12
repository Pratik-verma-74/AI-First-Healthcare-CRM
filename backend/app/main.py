import logging
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.database import engine, Base, SessionLocal
from app.routers import hcp_router, interaction_router, chat_router, analytics_router
from app.seed_data import seed_initial_data

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("CRM-Backend")

# Initialize FastAPI application
app = FastAPI(
    title="AI-First Healthcare CRM API",
    description="Production-grade FastAPI + LangGraph + Supabase backend for Medical Representatives (HCP Interaction Logging)",
    version="1.0.0"
)

# Configure CORS for React Vite Frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:3000", "*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include Routers (Standard / Local)
app.include_router(chat_router)
app.include_router(interaction_router)
app.include_router(hcp_router)
app.include_router(analytics_router)

# Include Routers with /api prefix (For Vercel Serverless Function Routing)
app.include_router(chat_router, prefix="/api")
app.include_router(interaction_router, prefix="/api")
app.include_router(hcp_router, prefix="/api")
app.include_router(analytics_router, prefix="/api")



@app.on_event("startup")
def startup_event():
    logger.info("Initializing database schema if not present...")
    try:
        Base.metadata.create_all(bind=engine)
        logger.info("Database schema check completed successfully.")
        db = SessionLocal()
        try:
            seed_initial_data(db)
            logger.info("Database seeding check completed successfully.")
        finally:
            db.close()
    except Exception as e:
        logger.error(f"Error during database initialization or seeding check: {e}")


@app.get("/", tags=["Health Check"])
def root():
    return {
        "service": "AI-First Healthcare CRM API",
        "status": "ONLINE",
        "version": "1.0.0",
        "endpoints": [
            "POST /chat",
            "POST /interaction",
            "PUT /interaction/{id}",
            "DELETE /interaction/{id}",
            "GET /interaction",
            "GET /interaction/{id}",
            "GET /hcp",
            "GET /hcp/{id}",
            "GET /history/{id}"
        ]
    }
