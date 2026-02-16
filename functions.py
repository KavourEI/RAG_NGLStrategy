"""
functions.py - Modular utility functions for RAG applications.

This module contains all non-Streamlit business logic functions that can be
reused across different projects and pages. Functions include:
- LlamaCloud document management (fetch, upload, delete) with retry logic
- LlamaIndex resource initialization (index, LLM, query engine) with caching
- Document metadata parsing (★NO.XXXX date pattern extraction)
- Date-priority node postprocessing (newest documents first)
- Concurrent batch file uploads via ThreadPoolExecutor
- Centralized LlamaIndex Settings initialization
- Configuration validation
- Response processing utilities with enhanced metadata extraction
"""

import os
import re
import time
import logging
import tempfile
import requests
import json
from datetime import datetime
from functools import wraps
from concurrent.futures import ThreadPoolExecutor, as_completed
from dotenv import load_dotenv

# Load environment variables once at module level
load_dotenv()

# Module-level logger
logger = logging.getLogger(__name__)

# ---------- Module-level Cache ----------
_cache = {
    'index': None,
    'llm': None,
    'query_engine': None,
}


def clear_cache():
    """Clear all cached LlamaIndex resources. Useful when credentials change."""
    _cache['index'] = None
    _cache['llm'] = None
    _cache['query_engine'] = None


# ---------- Retry Decorator ----------

def retry_with_backoff(max_retries=3, base_delay=1.0, backoff_factor=2.0, retryable_exceptions=(requests.RequestException,)):
    """
    Decorator that retries a function with exponential backoff.
    
    Args:
        max_retries (int): Maximum number of retry attempts.
        base_delay (float): Initial delay in seconds before first retry.
        backoff_factor (float): Multiplier for delay between retries.
        retryable_exceptions (tuple): Exception types that trigger a retry.
    
    Returns:
        Decorated function with retry logic.
    """
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            last_exception = None
            for attempt in range(max_retries + 1):
                try:
                    return func(*args, **kwargs)
                except retryable_exceptions as e:
                    last_exception = e
                    if attempt < max_retries:
                        delay = base_delay * (backoff_factor ** attempt)
                        logger.warning(
                            f"{func.__name__} failed (attempt {attempt + 1}/{max_retries + 1}), "
                            f"retrying in {delay:.1f}s: {e}"
                        )
                        time.sleep(delay)
                    else:
                        logger.error(f"{func.__name__} failed after {max_retries + 1} attempts: {e}")
            raise last_exception
        return wrapper
    return decorator


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
    # return get_secret("LLAMA_NGL_PIPELINE_ID")
    return os.getenv("LLAMA_NGL_PIPELINE_ID")


def get_api_key():
    """Get the LlamaCloud API key from Streamlit secrets or environment variables."""
    # return get_secret("LLAMA_CLOUD_API_KEY")
    return os.getenv("LLAMA_CLOUD_API_KEY")


def get_org_id():
    """Get the organization ID from Streamlit secrets or environment variables."""
    # return get_secret("LLAMA_ORG_ID")
    return os.getenv("LLAMA_ORG_ID")


def get_base_url():
    """Get the base URL for LlamaCloud API."""
    # return get_secret("LLAMA_BASE_URL", "https://api.cloud.llamaindex.ai/api/v1")
    return os.getenv("LLAMA_BASE_URL")


# ---------- Settings Validation ----------

