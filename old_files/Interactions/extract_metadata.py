import pymupdf
from llama_index.core import SimpleDirectoryReader

def extract_pdf_metadata(file_path):
    doc = pymupdf.open(file_path)
    first_page = doc[0]
    lines = first_page.get_text().splitlines()
    if len(lines) >= 13:
        line = lines[13]
        # Example line: "★NO.5940 Jan 28 2026"
        import re
        match = re.search(r'NO\.(\d+)\s+([A-Za-z]+)\s+(\d{1,2})\s+(\d{4})', line)
        if match:
            no = match.group(1)
            month = match.group(2)
            day = match.group(3)
            year = match.group(4)
            # Convert month name to number
            from datetime import datetime
            month_num = datetime.strptime(month, "%b").month
            cdate = f"{day.zfill(2)}/{str(month_num).zfill(2)}/{year}"
            return {"No": no, "CDate": cdate}
    doc.close()
    return {}

reader = SimpleDirectoryReader(
    input_dir="data_test",
    file_metadata=extract_pdf_metadata
)
docs = reader.load_data()
print(docs[0].metadata)
