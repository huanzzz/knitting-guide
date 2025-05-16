import os
from dotenv import load_dotenv
from google import genai
from PIL import Image
import pytesseract
import glob
from tqdm import tqdm
import re

# 加载环境变量
load_dotenv()

# 获取项目根目录
ROOT_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

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
    使用 Gemini 处理文本，只处理页眉页脚和术语纠错
    """
    prompt = """
    你是一个专业的编织图解处理助手。请帮我处理以下文本，要求：

    1. 页眉页脚处理：
       - 严格识别并删除每页重复出现的页眉、页脚、页码等无关内容
       - 页眉示例：如"V: WDmaoxianwo 我的毛线窝翻译——《大吉岭》衣心"
       - 页脚示例：如"见小红书号;2639400533 淘宝和微店: 我的毛线帘"
       - 注意：页眉页脚可能包含社交媒体账号、店铺信息、页码等，这些都需要删除
       - 如果发现某行内容在多个页面重复出现，且与编织内容无关，应视为页眉页脚并删除

    2. 专有名词和常见术语纠错：
       - 遇到下列常见词汇时请自动纠正为标准写法：
         * "林迪" → "朱迪"
         * "衣刁" → "衣身"
         * "折灵边" → "折叠边"
         * "大言岭" → "大吉岭"
         * 其他常见编织术语请结合上下文自动修正

    3. 符号纠错：
       - 检查并修正常见符号识别错误，如：
         * 圆括号"（）"
         * 书名号"《》"
         * 其他常见符号

    4. 特别要求：
       - 保持原有的段落结构和换行
       - 不要修改任何标题格式
       - 不要删除任何以"选项"或"第X行"开头的内容
       - 不要合并或删除任何段落

    文本内容：
    {text}
    只输出处理后的文本内容，不要回复任何额外说明、请求或客套话。
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

def preprocess_image(image):
    """
    预处理图片以提高OCR识别率
    """
    # 转换为灰度图
    if image.mode != 'L':
        image = image.convert('L')
    
    # 增加对比度
    from PIL import ImageEnhance
    enhancer = ImageEnhance.Contrast(image)
    image = enhancer.enhance(2.0)
    
    return image

def images_to_text(image_dir):
    """
    处理图片并提取文本，所有页合并后统一处理
    """
    client = setup_gemini()
    all_text = []
    image_files = sorted(glob.glob(os.path.join(image_dir, '*.png')))
    
    # OCR配置
    custom_config = r'--oem 3 --psm 6 -c preserve_interword_spaces=1 -c textord_heavy_nr=1 -c textord_min_linesize=2.5'
    
    for img_path in tqdm(image_files, desc="处理图片"):
        try:
            # 打开并预处理图片
            image = Image.open(img_path)
            image = preprocess_image(image)
            
            # 使用 pytesseract 进行OCR识别
            text = pytesseract.image_to_string(
                image,
                lang='chi_sim',
                config=custom_config
            )
            
            # 清理文本
            # 1. 保留段落之间的空行
            text = re.sub(r'\n\s*\n', '\n\n', text)
            # 2. 移除多余的空格
            text = re.sub(r' +', ' ', text)
            # 3. 确保段落之间有正确的空行
            text = re.sub(r'\n{3,}', '\n\n', text)
            
            all_text.append(text)
        except Exception as e:
            print(f"处理图片 {img_path} 时出错: {e}")
            continue
    
    # 合并所有页的文本，保持段落结构
    merged_text = '\n\n'.join(all_text)
    
    # 用Gemini处理页眉页脚和术语纠错
    processed_text = process_text_with_gemini(merged_text, client)
    
    # 确保输出目录存在
    output_dir = os.path.join(ROOT_DIR, 'data', 'processed')
    os.makedirs(output_dir, exist_ok=True)
    
    # 保存所有处理结果到一个文件
    output_file = os.path.join(output_dir, 'all_processed_text.txt')
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(processed_text)
    
    return processed_text

if __name__ == '__main__':
    # 测试代码
    image_dir = os.path.join(ROOT_DIR, 'data', 'raw', 'imgs')
    text = images_to_text(image_dir)
    print(text)