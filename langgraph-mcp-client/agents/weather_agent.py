from typing import List, Any
from agents.base_agent import BaseAgent
from models.conversation import Conversation
from interfaces.llm_interface import ILLMProvider

class WeatherAgent(BaseAgent):
    """Specialized agent for weather-related queries"""
    
    def __init__(self, llm_provider: ILLMProvider):
        super().__init__(
            name="WeatherAgent",
            llm_provider=llm_provider,
            description="Specialized in providing weather information, forecasts, and climate-related queries."
        )
        self.weather_keywords = [
            'weather', 'temperature', 'rain', 'snow', 'sunny', 'cloudy', 
            'forecast', 'humidity', 'wind', 'storm', 'climate', 'hot', 'cold'
        ]
    
    def _get_default_system_prompt(self) -> str:
        """Get weather-specific system prompt"""
        return f"""You are {self.name}, a weather specialist AI assistant.

Your expertise includes:
- Current weather conditions
- Weather forecasts  
- Climate information
- Weather-related advice
- Meteorological explanations

Available weather tools: {[tool.name for tool in self.tools if 'weather' in tool.name.lower()] if self.tools else 'None'}

Always provide accurate, up-to-date weather information and include relevant details like temperature, conditions, and any weather advisories when available."""
    
    def get_relevant_tools(self, query: str) -> List[Any]:
        """Filter tools relevant to weather queries"""
        query_lower = query.lower()
        
        # Return weather-specific tools
        weather_tools = [
            tool for tool in self.tools 
            if any(keyword in tool.name.lower() or keyword in tool.description.lower() 
                   for keyword in ['weather', 'temperature', 'forecast', 'climate'])
        ]
        
        return weather_tools if weather_tools else self.tools
    
    def is_weather_query(self, query: str) -> bool:
        """Check if query is weather-related"""
        query_lower = query.lower()
        return any(keyword in query_lower for keyword in self.weather_keywords)
    
    async def process_query(self, conversation: Conversation, query: str) -> str:
        """Process weather-related query"""
        try:
            # Add system message if not present
            if not conversation.messages or conversation.messages[0].role != "system":
                conversation.messages.insert(0, 
                    Message(role="system", content=self.system_prompt)
                )
            
            # Add user query
            conversation.add_message("user", query)
            
            # Get relevant tools for this query
            relevant_tools = self.get_relevant_tools(query)
            
            # If we have weather tools, prioritize their use
            if relevant_tools:
                # Create a context-aware prompt
                enhanced_query = f"""Weather Query: {query}

Available weather tools: {[tool.name for tool in relevant_tools]}

Please use the appropriate weather tools to provide accurate, current information."""
                
                # Use LLM with tool context (this would integrate with your workflow)
                response = await self.llm_provider.generate_response(conversation.messages[-5:])
            else:
                # Fallback to general weather knowledge
                enhanced_query = f"""As a weather specialist, please provide information about: {query}

Note: Real-time weather data is not currently available, so provide general weather information and advice users to check current conditions from reliable weather services."""
                
                conversation.messages[-1].content = enhanced_query
                response = await self.llm_provider.generate_response(conversation.messages[-3:])
            
            # Add response to conversation
            conversation.add_message("assistant", response)
            
            return response
            
        except Exception as e:
            error_response = f"I apologize, but I encountered an error processing your weather query: {str(e)}. Please try rephrasing your question."
            conversation.add_message("assistant", error_response)
            return error_response
