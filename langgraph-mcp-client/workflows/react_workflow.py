from workflows.base_workflow import BaseWorkflow
from models.conversation import Conversation
from interfaces.llm_interface import ILLMService
from agents.agent_manager import AgentFactory, AgentManager

class ReactWorkflow(BaseWorkflow):
    """ReAct workflow with agent routing"""
    
    def __init__(self, llm_service: ILLMService, llm_name: str):
        super().__init__()
        self.llm_service = llm_service
        self.llm_name = llm_name
        self.agent_manager: AgentManager = AgentFactory.create_agent_manager(llm_service, llm_name)
        self.use_agent_routing = True
    
    def set_tools(self, tools: List[Any]):
        """Set tools and distribute to agents"""
        super().set_tools(tools)
        
        # Distribute tools to all agents
        for agent in self.agent_manager.agents.values():
            agent.set_tools(tools)
        
        print(f"✅ Distributed tools to {len(self.agent_manager.list_agents())} agents")
    
    async def execute(self, conversation: Conversation, query: str) -> str:
        """Execute workflow with agent routing"""
        try:
            if self.use_agent_routing:
                # Route to appropriate agent
                selected_agent = self.agent_manager.route_query(query)
                print(f"🎯 Routing to: {selected_agent.name}")
                return await selected_agent.process_query(conversation, query)
            else:
                # Use default agent
                default_agent = self.agent_manager.get_default_agent()
                if default_agent:
                    return await default_agent.process_query(conversation, query)
                else:
                    return "No agents available to process the query."
                    
        except Exception as e:
            error_msg = f"Error in agent workflow: {e}"
            conversation.add_message("assistant", error_msg)
            return error_msg
    
    def toggle_agent_routing(self, enabled: bool):
        """Enable/disable intelligent agent routing"""
        self.use_agent_routing = enabled
        print(f"Agent routing: {'enabled' if enabled else 'disabled'}")
