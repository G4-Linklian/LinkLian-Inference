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