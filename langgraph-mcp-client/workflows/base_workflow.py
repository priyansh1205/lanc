from abc import ABC
from typing import Any, List
from interfaces.workflow_interface import IWorkflow

class BaseWorkflow(IWorkflow):
    """Base workflow implementation"""
    
    def __init__(self):
        self.tools: List[Any] = []
    
    def set_tools(self, tools: List[Any]):
        """Set available tools for workflow"""
        self.tools = tools
        print(f"🔧 Loaded {len(tools)} tools for workflow")
        for tool in tools:
            print(f"   • {tool.name}: {tool.description}")
