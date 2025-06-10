from fastapi import APIRouter, HTTPException, Depends, Request
from typing import List
import logging
from datetime import datetime

from app.api.models.dating_schema import SearchRequest, SearchResponse, UserProfile, MatchResult
from app.services.dating_services import DatingService

logger = logging.getLogger(__name__)
router = APIRouter()

def get_dating_service(request: Request) -> DatingService:
    """Dependency to get dating service"""
    return request.app.state.dating_service

@router.post("/search", response_model=SearchResponse)
async def search_profiles(
    search_request: SearchRequest,
    dating_service: DatingService = Depends(get_dating_service)
):
    """Search for profiles using natural language query"""
    try:
        results = await dating_service.search_profiles(
            query=search_request.query,
            user_id=search_request.user_id,
            top_k=search_request.top_k
        )
        
        return SearchResponse(
            success=True,
            query=search_request.query,
            total_results=len(results),
            results=results,
            timestamp=datetime.now().isoformat()
        )
        
    except Exception as e:
        logger.error(f"Search error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/user/{user_id}", response_model=UserProfile)
async def get_user_profile(
    user_id: str,
    dating_service: DatingService = Depends(get_dating_service)
):
    """Get user profile by ID"""
    try:
        user = await dating_service.get_user_by_id(user_id)
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        
        return UserProfile(**user)
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Get user error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/users", response_model=List[UserProfile])
async def get_all_users(
    dating_service: DatingService = Depends(get_dating_service)
):
    """Get all user profiles"""
    try:
        users = await dating_service.get_all_users()
        return [UserProfile(**user) for user in users]
        
    except Exception as e:
        logger.error(f"Get all users error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/match/{user_id}", response_model=List[MatchResult])
async def get_matches_for_user(
    user_id: str,
    top_k: int = 5,
    dating_service: DatingService = Depends(get_dating_service)
):
    """Get matches for a specific user based on their profile"""
    try:
        user = await dating_service.get_user_by_id(user_id)
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        
        # Create a query based on user's interests and preferences
        interests = ', '.join(user.get('interests', [])[:3])
        relationship_type = user.get('relationship_type', '')
        query = f"Looking for {relationship_type} relationship with someone who likes {interests}"
        
        results = await dating_service.search_profiles(
            query=query,
            user_id=user_id,
            top_k=top_k
        )
        
        return [MatchResult(**result) for result in results]
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Match error: {e}")
        raise HTTPException(status_code=500, detail=str(e))