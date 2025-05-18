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
    
    def normalize_brackets(self, text: str) -> str:
        """
        统一括号格式，将中文括号转换为英文括号
        """
        # 将中文括号转换为英文括号
        text = text.replace('（', '(').replace('）', ')')
        return text

    def is_size_sequence(self, text: str) -> bool:
        """
        判断括号中的内容是否为尺码序列
        """
        # 移除括号（包括中文括号）
        content = text.strip('()（）')
        # 分割内容
        parts = [p.strip() for p in content.split('-')]
        
        # 检查每个部分是否符合尺码格式
        for part in parts:
            # 如果是空或x，跳过
            if not part or part.lower() == 'x':
                continue
            # 检查是否为数字或字母尺码
            if not (part.isdigit() or part.upper() in ['S', 'M', 'L', 'XL', '2XL', '3XL', '4XL']):
                return False
        return True

    def preprocess_text(self, text: str) -> str:
        """
        预处理文本，合并跨行的尺码数据
        """
        # 先统一括号格式
        text = self.normalize_brackets(text)
        
        lines = text.split('\n')
        processed_lines = []
        current_line = ""
        bracket_stack = []  # 用于跟踪括号嵌套
        
        for line in lines:
            # 处理当前行的每个字符
            for char in line:
                if char in ['(', '（']:
                    bracket_stack.append(len(current_line))  # 记录括号开始位置
                    current_line += '('  # 统一使用英文括号
                elif char in [')', '）']:
                    if bracket_stack:  # 如果有未闭合的括号
                        start_pos = bracket_stack.pop()
                        # 提取括号内容
                        bracket_content = current_line[start_pos:]
                        if self.is_size_sequence(bracket_content):
                            # 如果是尺码序列，保持原样
                            current_line += ')'
                        else:
                            # 如果不是尺码序列，保持原样
                            current_line += ')'
                    else:
                        # 没有对应的开始括号，保持原样
                        current_line += ')'
                else:
                    current_line += char
            
            # 如果当前行结束且没有未闭合的括号，添加到处理后的行
            if not bracket_stack:
                processed_lines.append(current_line)
                current_line = ""
            else:
                # 有未闭合的括号，继续处理下一行
                current_line += ' '  # 添加空格连接行
        
        # 处理最后一行
        if current_line:
            processed_lines.append(current_line)
        
        return '\n'.join(processed_lines)
    
    def extract_second_size(self, text: str) -> str:
        """
        使用 AI 从文本中提取括号中的第一个数字作为第二个尺码，并保留其他文本内容
        """
        # 先统一括号格式
        text = self.normalize_brackets(text)
        
        prompt = f"""
        请处理以下文本，将括号中的第一个数字作为第二个尺码替换到原文本中。
        
        规则：
        1. 对于形如 "a(b-c-d-e-f-g)" 的格式，a是第一个数，b是第二个数，所以提取b
        2. 尺码可以是数字（如：8、9、10）或字母（如：S、M、L）
        3. 保留括号外的所有文本内容，不要修改任何其他文本
        4. 如果一行中有多个括号，分别处理每个括号
        5. 注意处理各种格式，如：
           - 数字在前：370 (406 - 442 - 478 - 514 - 586 - 622 - 658) -> 370 406
           - 文字在前：第72 (72 - 78 - 84 - 84 - 84 - 92 - 92)行 -> 第72行
           - 多个括号：第72 (72 - 78)行和第92 (82 - 100)行 -> 第72行和第82行
           - 带单位：剩51 (56 - 65 - 71 - 81 - 87 - 92)针 -> 剩56针
           - 字母尺码：S (M - L - XL - 2XL - 3XL - 4XL) -> S M
           - 换行情况：重复【 】再8 (9 - 10 - 11 - 11 - 14 - 15 - 16) 次 -> 重复【 】再9次
           - 特殊格式：x (x-x-66-66-66-72-72) -> x
           - 多个尺码：行32 (32 - 34 - 30 - 30 - 30 - 32 - 32)，52 (52 - 56 - 48 - 48 - 48 - 52 - 52)和x (x-x-66-66-66-72-72) (扣眼行) -> 行32，52 和x(扣眼行)
        
        重要规则：
        1. 不要修改任何非尺码相关的文本内容
        2. 不要删除任何括号，除非是尺码括号
        3. 不要修改任何技术术语（如"左上2并1"、"右上2并1"等）
        4. 如果括号中的内容不是尺码序列，则保持原样
        5. 如果括号中的值是x，把x当成一个数字提取
        6. 当提取尺码时，不要保留括号，直接使用数字
        7. 如果一行中有多个尺码，每个尺码都单独处理，但保持它们的连接关系
        
        示例：
        输入：第72 (72 - 78 - 84 - 84 - 84 - 92 - 92)行和第92 (82 - 100 - 102 - 102 - 102 - 112 - 112) 行各增加一个扣眼
        输出：第72行和第82 行各增加一个扣眼
        
        输入：用 3.5mm 环针，起 370 (406 - 442 - 478 - 514 - 586 - 622 - 658)针
        输出：用 3.5mm 环针，起 406针
        
        输入：第 20 到 59 (59 - 63 - 67 - 67 - 67 - 73 - 73) 行织平针
        输出：第 20 到 59 行织平针
        
        输入：重复【 】再8 (9 - 10 - 11 - 11 - 14 - 15 - 16) 次
        输出：重复【 】再9次
        
        输入：(左上2并1) 3次，(空加针，1 下) 5 次，空加针，(右上2并1)3次
        输出：(左上2并1) 3次，(空加针，1 下) 5 次，空加针，(右上2并1)3次
        
        输入：第x (x-x-66-66-66-72-72)行
        输出：第x行
        
        输入：行32 (32 - 34 - 30 - 30 - 30 - 32 - 32)，52 (52 - 56 - 48 - 48 - 48 - 52 - 52)和x (x-x-66-66-66-72-72) (扣眼行)
        输出：行32，52 和x(扣眼行)
        
        请处理以下文本：
        {text}
        """
        
        try:
            response = self.client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "你是一个专门用于处理编织图解的助手。你的任务是提取括号中的第一个数字作为第二个尺码，并保留其他所有文本内容不变。不要修改任何技术术语，不要删除任何非尺码相关的括号。注意处理各种格式的尺码序列，包括数字和字母尺码，以及可能跨行的尺码序列。如果括号中的值是x，把x当成一个数字提取。当提取尺码时，不要保留括号，直接使用数字。如果一行中有多个尺码，每个尺码都单独处理，但保持它们的连接关系。"},
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
        # 预处理文本，合并跨行的尺码数据
        processed_text = self.preprocess_text(pattern_text)
        
        lines = processed_text.split('\n')
        processed_lines = []
        for line in lines:
            if '(' in line:  # 检查是否包含括号（现在只检查英文括号，因为已经统一了格式）
                processed_line = self.extract_second_size(line)
                processed_lines.append(processed_line)
            else:
                processed_lines.append(line)
        return '\n'.join(processed_lines)

def main():
    """从文本文件中提取尺码"""
    # 固定的输入输出路径
    input_file = '/Users/hw/Desktop/knitting/data/processed/all_processed_text.txt'
    output_file = '/Users/hw/Desktop/knitting/data/processed/extracted_sizes.txt'
    
    # 读取输入文件
    with open(input_file, 'r', encoding='utf-8') as f:
        text = f.read()
    
    # 提取尺码
    print("正在提取尺码...")
    size_extractor = SizeExtractor()
    result = size_extractor.process_knitting_pattern(text)
    
    # 保存结果
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(result)
    print(f"处理完成！结果已保存到: {output_file}")

if __name__ == '__main__':
    main() 