def validate_settings(require_llama=True, require_google=False):
    """
    Validate that required configuration settings are available.
    
    Call this early in your application to catch missing configuration
    before making API calls that would fail.
    
    Args:
        require_llama (bool): Check LlamaCloud credentials (pipeline, API key, org).
        require_google (bool): Check Google API key.
    
    Returns:
        dict: Validation result with 'valid' (bool) and 'missing' (list of str) keys.
    """
    missing = []
    
    if require_llama:
        if not get_pipeline_id():
            missing.append("LLAMA_NGL_PIPELINE_ID")
        if not get_api_key():
            missing.append("LLAMA_CLOUD_API_KEY")
        if not get_org_id():
            missing.append("LLAMA_ORG_ID")
        if not get_base_url():
            missing.append("LLAMA_BASE_URL")
    
    if require_google:
        if not os.getenv("GOOGLE_API_KEY"):
            missing.append("GOOGLE_API_KEY")
    
    if missing:
        logger.warning(f"Missing configuration keys: {', '.join(missing)}")
    
    return {
        'valid': len(missing) == 0,
        'missing': missing
    }


# ---------- LlamaCloud Document Management ----------

@retry_with_backoff(max_retries=3, base_delay=1.0, backoff_factor=2.0)
def fetch_uploaded_documents(
        pipeline_id=None, 
        api_key=None, 
        base_url=None):
    """
    Fetch list of uploaded documents from LlamaCloud API.
    
    Includes automatic retry with exponential backoff for transient failures.
    
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


def sync_pipeline(pipeline_id=None, api_key=None, base_url=None):
    """
    Trigger a pipeline sync on LlamaCloud.
    
    This should be called after deleting documents to ensure the pipeline
    index is updated and stale file references are cleaned up.
    
    Args:
        pipeline_id (str): The ID of the pipeline. Defaults to env var.
        api_key (str): Your Llama Cloud API key. Defaults to env var.
        base_url (str): Base URL for the API. Defaults to env var.
    
    Returns:
        dict: Result dictionary with 'success' and 'message' keys.
    """
    pipeline_id = pipeline_id or get_pipeline_id()
    api_key = api_key or get_api_key()
    base_url = base_url or get_base_url()
    
    if not pipeline_id or not api_key:
        return {'success': False, 'message': 'Pipeline ID and API key are required'}
    
    try:
        url = f"{base_url}/pipelines/{pipeline_id}/sync"
        headers = {
            'Accept': 'application/json',
            'Authorization': f'Bearer {api_key}'
        }
        
        response = requests.post(url, headers=headers, timeout=30)
        
        if response.status_code in [200, 202, 204]:
            logger.info(f"Pipeline {pipeline_id} sync triggered successfully.")
            return {'success': True, 'message': 'Pipeline sync triggered'}
        else:
            try:
                error_detail = response.json()
            except json.JSONDecodeError:
                error_detail = response.text
            logger.warning(f"Pipeline sync returned status {response.status_code}: {error_detail}")
            return {'success': False, 'message': f'Sync returned status {response.status_code}: {error_detail}'}
    except requests.RequestException as e:
        logger.warning(f"Pipeline sync network error: {e}")
        return {'success': False, 'message': f'Network error during sync: {str(e)}'}


@retry_with_backoff(max_retries=3, base_delay=1.0, backoff_factor=2.0)
def delete_document(
        file_id, 
        file_name=None, 
        pipeline_id=None, 
        api_key=None, 
        base_url=None):
    """
    Fully delete a document from LlamaCloud.
    
    Performs a three-step deletion to ensure the file is completely removed
    from all layers:
      1. Remove the file from the pipeline (DELETE /pipelines/{id}/files/{file_id})
      2. Remove the underlying file from the project (DELETE /files/{file_id})
      3. Sync the pipeline so the vector store drops its embeddings
    
    Also clears the cached query engine so subsequent queries won't reference
    stale vectors.
    
    Args:
        file_id (str): The ID of the file to delete. Required.
        file_name (str): The name of the file (for logging). Optional.
        pipeline_id (str): The ID of the pipeline. Defaults to env var.
        api_key (str): Your Llama Cloud API key. Defaults to env var.
        base_url (str): Base URL for the API. Defaults to env var.
    
    Returns:
        dict: Result dictionary with 'success' and 'message' keys.
    
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
    
    display_name = file_name or file_id
    steps_completed = []
    
    headers = {
        'Accept': 'application/json',
        'Authorization': f'Bearer {api_key}'
    }
    
    try:
        # --- Step 1: Remove file from the pipeline ---
        pipeline_url = f"{base_url}/pipelines/{pipeline_id}/files/{file_id}"
        r_pipeline = requests.delete(pipeline_url, headers=headers, timeout=30)
        
        if r_pipeline.status_code in [200, 204]:
            steps_completed.append('pipeline')
            logger.info(f"Step 1: Removed {display_name} from pipeline.")
        else:
            try:
                error_detail = r_pipeline.json()
            except json.JSONDecodeError:
                error_detail = r_pipeline.text
            
            detail_str = str(error_detail.get('detail', '')) if isinstance(error_detail, dict) else str(error_detail)
            if 'already deleted' in detail_str.lower():
                steps_completed.append('pipeline (was already removed)')
                logger.info(f"Step 1: {display_name} was already removed from pipeline.")
            else:
                logger.warning(f"Step 1 failed for {display_name}: {error_detail}")
        
        # --- Step 2: Delete the underlying file from the project ---
        file_url = f"{base_url}/files/{file_id}"
        r_file = requests.delete(file_url, headers=headers, timeout=30)
        
        if r_file.status_code in [200, 204]:
            steps_completed.append('project file')
            logger.info(f"Step 2: Deleted {display_name} from project files.")
        elif r_file.status_code == 404:
            steps_completed.append('project file (was already gone)')
            logger.info(f"Step 2: {display_name} was already deleted from project.")
        else:
            try:
                file_error = r_file.json()
            except json.JSONDecodeError:
                file_error = r_file.text
            logger.warning(f"Step 2 failed for {display_name}: status {r_file.status_code}, {file_error}")
        
        # --- Step 3: Sync the pipeline to update the vector store ---
        sync_result = sync_pipeline(pipeline_id, api_key, base_url)
        if sync_result['success']:
            steps_completed.append('pipeline sync')
            logger.info(f"Step 3: Pipeline sync triggered for {display_name}.")
        else:
            logger.warning(f"Step 3: Pipeline sync failed: {sync_result['message']}")
        
        # --- Step 4: Clear cached query engine so it rebuilds ---
        _cache['query_engine'] = None
        steps_completed.append('cache cleared')
        
        # Determine overall success
        # Success if we completed at least the pipeline removal and file deletion
        pipeline_ok = any('pipeline' in s for s in steps_completed)
        file_ok = any('project file' in s for s in steps_completed)
        
        if pipeline_ok and file_ok:
            return {
                'success': True,
                'message': f"Successfully deleted {display_name} (steps: {', '.join(steps_completed)})"
            }
        elif pipeline_ok or file_ok:
            return {
                'success': True,
                'message': f"Partially deleted {display_name} (steps: {', '.join(steps_completed)}). Full removal will complete after pipeline sync."
            }
        else:
            return {
                'success': False,
                'message': f"Failed to delete {display_name}. No deletion steps succeeded."
            }
    except requests.RequestException as e:
        return {
            'success': False,
            'message': f"Network error deleting {display_name}: {str(e)}"
        }
    except Exception as e:
        return {
            'success': False,
            'message': f"Unexpected error deleting {display_name}: {str(e)}"
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
        api_key=None,
        max_workers=3):
    """
    Upload multiple files to a LlamaIndex Cloud index concurrently.
    
    Uses ThreadPoolExecutor for parallel uploads, significantly improving
    throughput when uploading many files.
    
    Args:
        uploaded_files: List of Streamlit UploadedFile objects or file-like objects with
                       'name' attribute and 'getbuffer()' method.
        name (str): The name of the index. Defaults to LLAMA_INDEX_NAME or "NGL_Strategy".
        project_name (str): The name of the project. Defaults to LLAMA_PROJECT_NAME or "Default".
        org_id (str): The organization ID. Defaults to LLAMA_ORG_ID env var.
        api_key (str): Your Llama Cloud API key. Defaults to LLAMA_CLOUD_API_KEY env var.
        max_workers (int): Maximum number of concurrent uploads. Defaults to 3.
    
    Returns:
        dict: Result dictionary with 'success_files', 'failed_files', and 'errors' keys.
    """
    success_files = []
    failed_files = []
    errors = []

    def _upload_single(f):
        """Upload a single file in a thread-safe manner."""
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
            return f.name, result
        except Exception as e:
            return f.name, {'success': False, 'message': str(e)}
        finally:
            try:
                os.remove(file_path)
                os.rmdir(temp_dir)
            except OSError:
                pass  # Cleanup errors are non-critical

    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        futures = {executor.submit(_upload_single, f): f for f in uploaded_files}
        for future in as_completed(futures):
            file_name, result = future.result()
            if result['success']:
                success_files.append(file_name)
            else:
                failed_files.append(file_name)
                errors.append(result['message'])

    return {
        'success_files': success_files,
        'failed_files': failed_files,
        'errors': errors
    }


