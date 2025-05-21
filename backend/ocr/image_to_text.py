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

    1. 完整性要求（最重要）：
       - 严格保持所有原始内容，不允许任何信息丢失
       - 特别注意保持所有标题的完整性，如"选项一"、"选项二"等
       - 保持所有括号内的补充说明，如"（见折叠边）"等
       - 保持所有数字和符号的原始形式，包括"x"等特殊字符
       - 不允许删除或合并任何内容，即使看起来是重复的

    2. 上下文理解：
       - 这是一个编织图解文本，包含针法说明、尺寸数据等专业内容
       - 特别注意识别编织相关的专业术语，如"上针"、"下针"、"空加针"等
       - 数字通常表示针数、行数或尺寸，需要保持其准确性
       - 括号内的数字序列通常表示不同尺寸的对应数据

    3. 页眉页脚处理：
       - 识别并删除每页重复出现的页眉、页脚、页码等无关内容
       - 页眉示例：如"V: WDmaoxianwo 我的毛线窝翻译——《大吉岭》背心"
       - 页脚示例：如"见小红书号;2639400533 淘宝和微店: 我的毛线窝"
       - 注意：页眉页脚可能包含社交媒体账号、店铺信息、页码等，这些都需要删除

    4. 专业术语识别：
       - 结合上下文识别并纠正编织术语
       - 常见术语示例：
         * 针法：上针、下针、空加针、并针、挑针等
         * 部位：前片、后片、袖笼、领口等
         * 工具：环针、棒针等
       - 注意数字和单位的组合，如"3.5mm环针"、"185针"等

    5. 段落结构保持：
       - 严格保持原有的段落结构和换行
       - 每个编织步骤应该单独成段
       - 保持标题的层级结构（如"选项一"、"选项二"等）
       - 保持数字序列的格式，如"185 (203 - 221 - 239 - 257 - 293 - 311 - 329)针"

    6. 特别注意事项：
       - 不要修改任何以"选项"或"第X行"开头的内容
       - 不要合并或删除任何段落
       - 保持数字的准确性，特别是括号内的尺寸数据
       - 保持专业术语的准确性，不要随意替换
       - 保持所有补充说明的完整性，如"（见折叠边）"等
       - 保持所有特殊字符，如"x"等

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
    custom_config = r'--oem 3 --psm 6 -c preserve_interword_spaces=1 -c textord_heavy_nr=1 -c textord_min_linesize=2.5 -c textord_force_make_prop_words=0 -c textord_force_make_prop_fract=0 -c textord_parallel_baselines=1 -c textord_parallel_desc=1'
    
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
            
            # 清理文本，但保持所有原始内容
            # 1. 保持所有原始换行和空格
            # 2. 只处理明显的OCR错误，如多余的空格
            text = re.sub(r'(?<=\S) {2,}(?=\S)', ' ', text)  # 只处理行内多余的空格
            
            # 3. 保持所有数字和符号的原始形式
            # 4. 保持所有括号和补充说明
            text = re.sub(r'(\d+)\s*[（(]\s*(\d+)', r'\1 (\2', text)  # 只处理数字和括号之间的空格
            
            # 5. 保护标题格式
            text = re.sub(r'选项\s*(\d+)\s*:', r'选项\1:', text)  # 修复选项标题格式
            
            # 6. 保护数字和单位
            text = re.sub(r'(\d+)\s*个', r'\1个', text)  # 修复数字和"个"之间的空格
            text = re.sub(r'(\d+)\s*行', r'\1行', text)  # 修复数字和"行"之间的空格
            text = re.sub(r'(\d+)\s*针', r'\1针', text)  # 修复数字和"针"之间的空格
            
            # 7. 保护括号内的内容
            text = re.sub(r'[（(]\s*([^）)]+)\s*[）)]', r'(\1)', text)  # 统一括号格式
            
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