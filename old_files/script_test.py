import os
from llama_cloud.client import LlamaCloud
from dotenv import load_dotenv
load_dotenv()
client = LlamaCloud(token=os.getenv("LLAMA_CLOUD_API_KEY"))


file_obj = client.files.create(file="/Users/kavour/Documents/NGL_RAG/Rag_v1/data/lpg250630.pdf", purpose='user_data')
print(file_obj.id)

from old_files.llama_cloud_services import LlamaCloudIndex


index = LlamaCloudIndex(
  name="NGL_Strategy",
  project_name="Default",
  organization_id="44ae1ea1-e4cb-4a16-b55e-9024ef961a7c",
  api_key=os.getenv("LLAMA_CLOUD_API_KEY"),
)

index.upload_file(file_path="/Users/kavour/Documents/NGL_RAG/Rag_v1/data/lpg250630.pdf",)



#### Delete data form LLamaCloud Index ####

## V1 Seems to work but it loads for ever
api_key = os.getenv("LLAMA_CLOUD_API_KEY")
file_id =  '08f568c9-0fa8-43f8-aca9-69a1378931bc'# Replace with the actual file ID
pipeline_id = "70fa557d-916f-4372-9dd7-d85457059f10"

from llama_index.indices.managed.llama_cloud import LlamaCloudIndex

index = LlamaCloudIndex("70fa557d-916f-4372-9dd7-d85457059f10", project_name="Default")  # Use your Index ID/name
ref_doc_info = index.ref_doc_info  # Dict of {ref_doc_id: metadata}
print(list(ref_doc_info.keys()))  # Lists available file ref_doc_ids

ref_doc_id = "5ea457dcbb6f8a027d93f5cb9d3f8382bc916fb3099363ae4b"  # Replace with actual ID

index.delete_ref_doc(
    ref_doc_id=ref_doc_id,
    delete_from_docstore=True,  # Ensures full removal (nodes + docstore)
    verbose=True  # Logs progress
)

ref_doc_info
{'780232948c0d493c7ef79aac7ed850a73caf33ca62dd15165f': RefDocInfo(node_ids=[], metadata={'id': 'current.pdf', 'file_size': 1092590, 'last_modified_at': '2026-01-14T16:20:54', 'file_path': 'current.pdf', 'file_name': 'current.pdf', 'external_file_id': 'current.pdf', 'file_id': '6a34c1e7-0b16-4c4e-9902-271de743c2fc', 'pipeline_file_id': '4e510110-7e61-43fe-a214-dba49353fe57', 'pipeline_id': '70fa557d-916f-4372-9dd7-d85457059f10'}),
 '5ea457dcbb6f8a027d93f5cb9d3f8382bc916fb3099363ae4b': RefDocInfo(node_ids=[], metadata={'id': 'lpg250630.pdf', 'file_size': 1101965, 'last_modified_at': '2026-02-03T14:19:31', 'file_path': 'lpg250630.pdf', 'file_name': 'lpg250630.pdf', 'external_file_id': 'lpg250630.pdf', 'file_id': '55773df3-2d26-407d-bdfb-1ccc796e4379', 'pipeline_file_id': '08f568c9-0fa8-43f8-aca9-69a1378931bc', 'pipeline_id': '70fa557d-916f-4372-9dd7-d85457059f10'})}

## V2
import requests
import os

api_key = os.getenv("LLAMA_CLOUD_API_KEY")
pipeline_id = "70fa557d-916f-4372-9dd7-d85457059f10"
doc_id = '5ea457dcbb6f8a027d93f5cb9d3f8382bc916fb3099363ae4b'

response = requests.delete(
    f"https://api.cloud.llamaindex.ai/api/v1/pipelines/{pipeline_id}/documents/{doc_id}",
    headers={"x-api-key": api_key}
)
print(response.status_code)  # 204 success

import requests

API_KEY = api_key
FILE_ID = "lpg250630.pdf"  # e.g., from File Metadata
BASE_URL = "https://api.cloud.llamaindex.ai/v1"

headers = {
    "x-api-key": API_KEY,
    "Content-Type": "application/json"
}

response = requests.delete(f"{BASE_URL}/files/{FILE_ID}", headers=headers)