# ---------- LlamaIndex Resources ----------

def create_llama_cloud_index(name=None, project_name=None, org_id=None, api_key=None, use_cache=True):
    """
    Create and return a LlamaCloudIndex connection.
    
    Uses module-level caching by default to avoid redundant connections.
    Pass use_cache=False to force creating a new instance.
    
    Args:
        name (str): The name of the index. Defaults to LLAMA_INDEX_NAME or "NGL_Strategy".
        project_name (str): The name of the project. Defaults to LLAMA_PROJECT_NAME or "Default".
        org_id (str): The organization ID. Defaults to LLAMA_ORG_ID env var.
        api_key (str): Your Llama Cloud API key. Defaults to LLAMA_CLOUD_API_KEY env var.
        use_cache (bool): Whether to use/update module-level cache. Defaults to True.
    
    Returns:
        LlamaCloudIndex: The configured index object.
    """
    if use_cache and _cache['index'] is not None:
        return _cache['index']
    
    from llama_index.indices.managed.llama_cloud import LlamaCloudIndex
    
    name = name or get_secret("LLAMA_INDEX_NAME", "NGL_Strategy")
    project_name = project_name or get_secret("LLAMA_PROJECT_NAME", "Default")
    org_id = org_id or get_org_id()
    api_key = api_key or get_api_key()
    
    index = LlamaCloudIndex(
        name=name,
        project_name=project_name,
        organization_id=org_id,
        api_key=api_key,
    )
    
    if use_cache:
        _cache['index'] = index
    
    return index


