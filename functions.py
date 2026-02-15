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

def get_secret(key, default=None):
    """
    Get secret from Streamlit secrets (production) or environment variables (local).
    
    This hybrid approach allows the code to work seamlessly in both:
    - Production (Streamlit Cloud): Uses st.secrets
    - Local development: Uses .env files and os.getenv()
    
    Args:
        key (str): The secret key name
        default: Default value if key not found
    
    Returns:
        The secret value or default
    """
    try:
        # Try Streamlit secrets first (for deployed apps)
        import streamlit as st
        return st.secrets.get(key, default)
    except (ImportError, FileNotFoundError, KeyError, AttributeError):
        # Fall back to environment variables (for local development)
        return os.getenv(key, default)


def get_pipeline_id():
    """
    Get the pipeline ID from Streamlit secrets or environment variables.
    
    Checks LLAMA_PIPELINE_ID first, then falls back to LLAMA_NGL_PIPELINE_ID.
    Returns None if neither is set - callers should handle this case.
    """
    return get_secret("LLAMA_NGL_PIPELINE_ID")
    # return os.getenv("LLAMA_NGL_PIPELINE_ID")


def get_api_key():
    """Get the LlamaCloud API key from Streamlit secrets or environment variables."""
    return get_secret("LLAMA_CLOUD_API_KEY")
    # return os.getenv("LLAMA_CLOUD_API_KEY")


def get_org_id():
    """Get the organization ID from Streamlit secrets or environment variables."""
    return get_secret("LLAMA_ORG_ID")
    # return os.getenv("LLAMA_ORG_ID")


def get_base_url():
    """Get the base URL for LlamaCloud API."""
    return get_secret("LLAMA_BASE_URL", "https://api.cloud.llamaindex.ai/api/v1")
    # return os.getenv("LLAMA_BASE_URL")


# ---------- LlamaCloud Document Management ----------

def fetch_uploaded_documents(
        pipeline_id=None,
        api_key=None,
        base_url=None,
        force_refresh=False):
    """
    Fetch list of uploaded documents from LlamaCloud API.

    Args:
        pipeline_id (str): The ID of the pipeline. Defaults to env var.
        api_key (str): Your Llama Cloud API key. Defaults to env var.
        base_url (str): Base URL for the API. Defaults to env var.
        force_refresh (bool): Force refresh from API, bypassing any cache.

    Returns:
        list: List of dictionaries with 'name' and 'id' keys for each file.
              'id' should be the file_id, not the pipeline_file_id.
    """
    pipeline_id = pipeline_id or get_pipeline_id()
    api_key = api_key or get_api_key()
    base_url = base_url or get_base_url()

    if not pipeline_id or not api_key:
        return []  # Return empty list instead of fallback

    try:
        url = f"{base_url}/pipelines/{pipeline_id}/files2"

        headers = {
            'Accept': 'application/json',
            'Authorization': f'Bearer {api_key}',
            'Cache-Control': 'no-cache' if force_refresh else 'max-age=0'
        }

        response = requests.get(url, headers=headers, timeout=30)

        if response.status_code == 200:
            data = response.json()
            files = data.get('files', [])

            # IMPORTANT FIX: Return file_id (not pipeline_file_id or id)
            # Based on your metadata, the correct field is 'file_id'
            result = []
            for file in files:
                # Try to get the correct file_id from the response
                # You might need to check the actual API response structure
                file_id = file.get('file_id') or file.get('id')
                result.append({
                    'name': file.get('name', 'Unknown'),
                    'id': file_id  # This should be 'cf0708d0-...' not '2626fd6e-...'
                })
            return result
        else:
            try:
                error_detail = response.json()
            except json.JSONDecodeError:
                error_detail = response.text
            raise requests.RequestException(
                f"Failed to fetch documents (status {response.status_code}): {error_detail}")
    except requests.RequestException:
        raise
    except Exception as e:
        raise Exception(f"Unexpected error fetching documents: {str(e)}")


def delete_document(
        file_id,
        file_name=None,
        index_name=None,
        project_name=None,
        org_id=None,
        api_key=None,
        delete_from_docstore=True
):
    """
    Delete a document from LlamaCloud using LlamaCloudIndex.

    Args:
        file_id (str): The file_id (from metadata) of the document to delete. Required.
        file_name (str): The name of the file (for logging). Optional.
        index_name (str): Name of the index. Defaults to LLAMA_INDEX_NAME env var.
        project_name (str): Name of the project. Defaults to LLAMA_PROJECT_NAME env var.
        org_id (str): Organization ID. Defaults to LLAMA_ORG_ID env var.
        api_key (str): Your Llama Cloud API key. Defaults to LLAMA_CLOUD_API_KEY env var.
        delete_from_docstore (bool): Whether to delete from document store. Defaults to True.

    Returns:
        dict: Result dictionary with 'success' and optional 'message' keys.

    Raises:
        ValueError: If file_id is not provided or required parameters missing.
    """
    from llama_index.indices.managed.llama_cloud import LlamaCloudIndex

    if not file_id:
        raise ValueError("File ID is required to delete a document!")

    # Get configuration
    index_name = index_name or get_secret("LLAMA_INDEX_NAME")
    project_name = project_name or get_secret("LLAMA_PROJECT_NAME", "Default")
    org_id = org_id or get_org_id()
    api_key = api_key or get_api_key()

    if not all([index_name, project_name, org_id, api_key]):
        raise ValueError(
            "Index name, project name, organization ID, and API key are required. "
            "Please provide them as arguments or set the corresponding environment variables."
        )

    try:
        # Initialize the index
        index = LlamaCloudIndex(
            name=index_name,
            project_name=project_name,
            organization_id=org_id,
            api_key=api_key,
        )

        # Get all reference documents
        all_docs = index.ref_doc_info

        # Find the document with matching file_id in metadata
        document_id_to_delete = None
        for doc_key, doc_info in all_docs.items():
            if doc_info.metadata and doc_info.metadata.get('file_id') == file_id:
                document_id_to_delete = doc_key
                break

        if not document_id_to_delete:
            return {
                'success': False,
                'message': f"Document with file_id '{file_id}' not found in index"
            }

        # Delete the document
        index.delete_ref_doc(
            document_id_to_delete,
            delete_from_docstore=delete_from_docstore
        )

        return {
            'success': True,
            'message': f"Successfully deleted {file_name or file_id} (document_id: {document_id_to_delete})"
        }

    except Exception as e:
        return {
            'success': False,
            'message': f"Error deleting {file_name or file_id}: {str(e)}"
        }

def upload_file_to_index(
        file_path, 
        name=None,
        project_name=None,
        org_id=None,
        api_key=None):
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
    
    name = name or get_secret("LLAMA_INDEX_NAME", "NGL_Strategy")
    project_name = project_name or get_secret("LLAMA_PROJECT_NAME", "Default")
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


def upload_files_batch(
        uploaded_files, 
        name=None,
        project_name=None,
        org_id=None,
        api_key=None):
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
    
    name = name or get_secret("LLAMA_INDEX_NAME", "NGL_Strategy")
    project_name = project_name or get_secret("LLAMA_PROJECT_NAME", "Default")
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
    api_key = api_key or get_secret("GOOGLE_API_KEY")
    
    return Gemini(
        model=model,
        api_key=api_key,
    )


# ---------- LlamaIndex Resources ----------

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
