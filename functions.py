"""
functions.py - Modular utility functions for RAG applications.

This module contains all non-Streamlit business logic functions that can be
reused across different projects and pages. Functions include:
- LlamaCloud document management (fetch, upload, delete)
- LlamaIndex resource initialization (index, LLM, query engine)
- Response processing utilities
"""

import os
import tempfile
import requests
import json
from dotenv import load_dotenv

# Load environment variables once at module level
load_dotenv()


# ---------- Configuration ----------

def get_pipeline_id():
    """
    Get the pipeline ID from environment variables.
    
    Checks LLAMA_PIPELINE_ID first, then falls back to LLAMA_NGL_PIPELINE_ID.
    Returns None if neither is set - callers should handle this case.
    """
    return os.getenv("LLAMA_PIPELINE_ID") or os.getenv("LLAMA_NGL_PIPELINE_ID")


def get_api_key():
    """Get the LlamaCloud API key from environment variables."""
    return os.getenv("LLAMA_CLOUD_API_KEY")


def get_org_id():
    """Get the organization ID from environment variables."""
    return os.getenv("LLAMA_ORG_ID")


def get_base_url():
    """Get the base URL for LlamaCloud API."""
    return os.getenv("LLAMA_BASE_URL", "https://api.cloud.llamaindex.ai/api/v1")


# ---------- LlamaCloud Document Management ----------

def fetch_uploaded_documents(pipeline_id=None, api_key=None, base_url=None):
    """
    Fetch list of uploaded documents from LlamaCloud API.
    
    Args:
        pipeline_id (str): The ID of the pipeline. Defaults to env var.
        api_key (str): Your Llama Cloud API key. Defaults to env var.
        base_url (str): Base URL for the API. Defaults to env var.
    
    Returns:
        list: List of dictionaries with 'name' and 'id' keys for each file.
              Returns fallback list on error.
    """
    pipeline_id = pipeline_id or get_pipeline_id()
    api_key = api_key or get_api_key()
    base_url = base_url or get_base_url()
    
    if not pipeline_id or not api_key:
        return [{'name': 'current.pdf', 'id': None}]  # Fallback
    
    try:
        url = f"{base_url}/pipelines/{pipeline_id}/files2"
        
        headers = {
            'Accept': 'application/json',
            'Authorization': f'Bearer {api_key}'
        }
        
        response = requests.get(url, headers=headers, timeout=30)
        
        if response.status_code == 200:
            data = response.json()
            files = data.get('files', [])
            return [{'name': file.get('name', 'Unknown'), 'id': file.get('id')} for file in files]
        else:
            try:
                error_detail = response.json()
            except json.JSONDecodeError:
                error_detail = response.text
            raise requests.RequestException(f"Failed to fetch documents (status {response.status_code}): {error_detail}")
    except requests.RequestException:
        raise
    except Exception as e:
        raise Exception(f"Unexpected error fetching documents: {str(e)}")


def delete_document(file_id, file_name=None, pipeline_id=None, api_key=None, base_url=None):
    """
    Delete a document from LlamaCloud.
    
    Args:
        file_id (str): The ID of the file to delete. Required.
        file_name (str): The name of the file (for logging). Optional.
        pipeline_id (str): The ID of the pipeline. Defaults to env var.
        api_key (str): Your Llama Cloud API key. Defaults to env var.
        base_url (str): Base URL for the API. Defaults to env var.
    
    Returns:
        dict: Result dictionary with 'success' and optional 'message' keys.
    
    Raises:
        ValueError: If file_id is not provided.
        requests.RequestException: If the HTTP request fails.
    """
    if not file_id:
        raise ValueError("File ID is required to delete a file!")
    
    pipeline_id = pipeline_id or get_pipeline_id()
    api_key = api_key or get_api_key()
    base_url = base_url or get_base_url()
    
    if not pipeline_id or not api_key:
        raise ValueError("Pipeline ID and API key are required")
    
    try:
        url = f"{base_url}/pipelines/{pipeline_id}/files/{file_id}"
        
        headers = {
            'Accept': 'application/json',
            'Authorization': f'Bearer {api_key}'
        }
        
        response = requests.delete(url, headers=headers, timeout=30)
        
        if response.status_code in [200, 204]:
            return {
                'success': True,
                'message': f"Successfully deleted {file_name or file_id}"
            }
        else:
            try:
                error_detail = response.json()
            except json.JSONDecodeError:
                error_detail = response.text
            return {
                'success': False,
                'message': f"Failed to delete {file_name or file_id} (status {response.status_code}): {error_detail}"
            }
    except requests.RequestException as e:
        return {
            'success': False,
            'message': f"Network error deleting {file_name or file_id}: {str(e)}"
        }
    except Exception as e:
        return {
            'success': False,
            'message': f"Unexpected error deleting {file_name or file_id}: {str(e)}"
        }


