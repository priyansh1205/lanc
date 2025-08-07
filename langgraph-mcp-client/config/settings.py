import os
from typing import Dict, List, Optional
from dataclasses import dataclass
from dotenv import load_dotenv

load_dotenv()

@dataclass
class MCPServerConfig:
    name: str
    url: str
    transport: str = "sse"

@dataclass
class LLMConfig:
    name: str
    model_type: str
    model_name: str
    api_key_env: str
    temperature: float = 0.1
    additional_params: Optional[Dict] = None

@dataclass
class AppSettings:
    mcp_servers: List[MCPServerConfig]
    llm_configs: List[LLMConfig]
    default_llm: str
    client_type: str = "terminal"

def load_settings() -> AppSettings:
    """Load application settings from environment variables"""
    
    # MCP Servers configuration
    mcp_servers = [
        MCPServerConfig(
            name="weather",
            url=os.getenv("WEATHER_MCP_URL", ""),
            transport="sse"
        ),
        MCPServerConfig(
            name="news", 
            url=os.getenv("NEWS_MCP_URL", ""),
            transport="sse"
        )
    ]
    
    # LLM configurations
    llm_configs = [
        LLMConfig(
            name="gemini",
            model_type="google",
            model_name="gemini-1.5-flash",
            api_key_env="GOOGLE_API_KEY",
            temperature=0.1
        ),
        LLMConfig(
            name="openai",
            model_type="openai", 
            model_name="gpt-4",
            api_key_env="OPENAI_API_KEY",
            temperature=0.1
        )
    ]
    
    return AppSettings(
        mcp_servers=mcp_servers,
        llm_configs=llm_configs,
        default_llm=os.getenv("DEFAULT_LLM", "gemini"),
        client_type=os.getenv("CLIENT_TYPE", "terminal")
    )
