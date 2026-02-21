import http.client
import json
import os
import csv
from dotenv import load_dotenv
load_dotenv()

#### Step 1: Create the extraction agent with the desired configuration.

# conn = http.client.HTTPSConnection("api.cloud.llamaindex.ai")
# payload = json.dumps({
#     "name": "RIM_Extractor_v2",  # Unique name to avoid dupes
#     "data_schema": {
#         "type": "object",
#         "properties": {
#             "Location": {
#                 "type": "string",
#                 "description": "The location in the area of reference"
#             },
#             "Price": {
#                 "type": "string",
#                 "description": "Wholesale Prices (Yuan/mt ex-terminal)"
#             },
#             "Post Prices": {
#                 "type": "string",
#                 "description": "Refinery post prices"
#             }
#         } 
#     },
#     "config": {
#         "chunk_mode": "PAGE",
#         "cite_sources": False,
#         "confidence_scores": False,
#         "extraction_mode": "MULTIMODAL",
#         "extraction_target": "PER_TABLE_ROW",
#         "high_resolution_mode": False,
#         "invalidate_cache": False,
#         "multimodal_fast_mode": False,
#         "num_pages_context": 1,
#         "page_range": "5",
#         "parse_model": "gemini-2.0-flash",   # Use gemini here as well
#         "priority": "critical",
#         "system_prompt": "Extract all the exact infomration from tables with name \"South China\", \"East China\", \"North China\", and \"Northeast China\".",
#         "use_reasoning": False
#     },
# })
# headers = {
#     'Content-Type': 'application/json',
#     'Accept': 'application/json',
#     'Authorization': f'Bearer {os.getenv("LLAMA_CLOUD_API_KEY")}'
# }
# conn.request("POST", "/api/v1/extraction/extraction-agents", payload, headers)
# res = conn.getresponse()
# print("==========================Response from Llama Cloud API=========================")
# print(f"Status: {res.status} {res.reason}")
# print("================================================================================")
# data = res.read()
# print(data.decode("utf-8"))


#### Step 2: Run the extraction agent on a specific file.

# import http.client
# import json

# conn = http.client.HTTPSConnection("api.cloud.llamaindex.ai")
# payload = json.dumps({
#   "extraction_agent_id": "1945d115-2c9c-4f44-9284-408c331ac4f5",
#   "file_id": "f9a7abe2-0ad6-44a7-99c7-8e0d256b9282"
# })
# headers = {
#   'accept': 'application/json',
#   'Content-Type': 'application/json',
#   'Authorization': f'Bearer {os.getenv("LLAMA_CLOUD_API_KEY")}'
# }
# conn.request("POST", "/api/v1/extraction/jobs", payload, headers)
# res = conn.getresponse()
# data = res.read()
# print(data.decode("utf-8"))


#### Step 3: Retrieve the results of the extraction job and write to CSV.

# conn = http.client.HTTPSConnection("api.cloud.llamaindex.ai")
# payload = ''
# headers = {
#   'Accept': 'application/json',
#   'Authorization': f'Bearer {os.getenv("LLAMA_CLOUD_API_KEY")}'
# }
# conn.request("GET", "/api/v1/extraction/jobs/a2148af5-85d7-4592-8d0e-a59123272fcf/result", payload, headers)
# res = conn.getresponse()
# data = res.read()
# text = data.decode("utf-8")
# print(text)

# try:
#     payload_obj = json.loads(text)
# except Exception as e:
#     print("Failed to parse JSON response:", e)
#     raise

# rows = payload_obj.get("data", []) or []

# # Map Location values to the requested "Resourse" categories
# def map_resourse(loc):
#     if not isinstance(loc, str):
#         return ""
#     l = loc.strip()
#     south = {"East Guangdong", "Shenzhen", "Guangzhou", "Zhuhai", "Western Guangdong", "Guangxi", "Hainan"}
#     east = {"Jiangsu", "Shanghai", "Zhejiang", "Fujian"}
#     north = {"North-East", "South-East", "Shandong"}
#     northeast = {"Dalian*", "West Liaoning**", "Hei Longjiang***"}
#     rim = {"South China", "East China"}
#     if l in south:
#         return "South China"
#     if l in east:
#         return "East China"
#     if l in north:
#         return "North China"
#     if l in northeast:
#         return "Northeast China"
#     if l in rim:
#         return "Rim China Domestic Index"
#     return ""

# # Ensure output directory exists
# out_dir = os.path.join(os.getcwd(), "data", "extractions")
# os.makedirs(out_dir, exist_ok=True)
# # keep job id in filename when available, else write generic name
# job_id = payload_obj.get("run_id") or payload_obj.get("extraction_metadata", {}).get("parse_job_id") or "unknown"
# out_path = os.path.join(out_dir, f"extraction_{job_id}.csv")

# with open(out_path, "w", newline="", encoding="utf-8") as csvfile:
#     writer = csv.writer(csvfile)
#     writer.writerow(["Resourse", "Location", "Price", "Post Prices"])
#     for r in rows:
#         loc = r.get("Location")
#         res = map_resourse(loc)
#         writer.writerow([res, loc, r.get("Price"), r.get("Post Prices")])

# print(f"Wrote CSV: {out_path}")