def upload_file_to_index(file_path, name=None, project_name=None, org_id=None, api_key=None):
    """
    Upload a file to a LlamaIndex Cloud index.
    
    Args:
        file_path (str): Path to the file to upload. Required.
        name (str): The name of the index. Defaults to LLAMA_INDEX_NAME or "NGL_Strategy".
        project_name (str): The name of the project. Defaults to LLAMA_PROJECT_NAME or "Default".
        org_id (str): The organization ID. Defaults to LLAMA_ORG_ID env var.
        api_key (str): Your Llama Cloud API key. Defaults to LLAMA_CLOUD_API_KEY env var.
    
    Returns:
        dict: Result dictionary with 'success', 'message', and optional 'result' keys.
    
    Raises:
        ValueError: If required parameters are missing.
        FileNotFoundError: If file_path doesn't exist.
    """
    # Lazy import to avoid loading LlamaIndex when not needed
    from llama_index.indices.managed.llama_cloud import LlamaCloudIndex
    
    name = name or os.getenv("LLAMA_INDEX_NAME", "NGL_Strategy")
    project_name = project_name or os.getenv("LLAMA_PROJECT_NAME", "Default")
    org_id = org_id or get_org_id()
    api_key = api_key or get_api_key()
    
    if not file_path:
        raise ValueError("File path is required to upload a file!")
    
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"File not found: {file_path}")
    
    if not org_id or not api_key:
        raise ValueError("Organization ID and API key are required")
    
    try:
        index = LlamaCloudIndex(
            name=name,
            project_name=project_name,
            organization_id=org_id,
            api_key=api_key,
        )
        
        result = index.upload_file(file_path=file_path)
        return {
            'success': True,
            'message': f"Successfully uploaded {os.path.basename(file_path)}",
            'result': result
        }
    except Exception as e:
        return {
            'success': False,
            'message': f"Error uploading {os.path.basename(file_path)}: {str(e)}"
        }


def upload_files_batch(uploaded_files, name=None, project_name=None, org_id=None, api_key=None):
    """
    Upload multiple files to a LlamaIndex Cloud index.
    
    Args:
        uploaded_files: List of Streamlit UploadedFile objects or file-like objects with
                       'name' attribute and 'getbuffer()' method.
        name (str): The name of the index. Defaults to LLAMA_INDEX_NAME or "NGL_Strategy".
        project_name (str): The name of the project. Defaults to LLAMA_PROJECT_NAME or "Default".
        org_id (str): The organization ID. Defaults to LLAMA_ORG_ID env var.
        api_key (str): Your Llama Cloud API key. Defaults to LLAMA_CLOUD_API_KEY env var.
    
    Returns:
        dict: Result dictionary with 'success_files', 'failed_files', and 'errors' keys.
    """
    success_files = []
    failed_files = []
    errors = []
    
    for f in uploaded_files:
        temp_dir = tempfile.mkdtemp()
        file_path = os.path.join(temp_dir, f.name)
        
        try:
            with open(file_path, "wb") as temp_file:
                temp_file.write(f.getbuffer())
            
            result = upload_file_to_index(
                file_path=file_path,
                name=name,
                project_name=project_name,
                org_id=org_id,
                api_key=api_key
            )
            
            if result['success']:
                success_files.append(f.name)
            else:
                failed_files.append(f.name)
                errors.append(result['message'])
        except Exception as e:
            failed_files.append(f.name)
            errors.append(str(e))
        finally:
            try:
                os.remove(file_path)
                os.rmdir(temp_dir)
            except OSError:
                pass  # Cleanup errors are non-critical
    
    return {
        'success_files': success_files,
        'failed_files': failed_files,
        'errors': errors
    }


