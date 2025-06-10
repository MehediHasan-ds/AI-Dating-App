from fastapi import APIRouter, HTTPException, Depends, Request
import logging
from datetime import datetime

from app.api.models.chatbot_schema import ChatRequest, ChatResponse, ConversationStarterRequest, ConversationStarterResponse
from app.services.chat_services import ChatService
from app.services.dating_services import DatingService

logger = logging.getLogger(__name__)
router = APIRouter()

def get_dating_service(request: Request) -> DatingService:
    """Dependency to get dating service"""
    return request.app.state.dating_service

def get_chat_service(request: Request) -> ChatService:
    """Dependency to get chat service"""
    return request.app.state.chat_service

@router.post("/response", response_model=ChatResponse)
async def generate_chat_response(
    chat_request: ChatRequest,
    chat_service: ChatService = Depends(get_chat_service)
):
    """Generate a chat response using LLM"""
    try:
        response = await chat_service.generate_response(
            message=chat_request.message,
            context=chat_request.context
        )
        
        return ChatResponse(
            response=response,
            timestamp=datetime.now().isoformat()
        )
        
    except Exception as e:
        logger.error(f"Chat response error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/opener", response_model=ConversationStarterResponse)
async def generate_conversation_opener(
    starter_request: ConversationStarterRequest,
    dating_service: DatingService = Depends(get_dating_service),
    chat_service: ChatService = Depends(get_chat_service)
):
    """Generate a personalized conversation starter"""
    try:
        # Get target user profile
        user = await dating_service.get_user_by_id(starter_request.target_user_id)
        if not user:
            raise HTTPException(status_code=404, detail="Target user not found")
        
        # Generate conversation starter
        starter = await chat_service.generate_conversation_starter(user)
        
        return ConversationStarterResponse(
            starter=starter,
            target_user=user.get('name', 'User'),
            timestamp=datetime.now().isoformat()
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Conversation starter error: {e}")
        raise HTTPException(status_code=500, detail=str(e))