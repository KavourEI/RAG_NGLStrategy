import os
from dotenv import load_dotenv
import requests
import json
from llama_index.indices.managed.llama_cloud import LlamaCloudIndex

# Load environment variables once at module level
load_dotenv()


def get_pipeline_files(pipeline_id=None, api_key=None, base_url=None):
    """
    Get files from a LlamaIndex Cloud pipeline.

    Args:
        pipeline_id (str): The ID of the pipeline. Defaults to LLAMA_NGL_PIPELINE_ID env var.
        api_key (str): Your Llama Cloud API key. Defaults to LLAMA_CLOUD_API_KEY env var.
        base_url (str): Base URL for the API. Defaults to LLAMA_BASE_URL env var.

    Returns:
        dict: JSON response containing pipeline files data

    Raises:
        ValueError: If required parameters are missing
        requests.RequestException: If the HTTP request fails
    """
    # Load values from environment if not provided
    pipeline_id = pipeline_id or os.getenv("LLAMA_NGL_PIPELINE_ID")
    api_key = api_key or os.getenv("LLAMA_CLOUD_API_KEY")
    base_url = base_url or os.getenv("LLAMA_BASE_URL")

    # Validate required parameters
    if not pipeline_id:
        raise ValueError("Pipeline ID is required. Set LLAMA_NGL_PIPELINE_ID in .env or pass as argument")

    if not api_key:
        raise ValueError("API key is required. Set LLAMA_CLOUD_API_KEY in .env or pass as argument")

    if not base_url:
        # Default to the original URL if not specified
        base_url = "https://api.cloud.llamaindex.ai/api/v1"

    # Construct URL
    url = f"{base_url}/pipelines/{pipeline_id}/files"

    # Prepare headers
    headers = {
        'Accept': 'application/json',
        'Authorization': f'Bearer {api_key}'
    }

    try:
        # Make the request
        response = requests.get(url, headers=headers, timeout=30)
        response.raise_for_status()

        # Return parsed JSON
        return response.json()

    except requests.RequestException as e:
        print(f"Error making request to {url}: {e}")
        raise
    except json.JSONDecodeError as e:
        print(f"Error parsing JSON response: {e}")
        raise


def upload_file_to_pipeline(name=None, project_name=None, org_id=None,
                            api_key=None, file_path=None):
    """
    Upload a file to a LlamaIndex Cloud pipeline.

    Args:
        name (str): The name of the index. Defaults to LLAMA_INDEX_NAME env var.
        project_name (str): The name of the project. Defaults to LLAMA_PROJECT_NAME env var.
        org_id (str): The organization ID. Defaults to LLAMA_ORG_ID env var.
        api_key (str): Your Llama Cloud API key. Defaults to LLAMA_CLOUD_API_KEY env var.
        file_path (str): Path to the file to upload. Required.

    Returns:
        dict: Upload result from LlamaCloudIndex

    Raises:
        ValueError: If required parameters are missing
        FileNotFoundError: If file_path doesn't exist
        Exception: For other upload errors
    """
    # Load values from environment if not provided
    name = name or os.getenv("LLAMA_INDEX_NAME")
    project_name = project_name or os.getenv("LLAMA_PROJECT_NAME")
    org_id = org_id or os.getenv("LLAMA_ORG_ID")
    api_key = api_key or os.getenv("LLAMA_CLOUD_API_KEY")

    # Validate required parameters
    if not name:
        raise ValueError("Index name is required. Set LLAMA_INDEX_NAME in .env or pass as argument")

    if not project_name:
        raise ValueError("Project name is required. Set LLAMA_PROJECT_NAME in .env or pass as argument")

    if not org_id:
        raise ValueError("Organization ID is required. Set LLAMA_ORG_ID in .env or pass as argument")

    if not api_key:
        raise ValueError("API key is required. Set LLAMA_CLOUD_API_KEY in .env or pass as argument")

    if not file_path:
        raise ValueError("File path is required to upload a file!")

    if not os.path.exists(file_path):
        raise FileNotFoundError(f"File not found: {file_path}")

    try:
        # Create index and upload file
        index = LlamaCloudIndex(
            name=name,
            project_name=project_name,
            organization_id=org_id,
            api_key=api_key,
        )

        # Assuming upload_file returns something - you might need to check LlamaCloudIndex docs
        result = index.upload_file(file_path=file_path)
        return result

    except Exception as e:
        print(f"Error uploading file {file_path}: {e}")
        raise


def delete_pipeline_file(pipeline_id=None, file_id=None, api_key=None, base_url=None):
    """
    Delete a file from a LlamaIndex Cloud pipeline.

    Args:
        pipeline_id (str): The ID of the pipeline. Defaults to LLAMA_NGL_PIPELINE_ID env var.
        file_id (str): The ID of the file to delete. Required.
        api_key (str): Your Llama Cloud API key. Defaults to LLAMA_CLOUD_API_KEY env var.
        base_url (str): Base URL for the API. Defaults to LLAMA_BASE_URL env var.

    Returns:
        dict: JSON response containing deletion result

    Raises:
        ValueError: If required parameters are missing
        requests.RequestException: If the HTTP request fails
    """
    # Load values from environment if not provided
    pipeline_id = pipeline_id or os.getenv("LLAMA_NGL_PIPELINE_ID")
    api_key = api_key or os.getenv("LLAMA_CLOUD_API_KEY")
    base_url = base_url or os.getenv("LLAMA_BASE_URL")

    # Validate required parameters
    if not pipeline_id:
        raise ValueError("Pipeline ID is required. Set LLAMA_NGL_PIPELINE_ID in .env or pass as argument")

    if not file_id:
        raise ValueError("File ID is required to delete a file!")

    if not api_key:
        raise ValueError("API key is required. Set LLAMA_CLOUD_API_KEY in .env or pass as argument")

    if not base_url:
        base_url = "https://api.cloud.llamaindex.ai/api/v1"

    # Construct URL
    url = f"{base_url}/pipelines/{pipeline_id}/files/{file_id}"

    # Prepare headers
    headers = {
        'Authorization': f'Bearer {api_key}'
    }

    try:
        # Make the request using requests library (consistent with other functions)
        response = requests.delete(url, headers=headers, timeout=30)
        response.raise_for_status()

        # Return response if successful
        if response.status_code == 204:  # No Content
            return {"success": True, "message": f"File {file_id} deleted successfully"}

        try:
            return response.json()
        except json.JSONDecodeError:
            return {"success": True, "status_code": response.status_code}

    except requests.RequestException as e:
        print(f"Error deleting file {file_id}: {e}")
        raise

