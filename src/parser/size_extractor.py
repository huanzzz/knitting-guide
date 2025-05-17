import re
from typing import Dict, List, Tuple
import openai
import os
from dotenv import load_dotenv

class SizeExtractor:
    def __init__(self):
        # 加载环境变量
        load_dotenv()
        # 初始化 OpenAI 客户端
        self.client = openai.OpenAI(api_key=os.getenv('OPENAI_API_KEY'))
    
    def extract_second_size(self, text: str) -> str:
        """
        使用 AI 从文本中提取括号中的第一个数字，并保留其他文本内容
        """
        prompt = f"""
        请处理以下文本，将括号中的第一个数字替换到原文本中。
        
        规则：
        1. 对于形如 "a(b-c-d-e-f-g)" 的格式，提取第一个数字 "b"
        2. 保留括号外的所有文本内容
        3. 如果一行中有多个括号，分别处理每个括号
        4. 注意处理各种格式，如：
           - 数字在前：370 (406 - 442 - 478 - 514 - 586 - 622 - 658) -> 370 (406)
           - 文字在前：第72 (72 - 78 - 84 - 84 - 84 - 92 - 92)行 -> 第72行
           - 多个括号：第72 (72 - 78)行和第92 (82 - 100)行 -> 第72行和第82行
           - 带单位：剩51 (56 - 65 - 71 - 81 - 87 - 92)针 -> 剩56针
        
        示例：
        输入：第72 (72 - 78 - 84 - 84 - 84 - 92 - 92)行和第92 (82 - 100 - 102 - 102 - 102 - 112 - 112) 行各增加一个扣眼
        输出：第72行和第82 行各增加一个扣眼
        
        输入：用 3.5mm 环针，起 370 (406 - 442 - 478 - 514 - 586 - 622 - 658)针
        输出：用 3.5mm 环针，起 406针
        
        输入：第 20 到 59 (59 - 63 - 67 - 67 - 67 - 73 - 73) 行织平针
        输出：第 20 到 59 行织平针
        
        请处理以下文本：
        {text}
        """
        
        try:
            response = self.client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "你是一个专门用于处理编织图解的助手。请按照规则提取括号中的第一个数字，并保留其他文本内容。注意处理各种格式的括号数字序列。"},
                    {"role": "user", "content": prompt}
                ],
                temperature=0
            )
            return response.choices[0].message.content.strip()
        except Exception as e:
            print(f"AI 处理出错: {e}")
            return text
    
    def process_knitting_pattern(self, pattern_text: str) -> str:
        """
        处理编织图解文本，提取括号中的第一个数字
        """
        lines = pattern_text.split('\n')
        processed_lines = []
        for line in lines:
            if '(' in line or '（' in line:  # 简单检查是否包含括号
                processed_line = self.extract_second_size(line)
                processed_lines.append(processed_line)
            else:
                processed_lines.append(line)
        return '\n'.join(processed_lines) 