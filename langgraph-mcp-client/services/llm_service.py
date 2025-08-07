import os
from typing import Dict, List
from interfaces.llm_interface import ILLMProvider, ILLMService
from models.message import Message
from config.settings import LLMConfig

try:
    from langchain_google_genai import ChatGoogleGenerativeAI
except ImportError:
    ChatGoogleGenerativeAI = None

try:
    from langchain_openai import ChatOpenAI
except ImportError:
    ChatOpenAI = None

class GoogleLLMProvider(ILLMProvider):
    """Google Gemini LLM Provider"""
    
    def __init__(self, config: LLMConfig):
        if ChatGoogleGenerativeAI is None:
            raise ImportError("langchain_google_genai not installed")
            
        self.config = config
        self.llm = ChatGoogleGenerativeAI(
            model=config.model_name,
            google_api_key=os.getenv(config.api_key_env),
            temperature=config.temperature
        )
    
    async def generate_response(self, messages: List[Message]) -> str:
        """Generate response using Google Gemini"""
        # Convert messages to LangChain format
        formatted_messages = [{"role": msg.role, "content": msg.content} for msg in messages]
        response = await self.llm.ainvoke(formatted_messages)
        return response.content if hasattr(response, 'content') else str(response)
    
    def get_model_info(self) -> dict:
        return {
            "provider": "Google",
            "model": self.config.model_name,
            "temperature": self.config.temperature
        }

class OpenAILLMProvider(ILLMProvider):
    """OpenAI LLM Provider"""
    
    def __init__(self, config: LLMConfig):
        if ChatOpenAI is None:
            raise ImportError("langchain_openai not installed")
            
        self.config = config
        self.llm = ChatOpenAI(
            model=config.model_name,
            api_key=os.getenv(config.api_key_env),
            temperature=config.temperature
        )
    
    async def generate_response(self, messages: List[Message]) -> str:
        """Generate response using OpenAI"""
        formatted_messages = [{"role": msg.role, "content": msg.content} for msg in messages]
        response = await self.llm.ainvoke(formatted_messages)
        return response.content if hasattr(response, 'content') else str(response)
    
    def get_model_info(self) -> dict:
        return {
            "provider": "OpenAI",
            "model": self.config.model_name,
            "temperature": self.config.temperature
        }

class LLMService(ILLMService):
    """Service for managing multiple LLM providers"""
    
    def __init__(self):
        self._providers: Dict[str, ILLMProvider] = {}
    
    def register_llm(self, name: str, provider: ILLMProvider):
        """Register a new LLM provider"""
        self._providers[name] = provider
    
    def get_llm(self, name: str) -> ILLMProvider:
        """Get LLM provider by name"""
        if name not in self._providers:
            raise ValueError(f"LLM provider '{name}' not found")
        return self._providers[name]
    
    def list_providers(self) -> List[str]:
        """List all available providers"""
        return list(self._providers.keys())

class LLMServiceFactory:
    """Factory for creating LLM services"""
    
    @staticmethod
    def create_llm_service(llm_configs: List[LLMConfig]) -> LLMService:
        """Create and configure LLM service with providers"""
        service = LLMService()
        
        for config in llm_configs:
            try:
                if config.model_type == "google":
                    provider = GoogleLLMProvider(config)
                elif config.model_type == "openai":
                    provider = OpenAILLMProvider(config)
                else:
                    print(f"Unknown LLM type: {config.model_type}")
                    continue
                
                service.register_llm(config.name, provider)
                print(f"✅ Registered LLM: {config.name} ({config.model_name})")
                
            except Exception as e:
                print(f"❌ Failed to register {config.name}: {e}")
        
        return service
