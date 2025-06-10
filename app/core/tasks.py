from typing import List, Dict, Any, Tuple
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity
import asyncio
import logging

logger = logging.getLogger(__name__)

class EmbeddingTask:
    """Task for generating embeddings"""
    
    def __init__(self, model):
        self.model = model
    
    async def generate_embeddings(self, texts: List[str]) -> np.ndarray:
        """Generate embeddings for a list of texts"""
        loop = asyncio.get_event_loop()
        embeddings = await loop.run_in_executor(None, self.model.encode, texts)
        return embeddings

class FilterTask:
    """Task for filtering users based on criteria"""
    
    @staticmethod
    async def apply_filters(users: List[Dict], filters: Dict[str, Any]) -> List[Dict]:
        """Apply filters to user list"""
        filtered_users = users.copy()
        
        if 'age_min' in filters and 'age_max' in filters:
            filtered_users = [u for u in filtered_users 
                            if filters['age_min'] <= u.get('age', 0) <= filters['age_max']]
        
        if 'location' in filters:
            filtered_users = [u for u in filtered_users 
                            if filters['location'].lower() in u.get('location', '').lower()]
        
        if 'relationship_type' in filters:
            filtered_users = [u for u in filtered_users 
                            if u.get('relationship_type') == filters['relationship_type']]
        
        logger.info(f"Filtered {len(users)} users to {len(filtered_users)} users")
        return filtered_users

class MatchScoringTask:
    """Task for scoring matches"""
    
    @staticmethod
    async def calculate_similarity(query_embedding: np.ndarray, user_embeddings: np.ndarray) -> np.ndarray:
        """Calculate cosine similarity scores"""
        loop = asyncio.get_event_loop()
        similarities = await loop.run_in_executor(
            None, 
            cosine_similarity, 
            query_embedding.reshape(1, -1), 
            user_embeddings
        )
        return similarities[0]
    
    @staticmethod
    async def rank_matches(users: List[Dict], similarities: np.ndarray, top_k: int = 5) -> List[Tuple[Dict, float]]:
        """Rank users by similarity score"""
        scored_users = list(zip(users, similarities))
        scored_users.sort(key=lambda x: x[1], reverse=True)
        return scored_users[:top_k]
