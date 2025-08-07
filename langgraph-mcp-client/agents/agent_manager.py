from typing import Dict, List, Optional
from agents.base_agent import BaseAgent
from agents.weather_agent import WeatherAgent
from agents.news_agent import NewsAgent
from interfaces.llm_interface import ILLMService

class AgentManager:
    """Manager for handling multiple specialized agents"""
    
    def __init__(self, llm_service: ILLMService):
        self.llm_service = llm_service
        self.agents: Dict[str, BaseAgent] = {}
        self.default_agent_name = None
    
    def register_agent(self, agent: BaseAgent, is_default: bool = False):
        """Register a new agent"""
        self.agents[agent.name] = agent
        if is_default or not self.default_agent_name:
            self.default_agent_name = agent.name
        print(f"✅ Registered agent: {agent.name}")
    
    def get_agent(self, name: str) -> Optional[BaseAgent]:
        """Get agent by name"""
        return self.agents.get(name)
    
    def get_default_agent(self) -> Optional[BaseAgent]:
        """Get the default agent"""
        if self.default_agent_name:
            return self.agents.get(self.default_agent_name)
        return None
    
    def route_query(self, query: str) -> BaseAgent:
        """Route query to the most appropriate agent"""
        query_lower = query.lower()
        
        # Check weather agent
        if 'weather_agent' in self.agents:
            weather_agent = self.agents['weather_agent']
            if hasattr(weather_agent, 'is_weather_query') and weather_agent.is_weather_query(query):
                return weather_agent
        
        # Check news agent
        if 'news_agent' in self.agents:
            news_agent = self.agents['news_agent']
            if hasattr(news_agent, 'is_news_query') and news_agent.is_news_query(query):
                return news_agent
        
        # Return default agent or first available
        default_agent = self.get_default_agent()
        if default_agent:
            return default_agent
        
        # Return first available agent as fallback
        if self.agents:
            return next(iter(self.agents.values()))
        
        raise ValueError("No agents available")
    
    def list_agents(self) -> List[str]:
        """List all registered agents"""
        return list(self.agents.keys())
    
    def get_agents_info(self) -> Dict[str, Dict]:
        """Get information about all agents"""
        return {name: agent.get_agent_info() for name, agent in self.agents.items()}

class AgentFactory:
    """Factory for creating specialized agents"""
    
    @staticmethod
    def create_agent_manager(llm_service: ILLMService, default_llm: str = None) -> AgentManager:
        """Create and populate agent manager with default agents"""
        manager = AgentManager(llm_service)
        
        # Get default LLM provider
        if not default_llm:
            available_llms = llm_service.list_providers()
            if not available_llms:
                raise ValueError("No LLM providers available")
            default_llm = available_llms[0]
        
        llm_provider = llm_service.get_llm(default_llm)
        
        # Create specialized agents
        try:
            weather_agent = WeatherAgent(llm_provider)
            manager.register_agent(weather_agent)
            
            news_agent = NewsAgent(llm_provider)  
            manager.register_agent(news_agent, is_default=True)  # Make news agent default
            
            print(f"✅ Created agent manager with {len(manager.list_agents())} agents")
            
        except Exception as e:
            print(f"❌ Error creating agents: {e}")
        
        return manager
