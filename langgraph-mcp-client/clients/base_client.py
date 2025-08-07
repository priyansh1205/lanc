from abc import ABC
from interfaces.client_interface import IClient
from interfaces.workflow_interface import IWorkflow
from models.conversation import Conversation

class BaseClient(IClient):
    """Base client implementation"""
    
    def __init__(self, workflow: IWorkflow):
        self.workflow = workflow
        self.conversation = Conversation()
    
    def set_workflow(self, workflow: IWorkflow):
        """Set the workflow to use"""
        self.workflow = workflow
