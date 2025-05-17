import re
from typing import Dict, List, Tuple
import importlib.util
import os

class OCRPostProcessor:
    def __init__(self):
        self.load_correction_rules()
    
    def load_correction_rules(self):
        """加载纠正规则"""
        # 默认规则
        self.term_mapping = {
            "林迪": "朱迪",
            "衣刁": "衣身",
            "折灵边": "折叠边",
            "大言岭": "大吉岭",
            "扣了眼": "扣眼",
            "裕加针": "空加针",
            "左上2并1": "左上2并1",
            "右上2并1": "右上2并1"
        }
        
        self.symbol_mapping = {
            "【": "【",
            "】": "】",
            "［": "【",
            "］": "】",
            "《": "（",
            "》": "）"
        }
        
        # 从correction_rules.py加载规则
        if os.path.exists('correction_rules.py'):
            spec = importlib.util.spec_from_file_location("correction_rules", os.path.join(os.path.dirname(__file__), "correction_rules.py"))
            rules = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(rules)
            
            # 更新规则
            self.term_mapping.update(rules.TERM_MAPPING)
            self.symbol_mapping.update(rules.SYMBOL_MAPPING)
            if hasattr(rules, 'NUMBER_PATTERNS'):
                self.number_patterns = rules.NUMBER_PATTERNS
        
        # 数字模式
        self.number_pattern = re.compile(r'(\d+)\s*[（(]\s*(\d+)\s*[-—]\s*(\d+)\s*[-—]\s*(\d+)\s*[-—]\s*(\d+)\s*[-—]\s*(\d+)\s*[-—]\s*(\d+)\s*[-—]\s*(\d+)\s*[-—]\s*(\d+)\s*[)）]')
    
    def standardize_numbers(self, text: str) -> str:
        """标准化数字格式"""
        def replace_numbers(match):
            numbers = [match.group(i) for i in range(1, 9)]
            return f"{numbers[0]} ({numbers[1]} - {numbers[2]} - {numbers[3]} - {numbers[4]} - {numbers[5]} - {numbers[6]} - {numbers[7]})"
        
        return self.number_pattern.sub(replace_numbers, text)
    
    def correct_terms(self, text: str) -> str:
        """修正专业术语"""
        for wrong, correct in self.term_mapping.items():
            text = text.replace(wrong, correct)
        return text
    
    def standardize_symbols(self, text: str) -> str:
        """标准化符号"""
        for wrong, correct in self.symbol_mapping.items():
            text = text.replace(wrong, correct)
        return text
    
    def fix_formatting(self, text: str) -> str:
        """修复格式问题"""
        # 1. 处理段落结构
        # 保留标题格式
        text = re.sub(r'^#\s*(\w+)', r'# \1', text, flags=re.MULTILINE)
        text = re.sub(r'^##\s*(\w+)', r'## \1', text, flags=re.MULTILINE)
        
        # 2. 处理数字格式
        # 标准化括号内的数字序列
        text = re.sub(r'(\d+)\s*[（(]\s*(\d+)\s*[-—]\s*(\d+)\s*[-—]\s*(\d+)\s*[-—]\s*(\d+)\s*[-—]\s*(\d+)\s*[-—]\s*(\d+)\s*[-—]\s*(\d+)\s*[)）]', r'\1 (\2-\3-\4-\5-\6-\7-\8)', text)
        # 标准化单个数字的括号
        text = re.sub(r'(\d+)\s*[（(]\s*(\d+)\s*[)）]', r'\1 (\2)', text)
        
        # 3. 处理段落分隔
        # 在句号、感叹号、问号后添加空行
        text = re.sub(r'([。！？])\n', r'\1\n\n', text)
        # 删除多余的空行（保留最多两个连续空行）
        text = re.sub(r'\n{3,}', '\n\n', text)
        
        # 4. 处理行内格式
        # 保留段落缩进，但删除行内多余空格
        lines = text.split('\n')
        processed_lines = []
        for line in lines:
            # 保留行首的缩进空格
            indent = len(line) - len(line.lstrip())
            processed_line = ' ' * indent + ' '.join(line.strip().split())
            processed_lines.append(processed_line)
        
        # 重新组合文本
        text = '\n'.join(processed_lines)
        
        return text
    
    def process(self, text: str) -> str:
        """处理文本的主函数"""
        # 按顺序应用所有处理步骤
        text = self.standardize_numbers(text)
        text = self.correct_terms(text)
        text = self.standardize_symbols(text)
        text = self.fix_formatting(text)
        return text

def process_file(input_file: str, output_file: str):
    """处理文件的主函数"""
    processor = OCRPostProcessor()
    
    try:
        with open(input_file, 'r', encoding='utf-8') as f:
            text = f.read()
        
        processed_text = processor.process(text)
        
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(processed_text)
            
        print(f"处理完成！结果已保存到 {output_file}")
        
    except Exception as e:
        print(f"处理文件时出错: {e}")

if __name__ == '__main__':
    input_file = 'all_processed_text.txt'
    output_file = 'all_processed_text_corrected.txt'
    process_file(input_file, output_file) 