import os
from dotenv import load_dotenv
load_dotenv()


from old_files.llama_cloud_services import LlamaCloudIndex
name = os.getenv("LLAMA_INDEX_NAME")
project_name = os.getenv("LLAMA_PROJECT_NAME")
org_id = os.getenv("LLAMA_ORG_ID")
api_key = os.getenv("LLAMA_CLOUD_API_KEY")

index = LlamaCloudIndex(
  name=name,
  project_name=project_name,
  organization_id=org_id,
  api_key=api_key,
)

index.upload_file(file_path="data/current.pdf",)
