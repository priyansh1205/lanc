from typing import List, Any
from agents.base_agent import BaseAgent
from models.conversation import Conversation
from interfaces.llm_interface import ILLMProvider

class NewsAgent(BaseAgent):
    """Specialized agent for news and current events queries"""
    
    def __init__(self, llm_provider: ILLMProvider):
        super().__init__(
            name="NewsAgent", 
            llm_provider=llm_provider,
            description="Specialized in providing current news, trending topics, and analysis of recent events."
        )
        self.news_keywords = [
            'news', 'breaking', 'headlines', 'current events', 'trending',
            'politics', 'business', 'technology', 'sports', 'entertainment',
            'world', 'local', 'latest', 'update', 'report'
        ]
        self.news_categories = [
            'general', 'business', 'technology', 'sports', 'health',
            'science', 'entertainment', 'politics', 'world'
        ]
    
    def _get_default_system_prompt(self) -> str:
        """Get news-specific system prompt"""
        return f"""You are {self.name}, a news and current events specialist AI assistant.

Your expertise includes:
- Latest news and headlines
- Breaking news updates  
- News analysis and summaries
- Trending topics across categories
- Current events context

Available news tools: {[tool.name for tool in self.tools if 'news' in tool.name.lower()] if self.tools else 'None'}

Categories you can help with: {', '.join(self.news_categories)}

Always provide factual, unbiased news information and cite sources when available. For breaking news, emphasize the importance of checking multiple reliable sources."""
    
    def get_relevant_tools(self, query: str) -> List[Any]:
        """Filter tools relevant to news queries"""
        query_lower = query.lower()
        
        # Return news-specific tools
        news_tools = [
            tool for tool in self.tools 
            if any(keyword in tool.name.lower() or keyword in tool.description.lower() 
                   for keyword in ['news', 'headline', 'article', 'press'])
        ]
        
        return news_tools if news_tools else self.tools
    
    def is_news_query(self, query: str) -> bool:
        """Check if query is news-related"""
        query_lower = query.lower()
        return any(keyword in query_lower for keyword in self.news_keywords)
    
    def extract_news_category(self, query: str) -> str:
        """Extract news category from query"""
        query_lower = query.lower()
        for category in self.news_categories:
            if category in query_lower:
                return category
        return 'general'  # default category
    
    async def process_query(self, conversation: Conversation, query: str) -> str:
        """Process news-related query"""
        try:
            # Add system message if not present
            if not conversation.messages or conversation.messages[0].role != "system":
                conversation.messages.insert(0, 
                    Message(role="system", content=self.system_prompt)
                )
            
            # Add user query
            conversation.add_message("user", query)
            
            # Get relevant tools and category
            relevant_tools = self.get_relevant_tools(query)
            category = self.extract_news_category(query)
            
            if relevant_tools:
                # Create a context-aware prompt for news
                enhanced_query = f"""News Query: {query}
Category: {category}

Available news tools: {[tool.name for tool in relevant_tools]}

Please use the appropriate news tools to fetch current, relevant information. Provide a summary and highlight key points."""
                
                # Use LLM with tool context
                response = await self.llm_provider.generate_response(conversation.messages[-5:])
            else:
                # Fallback to general news knowledge
                enhanced_query = f"""As a news specialist, please provide information about: {query}

Category: {category}

Note: Real-time news data is not currently available. Please provide context based on general knowledge and advise users to check current news from reliable sources for the latest updates."""
                
                conversation.messages[-1].content = enhanced_query  
                response = await self.llm_provider.generate_response(conversation.messages[-3:])
            
            # Add response to conversation
            conversation.add_message("assistant", response)
            
            return response
            
        except Exception as e:
            error_response = f"I apologize, but I encountered an error processing your news query: {str(e)}. Please try rephrasing your question."
            conversation.add_message("assistant", error_response)
            return error_response