def create_gemini_llm(model=None, api_key=None, use_cache=True):
    """
    Create and return a Gemini LLM instance.
    
    Uses module-level caching by default to avoid redundant initialization.
    Pass use_cache=False to force creating a new instance.
    
    Args:
        model (str): The model name. Defaults to "models/gemini-2.5-flash".
        api_key (str): Google API key. Defaults to GOOGLE_API_KEY env var.
        use_cache (bool): Whether to use/update module-level cache. Defaults to True.
    
    Returns:
        Gemini: The configured LLM object.
    """
    if use_cache and _cache['llm'] is not None:
        return _cache['llm']
    
    from llama_index.llms.gemini import Gemini
    
    model = model or "models/gemini-2.5-flash"
    api_key = api_key or get_secret("GOOGLE_API_KEY")
    
    llm = Gemini(
        model=model,
        api_key=api_key,
    )
    
    if use_cache:
        _cache['llm'] = llm
    
    return llm


def initialize_settings(llm=None, embed_model=None):
    """
    Initialize global LlamaIndex Settings for consistent configuration.
    
    Call this once at application startup to set the default LLM and
    embedding model used across all LlamaIndex operations.
    
    Args:
        llm: A LlamaIndex LLM object. If None, creates a default Gemini LLM.
        embed_model: An embedding model or string identifier. Defaults to "default".
    """
    from llama_index.core import Settings
    
    if llm is None:
        llm = create_gemini_llm()
    
    Settings.llm = llm
    Settings.embed_model = embed_model or "default"
    logger.info("LlamaIndex Settings initialized successfully.")


