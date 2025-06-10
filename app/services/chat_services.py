#chat_services.py

from typing import Dict, Any, Optional
import random
import logging
from transformers import AutoTokenizer, AutoModelForCausalLM
import torch
import asyncio

from app.core.config import settings

logger = logging.getLogger(__name__)

class ChatService:
    """Service for chat and conversation features"""
    
    def __init__(self):
        self.tokenizer = None
        self.model = None
        self.conversation_starters = [
            "What's the most interesting place you've traveled to recently?",
            "I noticed you're into {interest} - what got you started with that?",
            "Your photos suggest you love {activity} - any favorite spots?",
            "What's been the highlight of your week so far?",
            "I see you work in {profession} - how are you finding it?",
            "What's your go-to comfort food when you need a pick-me-up?",
            "Any book/movie/show recommendations lately?",
            "What's something you're really passionate about right now?"
        ]
    
    async def initialize(self):
        """Initialize chat service with LLM"""
        try:
            loop = asyncio.get_event_loop()
            
            # Load tokenizer and model
            self.tokenizer = await loop.run_in_executor(
                None, 
                AutoTokenizer.from_pretrained, 
                settings.llm_model_name
            )
            
            self.model = await loop.run_in_executor(
                None, 
                AutoModelForCausalLM.from_pretrained, 
                settings.llm_model_name
            )
            
            # Add padding token if not present
            if self.tokenizer.pad_token is None:
                self.tokenizer.pad_token = self.tokenizer.eos_token
            
            logger.info(f"Chat service initialized with {settings.llm_model_name}")
            
        except Exception as e:
            logger.error(f"Failed to initialize chat service: {e}")
            self.tokenizer = None
            self.model = None
    
    async def generate_conversation_starter(self, user_profile: Dict[str, Any]) -> str:
        """Generate a personalized conversation starter"""
        try:
            # Get user info
            interests = user_profile.get('interests', [])
            profession = user_profile.get('profession', '')
            name = user_profile.get('name', '')
            
            # Select random starter template
            starter_template = random.choice(self.conversation_starters)
            
            # Personalize based on profile
            if '{interest}' in starter_template and interests:
                starter = starter_template.format(interest=random.choice(interests))
            elif '{profession}' in starter_template and profession:
                starter = starter_template.format(profession=profession.lower())
            elif '{activity}' in starter_template and interests:
                activity = random.choice([i for i in interests if len(i) > 3])
                starter = starter_template.format(activity=activity)
            else:
                starter = starter_template
            
            return f"Hey {name}! {starter}"
            
        except Exception as e:
            logger.error(f"Error generating conversation starter: {e}")
            return "Hey! How's your day going?"
    
    async def generate_response(self, message: str, context: Optional[str] = None) -> str:
        """Generate a response using the LLM"""
        if not self.model or not self.tokenizer:
            return "I'm still learning how to chat better. Try asking me for a conversation starter instead!"
        
        try:
            # Prepare input
            input_text = f"Context: {context}\nMessage: {message}\nResponse:" if context else f"Message: {message}\nResponse:"
            
            # Tokenize
            inputs = self.tokenizer.encode(input_text, return_tensors='pt', max_length=512, truncation=True)
            
            # Generate response
            loop = asyncio.get_event_loop()
            with torch.no_grad():
                outputs = await loop.run_in_executor(
                    None,
                    lambda: self.model.generate(
                        inputs,
                        max_length=inputs.shape[1] + 50,
                        num_return_sequences=1,
                        temperature=0.7,
                        do_sample=True,
                        pad_token_id=self.tokenizer.eos_token_id
                    )
                )
            
            # Decode response
            response = self.tokenizer.decode(outputs[0], skip_special_tokens=True)
            
            # Extract just the response part
            if "Response:" in response:
                response = response.split("Response:")[-1].strip()
            
            return response[:200]  # Limit response length
            
        except Exception as e:
            logger.error(f"Error generating response: {e}")
            return "That's interesting! Tell me more about that."
