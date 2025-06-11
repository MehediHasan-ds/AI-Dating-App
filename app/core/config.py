# config.py

from pydantic_settings import BaseSettings
from typing import Optional
import os
from pathlib import Path

class Settings(BaseSettings):
    # API Configuration
    api_title: str = "AI Dating App"
    api_version: str = "1.0.0"
    debug: bool = False
    
    # Model Configuration
    embedding_model_name: str = "sentence-transformers/all-MiniLM-L6-v2"
    llm_model_name: str = "microsoft/DialoGPT-small"
    
    # Database Configuration
    users_json_path: str = "app/database/users.json"
    
    # API Keys (optional for local models)
    openai_api_key: Optional[str] = None
    huggingface_api_key: Optional[str] = None
    
    # Search Configuration
    default_top_k: int = 5
    similarity_threshold: float = 0.3
    
    # File paths
    base_dir: Path = Path(__file__).parent.parent.parent
    
    class Config:
        env_file = ".env"
        case_sensitive = False

settings = Settings()