# ---------- Document Metadata Parsing ----------

# Regex pattern for ★NO.XXXX Mon DD YYYY (e.g., ★NO.5788 Jun 10 2025)
_DOCUMENT_META_PATTERN = re.compile(r'★NO\.(\d+)\s+(\w{3,9}\s+\d{1,2}\s+\d{4})')


def parse_document_metadata(text):
    """
    Extract document number and creation date from text.
    
    Parses the pattern ★NO.XXXX Mon DD YYYY found on the first page of
    each document (e.g., ★NO.5788 Jun 10 2025).
    
    Args:
        text (str): The text content to search for the metadata pattern.
    
    Returns:
        dict or None: Dictionary with 'no' (int) and 'creation_date' (datetime)
                      keys, or None if the pattern is not found.
    """
    if not text:
        return None
    
    match = _DOCUMENT_META_PATTERN.search(text)
    if not match:
        return None
    
    try:
        doc_no = int(match.group(1))
        date_str = match.group(2)  # e.g., "Jun 10 2025"
        creation_date = datetime.strptime(date_str, "%b %d %Y")
        return {
            'no': doc_no,
            'creation_date': creation_date,
        }
    except (ValueError, TypeError) as e:
        logger.warning(f"Failed to parse document metadata: {e}")
        return None


def _get_node_creation_date(node):
    """
    Extract the CreationDate from a retrieved node.
    
    Checks node metadata first (if previously stored), then falls back
    to parsing the node text for the ★NO pattern.
    
    Args:
        node: A LlamaIndex NodeWithScore object.
    
    Returns:
        datetime or None: The parsed creation date, or None if not found.
    """
    # Check if metadata already has creation_date
    metadata = getattr(node.node, 'metadata', {}) or {}
    if 'creation_date' in metadata:
        val = metadata['creation_date']
        if isinstance(val, datetime):
            return val
        try:
            return datetime.fromisoformat(val)
        except (ValueError, TypeError):
            pass
    
    # Fall back to parsing from node text
    text = node.node.text if hasattr(node.node, 'text') else ''
    parsed = parse_document_metadata(text)
    if parsed:
        return parsed['creation_date']
    
    # Also check the file_name pattern (lpgYYMMDD.pdf -> date)
    file_name = metadata.get('file_name', '')
    fname_match = re.match(r'lpg(\d{2})(\d{2})(\d{2})\.pdf', file_name)
    if fname_match:
        try:
            yy, mm, dd = fname_match.groups()
            return datetime(2000 + int(yy), int(mm), int(dd))
        except ValueError:
            pass
    
    return None


# ---------- Date Priority Node Postprocessor ----------

class DatePriorityPostprocessor:
    """
    Node postprocessor that reorders retrieved nodes by document CreationDate.
    
    Nodes from newer documents are placed first so the LLM synthesizes
    answers prioritizing the most recent information. Nodes without a
    parseable date are placed last.
    
    Usage:
        postprocessor = DatePriorityPostprocessor()
        query_engine = index.as_query_engine(
            node_postprocessors=[postprocessor]
        )
    """
    
    def postprocess_nodes(self, nodes, query_bundle=None, **kwargs):
        """
        Reorder nodes by CreationDate (newest first).
        
        Args:
            nodes: List of NodeWithScore objects from the retriever.
            query_bundle: The query (unused, kept for interface compatibility).
        
        Returns:
            list: Reordered list of NodeWithScore objects.
        """
        def sort_key(node):
            creation_date = _get_node_creation_date(node)
            if creation_date is None:
                # Nodes without dates go last (use earliest possible date)
                return datetime.min
            return creation_date
        
        sorted_nodes = sorted(nodes, key=sort_key, reverse=True)
        
        # Log the reordering for debugging
        for i, node in enumerate(sorted_nodes):
            cd = _get_node_creation_date(node)
            fname = getattr(node.node, 'metadata', {}).get('file_name', 'Unknown')
            logger.debug(
                f"Node {i+1}: {fname}, CreationDate={cd.strftime('%d/%m/%Y') if cd else 'N/A'}"
            )
        
        return sorted_nodes