# ---------- LlamaIndex Resources ----------

def create_llama_cloud_index(name=None, project_name=None, org_id=None, api_key=None):
    """
    Create and return a LlamaCloudIndex connection.
    
    Args:
        name (str): The name of the index. Defaults to LLAMA_INDEX_NAME or "NGL_Strategy".
        project_name (str): The name of the project. Defaults to LLAMA_PROJECT_NAME or "Default".
        org_id (str): The organization ID. Defaults to LLAMA_ORG_ID env var.
        api_key (str): Your Llama Cloud API key. Defaults to LLAMA_CLOUD_API_KEY env var.
    
    Returns:
        LlamaCloudIndex: The configured index object.
    """
    from llama_index.indices.managed.llama_cloud import LlamaCloudIndex
    
    name = name or os.getenv("LLAMA_INDEX_NAME", "NGL_Strategy")
    project_name = project_name or os.getenv("LLAMA_PROJECT_NAME", "Default")
    org_id = org_id or get_org_id()
    api_key = api_key or get_api_key()
    
    return LlamaCloudIndex(
        name=name,
        project_name=project_name,
        organization_id=org_id,
        api_key=api_key,
    )


def create_gemini_llm(model=None, api_key=None):
    """
    Create and return a Gemini LLM instance.
    
    Args:
        model (str): The model name. Defaults to "models/gemini-2.5-flash".
        api_key (str): Google API key. Defaults to GOOGLE_API_KEY env var.
    
    Returns:
        Gemini: The configured LLM object.
    """
    from llama_index.llms.gemini import Gemini
    
    model = model or "models/gemini-2.5-flash"
    api_key = api_key or os.getenv("GOOGLE_API_KEY")
    
    return Gemini(
        model=model,
        api_key=api_key,
    )


def create_query_engine(index=None, llm=None):
    """
    Create and return a query engine using the provided index and LLM.
    
    Args:
        index: A LlamaIndex index object. If None, creates a default LlamaCloudIndex.
        llm: A LlamaIndex LLM object. If None, creates a default Gemini LLM.
    
    Returns:
        QueryEngine: The configured query engine.
    """
    if index is None:
        index = create_llama_cloud_index()
    if llm is None:
        llm = create_gemini_llm()
    
    return index.as_query_engine(llm=llm)


# ---------- Response Processing ----------

def extract_response_text(response):
    """
    Extract text content from a LlamaIndex query response.
    
    Args:
        response: The response object from a query engine.
    
    Returns:
        str: The extracted text content.
    """
    if hasattr(response, "response"):
        return response.response
    elif hasattr(response, "text"):
        return response.text
    else:
        return str(response)


def extract_source_nodes(response, max_text_length=200):
    """
    Extract source information from a LlamaIndex query response.
    
    Args:
        response: The response object from a query engine.
        max_text_length (int): Maximum characters to include from source text.
    
    Returns:
        list: List of dictionaries containing source information.
    """
    sources = []
    if hasattr(response, "source_nodes"):
        for node in response.source_nodes:
            source_info = {
                'file_name': node.node.metadata.get('file_name', 'Unknown'),
                'text': node.node.text if hasattr(node.node, 'text') else '',
                'score': node.score if hasattr(node, 'score') else None
            }
            sources.append(source_info)
    return sources


def process_query_response(response, max_source_text_length=200):
    """
    Process a complete query response and extract text and sources.
    
    Args:
        response: The response object from a query engine.
        max_source_text_length (int): Maximum characters to include from source text.
    
    Returns:
        dict: Dictionary with 'text' and 'sources' keys.
    """
    return {
        'text': extract_response_text(response),
        'sources': extract_source_nodes(response, max_source_text_length)
    }
