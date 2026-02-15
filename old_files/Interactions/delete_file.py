import os
from dotenv import load_dotenv
load_dotenv()
import http.client

api_key = os.getenv("LLAMA_CLOUD_API_KEY")
pipe_id = os.getenv("LLAMA_NGL_PIPELINE_ID")

file_id = '97b39d52-c7b2-468a-87d6-35a84f6a989a'

conn = http.client.HTTPSConnection("api.cloud.llamaindex.ai")
payload = ''
headers = {
  'Authorization': f'Bearer {api_key}'
}
conn.request("DELETE", f"/api/v1/pipelines/{pipe_id}/files/{file_id}", payload, headers)
res = conn.getresponse()
data = res.read()
print(data.decode("utf-8"))


import requests

url = f"https://api.cloud.llamaindex.ai/api/v1/pipelines/{pipe_id}/files/{file_id}"
headers = {"Authorization": f"Bearer {api_key}"}

response = requests.delete(url, headers=headers)
if response.status_code == 204:
    print("File deleted successfully.")
else:
    print("Error:", response.status_code, response.text)

url_sync = f"https://api.cloud.llamaindex.ai/api/v1/pipelines/{pipe_id}/sync"
headers = {"Authorization": f"Bearer {api_key}"}

response = requests.post(url_sync, headers=headers)
if response.status_code == 200:
    print("Pipeline synced successfully.")
else:
    print("Error:", response.status_code, response.text)


### Deepseek Test

from llama_index.indices.managed.llama_cloud import LlamaCloudIndex
import os
from dotenv import load_dotenv
load_dotenv()

# Assuming you have your index configured
index = LlamaCloudIndex(
    name=os.getenv("LLAMA_INDEX_NAME"),
    project_name=os.getenv("LLAMA_PROJECT_NAME"),
    organization_id=os.getenv("LLAMA_ORG_ID"),
    api_key=os.getenv("LLAMA_CLOUD_API_KEY")
)

# List all documents to find what you want to delete
all_docs = index.ref_doc_info
list(all_docs.keys())[0]
print("Available documents:", all_docs.keys())
all_docs['ed24935bc4ac4ab9feb5500eaefae41c15bdf69591b70880cd']['metadata']
doc = next(iter(all_docs.values()))
doc.metadata['id']
# Delete a specific document
document_id_to_delete = 'ed24935bc4ac4ab9feb5500eaefae41c15bdf69591b70880cd'
index.delete_ref_doc(document_id_to_delete, delete_from_docstore=True)

# Verify deletion
updated_docs = index.ref_doc_info
print(f"Document {document_id_to_delete} deleted. Remaining: {updated_docs.keys()}")

target_id = "14_Pazzaglia_23.pdf"

doc_key = next(
    key for key, value in all_docs.items()
    if value.metadata.get("id") == target_id
)

print(doc_key)
'2626fd6e-6ab5-45c3-8ddc-829c027c2d58'