# ---------- Query Engine Creation ----------

def create_query_engine(
    index=None,
    llm=None,
    similarity_top_k=5,
    response_mode="compact",
    date_priority=True,
    node_postprocessors=None,
    use_cache=True,
):
    """
    Create and return a query engine using the provided index and LLM.
    
    By default, enables date-priority reranking so that chunks from documents
    with the most recent CreationDate are presented to the LLM first. Retrieves
    more candidates (similarity_top_k=5) to ensure good coverage before reranking.
    
    Args:
        index: A LlamaIndex index object. If None, creates a default LlamaCloudIndex.
        llm: A LlamaIndex LLM object. If None, creates a default Gemini LLM.
        similarity_top_k (int): Number of top similar chunks to retrieve. Defaults to 5
            (higher than before to allow date-based reranking across more candidates).
        response_mode (str): How to synthesize the response from retrieved nodes.
            Options: "compact", "refine", "tree_summarize", "simple_summarize",
                     "accumulate", "no_text". Defaults to "compact".
        date_priority (bool): If True, reorder retrieved nodes by CreationDate
            (newest first) before response synthesis. Defaults to True.
        node_postprocessors (list): Additional node postprocessors to apply.
            The DatePriorityPostprocessor is prepended if date_priority=True.
        use_cache (bool): Whether to use/update module-level cache. Defaults to True.
    
    Returns:
        QueryEngine: The configured query engine.
    """
    if use_cache and _cache['query_engine'] is not None:
        return _cache['query_engine']
    
    if index is None:
        index = create_llama_cloud_index()
    if llm is None:
        llm = create_gemini_llm()
    
    # Build postprocessor list
    postprocessors = []
    if date_priority:
        postprocessors.append(DatePriorityPostprocessor())
    if node_postprocessors:
        postprocessors.extend(node_postprocessors)
    
    query_engine = index.as_query_engine(
        llm=llm,
        similarity_top_k=similarity_top_k,
        response_mode=response_mode,
        node_postprocessors=postprocessors if postprocessors else None,
    )
    
    if use_cache:
        _cache['query_engine'] = query_engine
    
    return query_engine


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
    
    Extracts comprehensive metadata including rank, page labels, document number,
    creation date, and truncated text from each source node.
    
    Args:
        response: The response object from a query engine.
        max_text_length (int): Maximum characters to include from source text.
    
    Returns:
        list: List of dictionaries containing source information with keys:
              'rank', 'file_name', 'page', 'doc_no', 'creation_date', 'score', 'text'.
    """
    sources = []
    if hasattr(response, "source_nodes"):
        for i, node in enumerate(response.source_nodes):
            text = node.node.text if hasattr(node.node, 'text') else ''
            
            # Parse document metadata (No and CreationDate)
            parsed_meta = parse_document_metadata(text)
            creation_date = _get_node_creation_date(node)
            
            source_info = {
                'rank': i + 1,
                'file_name': node.node.metadata.get('file_name', 'Unknown'),
                'page': node.node.metadata.get('page_label'),
                'doc_no': parsed_meta['no'] if parsed_meta else None,
                'creation_date': creation_date.strftime('%d/%m/%Y') if creation_date else None,
                'score': node.score if hasattr(node, 'score') else None,
                'text': text[:max_text_length] + ('...' if len(text) > max_text_length else '')
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
