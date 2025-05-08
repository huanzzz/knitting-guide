from pdf_to_images import pdf_to_images
from image_to_text import images_to_text
from text_to_json import text_to_json
import json

# 1. PDF转图片
image_paths = pdf_to_images('PDF/大吉岭背心-text.pdf', out_dir='imgs')

# 2. 图片OCR
text = images_to_text('imgs')

# 3. AI解析
json_data = text_to_json(text)

# 4. 保存
with open('result.json', 'w', encoding='utf-8') as f:
    json.dump(json_data, f, ensure_ascii=False, indent=2)