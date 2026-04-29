import json
import requests
from PIL import Image
import io

def safe_json_parse(text):
    try:
        return json.loads(text)
    except Exception:
        return None
    return data

def json_all_page(final_result):
  d = ""
  for i, page in enumerate(final_result):
    d += f"page {i+1} : {page} \n"

  return d

def load_pdf_from_url(url):
    res = requests.get(url)
    res.raise_for_status()
    return res.content  

def load_image_from_url(url):
    res = requests.get(url)
    res.raise_for_status()

    image = Image.open(io.BytesIO(res.content))
    return image

def load_text_from_url(url):
    res = requests.get(url)
    res.raise_for_status()
    return res.content.decode("utf-8")

def load_json_from_url(url):
    res = requests.get(url)
    res.raise_for_status()
    return res.json()

def load_page_summary_detail(post_id, top_k_pages):
  final_docs = ""
  for detail in top_k_pages:
    url = f"https://linklianstorage.blob.core.windows.net/ai-summary/summary-post-announcement/each-{post_id}-{detail['file']}-{detail['page']}.json"
    data = load_json_from_url(url)

    final_docs += f"file-{detail['file_name']}, page-{detail['page']} : {data}\n"

  return final_docs