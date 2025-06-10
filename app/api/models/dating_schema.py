from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any

class SearchRequest(BaseModel):
    query: str = Field(..., description="Natural language search query")
    user_id: Optional[str] = Field(None, description="ID of the searching user")
    top_k: Optional[int] = Field(5, description="Number of results to return", ge=1, le=20)

class SearchResponse(BaseModel):
    success: bool
    query: str
    total_results: int
    results: List[Dict[str, Any]]
    timestamp: str

class UserProfile(BaseModel):
    id: str
    name: str
    age: int
    location: str
    interests: List[str]
    profession: str
    education: str
    relationship_type: str
    bio: str
    preferences: Dict[str, Any]

class MatchResult(BaseModel):
    id: str
    name: str
    age: int
    location: str
    profession: str
    interests: List[str]
    bio: str
    relationship_type: str
    similarity_score: float
    match_percentage: int