from abc import ABC, abstractmethod
from typing import Dict, Any, List
import re
from sentence_transformers import SentenceTransformer
import logging

logger = logging.getLogger(__name__)

class BaseAgent(ABC):
    """Base class for all agents"""
    
    @abstractmethod
    async def process(self, input_data: Any) -> Any:
        pass

class QueryEnhancerAgent(BaseAgent):
    """Agent to enhance natural language queries"""
    
    def __init__(self):
        self.enhancement_patterns = {
            r'\b(doctor|physician|medical)\b': 'doctor physician medical healthcare',
            r'\b(engineer|tech|software)\b': 'engineer technology software programming',
            r'\b(artist|creative|design)\b': 'artist creative designer artistic',
            r'\b(fitness|gym|workout)\b': 'fitness gym workout sports athletic',
            r'\b(travel|adventure)\b': 'travel adventure explore wanderlust',
            r'\b(music|musician)\b': 'music musician singer instrument',
            r'\b(outdoors|nature|hiking)\b': 'outdoors nature hiking camping adventure',
            r'\b(foodie|cooking|chef)\b': 'food cooking culinary restaurant chef',
            r'\b(serious|long.?term)\b': 'serious relationship long-term commitment',
            r'\b(casual|fun|hookup)\b': 'casual dating fun no-strings',
            r'\b(young|twenties)\b': 'young 20s twenties',
            r'\b(professional|career)\b': 'professional career ambitious'
        }
    
    async def process(self, query: str) -> str:
        """Enhance query with related terms"""
        enhanced_query = query.lower()
        
        for pattern, expansion in self.enhancement_patterns.items():
            enhanced_query = re.sub(pattern, expansion, enhanced_query, flags=re.IGNORECASE)
        
        logger.info(f"Enhanced query: '{query}' -> '{enhanced_query}'")
        return enhanced_query

class FilterExtractorAgent(BaseAgent):
    """Agent to extract filters from natural language"""
    
    async def process(self, query: str) -> Dict[str, Any]:
        """Extract structured filters from query"""
        filters = {}
        
        # Age extraction
        age_patterns = [
            r'(\d{2})\s*-\s*(\d{2})\s*years?\s*old',
            r'between\s*(\d{2})\s*and\s*(\d{2})',
            r'age\s*(\d{2})\s*to\s*(\d{2})',
            r'(\d{2})s',  # 20s, 30s, etc.
        ]
        
        for pattern in age_patterns:
            match = re.search(pattern, query, re.IGNORECASE)
            if match:
                if len(match.groups()) == 2:
                    filters['age_min'] = int(match.group(1))
                    filters['age_max'] = int(match.group(2))
                elif 's' in match.group(0):
                    decade = int(match.group(1))
                    filters['age_min'] = decade
                    filters['age_max'] = decade + 9
                break
        
        # Location extraction
        location_match = re.search(r'\b(in|from|near)\s+([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)', query)
        if location_match:
            filters['location'] = location_match.group(2)
        
        # Relationship type
        if re.search(r'\b(serious|long.?term|committed)\b', query, re.IGNORECASE):
            filters['relationship_type'] = 'serious'
        elif re.search(r'\b(casual|fun|hookup|fling)\b', query, re.IGNORECASE):
            filters['relationship_type'] = 'casual'
        
        logger.info(f"Extracted filters: {filters}")
        return filters

class ProfileSummarizerAgent(BaseAgent):
    """Agent to generate profile summaries"""
    
    async def process(self, profile: Dict[str, Any]) -> str:
        """Generate a concise profile summary"""
        bio = profile.get('bio', '')[:100]
        if len(profile.get('bio', '')) > 100:
            bio += '...'
        
        interests = ', '.join(profile.get('interests', [])[:3])
        
        summary = f"{profile.get('name')} ({profile.get('age')}), {profile.get('profession')} in {profile.get('location')}. Interests: {interests}. {bio}"
        
        return summary