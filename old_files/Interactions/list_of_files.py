import os
from dotenv import load_dotenv
import requests
import json
load_dotenv()

pipeline_id = "70fa557d-916f-4372-9dd7-d85457059f10"
url = f"https://api.cloud.llamaindex.ai/api/v1/pipelines/{pipeline_id}/files"

payload = {}
headers = {
  'Accept': 'application/json',
  'Authorization': f'Bearer {os.getenv("LLAMA_CLOUD_API_KEY")}'
}

response = requests.request("GET", url, headers=headers, data=payload)
data_test = json.loads(response.content.decode('utf-8'))

data_test
# data_test['files'][0]['name']


# Test ---> 6a34c1e7-0b16-4c4e-9902-271de743c2fc



