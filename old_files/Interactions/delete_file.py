import os
from dotenv import load_dotenv
load_dotenv()
import http.client

api_key = os.getenv("LLAMA_CLOUD_API_KEY")
pipe_id = os.getenv("LLAMA_NGL_PIPELINE_ID")
file_id = '6a34c1e7-0b16-4c4e-9902-271de743c2fc'

conn = http.client.HTTPSConnection("api.cloud.llamaindex.ai")
payload = ''
headers = {
  'Authorization': f'Bearer {api_key}'
}
conn.request("DELETE", f"/api/v1/pipelines/{pipe_id}/files/{file_id}", payload, headers)
res = conn.getresponse()
data = res.read()
print(data.decode("utf-8"))