if response.status_code == 204:
    print("File deleted successfully!")
elif response.status_code == 404:
    print("File not found (already gone or wrong ID).")
else:
    print(f"Error: {response.status_code}, {response.text}")


url = f"https://api.cloud.llamaindex.ai/api/v1/pipelines/{pipeline_id}/documents"
headers = {
    'Accept': 'application/json',
    'Authorization': f'Bearer {os.getenv("LLAMA_CLOUD_API_KEY")}'
}
response = requests.get(url, headers=headers)
documents = response.json()
print([doc["id"] for doc in documents])


import requests
import os

pipeline_id = pipeline_id
document_id = '780232948c0d493c7ef79aac7ed850a73caf33ca62dd15165f'
url = f"https://api.cloud.llamaindex.ai/api/v1/pipelines/{pipeline_id}/documents/{document_id}"
headers = {
    'Authorization': f'Bearer {os.getenv("LLAMA_CLOUD_API_KEY")}',
}

response = requests.delete(url, headers=headers)
print(response.status_code)  # 204 means success

index.delete_ref_doc("5ea457dcbb6f8a027d93f5cb9d3f8382bc916fb3099363ae4b", delete_from_docstore=True, verbose=True)

data_test
{'files':
     [{'id': '08f568c9-0fa8-43f8-aca9-69a1378931bc', 'name': 'lpg250630.pdf', 'external_file_id': 'lpg250630.pdf', 'file_size': 1101965, 'file_type': 'pdf', 'project_id': '7009d266-1b7a-4ae6-a250-3544c12894f1', 'last_modified_at': '2026-02-03T14:19:31.867925Z', 'file_id': '55773df3-2d26-407d-bdfb-1ccc796e4379', 'pipeline_id': '70fa557d-916f-4372-9dd7-d85457059f10', 'resource_info': {'id': 'lpg250630.pdf', 'file_size': 1101965, 'last_modified_at': '2026-02-03T14:19:31'}, 'permission_info': None, 'custom_metadata': {}, 'data_source_id': None, 'config_hash': {'parsing_config_hash': '1c9c2bd1e2c03cd5704ed8be0b6ded072b658148f51441463d', 'embedding_config_hash': '2ad2e188cded9622db27e8566a3dec31f3f0a099f291446bcd', 'transform_config_hash': 'eb1c62554eaa6720e8b55e5a59cc9d9a76954563968f9d5148'}, 'indexed_page_count': 26, 'status': 'SUCCESS', 'status_updated_at': '2026-02-04T13:02:30.438069', 'created_at': '2026-02-03T14:19:31.294873Z', 'updated_at': '2026-02-04T13:13:29.556729Z'},
      {'id': '4e510110-7e61-43fe-a214-dba49353fe57', 'name': 'current.pdf', 'external_file_id': 'current.pdf', 'file_size': 1092590, 'file_type': 'pdf', 'project_id': '7009d266-1b7a-4ae6-a250-3544c12894f1', 'last_modified_at': '2026-01-14T16:20:55.157251Z', 'file_id': '6a34c1e7-0b16-4c4e-9902-271de743c2fc', 'pipeline_id': '70fa557d-916f-4372-9dd7-d85457059f10', 'resource_info': {'id': 'current.pdf', 'file_size': 1092590, 'last_modified_at': '2026-01-14T16:20:54'}, 'permission_info': None, 'custom_metadata': {}, 'data_source_id': None, 'config_hash': {'parsing_config_hash': '1c9c2bd1e2c03cd5704ed8be0b6ded072b658148f51441463d', 'embedding_config_hash': '2ad2e188cded9622db27e8566a3dec31f3f0a099f291446bcd', 'transform_config_hash': 'eb1c62554eaa6720e8b55e5a59cc9d9a76954563968f9d5148'}, 'indexed_page_count': 24, 'status': 'SUCCESS', 'status_updated_at': '2026-02-04T12:51:38.032225', 'created_at': '2026-01-14T16:20:54.636999Z', 'updated_at': '2026-02-04T13:13:29.552792Z'}], 'limit': 2, 'offset': 0, 'total_count': 2}
