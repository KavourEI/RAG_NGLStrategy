"""LlamaCloud services module for RAG document indexing"""
import os
from llama_index.indices.managed.llama_cloud import LlamaCloudIndex as BaseLlamaCloudIndex


class LlamaCloudIndex:
    """Wrapper for LlamaCloud index with proper authentication"""
    
    def __init__(self, name: str, project_name: str, organization_id: str, api_key: str):
        """
        Initialize LlamaCloud index with authentication credentials.
        
        Args:
            name: Name of the index
            project_name: Project name in LlamaCloud
            organization_id: Organization ID for LlamaCloud
            api_key: API key for authentication
        """
        self.name = name
        self.project_name = project_name
        self.organization_id = organization_id
        self.api_key = api_key
        
        # Set environment variables for LlamaCloud authentication
        os.environ["LLAMA_CLOUD_API_KEY"] = api_key
        
        # Initialize the base index
        self.index = BaseLlamaCloudIndex(
            name=name,
            project_name=project_name,
            organization_id=organization_id,
            api_key=api_key
        )
    
    def as_query_engine(self, llm=None):
        """
        Get query engine from the index.
        
        Args:
            llm: LLM to use for query engine
            
        Returns:
            Query engine for the index
        """
        if llm:
            return self.index.as_query_engine(llm=llm)
        else:
            return self.index.as_query_engine()
