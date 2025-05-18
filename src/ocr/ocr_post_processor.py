import re
from .correction_rules import TERM_MAPPING, REMOVE_PATTERNS, NUMBER_PATTERNS, BRACKET_PATTERNS, CONTEXT_PATTERNS

class OCRPostProcessor:
    def __init__(self):
        self.term_mapping = TERM_MAPPING
        self.remove_patterns = [re.compile(pattern) for pattern in REMOVE_PATTERNS]
        self.number_patterns = [(re.compile(pattern), replacement) for pattern, replacement in NUMBER_PATTERNS]
        self.bracket_patterns = BRACKET_PATTERNS
        self.context_patterns = [(re.compile(pattern), replacement) for pattern, replacement in CONTEXT_PATTERNS]

    def process(self, text: str) -> str:
        """处理OCR文本"""
        # 1. 删除不需要的文本
        for pattern in self.remove_patterns:
            text = pattern.sub('', text)

        # 2. 修复数字模式
        for pattern, replacement in self.number_patterns:
            text = pattern.sub(replacement, text)

        # 3. 标准化括号
        for old, new in self.bracket_patterns:
            text = text.replace(old, new)

        # 4. 上下文相关的替换
        for pattern, replacement in self.context_patterns:
            text = pattern.sub(replacement, text)

        # 5. 替换术语
        for old, new in self.term_mapping.items():
            text = text.replace(old, new)

        return text

def process_text(text: str) -> str:
    """处理文本的便捷函数"""
    processor = OCRPostProcessor()
    return processor.process(text) 