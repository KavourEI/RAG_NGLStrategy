import os
from llama_cloud.client import LlamaCloud
from dotenv import load_dotenv
load_dotenv()
client = LlamaCloud(token=os.getenv("LLAMA_CLOUD_API_KEY"))


file_obj = client.files.create(file="/Users/kavour/Documents/NGL_RAG/Rag_v1/data/lpg250630.pdf", purpose='user_data')
print(file_obj.id)

from llama_cloud_services import LlamaCloudIndex


index = LlamaCloudIndex(
  name="NGL_Strategy",
  project_name="Default",
  organization_id="44ae1ea1-e4cb-4a16-b55e-9024ef961a7c",
  api_key=os.getenv("LLAMA_CLOUD_API_KEY"),
)

index.upload_file(file_path="/Users/kavour/Documents/NGL_RAG/Rag_v1/data/lpg250630.pdf",)



#### Download a list of all files used in the LlamaCloudIndex

import requests
import json

pipeline_id = "70fa557d-916f-4372-9dd7-d85457059f10"
url = f"https://api.cloud.llamaindex.ai/api/v1/pipelines/{pipeline_id}/files2"

payload = {}
headers = {
  'Accept': 'application/json',
  'Authorization': f'Bearer {os.getenv("LLAMA_CLOUD_API_KEY")}'
}

response = requests.request("GET", url, headers=headers, data=payload)

data_test = json.loads(response.content.decode('utf-8'))
data_test['files'][0]['name']