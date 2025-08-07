from abc import ABC, abstractmethod
from workflows.base_workflow import IWorkflow

class IClient(ABC):
    """Interface for client implementations"""
    
    @abstractmethod
    async def start(self):
        """Start the client"""
        pass
    
    @abstractmethod
    async def stop(self):
        """Stop the client"""
        pass
    
    @abstractmethod
    def set_workflow(self, workflow: IWorkflow):
        """Set the workflow to use"""
        pass
