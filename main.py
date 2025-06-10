from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import logging
from contextlib import asynccontextmanager

from app.api.endpoints import chatbot, dating
from app.core.config import settings
from app.services.dating_services import DatingService
from app.services.chat_services import ChatService

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Global service instances
dating_service = None
chat_service = None

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    global dating_service, chat_service
    logger.info("Starting up Dating App...")
    
    # Initialize services
    dating_service = DatingService()
    await dating_service.initialize()
    
    chat_service = ChatService()
    await chat_service.initialize()
    
    # Store in app state
    app.state.dating_service = dating_service
    app.state.chat_service = chat_service
    
    logger.info("Dating App started successfully!")
    yield
    
    # Shutdown
    logger.info("Shutting down Dating App...")

# Create FastAPI app
app = FastAPI(
    title="AI Dating App",
    description="Natural Language Dating App with LLM-powered matching",
    version="1.0.0",
    lifespan=lifespan
)

# Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(chatbot.router, prefix="/api/v1/chat", tags=["Chatbot"])
app.include_router(dating.router, prefix="/api/v1/dating", tags=["Dating"])

@app.get("/")
async def root():
    return {"message": "AI Dating App API", "version": "1.0.0"}

@app.get("/health")
async def health_check():
    return {"status": "healthy", "services": ["dating", "chat"]}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )