import os
from dotenv import load_dotenv
from google import genai
from PIL import Image
import pytesseract
import glob
from tqdm import tqdm

# 加载环境变量
load_dotenv()

def setup_gemini():
    """
    设置 Gemini API
    """
    # 从环境变量获取 API key
    GOOGLE_API_KEY = os.getenv('GOOGLE_API_KEY')
    if not GOOGLE_API_KEY:
        raise ValueError("未找到 GOOGLE_API_KEY 环境变量")
    
    client = genai.Client(api_key=GOOGLE_API_KEY)
    return client

def process_text_with_gemini(text, client):
    """
    使用 Gemini 处理文本，针对编织图解的特点进行优化
    """
    prompt = """
    你是一个专业的编织图解处理助手。请帮我处理以下文本，要求：
    
    1. 段落处理：
       - 将属于同一段的内容合并在一起，不要随意拆分成多行
       - 例如："我的毛线窝翻译——《大言岭》衣心 林迪的魔术起针法: 相关视频见微博或小红书 Figure 8 起针法: 相关视频见微博或小红书 天线尾挑织，相关视频见微博或小红书" 应该保持为一段
       - 只有真正的段落分隔才使用换行
    
    2. 格式规范：
       - 删除页眉页脚、页码等无关内容
       - 删除重复的内容
       - 删除空行和多余的空格
       - 同一段内的内容用空格分隔，不要使用换行符
       - 只有不同段落之间才使用换行分隔
    
    3. 特殊处理：
       - 保持数字和单位的正确格式（如：10针、20行）
       - 保持针法符号的准确性（如：上针、下针、加针、减针等）
       - 保持编织指令的完整性（如：重复、交替等）
    
    4. 结构优化：
       - 保持原文的逻辑顺序
       - 确保每个段落都有明确的主题
       - 保持编织步骤的连贯性
    
    请以清晰的格式返回处理后的文本，注意：
    - 同一段的内容要合并在一起
    - 不要使用 \n\n 这样的换行符
    - 只有真正的段落分隔才使用换行
    
    文本内容：
    {text}
    """
    
    try:
        response = client.models.generate_content(
            model="gemini-2.0-flash",
            contents=prompt.format(text=text)
        )
        return response.text
    except Exception as e:
        print(f"处理文本时出错: {e}")
        return text  # 如果处理失败，返回原始文本

def images_to_text(image_dir):
    """
    处理图片并提取文本
    """
    # 初始化 Gemini
    client = setup_gemini()
    
    all_text = []
    image_files = sorted(glob.glob(os.path.join(image_dir, '*.png')))
    
    for img_path in tqdm(image_files, desc="处理图片"):
        # 使用 pytesseract 进行初步 OCR
        text = pytesseract.image_to_string(Image.open(img_path), lang='chi_sim')
        
        # 使用 Gemini 处理文本
        processed_text = process_text_with_gemini(text, client)
        all_text.append(processed_text)
    
    return '\n\n'.join(all_text)

if __name__ == '__main__':
    # 测试代码
    image_dir = 'imgs'
    text = images_to_text(image_dir)
    print(text)