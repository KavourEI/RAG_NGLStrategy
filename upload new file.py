import os
from llama_cloud import LlamaCloud
from dotenv import load_dotenv
load_dotenv()
client = LlamaCloud(api_key=os.getenv("LLAMA_CLOUD_API_KEY"))


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
