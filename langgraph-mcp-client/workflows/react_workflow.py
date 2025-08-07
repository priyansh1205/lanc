from typing import Any, List
from workflows.base_workflow import BaseWorkflow
from models.conversation import Conversation
from interfaces.llm_interface import ILLMService

try:
    from langgraph.prebuilt import create_react_agent
except ImportError:
    create_react_agent = None

class ReactWorkflow(BaseWorkflow):
    """ReAct (Reasoning + Acting) workflow implementation"""
    
    def __init__(self, llm_service: ILLMService, llm_name: str):
        super().__init__()
        self.llm_service = llm_service
        self.llm_name = llm_name
        self.agent = None
    
    def set_tools(self, tools: List[Any]):
        """Set tools and create ReAct agent"""
        super().set_tools(tools)
        
        if create_react_agent is None:
            raise ImportError("langgraph not installed")
        
        try:
            # Get the LLM provider
            llm_provider = self.llm_service.get_llm(self.llm_name)
            
            # For LangGraph, we need the actual LLM instance, not our wrapper
            # This is a simplified approach - you may need to adjust based on your LLM providers
            if hasattr(llm_provider, 'llm'):
                self.agent = create_react_agent(llm_provider.llm, tools)
            else:
                raise ValueError("LLM provider doesn't expose underlying LLM instance")
                
            print(f"✅ ReAct agent created with {self.llm_name}")
            
        except Exception as e:
            print(f"❌ Failed to create ReAct agent: {e}")
            raise
    
    async def execute(self, conversation: Conversation, query: str) -> str:
        """Execute ReAct workflow"""
        if not self.agent:
            raise ValueError("Agent not initialized. Call set_tools first.")
        
        try:
            # Add user query to conversation
            conversation.add_message("user", query)
            
            # Convert to LangGraph format and invoke
            conversation_state = conversation.to_langgraph_format()
            result = await self.agent.ainvoke(conversation_state)
            
            # Extract response
            response_content = self._extract_response(result)
            
            # Add assistant response to conversation
            conversation.add_message("assistant", response_content)
            
            return response_content
            
        except Exception as e:
            error_msg = f"Error in ReAct workflow: {e}"
            conversation.add_message("assistant", error_msg)
            return error_msg
    
    def _extract_response(self, result: Any) -> str:
        """Extract response content from LangGraph result"""
        try:
            if isinstance(result, dict):
                if "messages" in result and len(result["messages"]) > 0:
                    last_message = result["messages"][-1]
                    if isinstance(last_message, dict):
                        return last_message.get("content", str(last_message))
                    elif hasattr(last_message, 'content'):
                        return last_message.content
                    else:
                        return str(last_message)
                else:
                    return str(result)
            elif hasattr(result, 'content'):
                return result.content
            elif hasattr(result, 'messages') and len(result.messages) > 0:
                return result.messages[-1].content
            else:
                return str(result)
        except Exception as e:
            return f"Could not extract response: {e}"
